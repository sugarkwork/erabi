"""Independent rendered-text validator for RC3.1 logic data.

The validator intentionally does not import the generator and does not use the
stored target, state_key, or operator metadata to derive the answer.  It parses
the rendered context and question, evaluates the parsed expression, then maps
the rendered true/false actions back to choice IDs.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple


class SemanticValidationError(ValueError):
    pass


State = Tuple[bool, bool, bool]

_EXPRESSION_TO_OPERATOR: Tuple[Tuple[str, str], ...] = (
    ("(A XOR B) AND C", "nested_xor_and"),
    ("(A AND B) OR C", "nested_and_or"),
    ("A AND (B OR C)", "nested_a_and_or"),
    ("NOT(A AND B)", "nested_not_and"),
    ("NOT(A OR B)", "nested_not_or"),
    ("NOT NOT A", "double_negation"),
    ("REVERSE(A)", "polarity_reversal"),
    ("NAND(A,B)", "nand"),
    ("NOR(A,B)", "nor"),
    ("A XOR B", "xor"),
    ("A AND NOT B", "and_not_b"),
    ("NOT A OR B", "not_a_or_b"),
    ("A AND B", "and"),
    ("A OR B", "or"),
    ("A -> B", "implication"),
    ("NOT A", "not"),
)
_OPERATOR_TO_EXPRESSION = {operator: expression for expression, operator in _EXPRESSION_TO_OPERATOR}

_CONTEXT_RE = re.compile(
    r"条件(?P<name>[ABC])「(?P<label>[^」]+)」(?:の状態)?は(?P<status>不成立|成立)"
)
_CONTEXT_PREFIX_RE = re.compile(
    r"(?:"
    r"運用記録コード [A-Za-z]+-[A-Za-z]+：[^。]+。|"
    r"制御盤入力 [A-Za-z]+-[A-Za-z]+。対象は[^。]+である。|"
    r"点検票 [A-Za-z]+-[A-Za-z]+ の対象は[^。]+。|"
    r"観測メモ [A-Za-z]+-[A-Za-z]+：[^。]+。|"
    r"確認記録 [A-Za-z]+-[A-Za-z]+。[^。]+を評価する。|"
    r"判定記録 [A-Za-z]+-[A-Za-z]+：[^。]+。"
    r")\Z"
)
_QUESTION_EXPRESSION_RE = re.compile(
    r"\A(?P<head>評価式|論理式|判定式|式)「(?P<expression>[^」]+)」(?P<rest>.*)\Z"
)
_NORMAL_MAPPING_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"が成立なら「(?P<true>[^」]+)」、不成立なら「(?P<false>[^」]+)」を選択してください。\Z"),
    re.compile(r"の判定が真の場合は「(?P<true>[^」]+)」、偽の場合は「(?P<false>[^」]+)」としてください。\Z"),
    re.compile(r"が有効なら「(?P<true>[^」]+)」、無効なら「(?P<false>[^」]+)」を実施してください。\Z"),
    re.compile(r"の結果が真なら「(?P<true>[^」]+)」、偽なら「(?P<false>[^」]+)」を選んでください。\Z"),
    re.compile(r"が真なら「(?P<true>[^」]+)」、偽なら「(?P<false>[^」]+)」を選択してください。\Z"),
)
_REORDERED_MAPPING_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"が不成立なら「(?P<false>[^」]+)」、成立なら「(?P<true>[^」]+)」を選択してください。\Z"),
    re.compile(r"の判定が偽の場合は「(?P<false>[^」]+)」、真の場合は「(?P<true>[^」]+)」としてください。\Z"),
    re.compile(r"が無効なら「(?P<false>[^」]+)」、有効なら「(?P<true>[^」]+)」を実施してください。\Z"),
    re.compile(r"の結果が偽なら「(?P<false>[^」]+)」、真なら「(?P<true>[^」]+)」を選んでください。\Z"),
    re.compile(r"が偽なら「(?P<false>[^」]+)」、真なら「(?P<true>[^」]+)」を選択してください。\Z"),
)
_IMPLICIT_MAPPING_PATTERN = re.compile(
    r"では通常「(?P<false>[^」]+)」を選択します。ただし、成立する場合に限り「(?P<true>[^」]+)」を選択してください。\Z"
)


def parse_context(context: str) -> State:
    matches = list(_CONTEXT_RE.finditer(context))
    names = [m.group("name") for m in matches]
    if len(matches) != 3 or sorted(names) != ["A", "B", "C"]:
        raise SemanticValidationError(f"Could not parse A/B/C states: {context}")
    prefix = context[: matches[0].start()]
    if not _CONTEXT_PREFIX_RE.fullmatch(prefix):
        raise SemanticValidationError(f"Context has an unsupported or unparsed prefix: {context}")
    if context.count("条件") != 3 or context[matches[-1].end() :] != "。":
        raise SemanticValidationError(f"Context has unparsed or duplicate condition text: {context}")
    if any(context[left.end() : right.start()] != "、" for left, right in zip(matches, matches[1:])):
        raise SemanticValidationError(f"Context condition separators are ambiguous: {context}")
    found = {m.group("name"): m.group("status") for m in matches}
    return tuple(found[name] == "成立" for name in ("A", "B", "C"))  # type: ignore[return-value]


def parse_question(question: str) -> Tuple[str, str, str, str]:
    match = _QUESTION_EXPRESSION_RE.fullmatch(question)
    if not match:
        raise SemanticValidationError(f"Question has an unsupported or unparsed expression prefix: {question}")
    expression = match.group("expression")
    expression_matches = [marker for marker, _ in _EXPRESSION_TO_OPERATOR if marker == expression]
    if len(expression_matches) != 1:
        raise SemanticValidationError(f"Expression marker is missing, unsupported, or ambiguous: {question}")
    operator = dict(_EXPRESSION_TO_OPERATOR)[expression]
    rest = match.group("rest")
    matched: List[Tuple[str, re.Match[str]]] = []
    for style, patterns in (("normal", _NORMAL_MAPPING_PATTERNS), ("reordered", _REORDERED_MAPPING_PATTERNS)):
        for pattern in patterns:
            result = pattern.fullmatch(rest)
            if result:
                matched.append((style, result))
    implicit = _IMPLICIT_MAPPING_PATTERN.fullmatch(rest)
    if implicit:
        matched.append(("implicit_fallback", implicit))
    if len(matched) != 1:
        raise SemanticValidationError(f"Action mapping is missing, multiple, or unparsed: {question}")
    style, action_match = matched[0]
    true_text = action_match.group("true")
    false_text = action_match.group("false")
    if true_text == false_text:
        raise SemanticValidationError(f"True/false action mapping collapses to one action: {question}")
    return operator, true_text, false_text, style


def evaluate_parsed_operator(operator: str, state: State) -> bool:
    """Independent evaluator; intentionally separate from generator.evaluate_operator."""
    a, b, c = state
    table = {
        "and": a and b,
        "or": a or b,
        "xor": (a and not b) or (not a and b),
        "and_not_b": a and (not b),
        "not_a_or_b": (not a) or b,
        "nand": not (a and b),
        "nor": (not a) and (not b),
        "not": not a,
        "implication": (not a) or b,
        "double_negation": not (not a),
        "polarity_reversal": not a,
        "nested_and_or": (a and b) or c,
        "nested_a_and_or": a and (b or c),
        "nested_not_and": not (a and b),
        "nested_not_or": not (a or b),
        "nested_xor_and": ((a and not b) or (not a and b)) and c,
    }
    try:
        return bool(table[operator])
    except KeyError as exc:
        raise SemanticValidationError(f"Unknown parsed operator: {operator}") from exc


def derive_record(record: Mapping[str, Any]) -> Dict[str, Any]:
    context_state = parse_context(str(record["context"]))
    operator, true_text, false_text, mapping_style = parse_question(str(record["question"]))
    choices = record["choices"]
    by_text = {str(choice["text"]): str(choice["id"]) for choice in choices}
    if true_text not in by_text or false_text not in by_text:
        raise SemanticValidationError(f"Rendered actions are not both choices: {record.get('id')}")
    result = evaluate_parsed_operator(operator, context_state)
    expected = by_text[true_text if result else false_text]
    stored = str(record["target"]["choice_id"])
    return {
        "id": str(record.get("id", "")),
        "group_id": str(record.get("group_id", "")),
        "operator": operator,
        "expression": _OPERATOR_TO_EXPRESSION.get(operator, ""),
        "state": "".join("1" if bit else "0" for bit in context_state),
        "mapping_style": mapping_style,
        "true_action": true_text,
        "false_action": false_text,
        "expected_target": expected,
        "stored_target": stored,
        "is_match": expected == stored,
        "metadata_operator_match": record.get("operator_family") in (None, operator),
    }


def _validate_shape(record: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    required = ("id", "group_id", "family", "context", "question", "choices", "target")
    for key in required:
        if key not in record:
            errors.append(f"{record.get('id', '<unknown>')}: missing {key}")
    if errors:
        return errors
    choices = record["choices"]
    if not isinstance(choices, list) or len(choices) < 2:
        errors.append(f"{record['id']}: choices must contain at least two entries")
        return errors
    if any(not isinstance(choice, Mapping) for choice in choices):
        errors.append(f"{record['id']}: choices must be mapping objects")
        return errors
    ids = [str(choice.get("id", "")) for choice in choices]
    texts = [str(choice.get("text", "")).strip() for choice in choices]
    if len(set(ids)) != len(ids):
        errors.append(f"{record['id']}: duplicate choice IDs")
    if len(set(texts)) != len(texts):
        errors.append(f"{record['id']}: duplicate choice text")
    if any(not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", cid) for cid in ids):
        errors.append(f"{record['id']}: malformed choice ID")
    target = str(record["target"].get("choice_id", ""))
    if target not in ids:
        errors.append(f"{record['id']}: target not in choices")
    for choice in choices:
        text = str(choice.get("text", "")).strip()
        if not text:
            errors.append(f"{record['id']}: empty choice text")
        if any(token in text for token in ("ため", "ので", "により", "理由", "として", "確認し", "認められ")):
            errors.append(f"{record['id']}: choice contains rationale-like wording")
    rendered = (
        f"{record.get('context', '')}\n{record.get('question', '')}\n"
        + "\n".join(texts)
    )
    if any(marker in rendered for marker in ("__", "expected_target", "truth_value", "target_id")):
        errors.append(f"{record['id']}: internal marker leaked into rendered input")
    return errors


def validate_records(records: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    errors: List[str] = []
    derived: List[Dict[str, Any]] = []
    groups: Dict[str, List[Mapping[str, Any]]] = defaultdict(list)
    for record in records:
        errors.extend(_validate_shape(record))
        try:
            result = derive_record(record)
            derived.append(result)
            if not result["is_match"]:
                errors.append(
                    f"{record.get('id')}: semantic mismatch expected={result['expected_target']} stored={result['stored_target']}"
                )
            if not result["metadata_operator_match"]:
                errors.append(f"{record.get('id')}: metadata operator disagrees with rendered question")
        except (KeyError, TypeError, SemanticValidationError) as exc:
            errors.append(f"{record.get('id', '<unknown>')}: {exc}")
        groups[str(record.get("group_id", ""))].append(record)

    pair_count = 0
    diff_target_pairs = 0
    for group_id, pair in sorted(groups.items()):
        if len(pair) != 2:
            errors.append(f"{group_id}: expected exactly two records, got {len(pair)}")
            continue
        pair_count += 1
        if pair[0].get("context") != pair[1].get("context"):
            errors.append(f"{group_id}: pair context differs")
        if [c.get("text") for c in pair[0].get("choices", [])] != [c.get("text") for c in pair[1].get("choices", [])]:
            errors.append(f"{group_id}: pair choices differ")
        if pair[0].get("mapping_style") != pair[1].get("mapping_style"):
            errors.append(f"{group_id}: pair mapping styles differ")
        if pair[0].get("condition_order") != pair[1].get("condition_order"):
            errors.append(f"{group_id}: pair condition order differs")
        if pair[0].get("target", {}).get("choice_id") != pair[1].get("target", {}).get("choice_id"):
            diff_target_pairs += 1
        else:
            errors.append(f"{group_id}: pair targets are not contrastive")

    by_operator = Counter(item["operator"] for item in derived)
    by_state = Counter((item["operator"], item["state"]) for item in derived)
    by_target = Counter(item["stored_target"] for item in derived)
    by_domain = Counter(str(record.get("domain", "unknown")) for record in records)
    by_k = Counter(len(record.get("choices", [])) for record in records)
    return {
        "total_records": len(records),
        "total_pairs": pair_count,
        "derived_records": len(derived),
        "semantic_mismatch_count": sum(1 for item in derived if not item["is_match"]),
        "diff_target_pairs": diff_target_pairs,
        "pair_integrity": diff_target_pairs == pair_count and not any("pair " in error for error in errors),
        "by_operator": dict(sorted(by_operator.items())),
        "by_operator_state": {f"{op}:{state}": count for (op, state), count in sorted(by_state.items())},
        "by_target": dict(sorted(by_target.items())),
        "by_domain": dict(sorted(by_domain.items())),
        "by_k": {str(k): count for k, count in sorted(by_k.items())},
        "errors": errors,
        "error_count": len(errors),
        "is_valid": not errors,
    }
