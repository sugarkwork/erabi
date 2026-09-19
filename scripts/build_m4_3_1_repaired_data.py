"""Data Generator & Semantic Repair for ERABI M4.3.1.

Fixes the Rule A sampling bug in game_action and facility_control,
aligns context descriptions with truth states,
and rigorously audits 100% of generated records using the independent semantic validator.

Outputs to:
- data/m4_3_1_phrasing_fix/phrasing_train.jsonl (240 records / 120 pairs: Families E~J)
- data/m4_3_1_phrasing_fix/phrasing_dev.jsonl (80 records / 40 pairs: Families K~L)
- data/m4_3_1_phrasing_fix/fresh_phrasing_eval.jsonl (120 records / 60 pairs: Families M~P)
- data/m4_3_1_phrasing_fix/combined_train.jsonl (1080 records)
- data/m4_3_1_phrasing_fix/combined_dev.jsonl (220 records)
- data/m4_3_1_phrasing_fix/diagnostic_fix/cell_a_old_domain_old_phrasing.jsonl (40 records / 20 pairs)
- data/m4_3_1_phrasing_fix/diagnostic_fix/cell_b_old_domain_new_phrasing.jsonl (40 records / 20 pairs)
- data/m4_3_1_phrasing_fix/manifest.json
- data/m4_3_1_phrasing_fix/semantic_audit.json
"""

from __future__ import annotations

import hashlib
import json
import os
import random
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

from erabi.semantic_validator import derive_semantics, validate_dataset

ROOT = Path(__file__).resolve().parent.parent

PAST_DATASETS = [
    ROOT / "data/m3_3_v2/train.jsonl",
    ROOT / "data/m3_3_v2/dev.jsonl",
    ROOT / "data/m3_3_v2/eval_v2.jsonl",
    ROOT / "data/m3_6_cal/calibration.jsonl",
    ROOT / "data/m3_6_cal/fresh_eval.jsonl",
    ROOT / "data/m4_1_exception/train_exception.jsonl",
    ROOT / "data/m4_1_exception/dev_exception.jsonl",
    ROOT / "data/m4_1_exception/eval_exception.jsonl",
    ROOT / "data/m4_2_robustness/novel_priority_eval.jsonl",
    ROOT / "data/m4_2_1_diagnostic/cell_a_old_domain_old_phrasing.jsonl",
    ROOT / "data/m4_2_1_diagnostic/cell_b_old_domain_new_phrasing.jsonl",
    ROOT / "data/m4_2_1_diagnostic/cell_c_new_domain_old_phrasing.jsonl",
    ROOT / "data/m3_1/transfer_probe.jsonl",
    ROOT / "examples/smoke_cases.jsonl",
]


def compute_fingerprint(record: Dict[str, Any]) -> str:
    ctx = record.get("context", "").strip()
    q = record.get("question", "").strip()
    c_texts = "||".join(c["text"].strip() for c in record.get("choices", []))
    raw = f"{ctx} ||| {q} ||| {c_texts}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# 8 Domains: 4 from OLD (M4.1) + 4 from NEW (M4.2)
