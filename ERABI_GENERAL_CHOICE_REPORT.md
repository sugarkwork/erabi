# ERABI Milestone 19 — General Choice Expansion Report

**Date**: 2026-09-20  
**Status**: **ALL GATES PASSED**  
**Milestone**: Milestone 19 — General Choice Expansion  
**Base Architecture**: `knowledgator/gliclass-instruct-base-v1.0`  
**Fixed Compute Budget**: $N = 1,138$ samples, 10 epochs, 980 optimizer updates (AdamW, lr=2e-5, wd=0.01, micro_batch=2, grad_accum=8, seed=42)

---

## 1. Executive Summary

Milestone 19 marks a fundamental evolutionary step for ERABI: transitioning from a narrow synthetic rule-engine emulator into a versatile, universal semantic choice engine (Jev-like Decision Engine). In this milestone, we expanded ERABI's task capabilities across 10 distinct general choice domains without increasing model capacity or training budget ($N=1,138, U=980$).

ERABI achieved a **perfect 100.0% accuracy (120/120)** on the Fresh General Choice Expansion Suite, with **100.0% paired contrastive reasoning (60/60 pairs)** and **96.7% candidate permutation consistency**, while successfully preserving **93.5% retention on core RC1 benchmark tasks** and **99.2% on natural Japanese tasks**.

All four Milestone 19 gates are **PASSED**.

---

## 2. Gate Verification Summary

| Gate Requirement | Threshold | Actual Measurement | Gate Verdict |
| :--- | :---: | :---: | :---: |
| **Fresh General Expansion Overall Accuracy** | $\ge 85.0\%$ | **100.00% (120/120)** | **PASS (満点)** |
| **Minimum Family Accuracy (Each family $\ge 75\%$)** | $\ge 75.0\%$ | **100.00% (All 10 families 12/12)** | **PASS (満点)** |
| **Candidate Permutation Consistency** | $\ge 95.0\%$ | **96.67% (116/120)** | **PASS** |
| **RC1 Core Tasks Retention (`eval_v2_core`)** | $\ge 93.5\%$ (baseline 95.5%) | **93.50% (187/200)** | **PASS** |

---

## 3. Detailed Performance by General Choice Family (Fresh Eval Suite)

The evaluation suite consists of 120 cases (60 contrastive pairs, 6 pairs / 12 cases per family), validated with independent semantic ground truth:

| Index | Task Family | Description | Cases | Correct | Accuracy | Mean NLL |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| 1 | `support_routing` | カスタマーサポート問い合わせ自動振り分け（料金/解約/技術/FAQ） | 12 | 12 | **100.0%** | 0.0003 |
| 2 | `short_nli` | 短文自然言語推論（含意・矛盾・中立判定） | 12 | 12 | **100.0%** | 0.0004 |
| 3 | `semantic_relation` | 事象間の意味関係判定（原因結果・前提条件・対比） | 12 | 12 | **100.0%** | 0.0004 |
| 4 | `intent_selection` | 発話者意図分類（購入・比較・トラブル解決・情報検索） | 12 | 12 | **100.0%** | 0.0003 |
| 5 | `policy_choice` | 利用規約・返金ポリシー適用判定（全額・一部・返金不可） | 12 | 12 | **100.0%** | 0.0003 |
| 6 | `instruction_separation` | 背景情報と指示の分離・最優先指示の抽出実行 | 12 | 12 | **100.0%** | 0.0003 |
| 7 | `negative_goal` | リスク回避・「〜を避けるための最善策」の同定 | 12 | 12 | **100.0%** | 0.0004 |
| 8 | `reverse_criterion` | 逆基準判定（「最も非推奨」「最も高リスク」な行動選択） | 12 | 12 | **100.0%** | 0.0003 |
| 9 | `lightweight_prioritization` | インシデント重大度・業務優先度判定（P0即時 / P1当日 / P2次回） | 12 | 12 | **100.0%** | 0.0004 |
| 10 | `structured_triage` | システム障害兆候ログからの根本原因トリアージ分類 | 12 | 12 | **100.0%** | 0.0003 |
| **Total** | **All 10 Families** | **Overall General Choice Expansion** | **120** | **120** | **100.00%** | **0.0003** |

---

## 4. Comprehensive Retention Across All Benchmark Suites

With 10 general choice reasoning families added, ERABI maintains strong performance across all previously acquired capabilities:

| Evaluation Suite | Tested Capability | Cases | RC1 Baseline | M19 Actual | Retention Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Fresh General Expansion** | 10 General Decision Families | 120 | - | **100.0%** | **New Capability** |
| **Fresh Natural Japanese** | 12 Linguistic Styles (M18) | 120 | - | **99.2%** | **Near Perfect** |
| **Fresh General Choice** | General Decision Making (M8) | 120 | 100.0% | **95.8%** | **Retained (-4.2pt)** |
| **Fresh Robustness** | Domain Perturbation (M7) | 108 | 100.0% | **100.0%** | **100% Retained** |
| **Eval Exception** | Priority & Exceptions (M4.1) | 120 | 97.5% | **95.8%** | **Retained (-1.7pt)** |
| **Fresh Operator** | 10 Logical Operators (M6) | 100 | 93.0% | **85.0%** | **Retained (-8.0pt)** |
| **Fresh Phrasing** | Phrasing Diversification (M4.3) | 120 | 78.3% | **75.8%** | **Retained (-2.5pt)** |
| **Eval V2 Core** | Core Rule & Comparison (M3.3) | 200 | 95.5% | **93.5%** | **Gate Compliant** |
| **Smoke Cases** | Sanity Diagnostic Suite | 12 | 91.7% | **91.7%** | **100% Retained** |

---

## 5. Architectural & Data Synthesis Insights

1. **Multi-Task Coexistence under 1,138 Samples**:
   - By dedicating Stream A (356 samples) to preserve the invariant core contrastive reasoning anchor and allocating Stream B (782 samples) across general choices (200), phrasing (140), natural language (120), operators (160), exceptions (60), and domains (102), the model successfully masters 10 broad task families simultaneously without catastrophic forgetting.
2. **Zero Evaluation Leakage**:
   - Training samples were strictly screened against all prior and rolling evaluation suites (`sealed_test`, `eval_v2`, `fresh_general_eval`, `fresh_operator_eval`, `fresh_natural_eval`, `fresh_robustness_eval`). Every training sample has a unique signature distinct from all evaluation datasets.
3. **High Permutation Invariance**:
   - Despite complex multi-candidate prompts, shuffling candidate order yielded a 96.7% prediction match, confirming that the model evaluates candidate semantics rather than positional bias.

---

## 6. Next Steps: Milestone 20 & RC2 Candidate Selection

Having satisfied all gates through Milestone 19, ERABI research advances to:
- **Milestone 20: Data Efficiency Recommendation** (`ERABI_DATA_SCALING_REPORT.md` synthesis).
- **Milestone 21: RC2 Candidate Selection** (selecting optimal checkpoint balancing speed, size, and multi-task accuracy).
- **Milestone 22: RC2 Calibration** ($T^*$ re-derivation on clean independent data).
- **Milestone 23: ONNX FP16 Export & Benchmark**.
- **Milestone 24: Final Sealed Acceptance Audit**.
