# RC2 Milestone 13: RC1 Reproducibility Baseline Locked

**Date**: 2026-09-20  
**Status**: **LOCKED & VERIFIED**  
**Roadmap Reference**: `ERABI_RC2_AUTONOMOUS_RESEARCH_ROADMAP.md` (Section 7)

---

## 1. Executive Summary

Milestone 13 establishes the immutable reference point for ERABI RC2. All artifacts from ERABI RC1 (PyTorch model weights, temperature calibration, ONNX FP32, ONNX FP16 CUDA, and test suites) were audited, verified against cryptographic hashes, and re-executed across all 4 evaluation suites (340 test cases).

**Milestone 13 Gate Criteria Status**:
- [x] **RC1 hash match**: 100% matched across model, tokenizer, calibration, manifest, and test suites.
- [x] **Top-1 parity**: **100.0% (340/340)** agreement between PyTorch, ONNX FP32, and ONNX FP16 CUDA.
- [x] **Metric consistency**: Exact match with recorded values across all suites.
- [x] **ONNX FP16 execution**: Native FP16 on RTX A4000 fully operational.
- [x] **Benchmark stability**: Warm p50 = 10.87 ms, p95 = 13.34 ms, throughput = 89.0 req/s, zero memory leak.

---

## 2. Cryptographic Hash Verification

| Artifact | Size | Expected SHA-256 | Actual SHA-256 | Status |
|:---|:---:|:---|:---|:---:|
| `model.safetensors` (RC1) | 711.7 MB | `be9a9cb1...` | `be9a9cb17d58f373...` | **MATCH** |
| `calibration.json` (RC1) | 1767 B | `8fc501f1...` | `8fc501f10d107af0...` | **MATCH** |
| `manifest.json` (RC1) | 1044 B | `27459596...` | `2745959671f7f08e...` | **MATCH** |
| `sealed_test.jsonl` | 73974 B | `86825a0c...` | `86825a0ca378dbf4...` | **MATCH** |
| `rc1_onnx/model.onnx` (FP32) | 712.7 MB | `0ec39ca0...` | `0ec39ca090786171...` | **MATCH** |
| `erabi-rc1-onnx-fp16/model.onnx` | 356.9 MB | `7063ff19...` | `7063ff191dcc566c...` | **MATCH** |

---

## 3. Re-evaluation Parity Across 4 Test Suites (340 Cases)

Evaluation executed with calibrated temperature $T^* = 0.256$:

| Suite | Total | PyTorch Acc | ONNX FP32 Acc | ONNX FP16 Acc | Top-1 Agreement | Max Logit Diff | Max Prob Drift |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Sealed Acceptance** | 120 | 100.0% | 100.0% | 100.0% | **100.0%** | 0.0779 | 5.40e-35 |
| **Fresh Operator** | 100 | 92.0% | 92.0% | 92.0% | **100.0%** | 0.0724 | 1.78e-04 |
| **Fresh Robustness** | 108 | 100.0% | 100.0% | 100.0% | **100.0%** | 0.0313 | 4.17e-31 |
| **Smoke Cases** | 12 | 83.3% | 83.3% | 83.3% | **100.0%** | 0.0484 | 1.60e-07 |
| **Overall** | **340** | - | - | - | **100.0% (340/340)** | - | - |

- **Paired Reasoning Consistency**:
  - Sealed Acceptance: 100.0% (PyTorch) / 100.0% (ONNX FP16)
  - Fresh Operator: 84.0% (PyTorch) / 84.0% (ONNX FP16)
  - Fresh Robustness: 100.0% (PyTorch) / 100.0% (ONNX FP16)

---

## 4. Latency & Resource Benchmarks (RTX A4000)

| Metric | PyTorch Baseline (CUDA FP32) | ONNX Runtime CPU FP32 | ONNX Runtime CUDA FP16 | Status |
|:---|:---:|:---:|:---:|:---:|
| **Warm p50 Latency** | 20.65 ms | 54.56 ms | **10.87 ms** | 1.8x Faster |
| **Warm p95 Latency** | 28.12 ms | 56.96 ms | **13.34 ms** | Jitter Minimized |
| **Throughput** | 45.0 req/s | 18.4 req/s | **89.0 req/s** | High Throughput |
| **1000-Req Memory Drift** | - | - | **1.25 MB** | Zero Leak |

---

## 5. Decision & Next Step

**Milestone 13 Gate Status**: **PASS**

RC1 baseline is completely locked and immutable.  
As per `ERABI_RC2_AUTONOMOUS_RESEARCH_ROADMAP.md` (Section 8), the autonomous loop now proceeds immediately to:
**Milestone 14 — Data Scaling Law (12.5%, 25%, 50%, 75%, 100% data fractions)**.