# Rigorously defined with rule_a_true_range and rule_a_false_range
DOMAINS = [
    # 1. game_action (OLD)
    {
        "domain": "game_action",
        "domain_class": "old",
        "choices": [
            {"id": "heal", "text": "回復する"},
            {"id": "continue", "text": "移動を継続する"},
            {"id": "wait", "text": "待機する"},
        ],
        "rule_a_name": "HP基準",
        "rule_a_desc": "HPが20未満なら「回復する」",
        "rule_b_name": "移動例外",
        "rule_b_desc": "安全地帯等への移動中・進軍中なら「移動を継続する」",
        "fallback_text": "待機する",
        "action_a": "heal",
        "action_b": "continue",
        "action_fallback": "wait",
        "rule_a_true_range": (5, 19),    # HP < 20
        "rule_a_false_range": (22, 50),  # HP >= 20
        "contexts_conflict": [
            ("現在のプレイヤーのHPは{v1}です（危険水域）。回復アイテムあり。現在、安全地帯へ移動中。", True, True),
            ("状況：HPは{v1}（危険水域）。ポーション所持。部隊は前線へ進軍中。", True, True),
            ("ステータス：残り体力{v1}。救急キットあり。目的地へ急行中。", True, True),
        ],
        "contexts_single_a": [
            ("現在のプレイヤーのHPは{v1}です（危険水域）。回復アイテムあり。移動はしておらず安全地帯に滞在中。", True, False),
            ("状況：HPは{v1}（危険水域）。ポーション所持。現在は停止して索敵中。", True, False),
        ],
        "contexts_single_b": [
            ("現在のプレイヤーのHPは{v1}です（危険水域外）。HPは十分あり。現在、安全地帯へ移動中。", False, True),
            ("ステータス：体力十分（{v1}）。部隊は前線へ進軍中。", False, True),
        ],
        "contexts_fallback": [
            ("現在のプレイヤーのHPは{v1}（危険水域外）。移動はしておらず安全地帯に滞在中。", False, False),
            ("状況：HPは{v1}で十分。停止して周囲を索敵中。", False, False),
        ],
    },
    # 2. delivery_dispatch (OLD)
    {
        "domain": "delivery_dispatch",
        "domain_class": "old",
        "choices": [
            {"id": "standard", "text": "通常便で発送"},
            {"id": "express", "text": "特急便で発送"},
            {"id": "hold", "text": "保留にする"},
        ],
        "rule_a_name": "重量基準",
        "rule_a_desc": "重量が30kg以上なら「通常便で発送」",
        "rule_b_name": "緊急例外",
        "rule_b_desc": "至急・特急・緊急配送の指定があれば「特急便で発送」",
        "fallback_text": "保留にする",
        "action_a": "standard",
        "action_b": "express",
        "action_fallback": "hold",
        "rule_a_true_range": (35, 55),   # weight >= 30
        "rule_a_false_range": (12, 25),  # weight < 30
        "contexts_conflict": [
            ("荷物の重量は{v1}kgです。荷主より当日中の至急配送要請あり。", True, True),
            ("検品結果：総重量{v1}kg。伝票に「特急指定・緊急扱い」の記載あり。", True, True),
            ("配送依頼：積載重量{v1}kg。顧客からの緊急配送コールを受付済み。", True, True),
        ],
        "contexts_single_a": [
            ("荷物の重量は{v1}kgです。至急要請はなく通常納期での依頼です。", True, False),
            ("検品結果：総重量{v1}kg。特急指定はなく期日通りの配送希望です。", True, False),
        ],
        "contexts_single_b": [
            ("荷物の重量は{v1}kg（基準未満）。荷主より当日中の至急配送要請あり。", False, True),
            ("検品結果：総重量{v1}kg（基準未満）。伝票に「特急指定・緊急扱い」の記載あり。", False, True),
        ],
        "contexts_fallback": [
            ("荷物の重量は{v1}kg（基準未満）。至急要請はなく通常納期です。", False, False),
            ("検品結果：総重量{v1}kg（基準未満）。特急指定はなく期日通りの配送希望です。", False, False),
        ],
    },
    # 3. system_ops (OLD)
    {
        "domain": "system_ops",
        "domain_class": "old",
        "choices": [
            {"id": "scale_up", "text": "スケールアップ実行"},
            {"id": "isolate", "text": "ネットワーク遮断"},
            {"id": "monitor", "text": "監視継続"},
        ],
        "rule_a_name": "負荷基準",
        "rule_a_desc": "CPU使用率が80%以上なら「スケールアップ実行」",
        "rule_b_name": "保安例外",
        "rule_b_desc": "不正侵入・マルウェア・侵害検知時は即座に「ネットワーク遮断」",
        "fallback_text": "監視継続",
        "action_a": "scale_up",
        "action_b": "isolate",
        "action_fallback": "monitor",
        "rule_a_true_range": (85, 96),   # CPU >= 80
        "rule_a_false_range": (30, 65),  # CPU < 80
        "contexts_conflict": [
            ("サーバーCPU使用率は{v1}%です。同時に外部からの不正侵入アラート検知あり。", True, True),
            ("クラスター監視：CPU負荷率{v1}%。セキュリティ監視からマルウェア通信警告あり。", True, True),
            ("システム状況：プロセッサ負荷{v1}%。未知の管理者権限奪取の形跡を検知。", True, True),
        ],
        "contexts_single_a": [
            ("サーバーCPU使用率は{v1}%です。セキュリティ侵害のアラートは発生していません。", True, False),
            ("クラスター監視：CPU負荷率{v1}%。不正アクセスの兆候はなく安全です。", True, False),
        ],
        "contexts_single_b": [
            ("サーバーCPU使用率は{v1}%（負荷基準未満）。外部からの不正侵入アラート検知あり。", False, True),
            ("クラスター監視：CPU負荷率{v1}%（負荷基準未満）。セキュリティ監視からマルウェア通信警告あり。", False, True),
        ],
        "contexts_fallback": [
            ("サーバーCPU使用率は{v1}%（負荷基準未満）。セキュリティ侵害アラートなし。", False, False),
            ("システム状況：プロセッサ負荷{v1}%（負荷基準未満）。侵害の形跡はなく平穏です。", False, False),
        ],
    },
    # 4. facility_control (OLD)
    {
        "domain": "facility_control",
        "domain_class": "old",
        "choices": [
            {"id": "eco_mode", "text": "省エネ運転へ切替"},
            {"id": "emergency_stop", "text": "即時非常停止"},
            {"id": "normal_run", "text": "通常運転維持"},
        ],
        "rule_a_name": "温度基準",
        "rule_a_desc": "室温が25度以下なら「省エネ運転へ切替」",
        "rule_b_name": "安全例外",
        "rule_b_desc": "非常停止信号・警報・緊急ボタン検知時は「即時非常停止」",
        "fallback_text": "通常運転維持",
        "action_a": "eco_mode",
        "action_b": "emergency_stop",
        "action_fallback": "normal_run",
        "rule_a_true_range": (12, 25),   # temp <= 25
        "rule_a_false_range": (26, 42),  # temp > 25
        "contexts_conflict": [
            ("工場フロア：室温測定値{v1}度（省エネ基準以下）。火災検知器が作動し非常警報が鳴動中。", True, True),
            ("設備空調モニター：現在温度{v1}度（25度以下）。安全管理盤より緊急停止シグナル受信。", True, True),
            ("生産ライン環境：エリア温度{v1}度（基準以下）。作業員による非常停止ボタン押下検知。", True, True),
        ],
        "contexts_single_a": [
            ("工場フロア：室温測定値{v1}度（省エネ基準以下）。非常警報や安全停止信号は検知されていません。", True, False),
            ("設備空調モニター：現在温度{v1}度（25度以下）。安全システムは正常、警報なし。", True, False),
        ],
        "contexts_single_b": [
            ("工場フロア：室温測定値{v1}度（25度超過）。火災検知器が作動し非常警報が鳴動中。", False, True),
            ("生産ライン環境：エリア温度{v1}度（25度超過）。作業員による非常停止ボタン押下検知。", False, True),
        ],
        "contexts_fallback": [
            ("工場フロア：室温測定値{v1}度（25度超過）。警報や非常信号は検知されていません。", False, False),
            ("設備空調モニター：現在温度{v1}度（25度超過）。安全システム正常、警報なし。", False, False),
        ],
    },
    # 5. manufacturing (NEW)
    {
        "domain": "manufacturing",
        "domain_class": "new",
        "choices": [
            {"id": "pass", "text": "通常合格とする"},
            {"id": "recheck", "text": "再検査ラインへ送る"},
            {"id": "hold", "text": "規格外保留とする"},
        ],
        "rule_a_name": "寸法基準",
        "rule_a_desc": "寸法誤差0.04mm以下なら「通常合格とする」",
        "rule_b_name": "外観基準",
        "rule_b_desc": "外観キズ検知時は「再検査ラインへ送る」",
        "fallback_text": "規格外保留とする",
        "action_a": "pass",
        "action_b": "recheck",
        "action_fallback": "hold",
        "rule_a_true_range": (0.012, 0.038),  # error <= 0.04
        "rule_a_false_range": (0.045, 0.080), # error > 0.04
        "contexts_conflict": [
            ("製品検査：寸法誤差は{err:.3f}mm（公差内）。表面キズを検知。", True, True),
            ("精密測定：測定誤差{err:.3f}mm。外観打痕を検出。", True, True),
            ("ロット測定：誤差{err:.3f}mm。微小異物付着のアラートあり。", True, True),
        ],
        "contexts_single_a": [
            ("製品検査：寸法誤差は{err:.3f}mm（公差内）。欠陥なし。", True, False),
            ("精密測定：測定誤差{err:.3f}mm。キズなし、画像診断は正常判定。", True, False),
        ],
        "contexts_single_b": [
            ("製品検査：寸法誤差は{err:.3f}mm（基準超過）。表面キズを検知。", False, True),
            ("精密測定：測定誤差{err:.3f}mm（基準超過）。外観打痕を検出。", False, True),
        ],
        "contexts_fallback": [
            ("製品検査：寸法誤差は{err:.3f}mm（基準超過）。キズなし、外観センサーは正常。", False, False),
            ("精密測定：測定誤差{err:.3f}mm（基準超過）。欠陥なし。", False, False),
        ],
    },
    # 6. facility_power (NEW)
    {
        "domain": "facility_power",
        "domain_class": "new",
        "choices": [
            {"id": "peak_cut", "text": "ピークカット運転へ移行"},
            {"id": "battery", "text": "蓄電池放電へ切替"},
            {"id": "normal", "text": "通常給電を維持"},
        ],
        "rule_a_name": "買電ピーク基準",
        "rule_a_desc": "買電電力400kW以上なら「ピークカット運転へ移行」",
        "rule_b_name": "蓄電池基準",
        "rule_b_desc": "蓄電池残量90%以上なら「蓄電池放電へ切替」",
        "fallback_text": "通常給電を維持",
        "action_a": "peak_cut",
        "action_b": "battery",
        "action_fallback": "normal",
        "rule_a_true_range": (415, 490),  # kW >= 400
        "rule_a_false_range": (310, 385), # kW < 400
        "rule_b_true_range": (91, 98),    # SOC >= 90
        "rule_b_false_range": (40, 75),   # SOC < 90
        "contexts_conflict": [
            ("エネルギー管理：受電電力{kw}kW（400kW超）。蓄電池SOCは{soc}%（満充電帯）。", True, True),
            ("施設受電状況：受電電力{kw}kW。施設側蓄電システム残量は{soc}%（十分な残量あり）。", True, True),
            ("電力監視ログ：現在消費{kw}kW。定置型蓄電池の充電率は{soc}%に達しています。", True, True),
        ],
        "contexts_single_a": [
            ("エネルギー管理：受電電力{kw}kW。蓄電池SOCは{soc}%（放電基準未満）。", True, False),
            ("施設受電状況：受電電力{kw}kW。蓄電池残量は{soc}%で蓄電余力なし。", True, False),
        ],
        "contexts_single_b": [
            ("エネルギー管理：受電電力{kw}kW（400kW未満）。蓄電池SOCは{soc}%（満充電帯）。", False, True),
            ("施設受電状況：受電電力{kw}kW（400kW未満）。蓄電池残量{soc}%（十分な残量あり）。", False, True),
        ],
        "contexts_fallback": [
            ("エネルギー管理：受電電力{kw}kW（400kW未満）。蓄電池SOCは{soc}%（放電基準未満）。", False, False),
            ("電力監視ログ：現在消費{kw}kW（400kW未満）。蓄電池残量は{soc}%で蓄電余力なし。", False, False),
        ],
    },
    # 7. inventory (NEW)
    {
        "domain": "inventory",
        "domain_class": "new",
        "choices": [
            {"id": "fifo_ship", "text": "先出出荷とする"},
            {"id": "quarantine", "text": "出荷保留・隔離"},
            {"id": "standard_ship", "text": "通常出庫とする"},
        ],
        "rule_a_name": "滞留基準",
        "rule_a_desc": "保管日数180日以上なら「先出出荷とする」",
        "rule_b_name": "検疫基準",
        "rule_b_desc": "検疫・品質確認指定ロットは「出荷保留・隔離」",
        "fallback_text": "通常出庫とする",
        "action_a": "fifo_ship",
        "action_b": "quarantine",
        "action_fallback": "standard_ship",
        "rule_a_true_range": (185, 290),  # days >= 180
        "rule_a_false_range": (30, 140),  # days < 180
        "contexts_conflict": [
            ("倉庫管理：保管日数{days}日（長期滞留）。管理システムに「検疫検査・品質再確認対象」の指定あり。", True, True),
            ("在庫ステータス：入庫から{days}日経過。出荷伝票に「品質監査指定ロット・隔離要」のタグあり。", True, True),
            ("出荷指示照会：保管期間{days}日。検疫管理フラグが有効化されています。", True, True),
        ],
        "contexts_single_a": [
            ("倉庫管理：保管日数{days}日（長期滞留）。検疫指定はなく、品質検査済み通常ロット。", True, False),
            ("在庫ステータス：入庫から{days}日経過。出荷伝票に検疫・保留の指定は一切なし。", True, False),
        ],
        "contexts_single_b": [
            ("倉庫管理：保管日数{days}日（直近入庫）。管理システムに「検疫検査対象」の指定あり。", False, True),
            ("在庫ステータス：入庫から{days}日。検疫管理フラグが有効化されています。", False, True),
        ],
        "contexts_fallback": [
            ("倉庫管理：保管日数{days}日（直近入庫）。検疫指定はなく、通常品です。", False, False),
            ("在庫ステータス：入庫から{days}日。検疫タグなし、通常品です。", False, False),
        ],
    },
    # 8. job_scheduler (NEW)
    {
        "domain": "job_scheduler",
        "domain_class": "new",
        "choices": [
            {"id": "promote_queue", "text": "優先キューへ昇格"},
            {"id": "defer_night", "text": "夜間バッチへ延期"},
            {"id": "standard_run", "text": "通常順次実行"},
        ],
        "rule_a_name": "待機時間基準",
        "rule_a_desc": "待機時間60分以上なら「優先キューへ昇格」",
        "rule_b_name": "資源負荷基準",
        "rule_b_desc": "メモリ消費64GB以上の大型ジョブは「夜間バッチへ延期」",
        "fallback_text": "通常順次実行",
        "action_a": "promote_queue",
        "action_b": "defer_night",
        "action_fallback": "standard_run",
        "rule_a_true_range": (65, 180),  # mins >= 60
        "rule_a_false_range": (10, 45),  # mins < 60
        "rule_b_true_range": (70, 256),  # mem >= 64
        "rule_b_false_range": (8, 32),   # mem < 64
        "contexts_conflict": [
            ("ジョブ実行状況：キュー待機時間{mins}分。要求メモリ{mem}GB（64GB超の特大ジョブ）。", True, True),
            ("スケジューラ監視：待ち時間{mins}分経過。リソース定義：メモリ{mem}GBの専有バッチジョブ。", True, True),
            ("計算ノード依頼：キュー滞在{mins}分。大容量メモリ要求（{mem}GB）フラグが付与。", True, True),
        ],
        "contexts_single_a": [
            ("ジョブ実行状況：キュー待機時間{mins}分。要求メモリ{mem}GB（標準規模のメモリ消費）。", True, False),
            ("スケジューラ監視：待ち時間{mins}分経過。メモリ要求{mem}GB、大規模フラグなし。", True, False),
        ],
        "contexts_single_b": [
            ("ジョブ実行状況：キュー待機時間{mins}分（投入直後）。要求メモリ{mem}GB（特大ジョブ）。", False, True),
            ("計算ノード依頼：キュー滞在{mins}分。メモリ要求{mem}GBの専有バッチ指定あり。", False, True),
        ],
        "contexts_fallback": [
            ("ジョブ実行状況：キュー待機時間{mins}分（投入直後）。要求メモリ{mem}GB、標準規模ジョブ。", False, False),
            ("スケジューラ監視：待ち時間{mins}分経過。メモリ要求{mem}GB、特大フラグなし。", False, False),
        ],
    },
]


