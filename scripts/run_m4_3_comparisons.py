"""Comprehensive comparison script for M4.3-P Priority Phrasing Diversification.

Compares 3 models at strictly T=1.0:
1. W_v2_ce10 (M3 Baseline: runs/m3_5_ce10/trained/checkpoint)
2. W_m4_1 (M4.1 Experiment: runs/m4_1_exception/trained/checkpoint)
3. W_m4_3p (M4.3-P Experiment: runs/m4_3_phrasing/trained/checkpoint)

Across 8 evaluation datasets:
1. fresh_phrasing_eval (120 cases: Families M~P) - PRIMARY fresh capability
2. novel_priority_eval (120 cases: Families A~D) - Historical diagnostic
3. cell_b (40 cases: old domain + new phrasing)
4. cell_c (40 cases: new domain + old phrasing)
5. eval_exception (120 cases: M4.1 exception priority)
6. eval_v2 (200 cases: M3 synthetic rules)
7. transfer_probe (32 cases: transfer regression diagnostic)
8. smoke_cases (12 cases: general regression diagnostic)

Outputs to runs/m4_3_phrasing/comparisons/:
- Individual predictions for each model and dataset
- comparisons_summary.json
"""

from __future__ import annotations

import json
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

from erabi.inference import GLiClassEngine
from erabi.schema import ChoiceRequest

OUT_DIR = ROOT / "runs/m4_3_phrasing/comparisons"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODELS = {
    "W_v2_ce10": str(ROOT / "runs/m3_5_ce10/trained/checkpoint"),
    "W_m4_1": str(ROOT / "runs/m4_1_exception/trained/checkpoint"),
    "W_m4_3p": str(ROOT / "runs/m4_3_phrasing/trained/checkpoint"),
}

DATASETS = {
    "fresh_phrasing_eval": ROOT / "data/m4_3_phrasing/fresh_phrasing_eval.jsonl",
    "novel_priority_eval": ROOT / "data/m4_2_robustness/novel_priority_eval.jsonl",
    "cell_b_old_dom_new_phr": ROOT / "data/m4_2_1_diagnostic/cell_b_old_domain_new_phrasing.jsonl",
    "cell_c_new_dom_old_phr": ROOT / "data/m4_2_1_diagnostic/cell_c_new_domain_old_phrasing.jsonl",
    "eval_exception": ROOT / "data/m4_1_exception/eval_exception.jsonl",
    "eval_v2": ROOT / "data/m3_3_v2/eval_v2.jsonl",
    "transfer_probe": ROOT / "data/m3_1/transfer_probe.jsonl",
    "smoke_cases": ROOT / "examples/smoke_cases.jsonl",
}


