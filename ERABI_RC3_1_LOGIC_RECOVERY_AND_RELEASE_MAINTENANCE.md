# ERABI RC3.1 — Logic Recovery + Final Re-Acceptance Roadmap
## Blind v5診断を踏まえた最小追加学習 / Blind v6 / MIT化 / Repository Rename

作成日: 2026-09-21
対象: Codex / Antigravity
開発モード: 自律実行
前提: RC1 / RC2 / RC2.1 / RC3 / Blind v5 は凍結し、既存成果物を上書きしない

# 0. Decision

次の方針は **Option A相当の最小論理演算リカバリー** とする。

ただし、Blind v5を見た後なので、

> Blind v5を直接学習・checkpoint選定・再受験には使わない。

Blind v5はここで **Retired Diagnostic Benchmark** として固定する。

RC3.1では、Blind v5から抽象化した失敗カテゴリだけを利用し、
文章・数値・ドメイン・テンプレートが完全に異なる新規データで補強する。

最終判定は完全新規 **Blind v6** で一度だけ行う。

# 1. 現状

RC3 438Mモデル:
- Backbone: `knowledgator/gliclass-instruct-large-v1.0`
- Parameters: 約438M
- PyTorch model: 約1.75GB
- ONNX FP16: 約838.76MB
- ONNX FP16 CUDA p50: 約24.63ms
- PyTorch ↔ ONNX Top-1 parity: 100%

Blind v5:
- Overall: 409/480 = 85.21%
- Paired Both: 179/240 = 74.58%
- Permutation: 96.46%
- High-confidence error: 6.57%
- 7/8 familyは 81.67%〜95.00%
- `logical_operators` のみ 40/60 = 66.67%

したがって現時点では、巨大化・全面architecture変更より、
`logical_operators` の局所修復を優先する。

# 2. 数値上の正式ターゲット

現状:
`409 / 480 = 85.21%`

88% Gateを超える最低正解数:
`423 / 480 = 88.125%`

必要改善:
`+14 correct cases`

もし改善がすべてlogical_operatorsだけから来るなら:
`40 / 60 → 54 / 60 = 90.0%`

が必要。

したがってRC3.1 Development Gateでは、
logical operatorの目標を単に85%ではなく **>= 90%** へ設定する。

# 3. Blind v5の扱い

Blind v5は以下のみ許可。

許可:
- aggregate error category分析
- operator type別失敗率分析
- confidence傾向
- K/length/negation/nesting等の難易度軸の抽象化

禁止:
- Blind v5の文章をtrainへコピー
- 数値だけ変更したnear-copy
- Blind v5をdev/checkpoint selectionへ利用
- Blind v5で再度Final Acceptance判定

Blind v5は以後 `Retired Diagnostic Benchmark` として保存する。

# 4. RC3.1 North Star

目的:

> RC3の高速・軽量な438M All-in-One Cross-Encoder構造を維持したまま、
> 形式論理・複合否定・真理値切替の汎化だけを改善し、
> 完全新規Blind v6で88%以上を達成する。

変更しないもの:
- 438M backbone
- All-in-One Cross-Encoder
- input contract
- ONNX FP16 release path
- variable choice support
- calibration framework

# 5. Milestone 35 — Independent Logic Recovery Dataset

Blind v5の失敗文章を使わず、新規の意味状態・ドメイン・語彙で作成する。

必須operator:
- AND
- OR
- XOR
- NAND
- NOR
- NOT
- implication / conditional
- double negation
- polarity reversal
- nested conjunction/disjunction

必須状態:
- XORの4真理値状態
- NAND / NORの全真理値状態
- A / not A / not not A / A and not B / not A or B
- `(A AND B) OR C`
- `A AND (B OR C)`
- `NOT(A AND B)`
- `NOT(A OR B)`
- `(A XOR B) AND C`

深さはまず2まで。

# 6. Domain Diversity

最低12ドメイン以上:
- aerospace
- medical device
- railway
- semiconductor
- energy grid
- satellite telemetry
- warehouse safety
- chemical plant
- network routing
- robotics
- maritime
- manufacturing QA

1 domain = 1 operatorに固定しない。
各operatorを複数domainへ跨らせる。

# 7. Choice Design

選択肢に答えの理由を書かない。

禁止例:
`条件を満たしているため運転継続`

許可:
`運転継続 / 緊急停止 / 監視継続 / 手動点検`

禁止:
- joke distractor
- 不自然なダミー
- targetだけ長い説明文

