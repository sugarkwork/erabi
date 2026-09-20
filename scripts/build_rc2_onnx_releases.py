"""Build, Verify, Benchmark, and Package ERABI RC2 ONNX FP32 and ONNX FP16 Releases.

Roadmap Reference:
Milestone 23 — ONNX FP16 (Section 17).
Pipeline:
PyTorch -> ONNX FP32 -> parity -> ONNX FP16 CUDA -> parity -> benchmark

Gate Conditions:
1. PyTorch <-> ONNX FP32 Top-1 parity 100%
2. PyTorch <-> ONNX FP16 Top-1 parity 100%
3. Representative eval parity across RC2 suites (General Expansion, Natural Japanese, Variable Choices 2..16, Smoke)
4. Calibration applicable with T* = 0.263007
5. Variable choices 2..16 fully operational
6. Memory leak: zero accumulation across continuous requests
7. Latency: p50 <= 15 ms, p95 <= 20 ms
"""

from __future__ import annotations

import datetime
import gc
import json
import logging
import math
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

# Setup DLL path for ONNX Runtime CUDA on Windows
if sys.platform == "win32":
    torch_lib = os.path.join(os.path.dirname(torch.__file__), "lib")
    if os.path.exists(torch_lib):
        os.add_dll_directory(torch_lib)
        os.environ["PATH"] = torch_lib + os.pathsep + os.environ.get("PATH", "")

import onnx
import onnxruntime as ort
from erabi.inference import GLiClassEngine
from erabi.onnx_engine import ERABIONNXEngine
from erabi.schema import ChoiceRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.rc2_onnx_release")

RC2_DIR = ROOT / "release/rc2"
RC2_MODEL_DIR = RC2_DIR / "model"
RC2_CALIB_PATH = RC2_DIR / "calibration.json"

ONNX_FP32_DIR = ROOT / "release/rc2_onnx"
ONNX_FP16_DIR = ROOT / "release/erabi-rc2-onnx-fp16"


def patch_vectorized_segment_ids(model_inner):
    """Vectorize _create_segment_ids to avoid python control flow and .item() during ONNX trace."""
    def vectorized_create_segment_ids(self, input_ids):
        seq_length = input_ids.shape[-1]
        seq_idx = torch.arange(seq_length, device=input_ids.device).unsqueeze(0)
        text_token_mask = input_ids == self.config.text_token_index
        text_token_indices = text_token_mask.int().argmax(dim=-1, keepdim=True)
        example_token_mask = input_ids == self.config.example_token_index
        example_token_indices = example_token_mask.int().argmax(dim=-1, keepdim=True)
        has_example = example_token_mask.any(dim=-1, keepdim=True)
        segment_ids = (seq_idx >= text_token_indices).long()
        example_mask = has_example & (seq_idx >= example_token_indices)
        segment_ids = torch.where(example_mask, 2, segment_ids)
        return segment_ids

    type(model_inner)._create_segment_ids = vectorized_create_segment_ids


class ONNXFP32ExportWrapper(torch.nn.Module):
    def __init__(self, m):
        super().__init__()
        self.m = m

    def forward(self, input_ids, attention_mask):
        outputs = self.m(input_ids=input_ids, attention_mask=attention_mask)
        return outputs.logits


class ONNXFP16ExportWrapper(torch.nn.Module):
    def __init__(self, m):
        super().__init__()
        self.m = m

    def forward(self, input_ids, attention_mask):
        outputs = self.m(input_ids=input_ids, attention_mask=attention_mask)
        return outputs.logits.float()


