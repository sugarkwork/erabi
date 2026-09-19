# ERABI Autonomous Development Roadmap
## Codex / Antigravity 自律開発指示書

作成日: 2026-09-19

# 0. North Star

ERABIの最終目的は、

> 自然文の状況・指示・任意の候補群を入力し、候補ごとの信頼可能な確率を高速に返す、ローカル動作の小型Jev型判断エンジン

を作ること。

単なる固定テンプレート分類器ではなく、言い換え、未見ドメイン、条件分岐、AND/OR、inclusive/exclusive boundary、優先順位/override/first-match、negation/goal switch、candidate order変更に対して、同じ意味なら同じ判断を行えることを目指す。

APIは当面 `review` 固定。高確率だから自動acceptする機能は最終検証完了まで有効化しない。

# 1. 自律開発モード

この文書以降、Codex / Antigravityは小さな実験ごとにユーザー承認を求めない。

以下のループを自律的に実行する。

```text
現状読込
  ↓
最大のボトルネックを1つ特定
  ↓
仮説を明文化
  ↓
最小実験を事前登録
  ↓
データ監査
  ↓
実行
  ↓
保存logitsから再集計
  ↓
コード・ラベル・リーク監査
  ↓
成功/失敗判定
  ↓
次の最小実験を自分で選択
```

計画書だけ作って停止しない。非破壊・ローカル・既存設計内の作業は原則としてそのまま実行する。

# 2. ユーザーへ確認が必要なのは例外だけ

次の場合のみ停止してユーザー判断を求める。

1. 既存の基準モデル・成果物を削除/上書きする必要がある。
2. 外部有料API・クラウドGPU・外部サービスの契約/課金が必要。
3. リポジトリ外・OS全体へ大きな変更が必要。
4. 3回の独立した改善実験を行っても同じMilestoneを突破できない。
5. モデルアーキテクチャを全面変更する必要がある。
6. 要求仕様そのものを変えないと先へ進めない。
7. データの意味や正解を人間判断なしでは確定できない。

それ以外は自律実行する。

# 3. 絶対ルール

## 3.1 過去成果物を上書きしない
各runは新しいディレクトリへ保存する。

## 3.2 Evaluation Leakage禁止
以下は学習に直接使用しない。
- eval_v2
- transfer_probe
- smoke_cases
- fresh evaluation
- sealed acceptance evaluation
- 過去に評価専用と指定されたfamily

評価で誤答した文章をコピーしてtrain化しない。必要な能力をtrainへ追加する場合は、別数値・別文章・別domain・別templateで新しいtraining例を作る。

## 3.3 データ意味整合性
新データは必ず generator / rendered text / independent semantic validator の3者を分離する。
validatorはgenerator内部のtruth flagをそのまま信用せず、rendered `context + question + choices` から期待targetを再導出する。
1件でも不一致なら学習を開始しない。

## 3.4 1実験1主要変数
原則として data mixture / replay / checkpoint selection / training budget / loss / model architecture を一度に複数変更しない。

# 4. Complexity Ladder

問題が出たときは以下の順で解決を試みる。

1. Data correctness
2. Sampling / weighting / checkpoint
3. Training schedule
4. Objective
5. Model/backend

上位Levelへ進む前に、下位Levelで解けない証拠を残す。

# 5. 実験予算

各Milestoneにつき full training experiment は最大3回。
診断のみの評価は必要な範囲で可。

3回でGate未達なら `MILESTONE_BLOCKED.md` を作成し、ユーザーへ報告する。
1回の失敗で大規模変更へ飛ばない。

# 6. Milestone 5 — Balanced Core Reasoner

## Goal
M3の論理能力とM4のpriority phrasing能力を同一checkpointで両立する。

## Development Gate

### M3 retention
- `eval_v2 Accuracy >= 97.0%`
- Diff-Target Both >= 88%

### Priority
- Fresh priority/phrasing Accuracy >= 80%
- Diff-Target Both >= 60%
- Same-Target Both >= 75%

### Exception
- `eval_exception Accuracy >= 98%`
- Diff Both >= 95%

### Smoke
- >= 10/12

### Data
- semantic mismatch = 0
- exact input overlap = 0

## 自律的に選べる改善策
- checkpoint trajectory / early stopping
- fresh retention sentinel
- replay selector修正
- replay比率の小変更
- curriculum
- task-balanced sampling
- small task weighting

ただしComplexity Ladderを守る。

## Pass時
`W_core_v1` としてfreezeする。

# 7. Milestone 6 — Operator Generalization

## Goal
特定のpriority文面ではなく論理operatorそのものへ一般化する。

対象:
- AND
- OR
- >= / >
- <= / <
- override
- default + exception
- first-match / precedence
- priority ranking
- negation
- goal switching

Train / Dev / Freshで表現familyを完全分離。

## Gate
新規 `fresh_operator_eval`:
- Overall Accuracy >= 85%
- Diff/contrast pair both >= 70%
- 各主要operator family >= 60%
- 0% familyを残さない
- Core retentionはMilestone 5主要指標から -2pt以内

# 8. Milestone 7 — Domain & Perturbation Robustness

## Goal
意味に無関係な変更で判断が変わらない。

対象:
- unseen domains
- candidate permutation
- choice ID変更
- context sentence order
- irrelevant distractor
- numerical scale changes
- paraphrase
- 2〜5 choices

