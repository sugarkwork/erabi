"""Audits for RC3.1 data isolation, balance, and token contracts."""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[2]
NEW_DIR_NAMES = {"rc3_1_train", "rc3_1_logic_bridge"}
FUZZY_SIMILARITY_THRESHOLD = 0.97
FUZZY_CHAR_NGRAM_SIZE = 5
FUZZY_TOKEN_NGRAM_SIZE = 3
FUZZY_MAX_POSTINGS = 128
FUZZY_MAX_CANDIDATES = 40

REQUIRED_OPERATOR_STATES: Dict[str, set[str]] = {
    operator: {"000", "010", "100", "110"}
    for operator in (
        "and",
        "or",
        "xor",
        "and_not_b",
        "not_a_or_b",
        "nand",
        "nor",
        "not",
        "implication",
        "double_negation",
        "polarity_reversal",
    )
}
REQUIRED_OPERATOR_STATES.update(
    {
        operator: {f"{a}{b}{c}" for a in "01" for b in "01" for c in "01"}
        for operator in (
            "nested_and_or",
            "nested_a_and_or",
            "nested_not_and",
            "nested_not_or",
            "nested_xor_and",
        )
    }
)


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def full_signature(record: Mapping[str, Any]) -> Tuple[str, str, Tuple[Tuple[str, str], ...]]:
    choices = tuple(
        (
            str(choice.get("id", choice.get("choice_id", choice.get("label", "")))),
            str(choice.get("text", choice.get("label", choice.get("name", "")))),
        )
        for choice in record.get("choices", [])
        if isinstance(choice, Mapping)
    )
    return (str(record.get("context", "")).strip(), str(record.get("question", "")).strip(), choices)


def context_question_signature(record: Mapping[str, Any]) -> Tuple[str, str]:
    return (str(record.get("context", "")).strip(), str(record.get("question", "")).strip())


def _normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).lower()
    value = re.sub(r"\d+(?:\.\d+)?", "<num>", value)
    value = re.sub(r"\s+", "", value)
    value = re.sub(r"[、。,:：;；.!！?？()（）「」『』【】\[\]{}<>《》/\\_-]+", "|", value)
    return value


def normalized_signature(record: Mapping[str, Any]) -> str:
    context = _normalize_text(str(record.get("context", "")))
    question = _normalize_text(str(record.get("question", "")))
    choices = sorted(
        _normalize_text(str(choice.get("text", "")))
        for choice in record.get("choices", [])
        if isinstance(choice, Mapping)
    )
    return f"{context}|||{question}|||{'|'.join(choices)}"


def historical_jsonl_paths(root: Path = ROOT) -> List[Path]:
    paths: List[Path] = []
    for base in (root / "data", root / "examples", root / "evidence", root / "runs"):
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.jsonl")):
            if any(part in NEW_DIR_NAMES for part in path.parts):
                continue
            paths.append(path)
    return paths


def load_historical_records(root: Path = ROOT) -> Tuple[List[Dict[str, Any]], List[str]]:
    records: List[Dict[str, Any]] = []
    paths = historical_jsonl_paths(root)
    for path in paths:
        records.extend(load_jsonl(path))
    return records, [str(path.relative_to(root)) for path in paths]


