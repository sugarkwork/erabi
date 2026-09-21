"""Generate independent RC3.1 logic-recovery records.

This module is deliberately independent from the retired Blind v5 generators.
It produces symbolic-expression metadata for audit/reporting, but the rendered
context, question, and choices contain no internal audit markers.  The target
is produced from the expression here only so that an independent validator can
re-derive it from the rendered text later.
"""

from __future__ import annotations

import random
from collections import Counter
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple


State = Tuple[bool, bool, bool]
Action = Tuple[str, str]


OPERATOR_FAMILIES: Tuple[str, ...] = (
    "and",
    "or",
    "xor",
    "and_not_b",
    "not_a_or_b",
    "nand",
    "nor",
    "not",
    "implication",
    "double_negation",
    "polarity_reversal",
    "nested_and_or",
    "nested_a_and_or",
    "nested_not_and",
    "nested_not_or",
    "nested_xor_and",
)

EXPRESSION_TEXTS: Mapping[str, str] = {
    "and": "A AND B",
    "or": "A OR B",
    "xor": "A XOR B",
    "and_not_b": "A AND NOT B",
    "not_a_or_b": "NOT A OR B",
    "nand": "NAND(A,B)",
    "nor": "NOR(A,B)",
    "not": "NOT A",
    "implication": "A -> B",
    "double_negation": "NOT NOT A",
    "polarity_reversal": "REVERSE(A)",
    "nested_and_or": "(A AND B) OR C",
    "nested_a_and_or": "A AND (B OR C)",
    "nested_not_and": "NOT(A AND B)",
    "nested_not_or": "NOT(A OR B)",
    "nested_xor_and": "(A XOR B) AND C",
}

NESTED_OPERATORS = {
    "nested_and_or",
    "nested_a_and_or",
    "nested_not_and",
    "nested_not_or",
    "nested_xor_and",
}

BRIDGE_TEMPLATE_FAMILIES: Tuple[str, ...] = (
    "bridge_logbook",
    "bridge_control_panel",
    "bridge_inspection_sheet",
    "bridge_telemetry_note",
)

MAPPING_STYLES: Tuple[str, ...] = ("normal", "reordered", "implicit_fallback")
CONDITION_ORDERS: Tuple[Tuple[str, str, str], ...] = (
    ("A", "B", "C"),
    ("B", "C", "A"),
    ("C", "A", "B"),
    ("A", "C", "B"),
    ("B", "A", "C"),
    ("C", "B", "A"),
)

TRAIN_TEMPLATE_FAMILIES: Mapping[str, Tuple[str, ...]] = {
    "train": ("train_shift_note", "train_dispatch_card", "train_quality_record"),
    "dev": ("dev_operator_report", "dev_maintenance_ticket"),
    "calibration": ("calibration_review_memo",),
}

_CODE_WORDS = (
    "Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel",
    "India", "Juliett", "Kilo", "Lima", "Mike", "November", "Oscar", "Papa",
    "Quebec", "Romeo", "Sierra", "Tango", "Uniform", "Victor", "Whiskey", "Xray",
    "Yankee", "Zulu",
)


