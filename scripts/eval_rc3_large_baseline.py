"""Evaluate untrained knowledgator/gliclass-instruct-large-v1.0 on RC3 Bridge and Core benchmarks.

Provides the zero-shot / untreated foundation baseline for Level 4 mid-size backbone.
"""

from __future__ import annotations

import datetime
import json
import logging
from pathlib import Path
import sys
import time

import torch

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from erabi.inference import GLiClassEngine
from scripts.train_rc3 import evaluate_records, load_jsonl

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.eval_large_baseline")

MODEL_ID = "knowledgator/gliclass-instruct-large-v1.0"
BRIDGE_FILE = ROOT / "data" / "rc3_bridge" / "rc3_bridge_benchmark.jsonl"
EVAL_V2_FILE = ROOT / "data" / "m3_3_v2" / "eval_v2.jsonl"
OUT_DIR = ROOT / "runs" / "rc3_large_baseline"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    logger.info(f"Loading {MODEL_ID} on {device}...")
    t0 = time.time()
    engine = GLiClassEngine(model_id=MODEL_ID, device=device)
    logger.info(f"Loaded in {time.time() - t0:.2f}s")

    # Evaluate Bridge Benchmark
    logger.info("Evaluating RC3 Bridge Benchmark (480 cases)...")
    bridge_records = load_jsonl(BRIDGE_FILE)
    t_b0 = time.time()
    bridge_results = evaluate_records(engine, bridge_records, test_permutation=True, seed=42)
    bridge_time = time.time() - t_b0
    logger.info(f"Bridge Benchmark Complete in {bridge_time:.1f}s:")
    logger.info(f"  Overall Acc: {bridge_results['accuracy']*100:.2f}% ({bridge_results['correct']}/{bridge_results['total_cases']})")
    logger.info(f"  Paired Both: {bridge_results['paired_both_rate']*100:.2f}% ({bridge_results['paired_both']}/{bridge_results['paired_total']})")
    logger.info(f"  Permutation Consistency: {bridge_results['permutation_consistency']*100:.2f}%")

    for fam, s in bridge_results["by_family"].items():
        logger.info(f"    - {fam:25s}: {s['accuracy']*100:.2f}% ({s['correct']}/{s['total']})")

    # Evaluate eval_v2 (Core retention)
    logger.info("Evaluating eval_v2 Core Benchmark (200 cases)...")
    ev2_records = load_jsonl(EVAL_V2_FILE)
    ev2_results = evaluate_records(engine, ev2_records, test_permutation=False)
    logger.info(f"eval_v2 Acc: {ev2_results['accuracy']*100:.2f}% ({ev2_results['correct']}/{ev2_results['total_cases']})")

    out_data = {
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "model_id": MODEL_ID,
        "bridge_accuracy": bridge_results["accuracy"],
        "bridge_paired_both_rate": bridge_results["paired_both_rate"],
        "bridge_permutation_consistency": bridge_results["permutation_consistency"],
        "eval_v2_accuracy": ev2_results["accuracy"],
        "bridge_by_family": bridge_results["by_family"],
        "bridge_by_k": bridge_results["by_k"],
        "time_seconds": bridge_time,
    }

    out_json = OUT_DIR / "large_baseline_results.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved results to {out_json}")


if __name__ == "__main__":
    main()
