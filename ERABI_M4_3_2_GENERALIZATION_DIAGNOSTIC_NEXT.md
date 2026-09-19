# ERABI — M4.3.2: Phrasing Generalization Gap Diagnostic

作成日: 2026-09-19

## 0. 目的

再学習なしで、

1. Training Families E〜J をモデルが覚えられているか。
2. Dev Families K〜L へどれだけ移るか。
3. Fresh Families M〜P でどこが崩れるか。
4. M3旧能力の退行がどの系統へ集中するか。

を分ける。

結果を見てから、
次の学習を

- データ量増加
- 表現種類増加
- 旧能力replay強化
- モデル容量検討

のどれにするか一つだけ選ぶ。

---

## 1. 今回は学習しない

固定:

- W_v2_ce10
- W_m4_1
- W_m4_3p_fix
- 全評価 T=1

変更禁止:

- weights
- data
- calibration
- API
- loss
- tokenizer
- model architecture

新しいデータ生成も原則しない。

保存済みdatasetとモデルを評価するだけ。

---

## 2. 最優先: Phrasing Train / Dev / Fresh を同じ集計で評価

W_m4_3p_fixについて:

### Train
`data/m4_3_1_phrasing_fix/phrasing_train.jsonl`
Families E〜J

### Dev
`data/m4_3_1_phrasing_fix/phrasing_dev.jsonl`
Families K〜L

### Fresh
`data/m4_3_1_phrasing_fix/fresh_phrasing_eval.jsonl`
Families M〜P

同じevaluate経路、生logits、T=1で測る。

各splitについて:

- Accuracy
- NLL
- Brier
- Pair Both
- Diff-Target Both
- Same-Target Both
- Unswitched rate
- switched-but-wrong rate

---

## 3. Family別

E〜Pの各familyごとに:

- cases
- pairs
- diff pairs
- same pairs
- Accuracy
- Diff Both
- Same Both
- NLL
- Brier
- A_over_B case accuracy
- B_over_A case accuracy

を出す。

分母を必ず併記する。

---

## 4. Domain / State別

最低限:

### domain_class
- old
- new

### stratum
- conflict
- single
- fallback

### domain
各domain

についてAccuracyを出す。

ただし少数セルの値を一般性能と呼ばない。

---

## 5. 解釈ルール

### Case A — Train E〜JもDiff Bothが低い
目安:
- train diff both < 90%

意味:
- 未見表現汎化以前に、学習family自体の習得が不十分。
- データ件数、更新回数、モデル容量の問題が候補。

次:
- いきなりfamilyを増やさない。
- 同じE〜Jのデータ量/学習予算の小規模スケーリングを検討。

### Case B — Train高い、Dev K〜L低い
意味:
- 表現generalization gapが明確。
- E〜Jを覚えたが別表現へ移れていない。

次:
- train phrasing familiesの種類を広げる。
- ただしK〜Pをそのまま学習に使わず、
  新しいtraining-only familiesを作る。

### Case C — Train/Dev高いがFresh O/Pだけ弱い
意味:
- 一般的なphrasing shiftより、
  ordered precedence / overrideの特定意味構造が難しい。

次:
- O/Pの文面をコピーせず、
  同じsemantic operatorを別文面で表す新training familiesを追加。

### Case D — Train/Dev/Freshとも高い
意味:
- 既存freshの50%集計やcheckpointが不整合の可能性。
- まず評価・ファイル対応を監査し、再学習しない。

---

## 6. M3 retention audit

`eval_v2`について:

W_v2_ce10 -> W_m4_3p_fix の

- maintained correct
- recovered
- regressed
- wrong both

を個票化する。

退行9件について:

- task_family
- template_family
- rule_kind等、存在するmetadata
- target
- baseline prediction
- fix prediction
- pmax / target probability

を保存。

系統別件数を集計。

目的:
次回のreplay増量が本当に必要か判断する。

---

## 7. transfer transition audit

transfer_probeも:

- maintained
- recovered
- regressed
- wrong both

を出す。

既存32問は学習に使わない。

---

## 8. Fresh M〜Pのerror matrix

特にM/N/O/Pについて:

- diff pair both失敗
- unswitched
- switched-but-wrong
- priority direction
- domain

を一覧化。

既に確認されている傾向:

- M: Diff 5/8
- N: 6/8
- O: 3/7
- P: 1/7

これを実機保存予測から正式に再集計する。

---

## 9. 次フェーズを一つだけ提案する

診断後、以下から一つだけ。

### M4.4-S — Scale
Train E〜J自体が未習得の場合。
同じ意味分布の学習量/予算を増やす。

### M4.4-V — Variety
Trainは高いがDev/Freshへ移らない場合。
新しいtraining-only phrasing familiesを増やす。

### M4.4-O — Operator
O/P型semantic operatorだけが弱い場合。
override / ordered-precedenceの別表現を重点追加。

### M4.4-R — Retention
phrasingは十分だがM3退行が支配的な場合。
旧M3 replay比率やcheckpoint選択を小さく調整。

一度に複数実施しない。

---

## 10. 成果物

例:

```text
runs/m4_3_2_diagnostic/
  phrasing_train_predictions.json
  phrasing_dev_predictions.json
  phrasing_fresh_predictions.json
  family_summary.json
  retention_transitions.json
  transfer_transitions.json
  notes.md
```

新しいDBや実験基盤不要。

---

## 11. テスト

新コードが単なる集計なら、
大きなunit test追加は不要。

必要なら:
- pair groupingの小さな手計算例
- transition countの検算

程度。

通常モデル精度をpytest条件にしない。

---

## 12. Codex / Antigravityへの実行指示

```text
M4.3.1のSemantic Repairは確認できました。

ただし現モデルは、
fresh M〜P Diff Both 50%で元目標60%未満、
eval_v2も97.5%から93.5%へ4pt低下しており、
まだ採用版にはしません。

次の再学習前に、
M4.3.2 Generalization Gap Diagnosticを実施してください。

今回は学習・データ生成・校正・API変更を一切行いません。

W_m4_3p_fixをT=1で、
phrasing_train E〜J、
phrasing_dev K〜L、
fresh M〜P
の3splitへ同じ評価コードで通してください。

各split・各familyで
Accuracy,
NLL,
Brier,
Pair Both,
Diff Both,
Same Both,
Unswitched,
A_over_B/B_over_A
を出してください。

特に、
train E〜J自体が高精度なのか、
trainは高いがK〜Pへ移らないのか
を明確にしてください。

同時にeval_v2の
W_v2_ce10 -> W_m4_3p_fixの退行9件と回復1件、
transfer_probeの回復/退行を個票化してください。

結果に応じて、
Scale / Variety / Operator / Retention
の一つだけを次フェーズとして提案してください。

既存モデル・データ・校正・APIは上書きしません。
テストや抽象化を増やし過ぎず、
計画だけで止めず、診断・集計・結果保存まで進めてください。
```
