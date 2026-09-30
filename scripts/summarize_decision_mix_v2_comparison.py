"""Create the matched ERABI baseline/selected/Laya Decision Mix V2 comparison."""
from __future__ import annotations

import argparse
import json
import random
import statistics
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def bootstrap_difference(left: dict[str, dict], right: dict[str, dict], seed: int = 20260930,
                         iterations: int = 10000) -> dict:
    common = sorted(set(left) & set(right))
    groups: dict[str, list[str]] = {}
    for row_id in common:
        groups.setdefault(left[row_id]["canonical_group_id"], []).append(row_id)
    group_ids = sorted(groups)
    rng = random.Random(seed)
    values = []
    for _ in range(iterations):
        sampled = [rng.choice(group_ids) for _ in group_ids]
        ids = [row_id for group_id in sampled for row_id in groups[group_id]]
        values.append(statistics.mean(left[row_id]["correct"] for row_id in ids)
                      - statistics.mean(right[row_id]["correct"] for row_id in ids))
    values.sort()
    return {"difference": statistics.mean(row["correct"] for row in left.values())
                          - statistics.mean(row["correct"] for row in right.values()),
            "cluster_groups": len(group_ids), "iterations": iterations,
            "ci95": [values[int(.025 * iterations)], values[int(.975 * iterations)]]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--laya", type=Path, required=True, help="Laya summary.json")
    parser.add_argument("--jev", type=Path, help="Optional Jev summary.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    erabi = load_json(args.run_dir / "summary.json")
    baseline_rows = load_jsonl(args.run_dir / "baseline_final" / "predictions.jsonl")
    selected_rows = load_jsonl(args.run_dir / "selected_final" / "predictions.jsonl")
    laya = load_json(args.laya)
    laya_rows = laya["records"]
    systems = {
        "ERABI before": {row["id"]: row for row in baseline_rows},
        "ERABI after": {row["id"]: row for row in selected_rows},
        "Laya reviewed": {row["id"]: row for row in laya_rows},
    }
    jev = load_json(args.jev) if args.jev else None
    if jev:
        systems["Jev 1.13"] = {row["id"]: row for row in jev["records"]}
    id_sets = [set(rows) for rows in systems.values()]
    if any(ids != id_sets[0] for ids in id_sets[1:]):
        raise ValueError("systems did not score exactly the same row IDs")
    for row_id in id_sets[0]:
        targets = {rows[row_id]["target"] for rows in systems.values()}
        if len(targets) != 1:
            raise ValueError(f"target mismatch for {row_id}")

    summaries = {
        "ERABI before": erabi["baseline_final"],
        "ERABI after": erabi["selected_final"],
        "Laya reviewed": laya["metrics"],
    }
    if jev:
        summaries["Jev 1.13"] = jev["metrics"]
    rows = []
    for name, summary in summaries.items():
        overall = summary["overall"]
        rows.append({"system": name, "correct": overall["correct_count"], "total": overall["count"],
                     "accuracy": overall["accuracy"], "family_macro": summary["family_macro_accuracy"],
                     "group_all_correct": summary["canonical_group_all_correct"]["rate"],
                     "mean_nll": overall["mean_nll"], "mean_brier": overall["mean_brier"]})
    comparison = {
        "rows": rows,
        "paired_group_bootstrap": {
            "after_minus_before": bootstrap_difference(systems["ERABI after"], systems["ERABI before"]),
            "after_minus_laya": bootstrap_difference(systems["ERABI after"], systems["Laya reviewed"]),
            "before_minus_laya": bootstrap_difference(systems["ERABI before"], systems["Laya reviewed"]),
        },
        "by_family": {
            family: {name: summary["by_family"][family]["accuracy"] for name, summary in summaries.items()}
            for family in sorted(next(iter(summaries.values()))["by_family"])
        },
        "caveats": [
            "The labels are provisional synthetic agreement, not independent human gold.",
            "ERABI after was trained on the Decision Mix V2 train split; Laya was not.",
            "Rows share canonical groups, so uncertainty uses paired canonical-group resampling.",
            "A single seed and run do not establish general superiority.",
        ],
    }
    if jev:
        comparison["caveats"].append(
            "Jev was called as the remote OrcaRouter deployment; its weights and training data are not inspectable here."
        )
        comparison["paired_group_bootstrap"].update({
            "jev_minus_after": bootstrap_difference(systems["Jev 1.13"], systems["ERABI after"]),
            "jev_minus_before": bootstrap_difference(systems["Jev 1.13"], systems["ERABI before"]),
            "jev_minus_laya": bootstrap_difference(systems["Jev 1.13"], systems["Laya reviewed"]),
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.with_suffix(".json").write_text(json.dumps(comparison, ensure_ascii=False, indent=2) + "\n",
                                                encoding="utf-8")
    lines = ["# Decision Mix V2 matched comparison", "", "| System | Correct | Accuracy | Family macro | Group all-correct | NLL | Brier |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(f"| {row['system']} | {row['correct']}/{row['total']} | {row['accuracy']:.2%} | "
                     f"{row['family_macro']:.2%} | {row['group_all_correct']:.2%} | "
                     f"{row['mean_nll']:.4f} | {row['mean_brier']:.4f} |")
    names = list(summaries)
    lines += ["", "## Accuracy by family", "", "| Family | " + " | ".join(names) + " |",
              "|---|" + "---:|" * len(names)]
    for family, values in comparison["by_family"].items():
        lines.append("| " + family + " | " + " | ".join(f"{values[name]:.2%}" for name in names) + " |")
    lines += ["", "## Paired canonical-group bootstrap", ""]
    for name, value in comparison["paired_group_bootstrap"].items():
        lines.append(f"- {name}: {value['difference']:+.2%}, 95% CI [{value['ci95'][0]:+.2%}, {value['ci95'][1]:+.2%}]")
    lines += ["", "## Caveats", ""] + [f"- {text}" for text in comparison["caveats"]]
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(comparison, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
