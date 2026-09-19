"""Training script for M4.4.1 Targeted Retention Replay (W_m4_4_1r).

Selector Coverage Fix:
Adds R1b (Equality Comparison): inventory == demand comparison pairs from M3 train.

Executes a single standard Cross-Entropy fine-tuning run from B0 on 1192 combined cases:
- 600 M3 base train cases (data/m3_3_v2/train.jsonl)
- 240 M4.1 exception train cases (data/m4_1_exception/train_exception.jsonl)
- 240 M4.3.1 phrasing train cases (data/m4_3_1_phrasing_fix/phrasing_train.jsonl)
- 112 targeted retention replay cases:
  - 48 R1 equality boundary
  - 8 R1b equality comparison (inventory == demand)
  - 56 R2 4-state balanced composite logic

Dev evaluation on 220 cases (identical to M4.3.1 / M4.4-R):
- 100 M3 base dev cases (with diagnostic display of R1, R1b, and R2 subsets)
- 40 M4.1 exception dev cases
- 80 M4.3.1 phrasing dev cases

Checkpoint Selection Criteria (maintained from M4.3.1 / M4.4-R):
1. M3 dev accuracy >= 95%
2. M4.1 exception dev accuracy >= 95%
3. Maximum M4.3.1 phrasing dev diff-target pair both
4. Tie-break: lowest phrasing dev NLL

Saves best checkpoint to runs/m4_4_1_retention/trained/checkpoint.
Does NOT overwrite existing baseline checkpoints or calibration.
"""

from __future__ import annotations

import json
import logging
import os
import random
import re
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
logger = logging.getLogger("erabi.train_m4_4_1r")

OUT_DIR = ROOT / "runs/m4_4_1_retention/trained"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_FILE = ROOT / "data/m4_4_1_retention/combined_train_retention.jsonl"
DEV_FILE = ROOT / "data/m4_3_1_phrasing_fix/combined_dev.jsonl"


