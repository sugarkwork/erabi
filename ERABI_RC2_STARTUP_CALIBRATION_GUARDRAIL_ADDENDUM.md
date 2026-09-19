# ERABI RC2 Startup Audit / Calibration Guardrail Addendum

作成日: 2026-09-20

## 0. 結論

今回共有された `STATUS.md` では、ERABI RC1は以下まで完了している。

- Final Acceptance / Integrity Audit
- ONNX Runtime CUDA FP16 release
- GitHub Public Release

一方、今回の `review_bundle(20260919-155140).zip` はRC2 Milestone 13/14の成果物ではなく、
**RC1 Milestone 9 Calibrationの4ファイルだけを含むバンドル**だった。

したがって:

1. RC1は変更しない。
2. RC2 Autonomous Roadmapをそのまま開始する。
3. ただしRC2のCalibration Milestoneには、以下の追加guardrailを適用する。

---

# 1. 今回のZIP実物監査

ZIP:

- files: 4
- calibration.json
- calibration_report.json
- calibration.jsonl
- fresh_calibration_eval.jsonl

このバンドル単体にはraw logitsやtraining artifactsは入っていないため、
温度最適化そのものを完全に独立再計算するreview bundleとしては不十分。

RC1の最終監査結果を否定するものではないが、
RC2ではcalibration review bundleにraw logits sidecarを含める。

---

# 2. Calibration / Fresh Calibration の構造重複

実ファイルを正規化監査した。

Calibration:
- 100 cases
- 50 groups
- 5 categories
- 全件2-choice
- normalized structural signature: 20種類

Fresh Calibration Eval:
- 100 cases
- 50 groups
- 同じ5 categories
- 全件2-choice
- normalized structural signature: 20種類

数値、`CALIB` / `FCALIB`、ID番号を正規化すると:

- Fresh 100/100 casesがCalibration側の構造signatureと一致
- normalized question patternもFresh 100/100で既出
- ordered choice definitionsもFresh 100/100で既出

つまりこれは

> 「別record・別数値のholdout」

としては有効だが、

> 「未知の表現構造に対するfresh calibration validation」

としては弱い。

---

# 3. Temperature Scalingの注意

現在のcalibration artifact:

- T=1 calibration NLL ≈ 1.72e-7
- Fresh T=1 NLL ≈ 2.69e-7
- Accuracy 100%
- optimal T ≈ 0.256

つまりT=1の時点でほぼ完全な確率になっている。

T<1は確率をさらにsharpにする。

この状況では、
NLLを `1e-7 → ~0` にする改善は数値上は成立しても、
実運用上のcalibration改善を十分に証明しない。

特にerror caseが0件のdatasetでは、
「誤答時のconfidenceを下げる」という校正能力を評価できない。

RC1はfreeze済みなので変更しない。
この知見はRC2のCalibration設計へ反映する。

---

# 4. RC2 Calibration Guardrail

Milestone 22では以下を追加する。

## 4.1 Structural Holdout

calibrationとfresh_calibration_evalは、
単に数字や固有名詞だけ変えない。

最低限:

- phrasing family分離
- domain分離を一部含む
- operator composition分離を一部含む
- choice count分布の違いを含む

を行う。

normalized structural signature overlapを集計する。

目標:
- exact model input overlap = 0
- normalized structural template overlapを可能な限り低くする
- overlapがある場合は件数と理由を明記

---

## 4.2 Variable Choice Count

RC2が2〜16 choicesをscopeに含むなら、
calibrationも2択だけにしない。

代表分布を含める:

- 2
- 3
- 4
- 6
- 8
- 12
- 16

全候補数を均等にする必要はないが、
production scopeを代表すること。

---

## 4.3 Calibration Identifiability

以下の場合:

- calibration Accuracy = 100%
- fresh calibration Accuracy = 100%
- T=1 NLLが既に非常に小さい
- error case / borderline caseがほぼ0

なら、温度最適化結果を無条件採用しない。

推奨判定:

```text
if baseline NLL is already negligible
and fresh set has no meaningful uncertainty/errors:
    calibration_decision = NO_OP_OR_INSUFFICIENT_SIGNAL
    temperature = 1.0
```

「最適化できた」ことと「校正が必要だった」ことを分離する。

---

## 4.4 Calibration Dataset Difficulty

人工的に誤答を作る必要はない。

ただしcalibration suiteはproduction distributionを代表し、
以下を含める:

- easy
- medium
- difficult
- semantic near-ties
- semantically similar distractors
- unseen phrasing
- longer context
- variable choice count

モデルが100%でもよいが、
その場合は「校正性能を十分評価できない」と明記する。

---

## 4.5 Metrics

最低限:

- Accuracy
- NLL
- Brier
- confidence histogram
- high-confidence error rate
- per-choice-count metrics
- per-task-family metrics

ECEは補助指標として使用可能だが、
small sampleでは主Gateにしない。

---

## 4.6 Review Bundle

RC2 calibration review bundleには最低限:

```text
calibration.json
calibration_report.json
calibration.jsonl
fresh_calibration_eval.jsonl
raw_logits_calibration.jsonl
raw_logits_calibration.jsonl.manifest.json
raw_logits_fresh.jsonl
raw_logits_fresh.jsonl.manifest.json
structural_overlap_audit.json
```

を含める。

これにより第三者が温度探索・NLL/Brierを独立再計算できる。

---

# 5. RC2開始指示

現在共有されたSTATUSにはRC2 Milestone 13以降の完了記録はない。

したがって次はロードマップどおり:

1. Milestone 13 — RC1 Reproducibility Baseline
2. Milestone 14 — Data Scaling Law
3. Milestone 15 — Quantity vs Diversity
4. Milestone 16 — Diversity Attribution

へ自律進行する。

RC1 calibrationをやり直す必要はない。

---

# 6. Codex / Antigravityへの追補指示

```text
ERABI RC1はfreeze済みのまま維持してください。

今回のreview bundleを再監査したところ、
M9 calibration / fresh_calibration_evalは
exact recordとしては分離されていますが、
数値・CALIB/FCALIB識別子を正規化すると
fresh 100/100件がcalibration側と同じ構造テンプレートに対応していました。

RC1を変更する必要はありません。

ただしRC2 Milestone 22 Calibrationでは、
単なる数値差し替えholdoutではなく、
phrasing/domain/operator composition/choice countを含む
structural holdoutを導入してください。

また、
Accuracy 100%かつT=1 NLLが既にほぼ0のdatasetでは、
T<1でNLLをさらに0へ近づけることを
自動的に「校正改善」とみなさないでください。

calibration signalが不足している場合は
NO_OP_OR_INSUFFICIENT_SIGNALとしてT=1を維持する選択肢を設けてください。

RC2 calibration review bundleにはraw logitsとsidecar manifestを含め、
第三者がtemperature/NLL/Brierを独立再計算可能にしてください。

現時点ではRC1 calibrationを再実行せず、
ERABI_RC2_AUTONOMOUS_RESEARCH_ROADMAP.mdに従って
Milestone 13 RC1 Reproducibility Baselineから自律進行してください。

その後Milestone 14 Data Scaling Lawへ進み、
12.5/25/50/75/100%のsample-size curveを取得してください。
```
