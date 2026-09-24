"""Train on a reshuffled private Exam-QA split with a sealed final test."""

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
sys.path.insert(0, str(ROOT / "scripts"))

BASE = ROOT / "runs" / "practical_v1_finetune_20260922" / "checkpoint"
DATA = ROOT / "data" / "exam_qa_erabi_v1_reshuffle_20260924"
PRACTICAL = ROOT / "data" / "practical_v1"
BRIDGE = ROOT / "data" / "rc3_bridge" / "rc3_bridge_benchmark.jsonl"
DEFAULT_OUTPUT = ROOT / "runs" / "exam_qa_reshuffle_v1_finetune_20260924"
MAX_TOKENS = 1024


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def select_replay(records: list[dict], count: int, seed: int) -> list[dict]:
    shuffled = list(records)
    random.Random(seed).shuffle(shuffled)
    selected = json.loads(json.dumps(shuffled[:count], ensure_ascii=False))
    for index, row in enumerate(selected):
        row["id"] = f"reshuffle_replay_{index}_{row['id']}"
        row["group_id"] = f"reshuffle_replay_{row['group_id']}"
        row["split"] = "train"
    return selected


def retention_pass(baseline: dict, trained: dict) -> bool:
    return (
        trained["practical_dev"]["accuracy"] >= baseline["practical_dev"]["accuracy"] - 0.02
        and trained["bridge"]["accuracy"] >= baseline["bridge"]["accuracy"] - 0.02
    )


