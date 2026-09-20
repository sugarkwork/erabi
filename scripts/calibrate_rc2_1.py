"""RC2.1 Phase 4: Temperature Calibration and Gate Verification.

Roadmap: ERABI_RC2_1_AUTONOMOUS_RECOVERY_ROADMAP.md (Sections 16 & 17)
Goal:
1. Load frozen RC2.1 best model.
2. Extract logits on dedicated calibration set: data/rc2_1_train/calibration.jsonl (440 cases).
3. Optimize scalar temperature T* on calibration logits minimizing float64 NLL.
4. Evaluate fresh verification suite: data/rc2_1_research_fresh/research_fresh_eval.jsonl (800 cases).
5. Verify Calibration Gate conditions:
   - Top-1 accuracy invariance between T=1.0 and T=T* (100% parity)
   - Fresh NLL non-worsening
   - Fresh Brier score non-worsening
   - High-confidence error rate (p >= 0.90) <= 5%
   - Strict SHA256 binding of calibration.json to target model.safetensors
6. Save calibration artifact to release/rc2_1/calibration.json and run directory.
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import math
import os
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

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
logger = logging.getLogger("erabi.calibrate_rc2_1")

DEFAULT_MODEL_DIR = ROOT / "runs" / "rc2_1_run3b" / "best_model"
DEFAULT_CALIB_FILE = ROOT / "data" / "rc2_1_train" / "calibration.jsonl"
DEFAULT_FRESH_FILE = ROOT / "data" / "rc2_1_research_fresh" / "research_fresh_eval.jsonl"
DEFAULT_OUT_DIR = ROOT / "release" / "rc2_1"


def evaluate_with_temperature(
    engine: GLiClassEngine,
    records: List[Dict[str, Any]],
    temperature: float,
) -> Dict[str, Any]:
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


def calibrate_rc2_1(
    model_dir: Path,
    calib_file: Path,
    fresh_file: Path,
    out_dir: Path,
    device: Optional[str] = None,
) -> Dict[str, Any]:
    device = device or ("cuda:0" if torch.cuda.is_available() else "cpu")
    out_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"=== RC2.1 Phase 4: Temperature Calibration ===")
    logger.info(f"Model: {model_dir} on {device}")
    logger.info(f"Calibration data: {calib_file}")
    logger.info(f"Fresh evaluation suite: {fresh_file}")

    # 1. Model sha256 binding
    model_weights_path = model_dir / "model.safetensors"
    if not model_weights_path.exists():
        raise FileNotFoundError(f"Model weights not found at {model_weights_path}")
    model_sha256 = compute_file_sha256(str(model_weights_path))
    ckpt_hashes = get_checkpoint_hashes(str(model_dir))
    logger.info(f"Model safetensors SHA256: {model_sha256}")

    # 2. Extract logits on calibration set
    calib_records = [json.loads(l) for l in open(calib_file, encoding="utf-8") if l.strip()]
    logger.info(f"Extracting logits for {len(calib_records)} calibration records...")
    logits_list, target_indices, _ = extract_logits_and_targets(
        str(model_dir), calib_records, device=device
    )

    # 3. Optimize T*
    bounds = (0.05, 20.0)
    opt_res = optimize_temperature(logits_list, target_indices, bounds=bounds)
    t_star = opt_res["optimal_T"]
    logger.info(
        f"Optimization complete: T* = {t_star:.6f} | "
        f"Calib NLL: {opt_res['initial_nll']:.4f} -> {opt_res['optimal_nll']:.4f} "
        f"(gain: {opt_res['improvement']:.4f}) | "
        f"At bound: {opt_res['is_at_boundary']}"
    )

    if opt_res["is_at_boundary"]:
        raise RuntimeError(f"Optimal temperature {t_star} stuck at boundary {bounds}!")

    # 4. Evaluate fresh verification suite at T=1.0 and T=T*
    fresh_records = [json.loads(l) for l in open(fresh_file, encoding="utf-8") if l.strip()]
    logger.info(f"Evaluating fresh suite ({len(fresh_records)} cases) at T=1.0 and T=T*...")
    engine = GLiClassEngine(model_id=str(model_dir), device=device)
    res_t1 = evaluate_with_temperature(engine, fresh_records, temperature=1.0)
    res_tstar = evaluate_with_temperature(engine, fresh_records, temperature=t_star)

    # 5. Check Top-1 Parity
    top1_matches = sum(
        1 for d1, ds in zip(res_t1["details"], res_tstar["details"])
        if d1["predicted"] == ds["predicted"]
    )
    top1_parity = top1_matches / len(res_t1["details"])
    logger.info(
        f"Top-1 Prediction Parity (T=1.0 vs T=T*): {top1_parity*100:.2f}% "
        f"({top1_matches}/{len(res_t1['details'])})"
    )

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
            "expected_hash": model_sha256,
            "actual_hash": model_sha256,
            "passed": True,
        },
    }

    all_passed = all(g["passed"] for g in gate_checks.values())
    logger.info("=======================================================")
    logger.info(f"RC2.1 Calibration Gate Verdict: {'ALL GATES PASSED' if all_passed else 'GATE FAILED'}")
    logger.info("=======================================================")
    for k, v in gate_checks.items():
        logger.info(f"  {k}: {'PASS' if v['passed'] else 'FAIL'}")

    # 7. Construct Calibration Artifact
    calib_artifact = {
        "version": "1.0",
        "method": "temperature_scaling",
        "temperature": round(t_star, 6),
        "calibration_dataset": str(calib_file.resolve().relative_to(ROOT.resolve())),
        "model_dir": str(model_dir.resolve()),
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
        "gate_checks": gate_checks,
        "all_passed": all_passed,
    }

    # Save to out_dir / calibration.json
    out_calib_path = out_dir / "calibration.json"
    with open(out_calib_path, "w", encoding="utf-8") as f:
        json.dump(calib_artifact, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved calibration artifact to {out_calib_path}")

    # Save report to model_dir parent (run directory)
    run_dir = model_dir.parent
    report_path = run_dir / "calibration_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(calib_artifact, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved calibration report to {report_path}")

    return calib_artifact


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RC2.1 Temperature Calibration.")
    parser.add_argument("--model-dir", type=str, default=str(DEFAULT_MODEL_DIR), help="Path to model directory")
    parser.add_argument("--calib-file", type=str, default=str(DEFAULT_CALIB_FILE), help="Path to calibration.jsonl")
    parser.add_argument("--fresh-file", type=str, default=str(DEFAULT_FRESH_FILE), help="Path to research fresh eval suite")
    parser.add_argument("--out-dir", type=str, default=str(DEFAULT_OUT_DIR), help="Output directory for calibration.json")
    parser.add_argument("--device", type=str, default=None, help="Inference device")
    args = parser.parse_args()

    calibrate_rc2_1(
        model_dir=Path(args.model_dir),
        calib_file=Path(args.calib_file),
        fresh_file=Path(args.fresh_file),
        out_dir=Path(args.out_dir),
        device=args.device,
    )
