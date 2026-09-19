# ERABI Release Candidate 1 — ONNX FP16 Optimized Package

- **Version**: `RC-1.0.0 (erabi-rc1-onnx-fp16)`
- **Runtime**: ONNX Runtime (CUDA Execution Provider)
- **Target Precision**: Native FP16 with Float32 Logit Output
- **Model Size**: 356.9 MB (50% reduction vs PyTorch 712 MB)
- **Calibrated Temperature**: $T^* = 0.256$

---

## 1. Benchmark & Acceleration Summary

| Metric | PyTorch Baseline (CUDA FP32) | ONNX FP16 (CUDA EP) | Improvement / Acceleration |
|:---|:---:|:---:|:---:|
| **Warm Latency p50** | 20.65 ms | **11.14 ms** | **1.85x faster** |
| **Warm Latency p95** | 33.59 ms | **11.99 ms** | **2.80x faster** |
| **Throughput** | 45.0 req/s | **88.5 req/s** | **+43.5 req/s** |
| **Model Footprint** | 712.7 MB | **356.9 MB** | **50.0% VRAM saving** |
| **1000-Req Memory Drift** | - | **-1.51 MB** | **Zero leak** |

---

## 2. Accuracy & Numerical Parity Across Suites

| Evaluation Suite | Cases | PyTorch Top-1 | ONNX FP16 Top-1 | Top-1 Agreement | Max Logit Diff | Max Prob Drift |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Sealed Acceptance** | 120 | 100.0% | **100.0%** | **100.0%** | 0.0779 | 5.40e-35 |
| **Fresh Operator Eval** | 100 | 92.0% | **92.0%** | **100.0%** | 0.0724 | 1.78e-04 |
| **Fresh Robustness Eval** | 108 | 100.0% | **100.0%** | **100.0%** | 0.0313 | 4.17e-31 |
| **Smoke Cases** | 12 | 83.3% | **83.3%** | **100.0%** | 0.0484 | 1.60e-07 |

---

## 3. Package Structure

```text
release/erabi-rc1-onnx-fp16/
  ├── model.onnx             # Optimized ONNX FP16 graph (356.9 MB)
  ├── tokenizer.json         # DeBERTa-v3 tokenizer data
  ├── tokenizer_config.json  # Tokenizer special tokens configuration
  ├── config.json            # Model architecture configuration
  ├── calibration.json       # Temperature scaling binding (T* = 0.256)
  ├── manifest.json          # Package manifest & cryptographic hashes
  ├── benchmark.json         # Complete performance & resource measurements
  ├── example.py             # Self-contained runnable usage script
  ├── README.md              # Documentation & performance overview
  └── LIMITATIONS.md         # Operational constraints & error bounds
```

## 4. Quick Start

```python
from erabi.onnx_engine import ERABIONNXEngine
from erabi.schema import ChoiceRequest

engine = ERABIONNXEngine("release/erabi-rc1-onnx-fp16", device="cuda")
resp = engine.predict(ChoiceRequest.from_dict({...}), temperature=0.256)
print(resp.best_candidate_id, [(c.id, c.probability) for c in resp.choices])
```
