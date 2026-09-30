"""Build a deterministic, class-balanced public benchmark shared by ERABI and Laya.

Run with an environment that has `datasets` and `huggingface_hub` installed. The
generated cases stay under runs/ and are not committed with this harness.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import zlib
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = 13
MAX_CHOICES = 16
MAX_CONTEXT_CHARS = {"ja": 320, "zh-CN": 320, "zh": 320, "default": 800}
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
SECRET_RE = re.compile(r"\b(?:sk|rk|api|token|secret)[-_][A-Z0-9_-]{16,}\b", re.I)
PHONE_RE = re.compile(r"(?<!\w)\+?\d[\d ().-]{8,}\d(?!\w)")


def _clean(text: object, language: str) -> tuple[str, int, int]:
    value = str(text or "").strip()
    redactions = 0
    for pattern, replacement in ((EMAIL_RE, "[EMAIL]"), (SECRET_RE, "[SECRET]")):
        value, count = pattern.subn(replacement, value)
        redactions += count
    def mask_phone(match: re.Match[str]) -> str:
        nonlocal redactions
        digits = re.sub(r"\D", "", match.group())
        if 10 <= len(digits) <= 15:
            redactions += 1
            return "[PHONE]"
        return match.group()
    value = PHONE_RE.sub(mask_phone, value)
    cap = MAX_CONTEXT_CHARS.get(language, MAX_CONTEXT_CHARS["default"])
    removed = max(0, len(value) - cap)
    return value[:cap], removed, redactions


def _balanced(rows, label_of, per_label: int, rng: random.Random):
    groups = defaultdict(list)
    for index, row in enumerate(rows):
        label = label_of(row)
        if label is not None:
            groups[str(label)].append((index, row))
    picked = []
    counts = {}
    for label in sorted(groups):
        items = groups[label]
        rng.shuffle(items)
        selected = items[:per_label]
        counts[label] = len(selected)
        picked.extend((index, row, label) for index, row in selected)
    rng.shuffle(picked)
    return picked, counts


def _rng_for(name: str) -> random.Random:
    return random.Random(SEED + zlib.crc32(name.encode("utf-8")))


def _make_rows(suite: str, dataset_id: str, config: str | None, split: str,
               language: str, raw_rows, label_of, label_text: dict[str, str],
               question: str, per_label: int, max_options: int = MAX_CHOICES):
    rng = _rng_for(suite)
    picked, class_counts = _balanced(raw_rows, label_of, per_label, rng)
    all_labels = sorted(label_text)
    if not picked or len(all_labels) < 2:
        raise ValueError(f"{suite}: no usable labelled rows or fewer than two classes")
    cases = []
    truncated_count = redaction_count = 0
    for source_index, raw, gold_label in picked:
        if gold_label not in label_text:
            raise ValueError(f"{suite}: missing display text for label {gold_label}")
        if len(all_labels) > max_options:
            distractors = [label for label in all_labels if label != gold_label]
            candidate_labels = [gold_label, *rng.sample(distractors, max_options - 1)]
        else:
            candidate_labels = list(all_labels)
        rng.shuffle(candidate_labels)
        text_field = raw.get("text", raw.get("sentence", ""))
        if suite.startswith("xnli"):
            context_raw = f"Premise: {raw['premise']}\nHypothesis: {raw['hypothesis']}"
        else:
            context_raw = str(text_field or "")
        context, removed, redactions = _clean(context_raw, language)
        # Do not benchmark a source label against a silently shortened example.
        # The shared runner performs the authoritative tokenizer-level limit
        # check; this character guard removes obviously long rows first.
        if not context or removed:
            continue
        choices = [{"id": f"c{position:02d}", "text": label_text[label]}
                   for position, label in enumerate(candidate_labels)]
        if len({choice["text"] for choice in choices}) != len(choices):
            raise ValueError(f"{suite}: candidate display labels are not unique")
        gold_position = candidate_labels.index(gold_label)
        cases.append({
            "id": f"{suite}:{source_index:06d}",
            "suite": suite,
            "dataset": dataset_id,
            "config": config,
            "split": split,
            "language": language,
            "context": context,
            "question": question,
            "choices": choices,
            "gold_choice_id": choices[gold_position]["id"],
            "gold_label": label_text[gold_label],
            "source_label": gold_label,
            "source_row_index": source_index,
            "source_chars_removed": removed,
            "contact_or_secret_redactions": redactions,
        })
        redaction_count += redactions
    actual_class_counts = dict(Counter(case["source_label"] for case in cases))
    return cases, {
        "dataset": dataset_id, "config": config, "split": split,
        "language": language, "rows": len(cases), "balanced_rows_per_label": per_label,
        "sampled_class_counts_before_length_filter": class_counts,
        "included_class_counts": actual_class_counts,
        "source_char_truncated_rows": truncated_count,
        "contact_or_secret_redactions": redaction_count,
        "source_split_note": "public test split; source provenance recorded in manifest; character-truncated rows are excluded",
    }


def _load(repo: str, config: str | None, split: str = "test", revision: str | None = None):
    from datasets import load_dataset
    kwargs = {"revision": revision} if revision else {}
    return load_dataset(repo, config, split=split, **kwargs) if config else load_dataset(repo, split=split, **kwargs)


def _add(suites, manifest, *args, **kwargs):
    rows, meta = _make_rows(*args, **kwargs)
    suites.extend(rows)
    manifest[meta["dataset"] + ("/" + meta["config"] if meta["config"] else "") + "/" + meta["language"]] = meta


def build(per_label: int | None, output_dir: Path) -> None:
    from huggingface_hub import HfApi

    suite_rows = []
    suite_manifest = {}
    sources = {}

    def note_source(repo: str):
        if repo in sources:
            return
        try:
            info = HfApi().dataset_info(repo)
            card = info.card_data
            sources[repo] = {"revision": info.sha, "license": getattr(card, "license", None)}
        except Exception as exc:
            sources[repo] = {"revision": None, "license": None,
                             "metadata_error": type(exc).__name__}

    massive_repo = "mteb/amazon_massive_intent"
    for lang in ("ja", "en", "zh-CN"):
        note_source(massive_repo)
        dataset = _load(massive_repo, lang, revision=sources[massive_repo].get("revision"))
        labels = {str(label): str(label).replace("_", " ").replace(".", ": ")
                  for label in sorted(set(dataset["label_text"]))}
        _add(suite_rows, suite_manifest, f"massive_intent_{lang}", massive_repo, lang,
             "test", lang, dataset, lambda row: row["label_text"], labels,
             "Which intent best matches the user's utterance?", per_label or 8)

    xnli_repo = "facebook/xnli"
    xnli_label_text = {
        "0": "entailment: the premise implies the hypothesis",
        "1": "neutral: the premise neither implies nor contradicts the hypothesis",
        "2": "contradiction: the premise implies the hypothesis is false",
    }
    xnli_zh_text = {
        "0": "蕴含：前提可以推出假设",
        "1": "中立：前提既不能推出也不能反驳假设",
        "2": "矛盾：前提可以推出假设为假",
    }
    note_source(xnli_repo)
    for lang in ("en", "zh"):
        dataset = _load(xnli_repo, lang, revision=sources[xnli_repo].get("revision"))
        _add(suite_rows, suite_manifest, f"xnli_{lang}", xnli_repo, lang, "test", lang,
             dataset, lambda row: str(row["label"]), xnli_zh_text if lang == "zh" else xnli_label_text,
             "What is the relationship between the premise and hypothesis?",
             per_label or 100)

    fixed_specs = [
        ("sst5", "SetFit/sst5", None, "en", ["very negative", "negative", "neutral", "positive", "very positive"],
         "Which sentiment best describes the text?", lambda row: str(row["label"]), None),
        ("emotion", "dair-ai/emotion", "split", "en", ["sadness", "joy", "love", "anger", "fear", "surprise"],
         "Which emotion is most strongly expressed in the text?", lambda row: str(row["label"]), None),
        ("prompt_injections", "deepset/prompt-injections", None, "en", ["no injection", "instruction injection"],
         "Does this text attempt to inject or override instructions for an AI system?", lambda row: str(row["label"]), None),
        ("toxic_chat_jailbreak", "lmsys/toxic-chat", "toxicchat0124", "en", ["not a jailbreak", "jailbreak attempt"],
         "Does this prompt try to make an AI assistant ignore its rules or system instructions?", lambda row: str(int(row["jailbreaking"])), "jailbreaking"),
        ("toxic_chat_toxicity", "lmsys/toxic-chat", "toxicchat0124", "en", ["not toxic", "toxic"],
         "Is this text toxic, rude, or disrespectful?", lambda row: str(int(row["toxicity"])), "toxicity"),
    ]
    for suite, repo, config, lang, display, question, labeler, toxic_field in fixed_specs:
        note_source(repo)
        dataset = _load(repo, config, revision=sources[repo].get("revision"))
        if suite == "sst5":
            label_text = {str(i): display[i] for i in range(len(display))}
            budget = per_label or 100
        elif suite == "emotion":
            label_text = {str(i): display[i] for i in range(len(display))}
            budget = per_label or 100
        elif suite == "prompt_injections":
            label_text = {"0": display[0], "1": display[1]}
            budget = per_label or 100
        else:
            label_text = {"0": display[0], "1": display[1]}
            budget = per_label or 150
            dataset = [row for row in dataset if row.get("user_input") and row.get("jailbreaking") is not None and row.get("toxicity") is not None]
            dataset = [{**row, "text": row["user_input"]} for row in dataset]
        _add(suite_rows, suite_manifest, suite, repo, config, "test", lang, dataset,
             labeler, label_text, question, budget)

    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite {output_dir}")
    output_dir.mkdir(parents=True)
    cases_path = output_dir / "cases.jsonl"
    with cases_path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in suite_rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    manifest = {
        "format": "erabi-laya-neutral-choice-v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "seed": SEED,
        "max_choices": MAX_CHOICES,
        "sampling": "class-balanced sampling from public test splits; fixed candidate order per case",
        "input_policy": {"max_context_chars": MAX_CONTEXT_CHARS,
                         "contact_and_credential_patterns_redacted": True,
                         "char_truncation_is_recorded_per_case": True},
        "sources": sources,
        "suites": suite_manifest,
        "total_cases": len(suite_rows),
        "cases_sha256": hashlib.sha256(cases_path.read_bytes()).hexdigest(),
        "neutrality_note": (
            "Laya repository describes the selected test sources as held out where applicable. "
            "ERABI training-data overlap still requires a separate exact-text audit before treating "
            "the score comparison as fully neutral."
        ),
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"cases": len(suite_rows), "cases_path": str(cases_path),
                      "manifest_path": str(output_dir / "manifest.json"),
                      "cases_sha256": manifest["cases_sha256"]}, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "runs" / "neutral_public_benchmark_20260929")
    parser.add_argument("--per-label", type=int,
                        help="Override each suite's per-class sample size (normal defaults: MASSIVE 8; other suites 100; Toxic Chat 150). Use 1 for a smoke build.")
    args = parser.parse_args()
    if args.per_label is not None and args.per_label < 1:
        parser.error("--per-label must be positive")
    build(args.per_label, args.output_dir.resolve())


if __name__ == "__main__":
    main()
