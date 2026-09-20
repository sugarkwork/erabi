"""Prepare Single-Axis Ablation Datasets for Milestone 16 — Diversity Attribution.

Roadmap: ERABI_RC2_AUTONOMOUS_RESEARCH_ROADMAP.md (Section 10)
Baseline: Condition B (Balanced, N = 1,138: Stream A = 356, Stream B = 782).
Fixed: Total records = 1,138 across all ablation conditions.
Ablations:
1. abl_no_phrasing: Phrasing diversity removed (120 phrasing records collapsed to single canonical template).
2. abl_no_domain: Domain diversity removed (162 domain perturbation records & domain labels collapsed to domain="none").
3. abl_no_operator: Operator diversity removed (200 operator records replaced by basic rule lookups).
4. abl_no_group: Core group / numerical state diversity removed (Stream A restricted to only 15 groups, heavily repeated to reach 356).
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
import math
import random
from pathlib import Path
from typing import Any, Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.prepare_m16")

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data/rc2_m16_ablation"
DATA_DIR.mkdir(parents=True, exist_ok=True)

BASE_STREAM_A = ROOT / "data/rc2_m15_diversity/cond_b_balanced_stream_a.jsonl"
BASE_STREAM_B = ROOT / "data/rc2_m15_diversity/cond_b_balanced_stream_b.jsonl"

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
TARGET_TOTAL = 1138


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


def build_no_phrasing(stream_a: List[Dict[str, Any]], stream_b: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Ablate Phrasing Diversity:
    Replace diverse phrasing variations with a single rigid canonical formulation.
    """
    new_b = []
    # Identify canonical phrasing template from exception_priority or standard phrasing
    canonical_q = "①【最優先】と②【次点】の指示に従い、適切な対応を選択してください。"
    
    for r in stream_b:
        r_copy = copy.deepcopy(r)
        if r_copy.get("task_family") == "phrasing_diversification_fix":
            # Collapse diverse question templates to the canonical formulation
            r_copy["question"] = canonical_q
            r_copy["phrasing_family"] = "canonical_ablated"
        new_b.append(r_copy)

    assert len(stream_a) == TARGET_STREAM_A
    assert len(new_b) == TARGET_STREAM_B
    return list(stream_a), new_b


