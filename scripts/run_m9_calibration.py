"""Milestone 9 Calibration Script (ERABI).

Roadmap Reference:
Milestone 9 Calibration (Section 10).

Procedure:
1. Load frozen model W_general_v1 (runs/m8_general/checkpoint).
2. Extract logits and optimize temperature T on data/m9_calibration/calibration.jsonl.
3. Validate T* does not stick to boundary and improves calibration NLL.
4. Evaluate fresh_calibration_eval.jsonl at T=1.0 vs T=T*:
   - Top-1 accuracy invariance
   - Fresh NLL improvement
   - Brier score non-worsening
   - High-confidence (p >= 0.90) error rate <= 5%
5. Build verified calibration artifact and review bundle.

Outputs:
- runs/m9_calibration/calibration.json
- runs/m9_calibration/calibration_report.json
- runs/m9_calibration/notes.md
- runs/m9_calibration/review_bundle.zip
"""

from __future__ import annotations

import datetime
import json
import logging
import math
import os
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

from erabi.calibrate import (
    build_calibration_artifact,
    extract_logits_and_targets,
    optimize_temperature,
)
from erabi.inference import GLiClassEngine
from erabi.schema import ChoiceRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.m9_calibration")

OUT_DIR = ROOT / "runs/m9_calibration"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_DIR = ROOT / "runs/m8_general/checkpoint"
CALIB_FILE = ROOT / "data/m9_calibration/calibration.jsonl"
FRESH_CALIB_FILE = ROOT / "data/m9_calibration/fresh_calibration_eval.jsonl"


def evaluate_with_temperature(
    engine: GLiClassEngine,
    dataset_path: Path,
    temperature: float,
) -> Dict[str, Any]:
    records = [json.loads(l) for l in open(dataset_path, encoding="utf-8") if l.strip()]
    results = []
    total_nll = 0.0
    total_brier = 0.0
    correct_count = 0

    high_conf_total = 0
    high_conf_errors = 0

    for r in records:
        req = ChoiceRequest.from_dict(r)
        tgt_cid = r["target"]["choice_id"]
        tgt_idx = next(i for i, c in enumerate(req.choices) if c.id == tgt_cid)

        resp = engine.predict(req, temperature=temperature, return_logits=True)
        raw_logits = resp.raw_logits
        pred_cid = resp.best_candidate_id
        is_corr = (pred_cid == tgt_cid)
        if is_corr:
            correct_count += 1

        probs = {c.id: c.probability for c in resp.choices}
        max_p = max(probs.values())
        if max_p >= 0.90:
            high_conf_total += 1
            if not is_corr:
                high_conf_errors += 1

        t_logits = torch.tensor(raw_logits, dtype=torch.float64) / temperature
        log_probs = F.log_softmax(t_logits, dim=-1).tolist()
        t_probs = F.softmax(t_logits, dim=-1).tolist()

        nll = -log_probs[tgt_idx]
        total_nll += nll

        one_hot = [1.0 if i == tgt_idx else 0.0 for i in range(len(req.choices))]
        brier = sum((p - y) ** 2 for p, y in zip(t_probs, one_hot))
        total_brier += brier

        results.append({
            "id": r["id"],
            "target": tgt_cid,
            "predicted": pred_cid,
            "is_correct": is_corr,
            "probs": probs,
            "nll": nll,
            "brier": brier,
        })

    n = len(records)
    high_conf_error_rate = (high_conf_errors / high_conf_total) if high_conf_total > 0 else 0.0

    return {
        "count": n,
        "temperature": temperature,
        "correct_count": correct_count,
        "accuracy": correct_count / n,
        "mean_nll": total_nll / n,
        "mean_brier": total_brier / n,
        "high_conf_total": high_conf_total,
        "high_conf_errors": high_conf_errors,
        "high_conf_error_rate": high_conf_error_rate,
        "details": results,
    }


