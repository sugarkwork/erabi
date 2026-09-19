# ERABI — M3.7 ZIP実物レビュー追補 / M4.1開始前の最小修正

作成日: 2026-09-19

## 結論

M3.7 の主要目的は達成済みとして扱う。

確認できたこと:
- review_bundle.zip は 40 files / 151,151 bytes。
- SHA256 は `d288cd77782194860334e21b594db115a659f9625c607593b05a073dc285ab3a` で報告値と一致。
- ZIP破損なし。
- `status="applied"` と scope/adoption の分離は実コードへ反映。
- ローカルcheckpointのhash照合、schema/max_tokens/formatter確認、sidecar manifest、GF意味状態監査、APIでの単一温度適用確認が成果物に含まれる。
- 校正値 T=3.1097、重み、既存データ、M3.7 API契約は変更しない。

M4.1へ進む前に、以下2点だけ最小修正する。再学習・再校正は不要。

---

## 1. calibration contract の precision を「存在確認」ではなく一致確認にする

現在の `load_and_verify_calibration()` は、
`contract.precision` が空でないことしか確認していない。

現在:
```python
precision = contract.get("precision")
if not precision:
    raise ValueError(...)
```

このままでは、例えば
`precision="different_precision_mode"`
でも校正を applied として読み込める。

### 修正

baseline runtime の期待値を一箇所の定数として定義し、
artifact側の precision と完全一致させる。

例:
```python
RUNTIME_PRECISION_CONTRACT = "float32_forward_float64_nll"

precision = contract.get("precision")
if precision != RUNTIME_PRECISION_CONTRACT:
    raise ValueError(
        f"Calibration contract precision mismatch: "
        f"expected '{RUNTIME_PRECISION_CONTRACT}', got '{precision}'"
    )
```

artifact生成、cache manifest、runtime検証で同じ定数を共有する。
新しい抽象化層は作らない。

### テスト

既存 `test_rejection_of_misapplications` に1ケース追加するだけでよい。

- precisionを別文字列に書換える
- `load_and_verify_calibration()` が拒否する

---

## 2. raw logits sidecar に「datasetと各logits行の対応」を結び付ける

現在のsidecarは、
- datasetファイルのSHA256
- logitsファイルのSHA256
- model hash
- record count
- formatter / precision

を確認している。

これはファイル改変検知としては有効だが、
`save_logits_with_manifest(raw_records=A, data_path=B)` のように、
生成時点で別データ由来のraw_recordsとdata_pathを誤って組み合わせた場合、
その誤対応をmanifest自身では検出できない。

コードコメントには
「Exact candidate ID order and target index integrity」
まで保証すると書かれているため、実装と契約を合わせる。

### 最小修正

manifestに大きなデータ構造を重複保存しない。

dataset JSONLとraw_recordsから、対応に必要な最小情報だけを正規化して
`alignment_sha256` を作る。

各行について例えば:
```text
id
ordered choice ids
target choice id / target index
```

を連結したdigestを作り、全行分をまとめてSHA256する。

保存時:
- dataset側alignment digest
- raw logits側alignment digest
が一致しなければ保存自体を失敗させる。
一致したdigestをmanifestへ保存する。

読込時:
- 現datasetから再計算
- raw logitsから再計算
- manifestの値
の3者が一致することを確認する。

候補本文全文やcontext全文をsidecarに複製する必要はない。
dataset本体のSHA256が既にそれらを拘束している。

### テスト

1ケースだけ追加:
- 同じ件数だがID/targetまたは候補順の異なるdatasetとraw_recordsを組み合わせる
- `save_logits_with_manifest()` またはload時検証が拒否する

---

## 3. baseline checkpointで tokenizer も必須契約にする

現在のartifactには
- `model.safetensors`
- `config.json`
- `tokenizer.json`
- `tokenizer_config.json`

のhashが入っており、artifactに列挙されているファイルは実際に照合される。

ただしloaderの「最低限必須」は
`model.safetensors` と `config.json` の2つだけなので、
手編集artifactからtokenizer項目を削除すると受理できる。

今回の baseline `W_v2_ce10` に限っては、
少なくとも以下4ファイルを必須とする。

```text
model.safetensors
config.json
tokenizer.json
tokenizer_config.json
```

将来別tokenizer形式を使うモデルへ一般化する仕組みは今は作らない。
モデル交換フェーズで必要になった時に見直す。

テストは tokenizer.json をartifactから削除した場合の拒否を1ケース追加。

---

## 4. 修正後の確認

次だけで十分。

1. CPU unit tests。
2. M3.7 `calibration.json` をそのまま再読込できる。
3. `raw_logits_calibration.jsonl` と `raw_logits_fresh_eval.jsonl` の既存sidecarを、新形式へ移行または再生成する。
4. APIを `--require-calibration` で起動し、既存代表1～2問で `T=3.1097`, `status=applied`, `decision=review` を確認。

温度再探索、モデル再学習、新データ作成はしない。

旧M3.7成果物を上書きせず、
`runs/m3_7_1_contract_fix/` 等へ差分成果物を置く。

---

## 5. その後

上記が通ったらM3は終了。

既に用意した `ERABI_M4_1_EXCEPTION_PRIORITY_NEXT.md` の
「例外・優先順位」実験へ進む。

M4.1でも:
- baseline `W_v2_ce10` + M3.7 calibration を上書きしない。
- 実験版の新重みに既存T=3.1097を流用しない。
- 通常CEのまま開始。
- NLI、ルーティング、偽指示、別モデル等を同時追加しない。
- テストや抽象化を増やし過ぎない。

---

## Codex / Antigravityへの指示

```text
M3.7 review_bundle.zip の実物レビューで、
M3.7の主要目的は達成済みと確認しました。

M4.1へ進む前に、この文書の3点だけ最小修正してください。

1. calibration contract の precision を存在確認ではなくruntime期待値との完全一致にする。
2. raw logits sidecarへdataset↔logits行対応のalignment digestを追加する。
3. 現baseline checkpointでは tokenizer.json / tokenizer_config.json も必須hash対象にする。

再学習、温度再探索、新データ生成、API機能追加は行わないでください。
M3.7の重み・T=3.1097・既存評価結果は変更しません。

各修正に必要な最小テストだけ追加し、
既存テストと代表1～2問のAPI接続確認まで行ってください。
旧M3.7成果物を上書きせず、差分成果物を別ディレクトリへ保存してください。

修正が通ったらM3を終了とし、
その後 ERABI_M4_1_EXCEPTION_PRIORITY_NEXT.md の範囲へ進んでください。
```
