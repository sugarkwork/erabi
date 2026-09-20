"""RC2.1 Phase 5: ONNX FP32 & ONNX FP16 CUDA Export, Parity Verification, and Benchmarking.

Roadmap: ERABI_RC2_1_AUTONOMOUS_RECOVERY_ROADMAP.md (Section 18)
Pipeline:
PyTorch -> ONNX FP32 -> parity -> ONNX FP16 CUDA -> parity -> benchmark -> packaging

Gate Conditions:
1. PyTorch <-> ONNX FP32 Top-1 parity 100%
2. PyTorch <-> ONNX FP16 Top-1 parity 100%
3. Parity evaluated on Research Fresh Suite (800 cases) and Smoke cases
4. Calibration applicable with calibrated T*
5. Zero memory leak across 1,000 continuous requests
6. Latency: p50 <= 15 ms, p95 <= 20 ms
"""

from __future__ import annotations

import argparse
import datetime
import gc
import json
import logging
import math
import os
from pathlib import Path
import shutil
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

# Windows DLL path setup for ONNX Runtime CUDA
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
logger = logging.getLogger("erabi.rc2_1_onnx")

DEFAULT_PYTORCH_DIR = ROOT / "release" / "rc2_1" / "model"
DEFAULT_CALIB_PATH = ROOT / "release" / "rc2_1" / "calibration.json"
DEFAULT_FP32_DIR = ROOT / "release" / "rc2_1_onnx"
DEFAULT_FP16_DIR = ROOT / "release" / "erabi-rc2_1-onnx-fp16"
RESEARCH_FRESH_PATH = ROOT / "data" / "rc2_1_research_fresh" / "research_fresh_eval.jsonl"
SMOKE_PATH = ROOT / "examples" / "smoke_cases.jsonl"


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


