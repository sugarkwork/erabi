"""New dataset generator for ERABI M3.3.

Eliminates:
1. Exact input overlaps across splits (train, dev, eval_v2) via fingerprint verification.
2. Boundary value shortcut (actual == threshold fixed bias -> diverse <, ==, >).
3. Two-attribute rank correlation shortcut in goal_following (ranks are generated independently).
4. Capacity min/max direction bug (server capacity is strictly max).

Outputs to data/m3_3_v2/:
- train.jsonl (~600 cases / 300 pairs)
- dev.jsonl (~100 cases / 50 pairs)
- eval_v2.jsonl (~200 cases / 100 pairs)
- manifest.json
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent


def normalize_text(t: str) -> str:
    return unicodedata.normalize("NFC", t).strip().lower()


def compute_input_fingerprint(context: str, question: str, choices: List[Dict[str, str]]) -> str:
    """Compute strict cryptographic fingerprint of model input (context + question + ordered choice texts)."""
    norm_ctx = normalize_text(context)
    norm_q = normalize_text(question)
    norm_choices = "###".join(normalize_text(c["text"]) for c in choices)
    combined = f"{norm_ctx}|||{norm_q}|||{norm_choices}"
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def compute_file_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


# ---------------------------------------------------------
# Goal Following Scenario Generator
# ---------------------------------------------------------

GOAL_DOMAINS = [
    # domain_name, prefix, unit1, unit2, attr1_name, attr2_name, adj1, adj2, dir1, dir2
    ("プラン", "プラン", "円", "日", "価格", "到着速度", "安い", "早く届く", "min", "min"),
    ("サーバー", "サーバー", "GB", "ms", "メモリ容量", "応答遅延", "大容量の", "低遅延な", "max", "min"),
    ("PC", "PC", "万円", "kg", "価格", "重量", "低価格な", "軽量な", "min", "min"),
    ("ホテル", "ホテル", "円", "分", "宿泊料金", "駅からの距離", "リーズナブルな", "駅から近い", "min", "min"),
    ("オフィス", "オフィス", "万円", "分", "賃料", "徒歩分数", "低コストな", "駅チカな", "min", "min"),
    ("配送便", "便", "円", "時間", "配送料", "配達所要時間", "安価な", "所要時間が短い", "min", "min"),
]


def generate_goal_following_scenario(
    group_id: str,
    domain_idx: int,
    rng: random.Random,
    novel_template: bool = False,
) -> List[Dict[str, Any]]:
    """Generate pair of criteria-switching questions with independent attribute ranks."""
    dom = GOAL_DOMAINS[domain_idx % len(GOAL_DOMAINS)]
    _, prefix, u1, u2, a1_name, a2_name, adj1, adj2, dir1, dir2 = dom

    # 3 distinct choices: A, B, C
    choice_letters = ["A", "B", "C"]
    choice_ids = ["a", "b", "c"]

    # Sample attribute 1 values (3 distinct values)
    if u1 == "円" and "ホテル" in dom[0]:
        v1_pool = sorted(rng.sample(range(4000, 15000, 500), 3))
    elif u1 == "円":
        v1_pool = sorted(rng.sample(range(500, 5000, 100), 3))
    elif u1 == "GB":
        v1_pool = sorted(rng.sample(range(64, 512, 32), 3))
    elif u1 == "万円":
        v1_pool = sorted(rng.sample(range(8, 50, 2), 3))
    else:
        v1_pool = sorted(rng.sample(range(100, 900, 50), 3))

    # Sample attribute 2 values (3 distinct values)
    if u2 == "日":
        v2_pool = sorted(rng.sample(range(1, 10), 3))
    elif u2 == "ms":
        v2_pool = sorted(rng.sample(range(2, 60, 2), 3))
    elif u2 == "kg":
        v2_pool = sorted(rng.sample(range(1, 8), 3))
    elif u2 == "分":
        v2_pool = sorted(rng.sample(range(2, 25), 3))
    elif u2 == "時間":
        v2_pool = sorted(rng.sample(range(1, 12), 3))
    else:
        v2_pool = sorted(rng.sample(range(1, 20), 3))

    # Independent permutations for attr1 and attr2 across the 3 choices
    # This completely eliminates rank correlation (attr1 best can be attr2 best, worst, or mid)
    p1 = [0, 1, 2]
    rng.shuffle(p1)
    p2 = [0, 1, 2]
    rng.shuffle(p2)

    items = []
    choices = []
    for idx in range(3):
        cid = choice_ids[idx]
        cname = f"{prefix}{choice_letters[idx]}"
        val1 = v1_pool[p1[idx]]
        val2 = v2_pool[p2[idx]]
        items.append({"id": cid, "name": cname, "v1": val1, "v2": val2})
        choices.append({"id": cid, "text": cname})

    # Shuffle presentation order in context to avoid positional correlation
    ctx_items = list(items)
    rng.shuffle(ctx_items)
    ctx_parts = [f"{it['name']}は{it['v1']}{u1}で{it['v2']}{u2}" for it in ctx_items]
    context = "、".join(ctx_parts) + "です。"

    # Compute ground truth mathematically based on dir1 and dir2
    if dir1 == "min":
        best_c1_item = min(items, key=lambda x: x["v1"])
    else:  # max
        best_c1_item = max(items, key=lambda x: x["v1"])
    best_c1_id = best_c1_item["id"]

    if dir2 == "min":
        best_c2_item = min(items, key=lambda x: x["v2"])
    else:  # max
        best_c2_item = max(items, key=lambda x: x["v2"])
    best_c2_id = best_c2_item["id"]

    # Templates
    if not novel_template:
        q1 = f"{a2_name}を考慮せず、最も{adj1}{prefix}を一つ選んでください。"
        q2 = f"{a1_name}を考慮せず、最も{adj2}{prefix}を一つ選んでください。"
    else:
        q1 = f"次の条件で決定せよ：{a2_name}は問わず、{adj1}ものを選択すること。"
        q2 = f"次の条件で決定せよ：{a1_name}は問わず、{adj2}ものを選択すること。"

    case1 = {
        "schema_version": "1",
        "id": f"{group_id}-c1",
        "group_id": group_id,
        "task_family": "goal_following",
        "language": "ja",
        "template_family": "novel" if novel_template else "seen",
        "context": context,
        "question": q1,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": best_c1_id},
        "source": {"kind": "generated", "reference": "M3.3-independent-generator"},
        "quality": {"label_status": "program_verified"},
    }
    case2 = {
        "schema_version": "1",
        "id": f"{group_id}-c2",
        "group_id": group_id,
        "task_family": "goal_following",
        "language": "ja",
        "template_family": "novel" if novel_template else "seen",
        "context": context,
        "question": q2,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": best_c2_id},
        "source": {"kind": "generated", "reference": "M3.3-independent-generator"},
        "quality": {"label_status": "program_verified"},
    }
    return [case1, case2]


# ---------------------------------------------------------
# Explicit Rule Scenario Generator
# ---------------------------------------------------------

def generate_explicit_rule_scenario(
    group_id: str,
    rule_type: int,
    rng: random.Random,
    novel_template: bool = False,
) -> List[Dict[str, Any]]:
    """Generate boundary and composite condition pairs with diverse states and no shortcuts."""
    choices_pass_fail = [{"id": "pass", "text": "合格"}, {"id": "fail", "text": "不合格"}]
    choices_action = [{"id": "heal", "text": "回復する"}, {"id": "wait", "text": "待機する"}]

    if rule_type == 0:
        # Boundary threshold test:
        # Crucial fix: sample actual to be below, exactly at, or above threshold
        threshold = rng.randint(20, 80)
        rel = rng.choice(["below", "at", "above"])
        if rel == "below":
            delta = rng.randint(1, 5)
            actual = threshold - delta
        elif rel == "above":
            delta = rng.randint(1, 5)
            actual = threshold + delta
        else:
            actual = threshold

        context = f"測定数値はちょうど{actual}点です。"

        if not novel_template:
            q1 = f"ルールに従って選んでください。{threshold}点以下なら合格、{threshold}点を超えるなら不合格とします。"
            q2 = f"ルールに従って選んでください。{threshold}点未満なら合格、{threshold}点以上なら不合格とします。"
        else:
            q1 = f"規定に照らし判定を行え。基準：{threshold}点以下は合格、それを超える数値は不合格。"
            q2 = f"規定に照らし判定を行え。基準：{threshold}点未満は合格、それ以上の数値は不合格。"

        # Mathematical truth
        ans1 = "pass" if actual <= threshold else "fail"
        ans2 = "pass" if actual < threshold else "fail"

        case1 = {
            "schema_version": "1",
            "id": f"{group_id}-c1",
            "group_id": group_id,
            "task_family": "explicit_rule",
            "rule_kind": "boundary",
            "language": "ja",
            "template_family": "novel" if novel_template else "seen",
            "context": context,
            "question": q1,
            "choices": choices_pass_fail,
            "target": {"kind": "hard", "choice_id": ans1},
            "source": {"kind": "generated", "reference": "M3.3-generator"},
            "quality": {"label_status": "program_verified"},
        }
        case2 = {
            "schema_version": "1",
            "id": f"{group_id}-c2",
            "group_id": group_id,
            "task_family": "explicit_rule",
            "rule_kind": "boundary",
            "language": "ja",
            "template_family": "novel" if novel_template else "seen",
            "context": context,
            "question": q2,
            "choices": choices_pass_fail,
            "target": {"kind": "hard", "choice_id": ans2},
            "source": {"kind": "generated", "reference": "M3.3-generator"},
            "quality": {"label_status": "program_verified"},
        }
        return [case1, case2]

    elif rule_type == 1:
        # Composite logic: Diverse threshold and HP values
        threshold = rng.choice([15, 20, 25, 30, 40])
        hp = rng.choice([threshold - 5, threshold - 2, threshold, threshold + 3, threshold + 8])
        has_item = rng.choice([True, False])
        context = f"現在のHPは{hp}。回復アイテム{'あり' if has_item else 'なし'}。"

        # Pair contrasting AND condition vs OR condition
        if not novel_template:
            q1 = f"ルールに従って選択してください。HPが{threshold}未満かつアイテムがあれば回復し、そうでなければ待機します。"
            q2 = f"ルールに従って選択してください。HPが{threshold}未満またはアイテムがあれば回復し、どちらでもなければ待機します。"
        else:
            q1 = f"行動規定：HPが{threshold}未満で、なおかつアイテムを所持している場合に回復、未充足時は待機を選べ。"
            q2 = f"行動規定：HPが{threshold}未満か、あるいはアイテムを所持している場合に回復、どちらも満たさない時は待機を選べ。"

        cond1_met = (hp < threshold and has_item)
        cond2_met = (hp < threshold or has_item)
        ans1 = "heal" if cond1_met else "wait"
        ans2 = "heal" if cond2_met else "wait"

        case1 = {
            "schema_version": "1",
            "id": f"{group_id}-c1",
            "group_id": group_id,
            "task_family": "explicit_rule",
            "rule_kind": "composite_logic",
            "language": "ja",
            "template_family": "novel" if novel_template else "seen",
            "context": context,
            "question": q1,
            "choices": choices_action,
            "target": {"kind": "hard", "choice_id": ans1},
            "source": {"kind": "generated", "reference": "M3.3-generator"},
            "quality": {"label_status": "program_verified"},
        }
        case2 = {
            "schema_version": "1",
            "id": f"{group_id}-c2",
            "group_id": group_id,
            "task_family": "explicit_rule",
            "rule_kind": "composite_logic",
            "language": "ja",
            "template_family": "novel" if novel_template else "seen",
            "context": context,
            "question": q2,
            "choices": choices_action,
            "target": {"kind": "hard", "choice_id": ans2},
            "source": {"kind": "generated", "reference": "M3.3-generator"},
            "quality": {"label_status": "program_verified"},
        }
        return [case1, case2]

    else:
        # Comparison condition: Warehouse inventory vs order demand
        inv = rng.randint(10, 100)
        diff = rng.choice([-15, -8, -2, 0, 3, 10, 20])
        demand = max(5, inv + diff)
        context = f"倉庫の在庫数は{inv}個、顧客からの受注数は{demand}個です。"
        choices_ship = [{"id": "ship", "text": "出荷する"}, {"id": "delay", "text": "出荷を見送る"}]

        if not novel_template:
            q1 = "業務ルール：在庫が受注数以上あれば即時出荷し、不足していれば出荷を見送ります。"
            q2 = "業務ルール：在庫が受注数を上回っている（受注数を超える）場合のみ出荷し、そうでなければ見送ります。"
        else:
            q1 = "処理基準：在庫数が受注数に達していれば出荷、足りなければ出荷見送りを適用せよ。"
            q2 = "処理基準：在庫数が受注数より多い場合に限り出荷、それ以下は見送りを適用せよ。"

        ans1 = "ship" if inv >= demand else "delay"
        ans2 = "ship" if inv > demand else "delay"

        case1 = {
            "schema_version": "1",
            "id": f"{group_id}-c1",
            "group_id": group_id,
            "task_family": "explicit_rule",
            "rule_kind": "comparison",
            "language": "ja",
            "template_family": "novel" if novel_template else "seen",
            "context": context,
            "question": q1,
            "choices": choices_ship,
            "target": {"kind": "hard", "choice_id": ans1},
            "source": {"kind": "generated", "reference": "M3.3-generator"},
            "quality": {"label_status": "program_verified"},
        }
        case2 = {
            "schema_version": "1",
            "id": f"{group_id}-c2",
            "group_id": group_id,
            "task_family": "explicit_rule",
            "rule_kind": "comparison",
            "language": "ja",
            "template_family": "novel" if novel_template else "seen",
            "context": context,
            "question": q2,
            "choices": choices_ship,
            "target": {"kind": "hard", "choice_id": ans2},
            "source": {"kind": "generated", "reference": "M3.3-generator"},
            "quality": {"label_status": "program_verified"},
        }
        return [case1, case2]


# ---------------------------------------------------------
# Build Dataset with Strict Cross-Split Fingerprint Isolation
# ---------------------------------------------------------

def build_dataset():
    out_dir = ROOT_DIR / "data" / "m3_3_v2"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Collect fingerprints from existing diagnostic suites to guarantee zero contamination
    existing_diagnostic_fingerprints: Set[str] = set()
    diag_files = [
        ROOT_DIR / "examples" / "smoke_cases.jsonl",
        ROOT_DIR / "data" / "m3_1" / "transfer_probe.jsonl",
    ]
    for df in diag_files:
        if df.exists():
            with open(df, "r", encoding="utf-8") as f:
                for line in f:
                    rec = json.loads(line)
                    fp = compute_input_fingerprint(rec["context"], rec["question"], rec["choices"])
                    existing_diagnostic_fingerprints.add(fp)
    print(f"Loaded {len(existing_diagnostic_fingerprints)} diagnostic fingerprints to avoid.")

    # Target specs:
    # train: 300 groups (600 cases) -> 150 GF + 150 ER
    # dev: 50 groups (100 cases) -> 25 GF + 25 ER
    # eval_v2: 100 groups (200 cases) -> 50 GF + 50 ER (with 50 seen / 50 novel templates)
    
    global_fingerprints: Set[str] = set(existing_diagnostic_fingerprints)
    splits = {
        "train": {"target_groups": 300, "novel_rate": 0.0},
        "dev": {"target_groups": 50, "novel_rate": 0.0},
        "eval_v2": {"target_groups": 100, "novel_rate": 0.5},
    }

    rng = random.Random(20260918)
    dataset_records: Dict[str, List[Dict[str, Any]]] = {"train": [], "dev": [], "eval_v2": []}
    split_fingerprints: Dict[str, Set[str]] = {"train": set(), "dev": set(), "eval_v2": set()}

    group_counter = 0

    for split_name, config in splits.items():
        target_groups = config["target_groups"]
        novel_rate = config["novel_rate"]
        groups_collected = 0

        while groups_collected < target_groups:
            is_novel = (rng.random() < novel_rate)
            # Alternate between GF and ER
            if groups_collected % 2 == 0:
                # GF
                dom_idx = rng.randint(0, len(GOAL_DOMAINS) - 1)
                gid = f"{split_name}-gf-{groups_collected:04d}"
                pair = generate_goal_following_scenario(gid, dom_idx, rng, novel_template=is_novel)
            else:
                # ER
                rule_type = rng.randint(0, 2)
                gid = f"{split_name}-er-{groups_collected:04d}"
                pair = generate_explicit_rule_scenario(gid, rule_type, rng, novel_template=is_novel)

            # Check fingerprints of both cases
            fp1 = compute_input_fingerprint(pair[0]["context"], pair[0]["question"], pair[0]["choices"])
            fp2 = compute_input_fingerprint(pair[1]["context"], pair[1]["question"], pair[1]["choices"])

            # Must be completely unseen globally
            if fp1 in global_fingerprints or fp2 in global_fingerprints or fp1 == fp2:
                # Reject collision and retry with new parameters
                continue

            # Accept group
            global_fingerprints.add(fp1)
            global_fingerprints.add(fp2)
            split_fingerprints[split_name].add(fp1)
            split_fingerprints[split_name].add(fp2)

            dataset_records[split_name].extend(pair)
            groups_collected += 1
            group_counter += 1

    # ---------------------------------------------------------
    # Verification of Invariants
    # ---------------------------------------------------------
    print("\n=== Verifying Invariants ===")
    for sname in ["train", "dev", "eval_v2"]:
        recs = dataset_records[sname]
        fps = split_fingerprints[sname]
        print(f"Split '{sname}': {len(recs)} cases, {len(fps)} unique fingerprints. Duplicates within split: {len(recs) - len(fps)}")
        assert len(recs) == len(fps), f"Internal duplicate found in {sname}!"

    # Cross-split overlap verification
    train_fps = split_fingerprints["train"]
    dev_fps = split_fingerprints["dev"]
    eval_fps = split_fingerprints["eval_v2"]

    train_dev_overlap = len(train_fps & dev_fps)
    train_eval_overlap = len(train_fps & eval_fps)
    dev_eval_overlap = len(dev_fps & eval_fps)

    print(f"Cross-split overlap: train <-> dev = {train_dev_overlap}")
    print(f"Cross-split overlap: train <-> eval_v2 = {train_eval_overlap}")
    print(f"Cross-split overlap: dev <-> eval_v2 = {dev_eval_overlap}")

    assert train_dev_overlap == 0, "Train-Dev overlap detected!"
    assert train_eval_overlap == 0, "Train-Eval overlap detected!"
    assert dev_eval_overlap == 0, "Dev-Eval overlap detected!"

    # Diagnostic suite collision check
    for sname, fps in split_fingerprints.items():
        overlap_with_diag = len(fps & existing_diagnostic_fingerprints)
        print(f"Overlap {sname} <-> diagnostics: {overlap_with_diag}")
        assert overlap_with_diag == 0, f"{sname} overlaps with existing diagnostic cases!"

    # ---------------------------------------------------------
    # Save files
    # ---------------------------------------------------------
    for sname, recs in dataset_records.items():
        fname = f"{sname}.jsonl"
        fpath = out_dir / fname
        with open(fpath, "w", encoding="utf-8") as f:
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"Saved {len(recs)} records to {fpath}")

    # Generate manifest.json
    manifest = {
        "version": "M3.3_v2",
        "description": "Rebuilt datasets eliminating cross-split leaks, rank correlations, and boundary biases.",
        "splits": {
            sname: {
                "file": f"{sname}.jsonl",
                "cases": len(dataset_records[sname]),
                "groups": len(dataset_records[sname]) // 2,
                "unique_fingerprints": len(split_fingerprints[sname]),
                "sha256": compute_file_sha256(out_dir / f"{sname}.jsonl"),
            }
            for sname in ["train", "dev", "eval_v2"]
        },
        "invariance_checks": {
            "cross_split_overlaps": {
                "train_dev": train_dev_overlap,
                "train_eval_v2": train_eval_overlap,
                "dev_eval_v2": dev_eval_overlap,
            },
            "diagnostic_overlaps": 0,
            "internal_duplicates": 0,
        },
    }

    manifest_path = out_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"Saved manifest to {manifest_path}")

    print("\nDataset generation successfully completed!")


if __name__ == "__main__":
    build_dataset()
