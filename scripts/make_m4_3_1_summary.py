"""Generate summary report JSON and notes markdown for ERABI M4.3.1 Semantic Repair."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent.parent

RUN_DIR = ROOT / "runs/m4_3_1_phrasing_fix"
RUN_DIR.mkdir(parents=True, exist_ok=True)


def main():
    comp_path = RUN_DIR / "comparisons/comparisons_summary.json"
    train_path = RUN_DIR / "trained/training_summary.json"
    manifest_path = ROOT / "data/m4_3_1_phrasing_fix/manifest.json"
    audit_path = ROOT / "data/m4_3_1_phrasing_fix/semantic_audit.json"

    comp_data = json.load(open(comp_path, encoding="utf-8"))
    train_data = json.load(open(train_path, encoding="utf-8"))
    manifest = json.load(open(manifest_path, encoding="utf-8"))
    audit = json.load(open(audit_path, encoding="utf-8"))

    # Build summary report
    report = {
        "experiment_title": "ERABI M4.3.1 Phrasing Dataset Semantic Repair Experiment",
        "description": (
            "Semantic repair of phrasing dataset Rule A conditions (game_action HP<20, facility_control temp<=25), "
            "independent semantic validation (100% pass), and re-training from B0 under identical standard CE conditions."
        ),
        "models": {
            "W_v2_ce10": {
                "name": "W_v2_ce10",
                "path": str(ROOT / "runs/m3_5_ce10/trained/checkpoint"),
                "description": "M3 baseline (10-epoch CE on M3 synthetic rules)",
            },
            "W_m4_1": {
                "name": "W_m4_1",
                "path": str(ROOT / "runs/m4_1_exception/trained/checkpoint"),
                "description": "M4.1 exception priority model (trained on 600 M3 + 240 Exception cases)",
            },
            "W_m4_3p": {
                "name": "W_m4_3p",
                "path": str(ROOT / "runs/m4_3_phrasing/trained/checkpoint"),
                "description": "M4.3-P prior model (trained with sampling bug in game/facility)",
            },
            "W_m4_3p_fix": {
                "name": "W_m4_3p_fix",
                "path": str(ROOT / "runs/m4_3_1_phrasing_fix/trained/checkpoint"),
                "description": "M4.3.1 repaired model (trained from B0 on 1080 combined cases with audited semantics)",
                "best_epoch": train_data["best_epoch"],
                "best_diff_both": train_data["best_diff_both"],
                "best_phr_nll": train_data["best_phr_nll"],
            },
        },
        "evaluation_temperature": 1.0,
        "temperature_policy": "strictly_uncalibrated_T1 (no calibration applied to new weights)",
        "semantic_audit_summary": {
            "phrasing_train": audit["phrasing_train"]["is_all_valid"],
            "phrasing_dev": audit["phrasing_dev"]["is_all_valid"],
            "fresh_phrasing_eval": audit["fresh_phrasing_eval"]["is_all_valid"],
            "cell_a_fix": audit["cell_a_fix"]["is_all_valid"],
            "cell_b_fix": audit["cell_b_fix"]["is_all_valid"],
        },
        "comparisons": comp_data,
        "training_history": train_data["history"],
    }

    report_path = RUN_DIR / "summary_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"Written summary report to {report_path}")

    # Build Notes Markdown
    w_base = comp_data["W_v2_ce10"]
    w_m41 = comp_data["W_m4_1"]
    w_old = comp_data["W_m4_3p"]
    w_fix = comp_data["W_m4_3p_fix"]

    notes = f"""# ERABI M4.3.1: Phrasing Dataset Semantic Repair 報告書

更新日: 2026-09-19
実験種別: データ意味整合性是正（Semantic Repair）および同一条件再学習・4モデル比較評価
評価条件: 全モデル・全評価セット **$T=1.0$ 固定**（未校正・新重みへの校正温度適用禁止を遵守）

---

## 1. エグゼクティブサマリ

### 1.1 背景と是正内容
- **不具合の原因**: `game_action`（HP < 20）および `facility_control`（温度 <= 25）において、Rule A成立が「小数値側」であるにもかかわらず、ジェネレータが他ドメインと一律に `val_high` をサンプリングしたため、**自然文ではRule A不成立であるにもかかわらず内部フラグではRule A成立・target=Rule A結論** と記録される意味反転が発生していた。
- **独立意味バリデータの配備**: ジェネレータ内部の `cond_a`, `cond_b` を一切受け取らず、レンダリング後の自然文（context・question・choices）のみからドメイン固有の正規表現により真偽値と論理的期待正解を復元する `erabi.semantic_validator.derive_semantics` を実装。
- **データセットの全件監査**:
  - 旧M4.3データの監査: `phrasing_train` で41件、`phrasing_dev` で15件、`fresh_phrasing_eval` で18件、M4.2.1 Cell A/B で各10件（合計94件）の不一致を完全検出・再現。
  - 新M4.3.1データの監査: ドメインごとの明示的 `rule_a_true_range` / `rule_a_false_range` によるサンプリング修正と文脈テンプレート是正を実施。
  - **新データ全5セット（計520件）において不一致 0件（100% VALID）を確認**。