# The bridge domains intentionally do not occur in the RC3.1 training data.
BRIDGE_DOMAINS: Tuple[Dict[str, Any], ...] = (
    {
        "slug": "aerospace",
        "name": "航空宇宙機の姿勢制御",
        "a": "姿勢同期信号",
        "b": "推進系熱保護信号",
        "c": "通信アンテナ冗長信号",
        "actions": (
            ("aero_primary", "姿勢制御系へ切り替える"),
            ("aero_secondary", "安全保持モードを継続する"),
            ("aero_d1", "地上管制へ照会する"),
            ("aero_d2", "予備電源を接続する"),
            ("aero_d3", "観測計画を一時停止する"),
            ("aero_d4", "通信帯域を制限する"),
        ),
    },
    {
        "slug": "medical_device",
        "name": "医療機器の滅菌工程",
        "a": "チャンバー温度到達信号",
        "b": "滅菌保持時間完了信号",
        "c": "扉インターロック信号",
        "actions": (
            ("med_primary", "次の滅菌工程へ進める"),
            ("med_secondary", "工程を安全待機にする"),
            ("med_d1", "再測定を依頼する"),
            ("med_d2", "装置ログを保存する"),
            ("med_d3", "保守担当へ連絡する"),
            ("med_d4", "試料を隔離する"),
        ),
    },
    {
        "slug": "railway",
        "name": "鉄道信号の進路制御",
        "a": "進路鎖錠信号",
        "b": "軌道回路無占有信号",
        "c": "転轍機定位信号",
        "actions": (
            ("rail_primary", "進行信号を現示する"),
            ("rail_secondary", "停止信号を維持する"),
            ("rail_d1", "駅係員へ通報する"),
            ("rail_d2", "進路を再照合する"),
            ("rail_d3", "保安装置を点検する"),
            ("rail_d4", "列車を場内で待機させる"),
        ),
    },
    {
        "slug": "semiconductor",
        "name": "半導体露光装置の搬送",
        "a": "真空到達信号",
        "b": "ウエハ位置確認信号",
        "c": "薬液供給安定信号",
        "actions": (
            ("semi_primary", "露光搬送を開始する"),
            ("semi_secondary", "搬送をインターロックする"),
            ("semi_d1", "装置を初期化する"),
            ("semi_d2", "確認画面を開く"),
            ("semi_d3", "予備ステージを選択する"),
            ("semi_d4", "品質記録を確認する"),
        ),
    },
    {
        "slug": "energy_grid",
        "name": "送電網の周波数制御",
        "a": "系統周波数安定信号",
        "b": "予備発電容量信号",
        "c": "連系線余力信号",
        "actions": (
            ("grid_primary", "通常の系統制御を続ける"),
            ("grid_secondary", "負荷抑制制御へ移る"),
            ("grid_d1", "予備発電を起動する"),
            ("grid_d2", "需給担当へ連絡する"),
            ("grid_d3", "監視周期を短縮する"),
            ("grid_d4", "連系線を切り離す"),
        ),
    },
    {
        "slug": "satellite_telemetry",
        "name": "衛星テレメトリ受信",
        "a": "主中継器ロック信号",
        "b": "時刻同期信号",
        "c": "アンテナ追尾信号",
        "actions": (
            ("sat_primary", "通常テレメトリを受信する"),
            ("sat_secondary", "重要テレメトリへ退避する"),
            ("sat_d1", "予備中継器を選択する"),
            ("sat_d2", "受信窓を延長する"),
            ("sat_d3", "地上局へ再送要求する"),
            ("sat_d4", "姿勢保持を優先する"),
        ),
    },
    {
        "slug": "warehouse_safety",
        "name": "倉庫搬送の安全監視",
        "a": "通路センサー無障害信号",
        "b": "搬送台車停止信号",
        "c": "防護柵閉鎖信号",
        "actions": (
            ("warehouse_primary", "搬送走行を許可する"),
            ("warehouse_secondary", "搬送を停止保持する"),
            ("warehouse_d1", "現場確認を依頼する"),
            ("warehouse_d2", "迂回経路を設定する"),
            ("warehouse_d3", "警戒員を配置する"),
            ("warehouse_d4", "搬送計画を更新する"),
        ),
    },
    {
        "slug": "chemical_plant",
        "name": "化学プラントの反応槽管理",
        "a": "反応温度安定信号",
        "b": "圧力上限余裕信号",
        "c": "冷却循環確認信号",
        "actions": (
            ("chem_primary", "反応運転を継続する"),
            ("chem_secondary", "反応槽を安全停止する"),
            ("chem_d1", "冷却流量を確認する"),
            ("chem_d2", "分析試料を採取する"),
            ("chem_d3", "緊急連絡網を起動する"),
            ("chem_d4", "原料供給を保留する"),
        ),
    },
    {
        "slug": "network_routing",
        "name": "ネットワーク経路制御",
        "a": "主経路到達可能信号",
        "b": "遅延上限内信号",
        "c": "認証経路健全信号",
        "actions": (
            ("net_primary", "主経路を使用する"),
            ("net_secondary", "予備経路へ切り替える"),
            ("net_d1", "経路広告を再計算する"),
            ("net_d2", "監視パケットを増やす"),
            ("net_d3", "接続を一時制限する"),
            ("net_d4", "管理者へ状態を通知する"),
        ),
    },
    {
        "slug": "robotics",
        "name": "産業ロボットの教示運転",
        "a": "非常停止解除信号",
        "b": "イネーブルスイッチ信号",
        "c": "作業領域無人信号",
        "actions": (
            ("robot_primary", "教示運転を許可する"),
            ("robot_secondary", "ロボットを停止保持する"),
            ("robot_d1", "保護扉を点検する"),
            ("robot_d2", "速度上限を下げる"),
            ("robot_d3", "作業者へ退避を促す"),
            ("robot_d4", "教示計画を保存する"),
        ),
    },
    {
        "slug": "maritime",
        "name": "船舶機関の航行監視",
        "a": "主機回転安定信号",
        "b": "冷却水流量信号",
        "c": "操舵装置健全信号",
        "actions": (
            ("sea_primary", "通常航行を継続する"),
            ("sea_secondary", "減速航行へ移る"),
            ("sea_d1", "機関室へ連絡する"),
            ("sea_d2", "予備ポンプを起動する"),
            ("sea_d3", "航路を変更する"),
            ("sea_d4", "機関ログを保存する"),
        ),
    },
    {
        "slug": "manufacturing_qa",
        "name": "製造品質の出荷判定",
        "a": "寸法検査合格信号",
        "b": "外観検査合格信号",
        "c": "トレーサビリティ登録信号",
        "actions": (
            ("qa_primary", "出荷判定を承認する"),
            ("qa_secondary", "ロットを保留する"),
            ("qa_d1", "再検査を実施する"),
            ("qa_d2", "品質保証へ照会する"),
            ("qa_d3", "検査記録を補完する"),
            ("qa_d4", "代替ロットを確認する"),
        ),
    },
)


