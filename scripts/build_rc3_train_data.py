"""Build RC3 Training Dataset: Stream A (Core Retention) + Stream B (RC3 Diversity & Hard Negatives).

Assembles:
- Stream A: 510 groups (1,020 records) from clean historical core training sets
- Stream B: 2,000 groups (4,000 records) synthesized by fresh RC3 generators:
  - Logical Operators & Propositional Reasoning (300 groups)
  - Lexical Overlap Hard Negatives (300 groups)
  - Priority Exceptions & Overrides (300 groups)
  - Variable Cardinality K=4..16 (300 groups)
  - Natural Japanese Concessive Phrasing (300 groups)
  - General Choice Tasks (300 groups)
  - Perturbation Invariance & Robustness (200 groups)
Total: 2,510 groups (5,020 records)

Performs:
1. Pair integrity audit (2 distinct targets per group in Stream B, targets valid in choices)
2. Token length contract audit (<= 450 design target, <= 512 hard ceiling)
3. Zero-leakage audit against:
   - RC3 Bridge Benchmark (data/rc3_bridge/rc3_bridge_benchmark.jsonl)
   - Blind v4 (data/rc2_blind_v4/blind_v4_evaluation.jsonl)
   - Blind v3 (data/sealed_acceptance_rc2_blind_v3/sealed_test_rc2_blind_v3.jsonl)
   - Core historical eval suites
4. Stratified group-based split:
   - Train: 80% (2,008 groups = 4,016 records)
   - Dev: 10% (251 groups = 502 records)
   - Calibration: 10% (251 groups = 502 records)
5. Saves artifacts to data/rc3_train/
"""

from __future__ import annotations

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

from scripts.rc3_train_data.generate_rc3_logical import generate_rc3_logical
from scripts.rc3_train_data.generate_rc3_truth_tables import generate_rc3_truth_tables
from scripts.rc3_train_data.generate_rc3_lexical_overlap import generate_rc3_lexical_overlap
from scripts.rc3_train_data.generate_rc3_priority import generate_rc3_priority
from scripts.rc3_train_data.generate_rc3_variable_k import generate_rc3_variable_k
from scripts.rc3_train_data.generate_rc3_natural import generate_rc3_natural
from scripts.rc3_train_data.generate_rc3_general import generate_rc3_general
from scripts.rc3_train_data.generate_rc3_perturbation import generate_rc3_perturbation
from scripts.rc3_train_data.generate_rc3_technical_specs import generate_rc3_technical_specs

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("build_rc3_train_data")

OUTPUT_DIR = ROOT / "data" / "rc3_train"


def load_stream_a_core(seed: int = 42) -> List[Dict[str, Any]]:
    """Load the full proven RC2.1 training foundation (5,610 records = 2,805 pairs)."""
    logger.info("Loading Stream A from data/rc2_1_train/train.jsonl...")
    path = ROOT / "data" / "rc2_1_train" / "train.jsonl"
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            records.append(json.loads(line))

    logger.info(f"Stream A loaded: {len(records)} records ({len(records)//2} pairs)")
    return records


def load_stream_b_rc3() -> List[Dict[str, Any]]:
    """Synthesize 2,300 groups (4,600 records) from RC3 generators."""
    logger.info("Synthesizing Stream B (RC3 Generalization & Hard Negatives)...")
    records = []

    logical = generate_rc3_logical()
    logger.info(f"  - Logical operators: {len(logical)} records")
    records.extend(logical)

    truth_tables = generate_rc3_truth_tables()
    logger.info(f"  - Truth table operators: {len(truth_tables)} records")
    records.extend(truth_tables)

    lexical = generate_rc3_lexical_overlap()
    logger.info(f"  - Lexical overlap resistance: {len(lexical)} records")
    records.extend(lexical)

    priority = generate_rc3_priority()
    logger.info(f"  - Priority exceptions: {len(priority)} records")
    records.extend(priority)

    variable_k = generate_rc3_variable_k()
    logger.info(f"  - Variable K cardinality: {len(variable_k)} records")
    records.extend(variable_k)

    natural = generate_rc3_natural()
    logger.info(f"  - Natural Japanese phrasing: {len(natural)} records")
    records.extend(natural)

    general = generate_rc3_general()
    logger.info(f"  - General choice: {len(general)} records")
    records.extend(general)

    perturbation = generate_rc3_perturbation()
    logger.info(f"  - Perturbation invariance: {len(perturbation)} records")
    records.extend(perturbation)

    technical_specs = generate_rc3_technical_specs()
    logger.info(f"  - Technical specification thresholds: {len(technical_specs)} records")
    records.extend(technical_specs)

    for r in records:
        r["stream"] = "stream_b_generalization"

    logger.info(f"Stream B synthesized: {len(records)} records ({len(records)//2} pairs)")
    return records


