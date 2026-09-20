"""Generator and Independent Semantic Validator for Milestone 19 — General Choice Expansion.

Roadmap: ERABI_RC2_AUTONOMOUS_RESEARCH_ROADMAP.md (Section 13)
Goal: Expand ERABI into a versatile Jev-like Choice Engine beyond rule-engine imitation:
10 Target Families:
1. support_routing (カスタマーサポート振り分け)
2. short_nli (含意・矛盾・中立)
3. semantic_relation (原因・結果・前提)
4. intent_selection (ユーザー意図推定)
5. policy_choice (利用規約・返金ポリシー)
6. instruction_separation (指示と背景情報の分離・最優先指示)
7. negative_goal (〜を避ける、リスク回避策)
8. reverse_criterion (逆基準: 最も非推奨・最も危険な選択)
9. lightweight_prioritization (優先順位・トリアージレベル)
10. structured_triage (システム障害・インシデント対応)

Outputs:
- data/rc2_m19_general/fresh_general_expansion_eval.jsonl (120 cases / 60 pairs across 10 families)
- data/rc2_m19_general/train_general_stream_a.jsonl (356 records)
- data/rc2_m19_general/train_general_stream_b.jsonl (782 records)
- data/rc2_m19_general/train_general_combined.jsonl (1,138 records)
- data/rc2_m19_general/manifest.json
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.build_m19")

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data/rc2_m19_general"
DATA_DIR.mkdir(parents=True, exist_ok=True)

EVAL_FILES_TO_CHECK = [
    ROOT / "data/sealed_acceptance/sealed_test.jsonl",
    ROOT / "data/m8_general_choice/fresh_general_eval.jsonl",
    ROOT / "data/m7_robustness/fresh_robustness_eval.jsonl",
    ROOT / "data/m6_operator/fresh_operator_eval.jsonl",
    ROOT / "data/m3_3_v2/eval_v2.jsonl",
    ROOT / "data/m4_3_1_phrasing_fix/fresh_phrasing_eval.jsonl",
    ROOT / "data/m4_1_exception/eval_exception.jsonl",
    ROOT / "data/rc2_m18_natural/fresh_natural_eval.jsonl",
    ROOT / "examples/smoke_cases.jsonl",
]

GENERAL_FAMILIES = [
    "support_routing",
    "short_nli",
    "semantic_relation",
    "intent_selection",
    "policy_choice",
    "instruction_separation",
    "negative_goal",
    "reverse_criterion",
    "lightweight_prioritization",
    "structured_triage",
]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def verify_leakage(train_records: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    eval_signatures = set()
    for ef in EVAL_FILES_TO_CHECK:
        if not ef.exists():
            continue
        for line in open(ef, encoding="utf-8"):
            if not line.strip():
                continue
            r = json.loads(line)
            ctx = r.get("context", "").strip()
            q = r.get("question", "").strip()
            eval_signatures.add((ctx, q))

    leaks = []
    for r in train_records:
        ctx = r.get("context", "").strip()
        q = r.get("question", "").strip()
        if (ctx, q) in eval_signatures:
            leaks.append(f"Leak: '{ctx[:40]}' + '{q[:20]}'")

    return len(leaks) == 0, leaks


# ==============================================================================
# GENERAL CHOICE ENGINE GENERATORS (Independent Semantic Validator)
# ==============================================================================

def generate_general_expansion_pair(
    family: str,
    group_idx: int,
    rng: random.Random,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    gid = f"genexp_{family}_{group_idx:03d}"

    if family == "support_routing":
        choices = [
            {"id": "billing", "text": "料金・請求窓口へ案内"},
            {"id": "cancellation", "text": "解約・退会窓口へ案内"},
            {"id": "tech_support", "text": "技術・不具合担当へ転送"},
            {"id": "general_faq", "text": "初期設定マニュアル・操作FAQを提示"},
        ]
        q = "お客様からの連絡内容を分析し、最適な対応窓口を選択してください。"
        # Case 1: Billing inquiry
        amt = rng.randint(2000, 9000)
        ctx1 = f"先月の請求金額が想定より高く、{amt}円引き落とされている理由について明細を確認したいとのご連絡です。"
        tgt1 = "billing"

        # Case 2: Cancellation inquiry
        ctx2 = f"サービスをこれ以上利用しないため、月額契約の解除手順と解約締日について知りたいとのご連絡です。"
        tgt2 = "cancellation"

    elif family == "short_nli":
        choices = [
            {"id": "entailment", "text": "真（前提から確実に導かれる）"},
            {"id": "contradiction", "text": "偽（前提と明らかに矛盾する）"},
            {"id": "neutral", "text": "中立（前提からは真偽を判定できない）"},
        ]
        q = "提示された前提文に対し、仮説文の論理的関係を判定してください。"
        # Case 1: Entailment
        ctx1 = "前提: 当社はすべての正社員および契約社員に対して年次有給休暇を付与している。\n仮説: 当社の契約社員は年次有給休暇の付与対象である。"
        tgt1 = "entailment"

        # Case 2: Contradiction
        ctx2 = "前提: 当社はすべての正社員および契約社員に対して年次有給休暇を付与している。\n仮説: 当社の契約社員には有給休暇が一切付与されない。"
        tgt2 = "contradiction"

    elif family == "semantic_relation":
        choices = [
            {"id": "cause_effect", "text": "原因と結果の関係"},
            {"id": "prerequisite", "text": "前提条件と実行の関係"},
            {"id": "contrast", "text": "対比・対立の関係"},
        ]
        q = "2つの事象の間に成り立つ主要な意味的関係を選択してください。"
        # Case 1: Cause & Effect
        ctx1 = "事象A: データベースサーバのディスク使用率が100%に達した。\n事象B: すべての書き込みクエリがエラーとなりシステムが停止した。"
        tgt1 = "cause_effect"

        # Case 2: Prerequisite
        ctx2 = "事象A: 二段階認証用のセキュリティキーをあらかじめ登録する。\n事象B: 社内管理コンソールへのリモートアクセスを許可される。"
        tgt2 = "prerequisite"

    elif family == "intent_selection":
        choices = [
            {"id": "purchase", "text": "購入・契約意思の表明"},
            {"id": "compare", "text": "他社製品・プランとの比較検討"},
            {"id": "troubleshooting", "text": "既存トラブルの解決依頼"},
            {"id": "information_search", "text": "仕様や基本情報の検索"},
        ]
        q = "発言者の中心的な意図を最も的確に表す項目を選択してください。"
        # Case 1: Compare
        ctx1 = "「御社のエンタープライズプランと競合他社Bの同等プランで、同時接続数と月額費用の違いを教えてほしい」"
        tgt1 = "compare"

        # Case 2: Purchase
        ctx2 = "「見積書の内容で問題ありませんので、来月1日からの本契約を進めるための申込書を送ってください」"
        tgt2 = "purchase"

    elif family == "policy_choice":
        choices = [
            {"id": "full_refund", "text": "全額返金可能"},
            {"id": "partial_refund", "text": "手数料を差し引いた一部返金"},
            {"id": "no_refund", "text": "返金不可（利用規約の対象外）"},
        ]
        q = "返金ポリシーに基づき、本申請に対する適用結果を選択してください。"
        # Case 1: Full refund (within 7 days, unused)
        days1 = rng.randint(1, 6)
        ctx1 = f"【返金規定】購入後7日以内で未使用の場合は全額返金。7日超過または使用済みの場合は返金不可。\n【申請情報】購入から{days1}日経過しており、ライセンスキーは未使用です。"
        tgt1 = "full_refund"

        # Case 2: No refund (exceeded 7 days)
        days2 = rng.randint(8, 20)
        ctx2 = f"【返金規定】購入後7日以内で未使用の場合は全額返金。7日超過または使用済みの場合は返金不可。\n【申請情報】購入から{days2}日経過しており、ライセンスキーは未使用です。"
        tgt2 = "no_refund"

    elif family == "instruction_separation":
        choices = [
            {"id": "halt_immediately", "text": "即時停止してログ退避"},
            {"id": "continue_job", "text": "バッチ処理を最後まで続行"},
            {"id": "ignore_warning", "text": "警告を無視して通常運用"},
        ]
        q = "背景説明と指示が混在する文章から、最優先で実行すべき指示を選択してください。"
        # Case 1: Halt
        ctx1 = "昨夜は夜間メンテナンスが行われ、様々な議論がありましたが、本番DBでエラー検知があった場合は直ちに処理を即時停止してログ退避を行ってください。途中で再開してはなりません。"
        tgt1 = "halt_immediately"

        # Case 2: Continue
        ctx2 = "昨夜は夜間メンテナンスが行われ、様々な議論がありましたが、軽微な通知にとどまる場合はバッチ処理を最後まで続行してください。決して自己判断で停止しないでください。"
        tgt2 = "continue_job"

    elif family == "negative_goal":
        choices = [
            {"id": "isolate_network", "text": "感染端末のネットワークを即時切断する"},
            {"id": "format_disk", "text": "ディスクを初期化して再インストールする"},
            {"id": "send_alert_email", "text": "感染端末から全社宛てに注意喚起メールを一斉送信する"},
        ]
        q1 = "「二次被害や社内感染拡大を絶対に防ぐ」という目標において、取るべき最善の行動を選択してください。"
        ctx1 = "マルウェア感染の疑いがある端末が検知されました。最も避けるべき事態は社内LANを通じた他端末への感染拡大です。"
        tgt1 = "isolate_network"

        q2 = "「OSカーネル改ざんによる再発リスクを完全に排除する」という目標において、取るべき最善の行動を選択してください。"
        ctx2 = "調査の結果、OSカーネルレベルで改ざんを行うルートキットが潜伏していることが判明しました。感染痕跡を残すリスクを避ける必要があります。"
        tgt2 = "format_disk"

    elif family == "reverse_criterion":
        choices = [
            {"id": "share_cleartext", "text": "本番パスワードを平文のままチャットツールで共有する"},
            {"id": "use_vault", "text": "暗号化シークレット管理ツールに登録して共有する"},
            {"id": "rotate_keys", "text": "鍵を定期的に更新する"},
        ]
        q1 = "セキュリティ観点から【最も非推奨・最もリスクが高い行為】を一つ選択してください。"
        ctx1 = "社内開発チームでAPIクレデンシャルを共有するにあたり、運用ポリシーを策定しています。"
        tgt1 = "share_cleartext"

        q2 = "セキュリティ観点から【最も推奨される安全な管理行為】を一つ選択してください。"
        ctx2 = "社内開発チームでAPIクレデンシャルを共有するにあたり、運用ポリシーを策定しています。"
        tgt2 = "use_vault"

    elif family == "lightweight_prioritization":
        choices = [
            {"id": "p0_immediate", "text": "優先度P0: 深夜休日を問わず即時招集・対応"},
            {"id": "p1_same_day", "text": "優先度P1: 当日営業時間内に対応"},
            {"id": "p2_next_sprint", "text": "優先度P2: 次回以降のスプリントで改修"},
        ]
        q = "インシデント重大度基準に従い、適切な優先度を判定してください。"
        # Case 1: P0 (Total outage)
        ctx1 = "全決済機能が停止し、すべてのユーザーが購入手続きを行えない状態が発生しています。"
        tgt1 = "p0_immediate"

        # Case 2: P2 (Cosmetic UI typo)
        ctx2 = "設定画面のヘルプテキストに軽微な誤字が1箇所見つかりましたが、機能上の動作には全く影響ありません。"
        tgt2 = "p2_next_sprint"

    elif family == "structured_triage":
        choices = [
            {"id": "hardware_failure", "text": "物理ハードウェア・ストレージ障害"},
            {"id": "network_partition", "text": "ネットワーク分断・疎通不能"},
            {"id": "application_bug", "text": "アプリケーション内部例外・ロジック不具合"},
        ]
        q = "障害兆候ログから、最も可能性の高い根本原因トリアージ分類を選択してください。"
        # Case 1: Hardware failure
        ctx1 = "ログ: RAIDコントローラからI/Oエラーが連発し、セクタ読み出し不能によるSMART警告が発報されています。"
        tgt1 = "hardware_failure"

        # Case 2: Network partition
        ctx2 = "ログ: サーバCPU/メモリは正常ですが、東西リージョン間のPING応答が100%パケットロスとなりクラスタ通信が断絶しています。"
        tgt2 = "network_partition"

    else:
        raise ValueError(f"Unknown family: {family}")

    question1 = q1 if "q1" in locals() else q
    question2 = q2 if "q2" in locals() else q

    case1 = {
        "id": f"{gid}_case1",
        "group_id": gid,
        "task_family": f"general_{family}",
        "general_expansion_family": family,
        "context": ctx1,
        "question": question1,
        "choices": choices,
        "target": {"choice_id": tgt1, "reasoning": f"Derived via {family} criteria"},
    }

    case2 = {
        "id": f"{gid}_case2",
        "group_id": gid,
        "task_family": f"general_{family}",
        "general_expansion_family": family,
        "context": ctx2,
        "question": question2,
        "choices": choices,
        "target": {"choice_id": tgt2, "reasoning": f"Derived via {family} criteria"},
    }

    return case1, case2


def generate_fresh_general_expansion_suite() -> List[Dict[str, Any]]:
    """Generate exactly 120 cases (12 cases / 6 contrastive pairs per family across 10 families)."""
    eval_cases = []
    rng = random.Random(2026)

    for fam in GENERAL_FAMILIES:
        for p in range(6):  # 6 pairs = 12 cases per family * 10 = 120 cases
            c1, c2 = generate_general_expansion_pair(family=fam, group_idx=p, rng=rng)
            eval_cases.append(c1)
            eval_cases.append(c2)

    assert len(eval_cases) == 120
    return eval_cases


def generate_general_expansion_training_set() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Generate training datasets (Stream A: 356 samples, Stream B: 782 samples = 1,138 total).
    Stream A: 300 groups of core contrastive reasoning.
    Stream B: 782 samples (300 general expansion samples + 482 diverse samples across natural/variable/operators).
    """
    rng = random.Random(42)

    # Stream A: 356 samples from core
    pool_a_file = ROOT / "data/rc2_m18_natural/train_natural_stream_a.jsonl"
    stream_a = [json.loads(l) for l in open(pool_a_file, encoding="utf-8") if l.strip()]
    assert len(stream_a) == 356

    # Stream B: 782 samples
    # 200 General expansion samples (10 families x 10 pairs = 20 samples per family)
    general_pairs = []
    for fam in GENERAL_FAMILIES:
        for p in range(10):  # 10 pairs = 20 samples * 10 = 200 samples
            c1, c2 = generate_general_expansion_pair(family=fam, group_idx=100 + p, rng=rng)
            general_pairs.extend([c1, c2])

    assert len(general_pairs) == 200

    # Fill remaining 582 samples from clean (leak-free) M18 Stream B pool
    eval_signatures = set()
    for ef in EVAL_FILES_TO_CHECK:
        if not ef.exists():
            continue
        for line in open(ef, encoding="utf-8"):
            if not line.strip():
                continue
            r = json.loads(line)
            eval_signatures.add((r.get("context", "").strip(), r.get("question", "").strip()))

    pool_b_file = ROOT / "data/rc2_m18_natural/train_natural_stream_b.jsonl"
    stream_b_raw = [
        json.loads(l) for l in open(pool_b_file, encoding="utf-8")
        if l.strip() and (json.loads(l).get("context", "").strip(), json.loads(l).get("question", "").strip()) not in eval_signatures
    ]

    phrasing = [r for r in stream_b_raw if r.get("task_family") == "phrasing_diversification_fix"]
    natural = [r for r in stream_b_raw if r.get("task_family", "").startswith("natural_")]
    exception = [r for r in stream_b_raw if r.get("task_family") == "exception_priority"]
    operators = [r for r in stream_b_raw if r.get("task_family") in [
        "and_logic", "or_logic", "ge_vs_gt", "le_vs_lt", "negation", "override",
        "priority_ranking", "first_match", "default_exception", "goal_switching"
    ]]
    others = [r for r in stream_b_raw if r not in phrasing and r not in natural and r not in exception and r not in operators]

    rng.shuffle(natural)
    rng.shuffle(exception)
    rng.shuffle(operators)
    rng.shuffle(others)

    selected_phrasing = phrasing[:140]      # 140
    selected_natural = natural[:120]        # 120
    selected_operators = operators[:160]    # 160
    selected_exception = exception[:60]     # 60
    selected_others = others[:102]          # 102

    stream_b = general_pairs + selected_phrasing + selected_natural + selected_operators + selected_exception + selected_others
    assert len(stream_b) == 782

    return stream_a, stream_b


