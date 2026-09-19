# ERABI — M4.4.1: Corrected Retention Selector

作成日: 2026-09-19

## 0. 目的

M4.4-RでR1 Retention selectorが
`rule_kind == "boundary"` に限定されていたため、
eval_v2退行と直接対応する
`rule_kind == "comparison"` の在庫=受注 equalityケースを
replayできていなかった。

今回は **selector coverageだけを修正**する。

新しい合成データは作らない。
replay量の大幅増加もしない。
HP R2の重みも変更しない。

---

## 1. 固定するもの

M4.4と同一:

- B0
- standard CE
- lr=2e-5
- wd=0.01
- micro=2
- accum=8
- seed=42
- max epochs=10
- M3 train 600
- M4.1 train 240
- M4.3.1 phrasing train 240
- R1 boundary replay 48
- R2 composite replay 56
- dev 220
- checkpoint selection規則
- T=1 evaluation

変更しない:

- Family K〜P学習利用
- transfer_probe学習
- eval_v2学習
- smoke学習
- new loss
- architecture
- calibration
- API

---

## 2. 新しく追加するR1b

対象:
`data/m3_3_v2/train.jsonl`

`rule_kind == "comparison"` で、

```text
inventory == demand
```

となるgroupを抽出する。

レビューで確認済み候補:

- train-er-0031
- train-er-0151
- train-er-0199
- train-er-0283

4 groups / 8 cases。

c1/c2両方をgroup単位でreplayする。

### 意味

c1:
`在庫 >= 受注`
→ equalityでは ship

c2:
`在庫 > 受注`
→ equalityでは delay

---

## 3. 抽出を文字列ID固定にしない

上記IDは監査用。

実装ではcontextから在庫数・受注数をparseし、

```python
rule_kind == "comparison"
and inventory == demand
```

で抽出する。

数件の手計算テストを作る。

---

## 4. Replay総量

M4.4:

- R1 boundary: 48
- R2 composite: 56
- total: 104

M4.4.1:

- R1 boundary: 48
- R1b comparison equality: 8
- R2 composite: 56
- total: **112**

元combined 1080に対し約10.4%。

160上限以内。

同じrecordをさらに何倍も複製しない。
各対象を追加1回だけ。

---

## 5. Manifest

保存:

```text
r1_boundary
r1b_comparison_equality
r2_composite
```

を別集計する。

R1bについて:

- source group IDs
- source record IDs
- parsed inventory
- parsed demand
- targets c1/c2

を監査JSONへ残す。

---

## 6. Data isolation

replay sourceはM3 trainのみ。

次とのID / exact input overlapを改めて0確認:

- M3 dev
- eval_v2
- transfer_probe
- smoke
- fresh phrasing

評価データそのものを追加しない。

---

## 7. 学習

B0から一回。

```text
M3                         600
M4.1                       240
M4.3.1 phrasing            240
R1 boundary replay          48
R1b comparison replay        8
R2 composite replay         56
--------------------------------
total                     1192
```

M4.4 checkpointから継続学習しない。

---

## 8. checkpoint selection

M4.4と同じ規則を維持。

eval_v2を選定に使わない。

新しいR1b devを作らない。
今回はtraining source coverage修正だけを見る。

---

## 9. 評価

比較:

- W_v2_ce10
- W_m4_3p_fix
- W_m4_4r
- 新 W_m4_4_1

T=1。

### eval_v2

特に旧9 regression IDsを分離。

さらに5件のcomparison equality regression:

- eval_v2-er-0009-c1
- eval_v2-er-0009-c2
- eval_v2-er-0049-c1
- eval_v2-er-0093-c1
- eval_v2-er-0093-c2

について回復数を明記。

### HP regressions

4件は別に記録する。

M4.4.1ではここが回復しなくても、
R1b修正の成否とは分けて解釈する。

### その他

- fresh M〜P
- eval_exception
- transfer_probe
- smoke

を同じ条件で評価。

---

## 10. 成功判定

M4.4.1は総合採用試験ではなく
**selector修正の因果テスト**。

### R1b success

5件の在庫comparison equality regressionのうち
明確な回復が見られる。

目安:
- 3/5以上回復

かつ新しいcomparison regressionを大量に作らない。

### fresh保持

- Diff Both >= 55%
を目安。

M4.4の60%から多少揺れることは許容する。

### 全体

eval_v2総合97%に届かなくても、
R1bが回復すれば実験は有益。

HP ANDは次の独立課題として扱う。

---

## 11. 結果分岐

### A: comparison equality回復
Retention Replay自体は有効。
M4.4失敗の一因はselector coverage不足。

次:
HP composite interferenceだけを独立分析。

### B: comparison equalityも回復しない
train内の直接対応例をreplayしても保持できない。

次:
checkpoint selection / task interference / capacity
の診断へ進む。

### C: equality回復するがfresh大幅低下
replayによるtradeoff。

次:
replay weightingを減らすか、
別の保持方式を検討。
大量追加しない。

---

## 12. テスト

必要:

1. comparison equality selector:
   inventory==demandだけ抽出。
2. 4 groups / 8 casesを現データで確認。
3. c1/c2 targetが equalityで逆になること。
4. replay total 112。
5. sourceがM3 trainだけ。
6. evaluation set overlap 0。

既存test infrastructureを使う。

---

## 13. Codex / Antigravityへの指示

```text
M4.4-Rのreview_bundle.zipを実物レビューしました。

重要な見落としがあります。

M4.4のR1 selectorは
rule_kind == "boundary"
だけを対象にしていたため、
eval_v2で実際に退行している
在庫数 == 受注数 の rule_kind == "comparison"
をreplayしていません。

M3 trainには直接対応する例が存在します:

train-er-0031: 38 == 38
train-er-0151: 55 == 55
train-er-0199: 59 == 59
train-er-0283: 40 == 40

各groupで、
在庫 >= 受注 はship、
在庫 > 受注 はdelay
となっています。

したがって、
「trainに対応ドメイン/能力がない」
「単純Retention Replayは効かない」
とはまだ結論しないでください。

M4.4.1ではselector coverageだけを修正します。

既存M4.4の
R1 boundary 48 cases
R2 composite 56 cases
を維持し、

M3 trainの
rule_kind=comparison かつ inventory==demand
4 groups / 8 casesをR1bとして追加replayしてください。

合計replayは112 casesです。

HP R2の量は変更しないでください。
新データ生成、新loss、checkpoint規則変更、
校正、API変更はしません。

B0からM4.4と同一条件で一回だけ学習し、
eval_v2の旧5件comparison equality regressionが
何件回復するかを最重要で比較してください。

fresh phrasing、eval_exception、transfer、smokeもT=1で確認してください。

これでcomparison equalityが回復するなら、
M4.4のPattern Cはselector coverage不足が主因だったと判断できます。

回復しない場合に初めて、
checkpoint selection / task interference / capacityを検討します。

旧モデル・旧成果物は上書きせず、
レビューZIPを作成してください。
```
