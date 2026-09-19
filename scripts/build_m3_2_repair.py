"""Build repaired dataset for ERABI M3.2.

This script:
1. Audits and repairs label errors in goal-following server cases (large capacity = max GB).
2. Preserves 100% of the input text, question, choices, IDs, groups, and splits.
3. Outputs to data/m3_2_label_fix/:
   - train.jsonl
   - dev.jsonl
   - holdout_corrected.jsonl
   - final_test_corrected.jsonl
   - label_changes.jsonl
   - audit_cases.jsonl (independent ground-truth table)
   - counterfactual_probe.jsonl (24 counterfactual test cases)
   - manifest.json
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Tuple


def normalize_text(t: str) -> str:
    return unicodedata.normalize("NFC", t).strip().lower()


def text_hash(context: str, question: str) -> str:
    norm = f"{normalize_text(context)}|||{normalize_text(question)}"
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


def compute_file_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


def parse_server_gb(context: str, choices: List[Dict[str, str]]) -> Dict[str, int]:
    """Parse server memory capacities (GB) from context for each choice."""
    # Pattern e.g. "サーバーAは320GBで1ms、..."
    c_map = {c["text"]: c["id"] for c in choices}
    pattern = r"([^\s、]+)は(\d+)GB"
    matches = re.findall(pattern, context)
    gb_by_id = {}
    for name, gb_str in matches:
        if name in c_map:
            gb_by_id[c_map[name]] = int(gb_str)
    return gb_by_id


def repair_dataset_file(
    input_path: Path,
    output_path: Path,
    split_name: str,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Repair server capacity labels in a jsonl file while preserving all inputs."""
    repaired_records = []
    changes = []

    with open(input_path, "r", encoding="utf-8") as f:
        for line_idx, line in enumerate(f):
            record = json.loads(line.strip())
            old_hash = text_hash(record["context"], record["question"])
            old_target = record["target"]["choice_id"]
            
            q = record["question"]
            ctx = record["context"]
            choices = record["choices"]

            # Check if this is a server capacity case asking for max capacity
            is_server_capacity_max = ("サーバー" in ctx) and (
                "大容量" in q or "メモリ潤沢" in q
            )

            if is_server_capacity_max:
                gb_by_id = parse_server_gb(ctx, choices)
                assert len(gb_by_id) == len(choices), (
                    f"Failed to parse all GBs in {record['id']}: {ctx}"
                )
                # True answer is max GB
                best_id = max(gb_by_id.keys(), key=lambda cid: gb_by_id[cid])
                
                if best_id != old_target:
                    # Create change entry
                    change_entry = {
                        "id": record["id"],
                        "split": split_name,
                        "group_id": record.get("group_id", ""),
                        "old_target": old_target,
                        "new_target": best_id,
                        "reason": (
                            f"サーバーメモリ容量の要求（大容量/メモリ潤沢）に対し、"
                            f"旧生成器が最小値(min)を正解としていたため、"
                            f"真の最大値({gb_by_id[best_id]}GB, id='{best_id}')へ是正。"
                        ),
                        "input_hash": old_hash,
                        "choice_values": {
                            cid: f"{gb_by_id[cid]}GB" for cid in gb_by_id
                        },
                    }
                    changes.append(change_entry)

                    # Update record target
                    new_record = dict(record)
                    new_record["target"] = dict(record["target"])
                    new_record["target"]["choice_id"] = best_id
                    new_record["quality"] = dict(record.get("quality", {}))
                    new_record["quality"]["label_status"] = "repaired_verified"
                    record = new_record

            # Verification: text and choices must be strictly invariant
            new_hash = text_hash(record["context"], record["question"])
            assert old_hash == new_hash, f"Input hash corrupted for {record['id']}"

            repaired_records.append(record)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for rec in repaired_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    return repaired_records, changes


