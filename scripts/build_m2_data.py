"""Script to build M2.1 dataset with strict group-level splits.

Generates:
  - System A: Goal following / criteria switching (pair questions per scenario)
  - System B: Explicit rules / composite conditions / boundary values (pair questions per scenario)
Splits:
  - train: 300 groups (600 cases)
  - dev: 50 groups (100 cases)
  - holdout: 100 groups (200 cases: 50 in-family groups + 50 novel template family groups)
Total: 450 groups (900 cases)
"""

from __future__ import annotations

import hashlib
import json
import os
import random
from typing import Any, Dict, List, Tuple


def generate_goal_following_scenario(
    group_idx: int, rng: random.Random, novel_template: bool = False
) -> List[Dict[str, Any]]:
    """Generate a pair of criteria-switching questions for the same context."""
    group_id = f"gf-grp-{group_idx:04d}"

    # Generate 3 distinct items with 2 conflicting attributes
    # e.g., Plan A, B, C with price and days
    domains = [
        ("プラン", "円", "日", "価格", "到着速度", "安い", "早く届く"),
        ("サーバー", "GB", "ms", "メモリ容量", "応答速度", "大容量の", "高速な"),
        ("PC", "万円", "kg", "価格", "軽さ", "低価格な", "軽量な"),
        ("ホテル", "円", "分", "宿泊料金", "駅からの近さ", "リーズナブルな", "駅から近い"),
    ]
    domain = domains[group_idx % len(domains)]
    prefix, u1, u2, attr1_name, attr2_name, adj1, adj2 = domain

    # Guarantee unique minimums for each attribute
    # Item 0: best in attr1, worst in attr2
    # Item 1: worst in attr1, best in attr2
    # Item 2: middle in both
    v1_list = [100, 300, 200]
    v2_list = [5, 1, 3]

    # Shuffle assignment to choices
    perm = [0, 1, 2]
    rng.shuffle(perm)
    items = []
    choice_ids = ["a", "b", "c"]
    choices = []
    best_attr1_id = None
    best_attr2_id = None

    for idx, p in enumerate(perm):
        cid = choice_ids[idx]
        val1 = v1_list[p] + rng.randint(1, 9) * 10
        val2 = v2_list[p]
        cname = f"{prefix}{cid.upper()}"
        items.append((cname, val1, val2, cid))
        choices.append({"id": cid, "text": cname})
        if p == 0:
            best_attr1_id = cid
        elif p == 1:
            best_attr2_id = cid

    # Build context
    ctx_parts = [f"{name}は{v1}{u1}で{v2}{u2}" for name, v1, v2, _ in items]
    context = "、".join(ctx_parts) + "です。"

    # Template styles
    if not novel_template:
        # Seen template style
        q1 = f"{attr2_name}を考慮せず、最も{adj1}{prefix}を一つ選んでください。"
        q2 = f"{attr1_name}を考慮せず、最も{adj2}{prefix}を一つ選んでください。"
    else:
        # Novel template style (distinct phrasing for generalization testing)
        q1 = f"次の条件で決定せよ：{attr2_name}は問わず、{adj1}ものを選択すること。"
        q2 = f"次の条件で決定せよ：{attr1_name}は問わず、{adj2}ものを選択すること。"

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
        "target": {"kind": "hard", "choice_id": best_attr1_id},
        "source": {"kind": "generated", "reference": "M2.1-generator"},
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
        "target": {"kind": "hard", "choice_id": best_attr2_id},
        "source": {"kind": "generated", "reference": "M2.1-generator"},
        "quality": {"label_status": "program_verified"},
    }

    return [case1, case2]