def load_blind_v5_records(root: Path = ROOT) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Load Blind v5 only from explicitly named historical paths."""
    records: List[Dict[str, Any]] = []
    paths: List[str] = []
    for path in historical_jsonl_paths(root):
        normalized = str(path).lower().replace("-", "_")
        if "blind_v5" not in normalized and "blind5" not in normalized:
            continue
        records.extend(load_jsonl(path))
        paths.append(str(path.relative_to(root)))
    return records, paths


def _comparison_text(record: Mapping[str, Any]) -> str:
    choices = "|".join(
        str(choice.get("text", "")) for choice in record.get("choices", []) if isinstance(choice, Mapping)
    )
    return _normalize_text(f"{record.get('context', '')}\n{record.get('question', '')}\n{choices}")


def _ngram_keys(value: str) -> set[str]:
    keys = {f"char:{value[index:index + FUZZY_CHAR_NGRAM_SIZE]}" for index in range(max(0, len(value) - FUZZY_CHAR_NGRAM_SIZE + 1))}
    tokens = re.findall(r"[一-龯ぁ-んァ-ヶー]+|[A-Za-z0-9]+", value)
    keys.update(
        "token:" + "\x1f".join(tokens[index : index + FUZZY_TOKEN_NGRAM_SIZE])
        for index in range(max(0, len(tokens) - FUZZY_TOKEN_NGRAM_SIZE + 1))
    )
    return keys


def _fuzzy_near_copy_candidates(
    records: Sequence[Mapping[str, Any]],
    historical: Sequence[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    """Find light-edit copies using bounded char/token n-gram retrieval.

    The inverted index caps postings and each new record is compared with at
    most FUZZY_MAX_CANDIDATES historical records, avoiding quadratic matching.
    """
    historical_texts = [_comparison_text(record) for record in historical]
    index: Dict[str, List[int]] = {}
    for index_value, text_value in enumerate(historical_texts):
        for key in _ngram_keys(text_value):
            postings = index.setdefault(key, [])
            if len(postings) < FUZZY_MAX_POSTINGS:
                postings.append(index_value)
    candidates: List[Dict[str, Any]] = []
    for record in records:
        text_value = _comparison_text(record)
        if not text_value:
            continue
        votes: Counter[int] = Counter()
        query_keys = _ngram_keys(text_value)
        for key in query_keys:
            votes.update(index.get(key, ()))
        for historical_index, shared in votes.most_common(FUZZY_MAX_CANDIDATES):
            historical_text = historical_texts[historical_index]
            if text_value == historical_text or shared < 6:
                continue
            similarity = SequenceMatcher(None, text_value, historical_text, autojunk=False).ratio()
            if similarity >= FUZZY_SIMILARITY_THRESHOLD:
                candidates.append(
                    {
                        "record_id": str(record.get("id")),
                        "historical_record_id": str(historical[historical_index].get("id")),
                        "historical_index": historical_index,
                        "shared_ngrams": shared,
                        "similarity": round(similarity, 6),
                    }
                )
    return sorted(candidates, key=lambda item: (item["record_id"], item["historical_index"]))


def audit_historical_overlap(
    records: Sequence[Mapping[str, Any]],
    historical: Sequence[Mapping[str, Any]],
    historical_paths: Sequence[str],
    blind_v5_records: Sequence[Mapping[str, Any]] | None = None,
    blind_v5_paths: Sequence[str] | None = None,
) -> Dict[str, Any]:
    historical_full = {full_signature(record) for record in historical}
    historical_context_question = {context_question_signature(record) for record in historical}
    historical_normalized = {normalized_signature(record) for record in historical}
    blind_v5 = list(blind_v5_records) if blind_v5_records is not None else [record for record in historical if str(record.get("id", "")).startswith("rc3_blind5_")]
    blind_v5_full = {full_signature(record) for record in blind_v5}
    full_matches = [str(record.get("id")) for record in records if full_signature(record) in historical_full]
    context_question_matches = [str(record.get("id")) for record in records if context_question_signature(record) in historical_context_question]
    blind_matches = [str(record.get("id")) for record in records if full_signature(record) in blind_v5_full]
    normalized_candidates = [str(record.get("id")) for record in records if normalized_signature(record) in historical_normalized]
    fuzzy_candidates = _fuzzy_near_copy_candidates(records, historical)
    return {
        "historical_files": len(historical_paths),
        "historical_records": len(historical),
        "exact_full_matches": sorted(set(full_matches)),
        "exact_context_question_matches": sorted(set(context_question_matches)),
        "blind_v5_exact_matches": sorted(set(blind_matches)),
        "normalized_near_copy_candidates": sorted(set(normalized_candidates)),
        "fuzzy_near_copy_candidates": fuzzy_candidates,
        "fuzzy_similarity_threshold": FUZZY_SIMILARITY_THRESHOLD,
        "fuzzy_ngram": {
            "types": ["character", "token"],
            "character_size": FUZZY_CHAR_NGRAM_SIZE,
            "token_size": FUZZY_TOKEN_NGRAM_SIZE,
            "max_postings": FUZZY_MAX_POSTINGS,
            "max_candidates_per_record": FUZZY_MAX_CANDIDATES,
        },
        "blind_v5_paths": sorted(set(blind_v5_paths or ())),
        "is_clean": not (full_matches or context_question_matches or blind_matches or normalized_candidates or fuzzy_candidates),
    }


def audit_split_isolation(split_records: Mapping[str, Sequence[Mapping[str, Any]]]) -> Dict[str, Any]:
    split_names = sorted(split_records)
    exact_overlaps: Dict[str, int] = {}
    normalized_overlaps: Dict[str, int] = {}
    group_overlaps: Dict[str, int] = {}
    domain_overlaps: Dict[str, List[str]] = {}
    template_overlaps: Dict[str, List[str]] = {}
    for i, left_name in enumerate(split_names):
        left = split_records[left_name]
        left_full = {full_signature(record) for record in left}
        left_norm = {normalized_signature(record) for record in left}
        left_groups = {str(record.get("group_id")) for record in left}
        left_domains = {str(record.get("domain")) for record in left}
        left_templates = {str(record.get("template_family")) for record in left}
        for right_name in split_names[i + 1 :]:
            right = split_records[right_name]
            key = f"{left_name}__{right_name}"
            exact_overlaps[key] = len(left_full & {full_signature(record) for record in right})
            normalized_overlaps[key] = len(left_norm & {normalized_signature(record) for record in right})
            group_overlaps[key] = len(left_groups & {str(record.get("group_id")) for record in right})
            domain_overlaps[key] = sorted(left_domains & {str(record.get("domain")) for record in right})
            template_overlaps[key] = sorted(left_templates & {str(record.get("template_family")) for record in right})
    is_clean = (
        not any(exact_overlaps.values())
        and not any(normalized_overlaps.values())
        and not any(group_overlaps.values())
        and not any(domain_overlaps.values())
        and not any(template_overlaps.values())
    )
    return {
        "exact_overlaps": exact_overlaps,
        "normalized_overlaps": normalized_overlaps,
        "group_overlaps": group_overlaps,
        "domain_overlaps": domain_overlaps,
        "template_overlaps": template_overlaps,
        "is_clean": is_clean,
    }


def audit_balance(records: Sequence[Mapping[str, Any]], derived: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    by_position: Counter[int] = Counter()
    by_target: Counter[str] = Counter()
    by_k_position: Dict[int, Counter[int]] = {}
    for record in records:
        target = str(record["target"]["choice_id"])
        position = next(i for i, choice in enumerate(record["choices"]) if str(choice["id"]) == target) + 1
        choice_count = len(record["choices"])
        by_position[position] += 1
        by_k_position.setdefault(choice_count, Counter())[position] += 1
        by_target[target] += 1
    operators = Counter(str(item["operator"]) for item in derived)
    domains = Counter(str(record.get("domain")) for record in records)
    ks = Counter(len(record.get("choices", [])) for record in records)
    position_values = list(by_position.values())
    target_values = list(by_target.values())
    operator_values = list(operators.values())
    operator_domain_sets: Dict[str, set[str]] = {}
    for record, item in zip(records, derived):
        operator_domain_sets.setdefault(str(item["operator"]), set()).add(str(record.get("domain")))
    observed_states: Dict[str, set[str]] = {}
    for item in derived:
        observed_states.setdefault(str(item["operator"]), set()).add(str(item["state"]))
    truth_state_coverage = {
        operator: {
            "required": sorted(required),
            "observed": sorted(observed_states.get(operator, set())),
            "missing": sorted(required - observed_states.get(operator, set())),
        }
        for operator, required in sorted(REQUIRED_OPERATOR_STATES.items())
    }
    truth_state_gate = all(not item["missing"] for item in truth_state_coverage.values())
    operator_domain_counts = {operator: len(domains_for_operator) for operator, domains_for_operator in sorted(operator_domain_sets.items())}
    operator_domain_gate = set(operator_domain_counts) == set(REQUIRED_OPERATOR_STATES) and all(
        count >= 2 for count in operator_domain_counts.values()
    )
    pair_groups: Dict[str, List[Mapping[str, Any]]] = {}
    for record in records:
        pair_groups.setdefault(str(record.get("group_id")), []).append(record)
    pair_integrity = True
    for pair in pair_groups.values():
        if len(pair) != 2:
            pair_integrity = False
            break
        if pair[0].get("context") != pair[1].get("context"):
            pair_integrity = False
            break
        if [choice.get("text") for choice in pair[0].get("choices", [])] != [choice.get("text") for choice in pair[1].get("choices", [])]:
            pair_integrity = False
            break
        if pair[0].get("target", {}).get("choice_id") == pair[1].get("target", {}).get("choice_id"):
            pair_integrity = False
            break
    lexical_by_k: Dict[str, Dict[str, Any]] = {}
    for k in sorted(ks):
        if k <= 2:
            continue
        selected = [record for record in records if len(record.get("choices", [])) == k]
        lexical_records = [
            record
            for record in selected
            if any(value == "lexical_overlap" for value in dict(record.get("distractor_classes", {})).values())
        ]
        lexical_by_k[str(k)] = {
            "records": len(selected),
            "with_lexical_overlap": len(lexical_records),
            "coverage": round(len(lexical_records) / len(selected), 6) if selected else 0.0,
        }
    lexical_overlap_gate = all(
        item["records"] > 0 and item["with_lexical_overlap"] == item["records"]
        for item in lexical_by_k.values()
    )
    position_spread_by_k = {
        str(k): max(counter.values()) - min(counter.get(position, 0) for position in range(1, k + 1))
        for k, counter in sorted(by_k_position.items())
    }
    # Position balance is meaningful within each choice cardinality.  Across
    # K values, later positions necessarily have fewer opportunities.
    position_balance = all(
        spread <= max(2, sum(counter.values()) // 20)
        for (k, counter), spread in zip(sorted(by_k_position.items()), position_spread_by_k.values())
    )
    # Operator balance is evaluated over the complete artifact.  Split-level
    # domain counts can intentionally differ because dev/calibration domains
    # are held out, so domain counts are reported but are not used as a gate.
    operator_spread = max(operator_values) - min(operator_values) if operator_values else 0
    operator_balance = bool(operator_values) and operator_spread <= max(2, len(records) // 500)
    return {
        "operator_counts": dict(sorted(operators.items())),
        "operator_spread": operator_spread,
        "operator_balance": operator_balance,
        "truth_state_coverage": truth_state_coverage,
        "truth_state_gate": truth_state_gate,
        "operator_domain_counts": operator_domain_counts,
        "operator_domain_gate": operator_domain_gate,
        "pair_integrity": pair_integrity,
        "lexical_overlap_by_k": lexical_by_k,
        "lexical_overlap_gate": lexical_overlap_gate,
        "domain_counts": dict(sorted(domains.items())),
        "k_counts": {str(k): value for k, value in sorted(ks.items())},
        "target_position_counts": {str(k): value for k, value in sorted(by_position.items())},
        "target_position_counts_by_k": {
            str(k): {str(position): counter.get(position, 0) for position in range(1, k + 1)}
            for k, counter in sorted(by_k_position.items())
        },
        "target_choice_counts": dict(sorted(by_target.items())),
        "position_spread": max(position_values) - min(position_values) if position_values else 0,
        "position_spread_by_k": position_spread_by_k,
        "target_spread": max(target_values) - min(target_values) if target_values else 0,
        "is_balanced": bool(position_values)
        and position_balance
        and operator_balance
        and truth_state_gate
        and operator_domain_gate
        and pair_integrity
        and lexical_overlap_gate,
    }


def audit_token_contract(records: Sequence[Mapping[str, Any]], tokenizer_path: Path) -> Dict[str, Any]:
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_path), local_files_only=True)
    text_counts: List[int] = []
    label_counts: List[int] = []
    combined_counts: List[int] = []
    violations: List[Dict[str, Any]] = []
    for record in records:
        # This mirrors GLiClass's bi-encoder prepare_inputs path used by
        # src/erabi/inference.py and src/erabi/train.py: prompt + space +
        # context is the text encoder input; each label is tokenized by the
        # separate label tokenizer.  No synthetic Context/Question wrapper is
        # counted here.
        model_text = f"{record['question']} {record['context']}"
        text_ids = tokenizer(model_text, add_special_tokens=True, truncation=False)["input_ids"]
        label_lengths = [
            len(tokenizer(str(choice["text"]), add_special_tokens=True, truncation=False)["input_ids"])
            for choice in record["choices"]
        ]
        text_count = len(text_ids)
        label_max = max(label_lengths) if label_lengths else 0
        combined = text_count + label_max
        text_counts.append(text_count)
        label_counts.append(label_max)
        combined_counts.append(combined)
        for count, kind in ((text_count, "safety_budget"), (text_count, "hard_limit")):
            limit = 450 if kind == "safety_budget" else 512
            if count > limit:
                violations.append({"id": record.get("id"), "tokens": count, "kind": kind})
    return {
        "total_records": len(records),
        "formatter": "GLiClass bi-encoder prepare_inputs: prompt + ' ' + context; labels independently tokenized",
        "max_tokens": max(text_counts) if text_counts else 0,
        "min_tokens": min(text_counts) if text_counts else 0,
        "avg_tokens": round(sum(text_counts) / len(text_counts), 2) if text_counts else 0.0,
        "max_label_tokens": max(label_counts) if label_counts else 0,
        "max_text_plus_label_tokens": max(combined_counts) if combined_counts else 0,
        "safety_limit": 450,
        "hard_limit": 512,
        "violations": violations,
        "violations_count": len(violations),
        "is_compliant": not violations,
    }


def sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()
