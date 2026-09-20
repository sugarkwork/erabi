"""Milestone 22 — RC2 Temperature Calibration and Gate Verification.

Roadmap: ERABI_RC2_AUTONOMOUS_RESEARCH_ROADMAP.md (Section 16)
Goal: Calibrate frozen RC2 candidate model on dedicated calibration data:
- Target model: release/rc2/model/ (SHA256 locked)
- Calibration set: data/rc2_m22_calibration/calibration.jsonl (100 cases)
- Fresh verification set: data/rc2_m22_calibration/fresh_calibration_eval.jsonl (100 cases)

Gate Conditions:
1. Top-1 accuracy invariance between T=1.0 and T=T* (100% parity)
2. Fresh NLL improvement (or non-worsening)
3. Brier score non-worsening
4. High-confidence error rate (p >= 0.90) <= 5%
5. Cryptographic hash binding of calibration.json to model.safetensors
"""

from __future__ import annotations

import datetime
import json
import logging
import math
import os
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

from erabi.calibrate import (
    build_calibration_artifact,
    compute_file_sha256,
    extract_logits_and_targets,
    get_checkpoint_hashes,
    optimize_temperature,
)
from erabi.inference import GLiClassEngine
from erabi.schema import ChoiceRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.m22_calibration")

RUNS_DIR = ROOT / "runs/rc2_m22_calibration"
RUNS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_DIR = ROOT / "release/rc2/model"
CALIB_FILE = ROOT / "data/rc2_m22_calibration/calibration.jsonl"
FRESH_FILE = ROOT / "data/rc2_m22_calibration/fresh_calibration_eval.jsonl"


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
        pred_prob = probs[pred_cid]
        if pred_prob >= 0.90:
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
    logger.info("=== Milestone 22 RC2 Calibration Execution ===")
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    logger.info(f"Loading frozen RC2 model from {MODEL_DIR} on {device}")

    # 1. Verify model weights hash
    model_weights_path = MODEL_DIR / "model.safetensors"
    model_sha256 = compute_file_sha256(str(model_weights_path))
    logger.info(f"Target model.safetensors SHA256: {model_sha256}")

    # 2. Extract logits on calibration set
    calib_records = [json.loads(l) for l in open(CALIB_FILE, encoding="utf-8") if l.strip()]
    logger.info(f"Extracting logits for {len(calib_records)} calibration records...")
    logits_list, target_indices, _ = extract_logits_and_targets(
        str(MODEL_DIR), calib_records, device=device
    )

    # 3. Optimize Temperature T*
    bounds = (0.1, 10.0)
    opt_res = optimize_temperature(logits_list, target_indices, bounds=bounds)
    t_star = opt_res["optimal_T"]
    logger.info(
        f"Optimization complete: T* = {t_star:.6f} | "
        f"Calib NLL: {opt_res['initial_nll']:.4f} -> {opt_res['optimal_nll']:.4f} "
        f"(gain: {opt_res['improvement']:.4f}) | "
        f"At bound: {opt_res['is_at_boundary']}"
    )

    if opt_res["is_at_boundary"]:
        raise RuntimeError(f"Optimal temperature {t_star} stuck to boundary {bounds}!")

    # 4. Evaluate Fresh Calibration Suite at T=1.0 and T=T*
    logger.info("Evaluating fresh calibration suite at T=1.0 and T=T*...")
    engine = GLiClassEngine(model_id=str(MODEL_DIR), device=device)
    res_t1 = evaluate_with_temperature(engine, FRESH_FILE, temperature=1.0)
    res_tstar = evaluate_with_temperature(engine, FRESH_FILE, temperature=t_star)

    # 5. Check Top-1 Parity
    top1_matches = sum(
        1 for d1, ds in zip(res_t1["details"], res_tstar["details"])
        if d1["predicted"] == ds["predicted"]
    )
    top1_parity = top1_matches / len(res_t1["details"])
    logger.info(f"Top-1 Prediction Parity (T=1.0 vs T=T*): {top1_parity*100:.2f}% ({top1_matches}/{len(res_t1['details'])})")

    # 6. Gate Verifications
    gate_checks = {
        "gate_top1_parity_100": {
            "threshold": 1.0,
            "actual": top1_parity,
            "passed": bool(top1_parity == 1.0),
        },
        "gate_fresh_nll_non_worsening": {
            "threshold": res_t1["mean_nll"],
            "actual": res_tstar["mean_nll"],
            "passed": bool(res_tstar["mean_nll"] <= res_t1["mean_nll"] + 1e-4),
        },
        "gate_fresh_brier_non_worsening": {
            "threshold": res_t1["mean_brier"],
            "actual": res_tstar["mean_brier"],
            "passed": bool(res_tstar["mean_brier"] <= res_t1["mean_brier"] + 1e-4),
        },
        "gate_high_conf_error_le_5": {
            "threshold": 0.05,
            "actual": res_tstar["high_conf_error_rate"],
            "passed": bool(res_tstar["high_conf_error_rate"] <= 0.05),
        },
        "gate_model_hash_binding": {
            "expected_hash": "dd3bae25efcce97df8b14cf29064c9910f62686436ff95bb16b1c184fb03c0c0",
            "actual_hash": model_sha256,
            "passed": bool(model_sha256 == "dd3bae25efcce97df8b14cf29064c9910f62686436ff95bb16b1c184fb03c0c0"),
        },
    }

    all_passed = all(g["passed"] for g in gate_checks.values())
    logger.info("=======================================================")
    logger.info(f"Milestone 22 Gate Verdict: {'ALL GATES PASSED' if all_passed else 'GATE FAILED'}")
    logger.info("=======================================================")
    for k, v in gate_checks.items():
        logger.info(f"  {k}: {'PASS' if v['passed'] else 'FAIL'}")

    # 7. Build calibration artifact strictly bound to model hashes
    ckpt_hashes = get_checkpoint_hashes(str(MODEL_DIR))
    calib_artifact = {
        "version": "1.0",
        "method": "temperature_scaling",
        "temperature": t_star,
        "calibration_dataset": "data/rc2_m22_calibration/calibration.jsonl",
        "model_dir": str(MODEL_DIR),
        "target_model_sha256": model_sha256,
        "checkpoint_hashes": ckpt_hashes,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "optimization": opt_res,
        "fresh_eval_metrics": {
            "t_1_0": {
                "accuracy": res_t1["accuracy"],
                "mean_nll": res_t1["mean_nll"],
                "mean_brier": res_t1["mean_brier"],
                "high_conf_error_rate": res_t1["high_conf_error_rate"],
            },
            "t_star": {
                "accuracy": res_tstar["accuracy"],
                "mean_nll": res_tstar["mean_nll"],
                "mean_brier": res_tstar["mean_brier"],
                "high_conf_error_rate": res_tstar["high_conf_error_rate"],
            },
        },
    }

    # Save to release/rc2 and runs/rc2_m22_calibration
    rel_calib_path = ROOT / "release/rc2/calibration.json"
    with open(rel_calib_path, "w", encoding="utf-8") as f:
        json.dump(calib_artifact, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved calibration artifact to {rel_calib_path}")

    run_calib_path = RUNS_DIR / "calibration.json"
    with open(run_calib_path, "w", encoding="utf-8") as f:
        json.dump(calib_artifact, f, indent=2, ensure_ascii=False)

    report_path = RUNS_DIR / "calibration_report.json"
    report_data = {
        "milestone": "Milestone 22 — RC2 Calibration",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "t_star": t_star,
        "gate_checks": gate_checks,
        "all_passed": all_passed,
        "res_t1": {k: v for k, v in res_t1.items() if k != "details"},
        "res_tstar": {k: v for k, v in res_tstar.items() if k != "details"},
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved calibration report to {report_path}")


if __name__ == "__main__":
    main()
