# ERABI Release Candidate 2.1 Blind Sealed Re-Acceptance Failed

**Audit Date**: 2026-09-20 19:54:52 UTC  
**Model Checkpoint**: `F:\ai\erabi-local\release\rc2_1\model`  
**Calibration**: `F:\ai\erabi-local\release\rc2_1\calibration.json` ($T^* = 2.772176$)  
**ONNX Runtime**: `F:\ai\erabi-local\release\erabi-rc2_1-onnx-fp16`  
**Blind Test Suite**: `F:\ai\erabi-local\data\sealed_acceptance_rc2_1_blind_v4\sealed_test_rc2_1_blind_v4.jsonl` (480 cases, 240 pairs)  
**Overall Verdict**: **FINAL ACCEPTANCE GATES FAILED**  

---

## 1. Immutable Final Acceptance Gate Scorecard

| Gate Requirement | Target / Threshold | Measured Value | Status |
|:---|:---:|:---:|:---:|
| **Overall Accuracy (PyTorch >= 90.0%)** | >= 90.0% | **74.17%** | **FAILED** |
| **Overall Accuracy (ONNX FP16 >= 90.0%)** | >= 90.0% | **74.17%** | **FAILED** |
| **PyTorch <-> ONNX FP16 Parity (== 100.0%)** | == 100.0% | **100.00%** | **PASSED** |
| **Critical Paired Reasoning (>= 85.0%)** | >= 85.0% | **57.08%** | **FAILED** |
| **Candidate Permutation Consistency (>= 95.0%)** | >= 95.0% | **93.54%** | **FAILED** |
| **Family Minimum Accuracy (>= 80.0%)** | All >= 80.0% | **Min 55.00%** | **FAILED** |
| **Logical Operators (>= 85.0%)** | >= 85.0% | **55.00%** | **FAILED** |
| **Natural Japanese (>= 85.0%)** | >= 85.0% | **90.00%** | **PASSED** |
| **General Choice (>= 85.0%)** | >= 85.0% | **60.00%** | **FAILED** |
| **Perturbation Invariance (>= 90.0%)** | >= 90.0% | **56.67%** | **FAILED** |
| **Variable Choice Overall (>= 85.0%)** | >= 85.0% | **63.33%** | **FAILED** |
| **Variable Choices K=2..8 (>= 85.0%)** | >= 85.0% | **80.00%** | **FAILED** |
| **Variable Choices K=12..16 (>= 80.0%)** | >= 80.0% | **56.67%** | **FAILED** |
| **High-Confidence Error Rate (<= 5.0%)** | <= 5.0% | **17.41%** | **FAILED** |
| **Semantic Ground-Truth Errors (== 0)** | Audited by Programmatic Validator | **0** | **PASSED** |
| **Data Leakage against Background Records (== 0)** | Audited by Overlap Validator | **0** | **PASSED** |

---

## 2. Capability Breakdown Across 8 Reasoning Paradigms (60 Cases / 30 Pairs Each)

| Family | Cases | PyTorch Acc | ONNX Acc | Paired Reasoning | Permutation | Mean NLL | Status |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `core_rules` | 60 | **81.7%** | 81.7% | 70.0% (21/30) | 98.3% | 0.9041 | **FAIL** |
| `domain_transfer` | 60 | **95.0%** | 95.0% | 90.0% (27/30) | 95.0% | 0.3424 | **PASS** |
| `general_choice` | 60 | **60.0%** | 60.0% | 43.3% (13/30) | 86.7% | 1.5375 | **FAIL** |
| `logical_operators` | 60 | **55.0%** | 55.0% | 20.0% (6/30) | 93.3% | 2.1527 | **FAIL** |
| `natural_japanese` | 60 | **90.0%** | 90.0% | 80.0% (24/30) | 96.7% | 0.3419 | **PASS** |
| `perturbation_invariance` | 60 | **56.7%** | 56.7% | 20.0% (6/30) | 88.3% | 2.9164 | **FAIL** |
| `priority_exception` | 60 | **91.7%** | 91.7% | 86.7% (26/30) | 100.0% | 0.5175 | **PASS** |
| `variable_choice` | 60 | **63.3%** | 63.3% | 46.7% (14/30) | 90.0% | 2.3008 | **FAIL** |

---

## 3. Candidate Count Scaling Breakdown ($K=2..16$)

| Choice Count ($K$) | Cases | PyTorch Accuracy | Status |
|:---:|:---:|:---:|:---:|
| **$K=2$** | 60 | **61.7%** (37/60) | **PASS** |
| **$K=3$** | 60 | **73.3%** (44/60) | **PASS** |
| **$K=4$** | 120 | **90.0%** (108/120) | **PASS** |
| **$K=6$** | 60 | **88.3%** (53/60) | **PASS** |
| **$K=8$** | 60 | **76.7%** (46/60) | **PASS** |
| **$K=12$** | 60 | **66.7%** (40/60) | **PASS** |
| **$K=16$** | 60 | **46.7%** (28/60) | **PASS** |

---

## 4. Integrity & Reproducibility Statement

1. **Pre-Commit Isolation**: The blind test suite v4 was authored, validated for zero leakage against all background records, and committed before inference.
2. **Strict One-Shot Execution**: Evaluated in a single uninterrupted forward pass without prompt tuning or cherry-picking.
3. **Dual Engine Parity**: PyTorch and ONNX FP16 produce 100.0% identical top-1 rankings across all test cases.
