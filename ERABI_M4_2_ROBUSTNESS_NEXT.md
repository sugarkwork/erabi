# ERABI — M4.2: 未見の優先順位表現の検証と、転用退行の最小是正

作成日: 2026-09-19

## 0. 結論

M4.1 の改善は有望だが、次の学習を始める前に二点を切り分ける。

1. `eval_exception` 99.2% が、未見の「優先順位という能力」へ一般化しているか。
2. `transfer_probe` 25/32 → 20/32 の退行が、少量の汎用保持データで回復できるか。

今回は、既存の `transfer_probe` を学習データへ流用しない。
既に結果を何度も見ているため、開発用診断としてのみ使う。

M3基準版、M4.1実験版、既存校正artifactは上書きしない。

---

## 1. M4.1実物レビューで確認したこと

レビューZIP:
- 59 files
- ZIP SHA256:
  `67357d270fbd899ee899b54f39b994420abcdbc04c97ca7aee88c44557988cce`
- ZIP破損なし。

保存予測から、報告された主要指標は再現できる。

特に:
- `eval_exception`: 39/120 → 119/120
- `smoke_cases`: 9/12 → 12/12
- `eval_v2`: 195/200 → 194/200
- `transfer_probe`: 25/32 → 20/32

ただし、transferの個票では
- 維持正解 18
- 回復 2
- 新規退行 7
- 両モデル誤答 5

であり、「5問だけが入れ替わった」という意味ではない。
正解数の純減が5問で、実際には7問退行・2問回復している。

次回報告では純増減と個票遷移を分けて書く。

---

## 2. M4.1データ分布の報告値を訂正する

`build_m4_1_data.py` のコメント上は、
- dev: conflict 10 / nonconflict 10
- eval: conflict 30 / nonconflict 30

を意図している。

しかし、意味状態重複を避けるため候補をrejectしながら
グローバルな件数だけを満たす生成方法になっており、
実データでは比率が変化している。

実ファイル:
- train: conflict 60 / nonconflict 60
- dev: conflict 12 / nonconflict 8
- eval: conflict 37 / nonconflict 23

evalの正解が異なるペア37組 / 同一23組は、この実分布と一致する。

### 修正方針

M4.1のデータや既存結果を作り直さない。
結果は「実際の分布」で有効なので、報告の設計説明だけ訂正する。

今後の生成器では、先に `(domain, conflict/nonconflict)` ごとのquotaを固定し、
各stratum内で一意状態を生成する。

重複で候補をrejectした場合、
別stratumの件数で穴埋めしない。

quotaを満たせない場合は明示エラーで止める。

---

## 3. M4.1の99.2%が示している範囲

現在の `eval_exception` は、
trainと同じ5ドメイン、同じrule A/Bの文章、同じ質問フォーマット

```text
①【最優先】...
②【次点】...
優先順位に従って...
```

を使用している。

異なるのは主に数値、context template、状態組合せである。

したがって119/120は、

> 学習した優先順位スキーマについて、未使用状態へ高く適応できた

ことを支持する。

一方、

> 初めて見る優先順位表現・新ドメインでも99%解ける

ことはまだ測っていない。

M4.2では、ここを最初に測る。

---

# Phase A — 再学習前の Novel Priority Probe

## 4. 新しい評価だけを作る

`data/m4_2_robustness/novel_priority_eval.jsonl`

目安:
- 60 pairs / 120 cases

**学習には絶対に使わない。**

既存5ドメインをそのまま使わず、
少なくとも4つの新ドメインを使う。

例:
- 製造品質判定
- 予約・座席割当
- 電力制御
- 在庫・安全管理
- 医療ではない一般的な作業優先度
- ファイル処理・ジョブスケジューリング

高リスクな現実判断の正解データとしてではなく、
合成ルール判断問題として作る。

## 5. 優先順位の文章形式を変える

M4.1の固定表現をコピーしない。

例として複数familyを作る。

### family A
```text
通常はルールAに従う。
ただしルールBの条件が成立した場合はBを優先する。
```

### family B
```text
AとBが同時に成立する場合のみ、AよりBを優先する。
それ以外はAの判定を使う。
```

