"""Standardized comparison script for ERABI M3.3.

Compares 3 models:
1. B0: knowledgator/gliclass-instruct-base-v1.0 (unfine-tuned base)
2. W_fix: runs/m3_2_label_fix/trained/checkpoint (M3.2 repaired label model)
3. W_v2: runs/m3_3_v2/trained/checkpoint (M3.3 rebuilt dataset model)

Evaluated on:
1. data/m3_3_v2/eval_v2.jsonl (200 cases / 100 pairs)
2. examples/smoke_cases.jsonl (12 cases)
3. data/m3_1/transfer_probe.jsonl (32 cases)

Also runs audit shortcut heuristics on eval_v2 to show shortcut breakdown.
Outputs to runs/m3_3_v2/comparisons/
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from erabi.evaluate import compute_metrics
from erabi.inference import GLiClassEngine
from erabi.schema import ChoiceRequest


def evaluate_engine_on_file(engine: GLiClassEngine, filepath: Path) -> Dict[str, Any]:
    with open(filepath, "r", encoding="utf-8") as f:
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
            "rule_kind": rec.get("rule_kind", ""),
            "choices": [{"id": co.id, "probability": co.probability} for co in resp.choices],
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
            "rule_kind": p["rule_kind"],
        }
        for p in predictions
    ]

    metrics = compute_metrics(predictions, targets, metadata=metadata, temperature=1.0)
    metrics["latency_total_sec"] = round(elapsed, 2)

    # Detailed pair metrics (diff target vs same target)
    groups = defaultdict(list)
    for p in predictions:
        groups[p["group_id"]].append(p)

    all_pairs = len(groups)
    all_both = 0
    diff_pairs = 0
    diff_both = 0
    same_pairs = 0
    same_both = 0

    for gid, plist in groups.items():
        if len(plist) == 2:
            both = (plist[0]["is_correct"] and plist[1]["is_correct"])
            if both:
                all_both += 1
            if plist[0]["target"] != plist[1]["target"]:
                diff_pairs += 1
                if both:
                    diff_both += 1
            else:
                same_pairs += 1
                if both:
                    same_both += 1

    metrics["pair_breakdown"] = {
        "all_pairs": f"{all_both}/{all_pairs} ({all_both/max(all_pairs,1)*100:.1f}%)",
        "diff_target_pairs": f"{diff_both}/{diff_pairs} ({diff_both/max(diff_pairs,1)*100:.1f}%)",
        "same_target_pairs": f"{same_both}/{same_pairs} ({same_both/max(same_pairs,1)*100:.1f}%)",
    }

    return {
        "metrics": metrics,
        "predictions": predictions,
    }


def evaluate_shortcuts_on_eval_v2(filepath: Path) -> Dict[str, Any]:
    with open(filepath, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f]

    # 1. Boundary keyword shortcut
    bound_cases = [r for r in records if r.get("rule_kind") == "boundary"]
    kw_correct = 0
    for r in bound_cases:
        pred = "pass" if "以下" in r["question"] else "fail"
        if pred == r["target"]["choice_id"]:
            kw_correct += 1

    # 2. Second attribute shortcut on goal following
    gf_cases = [r for r in records if r.get("task_family") == "goal_following"]
    attr2_correct = 0
    for r in gf_cases:
        ctx = r["context"]
        matches = re.findall(r"([^\s、]+)は(\d+)([^\d]+)で(\d+)([^\d、]+)", ctx)
        if len(matches) == 3:
            c_map = {c["text"]: c["id"] for c in r["choices"]}
            items = {m[0]: (int(m[1]), int(m[3])) for m in matches}
            min_v2_name = min(items.keys(), key=lambda k: items[k][1])
            pred_id = c_map.get(min_v2_name)
            if pred_id == r["target"]["choice_id"]:
                attr2_correct += 1

    return {
        "boundary_keyword_shortcut": f"{kw_correct}/{len(bound_cases)} ({kw_correct/max(len(bound_cases),1)*100:.1f}%)",
        "attr2_shortcut_on_goal_following": f"{attr2_correct}/{len(gf_cases)} ({attr2_correct/max(len(gf_cases),1)*100:.1f}%)",
    }


def main():
    out_dir = ROOT_DIR / "runs" / "m3_3_v2" / "comparisons"
    out_dir.mkdir(parents=True, exist_ok=True)

    models = [
        ("B0", "knowledgator/gliclass-instruct-base-v1.0"),
        ("W_fix", str(ROOT_DIR / "runs" / "m3_2_label_fix" / "trained" / "checkpoint")),
        ("W_v2", str(ROOT_DIR / "runs" / "m3_3_v2" / "trained" / "checkpoint")),
    ]

    datasets = [
        ("eval_v2", ROOT_DIR / "data" / "m3_3_v2" / "eval_v2.jsonl"),
        ("smoke_cases", ROOT_DIR / "examples" / "smoke_cases.jsonl"),
        ("transfer_probe", ROOT_DIR / "data" / "m3_1" / "transfer_probe.jsonl"),
    ]

    # Evaluate shortcuts on eval_v2
    shortcut_results = evaluate_shortcuts_on_eval_v2(ROOT_DIR / "data" / "m3_3_v2" / "eval_v2.jsonl")
    print("\n=== Audit Shortcut Heuristics on eval_v2 ===")
    print(f"Boundary keyword shortcut: {shortcut_results['boundary_keyword_shortcut']} (was 100% in old)")
    print(f"Attr2 shortcut on GF:     {shortcut_results['attr2_shortcut_on_goal_following']} (was 100% in old)")

    all_results = {}

    for mname, mpath in models:
        print(f"\n==========================================")
        print(f"Loading Model: {mname} ({mpath})")
        print(f"==========================================")
        engine = GLiClassEngine(model_id=mpath)
        all_results[mname] = {}

        for ds_name, ds_path in datasets:
            print(f"Evaluating {mname} on {ds_name}...")
            res = evaluate_engine_on_file(engine, ds_path)
            all_results[mname][ds_name] = res["metrics"]

            # Save detailed per-model predictions
            pred_file = out_dir / f"{mname}_{ds_name}_predictions.jsonl"
            with open(pred_file, "w", encoding="utf-8") as f:
                for p in res["predictions"]:
                    f.write(json.dumps(p, ensure_ascii=False) + "\n")

    # Build summary comparison matrix
    summary = {
        "models": ["B0", "W_fix", "W_v2"],
        "eval_v2_shortcut_heuristics": shortcut_results,
        "datasets": {},
    }

    for ds_name, _ in datasets:
        summary["datasets"][ds_name] = {}
        for mname, _ in models:
            m = all_results[mname][ds_name]
            entry = {
                "accuracy": f"{m['correct_count']}/{m['count']} ({m['accuracy']*100:.1f}%)",
                "mean_nll": m["mean_nll"],
                "mean_brier": m["mean_brier"],
            }
            if "pair_breakdown" in m:
                entry["pair_breakdown"] = m["pair_breakdown"]
            if "task_family_breakdown" in m:
                entry["task_family_breakdown"] = m["task_family_breakdown"]
            summary["datasets"][ds_name][mname] = entry

    # Detailed smoke breakdown for B0, W_fix, W_v2
    with open(ROOT_DIR / "examples" / "smoke_cases.jsonl", "r", encoding="utf-8") as f:
        smoke_cases = [json.loads(line) for line in f]

    smoke_preds = {}
    for mname, _ in models:
        pfile = out_dir / f"{mname}_smoke_cases_predictions.jsonl"
        with open(pfile, "r", encoding="utf-8") as f:
            smoke_preds[mname] = {p["id"]: p for p in [json.loads(line) for line in f]}

    smoke_rows = []
    for sc in smoke_cases:
        sid = sc["id"]
        tgt = sc["target"]["choice_id"]
        p_b0 = smoke_preds["B0"][sid]
        p_fix = smoke_preds["W_fix"][sid]
        p_v2 = smoke_preds["W_v2"][sid]

        smoke_rows.append({
            "id": sid,
            "question": sc["question"],
            "target": tgt,
            "B0": f"{p_b0['best_candidate_id']} ({'O' if p_b0['is_correct'] else 'X'})",
            "W_fix": f"{p_fix['best_candidate_id']} ({'O' if p_fix['is_correct'] else 'X'})",
            "W_v2": f"{p_v2['best_candidate_id']} ({'O' if p_v2['is_correct'] else 'X'})",
        })
    summary["smoke_case_breakdown"] = smoke_rows

    # Save summary
    summary_path = out_dir / "comparisons_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\nSaved comparisons summary to {summary_path}")

    # Print summary table
    print("\n=== M3.3 COMPARISON SUMMARY ===")
    for ds_name in summary["datasets"]:
        print(f"\n--- Dataset: {ds_name} ---")
        for mname in ["B0", "W_fix", "W_v2"]:
            info = summary["datasets"][ds_name][mname]
            pair_str = f" | Pairs: {info['pair_breakdown']['all_pairs']}" if 'pair_breakdown' in info else ""
            print(f"  {mname:6s} Acc: {info['accuracy']:18s} NLL: {info['mean_nll']:<6.4f} Brier: {info['mean_brier']:<6.4f}{pair_str}")


if __name__ == "__main__":
    main()