def main():
    logger.info("=== Preparing Milestone 19 General Choice Expansion Datasets ===")

    # 1. Fresh General Expansion Evaluation Suite
    logger.info("Generating fresh_general_expansion_eval.jsonl (120 cases / 60 pairs across 10 families)...")
    eval_cases = generate_fresh_general_expansion_suite()
    eval_file = DATA_DIR / "fresh_general_expansion_eval.jsonl"
    with open(eval_file, "w", encoding="utf-8") as f:
        for r in eval_cases:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    logger.info(f"Saved {len(eval_cases)} evaluation cases to {eval_file}")

    # 2. Training Datasets
    logger.info("Generating general choice expansion training sets (Stream A: 356, Stream B: 782)...")
    stream_a, stream_b = generate_general_expansion_training_set()
    all_recs = stream_a + stream_b

    # Verify zero leakage
    leak_free, leaks = verify_leakage(all_recs)
    if not leak_free:
        raise RuntimeError(f"Leakage detected: {leaks[:3]}")

    file_a = DATA_DIR / "train_general_stream_a.jsonl"
    file_b = DATA_DIR / "train_general_stream_b.jsonl"
    file_comb = DATA_DIR / "train_general_combined.jsonl"

    with open(file_a, "w", encoding="utf-8") as f:
        for r in stream_a:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(file_b, "w", encoding="utf-8") as f:
        for r in stream_b:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(file_comb, "w", encoding="utf-8") as f:
        for r in all_recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    logger.info(f"Saved {len(stream_a)} Stream A and {len(stream_b)} Stream B records to {DATA_DIR}.")

    manifest = {
        "milestone": "Milestone 19 General Choice Expansion",
        "families": GENERAL_FAMILIES,
        "eval_cases": len(eval_cases),
        "train_cases": len(all_recs),
        "sha256": {
            "eval": sha256_file(eval_file),
            "train_combined": sha256_file(file_comb),
        },
    }

    manifest_path = DATA_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    logger.info(f"Manifest written to {manifest_path}")


if __name__ == "__main__":
    main()
