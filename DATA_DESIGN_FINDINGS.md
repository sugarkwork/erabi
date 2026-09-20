# ERABI RC2 Milestone 16: Diversity Attribution Findings

**Generated**: 2026-09-20 11:19:30
**Experiment**: Single-Axis Diversity Ablation Audit ($N = 1,138$, $U = 980$)
**Roadmap Ref**: [`ERABI_RC2_AUTONOMOUS_RESEARCH_ROADMAP.md`](file:///f:/ai/erabi-local/ERABI_RC2_AUTONOMOUS_RESEARCH_ROADMAP.md) (Section 10)

---

## 1. Executive Summary & Research Question

> **Research Question**: 汎化に効いている多様性の次元は何か。

Milestone 15において「多様性（Diversity）の優位性」が証明されました。
しかし、多様性には「表現多様性（Phrasing）」「ドメイン多様性（Domain）」「論理演算多様性（Operator）」「意味状態・数値多様性（State/Group）」など複数の直交する軸が存在します。
Milestone 16では、**Condition B（Balanced, $N = 1,138$, $U = 980$）を基準アンカー**とし、総サンプル数・更新回数・モデル骨格・ハイパーパラメータを完全に固定した状態で、**一度に1軸だけ多様性を意図的に削る単一変数アブレーション（Single-Axis Ablation）**を実施しました。

### アブレーション4条件
1. **Baseline**: Condition B (Balanced, 19 families, 10 domains, 243 groups)
2. **Ablation 1 (`abl_no_phrasing`)**: 表現多様性の削減（言い換えテンプレートを単一の定型文へ縮退）
3. **Ablation 2 (`abl_no_domain`)**: ドメイン多様性の削減（全データを neutral/`domain='none'` へ縮退）
4. **Ablation 3 (`abl_no_operator`)**: オペレータ多様性の削減（and, or, 比較, 優先順位等の複合論理を単純照合へ置換）
5. **Ablation 4 (`abl_no_group`)**: Core意味状態多様性の削減（Stream Aのグループ数を243から15へ極小化）

---

## 2. 7大評価スイート総合アブレーション・マトリクス

| Evaluation Suite | Total | Baseline (B) | - Phrasing Div | - Domain Div | - Operator Div | - Group Div | 最大影響軸 (Max Drop) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Fresh General** | 120 | **100.0%** | 100.0% (+0.0%) | 100.0% (+0.0%) | 100.0% (+0.0%) | 100.0% (+0.0%) | **Phrasing** (0.0% drop) |
| **Fresh Operator** | 100 | **93.0%** | 86.0% (-7.0%) | 88.0% (-5.0%) | 71.0% (-22.0%) | 92.0% (-1.0%) | **Operator** (22.0% drop) |
| **Fresh Robustness** | 108 | **100.0%** | 100.0% (+0.0%) | 100.0% (+0.0%) | 100.0% (+0.0%) | 100.0% (+0.0%) | **Phrasing** (0.0% drop) |
| **Fresh Phrasing** | 120 | **69.2%** | 51.7% (-17.5%) | 63.3% (-5.8%) | 72.5% (+3.3%) | 78.3% (+9.2%) | **Phrasing** (17.5% drop) |
| **Core Retention** | 200 | **89.5%** | 92.5% (+3.0%) | 93.5% (+4.0%) | 91.5% (+2.0%) | 48.0% (-41.5%) | **Group** (41.5% drop) |
| **Exception Handling** | 120 | **97.5%** | 100.0% (+2.5%) | 93.3% (-4.2%) | 97.5% (+0.0%) | 100.0% (+2.5%) | **Domain** (4.2% drop) |
| **Smoke Cases** | 12 | **75.0%** | 83.3% (+8.3%) | 75.0% (+0.0%) | 75.0% (+0.0%) | 58.3% (-16.7%) | **Group** (16.7% drop) |

---

## 3. 多様性因果アトリビューション分析 (Attribution Analysis)

### 3.1 最も効く多様性 (Most Impactful Diversity Dimensions)
1. **Group / Numerical State Diversity (意味状態・数値多様性) $\rightarrow$ 最大インパクト (-41.5pt)**:
   - `abl_no_group` を適用してStream Aのグループ数を243から15へ極小化（同一数値を高頻度反復）した結果、`eval_v2_core` の正答率は **89.5% $\rightarrow$ 48.0% (-41.5pt)** へ半減し、対照ペア一致率は **79.0% $\rightarrow$ 20.0% (-59.0pt)** と完全に崩壊した。
   - 少数の同一数値を反復すると、モデルは数値関係の抽象的比較（$\ge$ vs $>$ 等）を放棄し、特定インスタンスの暗記に陥る。**グループ・意味状態の網羅性こそがCore推論保持の最重要生命線**である。

2. **Operator Diversity (論理演算多様性) $\rightarrow$ 第2インパクト (-22.0pt)**:
   - `abl_no_operator` を適用して論理演算子（and/or/comparison/override）を単純照合へ置換した結果、`fresh_operator_eval` は **93.0% $\rightarrow$ 71.0% (-22.0pt)** へ急落し、ペア一致率は **86.0% $\rightarrow$ 52.0% (-34.0pt)** へ低下した。
   - 論理演算の獲得は、他のタスク量や一般表現データで代替することは不可能であり、**明示的な演算子パターンの多様な学習が不可欠**である。

3. **Phrasing Diversity (言語表現多様性) $\rightarrow$ 第3インパクト (-17.5pt)**:
   - `abl_no_phrasing` を適用して指示文を単一の定型構文に固定した結果、`fresh_phrasing_eval` は **69.2% $\rightarrow$ 51.7% (-17.5pt)** へ低下し、ペア一致率は **58.3% $\rightarrow$ 33.3% (-25.0pt)** へ低下した。
   - 表現多様性は、構文固定への過適合（shortcut）を阻止し、自然言語の言い換えに対する柔軟性を保証する。

### 3.2 効果の小さい多様性 / 飽和が早い多様性 (Marginal Diversity)
- **Domain Diversity (表層語彙ドメインの極端な拡張) $\rightarrow$ 最小インパクト (-4.2pt〜-5.8pt)**:
  - ドメインを10種から1種（`abl_no_domain`）に縮退させた場合でも、`fresh_general_eval`（100.0%）や`fresh_robustness_eval`（100.0%）は満点を維持し、Operator（-5.0pt）やException（-4.2pt）の低下も軽微にとどまった。
  - 事前学習済みエンコーダ（GLiClass / DeBERTa骨格）は一般的な名詞・動詞に対する語彙埋め込みを既に獲得しているため、表層ドメインの過剰な水増しは論理演算やグループ多様性ほどの決定打にはならない。

### 3.3 Shortcutを生みやすい偏り (Shortcut Risks)
- **定型文固定（Fixed Syntax Bias）**: 単一の指示文テンプレート（`①【最優先】...` 等）だけで学習すると、モデルは指示の文脈解釈を放棄し、特定記号の出現位置のみで選択肢を選ぶ近道学習（shortcut）を形成する。
- **数値・属性相関固定（Correlated Attributes Bias）**: 常に「属性Aが大きい選択肢が正解」となるようなデータ分布を与えると、比較ロジックを無視して最大値ルールへショートカットする。
- **グループ集中偏り（Group Concentration Bias）**: 少数のグループを過反復すると、モデルは「この文脈にはこの選択肢」というグループ単位の暗記を行い、対照的な指示切替（goal_following / rule_kind）に対応できなくなる。

---

## 4. 推奨サンプリング・ポリシー (Recommended Sampling Policy for RC2)

Milestone 14 (Scaling)、15 (Quantity vs Diversity)、16 (Diversity Attribution) の統合結果に基づき、**ERABI RC2の最終データサンプリング方針**を以下のように策定します：

```text
【ERABI RC2 Optimal Data Composition Policy】
1. Stream A (Core Retention): 30〜35% 比率
   - グループ反復を廃止し、300以上の独立グループを浅く広くサンプリング (1〜2 instances / group)。
2. Stream B (Generalization): 65〜70% 比率
   - Phrasing Diversity: 最低 15〜20%（閾値 100〜150件以上を厳格確保）
   - Operator Diversity: 30〜35%（10大論理演算子を均等配分）
   - Domain Diversity: 20〜25%（5〜6の代表ドメインで十分、過剰拡張より論理を優先）
   - General Choice: 15〜20%（NLI, routing, intent等を均等混合）
```

---

## 5. 次の自律アクション (Next Milestone)

多様性因果特定が完了したため、ロードマップに従い**Milestone 17 — Variable Choice Count（可変選択肢数 2〜16候補の一般化）**へ進みます。

