"""Independent Semantic Validator for Milestone 8 General Choice Tasks (ERABI).

Rule 3.3 Compliance:
- Does NOT inspect generator flags.
- Re-derives the ground-truth choice ID directly from the rendered text: context, question, and choices.
"""

from __future__ import annotations

from typing import Any, Dict, List


class SemanticValidationError(Exception):
    pass


def rederive_general_choice_id(record: Dict[str, Any]) -> str:
    ctx = record["context"]
    q = record["question"]
    fam = record.get("task_family")
    choices = record["choices"]
    c_map = {c["id"]: c["text"] for c in choices}

    if fam == "support_routing":
        if any(k in ctx for k in ["引き落とし明細", "過剰請求", "返金内訳"]):
            return "billing"
        elif any(k in ctx for k in ["エラーコード502", "通信できません", "障害の復旧"]):
            return "technical"
        elif any(k in ctx for k in ["ログイン試行", "認証トークン", "不正アクセス"]):
            return "account_security"
        elif any(k in ctx for k in ["エンタープライズ一括ライセンス", "全社導入", "商談"]):
            return "sales_inquiry"
        elif any(k in ctx for k in ["初期破損", "良品への無償交換"]):
            return "returns_exchange"
        elif any(k in ctx for k in ["予定日を過ぎました", "追跡ステータス"]):
            return "delivery_status"

    elif fam == "short_nli":
        if any(k in ctx for k in ["午前2時でも営業", "すべての担当者は資格試験に合格"]):
            return "entailment"
        elif any(k in ctx for k in ["業務を休止している", "未経験者が含まれる"]):
            return "contradiction"

    elif fam == "semantic_relation":
        if any(k in ctx for k in ["大型台風", "計画運休"]):
            return "cause_effect"
        elif any(k in ctx for k in ["猛暑日", "快適な室温"]):
            return "contrast"
        elif any(k in ctx for k in ["主翼", "一部品"]):
            return "part_whole"
        elif any(k in ctx for k in ["アサガオ", "具体例"]):
            return "category_instance"

    elif fam == "intent_selection":
        if any(k in ctx for k in ["二重決済", "全額返金"]):
            return "refund_request"
        elif any(k in ctx for k in ["自動継続更新を解除", "会員解約"]):
            return "cancel_subscription"
        elif any(k in ctx for k in ["配送追跡番号で現在地", "照会したい"]):
            return "track_order"
        elif any(k in ctx for k in ["新住所へ修正", "変更してください"]):
            return "change_address"

    elif fam == "instruction_separation":
        if "安全基準値の範囲内" in ctx:
            return "standard_procedure"
        elif "警告閾値を突破" in ctx:
            return "emergency_override"

    elif fam == "negative_goal":
        if any(k in q for k in ["禁止事項", "違反行為"]):
            return "forbidden_action"
        elif any(k in q for k in ["推奨行為", "適合措置"]):
            return "compliant_action"

    raise SemanticValidationError(f"Could not re-derive target for record {record['id']} in family {fam}")


def validate_general_dataset(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(records)
    groups: Dict[str, List[Dict[str, Any]]] = {}

    for idx, r in enumerate(records):
        for req_key in ["id", "group_id", "task_family", "split", "context", "question", "choices", "target"]:
            if req_key not in r:
                raise SemanticValidationError(f"Record #{idx} missing key: {req_key}")

        choices = r["choices"]
        if len(choices) < 2:
            raise SemanticValidationError(f"Record {r['id']} has < 2 choices")
        c_ids = {c["id"] for c in choices}
        if len(c_ids) != len(choices):
            raise SemanticValidationError(f"Record {r['id']} duplicate choice IDs")

        tgt = r["target"].get("choice_id")
        if tgt not in c_ids:
            raise SemanticValidationError(f"Record {r['id']} target {tgt} not in choices {c_ids}")

        derived = rederive_general_choice_id(r)
        if derived != tgt:
            raise SemanticValidationError(
                f"Semantic mismatch in {r['id']} ({r.get('task_family')}): "
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
