"""M4.4-R Targeted Retention Replay Data Preparation Script for ERABI.

Extracts targeted retention replay samples exclusively from data/m3_3_v2/train.jsonl:
1. R1 (Equality Boundary): actual == threshold, 24 groups = 48 cases
2. R2 (Composite Logic): 4-state balanced (HP < thresh, item_has), 7 groups each = 28 groups = 56 cases
Total replay: 52 groups = 104 cases (<= 160 case cap).

Builds combined_train_retention.jsonl:
- 600 M3 base train
- 240 M4.1 exception train
- 240 M4.3.1 phrasing train
- 104 retention replay
Total = 1184 cases.

Outputs:
- data/m4_4_retention/combined_train_retention.jsonl
- data/m4_4_retention/retention_manifest.json
- runs/m4_4_retention/retention_source_audit.json
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
M3_TRAIN = ROOT / "data/m3_3_v2/train.jsonl"
M4_1_TRAIN = ROOT / "data/m4_1_exception/train_exception.jsonl"
M4_3_1_TRAIN = ROOT / "data/m4_3_1_phrasing_fix/phrasing_train.jsonl"

OUT_DATA_DIR = ROOT / "data/m4_4_retention"
OUT_RUN_DIR = ROOT / "runs/m4_4_retention"
OUT_DATA_DIR.mkdir(parents=True, exist_ok=True)
OUT_RUN_DIR.mkdir(parents=True, exist_ok=True)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def extract_retention_candidates() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    m3_records = [json.loads(line) for line in open(M3_TRAIN, encoding="utf-8") if line.strip()]

    # 1. R1: Equality Boundary
    boundary_groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in m3_records:
        if r.get("rule_kind") == "boundary":
            boundary_groups.setdefault(r["group_id"], []).append(r)

    r1_groups: List[Tuple[str, List[Dict[str, Any]]]] = []
    for gid, pair in sorted(boundary_groups.items()):
        if len(pair) == 2:
            ctx = pair[0]["context"]
            q = pair[0]["question"]
            nums_ctx = [int(x) for x in re.findall(r"\d+", ctx)]
            nums_q = [int(x) for x in re.findall(r"\d+", q)]
            if nums_ctx and nums_q and nums_ctx[0] == nums_q[0]:
                r1_groups.append((gid, pair))

    r1_records = [r for gid, pair in r1_groups for r in pair]

    # 2. R2: Composite Logic (4-state balanced)
    composite_groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in m3_records:
        if r.get("rule_kind") == "composite_logic":
            composite_groups.setdefault(r["group_id"], []).append(r)

    state_groups: Dict[Tuple[bool, bool], List[Tuple[str, List[Dict[str, Any]]]]] = {
        (True, False): [],
        (True, True): [],
        (False, True): [],
        (False, False): [],
    }

    for gid, pair in sorted(composite_groups.items()):
        if len(pair) == 2:
            ctx = pair[0]["context"]
            q1 = pair[0]["question"]
            hp_val = int(re.search(r"HPは(\d+)", ctx).group(1))
            item_has = "回復アイテムあり" in ctx
            thresh = int(re.search(r"HPが(\d+)未満", q1).group(1))
            hp_cond = (hp_val < thresh)
            st = (hp_cond, item_has)
            state_groups[st].append((gid, pair))

    # Balance 4 states: take 7 groups from each state
    TARGET_PER_STATE = 7
    r2_groups: List[Tuple[str, List[Dict[str, Any]]]] = []
    r2_state_breakdown = {}

    for st in [(True, False), (True, True), (False, True), (False, False)]:
        available = state_groups[st]
        selected = available[:TARGET_PER_STATE]
        r2_groups.extend(selected)
        r2_state_breakdown[f"HP_{st[0]}_item_{st[1]}"] = {
            "available_groups": len(available),
            "available_cases": len(available) * 2,
            "selected_groups": len(selected),
            "selected_cases": len(selected) * 2,
            "selected_group_ids": [gid for gid, _ in selected],
        }

    r2_records = [r for gid, pair in r2_groups for r in pair]

    all_replay_records = r1_records + r2_records

    audit_info = {
        "m3_total_train_records": len(m3_records),
        "r1_equality_boundary": {
            "description": "actual == threshold boundary comparison pairs",
            "total_groups": len(r1_groups),
            "total_cases": len(r1_records),
            "group_ids": [gid for gid, _ in r1_groups],
        },
        "r2_composite_logic": {
            "description": "4-state balanced composite logic pairs (HP < thresh, item_has)",
            "total_groups": len(r2_groups),
            "total_cases": len(r2_records),
            "states": r2_state_breakdown,
        },
        "total_replay_groups": len(r1_groups) + len(r2_groups),
        "total_replay_cases": len(all_replay_records),
        "replay_cap": 160,
        "is_under_cap": len(all_replay_records) <= 160,
    }

    return all_replay_records, audit_info


def main():
    print("=== ERABI M4.4-R Retention Replay Data Preparation ===")
    replay_records, audit_info = extract_retention_candidates()
    print(f"Extracted R1 (Equality Boundary): {audit_info['r1_equality_boundary']['total_cases']} cases ({audit_info['r1_equality_boundary']['total_groups']} groups)")
    print(f"Extracted R2 (Composite Logic):   {audit_info['r2_composite_logic']['total_cases']} cases ({audit_info['r2_composite_logic']['total_groups']} groups)")
    print(f"Total Replay:                     {len(replay_records)} cases (Cap: <= 160)")

    # Load base train files
    m3_train = [json.loads(l) for l in open(M3_TRAIN, encoding="utf-8") if l.strip()]
    m4_1_train = [json.loads(l) for l in open(M4_1_TRAIN, encoding="utf-8") if l.strip()]
    m4_3_1_train = [json.loads(l) for l in open(M4_3_1_TRAIN, encoding="utf-8") if l.strip()]

    print(f"\nBase M3 train:        {len(m3_train)} cases")
    print(f"Base M4.1 train:      {len(m4_1_train)} cases")
    print(f"Base M4.3.1 train:    {len(m4_3_1_train)} cases")
    print(f"Retention replay:     {len(replay_records)} cases")

    # Combine all
    combined_train = m3_train + m4_1_train + m4_3_1_train + replay_records
    print(f"Combined train total: {len(combined_train)} cases (Cap: <= 1240)")

    # Write combined train
    out_train_path = OUT_DATA_DIR / "combined_train_retention.jsonl"
    with open(out_train_path, "w", encoding="utf-8") as f:
        for r in combined_train:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Saved combined train to {out_train_path}")

    # Build manifest
    source_counts = {}
    for r in combined_train:
        cid = r["id"]
        source_counts[cid] = source_counts.get(cid, 0) + 1

    replayed_source_ids = {cid: cnt for cid, cnt in source_counts.items() if cnt > 1}

    manifest = {
        "dataset_name": "m4_4_retention_combined_train",
        "description": "Combined training set with targeted M3 retention replay",
        "base_components": {
            "m3_train": {"path": str(M3_TRAIN), "count": len(m3_train)},
            "m4_1_train": {"path": str(M4_1_TRAIN), "count": len(m4_1_train)},
            "m4_3_1_train": {"path": str(M4_3_1_TRAIN), "count": len(m4_3_1_train)},
            "retention_replay": {"count": len(replay_records)},
        },
        "total_records": len(combined_train),
        "unique_records": len(source_counts),
        "replayed_records_count": len(replayed_source_ids),
        "replayed_records_multiplicity": 2,
        "replayed_ids": sorted(list(replayed_source_ids.keys())),
        "combined_train_sha256": sha256_file(out_train_path),
    }

    manifest_path = OUT_DATA_DIR / "retention_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"Saved manifest to {manifest_path}")

    # Write audit info
    audit_path = OUT_RUN_DIR / "retention_source_audit.json"
    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump(audit_info, f, indent=2, ensure_ascii=False)
    print(f"Saved retention source audit to {audit_path}")


if __name__ == "__main__":
    main()
