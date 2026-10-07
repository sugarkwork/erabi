# ローカル・API判断エンジンの共通比較

同じ安全な公開150問による、選択式判断の測定です。対象はERABI、Laya、Cloudflare CLEF/CLEF Flash、Jev、OpenAI GPT-6 LunaのDecisions/Responsesです。測定日：2026-10-07。

## 正答率・応答時間

単位はms。全行150問、最短・最長は測定した単発要求の範囲です。p95は線形補間で統一しています。

| モデル・構成 | 正答数・一致率 | 平均/件 | 最短 | 最長 | p50 | p95 |
|---|---:|---:|---:|---:|---:|---:|
| ERABI GPU ONNX FP16 | 105/150・70.00% | 28.80 | 20.51 | 102.64 | 26.62 | 37.12 |
| ERABI GPU ONNX FP32 | 105/150・70.00% | 30.73 | 16.28 | 72.07 | 21.32 | 61.84 |
| ERABI GPU PyTorch FP32 | 105/150・70.00% | 46.66 | 38.16 | 85.55 | 40.66 | 80.92 |
| ERABI CPU ONNX FP32 | 105/150・70.00% | 177.62 | 134.51 | 292.64 | 171.43 | 238.93 |
| Laya ID＋説明文 | 94/150・62.67% | 32.73 | 24.49 | 67.38 | 30.74 | 46.31 |
| Laya 文章キー | 107/150・71.33% | 36.85 | 25.41 | 92.98 | 32.48 | 67.15 |
| CLEF Flash NF4 | 131/150・87.33% | 251.60 | 191.06 | 295.23 | 272.37 | 287.35 |
| CLEF Flash BF16・CPU退避 | 133/150・88.67% | 1229.41 | 1076.16 | 1429.19 | 1220.81 | 1345.05 |
| CLEF 27B NF4・CPU退避 | 136/150・90.67% | 2095.20 | 1754.29 | 2396.86 | 2107.73 | 2335.34 |
| CLEF 27B BF16・CPU退避 | 135/150・90.00% | 7264.33 | 6524.45 | 8506.48 | 7239.98 | 7838.36 |
| Jev API | 136/150・90.67% | 357.71 | 285.81 | 1266.42 | 332.84 | 450.68 |
| GPT-6 Luna Decisions | 121/150・80.67% | 303.13 | 202.45 | 1349.18 | 267.39 | 543.38 |
| GPT-6 Luna Responses none | 124/150・82.67% | 1352.52 | 761.69 | 12530.08 | 1142.71 | 2065.86 |
| GPT-6 Luna Responses low | 124/150・82.67% | 1537.74 | 765.10 | 7465.62 | 1356.34 | 2791.07 |

この150問では、JevとCLEF NF4が136問で最多、平均速度はERABI GPU ONNX FP16が最短です。小標本・1回ずつの測定なので、数問の差から一般的な優劣やNF4がBF16より高精度だとは断定しません。Layaの文章キーはID＋説明文より13問多く正解し、入力形式に依存する差が出ています。

## 初期化・メモリ・費用

初期化は秒、メモリはGiB。VRAMは全GPUの開始値との差分と絶対peakの両方を示します。CPU版のVRAMは推論で未使用、APIサーバーの初期化・メモリは観測不能です。

| モデル・構成 | 初期化 | RAM peak RSS | VRAM増分 / 全GPU peak | 150要求のAPI費用 USD | 1要求のAPI費用 USD |
|---|---:|---:|---:|---:|---:|
| ERABI GPU ONNX FP16 | 31.32 | 1.60 | 1.66 / 3.17 | 課金なし | 課金なし |
| ERABI GPU ONNX FP32 | 10.25 | 2.35 | 2.49 / 4.04 | 課金なし | 課金なし |
| ERABI GPU PyTorch FP32 | 6.87 | 2.01 | 2.13 / 3.75 | 課金なし | 課金なし |
| ERABI CPU ONNX FP32 | 9.33 | 2.69 | 未使用 | 課金なし | 課金なし |
| Laya ID＋説明文 | 8.42 | 2.90 | 2.90 / 4.80 | 課金なし | 課金なし |
| Laya 文章キー | 8.05 | 2.94 | 3.40 / 5.03 | 課金なし | 課金なし |
| CLEF Flash NF4 | 33.24 | 4.61 | 8.37 / 10.11 | 課金なし | 課金なし |
| CLEF Flash BF16・CPU退避 | 18.79 | 10.07 | 10.92 / 12.82 | 課金なし | 課金なし |
| CLEF 27B NF4・CPU退避 | 79.70 | 14.36 | 13.07 / 15.05 | 課金なし | 課金なし |
| CLEF 27B BF16・CPU退避 | 56.28 | 43.91 | 11.07 / 12.76 | 課金なし | 課金なし |
| Jev API | 不明 | 不明 | 不明 | 0.003156090 | 0.000021041 |
| GPT-6 Luna Decisions | 不明 | 不明 | 不明 | 0.003430200 | 0.000022868 |
| GPT-6 Luna Responses none | 不明 | 不明 | 不明 | 0.005361600 | 0.000035744 |
| GPT-6 Luna Responses low | 不明 | 不明 | 不明 | 0.008375100 | 0.000055834 |

