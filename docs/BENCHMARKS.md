# ベンチマークと推論性能

正答率はデータ分布に、速度は入力長・候補数・backend・精度・GPU温度・同時負荷に依存します。以下は保証値ではなく、特定条件での実測です。旧モデルと今回のモデル、リモートAPIとローカル推論を区別しています。

## Decision Mix V2：同じ311件での比較

2026-09-30、train/dev/calibrationとcanonical group単位で分離したfinal 311件・109 groupsです。全システムに同じcontext、question、候補IDと順序を渡しました。ERABIのfinal入力は88〜511 tokens。testのSHA256は`c9e8227429fe5388cae9b45bcc040d029336cfb2c988bd2c32b5faa19f3677ee`です。データ本体は非公開です。

| システム | 正答数 | 正答率 | family macro | group全問正答率 | NLL | Brier |
|---|---:|---:|---:|---:|---:|---:|
| ERABI World Choice（学習前） | 183/311 | 58.84% | 56.31% | 27.52% | 1.3814 | 0.5964 |
| ERABI Decision Mix V2（学習後） | 210/311 | 67.52% | 63.64% | 39.45% | 0.8642 | 0.4318 |
| Laya 0.3.21 reviewed | 107/311 | 34.41% | 34.38% | 9.17% | 1.4433 | 0.7690 |
| Jev 1.13（リモート） | 287/311 | 92.28% | 90.95% | 80.73% | 0.4382 | 0.1463 |

### カテゴリ別

| カテゴリ | 件数 | ERABI学習前 | ERABI学習後 | Laya | Jev |
|---|---:|---:|---:|---:|---:|
| コマンド危険性 | 82 | 63.41% | 80.49% | 34.15% | 96.34% |
| 一般ゲート | 48 | 81.25% | 85.42% | 52.08% | 97.92% |
| NPC内面・目標 | 45 | 37.78% | 42.22% | 26.67% | 82.22% |
| 架空platformer | 40 | 40.00% | 37.50% | 32.50% | 87.50% |
| 架空voxel survival | 29 | 48.28% | 58.62% | 31.03% | 86.21% |
| 反実仮想・既知弱点 | 67 | 67.16% | 77.61% | 29.85% | 95.52% |

改善は均一ではなくplatformerは低下しました。単純な「最長候補を選ぶ」baselineも55.63%あるため、候補長shortcutには注意が必要です（同率最長は正解候補を含めば一致と数える定義）。

canonical group単位のpaired bootstrap 10,000回による正答率差の95%区間は、追加学習後−前が+8.68pt［+3.69, +13.97］、学習後ERABI−Layaが+33.12pt［+25.16, +40.85］、Jev−学習後ERABIが+24.76pt［+19.05, +30.63］でした。

### 比較条件と限界

