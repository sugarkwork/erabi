"""Prepare stratified, nested datasets for Milestone 14 Data Scaling Law.

Fractions: 12.5%, 25%, 50%, 75%, 100%
Sampling: Stratified by task family, source component, domain, operator, and target.
Nested: S_12.5% <= S_25% <= S_50% <= S_75% <= S_100%
Zero-leakage: Audited against all dev and fresh evaluation suites.
"""

from __future__ import annotations

import hashlib
import json
import logging
import random
from pathlib import Path
from typing import Any, Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.prepare_scaling")

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data/rc2_scaling"
DATA_DIR.mkdir(parents=True, exist_ok=True)

M3_TRAIN_FILE = ROOT / "data/m3_3_v2/train.jsonl"
M4_1_TRAIN_FILE = ROOT / "data/m4_1_exception/train_exception.jsonl"
M4_3_1_TRAIN_FILE = ROOT / "data/m4_3_1_phrasing_fix/phrasing_train.jsonl"
M6_TRAIN_FILE = ROOT / "data/m6_operator/train_operator.jsonl"
M7_TRAIN_FILE = ROOT / "data/m7_robustness/train_robustness.jsonl"
M8_TRAIN_FILE = ROOT / "data/m8_general_choice/train_general.jsonl"
AUDIT_FILE = ROOT / "runs/m4_4_1_retention/retention_source_audit.json"

EVAL_FILES = [
    ROOT / "data/sealed_acceptance/sealed_test.jsonl",
    ROOT / "data/m8_general_choice/fresh_general_eval.jsonl",
    ROOT / "data/m7_robustness/fresh_robustness_eval.jsonl",
    ROOT / "data/m6_operator/fresh_operator_eval.jsonl",
    ROOT / "data/m3_3_v2/eval_v2.jsonl",
    ROOT / "data/m4_3_1_phrasing_fix/fresh_phrasing_eval.jsonl",
    ROOT / "data/m4_1_exception/eval_exception.jsonl",
    ROOT / "examples/smoke_cases.jsonl",
    ROOT / "data/m8_general_choice/dev_general.jsonl",
]

FRACTIONS = [0.125, 0.25, 0.50, 0.75, 1.0]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def load_raw_components() -> Dict[str, List[Dict[str, Any]]]:
    m3_train = [json.loads(l) for l in open(M3_TRAIN_FILE, encoding="utf-8") if l.strip()]
    audit = json.load(open(AUDIT_FILE, encoding="utf-8"))
    r1_gids = set(audit["r1_equality_boundary"]["group_ids"])
    r1b_gids = set(audit["r1b_equality_comparison"]["group_ids"])
    r2_gids = set()
    for st_info in audit["r2_composite_logic"]["states"].values():
        r2_gids.update(st_info["selected_group_ids"])
    replay_gids = r1_gids | r1b_gids | r2_gids
    replay_records = [r for r in m3_train if r["group_id"] in replay_gids]

    m4_1_train = [json.loads(l) for l in open(M4_1_TRAIN_FILE, encoding="utf-8") if l.strip()]
    m4_3_1_train = [json.loads(l) for l in open(M4_3_1_TRAIN_FILE, encoding="utf-8") if l.strip()]
    m6_op_train = [json.loads(l) for l in open(M6_TRAIN_FILE, encoding="utf-8") if l.strip()]
    m7_rob_train = [json.loads(l) for l in open(M7_TRAIN_FILE, encoding="utf-8") if l.strip()]
    m8_gen_train = [json.loads(l) for l in open(M8_TRAIN_FILE, encoding="utf-8") if l.strip()]

    return {
        "m3_train": m3_train,
        "m3_replay": replay_records,
        "m4_1_exception": m4_1_train,
        "m4_3_1_phrasing": m4_3_1_train,
        "m6_operator": m6_op_train,
        "m7_robustness": m7_rob_train,
        "m8_general": m8_gen_train,
    }


def get_strat_key(r: Dict[str, Any], comp_name: str) -> str:
    fam = r.get("task_family", "none")
    tgt = r.get("target", {}).get("choice_id", r.get("target", "none")) if isinstance(r.get("target"), dict) else r.get("target", "none")
    dom = r.get("domain", "none")
    op = r.get("operator", "none")
    n_ch = len(r.get("choices", []))
    return f"{comp_name}::{fam}::{op}::{dom}::{tgt}::{n_ch}"


