"""Create a private, shuffled train/dev/final-test clone of curated Exam-QA.

Splits are group-disjoint. DeepSeek-generated distractors are train-only, and
prompt-pilot groups are forced into train. The final test must not be read by
the training loop until an epoch has been selected on dev.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "data" / "exam_qa_erabi_v1"
DEFAULT_OUTPUT = ROOT / "data" / "exam_qa_erabi_v1_reshuffle_20260924"
OFFICIAL_KIND = "official_choices_label_to_text"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def select_groups(
    grouped: dict[str, list[dict[str, Any]]],
    eligible: set[str],
    targets: dict[str, int],
    seed: int,
    salt: str,
) -> set[str]:
    selected: set[str] = set()
    counts: Counter[str] = Counter()
    ranked = sorted(eligible, key=lambda gid: hashlib.sha256(f"{seed}:{salt}:{gid}".encode()).hexdigest())
    for gid in ranked:
        if all(counts[language] >= target for language, target in targets.items()):
            break
        contribution = Counter(
            row["language"] for row in grouped[gid]
            if row["provenance"]["transform_kind"] == OFFICIAL_KIND
        )
        if any(counts[language] < targets[language] and contribution[language] for language in targets):
            selected.add(gid)
            counts.update(contribution)
    return selected


def make_splits(
    records: list[dict[str, Any]],
    pilot_source_ids: set[str],
    seed: int = 20260924,
    dev_fraction: float = 0.15,
    test_fraction: float = 0.20,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    if not 0 < dev_fraction < 0.4 or not 0 < test_fraction < 0.4 or dev_fraction + test_fraction >= 0.6:
        raise ValueError("dev/test fractions are out of bounds")
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        grouped[row["group_id"]].append(row)
    pilot_groups = {
        row["group_id"] for row in records if row["source"]["source_id"] in pilot_source_ids
    }
    official_counts = Counter(
        row["language"] for row in records if row["provenance"]["transform_kind"] == OFFICIAL_KIND
    )
    eligible = {
        gid for gid, rows in grouped.items()
        if gid not in pilot_groups and any(row["provenance"]["transform_kind"] == OFFICIAL_KIND for row in rows)
    }
    test_targets = {lang: max(1, round(count * test_fraction)) for lang, count in official_counts.items()}
    test_groups = select_groups(grouped, eligible, test_targets, seed, "final_test")
    remaining = eligible - test_groups
    dev_targets = {lang: max(1, round(count * dev_fraction)) for lang, count in official_counts.items()}
    dev_groups = select_groups(grouped, remaining, dev_targets, seed, "dev")

    splits = {"train": [], "dev": [], "final_test": [], "excluded": []}
    for row in records:
        copy = json.loads(json.dumps(row, ensure_ascii=False))
        gid = row["group_id"]
        if gid in test_groups or gid in dev_groups:
            split = "final_test" if gid in test_groups else "dev"
            if row["provenance"]["transform_kind"] != OFFICIAL_KIND:
                splits["excluded"].append({
                    "source_id": row["source"]["source_id"],
                    "group_id": gid,
                    "reason_code": f"synthetic_choices_in_{split}_group",
                })
                continue
        else:
            split = "train"
        copy["split"] = split
        splits[split].append(copy)

    rng = random.Random(seed)
    for name in ("train", "dev", "final_test"):
        rng.shuffle(splits[name])
    group_sets = {name: {row["group_id"] for row in splits[name]} for name in ("train", "dev", "final_test")}
    if group_sets["train"] & group_sets["dev"] or group_sets["train"] & group_sets["final_test"] or group_sets["dev"] & group_sets["final_test"]:
        raise AssertionError("split groups overlap")
    if any(row["provenance"]["transform_kind"] != OFFICIAL_KIND for name in ("dev", "final_test") for row in splits[name]):
        raise AssertionError("holdout contains generated distractors")
    if not pilot_groups <= group_sets["train"]:
        raise AssertionError("pilot group escaped train")
    manifest = {
        "seed": seed,
        "fractions": {"dev": dev_fraction, "final_test": test_fraction},
        "counts": {name: len(rows) for name, rows in splits.items()},
        "groups": {name: len(groups) for name, groups in group_sets.items()},
        "languages": {
            name: dict(sorted(Counter(row["language"] for row in splits[name]).items()))
            for name in ("train", "dev", "final_test")
        },
        "pilot_groups_forced_train": len(pilot_groups),
        "policy": "Group-disjoint; shuffled within split; generated distractors train-only; final_test unopened during epoch selection.",
        "status": "private_unpublished_deepseek_curated_unreviewed",
    }
    return splits, manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--seed", type=int, default=20260924)
    parser.add_argument("--dev-fraction", type=float, default=0.15)
    parser.add_argument("--test-fraction", type=float, default=0.20)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    records = read_jsonl(args.source_dir / "results_full_v3.jsonl")
    selection = json.loads((args.source_dir / "selection_pilot_v3.json").read_text(encoding="utf-8"))
    pilot_ids = {row["id"] for row in selection["records"]}
    splits, manifest = make_splits(records, pilot_ids, args.seed, args.dev_fraction, args.test_fraction)
    args.output_dir.mkdir(parents=True)
    for name, rows in splits.items():
        path = args.output_dir / f"{name}.jsonl"
        path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
        manifest.setdefault("sha256", {})[name] = sha256(path)
    (args.output_dir / "split_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
