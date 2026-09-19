# ERABI — M3.4：勾配蓄積の修正と、条件を固定した1回の比較学習

作成日：2026-09-18  
対象：既存 `erabi-local` を実装する Codex / Antigravity  
位置付け：M3.3追補ZIPの実コード監査を受けた追加指示。既存の入出力仕様・review固定方針を維持する。

## 0. 今回の結論と範囲

**Paired Contrastive Learning、独自の正則化、データの再生成より先に、通常学習の勾配蓄積を修正する。**

最新ZIPの `src/erabi/train.py` に、同じoptimizer更新内で損失の除数が8,7,…,1へ変わる不具合を確認した。これは最後の端数だけでなく、通常の8回蓄積でも発生する。レビュー環境ではアップロードされた `run_full_training` と `compute_batch_loss` の関数本体を利用したCPUの小モデル診断で再現し、修正案ではまとめて計算した平均損失の勾配と一致した。本物のGLiClassの再学習・精度回復は未検証である。

今回行うことは以下に限定する。

1. 手元のコードと今回確認した不具合を照合し、修正前の挙動を小さく再現する。
2. 勾配蓄積のサンプル重み付けを最小修正し、実処理を通るCPU回帰検証を行う。
3. データ、初期チェックポイント、シャッフル、学習条件、チェックポイント選択基準をできる限り固定し、元のB0から**1回だけ**再学習する。
4. 保存済みB0 / W_fix / W_v2と新モデルを同じデータ・指標で比較し、差と限界を記録する。

**行わないこと：** ペア学習の導入、データの増量・再生成・比率変更、別タスクの混合、損失の追加、モデル交換、LoRA、量子化、AMPの新規導入、校正、API変更、自動採用、UI、DB、分散処理、有料API、依存関係の一括更新。

計画だけで止まらず、上記範囲の確認・最小修正・実行・結果保存まで進める。ツール側が要求する承認を迂回しない。既存GPUジョブを停止せず、既存のデータ・結果・チェックポイントを上書きしない。

## 1. 監査の根拠

### 1.1 対象

- `review_bundle_followup.zip`
- SHA256：`4179fc2569b3d42f65a7b9bcdc5a9fbc8121fdbd0cff3618eebf3352b0491ed0`
- 44ファイル、183,065 bytes。
- 監査時 `src/erabi/train.py` のUTF-8文字列SHA256：`faca48cc761ed6b0e85c6201a9334b4b2333257011e09e3a774f2ed24447db67`

M3.3本体ZIPと追補ZIPで学習コードは同一。変更はSTATUSと追補の集計成果物。M3.2版との比較では、この除数計算はM3.3の端数対応で追加されたものだった。

ハッシュが違ってもファイル全体を巻き戻さず、対応箇所を読む。添付パッチは監査した版に対する参考差分であり、別版へ無確認で適用しない。

### 1.2 確認できた成績と、原因の未確定性

保存済み9予測ファイル・732行を再計算し、報告の正答数・NLL・Brierを確認した。

- eval_v2：B0 89/200、W_fix 106/200、W_v2 117/200。
- 正解が異なる47組：W_fix 14組両問正解、W_v2 8組。
- W_v2のこの47組で、同じ予測を返した組は34組。
- goal_followingの31組はW_v2で両問正解1組、未切替25組。
- composite_logicの7組はW_v2で両問正解0組、全7組で同一予測。

これらは観測である。重みがZIPにないため再推論はしていない。「語彙バイアスが原因」「ペア学習が必須」「このバグだけで全退行を説明できる」と断定しない。

## 2. 不具合の内容

現在の通常学習ループには次の形がある。

```python
window_offset = batch_idx % trainer.gradient_accumulation_steps
remaining_in_window = trainer.gradient_accumulation_steps - window_offset
remaining_in_epoch = total_micro_batches - batch_idx
current_window_size = min(remaining_in_window, remaining_in_epoch)
loss_scaled = loss / current_window_size
```

`current_window_size` は「今回の更新で平均する全ミニバッチ数」ではなく「残り回数」になっている。8回蓄積で除数が8,7,6,5,4,3,2,1と変わる。

各ミニバッチが同じ2件なら、本来の損失は

