"""Private 1k Exam-QA fine-tuning experiment from Practical V1 weights."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

BASE = ROOT / "runs" / "practical_v1_finetune_20260922" / "checkpoint"
EXAM_DATA = ROOT / "data" / "exam_qa_erabi_v1"
PRACTICAL = ROOT / "data" / "practical_v1"
BRIDGE = ROOT / "data" / "rc3_bridge" / "rc3_bridge_benchmark.jsonl"
DEFAULT_OUTPUT = ROOT / "runs" / "exam_qa_erabi_v1_finetune_20260923"
MAX_TOKENS = 1024


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def select_replay(records: list[dict], count: int, seed: int) -> list[dict]:
    if count > len(records):
        raise ValueError("replay count exceeds available records")
    rng = random.Random(seed)
    shuffled = list(records)
    rng.shuffle(shuffled)
    selected = shuffled[:count]
    # Preserve source records and annotate only the private in-memory copies.
    return [json.loads(json.dumps(record, ensure_ascii=False)) for record in selected]


def preflight(output: Path, seed: int) -> tuple[list[dict], list[dict], list[dict], list[dict], dict]:
    if output.exists():
        raise FileExistsError(f"Output already exists: {output}")
    paths = {
        "base": BASE / "model.safetensors",
        "exam_train": EXAM_DATA / "train.jsonl",
        "exam_valid": EXAM_DATA / "valid.jsonl",
        "split_manifest": EXAM_DATA / "split_manifest.json",
        "practical_train": PRACTICAL / "train.jsonl",
        "practical_dev": PRACTICAL / "dev.jsonl",
        "bridge": BRIDGE,
    }
    for name, path in paths.items():
        if not path.is_file():
            raise FileNotFoundError(f"Missing {name}: {path}")
    exam_train = read_jsonl(paths["exam_train"])
    exam_valid = read_jsonl(paths["exam_valid"])
    practical_train = read_jsonl(paths["practical_train"])
    practical_dev = read_jsonl(paths["practical_dev"])
    bridge = read_jsonl(paths["bridge"])
    train_groups = {row["group_id"] for row in exam_train}
    valid_groups = {row["group_id"] for row in exam_valid}
    if train_groups & valid_groups:
        raise ValueError("Exam train/valid group overlap")
    if any(row.get("split") != "train" for row in exam_train) or any(row.get("split") != "valid" for row in exam_valid):
        raise ValueError("Exam split markers are inconsistent")
    if any(row.get("input_tokens", MAX_TOKENS + 1) > MAX_TOKENS for row in exam_train + exam_valid):
        raise ValueError("Exam input exceeds 1024-token contract")
    if any(row["provenance"]["transform_kind"] != "official_choices_label_to_text" for row in exam_valid):
        raise ValueError("Validation must use official source choices only")
    replay = select_replay(practical_train, len(exam_train), seed)
    for index, row in enumerate(replay):
        row["id"] = f"replay_{index}_{row['id']}"
        row["group_id"] = f"replay_{row['group_id']}"
        row["split"] = "train"
    mixed_train = list(exam_train) + replay
    manifest = {
        "files": {name: {"path": str(path), "sha256": sha256(path)} for name, path in paths.items()},
        "counts": {
            "exam_train": len(exam_train),
            "replay_train": len(replay),
            "mixed_train": len(mixed_train),
            "exam_valid": len(exam_valid),
            "practical_dev": len(practical_dev),
            "bridge": len(bridge),
        },
        "max_tokens": MAX_TOKENS,
        "seed": seed,
        "dataset_status": "private_unpublished_deepseek_curated_unreviewed",
    }
    return mixed_train, exam_valid, practical_dev, bridge, manifest


def selection_pass(baseline: dict, trained: dict) -> bool:
    return (
        trained["exam_valid"]["accuracy"] > baseline["exam_valid"]["accuracy"]
        and trained["practical_dev"]["accuracy"] >= baseline["practical_dev"]["accuracy"] - 0.02
        and trained["bridge"]["accuracy"] >= baseline["bridge"]["accuracy"] - 0.02
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--lr", type=float, default=1.5e-6)
    parser.add_argument("--seed", type=int, default=20260923)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.epochs <= 4:
        raise ValueError("epochs must be 1..4")
    mixed_train, exam_valid, practical_dev, bridge, manifest = preflight(args.output_dir, args.seed)
    config = {
        "base": str(BASE),
        "epochs": args.epochs,
        "lr": args.lr,
        "seed": args.seed,
        "device": args.device,
        "max_tokens": MAX_TOKENS,
        "micro_batch_size": 2,
        "gradient_accumulation_steps": 8,
        "optimizer_steps_per_epoch": math.ceil(math.ceil(len(mixed_train) / 2) / 8),
    }
    print(json.dumps({"manifest": manifest, "config": config}, ensure_ascii=False, indent=2), flush=True)
    if args.dry_run:
        return

    import torch
    from erabi.train import Trainer
    from train_practical_v1 import train_one_epoch

    if not args.device.startswith("cuda") or not torch.cuda.is_available():
        raise RuntimeError("This experiment requires one CUDA GPU")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    (args.output_dir / "manifest.json").write_text(json.dumps({"manifest": manifest, "config": config}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    trainer = Trainer(
        model_id=str(BASE),
        device=args.device,
        lr=args.lr,
        weight_decay=0.01,
        micro_batch_size=2,
        gradient_accumulation_steps=8,
        seed=args.seed,
    )
    trainer.pipeline.pipe.max_length = MAX_TOKENS
    baseline = {
        "exam_valid": trainer.evaluate(exam_valid),
        "practical_dev": trainer.evaluate(practical_dev),
        "bridge": trainer.evaluate(bridge),
    }
    print(
        f"baseline exam={baseline['exam_valid']['accuracy']:.4f} "
        f"practical={baseline['practical_dev']['accuracy']:.4f} bridge={baseline['bridge']['accuracy']:.4f}",
        flush=True,
    )
    epochs = []
    best_epoch = None
    best_accuracy = -1.0
    for epoch in range(1, args.epochs + 1):
        training = train_one_epoch(mixed_train, trainer, args.lr, args.seed + epoch - 1)
        metrics = {
            "exam_valid": trainer.evaluate(exam_valid),
            "practical_dev": trainer.evaluate(practical_dev),
            "bridge": trainer.evaluate(bridge),
        }
        passed = selection_pass(baseline, metrics)
        entry = {"epoch": epoch, "training": training, "metrics": metrics, "selection_pass": passed}
        epochs.append(entry)
        print(
            f"epoch={epoch} exam={metrics['exam_valid']['accuracy']:.4f} "
            f"practical={metrics['practical_dev']['accuracy']:.4f} bridge={metrics['bridge']['accuracy']:.4f} pass={passed}",
            flush=True,
        )
        if passed and metrics["exam_valid"]["accuracy"] > best_accuracy:
            best_accuracy = metrics["exam_valid"]["accuracy"]
            best_epoch = epoch
            trainer.save_checkpoint(str(args.output_dir / "checkpoint"))
    summary = {
        "manifest": manifest,
        "config": config,
        "baseline": baseline,
        "epochs": epochs,
        "best_epoch": best_epoch,
        "selection_pass": best_epoch is not None,
        "criterion": "Exam-QA official-choice valid accuracy strictly improves; Practical V1 dev and RC3 Bridge each drop by no more than 2 percentage points.",
        "limitations": [
            "Exam-QA valid is group-disjoint but not an untouched final test.",
            "DeepSeek-generated distractors are train-only and are not human-reviewed gold.",
            "1024-token operation is experimental; the public package default remains 512 until separately promoted.",
        ],
    }
    (args.output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"best_epoch": best_epoch, "selection_pass": best_epoch is not None}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
