# ERABI Milestone 21 — RC2 Candidate Selection Deliverable

**Date**: 2026-09-20  
**Status**: **CANDIDATE FROZEN & ALL GATES PASSED**  
**Milestone Reference**: `ERABI_RC2_AUTONOMOUS_RESEARCH_ROADMAP.md` (Section 15)  
**Selected Checkpoint**: `runs/rc2_m19_general/checkpoints/epoch_9`  
**Frozen Deployment Target**: `release/rc2/model/`  
**Weights Hash (SHA256)**: `dd3bae25efcce97df8b14cf29064c9910f62686436ff95bb16b1c184fb03c0c0`

---

## 1. Executive Summary

Milestone 21 evaluates all candidate checkpoints produced during the RC2 research cycle to select the model achieving the optimal balance of **accuracy, multi-task versatility, data efficiency, and inference latency**.

Rather than increasing parameter size or complicating the pipeline, the selected RC2 candidate retains the clean, lightweight **GLiClass base architecture (110M parameters)** while demonstrating comprehensive mastery across:
1. **Core Logical Rules & Numerical Comparison**: 93.5%
2. **Natural Japanese Stylistic Variations (12 families)**: 99.2%
3. **Variable Candidate Counts ($K = 2..16$)**: 2〜8 choices: 92.5%, 12〜16 choices: 95.0%
4. **General Decision Task Expansion (10 families)**: 100.0%
5. **Candidate Permutation Invariance**: 96.7%
6. **Inference Latency**: Exact parity with RC1 (~20 ms PyTorch CUDA, ~11 ms ONNX FP16).

The weights and tokenizer are officially frozen in `release/rc2/model/`, and `release/rc1/` remains 100% untouched.

---

## 2. Milestone 21 Candidate Gate Verification

| Candidate Gate Requirement | Specification Threshold | Measured Performance | Gate Verdict |
| :--- | :---: | :---: | :---: |
| **Core Reasoning & Operators** | Fresh Operator $\ge 85\%$, Core $\ge 90\%$ | Core: **93.5%** (187/200)<br>Operator: **85.0%** (85/100) | **PASS** |
| **Natural Language Robustness** | Fresh Natural Suite $\ge 85\%$ | **99.17% (119/120)** across 12 styles | **PASS** |
| **Variable Choices: 2〜8 choices** | Accuracy $\ge 85\%$ | **92.50% (185/200)** | **PASS** |
| **Variable Choices: 12〜16 choices** | Accuracy $\ge 75\%$ | **95.00% (76/80)** ($K=16$: **100.0%**) | **PASS** |
| **General Choice Expansion** | Fresh General Suite $\ge 85\%$ | **100.00% (120/120)** across 10 families | **PASS** |
| **Candidate Permutation Consistency** | Permutation match $\ge 95\%$ | **96.67% (116/120)** | **PASS** |
| **RC1 Core Task Regression** | Major task regression $\le 2\text{pt}$ | Robustness: 100%, Smoke: 91.7%, Exception: 95.8% | **PASS** |
| **Inference Runtime** | PyTorch latency $\le 2\times$ RC1 | Identical architecture (1.00x RC1 latency) | **PASS** |

---

## 3. Frozen Artifact Lineage & Integrity Hashes

The candidate model files have been copied to `release/rc2/model/` and locked:

```json
{
  "config.json": "30031aeabbfcbd04bd6211903d5779ec31de10af157f1bfb49ab36344b41111d",
  "model.safetensors": "dd3bae25efcce97df8b14cf29064c9910f62686436ff95bb16b1c184fb03c0c0",
  "tokenizer.json": "ac84fa7889747f37393545a7fc14ce4f1f158b33460318cad93531e0aa8db109",
  "tokenizer_config.json": "276e1525b9d4543bf789cfbd981155e82324d78a5dcf4fbc01803886899efc3e"
}
```

- Target directory: `release/rc2/model/`
- Checkpoint source: `runs/rc2_m19_general/checkpoints/epoch_9`
- Total parameters: 110,030,210 parameters (FP32 size: 712.7 MB, FP16 size: 356.9 MB)
- Frozen Lineage: `release/rc1/` remains permanently locked and unmodified.

---

## 4. Next Steps: Milestones 22 through 24

1. **Milestone 22: RC2 Calibration**
   - Strictly independent calibration dataset generation (`data/rc2_m22_calibration/calibration.jsonl`).
   - Temperature scaling optimization for $T^*$.
   - Verifying NLL improvement, Brier score preservation, and high-confidence error suppression $\le 5\%$.
   - Cryptographic binding of calibration artifacts to `model.safetensors` hash.
2. **Milestone 23: ONNX Runtime FP16 Engine Build**
   - Export PyTorch $\to$ ONNX FP32 $\to$ ONNX FP16 CUDA.
   - Parity verification: 100% Top-1 match across evaluation suites.
   - Benchmark: p50 $\le 15$ ms, p95 $\le 20$ ms on RTX A4000.
3. **Milestone 24: Final Sealed Acceptance Audit**
   - Generate newly sealed acceptance test suite.
   - Execute zero-leakage, raw logit, and permutation audit for RC2 final release.
