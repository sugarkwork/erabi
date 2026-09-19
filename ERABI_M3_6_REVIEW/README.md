# ERABI M3.6 レビュー資料

最初に `ERABI_M3_6_REVIEW.md` を読み、次の実装には `ERABI_M3_7_CALIBRATION_HANDOFF_NEXT.md` を使用してください。

## 内容

- レビュー結果と次の実装指示。
- source_excerpt.md：元ZIP内の関連コード、元の行番号付き。
- audit_saved_results.py：保存644件のlogits・正解・データ分離の独立再計算。
- probe_contracts.py：元のAPI/校正ローダー/生成器を使うCPU不具合再現。モデルはfake scorer。
- results/：今回実際に実行した結果、CPUテスト出力、環境と確認範囲。

元のユーザー提供ZIP、学習済み重み、仮想環境はこのレビューZIPへ重複収録していません。

## 再実行

元の `review_bundle(3).zip` を別のディレクトリへ展開し、既存の必要なCPU依存が入った環境で実行します。

```text
python ERABI_M3_6_REVIEW/audit_saved_results.py <元ZIPの展開先> <再計算結果の保存先>
python ERABI_M3_6_REVIEW/probe_contracts.py <元ZIPの展開先> <再現結果JSONの保存先>
```

既存のデータやモデルは上書きしません。モデルの学習やネットワークダウンロードは実行しません。
`probe_contracts.py` は今回の元コードの問題を再現する診断であり、修正後に同じ不具合を要求する恒久的なユニットテストではありません。

`results/historical_transitions.json` は前回のM3.4 ZIP内の保存予測とも比較した結果です。この比較自体に実モデル推論は使用していません。
