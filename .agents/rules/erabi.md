# ERABI workspace rule

このworkspaceでは、ルートのAGENTS.mdを共通指示として読み、KICKOFF.mdとSTATUS.mdで現在の作業範囲を確認してください。

@../../AGENTS.md

仕様の正本はdocs/ERABI_DESIGN.mdです。初回はM0/M1のみ。単一選択・GPU1基・薄いPython実装から始め、課金API、大規模学習、UI、分散基盤、過剰なユニットテストを先に作らないでください。

このルールの適用状態はAntigravityのCustomizationsで確認してください。AGENTS.mdの自動読込を仮定せず、依頼プロンプトでも参照します。global設定は変更しません。
