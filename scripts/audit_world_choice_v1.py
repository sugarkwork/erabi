"""Package and audit privately generated world-choice candidates, without models."""
from __future__ import annotations

import json
import random
import re
from collections import Counter

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

from erabi.schema import ChoiceRequest
from scripts.build_world_choice_v1 import (CATEGORIES, OUT, SEED, VERSION, collect,
    digest, historical_signatures, normalized, read_jsonl, save_json, signature,
    snapshot_existing, write_jsonl)


def template_text(row):
    # Also detect copies that differ only in numbers; this cannot detect all paraphrases.
    text = row["context"] + "\n" + row["question"]
    return re.sub(r"\d+(?:[.,]\d+)*", "NUM", normalized(text))


def near_duplicates(rows, threshold=0.90):
    if len(rows) < 2:
        return []
    vectors = TfidfVectorizer(analyzer="char", ngram_range=(3, 5), min_df=2, max_features=150000, dtype=np.float32).fit_transform([template_text(r) for r in rows])
    search = NearestNeighbors(n_neighbors=min(8, len(rows)), metric="cosine", algorithm="brute", n_jobs=2).fit(vectors)
    pairs = {}
    for start in range(0, len(rows), 200):
        distances, neighbors = search.kneighbors(vectors[start:start+200])
        for offset, (ds, ns) in enumerate(zip(distances, neighbors)):
            i = start + offset
            for distance, j in zip(ds, ns):
                if i != j and 1-float(distance) >= threshold:
                    left, right = sorted((i, int(j)))
                    pairs[left, right] = {"left": rows[left]["id"], "right": rows[right]["id"],
                        "similarity": round(1-float(distance), 6), "cross_split": rows[left]["split"] != rows[right]["split"]}
    return list(pairs.values())


