"""Run standardized comparison across 3 models: B0, W_bad, W_fix.

Evaluation datasets:
1. data/m3_2_label_fix/holdout_corrected.jsonl (200 cases)
2. data/m3_2_label_fix/final_test_corrected.jsonl (200 cases)
3. examples/smoke_cases.jsonl (12 cases)
4. data/m3_1/transfer_probe.jsonl (32 cases)
5. data/m3_2_label_fix/counterfactual_probe.jsonl (24 cases)

Saves all detailed outputs to runs/m3_2_label_fix/comparisons/
"""

from __future__ import annotations

import json
import math
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

# Ensure src/ is in sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "src"))

from erabi.evaluate import compute_metrics
from erabi.inference import GLiClassEngine
from erabi.schema import ChoiceRequest


def evaluate_model_on_dataset(
    engine: GLiClassEngine,
    dataset_path: Path,
    dataset_name: str,
) -> Dict[str, Any]:
    with open(dataset_path, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f]

    predictions = []
    t0 = time.time()
    for rec in records:
        req = ChoiceRequest.from_dict(rec)
        resp = engine.predict(req, return_logits=True)
        pred_entry = {
            "id": rec["id"],
            "group_id": rec.get("group_id", ""),
            "task_family": rec.get("task_family", ""),
            "template_family": rec.get("template_family", ""),
            "context": rec.get("context", ""),
            "question": rec.get("question", ""),
            "choices": [
                {"id": co.id, "probability": co.probability}
                for co in resp.choices
            ],
            "best_candidate_id": resp.best_candidate_id,
            "target": rec["target"]["choice_id"],
            "raw_logits": resp.raw_logits,
            "is_correct": (resp.best_candidate_id == rec["target"]["choice_id"]),
        }
        predictions.append(pred_entry)
    elapsed = time.time() - t0

    targets = [p["target"] for p in predictions]
    metadata = [
        {
            "group_id": p["group_id"],
            "task_family": p["task_family"],
            "template_family": p["template_family"],
        }
        for p in predictions
    ]

    metrics = compute_metrics(predictions, targets, metadata, temperature=1.0)
    metrics["latency_total_sec"] = round(elapsed, 2)
    metrics["latency_per_sample_ms"] = round((elapsed / len(records)) * 1000, 2) if records else 0

    # Specific breakdowns for analysis
    server_cases = [p for p in predictions if "サーバー" in p.get("context", "")]
    if server_cases:
        s_targets = [p["target"] for p in server_cases]
        s_corr = sum(1 for p in server_cases if p["is_correct"])
        # server max cases (c1: asking for large capacity)
        s_max_cases = [p for p in server_cases if ("大容量" in p["question"] or "メモリ潤沢" in p["question"])]
        s_max_corr = sum(1 for p in s_max_cases if p["is_correct"])
        # non-server cases
        non_server_cases = [p for p in predictions if "サーバー" not in p.get("context", "")]
        ns_corr = sum(1 for p in non_server_cases if p["is_correct"])

        metrics["domain_breakdown"] = {
            "server_total": f"{s_corr}/{len(server_cases)}",
            "server_capacity_max": f"{s_max_corr}/{len(s_max_cases)}",
            "non_server": f"{ns_corr}/{len(non_server_cases)}",
        }

    return {
        "dataset": dataset_name,
        "metrics": metrics,
        "predictions": predictions,
    }


