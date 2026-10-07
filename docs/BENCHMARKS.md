# ベンチマークと推論性能

正答率はデータ分布に、速度は入力長・候補数・backend・精度・GPU温度・同時負荷に依存します。以下は保証値ではなく、特定条件での実測です。現行モデルと過去の測定、リモートAPIとローカル推論を区別しています。

[全モデルの共通150問比較](DECISION_ENGINE_COMPARISON.md)では、ERABI・Laya・CLEF・CLEF Flash・Jev・GPT-6 Lunaを同じ安全な公開データで評価しています。初期化、平均・最短・最長・p50/p95、RAM・VRAM、API費用を掲載しています。以下の独自311問・公開共通160問とは部分集合・条件が異なるため、表を跨いで順位付けしないでください。

## 現行モデル：RTX 5060 Tiでの測定結果（2026-10-02）

評価対象は現行配布weightsと固定testです。CLEFとの共通比較は独自Decision Mix V2の311件すべてと、公開test 10 suitesから各16件抽出した160件です。ERABIとLayaには公開test全3,584件の結果もあります。Jevは2026-09-30のリモート結果です。独自testの合成ラベル・分布適応の制約は後述の比較条件と同じです。

### CLEFを含む共通テスト

公開160件は固定公開testから`--public-limit-per-domain 16 --sample-seed 42`で抽出し、全モデルで同じcase IDを使いました。抽出はモデル結果を見る前に固定しています。独自311件は省略しません。公開subsetはsuite単位の抽出でラベル別均等ではなく、3,584件の全体正答率とは異なる指標です。160件・各カテゴリ16件の小標本から一般的な性能順位を断定しません。

公開データは共通の`context / question / choices`へ変換したローカルchoice benchmarkです。MASSIVEは元の60意図すべてを候補にせず、正解を含む最大16候補にしています。長すぎる入力は構築時に除外します。各データセットやモデルの公式task scoreと同じ数字ではありません。

| 実行系 | 独自311件 | 公開共通160件 |
|---|---:|---:|
| ERABI GPU PyTorch / ONNX FP32 / FP16 | 210（67.52%） | 99（61.88%） |
| Laya ID＋説明文 | 109（35.05%） | 92（57.50%） |
| Laya文章キー | 119（38.26%） | 105（65.63%） |
| CLEF NF4＋CPU退避 | 276（88.75%） | 131（81.88%） |
| CLEF BF16＋CPU退避 | 276（88.75%） | 132（82.50%） |
| CLEF Flash NF4・GPU常駐 | 258（82.96%） | 132（82.50%） |
| CLEF Flash BF16＋CPU退避 | 268（86.17%） | 133（83.13%） |

共通公開160件のID hashは`39ba111f460f6c2c7224e2b25a69b5355776c519625b64a4579ba2ccf8643ff4`、独自311件は`fcd8766f06140b7feb1e04111a7c2f793ee9ba08d3cafacdcdd4b9f95496da62`です。ERABI/Layaの共通160件の値は全3,895件run内の該当予測・要求時間を抽出して計算し、再推論で選び直していません。

以下は共通テストのカテゴリ別**正答数**です。正答率は正答数÷件数です。公開各カテゴリは16件なので、1問で6.25ポイント変わります。

