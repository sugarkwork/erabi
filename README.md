# ERABI（えらび）

Jevっぽい「状況を読んで候補を選ぶ」動きを、GLiClassを使って再現してみた実験プロジェクトです。Jevの公式版でも、内部実装の再現版でもありません。

状況 `context`、判断基準 `question`、2〜16個の `choices` を渡すと、全候補の確率分布をローカルで返します。会話のツール選択、ゲームNPCの行動、コマンドの危険性分類などを試すための判断エンジンで、文章や画像を生成したり、選んだツールを実行したりはしません。

GLiClassの約438Mパラメータモデルを追加学習し、PyTorch safetensors・CPU用ONNX FP32・GPU用ONNX FP16を配布しています。入力全体の上限は512トークン。日本語・英語・中国語を含むデータで実験していますが、品質は用途ごとに検証が必要です。

[公開モデル](https://huggingface.co/sugarknight/erabi-practical-v1-experimental) · [詳しい使い方](docs/USAGE.md) · [ベンチマーク詳細](docs/BENCHMARKS.md) · [追加学習とデータ形式](docs/TRAINING.md)

## すぐに試す

Python 3.11以上が必要です。以下はWindows PowerShellの例です。

### 1. 仮想環境とインストール

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
$env:HF_HUB_DISABLE_SYMLINKS = "1"  # Windowsで管理者権限なしのキャッシュを使用

# CPU + ONNX FP32（おすすめ）
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install erabi onnxruntime
```

Linux/macOSは `python3 -m venv .venv` と `source .venv/bin/activate` に置き換えます。有効化できない場合、Windowsでは `.\.venv\Scripts\python.exe` を直接使えます。

NVIDIA GPUを使う場合は、別の仮想環境で、環境に合う[GPU用PyTorch](https://pytorch.org/get-started/locally/)を導入してから次を実行します。

```powershell
python -m pip install erabi onnxruntime-gpu
```

CPU版 `onnxruntime` とGPU版 `onnxruntime-gpu` は同じ環境に両方入れないでください。GPUには互換なCUDA/cuDNNが必要です（[対応表](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html)）。ONNXを使わない場合は `pip install erabi` だけでPyTorch版を利用できます。

### 2. sample.pyを作る

以下を `sample.py` として保存してください。初期化と推論の時間を表示します。

```python
from time import perf_counter
from erabi.model_loader import load_engine
from erabi.schema import ChoiceRequest

print("モデルを読み込みます（初回はダウンロード）...", flush=True)
t = perf_counter()
engine = load_engine(device="cpu", revision="main")
print(f"初期化: {perf_counter() - t:.2f}秒 / {engine.model_format}")

request = ChoiceRequest.from_dict({
    "context": "ユーザーが今日の宮崎の天気を知りたいと言った。",
    "question": "次に使う機能を選んでください。",
    "choices": [
        {"id": "chat", "text": "雑談をする"},
        {"id": "web", "text": "Web検索する"},
        {"id": "image", "text": "イラストを作成する"},
    ],
})

print("推論します...", flush=True)
t = perf_counter()
result = engine.predict(request)
print(f"推論: {perf_counter() - t:.3f}秒")
print("選択:", result.best_candidate_id)
print("確率:", {c.id: round(c.probability, 4) for c in result.choices})
```

```powershell
python sample.py
```

GPUでは `device="cuda:0"` に変更します。モデルが未取得なら、必要な形式だけ自動ダウンロードします（約0.88〜1.76GB）。初期化時間には初回ダウンロードが含まれ、2回目以降はキャッシュを再利用します。

この例の `revision="main"` は最新の公開モデルを選ぶ指定です。PyPI版0.1.4の既定モデルは最新ではないため、この指定を付けてください。再現性が必要な場合は[モデルのコミットID](docs/BENCHMARKS.md#配布物の識別)を指定してください。

## モデル形式と保存先

| 利用環境 | おすすめ | 自動選択 |
|---|---|---|
| CPU + ONNX Runtime | ONNX FP32 | `onnx-fp32` |
| NVIDIA GPU + CUDA対応ONNX Runtime | ONNX FP16 | `onnx-fp16` |
| ONNX Runtimeなし・互換性優先 | PyTorch safetensors | `pytorch` |

```python
engine = load_engine(
    device="cpu", model_format="onnx-fp32",
    revision="main", cache_dir="./model-cache",
)
```

保存先は `ERABI_MODEL_CACHE_DIR` 環境変数でも指定できます。形式の明示指定、バッチ処理、CLI、ローカルHTTP APIは[使い方](docs/USAGE.md)を参照してください。

## ベンチマーク

### 独自データセットでLaya・Jevと比較

Decision Mix V2の未学習テスト311件に、同じ状況・質問・候補順を渡しました（2026-09-30）。

| モデル | 正答数 | 正答率 |
|---|---:|---:|
| ERABI（PyTorch / ONNX FP32） | 210 / 311 | 67.52% |
| ERABI（ONNX FP16） | 211 / 311 | 67.85% |
| Laya 0.3.21 reviewed | 107 / 311 | 34.41% |
| Jev 1.13（リモートAPI） | 287 / 311 | 92.28% |

ラベルは独立した人手goldではなく、合成教師の再判定一致です。ERABIは同系統のtrain splitで調整済み、Layaには同じ調整を行っていないため、一般的な性能順位ではありません。FP16の丸め差やカテゴリ別成績などの[比較条件・詳細](docs/BENCHMARKS.md)も確認してください。

### 速度とメモリの目安

今回のモデルを同じ311件・batch 1で測定しました。初回ダウンロードは含めません。

| 実行系 | 初期化 | 推論p50 / p95 | 処理量 | RAM / VRAM目安 |
|---|---:|---:|---:|---|
| GPU ONNX FP16 | 8.86秒 | 74.93 / 121.25ms | 12.73件/秒 | ピークRSS約1.59GiB / 全GPU使用量増分約2.53GiB |
| CPU ONNX FP32 | 11.22秒 | 778.00 / 1,524.25ms | 1.20件/秒 | ピークRSS約3.73GiB / VRAMなし |
| Laya 標準BF16 | 6.96秒 | 32.81 / 52.13ms | 27.84件/秒 | RAM未計測 / 全GPU使用量増分約3.92GiB |
| Jev リモートAPI | — | 652.70 / 843.50ms | 7.69件/秒（8並列） | サーバーRAM・VRAM未取得 |

CPUはRyzen 7 5800X、GPUはRTX A4000 16GBです。ERABIのGPU測定は強いクロック低下があり、Laya測定時と条件が揃っていないため、通常時の性能や速度順位は示しません。VRAM増分は他プロセスを含む全GPUのサンプル値、Jevは通信・サーバー待ち込みです。CPUは1プロセスあたり約4GiB以上の空きRAMを目安にしてください。詳しい[測定条件](docs/BENCHMARKS.md)も確認してください。

公開データでの比較や過去のモデルの測定記録は、[ベンチマーク詳細](docs/BENCHMARKS.md)に分けて掲載しています。

## 制限と安全性

全候補のlogitsに一度だけSoftmaxを適用し、候補IDと入力順を保持します。入力上限は状況・質問・候補を整形した全体で512トークンです。超過入力は黙って切り詰めずエラーにします。

出力は確認対象（`review`）で、未校正です。高い確率は正解や安全の保証ではありません。危険コマンド判定も実行許可の代わりにはならず、パス・権限・許可リストなど別の制御が必要です。

## さらに詳しく

- [使い方](docs/USAGE.md)：バッチ処理、キャッシュ、形式選択、CLI、HTTP API
- [ベンチマーク](docs/BENCHMARKS.md)：比較条件、速度・メモリ、量子化・長文の知見
- [追加学習](docs/TRAINING.md)：JSONL形式、group分割、学習・モデル選択、再現方法
- [設計仕様](docs/ERABI_DESIGN.md)：実装の入力・数値契約
- [作業記録](STATUS.md)：実測の履歴と未完了事項

コードは[MIT](LICENSE)。モデルと依存には別のライセンスが適用されます（[第三者ライセンス](THIRD_PARTY_LICENSES.md)）。
