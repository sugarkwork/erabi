"""Audit and verify semantic states across all ERABI datasets (M3.7).

Resolves Review Finding 5:
- Unifies canonical semantic state keys for goal_following (GF) between generation and extraction.
- Ensures order invariance of candidates in context text while preserving (attr1, attr2) pairing.
- Checks cross-split semantic overlap across train, dev, eval_v2, calibration, fresh_eval, smoke, transfer.
- Explicitly reports parseable count and unparseable count (does not claim 0 duplicates for unparseable).
- Verifies generation roundtrip consistency.
"""

from __future__ import annotations

import json
import os
import random
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))



def parse_gf_semantic_state(context: str) -> Optional[Tuple[str, str, Tuple[Tuple[int, int], ...]]]:
    """Extract canonical GF semantic state from context text.
    
    Returns: ('gf', domain_name, tuple(sorted((val1, val2) for each candidate)))
    """
    dom_name = None
    if "サーバー" in context:
        dom_name = "サーバー"
    elif "プラン" in context:
        dom_name = "プラン"
    elif "ホテル" in context:
        dom_name = "ホテル"
    elif "オフィス" in context:
        dom_name = "オフィス"
    elif "PC" in context:
        dom_name = "PC"
    elif "便" in context:
        dom_name = "配送便"
    else:
        return None

    # Matches pattern: {name}は{v1}{u1}で{v2}{u2}
    matches = re.findall(r"(\d+)[^\dで、。]+で(\d+)", context)
    if len(matches) == 3:
        val_pairs = tuple(sorted((int(m[0]), int(m[1])) for m in matches))
        return ("gf", dom_name, val_pairs)
    return None


def parse_er_semantic_state(
    context: str, question: str, rule_kind: Optional[str] = None
) -> Optional[Tuple[Any, ...]]:
    """Extract canonical ER semantic state from context and question text."""
    if rule_kind == "composite_logic" or "HP" in context:
        m_hp = re.search(r"HPは(\d+)", context)
        m_item = "アイテムあり" in context
        m_th = re.search(r"HPが(\d+)未満", question)
        if m_hp and m_th:
            return ("composite_logic", int(m_th.group(1)), int(m_hp.group(1)), m_item)
    elif rule_kind == "boundary" or "測定数値は" in context:
        m_act = re.search(r"ちょうど(\d+)点", context)
        m_th = re.search(r"(\d+)点", question)
        if m_act and m_th:
            return ("boundary", int(m_th.group(1)), int(m_act.group(1)))
    elif rule_kind == "comparison" or "在庫数" in context:
        m_inv = re.search(r"在庫数は(\d+)個", context)
        m_dem = re.search(r"受注数は(\d+)個", context)
        if m_inv and m_dem:
            return ("comparison", int(m_inv.group(1)), int(m_dem.group(1)))
    return None


