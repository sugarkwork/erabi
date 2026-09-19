# ERABI — M4.3-P: Priority Phrasing Diversification

作成日: 2026-09-19

## 0. 今回の判断

M4.2.1 の2×2診断は、優先順位表現の変更が主要な弱点であることを強く示した。

ただし、結論は次の範囲に限定する。

- Cell B（旧ドメイン + 新表現）: W_m4_1 Diff Both = 0/12
- Cell C（新ドメイン + 旧表現）: W_m4_1 Diff Both = 9/12
- Cell D（新ドメイン + 新表現）: W_m4_1 Diff Both = 2/12
- Cell A（旧ドメイン + 旧表現）も 6/12 に留まるため、
  「表現変更だけが唯一の原因」とまでは断定しない。

次の一手は M4.3-P（Priority Phrasing Diversification）とする。

今回は、既存の Family A〜D をそのまま学習して
同じ Family A〜D で評価する方式にはしない。

**別の表現群で学習し、さらに別の未見表現群で評価する。**

---

## 1. 保全するもの

上書き禁止:

- M3 baseline: `W_v2_ce10`
- M3.7 / M3.7.1 calibration artifacts
- M4.1: `W_m4_1`
- M4.2 Phase A `novel_priority_eval`
- M4.2.1 2×2 diagnostic datasets/results
- existing `transfer_probe`

新しい重みに既存 T=3.1097 を流用しない。

M4.3-P の全比較は T=1。

---

## 2. 今回は変更しないもの

- モデル構造
- 損失関数
- GLiClass backend
- 学習率
- optimizer
- gradient accumulation
- API
- calibration runtime
- NLI専用学習
- transfer_probeの学習利用
- ModernBERT
- LoRA / EWC / contrastive loss

通常CEのまま、**データの表現多様性だけ**を変更する。

---

## 3. データの考え方

狙いは、

> 「①【最優先】...②【次点】...」という字面ではなく、
> “競合した規則のどちらを優先するか” を読む

能力を増やすこと。

そのため、priority rule の意味は同じでも表面表現を変える。

また、特定のキーワードと正解candidateが固定対応しないようにする。

---

## 4. 既存Family A〜Dは学習に使わない

M4.2 Phase A / M4.2.1で既に評価に使用した:

- Family A: 通常はA、ただしBならB
- Family B: 同時成立時のみAよりB
- Family C: 優先度 B > A
- Family D: 第一判断A、例外Bで上書き

は **historical diagnostic** として固定する。

M4.3-Pのtrain/devには入れない。

M4.3-P後に、A〜Dで改善するかを追加診断として再評価してよい。
ただし最終fresh性能とは呼ばない。

---

## 5. Training Phrasing Families（E〜J）

6 familyを用意する。各familyで A優先 / B優先 の両方向を必ず含める。

### Family E — 原則 / 優先規則
```text
原則として規則Aを使う。
ただし規則Bが成立する場合は、BをAより優先する。
```
反転版も作る。

### Family F — 競合時の採用規則
```text
AとBの判定が競合した場合はBを採用する。
一方だけ成立する場合は、その成立した規則に従う。
```
反転版も作る。

### Family G — 上位 / 下位規則
```text
規則Bを上位規則、規則Aを下位規則とする。
両方成立した場合は上位規則を採用する。
```
反転版も作る。

### Family H — override
```text
通常の判定はAで行う。
Bの条件が成立した場合だけ、Aの結果をBで上書きする。
```
反転版も作る。

### Family I — 優先番号
```text
優先順位:
1位: B
2位: A
成立している規則のうち、順位が最も高いものを使う。
```
反転版も作る。

### Family J — if both
```text
AとBの両方が成立したときはBを選ぶ。
片方だけ成立した場合は成立側を選ぶ。
どちらも成立しなければ通常状態を選ぶ。
```
反転版も作る。

### 注意

「例外」という単語が出ればB、
「1位」と書かれた次の候補が正解、
というshortcutを作らない。

- A優先 / B優先を均衡
- ruleの記述順もランダム化
- candidate順も既存方式でランダム化
- conflict/single/fallbackを均衡
- 各candidate IDとpriority方向を固定対応させない