### family C
```text
優先度は B > A。
両方適用可能なら上位の規則を採用する。
```

### family D
```text
第一判断: A
例外条件: B
例外条件を満たした場合、第一判断を上書きする。
```

反対向き（A優先）も作り、
特定語「例外」が常に正解Bを意味するshortcutを作らない。

## 6. 状態構成

最低限:
- 両ルール成立し、優先順位によって正解が変わる
- 片方のみ成立し、優先順位を変えても正解が同じ
- どちらも成立せずfallbackへ行く

を含める。

候補数は既存中心の2～3択でよい。
4択以上は今回は増やさない。

## 7. 分割・正解

- M3/M4既存データとの exact input fingerprint 0。
- semantic stateは、新ドメインなので可能な範囲でcanonical化。
- generatorとは別の小さな正解検証関数で全件検証。
- group単位を維持。
- quotaを先に固定してから生成。

### Phase A評価

次の2モデルをT=1で評価:
- `W_v2_ce10`
- `W_m4_1`

保存:
- Accuracy
- pair both
- diff-target pair both
- same-target pair both
- NLL
- Brier
- 個票

### Phase A停止条件

`W_m4_1` の novel priority diff-target both が著しく低い
（設計上の目安: 60%未満）場合は、
「優先順位概念の転用不足」を主課題として報告し、
Phase Bの汎用保持データ混合へ自動で進まない。

その場合、次回は優先順位表現の多様化を先に設計する。

60%以上を目安に、少なくとも一定の転用が見られる場合のみPhase Bへ進む。
60%は実用品質保証ではなく、今回の実験分岐の目安。

---

# Phase B — 転用退行を抑える小規模保持学習

Phase Aを通過した場合のみ実施。

## 8. 既存transfer_probeを学習に使わない

既存:
`data/m3_1/transfer_probe.jsonl`

は何度も結果を見ているため、
今後も診断集合として固定する。

その文面、数値、candidate text、テンプレートをコピーして
学習データを作らない。

---

## 9. 新しい Robustness データ

作成:
- `robust_train.jsonl`: 160 cases
- `robust_dev.jsonl`: 40 cases
- `robust_fresh_eval.jsonl`: 80 cases

件数は実験予算であり必要量の主張ではない。

主に以下4系統を均等にする。

### R1. 否定されたゴール
文中に複数属性があるが、
「XではなくYを基準に」のように判断基準を明示する。

同じ単語があるだけで逆側を選べないよう、
両方向の対照例を入れる。

### R2. ルール方向の反転
同じ数値関係でも、
問題ごとに
- 小さい方を選ぶ
- 大きい方を選ぶ
- 閾値以上
- 閾値未満
などを切り替える。

特定の属性名とmin/maxを固定対応させない。

### R3. 論理関係 / 短いNLI
短い前提と主張から
- supports
- contradicts
- unknown

を選ぶ。

既存smokeの文章をコピーしない。
説明可能な合成文のみ使用する。

### R4. 表現・スケール転用
同じ論理を
- %
- 個数
- 秒
- 距離
- 容量
等へ写す。

数値スケールが変わっても比較方向を読む必要がある問題にする。

---

## 10. M4.2学習データ

M4.1の能力を維持するため、
新しいrobustデータだけで追加学習しない。

B0から改めて:

```text
M3 train                600
M4.1 exception train    240
M4.2 robust train       160
----------------------------
合計                   1000 cases
```

dev:
```text
M3 dev                  100
M4.1 exception dev       40
M4.2 robust dev          40
----------------------------
合計                    180 cases
```

通常CEのみ。
新しいloss、LoRA、EWC、contrastive lossは追加しない。

条件:
- base: `knowledgator/gliclass-instruct-base-v1.0`
- lr=2e-5
- wd=0.01
- micro=2
- accum=8
- seed=42
- max 10 epochs

checkpoint選択では、
単一の総合Accuracyだけで選ばない。

最低限、
- old M3 dev
- exception dev
- robustness dev

を別々に記録し、
どれか1領域が大幅に崩れたepochを
総合点だけでbestにしない。

