# ERABI（えらび）

ERABIは、`context`（状況）、`question`（判断基準）、2～16個の`choices`（候補）から、全候補の確率分布を返すローカル判断エンジンです。Jevの公式版や再現版ではありません。回答は常に確認対象（`review`）であり、最大確率は正解の保証ではありません。

## インストールと最初の推論

Python 3.11以上が必要です。PyTorchのGPU版を使う場合は、先に利用環境に合うPyTorchをインストールしてください。

```bash
python -m pip install erabi
erabi predict --request '{"schema_version":"1","context":"7冊のノートと2個の消しゴムを買った。","question":"全部で何個？","choices":[{"id":"nine","text":"9個"},{"id":"ten","text":"10個"}]}'
```

上のワンラインはPowerShell 7でも動作確認済みです。入力をファイルに保存して `erabi predict --request request.json` としても使えます。初回は選択された形式のモデル（約0.88～1.76GB）を取得し、以降はHugging Faceのローカルキャッシュを再利用します。ネットワークが使えない場合は、事前取得したモデルのローカルディレクトリを`--model-id`で指定してください。

### モデルの保存先

ダウンロード先を指定するには、`--model-cache-dir`を使います。`predict`、`evaluate`、`python -m erabi.serve`で利用でき、トークナイザーと重みの両方に適用されます。保存先に十分な空き容量を確保してください。

```powershell
erabi predict --request examples/request.json --model-cache-dir "F:\models\erabi-cache"
$env:ERABI_MODEL_CACHE_DIR = "F:\models\erabi-cache"
erabi predict --request examples/request.json
```

Linux/macOSでは`export ERABI_MODEL_CACHE_DIR=/data/models/erabi-cache`と設定します。優先順位は`--model-cache-dir`、`ERABI_MODEL_CACHE_DIR`、Hugging Face標準の`HF_HUB_CACHE`/`HF_HOME`、既定キャッシュの順です。環境変数を変更しても既存のダウンロードは移動されず、新しい場所に再取得されます。`--model-id`にローカルモデルディレクトリを指定した場合はその場所から読み込み、キャッシュ先の設定はモデル自体の移動には使われません。

既定モデルは、ONNX両形式を含む検証済みHugging Faceリビジョン`042998970aa20cc3371e0f7f0e320013a152c068`に固定しています。Windowsでシンボリックリンクを使えない環境ではモデルカード更新だけでも別リビジョンのキャッシュが重複し得るためです。新しいリビジョンを意図的に使う場合は`--revision main`またはコミットIDを指定してください。

### モデル形式の自動選択とおすすめ

形式選択はERABI 0.1.2以降の機能です（0.1.1以前はPyTorch版のみ）。`--model-format`を省略すると`auto`です。`--device`を省略した場合はCUDAが利用可能なら`cuda:0`、そうでなければ`cpu`を選びます。ONNX Runtimeが使える場合、CPUではFP32 ONNX、CUDA Execution Providerが使えるGPUではFP16 ONNXを**必要な形式だけ**Hugging Faceから取得します。ONNX Runtimeがない場合や、CUDA Execution ProviderがないGPUでは従来のPyTorch safetensorsに戻します。別のHugging FaceモデルIDは互換性維持のため`auto`でPyTorchを使い、明示指定すれば同じONNX配置のモデルも利用できます。

| 利用形態 | おすすめ | 理由 |
|---|---|---|
| NVIDIA GPU + 対応するONNX Runtime GPU版 | `auto` → `onnx-fp16` | このホストでp50が35.90→19.00ms、元weightsと最上位90/90一致 |
| CPU + ONNX Runtime CPU版 | `auto` → `onnx-fp32` | このホストでp50が366.73→201.67ms、元weightsと最上位90/90一致 |
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

2026-09-22時点の追加学習実験では、凍結RC3（約438Mパラメータ）からPractical V1のtrain 2,414問のみで1 epoch、151 optimizer steps、peak LR 2.5e-6、microbatch 2・勾配蓄積8、fp16 AMPを実施しました。dev 399問と旧RC3 Bridge 480問で選定し、eval 386問は選定後に一度だけ評価しました。release weightsは上書きしていません。

| セット | 学習前 | 学習後 |
|---|---:|---:|
| Practical V1 dev | 59.90% (239/399) | 77.19% (308/399) |
| Practical V1 eval | 61.66% (238/386) | 76.17% (294/386) |
| 旧RC3 Bridge | 88.75% (426/480) | 88.54% (425/480) |

新データでは日常算数23/68→48/68、ツール選択50/70→62/70、JSONログ判断51/69→65/69と改善しましたが、読解は54/71→50/71に低下しました。候補順序の入替一致率は旧Bridgeで97.29%→97.50%でした。**同一教師モデルが作成・再判定した未レビュー合成データ上の結果**であり、独立した人手goldでの汎化性能、実在入試問題の成績、Jevとの同等性は示しません。現時点では校正・正式リリースも未実施です。

Practical V1は日本語・英語・簡体字中国語の6分野（日常算数、ツール選択、会話の次行動、JSON会話ログ、読解、創作入試風）で構成されます。実在の入試問題や私的会話ログは利用していません。生成・再判定に使ったDeepSeek経由の料金推計は$1.0612で、追加予算枠は使いませんでした。より信頼できる次の評価には、人手ラベル監査と独立した実問題の調達が必要です。

再現用コードは[scripts/train_practical_v1.py](scripts/train_practical_v1.py)、監査結果は[data/practical_v1/audit.json](data/practical_v1/audit.json)にあります。この学習スクリプトの再実行には別途RC3チェックポイントが`release/rc3/model`に必要です。GPU学習と大容量weightsはpipパッケージに含まれません。

