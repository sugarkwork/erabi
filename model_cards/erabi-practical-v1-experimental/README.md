---
language:
- ja
- en
- zh
license: apache-2.0
base_model: knowledgator/gliclass-instruct-large-v1.0
library_name: transformers
pipeline_tag: text-classification
tags:
- gliclass
- choice-classification
- experimental
- onnx
---

# ERABI（えらび）

Jevっぽい「状況を読んで候補を選ぶ」動きを、GLiClassで再現してみたローカル判断エンジンです。Jevの公式版・内部実装の再現版ではありません。

状況 `context`、判断基準 `question`、2〜16個の `choices` を渡すと、全候補の確率分布を返します。会話のツール選択、ゲームNPCの行動、コマンド危険性分類などの実験向けで、文章生成やツール実行はしません。

約438MパラメータのGLiClass追加学習モデルです。日本語・英語・中国語を含むデータを使用し、PyTorch safetensors・CPU用ONNX FP32・GPU用ONNX FP16を配布しています。入力全体の上限は512トークンです。

[GitHub・Pythonコード](https://github.com/sugarkwork/erabi) · [詳しい使い方](https://github.com/sugarkwork/erabi/blob/main/docs/USAGE.md) · [追加学習・データ形式](https://github.com/sugarkwork/erabi/blob/main/docs/TRAINING.md)

## すぐに試す

Python 3.11以上が必要です。Windows PowerShellでCPU ONNXを使う例です。

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
$env:HF_HUB_DISABLE_SYMLINKS = "1"  # Windowsで管理者権限なしのキャッシュを使用
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install erabi onnxruntime
```

Linux/macOSでは `python3 -m venv .venv`、`source .venv/bin/activate` に置き換えます。以下を `sample.py` に保存し、`python sample.py` で実行してください。

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

`revision="main"` を付けて、このページで公開しているモデルを選択してください。再現性が必要なら、末尾のweightsコミットIDを指定します。初回は必要なモデル形式だけダウンロードし、以後はキャッシュを再利用します。

### GPU・モデル形式・保存先

NVIDIA GPUでは別の仮想環境を使い、サンプルを `device="cuda:0"` に変更します。RTX 5060 Tiで確認したCUDA 13構成は以下です。

```powershell
python -m pip install torch==2.12.0 --index-url https://download.pytorch.org/whl/cu130
python -m pip install erabi onnxruntime-gpu==1.30.0
```

他の構成では環境に合う[GPU用PyTorch](https://pytorch.org/get-started/locally/)と[ONNX Runtimeの対応表](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html)を確認してください。CPU版 `onnxruntime` とGPU版 `onnxruntime-gpu` は同じ環境に入れないでください。

| 利用環境 | 自動選択・おすすめ | ファイルサイズの目安 |
|---|---|---:|
| CPU + ONNX Runtime | ONNX FP32 | 約1.76GB |
| NVIDIA GPU + CUDA Provider | ONNX FP16 | 約0.88GB |
| ONNX Runtimeなし | PyTorch safetensors | 約1.75GB |

形式・保存先は明示指定もできます。

```python
engine = load_engine(
    device="cpu", model_format="onnx-fp32",
    revision="main", cache_dir="./model-cache",
)
```

形式は `pytorch / onnx-fp32 / onnx-fp16`、保存先は `ERABI_MODEL_CACHE_DIR` 環境変数でも指定できます。バッチ処理・CLI・ローカルHTTP APIは[使い方](https://github.com/sugarkwork/erabi/blob/main/docs/USAGE.md)を参照してください。

GPU自動選択は容量を抑えたFP16ですが、機種・入力によってはFP32の方が速くなります。`load_engine(device="cuda:0", model_format="onnx-fp32", revision="main")` でGPUのFP32も試せます。

## ベンチマーク

測定環境はRTX 5060 Ti 16GB（2026-10-02）。評価対象は独自Decision Mix V2の未学習311件すべてと、公開データ10種類からseed 42で各16件抽出した共通160件です。Jevのみ2026-09-30の同じ311件のリモート結果です。

| モデル・入力形式 | 独自311件 | 公開・共通160件 |
|---|---:|---:|
| ERABI GPU PyTorch / ONNX FP32 / FP16 | 210 / 311（67.52%） | 99 / 160（61.88%） |
| Laya 0.3.21 reviewed：ID＋説明文 | 109 / 311（35.05%） | 92 / 160（57.50%） |
| Laya 0.3.21 reviewed：文章キー | 119 / 311（38.26%） | 105 / 160（65.63%） |
| CLEF 27B：NF4＋CPU退避 | 276 / 311（88.75%） | 131 / 160（81.88%） |
| CLEF 27B：BF16＋CPU退避 | 276 / 311（88.75%） | 132 / 160（82.50%） |
| CLEF Flash 9B：NF4・GPU常駐 | 258 / 311（82.96%） | 132 / 160（82.50%） |
| CLEF Flash 9B：BF16＋CPU退避 | 268 / 311（86.17%） | 133 / 160（83.13%） |
| Jev 1.13：リモートAPI | 287 / 311（92.28%） | 未測定 |

ERABIのカテゴリ別正答率（PyTorch / ONNX FP32）は、コマンド危険性80.49%、一般ゲート85.42%、NPC内面・目標42.22%、架空platformer37.50%、架空voxel survival58.62%、反実仮想77.61%です。

独自311件のラベルは合成教師の正解非表示再判定による一致で、独立した人手goldではありません。ERABIは同系統のtrainで調整済み、他モデルは同じ調整を行っていないため、独自testの順位は一般的な性能順位ではありません。独自testは学習データとgroup単位で分離されています。独自データ本体は非公開です。公開160件は各公開データセットのラベルを使用します。比較条件の詳細は[ベンチマーク資料](https://github.com/sugarkwork/erabi/blob/main/docs/BENCHMARKS.md)に掲載しています。

Layaは同じ候補でも`{ID: 説明文}`と`{候補文: None}`で結果が変わるため、包装を分けて記載しています。公開testはMASSIVE・XNLI・感情・ゲート分類などで、事前学習との重複までは否定できません。ERABIとLayaの公開3,584件の追加測定は詳細資料に分離し、160件の成績と混ぜて順位付けはしません。

### 速度・メモリの参考値

速度の評価対象は独自311件、batch 1、8 warmups後の入力整形を含む推論時間です。初回ダウンロードは除外。処理量は推論時間から算出します。メモリピークは公開testを含む測定全体の値で、ERABI/Layaは3,895件、CLEF/CLEF Flashは471件、CPUは311件です。

| 実行系 | 初期化 | 推論p50 / p95 | 処理量 | RAM / VRAM目安 |
|---|---:|---:|---:|---|
| ERABI GPU PyTorch FP32 | 19.83秒 | 59.46 / 96.27ms | 15.49件/秒 | RSS 2.58GiB / 全GPU増分2.08GiB |
| ERABI GPU ONNX FP16 | 10.12秒 | 30.51 / 80.91ms | 25.27件/秒 | RSS 1.68GiB / 全GPU増分2.35GiB |
| ERABI GPU ONNX FP32（TF32有効） | 10.04秒 | 32.88 / 62.71ms | 27.94件/秒 | RSS 2.37GiB / 全GPU増分2.69GiB |
| ERABI CPU ONNX FP32 | 11.26秒 | 826.28 / 1,598.28ms | 1.12件/秒 | RSS 2.78GiB / VRAMなし |
| Laya BF16：ID＋説明文 | 11.08秒 | 28.10 / 72.73ms | 28.37件/秒 | RSS 3.17GiB / 全GPU増分3.13GiB |
| Laya BF16：文章キー | 9.68秒 | 31.44 / 74.23ms | 26.65件/秒 | RSS 2.69GiB / 全GPU増分3.13GiB |
| CLEF 27B NF4＋CPU退避 | 56.74秒 | 2,076.83 / 2,335.16ms | 0.48件/秒 | RSS 14.37GiB / 全GPU増分13.00GiB |
| CLEF 27B BF16＋CPU退避 | 58.46秒 | 7,207.44 / 7,749.63ms | 0.14件/秒 | RSS 43.93GiB / 全GPU増分11.20GiB |
| CLEF Flash 9B NF4・GPU常駐 | 24.05秒 | 264.18 / 328.72ms | 3.74件/秒 | RSS 4.62GiB / 全GPU増分8.11GiB |
| CLEF Flash 9B BF16＋CPU退避 | 20.09秒 | 1,234.05 / 1,324.05ms | 0.81件/秒 | RSS 10.10GiB / 全GPU増分10.70GiB |

CPUはRyzen 7 5800X、GPUはRTX 5060 Ti 16GB。PyTorch 2.12.0＋CUDA 13.0、ONNX Runtime 1.30.0です。共通公開160件のERABI中央値はFP16 27.42ms、FP32 19.98msで、FP16が常に最速ではありません。FP32側のTF32は低精度の高速演算で、厳密なFP32演算とは区別します。

[CLEF](https://huggingface.co/Cloudflare/clef)は27Bモデルで、この16GB GPUでは両方式ともCPU退避を併用しています。専用の高速化kernelは未導入のため、本構成の速度を大容量GPU上のCLEF本来の性能とはみなしません。BF16はGPU常駐層が少なく、VRAMは小さい一方、RAMと転送時間が増えます。Layaは英語・多言語2モデル常駐。評価対象はテキスト入力・1つの選択問題です。

VRAM増分は他プロセスを含む全GPUのサンプル値です。JevのサーバーRAM/VRAMは取得できず、リモート速度もローカルGPU速度と直接比較しません。CPUは1プロセスあたり約4GiB以上の空きRAMに、OS・他アプリ分の余裕を確保してください。[測定条件・カテゴリ別結果](https://github.com/sugarkwork/erabi/blob/main/docs/BENCHMARKS.md)も確認してください。

[CLEF Flash](https://huggingface.co/Cloudflare/clef-flash)は9B系の小型モデルです。NF4はGPU常駐、BF16はCPU退避を併用する構成です。Embeddingと判定headはBF16を使い、専用の高速化kernelは両構成とも未導入です。量子化と配置の両方が速度・メモリに影響します。

## 制限・ライセンス

- 状況・質問・全候補を整形した入力全体で512トークンまで。超過時は切り詰めずエラーにします。
- 出力は確認対象（`review`）で、確率は未校正です。高い確率は正解や安全を保証しません。
- FP16では丸め差によって近接した候補の順位が変わる場合があります。FP32との完全一致は保証しません。
- NPC判断やゲーム制御には用途別の検証が必要です。危険コマンド分類は実行許可の代わりにはならず、権限・パス・許可リストなど別の制御が必要です。
- モデルは[GLiClass](https://huggingface.co/knowledgator/gliclass-instruct-large-v1.0)由来のApache-2.0、ERABIのPythonコードはMITです。

固定運用向けweightsコミット：`67c587ca4c2a15586de306853410cd82dc81dbee`（3形式共通）。`revision="main"` の代わりにこのIDを指定できます。
