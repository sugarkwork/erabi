"""Evaluation and 4-Model Comparison Script for ERABI M4.4-R Targeted Retention Replay.

Evaluates at T = 1.0:
1. W_v2_ce10 (M3.5 Baseline)
2. W_m4_1 (M4.1 Exception Baseline)
3. W_m4_3p_fix (M4.3.1 Semantic Repair Model)
4. W_m4_4r (New M4.4-R Retention Replay Model)

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

Produces:
- Prediction files for W_m4_4r across all datasets in runs/m4_4_retention/comparisons/
- Full transition analysis (W_m4_3p_fix -> W_m4_4r) for eval_v2, fresh_eval, transfer, smoke
- Comprehensive comparison report in runs/m4_4_retention/transition_summary.json
- Markdown report in runs/m4_4_retention/notes.md
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

OUT_DIR = ROOT / "runs/m4_4_retention"
COMP_DIR = OUT_DIR / "comparisons"
COMP_DIR.mkdir(parents=True, exist_ok=True)

MODEL_M4_4R_PATH = ROOT / "runs/m4_4_retention/trained/checkpoint"
M4_3_1_COMP_DIR = ROOT / "runs/m4_3_1_phrasing_fix/comparisons"

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
    print("=== ERABI M4.4-R Comprehensive 4-Model Comparison ===")
    t0 = time.time()

    print(f"Loading W_m4_4r engine from {MODEL_M4_4R_PATH}...")
    engine = GLiClassEngine(model_id=str(MODEL_M4_4R_PATH), device="cuda:0" if torch.cuda.is_available() else "cpu")

    m4_4r_predictions: Dict[str, List[Dict[str, Any]]] = {}
    m4_4r_metrics: Dict[str, Dict[str, Any]] = {}

    for dname, dpath in DATASETS.items():
        print(f"Evaluating W_m4_4r on {dname} ({dpath.name})...")
        t_d = time.time()
        res, met = evaluate_dataset(engine, dpath)
        print(f"  Acc: {met['accuracy']*100:.1f}%, NLL: {met['mean_nll']:.4f}, Duration: {time.time() - t_d:.2f}s")
        m4_4r_predictions[dname] = res
        m4_4r_metrics[dname] = met

        # Save individual prediction file
        out_pred_file = COMP_DIR / f"W_m4_4r_{dname}_predictions.json"
        with open(out_pred_file, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2, ensure_ascii=False)

    del engine
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # Load baseline predictions from M4.3.1 comparisons
    models = ["W_v2_ce10", "W_m4_1", "W_m4_3p_fix", "W_m4_4r"]
    all_metrics: Dict[str, Dict[str, Dict[str, Any]]] = {m: {} for m in models}
    all_metrics["W_m4_4r"] = m4_4r_metrics

    for m in ["W_v2_ce10", "W_m4_1", "W_m4_3p_fix"]:
        for dname, dpath in DATASETS.items():
            base_pred_file = M4_3_1_COMP_DIR / f"{m}_{dname}_predictions.json"
            if base_pred_file.exists():
                records = json.load(open(base_pred_file, encoding="utf-8"))
                # Recalculate metrics
                corr = sum(1 for r in records if r["is_correct"])
                n = len(records)
                nll = sum(r["nll"] for r in records) / n
                brier = sum(r["brier"] for r in records) / n
                met = {"count": n, "correct_count": corr, "accuracy": corr / n, "mean_nll": nll, "mean_brier": brier}

                # Pair stats
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
                            else:
                                if pair[0]["predicted"] == pair[1]["predicted"]:
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
                    met["diff_unswitched_rate"] = (diff_unswitched / diff_pairs) if diff_pairs > 0 else 0.0
                    met["same_pairs"] = same_pairs
                    met["same_both"] = same_both
                    met["same_both_rate"] = (same_both / same_pairs) if same_pairs > 0 else 0.0

                all_metrics[m][dname] = met

    # Transition Analysis (W_m4_3p_fix -> W_m4_4r)
    transitions: Dict[str, Any] = {}
    for dname, dpath in DATASETS.items():
        raw_map = {json.loads(l)["id"]: json.loads(l) for l in open(dpath, encoding="utf-8") if l.strip()}
        base_pred_file = M4_3_1_COMP_DIR / f"W_m4_3p_fix_{dname}_predictions.json"
        if base_pred_file.exists():
            base_preds = {r["id"]: r for r in json.load(open(base_pred_file, encoding="utf-8"))}
            new_preds = {r["id"]: r for r in m4_4r_predictions[dname]}
            transitions[dname] = compute_transitions(base_preds, new_preds, raw_map)

    # Save transitions
    trans_path = OUT_DIR / "transition_summary.json"
    with open(trans_path, "w", encoding="utf-8") as f:
        json.dump(transitions, f, indent=2, ensure_ascii=False)
    print(f"\nSaved transition summary to {trans_path}")

    # Build Markdown report
    build_markdown_report(all_metrics, transitions, m4_4r_predictions)
    print(f"\nCompleted evaluation and report generation in {time.time() - t0:.1f}s!")


def build_markdown_report(metrics: Dict[str, Dict[str, Dict[str, Any]]],
                          transitions: Dict[str, Any],
                          m4_4r_preds: Dict[str, List[Dict[str, Any]]]):
    # Table of 4 models across 9 datasets
    rows = []
    dataset_order = [
        ("fresh_phrasing_eval_fix", "1. 修正 fresh_phrasing_eval (未見M〜P, 120件)"),
        ("cell_a_fix", "2. 修正 Cell A (Old Dom + Old Phr, 40件)"),
        ("cell_b_fix", "3. 修正 Cell B (Old Dom + New Phr, 40件)"),
        ("cell_c_new_dom_old_phr", "4. Cell C (New Dom + Old Phr, 40件)"),
        ("novel_priority_eval", "5. novel_priority_eval (Hist A〜D, 120件)"),
        ("eval_exception", "6. eval_exception (M4.1, 120件)"),
        ("eval_v2", "7. eval_v2 (M3 合成ルール, 200件)"),
        ("transfer_probe", "8. transfer_probe (32問)"),
        ("smoke_cases", "9. smoke_cases (12問)"),
    ]

    for dkey, dlabel in dataset_order:
        row_str = f"| **{dlabel}** | "
        for m in ["W_v2_ce10", "W_m4_1", "W_m4_3p_fix", "W_m4_4r"]:
            m_data = metrics.get(m, {}).get(dkey, {})
            acc_str = f"{m_data.get('accuracy', 0.0)*100:.1f}% ({m_data.get('correct_count', 0)}/{m_data.get('count', 0)})"
            if "diff_both" in m_data:
                db_str = f"<br>Diff Both: {m_data['diff_both']}/{m_data['diff_pairs']} ({m_data['diff_both_rate']*100:.1f}%)"
            else:
                db_str = ""
            nll_str = f"<br>NLL: {m_data.get('mean_nll', 0.0):.4f}"
            row_str += f"{acc_str}{db_str}{nll_str} | "
        rows.append(row_str)

    # eval_v2 transition breakdown
    v2_tr = transitions["eval_v2"]
    v2_rec = v2_tr["recovered_cases"]
    v2_reg = v2_tr["regressed_cases"]

    # Fresh phrasing family breakdown
    fresh_results = m4_4r_preds["fresh_phrasing_eval_fix"]
    fresh_fams = sorted(list(set(r["phrasing_family"] for r in fresh_results)))
    fresh_fam_rows = []
    for fam in fresh_fams:
        f_sub = [r for r in fresh_results if r["phrasing_family"] == fam]
        corr = sum(1 for r in f_sub if r["is_correct"])
        acc = corr / len(f_sub)
        nll = sum(r["nll"] for r in f_sub) / len(f_sub)

        f_groups: Dict[str, List[Dict[str, Any]]] = {}
        for r in f_sub:
            f_groups.setdefault(r["group_id"], []).append(r)
        d_both = 0
        d_pairs = 0
        s_both = 0
        s_pairs = 0
        d_unsw = 0
        for gid, pair in f_groups.items():
            if len(pair) == 2:
                is_b = pair[0]["is_correct"] and pair[1]["is_correct"]
                if pair[0]["target"] != pair[1]["target"]:
                    d_pairs += 1
                    if is_b:
                        d_both += 1
                    elif pair[0]["predicted"] == pair[1]["predicted"]:
                        d_unsw += 1
                else:
                    s_pairs += 1
                    if is_b:
                        s_both += 1
        fresh_fam_rows.append(
            f"| `{fam}` | {len(f_sub)} | {acc*100:.1f}% ({corr}/{len(f_sub)}) | {nll:.4f} | "
            f"{d_both}/{d_pairs} ({(d_both/d_pairs)*100:.1f}%) | "
            f"{s_both}/{s_pairs} ({(s_both/s_pairs)*100:.1f}%) | "
            f"{d_unsw}/{d_pairs} ({(d_unsw/d_pairs)*100:.1f}%) |"
        )

    report = f"""# ERABI M4.4-R Targeted Retention Replay 実測報告