# Training domains are intentionally separate from all bridge domain slugs.
TRAIN_DOMAINS: Tuple[Dict[str, Any], ...] = (
    {
        "slug": "glass_fabrication",
        "name": "ガラス成形ライン",
        "a": "炉内温度安定信号",
        "b": "成形金型準備信号",
        "c": "冷却水循環信号",
        "actions": (("glass_primary", "成形工程を開始する"), ("glass_secondary", "工程を待機させる"), ("glass_d1", "炉を保温する"), ("glass_d2", "金型を交換する"), ("glass_d3", "検査を依頼する"), ("glass_d4", "材料供給を止める")),
    },
    {
        "slug": "district_heating",
        "name": "地域熱供給設備",
        "a": "熱源機運転信号",
        "b": "配管差圧信号",
        "c": "蓄熱槽余力信号",
        "actions": (("heat_primary", "熱供給を継続する"), ("heat_secondary", "供給を制限する"), ("heat_d1", "蓄熱槽を切り替える"), ("heat_d2", "保守員を呼ぶ"), ("heat_d3", "監視値を再取得する"), ("heat_d4", "需要側へ通知する")),
    },
    {
        "slug": "port_crane",
        "name": "港湾クレーン運用",
        "a": "吊荷重量許可信号",
        "b": "風速上限内信号",
        "c": "走行レール無障害信号",
        "actions": (("crane_primary", "荷役作業を許可する"), ("crane_secondary", "荷役を停止する"), ("crane_d1", "吊荷を降ろす"), ("crane_d2", "作業区域を封鎖する"), ("crane_d3", "運転員へ確認する"), ("crane_d4", "別クレーンを手配する")),
    },
    {
        "slug": "genomics_lab",
        "name": "遺伝子解析ラボ",
        "a": "試料温度管理信号",
        "b": "試薬有効期限信号",
        "c": "解析装置校正信号",
        "actions": (("gene_primary", "解析を開始する"), ("gene_secondary", "試料を保留する"), ("gene_d1", "再校正を実施する"), ("gene_d2", "試薬を交換する"), ("gene_d3", "責任者へ照会する"), ("gene_d4", "試料を再採取する")),
    },
    {
        "slug": "retail_replenishment",
        "name": "小売補充計画",
        "a": "需要予測更新信号",
        "b": "倉庫在庫余力信号",
        "c": "配送枠確保信号",
        "actions": (("retail_primary", "補充発注を確定する"), ("retail_secondary", "発注を保留する"), ("retail_d1", "在庫を再集計する"), ("retail_d2", "配送枠を照会する"), ("retail_d3", "店舗へ通知する"), ("retail_d4", "代替商品を確認する")),
    },
    {
        "slug": "film_archive",
        "name": "映像アーカイブ保存",
        "a": "原版読取完了信号",
        "b": "保存媒体健全信号",
        "c": "メタデータ登録信号",
        "actions": (("film_primary", "保存処理を確定する"), ("film_secondary", "保存処理を保留する"), ("film_d1", "媒体を交換する"), ("film_d2", "原版を再読取する"), ("film_d3", "台帳を更新する"), ("film_d4", "管理者へ照会する")),
    },
    {
        "slug": "water_treatment",
        "name": "浄水処理施設",
        "a": "濁度管理信号",
        "b": "薬注ポンプ運転信号",
        "c": "ろ過槽差圧信号",
        "actions": (("water_primary", "通常ろ過を続ける"), ("water_secondary", "処理を安全停止する"), ("water_d1", "薬注量を確認する"), ("water_d2", "逆洗工程へ移る"), ("water_d3", "採水検査を行う"), ("water_d4", "担当部署へ連絡する")),
    },
    {
        "slug": "food_processing",
        "name": "食品加工ライン",
        "a": "加熱温度到達信号",
        "b": "包装シール確認信号",
        "c": "異物検査合格信号",
        "actions": (("food_primary", "製品を次工程へ送る"), ("food_secondary", "製品を隔離する"), ("food_d1", "再加熱を実施する"), ("food_d2", "包装機を調整する"), ("food_d3", "検査記録を確認する"), ("food_d4", "品質担当へ連絡する")),
    },
    {
        "slug": "battery_recycling",
        "name": "蓄電池リサイクル工程",
        "a": "残留電圧安全信号",
        "b": "解体治具固定信号",
        "c": "換気監視信号",
        "actions": (("battery_primary", "解体工程を開始する"), ("battery_secondary", "解体を停止保持する"), ("battery_d1", "放電を追加する"), ("battery_d2", "治具を再固定する"), ("battery_d3", "換気量を増やす"), ("battery_d4", "ロットを隔離する")),
    },
    {
        "slug": "data_center_cooling",
        "name": "データセンター冷却設備",
        "a": "冷却水流量信号",
        "b": "ラック温度上限信号",
        "c": "予備冷却機待機信号",
        "actions": (("dc_primary", "通常冷却を継続する"), ("dc_secondary", "負荷を縮退する"), ("dc_d1", "予備冷却機を起動する"), ("dc_d2", "ラックを移動する"), ("dc_d3", "監視間隔を短縮する"), ("dc_d4", "運用担当へ通知する")),
    },
    {
        "slug": "weather_radar",
        "name": "気象レーダー観測",
        "a": "観測アンテナ追尾信号",
        "b": "受信機校正信号",
        "c": "電源品質信号",
        "actions": (("weather_primary", "観測を継続する"), ("weather_secondary", "観測を一時停止する"), ("weather_d1", "校正を再実施する"), ("weather_d2", "予備電源へ切り替える"), ("weather_d3", "観測員へ連絡する"), ("weather_d4", "速報配信を制限する")),
    },
    {
        "slug": "cold_chain",
        "name": "低温物流の出荷管理",
        "a": "庫内温度許可信号",
        "b": "保冷容器封印信号",
        "c": "配送車両位置信号",
        "actions": (("cold_primary", "出荷を許可する"), ("cold_secondary", "出荷を保留する"), ("cold_d1", "温度を再測定する"), ("cold_d2", "容器を交換する"), ("cold_d3", "配送担当へ照会する"), ("cold_d4", "代替車両を手配する")),
    },
)


