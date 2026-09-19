"""Run comprehensive calibration and evaluation pipeline for ERABI M3.6.

Steps:
1. Load W_v2_ce10 (runs/m3_5_ce10/trained/checkpoint).
2. Run single GPU inference on:
   - data/m3_6_cal/calibration.jsonl (200 cases)
   - data/m3_6_cal/fresh_eval.jsonl (200 cases)
   Save raw logits to runs/m3_6_calibration/.
3. Optimize single temperature T > 0 on calibration.jsonl using float64 NLL minimization.
4. Evaluate fresh_eval.jsonl under T=1.0 and calibrated T:
   - Accuracy, pair both rate (total, diff, same, per task family)
   - Mean NLL, Mean Brier score (overall, 2-choice, 3-choice)
   - Confidence bins (0.0-0.5, 0.5-0.7, 0.7-0.9, 0.9-1.0)
   - Top high-confidence error cases
   - Hypothetical threshold policy evaluation (0.8, 0.9, 0.95)
5. Apply the exact same T to existing diagnostic sets using saved raw_logits:
   - data/m3_3_v2/eval_v2.jsonl
   - examples/smoke_cases.jsonl
   - data/m3_1/transfer_probe.jsonl
   Report as separate scoped diagnostics (do not combine into single aggregate).
6. Save calibration.json with strict checkpoint file hashes and metadata.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import logging
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn.functional as F
from erabi.schema import ChoiceRequest, MAX_TOKENS
from gliclass import GLiClassModel, ZeroShotClassificationPipeline
from scipy.optimize import minimize_scalar
from transformers import AutoTokenizer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.m3_6_cal")

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "runs/m3_5_ce10/trained/checkpoint"
OUT_DIR = ROOT / "runs/m3_6_calibration"


def compute_file_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_checkpoint_hashes(checkpoint_dir: Path) -> Dict[str, str]:
    hashes = {}
    for fname in sorted(os.listdir(checkpoint_dir)):
        fpath = checkpoint_dir / fname
        if fpath.is_file():
            hashes[fname] = compute_file_sha256(fpath)
    return hashes


def run_inference_and_extract_records(
    model: GLiClassModel,
    tokenizer: AutoTokenizer,
    records: List[Dict[str, Any]],
    device: str,
) -> List[Dict[str, Any]]:
    pipeline = ZeroShotClassificationPipeline(
        model=model,
        tokenizer=tokenizer,
        classification_type="single-label",
        device=device,
    )
    inner_pipe = pipeline.pipe

    results = []
    with torch.inference_mode():
        for row in records:
            req = ChoiceRequest.from_dict(row)
            labels = [c.text for c in req.choices]
            choice_ids = [c.id for c in req.choices]
            target_cid = row["target"]["choice_id"]
            target_idx = choice_ids.index(target_cid)

            tokenized = inner_pipe.prepare_inputs(
                texts=[req.context],
                labels=[labels],
                same_labels=False,
                prompt=[req.question],
            )
            max_num_classes = inner_pipe._resolve_max_num_classes([labels], same_labels=False)

            outputs = model(**tokenized, max_num_classes=max_num_classes)
            sample_logits = outputs.logits[0, : len(labels)].to(torch.float32).cpu().tolist()

            for val in sample_logits:
                if not math.isfinite(val):
                    raise ValueError(f"Model returned non-finite logit: {val}")

            best_idx = int(np.argmax(sample_logits))
            best_cid = choice_ids[best_idx]
            is_correct = (best_cid == target_cid)

            res = {
                "id": row["id"],
                "group_id": row["group_id"],
                "task_family": row.get("task_family"),
                "template_family": row.get("template_family"),
                "rule_kind": row.get("rule_kind"),
                "choices": [{"id": c.id, "text": c.text} for c in req.choices],
                "target": target_cid,
                "target_index": target_idx,
                "best_candidate_id": best_cid,
                "is_correct": is_correct,
                "raw_logits": sample_logits,
            }
            results.append(res)
    return results


def compute_nll_and_brier(
    logits_list: List[List[float]],
    target_indices: List[int],
    temperature: float,
) -> Tuple[float, float, List[Dict[str, Any]]]:
    """Compute NLL and Brier score in float64 with given temperature."""
    total_nll = 0.0
    total_brier = 0.0
    item_metrics = []

    for logits, tgt in zip(logits_list, target_indices):
        t_logits = torch.tensor(logits, dtype=torch.float64) / temperature
        log_probs = F.log_softmax(t_logits, dim=-1)
        probs = torch.exp(log_probs).numpy()

        nll_val = -float(log_probs[tgt].item())
        total_nll += nll_val

        # Brier: sum_i (p_i - y_i)^2
        one_hot = np.zeros_like(probs)
        one_hot[tgt] = 1.0
        brier_val = float(np.sum((probs - one_hot) ** 2))
        total_brier += brier_val

        item_metrics.append({
            "probs": probs.tolist(),
            "p_max": float(np.max(probs)),
            "p_target": float(probs[tgt]),
            "nll": nll_val,
            "brier": brier_val,
        })

    n = len(logits_list)
    return total_nll / n, total_brier / n, item_metrics


def evaluate_dataset_at_temperatures(
    dataset_records: List[Dict[str, Any]],
    temperature: float,
) -> Dict[str, Any]:
    """Comprehensive evaluation of a dataset under T=1.0 and calibrated T."""
    logits_list = [r["raw_logits"] for r in dataset_records]
    target_indices = [r["target_index"] for r in dataset_records]

    nll_t1, brier_t1, metrics_t1 = compute_nll_and_brier(logits_list, target_indices, 1.0)
    nll_cal, brier_cal, metrics_cal = compute_nll_and_brier(logits_list, target_indices, temperature)

    # Invariant check: Argmax predictions must not change under positive scalar T
    for i, r in enumerate(dataset_records):
        best_t1 = int(np.argmax(metrics_t1[i]["probs"]))
        best_cal = int(np.argmax(metrics_cal[i]["probs"]))
        best_raw = int(np.argmax(r["raw_logits"]))
        assert best_t1 == best_cal == best_raw, f"Argmax changed under temperature! item {r['id']}"

    total_cases = len(dataset_records)
    correct_count = sum(1 for r in dataset_records if r["is_correct"])
    accuracy = correct_count / total_cases

    # Pair evaluation (only if dataset has strictly 2 items per group)
    pairs = {}
    for i, r in enumerate(dataset_records):
        gid = r.get("group_id") or r.get("id")
        if gid not in pairs:
            pairs[gid] = []
        pairs[gid].append((r, metrics_cal[i]))

    total_pairs = len(pairs)
    both_correct = 0
    diff_target_both = 0
    diff_target_total = 0
    same_target_both = 0
    same_target_total = 0
    task_breakdown = {}

    is_paired_dataset = all(len(items) == 2 for items in pairs.values())

    if is_paired_dataset:
        for gid, items in pairs.items():
            r1, m1 = items[0]
            r2, m2 = items[1]
            c1 = r1["is_correct"]
            c2 = r2["is_correct"]
            is_both = (c1 and c2)

            task_fam = r1.get("task_family") or "unknown"
            rule_k = r1.get("rule_kind")
            key = f"{task_fam}:{rule_k}" if rule_k else task_fam
            if key not in task_breakdown:
                task_breakdown[key] = {"total_pairs": 0, "both_correct": 0, "diff_pairs": 0, "diff_both": 0}
            task_breakdown[key]["total_pairs"] += 1

            if is_both:
                both_correct += 1
                task_breakdown[key]["both_correct"] += 1

            if r1["target"] != r2["target"]:
                diff_target_total += 1
                task_breakdown[key]["diff_pairs"] += 1
                if is_both:
                    diff_target_both += 1
                    task_breakdown[key]["diff_both"] += 1
            else:
                same_target_total += 1
                if is_both:
                    same_target_both += 1

        pair_stats = {
            "is_paired": True,
            "total_pairs": total_pairs,
            "both_correct": both_correct,
            "both_rate": both_correct / total_pairs,
            "diff_target_pairs": diff_target_total,
            "diff_target_both": diff_target_both,
            "diff_target_rate": diff_target_both / max(1, diff_target_total),
            "same_target_pairs": same_target_total,
            "same_target_both": same_target_both,
            "same_target_rate": same_target_both / max(1, same_target_total),
            "task_breakdown": task_breakdown,
        }
    else:
        pair_stats = {
            "is_paired": False,
            "note": "Dataset contains single or non-binary group records (e.g. smoke cases). Pair stats omitted.",
        }

    # NLL / Brier breakdown by choice count (2 vs 3 choices)
    nll_2ch_t1, nll_2ch_cal = [], []
    nll_3ch_t1, nll_3ch_cal = [], []
    brier_2ch_t1, brier_2ch_cal = [], []
    brier_3ch_t1, brier_3ch_cal = [], []

    for i, r in enumerate(dataset_records):
        n_ch = len(r["choices"])
        if n_ch == 2:
            nll_2ch_t1.append(metrics_t1[i]["nll"])
            nll_2ch_cal.append(metrics_cal[i]["nll"])
            brier_2ch_t1.append(metrics_t1[i]["brier"])
            brier_2ch_cal.append(metrics_cal[i]["brier"])
        else:
            nll_3ch_t1.append(metrics_t1[i]["nll"])
            nll_3ch_cal.append(metrics_cal[i]["nll"])
            brier_3ch_t1.append(metrics_t1[i]["brier"])
            brier_3ch_cal.append(metrics_cal[i]["brier"])

    # Confidence bin analysis (calibrated vs uncalibrated)
    def compute_bins(metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        bin_ranges = [(0.0, 0.5), (0.5, 0.7), (0.7, 0.9), (0.9, 1.000001)]
        bin_stats = []
        for low, high in bin_ranges:
            indices = [i for i, m in enumerate(metrics) if low <= m["p_max"] < high]
            count = len(indices)
            if count > 0:
                avg_conf = float(np.mean([metrics[i]["p_max"] for i in indices]))
                acc = float(np.mean([1.0 if dataset_records[i]["is_correct"] else 0.0 for i in indices]))
            else:
                avg_conf = None
                acc = None
            bin_stats.append({
                "range": f"[{low:.1f}, {min(1.0, high):.1f})",
                "count": count,
                "avg_confidence": avg_conf,
                "accuracy": acc,
            })
        return bin_stats

    bins_t1 = compute_bins(metrics_t1)
    bins_cal = compute_bins(metrics_cal)

    # High-confidence error cases under calibrated T
    errors = []
    for i, r in enumerate(dataset_records):
        if not r["is_correct"]:
            errors.append({
                "id": r["id"],
                "group_id": r["group_id"],
                "task_family": r.get("task_family"),
                "target": r["target"],
                "predicted": r["best_candidate_id"],
                "p_max_t1": metrics_t1[i]["p_max"],
                "p_max_cal": metrics_cal[i]["p_max"],
                "p_target_cal": metrics_cal[i]["p_target"],
                "nll_t1": metrics_t1[i]["nll"],
                "nll_cal": metrics_cal[i]["nll"],
            })
    errors.sort(key=lambda x: x["p_max_cal"], reverse=True)

    # Threshold policies (0.8, 0.9, 0.95)
    def compute_threshold_policy(metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        policy = {}
        for th in [0.8, 0.9, 0.95]:
            accepted = [i for i, m in enumerate(metrics) if m["p_max"] >= th]
            n_acc = len(accepted)
            coverage = n_acc / total_cases
            if n_acc > 0:
                n_err = sum(1 for i in accepted if not dataset_records[i]["is_correct"])
                risk = n_err / n_acc
            else:
                n_err = 0
                risk = None
            policy[f"threshold_{th}"] = {
                "accepted_count": n_acc,
                "coverage": coverage,
                "error_count": n_err,
                "risk": risk,
            }
        return policy

    policy_t1 = compute_threshold_policy(metrics_t1)
    policy_cal = compute_threshold_policy(metrics_cal)

    return {
        "total_cases": total_cases,
        "correct_count": correct_count,
        "accuracy": accuracy,
        "pair_stats": {
            "total_pairs": total_pairs,
            "both_correct": both_correct,
            "both_rate": both_correct / total_pairs,
            "diff_target_pairs": diff_target_total,
            "diff_target_both": diff_target_both,
            "diff_target_rate": diff_target_both / max(1, diff_target_total),
            "same_target_pairs": same_target_total,
            "same_target_both": same_target_both,
            "same_target_rate": same_target_both / max(1, same_target_total),
            "task_breakdown": task_breakdown,
        },
        "metrics_uncalibrated_T1": {
            "mean_nll": nll_t1,
            "mean_brier": brier_t1,
            "nll_2choice": float(np.mean(nll_2ch_t1)) if nll_2ch_t1 else None,
            "nll_3choice": float(np.mean(nll_3ch_t1)) if nll_3ch_t1 else None,
            "brier_2choice": float(np.mean(brier_2ch_t1)) if brier_2ch_t1 else None,
            "brier_3choice": float(np.mean(brier_3ch_t1)) if brier_3ch_t1 else None,
            "confidence_bins": bins_t1,
            "policy": policy_t1,
        },
        "metrics_calibrated_T": {
            "temperature": temperature,
            "mean_nll": nll_cal,
            "mean_brier": brier_cal,
            "nll_2choice": float(np.mean(nll_2ch_cal)) if nll_2ch_cal else None,
            "nll_3choice": float(np.mean(nll_3ch_cal)) if nll_3ch_cal else None,
            "brier_2choice": float(np.mean(brier_2ch_cal)) if brier_2ch_cal else None,
            "brier_3choice": float(np.mean(brier_3ch_cal)) if brier_3ch_cal else None,
            "confidence_bins": bins_cal,
            "policy": policy_cal,
        },
        "improvement": {
            "nll_diff": nll_t1 - nll_cal,
            "brier_diff": brier_t1 - brier_cal,
        },
        "error_cases": errors,
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")

    # Compute checkpoint hashes
    checkpoint_hashes = get_checkpoint_hashes(MODEL_PATH)
    logger.info(f"Verified {len(checkpoint_hashes)} files in checkpoint.")

    # 2. Extract or load raw logits on calibration and fresh_eval
    datasets = {
        "calibration": ROOT / "data/m3_6_cal/calibration.jsonl",
        "fresh_eval": ROOT / "data/m3_6_cal/fresh_eval.jsonl",
    }

    raw_results = {}
    need_inference = False
    for sname, spath in datasets.items():
        out_pred = OUT_DIR / f"raw_logits_{sname}.jsonl"
        if out_pred.exists():
            logger.info(f"Loading existing raw logits for {sname} from {out_pred}...")
            raw_results[sname] = [json.loads(l) for l in open(out_pred, encoding="utf-8")]
        else:
            need_inference = True

    if need_inference:
        logger.info(f"Loading checkpoint from {MODEL_PATH} onto {device}...")
        tokenizer = AutoTokenizer.from_pretrained(str(MODEL_PATH))
        model = GLiClassModel.from_pretrained(str(MODEL_PATH)).to(device)
        model.eval()

        for sname, spath in datasets.items():
            if sname in raw_results:
                continue
            logger.info(f"Running inference on {sname} ({spath})...")
            records = [json.loads(l) for l in open(spath, encoding="utf-8")]
            res = run_inference_and_extract_records(model, tokenizer, records, device)
            raw_results[sname] = res

            out_pred = OUT_DIR / f"raw_logits_{sname}.jsonl"
            with open(out_pred, "w", encoding="utf-8") as f:
                for item in res:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
            logger.info(f"Saved {len(res)} raw predictions to {out_pred}")
    else:
        logger.info("All raw logits loaded from disk. Skipping model inference.")

    # 3. Optimize Temperature on calibration
    logger.info("Optimizing single temperature T on calibration data...")
    cal_logits = [r["raw_logits"] for r in raw_results["calibration"]]
    cal_targets = [r["target_index"] for r in raw_results["calibration"]]

    eval_count = 0
    t1_nll, t1_brier, _ = compute_nll_and_brier(cal_logits, cal_targets, 1.0)

    bounds = (0.05, 20.0)

    def objective(T: float) -> float:
        nonlocal eval_count
        eval_count += 1
        nll, _, _ = compute_nll_and_brier(cal_logits, cal_targets, T)
        return nll

    res = minimize_scalar(
        objective,
        bounds=bounds,
        method="bounded",
        options={"maxiter": 100, "xatol": 1e-4},
    )

    optimal_T = float(res.x)
    optimal_nll = float(res.fun)
    is_at_boundary = (optimal_T <= bounds[0] + 0.01) or (optimal_T >= bounds[1] - 0.1)

    opt_summary = {
        "initial_T": 1.0,
        "initial_nll": t1_nll,
        "optimal_T": optimal_T,
        "optimal_nll": optimal_nll,
        "improvement": t1_nll - optimal_nll,
        "eval_count": eval_count,
        "success": bool(res.success),
        "is_at_boundary": is_at_boundary,
        "bounds": bounds,
    }

    logger.info(f"Optimization finished: T={optimal_T:.4f} (NLL: {t1_nll:.6f} -> {optimal_nll:.6f}, evals={eval_count})")

    # 4. Evaluate fresh_eval under T=1.0 and calibrated T
    logger.info("Evaluating fresh_eval under T=1.0 and calibrated T...")
    fresh_eval_summary = evaluate_dataset_at_temperatures(raw_results["fresh_eval"], optimal_T)

    with open(OUT_DIR / "eval_comparison_fresh_eval.json", "w", encoding="utf-8") as f:
        json.dump(fresh_eval_summary, f, indent=2, ensure_ascii=False)

    # 5. Apply the exact same T to existing diagnostic sets (eval_v2, smoke_cases, transfer_probe)
    # Re-use saved raw_logits from runs/m3_5_ce10/comparisons/
    diag_files = {
        "eval_v2": (
            ROOT / "runs/m3_5_ce10/comparisons/W_v2_ce10_eval_v2_predictions.jsonl",
            ROOT / "data/m3_3_v2/eval_v2.jsonl",
        ),
        "smoke_cases": (
            ROOT / "runs/m3_5_ce10/comparisons/W_v2_ce10_smoke_cases_predictions.jsonl",
            ROOT / "examples/smoke_cases.jsonl",
        ),
        "transfer_probe": (
            ROOT / "runs/m3_5_ce10/comparisons/W_v2_ce10_transfer_probe_predictions.jsonl",
            ROOT / "data/m3_1/transfer_probe.jsonl",
        ),
    }

    diag_summaries = {}
    for dname, (pred_file, orig_file) in diag_files.items():
        logger.info(f"Applying calibrated T to diagnostic dataset: {dname}...")
        preds = [json.loads(l) for l in open(pred_file, encoding="utf-8")]
        # Ensure target_index is populated
        for r in preds:
            cids = [c["id"] if isinstance(c, dict) else c for c in r["choices"]]
            r["target_index"] = cids.index(r["target"])

        summary = evaluate_dataset_at_temperatures(preds, optimal_T)
        diag_summaries[dname] = summary

        with open(OUT_DIR / f"eval_comparison_{dname}.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

    # 6. Determine Adoption Decision based on §6.1 Criteria:
    # Criteria:
    # - Numerically sound and not at search boundary
    # - On fresh_eval: NLL decreases (nll_diff > 0) AND Brier score does not worsen (brier_diff >= -1e-5)
    fresh_nll_imp = fresh_eval_summary["improvement"]["nll_diff"]
    fresh_brier_imp = fresh_eval_summary["improvement"]["brier_diff"]

    if not opt_summary["success"] or opt_summary["is_at_boundary"]:
        adoption_status = "unstable_boundary"
        adoption_decision = "HOLD (採用保留)"
        decision_reason = "Optimization failed or reached search boundary."
    elif fresh_nll_imp > 0 and fresh_brier_imp >= -1e-5:
        adoption_status = "applied_scoped"
        adoption_decision = "ACCEPT_SCOPED (合成ルール限定用途の校正候補として採用)"
        decision_reason = f"Fresh eval NLL improved by {fresh_nll_imp:.6f} and Brier score improved/maintained by {fresh_brier_imp:.6f}."
    else:
        adoption_status = "rejected_no_improvement"
        adoption_decision = "HOLD (採用保留)"
        decision_reason = f"Did not meet adoption criteria: NLL diff={fresh_nll_imp:.6f}, Brier diff={fresh_brier_imp:.6f}."

    logger.info(f"Adoption Decision: {adoption_decision} - {decision_reason}")

    # 7. Save calibration.json
    cal_file = ROOT / "data/m3_6_cal/calibration.jsonl"
    artifact_id = f"calib-m3_6-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')}"

    calibration_artifact = {
        "artifact_id": artifact_id,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": adoption_status,
        "temperature": round(optimal_T, 4),
        "method": "temperature_scaling_nll_minimize_scalar",
        "optimization": opt_summary,
        "target_model": {
            "checkpoint_path": str(MODEL_PATH),
            "model_safetensors_sha256": checkpoint_hashes.get("model.safetensors"),
            "files": checkpoint_hashes,
        },
        "dataset": {
            "path": str(cal_file),
            "cases": len(raw_results["calibration"]),
            "groups": len(raw_results["calibration"]) // 2,
            "sha256": compute_file_sha256(cal_file),
            "description": "ERABI M3.6 synthetic rule calibration set (goal_following and explicit_rule pairs)",
        },
        "contract": {
            "schema_version": "1",
            "max_tokens": MAX_TOKENS,
            "precision": "float32_forward_float64_nll",
            "decision_policy": "review_default",
            "scope": "bounded_synthetic_rules_only",
        },
        "adoption": {
            "decision": adoption_decision,
            "reason": decision_reason,
            "fresh_eval_metrics": {
                "nll_t1": fresh_eval_summary["metrics_uncalibrated_T1"]["mean_nll"],
                "nll_cal": fresh_eval_summary["metrics_calibrated_T"]["mean_nll"],
                "brier_t1": fresh_eval_summary["metrics_uncalibrated_T1"]["mean_brier"],
                "brier_cal": fresh_eval_summary["metrics_calibrated_T"]["mean_brier"],
            },
        },
    }

    with open(OUT_DIR / "calibration.json", "w", encoding="utf-8") as f:
        json.dump(calibration_artifact, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved calibration artifact to {OUT_DIR / 'calibration.json'}")

    # 8. Master Summary Report
    summary_report = {
        "run_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "target_model_checkpoint": str(MODEL_PATH),
        "model_safetensors_sha256": checkpoint_hashes.get("model.safetensors"),
        "temperature_optimization": opt_summary,
        "adoption": {
            "status": adoption_status,
            "decision": adoption_decision,
            "reason": decision_reason,
        },
        "fresh_eval": fresh_eval_summary,
        "diagnostics_separate_eval": diag_summaries,
    }

    with open(OUT_DIR / "summary_report.json", "w", encoding="utf-8") as f:
        json.dump(summary_report, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved summary report to {OUT_DIR / 'summary_report.json'}")

    print("\nM3.6 Calibration and Evaluation Pipeline completed successfully!")


if __name__ == "__main__":
    main()
