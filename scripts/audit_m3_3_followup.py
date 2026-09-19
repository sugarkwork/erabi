"""Comprehensive audit and followup analysis script for ERABI M3.3.

Implements all analyses requested in ERABI_M3_3_FOLLOWUP.md:
1. File hashes and record count verification (3x(200+12+32)=732 predictions).
2. Detailed 47 diff-target pair analysis (pred_same vs pred_diff, error breakdown, task_family/rule_kind breakdown).
3. Representative transition examples (W_fix correct -> W_v2 fail, and vice versa).
4. Second attribute shortcut breakdown (case1 attr1 question vs case2 attr2 question).
5. Boundary keyword shortcut breakdown (below, at, above states vs theoretical baseline).
6. Split overlap and context collision verification.
7. Uniform baseline and confidence calibration bins.
8. Output pair_details.jsonl and diagnostic_summary.json.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent


def compute_file_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_jsonl(filepath: Path) -> List[Dict[str, Any]]:
    with open(filepath, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    print("=== Running M3.3 Followup Audit ===")

    # 1. File verification and SHA256 hashes
    target_files = [
        ROOT_DIR / "data" / "m3_3_v2" / "train.jsonl",
        ROOT_DIR / "data" / "m3_3_v2" / "dev.jsonl",
        ROOT_DIR / "data" / "m3_3_v2" / "eval_v2.jsonl",
        ROOT_DIR / "examples" / "smoke_cases.jsonl",
        ROOT_DIR / "data" / "m3_1" / "transfer_probe.jsonl",
        ROOT_DIR / "runs" / "m3_3_v2" / "comparisons" / "B0_eval_v2_predictions.jsonl",
        ROOT_DIR / "runs" / "m3_3_v2" / "comparisons" / "B0_smoke_cases_predictions.jsonl",
        ROOT_DIR / "runs" / "m3_3_v2" / "comparisons" / "B0_transfer_probe_predictions.jsonl",
        ROOT_DIR / "runs" / "m3_3_v2" / "comparisons" / "W_fix_eval_v2_predictions.jsonl",
        ROOT_DIR / "runs" / "m3_3_v2" / "comparisons" / "W_fix_smoke_cases_predictions.jsonl",
        ROOT_DIR / "runs" / "m3_3_v2" / "comparisons" / "W_fix_transfer_probe_predictions.jsonl",
        ROOT_DIR / "runs" / "m3_3_v2" / "comparisons" / "W_v2_eval_v2_predictions.jsonl",
        ROOT_DIR / "runs" / "m3_3_v2" / "comparisons" / "W_v2_smoke_cases_predictions.jsonl",
        ROOT_DIR / "runs" / "m3_3_v2" / "comparisons" / "W_v2_transfer_probe_predictions.jsonl",
    ]

    file_hashes = {}
    for fp in target_files:
        if fp.exists():
            file_hashes[fp.relative_to(ROOT_DIR).as_posix()] = {
                "sha256": compute_file_sha256(fp),
                "size_bytes": fp.stat().st_size,
            }
        else:
            file_hashes[fp.relative_to(ROOT_DIR).as_posix()] = "MISSING"

    # Verify prediction counts
    pred_counts = {}
    for mname in ["B0", "W_fix", "W_v2"]:
        for ds in ["eval_v2", "smoke_cases", "transfer_probe"]:
            pfile = ROOT_DIR / "runs" / "m3_3_v2" / "comparisons" / f"{mname}_{ds}_predictions.jsonl"
            lines = load_jsonl(pfile)
            pred_counts[f"{mname}_{ds}"] = len(lines)

    print(f"Prediction counts (expected: 3*(200+12+32)=732 total): {sum(pred_counts.values())} total")

    # Load eval_v2 records and predictions
    eval_records = load_jsonl(ROOT_DIR / "data" / "m3_3_v2" / "eval_v2.jsonl")
    rec_by_id = {r["id"]: r for r in eval_records}

    preds_b0 = {p["id"]: p for p in load_jsonl(ROOT_DIR / "runs" / "m3_3_v2" / "comparisons" / "B0_eval_v2_predictions.jsonl")}
    preds_fix = {p["id"]: p for p in load_jsonl(ROOT_DIR / "runs" / "m3_3_v2" / "comparisons" / "W_fix_eval_v2_predictions.jsonl")}
    preds_v2 = {p["id"]: p for p in load_jsonl(ROOT_DIR / "runs" / "m3_3_v2" / "comparisons" / "W_v2_eval_v2_predictions.jsonl")}

    # Group eval_v2 records into pairs
    groups = defaultdict(list)
    for r in eval_records:
        groups[r["group_id"]].append(r)

    print(f"Total groups in eval_v2: {len(groups)}")

    # 2. Pairwise Analysis (Diff-target vs Same-target)
    pair_details = []
    models = ["B0", "W_fix", "W_v2"]
    model_preds = {"B0": preds_b0, "W_fix": preds_fix, "W_v2": preds_v2}

    pair_stats = {
        "diff_target": {m: {"both_correct": 0, "one_correct": 0, "neither_correct": 0, "pred_same": 0, "pred_diff": 0, "switch_success": 0, "pred_same_failure": 0, "pred_diff_failure": 0} for m in models},
        "same_target": {m: {"both_correct": 0, "one_correct": 0, "neither_correct": 0, "pred_same": 0, "pred_diff": 0, "switch_success": 0, "pred_same_failure": 0, "pred_diff_failure": 0} for m in models},
    }

    # Transition tracking W_fix -> W_v2
    transitions = {
        "diff_target": {"maintained": 0, "recovered": 0, "regressed": 0, "both_failed": 0},
        "same_target": {"maintained": 0, "recovered": 0, "regressed": 0, "both_failed": 0},
    }

    # Breakdown by task_family and rule_kind for diff_target
    diff_by_family = defaultdict(lambda: {m: {"total_pairs": 0, "both_correct": 0, "pred_same": 0, "pred_diff": 0} for m in models})
    diff_transition_by_family = defaultdict(lambda: {"maintained": 0, "recovered": 0, "regressed": 0, "both_failed": 0})

    for gid in sorted(groups.keys()):
        recs = groups[gid]
        assert len(recs) == 2, f"Group {gid} has {len(recs)} records, expected 2"
        r1, r2 = recs[0], recs[1]
        t1, t2 = r1["target"]["choice_id"], r2["target"]["choice_id"]
        is_diff = (t1 != t2)
        cat_key = "diff_target" if is_diff else "same_target"

        fam_key = r1.get("task_family", "unknown")
        if fam_key == "explicit_rule":
            fam_key = f"explicit_rule:{r1.get('rule_kind', 'unknown')}"

        if is_diff:
            for m in models:
                diff_by_family[fam_key][m]["total_pairs"] += 1

        p_info = {
            "group_id": gid,
            "category": cat_key,
            "task_family": r1.get("task_family"),
            "rule_kind": r1.get("rule_kind"),
            "template_family": r1.get("template_family"),
            "case1_id": r1["id"],
            "case2_id": r2["id"],
            "target1": t1,
            "target2": t2,
            "models": {},
        }

        m_both = {}
        for m in models:
            p1 = model_preds[m][r1["id"]]
            p2 = model_preds[m][r2["id"]]
            pred1 = p1["best_candidate_id"]
            pred2 = p2["best_candidate_id"]
            c1 = (pred1 == t1)
            c2 = (pred2 == t2)
            both = (c1 and c2)
            one = (c1 != c2)
            neither = (not c1 and not c2)
            pred_same = (pred1 == pred2)
            pred_diff = (pred1 != pred2)

            m_both[m] = both

            # Counts
            if both:
                pair_stats[cat_key][m]["both_correct"] += 1
            elif one:
                pair_stats[cat_key][m]["one_correct"] += 1
            else:
                pair_stats[cat_key][m]["neither_correct"] += 1

            if pred_same:
                pair_stats[cat_key][m]["pred_same"] += 1
            else:
                pair_stats[cat_key][m]["pred_diff"] += 1

            if is_diff:
                if both:
                    pair_stats[cat_key][m]["switch_success"] += 1
                else:
                    if pred_same:
                        pair_stats[cat_key][m]["pred_same_failure"] += 1
                    else:
                        pair_stats[cat_key][m]["pred_diff_failure"] += 1

                if both:
                    diff_by_family[fam_key][m]["both_correct"] += 1
                if pred_same:
                    diff_by_family[fam_key][m]["pred_same"] += 1
                else:
                    diff_by_family[fam_key][m]["pred_diff"] += 1

            p_info["models"][m] = {
                "pred1": pred1,
                "pred2": pred2,
                "both_correct": both,
                "correct1": c1,
                "correct2": c2,
                "pred_same": pred_same,
                "p1_choices": p1["choices"],
                "p2_choices": p2["choices"],
            }

        # Transition W_fix -> W_v2
        fix_both = m_both["W_fix"]
        v2_both = m_both["W_v2"]
        if fix_both and v2_both:
            tr = "maintained"
        elif not fix_both and v2_both:
            tr = "recovered"
        elif fix_both and not v2_both:
            tr = "regressed"
        else:
            tr = "both_failed"

        transitions[cat_key][tr] += 1
        if is_diff:
            diff_transition_by_family[fam_key][tr] += 1

        p_info["transition_W_fix_to_W_v2"] = tr
        pair_details.append(p_info)

    # Representatives: Regressed (W_fix correct -> W_v2 failed) and Recovered (W_fix failed -> W_v2 correct)
    regressed_examples = []
    recovered_examples = []
    for pd in pair_details:
        if pd["category"] == "diff_target":
            if pd["transition_W_fix_to_W_v2"] == "regressed" and len(regressed_examples) < 3:
                r1 = rec_by_id[pd["case1_id"]]
                r2 = rec_by_id[pd["case2_id"]]
                regressed_examples.append({
                    "group_id": pd["group_id"],
                    "task_family": pd["task_family"],
                    "rule_kind": pd["rule_kind"],
                    "context": r1["context"],
                    "question1": r1["question"],
                    "question2": r2["question"],
                    "choices": r1["choices"],
                    "target1": pd["target1"],
                    "target2": pd["target2"],
                    "W_fix": pd["models"]["W_fix"],
                    "W_v2": pd["models"]["W_v2"],
                })
            elif pd["transition_W_fix_to_W_v2"] == "recovered" and len(recovered_examples) < 3:
                r1 = rec_by_id[pd["case1_id"]]
                r2 = rec_by_id[pd["case2_id"]]
                recovered_examples.append({
                    "group_id": pd["group_id"],
                    "task_family": pd["task_family"],
                    "rule_kind": pd["rule_kind"],
                    "context": r1["context"],
                    "question1": r1["question"],
                    "question2": r2["question"],
                    "choices": r1["choices"],
                    "target1": pd["target1"],
                    "target2": pd["target2"],
                    "W_fix": pd["models"]["W_fix"],
                    "W_v2": pd["models"]["W_v2"],
                })

    # 3. Second Attribute Shortcut Breakdown on goal_following
    # Split into case1 (asks for attr1, ignores attr2) vs case2 (asks for attr2, ignores attr1)
    gf_cases = [r for r in eval_records if r.get("task_family") == "goal_following"]
    gf_c1 = [r for r in gf_cases if r["id"].endswith("-c1")]
    gf_c2 = [r for r in gf_cases if r["id"].endswith("-c2")]

    def audit_attr_heuristic(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        parse_success = 0
        parse_failed = 0
        min_attr1_correct = 0
        max_attr1_correct = 0
        min_attr2_correct = 0
        max_attr2_correct = 0

        for r in cases:
            ctx = r["context"]
            matches = re.findall(r"([^\s、]+)は(\d+)([^\d]+)で(\d+)([^\d、]+)", ctx)
            if len(matches) == 3:
                parse_success += 1
                c_map = {c["text"]: c["id"] for c in r["choices"]}
                items = {m[0]: (int(m[1]), int(m[3])) for m in matches}

                # min / max for attr1
                min_v1_name = min(items.keys(), key=lambda k: items[k][0])
                max_v1_name = max(items.keys(), key=lambda k: items[k][0])
                # min / max for attr2
                min_v2_name = min(items.keys(), key=lambda k: items[k][1])
                max_v2_name = max(items.keys(), key=lambda k: items[k][1])

                tgt = r["target"]["choice_id"]
                if c_map.get(min_v1_name) == tgt:
                    min_attr1_correct += 1
                if c_map.get(max_v1_name) == tgt:
                    max_attr1_correct += 1
                if c_map.get(min_v2_name) == tgt:
                    min_attr2_correct += 1
                if c_map.get(max_v2_name) == tgt:
                    max_attr2_correct += 1
            else:
                parse_failed += 1

        n = len(cases)
        return {
            "total_cases": n,
            "parse_success": parse_success,
            "parse_failed": parse_failed,
            "min_attr2_accuracy": f"{min_attr2_correct}/{n} ({min_attr2_correct/max(n,1)*100:.1f}%)",
            "max_attr2_accuracy": f"{max_attr2_correct}/{n} ({max_attr2_correct/max(n,1)*100:.1f}%)",
            "min_attr1_accuracy": f"{min_attr1_correct}/{n} ({min_attr1_correct/max(n,1)*100:.1f}%)",
            "max_attr1_accuracy": f"{max_attr1_correct}/{n} ({max_attr1_correct/max(n,1)*100:.1f}%)",
        }

    attr_audit_c1 = audit_attr_heuristic(gf_c1)  # Target is attr1
    attr_audit_c2 = audit_attr_heuristic(gf_c2)  # Target is attr2
    attr_audit_all = audit_attr_heuristic(gf_cases)

    # 4. Boundary Keyword Shortcut Breakdown
    # Split into actual < threshold (below), actual == threshold (at), actual > threshold (above)
    bound_cases = [r for r in eval_records if r.get("rule_kind") == "boundary"]

    bound_breakdown = {
        "below": {"count": 0, "q_le_count": 0, "q_lt_count": 0, "pass_targets": 0, "fail_targets": 0, "kw_shortcut_correct": 0},
        "at": {"count": 0, "q_le_count": 0, "q_lt_count": 0, "pass_targets": 0, "fail_targets": 0, "kw_shortcut_correct": 0},
        "above": {"count": 0, "q_le_count": 0, "q_lt_count": 0, "pass_targets": 0, "fail_targets": 0, "kw_shortcut_correct": 0},
        "unparsed": 0,
    }

    for r in bound_cases:
        ctx = r["context"]
        q = r["question"]
        tgt = r["target"]["choice_id"]

        # Parse actual from context: "測定数値はちょうど{actual}点です。"
        m_act = re.search(r"ちょうど(\d+)点", ctx)
        # Parse threshold from question: "{threshold}点以下" or "{threshold}点未満"
        m_thr = re.search(r"(\d+)点(?:以下|未満)", q)

        if m_act and m_thr:
            actual = int(m_act.group(1))
            threshold = int(m_thr.group(1))

            if actual < threshold:
                state = "below"
            elif actual == threshold:
                state = "at"
            else:
                state = "above"

            b = bound_breakdown[state]
            b["count"] += 1
            is_le = ("以下" in q)
            if is_le:
                b["q_le_count"] += 1
            else:
                b["q_lt_count"] += 1

            if tgt == "pass":
                b["pass_targets"] += 1
            else:
                b["fail_targets"] += 1

            kw_pred = "pass" if is_le else "fail"
            if kw_pred == tgt:
                b["kw_shortcut_correct"] += 1
        else:
            bound_breakdown["unparsed"] += 1

    # 5. Uniform Distribution Baseline on eval_v2
    # Number of choices K per case
    k_list = [len(r["choices"]) for r in eval_records]
    k_counts = defaultdict(int)
    for k in k_list:
        k_counts[k] += 1

    uniform_acc = sum(1.0 / k for k in k_list) / len(k_list)
    uniform_nll = sum(math.log(k) for k in k_list) / len(k_list)
    uniform_brier = sum(1.0 - (1.0 / k) for k in k_list) / len(k_list)

    # 6. Confidence Calibration Bins (pmax bins) on eval_v2
    bins = [
        ("0.00-0.50", 0.0, 0.5),
        ("0.50-0.70", 0.5, 0.7),
        ("0.70-0.90", 0.7, 0.9),
        ("0.90-1.00", 0.9, 1.0001),
    ]

    conf_bins = {m: [] for m in models}
    for m in models:
        for bname, blow, bhigh in bins:
            m_preds = model_preds[m]
            in_bin = []
            for r in eval_records:
                p = m_preds[r["id"]]
                # compute pmax
                pmax = max(c["probability"] for c in p["choices"])
                if blow <= pmax < bhigh:
                    in_bin.append((pmax, p["is_correct"]))

            cnt = len(in_bin)
            avg_pmax = sum(x[0] for x in in_bin) / cnt if cnt > 0 else None
            acc = sum(1 for x in in_bin if x[1]) / cnt if cnt > 0 else None
            conf_bins[m].append({
                "bin": bname,
                "count": cnt,
                "mean_pmax": round(avg_pmax, 4) if avg_pmax is not None else "-",
                "accuracy": round(acc, 4) if acc is not None else "-",
            })

    # 7. Split Overlap & Context Collision Verification
    train_records = load_jsonl(ROOT_DIR / "data" / "m3_3_v2" / "train.jsonl")
    dev_records = load_jsonl(ROOT_DIR / "data" / "m3_3_v2" / "dev.jsonl")

    def get_order_free_fingerprint(r: Dict[str, Any]) -> str:
        norm_ctx = r["context"].strip().lower()
        norm_q = r["question"].strip().lower()
        norm_choices = "###".join(sorted(c["text"].strip().lower() for c in r["choices"]))
        return hashlib.sha256(f"{norm_ctx}|||{norm_q}|||{norm_choices}".encode("utf-8")).hexdigest()

    train_of_fps = {get_order_free_fingerprint(r) for r in train_records}
    dev_of_fps = {get_order_free_fingerprint(r) for r in dev_records}
    eval_of_fps = {get_order_free_fingerprint(r) for r in eval_records}

    of_overlap_train_eval = train_of_fps.intersection(eval_of_fps)
    of_overlap_dev_eval = dev_of_fps.intersection(eval_of_fps)
    of_overlap_train_dev = train_of_fps.intersection(dev_of_fps)

    # 8. Save outputs to runs/m3_3_v2/followup/
    out_dir = ROOT_DIR / "runs" / "m3_3_v2" / "followup"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save pair_details.jsonl
    pair_details_path = out_dir / "pair_details.jsonl"
    with open(pair_details_path, "w", encoding="utf-8") as f:
        for p in pair_details:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    # Build comprehensive diagnostic summary JSON
    diag_summary = {
        "file_hashes": file_hashes,
        "prediction_counts": pred_counts,
        "pair_breakdown": {
            "diff_target_47_pairs": pair_stats["diff_target"],
            "same_target_53_pairs": pair_stats["same_target"],
            "diff_target_by_family": diff_by_family,
            "transitions_W_fix_to_W_v2": transitions,
            "diff_transitions_by_family": diff_transition_by_family,
        },
        "shortcut_heuristics_detailed": {
            "second_attribute": {
                "overall_100_cases": attr_audit_all,
                "case1_asks_attr1_ignore_attr2": attr_audit_c1,
                "case2_asks_attr2_ignore_attr1": attr_audit_c2,
                "note": "case2 asking for attr2 is valid ground truth matching (normal control), while case1 asking for attr1 tests actual shortcut reliance.",
            },
            "boundary_keyword": {
                "states": bound_breakdown,
                "total_boundary_cases": len(bound_cases),
                "theoretical_expectation": "Under uniform below/at/above split with le/lt pairs: below gives 1/2, at gives 2/2, above gives 1/2 -> expected 4/6 = 66.7%",
            },
        },
        "uniform_distribution_baseline": {
            "total_cases": len(eval_records),
            "choice_count_distribution": dict(k_counts),
            "uniform_expected_accuracy": round(uniform_acc, 5),
            "uniform_mean_nll": round(uniform_nll, 5),
            "uniform_mean_brier": round(uniform_brier, 5),
        },
        "confidence_calibration_bins": conf_bins,
        "split_collision_audit": {
            "order_free_fingerprint_overlaps": {
                "train_eval": len(of_overlap_train_eval),
                "dev_eval": len(of_overlap_dev_eval),
                "train_dev": len(of_overlap_train_dev),
            },
        },
        "representative_examples": {
            "regressed_W_fix_correct_to_W_v2_fail": regressed_examples,
            "recovered_W_fix_fail_to_W_v2_correct": recovered_examples,
        },
    }

    diag_summary_path = out_dir / "diagnostic_summary.json"
    with open(diag_summary_path, "w", encoding="utf-8") as f:
        json.dump(diag_summary, f, ensure_ascii=False, indent=2)

    print(f"Saved pair details to {pair_details_path}")
    print(f"Saved diagnostic summary to {diag_summary_path}")
    print("=== M3.3 Followup Audit Completed Successfully ===")


if __name__ == "__main__":
    main()
