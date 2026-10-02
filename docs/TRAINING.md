# 追加学習・データセット形式

ERABIはGLiClassの事前学習weightsを起点にした追加学習です。毎回ランダム初期化から学習しているわけではありません。今回のDecision Mix V2版はWorld Choice版checkpointから全weightsを追加学習しています。LoRAやオンライン学習ではありません。

## データ形式

UTF-8 JSONLで1行1問です。これは説明用の人工例で、人手goldではありません。

```json
{"schema_version":"1","id":"sample-001","group_id":"story-001","context":"ノート7冊と消しゴム2個を買った。","question":"全部で何個？","choices":[{"id":"a","text":"9個"},{"id":"b","text":"10個"}],"target":{"kind":"hard","choice_id":"a"},"language":"ja","family":"everyday_arithmetic","review_status":"unreviewed"}
```

`target.choice_id`は候補IDを参照します。候補を入れ替えても正解IDを維持し、教師分布がある場合は同じpermutationを適用します。学習・推論で入力整形を共通化し、候補paddingは損失とSoftmaxから除外します。

同じ原題、会話、エピソード、反実仮想、言い換え、候補順違いは同じ`group_id`／`canonical_group_id`にまとめます。groupをまたいでtrain/dev/calibration/final_testへ流出させません。

## Decision Mix V2（2026-09-30）

カテゴリは、人間可読のNPC内面・優先目標、架空platformer、架空voxel survival、防御目的のコマンド危険性、オリジナル反実仮想、非露骨な一般ゲートの6種類です。超短縮keyやopaque行動コード、センシティブな生成領域は対象にしていません。

生成した4,111件に対しschema・全入力token上限・重複・正解位置・候補長shortcutを検査し、正解を見せない教師の独立再判定を行いました。60件の抜き取りレビューで明確な問題を9件隔離しましたが、全件の人手検証済みデータではありません。同じ教師モデルによる再判定一致も、独立した正解保証ではありません。

| 分割 | 件数 | 用途 |
|---|---:|---|
| train | 3,238 | weights更新 |
| dev | 353 | epoch選択 |
| calibration | 200 | 保留。今回未使用 |
| final_test | 311 | 選択後の固定評価（109 canonical groups） |

全入力は60〜511トークンで、黙ったtruncationはありません。データ本体、教師応答、変換ログは非公開のままです。pip・Git・モデル配布に含めません。スクリプトだけでは私有データを再現できません。

### 学習と選択

| 項目 | 設定 |
|---|---|
| 起点 | World Choice V1の選択済みcheckpoint |
| epoch | 3。毎epoch保存・dev評価 |
| learning rate | 1e-6 |
| microbatch / 勾配蓄積 | 1 / 16 |
| 精度・GPU | FP16 AMP、GPU 1基 |
| seed | 20260930 |
| 候補 | 学習時にシャッフル、ID対応を維持 |
| replay | World 1,008、Practical 1,024、Exam 91（trainだけ） |
| 1 epochの総行数 | 5,361 |

devのfamily macroと既存能力のretention gateで選択しました。final_testはcheckpoint選択とhash固定の後に開き、校正や再選択には使っていません。

| checkpoint | dev正答率 | dev family macro |
|---|---:|---:|
| 追加学習前 | 59.49% | 59.21% |
| epoch 1 | 67.71% | 65.81% |
| epoch 2 | 70.54% | 67.72% |
| epoch 3（採用） | 71.39% | 68.52% |

全epochでretention gateを通過しました。学習とERABI評価に合計122.42分かかりましたが、これはGPU・冷却・入力分布に依存する1回の実験値です。finalの結果と限界は[ベンチマーク](BENCHMARKS.md)を参照してください。

## 実行方法

ソースと正当に用意したローカルデータが必要です。GPU学習や大容量weightsはpipパッケージに含めません。

```powershell
python -m pip install -e ".[dev]"
python -m scripts.train_decision_mix_v2 --dry-run --output-dir runs/dm2-check
python -m scripts.train_decision_mix_v2 --base-model path/to/base-checkpoint --output-dir runs/dm2-training --epochs 3 --lr 1e-6
```

このスクリプトは`data/decision_mix_v2/`と以前のreplay・retention用データを利用します。既存のrunは上書きせず、新しい出力ディレクトリを指定してください。実装は[train_decision_mix_v2.py](../scripts/train_decision_mix_v2.py)、生成・監査は[build_decision_mix_v2.py](../scripts/build_decision_mix_v2.py)と[audit_decision_mix_v2.py](../scripts/audit_decision_mix_v2.py)です。外部API生成は別途許可・予算・送信可能範囲を確認して実行します。

## ONNXへの変換と検証

```powershell
python -m pip install onnx
python scripts/export_exam_qa_erabi_v1_onnx.py --checkpoint runs/dm2-training/checkpoint_selected --valid runs/dm2-training/filtered_final.jsonl --output-dir runs/dm2-training/onnx --max-tokens 512
```

歴史的なスクリプト名ですが、任意checkpointをFP32/FP16に変換できます。候補数と入力長は動的です。変換後はPyTorchとTop-1・logitsを照合し、配布するweightsとの対応をSHA256で保存します。今回の配布物は校正未実施で、古いcheckpointの校正ファイルを流用しません。

## 追加学習で守ること

- final_testを毎epochのモデル選択に使わない。epoch選択はdev、確率校正は独立calibration、最終報告はfinal_test。
- 元データを複製・シャッフルしても情報量は増えない。原題groupを分割しない。
- 新データだけに偏ると旧能力が落ちるので、train replayとretention評価を分けて使う。
- JSON key順・候補順・無関係候補追加などの揺らぎは、正解対応と意味を維持した独立評価で測る。完全不変を保証しない。
- 合成ラベル、校正された確率、高い最大確率のいずれも正解保証ではない。

## 過去の実験

Practical V1、Exam-QA、World Choice、長文、量子化の経緯・実測は[STATUS](../STATUS.md)とGit履歴に残しています。古いモデルの測定を今回の配布モデルの結果として扱わないでください。RC3の設計契約は[設計仕様](ERABI_DESIGN.md)を参照してください。

## 開発者向けの作業記録

[STATUS.md](../STATUS.md)には実測の履歴、失敗した試行、未完了事項、次の作業を記録しています。利用方法は[README](../README.md)、配布モデルの性能と測定条件は[ベンチマーク](BENCHMARKS.md)を参照してください。