def package():
    frozen_count = snapshot_existing()
    original = sorted(collect(), key=lambda r: r["id"])
    historical, historical_count = historical_signatures()
    pilot_signatures = set()
    for path in (OUT / "groups").glob("*.json"):
        if not path.name.startswith("wc1_main_" + VERSION + "_"):
            pilot_signatures.update(signature(r) for r in json.loads(path.read_text(encoding="utf-8"))["accepted"])
    review_path = OUT / "quality_exclusions.json"
    reviewed_exclusions = json.loads(review_path.read_text(encoding="utf-8")) if review_path.exists() else {}
    seen, ids = set(), set()
    exclusions = []
    rows = []
    for row in original:
        ChoiceRequest.from_dict(row)
        assert row["id"] not in ids
        ids.add(row["id"])
        assert 15 <= row["input_tokens"] <= 1024
        assert row["target"]["choice_id"] in {c["id"] for c in row["choices"]}
        sig = signature(row)
        if row["id"] in reviewed_exclusions:
            exclusions.append({"id": row["id"], "reason": "quality_review", "detail": reviewed_exclusions[row["id"]]})
            continue
        if sig in pilot_signatures:
            exclusions.append({"id": row["id"], "reason": "pilot_overlap"})
            continue
        if sig in seen or sig in historical:
            exclusions.append({"id": row["id"], "reason": "exact_input_duplicate"})
            continue
        seen.add(sig)
        rows.append(row)
    pairs = near_duplicates(rows)
    removed = set()
    for pair in pairs:
        if pair["left"] not in removed and pair["right"] not in removed:
            removed.add(pair["right"])
            exclusions.append({"id": pair["right"], "reason": "lexical_near_duplicate", "other_id": pair["left"], "similarity": pair["similarity"]})
    rows = [r for r in rows if r["id"] not in removed]
    write_jsonl(OUT / "duplicate_exclusions.jsonl", exclusions)
    save_json(OUT / "near_duplicate_pairs.json", pairs)
    clean = []
    for row in rows:
        new = {k: v for k, v in row.items() if k not in ("answer_explanation", "judge_reason")}
        new["source"] = {"kind": "deepseek_synthetic", "model": row["source_model"], "prompt_version": VERSION, "group": row["group_id"]}
        new["quality"] = {"label_status": "same_model_answer_blind_agreement_not_human_gold"}
        clean.append(new)
    write_jsonl(OUT / "all.jsonl", clean)
    split_groups = {}
    paths = {}
    for split in ("train", "dev", "calibration", "final_test"):
        split_rows = [r for r in clean if r["split"] == split]
        split_groups[split] = {r["group_id"] for r in split_rows}
        path = OUT / (split + ".jsonl")
        write_jsonl(path, split_rows)
        paths[split] = {"rows": len(split_rows), "groups": len(split_groups[split]), "sha256": digest(path)}
    for a in split_groups:
        for b in split_groups:
            if a != b:
                assert not split_groups[a] & split_groups[b]
    rng = random.Random(SEED + 910)
    samples = []
    for category in CATEGORIES:
        pool = [r for r in rows if r["domain"] == category]
        samples += rng.sample(pool, min(10, len(pool)))
    rng.shuffle(samples)
    sample_path = OUT / "review_sample_100.jsonl"
    if sample_path.exists():
        # Preserve the original random draw when applying review exclusions;
        # otherwise failed examples could quietly disappear from the audit sample.
        samples = [json.loads(line) for line in sample_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    else:
        write_jsonl(sample_path, samples)
    review_summary = {"status": "pending", "human_gold": False}
    decisions_path = OUT / "review_decisions.json"
    if decisions_path.exists():
        decisions = json.loads(decisions_path.read_text(encoding="utf-8"))
        assert decisions["sample_sha256"] == digest(sample_path)
        assert decisions["all_sample_rows_read"] is True
        assert decisions["reviewed_rows"] == len(samples)
        rejected_ids = set(decisions["rejected_ids"])
        assert rejected_ids <= {r["id"] for r in samples}
        assert rejected_ids <= reviewed_exclusions.keys()
        assert not rejected_ids & {r["id"] for r in clean}
        results = [{"id": r["id"], "domain": r["domain"],
            "decision": "quarantine" if r["id"] in rejected_ids else "retain_provisionally",
            "reason": reviewed_exclusions.get(r["id"], decisions.get("retained_notes", {}).get(r["id"], "No blocking defect found in this qualitative review."))}
            for r in samples]
        review_summary = {"status": "needs_independent_curation", "human_gold": False,
            "reviewer": decisions["reviewer"], "sample_rows": len(samples),
            "quarantined": len(rejected_ids), "retained_provisionally": len(samples)-len(rejected_ids),
            "by_category": {category: dict(Counter(r["decision"] for r in results if r["domain"] == category)) for category in CATEGORIES},
            "assessment": decisions["assessment"], "scope": decisions["scope"]}
        if "targeted_followup" in decisions:
            followup = decisions["targeted_followup"]
            assert set(followup["additional_excluded"]) <= reviewed_exclusions.keys()
            assert not set(followup["additional_excluded"]) & {r["id"] for r in clean}
            review_summary["targeted_followup"] = followup
        save_json(OUT / "review_report.json", {**review_summary, "sample_sha256": digest(sample_path), "items": results})
    lengths = sorted(r["input_tokens"] for r in rows)
    length_baseline = {}
    for category in CATEGORIES:
        subset = [r for r in rows if r["domain"] == category]
        hits = sum(max(r["choices"], key=lambda c: len(c["text"]))["id"] == r["target"]["choice_id"] for r in subset)
        length_baseline[category] = {"rows": len(subset), "longest_choice_top1": round(hits / len(subset), 4) if subset else None,
            "uniform_random_expected_top1": round(sum(1/len(r["choices"]) for r in subset)/len(subset), 4) if subset else None}
    manifest = {
        "dataset": "world_choice_v1", "prompt_version": VERSION, "sampling_seed": SEED + 910,
        "status": "private_synthetic_answer_blind_agreed_not_human_gold",
        "generated_accepted_before_dedup": len(original), "accepted": len(rows), "exclusions": dict(Counter(r["reason"] for r in exclusions)),
        "categories": dict(Counter(r["domain"] for r in rows)), "languages": dict(Counter(r["language"] for r in rows)),
        "choice_counts": dict(Counter(len(r["choices"]) for r in rows)), "splits": paths,
        "target_positions": {str(k): dict(Counter(r["target"]["choice_id"] for r in rows if len(r["choices"]) == k)) for k in (2, 4, 6, 8)},
        "choice_length_shortcut_audit": length_baseline,
        "actual_token_lengths": {"min": min(lengths, default=0), "median": lengths[len(lengths)//2] if lengths else 0,
            "p95": lengths[int(len(lengths)*.95)] if lengths else 0, "max": max(lengths, default=0), "over_512": sum(n>512 for n in lengths), "over_1024": sum(n>1024 for n in lengths)},
        "existing_rows_screened": historical_count, "exact_overlap_after_filter": 0,
        "pilot_inputs_screened": len(pilot_signatures),
        "existing_evaluation_files_unchanged": frozen_count, "group_split_overlap": 0,
        "lexical_near_duplicate_threshold": .90, "lexical_near_duplicate_pairs": len(pairs),
        "all_sha256": digest(OUT / "all.jsonl"), "random_review_sample": {"rows": len(samples), "sha256": digest(sample_path), "policy": "Original stratified random draw preserved after review exclusions; not resampled to hide failures."},
        "quality_review": review_summary,
        "cost": json.loads((OUT / "cost_summary.json").read_text(encoding="utf-8")),
        "limitations": ["Same-model answer-blind agreement is not independent human verification.", "Lexical near-duplicate screening covers this new main corpus only; historical corpora are screened for exact inputs, not near copies.", "Lexical screening does not prove absence of semantic or cross-language duplicates.", "Generation batches are group-disjoint; broad categories and instructions are shared across splits, not strictly held-out world/template families.", "No model training or benchmark scoring has been performed on this corpus."],
    }
    responses = [r for r in read_jsonl(OUT / "api_journal.jsonl") if r.get("event") == "response" and r.get("kind") == "generate"]
    manifest["raw_generated_rows"] = {
        "all_prompt_versions_including_pilots": sum(len(r["payload"].get("examples", [])) for r in responses),
        "main_v4": sum(len(r["payload"].get("examples", [])) for r in responses if any("main_v4" in i for i in r["ids"])),
        "note": "Counts parseable returned examples, not malformed or truncated text, requested slots, or accepted training rows."}
    manifest["main_generation_response_identifiers"] = dict(Counter(r["response_model"] for r in responses if any("main_v4" in i for i in r["ids"])))
    save_json(OUT / "manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    package()