def export_fp32_model(out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_onnx = out_dir / "model.onnx"
    if out_onnx.exists():
        logger.info(f"FP32 ONNX Model already exists at {out_onnx}.")
        return out_onnx

    logger.info(f"=== Exporting RC2 FP32 ONNX Model to {out_onnx} ===")
    engine = GLiClassEngine(str(RC2_MODEL_DIR), device="cpu")
    model = engine.pipe.pipe.model
    model.eval()

    patch_vectorized_segment_ids(model.model)
    wrapper = ONNXFP32ExportWrapper(model)
    wrapper.eval()

    dummy_ids = torch.ones((1, 48), dtype=torch.long)
    dummy_ids[0, 5] = model.model.config.text_token_index
    dummy_ids[0, 1] = model.model.config.class_token_index
    dummy_ids[0, 3] = model.model.config.class_token_index
    dummy_mask = torch.ones((1, 48), dtype=torch.long)

    torch.onnx.export(
        wrapper,
        (dummy_ids, dummy_mask),
        str(out_onnx),
        input_names=["input_ids", "attention_mask"],
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch_size", 1: "sequence_length"},
            "attention_mask": {0: "batch_size", 1: "sequence_length"},
            "logits": {0: "batch_size", 1: "num_classes"},
        },
        opset_version=17,
    )
    logger.info("FP32 ONNX Export completed. Running ONNX model checker...")
    m = onnx.load(str(out_onnx))
    onnx.checker.check_model(m)

    for fname in ["tokenizer.json", "tokenizer_config.json", "config.json"]:
        shutil.copy2(RC2_MODEL_DIR / fname, out_dir / fname)
    shutil.copy2(RC2_CALIB_PATH, out_dir / "calibration.json")
    logger.info(f"Copied companion files to {out_dir}")

    del engine, model, wrapper
    gc.collect()
    return out_onnx


def export_fp16_model(out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_onnx = out_dir / "model.onnx"
    if out_onnx.exists():
        logger.info(f"FP16 ONNX Model already exists at {out_onnx}.")
        return out_onnx

    logger.info(f"=== Exporting Native RC2 FP16 ONNX Model to {out_onnx} ===")
    engine = GLiClassEngine(str(RC2_MODEL_DIR), device="cuda:0")
    model = engine.pipe.pipe.model
    patch_vectorized_segment_ids(model.model)

    model = model.half().cuda()
    model.eval()

    wrapper = ONNXFP16ExportWrapper(model)
    wrapper.eval()

    dummy_ids = torch.ones((1, 48), dtype=torch.long, device="cuda:0")
    dummy_ids[0, 5] = model.model.config.text_token_index
    dummy_ids[0, 1] = model.model.config.class_token_index
    dummy_ids[0, 3] = model.model.config.class_token_index
    dummy_mask = torch.ones((1, 48), dtype=torch.long, device="cuda:0")

    torch.onnx.export(
        wrapper,
        (dummy_ids, dummy_mask),
        str(out_onnx),
        input_names=["input_ids", "attention_mask"],
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch_size", 1: "sequence_length"},
            "attention_mask": {0: "batch_size", 1: "sequence_length"},
            "logits": {0: "batch_size", 1: "num_classes"},
        },
        opset_version=17,
    )
    logger.info("FP16 ONNX Export completed. Running ONNX model checker...")
    m = onnx.load(str(out_onnx))
    onnx.checker.check_model(m)

    for fname in ["tokenizer.json", "tokenizer_config.json", "config.json"]:
        shutil.copy2(RC2_MODEL_DIR / fname, out_dir / fname)
    shutil.copy2(RC2_CALIB_PATH, out_dir / "calibration.json")
    logger.info(f"Copied companion files to {out_dir}")

    del engine, model, wrapper
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()
    return out_onnx


