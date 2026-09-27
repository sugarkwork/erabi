"""Fine-tune the current ERABI checkpoint on World Choice V1.

The World Choice split is group-disjoint.  Epoch selection uses only development
suites; final/reference suites are measured before training and after selection,
but never influence checkpoint selection.
"""
from __future__ import annotations

import argparse
import datetime as dt
import gc
import hashlib
import json
import math
import os
import random
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

BASE = ROOT / "runs" / "exam_qa_erabi_v1_finetune_20260923" / "checkpoint"
WORLD = ROOT / "data" / "world_choice_v1"
PRACTICAL = ROOT / "data" / "practical_v1"
BRIDGE = ROOT / "data" / "rc3_bridge" / "rc3_bridge_benchmark.jsonl"
EXAM = ROOT / "data" / "exam_qa_erabi_v1"
EXAM_SPLIT = ROOT / "data" / "exam_qa_erabi_v1_reshuffle_20260924"
WEAKNESS = ROOT / "data" / "exam_qa_weakness_v1_split_20260924"
DEFAULT_OUTPUT = ROOT / "runs" / "world_choice_v1_finetune_20260927"
MAX_TOKENS = 1024
MICRO_BATCH_SIZE = 1
GRADIENT_ACCUMULATION_STEPS = 16


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def copy_for_replay(records: list[dict], prefix: str) -> list[dict]:
    copies = json.loads(json.dumps(records, ensure_ascii=False))
    for row in copies:
        row["id"] = f"{prefix}_{row['id']}"
        row["group_id"] = f"{prefix}_{row['group_id']}"
        row["split"] = "train"
    return copies


def retention_pass(baseline: dict, candidate: dict) -> bool:
    return (
        candidate["practical_dev"]["accuracy"] >= baseline["practical_dev"]["accuracy"] - 0.02
        and candidate["bridge"]["accuracy"] >= baseline["bridge"]["accuracy"] - 0.02
        and candidate["exam_dev"]["accuracy"] >= baseline["exam_dev"]["accuracy"] - 0.03
        and candidate["weakness_dev"]["accuracy"] >= baseline["weakness_dev"]["accuracy"] - 0.03
    )


