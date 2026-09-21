"""Level 4: Mid-Size Compatible Backbone Training & Milestone 31 Development Gate.

Backbone: knowledgator/gliclass-instruct-large-v1.0 (438M parameters)
Dataset: data/rc3_train/train.jsonl (8,650 records, 4,325 pairs)
Effective batch size: 16 (micro_batch_size=1, gradient_accumulation_steps=16)
Optimization: AdamW, AMP FP16, Cosine Decay with Warmup.
"""

from __future__ import annotations

import argparse
import copy
import datetime
import gc
import json
import logging
import math
from pathlib import Path
import random
import shutil
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer
from gliclass import GLiClassModel, ZeroShotClassificationPipeline

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from erabi.inference import GLiClassEngine
from erabi.schema import ChoiceRequest
from erabi.train import set_seed
from scripts.train_rc3 import evaluate_records, evaluate_development_gate, load_jsonl

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.train_rc3_large")

MODEL_ID = "knowledgator/gliclass-instruct-large-v1.0"
TRAIN_FILE = ROOT / "data" / "rc3_train" / "train.jsonl"
DEV_FILE = ROOT / "data" / "rc3_train" / "dev.jsonl"
BRIDGE_BENCHMARK_FILE = ROOT / "data" / "rc3_bridge" / "rc3_bridge_benchmark.jsonl"
EVAL_V2_FILE = ROOT / "data" / "m3_3_v2" / "eval_v2.jsonl"