候補順はtraining中にshuffle。

# 8. Logic Development Benchmark

Blind v5とは完全独立な `data/rc3_1_logic_bridge/` を作る。

目安:
- 320〜480 cases
- 160〜240 contrastive pairs

含める:
- unseen domains
- unseen phrasing families
- XOR/NAND/NOR
- double negation
- nested logic
- K=2,3,4,6
- lexical-overlap distractor
- implicit fallback
- reordered clauses

# 9. Logic Bridge Integrity Gate

必須:
- semantic mismatch = 0
- exact train overlap = 0
- exact historical eval overlap = 0
- Blind v5 exact overlap = 0
- normalized near-copy監査
- choice-position balance
- target distribution balance
- token limit compliance

generatorとvalidatorは独立。

# 10. Milestone 36 — RC3.1 Training

Base:
`release/rc3/model`

continual fine-tuningを優先。

Run 1:
- RC3 historical curriculum
- new logic recovery dataset
- task-balanced sampling
- low LR
- 1〜2 epochs程度

Run 2:
Run 1で不足する場合のみ。
変更は1 primary variableに限定。

原則2 full-trainingまで。

# 11. RC3.1 Development Gate

Logic Bridge:
- Overall >= 90%
- XOR >= 85%
- NAND >= 85%
- NOR >= 85%
- NOT / negation >= 90%
- nested logic >= 85%
- Paired Both >= 85%

Existing RC3 Bridge:
- Overall >= 88%
- logical_operators >= 90%
- general_choice >= 85%
- priority_exception >= 85%
- variable_choice >= 85%
- perturbation >= 85%
- natural_japanese >= 90%
- permutation >= 95%

Retention:
- mean core retention >= 96%

# 12. Checkpoint Selection

Blind v5は使わない。

使用可能:
- RC3.1 train/dev
- RC3 Bridge
- RC3.1 Logic Bridge
- historical retention suites

選定順:
1. retention gate
2. logic bridge
3. RC3 Bridge overall
4. paired both
5. NLL

# 13. Milestone 37 — RC3.1 Calibration

weights freeze後のみ。

RC3のTは流用しない。

新規calibration / fresh_calibration_evalを作る。

Guardrail:
- structural holdout
- operator family holdout
- K分布
- raw logits保存
- T=1ですでに十分ならNO_OP可

Gate:
- Top1不変
- fresh NLL改善
- Brier悪化なし
- high-confidence error改善または非悪化
- model hash binding

# 14. Milestone 38 — ONNX FP16

再export必須。

`PyTorch → ONNX FP32 → ONNX FP16 CUDA`

Gate:
- Top1 parity 100%
- calibration parity
- K=2..16 support
- probability drift acceptable
- 1000回memory leakなし

Performance target:
- p50 <= 27ms
- p95 <= 45ms

# 15. Milestone 39 — Blind v6 Final Acceptance

RC3.1 weights / calibration / ONNXをfreezeした後にのみ作成。

Blind v5 generator/templateの単純流用禁止。

Blind v6は完全新規。

Gate:
- Overall >= 88%
- logical_operators >= 80%
- no major family < 75%
- Paired Both >= 75%
- Permutation >= 95%
- high-confidence error <= 7%
- PyTorch ↔ ONNX parity 100%
- semantic error 0
- leakage 0

Blind v6は一度だけ実行。
失敗時は次回Blind v7。

# 16. 8Bへの移行条件

RC3.1でも以下ならLevel 5/6を再検討:
- Logic Bridge >=90%に届かない
- new logic dataでもnested/XOR/NAND/NORが伸びない
- 2 full-trainingで改善が小さい
- retention tradeoff解消不能

いきなり8Bへ移行しない。

# 17. Repository / Licensing Maintenance

モデル研究とは独立したmaintenance taskとして実施する。

## 17.1 Repository Rename

GitHub repository名を `erabi-local` から `erabi` へ変更する。

正式URL:
`https://github.com/sugarkwork/erabi`

rename後、repository全体を検索し、
`erabi-local`
`github.com/sugarkwork/erabi-local`
を含む参照を更新する。

対象:
- README
- badges
- docs
- clone examples
- CI/CD
- manifest
- release metadata
- package metadata
- scripts
- GitHub Actions
- issue/template links

ローカルGit remote:
`git remote set-url origin https://github.com/sugarkwork/erabi.git`

モデル説明中の「local decision engine」は残してよい。
正式プロジェクト名・repo名からのみ `local` を外す。

