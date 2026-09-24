# ERABI（えらび）

ERABIは、Jevっぽい「状況を読んで候補を選ぶ」動きを、GLiClassを使って再現してみた実験プロジェクトです。Jevの公式版や内部実装の再現版ではありません。

`context`（状況）、`question`（判断基準）、2～16個の`choices`（候補）から、全候補の確率分布を返します。回答は常に確認対象（`review`）であり、最大確率は正解の保証ではありません。

## インストールと最初の推論

Python 3.11以上が必要です。PyTorchのGPU版を使う場合は、先に利用環境に合うPyTorchをインストールしてください。

```bash
python -m pip install erabi
erabi predict --request '{"schema_version":"1","context":"7冊のノートと2個の消しゴムを買った。","question":"全部で何個？","choices":[{"id":"nine","text":"9個"},{"id":"ten","text":"10個"}]}'
```

上のワンラインはPowerShell 7でも動作確認済みです。入力をファイルに保存して `erabi predict --request request.json` としても使えます。初回は選択された形式のモデル（約0.88～1.76GB）を取得し、以降はHugging Faceのローカルキャッシュを再利用します。ネットワークが使えない場合は、事前取得したモデルのローカルディレクトリを`--model-id`で指定してください。

### Pythonから使う：仮想環境から `sample.py` まで

Python 3.11以上で、任意の作業フォルダから実行できます。この後に示すコードを`sample.py`としてそのフォルダへ保存してください（リポジトリを取得済みなら[sample.py](sample.py)をそのまま使えます）。以下はWindows PowerShellでPython 3.12を使う例です。`py -3.12`がない場合は、インストール済みの対応バージョンを指定してください。

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Linux/macOSでは、代わりに`python3.12 -m venv .venv`、`source .venv/bin/activate`で仮想環境を有効化します。以降のコマンドは有効化した仮想環境内で実行します。PowerShellで有効化が制限される場合は、`python`の代わりに`.\.venv\Scripts\python.exe`を直接使えます。

使いたい実行方法に応じて、次の**いずれか1つ**を選びます。どの方法でも`erabi`は同じpipパッケージです。ONNX版でも`erabi`の依存としてPyTorchはインストールされます。

```powershell
# CPU + ONNX FP32（推奨）: CPU専用PyTorchを先に入れ、ONNX Runtime CPU版を追加
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install erabi onnxruntime
python sample.py
```

```powershell
# CPU + PyTorch safetensors（ONNX Runtimeを使わない）
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install erabi
python sample.py --model-format pytorch
```

```powershell
# NVIDIA GPU + ONNX FP16（対応するCUDA/cuDNN環境が必要）
python -m pip install erabi onnxruntime-gpu
python sample.py --device cuda:0
```

