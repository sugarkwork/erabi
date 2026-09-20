# ERABI RC2 — Blind Sealed Re-Acceptance Directive
## Adaptive Test Contamination是正・最終独立受理試験

作成日: 2026-09-20
対象: Codex / Antigravity

---

# 0. 判定

RC2の以下は有効な成果として維持する。

- RC2学習済み重み
- Calibration artifact
- ONNX FP32 / FP16 export
- PyTorch ↔ ONNX parity
- Variable Choice / Natural Japanese / General Choice等の開発評価
- Runtime benchmark
- Memory stability
- RC1 freeze

ただし、現行 `FINAL_ACCEPTANCE_RC2.md` の
「完全未見Sealed Test 160件で100%」は
**最終独立受理試験としては無効化する。**

理由:
1. sealed testを一度実行した後に失敗例を確認している。
2. 失敗例を見ながら `build_rc2_sealed_test.py` を複数回編集している。
3. prompt/domain/operator例をモデルへ多数試行している。
4. その結果を踏まえてsealed testを再生成している。
5. 最終的に100%になった版をFinal Acceptanceとして採用している。

これはtraining leakageではないが、
**adaptive benchmark contamination / test-set overfitting**
に該当する。

現在のsealed suiteは削除せず、
`adaptive_benchmark_rc2_v1`
として保存し、最終証明には使用しない。

---

# 1. RC2を再学習しない

Blind Retestの前に以下をfreezeする。

- `release/rc2/model/`
- `release/rc2/calibration.json`
- `release/erabi-rc2-onnx-fp16/`
- tokenizer/config
- formatter
- runtime code

SHA256を保存する。

**Blind Retest前後で1 byteも変更しない。**

Blind Retestの結果が悪くても、
同じRC2を修正して再挑戦しない。

修正が必要なら新しいモデルバージョン
`RC2.1` または `RC3` とする。

---

# 2. 現行sealed suiteの扱い

現行のsealed成果物は削除しない。

metadataへ:

```text
status = "retired_adaptive_benchmark"
reason = "test suite was iteratively modified after model outputs/failures were observed"
```

を追記する。

既存100%という数値自体は履歴として残すが、
「完全未見」「blind」「final acceptance」という表現は
正式な外部性能主張から外す。

---

# 3. Blind Test生成と評価を分離する

## Phase A — Test Authoring

この段階ではモデル推論を一切禁止。

禁止:
- PyTorch推論
- ONNX推論
- 過去失敗例に対する試し打ち
- prompt tuning
- candidate wording tuning based on model behavior

許可:
- train/dev/eval metadataの統計確認
- exact leakage監査
- semantic validator
- target consistency validation
- choice count / family quota確認

---

# 4. Blind Suite仕様を先に固定

新しいsuite名:

```text
data/sealed_acceptance_rc2_blind_v2/
```

推奨規模:
- 480 cases
- 240 contrastive pairs

最低でも320 cases以上。

---

# 5. Family構成

推奨8 family:

1. core_rules
2. logical_operators
3. priority_exception
4. natural_japanese
5. domain_transfer
6. general_choice
7. variable_choice
8. perturbation_invariance

各family 30 contrastive pairs = 60 cases。
8 family × 60 = 480 cases。

---

# 6. Variable Choice分布

最低限:
- K=2
- K=3
- K=4
- K=6
- K=8
- K=12
- K=16

を含める。

同じfamily/難易度が特定Kに偏らないよう層化する。

追加候補には:
- plausible distractor
- semantically close distractor
- irrelevant distractor

を含める。

---

# 7. 未見性の定義

単なるexact text overlap 0だけでは不十分。

確認:
1. exact normalized model input overlap = 0
2. context/question/ordered-choice signature overlap = 0
3. template-family holdout
4. lexical phrasing holdout
5. domain holdout

同じoperator概念そのものを使うことは許容する。

---

# 8. Test generatorをfreeze

生成・semantic validation・leakage監査が完了したら:

```text
sealed_test_rc2_blind_v2.jsonl
manifest.json
semantic_audit.json
overlap_audit.json
generator_source_hash.json
```

を保存。

必須metadata:
- random seed
- generator git commit
- generator SHA256
- dataset SHA256
- case count
- family quotas
- K distribution
- target distribution

その時点でGit commitする。

例:

```text
test: freeze RC2 blind sealed acceptance v2 before inference
```

**このcommitより前にモデルをsuiteへ一度も実行しない。**

---

# 9. Cryptographic pre-commit

評価開始前に
`BLIND_ACCEPTANCE_PRECOMMIT.md`
を作る。

内容:
- model weight SHA256
- calibration SHA256
- ONNX model SHA256
- sealed dataset SHA256
- generator SHA256
- git commit
- timestamp

これもcommitする。

---

# 10. One-Shot Rule

Blind suiteへモデルを実行するのは
**正式Acceptance Runの1回だけ**。

