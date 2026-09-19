"""Milestone 6 Experiment 1: Operator Generalization Training Script (ERABI).

Roadmap Reference:
Milestone 6 Operator Generalization (Section 7).
Budget: Experiment 1 of 3 for Milestone 6.

Pre-registered Hypothesis:
Fine-tuning from the base architecture using a 1:1 Task-Balanced Micro-Batch schedule:
- Stream A (Core Logic & Retention): 712 records (600 M3 + 112 Replay)
- Stream B (Multitask Operators & Priority): 780 records (240 M4.1 + 240 M4.3.1 + 300 M6 Operator Train)
guarantees that gradient steps simultaneously enforce core invariant reasoning and operator mechanics
across all 10 logical operators (AND, OR, >=/>, <=/<, override, default+exception, first-match,
priority ranking, negation, goal switching), enabling fresh_operator_eval to reach >= 85% accuracy
and >= 70% contrast pair both, while preserving Core retention (eval_v2 >= 96.0%, eval_exception >= 98.0%).

Outputs:
- runs/m6_e1_operator/checkpoints/
- runs/m6_e1_operator/evaluation_report.json
- runs/m6_e1_operator/notes.md
"""

from __future__ import annotations

import json
import logging
import math
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
from erabi.inference import GLiClassEngine
from erabi.schema import ChoiceRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.m6_e1_operator")

OUT_DIR = ROOT / "runs/m6_e1_operator"
CKPT_DIR = OUT_DIR / "checkpoints"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CKPT_DIR.mkdir(parents=True, exist_ok=True)

M3_TRAIN_FILE = ROOT / "data/m3_3_v2/train.jsonl"
M4_1_TRAIN_FILE = ROOT / "data/m4_1_exception/train_exception.jsonl"
M4_3_1_TRAIN_FILE = ROOT / "data/m4_3_1_phrasing_fix/phrasing_train.jsonl"
M6_TRAIN_FILE = ROOT / "data/m6_operator/train_operator.jsonl"
AUDIT_FILE = ROOT / "runs/m4_4_1_retention/retention_source_audit.json"

DEV_M3_FILE = ROOT / "data/m4_3_1_phrasing_fix/combined_dev.jsonl"
DEV_OP_FILE = ROOT / "data/m6_operator/dev_operator.jsonl"

BENCHMARKS = {
    "fresh_operator_eval": ROOT / "data/m6_operator/fresh_operator_eval.jsonl",
    "dev_operator": ROOT / "data/m6_operator/dev_operator.jsonl",
    "eval_v2": ROOT / "data/m3_3_v2/eval_v2.jsonl",
    "fresh_phrasing_eval": ROOT / "data/m4_3_1_phrasing_fix/fresh_phrasing_eval.jsonl",
    "eval_exception": ROOT / "data/m4_1_exception/eval_exception.jsonl",
    "transfer_probe": ROOT / "data/m3_1/transfer_probe.jsonl",
    "smoke_cases": ROOT / "examples/smoke_cases.jsonl",
}


def load_data_streams() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    # Stream A: Core Logic & Retention (712 records)
    m3_train = [json.loads(l) for l in open(M3_TRAIN_FILE, encoding="utf-8") if l.strip()]
    audit = json.load(open(AUDIT_FILE, encoding="utf-8"))
    r1_gids = set(audit["r1_equality_boundary"]["group_ids"])
    r1b_gids = set(audit["r1b_equality_comparison"]["group_ids"])
    r2_gids = set()
    for st_info in audit["r2_composite_logic"]["states"].values():
        r2_gids.update(st_info["selected_group_ids"])
    replay_gids = r1_gids | r1b_gids | r2_gids
    replay_records = [r for r in m3_train if r["group_id"] in replay_gids]
    stream_a = m3_train + replay_records
    assert len(stream_a) == 712, f"Expected 712 in Stream A, got {len(stream_a)}"

    # Stream B: Multitask Priority & Operators (240 + 240 + 300 = 780 records)
    m4_1_train = [json.loads(l) for l in open(M4_1_TRAIN_FILE, encoding="utf-8") if l.strip()]
    m4_3_1_train = [json.loads(l) for l in open(M4_3_1_TRAIN_FILE, encoding="utf-8") if l.strip()]
    m6_op_train = [json.loads(l) for l in open(M6_TRAIN_FILE, encoding="utf-8") if l.strip()]
    stream_b = m4_1_train + m4_3_1_train + m6_op_train
    assert len(stream_b) == 780, f"Expected 780 in Stream B, got {len(stream_b)}"

    return stream_a, stream_b


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
            "task_family": row.get("task_family"),
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

    # Per-family breakdown if multiple families
    families = sorted(list({r.get("task_family") for r in results if r.get("task_family")}))
    if len(families) > 1:
        fam_m = {}
        for fam in families:
            fam_rows = [r for r in results if r.get("task_family") == fam]
            f_n = len(fam_rows)
            f_corr = sum(1 for r in fam_rows if r["is_correct"])
            f_acc = f_corr / f_n if f_n > 0 else 0.0
            fam_m[fam] = {
                "count": f_n,
                "correct": f_corr,
                "accuracy": f_acc,
            }
        metrics["per_family"] = fam_m

    return metrics