def evaluate_dataset(engine: GLiClassEngine, dataset_path: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    records = [json.loads(line) for line in open(dataset_path, encoding="utf-8") if line.strip()]
    results = []
    total_nll = 0.0
    total_brier = 0.0
    correct_count = 0

    for row in records:
        req = ChoiceRequest.from_dict(row)
        tgt_cid = row["target"]["choice_id"]
        tgt_idx = next(i for i, c in enumerate(req.choices) if c.id == tgt_cid)

        resp = engine.predict(req, temperature=1.0, return_logits=True)
        raw_logits = resp.raw_logits
        pred_cid = resp.best_candidate_id
        is_corr = (pred_cid == tgt_cid)
        if is_corr:
            correct_count += 1

        probs = [c.probability for c in resp.choices]
        log_probs = F.log_softmax(torch.tensor(raw_logits, dtype=torch.float64), dim=-1)
        nll_val = -float(log_probs[tgt_idx].item())
        total_nll += nll_val

        brier_val = sum((p - (1.0 if i == tgt_idx else 0.0)) ** 2 for i, p in enumerate(probs))
        total_brier += brier_val

        results.append({
            "id": row.get("id"),
            "group_id": row.get("group_id"),
            "task_family": row.get("task_family"),
            "phrasing_family": row.get("phrasing_family"),
            "template_family": row.get("template_family"),
            "target": tgt_cid,
            "target_index": tgt_idx,
            "predicted": pred_cid,
            "is_correct": is_corr,
            "probabilities": probs,
            "raw_logits": raw_logits,
            "nll": nll_val,
            "brier": brier_val,
        })

    n = len(records)
    metrics: Dict[str, Any] = {
        "count": n,
        "correct_count": correct_count,
        "accuracy": correct_count / n,
        "mean_nll": total_nll / n,
        "mean_brier": total_brier / n,
    }

    # Pair metrics
    groups: Dict[str, List[int]] = {}
    for i, r in enumerate(results):
        gid = r.get("group_id")
        if gid:
            groups.setdefault(gid, []).append(i)

    paired_groups = {k: v for k, v in groups.items() if len(v) == 2}
    if paired_groups and dataset_path.name != "smoke_cases.jsonl":
        both_correct = 0
        diff_pairs = 0
        diff_both = 0
        diff_unswitched = 0
        diff_switched_wrong = 0
        same_pairs = 0
        same_both = 0

        for gid, indices in paired_groups.items():
            r1, r2 = results[indices[0]], results[indices[1]]
            is_both = r1["is_correct"] and r2["is_correct"]
            if is_both:
                both_correct += 1

            is_diff = (r1["target"] != r2["target"])
            if is_diff:
                diff_pairs += 1
                if is_both:
                    diff_both += 1
                else:
                    if r1["predicted"] == r2["predicted"]:
                        diff_unswitched += 1
                    else:
                        diff_switched_wrong += 1
            else:
                same_pairs += 1
                if is_both:
                    same_both += 1

        metrics["pair_stats"] = {
            "total_pairs": len(paired_groups),
            "both_correct": both_correct,
            "both_rate": both_correct / len(paired_groups),
            "diff_target_pairs": diff_pairs,
            "diff_target_both": diff_both,
            "diff_target_rate": (diff_both / diff_pairs) if diff_pairs > 0 else 0.0,
            "diff_unswitched": diff_unswitched,
            "diff_unswitched_rate": (diff_unswitched / diff_pairs) if diff_pairs > 0 else 0.0,
            "diff_switched_wrong": diff_switched_wrong,
            "diff_switched_wrong_rate": (diff_switched_wrong / diff_pairs) if diff_pairs > 0 else 0.0,
            "same_target_pairs": same_pairs,
            "same_target_both": same_both,
            "same_target_rate": (same_both / same_pairs) if same_pairs > 0 else 0.0,
        }
    else:
        metrics["pair_stats"] = None

    return results, metrics


def main():
    print("=" * 80)
    print("ERABI M4.3-P Comprehensive 3-Model Comparison (T=1.0)")
    print("=" * 80)

    summary: Dict[str, Dict[str, Any]] = {m: {} for m in MODELS}

    for model_name, model_path in MODELS.items():
        print(f"\n--- Loading and Evaluating Model: {model_name} ({model_path}) ---")
        engine = GLiClassEngine(model_id=model_path, device="cuda" if torch.cuda.is_available() else "cpu")

        for d_key, d_path in DATASETS.items():
            t0 = time.time()
            preds, m = evaluate_dataset(engine, d_path)
            summary[model_name][d_key] = m

            # Save predictions
            pred_file = OUT_DIR / f"{model_name}_{d_key}_predictions.jsonl"
            with open(pred_file, "w", encoding="utf-8") as f:
                for p in preds:
                    f.write(json.dumps(p, ensure_ascii=False) + "\n")

            p_str = ""
            if m["pair_stats"]:
                diff_b = m["pair_stats"]["diff_target_both"]
                diff_t = m["pair_stats"]["diff_target_pairs"]
                diff_r = m["pair_stats"]["diff_target_rate"] * 100
                p_str = f" | DiffBoth={diff_b:2d}/{diff_t:2d} ({diff_r:5.1f}%)"

            print(f"  {d_key:<24}: Acc={m['accuracy']*100:5.1f}% ({m['correct_count']:3d}/{m['count']:3d}){p_str} | NLL={m['mean_nll']:.4f} ({time.time()-t0:.1f}s)")

        del engine
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    with open(OUT_DIR / "comparisons_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 80)
    print("M4.3-P COMPARISON SUMMARY TABLE (T=1.0)")
    print("=" * 80)
    print(f"| {'Dataset':<24} | {'Metric':<18} | {'W_v2_ce10':<14} | {'W_m4_1':<14} | {'W_m4_3p':<14} |")
    print("|" + "-" * 26 + "|" + "-" * 20 + "|" + "-" * 16 + "|" + "-" * 16 + "|" + "-" * 16 + "|")

    for d_key in DATASETS:
        acc_v2 = f"{summary['W_v2_ce10'][d_key]['accuracy']*100:.1f}% ({summary['W_v2_ce10'][d_key]['correct_count']}/{summary['W_v2_ce10'][d_key]['count']})"
        acc_m41 = f"{summary['W_m4_1'][d_key]['accuracy']*100:.1f}% ({summary['W_m4_1'][d_key]['correct_count']}/{summary['W_m4_1'][d_key]['count']})"
        acc_m43 = f"{summary['W_m4_3p'][d_key]['accuracy']*100:.1f}% ({summary['W_m4_3p'][d_key]['correct_count']}/{summary['W_m4_3p'][d_key]['count']})"
        print(f"| {d_key:<24} | {'Accuracy':<18} | {acc_v2:<14} | {acc_m41:<14} | {acc_m43:<14} |")

        p_v2 = summary['W_v2_ce10'][d_key]['pair_stats']
        p_m41 = summary['W_m4_1'][d_key]['pair_stats']
        p_m43 = summary['W_m4_3p'][d_key]['pair_stats']

        if p_v2 and p_m41 and p_m43:
            db_v2 = f"{p_v2['diff_target_both']}/{p_v2['diff_target_pairs']} ({p_v2['diff_target_rate']*100:.1f}%)"
            db_m41 = f"{p_m41['diff_target_both']}/{p_m41['diff_target_pairs']} ({p_m41['diff_target_rate']*100:.1f}%)"
            db_m43 = f"{p_m43['diff_target_both']}/{p_m43['diff_target_pairs']} ({p_m43['diff_target_rate']*100:.1f}%)"
            print(f"| {'':<24} | {'Diff-Target Both':<18} | {db_v2:<14} | {db_m41:<14} | {db_m43:<14} |")

    print("=" * 80)


if __name__ == "__main__":
    main()