def production_candidate(baseline: dict, candidate: dict) -> bool:
    final_gain = candidate["final_test"]["accuracy"] - baseline["final_test"]["accuracy"]
    return (
        final_gain >= 0.05
        and candidate["dev"]["accuracy"] > baseline["dev"]["accuracy"]
        and retention_pass(baseline, candidate)
        and candidate["practical_eval"]["accuracy"] >= baseline["practical_eval"]["accuracy"] - 0.01
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DATA)
    parser.add_argument("--base-model", type=Path, default=BASE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--lr", type=float, default=1.5e-6)
    parser.add_argument("--seed", type=int, default=20260924)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    if not 1 <= args.epochs <= 4:
        raise ValueError("epochs must be 1..4")

    paths = {
        "base": args.base_model / "model.safetensors",
        "exam_train": args.data_dir / "train.jsonl",
        "exam_dev": args.data_dir / "dev.jsonl",
        "exam_final_test": args.data_dir / "final_test.jsonl",
        "split_manifest": args.data_dir / "split_manifest.json",
        "practical_train": PRACTICAL / "train.jsonl",
        "practical_dev": PRACTICAL / "dev.jsonl",
        "practical_eval": PRACTICAL / "eval_teacher_agreed.jsonl",
        "bridge": BRIDGE,
    }
    for name, path in paths.items():
        if not path.is_file():
            raise FileNotFoundError(f"Missing {name}: {path}")
    exam_train = read_jsonl(paths["exam_train"])
    exam_dev = read_jsonl(paths["exam_dev"])
    exam_final = read_jsonl(paths["exam_final_test"])
    groups = [{row["group_id"] for row in split} for split in (exam_train, exam_dev, exam_final)]
    if groups[0] & groups[1] or groups[0] & groups[2] or groups[1] & groups[2]:
        raise ValueError("Exam split group overlap")
    if any(row.get("input_tokens", MAX_TOKENS + 1) > MAX_TOKENS for row in exam_train + exam_dev + exam_final):
        raise ValueError("Exam input exceeds 1024-token contract")
    practical_train = read_jsonl(paths["practical_train"])
    suites = {
        "dev": exam_dev,
        "final_test": exam_final,
        "practical_dev": read_jsonl(paths["practical_dev"]),
        "practical_eval": read_jsonl(paths["practical_eval"]),
        "bridge": read_jsonl(paths["bridge"]),
    }
    replay = select_replay(practical_train, len(exam_train), args.seed)
    mixed_train = exam_train + replay
    manifest = {
        "files": {name: {"path": str(path), "sha256": sha256(path)} for name, path in paths.items()},
        "counts": {
            "exam_train": len(exam_train), "replay": len(replay), "mixed_train": len(mixed_train),
            **{name: len(rows) for name, rows in suites.items()},
        },
        "config": {
            "epochs": args.epochs, "lr": args.lr, "seed": args.seed, "device": args.device,
            "max_tokens": MAX_TOKENS, "micro_batch_size": 2, "gradient_accumulation_steps": 8,
            "optimizer_steps_per_epoch": math.ceil(math.ceil(len(mixed_train) / 2) / 8),
        },
        "final_test_policy": "Sealed during epoch selection; evaluated once on the selected checkpoint.",
    }
    print(json.dumps(manifest, ensure_ascii=False, indent=2), flush=True)
    if args.dry_run:
        return

    import torch
    from erabi.train import Trainer
    from train_practical_v1 import train_one_epoch

    if not args.device.startswith("cuda") or not torch.cuda.is_available():
        raise RuntimeError("This experiment requires one CUDA GPU")
    args.output_dir.mkdir(parents=True)
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    trainer = Trainer(
        model_id=str(args.base_model), device=args.device, lr=args.lr, weight_decay=0.01,
        micro_batch_size=2, gradient_accumulation_steps=8, seed=args.seed,
    )
    trainer.pipeline.pipe.max_length = MAX_TOKENS
    baseline = {name: trainer.evaluate(rows) for name, rows in suites.items()}
    print(
        f"baseline dev={baseline['dev']['accuracy']:.4f} final={baseline['final_test']['accuracy']:.4f} "
        f"practical={baseline['practical_dev']['accuracy']:.4f} bridge={baseline['bridge']['accuracy']:.4f}",
        flush=True,
    )
    epochs = []
    best_epoch = None
    best_key = None
    for epoch in range(1, args.epochs + 1):
        training = train_one_epoch(mixed_train, trainer, args.lr, args.seed + epoch - 1)
        metrics = {
            "dev": trainer.evaluate(suites["dev"]),
            "practical_dev": trainer.evaluate(suites["practical_dev"]),
            "bridge": trainer.evaluate(suites["bridge"]),
        }
        passed = metrics["dev"]["accuracy"] > baseline["dev"]["accuracy"] and retention_pass(baseline, metrics)
        epochs.append({"epoch": epoch, "training": training, "metrics": metrics, "selection_pass": passed})
        print(
            f"epoch={epoch} dev={metrics['dev']['accuracy']:.4f} "
            f"practical={metrics['practical_dev']['accuracy']:.4f} bridge={metrics['bridge']['accuracy']:.4f} pass={passed}",
            flush=True,
        )
        key = (metrics["dev"]["accuracy"], -metrics["dev"]["mean_nll"], metrics["practical_dev"]["accuracy"])
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
        selected_trainer = Trainer(
            model_id=str(args.output_dir / "checkpoint"), device=args.device, lr=args.lr,
            weight_decay=0.01, micro_batch_size=2, gradient_accumulation_steps=8, seed=args.seed,
        )
        selected_trainer.pipeline.pipe.max_length = MAX_TOKENS
        selected = {
            "dev": selected_trainer.evaluate(suites["dev"]),
            "final_test": selected_trainer.evaluate(suites["final_test"]),
            "practical_dev": selected_trainer.evaluate(suites["practical_dev"]),
            "practical_eval": selected_trainer.evaluate(suites["practical_eval"]),
            "bridge": selected_trainer.evaluate(suites["bridge"]),
        }
        promoted = production_candidate(baseline, selected)
        print(
            f"selected epoch={best_epoch} final={selected['final_test']['accuracy']:.4f} "
            f"baseline_final={baseline['final_test']['accuracy']:.4f} production_candidate={promoted}",
            flush=True,
        )
    summary = {
        "manifest": manifest,
        "baseline": baseline,
        "epochs": epochs,
        "best_epoch": best_epoch,
        "selected": selected,
        "production_candidate": promoted,
        "production_criterion": "Final-test gain >=5 points, dev strictly improves, Practical dev/Bridge lose <=2 points, Practical eval loses <=1 point.",
        "limitations": [
            "The private final test is small and DeepSeek-curated, not human-reviewed gold.",
            "The earlier public Exam-QA model used a different split, so its Exam score is not directly comparable.",
            "No public model is overwritten unless the production criterion passes and follow-up parity checks succeed.",
        ],
    }
    (args.output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"best_epoch": best_epoch, "production_candidate": promoted}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
