"""Fine-tune the current Practical V1 model on private weakness candidates."""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

BASE = ROOT / "runs" / "exam_qa_erabi_v1_finetune_20260923" / "checkpoint"
DATA = ROOT / "data" / "exam_qa_weakness_v1_split_20260924"
PRACTICAL = ROOT / "data" / "practical_v1"
BRIDGE = ROOT / "data" / "rc3_bridge" / "rc3_bridge_benchmark.jsonl"
ORIGINAL_EXAM = ROOT / "data" / "exam_qa_erabi_v1_reshuffle_20260924"
DEFAULT_OUTPUT = ROOT / "runs" / "exam_qa_weakness_v1_finetune_20260924"
MAX_TOKENS = 1024
MICRO_BATCH_SIZE = 1
GRADIENT_ACCUMULATION_STEPS = 16


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def select_replay(records: list[dict], count: int, seed: int) -> list[dict]:
    if count > len(records):
        raise ValueError("replay count exceeds available records")
    selected = list(records)
    random.Random(seed).shuffle(selected)
    copies = json.loads(json.dumps(selected[:count], ensure_ascii=False))
    for index, row in enumerate(copies):
        row["id"] = f"weakness_replay_{index}_{row['id']}"
        row["group_id"] = f"weakness_replay_{row['group_id']}"
        row["split"] = "train"
    return copies


def retention_pass(baseline: dict, trained: dict) -> bool:
    return (
        trained["practical_dev"]["accuracy"] >= baseline["practical_dev"]["accuracy"] - 0.02
        and trained["bridge"]["accuracy"] >= baseline["bridge"]["accuracy"] - 0.02
        and trained["original_exam_dev"]["accuracy"] >= baseline["original_exam_dev"]["accuracy"] - 0.03
    )


def production_candidate(baseline: dict, candidate: dict) -> bool:
    return (
        candidate["weakness_final"]["accuracy"] >= baseline["weakness_final"]["accuracy"] + 0.05
        and candidate["weakness_dev"]["accuracy"] > baseline["weakness_dev"]["accuracy"]
        and retention_pass(baseline, candidate)
        and candidate["practical_eval"]["accuracy"] >= baseline["practical_eval"]["accuracy"] - 0.01
        and candidate["original_exam_final"]["accuracy"] >= baseline["original_exam_final"]["accuracy"] - 0.02
    )