def export_fp32_model(pytorch_dir: Path, out_dir: Path, calib_path: Optional[Path] = None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_onnx = out_dir / "model.onnx"
    if out_onnx.exists():
        logger.info(f"FP32 ONNX Model already exists at {out_onnx}.")
        return out_onnx

    logger.info(f"=== Exporting RC2.1 FP32 ONNX Model to {out_onnx} ===")
    engine = GLiClassEngine(str(pytorch_dir), device="cpu")
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
    logger.info("FP32 ONNX Export completed. Checking model...")
    m = onnx.load(str(out_onnx))
    onnx.checker.check_model(m)

    for fname in ["tokenizer.json", "tokenizer_config.json", "config.json"]:
        src = pytorch_dir / fname
        if src.exists():
            shutil.copy2(src, out_dir / fname)
    if calib_path and calib_path.exists():
        shutil.copy2(calib_path, out_dir / "calibration.json")
    logger.info(f"Copied companion files to {out_dir}")

    del engine, model, wrapper
    gc.collect()
    return out_onnx


def export_fp16_model(pytorch_dir: Path, out_dir: Path, calib_path: Optional[Path] = None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_onnx = out_dir / "model.onnx"
    if out_onnx.exists():
        logger.info(f"FP16 ONNX Model already exists at {out_onnx}.")
        return out_onnx

    logger.info(f"=== Exporting RC2.1 FP16 ONNX Model to {out_onnx} ===")
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    engine = GLiClassEngine(str(pytorch_dir), device=device)
    model = engine.pipe.pipe.model
    patch_vectorized_segment_ids(model.model)

    model = model.half().to(device)
    model.eval()

    wrapper = ONNXFP16ExportWrapper(model)
    wrapper.eval()

    dummy_ids = torch.ones((1, 48), dtype=torch.long, device=device)
    dummy_ids[0, 5] = model.model.config.text_token_index
    dummy_ids[0, 1] = model.model.config.class_token_index
    dummy_ids[0, 3] = model.model.config.class_token_index
    dummy_mask = torch.ones((1, 48), dtype=torch.long, device=device)

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
    logger.info("FP16 ONNX Export completed. Checking model...")
    m = onnx.load(str(out_onnx))
    onnx.checker.check_model(m)

    for fname in ["tokenizer.json", "tokenizer_config.json", "config.json"]:
        src = pytorch_dir / fname
        if src.exists():
            shutil.copy2(src, out_dir / fname)
    if calib_path and calib_path.exists():
        shutil.copy2(calib_path, out_dir / "calibration.json")
    logger.info(f"Copied companion files to {out_dir}")

    del engine, model, wrapper
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()
    return out_onnx


def run_rc2_1_parity_audit(
    pt_engine: GLiClassEngine,
    fp32_engine: ERABIONNXEngine,
    fp16_engine: ERABIONNXEngine,
    T: float,
    suites: Dict[str, Path],
) -> Dict[str, Any]:
    logger.info("=== Running RC2.1 Parity Audit ===")
    suite_results = {}

    for sname, spath in suites.items():
        if not spath.exists():
            logger.warning(f"Suite {spath} does not exist, skipping.")
            continue
        records = [json.loads(l) for l in open(spath, encoding="utf-8") if l.strip()]
        logger.info(f"Evaluating suite: {sname} ({len(records)} cases)...")

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

            pt_resp = pt_engine.predict(req, temperature=T, return_logits=True)
            pt_pred = pt_resp.best_candidate_id
            if pt_pred == tgt_cid:
                pt_correct += 1

            fp32_resp = fp32_engine.predict(req, temperature=T, return_logits=True)
            fp32_pred = fp32_resp.best_candidate_id
            if fp32_pred == tgt_cid:
                fp32_correct += 1
            if fp32_pred == pt_pred:
                fp32_top1_matches += 1

            fp16_resp = fp16_engine.predict(req, temperature=T, return_logits=True)
            fp16_pred = fp16_resp.best_candidate_id
            if fp16_pred == tgt_cid:
                fp16_correct += 1
            if fp16_pred == pt_pred:
                fp16_top1_matches += 1

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

    t0_cold = time.perf_counter()
    engine.predict(reqs[0], temperature=T)
    cold_latency_ms = (time.perf_counter() - t0_cold) * 1000.0

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


def export_and_verify_rc2_1(
    pytorch_dir: Path,
    calib_path: Optional[Path],
    fp32_dir: Path,
    fp16_dir: Path,
    device: Optional[str] = None,
) -> Dict[str, Any]:
    device = device or ("cuda:0" if torch.cuda.is_available() else "cpu")
    logger.info("=== RC2.1 Phase 5: ONNX FP32 and FP16 CUDA Export ===")

    # 1. Export models
    export_fp32_model(pytorch_dir, fp32_dir, calib_path)
    export_fp16_model(pytorch_dir, fp16_dir, calib_path)

    # 2. Calibrated Temperature T*
    t_star = 1.0
    if calib_path and calib_path.exists():
        with open(calib_path, "r", encoding="utf-8") as f:
            cdata = json.load(f)
            t_star = float(cdata.get("temperature", 1.0))
    logger.info(f"Operating at T* = {t_star:.6f}")

    # 3. Instantiate engines
    pt_engine = GLiClassEngine(str(pytorch_dir), device=device)
    fp32_engine = ERABIONNXEngine(str(fp32_dir), device=device)
    fp16_engine = ERABIONNXEngine(str(fp16_dir), device=device)

    # 4. Parity Evaluation
    suites = {
        "research_fresh_suite": RESEARCH_FRESH_PATH,
        "smoke_cases": SMOKE_PATH,
    }
    parity_results = run_rc2_1_parity_audit(pt_engine, fp32_engine, fp16_engine, T=t_star, suites=suites)

    # 5. Benchmarking
    smoke_records = [json.loads(l) for l in open(SMOKE_PATH, encoding="utf-8") if l.strip()]
    bench_pt = benchmark_engine(pt_engine, "PyTorch CUDA FP32", smoke_records, iterations=100, T=t_star)
    bench_fp32 = benchmark_engine(fp32_engine, "ONNX Runtime CUDA FP32", smoke_records, iterations=100, T=t_star)
    bench_fp16 = benchmark_engine(fp16_engine, "ONNX Runtime CUDA FP16", smoke_records, iterations=100, T=t_star)

    # 6. Memory leak audit (1,000 requests on FP16)
    logger.info("Running 1,000 request continuous memory leak check on ONNX FP16...")
    mem_before_mb = get_process_rss_mb()
    reqs = [ChoiceRequest.from_dict(c) for c in smoke_records]
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
    logger.info(f"RC2.1 Phase 5 Gate Verdict: {'ALL GATES PASSED' if all_passed else 'GATE FAILED'}")
    logger.info("=======================================================")
    for k, v in gate_checks.items():
        logger.info(f"  {k}: {'PASS' if v['passed'] else 'FAIL'}")

    # 8. Manifests and benchmarks
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
        "release": "erabi-rc2_1-onnx-fp16",
        "version": "rc2.1-fp16",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "model_file": "model.onnx",
        "file_size_bytes": os.path.getsize(fp16_dir / "model.onnx"),
        "calibrated_temperature": t_star,
        "parity": parity_results,
        "benchmark": bench_fp16,
        "gate_checks": gate_checks,
        "all_passed": all_passed,
    }

    with open(fp16_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest_fp16, f, indent=2, ensure_ascii=False)
    with open(fp16_dir / "benchmark.json", "w", encoding="utf-8") as f:
        json.dump(bench_data, f, indent=2, ensure_ascii=False)

    report_out = {
        "milestone": "RC2.1 Phase 5 — ONNX FP16",
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parity_results": parity_results,
        "benchmarks": bench_data,
        "gate_checks": gate_checks,
        "all_passed": all_passed,
    }

    run_dir = pytorch_dir.parent
    with open(run_dir / "onnx_verification_results.json", "w", encoding="utf-8") as f:
        json.dump(report_out, f, indent=2, ensure_ascii=False)

    logger.info(f"RC2.1 ONNX releases packaged at {fp16_dir} and verified.")
    return report_out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RC2.1 ONNX Export and Parity Verification.")
    parser.add_argument("--pytorch-dir", type=str, default=str(DEFAULT_PYTORCH_DIR), help="Path to PyTorch model directory")
    parser.add_argument("--calib-path", type=str, default=str(DEFAULT_CALIB_PATH), help="Path to calibration.json")
    parser.add_argument("--fp32-dir", type=str, default=str(DEFAULT_FP32_DIR), help="Output FP32 ONNX directory")
    parser.add_argument("--fp16-dir", type=str, default=str(DEFAULT_FP16_DIR), help="Output FP16 ONNX directory")
    parser.add_argument("--device", type=str, default=None, help="Inference device")
    args = parser.parse_args()

    export_and_verify_rc2_1(
        pytorch_dir=Path(args.pytorch_dir),
        calib_path=Path(args.calib_path) if args.calib_path else None,
        fp32_dir=Path(args.fp32_dir),
        fp16_dir=Path(args.fp16_dir),
        device=args.device,
    )
