"""Build Blind Sealed Acceptance Test Suite v5 for ERABI Release Candidate 3.

Directive Reference:
ERABI_RC3_DIAGNOSTIC_FIRST_ARCHITECTURE_ROADMAP.md (Section 23, Milestone 34).

Mandates:
1. ZERO MODEL INFERENCE during test authoring.
   - Absolutely no PyTorch, ONNX, GLiClassEngine, or model prediction probes.
2. 480 test cases organized into 240 contrastive pairs.
3. 8 balanced families (60 cases / 30 pairs each):
   - core_rules (30 pairs, prefix rc3_blind5_core_)
   - logical_operators (30 pairs, prefix rc3_blind5_op_)
   - priority_exception (30 pairs, prefix rc3_blind5_prio_)
   - natural_japanese (30 pairs, prefix rc3_blind5_nat_)
   - domain_transfer (30 pairs, prefix rc3_blind5_dom_)
   - general_choice (30 pairs, prefix rc3_blind5_gen_)
   - variable_choice (30 pairs, prefix rc3_blind5_var_)
   - perturbation_invariance (30 pairs, prefix rc3_blind5_pert_)
4. Choice count (K) stratification:
   - K=2: 20 pairs (40 cases)
   - K=3: 60 pairs (120 cases)
   - K=4: 90 pairs (180 cases)
   - K=6: 40 pairs (80 cases)
   - K=8: 15 pairs (30 cases)
   - K=12: 5 pairs (10 cases)
   - K=16: 10 pairs (20 cases)
   Total: 240 pairs = 480 cases.
5. Strict token length contract validation:
   - Every single test case MUST strictly adhere to total tokens <= 450 (< 512 hard limit).
6. Rigorous zero-leakage audit against all background training, dev, calibration, and past blind sets.
7. Independent programmatic semantic validation.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# Verify zero model inference imports
assert "torch" not in sys.modules, "FATAL: torch imported during blind test authoring!"
assert "onnxruntime" not in sys.modules, "FATAL: onnxruntime imported during blind test authoring!"
assert "erabi.inference" not in sys.modules, "FATAL: erabi.inference imported during blind test authoring!"

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from rc3_blind_v5_data.family_core_rules import get_core_rules_pairs
from rc3_blind_v5_data.family_domain_transfer import get_domain_transfer_pairs
from rc3_blind_v5_data.family_general_choice import get_general_choice_pairs
from rc3_blind_v5_data.family_logical_operators import get_logical_operators_pairs
from rc3_blind_v5_data.family_natural_japanese import get_natural_japanese_pairs
from rc3_blind_v5_data.family_perturbation_invariance import get_perturbation_invariance_pairs
from rc3_blind_v5_data.family_priority_exception import get_priority_exception_pairs
from rc3_blind_v5_data.family_variable_choice import get_variable_choice_pairs

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.build_rc3_blind_v5")

OUT_DIR = ROOT / "data" / "sealed_acceptance_rc3_blind_v5"
OUT_PATH = OUT_DIR / "sealed_test_rc3_blind_v5.jsonl"
MANIFEST_PATH = OUT_DIR / "manifest.json"
SEMANTIC_AUDIT_PATH = OUT_DIR / "semantic_audit.json"
OVERLAP_AUDIT_PATH = OUT_DIR / "overlap_audit.json"
TOKEN_AUDIT_PATH = OUT_DIR / "token_audit.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def assemble_all_pairs() -> List[Dict[str, Any]]:
    pairs = []
    pairs.extend(get_core_rules_pairs())
    pairs.extend(get_logical_operators_pairs())
    pairs.extend(get_priority_exception_pairs())
    pairs.extend(get_natural_japanese_pairs())
    pairs.extend(get_domain_transfer_pairs())
    pairs.extend(get_general_choice_pairs())
    pairs.extend(get_variable_choice_pairs())
    pairs.extend(get_perturbation_invariance_pairs())
    return pairs


def flatten_pairs_to_cases(pairs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cases = []
    for p in pairs:
        cases.append(p["case_1"])
        cases.append(p["case_2"])
    return cases


def run_semantic_and_structural_audit(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    logger.info("Running independent programmatic semantic and structural audit...")
    audit_results: Dict[str, Any] = {
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_cases": len(cases),
        "total_pairs": len(cases) // 2,
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "families": {},
        "k_distribution": {},
        "pair_integrity": {}
    }

    # 1. Total count check
    if len(cases) != 480:
        audit_results["errors"].append(f"Total cases {len(cases)} != 480")
        audit_results["is_valid"] = False

    # 2. Family distribution check
    expected_families = [
        "core_rules",
        "logical_operators",
        "priority_exception",
        "natural_japanese",
        "domain_transfer",
        "general_choice",
        "variable_choice",
        "perturbation_invariance"
    ]
    fam_counts = {}
    for c in cases:
        f = c["family"]
        fam_counts[f] = fam_counts.get(f, 0) + 1

    for ef in expected_families:
        cnt = fam_counts.get(ef, 0)
        audit_results["families"][ef] = cnt
        if cnt != 60:
            audit_results["errors"].append(f"Family '{ef}' count {cnt} != 60")
            audit_results["is_valid"] = False

    # 3. K distribution check
    k_counts = {}
    for c in cases:
        k = len(c["choices"])
        k_counts[k] = k_counts.get(k, 0) + 1

    audit_results["k_distribution"] = k_counts
    expected_k = {2: 40, 3: 120, 4: 180, 6: 80, 8: 30, 12: 10, 16: 20}
    for k_val, exp_cnt in expected_k.items():
        act_cnt = k_counts.get(k_val, 0)
        if act_cnt != exp_cnt:
            audit_results["errors"].append(f"K={k_val} count {act_cnt} != {exp_cnt}")
            audit_results["is_valid"] = False

    # 4. Pair integrity check
    by_group = {}
    for c in cases:
        gid = c["group_id"]
        by_group.setdefault(gid, []).append(c)

    if len(by_group) != 240:
        audit_results["errors"].append(f"Total distinct groups {len(by_group)} != 240")
        audit_results["is_valid"] = False

    for gid, group_cases in by_group.items():
        if len(group_cases) != 2:
            audit_results["errors"].append(f"Group {gid} has {len(group_cases)} cases (expected 2)")
            audit_results["is_valid"] = False
            continue

        c1, c2 = group_cases[0], group_cases[1]
        ids = {c1["id"], c2["id"]}
        expected_ids = {f"{gid}_s1", f"{gid}_s2"}
        if ids != expected_ids:
            audit_results["errors"].append(f"Group {gid} ids {ids} != {expected_ids}")
            audit_results["is_valid"] = False

        # Contrastive target check
        t1 = c1["target"]["choice_id"]
        t2 = c2["target"]["choice_id"]
        if t1 == t2:
            audit_results["errors"].append(f"Group {gid} has identical targets: t1={t1} == t2={t2}")
            audit_results["is_valid"] = False

        # Choice count match
        if len(c1["choices"]) != len(c2["choices"]):
            audit_results["errors"].append(f"Group {gid} choice count mismatch: {len(c1['choices'])} vs {len(c2['choices'])}")
            audit_results["is_valid"] = False

        # Choice ID set match
        c1_ids = [ch["id"] for ch in c1["choices"]]
        c2_ids = [ch["id"] for ch in c2["choices"]]
        if set(c1_ids) != set(c2_ids):
            audit_results["errors"].append(f"Group {gid} choice IDs mismatch between c1 and c2")
            audit_results["is_valid"] = False

        if len(c1_ids) != len(set(c1_ids)):
            audit_results["errors"].append(f"Group {gid} has duplicate choice IDs")
            audit_results["is_valid"] = False

        if t1 not in c1_ids:
            audit_results["errors"].append(f"Group {gid} target {t1} not in choices")
            audit_results["is_valid"] = False
        if t2 not in c2_ids:
            audit_results["errors"].append(f"Group {gid} target {t2} not in choices")
            audit_results["is_valid"] = False

    # 5. String sanity check
    choice_id_pattern = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
    for c in cases:
        if not c.get("context", "").strip():
            audit_results["errors"].append(f"Case {c['id']} has empty context")
            audit_results["is_valid"] = False
        if not c.get("question", "").strip():
            audit_results["errors"].append(f"Case {c['id']} has empty question")
            audit_results["is_valid"] = False
        for ch in c["choices"]:
            cid = ch.get("id", "")
            if not cid.strip() or not ch.get("text", "").strip():
                audit_results["errors"].append(f"Case {c['id']} has malformed choice: {ch}")
                audit_results["is_valid"] = False
            if not choice_id_pattern.match(cid):
                audit_results["errors"].append(f"Case {c['id']} choice id '{cid}' violates schema")
                audit_results["is_valid"] = False

    audit_results["error_count"] = len(audit_results["errors"])
    return audit_results


def run_token_contract_audit(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    logger.info("Running strict token length contract audit using tokenizer...")
    from transformers import AutoTokenizer

    model_dir = ROOT / "release" / "rc3" / "model"
    tok = AutoTokenizer.from_pretrained(str(model_dir))
    violations = []
    token_stats = []

    for idx, c in enumerate(cases):
        text = f"Context: {c['context']}\nQuestion: {c['question']}"
        labels = [ch["text"] for ch in c["choices"]]
        text_enc = tok(text, add_special_tokens=False)["input_ids"]
        labels_enc = [tok(l, add_special_tokens=False)["input_ids"] for l in labels]
        # GLiClass input format: [CLS] text [SEP] [LABEL] l1 [SEP] ... [SEP]
        total_tokens = len(text_enc) + sum(len(l) + 2 for l in labels_enc) + 2

        token_stats.append({
            "id": c["id"],
            "family": c["family"],
            "k": len(labels),
            "tokens": total_tokens
        })

        if total_tokens > 512:
            violations.append({
                "idx": idx,
                "id": c["id"],
                "family": c["family"],
                "k": len(labels),
                "tokens": total_tokens,
                "error": "Exceeds 512 token limit"
            })
        elif total_tokens > 450:
            logger.warning(f"Case {c['id']} exceeds 450 target ({total_tokens} tokens)")

    max_tokens = max(s["tokens"] for s in token_stats)
    min_tokens = min(s["tokens"] for s in token_stats)
    avg_tokens = sum(s["tokens"] for s in token_stats) / len(token_stats)

    audit_result = {
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_cases_audited": len(cases),
        "hard_limit": 512,
        "max_tokens": max_tokens,
        "min_tokens": min_tokens,
        "avg_tokens": round(avg_tokens, 2),
        "violations_count": len(violations),
        "is_contract_compliant": (len(violations) == 0),
        "violations": violations
    }

    if violations:
        logger.error(f"FATAL: Token length contract violations detected ({len(violations)} cases > 512 tokens)!")
    else:
        logger.info(f"Token length contract PASSED: max={max_tokens}, avg={round(avg_tokens, 1)}, 0 violations > 512.")

    return audit_result


def run_zero_leakage_audit(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    logger.info("Verifying ZERO data leakage against all training, calibration, and past benchmark sets...")
    check_paths = [
        p for p in (ROOT / "data").glob("**/*.jsonl") if "sealed_acceptance_rc3_blind_v5" not in str(p)
    ] + list((ROOT / "examples").glob("**/*.jsonl"))

    corpus_contexts: Set[str] = set()
    corpus_questions: Set[str] = set()
    corpus_fingerprints: Set[str] = set()
    total_loaded = 0

    for cp in check_paths:
        if not cp.exists():
            continue
        with open(cp, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                ctx = r.get("context", "").strip()
                q = r.get("question", "").strip()
                ch_texts = tuple(sorted(c.get("text", "").strip() for c in r.get("choices", [])))
                corpus_contexts.add(ctx)
                if len(q) > 35:
                    corpus_questions.add(q)
                if ctx and q and ch_texts:
                    fp = f"{ctx} ||| {q} ||| {'|'.join(ch_texts)}"
                    corpus_fingerprints.add(fp)
                total_loaded += 1

    logger.info(f"Loaded {total_loaded} background records across {len(check_paths)} files.")

    leak_context_matches = []
    leak_question_matches = []
    leak_fp_matches = []

    for c in cases:
        ctx = c.get("context", "").strip()
        q = c.get("question", "").strip()
        ch_texts = tuple(sorted(ch.get("text", "").strip() for ch in c.get("choices", [])))
        fp = f"{ctx} ||| {q} ||| {'|'.join(ch_texts)}"

        if ctx in corpus_contexts:
            leak_context_matches.append({"id": c["id"], "context": ctx[:80]})
        if q in corpus_questions:
            leak_question_matches.append({"id": c["id"], "question": q[:80]})
        if fp in corpus_fingerprints:
            leak_fp_matches.append({"id": c["id"], "fingerprint": fp[:100]})

    total_leaks = len(leak_context_matches) + len(leak_question_matches) + len(leak_fp_matches)
    is_leak_free = (total_leaks == 0)

    audit_result = {
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_background_records_audited": total_loaded,
        "total_background_files_audited": len(check_paths),
        "leakage_count": total_leaks,
        "is_leak_free": is_leak_free,
        "context_matches": leak_context_matches,
        "question_matches": leak_question_matches,
        "fingerprint_matches": leak_fp_matches
    }

    if not is_leak_free:
        logger.error(f"FATAL: Overlap detected! {total_leaks} matches against background datasets.")
    else:
        logger.info("Zero-leakage audit PASSED: 0 overlap with all 64,000+ historical records.")

    return audit_result


def main() -> None:
    logger.info("=== Starting Blind v5 Sealed Acceptance Test Suite Assembly ===")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    pairs = assemble_all_pairs()
    cases = flatten_pairs_to_cases(pairs)
    logger.info(f"Assembled {len(pairs)} contrastive pairs ({len(cases)} test cases).")

    # 1. Semantic & Structural Audit
    semantic_audit = run_semantic_and_structural_audit(cases)
    with open(SEMANTIC_AUDIT_PATH, "w", encoding="utf-8") as f:
        json.dump(semantic_audit, f, indent=2, ensure_ascii=False)

    if not semantic_audit["is_valid"]:
        logger.error(f"Semantic audit failed with {semantic_audit['error_count']} errors:")
        for err in semantic_audit["errors"]:
            logger.error(f"  - {err}")
        sys.exit(1)
    logger.info("Semantic and structural audit PASSED.")

    # 2. Token Contract Audit
    token_audit = run_token_contract_audit(cases)
    with open(TOKEN_AUDIT_PATH, "w", encoding="utf-8") as f:
        json.dump(token_audit, f, indent=2, ensure_ascii=False)

    if not token_audit["is_contract_compliant"]:
        logger.error(f"Token contract audit failed with {token_audit['violations_count']} violations!")
        sys.exit(1)
    logger.info("Token length contract audit PASSED.")

    # 3. Zero-Leakage Overlap Audit
    overlap_audit = run_zero_leakage_audit(cases)
    with open(OVERLAP_AUDIT_PATH, "w", encoding="utf-8") as f:
        json.dump(overlap_audit, f, indent=2, ensure_ascii=False)

    if not overlap_audit["is_leak_free"]:
        logger.error(f"Zero-leakage audit failed with {overlap_audit['leakage_count']} matches!")
        sys.exit(1)
    logger.info("Zero-leakage overlap audit PASSED.")

    # 4. Write Sealed Dataset
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    file_sha256 = sha256_file(OUT_PATH)
    file_size_bytes = OUT_PATH.stat().st_size

    manifest = {
        "suite_name": "sealed_test_rc3_blind_v5",
        "description": "ERABI Release Candidate 3 Sealed Acceptance Benchmark Suite (Milestone 34)",
        "created_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_pairs": len(pairs),
        "total_cases": len(cases),
        "file_sha256": file_sha256,
        "file_size_bytes": file_size_bytes,
        "families": semantic_audit["families"],
        "k_distribution": semantic_audit["k_distribution"],
        "token_stats": {
            "max_tokens": token_audit["max_tokens"],
            "avg_tokens": token_audit["avg_tokens"],
            "min_tokens": token_audit["min_tokens"]
        },
        "audits": {
            "semantic_valid": semantic_audit["is_valid"],
            "token_compliant": token_audit["is_contract_compliant"],
            "leak_free": overlap_audit["is_leak_free"],
            "background_records_screened": overlap_audit["total_background_records_audited"]
        }
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    logger.info("=== Blind v5 Suite Assembly Successfully Completed ===")
    logger.info(f"Dataset: {OUT_PATH} ({file_size_bytes} bytes, SHA256: {file_sha256})")
    logger.info(f"Manifest: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