def train_one_epoch(rows: list[dict], trainer, lr: float, seed: int) -> dict:
    import torch
    import torch.nn.functional as F

    rng = random.Random(seed)
    shuffled = list(rows)
    rng.shuffle(shuffled)
    batches = [shuffled[index : index + MICRO_BATCH_SIZE] for index in range(0, len(shuffled), MICRO_BATCH_SIZE)]
    windows = math.ceil(len(batches) / GRADIENT_ACCUMULATION_STEPS)
    warmup = min(10, max(1, windows // 3))
    floor = min(3e-7, lr)
    scaler = torch.amp.GradScaler("cuda", enabled=True)
    trainer.model.train()
    total_loss = 0.0
    processed = 0
    skipped_steps = 0
    for window in range(windows):
        group = batches[
            window * GRADIENT_ACCUMULATION_STEPS : (window + 1) * GRADIENT_ACCUMULATION_STEPS
        ]
        sample_count = sum(len(batch) for batch in group)
        if window < warmup:
            current_lr = lr * (window + 1) / warmup
        else:
            fraction = (window - warmup) / max(1, windows - warmup - 1)
            current_lr = floor + 0.5 * (lr - floor) * (1 + math.cos(math.pi * fraction))
        for params in trainer.optimizer.param_groups:
            params["lr"] = current_lr
        trainer.optimizer.zero_grad(set_to_none=True)
        window_loss = 0.0
        for batch in group:
            inputs, targets, choice_counts, max_classes = trainer.prepare_batch(
                batch, shuffle_choices=True, rng=rng
            )
            with torch.amp.autocast("cuda", dtype=torch.float16):
                outputs = trainer.model(**inputs, max_num_classes=max_classes)
                per_batch = torch.tensor(0.0, device=trainer.device)
                for index, (target, count) in enumerate(zip(targets, choice_counts)):
                    logits = outputs.logits[index, :count].to(torch.float32)
                    target_tensor = torch.tensor([target], device=trainer.device)
                    per_batch = per_batch + F.cross_entropy(logits.unsqueeze(0), target_tensor)
                loss = per_batch / sample_count
            if not torch.isfinite(loss):
                raise FloatingPointError(f"Nonfinite loss at optimizer window {window + 1}")
            scaler.scale(loss).backward()
            window_loss += float(per_batch.detach().cpu())
        scaler.unscale_(trainer.optimizer)
        torch.nn.utils.clip_grad_norm_(trainer.model.parameters(), 1.0)
        scale_before = scaler.get_scale()
        scaler.step(trainer.optimizer)
        scaler.update()
        if scaler.get_scale() < scale_before:
            skipped_steps += 1
        total_loss += window_loss
        processed += sample_count
        if (window + 1) % 5 == 0 or window + 1 == windows:
            print(
                f"step {window + 1}/{windows} mean_ce={total_loss / processed:.4f} "
                f"lr={current_lr:.2e} scaler={scaler.get_scale():.0f}",
                flush=True,
            )
    return {
        "optimizer_windows": windows,
        "optimizer_steps": windows - skipped_steps,
        "amp_skipped_steps": skipped_steps,
        "mean_train_ce": total_loss / len(rows),
        "learning_rate": lr,
        "micro_batch_size": MICRO_BATCH_SIZE,
        "gradient_accumulation_steps": GRADIENT_ACCUMULATION_STEPS,
        "seed": seed,
        "precision": "fp16_amp",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DATA)
    parser.add_argument("--base-model", type=Path, default=BASE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--lr", type=float, default=1e-6)
    parser.add_argument("--seed", type=int, default=20260924)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    if not 1 <= args.epochs <= 4:
        raise ValueError("epochs must be 1..4")

    paths = {
        "base": args.base_model / "model.safetensors",
        "weakness_train": args.data_dir / "train.jsonl",
        "weakness_dev": args.data_dir / "dev.jsonl",
        "weakness_final": args.data_dir / "final_test.jsonl",
        "split_manifest": args.data_dir / "split_manifest.json",
        "practical_train": PRACTICAL / "train.jsonl",
        "practical_dev": PRACTICAL / "dev.jsonl",
        "practical_eval": PRACTICAL / "eval_teacher_agreed.jsonl",
        "bridge": BRIDGE,
        "original_exam_dev": ORIGINAL_EXAM / "dev.jsonl",
        "original_exam_final": ORIGINAL_EXAM / "final_test.jsonl",
    }
    for name, path in paths.items():
        if not path.is_file():
            raise FileNotFoundError(f"Missing {name}: {path}")
    weakness_train = read_jsonl(paths["weakness_train"])
    weakness_dev = read_jsonl(paths["weakness_dev"])
    weakness_final = read_jsonl(paths["weakness_final"])
    weakness_groups = [set(row["group_id"] for row in rows) for rows in (weakness_train, weakness_dev, weakness_final)]
    if weakness_groups[0] & weakness_groups[1] or weakness_groups[0] & weakness_groups[2] or weakness_groups[1] & weakness_groups[2]:
        raise ValueError("weakness split group overlap")
    if any(row.get("input_tokens", MAX_TOKENS + 1) > MAX_TOKENS for row in weakness_train + weakness_dev + weakness_final):
        raise ValueError("weakness input exceeds 1024-token contract")
    expected_status = "deepseek_generated_and_answer_blind_agreed_unreviewed"
    if any(row.get("review_status") != expected_status for row in weakness_train + weakness_dev + weakness_final):
        raise ValueError("weakness records have unexpected review status")

    practical_train = read_jsonl(paths["practical_train"])
    replay = select_replay(practical_train, len(weakness_train), args.seed)
    mixed_train = weakness_train + replay
    selection_suites = {
        "weakness_dev": weakness_dev,
        "practical_dev": read_jsonl(paths["practical_dev"]),
        "bridge": read_jsonl(paths["bridge"]),
        "original_exam_dev": read_jsonl(paths["original_exam_dev"]),
    }
    final_only_suites = {
        "weakness_final": weakness_final,
        "practical_eval": read_jsonl(paths["practical_eval"]),
        "original_exam_final": read_jsonl(paths["original_exam_final"]),
    }
    final_suites = {**selection_suites, **final_only_suites}
    manifest = {
        "files": {name: {"path": str(path), "sha256": sha256(path)} for name, path in paths.items()},
        "counts": {
            "weakness_train": len(weakness_train),
            "practical_replay": len(replay),
            "mixed_train": len(mixed_train),
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
        "final_test_policy": "Weakness and original Exam final tests stay sealed until epoch selection.",
    }
    print(json.dumps(manifest, ensure_ascii=False, indent=2), flush=True)
    if args.dry_run:
        return

    import torch
    from erabi.train import Trainer

    if not args.device.startswith("cuda") or not torch.cuda.is_available():
        raise RuntimeError("This experiment requires one CUDA GPU")
    args.output_dir.mkdir(parents=True)
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
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
    baseline = {name: trainer.evaluate(rows) for name, rows in selection_suites.items()}
    print(
        f"baseline weakness_dev={baseline['weakness_dev']['accuracy']:.4f} "
        f"practical={baseline['practical_dev']['accuracy']:.4f} bridge={baseline['bridge']['accuracy']:.4f}",
        flush=True,
    )

    epochs = []
    best_epoch = None
    best_key = None
    for epoch in range(1, args.epochs + 1):
        training = train_one_epoch(mixed_train, trainer, args.lr, args.seed + epoch - 1)
        metrics = {name: trainer.evaluate(rows) for name, rows in selection_suites.items()}
        passed = metrics["weakness_dev"]["accuracy"] > baseline["weakness_dev"]["accuracy"] and retention_pass(baseline, metrics)
        epochs.append({"epoch": epoch, "training": training, "metrics": metrics, "selection_pass": passed})
        print(
            f"epoch={epoch} weakness_dev={metrics['weakness_dev']['accuracy']:.4f} "
            f"practical={metrics['practical_dev']['accuracy']:.4f} bridge={metrics['bridge']['accuracy']:.4f} "
            f"original_exam_dev={metrics['original_exam_dev']['accuracy']:.4f} pass={passed}",
            flush=True,
        )
        key = (metrics["weakness_dev"]["accuracy"], -metrics["weakness_dev"]["mean_nll"], metrics["practical_dev"]["accuracy"])
        if passed and (best_key is None or key > best_key):
            best_key = key
            best_epoch = epoch
            trainer.save_checkpoint(str(args.output_dir / "checkpoint"))

    del trainer
    gc.collect()
    torch.cuda.empty_cache()
    selected = None
    promoted = False
    if best_epoch is not None:
        baseline_final_trainer = Trainer(
            model_id=str(args.base_model),
            device=args.device,
            lr=args.lr,
            weight_decay=0.01,
            micro_batch_size=MICRO_BATCH_SIZE,
            gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
            seed=args.seed,
        )
        baseline_final_trainer.pipeline.pipe.max_length = MAX_TOKENS
        baseline.update({name: baseline_final_trainer.evaluate(rows) for name, rows in final_only_suites.items()})
        del baseline_final_trainer
        gc.collect()
        torch.cuda.empty_cache()
        selected_trainer = Trainer(
            model_id=str(args.output_dir / "checkpoint"),
            device=args.device,
            lr=args.lr,
            weight_decay=0.01,
            micro_batch_size=MICRO_BATCH_SIZE,
            gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
            seed=args.seed,
        )
        selected_trainer.pipeline.pipe.max_length = MAX_TOKENS
        selected = {name: selected_trainer.evaluate(rows) for name, rows in final_suites.items()}
        promoted = production_candidate(baseline, selected)
        print(
            f"selected epoch={best_epoch} weakness_final={selected['weakness_final']['accuracy']:.4f} "
            f"baseline_final={baseline['weakness_final']['accuracy']:.4f} production_candidate={promoted}",
            flush=True,
        )
    summary = {
        "manifest": manifest,
        "baseline": baseline,
        "epochs": epochs,
        "best_epoch": best_epoch,
        "selected": selected,
        "production_candidate": promoted,
        "production_criterion": "Weakness final gains >=5 points; weakness dev improves; Practical dev and Bridge lose <=2 points; Practical eval loses <=1 point; original Exam dev loses <=3 points and final loses <=2 points.",
        "limitations": [
            "Weakness splits share one generator and prompt family, so improvement may be generator-style adaptation.",
            "DeepSeek generation and answer-blind agreement are not independent human gold.",
            "The final sets are small; promotion still requires follow-up ONNX parity, calibration, and independent evaluation.",
        ],
    }
    (args.output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"best_epoch": best_epoch, "production_candidate": promoted}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