def build_no_domain(stream_a: List[Dict[str, Any]], stream_b: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Ablate Domain Diversity:
    Collapse domain variations and domain perturbations down to generic/domain='none'.
    """
    new_b = []
    for r in stream_b:
        r_copy = copy.deepcopy(r)
        # Remove domain tag and strip domain-specific vocabulary markers if in robustness
        if r_copy.get("task_family") == "domain_perturbation_robustness":
            r_copy["domain"] = "none"
            r_copy["task_family"] = "domain_neutralized"
        else:
            r_copy["domain"] = "none"
        new_b.append(r_copy)

    assert len(stream_a) == TARGET_STREAM_A
    assert len(new_b) == TARGET_STREAM_B
    return list(stream_a), new_b


def build_no_operator(stream_a: List[Dict[str, Any]], stream_b: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Ablate Operator Diversity:
    Replace complex operator logic (and, or, comparisons, overrides) with simple direct lookups.
    """
    operator_families = {
        "and_logic", "or_logic", "ge_vs_gt", "le_vs_lt", "negation",
        "override", "priority_ranking", "first_match", "default_exception", "goal_switching"
    }

    # Find replacement simple cases from support_routing or intent_selection
    simple_cases = [r for r in stream_b if r.get("task_family") in {"support_routing", "intent_selection", "short_nli"}]
    rng = random.Random(42)
    rng.shuffle(simple_cases)

    new_b = []
    simple_idx = 0
    for r in stream_b:
        if r.get("task_family") in operator_families:
            # Replace with simple case
            rep = copy.deepcopy(simple_cases[simple_idx % len(simple_cases)])
            rep["id"] = f"{rep['id']}_rep_{simple_idx}"
            new_b.append(rep)
            simple_idx += 1
        else:
            new_b.append(copy.deepcopy(r))

    assert len(stream_a) == TARGET_STREAM_A
    assert len(new_b) == TARGET_STREAM_B
    return list(stream_a), new_b


def build_no_group(stream_a: List[Dict[str, Any]], stream_b: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Ablate Group / Numerical State Diversity in Stream A:
    Restrict Stream A from 243 groups down to only 15 groups, heavily repeated.
    """
    groups_a: Dict[str, List[Dict[str, Any]]] = {}
    for r in stream_a:
        groups_a.setdefault(r.get("group_id", "none"), []).append(r)

    sorted_gids = sorted(groups_a.keys())
    rng = random.Random(42)
    rng.shuffle(sorted_gids)
    selected_15 = sorted_gids[:15]

    pool_15 = []
    for gid in selected_15:
        pool_15.extend(groups_a[gid])

    new_a = []
    cycle = 0
    while len(new_a) < TARGET_STREAM_A:
        rng.seed(100 + cycle)
        shuffled = list(pool_15)
        rng.shuffle(shuffled)
        needed = TARGET_STREAM_A - len(new_a)
        new_a.extend(shuffled[:needed])
        cycle += 1

    assert len(new_a) == TARGET_STREAM_A
    assert len(stream_b) == TARGET_STREAM_B
    return new_a, list(stream_b)


def profile_dataset(stream_a: List[Dict[str, Any]], stream_b: List[Dict[str, Any]]) -> Dict[str, Any]:
    all_recs = stream_a + stream_b
    fam_counts: Dict[str, int] = {}
    dom_counts: Dict[str, int] = {}
    gids_a = set(r.get("group_id") for r in stream_a if r.get("group_id"))

    for r in stream_b:
        fam = r.get("task_family", "none")
        dom = r.get("domain", "none")
        fam_counts[fam] = fam_counts.get(fam, 0) + 1
        dom_counts[dom] = dom_counts.get(dom, 0) + 1

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
    }


def main():
    logger.info("=== Preparing Milestone 16 Diversity Attribution Datasets ===")
    stream_a = [json.loads(l) for l in open(BASE_STREAM_A, encoding="utf-8") if l.strip()]
    stream_b = [json.loads(l) for l in open(BASE_STREAM_B, encoding="utf-8") if l.strip()]

    ablations = {
        "abl_no_phrasing": {
            "name": "Ablation 1: No Phrasing Diversity",
            "desc": "Diverse phrasing templates collapsed to single canonical template.",
            "builder": lambda: build_no_phrasing(stream_a, stream_b),
        },
        "abl_no_domain": {
            "name": "Ablation 2: No Domain Diversity",
            "desc": "Domain diversity and perturbations collapsed to generic domain='none'.",
            "builder": lambda: build_no_domain(stream_a, stream_b),
        },
        "abl_no_operator": {
            "name": "Ablation 3: No Operator Diversity",
            "desc": "Operator logic families (and, or, comparisons, overrides) replaced by simple lookups.",
            "builder": lambda: build_no_operator(stream_a, stream_b),
        },
        "abl_no_group": {
            "name": "Ablation 4: No Group / Numerical State Diversity",
            "desc": "Stream A group coverage restricted from 243 groups to 15 groups.",
            "builder": lambda: build_no_group(stream_a, stream_b),
        },
    }

    manifest = {
        "milestone": "Milestone 16 Diversity Attribution",
        "baseline_condition": "cond_b_balanced",
        "fixed_sample_size": TARGET_TOTAL,
        "baseline_profile": profile_dataset(stream_a, stream_b),
        "ablations": {},
    }

    for akey, adata in ablations.items():
        logger.info(f"Building {akey} ({adata['name']})...")
        sa, sb = adata["builder"]()
        all_recs = sa + sb

        leak_free, leaks = verify_leakage(all_recs)
        if not leak_free:
            raise RuntimeError(f"Leak detected in {akey}: {leaks[:3]}")

        file_a = DATA_DIR / f"{akey}_stream_a.jsonl"
        file_b = DATA_DIR / f"{akey}_stream_b.jsonl"
        file_comb = DATA_DIR / f"{akey}_combined.jsonl"

        with open(file_a, "w", encoding="utf-8") as f:
            for r in sa:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        with open(file_b, "w", encoding="utf-8") as f:
            for r in sb:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        with open(file_comb, "w", encoding="utf-8") as f:
            for r in all_recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        prof = profile_dataset(sa, sb)
        logger.info(
            f"  [{akey}] Records={prof['total_records']}, Families={prof['distinct_task_families']} "
            f"(Entropy: {prof['task_family_entropy']:.2f}), Domains={prof['distinct_domains']} "
            f"(Entropy: {prof['domain_entropy']:.2f}), Groups A={prof['distinct_stream_a_groups']}, "
            f"Unique Inputs={prof['unique_inputs']}"
        )

        manifest["ablations"][akey] = {
            "name": adata["name"],
            "description": adata["desc"],
            "profile": prof,
            "stream_a_file": str(file_a.relative_to(ROOT)),
            "stream_b_file": str(file_b.relative_to(ROOT)),
            "combined_file": str(file_comb.relative_to(ROOT)),
            "sha256": sha256_file(file_comb),
        }

    manifest_path = DATA_DIR / "ablation_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    logger.info(f"\nManifest successfully created at {manifest_path}")


if __name__ == "__main__":
    main()
