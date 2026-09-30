"""Combine and audit private Decision Mix V2 v3/v4 production rows."""
from __future__ import annotations

import hashlib
import json
import random
import re
import statistics
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

from erabi.schema import ChoiceRequest
from scripts.build_decision_mix_v2 import OUT, SEED, _all_historical_signatures
from scripts.build_exam_qa_weakness_v1 import journal_cost, read_jsonl

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = ("v3", "v4")
NEAR_THRESHOLD = 0.90


def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def signature(row: dict[str, Any]) -> str:
    return hashlib.sha256(normalized(row["context"] + "\n" + row["question"]).encode()).hexdigest()


def canonical_group(row: dict[str, Any]) -> str:
    return re.sub(r"^dm2_main_v[34]_", "dm2_main_", row["group_id"])


def template_text(row: dict[str, Any]) -> str:
    text = row["context"] + "\n" + row["question"] + "\n" + "\n".join(choice["text"] for choice in row["choices"])
    return re.sub(r"\d+(?:[.,]\d+)*", "NUM", normalized(text))


def near_duplicates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    for family in sorted({row["domain"] for row in rows}):
        subset = [row for row in rows if row["domain"] == family]
        if len(subset) < 2:
            continue
        vectors = TfidfVectorizer(
            analyzer="char", ngram_range=(3, 5), min_df=2, max_features=150_000, dtype=np.float32
        ).fit_transform([template_text(row) for row in subset])
        search = NearestNeighbors(
            n_neighbors=min(10, len(subset)), metric="cosine", algorithm="brute", n_jobs=2
        ).fit(vectors)
        found: dict[tuple[int, int], dict[str, Any]] = {}
        for start in range(0, len(subset), 200):
            distances, neighbors = search.kneighbors(vectors[start:start + 200])
            for offset, (row_distances, row_neighbors) in enumerate(zip(distances, neighbors)):
                left_index = start + offset
                for distance, right_index_raw in zip(row_distances, row_neighbors):
                    right_index = int(right_index_raw)
                    similarity = 1 - float(distance)
                    if left_index == right_index or similarity < NEAR_THRESHOLD:
                        continue
                    left, right = sorted((left_index, right_index))
                    if canonical_group(subset[left]) == canonical_group(subset[right]):
                        continue
                    found[left, right] = {
                        "left": subset[left]["id"],
                        "right": subset[right]["id"],
                        "family": family,
                        "similarity": round(similarity, 6),
                        "cross_split": subset[left]["split"] != subset[right]["split"],
                    }
        pairs.extend(found.values())
    return sorted(pairs, key=lambda item: (item["family"], item["left"], item["right"]))


def load_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for version in VERSIONS:
        for path in sorted((OUT / "main" / "groups").glob(f"dm2_main_{version}_*.json")):
            value = json.loads(path.read_text(encoding="utf-8"))
            rows.extend(value.get("accepted", []))
    return sorted(rows, key=lambda row: row["id"])


