# ERABI RC2 Blind Sealed Re-Acceptance Pre-Commit Manifesto

**Pre-Commit Timestamp (UTC)**: 2026-09-20 05:58:00 UTC  
**Milestone**: Milestone 24.1 — Blind Sealed Re-Acceptance (Directive Execution)  
**Target Engine**: ERABI Release Candidate 2 (`ERABI-RC2`)  
**Evaluation Protocol**: Strict One-Shot Cryptographic Pre-Commit  

---

## 1. Executive Summary & Non-Contamination Declaration

In accordance with [`ERABI_RC2_BLIND_SEALED_REACCEPTANCE_DIRECTIVE.md`](file:///f:/ai/erabi-local/ERABI_RC2_BLIND_SEALED_REACCEPTANCE_DIRECTIVE.md), this document locks and cryptographically certifies the brand-new, unseen blind test suite v2 (`data/sealed_acceptance_rc2_blind_v2/sealed_test_rc2_blind_v2.jsonl`) **PRIOR TO ANY MODEL INFERENCE**.

### Solemn Non-Contamination Certifications:
1. **Zero Model Inference During Authoring**: At no point during the drafting, coding, or generation of `scripts/build_rc2_blind_test_v2.py` and `scripts/blind_v2_data/` was any model (PyTorch, ONNX, GLiClass, or external) invoked, probed, or consulted.
2. **Strict Freeze of RC2 Artifacts**: The model weights (`release/rc2/model/`), calibration parameters (`release/rc2/calibration.json`), and ONNX FP16 engine (`release/erabi-rc2-onnx-fp16/`) remain 100% frozen with byte-level cryptographic integrity preserved.
3. **Zero Background Leakage**: The test suite was programmatically audited against all 48,964 historical background records across 107 files in `data/` and `examples/`. Zero (0) exact context matches, zero (0) question overlaps, and zero (0) input fingerprints were detected (`overlap_audit.json`: `is_leak_free=True`).
4. **Independent Programmatic Semantic Audit**: All 480 test cases (240 contrastive pairs) passed automated logical, structural, and schema validation (`semantic_audit.json`: `is_valid=True`, 0 errors).
5. **Pre-Commit Before Execution**: This manifesto, the dataset, and the generator are committed to Git revision control **BEFORE** the single acceptance evaluation run is triggered.

---

## 2. Cryptographic Hash Lock

### 2.1 Frozen RC2 Model & Runtime Artifacts
| Component | File Path | SHA-256 Hash |
|:---|:---|:---|
| **PyTorch Weights** | `release/rc2/model/model.safetensors` | `dd3bae25efcce97df8b14cf29064c9910f62686436ff95bb16b1c184fb03c0c0` |
| **PyTorch Config** | `release/rc2/model/config.json` | `30031aeabbfcbd04bd6211903d5779ec31de10af157f1bfb49ab36344b41111d` |
| **PyTorch Tokenizer** | `release/rc2/model/tokenizer.json` | `ac84fa7889747f37393545a7fc14ce4f1f158b33460318cad93531e0aa8db109` |
| **Calibration Artifact** | `release/rc2/calibration.json` ($T^* = 0.263007$) | `1ea8d18b724bd0b0d6e29db2d10a8930908c4f4b32a83b78778f6439385828b1` |
| **ONNX FP16 Engine** | `release/erabi-rc2-onnx-fp16/model.onnx` | `49340dd4fb62a4ae49472ceb10dc3f144822d3434aa1a9cf7e4a4369f12127b5` |
| **ONNX Manifest** | `release/erabi-rc2-onnx-fp16/manifest.json` | `570170713665a26204e8f750d33a3f71f1bb24c48a80ee3bd26b2ba458797341` |

### 2.2 Blind Acceptance Suite v2 & Generator Artifacts
| Component | File Path | SHA-256 Hash |
|:---|:---|:---|
| **Blind Test Dataset** | `data/sealed_acceptance_rc2_blind_v2/sealed_test_rc2_blind_v2.jsonl` | `fd4f932a4c216d1f9f29b2b976498fcfde07bb5552779953ea8ef91e72cc85bc` |
| **Suite Manifest** | `data/sealed_acceptance_rc2_blind_v2/manifest.json` | `f59972c72b22596489375ff412c1b9b1c7dc4dfd20d754f9a0ad47648ba6d51a` |
| **Semantic Audit** | `data/sealed_acceptance_rc2_blind_v2/semantic_audit.json` | `d55dcad293e6df047321eb59f4fbb4e8e8eaef75c7b398ca6e2759e0c812d46e` |
| **Overlap Audit** | `data/sealed_acceptance_rc2_blind_v2/overlap_audit.json` | `64d4f8087cf283d5cf7ef89369d13e31cbb22f87ee2e74e622ef1fbfa3fafe19` |
| **Main Generator** | `scripts/build_rc2_blind_test_v2.py` | `5927de31286d6f185eef7ec80e0132e5e9a844cd13493b0e8ba73cf042df5baa` |
| Data Module: Core Rules | `scripts/blind_v2_data/family_core_rules.py` | `4d9f51674a4b99198c760a40a46c96e89a60f677c9edee88f22fa618f11650e8` |
| Data Module: Operators | `scripts/blind_v2_data/family_logical_operators.py` | `701a4a1e232a41d120841292d5e2c2dc73aa608613b864d875a867916951ce38` |
| Data Module: Priorities | `scripts/blind_v2_data/family_priority_exception.py` | `22124c40d80f11acdf3c29b2568359a9a5c0a30b95a66f55468dec6552f3890d` |
| Data Module: Japanese | `scripts/blind_v2_data/family_natural_japanese.py` | `97fb9254b00447865d7ba6467da6bddab45a2c55d176d8be1d5117ef83bf6b37` |
| Data Module: Transfer | `scripts/blind_v2_data/family_domain_transfer.py` | `239c7e847f892e2c6436a360420dc52ab364cdadc3f3be0a5bda9cffbe26af3b` |
| Data Module: General | `scripts/blind_v2_data/family_general_choice.py` | `074bd8514b5d7d23a88993634e12f10c9448dcdd466862b54f8b3337fa584596` |
| Data Module: Variable | `scripts/blind_v2_data/family_variable_choice.py` | `164bc5a034100e2a3a8ae906a79c2bb3da932db5b7e30c60186eaf836f89cc34` |
| Data Module: Perturb | `scripts/blind_v2_data/family_perturbation_invariance.py` | `99c1cb5e9d308cce321b7bf2da7b5c3c34de0517a14e6c7b002a6a80c5943e88` |

---

## 3. Suite Composition & Stratification Matrix

### 3.1 Family Breakdown (480 cases / 240 pairs)
- `core_rules`: 60 cases (30 pairs)
- `logical_operators`: 60 cases (30 pairs)
- `priority_exception`: 60 cases (30 pairs)
- `natural_japanese`: 60 cases (30 pairs)
- `domain_transfer`: 60 cases (30 pairs)
- `general_choice`: 60 cases (30 pairs)
- `variable_choice`: 60 cases (30 pairs)
- `perturbation_invariance`: 60 cases (30 pairs)

### 3.2 Candidate Count ($K$) Stratification
- $K=2$: 60 cases (30 pairs)
- $K=3$: 60 cases (30 pairs)
- $K=4$: 120 cases (60 pairs)
- $K=6$: 60 cases (30 pairs)
- $K=8$: 60 cases (30 pairs)
- $K=12$: 60 cases (30 pairs)
- $K=16$: 60 cases (30 pairs)
**Total**: Exactly 480 cases (240 contrastive pairs).

---

## 4. Immutable Final Acceptance Gate

The following thresholds are locked from the original RC2 roadmap and will be judged strictly without post-hoc modification:

| Acceptance Gate Requirement | Criterion Threshold |
|:---|:---:|
| **Overall Accuracy** | $\ge 90.0\%$ |
| **No Major Family Collapse** | Every Family $\ge 75.0\%$ |
| **Critical Paired Reasoning (Both Correct)** | $\ge 80.0\%$ |
| **Candidate Permutation Consistency** | $\ge 95.0\%$ |
| **Small-to-Medium Candidate Accuracy ($K=2..8$)** | $\ge 85.0\%$ |
| **Large Candidate Accuracy ($K=12..16$)** | $\ge 75.0\%$ |
| **PyTorch $\leftrightarrow$ ONNX FP16 Top-1 Parity** | $= 100.0\%$ |
| **Semantic Errors in Dataset** | $= 0$ |
| **Exact Background Data Leakage** | $= 0$ |

---

## 5. One-Shot Execution Protocol

Following this pre-commit, the single evaluation script (`scripts/run_rc2_blind_reacceptance.py`) will be executed **EXACTLY ONCE**.
- The model will receive the blind test suite as-is.
- No prompt editing, no case filtering, and no post-hoc tuning will occur.
- If all gates pass, `FINAL_ACCEPTANCE_RC2_BLIND_VERIFIED.md` will be generated.
- If any gate fails, `FINAL_ACCEPTANCE_RC2_BLIND_FAILED.md` will be generated.