def train_one_epoch(rows: list[dict], trainer, lr: float, seed: int) -> dict:
    import torch
    import torch.nn.functional as F

    rng = random.Random(seed)
    shuffled = list(rows)
    rng.shuffle(shuffled)
    windows = math.ceil(len(shuffled) / GRADIENT_ACCUMULATION_STEPS)
    warmup = min(10, max(1, windows // 3))
    floor = min(3e-7, lr)
    scaler = torch.amp.GradScaler("cuda", enabled=True)
    trainer.model.train()
    total_loss = 0.0
    processed = 0
    skipped_steps = 0
    started = time.perf_counter()
    for window in range(windows):
        group = shuffled[
            window * GRADIENT_ACCUMULATION_STEPS : (window + 1) * GRADIENT_ACCUMULATION_STEPS
        ]
        if window < warmup:
            current_lr = lr * (window + 1) / warmup
        else:
            fraction = (window - warmup) / max(1, windows - warmup - 1)
            current_lr = floor + 0.5 * (lr - floor) * (1 + math.cos(math.pi * fraction))
        for params in trainer.optimizer.param_groups:
            params["lr"] = current_lr
        trainer.optimizer.zero_grad(set_to_none=True)
        window_loss = 0.0
        for row in group:
            inputs, targets, choice_counts, max_classes = trainer.prepare_batch(
                [row], shuffle_choices=True, rng=rng
            )
            with torch.amp.autocast("cuda", dtype=torch.float16):
                outputs = trainer.model(**inputs, max_num_classes=max_classes)
                logits = outputs.logits[0, : choice_counts[0]].to(torch.float32)
                target = torch.tensor([targets[0]], device=trainer.device)
                per_sample = F.cross_entropy(logits.unsqueeze(0), target)
                loss = per_sample / len(group)
            if not torch.isfinite(loss):
                raise FloatingPointError(f"Nonfinite loss at optimizer window {window + 1}")
            scaler.scale(loss).backward()
            window_loss += float(per_sample.detach().cpu())
        scaler.unscale_(trainer.optimizer)
        torch.nn.utils.clip_grad_norm_(trainer.model.parameters(), 1.0)
        scale_before = scaler.get_scale()
        scaler.step(trainer.optimizer)
        scaler.update()
        if scaler.get_scale() < scale_before:
            skipped_steps += 1
        total_loss += window_loss
        processed += len(group)
        if (window + 1) % 20 == 0 or window + 1 == windows:
            print(
                f"step {window + 1}/{windows} mean_ce={total_loss / processed:.4f} "
                f"lr={current_lr:.2e} elapsed_min={(time.perf_counter()-started)/60:.1f}",
                flush=True,
            )
    return {
        "optimizer_windows": windows,
        "optimizer_steps": windows - skipped_steps,
        "amp_skipped_steps": skipped_steps,
        "mean_train_ce": total_loss / len(rows),
        "elapsed_seconds": time.perf_counter() - started,
    }


def eval_suites(trainer, suites: dict[str, list[dict]], label: str) -> dict:
    result = {}
    for name, rows in suites.items():
        started = time.perf_counter()
        result[name] = trainer.evaluate(rows)
        result[name]["elapsed_seconds"] = time.perf_counter() - started
        print(
            f"{label} {name}: {result[name]['correct_count']}/{len(rows)} "
            f"acc={result[name]['accuracy']:.4f} nll={result[name]['mean_nll']:.4f} "
            f"elapsed={result[name]['elapsed_seconds']:.1f}s",
            flush=True,
        )
    return result


def checkpoint_key(metrics: dict) -> tuple:
    world = metrics["world_dev"]
    return (world["accuracy"], -world["mean_nll"], metrics["practical_dev"]["accuracy"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-model", type=Path, default=BASE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--lr", type=float, default=1e-6)
    parser.add_argument("--seed", type=int, default=20260927)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    if not 1 <= args.epochs <= 5:
        raise ValueError("epochs must be 1..5")

    paths = {
        "weights": args.base_model / "model.safetensors",
        "world_train": WORLD / "train.jsonl",
        "world_dev": WORLD / "dev.jsonl",
        "world_calibration": WORLD / "calibration.jsonl",
        "world_final": WORLD / "final_test.jsonl",
        "world_manifest": WORLD / "manifest.json",
        "world_exposure": WORLD / "evaluation_exposure.json",
        "practical_train": PRACTICAL / "train.jsonl",
        "practical_dev": PRACTICAL / "dev.jsonl",
        "practical_final": PRACTICAL / "eval_teacher_agreed.jsonl",
        "bridge": BRIDGE,
        "exam_train": EXAM / "train.jsonl",
        "exam_dev": EXAM_SPLIT / "dev.jsonl",
        "exam_final": EXAM_SPLIT / "final_test.jsonl",
        "weakness_dev": WEAKNESS / "dev.jsonl",
        "weakness_final": WEAKNESS / "final_test.jsonl",
    }
    for name, path in paths.items():
        if not path.is_file():
            raise FileNotFoundError(f"Missing {name}: {path}")

    world_parts = {name: read_jsonl(paths[f"world_{name}"]) for name in ("train", "dev", "calibration", "final")}
    group_sets = {name: {row["group_id"] for row in rows} for name, rows in world_parts.items()}
    for left, left_groups in group_sets.items():
        for right, right_groups in group_sets.items():
            if left < right and left_groups & right_groups:
                raise ValueError(f"World Choice group overlap: {left}/{right}")
    all_world = sum(world_parts.values(), [])
    if len({row["id"] for row in all_world}) != len(all_world):
        raise ValueError("Duplicate World Choice ids")

    practical_train = read_jsonl(paths["practical_train"])
    exam_train = read_jsonl(paths["exam_train"])
    mixed_train = (
        world_parts["train"]
        + copy_for_replay(practical_train, "world_replay_practical")
        + copy_for_replay(exam_train, "world_replay_exam")
    )
    selection_suites = {
        "world_dev": world_parts["dev"],
        "practical_dev": read_jsonl(paths["practical_dev"]),
        "bridge": read_jsonl(paths["bridge"]),
        "exam_dev": read_jsonl(paths["exam_dev"]),
        "weakness_dev": read_jsonl(paths["weakness_dev"]),
    }
    final_suites = {
        "world_final": world_parts["final"],
        "practical_final": read_jsonl(paths["practical_final"]),
        "bridge": selection_suites["bridge"],
        "exam_final": read_jsonl(paths["exam_final"]),
        "weakness_final": read_jsonl(paths["weakness_final"]),
    }
    manifest = {
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "files": {name: {"path": str(path.resolve()), "sha256": sha256(path)} for name, path in paths.items()},
        "counts": {
            "world_train": len(world_parts["train"]),
            "practical_replay": len(practical_train),
            "exam_replay": len(exam_train),
            "mixed_train": len(mixed_train),
            **{name: len(rows) for name, rows in selection_suites.items()},
            **{name: len(rows) for name, rows in final_suites.items()},
        },
        "config": {
            "epochs": args.epochs,
            "lr": args.lr,
            "seed": args.seed,
            "device": args.device,
            "max_tokens": MAX_TOKENS,
            "micro_batch_size": MICRO_BATCH_SIZE,
            "gradient_accumulation_steps": GRADIENT_ACCUMULATION_STEPS,
            "optimizer_windows_per_epoch": math.ceil(len(mixed_train) / GRADIENT_ACCUMULATION_STEPS),
        },
        "selection_policy": "Highest World Choice dev accuracy, then lower dev NLL, among epochs passing legacy-dev retention. If none pass, highest World Choice dev is retained as an experimental rejected candidate.",
        "retention_policy": "Practical and Bridge dev drops <=2 points; Exam and Weakness dev drops <=3 points.",
        "final_test_policy": "Final/reference suites are evaluated before training for a baseline and after dev-only checkpoint selection; their results never select an epoch.",
        "exposure_note": "World Choice final_test was already exposed by the prior user-authorized all-row reference benchmark, so it is a reference test, not an untouched acceptance set.",
    }
    print(json.dumps(manifest, ensure_ascii=False, indent=2), flush=True)
    if args.dry_run:
        return

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    import torch
    from erabi.train import Trainer

    if not args.device.startswith("cuda") or not torch.cuda.is_available():
        raise RuntimeError("This experiment requires one CUDA GPU")
    args.output_dir.mkdir(parents=True)
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    run_started = time.perf_counter()
    trainer = Trainer(
        model_id=str(args.base_model),
        device=args.device,
        lr=args.lr,
        weight_decay=0.01,
        micro_batch_size=MICRO_BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        seed=args.seed,
    )
    trainer.pipeline.pipe.max_length = MAX_TOKENS

    # The current formatter is the contract. Check all World Choice inputs without truncation.
    token_lengths = []
    for row in all_world:
        text = trainer.pipeline.pipe.prepare_input(
            row.get("context", ""), [choice["text"] for choice in row["choices"]], prompt=row["question"]
        )
        length = len(trainer.tokenizer(text, truncation=False)["input_ids"])
        if length > MAX_TOKENS:
            raise ValueError(f"{row['id']}: actual formatted input has {length} tokens")
        token_lengths.append(length)
    manifest["actual_world_tokens"] = {"min": min(token_lengths), "max": max(token_lengths), "over_512": sum(x > 512 for x in token_lengths)}
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    baseline_selection = eval_suites(trainer, selection_suites, "baseline-selection")
    baseline_final = eval_suites(trainer, final_suites, "baseline-final")
    epochs = []
    best_any_key = None
    best_any_epoch = None
    best_eligible_key = None
    best_eligible_epoch = None

    for epoch in range(1, args.epochs + 1):
        print(f"epoch {epoch}/{args.epochs} training", flush=True)
        training = train_one_epoch(mixed_train, trainer, args.lr, args.seed + epoch - 1)
        metrics = eval_suites(trainer, selection_suites, f"epoch-{epoch}")
        passed = retention_pass(baseline_selection, metrics)
        key = checkpoint_key(metrics)
        epochs.append({"epoch": epoch, "training": training, "metrics": metrics, "retention_pass": passed})
        if best_any_key is None or key > best_any_key:
            best_any_key = key
            best_any_epoch = epoch
            target = args.output_dir / "checkpoint_best_dev"
            if target.exists():
                shutil.rmtree(target)
            trainer.save_checkpoint(str(target))
        if passed and (best_eligible_key is None or key > best_eligible_key):
            best_eligible_key = key
            best_eligible_epoch = epoch
            target = args.output_dir / "checkpoint_selected"
            if target.exists():
                shutil.rmtree(target)
            trainer.save_checkpoint(str(target))
        print(
            f"epoch={epoch} world_dev={metrics['world_dev']['accuracy']:.4f} "
            f"retention_pass={passed} best_eligible_epoch={best_eligible_epoch}",
            flush=True,
        )

    selected_epoch = best_eligible_epoch if best_eligible_epoch is not None else best_any_epoch
    selected_checkpoint = args.output_dir / ("checkpoint_selected" if best_eligible_epoch is not None else "checkpoint_best_dev")
    del trainer
    gc.collect()
    torch.cuda.empty_cache()

    selected_trainer = Trainer(
        model_id=str(selected_checkpoint),
        device=args.device,
        lr=args.lr,
        weight_decay=0.01,
        micro_batch_size=MICRO_BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        seed=args.seed,
    )
    selected_trainer.pipeline.pipe.max_length = MAX_TOKENS
    selected_selection = eval_suites(selected_trainer, selection_suites, "selected-selection")
    selected_final = eval_suites(selected_trainer, final_suites, "selected-final")
    production_candidate = (
        best_eligible_epoch is not None
        and selected_selection["world_dev"]["accuracy"] > baseline_selection["world_dev"]["accuracy"]
        and selected_final["world_final"]["accuracy"] > baseline_final["world_final"]["accuracy"]
        and selected_final["practical_final"]["accuracy"] >= baseline_final["practical_final"]["accuracy"] - 0.01
        and selected_final["exam_final"]["accuracy"] >= baseline_final["exam_final"]["accuracy"] - 0.02
    )
    summary = {
        "manifest": manifest,
        "baseline_selection": baseline_selection,
        "baseline_final": baseline_final,
        "epochs": epochs,
        "best_any_epoch": best_any_epoch,
        "best_eligible_epoch": best_eligible_epoch,
        "selected_epoch": selected_epoch,
        "selected_checkpoint": str(selected_checkpoint.resolve()),
        "selected_weights_sha256": sha256(selected_checkpoint / "model.safetensors"),
        "selected_selection": selected_selection,
        "selected_final": selected_final,
        "production_candidate": production_candidate,
        "total_elapsed_seconds": time.perf_counter() - run_started,
        "limitations": [
            "World Choice labels are provisional same-model synthetic agreement, not independent human gold.",
            "World Choice final_test was exposed by an earlier all-row benchmark.",
            "No calibration, ONNX export, publication, or replacement of the current model is performed by this experiment.",
        ],
    }
    (args.output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "selected_epoch": selected_epoch,
        "production_candidate": production_candidate,
        "world_final_before": baseline_final["world_final"]["accuracy"],
        "world_final_after": selected_final["world_final"]["accuracy"],
        "elapsed_minutes": summary["total_elapsed_seconds"] / 60,
    }, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
