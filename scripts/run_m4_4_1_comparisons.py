"""Evaluation and Multi-Model Comparison Script for ERABI M4.4.1 Targeted Retention Replay.

Evaluates at T = 1.0:
1. W_v2_ce10 (M3.5 Baseline)
2. W_m4_1 (M4.1 Exception Baseline)
3. W_m4_3p_fix (M4.3.1 Semantic Repair Model)
4. W_m4_4r (M4.4-R Retention Replay Model)
5. W_m4_4_1r (New M4.4.1 Selector Coverage Fix Model)

Across 9 Evaluation Datasets:
1. fresh_phrasing_eval (120 cases: 60 pairs, Families M~P)
2. cell_a_fix (40 cases: Old Domain + Old Phrasing)
3. cell_b_fix (40 cases: Old Domain + New Phrasing)
4. cell_c (40 cases: New Domain + Old Phrasing)
5. novel_priority_eval (120 cases: Historical Families A~D)
6. eval_exception (120 cases: M4.1 Rule Exception)
7. eval_v2 (200 cases: M3 Synthetic Rules)
8. transfer_probe (32 cases: M3.1 Transfer Probe)
9. smoke_cases (12 cases: Operational Smoke)

Special Focus on Regression Tracking:
- 5 Comparison Equality regressions: eval_v2-er-0009-c1, eval_v2-er-0009-c2, eval_v2-er-0049-c1, eval_v2-er-0093-c1, eval_v2-er-0093-c2
- 4 Composite Logic regressions: eval_v2-er-0015-c1, eval_v2-er-0057-c1, eval_v2-er-0071-c1, eval_v2-er-0091-c1
- 2 M4.4-R regressions: eval_v2-gf-0002-c1, eval_v2-gf-0052-c1

Outputs:
- runs/m4_4_1_retention/comparisons/
- runs/m4_4_1_retention/transition_summary.json
- runs/m4_4_1_retention/regression_case_study.json
- runs/m4_4_1_retention/notes.md
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

OUT_DIR = ROOT / "runs/m4_4_1_retention"
COMP_DIR = OUT_DIR / "comparisons"
COMP_DIR.mkdir(parents=True, exist_ok=True)

MODEL_M4_4_1R_PATH = ROOT / "runs/m4_4_1_retention/trained/checkpoint"
M4_3_1_COMP_DIR = ROOT / "runs/m4_3_1_phrasing_fix/comparisons"
M4_4_COMP_DIR = ROOT / "runs/m4_4_retention/comparisons"

DATASETS = {
    "fresh_phrasing_eval_fix": ROOT / "data/m4_3_1_phrasing_fix/fresh_phrasing_eval.jsonl",
    "cell_a_fix": ROOT / "data/m4_3_1_phrasing_fix/diagnostic_fix/cell_a_old_domain_old_phrasing.jsonl",
    "cell_b_fix": ROOT / "data/m4_3_1_phrasing_fix/diagnostic_fix/cell_b_old_domain_new_phrasing.jsonl",
    "cell_c_new_dom_old_phr": ROOT / "data/m4_2_1_diagnostic/cell_c_new_domain_old_phrasing.jsonl",
    "novel_priority_eval": ROOT / "data/m4_2_robustness/novel_priority_eval.jsonl",
    "eval_exception": ROOT / "data/m4_1_exception/eval_exception.jsonl",
    "eval_v2": ROOT / "data/m3_3_v2/eval_v2.jsonl",
    "transfer_probe": ROOT / "data/m3_1/transfer_probe.jsonl",
    "smoke_cases": ROOT / "examples/smoke_cases.jsonl",
}

COMPARISON_EQUALITY_REGRESSIONS = [
    "eval_v2-er-0009-c1",
    "eval_v2-er-0009-c2",
    "eval_v2-er-0049-c1",
    "eval_v2-er-0093-c1",
    "eval_v2-er-0093-c2",
]

COMPOSITE_LOGIC_REGRESSIONS = [
    "eval_v2-er-0015-c1",
    "eval_v2-er-0057-c1",
    "eval_v2-er-0071-c1",
    "eval_v2-er-0091-c1",
]

M4_4_NEW_REGRESSIONS = [
    "eval_v2-gf-0002-c1",
    "eval_v2-gf-0052-c1",
]


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
            "rule_kind": row.get("rule_kind"),
            "domain_class": row.get("domain_class"),
            "stratum": row.get("stratum"),
            "conflict": row.get("conflict"),
            "priority_order": row.get("priority_order"),
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
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in results:
        gid = r.get("group_id")
        if gid:
            groups.setdefault(gid, []).append(r)

    total_pairs = 0
    pair_both = 0
    diff_pairs = 0
    diff_both = 0
    diff_unswitched = 0
    diff_switched_wrong = 0
    same_pairs = 0
    same_both = 0

    for gid, pair in groups.items():
        if len(pair) == 2:
            total_pairs += 1
            r1, r2 = pair[0], pair[1]
            is_both = (r1["is_correct"] and r2["is_correct"])
            if is_both:
                pair_both += 1

            if r1["target"] != r2["target"]:
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

    if total_pairs > 0:
        metrics["total_pairs"] = total_pairs
        metrics["pair_both"] = pair_both
        metrics["pair_both_rate"] = pair_both / total_pairs
        metrics["diff_pairs"] = diff_pairs
        metrics["diff_both"] = diff_both
        metrics["diff_both_rate"] = (diff_both / diff_pairs) if diff_pairs > 0 else 0.0
        metrics["diff_unswitched"] = diff_unswitched
        metrics["diff_unswitched_rate"] = (diff_unswitched / diff_pairs) if diff_pairs > 0 else 0.0
        metrics["same_pairs"] = same_pairs
        metrics["same_both"] = same_both
        metrics["same_both_rate"] = (same_both / same_pairs) if same_pairs > 0 else 0.0

    return results, metrics


def compute_transitions(base_preds: Dict[str, Dict[str, Any]],
                        new_preds: Dict[str, Dict[str, Any]],
                        raw_records: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    maintained_correct = []
    recovered = []
    regressed = []
    wrong_both = []

    for cid, raw in sorted(raw_records.items()):
        p_base = base_preds.get(cid)
        p_new = new_preds.get(cid)
        if not p_base or not p_new:
            continue

        c_base = p_base["is_correct"]
        c_new = p_new["is_correct"]

        entry = {
            "id": cid,
            "group_id": raw.get("group_id"),
            "task_family": raw.get("task_family"),
            "rule_kind": raw.get("rule_kind"),
            "template_family": raw.get("template_family"),
            "context": raw.get("context"),
            "question": raw.get("question"),
            "target": raw["target"]["choice_id"],
            "base_predicted": p_base["predicted"],
            "base_prob": p_base.get("probabilities", []),
            "new_predicted": p_new["predicted"],
            "new_prob": p_new.get("probabilities", []),
        }

        if c_base and c_new:
            maintained_correct.append(entry)
        elif not c_base and c_new:
            recovered.append(entry)
        elif c_base and not c_new:
            regressed.append(entry)
        else:
            wrong_both.append(entry)

    total = len(maintained_correct) + len(recovered) + len(regressed) + len(wrong_both)
    return {
        "total_cases": total,
        "maintained_correct_count": len(maintained_correct),
        "recovered_count": len(recovered),
        "regressed_count": len(regressed),
        "wrong_both_count": len(wrong_both),
        "maintained_correct_rate": len(maintained_correct) / total if total > 0 else 0.0,
        "recovered_rate": len(recovered) / total if total > 0 else 0.0,
        "regressed_rate": len(regressed) / total if total > 0 else 0.0,
        "wrong_both_rate": len(wrong_both) / total if total > 0 else 0.0,
        "recovered_cases": recovered,
        "regressed_cases": regressed,
    }


def main():
    print("=== ERABI M4.4.1 Comprehensive 5-Model Comparison ===")
    t0 = time.time()

    print(f"Loading W_m4_4_1r engine from {MODEL_M4_4_1R_PATH}...")
    engine = GLiClassEngine(model_id=str(MODEL_M4_4_1R_PATH), device="cuda:0" if torch.cuda.is_available() else "cpu")

    m4_4_1r_predictions: Dict[str, List[Dict[str, Any]]] = {}
    m4_4_1r_metrics: Dict[str, Dict[str, Any]] = {}

    for dname, dpath in DATASETS.items():
        print(f"Evaluating W_m4_4_1r on {dname} ({dpath.name})...")
        t_d = time.time()
        res, met = evaluate_dataset(engine, dpath)
        print(f"  Acc: {met['accuracy']*100:.1f}%, NLL: {met['mean_nll']:.4f}, Duration: {time.time() - t_d:.2f}s")
        m4_4_1r_predictions[dname] = res
        m4_4_1r_metrics[dname] = met

        # Save individual prediction file
        out_pred_file = COMP_DIR / f"W_m4_4_1r_{dname}_predictions.json"
        with open(out_pred_file, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2, ensure_ascii=False)

    del engine
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # Load baseline predictions
    models = ["W_v2_ce10", "W_m4_1", "W_m4_3p_fix", "W_m4_4r", "W_m4_4_1r"]
    all_metrics: Dict[str, Dict[str, Dict[str, Any]]] = {m: {} for m in models}
    all_metrics["W_m4_4_1r"] = m4_4_1r_metrics

    # Load W_v2_ce10, W_m4_1, W_m4_3p_fix from M4.3.1 comparisons
    for m in ["W_v2_ce10", "W_m4_1", "W_m4_3p_fix"]:
        for dname, dpath in DATASETS.items():
            base_pred_file = M4_3_1_COMP_DIR / f"{m}_{dname}_predictions.json"
            if base_pred_file.exists():
                records = json.load(open(base_pred_file, encoding="utf-8"))
                corr = sum(1 for r in records if r["is_correct"])
                n = len(records)
                nll = sum(r["nll"] for r in records) / n
                brier = sum(r["brier"] for r in records) / n
                met = {"count": n, "correct_count": corr, "accuracy": corr / n, "mean_nll": nll, "mean_brier": brier}

                groups: Dict[str, List[Dict[str, Any]]] = {}
                for r in records:
                    gid = r.get("group_id")
                    if gid:
                        groups.setdefault(gid, []).append(r)
                total_pairs = 0
                pair_both = 0
                diff_pairs = 0
                diff_both = 0
                same_pairs = 0
                same_both = 0
                diff_unswitched = 0
                for gid, pair in groups.items():
                    if len(pair) == 2:
                        total_pairs += 1
                        is_both = pair[0]["is_correct"] and pair[1]["is_correct"]
                        if is_both:
                            pair_both += 1
                        if pair[0]["target"] != pair[1]["target"]:
                            diff_pairs += 1
                            if is_both:
                                diff_both += 1
                            elif pair[0]["predicted"] == pair[1]["predicted"]:
                                diff_unswitched += 1
                        else:
                            same_pairs += 1
                            if is_both:
                                same_both += 1

                if total_pairs > 0:
                    met["total_pairs"] = total_pairs
                    met["pair_both"] = pair_both
                    met["pair_both_rate"] = pair_both / total_pairs
                    met["diff_pairs"] = diff_pairs
                    met["diff_both"] = diff_both
                    met["diff_both_rate"] = (diff_both / diff_pairs) if diff_pairs > 0 else 0.0
                    met["diff_unswitched"] = diff_unswitched
                    met["same_pairs"] = same_pairs
                    met["same_both"] = same_both
                    met["same_both_rate"] = (same_both / same_pairs) if same_pairs > 0 else 0.0

                all_metrics[m][dname] = met

    # Load W_m4_4r from M4.4 comparisons
    for dname, dpath in DATASETS.items():
        base_pred_file = M4_4_COMP_DIR / f"W_m4_4r_{dname}_predictions.json"
        if base_pred_file.exists():
            records = json.load(open(base_pred_file, encoding="utf-8"))
            corr = sum(1 for r in records if r["is_correct"])
            n = len(records)
            nll = sum(r["nll"] for r in records) / n
            brier = sum(r["brier"] for r in records) / n
            met = {"count": n, "correct_count": corr, "accuracy": corr / n, "mean_nll": nll, "mean_brier": brier}

            groups = {}
            for r in records:
                gid = r.get("group_id")
                if gid:
                    groups.setdefault(gid, []).append(r)
            total_pairs = 0
            pair_both = 0
            diff_pairs = 0
            diff_both = 0
            same_pairs = 0
            same_both = 0
            diff_unswitched = 0
            for gid, pair in groups.items():
                if len(pair) == 2:
                    total_pairs += 1
                    is_both = pair[0]["is_correct"] and pair[1]["is_correct"]
                    if is_both:
                        pair_both += 1
                    if pair[0]["target"] != pair[1]["target"]:
                        diff_pairs += 1
                        if is_both:
                            diff_both += 1
                        elif pair[0]["predicted"] == pair[1]["predicted"]:
                            diff_unswitched += 1
                    else:
                        same_pairs += 1
                        if is_both:
                            same_both += 1

            if total_pairs > 0:
                met["total_pairs"] = total_pairs
                met["pair_both"] = pair_both
                met["pair_both_rate"] = pair_both / total_pairs
                met["diff_pairs"] = diff_pairs
                met["diff_both"] = diff_both
                met["diff_both_rate"] = (diff_both / diff_pairs) if diff_pairs > 0 else 0.0
                met["diff_unswitched"] = diff_unswitched
                met["same_pairs"] = same_pairs
                met["same_both"] = same_both
                met["same_both_rate"] = (same_both / same_pairs) if same_pairs > 0 else 0.0

            all_metrics["W_m4_4r"][dname] = met

    # Transition Analysis vs W_m4_3p_fix
    transitions: Dict[str, Any] = {}
    for dname, dpath in DATASETS.items():
        base_pred_file = M4_3_1_COMP_DIR / f"W_m4_3p_fix_{dname}_predictions.json"
        if base_pred_file.exists():
            base_records = {r["id"]: r for r in json.load(open(base_pred_file, encoding="utf-8"))}
            new_records = {r["id"]: r for r in m4_4_1r_predictions[dname]}
            raw_records = {json.loads(l)["id"]: json.loads(l) for l in open(dpath, encoding="utf-8") if l.strip()}
            trans = compute_transitions(base_records, new_records, raw_records)
            transitions[dname] = trans

    with open(OUT_DIR / "transition_summary.json", "w", encoding="utf-8") as f:
        json.dump(transitions, f, indent=2, ensure_ascii=False)

    # Dedicated Regression Tracking for eval_v2
    eval_v2_preds_m4_4_1 = {r["id"]: r for r in m4_4_1r_predictions["eval_v2"]}
    eval_v2_preds_m4_3_1 = {r["id"]: r for r in json.load(open(M4_3_1_COMP_DIR / "W_m4_3p_fix_eval_v2_predictions.json", encoding="utf-8"))}
    eval_v2_preds_m4_4r = {r["id"]: r for r in json.load(open(M4_4_COMP_DIR / "W_m4_4r_eval_v2_predictions.json", encoding="utf-8"))}
    eval_v2_preds_v2_ce10 = {r["id"]: r for r in json.load(open(M4_3_1_COMP_DIR / "W_v2_ce10_eval_v2_predictions.json", encoding="utf-8"))}
    eval_v2_raw = {json.loads(l)["id"]: json.loads(l) for l in open(DATASETS["eval_v2"], encoding="utf-8") if l.strip()}

    def get_case_status(cid: str) -> Dict[str, Any]:
        raw = eval_v2_raw[cid]
        return {
            "id": cid,
            "group_id": raw["group_id"],
            "context": raw["context"],
            "question": raw["question"],
            "target": raw["target"]["choice_id"],
            "W_v2_ce10": {"pred": eval_v2_preds_v2_ce10[cid]["predicted"], "is_correct": eval_v2_preds_v2_ce10[cid]["is_correct"]},
            "W_m4_3p_fix": {"pred": eval_v2_preds_m4_3_1[cid]["predicted"], "is_correct": eval_v2_preds_m4_3_1[cid]["is_correct"]},
            "W_m4_4r": {"pred": eval_v2_preds_m4_4r[cid]["predicted"], "is_correct": eval_v2_preds_m4_4r[cid]["is_correct"]},
            "W_m4_4_1r": {
                "pred": eval_v2_preds_m4_4_1[cid]["predicted"],
                "is_correct": eval_v2_preds_m4_4_1[cid]["is_correct"],
                "probs": eval_v2_preds_m4_4_1[cid]["probabilities"],
            },
        }

    comp_regressions_status = [get_case_status(cid) for cid in COMPARISON_EQUALITY_REGRESSIONS]
    comp_recovered_count = sum(1 for c in comp_regressions_status if c["W_m4_4_1r"]["is_correct"])

    composite_regressions_status = [get_case_status(cid) for cid in COMPOSITE_LOGIC_REGRESSIONS]
    composite_recovered_count = sum(1 for c in composite_regressions_status if c["W_m4_4_1r"]["is_correct"])

    m4_4_regressions_status = [get_case_status(cid) for cid in M4_4_NEW_REGRESSIONS]
    m4_4_recovered_count = sum(1 for c in m4_4_regressions_status if c["W_m4_4_1r"]["is_correct"])

    case_study = {
        "comparison_equality_regressions": {
            "total_tracked": len(COMPARISON_EQUALITY_REGRESSIONS),
            "recovered_count": comp_recovered_count,
            "recovered_rate": comp_recovered_count / len(COMPARISON_EQUALITY_REGRESSIONS),
            "cases": comp_regressions_status,
        },
        "composite_logic_regressions": {
            "total_tracked": len(COMPOSITE_LOGIC_REGRESSIONS),
            "recovered_count": composite_recovered_count,
            "recovered_rate": composite_recovered_count / len(COMPOSITE_LOGIC_REGRESSIONS),
            "cases": composite_regressions_status,
        },
        "m4_4_new_regressions": {
            "total_tracked": len(M4_4_NEW_REGRESSIONS),
            "recovered_count": m4_4_recovered_count,
            "recovered_rate": m4_4_recovered_count / len(M4_4_NEW_REGRESSIONS),
            "cases": m4_4_regressions_status,
        },
    }

    with open(OUT_DIR / "regression_case_study.json", "w", encoding="utf-8") as f:
        json.dump(case_study, f, indent=2, ensure_ascii=False)

    # Save Markdown notes
    notes_lines = [
        "# ERABI M4.4.1 Targeted Retention Replay (Selector Coverage Fix) Evaluation Notes\n",
        f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
        "## 1. 5-Model Comparison Overview (All T = 1.0)\n",
        "| Evaluation Dataset | Metric | W_v2_ce10 (M3.5) | W_m4_1 (M4.1) | W_m4_3p_fix (M4.3.1) | W_m4_4r (M4.4-R) | W_m4_4_1r (M4.4.1) |",
        "|---|---|:---:|:---:|:---:|:---:|:---:|",
    ]

    for dname in DATASETS:
        m_v2 = all_metrics["W_v2_ce10"].get(dname, {})
        m_41 = all_metrics["W_m4_1"].get(dname, {})
        m_43 = all_metrics["W_m4_3p_fix"].get(dname, {})
        m_44 = all_metrics["W_m4_4r"].get(dname, {})
        m_441 = all_metrics["W_m4_4_1r"].get(dname, {})

        acc_v2 = f"{m_v2.get('accuracy', 0)*100:.1f}%"
        acc_41 = f"{m_41.get('accuracy', 0)*100:.1f}%"
        acc_43 = f"{m_43.get('accuracy', 0)*100:.1f}%"
        acc_44 = f"{m_44.get('accuracy', 0)*100:.1f}%"
        acc_441 = f"{m_441.get('accuracy', 0)*100:.1f}%"

        notes_lines.append(f"| **{dname}** | Accuracy | {acc_v2} | {acc_41} | {acc_43} | {acc_44} | **{acc_441}** |")
        if "diff_both" in m_441:
            db_v2 = f"{m_v2.get('diff_both', 0)}/{m_v2.get('diff_pairs', 0)} ({m_v2.get('diff_both_rate', 0)*100:.1f}%)"
            db_41 = f"{m_41.get('diff_both', 0)}/{m_41.get('diff_pairs', 0)} ({m_41.get('diff_both_rate', 0)*100:.1f}%)"
            db_43 = f"{m_43.get('diff_both', 0)}/{m_43.get('diff_pairs', 0)} ({m_43.get('diff_both_rate', 0)*100:.1f}%)"
            db_44 = f"{m_44.get('diff_both', 0)}/{m_44.get('diff_pairs', 0)} ({m_44.get('diff_both_rate', 0)*100:.1f}%)"
            db_441 = f"{m_441.get('diff_both', 0)}/{m_441.get('diff_pairs', 0)} ({m_441.get('diff_both_rate', 0)*100:.1f}%)"
            notes_lines.append(f"| | Diff Both | {db_v2} | {db_41} | {db_43} | {db_44} | **{db_441}** |")

    notes_lines.extend([
        "\n## 2. Comparison Equality Regressions Recovery Status\n",
        f"Recovered: **{comp_recovered_count} / {len(COMPARISON_EQUALITY_REGRESSIONS)}** ({comp_recovered_count/len(COMPARISON_EQUALITY_REGRESSIONS)*100:.1f}%)\n",
    ])
    for c in comp_regressions_status:
        st = "RECOVERED" if c["W_m4_4_1r"]["is_correct"] else "STILL_WRONG"
        notes_lines.append(f"- **{c['id']}** ({c['group_id']}): Target={c['target']} | W_m4_3p_fix={c['W_m4_3p_fix']['pred']} | W_m4_4r={c['W_m4_4r']['pred']} | W_m4_4_1r={c['W_m4_4_1r']['pred']} -> **{st}**")

    notes_lines.extend([
        "\n## 3. Composite Logic Regressions Status\n",
        f"Recovered: **{composite_recovered_count} / {len(COMPOSITE_LOGIC_REGRESSIONS)}** ({composite_recovered_count/len(COMPOSITE_LOGIC_REGRESSIONS)*100:.1f}%)\n",
    ])
    for c in composite_regressions_status:
        st = "RECOVERED" if c["W_m4_4_1r"]["is_correct"] else "STILL_WRONG"
        notes_lines.append(f"- **{c['id']}** ({c['group_id']}): Target={c['target']} | W_m4_3p_fix={c['W_m4_3p_fix']['pred']} | W_m4_4r={c['W_m4_4r']['pred']} | W_m4_4_1r={c['W_m4_4_1r']['pred']} -> **{st}**")

    with open(OUT_DIR / "notes.md", "w", encoding="utf-8") as f:
        f.write("\n".join(notes_lines) + "\n")

    print(f"\nAll comparisons and regression case studies completed in {time.time() - t0:.2f}s.")
    print(f"Comparison equality recovery: {comp_recovered_count}/{len(COMPARISON_EQUALITY_REGRESSIONS)}")


if __name__ == "__main__":
    main()