def _add_lexical_overlap_distractor(domain: Mapping[str, Any]) -> Dict[str, Any]:
    """Add one explicit action-only distractor sharing target vocabulary.

    It occupies the first distractor slot, so every K>2 rendering contains a
    lexical-overlap candidate while K=2 remains a pure target contrast.
    """
    actions = list(domain["actions"])
    primary_id, primary_text = actions[0]
    lexical_id = f"{domain['slug']}_lexical_distractor"
    lexical_text = f"「{primary_text}」の関連記録を確認する"
    actions[2] = (lexical_id, lexical_text)
    return {
        **domain,
        "actions": tuple(actions),
        "lexical_overlap_ids": (lexical_id,),
        "lexical_overlap_source": primary_id,
    }


# Keep the classification explicit in generator metadata while leaving all
# audit fields outside the model-visible context/question/choices contract.
BRIDGE_DOMAINS = tuple(_add_lexical_overlap_distractor(domain) for domain in BRIDGE_DOMAINS)
TRAIN_DOMAINS = tuple(_add_lexical_overlap_distractor(domain) for domain in TRAIN_DOMAINS)


def _word_code(index: int) -> str:
    return f"{_CODE_WORDS[(index // len(_CODE_WORDS)) % len(_CODE_WORDS)]}-{_CODE_WORDS[index % len(_CODE_WORDS)]}"


