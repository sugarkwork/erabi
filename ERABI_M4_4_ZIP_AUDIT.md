# ERABI M4.4-R ZIP実物レビュー

作成日: 2026-09-19

## 結論

M4.4-R の実験結果自体は報告と整合する。

ただし、

> 「M3 train内のRetention Replayでは回復できなかった」
> 「在庫・出荷の等号境界はtrainに対応語彙/ドメインがない」

という解釈には重要な見落としがある。

**Retention selector が `rule_kind == "boundary"` だけをR1対象にしており、
`rule_kind == "comparison"` の在庫=受注の等号ケースを取りこぼしている。**

したがって今回の結果は、

> 「点数ドメインのboundary equalityを増やしても、
> 在庫comparison equalityの忘却は回復しなかった」

ことは示すが、

> 「正しく対応したM3 train retentionを行っても回復しない」

ことまでは示していない。

大量リプレイやtask interference分析へ進む前に、
selectorを一度だけ正して再試験するのが最小である。

---

## 1. ZIP確認

ユーザー提供 `review_bundle(9).zip`:

- files: 20
- size: 164,625 bytes
- SHA256:
  `c9eccb61a57f80c93e11ee78277cf6b1b99a10c01820dd92afbecafc2065afb4`
- ZIP integrity: OK

報告値と一致。

---

## 2. 現Retention R1実装の問題

`prepare_m4_4_retention_data.py` はR1抽出時に:

```python
if r.get("rule_kind") == "boundary":
    ...
```

としている。

そのためR1に選ばれたのは:

- 点数
- 合格 / 不合格
- 以下 / 未満

の `boundary` 問題だけ。

実際:
- 24 groups
- 48 cases

がreplayされた。

---

## 3. しかしM3 trainには、退行ケースと同型の在庫comparison equalityが存在する

M3 trainの `rule_kind == "comparison"` を独立に確認した。

comparison:
- 116 cases

そのうち `在庫数 == 受注数`:
- **4 groups / 8 cases**

具体例:

### train-er-0031

```text
倉庫の在庫数は38個、顧客からの受注数は38個です。

c1:
在庫が受注数以上あれば即時出荷
→ target: ship

c2:
在庫が受注数を上回っている（受注数を超える）場合のみ出荷
→ target: delay
```

他:
- train-er-0151: 55 == 55
- train-er-0199: 59 == 59
- train-er-0283: 40 == 40

これはeval_v2で退行した:

```text
在庫92、受注92
「達していれば出荷」 vs 「受注より多い場合のみ出荷」
```

と、ドメイン・数値関係・`>=` vs `>` の意味構造が直接対応している。

---

## 4. 「語彙・ドメイン完全乖離」は正確ではない

M4.4報告では、

- M3 train equalityは100%点数ドメイン
- eval_v2 regressionは在庫・受注
- 「達していれば」はtrainに0回

を根拠に完全乖離と解釈している。

しかし実際にはM3 trainに:

```text
在庫が受注数以上あれば即時出荷
```

と

```text
在庫が受注数を上回っている（受注数を超える）場合のみ出荷
```

の equality comparison が存在する。

「達していれば」という**文字列そのもの**は0回でも、
同じ在庫/受注ドメイン・同じinclusive/exclusive comparisonはtrainにある。

元 `W_v2_ce10` がnovel wordingへ一般化していたこととも整合する。

したがって、問題は
「trainに対応能力がない」ではなく、

**今回のRetention selectorが対応能力をreplay対象に含めなかった**
可能性が高い。

---

## 5. M4.4結果の有効な部分

M4.4-Rの保存結果自体は有効。

特に:

- fresh Diff Both:
  50.0% → 60.0%
- eval_exception:
  100%維持
- smoke:
  10/12 → 11/12
- eval_v2:
  93.5% → 92.5%

は実験結果として記録してよい。

また、単なる点数boundary replayで
在庫comparison equalityが回復しなかったことも有用。

ただしこれを
「Retention Replayという方法自体の失敗」
とは扱わない。

---

## 6. Checkpoint selectionの問題もまだ未証明

M4.4 best checkpointはEpoch 9。

Dev historyではEpoch 7〜10がeligibilityを満たすが、
M3 devは98〜100%で飽和している。

R1/R2 dev diagnosticsも早期から100%に張り付いている。

これは、

> 現devでは今回の在庫comparison equality忘却を観測できない

ことを示す。

ただし、checkpoint selectionだけを変えれば解決すると
まだ証明されたわけでもない。

先に正しいRetention sourceを入れ、
同じselection規則で一度試す方が因果関係が明確。

---

## 7. 次の実験

M4.4.1 Corrected Retention Selector:

変更は **R1 selectorだけ**。

既存M4.4の:

- R1 boundary equality 48 cases
- R2 composite balanced 56 cases

を維持し、
さらに

- R1b comparison equality 8 cases

をM3 trainからreplayする。

合計 replay:
- 112 cases

上限160以下。

まず1回だけ同条件でB0から再学習。

これで在庫comparison regressionが回復するなら、
M4.4のPattern C判断は
「selector coverage不足」が主因だったと分かる。

回復しないなら、
その時点でtask interference / checkpoint selectionを検討する。

---

## 8. HP複合ANDについて

M4.4ではR2を正しく4状態均衡でreplayしたにもかかわらず、
eval_v2の4件は回復しなかった。

これは別問題として残る。

M4.4.1ではR2量を増やさない。

理由:
R1 selector修正とR2比率変更を同時に行うと、
結果の原因が分からなくなる。

M4.4.1後に:

- comparison equalityだけ回復
- HP ANDは回復しない

となれば、HP interferenceを独立して扱える。

---

## 9. 採用判断

現在:

- W_v2_ce10: 基準版
- W_m4_3p_fix: 有望なphrasing実験版
- W_m4_4r: retention実験版、採用しない

を維持。

M4.4.1も正式採用を前提にしない。