def generate_explicit_rule_scenario(
    group_idx: int, rng: random.Random, novel_template: bool = False
) -> List[Dict[str, Any]]:
    """Generate boundary and composite condition rule pairs."""
    group_id = f"er-grp-{group_idx:04d}"

    rule_type = group_idx % 3

    if rule_type == 0:
        # Boundary value: <= threshold vs < threshold
        threshold = rng.randint(5, 50)
        actual = threshold  # Exactly on boundary!
        context = f"測定値はちょうど{actual}点です。"
        choices = [{"id": "pass", "text": "合格"}, {"id": "fail", "text": "不合格"}]

        if not novel_template:
            # Rule 1: <= threshold is pass -> True -> pass
            q1 = f"ルールに従って選んでください。{threshold}点以下なら合格、{threshold}点を超えるなら不合格とします。"
            ans1 = "pass"
            # Rule 2: < threshold is pass -> actual is threshold -> False -> fail
            q2 = f"ルールに従って選んでください。{threshold}点未満なら合格、{threshold}点以上なら不合格とします。"
            ans2 = "fail"
        else:
            q1 = f"規定に照らし判定を行え。基準：{threshold}点以下は合格、それを超える数値は不合格。"
            ans1 = "pass"
            q2 = f"規定に照らし判定を行え。基準：{threshold}点未満は合格、それ以上の数値は不合格。"
            ans2 = "fail"

    elif rule_type == 1:
        # Composite AND condition
        # e.g., HP < 20 AND item available
        hp = rng.choice([15, 25])
        has_item = rng.choice([True, False])
        context = f"現在のHPは{hp}。回復アイテム{'あり' if has_item else 'なし'}。"
        choices = [{"id": "heal", "text": "回復する"}, {"id": "wait", "text": "待機する"}]

        # Rule 1: AND condition
        cond1_met = (hp < 20 and has_item)
        ans1 = "heal" if cond1_met else "wait"

        # Rule 2: OR condition
        cond2_met = (hp < 20 or has_item)
        ans2 = "heal" if cond2_met else "wait"

        if not novel_template:
            q1 = "ルールに従って選択してください。HPが20未満かつアイテムがあれば回復し、そうでなければ待機します。"
            q2 = "ルールに従って選択してください。HPが20未満またはアイテムがあれば回復し、どちらでもなければ待機します。"
        else:
            q1 = "行動基準：HPが20未満かつアイテム所持を満たす場合は回復、非該当は待機を選択せよ。"
            q2 = "行動基準：HPが20未満またはアイテム所持のいずれかを満たす場合は回復、非該当は待機を選択せよ。"

    else:
        # Numerical comparison between two entities
        val_x = rng.randint(10, 50)
        val_y = rng.randint(10, 50)
        while val_y == val_x:
            val_y = rng.randint(10, 50)
        context = f"倉庫Aの在庫は{val_x}箱、倉庫Bの在庫は{val_y}箱です。"
        choices = [{"id": "a", "text": "倉庫A"}, {"id": "b", "text": "倉庫B"}]

        if not novel_template:
            q1 = "在庫数がより多い倉庫を一つ選んでください。"
            ans1 = "a" if val_x > val_y else "b"
            q2 = "在庫数がより少ない倉庫を一つ選んでください。"
            ans2 = "a" if val_x < val_y else "b"
        else:
            q1 = "点検対象の指示：保有在庫が優勢（多い）側の拠点を指名せよ。"
            ans1 = "a" if val_x > val_y else "b"
            q2 = "点検対象の指示：保有在庫が劣勢（少ない）側の拠点を指名せよ。"
            ans2 = "a" if val_x < val_y else "b"

    case1 = {
        "schema_version": "1",
        "id": f"{group_id}-c1",
        "group_id": group_id,
        "task_family": "explicit_rule",
        "language": "ja",
        "template_family": "novel" if novel_template else "seen",
        "context": context,
        "question": q1,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": ans1},
        "source": {"kind": "generated", "reference": "M2.1-generator"},
        "quality": {"label_status": "program_verified"},
    }
    case2 = {
        "schema_version": "1",
        "id": f"{group_id}-c2",
        "group_id": group_id,
        "task_family": "explicit_rule",
        "language": "ja",
        "template_family": "novel" if novel_template else "seen",
        "context": context,
        "question": q2,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": ans2},
        "source": {"kind": "generated", "reference": "M2.1-generator"},
        "quality": {"label_status": "program_verified"},
    }

    return [case1, case2]