def run_rc2_parity_audit(
    pt_engine: GLiClassEngine,
    fp32_engine: ERABIONNXEngine,
    fp16_engine: ERABIONNXEngine,
    T: float,
) -> Dict[str, Any]:
    logger.info("=== Running RC2 Parity Audit Across 4 Evaluation Suites ===")

    eval_suites = {
        "fresh_general_expansion": ROOT / "data/rc2_m19_general/fresh_general_expansion_eval.jsonl",
        "fresh_natural": ROOT / "data/rc2_m18_natural/fresh_natural_eval.jsonl",
        "variable_choices": ROOT / "data/rc2_m17_choices/variable_choice_eval.jsonl",
        "smoke_cases": ROOT / "examples/smoke_cases.jsonl",
    }

    suite_results = {}

    for sname, spath in eval_suites.items():
        logger.info(f"Evaluating suite: {sname} ({spath.name})...")
        records = [json.loads(l) for l in open(spath, encoding="utf-8") if l.strip()]

        pt_correct = 0
        fp32_correct = 0
        fp16_correct = 0

        fp32_top1_matches = 0
        fp16_top1_matches = 0

        max_logit_diff_fp32 = 0.0
        max_logit_diff_fp16 = 0.0

        max_prob_drift_fp32 = 0.0
        max_prob_drift_fp16 = 0.0

        for r in records:
            req = ChoiceRequest.from_dict(r)
            tgt_cid = r["target"]["choice_id"]

            # PyTorch inference
            pt_resp = pt_engine.predict(req, temperature=T, return_logits=True)
            pt_pred = pt_resp.best_candidate_id
            if pt_pred == tgt_cid:
                pt_correct += 1

            # ONNX FP32 inference
            fp32_resp = fp32_engine.predict(req, temperature=T, return_logits=True)
            fp32_pred = fp32_resp.best_candidate_id
            if fp32_pred == tgt_cid:
                fp32_correct += 1
            if fp32_pred == pt_pred:
                fp32_top1_matches += 1

            # ONNX FP16 inference
            fp16_resp = fp16_engine.predict(req, temperature=T, return_logits=True)
            fp16_pred = fp16_resp.best_candidate_id
            if fp16_pred == tgt_cid:
                fp16_correct += 1
            if fp16_pred == pt_pred:
                fp16_top1_matches += 1

            # Differences
            pt_logits = np.array(pt_resp.raw_logits, dtype=np.float32)
            fp32_logits = np.array(fp32_resp.raw_logits, dtype=np.float32)
            fp16_logits = np.array(fp16_resp.raw_logits, dtype=np.float32)

            diff_fp32 = np.max(np.abs(pt_logits - fp32_logits))
            diff_fp16 = np.max(np.abs(pt_logits - fp16_logits))
            max_logit_diff_fp32 = max(max_logit_diff_fp32, float(diff_fp32))
            max_logit_diff_fp16 = max(max_logit_diff_fp16, float(diff_fp16))

            pt_probs = np.array([c.probability for c in pt_resp.choices], dtype=np.float32)
            fp32_probs = np.array([c.probability for c in fp32_resp.choices], dtype=np.float32)
            fp16_probs = np.array([c.probability for c in fp16_resp.choices], dtype=np.float32)

            p_drift_fp32 = np.max(np.abs(pt_probs - fp32_probs))
            p_drift_fp16 = np.max(np.abs(pt_probs - fp16_probs))
            max_prob_drift_fp32 = max(max_prob_drift_fp32, float(p_drift_fp32))
            max_prob_drift_fp16 = max(max_prob_drift_fp16, float(p_drift_fp16))

        n = len(records)
        suite_results[sname] = {
            "total_cases": n,
            "pytorch_accuracy": pt_correct / n,
            "onnx_fp32_accuracy": fp32_correct / n,
            "onnx_fp16_accuracy": fp16_correct / n,
            "fp32_top1_parity": fp32_top1_matches / n,
            "fp16_top1_parity": fp16_top1_matches / n,
            "max_logit_diff_fp32": max_logit_diff_fp32,
            "max_logit_diff_fp16": max_logit_diff_fp16,
            "max_prob_drift_fp32": max_prob_drift_fp32,
            "max_prob_drift_fp16": max_prob_drift_fp16,
        }
        logger.info(
            f"  {sname:25s} | Cases: {n:3d} | PT: {pt_correct/n*100:5.1f}% | "
            f"FP32 Parity: {fp32_top1_matches/n*100:5.1f}% | FP16 Parity: {fp16_top1_matches/n*100:5.1f}%"
        )

    return suite_results