CLEFの量子化なしBF16は16GB GPUへ全面常駐できず、CPU退避が速度・RAM使用量へ大きく影響します。NF4との比較には量子化と配置の両方が含まれます。初期化は1回の観測で、filesystem cacheやdisk状態の影響を含みます。ローカルの電気代・機材費は未測定です。

## カテゴリ別の正答数

| モデル・構成 | MASSIVE ja /32 | MASSIVE en /32 | MASSIVE zh /32 | XNLI en /28 | XNLI zh /26 |
|---|---:|---:|---:|---:|---:|
| ERABI GPU ONNX FP16 | 26 | 27 | 21 | 18 | 13 |
| ERABI GPU ONNX FP32 | 26 | 27 | 21 | 18 | 13 |
| ERABI GPU PyTorch FP32 | 26 | 27 | 21 | 18 | 13 |
| ERABI CPU ONNX FP32 | 26 | 27 | 21 | 18 | 13 |
| Laya ID＋説明文 | 20 | 23 | 15 | 25 | 11 |
| Laya 文章キー | 20 | 24 | 19 | 24 | 20 |
| CLEF Flash NF4 | 29 | 31 | 28 | 23 | 20 |
| CLEF Flash BF16・CPU退避 | 29 | 31 | 28 | 25 | 20 |
| CLEF 27B NF4・CPU退避 | 30 | 31 | 26 | 25 | 24 |
| CLEF 27B BF16・CPU退避 | 30 | 31 | 26 | 25 | 23 |
| Jev API | 30 | 30 | 29 | 24 | 23 |
| GPT-6 Luna Decisions | 28 | 29 | 25 | 23 | 16 |
| GPT-6 Luna Responses none | 28 | 30 | 25 | 24 | 17 |
| GPT-6 Luna Responses low | 29 | 30 | 26 | 23 | 16 |

全構成のcase IDと入力hashを照合済み。拒否・非有限確率・ID不足・重複・切り詰めを成功例へ混ぜず、150件すべて有効な回答として完了しています。

## 比較条件

- MASSIVE日本語32・英語32・中国語32、XNLI英語28・中国語26。公開testからseed固定で抽出し、安全性確認で10問を除外した150問を、モデルの出力を見る前に固定しています。全モデルでcontext・question・候補文と候補IDを共有し、正解はAPIに送りません。
- 正答率は公開元ラベルとの一致率です。人手で独立検証したgoldや事前学習非重複を保証しません。MASSIVEは元の60意図を最大16候補に変換した形式で、公式ベンチマークscoreではありません。短文150問の結果から、長文・NPC・危険コマンドなどの一般的な性能順位は断定できません。
- 候補はMASSIVEが16個×96問、XNLIが3個×54問。一様ランダム選択の期待正答率は16.00%。ERABI tokenizerでは全入力61〜133 tokens、中央値82。切り詰めなし。異なるtokenizerのtoken数は直接比較しません。独自311問や別の公開160問の結果は、この表には混ぜません。
- ローカルは1プロセスずつ、batch 1・8 warmups・1件ごとにGPU同期。推論時間はtokenizer・候補処理込み、初期化・warmup・journal書込を除きます。初期化は保存済みweightsの読込とbackend準備で、Python起動・事前library import・初回downloadを含みません。OSのfile cacheは消去しておらず、cold start保証値ではありません。
- APIは永続HTTP Sessionによる直列要求。通信・サーバー処理・応答受信・最初のPOSTを含みます。Jevは最初の3問と残り147問で、2 Sessionを使用。各Sessionの公式料金catalog GETは測定外で、POST前に接続を温める可能性があります。OpenAIは同日の150問×3方式の測定結果です。初期化や内部VRAMはAPIから観測できず、不明です。ネットワーク条件と測定時刻の差は残ります。
- GPUはRTX 5060 Ti 16GB、driver 617.14。CPU Ryzen 7 5800X、RAM 96GB。実行環境：Python 3.12、torch 2.12.0+cu130、transformers 5.17.0、ORT GPU 1.30.0、bitsandbytes 0.50.2。PyTorchは8 threads、ORTは既定threads。
- VRAM増分は`nvidia-smi`全GPU peak−測定開始値、0.5秒間隔。モデル専有量ではなく、他プロセスや短いpeakの取りこぼしを含む目安です。RAMは測定プロセスのpeak RSS。CPU版はGPU推論なし。APIサーバーのRAM/VRAMをクライアント使用量で代用しません。

