# ERABI RC2 — M14.1 Compute-Controlled Scaling Audit
## Data量とOptimization量の因果分離 + M15への自律移行指示

作成日: 2026-09-20  
対象: Codex / Antigravity

## 0. 結論

Milestone 13 / 14 の成果は有効です。ただし M14 は全fractionを「10 epochs固定」で学習しているため、dataset fractionが大きいほど総optimizer update数も増えています。

したがって現在のM14は **Epoch-Controlled Empirical Scaling Curve** として扱い、unique data量の効果とcompute/update量の効果をM14.1で分離します。

M14自体はinvalidにしません。M14.1終了後、両曲線を `ERABI_DATA_SCALING_REPORT.md` に併記します。

---

# 1. 現時点で有効なM14知見

- General Choice: 284件（12.5%）ですでに99.2%。非常にsample-efficient。
- Fresh Operator: 69.0 → 77.0 → 93.0 → 92.0 → 93.0%。50%付近からplateau傾向。
- Fresh Robustness: 92.6 → 98.1 → 100 → 100 → 100%。50%付近でほぼ飽和。
- Core eval_v2: 57.5 → 78.0 → 89.5 → 93.5 → 99.5%。100%まで明確に伸びる。
- Fresh Phrasing: 43.3 → 70.0 → 69.2 → 70.8 → 77.5%。100%で再上昇。

従って「全能力が50〜75%で飽和」とは結論しません。

正確には、

> **能力ごとにsample requirementが異なる。Operator / Robustnessは早期飽和傾向、Core / Phrasingは追加データ依存が残る。**

---

# 2. M14.1 Research Question

> M14の性能向上は、unique data量の増加によるものか、それともoptimizer update数の増加によるものか。

---

# 3. 実験設計

新しいデータは作りません。

M14で作成済みfractionから以下の3 anchorを使います。

- 12.5%
- 50%
- 100%

100%は既存M14 runをreferenceとして再利用します。

原則として新規full trainingは以下の2本だけです。

- 12.5% equal-update
- 50% equal-update

結果が曖昧な場合のみ、25%または75%を追加で1回実行可能です。

---

# 4. Compute Control

M14の100% runが実行した総optimizer update数を `U_ref` としてtraining logから取得します。

12.5% / 50%も、

```text
optimizer_updates = U_ref
```

まで学習します。

datasetを使い切ったらseeded reshuffleして再利用します。

固定:
- model
- optimizer
- lr
- weight decay
- micro batch
- grad accumulation
- seed
- 1:1 Task-Balanced Micro-Batch
- formatter
- dev policy

同じrecord orderを単純loopせず、各cycleでseeded reshuffleします。

---

# 5. EpochではなくUpdate数で停止

見かけ上、12.5%は約80 epochs、50%は約20 epochs相当になる可能性がありますが、実装はepoch数ではなく

```text
max_optimizer_updates = U_ref
```

で停止します。

端数やstream長の差を吸収するためです。

---

# 6. Checkpoint Evaluation Schedule

devを見る回数も統一します。

各runで:

```text
10%, 20%, 30%, ... 100% of U_ref
```

の10地点だけをcheckpoint候補にします。

best checkpoint selection ruleはM14と同じにします。

100%既存runのepoch 1〜10が同じupdate比率に対応する場合は既存結果を再利用します。対応しない場合は100% checkpointを再評価するだけにし、原則再学習しません。

---

# 7. 必須ログ

各fractionで保存:

- unique records available
- unique records actually seen
- total record exposures
- mean exposures / unique record
- optimizer updates
- effective epochs
- wall time
- GPU time
- best checkpoint update
- train/dev metrics
- fresh metrics

---

# 8. 評価セット

M14と同じセットを使います。

- fresh_general
- fresh_operator
- fresh_robustness
- fresh_phrasing
- eval_v2
- eval_exception
- smoke

M14.1では新evalを作りません。

---

# 9. 必須比較

## Epoch-controlled（既存M14）

| Fraction | Unique N | Updates | General | Operator | Robustness | Phrasing | Core |
|---|---:|---:|---:|---:|---:|---:|---:|

## Compute-controlled（M14.1）

| Fraction | Unique N | Fixed Updates | Exposures/sample | General | Operator | Robustness | Phrasing | Core |
|---|---:|---:|---:|---:|---:|---:|---:|---:|

さらに各suiteで:

```text
compute_gain = equal_update_metric - original_10epoch_metric
```

を算出します。

---

# 10. Interpretation Rules

### Pattern A — Compute-limited

12.5% equal-updateが複数Fresh suiteで+10pt以上改善し、100%との差が5pt以内程度まで縮む。

→ M14の差の大部分はdata量ではなくupdate不足。

### Pattern B — Unique-data-limited