```text
(L1 + L2 + ... + L8) / 8
```

だが、現状は

```text
L1/8 + L2/7 + ... + L7/2 + L8
```

となる。8番目は1番目の8倍の係数になる。全係数の和は約2.717857であり、単なる均等平均ではない。AdamWや勾配クリップもあるため、「実効学習率が正確に2.717857倍」とは表現しない。サンプル間の相対的な寄与が変わることが問題である。

## 3. 修正する計算

### 3.1 基本契約

`compute_batch_loss` は、そのミニバッチに含まれる**サンプルごとのクロスエントロピーの平均**を返す。したがって、更新対象ウィンドウ全体の平均にするには次を使う。

```text
backwardへ渡すloss
= ミニバッチの平均loss × ミニバッチの実件数 / 更新ウィンドウの総実件数
```

ウィンドウとは、1回の `optimizer.step()` までに蓄積する範囲。

例：

- 2件 × 8回 → 全16件。各ミニバッチの重み2/16。
- 最後が2件 × 4回 → 全8件。各ミニバッチの重み2/8。
- 最後が2,2,2,1件 → 全7件。重み2/7,2/7,2/7,1/7。

単に最後のウィンドウまで一律8で割る修正へ戻さない。端数サンプルを黙って捨てる `drop_last` も導入しない。

### 3.2 現行ループへの最小変更例

現行のインデックス変数を維持するなら、以下の計算でよい。

```python
window_start_batch = (
    batch_idx // trainer.gradient_accumulation_steps
) * trainer.gradient_accumulation_steps
window_start_sample = window_start_batch * batch_size
window_end_sample = min(
    window_start_sample
    + trainer.gradient_accumulation_steps * batch_size,
    len(epoch_records),
)
window_sample_count = window_end_sample - window_start_sample

loss = trainer.compute_batch_loss(
    tokenized, target_indices, num_choices_list, max_num_classes
)
loss_scaled = loss * (len(batch_records) / window_sample_count)
loss_scaled.backward()
```

分母は同じ更新ウィンドウ内で変わらない。不要になったremaining系変数は除去する。更新タイミング・クリップ・zero_gradは1ウィンドウにつき1回を維持する。

通常学習の修正を優先する。現在の64件過学習診断を大きく再設計しない。共通化が本当に必要な場合のみ、小さな関数へ分ける。汎用Trainerフレームワークは作らない。

### 3.3 修正前後の再現資料

同梱の `repro_accumulation.py` は、ネットワーク・GLiClass・GPU不要の監査用スクリプト。PyTorchだけを使用する。

- 実際の `run_full_training` と `compute_batch_loss` の関数本体をASTで読み込む。
- モデルはCPUの小さな決定的モデル、optimizerは勾配記録用に置き換える。
- 本来の除数計算・backward・更新境界を実行する。
- 元の平均損失を一括で微分した結果と比較する。
- 参考パッチを生成し、その修正案でも同じ比較を行う。

監査で得た16件の例：正しい一括平均勾配 +0.625、旧ループ -0.2821428329、修正案 +0.625。これは**合成CPU例**であり、GLiClassの実勾配や精度回復を測定した数字ではない。

この監査スクリプトは、監査した旧ブロックがなくなると停止する。その停止は修正後の失敗を意味しない。恒久テストは下記の方法で実処理へつなぎ、監査スクリプトのAST読込方式を製品コードへ入れない。

## 4. テストは「実ループの勾配が合うか」に絞る

CPUの小さなモデルで、修正した学習処理を通して比較する。dropoutを無効にし、BatchNorm等のバッチ依存処理を使わず、比較はクリップ前の勾配（またはクリップが発動しない設定）で行う。

1つの責務を少数ケースで確認する。

- 通常の16件を、16件一括と2件×8回で比較。
- データ終端に端数ウィンドウがあるケース。
- 最後のミニバッチが1件になるケース。
- 必要なら蓄積回数1の既定動作。

損失の値だけでなく、パラメータへ蓄積された勾配と更新回数を比較する。許容誤差はdtypeに合わせる。全エポックの平均lossは、サンプル数に応じた表示でよいが、表示値とbackward用のスケールを混同しない。

