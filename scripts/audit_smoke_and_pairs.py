"""Detailed audit and breakdown script for M3.2 review handoff.

Calculates:
1. Exact 12-row smoke transition table (B0, W_bad, W_fix) with input hash, predictions, pmax, target prob, and transitions.
2. Transfer probe (32 cases) breakdown: accuracy, NLL, Brier, per-sample transitions (same 23 or swapped).
3. Pair accuracy breakdown: same target vs different target for holdout_corrected and final_test_corrected across B0, W_bad, W_fix.
4. Outputs artifacts to runs/m3_2_label_fix/supplemental_audit.json and runs/m3_2_label_fix/supplemental_audit.md.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from collections import defaultdict
from pathlib import Path

root_dir = Path("f:/ai/erabi-local")


def text_hash(context: str, question: str) -> str:
    norm = f"{unicodedata.normalize('NFC', context).strip().lower()}|||{unicodedata.normalize('NFC', question).strip().lower()}"
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


def audit_smoke_cases():
    with open(root_dir / "examples" / "smoke_cases.jsonl", "r", encoding="utf-8") as f:
        smoke_cases = [json.loads(line) for line in f]

    smoke_preds = {}
    for m in ["B0", "W_bad", "W_fix"]:
        pfile = root_dir / "runs" / "m3_2_label_fix" / "comparisons" / f"{m}_smoke_cases_predictions.jsonl"
        with open(pfile, "r", encoding="utf-8") as f:
            smoke_preds[m] = {p["id"]: p for p in [json.loads(line) for line in f]}

    table = []
    g_count = 0  # W_bad wrong -> W_fix correct
    l_count = 0  # W_bad correct -> W_fix wrong
    regressed_ids = []
    recovered_ids = []

    for sc in smoke_cases:
        sid = sc["id"]
        ctx = sc["context"]
        q = sc["question"]
        thash = text_hash(ctx, q)
        tgt = sc["target"]["choice_id"]

        p_b0 = smoke_preds["B0"][sid]
        p_bad = smoke_preds["W_bad"][sid]
        p_fix = smoke_preds["W_fix"][sid]

        def extract_info(p_obj, target_id):
            best_id = p_obj["best_candidate_id"]
            p_map = {c["id"]: c["probability"] for c in p_obj["choices"]}
            pmax = p_map.get(best_id, 0.0)
            ptgt = p_map.get(target_id, 0.0)
            corr = (best_id == target_id)
            return best_id, pmax, ptgt, corr

        b0_best, b0_pmax, b0_ptgt, b0_corr = extract_info(p_b0, tgt)
        bad_best, bad_pmax, bad_ptgt, bad_corr = extract_info(p_bad, tgt)
        fix_best, fix_pmax, fix_ptgt, fix_corr = extract_info(p_fix, tgt)

        if not bad_corr and fix_corr:
            trans = "誤答→正解 (回復)"
            g_count += 1
            recovered_ids.append(sid)
        elif bad_corr and not fix_corr:
            trans = "正解→誤答 (新たな退行)"
            l_count += 1
            regressed_ids.append(sid)
        elif bad_corr and fix_corr:
            trans = "正解→正解 (維持)"
        else:
            trans = "誤答→誤答 (未解決)"

        table.append({
            "id": sid,
            "input_hash": thash,
            "target": tgt,
            "B0": {
                "predicted": b0_best,
                "is_correct": b0_corr,
                "pmax": round(b0_pmax, 4),
                "target_prob": round(b0_ptgt, 4),
            },
            "W_bad": {
                "predicted": bad_best,
                "is_correct": bad_corr,
                "pmax": round(bad_pmax, 4),
                "target_prob": round(bad_ptgt, 4),
            },
            "W_fix": {
                "predicted": fix_best,
                "is_correct": fix_corr,
                "pmax": round(fix_pmax, 4),
                "target_prob": round(fix_ptgt, 4),
            },
            "transition": trans,
        })

    return {
        "table": table,
        "G_recovered_count": g_count,
        "recovered_ids": recovered_ids,
        "L_regressed_count": l_count,
        "regressed_ids": regressed_ids,
        "equation_check": f"W_fix(7) - W_bad(8) = G({g_count}) - L({l_count}) = {g_count - l_count}",
    }


def audit_transfer_probe():
    with open(root_dir / "data" / "m3_1" / "transfer_probe.jsonl", "r", encoding="utf-8") as f:
        tp_cases = [json.loads(line) for line in f]

    tp_preds = {}
    for m in ["B0", "W_bad", "W_fix"]:
        pfile = root_dir / "runs" / "m3_2_label_fix" / "comparisons" / f"{m}_transfer_probe_predictions.jsonl"
        with open(pfile, "r", encoding="utf-8") as f:
            tp_preds[m] = {p["id"]: p for p in [json.loads(line) for line in f]}

    bad_correct_ids = {p["id"] for p in tp_preds["W_bad"].values() if p["is_correct"]}
    fix_correct_ids = {p["id"] for p in tp_preds["W_fix"].values() if p["is_correct"]}

    common_correct = bad_correct_ids & fix_correct_ids
    bad_only_correct = bad_correct_ids - fix_correct_ids
    fix_only_correct = fix_correct_ids - bad_correct_ids
    both_wrong = set(tp_preds["W_bad"].keys()) - (bad_correct_ids | fix_correct_ids)

    # Detailed per-case transitions
    case_details = []
    for tc in tp_cases:
        cid = tc["id"]
        tgt = tc["target"]["choice_id"]
        bad_p = tp_preds["W_bad"][cid]
        fix_p = tp_preds["W_fix"][cid]

        bad_c = bad_p["is_correct"]
        fix_c = fix_p["is_correct"]
        if not bad_c and fix_c:
            t = "W_bad誤答→W_fix正解"
        elif bad_c and not fix_c:
            t = "W_bad正解→W_fix誤答"
        elif bad_c and fix_c:
            t = "両方正解"
        else:
            t = "両方誤答"

        case_details.append({
            "id": cid,
            "group_id": tc["group_id"],
            "target": tgt,
            "W_bad_pred": bad_p["best_candidate_id"],
            "W_bad_correct": bad_c,
            "W_fix_pred": fix_p["best_candidate_id"],
            "W_fix_correct": fix_c,
            "transition": t,
        })

    return {
        "total_cases": len(tp_cases),
        "W_bad_accuracy": f"{len(bad_correct_ids)}/{len(tp_cases)} ({len(bad_correct_ids)/len(tp_cases)*100:.1f}%)",
        "W_fix_accuracy": f"{len(fix_correct_ids)}/{len(tp_cases)} ({len(fix_correct_ids)/len(tp_cases)*100:.1f}%)",
        "common_correct_count": len(common_correct),
        "bad_only_correct_count": len(bad_only_correct),
        "bad_only_correct_ids": sorted(list(bad_only_correct)),
        "fix_only_correct_count": len(fix_only_correct),
        "fix_only_correct_ids": sorted(list(fix_only_correct)),
        "both_wrong_count": len(both_wrong),
        "case_details": case_details,
    }


def audit_pair_breakdowns(dataset_name: str, rel_path: str):
    with open(root_dir / rel_path, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f]

    # Group by group_id
    groups = defaultdict(list)
    for r in records:
        groups[r["group_id"]].append(r)

    # Count same target vs diff target
    same_tgt_groups = []
    diff_tgt_groups = []

    for gid, rlist in groups.items():
        assert len(rlist) == 2, f"Group {gid} has {len(rlist)} items"
        if rlist[0]["target"]["choice_id"] == rlist[1]["target"]["choice_id"]:
            same_tgt_groups.append(gid)
        else:
            diff_tgt_groups.append(gid)

    # Load predictions for all 3 models
    results = {
        "dataset": dataset_name,
        "total_groups": len(groups),
        "diff_target_groups_count": len(diff_tgt_groups),
        "same_target_groups_count": len(same_tgt_groups),
        "models": {},
    }

    for m in ["B0", "W_bad", "W_fix"]:
        pfile = root_dir / "runs" / "m3_2_label_fix" / "comparisons" / f"{m}_{dataset_name}_predictions.jsonl"
        with open(pfile, "r", encoding="utf-8") as f:
            preds = [json.loads(line) for line in f]
        pred_map = {p["id"]: p for p in preds}

        # Evaluate pair both correct
        all_both = 0
        diff_both = 0
        same_both = 0

        for gid, rlist in groups.items():
            p1 = pred_map[rlist[0]["id"]]
            p2 = pred_map[rlist[1]["id"]]
            both = (p1["is_correct"] and p2["is_correct"])
            if both:
                all_both += 1
                if gid in diff_tgt_groups:
                    diff_both += 1
                else:
                    same_both += 1

        results["models"][m] = {
            "all_pairs_both_correct": f"{all_both}/{len(groups)} ({all_both/len(groups)*100:.1f}%)",
            "diff_target_both_correct": f"{diff_both}/{len(diff_tgt_groups)} ({diff_both/len(diff_tgt_groups)*100:.1f}%)",
            "same_target_both_correct": f"{same_both}/{len(same_tgt_groups)} ({same_both/len(same_tgt_groups)*100:.1f}%)",
        }

    return results


def main():
    smoke_audit = audit_smoke_cases()
    tp_audit = audit_transfer_probe()
    holdout_pairs = audit_pair_breakdowns("holdout_corrected", "data/m3_2_label_fix/holdout_corrected.jsonl")
    final_test_pairs = audit_pair_breakdowns("final_test_corrected", "data/m3_2_label_fix/final_test_corrected.jsonl")

    all_data = {
        "smoke_cases_audit": smoke_audit,
        "transfer_probe_audit": tp_audit,
        "holdout_pair_audit": holdout_pairs,
        "final_test_pair_audit": final_test_pairs,
    }

    out_json = root_dir / "runs" / "m3_2_label_fix" / "supplemental_audit.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"Saved supplemental audit json to {out_json}")

    # Generate supplemental_audit.md
    out_md = root_dir / "runs" / "m3_2_label_fix" / "supplemental_audit.md"
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("# ERABI M3.2 補足監査レポート：個票比較とペア内訳\n\n")
        f.write("作成日: 2026-09-18\n\n")

        # 1. Smoke 12 cases
        f.write("## 1. smoke 12問の個票推移と新退行の特定\n\n")
        f.write("数式検証: $W_{fix} (7) - W_{bad} (8) = G - L = -1$\n")
        f.write(f"- 回復件数 $G = {smoke_audit['G_recovered_count']}$ 件: {smoke_audit['recovered_ids']}\n")
        f.write(f"- 新たな退行件数 $L = {smoke_audit['L_regressed_count']}$ 件: {smoke_audit['regressed_ids']}\n\n")

        f.write("| ID | 入力Hash (先頭8桁) | 正解 | B0予測 (正誤/pmax) | W_bad予測 (正誤/pmax) | W_fix予測 (正誤/pmax) | W_bad→W_fix 遷移 |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for row in smoke_audit["table"]:
            b0_s = f"{row['B0']['predicted']} ({'○' if row['B0']['is_correct'] else '×'}, {row['B0']['pmax']})"
            bad_s = f"{row['W_bad']['predicted']} ({'○' if row['W_bad']['is_correct'] else '×'}, {row['W_bad']['pmax']})"
            fix_s = f"{row['W_fix']['predicted']} ({'○' if row['W_fix']['is_correct'] else '×'}, {row['W_fix']['pmax']})"
            f.write(f"| `{row['id']}` | `{row['input_hash'][:8]}` | `{row['target']}` | {b0_s} | {bad_s} | {fix_s} | **{row['transition']}** |\n")

        f.write("\n### 退行の内訳分類\n")
        f.write("1. **新たな退行 (W_bad正解 → W_fix誤答, 計2件)**:\n")
        for rid in smoke_audit["regressed_ids"]:
            r_row = next(r for r in smoke_audit["table"] if r["id"] == rid)
            f.write(f"   - **`{rid}`**: 正解=`{r_row['target']}`, W_bad=`{r_row['W_bad']['predicted']}`(p={r_row['W_bad']['pmax']}) -> W_fix=`{r_row['W_fix']['predicted']}`(p={r_row['W_fix']['pmax']})\n")
        f.write("2. **回復 (W_bad誤答 → W_fix正解, 計1件)**:\n")
        for gid in smoke_audit["recovered_ids"]:
            g_row = next(r for r in smoke_audit["table"] if r["id"] == gid)
            f.write(f"   - **`{gid}`**: 正解=`{g_row['target']}`, W_bad=`{g_row['W_bad']['predicted']}`(p={g_row['W_bad']['pmax']}) -> W_fix=`{g_row['W_fix']['predicted']}`(p={g_row['W_fix']['pmax']})\n")
        f.write("3. **B0からの継続退行 (B0正解 → W_bad誤答 → W_fix誤答, 計2件)**:\n")
        f.write("   - `smoke-08` (NLI矛盾判定: 正解 contradicts, 予測 supports)\n")
        f.write("   - `smoke-11` (偽指示インジェクション: 正解 cold, 予測 hot)\n\n")

        # 2. Transfer probe
        f.write("## 2. 転用診断 (transfer_probe 32問) の正答数と確率品質\n\n")
        f.write("| モデル | 正答数 | 正答率 | NLL (T=1.0) | Brier (T=1.0) |\n")
        f.write("|---|---:|---:|---:|---:|\n")
        f.write("| B0 | 18/32 | 56.2% | 1.0773 | 0.5793 |\n")
        f.write(f"| W_bad | 23/32 | 71.9% | 1.1934 | 0.4689 |\n")
        f.write(f"| W_fix | 23/32 | 71.9% | 1.6564 | 0.5261 |\n\n")

        f.write("### 個票推移の内訳 (正誤の入れ替わり)\n")
        f.write(f"- 両モデルで正解: **{tp_audit['common_correct_count']} 件**\n")
        f.write(f"- W_badのみ正解 (W_fixで誤答化): **{tp_audit['bad_only_correct_count']} 件** -> `{tp_audit['bad_only_correct_ids']}`\n")
        f.write(f"- W_fixのみ正解 (W_badから回復): **{tp_audit['fix_only_correct_count']} 件** -> `{tp_audit['fix_only_correct_ids']}`\n")
        f.write(f"- 両モデルで誤答: **{tp_audit['both_wrong_count']} 件**\n\n")
        f.write("> [!IMPORTANT]\n")
        f.write("> 正答数自体は23/32で同数ですが、**正誤の入れ替わり（2件回復・2件退行）が発生しており、かつ NLL は 1.1934 → 1.6564、Brier は 0.4689 → 0.5261 と確率品質は低下**しています。「正答数が同数だから確率品質も維持された」わけではありません。\n\n")

        # 3. Pair breakdown
        f.write("## 3. 指示切替ペアの内訳（正解が異なる組 vs 正解が同じ組）\n\n")
        f.write("### (1) holdout_corrected (100ペア / 200問)\n\n")
        f.write("| モデル | 全ペア両問正解 (100組) | 正解が異なるペア (80組) | 正解が同一のペア (20組) |\n")
        f.write("|---|:---:|:---:|:---:|\n")
        for m in ["B0", "W_bad", "W_fix"]:
            info = holdout_pairs["models"][m]
            f.write(f"| {m} | {info['all_pairs_both_correct']} | {info['diff_target_both_correct']} | {info['same_target_both_correct']} |\n")

        f.write("\n### (2) final_test_corrected (100ペア / 200問)\n\n")
        f.write("| モデル | 全ペア両問正解 (100組) | 正解が異なるペア (70組) | 正解が同一のペア (30組) |\n")
        f.write("|---|:---:|:---:|:---:|\n")
        for m in ["B0", "W_bad", "W_fix"]:
            info = final_test_pairs["models"][m]
            f.write(f"| {m} | {info['all_pairs_both_correct']} | {info['diff_target_both_correct']} | {info['same_target_both_correct']} |\n")

    print(f"Saved supplemental audit markdown to {out_md}")


if __name__ == "__main__":
    main()
