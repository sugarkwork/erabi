# ERABI M4.3.1 ZIP 実物レビュー

作成日: 2026-09-19

## 結論

M4.3.1 Semantic Repair は成功している。

- generatorの意味ラベル不整合は修正された。
- rendered-record-only semantic validator が導入された。
- 修正版 train/dev/fresh は validator 100% PASS。
- 保存予測の主要集計は報告値と一致。
- ZIPは87 files / 565,614 bytes、SHA256も報告値と一致。

ただし `W_m4_3p_fix` は、M4.3-Pで事前に置いた採用目安をまだ満たしていない。

### 未見表現
fresh M〜P:
- Accuracy: 94/120 = 78.3%
- Diff-Target Both: 15/30 = 50.0%

元の実験目安:
- Diff-Target Both >= 60%

したがって、未見priority phrasingへの一般化は明確に改善したが、目標未達。

### M3保持
eval_v2:
- W_v2_ce10: 195/200 = 97.5%
- W_m4_3p_fix: 187/200 = 93.5%

差:
- -4.0pt

元の保持目安:
- -3pt以内

したがって、旧能力保持も目安を少し超えて悪化している。

`W_m4_3p_fix` をM3基準版の置換モデルとして昇格する段階ではない。
有望な実験版として保全する。

---

## 1. Fresh family別の偏り

保存予測を再集計した結果:

| Family | Accuracy | Diff Both | Same Both |
|---|---:|---:|---:|
| M | 29/32 | 5/8 | 8/8 |
| N | 28/32 | 6/8 | 6/8 |
| O | 22/28 | 3/7 | 5/7 |
| P | 15/28 | 1/7 | 3/7 |

Family M/Nは比較的強い。
Family O/Pは明確に弱い。

特にP:
`競合解決順はA、Bの順。最初に成立した規則の結果を採用`
という「ordered precedence / first-match」型で、
priority切替を十分に読めていない。

O:
`Bを基本判定とするが、A成立時にはAを最終結果とする`
というoverride構文でも失敗が残る。

---

## 2. Priority方向の偏り

freshケース単位の正答:

Family M:
- A_over_B: 16/16
- B_over_A: 13/16

Family N:
- A_over_B: 16/16
- B_over_A: 12/16

Family O:
- A_over_B: 12/14
- B_over_A: 10/14

Family P:
- A_over_B: 6/14
- B_over_A: 9/14

単純に「B優先だけ苦手」ではない。
phrasing familyとpriority方向の相互作用がある。

M/NではA_over_Bに強く、
Pでは逆にA_over_Bが弱い。

したがって、単一の方向バイアス補正だけでは説明できない。

---

## 3. M3退行の個票

eval_v2で baseline `W_v2_ce10` と `W_m4_3p_fix` を比較:

- 共通正解: 186
- baselineのみ正解（新モデルで退行）: 9
- 新モデルのみ正解: 1
- 共通誤答: 4

純減:
- 8問

退行9件の大半は `explicit_rule` の novel 問題。
比較・複合条件の旧能力が一部失われている。

したがって、次モデルでは phrasing能力だけでなく
M3 replay / retentionも観測対象にする必要がある。

---

## 4. transfer_probeの遷移

W_v2_ce10 -> W_m4_3p_fix:

- baselineのみ正解: 5
- fixのみ正解: 2
- 純減: 3問

正答数:
- 25/32 -> 22/32

回復:
- negation系2件

退行:
- boundary
- edge
- retain
- NLI retain
- scale

など複数種類。

特定1タスクだけの退行ではない。

---

## 5. smoke

W_v2_ce10 -> W_m4_3p_fix:

回復:
- smoke-08 NLI contradiction
- smoke-09 NLI unknown

退行:
- smoke-10 exchange -> none

結果:
- 9/12 -> 10/12

smokeだけを見ると改善だが、
M3/transfer全体の保持を保証しない。

---

## 6. semantic validatorについて

今回ZIPのvalidatorは、
generator内部の `cond_a`, `cond_b` を受け取らず、

- context
- question
- choices

からdomain、条件成立、priority orderを再導出している。

M4.3旧版の問題だった
「generator内部フラグとvalidatorが同じ誤りを共有」
という構造は解消されている。

固定合成文法用validatorとしては妥当。

汎用自然言語validatorではないので、
今後新しいtemplateを追加した場合は
parser対応と独立手計算例を追加する。

---

## 7. family quotaの実際

fresh M〜Pは120件だが、
family件数は完全均等ではない。

- M: 32 cases / 16 pairs
- N: 32 / 16
- O: 28 / 14
- P: 28 / 14

原因はquota 30/18/12 pairsを4 familyへ整数分配した余りを
前方familyへ配る実装。

これはラベルバグではない。
manifestにも正しく記録されている。

ただしfamily別比較では分母を必ず併記する。

---

## 8. 次の判断

まだ追加学習しない。

未確認なのは、

> W_m4_3p_fix が、学習したE〜J自体をどの程度解けているか

である。

これを測らずに「表現多様性がもっと必要」と結論付けると、
実際には単なるunderfittingだった場合を見落とす。

次は M4.3.2 Generalization Gap Diagnostic を実施する。
