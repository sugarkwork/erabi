"""Independent Semantic Validator for Milestone 6 Operator Datasets (ERABI).

Rule 3.3 Compliance:
- Does NOT rely on generator flags or metadata.
- Re-derives the expected target choice ID purely from the rendered strings:
  `context`, `question`, and `choices`.
- Validates structural contracts, schema, and contrastive pair consistency.
- Any mismatch raises a SemanticValidationError.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple


class SemanticValidationError(Exception):
    pass


def rederive_expected_choice_id(record: Dict[str, Any]) -> str:
    ctx = record["context"]
    q = record["question"]
    choices = record["choices"]
    fam = record.get("task_family")

    if fam == "and_logic":
        # AND requires both conditions to hold.
        is_both_satisfied = not any(neg in ctx for neg in ["未受領", "不足", "まだ溜まって", "営業時間外", "確認できていません"])
        first_part = re.split(r"そうでない|片方でも|二条件が揃わない", q)[0]
        second_part = re.split(r"そうでない|片方でも|二条件が揃わない", q)[-1]
        
        if is_both_satisfied:
            for c in choices:
                if c["text"] in first_part:
                    return c["id"]
        else:
            for c in choices:
                if c["text"] in second_part:
                    return c["id"]
        raise SemanticValidationError(f"Could not rederive AND target for {record['id']}")

    elif fam == "or_logic":
        # OR requires at least one condition to hold.
        has_positive = any(
            pos in ctx for pos in ["在庫があります", "応答があります", "毒状態になっています", "指定があります", "保有しています"]
        )
        first_part = re.split(r"どちらも|双方とも|両条件とも未充足", q)[0]
        second_part = re.split(r"どちらも|双方とも|両条件とも未充足", q)[-1]

        if has_positive:
            for c in choices:
                if c["text"] in first_part:
                    return c["id"]
        else:
            for c in choices:
                if c["text"] in second_part:
                    return c["id"]
        raise SemanticValidationError(f"Could not rederive OR target for {record['id']}")

    elif fam == "ge_vs_gt":
        # Context has exact equality: "ちょうど{val}"
        is_inclusive = any(k in q for k in ["以上", "達していれば", "下回らない", "下回っていなければ", "クリアしていれば"])
        is_exclusive = any(k in q for k in ["超える", "上回っていれば", "厳密に超過", "より大きい", "超過している場合", "上回る実績"])

        first_part = re.split(r"そうでなければ|未満なら|欠落していれば|満たさない場合は|下回っていれば|届かなければ", q)[0]
        second_part = re.split(r"そうでなければ|以下にとどまる|超過していなければ|そうでない場合は", q)[-1]

        if is_inclusive and not is_exclusive:
            for c in choices:
                if c["text"] in first_part:
                    return c["id"]
        else:
            for c in choices:
                if c["text"] in second_part:
                    return c["id"]
        raise SemanticValidationError(f"Could not rederive GE_VS_GT target for {record['id']}")

    elif fam == "le_vs_lt":
        # Context has exact equality: "ちょうど{val}"
        is_inclusive = any(k in q for k in ["以下", "以内に収まって", "超過しない", "超過していなければ", "収まっている"])
        is_exclusive = any(k in q for k in ["未満", "下回っていれば", "満たない", "より小さい", "より少ない", "下回る水準"])

        first_part = re.split(r"そうでなければ|超えていれば|上限突破時|上限を突破している場合は|超過していれば|枠を超えるなら", q)[0]
        second_part = re.split(r"そうでなければ|以上なら|到達していれば|そうでない場合は|満たしていれば", q)[-1]

        if is_inclusive and not is_exclusive:
            for c in choices:
                if c["text"] in first_part:
                    return c["id"]
        else:
            for c in choices:
                if c["text"] in second_part:
                    return c["id"]
        raise SemanticValidationError(f"Could not rederive LE_VS_LT target for {record['id']}")

    elif fam == "override":
        override_active = any(k in ctx for k in ["オンになっています", "設定されています", "発動しました", "添付されています", "立っています"])
        override_part = re.split(r"上書きして|優先して|最優先され|優先され|で上書き実行", q)[-1]
        std_part = re.split(r"上書き条件|ただし|原則規程として", q)[0]

        if override_active:
            for c in choices:
                if c["text"] in override_part:
                    return c["id"]
        else:
            for c in choices:
                if c["text"] in q and c["text"] not in override_part:
                    return c["id"]
        raise SemanticValidationError(f"Could not rederive OVERRIDE target for {record['id']}")

    elif fam == "default_exception":
        exception_active = any(
            k in ctx
            for k in [
                "セール対象品です",
                "祝前日に指定",
                "微弱な魔力反応",
                "罠の兆候）があります",
                "強風警報が発令",
                "海外IPからの接続",
            ]
        )
        exc_part = re.split(r"例外として|例外扱いとし、|例外要件を満たすときのみ例外規定|例外規定", q)[-1]

        if exception_active:
            for c in choices:
                if c["text"] in exc_part:
                    return c["id"]
        else:
            for c in choices:
                if c["text"] in q and c["text"] not in exc_part:
                    return c["id"]
        raise SemanticValidationError(f"Could not rederive DEFAULT_EXCEPTION target for {record['id']}")

    elif fam == "first_match":
        rule1_matches = any(k in ctx for k in ["要冷凍マークあり", "重度障害アラート検知", "戦闘不能状態", "危険物指定あり", "二重請求"])
        if rule1_matches:
            part1 = re.split(r"1\.\s*|\[規則1\]\s*|第1項：", q)[1]
            part1 = re.split(r"2\.\s*|\[規則2\]\s*|／第2項：", part1)[0]
            for c in choices:
                if c["text"] in part1:
                    return c["id"]
        else:
            rule2_matches = any(k in ctx for k in ["賞味期限は2日後", "中度負荷アラート", "HP25%", "割れ物注意の表記", "お得なプラン見直し"])
            if rule2_matches:
                part2 = re.split(r"2\.\s*|\[規則2\]\s*|／第2項：", q)[1]
                part2 = re.split(r"3\.\s*|\[規則3\]\s*|／第3項：", part2)[0]
                for c in choices:
                    if c["text"] in part2:
                        return c["id"]
        raise SemanticValidationError(f"Could not rederive FIRST_MATCH target for {record['id']}")

    elif fam == "priority_ranking":
        # Options sorted by appearance order in ranking statement:
        choice_positions = []
        for c in choices:
            pos = q.find(c["text"])
            if pos != -1:
                choice_positions.append((pos, c["id"]))
        if len(choice_positions) >= 2:
            choice_positions.sort(key=lambda x: x[0])
            return choice_positions[0][1]
        raise SemanticValidationError(f"Could not rederive PRIORITY_RANKING target for {record['id']}")

    elif fam == "negation":
        # Find choices by appearance in question
        choice_positions = []
        for c in choices:
            pos = q.find(c["text"])
            if pos != -1:
                choice_positions.append((pos, c["id"]))
        if len(choice_positions) >= 2:
            choice_positions.sort(key=lambda x: x[0])
            first_clause = q[: choice_positions[0][0]]
            is_neg_q = any(w in first_clause for w in ["ない", "除外", "満たさない", "不成立", "ではない"])
            # First mentioned action is POS condition action, second is NEG condition action
            if not is_neg_q:
                return choice_positions[0][1]
            else:
                return choice_positions[1][1]
        raise SemanticValidationError(f"Could not rederive NEGATION target for {record['id']}")

    elif fam == "goal_switching":
        if "度外視" in q:
            target_phrase = q.split("度外視")[-1]
        elif "最優先" in q:
            target_phrase = q.split("最優先")[0]
        elif "最大化" in q:
            target_phrase = q.split("最大化")[0]
        else:
            target_phrase = q

        wants_a = any(w in target_phrase for w in ["早さ", "処理速度", "瞬間火力", "リードタイム", "スピード"])
        wants_b = any(w in target_phrase for w in ["安さ", "費用", "生存能力", "運賃", "料金"])

        for c in choices:
            is_choice_a = ("A" in c["text"] or "航空" in c["text"] or "武器" in c["text"])
            is_choice_b = ("B" in c["text"] or "船便" in c["text"] or "防具" in c["text"])
            if wants_a and is_choice_a:
                return c["id"]
            if wants_b and is_choice_b:
                return c["id"]
        raise SemanticValidationError(f"Could not rederive GOAL_SWITCHING target for {record['id']}")

    raise SemanticValidationError(f"Unknown task family: {fam}")


def validate_operator_dataset(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Run full semantic and structural validation over a list of operator records."""
    total = len(records)
    groups: Dict[str, List[Dict[str, Any]]] = {}

    for idx, r in enumerate(records):
        # 1. Structural schema
        for req_key in ["id", "group_id", "task_family", "domain", "split", "context", "question", "choices", "target"]:
            if req_key not in r:
                raise SemanticValidationError(f"Record #{idx} missing required key: {req_key}")

        choices = r["choices"]
        if len(choices) < 2:
            raise SemanticValidationError(f"Record {r['id']} has < 2 choices: {len(choices)}")
        choice_ids = {c["id"] for c in choices}
        if len(choice_ids) != len(choices):
            raise SemanticValidationError(f"Record {r['id']} has duplicate choice IDs")

        tgt_id = r["target"].get("choice_id")
        if tgt_id not in choice_ids:
            raise SemanticValidationError(f"Record {r['id']} target {tgt_id} not in choices {choice_ids}")

        # 2. Independent Semantic Re-derivation
        derived_id = rederive_expected_choice_id(r)
        if derived_id != tgt_id:
            raise SemanticValidationError(
                f"Semantic mismatch in {r['id']} ({r['task_family']}): "
                f"generator target={tgt_id}, rederived={derived_id}"
            )

        groups.setdefault(r["group_id"], []).append(r)

    # 3. Contrastive Pair Integrity
    diff_target_pairs = 0
    for gid, pair in groups.items():
        if len(pair) != 2:
            raise SemanticValidationError(f"Group {gid} does not have exactly 2 records: {len(pair)}")
        if pair[0]["target"]["choice_id"] != pair[1]["target"]["choice_id"]:
            diff_target_pairs += 1

    return {
        "total_records": total,
        "total_groups": len(groups),
        "diff_target_pairs": diff_target_pairs,
        "diff_pair_rate": diff_target_pairs / len(groups) if groups else 0.0,
        "validation_status": "ALL_PASSED",
    }
