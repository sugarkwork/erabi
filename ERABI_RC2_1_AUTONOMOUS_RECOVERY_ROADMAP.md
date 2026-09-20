# ERABI RC2.1 Autonomous Recovery Roadmap
## Blind Failure Recovery without Test-Set Tuning

作成日: 2026-09-20
対象: Codex / Antigravity
前提: RC2は凍結済み。Blind v3 は正式に FAILED として保存済み。

---

# 0. 現在地

RC2 Blind Sealed Re-Acceptance v3:

- Overall Accuracy: 71.04%
- Pair Both: 55.00%
- Permutation Consistency: 86.67%
- K=2..8: 74.17%
- K=12..16: 61.67%
- High-confidence error rate: 28.09%
- PyTorch ↔ ONNX FP16 parity: 100%

Family別:
- domain_transfer: 100.0%
- core_rules: 98.3%
- priority_exception: 95.0%
- variable_choice: 71.7%
- logical_operators: 53.3%
- natural_japanese: 51.7%
- general_choice: 50.0%
- perturbation_invariance: 48.3%

RC2は狭い意味で失敗したモデルではない。
core explicit rules / domain transfer / explicit priority-exception / ONNX FP16 runtime は成立している。

一方、Jev-like汎用Choice Engineとして必要な未見論理表現・自然日本語・semantic-preserving perturbation・general choice・多候補・OOD確率品質には不足がある。

---

# 1. 最重要ルール

## Blind v3を開発に使用しない

禁止:
- Blind v3個票をtrainへコピー
- Blind v3文章の言い換えをtrainへ追加
- Blind v3をDev/checkpoint selectionへ使用
- Blind v3で再評価しながらRC2.1を改善

許可:
- family-level failure category を研究課題の方向付けに使うこと

Blind v3は永久にretired blind benchmarkとして保存する。

---

# 2. RC2.1 North Star

RC2.1の目的:

> RC2が既に持つcore / priority / domain能力を保持しながら、
> 未見表現・自然日本語・一般Choice・摂動・可変候補に対する真の汎化能力を高める。

目標はBlind v3で100%ではない。
新しいResearch Fresh Evaluationで能力を改善し、RC2.1をfreezeした後に別のBlind v4で一発評価する。

---

# 3. Complexity Policy

RC2.1では、まずモデル構造を変えない。

維持:
- knowledgator/gliclass-instruct-base-v1.0
- standard CE
- current formatter
- current tokenizer
- current inference contract

順序:
1. Data coverage / diversity
2. Sampling / task balance
3. Training schedule
4. Calibration
5. Model capacity

最初の3 full-trainingで改善できなければ、初めてlarger backendを検討する。

---

# 4. RC2.1 Research Evaluation Set

Blind v3とは完全に別に、開発用の新規Research Fresh Suiteを作る。

名称例:
data/rc2_1_research_fresh/

これはsealedではない。
研究中に繰り返し使ってよいが、trainには使わない。

---

# 5. Research Fresh Suite構成

最低800 casesを推奨。

## A. logical_operator_generalization
200 cases

対象:
- AND
- OR
- NOT
- >= / >
- <= / <
- default + exception
- override
- first-match
- priority
- reverse criterion

同じoperatorを多数の未知表現familyで記述する。
単語差し替えではなく構文を変える。

## B. natural_japanese
200 cases

スタイル:
- 実務メール
- チャット
- FAQ
- 規約文
- 社内通知
- 操作手順
- 会話
- 敬語
- 省略
- 倒置
- 否定
- 二重否定
- 例外節
- 後置条件
- 長文内の関連1文
- unrelated filler

synthetic感の強い定型文だけにしない。
ただし意味はprogrammatic validatorで確定可能にする。

## C. perturbation_invariance
160 cases + paired transformations

同一semantic caseに対して:
- sentence order
- candidate order
- candidate ID
- irrelevant sentence insertion
- numeric format
- punctuation
- polite/neutral style
- parenthetical notes

を変える。正解は変わらない。

## D. general_choice
160 cases

