# ERABI — M4.4-R: Targeted Retention Replay

作成日: 2026-09-19

## 0. 今回の判断

M4.3.2 Generalization Gap Diagnostic の結果から、
次フェーズは **Retention Replay** とする。

理由:

- Phrasing Train E〜J:
  - Accuracy 98.3%
  - Diff Both 95.0%
  - Unswitched 5.0%
  → 学習表現自体は十分に習得済み。
- Fresh M〜P:
  - Diff Both 50.0%
  - Family M/Nは60%超、O/Pが弱い。
  → 表現汎化の課題は残るが、すべての表現で崩れているわけではない。
- eval_v2:
  - 97.5% → 93.5%
  - 退行9件が
    - 等号境界 5件
    - HP複合AND 4件
  に集中。
- transfer_probe:
  - 25/32 → 22/32
  - 境界値退行が一部共通。

今回は **旧能力保持の回復だけ** を変数にする。

Family K/Pへの追加学習、NLI混合、新loss、モデル変更、校正は行わない。

---

## 1. 重要な禁止事項

### eval_v2 を学習に使わない
今回退行した9件を、そのままtrainへ入れない。

### transfer_probe を学習に使わない
既に何度も結果を見ている診断集合なので固定する。

### smoke_cases を学習に使わない

### Family K〜P を新たに学習に使わない
今回のRetention実験ではpriority phrasing側を変更しない。

目的は、M3旧能力の保持だけを回復すること。

---

## 2. Baseline

比較対象:

- `W_v2_ce10`
- `W_m4_1`
- `W_m4_3p_fix`
- 新しい `W_m4_4r`

全評価 T=1。

既存M3 calibration `T=3.1097` を新重みに流用しない。

---

## 3. まず M3 train 内のRetention候補を監査する

対象:
`data/m3_3_v2/train.jsonl`

以下を抽出して件数を記録する。

### R1 — Equality Boundary

`actual == threshold` で、
演算子の違いが答えを変える能力を保持する例。

例:
- `>=` と `>`
- `<=` と `<`
- 「以上」と「超」
- 「以下」と「未満」

既存train内の該当record/groupのみを使用。

### R2 — Composite AND: one condition false

特にM4.3.2で退行した:

```text
HP条件は成立
アイテム条件は不成立
→ healしてはいけない
```

タイプ。

ただしこれだけに偏らない。

可能ならM3 trainから以下を均衡して抽出:

- HP true, item true
- HP true, item false
- HP false, item true
- HP false, item false

AND条件を片方だけ見てshortcutできない構成にする。

### R3 — その他のM3境界保持

監査で同じ原因に属するtrain例があれば、
既存M3 trainから少数追加してよい。

ただし新しい能力領域を増やさない。

---

## 4. Replayの作り方

最初は**既存M3 trainの再重み付け**だけを行う。

新しい合成データを作らない。

### 方法

対象record/groupを、combined train内で追加複製する。

例:

```text
base M3 train                  600
M4.1 exception train           240
M4.3.1 phrasing train          240
targeted retention replay     120前後
----------------------------------
total                       約1200
```

`120`は実験予算の目安。

実際のM3 train該当件数を確認してから、
以下のように均衡させる。

推奨目安:

- Equality boundary replay: 50〜60 cases
- Composite AND replay: 50〜60 cases

同じ1レコードを何十回も複製しない。

原則:
- unique source recordをできるだけ広く使う
- 必要なら2〜4倍程度の重み付け
- source ID / replay countをmanifestに保存

新しいSampler基盤を作らず、
`combined_train_retention.jsonl`を作るだけでよい。

---

## 5. Replay量の上限

オーバーフィットと新能力の希釈を避けるため、
replay追加は **元combined train 1080件の15%程度以内** を最初の上限とする。

目安:
- 最大160 cases程度

最初から300〜500件追加しない。

---

## 6. Devは原則変更しない

checkpoint選択は、
M4.3.1と同じ:

- M3 dev
- M4.1 exception dev
- M4.3.1 phrasing dev

を使用。

Retention専用devを新設しない。

理由:
eval_v2やtransferの既知誤答へbest checkpointを直接合わせないため。

必要なら、M3 dev内のR1/R2 subsetを
**診断表示だけ**追加してよいが、
selection条件を複雑化しない。

---

## 7. 学習

B0から一回だけ学習する。

```text
M3 train                   600
M4.1 exception train       240
M4.3.1 phrasing train      240
retention replay       <= 160
------------------------------
total                 <= 1240
```

設定は固定:

- base: `knowledgator/gliclass-instruct-base-v1.0`
- standard CE
- lr=2e-5
- wd=0.01
- micro=2
- accum=8
- seed=42
- max epochs=10

M4.3.1 checkpointから継ぎ足し学習しない。

---

## 8. Checkpoint選択

まずM4.3.1の選択規則を維持する。

1. M3 dev >= 95%
2. M4.1 exception dev >= 95%
3. 条件を満たす中で phrasing dev Diff Both 最大
4. tieなら phrasing dev NLL 最小