def evaluate_dev(trainer: Trainer, dev_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    trainer.model.eval()
    inner_pipe = trainer.pipeline.pipe

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

            log_probs = F.log_softmax(sample_logits.to(torch.float64), dim=-1)
            nll_val = -float(log_probs[target_idx].item())

            # Identify R1, R1b, and R2 in dev
            rule_k = row.get("rule_kind")
            is_r1_dev = False
            if rule_k == "boundary":
                nums_ctx = [int(x) for x in re.findall(r"\d+", row.get("context", ""))]
                nums_q = [int(x) for x in re.findall(r"\d+", row.get("question", ""))]
                if nums_ctx and nums_q and nums_ctx[0] == nums_q[0]:
                    is_r1_dev = True

            is_r1b_dev = False
            if rule_k == "comparison":
                nums_ctx = [int(x) for x in re.findall(r"\d+", row.get("context", ""))]
                if len(nums_ctx) >= 2 and nums_ctx[0] == nums_ctx[1]:
                    is_r1b_dev = True

            is_r2_dev = (rule_k == "composite_logic")

            results.append({
                "id": row.get("id"),
                "group_id": row.get("group_id"),
                "is_correct": is_corr,
                "target_idx": target_idx,
                "pred_idx": pred_idx,
                "target_cid": target_cid,
                "task_family": row.get("task_family"),
                "conflict": row.get("conflict", False),
                "is_r1_dev": is_r1_dev,
                "is_r1b_dev": is_r1b_dev,
                "is_r2_dev": is_r2_dev,
                "nll": nll_val,
            })

    # Overall metrics
    n = len(dev_records)
    overall_corr = sum(1 for r in results if r["is_correct"])
    overall_acc = overall_corr / n
    overall_nll = sum(r["nll"] for r in results) / n

    # 1. M3 dev subset (100 cases)
    m3_results = [r for r in results if r.get("task_family") in ["explicit_rule", "goal_following"]]
    m3_acc = (sum(1 for r in m3_results if r["is_correct"]) / len(m3_results)) if m3_results else 0.0
    m3_nll = (sum(r["nll"] for r in m3_results) / len(m3_results)) if m3_results else 0.0

    # Diagnostic: R1, R1b, and R2 subsets on M3 dev
    r1_dev_res = [r for r in results if r.get("is_r1_dev")]
    r1_dev_acc = (sum(1 for r in r1_dev_res if r["is_correct"]) / len(r1_dev_res)) if r1_dev_res else 0.0
    r1b_dev_res = [r for r in results if r.get("is_r1b_dev")]
    r1b_dev_acc = (sum(1 for r in r1b_dev_res if r["is_correct"]) / len(r1b_dev_res)) if r1b_dev_res else 0.0
    r2_dev_res = [r for r in results if r.get("is_r2_dev")]
    r2_dev_acc = (sum(1 for r in r2_dev_res if r["is_correct"]) / len(r2_dev_res)) if r2_dev_res else 0.0

    # 2. M4.1 exception dev subset (40 cases)
    m4_1_results = [r for r in results if r.get("task_family") == "exception_priority"]
    m4_1_acc = (sum(1 for r in m4_1_results if r["is_correct"]) / len(m4_1_results)) if m4_1_results else 0.0
    m4_1_nll = (sum(r["nll"] for r in m4_1_results) / len(m4_1_results)) if m4_1_results else 0.0

    # 3. M4.3.1 phrasing dev subset (80 cases / 40 pairs)
    phr_results = [r for r in results if r.get("task_family") in ["phrasing_diversification", "phrasing_diversification_fix"]]
    phr_acc = (sum(1 for r in phr_results if r["is_correct"]) / len(phr_results)) if phr_results else 0.0
    phr_nll = (sum(r["nll"] for r in phr_results) / len(phr_results)) if phr_results else 0.0

    # Phrasing pairs analysis
    phr_groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in phr_results:
        gid = r.get("group_id")
        if gid:
            phr_groups.setdefault(gid, []).append(r)

    phr_both = 0
    phr_diff_pairs = 0
    phr_diff_both = 0
    phr_same_pairs = 0
    phr_same_both = 0

    for gid, pair in phr_groups.items():
        if len(pair) == 2:
            r1, r2 = pair[0], pair[1]
            is_both = r1["is_correct"] and r2["is_correct"]
            if is_both:
                phr_both += 1
            if r1["target_cid"] != r2["target_cid"]:
                phr_diff_pairs += 1
                if is_both:
                    phr_diff_both += 1
            else:
                phr_same_pairs += 1
                if is_both:
                    phr_same_both += 1

    return {
        "overall_count": n,
        "overall_accuracy": overall_acc,
        "overall_nll": overall_nll,
        "m3_count": len(m3_results),
        "m3_accuracy": m3_acc,
        "m3_nll": m3_nll,
        "diagnostic_r1_dev_count": len(r1_dev_res),
        "diagnostic_r1_dev_accuracy": r1_dev_acc,
        "diagnostic_r1b_dev_count": len(r1b_dev_res),
        "diagnostic_r1b_dev_accuracy": r1b_dev_acc,
        "diagnostic_r2_dev_count": len(r2_dev_res),
        "diagnostic_r2_dev_accuracy": r2_dev_acc,
        "m4_1_count": len(m4_1_results),
        "m4_1_accuracy": m4_1_acc,
        "m4_1_nll": m4_1_nll,
        "phrasing_count": len(phr_results),
        "phrasing_accuracy": phr_acc,
        "phrasing_nll": phr_nll,
        "phrasing_total_pairs": len(phr_groups),
        "phrasing_both_correct": phr_both,
        "phrasing_diff_pairs": phr_diff_pairs,
        "phrasing_diff_both": phr_diff_both,
        "phrasing_diff_rate": (phr_diff_both / phr_diff_pairs) if phr_diff_pairs > 0 else 0.0,
        "phrasing_same_pairs": phr_same_pairs,
        "phrasing_same_both": phr_same_both,
    }


def main():
    set_seed(42)
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")

    train_records = [json.loads(line) for line in open(TRAIN_FILE, encoding="utf-8") if line.strip()]
    dev_records = [json.loads(line) for line in open(DEV_FILE, encoding="utf-8") if line.strip()]
    logger.info(f"Loaded {len(train_records)} train records (with retention replay) and {len(dev_records)} dev records.")

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
    best_diff_both = -1
    best_phr_nll = float("inf")
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
                batch_loss = torch.tensor(0.0, device=trainer.device)
                for i, (tgt, l_cnt) in enumerate(zip(target_indices, labels_count)):
                    logits = outputs.logits[i, :l_cnt]
                    batch_loss = batch_loss + F.cross_entropy(logits.unsqueeze(0), torch.tensor([tgt], device=trainer.device))

                weighted_loss = batch_loss / w_total_samples
                weighted_loss.backward()
                total_loss += batch_loss.item()

            torch.nn.utils.clip_grad_norm_(trainer.model.parameters(), trainer.max_norm)
            trainer.optimizer.step()

        ep_duration = time.time() - t0_ep
        avg_loss = total_loss / len(train_records)

        # Evaluate on dev
        dev_m = evaluate_dev(trainer, dev_records)

        # Check eligibility:
        # 1. M3 dev accuracy >= 95%
        # 2. M4.1 exception dev accuracy >= 95%
        is_eligible = (dev_m["m3_accuracy"] >= 0.95 and dev_m["m4_1_accuracy"] >= 0.95)

        logger.info(
            f"Epoch {epoch:2d}/{epochs} | Loss: {avg_loss:.4f} | "
            f"M3 Acc: {dev_m['m3_accuracy']*100:.1f}% (R1: {dev_m['diagnostic_r1_dev_accuracy']*100:.0f}%, R1b: {dev_m['diagnostic_r1b_dev_accuracy']*100:.0f}%, R2: {dev_m['diagnostic_r2_dev_accuracy']*100:.0f}%) | "
            f"M4.1 Acc: {dev_m['m4_1_accuracy']*100:.1f}% | "
            f"Phr Acc: {dev_m['phrasing_accuracy']*100:.1f}% | "
            f"Phr Diff Both: {dev_m['phrasing_diff_both']:2d}/{dev_m['phrasing_diff_pairs']:2d} ({dev_m['phrasing_diff_rate']*100:.1f}%) | "
            f"Phr NLL: {dev_m['phrasing_nll']:.4f} | Eligible: {is_eligible} | {ep_duration:.1f}s"
        )

        history.append({
            "epoch": epoch,
            "train_loss": avg_loss,
            "dev_metrics": dev_m,
            "is_eligible": is_eligible,
            "epoch_seconds": ep_duration,
        })

        # Checkpoint selection:
        # Criteria 3: Among eligible, max phrasing dev diff-target pair both
        # Criteria 4: Tie-break: lowest phrasing dev NLL
        diff_both = dev_m["phrasing_diff_both"]
        phr_nll = dev_m["phrasing_nll"]

        if is_eligible:
            is_better = False
            if diff_both > best_diff_both:
                is_better = True
            elif diff_both == best_diff_both and phr_nll < best_phr_nll:
                is_better = True

            if is_better:
                best_diff_both = diff_both
                best_phr_nll = phr_nll
                best_epoch = epoch
                logger.info(
                    f"--> New best eligible checkpoint at Epoch {epoch}! "
                    f"(Diff Both: {diff_both}/{dev_m['phrasing_diff_pairs']}, NLL: {phr_nll:.4f}) "
                    f"Saving to {best_checkpoint_dir}..."
                )
                trainer.model.save_pretrained(best_checkpoint_dir)
                trainer.tokenizer.save_pretrained(best_checkpoint_dir)

    total_time = time.time() - t0_train
    logger.info(
        f"Training finished in {total_time/60:.2f} minutes. "
        f"Best Epoch: {best_epoch} (Diff Both: {best_diff_both}/20, Phr NLL: {best_phr_nll:.4f})"
    )

    summary = {
        "epochs": epochs,
        "best_epoch": best_epoch,
        "best_diff_both": best_diff_both,
        "best_phr_nll": best_phr_nll,
        "total_seconds": total_time,
        "history": history,
    }
    with open(OUT_DIR / "training_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
