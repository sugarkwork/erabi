"""Temperature calibration module for ERABI (M3.1).

Optimizes a single temperature parameter T > 0 on calibration dataset logits
to minimize Negative Log-Likelihood (NLL) using scipy.optimize.minimize_scalar.

Invariants:
  - Preserves exact model candidate ranking (single T > 0 is strictly monotonic).
  - Only evaluates valid candidate logits (padding excluded).
  - Computes NLL using log_softmax in float64 for extreme numerical stability.
  - Binds calibration artifact strictly to model checkpoint file hashes.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import logging
import math
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.nn.functional as F
from erabi.schema import ChoiceRequest, MAX_TOKENS
from gliclass import GLiClassModel, ZeroShotClassificationPipeline
from scipy.optimize import minimize_scalar
from transformers import AutoTokenizer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.calibrate")


def compute_file_sha256(filepath: str, chunk_size: int = 1024 * 1024) -> str:
    """Compute SHA256 hex digest of a file in chunks to avoid high memory usage."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_checkpoint_hashes(checkpoint_dir: str) -> Dict[str, str]:
    """Compute sha256 hashes for all primary files in the checkpoint directory."""
    hashes = {}
    for fname in sorted(os.listdir(checkpoint_dir)):
        fpath = os.path.join(checkpoint_dir, fname)
        if os.path.isfile(fpath):
            hashes[fname] = compute_file_sha256(fpath)
    return hashes


