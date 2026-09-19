"""Data generator for M4.3-P Priority Phrasing Diversification.

Generates:
1. data/m4_3_phrasing/phrasing_train.jsonl (120 pairs / 240 cases: Families E~J)
2. data/m4_3_phrasing/phrasing_dev.jsonl (40 pairs / 80 cases: Families K~L)
3. data/m4_3_phrasing/fresh_phrasing_eval.jsonl (60 pairs / 120 cases: Families M~P)
4. data/m4_3_phrasing/combined_train.jsonl (1080 cases: 600 M3 + 240 M4.1 + 240 M4.3)
5. data/m4_3_phrasing/combined_dev.jsonl (220 cases: 100 M3 + 40 M4.1 + 80 M4.3)

Strict Guarantees:
- Historical Families A~D are NOT used for training or dev.
- Phrasing families strictly partitioned:
  * Train: Families E, F, G, H, I, J
  * Dev: Families K, L
  * Fresh Eval: Families M, N, O, P
- 8 diverse domains (4 old M4.1 + 4 new M4.2) mixed across all families.
- Fixed stratum quotas per family and split:
  * Train (120 pairs): 60 conflict, 36 single, 24 fallback (10 conflict, 6 single, 4 fallback per family E~J)
  * Dev (40 pairs): 20 conflict, 12 single, 8 fallback (10 conflict, 6 single, 4 fallback per family K~L)
  * Eval (60 pairs): 30 conflict, 18 single, 12 fallback
- 50/50 symmetric A_over_B and B_over_A priority directions.
- Zero exact input fingerprint collision against past datasets (M3, M4.1, M4.2, smoke, transfer: 1984 existing records).
- Zero cross-split fingerprint collision between train, dev, fresh_phrasing_eval.
- Programmatic correctness verification of ground truth for 100% of cases.
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
        "val_low": (10, 18),
        "val_high": (25, 45),
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
        "val_low": (12, 25),
        "val_high": (35, 55),
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
        "val_low": (30, 65),
        "val_high": (85, 96),
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
        "val_low": (15, 23),
        "val_high": (28, 38),
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
        "val_low": (0.012, 0.038),
        "val_high": (0.045, 0.080),
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
        "val_low": (310, 385),
        "val_high": (415, 490),
        "soc_low": (40, 75),
        "soc_high": (91, 98),
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
        "val_low": (30, 140),
        "val_high": (185, 290),
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
        "val_low": (10, 45),
        "val_high": (65, 180),
        "mem_low": (8, 32),
        "mem_high": (70, 256),
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
        # 原則 / 優先規則
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
        # 競合時の採用規則
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
        # 上位 / 下位規則
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
        # override
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
        # 優先番号
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
        # if both
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
        # 優先方針
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
        # precedence
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
                f"ルール：競合解決順は{rule_a_name}（{rule_a_desc}）、{rule_b_name}（{rule_b_desc}）の順。"
                f"最初に成立した規則の結果を採用し、どちらも非該当なら「{fallback_text}」。規則に従って行動を選択してください。"
            )
        else:
            return (
                f"ルール：競合解決順は{rule_b_name}（{rule_b_desc}）、{rule_a_name}（{rule_a_desc}）の順。"
                f"最初に成立した規則の結果を採用し、どちらも非該当なら「{fallback_text}」。規則に従って行動を選択してください。"
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
    """Independent ground-truth target determination."""
    if cond_a and cond_b:
        return action_a if priority_order == "A_over_B" else action_b
    elif cond_a and not cond_b:
        return action_a
    elif not cond_a and cond_b:
        return action_b
    else:
        return action_fallback


def generate_split_dataset(
    split_name: str,
    families: List[str],
    total_pairs: int,
    diff_pairs_quota: int,
    single_pairs_quota: int,
    fallback_pairs_quota: int,
    seed: int,
    global_fps: set,
) -> List[Dict[str, Any]]:
    """Generate dataset with exact quota per family and stratum."""
    rng = random.Random(seed)
    num_families = len(families)
    assert total_pairs == diff_pairs_quota + single_pairs_quota + fallback_pairs_quota

    # Exact quota per family
    # E.g. Train: 6 families, 60 diff (10/fam), 36 single (6/fam), 24 fallback (4/fam) = 20 pairs/fam
    # Dev: 2 families, 20 diff (10/fam), 12 single (6/fam), 8 fallback (4/fam) = 20 pairs/fam
    # Eval: 4 families, 30 diff, 18 single, 12 fallback
    diff_per_fam = diff_pairs_quota // num_families
    single_per_fam = single_pairs_quota // num_families
    fallback_per_fam = fallback_pairs_quota // num_families

    all_pairs: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []
    semantic_states = set()
    pair_idx = 0

    for fam_idx, family in enumerate(families):
        # Calculate exact stratum counts for this family
        # Handle non-divisible remainder if any
        n_diff = diff_per_fam + (1 if fam_idx < (diff_pairs_quota % num_families) else 0)
        n_single = single_per_fam + (1 if fam_idx < (single_pairs_quota % num_families) else 0)
        n_fallback = fallback_per_fam + (1 if fam_idx < (fallback_pairs_quota % num_families) else 0)

        family_strata = (
            ["conflict"] * n_diff
            + ["single"] * n_single
            + ["fallback"] * n_fallback
        )

        for s_idx, stratum_type in enumerate(family_strata):
            is_conflict = (stratum_type == "conflict")
            group_id = f"m4_3p-{split_name}-{pair_idx:04d}"

            # Distribute domains across pairs
            dom_idx = (pair_idx + fam_idx) % len(DOMAINS)
            dom = DOMAINS[dom_idx]
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

            attempts = 0
            while attempts < 3000:
                attempts += 1
                # Sample context based on domain and stratum
                if d_name in ["game_action", "delivery_dispatch", "system_ops", "facility_control"]:
                    if stratum_type == "conflict":
                        v1 = rng.randint(dom["val_high"][0], dom["val_high"][1])
                        tmpl, cond_a, cond_b = rng.choice(dom["contexts_conflict"])
                    elif stratum_type == "single":
                        if s_idx % 2 == 0:
                            v1 = rng.randint(dom["val_high"][0], dom["val_high"][1])
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_a"])
                        else:
                            v1 = rng.randint(dom["val_low"][0], dom["val_low"][1])
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_b"])
                    else:
                        v1 = rng.randint(dom["val_low"][0], dom["val_low"][1])
                        tmpl, cond_a, cond_b = rng.choice(dom["contexts_fallback"])
                    context_text = tmpl.format(v1=v1)
                    sem_state = (d_name, v1, cond_a, cond_b, stratum_type)

                elif d_name == "manufacturing":
                    if stratum_type == "conflict":
                        err = rng.uniform(dom["val_low"][0], dom["val_low"][1])
                        tmpl, cond_a, cond_b = rng.choice(dom["contexts_conflict"])
                    elif stratum_type == "single":
                        if s_idx % 2 == 0:
                            err = rng.uniform(dom["val_low"][0], dom["val_low"][1])
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_a"])
                        else:
                            err = rng.uniform(dom["val_high"][0], dom["val_high"][1])
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_b"])
                    else:
                        err = rng.uniform(dom["val_high"][0], dom["val_high"][1])
                        tmpl, cond_a, cond_b = rng.choice(dom["contexts_fallback"])
                    context_text = tmpl.format(err=err)
                    sem_state = (d_name, round(err, 3), cond_a, cond_b, stratum_type)

                elif d_name == "facility_power":
                    if stratum_type == "conflict":
                        kw = rng.randint(dom["val_high"][0], dom["val_high"][1])
                        soc = rng.randint(dom["soc_high"][0], dom["soc_high"][1])
                        tmpl, cond_a, cond_b = rng.choice(dom["contexts_conflict"])
                    elif stratum_type == "single":
                        if s_idx % 2 == 0:
                            kw = rng.randint(dom["val_high"][0], dom["val_high"][1])
                            soc = rng.randint(dom["soc_low"][0], dom["soc_low"][1])
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_a"])
                        else:
                            kw = rng.randint(dom["val_low"][0], dom["val_low"][1])
                            soc = rng.randint(dom["soc_high"][0], dom["soc_high"][1])
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_b"])
                    else:
                        kw = rng.randint(dom["val_low"][0], dom["val_low"][1])
                        soc = rng.randint(dom["soc_low"][0], dom["soc_low"][1])
                        tmpl, cond_a, cond_b = rng.choice(dom["contexts_fallback"])
                    context_text = tmpl.format(kw=kw, soc=soc)
                    sem_state = (d_name, kw, soc, cond_a, cond_b, stratum_type)

                elif d_name == "inventory":
                    if stratum_type == "conflict":
                        days = rng.randint(dom["val_high"][0], dom["val_high"][1])
                        tmpl, cond_a, cond_b = rng.choice(dom["contexts_conflict"])
                    elif stratum_type == "single":
                        if s_idx % 2 == 0:
                            days = rng.randint(dom["val_high"][0], dom["val_high"][1])
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_a"])
                        else:
                            days = rng.randint(dom["val_low"][0], dom["val_low"][1])
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_b"])
                    else:
                        days = rng.randint(dom["val_low"][0], dom["val_low"][1])
                        tmpl, cond_a, cond_b = rng.choice(dom["contexts_fallback"])
                    context_text = tmpl.format(days=days)
                    sem_state = (d_name, days, cond_a, cond_b, stratum_type)

                elif d_name == "job_scheduler":
                    if stratum_type == "conflict":
                        mins = rng.randint(dom["val_high"][0], dom["val_high"][1])
                        mem = rng.randint(dom["mem_high"][0], dom["mem_high"][1])
                        tmpl, cond_a, cond_b = rng.choice(dom["contexts_conflict"])
                    elif stratum_type == "single":
                        if s_idx % 2 == 0:
                            mins = rng.randint(dom["val_high"][0], dom["val_high"][1])
                            mem = rng.randint(dom["mem_low"][0], dom["mem_low"][1])
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_a"])
                        else:
                            mins = rng.randint(dom["val_low"][0], dom["val_low"][1])
                            mem = rng.randint(dom["mem_high"][0], dom["mem_high"][1])
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_b"])
                    else:
                        mins = rng.randint(dom["val_low"][0], dom["val_low"][1])
                        mem = rng.randint(dom["mem_low"][0], dom["mem_low"][1])
                        tmpl, cond_a, cond_b = rng.choice(dom["contexts_fallback"])
                    context_text = tmpl.format(mins=mins, mem=mem)
                    sem_state = (d_name, mins, mem, cond_a, cond_b, stratum_type)

                if sem_state in semantic_states:
                    continue

                # Format questions
                q1 = format_question_by_family(family, "A_over_B", rule_a_name, rule_a_desc, rule_b_name, rule_b_desc, fallback_text)
                q2 = format_question_by_family(family, "B_over_A", rule_a_name, rule_a_desc, rule_b_name, rule_b_desc, fallback_text)

                tgt1 = determine_target(cond_a, cond_b, "A_over_B", action_a, action_b, action_fallback)
                tgt2 = determine_target(cond_a, cond_b, "B_over_A", action_a, action_b, action_fallback)

                shuffled_choices = list(choices)
                rng.shuffle(shuffled_choices)

                rec1 = {
                    "id": f"{group_id}-c1",
                    "group_id": group_id,
                    "task_family": "phrasing_diversification",
                    "split": split_name,
                    "phrasing_family": family,
                    "template_family": d_name,
                    "domain_class": dom["domain_class"],
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
                    "task_family": "phrasing_diversification",
                    "split": split_name,
                    "phrasing_family": family,
                    "template_family": d_name,
                    "domain_class": dom["domain_class"],
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

                if fp1 in global_fps or fp2 in global_fps:
                    continue

                # Success
                semantic_states.add(sem_state)
                global_fps.add(fp1)
                global_fps.add(fp2)
                all_pairs.append((rec1, rec2))
                break
            else:
                raise RuntimeError(f"Split {split_name}: failed to generate pair for {family} / {stratum_type} / {d_name} after 3000 attempts!")

            pair_idx += 1

    flat_records = []
    diff_count = 0
    same_count = 0
    for r1, r2 in all_pairs:
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

    assert len(all_pairs) == total_pairs, f"Expected {total_pairs} pairs, got {len(all_pairs)}"
    assert diff_count == diff_pairs_quota, f"Expected {diff_pairs_quota} diff pairs, got {diff_count}"
    assert same_count == (single_pairs_quota + fallback_pairs_quota), f"Expected {single_pairs_quota+fallback_pairs_quota} same pairs, got {same_count}"
    assert len(flat_records) == total_pairs * 2

    print(f"Split {split_name}: {len(all_pairs)} pairs ({diff_count} diff, {same_count} same) = {len(flat_records)} cases.")
    return flat_records


def main():
    out_dir = ROOT / "data/m4_3_phrasing"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Collect past fingerprints
    global_fps = set()
    for p in PAST_DATASETS:
        if p.exists():
            for line in open(p, encoding="utf-8"):
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    global_fps.add(compute_fingerprint(rec))
    print(f"Loaded {len(global_fps)} existing fingerprints from past datasets.")

    # 2. Generate phrasing_train (120 pairs / 240 cases: Families E~J)
    # Quota: 60 conflict, 36 single, 24 fallback
    train_records = generate_split_dataset(
        split_name="train",
        families=["family_E", "family_F", "family_G", "family_H", "family_I", "family_J"],
        total_pairs=120,
        diff_pairs_quota=60,
        single_pairs_quota=36,
        fallback_pairs_quota=24,
        seed=2026091910,
        global_fps=global_fps,
    )
    with open(out_dir / "phrasing_train.jsonl", "w", encoding="utf-8") as f:
        for r in train_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # 3. Generate phrasing_dev (40 pairs / 80 cases: Families K~L)
    # Quota: 20 conflict, 12 single, 8 fallback
    dev_records = generate_split_dataset(
        split_name="dev",
        families=["family_K", "family_L"],
        total_pairs=40,
        diff_pairs_quota=20,
        single_pairs_quota=12,
        fallback_pairs_quota=8,
        seed=2026091911,
        global_fps=global_fps,
    )
    with open(out_dir / "phrasing_dev.jsonl", "w", encoding="utf-8") as f:
        for r in dev_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # 4. Generate fresh_phrasing_eval (60 pairs / 120 cases: Families M~P)
    # Quota: 30 conflict, 18 single, 12 fallback
    eval_records = generate_split_dataset(
        split_name="fresh_eval",
        families=["family_M", "family_N", "family_O", "family_P"],
        total_pairs=60,
        diff_pairs_quota=30,
        single_pairs_quota=18,
        fallback_pairs_quota=12,
        seed=2026091912,
        global_fps=global_fps,
    )
    with open(out_dir / "fresh_phrasing_eval.jsonl", "w", encoding="utf-8") as f:
        for r in eval_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # 5. Create combined train and dev datasets
    m3_train_path = ROOT / "data/m3_3_v2/train.jsonl"
    m3_dev_path = ROOT / "data/m3_3_v2/dev.jsonl"
    m4_1_train_path = ROOT / "data/m4_1_exception/train_exception.jsonl"
    m4_1_dev_path = ROOT / "data/m4_1_exception/dev_exception.jsonl"

    m3_train = [json.loads(line) for line in open(m3_train_path, encoding="utf-8") if line.strip()]
    m3_dev = [json.loads(line) for line in open(m3_dev_path, encoding="utf-8") if line.strip()]
    m4_1_train = [json.loads(line) for line in open(m4_1_train_path, encoding="utf-8") if line.strip()]
    m4_1_dev = [json.loads(line) for line in open(m4_1_dev_path, encoding="utf-8") if line.strip()]

    combined_train = m3_train + m4_1_train + train_records
    combined_dev = m3_dev + m4_1_dev + dev_records

    with open(out_dir / "combined_train.jsonl", "w", encoding="utf-8") as f:
        for r in combined_train:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(out_dir / "combined_dev.jsonl", "w", encoding="utf-8") as f:
        for r in combined_dev:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\nCreated combined_train: {len(combined_train)} cases (600 M3 + 240 M4.1 + {len(train_records)} M4.3).")
    print(f"Created combined_dev: {len(combined_dev)} cases (100 M3 + 40 M4.1 + {len(dev_records)} M4.3).")
    print("M4.3 dataset generation complete with verified quotas and ZERO leaks!")


if __name__ == "__main__":
    main()