def format_question_by_family(
    family: str,
    priority_order: str,
    rule_a_name: str,
    rule_a_desc: str,
    rule_b_name: str,
    rule_b_desc: str,
    fallback_text: str,
) -> str:
    """Format question based on the exact phrasing family."""
    # --- TRAIN FAMILIES (E ~ J) ---
    if family == "family_E":
        if priority_order == "A_over_B":
            return (
                f"ルール：原則として{rule_b_name}（{rule_b_desc}）を使う。ただし{rule_a_name}（{rule_a_desc}）が成立する場合は、"
                f"{rule_a_name}を{rule_b_name}より優先する。どちらも該当しない場合は「{fallback_text}」。規則に従って行動を選択してください。"
            )
        else:
            return (
                f"ルール：原則として{rule_a_name}（{rule_a_desc}）を使う。ただし{rule_b_name}（{rule_b_desc}）が成立する場合は、"
                f"{rule_b_name}を{rule_a_name}より優先する。どちらも該当しない場合は「{fallback_text}」。規則に従って行動を選択してください。"
            )

    elif family == "family_F":
        if priority_order == "A_over_B":
            return (
                f"ルール：{rule_a_name}（{rule_a_desc}）と{rule_b_name}（{rule_b_desc}）の判定が競合した場合は{rule_a_name}を採用する。"
                f"一方だけ成立する場合はその成立した規則に従い、どちらも不成立なら「{fallback_text}」。規則に従って行動を選択してください。"
            )
        else:
            return (
                f"ルール：{rule_a_name}（{rule_a_desc}）と{rule_b_name}（{rule_b_desc}）の判定が競合した場合は{rule_b_name}を採用する。"
                f"一方だけ成立する場合はその成立した規則に従い、どちらも不成立なら「{fallback_text}」。規則に従って行動を選択してください。"
            )

    elif family == "family_G":
        if priority_order == "A_over_B":
            return (
                f"ルール：{rule_a_name}（{rule_a_desc}）を上位規則、{rule_b_name}（{rule_b_desc}）を下位規則とする。"
                f"両方成立した場合は上位規則を採用し、どちらも該当しない場合は「{fallback_text}」。規則に従って行動を選択してください。"
            )
        else:
            return (
                f"ルール：{rule_b_name}（{rule_b_desc}）を上位規則、{rule_a_name}（{rule_a_desc}）を下位規則とする。"
                f"両方成立した場合は上位規則を採用し、どちらも該当しない場合は「{fallback_text}」。規則に従って行動を選択してください。"
            )

    elif family == "family_H":
        if priority_order == "A_over_B":
            return (
                f"ルール：通常の判定は{rule_b_name}（{rule_b_desc}）で行う。{rule_a_name}（{rule_a_desc}）の条件が成立した場合だけ、"
                f"結果を{rule_a_name}で上書きする。どちらも満たさない場合は「{fallback_text}」。規則に従って行動を選択してください。"
            )
        else:
            return (
                f"ルール：通常の判定は{rule_a_name}（{rule_a_desc}）で行う。{rule_b_name}（{rule_b_desc}）の条件が成立した場合だけ、"
                f"結果を{rule_b_name}で上書きする。どちらも満たさない場合は「{fallback_text}」。規則に従って行動を選択してください。"
            )

    elif family == "family_I":
        if priority_order == "A_over_B":
            return (
                f"ルール：優先順位：1位：{rule_a_name}（{rule_a_desc}）、2位：{rule_b_name}（{rule_b_desc}）。"
                f"成立している規則のうち順位が最も高いものを使い、どちらも該当しない場合は「{fallback_text}」。規則に従って行動を選択してください。"
            )
        else:
            return (
                f"ルール：優先順位：1位：{rule_b_name}（{rule_b_desc}）、2位：{rule_a_name}（{rule_a_desc}）。"
                f"成立している規則のうち順位が最も高いものを使い、どちらも該当しない場合は「{fallback_text}」。規則に従って行動を選択してください。"
            )

    elif family == "family_J":
        if priority_order == "A_over_B":
            return (
                f"ルール：{rule_a_name}（{rule_a_desc}）と{rule_b_name}（{rule_b_desc}）の両方が成立したときは{rule_a_name}を選ぶ。"
                f"片方だけ成立した場合は成立側を選び、どちらも成立しなければ「{fallback_text}」を選ぶ。規則に従って行動を選択してください。"
            )
        else:
            return (
                f"ルール：{rule_a_name}（{rule_a_desc}）と{rule_b_name}（{rule_b_desc}）の両方が成立したときは{rule_b_name}を選ぶ。"
                f"片方だけ成立した場合は成立側を選び、どちらも成立しなければ「{fallback_text}」を選ぶ。規則に従って行動を選択してください。"
            )

    # --- DEV FAMILIES (K ~ L) ---
    elif family == "family_K":
        if priority_order == "A_over_B":
            return (
                f"ルール：判断方針として、{rule_b_name}（{rule_b_desc}）より{rule_a_name}（{rule_a_desc}）を優先する。"
                f"競合しなければ成立している条件をそのまま採用し、どちらも不成立なら「{fallback_text}」。規則に従って行動を選択してください。"
            )
        else:
            return (
                f"ルール：判断方針として、{rule_a_name}（{rule_a_desc}）より{rule_b_name}（{rule_b_desc}）を優先する。"
                f"競合しなければ成立している条件をそのまま採用し、どちらも不成立なら「{fallback_text}」。規則に従って行動を選択してください。"
            )

    elif family == "family_L":
        if priority_order == "A_over_B":
            return (
                f"ルール：{rule_a_name}（{rule_a_desc}）は{rule_b_name}（{rule_b_desc}）に先行して評価される。"
                f"先行側が成立した場合はその結果を用い、不成立の場合に後行側を評価する。いずれも満たさない場合は「{fallback_text}」。規則に従って行動を選択してください。"
            )
        else:
            return (
                f"ルール：{rule_b_name}（{rule_b_desc}）は{rule_a_name}（{rule_a_desc}）に先行して評価される。"
                f"先行側が成立した場合はその結果を用い、不成立の場合に後行側を評価する。いずれも満たさない場合は「{fallback_text}」。規則に従って行動を選択してください。"
            )

    # --- FRESH EVAL FAMILIES (M ~ P) ---
    elif family == "family_M":
        if priority_order == "A_over_B":
            return (
                f"ルール：両規則{rule_a_name}（{rule_a_desc}）と{rule_b_name}（{rule_b_desc}）が該当するケースでは{rule_a_name}側の判断を採る。"
                f"それ以外は該当した規則の判断を採り、どちらも該当しなければ「{fallback_text}」。規則に従って行動を選択してください。"
            )
        else:
            return (
                f"ルール：両規則{rule_a_name}（{rule_a_desc}）と{rule_b_name}（{rule_b_desc}）が該当するケースでは{rule_b_name}側の判断を採る。"
                f"それ以外は該当した規則の判断を採り、どちらも該当しなければ「{fallback_text}」。規則に従って行動を選択してください。"
            )

    elif family == "family_N":
        if priority_order == "A_over_B":
            return (
                f"ルール：{rule_a_name}（{rule_a_desc}）と{rule_b_name}（{rule_b_desc}）の判定が重なった場合の決定権は{rule_a_name}にある。"
                f"重複しない場合は該当した規則を適用し、どちらも該当しないなら「{fallback_text}」。規則に従って行動を選択してください。"
            )
        else:
            return (
                f"ルール：{rule_a_name}（{rule_a_desc}）と{rule_b_name}（{rule_b_desc}）の判定が重なった場合の決定権は{rule_b_name}にある。"
                f"重複しない場合は該当した規則を適用し、どちらも該当しないなら「{fallback_text}」。規則に従って行動を選択してください。"
            )

    elif family == "family_O":
        if priority_order == "A_over_B":
            return (
                f"ルール：{rule_b_name}（{rule_b_desc}）を基本判定とするが、{rule_a_name}（{rule_a_desc}）の成立時には{rule_a_name}の結論を最終結果とする。"
                f"いずれの条件も満たさない場合は「{fallback_text}」。規則に従って行動を選択してください。"
            )
        else:
            return (
                f"ルール：{rule_a_name}（{rule_a_desc}）を基本判定とするが、{rule_b_name}（{rule_b_desc}）の成立時には{rule_b_name}の結論を最終結果とする。"
                f"いずれの条件も満たさない場合は「{fallback_text}」。規則に従って行動を選択してください。"
            )

    elif family == "family_P":
        if priority_order == "A_over_B":
            return (
                f"ルール：競合解決順は{rule_a_name}、{rule_b_name}の順。"
                f"最初に成立した規則の結果を採用し、どちらも不成立なら「{fallback_text}」。規則に従って行動を選択してください。"
            )
        else:
            return (
                f"ルール：競合解決順は{rule_b_name}、{rule_a_name}の順。"
                f"最初に成立した規則の結果を採用し、どちらも不成立なら「{fallback_text}」。規則に従って行動を選択してください。"
            )

    # --- HISTORICAL FAMILIES (A ~ D) for Cell A/B ---
    elif family == "family_A":
        if priority_order == "A_over_B":
            return f"ルール：①【最優先】{rule_a_name}（{rule_a_desc}） ②【次点】{rule_b_name}（{rule_b_desc}）。どちらも非該当なら「{fallback_text}」。規則に従って行動を選択してください。"
        else:
            return f"ルール：①【最優先】{rule_b_name}（{rule_b_desc}） ②【次点】{rule_a_name}（{rule_a_desc}）。どちらも非該当なら「{fallback_text}」。規則に従って行動を選択してください。"

    elif family == "family_B":
        if priority_order == "A_over_B":
            return f"ルール：「{rule_a_desc}」と「{rule_b_desc}」が同時に成立する場合のみ、{rule_a_name}を優先する。それ以外は成立した側の判定を適用し、どちらも不成立なら「{fallback_text}」。規則に従って行動を選択してください。"
        else:
            return f"ルール：「{rule_a_desc}」と「{rule_b_desc}」が同時に成立する場合のみ、{rule_b_name}を優先する。それ以外は成立した側の判定を適用し、どちらも不成立なら「{fallback_text}」。規則に従って行動を選択してください。"

    elif family == "family_C":
        if priority_order == "A_over_B":
            return f"ルール：優先度は {rule_a_name}（{rule_a_desc}） > {rule_b_name}（{rule_b_desc}）。両方適用可能なら上位の規則を採用する。どちらも該当しない場合は「{fallback_text}」。規則に従って行動を選択してください。"
        else:
            return f"ルール：優先度は {rule_b_name}（{rule_b_desc}） > {rule_a_name}（{rule_a_desc}）。両方適用可能なら上位の規則を採用する。どちらも該当しない場合は「{fallback_text}」。規則に従って行動を選択してください。"

    elif family == "family_D":
        if priority_order == "A_over_B":
            return f"ルール：第一判断：{rule_b_name}（{rule_b_desc}）。例外条件：{rule_a_name}（{rule_a_desc}）。例外条件を満たした場合、第一判断を上書きする。いずれも満たさない場合は「{fallback_text}」。規則に従って行動を選択してください。"
        else:
            return f"ルール：第一判断：{rule_a_name}（{rule_a_desc}）。例外条件：{rule_b_name}（{rule_b_desc}）。例外条件を満たした場合、第一判断を上書きする。いずれも満たさない場合は「{fallback_text}」。規則に従って行動を選択してください。"

    else:
        raise ValueError(f"Unknown family: {family}")