テストの中に正しい式を別途書いて、それだけを自己確認して終えない。実際の修正箇所を通すことが必須。既存の依存を軽くするための小さな関数抽出やfake modelは許容するが、大きなモック・プラグイン基盤を作らない。

既存 `test_independent_expected_cases` には `assert "a" == "a"` があり、最大容量を選ぶ生成処理をテストしていない。修正するなら、この空の確認を実際の生成結果と独立に定めた正解の照合へ置き換える。単純にテスト件数を増やさない。今回はデータ内容を変えるための作業ではない。

## 5. 再学習は条件固定で1回

名前の案：`W_v2_gradfix`。新しいデータ版や新しい学習目的のモデルと混同しない。

- 初期モデル：前回と同じ元B0。`W_v2` の続きから学習しない。
- 前回取得したモデルrevisionまたはローカルsnapshotを優先し、最新mainを再取得しない。
- 重み・tokenizer・configの識別子を記録する。前回のrevisionを確定できなければ、その差の不確実性を明記する。
- データ：`data/m3_3_v2/train.jsonl` と `dev.jsonl` を内容不変で再利用。既存manifestのハッシュを確認する。
- 600件、最大5 epochs、seed42、lr2e-5、weight_decay0.01、micro2、accum8、同じ候補シャッフルを維持。
- 学習のサンプル順と候補シャッフルの乱数消費順を不要に変えない。
- 通常の単一正解クロスエントロピーのみ。全パラメータ更新などの前回設定を維持。
- 新しくAMP等を足さず、実際に動いていた精度・依存関係を使う。
- チェックポイント選択は、今回に限り旧コードと同じ `(全ペア両問正解率, accuracy, -NLL)` を維持する。結果を見て切替ペア優先へ変えない。
- 新たにdevの同一正解ペア／異なる正解ペアの成績を記録してもよいが、今回は選択基準には使わない。
- 保存先例：`runs/m3_4_gradfix/trained/checkpoint/`。

600件・実効16件なら、1epochは37回の16件更新と1回の8件更新、計38 optimizer stepsが期待される。5epochsなら190回。スキップ等がなければこの数と整合することを記録する。

既存の学習CLIを再利用する。パッチ適用後の例：

```powershell
.venv\Scripts\python -m erabi.train --mode full `
  --model-id <前回と同一B0の識別子またはローカルsnapshot> `
  --data-dir data/m3_3_v2 `
  --output-dir runs/m3_4_gradfix/trained `
  --epochs 5 --lr 2e-5 --weight-decay 0.01 `
  --micro-batch-size 2 --gradient-accumulation-steps 8 --seed 42
