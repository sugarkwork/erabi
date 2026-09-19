"""Milestone 8 Experiment 1: General Choice Tasks Multitask Training Script (ERABI).

Roadmap Reference:
Milestone 8 General Choice Tasks (Section 9).
Budget: Experiment 1 of 3 for Milestone 8.

Pre-registered Hypothesis:
Baseline evaluation of W_robustness_v1 showed strong zero-shot transfer on instruction_separation (100%),
intent_selection (100%), support_routing (80%), and semantic_relation (75%), but failed on
negative_goal (50%) and short_nli (50%) due to positive confirmation bias.
By training with 1:1 Task-Balanced Micro-Batches:
- Stream A: Core Logic & Replay (712 records: 600 M3 + 112 Replay)
- Stream B: Multitask Extensions (1,564 records: 240 M4.1 + 240 M4.3.1 + 400 M6 + 324 M7 + 360 M8)
the model will overcome confirmation bias in negative goals and NLI contradictions, driving:
1. fresh_general_eval overall accuracy >= 82.0%
2. every task family >= 70.0% (no family below 70%)
3. Core and prior capability retention:
   - eval_v2 >= 95.0%
   - eval_exception >= 98.0%
   - fresh_phrasing_eval >= 77.0%
   - fresh_operator_eval >= 90.0%
   - fresh_robustness_eval >= 95.0%
   - smoke_cases >= 10/12

Outputs:
- runs/m8_e1_multitask/checkpoints/
- runs/m8_e1_multitask/evaluation_report.json
- runs/m8_e1_multitask/notes.md
"""

from __future__ import annotations

import json
import logging
import math
import os
import random
import sys
import time
import zipfile
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
logger = logging.getLogger("erabi.m8_e1_multitask")

OUT_DIR = ROOT / "runs/m8_e1_multitask"
CKPT_DIR = OUT_DIR / "checkpoints"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CKPT_DIR.mkdir(parents=True, exist_ok=True)

# Training files
M3_TRAIN_FILE = ROOT / "data/m3_3_v2/train.jsonl"
M4_1_TRAIN_FILE = ROOT / "data/m4_1_exception/train_exception.jsonl"
M4_3_1_TRAIN_FILE = ROOT / "data/m4_3_1_phrasing_fix/phrasing_train.jsonl"
M6_TRAIN_FILE = ROOT / "data/m6_operator/train_operator.jsonl"
M7_TRAIN_FILE = ROOT / "data/m7_robustness/train_robustness.jsonl"
M8_TRAIN_FILE = ROOT / "data/m8_general_choice/train_general.jsonl"
AUDIT_FILE = ROOT / "runs/m4_4_1_retention/retention_source_audit.json"