def sample_context_for_stratum(dom: Dict[str, Any], stratum: str, s_idx: int, rng: random.Random) -> Tuple[str, bool, bool, Any]:
    """Sample context and numerical values strictly according to truth state."""
    d_name = dom["domain"]
    if stratum == "conflict":
        target_a, target_b = True, True
        pool = dom["contexts_conflict"]
    elif stratum == "single":
        if s_idx % 2 == 0:
            target_a, target_b = True, False
            pool = dom["contexts_single_a"]
        else:
            target_a, target_b = False, True
            pool = dom["contexts_single_b"]
    else:  # fallback
        target_a, target_b = False, False
        pool = dom["contexts_fallback"]

    tmpl, c_a, c_b = rng.choice(pool)
    assert c_a == target_a and c_b == target_b

    # Sample numbers matching target truth states
    if d_name in ["game_action", "delivery_dispatch", "system_ops", "facility_control", "customer_service"]:
        r_a = dom["rule_a_true_range"] if target_a else dom["rule_a_false_range"]
        v1 = rng.randint(r_a[0], r_a[1])
        context_text = tmpl.format(v1=v1)
        sem_state = (d_name, v1, target_a, target_b, stratum)

    elif d_name == "manufacturing":
        r_a = dom["rule_a_true_range"] if target_a else dom["rule_a_false_range"]
        err = round(rng.uniform(r_a[0], r_a[1]), 3)
        context_text = tmpl.format(err=err)
        sem_state = (d_name, err, target_a, target_b, stratum)

    elif d_name == "facility_power":
        r_a = dom["rule_a_true_range"] if target_a else dom["rule_a_false_range"]
        r_b = dom["rule_b_true_range"] if target_b else dom["rule_b_false_range"]
        kw = rng.randint(r_a[0], r_a[1])
        soc = rng.randint(r_b[0], r_b[1])
        context_text = tmpl.format(kw=kw, soc=soc)
        sem_state = (d_name, kw, soc, target_a, target_b, stratum)

    elif d_name == "inventory":
        r_a = dom["rule_a_true_range"] if target_a else dom["rule_a_false_range"]
        days = rng.randint(r_a[0], r_a[1])
        context_text = tmpl.format(days=days)
        sem_state = (d_name, days, target_a, target_b, stratum)

    elif d_name == "job_scheduler":
        r_a = dom["rule_a_true_range"] if target_a else dom["rule_a_false_range"]
        r_b = dom["rule_b_true_range"] if target_b else dom["rule_b_false_range"]
        mins = rng.randint(r_a[0], r_a[1])
        mem = rng.randint(r_b[0], r_b[1])
        context_text = tmpl.format(mins=mins, mem=mem)
        sem_state = (d_name, mins, mem, target_a, target_b, stratum)

    else:
        raise ValueError(f"Unknown domain {d_name}")

    return context_text, target_a, target_b, sem_state


