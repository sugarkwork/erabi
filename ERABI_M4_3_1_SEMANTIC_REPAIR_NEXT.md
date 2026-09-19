# ERABI — M4.3.1: Phrasing Dataset Semantic Repair

作成日: 2026-09-19

## 0. 目的

M4.3-Pの表現多様化実験で見つかった、
`game_action` / `facility_control` の
「自然文の条件」と内部 `cond_a` / target の不一致を修正する。

今回は新しい能力追加をしない。

**データ意味整合性の修正だけを変数として、
同条件で一度だけ再学習する。**

---

## 1. 今回変更しないもの

- base model: `knowledgator/gliclass-instruct-base-v1.0`
- model architecture
- loss: standard CE
- lr = 2e-5
- weight_decay = 0.01
- micro_batch = 2
- grad_accum = 8
- seed = 42
- max epochs = 10
- M3 train/dev
- M4.1 exception train/dev
- phrasing family partition E-J / K-L / M-P
- API
- calibration
- transfer_probe
- smoke
- historical models

既存W_m4_3p、M3、M4.1成果物を上書きしない。

---

## 2. generatorの修正

`val_low / val_high` を
「Rule A false / true」と同一視しない。

各domainに明示的に:

```text
rule_a_true_range
rule_a_false_range
```

または同等の意味を持つ設定を置く。

例:

### game_action
Rule A:
`HP < 20`

```text
true_range  = 10..18
false_range = 25..45
```

### delivery_dispatch
Rule A:
`weight >= 30`

```text
true_range  = 35..55
false_range = 12..25
```

### system_ops
Rule A:
`CPU >= 80`

```text
true_range  = 85..96
false_range = 30..65
```

### facility_control
Rule A:
`temperature <= 25`

```text
true_range  = 15..23
false_range = 28..38
```

manufacturing / facility_power / inventory / job_schedulerも
同じ考え方で明示する。

### sampling

- conflict: Rule A true + Rule B true
- single_a: A true + B false
- single_b: A false + B true
- fallback: A false + B false

を先に意味として決め、
そのtruth stateに対応する値をsampleする。

---

## 3. context templateもtruth stateと一致させる

数値と説明文が矛盾しないこと。

禁止例:

```text
HPは16（危険水域外）
```

Rule AがHP<20なら16は危険側。

禁止例:

```text
温度21度（25度超過）
```

21 <= 25。

template中に
「基準未満」「基準超過」「十分」「満充電帯」
などの意味ヒントを書く場合、
数値と必ず一致させる。

---

## 4. 本当に独立したsemantic validator

generatorが設定した `cond_a`, `cond_b` をvalidatorへ渡さない。

validatorは **レンダリング後recordのみ** を受け取る。

```python
derive_semantics(record) -> {
    cond_a: bool,
    cond_b: bool,
    expected_target: choice_id
}
```

固定された合成文法なので、
汎用NLP parserを作る必要はない。

domainごとの小さなparserでよい。

例:
- game: HP数値 + 移動状態の語
- delivery: 重量 + 緊急指定
- system: CPU数値 + security alert
- facility: 温度 + emergency signal
- manufacturing: 誤差 + defect flag
- power: kW + SOC
- inventory: days + quarantine
- scheduler: wait minutes + memory GB

生成後、**全レコード**について:

```text
parsed expected target == stored target
```

をassertする。

validatorは `determine_target(cond_a, cond_b...)` と
同じ内部booleanを共有しない。

---

## 5. 既存M4.3データを修正せず、新版を別パスへ生成

例:

```text
data/m4_3_1_phrasing_fix/
  phrasing_train.jsonl
  phrasing_dev.jsonl
  fresh_phrasing_eval.jsonl
  combined_train.jsonl
  combined_dev.jsonl
  manifest.json
  semantic_audit.json
```

旧M4.3データは比較用に残す。

件数・family・quotaはM4.3と同じ。

- train 240
- dev 80
- fresh 120

M3 + M4.1とのcombined件数も同じ。

---

## 6. 分離

旧M4.3と文章が変わること自体は問題ない。

ただし修正版について:

- train/dev/fresh相互 exact overlap 0
- M3/M4.1/past evaluationとの exact overlap 0
- group separation
- family split E-J / K-L / M-P
- quota固定

を確認する。

semantic stateについては、
旧M4.3と同じ状態を完全禁止する必要はない。
今回は「同じ実験を正しいラベルでやり直す」ことが目的だから。

ただし新trainと新fresh間はsemantic stateを分離する。

---

## 7. M4.2.1 Cell A/Bの扱い

`build_m4_2_1_diagnostic_data.py` のOLD domain samplingも同じ問題を監査する。

