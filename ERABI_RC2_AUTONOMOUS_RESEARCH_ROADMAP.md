# ERABI RC2 Autonomous Research Roadmap
## Data Efficiency / Generalization / Jev-like Expansion

作成日: 2026-09-19
対象: Codex / Antigravity
開発モード: 自律研究・自律実装・自律評価

---

# 0. 現在地

ERABI RC1 は正式に凍結済みとする。

RC1の現状:
- Model: `W_general_v1`
- Release: `RC-1.0.0`
- Final Sealed Acceptance: PASS
- Final Integrity Audit: PASS
- ONNX Runtime CUDA FP16: PASS
- PyTorch ↔ ONNX FP32 ↔ ONNX FP16 Top-1 parity: 340/340
- ONNX FP16 model size: 約356.9 MB
- RTX A4000 warm p50: 約11.14 ms
- RTX A4000 warm p95: 約11.99 ms
- 約88.5 req/s
- 1000回連続推論で累積メモリリークなし

**RC1は今後の研究で変更・上書きしない。**

RC2は必ず別系統として開発する。

```text
release/rc1/
release/erabi-rc1-onnx-fp16/

research/rc2/
runs/rc2_*/
data/rc2_*/
```

---

# 1. RC2 North Star

ERABI RC2の目的は、

> RC1で成立したJev-like / System One型のローカルChoiceエンジンを、
> より少ないデータで、より広い未見表現・未見ドメイン・未見候補数へ一般化できるモデルへ発展させること。

単純にAccuracyを100%へ近づけることだけを目的にしない。

RC2では特に以下を研究対象とする。

1. 必要な学習データ件数
2. データ量と汎化性能の関係
3. 件数より多様性が重要か
4. 表現多様性・ドメイン多様性・operator多様性の寄与
5. 2択以外への一般化
6. より自然な日本語・長い入力への一般化
7. 新しいchoice taskへの転用
8. 小型モデルのまま性能を伸ばせる限界
9. RC1より汎用的でありながらONNX FP16で高速実行可能か

---

# 2. 最終ゴール

## Functional Goal

入力:

```text
context
question / instruction
arbitrary choices
```

出力:

```text
choice probabilities
top choice
review metadata
```

候補は固定ラベルではなく、推論時に任意に与えられること。

## Generalization Goal

学習時に見ていない:
- 表現
- ドメイン
- 数値
- operator combination
- candidate order
- candidate IDs
- 2〜16候補
- sentence order
- irrelevant information
- natural paraphrase

でも意味に従って判断できること。

## Efficiency Goal

「データを増やせば伸びる」だけではなく、

> どの種類のデータを何件程度与えれば、どの程度の汎化性能が得られるか

を定量化する。

## Runtime Goal

最終的に:

```text
model.onnx
tokenizer.json
calibration.json
manifest.json
```

でローカル実行可能。

必須:
- ONNX Runtime
- FP16
- CUDA
- PyTorchとのTop-1 parity

TensorRTはoptional。

---

# 3. 自律開発ルール

この文書以降、Codex / Antigravityは各小実験ごとにユーザー承認を求めない。

以下を自律的に繰り返す。

```text
現状確認
↓
仮説
↓
事前に成功条件を固定
↓
最小実験
↓
保存prediction/logitsから再集計
↓
リーク・ラベル・shortcut監査
↓
成功/失敗判定
↓
次の実験を自分で決定
```

計画だけ書いて停止しない。

---

# 4. ユーザーへ戻る条件

以下の場合だけユーザーへ報告して停止してよい。

1. RC1を変更する必要が発生した。
2. 外部有料サービス・クラウドGPU・有料APIが必要。
3. モデルアーキテクチャを全面変更する必要がある。
4. 同じMilestoneで3回のfull trainingを行ってもGate未達。
5. データの正解をプログラムで確定できず人間判断が必要。
6. モデルサイズを大幅に増やす必要がある。
7. 重大なデータリーク・ラベルバグを発見した。
8. 最終RC2候補が完成した。

それ以外は自律継続する。

---

# 5. 絶対ルール

## RC1 Freeze
RC1のweights / calibration / sealed evaluation / release artifacts / ONNX artifactsを変更しない。

## Evaluation Leakage禁止
評価問題をそのままtrainへコピーしない。
誤答分析から学習データを追加するときは別数値・別語彙・別domain・別templateで同じ能力を教える。

## GeneratorとValidatorを分離
新synthetic datasetは必ず generator / rendered natural language / independent semantic validator を分離する。
validatorはgenerator内部のtarget flagを信用しない。