- ERABIはDecision Mix V2のtrainで追加学習済み。Layaには同じ追加学習を行っていません。これは同じ入力での分布適応比較であり、一般的・中立的な性能順位ではありません。
- 正解はDeepSeek生成＋正解非表示の同系列教師再判定による暫定合成ラベルです。60件のレビューで明確な問題9件を隔離しましたが、全件の独立した人手goldではありません。
- ERABIはdevでepoch 3を選択・hash固定後にfinalを評価しました。calibration 200件は未使用。全システムの確率は正解保証ではなく、NLL/Brierも参考値です。
- Layaは[公式リポジトリ](https://github.com/NandhaKishorM/laya)commit `9d955671415fc19f069b9cc998928075c1f255ec`、標準Router、英語66件・多言語245件。BF16 autocast有効、compile/fast path無効。入力truncation、候補48-token上限到達、候補崩壊はいずれも0でした。
- Jevの要求モデルは`typesafe/jev-1.13`、実応答モデルは全件`typesafe/jev-1.13-20260917`です。リモートサービスの内部weights・学習データ・GPUは確認できません。
- 単一seed・単一runの結果であり、実ゲーム、複雑なコマンド、一般会話全体での安全性や品質を保証しません。

## 速度・RAM・VRAM

今回の配布ONNXを使った311件の単件測定を以下に追記します。初回ダウンロードを除外し、8回ウォームアップ後、tokenizationを含めて計測します。GPUは同期済みです。

| 実行系 | 初期化 | p50 / p95 | 処理量 | ピークRSS | 全GPUピーク−開始 |
|---|---:|---:|---:|---:|---:|
| Decision Mix V2 GPU ONNX FP16 | 8.86秒 | 74.93 / 121.25ms | 12.73件/秒 | 1,628MiB | 約2,591MiB |
| Decision Mix V2 CPU ONNX FP32 | 11.22秒 | 778.00 / 1,524.25ms | 1.20件/秒 | 3,815MiB | 使用なし |

CPUはRyzen 7 5800X（8C/16T）です。PyTorchは8 threads、ONNX Runtimeは既定のthread設定を使いました。今回のピークRSSは約3.73GiBで、1プロセスにつき少なくとも約4GiBの空きRAMに、OS・他アプリ分の余裕を足してください。8GB以上のシステムRAMを出発点にできますが、複数ワーカーは個別に測定してください。測定中にモデルアップロードも走っていたため、完全な無負荷測定ではありません。

今回のGPUはRTX A4000 16GB、PyTorch 2.6.0+cu124・ONNX Runtime 1.21.0。87〜91℃、SM clock中央値315MHzと強く低下していました。Laya測定時は中央値1,470MHzだったため、上の速度差をモデルやbackendの優劣とは判断できません。GPUの同温度・同クロックでの再比較は未実施です。311件の整形済み入力は88〜511 tokensでした。

Layaの同じ311件の測定は、RTX A4000 16GB、batch 1で初期化6.96秒、平均35.89ms、p50 32.81ms、p95 52.13ms、27.84件/秒でした。PyTorch peak allocatedは3,568.54MiB、reservedは3,754MiB。全GPU使用量は開始2,000MiB→ピーク6,011MiB（差4,011MiB）。GPUは89〜91℃です。

Jevは8並列で311要求を40.43秒、7.69件/秒、要求単位p50 652.70ms、p95 843.50msでした。ネットワークとサーバー待ち時間込みであり、ローカル推論のGPU速度やVRAMと直接比較できません。リモートVRAMは未取得です。

### 再測定

正当に保有するJSONLを指定します。privateデータはリポジトリに含まれません。入力にあるコマンドは実行せず、分類だけを行います。

```powershell
python -m pip install -e ".[dev]"
python -m scripts.benchmark_release --model path/to/onnx-fp32 --format onnx-fp32 --device cpu --input path/to/test.jsonl --output runs/cpu-check.json --threads 8
python -m scripts.benchmark_release --model path/to/onnx-fp16 --format onnx-fp16 --device cuda:0 --input path/to/test.jsonl --output runs/gpu-check.json --threads 8
```

`nvidia-smi`のVRAMは全GPUのサンプリング値で、他プロセスを含み、短いピークを見逃すことがあります。プロセスのVRAM allocationと同一視しないでください。RAMはPython・ランタイム・展開weights・一時bufferを含むRSSです。

## 公開データでの旧ERABI対Laya

2026-09-29に、公開test splitから固定seedで作った3,584件・10 suitesを同じ順序で評価しました。ここでのERABIは今回のモデルではなく、0.1.4既定のWorld Choice版ONNX FP16です。Jevと今回のDecision Mix V2版はこの表では未測定です。

| データ | 件数 | 旧ERABI正答率 | Laya正答率 | 旧ERABI p50 | Laya p50 |
|---|---:|---:|---:|---:|---:|
| Emotion | 566 | 49.3% | 50.5% | 23.38ms | 35.04ms |
| MASSIVE intent 英語 | 452 | 85.6% | 69.5% | 29.45ms | 37.14ms |
| MASSIVE intent 日本語 | 452 | 79.6% | 58.2% | 30.01ms | 31.23ms |
| MASSIVE intent 中国語 | 452 | 61.5% | 56.9% | 29.91ms | 32.77ms |
| Prompt injections | 116 | 51.7% | 66.4% | 24.93ms | 37.95ms |
| SST-5 | 500 | 36.2% | 43.4% | 22.66ms | 35.04ms |
| Toxic-chat jailbreak | 182 | 75.3% | 78.6% | 30.52ms | 33.42ms |
| Toxic-chat toxicity | 264 | 69.3% | 59.8% | 25.43ms | 36.54ms |
| XNLI 英語 | 300 | 62.7% | 86.0% | 30.85ms | 39.19ms |
| XNLI 中国語 | 300 | 48.7% | 75.3% | 35.48ms | 32.71ms |

総正答率は両方2,199/3,584＝61.36%、suite単純平均は旧ERABI 61.99%・Laya 64.46%。旧ERABIはintent、Layaは推論・感情・一部gateで強い結果でした。

| 実行系 | 初期化 | 平均推論 | 処理量 | ピークRSS | 全GPUピーク−開始 |
|---|---:|---:|---:|---:|---:|
| 旧ERABI ONNX FP16 | 7.65秒 | 31.07ms | 32.19件/秒 | 1,614MiB | 約1,582MiB |
| Laya標準BF16 | 8.45秒 | 40.60ms | 24.63件/秒 | 1,711MiB | 約4,096MiB |

同じ計時条件では「Layaが必ず速い」という以前の印象は再現しませんでした。モデルサイズだけでなく、入力token数、ONNX最適化、PyTorch精度、checkpointを何個常駐させるかが影響します。GPUは89〜90℃で、絶対速度は参考値です。

入力SHA256は`1be8ce3419a4824f5c2f0c15a22c84ee3694a41bfb1a96847bce9547767a8008`。見えるERABIデータ105,035行との正規化context完全一致は0ですが、意味・翻訳・事前学習の重複を否定できません。公開testラベルとの一致であって独立blind goldではありません。

再現コード：[データ構築](../scripts/build_neutral_benchmark.py)、[評価](../scripts/run_neutral_benchmark.py)、[集計](../scripts/summarize_neutral_benchmark.py)。元データの出所・revision・抽出条件は構築スクリプトとローカルmanifestに保存しています。

## 過去の最適化で分かったこと

以下は旧checkpointでの実験です。今回のモデルにそのまま同じ速度・精度を保証しません。

- Practical V1の90件では、CPU FP32 ONNXがPyTorch比p50 366.73→201.67ms、GPU FP16 ONNXが35.90→19.00ms。最上位は両形式90/90一致でした。
- 動的INT8は元モデルとの一致49/90、静的QDQ W8A8はCPU33/90・GPU29/90で、精度低下しました。静的版は速度も低下。このQDQはSmoothQuantではありません。INT8は配布・自動選択の対象外です。
- World Choice 404件のCPU FP32 ONNXはRyzen 7 5800X・8 threadsでp50 474ms、1.93件/秒、ピークRSS 2.59GiB。CPUでは入力長とthreadsが重要です。プロセス単位で少なくとも約3GiBの空きRAMを目安にしてください。
- World Choiceのbatch比較ではPyTorch CUDAはbatch 16で1.11倍、ONNX FP16は0.76倍、CPU ONNX FP32はbatch 2で0.92倍。ONNXはbatch 1が最速でした。FP16のbatch 4/8では境界的な1件が変わりました。
- 同一PyTorchでCUDA 13.0対13.2を比較した際、速度差は約0.2%以下、VRAMは同一でした。CUDA更新だけによる改善は確認できませんでした。
- 旧モデルの約508→1,012→2,038 token入力で、GPU ONNX FP16 p50は46.1→136.0→579.5ms。長文は遅く、2k学習は16GB GPUで実用性未確認です。配布版の正式入力契約は512のままです。

詳細な旧実験設定は[STATUS](../STATUS.md)、再現コードは`scripts/benchmark_practical_v1_runtimes.py`、`benchmark_world_choice_batch.py`、`benchmark_world_choice_cuda.py`、`probe_2k_context.py`です。

## 配布物の識別

今回のモデルはDecision Mix V2追加学習epoch 3です。Hub名は互換性維持のため以前と同じです。

- Hub：[sugarknight/erabi-practical-v1-experimental](https://huggingface.co/sugarknight/erabi-practical-v1-experimental)
- weights SHA256：`959c7c38ff00c40f39ac5ad0e40344117e8caa14dadc511b2128e6f18ff06934`
- 形式：`model.safetensors`、`onnx/fp32/model.onnx`、`onnx/fp16/model.onnx`
- 校正：未実施。古いモデルの校正を流用しない

weightsの公開コミット：[`67c587ca4c2a15586de306853410cd82dc81dbee`](https://huggingface.co/sugarknight/erabi-practical-v1-experimental/commit/67c587ca4c2a15586de306853410cd82dc81dbee)。`load_engine(revision="67c587ca4c2a15586de306853410cd82dc81dbee", device="cpu")`で固定できます。リポジトリ版の既定値もこのcommitへ更新しています。公開済みPyPI 0.1.4の無指定値は旧版のままです。

PyTorchとCPU FP32 ONNXは210/311（67.52%）、GPU FP16 ONNXは211/311（67.85%）でした。FP32はTop-1 311/311一致、FP16は310/311一致です。異なる1件の元モデル上位2候補の確率差は0.00816で、FP16の丸め差で順位が反転しました。全件の最大確率差は0.00470、最大logit差は0.01979。完全一致ではないことを明記し、FP32完全一致・FP16差1件以下・最大確率差0.01以下・不一致が確率差0.01以下の近接候補だけ、という限定した配布検査を通しました。FP16の1問改善をモデルの汎化改善とは扱いません。

FP32 ONNX SHA256：`3682944e03e8a1614b3d8766b166365408c3e603bd113ab0db5c0e3ba0dab95b`。FP16 ONNX SHA256：`466c2ee5cb9b525d9f5df9b34948bcfdd48770ec05fe533d6e42a528b1722431`。
