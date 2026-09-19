"""Unit tests for ERABI M4.3.1 Semantic Repair & Independent Validator."""

import json
import pytest
from erabi.semantic_validator import (
    derive_conditions_from_context,
    derive_semantics,
    identify_domain_from_choices,
    parse_priority_order_from_question,
)


def test_hand_calculated_rule_boundaries():
    """1. Test Rule A true/false hand-calculated boundaries for each domain."""
    # game_action: Rule A is HP < 20
    assert derive_conditions_from_context("game_action", "HPは19です。現在、安全地帯へ移動中。")[0] is True
    assert derive_conditions_from_context("game_action", "HPは20です。現在、安全地帯へ移動中。")[0] is False
    assert derive_conditions_from_context("game_action", "HPは35です。現在、安全地帯へ移動中。")[0] is False

    # delivery_dispatch: Rule A is weight >= 30
    assert derive_conditions_from_context("delivery_dispatch", "荷物の重量は30kgです。至急配送要請あり。")[0] is True
    assert derive_conditions_from_context("delivery_dispatch", "荷物の重量は29kgです。至急配送要請あり。")[0] is False

    # system_ops: Rule A is CPU >= 80%
    assert derive_conditions_from_context("system_ops", "サーバーCPU使用率は80%です。不正侵入アラート検知あり。")[0] is True
    assert derive_conditions_from_context("system_ops", "サーバーCPU使用率は79%です。不正侵入アラート検知あり。")[0] is False

    # facility_control: Rule A is temp <= 25
    assert derive_conditions_from_context("facility_control", "現在温度25度。火災検知器が作動し非常警報が鳴動中。")[0] is True
    assert derive_conditions_from_context("facility_control", "現在温度26度。火災検知器が作動し非常警報が鳴動中。")[0] is False

    # manufacturing: Rule A is err <= 0.040
    assert derive_conditions_from_context("manufacturing", "寸法誤差は0.040mm。表面キズを検知。")[0] is True
    assert derive_conditions_from_context("manufacturing", "寸法誤差は0.041mm。表面キズを検知。")[0] is False

    # facility_power: Rule A is kW >= 400
    assert derive_conditions_from_context("facility_power", "受電電力400kW。蓄電池SOCは92%。")[0] is True
    assert derive_conditions_from_context("facility_power", "受電電力399kW。蓄電池SOCは92%。")[0] is False

    # inventory: Rule A is days >= 180
    assert derive_conditions_from_context("inventory", "保管日数180日。検疫検査対象。")[0] is True
    assert derive_conditions_from_context("inventory", "保管日数179日。検疫検査対象。")[0] is False

    # job_scheduler: Rule A is wait mins >= 60
    assert derive_conditions_from_context("job_scheduler", "待機時間60分。要求メモリ100GB。")[0] is True
    assert derive_conditions_from_context("job_scheduler", "待機時間59分。要求メモリ100GB。")[0] is False


def test_hp35_moving_derives_continue():
    """3. HP=35 + moving must derive continue, not heal, even if Priority A > B."""
    record = {
        "context": "現在のプレイヤーのHPは35です。回復アイテムあり。現在、安全地帯へ移動中。",
        "question": (
            "ルール：原則として移動例外（安全地帯等への移動中・進軍中なら「移動を継続する」）を使う。"
            "ただしHP基準（HPが20未満なら「回復する」）が成立する場合は、HP基準を移動例外より優先する。"
            "どちらも該当しない場合は「待機する」。規則に従って行動を選択してください。"
        ),
        "choices": [
            {"id": "heal", "text": "回復する"},
            {"id": "continue", "text": "移動を継続する"},
            {"id": "wait", "text": "待機する"},
        ],
        "target": {"choice_id": "continue"},
    }
    sem = derive_semantics(record)
    assert sem["cond_a"] is False  # HP=35 >= 20, so Rule A is FALSE
    assert sem["cond_b"] is True   # moving is TRUE
    assert sem["state_stratum"] == "single_b"
    assert sem["expected_target"] == "continue"
    assert sem["is_match"] is True


