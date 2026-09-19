# ERABI 作業状況

更新日：2026-09-19

## 現在地

- **M0（環境確認・作業基盤）**: 完了。
- **M1（既存モデル推論・全候補確率・基本評価）**: 完了。
- **M1.5（入力経路監査・2モデル×2言語の対照実験・候補順検証）**: 完了。
- **M2.1（小規模追加学習・暗記と未学習問題への改善検証）**: 完了。
- **M3.1（限定評価・確率校正・review固定のローカルAPI）**: 完了。
- **M3.2（正解データの是正・修正効果を分けて測る再学習）**: 完了。
- **M3.3（入力重複・近道偏りの解消・新データセット再構成・W_v2小規模比較）**: 完了（※勾配蓄積の実装不具合があった版）。
- **M3.3追補（指示切替と近道診断の精査・保存済み個票のCPU再集計）**: 完了。
- **M3.4（勾配蓄積除数バグ修正・CPU検証・条件固定の単一再学習W_v2_gradfix・4モデル比較）**: 完了。
- **M3.5（通常CEの学習予算拡大：5→10エポック・同一実行内best_first5保全・ペア切替開花の確認・5モデル同一条件比較）**: 完了。
- **M3.7（校正成果物の生成・照合・API適用の一致、Sidecar Manifest導入、ローカルhash・契約照合厳格化、GF意味状態キー統一、報告訂正、手編集なしの実機API接続確認）**: 完了。
- **M4.1（例外・優先順位ルールの単一CE追加学習・基準版(W_v2_ce10)とのT=1比較・smoke-06回復・旧能力退行記録）**: 完了。
- **M4.2 Phase A（未見ドメイン・新表現プローブ評価・W_v2_ce10 vs W_m4_1比較・Diff両問正解15.0%により停止条件成立・Phase B未着手）**: 完了（Phase A停止）。
- **M4.3-P（優先順位表現多様化・Family E〜J学習・B0から1080件単一CE学習・未見表現M〜PでDiff両問80.0%達成・旧能力高水準保持・3モデル×8セットT=1比較）**: 完了（※game/facilityに意味反転バグがあった旧版）。
- **M4.3.1（表現データセット意味整合性是正・独立自然文バリデータ配備・B0から同一条件再学習W_m4_3p_fix・4モデル×9セットT=1比較・Cell A 97.5%/91.7%・fresh 78.3%/50.0%・Mean NLL 1.4657急減）**: 完了（意味整合性100%・正式代表性能確立）。
- **M4.3.2（汎化ギャップ診断・Train/Dev/Fresh全12Family集計・eval_v2退行9件個票精査・境界反転5件/HP単一ヒューリスティック4件の完全特定・次フェーズとしてRetentionを単一提案）**: 完了（要因特定・非再学習）。
- **M4.4-R（標的型リプレイ・M3 train等号境界48件+複合56件=104件重み付け・B0から1184件単一CE学習・fresh Diff Both 60.0%達成・eval_v2 92.5%で回復せずPattern C判定・停止条件成立）**: 完了（Pattern C特定・大量リプレイ回避）。
- **M4.4.1（セレクタカバレッジ修正・在庫==受注comparison 4組/8件追加・計112件replay・単一CE学習W_m4_4_1r・comparison退行2/5件回復・eval_v2 91.5%・transfer_probe 81.2%へ向上・5モデル比較）**: 完了。
- **Milestone 5（Balanced Core Reasoner・1:1 Task-Balanced Micro-Batch学習・eval_v2 98.0% / fresh phrasing 81.7% / eval_exception 100.0% / smoke 10/12・全Gate突破・W_core_v1としてfreeze）**: **完了（Gate完全通過・W_core_v1保全）**。
- **Milestone 6（Operator Generalization・10主要論理operator多角表現学習・fresh operator 94.0% / pair both 88.0% / 全family 80%以上 / eval_v2 98.0% / eval_exception 100.0% / 全Gate突破・W_operator_v1としてfreeze）**: **完了（Gate完全通過・W_operator_v1保全）**。
- **Milestone 7（Domain & Perturbation Robustness・9ドメイン×6摂動・fresh robustness 100.0% / permutation consistency 100.0% / 全ドメイン100% / eval_v2 97.0% / eval_exception 100.0% / fresh operator 92.0% / 全Gate突破・W_robustness_v1としてfreeze）**: **完了（Gate完全通過・W_robustness_v1保全）**。
- **Milestone 8（General Choice Tasks・一般choiceタスク拡張：routing, NLI, semantic relation, intent, instruction separation, negative goal 全6タスクファミリー・fresh general 100.0% / 各family 100.0% / eval_v2 97.5% / fresh robustness 100.0% / fresh operator 92.0% / 全Gate突破・W_general_v1としてfreeze）**: **完了（Gate完全通過・W_general_v1保全）**。
- **Milestone 9（Calibration・モデル重みfreeze後の独立校正・新規calibration / fresh_calibration_eval分離・T*=0.2560・Accuracy不変・Brier 0.000・p>=0.90誤差0.0%・全Gate突破・calibration.json保全）**: **完了（Gate完全通過・校正結合完了）**。
- **Milestone 10（Release Candidate・ローカルJev型choice engine固定：RC-1.0.0構築・localhost API・1 worker・review既定・全候補確率・raw order保持・fail closed・warm p50=27.7ms / p95=45.4ms・rc_bundle.zip保全）**: **完了（Gate完全通過・RC-1.0.0 freeze）**。
- **Milestone 12（Final Sealed Acceptance・完全未見Sealed Test 120件・全体正答率100.0% / 対照ペア両問100.0% / 順序不変性100.0% / 高信頼度誤差0.0% / 全Gate満額突破・FINAL_ACCEPTANCE_REPORT.md記録）**: **全工程完遂（正式受理）**。
- **Phase A（Final Acceptance Integrity Audit・Freeze Lineage・全過去データ13240件Leakageゼロ・レンダリング自然文意味検証120/120・Raw Logits数学的再計算・Permutation Invariance・FINAL_ACCEPTANCE_VERIFIED.md保全）**: **完了（独立完全合格）**。
- **Phase B（ONNX FP16 Release・ONNX Runtime CUDA FP16最適化・全4評価セット340問でTop1一致率100.0%・p50 11.14ms / p95 11.99ms / 88.5 req/s / 50%容量削減 / 1000回メモリドリフト-1.51MB・release/erabi-rc1-onnx-fp16/保全・テスト78/78件全PASS）**: **完了（正式リリース）**。

---

## 1. M3.3 データ再構成とコード境界修正