更新日: 2026-09-19  
対象モデル: `W_m4_4r` (`runs/m4_4_retention/trained/checkpoint`)  
評価条件: $T = 1.0$ 固定（再学習・データ生成・校正・API変更なし）

---

## 1. 4モデル総合対照表（すべて $T = 1.0$）

| 評価セット | 基準版 (`W_v2_ce10`) | M4.1版 (`W_m4_1`) | M4.3.1版 (`W_m4_3p_fix`) | **新M4.4-R (`W_m4_4r`)** |
|---|:---:|:---:|:---:|:---:|
{chr(10).join(rows)}

---

## 2. eval_v2 (M3旧能力) Retention 遷移分析

W_m4_3p_fix (93.5%, 187/200) -> **W_m4_4r ({metrics['W_m4_4r']['eval_v2']['accuracy']*100:.1f}%, {metrics['W_m4_4r']['eval_v2']['correct_count']}/200)**:

| 区分 | 件数 | 割合 | 説明 |
|---|---:|---:|---|
| **Maintained Correct** (正解維持) | **{v2_tr['maintained_correct_count']}** | {v2_tr['maintained_correct_rate']*100:.1f}% | 両モデルで正解 |
| **Recovered** (新規回復) | **{v2_tr['recovered_count']}** | {v2_tr['recovered_rate']*100:.1f}% | W_m4_3p_fix誤答 -> W_m4_4r正解 |
| **Regressed** (新規退行) | **{v2_tr['regressed_count']}** | {v2_tr['regressed_rate']*100:.1f}% | W_m4_3p_fix正解 -> W_m4_4r誤答 |
| **Wrong Both** (両方誤答) | **{v2_tr['wrong_both_count']}** | {v2_tr['wrong_both_rate']*100:.1f}% | 両モデルで誤答 |
| **合計** | **{v2_tr['total_cases']}** | 100.0% | |