## モデルと実行形式

- ERABI：現行配布のweights。同じweights由来のONNX FP16/FP32とPyTorch FP32。ONNX GPU FP32はCUDA providerのTF32設定を含み、厳密なFP32との同一速度・同一演算を主張しません。
- Laya：reviewed Router bundle `convaiinnovations/laya`、commit `55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851`。English＋multilingualをpreloadし、自動task検出なし。ID＋説明文と文章キーの2形式は、元の候補IDへ戻して評価します。
- CLEF 27B：commit `2f3de3dd85f379784083b0814d997ab627200f0c`。NF4は64 decoder layers中52をGPU、12を非量子化CPUへ退避。BF16はGPU 12GiB/CPU 52GiB予算のauto配置。CPU退避weightsはforward時にGPUへ転送して計算します。純粋なCPU推論ではありません。
- CLEF Flash：commit `17f0b0ad64efb65d273590632833508766b2aae6`。NF4は全面GPU、BF16は同じauto配置予算でCPU退避を伴います。
- CLEF系は公式head、SDPA、BF16 compute、NF4 double quant。公式encoderが内部で候補IDをsortし、確率は元のIDへ対応付けています。`causal_conv1d`/`flash-linear-attention`専用kernelは未導入でreference pathを使用。NF4/BF16の速度差には配置差も含みます。16GB機のこの構成は、最適化済み大容量GPUサーバーの公式速度を示すものではありません。公式ソースhashとローカルdownload metadataの固定commitを照合しています。
- Jev：OrcaRouter経由`typesafe/jev-1.13`、全応答のserved modelは`typesafe/jev-1.13-20260917`。OpenAI：全応答は`gpt-6-luna`、固定snapshot名なし。Responsesはstrict JSON Schemaで候補IDのみを返し、全候補確率を生成・仮造しません。Decisions・Jev・ローカル構成は全候補の有限確率・ID・確率和を検査し、再正規化せず使用します。

## 費用の意味

API費用はusageと確認済み単価による推計で、請求明細との照合ではありません。150要求分を比較し、ローカルの「API課金なし」は電気代・GPU購入費・保守費が無料という意味ではありません。

[Jev公式モデルページ](https://www.orcarouter.ai/models/typesafe/jev-1.13)と公式model catalogでは入力0.042 USD/M、出力0。150問の入力75,145・出力18,132 tokens、推計0.003156090 USD。出力tokenの課金単価は0です。

[Decisions公式ガイド](https://developers.openai.com/api/docs/guides/decisions)は入力0.10 USD/M、cache read/write/output追加課金なし。[GPT-6 Luna公式料金](https://developers.openai.com/api/docs/models/gpt-6-luna)のResponses Standardは入力0.10/cached 0.01/write 0.125/出力0.50 USD/M。この評価は長文・地域追加料金条件には該当しません。表は各方式150問の評価要求だけの費用で、動作確認要求は含めません。

## 集計・図の再現

公開しているのは[14構成の集計値](assets/decision-engine-benchmark.json)で、教材本文・要求ごとの予測・API原応答は含みません。READMEの図はこのJSONを使い、ネットワークやモデルなしで描画できます。

```powershell
# Pillowを使えるPython環境で実行
python scripts/render_decision_benchmark_charts.py
```

出力は`docs/assets/decision-engine-performance.png`と`docs/assets/decision-engine-resources.png`です。各モデルの版・入力形式・配置は上記の測定条件を参照してください。新たに異なる問題を抽出した測定は、同じ150問の再現結果とは扱いません。

入力SHA256：`51aab73bc044a02ad08d427dce1ef6f5cabf431c339861075ff3d4a8cf177b05`。case ID SHA256：`c34e1fcda5ec0915971e9d69b588fa50c6bbaaac00b17bd1ed8a8c2ad4fe47d9`。