def audit_pair_integrity(records: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """Verify group structure, choice validity, and contrastive targets."""
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
    """Check for ZERO leakage against Bridge Benchmark, Blind v4, Blind v3, and Core eval suites."""
    target_files = {
        "rc3_bridge": ROOT / "data" / "rc3_bridge" / "rc3_bridge_benchmark.jsonl",
        "rc2_blind_v4": ROOT / "data" / "rc2_blind_v4" / "blind_v4_evaluation.jsonl",
        "rc2_blind_v3": ROOT / "data" / "sealed_acceptance_rc2_blind_v3" / "sealed_test_rc2_blind_v3.jsonl",
        "eval_v2": ROOT / "data" / "m3_3_v2" / "eval_v2.jsonl",
        "eval_exception": ROOT / "data" / "m4_1_exception" / "eval_exception.jsonl",
        "fresh_operator": ROOT / "data" / "m6_operator" / "fresh_operator_eval.jsonl",
        "fresh_robustness": ROOT / "data" / "m7_robustness" / "fresh_robustness_eval.jsonl",
        "fresh_general": ROOT / "data" / "m8_general_choice" / "fresh_general_eval.jsonl",
    }

    train_fingerprints: Set[str] = set()
    for r in records:
        ctx = r.get("context", "").strip()
        q = r.get("question", "").strip()
        fp = f"{ctx} ||| {q}"
        train_fingerprints.add(fp)

    overlaps_by_source: Dict[str, int] = {}
    is_clean = True

    for name, path in target_files.items():
        if not path.exists():
            continue
        count = 0
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                o = json.loads(line)
                fp = f"{o.get('context', '').strip()} ||| {o.get('question', '').strip()}"
                if fp in train_fingerprints:
                    count += 1
        overlaps_by_source[name] = count
        if count > 0:
            is_clean = False
            logger.error(f"Leakage detected against {name}: {count} exact matches!")

    return {
        "is_clean": is_clean,
        "overlaps_by_source": overlaps_by_source,
        "total_sources_audited": len(target_files),
    }


def audit_token_contract(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Verify that all inputs conform to the <= 450 design target and <= 512 hard ceiling."""
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(str(ROOT / "release/rc2_1/model"))

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
            violations.append({"id": r["id"], "tokens": total, "error": "Exceeds 450 design target"})

    return {
        "max_tokens": max(token_counts),
        "min_tokens": min(token_counts),
        "avg_tokens": round(sum(token_counts) / len(token_counts), 2),
        "hard_ceiling": 512,
        "design_target": 450,
        "violations_count": len(violations),
        "is_compliant": len(violations) == 0,
        "violations": violations[:10],
    }


def split_stratified_by_group(
    records: List[Dict[str, Any]], seed: int = 1234
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Stratified 80/10/10 split by group_id across (stream, family)."""
    rng = random.Random(seed)

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

    stream_a = load_stream_a_core(seed=42)
    stream_b = load_stream_b_rc3()
    all_records = stream_a + stream_b
    logger.info(f"Total dataset assembled: {len(all_records)} records ({len(all_records)//2} groups)")

    # 1. Pair integrity audit
    logger.info("Auditing pair integrity...")
    pairs_ok, pair_errors = audit_pair_integrity(all_records)
    audit_pair_path = OUTPUT_DIR / "pair_integrity_audit.json"
    with open(audit_pair_path, "w", encoding="utf-8") as f:
        json.dump({"pairs_ok": pairs_ok, "error_count": len(pair_errors), "errors": pair_errors[:20]}, f, indent=2, ensure_ascii=False)
    if not pairs_ok:
        raise ValueError(f"Pair integrity audit FAILED with {len(pair_errors)} errors:\n" + "\n".join(pair_errors[:10]))
    logger.info("Pair integrity audit PASSED.")

    # 2. Leakage audit
    logger.info("Auditing zero leakage against Bridge, Blind v4, Blind v3, and Core suites...")
    leakage_result = audit_leakage(all_records)
    leakage_path = OUTPUT_DIR / "leakage_audit.json"
    with open(leakage_path, "w", encoding="utf-8") as f:
        json.dump(leakage_result, f, indent=2, ensure_ascii=False)
    if not leakage_result["is_clean"]:
        raise ValueError(f"Zero leakage audit FAILED! Overlaps: {leakage_result['overlaps_by_source']}")
    logger.info(f"Zero leakage audit PASSED: {leakage_result['overlaps_by_source']}")

    # 3. Token contract audit
    logger.info("Auditing token length contract (<= 450 target, <= 512 ceiling)...")
    token_result = audit_token_contract(all_records)
    token_path = OUTPUT_DIR / "token_audit.json"
    with open(token_path, "w", encoding="utf-8") as f:
        json.dump(token_result, f, indent=2, ensure_ascii=False)
    if not token_result["is_compliant"]:
        raise ValueError(f"Token contract audit FAILED! Max tokens: {token_result['max_tokens']} > 450")
    logger.info(f"Token contract audit PASSED (max={token_result['max_tokens']}, avg={token_result['avg_tokens']}, min={token_result['min_tokens']}).")

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
            "train": {
                "records": len(train_records),
                "groups": len(train_records) // 2,
                "ratio": round(len(train_records) / len(all_records), 4),
                "sha256": compute_sha256(train_file),
            },
            "dev": {
                "records": len(dev_records),
                "groups": len(dev_records) // 2,
                "ratio": round(len(dev_records) / len(all_records), 4),
                "sha256": compute_sha256(dev_file),
            },
            "calibration": {
                "records": len(cal_records),
                "groups": len(cal_records) // 2,
                "ratio": round(len(cal_records) / len(all_records), 4),
                "sha256": compute_sha256(cal_file),
            },
        },
        "token_summary": {
            "max": token_result["max_tokens"],
            "avg": token_result["avg_tokens"],
            "min": token_result["min_tokens"],
        },
        "zero_leakage": leakage_result["overlaps_by_source"],
    }
    manifest_path = OUTPUT_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    logger.info(f"=== RC3 Training Dataset Assembly Complete! Manifest: {manifest_path} ===")


if __name__ == "__main__":
    build_and_save()
