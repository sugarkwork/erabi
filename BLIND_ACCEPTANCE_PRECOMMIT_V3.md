# ERABI Release Candidate 2 Blind Sealed Acceptance Pre-Commit Manifesto (v3)

**Document Reference**: [`ERABI_RC2_BLIND_SEALED_REACCEPTANCE_DIRECTIVE.md`](file:///f:/ai/erabi-local/ERABI_RC2_BLIND_SEALED_REACCEPTANCE_DIRECTIVE.md)  
**Pre-Commit Timestamp**: 2026-09-20 06:10:00 UTC  
**Target Milestone**: Milestone 24.1 — Blind Sealed Re-Acceptance (Suite v3)  
**Supersedes**: [`BLIND_ACCEPTANCE_PRECOMMIT.md`](file:///f:/ai/erabi-local/BLIND_ACCEPTANCE_PRECOMMIT.md) (v2 retired per Section 10 in [`BLIND_ACCEPTANCE_V2_INVALIDATED.md`](file:///f:/ai/erabi-local/BLIND_ACCEPTANCE_V2_INVALIDATED.md))  

---

## 1. Zero Model Inference Guarantee (Phase A Certification)

In accordance with Section 1 & Section 10 of the Directive:
1. **Zero Model Inference Probing**: The test generator `scripts/build_rc2_blind_test_v3.py` and all modules under `scripts/blind_v3_data/` were authored and executed with **strictly zero model inference calls**.
2. **Import Verifications**: PyTorch model evaluation, ONNX runtime, and `erabi.inference` imports are explicitly blocked by hard runtime assertions during dataset generation.
3. **No Target Calibration / Adaptive Tuning**: Targets and distractor choices were authored independently based on rigorous domain and logical constraints, not by model response probing.

---

## 2. Frozen Release Candidate 2 Artifact Hashes

The candidate under evaluation remains strictly frozen with unchanged SHA-256 signatures:

| Artifact | Path | SHA-256 Checksum | Status |
|:---|:---|:---:|:---:|
| **PyTorch Weights** | `release/rc2/model/model.safetensors` | `dd3bae25efcce97df8b14cf29064c9910f62686436ff95bb16b1c184fb03c0c0` | **STRICTLY FROZEN** |
| **Calibration Parameters** | `release/rc2/calibration.json` ($T^* = 0.263007$) | `1ea8d18b724bd0b0d6e29db2d10a8930908c4f4b32a83b78778f6439385828b1` | **STRICTLY FROZEN** |
| **ONNX FP16 Runtime** | `release/erabi-rc2-onnx-fp16/model.onnx` | `49340dd4fb62a4ae49472ceb10dc3f144822d3434aa1a9cf7e4a4369f12127b5` | **STRICTLY FROZEN** |

---

## 3. Blind Sealed Acceptance Suite v3 Artifact Hashes

The complete blind sealed test suite v3, generator scripts, and audit reports are committed to Git prior to running any inference:

| Artifact | Path | SHA-256 Checksum |
|:---|:---|:---:|
| **Blind v3 Test Cases (480 cases)** | `data/sealed_acceptance_rc2_blind_v3/sealed_test_rc2_blind_v3.jsonl` | `4352d3b3d4acee00afa88e144d170219ca2e25765ba59ad21b597632d59ba11a` |
| **Suite Manifest** | `data/sealed_acceptance_rc2_blind_v3/manifest.json` | `d53aaa133d19855281aaf6814d03b8d160b331080b422d55b3553683e4ffe15e` |
| **Semantic & Structural Audit** | `data/sealed_acceptance_rc2_blind_v3/semantic_audit.json` | `ecba7d2d80830f64b48c19167462bc852cf4969b8bc48c208f45348aa1312a7e` |
| **Token Length Contract Audit** | `data/sealed_acceptance_rc2_blind_v3/token_audit.json` | `813f0dcb525b30d691a7e8f36d2b49cb0aa5a58fb06b64c322be78a56f3e9ccc` |
| **Zero Background Leakage Audit** | `data/sealed_acceptance_rc2_blind_v3/overlap_audit.json` | `afe2ac0f6ec1b3d5aa255dc3e0ef5c7250aafc55095f187e8925dfe4bb524bcb` |
| **Test Builder Script v3** | `scripts/build_rc2_blind_test_v3.py` | `12264e79dff853871a9ba6fdb5a2705cbb6ce7f4819e32127e3431a8db99f345` |
| **Re-Acceptance Eval Script v3** | `scripts/run_rc2_blind_reacceptance_v3.py` | `62a40d9834c76048b684ba8d82ef949dbe43d8a5a00509282c9b92344833b07f` |
| **Blind v3 Package Init** | `scripts/blind_v3_data/__init__.py` | `1ea3b020f2e72d7ff70423494cc006a2d83745a3d4537be3377513a116cf6777` |
| **Family: core_rules** | `scripts/blind_v3_data/family_core_rules.py` | `a4180d899c99318171cd0f762a1fabc3627d22bb7bbf50bf55be2172d8c5dd90` |
| **Family: logical_operators** | `scripts/blind_v3_data/family_logical_operators.py` | `276a6a531b0ee98d6adddc7a5bdb503e59b6695ef15f4f9b32c0cf39a33ebe17` |
| **Family: priority_exception** | `scripts/blind_v3_data/family_priority_exception.py` | `1f10a99b9263841c3d4d4b2f15fc29c6de6a140001145cffbafe2e7114c1c659` |
| **Family: natural_japanese** | `scripts/blind_v3_data/family_natural_japanese.py` | `334ee67c0689f807fe42ce19fbb49979f6967fedc2a7d0c496ac161d3aff7aa0` |
| **Family: domain_transfer** | `scripts/blind_v3_data/family_domain_transfer.py` | `982ca8e46b0fe7dab75ec9719ce1c83404fb0ca31aeef813a4214272e9d56424` |
| **Family: general_choice** | `scripts/blind_v3_data/family_general_choice.py` | `02c7cf8050425e8f106e8b72b058b296d836859c8574b3cdbec2112a7fc88937` |
| **Family: variable_choice** | `scripts/blind_v3_data/family_variable_choice.py` | `c9eabe93c1899365b1eb488b8b0efe7d395194c52234a32a25cd24d0d46b2dd7` |
| **Family: perturbation_invariance**| `scripts/blind_v3_data/family_perturbation_invariance.py` | `53657c51c57a67e7192e59029c55a9e848cd1d55cc1e499d5042f96a2e8bf744` |

---

## 4. Test Suite Composition & Audit Results

### 4.1 Structural Stratification
- **Total Test Cases**: 480 cases organized into 240 strictly contrastive pairs.
- **8 Balanced Families** (60 cases / 30 pairs each):
  1. `core_rules`: 60 cases (prefix `rc2b3_core_`)
  2. `logical_operators`: 60 cases (prefix `rc2b3_op_`)
  3. `priority_exception`: 60 cases (prefix `rc2b3_prio_`)
  4. `natural_japanese`: 60 cases (prefix `rc2b3_nat_`)
  5. `domain_transfer`: 60 cases (prefix `rc2b3_dom_`)
  6. `general_choice`: 60 cases (prefix `rc2b3_gen_`)
  7. `variable_choice`: 60 cases (prefix `rc2b3_var_`)
  8. `perturbation_invariance`: 60 cases (prefix `rc2b3_pert_`)
- **Candidate Count ($K$) Stratification**:
  - $K=2$: 60 cases (30 pairs)
  - $K=3$: 60 cases (30 pairs)
  - $K=4$: 120 cases (60 pairs)
  - $K=6$: 60 cases (30 pairs)
  - $K=8$: 60 cases (30 pairs)
  - $K=12$: 60 cases (30 pairs)
  - $K=16$: 60 cases (30 pairs)

### 4.2 Programmatic Semantic & Structural Audit
- **Audit File**: `data/sealed_acceptance_rc2_blind_v3/semantic_audit.json`
- **Result**: `is_valid: true`, `error_count: 0`
- Verified: No missing/empty context, no missing/empty questions, target IDs strictly present in choices, exact contrastive pairs with differing targets, unique candidate IDs per case.

### 4.3 Token Length Contract Audit
- **Audit File**: `data/sealed_acceptance_rc2_blind_v3/token_audit.json`
- **Result**: `is_contract_compliant: true`, `violations_count: 0`
- **Max Sequence Length**: 435 tokens (architectural contract ceiling: 512 tokens)
- **Average Sequence Length**: 258.7 tokens
- Verified: Zero risk of `ValidationError: Total input length exceeds maximum limit of 512 tokens`.

### 4.4 Zero Background Leakage Audit
- **Audit File**: `data/sealed_acceptance_rc2_blind_v3/overlap_audit.json`
- **Records Audited**: 48,964 background records across 107 files (`data/` training/dev/calibration/benchmarks + `examples/`).
- **Exact Overlaps Found**: **0 (Zero Leakage)**.
- Verified: Suite v3 is 100% genuine unseen out-of-distribution evaluation data.

---

## 5. Immutable Final Acceptance Gate Thresholds

The One-Shot evaluation will execute against the following non-negotiable gates:

| Gate Metric | Mandatory Pass Threshold |
|:---|:---:|
| **Overall Accuracy (PyTorch)** | $\ge 90.0\%$ |
| **Overall Accuracy (ONNX FP16)** | $\ge 90.0\%$ |
| **PyTorch $\leftrightarrow$ ONNX FP16 Top-1 Parity** | $100.0\%$ |
| **Critical Paired Reasoning (Both Correct)** | $\ge 80.0\%$ |
| **Candidate Permutation Consistency** | $\ge 95.0\%$ |
| **Family Minimum Accuracy (No Collapse)** | All families $\ge 75.0\%$ |
| **Small-to-Mid Candidates ($K=2..8$)** | $\ge 85.0\%$ |
| **Large Candidates ($K=12..16$)** | $\ge 75.0\%$ |
| **High-Confidence Error Rate ($p \ge 0.90$)** | $\le 5.0\%$ |
| **Semantic Ground-Truth Errors** | $0$ |
| **Data Leakage against Background Records** | $0$ |

---

## 6. One-Shot Execution Protocol Mandate

Per Directive Section 10:
> *「実行後: datasetを書き換えない、generatorを書き換えない、targetを書き換えない、wordingを書き換えない、「曖昧だったので除外」をしない」*

This pre-commit seals the dataset and evaluation code. The evaluation script `scripts/run_rc2_blind_reacceptance_v3.py` will be run exactly once. The outcome is final and definitive.