Retention replayを入れたからといって、
eval_v2をcheckpoint選択に使わない。

---

## 9. 評価

T=1。

最低限:

### A. M3 retention
`eval_v2`

見るもの:
- Accuracy
- Diff Both
- NLL
- Brier
- previous 9 regression IDsの回復数
- 新たな退行数

### B. Phrasing generalization
修正版 `fresh_phrasing_eval`

見るもの:
- Accuracy
- Diff Both
- Same Both
- Family M/N/O/P別
- Unswitched

Retentionでfresh能力が大きく落ちないことを確認。

### C. M4.1 exception
`eval_exception`

### D. transfer_probe

### E. smoke_cases

---

## 10. 成功目安

これは今回の実験判断用。

### Retention最優先

`eval_v2`:
- Accuracy >= 97.0% を目安
- 退行9件のうち明確な回復がある
- 新しい大規模退行を作らない

### Phrasing保持

fresh M〜P:
- Diff Bothを M4.3.1 の50%から **-5pt以内**
- できれば50%以上維持

今回Retentionだけを変更するので、
fresh 60%達成は必須にしない。

### Exception保持

`eval_exception`:
- >= 98%

### smoke

- >= 10/12

transfer_probeは参考。
既知32問への最適化はしない。

---

## 11. 結果の読み方

### Pattern A
eval_v2回復、fresh維持
→ Retention Replay成功。
次にOperator/Phrasing課題（O/P）へ進める。

### Pattern B
eval_v2回復、fresh大幅低下
→ replay比率が強すぎる可能性。
次回はreplay量だけを減らす小比較を検討。

### Pattern C
eval_v2回復しない
→ 単純な重み付けでは保持できない。
大量replayへ進まず停止。
次はcheckpoint selection / model capacity / task interferenceを検討。

### Pattern D
eval_v2は回復するが別M3領域が新たに退行
→ targeted replayがshortcutを作った可能性。
個票を分析して停止。

---

## 12. 追加する診断

### R1/R2 subset performance

学習前後で、
M3 train/devのRetention subsetを
診断表示する。

ただし最終評価とは呼ばない。

### Transition table

W_m4_3p_fix → W_m4_4rについて:

- maintained correct
- recovered
- regressed
- wrong both

を
- eval_v2
- fresh phrasing
- transfer
- smoke
で記録する。

---

## 13. テスト

最小限。

必要:
1. retention selectorがeval/dev/freshから取らず、M3 trainだけを使う。
2. equality boundary抽出が手計算例と一致。
3. composite AND subsetの4状態分類が正しい。
4. replay count上限を守る。
5. source_id / replay回数manifestが正しい。

不要:
- 新しいサンプラーframework
- 全例snapshot
- coverage目標
- experiment registry

---

## 14. 今回は行わない

- Family O/P類似表現の学習追加
- Family K〜Pの学習利用
- NLIデータ混合
- routingデータ混合
- transfer_probe学習
- contrastive loss
- distillation
- ModernBERT
- calibration
- API変更

---

## 15. 成果物例

```text
data/m4_4_retention/
  retention_manifest.json
  combined_train_retention.jsonl

runs/m4_4_retention/
  retention_source_audit.json
  training_summary.json
  comparisons/
  transition_summary.json
  notes.md
  review_bundle.zip
```

大きな新基盤は作らない。

---

## 16. Codex / Antigravityへの実行指示

```text
M4.3.2診断結果を確認しました。

Phrasing Train E〜Jは
Acc 98.3%、Diff Both 95.0%であり、
学習表現のunderfittingではありません。

一方、eval_v2の退行9件は
- actual == threshold 等号境界 5件
- HP複合AND条件 4件
に集中しています。

次はM4.4-R Targeted Retention Replayを実施してください。

重要:
eval_v2、transfer_probe、smoke、fresh evalの問題そのものを
学習データへ入れないでください。

M3 trainだけから、
1. equality boundary例
2. composite ANDの4状態
を抽出し、
合計最大160cases程度の小さなreplayとして
M4.3.1 combined trainへ追加してください。

新しいデータ生成は最初は行わず、
既存M3 trainの重み付けだけを変数にしてください。

B0から、
M3 600 + M4.1 240 + M4.3.1 240 + replay <=160
を、旧条件と同じstandard CEで一回学習してください。

checkpoint selectionはM4.3.1の規則を維持し、
eval_v2を選定には使わないでください。

T=1で
eval_v2、
fresh phrasing M〜P、
eval_exception、
transfer_probe、
smoke
を比較してください。

成功目安は、
eval_v2 >=97.0%へ回復し、
fresh Diff Bothを50%から大きく落とさないことです。

今回はphrasing variety、Operator対策、NLI混合、
新loss、校正、API変更を行いません。

旧モデル・旧データ・校正・APIを上書きしません。
テストや抽象化を増やし過ぎず、
計画だけで止めず、一回の学習・比較・保存まで進めてください。
```
