"""Independent Semantic Validator for ERABI M4.3.1.

Validates the ground-truth target of a record strictly from its rendered text:
- context
- question
- choices
Does NOT use or share generator internal booleans (cond_a, cond_b).
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple


def identify_domain_from_choices(choices: List[Dict[str, Any]]) -> str:
    """Identify domain uniquely from choice IDs."""
    c_ids = {c["id"] for c in choices}
    if c_ids == {"heal", "continue", "wait"}:
        return "game_action"
    if c_ids == {"standard", "express", "hold"}:
        return "delivery_dispatch"
    if c_ids == {"scale_up", "isolate", "monitor"}:
        return "system_ops"
    if c_ids == {"eco_mode", "emergency_stop", "normal_run"}:
        return "facility_control"
    if c_ids == {"standard_guide", "special_refund", "escalate"}:
        return "customer_service"
    if c_ids == {"pass", "recheck", "hold"}:
        return "manufacturing"
    if c_ids == {"peak_cut", "battery", "normal"}:
        return "facility_power"
    if c_ids == {"fifo_ship", "quarantine", "standard_ship"}:
        return "inventory"
    if c_ids == {"promote_queue", "defer_night", "standard_run"}:
        return "job_scheduler"
    raise ValueError(f"Unknown domain choices: {c_ids}")


DOMAIN_RULES = {
    "game_action": {"rule_a": "HP基準", "rule_b": "移動例外"},
    "delivery_dispatch": {"rule_a": "重量基準", "rule_b": "緊急例外"},
    "system_ops": {"rule_a": "負荷基準", "rule_b": "保安例外"},
    "facility_control": {"rule_a": "温度基準", "rule_b": "安全例外"},
    "customer_service": {"rule_a": "期限基準", "rule_b": "VIP例外"},
    "manufacturing": {"rule_a": "寸法基準", "rule_b": "外観基準"},
    "facility_power": {"rule_a": "買電ピーク基準", "rule_b": "蓄電池基準"},
    "inventory": {"rule_a": "滞留基準", "rule_b": "検疫基準"},
    "job_scheduler": {"rule_a": "待機時間基準", "rule_b": "資源負荷基準"},
}


def _is_rule_a(text: str, domain: str) -> bool:
    rule_a = DOMAIN_RULES[domain]["rule_a"]
    rule_b = DOMAIN_RULES[domain]["rule_b"]
    if rule_a in text and rule_b not in text:
        return True
    if rule_b in text and rule_a not in text:
        return False
    # If both appear or neither, check exact position or fallback
    return rule_a in text


def parse_priority_order_from_question(question: str, domain: str) -> str:
    """Parse whether Rule A takes precedence over Rule B or vice-versa.
    
    Supports:
    - Train Families: E, F, G, H, I, J
    - Dev Families: K, L
    - Fresh Eval Families: M, N, O, P
    - Historical Families: A, B, C, D
    """
    # Family A (historical): ①【最優先】...
    if "①【最優先】" in question:
        m = re.search(r"①【最優先】([^②\n]+)", question)
        if m:
            return "A_over_B" if _is_rule_a(m.group(1), domain) else "B_over_A"

    # Family C (historical): 優先度は A > B or 優先度：A > B
    if " > " in question:
        m_c = re.search(r"優先度(?:は|[：:])\s*(.+?)\s*>\s*(.+?)。", question)
        if m_c:
            return "A_over_B" if _is_rule_a(m_c.group(1), domain) else "B_over_A"

    # Family D (historical): 第一判断 / 例外条件
    if "例外条件" in question:
        m_d = re.search(r"例外条件[：:]([^\s（(]+)", question)
        if m_d:
            return "A_over_B" if _is_rule_a(m_d.group(1), domain) else "B_over_A"

    # Family B (historical): Aを優先 / Bを優先
    if "を優先" in question and "判断方針として" not in question and "より優先する" not in question:
        m_b = re.search(r"(?:成立した場合は|成立時は|同時成立時は|の場合は|場合のみ[、，]?)\s*([^\s、，]+)を優先", question)
        if m_b:
            return "A_over_B" if _is_rule_a(m_b.group(1), domain) else "B_over_A"

    # XをYより優先
    m_xy = re.search(r"([^\s（(「]+)を([^\s（(「]+)より優先", question)
    if m_xy and "判断方針として" not in question:
        return "A_over_B" if _is_rule_a(m_xy.group(1), domain) else "B_over_A"

    # YよりXを優先 (including Family K)
    m_yx = re.search(r"([^\s（(「]+)より([^\s（(「]+)を優先", question)
    if m_yx:
        return "A_over_B" if _is_rule_a(m_yx.group(2), domain) else "B_over_A"

    # Family F: 判定が競合した場合は...を採用する
    if "判定が競合した場合は" in question:
        m = re.search(r"判定が競合した場合は(.+?)を採用する", question)
        if m:
            return "A_over_B" if _is_rule_a(m.group(1), domain) else "B_over_A"

    # Family G: ...を上位規則、...を下位規則
    if "上位規則" in question:
        m = re.search(r"(.+?)（.+?）を上位規則", question)
        if m:
            return "A_over_B" if _is_rule_a(m.group(1), domain) else "B_over_A"

    # Family H: 結果を...で上書きする
    if "で上書きする" in question:
        m = re.search(r"結果を(.+?)で上書きする", question)
        if m:
            return "A_over_B" if _is_rule_a(m.group(1), domain) else "B_over_A"

    # Family I: 1位：...、2位：...
    if "1位：" in question:
        m = re.search(r"1位：(.+?)（", question)
        if m:
            return "A_over_B" if _is_rule_a(m.group(1), domain) else "B_over_A"

    # Family J: 両方が成立したときは...を選ぶ
    if "両方が成立したときは" in question:
        m = re.search(r"両方が成立したときは(.+?)を選ぶ", question)
        if m:
            return "A_over_B" if _is_rule_a(m.group(1), domain) else "B_over_A"

    # Family K (Dev): 判断方針として、lowerよりhigherを優先する
    if "判断方針として" in question:
        m = re.search(r"判断方針として、(.+?)より(.+?)を優先する", question)
        if m:
            return "A_over_B" if _is_rule_a(m.group(2), domain) else "B_over_A"

    # Family L (Dev): higherはlowerに先行して評価される
    if "先行して評価される" in question:
        m = re.search(r"ルール：(.+?)（.+?）は", question)
        if m:
            return "A_over_B" if _is_rule_a(m.group(1), domain) else "B_over_A"

    # Family M (Eval): 両規則が該当するケースではhigher側の判断を採る
    if "側の判断を採る" in question:
        m = re.search(r"両規則.+?が該当するケースでは(.+?)側の判断を採る", question)
        if m:
            return "A_over_B" if _is_rule_a(m.group(1), domain) else "B_over_A"

    # Family N (Eval): 判定が重なった場合の決定権はhigherにある
    if "決定権は" in question:
        m = re.search(r"決定権は(.+?)にある", question)
        if m:
            return "A_over_B" if _is_rule_a(m.group(1), domain) else "B_over_A"

    # Family O (Eval): ...を基本判定とするが、...の成立時にはhigherの結論を最終結果とする
    if "の結論を最終結果とする" in question:
        m = re.search(r"成立時には(.+?)の結論を最終結果とする", question)
        if m:
            return "A_over_B" if _is_rule_a(m.group(1), domain) else "B_over_A"

    # Family P (Eval): 競合解決順はhigher、lowerの順
    if "競合解決順は" in question:
        m = re.search(r"競合解決順は(.+?)、", question)
        if m:
            return "A_over_B" if _is_rule_a(m.group(1), domain) else "B_over_A"

    raise ValueError(f"Unable to parse priority order from question: {question}")


def derive_conditions_from_context(domain: str, context: str) -> Tuple[bool, bool]:
    """Parse truth values of Rule A and Rule B strictly from rendered context text."""
    if domain == "game_action":
        # Rule A: HP < 20
        m = re.search(r"(?:HP[は：\s]*|体力(?:満タン（|十分（)?|残り体力)(\d+)", context)
        if not m:
            raise ValueError(f"game_action HP not found in context: {context}")
        hp = int(m.group(1))
        cond_a = (hp < 20)

        # Rule B: 移動中 (moving)
        is_moving = any(k in context for k in ["移動中", "進軍中", "急行中"])
        is_stationary = any(k in context for k in ["移動はしておらず", "滞在中", "索敵中", "停止して", "待機中"])
        if is_moving and not is_stationary:
            cond_b = True
        elif is_stationary and not is_moving:
            cond_b = False
        else:
            raise ValueError(f"Ambiguous moving status (moving={is_moving}, stationary={is_stationary}) in context: {context}")
        return cond_a, cond_b

    elif domain == "delivery_dispatch":
        # Rule A: weight >= 30 kg
        m = re.search(r"(?:重量[は：\s]*|総重量|積載重量)(\d+)kg", context)
        if not m:
            raise ValueError(f"delivery_dispatch weight not found in context: {context}")
        w = int(m.group(1))
        cond_a = (w >= 30)

        # Rule B: urgent request
        is_urgent = any(k in context for k in ["至急配送要請あり", "特急指定・緊急扱い", "緊急配送コールを受付済み"])
        is_normal = any(k in context for k in ["至急要請はなく", "特急指定はなく", "通常納期", "期日通りの配送希望"])
        if is_urgent and not is_normal:
            cond_b = True
        elif is_normal and not is_urgent:
            cond_b = False
        else:
            raise ValueError(f"Ambiguous urgent status (urgent={is_urgent}, normal={is_normal}) in context: {context}")
        return cond_a, cond_b

    elif domain == "system_ops":
        # Rule A: CPU >= 80%
        m = re.search(r"(?:CPU使用率は|CPU負荷率|プロセッサ負荷)(\d+)%", context)
        if not m:
            raise ValueError(f"system_ops CPU not found in context: {context}")
        cpu = int(m.group(1))
        cond_a = (cpu >= 80)

        # Rule B: security incident
        is_alert = any(k in context for k in ["不正侵入アラート検知あり", "マルウェア通信警告あり", "管理者権限奪取の形跡を検知"])
        is_safe = any(k in context for k in ["アラートは発生していません", "兆候はなく安全です", "セキュリティ侵害アラートなし", "侵害の形跡はなく平穏です"])
        if is_alert and not is_safe:
            cond_b = True
        elif is_safe and not is_alert:
            cond_b = False
        else:
            raise ValueError(f"Ambiguous security status (alert={is_alert}, safe={is_safe}) in context: {context}")
        return cond_a, cond_b

    elif domain == "facility_control":
        # Rule A: temperature <= 25度
        m = re.search(r"(?:室温測定値|現在温度|エリア温度)(\d+)度", context)
        if not m:
            raise ValueError(f"facility_control temperature not found in context: {context}")
        temp = int(m.group(1))
        cond_a = (temp <= 25)

        # Rule B: emergency alarm
        is_emergency = any(k in context for k in ["非常警報が鳴動中", "緊急停止シグナル受信", "非常停止ボタン押下検知"])
        is_normal = any(k in context for k in ["検知されていません", "警報なし", "安全システム正常"])
        if is_emergency and not is_normal:
            cond_b = True
        elif is_normal and not is_emergency:
            cond_b = False
        else:
            raise ValueError(f"Ambiguous emergency status (emergency={is_emergency}, normal={is_normal}) in context: {context}")
        return cond_a, cond_b

    elif domain == "manufacturing":
        # Rule A: error <= 0.040 mm
        m = re.search(r"(?:寸法誤差は|測定誤差|誤差)(\d+\.\d+)mm", context)
        if not m:
            raise ValueError(f"manufacturing error not found in context: {context}")
        err = float(m.group(1))
        cond_a = (err <= 0.040)

        # Rule B: surface defect
        is_defect = any(k in context for k in ["表面キズを検知", "外観打痕を検出", "微小異物付着のアラートあり"])
        is_ok = any(k in context for k in ["欠陥なし", "キズなし", "外観センサーは正常", "画像診断は正常判定"])
        if is_defect and not is_ok:
            cond_b = True
        elif is_ok and not is_defect:
            cond_b = False
        else:
            raise ValueError(f"Ambiguous defect status (defect={is_defect}, ok={is_ok}) in context: {context}")
        return cond_a, cond_b

    elif domain == "facility_power":
        # Rule A: kW >= 400 kW
        m_kw = re.search(r"(?:受電電力|現在消費)(\d+)kW", context)
        if not m_kw:
            raise ValueError(f"facility_power kW not found in context: {context}")
        kw = int(m_kw.group(1))
        cond_a = (kw >= 400)

        # Rule B: SOC >= 90 %
        m_soc = re.search(r"(?:蓄電池SOCは|蓄電システム残量は|蓄電池残量は|充電率は|蓄電池残量)(\d+)%", context)
        if not m_soc:
            raise ValueError(f"facility_power SOC not found in context: {context}")
        soc = int(m_soc.group(1))
        cond_b = (soc >= 90)
        return cond_a, cond_b

    elif domain == "inventory":
        # Rule A: storage days >= 180 days
        m_days = re.search(r"(?:保管日数|入庫から|保管期間)(\d+)日", context)
        if not m_days:
            raise ValueError(f"inventory days not found in context: {context}")
        days = int(m_days.group(1))
        cond_a = (days >= 180)

        # Rule B: quarantine / quality audit tag
        is_quarantine = any(k in context for k in ["検疫検査・品質再確認対象", "品質監査指定ロット・隔離要", "検疫管理フラグが有効化", "検疫検査対象"])
        is_normal = any(k in context for k in ["検疫指定はなく", "検疫・保留の指定は一切なし", "通常品です", "検疫タグなし"])
        if is_quarantine and not is_normal:
            cond_b = True
        elif is_normal and not is_quarantine:
            cond_b = False
        else:
            raise ValueError(f"Ambiguous quarantine status (quarantine={is_quarantine}, normal={is_normal}) in context: {context}")
        return cond_a, cond_b

    elif domain == "job_scheduler":
        # Rule A: wait minutes >= 60 mins
        m_mins = re.search(r"(?:待機時間|待ち時間|キュー滞在)(\d+)分", context)
        if not m_mins:
            raise ValueError(f"job_scheduler wait mins not found in context: {context}")
        mins = int(m_mins.group(1))
        cond_a = (mins >= 60)

        # Rule B: memory >= 64 GB
        m_mem = re.search(r"(?:要求メモリ|メモリ要求|メモリ|大容量メモリ要求（)(\d+)GB", context)
        if not m_mem:
            raise ValueError(f"job_scheduler memory not found in context: {context}")
        mem = int(m_mem.group(1))
        cond_b = (mem >= 64)
        return cond_a, cond_b

    elif domain == "customer_service":
        # Rule A: days >= 30 days
        m_days = re.search(r"(?:商品購入から|利用開始から|購入後)(\d+)日", context)
        if not m_days:
            raise ValueError(f"customer_service days not found in context: {context}")
        days = int(m_days.group(1))
        cond_a = (days >= 30)

        # Rule B: VIP
        is_vip = any(k in context for k in ["最上位VIP", "プレミアVIP", "特別顧客"])
        is_normal = any(k in context for k in ["一般会員", "通常メンバー"])
        if is_vip and not is_normal:
            cond_b = True
        elif is_normal and not is_vip:
            cond_b = False
        else:
            raise ValueError(f"Ambiguous VIP status (vip={is_vip}, normal={is_normal}) in context: {context}")
        return cond_a, cond_b

    raise ValueError(f"Unknown domain: {domain}")


DOMAIN_ACTIONS = {
    "game_action": {"action_a": "heal", "action_b": "continue", "action_fallback": "wait"},
    "delivery_dispatch": {"action_a": "standard", "action_b": "express", "action_fallback": "hold"},
    "system_ops": {"action_a": "scale_up", "action_b": "isolate", "action_fallback": "monitor"},
    "facility_control": {"action_a": "eco_mode", "action_b": "emergency_stop", "action_fallback": "normal_run"},
    "customer_service": {"action_a": "standard_guide", "action_b": "special_refund", "action_fallback": "escalate"},
    "manufacturing": {"action_a": "pass", "action_b": "recheck", "action_fallback": "hold"},
    "facility_power": {"action_a": "peak_cut", "action_b": "battery", "action_fallback": "normal"},
    "inventory": {"action_a": "fifo_ship", "action_b": "quarantine", "action_fallback": "standard_ship"},
    "job_scheduler": {"action_a": "promote_queue", "action_b": "defer_night", "action_fallback": "standard_run"},
}


def derive_semantics(record: Dict[str, Any]) -> Dict[str, Any]:
    """Derive ground truth semantics and target purely from rendered record fields."""
    context = record["context"]
    question = record["question"]
    choices = record["choices"]
    stored_target = record["target"]["choice_id"]

    domain = identify_domain_from_choices(choices)
    cond_a, cond_b = derive_conditions_from_context(domain, context)
    priority_order = parse_priority_order_from_question(question, domain)

    actions = DOMAIN_ACTIONS[domain]
    action_a = actions["action_a"]
    action_b = actions["action_b"]
    action_fallback = actions["action_fallback"]

    if cond_a and cond_b:
        expected_target = action_a if priority_order == "A_over_B" else action_b
        state_stratum = "conflict"
    elif cond_a and not cond_b:
        expected_target = action_a
        state_stratum = "single_a"
    elif not cond_a and cond_b:
        expected_target = action_b
        state_stratum = "single_b"
    else:
        expected_target = action_fallback
        state_stratum = "fallback"

    is_match = (expected_target == stored_target)

    return {
        "id": record.get("id", ""),
        "domain": domain,
        "cond_a": cond_a,
        "cond_b": cond_b,
        "priority_order": priority_order,
        "state_stratum": state_stratum,
        "expected_target": expected_target,
        "stored_target": stored_target,
        "is_match": is_match,
    }


def validate_dataset(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Audit all records in a dataset and return summary with any mismatches."""
    mismatches = []
    total = len(records)
    for r in records:
        res = derive_semantics(r)
        if not res["is_match"]:
            mismatches.append(res)

    return {
        "total_records": total,
        "matched_records": total - len(mismatches),
        "mismatches_count": len(mismatches),
        "is_all_valid": (len(mismatches) == 0),
        "mismatches": mismatches,
    }