def main() -> None:
    original = load_rows()
    historical, historical_count = _all_historical_signatures()
    ids: set[str] = set()
    seen: set[str] = set()
    retained: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    for row in original:
        ChoiceRequest.from_dict(row)
        if row["id"] in ids:
            exclusions.append({"id": row["id"], "reason": "duplicate_id"})
            continue
        ids.add(row["id"])
        if not 20 <= row["input_tokens"] <= 512:
            exclusions.append({"id": row["id"], "reason": "token_contract"})
            continue
        if row["target"]["choice_id"] not in {choice["id"] for choice in row["choices"]}:
            exclusions.append({"id": row["id"], "reason": "invalid_target"})
            continue
        sig = signature(row)
        if sig in historical:
            exclusions.append({"id": row["id"], "reason": "historical_exact_duplicate"})
            continue
        if sig in seen:
            exclusions.append({"id": row["id"], "reason": "decision_mix_exact_duplicate"})
            continue
        seen.add(sig)
        retained.append(row)

    pairs = near_duplicates(retained)
    removed: set[str] = set()
    for pair in sorted(pairs, key=lambda item: (-item["similarity"], item["right"])):
        if pair["left"] in removed or pair["right"] in removed:
            continue
        removed.add(pair["right"])
        exclusions.append({
            "id": pair["right"], "reason": "lexical_near_duplicate",
            "other_id": pair["left"], "similarity": pair["similarity"],
        })
    retained = [row for row in retained if row["id"] not in removed]

    clean: list[dict[str, Any]] = []
    for row in retained:
        clean_row = {key: value for key, value in row.items() if key != "answer_explanation"}
        clean_row["canonical_group_id"] = canonical_group(row)
        clean_row["quality"] = {
            "label_status": "deepseek_generated_answer_blind_agreed_not_human_gold",
            "generator_and_judge_are_same_model_family": True,
        }
        clean.append(clean_row)

    all_path = OUT / "combined_all.jsonl"
    write_jsonl(all_path, clean)
    write_jsonl(OUT / "combined_duplicate_exclusions.jsonl", exclusions)
    save_json(OUT / "combined_near_duplicate_pairs.json", pairs)

    split_groups: dict[str, set[str]] = {}
    split_stats: dict[str, Any] = {}
    for split in ("train", "dev", "calibration", "final_test"):
        split_rows = [row for row in clean if row["split"] == split]
        path = OUT / f"combined_{split}.jsonl"
        write_jsonl(path, split_rows)
        split_groups[split] = {row["canonical_group_id"] for row in split_rows}
        split_stats[split] = {"rows": len(split_rows), "groups": len(split_groups[split]), "sha256": digest(path)}
    overlaps = []
    for left_index, left in enumerate(split_groups):
        for right in list(split_groups)[left_index + 1:]:
            overlap = split_groups[left] & split_groups[right]
            if overlap:
                overlaps.append({"left": left, "right": right, "groups": sorted(overlap)})
    if overlaps:
        raise RuntimeError(f"group_split_overlap:{len(overlaps)}")

    rng = random.Random(SEED + 404)
    samples: list[dict[str, Any]] = []
    for family in sorted({row["domain"] for row in clean}):
        pool = [row for row in clean if row["domain"] == family]
        samples.extend(rng.sample(pool, min(10, len(pool))))
    rng.shuffle(samples)
    write_jsonl(OUT / "combined_review_sample.jsonl", samples)

    lengths = sorted(row["input_tokens"] for row in clean)
    shortcut = {}
    for family in sorted({row["domain"] for row in clean}):
        subset = [row for row in clean if row["domain"] == family]
        longest = sum(
            len(row["choices"][int(row["target"]["choice_id"][1:]) - 1]["text"])
            == max(len(choice["text"]) for choice in row["choices"])
            for row in subset
        )
        shortcut[family] = {"rows": len(subset), "longest_choice_correct_rate": round(longest / len(subset), 4)}

    journal = read_jsonl(OUT / "api_journal.jsonl")
    spent, reserved, _, _ = journal_cost(journal)
    rejection_counts = Counter()
    for row in read_jsonl(OUT / "rejections.jsonl"):
        row_id = str(row.get("id", ""))
        if row_id.startswith(("dm2_main_v3_", "dm2_main_v4_")):
            reason = row.get("reason") or row.get("stage") or "unknown"
            rejection_counts[str(reason)[:120]] += 1
    manifest = {
        "dataset": "decision_mix_v2",
        "status": "private_synthetic_answer_blind_agreed_not_human_gold",
        "versions": list(VERSIONS),
        "generated_accepted_before_combined_dedup": len(original),
        "accepted": len(clean),
        "exclusions": dict(Counter(row["reason"] for row in exclusions)),
        "families": dict(Counter(row["domain"] for row in clean)),
        "languages": dict(Counter(row["language"] for row in clean)),
        "splits": split_stats,
        "target_positions": dict(Counter(row["target"]["choice_id"] for row in clean)),
        "token_lengths": {
            "min": min(lengths, default=0),
            "median": statistics.median(lengths) if lengths else 0,
            "p95": lengths[min(len(lengths) - 1, int(len(lengths) * 0.95))] if lengths else 0,
            "max": max(lengths, default=0),
            "over_512": sum(length > 512 for length in lengths),
        },
        "choice_length_shortcut_audit": shortcut,
        "historical_rows_screened": historical_count,
        "exact_overlap_after_filter": 0,
        "canonical_group_split_overlap": 0,
        "near_duplicate_threshold": NEAR_THRESHOLD,
        "near_duplicate_pairs": len(pairs),
        "near_duplicate_excluded": len(removed),
        "generation_rejections": dict(rejection_counts),
        "cost": {
            "estimated_usd": round(spent, 8),
            "unresolved_reserved_usd": round(reserved, 8),
            "conservative_total_usd": round(spent + reserved, 8),
            "cap_usd": 15.0,
        },
        "combined_all_sha256": digest(all_path),
        "review_sample": {
            "rows": len(samples),
            "sha256": digest(OUT / "combined_review_sample.jsonl"),
            "status": "pending_independent_human_review",
        },
        "limitations": [
            "The generator and blind judge use the same DeepSeek model family; this is not independent human gold.",
            "Character n-gram screening does not prove absence of semantic or translated duplicates.",
            "No ERABI training, model selection, calibration, or final-test scoring has been performed.",
        ],
    }
    save_json(OUT / "combined_manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
