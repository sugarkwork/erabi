# FINAL ACCEPTANCE RC3 BLIND AUDIT: FAILED

**Audit Timestamp**: `2026-09-21T03:31:09.501909+00:00`  
**Model Identifier**: `ERABI-RC3`  
**Backbone**: `knowledgator/gliclass-instruct-large-v1.0` (438M parameters)  
**PyTorch Weights**: `F:\ai\erabi-local\release\rc3\model`  
**Production ONNX FP16**: `F:\ai\erabi-local\release\erabi-rc3-onnx-fp16`  
**Calibrated Temperature**: $T^* = 2.6440$  
**Sealed Benchmark**: `data/sealed_acceptance_rc3_blind_v5/sealed_test_rc3_blind_v5.jsonl` (480 cases / 240 pairs)  

---

## Milestone 34 Gate Clearance Audit

| Roadmap Criterion | Target | Measured | Result |
| :--- | :---: | :---: | :---: |
| Overall Accuracy (PyTorch >= 88.0%) | - | 85.21% (>= 88.0%) | **FAIL** |
| Overall Accuracy (ONNX FP16 >= 88.0%) | - | 85.21% (>= 88.0%) | **FAIL** |
| PyTorch <-> ONNX FP16 Parity (== 100.0%) | - | 100.00% (== 100.0%) | **PASS** |
| No Major Family < 75.0% (Min Family >= 75.0%) | - | Min 66.67% (All >= 75.0%) | **FAIL** |
| Logical Operators (>= 80.0%) | - | 66.67% (>= 80.0%) | **FAIL** |
| Perturbation Invariance (>= 80.0%) | - | 85.00% (>= 80.0%) | **PASS** |
| Variable Choice (>= 80.0%) | - | 85.00% (>= 80.0%) | **PASS** |
| General Choice (>= 80.0%) | - | 95.00% (>= 80.0%) | **PASS** |
| Paired Reasoning (Both Correct >= 75.0%) | - | 74.58% (>= 75.0%) | **FAIL** |
| Candidate Permutation Consistency (>= 95.0%) | - | 96.46% (>= 95.0%) | **PASS** |
| High-Confidence Error Rate (<= 7.0%) | - | 6.57% (<= 7.0%) | **PASS** |
| Zero Data Leakage against Historical Corpus (== 0) | - | 0 (Cryptographically Verified) | **PASS** |
| Zero Semantic Ground-Truth Errors (== 0) | - | 0 (Programmatically Verified) | **PASS** |

### Key Results Highlights
- **Overall Accuracy (PyTorch)**: **85.21%** (Target: $\ge 88.0%$)
- **Overall Accuracy (ONNX FP16 CUDA)**: **85.21%** (Target: $\ge 88.0%$)
- **PyTorch $\leftrightarrow$ ONNX Parity**: **100.00%** (Target: $100.0%$)
- **Paired Reasoning (Both Correct)**: **74.58%** (Target: $\ge 75.0%$)
- **Candidate Permutation Invariance**: **96.46%** (Target: $\ge 95.0%$)
- **High-Confidence Error Rate**: **6.57%** (Target: $\le 7.0%$)
- **Data Leakage & Semantic Errors**: **0** (Audited)

Full detailed report available at `runs/rc3_blind_v5_acceptance/RC3_BLIND_V5_ACCEPTANCE_REPORT.md`.