---

## 6. Dev Phrasing Families（K〜L）

train E〜Jとは違う表現を使う。

### Family K — 優先方針
```text
判断方針として、AよりBを優先する。
競合しなければ成立している条件をそのまま採用する。
```

### Family L — precedence
```text
BはAに先行して評価される。
Bが成立した場合はBの結果を用い、
成立しない場合にAを評価する。
```

A優先版も作る。

checkpoint選択に使用するため、K/Lは最終fresh評価には使わない。

---

## 7. Fresh Evaluation Families（M〜P）

モデル選択には使用しない。学習・devと完全に分離する。

### Family M
```text
両規則が該当するケースではB側の判断を採る。
それ以外は該当した規則の判断を採る。
```

### Family N
```text
判定が重なった場合の決定権はBにある。
```

### Family O
```text
Aを基本判定とするが、
Bの成立時にはBの結論を最終結果とする。
```

### Family P
```text
競合解決順はB、Aの順。
最初に成立した規則の結果を採用する。
```

全familyで反転版も作る。

---

## 8. Domain構成

M4.2.1で新ドメイン自体は主因ではない傾向が出たが、
phrasingとdomainの結び付きを避けるため、trainには旧・新を混ぜる。

使用例:
- 旧ドメインから4種
- M4.2新ドメインから4種

合計8ドメイン程度。

特定familyを特定domain専用にしない。
各familyが複数domainへ出現するようにする。

高リスクな現実判断ではなく、あくまで合成規則問題として作る。

---

## 9. 件数

### 新規 phrasing train
- 120 pairs / 240 cases
- conflict/diff-target: 60 pairs
- single/nonconflict: 36 pairs
- fallback: 24 pairs

6 train familiesでできるだけ均等。

### 新規 phrasing dev
- 40 pairs / 80 cases
- diff-target: 20
- single/nonconflict: 12
- fallback: 8

### 新規 fresh phrasing eval
- 60 pairs / 120 cases
- diff-target: 30
- single/nonconflict: 18
- fallback: 12

件数は実験予算であり、必要量の主張ではない。

---

## 10. quotaを先に固定

M4.1で起きた「重複rejectでstratum比率が崩れる」問題を再発させない。

生成前に
`family × domain-class × state-kind × priority-direction`
のquotaを決める。

候補が既存semantic stateと重複した場合:
- 同じstratum内で再生成
- 別stratumの件数で穴埋めしない

規定回数でquotaを満たせない場合:
- 明示エラー
- 生成を止める

---

## 11. 分離・品質

必須:

- 新train/dev/fresh_eval相互のexact input重複 0
- 過去M3/M4全データとのexact input重複 0
- group単位管理
- semantic stateの重複を可能な範囲で0
- generatorとは別のverification関数で全target検証
- family / domain / state / priority direction の件数をmanifest保存

モデル出力を見てデータを削除・修正しない。

---

## 12. 学習構成

B0から改めて一回学習する。

train:
```text
M3 base train              600
M4.1 exception train       240
M4.3-P phrasing train      240
--------------------------------
Total                     1080
```

dev:
```text
M3 base dev                100
M4.1 exception dev          40
M4.3-P phrasing dev         80
--------------------------------
Total                      220
```

通常CEのみ。

設定:
- base: `knowledgator/gliclass-instruct-base-v1.0`
- lr = 2e-5
- weight_decay = 0.01
- micro_batch = 2
- grad_accum = 8
- seed = 42
- max epochs = 10

M4.1 checkpointから継ぎ足し学習しない。
B0から全データを一回で学習する。

---

## 13. checkpoint選択

総合accuracyだけで選ばない。

各epochで少なくとも:
- M3 dev accuracy
- M4.1 exception dev accuracy
- M4.3-P phrasing dev accuracy
- phrasing dev diff-target pair both
- 各NLL

を記録する。

簡単な選択規則:

1. M3 dev accuracy >= 95%
2. M4.1 exception dev accuracy >= 95%
3. 条件を満たすepochの中で M4.3-P phrasing dev diff-target pair both 最大
4. tieなら phrasing dev NLL が低い方

該当epochがない場合:
- bestを無理に昇格しない
- 結果を失敗として記録

複雑な多目的最適化基盤は作らない。

---

## 14. 評価

T=1。

比較:
- `W_v2_ce10`
- `W_m4_1`
- 新 `W_m4_3p`

評価セット:

1. **fresh_phrasing_eval (M〜P)** — 最重要
2. M4.2 historical novel_priority_eval (A〜D)
3. M4.2.1 Cell B（old domain + new phrasing）
4. M4.2.1 Cell C（new domain + old phrasing）
5. M4.1 eval_exception
6. M3 eval_v2
7. transfer_probe
8. smoke_cases

各セット:
- Accuracy
- Pair Both
- Diff-Target Both
- Same-Target Both
- NLL
- Brier
- 未切替率
- 個票の回復 / 退行

---

## 15. 成功の目安

これは実用品質保証ではなく、今回の実験判断目安。

### 最優先
fresh_phrasing_eval:
- Diff-Target Both >= 60%
- W_m4_1より明確に改善

### 旧能力保持
- eval_exception: M4.1から -3pt以内を目安
- eval_v2: W_v2_ce10 / M4.1から -3pt以内を目安
- smoke: 10/12以上を目安

transfer_probeは既知診断なので、スコアだけを目的関数にしない。

改善しなくてもデータ増量やloss追加へ自動で進まない。

---

## 16. 校正

M4.3-Pでは校正しない。

全比較T=1。

新重みに既存M3 T=3.1097を絶対に適用しない。

M4.3-Pを採用する場合のみ、別フェーズで独立calibrationを作る。

---

## 17. テスト方針

追加するのは重要な責務だけ。

必要:
- quotaの固定
- familyのsplit分離
- A/B priority方向の両方が存在
- train/dev/fresh exact overlap 0
- 過去データとのinput overlap 0
- 数件の独立target検証
- B0から指定条件で学習開始

不要:
- 全文章snapshot
- familyごとの大量unit test
- 新DSL
- registry
- カバレッジ目標

---

## 18. 終了条件

今回の完了は:

1. データ生成・監査
2. baseline 2モデルをfresh_phrasing_evalで事前評価
3. 条件を満たせばB0から一回学習
4. 3モデル比較
5. 回復・退行記録
6. review_bundle作成

まで。

結果が悪ければ、そのまま終了する。

---

## 19. Codex / Antigravityへの実行指示

```text
M4.2.1の2×2診断により、
新domainよりpriority phrasing変更の影響が大きいことが確認できました。

次は ERABI M4.3-P Priority Phrasing Diversification を実施してください。

重要:
M4.2で評価済みのFamily A〜Dをそのまま学習し、
A〜Dで改善しただけを成功とはしません。

trainは別表現Family E〜J、
devはK〜L、
fresh evaluationはM〜Pとして、
表現familyを完全に分離してください。

旧・新domainをtrainに混ぜ、
familyとdomainが固定対応しないようにしてください。
A優先/B優先、conflict/single/fallbackを事前quotaで均衡させ、
reject時に別stratumで穴埋めしないでください。

データ整合性を確認後、
B0から
M3 train 600 + M4.1 exception 240 + phrasing train 240
を通常CEのみで最大10epoch、一回学習してください。

checkpointは、
M3 dev >=95%、
M4.1 exception dev >=95%
を満たすepochの中で、
phrasing dev Diff-Target Both最大を選んでください。

新モデルはT=1で、
fresh_phrasing_evalを最重要として、
historical A〜D、Cell B/C、eval_exception、eval_v2、
transfer_probe、smokeを比較してください。

既存M3/M4.1モデル・校正・APIは上書きしません。
新重みにT=3.1097を流用しません。

新loss、モデル構造変更、NLI専用混合、
transfer_probeの学習利用、API変更は行いません。

テストや抽象化を増やし過ぎず、
計画だけで止めず、実行・比較・保存まで進めてください。
```