| データ | 件数 | ERABI GPU FP16 | Laya ID＋説明文 | Laya文章キー | CLEF 27B NF4 | CLEF 27B BF16 | Flash NF4 | Flash BF16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| コマンド危険性 | 82 | 66 | 28 | 27 | 77 | 78 | 73 | 75 |
| 一般ゲート | 48 | 41 | 26 | 27 | 45 | 46 | 44 | 46 |
| NPC内面・目標 | 45 | 19 | 12 | 14 | 31 | 31 | 29 | 29 |
| 架空platformer | 40 | 15 | 12 | 9 | 32 | 31 | 29 | 32 |
| 架空voxel survival | 29 | 17 | 10 | 12 | 26 | 26 | 24 | 25 |
| 反実仮想 | 67 | 52 | 21 | 30 | 65 | 64 | 59 | 61 |
| Emotion | 16 | 6 | 9 | 8 | 7 | 7 | 8 | 8 |
| MASSIVE英語 | 16 | 13 | 11 | 13 | 16 | 16 | 16 | 16 |
| MASSIVE日本語 | 16 | 13 | 7 | 7 | 16 | 16 | 16 | 16 |
| MASSIVE中国語 | 16 | 9 | 7 | 7 | 15 | 15 | 15 | 15 |
| Prompt injections | 16 | 10 | 13 | 11 | 12 | 12 | 11 | 11 |
| SST-5 | 16 | 7 | 5 | 10 | 10 | 10 | 10 | 10 |
| Toxic-chat jailbreak | 16 | 11 | 12 | 12 | 14 | 15 | 15 | 15 |
| Toxic-chat toxicity | 16 | 13 | 9 | 10 | 14 | 14 | 14 | 15 |
| XNLI英語 | 16 | 10 | 15 | 15 | 14 | 14 | 14 | 14 |
| XNLI中国語 | 16 | 7 | 4 | 12 | 13 | 13 | 13 | 13 |

| 実行系 | 独自test p50 / p95 | 共通公開test p50 / p95 |
|---|---:|---:|
| ERABI GPU PyTorch FP32 | 59.46 / 96.27ms | 50.41 / 105.26ms |
| ERABI GPU ONNX FP16 | 30.51 / 80.91ms | 27.42 / 84.48ms |
| ERABI GPU ONNX FP32・TF32 | 32.88 / 62.71ms | 19.98 / 65.62ms |
| Laya ID＋説明文 | 28.10 / 72.73ms | 35.31 / 83.44ms |
| Laya文章キー | 31.44 / 74.23ms | 37.50 / 82.07ms |
| CLEF NF4＋CPU退避 | 2,076.83 / 2,335.16ms | 1,972.62 / 2,322.15ms |
| CLEF BF16＋CPU退避 | 7,207.44 / 7,749.63ms | 6,994.53 / 7,410.67ms |
| CLEF Flash NF4・GPU常駐 | 264.18 / 328.72ms | 222.52 / 305.25ms |
| CLEF Flash BF16＋CPU退避 | 1,234.05 / 1,324.05ms | 1,174.86 / 1,325.49ms |

### CLEFの構成と解釈