def train_rc3_large(
    epochs: int = 3,
    lr: float = 1.5e-5,
    micro_batch_size: int = 2,
    gradient_accumulation_steps: int = 8,
    use_amp: bool = True,
    warmup_ratio: float = 0.08,
    weight_decay: float = 0.01,
    max_norm: float = 1.0,
    seed: int = 42,
    runs_dir: Optional[Path] = None,
    device: Optional[str] = None,
) -> Path:
    device = device or ("cuda:0" if torch.cuda.is_available() else "cpu")
    r_dir = runs_dir or (ROOT / "runs" / "rc3_large_curriculum")
    checkpoints_dir = r_dir / "checkpoints"
    best_model_dir = r_dir / "best_model"

    r_dir.mkdir(parents=True, exist_ok=True)
    checkpoints_dir.mkdir(parents=True, exist_ok=True)

    train_records = load_jsonl(TRAIN_FILE)
    dev_records = load_jsonl(DEV_FILE)
    bridge_records = load_jsonl(BRIDGE_BENCHMARK_FILE)
    eval_v2_records = load_jsonl(EVAL_V2_FILE)

    logger.info(f"Loaded {len(train_records)} train, {len(dev_records)} dev, {len(bridge_records)} bridge, {len(eval_v2_records)} eval_v2 records.")
    logger.info(f"Using Backbone: {MODEL_ID} (438M parameters)")
    logger.info(f"Effective batch size: {micro_batch_size * gradient_accumulation_steps} (micro={micro_batch_size}, accum={gradient_accumulation_steps})")

    set_seed(seed)
    logger.info(f"Instantiating model & tokenizer on {device}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = GLiClassModel.from_pretrained(MODEL_ID)
    model.to(device)

    pipeline = ZeroShotClassificationPipeline(
        model=model,
        tokenizer=tokenizer,
        classification_type="single-label",
        device=device,
    )
    inner_pipe = pipeline.pipe

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=lr,
        weight_decay=weight_decay,
        eps=1e-8,
    )

    scaler = torch.amp.GradScaler("cuda", enabled=use_amp and "cuda" in device)

    total_micro_batches_per_ep = (len(train_records) + micro_batch_size - 1) // micro_batch_size
    steps_per_epoch = (total_micro_batches_per_ep + gradient_accumulation_steps - 1) // gradient_accumulation_steps
    total_steps = steps_per_epoch * epochs
    warmup_steps = max(50, int(total_steps * warmup_ratio))

    logger.info(f"Total steps: {total_steps}, Warmup steps: {warmup_steps}, Peak LR: {lr:.2e}, AMP: {use_amp}")

    def get_lr(step: int) -> float:
        if step < warmup_steps:
            return lr * (step + 1) / warmup_steps
        progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
        return 1e-6 + 0.5 * (lr - 1e-6) * (1.0 + math.cos(math.pi * progress))

    t0_start = time.time()
    total_opt_steps = 0
    epoch_results: Dict[int, Dict[str, Any]] = {}

    for epoch in range(1, epochs + 1):
        t0_ep = time.time()
        model.train()
        rng = random.Random(seed + epoch * 100)

        # Group shuffle: keep paired records adjacent while shuffling group sequence
        groups: Dict[str, List[Dict[str, Any]]] = {}
        for r in train_records:
            groups.setdefault(r["group_id"], []).append(r)
        group_list = list(groups.values())
        rng.shuffle(group_list)

        shuffled_train: List[Dict[str, Any]] = []
        for g in group_list:
            shuffled_train.extend(g)

        micro_batches = []
        for i in range(0, len(shuffled_train), micro_batch_size):
            micro_batches.append(shuffled_train[i:i + micro_batch_size])

        total_loss = 0.0
        num_windows = (len(micro_batches) + gradient_accumulation_steps - 1) // gradient_accumulation_steps

        for w_idx in range(num_windows):
            w_start = w_idx * gradient_accumulation_steps
            w_end = min(w_start + gradient_accumulation_steps, len(micro_batches))
            w_batches = micro_batches[w_start:w_end]
            w_total_samples = sum(len(b) for b in w_batches)

            cur_lr = get_lr(total_opt_steps)
            for pg in optimizer.param_groups:
                pg["lr"] = cur_lr

            optimizer.zero_grad()

            for b in w_batches:
                # Prepare batch inputs with choice shuffling
                texts, labels_list, prompts, target_indices = [], [], [], []
                for row in b:
                    c_list = list(row["choices"])
                    rng.shuffle(c_list)
                    tgt_cid = row["target"]["choice_id"]
                    target_indices.append(next(i for i, c in enumerate(c_list) if c["id"] == tgt_cid))
                    texts.append(row.get("context", ""))
                    labels_list.append([c["text"] for c in c_list])
                    prompts.append(row.get("question", ""))

                tokenized = inner_pipe.prepare_inputs(
                    texts=texts,
                    labels=labels_list,
                    same_labels=False,
                    prompt=prompts,
                )
                tokenized = {k: v.to(device) if hasattr(v, "to") else v for k, v in tokenized.items()}
                max_classes = max(len(lbls) for lbls in labels_list)

                with torch.amp.autocast("cuda", enabled=use_amp and "cuda" in device):
                    outputs = model(**tokenized, max_num_classes=max_classes)
                    batch_loss = torch.tensor(0.0, device=device)
                    for i, (tgt, lbls) in enumerate(zip(target_indices, labels_list)):
                        logits = outputs.logits[i, :len(lbls)].to(torch.float32)
                        batch_loss = batch_loss + F.cross_entropy(logits.unsqueeze(0), torch.tensor([tgt], device=device))

                    weighted_loss = batch_loss / w_total_samples

                scaler.scale(weighted_loss).backward()
                total_loss += batch_loss.item()

            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm)
            scaler.step(optimizer)
            scaler.update()
            total_opt_steps += 1

            if total_opt_steps % 100 == 0 or total_opt_steps == total_steps:
                logger.info(f"Epoch {epoch:2d}/{epochs} | Step {total_opt_steps:4d}/{total_steps} | Loss: {batch_loss.item():.4f} | LR: {cur_lr:.2e}")

        ep_duration = time.time() - t0_ep
        avg_loss = total_loss / len(shuffled_train)
        logger.info(f"=== Epoch {epoch:2d} Finished in {ep_duration:.1f}s | Avg Train Loss: {avg_loss:.4f} ===")

        # Save checkpoint
        ep_dir = checkpoints_dir / f"epoch_{epoch}"
        ep_dir.mkdir(parents=True, exist_ok=True)
        model.save_pretrained(ep_dir)
        tokenizer.save_pretrained(ep_dir)

        # Evaluate using GLiClassEngine
        logger.info(f"Evaluating Epoch {epoch} checkpoints on Dev, eval_v2, and Bridge Benchmark...")
        eval_engine = GLiClassEngine(model_id=str(ep_dir), device=device)

        dev_eval = evaluate_records(eval_engine, dev_records, test_permutation=False)
        ev2_eval = evaluate_records(eval_engine, eval_v2_records, test_permutation=False)
        bridge_eval = evaluate_records(eval_engine, bridge_records, test_permutation=True, seed=42)

        del eval_engine
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()

        logger.info(
            f"Epoch {epoch:2d} Results:\n"
            f"  - Dev Acc: {dev_eval['accuracy']*100:.2f}% (Paired: {dev_eval['paired_both_rate']*100:.2f}%)\n"
            f"  - eval_v2 Core: {ev2_eval['accuracy']*100:.2f}%\n"
            f"  - Bridge Overall: {bridge_eval['accuracy']*100:.2f}% (Paired: {bridge_eval['paired_both_rate']*100:.2f}%, Perm: {bridge_eval['permutation_consistency']*100:.2f}%)\n"
            f"    * logical_operators: {bridge_eval['by_family'].get('logical_operators', {}).get('accuracy', 0.0)*100:.2f}%\n"
            f"    * priority_exception: {bridge_eval['by_family'].get('priority_exception', {}).get('accuracy', 0.0)*100:.2f}%\n"
            f"    * variable_choice: {bridge_eval['by_family'].get('variable_choice', {}).get('accuracy', 0.0)*100:.2f}%\n"
            f"    * perturbation_invariance: {bridge_eval['by_family'].get('perturbation_invariance', {}).get('accuracy', 0.0)*100:.2f}%"
        )

        epoch_results[epoch] = {
            "epoch": epoch,
            "loss": avg_loss,
            "dev_acc": dev_eval["accuracy"],
            "dev_paired": dev_eval["paired_both_rate"],
            "eval_v2_acc": ev2_eval["accuracy"],
            "bridge_acc": bridge_eval["accuracy"],
            "bridge_paired": bridge_eval["paired_both_rate"],
            "bridge_perm": bridge_eval["permutation_consistency"],
            "bridge_families": {f: s["accuracy"] for f, s in bridge_eval["by_family"].items()},
            "checkpoint_dir": str(ep_dir),
        }

    total_training_time = time.time() - t0_start
    logger.info(f"All {epochs} epochs completed in {total_training_time:.1f}s.")

    # Select best epoch by:
    # 1. eval_v2 >= 0.96 (core retention guarantee)
    # 2. bridge_acc highest
    qualifying = [ep for ep, r in epoch_results.items() if r["eval_v2_acc"] >= 0.96]
    if not qualifying:
        qualifying = [ep for ep, r in epoch_results.items() if r["eval_v2_acc"] >= 0.94]
    if not qualifying:
        qualifying = list(epoch_results.keys())

    best_ep = max(qualifying, key=lambda ep: (epoch_results[ep]["bridge_acc"], epoch_results[ep]["bridge_paired"]))
    best_ckpt = Path(epoch_results[best_ep]["checkpoint_dir"])
    logger.info(f"Selected Best Epoch: {best_ep} (Bridge: {epoch_results[best_ep]['bridge_acc']*100:.2f}%, eval_v2: {epoch_results[best_ep]['eval_v2_acc']*100:.2f}%)")

    if best_model_dir.exists():
        shutil.rmtree(best_model_dir)
    shutil.copytree(best_ckpt, best_model_dir)
    logger.info(f"Copied best checkpoint to {best_model_dir}")

    # Save summary
    summary_path = r_dir / "training_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "backbone": MODEL_ID,
            "epochs": epochs,
            "peak_lr": lr,
            "best_epoch": best_ep,
            "best_bridge_acc": epoch_results[best_ep]["bridge_acc"],
            "epoch_results": epoch_results,
            "total_time_seconds": total_training_time,
        }, f, indent=2, ensure_ascii=False)

    # Run full Milestone 31 Development Gate evaluation
    logger.info("=== Running Full Milestone 31 Development Gate Evaluation ===")
    dev_gate_results = evaluate_development_gate(best_model_dir, device=device, output_dir=r_dir)
    logger.info(f"Dev Gate Complete: Gate Passed = {dev_gate_results['milestone_31_gate_passed']}")

    return best_model_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train RC3 Large Compatible Backbone")
    parser.add_argument("--epochs", type=int, default=3, help="Number of epochs")
    parser.add_argument("--lr", type=float, default=1.5e-5, help="Peak learning rate")
    parser.add_argument("--runs-dir", type=str, default="runs/rc3_large_curriculum", help="Directory to save runs")
    parser.add_argument("--micro-batch-size", type=int, default=2, help="Micro batch size")
    parser.add_argument("--grad-accum", type=int, default=8, help="Gradient accumulation steps")
    parser.add_argument("--no-amp", action="store_true", help="Disable AMP")
    parser.add_argument("--device", type=str, default=None, help="Device")
    args = parser.parse_args()

    train_rc3_large(
        epochs=args.epochs,
        lr=args.lr,
        micro_batch_size=args.micro_batch_size,
        gradient_accumulation_steps=args.grad_accum,
        use_amp=not args.no_amp,
        runs_dir=Path(args.runs_dir) if args.runs_dir else None,
        device=args.device,
    )
