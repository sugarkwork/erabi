"""Check matching runs and write a per-suite Markdown comparison table."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def fmt(value, digits=3):
    return "—" if value is None else f"{value:.{digits}f}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--erabi", type=Path, required=True)
    parser.add_argument("--laya", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    erabi = json.loads(args.erabi.read_text(encoding="utf-8"))
    laya = json.loads(args.laya.read_text(encoding="utf-8"))
    if erabi["system"] != "erabi" or laya["system"] != "laya":
        raise ValueError("Run files must be ERABI and Laya respectively")
    if erabi["cases_sha256"] != laya["cases_sha256"]:
        raise ValueError("Runs used different case files")
    erabi_ids = [row["id"] for row in erabi["records"]]
    laya_ids = [row["id"] for row in laya["records"]]
    if erabi_ids != laya_ids:
        raise ValueError("Runs have different case IDs or case ordering")
    if set(erabi["suites"]) != set(laya["suites"]):
        raise ValueError("Runs have different suite sets")

    lines = [
        "# ERABI and Laya public benchmark comparison", "",
        f"Cases SHA256: `{erabi['cases_sha256']}` ({erabi['cases']} cases).",
        "Both runs used the same ordered JSONL cases. Accuracy uses source labels; chance is the mean 1/k baseline.",
        "", "| Dataset | N | ERABI accuracy | Laya accuracy | ERABI macro-F1 | Laya macro-F1 | Chance | ERABI p50 ms | Laya p50 ms | ERABI req/s | Laya req/s | ERABI VRAM delta MiB* | Laya VRAM delta MiB* | ERABI RSS peak MiB | Laya RSS peak MiB | GPU temp °C E/L | SM clock MHz E/L |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in sorted(erabi["suites"]):
        e, l = erabi["suites"][name], laya["suites"][name]
        if e["n"] != l["n"]:
            raise ValueError(f"Suite row count differs: {name}")
        ev = e["gpu_sample_summary"].get("memory_used_mib", {}).get("max", erabi["gpu_total_memory_mib"]["peak_sampled"])
        lv = l["gpu_sample_summary"].get("memory_used_mib", {}).get("max", laya["gpu_total_memory_mib"]["peak_sampled"])
        ebase = erabi["gpu_total_memory_mib"]["before_model_load"]["memory_used_mib"]
        lbase = laya["gpu_total_memory_mib"]["before_model_load"]["memory_used_mib"]
        et = e["gpu_sample_summary"].get("temperature_c", {}).get("median")
        lt = l["gpu_sample_summary"].get("temperature_c", {}).get("median")
        ec = e["gpu_sample_summary"].get("sm_clock_mhz", {}).get("median")
        lc = l["gpu_sample_summary"].get("sm_clock_mhz", {}).get("median")
        lines.append(
            f"| {name} | {e['n']} | {e['accuracy']:.3f} | {l['accuracy']:.3f} | "
            f"{e['macro_f1']:.3f} | {l['macro_f1']:.3f} | {e['chance_accuracy_mean']:.3f} | "
            f"{e['latency_ms']['p50']:.2f} | {l['latency_ms']['p50']:.2f} | "
            f"{e['throughput_requests_per_second']:.2f} | {l['throughput_requests_per_second']:.2f} | "
            f"{fmt(ev - ebase, 0)} | {fmt(lv - lbase, 0)} | "
            f"{fmt(e['process_rss_peak_mib'], 0)} | {fmt(l['process_rss_peak_mib'], 0)} | "
            f"{fmt(et, 1)} / {fmt(lt, 1)} | {fmt(ec, 0)} / {fmt(lc, 0)} |"
        )
    lines.extend([
        "", "## Overall accuracy", "",
        "| System | Correct / total | Micro accuracy | Mean suite accuracy | Mean latency ms |",
        "|---|---:|---:|---:|---:|",
    ])
    for run in (erabi, laya):
        correct = sum(record["correct"] for record in run["records"])
        mean_suite = sum(suite["accuracy"] for suite in run["suites"].values()) / len(run["suites"])
        lines.append(
            f"| {run['system']} | {correct}/{run['cases']} | {correct / run['cases']:.4f} | "
            f"{mean_suite:.4f} | {1000 / run['overall_throughput_requests_per_second']:.2f} |"
        )
    lines.extend([
        "", "## Initialization and device summary", "",
        f"| System | Initialization s | Throughput req/s | RSS before / loaded / sampled peak MiB | GPU used baseline / after load / sampled peak MiB |",
        "|---|---:|---:|---:|---:|",
    ])
    for run in (erabi, laya):
        rss = run["process_rss_mib"]
        gpu = run["gpu_total_memory_mib"]
        before = gpu["before_model_load"].get("memory_used_mib") if gpu["before_model_load"] else None
        loaded = gpu["after_model_load"].get("memory_used_mib") if gpu["after_model_load"] else None
        lines.append(f"| {run['system']} | {run['engine_initialization_seconds']:.2f} | {run['overall_throughput_requests_per_second']:.2f} | "
                     f"{fmt(rss['before_model_load'], 0)} / {fmt(rss['after_model_load'], 0)} / {fmt(rss['peak_sampled'], 0)} | "
                     f"{fmt(before, 0)} / {fmt(loaded, 0)} / {fmt(gpu['peak_sampled'], 0)} |")
    lines.extend([
        "", "## Limits", "",
        "GPU memory values come from whole-device `nvidia-smi`, include unrelated processes, and are sampled every 0.5 seconds; they are not per-process allocations and short peaks can be missed.",
        "*Per-suite VRAM deltas subtract the whole-device pre-load baseline from the whole-device peak sampled during that suite. They remain approximate because unrelated processes can change during a run.",
        "ERABI rejects inputs above 512 tokenizer tokens. Laya token audit reports actual context truncation, its per-option 48-token maximum, the shared option budget, and collapsed choices.",
        "Laya's training exclusions are based on its published benchmark notes. Verify ERABI's exact training-data overlap before calling the comparison fully neutral.",
        "", "Per-suite macro-F1, latency percentiles, GPU temperature and SM-clock samples are retained in the two JSON run files.",
    ])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(args.output.resolve())


if __name__ == "__main__":
    main()
