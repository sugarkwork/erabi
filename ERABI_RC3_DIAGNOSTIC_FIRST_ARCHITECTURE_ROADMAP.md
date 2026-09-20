# ERABI RC3 — Diagnostic-First Architecture Roadmap
## Blind v4失敗を「容量不足」と決めつけず、原因を分離してから次モデルへ進む自律開発指示書

作成日: 2026-09-21  
対象: Codex / Antigravity  
前提: RC1 / RC2 / RC2.1 はすべて凍結し、上書きしない

---

# 0. 現状認識

RC2.1 は Development Gate では高性能だった。

- Research Fresh 800件: 92.37%
- Paired Both: 85.25%
- Calibration: PASS
- ONNX FP16 parity: 100%
- ONNX FP16 p50: 約11.13ms

しかし、完全新規 Blind v4 では:

- Overall: 74.17% (356/480)
- Paired Both: 57.08%
- Permutation: 93.54%
- logical_operators: 55.00%
- perturbation_invariance: 56.67%
- variable_choice: 63.33%
- general_choice: 60.00%
- high-confidence error: 17.41%

となり、最終Gateを明確に未達した。

この結果は正式に保持する。

---

# 1. 最重要判断

現時点で以下を断定しない。

> 「200M級GLiClass Cross-Encoderのcapacity ceilingが実証された」

Blind v4の失敗は、少なくとも以下の仮説で説明可能である。

1. Research Freshへの開発過適合
2. Blind v4との表現・難易度・候補数分布差
3. K増加によるcandidate interference
4. sequence length増加によるattention dilution
5. distractor semantic similarity
6. implicit rule / unseen composition gap
7. backbone capacity不足
8. current choice-encoding architectureの限界

これらを分離してからarchitecture変更へ進む。

---

# 2. Blind v4の扱い

Blind v4は今後:

> **Retired Diagnostic Benchmark**

とする。

許可:
- 誤答分析
- aggregate failure patternの抽出
- architecture診断
- future training designの抽象的方針に利用

禁止:
- Blind v4文章のtrainコピー
- 数値だけ差し替えたtrain化
- Blind v4をcheckpoint selectionに使用
- Blind v4をRC3 Final Acceptanceに再利用

RC3 Final Acceptanceには完全新規 Blind v5を作る。

---

# 3. RC3 North Star

ERABI RC3の目的は、

> **Blind分布でも高い汎化性能を保ちつつ、ローカル・高速・ONNX FP16というERABIの強みを維持すること。**

単にモデルを巨大化することを目的にしない。

優先順位:

1. 汎化
2. 変動候補数への安定性
3. 論理operator汎化
4. perturbation invariance
5. general choice transfer
6. 校正
7. レイテンシ / モデルサイズ

---

# 4. Complexity Ladder for RC3

以下の順番を必ず守る。

## Level 1 — Evaluation diagnosis
- Blind v4 difficulty decomposition
- Research Freshとの分布比較
- K / length / distractor / operatorの因果分離

## Level 2 — Input / choice encoding
- candidate interactionの診断
- candidate-independent scoringの検討
- permutation robustness

## Level 3 — Training/data design
- composition diversity
- implicit negative / fallback
- hard distractor diversity
- curriculum

## Level 4 — Larger compatible backbone
- 同じchoice architectureのままbackboneだけ拡大

## Level 5 — Architecture change
- separated candidate encoder
- hybrid bi-encoder / cross-encoder
- pairwise scoring
- other architecture

## Level 6 — Very large backend
8B級等。

Level 6へ直接飛ばない。

---

# 5. Milestone 25 — RC2.1 Freeze & Blind v4 Retirement

## Goal

RC2.1を研究基準として完全固定する。

保存:

```text
release/rc2_1/
release/erabi-rc2_1-onnx-fp16/
FINAL_ACCEPTANCE_RC2_1_BLIND_FAILED.md
```

記録:

- model hash
- calibration hash
- ONNX hash
- Blind v4 hash
- Git commit

## Gate

全hash固定、既存artifact非変更。

---

# 6. Milestone 26 — Blind v4 Forensic Decomposition

## Goal

74.17%の失敗を「何が難しかったか」に分解する。

再学習禁止。

---

## 6.1 必須軸

Blind v4全480問について以下を集計する。

### Family
- core_rules
- logical_operators
- priority_exception
- natural_japanese
- domain_transfer
- general_choice
- variable_choice
- perturbation_invariance

### Choice Count
- K=2
- K=3
- K=4
- K=6
- K=8
- K=12
- K=16

### Sequence Length
token bins:
- <=128
- 129–256
- 257–384
- 385–512

### Pair Direction
- s1
- s2
- both
- one-sided failure

### Semantic Difficulty
可能な範囲で:
- explicit rule
- implicit fallback
- negation
- double negation
- equality boundary
- AND
- OR
- priority
- exception
- first-match
- reverse criterion
- semantic relation

### Distractor Type
- irrelevant
- plausible
- semantically close
- adversarial lexical overlap