def check_m6_gate(bench_results: Dict[str, Dict[str, Any]]) -> Tuple[bool, List[str]]:
    passed = True
    reasons = []

    # 1. fresh_operator_eval
    fop = bench_results.get("fresh_operator_eval", {})
    fop_acc = fop.get("accuracy", 0.0)
    fop_pair = fop.get("diff_both_rate", 0.0)
    if fop_acc < 0.85:
        passed = False
        reasons.append(f"fresh operator accuracy {fop_acc*100:.1f}% < 85.0%")
    if fop_pair < 0.70:
        passed = False
        reasons.append(f"fresh operator pair both {fop_pair*100:.1f}% < 70.0%")

    # Per-operator family check
    fam_dict = fop.get("per_family", {})
    for fam, fm in fam_dict.items():
        if fm["accuracy"] < 0.60:
            passed = False
            reasons.append(f"operator family '{fam}' acc {fm['accuracy']*100:.1f}% < 60.0%")
        if fm["accuracy"] == 0.0:
            passed = False
            reasons.append(f"operator family '{fam}' has 0.0% accuracy")

    # 2. Core retention: within -2pt of Milestone 5
    # eval_v2 >= 96.0%
    ev2 = bench_results.get("eval_v2", {})
    ev2_acc = ev2.get("accuracy", 0.0)
    if ev2_acc < 0.96:
        passed = False
        reasons.append(f"eval_v2 retention accuracy {ev2_acc*100:.1f}% < 96.0%")

    # eval_exception >= 98.0%
    exc = bench_results.get("eval_exception", {})
    exc_acc = exc.get("accuracy", 0.0)
    if exc_acc < 0.98:
        passed = False
        reasons.append(f"eval_exception retention accuracy {exc_acc*100:.1f}% < 98.0%")

    # fresh_phrasing >= 79.7%
    fr = bench_results.get("fresh_phrasing_eval", {})
    fr_acc = fr.get("accuracy", 0.0)
    if fr_acc < 0.797:
        passed = False
        reasons.append(f"fresh phrasing retention accuracy {fr_acc*100:.1f}% < 79.7%")

    # smoke_cases >= 10/12
    smk = bench_results.get("smoke_cases", {})
    smk_corr = smk.get("correct_count", 0)
    if smk_corr < 10:
        passed = False
        reasons.append(f"smoke cases {smk_corr}/12 < 10/12")

    return passed, reasons


