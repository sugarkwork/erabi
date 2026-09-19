"""Standardized comparison script for ERABI M3.5 (W_v2_ce10 vs W_v2_first5/W_v2_gradfix).

Evaluates W_v2_ce10 (10-epoch best) on:
1. data/m3_3_v2/eval_v2.jsonl (200 cases / 100 pairs)
2. examples/smoke_cases.jsonl (12 cases)
3. data/m3_1/transfer_probe.jsonl (32 cases)

Reuses saved predictions for B0, W_fix, W_v2, W_v2_gradfix (which is bit-identical to W_v2_first5).
Computes:
- Overall metrics: Accuracy, NLL, Brier
- 47 diff-target pairs: both_correct, pred_same failure, pred_diff failure
- 53 same-target pairs: both_correct, unnecessary switch failure
- Task breakdowns: goal_following, composite_logic, boundary, comparison
- smoke 12 cases individual breakdown
- 178-case auxiliary non-overlap metric
Saves outputs to runs/m3_5_ce10/comparisons/
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from erabi.evaluate import compute_metrics
from erabi.inference import GLiClassEngine
from erabi.schema import ChoiceRequest


def compute_file_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_jsonl(filepath: Path) -> List[Dict[str, Any]]:
    with open(filepath, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def evaluate_engine_on_file(engine: GLiClassEngine, filepath: Path) -> Dict[str, Any]:
    records = load_jsonl(filepath)
    predictions = []
    t0 = time.time()
    for rec in records:
        req = ChoiceRequest.from_dict(rec)
        resp = engine.predict(req, return_logits=True)
        predictions.append({
            "id": rec["id"],
            "group_id": rec.get("group_id", ""),
            "task_family": rec.get("task_family", ""),
            "template_family": rec.get("template_family", ""),
            "rule_kind": rec.get("rule_kind", ""),
            "choices": [{"id": co.id, "probability": co.probability} for co in resp.choices],
            "best_candidate_id": resp.best_candidate_id,
            "target": rec["target"]["choice_id"],
            "raw_logits": resp.raw_logits,
            "is_correct": (resp.best_candidate_id == rec["target"]["choice_id"]),
        })
    elapsed = time.time() - t0

    targets = [p["target"] for p in predictions]
    metadata = [
        {
            "group_id": p["group_id"],
            "task_family": p["task_family"],
            "template_family": p["template_family"],
            "rule_kind": p["rule_kind"],
        }
        for p in predictions
    ]

    metrics = compute_metrics(predictions, targets, metadata=metadata, temperature=1.0)
    metrics["latency_total_sec"] = round(elapsed, 2)
    return {"metrics": metrics, "predictions": predictions}


def main():
    out_dir = ROOT_DIR / "runs" / "m3_5_ce10" / "comparisons"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Config and file hashes
    h_first5 = compute_file_sha256(ROOT_DIR / "runs" / "m3_5_ce10" / "trained" / "checkpoint_best_first5" / "model.safetensors")
    h_ce10 = compute_file_sha256(ROOT_DIR / "runs" / "m3_5_ce10" / "trained" / "checkpoint" / "model.safetensors")
    h_m3_4 = compute_file_sha256(ROOT_DIR / "runs" / "m3_4_gradfix" / "trained" / "checkpoint" / "model.safetensors")

    config = {
        "experiment": "M3.5 CE Budget Expansion (5 -> 10 epochs)",
        "base_model": "knowledgator/gliclass-instruct-base-v1.0",
        "training_data": {
            "train": "data/m3_3_v2/train.jsonl",
            "train_sha256": compute_file_sha256(ROOT_DIR / "data" / "m3_3_v2" / "train.jsonl"),
            "dev": "data/m3_3_v2/dev.jsonl",
            "dev_sha256": compute_file_sha256(ROOT_DIR / "data" / "m3_3_v2" / "dev.jsonl"),
            "eval_v2": "data/m3_3_v2/eval_v2.jsonl",
            "eval_v2_sha256": compute_file_sha256(ROOT_DIR / "data" / "m3_3_v2" / "eval_v2.jsonl"),
        },
        "hyperparameters": {
            "epochs": 10,
            "lr": 2e-5,
            "weight_decay": 0.01,
            "micro_batch_size": 2,
            "gradient_accumulation_steps": 8,
            "seed": 42,
        },
        "checkpoints": {
            "W_v2_first5_epoch": 5,
            "W_v2_first5_safetensors_sha256": h_first5,
            "W_v2_gradfix_m3_4_safetensors_sha256": h_m3_4,
            "first5_identical_to_m3_4": (h_first5 == h_m3_4),
            "W_v2_ce10_epoch": 10,
            "W_v2_ce10_safetensors_sha256": h_ce10,
        },
    }
    with open(ROOT_DIR / "runs" / "m3_5_ce10" / "config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    # 2. Run inference for W_v2_ce10
    ce10_ckpt = ROOT_DIR / "runs" / "m3_5_ce10" / "trained" / "checkpoint"
    print(f"Loading W_v2_ce10 from {ce10_ckpt}...")
    engine = GLiClassEngine(model_id=str(ce10_ckpt))

    datasets = [
        ("eval_v2", ROOT_DIR / "data" / "m3_3_v2" / "eval_v2.jsonl"),
        ("smoke_cases", ROOT_DIR / "examples" / "smoke_cases.jsonl"),
        ("transfer_probe", ROOT_DIR / "data" / "m3_1" / "transfer_probe.jsonl"),
    ]

    new_results = {}
    for ds_name, ds_path in datasets:
        print(f"Evaluating W_v2_ce10 on {ds_name}...")
        res = evaluate_engine_on_file(engine, ds_path)
        new_results[ds_name] = res
        pred_file = out_dir / f"W_v2_ce10_{ds_name}_predictions.jsonl"
        with open(pred_file, "w", encoding="utf-8") as f:
            for p in res["predictions"]:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")

    # 3. Load saved predictions for comparison models
    models = ["B0", "W_fix", "W_v2", "W_v2_gradfix", "W_v2_ce10"]
    all_preds = {
        "B0": {ds: {p["id"]: p for p in load_jsonl(ROOT_DIR / "runs" / "m3_3_v2" / "comparisons" / f"B0_{ds}_predictions.jsonl")} for ds, _ in datasets},
        "W_fix": {ds: {p["id"]: p for p in load_jsonl(ROOT_DIR / "runs" / "m3_3_v2" / "comparisons" / f"W_fix_{ds}_predictions.jsonl")} for ds, _ in datasets},
        "W_v2": {ds: {p["id"]: p for p in load_jsonl(ROOT_DIR / "runs" / "m3_3_v2" / "comparisons" / f"W_v2_{ds}_predictions.jsonl")} for ds, _ in datasets},
        "W_v2_gradfix": {ds: {p["id"]: p for p in load_jsonl(ROOT_DIR / "runs" / "m3_4_gradfix" / "comparisons" / f"W_v2_gradfix_{ds}_predictions.jsonl")} for ds, _ in datasets},
        "W_v2_ce10": {ds: {p["id"]: p for p in new_results[ds]["predictions"]} for ds, _ in datasets},
    }

    # 4. Pairwise analysis on eval_v2
    eval_records = load_jsonl(ROOT_DIR / "data" / "m3_3_v2" / "eval_v2.jsonl")
    groups = defaultdict(list)
    for r in eval_records:
        groups[r["group_id"]].append(r)

    overlap_gids = {
        "eval_v2-er-0003", "eval_v2-er-0007", "eval_v2-er-0011", "eval_v2-er-0015",
        "eval_v2-er-0019", "eval_v2-er-0025", "eval_v2-er-0057", "eval_v2-er-0071",
        "eval_v2-er-0087", "eval_v2-er-0089", "eval_v2-er-0091"
    }

    comparison_summary = {
        "datasets": {},
        "eval_v2_detailed_pairs": {
            "diff_target_47": {},
            "same_target_53": {},
            "task_family_diff_target": defaultdict(dict),
        },
        "auxiliary_178_cases": {},
    }

    for ds_name, ds_path in datasets:
        ds_records = load_jsonl(ds_path)
        comparison_summary["datasets"][ds_name] = {}
        for m in models:
            preds_m = [all_preds[m][ds_name][r["id"]] for r in ds_records]
            targets_m = [r["target"]["choice_id"] for r in ds_records]
            m_metrics = compute_metrics(preds_m, targets_m, temperature=1.0)
            comparison_summary["datasets"][ds_name][m] = {
                "accuracy": f"{m_metrics['correct_count']}/{m_metrics['count']} ({m_metrics['accuracy']*100:.1f}%)",
                "mean_nll": m_metrics["mean_nll"],
                "mean_brier": m_metrics["mean_brier"],
            }

    # Pair metrics for diff (47) and same (53)
    for cat, is_diff_target in [("diff_target_47", True), ("same_target_53", False)]:
        cat_groups = {gid: recs for gid, recs in groups.items() if (recs[0]["target"]["choice_id"] != recs[1]["target"]["choice_id"]) == is_diff_target}
        for m in models:
            both_correct = 0
            one_correct = 0
            neither_correct = 0
            pred_same = 0
            pred_diff = 0
            for gid, recs in cat_groups.items():
                p1 = all_preds[m]["eval_v2"][recs[0]["id"]]
                p2 = all_preds[m]["eval_v2"][recs[1]["id"]]
                c1 = p1["is_correct"]
                c2 = p2["is_correct"]
                if c1 and c2:
                    both_correct += 1
                elif c1 or c2:
                    one_correct += 1
                else:
                    neither_correct += 1
                if p1["best_candidate_id"] == p2["best_candidate_id"]:
                    pred_same += 1
                else:
                    pred_diff += 1

            entry = {
                "total_pairs": len(cat_groups),
                "both_correct": both_correct,
                "one_correct": one_correct,
                "neither_correct": neither_correct,
                "pred_same": pred_same,
                "pred_diff": pred_diff,
            }
            if is_diff_target:
                entry["switch_success"] = both_correct
                entry["pred_same_failure"] = pred_same
                entry["pred_diff_failure"] = len(cat_groups) - both_correct - pred_same
            comparison_summary["eval_v2_detailed_pairs"][cat][m] = entry

    # Diff target task breakdown
    diff_groups = {gid: recs for gid, recs in groups.items() if recs[0]["target"]["choice_id"] != recs[1]["target"]["choice_id"]}
    fam_groups = defaultdict(dict)
    for gid, recs in diff_groups.items():
        fam = recs[0].get("task_family")
        if fam == "explicit_rule":
            fam = f"explicit_rule:{recs[0].get('rule_kind')}"
        fam_groups[fam][gid] = recs

    for fam, f_groups in fam_groups.items():
        for m in models:
            both = sum(1 for gid, recs in f_groups.items() if all_preds[m]["eval_v2"][recs[0]["id"]]["is_correct"] and all_preds[m]["eval_v2"][recs[1]["id"]]["is_correct"])
            same_p = sum(1 for gid, recs in f_groups.items() if all_preds[m]["eval_v2"][recs[0]["id"]]["best_candidate_id"] == all_preds[m]["eval_v2"][recs[1]["id"]]["best_candidate_id"])
            comparison_summary["eval_v2_detailed_pairs"]["task_family_diff_target"][fam][m] = {
                "total_pairs": len(f_groups),
                "both_correct": both,
                "pred_same": same_p,
                "pred_diff": len(f_groups) - same_p,
            }

    # Smoke breakdown
    smoke_records = load_jsonl(ROOT_DIR / "examples" / "smoke_cases.jsonl")
    smoke_rows = []
    for sc in smoke_records:
        sid = sc["id"]
        tgt = sc["target"]["choice_id"]
        row = {"id": sid, "question": sc["question"], "target": tgt}
        for m in models:
            p = all_preds[m]["smoke_cases"][sid]
            mark = "O" if p["is_correct"] else "X"
            row[m] = f"{p['best_candidate_id']} ({mark})"
        smoke_rows.append(row)
    comparison_summary["smoke_cases_breakdown"] = smoke_rows

    # 178 non-overlap auxiliary evaluation
    non_overlap_recs = [r for r in eval_records if r["group_id"] not in overlap_gids]
    groups_178 = defaultdict(list)
    for r in non_overlap_recs:
        groups_178[r["group_id"]].append(r)
    diff_178_groups = {gid: recs for gid, recs in groups_178.items() if recs[0]["target"]["choice_id"] != recs[1]["target"]["choice_id"]}

    for m in models:
        preds_178 = [all_preds[m]["eval_v2"][r["id"]] for r in non_overlap_recs]
        tgts_178 = [r["target"]["choice_id"] for r in non_overlap_recs]
        m178 = compute_metrics(preds_178, tgts_178, temperature=1.0)
        both_178 = sum(1 for gid, recs in diff_178_groups.items() if all_preds[m]["eval_v2"][recs[0]["id"]]["is_correct"] and all_preds[m]["eval_v2"][recs[1]["id"]]["is_correct"])
        same_178 = sum(1 for gid, recs in diff_178_groups.items() if all_preds[m]["eval_v2"][recs[0]["id"]]["best_candidate_id"] == all_preds[m]["eval_v2"][recs[1]["id"]]["best_candidate_id"])
        comparison_summary["auxiliary_178_cases"][m] = {
            "accuracy": f"{m178['correct_count']}/{m178['count']} ({m178['accuracy']*100:.1f}%)",
            "mean_nll": m178["mean_nll"],
            "mean_brier": m178["mean_brier"],
            "diff_target_39_both_correct": f"{both_178}/{len(diff_178_groups)}",
            "diff_target_39_pred_same": same_178,
        }

    # Save summary
    summary_path = out_dir / "comparisons_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(comparison_summary, f, indent=2, ensure_ascii=False)

    print(f"\nSaved comparisons summary to {summary_path}")

    # Clean print summary
    print("\n=======================================================")
    print("=== ERABI M3.5 COMPARISON SUMMARY (W_v2_gradfix vs W_v2_ce10) ===")
    print("=======================================================")
    for ds_name in datasets:
        dname = ds_name[0]
        print(f"\n--- Dataset: {dname} ---")
        for m in ["W_v2_gradfix", "W_v2_ce10"]:
            info = comparison_summary["datasets"][dname][m]
            print(f"  {m:14s} | Acc: {info['accuracy']:18s} | NLL: {info['mean_nll']:<6.4f} | Brier: {info['mean_brier']:<6.4f}")

    print("\n--- eval_v2 Pair Metrics (Diff-Target 47 Pairs) ---")
    for m in ["W_v2_gradfix", "W_v2_ce10"]:
        d = comparison_summary["eval_v2_detailed_pairs"]["diff_target_47"][m]
        print(f"  {m:14s} | Both: {d['both_correct']:2d}/47 ({d['both_correct']/47*100:4.1f}%) | Pred Same: {d['pred_same']:2d} | Pred Diff: {d['pred_diff']:2d}")

    print("\n--- eval_v2 Pair Metrics (Same-Target 53 Pairs) ---")
    for m in ["W_v2_gradfix", "W_v2_ce10"]:
        d = comparison_summary["eval_v2_detailed_pairs"]["same_target_53"][m]
        print(f"  {m:14s} | Both: {d['both_correct']:2d}/53 ({d['both_correct']/53*100:4.1f}%) | Pred Same: {d['pred_same']:2d} | Pred Diff: {d['pred_diff']:2d}")

    print("\n--- Task Breakdown on Diff-Target 47 Pairs ---")
    for fam in comparison_summary["eval_v2_detailed_pairs"]["task_family_diff_target"]:
        print(f"  [{fam}]")
        for m in ["W_v2_gradfix", "W_v2_ce10"]:
            d = comparison_summary["eval_v2_detailed_pairs"]["task_family_diff_target"][fam][m]
            print(f"    {m:14s} Both: {d['both_correct']}/{d['total_pairs']} | Same: {d['pred_same']} | Diff: {d['pred_diff']}")


if __name__ == "__main__":
    main()