def evaluate_operator(operator: str, state: State) -> bool:
    """Evaluate a symbolic expression for generation only."""
    a, b, c = state
    if operator == "and":
        return a and b
    if operator == "or":
        return a or b
    if operator == "xor":
        return a != b
    if operator == "and_not_b":
        return a and (not b)
    if operator == "not_a_or_b":
        return (not a) or b
    if operator == "nand":
        return not (a and b)
    if operator == "nor":
        return not (a or b)
    if operator == "not":
        return not a
    if operator == "implication":
        return (not a) or b
    if operator == "double_negation":
        return not (not a)
    if operator == "polarity_reversal":
        return not a
    if operator == "nested_and_or":
        return (a and b) or c
    if operator == "nested_a_and_or":
        return a and (b or c)
    if operator == "nested_not_and":
        return not (a and b)
    if operator == "nested_not_or":
        return not (a or b)
    if operator == "nested_xor_and":
        return (a != b) and c
    raise ValueError(f"Unknown operator: {operator}")


def _state_for(operator: str, index: int) -> State:
    if operator in {"and", "or", "xor", "and_not_b", "not_a_or_b", "nand", "nor", "implication"}:
        states = [(False, False, False), (False, True, False), (True, False, False), (True, True, False)]
    elif operator in NESTED_OPERATORS:
        states = [(a, b, c) for a in (False, True) for b in (False, True) for c in (False, True)]
    else:
        states = [(False, False, False), (False, True, False), (True, False, False), (True, True, False)]
    return states[index % len(states)]