修正後:

- Cell A old-domain + old-phrasing
- Cell B old-domain + new-phrasing

を別パスへ再生成して再評価する。

Cell C（new domain）とPhase A D（new domain）は
今回の旧-domain samplingバグの直接対象ではないので、
既存結果を保持してよい。

2×2診断の結論は新A/Bで更新する。

---

## 8. 再学習

データ監査が100%通った場合のみ実施。

B0から:

```text
M3 train               600
M4.1 exception train   240
M4.3.1 phrasing train  240
---------------------------
total                  1080
```

dev:

```text
M3 dev                 100
M4.1 dev                40
M4.3.1 phrasing dev     80
---------------------------
total                  220
```

学習条件は旧M4.3と完全同一。

checkpoint selectionも同一規則:

1. M3 dev >= 95%
2. M4.1 dev >= 95%
3. その中で phrasing dev Diff Both 最大
4. tieなら phrasing dev NLL 最小

---

## 9. 比較

T=1。

比較:
- W_v2_ce10
- W_m4_1
- 旧 W_m4_3p
- 新 W_m4_3p_fix

評価:
1. 修正版 fresh M-P
2. 修正版 M4.2.1 Cell A/B
3. novel_priority_eval A-D（new-domain部分は既存）
4. Cell C
5. eval_exception
6. eval_v2
7. transfer_probe
8. smoke

特に:
- fresh Diff Both
- fresh Same Both
- family M/N/O/P別
- game_action / facility_control別
- new-domain-only subset
- old-domain-only subset
を出す。

---

## 10. 旧結果の扱い

旧M4.3の:
- 85.8% fresh accuracy
- 80.0% fresh Diff Both

は **誤ラベルを含む旧データ上のスコア**として記録し、
以降の代表性能として使わない。

ただし方向性の参考として削除しない。

保存logitsを使った暫定補正では、
確認できたgame/facility誤ラベルだけ直すと:

- W_m4_3p fresh accuracy: 約75.0%
- Diff Both: 約73.1%

また、当該バグの影響を受けないnew-domain subsetでは:
- 54/62 = 87.1%
- Diff Both 12/16 = 75.0%

よって「phrasing diversificationの効果がゼロだった」とは扱わない。

正式値は修正版データ・修正版モデルで決める。

---

## 11. テスト

増やすのは次だけ。

1. 各domainのRule A true/false境界の手計算例。
2. rendered recordだけからsemantic validatorが正解を復元できる。
3. HP=35 + moving では healではなくcontinueになること。
4. temp=21 + no alarm では eco_modeになること。
5. `25度超過`等の説明と数値が矛盾しない。
6. quota / split / family分離。

テスト件数やcoverage目標を増やさない。

---

## 12. 停止条件

独立semantic validatorで1件でも不一致が残る場合:
- 再学習しない。
- mismatch一覧を保存して終了。

全件通過した場合のみ一回再学習する。

---

## 13. Codex / Antigravityへの指示

```text
M4.3-P review_bundle.zip の実物レビューで、
新規phrasingデータに意味ラベル不整合が見つかりました。

build_m4_3_data.py はOLD domainで一律に
conflict/single-Aへval_high、
single-B/fallbackへval_low
を使っています。

これは delivery/system では成立しますが、
game_action (HP<20) と facility_control (temp<=25) では逆です。

実データでは少なくとも:
- phrasing_train: 41/240 records
- phrasing_dev: 15/80 records
- fresh_eval: 18/120 records
で、game/facilityの自然文から導くtargetと保存targetが不一致です。

例:
HP=35、移動中、Rule A=HP<20、Rule B=移動中、
A>Bとして保存target=heal ですが、
自然文上はA不成立/B成立なのでcontinueが正解です。

今回は新しい能力追加へ進まず、
ERABI M4.3.1 Semantic Repairを行ってください。

domainごとにRule A true_range / false_rangeを明示し、
truth stateから値をsampleしてください。

さらに、generator内部のcond_a/cond_bを共有しない
rendered-record-onlyの独立semantic validatorを実装し、
全レコードのtargetを検証してください。

M4.3.1のtrain/dev/freshを別パスへ再生成し、
validatorが100%通った場合だけ、
B0から旧M4.3と同一条件で一度だけ再学習してください。

M4.2.1 Cell A/BのOLD domain生成も同様に監査・修正してください。

旧データ・旧モデル・M3/M4.1・校正・APIは上書きしません。
新loss、モデル構造変更、robustness混合、校正は行いません。

テストや抽象化を増やし過ぎず、
修正・監査・一回の比較再学習・結果保存まで進めてください。
```