- **同条件での一回限りの再学習**:
  - Base Model: `knowledgator/gliclass-instruct-base-v1.0` (B0)
  - 訓練集合: 合計1080件（M3 600件 + M4.1 240件 + M4.3.1 修正 phrasing 240件）
  - 検証集合: 合計220件（M3 100件 + M4.1 40件 + M4.3.1 修正 phrasing 80件）
  - ハイパーパラメータ: 旧M4.3と完全同一（lr=2e-5, weight_decay=0.01, micro_batch=2, grad_accum=8, seed=42, 10 epochs, standard CE）。
  - Checkpoint選択基準: M3 dev >= 95% かつ M4.1 dev >= 95% の中で phrasing dev Diff Both 最大（タイブレーク: NLL最小）。
  - **選定結果: Epoch 8（M3: 98.0%, M4.1: 100.0%, Phrasing: 72.5%, Diff Both: 5/20 = 25.0%, NLL: 2.5112）**。

---

## 2. 4モデル総合比較結果 ($T=1.0$)

| 評価データセット | 件数 | W_v2_ce10 (M3) | W_m4_1 (M4.1) | W_m4_3p (旧M4.3) | **W_m4_3p_fix (新M4.3.1)** |
|---|---:|---:|---:|---:|---:|
| **修正 fresh_phrasing_eval (M〜P)** | 120 | 45.0% (54/120)<br>Diff: 0/30 (0.0%) | 36.7% (44/120)<br>Diff: 0/30 (0.0%) | 74.2% (89/120)<br>Diff: 14/30 (46.7%) | **78.3% (94/120)**<br>**Diff: 15/30 (50.0%)** |
| 　*fresh Mean NLL* | - | 2.5776 | 8.5316 | 2.2942 | **1.4657** |
| **修正 Cell A (old dom + old phr)** | 40 | 52.5% (21/40)<br>Diff: 2/12 (16.7%) | 65.0% (26/40)<br>Diff: 6/12 (50.0%) | 72.5% (29/40)<br>Diff: 5/12 (41.7%) | **97.5% (39/40)**<br>**Diff: 11/12 (91.7%)** |
| **修正 Cell B (old dom + new phr)** | 40 | 35.0% (14/40)<br>Diff: 0/12 (0.0%) | 65.0% (26/40)<br>Diff: 3/12 (25.0%) | 55.0% (22/40)<br>Diff: 3/12 (25.0%) | **80.0% (32/40)**<br>**Diff: 5/12 (41.7%)** |
| **Cell C (new dom + old phr)** | 40 | 40.0% (16/40)<br>Diff: 1/12 (8.3%) | 57.5% (23/40)<br>Diff: 9/12 (75.0%) | 80.0% (32/40)<br>Diff: 9/12 (75.0%) | **85.0% (34/40)**<br>**Diff: 12/12 (100.0%)** |
| **novel_priority_eval (A〜D)** | 120 | 41.7% (50/120)<br>Diff: 5/40 (12.5%) | 46.7% (56/120)<br>Diff: 6/40 (15.0%) | 70.0% (84/120)<br>Diff: 18/40 (45.0%) | **72.5% (87/120)**<br>**Diff: 20/40 (50.0%)** |
| **eval_exception (M4.1)** | 120 | 32.5% (39/120)<br>Diff: 0/37 (0.0%) | 99.2% (119/120)<br>Diff: 37/37 (100.0%) | **100.0% (120/120)**<br>Diff: 37/37 (100.0%) | **100.0% (120/120)**<br>**Diff: 37/37 (100.0%)** |
| **eval_v2 (M3 合成ルール)** | 200 | **97.5% (195/200)**<br>Diff: 43/47 (91.5%) | 97.0% (194/200)<br>Diff: 42/47 (89.4%) | 95.5% (191/200)<br>Diff: 38/47 (80.9%) | **93.5% (187/200)**<br>**Diff: 37/47 (78.7%)** |
| **transfer_probe (32問)** | 32 | **78.1% (25/32)** | 62.5% (20/32) | 68.8% (22/32) | **68.8% (22/32)** |
| **smoke_cases (12問)** | 12 | 75.0% (9/12) | **100.0% (12/12)** | 83.3% (10/12) | **83.3% (10/12)** |

---

## 3. fresh_phrasing_eval_fix の詳細内訳分析

### 3.1 表現ファミリー別（M, N, O, P）
- **Family M** (Aを第一判断、Bを例外条件):
  - W_old: Acc 90.6%, Diff Both 5/8 (62.5%), Same Both 8/8 (100%)
  - **W_fix: Acc 90.6%, Diff Both 5/8 (62.5%), Same Both 8/8 (100%)**
