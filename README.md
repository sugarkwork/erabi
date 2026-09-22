# ERABI（えらび）

ERABIは、`context`（状況）、`question`（判断基準）、2～16個の`choices`（候補）から、全候補の確率分布を返すローカル判断エンジンです。Jevの公式版や再現版ではありません。回答は常に確認対象（`review`）であり、最大確率は正解の保証ではありません。

## インストールと最初の推論

Python 3.11以上が必要です。現時点ではPyPIには公開していないため、GitHubからpipでインストールします。PyTorchのGPU版を使う場合は、先に利用環境に合うPyTorchをインストールしてください。

```bash
python -m pip install "git+https://github.com/sugarkwork/erabi.git"
erabi predict --request '{"schema_version":"1","context":"7冊のノートと2個の消しゴムを買った。","question":"全部で何個？","choices":[{"id":"nine","text":"9個"},{"id":"ten","text":"10個"}]}'
```

PowerShellではJSONの引用規則が異なるため、リポジトリを取得して `erabi predict --request examples/request.json` とするのが簡単です。初回は約1.75GBのモデルダウンロードが必要で、以降はHugging Faceのローカルキャッシュを再利用します。ネットワークが使えない場合は、事前取得したモデルのローカルディレクトリを`--model-id`で指定してください。

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

## 開発とライセンス

```bash
python -m pip install -e ".[dev]"
python -m pytest tests -q
```

コードは[MIT License](LICENSE)です。ベースモデルと学習済みweightsには別のライセンスが適用されます。[THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md)を参照してください。