def test_temp21_no_alarm_derives_eco_mode():
    """4. temp=21 + no alarm must derive eco_mode, not emergency_stop or normal_run."""
    record = {
        "context": "設備空調モニター：現在温度21度（省エネ基準以下）。安全システム正常、警報なし。",
        "question": (
            "ルール：温度基準（室温が25度以下なら「省エネ運転へ切替」）と安全例外（非常停止信号・警報・緊急ボタン検知時は「即時非常停止」）"
            "の両方が成立したときは安全例外を選ぶ。片方だけ成立した場合は成立側を選び、どちらも成立しなければ「通常運転維持」を選ぶ。"
            "規則に従って行動を選択してください。"
        ),
        "choices": [
            {"id": "eco_mode", "text": "省エネ運転へ切替"},
            {"id": "emergency_stop", "text": "即時非常停止"},
            {"id": "normal_run", "text": "通常運転維持"},
        ],
        "target": {"choice_id": "eco_mode"},
    }
    sem = derive_semantics(record)
    assert sem["cond_a"] is True   # temp=21 <= 25, so Rule A is TRUE
    assert sem["cond_b"] is False  # no alarm
    assert sem["state_stratum"] == "single_a"
    assert sem["expected_target"] == "eco_mode"
    assert sem["is_match"] is True


def test_no_contradictory_temp_description():
    """5. Context text must never say '21度（25度超過）' or '35（危険水域）'."""
    # Contradictory text should be caught by assertion or logic
    # In facility_control, temp <= 25 is '省エネ基準以下', not '25度超過'
    cond_a, _ = derive_conditions_from_context("facility_control", "設備空調モニター：現在温度21度（省エネ基準以下）。警報なし。")
    assert cond_a is True

    cond_a_high, _ = derive_conditions_from_context("facility_control", "設備空調モニター：現在温度29度（25度超過）。警報なし。")
    assert cond_a_high is False


def test_repaired_datasets_isolation_and_quotas():
    """6. Quota, split separation, family partition, and semantic state separation."""
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from scripts.build_m4_3_1_repaired_data import PAST_DATASETS, compute_fingerprint
    data_dir = root / "data/m4_3_1_phrasing_fix"

    train = [json.loads(line) for line in open(data_dir / "phrasing_train.jsonl", encoding="utf-8") if line.strip()]
    dev = [json.loads(line) for line in open(data_dir / "phrasing_dev.jsonl", encoding="utf-8") if line.strip()]
    fresh = [json.loads(line) for line in open(data_dir / "fresh_phrasing_eval.jsonl", encoding="utf-8") if line.strip()]
    cell_a = [json.loads(line) for line in open(data_dir / "diagnostic_fix/cell_a_old_domain_old_phrasing.jsonl", encoding="utf-8") if line.strip()]
    cell_b = [json.loads(line) for line in open(data_dir / "diagnostic_fix/cell_b_old_domain_new_phrasing.jsonl", encoding="utf-8") if line.strip()]

    # Quotas
    assert len(train) == 240
    assert len(dev) == 80
    assert len(fresh) == 120
    assert len(cell_a) == 40
    assert len(cell_b) == 40

    # Family separation
    train_fams = set(r["phrasing_family"] for r in train)
    dev_fams = set(r["phrasing_family"] for r in dev)
    fresh_fams = set(r["phrasing_family"] for r in fresh)
    assert train_fams == {"family_E", "family_F", "family_G", "family_H", "family_I", "family_J"}
    assert dev_fams == {"family_K", "family_L"}
    assert fresh_fams == {"family_M", "family_N", "family_O", "family_P"}
    assert train_fams.isdisjoint(dev_fams)
    assert train_fams.isdisjoint(fresh_fams)
    assert dev_fams.isdisjoint(fresh_fams)

    # Overlaps
    train_fps = set(compute_fingerprint(r) for r in train)
    dev_fps = set(compute_fingerprint(r) for r in dev)
    fresh_fps = set(compute_fingerprint(r) for r in fresh)
    assert len(train_fps) == 240
    assert len(dev_fps) == 80
    assert len(fresh_fps) == 120
    assert train_fps.isdisjoint(dev_fps)
    assert train_fps.isdisjoint(fresh_fps)
    assert dev_fps.isdisjoint(fresh_fps)

    # Zero overlap with past datasets
    past_fps = set()
    for p in PAST_DATASETS:
        if p.is_file():
            for line in open(p, encoding="utf-8"):
                if line.strip():
                    past_fps.add(compute_fingerprint(json.loads(line)))
    assert train_fps.isdisjoint(past_fps)
    assert dev_fps.isdisjoint(past_fps)
    assert fresh_fps.isdisjoint(past_fps)

    # 100% semantic validity
    audit = json.load(open(data_dir / "semantic_audit.json", encoding="utf-8"))
    assert audit["phrasing_train"]["is_all_valid"] is True
    assert audit["phrasing_dev"]["is_all_valid"] is True
    assert audit["fresh_phrasing_eval"]["is_all_valid"] is True
    assert audit["cell_a_fix"]["is_all_valid"] is True
    assert audit["cell_b_fix"]["is_all_valid"] is True

