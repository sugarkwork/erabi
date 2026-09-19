# ERABI — Final Acceptance Integrity Audit → ONNX FP16 Release

作成日: 2026-09-19

## 0. 結論

`FINAL_ACCEPTANCE_REPORT.md` 上では RC-1.0.0 (`W_general_v1`) が全Acceptance Gateを通過している。

ただし以下は非常に強い結果なので、正式リリース前に一度だけ独立監査する。

- sealed 120/120 正解
- paired reasoning 60/60
- permutation 120/120
- 全family 100%
- calibrated NLL 0.0000
- calibrated Brier 0.0000

この監査ではモデルを再学習しない。Gateを後付け変更しない。sealed setの結果を見てデータを書き換えない。

監査PASS後のみ、ONNX FP16 exportへ進む。

---

# Phase A — Final Acceptance Integrity Audit

## 1. Freeze確認

以下を記録する。

- RC model checkpoint path
- model weights SHA256
- tokenizer/config SHA256
- source commit / repository state
- calibration artifact SHA256
- calibration T full precision
- sealed dataset SHA256
- sealed dataset生成日時
- model freeze日時
- calibration freeze日時

重要:

**sealed datasetがRC/model/calibration freeze後に作られたか、少なくともモデル選択・校正・学習へ一度も使用されていないことを証明する。**

日時だけでなく、run logs / manifests / source referencesを照合する。

## 2. Leakage監査

sealed 120 casesを、以下すべてと比較する。

- 全train
- 全dev
- calibration
- fresh calibration eval
- historical eval
- transfer probes
- smoke
- operator eval
- robustness eval
- general-choice eval

最低限:

1. exact normalized model-input fingerprint
2. group/scenario ID
3. canonical semantic state
4. same values + same operator + same target structure
5. candidate texts/order structure

を確認。

完全一致だけでなく、既知の合成generatorで抽出可能なsemantic-state overlapも集計する。
解析対象外件数も必ず併記する。

## 3. Sealed target独立検証

generatorが保存したtruth flagやtargetをそのまま再利用しない。

rendered:
- context
- question
- choices

から、独立semantic validatorで期待targetを再導出する。

120/120を検証。

validator非対応ケースがあれば、「0 semantic errors」と総括せず未検証件数を記録する。

## 4. Raw logitsから全指標を再計算

summary JSONや保存probabilityを信用せず、**raw logits** から独立再計算する。

### T=1
- Accuracy
- paired both
- family metrics
- permutation consistency
- NLL
- Brier

### calibrated T
- Tのfull precisionを使用
- softmax(logits / T)
- NLL
- Brier
- confidence bins
- p>=0.90 error rate

注意:
- probability rounding前に計算
- `0.0000`ではなく科学表記/full precisionも保存
- clampした場合はclamp値を記録

NLL/Brierが本当に数学的にほぼ0なのか、表示丸めだけなのかを区別する。

## 5. Calibration independence

T*=0.2560 がsealed testを使わずに推定されたことを確認する。

- calibration dataset hash
- calibration count
- optimizer bounds
- optimum full precision
- boundary hit有無
- fresh calibration eval

を確認。

sealed logits/labelsを温度探索・モデル選択へ使っていないこと。

## 6. Permutation audit

Permutation 120/120について:

- candidate orderが本当に変わっている
- choice IDだけでなくcandidate textsの順序も変化
- target mappingを正しく追随
- original/permutedのraw logitsをcandidate identityへre-mapして比較

を確認する。

最低限:
- top1 consistency
- probability distribution difference
- max abs probability drift

を保存する。

## 7. Family別誤差

今回は全family 100%なのでaccuracyだけでは差が見えない。

各familyについて:
- mean target probability
- minimum target probability
- mean margin(top1-top2)
- worst 3 cases
- NLL
- Brier

を出す。

## 8. Acceptance audit PASS条件

以下すべて:

- sealed dataset leakage問題なし
- rendered semantics 120/120確認
- raw logits再計算で120/120一致
- permutation実装正常
- T推定にsealed未使用
- NLL/Brier再計算一致
- hash / freeze lineage説明可能
- 重大なコード/データ不具合なし