def main():
    set_seed(42)
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    logger.info("=== ERABI Milestone 6 Experiment 1: Operator Generalization ===")
    logger.info(f"Using device: {device}")

    stream_a, stream_b = load_data_streams()
    logger.info(f"Stream A (Core Logic & Retention): {len(stream_a)} records")
    logger.info(f"Stream B (Operators & Priority):    {len(stream_b)} records")

    dev_records = [json.loads(l) for l in open(DEV_M3_FILE, encoding="utf-8") if l.strip()]
    dev_op_records = [json.loads(l) for l in open(DEV_OP_FILE, encoding="utf-8") if l.strip()]
    all_dev = dev_records + dev_op_records
    logger.info(f"Loaded {len(all_dev)} combined dev records ({len(dev_records)} M3/M4 + {len(dev_op_records)} M6 Op).")

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
    SAVE_EPOCHS = [5, 6, 7, 8, 9, 10]
    saved_paths: Dict[int, Path] = {}

    t0_train = time.time()

    for epoch in range(1, epochs + 1):
        t0_ep = time.time()
        trainer.model.train()

        rng = random.Random(42 + epoch)

        shuffled_a = list(stream_a)
        shuffled_b = list(stream_b)
        rng.shuffle(shuffled_a)
        rng.shuffle(shuffled_b)

        # Build 1-to-1 micro-batches: 1 from Stream A, 1 from Stream B
        # Use max length of the two streams (780)
        n_max = max(len(shuffled_a), len(shuffled_b))  # 780
        micro_batches = []
        for i in range(n_max):
            rec_a = shuffled_a[i % len(shuffled_a)]
            rec_b = shuffled_b[i % len(shuffled_b)]
            if rng.random() < 0.5:
                pair = [rec_a, rec_b]
            else:
                pair = [rec_b, rec_a]
            micro_batches.append(pair)

        rng.shuffle(micro_batches)

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
        avg_loss = total_loss / (len(micro_batches) * 2)

        logger.info(f"Epoch {epoch:2d}/{epochs} | Loss: {avg_loss:.4f} | Duration: {ep_duration:.1f}s")

        if epoch in SAVE_EPOCHS:
            ep_dir = CKPT_DIR / f"epoch_{epoch}"
            ep_dir.mkdir(parents=True, exist_ok=True)
            trainer.model.save_pretrained(ep_dir)
            trainer.tokenizer.save_pretrained(ep_dir)
            saved_paths[epoch] = ep_dir
            logger.info(f"--> Saved checkpoint for Epoch {epoch} to {ep_dir}")

    train_time = time.time() - t0_train
    logger.info(f"Training finished in {train_time/60:.2f} minutes.")

    del trainer
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # Evaluation Phase across all saved epochs
    logger.info("\n=== Evaluating Saved Checkpoints on Full Milestone 6 Suite ===")
    eval_results = {}
    best_m6_epoch = None
    best_m6_passed = False

    for ep in SAVE_EPOCHS:
        ckpt_path = saved_paths[ep]
        logger.info(f"\nEvaluating Epoch {ep} ({ckpt_path})...")
        engine = GLiClassEngine(model_id=str(ckpt_path), device=device)

        ep_metrics = {}
        for bname, bpath in BENCHMARKS.items():
            met = evaluate_dataset_with_engine(engine, bpath)
            ep_metrics[bname] = met
            acc_str = f"Acc: {met['accuracy']*100:.1f}%"
            diff_str = f"Diff Both: {met.get('diff_both', 0)}/{met.get('diff_pairs', 0)} ({met.get('diff_both_rate', 0)*100:.1f}%)" if "diff_both" in met else ""
            logger.info(f"  {bname:20s} | {acc_str:15s} | {diff_str}")

        del engine
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        is_m6_pass, gate_reasons = check_m6_gate(ep_metrics)
        logger.info(f"Epoch {ep} M6 Gate Pass: {is_m6_pass} | Reasons: {gate_reasons if not is_m6_pass else 'ALL PASSED'}")

        eval_results[ep] = {
            "metrics": ep_metrics,
            "is_m6_pass": is_m6_pass,
            "gate_reasons": gate_reasons,
        }

        if is_m6_pass and not best_m6_passed:
            best_m6_passed = True
            best_m6_epoch = ep

    # Save summary report
    report = {
        "experiment_name": "Milestone 6 Experiment 1: Operator Generalization",
        "saved_epochs": SAVE_EPOCHS,
        "best_m6_passed": best_m6_passed,
        "best_m6_epoch": best_m6_epoch,
        "results": eval_results,
    }
    with open(OUT_DIR / "evaluation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Markdown Table
    md_lines = [
        "# Milestone 6 Experiment 1: Operator Generalization Report\n",
        f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
        "## Multi-Epoch Benchmark Results\n",
        "| Epoch | fresh_op Acc | fresh_op Pair Both | eval_v2 Acc | fresh_phr Acc | eval_exc Acc | smoke | M6 Gate |",
        "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]

    for ep in SAVE_EPOCHS:
        m = eval_results[ep]["metrics"]
        fop_acc = f"{m['fresh_operator_eval']['accuracy']*100:.1f}%"
        fop_pb = f"{m['fresh_operator_eval'].get('diff_both', 0)}/{m['fresh_operator_eval'].get('diff_pairs', 0)} ({m['fresh_operator_eval'].get('diff_both_rate', 0)*100:.1f}%)"
        ev2_acc = f"{m['eval_v2']['accuracy']*100:.1f}%"
        fr_acc = f"{m['fresh_phrasing_eval']['accuracy']*100:.1f}%"
        exc_acc = f"{m['eval_exception']['accuracy']*100:.1f}%"
        smk = f"{m['smoke_cases']['correct_count']}/12"
        gate_status = "**PASS**" if eval_results[ep]["is_m6_pass"] else "FAIL"
        md_lines.append(f"| Epoch {ep} | {fop_acc} | {fop_pb} | {ev2_acc} | {fr_acc} | {exc_acc} | {smk} | {gate_status} |")

    md_lines.append(f"\n**M6 Gate Passed**: {best_m6_passed}")
    if best_m6_passed:
        md_lines.append(f"**Selected Passing Epoch**: Epoch {best_m6_epoch}")

    with open(OUT_DIR / "notes.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    logger.info(f"Report saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
