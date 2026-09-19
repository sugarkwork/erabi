"""Robustness & Perturbation dataset generator for Milestone 7 (ERABI).

Covers:
1. Unseen novel domains: medical, finance, factory, smart_home
2. Existing domains: inventory, server, game, delivery, support
3. Perturbations:
   - clean
   - distractor (irrelevant background statement)
   - sentence_swap (swapped context sentences)
   - numerical_scale (scaled numbers)
   - choice_id_perturbation (non-default choice IDs)
   - three_choices (with logically dominated distractor candidate)
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Tuple


ALL_DOMAINS = [
    # Novel unseen domains
    "medical",
    "finance",
    "factory",
    "smart_home",
    # Existing domains
    "inventory",
    "server",
    "game",
    "delivery",
    "support",
]

IRRELEVANT_DISTRACTORS = [
    "なお、本日のオフィス周辺の天候は快晴です。",
    "室内の空調設定温度は24度に保たれています。",
    "本システムは最新のセキュリティパッチが適用済みです。",
    "本記録は自動監査ログにタイムスタンプとともに記録されます。",
    "本案件は標準ログフォーマットに従って出力されています。",
]


def generate_robust_case(
    group_idx: int,
    split: str,
    domain: str,
    perturbation: str,
    rng: random.Random,
    pair_sub_idx: int = 0,
) -> List[Dict[str, Any]]:
    """Generates a contrastive pair for a specific domain and perturbation."""

    # Select logic operator and build scenario based on domain
    if domain == "medical":
        base_thresh = [88, 90, 94][pair_sub_idx % 3] if split == "train" else (91 if split == "dev" else 92)
        thresh = base_thresh if perturbation != "numerical_scale" else base_thresh * 100
        val = thresh
        patient = f"患者TR-{pair_sub_idx+1}" if split == "train" else ("患者DEV-1" if split == "dev" else "患者FR-1")
        c_pos = ("oxygen_therapy", "酸素投与を開始する")
        c_neg = ("regular_monitor", "通常経過観察を行う")

        s1 = f"{patient}の酸素飽和度（SpO2）はちょうど{val}です。"
        s2 = "呼吸不全の兆候が確認されています。"
        s2_alt = "呼吸不全の兆候は認められません。"

        q_clean = f"基準値{thresh}を下回らない（{thresh}を含む）場合は酸素投与を開始する、届かなければ通常経過観察を行うを適用してください。"
        q_contrast = f"基準値{thresh}の枠を厳密に超過している場合に限り酸素投与を開始する、超過していなければ通常経過観察を行うを適用してください。"

    elif domain == "finance":
        base_thresh = [40, 45, 60][pair_sub_idx % 3] if split == "train" else (55 if split == "dev" else 50)
        thresh = base_thresh if perturbation != "numerical_scale" else base_thresh * 1000
        val = thresh
        applicant = f"申込者TR-{pair_sub_idx+1}" if split == "train" else ("申込者DEV-1" if split == "dev" else "申込者FR-1")
        c_pos = ("instant_approve", "即時融資を承認する")
        c_neg = ("manual_review", "人手による詳細審査に回す")

        s1 = f"{applicant}の借入比率はちょうど{val}%です。"
        s2 = "担保設定書類が提出されています。"
        s2_alt = "担保設定書類は未提出です。"

        q_clean = f"借入比率が上限{thresh}を超過しない（{thresh}を含む）場合は即時融資を承認する、上限突破時は人手による詳細審査に回すを選択してください。"
        q_contrast = f"借入比率が{thresh}に満たない（厳密なショート）状態に限り即時融資を承認する、{thresh}に到達していれば人手による詳細審査に回すを選択してください。"

    elif domain == "factory":
        base_thresh = [65, 75, 85][pair_sub_idx % 3] if split == "train" else (70 if split == "dev" else 80)
        thresh = base_thresh if perturbation != "numerical_scale" else base_thresh * 100
        val = thresh
        line = f"第{pair_sub_idx+1}生産ライン" if split == "train" else ("第4生産ライン" if split == "dev" else "第5生産ライン")
        c_pos = ("normal_run", "生産ライン稼働継続")
        c_neg = ("emergency_stop", "ライン緊急停止")

        s1 = f"{line}センサーの振動値はちょうど{val}です。"
        s2 = "安全防護柵が正常にロックされています。"
        s2_alt = "安全防護柵のロックが解除されています。"

        q_clean = f"振動値が許容値{thresh}以下で安全柵がロックされていれば生産ライン稼働継続、片方でも異常ならライン緊急停止を選定してください。"
        q_contrast = f"原則として生産ライン稼働継続とします。ただし安全防護柵のロックが解除されている場合は例外としてライン緊急停止としてください。"

    elif domain == "smart_home":
        rooms_tr = [f"リビング（エリア{pair_sub_idx+1}）", f"寝室（エリア{pair_sub_idx+1}）", f"書斎（エリア{pair_sub_idx+1}）"]
        room = rooms_tr[pair_sub_idx % 3] if split == "train" else ("和室（エリア4）" if split == "dev" else "主寝室（エリア5）")
        temp = [27, 29, 30][pair_sub_idx % 3] if split == "train" else (26 if split == "dev" else 28)
        c_pos = ("eco_mode", "省エネ運転モード")
        c_neg = ("comfort_mode", "快適優先運転モード")

        s1 = f"{room}：室温{temp}度、湿度65%を検知。"
        s2 = "居住者不在フラグがオンになっています。"
        s2_alt = "居住者在室フラグがオンになっています。"

        q_clean = "【方針】：電力消費抑制を最優先とし、快適性は重視しません。省エネ運転モードまたは快適優先運転モードから選んでください。"
        q_contrast = "【方針】：室内の快適性確保を最優先とし、電気代の節約は度外視します。省エネ運転モードまたは快適優先運転モードから選んでください。"

    elif domain == "inventory":
        base_thresh = [35, 45, 55][pair_sub_idx % 3] if split == "train" else (30 if split == "dev" else 40)
        thresh = base_thresh if perturbation != "numerical_scale" else base_thresh * 1000
        val = thresh
        item = f"型番TR-00{pair_sub_idx+1}" if split == "train" else ("型番DEV-001" if split == "dev" else "型番FR-001")
        c_pos = ("ship", "出荷する")
        c_neg = ("hold", "保留する")

        s1 = f"倉庫内の{item}在庫数はちょうど{val}個です。"
        s2 = "検品証明書も受領済みです。"
        s2_alt = "検品証明書は未受領です。"

        q_clean = f"数量が{thresh}を下回らない（{thresh}を含む）場合は出荷する、欠落していれば保留するを適用してください。"
        q_contrast = f"数量が{thresh}の枠を厳密に超過している場合に限り出荷する、超過していなければ保留するを適用してください。"

    elif domain == "server":
        base_thresh = [25, 35, 45][pair_sub_idx % 3] if split == "train" else (20 if split == "dev" else 30)
        thresh = base_thresh if perturbation != "numerical_scale" else base_thresh * 100
        val = thresh
        srv = f"クラスターTR-node-{pair_sub_idx+1}" if split == "train" else ("クラスターDEV-node-1" if split == "dev" else "クラスターFR-node-1")
        c_pos = ("alert", "警告通知を発出する")
        c_neg = ("pass", "正常とみなす")

        s1 = f"{srv}の応答レイテンシはちょうど{val}msです。"
        s2 = "CPU使用率は安全圏内です。"
        s2_alt = "CPU使用率も高負荷です。"

        q_clean = f"レイテンシが{thresh}以上であれば警告通知を発出する、そうでなければ正常とみなすを選んでください。"
        q_contrast = f"レイテンシが{thresh}を超える（より大きい）場合は警告通知を発出する、そうでなければ正常とみなすを選んでください。"

    elif domain == "game":
        enemy = f"討伐対象魔獣TR-{pair_sub_idx+1}" if split == "train" else ("討伐対象巨兵DEV-1" if split == "dev" else "討伐対象暗黒騎士FR-1")
        hp = [15, 25, 30][pair_sub_idx % 3] if split == "train" else (10 if split == "dev" else 20)
        c_pos = ("ultimate", "必殺技を発動する")
        c_neg = ("attack", "通常攻撃を行う")

        s1 = f"{enemy}のHPは{hp}%以下です。"
        s2 = "必殺技ゲージも最大まで溜まっています。"
        s2_alt = "必殺技ゲージはまだ溜まっていません。"

        q_clean = "条件Aと条件Bの双方が同時に成立しているときに限り必殺技を発動する、二条件が揃わないときは通常攻撃を行うとしてください。"
        q_contrast = "条件Aと条件Bの双方が同時に成立しているときに限り必殺技を発動する、二条件が揃わないときは通常攻撃を行うとしてください。"

    elif domain == "delivery":
        base_thresh = [12, 18, 22][pair_sub_idx % 3] if split == "train" else (10 if split == "dev" else 15)
        thresh = base_thresh if perturbation != "numerical_scale" else base_thresh * 100
        val = thresh
        pkg = f"配送荷物TR-{pair_sub_idx+1}" if split == "train" else ("配送荷物DEV-1" if split == "dev" else "配送荷物FR-1")
        c_pos = ("small_box", "小型区分で梱包する")
        c_neg = ("large_box", "大型区分で梱包する")

        s1 = f"{pkg}の梱包サイズ合計はちょうど{val}cmです。"
        s2 = "重量制限はクリアしています。"
        s2_alt = "重量制限は超過しています。"

        q_clean = f"数値が上限{thresh}を超過しない（{thresh}を含む）範囲にとどまる場合は小型区分で梱包する、上限突破時は大型区分で梱包するを適用してください。"
        q_contrast = f"数値が{thresh}に満たない（厳密なショート）状態に限り小型区分で梱包する、{thresh}に到達していれば大型区分で梱包するを適用してください。"

    else:  # support
        tier = f"TR-契約プラン{pair_sub_idx+1}" if split == "train" else ("DEV-特定事業所プラン" if split == "dev" else "FR-特別協定プラン")
        c_pos = ("free_repair", "無償修理を手配")
        c_neg = ("paid_repair", "有償見積を案内")

        s1 = f"ユーザー契約（{tier}）：年間保守サポートプランに加入しています。"
        s2 = "対象製品の保証期間内です。"
        s2_alt = "対象製品の保証期間外です。"

        q_clean = "【年間保守サポートプラン加入】の条件を満たす場合は無償修理を手配、満たさない場合は有償見積を案内を適用してください。"
        q_contrast = "【年間保守サポートプラン加入】の条件から除外されている（満たさない）場合は無償修理を手配、満たす場合は有償見積を案内を適用してください。"

    # Apply Perturbations
    if perturbation == "sentence_swap":
        ctx1 = f"{s2} {s1}"
        ctx2 = f"{s2_alt} {s1}"
    else:
        ctx1 = f"{s1} {s2}"
        ctx2 = f"{s1} {s2_alt}"

    if perturbation == "distractor":
        if split == "train":
            d_pool = [
                "なお、本日のオフィス周辺の天候は快晴です。",
                "室内の空調設定温度は24度に保たれています。",
                "本記録は自動監査ログにタイムスタンプとともに記録されます。",
            ]
        elif split == "dev":
            d_pool = [
                "本システムの監視エージェントは正常稼働状態を維持しています。",
                "内部ネットワークの通信遅延は規定許容値の範囲内です。",
            ]
        else:
            d_pool = [
                "本案件は標準ログフォーマットに従って出力されています。",
                "本システムは最新のセキュリティパッチが適用済みです。",
            ]
        distractor = rng.choice(d_pool)
        ctx1 = f"{ctx1} {distractor}"
        ctx2 = f"{ctx2} {distractor}"

    # Choice IDs
    id_pos = c_pos[0]
    id_neg = c_neg[0]
    if perturbation == "choice_id_perturbation":
        id_pos = f"cand_1_{id_pos}"
        id_neg = f"cand_2_{id_neg}"

    choices = [
        {"id": id_pos, "text": c_pos[1]},
        {"id": id_neg, "text": c_neg[1]},
    ]
    if perturbation == "three_choices":
        choices.append({"id": "dummy_none", "text": "該当なし・何もしない"})

    if rng.random() < 0.5:
        choices.reverse()

    r1 = {
        "id": f"m7-rob-{split}-{group_idx:04d}-c1",
        "group_id": f"m7-grp-{split}-{group_idx:04d}",
        "task_family": "domain_perturbation_robustness",
        "domain": domain,
        "perturbation": perturbation,
        "split": split,
        "context": ctx1,
        "question": q_clean,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": id_pos},
        "case_kind": "pos_target",
    }
    r2 = {
        "id": f"m7-rob-{split}-{group_idx:04d}-c2",
        "group_id": f"m7-grp-{split}-{group_idx:04d}",
        "task_family": "domain_perturbation_robustness",
        "domain": domain,
        "perturbation": perturbation,
        "split": split,
        "context": ctx1 if domain in ["medical", "finance", "inventory", "server", "delivery", "support"] else ctx2,
        "question": q_contrast,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": id_neg},
        "case_kind": "neg_target",
    }

    return [r1, r2]


def build_robustness_split(
    split: str,
    pairs_per_cell: int,
    seed: int,
    start_group_idx: int = 1,
) -> Tuple[List[Dict[str, Any]], int]:
    rng = random.Random(seed)
    records = []
    grp_idx = start_group_idx

    # Perturbations
    perturbations = ["clean", "distractor", "sentence_swap", "numerical_scale", "choice_id_perturbation", "three_choices"]

    for d in ALL_DOMAINS:
        for p in perturbations:
            for pair_sub_idx in range(pairs_per_cell):
                pair = generate_robust_case(grp_idx, split, d, p, rng, pair_sub_idx=pair_sub_idx)
                records.extend(pair)
                grp_idx += 1

    return records, grp_idx