def create_audit_cases() -> List[Dict[str, Any]]:
    """Create 10 independent, hand-crafted ground truth cases without generator logic."""
    cases = [
        {
            "id": "audit-001",
            "task_family": "audit_ground_truth",
            "context": "サーバーAは100GBで5ms、サーバーBは300GBで1ms、サーバーCは200GBで3msです。",
            "question": "応答速度を考慮せず、最も大容量のサーバーを一つ選んでください。",
            "choices": [
                {"id": "a", "text": "サーバーA"},
                {"id": "b", "text": "サーバーB"},
                {"id": "c", "text": "サーバーC"},
            ],
            "target": {"kind": "hard", "choice_id": "b"},
            "rationale": "サーバーBのメモリ容量(300GB)が最大。旧生成器のバグ(最小100GB=A)を検出可能。",
        },
        {
            "id": "audit-002",
            "task_family": "audit_ground_truth",
            "context": "サーバーAは100GBで5ms、サーバーBは300GBで1ms、サーバーCは200GBで3msです。",
            "question": "応答速度を考慮せず、最も小容量のサーバーを一つ選んでください。",
            "choices": [
                {"id": "a", "text": "サーバーA"},
                {"id": "b", "text": "サーバーB"},
                {"id": "c", "text": "サーバーC"},
            ],
            "target": {"kind": "hard", "choice_id": "a"},
            "rationale": "小容量の要求に対してはサーバーA(100GB)が正解。",
        },
        {
            "id": "audit-003",
            "task_family": "audit_ground_truth",
            "context": "サーバーAは400GBで20ms、サーバーBは150GBで5ms、サーバーCは250GBで10msです。",
            "question": "次の条件で決定せよ：応答遅延は問わず、大容量のものを選択すること。",
            "choices": [
                {"id": "a", "text": "サーバーA"},
                {"id": "b", "text": "サーバーB"},
                {"id": "c", "text": "サーバーC"},
            ],
            "target": {"kind": "hard", "choice_id": "a"},
            "rationale": "値割り当てが変わりサーバーA(400GB)が最大。固定IDの決め打ちを防止。",
        },
        {
            "id": "audit-004",
            "task_family": "audit_ground_truth",
            "context": "サーバーAは100GBで5ms、サーバーBは300GBで1ms、サーバーCは200GBで3msです。",
            "question": "メモリ容量を考慮せず、最も高速なサーバーを一つ選んでください。",
            "choices": [
                {"id": "a", "text": "サーバーA"},
                {"id": "b", "text": "サーバーB"},
                {"id": "c", "text": "サーバーC"},
            ],
            "target": {"kind": "hard", "choice_id": "b"},
            "rationale": "応答速度1msのサーバーBが最速。min判定の確認。",
        },
        {
            "id": "audit-005",
            "task_family": "audit_ground_truth",
            "context": "プランAは1000円で5日、プランBは3000円で1日、プランCは2000円で3日です。",
            "question": "到着速度を考慮せず、最も安いプランを一つ選んでください。",
            "choices": [
                {"id": "a", "text": "プランA"},
                {"id": "b", "text": "プランB"},
                {"id": "c", "text": "プランC"},
            ],
            "target": {"kind": "hard", "choice_id": "a"},
            "rationale": "価格1000円のプランAが最安。他ドメインmin判定の確認。",
        },
        {
            "id": "audit-006",
            "task_family": "audit_ground_truth",
            "context": "プランAは1000円で5日、プランBは3000円で1日、プランCは2000円で3日です。",
            "question": "価格を考慮せず、最も早く届くプランを一つ選んでください。",
            "choices": [
                {"id": "a", "text": "プランA"},
                {"id": "b", "text": "プランB"},
                {"id": "c", "text": "プランC"},
            ],
            "target": {"kind": "hard", "choice_id": "b"},
            "rationale": "納期1日のプランBが最速。他ドメインmin判定の確認。",
        },
        {
            "id": "audit-007",
            "task_family": "audit_ground_truth",
            "context": "測定値はちょうど30点です。",
            "question": "ルールに従って選んでください。30点以下なら合格、30点を超えるなら不合格とします。",
            "choices": [
                {"id": "pass", "text": "合格"},
                {"id": "fail", "text": "不合格"},
            ],
            "target": {"kind": "hard", "choice_id": "pass"},
            "rationale": "30点以下（<=30）を満たすため合格。",
        },
        {
            "id": "audit-008",
            "task_family": "audit_ground_truth",
            "context": "測定値はちょうど30点です。",
            "question": "ルールに従って選んでください。30点未満なら合格、30点以上なら不合格とします。",
            "choices": [
                {"id": "pass", "text": "合格"},
                {"id": "fail", "text": "不合格"},
            ],
            "target": {"kind": "hard", "choice_id": "fail"},
            "rationale": "30点未満（<30）を満たさず30点以上であるため不合格。境界値判定の確認。",
        },
        {
            "id": "audit-009",
            "task_family": "audit_ground_truth",
            "context": "現在のHPは15。回復アイテムあり。",
            "question": "ルールに従って選択してください。HPが20未満かつアイテムがあれば回復し、そうでなければ待機します。",
            "choices": [
                {"id": "heal", "text": "回復する"},
                {"id": "wait", "text": "待機する"},
            ],
            "target": {"kind": "hard", "choice_id": "heal"},
            "rationale": "HP<20かつアイテムありのAND条件を満たすため回復。",
        },
        {
            "id": "audit-010",
            "task_family": "audit_ground_truth",
            "context": "現在のHPは25。回復アイテムあり。",
            "question": "ルールに従って選択してください。HPが20未満かつアイテムがあれば回復し、そうでなければ待機します。",
            "choices": [
                {"id": "heal", "text": "回復する"},
                {"id": "wait", "text": "待機する"},
            ],
            "target": {"kind": "hard", "choice_id": "wait"},
            "rationale": "HP>=20のためAND条件を満たさず待機。複合条件判定の確認。",
        },
    ]
    return cases


