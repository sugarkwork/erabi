# ERABI（えらび）

自然文・判断基準・可変の選択肢から確率分布を返す、ローカル判断エンジンです。

## 実装状況 (2026-09-18)

- **M0（環境基盤）** & **M1（既存モデル推論・評価）** が実装・実測完了。
- 採用モデル: `knowledgator/gliclass-multilang-mini` (Apache-2.0, ~0.3B)
- 単一 Softmax 正規化による全候補の完全な確率分布取得、厳密な入力契約・バリデーション、評価指標（Accuracy, NLL, Brier, Reliability bins）の計算に対応。

## セットアップ

```pwsh
# 1. 仮想環境の作成 (Python 3.12推奨)
py -3.12 -m venv .venv

# 2. PyTorch (CUDA 12.4版) のインストール
.venv\Scripts\pip install torch --index-url https://download.pytorch.org/whl/cu124

# 3. 依存ライブラリおよびERABIのインストール
.venv\Scripts\pip install -e .[dev]
```

## 使い方 (CLI)

### 1. 環境診断 (`doctor`)
システムスペック、PyTorch/CUDA、GPU、VRAM、ディスク使用量を取得・表示します。

```pwsh
.venv\Scripts\python -m erabi doctor [--save runs/environment.json]
```

### 2. 単一推論 (`predict`)
JSONファイルまたはJSON文字列を入力とし、全候補の確率分布を計算して返します。

```pwsh
.venv\Scripts\python -m erabi predict --request examples/request.json
```

出力例:
```json
{
  "schema_version": "1",
  "model_id": "knowledgator/gliclass-multilang-mini",
  "choices": [
    {"id": "technical", "probability": 0.933457},
    {"id": "billing", "probability": 0.006144},
    {"id": "sales", "probability": 0.002561},
    {"id": "insufficient", "probability": 0.057838}
  ],
  "best_candidate_id": "technical",
  "decision": {"status": "review", "reason": "policy_not_configured"},
  "calibration": {"status": "none", "artifact_id": null},
  "usage": {
    "input_tokens": 47,
    "truncated": false,
    "latency_ms": 310.87
  }
}
```

### 3. ベンチマーク評価 (`evaluate`)
JSONL形式の評価データを順次推論し、Accuracy、NLL、Brierスコア、確信度別ビンを集計して `runs/<run_id>/` に成果物を保存します。

```pwsh
.venv\Scripts\python -m erabi evaluate --input examples/smoke_cases.jsonl --output-dir runs/smoke_eval_m1
```

生成される成果物:
- `config.json`: 実行設定（モデルID、リビジョン、デバイス等）
- `environment.json`: 実行環境情報
- `metrics.json`: Accuracy, NLL, Brier, Reliability bins, 推論レイテンシ
- `predictions.jsonl`: 各問ごとの推論結果、確率分布、正否、トークン数
- `notes.md`: サマリーメモ

### 4. ローカルHTTP APIサーバー (`serve`)
`127.0.0.1:8765` で動作する、全件review固定・1並行排他制御のローカル推論サーバーを起動します。

```pwsh
# サーバー起動 (オフライン可)
$env:HF_HUB_OFFLINE = "1"
.venv\Scripts\python -m erabi.serve --model-id runs/m2_1/trained_instruct_base/checkpoint --port 8765
```

PowerShell からの推論リクエスト例:
```pwsh
# 健全性確認
Invoke-RestMethod -Uri "http://127.0.0.1:8765/health" -Method Get

# 推論リクエスト
$body = @{
    context = "プランAは100円で5日、プランBは300円で1日です。"
    question = "最も安いプランを選んでください。"
    choices = @(
        @{ id = "a"; text = "プランA" },
        @{ id = "b"; text = "プランB" }
    )
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8765/predict" -Method Post -ContentType "application/json" -Body $body
```

### 5. 確率校正 (`calibrate`)
独立した校正データ（`calibration.jsonl`）から生logitsを抽出し、NLLを最小化する単一温度 $T > 0$ を最適化して `calibration.json` を生成します。

```pwsh
.venv\Scripts\python -m erabi.calibrate --data-dir data/m3_1 --model-id runs/m2_1/trained_instruct_base/checkpoint --output-dir runs/m3_1
```

### 6. テストの実行 (CPU・オフライン)
契約検証、Softmax数値安定性、温度校正、HTTP API契約、排他制御など全31件の単体テストを実行します。

```pwsh
.venv\Scripts\pytest tests/ -v
```

## ファイル構成

| ファイル | 役割 |
|---|---|
| `docs/ERABI_DESIGN.md` | 技術背景・仕様・学習・評価・テスト・運用をまとめた正本 |
| `AGENTS.md` | 作業上の制約と過剰設計防止の共通指示 |
| `STATUS.md` | 現在の作業状況・実測値・次の一手 |
| `src/erabi/schema.py` | 入出力スキーマと契約バリデーション |
| `src/erabi/inference.py` | GLiClassアダプターと全候補logits/Softmax推論 |
| `src/erabi/evaluate.py` | Accuracy, NLL, Brier, 確信度ビン, 選択的リスク集計 |
| `src/erabi/calibrate.py` | 単一温度最適化とモデルハッシュ付き校正アーティファクト生成 |
| `src/erabi/api.py` | FastAPI アプリケーションファクトリ（lifespan, 1並行排他, review固定） |
| `src/erabi/serve.py` | ローカルHTTP APIサーバーCLI (127.0.0.1:8765) |
| `src/erabi/__main__.py` | CLIエントリーポイント (`doctor`, `predict`, `evaluate`) |
| `tests/` | 高速なCPU単体テスト群 (31件) |
| `examples/` | APIリクエスト例・レスポンス例・配線確認データ |
| `runs/` | 評価実行結果・監査レポート・校正成果物・レビューバンドルの保存先 |

## ライセンス

ERABI original source code is licensed under the [MIT License](LICENSE).

Third-party libraries, pretrained models, model weights, and upstream
components remain subject to their respective licenses.
See [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) for details.
