# 例示ファイルの位置づけ

`request.json` と `response.example.json` はAPI形式の例です。確率・トークン数・モデルIDは説明用で、実測ではありません。

`smoke_cases.jsonl` は配線確認用の12件です。すべて `label_status=unreviewed` であり、人手で独立検証済みのgoldではありません。学習・校正・最終評価へそのまま流用せず、まず内容を確認してください。

同じcontextに違う判断基準を与える対照例などは同じgroup_idです。これらを別splitに分けたり、別々の独立標本として品質保証に使ったりしないでください。

`config.example.toml` は将来の実装向けの設定例です。現時点で読込コードは存在しません。未知のrevision等を実装時に確認し、採用した設定をrunへ保存してください。