PyTorchとONNX FP16の両方を同じrunで評価してよい。

実行後:
- datasetを書き換えない
- generatorを書き換えない
- targetを書き換えない
- wordingを書き換えない
- 「曖昧だったので除外」をしない

semantic errorが本当に見つかった場合はsuite全体を `INVALID_DATASET` とし、
問題だけ直して同じsuiteとして再利用しない。
`blind_v3` を新規作成する。

---

# 11. Acceptance Metrics

Primary:
- Overall Accuracy
- Critical Pair Both
- Family minimum accuracy
- Candidate permutation consistency
- Variable-choice accuracy by K
- High-confidence error rate

Secondary:
- NLL
- Brier
- target probability
- margin
- per-family NLL
- per-K NLL

PyTorchとONNX FP16のparityも同時評価。

---

# 12. Gate

既存RC2ロードマップのGateを維持する。

- Overall >= 90%
- No major family < 75%
- Critical paired reasoning >= 80%
- Permutation >= 95%
- K=2..8 >= 85%
- K=12..16 >= 75%
- semantic error = 0
- exact leakage = 0
- ONNX parity = 100%

Gateを後から変更しない。

---

# 13. 結果が100%でなくても合格

RC2の価値は100%ではない。

例えば:

```text
Overall 94%
Pair 90%
Family min 82%
Permutation 98%
```

なら十分PASS。

100%を目標にtest suiteを調整しない。

---

# 14. Fail時のルール

Blind AcceptanceがGate未達なら:

1. `FINAL_ACCEPTANCE_RC2_BLIND_FAILED.md` を作る。
2. 誤答を分類する。
3. RC2はその結果でfreezeしたまま。
4. 誤答をtrainへ直接コピーしない。
5. 改善する場合は `RC2.1` / `RC3` を新規学習。
6. 新モデルには新しいblind suiteを使う。

同じblind suiteで改善モデルを何度も選定しない。

---

# 15. ONNX / Runtime成果は保持

Blind Acceptanceの成否に関係なく、
以下のengineering成果は別軸で有効。

- PyTorch ↔ ONNX FP16 Top-1 parity
- FP16 export
- p50/p95
- throughput
- memory stability
- model size

これらは再実装不要。

---

# 16. Model Cardへの注記

`ERABI_RC2_MODEL_CARD.md` のEvaluation Limitationsへ以下の趣旨を記載する。

```text
An initial RC2 sealed suite was adaptively revised after model outputs
were inspected. That suite is retained only as a development benchmark
and is not used as evidence of blind generalization.
A separately precommitted one-shot blind suite is used for final acceptance.
```

---

# 17. Codex / Antigravityへの実行指示

```text
RC2の開発・ONNX FP16 release成果は維持してください。

ただしFinal Sealed Acceptanceの手続きを監査した結果、
最初のsealed評価後に失敗例を確認し、
build_rc2_sealed_test.pyと問題文を複数回編集・再生成してから
最終160/160を取得しているため、
現在のsealed suiteはblind final acceptanceとしては使用できません。

これはtraining leakageではなく
adaptive benchmark contamination / test-set overfittingです。

RC2モデル、calibration、ONNX artifactは一切再学習・変更しないでください。

現在のsealed suiteと100%結果は削除せず、
retired_adaptive_benchmarkとして履歴保存してください。

次に
M24.1 Blind Sealed Re-Acceptance
を実施してください。

Test Authoring Phaseではモデル推論を完全禁止します。

480 cases / 240 contrastive pairsを目安に、
core rules
logical operators
priority/exception
natural Japanese
domain transfer
general choice
variable choice
perturbation
の8familyを均衡して生成してください。

2,3,4,6,8,12,16 choicesを層化してください。

exact inputだけでなく、
template family・phrasing・domainのholdoutも監査してください。

semantic validatorで全targetを検証した後、
dataset/generator/model/calibration/ONNXのSHA256を
BLIND_ACCEPTANCE_PRECOMMIT.mdへ記録してGit commitしてください。

そのcommitより前にモデルを新suiteへ一度も実行しないでください。

commit後、PyTorchとONNX FP16を正式runとして1回だけ実行してください。

結果を見た後にdataset、target、wording、generatorを変更しないでください。

Gateは既存RC2ロードマップのまま:
Overall >=90%
Family min >=75%
Pair >=80%
Permutation >=95%
K2..8 >=85%
K12..16 >=75%
ONNX parity 100%
です。

100%を目標にsuiteを調整しないでください。

Gate PASSなら
FINAL_ACCEPTANCE_RC2_BLIND_VERIFIED.md
を作り、これを正式なRC2 generalization certificateとしてください。

Gate FAILならそのままFAILとして記録し、
RC2を修正せずユーザーへ報告してください。
改善版はRC2.1/RC3として別モデル・別blind suiteで扱います。
```
