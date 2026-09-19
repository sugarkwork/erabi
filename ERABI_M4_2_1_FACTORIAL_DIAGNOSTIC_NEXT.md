# ERABI — M4.2.1: 優先順位失敗の要因分離（Domain × Phrasing 2×2 診断）

作成日: 2026-09-19

## 0. 結論

M4.2 Phase A は設計どおり停止してよい。

ただし、`novel_priority_eval` は
- 未学習ドメイン
- 未学習の優先順位表現

を同時に変更している。

したがって、15%という低成績だけから
「M4.1は固定構文に過適合した」
と断定しない。

可能性は少なくとも次の4つある。

1. 優先順位の表現変更に弱い。
2. 新ドメイン語彙に弱い。
3. 両方が同時に変わったときだけ弱い。
4. そもそもM4.1で学んだpriority schemaが限定的。

次の再学習前に、これを小さな2×2評価で分離する。

---

# 1. 今回は再学習しない

固定するもの:
- Baseline: `W_v2_ce10`
- Experiment: `W_m4_1`
- 温度: T=1.0
- M3/M4.1の既存モデル・校正・API
- 既存 `novel_priority_eval`

今回は行わない:
- 新しい学習
- Family A〜Dの混合学習
- transfer robustness学習
- 新loss
- モデル交換
- 校正
- API変更

目的は原因分離だけ。

---

# 2. 2×2診断

二つの軸を分ける。

## Axis A: Domain
- OLD DOMAIN: M4.1学習時に使った5ドメイン
- NEW DOMAIN: M4.2 Phase Aで使った未学習4ドメイン

## Axis B: Priority Phrasing
- OLD PHRASING: M4.1固定表現 `①【最優先】... ②【次点】...`
- NEW PHRASING: M4.2のFamily A〜D

この組合せで4セルを作る。

| Cell | Domain | Phrasing | 目的 |
|---|---|---|---|
| A | OLD | OLD | 既知条件のcontrol |
| B | OLD | NEW | 表現変更だけの影響 |
| C | NEW | OLD | ドメイン変更だけの影響 |
| D | NEW | NEW | 既存Phase A。複合変化 |

Cell D は既存 `novel_priority_eval` を再利用してよい。
A/B/Cだけ新規作成する。

---

# 3. 問題数

各セル:
- 20 pairs / 40 cases を目安

合計:
- 新規 A/B/C = 60 pairs / 120 cases
- 既存 D = 60 pairs / 120 cases

比較しやすいよう、各セルで conflict / nonconflict / fallback の比率を揃える。

推奨:
- conflict: 12 pairs
- single/nonconflict: 5 pairs
- fallback: 3 pairs

この比率は実験用。必要量の主張ではない。

---

# 4. 内容を対応させる

可能なら同じ論理状態をA/B/C/Dへ写像して比較できるようにする。

例:
- A: ゲームドメイン + 旧phrasing
- B: ゲームドメイン + 新phrasing
- C: 製造ドメイン + 旧phrasing
- D: 製造ドメイン + 新phrasing

完全に同一文章にする必要はないが、ルール構造・conflict/same/fallback区分・候補数を揃える。

---

# 5. Shortcutを作らない

次を避ける。

- 「例外」という単語が出たら常にchoice B。
- Family Cなら常に二番目のruleを選ぶ。
- 新ドメイン固有語だけで答えが決まる。
- conflictだけで正解candidateが固定。
- A/Bの順序と正解IDが固定。

各familyでA優先・B優先を両方作る。

同じcontextでもpriorityだけ変えたpairを含める。

---

# 6. 分離と品質

- 既存train/dev/evalとのexact input重複0。
- 新規A/B/C相互のexact input重複0。
- group単位で管理。
- generatorとは別の小さな正解検証関数で全件検証。
- quotaを先に固定し、rejectで他stratumに穴埋めしない。
- quotaを満たせなければエラー停止。

大量のsnapshotテストは不要。

---

# 7. 評価

T=1で以下2モデル:
- `W_v2_ce10`
- `W_m4_1`

各セルごとに:
- Accuracy
- Pair Both Correct
- Diff-Target Pair Both
- Same-Target Pair Both
- NLL
- Brier
- 未切替率
- 切替えたが誤答した率

特に `W_m4_1` のB/C/Dを比較する。

---

# 8. 結果の読み方

## Pattern 1: Bだけ大きく低下、Cは高い
意味:
- ドメインよりpriority phrasing変更が主因。

次:
- Family A〜D等のphrasing多様化学習へ進む。

## Pattern 2: Cだけ大きく低下、Bは高い
意味:
- priority conceptより新ドメイン語彙・状態表現が主因。

次:
- domain/content diversificationを優先。
- priority phrasing学習だけでは不足。

## Pattern 3: BもCも低い
意味:
- 両方に独立した弱さ。

次:
- 一度に大量混合せず、phrasing diversification + domain diversificationを小さく均衡させる設計。

## Pattern 4: BとCは高いがDだけ低い
意味:
- 二つのshiftが同時に起きると性能が崩れるinteraction。

次:
- cross-combination trainingを検討。

## Pattern 5: Aすら低い
意味:
- M4.1既知スキーマの再現条件がおかしいか、新しいgenerator/evaluationに問題がある可能性。

次:
- 再学習せず、入力・ラベル・評価を監査。

---

# 9. 次の学習へ進む条件

今回の2×2結果が出るまでは学習しない。

結果に応じて次のM4.3を一つ選ぶ。

### M4.3-P
Priority phrasing diversification

### M4.3-D
Domain/content diversification

### M4.3-X
Cross-shift diversification

複数を同時実装しない。

---

# 10. transfer_probeについて

既存 `transfer_probe` は今回も学習に使わない。

M4.1で
- 7問退行
- 2問回復
- 純減5問

という個票遷移があるため、次回報告は「-5問」だけでなく回復/退行の両方を記録する。

2×2診断の後、必要なら独立robustnessデータを作る。

---

# 11. テスト方針

追加は小さく。

必要:
- 4セルのquota
- conflict/same/fallback比率
- A/B priority方向が両方存在
- split/input重複0
- 数件の独立正解検証

不要:
- 全テンプレートsnapshot
- カバレッジ目標
- 新実験管理基盤
- 新しい汎用データDSL

---

# 12. Codex / Antigravityへの指示

```text
M4.2 Phase Aの15%という結果は有用ですが、
novel_priority_evalでは「新ドメイン」と「新priority phrasing」を同時に変更しています。

そのため、固定構文への過適合だけが原因と断定せず、
再学習前にDomain × Phrasingの2×2診断を行ってください。

今回は再学習しません。

4セル:
A = old domain + old phrasing
B = old domain + new phrasing
C = new domain + old phrasing
D = new domain + new phrasing（既存Phase Aを再利用）

A/B/Cを小規模新規生成し、
W_v2_ce10 と W_m4_1 を T=1 で比較してください。

各セルで
Accuracy、
Pair Both、
Diff/Same pair both、
NLL、
Brier、
未切替率
を出してください。

quotaを事前固定し、
rejectによるstratum比率崩れを起こさないでください。
generatorとは別の正解検証を行ってください。

結果に応じて、
phrasingが主因ならM4.3-P、
domainが主因ならM4.3-D、
同時shiftだけが問題ならM4.3-X
の一つだけを次の提案にしてください。

既存transfer_probeは学習に使わないでください。
M3/M4.1モデル・校正・APIは上書きしません。
テストや抽象化を増やし過ぎないでください。

計画だけで止めず、
この2×2評価と結果保存まで進めてください。
```