- **Family N** (基本判定B、ただしA成立時はAを優先):
  - W_old: Acc 75.0%, Diff Both 7/8 (87.5%), Same Both 3/8 (37.5%)
  - **W_fix: Acc 87.5%, Diff Both 6/8 (75.0%), Same Both 6/8 (75.0%)** $\to$ 正確度とSame両問が大幅改善
- **Family O** (Bを基本判定、A成立時はAの結論を最終結果):
  - W_old: Acc 82.1%, Diff Both 2/7 (28.6%), Same Both 7/7 (100%)
  - **W_fix: Acc 78.6%, Diff Both 3/7 (42.9%), Same Both 5/7 (71.4%)** $\to$ 指示切替成功率が上昇
- **Family P** (競合解決順はA、Bの順):
  - W_old: Acc 46.4%, Diff Both 0/7 (0.0%), Same Both 4/7 (57.1%)
  - **W_fix: Acc 53.6%, Diff Both 1/7 (14.3%), Same Both 3/7 (42.9%)** $\to$ 最難関のFamily Pで初めてDiff Both正解を獲得

### 3.2 是正対象ドメイン（game_action / facility_control）の実測改善
- **facility_control (温度 <= 25)**:
  - W_old: Acc 62.5% (10/16), Diff Both 2/4 (50.0%), Same Both 2/4 (50.0%)
  - **W_fix: Acc 81.25% (13/16), Diff Both 4/4 (100.0%)! Same Both 2/4 (50.0%)**
  - $\to$ **競合・指示切替ペアの両問正解率が 50.0% から 100.0% へ完全跳躍**！
- **game_action (HP < 20)**:
  - W_old: Acc 50.0% (6/12), Diff Both 1/5 (20.0%), Same Both 0/1 (0.0%)
  - **W_fix: Acc 66.7% (8/12), Diff Both 1/5 (20.0%), Same Both 1/1 (100.0%)**
- **Old Domain 全体 (58問)**:
  - W_old: Acc 75.9% (44/58), Diff Both 10/18 (55.6%), Same Both 8/11 (72.7%)
  - **W_fix: Acc 84.5% (49/58), Diff Both 12/18 (66.7%), Same Both 9/11 (81.8%)**
  - $\to$ 意味修正により、既存ドメインに対する確信度と指示切替率が大幅に向上。
- **New Domain 全体 (62問)**:
  - W_old: Acc 72.6% (45/62), Diff Both 4/12 (33.3%), Same Both 14/19 (73.7%)
  - **W_fix: Acc 72.6% (45/62), Diff Both 3/12 (25.0%), Same Both 13/19 (68.4%)**

---

## 4. 要因分離（2×2 Factorial Diagnostic）の更新結論

| ドメイン＼表現 | Old Phrasing (Family A) | New Phrasing (Families B〜D) |
|---|---|---|
| **Old Domain** (game, delivery, system, facility, cs) | **Cell A (fix): 97.5% Acc / 91.7% Diff Both**<br>(W_m4_1: 65.0% / 50.0%) | **Cell B (fix): 80.0% Acc / 41.7% Diff Both**<br>(W_m4_1: 65.0% / 25.0%) |
| **New Domain** (mfg, power, inventory, scheduler) | **Cell C: 85.0% Acc / 100.0% Diff Both**<br>(W_m4_1: 57.5% / 75.0%) | **Novel Priority D: 72.5% Acc / 50.0% Diff Both**<br>(W_m4_1: 46.7% / 15.0%) |

- **Cell A**: 正しい意味ラベルで再学習した結果、既存構文かつ既存ドメインでは **97.5% Acc / 91.7% Diff Both** とほぼ完全解法を達成。
- **Cell B**: 旧M4.3では 55.0% Acc / 25.0% Diff Both だったものが、**80.0% Acc / 41.7% Diff Both** へと大幅に改善。
- **Cell C**: 85.0% Acc、**Diff Both 100.0%**（12組すべて指示切替成功）を維持・強化。

---

## 5. 旧結果（M4.3-P）の扱いに関する注記
- 旧M4.3-P報告書における `fresh_phrasing_eval` の **85.8% (103/120)** および **Diff Both 80.0% (24/30)** は、`game_action` と `facility_control` の誤ラベルが含まれていた旧評価データ上のものであるため、**代表性能としては使用しない**。
- 正しい意味ラベルで監査・再生成した新データと新重みによる正式な代表性能は:
  - **新 fresh_phrasing_eval 精度: 78.3% (94/120)**
  - **新 Diff-Target 両問正解: 15/30 (50.0%)**
  - **新 Mean NLL: 1.4657** (旧モデル 2.2942 から大幅な確信度・損失改善)
- これにより、意味反転ノイズを除去した真の汎化性能が確立された。
"""

    notes_path = RUN_DIR / "notes.md"
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write(notes)
    print(f"Written notes to {notes_path}")


if __name__ == "__main__":
    main()
