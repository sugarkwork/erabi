"""Fine-tune ERABI on Decision Mix V2 and open the fixed final test only after dev selection."""
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
import statistics
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
BASE = ROOT / "runs" / "world_choice_v1_finetune_20260927" / "checkpoint_selected"
DM2 = ROOT / "data" / "decision_mix_v2"
WORLD = ROOT / "data" / "world_choice_v1"
PRACTICAL = ROOT / "data" / "practical_v1"
EXAM = ROOT / "data" / "exam_qa_erabi_v1_reshuffle_20260924"
WEAKNESS = ROOT / "data" / "exam_qa_weakness_v1_split_20260924"
BRIDGE = ROOT / "data" / "rc3_bridge" / "rc3_bridge_benchmark.jsonl"
DEFAULT_OUTPUT = ROOT / "runs" / "decision_mix_v2_finetune_20260930"
MAX_TOKENS = 512
ACCUMULATION = 16


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def input_signature(row: dict) -> str:
    value = {
        "context": row.get("context", ""), "question": row.get("question", ""),
        "choices": [choice["text"] for choice in row["choices"]],
    }
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def canonical_group(row: dict) -> str:
    return row.get("canonical_group_id") or row["group_id"]


def prefixed_copy(rows: list[dict], prefix: str) -> list[dict]:
    copied = json.loads(json.dumps(rows, ensure_ascii=False))
    for row in copied:
        row["id"] = f"{prefix}_{row['id']}"
        row["group_id"] = f"{prefix}_{row['group_id']}"
        row["canonical_group_id"] = f"{prefix}_{canonical_group(row)}"
        row["split"] = "train"
    return copied


def assert_group_disjoint(parts: dict[str, list[dict]]) -> None:
    groups = {name: {canonical_group(row) for row in rows} for name, rows in parts.items()}
    names = list(groups)
    for index, left in enumerate(names):
        for right in names[index + 1:]:
            overlap = groups[left] & groups[right]
            if overlap:
                raise ValueError(f"canonical group overlap {left}/{right}: {sorted(overlap)[:3]}")


def formatted_tokens(trainer, row: dict) -> int:
    inner = trainer.pipeline.pipe
    text = inner.prepare_input(row.get("context", ""), [choice["text"] for choice in row["choices"]],
                               prompt=row.get("question", ""))
    return len(trainer.tokenizer(text, truncation=False)["input_ids"])


