# ERABI — M3.5：通常CEの学習予算を5→10エポックへ広げる、一回の比較

作成日：2026-09-18  
対象：既存 erabi-local を実装している Codex / Antigravity  
前提：M3.4のZIP・保存予測・学習ループをレビュー済み。設計者はモデル重みを受領しておらず、実モデルの学習は再現していない。

## 0. 今回の決定

**勾配蓄積の修正は成立している。今回は新しい損失を追加せず、通常のクロスエントロピー（CE）で、最大10エポックの学習を一回だけ行う。**

目的は「5エポックという初期上限が、指示切替を学ぶには短かった可能性」を検証すること。改善を保証せず、10エポックも最適値や必要最低量とは呼ばない。

元モデルB0・既存データ・損失・行シャッフル・候補シャッフル・実効バッチ・学習率・checkpoint選択基準は維持する。変える学習条件は最大エポック数だけ。観測用のtrain/dev集計と5エポック時点のcheckpoint保全を小さく追加する。

既存AGENTS.md、STATUS.md、設計書を読む。ただし過去文書の将来機能を一括実装しない。計画だけで止めず、この範囲の実装・実行・記録まで行う。ツール側の必須承認は迂回しない。

## 1. 根拠と、まだ分からないこと

### 1.1 M3.4で確認できた改善

保存予測を再計算した結果は次の通り。

| 指標 | W_v2 | W_v2_gradfix |
|---|---:|---:|
| eval_v2 正解数 | 117/200 | 162/200 |
| NLL | 0.8224 | 0.4761 |
| Brier | 0.5187 | 0.2755 |
| 正解が異なるペアの両問正解 | 8/47 | 12/47 |
| 正解が同じペアの両問正解 | 28/53 | 52/53 |
| transfer_probe | 20/32 | 25/32 |
| smoke | 9/12 | 8/12 |

W_v2_gradfixの200問を分けると、goal_followingは69/100、explicit_ruleは93/100。正解が異なるgoal_followingペアは3/31で、選ぶ属性の切替は残る課題。smoke-11は今回退行しており、能力保持全般を証明したとは書かない。

### 1.2 学習終了時点で、まだ改善している

M3.4のdev履歴は、epoch 3で58%/ペア44%、epoch 4で75%/54%、epoch 5で80%/62%。dev NLLは0.7064→0.6438→0.3778。5は最初に決めた上限であり、収束を実測して決めた上限ではない。

ただし、これだけで学習不足とも断定しない。学習集合の指示切替成績が未記録なので、学習集合でも未習得なのか、学習集合では解けるが別状況へ転用できないのかは未確定。今回、両者を測る。

### 1.3 対照学習は今回はしない

通常CEは各質問にそれぞれ正しいラベルを与える目的関数である。独立サンプルCEだから原理的に指示追従できない、という結論は今回の結果から出ない。

同一ペアのCEを単に平均するだけなら、目的関数は元の平均CEと同じ。ペアを同じ更新に含めることはバッチ構成の実験であり、独自の対照損失とは区別する。また指示が違っても正解が同じ組があるため、一律に分布を離すことを正解条件にしない。

## 2. 固定するもの・行わないもの

### 固定

- 元ベース：M3.4と同じ knowledgator/gliclass-instruct-base-v1.0 の取得済み重み。
- train：data/m3_3_v2/train.jsonl、600件 / 300 groups。
- dev：data/m3_3_v2/dev.jsonl、100件 / 50 groups。
- 学習率2e-5、AdamW、weight_decay=0.01、micro_batch=2、accum=8、seed=42、max_norm=1.0。
- 行単位のシャッフルと候補順シャッフル。今のrngの使い方を変えない。
- hard-label平均CE、今回修正された実件数による勾配蓄積、入力整形、precision、512トークンの既存条件。
- checkpoint選択順：全ペア両問正解率、全体正答率、NLLの順（現コードの辞書式順序を維持）。

train SHA256：`9cb6545fc3f3a982ce22942a66b97984f2c8e4bd328bcfb96acc1a860db0a7d9`  
dev SHA256：`623729415d6b00f3589f7aa4659adbb86aecb012d1073a2f608e64f9729dfce3`  
eval_v2 SHA256：`e528ee7acc26c06a2a6db8c297e0b92c8fe25835235aeaf90bc121127266b9bc`

### 変更

- 最大エポック数：5→10。600件なら38更新/epoch、最大380 optimizer updates。
- 学習能力の観測を追加する。観測値でサンプル配分・損失・学習率を変えない。

### 禁止

