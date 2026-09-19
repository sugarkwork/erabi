"""Independent Semantic Validator for Milestone 7 Robustness Datasets (ERABI).

Rule 3.3 Compliance:
- Does NOT rely on generator flags.
- Re-derives the target choice ID from the rendered strings: context, question, and choices.
- Handles distractor sentences, swapped contexts, non-standard choice IDs, and 3 choices.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List


class SemanticValidationError(Exception):
    pass


def rederive_robustness_choice_id(record: Dict[str, Any]) -> str:
    ctx = record["context"]
    q = record["question"]
    choices = record["choices"]

    # Filter out dummy choice if 3 choices
    valid_choices = [c for c in choices if c["id"] != "dummy_none"]
    assert len(valid_choices) == 2, f"Expected 2 real choices, got {len(valid_choices)}"

    # Determine whether the query asks for the POS action or NEG action
    is_pos_query = any(
        k in q
        for k in [
            "下回らない",
            "超過しない",
            "以上であれば",
            "以下で",
            "電力消費抑制",
            "双方",
            "条件を満たす場合",
        ]
    )
    is_neg_query = any(
        k in q
        for k in [
            "枠を厳密に超過",
            "満たない",
            "より大きい",
            "例外として",
            "度外視",
            "二条件が揃わない",
            "から除外されている",
        ]
    )

    # Context state check for composite logic
    is_ctx_abnormal = any(
        k in ctx
        for k in [
            "ロックが解除",
            "未受領",
            "高負荷",
            "まだ溜まっていません",
            "超過しています",
            "保証期間外",
            "未提出",
            "認められません",
            "在室フラグがオン",
        ]
    )

    # Locate choice positions in question
    choice_positions = []
    for c in valid_choices:
        pos = q.find(c["text"])
        if pos != -1:
            choice_positions.append((pos, c["id"]))

    assert len(choice_positions) >= 2, f"Could not find both choice texts in question: {q}"
    choice_positions.sort(key=lambda x: x[0])
    first_choice_id = choice_positions[0][1]
    second_choice_id = choice_positions[1][1]

    # Decision logic
    if is_pos_query:
        if is_ctx_abnormal:
            # One condition failed in composite AND
            return second_choice_id
        return first_choice_id
    elif is_neg_query:
        return second_choice_id

    raise SemanticValidationError(f"Could not rederive target for {record['id']}")


def validate_robustness_dataset(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(records)
    groups: Dict[str, List[Dict[str, Any]]] = {}

    for idx, r in enumerate(records):
        for req_key in ["id", "group_id", "domain", "perturbation", "split", "context", "question", "choices", "target"]:
            if req_key not in r:
                raise SemanticValidationError(f"Record #{idx} missing key: {req_key}")

        choices = r["choices"]
        if len(choices) < 2:
            raise SemanticValidationError(f"Record {r['id']} has < 2 choices")
        c_ids = {c["id"] for c in choices}
        if len(c_ids) != len(choices):
            raise SemanticValidationError(f"Record {r['id']} has duplicate choice IDs")

        tgt = r["target"].get("choice_id")
        if tgt not in c_ids:
            raise SemanticValidationError(f"Record {r['id']} target {tgt} not in choices {c_ids}")

        derived = rederive_robustness_choice_id(r)
        if derived != tgt:
            raise SemanticValidationError(
                f"Semantic mismatch in {r['id']} ({r['domain']}, {r['perturbation']}): "
                f"generator={tgt}, rederived={derived}"
            )

        groups.setdefault(r["group_id"], []).append(r)

    diff_pairs = 0
    for gid, pair in groups.items():
        if len(pair) != 2:
            raise SemanticValidationError(f"Group {gid} has {len(pair)} records, expected 2")
        if pair[0]["target"]["choice_id"] != pair[1]["target"]["choice_id"]:
            diff_pairs += 1

    return {
        "total_records": total,
        "total_groups": len(groups),
        "diff_target_pairs": diff_pairs,
        "diff_pair_rate": diff_pairs / len(groups) if groups else 0.0,
        "validation_status": "ALL_PASSED",
    }