## 1 experiment = 1 primary variable
一度に複数の主変数を変更しない。

---

# 6. 評価セットの階層

- Train: 学習専用
- Dev: checkpoint selection専用
- Research Fresh Eval: 研究中に繰り返し参照可、train利用禁止
- Rolling Fresh Eval: Milestoneごとに新規生成
- Final RC2 Sealed Acceptance: RC2候補freeze後にのみ生成

一度結果を見たsealed setは、次RCのfinal sealedには再利用しない。

---

# 7. Milestone 13 — RC1 Reproducibility Baseline

## Goal
RC2研究の前にRC1を基準点として完全固定する。

## Task
同一環境でPyTorch / ONNX FP32 / ONNX FP16を再実行し、主要評価セットを再測定する。

## Gate
- RC1 hash一致
- Top-1 parity 100%
- 主要metricsが保存値と一致
- ONNX FP16実行成功
- benchmark大幅変動なし

## Deliverable
`RC2_BASELINE_LOCKED.md`

---

# 8. Milestone 14 — Data Scaling Law

## Research Question
> ERABIは何件の学習データからJev-likeな能力を獲得するのか。

## Data Fractions
同じデータ分布・同じsampling policyから:

```text
12.5%
25%
50%
75%
100%
```

必要なら125% / 150%を追加可能。

## Important
単純に先頭N件を使わない。

各fractionで以下の比率を維持:
- task family
- operator
- domain
- choice count
- target distribution

## Training
各fractionで同じ:
- base model
- optimizer
- seed
- epoch policy
- checkpoint selection

データ量以外を変えない。

## Measure
- Train Accuracy
- Dev Accuracy
- Fresh Accuracy
- paired reasoning
- operator family accuracy
- domain accuracy
- NLL
- Brier
- training time
- updates
- GPU time
- VRAM
- performance / 1000 training samples

## Output
以下のcurveを作る。

```text
training samples → fresh accuracy
training samples → paired reasoning
training samples → NLL
training samples → training cost
```

## Gate
- 5点以上のsample-size curve
- semantic error 0
- split leakage 0
- 同一training policy
- saturation pointの暫定推定

---

# 9. Milestone 15 — Quantity vs Diversity

## Research Question
> 同じデータ件数なら、繰り返し量と多様性のどちらが汎化に効くか。

## Controlled Experiment
同じ件数で3条件以上:

### A — Low Diversity / High Repetition
少数template/domainを多数sampling。

### B — Balanced
RC1相当。

### C — High Diversity
多数template/domain/operator combinationを少数ずつsampling。

## Fixed
- total record count
- model
- optimizer
- training updates
- target distribution

## Measure
- seen-domain
- unseen-domain
- seen-phrasing
- unseen-phrasing
- operator generalization
- permutation
- NLL/Brier

## Gate
High Diversityが有利かどうかを少なくとも2つ以上のFresh軸で判定可能にする。

---

# 10. Milestone 16 — Diversity Attribution

## Research Question
汎化に効いているのは何か。

独立評価:
1. phrasing diversity
2. domain diversity
3. operator diversity
4. numerical state diversity
5. candidate diversity

## Method
一度に1軸だけ減らすablation。

## Deliverable
`DATA_DESIGN_FINDINGS.md`

記録:
- 最も効く多様性
- 効果の小さい多様性
- shortcutを生みやすい偏り
- 推奨sampling policy

---

# 11. Milestone 17 — Variable Choice Count

## Goal
固定2〜3択依存から離れる。

## Choice Counts
```text
2
3
4
6
8
12
16
```

同じsemantic taskを異なる候補数へ展開する。

追加候補:
- plausible distractor
- irrelevant distractor
- semantically close distractor

## Gate
- 2〜4 choices: >= 90%
- 6〜8 choices: >= 85%
- 12〜16 choices: >= 75%
- candidate permutation consistency >= 95%
- choice IDs変更で大幅崩壊なし
- RC1 core tasks -2pt以内

---

# 12. Milestone 18 — Natural Japanese Robustness

## Goal
synthetic template感の強い文章だけでなく、自然な日本語でも判断できるようにする。

## Variation
- 丁寧語
- 口語
- 箇条書き
- 長文
- 冗長表現
- 主語省略
- 条件の前後入替
- 否定
- 二重否定
- 例外
- 「ただし」
- 「原則」
- 「〜の場合を除く」
- irrelevant context

## Data Policy
意味をプログラムで確定できる範囲を優先。
曖昧な自然文を無理に正解付きデータにしない。

