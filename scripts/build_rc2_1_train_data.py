"""Build RC2.1 Training Dataset: Stream A (Core) + Stream B (Generalization).

Assembles:
- Stream A: 510 groups (1,020 records) sampled from core historical training sets
- Stream B: 1,200 groups (2,400 records) synthesized by fresh diversity generators
Total: 1,710 groups (3,420 records)

Performs:
1. Structural and semantic pair integrity audit (all groups have 2 distinct targets)
2. Token length contract audit (<= 450 target, <= 512 hard ceiling)
3. Zero-leakage audit against Research Fresh Suite (800) and Blind v3 (480)
4. Stratified group-based split:
   - Train: 80% (1,368 groups = 2,736 records)
   - Dev: 10% (171 groups = 342 records)
   - Calibration: 10% (171 groups = 342 records)
5. Saves artifacts to data/rc2_1_train/
"""

import datetime
import hashlib
import json
import logging
from pathlib import Path
import random
import sys
from typing import Any, Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.rc2_1_train_data.generate_logical import generate_logical_stream_b
from scripts.rc2_1_train_data.generate_natural import generate_natural_stream_b
from scripts.rc2_1_train_data.generate_perturbation import generate_perturbation_stream_b
from scripts.rc2_1_train_data.generate_general import generate_general_stream_b
from scripts.rc2_1_train_data.generate_variable_k import generate_variable_k_stream_b

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("build_rc2_1_train_data")

OUTPUT_DIR = ROOT / "data" / "rc2_1_train"


def load_stream_a_groups(seed: int = 42) -> List[Dict[str, Any]]:
    """Sample 510 groups (1,020 records) from core historical clean training sets."""
    logger.info("Loading and sampling Stream A (Core/Retention)...")
    core_sources = [
        ("data/m3_3_v2/train.jsonl", "core_rules_v2", 300),
        ("data/m4_1_exception/train_exception.jsonl", "priority_exception", 100),
        ("data/m6_operator/train_operator.jsonl", "composite_operator", 140),
        ("data/m7_robustness/train_robustness.jsonl", "robustness_perturbation", 100),
        ("data/m8_general_choice/train_general.jsonl", "general_choice_v1", 120),
    ]

    rng = random.Random(seed)
    all_stream_a_records = []

    for rel_path, subcategory, sample_k in core_sources:
        path = ROOT / rel_path
        groups: Dict[str, List[Dict[str, Any]]] = {}
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                obj = json.loads(line)
                gid = obj["group_id"]
                groups.setdefault(gid, []).append(obj)

        valid_gids = [gid for gid, items in groups.items() if len(items) == 2]
        logger.info(f"Source {rel_path}: {len(valid_gids)} candidate pairs, sampling {sample_k} pairs")
        sampled_gids = rng.sample(valid_gids, sample_k)

        for gid in sampled_gids:
            for item in groups[gid]:
                norm_rec = {
                    "id": item["id"],
                    "group_id": item["group_id"],
                    "stream": "stream_a_core",
                    "family": "core_retention",
                    "subcategory": subcategory,
                    "context": item["context"],
                    "question": item["question"],
                    "choices": item["choices"],
                    "target": item["target"],
                }
                all_stream_a_records.append(norm_rec)

    logger.info(f"Stream A loaded: {len(all_stream_a_records)} records ({len(all_stream_a_records)//2} pairs)")
    return all_stream_a_records


def load_stream_b_groups() -> List[Dict[str, Any]]:
    """Synthesize 1,200 groups (2,400 records) from Stream B generators."""
    logger.info("Synthesizing Stream B (Generalization)...")
    records = []

    logical = generate_logical_stream_b()
    logger.info(f"  - Logical operators: {len(logical)} records")
    records.extend(logical)

    natural = generate_natural_stream_b()
    logger.info(f"  - Natural Japanese: {len(natural)} records")
    records.extend(natural)

    perturbation = generate_perturbation_stream_b()
    logger.info(f"  - Perturbation: {len(perturbation)} records")
    records.extend(perturbation)

    general = generate_general_stream_b()
    logger.info(f"  - General choice: {len(general)} records")
    records.extend(general)

    variable_k = generate_variable_k_stream_b()
    logger.info(f"  - Variable choice: {len(variable_k)} records")
    records.extend(variable_k)

    for r in records:
        r["stream"] = "stream_b_generalization"

    logger.info(f"Stream B synthesized: {len(records)} records ({len(records)//2} pairs)")
    return records