### 2.1 回復個票 ({len(v2_rec)}件)
"""
    for r in v2_rec:
        report += f"- `{r['id']}` ({r.get('rule_kind')}, {r.get('template_family')}): Gold `{r['target']}` | Fix `{r['base_predicted']}` -> **4R `{r['new_predicted']}`**\\n"

    report += f"\n### 2.2 新規退行個票 ({len(v2_reg)}件)\n"
    if not v2_reg:
        report += "- **新規退行 0件（完全な単調改善）**\n"
    for r in v2_reg:
        report += f"- `{r['id']}` ({r.get('rule_kind')}): Gold `{r['target']}` | Fix `{r['base_predicted']}` -> **4R `{r['new_predicted']}`**\\n"

    report += f"""
---

## 3. fresh_phrasing_eval Family別詳細集計表

| 表現Family | 件数 | 正答率 (Acc) | Mean NLL | Diff Both | Same Both | Diff Unswitched |
|---|---:|:---:|:---:|:---:|:---:|:---:|
{chr(10).join(fresh_fam_rows)}

---

## 4. 目標達成判定

| 判定基準項目 | 目標値 | W_m4_3p_fix 実測値 | **W_m4_4r 実測値** | 判定 |
|---|:---:|:---:|:---:|:---:|
| **eval_v2 (Retention回復)** | >= 97.0% | 93.5% (187/200) | **{metrics['W_m4_4r']['eval_v2']['accuracy']*100:.1f}% ({metrics['W_m4_4r']['eval_v2']['correct_count']}/200)** | **{'PASS' if metrics['W_m4_4r']['eval_v2']['accuracy'] >= 0.97 else 'FAIL'}** |
| **fresh Diff Both (表現保持)** | >= 45.0% (50%から-5pt以内) | 50.0% (15/30) | **{metrics['W_m4_4r']['fresh_phrasing_eval_fix']['diff_both_rate']*100:.1f}% ({metrics['W_m4_4r']['fresh_phrasing_eval_fix']['diff_both']}/30)** | **{'PASS' if metrics['W_m4_4r']['fresh_phrasing_eval_fix']['diff_both_rate'] >= 0.45 else 'FAIL'}** |
| **eval_exception (例外保持)** | >= 98.0% | 100.0% (120/120) | **{metrics['W_m4_4r']['eval_exception']['accuracy']*100:.1f}% ({metrics['W_m4_4r']['eval_exception']['correct_count']}/120)** | **{'PASS' if metrics['W_m4_4r']['eval_exception']['accuracy'] >= 0.98 else 'FAIL'}** |
| **smoke_cases (スモーク保持)** | >= 10/12 (83.3%) | 10/12 (83.3%) | **{metrics['W_m4_4r']['smoke_cases']['correct_count']}/12 ({metrics['W_m4_4r']['smoke_cases']['accuracy']*100:.1f}%)** | **{'PASS' if metrics['W_m4_4r']['smoke_cases']['correct_count'] >= 10 else 'FAIL'}** |
"""

    notes_path = OUT_DIR / "notes.md"
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Saved report to {notes_path}")


if __name__ == "__main__":
    main()
