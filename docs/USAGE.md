# ERABIの使い方

最初のインストールとPythonサンプルは[README](../README.md)を参照してください。

## モデルのロード

```python
from erabi.model_loader import load_engine

engine = load_engine(device="cpu", revision="main")
# 明示指定する場合
engine = load_engine(device="cuda:0", model_format="onnx-fp16", revision="main")
```

`device`を省略すると、PyTorchからCUDAが見えれば`cuda:0`、そうでなければCPUになります。`auto`はCPUでONNX FP32、CUDA Execution Providerが使えるGPUでONNX FP16、ONNX Runtimeが使えない場合はPyTorchを選びます。GPU Providerの起動に失敗した際、ONNXモデルを黙ってCPU実行することはありません。

形式の明示指定には`pytorch`、`onnx-fp32`、`onnx-fp16`を使います。FP16 ONNXのCPU実行は非対応です。カスタムHubモデルIDは、`auto`では互換性のためPyTorchを選びます。明示指定でONNXを使う場合、配布モデルと同じファイル配置が必要です。

`revision="main"`は最新モデルです。固定運用では[配布物の識別](BENCHMARKS.md#配布物の識別)にあるコミットIDを指定してください。旧PyPI版の既定リビジョンとHubの最新モデルは同一とは限りません。

## 保存先・オフライン利用

```python
engine = load_engine(device="cpu", revision="main", cache_dir="D:/models/erabi")
```

```powershell
$env:ERABI_MODEL_CACHE_DIR = "D:\models\erabi"
erabi predict --request request.json --device cpu --revision main
```

Linux/macOSは`export ERABI_MODEL_CACHE_DIR=/data/models/erabi`です。優先順位は明示した`cache_dir`／CLIの`--model-cache-dir`、`ERABI_MODEL_CACHE_DIR`、Hugging Face標準キャッシュです。設定変更は既存ファイルを移動せず、新しい場所に取得します。

オフラインでは`load_engine(model_id="path/to/model", model_format="pytorch", device="cpu")`のようにローカルディレクトリを指定します。ONNXなら同じフォルダに`model.onnx`、`config.json`、`tokenizer.json`、`tokenizer_config.json`を用意してください。Hubと同じ`onnx/fp32/`・`onnx/fp16/`配置も利用できます。

## 入出力

入力は`ChoiceRequest.from_dict()`で検証します。

```json
{
  "schema_version": "1",
  "context": "ノート7冊と消しゴム2個を買った。",
  "question": "全部で何個？",
  "choices": [{"id": "a", "text": "9個"}, {"id": "b", "text": "10個"}]
}
```

候補は2〜16個で、IDは重複させません。入力全体をモデルの形式に整形した後の長さが512トークンを超える場合、エラーにします。文字数や`context`だけの長さとは異なります。

結果の`choices`に各IDと確率、`best_candidate_id`に最大logitのIDが入ります。候補の順序を保持し、padding候補を除いてSoftmaxを一度だけ適用します。`decision.status`は`review`、未校正モデルの`calibration.status`は`none`です。

## バッチ処理

```python
results = engine.predict_batch([request_a, request_b])
print([result.best_candidate_id for result in results])
# 明示的に変更する場合
results = engine.predict_batch([request_a, request_b], batch_size=8)
```

要求ごとに文脈・質問・候補数が異なっても利用できます。内部で入力長をまとめ、返却時に要求順を戻します。既定batchはPyTorch CUDAが16、CPU PyTorchとONNXが1です。複数要求を渡せることと、モデルの一括forwardが速いことは別です。旧モデルの実測ではONNXのbatchを増やすと遅くなりました（[測定詳細](BENCHMARKS.md)）。

## CLIとローカルHTTP API

上記JSONを`request.json`へ保存して使います。

```powershell
erabi doctor
erabi predict --request request.json --device cpu --revision main
erabi predict --request request.json --device cuda:0 --model-format onnx-fp16 --revision main
erabi predict --request request.json --model-cache-dir ".\model-cache" --revision main
erabi evaluate --input examples/smoke_cases.jsonl --output-dir runs/my-smoke --revision main
```

CLIの`ERABI_MODEL_FORMAT`は`--model-format`より低い優先度で、Pythonでは関数の引数を指定してください。`--model-id`にはHub IDまたはローカルパスを指定できます。

```powershell
python -m pip install "erabi[api]"
python -m erabi.serve --model-id path/to/downloaded-model --device cpu
```

HTTP APIはlocalhost限定です。単件は`POST /v1/choice`、バッチは最大16要求の`POST /v1/choice/batch`で、本文は`{"requests":[...]}`です。バッチ全体1 MiB、各要求64 KiBを上限とし、1件でも不正なら全体を422で拒否します。外部公開や実行権限は提供しません。

## GPUの依存関係

Windowsで初回取得に`WinError 1314`が出る場合、管理者実行ではなく、Python起動前に`$env:HF_HUB_DISABLE_SYMLINKS = "1"`を設定してください（対応するhuggingface_hubのバージョンが必要）。これは警告を隠す`HF_HUB_DISABLE_SYMLINKS_WARNING`とは別で、シンボリックリンク自体を使わない指定です。キャッシュがコピーになるため余分なディスク容量が必要になることがあります。ソース版のONNX取得もWindowsでは1 workerにして、初回symlink能力検査の競合を避けます。

GPU用PyTorchとONNX RuntimeのCUDA/cuDNN互換性を[公式対応表](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html)で確認してください。CPU版・GPU版ONNX Runtimeは同時にインストールしません。

```powershell
python -c "import onnxruntime as ort; print(ort.get_available_providers())"
```

`CUDAExecutionProvider`がなければ、GPU用ONNXを明示指定しても実行できません。ドライバーの対応CUDA上限と、PyTorch/ONNX Runtimeが利用するCUDA Runtimeのバージョンは別物です。