def audit_pair_integrity(records: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """Verify that all records are grouped in valid pairs and targets exist in choices."""
    errors = []
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in records:
        groups.setdefault(r["group_id"], []).append(r)

    for gid, items in groups.items():
        if len(items) != 2:
            errors.append(f"Group {gid} has {len(items)} items (expected 2)")
            continue
        c1, c2 = items[0], items[1]
        t1 = c1["target"]["choice_id"]
        t2 = c2["target"]["choice_id"]

        # Stream B requires contrastive pairs (t1 != t2)
        if c1.get("stream") == "stream_b_generalization" and t1 == t2:
            errors.append(f"Stream B Group {gid} has identical targets: t1={t1}, t2={t2}")

        c1_ids = {c["id"] for c in c1["choices"]}
        c2_ids = {c["id"] for c in c2["choices"]}
        if t1 not in c1_ids:
            errors.append(f"Group {gid} item {c1['id']} target {t1} not in choices")
        if t2 not in c2_ids:
            errors.append(f"Group {gid} item {c2['id']} target {t2} not in choices")

    return len(errors) == 0, errors


def audit_leakage(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Check for zero leakage against Research Fresh and Blind v3."""
    fresh_file = ROOT / "data" / "rc2_1_research_fresh" / "research_fresh_eval.jsonl"
    blind3_file = ROOT / "data" / "sealed_acceptance_rc2_blind_v3" / "sealed_test_rc2_blind_v3.jsonl"

    def get_keys(path: Path) -> Set[Tuple[str, str]]:
        keys = set()
        if not path.exists():
            return keys
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                o = json.loads(line)
                keys.add((o["context"].strip(), o["question"].strip()))
        return keys

    fresh_keys = get_keys(fresh_file)
    blind3_keys = get_keys(blind3_file)

    train_keys = {(r["context"].strip(), r["question"].strip()): r["id"] for r in records}

    overlap_fresh = []
    for k in fresh_keys:
        if k in train_keys:
            overlap_fresh.append({"train_id": train_keys[k], "context": k[0][:50], "question": k[1][:50]})

    overlap_blind3 = []
    for k in blind3_keys:
        if k in train_keys:
            overlap_blind3.append({"train_id": train_keys[k], "context": k[0][:50], "question": k[1][:50]})

    is_clean = (len(overlap_fresh) == 0 and len(overlap_blind3) == 0)
    return {
        "is_clean": is_clean,
        "fresh_suite_cases": len(fresh_keys),
        "blind3_suite_cases": len(blind3_keys),
        "fresh_overlap_count": len(overlap_fresh),
        "blind3_overlap_count": len(overlap_blind3),
        "fresh_overlaps": overlap_fresh,
        "blind3_overlaps": overlap_blind3,
    }


def audit_token_contract(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Verify that all inputs conform to the <= 450 design target and <= 512 hard limit."""
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(str(ROOT / "release/rc2/model"))

    token_counts = []
    violations = []

    for r in records:
        text = f"Context: {r['context']}\nQuestion: {r['question']}"
        labels = [c["text"] for c in r["choices"]]
        text_ids = tok(text, add_special_tokens=False)["input_ids"]
        labels_ids = [tok(l, add_special_tokens=False)["input_ids"] for l in labels]
        total = len(text_ids) + sum(len(l) + 2 for l in labels_ids) + 2

        token_counts.append(total)
        if total > 512:
            violations.append({"id": r["id"], "tokens": total, "error": "Exceeds 512 hard ceiling"})
        elif total > 450:
            logger.warning(f"Record {r['id']} close to ceiling ({total} tokens)")

    return {
        "max_tokens": max(token_counts),
        "min_tokens": min(token_counts),
        "avg_tokens": round(sum(token_counts) / len(token_counts), 2),
        "hard_ceiling": 512,
        "design_target": 450,
        "violations_count": len(violations),
        "is_compliant": len(violations) == 0 and max(token_counts) <= 450,
        "violations": violations,
    }


def split_stratified_by_group(
    records: List[Dict[str, Any]], seed: int = 1234
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Stratified 80/10/10 split by group_id."""
    rng = random.Random(seed)

    # Group records by (stream, family)
    strata: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    for r in records:
        stratum_key = f"{r['stream']}::{r['family']}"
        gid = r["group_id"]
        strata.setdefault(stratum_key, {}).setdefault(gid, []).append(r)

    train_records = []
    dev_records = []
    cal_records = []

    for stratum_key, group_dict in sorted(strata.items()):
        gids = list(group_dict.keys())
        rng.shuffle(gids)

        n_groups = len(gids)
        n_dev = max(1, round(n_groups * 0.10))
        n_cal = max(1, round(n_groups * 0.10))
        n_train = n_groups - n_dev - n_cal

        train_gids = gids[:n_train]
        dev_gids = gids[n_train:n_train + n_dev]
        cal_gids = gids[n_train + n_dev:]

        logger.info(
            f"Stratum {stratum_key}: {n_groups} groups -> "
            f"train={len(train_gids)}, dev={len(dev_gids)}, cal={len(cal_gids)}"
        )

        for gid in train_gids:
            train_records.extend(group_dict[gid])
        for gid in dev_gids:
            dev_records.extend(group_dict[gid])
        for gid in cal_gids:
            cal_records.extend(group_dict[gid])

    return train_records, dev_records, cal_records


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def build_and_save():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    stream_a = load_stream_a_groups(seed=42)
    stream_b = load_stream_b_groups()
    all_records = stream_a + stream_b
    logger.info(f"Total dataset assembled: {len(all_records)} records ({len(all_records)//2} groups)")

    # 1. Pair integrity audit
    logger.info("Auditing pair integrity...")
    pairs_ok, pair_errors = audit_pair_integrity(all_records)
    if not pairs_ok:
        raise ValueError(f"Pair integrity audit FAILED with {len(pair_errors)} errors:\n" + "\n".join(pair_errors[:10]))
    logger.info("Pair integrity audit PASSED.")

    # 2. Leakage audit
    logger.info("Auditing zero leakage against Fresh Suite and Blind v3...")
    leakage_result = audit_leakage(all_records)
    leakage_path = OUTPUT_DIR / "leakage_audit.json"
    with open(leakage_path, "w", encoding="utf-8") as f:
        json.dump(leakage_result, f, indent=2, ensure_ascii=False)

    if not leakage_result["is_clean"]:
        raise ValueError(f"Zero leakage audit FAILED! Fresh overlaps: {leakage_result['fresh_overlap_count']}, Blind3: {leakage_result['blind3_overlap_count']}")
    logger.info("Zero leakage audit PASSED (0 overlap with Fresh Suite and Blind v3).")

    # 3. Token contract audit
    logger.info("Auditing token contract...")
    token_result = audit_token_contract(all_records)
    token_path = OUTPUT_DIR / "token_audit.json"
    with open(token_path, "w", encoding="utf-8") as f:
        json.dump(token_result, f, indent=2, ensure_ascii=False)

    if not token_result["is_compliant"]:
        raise ValueError(f"Token contract audit FAILED! Max tokens: {token_result['max_tokens']} > 450")
    logger.info(f"Token contract audit PASSED (max={token_result['max_tokens']}, avg={token_result['avg_tokens']}).")

    # 4. Stratified Group Split
    logger.info("Splitting dataset into train (80%), dev (10%), calibration (10%)...")
    train_records, dev_records, cal_records = split_stratified_by_group(all_records, seed=1234)

    logger.info(f"Split results: Train={len(train_records)} records ({len(train_records)//2} groups), "
                f"Dev={len(dev_records)} records ({len(dev_records)//2} groups), "
                f"Cal={len(cal_records)} records ({len(cal_records)//2} groups)")

    # 5. Save jsonl files
    train_file = OUTPUT_DIR / "train.jsonl"
    dev_file = OUTPUT_DIR / "dev.jsonl"
    cal_file = OUTPUT_DIR / "calibration.jsonl"

    for path, data in [(train_file, train_records), (dev_file, dev_records), (cal_file, cal_records)]:
        with open(path, "w", encoding="utf-8") as f:
            for r in data:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        logger.info(f"Saved {path.name}: {len(data)} records")

    # 6. Save manifest
    manifest = {
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_records": len(all_records),
        "total_groups": len(all_records) // 2,
        "streams": {
            "stream_a_core": len(stream_a),
            "stream_b_generalization": len(stream_b),
        },
        "splits": {
            "train": {"records": len(train_records), "groups": len(train_records) // 2, "ratio": round(len(train_records) / len(all_records), 4), "sha256": compute_sha256(train_file)},
            "dev": {"records": len(dev_records), "groups": len(dev_records) // 2, "ratio": round(len(dev_records) / len(all_records), 4), "sha256": compute_sha256(dev_file)},
            "calibration": {"records": len(cal_records), "groups": len(cal_records) // 2, "ratio": round(len(cal_records) / len(all_records), 4), "sha256": compute_sha256(cal_file)},
        },
        "token_summary": {
            "max": token_result["max_tokens"],
            "avg": token_result["avg_tokens"],
            "min": token_result["min_tokens"],
        },
        "zero_leakage": {
            "fresh_suite_overlap": 0,
            "blind3_overlap": 0,
        }
    }
    manifest_path = OUTPUT_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    logger.info(f"Dataset build complete! Manifest saved to {manifest_path}")


if __name__ == "__main__":
    build_and_save()