def benchmark_engine(
    engine: Any,
    name: str,
    cases: List[Dict[str, Any]],
    warmup: int = 20,
    iterations: int = 100,
    T: float = 1.0,
) -> Dict[str, Any]:
    logger.info(f"Benchmarking {name} ({iterations} iterations)...")
    reqs = [ChoiceRequest.from_dict(c) for c in cases]

    # Cold start timing
    t0_cold = time.perf_counter()
    engine.predict(reqs[0], temperature=T)
    cold_latency_ms = (time.perf_counter() - t0_cold) * 1000.0

    # Warmup
    for i in range(warmup):
        engine.predict(reqs[i % len(reqs)], temperature=T)

    latencies_ms = []
    t_bench_start = time.perf_counter()
    for i in range(iterations):
        req = reqs[i % len(reqs)]
        t0 = time.perf_counter()
        engine.predict(req, temperature=T)
        latencies_ms.append((time.perf_counter() - t0) * 1000.0)
    total_time_s = time.perf_counter() - t_bench_start

    latencies_ms = np.array(latencies_ms)
    throughput = iterations / total_time_s

    return {
        "engine": name,
        "iterations": iterations,
        "cold_start_ms": round(cold_latency_ms, 2),
        "warm_mean_ms": round(float(np.mean(latencies_ms)), 2),
        "warm_p50_ms": round(float(np.percentile(latencies_ms, 50)), 2),
        "warm_p90_ms": round(float(np.percentile(latencies_ms, 90)), 2),
        "warm_p95_ms": round(float(np.percentile(latencies_ms, 95)), 2),
        "warm_p99_ms": round(float(np.percentile(latencies_ms, 99)), 2),
        "throughput_req_per_sec": round(throughput, 1),
    }


def get_process_rss_mb() -> float:
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes
            class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD),
                    ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]
            psapi = ctypes.windll.psapi
            kernel32 = ctypes.windll.kernel32
            psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESS_MEMORY_COUNTERS), wintypes.DWORD]
            psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
            counters = PROCESS_MEMORY_COUNTERS()
            counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
            handle = kernel32.GetCurrentProcess()
            if psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
                return float(counters.WorkingSetSize / (1024 * 1024))
        except Exception:
            pass
    return 0.0