ただし複雑な多目的optimizer/registryは作らない。

簡単な選択規則の例:
1. exception dev accuracy >= 95%
2. M3 dev accuracy >= 95%
3. 条件を満たすepochの中で robust dev accuracy 最大
4. tieなら NLL が低い方

これは今回の実験用規則であり一般最適解ではない。

---

## 11. 評価

比較モデル:
- `W_v2_ce10`
- `W_m4_1`
- 新しい `W_m4_2`

全て **T=1**。

新しい重みに既存T=3.1097を適用しない。

評価:
1. `novel_priority_eval`
2. `robust_fresh_eval`
3. `eval_exception`
4. `eval_v2`
5. `transfer_probe`
6. `smoke_cases`

特に次を表にする:
- Accuracy
- diff/same pair both
- NLL
- Brier
- W_m4_1 → W_m4_2 の回復/退行個票

`transfer_probe` は開発判断で既に見ているため、
最終的な「未知性能」とは呼ばない。

---

## 12. 成功の読み方

理想:
- exception能力をほぼ維持
- eval_v2をほぼ維持
- fresh robustnessで改善
- transfer_probeの退行が一部回復
- novel priorityで優先順位概念の転用が確認できる

ただし、例えば
`transfer_probe 25/32`へ戻ることだけを目標にしない。
既知32問へ最適化するのではなく、
fresh robustnessで改善していることを優先する。

M4.2でも悪化するなら、
データ量を無制限に増やさず停止して分析する。

---

## 13. M3.7.1契約修正について

M4.1と並行して実施した以下は、
M3基準版の保全修正として扱う。

- strict precision contract
- tokenizer必須hash
- dataset↔logits alignment digest

M4.2ではこの契約層を再設計しない。

M3の校正T=3.1097と基準APIを変更しない。

---

## 14. テスト方針

増やすのは今回壊れると困る責務だけ。

必要:
- quotaどおりのsplit構成
- train/dev/evalのinput重複0
- 手計算可能な数件のtarget検証
- B0からの学習設定が意図どおり
- 新checkpointへ旧calibrationを誤適用しない

不要:
- 文章テンプレートごとの大量unit test
- 全生成例のsnapshot
- カバレッジ目標
- 新しい実験管理基盤

---

## 15. Codex / Antigravityへの実行指示

```text
M4.1のreview_bundle.zipを実物レビューしました。

M4.1の改善自体は支持されますが、
eval_exceptionは学習と同じ5ドメイン・同じrule文・同じ優先順位表現なので、
119/120を「未知の優先順位表現への99%汎化」とは扱いません。

また実データは、
dev conflict/nonconflict = 12/8、
eval = 37/23 であり、
生成器コメント上の10/10・30/30とは一致していません。
重複rejectによってquotaが崩れたためです。
既存結果は作り直さず、報告を実分布へ訂正してください。

まずPhase Aとして、
未使用ドメイン・未使用の優先順位表現だけで
novel_priority_evalを新規作成し、
W_v2_ce10とW_m4_1をT=1で評価してください。
このデータは学習に使わないでください。

W_m4_1のdiff-target pair bothが60%未満なら、
そこで停止し、優先順位表現の転用不足を報告してください。

一定の転用が確認できた場合のみPhase Bへ進みます。

Phase Bでは既存transfer_probeを学習へ流用せず、
否定ゴール、方向反転、短いNLI、スケール転用からなる
独立したrobust train/dev/fresh_evalを作ってください。

B0から、
M3 train 600 + M4.1 exception 240 + robust 160
を通常CEのみで一回学習してください。
新しいlossやモデル構造は追加しません。

新モデルはT=1で、
novel_priority_eval、robust_fresh_eval、eval_exception、
eval_v2、transfer_probe、smokeを比較してください。

transfer_probeは既知診断なので、そこだけに最適化しないでください。
fresh robustnessの改善と旧能力保持を優先してください。

M3/M4.1のモデル・校正・APIは上書きしません。
既存コードを再利用し、テストや抽象化を増やし過ぎないでください。
結果が悪ければそのまま停止・記録してください。
```