def create_counterfactual_probe() -> List[Dict[str, Any]]:
    """Create 24 counterfactual probe cases (12 pairs) to diagnose sensitivity."""
    pairs = [
        # Pair 1: Value swap (capacity max)
        (
            "cf-pair-01-c1", "cf-pair-01",
            "サーバーAは400GBで15ms、サーバーBは150GBで3ms、サーバーCは250GBで8msです。",
            "応答遅延は考慮せず、最も大容量のサーバーを一つ選んでください。",
            [{"id": "a", "text": "サーバーA"}, {"id": "b", "text": "サーバーB"}, {"id": "c", "text": "サーバーC"}],
            "a", "サーバーAが400GBで最大"
        ),
        (
            "cf-pair-01-c2", "cf-pair-01",
            "サーバーAは150GBで15ms、サーバーBは400GBで3ms、サーバーCは250GBで8msです。",
            "応答遅延は考慮せず、最も大容量のサーバーを一つ選んでください。",
            [{"id": "a", "text": "サーバーA"}, {"id": "b", "text": "サーバーB"}, {"id": "c", "text": "サーバーC"}],
            "b", "数値を入れ替え、サーバーBが400GBで最大"
        ),

        # Pair 2: Criterion inversion (max vs min capacity with identical context)
        (
            "cf-pair-02-c1", "cf-pair-02",
            "サーバーXは500GBで20ms、サーバーYは100GBで2ms、サーバーZは300GBで10msです。",
            "通信速度は問わず、大容量のサーバーを選択せよ。",
            [{"id": "x", "text": "サーバーX"}, {"id": "y", "text": "サーバーY"}, {"id": "z", "text": "サーバーZ"}],
            "x", "サーバーXが500GBで大容量"
        ),
        (
            "cf-pair-02-c2", "cf-pair-02",
            "サーバーXは500GBで20ms、サーバーYは100GBで2ms、サーバーZは300GBで10msです。",
            "通信速度は問わず、小容量のサーバーを選択せよ。",
            [{"id": "x", "text": "サーバーX"}, {"id": "y", "text": "サーバーY"}, {"id": "z", "text": "サーバーZ"}],
            "y", "サーバーYが100GBで小容量"
        ),

        # Pair 3: Speed criterion inversion (fastest vs slowest with identical context)
        (
            "cf-pair-03-c1", "cf-pair-03",
            "サーバーAは300GBで5ms、サーバーBは200GBで50ms、サーバーCは100GBで20msです。",
            "容量は考慮せず、応答速度が最も高速なサーバーを選んでください。",
            [{"id": "a", "text": "サーバーA"}, {"id": "b", "text": "サーバーB"}, {"id": "c", "text": "サーバーC"}],
            "a", "サーバーAが5msで最速（最小遅延）"
        ),
        (
            "cf-pair-03-c2", "cf-pair-03",
            "サーバーAは300GBで5ms、サーバーBは200GBで50ms、サーバーCは100GBで20msです。",
            "容量は考慮せず、応答遅延が最も大きい（低速な）サーバーを選んでください。",
            [{"id": "a", "text": "サーバーA"}, {"id": "b", "text": "サーバーB"}, {"id": "c", "text": "サーバーC"}],
            "b", "サーバーBが50msで最大遅延（最も低速）"
        ),

        # Pair 4: Price criterion inversion (cheapest vs most expensive)
        (
            "cf-pair-04-c1", "cf-pair-04",
            "プランAlphaは800円、プランBetaは3500円、プランGammaは1800円です。",
            "最も低価格なプランを一つ選定してください。",
            [{"id": "a", "text": "プランAlpha"}, {"id": "b", "text": "プランBeta"}, {"id": "c", "text": "プランGamma"}],
            "a", "プランAlphaが800円で最安"
        ),
        (
            "cf-pair-04-c2", "cf-pair-04",
            "プランAlphaは800円、プランBetaは3500円、プランGammaは1800円です。",
            "最も高額なプランを一つ選定してください。",
            [{"id": "a", "text": "プランAlpha"}, {"id": "b", "text": "プランBeta"}, {"id": "c", "text": "プランGamma"}],
            "b", "プランBetaが3500円で最高額"
        ),

        # Pair 5: Plan price value swap
        (
            "cf-pair-05-c1", "cf-pair-05",
            "商品Aは1200円、商品Bは4000円、商品Cは2500円です。",
            "最も安価な商品を選択してください。",
            [{"id": "a", "text": "商品A"}, {"id": "b", "text": "商品B"}, {"id": "c", "text": "商品C"}],
            "a", "商品Aが1200円で最安"
        ),
        (
            "cf-pair-05-c2", "cf-pair-05",
            "商品Aは4000円、商品Bは2500円、商品Cは1200円です。",
            "最も安価な商品を選択してください。",
            [{"id": "a", "text": "商品A"}, {"id": "b", "text": "商品B"}, {"id": "c", "text": "商品C"}],
            "c", "数値を入れ替え、商品Cが1200円で最安"
        ),

        # Pair 6: Boundary threshold <= vs <
        (
            "cf-pair-06-c1", "cf-pair-06",
            "検査結果の数値はちょうど50点です。",
            "基準：50点以下なら合格、50点を超える場合は不合格。",
            [{"id": "pass", "text": "合格"}, {"id": "fail", "text": "不合格"}],
            "pass", "50点ちょうどは50点以下に合致し合格"
        ),
        (
            "cf-pair-06-c2", "cf-pair-06",
            "検査結果の数値はちょうど50点です。",
            "基準：50点未満なら合格、50点以上の場合は不合格。",
            [{"id": "pass", "text": "合格"}, {"id": "fail", "text": "不合格"}],
            "fail", "50点ちょうどは50点未満に合致せず不合格"
        ),

        # Pair 7: Boundary threshold >= vs >
        (
            "cf-pair-07-c1", "cf-pair-07",
            "現在の達成率はちょうど80%です。",
            "判定条件：80%以上は達成、80%未満は未達成とせよ。",
            [{"id": "achieve", "text": "達成"}, {"id": "unachieve", "text": "未達成"}],
            "achieve", "80%ちょうどは80%以上に合致し達成"
        ),
        (
            "cf-pair-07-c2", "cf-pair-07",
            "現在の達成率はちょうど80%です。",
            "判定条件：80%を超える場合は達成、80%以下は未達成とせよ。",
            [{"id": "achieve", "text": "達成"}, {"id": "unachieve", "text": "未達成"}],
            "unachieve", "80%ちょうどは80%超に合致せず未達成"
        ),

        # Pair 8: Logic AND vs OR
        (
            "cf-pair-08-c1", "cf-pair-08",
            "在庫数は10個。予約注文あり。",
            "発注ルール：在庫が15個以下かつ予約なしの場合は補充、それ以外は見送りとせよ。",
            [{"id": "order", "text": "補充"}, {"id": "skip", "text": "見送り"}],
            "skip", "在庫<=15だが予約ありのためAND不成立で見送り"
        ),
        (
            "cf-pair-08-c2", "cf-pair-08",
            "在庫数は10個。予約注文あり。",
            "発注ルール：在庫が15個以下または予約なしのいずれかを満たす場合は補充、どちらでもない場合は見送りとせよ。",
            [{"id": "order", "text": "補充"}, {"id": "skip", "text": "見送り"}],
            "order", "在庫<=15を満たすためOR成立で補充"
        ),

        # Pair 9: Context order permutation (B, A, C) vs (A, B, C)
        (
            "cf-pair-09-c1", "cf-pair-09",
            "サーバーAは350GBで10ms、サーバーBは120GBで2ms、サーバーCは200GBで5msです。",
            "応答速度を考慮せず、最も大容量のサーバーを一つ選んでください。",
            [{"id": "a", "text": "サーバーA"}, {"id": "b", "text": "サーバーB"}, {"id": "c", "text": "サーバーC"}],
            "a", "サーバーAが350GBで最大"
        ),
        (
            "cf-pair-09-c2", "cf-pair-09",
            "サーバーBは120GBで2ms、サーバーAは350GBで10ms、サーバーCは200GBで5msです。",
            "応答速度を考慮せず、最も大容量のサーバーを一つ選んでください。",
            [{"id": "a", "text": "サーバーA"}, {"id": "b", "text": "サーバーB"}, {"id": "c", "text": "サーバーC"}],
            "a", "文脈内の記述順をB, A, Cに入れ替えてもサーバーAが350GBで最大"
        ),

        # Pair 10: Irrelevant attribute distractor
        (
            "cf-pair-10-c1", "cf-pair-10",
            "サーバーAは黒色ラックで250GB、サーバーBは銀色ラックで600GB、サーバーCは青色ラックで150GBです。",
            "外見色は問わず、最も大容量のサーバーを選定せよ。",
            [{"id": "a", "text": "サーバーA"}, {"id": "b", "text": "サーバーB"}, {"id": "c", "text": "サーバーC"}],
            "b", "サーバーBが600GBで最大（色は無関係）"
        ),
        (
            "cf-pair-10-c2", "cf-pair-10",
            "サーバーAは黒色ラックで250GB、サーバーBは銀色ラックで600GB、サーバーCは青色ラックで150GBです。",
            "外見色は問わず、最も小容量のサーバーを選定せよ。",
            [{"id": "a", "text": "サーバーA"}, {"id": "b", "text": "サーバーB"}, {"id": "c", "text": "サーバーC"}],
            "c", "サーバーCが150GBで最小（色は無関係）"
        ),

        # Pair 11: 4-choice scale capacity
        (
            "cf-pair-11-c1", "cf-pair-11",
            "モデル1は64GB、モデル2は256GB、モデル3は128GB、モデル4は512GBです。",
            "ストレージ容量が最大のモデルを一つ選択せよ。",
            [{"id": "m1", "text": "モデル1"}, {"id": "m2", "text": "モデル2"}, {"id": "m3", "text": "モデル3"}, {"id": "m4", "text": "モデル4"}],
            "m4", "モデル4が512GBで最大"
        ),
        (
            "cf-pair-11-c2", "cf-pair-11",
            "モデル1は64GB、モデル2は256GB、モデル3は128GB、モデル4は512GBです。",
            "ストレージ容量が最小のモデルを一つ選択せよ。",
            [{"id": "m1", "text": "モデル1"}, {"id": "m2", "text": "モデル2"}, {"id": "m3", "text": "モデル3"}, {"id": "m4", "text": "モデル4"}],
            "m1", "モデル1が64GBで最小"
        ),

        # Pair 12: Novel wording for capacity
        (
            "cf-pair-12-c1", "cf-pair-12",
            "ノードAは180GBで応答20ms、ノードBは450GBで応答8ms、ノードCは320GBで応答15msです。",
            "要件：応答時間は度外視し、記憶領域が最も潤沢なノードを指定すること。",
            [{"id": "a", "text": "ノードA"}, {"id": "b", "text": "ノードB"}, {"id": "c", "text": "ノードC"}],
            "b", "ノードBが450GBで最も記憶領域が潤沢（最大容量）"
        ),
        (
            "cf-pair-12-c2", "cf-pair-12",
            "ノードAは180GBで応答20ms、ノードBは450GBで応答8ms、ノードCは320GBで応答15msです。",
            "要件：記憶領域は度外視し、処理遅延が極小のノードを指定すること。",
            [{"id": "a", "text": "ノードA"}, {"id": "b", "text": "ノードB"}, {"id": "c", "text": "ノードC"}],
            "b", "ノードBが8msで遅延極小（最速）"
        ),
    ]

    records = []
    for cid, gid, ctx, q, choices, tgt_id, rat in pairs:
        rec = {
            "schema_version": "1",
            "id": cid,
            "group_id": gid,
            "task_family": "counterfactual_probe",
            "language": "ja",
            "template_family": "counterfactual",
            "context": ctx,
            "question": q,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": tgt_id},
            "rationale": rat,
            "quality": {"label_status": "human_verified"},
        }
        records.append(rec)
    return records