ペア専用loss、contrastive正則化、ペアbatchへの変更、重み付け・oversampling、データ生成・ラベル変更・タスク追加、モデル交換、LoRA、蒸留、強化学習、校正再推定、API変更、UI、DB、分散処理、ハイパーパラメータ探索、有料APIを今回は行わない。

途中でeval_v2の正答率を見ながらエポック数・checkpoint選択基準を変えない。結果が良くなくても10から20へ無断延長しない。

## 3. 既存成果物の保護と出発点

新しいrunの例：`runs/m3_5_ce10/`。旧W_v2/W_v2_gradfixやデータは上書きしない。

M3.4のZIPにはoptimizer stateが含まれておらず、手元で保存されているかも未確認。そのため今回は、**W_v2_gradfixの重みだけをロードしてAdamWを新規初期化する「続き学習」ではなく、B0から10エポックの一回の学習**を基本とする。旧5エポックと同じ学習の続きだと称してoptimizer状態を失わない。

取得済みのB0のローカルsnapshot/revisionと重みhashを記録する。最新重み・ライブラリへの自動更新をしない。過去に使ったrevisionが記録から復元できない場合は、今回の実ファイルを固定し、その限界を記録する。「条件完全固定」を無根拠に主張しない。

GPUの空きを確認する際、torch.cuda.memory_allocated()はそのプロセスの割当量であってGPU全体の空きではない。既存の運用手順で確認し、他のジョブを停止しない。グローバルPython環境を変更しない。

## 4. 観測の最小追加

### 4.1 まず現在のW_v2_gradfixをtrain/devで測る

固定候補順・model.eval()・勾配無効化で、現在の保存checkpointをtrain600件・dev100件に対し一回ずつ評価し、以下を保存する。train評価に含まれるtargetやgroupは採点にのみ使い、モデル入力へは入れない。

- 全体の正解数/件数、NLL、Brier。
- task_family別、explicit_ruleのrule_kind別。
- 正解が異なるペア/同じペアそれぞれの両問正解数。
- 正解が異なるgoal_followingペアの両問正解数。
- 各ペアの予測一致/不一致。top-1が同じでも確率は変わり得るため「指示が入力されていない」と断定しない。

既存比較スクリプトのgroup集計を再利用する。全タスクへ対応する評価フレームワークを新設しない。

### 4.2 新しいrunのdev履歴

各epochの現在のdev評価に、上記のペア内訳を追加する。推論を二重に行わず、その評価で得た予測から集計する。

**新しい内訳は診断用。checkpoint選択の目的を今回同時に変更しない。** 一方、最終判断では全体点だけでなく切替指標の変化を重視する。

学習時lossのエポック平均と、固定済みcheckpointのtrain評価NLLは別物。前者はepoch途中の異なる重み・trainモード、後者は固定重み・evalモードなので、無条件に学習/汎化ギャップとして差し引かない。

### 4.3 同じrun内で5エポック予算と10エポック予算を比較

epoch5終了時に、その時点までの既存選択基準でのbest checkpointを別名で保存する。

- `checkpoint_best_first5/`：今回のrunの最初の5epochから選んだbest。
- `checkpoint/`：同じrunの最大10epochから選んだbest。

epoch5の重みが必ずfirst5のbestになるとは仮定せず、選ばれたepochを明記する。原則この2個だけ保存し、全epochの重みやモデルregistryは作らない。保存済みbestをコピーする程度でよい。

最初の5epochと旧M3.4の履歴が大きく違う場合は、入力hash、B0、seed、dtype、依存版、シャッフル、診断追加によるモード/RNG変化を確認する。小さな非決定性と大きな条件変更を区別する。都合のよいseedを探さず、未解決の差は報告する。

## 5. 学習・評価を実行する

既存のCLIに観測用の小変更を行うだけでよい。コマンドの基本形は次の通り。B0をローカルsnapshotのパスで固定できる場合は、その値をmodel-idへ指定する。

```powershell
.venv\Scripts\python.exe -m erabi.train `
  --mode full `
  --model-id knowledgator/gliclass-instruct-base-v1.0 `
  --data-dir data/m3_3_v2 `
  --output-dir runs/m3_5_ce10/trained `
  --epochs 10 --lr 2e-5 --weight-decay 0.01 `
  --micro-batch-size 2 --gradient-accumulation-steps 8 --seed 42
```

これは既存CLIの基本形であって、未実装のcheckpoint保全や追加観測が自動で付くという意味ではない。必要な最小改修を先に行う。

学習中は従来どおりdevのみで選択する。eval_v2・smoke・transferを毎epoch推論しない。学習が終了した後、次を比較する。

1. 保存済みW_v2_gradfixの既存予測。
2. 今回の `checkpoint_best_first5`。
3. 今回の最大10epochで選択された `checkpoint`（仮称W_v2_ce10）。

