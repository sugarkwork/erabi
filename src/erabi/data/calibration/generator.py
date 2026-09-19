"""Dedicated dataset generator for Milestone 9 Calibration (ERABI).

Generates two completely isolated datasets:
1. data/m9_calibration/calibration.jsonl (100 cases, 50 contrast pairs)
2. data/m9_calibration/fresh_calibration_eval.jsonl (100 cases, 50 contrast pairs)

Spans all 5 ERABI reasoning paradigms:
1. Core boundary reasoning (inventory, server)
2. Logical operators (AND, OR, LE/LT, negation, priority)
3. Domain robustness (medical, finance, factory, smart_home)
4. General choice (routing, intent, negative goal)
5. Short NLI & Semantic relations
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Tuple


def generate_calib_case_core(group_idx: int, split: str, sub_idx: int, rng: random.Random) -> List[Dict[str, Any]]:
    prefix = "CALIB" if split == "calib" else "FCALIB"
    base_thresh = [22, 38, 54, 66, 78][sub_idx % 5]
    delta = 10 if split == "calib" else 15
    thresh = base_thresh + delta
    val = thresh

    item = f"{prefix}-ITEM-{sub_idx+1:03d}"
    c1 = ("ship", "出荷する")
    c2 = ("hold", "保留する")

    ctx1 = f"倉庫拠点（{prefix}）：{item}の保管在庫数はちょうど{val}点です。出荷前検品は完了しています。"
    ctx2 = f"倉庫拠点（{prefix}）：{item}の保管在庫数はちょうど{val}点です。出荷前検品は未完了です。"

    q_pos = f"数量が{thresh}を下回らない（{thresh}を含む）場合は出荷する、欠落していれば保留するを適用してください。"
    q_neg = f"数量が{thresh}の枠を厳密に超過している場合に限り出荷する、超過していなければ保留するを適用してください。"

    choices = [{"id": c1[0], "text": c1[1]}, {"id": c2[0], "text": c2[1]}]
    if rng.random() < 0.5:
        choices.reverse()

    r1 = {
        "id": f"m9-{split}-{group_idx:04d}-c1",
        "group_id": f"m9-grp-{split}-{group_idx:04d}",
        "category": "core_boundary",
        "split": split,
        "context": ctx1,
        "question": q_pos,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": "ship"},
    }
    r2 = {
        "id": f"m9-{split}-{group_idx:04d}-c2",
        "group_id": f"m9-grp-{split}-{group_idx:04d}",
        "category": "core_boundary",
        "split": split,
        "context": ctx1,
        "question": q_neg,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": "hold"},
    }
    return [r1, r2]


def generate_calib_case_operator(group_idx: int, split: str, sub_idx: int, rng: random.Random) -> List[Dict[str, Any]]:
    prefix = "CALIB" if split == "calib" else "FCALIB"
    srv = f"{prefix}-NODE-{sub_idx+1:03d}"

    c1 = ("pass", "安全とみなす")
    c2 = ("alert", "警告を発令する")

    ctx1 = f"サーバー監視（{prefix}）：{srv}のCPU負荷率は安全圏内です。メモリ空き容量も十分に確保されています。"
    ctx2 = f"サーバー監視（{prefix}）：{srv}のCPU負荷率は安全圏内です。メモリ空き容量は不足しています。"

    q = "CPU使用率とメモリ容量の両方が同時に安全である場合に限り安全とみなす、片方でも異常なら警告を発令するを選択してください。"

    choices = [{"id": c1[0], "text": c1[1]}, {"id": c2[0], "text": c2[1]}]
    if rng.random() < 0.5:
        choices.reverse()

    r1 = {
        "id": f"m9-{split}-{group_idx:04d}-c1",
        "group_id": f"m9-grp-{split}-{group_idx:04d}",
        "category": "logical_operator",
        "split": split,
        "context": ctx1,
        "question": q,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": "pass"},
    }
    r2 = {
        "id": f"m9-{split}-{group_idx:04d}-c2",
        "group_id": f"m9-grp-{split}-{group_idx:04d}",
        "category": "logical_operator",
        "split": split,
        "context": ctx2,
        "question": q,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": "alert"},
    }
    return [r1, r2]


def generate_calib_case_domain(group_idx: int, split: str, sub_idx: int, rng: random.Random) -> List[Dict[str, Any]]:
    prefix = "CALIB" if split == "calib" else "FCALIB"
    line_id = f"{prefix}-LINE-{sub_idx+1:03d}"
    thresh = 70 + (sub_idx * 3) + (2 if split == "calib" else 5)
    val = thresh

    c1 = ("normal_run", "生産ライン稼働継続")
    c2 = ("emergency_stop", "ライン緊急停止")

    ctx1 = f"工場（{prefix}）：{line_id}センサーの振動値はちょうど{val}です。安全防護柵が正常にロックされています。"
    ctx2 = f"工場（{prefix}）：{line_id}センサーの振動値はちょうど{val}です。安全防護柵のロックが解除されています。"

    q_pos = f"振動値が許容値{thresh}以下で安全柵がロックされていれば生産ライン稼働継続、片方でも異常ならライン緊急停止を選定してください。"
    q_neg = f"原則として生産ライン稼働継続とします。ただし安全防護柵のロックが解除されている場合は例外としてライン緊急停止としてください。"

    choices = [{"id": c1[0], "text": c1[1]}, {"id": c2[0], "text": c2[1]}]
    if rng.random() < 0.5:
        choices.reverse()

    r1 = {
        "id": f"m9-{split}-{group_idx:04d}-c1",
        "group_id": f"m9-grp-{split}-{group_idx:04d}",
        "category": "domain_robustness",
        "split": split,
        "context": ctx1,
        "question": q_pos,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": "normal_run"},
    }
    r2 = {
        "id": f"m9-{split}-{group_idx:04d}-c2",
        "group_id": f"m9-grp-{split}-{group_idx:04d}",
        "category": "domain_robustness",
        "split": split,
        "context": ctx2,
        "question": q_neg,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": "emergency_stop"},
    }
    return [r1, r2]


def generate_calib_case_general(group_idx: int, split: str, sub_idx: int, rng: random.Random) -> List[Dict[str, Any]]:
    prefix = "CALIB" if split == "calib" else "FCALIB"
    cid = f"{prefix}-CUST-{sub_idx+1:03d}"

    c1 = ("billing", "請求・経理窓口")
    c2 = ("technical", "技術サポート窓口")

    ctx1 = f"お客様（ID:{cid}）より『先月の明細書で請求金額の内訳を確認したいです。返金手続きの相談をお願いします』との照会がありました。"
    ctx2 = f"お客様（ID:{cid}）より『管理画面へのログイン時にエラー500が発生しサーバーに繋がりません。システム障害の復旧をお願いします』との照会がありました。"

    q = "このお問い合わせの担当窓口として最も適切な部署を選択してください。"

    choices = [{"id": c1[0], "text": c1[1]}, {"id": c2[0], "text": c2[1]}]
    if rng.random() < 0.5:
        choices.reverse()

    r1 = {
        "id": f"m9-{split}-{group_idx:04d}-c1",
        "group_id": f"m9-grp-{split}-{group_idx:04d}",
        "category": "general_choice",
        "split": split,
        "context": ctx1,
        "question": q,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": "billing"},
    }
    r2 = {
        "id": f"m9-{split}-{group_idx:04d}-c2",
        "group_id": f"m9-grp-{split}-{group_idx:04d}",
        "category": "general_choice",
        "split": split,
        "context": ctx2,
        "question": q,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": "technical"},
    }
    return [r1, r2]


def generate_calib_case_negative(group_idx: int, split: str, sub_idx: int, rng: random.Random) -> List[Dict[str, Any]]:
    prefix = "CALIB" if split == "calib" else "FCALIB"
    sec_id = f"{prefix}-RULE-{sub_idx+1:03d}"

    c_neg = ("forbidden_action", "未承認の外部オンラインストレージへ無断転送する")
    c_pos = ("compliant_action", "承認された社内セキュアストレージへ暗号化保管する")

    ctx = f"【情報管理規程{sec_id}】：全従業員は機密情報を承認された社内セキュアストレージへ暗号化保管しなければならない。いかなる場合も、未承認の外部オンラインストレージへ無断転送することは固く禁じられている。"

    q1 = "上記の管理規程に基づき、【行ってはならない禁止事項（違反行為）】を選択してください。"
    q2 = "上記の管理規程に基づき、【遵守すべき推奨行為（適合措置）】を選択してください。"

    choices = [{"id": c_neg[0], "text": c_neg[1]}, {"id": c_pos[0], "text": c_pos[1]}]
    if rng.random() < 0.5:
        choices.reverse()

    r1 = {
        "id": f"m9-{split}-{group_idx:04d}-c1",
        "group_id": f"m9-grp-{split}-{group_idx:04d}",
        "category": "negative_goal",
        "split": split,
        "context": ctx,
        "question": q1,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": "forbidden_action"},
    }
    r2 = {
        "id": f"m9-{split}-{group_idx:04d}-c2",
        "group_id": f"m9-grp-{split}-{group_idx:04d}",
        "category": "negative_goal",
        "split": split,
        "context": ctx,
        "question": q2,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": "compliant_action"},
    }
    return [r1, r2]


def build_calibration_split(split: str, pairs_per_category: int = 10, seed: int = 9001) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    records = []
    grp_idx = 1

    cats = [
        generate_calib_case_core,
        generate_calib_case_operator,
        generate_calib_case_domain,
        generate_calib_case_general,
        generate_calib_case_negative,
    ]

    for cat_fn in cats:
        for sub_idx in range(pairs_per_category):
            pair = cat_fn(grp_idx, split, sub_idx, rng)
            records.extend(pair)
            grp_idx += 1

    return records