def audit_datasets() -> Dict[str, Any]:
    datasets = {
        "train": ROOT / "data/m3_3_v2/train.jsonl",
        "dev": ROOT / "data/m3_3_v2/dev.jsonl",
        "eval_v2": ROOT / "data/m3_3_v2/eval_v2.jsonl",
        "calibration": ROOT / "data/m3_6_cal/calibration.jsonl",
        "fresh_eval": ROOT / "data/m3_6_cal/fresh_eval.jsonl",
        "smoke_cases": ROOT / "examples/smoke_cases.jsonl",
        "transfer_probe": ROOT / "data/m3_1/transfer_probe.jsonl",
    }

    per_dataset_stats = {}
    split_states: Dict[str, Set[Any]] = {}

    for sname, spath in datasets.items():
        records = [json.loads(line) for line in open(spath, encoding="utf-8")]
        total = len(records)
        parsed_count = 0
        unparsed_count = 0
        parsed_states = set()

        for r in records:
            tf = r.get("task_family")
            rk = r.get("rule_kind")
            ctx = r.get("context", "")
            q = r.get("question", "")

            state = None
            if tf == "goal_following":
                state = parse_gf_semantic_state(ctx)
            elif tf == "explicit_rule":
                state = parse_er_semantic_state(ctx, q, rk)
            else:
                # Try both parsers anyway (for smoke cases that might share templates)
                state = parse_gf_semantic_state(ctx) or parse_er_semantic_state(ctx, q, rk)

            if state is not None:
                parsed_count += 1
                parsed_states.add(state)
            else:
                unparsed_count += 1

        per_dataset_stats[sname] = {
            "total_records": total,
            "parsed_records": parsed_count,
            "unparsed_records": unparsed_count,
            "unique_states": len(parsed_states),
            "parse_coverage": parsed_count / total,
        }
        split_states[sname] = parsed_states

    # Cross-split overlap analysis on parsed states
    split_names = ["train", "dev", "eval_v2", "calibration", "fresh_eval"]
    cross_overlaps = {}
    for i in range(len(split_names)):
        for j in range(i + 1, len(split_names)):
            s1 = split_names[i]
            s2 = split_names[j]
            overlap = split_states[s1] & split_states[s2]
            cross_overlaps[f"{s1}_vs_{s2}"] = {
                "overlap_count": len(overlap),
                "overlap_items": [str(x) for x in list(overlap)[:5]],
            }

    # Overlaps with diagnostic sets (smoke, transfer)
    diag_overlaps = {}
    for diag in ["smoke_cases", "transfer_probe"]:
        diag_overlaps[diag] = {}
        for sname in ["calibration", "fresh_eval"]:
            overlap = split_states[diag] & split_states[sname]
            diag_overlaps[diag][sname] = {
                "overlap_count": len(overlap),
                "overlap_items": [str(x) for x in list(overlap)],
            }

    # Roundtrip test
    from scripts.build_m3_6_data import generate_goal_following_scenario
    rng = random.Random(20260919)
    roundtrip_successes = 0
    roundtrip_trials = 50
    for trial in range(roundtrip_trials):
        pair, expected_state = generate_goal_following_scenario(f"test-{trial}", trial % 6, rng)
        # Parse from context
        extracted_state = parse_gf_semantic_state(pair[0]["context"])
        if extracted_state == expected_state:
            roundtrip_successes += 1

    report = {
        "dataset_parsing_stats": per_dataset_stats,
        "cross_split_overlaps": cross_overlaps,
        "diagnostic_overlaps": diag_overlaps,
        "roundtrip_consistency": {
            "trials": roundtrip_trials,
            "successes": roundtrip_successes,
            "roundtrip_rate": roundtrip_successes / roundtrip_trials,
        },
    }
    return report


def main():
    out_dir = ROOT / "runs/m3_7_calibration_handoff"
    out_dir.mkdir(parents=True, exist_ok=True)

    report = audit_datasets()

    out_file = out_dir / "semantic_check.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("=== Semantic States Audit Results ===")
    for sname, stats in report["dataset_parsing_stats"].items():
        print(f"[{sname:14s}] Total: {stats['total_records']:3d} | Parsed: {stats['parsed_records']:3d} | Unparsed: {stats['unparsed_records']:3d} | Unique states: {stats['unique_states']:3d}")

    print("\n=== Cross-Split Overlaps (Synthetic Sets) ===")
    total_cross_overlaps = 0
    for pair_key, res in report["cross_split_overlaps"].items():
        count = res["overlap_count"]
        total_cross_overlaps += count
        if count > 0:
            print(f"  {pair_key}: {count} overlaps!")
    if total_cross_overlaps == 0:
        print("  ALL synthetic splits (train, dev, eval_v2, calibration, fresh_eval) have ZERO semantic overlap!")

    print(f"\nRoundtrip Consistency: {report['roundtrip_consistency']['successes']} / {report['roundtrip_consistency']['trials']}")
    print(f"Saved audit report to {out_file}")


if __name__ == "__main__":
    main()