### Confidence
- <0.6
- 0.6–0.8
- 0.8–0.9
- >=0.9

---

## 6.2 Research Freshとの比較

Research Fresh 800とBlind v4を同じ軸で比較。

以下を作る:

```text
blind_vs_dev_distribution.json
blind_failure_matrix.json
```

確認する:

- BlindだけKが大きいか
- Blindだけtoken lengthが長いか
- Blindだけimplicit/negativeが多いか
- distractor similarityが高いか
- operator compositionが複雑か

---

## 6.3 Gate

最低限、Blind v4誤答124件の80%以上を
2〜5個の主要failure clustersへ分類できること。

分類不能が多い場合は無理にcapacityと結論しない。

---

# 7. Milestone 27 — Frozen-Model Controlled Factorial Diagnostics

## Goal

**モデルを学習せず**、現RC2.1 frozen modelで
K・length・distractor complexityの因果効果を測る。

新しいResearch Diagnostic Suiteを作る。

Final sealedではない。

---

# 8. Experiment A — K Scaling

同じsemantic questionを維持したまま候補数だけ変える。

```text
K = 2, 4, 8, 12, 16
```

同一target。

追加distractorは段階的に増やす。

最低50 semantic states。

## Measure

- Accuracy
- target probability
- top1 margin
- permutation consistency

## Interpretation

K増加とともに単調低下するなら
candidate-set interactionが主要因。

---

# 9. Experiment B — Sequence Length vs K

Kを固定し、distractor/contextの長さだけ変更。

例:

```text
K=4, short context
K=4, long context
K=12, short context
K=12, long context
```

2×2 factorial。

## Goal

「候補数」なのか
「総token長」なのかを分離する。

---

# 10. Experiment C — Distractor Similarity

K固定。

- random irrelevant
- domain plausible
- lexical-overlap
- semantically close

を比較。

## Goal

attention dilutionではなく
semantic competitionが原因かを見る。

---

# 11. Experiment D — Rule Explicitness

同じ意味状態で:

- explicit else
- implicit else
- paraphrased fallback
- negated rule

を比較。

## Goal

Cross-Encoderのcapacityより
training representation coverage問題かを見る。

---

# 12. Milestone 27 Gate

以下のどれかを明確に判定する。

### Pattern A — K-driven
K増加だけで大幅低下。

→ choice encodingを優先。

### Pattern B — Length-driven
Kではなく総sequence lengthで低下。

→ formatting / token budget / architectureを検討。

### Pattern C — Distractor-driven
semantic similarityが主因。

→ hard-negative / scoring designを優先。

### Pattern D — Representation-driven
implicit/negative表現だけ崩れる。

→ data composition問題。

### Pattern E — Global ceiling
すべてをcontrolledにしても低性能。

→ backbone capacity疑いが強まる。

---

# 13. Milestone 28 — Bridge Benchmark

Blind v4を見た後なので、
Blind v4をDevにはしない。

新しい:

```text
data/rc3_bridge/
```

を作る。

目的:

> Blind v4で判明した難易度軸を再現するが、
> 文章・数値・ドメイン・templateは完全新規

のDevelopment Benchmark。

---

## Gate

- exact overlap = 0
- normalized structural overlapを記録
- semantic validator PASS
- Blind v4文章をコピーしない
- 400〜800 cases程度

BridgeはRC3開発中に参照してよい。

---

# 14. Milestone 29 — Minimal Architecture A/B

Milestone 26–28の結果に応じて実施。

---

## 14.1 Backbone-only Test

もしGlobal ceilingの疑いが強い場合:

現行choice encodingを固定して、

```text
Current backbone
vs
Larger compatible encoder
```

を比較。

モデルサイズはまず中規模拡大。

目安:
- 現行の1.5〜3倍程度

いきなり8Bへ行かない。

---

## 14.2 Choice-Encoding Test

K-drivenの疑いが強い場合:

backboneを固定して、

```text
Current all-choices-in-one-sequence
vs
candidate-separated scoring
```

を比較。

候補を独立スコアリングする方式を試す。

候補間比較が必要なら、
最終段のみjoint normalizationする。

---

## 14.3 2×2 Test

予算が許せば:

| | Current Encoding | Separated Encoding |
|---|---|---|
| Current Backbone | A | B |
| Larger Backbone | C | D |

最大4条件。

ただし最初はA/BまたはA/Cだけでよい。

---

# 15. Architecture Selection Metrics

主指標:

- RC3 Bridge overall
- logical operators
- perturbation
- variable K
- general choice
- paired both
- permutation
- high-confidence error

副指標:

- latency
- model size
- VRAM
- ONNX exportability

---

# 16. Architecture Promotion Gate

新architecture/backendを採用するには:

- Bridge Overall: current RC2.1より +8pt以上
- logical_operators: +10pt以上
- variable K: +10pt以上
- permutation >=95%
- Core retention >=95%
- ONNX export pathが現実的

のうち大半を満たすこと。

1〜2pt改善だけなら複雑化しない。

---

# 17. 8B級モデルへの移行条件

8B級は最終手段。