```

手元のCLIの引数に合わせて確認する。角括弧のプレースホルダをそのまま実行しない。空きVRAMが足りない場合は他ジョブを止めず、制約を記録する。比較条件を変えなければ実行不能な場合、その変更は明示する。

## 6. 比較は既存データと保存予測を再利用

評価対象は `eval_v2.jsonl`、既存smoke12件、transfer_probe32件。B0 / W_fix / W_v2の保存予測が同じ入力・正解・後処理なら再利用し、新モデルだけ推論する。

最低限、以下を比較する。

| 対象 | 指標 |
|---|---|
| 全体 | 正解数/件数、NLL、Brier |
| 正解が異なる47組 | 両問正解、未切替失敗、切り替わるが不正解 |
| 正解が同じ53組 | 両問正解、不必要に予測を変えて失敗する組 |
| タスク別 | goal_following / composite_logic / boundary / comparison |
| smoke / transfer | 正解→誤答と誤答→正解のID、NLL/Brier |

主たる比較は `W_v2` と `W_v2_gradfix`。修正だけでどこが変わるかを見る。温度はT=1を維持。元の旧モデルの予測を正解表から書き換えない。

### 6.1 既存評価集合の制約を記録する

今回のZIPで、質問・本文・候補文（順序非依存）の完全一致はtrain/dev/eval間0件だった。

一方、明示ルールの「数値・条件が同じで文体だけ異なる」状態は残る。

- trainとeval：9組（composite_logic 8組、boundary 1組）。
- devとeval：2組（composite_logic 2組）。
- 合計11組22問。全てevalのnovel表現側。

これは完全一致入力0件という確認と矛盾しないが、厳密な新規シナリオ試験とは呼べない。今回の目的は**同一データ上での実装修正の比較**であるため、ここで生成器をまた作り直さない。

可能なら既存の構造キーから上記22問を除いた178問の補助集計も同時に出す。ただし、削除後も評価を既に見て開発している事実は変わらず、新しい未使用テストにはならない。

参考の保存予測再計算：残り178問はB0 74問、W_fix 88問、W_v2 102問正解。正解が異なる組は39組で、両問正解は順に2・10・7組。

### 6.2 結果の読み方

- 改善すれば、今回の固定条件の実験で修正後の成績がよかったと報告する。
- 改善しなくても、損失の平均として不正だった計算を戻して「高得点なので正しい」と扱わない。
- この1runではseed感度・全用途への汎化・因果効果の精密な大きさは確定しない。
- 残る失敗を「勾配修正だけで解決できない課題」として分離する。
- 結果を見て同じフェーズ内でペア損失、リサンプリング、学習率探索へ進まない。

## 7. なぜ今回はペア学習を追加しないか

普通のCEを使うなら、同じ重みでの2問の損失は `(CE1 + CE2)/2`。ペアで集めても、単なる平均の目的関数自体は同じである。バッチ編成による勾配のばらつき等は変わり得るが、「ペアごとCEにした」だけで新しい対照目的が生まれるわけではない。[R2]

また「指示が違えば必ず別の答えにする」という正則化は導入しない。現在のevalには、指示は異なるが正解は同じ53組がある。意味が保たれる指示変更では同じ候補を選べなければならない。

将来ペアを活用する場合も、同一正解／異なる正解を区別し、各問の正解を学ぶことを主目的にする。今回はその必要性・有効性の実験をまだ行わない。

## 8. 成果物と終了条件

既存の配置を優先し、最小限でよい。

```text
runs/m3_4_gradfix/
  notes.md
  config.json                    # 使用した条件・revision・ハッシュ
  gradient_check.json            # 修正前後と一括平均の小さな検証
  trained/train_summary.json
  trained/checkpoint/            # ローカルのみ。レビューZIPから除外
  comparisons/                  # 新モデル個票と既存比較の要約
  review_bundle.zip
```

README/STATUSには観測、原因の仮説、未実行項目を分けて残す。旧M3.3を消さず、「勾配蓄積の実装不具合があった版」と追記する。今回改善しなかった場合も、そのまま完了結果として報告する。

レビューZIPには最新の該当コード、必要なCPUテスト、使用データとハッシュ、元モデルrevision、学習条件、比較対象の個票、比較集計、notes/STATUSを含める。既に添付した旧成果物を参照する場合はパスとSHA256を残す。重み、optimizer state、.venv、HFキャッシュ、秘密情報は含めない。

校正の流用、APIのモデル自動切替、自動処理の有効化は行わない。

## 9. 参考と出所

[F1] 今回ユーザー提供の `review_bundle_followup.zip`。コード・データ・保存予測が根拠。GLiClassの実モデル再学習はレビュー環境で実行していない。

[F2] 同梱 `repro_accumulation.py` と `results/gradient_probe.json`。CPUの小モデルによるコード計算の再現であり、実モデルの性能評価ではない。

[R1] PyTorch公式 Automatic Mixed Precision examples / Gradient accumulation。等サイズミニバッチを固定の蓄積回数で割り、蓄積後にstepする基本例。ERABIでAMPを新規導入する指示ではない。
```text
https://docs.pytorch.org/docs/2.14/notes/amp_examples.html#gradient-accumulation
```

[R2] PyTorch公式 CrossEntropyLoss。単一正解のCEとmean reductionの定義。今回のサンプル数重み付け・ペア平均の説明の基礎。
```text
https://docs.pytorch.org/docs/2.14/generated/torch.nn.CrossEntropyLoss.html
```

外部資料確認日：2026-09-18。手元のPyTorchをドキュメントの版へ更新しない。今回の実験回数・データ据置・出力名はERABI向けの設計判断である。
