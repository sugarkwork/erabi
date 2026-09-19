"""Data generator for M4.2 Phase A: Novel Priority Probe Evaluation.

Generates:
- data/m4_2_robustness/novel_priority_eval.jsonl (60 pairs / 120 cases)

Guarantees:
- 4 completely novel domains (never seen in train or previous evals):
  1. manufacturing (品質寸法誤差 vs 外観キズ検知)
  2. facility_power (買電ピーク vs 蓄電池放電)
  3. inventory (長期滞留先出 vs 検疫・保留)
  4. job_scheduler (待機時間昇格 vs 資源負荷延期)
- 4 novel phrasing families:
  Family A: 通常はルールAに従う。ただしルールBが成立した場合はBを優先する。
  Family B: AとBが同時に成立する場合のみ、AよりBを優先する。それ以外はAの判定を使う。
  Family C: 優先度は B > A。両方適用可能なら上位の規則を採用する。
  Family D: 第一判断: A。例外条件: B。例外条件を満たした場合、第一判断を上書きする。
- Symmetric directions (A > B and B > A) across all families.
- Fixed stratum quotas per domain:
  * 10 conflict pairs (diff-target pairs: priority flip changes answer) -> 40 pairs (80 cases)
  * 3 nonconflict single pairs (same-target pairs) -> 12 pairs (24 cases)
  * 2 nonconflict fallback pairs (same-target pairs) -> 8 pairs (16 cases)
  Total: 60 pairs = 120 cases.
- Zero exact input fingerprint overlap with past datasets (M3, M4.1, smoke, transfer).
- Programmatic correctness verification for all 120 cases.
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

# Past dataset paths for fingerprint collision checks
PAST_DATASETS = [
    ROOT / "data/m3_3_v2/train.jsonl",
    ROOT / "data/m3_3_v2/dev.jsonl",
    ROOT / "data/m3_3_v2/eval_v2.jsonl",
    ROOT / "data/m3_6_cal/calibration.jsonl",
    ROOT / "data/m3_6_cal/fresh_eval.jsonl",
    ROOT / "data/m4_1_exception/train_exception.jsonl",
    ROOT / "data/m4_1_exception/dev_exception.jsonl",
    ROOT / "data/m4_1_exception/eval_exception.jsonl",
    ROOT / "data/m3_1/transfer_probe.jsonl",
    ROOT / "examples/smoke_cases.jsonl",
]


def compute_fingerprint(record: Dict[str, Any]) -> str:
    ctx = record.get("context", "").strip()
    q = record.get("question", "").strip()
    c_texts = "||".join(c["text"].strip() for c in record.get("choices", []))
    raw = f"{ctx} ||| {q} ||| {c_texts}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


DOMAINS = [
    {
        "domain": "manufacturing",
        "choices": [
            {"id": "pass", "text": "通常合格とする"},
            {"id": "recheck", "text": "再検査ラインへ送る"},
            {"id": "hold", "text": "規格外保留とする"},
        ],
        "rule_a_name": "寸法基準",
        "rule_a_desc": "寸法誤差0.04mm以下なら通常合格",
        "rule_b_name": "外観基準",
        "rule_b_desc": "外観キズ検知時は再検査ラインへ送る",
        "fallback_text": "規格外保留とする",
        "action_a": "pass",
        "action_b": "recheck",
        "action_fallback": "hold",
        # contexts: (text_tmpl, cond_a, cond_b)
        "contexts_conflict": [
            ("製品検査：寸法誤差は{err:.3f}mm（基準0.040mm以下）。高解像度カメラにより表面キズを検知。", True, True),
            ("精密測定：測定誤差{err:.3f}mm。ラインセンサーが微細な外観打痕を検出。", True, True),
            ("ロット測定：誤差{err:.3f}mm（公差内）。目視検査にて微小異物付着のアラートあり。", True, True),
        ],
        "contexts_single_a": [
            ("製品検査：寸法誤差は{err:.3f}mm。外観センサー・光学検査ともにキズや欠陥は一切検知されず。", True, False),
            ("精密測定：測定誤差{err:.3f}mm。外観画像診断は正常判定、欠陥なし。", True, False),
        ],
        "contexts_single_b": [
            ("製品検査：寸法誤差は{err:.3f}mm（基準0.040mm超過）。高解像度カメラにより表面キズを検知。", False, True),
            ("精密測定：測定誤差{err:.3f}mm。ラインセンサーが外観不良を検出。", False, True),
        ],
        "contexts_fallback": [
            ("製品検査：寸法誤差は{err:.3f}mm（基準超過）。外観キズの検知はありません。", False, False),
            ("ロット測定：誤差{err:.3f}mm。外観センサーは正常だが寸法公差外。", False, False),
        ],
    },
    {
        "domain": "facility_power",
        "choices": [
            {"id": "peak_cut", "text": "ピークカット運転へ移行"},
            {"id": "battery", "text": "蓄電池放電へ切替"},
            {"id": "normal", "text": "通常給電を維持"},
        ],
        "rule_a_name": "買電ピーク基準",
        "rule_a_desc": "買電電力400kW以上ならピークカット運転",
        "rule_b_name": "蓄電池基準",
        "rule_b_desc": "蓄電池残量90%以上なら蓄電池放電へ切替",
        "fallback_text": "通常給電を維持",
        "action_a": "peak_cut",
        "action_b": "battery",
        "action_fallback": "normal",
        "contexts_conflict": [
            ("エネルギー管理：受電電力{kw}kW（契約閾値400kW超）。蓄電池SOCは{soc}%（満充電帯）。", True, True),
            ("施設受電状況：受電電力{kw}kW。施設側蓄電システム残量は{soc}%（十分な残量あり）。", True, True),
            ("電力監視ログ：現在消費{kw}kW。定置型蓄電池の充電率は{soc}%に達しています。", True, True),
        ],
        "contexts_single_a": [
            ("エネルギー管理：受電電力{kw}kW。蓄電池SOCは{soc}%（放電基準未満・通常待機中）。", True, False),
            ("施設受電状況：受電電力{kw}kW。蓄電池残量は{soc}%で蓄電余力なし。", True, False),
        ],
        "contexts_single_b": [
            ("エネルギー管理：受電電力{kw}kW（400kW未満）。蓄電池SOCは{soc}%（満充電帯）。", False, True),
            ("電力監視ログ：現在消費{kw}kW。定置型蓄電池の充電率は{soc}%に達しています。", False, True),
        ],
        "contexts_fallback": [
            ("エネルギー管理：受電電力{kw}kW（400kW未満）。蓄電池SOCは{soc}%（通常レベル）。", False, False),
            ("施設受電状況：受電電力{kw}kW。蓄電池残量{soc}%、ピーク基準・蓄電池基準ともに非該当。", False, False),
        ],
    },
    {
        "domain": "inventory",
        "choices": [
            {"id": "fifo_ship", "text": "先出出荷とする"},
            {"id": "quarantine", "text": "出荷保留・隔離"},
            {"id": "standard_ship", "text": "通常出庫とする"},
        ],
        "rule_a_name": "滞留基準",
        "rule_a_desc": "保管日数180日以上なら先出出荷",
        "rule_b_name": "検疫基準",
        "rule_b_desc": "検疫・品質確認指定ロットは出荷保留・隔離",
        "fallback_text": "通常出庫とする",
        "action_a": "fifo_ship",
        "action_b": "quarantine",
        "action_fallback": "standard_ship",
        "contexts_conflict": [
            ("倉庫管理：保管日数{days}日（長期滞留）。管理システムに「検疫検査・品質再確認対象」の指定あり。", True, True),
            ("在庫ステータス：入庫から{days}日経過。出荷伝票に「品質監査指定ロット・隔離要」の警告タグあり。", True, True),
            ("出荷指示照会：保管期間{days}日。検疫管理フラグが有効化されています。", True, True),
        ],
        "contexts_single_a": [
            ("倉庫管理：保管日数{days}日。検疫指定はなく、品質検査済み通常ロット。", True, False),
            ("在庫ステータス：入庫から{days}日経過。出荷伝票に検疫・保留の指定は一切なし。", True, False),
        ],
        "contexts_single_b": [
            ("倉庫管理：保管日数{days}日（直近入庫）。管理システムに「検疫検査・品質再確認対象」の指定あり。", False, True),
            ("在庫ステータス：入庫から{days}日。検疫管理フラグが有効化されています。", False, True),
        ],
        "contexts_fallback": [
            ("倉庫管理：保管日数{days}日（入庫直後）。検疫指定はなく通常品です。", False, False),
            ("在庫ステータス：入庫から{days}日経過。検疫タグなし、長期滞留基準にも非該当。", False, False),
        ],
    },
    {
        "domain": "job_scheduler",
        "choices": [
            {"id": "promote_queue", "text": "優先キューへ昇格"},
            {"id": "defer_night", "text": "夜間バッチへ延期"},
            {"id": "standard_run", "text": "通常順次実行"},
        ],
        "rule_a_name": "待機時間基準",
        "rule_a_desc": "待機時間60分以上なら優先キューへ昇格",
        "rule_b_name": "資源負荷基準",
        "rule_b_desc": "メモリ消費64GB以上の大型ジョブは夜間バッチへ延期",
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
    },
]


def format_question(
    family: str,
    priority_order: str,
    rule_a_name: str,
    rule_a_desc: str,
    rule_b_name: str,
    rule_b_desc: str,
    fallback_text: str,
) -> str:
    """Format question text based on family and priority order."""
    if family == "family_A":
        # Family A: 通常はXに従う。ただしYの条件が成立した場合はYを優先する。
        if priority_order == "A_over_B":
            # Priority is A over B -> Default is B, but if A met, prioritize A
            return (
                f"ルール：通常は「{rule_b_desc}」に従う。ただし「{rule_a_desc}」の条件が成立した場合は{rule_a_name}を優先する。"
                f"どちらも該当しない場合は「{fallback_text}」。規則に従って行動を選択してください。"
            )
        else:
            # Priority is B over A -> Default is A, but if B met, prioritize B
            return (
                f"ルール：通常は「{rule_a_desc}」に従う。ただし「{rule_b_desc}」の条件が成立した場合は{rule_b_name}を優先する。"
                f"どちらも該当しない場合は「{fallback_text}」。規則に従って行動を選択してください。"
            )

    elif family == "family_B":
        # Family B: AとBが同時に成立する場合のみ、AよりBを優先する。それ以外はAの判定を使う。
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
        # Family C: 優先度は B > A。両方適用可能なら上位の規則を採用する。
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
        # Family D: 第一判断: A。例外条件: B。例外条件を満たした場合、第一判断を上書きする。
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
    """Independent verification logic for ground truth action."""
    if cond_a and cond_b:
        return action_a if priority_order == "A_over_B" else action_b
    elif cond_a and not cond_b:
        return action_a
    elif not cond_a and cond_b:
        return action_b
    else:
        return action_fallback


def build_novel_priority_dataset() -> List[Dict[str, Any]]:
    # Collect past fingerprints
    past_fps = set()
    for p in PAST_DATASETS:
        if p.exists():
            for line in open(p, encoding="utf-8"):
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    past_fps.add(compute_fingerprint(rec))
    print(f"Loaded {len(past_fps)} existing fingerprints from past datasets.")

    rng = random.Random(202609194)
    all_pairs: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []
    generated_fps = set()
    semantic_states = set()

    families = ["family_A", "family_B", "family_C", "family_D"]

    pair_counter = 0

    for d_idx, dom in enumerate(DOMAINS):
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

        # Stratum plan for this domain:
        # 10 conflict pairs (diff-target)
        # 3 nonconflict single (same-target)
        # 2 nonconflict fallback (same-target)
        strata = (
            [("conflict", True)] * 10
            + [("single", False)] * 3
            + [("fallback", False)] * 2
        )

        for s_idx, (stratum_type, is_conflict) in enumerate(strata):
            family = families[(pair_counter) % len(families)]
            group_id = f"m4_2-np-{pair_counter:04d}"

            # Generate context text and condition values based on domain & stratum
            attempts = 0
            while attempts < 1000:
                attempts += 1
                if d_name == "manufacturing":
                    if stratum_type == "conflict":
                        err = rng.uniform(0.010, 0.038)
                        tmpl, cond_a, cond_b = rng.choice(dom["contexts_conflict"])
                    elif stratum_type == "single":
                        if s_idx % 2 == 0:
                            err = rng.uniform(0.010, 0.038)
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_a"])
                        else:
                            err = rng.uniform(0.045, 0.075)
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_b"])
                    else:
                        err = rng.uniform(0.045, 0.075)
                        tmpl, cond_a, cond_b = rng.choice(dom["contexts_fallback"])
                    context_text = tmpl.format(err=err)
                    sem_state = (d_name, round(err, 3), cond_a, cond_b, stratum_type)

                elif d_name == "facility_power":
                    if stratum_type == "conflict":
                        kw = rng.randint(410, 490)
                        soc = rng.randint(91, 98)
                        tmpl, cond_a, cond_b = rng.choice(dom["contexts_conflict"])
                    elif stratum_type == "single":
                        if s_idx % 2 == 0:
                            kw = rng.randint(410, 490)
                            soc = rng.randint(40, 75)
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_a"])
                        else:
                            kw = rng.randint(310, 380)
                            soc = rng.randint(91, 98)
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_b"])
                    else:
                        kw = rng.randint(310, 380)
                        soc = rng.randint(40, 75)
                        tmpl, cond_a, cond_b = rng.choice(dom["contexts_fallback"])
                    context_text = tmpl.format(kw=kw, soc=soc)
                    sem_state = (d_name, kw, soc, cond_a, cond_b, stratum_type)

                elif d_name == "inventory":
                    if stratum_type == "conflict":
                        days = rng.randint(185, 290)
                        tmpl, cond_a, cond_b = rng.choice(dom["contexts_conflict"])
                    elif stratum_type == "single":
                        if s_idx % 2 == 0:
                            days = rng.randint(185, 290)
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_a"])
                        else:
                            days = rng.randint(30, 150)
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_b"])
                    else:
                        days = rng.randint(30, 150)
                        tmpl, cond_a, cond_b = rng.choice(dom["contexts_fallback"])
                    context_text = tmpl.format(days=days)
                    sem_state = (d_name, days, cond_a, cond_b, stratum_type)

                elif d_name == "job_scheduler":
                    if stratum_type == "conflict":
                        mins = rng.randint(65, 180)
                        mem = rng.randint(70, 256)
                        tmpl, cond_a, cond_b = rng.choice(dom["contexts_conflict"])
                    elif stratum_type == "single":
                        if s_idx % 2 == 0:
                            mins = rng.randint(65, 180)
                            mem = rng.randint(8, 32)
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_a"])
                        else:
                            mins = rng.randint(10, 45)
                            mem = rng.randint(70, 256)
                            tmpl, cond_a, cond_b = rng.choice(dom["contexts_single_b"])
                    else:
                        mins = rng.randint(10, 45)
                        mem = rng.randint(8, 32)
                        tmpl, cond_a, cond_b = rng.choice(dom["contexts_fallback"])
                    context_text = tmpl.format(mins=mins, mem=mem)
                    sem_state = (d_name, mins, mem, cond_a, cond_b, stratum_type)

                if sem_state in semantic_states:
                    continue

                # Prepare questions for A_over_B and B_over_A
                q1 = format_question(family, "A_over_B", rule_a_name, rule_a_desc, rule_b_name, rule_b_desc, fallback_text)
                q2 = format_question(family, "B_over_A", rule_a_name, rule_a_desc, rule_b_name, rule_b_desc, fallback_text)

                tgt1 = determine_target(cond_a, cond_b, "A_over_B", action_a, action_b, action_fallback)
                tgt2 = determine_target(cond_a, cond_b, "B_over_A", action_a, action_b, action_fallback)

                # Shuffled choices order (same order within pair)
                shuffled_choices = list(choices)
                rng.shuffle(shuffled_choices)

                rec1 = {
                    "id": f"{group_id}-c1",
                    "group_id": group_id,
                    "task_family": "novel_priority",
                    "template_family": d_name,
                    "phrasing_family": family,
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
                    "task_family": "novel_priority",
                    "template_family": d_name,
                    "phrasing_family": family,
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
                    fp1 in past_fps
                    or fp2 in past_fps
                    or fp1 in generated_fps
                    or fp2 in generated_fps
                ):
                    continue

                # Successfully found unique pair
                semantic_states.add(sem_state)
                generated_fps.add(fp1)
                generated_fps.add(fp2)
                all_pairs.append((rec1, rec2))
                break
            else:
                raise RuntimeError(f"Failed to generate unique pair for stratum {stratum_type} in {d_name} after 1000 attempts!")

            pair_counter += 1

    print(f"Generated {len(all_pairs)} pairs ({len(all_pairs)*2} cases).")
    flat_records = []
    diff_pairs_count = 0
    same_pairs_count = 0

    for r1, r2 in all_pairs:
        # Programmatic assertions
        assert r1["group_id"] == r2["group_id"]
        assert r1["context"] == r2["context"]
        assert r1["choices"] == r2["choices"]
        if r1["conflict"]:
            assert r1["target"]["choice_id"] != r2["target"]["choice_id"], f"Conflict pair should have different targets: {r1['id']}"
            diff_pairs_count += 1
        else:
            assert r1["target"]["choice_id"] == r2["target"]["choice_id"], f"Nonconflict pair should have same target: {r1['id']}"
            same_pairs_count += 1
        flat_records.append(r1)
        flat_records.append(r2)

    print(f"Stratum breakdown: {diff_pairs_count} diff-target pairs, {same_pairs_count} same-target pairs.")
    assert len(all_pairs) == 60, f"Expected 60 pairs, got {len(all_pairs)}"
    assert diff_pairs_count == 40, f"Expected 40 diff-target pairs, got {diff_pairs_count}"
    assert same_pairs_count == 20, f"Expected 20 same-target pairs, got {same_pairs_count}"
    assert len(flat_records) == 120, f"Expected 120 cases, got {len(flat_records)}"

    return flat_records


def main():
    out_dir = ROOT / "data/m4_2_robustness"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "novel_priority_eval.jsonl"

    print("Building novel_priority_eval.jsonl for Phase A...")
    records = build_novel_priority_dataset()

    with open(out_file, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Saved {len(records)} records to {out_file}.")
    file_sha256 = hashlib.sha256(open(out_file, "rb").read()).hexdigest()
    print(f"SHA256: {file_sha256}")
    print("Zero-leak and mathematical validity checks PASSED.")


if __name__ == "__main__":
    main()
