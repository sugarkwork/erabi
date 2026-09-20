"""Prepare Condition A (Low Diversity), Condition B (Balanced), and Condition C (High Diversity) datasets for Milestone 15.

Roadmap: ERABI_RC2_AUTONOMOUS_RESEARCH_ROADMAP.md (Section 9) & ERABI_M14_1_COMPUTE_CONTROLLED_SCALING_AND_M15_NEXT.md (Sections 15, 16)
Fixed: Total records = 1,138 (Stream A = 356, Stream B = 782) across all 3 conditions.
Condition A (Low Diversity): Concentrated in 6 task families and 3 domains, high repetition.
Condition B (Balanced): Standard proportional 50% fraction from M14.
Condition C (High Diversity): Uniform coverage across all 19 task families and 10 domains, minimal repetition.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import random
from pathlib import Path
from typing import Any, Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.prepare_m15")

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data/rc2_m15_diversity"
DATA_DIR.mkdir(parents=True, exist_ok=True)

POOL_STREAM_A = ROOT / "data/rc2_scaling/train_stream_a_frac_100.jsonl"
POOL_STREAM_B = ROOT / "data/rc2_scaling/train_stream_b_frac_100.jsonl"

EVAL_FILES = [
    ROOT / "data/sealed_acceptance/sealed_test.jsonl",
    ROOT / "data/m8_general_choice/fresh_general_eval.jsonl",
    ROOT / "data/m7_robustness/fresh_robustness_eval.jsonl",
    ROOT / "data/m6_operator/fresh_operator_eval.jsonl",
    ROOT / "data/m3_3_v2/eval_v2.jsonl",
    ROOT / "data/m4_3_1_phrasing_fix/fresh_phrasing_eval.jsonl",
    ROOT / "data/m4_1_exception/eval_exception.jsonl",
    ROOT / "examples/smoke_cases.jsonl",
]

TARGET_STREAM_A = 356
TARGET_STREAM_B = 782
TARGET_TOTAL = TARGET_STREAM_A + TARGET_STREAM_B  # 1,138


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def compute_entropy(counts: Dict[str, int]) -> float:
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return -sum((c / total) * math.log(c / total) for c in counts.values() if c > 0)


def verify_leakage(train_records: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    eval_signatures = set()
    for ef in EVAL_FILES:
        if not ef.exists():
            continue
        for line in open(ef, encoding="utf-8"):
            if not line.strip():
                continue
            r = json.loads(line)
            ctx = r.get("context", "").strip()
            q = r.get("question", "").strip()
            eval_signatures.add((ctx, q))

    leaks = []
    for r in train_records:
        ctx = r.get("context", "").strip()
        q = r.get("question", "").strip()
        if (ctx, q) in eval_signatures:
            leaks.append(f"Leak: '{ctx[:40]}' + '{q[:20]}'")

    return len(leaks) == 0, leaks


def build_condition_a(pool_a: List[Dict[str, Any]], pool_b: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Condition A: Low Diversity / High Repetition.
    Restrict to 3 domains (inventory, support, server) and 6 families.
    In Stream A, restrict to a small group subset.
    """
    rng = random.Random(42)

    # Stream B: Filter to concentrated domains and families
    allowed_domains = {"inventory", "support", "server", "none"}
    allowed_families = {
        "and_logic",
        "or_logic",
        "exception_priority",
        "support_routing",
        "instruction_separation",
        "phrasing_diversification_fix",
    }

    filtered_b = [
        r for r in pool_b
        if r.get("task_family") in allowed_families and r.get("domain", "none") in allowed_domains
    ]
    logger.info(f"Condition A: Eligible Stream B pool = {len(filtered_b)} records")

    # Sample exactly 782 with replacement/repetition if needed, or by repeated cycles
    sampled_b = []
    shuffled_pool = list(filtered_b)
    cycle = 0
    while len(sampled_b) < TARGET_STREAM_B:
        rng.seed(42 + cycle)
        rng.shuffle(shuffled_pool)
        needed = TARGET_STREAM_B - len(sampled_b)
        sampled_b.extend(shuffled_pool[:needed])
        cycle += 1

    # Stream A: Restrict to only 45 groups, highly repeated to reach 356
    groups_a: Dict[str, List[Dict[str, Any]]] = {}
    for r in pool_a:
        groups_a.setdefault(r.get("group_id", "none"), []).append(r)

    sorted_gids = sorted(groups_a.keys())
    rng.seed(100)
    rng.shuffle(sorted_gids)
    selected_gids = sorted_gids[:45]

    concentrated_a = []
    for gid in selected_gids:
        concentrated_a.extend(groups_a[gid])

    sampled_a = []
    cycle_a = 0
    while len(sampled_a) < TARGET_STREAM_A:
        rng.seed(200 + cycle_a)
        rng.shuffle(concentrated_a)
        needed = TARGET_STREAM_A - len(sampled_a)
        sampled_a.extend(concentrated_a[:needed])
        cycle_a += 1

    assert len(sampled_a) == TARGET_STREAM_A
    assert len(sampled_b) == TARGET_STREAM_B
    return sampled_a, sampled_b