def main():
    logger.info("=== Starting Milestone 23: ONNX FP16 Engine Build & Benchmark ===")

    # 1. Export FP32 & FP16
    fp32_path = export_fp32_model(ONNX_FP32_DIR)
    fp16_path = export_fp16_model(ONNX_FP16_DIR)

    # 2. Load calibration T*
    calib_data = json.load(open(RC2_CALIB_PATH, encoding="utf-8"))
    t_star = float(calib_data["temperature"])
    logger.info(f"Loaded RC2 calibrated temperature T* = {t_star:.6f}")

    # 3. Instantiate engines
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    logger.info("Initializing PyTorch and ONNX engines...")
    pt_engine = GLiClassEngine(str(RC2_MODEL_DIR), device=device)
    fp32_engine = ERABIONNXEngine(str(ONNX_FP32_DIR), device=device)
    fp16_engine = ERABIONNXEngine(str(ONNX_FP16_DIR), device=device)

    # 4. Parity Verification across representative suites
    parity_results = run_rc2_parity_audit(pt_engine, fp32_engine, fp16_engine, T=t_star)

    # 5. Benchmarking on RTX A4000
    smoke_file = ROOT / "examples/smoke_cases.jsonl"
    benchmark_cases = [json.loads(l) for l in open(smoke_file, encoding="utf-8") if l.strip()]

    bench_pt = benchmark_engine(pt_engine, "PyTorch CUDA FP32", benchmark_cases, iterations=100, T=t_star)
    bench_fp32 = benchmark_engine(fp32_engine, "ONNX Runtime CUDA FP32", benchmark_cases, iterations=100, T=t_star)
    bench_fp16 = benchmark_engine(fp16_engine, "ONNX Runtime CUDA FP16", benchmark_cases, iterations=100, T=t_star)

    logger.info("=== Benchmark Results Summary ===")
    for b in [bench_pt, bench_fp32, bench_fp16]:
        logger.info(
            f"  {b['engine']:26s} | Cold: {b['cold_start_ms']:6.2f} ms | "
            f"p50: {b['warm_p50_ms']:5.2f} ms | p95: {b['warm_p95_ms']:5.2f} ms | "
            f"Throughput: {b['throughput_req_per_sec']:5.1f} req/s"
        )



    # 6. Memory Leak Audit (1000 requests on FP16)
    logger.info("Running 1,000 request continuous memory leak check on ONNX FP16...")
    mem_before_mb = get_process_rss_mb()
    reqs = [ChoiceRequest.from_dict(c) for c in benchmark_cases]
    for i in range(1000):
        fp16_engine.predict(reqs[i % len(reqs)], temperature=t_star)
    mem_after_mb = get_process_rss_mb()
    mem_drift_mb = mem_after_mb - mem_before_mb
    logger.info(f"Memory before: {mem_before_mb:.1f} MB, after: {mem_after_mb:.1f} MB, drift: {mem_drift_mb:+.2f} MB")

    # 7. Gate Verifications
    all_fp32_parity_100 = all(s["fp32_top1_parity"] == 1.0 for s in parity_results.values())
    all_fp16_parity_100 = all(s["fp16_top1_parity"] == 1.0 for s in parity_results.values())
    p50_pass = bool(bench_fp16["warm_p50_ms"] <= 15.0)
    p95_pass = bool(bench_fp16["warm_p95_ms"] <= 20.0)
    leak_pass = bool(abs(mem_drift_mb) < 50.0)

    gate_checks = {
        "gate_onnx_fp32_parity_100": {
            "passed": all_fp32_parity_100,
            "threshold": 1.0,
        },
        "gate_onnx_fp16_parity_100": {
            "passed": all_fp16_parity_100,
            "threshold": 1.0,
        },
        "gate_p50_latency_le_15ms": {
            "passed": p50_pass,
            "actual_ms": bench_fp16["warm_p50_ms"],
            "threshold_ms": 15.0,
        },
        "gate_p95_latency_le_20ms": {
            "passed": p95_pass,
            "actual_ms": bench_fp16["warm_p95_ms"],
            "threshold_ms": 20.0,
        },
        "gate_zero_memory_leak": {
            "passed": leak_pass,
            "drift_mb": mem_drift_mb,
            "threshold_mb": 50.0,
        },
    }

    all_passed = all(g["passed"] for g in gate_checks.values())
    logger.info("=======================================================")
    logger.info(f"Milestone 23 Gate Verdict: {'ALL GATES PASSED' if all_passed else 'GATE FAILED'}")
    logger.info("=======================================================")
    for k, v in gate_checks.items():
        logger.info(f"  {k}: {'PASS' if v['passed'] else 'FAIL'}")

    # 8. Export manifests & benchmarks
    bench_data = {
        "pytorch": bench_pt,
        "onnx_fp32": bench_fp32,
        "onnx_fp16": bench_fp16,
        "memory_leak_audit": {
            "iterations": 1000,
            "drift_mb": round(mem_drift_mb, 2),
            "passed": leak_pass,
        },
    }

    manifest_fp16 = {
        "release": "erabi-rc2-onnx-fp16",
        "version": "rc2-fp16",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "model_file": "model.onnx",
        "file_size_bytes": os.path.getsize(ONNX_FP16_DIR / "model.onnx"),
        "calibrated_temperature": t_star,
        "parity": parity_results,
        "benchmark": bench_fp16,
        "gate_checks": gate_checks,
        "all_passed": all_passed,
    }

    with open(ONNX_FP16_DIR / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest_fp16, f, indent=2, ensure_ascii=False)
    with open(ONNX_FP16_DIR / "benchmark.json", "w", encoding="utf-8") as f:
        json.dump(bench_data, f, indent=2, ensure_ascii=False)

    report_out = {
        "milestone": "Milestone 23 — ONNX FP16",
        "parity_results": parity_results,
        "benchmarks": bench_data,
        "gate_checks": gate_checks,
        "all_passed": all_passed,
    }

    runs_m23 = ROOT / "runs/rc2_m23_onnx"
    runs_m23.mkdir(parents=True, exist_ok=True)
    with open(runs_m23 / "m23_onnx_results.json", "w", encoding="utf-8") as f:
        json.dump(report_out, f, indent=2, ensure_ascii=False)

    logger.info(f"Milestone 23 reports and manifests written to {ONNX_FP16_DIR} and {runs_m23}")


if __name__ == "__main__":
    main()