GPU用PyTorchを明示的に導入する場合は、[PyTorch公式のインストール案内](https://pytorch.org/get-started/locally/)で環境に合うコマンドを先に実行してください。`onnxruntime`と`onnxruntime-gpu`は**同じ仮想環境に両方入れない**でください（[ONNX Runtime公式案内](https://onnxruntime.ai/docs/get-started/with-python.html)）。GPU版でもCUDA Execution Providerが使えなければ、自動選択はPyTorchに戻ります。`python -c "import onnxruntime as ort; print(ort.get_available_providers())"`で確認できます。

[sample.py](sample.py)はモデルの初期化と1問の推論を試すコードです。追加学習したGLiClassモデルをHugging Faceから取得し、CPU/GPU向けのONNX RuntimeまたはPyTorchで実行します。中身は次のとおりです。

```python
import argparse
from time import perf_counter

from erabi.model_loader import load_engine
from erabi.schema import ChoiceRequest

parser = argparse.ArgumentParser()
parser.add_argument("--device", default="cpu")
parser.add_argument("--model-format", default="auto")
args = parser.parse_args()

print("ERABI: recreating Jev-like choice decisions with GLiClass (experimental, not official Jev).", flush=True)
print("Runtime: ONNX Runtime or PyTorch; model downloaded from Hugging Face.", flush=True)
print(f"[1/2] Loading model (device={args.device}, format={args.model_format})...", flush=True)
started = perf_counter()
engine = load_engine(device=args.device, model_format=args.model_format)
print(f"[1/2] Model ready in {perf_counter() - started:.2f}s (format={engine.model_format})", flush=True)

request = ChoiceRequest.from_dict({
    "context": "ノートを7冊、消しゴムを2個買った。",
    "question": "全部で何個？",
    "choices": [
        {"id": "nine", "text": "9個"},
        {"id": "ten", "text": "10個"},
    ],
})
print("[2/2] Running inference...", flush=True)
started = perf_counter()
result = engine.predict(request)
print(f"[2/2] Inference done in {perf_counter() - started:.2f}s", flush=True)
print("best:", result.best_candidate_id)
print("probabilities:", {choice.id: choice.probability for choice in result.choices})
```

初回は選択されたモデルを自動ダウンロードします。「初期化」にはモデルの取得・読み込みが含まれ、「推論」は1問を処理する時間です。`sample.py`は既定でCPUを使い、ONNX Runtime CPU版があればFP32 ONNX、なければPyTorchを選びます。表示される確率は正解の保証ではありません。

### モデルの保存先

ダウンロード先を指定するには、`--model-cache-dir`を使います。`predict`、`evaluate`、`python -m erabi.serve`で利用でき、トークナイザーと重みの両方に適用されます。保存先に十分な空き容量を確保してください。

```powershell
erabi predict --request examples/request.json --model-cache-dir ".\model-cache"
$env:ERABI_MODEL_CACHE_DIR = ".\model-cache"
erabi predict --request examples/request.json
```

Linux/macOSでは`export ERABI_MODEL_CACHE_DIR=/data/models/erabi-cache`と設定します。優先順位は`--model-cache-dir`、`ERABI_MODEL_CACHE_DIR`、Hugging Face標準の`HF_HUB_CACHE`/`HF_HOME`、既定キャッシュの順です。環境変数を変更しても既存のダウンロードは移動されず、新しい場所に再取得されます。`--model-id`にローカルモデルディレクトリを指定した場合はその場所から読み込み、キャッシュ先の設定はモデル自体の移動には使われません。

ERABI 0.1.3の既定モデルは、Exam-QA追加実験後の3形式を含む検証済みHugging Faceリビジョン`c6c7acf0280b8af5cce6c2a18e9a215f7d2eae57`に固定しています。Windowsでシンボリックリンクを使えない環境ではモデルカード更新だけでも別リビジョンのキャッシュが重複し得るためです。新しいリビジョンを意図的に使う場合は`--revision main`またはコミットIDを指定してください。

### モデル形式の自動選択とおすすめ

形式選択はERABI 0.1.2以降の機能です（0.1.1以前はPyTorch版のみ）。既存環境は`python -m pip install --upgrade erabi`で更新できます。`--model-format`を省略すると`auto`です。`--device`を省略した場合はCUDAが利用可能なら`cuda:0`、そうでなければ`cpu`を選びます。ONNX Runtimeが使える場合、CPUではFP32 ONNX、CUDA Execution Providerが使えるGPUではFP16 ONNXを**必要な形式だけ**Hugging Faceから取得します。ONNX Runtimeがない場合や、CUDA Execution ProviderがないGPUでは従来のPyTorch safetensorsに戻します。別のHugging FaceモデルIDは互換性維持のため`auto`でPyTorchを使い、明示指定すれば同じONNX配置のモデルも利用できます。

| 利用形態 | おすすめ | 理由 |
|---|---|---|
| NVIDIA GPU + 対応するONNX Runtime GPU版 | `auto` → `onnx-fp16` | 下記ベンチマークでp50が35.90→19.00ms、元weightsと最上位90/90一致 |
| CPU + ONNX Runtime CPU版 | `auto` → `onnx-fp32` | 下記ベンチマークでp50が366.73→201.67ms、元weightsと最上位90/90一致 |
| ONNX Runtimeなし・互換性優先 | `pytorch` | `pip install erabi`のみで動作し、元のsafetensorsを使用 |

これらはPractical V1の未レビュー合成90件での比較であり、人手goldでの品質保証ではありません。INT8版は今回の量子化設定で予測が大きく変わったため、自動選択・公開対象から除外しました。

PyTorchのGPU版を使う場合は[公式案内](https://pytorch.org/get-started/locally/)で環境に合う版を先に導入します。ONNX RuntimeはCPUなら`python -m pip install onnxruntime`、NVIDIA GPUなら環境に合う`onnxruntime-gpu`を導入してください。**両パッケージを同じ仮想環境に同時インストールしない**でください（[ONNX Runtime公式案内](https://onnxruntime.ai/docs/get-started/with-python.html)）。GPU版はPyTorch、CUDA、cuDNNと互換な版を[公式CUDA表](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html)で確認してください。

```powershell
erabi doctor
erabi predict --request examples/request.json --device cpu
erabi predict --request examples/request.json --device cuda:0
erabi predict --request examples/request.json --model-format pytorch
erabi predict --request examples/request.json --model-format onnx-fp32 --device cpu
erabi predict --request examples/request.json --model-format onnx-fp16 --device cuda:0
```

`ERABI_MODEL_FORMAT=onnx-fp32`のように環境変数でも指定できます。優先順位は`--model-format`、`ERABI_MODEL_FORMAT`、`auto`です。明示指定したONNX形式がそのデバイス・実行環境に対応しない場合は、別形式へ黙って切り替えずエラーにします。Python APIでは`from erabi.model_loader import load_engine`を使い、`load_engine(model_format="auto", device="cpu")`のように指定します。`predict`、`evaluate`、ローカルHTTP APIの`--model-format`で同じ選択ができます。

無指定の既定値は公開済みの[ERABI Practical V1実験モデル](https://huggingface.co/sugarknight/erabi-practical-v1-experimental)です。正式合格モデルではなく、未レビュー合成データで追加学習した未校正weightsです。別のモデルを使う場合はローカルパスまたはHugging FaceのモデルIDを指定できます。

```bash
erabi predict --request examples/request.json --model-id path/to/checkpoint
# または、利用するモデルIDを既定値として設定
export ERABI_MODEL_ID=owner/model-name
erabi predict --request examples/request.json
```

`erabi doctor` はCPU/CUDAと空き容量を表示します。`erabi evaluate --input examples/smoke_cases.jsonl --output-dir runs/smoke` は評価ファイルを処理します。ローカルHTTP APIはオプション依存を入れて `python -m erabi.serve --model-id path/to/checkpoint` で起動します（localhost限定）。

## 入出力とデータセット形式

推論入力はUTF-8 JSONです。候補の`id`と順序を保ち、全候補のlogitsに対して1回だけSoftmaxを適用します。入力全体が512トークンを超える場合は無言で切り詰めずにエラーにします。

```json
{
  "schema_version": "1",
  "context": "文房具店でノートを7冊、消しゴムを2個買った。",
  "question": "全部で何個買った？",
  "choices": [
    {"id": "a", "text": "9個"},
    {"id": "b", "text": "10個"}
  ]
}
```

出力の`choices`は各候補の`id`と`probability`を入力順で返し、`best_candidate_id`は最大logitの候補を示します。`decision.status`は既定で`review`、未校正の`calibration.status`は`none`です。例は[examples/request.json](examples/request.json)を参照してください。

学習・評価データは1行1問のJSONLです。上の入力に加えて、最低限`id`、`group_id`、`target`を付けます。`group_id`は同じ原題の言い換えや候補順序違いをまとめ、train/dev/calibration/final_test間で重複させません。

```json
{"schema_version":"1","id":"sample-001","group_id":"story-001","context":"ノート7冊と消しゴム2個を買った。","question":"全部で何個？","choices":[{"id":"a","text":"9個"},{"id":"b","text":"10個"}],"target":{"kind":"hard","choice_id":"a"},"language":"ja","family":"everyday_arithmetic","review_status":"unreviewed"}
```

`target.choice_id`は選択肢のIDを参照し、選択肢を並べ替えても正しいIDを保ちます。`language`、`family`、`review_status`などは出所・品質の追跡用メタデータです。合成教師ラベルを人手確認済みgoldと呼ばないことが重要です。[Practical V1のデータ説明](data/practical_v1/README.md)に生成・監査の詳細があります。

## 学習と評価で得られた知見

2026-09-22時点の追加学習実験では、凍結RC3（約438Mパラメータ）からPractical V1のtrain 2,414問のみで1 epoch、151 optimizer steps、peak LR 2.5e-6、microbatch 2・勾配蓄積8、fp16 AMPを実施しました。dev 399問と旧RC3 Bridge 480問で選定し、eval 386問は選定後に一度だけ評価しました。

| セット | 学習前 | 学習後 |
|---|---:|---:|
| Practical V1 dev | 59.90% (239/399) | 77.19% (308/399) |
| Practical V1 eval | 61.66% (238/386) | 76.17% (294/386) |
| 旧RC3 Bridge | 88.75% (426/480) | 88.54% (425/480) |

新データでは日常算数23/68→48/68、ツール選択50/70→62/70、JSONログ判断51/69→65/69と改善しましたが、読解は54/71→50/71に低下しました。候補順序の入替一致率は旧Bridgeで97.29%→97.50%でした。**同一教師モデルが作成・再判定した未レビュー合成データ上の結果**であり、独立した人手goldでの汎化性能、実在入試問題の成績、Jevとの同等性は示しません。現時点では校正・正式リリースも未実施です。

Practical V1は日本語・英語・簡体字中国語の6分野（日常算数、ツール選択、会話の次行動、JSON会話ログ、読解、創作入試風）で構成されます。実在の入試問題や私的会話ログは利用していません。より信頼できる評価には、人手ラベル監査と独立した実問題が必要です。

再現用コードは[scripts/train_practical_v1.py](scripts/train_practical_v1.py)、監査結果は[data/practical_v1/audit.json](data/practical_v1/audit.json)にあります。この学習スクリプトの再実行には別途RC3チェックポイントが`release/rc3/model`に必要です。GPU学習と大容量weightsはpipパッケージに含まれません。

### Exam-QAを使った追加実験（2026-09-23）

非公開のExam-QA 374件を、そのまま学習へ流さず、`deepseek/deepseek-v4.1-flash`でERABI形式へ選別・変換しました。固定seedで形式を分散させた10件を先に3回処理し、最終v3では「判断不能なら早期skip」、1024 tokens超のAPI送信前除外、図・複数正解・不完全な複数空欄・部分点式証明の除外を明示しています。記号選択肢は元の選択肢本文へ対応付け、自由記述だけは公式解答を正解候補としてDeepSeekに同型の誤答候補を作らせ、ローカル検証を通したものだけ採用しました。

全374件中217件を採用、157件を除外しました。分割は原題グループ単位で、train 175件、valid 37件です。validは元資料に正式な選択肢がある問題だけに限定し、DeepSeek生成の誤答候補はtrainにだけ入れています。5件はvalid側グループに属する生成候補だったため両方から除外しました。日本語104件・英語113件、入力長は最大860 tokensです。

Practical V1 checkpointにExam-QA 175件とPractical replay 175件を混ぜ、`max_length=1024`、2 epoch、学習率1.5e-6で追加学習しました。選定されたepoch 1の結果は次の通りです。

| セット | 追加学習前 | 追加学習後 |
|---|---:|---:|
| Exam-QA valid（独立group、公式選択肢のみ） | 21.62% (8/37) | **24.32% (9/37)** |
| Practical V1 dev | 77.19% (308/399) | **78.20% (312/399)** |
| 旧RC3 Bridge | 88.54% (425/480) | **88.54% (425/480)** |
| Practical V1 teacher-agreed eval | 76.17% (294/386) | 75.65% (292/386) |

改善はExam-QA validで**1問だけ**なので、入試問題への一般化を確立したとは見なしません。データはDeepSeek選別済みですが人手gold監査前で、出典ごとの再配布条件も未確認です。このためExam-QA由来のJSONL、API応答、変換ログはGit/Hugging Faceへ公開していません。変換・学習手順だけを[scripts/build_exam_qa_erabi_v1.py](scripts/build_exam_qa_erabi_v1.py)と[scripts/train_exam_qa_erabi_v1.py](scripts/train_exam_qa_erabi_v1.py)で公開します。入力データを正当に用意した環境でのみ再実行できます。

新checkpointからONNX FP32/FP16も再生成し、非公開valid 37件（最大853 tokens）でPyTorchとのTop-1一致37/37を確認しました。公開実験モデルはこのcheckpointへ更新しましたが、pip/APIの既定入力契約は安全側の512 tokensのままです。`max_tokens=1024`は前処理の`max_length`も同時に変更し、切り詰め前の長さを検査する実験用途に限ります。

## Practical V1 推論最適化の実測

2026-09-22、Windows、RTX A4000 16GB、PyTorch 2.6.0+cu124、ONNX Runtime 1.21.0で、同じPractical V1 checkpointを比較しました。CPUはPyTorch safetensors、ONNX FP32、動的INT8、静的QDQ W8A8、GPUはPyTorch safetensors、ONNX FP16、静的QDQ W8A8を試しています。90件は`eval_teacher_agreed.jsonl`から分野・言語別に抽出した未レビュー合成ラベルです。全モデルで温度1.0、全90件の予測確認後に8回ウォームアップし、40回の単件レイテンシを測定しました。

| 実行先・形式 | 重み/ONNX容量 | p50 / p95 | 元weightsとの最上位一致 | 合成教師ラベル一致 |
|---|---:|---:|---:|---:|
| CPU PyTorch safetensors | 1.75 GB | 366.73 / 521.44 ms | 基準 | 69/90 |
| CPU ONNX FP32 | 1.76 GB | **201.67 / 378.73 ms** | **90/90** | 69/90 |
| CPU ONNX 動的INT8 | 1.04 GB | 120.42 / 236.11 ms | 49/90 | 42/90 |
| CPU ONNX 静的QDQ W8A8 | 0.84 GB | 908.17 / 1,142.89 ms | 33/90 | 36/90 |
| GPU PyTorch safetensors | 1.75 GB | 35.90 / 44.12 ms | 基準 | 69/90 |
| GPU ONNX FP16 | 0.88 GB | **19.00 / 22.80 ms** | **90/90** | 69/90 |
| GPU ONNX 静的QDQ W8A8 | 0.84 GB | 84.75 / 89.44 ms | 29/90 | 27/90 |

この測定ではCPUはONNX FP32、GPUはONNX FP16が速度と出力一致の両面で有望でした。FP32の最大確率差は元weights比で最大0.00000493、FP16は最大0.00374でした。動的/静的INT8は軽量化できても予測が大きく変化し、静的版はCPU/GPUとも遅くなりました。静的W8A8はONNX RuntimeのMinMax校正によるQDQであり、SmoothQuantではありません。INT8版は配布・自動選択の対象外です。FP32/FP16版も、独立goldでの確認や校正は未実施です。

再現にはリポジトリをチェックアウトし、開発用仮想環境へ`pip install -e ".[dev]"`、環境に合う`onnxruntime`または`onnxruntime-gpu`と`onnx`を導入します。以下は公開モデルをHugging Face CLIで別ディレクトリへ取得する例です（約1.75GB、十分な空き容量が必要）。実験結果は`runs/`配下（Git管理外）へ書き、モデルと評価結果の既存ファイルは上書きしないでください。

```powershell
$out = "runs/practical_v1_optimization"
$checkpoint = "$out/checkpoint"
hf download sugarknight/erabi-practical-v1-experimental model.safetensors config.json tokenizer.json tokenizer_config.json --local-dir $checkpoint
python -c "from pathlib import Path; from scripts.export_rc3_onnx import export_fp32_model, export_fp16_model; p=Path('$checkpoint'); o=Path('$out'); export_fp32_model(p,o/'fp32'); export_fp16_model(p,o/'fp16')"
python scripts/benchmark_practical_v1_runtimes.py quantize --mode dynamic --fp32-dir "$out/fp32" --output-dir "$out/int8_dynamic_cpu"
python scripts/benchmark_practical_v1_runtimes.py quantize --mode static --fp32-dir "$out/fp32" --output-dir "$out/int8_static_w8a8" --train-file data/practical_v1/train.jsonl --calibration-count 128
python scripts/benchmark_practical_v1_runtimes.py benchmark --backend pytorch --device cuda --model-dir $checkpoint --output "$out/results/pytorch_cuda.json"
python scripts/benchmark_practical_v1_runtimes.py benchmark --backend onnx --device cuda --model-dir "$out/fp16" --output "$out/results/onnx_fp16_cuda.json"
python scripts/benchmark_practical_v1_runtimes.py compare --baseline "$out/results/pytorch_cuda.json" --candidate "$out/results/onnx_fp16_cuda.json"
```

CPU比較は同じ`benchmark`コマンドで`--device cpu`を指定し、`--backend pytorch --model-dir $checkpoint`、または`--backend onnx --model-dir "$out/fp32"` / `"$out/int8_dynamic_cpu"` / `"$out/int8_static_w8a8"`をそれぞれ実行します。GPU静的INT8も`--backend onnx --device cuda --model-dir "$out/int8_static_w8a8"`で測れます。既定の90件・8回ウォームアップ・40回計測を変更する場合は`--cases`、`--warmup`、`--iterations`を指定します。静的量子化の128件は**trainのみ**から取り、評価90件を校正には使いません。モデル読込・エクスポート・量子化の時間は単件レイテンシに含みません。測定値はハードウェア、実行環境、入力長によって変わります。

## 2k入力の探索実験（2026-09-22）

現行の配布版は引き続き512トークン上限です。約2kを試すにはERABIの上限だけでなく、GLiClass前処理の既定1024トークン切り詰めも実験時に変更する必要があります。[診断スクリプト](scripts/probe_2k_context.py)は整形後の入力長を切り詰め前後で照合します。以下はRTX A4000 16GB、Practical V1実験weights、4候補、batch 1での予備測定です。

| 実入力長 | PyTorch GPU p50（10回の初回測定） | ONNX FP16 GPU p50（10回の初回測定） | PyTorch推論peak割当 |
| ---: | ---: | ---: | ---: |
| 508 | 84.6ms | 46.1ms | 1,836MiB |
| 1,012 | 217.5ms | 136.0ms | 2,152MiB |
| 2,038 | 701.5ms | 579.5ms | 3,326MiB |

レイテンシは入力長とともに大きく増え、長時間・高負荷時にはさらに変動します。学習の単一optimizer step（batch 1、fp16 AMP）は508トークンで約0.80秒・peak割当8,387MiB、2,038トークンで約9.63秒・19,020MiBでした。2k学習は16GB GPUで実用的とはいえず、収束や長文精度も未検証です。[学習診断コード](scripts/probe_2k_train_step.py)。

NPCツール選択のCodex起草130件は**2k動作診断専用で、学習・正式評価データには使用しない**。データ本体と説明はローカルに留め、Gitでは公開していない。未学習モデルでの暫定診断はdev 19/26、eval 18/26、512超の長文では各1/2で、PyTorchとONNX FP16の最上位選択は52/52件一致した。テンプレートを分割間で共有し、ラベルも未レビューなので、これを実運用精度やJevとの比較には用いない。[評価スクリプト](scripts/eval_npc_tool_routing_v1.py)。

学習・評価の候補として、DeepSeek V4.1 FlashでゲームNPCのマルチターン会話198件も生成しました。データ本体は非公開です。train 140／dev 28／eval 30で、20件が512超、最長1301トークン。Web、画像・動画生成、コマンド、スクリーンショット、画像解析、ゲーム状態・クエスト・経路探索、ツールなしの会話を可変候補から選びます。旧モデルweightsの2048上限診断ではdev 26/28、eval 27/30、PyTorch↔ONNX FP16の選択は58/58一致しました。教師ラベルは人手確認前で、このデータによる追加学習も未実施です。同じ行動対照パターンが分割間で再登場するため、独立gold精度やJev同等性は示しません。

### 1k上限の追加診断

約1k（実際は1012トークン）なら、上表の初回10回測定でGPU単件推論p50はPyTorch 217.5ms、ONNX FP16 136.0ms。512相当（508トークン）の84.6ms／46.1msより遅いが、2kより大幅に軽い。単一optimizer stepのmicrobatch 2・fp16 AMP・AdamWでは508→1012トークンで約0.76→1.09秒、PyTorch peak割当8,386→12,191MiB、peak予約8,652→14,580MiBで、両方ともstepを実行できた。ただし1 stepだけなので連続学習の安定性や精度向上は未検証。DeepSeek NPC 198件のうち190件は1024以内、8件は超過。dev/evalの適合55件だけを切り詰めずにONNX FP16で評価するとdev 26/27、eval 26/28で、超過3件は除外した（2k評価と母数が異なる）。[評価コード](scripts/eval_npc_tool_routing_v1.py)は除外IDを出力に残す。

現行GLiClass前処理の既定値は1024で、先に切り詰めてからERABIが長さを確認する。したがって**単にERABIの上限を1024へ変えると超過入力を黙って切り詰める可能性があり、正式な1k対応には事前トークン数検証と前処理の修正が必要**。配布版は512のまま。

## 開発とライセンス

```bash
python -m pip install -e ".[dev]"
python -m pytest tests -q
```

コードは[MIT License](LICENSE)です。ベースモデルと学習済みweightsには別のライセンスが適用されます。[THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md)を参照してください。
