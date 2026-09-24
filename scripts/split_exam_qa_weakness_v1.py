"""Create deterministic private train/dev/final splits for weakness candidates."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "exam_qa_weakness_v1" / "train.jsonl"
OUTPUT = ROOT / "data" / "exam_qa_weakness_v1_split_20260924"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_rows(rows: list[dict], seed: int) -> dict[str, list[dict]]:
    buckets: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        buckets[(row["domain"], row["language"])].append(row)
    splits = {"train": [], "dev": [], "final_test": []}
    for key in sorted(buckets):
        bucket = list(buckets[key])
        random.Random(f"{seed}:{key[0]}:{key[1]}").shuffle(bucket)
        size = len(bucket)
        dev_count = max(1, round(size * 0.15))
        final_count = max(1, round(size * 0.15))
        train_count = size - dev_count - final_count
        if train_count < 1:
            raise ValueError(f"Stratum too small: {key}={size}")
        partitions = {
            "train": bucket[:train_count],
            "dev": bucket[train_count : train_count + dev_count],
            "final_test": bucket[train_count + dev_count :],
        }
        for split, selected in partitions.items():
            for source in selected:
                row = json.loads(json.dumps(source, ensure_ascii=False))
                row["split"] = split
                splits[split].append(row)
    for split in splits:
        splits[split].sort(key=lambda row: row["id"])
    group_sets = [{row["group_id"] for row in splits[name]} for name in ("train", "dev", "final_test")]
    if group_sets[0] & group_sets[1] or group_sets[0] & group_sets[2] or group_sets[1] & group_sets[2]:
        raise ValueError("group overlap")
    return splits


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    parser.add_argument("--seed", type=int, default=20260924)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    rows = read_jsonl(args.source)
    if not rows or len({row["id"] for row in rows}) != len(rows):
        raise ValueError("source must be nonempty with unique ids")
    splits = split_rows(rows, args.seed)
    args.output_dir.mkdir(parents=True)
    file_hashes = {}
    for name, selected in splits.items():
        path = args.output_dir / f"{name}.jsonl"
        path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in selected), encoding="utf-8")
        file_hashes[path.name] = sha256(path)
    manifest = {
        "source": str(args.source),
        "source_sha256": sha256(args.source),
        "seed": args.seed,
        "split_policy": "Stratified by domain and language; approximately 70/15/15; group-disjoint.",
        "counts": {name: len(selected) for name, selected in splits.items()},
        "domains": {name: dict(sorted(Counter(row["domain"] for row in selected).items())) for name, selected in splits.items()},
        "languages": {name: dict(sorted(Counter(row["language"] for row in selected).items())) for name, selected in splits.items()},
        "choice_counts": {name: dict(sorted(Counter(str(len(row["choices"])) for row in selected).items())) for name, selected in splits.items()},
        "length_tiers": {name: dict(sorted(Counter(row["generation_spec"]["length_tier"] for row in selected).items())) for name, selected in splits.items()},
        "sha256": file_hashes,
        "status": "private_unpublished_same_generator_split_not_human_gold",
    }
    (args.output_dir / "split_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
