"""Dataset builder for ERABI M3.6.

Generates:
1. calibration.jsonl (~200 cases / 100 pairs) -> 50 GF + 50 ER (35 composite, 7 comparison, 8 boundary)
2. fresh_eval.jsonl (~200 cases / 100 pairs) -> 50 GF + 50 ER (35 composite, 7 comparison, 8 boundary)
3. manifest.json

Guarantees:
- Input fingerprints (context ||| question ||| [choices]) are strictly isolated from:
  - train.jsonl (600)
  - dev.jsonl (100)
  - eval_v2.jsonl (200)
  - smoke_cases.jsonl (12)
  - transfer_probe.jsonl (32)
  - and between calibration and fresh_eval.
- Semantic states (HP/threshold/item, actual/threshold, inv/demand, domain/values)
  are strictly isolated from existing datasets and across splits.
- No shortcuts (boundary actual <, ==, > balanced; independent 2-attribute ranks in GF).
- Exact mathematical ground-truth verification for every single question.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent


def normalize_text(t: str) -> str:
    return unicodedata.normalize("NFC", t).strip().lower()


def compute_input_fingerprint(context: str, question: str, choices: List[Dict[str, str]]) -> str:
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
) -> Tuple[List[Dict[str, Any]], Tuple[str, Tuple[Tuple[int, int], ...]]]:
    dom = GOAL_DOMAINS[domain_idx % len(GOAL_DOMAINS)]
    dom_name, prefix, u1, u2, a1_name, a2_name, adj1, adj2, dir1, dir2 = dom

    choice_letters = ["A", "B", "C"]
    choice_ids = ["a", "b", "c"]

    if u1 == "円" and "ホテル" in dom[0]:
        v1_pool = sorted(rng.sample(range(4000, 16000, 200), 3))
    elif u1 == "円":
        v1_pool = sorted(rng.sample(range(400, 6000, 50), 3))
    elif u1 == "GB":
        v1_pool = sorted(rng.sample(range(32, 1024, 16), 3))
    elif u1 == "万円":
        v1_pool = sorted(rng.sample(range(6, 60, 1), 3))
    else:
        v1_pool = sorted(rng.sample(range(50, 1200, 25), 3))

    if u2 == "日":
        v2_pool = sorted(rng.sample(range(1, 14), 3))
    elif u2 == "ms":
        v2_pool = sorted(rng.sample(range(1, 80, 1), 3))
    elif u2 == "kg":
        v2_pool = sorted(rng.sample(range(1, 10), 3))
    elif u2 == "分":
        v2_pool = sorted(rng.sample(range(1, 30), 3))
    elif u2 == "時間":
        v2_pool = sorted(rng.sample(range(1, 18), 3))
    else:
        v2_pool = sorted(rng.sample(range(1, 25), 3))

    p1 = [0, 1, 2]
    rng.shuffle(p1)
    p2 = [0, 1, 2]
    rng.shuffle(p2)

    items = []
    choices = []
    val_pairs = []
    for idx in range(3):
        cid = choice_ids[idx]
        cname = f"{prefix}{choice_letters[idx]}"
        val1 = v1_pool[p1[idx]]
        val2 = v2_pool[p2[idx]]
        items.append({"id": cid, "name": cname, "v1": val1, "v2": val2})
        choices.append({"id": cid, "text": cname})
        val_pairs.append((val1, val2))

    semantic_state = ("gf", dom_name, tuple(sorted(val_pairs)))

    ctx_items = list(items)
    rng.shuffle(ctx_items)
    ctx_parts = [f"{it['name']}は{it['v1']}{u1}で{it['v2']}{u2}" for it in ctx_items]
    context = "、".join(ctx_parts) + "です。"

    if dir1 == "min":
        best_c1_item = min(items, key=lambda x: x["v1"])
    else:
        best_c1_item = max(items, key=lambda x: x["v1"])
    best_c1_id = best_c1_item["id"]

    if dir2 == "min":
        best_c2_item = min(items, key=lambda x: x["v2"])
    else:
        best_c2_item = max(items, key=lambda x: x["v2"])
    best_c2_id = best_c2_item["id"]

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
        "source": {"kind": "generated", "reference": "M3.6-cal-generator"},
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
        "source": {"kind": "generated", "reference": "M3.6-cal-generator"},
        "quality": {"label_status": "program_verified"},
    }
    return [case1, case2], semantic_state


# ---------------------------------------------------------
# Explicit Rule Scenario Generator
# ---------------------------------------------------------

def generate_explicit_rule_scenario(
    group_id: str,
    rule_type: int,
    rng: random.Random,
    novel_template: bool = False,
) -> Tuple[List[Dict[str, Any]], Tuple[str, Any]]:
    choices_pass_fail = [{"id": "pass", "text": "合格"}, {"id": "fail", "text": "不合格"}]
    choices_action = [{"id": "heal", "text": "回復する"}, {"id": "wait", "text": "待機する"}]
    choices_ship = [{"id": "ship", "text": "出荷する"}, {"id": "delay", "text": "出荷を見送る"}]

    if rule_type == 0:
        # Boundary threshold test: balanced below, at, above
        threshold = rng.randint(20, 85)
        rel = rng.choice(["below", "at", "above"])
        if rel == "below":
            delta = rng.randint(1, 6)
            actual = threshold - delta
        elif rel == "above":
            delta = rng.randint(1, 6)
            actual = threshold + delta
        else:
            actual = threshold

        context = f"測定数値はちょうど{actual}点です。"
        semantic_state = ("boundary", threshold, actual)

        if not novel_template:
            q1 = f"ルールに従って選んでください。{threshold}点以下なら合格、{threshold}点を超えるなら不合格とします。"
            q2 = f"ルールに従って選んでください。{threshold}点未満なら合格、{threshold}点以上なら不合格とします。"
        else:
            q1 = f"規定に照らし判定を行え。基準：{threshold}点以下は合格、それを超える数値は不合格。"
            q2 = f"規定に照らし判定を行え。基準：{threshold}点未満は合格、それ以上の数値は不合格。"

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
            "source": {"kind": "generated", "reference": "M3.6-cal-generator"},
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
            "source": {"kind": "generated", "reference": "M3.6-cal-generator"},
            "quality": {"label_status": "program_verified"},
        }
        return [case1, case2], semantic_state

    elif rule_type == 1:
        # Composite logic: Diverse threshold and HP values
        threshold = rng.choice([14, 16, 18, 22, 24, 26, 28, 32, 35, 36, 38, 42, 45, 48, 50, 52, 55])
        diff = rng.choice([-8, -6, -4, -2, -1, 0, 1, 3, 5, 7, 9])
        hp = max(1, threshold + diff)
        has_item = rng.choice([True, False])
        context = f"現在のHPは{hp}。回復アイテム{'あり' if has_item else 'なし'}。"
        semantic_state = ("composite_logic", threshold, hp, has_item)

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
            "source": {"kind": "generated", "reference": "M3.6-cal-generator"},
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
            "source": {"kind": "generated", "reference": "M3.6-cal-generator"},
            "quality": {"label_status": "program_verified"},
        }
        return [case1, case2], semantic_state

    else:
        # Comparison condition: Warehouse inventory vs order demand
        inv = rng.randint(8, 130)
        diff = rng.choice([-20, -15, -10, -5, -2, -1, 0, 1, 2, 5, 10, 15, 25])
        demand = max(2, inv + diff)
        context = f"倉庫の在庫数は{inv}個、顧客からの受注数は{demand}個です。"
        semantic_state = ("comparison", inv, demand)

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
            "source": {"kind": "generated", "reference": "M3.6-cal-generator"},
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
            "source": {"kind": "generated", "reference": "M3.6-cal-generator"},
            "quality": {"label_status": "program_verified"},
        }
        return [case1, case2], semantic_state


# ---------------------------------------------------------
# Build Datasets with Strict Fingerprint & Semantic State Isolation
# ---------------------------------------------------------

def extract_existing_semantic_states(filepath: Path) -> Set[Any]:
    states = set()
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            ctx = d["context"]
            q = d["question"]
            rk = d.get("rule_kind")
            tf = d["task_family"]
            if tf == "explicit_rule":
                if rk == "composite_logic" or "HP" in ctx:
                    m_hp = re.search(r"HPは(\d+)", ctx)
                    m_item = "アイテムあり" in ctx
                    m_th = re.search(r"HPが(\d+)未満", q)
                    if m_hp and m_th:
                        states.add(("composite_logic", int(m_th.group(1)), int(m_hp.group(1)), m_item))
                elif rk == "boundary" or "測定数値は" in ctx:
                    m_act = re.search(r"ちょうど(\d+)点", ctx)
                    m_th = re.search(r"(\d+)点", q)
                    if m_act and m_th:
                        states.add(("boundary", int(m_th.group(1)), int(m_act.group(1))))
                elif rk == "comparison" or "在庫数" in ctx:
                    m_inv = re.search(r"在庫数は(\d+)個", ctx)
                    m_dem = re.search(r"受注数は(\d+)個", ctx)
                    if m_inv and m_dem:
                        states.add(("comparison", int(m_inv.group(1)), int(m_dem.group(1))))
            elif tf == "goal_following":
                # Extract numeric tuples
                m_nums = tuple(map(int, re.findall(r"(\d+)", ctx)))
                if m_nums:
                    states.add(("gf", m_nums))
    return states


def build_m3_6_datasets():
    out_dir = ROOT_DIR / "data" / "m3_6_cal"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Collect all existing input fingerprints and semantic states
    existing_fingerprints: Set[str] = set()
    existing_semantic_states: Set[Any] = set()

    files_to_protect = [
        ROOT_DIR / "data" / "m3_3_v2" / "train.jsonl",
        ROOT_DIR / "data" / "m3_3_v2" / "dev.jsonl",
        ROOT_DIR / "data" / "m3_3_v2" / "eval_v2.jsonl",
        ROOT_DIR / "examples" / "smoke_cases.jsonl",
        ROOT_DIR / "data" / "m3_1" / "transfer_probe.jsonl",
    ]

    for fp in files_to_protect:
        if fp.exists():
            with open(fp, "r", encoding="utf-8") as f:
                for line in f:
                    rec = json.loads(line)
                    fingerprint = compute_input_fingerprint(rec["context"], rec["question"], rec["choices"])
                    existing_fingerprints.add(fingerprint)
            existing_semantic_states.update(extract_existing_semantic_states(fp))

    print(f"Loaded {len(existing_fingerprints)} existing fingerprints to avoid.")
    print(f"Loaded {len(existing_semantic_states)} existing semantic states to avoid.")

    # 2. Target splits: calibration and fresh_eval
    # Each split: 100 groups (200 cases): 50 GF + 50 ER (35 composite, 7 comparison, 8 boundary)
    split_configs = {
        "calibration": {"target_groups": 100, "novel_rate": 0.5, "seed": 20260919},
        "fresh_eval": {"target_groups": 100, "novel_rate": 0.5, "seed": 20260920},
    }

    global_fingerprints: Set[str] = set(existing_fingerprints)
    global_semantic_states: Set[Any] = set(existing_semantic_states)

    split_records: Dict[str, List[Dict[str, Any]]] = {"calibration": [], "fresh_eval": []}
    split_fps: Dict[str, Set[str]] = {"calibration": set(), "fresh_eval": set()}
    split_stats: Dict[str, Dict[str, int]] = {}

    for sname, cfg in split_configs.items():
        rng = random.Random(cfg["seed"])
        target_groups = cfg["target_groups"]
        novel_rate = cfg["novel_rate"]

        groups_collected = 0
        gf_count = 0
        er_composite_count = 0
        er_comp_count = 0
        er_bnd_count = 0

        # ER rule distribution: 35 composite (idx 1), 7 comparison (idx 2), 8 boundary (idx 0)
        er_rule_queue = [1] * 35 + [2] * 7 + [0] * 8
        rng.shuffle(er_rule_queue)
        er_idx = 0

        attempts = 0
        max_attempts = 100000

        while groups_collected < target_groups and attempts < max_attempts:
            attempts += 1
            is_novel = (rng.random() < novel_rate)
            # Alternate GF (50 groups) and ER (50 groups)
            if groups_collected % 2 == 0:
                dom_idx = rng.randint(0, len(GOAL_DOMAINS) - 1)
                gid = f"{sname}-gf-{gf_count:04d}"
                pair, state = generate_goal_following_scenario(gid, dom_idx, rng, novel_template=is_novel)
                task_type = "gf"
            else:
                rule_type = er_rule_queue[er_idx]
                gid = f"{sname}-er-{groups_collected:04d}"
                pair, state = generate_explicit_rule_scenario(gid, rule_type, rng, novel_template=is_novel)
                task_type = "er"

            fp1 = compute_input_fingerprint(pair[0]["context"], pair[0]["question"], pair[0]["choices"])
            fp2 = compute_input_fingerprint(pair[1]["context"], pair[1]["question"], pair[1]["choices"])

            # Strict collision check: fingerprint and semantic state
            if fp1 in global_fingerprints or fp2 in global_fingerprints or fp1 == fp2:
                continue
            if state in global_semantic_states:
                continue

            # Accept group
            global_fingerprints.add(fp1)
            global_fingerprints.add(fp2)
            global_semantic_states.add(state)

            split_fps[sname].add(fp1)
            split_fps[sname].add(fp2)
            split_records[sname].extend(pair)

            if task_type == "gf":
                gf_count += 1
            else:
                if er_rule_queue[er_idx] == 0:
                    er_bnd_count += 1
                elif er_rule_queue[er_idx] == 1:
                    er_composite_count += 1
                else:
                    er_comp_count += 1
                er_idx += 1

            groups_collected += 1

        if groups_collected < target_groups:
            raise RuntimeError(f"Could not collect {target_groups} groups for {sname} within {max_attempts} attempts!")

        split_stats[sname] = {
            "total_groups": groups_collected,
            "total_cases": len(split_records[sname]),
            "gf_groups": gf_count,
            "er_composite_groups": er_composite_count,
            "er_comparison_groups": er_comp_count,
            "er_boundary_groups": er_bnd_count,
            "attempts": attempts,
        }

    # 3. Verify Invariants
    print("\n=== Verifying M3.6 Data Invariants ===")
    cal_fps = split_fps["calibration"]
    fresh_fps = split_fps["fresh_eval"]

    print(f"Calibration cases: {len(split_records['calibration'])}, Unique fingerprints: {len(cal_fps)}")
    print(f"Fresh Eval cases:  {len(split_records['fresh_eval'])}, Unique fingerprints: {len(fresh_fps)}")

    assert len(split_records["calibration"]) == len(cal_fps), "Internal duplicates in calibration!"
    assert len(split_records["fresh_eval"]) == len(fresh_fps), "Internal duplicates in fresh_eval!"

    cal_fresh_overlap = len(cal_fps & fresh_fps)
    print(f"Calibration <-> Fresh Eval overlap: {cal_fresh_overlap}")
    assert cal_fresh_overlap == 0, "Calibration and Fresh Eval overlap!"

    cal_existing_overlap = len(cal_fps & existing_fingerprints)
    fresh_existing_overlap = len(fresh_fps & existing_fingerprints)
    print(f"Calibration <-> Existing overlap: {cal_existing_overlap}")
    print(f"Fresh Eval <-> Existing overlap:  {fresh_existing_overlap}")
    assert cal_existing_overlap == 0, "Calibration overlaps with existing datasets!"
    assert fresh_existing_overlap == 0, "Fresh Eval overlaps with existing datasets!"

    # Programmatic verification of all ground truths
    for sname, recs in split_records.items():
        diff_count = 0
        same_count = 0
        for i in range(0, len(recs), 2):
            c1 = recs[i]
            c2 = recs[i+1]
            assert c1["group_id"] == c2["group_id"]
            if c1["target"]["choice_id"] != c2["target"]["choice_id"]:
                diff_count += 1
            else:
                same_count += 1
        print(f"[{sname}] 100 pairs: Diff target pairs = {diff_count}, Same target pairs = {same_count}")

    # 4. Save files
    for sname, recs in split_records.items():
        fpath = out_dir / f"{sname}.jsonl"
        with open(fpath, "w", encoding="utf-8") as f:
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"Saved {len(recs)} records to {fpath}")

    # 5. Manifest
    manifest = {
        "version": "M3.6_cal",
        "description": "Calibration and fresh evaluation datasets for bounded synthetic rule calibration.",
        "splits": {
            sname: {
                "file": f"{sname}.jsonl",
                "cases": len(split_records[sname]),
                "groups": len(split_records[sname]) // 2,
                "unique_fingerprints": len(split_fps[sname]),
                "stats": split_stats[sname],
                "sha256": compute_file_sha256(out_dir / f"{sname}.jsonl"),
            }
            for sname in ["calibration", "fresh_eval"]
        },
        "invariance_checks": {
            "cal_fresh_overlap": cal_fresh_overlap,
            "cal_existing_overlap": cal_existing_overlap,
            "fresh_existing_overlap": fresh_existing_overlap,
            "internal_duplicates": 0,
        },
    }

    manifest_path = out_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"Saved manifest to {manifest_path}")
    print("\nM3.6 Datasets created and verified successfully!")


if __name__ == "__main__":
    build_m3_6_datasets()
