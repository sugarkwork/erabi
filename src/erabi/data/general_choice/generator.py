"""General choice task dataset generator for Milestone 8 (ERABI).

Covers 6 general choice families:
1. support_routing: Support ticket triage (billing, tech_support, account_security, sales_inquiry, etc.)
2. short_nli: Concise natural language inference (entailment vs contradiction)
3. semantic_relation: Relational reasoning (cause_effect vs contrast, part_whole vs category_instance)
4. intent_selection: Dialog act / intent classification (refund vs cancel, track vs change_address)
5. instruction_separation: Resolving constraints / priority rules in operational instructions
6. negative_goal: Reverse criteria / negative selection ("禁止事項" vs "推奨行為")

Strict split isolation:
- train: TR entity IDs / scenarios
- dev: DEV entity IDs / scenarios
- fresh: FR entity IDs / scenarios (completely held-out)
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Tuple

GENERAL_FAMILIES = [
    "support_routing",
    "short_nli",
    "semantic_relation",
    "intent_selection",
    "instruction_separation",
    "negative_goal",
]


def generate_support_routing_pair(
    group_idx: int, split: str, pair_idx: int, rng: random.Random
) -> List[Dict[str, Any]]:
    cid = f"{split.upper()}-CUST-{pair_idx+1:03d}"
    sub_type = pair_idx % 3

    if sub_type == 0:
        c1 = ("billing", "請求・経理窓口")
        c2 = ("technical", "技術サポート窓口")
        ctx1 = f"お客様（ID:{cid}）より『先月の利用料金引き落とし明細が契約金額と一致しません。過剰請求の確認と返金内訳について照会したいです』との連絡がありました。"
        ctx2 = f"お客様（ID:{cid}）より『専用アプリを起動するとエラーコード502が頻発し、データベースと通信できません。システム障害の復旧をお願いします』との連絡がありました。"
    elif sub_type == 1:
        c1 = ("account_security", "セキュリティ管理窓口")
        c2 = ("sales_inquiry", "法人営業窓口")
        ctx1 = f"お客様（ID:{cid}）より『身に覚えのない深夜の海外IPからアカウントへのログイン試行通知が届きました。認証トークンの失効と不正アクセス調査をお願いします』との連絡がありました。"
        ctx2 = f"お客様（ID:{cid}）より『来年度からの全社導入に向けてエンタープライズ一括ライセンスの見積もりを希望しています。営業担当者とのオンライン商談を設定してください』との連絡がありました。"
    else:
        c1 = ("returns_exchange", "返品・交換窓口")
        c2 = ("delivery_status", "配送状況追跡窓口")
        ctx1 = f"お客様（ID:{cid}）より『到着した梱包箱を開封したところ、商品本体に明らかな初期破損がありました。至急、良品への無償交換を手配してください』との連絡がありました。"
        ctx2 = f"お客様（ID:{cid}）より『発送案内メールを受領してから予定日を過ぎましたが荷物がまだ届きません。現在の配送業者での追跡ステータスを確認してください』との連絡がありました。"

    q = "このお問い合わせの担当窓口として最も適切な部署を選択してください。"

    choices = [{"id": c1[0], "text": c1[1]}, {"id": c2[0], "text": c2[1]}]
    if rng.random() < 0.5:
        choices.reverse()

    r1 = {
        "id": f"m8-gen-{split}-{group_idx:04d}-c1",
        "group_id": f"m8-grp-{split}-{group_idx:04d}",
        "task_family": "support_routing",
        "split": split,
        "context": ctx1,
        "question": q,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": c1[0]},
    }
    r2 = {
        "id": f"m8-gen-{split}-{group_idx:04d}-c2",
        "group_id": f"m8-grp-{split}-{group_idx:04d}",
        "task_family": "support_routing",
        "split": split,
        "context": ctx2,
        "question": q,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": c2[0]},
    }
    return [r1, r2]


def generate_short_nli_pair(
    group_idx: int, split: str, pair_idx: int, rng: random.Random
) -> List[Dict[str, Any]]:
    loc_id = f"{split.upper()}-LOC-{pair_idx+1:03d}"
    sub_type = pair_idx % 2

    c_ent = ("entailment", "含意（前提から確実に真）")
    c_con = ("contradiction", "矛盾（前提と明らかに両立しない）")

    if sub_type == 0:
        premise = f"施設{loc_id}は祝日を含め年中無休で24時間体制の営業を継続している。"
        hypo_true = f"施設{loc_id}は深夜の午前2時でも営業している。"
        hypo_false = f"施設{loc_id}は深夜帯は完全閉鎖され業務を休止している。"
    else:
        premise = f"プロジェクト{loc_id}の参加メンバーは全員が情報処理技術者資格を保有している。"
        hypo_true = f"プロジェクト{loc_id}に参加しているすべての担当者は資格試験に合格している。"
        hypo_false = f"プロジェクト{loc_id}の参加メンバーの中には該当資格を持たない未経験者が含まれる。"

    ctx1 = f"【前提文】：{premise} 【仮説文】：{hypo_true}"
    ctx2 = f"【前提文】：{premise} 【仮説文】：{hypo_false}"
    q = "提示された前提文に対し、仮説文の真偽関係として最も適切な判定を選択してください。"

    choices = [{"id": c_ent[0], "text": c_ent[1]}, {"id": c_con[0], "text": c_con[1]}]
    if rng.random() < 0.5:
        choices.reverse()

    r1 = {
        "id": f"m8-gen-{split}-{group_idx:04d}-c1",
        "group_id": f"m8-grp-{split}-{group_idx:04d}",
        "task_family": "short_nli",
        "split": split,
        "context": ctx1,
        "question": q,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": c_ent[0]},
    }
    r2 = {
        "id": f"m8-gen-{split}-{group_idx:04d}-c2",
        "group_id": f"m8-grp-{split}-{group_idx:04d}",
        "task_family": "short_nli",
        "split": split,
        "context": ctx2,
        "question": q,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": c_con[0]},
    }
    return [r1, r2]


def generate_semantic_relation_pair(
    group_idx: int, split: str, pair_idx: int, rng: random.Random
) -> List[Dict[str, Any]]:
    rid = f"{split.upper()}-REL-{pair_idx+1:03d}"
    sub_type = pair_idx % 2

    if sub_type == 0:
        c1 = ("cause_effect", "因果関係（原因と結果）")
        c2 = ("contrast", "対比関係（逆接や対立）")
        ctx1 = f"地域{rid}において大型台風の上陸と記録的暴風雨が発生したため、域内の全鉄道路線で終日計画運休が実施された。"
        ctx2 = f"地域{rid}の屋外気温は猛暑日を記録している一方で、オフィスビル内部は空調制御により快適な室温に保たれている。"
    else:
        c1 = ("part_whole", "部分と全体の関係")
        c2 = ("category_instance", "包含関係（カテゴリと具体例）")
        ctx1 = f"機体設計{rid}において、主翼およびエンジンブロックは旅客機全体の構造を構成する不可欠な一部品である。"
        ctx2 = f"栽培品種{rid}において、アサガオやヒマワリはキク類やマメ科と並ぶ顕花植物の代表的な具体例である。"

    q = "文中に示されている2つの要素・事象の論理的関係として最も当てはまるものを選択してください。"

    choices = [{"id": c1[0], "text": c1[1]}, {"id": c2[0], "text": c2[1]}]
    if rng.random() < 0.5:
        choices.reverse()

    r1 = {
        "id": f"m8-gen-{split}-{group_idx:04d}-c1",
        "group_id": f"m8-grp-{split}-{group_idx:04d}",
        "task_family": "semantic_relation",
        "split": split,
        "context": ctx1,
        "question": q,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": c1[0]},
    }
    r2 = {
        "id": f"m8-gen-{split}-{group_idx:04d}-c2",
        "group_id": f"m8-grp-{split}-{group_idx:04d}",
        "task_family": "semantic_relation",
        "split": split,
        "context": ctx2,
        "question": q,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": c2[0]},
    }
    return [r1, r2]


def generate_intent_selection_pair(
    group_idx: int, split: str, pair_idx: int, rng: random.Random
) -> List[Dict[str, Any]]:
    oid = f"{split.upper()}-ORD-{pair_idx+1:04d}"
    sub_type = pair_idx % 2

    if sub_type == 0:
        c1 = ("refund_request", "返金申請を処理する")
        c2 = ("cancel_subscription", "定期契約を解約する")
        ctx1 = f"ユーザー発言：注文コード『{oid}』の購入代金が二重決済されていました。クレジットカードへの超過分全額返金を至急手続きしてください。"
        ctx2 = f"ユーザー発言（会員{oid}）：現在登録されている月額プレミアムプランの自動継続更新を解除し、今月末での会員解約手続きを完了させてください。"
    else:
        c1 = ("track_order", "配送状況を追跡確認する")
        c2 = ("change_address", "送付先住所情報を変更する")
        ctx1 = f"ユーザー発言：出荷完了メールを受領した注文『{oid}』の配送追跡番号で現在地と到着予定時刻を照会したいです。"
        ctx2 = f"ユーザー発言：先ほど確定した注文『{oid}』の配送先住所を引っ越し先の新住所へ修正・変更してください。"

    q = "ユーザーの発言が要求している目的（意図）として最も適切なアクションを選択してください。"

    choices = [{"id": c1[0], "text": c1[1]}, {"id": c2[0], "text": c2[1]}]
    if rng.random() < 0.5:
        choices.reverse()

    r1 = {
        "id": f"m8-gen-{split}-{group_idx:04d}-c1",
        "group_id": f"m8-grp-{split}-{group_idx:04d}",
        "task_family": "intent_selection",
        "split": split,
        "context": ctx1,
        "question": q,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": c1[0]},
    }
    r2 = {
        "id": f"m8-gen-{split}-{group_idx:04d}-c2",
        "group_id": f"m8-grp-{split}-{group_idx:04d}",
        "task_family": "intent_selection",
        "split": split,
        "context": ctx2,
        "question": q,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": c2[0]},
    }
    return [r1, r2]


def generate_instruction_separation_pair(
    group_idx: int, split: str, pair_idx: int, rng: random.Random
) -> List[Dict[str, Any]]:
    pid = f"{split.upper()}-POL-{pair_idx+1:03d}"
    c1 = ("standard_procedure", "標準手順（通常プロセス）を実行")
    c2 = ("emergency_override", "緊急手順（割込プロセス）を実行")

    val_norm = [25, 30, 35][pair_idx % 3]
    val_emer = [85, 90, 95][pair_idx % 3]

    rule = f"【運用規定{pid}】：平常時は標準手順（通常プロセス）を実行する。ただし負荷指数が80を超過した場合は例外として緊急手順（割込プロセス）を実行しなければならない。"
    ctx1 = f"{rule} 現状の計測値：現在の負荷指数は{val_norm}で安全基準値の範囲内です。"
    ctx2 = f"{rule} 現状の計測値：現在の負荷指数は{val_emer}に急上昇し警告閾値を突破しています。"

    q = "運用規定および現在のシステム状況に基づき、最優先で実行すべき措置を選択してください。"

    choices = [{"id": c1[0], "text": c1[1]}, {"id": c2[0], "text": c2[1]}]
    if rng.random() < 0.5:
        choices.reverse()

    r1 = {
        "id": f"m8-gen-{split}-{group_idx:04d}-c1",
        "group_id": f"m8-grp-{split}-{group_idx:04d}",
        "task_family": "instruction_separation",
        "split": split,
        "context": ctx1,
        "question": q,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": c1[0]},
    }
    r2 = {
        "id": f"m8-gen-{split}-{group_idx:04d}-c2",
        "group_id": f"m8-grp-{split}-{group_idx:04d}",
        "task_family": "instruction_separation",
        "split": split,
        "context": ctx2,
        "question": q,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": c2[0]},
    }
    return [r1, r2]


def generate_negative_goal_pair(
    group_idx: int, split: str, pair_idx: int, rng: random.Random
) -> List[Dict[str, Any]]:
    sec_id = f"{split.upper()}-SEC-{pair_idx+1:03d}"
    c_neg = ("forbidden_action", "未承認の個人クラウドストレージへ社外持ち出し保存する")
    c_pos = ("compliant_action", "暗号化が施された社内承認済み共有ストレージへ保存する")

    ctx = f"【セキュリティ規程{sec_id}】：顧客の機密データおよび個人情報は暗号化が施された社内承認済み共有ストレージへ保存することを義務付ける。いかなる理由があっても、未承認の個人クラウドストレージへ社外持ち出し保存することは固く禁じられている。"

    q1 = "上記のセキュリティ規程に照らし、【行ってはならない禁止事項（違反行為）】を選択してください。"
    q2 = "上記のセキュリティ規程に照らし、【遵守すべき推奨行為（適合措置）】を選択してください。"

    choices = [{"id": c_neg[0], "text": c_neg[1]}, {"id": c_pos[0], "text": c_pos[1]}]
    if rng.random() < 0.5:
        choices.reverse()

    r1 = {
        "id": f"m8-gen-{split}-{group_idx:04d}-c1",
        "group_id": f"m8-grp-{split}-{group_idx:04d}",
        "task_family": "negative_goal",
        "split": split,
        "context": ctx,
        "question": q1,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": c_neg[0]},
    }
    r2 = {
        "id": f"m8-gen-{split}-{group_idx:04d}-c2",
        "group_id": f"m8-grp-{split}-{group_idx:04d}",
        "task_family": "negative_goal",
        "split": split,
        "context": ctx,
        "question": q2,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": c_pos[0]},
    }
    return [r1, r2]


def build_general_split(
    split: str,
    pairs_per_family: int,
    seed: int,
    start_group_idx: int = 1,
) -> Tuple[List[Dict[str, Any]], int]:
    rng = random.Random(seed)
    records = []
    grp_idx = start_group_idx

    family_funcs = {
        "support_routing": generate_support_routing_pair,
        "short_nli": generate_short_nli_pair,
        "semantic_relation": generate_semantic_relation_pair,
        "intent_selection": generate_intent_selection_pair,
        "instruction_separation": generate_instruction_separation_pair,
        "negative_goal": generate_negative_goal_pair,
    }

    for fam in GENERAL_FAMILIES:
        fn = family_funcs[fam]
        for p_idx in range(pairs_per_family):
            pair = fn(grp_idx, split, p_idx, rng)
            records.extend(pair)
            grp_idx += 1

    return records, grp_idx
