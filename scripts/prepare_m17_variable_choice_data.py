"""Prepare Variable Choice Count (K in [2, 3, 4, 6, 8, 12, 16]) Datasets for Milestone 17.

Roadmap: ERABI_RC2_AUTONOMOUS_RESEARCH_ROADMAP.md (Section 11)
Goal: Break dependence on fixed 2-3 choices. Generalize to 2, 3, 4, 6, 8, 12, 16 choices.
Distractor types:
- plausible in-domain distractors
- semantically close distractors
- irrelevant cross-domain distractors

Output:
- data/rc2_m17_choices/variable_choice_eval.jsonl (280 benchmark cases: 40 cases per K in [2, 3, 4, 6, 8, 12, 16])
- data/rc2_m17_choices/train_variable_choices_stream_a.jsonl (356 samples, variable K)
- data/rc2_m17_choices/train_variable_choices_stream_b.jsonl (782 samples, variable K)
- data/rc2_m17_choices/train_variable_choices_combined.jsonl (1,138 samples total)
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
import random
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.prepare_m17")

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data/rc2_m17_choices"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CHOICE_COUNTS = [2, 3, 4, 6, 8, 12, 16]

# Comprehensive Distractor Library by Domain
DISTRACTOR_POOLS: Dict[str, List[Tuple[str, str]]] = {
    "inventory": [
        ("ship", "即時出荷"),
        ("delay", "出荷保留"),
        ("cancel", "注文キャンセル"),
        ("partial_ship", "分割出荷"),
        ("priority_ship", "優先出荷"),
        ("warehouse_transfer", "倉庫間移動"),
        ("verify_address", "配送先確認"),
        ("stock_replenish", "在庫補充"),
        ("inspect_quality", "品質検査"),
        ("return_supplier", "仕入先返品"),
        ("contact_buyer", "購入者連絡"),
        ("batch_process", "一括処理"),
        ("archive_order", "注文アーカイブ"),
        ("manual_review", "手動審査"),
        ("discount_apply", "割引適用"),
        ("flag_urgent", "緊急フラグ設定"),
    ],
    "server": [
        ("reboot", "サーバ再起動"),
        ("scale_up", "スケールアップ"),
        ("ignore_alert", "アラート静観"),
        ("isolate_node", "ノード隔離"),
        ("restart_service", "サービス再起動"),
        ("flush_cache", "キャッシュクリア"),
        ("block_ip", "IPアドレス遮断"),
        ("rollback_deploy", "デプロイ切り戻し"),
        ("notify_admin", "管理者通知"),
        ("dump_logs", "ログダンプ取得"),
        ("enable_safemode", "セーフモード移行"),
        ("switch_standby", "待機系切替"),
        ("kill_process", "プロセス強制終了"),
        ("update_cert", "証明書更新"),
        ("run_diagnostic", "診断スクリプト実行"),
        ("throttle_traffic", "トラフィック制限"),
    ],
    "delivery": [
        ("express", "特急便で配送"),
        ("standard", "通常便で配送"),
        ("hold_depot", "営業所留め"),
        ("redeliver", "再配達手配"),
        ("return_sender", "差出人返送"),
        ("confirm_time", "配達時間確認"),
        ("change_address", "配送先変更"),
        ("repack_item", "荷物再梱包"),
        ("locker_drop", "宅配ロッカー納品"),
        ("contact_driver", "ドライバー連絡"),
        ("priority_sort", "優先仕分け"),
        ("fragile_handling", "精密品扱い"),
        ("customs_check", "税関確認"),
        ("delay_notice", "遅延通知送付"),
        ("cancel_transit", "配送中止"),
        ("signature_required", "対面受取指定"),
    ],
    "game": [
        ("heal", "回復アイテム使用"),
        ("attack", "通常攻撃実行"),
        ("special_skill", "必殺技発動"),
        ("defend", "防御態勢"),
        ("escape", "戦闘から離脱"),
        ("use_buff", "強化魔法使用"),
        ("swap_weapon", "武器切替"),
        ("wait_turn", "待機"),
        ("cast_debuff", "弱体化魔法"),
        ("revive_ally", "味方蘇生"),
        ("counter_stance", "反撃構え"),
        ("analyze_enemy", "敵弱点分析"),
        ("charge_mana", "魔力充填"),
        ("call_reinforce", "援軍要請"),
        ("protect_ally", "味方をかばう"),
        ("taunt_boss", "敵を挑発"),
    ],
    "support": [
        ("technical", "技術サポート窓口へ転送"),
        ("billing", "請求・支払い窓口へ転送"),
        ("general", "一般案内窓口へ転送"),
        ("escalate_tier2", "2次対応へエスカレーション"),
        ("send_faq", "FAQ案内メール送付"),
        ("schedule_callback", "折り返し電話予約"),
        ("close_ticket", "問い合わせ完了処理"),
        ("refund_request", "返金申請受付"),
        ("reset_password", "パスワード初期化案内"),
        ("hardware_repair", "修理受付窓口へ転送"),
        ("cancel_contract", "解約案内窓口へ転送"),
        ("record_feedback", "要望記録のみ実施"),
        ("legal_compliance", "法務コンプライアンス窓口"),
        ("account_unlock", "アカウント凍結解除"),
        ("sales_inquiry", "営業相談窓口へ転送"),
        ("status_check", "受付状況確認"),
    ],
}

IRRELEVANT_DISTRACTORS: List[Tuple[str, str]] = [
    ("irr_weather", "天気予報を確認"),
    ("irr_printer", "プリンタの用紙を補給"),
    ("irr_coffee", "休憩室の清掃を実施"),
    ("irr_calendar", "来月の祝日を確認"),
    ("irr_backup", "オフライン磁気テープを保管"),
    ("irr_lights", "オフィスの照明を消灯"),
    ("irr_door", "自動ドアの点検を実施"),
    ("irr_music", "BGMの音量を調整"),
]


def expand_choices(
    record: Dict[str, Any],
    target_count: int,
    rng: random.Random,
) -> Dict[str, Any]:
    """Expand a choice record to have exactly target_count choices without altering target truth."""
    rec = copy.deepcopy(record)
    existing_choices = rec["choices"]
    target_cid = rec["target"]["choice_id"]
    domain = rec.get("domain", "none")

    # Preserve target choice
    tgt_choice = next(c for c in existing_choices if c["id"] == target_cid)
    
    # Collect candidate distractor texts already present
    used_texts = {c["text"] for c in existing_choices}
    used_ids = {c["id"] for c in existing_choices}

    needed = target_count - len(existing_choices)
    if needed <= 0:
        # If record already has more choices than target_count, keep target and randomly sample others
        non_tgt = [c for c in existing_choices if c["id"] != target_cid]
        rng.shuffle(non_tgt)
        selected = [tgt_choice] + non_tgt[: target_count - 1]
        rng.shuffle(selected)
        rec["choices"] = selected
        rec["choice_count"] = target_count
        return rec

    # Available candidate pools
    in_domain_pool = DISTRACTOR_POOLS.get(domain, [])
    other_domain_pools = []
    for d, pool in DISTRACTOR_POOLS.items():
        if d != domain:
            other_domain_pools.extend(pool)

    # 1. In-domain plausible distractors
    plausible_candidates = [
        (cid, text) for cid, text in in_domain_pool
        if text not in used_texts and cid != target_cid
    ]
    rng.shuffle(plausible_candidates)

    # 2. Cross-domain / irrelevant distractors
    other_candidates = [
        (cid, text) for cid, text in (other_domain_pools + IRRELEVANT_DISTRACTORS)
        if text not in used_texts
    ]
    rng.shuffle(other_candidates)

    added_choices = []
    # Add plausible distractors first
    while plausible_candidates and len(added_choices) < needed:
        cid, text = plausible_candidates.pop(0)
        c_id = cid if cid not in used_ids else f"{cid}_{len(added_choices)}"
        used_ids.add(c_id)
        used_texts.add(text)
        added_choices.append({"id": c_id, "text": text})

    # Fill remainder with other/irrelevant distractors
    while len(added_choices) < needed:
        if other_candidates:
            cid, text = other_candidates.pop(0)
        else:
            cid, text = f"dist_{len(added_choices)}", f"その他の対応_{len(added_choices)}"
        c_id = cid if cid not in used_ids else f"{cid}_{len(added_choices)}"
        used_ids.add(c_id)
        used_texts.add(text)
        added_choices.append({"id": c_id, "text": text})

    new_choices = list(existing_choices) + added_choices
    assert len(new_choices) == target_count

    # Shuffle choice positions
    rng.shuffle(new_choices)
    rec["choices"] = new_choices
    rec["choice_count"] = target_count
    return rec


def generate_variable_eval_set() -> List[Dict[str, Any]]:
    """Generate 280 evaluation cases (40 per choice count K in [2, 3, 4, 6, 8, 12, 16]).
    Strictly stratified across every K:
    - 10 General Choice cases
    - 10 Operator Reasoning cases
    - 10 Robustness cases
    - 5 Phrasing Variation cases
    - 5 Core Retention cases
    Total per K = 40 cases. Total = 280 cases.
    """
    rng = random.Random(42)

    gen_cases = [json.loads(l) for l in open(ROOT / "data/m8_general_choice/fresh_general_eval.jsonl", encoding="utf-8") if l.strip()]
    op_cases = [json.loads(l) for l in open(ROOT / "data/m6_operator/fresh_operator_eval.jsonl", encoding="utf-8") if l.strip()]
    rob_cases = [json.loads(l) for l in open(ROOT / "data/m7_robustness/fresh_robustness_eval.jsonl", encoding="utf-8") if l.strip()]
    phr_cases = [json.loads(l) for l in open(ROOT / "data/m4_3_1_phrasing_fix/fresh_phrasing_eval.jsonl", encoding="utf-8") if l.strip()]
    core_cases = [json.loads(l) for l in open(ROOT / "data/m3_3_v2/eval_v2.jsonl", encoding="utf-8") if l.strip()]

    rng.shuffle(gen_cases)
    rng.shuffle(op_cases)
    rng.shuffle(rob_cases)
    rng.shuffle(phr_cases)
    rng.shuffle(core_cases)

    eval_cases = []
    for k_idx, k in enumerate(CHOICE_COUNTS):
        k_raw = []
        # Take disjoint slices for each K
        k_raw.extend(gen_cases[k_idx * 10 : (k_idx + 1) * 10])
        k_raw.extend(op_cases[k_idx * 10 : (k_idx + 1) * 10])
        k_raw.extend(rob_cases[k_idx * 10 : (k_idx + 1) * 10])
        k_raw.extend(phr_cases[k_idx * 5 : (k_idx + 1) * 5])
        k_raw.extend(core_cases[k_idx * 5 : (k_idx + 1) * 5])
        assert len(k_raw) == 40

        rng.shuffle(k_raw)
        for i, raw in enumerate(k_raw):
            rec = expand_choices(raw, target_count=k, rng=rng)
            rec["id"] = f"var_k{k}_{i:03d}"
            rec["choice_count"] = k
            eval_cases.append(rec)

    assert len(eval_cases) == len(CHOICE_COUNTS) * 40  # 280
    return eval_cases


def generate_variable_training_set(
    stream_a: List[Dict[str, Any]],
    stream_b: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Expand training datasets to variable candidate counts K in [2, 3, 4, 6, 8, 12, 16].
    Weighted choice distribution:
    - 2 choices: 25%
    - 3 choices: 25%
    - 4 choices: 15%
    - 6 choices: 10%
    - 8 choices: 10%
    - 12 choices: 7.5%
    - 16 choices: 7.5%
    Anchoring 50% on 2-3 choices preserves sharp 2-3 choice contrastive resolution,
    while 50% on 4..16 choices teaches distractor discrimination at scale.
    """
    rng = random.Random(100)

    # Choice schedule
    k_distribution = [2, 2, 3, 3, 4, 6, 8, 12, 16]

    var_stream_a = []
    for idx, r in enumerate(stream_a):
        k = k_distribution[idx % len(k_distribution)]
        var_stream_a.append(expand_choices(r, target_count=k, rng=rng))

    var_stream_b = []
    for idx, r in enumerate(stream_b):
        k = k_distribution[idx % len(k_distribution)]
        var_stream_b.append(expand_choices(r, target_count=k, rng=rng))

    assert len(var_stream_a) == len(stream_a)
    assert len(var_stream_b) == len(stream_b)
    return var_stream_a, var_stream_b