def _render_context(
    domain: Mapping[str, Any],
    state: State,
    template_family: str,
    variant: str,
    condition_order: Tuple[str, str, str],
) -> str:
    statuses = ["成立" if value else "不成立" for value in state]
    a, b, c = domain["a"], domain["b"], domain["c"]
    name = domain["name"]
    if "logbook" in template_family or "shift" in template_family:
        prefix = f"運用記録コード {variant}：{name}。"
    elif "panel" in template_family or "dispatch" in template_family:
        prefix = f"制御盤入力 {variant}。対象は{name}である。"
    elif "inspection" in template_family or "quality" in template_family:
        prefix = f"点検票 {variant} の対象は{name}。"
    elif "telemetry" in template_family or "operator" in template_family:
        prefix = f"観測メモ {variant}：{name}。"
    elif "maintenance" in template_family or "review" in template_family:
        prefix = f"確認記録 {variant}。{name}を評価する。"
    else:
        prefix = f"判定記録 {variant}：{name}。"
    labels = {"A": a, "B": b, "C": c}
    status_by_label = {"A": statuses[0], "B": statuses[1], "C": statuses[2]}
    conditions = "、".join(
        f"条件{label}「{labels[label]}」は{status_by_label[label]}" for label in condition_order
    )
    return f"{prefix}{conditions}。"


def _render_question(
    operator: str,
    true_text: str,
    false_text: str,
    template_family: str,
    mapping_style: str,
) -> str:
    expression = EXPRESSION_TEXTS[operator]
    if mapping_style not in MAPPING_STYLES:
        raise ValueError(f"Unknown mapping style: {mapping_style}")
    if mapping_style == "implicit_fallback":
        return f"論理式「{expression}」では通常「{false_text}」を選択します。ただし、成立する場合に限り「{true_text}」を選択してください。"
    if "control_panel" in template_family or "dispatch" in template_family:
        if mapping_style == "normal":
            return f"評価式「{expression}」が成立なら「{true_text}」、不成立なら「{false_text}」を選択してください。"
        return f"評価式「{expression}」が不成立なら「{false_text}」、成立なら「{true_text}」を選択してください。"
    if "inspection" in template_family or "quality" in template_family:
        if mapping_style == "normal":
            return f"論理式「{expression}」の判定が真の場合は「{true_text}」、偽の場合は「{false_text}」としてください。"
        return f"論理式「{expression}」の判定が偽の場合は「{false_text}」、真の場合は「{true_text}」としてください。"
    elif "telemetry" in template_family or "operator" in template_family:
        if mapping_style == "normal":
            return f"式「{expression}」が有効なら「{true_text}」、無効なら「{false_text}」を実施してください。"
        return f"式「{expression}」が無効なら「{false_text}」、有効なら「{true_text}」を実施してください。"
    elif "maintenance" in template_family or "review" in template_family:
        if mapping_style == "normal":
            return f"判定式「{expression}」の結果が真なら「{true_text}」、偽なら「{false_text}」を選んでください。"
        return f"判定式「{expression}」の結果が偽なら「{false_text}」、真なら「{true_text}」を選んでください。"
    else:
        if mapping_style == "normal":
            return f"論理式「{expression}」が真なら「{true_text}」、偽なら「{false_text}」を選択してください。"
        return f"論理式「{expression}」が偽なら「{false_text}」、真なら「{true_text}」を選択してください。"


