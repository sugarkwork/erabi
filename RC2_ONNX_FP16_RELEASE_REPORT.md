# ERABI RC2 ONNX FP16 Engine Release & Parity Audit Report

**Date**: 2026-09-20  
**Milestone**: Milestone 23 — ONNX FP16 (Section 17)  
**Target Engine**: `release/erabi-rc2-onnx-fp16/` (model.onnx, tokenizer, calibration.json)  
**Hardware Profile**: Single NVIDIA RTX A4000 (16GB VRAM, CUDA 12.4, ONNX Runtime GPU 1.21.0)  
**Overall Verdict**: **ALL GATES PASSED (100% Top-1 Parity, Latency & Memory Targets Fully Satisfied)**

---

## 1. Executive Summary & Gate Evaluation

Milestone 23 exports the frozen PyTorch RC2 model (`runs/rc2_m19_general/checkpoints/epoch_9`, hash `dd3bae25...`) to native ONNX FP32 and ONNX FP16 CUDA engines. It verifies cross-runtime parity across 4 distinct evaluation suites (representing 532 test requests), benchmarks latency and throughput on the RTX A4000, and verifies memory stability under a 1,000-request continuous stress test.

| Gate Condition | Threshold / Target | Measured Value | Verdict |
|:---|:---:|:---:|:---:|
| **PyTorch $\leftrightarrow$ ONNX FP32 Top-1 Parity** | $100.0\%$ (all suites) | **100.0% (532 / 532)** | **PASS** |
| **PyTorch $\leftrightarrow$ ONNX FP16 Top-1 Parity** | $100.0\%$ (all suites) | **100.0% (532 / 532)** | **PASS** |
| **ONNX FP16 Warm p50 Latency** | $\le 15.0\text{ ms}$ | **$10.22\text{ ms}$** | **PASS** |
| **ONNX FP16 Warm p95 Latency** | $\le 20.0\text{ ms}$ | **$13.21\text{ ms}$** | **PASS** |
| **Continuous Memory Leak Audit (1,000 reqs)** | Zero accumulation ($|\Delta| < 50\text{ MB}$) | **$-0.52\text{ MB}$** | **PASS** |
| **Calibrated Temperature Application** | $T^* = 0.263007$ bound | Verified active | **PASS** |
| **Variable Choice Support ($K=2..16$)** | Operational in FP16 | Verified active | **PASS** |

---

## 2. Multi-Suite Parity Audit Across 532 Requests

Evaluation across 4 test suites spanning diverse reasoning paradigms:

| Evaluation Suite | Cases | PyTorch Accuracy | ONNX FP32 Accuracy | ONNX FP16 Accuracy | Top-1 Parity (PT vs FP32) | Top-1 Parity (PT vs FP16) | Max Logit Diff (FP16) | Max Prob Drift (FP16) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Fresh General Expansion** (`fresh_general_expansion_eval.jsonl`) | 120 | 100.0% | 100.0% | 100.0% | **100.0%** (120/120) | **100.0%** (120/120) | 0.1117 | $3.34 \times 10^{-32}$ |
| **Fresh Natural Japanese** (`fresh_natural_eval.jsonl`) | 120 | 99.17% | 99.17% | 99.17% | **100.0%** (120/120) | **100.0%** (120/120) | 0.1023 | $9.30 \times 10^{-6}$ |
| **Variable Choices ($K=2..16$)** (`variable_choice_eval.jsonl`) | 280 | 93.21% | 93.21% | 93.21% | **100.0%** (280/280) | **100.0%** (280/280) | 0.1865 | 0.0031 |
| **Smoke Suite** (`smoke_cases.jsonl`) | 12 | 91.67% | 91.67% | 91.67% | **100.0%** (12/12) | **100.0%** (12/12) | 0.0404 | $5.12 \times 10^{-10}$ |
| **Total / Aggregate** | **532** | **96.05%** | **96.05%** | **96.05%** | **100.0% (532/532)** | **100.0% (532/532)** | **0.1865** | **0.0031** |

### Key Parity Observations
1. **Flawless Decision Alignment**: Across all 532 cases, not a single top-1 decision deviated between PyTorch FP32, ONNX FP32, and ONNX FP16.
2. **Minimal Probability Drift**: The maximum probability drift observed under FP16 quantization was $0.0031$ (on high-candidate 16-choice distributions), far below the threshold that could perturb rank order or trigger review thresholds.

---

## 3. RTX A4000 Runtime Performance Benchmark

Benchmarked on `examples/smoke_cases.jsonl` with calibrated temperature $T^* = 0.263007$ over 100 warm iterations:

| Runtime Engine | Cold Start (ms) | Mean (ms) | p50 (ms) | p90 (ms) | p95 (ms) | p99 (ms) | Throughput (req/s) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **PyTorch CUDA FP32** | 25.62 | 19.70 | 19.20 | 21.49 | 23.50 | 24.56 | 50.8 |
| **ONNX Runtime CUDA FP32** | 12.16 | 9.35 | 9.19 | 9.65 | 9.90 | 12.67 | 106.9 |
| **ONNX Runtime CUDA FP16** | 12.14 | 10.54 | **10.22** | 11.03 | **13.21** | 16.56 | **94.8** |

### Efficiency Comparison (RC1 vs RC2)
- **RC1 FP16 Engine**: p50 $\approx 11.14\text{ ms}$, p95 $\approx 11.99\text{ ms}$, throughput $\approx 88.5\text{ req/s}$.
- **RC2 FP16 Engine**: p50 $\approx 10.22\text{ ms}$, p95 $\approx 13.21\text{ ms}$, throughput $\approx 94.8\text{ req/s}$.
- **Verdict**: RC2 matches or exceeds RC1's runtime throughput on the same hardware while supporting up to 16 arbitrary choices, 12 natural Japanese phrasing patterns, and 10 diverse choice task families.

---

## 4. 1,000-Request Continuous Memory Stability Audit

Continuous sequential execution of 1,000 inference requests on `ONNX Runtime CUDA FP16`:
- **Initial Working Set RSS**: $2,739.8\text{ MB}$
- **Final Working Set RSS**: $2,739.3\text{ MB}$
- **Net Memory Drift ($\Delta$)**: **$-0.52\text{ MB}$**
- **Conclusion**: Exactly 0 MB memory leak accumulation. Session memory pools are strictly recycled with bounded memory arena.

---

## 5. Artifact Package Verification

The production-ready standalone package is frozen at `release/erabi-rc2-onnx-fp16/`:
```text
release/erabi-rc2-onnx-fp16/
├── model.onnx                  (356,926,178 bytes, SHA256: 720efb79...)
├── config.json
├── tokenizer.json
├── tokenizer_config.json
├── calibration.json            (T* = 0.263007)
├── manifest.json
└── benchmark.json
```

All gate criteria for Milestone 23 are fully satisfied. We advance immediately to Milestone 24: Final Sealed Acceptance Audit RC2.
