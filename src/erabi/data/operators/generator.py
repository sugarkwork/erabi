"""Operator dataset generator for Milestone 6 (ERABI).

Generates paired contrastive examples for 10 core logical operators across 5 domains:
1. AND (conjunction)
2. OR (disjunction)
3. GE_VS_GT (inclusive vs exclusive upper bound)
4. LE_VS_LT (inclusive vs exclusive lower bound)
5. OVERRIDE (standard rule vs priority override)
6. DEFAULT_EXCEPTION (default baseline vs conditional exception)
7. FIRST_MATCH (top-to-bottom rule precedence)
8. PRIORITY_RANKING (tiered priority hierarchy)
9. NEGATION (positive vs negated conditional)
10. GOAL_SWITCHING (trade-off objective reversal)

Strict split isolation:
- train: families 'TR_1', 'TR_2'
- dev: family 'DEV'
- fresh: families 'FR_1', 'FR_2' (completely unseen operator phrasing expressions)
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


OPERATOR_FAMILIES = [
    "and_logic",
    "or_logic",
    "ge_vs_gt",
    "le_vs_lt",
    "override",
    "default_exception",
    "first_match",
    "priority_ranking",
    "negation",
    "goal_switching",
]

DOMAINS = [
    "inventory",
    "server",
    "game",
    "delivery",
    "support",
]


def generate_and_logic_pair(group_idx: int, split: str, domain: str, rng: random.Random) -> List[Dict[str, Any]]:
    # AND requires BOTH conditions to hold.
    # Case 1: Cond A True, Cond B True -> Action TRUE
    # Case 2: Cond A True, Cond B False -> Action FALSE
    if split == "train":
        tmpl = "条件Aと条件Bの両方を満たす場合は{act_true}、そうでない場合は{act_false}を選択してください。"
    elif split == "dev":
        tmpl = "条件Aであり、かつ条件Bでもある状況では{act_true}、片方でも満たさなければ{act_false}を選びます。"
    else:  # fresh
        tmpl = "条件Aと条件Bの双方が同時に成立しているときに限り{act_true}とし、二条件が揃わないときは{act_false}としてください。"

    if domain == "inventory":
        ctx1 = "在庫数は50個で基準を満たしています。検品証明書も受領済みです。"
        ctx2 = "在庫数は50個で基準を満たしています。検品証明書は未受領です。"
        c_true, c_false = ("ship", "出荷する"), ("hold", "保留する")
    elif domain == "server":
        ctx1 = "CPU使用率は安全圏内です。メモリ空き容量も十分に確保されています。"
        ctx2 = "CPU使用率は安全圏内です。メモリ空き容量は不足しています。"
        c_true, c_false = ("approve", "デプロイ承認"), ("reject", "デプロイ拒否")
    elif domain == "game":
        ctx1 = "ボスのHPは20%以下です。必殺技ゲージも最大まで溜まっています。"
        ctx2 = "ボスのHPは20%以下です。必殺技ゲージはまだ溜まっていません。"
        c_true, c_false = ("ultimate", "必殺技を発動する"), ("attack", "通常攻撃を行う")
    elif domain == "delivery":
        ctx1 = "配達先は配送可能エリア内です。希望配達時間帯も営業時間内です。"
        ctx2 = "配達先は配送可能エリア内です。希望配達時間帯は営業時間外です。"
        c_true, c_false = ("accept", "配達を受諾する"), ("reschedule", "日時再調整を求める")
    else:  # support
        ctx1 = "本人確認書類は提出済みです。利用規約への同意も確認できました。"
        ctx2 = "本人確認書類は提出済みです。利用規約への同意はまだ確認できていません。"
        c_true, c_false = ("issue", "アカウントを発行する"), ("guide", "同意手続きを案内する")

    q_text = tmpl.format(act_true=c_true[1], act_false=c_false[1])

    choices = [
        {"id": c_true[0], "text": c_true[1]},
        {"id": c_false[0], "text": c_false[1]},
    ]
    if rng.random() < 0.5:
        choices.reverse()

    r1 = {
        "id": f"m6-op-{split}-{group_idx:04d}-c1",
        "group_id": f"m6-grp-{split}-{group_idx:04d}",
        "task_family": "and_logic",
        "domain": domain,
        "split": split,
        "context": ctx1,
        "question": q_text,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": c_true[0]},
        "case_kind": "both_true",
    }
    r2 = {
        "id": f"m6-op-{split}-{group_idx:04d}-c2",
        "group_id": f"m6-grp-{split}-{group_idx:04d}",
        "task_family": "and_logic",
        "domain": domain,
        "split": split,
        "context": ctx2,
        "question": q_text,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": c_false[0]},
        "case_kind": "one_false",
    }
    return [r1, r2]


def generate_or_logic_pair(group_idx: int, split: str, domain: str, rng: random.Random) -> List[Dict[str, Any]]:
    # OR requires AT LEAST ONE condition to hold.
    # Case 1: Cond A True, Cond B False -> Action TRUE (since at least one is True)
    # Case 2: Cond A False, Cond B False -> Action FALSE
    if split == "train":
        tmpl = "条件Aまたは条件Bの少なくとも一方を満たす場合は{act_true}、どちらも満たさない場合は{act_false}を選択してください。"
    elif split == "dev":
        tmpl = "条件Aか条件Bのいずれかが成立していれば{act_true}、双方とも成立していなければ{act_false}とします。"
    else:  # fresh
        tmpl = "条件Aないし条件Bのうち一方でも充足していれば{act_true}を適用し、両条件とも未充足であるときに限って{act_false}を適用してください。"

    if domain == "inventory":
        ctx1 = "倉庫Aには在庫があります。倉庫Bには在庫がありません。"
        ctx2 = "倉庫Aには在庫がありません。倉庫Bにも在庫がありません。"
        c_true, c_false = ("confirm", "受注を確定する"), ("notify", "欠品を通知する")
    elif domain == "server":
        ctx1 = "第一監視ノードから応答があります。第二監視ノードからは応答がありません。"
        ctx2 = "第一監視ノードから応答がありません。第二監視ノードからも応答がありません。"
        c_true, c_false = ("keep", "通常稼働を継続する"), ("failover", "予備系へ切り替える")
    elif domain == "game":
        ctx1 = "毒状態になっています。麻痺状態にはなっていません。"
        ctx2 = "毒状態にはなっていません。麻痺状態にもなっていません。"
        c_true, c_false = ("cure", "万能薬を使用する"), ("wait", "待機する")
    elif domain == "delivery":
        ctx1 = "置き配の事前指定があります。宅配ボックスの利用許可はありません。"
        ctx2 = "置き配の事前指定はありません。宅配ボックスの利用許可もありません。"
        c_true, c_false = ("leave", "非対面で留め置く"), ("hand", "対面で手渡す")
    else:  # support
        ctx1 = "プレミアム会員資格を保有しています。特別クーポンは所持していません。"
        ctx2 = "プレミアム会員資格を保有していません。特別クーポンも所持していません。"
        c_true, c_false = ("priority_lane", "優先レーンに案内する"), ("regular_lane", "一般窓口に案内する")

    q_text = tmpl.format(act_true=c_true[1], act_false=c_false[1])

    choices = [
        {"id": c_true[0], "text": c_true[1]},
        {"id": c_false[0], "text": c_false[1]},
    ]
    if rng.random() < 0.5:
        choices.reverse()

    r1 = {
        "id": f"m6-op-{split}-{group_idx:04d}-c1",
        "group_id": f"m6-grp-{split}-{group_idx:04d}",
        "task_family": "or_logic",
        "domain": domain,
        "split": split,
        "context": ctx1,
        "question": q_text,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": c_true[0]},
        "case_kind": "one_true",
    }
    r2 = {
        "id": f"m6-op-{split}-{group_idx:04d}-c2",
        "group_id": f"m6-grp-{split}-{group_idx:04d}",
        "task_family": "or_logic",
        "domain": domain,
        "split": split,
        "context": ctx2,
        "question": q_text,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": c_false[0]},
        "case_kind": "both_false",
    }
    return [r1, r2]


def generate_ge_vs_gt_pair(group_idx: int, split: str, domain: str, rng: random.Random) -> List[Dict[str, Any]]:
    # Context has Value == Threshold exactly.
    # Question 1 asks for ">= Threshold" (inclusive: threshold is included -> True)
    # Question 2 asks for "> Threshold" (exclusive: threshold is NOT strictly greater -> False)
    val = rng.choice([20, 30, 50, 100])
    
    if split == "train":
        train_templates = [
            (
                f"数値が{val}以上であれば{{act_true}}、そうでなければ{{act_false}}を選んでください。",
                f"数値が{val}を超える（より大きい）場合は{{act_true}}、そうでなければ{{act_false}}を選んでください。",
            ),
            (
                f"目標値{val}をクリアしていれば{{act_true}}、届かなければ{{act_false}}としてください。",
                f"目標値{val}を上回る実績であれば{{act_true}}、そうでなければ{{act_false}}としてください。",
            ),
            (
                f"{val}以上の数値を満たす場合は{{act_true}}、満たさない場合は{{act_false}}を選定してください。",
                f"{val}より大きい数値の場合に限り{{act_true}}、そうでない場合は{{act_false}}を選定してください。",
            ),
            (
                f"数量が{val}を下回っていなければ{{act_true}}、下回っていれば{{act_false}}を適用してください。",
                f"数量が{val}を超過している場合は{{act_true}}、超過していなければ{{act_false}}を適用してください。",
            ),
        ]
        q_ge, q_gt = train_templates[group_idx % len(train_templates)]
    elif split == "dev":
        q_ge = f"基準値{val}に達していれば{{act_true}}、{val}未満なら{{act_false}}としてください。"
        q_gt = f"基準値{val}を上回っていれば{{act_true}}、{val}以下にとどまるなら{{act_false}}としてください。"
    else:  # fresh
        q_ge = f"数量が{val}を下回らない（{val}を含む）場合は{{act_true}}、欠落していれば{{act_false}}を適用してください。"
        q_gt = f"数量が{val}の枠を厳密に超過している場合に限り{{act_true}}、超過していなければ{{act_false}}を適用してください。"

    if domain == "inventory":
        ctx = f"現在の倉庫在庫数はちょうど{val}個です。"
        act_t, act_f = ("ship", "出荷する"), ("delay", "出荷を見合わせる")
    elif domain == "server":
        ctx = f"計測された応答レイテンシはちょうど{val}msです。"
        act_t, act_f = ("alert", "警告通知を発出する"), ("pass", "正常とみなす")
    elif domain == "game":
        ctx = f"キャラクターの経験値はちょうど{val}ポイントです。"
        act_t, act_f = ("rank_up", "ランクアップを適用する"), ("stay", "現状を維持する")
    elif domain == "delivery":
        ctx = f"荷物の重量はちょうど{val}kgと計量されました。"
        act_t, act_f = ("heavy_fee", "大型加算を適用する"), ("standard_fee", "通常運賃を適用する")
    else:  # support
        ctx = f"顧客の年間購入金額はちょうど{val}万円です。"
        act_t, act_f = ("gold_tier", "ゴールド待遇を付与する"), ("silver_tier", "シルバー待遇を維持する")

    choices = [
        {"id": act_t[0], "text": act_t[1]},
        {"id": act_f[0], "text": act_f[1]},
    ]
    if rng.random() < 0.5:
        choices.reverse()

    r1 = {
        "id": f"m6-op-{split}-{group_idx:04d}-c1",
        "group_id": f"m6-grp-{split}-{group_idx:04d}",
        "task_family": "ge_vs_gt",
        "domain": domain,
        "split": split,
        "context": ctx,
        "question": q_ge.format(act_true=act_t[1], act_false=act_f[1]),
        "choices": choices,
        "target": {"kind": "hard", "choice_id": act_t[0]},
        "case_kind": "inclusive_match",
    }
    r2 = {
        "id": f"m6-op-{split}-{group_idx:04d}-c2",
        "group_id": f"m6-grp-{split}-{group_idx:04d}",
        "task_family": "ge_vs_gt",
        "domain": domain,
        "split": split,
        "context": ctx,
        "question": q_gt.format(act_true=act_t[1], act_false=act_f[1]),
        "choices": choices,
        "target": {"kind": "hard", "choice_id": act_f[0]},
        "case_kind": "exclusive_unmatch",
    }
    return [r1, r2]


def generate_le_vs_lt_pair(group_idx: int, split: str, domain: str, rng: random.Random) -> List[Dict[str, Any]]:
    # Context has Value == Threshold exactly.
    # Question 1 asks for "<= Threshold" (inclusive: threshold is included -> True)
    # Question 2 asks for "< Threshold" (exclusive: threshold is NOT strictly less -> False)
    val = rng.choice([15, 25, 40, 80])

    if split == "train":
        train_templates = [
            (
                f"数値が{val}以下であれば{{act_true}}、そうでなければ{{act_false}}を選んでください。",
                f"数値が{val}未満（より小さい）場合は{{act_true}}、そうでなければ{{act_false}}を選んでください。",
            ),
            (
                f"許容枠{val}に収まっている場合は{{act_true}}、枠を超えるなら{{act_false}}としてください。",
                f"許容枠{val}を下回る水準のときは{{act_true}}、そうでなければ{{act_false}}としてください。",
            ),
            (
                f"{val}以下の範囲であれば{{act_true}}、上限を突破している場合は{{act_false}}を選定してください。",
                f"{val}より少ない数値の場合に限り{{act_true}}、そうでない場合は{{act_false}}を選定してください。",
            ),
            (
                f"数値が{val}を超過していなければ{{act_true}}、超過していれば{{act_false}}を適用してください。",
                f"数値が{val}に満たない場合は{{act_true}}、満たしていれば{{act_false}}を適用してください。",
            ),
        ]
        q_le, q_lt = train_templates[group_idx % len(train_templates)]
    elif split == "dev":
        q_le = f"基準値{val}以内に収まっていれば{{act_true}}、{val}を超えていれば{{act_false}}としてください。"
        q_lt = f"基準値{val}を下回っていれば{{act_true}}、{val}以上なら{{act_false}}としてください。"
    else:  # fresh
        q_le = f"数値が上限{val}を超過しない（{val}を含む）範囲にとどまる場合は{{act_true}}、上限突破時は{{act_false}}を適用してください。"
        q_lt = f"数値が{val}に満たない（厳密なショート）状態に限り{{act_true}}、{val}に到達していれば{{act_false}}を適用してください。"

    if domain == "inventory":
        ctx = f"発注残数はちょうど{val}個です。"
        act_t, act_f = ("reorder", "追加発注を行う"), ("hold_order", "発注を見送る")
    elif domain == "server":
        ctx = f"現在のシステムエラー件数はちょうど{val}件です。"
        act_t, act_f = ("allow_release", "リリースを許可する"), ("block_release", "リリースをブロックする")
    elif domain == "game":
        ctx = f"プレイヤーの残り体力はちょうど{val}です。"
        act_t, act_f = ("use_potion", "回復薬を飲む"), ("keep_fighting", "そのまま戦う")
    elif domain == "delivery":
        ctx = f"荷物の梱包サイズ合計はちょうど{val}cmです。"
        act_t, act_f = ("small_box", "小型区分で梱包する"), ("large_box", "大型区分で梱包する")
    else:  # support
        ctx = f"保留中の問い合わせ件数はちょうど{val}件です。"
        act_t, act_f = ("normal_shift", "通常体制で対応する"), ("emergency_shift", "増員体制を発令する")

    choices = [
        {"id": act_t[0], "text": act_t[1]},
        {"id": act_f[0], "text": act_f[1]},
    ]
    if rng.random() < 0.5:
        choices.reverse()

    r1 = {
        "id": f"m6-op-{split}-{group_idx:04d}-c1",
        "group_id": f"m6-grp-{split}-{group_idx:04d}",
        "task_family": "le_vs_lt",
        "domain": domain,
        "split": split,
        "context": ctx,
        "question": q_le.format(act_true=act_t[1], act_false=act_f[1]),
        "choices": choices,
        "target": {"kind": "hard", "choice_id": act_t[0]},
        "case_kind": "inclusive_lower_match",
    }
    r2 = {
        "id": f"m6-op-{split}-{group_idx:04d}-c2",
        "group_id": f"m6-grp-{split}-{group_idx:04d}",
        "task_family": "le_vs_lt",
        "domain": domain,
        "split": split,
        "context": ctx,
        "question": q_lt.format(act_true=act_t[1], act_false=act_f[1]),
        "choices": choices,
        "target": {"kind": "hard", "choice_id": act_f[0]},
        "case_kind": "exclusive_lower_unmatch",
    }
    return [r1, r2]


def generate_override_pair(group_idx: int, split: str, domain: str, rng: random.Random) -> List[Dict[str, Any]]:
    # Standard rule prescribes Action A. But if Override Condition is met, Override rule takes precedence -> Action B.
    # Case 1: Override Condition is NOT met -> Standard Action A
    # Case 2: Override Condition IS met -> Override Action B
    if split == "train":
        train_templates = [
            "通常ルールでは{act_std}としますが、上書き条件（緊急または管理者指示）がある場合はルールを上書きして{act_ovr}としてください。",
            "基本規定は{act_std}です。ただし特例指定が発効したときは基本規定に優先して{act_ovr}を適用します。",
            "標準対応として{act_std}を行いますが、例外指定フラグがオンのときは本指定が優先され、{act_ovr}を選択してください。",
            "通常手順の{act_std}に従いますが、上書きフラグが有効な場合は上書きして{act_ovr}を実行してください。",
        ]
        q_tmpl = train_templates[group_idx % len(train_templates)]
    elif split == "dev":
        q_tmpl = "基本規定は{act_std}です。ただし、特例指定が発効したときは基本規定に優先して{act_ovr}を適用します。"
    else:  # fresh
        q_tmpl = "原則規程として{act_std}を行いますが、例外指定フラグがオンのときは本指定が通常規程を塗り替えて最優先され、{act_ovr}を選択しなければなりません。"

    if domain == "inventory":
        ctx1 = "定期発注スケジュールです。特例指定フラグはオフです。"
        ctx2 = "定期発注スケジュールです。特例指定フラグがオンになっています。"
        act_std, act_ovr = ("batch_ship", "一括定期発送"), ("express_ship", "緊急特急発送")
    elif domain == "server":
        ctx1 = "通常アクセス集中を検知。メンテナンス除外フラグは未設定です。"
        ctx2 = "通常アクセス集中を検知。メンテナンス除外フラグが設定されています。"
        act_std, act_ovr = ("auto_scale", "自動スケールアウト"), ("bypass_scale", "制限をバイパス")
    elif domain == "game":
        ctx1 = "通常ターン順序です。割り込み特権スキルは未発動です。"
        ctx2 = "通常ターン順序です。割り込み特権スキルが発動しました。"
        act_std, act_ovr = ("normal_turn", "ターン順に従い行動"), ("interrupt_turn", "即時割り込みを実行")
    elif domain == "delivery":
        ctx1 = "一般ルート配送です。特別配送指示書は添付されていません。"
        ctx2 = "一般ルート配送です。特別配送指示書が添付されています。"
        act_std, act_ovr = ("regular_route", "標準ルートで巡回"), ("direct_route", "直行便に切り替え")
    else:  # support
        ctx1 = "標準問い合わせ手順です。役員直轄フラグは立っていません。"
        ctx2 = "標準問い合わせ手順です。役員直轄フラグが立っています。"
        act_std, act_ovr = ("standard_reply", "順次回答キューに投入"), ("escalate_ceo", "役員直轄案件として即時対応")

    choices = [
        {"id": act_std[0], "text": act_std[1]},
        {"id": act_ovr[0], "text": act_ovr[1]},
    ]
    if rng.random() < 0.5:
        choices.reverse()

    r1 = {
        "id": f"m6-op-{split}-{group_idx:04d}-c1",
        "group_id": f"m6-grp-{split}-{group_idx:04d}",
        "task_family": "override",
        "domain": domain,
        "split": split,
        "context": ctx1,
        "question": q_tmpl.format(act_std=act_std[1], act_ovr=act_ovr[1]),
        "choices": choices,
        "target": {"kind": "hard", "choice_id": act_std[0]},
        "case_kind": "standard_applies",
    }
    r2 = {
        "id": f"m6-op-{split}-{group_idx:04d}-c2",
        "group_id": f"m6-grp-{split}-{group_idx:04d}",
        "task_family": "override",
        "domain": domain,
        "split": split,
        "context": ctx2,
        "question": q_tmpl.format(act_std=act_std[1], act_ovr=act_ovr[1]),
        "choices": choices,
        "target": {"kind": "hard", "choice_id": act_ovr[0]},
        "case_kind": "override_fires",
    }
    return [r1, r2]


def generate_default_exception_pair(group_idx: int, split: str, domain: str, rng: random.Random) -> List[Dict[str, Any]]:
    # Baseline default applies unless a specific exception occurs.
    # Case 1: Normal situation -> Default Action
    # Case 2: Exception situation -> Exception Action
    if split == "train":
        q_tmpl = "原則として{act_def}とします。ただし{cond_exc}の場合は例外として{act_exc}としてください。"
    elif split == "dev":
        q_tmpl = "デフォルト方針は{act_def}です。{cond_exc}に該当するケースに限り例外扱いとし、{act_exc}を選択します。"
    else:  # fresh
        q_tmpl = "別記の例外事項（{cond_exc}）に該当しない限り通則の{act_def}に準拠し、例外要件を満たすときのみ例外規定{act_exc}を採択してください。"

    if domain == "inventory":
        ctx1 = "返品申請。未開封で受領から7日以内です。セール品ではありません。"
        ctx2 = "返品申請。未開封で受領から7日以内ですが、セール対象品です。"
        cond_exc = "セール対象品"
        act_def, act_exc = ("refund_full", "全額返金を受理"), ("refund_deny", "セール品につき返品不可")
    elif domain == "server":
        ctx1 = "夜間自動バックアップジョブ。平日深夜です。祝前日ではありません。"
        ctx2 = "夜間自動バックアップジョブ。平日深夜ですが、祝前日に指定されています。"
        cond_exc = "祝前日"
        act_def, act_exc = ("run_backup", "定期バックアップ実行"), ("skip_backup", "バックアップを延期")
    elif domain == "game":
        ctx1 = "宝箱を発見。鍵がかかっています。罠の兆候はありません。"
        ctx2 = "宝箱を発見。鍵がかかっています。微弱な魔力反応（罠の兆候）があります。"
        cond_exc = "罠の兆候がある場合"
        act_def, act_exc = ("open_chest", "そのまま開錠する"), ("disarm_trap", "罠解除を先行する")
    elif domain == "delivery":
        ctx1 = "雨天時の配達。通常の雨具を着用しています。強風警報は出ていません。"
        ctx2 = "雨天時の配達。通常の雨具を着用していますが、強風警報が発令されています。"
        cond_exc = "強風警報発令時"
        act_def, act_exc = ("proceed_delivery", "配達を続行"), ("pause_delivery", "安全のため待機")
    else:  # support
        ctx1 = "パスワード再設定依頼。登録メールアドレスが利用可能です。海外IPではありません。"
        ctx2 = "パスワード再設定依頼。登録メールアドレスが利用可能ですが、海外IPからの接続です。"
        cond_exc = "海外IPからのアクセス"
        act_def, act_exc = ("send_reset_mail", "リセットメール送信"), ("require_2fa", "二段階認証を要求")

    choices = [
        {"id": act_def[0], "text": act_def[1]},
        {"id": act_exc[0], "text": act_exc[1]},
    ]
    if rng.random() < 0.5:
        choices.reverse()

    r1 = {
        "id": f"m6-op-{split}-{group_idx:04d}-c1",
        "group_id": f"m6-grp-{split}-{group_idx:04d}",
        "task_family": "default_exception",
        "domain": domain,
        "split": split,
        "context": ctx1,
        "question": q_tmpl.format(act_def=act_def[1], cond_exc=cond_exc, act_exc=act_exc[1]),
        "choices": choices,
        "target": {"kind": "hard", "choice_id": act_def[0]},
        "case_kind": "default_applies",
    }
    r2 = {
        "id": f"m6-op-{split}-{group_idx:04d}-c2",
        "group_id": f"m6-grp-{split}-{group_idx:04d}",
        "task_family": "default_exception",
        "domain": domain,
        "split": split,
        "context": ctx2,
        "question": q_tmpl.format(act_def=act_def[1], cond_exc=cond_exc, act_exc=act_exc[1]),
        "choices": choices,
        "target": {"kind": "hard", "choice_id": act_exc[0]},
        "case_kind": "exception_applies",
    }
    return [r1, r2]


def generate_first_match_pair(group_idx: int, split: str, domain: str, rng: random.Random) -> List[Dict[str, Any]]:
    # Sequential rule list: Rule 1, Rule 2, Rule 3. First rule that matches wins.
    # Case 1: Both Rule 1 and Rule 2 match -> Rule 1 wins (first match precedence)
    # Case 2: Rule 1 does NOT match, Rule 2 matches -> Rule 2 wins
    if split == "train":
        q_tmpl = "上から順に判定し、最初に一致したルールを適用してください：1. {cond1}なら{act1}、2. {cond2}なら{act2}、3. いずれでもなければ{act3}。"
    elif split == "dev":
        q_tmpl = "以下の規則を上位から順次評価し、初めに合致したものを採用します：[規則1] {cond1}時は{act1}、[規則2] {cond2}時は{act2}、[規則3] その他は{act3}。"
    else:  # fresh
        q_tmpl = "箇条書きの先頭順に走査し、初手で合致した規程を確定採択してください（後続は無視）：第1項：{cond1} $\\implies$ {act1}／第2項：{cond2} $\\implies$ {act2}／第3項：未該当 $\\implies$ {act3}。"

    if domain == "inventory":
        cond1, cond2 = "要冷凍マークあり", "賞味期限3日以内"
        act1, act2, act3 = ("freeze", "冷凍倉庫へ格納"), ("expedite", "最優先で早期出荷"), ("standard_store", "常温棚へ格納")
        ctx1 = "荷札：要冷凍マークあり。賞味期限は2日後（3日以内）です。"  # both match -> act1
        ctx2 = "荷札：常温指定（冷凍マークなし）。賞味期限は2日後（3日以内）です。"  # rule 1 fails, rule 2 matches -> act2
    elif domain == "server":
        cond1, cond2 = "重度障害アラート", "中度負荷アラート"
        act1, act2, act3 = ("reboot", "システム即時再起動"), ("throttle", "リクエスト流量制限"), ("monitor", "静観・監視継続")
        ctx1 = "監視ログ：重度障害アラート検知。同時に中度負荷アラートも検知。"
        ctx2 = "監視ログ：重度障害アラートは未検知。中度負荷アラートを検知。"
    elif domain == "game":
        cond1, cond2 = "味方のHPが0（戦闘不能）", "味方のHPが30%以下"
        act1, act2, act3 = ("revive", "蘇生魔法を使用"), ("heal", "大回復魔法を使用"), ("defend", "防御姿勢をとる")
        ctx1 = "味方AはHP0（戦闘不能状態）。味方BはHP25%（30%以下）です。"
        ctx2 = "味方は誰も戦闘不能ではありません。味方BはHP25%（30%以下）です。"
    elif domain == "delivery":
        cond1, cond2 = "危険物指定あり", "割れ物注意指定あり"
        act1, act2, act3 = ("hazmat", "専用防護便で輸送"), ("cushion", "緩衝材強化便で輸送"), ("normal_cargo", "一般貨物便で輸送")
        ctx1 = "貨物伝票：危険物指定あり。割れ物注意の表記もあります。"
        ctx2 = "貨物伝票：危険物指定なし。割れ物注意の表記があります。"
    else:  # support
        cond1, cond2 = "不当請求の疑い報告", "プラン変更の相談"
        act1, act2, act3 = ("legal_dept", "法務・コンプライアンス窓口"), ("sales_dept", "営業・プラン案内窓口"), ("general_faq", "総合FAQ案内")
        ctx1 = "相談内容：「同じ月に二重請求されている。ついでにプラン見直しも検討したい」"
        ctx2 = "相談内容：「請求金額に誤りはないが、お得なプラン見直しを検討したい」"

    choices = [
        {"id": act1[0], "text": act1[1]},
        {"id": act2[0], "text": act2[1]},
        {"id": act3[0], "text": act3[1]},
    ]
    if rng.random() < 0.5:
        choices.reverse()

    r1 = {
        "id": f"m6-op-{split}-{group_idx:04d}-c1",
        "group_id": f"m6-grp-{split}-{group_idx:04d}",
        "task_family": "first_match",
        "domain": domain,
        "split": split,
        "context": ctx1,
        "question": q_tmpl.format(cond1=cond1, act1=act1[1], cond2=cond2, act2=act2[1], act3=act3[1]),
        "choices": choices,
        "target": {"kind": "hard", "choice_id": act1[0]},
        "case_kind": "rule1_first_match",
    }
    r2 = {
        "id": f"m6-op-{split}-{group_idx:04d}-c2",
        "group_id": f"m6-grp-{split}-{group_idx:04d}",
        "task_family": "first_match",
        "domain": domain,
        "split": split,
        "context": ctx2,
        "question": q_tmpl.format(cond1=cond1, act1=act1[1], cond2=cond2, act2=act2[1], act3=act3[1]),
        "choices": choices,
        "target": {"kind": "hard", "choice_id": act2[0]},
        "case_kind": "rule2_second_match",
    }
    return [r1, r2]


def generate_priority_ranking_pair(group_idx: int, split: str, domain: str, rng: random.Random) -> List[Dict[str, Any]]:
    # Explicit hierarchy between conflicting options.
    # Case 1: Option A > Option B -> Option A wins
    # Case 2: Option B > Option A -> Option B wins
    if split == "train":
        q_order1 = "優先順位（高＞低）：【{opt_a}】＞【{opt_b}】。両方の要件が存在する場合、優先順位に従って対応を選んでください。"
        q_order2 = "優先順位（高＞低）：【{opt_b}】＞【{opt_a}】。両方の要件が存在する場合、優先順位に従って対応を選んでください。"
    elif split == "dev":
        q_order1 = "優先度序列：最優先は{opt_a}、次点が{opt_b}です。競合時は高優先度側の指示を遂行してください。"
        q_order2 = "優先度序列：最優先は{opt_b}、次点が{opt_a}です。競合時は高優先度側の指示を遂行してください。"
    else:  # fresh
        q_order1 = "格付け基準（プライオリティ）：『{opt_a}』が『{opt_b}』より上位に位置づけられています。競合事象においては上位格付けを選択してください。"
        q_order2 = "格付け基準（プライオリティ）：『{opt_b}』が『{opt_a}』より上位に位置づけられています。競合事象においては上位格付けを選択してください。"

    if domain == "inventory":
        ctx = "案件状況：直営店向けの納品要請と、海外提携先向けの納品要請が同一ロットに対して重複発生しています。"
        opt_a = ("direct_store", "直営店への納品")
        opt_b = ("overseas_partner", "海外提携先への納品")
    elif domain == "server":
        ctx = "リソース競合：決済処理トランザクションと、データ集計バッチが同一DBロックを要求しています。"
        opt_a = ("payment_tx", "決済トランザクションの処理")
        opt_b = ("batch_job", "集計バッチの処理")
    elif domain == "game":
        ctx = "戦況：拠点の防衛目標と、敵リーダーの撃破目標が同時にタイムリミットを迎えています。"
        opt_a = ("defend_base", "拠点の防衛")
        opt_b = ("kill_leader", "敵リーダーの撃破")
    elif domain == "delivery":
        ctx = "配車要請：医薬品の緊急配送と、生鮮食品の即日配送で同一車両が競合しています。"
        opt_a = ("pharma_delivery", "医薬品の緊急搬送")
        opt_b = ("fresh_food", "生鮮食品の即時配達")
    else:  # support
        ctx = "相談受付：公的機関からの照会要請と、VIP顧客からの個別相談が同時着信しています。"
        opt_a = ("public_inquiry", "公的機関の照会対応")
        opt_b = ("vip_client", "VIP顧客の個別対応")

    choices = [
        {"id": opt_a[0], "text": opt_a[1]},
        {"id": opt_b[0], "text": opt_b[1]},
    ]
    if rng.random() < 0.5:
        choices.reverse()

    r1 = {
        "id": f"m6-op-{split}-{group_idx:04d}-c1",
        "group_id": f"m6-grp-{split}-{group_idx:04d}",
        "task_family": "priority_ranking",
        "domain": domain,
        "split": split,
        "context": ctx,
        "question": q_order1.format(opt_a=opt_a[1], opt_b=opt_b[1]),
        "choices": choices,
        "target": {"kind": "hard", "choice_id": opt_a[0]},
        "case_kind": "rank_a_wins",
    }
    r2 = {
        "id": f"m6-op-{split}-{group_idx:04d}-c2",
        "group_id": f"m6-grp-{split}-{group_idx:04d}",
        "task_family": "priority_ranking",
        "domain": domain,
        "split": split,
        "context": ctx,
        "question": q_order2.format(opt_a=opt_a[1], opt_b=opt_b[1]),
        "choices": choices,
        "target": {"kind": "hard", "choice_id": opt_b[0]},
        "case_kind": "rank_b_wins",
    }
    return [r1, r2]


def generate_negation_pair(group_idx: int, split: str, domain: str, rng: random.Random) -> List[Dict[str, Any]]:
    # Positive condition vs Negated condition on identical context.
    # Context satisfies Condition C.
    # Question 1: If C is met -> Action POS, else Action NEG. Target = POS
    # Question 2: If C is NOT met -> Action POS, else Action NEG. Target = NEG
    if split == "train":
        train_templates = [
            (
                "状況が【{cond}】に該当する場合は{act_pos}、そうでない場合は{act_neg}を選択してください。",
                "状況が【{cond}】に該当しない（ではない）場合は{act_pos}、そうでない場合は{act_neg}を選択してください。",
            ),
            (
                "【{cond}】が確認できる状況では{act_pos}、確認できない場合は{act_neg}を選びます。",
                "【{cond}】が確認できない（該当がない）状況では{act_pos}、確認できる場合は{act_neg}を選びます。",
            ),
            (
                "【{cond}】の条件を満たす場合は{act_pos}、満たさない場合は{act_neg}を適用してください。",
                "【{cond}】の条件を満たさない（非該当の）場合は{act_pos}、満たす場合は{act_neg}を適用してください。",
            ),
            (
                "【{cond}】であるときは{act_pos}、そうではないときは{act_neg}を決定してください。",
                "【{cond}】ではないときは{act_pos}、そうであるときは{act_neg}を決定してください。",
            ),
        ]
        q_pos, q_neg = train_templates[group_idx % len(train_templates)]
    elif split == "dev":
        q_pos = "【{cond}】が成立しているなら{act_pos}、不成立なら{act_neg}を選びます。"
        q_neg = "【{cond}】が成立していない場合に限り{act_pos}、成立している場合は{act_neg}を選びます。"
    else:  # fresh
        q_pos = "【{cond}】の事象を満たしているケースでは{act_pos}を決定し、満たしていないケースでは{act_neg}を決定してください。"
        q_neg = "【{cond}】の事象から除外されている（満たさない）ケースでは{act_pos}を決定し、事象を満たしている場合は{act_neg}を決定してください。"

    if domain == "inventory":
        ctx = "判定対象の製品ロット：品質基準検査をクリアしています。"
        cond = "品質検査合格"
        act_pos, act_neg = ("approve_lot", "出荷合格ロットとして登録"), ("reinspect_lot", "再検査キューへ回付")
    elif domain == "server":
        ctx = "通信パケット：送信元IPがホワイトリストに登録されています。"
        cond = "ホワイトリスト登録済み"
        act_pos, act_neg = ("accept_packet", "通信を許可して通過"), ("drop_packet", "パケットを遮断破棄")
    elif domain == "game":
        ctx = "対象の敵キャラクター：水属性シールドを展開しています。"
        cond = "水属性シールド展開中"
        act_pos, act_neg = ("use_thunder", "雷属性攻撃でシールド破壊"), ("use_physical", "通常物理攻撃")
    elif domain == "delivery":
        ctx = "配送依頼：送り状に日時指定ラベルが貼付されています。"
        cond = "日時指定あり"
        act_pos, act_neg = ("lock_time_slot", "指定便枠に固定"), ("flexible_slot", "自由巡回便に配置")
    else:  # support
        ctx = "ユーザー契約：年間保守サポートプランに加入しています。"
        cond = "年間保守契約中"
        act_pos, act_neg = ("free_repair", "無償修理を手配"), ("paid_repair", "有償見積を案内")

    choices = [
        {"id": act_pos[0], "text": act_pos[1]},
        {"id": act_neg[0], "text": act_neg[1]},
    ]
    if rng.random() < 0.5:
        choices.reverse()

    r1 = {
        "id": f"m6-op-{split}-{group_idx:04d}-c1",
        "group_id": f"m6-grp-{split}-{group_idx:04d}",
        "task_family": "negation",
        "domain": domain,
        "split": split,
        "context": ctx,
        "question": q_pos.format(cond=cond, act_pos=act_pos[1], act_neg=act_neg[1]),
        "choices": choices,
        "target": {"kind": "hard", "choice_id": act_pos[0]},
        "case_kind": "positive_condition",
    }
    r2 = {
        "id": f"m6-op-{split}-{group_idx:04d}-c2",
        "group_id": f"m6-grp-{split}-{group_idx:04d}",
        "task_family": "negation",
        "domain": domain,
        "split": split,
        "context": ctx,
        "question": q_neg.format(cond=cond, act_pos=act_pos[1], act_neg=act_neg[1]),
        "choices": choices,
        "target": {"kind": "hard", "choice_id": act_neg[0]},
        "case_kind": "negated_condition",
    }
    return [r1, r2]


def generate_goal_switching_pair(group_idx: int, split: str, domain: str, rng: random.Random) -> List[Dict[str, Any]]:
    # Option A excels at Metric X (e.g. Speed/Fast). Option B excels at Metric Y (e.g. Cost/Cheap).
    # Question 1: Maximize Metric X (Speed) -> Option A
    # Question 2: Maximize Metric Y (Cost) -> Option B
    if split == "train":
        q_goal1 = "【方針】：{goal_x}を最優先とし、{goal_y}は重視しません。この方針に従って最適な選択肢を一つ選んでください。"
        q_goal2 = "【方針】：{goal_y}を最優先とし、{goal_x}は重視しません。この方針に従って最適な選択肢を一つ選んでください。"
    elif split == "dev":
        q_goal1 = "最適化目標：{goal_x}の最大化（{goal_y}の悪化は許容）。この目標に合致する手段を選定してください。"
        q_goal2 = "最適化目標：{goal_y}の最大化（{goal_x}の悪化は許容）。この目標に合致する手段を選定してください。"
    else:  # fresh
        q_goal1 = "指針転換：評価軸をシフトし、{goal_y}を度外視してでも{goal_x}の極大化を達成する選択肢を決定してください。"
        q_goal2 = "指針転換：評価軸をシフトし、{goal_x}を度外視してでも{goal_y}の極大化を達成する選択肢を決定してください。"

    if domain == "inventory":
        ctx = "調達ルート比較：ルートAは翌日納品ですが輸送費が割高です。ルートBは納品まで7日かかりますが輸送費は最安値です。"
        goal_x, goal_y = "納期の早さ（短縮）", "調達コストの安さ（節約）"
        opt_a, opt_b = ("route_a", "ルートAを採用する"), ("route_b", "ルートBを採用する")
    elif domain == "server":
        ctx = "インスタンス設計：プランAは高性能GPU搭載で高速処理ですが月額費用が高いです。プランBは省電力CPU構成で処理速度は劣りますが極めて低コストです。"
        goal_x, goal_y = "処理速度・スループット", "インフラ維持費用の抑制"
        opt_a, opt_b = ("plan_a", "プランAを契約する"), ("plan_b", "プランBを契約する")
    elif domain == "game":
        ctx = "装備の選択：武器Aは攻撃力+50ですが防御力-20のペナルティ。防具Bは防御力+50ですが攻撃力-20のペナルティがあります。"
        goal_x, goal_y = "瞬間火力（攻撃力）", "生存能力（防御力）"
        opt_a, opt_b = ("equip_a", "武器Aを装備する"), ("equip_b", "防具Bを装備する")
    elif domain == "delivery":
        ctx = "配送手段の検討：航空便は即日配送が可能ですが特別運賃が必要です。船便は到着まで日数を要しますが最安運賃です。"
        goal_x, goal_y = "配送リードタイムの短縮", "運賃負担の最小化"
        opt_a, opt_b = ("air_freight", "航空便を手配する"), ("sea_freight", "船便を手配する")
    else:  # support
        ctx = "対応プラン：オプションAは専任担当が即時電話対応（高額）。オプションBはチャットボットとメールで数日以内対応（無料）です。"
        goal_x, goal_y = "対応スピードと手厚さ", "利用料金の安さ"
        opt_a, opt_b = ("option_a", "オプションAを申し込む"), ("option_b", "オプションBを申し込む")

    choices = [
        {"id": opt_a[0], "text": opt_a[1]},
        {"id": opt_b[0], "text": opt_b[1]},
    ]
    if rng.random() < 0.5:
        choices.reverse()

    r1 = {
        "id": f"m6-op-{split}-{group_idx:04d}-c1",
        "group_id": f"m6-grp-{split}-{group_idx:04d}",
        "task_family": "goal_switching",
        "domain": domain,
        "split": split,
        "context": ctx,
        "question": q_goal1.format(goal_x=goal_x, goal_y=goal_y),
        "choices": choices,
        "target": {"kind": "hard", "choice_id": opt_a[0]},
        "case_kind": "goal_x_priority",
    }
    r2 = {
        "id": f"m6-op-{split}-{group_idx:04d}-c2",
        "group_id": f"m6-grp-{split}-{group_idx:04d}",
        "task_family": "goal_switching",
        "domain": domain,
        "split": split,
        "context": ctx,
        "question": q_goal2.format(goal_x=goal_x, goal_y=goal_y),
        "choices": choices,
        "target": {"kind": "hard", "choice_id": opt_b[0]},
        "case_kind": "goal_y_priority",
    }
    return [r1, r2]


GENERATORS = {
    "and_logic": generate_and_logic_pair,
    "or_logic": generate_or_logic_pair,
    "ge_vs_gt": generate_ge_vs_gt_pair,
    "le_vs_lt": generate_le_vs_lt_pair,
    "override": generate_override_pair,
    "default_exception": generate_default_exception_pair,
    "first_match": generate_first_match_pair,
    "priority_ranking": generate_priority_ranking_pair,
    "negation": generate_negation_pair,
    "goal_switching": generate_goal_switching_pair,
}


def build_split(
    split: str,
    pairs_per_op: int,
    seed: int,
    start_group_idx: int = 1,
) -> Tuple[List[Dict[str, Any]], int]:
    rng = random.Random(seed)
    records = []
    grp_idx = start_group_idx

    for op in OPERATOR_FAMILIES:
        gen_fn = GENERATORS[op]
        for p_i in range(pairs_per_op):
            domain = DOMAINS[(grp_idx + p_i) % len(DOMAINS)]
            pair = gen_fn(grp_idx, split, domain, rng)
            records.extend(pair)
            grp_idx += 1

    return records, grp_idx