PASSなら `FINAL_ACCEPTANCE_VERIFIED.md` を作る。

問題があれば:
- 結果を隠さない
- sealed setを学習へコピーしない
- `FINAL_ACCEPTANCE_AUDIT_FAILED.md`
- 原因と影響範囲を記録
- 必要ならRCを再開発

---

# Phase B — ONNX FP16 Release

Phase A PASS後のみ実施。

## 9. ONNX export

最初の目標はTensorRTではなく:

> **ONNX Runtime + FP16**

成果物例:

```text
release/rc1_onnx/
  model.onnx
  tokenizer.json
  tokenizer_config.json
  config.json
  calibration.json
  manifest.json
```

## 10. Export contract

PyTorchとONNXで同じ入力契約を使う。

最低限:
- dynamic batch
- dynamic sequence length
- max sequence <= current runtime contract
- 2〜16 choices
- same formatter
- same tokenizer
- raw logits output

Temperature scaling / softmaxは最初はONNX graph外の後処理を推奨する。

## 11. FP32 ONNX parity

最初にONNX FP32。

代表評価:
- sealed acceptance
- fresh operator
- robustness
- smoke

でPyTorchと比較。

Gate:
- Top1一致 100%
- candidate order一致
- raw logits max abs errorを記録
- probability max abs driftを記録
- Accuracy/NLL/Brierが実質同等

FP32 parityを確認してからFP16へ進む。

## 12. FP16 ONNX

ONNX Runtime CUDAでFP16化。

Gate目安:
- PyTorch/FP32 ONNXとのTop1一致 100%
- sealed top1 120/120維持
- paired reasoning維持
- permutation consistency維持
- NLL/Brierの悪化がごく小さい
- calibration artifactを同じTで適用可能

FP16で確率品質が崩れる場合、Top1だけ一致していてもPASSとしない。

## 13. Benchmark

同一PCで:
- PyTorch current runtime
- ONNX FP32
- ONNX FP16 CUDA

を比較。

測定:
- cold start
- warm p50
- p95
- throughput
- VRAM
- RAM
- 1000回程度の繰返しでmemory drift

TensorRTは必須ではない。

## 14. Final artifact

ONNX FP16がPASSしたら:

```text
release/erabi-rc1-onnx-fp16/
```

を作り、
- model
- tokenizer
- calibration
- manifest
- usage example
- benchmark
- limitations

を保存する。

## 15. Codex / Antigravityへの指示

```text
FINAL_ACCEPTANCE_REPORT.md を確認しました。

RC-1.0.0は報告上、
sealed 120/120、pair 60/60、permutation 120/120、
全family 100%、calibrated NLL/Brier 0.0000で
全Gateを通過しています。

結果が非常に強いため、
次は追加学習をせず Final Acceptance Integrity Audit を実施してください。

sealed setのfreeze lineage、全過去データとのleakage、
rendered textからの独立semantic validation、
raw logitsからのAccuracy/NLL/Brier再計算、
calibration independence、
candidate permutation実装
を監査してください。

0.0000のNLL/Brierは丸め表示ではなくfull precision値も保存してください。

問題がなければ FINAL_ACCEPTANCE_VERIFIED.md を作成し、
そのままユーザー承認を待たず ONNX FP16 Releaseへ進んでください。

まずONNX FP32 parityを確認し、
その後ONNX Runtime CUDA FP16へ変換してください。

PyTorch ↔ ONNX FP32 ↔ ONNX FP16で、
Top1、raw logits、確率、NLL/Brier、paired reasoning、
permutation consistencyを比較してください。

最終目標は
`model.onnx + tokenizer + calibration + manifest`
でローカル実行可能なRCを作ることです。

TensorRTは今回は必須ではありません。

Integrity Auditで重大問題が見つかった場合は、
ONNX exportへ進まず停止し、
FINAL_ACCEPTANCE_AUDIT_FAILED.mdを作成してください。
```