## Gate
Fresh natural-language suite:
- overall >= 85%
- no major family < 70%
- paired reasoning >= 75%
- high-confidence wrong <= 5%

---

# 13. Milestone 19 — General Choice Expansion

## Goal
ERABIをrule-engine imitationだけでなく、より広いJev-like Choice Engineにする。

## Target Families
- support routing
- short NLI
- semantic relation
- intent selection
- policy choice
- instruction separation
- negative goal
- reverse criterion
- lightweight prioritization
- structured triage

一度に全部増やさず、干渉を計測しながら追加する。

## Gate
- fresh general overall >= 85%
- each major family >= 75%
- RC2 core reasoning退行 <= 2pt
- candidate permutation >= 95%

---

# 14. Milestone 20 — Data Efficiency Recommendation

ここで一度モデル改善を止め、研究結果をまとめる。

## 必須回答

### Q1
RC2相当の性能に必要な最低データ数はどの程度か。

### Q2
データを2倍にしたときFresh性能は何pt伸びるか。

### Q3
件数を2倍にするのとtemplate/domain/operator diversityを増やすのでは、どちらが効率的か。

### Q4
性能が飽和し始めるsample countはどこか。

### Q5
最もsample-efficientなdata mixtureは何か。

## Deliverable
`ERABI_DATA_SCALING_REPORT.md`

可能ならグラフも保存する。

---

# 15. Milestone 21 — RC2 Candidate Selection

## Goal
最も大きいモデルではなく、

> 精度・汎用性・データ効率・速度のバランスが最も良いcheckpoint

を選ぶ。

## Candidate Gate

### Core
- rule/operator fresh >= 90%

### Natural Language
- >= 85%

### Variable Choices
- 2〜8 choices >= 85%
- 12〜16 choices >= 75%

### General Choice
- >= 85%

### Permutation
- >= 95%

### Regression
RC1主要能力から大幅退行なし。

### Runtime
PyTorchでRC1比2倍以上遅くならない。

---

# 16. Milestone 22 — Calibration

RC2 weightsをfreezeしてから実施。

RC1のTを流用しない。

RC2専用:
```text
calibration
fresh_calibration_eval
```

を新規生成。

## Gate
- top1不変
- fresh NLL改善
- Brier悪化なし
- high-confidence error <= 5%
- calibration artifact model hash binding

---

# 17. Milestone 23 — ONNX FP16

## Goal
RC2もRC1同様、Python/PyTorchなしで高速推論可能にする。

## Pipeline
```text
PyTorch
↓
ONNX FP32
↓
parity
↓
ONNX FP16 CUDA
↓
parity
↓
benchmark
```

## Gate
- PyTorch ↔ ONNX FP32 Top-1 100%
- PyTorch ↔ ONNX FP16 Top-1 100%
- representative eval parity
- probability drift acceptable
- calibration適用可能
- 2〜16 choices動作
- memory leakなし

## Performance Goal
RC1基準:
- p50 ~11.14 ms
- p95 ~11.99 ms

RC2目安:
- p50 <= 15 ms
- p95 <= 20 ms

汎用性向上のため多少遅くなることは許容。

---

# 18. Milestone 24 — Final Sealed Acceptance RC2

RC2候補・calibration・ONNX artifactをfreezeした後にのみ生成。

## Scope
- core rules
- operators
- priority
- natural Japanese
- unseen domains
- variable choices
- general choice
- permutation
- distractors

## Final Gate
- Overall >= 90%
- No major family < 75%
- Critical paired reasoning >= 80%
- Permutation >= 95%
- 2〜8 choice performance >= 85%
- semantic data error 0
- leakage 0
- calibration pass
- ONNX parity pass

---

# 19. 実験予算

各Milestone:
- full training 最大3回
- diagnostic evaluationは必要な範囲で可

3回で結論が出ない場合:
`MILESTONE_BLOCKED.md`

を作る。

---

# 20. Model Capacity変更ルール

RC2の基本方針は現在のGLiClass instruct-base系を維持する。

以下の証拠が揃うまで大型化しない。

- train performance高い
- data diversity十分
- checkpoint問題なし
- sampling問題なし
- simple curriculumでも改善なし
- 3実験以上で同じcapacity ceiling

その場合のみlarger encoder/backend比較をユーザーへ提案する。

---

# 21. 自律Decision Rules

