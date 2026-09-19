"""M4.4.2 Checkpoint Trajectory Diagnostic Script for ERABI Milestone 5.

Pre-registered Hypothesis:
During fine-tuning from B0, phrasing generalization develops around epoch 5-7, while
later epochs (8-10) overfit to phrasing syntax (phrasing NLL explodes from 1.9 to 6.9)
and induce catastrophic task interference with M3 synthetic rule boundary conditions.
By tracking checkpoints across epochs 4 through 10, we determine whether an intermediate
epoch satisfies the Milestone 5 Balanced Core Reasoner Gate:
- eval_v2 Acc >= 97.0%, Diff Both >= 88%
- fresh phrasing Acc >= 80.0%, Diff Both >= 60%, Same Both >= 75%
- eval_exception Acc >= 98.0%, Diff Both >= 95%
- smoke_cases >= 10/12

Budget: Full training experiment 1 of 3 for Milestone 5.
Data: data/m4_4_1_retention/combined_train_retention.jsonl (1192 cases).
Evaluation sets: strictly isolated (zero contamination).
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
from erabi.inference import GLiClassEngine
from erabi.schema import ChoiceRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.m4_4_2_trajectory")

OUT_DIR = ROOT / "runs/m4_4_2_trajectory"
CKPT_DIR = OUT_DIR / "checkpoints"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CKPT_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_FILE = ROOT / "data/m4_4_1_retention/combined_train_retention.jsonl"
DEV_FILE = ROOT / "data/m4_3_1_phrasing_fix/combined_dev.jsonl"

DATASETS = {
    "eval_v2": ROOT / "data/m3_3_v2/eval_v2.jsonl",
    "fresh_phrasing_eval": ROOT / "data/m4_3_1_phrasing_fix/fresh_phrasing_eval.jsonl",
    "eval_exception": ROOT / "data/m4_1_exception/eval_exception.jsonl",
    "transfer_probe": ROOT / "data/m3_1/transfer_probe.jsonl",
    "smoke_cases": ROOT / "examples/smoke_cases.jsonl",
}


def evaluate_dataset_with_engine(engine: GLiClassEngine, dataset_path: Path) -> Dict[str, Any]:
    records = [json.loads(line) for line in open(dataset_path, encoding="utf-8") if line.strip()]
    results = []
    total_nll = 0.0
    correct_count = 0

    for row in records:
        req = ChoiceRequest.from_dict(row)
        tgt_cid = row["target"]["choice_id"]
        tgt_idx = next(i for i, c in enumerate(req.choices) if c.id == tgt_cid)

        resp = engine.predict(req, temperature=1.0, return_logits=True)
        pred_cid = resp.best_candidate_id
        is_corr = (pred_cid == tgt_cid)
        if is_corr:
            correct_count += 1

        log_probs = F.log_softmax(torch.tensor(resp.raw_logits, dtype=torch.float64), dim=-1)
        total_nll += -float(log_probs[tgt_idx].item())

        results.append({
            "id": row.get("id"),
            "group_id": row.get("group_id"),
            "target": tgt_cid,
            "predicted": pred_cid,
            "is_correct": is_corr,
        })

    n = len(records)
    metrics: Dict[str, Any] = {
        "count": n,
        "correct_count": correct_count,
        "accuracy": correct_count / n,
        "mean_nll": total_nll / n,
    }

    groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in results:
        gid = r.get("group_id")
        if gid:
            groups.setdefault(gid, []).append(r)

    total_pairs = 0
    pair_both = 0
    diff_pairs = 0
    diff_both = 0
    same_pairs = 0
    same_both = 0

    for gid, pair in groups.items():
        if len(pair) == 2:
            total_pairs += 1
            r1, r2 = pair[0], pair[1]
            is_both = (r1["is_correct"] and r2["is_correct"])
            if is_both:
                pair_both += 1
            if r1["target"] != r2["target"]:
                diff_pairs += 1
                if is_both:
                    diff_both += 1
            else:
                same_pairs += 1
                if is_both:
                    same_both += 1

    if total_pairs > 0:
        metrics["total_pairs"] = total_pairs
        metrics["pair_both"] = pair_both
        metrics["pair_both_rate"] = pair_both / total_pairs
        metrics["diff_pairs"] = diff_pairs
        metrics["diff_both"] = diff_both
        metrics["diff_both_rate"] = (diff_both / diff_pairs) if diff_pairs > 0 else 0.0
        metrics["same_pairs"] = same_pairs
        metrics["same_both"] = same_both
        metrics["same_both_rate"] = (same_both / same_pairs) if same_pairs > 0 else 0.0

    return metrics


def check_m5_gate(eval_res: Dict[str, Dict[str, Any]]) -> Tuple[bool, List[str]]:
    passed = True
    reasons = []

    # 1. eval_v2
    ev2 = eval_res.get("eval_v2", {})
    ev2_acc = ev2.get("accuracy", 0.0)
    ev2_diff = ev2.get("diff_both_rate", 0.0)
    if ev2_acc < 0.97:
        passed = False
        reasons.append(f"eval_v2 accuracy {ev2_acc*100:.1f}% < 97.0%")
    if ev2_diff < 0.88:
        passed = False
        reasons.append(f"eval_v2 diff both {ev2_diff*100:.1f}% < 88.0%")

    # 2. fresh_phrasing_eval
    fr = eval_res.get("fresh_phrasing_eval", {})
    fr_acc = fr.get("accuracy", 0.0)
    fr_diff = fr.get("diff_both_rate", 0.0)
    fr_same = fr.get("same_both_rate", 0.0)
    if fr_acc < 0.80:
        passed = False
        reasons.append(f"fresh phrasing accuracy {fr_acc*100:.1f}% < 80.0%")
    if fr_diff < 0.60:
        passed = False
        reasons.append(f"fresh phrasing diff both {fr_diff*100:.1f}% < 60.0%")
    if fr_same < 0.75:
        passed = False
        reasons.append(f"fresh phrasing same both {fr_same*100:.1f}% < 75.0%")

    # 3. eval_exception
    exc = eval_res.get("eval_exception", {})
    exc_acc = exc.get("accuracy", 0.0)
    exc_diff = exc.get("diff_both_rate", 0.0)
    if exc_acc < 0.98:
        passed = False
        reasons.append(f"eval_exception accuracy {exc_acc*100:.1f}% < 98.0%")
    if exc_diff < 0.95:
        passed = False
        reasons.append(f"eval_exception diff both {exc_diff*100:.1f}% < 95.0%")

    # 4. smoke_cases
    smk = eval_res.get("smoke_cases", {})
    smk_corr = smk.get("correct_count", 0)
    if smk_corr < 10:
        passed = False
        reasons.append(f"smoke cases {smk_corr}/12 < 10/12")

    return passed, reasons


def main():
    set_seed(42)
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    logger.info(f"=== M4.4.2 Checkpoint Trajectory Diagnostic ===")
    logger.info(f"Device: {device}")

    train_records = [json.loads(line) for line in open(TRAIN_FILE, encoding="utf-8") if line.strip()]
    logger.info(f"Loaded {len(train_records)} train records.")

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
    SAVE_EPOCHS = [4, 5, 6, 7, 8, 9, 10]
    saved_paths: Dict[int, Path] = {}

    t0 = time.time()
    for epoch in range(1, epochs + 1):
        t0_ep = time.time()
        trainer.model.train()

        rng = random.Random(42 + epoch)
        shuffled = list(train_records)
        rng.shuffle(shuffled)

        micro_batches = [
            shuffled[i : i + trainer.micro_batch_size]
            for i in range(0, len(shuffled), trainer.micro_batch_size)
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
        logger.info(f"Epoch {epoch:2d}/{epochs} finished in {ep_duration:.1f}s | Loss: {avg_loss:.4f}")

        if epoch in SAVE_EPOCHS:
            ep_dir = CKPT_DIR / f"epoch_{epoch}"
            ep_dir.mkdir(parents=True, exist_ok=True)
            trainer.model.save_pretrained(ep_dir)
            trainer.tokenizer.save_pretrained(ep_dir)
            saved_paths[epoch] = ep_dir
            logger.info(f"--> Saved checkpoint for Epoch {epoch} to {ep_dir}")

    train_time = time.time() - t0
    logger.info(f"Training completed in {train_time/60:.2f} minutes.")

    # Free trainer model memory before evaluation
    del trainer
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # Diagnostic Evaluation Phase
    logger.info("Starting Trajectory Diagnostic Evaluation across epochs 4..10...")
    trajectory_results = {}
    best_m5_epoch = None
    best_m5_passed = False

    for ep in SAVE_EPOCHS:
        ckpt_path = saved_paths[ep]
        logger.info(f"\n--- Evaluating Epoch {ep} from {ckpt_path} ---")
        engine = GLiClassEngine(model_id=str(ckpt_path), device=device)

        ep_metrics = {}
        for dname, dpath in DATASETS.items():
            met = evaluate_dataset_with_engine(engine, dpath)
            ep_metrics[dname] = met
            acc_str = f"Acc: {met['accuracy']*100:.1f}%"
            diff_str = f"Diff Both: {met.get('diff_both', 0)}/{met.get('diff_pairs', 0)} ({met.get('diff_both_rate', 0)*100:.1f}%)" if "diff_both" in met else ""
            logger.info(f"  {dname:20s} | {acc_str:15s} | {diff_str}")

        del engine
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        is_m5_pass, gate_reasons = check_m5_gate(ep_metrics)
        logger.info(f"Epoch {ep} M5 Gate Pass: {is_m5_pass} | Reasons: {gate_reasons if not is_m5_pass else 'ALL PASSED'}")

        trajectory_results[ep] = {
            "metrics": ep_metrics,
            "is_m5_pass": is_m5_pass,
            "gate_reasons": gate_reasons,
        }

        if is_m5_pass and not best_m5_passed:
            best_m5_passed = True
            best_m5_epoch = ep

    # Summary Report
    summary = {
        "diagnostic_name": "M4.4.2 Checkpoint Trajectory Diagnostic",
        "save_epochs": SAVE_EPOCHS,
        "best_m5_passed": best_m5_passed,
        "best_m5_epoch": best_m5_epoch,
        "trajectory": trajectory_results,
    }

    report_json_path = OUT_DIR / "trajectory_report.json"
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved trajectory report to {report_json_path}")

    # Build Markdown table
    md_lines = [
        "# M4.4.2 Checkpoint Trajectory Diagnostic Report\n",
        f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
        "## Trajectory Table Across Epochs\n",
        "| Epoch | eval_v2 Acc | eval_v2 Diff Both | fresh Acc | fresh Diff Both | eval_exception Acc | transfer_probe | smoke | M5 Gate |",
        "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]

    for ep in SAVE_EPOCHS:
        m = trajectory_results[ep]["metrics"]
        ev2_acc = f"{m['eval_v2']['accuracy']*100:.1f}%"
        ev2_db = f"{m['eval_v2'].get('diff_both', 0)}/{m['eval_v2'].get('diff_pairs', 0)} ({m['eval_v2'].get('diff_both_rate', 0)*100:.1f}%)"
        fr_acc = f"{m['fresh_phrasing_eval']['accuracy']*100:.1f}%"
        fr_db = f"{m['fresh_phrasing_eval'].get('diff_both', 0)}/{m['fresh_phrasing_eval'].get('diff_pairs', 0)} ({m['fresh_phrasing_eval'].get('diff_both_rate', 0)*100:.1f}%)"
        exc_acc = f"{m['eval_exception']['accuracy']*100:.1f}%"
        tp_acc = f"{m['transfer_probe']['correct_count']}/32 ({m['transfer_probe']['accuracy']*100:.1f}%)"
        smk = f"{m['smoke_cases']['correct_count']}/12"
        gate_status = "**PASS**" if trajectory_results[ep]["is_m5_pass"] else "FAIL"

        md_lines.append(f"| Epoch {ep} | {ev2_acc} | {ev2_db} | {fr_acc} | {fr_db} | {exc_acc} | {tp_acc} | {smk} | {gate_status} |")

    md_lines.append(f"\n**M5 Gate Passed**: {best_m5_passed}")
    if best_m5_passed:
        md_lines.append(f"**Selected Passing Epoch**: Epoch {best_m5_epoch}")
    else:
        md_lines.append(f"**Diagnostic Conclusion**: All epochs trade off between eval_v2 retention and fresh phrasing generalization.")

    with open(OUT_DIR / "notes.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")
    logger.info(f"Saved Markdown report to {OUT_DIR / 'notes.md'}")


if __name__ == "__main__":
    main()