equal-updateでも12.5% / 50%と100%の差が2つ以上のFresh suiteで10pt超残る。

→ unique data / diversityが本質。M15へ進む強い根拠。

### Pattern C — Capability-specific

General / Operator / Robustnessは追いつくがCore / Phrasingだけgapが残る。

→ 能力ごとにsample efficiencyが異なる。M15ではCore/Phrasingを中心に設計。

### Pattern D — Small-data overfit

12.5% equal-updateでtrain/devは高いがFreshが悪化。

→ 小さなunique setを反復しても汎化しない。データ多様性が必要。

---

# 11. NLLの扱い

M14 Fresh NLLは:

```text
0.3465
0.5777
0.0902
0.2576
0.1379
```

と非単調です。

Accuracyだけでなく、
- wrong-case confidence
- target margin
- per-family NLL

も確認します。

M14.1ではcalibrationしません。T=1固定です。

---

# 12. M14.1 Completion Gate

性能閾値ではなく、因果解釈が可能になればPASS。

必須:
- 12.5 / 50 / 100のequal-update比較
- optimizer update数一致
- dev evaluation回数一致
- training policy一致
- leakage 0
- semantic data変更なし
- Combined interpretation作成

---

# 13. M14 Report更新

M14の既存数値は削除しません。

`ERABI_DATA_SCALING_REPORT.md` に以下を追記します。

1. Epoch-Controlled Scaling
2. Compute-Controlled Scaling
3. 両者を統合した解釈
4. 能力別saturation point
5. data量とcompute量のどちらが支配的か

---

# 14. M15への自律移行

M14.1完了後、ユーザー承認を待たずM15へ進みます。

M15の固定データ件数はM14/M14.1から自律的に決定します。

基準:
- saturation直前
- full datasetより十分小さい
- diversity差を観測しやすい

現時点の暫定候補は約1,000〜1,200件。

---

# 15. M15 Quantity vs Diversity

同一の:
- total records
- optimizer updates
- task balance
- target distribution
- model
- optimizer
- dev policy

で3条件を比較します。

### A — Low Diversity
少数domain / template / operator構成を高反復。

### B — Balanced
現在の代表sampling。

### C — High Diversity
より多くのdomain / template / operator combinationを浅く広くsampling。

総unique件数だけでなく、semantic-state diversityも記録します。

---

# 16. M15最重要Metric

Train Accuracyを主指標にしません。

優先:
1. unseen phrasing
2. unseen domain
3. fresh operator
4. core paired reasoning
5. semantic-state transfer
6. NLL / confidence

High Diversityが2つ以上のFresh軸でBalanced/Lowより改善した場合、「量より多様性」の実証根拠とします。

---

# 17. Codex / Antigravityへの実行指示

```text
Milestone 13 / 14の結果を確認しました。

M13はPASSとして維持してください。

M14の5点scaling curveも有効ですが、
10 epochs固定のためdataset fractionが増えるほど
総optimizer update数も増えており、

unique data量
と
optimization compute量

が交絡しています。

M15へ進む前に、
M14.1 Compute-Controlled Scaling Auditを実施してください。

新しいデータは作りません。

M14で作成済みの
12.5%, 50%, 100%
をanchorとして使用してください。

100% M14 runの総optimizer update数をU_refとして取得し、
12.5%と50%もdatasetをseeded reshuffleしながら再利用して
U_refまで学習してください。

micro batch, grad accum, lr, optimizer,
1:1 task-balanced micro-batch,
seed, formatter, dev policyは変更しません。

dev/checkpoint評価も
10%,20%,...,100% of U_ref
の10地点に統一してください。

100%は既存M14 runをreferenceとして再利用してください。
原則、新規full trainingは12.5%と50%の2本だけです。

各fractionについて
unique sample count
total sample exposures
exposures per unique sample
optimizer updates
Fresh General
Fresh Operator
Fresh Robustness
Fresh Phrasing
eval_v2 Core
paired reasoning
NLL
を出してください。

M14の結論は
「全体が50〜75%で飽和」
とはしないでください。

現状の正確な観察は、
Operator/Robustnessは50%付近で飽和傾向、
General Choiceは12.5%から高性能、
Core/Phrasingは100%までデータ依存が残る、
です。

M14.1終了後、
Epoch-controlled curveとCompute-controlled curveを
ERABI_DATA_SCALING_REPORT.mdへ併記してください。

その結果から、
Compute-limited / Unique-data-limited /
Capability-specific / Small-data-overfit
を判定してください。

M14.1完了後はユーザー承認を待たず、
Milestone 15 Quantity vs Diversityへ進んでください。

M15ではLow Diversity / Balanced / High Diversityを
同一件数・同一update数で比較してください。

RC1は一切変更しません。
```