[Cloudflare/clef](https://huggingface.co/Cloudflare/clef)の公式27B BF16 weightsとjoint schema headを、commit `2f3de3dd85f379784083b0814d997ab627200f0c`へ固定しました。13 shards等で約55GBです。公式`joint_schema_model.py`を読んでから実行し、SHA256 `0e304cf7c6500e8bb59bef7e2afd2c6373f82596dfb3b57d1aa93c175e2dc3a3`を実行前に検査します。safetensors、`trust_remote_code=False`、ローカルweightsを使います。

- NF4はbitsandbytes 0.50.2のdouble quant、BF16 compute。64 decoder layersのうち52をGPU、12をCPUに明示配置し、CPU layersは非量子化です。visual encoderとlm_headはCPU、text embeddings・norm・RoPE・公式headはGPUです。明示mapなので`max_memory`はこの配置の容量上限として機能しません。全面4bit・全面GPUとは呼びません。
- BF16は量子化なし、Accelerateのauto mapとGPU 12GiB / CPU 52GiBの配置予算を使います。16GB VRAMには27B BF16全体が入らないため、CPUからの転送を伴います。
- CPU配置はweightsの退避先です。Accelerateは対象層のweightsをforward時にGPUへ移して演算するため、純粋なCPU推論との比較ではありません。BF16 smokeでは64 decoder layers中9層がGPU常駐、残り55層がCPU退避でした。NF4は52層GPU常駐で配置も異なるため、速度差を量子化だけの効果として分離できません。実測時の接続はPCIe 4.0 x8でした。
- テキストのみ、1 requestにchoice質問1つ、batch 1、SDPA、KV cacheなし。画像や複数質問を同時に処理するCLEFの機能は評価していません。公式encoderは候補IDをsortしますが、今回の全入力は元から同じ順序で、ID対応も検査します。
- 入力は一度十分大きな上限でencodeし、16,384 tokens超ならエラーにします。全3,895件の事前監査は139〜521 tokens、中央値233、超過0。tokenizerが異なるのでERABIとtoken数自体の大小は直接比較しません。
- `causal_conv1d` / `flash-linear-attention`の高速kernelは未導入で、正しいが遅いPyTorch reference pathの警告が出ました。CPU退避とこの実装条件を含む測定です。大容量GPU・最適化済みserverでのCLEF速度や公式値を再現したものではありません。

両方式のメモリは公開＋独自471件の測定全体、初回downloadは含みません。VRAMは全GPUの0.5秒サンプル差分なので、短いpeakを見逃し、他プロセスも含みます。

| CLEF構成 | 初期化 | peak RSS | 全GPU peak−開始 | torch peak allocated / reserved | 独自処理量 | 471件の測定wall |
|---|---:|---:|---:|---:|---:|---:|
| NF4＋CPU退避 | 56.74秒 | 14,715MiB（14.37GiB） | 13,310MiB（13.00GiB） | 12,775 / 13,098MiB | 0.48件/秒 | 16.14分 |
| BF16＋CPU退避 | 58.46秒 | 44,988MiB（43.93GiB） | 11,467MiB（11.20GiB） | 10,396 / 10,598MiB | 0.14件/秒 | 56.10分 |

測定wallは初期化・warmupを除き、予測journalの書込を含みます。温度はNF4 38〜69℃、BF16 43〜70℃、SM clock中央値は両方2,842MHz。BF16の方がGPU常駐層が少ないため、VRAM値は低く、CPU RSSと転送量が大きくなります。独自311件の正答数は同じですが、全471件のTop-1は12件異なりました。量子化しても常に同じ判断になるとは保証しません。

自動NF4配置は量子化tensorのCPU/meta dispatchで失敗したため、CPU側を非量子化にする明示mapで動作を確認しました。またCPU-offload hookがRoPEの非永続bufferを移動しなかったため、そのbufferをGPUへ配置しています。lm_headの全vocabularyをGPUに載せず、公式headが参照するoption embedding slicesだけを転送します。これらは推論を成立させる配置上の対応で、headや重みの追加学習ではありません。

再現には`accelerate==1.15.0 bitsandbytes==0.50.2 pillow sentencepiece psutil`を測定用venvへ追加し、公式weightsを取得してください（[量子化の対応環境](https://huggingface.co/docs/transformers/quantization/bitsandbytes)、[CPUオフロード](https://huggingface.co/docs/accelerate/usage_guides/big_modeling)）。

```powershell
hf download Cloudflare/clef --revision 2f3de3dd85f379784083b0814d997ab627200f0c --local-dir models/clef-27b --max-workers 4
python -m scripts.benchmark_gpu_refresh --system clef_nf4 --model-dir models/clef-27b --public-limit-per-domain 16 --sample-seed 42 --input path/to/public-cases.jsonl path/to/private-test.jsonl --output runs/clef-nf4.json
python -m scripts.benchmark_gpu_refresh --system clef_offload --model-dir models/clef-27b --public-limit-per-domain 16 --sample-seed 42 --input path/to/public-cases.jsonl path/to/private-test.jsonl --output runs/clef-bf16.json
python -m scripts.summarize_gpu_refresh --match-cases runs/clef-nf4.jsonl --reports runs/fp16.json runs/laya-id.json runs/clef-nf4.json runs/clef-bf16.json --output runs/common-comparison.json
```

### CLEF Flashの構成と測定結果

[Cloudflare/clef-flash](https://huggingface.co/Cloudflare/clef-flash)はQwen3.5-9Bを基にしたモデルです。公式commit `17f0b0ad64efb65d273590632833508766b2aae6`、約19GBの配布ファイルへ固定しています。公式判定ソースのSHA256はCLEF 27Bと同じ`0e304cf7c6500e8bb59bef7e2afd2c6373f82596dfb3b57d1aa93c175e2dc3a3`です。ソースを確認し、safetensors・`trust_remote_code=False`で実行します。

- NF4はdouble quant、BF16 compute、32 decoder layersを含むbackbone全体と公式BF16 headをGPUに常駐させます。Embedding等はBF16のままで、全parametersを4bitに変換した構成ではありません。明示root mapでは`max_memory`は容量上限として機能しません。
- BF16は量子化なし、GPU 12GiB / CPU 52GiBのauto mapです。32 decoder layers中18がGPU常駐、14がCPU退避です。visual encoder・text embeddings・公式headはGPU、lm_headとnormはCPU退避、RoPE bufferはGPUです。CPU退避層のweightsはforward時にGPUへ移して演算します。量子化だけでなくGPU常駐層数も異なるため、両構成の速度差を純粋な精度形式の効果とは呼びません。
- テキスト・choice質問1つ・batch 1・SDPA・KV cacheなし。`causal_conv1d`と`flash-linear-attention`は未導入で、27Bと同じPyTorch reference pathを使います。専用kernelや大容量GPUでの公式速度を再現した測定ではありません。
- 共通471件の入力監査は142〜521 tokens、中央値330、上限超過0、候補IDのsortによる順序変化0です。モデルごとにtokenizerが異なるので、token数そのものから速度差を比較しません。

NF4の独自正答率は258/311（82.96%）、公開共通testは132/160（82.50%）。初期化24.05秒、独自p50 / p95は264.18 / 328.72ms、3.74件/秒です。peak RSSは4,733MiB（4.62GiB）、全GPU peak−開始は8,309MiB（8.11GiB）、torch peak allocated / reservedは8,031 / 8,118MiB。471件の測定wallは121.24秒（2.02分）、温度43〜73℃、SM clock中央値2,775MHzでした。独自ラベル・公開choice変換・少数標本の制約は他モデルと同じです。

BF16の独自正答率は268/311（86.17%）、公開共通testは133/160（83.13%）。初期化20.09秒、独自p50 / p95は1,234.05 / 1,324.05ms、0.81件/秒です。peak RSSは10,343MiB（10.10GiB）、全GPU peak−開始は10,960MiB（10.70GiB）、torch peak allocated / reservedは10,715 / 10,836MiB。測定wallは576.77秒（9.61分）、温度42〜69℃、SM clock中央値2,827MHzです。全471件のTop-1はNF4とBF16で18件異なり、量子化後の完全一致は保証しません。

再現用コマンド（privateデータは含まれないため、権利を持つJSONLを指定）：

```powershell
hf download Cloudflare/clef-flash --revision 17f0b0ad64efb65d273590632833508766b2aae6 --local-dir models/clef-flash --max-workers 4
python -m scripts.benchmark_gpu_refresh --system clef_flash_nf4 --model-dir models/clef-flash --public-limit-per-domain 16 --sample-seed 42 --input path/to/public-cases.jsonl path/to/private-test.jsonl --output runs/clef-flash-nf4.json
python -m scripts.benchmark_gpu_refresh --system clef_flash_offload --model-dir models/clef-flash --public-limit-per-domain 16 --sample-seed 42 --input path/to/public-cases.jsonl path/to/private-test.jsonl --output runs/clef-flash-bf16.json
```

### 追加測定：ERABI・Layaの公開test全3,584件

| 実行系・候補の包装 | 独自311件 | 公開3,584件 |
|---|---:|---:|
| ERABI GPU PyTorch FP32 | 210（67.52%） | 2,203（61.47%） |
| ERABI GPU ONNX FP16 | 210（67.52%） | 2,204（61.50%） |
| ERABI GPU ONNX FP32・既定TF32 | 210（67.52%） | 2,203（61.47%） |
| ERABI CPU ONNX FP32 | 210（67.52%） | 未測定 |
| Laya reviewed・ID＋説明文 | 109（35.05%） | 2,003（55.89%） |
| Laya reviewed・文章キー | 119（38.26%） | 2,201（61.41%） |

ERABIは候補IDを返却用に保持し、モデルには候補文を渡します。Layaの標準APIには`criteria={id: description}`を渡す形式と、`criteria={description: None}`として元のIDへ対応を戻す形式があり、両方を測定しました。本文・問題・候補の意味・正解は同じですが、モデルへの包装が異なります。以前の公開benchmarkは文章キー、独自benchmarkはID＋説明文だったため、包装差をGPU変更による精度差と混同しないよう別行にしています。文章キー形式では候補本文が一意であることを検査します。

LayaのBF16表記は標準CUDA autocastの演算精度です。モデルparametersは標準loaderのFP32のままで、英語・多言語2 checkpointを常駐させています。ERABI PyTorchはFP32、CLEFは量子化／CPU退避という別構成です。各モデルの通常利用構成の比較であり、同一precision・同一parameter数の比較ではありません。

Layaは同系統の追加学習をしていません。独自testでの優劣は分布適応の比較で、一般性能の順位ではありません。公開testもモデルの事前学習との重複を否定できず、独立blind goldではありません。

### データセット別正答率

| データ | 件数 | ERABI GPU FP16 | Laya ID＋説明文 | Laya文章キー |
|---|---:|---:|---:|---:|
| コマンド危険性 | 82 | 80.49% | 34.15% | 32.93% |
| 一般ゲート | 48 | 85.42% | 54.17% | 56.25% |
| NPC内面・目標 | 45 | 42.22% | 26.67% | 31.11% |
| 架空platformer | 40 | 37.50% | 30.00% | 22.50% |
| 架空voxel survival | 29 | 58.62% | 34.48% | 41.38% |
| 反実仮想 | 67 | 77.61% | 31.34% | 44.78% |
| Emotion | 566 | 48.76% | 49.82% | 50.53% |
| MASSIVE英語 | 452 | 85.18% | 65.71% | 69.91% |
| MASSIVE日本語 | 452 | 79.42% | 53.76% | 58.19% |
| MASSIVE中国語 | 452 | 62.39% | 49.56% | 56.64% |
| Prompt injections | 116 | 50.00% | 63.79% | 66.38% |
| SST-5 | 500 | 36.20% | 36.40% | 43.60% |
| Toxic-chat jailbreak | 182 | 84.62% | 81.32% | 78.57% |
| Toxic-chat toxicity | 264 | 65.91% | 60.98% | 59.85% |
| XNLI英語 | 300 | 62.67% | 85.33% | 86.00% |
| XNLI中国語 | 300 | 49.00% | 45.33% | 75.33% |

### 速度・メモリ

batch 1、8 warmups、CUDA同期、入力整形を含む要求単位の時間です。初回ダウンロードと予測journal書込は推論時間から除外しています。初期化はモデル読込・runtime準備で、Python/import自体は含みません。Laya初期化にはキャッシュ済みHub snapshotの確認と2 checkpointのpreloadを含みます。

| 実行系 | 初期化 | 独自test p50 / p95 | 公開test p50 / p95 | peak RSS | 全GPU peak−開始 |
|---|---:|---:|---:|---:|---:|
| ERABI GPU PyTorch FP32 | 19.83秒 | 59.46 / 96.27ms | 51.24 / 104.53ms | 2,640MiB | 2,133MiB |
| ERABI GPU ONNX FP16 | 10.12秒 | 30.51 / 80.91ms | 27.78 / 83.98ms | 1,716MiB | 2,408MiB |
| ERABI GPU ONNX FP32・TF32 | 10.04秒 | 32.88 / 62.71ms | 19.87 / 64.57ms | 2,429MiB | 2,757MiB |
| ERABI CPU ONNX FP32 | 11.26秒 | 826.28 / 1,598.28ms | 未測定 | 2,848MiB | 使用なし |
| Laya ID＋説明文 | 11.08秒 | 28.10 / 72.73ms | 34.81 / 83.21ms | 3,250MiB | 3,207MiB |
| Laya文章キー | 9.68秒 | 31.44 / 74.23ms | 37.66 / 84.55ms | 2,757MiB | 3,202MiB |

GPUモデルのメモリピークは公開＋独自の3,895件を通した値、CPUは311件です。`nvidia-smi`を0.5秒ごとに採り、開始時からの全GPU使用量差を計算しています。他プロセスを含み、短いピークを見逃すのでモデル単体のVRAM割当とは呼びません。PyTorch allocatorのpeak allocated / reservedはERABI PyTorch 1,859 / 1,940MiB、Laya ID形式2,912 / 3,026MiB、Laya文章キー2,911 / 3,028MiBです。ONNXの割当はこのPyTorchカウンターに現れず、0をVRAM不使用とは扱いません。

GPUはRTX 5060 Ti 16GB、driver 617.14。CPUはRyzen 7 5800X 8C/16T、RAM 96GB。torch 2.12.0+cu130、transformers 5.17.0、GLiClass 0.1.20、ORT GPU 1.30.0、Python 3.12.10を使いました。PyTorchは8 threads、ORTは既定threads。CPU再測定もORT 1.30.0です。GPUを使う測定は単独・順番に実行しています。背景でモデルの取得が走っていたため、ディスク・CPU・初期化時間は完全無負荷ではありません。

CPUの値は同じORT GPU wheel 1.30.0の`CPUExecutionProvider`で測定し、GPU演算は使っていません。CPU専用wheelとのbinary比較は未実施です。

採用GPU runの全サンプル温度は37〜73℃、SM clock中央値はPyTorch 2,775MHz、他GPU runは2,827MHzでした。旧A4000の強いクロック低下時の絶対速度は現行値として流用しません。

この環境では公開testでONNX FP32がFP16より速く、独自testではFP16のp50が僅かに速い一方、FP32のp95が小さくなりました。ORTの`use_tf32=1`を別のprovider確認runで確認しています。TF32は低精度の高速FP32演算で、厳密なFP32演算とは異なります（[公式設定](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html#use_tf32)）。PyTorch側はfloat32 matmul precision `highest`でした。形式の名前だけで速度順位を決めず、実入力で確認してください。

PyTorchとGPU FP16は独自311件のTop-1全件一致、公開では4件差。全3,895件の最大確率差は0.01946で、runtime・GPU変更後に旧環境と同じ丸め誤差幅を保証しません。これはweightsの追加学習ではありません。Layaは全行でstate clipping、実際にrenderした候補の48-token超過が0（ID形式最大46、文章キー最大43 tokens）ですが、英語checkpointの校正温度clamp警告があり、確率は未校正参考値です。両包装とも英語route 2,205件・多言語route 1,690件で、今回の包装差による成績変化はroute選択差ではありません。

### 再現

公開testの構築は`build_neutral_benchmark.py`、私有testは正当に保有するJSONLを使ってください。モデルはローカルへ取得し、Layaは[公式リポジトリ](https://github.com/NandhaKishorM/laya)のcommit `9d955671415fc19f069b9cc998928075c1f255ec`を使いました。標準Routerの取得元はbundle repo `convaiinnovations/laya` commit `55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851`で、英語はroot、多言語は`multilingual/` subfolderです。別のstandalone多言語repoのrevisionは今回使っていません。

```powershell
python -m scripts.benchmark_gpu_refresh --system erabi_fp16 --device cuda:0 --model-dir path/to/onnx/fp16 --input path/to/test.jsonl --output runs/fp16.json
python -m scripts.benchmark_gpu_refresh --system erabi_fp32 --device cuda:0 --model-dir path/to/onnx/fp32 --input path/to/test.jsonl --output runs/fp32.json
python -m scripts.benchmark_gpu_refresh --system erabi_pytorch --device cuda:0 --model-dir path/to/checkpoint --input path/to/test.jsonl --output runs/pytorch.json
python -m scripts.benchmark_gpu_refresh --system erabi_fp32 --device cpu --model-dir path/to/onnx/fp32 --input path/to/test.jsonl --output runs/cpu.json
python -m scripts.benchmark_gpu_refresh --system laya --laya-repo path/to/laya --input path/to/test.jsonl --output runs/laya-id.json
python -m scripts.benchmark_gpu_refresh --system laya --laya-repo path/to/laya --laya-text-keys --input path/to/test.jsonl --output runs/laya-text.json
python -m scripts.summarize_gpu_refresh --reports runs/fp16.json runs/laya-id.json --output runs/comparison.json
```

必要な測定用依存は`psutil`です。複数の`--input`を渡せます。出力が既存なら上書きせず停止します。小規模確認は`--limit-per-domain 1`ですが、この結果を全testの成績とは呼ばないでください。集計のcase ID hashで同じ部分集合か確認できます。公開test SHA256は`1be8ce3419a4824f5c2f0c15a22c84ee3694a41bfb1a96847bce9547767a8008`、独自testは`c9e8227429fe5388cae9b45bcc040d029336cfb2c988bd2c32b5faa19f3677ee`です。

## 過去の測定：Decision Mix V2・RTX A4000（2026-09-30）

2026-09-30、train/dev/calibrationとcanonical group単位で分離したfinal 311件・109 groupsです。全システムに同じcontext、question、候補IDと順序を渡しました。ERABIのfinal入力は88〜511 tokens。testのSHA256は`c9e8227429fe5388cae9b45bcc040d029336cfb2c988bd2c32b5faa19f3677ee`です。データ本体は非公開です。

| システム | 正答数 | 正答率 | family macro | group全問正答率 | NLL | Brier |
|---|---:|---:|---:|---:|---:|---:|
| ERABI World Choice（学習前） | 183/311 | 58.84% | 56.31% | 27.52% | 1.3814 | 0.5964 |
| ERABI Decision Mix V2（学習後） | 210/311 | 67.52% | 63.64% | 39.45% | 0.8642 | 0.4318 |
| Laya 0.3.21 reviewed | 107/311 | 34.41% | 34.38% | 9.17% | 1.4433 | 0.7690 |
| Jev 1.13（リモート） | 287/311 | 92.28% | 90.95% | 80.73% | 0.4382 | 0.1463 |

### 過去の配布時検査：RTX A4000（2026-09-30）

以下は旧測定環境（PyTorch 2.6.0+cu124、ONNX Runtime 1.21.0）の配布時検査であり、RTX 5060 Tiの測定結果ではありません。同一weightsでもruntime・演算精度による丸め差があります。現行環境のGPU 3形式は210/311（67.52%）です。

旧環境ではPyTorchとCPU FP32 ONNXは210/311（67.52%）、GPU FP16 ONNXは211/311（67.85%）でした。FP32はTop-1 311/311一致、FP16は310/311一致です。異なる1件の元モデル上位2候補の確率差は0.00816で、FP16の丸め差で順位が反転しました。全件の最大確率差は0.00470、最大logit差は0.01979。FP32完全一致・FP16差1件以下・最大確率差0.01以下・不一致が確率差0.01以下の近接候補だけ、という限定した配布検査の結果です。FP16の1問改善は汎化改善ではなく、旧環境の一致率を別環境へ保証しません。

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

### 過去の速度・RAM・VRAM：RTX A4000（2026-09-30）

以下はRTX A4000での過去の測定です。配布ONNXを使った311件、初回ダウンロードを除外、8回ウォームアップ後、tokenizationを含む単件推論、GPU同期ありという条件です。現行RTX 5060 Tiの数値は冒頭の節を参照してください。

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

配布モデルはDecision Mix V2追加学習epoch 3です。Hub名は互換性維持のため固定しています。

- Hub：[sugarknight/erabi-practical-v1-experimental](https://huggingface.co/sugarknight/erabi-practical-v1-experimental)
- weights SHA256：`959c7c38ff00c40f39ac5ad0e40344117e8caa14dadc511b2128e6f18ff06934`
- 形式：`model.safetensors`、`onnx/fp32/model.onnx`、`onnx/fp16/model.onnx`
- 校正：未実施。古いモデルの校正を流用しない

weightsの公開コミット：[`67c587ca4c2a15586de306853410cd82dc81dbee`](https://huggingface.co/sugarknight/erabi-practical-v1-experimental/commit/67c587ca4c2a15586de306853410cd82dc81dbee)。`load_engine(revision="67c587ca4c2a15586de306853410cd82dc81dbee", device="cpu")`で固定できます。リポジトリ版の既定値もこのcommitへ更新しています。公開済みPyPI 0.1.4の無指定値は旧版のままです。

FP32 ONNX SHA256：`3682944e03e8a1614b3d8766b166365408c3e603bd113ab0db5c0e3ba0dab95b`。FP16 ONNX SHA256：`466c2ee5cb9b525d9f5df9b34948bcfdd48770ec05fe533d6e42a528b1722431`。