def generate_split_dataset(
    split_name: str,
    families: List[str],
    total_pairs: int,
    diff_pairs_quota: int,
    single_pairs_quota: int,
    fallback_pairs_quota: int,
    seed: int,
    global_fps: set,
    allowed_domains: List[Dict[str, Any]] = None,
    external_sem_states: set = None,
) -> Tuple[List[Dict[str, Any]], set]:
    """Generate pair dataset with strict stratum quotas and semantic verification."""
    rng = random.Random(seed)
    if allowed_domains is None:
        domains = DOMAINS
    else:
        domains = allowed_domains

    # Build quota list per family, distributing remainders
    diff_base = diff_pairs_quota // len(families)
    diff_rem = diff_pairs_quota % len(families)
    single_base = single_pairs_quota // len(families)
    single_rem = single_pairs_quota % len(families)
    fallback_base = fallback_pairs_quota // len(families)
    fallback_rem = fallback_pairs_quota % len(families)

    records: List[Dict[str, Any]] = []
    semantic_states = set()
    pair_idx = 0

    for fam_idx, family in enumerate(families):
        n_diff = diff_base + (1 if fam_idx < diff_rem else 0)
        n_single = single_base + (1 if fam_idx < single_rem else 0)
        n_fallback = fallback_base + (1 if fam_idx < fallback_rem else 0)

        strata_plan = (
            ["conflict"] * n_diff
            + ["single"] * n_single
            + ["fallback"] * n_fallback
        )
        rng.shuffle(strata_plan)

        for s_idx, stratum_type in enumerate(strata_plan):
            group_id = f"m4_3_1p-{split_name}-{pair_idx:04d}"

            attempts = 0
            while attempts < 3000:
                attempts += 1
                dom = domains[(pair_idx + fam_idx + attempts // 25) % len(domains)]
                d_name = dom["domain"]
                ctx_text, cond_a, cond_b, sem_state = sample_context_for_stratum(dom, stratum_type, s_idx, rng)

                if sem_state in semantic_states:
                    continue
                if external_sem_states and sem_state in external_sem_states:
                    continue

                # Prepare choices with randomized order
                shuffled_choices = list(dom["choices"])
                rng.shuffle(shuffled_choices)

                # Case 1 & Case 2 priority directions: 50/50 balanced
                # Alternating direction assignment ensures strict balance
                if pair_idx % 2 == 0:
                    c1_order, c2_order = "A_over_B", "B_over_A"
                else:
                    c1_order, c2_order = "B_over_A", "A_over_B"

                # Targets
                action_a = dom["action_a"]
                action_b = dom["action_b"]
                action_fb = dom["action_fallback"]

                if cond_a and cond_b:
                    t1 = action_a if c1_order == "A_over_B" else action_b
                    t2 = action_a if c2_order == "A_over_B" else action_b
                elif cond_a and not cond_b:
                    t1, t2 = action_a, action_a
                elif not cond_a and cond_b:
                    t1, t2 = action_b, action_b
                else:
                    t1, t2 = action_fb, action_fb

                q1 = format_question_by_family(
                    family=family,
                    priority_order=c1_order,
                    rule_a_name=dom["rule_a_name"],
                    rule_a_desc=dom["rule_a_desc"],
                    rule_b_name=dom["rule_b_name"],
                    rule_b_desc=dom["rule_b_desc"],
                    fallback_text=dom["fallback_text"],
                )
                q2 = format_question_by_family(
                    family=family,
                    priority_order=c2_order,
                    rule_a_name=dom["rule_a_name"],
                    rule_a_desc=dom["rule_a_desc"],
                    rule_b_name=dom["rule_b_name"],
                    rule_b_desc=dom["rule_b_desc"],
                    fallback_text=dom["fallback_text"],
                )

                rec1 = {
                    "id": f"{group_id}-c1",
                    "group_id": group_id,
                    "task_family": "phrasing_diversification_fix",
                    "split": split_name,
                    "phrasing_family": family,
                    "template_family": d_name,
                    "domain_class": dom["domain_class"],
                    "stratum": stratum_type,
                    "conflict": (stratum_type == "conflict"),
                    "priority_order": c1_order,
                    "context": ctx_text,
                    "question": q1,
                    "choices": shuffled_choices,
                    "target": {"choice_id": t1},
                }
                rec2 = {
                    "id": f"{group_id}-c2",
                    "group_id": group_id,
                    "task_family": "phrasing_diversification_fix",
                    "split": split_name,
                    "phrasing_family": family,
                    "template_family": d_name,
                    "domain_class": dom["domain_class"],
                    "stratum": stratum_type,
                    "conflict": (stratum_type == "conflict"),
                    "priority_order": c2_order,
                    "context": ctx_text,
                    "question": q2,
                    "choices": shuffled_choices,
                    "target": {"choice_id": t2},
                }

                fp1 = compute_fingerprint(rec1)
                fp2 = compute_fingerprint(rec2)
                if fp1 in global_fps or fp2 in global_fps or fp1 == fp2:
                    continue

                # RUN INDEPENDENT SEMANTIC VALIDATOR ON BOTH RECORDS
                v1 = derive_semantics(rec1)
                v2 = derive_semantics(rec2)
                if not v1["is_match"] or not v2["is_match"]:
                    raise RuntimeError(f"Validator mismatch on newly generated pair {group_id}: v1={v1}, v2={v2}")

                global_fps.add(fp1)
                global_fps.add(fp2)
                semantic_states.add(sem_state)
                records.extend([rec1, rec2])
                pair_idx += 1
                break
            else:
                raise RuntimeError(f"Could not fulfill quota for {split_name}, family={family}, stratum={stratum_type}")

    return records, semantic_states


def main():
    print("Building M4.3.1 Repaired Phrasing Datasets...")
    out_dir = ROOT / "data/m4_3_1_phrasing_fix"
    out_dir.mkdir(parents=True, exist_ok=True)
    diag_dir = out_dir / "diagnostic_fix"
    diag_dir.mkdir(parents=True, exist_ok=True)

    # Load existing fingerprints
    global_fps = set()
    for p in PAST_DATASETS:
        if p.is_file():
            with open(p, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        r = json.loads(line)
                        global_fps.add(compute_fingerprint(r))
    print(f"Loaded {len(global_fps)} unique fingerprints from past datasets.")

    # 1. Generate phrasing_train (120 pairs / 240 cases: Families E~J)
    train_records, train_sem_states = generate_split_dataset(
        split_name="train",
        families=["family_E", "family_F", "family_G", "family_H", "family_I", "family_J"],
        total_pairs=120,
        diff_pairs_quota=60,
        single_pairs_quota=36,
        fallback_pairs_quota=24,
        seed=2026091921,
        global_fps=global_fps,
    )
    with open(out_dir / "phrasing_train.jsonl", "w", encoding="utf-8") as f:
        for r in train_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # 2. Generate phrasing_dev (40 pairs / 80 cases: Families K~L)
    dev_records, dev_sem_states = generate_split_dataset(
        split_name="dev",
        families=["family_K", "family_L"],
        total_pairs=40,
        diff_pairs_quota=20,
        single_pairs_quota=12,
        fallback_pairs_quota=8,
        seed=2026091922,
        global_fps=global_fps,
    )
    with open(out_dir / "phrasing_dev.jsonl", "w", encoding="utf-8") as f:
        for r in dev_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # 3. Generate fresh_phrasing_eval (60 pairs / 120 cases: Families M~P)
    # Strictly separated semantic states from train
    eval_records, eval_sem_states = generate_split_dataset(
        split_name="fresh_eval",
        families=["family_M", "family_N", "family_O", "family_P"],
        total_pairs=60,
        diff_pairs_quota=30,
        single_pairs_quota=18,
        fallback_pairs_quota=12,
        seed=2026091923,
        global_fps=global_fps,
        external_sem_states=train_sem_states,
    )
    with open(out_dir / "fresh_phrasing_eval.jsonl", "w", encoding="utf-8") as f:
        for r in eval_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # 4. Generate combined train and dev
    m3_train = [json.loads(line) for line in open(ROOT / "data/m3_3_v2/train.jsonl", encoding="utf-8") if line.strip()]
    m3_dev = [json.loads(line) for line in open(ROOT / "data/m3_3_v2/dev.jsonl", encoding="utf-8") if line.strip()]
    m4_1_train = [json.loads(line) for line in open(ROOT / "data/m4_1_exception/train_exception.jsonl", encoding="utf-8") if line.strip()]
    m4_1_dev = [json.loads(line) for line in open(ROOT / "data/m4_1_exception/dev_exception.jsonl", encoding="utf-8") if line.strip()]

    combined_train = m3_train + m4_1_train + train_records
    combined_dev = m3_dev + m4_1_dev + dev_records

    with open(out_dir / "combined_train.jsonl", "w", encoding="utf-8") as f:
        for r in combined_train:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(out_dir / "combined_dev.jsonl", "w", encoding="utf-8") as f:
        for r in combined_dev:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # 5. Generate Repaired Cell A and Cell B (Old Domain + Old/New Phrasing)
    # Include customer_service as 5th domain matching M4.1/M4.2.1
    old_domains_with_cs = list(DOMAINS[:4]) + [
        {
            "domain": "customer_service",
            "domain_class": "old",
            "choices": [
                {"id": "standard_guide", "text": "規約通りの通常案内"},
                {"id": "special_refund", "text": "特例全額返金"},
                {"id": "escalate", "text": "上長へエスカレーション"},
            ],
            "rule_a_name": "期限基準",
            "rule_a_desc": "購入から30日経過後は原則として「規約通りの通常案内」",
            "rule_b_name": "VIP例外",
            "rule_b_desc": "最上位VIP・特別顧客からの依頼は顧客維持のため「特例全額返金」",
            "fallback_text": "上長へエスカレーション",
            "action_a": "standard_guide",
            "action_b": "special_refund",
            "action_fallback": "escalate",
            "rule_a_true_range": (35, 60),
            "rule_a_false_range": (5, 25),
            "contexts_conflict": [
                ("商品購入から{v1}日経過した返品依頼です。お客様属性：最上位VIP会員様。", True, True),
                ("窓口受付：利用開始から{v1}日経過。顧客ランクはプレミアVIPランク該当者。", True, True),
                ("問い合わせ：購入後{v1}日経過後の解約申請。年間利用額上位0.1%の特別顧客様。", True, True),
            ],
            "contexts_single_a": [
                ("商品購入から{v1}日経過した返品依頼です。顧客属性：一般会員様。", True, False),
                ("窓口受付：利用開始から{v1}日経過。顧客ランクは通常メンバー該当者。", True, False),
            ],
            "contexts_single_b": [
                ("商品購入から{v1}日経過（30日以内）。お客様属性：最上位VIP会員様。", False, True),
                ("窓口受付：利用開始から{v1}日（30日以内）。顧客ランクはプレミアVIPランク該当者。", False, True),
            ],
            "contexts_fallback": [
                ("商品購入から{v1}日経過（30日以内）。顧客属性：一般会員様。", False, False),
                ("窓口受付：利用開始から{v1}日（30日以内）。顧客ランクは通常メンバー該当者。", False, False),
            ],
        }
    ]

    cell_a_records, _ = generate_split_dataset(
        split_name="cell_a_fix",
        families=["family_A"],
        total_pairs=20,
        diff_pairs_quota=12,
        single_pairs_quota=5,
        fallback_pairs_quota=3,
        seed=2026091924,
        global_fps=global_fps,
        allowed_domains=old_domains_with_cs,
    )
    cell_b_records, _ = generate_split_dataset(
        split_name="cell_b_fix",
        families=["family_A", "family_B", "family_C", "family_D"],
        total_pairs=20,
        diff_pairs_quota=12,
        single_pairs_quota=5,
        fallback_pairs_quota=3,
        seed=2026091925,
        global_fps=global_fps,
        allowed_domains=old_domains_with_cs,
    )
    with open(diag_dir / "cell_a_old_domain_old_phrasing.jsonl", "w", encoding="utf-8") as f:
        for r in cell_a_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(diag_dir / "cell_b_old_domain_new_phrasing.jsonl", "w", encoding="utf-8") as f:
        for r in cell_b_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # 6. Run 100% semantic audit on all new files
    audit_report = {
        "title": "M4.3.1 Semantic Validation Audit",
        "phrasing_train": validate_dataset(train_records),
        "phrasing_dev": validate_dataset(dev_records),
        "fresh_phrasing_eval": validate_dataset(eval_records),
        "cell_a_fix": validate_dataset(cell_a_records),
        "cell_b_fix": validate_dataset(cell_b_records),
    }
    with open(out_dir / "semantic_audit.json", "w", encoding="utf-8") as f:
        json.dump(audit_report, f, indent=2, ensure_ascii=False)

    # 7. Build Manifest
    manifest = {
        "title": "M4.3.1 Phrasing Repaired Data Manifest",
        "splits": {
            "phrasing_train": {
                "total_cases": len(train_records),
                "total_pairs": len(train_records) // 2,
                "families": dict(Counter(r["phrasing_family"] for r in train_records)),
                "domains": dict(Counter(r["template_family"] for r in train_records)),
                "domain_classes": dict(Counter(r["domain_class"] for r in train_records)),
                "strata": dict(Counter(r["stratum"] for r in train_records)),
                "priorities": dict(Counter(r["priority_order"] for r in train_records)),
            },
            "phrasing_dev": {
                "total_cases": len(dev_records),
                "total_pairs": len(dev_records) // 2,
                "families": dict(Counter(r["phrasing_family"] for r in dev_records)),
                "domains": dict(Counter(r["template_family"] for r in dev_records)),
                "domain_classes": dict(Counter(r["domain_class"] for r in dev_records)),
                "strata": dict(Counter(r["stratum"] for r in dev_records)),
                "priorities": dict(Counter(r["priority_order"] for r in dev_records)),
            },
            "fresh_phrasing_eval": {
                "total_cases": len(eval_records),
                "total_pairs": len(eval_records) // 2,
                "families": dict(Counter(r["phrasing_family"] for r in eval_records)),
                "domains": dict(Counter(r["template_family"] for r in eval_records)),
                "domain_classes": dict(Counter(r["domain_class"] for r in eval_records)),
                "strata": dict(Counter(r["stratum"] for r in eval_records)),
                "priorities": dict(Counter(r["priority_order"] for r in eval_records)),
            },
            "cell_a_fix": {
                "total_cases": len(cell_a_records),
                "total_pairs": len(cell_a_records) // 2,
                "strata": dict(Counter(r["stratum"] for r in cell_a_records)),
            },
            "cell_b_fix": {
                "total_cases": len(cell_b_records),
                "total_pairs": len(cell_b_records) // 2,
                "strata": dict(Counter(r["stratum"] for r in cell_b_records)),
            },
        },
    }
    with open(out_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("\nM4.3.1 Data generation complete!")
    print(f"phrasing_train: {len(train_records)} records, audit valid={audit_report['phrasing_train']['is_all_valid']}")
    print(f"phrasing_dev: {len(dev_records)} records, audit valid={audit_report['phrasing_dev']['is_all_valid']}")
    print(f"fresh_phrasing_eval: {len(eval_records)} records, audit valid={audit_report['fresh_phrasing_eval']['is_all_valid']}")
    print(f"cell_a_fix: {len(cell_a_records)} records, audit valid={audit_report['cell_a_fix']['is_all_valid']}")
    print(f"cell_b_fix: {len(cell_b_records)} records, audit valid={audit_report['cell_b_fix']['is_all_valid']}")


if __name__ == "__main__":
    main()
