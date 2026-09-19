"""Comprehensive 4-Model Comparison Script for ERABI M4.3.1 Semantic Repair.

Compares 4 models at strictly T=1.0:
1. W_v2_ce10 (M3 Baseline: runs/m3_5_ce10/trained/checkpoint)
2. W_m4_1 (M4.1 Experiment: runs/m4_1_exception/trained/checkpoint)
3. W_m4_3p (M4.3-P Prior Experiment: runs/m4_3_phrasing/trained/checkpoint)
4. W_m4_3p_fix (M4.3.1 Repaired Experiment: runs/m4_3_1_phrasing_fix/trained/checkpoint)

Across 9 evaluation datasets:
1. fresh_phrasing_eval_fix (120 cases: Families M~P, data/m4_3_1_phrasing_fix/fresh_phrasing_eval.jsonl)
2. cell_a_fix (40 cases: old domain + old phrasing, diagnostic_fix/cell_a_old_domain_old_phrasing.jsonl)
3. cell_b_fix (40 cases: old domain + new phrasing, diagnostic_fix/cell_b_old_domain_new_phrasing.jsonl)
4. novel_priority_eval (120 cases: Families A~D, data/m4_2_robustness/novel_priority_eval.jsonl)
5. cell_c (40 cases: new domain + old phrasing, data/m4_2_1_diagnostic/cell_c_new_domain_old_phrasing.jsonl)
6. eval_exception (120 cases: M4.1 exception priority, data/m4_1_exception/eval_exception.jsonl)
7. eval_v2 (200 cases: M3 synthetic rules, data/m3_3_v2/eval_v2.jsonl)
8. transfer_probe (32 cases: transfer regression diagnostic, data/m3_1/transfer_probe.jsonl)
9. smoke_cases (12 cases: general regression diagnostic, examples/smoke_cases.jsonl)

Detailed Breakdowns on fresh_phrasing_eval_fix:
- Diff Both / Same Both
- Family M, N, O, P
- Domain breakdowns (especially game_action and facility_control)
- Old-domain-only vs New-domain-only subsets

Outputs to runs/m4_3_1_phrasing_fix/comparisons/:
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

OUT_DIR = ROOT / "runs/m4_3_1_phrasing_fix/comparisons"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODELS = {
    "W_v2_ce10": str(ROOT / "runs/m3_5_ce10/trained/checkpoint"),
    "W_m4_1": str(ROOT / "runs/m4_1_exception/trained/checkpoint"),
    "W_m4_3p": str(ROOT / "runs/m4_3_phrasing/trained/checkpoint"),
    "W_m4_3p_fix": str(ROOT / "runs/m4_3_1_phrasing_fix/trained/checkpoint"),
}

DATASETS = {
    "fresh_phrasing_eval_fix": ROOT / "data/m4_3_1_phrasing_fix/fresh_phrasing_eval.jsonl",
    "cell_a_fix": ROOT / "data/m4_3_1_phrasing_fix/diagnostic_fix/cell_a_old_domain_old_phrasing.jsonl",
    "cell_b_fix": ROOT / "data/m4_3_1_phrasing_fix/diagnostic_fix/cell_b_old_domain_new_phrasing.jsonl",
    "novel_priority_eval": ROOT / "data/m4_2_robustness/novel_priority_eval.jsonl",
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
            "domain_class": row.get("domain_class"),
            "stratum": row.get("stratum"),
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

    diff_pairs = 0
    diff_both = 0
    diff_one = 0
    diff_zero = 0
    diff_switched_wrong = 0
    diff_no_switch = 0

    same_pairs = 0
    same_both = 0
    same_one = 0
    same_zero = 0

    for gid, idxs in groups.items():
        if len(idxs) == 2:
            r1, r2 = results[idxs[0]], results[idxs[1]]
            is_diff = (r1["target"] != r2["target"])
            n_corr = (1 if r1["is_correct"] else 0) + (1 if r2["is_correct"] else 0)
            pred_switched = (r1["predicted"] != r2["predicted"])

            if is_diff:
                diff_pairs += 1
                if n_corr == 2:
                    diff_both += 1
                elif n_corr == 1:
                    diff_one += 1
                else:
                    diff_zero += 1
                    if pred_switched:
                        diff_switched_wrong += 1
                    else:
                        diff_no_switch += 1
            else:
                same_pairs += 1
                if n_corr == 2:
                    same_both += 1
                elif n_corr == 1:
                    same_one += 1
                else:
                    same_zero += 1

    if diff_pairs > 0 or same_pairs > 0:
        metrics["pairs"] = {
            "total_groups": len(groups),
            "diff_pairs": diff_pairs,
            "diff_both": diff_both,
            "diff_both_rate": (diff_both / diff_pairs) if diff_pairs > 0 else 0.0,
            "diff_one": diff_one,
            "diff_zero": diff_zero,
            "diff_switched_wrong": diff_switched_wrong,
            "diff_no_switch": diff_no_switch,
            "same_pairs": same_pairs,
            "same_both": same_both,
            "same_both_rate": (same_both / same_pairs) if same_pairs > 0 else 0.0,
            "same_one": same_one,
            "same_zero": same_zero,
        }

    return results, metrics


def compute_fresh_breakdowns(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute detailed subsets for fresh phrasing eval."""
    breakdowns = {}

    # 1. By Family (M, N, O, P)
    fams = ["family_M", "family_N", "family_O", "family_P"]
    fam_stats = {}
    for f in fams:
        subset = [r for r in results if r.get("phrasing_family") == f]
        if subset:
            corr = sum(1 for r in subset if r["is_correct"])
            # pairs
            g_map: Dict[str, List[Dict[str, Any]]] = {}
            for r in subset:
                g_map.setdefault(r["group_id"], []).append(r)
            diff_both = 0
            diff_total = 0
            same_both = 0
            same_total = 0
            for g, pair in g_map.items():
                if len(pair) == 2:
                    is_both = pair[0]["is_correct"] and pair[1]["is_correct"]
                    if pair[0]["target"] != pair[1]["target"]:
                        diff_total += 1
                        if is_both:
                            diff_both += 1
                    else:
                        same_total += 1
                        if is_both:
                            same_both += 1
            fam_stats[f] = {
                "count": len(subset),
                "accuracy": corr / len(subset),
                "diff_both": diff_both,
                "diff_total": diff_total,
                "diff_both_rate": (diff_both / diff_total) if diff_total > 0 else 0.0,
                "same_both": same_both,
                "same_total": same_total,
            }
    breakdowns["by_family"] = fam_stats

    # 2. By Domain Class (Old vs New)
    old_subset = [r for r in results if r.get("domain_class") == "old"]
    new_subset = [r for r in results if r.get("domain_class") == "new"]

    def _subset_pair_stats(sub: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not sub:
            return {"count": 0, "accuracy": 0.0, "diff_both": 0, "diff_total": 0, "diff_both_rate": 0.0}
        corr = sum(1 for r in sub if r["is_correct"])
        g_map: Dict[str, List[Dict[str, Any]]] = {}
        for r in sub:
            g_map.setdefault(r["group_id"], []).append(r)
        d_both, d_tot = 0, 0
        s_both, s_tot = 0, 0
        for g, pair in g_map.items():
            if len(pair) == 2:
                is_both = pair[0]["is_correct"] and pair[1]["is_correct"]
                if pair[0]["target"] != pair[1]["target"]:
                    d_tot += 1
                    if is_both:
                        d_both += 1
                else:
                    s_tot += 1
                    if is_both:
                        s_both += 1
        return {
            "count": len(sub),
            "accuracy": corr / len(sub),
            "diff_both": d_both,
            "diff_total": d_tot,
            "diff_both_rate": (d_both / d_tot) if d_tot > 0 else 0.0,
            "same_both": s_both,
            "same_total": s_tot,
            "same_both_rate": (s_both / s_tot) if s_tot > 0 else 0.0,
        }

    breakdowns["old_domain_subset"] = _subset_pair_stats(old_subset)
    breakdowns["new_domain_subset"] = _subset_pair_stats(new_subset)

    # 3. Game action & Facility control specific
    game_sub = [r for r in results if r.get("template_family") == "game_action"]
    fac_sub = [r for r in results if r.get("template_family") == "facility_control"]
    breakdowns["game_action"] = _subset_pair_stats(game_sub)
    breakdowns["facility_control"] = _subset_pair_stats(fac_sub)

    return breakdowns


def main():
    print("=== Running Comprehensive 4-Model Comparison (M4.3.1 Repaired) ===")
    t0_all = time.time()
    all_summaries: Dict[str, Dict[str, Any]] = {}

    for model_name, model_path in MODELS.items():
        print(f"\n[{time.strftime('%H:%M:%S')}] Loading model: {model_name} from {model_path}...")
        if not Path(model_path).exists():
            print(f"WARNING: Model path does not exist: {model_path}. Skipping.")
            continue

        engine = GLiClassEngine(model_id=model_path, device="cuda" if torch.cuda.is_available() else "cpu")
        model_summary: Dict[str, Any] = {}

        for ds_name, ds_path in DATASETS.items():
            if not ds_path.exists():
                print(f"  Skipping missing dataset: {ds_name} ({ds_path})")
                continue

            t0_ds = time.time()
            results, metrics = evaluate_dataset(engine, ds_path)
            duration = time.time() - t0_ds

            # Detailed breakdowns for fresh eval
            if ds_name == "fresh_phrasing_eval_fix":
                metrics["breakdowns"] = compute_fresh_breakdowns(results)

            model_summary[ds_name] = metrics

            # Save individual predictions
            pred_file = OUT_DIR / f"{model_name}_{ds_name}_predictions.json"
            with open(pred_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            pair_info = ""
            if "pairs" in metrics:
                p = metrics["pairs"]
                pair_info = f" | Diff Both: {p['diff_both']}/{p['diff_pairs']} ({p['diff_both_rate']*100:.1f}%)"

            print(
                f"  [{model_name}] {ds_name:24s} | Acc: {metrics['accuracy']*100:5.1f}% "
                f"({metrics['correct_count']:3d}/{metrics['count']:3d}){pair_info} | "
                f"NLL: {metrics['mean_nll']:.4f} | {duration:.2f}s"
            )

        all_summaries[model_name] = model_summary
        del engine
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    total_duration = time.time() - t0_all
    print(f"\nAll evaluations finished in {total_duration:.1f}s.")

    # Save summary
    summary_path = OUT_DIR / "comparisons_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(all_summaries, f, indent=2, ensure_ascii=False)
    print(f"Summary written to {summary_path}")


if __name__ == "__main__":
    main()