def main():
    rng = random.Random(42)
    output_dir = "data/m2_1"
    os.makedirs(output_dir, exist_ok=True)

    # 450 groups total:
    # 225 Goal Following groups + 225 Explicit Rule groups
    # Allocation:
    #   train: 300 groups (150 GF + 150 ER) -> 600 cases
    #   dev:   50 groups (25 GF + 25 ER)   -> 100 cases
    #   holdout: 100 groups (50 GF + 50 ER) -> 200 cases
    #     - 50 seen template (25 GF + 25 ER) -> 100 cases
    #     - 50 novel template (25 GF + 25 ER) -> 100 cases

    gf_groups: List[List[Dict[str, Any]]] = []
    er_groups: List[List[Dict[str, Any]]] = []

    # Generate 225 GF groups
    for i in range(225):
        # Last 25 groups are novel template
        is_novel = (i >= 200)
        grp = generate_goal_following_scenario(i, rng, novel_template=is_novel)
        gf_groups.append(grp)

    # Generate 225 ER groups
    for i in range(225):
        is_novel = (i >= 200)
        grp = generate_explicit_rule_scenario(i, rng, novel_template=is_novel)
        er_groups.append(grp)

    # Split groups
    # Train: first 150 of each (seen template) -> 300 groups
    train_groups = gf_groups[:150] + er_groups[:150]
    # Dev: next 25 of each (seen template) -> 50 groups
    dev_groups = gf_groups[150:175] + er_groups[150:175]
    # Holdout seen: next 25 of each (seen template) -> 50 groups
    # Holdout novel: last 25 of each (novel template) -> 50 groups
    holdout_groups = gf_groups[175:225] + er_groups[175:225]

    # Verify no group overlap
    train_gids = {c["group_id"] for g in train_groups for c in g}
    dev_gids = {c["group_id"] for g in dev_groups for c in g}
    holdout_gids = {c["group_id"] for g in holdout_groups for c in g}

    assert len(train_gids & dev_gids) == 0, "Train and Dev groups overlap!"
    assert len(train_gids & holdout_gids) == 0, "Train and Holdout groups overlap!"
    assert len(dev_gids & holdout_gids) == 0, "Dev and Holdout groups overlap!"

    # Flatten cases
    train_cases = [c for g in train_groups for c in g]
    dev_cases = [c for g in dev_groups for c in g]
    holdout_cases = [c for g in holdout_groups for c in g]

    # Write files
    def write_jsonl(filename: str, cases: List[Dict[str, Any]]) -> str:
        path = os.path.join(output_dir, filename)
        hasher = hashlib.sha256()
        with open(path, "w", encoding="utf-8") as f:
            for c in cases:
                line = json.dumps(c, ensure_ascii=False) + "\n"
                f.write(line)
                hasher.update(line.encode("utf-8"))
        return hasher.hexdigest()

    train_hash = write_jsonl("train.jsonl", train_cases)
    dev_hash = write_jsonl("dev.jsonl", dev_cases)
    holdout_hash = write_jsonl("holdout.jsonl", holdout_cases)

    # Write manifest
    manifest = {
        "generator_seed": 42,
        "splits": {
            "train": {
                "file": "train.jsonl",
                "groups": len(train_groups),
                "cases": len(train_cases),
                "sha256": train_hash,
            },
            "dev": {
                "file": "dev.jsonl",
                "groups": len(dev_groups),
                "cases": len(dev_cases),
                "sha256": dev_hash,
            },
            "holdout": {
                "file": "holdout.jsonl",
                "groups": len(holdout_groups),
                "cases": len(holdout_cases),
                "seen_template_cases": sum(1 for c in holdout_cases if c.get("template_family") == "seen"),
                "novel_template_cases": sum(1 for c in holdout_cases if c.get("template_family") == "novel"),
                "sha256": holdout_hash,
            },
        },
    }

    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("=== M2.1 Dataset Generation Complete ===")
    print(f"Train:   {len(train_groups)} groups, {len(train_cases)} cases")
    print(f"Dev:     {len(dev_groups)} groups, {len(dev_cases)} cases")
    print(f"Holdout: {len(holdout_groups)} groups, {len(holdout_cases)} cases (Seen: {manifest['splits']['holdout']['seen_template_cases']}, Novel: {manifest['splits']['holdout']['novel_template_cases']})")
    print(f"Manifest written to: {manifest_path}")


if __name__ == "__main__":
    main()
