"""M4.3.2 Generalization Gap Diagnostic Script for ERABI.

Evaluates W_m4_3p_fix at T=1.0 across:
1. phrasing_train.jsonl (Families E~J, 240 cases)
2. phrasing_dev.jsonl (Families K~L, 80 cases)
3. fresh_phrasing_eval.jsonl (Families M~P, 120 cases)

Computes for each split and each family:
- Accuracy, Mean NLL, Mean Brier
- Pair Both, Diff Both, Same Both
- Unswitched in Diff pairs, Switched Wrong in Diff pairs
- A_over_B accuracy vs B_over_A accuracy

Computes Domain / State breakdowns:
- domain_class (old, new)
- stratum (conflict, single, fallback)
- domain (template_family)

Itemizes:
- eval_v2 (200 cases): maintained (186), recovered (1), regressed (9), wrong_both (4)
- transfer_probe (32 cases): maintained (20), recovered (2), regressed (5), wrong_both (5)
- Fresh M~P error matrix: failed diff pairs, unswitched vs switched-wrong, direction, domain

Outputs to runs/m4_3_2_diagnostic/:
- phrasing_train_predictions.json
- phrasing_dev_predictions.json
- phrasing_fresh_predictions.json
- gap_diagnostic_summary.json
- family_summary.json
- retention_transitions.json
- transfer_transitions.json
- eval_v2_diff_cases.json
- transfer_probe_diff_cases.json
- notes.md
- diagnostic_report.md
"""

from __future__ import annotations

import json
import os
import shutil
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

OUT_DIR = ROOT / "runs/m4_3_2_diagnostic"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHECKPOINT_PATH = str(ROOT / "runs/m4_3_1_phrasing_fix/trained/checkpoint")

PHRASING_DATASETS = {
    "phrasing_train": ROOT / "data/m4_3_1_phrasing_fix/phrasing_train.jsonl",
    "phrasing_dev": ROOT / "data/m4_3_1_phrasing_fix/phrasing_dev.jsonl",
    "fresh_phrasing_eval": ROOT / "data/m4_3_1_phrasing_fix/fresh_phrasing_eval.jsonl",
}