## Gate
- Overall >= 85%
- Candidate permutation top1 consistency >= 95%
- Domain別Accuracyで極端な崩壊なし
- どのdomainも60%未満に落ちない
- Core/operator retention -2pt以内

# 9. Milestone 8 — General Choice Tasks

ERABIを合成ルール専用から、よりJev型の一般choice engineへ広げる。

追加順:
1. support / routing
2. short NLI
3. semantic relation
4. intent selection
5. instruction separation
6. negative goal / reverse criteria

## Gate
- Fresh multitask Overall >= 82%
- 各task family >= 70%
- Core rule reasoning退行 <= 2pt

# 10. Milestone 9 — Calibration

モデル重みがfreezeしてからのみ実施。

新規 calibration / fresh_calibration_eval を完全分離。

## Gate
- finite T
- optimizer boundaryへ張り付かない
- Fresh NLLが明確に改善
- Brierが悪化しない
- Accuracy/top1不変
- p>=0.90帯 error rate <=5%を目安
- artifactがmodel/hash/formatter/precisionと結合

# 11. Milestone 10 — Release Candidate

## Goal
ローカルJev型choice engineとして使える状態に固定する。

API:
- localhost
- 1 worker
- review default
- model version
- calibration version
- full candidate probabilities
- raw choice order保持
- no silent fallback
- fail closed on calibration mismatch

Performance目安:
- warm p50 <= 50 ms
- p95 <= 100 ms
- no memory leak
- probabilities sum ~= 1
- deterministic eval mode

# 12. Final Sealed Acceptance

Release Candidateをfreezeした後にのみ作る。

AgentはRCをfreezeする前にsealed setのモデル結果を見てはいけない。

## Final Gate
scope内で:
- Overall Accuracy >= 85%
- Critical paired reasoning >= 70%
- No family < 60%
- permutation consistency >= 95%
- semantic data errors = 0
- calibration NLL/Brier pass
- high-confidence error rate acceptable
- API contract pass

失敗したsealed setはretired evaluationとして保存し、trainへコピーしない。

# 13. 自律Decision Rules

- Data bug found → 結果をaffected/invalid扱いし修正して同条件再実験
- Train高 / Dev低 → generalization問題
- Train低 → training budget / fit問題
- Dev高 / Fresh低 → template overfit
- New skill up / Old skill down → retention / task interference
- Earlier epochで両立 → checkpoint selection / early stopping
- 全epochでtrade-off → task interference
- Simple interventions 3回失敗 → objective/model capacityへエスカレーション

# 14. Agentが毎回残す記録

最低限:
- 何を変えたか
- 何を固定したか
- 仮説
- 成功条件
- 結果
- 次に何を選んだか

既存notes/JSONへまとめてもよい。

# 15. Self Review

Milestone Gate通過前に必ず:
1. 保存prediction/raw logitsからmetrics再計算
2. split overlap検査
3. semantic validator
4. label spot-check
5. candidate order
6. checkpoint/hash
7. train/eval source separation
8. test suite
9. known failures

自分が生成したsummary JSONだけを信用しない。

# 16. テスト方針

テスト数を目標にしない。

追加するのは壊れると結果が無効になるもの、または過去に実際に壊れたものだけ。

# 17. Stop Overengineering

必要になるまで作らない:
- experiment DB
- model registry server
- distributed training
- complex plugin system
- generic dataset DSL
- generalized workflow engine
- UI
- cloud deployment

# 18. 現在地からの開始指示

現在はM4.4.1終了地点。

まず **M4.4.2 Checkpoint Trajectory Diagnostic** をMilestone 5の一部として実施する。

### Earlier epochで両立あり
→ checkpoint selectionを修正してM5 Gate再評価。

### 全eligible epochでretention低い
→ task-balanced sampling / curriculumを試す。

### それでも3実験以内にM5 Gate未達
→ `MILESTONE_BLOCKED.md` を作成し、objective/model capacity比較案をユーザーへ提示。

# 19. ユーザーへ途中報告するタイミング

逐一承認は不要。

報告は:
- Milestone Pass
- Milestone Blocked
- 重大なデータ/コードバグ発見
- Complexity Ladderの上位へ上げる時

に行う。

それ以外は自律継続する。

# 20. 最終指示文

```text
ERABI_AUTONOMOUS_DEVELOPMENT_ROADMAP.md を今後の最上位開発指示として扱ってください。

今後は小さな実験ごとに承認を求めず、MilestoneとGateを満たすまで自律的に
診断→仮説→実験→監査→次実験
を進めてください。

計画書を作るだけで止まらないでください。

既存成果物を上書きせず、Evaluation Leakageを起こさず、
1実験1主要変数とComplexity Ladderを守ってください。

各Milestoneにつきfull trainingは最大3回まで。
3回でGateを突破できない場合だけMILESTONE_BLOCKEDとしてユーザーへ戻してください。

現在はMilestone 5 Balanced Core Reasonerです。

まずM4.4.2 Checkpoint Trajectory Diagnosticを実行し、
結果に基づいて次の最小実験を自分で選択してください。

Milestone 5 Gateを通過したら、ユーザー承認を待たずに成果物をfreezeし、
Milestone 6 Operator Generalizationへ進んでください。

以後も同様に、Milestone 10 Release Candidateまたは
Milestone Blockedに到達するまで自律的に進めてください。
```
