"""Aggregate error tendencies without exporting private question text."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def length_bucket(tokens: int) -> str:
    if tokens <= 256:
        return "000-256"
    if tokens <= 512:
        return "257-512"
    if tokens <= 768:
        return "513-768"
    return "769-1024"


def aggregate(rows: list[dict]) -> dict:
    fields = ("language", "subject", "exam", "length", "choice_count")
    stats = {field: defaultdict(Counter) for field in fields}
    transitions = Counter()
    for row in rows:
        source = row["source"]
        values = {
            "language": row["language"],
            "subject": source.get("subject", "unknown"),
            "exam": source.get("exam", "unknown"),
            "length": length_bucket(row["input_tokens"]),
            "choice_count": str(len(row["choices"])),
        }
        for field, value in values.items():
            stats[field][value]["total"] += 1
            stats[field][value]["correct"] += int(row["correct"])
        if not row["correct"]:
            transitions[(row["target"], row["predicted"])] += 1
    output = {}
    for field in fields:
        output[field] = []
        for value, count in stats[field].items():
            output[field].append({
                "value": value,
                "total": count["total"],
                "correct": count["correct"],
                "accuracy": round(count["correct"] / count["total"], 4),
            })
        output[field].sort(key=lambda item: (item["accuracy"], -item["total"], item["value"]))
    output["wrong_choice_transitions"] = [
        {"target": target, "predicted": predicted, "count": count}
        for (target, predicted), count in transitions.most_common()
    ]
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)

    from erabi.inference import GLiClassEngine
    from erabi.schema import ChoiceRequest

    engine = GLiClassEngine(str(args.model_dir), device=args.device, max_tokens=1024)
    engine.pipe.pipe.max_length = 1024
    results = []
    for row in read_jsonl(args.input):
        response = engine.predict(ChoiceRequest.from_dict(row))
        results.append({
            "id": row["id"],
            "source": row["source"],
            "language": row["language"],
            "input_tokens": response.usage.input_tokens,
            "choices": row["choices"],
            "target": row["target"]["choice_id"],
            "predicted": response.best_candidate_id,
            "correct": response.best_candidate_id == row["target"]["choice_id"],
        })
    report = {
        "model_dir": str(args.model_dir),
        "input": str(args.input),
        "count": len(results),
        "correct": sum(row["correct"] for row in results),
        "aggregate": aggregate(results),
        "rows": results,
        "privacy": "No question or context text is stored in this report.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "rows"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