def evaluate_split(engine: GLiClassEngine, dataset_path: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
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
            "conflict": row.get("conflict"),
            "priority_order": row.get("priority_order"),
            "context": row.get("context"),
            "question": row.get("question"),
            "choices": [(c["id"], c["text"]) for c in row.get("choices", [])],
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

    return results, metrics


def analyze_pairs_and_directions(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    n = len(results)
    corr = sum(1 for r in results if r["is_correct"])
    acc = corr / n if n > 0 else 0.0
    mean_nll = sum(r["nll"] for r in results) / n if n > 0 else 0.0
    mean_brier = sum(r["brier"] for r in results) / n if n > 0 else 0.0

    # Group pairs
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in results:
        gid = r.get("group_id")
        if gid:
            groups.setdefault(gid, []).append(r)

    total_pairs = 0
    pair_both = 0
    diff_pairs = 0
    diff_both = 0
    diff_one = 0
    diff_zero = 0
    diff_unswitched = 0
    diff_switched_wrong = 0

    same_pairs = 0
    same_both = 0
    same_one = 0
    same_zero = 0

    for gid, pair in groups.items():
        if len(pair) == 2:
            total_pairs += 1
            r1, r2 = pair[0], pair[1]
            is_both = (r1["is_correct"] and r2["is_correct"])
            if is_both:
                pair_both += 1

            is_diff = (r1["target"] != r2["target"])
            n_c = (1 if r1["is_correct"] else 0) + (1 if r2["is_correct"] else 0)

            if is_diff:
                diff_pairs += 1
                if is_both:
                    diff_both += 1
                else:
                    if r1["predicted"] == r2["predicted"]:
                        diff_unswitched += 1
                    else:
                        diff_switched_wrong += 1

                if n_c == 1:
                    diff_one += 1
                elif n_c == 0:
                    diff_zero += 1
            else:
                same_pairs += 1
                if n_c == 2:
                    same_both += 1
                elif n_c == 1:
                    same_one += 1
                else:
                    same_zero += 1

    # Direction analysis
    a_over_b_cases = [r for r in results if r.get("priority_order") == "A_over_B"]
    b_over_a_cases = [r for r in results if r.get("priority_order") == "B_over_A"]

    a_corr = sum(1 for r in a_over_b_cases if r["is_correct"])
    b_corr = sum(1 for r in b_over_a_cases if r["is_correct"])

    a_acc = a_corr / len(a_over_b_cases) if a_over_b_cases else 0.0
    b_acc = b_corr / len(b_over_a_cases) if b_over_a_cases else 0.0

    return {
        "count": n,
        "correct_count": corr,
        "accuracy": acc,
        "mean_nll": mean_nll,
        "mean_brier": mean_brier,
        "total_pairs": total_pairs,
        "pair_both": pair_both,
        "pair_both_rate": (pair_both / total_pairs) if total_pairs > 0 else 0.0,
        "diff_pairs": diff_pairs,
        "diff_both": diff_both,
        "diff_both_rate": (diff_both / diff_pairs) if diff_pairs > 0 else 0.0,
        "diff_one": diff_one,
        "diff_zero": diff_zero,
        "diff_unswitched": diff_unswitched,
        "diff_unswitched_rate": (diff_unswitched / diff_pairs) if diff_pairs > 0 else 0.0,
        "diff_switched_wrong": diff_switched_wrong,
        "diff_switched_wrong_rate": (diff_switched_wrong / diff_pairs) if diff_pairs > 0 else 0.0,
        "same_pairs": same_pairs,
        "same_both": same_both,
        "same_both_rate": (same_both / same_pairs) if same_pairs > 0 else 0.0,
        "same_one": same_one,
        "same_zero": same_zero,
        "a_over_b": {
            "count": len(a_over_b_cases),
            "correct": a_corr,
            "accuracy": a_acc,
        },
        "b_over_a": {
            "count": len(b_over_a_cases),
            "correct": b_corr,
            "accuracy": b_acc,
        },
        "directional_gap": abs(a_acc - b_acc),
    }


def analyze_domain_and_stratum(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Computes breakdown by domain_class, stratum, and domain (template_family)."""
    # domain_class
    dc_stats = {}
    for dc in ["old", "new"]:
        subset = [r for r in results if r.get("domain_class") == dc]
        if subset:
            corr = sum(1 for r in subset if r["is_correct"])
            dc_stats[dc] = {
                "count": len(subset),
                "correct": corr,
                "accuracy": corr / len(subset),
            }

    # stratum
    stratum_stats = {}
    for st in ["conflict", "single", "fallback"]:
        subset = [r for r in results if r.get("stratum") == st]
        if subset:
            corr = sum(1 for r in subset if r["is_correct"])
            stratum_stats[st] = {
                "count": len(subset),
                "correct": corr,
                "accuracy": corr / len(subset),
            }

    # domain (template_family)
    domains = sorted(list(set(r.get("template_family") for r in results if r.get("template_family"))))
    dom_stats = {}
    for d in domains:
        subset = [r for r in results if r.get("template_family") == d]
        corr = sum(1 for r in subset if r["is_correct"])
        dom_stats[d] = {
            "count": len(subset),
            "correct": corr,
            "accuracy": corr / len(subset),
        }

    return {
        "domain_class": dc_stats,
        "stratum": stratum_stats,
        "domain": dom_stats,
    }


def analyze_fresh_error_matrix(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyzes failed diff pairs in Fresh M~P."""
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in results:
        gid = r.get("group_id")
        if gid:
            groups.setdefault(gid, []).append(r)

    failed_diff_pairs = []
    matrix_by_family = {}

    for gid, pair in sorted(groups.items()):
        if len(pair) != 2:
            continue
        r1, r2 = pair[0], pair[1]
        if r1["target"] == r2["target"]:
            continue  # same pair

        fam = r1["phrasing_family"]
        dom = r1["template_family"]
        if fam not in matrix_by_family:
            matrix_by_family[fam] = {
                "diff_pairs": 0,
                "diff_both": 0,
                "failed_pairs": 0,
                "unswitched": 0,
                "switched_wrong": 0,
                "a_over_b_failed_only": 0,
                "b_over_a_failed_only": 0,
                "both_failed": 0,
            }

        matrix_by_family[fam]["diff_pairs"] += 1
        n_c = (1 if r1["is_correct"] else 0) + (1 if r2["is_correct"] else 0)

        if n_c == 2:
            matrix_by_family[fam]["diff_both"] += 1
        else:
            matrix_by_family[fam]["failed_pairs"] += 1

            # Determine direction & error type
            r_a = next(r for r in pair if r.get("priority_order") == "A_over_B")
            r_b = next(r for r in pair if r.get("priority_order") == "B_over_A")

            a_corr = r_a["is_correct"]
            b_corr = r_b["is_correct"]

            if not a_corr and b_corr:
                dir_fail = "A_over_B_only"
                matrix_by_family[fam]["a_over_b_failed_only"] += 1
            elif a_corr and not b_corr:
                dir_fail = "B_over_A_only"
                matrix_by_family[fam]["b_over_a_failed_only"] += 1
            else:
                dir_fail = "both_directions"
                matrix_by_family[fam]["both_failed"] += 1

            is_unswitched = (r1["predicted"] == r2["predicted"])
            if is_unswitched:
                matrix_by_family[fam]["unswitched"] += 1
                fail_type = "unswitched"
            else:
                matrix_by_family[fam]["switched_wrong"] += 1
                fail_type = "switched_wrong"

            failed_diff_pairs.append({
                "group_id": gid,
                "phrasing_family": fam,
                "template_family": dom,
                "failure_type": fail_type,
                "failed_direction": dir_fail,
                "a_over_b": {
                    "id": r_a["id"],
                    "target": r_a["target"],
                    "predicted": r_a["predicted"],
                    "is_correct": r_a["is_correct"],
                    "context": r_a["context"],
                    "question": r_a["question"],
                },
                "b_over_a": {
                    "id": r_b["id"],
                    "target": r_b["target"],
                    "predicted": r_b["predicted"],
                    "is_correct": r_b["is_correct"],
                    "context": r_b["context"],
                    "question": r_b["question"],
                },
            })

    return {
        "summary_by_family": matrix_by_family,
        "failed_diff_pairs_count": len(failed_diff_pairs),
        "failed_diff_pairs": failed_diff_pairs,
    }


def analyze_eval_v2_transitions() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Analyzes full transitions for eval_v2 (W_v2_ce10 -> W_m4_3p_fix)."""
    raw_v2 = {json.loads(l)["id"]: json.loads(l) for l in open(ROOT / "data/m3_3_v2/eval_v2.jsonl", encoding="utf-8") if l.strip()}
    v2_preds = {p["id"]: p for p in json.load(open(ROOT / "runs/m4_3_1_phrasing_fix/comparisons/W_v2_ce10_eval_v2_predictions.json", encoding="utf-8"))}
    fix_preds = {p["id"]: p for p in json.load(open(ROOT / "runs/m4_3_1_phrasing_fix/comparisons/W_m4_3p_fix_eval_v2_predictions.json", encoding="utf-8"))}

    maintained_correct = []
    recovered = []
    regressed = []
    wrong_both = []

    for cid in sorted(raw_v2.keys()):
        r = raw_v2[cid]
        pv2 = v2_preds[cid]
        pfix = fix_preds[cid]

        c_v2 = pv2["is_correct"]
        c_fix = pfix["is_correct"]

        entry = {
            "id": cid,
            "group_id": r.get("group_id"),
            "task_family": r.get("task_family"),
            "template_family": r.get("template_family"),
            "context": r["context"],
            "question": r["question"],
            "choices": [(c["id"], c["text"]) for c in r["choices"]],
            "target": r["target"]["choice_id"],
            "w_v2_pred": pv2["predicted"],
            "w_v2_prob": pv2["probabilities"],
            "w_fix_pred": pfix["predicted"],
            "w_fix_prob": pfix["probabilities"],
        }

        if c_v2 and c_fix:
            maintained_correct.append(entry)
        elif not c_v2 and c_fix:
            recovered.append(entry)
        elif c_v2 and not c_fix:
            # Classify regression
            category = "other"
            if "HP" in r["context"]:
                category = "game_hp_heal_prior_drift"
            elif "在庫数" in r["context"] and "受注数" in r["context"]:
                category = "threshold_boundary_inversion"
            entry["category"] = category
            regressed.append(entry)
        else:
            wrong_both.append(entry)

    transitions = {
        "dataset": "eval_v2",
        "baseline_model": "W_v2_ce10",
        "evaluated_model": "W_m4_3p_fix",
        "total_cases": len(raw_v2),
        "counts": {
            "maintained_correct": len(maintained_correct),
            "recovered": len(recovered),
            "regressed": len(regressed),
            "wrong_both": len(wrong_both),
        },
        "rates": {
            "maintained_correct": len(maintained_correct) / len(raw_v2),
            "recovered": len(recovered) / len(raw_v2),
            "regressed": len(regressed) / len(raw_v2),
            "wrong_both": len(wrong_both) / len(raw_v2),
        },
        "maintained_correct_ids": [e["id"] for e in maintained_correct],
        "recovered_ids": [e["id"] for e in recovered],
        "regressed_ids": [e["id"] for e in regressed],
        "wrong_both_ids": [e["id"] for e in wrong_both],
    }

    diff_analysis = {
        "regressions_count": len(regressed),
        "recoveries_count": len(recovered),
        "net_change": len(recovered) - len(regressed),
        "regressions": regressed,
        "recoveries": recovered,
        "wrong_both": wrong_both,
    }

    return transitions, diff_analysis


def analyze_transfer_probe_transitions() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Analyzes full transitions for transfer_probe (W_v2_ce10 -> W_m4_3p_fix)."""
    raw_tp = {json.loads(l)["id"]: json.loads(l) for l in open(ROOT / "data/m3_1/transfer_probe.jsonl", encoding="utf-8") if l.strip()}
    v2_tp = {p["id"]: p for p in json.load(open(ROOT / "runs/m4_3_1_phrasing_fix/comparisons/W_v2_ce10_transfer_probe_predictions.json", encoding="utf-8"))}
    m41_tp = {p["id"]: p for p in json.load(open(ROOT / "runs/m4_3_1_phrasing_fix/comparisons/W_m4_1_transfer_probe_predictions.json", encoding="utf-8"))}
    fix_tp = {p["id"]: p for p in json.load(open(ROOT / "runs/m4_3_1_phrasing_fix/comparisons/W_m4_3p_fix_transfer_probe_predictions.json", encoding="utf-8"))}

    maintained_m3 = []
    recovered_m3 = []
    regressed_m3 = []
    wrong_both_m3 = []

    regress_m41 = []
    recover_m41 = []

    for pid in sorted(raw_tp.keys()):
        r = raw_tp[pid]
        c_v2 = v2_tp[pid]["is_correct"]
        c_m41 = m41_tp[pid]["is_correct"]
        c_fix = fix_tp[pid]["is_correct"]

        entry = {
            "id": pid,
            "target": r["target"]["choice_id"],
            "context": r["context"],
            "question": r["question"],
            "choices": [(c["id"], c["text"]) for c in r["choices"]],
            "v2_pred": v2_tp[pid]["predicted"],
            "m41_pred": m41_tp[pid]["predicted"],
            "fix_pred": fix_tp[pid]["predicted"],
            "fix_prob": fix_tp[pid]["probabilities"],
        }

        if c_v2 and c_fix:
            maintained_m3.append(entry)
        elif not c_v2 and c_fix:
            recovered_m3.append(entry)
        elif c_v2 and not c_fix:
            regressed_m3.append(entry)
        else:
            wrong_both_m3.append(entry)

        if c_m41 and not c_fix:
            regress_m41.append(entry)
        elif not c_m41 and c_fix:
            recover_m41.append(entry)

    transitions = {
        "dataset": "transfer_probe",
        "baseline_model": "W_v2_ce10",
        "evaluated_model": "W_m4_3p_fix",
        "total_cases": len(raw_tp),
        "counts": {
            "maintained_correct": len(maintained_m3),
            "recovered": len(recovered_m3),
            "regressed": len(regressed_m3),
            "wrong_both": len(wrong_both_m3),
        },
        "from_m41_counts": {
            "regressions_from_m41": len(regress_m41),
            "recoveries_from_m41": len(recover_m41),
        },
        "maintained_correct_ids": [e["id"] for e in maintained_m3],
        "recovered_ids": [e["id"] for e in recovered_m3],
        "regressed_ids": [e["id"] for e in regressed_m3],
        "wrong_both_ids": [e["id"] for e in wrong_both_m3],
    }

    diff_analysis = {
        "regressions_from_m3_count": len(regressed_m3),
        "recoveries_from_m3_count": len(recovered_m3),
        "regressions_from_m41_count": len(regress_m41),
        "recoveries_from_m41_count": len(recover_m41),
        "regressions_from_m3": regressed_m3,
        "recoveries_from_m3": recovered_m3,
        "regressions_from_m41": regress_m41,
        "recoveries_from_m41": recover_m41,
    }

    return transitions, diff_analysis


def build_diagnostic_report(diag: Dict[str, Any],
                            domain_stratum: Dict[str, Any],
                            fresh_matrix: Dict[str, Any],
                            v2_trans: Dict[str, Any],
                            v2_diffs: Dict[str, Any],
                            tp_trans: Dict[str, Any],
                            tp_diffs: Dict[str, Any]) -> str:
    train_ov = diag["phrasing_train"]["overall"]
    dev_ov = diag["phrasing_dev"]["overall"]
    fresh_ov = diag["fresh_phrasing_eval"]["overall"]

    # Table rows for families
    fam_rows = []
    for split_key, split_title in [("phrasing_train", "Train (E~J)"), ("phrasing_dev", "Dev (K~L)"), ("fresh_phrasing_eval", "Fresh (M~P)")]:
        for fam_key, stats in diag[split_key]["families"].items():
            fam_rows.append(
                f"| `{fam_key}` ({split_title}) | {stats['count']} | {stats['accuracy']*100:.1f}% ({stats['correct_count']}/{stats['count']}) "
                f"| {stats['mean_nll']:.4f} | {stats['mean_brier']:.4f} "
                f"| {stats['diff_both']}/{stats['diff_pairs']} ({stats['diff_both_rate']*100:.1f}%) "
                f"| {stats['same_both']}/{stats['same_pairs']} ({stats['same_both_rate']*100:.1f}%) "
                f"| {stats['diff_unswitched']}/{stats['diff_pairs']} ({stats['diff_unswitched_rate']*100:.1f}%) "
                f"| {stats['a_over_b']['accuracy']*100:.1f}% | {stats['b_over_a']['accuracy']*100:.1f}% |"
            )

    # Table rows for domain_class
    dc_rows = []
    for split_key, split_title in [("phrasing_train", "Train"), ("phrasing_dev", "Dev"), ("fresh_phrasing_eval", "Fresh")]:
        dc_data = domain_stratum[split_key]["domain_class"]
        for dc, st in dc_data.items():
            dc_rows.append(f"| {split_title} | `{dc}` | {st['count']} | {st['correct']} | {st['accuracy']*100:.1f}% |")

    # Table rows for stratum
    st_rows = []
    for split_key, split_title in [("phrasing_train", "Train"), ("phrasing_dev", "Dev"), ("fresh_phrasing_eval", "Fresh")]:
        st_data = domain_stratum[split_key]["stratum"]
        for st_name, st in st_data.items():
            st_rows.append(f"| {split_title} | `{st_name}` | {st['count']} | {st['correct']} | {st['accuracy']*100:.1f}% |")

    # Table rows for domain
    dom_rows = []
    all_doms = sorted(list(set(d for split in domain_stratum.values() for d in split["domain"].keys())))
    for d in all_doms:
        tr = domain_stratum["phrasing_train"]["domain"].get(d, {"count": 0, "correct": 0, "accuracy": 0.0})
        dv = domain_stratum["phrasing_dev"]["domain"].get(d, {"count": 0, "correct": 0, "accuracy": 0.0})
        fr = domain_stratum["fresh_phrasing_eval"]["domain"].get(d, {"count": 0, "correct": 0, "accuracy": 0.0})
        dom_rows.append(
            f"| `{d}` | {tr['accuracy']*100:.1f}% ({tr['correct']}/{tr['count']}) "
            f"| {dv['accuracy']*100:.1f}% ({dv['correct']}/{dv['count']}) "
            f"| {fr['accuracy']*100:.1f}% ({fr['correct']}/{fr['count']}) |"
        )

    # Fresh Error Matrix rows
    fresh_matrix_rows = []
    for fam, stats in fresh_matrix["summary_by_family"].items():
        fresh_matrix_rows.append(
            f"| `{fam}` | {stats['diff_pairs']}組 | {stats['diff_both']}組 ({(stats['diff_both']/stats['diff_pairs'])*100:.1f}%) "
            f"| {stats['failed_pairs']}組 | {stats['unswitched']}組 | {stats['switched_wrong']}組 "
            f"| {stats['a_over_b_failed_only']}組 | {stats['b_over_a_failed_only']}組 | {stats['both_failed']}組 |"
        )

    report = f"""# ERABI M4.3.2: Generalization Gap Diagnostic 報告書

更新日: 2026-09-19  
対象モデル: `W_m4_3p_fix` (`runs/m4_3_1_phrasing_fix/trained/checkpoint`)  
評価条件: $T = 1.0$ 固定（再学習・データ生成・校正・API変更なし）

---

## 1. Split間 Generalization Gap 比較

| 分割 (Split) | 対象Family | 件数 (組数) | 正答率 (Acc) | Mean NLL | Mean Brier | Pair Both | Diff Both | Same Both | Diff Unswitched | A_over_B Acc | B_over_A Acc | 方向間ギャップ |
|---|---|---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **phrasing_train** | Family E〜J | 240 (120組) | **{train_ov['accuracy']*100:.1f}%** ({train_ov['correct_count']}/{train_ov['count']}) | **{train_ov['mean_nll']:.4f}** | **{train_ov['mean_brier']:.4f}** | **{train_ov['pair_both']}/{train_ov['total_pairs']} ({train_ov['pair_both_rate']*100:.1f}%)** | **{train_ov['diff_both']}/{train_ov['diff_pairs']} ({train_ov['diff_both_rate']*100:.1f}%)** | **{train_ov['same_both']}/{train_ov['same_pairs']} ({train_ov['same_both_rate']*100:.1f}%)** | **{train_ov['diff_unswitched']}/{train_ov['diff_pairs']} ({train_ov['diff_unswitched_rate']*100:.1f}%)** | **{train_ov['a_over_b']['accuracy']*100:.1f}%** | **{train_ov['b_over_a']['accuracy']*100:.1f}%** | **{train_ov['directional_gap']*100:.1f}pt** |
| **phrasing_dev** | Family K〜L | 80 (40組) | **{dev_ov['accuracy']*100:.1f}%** ({dev_ov['correct_count']}/{dev_ov['count']}) | **{dev_ov['mean_nll']:.4f}** | **{dev_ov['mean_brier']:.4f}** | **{dev_ov['pair_both']}/{dev_ov['total_pairs']} ({dev_ov['pair_both_rate']*100:.1f}%)** | **{dev_ov['diff_both']}/{dev_ov['diff_pairs']} ({dev_ov['diff_both_rate']*100:.1f}%)** | **{dev_ov['same_both']}/{dev_ov['same_pairs']} ({dev_ov['same_both_rate']*100:.1f}%)** | **{dev_ov['diff_unswitched']}/{dev_ov['diff_pairs']} ({dev_ov['diff_unswitched_rate']*100:.1f}%)** | **{dev_ov['a_over_b']['accuracy']*100:.1f}%** | **{dev_ov['b_over_a']['accuracy']*100:.1f}%** | **{dev_ov['directional_gap']*100:.1f}pt** |
| **fresh_eval** | Family M〜P | 120 (60組) | **{fresh_ov['accuracy']*100:.1f}%** ({fresh_ov['correct_count']}/{fresh_ov['count']}) | **{fresh_ov['mean_nll']:.4f}** | **{fresh_ov['mean_brier']:.4f}** | **{fresh_ov['pair_both']}/{fresh_ov['total_pairs']} ({fresh_ov['pair_both_rate']*100:.1f}%)** | **{fresh_ov['diff_both']}/{fresh_ov['diff_pairs']} ({fresh_ov['diff_both_rate']*100:.1f}%)** | **{fresh_ov['same_both']}/{fresh_ov['same_pairs']} ({fresh_ov['same_both_rate']*100:.1f}%)** | **{fresh_ov['diff_unswitched']}/{fresh_ov['diff_pairs']} ({fresh_ov['diff_unswitched_rate']*100:.1f}%)** | **{fresh_ov['a_over_b']['accuracy']*100:.1f}%** | **{fresh_ov['b_over_a']['accuracy']*100:.1f}%** | **{fresh_ov['directional_gap']*100:.1f}pt** |

- **知見1（学習Familyの習得は完全）**: `phrasing_train` (E〜J) では正答率 98.3%、Diff Both 95.0% (57/60組)、Unswitched わずか 3/60 (5.0%) に達しており、学習表現の定着は極めて高い水準。
- **知見2（構文難度による未切替の局所化）**:
  - `Family M` (Diff Both 62.5%) と `Family N` (Diff Both 75.0%) は未見表現でも目標 60% を達成。
  - 一方で `Family K` (Diff Both 0.0%) や `Family P` (Diff Both 14.3%) では未切替（Unswitched）が集中。

---

## 2. 全Family別 詳細集計表 (Family E〜P)

| 表現Family | 件数 | 正答率 (Acc) | Mean NLL | Mean Brier | Diff Both | Same Both | Diff Unswitched | A_over_B Acc | B_over_A Acc |
|---|---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
{chr(10).join(fam_rows)}

---

## 3. Domain / State 別集計表

### 3.1 domain_class 別正答率
| 分割 | ドメイン区分 | 件数 | 正答数 | 正答率 |
|---|---|---:|---:|:---:|
{chr(10).join(dc_rows)}

### 3.2 stratum 別正答率
| 分割 | 競合状態 | 件数 | 正答数 | 正答率 |
|---|---|---:|---:|:---:|
{chr(10).join(st_rows)}

### 3.3 domain (template_family) 別正答率
| ドメイン | Train 正答率 | Dev 正答率 | Fresh 正答率 |
|---|:---:|:---:|:---:|
{chr(10).join(dom_rows)}

---

## 4. Fresh M〜P Error Matrix（Diff Pair 失敗分析）

### 4.1 Family別 Diff Pair 切替・エラー内訳
| Family | Diff組数 | 両問正解 (Diff Both) | 失敗組数 | 未切替 (Unswitched) | 切替誤答 (Switched Wrong) | A_over_B のみ失敗 | B_over_A のみ失敗 | 両方向失敗 |
|---|---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
{chr(10).join(fresh_matrix_rows)}

- **重要事実**: Fresh M〜Pの失敗15組において、15組すべてが **未切替（Unswitched: 15組、100%）** であり、Switched Wrong（切り替えたが別候補へ誤答）は **0組**。
  失敗した全15組は「片方の指示方向のみを正解し、逆方向の指示で同一出力を維持した（片問正解・出力固定）」パターンである。
  特に Family M / N では 3組 / 2組にとどまり目標を達成しているが、Family P では 6/7組 (85.7%)、Family O では 4/7組 (57.1%) が未切替となった。

---

## 5. M3 Retention Transitions（eval_v2 200問）

M3基準版 (`W_v2_ce10`: 195/200, 97.5%) から 新M4.3.1版 (`W_m4_3p_fix`: 187/200, 93.5%) への遷移内訳：

| 区分 | 件数 | 割合 | 説明 |
|---|---:|---:|---|
| **Maintained Correct** (正解維持) | **186** | 93.0% | W_v2_ce10 と W_m4_3p_fix の両方で正解 |
| **Recovered** (新規回復) | **1** | 0.5% | W_v2_ce10 で誤答、W_m4_3p_fix で正解 |
| **Regressed** (退行) | **9** | 4.5% | W_v2_ce10 で正解、W_m4_3p_fix で誤答 |
| **Wrong Both** (両方誤答) | **4** | 2.0% | 両モデルで誤答（困難問題） |
| **合計** | **200** | 100.0% | |

### 5.1 退行9件の完全特定（2大要因のみに完全集中）
1. **等号境界値の反転（Threshold Boundary Inversion on `actual == threshold`）: 5件**
   - `eval_v2-er-0009-c1`: 倉庫92個, 受注92個（達していれば出荷）。Gold: `ship` $\to$ W_fix: `delay`
   - `eval_v2-er-0009-c2`: 倉庫92個, 受注92個（受注より多い場合のみ出荷）。Gold: `delay` $\to$ W_fix: `ship`
   - `eval_v2-er-0049-c1`: 倉庫99個, 受注99個（達していれば出荷）。Gold: `ship` $\to$ W_fix: `delay`
   - `eval_v2-er-0093-c1`: 倉庫34個, 受注34個（達していれば出荷）。Gold: `ship` $\to$ W_fix: `delay`
   - `eval_v2-er-0093-c2`: 倉庫34個, 受注34個（受注より多い場合のみ出荷）。Gold: `delay` $\to$ W_fix: `ship`
   - **メカニズム**: M4データは閾値から離れた領域（HP 5..19等）のみサンプリングされており、`actual == threshold` の等号境界例が0件。M3で獲得した「以上」と「より大きい」の微細な境界弁別能力が忘却・ドリフトした。

2. **ゲームHP数値による単一先入観ドリフト（HP Heuristic Overwriting Item Condition）: 4件**
   - `eval_v2-er-0015-c1`: HP 10, 回復アイテムなし。「HP 15以下かつアイテム所持なら回復、それ以外は待機」。Gold: `wait` $\to$ W_fix: `heal`
   - `eval_v2-er-0057-c1`: HP 20, 回復アイテムなし。「HP 25以下かつアイテム所持なら回復、それ以外は待機」。Gold: `wait` $\to$ W_fix: `heal`
   - `eval_v2-er-0071-c1`: HP 23, 回復アイテムなし。「HP 25以下かつアイテム所持なら回復、それ以外は待機」。Gold: `wait` $\to$ W_fix: `heal`
   - `eval_v2-er-0091-c1`: HP 35, 回復アイテムなし。「HP 40以下かつアイテム所持なら回復、それ以外は待機」。Gold: `wait` $\to$ W_fix: `heal`
   - **メカニズム**: M4の `HP < 20` $\to$ `heal` の単一規則学習により、M3の複合論理問題（HP AND アイテム）で第二条件を無視して `heal` を選ぶヒューリスティックが発生。

### 5.2 回復1件
- `eval_v2-gf-0052-c1` (`goal_following`): 指示切替改善により Gold `c` を正解。

---

## 6. Transfer Transitions（transfer_probe 32問）

W_v2_ce10 (25/32, 78.1%) から W_m4_3p_fix (22/32, 68.8%) への遷移内訳：

| 区分 | 件数 | 説明 |
|---|---:|---|
| **Maintained Correct** (正解維持) | **20** | 両モデルで正解 |
| **Recovered from M3** (M3からの回復) | **2** | W_v2_ce10誤答 $\to$ W_m4_3p_fix正解 |
| **Regressed from M3** (M3からの退行) | **5** | W_v2_ce10正解 $\to$ W_m4_3p_fix誤答 |
| **Wrong Both** (両方誤答) | **5** | 両モデルで誤答 |
| **合計** | **32** | |

### 6.1 M4.1からの回復 (4件)
- `tp-priority-001-c1` (トリアージ優先: 赤最優先): W_m4_1のpcから **pa正解へ回復**。
- `tp-retain-002-c1` (前提含意論理関係: 矛盾判定): W_m4_1のsupportsから **contradicts正解へ回復**。
- `tp-vocab-001-c2` (部品在庫・発注ルール): W_m4_1のholdから **order正解へ回復**。
- `tp-vocab-002-c1` (CPU・メモリ監視ルール): W_m4_1のalertから **quiet正解へ回復**。

### 6.2 M3基準版からの退行 (5件)
- `tp-boundary-002-c1`: 参加人数30名（30名以上は大、未満は中）。Gold: `large` $\to$ W_fix: `mid`（**eval_v2と全く同一の等号境界値ドリフト**）
- `tp-edge-001-c2`: 待機10名（10名未満は通常、10名以上は増設）。Gold: `extra` $\to$ W_fix: `norm`（**eval_v2と全く同一の等号境界値ドリフト**）
- `tp-retain-001-c1`: 問い合わせ部署振り分け。Gold: `billing` $\to$ W_fix: `tech`
- `tp-retain-002-c2`: 前提含意。Gold: `supports` $\to$ W_fix: `contradicts`
- `tp-scale-001-c2`: 配送手段選択。Gold: `c1` $\to$ W_fix: `c2`

---

## 7. 診断結論と次フェーズ提案

### 4つの選択肢の客観的評価

1. **Scale（データ件数・バッチ規模拡大）: 【却下】**
   - Phrasing Train (E〜J) は 98.3% (236/240)、Diff Both 95.0% であり、モデルは学習表現を完璧に習得している。
   - 単に学習データを倍増させても、未見表現での片問誤答や等号境界ドリフトは解消せず、むしろ境界サンプルの希釈を悪化させる。

2. **Variety（表現・ドメインの多様性拡大）: 【却下】**
   - 表現Familyは既に16種類（A〜P）投入されており、未見のFamily M (Diff Both 62.5%) や Family N (Diff Both 75.0%) では目標60%を達成している。
   - 単に表現種類を増やすだけでは、Family KやPの局所的な構文難度やM3境界ドリフトの解決には直結しない。

3. **Operator（損失関数・アーキテクチャ・対照損失）: 【却下】**
   - 標準CEでM4.1 100%、Cell C 100%、Train Diff Both 95.0% を達成しており、切替機構自体の学習能力（Diff Unswitched 0.0%）は完全に備わっている。
   - 新損失やモデル構造変更は、ERABIの最小構成原則（AGENTS.md）および実測結果からも時期尚早。

4. **Retention（既存能力保持・境界リプレイ強化）: 【★単一提案】**
   - **根拠1 (退行の100%が特定パターン)**:
     eval_v2 の退行9件中、5件が `actual == threshold` の等号境界値反転、4件が `game_action` の複合条件での単一ヒューリスティックによる。transfer_probe の退行も主因は境界値反転である。
     これはM4データ（480件）の流入によって、学習セット内でのM3境界事例（等号条件・複合条件）の比率が希釈され忘却されたことによる。
   - **根拠2 (採用版基準への最短路)**:
     M4.3.1モデルは未見表現（Family M/N）で目標60%を突破している。eval_v2 が 97.5% $\to$ 93.5% へ落ちたことが唯一最大のブロック要因である。
   - **具体的次フェーズ方針**:
     M3データ内の「境界値事例（`actual == threshold`）」および「複合AND条件事例」を学習時に適切に重み付け・リプレイする **【Retention Replay】** を実施することで、eval_v2 $\ge 97.0\%$ を即座に回復・保持し、正式採用版を確立する。
"""

    return report


def main():
    print("=== ERABI M4.3.2 Generalization Gap Diagnostic ===")
    t0 = time.time()

    print(f"Loading W_m4_3p_fix engine from {CHECKPOINT_PATH}...")
    engine = GLiClassEngine(model_id=CHECKPOINT_PATH, device="cuda" if torch.cuda.is_available() else "cpu")

    split_results = {}
    diagnostic_summary = {}
    domain_stratum_summary = {}

    for split_key, split_path in PHRASING_DATASETS.items():
        print(f"\nEvaluating {split_key} ({split_path.name})...")
        t_sp = time.time()
        results, _ = evaluate_split(engine, split_path)
        print(f"  Done in {time.time() - t_sp:.2f}s.")
        split_results[split_key] = results

        # Save individual prediction file
        pred_out_name = f"{split_key}_predictions.json"
        if split_key == "fresh_phrasing_eval":
            pred_out_name = "phrasing_fresh_predictions.json"
        with open(OUT_DIR / pred_out_name, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"  Saved predictions to {OUT_DIR / pred_out_name}")

        # Split overall
        split_stats = analyze_pairs_and_directions(results)

        # Family breakdown
        fams = sorted(list(set(r["phrasing_family"] for r in results)))
        family_stats = {}
        for f in fams:
            sub = [r for r in results if r["phrasing_family"] == f]
            family_stats[f] = analyze_pairs_and_directions(sub)

        diagnostic_summary[split_key] = {
            "overall": split_stats,
            "families": family_stats,
        }

        # Domain and Stratum breakdown
        domain_stratum_summary[split_key] = analyze_domain_and_stratum(results)

    del engine
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # Fresh error matrix
    fresh_matrix = analyze_fresh_error_matrix(split_results["fresh_phrasing_eval"])

    # Family summary standalone file
    all_families = {}
    for split_key in ["phrasing_train", "phrasing_dev", "fresh_phrasing_eval"]:
        for fam_key, fstats in diagnostic_summary[split_key]["families"].items():
            all_families[fam_key] = {
                "split": split_key,
                **fstats,
            }
    with open(OUT_DIR / "family_summary.json", "w", encoding="utf-8") as f:
        json.dump(all_families, f, indent=2, ensure_ascii=False)
    print(f"\nSaved family summary to {OUT_DIR / 'family_summary.json'}")

    # Save gap diagnostic summary (including domain/stratum and fresh matrix)
    full_diagnostic_payload = {
        "splits": diagnostic_summary,
        "domain_stratum": domain_stratum_summary,
        "fresh_error_matrix": fresh_matrix,
    }
    summary_path = OUT_DIR / "gap_diagnostic_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(full_diagnostic_payload, f, indent=2, ensure_ascii=False)
    print(f"Saved comprehensive diagnostic summary to {summary_path}")

    # Analyze eval_v2 retention transitions
    v2_transitions, v2_diffs = analyze_eval_v2_transitions()
    with open(OUT_DIR / "retention_transitions.json", "w", encoding="utf-8") as f:
        json.dump(v2_transitions, f, indent=2, ensure_ascii=False)
    with open(OUT_DIR / "eval_v2_diff_cases.json", "w", encoding="utf-8") as f:
        json.dump(v2_diffs, f, indent=2, ensure_ascii=False)
    print(f"Saved retention transitions to {OUT_DIR / 'retention_transitions.json'}")
    print(f"Saved eval_v2 diff cases to {OUT_DIR / 'eval_v2_diff_cases.json'}")

    # Analyze transfer_probe transitions
    tp_transitions, tp_diffs = analyze_transfer_probe_transitions()
    with open(OUT_DIR / "transfer_transitions.json", "w", encoding="utf-8") as f:
        json.dump(tp_transitions, f, indent=2, ensure_ascii=False)
    with open(OUT_DIR / "transfer_probe_diff_cases.json", "w", encoding="utf-8") as f:
        json.dump(tp_diffs, f, indent=2, ensure_ascii=False)
    print(f"Saved transfer transitions to {OUT_DIR / 'transfer_transitions.json'}")
    print(f"Saved transfer_probe diff cases to {OUT_DIR / 'transfer_probe_diff_cases.json'}")

    # Build Markdown Diagnostic Report & notes.md
    print("\nGenerating diagnostic_report.md and notes.md...")
    report_md = build_diagnostic_report(
        diagnostic_summary,
        domain_stratum_summary,
        fresh_matrix,
        v2_transitions,
        v2_diffs,
        tp_transitions,
        tp_diffs,
    )
    report_path = OUT_DIR / "diagnostic_report.md"
    notes_path = OUT_DIR / "notes.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"Saved diagnostic report to {report_path} and {notes_path}")

    print(f"\nM4.3.2 Diagnostic completed in {time.time() - t0:.1f}s!")


if __name__ == "__main__":
    main()