def build_condition_b() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Condition B: Balanced 50% fraction from M14."""
    file_a = ROOT / "data/rc2_scaling/train_stream_a_frac_50.jsonl"
    file_b = ROOT / "data/rc2_scaling/train_stream_b_frac_50.jsonl"
    sampled_a = [json.loads(l) for l in open(file_a, encoding="utf-8") if l.strip()]
    sampled_b = [json.loads(l) for l in open(file_b, encoding="utf-8") if l.strip()]
    assert len(sampled_a) == TARGET_STREAM_A
    assert len(sampled_b) == TARGET_STREAM_B
    return sampled_a, sampled_b


def build_condition_c(pool_a: List[Dict[str, Any]], pool_b: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Condition C: High Diversity / Wide Coverage.
    Uniform allocation across ALL 19 task families and ALL 10 domains without replacement.
    Maximize unique group IDs in Stream A (300 distinct groups).
    """
    rng = random.Random(42)

    # Stream B: Group by (task_family, domain)
    strata: Dict[str, List[Dict[str, Any]]] = {}
    for r in pool_b:
        fam = r.get("task_family", "none")
        dom = r.get("domain", "none")
        k = f"{fam}::{dom}"
        strata.setdefault(k, []).append(r)

    # Round-robin sampling across all strata WITHOUT replacement to achieve maximal entropy & uniqueness
    sampled_b = []
    strata_keys = sorted(strata.keys())
    shuffled_strata = {k: list(v) for k, v in strata.items()}
    for k in strata_keys:
        rng.seed(hash(k) % 100000)
        rng.shuffle(shuffled_strata[k])

    while len(sampled_b) < TARGET_STREAM_B:
        remaining_keys = [k for k in strata_keys if len(shuffled_strata[k]) > 0]
        if not remaining_keys:
            break
        for k in remaining_keys:
            if len(sampled_b) >= TARGET_STREAM_B:
                break
            sampled_b.append(shuffled_strata[k].pop(0))

    # Stream A: Draw 1 example from all 300 distinct groups, then fill remainder to reach 356
    groups_a: Dict[str, List[Dict[str, Any]]] = {}
    for r in pool_a:
        groups_a.setdefault(r.get("group_id", "none"), []).append(r)

    sorted_gids = sorted(groups_a.keys())
    rng.seed(300)
    rng.shuffle(sorted_gids)

    sampled_a = []
    for gid in sorted_gids:
        sampled_a.append(groups_a[gid][0])

    extra_gids = [gid for gid in sorted_gids if len(groups_a[gid]) > 1]
    rng.shuffle(extra_gids)
    for gid in extra_gids:
        if len(sampled_a) >= TARGET_STREAM_A:
            break
        sampled_a.append(groups_a[gid][1])

    assert len(sampled_a) == TARGET_STREAM_A
    assert len(sampled_b) == TARGET_STREAM_B
    return sampled_a, sampled_b


def profile_diversity(stream_a: List[Dict[str, Any]], stream_b: List[Dict[str, Any]]) -> Dict[str, Any]:
    all_recs = stream_a + stream_b
    fam_counts: Dict[str, int] = {}
    dom_counts: Dict[str, int] = {}
    gids_a = set(r.get("group_id") for r in stream_a if r.get("group_id"))

    for r in stream_b:
        fam = r.get("task_family", "none")
        dom = r.get("domain", "none")
        fam_counts[fam] = fam_counts.get(fam, 0) + 1
        dom_counts[dom] = dom_counts.get(dom, 0) + 1

    # Unique text inputs (context + question)
    unique_contexts = len(set(r["context"] for r in all_recs))
    unique_inputs = len(set((r["context"], r["question"]) for r in all_recs))

    return {
        "total_records": len(all_recs),
        "stream_a_records": len(stream_a),
        "stream_b_records": len(stream_b),
        "distinct_task_families": len(fam_counts),
        "distinct_domains": len(dom_counts),
        "distinct_stream_a_groups": len(gids_a),
        "task_family_entropy": compute_entropy(fam_counts),
        "domain_entropy": compute_entropy(dom_counts),
        "unique_contexts": unique_contexts,
        "unique_inputs": unique_inputs,
        "family_distribution": fam_counts,
        "domain_distribution": dom_counts,
    }