def main():
    comparisons_dir = root_dir / "runs" / "m3_2_label_fix" / "comparisons"
    comparisons_dir.mkdir(parents=True, exist_ok=True)

    models = [
        ("B0", "knowledgator/gliclass-instruct-base-v1.0"),
        ("W_bad", str(root_dir / "runs" / "m2_1" / "trained_instruct_base" / "checkpoint")),
        ("W_fix", str(root_dir / "runs" / "m3_2_label_fix" / "trained" / "checkpoint")),
    ]

    datasets = [
        ("holdout_corrected", root_dir / "data" / "m3_2_label_fix" / "holdout_corrected.jsonl"),
        ("final_test_corrected", root_dir / "data" / "m3_2_label_fix" / "final_test_corrected.jsonl"),
        ("smoke_cases", root_dir / "examples" / "smoke_cases.jsonl"),
        ("transfer_probe", root_dir / "data" / "m3_1" / "transfer_probe.jsonl"),
        ("counterfactual_probe", root_dir / "data" / "m3_2_label_fix" / "counterfactual_probe.jsonl"),
    ]

    all_results = {}

    for model_name, model_path in models:
        print(f"\n==========================================")
        print(f"Loading Model: {model_name} ({model_path})")
        print(f"==========================================")
        engine = GLiClassEngine(model_id=model_path)
        all_results[model_name] = {}

        for ds_name, ds_path in datasets:
            print(f"--> Evaluating {model_name} on {ds_name}...")
            res = evaluate_model_on_dataset(engine, ds_path, ds_name)
            all_results[model_name][ds_name] = res["metrics"]

            # Save detailed per-model per-dataset predictions
            pred_file = comparisons_dir / f"{model_name}_{ds_name}_predictions.jsonl"
            with open(pred_file, "w", encoding="utf-8") as f:
                for p in res["predictions"]:
                    f.write(json.dumps(p, ensure_ascii=False) + "\n")

    # Build summary comparison matrix
    summary_matrix = {
        "models": ["B0 (Base)", "W_bad (Old Mislabelled)", "W_fix (Repaired)"],
        "datasets": {},
    }

    for ds_name, _ in datasets:
        summary_matrix["datasets"][ds_name] = {}
        for mname, _ in models:
            m = all_results[mname][ds_name]
            entry = {
                "accuracy": f"{m['correct_count']}/{m['count']} ({m['accuracy']*100:.1f}%)",
                "mean_nll": m["mean_nll"],
                "mean_brier": m["mean_brier"],
            }
            if "pair_metrics" in m:
                entry["both_correct_pairs"] = f"{m['pair_metrics']['both_correct_pairs']}/{m['pair_metrics']['total_pairs']} ({m['pair_metrics']['both_correct_rate']*100:.1f}%)"
            if "domain_breakdown" in m:
                entry["server_capacity_max"] = m["domain_breakdown"]["server_capacity_max"]
                entry["non_server"] = m["domain_breakdown"]["non_server"]
            summary_matrix["datasets"][ds_name][mname] = entry

    # Detailed smoke breakdown
    smoke_preds = {}
    for mname, _ in models:
        pfile = comparisons_dir / f"{mname}_smoke_cases_predictions.jsonl"
        with open(pfile, "r", encoding="utf-8") as f:
            smoke_preds[mname] = {p["id"]: p["is_correct"] for p in [json.loads(line) for line in f]}

    smoke_breakdown = []
    with open(root_dir / "examples" / "smoke_cases.jsonl", "r", encoding="utf-8") as f:
        smoke_cases = [json.loads(line) for line in f]

    for sc in smoke_cases:
        sid = sc["id"]
        smoke_breakdown.append({
            "id": sid,
            "question": sc["question"],
            "target": sc["target"]["choice_id"],
            "B0_correct": smoke_preds["B0"].get(sid),
            "W_bad_correct": smoke_preds["W_bad"].get(sid),
            "W_fix_correct": smoke_preds["W_fix"].get(sid),
        })
    summary_matrix["smoke_case_breakdown"] = smoke_breakdown

    # Save summary
    summary_path = comparisons_dir / "comparisons_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_matrix, f, ensure_ascii=False, indent=2)
    print(f"\nSaved comparisons summary to {summary_path}")

    print("\n=== COMPARISON SUMMARY TABLE ===")
    for ds_name in summary_matrix["datasets"]:
        print(f"\n--- Dataset: {ds_name} ---")
        for mname in ["B0", "W_bad", "W_fix"]:
            info = summary_matrix["datasets"][ds_name][mname]
            extra = f", Pair: {info.get('both_correct_pairs', 'N/A')}" if 'both_correct_pairs' in info else ""
            if "server_capacity_max" in info:
                extra += f", SrvMax: {info['server_capacity_max']}"
            print(f"  {mname:6s} Acc: {info['accuracy']:18s} NLL: {info['mean_nll']:<6.4f} Brier: {info['mean_brier']:<6.4f}{extra}")


if __name__ == "__main__":
    main()