詳細は [`runs/m3_3_v2/audit.md`](file:///f:/ai/erabi-local/runs/m3_3_v2/audit.md) を参照。

### 1.1 課題と是正内容
1. **IDではなくモデル入力完全一致による重複排除**:
   - `train`, `dev`, `eval_v2` 間で `context ||| question ||| [choices]` の暗号学的指紋を検査。
   - クロススプリット重複（train <-> dev, train <-> eval_v2, dev <-> eval_v2）: **すべて 0件**。
   - 各 split 内部の重複行数: **0件**（全件一意）。
   - 既存診断セット（smoke 12問, transfer 32問）との重複: **0件**。
2. **境界値問題の偏り（actual == threshold 固定）の解消**:
   - `actual < threshold`, `actual == threshold`, `actual > threshold` を均等配分。
   - 質問キーワードのみで100%解けていたショートカットが、新 `eval_v2` では **25/38 (65.8%)** と変化した。
3. **二属性の順位関係固定（相関固定）の解消**:
   - 属性1と属性2の数値を独立サンプリングし、属性1最良が属性2最良・最悪・中間の全パターンを網羅。
   - 第二属性の数値のみで100%解けていたショートカットが、新 `eval_v2` では **69/100 (69.0%)** と変化した。
4. **コードの最小修正**:
   - `src/erabi/inference.py`: 最上位候補を丸め後確率ではなく、生logits（row_logits）の argmax で決定。
   - `src/erabi/train.py`: dev評価時に `raw_logits` を渡し、通常評価と同一の log-sum-exp NLL を算出。勾配蓄積端数窓の実サンプル数スケーリング。
   - `src/erabi/evaluate.py`: 温度 $T \le 0$ または非有限値の温度を厳格に拒否（ValueError）。
   - `src/erabi/api.py`: `require_calibration=True` かつパス欠落時の起動拒否（RuntimeError）。
   - `pyproject.toml`: fastapi, uvicorn, scipy, httpx を明文化。
   - 単体テスト: 新規5件追加（全40件 PASS）。

---

## 2. 新データセット分布 (`data/m3_3_v2/`)

| Split | 総件数 | グループ数 | 一意な入力指紋数 | 内部重複件数 | trainとの重複 | devとの重複 | eval_v2との重複 | 診断セットとの重複 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `train.jsonl` | 600 | 300 | **600** | **0** | - | **0** | **0** | **0** |
| `dev.jsonl` | 100 | 50 | **100** | **0** | **0** | - | **0** | **0** |
| `eval_v2.jsonl` | 200 | 100 | **200** | **0** | **0** | **0** | - | **0** |

---

## 3. 単一小規模学習（`W_v2`）と3モデル同一条件比較評価

- **再学習条件**:
  - ベースモデル: `B0` (`knowledgator/gliclass-instruct-base-v1.0`)
  - データ: `data/m3_3_v2/train.jsonl` (600件), `dev.jsonl` (100件)
  - パラメータ: lr=2e-5, wd=0.01, micro_batch=2, grad_accum=8, epochs=5, seed=42
  - 最良モデル: Epoch 4 (Dev Acc: 64.0%, Pair: 46.0%, NLL: 0.7361) を [`runs/m3_3_v2/trained/checkpoint`](file:///f:/ai/erabi-local/runs/m3_3_v2/trained/checkpoint) に保存。

### 3.1 3モデル比較サマリー（B0, W_fix, W_v2）

| 評価セット | 指標 | B0 (未学習ベース) | W_fix (M3.2旧データ学習版) | W_v2 (M3.3新データ学習版) | 分析と解釈 |
|---|---|:---:|:---:|:---:|---|
| **eval_v2**<br>(新規評価 200件: 100組) | 正答率<br>NLL<br>Brier<br>全ペア両問<br>（正解が異なる47組）<br>（正解が同一の53組） | 44.5% (89/200)<br>2.2640<br>0.9049<br>19.0% (19/100)<br>3/47 (6.4%)<br>16/53 (30.2%) | 53.0% (106/200)<br>4.1315<br>0.8503<br>27.0% (27/100)<br>14/47 (29.8%)<br>13/53 (24.5%) | **58.5% (117/200)**<br>**0.8224**<br>**0.5187**<br>**36.0% (36/100)**<br>8/47 (17.0%)<br>**28/53 (52.8%)** | W_v2は同一評価でNLL/Brierが比較モデルより低く抑えられた。一方、正解が異なる組の両問正解はW_fixの14/47から8/47へ低下しており、詳細は後述の追補で精査。 |
| **smoke_cases**<br>(12件) | 正答数<br>NLL<br>Brier | 7/12 (58.3%)<br>1.3799<br>0.6261 | 7/12 (58.3%)<br>3.0166<br>0.7579 | **9/12 (75.0%)**<br>**0.8317**<br>**0.4904** | smoke-08（NLI矛盾）とsmoke-11（偽指示無視）がこの入力で回復したと報告されている。 |
| **transfer_probe**<br>(32件: 16組) | 正答数<br>NLL<br>Brier<br>全ペア両問 | 18/32 (56.2%)<br>1.0773<br>0.5793<br>25.0% (4/16) | 23/32 (71.9%)<br>1.6564<br>0.5261<br>50.0% (8/16) | 20/32 (62.5%)<br>**0.7412**<br>**0.4735**<br>43.8% (7/16) | 正答数は20/32だが、NLL/Brierは全モデル中最も低い。 |

---

### 3.2 smoke 12問の個票推移（B0, W_fix, W_v2）

| ID | 正解 | B0 | W_fix | W_v2 | W_fix → W_v2 遷移 |
|---|---|:---:|:---:|:---:|---|
| `smoke-01` (窓口技術) | `technical` | × (billing) | ○ | ○ | 正解維持 |
| `smoke-02` (窓口請求) | `billing` | ○ | ○ | ○ | 正解維持 |
| `smoke-03` (プラン最安) | `a` | × (b) | × (c) | **○ (a)** | 回復 (誤→正) |
| `smoke-04` (プラン最速) | `b` | ○ | ○ | × (a) | 新たな誤答 (正→誤) |
| `smoke-05` (HP回復ルール) | `heal` | × (wait) | × (continue) | **○ (heal)** | 回復 (誤→正) |
| `smoke-06` (移動継続ルール) | `continue` | ○ | ○ | × (heal) | 新たな誤答 (正→誤) |
| `smoke-07` (NLI支持) | `supports` | × (contradicts) | ○ | ○ | 正解維持 |
| `smoke-08` (NLI矛盾) | `contradicts` | ○ | × (supports) | **○ (contradicts)** | 回復 (smoke-08) |
| `smoke-09` (NLI不明) | `unknown` | × (contradicts) | × (supports) | × (supports) | 未解決 |
| `smoke-10` (意図抽出) | `exchange` | ○ | ○ | ○ | 正解維持 |
| `smoke-11` (偽指示インジェクション) | `cold` | ○ | × (hot) | **○ (cold)** | 回復 (smoke-11) |
| `smoke-12` (荷物境界値) | `normal` | ○ | ○ | ○ | 正解維持 |

---

## 4. M3.3 追補：指示切替ペアと近道診断の精査結果

詳細は [`runs/m3_3_v2/followup/notes.md`](file:///f:/ai/erabi-local/runs/m3_3_v2/followup/notes.md) および [`runs/m3_3_v2/followup/diagnostic_summary.json`](file:///f:/ai/erabi-local/runs/m3_3_v2/followup/diagnostic_summary.json) を参照。

### 4.1 正解が異なる47組における失敗パターンの分解
W_fix（14/47）からW_v2（8/47）への両問正解減少（-6組）の要因：
- **失敗パターンの分類**:
  - W_v2の失敗39組中、**34組（87.2%）は「予測が切り替わらない失敗（同一候補を予測）」**。
  - 「予測は切り替わるが正しくない失敗」はわずか **5組（12.8%）**。
- **悪化系統の局所化**:
  - `goal_following`（31組中、両問正解が 5組 → 1組 へ退行）：25組で同一候補を予測。
  - `composite_logic`（7組中、両問正解が 3組 → 0組 へ退行）：全7組で同一候補（heal）を予測。
  - `boundary`（6組）：**6組中6組で両問正解（6/6）を完全維持**（退行0組）。
  - `comparison`（3組）：W_fix 0組 → W_v2 **1組へ回復**。
- **結論**: W_v2の失敗の本質は複雑な推論ミスではなく、「指示文の切替に対する感度が不足し、文脈の語彙バイアスに引きずられて同一候補を返してしまうこと」である。

### 4.2 近道診断（69.0% / 65.8%）の数学的実態
- **第2属性診断（69.0%）の分解**:
  - 第2属性を尋ねた問題（case2, 50問）: **50/50（100.0%）正解**。第2属性の最適化方向はすべてminであるため、これは正規の正当解法。
  - 第1属性を尋ねた問題（case1, 50問）: **19/50（38.0%）正解**。3選択肢の完全独立シャッフルにおける偶然一致理論値（33.3%）に整合。
  - したがって、全体で69.0%となったのは正常解法50問と偶然一致19問の合算であり、近道依存の証拠ではない。
- **境界キーワード診断（65.8%）の分解**:
  - `actual < threshold`（12問）: 6/12（50.0%）正解。
  - `actual == threshold`（12問）: 12/12（100.0%）正解。
  - `actual > threshold`（14問）: 7/14（50.0%）正解。
  - 合計 25/38（65.8%）。これは均等3状態サンプリングに対するキーワード規則の数学的期待値（4/6 = 66.7%）と完全に一致する。

### 4.3 一様分布基準と信頼度帯
- eval_v2（2択100問、3択100問）の一様分布基準: 期待正答率 41.7%, NLL 0.8959, Brier 0.5833。
- W_v2は正答率 58.5%、NLL 0.8224、Brier 0.5187 と一様分布を有意に上回る。
- 確信度帯別では、$p_{max} \ge 0.90$ の領域（45件）において正答率 **91.1%（41/45）** を記録した。ただし 0.70〜0.90 帯（19件）で 36.8% の落ち込みがあり、サンプル規模（200問）の制約から完全校正とは見なせない。

---

## 5. M3.4 勾配蓄積修正とW_v2_gradfix比較結果

詳細は [`runs/m3_4_gradfix/notes.md`](file:///f:/ai/erabi-local/runs/m3_4_gradfix/notes.md) および [`runs/m3_4_gradfix/comparisons/comparisons_summary.json`](file:///f:/ai/erabi-local/runs/m3_4_gradfix/comparisons/comparisons_summary.json) を参照。

### 5.1 勾配蓄積除数バグの是正とCPU検証
- **不具合**: `src/erabi/train.py` において、勾配蓄積の除数が「ウィンドウ内の残りマイクロバッチ数（8, 7, ..., 1）」となっており、後半のミニバッチほど損失が過大評価される歪みが生じていた。
- **是正**: 各ミニバッチの平均損失に対し、`(len(batch_records) / window_sample_count)` で重み付けする正確な平均勾配計算へ修正。
- **CPU検証 (`runs/m3_4_gradfix/gradient_check.json`)**:
  - 通常16件 (2x8)、端数8件 (2x4)、奇数端数15件 (2x7+1x1)、複数ウィンドウ23件 (16+7)、accum=1 の全5条件で、一括平均勾配との最大誤差が $10^{-8}$ 未満で完全一致することを確認。

### 5.2 条件完全固定での単一再学習 (`W_v2_gradfix`)
- 元B0 (`knowledgator/gliclass-instruct-base-v1.0`)、データ `data/m3_3_v2` (train 600件, dev 100件)、lr=2e-5, epochs=5, seed=42, accum=8。
- 1epochあたり38更新、計190 updates。
- 最良エポック: **Epoch 5 (Dev Acc: 80.00%, Dev Pair: 62.00% (31/50), NLL: 0.3778)**。
  - ※ W_v2（Dev Acc 64.0%, Pair 46.0%, NLL 0.7361）から大幅に改善。

---

## 6. M3.5 通常CE学習予算拡大（5→10エポック）と指示切替の開花

詳細は [`runs/m3_5_ce10/notes.md`](file:///f:/ai/erabi-local/runs/m3_5_ce10/notes.md) および [`runs/m3_5_ce10/comparisons/comparisons_summary.json`](file:///f:/ai/erabi-local/runs/m3_5_ce10/comparisons/comparisons_summary.json) を参照。

### 6.1 背景と実験条件
- **目的**: 対照学習やペア損失などの構造的追加を行う前に、通常CEのまま学習予算（エポック数）を 5 → 10 へ拡大し、指示切替（goal_following）の習得が単なる更新ステップ数不足によるものかを検証。
- **前提と条件**:
  - ベースモデル: 元B0 (`knowledgator/gliclass-instruct-base-v1.0`、ローカルキャッシュ重み)
  - データ: `data/m3_3_v2/train.jsonl` (600件), `dev.jsonl` (100件), `eval_v2.jsonl` (200件)
  - 学習ハイパーパラメータ: lr=2e-5, wd=0.01, micro=2, accum=8, seed=42（**変更したのは epochs=10 のみ**）。
  - 総更新ステップ数: 38 updates/epoch × 10 = 380 updates。
- **同一実行内でのチェックポイント保全**:
  - `checkpoint_best_first5`: エポック1〜5の範囲で最良（Epoch 5）。
    - 重み `model.safetensors` SHA256: `631a6d8a6084...` -> **M3.4の W_v2_gradfix とバイト単位で完全一致（True）**。
  - `checkpoint` (全体最良 `W_v2_ce10`): エポック1〜10の範囲で最良（Epoch 10）。
    - 重み `model.safetensors` SHA256: `6c9cac061079...`

### 6.2 Train / Dev における切替の劇的開花
- **Dev セット（100件: 50組）の推移**:
  - エポック1〜5: Dev Acc 52%〜80%、異なる正解24組の両問正解は 0〜5組、うち `goal_following` (19組) は **0/19 (0.0%) のまま推移**。
  - エポック6: Dev Acc 90.0%、`goal_following` が **12/19** へ急上昇。
  - エポック7〜10: エポック7で **19/19 (100% 満点)** に到達。エポック10で Dev Acc 99.0%, Dev NLL 0.0291, 異なる正解 24/24 (100%)。
- **事前/事後 train/dev 診断 (`diag_train_dev.py`)**:
  - **Train (600件)**:
    - W_v2_gradfix (5ep): 正答率 83.8%, 異なる正解 56/147, goal_following 10/97 (10.3%)
    - W_v2_ce10 (10ep): 正答率 **99.5%**, 異なる正解 **147/147 (100.0%)**, goal_following **97/97 (100.0%)**
  - **Dev (100件)**:
    - W_v2_gradfix (5ep): 正答率 80.0%, 異なる正解 5/24, goal_following 0/19 (0.0%)
    - W_v2_ce10 (10ep): 正答率 **99.0%**, 異なる正解 **24/24 (100.0%)**, goal_following **19/19 (100.0%)**
- **結論**: 通常CEで指示切替が学習できなかった原因は「対照学習の欠如」ではなく、「5エポック（190 updates）では語彙バイアスを脱して指示文の属性切替へ注意を向ける更新回数が不足していたこと」であった。

### 6.3 smoke-11 個票照合と訂正（維持ではなく回復）
- M3.5報告で「維持」と記載されていた `smoke-11` は、保存個票の照合により 5ep (`hot`, False) → 10ep (`cold`, True) の **正解回復** であると訂正。
- smoke 12問推移: 5epの 8問正解 + 回復2問 (04, 11) - 退行1問 (08) = **9問正解**（8+2-1=9で完全整合）。

### 6.4 5モデル同一条件比較サマリー

| 評価セット | 指標 | B0 (未学習) | W_fix (旧データ) | W_v2 (勾配バグ版) | W_v2_gradfix (5ep) | W_v2_ce10 (10ep) |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **eval_v2**<br>(新規評価 200問: 100組) | 正解数 (正答率)<br>Mean NLL<br>Mean Brier<br>全ペア両問正解<br>・正解が異なる47組<br>・正解が同一の53組 | 89/200 (44.5%)<br>2.2640<br>0.9049<br>19/100 (19.0%)<br>3/47 (6.4%)<br>16/53 (30.2%) | 106/200 (53.0%)<br>4.1315<br>0.8503<br>27/100 (27.0%)<br>14/47 (29.8%)<br>13/53 (24.5%) | 117/200 (58.5%)<br>0.8224<br>0.5187<br>36/100 (36.0%)<br>8/47 (17.0%)<br>28/53 (52.8%) | 162/200 (81.0%)<br>0.4761<br>0.2755<br>64/100 (64.0%)<br>12/47 (25.5%)<br>52/53 (98.1%) | **195/200 (97.5%)**<br>**0.1538**<br>**0.0484**<br>**95/100 (95.0%)**<br>**43/47 (91.5%)**<br>**52/53 (98.1%)** |
| **transfer_probe**<br>(32問: 16組) | 正解数 (正答率)<br>Mean NLL<br>Mean Brier | 18/32 (56.2%)<br>1.0773<br>0.5793 | 23/32 (71.9%)<br>1.6564<br>0.5261 | 20/32 (62.5%)<br>0.7412<br>0.4735 | **25/32 (78.1%)**<br>**0.6738**<br>**0.3875** | **25/32 (78.1%)**<br>1.6239<br>0.4754 |
| **smoke_cases**<br>(12問) | 正解数 (正答率)<br>Mean NLL<br>Mean Brier | 7/12 (58.3%)<br>1.3799<br>0.6261 | 7/12 (58.3%)<br>3.0166<br>0.7579 | 9/12 (75.0%)<br>0.8317<br>0.4904 | 8/12 (66.7%)<br>1.5148<br>0.4985 | **9/12 (75.0%)**<br>2.1239<br>0.4902 |

### 6.5 正解が異なる47組における切替成績（タスク別）

| タスク系統 | 組数 | W_v2_gradfix (5ep) | W_v2_ce10 (10ep) | 失敗の内訳 (W_v2_ce10) |
|---|---:|:---:|:---:|---|
| **`goal_following`** | 31 | 3 / 31 (未切替: 28) | **31 / 31 (100.0% 満点！)** | **未切替 0組（完全解消）** |
| **`explicit_rule:composite_logic`** | 7 | 3 / 7 (未切替: 4) | **4 / 7** | 未切替 3組 (er-0003, er-0025, er-0087) |
| **`explicit_rule:comparison`** | 3 | 0 / 3 (未切替: 3) | **2 / 3** | 未切替 1組 (er-0009: 等値境界) |
| **`explicit_rule:boundary`** | 6 | 6 / 6 (満点) | **6 / 6 (満点維持)** | 未切替 0組 |
| **合計** | 47 | 12 / 47 (25.5%) | **43 / 47 (91.5%)** | **未切替失敗は 35組 → 4組 へ激減** |

- 正解が同一の53組でも、不必要な切替は発生せず **52/53 (98.1%)** を維持。

### 6.5 補助集計（構造共有22問を除いた178問）と残存トレードオフ
- **構造共有22問を除外した178問**:
  - 正答率: 144/178 (80.9%) -> **176/178 (98.9%)**
  - Mean NLL: 0.4676 -> **0.0529**
  - 正解が異なる39組の両問正解: 8/39 (20.5%) -> **38/39 (97.4%)**
  - 未切替失敗: 31組 -> **1組**
- **残存トレードオフ**:
  - `transfer_probe` において正答数は 25/32 (78.1%) を維持しているが、Mean NLL は 0.6738 → 1.6239 へ上昇。モデルの確信度過多（overconfidence）が発生している。
  - `smoke_cases` では smoke-04, 11 が回復した一方、smoke-08（NLI矛盾）が誤答となり、ゼロショット理解の一部にトレードオフが残る。

---

## 7. M3.6 重み固定・限定用途の確率校正と新規評価

詳細は [`runs/m3_6_calibration/notes.md`](file:///f:/ai/erabi-local/runs/m3_6_calibration/notes.md) および [`runs/m3_6_calibration/summary_report.json`](file:///f:/ai/erabi-local/runs/m3_6_calibration/summary_report.json) を参照。

### 7.1 新規データセット分離生成 (`data/m3_6_cal/`)
- 合成ルール判断（goal_following, explicit_rule）の限定用途として新規2集合を構築。
- `calibration.jsonl`: 200問 / 100組 (SHA256: `9b2338c57f39...`)
- `fresh_eval.jsonl`: 200問 / 100組 (SHA256: `ddd2be564dc8...`)
- **完全分離の検証**:
  - 入力指紋（context + question + ordered choices）の既存（train 600, dev 100, eval_v2 200, smoke 12, transfer 32）および相互間の重複: **完全 0件**。
  - 生成元の意味状態（HP/閾値/アイテム、測定値/閾値、在庫/受注、ドメイン/数値組）の重複: **完全 0件**。
  - 数学的正解検証: 全400問でプログラム検証合格。

### 7.2 単一温度 $T$ の推定と fresh_eval 検証
- W_v2_ce10 の全候補生logitsを取得し、calibration の NLL 最小化（$0.05 \le T \le 20.0$, Float64）で推定：
  - **最適温度 $T = 3.1097$** (初期 NLL 0.3436 → 最適 NLL 0.1572, evals=12, 境界外)。
- **fresh_eval（未知200問 / 100組）での校正効果**:
  - 正答率: 94.0% (188/200), ペア両問正解: 88.0% (88/100), 異なる正解51組の両問正解: 80.4% (41/51)（正の温度のため不変）。
  - **Mean NLL**: $0.3489 \to \mathbf{0.1675}$ (**-0.1814 の大幅改善**)。
    - 2択: $0.2964 \to 0.1376$, 3択: $0.4015 \to 0.1975$
  - **Mean Brier**: $0.1179 \to \mathbf{0.0957}$ (**-0.0222 の改善**)。
    - 2択: $0.0970 \to 0.0803$, 3択: $0.1389 \to 0.1111$
  - **確信度帯の改善**:
    - $T=1.0$ では 197問が $[0.9, 1.0)$ に偏り（平均確信度 99.8% に対し実精度 94.4% と過信）。
    - Calibrated $T$ では、$[0.9, 1.0)$ が 168問（平均確信度 97.9%, 実正答率 **97.6%**）とほぼ完全一致し、$[0.7, 0.9)$ に 27問（確信度 83.6%, 精度 77.8%）と綺麗に分散。過信が解消された。

### 7.3 既存診断セット（別枠集計）への同一温度の適用

| 評価セット | 指標 | 未校正 ($T=1.0$) | 校正後 ($T=3.1097$) | 差分 / 解釈 |
|---|---|:---:|:---:|---|
| **eval_v2**<br>(既知評価 200問) | 正答率<br>Mean NLL<br>Mean Brier | 97.5% (195/200)<br>0.1538<br>0.0484 | 97.5% (195/200)<br>**0.0880**<br>**0.0465** | NLL -0.0658, Brier -0.0019。<br>合成ルール領域での良好な校正効果を確認。 |
| **smoke_cases**<br>(12問) | 正答数<br>Mean NLL<br>Mean Brier | 9/12 (75.0%)<br>2.1239<br>0.4902 | 9/12 (75.0%)<br>**0.9413**<br>**0.4245** | NLL -1.1826, Brier -0.0657。<br>極端なペナルティが平滑化。 |
| **transfer_probe**<br>(32問) | 正答数<br>Mean NLL<br>Mean Brier | 25/32 (78.1%)<br>1.6239<br>0.4754 | 25/32 (78.1%)<br>**0.7705**<br>**0.4470** | NLL -0.8534, Brier -0.0284。<br>※ 確信度の平滑化によるNLL縮小であり、誤答判断自体は未解決。 |

- **校正の限界**:
  - `transfer_probe` の NLL は低下したものの、モデルが否定ゴールや逆転ゴールを誤答する本質的なエラーは解決していない。
  - したがって、温度 $T=3.1097$ の適用対象は情報が本文に明示された**合成ルール判断問題に限定**される。

### 7.4 採否判定とAPI接続確認
- **採否**: fresh_eval で NLL が低下し Brier も悪化しないため、§6.1 基準に基づき **`ACCEPT_SCOPED`（合成ルール限定用途の校正候補として採用）**。[`runs/m3_6_calibration/calibration.json`](file:///f:/ai/erabi-local/runs/m3_6_calibration/calibration.json) を保存。
- **API接続確認**: loopback (`127.0.0.1:8765`), 1 worker, reloadなし, HF_HUB_OFFLINE=1 で起動確認。
  - `GET /health` 正常（`calibration.status: applied`, `temperature: 3.1097`）。
  - サンプル推論2件（GF, ER境界）で `decision.status: review` を維持し、確率正規化を確認。プロセスはクリーンに停止完了。

---

## 8. レビューバンドル情報

- **M3.3初期版**: [`runs/m3_3_v2/review_bundle.zip`](file:///f:/ai/erabi-local/runs/m3_3_v2/review_bundle.zip)（約144KB / 40ファイル、保持）
- **M3.3追補版**: [`runs/m3_3_v2/review_bundle_followup.zip`](file:///f:/ai/erabi-local/runs/m3_3_v2/review_bundle_followup.zip)（約183KB / 44ファイル、保持）
- **M3.4勾配修正版**: [`runs/m3_4_gradfix/review_bundle.zip`](file:///f:/ai/erabi-local/runs/m3_4_gradfix/review_bundle.zip)（約186KB / 45ファイル、保持）
- **M3.5学習予算拡大版**: [`runs/m3_5_ce10/review_bundle.zip`](file:///f:/ai/erabi-local/runs/m3_5_ce10/review_bundle.zip)（約127KB / 40ファイル、保持）
- **M3.6校正・新規評価版**: [`runs/m3_6_calibration/review_bundle.zip`](file:///f:/ai/erabi-local/runs/m3_6_calibration/review_bundle.zip)
  - M3.6新規データセット（calibration, fresh_eval, manifest）、全生logits、温度校正アーティファクト、fresh_evalおよび診断3セットの詳細評価結果、API接続ログ、notes.md、最新STATUS.mdを収録。
  - 重みバイナリ、.venv、HFキャッシュ、秘密情報は除外。
---

## 8. M3.7 校正成果物の生成・照合・API適用の手編集なしハンドオフ

詳細は [`runs/m3_7_calibration_handoff/notes.md`](file:///f:/ai/erabi-local/runs/m3_7_calibration_handoff/notes.md) および [`runs/m3_7_calibration_handoff/migration_notes.md`](file:///f:/ai/erabi-local/runs/m3_7_calibration_handoff/migration_notes.md) を参照。

### 8.1 不整合の解消と契約の厳格化
1. **Runtime状態名と限定採用スコープの分離**:
   - スクリプト作成側の `applied_scoped` と API側の `applied` の不一致を解消。
   - runtime状態は `status="applied"` を維持し、限定範囲は `adoption.decision = "ACCEPT_SCOPED"` および `contract.scope` へ分離。手編集なしでAPIへ直結可能に是正。
2. **ローカルチェックポイント・ファイルハッシュ・契約照合**:
   - `load_and_verify_calibration` において、存在しないモデルパスの拒否、必須ファイル（`model.safetensors`, `config.json` 等）の存在確認とSHA256照合、契約照合（`schema_version="1"`, `max_tokens=512`, `formatter_version="m1_instruct_pipe_v1"`, `precision`）を厳格化。
3. **保存logitsの出所管理（Sidecar Manifest）**:
   - `raw_logits_*.jsonl` に暗号学的 sidecar manifest (`.manifest.json`) を導入。
   - モデルチェックポイント各ファイルハッシュ、入力データSHA256、件数、入力整形契約を記録し、不一致時の再利用を拒否。
4. **GF意味状態キーの統一と全データ再監査**:
   - ドメイン・属性値ペア（ソート済みタプル）による canonical key に統一。文脈中の出現順序に依存しない順序不変性を保証。
   - 全データセット（train, dev, eval_v2, calibration, fresh_eval, smoke, transfer）の監査を実施し、未対応件数（smoke: 8/12, transfer: 32/32）を正確に明記。新規合成スプリット（calib, fresh_eval）の重複は **完全 0件** を確認。
5. **集計の報告訂正**:
   - smoke 正解推移: 正解維持 7件、回復 2件 (`smoke-04`, `smoke-11`)、退行 1件 (`smoke-08`)、継続誤答 2件 (`smoke-06`, `smoke-09`)、最終正解 9/12。
   - 最適温度ステータス: 探索範囲 $[0.05, 20.0]$ の「内部・境界非到達（inside_bounds_not_reached）」。
   - 非ペアの smoke について `pair_stats` を `null` に設定。
   - 選択肢数集計において 4択を3択欄へ入れず、独立集計へ分離。

### 8.2 手編集なしでの実機API接続確認
- 実行スクリプト: [`scripts/verify_m3_7_api.py`](file:///f:/ai/erabi-local/scripts/verify_m3_7_api.py)
- 起動条件: 127.0.0.1:8765, 1 worker, reloadなし, `--require-calibration`, `HF_HUB_OFFLINE=1`。
- 結果:
  - `GET /health`: 7.53秒で HEALTHY（`status: ok`, `temperature: 3.1097`, `calibration.status: applied`, `artifact_id: calib-m3-7-scoped-w-v2-ce10`, `decision_policy: review_default`）。
  - 推論3問（GF, ER境界, ER複合論理）を実行し、生logitsの $\text{softmax}(z/T)$ との完全一致（最大誤差 $10^{-17}$）、$T=1$ や $T^2$ との不一致を確認し、**単一温度の確実な適用（二重適用なし）**を実証。
  - 全問で `decision.status="review"` を確認。
  - サーバープロセスはクリーンに停止。

---

## 9. M4.1 例外・優先順位（Exception Priority）実験

詳細は [`runs/m4_1_exception/notes.md`](file:///f:/ai/erabi-local/runs/m4_1_exception/notes.md) および [`runs/m4_1_exception/summary_report.json`](file:///f:/ai/erabi-local/runs/m4_1_exception/summary_report.json) を参照。

### 9.1 背景とデータセット
- **課題**: M3基準版（W_v2_ce10）は合成ルールで97.5%に達したが、`smoke-06` に代表される「一般ルールと例外・優先順位ルールの衝突」において、指示文の優先順位（①最優先 ②次点）を解釈できず誤答していた。
- **データ設計 (`data/m4_1_exception/`)**:
  - 5ドメイン（ゲーム行動、配送便、システム運用、窓口対応、設備制御）で構成。
  - 優先順位を入替えると正解が変わる組（diff_target_pairs）と同一の組（same_target_pairs）を半々で配分。
  - `train_exception.jsonl` (240件), `dev_exception.jsonl` (40件), `eval_exception.jsonl` (120件)。
  - 過去データ（1344件）およびスプリット間の指紋・意味状態重複は **完全 0件** を検証済み。
- **実スプリット分布の訂正**:
  - 生成時の重複回避rejectにより、実ファイル分布は dev: conflict 12 / nonconflict 8、eval: conflict 37 / nonconflict 23 となっている。M4.1の評価集計（正解が異なる37組 / 同一23組）はこの実分布に完全一致している。データ・評価は再生成せず、設計説明を実数へ訂正。
- **基準版の初期実測**:
  - `eval_exception` (120件): 正答率 **32.5%** (39/120)、ペア両問正解 **5.0%** (3/60)、**Diff Target Pairs: 0/37 (0.0% !!)**。
  - 改善余地が極めて巨大であることを確認。

### 9.2 単一追加学習（W_m4_1）と結果
- **条件**: 新しい損失やモデル構造は追加せず、通常CEで1回のみ学習。
  - データ: 既存train 600件 + train_exception 240件 = 840件。
  - 元ベース（B0）から lr=2e-5, epochs=10, micro=2, accum=8 で学習。Epoch 9 (Dev Acc 99.3%, Dev Pair 98.6%) を採用。
- **基準版 (W_v2_ce10) vs 実験版 (W_m4_1) 同一条件（T=1.0）比較**:
  1. **新規例外評価 (`eval_exception` 120件: 60組)**:
     - 正答率: 32.5% (39/120) $\to$ **99.2% (119/120)** (+66.7pt)
     - 全ペア両問正解: 5.0% (3/60) $\to$ **98.3% (59/60)** (+93.3pt)
     - **Diff Target Pairs: 0/37 (0.0%) $\to$ 37/37 (100.0% 満点！)**
     - Mean NLL: 4.4741 $\to$ **0.0211**、Mean Brier: 1.1573 $\to$ **0.0140**
  2. **smoke 12問 (`smoke_cases`)**:
     - 正答数: 9/12 (75.0%) $\to$ **12/12 (100.0% 満点達成！)**
     - 正解維持: 9件
     - **回復: 3件** (`smoke-06` 移動例外, `smoke-08` NLI矛盾, `smoke-09` NLI中立)
     - 退行: **0件**
     - ※ M3最大の未解決課題であった `smoke-06` が正解 `continue` へ完全に回復。
  3. **旧能力の退行検査**:
     - `eval_v2` (M3合成ルール 200件): 97.5% (195/200) $\to$ **97.0% (194/200)**（わずか1問差で高水準を完全維持）。
     - `transfer_probe` (転用プローブ 32件): 78.1% (25/32) $\to$ **62.5% (20/32)**（-5問純減: 18維持, 2回復, 7退行, 5両者誤答。構文特化によるドメイン外否定・逆転プロンプトへのトレードオフを正直に記録）。

---

## 10. M4.2 Phase A 未見優先順位表現プローブ評価結果

詳細は [`runs/m4_2_robustness/notes.md`](file:///f:/ai/erabi-local/runs/m4_2_robustness/notes.md) および [`runs/m4_2_robustness/phase_a/phase_a_summary.json`](file:///f:/ai/erabi-local/runs/m4_2_robustness/phase_a/phase_a_summary.json) を参照。

### 10.1 背景とデータセット (`data/m4_2_robustness/novel_priority_eval.jsonl`)
- **目的**: M4.1の `eval_exception` 99.2% が「未知のドメイン・新優先順位表現」へ一般化（転用）しているかを検証。
- **データ設計**:
  - 4新ドメイン（`manufacturing`, `facility_power`, `inventory`, `job_scheduler`）× 4表現family（通常はA/ただしB、同時成立時のみB優先、優先度B>A、第一判断A/例外B上書き）。
  - 各ドメイン quota 事前固定: conflict 10組 (20件), single 3組 (6件), fallback 2組 (4件) = 15組 (30件)。
  - 全体 60組 (120件): Diff-Target 40組 (80件), Same-Target 20組 (40件)。
  - 過去全データ（1744件）との入力指紋重複: **完全 0件**。学習には絶対に使用しない。

### 10.2 評価実測結果 ($T = 1.0$)

| 評価指標 | 基準版 (`W_v2_ce10`) | 実験版 (`W_m4_1`) | 差分 / 判定 |
|---|:---:|:---:|---|
| **全体正答率** | 41.7% (50/120) | 46.7% (56/120) | +5.0pt |
| **全ペア両問正解** | 20.0% (12/60) | 20.0% (12/60) | ±0.0pt |
| **Diff-Target 両問正解 (40組)** | **12.5% (5/40)** | **15.0% (6/40)** | **+2.5pt (1組増のみ)** |
| **Same-Target 両問正解 (20組)** | 35.0% (7/20) | 30.0% (6/20) | -5.0pt |
| **Mean NLL** | 2.1155 | **7.0699** | +4.9544 (誤答への過信) |
| **Mean Brier** | 0.9105 | 0.9888 | +0.0783 |

### 10.3 失敗要因の分析と Phase A 停止判定
- **失敗パターンの分解**:
  - Diff-Target 40組中、未正解34組の内訳は **未切替（同一候補を固定出力）が 31組 (91.2% / 全体の77.5%)**。
  - 文脈中のアラート・検疫・キズ等の単語に注意が固定され、新構文の優先順位指示を解釈できていない。
- **停止判定**:
  - `W_m4_1` の Diff-Target 両問正解率: **15.0% (6/40)**。
  - 設計基準 **60.0% 未満** のため、**Phase A 停止条件が成立**。
  - 指示書 §7 およびユーザー指示に基づき、**Phase B（汎用保持データ混合学習）へは進まず停止**。
  - 課題を**「優先順位概念の表現転用不足（固定構文への過適合）」**として確定・報告。

---

## 11. M4.2.1 要因分離（Domain × Phrasing 2×2 診断）実測結果

詳細は [`runs/m4_2_1_diagnostic/notes.md`](file:///f:/ai/erabi-local/runs/m4_2_1_diagnostic/notes.md) および [`runs/m4_2_1_diagnostic/diagnostic_summary.json`](file:///f:/ai/erabi-local/runs/m4_2_1_diagnostic/diagnostic_summary.json) を参照。

### 11.1 背景と設計
- **課題**: M4.2 Phase Aの15%という結果について、「ドメイン語彙」「優先順位表現形式」「その相互作用」のどれが主因かを再学習なしの2×2要因配置で切り分けた。
- **4セル構成（各20組 / 40件: conflict 12組, single 5組, fallback 3組）**:
  - **Cell A**: OLD Domain (既知5種) × OLD Phrasing (`①【最優先】...`)
  - **Cell B**: OLD Domain (既知5種) × NEW Phrasing (Family A〜D)
  - **Cell C**: NEW Domain (新4種) × OLD Phrasing (`①【最優先】...`)
  - **Cell D**: NEW Domain (新4種) × NEW Phrasing (Family A〜D, Phase A matched 20組)
- **入力重複**: 過去全データ（1864件）および新セル間との入力指紋重複は **完全 0件**。

### 11.2 2×2 実測結果対照表 ($T = 1.0$)

| Cell | Domain | Phrasing | 基準版 (`W_v2_ce10`)<br>Diff Both | 実験版 (`W_m4_1`)<br>Diff Both | 実験版 (`W_m4_1`)<br>未切替率 (Unswitched) | 実験版 (`W_m4_1`)<br>Mean NLL |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Cell A** | **OLD** | **OLD** | 0/12 (0.0%) | **6/12 (50.0%)** | 1/12 (8.3%) | 5.4731 |
| **Cell B** | **OLD** | **NEW** | 0/12 (0.0%) | **0/12 (0.0%)** | **7/12 (58.3%)** | 7.6551 |
| **Cell C** | **NEW** | **OLD** | 1/12 (8.3%) | **9/12 (75.0%)** | 3/12 (25.0%) | 7.1343 |
| **Cell D (matched)** | **NEW** | **NEW** | 1/12 (8.3%) | **2/12 (16.7%)** | **10/12 (83.3%)** | 9.2194 |
| *Cell D (full 40組)* | *NEW* | *NEW* | 5/40 (12.5%) | *6/40 (15.0%)* | *31/40 (77.5%)* | 7.0699 |

### 11.3 要因診断の結論（Pattern 1 の特定）
- **判定**: **Pattern 1（Bだけ0%に急落、Cは75%と極めて高い）** に該当。
- **知見1（新ドメインへの転用成功）**:
  未学習の4ドメイン（製造品質・電力制御・倉庫在庫・ジョブスケジューラ）であっても、見慣れた表現形式（`①【最優先】...`）であれば、`W_m4_1` は **75.0% (9/12)** の Diff-Target 両問正解を達成した。モデルはドメイン語彙に対しては十分な汎化性能を持っている。
- **知見2（表現変更への完全崩壊）**:
  見慣れたドメイン（ゲーム行動や配送便）であっても、表現形式が Family A〜D に変わった途端、Diff-Target 両問正解率は **0.0% (0/12)** へ完全崩壊した。
- **結論**: Phase Aの失敗（15%）の主因は「新ドメイン語彙」ではなく、**「優先順位表現の固定構文依存（表現脆弱性）」** であると確定。

---

## 12. M4.3-P 優先順位表現多様化（Priority Phrasing Diversification）実測結果

詳細は [`runs/m4_3_phrasing/notes.md`](file:///f:/ai/erabi-local/runs/m4_3_phrasing/notes.md) および [`runs/m4_3_phrasing/summary_report.json`](file:///f:/ai/erabi-local/runs/m4_3_phrasing/summary_report.json) を参照。

### 12.1 背景・設計・データ分離
- **課題**: M4.2.1で特定された「固定構文依存（表現が変わると0%へ急落）」を解消するため、意味的な優先関係を捉える多様な表現Familyを設計・導入。
- **表現Familyの厳格な分離**:
  - **Historical Benchmark (評価専用)**: Family A〜D（M4.2過去評価資産、学習・devには一切不使用）
  - **Train Phrasing Families (学習専用)**: Family E, F, G, H, I, J（6 Families, 各20組/40件: 計120組/240件）
  - **Dev Phrasing Families (選定専用)**: Family K, L（2 Families, 各20組/40件: 計40組/80件）
  - **Fresh Phrasing Eval Families (未見評価専用)**: Family M, N, O, P（4 Families, 各15組/30件: 計60組/120件）
- **ドメインと表現の直交化**: 既知4ドメイン + 新規4ドメインを各Familyに均等配分。
- **均衡quota**: Conflict/Diff 50%, Single 30%, Fallback 20%、A_over_B 50% / B_over_A 50% を事前quota固定。
- **入力重複**: 過去全データ（1984件）および新split間との入力指紋重複は **完全 0件**。

### 12.2 単一CE学習プロセス（B0から一括学習）
- **学習データ**: `data/m4_3_phrasing/combined_train.jsonl` (1080件: M3 600 + M4.1 240 + M4.3 240)
- **開発データ**: `data/m4_3_phrasing/combined_dev.jsonl` (220件: M3 100 + M4.1 40 + M4.3 80)
- **ベースモデル**: `B0` (`knowledgator/gliclass-instruct-base-v1.0`)
- **ハイパーパラメータ**: lr=2e-5, wd=0.01, micro=2, accum=8, epochs=10, seed=42
- **チェックポイント選定**: Epoch 8（M3 Dev: 100.0%, M4.1 Dev: 100.0%, Phrasing Dev Diff Both: 7/20 = 35.0% で選定基準を最大充足）を `runs/m4_3_phrasing/trained/checkpoint` に保存。

### 12.3 3モデル × 8評価セット総合対照表（すべて $T = 1.0$）

| 評価セット | 主要指標 | 基準版 (`W_v2_ce10`) | M4.1版 (`W_m4_1`) | 実験版 (`W_m4_3p`) | 判定 / 改善効果 |
|---|---|:---:|:---:|:---:|---|
| **1. fresh_phrasing_eval**<br>(最重要・未見Family M〜P<br>120件: 60組) | 正答率<br>**Diff-Target Both**<br>・未切替 (Unswitched)<br>・切替誤 (Switched Wrong)<br>Same-Target Both<br>Mean NLL | 53.3% (64/120)<br>**10.0% (3/30)**<br>80.0% (24/30)<br>10.0% (3/30)<br>56.7% (17/30)<br>1.7287 | 48.3% (58/120)<br>**0.0% (0/30)**<br>**96.7% (29/30)**<br>3.3% (1/30)<br>46.7% (14/30)<br>8.6224 | **85.8% (103/120)**<br>**80.0% (24/30)**<br>**20.0% (6/30)**<br>**0.0% (0/30)**<br>**76.7% (23/30)**<br>**1.3210** | **+80.0pt (劇的突破！)**<br>目標 >= 60% を大幅達成<br>固定構文過適合が完全解消<br>未切替率 96.7% → 20.0%<br>NLL 8.62 → 1.32 急減 |
| **2. novel_priority_eval**<br>(Historical Family A〜D<br>120件: 60組) | 正答率<br>**Diff-Target Both**<br>・未切替 (Unswitched)<br>Mean NLL | 41.7% (50/120)<br>12.5% (5/40)<br>62.5% (25/40)<br>2.1155 | 46.7% (56/120)<br>**15.0% (6/40)**<br>77.5% (31/40)<br>7.0699 | **70.0% (84/120)**<br>**45.0% (18/40)**<br>**45.0% (18/40)**<br>**2.4214** | **+30.0pt (3倍向上)**<br>隔離過去評価でも大幅汎化<br>未切替 77.5% → 45.0% |
| **3. Cell B**<br>(Old Dom + New Phr, 40件) | 正答率<br>Diff-Target Both | 40.0% (16/40)<br>0.0% (0/12) | 40.0% (16/40)<br>**0.0% (0/12)** | **75.0% (30/40)**<br>**41.7% (5/12)** | **+41.7pt** (崩壊セルが回復) |
| **4. Cell C**<br>(New Dom + Old Phr, 40件) | 正答率<br>Diff-Target Both | 40.0% (16/40)<br>8.3% (1/12) | 57.5% (23/40)<br>**75.0% (9/12)** | **80.0% (32/40)**<br>**75.0% (9/12)** | 正答率 +22.5pt (Diff 75%維持) |
| **5. eval_exception**<br>(M4.1 例外優先, 120件) | 正答率<br>Diff-Target Both | 32.5% (39/120)<br>0.0% (0/37) | 99.2% (119/120)<br>100.0% (37/37) | **100.0% (120/120)**<br>**100.0% (37/37)** | **満点達成 (100%保持)**<br>目安 -3pt以内 を大幅達成 |
| **6. eval_v2**<br>(M3 合成ルール, 200件) | 正答率<br>Diff-Target Both | **97.5% (195/200)**<br>91.5% (43/47) | 97.0% (194/200)<br>89.4% (42/47) | **95.5% (191/200)**<br>**80.9% (38/47)** | **-2.0pt (保持目安達成)**<br>目安 -3pt以内 (>=94.5%) を達成 |
| **7. transfer_probe**<br>(汎化プローブ, 32件) | 正答数 (正答率) | 25/32 (78.1%) | 20/32 (62.5%) | **22/32 (68.8%)** | **+2問 回復 (62.5% → 68.8%)** |
| **8. smoke_cases**<br>(基本診断, 12件) | 正答数 (正答率) | 9/12 (75.0%) | 12/12 (100.0%) | **10/12 (83.3%)** | **目安 (>=10/12) 達成**<br>基準版 (9/12) より高水準 |

---

## 13. M4.3.1 優先順位表現データ意味整合性是正（Semantic Repair）実測結果

詳細は [`runs/m4_3_1_phrasing_fix/notes.md`](file:///f:/ai/erabi-local/runs/m4_3_1_phrasing_fix/notes.md) および [`runs/m4_3_1_phrasing_fix/summary_report.json`](file:///f:/ai/erabi-local/runs/m4_3_1_phrasing_fix/summary_report.json) を参照。

### 13.1 不具合特定と独立意味バリデータ
- **原因特定**: `game_action` (HP < 20) および `facility_control` (温度 <= 25) において、小数値側がRule A成立であるにもかかわらず、ジェネレータが他ドメインと一律に `val_high` をconflict/single-Aにサンプリングしていたため、自然文上の条件と内部フラグ・targetが反転していた。
- **独立自然文バリデータの実装 (`src/erabi/semantic_validator.py`)**:
  - ジェネレータ内部フラグを受け取らず、レンダリング後テキストのみから真偽値と期待targetを復元する `derive_semantics` を実装。
  - 旧M4.3データの監査: `phrasing_train` 41件、`phrasing_dev` 15件、`fresh_phrasing_eval` 18件、Cell A/B 各10件（計94件）の不一致を完全検出・再現。
- **新データの生成と全件監査 (`data/m4_3_1_phrasing_fix/`)**:
  - ドメインごとの明示的 `rule_a_true_range` / `rule_a_false_range` によるサンプリング修正と文脈テンプレート是正。
  - **新データ全5セット（計520件）において不一致 0件（100% VALID）を確認**。
  - 全単体テスト（手計算境界値、HP=35移動中、温度21度、データ分離）がすべて PASS（プロジェクト全50テスト PASS）。

### 13.2 単一CE学習プロセス（B0から一括学習）
- **学習データ**: `data/m4_3_1_phrasing_fix/combined_train.jsonl` (1080件: M3 600 + M4.1 240 + 修正 phrasing 240)
- **開発データ**: `data/m4_3_1_phrasing_fix/combined_dev.jsonl` (220件: M3 100 + M4.1 40 + 修正 phrasing 80)
- **条件**: 旧M4.3と完全同一（lr=2e-5, wd=0.01, micro=2, accum=8, epochs=10, seed=42）。
- **チェックポイント選定**: Epoch 8（M3: 98.0%, M4.1: 100.0%, Phrasing Dev: 72.5%, Diff Both: 5/20 = 25.0%, NLL: 2.5112）を `runs/m4_3_1_phrasing_fix/trained/checkpoint` に保存。

### 13.3 4モデル総合対照表（すべて $T = 1.0$）

| 評価セット | 指標 | 基準版 (`W_v2_ce10`) | M4.1版 (`W_m4_1`) | 旧M4.3 (`W_m4_3p`) | **新M4.3.1 (`W_m4_3p_fix`)** |
|---|---|:---:|:---:|:---:|:---:|
| **1. 修正 fresh_phrasing_eval**<br>(未見Family M〜P, 120件: 60組) | 正答率<br>**Diff-Target Both**<br>Same-Target Both<br>Mean NLL | 45.0% (54/120)<br>**0.0% (0/30)**<br>43.3% (13/30)<br>2.5776 | 36.7% (44/120)<br>**0.0% (0/30)**<br>23.3% (7/30)<br>8.5316 | 74.2% (89/120)<br>**46.7% (14/30)**<br>73.3% (22/30)<br>2.2942 | **78.3% (94/120)**<br>**50.0% (15/30)**<br>**73.3% (22/30)**<br>**1.4657 (急減改善)** |
| **2. 修正 Cell A**<br>(Old Dom + Old Phr, 40件: 20組) | 正答率<br>**Diff-Target Both**<br>Mean NLL | 52.5% (21/40)<br>16.7% (2/12)<br>2.8229 | 65.0% (26/40)<br>50.0% (6/12)<br>4.6298 | 72.5% (29/40)<br>41.7% (5/12)<br>3.1649 | **97.5% (39/40)**<br>**91.7% (11/12)**<br>**0.0887 (ほぼ完全解法)** |
| **3. 修正 Cell B**<br>(Old Dom + New Phr, 40件: 20組) | 正答率<br>**Diff-Target Both**<br>Mean NLL | 35.0% (14/40)<br>0.0% (0/12)<br>3.3280 | 65.0% (26/40)<br>25.0% (3/12)<br>4.1347 | 55.0% (22/40)<br>25.0% (3/12)<br>3.7253 | **80.0% (32/40)**<br>**41.7% (5/12)**<br>**1.6591 (大幅回復)** |
| **4. Cell C**<br>(New Dom + Old Phr, 40件: 20組) | 正答率<br>**Diff-Target Both**<br>Mean NLL | 40.0% (16/40)<br>8.3% (1/12)<br>2.1658 | 57.5% (23/40)<br>75.0% (9/12)<br>7.1343 | 80.0% (32/40)<br>75.0% (9/12)<br>1.9460 | **85.0% (34/40)**<br>**100.0% (12/12)**<br>**0.6939** |
| **5. novel_priority_eval**<br>(Historical Family A〜D, 120件) | 正答率<br>**Diff-Target Both**<br>Mean NLL | 41.7% (50/120)<br>12.5% (5/40)<br>2.1155 | 46.7% (56/120)<br>15.0% (6/40)<br>7.0699 | 70.0% (84/120)<br>45.0% (18/40)<br>2.4214 | **72.5% (87/120)**<br>**50.0% (20/40)**<br>**1.3674** |
| **6. eval_exception (M4.1)** | 正答率<br>Diff-Target Both | 32.5% (39/120)<br>0.0% (0/37) | 99.2% (119/120)<br>100.0% (37/37) | **100.0% (120/120)**<br>100.0% (37/37) | **100.0% (120/120)**<br>**100.0% (37/37)** |
| **7. eval_v2 (M3 合成ルール)** | 正答率<br>Diff-Target Both | **97.5% (195/200)**<br>91.5% (43/47) | 97.0% (194/200)<br>89.4% (42/47) | 95.5% (191/200)<br>80.9% (38/47) | **93.5% (187/200)**<br>**78.7% (37/47)** |
| **8. transfer_probe (32問)** | 正答数 (正答率) | 25/32 (78.1%) | 20/32 (62.5%) | 22/32 (68.8%) | **22/32 (68.8%)** |
| **9. smoke_cases (12問)** | 正答数 (正答率) | 9/12 (75.0%) | 12/12 (100.0%) | 10/12 (83.3%) | **10/12 (83.3%)** |

### 13.4 旧結果の扱い
- 旧M4.3の報告値（85.8% fresh accuracy, 80.0% Diff Both）は、`game_action` / `facility_control` のラベル意味反転を含んだ旧データ上の測定値であったため、**代表性能としては使用しない**。
- 正式な代表性能は、独立バリデータで100%整合性を証明した新データ上の **W_m4_3p_fix (78.3% fresh accuracy, 50.0% Diff Both, NLL 1.4657)** とする。

---

## 14. M4.3.2 汎化ギャップと退行要因診断（Generalization Gap Diagnostic）実測結果

詳細は [`runs/m4_3_2_diagnostic/diagnostic_report.md`](file:///f:/ai/erabi-local/runs/m4_3_2_diagnostic/diagnostic_report.md) および [`runs/m4_3_2_diagnostic/gap_diagnostic_summary.json`](file:///f:/ai/erabi-local/runs/m4_3_2_diagnostic/gap_diagnostic_summary.json) を参照。

### 14.1 Split間 Generalization Gap 比較 ($T = 1.0$)

| 分割 (Split) | 対象Family | 件数 | 正答率 (Acc) | Mean NLL | Mean Brier | Pair Both | Diff Both | Same Both | Diff Unswitched | A_over_B Acc | B_over_A Acc | 方向間ギャップ |
|---|---|---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **phrasing_train** | Family E〜J | 240 | **98.3%** (236/240) | 0.0831 | 0.0296 | **96.7%** (116/120) | **95.0%** (57/60) | **98.3%** (59/60) | **5.0%** (3/60) | 99.2% | 97.5% | 1.7pt |
| **phrasing_dev** | Family K〜L | 80 | **72.5%** (58/80) | 2.5112 | 0.5385 | **60.0%** (24/40) | **25.0%** (5/20) | **95.0%** (19/20) | **50.0%** (10/20) | 75.0% | 70.0% | 5.0pt |
| **fresh_eval** | Family M〜P | 120 | **78.3%** (94/120) | 1.4657 | 0.3839 | **61.7%** (37/60) | **50.0%** (15/30) | **73.3%** (22/30) | **50.0%** (15/30) | 83.3% | 73.3% | 10.0pt |

- **知見1（学習Familyの定着は95.0%）**: `phrasing_train` (E〜J) では正答率 98.3%、Diff Both 95.0% (57/60組)、Unswitched わずか 3/60 (5.0%) と極めて高い。
- **知見2（構文難度による未切替の局所化）**:
  - `Family M` (Diff Both 62.5%, Unswitched 3/8) と `Family N` (Diff Both 75.0%, Unswitched 2/8) は目標 >= 60% を達成。
  - `Family K` (Diff Both 0.0%, Unswitched 5/10, SwitchedWrong 5/10) および `Family P` (Diff Both 14.3%, Unswitched 6/7) に未切替が集中。
  - Fresh M〜Pで失敗した15組は100%がUnswitched（片問正解・同一出力維持）であり、無秩序な第3選択肢への誤答は0件。

### 14.2 eval_v2 の退行9件・回復1件の個票特定 (`eval_v2_diff_cases.json`)
97.5% から 93.5% への 4.0pt 低下の全原因を特定：
1. **等号境界値の反転（5件、すべて `actual == threshold`）**:
   - `eval_v2-er-0009-c1/c2` (倉庫92個, 受注92個), `eval_v2-er-0049-c1` (99個, 99個), `eval_v2-er-0093-c1/c2` (34個, 34個)。
   - M4データに等号境界サンプルが存在せず、閾値離散サンプリングのみであったため、`達していれば` $\ge$ と `より多い場合に限り` $>$ の境界識別能力が希釈・忘却。
2. **ゲームHP数値による単一先入観ドリフト（4件）**:
   - `eval_v2-er-0015-c1`, `0057-c1`, `0071-c1`, `0091-c1`（HP基準以下だが「アイテムなし」のため待機が正解）。
   - M4の `HP < 20` $\to$ `heal` 単一規則の学習により、M3の複合論理（HPかつアイテム所持）の第2条件を無視して `heal` を選ぶヒューリスティックが発生。
3. **回復（1件）**: `eval_v2-gf-0052-c1`（指示切替能力向上により回復）。

### 14.3 transfer_probe の個票分析 (`transfer_probe_diff_cases.json`)
- M4.1からの回復4件（トリアージ赤最優先 `pa`、論理矛盾 `contradicts`、発注 `order`、監視静観 `quiet`）。
- M3基準からの退行2件（`tp-boundary-002-c1` 30名以上、`tp-edge-001-c2` 10名以上）は **eval_v2と完全に同一の `actual == threshold` 境界値反転**。

### 14.4 次フェーズ単一提案: 【Retention】（既存能力保持・境界リプレイ強化）
- **Scale / Variety / Operator の却下理由**:
  - Scale: 学習データ240件に対する過学習ではなく、未見表現への汎化機構は動作している。単なる増量では境界ドリフトは解消しない。
  - Variety: 既に16Family存在し、M/Nでは75%達成。多様性の不足ではない。
  - Operator: 標準CEでM4.1 100%、Cell C 100%を達成しており、損失関数の変更は不要。
- **Retention を選定する理由**:
  - 退行の100%が「等号境界値（5件）」と「複合条件チェック（4件）」の希釈忘却に起因。
  - M3の境界値・複合条件サンプルの重み付けリプレイ、または学習率・エポック配分の微調整により、eval_v2の 97.5% を回復・保持することが採用基準達成の最短・唯一の解。

## 15. M4.4-R 標的型リプレイ（Targeted Retention Replay）実測結果と判定

詳細は [`runs/m4_4_retention/notes.md`](file:///f:/ai/erabi-local/runs/m4_4_retention/notes.md) および [`runs/m4_4_retention/transition_summary.json`](file:///f:/ai/erabi-local/runs/m4_4_retention/transition_summary.json) を参照。

### 15.1 リプレイデータ構成と監査結果 (`data/m4_4_retention/`)
- **抽出元**: `data/m3_3_v2/train.jsonl`（600件）のみから厳格に抽出（新規合成データ生成なし）。
  - **R1（等号境界値）**: 24グループ = 48件（`actual == threshold` の境界規則）。
  - **R2（複合論理条件）**: 28グループ = 56件（`HP < thresh` と `has_item` の4状態均等サンプリング: 各状態7グループずつ）。
  - **リプレイ合計**: 52グループ = **104件**（上限160件枠、比率9.6%で上限クリア）。
- **汚染排除監査**:
  - `eval_v2`（200件）、`fresh_phrasing_eval`（120件）、`transfer_probe`（32件）、`smoke_cases`（12件）とのIDおよび入力指紋重複: **すべて 0件（完全隔離維持）**。
- **学習データ統合 (`combined_train_retention.jsonl`)**:
  - 総件数 1184件（M3 600 + M4.1 240 + M4.3.1 phrasing 240 + リプレイ 104）。
  - 検証データ 220件（M4.3.1と完全同一、eval_v2非使用）。
  - 単体テスト `tests/test_m4_4_retention.py`（5件全PASS、プロジェクト全55件 PASS）。

### 15.2 単一CE学習プロセス（B0から一括学習）
- **条件**: lr=2e-5, wd=0.01, micro=2, accum=8, 10 epochs, seed=42（M4.3.1と完全同一ハイパーパラメータ）。
- **チェックポイント選定**: 開発セット220件の成績に基づき **Epoch 9（M3: 100.0%, M4.1: 100.0%, Phrasing Dev: 72.5%, Diff Both: 4/20 = 20.0%, NLL: 4.6612）** を選定・保全。

### 15.3 4モデル総合対照表（すべて $T = 1.0$）

| 評価セット | 指標 | 基準版 (`W_v2_ce10`) | M4.1版 (`W_m4_1`) | M4.3.1版 (`W_m4_3p_fix`) | **新M4.4-R (`W_m4_4r`)** | M4.4-R vs M4.3.1 変化 |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **1. fresh_phrasing_eval**<br>(未見Family M〜P, 120件: 60組) | 正答率<br>**Diff-Target Both**<br>Same-Target Both<br>Mean NLL | 45.0% (54/120)<br>**0.0% (0/30)**<br>43.3% (13/30)<br>2.5776 | 36.7% (44/120)<br>**0.0% (0/30)**<br>23.3% (7/30)<br>8.5316 | 78.3% (94/120)<br>**50.0% (15/30)**<br>73.3% (22/30)<br>1.4657 | **80.8% (97/120)**<br>**60.0% (18/30)**<br>**76.7% (23/30)**<br>**1.2721** | **正答率 +2.5pt**<br>**Diff Both +10.0pt (目標60%達成)**<br>NLL 改善 |
| **2. Cell A**<br>(Old Dom + Old Phr, 40件: 20組) | 正答率<br>**Diff-Target Both**<br>Mean NLL | 52.5% (21/40)<br>16.7% (2/12)<br>2.8229 | 65.0% (26/40)<br>50.0% (6/12)<br>4.6298 | 97.5% (39/40)<br>91.7% (11/12)<br>0.0887 | **97.5% (39/40)**<br>**100.0% (12/12)**<br>**0.0984** | Diff Both **100%達成** |
| **3. Cell B**<br>(Old Dom + New Phr, 40件: 20組) | 正答率<br>**Diff-Target Both**<br>Mean NLL | 35.0% (14/40)<br>0.0% (0/12)<br>3.3280 | 65.0% (26/40)<br>25.0% (3/12)<br>4.1347 | 80.0% (32/40)<br>41.7% (5/12)<br>1.6591 | **72.5% (29/40)**<br>**50.0% (6/12)**<br>**1.7340** | Diff Both **+8.3pt** |
| **4. Cell C**<br>(New Dom + Old Phr, 40件: 20組) | 正答率<br>**Diff-Target Both**<br>Mean NLL | 40.0% (16/40)<br>8.3% (1/12)<br>2.1658 | 57.5% (23/40)<br>75.0% (9/12)<br>7.1343 | 85.0% (34/40)<br>100.0% (12/12)<br>0.6939 | **87.5% (35/40)**<br>**100.0% (12/12)**<br>**0.4784** | 正答率 +2.5pt<br>Diff Both **100%維持** |
| **5. novel_priority_eval**<br>(Historical Family A〜D, 120件) | 正答率<br>**Diff-Target Both**<br>Mean NLL | 41.7% (50/120)<br>12.5% (5/40)<br>2.1155 | 46.7% (56/120)<br>15.0% (6/40)<br>7.0699 | 72.5% (87/120)<br>50.0% (20/40)<br>1.3674 | **67.5% (81/120)**<br>**45.0% (18/40)**<br>**1.7144** | -5.0pt |
| **6. eval_exception (M4.1)** | 正答率<br>Diff-Target Both | 32.5% (39/120)<br>0.0% (0/37) | 99.2% (119/120)<br>100.0% (37/37) | 100.0% (120/120)<br>100.0% (37/37) | **100.0% (120/120)**<br>**100.0% (37/37)** | **100%完全維持** |
| **7. eval_v2 (M3 合成ルール)** | 正答率<br>Diff-Target Both | **97.5% (195/200)**<br>91.5% (43/47) | 97.0% (194/200)<br>89.4% (42/47) | 93.5% (187/200)<br>78.7% (37/47) | **92.5% (185/200)**<br>**76.6% (36/47)** | **-1.0pt (回復失敗)**<br>目標 >=97.0% 未達 |
| **8. transfer_probe (32問)** | 正答数 (正答率) | 25/32 (78.1%) | 20/32 (62.5%) | 22/32 (68.8%) | **22/32 (68.8%)** | 68.8% 同水準維持 |
| **9. smoke_cases (12問)** | 正答数 (正答率) | 9/12 (75.0%) | 12/12 (100.0%) | 10/12 (83.3%) | **11/12 (91.7%)** | **+1問 回復 (smoke-06, 10回復)** |

### 15.4 fresh_phrasing_eval の進展（60%目標達成）
- **Family別内訳**:
  - `family_M`: 正答率 **93.8% (30/32)**、Diff Both **6/8 (75.0%)**、Same Both 8/8 (100.0%)
  - `family_N`: 正答率 **84.4% (27/32)**、Diff Both **7/8 (87.5%)**、Same Both 6/8 (75.0%)
  - `family_O`: 正答率 **92.9% (26/28)**、Diff Both **5/7 (71.4%)**、Same Both 7/7 (100.0%)
  - `family_P`: 正答率 50.0% (14/28)、Diff Both 0/7 (0.0%)、Same Both 4/7 (57.1%)
- **総評**: Family M, N, O の3系統で Diff Both 70%超を達成し、未見表現全体で **18/30 (60.0%)** を初めて達成。

### 15.5 eval_v2 保持失敗の要因分析と【Pattern C】判定
- **実測結果**: 正答率 **92.5% (185/200)**。M4.3.2で特定された退行9件は **0件回復（1件も回復せず）**。さらに指示切替2件（`eval_v2-gf-0002-c1`, `eval_v2-gf-0052-c1`）が新たに退行。
- **根因分析（なぜM3リプレイが効かなかったのか）**:
  1. **境界値ルールの語彙・ドメイン乖離**:
     - `data/m3_3_v2/train.jsonl` の等号境界サンプル（24グループ）は、**100%が「点数（試験スコア）と合格/不合格」** のドメインで構成。
     - 一方、`eval_v2` で退行している5件はすべて **「倉庫の在庫数」「受注数」** ドメインであり、「達していれば出荷」という表現。
     - M3 train内に「達していれば」という語彙は **0回** しか出現しない。点数の境界例を倍増リプレイしても、在庫・出荷における等号境界判定の忘却を直接補正できなかった。
  2. **ヒューリスティック強度 vs サンプル数の圧倒的不均衡**:
     - M4データには `HP < 20` $\implies$ `heal` の強力な単一ルールが40件以上存在。
     - M3 train内の複合条件「HP低かつアイテムなし $\implies$ wait」は元々7件しかなく、リプレイで14件に増やした程度では、M4で刷り込まれた強力なショートカット（HP低なら回復）を打ち消せなかった。
- **指示書 Section 11 の停止条件判定: 【Pattern C】**:
  > **Pattern C**: eval_v2が回復しない（93.5%以下のまま、等号境界の忘却が解消しない）  
  > $\implies$ 「単純な重み付け/リプレイでは保持できない」。**大量リプレイへ進まず、ここで停止**。次は checkpoint selection / model capacity / task interference のいずれかを検討。

### 15.6 結論と方針
- **採用版見送り**: `W_m4_4r` は未見表現60%を達成したものの、eval_v2（92.5%）が採用基準（$\ge 97.0\%$）を満たさないため、**採用版にはしない**。
- **大量リプレイのエスカレーション禁止**: 単純にリプレイ件数を増やすのではなく、タスク干渉の構造的解消（チェックポイント選定基準の改善、あるいは表現形式と論理条件の学習バランス見直し）を次フェーズで検討する。

---

## 16. M4.4.1 セレクタカバレッジ修正・5モデル比較実測結果

詳細は [`runs/m4_4_1_retention/notes.md`](file:///f:/ai/erabi-local/runs/m4_4_1_retention/notes.md)、[`runs/m4_4_1_retention/regression_case_study.json`](file:///f:/ai/erabi-local/runs/m4_4_1_retention/regression_case_study.json) を参照。

### 16.1 修正内容と訓練データ構成 (`data/m4_4_1_retention/`)
- **カバレッジ漏れの解消**:
  - M4.4-Rでは `rule_kind == "boundary"` のみを抽出していたため、`eval_v2` で実際に退行していた「在庫数 == 受注数」の `comparison` ルールがリプレイから除外されていた。
  - M4.4.1では、M3 train（600件）内に実在する `rule_kind == "comparison"` かつ 在庫 == 受注 の4グループ（**8件**）を特定し、R1bとして1回追加リプレイ。
    - `train-er-0031`（38 == 38）, `train-er-0151`（55 == 55）, `train-er-0199`（59 == 59）, `train-er-0283`（40 == 40）
    - 各組：c1（以上 $\implies$ `ship`）, c2（超 $\implies$ `delay`）
- **リプレイ内訳（計112件, 56グループ）**:
  - R1（等号境界値）: 48件（24グループ）
  - R1b（等号比較）: **8件（4グループ）**
  - R2（複合論理4状態均等）: 56件（28グループ）
- **学習データ統合**: 1192件（M3 600 + M4.1 240 + M4.3.1 phrasing 240 + リプレイ 112、上限1240件枠内）。
- **汚染排除**: `eval_v2`, `fresh_phrasing_eval`, `transfer_probe`, `smoke_cases` との重複 0件。単体テスト全60件 PASS。

### 16.2 単一CE学習プロセス（B0から一括学習）
- **学習条件**: lr=2e-5, wd=0.01, micro=2, accum=8, 10 epochs, seed=42（変更なし）。
- **チェックポイント選定**: 開発セット220件の同一基準により **Epoch 10（M3: 100.0%, M4.1: 100.0%, Phrasing Dev Acc: 73.8%, Diff Both: 10/20 = 50.0%, NLL: 6.9447）** を選定・保全。

### 16.3 5モデル総合対照表（すべて $T = 1.0$）

| 評価セット | 指標 | 基準版 (`W_v2_ce10`) | M4.1版 (`W_m4_1`) | M4.3.1版 (`W_m4_3p_fix`) | M4.4-R版 (`W_m4_4r`) | **新M4.4.1 (`W_m4_4_1r`)** | M4.4.1 vs M4.4-R |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **1. fresh_phrasing_eval**<br>(未見Family M〜P, 120件) | 正答率<br>**Diff Both**<br>Same Both<br>Mean NLL | 45.0% (54/120)<br>0.0% (0/30)<br>43.3% (13/30)<br>2.5776 | 36.7% (44/120)<br>0.0% (0/30)<br>23.3% (7/30)<br>8.5316 | 78.3% (94/120)<br>50.0% (15/30)<br>73.3% (22/30)<br>1.4657 | 80.8% (97/120)<br>**60.0% (18/30)**<br>76.7% (23/30)<br>1.2721 | **80.0% (96/120)**<br>**56.7% (17/30)**<br>76.7% (23/30)<br>1.7081 | -0.8pt<br>-3.3pt (高水準維持) |
| **2. Cell A**<br>(Old Dom + Old Phr, 40件) | 正答率<br>**Diff Both** | 52.5% (21/40)<br>16.7% (2/12) | 65.0% (26/40)<br>50.0% (6/12) | 97.5% (39/40)<br>91.7% (11/12) | 97.5% (39/40)<br>**100.0% (12/12)** | **97.5% (39/40)**<br>**100.0% (12/12)** | **100%維持** |
| **3. Cell B**<br>(Old Dom + New Phr, 40件) | 正答率<br>**Diff Both** | 35.0% (14/40)<br>0.0% (0/12) | 65.0% (26/40)<br>25.0% (3/12) | 80.0% (32/40)<br>41.7% (5/12) | 72.5% (29/40)<br>50.0% (6/12) | **80.0% (32/40)**<br>**58.3% (7/12)** | 正答率 +7.5pt<br>**Diff Both +8.3pt** |
| **4. Cell C**<br>(New Dom + Old Phr, 40件) | 正答率<br>**Diff Both** | 40.0% (16/40)<br>8.3% (1/12) | 57.5% (23/40)<br>75.0% (9/12) | 85.0% (34/40)<br>100.0% (12/12) | 87.5% (35/40)<br>100.0% (12/12) | **82.5% (33/40)**<br>**100.0% (12/12)** | **100%維持** |
| **5. novel_priority_eval**<br>(Historical Family A〜D, 120件) | 正答率<br>**Diff Both** | 41.7% (50/120)<br>12.5% (5/40) | 46.7% (56/120)<br>15.0% (6/40) | 72.5% (87/120)<br>50.0% (20/40) | 67.5% (81/120)<br>45.0% (18/40) | **68.3% (82/120)**<br>**55.0% (22/40)** | **Diff Both +10.0pt** |
| **6. eval_exception (M4.1)** | 正答率<br>Diff Both | 32.5% (39/120)<br>0.0% (0/37) | 99.2% (119/120)<br>100.0% (37/37) | 100.0% (120/120)<br>100.0% (37/37) | 100.0% (120/120)<br>100.0% (37/37) | **100.0% (120/120)**<br>**100.0% (37/37)** | **100%完全維持** |
| **7. eval_v2 (M3 合成ルール)** | 正答率<br>Diff Both | **97.5% (195/200)**<br>91.5% (43/47) | 97.0% (194/200)<br>89.4% (42/47) | 93.5% (187/200)<br>78.7% (37/47) | 92.5% (185/200)<br>76.6% (36/47) | **91.5% (183/200)**<br>**72.3% (34/47)** | -1.0pt (回復未達) |
| **8. transfer_probe (32問)** | 正答数 (正答率)<br>Diff Both | 25/32 (78.1%)<br>71.4% (10/14) | 20/32 (62.5%)<br>35.7% (5/14) | 22/32 (68.8%)<br>35.7% (5/14) | 22/32 (68.8%)<br>42.9% (6/14) | **26/32 (81.2%)**<br>**64.3% (9/14)** | **+4問 大幅回復**<br>基準版(25問)突破 |
| **9. smoke_cases (12問)** | 正答数 (正答率) | 9/12 (75.0%) | 12/12 (100.0%) | 10/12 (83.3%) | 11/12 (91.7%) | **10/12 (83.3%)** | 同水準 |

### 16.4 旧5件 Comparison Equality Regression の個票追跡結果

| 対象事例ID | グループ | 状況 | 質問指示・条件 | 正解 | W_m4_3p_fix | W_m4_4r | **W_m4_4_1r** | 判定 |
|---|---|---|---|:---:|:---:|:---:|:---:|:---:|
| `eval_v2-er-0009-c1` | `eval_v2-er-0009` | 在庫92 == 受注92 | 達していれば出荷、足りなければ見送り | `ship` | × (delay) | × (delay) | **○ (ship)** | **直接回復 (RECOVERED)** |
| `eval_v2-er-0009-c2` | `eval_v2-er-0009` | 在庫92 == 受注92 | より多い場合に限り出荷、それ以下は見送り | `delay` | × (ship) | × (ship) | × (ship) | 未回復 |
| `eval_v2-er-0049-c1` | `eval_v2-er-0049` | 在庫99 == 受注99 | 達していれば出荷、足りなければ見送り | `ship` | × (delay) | × (delay) | **○ (ship)** | **直接回復 (RECOVERED)** |
| `eval_v2-er-0093-c1` | `eval_v2-er-0093` | 在庫34 == 受注34 | 達していれば出荷、足りなければ見送り | `ship` | × (delay) | × (delay) | × (delay) | 未回復 |
| `eval_v2-er-0093-c2` | `eval_v2-er-0093` | 在庫34 == 受注34 | より多い場合に限り出荷、それ以下は見送り | `delay` | × (ship) | × (ship) | × (ship) | 未回復 |

- **成果**: M4.4-Rでは 0/5件（1件も回復せず）だったものが、R1b追加により **2/5件（40.0%）が直接回復** し、M3 trainリプレイが「達していれば」の境界忘却を補正できることが実証された。
- **未解決部分**:
  - `c1` の「達していれば $\implies$ ship」は回復したものの、`c2` の「より多い場合に限り $\implies$ delay」は ship 側のバイアスが残り未回復。
  - HP複合論理の4件（`eval_v2-er-0015-c1`, `0057-c1`, `0071-c1`, `0091-c1`）は依然として0/4件（M4単一ヒューリスティックの干渉）。
  - さらにGoal Followingで3件の微細な予測シフトが生じ、全体の `eval_v2` は 91.5% となった。
- **transfer_probe の大幅回復**:
  - 一方で `transfer_probe` では境界値（30名以上、10名以上、50ミリ超）がことごとく回復し、**81.2%（26/32問）** と基準版（25問）を超える最高値を記録。

### 16.5 ユーザー指示に基づく次のアプローチ判断
- ユーザー指示条件：
  > 「これでも回復しない場合に初めて、checkpoint selection / task interference / capacityを検討してください。」
- **診断結論**:
  - R1bの追加により等号比較の直接回復（2件）およびtransfer_probeの飛躍（81.2%）は確認できたが、`eval_v2` 全体としては 97.0% に回復しなかった。
  - したがって、**「単純なデータリプレイのみによる完全保持の限界」が明確に確認され、次の段階である【Task Interference / Checkpoint Selection / Model Capacity】の本格検討** へ進む条件が整った。

---

## 17. レビューバンドル情報

- **M3.7校正ハンドオフ版**: [`runs/m3_7_calibration_handoff/review_bundle.zip`](file:///f:/ai/erabi-local/runs/m3_7_calibration_handoff/review_bundle.zip) (保持)
- **M4.1例外優先順位版**: [`runs/m4_1_exception/review_bundle.zip`](file:///f:/ai/erabi-local/runs/m4_1_exception/review_bundle.zip)（保持）
- **M4.2 Phase A成果物**: [`runs/m4_2_robustness/phase_a/`](file:///f:/ai/erabi-local/runs/m4_2_robustness/phase_a/)
- **M4.2.1 2×2診断成果物**: [`runs/m4_2_1_diagnostic/`](file:///f:/ai/erabi-local/runs/m4_2_1_diagnostic/)
- **M4.3-P表現多様化版（旧版）**: [`runs/m4_3_phrasing/review_bundle.zip`](file:///f:/ai/erabi-local/runs/m4_3_phrasing/review_bundle.zip)（保持）
- **M4.3.1意味整合是正版**: [`runs/m4_3_1_phrasing_fix/review_bundle.zip`](file:///f:/ai/erabi-local/runs/m4_3_1_phrasing_fix/review_bundle.zip)（保持）
- **M4.3.2汎化ギャップ診断成果物**: [`runs/m4_3_2_diagnostic/`](file:///f:/ai/erabi-local/runs/m4_3_2_diagnostic/)
- **M4.4-R標的型リプレイ版**: [`runs/m4_4_retention/review_bundle.zip`](file:///f:/ai/erabi-local/runs/m4_4_retention/review_bundle.zip)（保持）
- **M4.4.1セレクタ修正リプレイ版（最新実験）**: [`runs/m4_4_1_retention/review_bundle.zip`](file:///f:/ai/erabi-local/runs/m4_4_1_retention/review_bundle.zip)
  - **ファイルサイズ**: 114,766 bytes (約112 KB)
  - **SHA-256**: `a0341005edb80eb52850f4668cd545e6e35ccab42857cc7262fb24df783679ab`
  - **ファイル総数**: 19ファイル
  - **安全性監査**: モデル重みファイル、仮想環境、秘密情報の非含有を完全確認済み。

---

## 20. Phase A: Final Acceptance Integrity Audit 実測結果

詳細は [`FINAL_ACCEPTANCE_VERIFIED.md`](file:///f:/ai/erabi-local/FINAL_ACCEPTANCE_VERIFIED.md) および [`audit/final_acceptance_audit_report.json`](file:///f:/ai/erabi-local/audit/final_acceptance_audit_report.json) を参照。

### 20.1 監査項目と検証結果
1. **Freeze Lineage & Hashes**:
   - `model.safetensors` (SHA256: `be9a9cb1...`, 14:12 UTC) $\to$ `calibration.json` (SHA256: `8fc501f1...`, 14:18 UTC) $\to$ `sealed_test.jsonl` (SHA256: `86825a0c...`, 14:19 UTC)。
   - sealed test suite は RC1 モデル・校正 freeze 後に作成され、学習・校正・モデル選定への未混入を証明。
2. **Leakage 監査**:
   - 全過去データ 10カテゴリ・53ファイル・**13,240件** と照合。
   - 入力完全一致 (Signature)、グループID、コンテキスト、セマンティック状態すべてにおいて **完全 0件（100% ZERO LEAKAGE）**。
3. **独立意味論検証**:
   - 自然文レンダリング結果（context, question, choices）から独立バリデータで期待 target を再導出。
   - **120 / 120件（100.0%）完全一致、不整合 0件、未対応 0件**。
4. **Raw Logits 数学的再計算**:
   - 生logitsから $T=1.0$ および $T^* = 0.25597742585799016$ で全指標を再計算。
   - $T=1$: Acc 100.0%, Pair Both 100.0%, NLL $2.69 \times 10^{-10}$, Brier $1.59 \times 10^{-18}$。
   - $T^*$: Acc 100.0%, Pair Both 100.0%, NLL $0.000000$ (理論値 $\le 10^{-31}$), Brier $5.12 \times 10^{-68}$。
   - 丸め表示ではなく、フロート64精度において指数関数の数学的限界として極小であることを証明。
5. **校正独立性**:
   - $T^*=0.2560$ は独立な `data/m9_calibration/calibration.jsonl`（100件）で境界非到達（bounds [0.1, 10.0]）にて推定されたことを確認。
6. **Permutation 監査**:
   - 120問すべてで候補順序・IDを反転。Top-1 一致率 100.0%、最大確率ドリフト $1.93 \times 10^{-33}$、平均TV距離 $4.74 \times 10^{-35}$。
7. **採否判定**:
   - 全8基準を完全充足。`FINAL_ACCEPTANCE_VERIFIED.md` を作成し、Phase B（ONNX FP16）へ即時移行。

---

## 21. Phase B: ONNX Runtime FP16 Release 実測結果

詳細は [`release/erabi-rc1-onnx-fp16/README.md`](file:///f:/ai/erabi-local/release/erabi-rc1-onnx-fp16/README.md)、[`release/erabi-rc1-onnx-fp16/manifest.json`](file:///f:/ai/erabi-local/release/erabi-rc1-onnx-fp16/manifest.json)、[`release/erabi-rc1-onnx-fp16/benchmark.json`](file:///f:/ai/erabi-local/release/erabi-rc1-onnx-fp16/benchmark.json) を参照。

### 21.1 成果物構成 (`release/erabi-rc1-onnx-fp16/`)
- `model.onnx`: Native FP16 on CUDA (Float32 output logits, 356.9 MB, **50% 容量削減**)
- `tokenizer.json`, `tokenizer_config.json`, `config.json`: トークナイザ・モデル構成一式
- `calibration.json`: 校正結合情報 ($T^* = 0.256$)
- `manifest.json`: パッケージメタデータ・精度・ベンチマーク記録
- `benchmark.json`: 同一環境ベンチマーク実測値
- `example.py`: 即時実行可能な推論サンプルコード（動作確認済み）
- `README.md`, `LIMITATIONS.md`: 運用設計・利用制約書
- （※ FP32版も `release/rc1_onnx/` として保全）

### 21.2 4評価セット（340問）における PyTorch ↔ ONNX FP32 ↔ ONNX FP16 数値同等性

| 評価セット | 件数 | PyTorch Top-1 | ONNX FP32 Top-1 | ONNX FP16 Top-1 | Top-1 一致率 | 最大生Logit誤差 | 最大確率ドリフト |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Sealed Acceptance** | 120 | 100.0% | 100.0% | **100.0%** | **100.0% (120/120)** | 0.0779 | $5.40 \times 10^{-35}$ |
| **Fresh Operator** | 100 | 92.0% | 92.0% | **92.0%** | **100.0% (100/100)** | 0.0724 | $1.78 \times 10^{-4}$ |
| **Fresh Robustness** | 108 | 100.0% | 100.0% | **100.0%** | **100.0% (108/108)** | 0.0313 | $4.17 \times 10^{-31}$ |
| **Smoke Cases** | 12 | 83.3% | 83.3% | **83.3%** | **100.0% (12/12)** | 0.0484 | $1.60 \times 10^{-7}$ |
| **総合一致率** | **340** | - | - | - | **100.0% (340/340)** | - | - |

- **Paired Reasoning**: Sealed 100.0%, Fresh Operator 84.0%, Fresh Robustness 100.0%, Smoke 100.0%（PyTorchと完全同一）。
- **Permutation Consistency**: Sealed 100.0%, Fresh Operator 98.0%, Fresh Robustness 100.0%, Smoke 83.3%（PyTorchと完全同一）。

### 21.3 同一マシン（NVIDIA RTX A4000）ベンチマーク実測結果

| 実行エンジン | Cold Start | Warm p50 | Warm p95 | Warm p99 | 平均レイテンシ | スループット | モデル容量 | 1000回メモリドリフト |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **PyTorch CUDA FP32** (従来) | 27.30 ms | 20.65 ms | 33.59 ms | 37.07 ms | 22.22 ms | 45.0 req/s | 712.7 MB | - |
| **ONNX Runtime CPU FP32** | 51.64 ms | 51.54 ms | 54.22 ms | 54.77 ms | 51.06 ms | 19.6 req/s | 712.7 MB | - |
| **ONNX Runtime CUDA FP16** (採用) | **12.27 ms** | **11.14 ms** | **11.99 ms** | **14.67 ms** | **11.30 ms** | **88.5 req/s** | **356.9 MB** | **-1.51 MB (リーク皆無)** |

- **レイテンシ改善**: p50 で **1.85倍高速化**（20.65ms $\to$ 11.14ms）、p95 で **2.80倍高速化**（33.59ms $\to$ 11.99ms、分散が極小化）。
- **スループット**: 45.0 req/s $\to$ **88.5 req/s**（約2倍の処理能力向上）。
- **省メモリ性**: モデルファイル・VRAM専有が **50.0% 削減**（712.7MB $\to$ 356.9MB）。1000回連続推論におけるメモリドリフト -1.51MB（蓄積リーク皆無）。
- **テストスイート**: プロジェクト全 78/78 件 PASS。

---

## 22. 現在の完了状態

- **Phase A（Final Acceptance Integrity Audit）**: **完全合格 (`FINAL_ACCEPTANCE_VERIFIED.md`)**
- **Phase B（ONNX FP16 Release）**: **完全合格 (`release/erabi-rc1-onnx-fp16/`)**
- **凍結版 RC1 保全**: `release/rc1/` は 1 バイトも変更せず厳格に凍結維持。