def extract_logits_and_targets(
    model_id: str,
    records: List[Dict[str, Any]],
    device: Optional[str] = None,
) -> Tuple[List[List[float]], List[int], List[Dict[str, Any]]]:
    """Run model once over records to extract raw float32 logits and target indices."""
    if device is None:
        device = "cuda:0" if torch.cuda.is_available() else "cpu"

    logger.info(f"Loading checkpoint from {model_id} onto {device}...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = GLiClassModel.from_pretrained(model_id).to(device)
    model.eval()

    pipeline = ZeroShotClassificationPipeline(
        model=model,
        tokenizer=tokenizer,
        classification_type="single-label",
        device=device,
    )
    inner_pipe = pipeline.pipe

    logits_list: List[List[float]] = []
    target_indices: List[int] = []
    metadata_list: List[Dict[str, Any]] = []

    logger.info(f"Extracting raw logits for {len(records)} records...")
    with torch.inference_mode():
        for row in records:
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

            outputs = model(**tokenized, max_num_classes=max_num_classes)
            # Cast logits to float32 to prevent BFloat16 conversion errors
            sample_logits = outputs.logits[0, : len(labels)].to(torch.float32).cpu().tolist()

            # Validate logits
            for val in sample_logits:
                if not math.isfinite(val):
                    raise ValueError(f"Model returned non-finite logit: {val}")

            logits_list.append(sample_logits)
            target_indices.append(target_idx)
            metadata_list.append(row)

    return logits_list, target_indices, metadata_list


def compute_nll_objective(
    logits_list: List[List[float]],
    target_indices: List[int],
    temperature: float,
) -> float:
    """Compute mean NLL in double precision using PyTorch log_softmax."""
    if temperature <= 0.0 or not math.isfinite(temperature):
        return 1e9

    total_nll = 0.0
    for logits, tgt in zip(logits_list, target_indices):
        t_logits = torch.tensor(logits, dtype=torch.float64) / temperature
        log_probs = F.log_softmax(t_logits, dim=-1)
        total_nll += -float(log_probs[tgt].item())

    return total_nll / len(logits_list)


def optimize_temperature(
    logits_list: List[List[float]],
    target_indices: List[int],
    bounds: Tuple[float, float] = (0.05, 20.0),
    max_evals: int = 100,
) -> Dict[str, Any]:
    """Find optimal temperature T > 0 that minimizes NLL on the logits."""
    eval_count = 0
    t1_nll = compute_nll_objective(logits_list, target_indices, 1.0)

    def objective(T: float) -> float:
        nonlocal eval_count
        eval_count += 1
        return compute_nll_objective(logits_list, target_indices, T)

    res = minimize_scalar(
        objective,
        bounds=bounds,
        method="bounded",
        options={"maxiter": max_evals, "xatol": 1e-4},
    )

    optimal_T = float(res.x)
    optimal_nll = float(res.fun)

    # Check for boundary saturation
    is_at_boundary = (optimal_T <= bounds[0] + 0.01) or (optimal_T >= bounds[1] - 0.1)

    return {
        "initial_T": 1.0,
        "initial_nll": t1_nll,
        "initial_nll_scientific": f"{t1_nll:.6e}",
        "optimal_T": optimal_T,
        "optimal_nll": optimal_nll,
        "optimal_nll_scientific": f"{optimal_nll:.6e}",
        "improvement": t1_nll - optimal_nll,
        "eval_count": eval_count,
        "success": bool(res.success),
        "is_at_boundary": is_at_boundary,
        "bounds": bounds,
    }


def build_calibration_artifact(
    temperature: float,
    status: str,
    checkpoint_dir: str,
    dataset_path: str,
    dataset_cases: int,
    dataset_description: str = "ERABI synthetic rule calibration set",
    optimization_info: Optional[Dict[str, Any]] = None,
    adoption_decision: str = "ACCEPT_SCOPED",
    adoption_reason: str = "",
    scope: str = "bounded_synthetic_rules_only",
    precision: str = "float32_forward_float64_nll",
    artifact_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Construct a verified calibration artifact adhering strictly to runtime contracts."""
    from erabi.schema import (
        ALLOWED_CALIBRATION_STATUSES,
        FORMATTER_VERSION,
        MAX_TOKENS,
        SCHEMA_VERSION,
    )

    if status not in ALLOWED_CALIBRATION_STATUSES:
        raise ValueError(
            f"Invalid calibration status '{status}'. Must be one of {sorted(ALLOWED_CALIBRATION_STATUSES)}."
        )

    if not math.isfinite(temperature) or temperature <= 0.0:
        raise ValueError(f"Calibration temperature must be positive and finite, got {temperature}")

    if artifact_id is None:
        artifact_id = f"calib-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')}"

    checkpoint_hashes = get_checkpoint_hashes(checkpoint_dir)
    calib_data_hash = compute_file_sha256(dataset_path)

    artifact = {
        "artifact_id": artifact_id,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": status,
        "temperature": round(temperature, 4),
        "method": "temperature_scaling_nll_minimize_scalar",
        "optimization": optimization_info or {},
        "target_model": {
            "checkpoint_path": os.path.abspath(checkpoint_dir),
            "files": checkpoint_hashes,
        },
        "dataset": {
            "path": os.path.abspath(dataset_path),
            "cases": dataset_cases,
            "sha256": calib_data_hash,
            "description": dataset_description,
        },
        "contract": {
            "schema_version": SCHEMA_VERSION,
            "max_tokens": MAX_TOKENS,
            "formatter_version": FORMATTER_VERSION,
            "precision": precision,
            "decision_policy": "review_default",
            "scope": scope,
        },
        "adoption": {
            "decision": adoption_decision,
            "reason": adoption_reason,
        },
    }
    return artifact


def main():
    parser = argparse.ArgumentParser(prog="python -m erabi.calibrate")
    parser.add_argument("--data-dir", type=str, default="data/m3_6_cal", help="Data directory containing calibration.jsonl")
    parser.add_argument("--model-id", type=str, default="runs/m3_5_ce10/trained/checkpoint", help="Path to checkpoint")
    parser.add_argument("--output-dir", type=str, default="runs/m3_7_calibration_handoff", help="Output directory")
    parser.add_argument("--device", type=str, default=None, help="Device")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    calib_file = os.path.join(args.data_dir, "calibration.jsonl")
    if not os.path.exists(calib_file):
        raise FileNotFoundError(f"Calibration data not found at {calib_file}")

    records = []
    with open(calib_file, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))

    logger.info(f"Loaded {len(records)} calibration cases.")

    # 1. Extract logits
    logits_list, target_indices, metadata_list = extract_logits_and_targets(
        args.model_id, records, device=args.device
    )

    # 2. Optimize temperature
    logger.info("Optimizing single temperature parameter T...")
    opt_res = optimize_temperature(logits_list, target_indices, bounds=(0.05, 20.0))

    logger.info(f"T=1.0 NLL: {opt_res['initial_nll']:.6f} ({opt_res['initial_nll_scientific']})")
    logger.info(f"Optimal T: {opt_res['optimal_T']:.4f} -> NLL: {opt_res['optimal_nll']:.6f} ({opt_res['optimal_nll_scientific']})")
    logger.info(f"NLL Improvement: {opt_res['improvement']:.6f} in {opt_res['eval_count']} evaluations.")

    # 3. Status determination adhering to runtime contract
    if not opt_res["success"] or opt_res["is_at_boundary"] or opt_res["improvement"] <= 0:
        logger.warning("Optimization failed, hit boundary, or did not improve. Setting status to 'none'.")
        status = "none"
        decision = "REJECTED"
        reason = "Optimization failed, hit boundary, or did not improve NLL."
    else:
        status = "applied"
        decision = "ACCEPT_SCOPED"
        reason = f"NLL improved by {opt_res['improvement']:.6f} on calibration set."

    calibration_artifact = build_calibration_artifact(
        temperature=opt_res["optimal_T"],
        status=status,
        checkpoint_dir=args.model_id,
        dataset_path=calib_file,
        dataset_cases=len(records),
        dataset_description="ERABI synthetic rule calibration set",
        optimization_info=opt_res,
        adoption_decision=decision,
        adoption_reason=reason,
        scope="bounded_synthetic_rules_only",
    )

    out_path = os.path.join(args.output_dir, "calibration.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(calibration_artifact, f, indent=2, ensure_ascii=False)

    logger.info(f"Calibration artifact saved to {out_path}")


if __name__ == "__main__":
    main()

