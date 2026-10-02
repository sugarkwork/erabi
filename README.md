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
# 動作確認済みのCUDA 13構成（RTX 5060 Ti）
python -m pip install torch==2.12.0 --index-url https://download.pytorch.org/whl/cu130
python -m pip install erabi onnxruntime-gpu==1.30.0
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

GPUの自動選択は容量を抑えたFP16です。ただし機種・入力によってはFP32の方が速い場合があります。GPUでFP32を試すには `load_engine(device="cuda:0", model_format="onnx-fp32", revision="main")` を指定します。

## ベンチマーク

### 正答率

測定環境はRTX 5060 Ti 16GB（2026-10-02）。評価対象は独自Decision Mix V2の未学習テスト311件すべてと、公開データ10種類からseed 42で各16件抽出した共通160件です。Jevのみ2026-09-30の同じ311件のリモート結果です。

| モデル・入力形式 | 独自311件 | 公開・共通160件 |
|---|---:|---:|
| ERABI GPU PyTorch / ONNX FP32 / FP16 | 210 / 311（67.52%） | 99 / 160（61.88%） |
| Laya 0.3.21 reviewed：ID＋説明文 | 109 / 311（35.05%） | 92 / 160（57.50%） |
| Laya 0.3.21 reviewed：文章キー | 119 / 311（38.26%） | 105 / 160（65.63%） |
| CLEF 27B：NF4＋CPU退避 | 276 / 311（88.75%） | 131 / 160（81.88%） |
| CLEF 27B：BF16＋CPU退避 | 276 / 311（88.75%） | 132 / 160（82.50%） |
| Jev 1.13：リモートAPI | 287 / 311（92.28%） | 未測定 |

Layaは同じ候補でもAPIへの渡し方で結果が変わるため、`{ID: 説明文}` と `{候補文: None}` を分けています。公開テストはMASSIVE・XNLI・感情・ゲート分類などです。ERABIとLayaの公開3,584件の追加測定は[詳細資料](docs/BENCHMARKS.md)に掲載しています。160件の成績と混ぜて順位付けはしません。

独自311件のラベルは合成教師の再判定一致で、独立した人手goldではありません。独自データ本体は非公開です。公開160件は各公開データセットのラベルを使用します。ERABIは同系統のtrainで調整済み、他モデルに同じ追加学習はしていないため、独自testの順位を一般性能の順位とは呼びません。[カテゴリ別成績・比較条件](docs/BENCHMARKS.md)も確認してください。

### 速度とメモリの目安

速度の評価対象は独自311件、batch 1、8回ウォームアップ後の入力整形を含む推論時間です。初回ダウンロードは除外。処理量は推論時間から算出します。RAM/VRAMピークは公開testを含む測定全体の値で、ERABI/Layaは3,895件、CLEFは471件、CPUは311件です。

| 実行系 | 初期化 | 推論p50 / p95 | 処理量 | RAM / VRAM目安 |
|---|---:|---:|---:|---|
| ERABI GPU PyTorch FP32 | 19.83秒 | 59.46 / 96.27ms | 15.49件/秒 | RSS 2.58GiB / 全GPU増分2.08GiB |
| ERABI GPU ONNX FP16 | 10.12秒 | 30.51 / 80.91ms | 25.27件/秒 | RSS 1.68GiB / 全GPU増分2.35GiB |
| ERABI GPU ONNX FP32（TF32有効） | 10.04秒 | 32.88 / 62.71ms | 27.94件/秒 | RSS 2.37GiB / 全GPU増分2.69GiB |
| ERABI CPU ONNX FP32 | 11.26秒 | 826.28 / 1,598.28ms | 1.12件/秒 | RSS 2.78GiB / VRAMなし |
| Laya BF16：ID＋説明文 | 11.08秒 | 28.10 / 72.73ms | 28.37件/秒 | RSS 3.17GiB / 全GPU増分3.13GiB |
| Laya BF16：文章キー | 9.68秒 | 31.44 / 74.23ms | 26.65件/秒 | RSS 2.69GiB / 全GPU増分3.13GiB |
| CLEF NF4＋CPU退避 | 56.74秒 | 2,076.83 / 2,335.16ms | 0.48件/秒 | RSS 14.37GiB / 全GPU増分13.00GiB |
| CLEF BF16＋CPU退避 | 58.46秒 | 7,207.44 / 7,749.63ms | 0.14件/秒 | RSS 43.93GiB / 全GPU増分11.20GiB |

CPUはRyzen 7 5800X。GPUはRTX 5060 Ti、PyTorch 2.12.0＋CUDA 13.0、ONNX Runtime 1.30.0です。共通公開160件のERABI中央値はFP16 27.42ms、FP32 19.98msで、FP16が常に最速ではありません。FP32側のTF32は低精度の高速演算なので、厳密なFP32演算とは区別します。

[CLEF](https://huggingface.co/Cloudflare/clef)は27Bモデルです。この16GB GPUでは両方式ともCPU退避を併用し、専用の高速化kernelは未導入です。ここでの速度は本構成の実測で、大容量GPU上のCLEF本来の性能を表すものではありません。BF16はGPU常駐層が少ないためVRAMは小さくなりますが、RAMと転送時間が増えます。Layaは英語・多言語2モデル常駐。評価対象はテキスト入力・1つの選択問題です。

VRAM増分は他プロセスも含む全GPUのサンプル値です。JevのサーバーRAM/VRAMは取得できず、リモート速度もローカルGPU速度と直接比較しません。CPUは1プロセスあたり約4GiB以上の空きRAMを目安にしてください。[データセット別の速度・メモリ測定の定義](docs/BENCHMARKS.md)は詳細資料に掲載しています。

## 制限と安全性

全候補のlogitsに一度だけSoftmaxを適用し、候補IDと入力順を保持します。入力上限は状況・質問・候補を整形した全体で512トークンです。超過入力は黙って切り詰めずエラーにします。

出力は確認対象（`review`）で、未校正です。高い確率は正解や安全の保証ではありません。危険コマンド判定も実行許可の代わりにはならず、パス・権限・許可リストなど別の制御が必要です。

## さらに詳しく

- [使い方](docs/USAGE.md)：バッチ処理、キャッシュ、形式選択、CLI、HTTP API
- [ベンチマーク](docs/BENCHMARKS.md)：比較条件、速度・メモリ、量子化・長文の知見
- [追加学習](docs/TRAINING.md)：JSONL形式、group分割、学習・モデル選択、再現方法
- [設計仕様](docs/ERABI_DESIGN.md)：実装の入力・数値契約

コードは[MIT](LICENSE)。モデルと依存には別のライセンスが適用されます（[第三者ライセンス](THIRD_PARTY_LICENSES.md)）。