以下を満たした場合のみユーザーへ提案する。

1. Controlled diagnosticsでglobal capacity ceilingの証拠
2. mid-size backboneでも不足
3. candidate-separated scoringでも不足
4. data design改善でも不足
5. latency/VRAM tradeoffを提示済み

ユーザー承認なしに8Bへ移行しない。

理由:

- FP16 weightだけでも非常に大きい
- RTX A4000 16GBで余裕が小さい
- ERABIの「高速ローカル判断器」という価値を損なう可能性

---

# 18. Milestone 30 — RC3 Training

architecture選定後に初めてfull RC3 training。

Dataは:

- RC2.1 core retention
- operator diversity
- perturbation
- variable choice
- general choice
- natural Japanese

をtask-balancedに構成。

Bridgeはtrainに使用しない。

---

# 19. Milestone 31 — RC3 Development Gate

最低:

- Bridge Overall >= 88%
- logical operators >= 85%
- perturbation >= 85%
- general choice >= 85%
- variable choice >= 85%
- natural Japanese >= 90%
- paired both >= 80%
- permutation >= 95%
- core retention >= 96%

開発Gateを満たしたらfreeze。

---

# 20. Milestone 32 — Calibration

RC3 freeze後のみ。

以前のguardrailを適用:

- structural holdout
- variable K
- hard cases
- raw logits保存
- calibration signal不足ならT=1 NO-OPを許可

---

# 21. Milestone 33 — ONNX FP16

必須。

```text
PyTorch
→ ONNX FP32
→ ONNX FP16 CUDA
```

Gate:

- Top1 parity 100%
- probability drift acceptable
- calibration parity
- K=2..16 support
- no memory leak

---

# 22. Runtime Goal

RC3が大きくなっても:

- p50 <= 25msを第一目標
- p95 <= 40ms
- model <= 1.5GBを希望

これを超える場合は
性能改善とtradeoffを明示する。

---

# 23. Milestone 34 — Blind v5 Final Acceptance

RC3 model / calibration / ONNXをfreezeした後に
新規Blind v5を作る。

Blind v4 generator/templateをそのまま再利用しない。

---

## Blind v5 Gate

- Overall >= 88%
- No major family < 75%
- logical operators >=80%
- perturbation >=80%
- variable choice >=80%
- general choice >=80%
- paired both >=75%
- permutation >=95%
- high-confidence error <=7%
- PyTorch ↔ ONNX parity 100%
- leakage 0
- semantic errors 0

Blind v4の90% Gateより少し現実的に設定するが、
Blind v5はより広い分布を持たせる。

---

# 24. 実験予算

各Milestone:

- diagnostics:必要な範囲
- full training:最大3本

architecture comparisonは最大4条件。

大量探索禁止。

---

# 25. ユーザーへ戻る条件

以下のみ停止して報告。

1. Mid-size backend採用判断が必要
2. architecture全面変更が必要
3. 8B級への移行が必要
4. 3 full-trainingでRC3 Development Gate未達
5. Blind v5完了
6. 重大なdata/eval bug発見

それ以外は自律進行。

---

# 26. Codex / Antigravityへの最上位指示

```text
RC2.1 Blind v4結果を正式なFAILEDとしてfreezeしてください。

重要:
Blind v4 74.17%という結果だけから、
現行GLiClass約200M Cross-Encoderのcapacity ceilingが
実証されたとは扱わないでください。

Research Fresh 800件は複数runにわたり
誤答分析・データ追加・checkpoint selectionに使用されたため、
現在はDevelopment Benchmarkです。

Blind v4はRetired Diagnostic Benchmarkとして扱い、
今後trainやcheckpoint selectionには使用しません。

ERABI_RC3_DIAGNOSTIC_FIRST_ARCHITECTURE_ROADMAP.mdを
今後の最上位指示として実行してください。

最初に再学習せず、
Blind v4誤答124件を
family / K / token length / operator / implicitness /
distractor similarity / confidence
で分解してください。

次にfrozen RC2.1で、
K scaling,
sequence length × K,
distractor similarity,
explicit vs implicit rule
のcontrolled diagnosticを実施してください。

これにより、
K-driven / length-driven / distractor-driven /
representation-driven / global-capacity
のどれが主因か判定してください。

Blind v4をコピーせず、
同じ難易度軸を持つ完全新規RC3 Bridge Benchmarkを作成してください。

architecture変更は診断結果に応じて行います。

K-drivenならcandidate-separated scoringを優先。
Global capacityなら同じchoice encodingのまま
中規模larger backboneを比較してください。

いきなり8Bへ移行しないでください。

8B級は、
mid-size backbone、
candidate-separated scoring、
data design
でも不足する証拠が揃った場合のみ
ユーザーへ提案してください。

最終RC3はONNX FP16 CUDAへexport可能であることを必須とします。

Blind v5はRC3 freeze後にのみ作成し、
Blind v4はFinal Acceptanceに再利用しません。

計画だけ作って停止せず、
ユーザー確認条件に該当するまで自律的に
診断→比較→実装→評価
を進めてください。
```
