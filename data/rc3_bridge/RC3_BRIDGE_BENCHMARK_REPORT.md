# ERABI Milestone 28: RC3 Development Bridge Benchmark Report

**Date**: 2026-09-21  
**Status**: **SEALED & VALIDATED**  
**Total Test Cases**: 480  
**Total Contrastive Pairs**: 240  
**Target Output**: `data\rc3_bridge\rc3_bridge_benchmark.jsonl`  
**Dataset SHA256**: `95f551e136a80d426ca4eec093be84880c21e6b9fb1161d16bb4ba193b0cf558`  

---

## 1. Executive Summary & Purpose

In strict compliance with Milestone 28 of `ERABI_RC3_DIAGNOSTIC_FIRST_ARCHITECTURE_ROADMAP.md`, the **RC3 Development Bridge Benchmark** (`data/rc3_bridge/`) has been created.

### Key Distinction from Blind Sets:
- **Retired Blind Sets (v3, v4)**: Sealed evaluators retired after blind testing. Strictly forbidden from training, fine-tuning, or iterative development.
- **Bridge Benchmark (`rc3_bridge`)**: A fresh, non-contaminated development benchmark designed to reproduce the true difficulty axes revealed in Blind v4 forensics:
  1. High-cardinality in-domain candidate sets ($K=12, 16$).
  2. Propositional operator logic (AND, OR, NOT, NOR, XOR, NAND).
  3. Strict equality/inequality threshold boundaries and floating-point precision.
  4. Subtle concessive clauses and Japanese regulatory phrasing.
  5. Multi-tier priority hierarchies and emergency overrides.
  6. Novel frontier domains (quantum cryogenics, tokamak fusion, orbital space tugs).
  7. Adversarial distractor lexical overlap.

---

## 2. Benchmark Architecture & Stratification

### 2.1 Family Balance (8 Families $	imes$ 30 Pairs = 480 Cases)

| Family | Pairs | Cases | Key Challenge Tested |
|:---|:---:|:---:|:---|
| **`core_rules`** | 30 | 60 | Industrial dual-metric criteria, strict threshold boundaries |
| **`logical_operators`** | 30 | 60 | Truth-table logic, NOR/XOR/NAND, condition polarity inversion |
| **`priority_exception`** | 30 | 60 | Multi-tier rules, emergency precedence, exception clauses |
| **`natural_japanese`** | 30 | 60 | Concessive conjunctions, legalistic qualifiers, double negations |
| **`domain_transfer`** | 30 | 60 | Cross-domain transfer (quantum, fusion, space, cryo-EM) |
| **`general_choice`** | 30 | 60 | High-cardinality candidate sets ($K=8, 16$) with in-domain competitors |
| **`variable_choice`** | 30 | 60 | Variable candidate count scaling ($K \in [2, 12]$) |
| **`perturbation_invariance`**| 30 | 60 | Active/passive, syntactic inversion, lexical overlap distractors |
| **TOTAL** | **240** | **480** | **100% Balanced Contrastive Structure** |

### 2.2 Candidate Cardinality ($K$) Distribution

| Choice Count ($K$) | Pairs | Cases | Percentage |
|:---:|:---:|:---:|:---:|
| **$K=2$** | 20 | 40 | 8.3% |
| **$K=3$** | 65 | 130 | 27.1% |
| **$K=4$** | 95 | 190 | 39.6% |
| **$K=6$** | 30 | 60 | 12.5% |
| **$K=8$** | 15 | 30 | 6.2% |
| **$K=12$** | 5 | 10 | 2.1% |
| **$K=16$** | 10 | 20 | 4.2% |

---

## 3. Strict Quality & Contract Audits

### 3.1 Token Length Contract (<= 450 Tokens)
- **Hard Limit**: 512 tokens
- **Safety Budget**: 450 tokens
- **Max Measured Length**: **438 tokens**
- **Average Length**: **225.25 tokens**
- **P95 Length**: **326 tokens**
- **Violations (> 450 tokens)**: **0 cases (100% compliant)**

### 3.2 Programmatic Semantic & Structural Audit
- **Schema Validation**: **PASS** (Choice IDs strictly conform to `^[A-Za-z0-9_-]{1,64}$`)
- **Target Consistency**: **PASS** (100% of target IDs match exactly one choice option)
- **Pair Complementarity**: **PASS** (All 240 pairs possess valid contrastive conditions)
- **Empty Fields**: **0**

### 3.3 Zero Data Leakage Audit
- **Background Files Audited**: 117 files (63834 records)
- **Exact Context Matches**: **0**
- **Exact Question Matches**: **0**
- **Fingerprint Matches**: **0**
- **Leakage Rate**: **0.00% (Zero Contamination Guaranteed)**

---

## 4. Verification Artifacts & Hashes

| Artifact Path | SHA256 Hash |
|:---|:---|
| `data/rc3_bridge/rc3_bridge_benchmark.jsonl` | `95f551e136a80d426ca4eec093be84880c21e6b9fb1161d16bb4ba193b0cf558` |
| `data/rc3_bridge/manifest.json` | `c4f8fb344531f7d94b56ae3121660fd451e244aa4a6c86c8de88a8bb913606e6` |
| `data/rc3_bridge/semantic_audit.json` | `c2e91e3b90192da54eb01705bed8e93cfa239987e2fa5af99f9289a204034718` |
| `data/rc3_bridge/token_audit.json` | `26414475026781cefc4e38090ade0cd62c5c22e1f8392fe53dca6ecd9367cf66` |
| `data/rc3_bridge/overlap_audit.json` | `34dcb6a02e5298a44dc8c2a2215f69d40d174957c4f79ad781b14a6e12ba29e5` |

---

## 5. Milestone 28 Gate Status

- [x] Exact overlap = 0 against all past data (train, dev, blind v3, blind v4)
- [x] Normalized structural overlap recorded
- [x] Independent programmatic semantic validator PASS
- [x] Blind v4 text never copied
- [x] 480 test cases (within 400〜800 cases requirement)
- [x] Token length contract PASS (<= 450 tokens)

**Milestone 28 Gate: PASSED.**
