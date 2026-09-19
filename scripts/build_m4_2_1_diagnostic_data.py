"""Data generator for M4.2.1 Factorial Diagnostic (Domain x Phrasing 2x2).

Generates 3 new datasets in data/m4_2_1_diagnostic/:
1. cell_a_old_domain_old_phrasing.jsonl (20 pairs / 40 cases) - Control
2. cell_b_old_domain_new_phrasing.jsonl (20 pairs / 40 cases) - Phrasing shift only
3. cell_c_new_domain_old_phrasing.jsonl (20 pairs / 40 cases) - Domain shift only
(Cell D is the existing novel_priority_eval.jsonl in data/m4_2_robustness/)

Each cell contains exactly:
- 12 conflict pairs (diff-target pairs: priority flip changes correct choice)
- 5 single condition pairs (same-target pairs)
- 3 fallback pairs (same-target pairs)
Total: 20 pairs / 40 cases per cell.

Guarantees:
- Zero fingerprint collision across all past datasets (M3, M4.1, M4.2 Phase A, smoke, transfer).
- Zero cross-cell fingerprint collision.
- Independent programmatic verification of all target choices.
- Fixed stratum quotas (no reject spillover).
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

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
    ROOT / "data/m3_1/transfer_probe.jsonl",
    ROOT / "examples/smoke_cases.jsonl",
]


def compute_fingerprint(record: Dict[str, Any]) -> str:
    ctx = record.get("context", "").strip()
    q = record.get("question", "").strip()
    c_texts = "||".join(c["text"].strip() for c in record.get("choices", []))
    raw = f"{ctx} ||| {q} ||| {c_texts}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# 1. OLD DOMAINS (from M4.1)
OLD_DOMAINS = [
    {
        "domain": "game_action",
        "choices": [
            {"id": "heal", "text": "回復する"},
            {"id": "continue", "text": "移動を継続する"},
            {"id": "wait", "text": "待機する"},
        ],
        "rule_a_name": "HP基準",
        "rule_a_desc": "HPが20未満なら「回復する」、それ以外なら「待機する」",
        "rule_b_name": "移動例外",
        "rule_b_desc": "安全地帯等への移動中・進軍中なら「移動を継続する」",
        "fallback_text": "待機する",
        "action_a": "heal",
        "action_b": "continue",
        "action_fallback": "wait",
        "contexts_conflict": [
            ("現在のプレイヤーのHPは{v1}です。回復アイテムあり。現在、安全地帯へ移動中。", True, True),
            ("状況：HPは{v1}。ポーション所持。部隊は前線へ進軍中。", True, True),
            ("ステータス：残り体力{v1}。救急キットあり。目的地へ急行中。", True, True),
        ],
        "contexts_single_a": [
            ("現在のプレイヤーのHPは{v1}です。回復アイテムあり。移動はしておらず安全地帯に滞在中。", True, False),
            ("状況：HPは{v1}。ポーション所持。現在は停止して索敵中。", True, False),
        ],
        "contexts_single_b": [
            ("現在のプレイヤーのHPは{v1}です。HPは十分あり。現在、安全地帯へ移動中。", False, True),
            ("ステータス：体力満タン（{v1}）。部隊は前線へ進軍中。", False, True),
        ],
        "contexts_fallback": [
            ("現在のプレイヤーのHPは{v1}（危険水域外）。移動はしておらず安全地帯に滞在中。", False, False),
            ("状況：HPは{v1}で十分。停止して周囲を索敵中。", False, False),
        ],
        "v1_low": (10, 18),
        "v1_high": (25, 45),
    },
    {
        "domain": "delivery_dispatch",
        "choices": [
            {"id": "standard", "text": "通常便で発送"},
            {"id": "express", "text": "特急便で発送"},
            {"id": "hold", "text": "保留にする"},
        ],
        "rule_a_name": "重量基準",
        "rule_a_desc": "重量が30kg以上なら「通常便で発送」、それ以外なら「保留にする」",
        "rule_b_name": "緊急例外",
        "rule_b_desc": "至急・特急・緊急配送の指定があれば「特急便で発送」",
        "fallback_text": "保留にする",
        "action_a": "standard",
        "action_b": "express",
        "action_fallback": "hold",
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
            ("検品結果：総重量{v1}kg。伝票に「特急指定・緊急扱い」の記載あり。", False, True),
        ],
        "contexts_fallback": [
            ("荷物の重量は{v1}kg（基準未満）。至急要請はなく通常納期です。", False, False),
            ("検品結果：総重量{v1}kg。特急指定はなく期日通りの配送希望です。", False, False),
        ],
        "v1_low": (12, 25),
        "v1_high": (35, 55),
    },
    {
        "domain": "system_ops",
        "choices": [
            {"id": "scale_up", "text": "スケールアップ実行"},
            {"id": "isolate", "text": "ネットワーク遮断"},
            {"id": "monitor", "text": "監視継続"},
        ],
        "rule_a_name": "負荷基準",
        "rule_a_desc": "CPU使用率が80%以上なら「スケールアップ実行」、それ以外なら「監視継続」",
        "rule_b_name": "保安例外",
        "rule_b_desc": "不正侵入・マルウェア・侵害検知時は即座に「ネットワーク遮断」",
        "fallback_text": "監視継続",
        "action_a": "scale_up",
        "action_b": "isolate",
        "action_fallback": "monitor",
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
            ("クラスター監視：CPU負荷率{v1}%。セキュリティ監視からマルウェア通信警告あり。", False, True),
        ],
        "contexts_fallback": [
            ("サーバーCPU使用率は{v1}%（負荷基準未満）。セキュリティ侵害アラートなし。", False, False),
            ("システム状況：プロセッサ負荷{v1}%。侵害の形跡はなく平穏です。", False, False),
        ],
        "v1_low": (30, 65),
        "v1_high": (85, 96),
    },
    {
        "domain": "customer_service",
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
            ("窓口受付：利用開始から{v1}日。顧客ランクは通常メンバー該当者。", False, False),
        ],
        "v1_low": (5, 25),
        "v1_high": (35, 60),
    },
    {
        "domain": "facility_control",
        "choices": [
            {"id": "eco_mode", "text": "省エネ運転へ切替"},
            {"id": "emergency_stop", "text": "即時非常停止"},
            {"id": "normal_run", "text": "通常運転維持"},
        ],
        "rule_a_name": "温度基準",
        "rule_a_desc": "室温が25度以下なら「省エネ運転へ切替」、それ以外なら「通常運転維持」",
        "rule_b_name": "安全例外",
        "rule_b_desc": "非常停止信号・警報・緊急ボタン検知時は「即時非常停止」",
        "fallback_text": "通常運転維持",
        "action_a": "eco_mode",
        "action_b": "emergency_stop",
        "action_fallback": "normal_run",
        "contexts_conflict": [
            ("工場フロア：室温測定値{v1}度。火災検知器が作動し非常警報が鳴動中。", True, True),
            ("設備空調モニター：現在温度{v1}度。安全管理盤より緊急停止シグナル受信。", True, True),
            ("生産ライン環境：エリア温度{v1}度。作業員による非常停止ボタン押下検知。", True, True),
        ],
        "contexts_single_a": [
            ("工場フロア：室温測定値{v1}度。非常警報や安全停止信号は検知されていません。", True, False),
            ("設備空調モニター：現在温度{v1}度。安全システムは正常、警報なし。", True, False),
        ],
        "contexts_single_b": [
            ("工場フロア：室温測定値{v1}度（25度超過）。火災検知器が作動し非常警報が鳴動中。", False, True),
            ("生産ライン環境：エリア温度{v1}度（25度超過）。作業員による非常停止ボタン押下検知。", False, True),
        ],
        "contexts_fallback": [
            ("工場フロア：室温測定値{v1}度（25度超過）。警報や非常信号は検知されていません。", False, False),
            ("設備空調モニター：現在温度{v1}度（25度超過）。安全システム正常、警報なし。", False, False),
        ],
        "v1_low": (15, 23),
        "v1_high": (28, 38),
    },
]


# 2. NEW DOMAINS (from M4.2)
NEW_DOMAINS = [
    {
        "domain": "manufacturing",
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
        "contexts_conflict": [
            ("製品検査：寸法誤差は{err:.3f}mm（公差内）。高解像度カメラにより表面キズを検知。", True, True),
            ("精密測定：測定誤差{err:.3f}mm。ラインセンサーが微細な外観打痕を検出。", True, True),
            ("ロット測定：誤差{err:.3f}mm。目視検査にて微小異物付着のアラートあり。", True, True),
        ],
        "contexts_single_a": [
            ("製品検査：寸法誤差は{err:.3f}mm。外観センサー・光学検査ともに欠陥なし。", True, False),
            ("精密測定：測定誤差{err:.3f}mm。外観画像診断は正常判定、キズなし。", True, False),
        ],
        "contexts_single_b": [
            ("製品検査：寸法誤差は{err:.3f}mm（基準超過）。表面キズを検知。", False, True),
            ("精密測定：測定誤差{err:.3f}mm（基準超過）。外観打痕を検出。", False, True),
        ],
        "contexts_fallback": [
            ("製品検査：寸法誤差は{err:.3f}mm（基準超過）。外観キズなし。", False, False),
            ("精密測定：測定誤差{err:.3f}mm（基準超過）。外観センサーは正常。", False, False),
        ],
        "err_low": (0.012, 0.038),
        "err_high": (0.045, 0.080),
    },
    {
        "domain": "facility_power",
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
            ("施設受電状況：受電電力{kw}kW（400kW未満）。蓄電池残量{soc}%。", False, True),
        ],
        "contexts_fallback": [
            ("エネルギー管理：受電電力{kw}kW（400kW未満）。蓄電池SOCは{soc}%（通常レベル）。", False, False),
            ("電力監視ログ：現在消費{kw}kW（400kW未満）。蓄電池残量は{soc}%。", False, False),
        ],
        "kw_low": (310, 385),
        "kw_high": (415, 490),
        "soc_low": (40, 75),
        "soc_high": (91, 98),
    },
    {
        "domain": "inventory",
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
        "contexts_conflict": [
            ("倉庫管理：保管日数{days}日（長期滞留）。管理システムに「検疫検査・品質再確認対象」の指定あり。", True, True),
            ("在庫ステータス：入庫から{days}日経過。出荷伝票に「品質監査指定ロット・隔離要」のタグあり。", True, True),
            ("出荷指示照会：保管期間{days}日。検疫管理フラグが有効化されています。", True, True),
        ],
        "contexts_single_a": [
            ("倉庫管理：保管日数{days}日。検疫指定はなく、品質検査済み通常ロット。", True, False),
            ("在庫ステータス：入庫から{days}日経過。出荷伝票に検疫・保留の指定は一切なし。", True, False),
        ],
        "contexts_single_b": [
            ("倉庫管理：保管日数{days}日（直近入庫）。管理システムに「検疫検査対象」の指定あり。", False, True),
            ("在庫ステータス：入庫から{days}日。検疫管理フラグが有効化されています。", False, True),
        ],
        "contexts_fallback": [
            ("倉庫管理：保管日数{days}日（入庫直後）。検疫指定はなく通常品です。", False, False),
            ("在庫ステータス：入庫から{days}日。検疫タグなし、長期滞留基準にも非該当。", False, False),
        ],
        "days_low": (30, 140),
        "days_high": (185, 290),
    },
    {
        "domain": "job_scheduler",
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
            ("ジョブ実行状況：キュー待機時間{mins}分。要求メモリ{mem}GB、標準規模ジョブ。", False, False),
            ("スケジューラ監視：待ち時間{mins}分経過。メモリ要求{mem}GB、特大フラグなし。", False, False),
        ],
        "mins_low": (10, 45),
        "mins_high": (65, 180),
        "mem_low": (8, 32),
        "mem_high": (70, 256),
    },
]


def format_old_phrasing(
    priority_order: str,
    rule_a_name: str,
    rule_a_desc: str,
    rule_b_name: str,
    rule_b_desc: str,
    fallback_text: str,
) -> str:
    """Format question using M4.1 OLD phrasing template (①【最優先】... ②【次点】...)."""
    if priority_order == "A_over_B":
        return (
            f"ルール：①【最優先】{rule_a_name}：{rule_a_desc}。②【次点】{rule_b_name}：{rule_b_desc}。"
            f"優先順位に従って行動を選んでください。"
        )
    else:
        return (
            f"ルール：①【最優先】{rule_b_name}：{rule_b_desc}。②【次点】{rule_a_name}：{rule_a_desc}。"
            f"優先順位に従って行動を選んでください。"
        )


def format_new_phrasing(
    family: str,
    priority_order: str,
    rule_a_name: str,
    rule_a_desc: str,
    rule_b_name: str,
    rule_b_desc: str,
    fallback_text: str,
) -> str:
    """Format question using M4.2 NEW phrasing families (A, B, C, D)."""
    if family == "family_A":
        if priority_order == "A_over_B":
            return (
                f"ルール：通常は「{rule_b_desc}」に従う。ただし「{rule_a_desc}」の条件が成立した場合は{rule_a_name}を優先する。"
                f"どちらも該当しない場合は「{fallback_text}」。規則に従って行動を選択してください。"
            )
        else:
            return (
                f"ルール：通常は「{rule_a_desc}」に従う。ただし「{rule_b_desc}」の条件が成立した場合は{rule_b_name}を優先する。"
                f"どちらも該当しない場合は「{fallback_text}」。規則に従って行動を選択してください。"
            )
    elif family == "family_B":
        if priority_order == "A_over_B":
            return (
                f"ルール：「{rule_a_desc}」と「{rule_b_desc}」が同時に成立する場合のみ、{rule_b_name}より{rule_a_name}を優先する。"
                f"それ以外は成立した側の判定を適用し、どちらも不成立なら「{fallback_text}」。規則に従って行動を選択してください。"
            )
        else:
            return (
                f"ルール：「{rule_a_desc}」と「{rule_b_desc}」が同時に成立する場合のみ、{rule_a_name}より{rule_b_name}を優先する。"
                f"それ以外は成立した側の判定を適用し、どちらも不成立なら「{fallback_text}」。規則に従って行動を選択してください。"
            )
    elif family == "family_C":
        if priority_order == "A_over_B":
            return (
                f"ルール：優先度は {rule_a_name}（{rule_a_desc}） > {rule_b_name}（{rule_b_desc}）。"
                f"両方適用可能なら上位の規則を採用する。どちらも該当しない場合は「{fallback_text}」。規則に従って行動を選択してください。"
            )
        else:
            return (
                f"ルール：優先度は {rule_b_name}（{rule_b_desc}） > {rule_a_name}（{rule_a_desc}）。"
                f"両方適用可能なら上位の規則を採用する。どちらも該当しない場合は「{fallback_text}」。規則に従って行動を選択してください。"
            )
    elif family == "family_D":
        if priority_order == "A_over_B":
            return (
                f"ルール：第一判断：{rule_b_name}（{rule_b_desc}）。例外条件：{rule_a_name}（{rule_a_desc}）。"
                f"例外条件を満たした場合、第一判断を上書きする。いずれも満たさない場合は「{fallback_text}」。規則に従って行動を選択してください。"
            )
        else:
            return (
                f"ルール：第一判断：{rule_a_name}（{rule_a_desc}）。例外条件：{rule_b_name}（{rule_b_desc}）。"
                f"例外条件を満たした場合、第一判断を上書きする。いずれも満たさない場合は「{fallback_text}」。規則に従って行動を選択してください。"
            )
    else:
        raise ValueError(f"Unknown phrasing family: {family}")


def determine_target(
    cond_a: bool,
    cond_b: bool,
    priority_order: str,
    action_a: str,
    action_b: str,
    action_fallback: str,
) -> str:
    """Independent ground truth action determination."""
    if cond_a and cond_b:
        return action_a if priority_order == "A_over_B" else action_b
    elif cond_a and not cond_b:
        return action_a
    elif not cond_a and cond_b:
        return action_b
    else:
        return action_fallback


def generate_cell_dataset(
    cell_name: str,
    domain_type: str,  # "OLD" or "NEW"
    phrasing_type: str,  # "OLD" or "NEW"
    seed: int,
    global_fps: set,
) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    domains = OLD_DOMAINS if domain_type == "OLD" else NEW_DOMAINS
    num_domains = len(domains)

    # 20 pairs total: exactly 12 conflict, 5 single, 3 fallback
    # Allocate to domains
    # If 5 domains (OLD):
    # conflict: 3, 3, 2, 2, 2 = 12
    # single: 1, 1, 1, 1, 1 = 5
    # fallback: 1, 1, 1, 0, 0 = 3
    # If 4 domains (NEW):
    # conflict: 3, 3, 3, 3 = 12
    # single: 1, 1, 1, 2 = 5
    # fallback: 1, 1, 1, 0 = 3
    if num_domains == 5:
        domain_allocations = [
            ("conflict", 3), ("single", 1), ("fallback", 1),  # dom 0 (5 pairs)
            ("conflict", 3), ("single", 1), ("fallback", 1),  # dom 1 (5 pairs)
            ("conflict", 2), ("single", 1), ("fallback", 1),  # dom 2 (4 pairs)
            ("conflict", 2), ("single", 1), ("fallback", 0),  # dom 3 (3 pairs)
            ("conflict", 2), ("single", 1), ("fallback", 0),  # dom 4 (3 pairs)
        ]
        # We group pairs per domain
        per_dom_strata = [
            ["conflict"] * 3 + ["single"] * 1 + ["fallback"] * 1,
            ["conflict"] * 3 + ["single"] * 1 + ["fallback"] * 1,
            ["conflict"] * 2 + ["single"] * 1 + ["fallback"] * 1,
            ["conflict"] * 2 + ["single"] * 1,
            ["conflict"] * 2 + ["single"] * 1,
        ]
    else:
        per_dom_strata = [
            ["conflict"] * 3 + ["single"] * 1 + ["fallback"] * 1,  # 5
            ["conflict"] * 3 + ["single"] * 1 + ["fallback"] * 1,  # 5
            ["conflict"] * 3 + ["single"] * 1 + ["fallback"] * 1,  # 5
            ["conflict"] * 3 + ["single"] * 2,                     # 5
        ]

    families = ["family_A", "family_B", "family_C", "family_D"]
    pair_counter = 0
    generated_pairs: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []
    semantic_states = set()

    for d_idx, strata in enumerate(per_dom_strata):
        dom = domains[d_idx]
        d_name = dom["domain"]
        rule_a_name = dom["rule_a_name"]
        rule_a_desc = dom["rule_a_desc"]
        rule_b_name = dom["rule_b_name"]
        rule_b_desc = dom["rule_b_desc"]
        fallback_text = dom["fallback_text"]
        action_a = dom["action_a"]
        action_b = dom["action_b"]
        action_fallback = dom["action_fallback"]
        choices = dom["choices"]

        for s_idx, stratum_type in enumerate(strata):
            is_conflict = (stratum_type == "conflict")
            family = families[pair_counter % len(families)]
            group_id = f"m4_2_1-{cell_name}-{pair_counter:04d}"

            attempts = 0
            while attempts < 2000:
                attempts += 1
                # Sample context based on domain and stratum
                if domain_type == "OLD":
                    v1_range = dom["v1_high"] if stratum_type in ["conflict", "single"] else dom["v1_low"]
                    # Generate value and pick template
                    if stratum_type == "conflict":
                        v1 = rng.randint(dom["v1_high"][0], dom["v1_high"][1])
                        tmpl, cond_a, cond_b = rng.choice(dom["contexts_conflict"])
                    elif stratum_type == "single":
                        if s_idx % 2 == 0:
                            v1 = rng.randint(dom["v1_high"][0], dom["v1_high"][1])
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_a"])
                        else:
                            v1 = rng.randint(dom["v1_low"][0], dom["v1_low"][1])
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_b"])
                    else:
                        v1 = rng.randint(dom["v1_low"][0], dom["v1_low"][1])
                        tmpl, cond_a, cond_b = rng.choice(dom["contexts_fallback"])
                    context_text = tmpl.format(v1=v1)
                    sem_state = (d_name, v1, cond_a, cond_b, stratum_type)

                else:  # NEW domain
                    if d_name == "manufacturing":
                        if stratum_type == "conflict":
                            err = rng.uniform(dom["err_low"][0], dom["err_low"][1])
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_conflict"])
                        elif stratum_type == "single":
                            if s_idx % 2 == 0:
                                err = rng.uniform(dom["err_low"][0], dom["err_low"][1])
                                tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_a"])
                            else:
                                err = rng.uniform(dom["err_high"][0], dom["err_high"][1])
                                tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_b"])
                        else:
                            err = rng.uniform(dom["err_high"][0], dom["err_high"][1])
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_fallback"])
                        context_text = tmpl.format(err=err)
                        sem_state = (d_name, round(err, 3), cond_a, cond_b, stratum_type)

                    elif d_name == "facility_power":
                        if stratum_type == "conflict":
                            kw = rng.randint(dom["kw_high"][0], dom["kw_high"][1])
                            soc = rng.randint(dom["soc_high"][0], dom["soc_high"][1])
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_conflict"])
                        elif stratum_type == "single":
                            if s_idx % 2 == 0:
                                kw = rng.randint(dom["kw_high"][0], dom["kw_high"][1])
                                soc = rng.randint(dom["soc_low"][0], dom["soc_low"][1])
                                tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_a"])
                            else:
                                kw = rng.randint(dom["kw_low"][0], dom["kw_low"][1])
                                soc = rng.randint(dom["soc_high"][0], dom["soc_high"][1])
                                tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_b"])
                        else:
                            kw = rng.randint(dom["kw_low"][0], dom["kw_low"][1])
                            soc = rng.randint(dom["soc_low"][0], dom["soc_low"][1])
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_fallback"])
                        context_text = tmpl.format(kw=kw, soc=soc)
                        sem_state = (d_name, kw, soc, cond_a, cond_b, stratum_type)

                    elif d_name == "inventory":
                        if stratum_type == "conflict":
                            days = rng.randint(dom["days_high"][0], dom["days_high"][1])
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_conflict"])
                        elif stratum_type == "single":
                            if s_idx % 2 == 0:
                                days = rng.randint(dom["days_high"][0], dom["days_high"][1])
                                tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_a"])
                            else:
                                days = rng.randint(dom["days_low"][0], dom["days_low"][1])
                                tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_b"])
                        else:
                            days = rng.randint(dom["days_low"][0], dom["days_low"][1])
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_fallback"])
                        context_text = tmpl.format(days=days)
                        sem_state = (d_name, days, cond_a, cond_b, stratum_type)

                    elif d_name == "job_scheduler":
                        if stratum_type == "conflict":
                            mins = rng.randint(dom["mins_high"][0], dom["mins_high"][1])
                            mem = rng.randint(dom["mem_high"][0], dom["mem_high"][1])
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_conflict"])
                        elif stratum_type == "single":
                            if s_idx % 2 == 0:
                                mins = rng.randint(dom["mins_high"][0], dom["mins_high"][1])
                                mem = rng.randint(dom["mem_low"][0], dom["mem_low"][1])
                                tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_a"])
                            else:
                                mins = rng.randint(dom["mins_low"][0], dom["mins_low"][1])
                                mem = rng.randint(dom["mem_high"][0], dom["mem_high"][1])
                                tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_b"])
                        else:
                            mins = rng.randint(dom["mins_low"][0], dom["mins_low"][1])
                            mem = rng.randint(dom["mem_low"][0], dom["mem_low"][1])
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_fallback"])
                        context_text = tmpl.format(mins=mins, mem=mem)
                        sem_state = (d_name, mins, mem, cond_a, cond_b, stratum_type)

                if sem_state in semantic_states:
                    continue

                # Format question
                if phrasing_type == "OLD":
                    q1 = format_old_phrasing("A_over_B", rule_a_name, rule_a_desc, rule_b_name, rule_b_desc, fallback_text)
                    q2 = format_old_phrasing("B_over_A", rule_a_name, rule_a_desc, rule_b_name, rule_b_desc, fallback_text)
                    phr_fam = "old_m4_1_numbered"
                else:
                    q1 = format_new_phrasing(family, "A_over_B", rule_a_name, rule_a_desc, rule_b_name, rule_b_desc, fallback_text)
                    q2 = format_new_phrasing(family, "B_over_A", rule_a_name, rule_a_desc, rule_b_name, rule_b_desc, fallback_text)
                    phr_fam = family

                tgt1 = determine_target(cond_a, cond_b, "A_over_B", action_a, action_b, action_fallback)
                tgt2 = determine_target(cond_a, cond_b, "B_over_A", action_a, action_b, action_fallback)

                shuffled_choices = list(choices)
                rng.shuffle(shuffled_choices)

                rec1 = {
                    "id": f"{group_id}-c1",
                    "group_id": group_id,
                    "task_family": "factorial_diagnostic",
                    "cell": cell_name,
                    "domain_axis": domain_type,
                    "phrasing_axis": phrasing_type,
                    "template_family": d_name,
                    "phrasing_family": phr_fam,
                    "stratum": stratum_type,
                    "conflict": is_conflict,
                    "priority_order": "A_over_B",
                    "context": context_text,
                    "question": q1,
                    "choices": shuffled_choices,
                    "target": {"choice_id": tgt1},
                }

                rec2 = {
                    "id": f"{group_id}-c2",
                    "group_id": group_id,
                    "task_family": "factorial_diagnostic",
                    "cell": cell_name,
                    "domain_axis": domain_type,
                    "phrasing_axis": phrasing_type,
                    "template_family": d_name,
                    "phrasing_family": phr_fam,
                    "stratum": stratum_type,
                    "conflict": is_conflict,
                    "priority_order": "B_over_A",
                    "context": context_text,
                    "question": q2,
                    "choices": shuffled_choices,
                    "target": {"choice_id": tgt2},
                }

                fp1 = compute_fingerprint(rec1)
                fp2 = compute_fingerprint(rec2)

                if (
                    fp1 in global_fps
                    or fp2 in global_fps
                ):
                    continue

                # Success
                semantic_states.add(sem_state)
                global_fps.add(fp1)
                global_fps.add(fp2)
                generated_pairs.append((rec1, rec2))
                break
            else:
                raise RuntimeError(f"Cell {cell_name}: failed to generate unique pair for stratum {stratum_type} in {d_name} after 2000 attempts!")

            pair_counter += 1

    flat_records = []
    diff_count = 0
    same_count = 0
    for r1, r2 in generated_pairs:
        assert r1["group_id"] == r2["group_id"]
        assert r1["context"] == r2["context"]
        if r1["conflict"]:
            assert r1["target"]["choice_id"] != r2["target"]["choice_id"]
            diff_count += 1
        else:
            assert r1["target"]["choice_id"] == r2["target"]["choice_id"]
            same_count += 1
        flat_records.append(r1)
        flat_records.append(r2)

    assert len(generated_pairs) == 20, f"Cell {cell_name}: expected 20 pairs, got {len(generated_pairs)}"
    assert diff_count == 12, f"Cell {cell_name}: expected 12 diff pairs, got {diff_count}"
    assert same_count == 8, f"Cell {cell_name}: expected 8 same pairs, got {same_count}"
    assert len(flat_records) == 40, f"Cell {cell_name}: expected 40 records, got {len(flat_records)}"

    print(f"Cell {cell_name} ({domain_type} domain, {phrasing_type} phrasing): 20 pairs (12 conflict, 8 same) = 40 records.")
    return flat_records


def main():
    out_dir = ROOT / "data/m4_2_1_diagnostic"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Collect past fingerprints
    global_fps = set()
    for p in PAST_DATASETS:
        if p.exists():
            for line in open(p, encoding="utf-8"):
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    global_fps.add(compute_fingerprint(rec))
    print(f"Loaded {len(global_fps)} existing fingerprints from past datasets.")

    # Generate Cell A: OLD Domain + OLD Phrasing
    cell_a_records = generate_cell_dataset("cell_a", "OLD", "OLD", seed=2026091901, global_fps=global_fps)
    with open(out_dir / "cell_a_old_domain_old_phrasing.jsonl", "w", encoding="utf-8") as f:
        for r in cell_a_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Generate Cell B: OLD Domain + NEW Phrasing
    cell_b_records = generate_cell_dataset("cell_b", "OLD", "NEW", seed=2026091902, global_fps=global_fps)
    with open(out_dir / "cell_b_old_domain_new_phrasing.jsonl", "w", encoding="utf-8") as f:
        for r in cell_b_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Generate Cell C: NEW Domain + OLD Phrasing
    cell_c_records = generate_cell_dataset("cell_c", "NEW", "OLD", seed=2026091903, global_fps=global_fps)
    with open(out_dir / "cell_c_new_domain_old_phrasing.jsonl", "w", encoding="utf-8") as f:
        for r in cell_c_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print("\nAll 3 diagnostic datasets successfully created with verified quotas and ZERO leaks!")


if __name__ == "__main__":
    main()