# Benchmarks
BENCHMARKS = {
    "fresh_general_eval": ROOT / "data/m8_general_choice/fresh_general_eval.jsonl",
    "dev_general": ROOT / "data/m8_general_choice/dev_general.jsonl",
    "fresh_robustness_eval": ROOT / "data/m7_robustness/fresh_robustness_eval.jsonl",
    "fresh_operator_eval": ROOT / "data/m6_operator/fresh_operator_eval.jsonl",
    "eval_v2": ROOT / "data/m3_3_v2/eval_v2.jsonl",
    "fresh_phrasing_eval": ROOT / "data/m4_3_1_phrasing_fix/fresh_phrasing_eval.jsonl",
    "eval_exception": ROOT / "data/m4_1_exception/eval_exception.jsonl",
    "smoke_cases": ROOT / "examples/smoke_cases.jsonl",
    "transfer_probe": ROOT / "data/m3_1/transfer_probe.jsonl",
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

    # Stream B: Multitask Extensions (240 + 240 + 400 + 324 + 360 = 1,564 records)
    m4_1_train = [json.loads(l) for l in open(M4_1_TRAIN_FILE, encoding="utf-8") if l.strip()]
    m4_3_1_train = [json.loads(l) for l in open(M4_3_1_TRAIN_FILE, encoding="utf-8") if l.strip()]
    m6_op_train = [json.loads(l) for l in open(M6_TRAIN_FILE, encoding="utf-8") if l.strip()]
    m7_rob_train = [json.loads(l) for l in open(M7_TRAIN_FILE, encoding="utf-8") if l.strip()]
    m8_gen_train = [json.loads(l) for l in open(M8_TRAIN_FILE, encoding="utf-8") if l.strip()]

    stream_b = m4_1_train + m4_3_1_train + m6_op_train + m7_rob_train + m8_gen_train
    assert len(stream_b) == 1564, f"Expected 1564 in Stream B, got {len(stream_b)}"

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

    if total_pairs > 0:
        metrics["total_pairs"] = total_pairs
        metrics["pair_both"] = pair_both
        metrics["pair_both_rate"] = pair_both / total_pairs
        metrics["diff_pairs"] = diff_pairs
        metrics["diff_both"] = diff_both
        metrics["diff_both_rate"] = (diff_both / diff_pairs) if diff_pairs > 0 else 0.0

    families = sorted(list({r.get("task_family") for r in results if r.get("task_family")}))
    if len(families) > 1:
        fam_m = {}
        for fam in families:
            fam_rows = [r for r in results if r.get("task_family") == fam]
            f_corr = sum(1 for r in fam_rows if r["is_correct"])
            fam_m[fam] = {
                "count": len(fam_rows),
                "correct": f_corr,
                "accuracy": f_corr / len(fam_rows),
            }
        metrics["per_family"] = fam_m

    return metrics


def check_m8_gate(bench_results: Dict[str, Dict[str, Any]]) -> Tuple[bool, List[str]]:
    passed = True
    reasons = []

    # 1. fresh_general_eval
    fgen = bench_results.get("fresh_general_eval", {})
    fgen_acc = fgen.get("accuracy", 0.0)

    if fgen_acc < 0.82:
        passed = False
        reasons.append(f"fresh general accuracy {fgen_acc*100:.1f}% < 82.0%")

    fam_dict = fgen.get("per_family", {})
    for fam, fm in fam_dict.items():
        if fm["accuracy"] < 0.70:
            passed = False
            reasons.append(f"general family '{fam}' acc {fm['accuracy']*100:.1f}% < 70.0%")
        if fm["accuracy"] == 0.0:
            passed = False
            reasons.append(f"general family '{fam}' has 0.0% accuracy")

    # 2. Robustness retention: fresh_robustness_eval >= 95.0%
    frob = bench_results.get("fresh_robustness_eval", {})
    frob_acc = frob.get("accuracy", 0.0)
    if frob_acc < 0.95:
        passed = False
        reasons.append(f"fresh robustness retention accuracy {frob_acc*100:.1f}% < 95.0%")

    # 3. Operator retention: fresh_operator_eval >= 90.0%
    fop = bench_results.get("fresh_operator_eval", {})
    fop_acc = fop.get("accuracy", 0.0)
    if fop_acc < 0.90:
        passed = False
        reasons.append(f"fresh operator retention accuracy {fop_acc*100:.1f}% < 90.0%")

    # 4. Core retention: within -2pt
    ev2 = bench_results.get("eval_v2", {})
    ev2_acc = ev2.get("accuracy", 0.0)
    if ev2_acc < 0.95:
        passed = False
        reasons.append(f"eval_v2 retention accuracy {ev2_acc*100:.1f}% < 95.0%")

    exc = bench_results.get("eval_exception", {})
    exc_acc = exc.get("accuracy", 0.0)
    if exc_acc < 0.98:
        passed = False
        reasons.append(f"eval_exception retention accuracy {exc_acc*100:.1f}% < 98.0%")

    fr = bench_results.get("fresh_phrasing_eval", {})
    fr_acc = fr.get("accuracy", 0.0)
    if fr_acc < 0.770:
        passed = False
        reasons.append(f"fresh phrasing retention accuracy {fr_acc*100:.1f}% < 77.0%")

    smk = bench_results.get("smoke_cases", {})
    smk_corr = smk.get("correct_count", 0)
    if smk_corr < 10:
        passed = False
        reasons.append(f"smoke cases {smk_corr}/12 < 10/12")

    return passed, reasons


def main():
    set_seed(42)
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    logger.info("=== ERABI Milestone 8 Experiment 1: General Choice Tasks Training ===")
    logger.info(f"Using device: {device}")

    stream_a, stream_b = load_data_streams()
    logger.info(f"Stream A (Core Logic & Retention): {len(stream_a)} records")
    logger.info(f"Stream B (Multitask Extensions):   {len(stream_b)} records")

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

        n_max = max(len(shuffled_a), len(shuffled_b))  # 1,564
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

    logger.info("\n=== Evaluating Saved Checkpoints on Full Milestone 8 Suite ===")
    eval_results = {}
    best_m8_epoch = None
    best_m8_passed = False
    best_score = -1.0

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
            logger.info(f"  {bname:22s} | {acc_str:14s} | {diff_str}")

        del engine
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        is_m8_pass, gate_reasons = check_m8_gate(ep_metrics)
        logger.info(f"Epoch {ep} M8 Gate Pass: {is_m8_pass} | Reasons: {gate_reasons if not is_m8_pass else 'ALL PASSED'}")

        # Composite score: fgen_acc + frob_acc + fop_acc + ev2_acc
        fgen_acc = ep_metrics["fresh_general_eval"]["accuracy"]
        frob_acc = ep_metrics["fresh_robustness_eval"]["accuracy"]
        fop_acc = ep_metrics["fresh_operator_eval"]["accuracy"]
        ev2_acc = ep_metrics["eval_v2"]["accuracy"]
        score = fgen_acc + frob_acc + fop_acc + ev2_acc

        eval_results[ep] = {
            "is_m8_pass": is_m8_pass,
            "gate_reasons": gate_reasons,
            "score": score,
            "metrics": ep_metrics,
        }

        if is_m8_pass and score > best_score:
            best_score = score
            best_m8_epoch = ep
            best_m8_passed = True

    # Save evaluation report
    report_path = OUT_DIR / "evaluation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2, ensure_ascii=False)
    logger.info(f"\nSaved evaluation report to {report_path}")

    # Process outcome
    if best_m8_passed and best_m8_epoch is not None:
        logger.info(f"\n=======================================================")
        logger.info(f"MILESTONE 8 GATE PASSED at Epoch {best_m8_epoch}! (Score: {best_score:.4f})")
        logger.info(f"=======================================================")

        best_ckpt = saved_paths[best_m8_epoch]
        target_dir = ROOT / "runs/m8_general/checkpoint"
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        if target_dir.exists():
            import shutil
            shutil.rmtree(target_dir)

        import shutil
        shutil.copytree(best_ckpt, target_dir)
        logger.info(f"Successfully frozen best checkpoint to {target_dir} as W_general_v1")

        # Manifest
        manifest = {
            "milestone": "Milestone 8 General Choice Tasks",
            "model_version": "W_general_v1",
            "best_epoch": best_m8_epoch,
            "evaluation_report": eval_results[best_m8_epoch],
            "benchmark_summary": {
                "fresh_general_eval_accuracy": eval_results[best_m8_epoch]["metrics"]["fresh_general_eval"]["accuracy"],
                "fresh_general_per_family": eval_results[best_m8_epoch]["metrics"]["fresh_general_eval"]["per_family"],
                "fresh_robustness_eval_accuracy": eval_results[best_m8_epoch]["metrics"]["fresh_robustness_eval"]["accuracy"],
                "fresh_operator_eval_accuracy": eval_results[best_m8_epoch]["metrics"]["fresh_operator_eval"]["accuracy"],
                "eval_v2_accuracy": eval_results[best_m8_epoch]["metrics"]["eval_v2"]["accuracy"],
                "eval_exception_accuracy": eval_results[best_m8_epoch]["metrics"]["eval_exception"]["accuracy"],
                "fresh_phrasing_eval_accuracy": eval_results[best_m8_epoch]["metrics"]["fresh_phrasing_eval"]["accuracy"],
                "smoke_cases_correct": eval_results[best_m8_epoch]["metrics"]["smoke_cases"]["correct_count"],
            },
            "frozen_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        manifest_path = ROOT / "runs/m8_general/manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        # Create review bundle zip
        bundle_path = ROOT / "runs/m8_general/review_bundle.zip"
        with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(manifest_path, arcname="manifest.json")
            zf.write(report_path, arcname="evaluation_report.json")
            zf.write(ROOT / "data/m8_general_choice/fresh_general_eval.jsonl", arcname="fresh_general_eval.jsonl")
            zf.write(ROOT / "runs/m8_baseline_diagnostic/baseline_report.json", arcname="baseline_report.json")
            zf.write(ROOT / "runs/m8_baseline_diagnostic/notes.md", arcname="baseline_notes.md")

        import hashlib
        h = hashlib.sha256(open(bundle_path, "rb").read()).hexdigest()
        logger.info(f"Created review_bundle.zip ({bundle_path.stat().st_size} bytes, SHA256: {h})")

    else:
        logger.error("No checkpoint passed the Milestone 8 Gate in Experiment 1.")


if __name__ == "__main__":
    main()
