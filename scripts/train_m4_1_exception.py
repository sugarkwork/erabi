"""Training script for M4.1 Exception Priority experiment.

Executes a single standard Cross-Entropy fine-tuning run on 840 combined cases:
- 600 existing train cases from data/m3_3_v2/train.jsonl
- 240 new exception priority cases from data/m4_1_exception/train_exception.jsonl

Dev evaluation on 140 cases:
- 100 existing dev cases
- 40 new dev exception cases

Saves best checkpoint to runs/m4_1_exception/trained/checkpoint.
Does NOT overwrite existing baseline checkpoints or calibration.
"""

from __future__ import annotations

import json
import logging
import os
import random
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from erabi.train import Trainer, set_seed
from erabi.schema import ChoiceRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.train_m4_1")

OUT_DIR = ROOT / "runs/m4_1_exception/trained"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_FILE = ROOT / "data/m4_1_exception/combined_train.jsonl"
DEV_FILE = ROOT / "data/m4_1_exception/combined_dev.jsonl"


def evaluate_dev(trainer: Trainer, dev_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    trainer.model.eval()
    inner_pipe = trainer.pipeline.pipe

    correct_count = 0
    total_nll = 0.0
    results = []

    with torch.inference_mode():
        for row in dev_records:
            req = ChoiceRequest.from_dict(row)
            labels = [c.text for c in req.choices]
            target_cid = row["target"]["choice_id"]
            target_idx = next(i for i, c in enumerate(req.choices) if c.id == target_cid)

            tokenized = inner_pipe.prepare_inputs(
                texts=[req.context],
                labels=[labels],
                same_labels=False,
                prompt=[req.question],
            )
            max_num_classes = inner_pipe._resolve_max_num_classes([labels], same_labels=False)
            outputs = trainer.model(**tokenized, max_num_classes=max_num_classes)
            sample_logits = outputs.logits[0, : len(labels)].to(torch.float32)

            pred_idx = int(torch.argmax(sample_logits).item())
            is_corr = (pred_idx == target_idx)
            if is_corr:
                correct_count += 1

            log_probs = F.log_softmax(sample_logits.to(torch.float64), dim=-1)
            nll_val = -float(log_probs[target_idx].item())
            total_nll += nll_val

            results.append({
                "group_id": row.get("group_id"),
                "is_correct": is_corr,
                "target_idx": target_idx,
                "pred_idx": pred_idx,
                "task_family": row.get("task_family"),
            })

    n = len(dev_records)
    acc = correct_count / n
    mean_nll = total_nll / n

    # Analyze pairs
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in results:
        gid = r.get("group_id")
        if gid:
            groups.setdefault(gid, []).append(r)

    paired = {k: v for k, v in groups.items() if len(v) == 2}
    both_correct = sum(1 for v in paired.values() if v[0]["is_correct"] and v[1]["is_correct"])
    pair_rate = both_correct / len(paired) if paired else 0.0

    # Exception task specific
    exc_results = [r for r in results if r.get("task_family") == "exception_priority"]
    exc_acc = (sum(1 for r in exc_results if r["is_correct"]) / len(exc_results)) if exc_results else 0.0

    return {
        "count": n,
        "accuracy": acc,
        "mean_nll": mean_nll,
        "total_pairs": len(paired),
        "both_correct_pairs": both_correct,
        "pair_rate": pair_rate,
        "exception_accuracy": exc_acc,
    }


def main():
    set_seed(42)
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")

    train_records = [json.loads(line) for line in open(TRAIN_FILE, encoding="utf-8") if line.strip()]
    dev_records = [json.loads(line) for line in open(DEV_FILE, encoding="utf-8") if line.strip()]
    logger.info(f"Loaded {len(train_records)} train records and {len(dev_records)} dev records.")

    trainer = Trainer(
        model_id="knowledgator/gliclass-instruct-base-v1.0",
        device=device,
        lr=2e-5,
        weight_decay=0.01,
        max_norm=1.0,
        gradient_accumulation_steps=8,
        micro_batch_size=2,
        seed=42,
    )

    epochs = 10
    best_score = -1.0
    best_epoch = -1
    best_checkpoint_dir = OUT_DIR / "checkpoint"
    history = []

    logger.info(f"Starting standard CE training for {epochs} epochs...")
    t0_train = time.time()

    for epoch in range(1, epochs + 1):
        t0_ep = time.time()
        trainer.model.train()

        # Shuffle training set
        rng = random.Random(42 + epoch)
        shuffled_records = list(train_records)
        rng.shuffle(shuffled_records)

        # Micro batches
        micro_batches = [
            shuffled_records[i : i + trainer.micro_batch_size]
            for i in range(0, len(shuffled_records), trainer.micro_batch_size)
        ]

        total_loss = 0.0
        num_windows = (len(micro_batches) + trainer.gradient_accumulation_steps - 1) // trainer.gradient_accumulation_steps

        for w_idx in range(num_windows):
            w_start = w_idx * trainer.gradient_accumulation_steps
            w_end = min(w_start + trainer.gradient_accumulation_steps, len(micro_batches))
            w_batches = micro_batches[w_start:w_end]

            w_total_samples = sum(len(b) for b in w_batches)
            trainer.optimizer.zero_grad()

            for b in w_batches:
                tokenized, target_indices, _, _ = trainer.prepare_batch(b, shuffle_choices=False, rng=rng)
                labels_count = [len(r["choices"]) for r in b]
                max_classes = max(labels_count)

                outputs = trainer.model(**tokenized, max_num_classes=max_classes)
                # Compute loss with exact window weighting
                batch_loss = torch.tensor(0.0, device=trainer.device)
                for i, (tgt, l_cnt) in enumerate(zip(target_indices, labels_count)):
                    logits = outputs.logits[i, :l_cnt]
                    batch_loss = batch_loss + F.cross_entropy(logits.unsqueeze(0), torch.tensor([tgt], device=trainer.device))

                # Weight by mini-batch size / window sample count
                weighted_loss = batch_loss / w_total_samples
                weighted_loss.backward()
                total_loss += batch_loss.item()

            torch.nn.utils.clip_grad_norm_(trainer.model.parameters(), trainer.max_norm)
            trainer.optimizer.step()

        ep_duration = time.time() - t0_ep
        avg_loss = total_loss / len(train_records)

        # Evaluate on dev
        dev_m = evaluate_dev(trainer, dev_records)
        score = dev_m["accuracy"] + dev_m["pair_rate"]

        logger.info(
            f"Epoch {epoch:2d}/{epochs} | Loss: {avg_loss:.4f} | Dev Acc: {dev_m['accuracy']*100:.1f}% | "
            f"Dev Pair: {dev_m['pair_rate']*100:.1f}% ({dev_m['both_correct_pairs']}/{dev_m['total_pairs']}) | "
            f"Dev Exc Acc: {dev_m['exception_accuracy']*100:.1f}% | NLL: {dev_m['mean_nll']:.4f} | {ep_duration:.1f}s"
        )

        history.append({
            "epoch": epoch,
            "train_loss": avg_loss,
            "dev_metrics": dev_m,
            "epoch_seconds": ep_duration,
        })

        if score > best_score:
            best_score = score
            best_epoch = epoch
            logger.info(f"--> New best model at Epoch {epoch}! Saving checkpoint to {best_checkpoint_dir}...")
            trainer.model.save_pretrained(best_checkpoint_dir)
            trainer.tokenizer.save_pretrained(best_checkpoint_dir)

    total_time = time.time() - t0_train
    logger.info(f"Training finished in {total_time/60:.2f} minutes. Best Epoch: {best_epoch} (Score: {best_score:.4f})")

    # Save training record
    summary = {
        "epochs": epochs,
        "best_epoch": best_epoch,
        "best_score": best_score,
        "total_seconds": total_time,
        "history": history,
    }
    with open(OUT_DIR / "training_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