対象:
- routing
- short NLI
- intent
- semantic relation
- policy choice
- structured triage
- instruction/background separation
- negative goal
- reverse criterion

候補text自体もtrainと別表現にする。

## E. variable_choice
80+ cases

K:
2, 3, 4, 6, 8, 12, 16

各Kで plausible / close / irrelevant distractor を混ぜる。

---

# 6. 新規Training Dataの設計

RC2.1では反復よりunique semantic groupsを増やす。

推奨初期規模:
3,000〜4,000 unique records

目安:

### Stream A — Core / Retention 30%
- core rules
- boundary/comparison
- composite logic
- priority exception
- core goal switching

### Stream B — Generalization 70%
- logical operators: 25%
- natural Japanese: 20%
- perturbation: 15%
- general choice: 20%
- variable-choice expansion: 10%

残りはtask balancing用。

---

# 7. Unique Group優先

同一groupを大量replayしない。

各familyで:
- template count
- domain count
- semantic-state count
- operator count
- choice-count distribution

をmanifestへ保存する。

unique_group_ratio >= 0.7 を目安。

---

# 8. Phrasing Diversity

1 operatorあたり:
- 8〜12 train phrasing families
- 2〜4 dev phrasing families
- 4+ research fresh phrasing families

を分離する。

Train / Dev / Research Freshで同じphrase templateを使わない。

---

# 9. Domain Diversity

Blind v3ではdomain_transferは100%だったため、domainは最優先課題ではない。

ただし語彙shortcut防止のため、各operator/choice taskを複数domainへ直交させる。

新しいdomain数を増やすより、同じoperatorを異なるdomainで表現することを優先する。

---

# 10. General Choiceの改善方針

固定候補IDや固定語彙を避ける。

候補ID:
- a,b,c
- choice_1
- route_x
- random UUID-like IDs

を混ぜる。

candidate semanticsもfamilyごとに変える。

---

# 11. Perturbation Training

同じcaseを複数変形する場合、1 semantic stateに対して2〜3 transformations程度に制限。

目的はtemplate暗記ではなくinvariance学習。

---

# 12. Variable Choice Training

K分布を明示的に管理する。

推奨:
- K=2: 20%
- K=3: 20%
- K=4: 15%
- K=6: 15%
- K=8: 10%
- K=12: 10%
- K=16: 10%

大Kではdistractor qualityを重視する。

---

# 13. RC2.1 Full Training Experiments

最大3回。

## Run 1 — Diversity Expansion
変更:
- unique data diversityのみ増加
- standard CE
- B0から学習
- task-balanced batches

目的:
data coverageだけでどこまで回復するか。

## Run 2 — Sampling Balance
Run 1の結果から弱い能力のsampling比率だけ調整。
model/lossは変更しない。

## Run 3 — Training Schedule
必要な場合のみ:
- update budget
- curriculum
- staged mixing

を変更。

まだloss/model architectureは変えない。

---

# 14. RC2.1 Development Gate

Research Fresh Suite:
- Overall >= 88%
- logical operators >= 85%
- natural Japanese >= 85%
- general choice >= 85%
- perturbation invariance >= 90%
- variable choice overall >= 85%
- family minimum >= 80%
- paired both >= 85%
- permutation >= 95%

Core retention:
- eval_v2 >= 96%
- priority/exception >= 95%
- domain transfer >= 95%

High-confidence error:
- raw T=1では記録のみ
- calibration後 <= 5%

---

# 15. Failure Analysis Rules

失敗時は個票そのものをtrain化しない。

分類:
- unswitched
- wrong operator
- negation inversion
- distractor capture
- candidate-position bias
- instruction/context confusion
- long-context miss
- overconfidence

各カテゴリについて別domain・別phraseのtrain例を生成する。

---

# 16. Calibrationは最後

RC2.1 weightsをfreezeするまでtemperature fittingをしない。

Calibration datasetは:
- difficult cases
- variable K
- natural language
- operators
- general choice
- perturbation

を含む。

---

# 17. Calibration Gate

まず単一global temperature。

Pass条件:
- fresh calibration NLL改善
- Brier悪化なし
- top1不変
- high-confidence error <=5%

