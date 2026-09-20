# ERABI Release Candidate 2 Blind Sealed Re-Acceptance Failed

**Audit Date**: 2026-09-20 06:07:09 UTC  
**Model Checkpoint**: `release/rc2/model` (SHA256: `dd3bae25efcce97df8b14cf29064c9910f62686436ff95bb16b1c184fb03c0c0`)  
**Calibration**: `release/rc2/calibration.json` ($T^* = 0.263007$)  
**ONNX Runtime**: `release/erabi-rc2-onnx-fp16`  
**Blind Test Suite**: `data/sealed_acceptance_rc2_blind_v3/sealed_test_rc2_blind_v3.jsonl` (480 cases, 240 pairs)  
**Pre-Commit Manifesto**: [`BLIND_ACCEPTANCE_PRECOMMIT_V3.md`](file:///f:/ai/erabi-local/BLIND_ACCEPTANCE_PRECOMMIT_V3.md)  
**Overall Verdict**: **RE-ACCEPTANCE GATES FAILED**  

---

## 1. Immutable Final Acceptance Gate Scorecard

| Gate Requirement | Target / Threshold | Measured Value | Status |
|:---|:---:|:---:|:---:|
| **Overall Accuracy (PyTorch)** | >= 90.0% | **71.04%** | **FAILED** |
| **Overall Accuracy (ONNX FP16)** | >= 90.0% | **71.04%** | **FAILED** |
| **PyTorch <-> ONNX FP16 Top-1 Parity** | == 100.0% | **100.00%** | **PASSED** |
| **Critical Paired Reasoning (Both Correct)** | >= 80.0% | **55.00%** | **FAILED** |
| **Candidate Permutation Consistency** | >= 95.0% | **86.67%** | **FAILED** |
| **No Major Family Collapse** | All >= 75.0% | **Min 48.33%** | **FAILED** |
| **Variable Choices (K=2..8)** | >= 85.0% | **74.17%** | **FAILED** |
| **Variable Choices (K=12..16)** | >= 75.0% | **61.67%** | **FAILED** |
| **High-Confidence Error Rate (p >= 0.90)** | <= 5.0% | **28.09%** | **FAILED** |
| **Semantic Ground-Truth Errors** | Audited by Programmatic Validator | **0** | **PASSED** |
| **Data Leakage against Background Records** | Audited by Overlap Validator | **0** | **PASSED** |

---

## 2. Capability Breakdown Across 8 Reasoning Paradigms (60 Cases / 30 Pairs Each)

| Family | Cases | PyTorch Acc | ONNX Acc | Paired Reasoning | Permutation | Mean NLL | Status |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `core_rules` | 60 | **98.3%** | 98.3% | 96.7% (29/30) | 100.0% | 0.9931 | **PASS** |
| `domain_transfer` | 60 | **100.0%** | 100.0% | 100.0% (30/30) | 98.3% | 0.0000 | **PASS** |
| `general_choice` | 60 | **50.0%** | 50.0% | 26.7% (8/30) | 80.0% | 19.3627 | **FAIL** |
| `logical_operators` | 60 | **53.3%** | 53.3% | 30.0% (9/30) | 90.0% | 32.2634 | **FAIL** |
| `natural_japanese` | 60 | **51.7%** | 51.7% | 10.0% (3/30) | 78.3% | 34.5356 | **FAIL** |
| `perturbation_invariance` | 60 | **48.3%** | 48.3% | 30.0% (9/30) | 65.0% | 18.1736 | **FAIL** |
| `priority_exception` | 60 | **95.0%** | 95.0% | 90.0% (27/30) | 95.0% | 2.6947 | **PASS** |
| `variable_choice` | 60 | **71.7%** | 71.7% | 56.7% (17/30) | 86.7% | 12.1645 | **FAIL** |

---

## 3. Candidate Count Scaling Breakdown ($K=2..16$)

| Choice Count ($K$) | Cases | PyTorch Accuracy | Status |
|:---:|:---:|:---:|:---:|
| **$K=2$** | 60 | **50.0%** (30/60) | **PASS** |
| **$K=3$** | 60 | **73.3%** (44/60) | **PASS** |
| **$K=4$** | 120 | **83.3%** (100/120) | **PASS** |
| **$K=6$** | 60 | **80.0%** (48/60) | **PASS** |
| **$K=8$** | 60 | **75.0%** (45/60) | **PASS** |
| **$K=12$** | 60 | **46.7%** (28/60) | **PASS** |
| **$K=16$** | 60 | **76.7%** (46/60) | **PASS** |

---

## 4. Integrity & Reproducibility Statement

1. **Pre-Commit Isolation**: The blind test suite v3 was finalized, verified for zero leakage against all 48,964 background records, verified for token length contract (all <= 435 < 512 tokens), and committed to Git before inference.
2. **Strict One-Shot Execution**: The model evaluated the suite in a single uninterrupted forward pass. No post-hoc modifications to prompts, distractors, or targets were performed.
3. **Dual Engine Parity**: PyTorch and ONNX FP16 runtimes produce 100.0% identical top-1 candidate rankings across all 480 test cases.