## 17.2 ERABI Source License

ERABI独自ソースコードは **MIT License** とする。

ルートに標準MIT本文 `LICENSE` を追加。

Copyright year:
`2026`

Copyright holderはrepository/project ownerとして一貫した名称を使用する。

## 17.3 pyproject.toml

package metadataでMITを明示する。
現行Python packaging standardに沿う形式を使用。

## 17.4 README License Section

READMEに最低限:

ERABI original source code is licensed under the MIT License.

Third-party libraries, pretrained models, model weights, and upstream
components remain subject to their respective licenses.

を明記する。

## 17.5 Third-Party Licenses

ERABIをMITにしても、GLiClass / DeBERTa / その他upstreamのライセンスをMITへ上書きしない。

必要なら `THIRD_PARTY_LICENSES.md` を作り、
- component
- upstream URL
- license
- bundled / dependency / model-base
を記録する。

# 18. GitHub Rename / License 作業の停止条件

GitHub側の権限不足でrenameできない場合:
- 代替repoを勝手に作らない
- ユーザーへ必要操作を報告

MIT適用範囲に法的不確実性がある第三者artifactを見つけた場合:
- そのartifactはMIT対象から除外
- upstream licenseを維持
- ユーザーへ報告

# 19. 自律実行順

A. RC3/Blind v5 freeze確認
B. Repository rename → erabi
C. MIT License / third-party notice整備
D. RC3.1 Logic Recovery Data
E. Logic Bridge Benchmark
F. RC3.1 Run 1
G. 必要ならRun 2
H. Development Gate
I. Calibration
J. ONNX FP16
K. Blind v6

Repository maintenanceとML実験はcommitを分ける。

# 20. ユーザーへ戻る条件

以下のみ停止して報告:
1. GitHub repo rename権限がない
2. third-party licenseに重大な不明点
3. 2 full-trainingでRC3.1 Development Gate未達
4. architecture変更が必要
5. 8B級を検討する必要
6. Blind v6完了
7. 重大なdata/eval bug発見

それ以外は自律進行。

# 21. Codex / Antigravityへの最上位指示文

RC3 Blind v5結果を正式FAILEDとしてfreezeしてください。

Blind v5は今後Retired Diagnostic Benchmarkとし、
train、checkpoint selection、Final Acceptance再利用には使わないでください。

次はERABI RC3.1として、
438M All-in-One Cross-Encoderを維持したまま
logical_operatorsだけを最小修復します。

Blind v5の文章・数値・templateをコピーせず、
XOR / NAND / NOR / NOT / double negation /
nested logic / polarity reversalを、
新規domain・新規phrasing・新規semantic statesで独立生成してください。

独立semantic validatorを必須とします。

新しいRC3.1 Logic Bridge Benchmarkを作成し、
Blind v5とは完全分離してください。

RC3.1 Development Gateでは
logical_operators >= 90%を目標にしてください。

現状409/480から88%を超えるには最低423/480、
すなわち+14問必要であり、
logical familyだけで埋めるなら40/60→54/60=90%が必要です。

full trainingは最大2回です。

Development Gateを突破したらweightsをfreezeし、
新規Calibration、
PyTorch→ONNX FP32→ONNX FP16 CUDA、
完全新規Blind v6へ進んでください。

Blind v6は一度だけFinal Acceptanceに使用します。

またML作業とは別commitでRepository Maintenanceを行ってください。

GitHub repo名を
sugarkwork/erabi-local
から
sugarkwork/erabi
へ変更してください。

正式URL:
https://github.com/sugarkwork/erabi

rename後、
README / badges / docs / scripts / manifests / CI /
clone examples / package metadata内の旧URLを検索し更新し、
local git remoteも新URLへ変更してください。

ERABI独自ソースコードはMIT Licenseにしてください。

root LICENSEに標準MIT本文を置き、
pyproject.tomlとREADMEにもMITを明記してください。

ただしGLiClass、DeBERTa、その他third-party component、
pretrained model、tokenizer、upstream artifactには
それぞれ元のライセンスを維持してください。

必要に応じてTHIRD_PARTY_LICENSES.mdを作成し、
component / upstream URL / license / roleを記録してください。

GitHub rename権限不足、
third-party license重大不明点、
2 full-training失敗、
architecture変更必要、
Blind v6完了、
重大data/eval bug
のいずれかに該当するまで、
ユーザー確認を待たず自律的に進めてください。