- Train高 / Fresh低 → generalization問題。data diversityを疑う。
- Train低 → optimization / capacity / budgetを疑う。
- Data量増加でFresh上昇 → scaling継続候補。
- Data量増加で飽和 → 量ではなくdiversityへ移行。
- Diversity増加でFresh上昇 → data designを優先。
- Diversity増加でCore低下 → task-balanced sampling。
- choice countだけで崩壊 → candidate-set generalization課題。
- natural Japaneseだけで崩壊 → synthetic phrasing dependency。
- 全条件で同時に飽和 → capacity検討。

---

# 22. 毎実験の記録

最低限:

```text
hypothesis
changed_variable
fixed_variables
dataset_hashes
training_config
checkpoint_hash
metrics
fresh_metrics
failure_cases
decision
next_action
```

summaryだけでなくprediction/logitsも保存する。

---

# 23. 過学習防止

禁止:
- eval誤答文のtrainコピー
- sealed testの再利用
- family名だけ変えた実質同一template
- target leakage
- choice position leakage
- numeric shortcut
- domain-specific shortcut
- validatorとgeneratorのtruth共有

---

# 24. RC1との関係

RC1は比較基準。

RC2が必ずしも全metricでRC1を超える必要はない。

RC2の価値は:
- 少ないデータ
- 広い汎化
- 多候補
- 自然文耐性
- 汎用choice

にある。

RC1の100% synthetic sealed scoreだけを追いかけてRC2を過適合させない。

---

# 25. RC2成功の定義

ERABI RC2成功とは、

> 「このデータセットでは100%」ではなく、
> 未見の意味表現・未見ドメイン・可変候補に対して高い安定性を持ち、
> その性能がどの程度のデータ量と多様性によって得られたか説明できること。

---

# 26. 最終成果物

```text
release/erabi-rc2/
release/erabi-rc2-onnx-fp16/

ERABI_RC2_MODEL_CARD.md
ERABI_DATA_SCALING_REPORT.md
ERABI_GENERALIZATION_REPORT.md
FINAL_ACCEPTANCE_RC2.md
FINAL_ACCEPTANCE_RC2_VERIFIED.md
```

---

# 27. Codex / Antigravityへの実行指示文

```text
ERABI RC1は正式にfreezeします。
今後RC1のweights、calibration、sealed evaluation、
ONNX release artifactを変更・上書きしないでください。

ここからERABI RC2 Researchを開始します。

RC2の目的は単純な正答率改善ではありません。

最重要テーマは、

1. 学習データ件数とFresh汎化性能のScaling Law
2. Quantity vs Diversity
3. phrasing / domain / operator diversityの寄与
4. 2〜16候補への一般化
5. より自然な日本語への一般化
6. より広いJev-like Choice taskへの拡張
7. 小型モデルのままどこまで汎化可能か
8. 最終的なONNX FP16実行

です。

ERABI_RC2_AUTONOMOUS_RESEARCH_ROADMAP.mdを
今後の最上位研究指示として扱ってください。

小実験ごとにユーザー承認を求めず、
各MilestoneのGoalとGateに従って

診断
→ 仮説
→ 実験設計
→ データ監査
→ 学習
→ Fresh評価
→ 保存logitsから再集計
→ failure analysis
→ 次実験決定

を自律的に繰り返してください。

計画だけ作って停止しないでください。

各Milestoneにつきfull trainingは最大3回です。
3回でGate突破または研究結論が得られない場合のみ、
MILESTONE_BLOCKED.mdを作成してユーザーへ戻ってください。

まずMilestone 13でRC1 reproducibility baselineを固定し、
その後Milestone 14 Data Scaling Lawへ進んでください。

Data Scalingでは12.5%, 25%, 50%, 75%, 100%の
学習データfractionを同一条件で比較し、
training samplesに対するFresh Accuracy、
paired reasoning、NLL、training costのcurveを取得してください。

続いてQuantity vs Diversity、
Diversity Attribution、
Variable Choice Count、
Natural Japanese Robustness、
General Choice Expansionへ自律的に進めてください。

評価データをtrainへコピーせず、
generatorとsemantic validatorを独立させ、
RC1を上書きせず、
1 experiment = 1 primary variableを守ってください。

RC2候補をfreezeした後にのみ
新しいcalibrationとFinal Sealed Acceptanceを作ってください。

Final Acceptance合格後は、
PyTorch → ONNX FP32 → ONNX FP16 CUDAへexportし、
Top-1 parity、probability drift、latency、memory stabilityを検証してください。

TensorRTは必須ではありません。

最終成果は、
「何件のどのようなデータで、どこまでJev-likeな汎化が得られるか」
を説明できるERABI RC2としてください。
```