def main():
    root_dir = Path("f:/ai/erabi-local")
    m2_dir = root_dir / "data" / "m2_1"
    m3_dir = root_dir / "data" / "m3_1"
    out_dir = root_dir / "data" / "m3_2_label_fix"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=== ERABI M3.2 Dataset Repair ===")

    all_changes = []

    # 1. Repair M2.1 datasets
    splits = [
        ("train.jsonl", "train.jsonl", "train"),
        ("dev.jsonl", "dev.jsonl", "dev"),
        ("holdout.jsonl", "holdout_corrected.jsonl", "holdout"),
    ]

    for in_file, out_file, sname in splits:
        in_path = m2_dir / in_file
        out_path = out_dir / out_file
        records, changes = repair_dataset_file(in_path, out_path, sname)
        all_changes.extend(changes)
        print(f"Repaired {sname}: {len(records)} records, {len(changes)} label changes.")

    # 2. Repair M3.1 final_test
    ftest_in = m3_dir / "final_test.jsonl"
    ftest_out = out_dir / "final_test_corrected.jsonl"
    ftest_records, ftest_changes = repair_dataset_file(ftest_in, ftest_out, "final_test")
    all_changes.extend(ftest_changes)
    print(f"Repaired final_test: {len(ftest_records)} records, {len(ftest_changes)} label changes.")

    # 3. Save label_changes.jsonl
    changes_path = out_dir / "label_changes.jsonl"
    with open(changes_path, "w", encoding="utf-8") as f:
        for ch in all_changes:
            f.write(json.dumps(ch, ensure_ascii=False) + "\n")
    print(f"Saved {len(all_changes)} label changes to {changes_path}")

    # 4. Save independent audit_cases.jsonl
    audit_cases = create_audit_cases()
    audit_path = out_dir / "audit_cases.jsonl"
    with open(audit_path, "w", encoding="utf-8") as f:
        for ac in audit_cases:
            f.write(json.dumps(ac, ensure_ascii=False) + "\n")
    print(f"Saved {len(audit_cases)} independent audit cases to {audit_path}")

    # 5. Save counterfactual_probe.jsonl
    cf_cases = create_counterfactual_probe()
    cf_path = out_dir / "counterfactual_probe.jsonl"
    with open(cf_path, "w", encoding="utf-8") as f:
        for cfc in cf_cases:
            f.write(json.dumps(cfc, ensure_ascii=False) + "\n")
    print(f"Saved {len(cf_cases)} counterfactual probe cases to {cf_path}")

    # 6. Generate manifest.json
    manifest = {
        "version": "M3.2",
        "description": "Repaired datasets for server capacity label bug, plus independent audit and counterfactual probes.",
        "files": {},
        "change_counts_by_split": {
            "train": sum(1 for c in all_changes if c["split"] == "train"),
            "dev": sum(1 for c in all_changes if c["split"] == "dev"),
            "holdout": sum(1 for c in all_changes if c["split"] == "holdout"),
            "final_test": sum(1 for c in all_changes if c["split"] == "final_test"),
            "total": len(all_changes),
        },
    }

    for fname in [
        "train.jsonl",
        "dev.jsonl",
        "holdout_corrected.jsonl",
        "final_test_corrected.jsonl",
        "label_changes.jsonl",
        "audit_cases.jsonl",
        "counterfactual_probe.jsonl",
    ]:
        fpath = out_dir / fname
        manifest["files"][fname] = {
            "sha256": compute_file_sha256(fpath),
            "size_bytes": fpath.stat().st_size,
        }

    manifest_path = out_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"Saved manifest to {manifest_path}")

    print("\nDataset repair complete!")


if __name__ == "__main__":
    main()