def main():
    logger.info("=== Preparing Milestone 15 Quantity vs Diversity Datasets ===")
    pool_a = [json.loads(l) for l in open(POOL_STREAM_A, encoding="utf-8") if l.strip()]
    pool_b = [json.loads(l) for l in open(POOL_STREAM_B, encoding="utf-8") if l.strip()]

    conditions = {}

    # 1. Condition A (Low Diversity)
    logger.info("Building Condition A (Low Diversity)...")
    a_stream_a, a_stream_b = build_condition_a(pool_a, pool_b)
    prof_a = profile_diversity(a_stream_a, a_stream_b)
    conditions["cond_a_low"] = {
        "name": "Condition A (Low Diversity / High Repetition)",
        "stream_a": a_stream_a,
        "stream_b": a_stream_b,
        "profile": prof_a,
    }

    # 2. Condition B (Balanced)
    logger.info("Building Condition B (Balanced)...")
    b_stream_a, b_stream_b = build_condition_b()
    prof_b = profile_diversity(b_stream_a, b_stream_b)
    conditions["cond_b_balanced"] = {
        "name": "Condition B (Balanced / Standard Proportional)",
        "stream_a": b_stream_a,
        "stream_b": b_stream_b,
        "profile": prof_b,
    }

    # 3. Condition C (High Diversity)
    logger.info("Building Condition C (High Diversity)...")
    c_stream_a, c_stream_b = build_condition_c(pool_a, pool_b)
    prof_c = profile_diversity(c_stream_a, c_stream_b)
    conditions["cond_c_high"] = {
        "name": "Condition C (High Diversity / Wide Coverage)",
        "stream_a": c_stream_a,
        "stream_b": c_stream_b,
        "profile": prof_c,
    }

    manifest = {
        "milestone": "Milestone 15 Quantity vs Diversity",
        "fixed_sample_size": TARGET_TOTAL,
        "conditions": {},
    }

    for ckey, cdata in conditions.items():
        all_recs = cdata["stream_a"] + cdata["stream_b"]
        leak_free, leaks = verify_leakage(all_recs)
        if not leak_free:
            raise RuntimeError(f"Leakage detected in {ckey}: {leaks[:3]}")

        file_a = DATA_DIR / f"{ckey}_stream_a.jsonl"
        file_b = DATA_DIR / f"{ckey}_stream_b.jsonl"
        file_comb = DATA_DIR / f"{ckey}_combined.jsonl"

        with open(file_a, "w", encoding="utf-8") as f:
            for r in cdata["stream_a"]:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        with open(file_b, "w", encoding="utf-8") as f:
            for r in cdata["stream_b"]:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        with open(file_comb, "w", encoding="utf-8") as f:
            for r in all_recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        prof = cdata["profile"]
        logger.info(
            f"[{ckey}] Records={prof['total_records']}, Families={prof['distinct_task_families']} "
            f"(Entropy: {prof['task_family_entropy']:.2f}), Domains={prof['distinct_domains']} "
            f"(Entropy: {prof['domain_entropy']:.2f}), Groups A={prof['distinct_stream_a_groups']}, "
            f"Unique Inputs={prof['unique_inputs']}"
        )

        manifest["conditions"][ckey] = {
            "name": cdata["name"],
            "profile": prof,
            "stream_a_file": str(file_a.relative_to(ROOT)),
            "stream_b_file": str(file_b.relative_to(ROOT)),
            "combined_file": str(file_comb.relative_to(ROOT)),
            "sha256": sha256_file(file_comb),
        }

    manifest_path = DATA_DIR / "diversity_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    logger.info(f"\nManifest successfully created at {manifest_path}")


if __name__ == "__main__":
    main()