## Practical V1 推論最適化の実測

2026-09-22、Windows、RTX A4000 16GB、PyTorch 2.6.0+cu124、ONNX Runtime 1.21.0で、同じPractical V1 checkpointを比較しました。CPUはPyTorch safetensors、ONNX FP32、動的INT8、静的QDQ W8A8、GPUはPyTorch safetensors、ONNX FP16、静的QDQ W8A8を試しています。90件は`eval_teacher_agreed.jsonl`から分野・言語別に抽出した未レビュー合成ラベルです。全モデルで温度1.0、全90件の予測確認後に8回ウォームアップし、40回の単件レイテンシを測定しました。CPU再測定とGPU測定時、Robloxは終了し、GPUの他負荷はほぼありませんでした。

| 実行先・形式 | 重み/ONNX容量 | p50 / p95 | 元weightsとの最上位一致 | 合成教師ラベル一致 |
|---|---:|---:|---:|---:|
| CPU PyTorch safetensors | 1.75 GB | 366.73 / 521.44 ms | 基準 | 69/90 |
| CPU ONNX FP32 | 1.76 GB | **201.67 / 378.73 ms** | **90/90** | 69/90 |
| CPU ONNX 動的INT8 | 1.04 GB | 120.42 / 236.11 ms | 49/90 | 42/90 |
| CPU ONNX 静的QDQ W8A8 | 0.84 GB | 908.17 / 1,142.89 ms | 33/90 | 36/90 |
| GPU PyTorch safetensors | 1.75 GB | 35.90 / 44.12 ms | 基準 | 69/90 |
| GPU ONNX FP16 | 0.88 GB | **19.00 / 22.80 ms** | **90/90** | 69/90 |
| GPU ONNX 静的QDQ W8A8 | 0.84 GB | 84.75 / 89.44 ms | 29/90 | 27/90 |

このホストではCPUはONNX FP32、GPUはONNX FP16が速度と出力一致の両面で有望でした。FP32の最大確率差は元weights比で最大0.00000493、FP16は最大0.00374でした。今回の動的/静的INT8設定は軽くなっても予測が大きく変化し、静的版はCPU/GPUとも遅くなりました。**今回の静的W8A8はONNX RuntimeのMinMax校正によるQDQであり、SmoothQuantではありません。** RTX A4000上でのSmoothQuant高速化を証明する結果ではなく、今回のINT8版を配布・既定化しません。CUDA Execution Providerが有効でも全ノードのGPU実行は保証されないため、静的INT8の遅さの原因をCPUフォールバックと断定しません。FP32/FP16版は実験モデルとして配布しますが、独立goldでの確認や校正は未実施です。

再現にはリポジトリをチェックアウトし、開発用仮想環境へ`pip install -e ".[dev]"`、環境に合う`onnxruntime`または`onnxruntime-gpu`と`onnx`を導入します。以下は公開モデルをHugging Face CLIで別ディレクトリへ取得する例です（約1.75GB、十分な空き容量が必要）。実験結果は`runs/`配下（Git管理外）へ書き、モデルと評価結果の既存ファイルは上書きしないでください。

```powershell
$out = "runs/practical_v1_optimization_20260922"
$checkpoint = "$out/checkpoint"
hf download sugarknight/erabi-practical-v1-experimental model.safetensors config.json tokenizer.json tokenizer_config.json --local-dir $checkpoint
python -c "from pathlib import Path; from scripts.export_rc3_onnx import export_fp32_model, export_fp16_model; p=Path('$checkpoint'); o=Path('$out'); export_fp32_model(p,o/'fp32'); export_fp16_model(p,o/'fp16')"
python scripts/benchmark_practical_v1_runtimes.py quantize --mode dynamic --fp32-dir "$out/fp32" --output-dir "$out/int8_dynamic_cpu"
python scripts/benchmark_practical_v1_runtimes.py quantize --mode static --fp32-dir "$out/fp32" --output-dir "$out/int8_static_w8a8" --train-file data/practical_v1/train.jsonl --calibration-count 128
python scripts/benchmark_practical_v1_runtimes.py benchmark --backend pytorch --device cuda --model-dir $checkpoint --output "$out/results/pytorch_cuda.json"
python scripts/benchmark_practical_v1_runtimes.py benchmark --backend onnx --device cuda --model-dir "$out/fp16" --output "$out/results/onnx_fp16_cuda.json"
python scripts/benchmark_practical_v1_runtimes.py compare --baseline "$out/results/pytorch_cuda.json" --candidate "$out/results/onnx_fp16_cuda.json"
```

CPU比較は同じ`benchmark`コマンドで`--device cpu`を指定し、`--backend pytorch --model-dir $checkpoint`、または`--backend onnx --model-dir "$out/fp32"` / `"$out/int8_dynamic_cpu"` / `"$out/int8_static_w8a8"`をそれぞれ実行します。GPU静的INT8も`--backend onnx --device cuda --model-dir "$out/int8_static_w8a8"`で測れます。既定の90件・8回ウォームアップ・40回計測を変更する場合は`--cases`、`--warmup`、`--iterations`を指定します。静的量子化の128件は**trainのみ**から取り、評価90件を校正には使いません。初回のモデル読込・エクスポート・量子化の時間は上記の単件レイテンシに含めず、端末・CPUスレッド数・温度・入力長で値は変わります。

## 開発とライセンス

```bash
python -m pip install -e ".[dev]"
python -m pytest tests -q
```

コードは[MIT License](LICENSE)です。ベースモデルと学習済みweightsには別のライセンスが適用されます。[THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md)を参照してください。
