# ERABI M4.3-P ZIP 実物レビュー

作成日: 2026-09-19

## 結論

M4.3-P の「表現多様化で改善した」という方向性は残るが、
現状の `W_m4_3p` を採用・校正する前に **M4.3新規データの意味ラベル不整合を修正して再学習**する必要がある。

今回確認したZIP:
- 71 files
- size: 449,309 bytes
- SHA256: `5c218a516f7a90191b9f94976554360ca937a6211443cc3bbed6411092b102b8`
- ZIP integrity: OK

---

## 1. 重大なデータ生成バグ

`build_m4_3_data.py` の旧4ドメイン用生成処理では、一律に

- conflict / single-A → `val_high`
- single-B / fallback → `val_low`

を使用している。

これは Rule A が「値が大きいと成立」するドメインでは成立するが、
Rule A が「値が小さいと成立」するドメインでは逆になる。

### 正しく動く例
- delivery_dispatch: 重量 >= 30 → high が true
- system_ops: CPU >= 80 → high が true

### 逆になる例
- game_action: HP < 20 → **low が true**
- facility_control: 温度 <= 25 → **low が true**

そのため、`game_action` と `facility_control` の一部レコードで、
内部フラグ `cond_a` とレンダリングされた自然文の真理値が逆転している。

---

## 2. 実データの明確な例

fresh eval先頭:

```text
Context:
現在のプレイヤーのHPは35です。回復アイテムあり。現在、安全地帯へ移動中。

Rule A:
HPが20未満なら「回復する」

Rule B:
移動中なら「移動を継続する」

Priority:
A > B
```

HP=35 なので Rule A は不成立。
Rule B だけ成立するため、priorityに関係なく正解は `continue`。

しかし保存データのtargetは `heal`。

これは曖昧な解釈ではなく、数値条件と正解ラベルの不一致。

別例:

```text
設備空調モニター：現在温度21度（25度超過）。
```

21度なのに「25度超過」と文章自体が矛盾している。
generic high/low sampling と template意味の不一致が原因。

---

## 3. 確認できた影響範囲

`game_action` と `facility_control` について、
レンダリング後の数値条件と文脈状態から独立に真理値を再計算した。

### phrasing_train
- 240 records中
- **41 records** で保存targetと自然文から導くtargetが不一致
- 120 pairs中 **30 pairs** が影響

### phrasing_dev
- 80 records中
- **15 records** 不一致
- 40 pairs中 **11 pairs** が影響

### fresh_phrasing_eval
- 120 records中
- **18 records** 不一致
- 60 pairs中 **14 pairs** が影響

これは少なくとも確認できた2ドメインの件数。
M4.3.1では全8ドメインを独立validatorで再検査する。

---

## 4. 「独立正解検証」は実装上独立していない

`build_m4_3_data.py` の:

```python
determine_target(cond_a, cond_b, ...)
```

は、context templateに付属した `cond_a / cond_b` をそのまま受け取ってtargetを決めている。

つまり、
**レンダリングされた自然文から条件を再評価していない。**

generatorの内部フラグが間違っていれば、
target計算も同じ間違いを共有するため検出できない。

報告の「生成ロジックとは独立した検証関数で全件検証」は、
今回ZIP内のM4.3 generatorについては、その意味では成立していない。

---

## 5. 保存logitsを使った暫定再採点

確認できた `game_action` / `facility_control` のtargetだけを
自然文の意味に合わせて訂正し、fresh M〜Pを保存raw logitsから再採点した。

これは正式な修正版評価ではなく、
影響規模を見るための暫定再採点。

### W_m4_3p

報告値:
- Accuracy: 103/120 = 85.8%
- Diff Both: 24/30 = 80.0%

確認済み誤ラベルだけを訂正した暫定値:
- **Accuracy: 90/120 = 75.0%**
- Diff-target pairs: 26組
- **Diff Both: 19/26 = 73.1%**

したがって、85.8% / 80.0% はそのまま採用しない。

一方で、当該バグの影響を受けない **new-domain subset** だけを見ると:

- **54/62 = 87.1%**
- **Diff Both 12/16 = 75.0%**

なので、
「未見phrasingへの改善シグナル」自体は残っている。

---

## 6. Family別の注意

W_m4_3p fresh（確認済み誤ラベル補正後の暫定）:

- Family M: 28/32, Diff 6/7
- Family N: 22/32, Diff 5/6
- Family O: 23/28, Diff 2/6
- Family P: 17/28, Diff 6/7

表現一般化は均一ではない。
特に Family O のdiff判断と、Family Pのsame/fallback系に弱さが残る。

「固定構文過適合が完全解消」とはまだ書かない。

---

## 7. M4.2.1診断への影響

`build_m4_2_1_diagnostic_data.py` にも、
old domain生成で同様の high/low generic sampling が存在する。

そのため Cell A/B（OLD domainを含む）は意味ラベルを再監査する必要がある。

ただし、
- Cell C = NEW domain + OLD phrasing
- Phase A / Cell D = NEW domain + NEW phrasing

という new-domain同士の比較では、
旧ドメインのこのバグの直接影響を受けない。

したがって、
「new phrasingで大きく落ちる」という診断シグナル自体は残るが、
Cell A/Bの数値は修正前の値として扱う。

---

## 8. 次の判断

M4.4やrobustness学習へはまだ進まない。

M4.3.1で:

1. generatorのRule A true/false samplingをドメイン意味に合わせて修正。
2. rendered contextから条件を再導出する独立semantic validatorを追加。
3. M4.3 phrasing train/dev/freshを再生成。
4. B0から同じ条件で一度だけ再学習。
5. W_v2_ce10 / W_m4_1 / 旧W_m4_3p / 修正版W_m4_3p_fixを比較。
6. M4.2.1 Cell A/Bも修正または正しいデータで再評価。

までを行う。

他の学習条件は変えない。
