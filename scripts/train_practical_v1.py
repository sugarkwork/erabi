"""One-epoch practical-data diagnostic from frozen RC3; never promotes weights."""

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

BASE = ROOT / "release" / "rc3" / "model"
DATA = ROOT / "data" / "practical_v1"
BRIDGE = ROOT / "data" / "rc3_bridge" / "rc3_bridge_benchmark.jsonl"
DEFAULT_OUTPUT = ROOT / "runs" / "practical_v1_finetune_20260922"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def preflight(output: Path) -> tuple[list[dict], list[dict], list[dict], dict]:
    if output.exists():
        raise FileExistsError(f"Output already exists: {output}")
    paths = {"base": BASE / "model.safetensors", "train": DATA / "train.jsonl", "dev": DATA / "dev.jsonl", "bridge": BRIDGE}
    for name, path in paths.items():
        if not path.is_file():
            raise FileNotFoundError(f"Missing {name}: {path}")
    train, dev, bridge = (read_jsonl(paths[name]) for name in ("train", "dev", "bridge"))
    if not train or not dev or not bridge:
        raise ValueError("Training, dev, and retention suites must be nonempty")
    if any(row.get("review_status") != "same_model_blind_agreement_unreviewed" for row in train + dev):
        raise ValueError("Practical records must be screened and marked unreviewed")
    train_groups = {row["group_id"] for row in train}
    dev_groups = {row["group_id"] for row in dev}
    if train_groups & dev_groups:
        raise ValueError("Train/dev group overlap")
    audit = json.loads((DATA / "audit.json").read_text(encoding="utf-8"))
    for name in ("train", "dev"):
        if audit["sha256"][f"{name}.jsonl"] != sha256(paths[name]):
            raise ValueError(f"{name} file differs from audited corpus")
    manifest = {"files": {name: {"path": str(path), "sha256": sha256(path)} for name, path in paths.items()}, "counts": {"train": len(train), "dev": len(dev), "bridge": len(bridge)}}
    return train, dev, bridge, manifest


def train_one_epoch(train: list[dict], trainer, lr: float, seed: int) -> dict:
    import torch
    import torch.nn.functional as F

    micro_batch_size = 2
    accumulation = 8
    warmup = 20
    floor = 5e-7
    rng = random.Random(seed)
    shuffled = list(train)
    rng.shuffle(shuffled)
    batches = [shuffled[i : i + micro_batch_size] for i in range(0, len(shuffled), micro_batch_size)]
    windows = math.ceil(len(batches) / accumulation)
    scaler = torch.amp.GradScaler("cuda", enabled=True)
    trainer.model.train()
    total_loss = 0.0
    for window in range(windows):
        group = batches[window * accumulation : (window + 1) * accumulation]
        sample_count = sum(len(batch) for batch in group)
        if window < warmup:
            current_lr = lr * (window + 1) / warmup
        else:
            fraction = (window - warmup) / max(1, windows - warmup - 1)
            current_lr = floor + .5 * (lr - floor) * (1 + math.cos(math.pi * fraction))
        for params in trainer.optimizer.param_groups:
            params["lr"] = current_lr
        trainer.optimizer.zero_grad(set_to_none=True)
        window_loss = 0.0
        for batch in group:
            inputs, targets, choice_counts, max_classes = trainer.prepare_batch(batch, shuffle_choices=True, rng=rng)
            with torch.amp.autocast("cuda", dtype=torch.float16):
                outputs = trainer.model(**inputs, max_num_classes=max_classes)
                per_batch = torch.tensor(0.0, device=trainer.device)
                for index, (target, count) in enumerate(zip(targets, choice_counts)):
                    logits = outputs.logits[index, :count].to(torch.float32)
                    per_batch = per_batch + F.cross_entropy(logits.unsqueeze(0), torch.tensor([target], device=trainer.device))
                loss = per_batch / sample_count
            if not torch.isfinite(loss):
                raise FloatingPointError(f"Nonfinite loss at optimizer window {window + 1}")
            scaler.scale(loss).backward()
            window_loss += float(per_batch.detach().cpu())
        scaler.unscale_(trainer.optimizer)
        torch.nn.utils.clip_grad_norm_(trainer.model.parameters(), 1.0)
        scaler.step(trainer.optimizer)
        scaler.update()
        total_loss += window_loss
        if (window + 1) % 10 == 0 or window + 1 == windows:
            print(f"step {window + 1}/{windows} mean_ce={total_loss / sum(len(b) for b in batches[: (window + 1) * accumulation]):.4f} lr={current_lr:.2e} scaler={scaler.get_scale():.0f}", flush=True)
    return {"optimizer_steps": windows, "mean_train_ce": total_loss / len(train), "learning_rate": lr, "micro_batch_size": micro_batch_size, "gradient_accumulation_steps": accumulation, "seed": seed, "precision": "fp16_amp"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--lr", type=float, default=2.5e-6)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    train, dev, bridge, manifest = preflight(args.output_dir)
    steps = math.ceil(math.ceil(len(train) / 2) / 8)
    print(json.dumps({"manifest": manifest, "config": {"epochs": 1, "optimizer_steps": steps, "lr": args.lr, "seed": args.seed, "device": args.device}}, ensure_ascii=False, indent=2), flush=True)
    if args.dry_run:
        return

    import torch
    from erabi.train import Trainer

    if not args.device.startswith("cuda") or not torch.cuda.is_available():
        raise RuntimeError("This diagnostic requires one available CUDA GPU")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    trainer = Trainer(model_id=str(BASE), device=args.device, lr=args.lr, weight_decay=.01, micro_batch_size=2, gradient_accumulation_steps=8, seed=args.seed)
    baseline_dev = trainer.evaluate(dev)
    baseline_bridge = trainer.evaluate(bridge)
    print(f"baseline dev={baseline_dev['accuracy']:.4f} bridge={baseline_bridge['accuracy']:.4f}", flush=True)
    training = train_one_epoch(train, trainer, args.lr, args.seed)
    checkpoint = args.output_dir / "checkpoint"
    trainer.save_checkpoint(str(checkpoint))
    trained_dev = trainer.evaluate(dev)
    trained_bridge = trainer.evaluate(bridge)
    selection_pass = trained_dev["accuracy"] > baseline_dev["accuracy"] and trained_bridge["accuracy"] >= baseline_bridge["accuracy"] - .02
    summary = {"manifest": manifest, "training": training, "baseline_dev": baseline_dev, "baseline_bridge": baseline_bridge, "trained_dev": trained_dev, "trained_bridge": trained_bridge, "selection_pass": selection_pass, "criterion": "dev accuracy improves and RC3 bridge accuracy drops by no more than 2 percentage points; exploratory only"}
    (args.output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"trained dev={trained_dev['accuracy']:.4f} bridge={trained_bridge['accuracy']:.4f} selection_pass={selection_pass}", flush=True)


if __name__ == "__main__":
    main()