def build_nested_rankings(components: Dict[str, List[Dict[str, Any]]], seed: int = 42) -> Dict[str, List[Dict[str, Any]]]:
    """Sort and assign a deterministic normalized rank to each record within its stratum."""
    rng = random.Random(seed)
    ranked_components = {}

    for cname, records in components.items():
        # Group by stratum
        strata: Dict[str, List[Dict[str, Any]]] = {}
        for r in records:
            k = get_strat_key(r, cname)
            strata.setdefault(k, []).append(r)

        # Shuffle each stratum deterministically
        ranked_list = []
        for k in sorted(strata.keys()):
            s_recs = list(strata[k])
            rng.shuffle(s_recs)
            for i, r in enumerate(s_recs):
                # Normalized percentile within stratum
                pct = (i + 0.5) / len(s_recs)
                ranked_list.append((pct, r))

        # Sort by percentile so taking the first int(len * frac) gives uniform stratified representation
        ranked_list.sort(key=lambda x: x[0])
        ranked_components[cname] = [r for _, r in ranked_list]

    return ranked_components


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


def main():
    logger.info("=== Preparing Milestone 14 Scaling Law Datasets ===")
    components = load_raw_components()

    for cname, recs in components.items():
        logger.info(f"Loaded component '{cname}': {len(recs)} records")

    ranked = build_nested_rankings(components, seed=42)

    manifest = {
        "milestone": "Milestone 14 Data Scaling Law",
        "fractions": {},
    }

    fraction_records: Dict[float, Dict[str, List[Dict[str, Any]]]] = {}

    for frac in FRACTIONS:
        pct_label = f"{frac * 100:g}"
        logger.info(f"\nProcessing fraction {frac:.3f} ({pct_label}%)...")

        frac_stream_a = []
        frac_stream_b = []

        comp_counts = {}
        for cname, recs in ranked.items():
            n_sample = max(1, int(round(len(recs) * frac))) if frac < 1.0 else len(recs)
            sampled = recs[:n_sample]
            comp_counts[cname] = len(sampled)
            if cname in ["m3_train", "m3_replay"]:
                frac_stream_a.extend(sampled)
            else:
                frac_stream_b.extend(sampled)

        total_records = len(frac_stream_a) + len(frac_stream_b)
        logger.info(
            f"Fraction {pct_label}%: Stream A = {len(frac_stream_a)}, Stream B = {len(frac_stream_b)}, "
            f"Total = {total_records}"
        )

        # Leakage check
        all_train = frac_stream_a + frac_stream_b
        leak_free, leaks = verify_leakage(all_train)
        if not leak_free:
            raise RuntimeError(f"Leakage detected in fraction {pct_label}%: {leaks[:3]}")

        # Save files
        stream_a_path = DATA_DIR / f"train_stream_a_frac_{pct_label}.jsonl"
        stream_b_path = DATA_DIR / f"train_stream_b_frac_{pct_label}.jsonl"
        combined_path = DATA_DIR / f"train_combined_frac_{pct_label}.jsonl"

        with open(stream_a_path, "w", encoding="utf-8") as f:
            for r in frac_stream_a:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        with open(stream_b_path, "w", encoding="utf-8") as f:
            for r in frac_stream_b:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        with open(combined_path, "w", encoding="utf-8") as f:
            for r in all_train:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        fraction_records[frac] = {
            "stream_a": frac_stream_a,
            "stream_b": frac_stream_b,
        }

        manifest["fractions"][pct_label] = {
            "fraction": frac,
            "total_records": total_records,
            "stream_a_records": len(frac_stream_a),
            "stream_b_records": len(frac_stream_b),
            "component_counts": comp_counts,
            "stream_a_file": str(stream_a_path.relative_to(ROOT)),
            "stream_b_file": str(stream_b_path.relative_to(ROOT)),
            "combined_file": str(combined_path.relative_to(ROOT)),
            "sha256": sha256_file(combined_path),
        }

    # Verify nested property: S_12.5 <= S_25 <= S_50 <= S_75 <= S_100
    logger.info("\nVerifying Nested Subset Property (S_i subseteq S_j)...")
    frac_keys = FRACTIONS
    for i in range(len(frac_keys) - 1):
        f_low = frac_keys[i]
        f_high = frac_keys[i + 1]
        recs_low = set(json.dumps(r, sort_keys=True) for r in fraction_records[f_low]["stream_a"] + fraction_records[f_low]["stream_b"])
        recs_high = set(json.dumps(r, sort_keys=True) for r in fraction_records[f_high]["stream_a"] + fraction_records[f_high]["stream_b"])
        is_sub = recs_low.issubset(recs_high)
        logger.info(f"Subset check: {f_low*100}% subset of {f_high*100}% -> {'VALID' if is_sub else 'VIOLATION'}")
        assert is_sub, f"Nested property violated between {f_low} and {f_high}"

    manifest_path = DATA_DIR / "scaling_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    logger.info(f"\nManifest successfully created at {manifest_path}")


if __name__ == "__main__":
    main()