同じ `eval_v2.jsonl`、`smoke_cases.jsonl`、`transfer_probe.jsonl`、未校正T=1を使う。今回の二checkpointが完全に同じ重みなら、推論を重複実行せずhash一致を記録して再利用してよい。

さらに今回の2checkpointをtrain/devでも固定重みで評価する。4.1と重複する同一モデル・同一データの推論は省いてよい。モデルをGPUへ同時常駐させない。

## 6. 何を比較して、どう結論を出すか

主たる診断は、**正解が異なるペアの両問正解数、特にgoal_followingでの両問正解数**。同じ正解の組を意図せず切り替えさせていないかも併記する。

| 観測 | 解釈する範囲 |
|---|---|
| trainの切替も低く、10epochでも低い | このデータ・条件・予算では習得不足が残る。CEでは不可能とは言わない |
| trainは切替でき、dev/evalでは難しい | 今回の汎化に課題。単なる更新回数不足だけでは説明しにくい |
| train/dev/evalの切替が改善 | 5epoch上限が制約だった可能性を支持。汎用能力の完成とは言わない |
| 全体点だけ伸び、異なる正解の組は伸びない | 中心課題は未解決。81%を超えたことだけで採用しない |
| NLLだけ改善し、top-1切替は変わらない | 確率側の変化と判断の変化を区別する |
| bestが5epoch以内のまま、後半が悪化 | 追加予算の利点を今回確認できなかった。元モデルを保持する |

smoke12件・transfer32件の正解→誤答も保存する。smoke-11に正解した一回を安全性保証と呼ばず、不正解の退行も隠さない。

eval_v2は過去の設計判断に繰り返し利用済みであり、11group22問はtrain/devと数値・条件構造を共有する。今回の同条件比較には使えるが、独立な最終評価や実利用精度の保証とは呼ばない。既存の178問の補助集計も再利用するが、新しい除外規則を成績に合わせて作らない。

一回のseedで改善しても普遍的な優越性とはしない。今回は追加seedでの再学習を実行しない。結果を見た後に別の損失やpaired batchを続けて試すのではなく、本範囲で終了する。

## 7. テスト・実装を増やしすぎない

M3.4の本番run_full_trainingとcompute_batch_lossは、設計者側の小さなCPU診断で、一括平均との一致を確認済み。修正をやり直すフェーズではない。

ただし、同梱の `verify_gradient_accumulation.py` とpytestは、学習式をテスト側で再実装している。productionの将来の変更を検知する力は限定的。今回それを直すなら既存の一件を実処理へ結び付ける差し替えにとどめる。新しい大きなmock基盤は作らない。

新たな最低限の確認は、観測後にtrainモードへ戻ること、checkpoint_first5を上書きしないこと、選択にeval_v2を使わないこと。既存の保存/推論処理を再利用する。テスト件数・網羅率を目標にしない。

エポック追加のためだけにcallbackシステム、プラグイン、トレーナー全面刷新、Lightning等への移行をしない。

## 8. 成果物・完了条件

- 使ったB0の識別情報、実データhash、依存版、dtype、seed、学習条件を保存。
- epochごとのtrain loss、dev各指標、best選択履歴。
- first5とbest10の選択epoch・重みhash、同じrun内の比較。
- 現W_v2_gradfixと新しい2checkpointのtrain/dev診断、評価用3集合の個票と集計。
- 指示切替の両問正解、同じ正解の維持、smoke/transferの退行。
- 実行できなかった項目と、報告・実測・仮説の区別。

改善しなかった結果も完成した実験として報告する。APIの採用checkpointを自動で変更せず、旧モデル・旧結果を保持し、全件review/T=1を維持する。

レビューZIPには上記の小さなJSON/JSONL/MD、関連コード、比較に使った保存予測、最新STATUSを含める。モデル重み、optimizer state、.venv、秘密情報は含めない。過去の比較予測を使うスクリプトなら、その予測も含めるか既存ZIPとの依存を明記する。学習GPUや環境を再現したと称するだけの空のmanifestを作らない。

## 9. 参照

一次資料：ユーザー添付M3.4報告、review_bundle(2).zip内のsrc/erabi/train.py、runs/m3_4_gradfix/trained/train_summary.json、個票予測。レビュー再計算結果は同梱のERABI_M3_4_REVIEW.mdとevidenceを参照。

外部の技術背景：PyTorch CrossEntropyLoss（logits、正解index、mean reduction）。外部資料がERABIにおける10epochの有効性を示したわけではない。
```text
https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html
```

10epoch・一回・上記成果物範囲は、ERABIの現在の実験履歴に基づく設計判断である。
