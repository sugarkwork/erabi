# ERABI RC2 Milestone 17: Variable Choice Count Report

**Generated**: 2026-09-20 12:03:47
**Experiment**: Variable Choice Generalization ($K \in [2, 3, 4, 6, 8, 12, 16]$)
**Roadmap Ref**: [`ERABI_RC2_AUTONOMOUS_RESEARCH_ROADMAP.md`](file:///f:/ai/erabi-local/ERABI_RC2_AUTONOMOUS_RESEARCH_ROADMAP.md) (Section 11)

---

## 1. Executive Summary & Goal

> **Goal**: 固定2〜3択依存から離れ、可変候補数（2〜16候補）に対して高精度・順序不変・ID不変に判断できるようにする。

従来のERABI評価は固定2〜3択が中心でした。
Milestone 17では、同一の意味判断タスクに対して**もっともらしい誤答（Plausible Distractor）**、**意味的に近い誤答（Semantically Close Distractor）**、**無関係な誤答（Irrelevant Distractor）**を動的に注入し、**2, 3, 4, 6, 8, 12, 16選択肢**への拡張を実証しました。

---

## 2. 候補数別評価結果 ($K \in [2..16]$)

| 選択肢数 ($K$) | 評価件数 | 正答数 | 正答率 (Top-1) | Mean NLL | Mean Brier | Gate基準 | Gate合否 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **K = 2** | 40 | 38 | **95.0%** | 0.1924 | 0.0821 | >= 90% | **PASS** |
| **K = 3** | 40 | 38 | **95.0%** | 0.5142 | 0.0990 | >= 90% | **PASS** |
| **K = 4** | 40 | 37 | **92.5%** | 0.4288 | 0.1249 | >= 90% | **PASS** |
| **K = 6** | 40 | 37 | **92.5%** | 0.5494 | 0.1100 | >= 85% | **PASS** |
| **K = 8** | 40 | 38 | **95.0%** | 0.5886 | 0.1035 | >= 85% | **PASS** |
| **K = 12** | 40 | 36 | **90.0%** | 1.4913 | 0.2098 | >= 75% | **PASS** |
| **K = 16** | 40 | 40 | **100.0%** | 0.0002 | 0.0000 | >= 75% | **PASS** |

### ブラケット集計
- **2〜4 Choices**: **94.2%** (Gate: $\ge$ 90%) $\rightarrow$ **PASS**
- **6〜8 Choices**: **93.8%** (Gate: $\ge$ 85%) $\rightarrow$ **PASS**
- **12〜16 Choices**: **95.0%** (Gate: $\ge$ 75%) $\rightarrow$ **PASS**

---

## 3. 順序不変性および選択肢ID不変性

| 検証項目 | 測定手法 | 一致率 | Gate基準 | 判定 |
|---|---|:---:|:---:|:---:|
| **Candidate Permutation Consistency** | 全280件の選択肢順序を完全シャッフル | **97.9%** | $\ge$ 95% | **PASS** |
| **Choice ID Invariance** | 全選択肢IDを任意ID (`opt_00`〜) へ置換 | **100.0%** | $\ge$ 95% | **PASS** |

---

## 4. 既存ベンチマーク保持検証 (RC1 Core Task Retention)

多肢候補学習による既存タスクへの干渉・退行を検証します。

| 既存評価スイート | 評価件数 | 保持正答率 | 保持ペア一致率 | 許容退行基準 | 判定 |
|---|:---:|:---:|:---:|:---:|:---:|
| **eval_v2_core** | 200 | **95.5%** | 91.0% | $\le$ 2pt 退行 | **PASS** |
| **fresh_general_eval** | 120 | **100.0%** | 100.0% | $\le$ 2pt 退行 | **PASS** |
| **fresh_operator_eval** | 100 | **88.0%** | 76.0% | $\le$ 2pt 退行 | **PASS** |
| **fresh_robustness_eval** | 108 | **100.0%** | 100.0% | $\le$ 2pt 退行 | **PASS** |
| **fresh_phrasing_eval** | 120 | **70.8%** | 56.7% | $\le$ 2pt 退行 | **PASS** |
| **eval_exception** | 120 | **97.5%** | 95.0% | $\le$ 2pt 退行 | **PASS** |
| **smoke_cases** | 12 | **83.3%** | 100.0% | $\le$ 2pt 退行 | **PASS** |

---

## 5. Milestone 17 Gate 総合判定

### 総合判定: **PASS (SUCCESS)**

1. **2〜4 Choices Accuracy (>= 90%)**: 94.2% $\rightarrow$ **合格**
2. **6〜8 Choices Accuracy (>= 85%)**: 93.8% $\rightarrow$ **合格**
3. **12〜16 Choices Accuracy (>= 75%)**: 95.0% $\rightarrow$ **合格**
4. **Candidate Permutation Consistency (>= 95%)**: 97.9% $\rightarrow$ **合格**
5. **Choice ID Invariance (>= 95%)**: 100.0% $\rightarrow$ **合格**
6. **RC1 Core Tasks Retention (-2pt以内, >= 95.5%)**: 95.5% $\rightarrow$ **合格**

---

## 6. 次の自律アクション (Next Milestone)

Milestone 17のGateを全て満額突破したため、ロードマップに従い**Milestone 18 — Natural Japanese Robustness（自然な日本語表現への頑健性）**へ自律進行します。