def _build_choices(domain: Mapping[str, Any], k: int, pair_index: int, seed: int) -> List[Dict[str, str]]:
    actions: Sequence[Action] = domain["actions"]
    # Keep the two semantic targets in a deterministic, K-local rotation.
    # Pair indices are interleaved by K (2, 3, 4, 6), so using pair_index
    # directly would pin K=2 to one slot.  Each contrastive pair then places
    # primary and secondary at two different slots, making target-position
    # counts balanced regardless of which expression is true.
    slot = (pair_index // 4) % k
    other_slot = (slot + max(1, k // 2)) % k
    result: List[Action | None] = [None] * k
    result[slot] = actions[0]
    result[other_slot] = actions[1]
    distractors = list(actions[2:k])
    rng = random.Random(0x31A5 + int(seed) * 1000003 + pair_index * 7919 + k)
    rng.shuffle(distractors)
    iterator = iter(distractors)
    for index, action in enumerate(result):
        if action is None:
            result[index] = next(iterator)
    return [{"id": cid, "text": text} for cid, text in result if cid is not None]


def _find_partner(
    operator: str,
    state: State,
    start: int,
    partner_counts: Mapping[str, int] | None = None,
) -> str:
    value = evaluate_operator(operator, state)
    candidates = [
        candidate
        for candidate in OPERATOR_FAMILIES
        if candidate != operator and evaluate_operator(candidate, state) != value
    ]
    if partner_counts is not None:
        # Keep the second member of each contrastive pair balanced too.  The
        # rotating tie-break preserves deterministic variation while the
        # minimum-count rule prevents common expressions (notably double
        # negation) from absorbing most partner slots.
        offset = (OPERATOR_FAMILIES.index(operator) + start) % len(OPERATOR_FAMILIES)
        candidates.sort(
            key=lambda candidate: (
                int(partner_counts.get(candidate, 0)),
                (OPERATOR_FAMILIES.index(candidate) - offset) % len(OPERATOR_FAMILIES),
            )
        )
        if candidates:
            return candidates[0]
    else:
        for offset in range(1, len(OPERATOR_FAMILIES) + 1):
            candidate = OPERATOR_FAMILIES[(OPERATOR_FAMILIES.index(operator) + start + offset) % len(OPERATOR_FAMILIES)]
            if candidate in candidates:
                return candidate
    raise AssertionError(f"Could not find contrastive partner for {operator} and {state}")


def _make_pair(
    domain: Mapping[str, Any],
    state: State,
    first_operator: str,
    second_operator: str,
    k: int,
    pair_index: int,
    template_family: str,
    split: str,
    mapping_style: str,
    condition_order: Tuple[str, str, str],
    seed: int,
) -> List[Dict[str, Any]]:
    choices = _build_choices(domain, k, pair_index, seed)
    true_action, false_action = domain["actions"][0], domain["actions"][1]
    context = _render_context(domain, state, template_family, _word_code(pair_index), condition_order)
    lexical_ids = set(str(value) for value in domain.get("lexical_overlap_ids", ()))
    distractor_classes = {
        str(choice["id"]): ("lexical_overlap" if str(choice["id"]) in lexical_ids else "plausible_distractor")
        for choice in choices
        if str(choice["id"]) not in {str(true_action[0]), str(false_action[0])}
    }
    records: List[Dict[str, Any]] = []
    for case_index, operator in enumerate((first_operator, second_operator), start=1):
        result = evaluate_operator(operator, state)
        true_text, false_text = true_action[1], false_action[1]
        question = _render_question(operator, true_text, false_text, template_family, mapping_style)
        target_id = true_action[0] if result else false_action[0]
        record = {
            "id": f"rc3_1_{split}_{pair_index:04d}_s{case_index}",
            "group_id": f"rc3_1_{split}_{pair_index:04d}",
            "family": "logical_operators",
            "subdomain": operator,
            "context": context,
            "question": question,
            "choices": [dict(choice) for choice in choices],
            "target": {"kind": "hard", "choice_id": target_id},
            # Audit metadata is outside the rendered model input.
            "operator_family": operator,
            "symbolic_expression": EXPRESSION_TEXTS[operator],
            "domain": domain["slug"],
            "template_family": template_family,
            "state_key": "".join("1" if bit else "0" for bit in state),
            "choice_count": k,
            "split": split,
            "mapping_style": mapping_style,
            "condition_order": "".join(condition_order),
            "distractor_classes": dict(distractor_classes),
        }
        records.append(record)
    if records[0]["target"]["choice_id"] == records[1]["target"]["choice_id"]:
        raise AssertionError(f"Non-contrastive pair generated: {records[0]['group_id']}")
    return records


def generate_bridge_records(seed: int = 3101, pair_count: int = 240) -> List[Dict[str, Any]]:
    """Generate 240 independent contrastive pairs for the Logic Bridge."""
    if pair_count != 240:
        raise ValueError("The RC3.1 Logic Bridge target is fixed at 240 pairs")
    records: List[Dict[str, Any]] = []
    partner_counts: Counter[str] = Counter()
    seed_offset = int(seed) % len(OPERATOR_FAMILIES)
    for pair_index in range(pair_count):
        operator_index = (pair_index + seed_offset) % len(OPERATOR_FAMILIES)
        repetition = pair_index // len(OPERATOR_FAMILIES)
        first_operator = OPERATOR_FAMILIES[operator_index]
        state = _state_for(first_operator, repetition)
        second_operator = _find_partner(first_operator, state, repetition + 1, partner_counts)
        partner_counts[second_operator] += 1
        domain = BRIDGE_DOMAINS[(operator_index * 7 + repetition) % len(BRIDGE_DOMAINS)]
        k = (2, 3, 4, 6)[pair_index % 4]
        template_family = BRIDGE_TEMPLATE_FAMILIES[pair_index % len(BRIDGE_TEMPLATE_FAMILIES)]
        mapping_style = MAPPING_STYLES[pair_index % len(MAPPING_STYLES)]
        condition_order = CONDITION_ORDERS[(pair_index + seed_offset) % len(CONDITION_ORDERS)]
        records.extend(
            _make_pair(
                domain,
                state,
                first_operator,
                second_operator,
                k,
                pair_index,
                template_family,
                "bridge",
                mapping_style,
                condition_order,
                seed,
            )
        )
    return records


def generate_train_records(seed: int = 3102) -> List[Dict[str, Any]]:
    """Generate non-duplicated RC3.1 continual-training/dev/calibration data."""
    records: List[Dict[str, Any]] = []
    partner_counts: Counter[str] = Counter()
    seed_offset = int(seed) % len(OPERATOR_FAMILIES)
    pair_index = 0
    for domain_index, domain in enumerate(TRAIN_DOMAINS):
        # Keep dev/calibration domains completely held out while meeting the
        # RC3.1 artifact target: 1,920 train records and 240 each for dev and
        # calibration.  The pair counts are divisible by the K schedule.
        if domain_index < 10:
            split = "train"
            pair_count = 96
        elif domain_index == 10:
            split = "dev"
            pair_count = 120
        else:
            split = "calibration"
            pair_count = 120
        templates = TRAIN_TEMPLATE_FAMILIES[split]
        for local_index in range(pair_count):
            operator_index = (local_index + domain_index * 3 + seed_offset) % len(OPERATOR_FAMILIES)
            first_operator = OPERATOR_FAMILIES[operator_index]
            # Index states by the operator's global occurrence, not by local
            # domain position, so every operator receives its complete truth
            # state set even when domains are split-held-out.
            state = _state_for(first_operator, (pair_index // len(OPERATOR_FAMILIES)) + seed_offset)
            second_operator = _find_partner(first_operator, state, local_index + 2 + seed_offset, partner_counts)
            partner_counts[second_operator] += 1
            k = (2, 3, 4, 6)[local_index % 4]
            template_family = templates[local_index % len(templates)]
            mapping_style = MAPPING_STYLES[(pair_index + seed_offset) % len(MAPPING_STYLES)]
            condition_order = CONDITION_ORDERS[(pair_index + domain_index + seed_offset) % len(CONDITION_ORDERS)]
            records.extend(
                _make_pair(
                    domain,
                    state,
                    first_operator,
                    second_operator,
                    k,
                    pair_index,
                    template_family,
                    split,
                    mapping_style,
                    condition_order,
                    seed,
                )
            )
            pair_index += 1
    return records


def generate_all(seed: int = 3101) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    return generate_train_records(seed + 1), generate_bridge_records(seed)