K別・family別calibrationも確認する。

---

# 18. ONNX

RC2.1 final model freeze後:

PyTorch → ONNX FP32 → ONNX FP16 CUDA

RC2のexport pipelineを再利用する。

Gate:
- Top1 parity 100%
- probability drift acceptable
- no memory leak
- p50 <= 15ms目安
- p95 <= 20ms目安

---

# 19. Final Blind v4

RC2.1 freeze後にのみ作る。

Blind v3は再利用しない。

data/sealed_acceptance_rc2_1_blind_v4/

最低480 cases。

手順:
1. Test authoring
2. semantic validation
3. leakage audit
4. token-length audit
5. Git precommit
6. SHA256 freeze
7. one-shot inference
8. no edits after results

---

# 20. RC2.1 Final Gate

- Overall >= 90%
- family minimum >= 80%
- logical operators >= 85%
- natural Japanese >= 85%
- general choice >= 85%
- perturbation >= 90%
- variable choice >= 85%
- paired both >= 85%
- permutation >= 95%
- K2..8 >= 85%
- K12..16 >= 80%
- high-confidence error <=5%
- ONNX parity 100%

---

# 21. 成果物

ERABI_RC2_1_MODEL_CARD.md
ERABI_RC2_1_GENERALIZATION_REPORT.md
ERABI_RC2_1_CALIBRATION_REPORT.md
FINAL_ACCEPTANCE_RC2_1_BLIND.md
FINAL_ACCEPTANCE_RC2_1_BLIND_VERIFIED.md

release/rc2_1/
release/erabi-rc2_1-onnx-fp16/

---

# 22. ユーザーへ戻る条件

以下の場合のみ停止:
1. 3 full-trainingでもDevelopment Gate未達
2. model capacity ceilingが明確
3. larger backendが必要
4. semantic labelsを人間判断しないと作れない
5. RC2.1 candidate freeze完了
6. Blind v4完了

それ以外は自律進行する。

---

# 23. Codex / Antigravityへの最上位指示

RC2 Blind v3の正式結果を受理します。

RC2はBlind Re-AcceptanceにFAILしましたが、
core_rules 98.3%、priority_exception 95.0%、
domain_transfer 100.0%、
PyTorch↔ONNX parity 100%を達成しているため、
RC2の全成果を破棄しません。

RC2はそのままfreezeしてください。

Blind v3は永久にretired blind benchmarkとして保存し、
RC2.1のtrain/dev/checkpoint selectionには一切使用しないでください。

次にERABI RC2.1 Researchを開始してください。

RC2.1の改善対象はfamily-levelでのみ定義します:
- logical operators
- natural Japanese
- general choice
- perturbation invariance
- variable choice
- confidence calibration

Blind v3の文章や失敗個票をtrainへコピーしたり、言い換えて利用したりしないでください。

新しいResearch Fresh SuiteをBlind v3とは完全独立に作成してください。

RC2.1ではモデル構造を変えず、まずData Diversityを拡大してください。

初回training datasetは3,000〜4,000 unique recordsを目安とし、
Stream A Core保持30%、Stream B Generalization70%程度から開始してください。

同一groupの過反復より、unique semantic state / phrase / operator combinationを優先してください。

full trainingは最大3回です。

Run 1: Diversity Expansion
Run 2: Sampling Balance
Run 3: Training Schedule

の順に進め、standard CE / current GLiClass baseを維持してください。

Research Fresh Gate:
Overall >=88%
logical >=85%
natural >=85%
general choice >=85%
perturbation >=90%
variable choice >=85%
family min >=80%
paired >=85%
permutation >=95%
eval_v2 >=96%
を目標としてください。

Gateを満たしたmodelのみRC2.1 candidateとしてfreezeしてください。

その後RC2.1専用calibrationを行い、最後に完全新規・事前commit・one-shotのBlind v4を作成してください。

Blind v3をRC2.1の性能確認には使用しないでください。

Blind v4でPASSまたはFAILが確定するまで、小実験ごとのユーザー承認は不要です。
