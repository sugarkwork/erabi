"""Summarize local reports without exposing benchmark inputs or raw model responses."""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from pathlib import Path

from scripts.run_neutral_benchmark import percentile


def metrics(rows):
    times = [r["elapsed_ms"] for r in rows]
    return {"n": len(rows), "correct": sum(r["correct"] for r in rows),
            "id_sha256": hashlib.sha256("\n".join(sorted(r["id"] for r in rows)).encode()).hexdigest(),
            "accuracy": statistics.mean(r["correct"] for r in rows),
            "p50_ms": percentile(times, .5), "p95_ms": percentile(times, .95),
            "requests_per_second": 1000 / statistics.mean(times)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--match-cases", type=Path, help="Prediction JSONL defining the exact common case IDs")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Summary preserved; select a new output")
    matched_ids = None
    if args.match_cases:
        reference = [json.loads(line) for line in args.match_cases.read_text(encoding="utf-8").splitlines() if line.strip()]
        matched_ids = {row["id"] for row in reference}
        if not reference or len(matched_ids) != len(reference):
            raise ValueError("Empty or duplicate reference case IDs")
    systems = []
    for path in args.reports:
        report = json.loads(path.read_text(encoding="utf-8"))
        rows = [json.loads(line) for line in path.with_suffix(".jsonl").read_text(encoding="utf-8").splitlines()]
        if len(rows) != report["overall"]["n"] or sum(r["correct"] for r in rows) != report["overall"]["correct"]:
            raise ValueError("Report/journal mismatch")
        if matched_ids is not None:
            rows = [row for row in rows if row["id"] in matched_ids]
            if len(rows) != len(matched_ids):
                raise ValueError("Report is missing common cases")
        prefix_metrics = {}
        for prefix in ("decision/", "public/"):
            selected = [r for r in rows if r["domain"].startswith(prefix)]
            if selected:
                prefix_metrics[prefix[:-1]] = metrics(selected)
        before = report["gpu_before"]
        gpu_delta = report["gpu_peak_mib"] - before["memory_used_mib"] if before else None
        samples = report["gpu_samples"]
        systems.append({"report": path.name, "system": report["system"], "mode": report["mode"],
                        "measurement_case_count": report["overall"]["n"],
                        "sources": report["sources"], "datasets": prefix_metrics,
                        "by_domain": {domain: metrics([row for row in rows if row["domain"] == domain]) for domain in sorted({row["domain"] for row in rows})}, "metadata": report["metadata"],
                        "init_seconds": report["init_seconds"], "peak_rss_mib": report["peak_rss_mib"],
                        "whole_gpu_peak_minus_start_mib": gpu_delta,
                        "torch_peak_allocated_mib": report["torch_peak_allocated_mib"],
                        "torch_peak_reserved_mib": report["torch_peak_reserved_mib"],
                        "gpu_temperature_range_c": [min(s["temperature_c"] for s in samples), max(s["temperature_c"] for s in samples)] if samples else None,
                        "gpu_clock_median_mhz": statistics.median(s["sm_clock_mhz"] for s in samples) if samples else None,
                        "versions": report["versions"]})
    # Results on unequal subsets must remain separate, not be ranked as matching tests.
    result = {"systems": systems, "matched_cases": len(matched_ids) if matched_ids is not None else None,
              "note": "Only compare accuracy on matching dataset counts/IDs. Filtered latency uses original calls; initialization/memory retain original full run (measurement_case_count). GPU delta is whole-device sampling, not process allocation."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for system in systems:
        print(json.dumps({k: system[k] for k in ("report", "datasets", "init_seconds", "peak_rss_mib", "whole_gpu_peak_minus_start_mib")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