def train_one_epoch(rows: list[dict], trainer, lr: float, seed: int) -> dict:
    import torch
    import torch.nn.functional as F
    rng = random.Random(seed)
    shuffled = list(rows)
    rng.shuffle(shuffled)
    windows = math.ceil(len(shuffled) / ACCUMULATION)
    warmup = min(10, max(1, windows // 3))
    floor = min(3e-7, lr)
    scaler = torch.amp.GradScaler("cuda", enabled=True)
    trainer.model.train()
    total_loss = 0.0
    processed = 0
    skipped = 0
    started = time.perf_counter()
    for window in range(windows):
        group = shuffled[window * ACCUMULATION:(window + 1) * ACCUMULATION]
        if window < warmup:
            current_lr = lr * (window + 1) / warmup
        else:
            fraction = (window - warmup) / max(1, windows - warmup - 1)
            current_lr = floor + .5 * (lr - floor) * (1 + math.cos(math.pi * fraction))
        for params in trainer.optimizer.param_groups:
            params["lr"] = current_lr
        trainer.optimizer.zero_grad(set_to_none=True)
        window_loss = 0.0
        for row in group:
            inputs, targets, counts, max_classes = trainer.prepare_batch([row], shuffle_choices=True, rng=rng)
            with torch.amp.autocast("cuda", dtype=torch.float16):
                outputs = trainer.model(**inputs, max_num_classes=max_classes)
                logits = outputs.logits[0, :counts[0]].float()
                target = torch.tensor([targets[0]], device=trainer.device)
                per_sample = F.cross_entropy(logits.unsqueeze(0), target)
                loss = per_sample / len(group)
            if not torch.isfinite(loss):
                raise FloatingPointError(f"nonfinite loss at window {window + 1}")
            scaler.scale(loss).backward()
            window_loss += float(per_sample.detach().cpu())
        scaler.unscale_(trainer.optimizer)
        torch.nn.utils.clip_grad_norm_(trainer.model.parameters(), 1.0)
        old_scale = scaler.get_scale()
        scaler.step(trainer.optimizer)
        scaler.update()
        skipped += scaler.get_scale() < old_scale
        total_loss += window_loss
        processed += len(group)
        if (window + 1) % 20 == 0 or window + 1 == windows:
            print(f"step {window + 1}/{windows} mean_ce={total_loss/processed:.4f} "
                  f"lr={current_lr:.2e} elapsed_min={(time.perf_counter()-started)/60:.1f}", flush=True)
    return {"rows": len(rows), "optimizer_windows": windows, "amp_skipped_steps": skipped,
            "mean_train_ce": total_loss / len(rows), "elapsed_seconds": time.perf_counter() - started}


def evaluate_selection(trainer, dm2_dev: list[dict], retention: dict[str, list[dict]], label: str) -> dict:
    result = {"decision_dev": trainer.evaluate(dm2_dev)}
    family = {}
    for name in sorted({row["domain"] for row in dm2_dev}):
        family[name] = trainer.evaluate([row for row in dm2_dev if row["domain"] == name])
    result["decision_family"] = family
    result["decision_family_macro_accuracy"] = statistics.mean(item["accuracy"] for item in family.values())
    for name, rows in retention.items():
        result[name] = trainer.evaluate(rows)
    print(f"{label}: decision={result['decision_dev']['correct_count']}/{len(dm2_dev)} "
          f"acc={result['decision_dev']['accuracy']:.4f} macro={result['decision_family_macro_accuracy']:.4f} "
          f"nll={result['decision_dev']['mean_nll']:.4f}", flush=True)
    return result


def retention_pass(baseline: dict, candidate: dict) -> bool:
    limits = {"practical_dev": .02, "world_dev": .02, "bridge": .02, "exam_dev": .03, "weakness_dev": .03}
    return all(candidate[name]["accuracy"] >= baseline[name]["accuracy"] - drop for name, drop in limits.items())


def selection_key(metrics: dict) -> tuple:
    return (metrics["decision_family_macro_accuracy"], metrics["decision_dev"]["accuracy"],
            -metrics["decision_dev"]["mean_nll"])


def detailed_evaluate(trainer, rows: list[dict], output_dir: Path, model_name: str) -> dict:
    import torch
    from erabi.evaluate import compute_metrics
    from erabi.schema import ChoiceRequest
    output_dir.mkdir(parents=True, exist_ok=False)
    trainer.model.eval()
    predictions = []
    records = []
    started = time.perf_counter()
    with (output_dir / "predictions.jsonl").open("x", encoding="utf-8") as handle:
        for index, row in enumerate(rows, 1):
            request = ChoiceRequest.from_dict(row)
            labels = [choice.text for choice in request.choices]
            inner = trainer.pipeline.pipe
            token_count = formatted_tokens(trainer, row)
            if token_count > MAX_TOKENS:
                raise ValueError(f"{row['id']}: {token_count} tokens exceeds {MAX_TOKENS}")
            inputs = inner.prepare_inputs(texts=[request.context], labels=[labels], same_labels=False,
                                          prompt=[request.question])
            max_classes = inner._resolve_max_num_classes([labels], same_labels=False)
            item_started = time.perf_counter()
            with torch.inference_mode():
                logits = trainer.model(**inputs, max_num_classes=max_classes).logits[0, :len(labels)].float()
            probabilities = torch.softmax(logits, -1).cpu().tolist()
            best = int(torch.argmax(logits).item())
            target = row["target"]["choice_id"]
            choice_ids = [choice.id for choice in request.choices]
            pred = {"choices": [{"id": cid, "probability": float(prob)} for cid, prob in zip(choice_ids, probabilities)],
                    "best_candidate_id": choice_ids[best], "raw_logits": logits.cpu().tolist()}
            predictions.append(pred)
            lengths = [len(choice.text) for choice in request.choices]
            maximum = max(lengths)
            record = {
                "id": row["id"], "canonical_group_id": canonical_group(row), "domain": row["domain"],
                "language": row["language"], "target": target, "prediction": choice_ids[best],
                "correct": choice_ids[best] == target, "choice_ids": choice_ids,
                "probabilities": {cid: float(prob) for cid, prob in zip(choice_ids, probabilities)},
                "longest_choice_ids": [choice_ids[i] for i, value in enumerate(lengths) if value == maximum],
                "input_tokens": token_count, "elapsed_ms": (time.perf_counter() - item_started) * 1000,
            }
            records.append(record)
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            if index % 50 == 0 or index == len(rows):
                print(f"{model_name} final {index}/{len(rows)}", flush=True)

    def block(selected: list[int]) -> dict:
        return compute_metrics([predictions[i] for i in selected], [records[i]["target"] for i in selected])
    family = {name: block([i for i, row in enumerate(rows) if row["domain"] == name])
              for name in sorted({row["domain"] for row in rows})}
    language = {name: block([i for i, row in enumerate(rows) if row["language"] == name])
                for name in sorted({row["language"] for row in rows})}
    groups: dict[str, list[bool]] = {}
    for record in records:
        groups.setdefault(record["canonical_group_id"], []).append(record["correct"])
    gold_longest = [i for i, record in enumerate(records) if record["target"] in record["longest_choice_ids"]]
    gold_not = [i for i in range(len(records)) if i not in set(gold_longest)]
    summary = {
        "model": model_name, "rows": len(rows), "evaluation_seconds": time.perf_counter() - started,
        "overall": block(list(range(len(rows)))),
        "family_macro_accuracy": statistics.mean(item["accuracy"] for item in family.values()),
        "by_family": family, "by_language": language,
        "canonical_group_all_correct": {"groups": len(groups),
            "correct_groups": sum(all(values) for values in groups.values()),
            "rate": sum(all(values) for values in groups.values()) / len(groups)},
        "uniform_random_expected_accuracy": statistics.mean(1 / len(record["choice_ids"]) for record in records),
        "longest_choice_baseline_accuracy": len(gold_longest) / len(records),
        "model_on_gold_longest": block(gold_longest), "model_on_gold_not_longest": block(gold_not),
        "latency_ms": {"mean": statistics.mean(row["elapsed_ms"] for row in records),
                       "median": statistics.median(row["elapsed_ms"] for row in records)},
    }
    write_json(output_dir / "summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-model", type=Path, default=BASE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--lr", type=float, default=1e-6)
    parser.add_argument("--seed", type=int, default=20260930)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    if not 1 <= args.epochs <= 5:
        raise ValueError("epochs must be 1..5")

    files = {
        "weights": args.base_model / "model.safetensors",
        "decision_train": DM2 / "combined_train.jsonl", "decision_dev": DM2 / "combined_dev.jsonl",
        "decision_calibration": DM2 / "combined_calibration.jsonl",
        "decision_final": DM2 / "combined_final_test.jsonl", "decision_manifest": DM2 / "combined_manifest.json",
        "quarantine": DM2 / "quality_quarantine.json", "world_train": WORLD / "train.jsonl",
        "world_dev": WORLD / "dev.jsonl", "practical_train": PRACTICAL / "train.jsonl",
        "practical_dev": PRACTICAL / "dev.jsonl", "exam_train": EXAM / "train.jsonl",
        "exam_dev": EXAM / "dev.jsonl", "weakness_dev": WEAKNESS / "dev.jsonl", "bridge": BRIDGE,
    }
    for name, path in files.items():
        if not path.is_file():
            raise FileNotFoundError(f"missing {name}: {path}")
    quarantine_doc = json.loads(files["quarantine"].read_text(encoding="utf-8"))
    quarantine = set(quarantine_doc["ids"])
    raw_parts = {name: read_jsonl(files[f"decision_{name}"]) for name in ("train", "dev", "calibration", "final")}
    parts = {name: [row for row in rows if row["id"] not in quarantine] for name, rows in raw_parts.items()}
    assert_group_disjoint(parts)
    all_rows = sum(parts.values(), [])
    if len({row["id"] for row in all_rows}) != len(all_rows):
        raise ValueError("duplicate Decision Mix IDs")
    heldout_signatures = {input_signature(row) for name in ("dev", "calibration", "final") for row in parts[name]}
    rng = random.Random(args.seed)
    replay_sources = {}
    for name, path, cap in (("world", files["world_train"], 1024),
                            ("practical", files["practical_train"], 1024),
                            ("exam", files["exam_train"], 117)):
        candidates = [row for row in read_jsonl(path) if input_signature(row) not in heldout_signatures]
        rng.shuffle(candidates)
        replay_sources[name] = candidates[:cap]

    manifest = {
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "files": {name: {"path": str(path.resolve()), "sha256": sha256(path)} for name, path in files.items()},
        "quarantine": {"reviewed_sample_rows": 60, "ids": sorted(quarantine),
                       "excluded_by_split": {name: len(raw_parts[name]) - len(parts[name]) for name in parts}},
        "decision_counts": {name: len(rows) for name, rows in parts.items()},
        "replay_requested": {"world": 1024, "practical": 1024, "exam": 117},
        "config": {"epochs": args.epochs, "lr": args.lr, "seed": args.seed, "device": args.device,
                   "max_tokens": MAX_TOKENS, "micro_batch_size": 1, "gradient_accumulation_steps": ACCUMULATION},
        "selection_policy": "Dev-only: highest six-family macro accuracy, then overall accuracy, then lower NLL, among retention-passing epochs.",
        "retention_policy": "World, Practical and Bridge drops <=2 points; Exam and Weakness drops <=3 points.",
        "final_policy": "Final rows are not scored until selection.json records a selected checkpoint and weights hash.",
        "label_note": "Synthetic DeepSeek generator plus answer-blind same-family judge; provisional, not human gold.",
    }
    print(json.dumps({"decision_counts": manifest["decision_counts"], "quarantine": manifest["quarantine"],
                      "config": manifest["config"]}, ensure_ascii=False, indent=2), flush=True)
    if args.dry_run:
        return

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    import torch
    from erabi.train import Trainer
    if not args.device.startswith("cuda") or not torch.cuda.is_available():
        raise RuntimeError("one CUDA GPU is required")
    args.output_dir.mkdir(parents=True)
    write_json(args.output_dir / "manifest.json", manifest)
    for name, rows in parts.items():
        write_jsonl(args.output_dir / f"filtered_{name}.jsonl", rows)

    run_started = time.perf_counter()
    trainer = Trainer(model_id=str(args.base_model), device=args.device, lr=args.lr, weight_decay=.01,
                      micro_batch_size=1, gradient_accumulation_steps=ACCUMULATION, seed=args.seed)
    trainer.pipeline.pipe.max_length = MAX_TOKENS
    lengths = {row["id"]: formatted_tokens(trainer, row) for row in all_rows}
    over = [row_id for row_id, value in lengths.items() if value > MAX_TOKENS]
    if over:
        raise ValueError(f"Decision Mix formatted rows exceed {MAX_TOKENS}: {over[:5]}")
    replay_filtered = {}
    for name, candidates in replay_sources.items():
        kept = [row for row in candidates if formatted_tokens(trainer, row) <= MAX_TOKENS]
        replay_filtered[name] = prefixed_copy(kept, f"dm2_replay_{name}")
    mixed_train = parts["train"] + sum(replay_filtered.values(), [])
    manifest["actual_tokens"] = {"min": min(lengths.values()), "max": max(lengths.values()), "over_512": 0}
    manifest["replay_kept"] = {name: len(rows) for name, rows in replay_filtered.items()}
    manifest["mixed_train_rows"] = len(mixed_train)
    write_json(args.output_dir / "manifest.json", manifest)

    retention = {"world_dev": read_jsonl(files["world_dev"]),
                 "practical_dev": read_jsonl(files["practical_dev"]), "bridge": read_jsonl(files["bridge"]),
                 "exam_dev": read_jsonl(files["exam_dev"]), "weakness_dev": read_jsonl(files["weakness_dev"])}
    baseline = evaluate_selection(trainer, parts["dev"], retention, "baseline")
    epochs = []
    best_any = None
    best_eligible = None
    for epoch in range(1, args.epochs + 1):
        print(f"epoch {epoch}/{args.epochs} training rows={len(mixed_train)}", flush=True)
        training = train_one_epoch(mixed_train, trainer, args.lr, args.seed + epoch - 1)
        metrics = evaluate_selection(trainer, parts["dev"], retention, f"epoch-{epoch}")
        passed = retention_pass(baseline, metrics)
        checkpoint = args.output_dir / f"checkpoint_epoch_{epoch}"
        trainer.save_checkpoint(str(checkpoint))
        item = {"epoch": epoch, "training": training, "metrics": metrics, "retention_pass": passed,
                "checkpoint": str(checkpoint.resolve()), "weights_sha256": sha256(checkpoint / "model.safetensors")}
        epochs.append(item)
        if best_any is None or selection_key(metrics) > selection_key(best_any["metrics"]):
            best_any = item
        if passed and (best_eligible is None or selection_key(metrics) > selection_key(best_eligible["metrics"])):
            best_eligible = item
        write_json(args.output_dir / "progress.json", {"baseline": baseline, "epochs": epochs})
        print(f"epoch={epoch} retention={passed}", flush=True)

    selected = best_eligible or best_any
    if selected is None:
        raise RuntimeError("no epoch was produced")
    selected_source = Path(selected["checkpoint"])
    selected_checkpoint = args.output_dir / "checkpoint_selected"
    shutil.copytree(selected_source, selected_checkpoint)
    selection = {
        "selected_epoch": selected["epoch"], "retention_pass": bool(best_eligible),
        "checkpoint": str(selected_checkpoint.resolve()),
        "weights_sha256": sha256(selected_checkpoint / "model.safetensors"),
        "selected_before_final_test": True, "selection_metrics": selected["metrics"],
    }
    write_json(args.output_dir / "selection.json", selection)

    # Only now load and score the final rows. Both systems use filtered_final.jsonl byte-for-byte.
    del trainer
    gc.collect()
    torch.cuda.empty_cache()
    baseline_trainer = Trainer(model_id=str(args.base_model), device=args.device, lr=args.lr, seed=args.seed)
    baseline_trainer.pipeline.pipe.max_length = MAX_TOKENS
    baseline_final = detailed_evaluate(baseline_trainer, parts["final"], args.output_dir / "baseline_final", "erabi_baseline")
    del baseline_trainer
    gc.collect()
    torch.cuda.empty_cache()
    selected_trainer = Trainer(model_id=str(selected_checkpoint), device=args.device, lr=args.lr, seed=args.seed)
    selected_trainer.pipeline.pipe.max_length = MAX_TOKENS
    selected_final = detailed_evaluate(selected_trainer, parts["final"], args.output_dir / "selected_final", "erabi_selected")
    summary = {
        "status": "complete", "baseline_selection": baseline, "epochs": epochs, "selection": selection,
        "baseline_final": baseline_final, "selected_final": selected_final,
        "final_input": str((args.output_dir / "filtered_final.jsonl").resolve()),
        "final_input_sha256": sha256(args.output_dir / "filtered_final.jsonl"),
        "total_elapsed_seconds": time.perf_counter() - run_started,
        "limitations": ["Labels are provisional synthetic agreement, not independent human gold.",
                        "One training run and one fixed final evaluation do not establish general superiority.",
                        "Calibration split was kept separate and not used."],
    }
    write_json(args.output_dir / "summary.json", summary)
    print(json.dumps({"selected_epoch": selection["selected_epoch"],
                      "baseline_final": baseline_final["overall"], "selected_final": selected_final["overall"],
                      "elapsed_minutes": summary["total_elapsed_seconds"] / 60}, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