def main():
    logger.info("=== Milestone 9 Calibration Run ===")
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    logger.info(f"Loading frozen W_general_v1 from {MODEL_DIR} on {device}")

    # 1. Load calibration records
    calib_records = [json.loads(l) for l in open(CALIB_FILE, encoding="utf-8") if l.strip()]
    logger.info(f"Loaded {len(calib_records)} calibration records from {CALIB_FILE}")

    # 2. Extract logits & optimize temperature
    logits_list, target_indices, _ = extract_logits_and_targets(
        str(MODEL_DIR), calib_records, device=device
    )
    opt_res = optimize_temperature(logits_list, target_indices, bounds=(0.1, 10.0))

    optimal_T = opt_res["optimal_T"]
    logger.info(f"Optimization results on calibration set:")
    logger.info(f"  T=1.0 NLL:    {opt_res['initial_nll']:.6f}")
    logger.info(f"  Optimal T*:   {optimal_T:.4f}")
    logger.info(f"  T* NLL:       {opt_res['optimal_nll']:.6f}")
    logger.info(f"  NLL Imprv:    {opt_res['improvement']:.6f}")
    logger.info(f"  At boundary:  {opt_res['is_at_boundary']}")

    # 3. Evaluate on held-out fresh_calibration_eval.jsonl at T=1.0 and T=T*
    logger.info("\n=== Evaluating on Fresh Calibration Eval Set ===")
    engine = GLiClassEngine(model_id=str(MODEL_DIR), device=device)

    eval_t1 = evaluate_with_temperature(engine, FRESH_CALIB_FILE, temperature=1.0)
    eval_topt = evaluate_with_temperature(engine, FRESH_CALIB_FILE, temperature=optimal_T)

    logger.info(f"T=1.0   -> Acc: {eval_t1['accuracy']*100:.1f}%, NLL: {eval_t1['mean_nll']:.6f}, Brier: {eval_t1['mean_brier']:.6f}, HighConf Err: {eval_t1['high_conf_error_rate']*100:.1f}% ({eval_t1['high_conf_errors']}/{eval_t1['high_conf_total']})")
    logger.info(f"T={optimal_T:.4f} -> Acc: {eval_topt['accuracy']*100:.1f}%, NLL: {eval_topt['mean_nll']:.6f}, Brier: {eval_topt['mean_brier']:.6f}, HighConf Err: {eval_topt['high_conf_error_rate']*100:.1f}% ({eval_topt['high_conf_errors']}/{eval_topt['high_conf_total']})")

    # 4. Check Milestone 9 Gate
    gate_passed = True
    gate_reasons = []

    # Check finite T and boundary
    if not math.isfinite(optimal_T) or optimal_T <= 0.0:
        gate_passed = False
        gate_reasons.append(f"Temperature {optimal_T} is not positive finite.")
    if opt_res["is_at_boundary"]:
        gate_passed = False
        gate_reasons.append(f"Optimal T* stuck at optimizer boundary.")

    # Top-1 accuracy invariant
    if eval_topt["accuracy"] != eval_t1["accuracy"]:
        gate_passed = False
        gate_reasons.append(f"Accuracy changed between T=1.0 and T*: {eval_t1['accuracy']} != {eval_topt['accuracy']}")

    # Fresh NLL improvement or stability
    fresh_nll_imprv = eval_t1["mean_nll"] - eval_topt["mean_nll"]
    logger.info(f"Fresh NLL change: {fresh_nll_imprv:+.6f}")
    if eval_topt["mean_nll"] > eval_t1["mean_nll"] + 1e-4:
        gate_passed = False
        gate_reasons.append(f"Fresh NLL worsened from {eval_t1['mean_nll']} to {eval_topt['mean_nll']}")

    # Brier does not worsen
    if eval_topt["mean_brier"] > eval_t1["mean_brier"] + 1e-4:
        gate_passed = False
        gate_reasons.append(f"Fresh Brier score worsened: {eval_t1['mean_brier']} -> {eval_topt['mean_brier']}")

    # High-confidence error rate <= 5%
    if eval_topt["high_conf_error_rate"] > 0.05:
        gate_passed = False
        gate_reasons.append(f"High confidence (p>=0.90) error rate {eval_topt['high_conf_error_rate']*100:.1f}% > 5.0%")

    logger.info(f"\nMilestone 9 Gate Pass: {gate_passed} | Reasons: {gate_reasons if not gate_passed else 'ALL PASSED'}")

    # 5. Build official calibration artifact
    decision = "ACCEPT_SCOPED" if gate_passed else "REJECTED"
    status = "applied" if gate_passed else "none"
    reason = f"Gate passed with Fresh NLL {eval_topt['mean_nll']:.6f} and Brier {eval_topt['mean_brier']:.6f}" if gate_passed else "; ".join(gate_reasons)

    calib_artifact = build_calibration_artifact(
        temperature=optimal_T,
        status=status,
        checkpoint_dir=str(MODEL_DIR),
        dataset_path=str(CALIB_FILE),
        dataset_cases=len(calib_records),
        dataset_description="ERABI Milestone 9 Multitask Calibration Set",
        optimization_info=opt_res,
        adoption_decision=decision,
        adoption_reason=reason,
        scope="multitask_general_choice_engine",
    )

    # Attach fresh eval metrics to artifact
    calib_artifact["fresh_eval"] = {
        "dataset_path": str(FRESH_CALIB_FILE),
        "t1_metrics": {
            "accuracy": eval_t1["accuracy"],
            "mean_nll": eval_t1["mean_nll"],
            "mean_brier": eval_t1["mean_brier"],
            "high_conf_error_rate": eval_t1["high_conf_error_rate"],
        },
        "topt_metrics": {
            "accuracy": eval_topt["accuracy"],
            "mean_nll": eval_topt["mean_nll"],
            "mean_brier": eval_topt["mean_brier"],
            "high_conf_error_rate": eval_topt["high_conf_error_rate"],
        },
        "fresh_nll_improvement": fresh_nll_imprv,
        "gate_passed": gate_passed,
    }

    calib_path = OUT_DIR / "calibration.json"
    with open(calib_path, "w", encoding="utf-8") as f:
        json.dump(calib_artifact, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved verified calibration artifact to {calib_path}")

    # Save detailed report
    report = {
        "milestone": "Milestone 9 Calibration",
        "model_dir": str(MODEL_DIR),
        "optimal_temperature": optimal_T,
        "optimization": opt_res,
        "fresh_eval_t1": eval_t1,
        "fresh_eval_topt": eval_topt,
        "gate_passed": gate_passed,
        "gate_reasons": gate_reasons,
    }
    report_path = OUT_DIR / "calibration_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Review bundle zip
    bundle_path = OUT_DIR / "review_bundle.zip"
    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(calib_path, arcname="calibration.json")
        zf.write(report_path, arcname="calibration_report.json")
        zf.write(CALIB_FILE, arcname="calibration.jsonl")
        zf.write(FRESH_CALIB_FILE, arcname="fresh_calibration_eval.jsonl")

    import hashlib
    h = hashlib.sha256(open(bundle_path, "rb").read()).hexdigest()
    logger.info(f"Created review_bundle.zip ({bundle_path.stat().st_size} bytes, SHA256: {h})")

    if gate_passed:
        logger.info("\n=======================================================")
        logger.info("MILESTONE 9 GATE PASSED!")
        logger.info("=======================================================")


if __name__ == "__main__":
    main()