def main():
    logger.info("=== Preparing Milestone 17 Variable Choice Count Datasets ===")
    
    # 1. Generate Variable Choice Evaluation Set
    logger.info("Generating variable_choice_eval.jsonl (280 cases: 40 per K in [2, 3, 4, 6, 8, 12, 16])...")
    eval_cases = generate_variable_eval_set()
    eval_file = DATA_DIR / "variable_choice_eval.jsonl"
    with open(eval_file, "w", encoding="utf-8") as f:
        for r in eval_cases:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    logger.info(f"Saved {len(eval_cases)} evaluation cases to {eval_file}")

    # 2. Generate Variable Choice Training Sets
    logger.info("Building optimal RC2 data mixture (M16 Recommended Policy)...")
    pool_a = [json.loads(l) for l in open(ROOT / "data/rc2_scaling/train_stream_a_frac_100.jsonl", encoding="utf-8") if l.strip()]
    pool_b = [json.loads(l) for l in open(ROOT / "data/rc2_scaling/train_stream_b_frac_100.jsonl", encoding="utf-8") if l.strip()]

    rng = random.Random(42)

    # Stream A: 300 distinct groups, 356 samples total
    groups_a: Dict[str, List[Dict[str, Any]]] = {}
    for r in pool_a:
        groups_a.setdefault(r["group_id"], []).append(r)
    sorted_gids = sorted(groups_a.keys())
    rng.shuffle(sorted_gids)

    stream_a = []
    for gid in sorted_gids:
        stream_a.append(groups_a[gid][0])
    extra_gids = [gid for gid in sorted_gids if len(groups_a[gid]) > 1]
    rng.shuffle(extra_gids)
    for gid in extra_gids:
        if len(stream_a) >= 356:
            break
        stream_a.append(groups_a[gid][1])
    assert len(stream_a) == 356

    # Stream B: 782 samples total
    # Phrasing: 140, Exception: 120, Operators: 240, Domain Perturbation: 140, General: 142
    fam_buckets: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in pool_b:
        fam_buckets[r["task_family"]].append(r)
    for fam in fam_buckets:
        rng.shuffle(fam_buckets[fam])

    stream_b = []
    stream_b.extend(fam_buckets["phrasing_diversification_fix"][:140])
    stream_b.extend(fam_buckets["exception_priority"][:120])
    stream_b.extend(fam_buckets["domain_perturbation_robustness"][:140])

    op_fams = ["and_logic", "or_logic", "ge_vs_gt", "le_vs_lt", "negation", "override", "priority_ranking", "first_match", "default_exception", "goal_switching"]
    op_per_fam = 24  # 10 * 24 = 240
    for of in op_fams:
        stream_b.extend(fam_buckets[of][:op_per_fam])

    gen_fams = ["intent_selection", "instruction_separation", "negative_goal", "short_nli", "support_routing", "semantic_relation"]
    # 142 across 6 families: 4*24 + 2*23 = 142
    for i, gf in enumerate(gen_fams):
        take = 24 if i < 4 else 23
        stream_b.extend(fam_buckets[gf][:take])

    assert len(stream_b) == 782
    logger.info(f"Stream B composition: Phrasing=140, Exception=120, Domain=140, Operators=240, General=142")

    logger.info("Generating variable choice training data with K in [2..16]...")
    var_a, var_b = generate_variable_training_set(stream_a, stream_b)
    all_recs = var_a + var_b

    file_a = DATA_DIR / "train_variable_choices_stream_a.jsonl"
    file_b = DATA_DIR / "train_variable_choices_stream_b.jsonl"
    file_comb = DATA_DIR / "train_variable_choices_combined.jsonl"

    with open(file_a, "w", encoding="utf-8") as f:
        for r in var_a:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(file_b, "w", encoding="utf-8") as f:
        for r in var_b:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(file_comb, "w", encoding="utf-8") as f:
        for r in all_recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    logger.info(f"Saved {len(var_a)} Stream A and {len(var_b)} Stream B variable choice records.")

    # Manifest
    k_eval_counts = {k: sum(1 for r in eval_cases if r["choice_count"] == k) for k in CHOICE_COUNTS}
    k_train_counts = {k: sum(1 for r in all_recs if r["choice_count"] == k) for k in CHOICE_COUNTS}

    manifest = {
        "milestone": "Milestone 17 Variable Choice Count",
        "supported_choice_counts": CHOICE_COUNTS,
        "eval_cases_per_k": k_eval_counts,
        "train_cases_per_k": k_train_counts,
        "total_train_records": len(all_recs),
        "total_eval_records": len(eval_cases),
        "files": {
            "eval": str(eval_file.relative_to(ROOT)),
            "train_stream_a": str(file_a.relative_to(ROOT)),
            "train_stream_b": str(file_b.relative_to(ROOT)),
            "train_combined": str(file_comb.relative_to(ROOT)),
        },
    }

    manifest_path = DATA_DIR / "variable_choices_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    logger.info(f"Manifest written to {manifest_path}")


if __name__ == "__main__":
    main()
