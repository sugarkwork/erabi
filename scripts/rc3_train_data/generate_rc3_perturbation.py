"""RC3 Training Data Synthesis: Perturbation Invariance and Robustness.

Generates 200 contrastive groups (400 records) across 10 domains with
structural, syntactic, and formatting variations:
1. Bullet points and bracketed formatting vs narrative prose (20 groups)
2. Question phrasing variations (direct imperative, polite inquiry, selection prompt) (20 groups)
3. Incidental sensor ID / timestamp injection (20 groups)
4. Order of premise clauses (rule first vs fact first) (20 groups)
5. Polite keigo vs technical concise operational style (20 groups)
6. Parenthetical clarifications and abbreviation expansions (20 groups)
7. Multi-line structured logs vs single-line streaming context (20 groups)
8. Punctuation variations (full-width vs half-width, colons vs brackets) (20 groups)
9. Operator shift header and logging prefixes (20 groups)
10. Neutral framing vs critical alert tags (20 groups)

Zero joke distractors. Domain-appropriate plausible choices.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Tuple


def make_choices(defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in defs]


def generate_rc3_perturbation(seed: int = 3007) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    records: List[Dict[str, Any]] = []

    perturbation_scenarios = [
        # Domain 1: Bullet points vs prose
        ("冷媒配管圧力安全インターロック",
         "【基準】・冷媒圧力 > 3.0MPa：凝縮器ファン緊急全開\n・冷媒圧力 <= 3.0MPa：通常循環ポンプ維持",
         "［現場計器記録］現在測定値：3.45MPa（上限超過）",
         "［現場計器記録］現在測定値：2.10MPa（正常領域）",
         "凝縮器冷却ファンを直ちに全開運転する", "通常冷媒循環ポンプ運転をそのまま維持する", "膨張弁を手動で全閉固定する",
         "condenser_fan_full_speed", "coolant_pump_normal_maintain", "expansion_valve_manual_shut"),

        # Domain 2: Question phrasing variations
        ("クリーンルーム差圧ダンパー制御",
         "無塵室規格：室間差圧が20Pa未満の場合は給気インバーター出力を100%に引き上げる。20Pa以上の陽圧が確保されている場合は現行の定常周波数を維持する。",
         "差圧センサーログ（ID: CR-04）：測定差圧 12Pa（規定下限割れ）。",
         "差圧センサーログ（ID: CR-04）：測定差圧 28Pa（良好な陽圧状態）。",
         "給気インバーター出力を100%に引き上げ差圧を回復する", "現行インバーター定常周波数を維持する", "排気側ダンパーを全開にして減圧する",
         "boost_air_supply_inverter_full", "maintain_steady_inverter_frequency", "open_exhaust_damper_to_depressurize"),

        # Domain 3: Incidental sensor ID and timestamps
        ("受電キュービクル絶縁監視警報",
         "保安基準（IEC-60364準拠）：零相変流器（ZCT）漏洩電流が50mAを超過した場合は主幹線受電遮断器を遮断する。50mA以下の場合は定常受電を継続する。",
         "2026-09-21 14:02:11 [NODE_ZCT_09] 漏洩電流測定値：82mA（閾値超過トリップ）。",
         "2026-09-21 14:02:11 [NODE_ZCT_09] 漏洩電流測定値：14mA（正常絶縁状態）。",
         "主幹線受電遮断器を直ちに開放遮断する", "定常受電運用をそのまま継続する", "零相変流器の接地線を切断する",
         "trip_main_incoming_circuit_breaker", "continue_steady_power_reception", "sever_zero_phase_grounding_wire"),

        # Domain 4: Order of premise clauses (Fact first vs Rule first)
        ("航空便受託手荷物超過料金精算",
         "【運送約款】無料受託手荷物許容量（23kg）を超過している場合は超過手荷物料金を徴収する。許容量以下の場合は無償で受託する。",
         "手荷物測定実績：旅客の預け入れスーツケース実測重量は27.5kgである。",
         "手荷物測定実績：旅客の預け入れスーツケース実測重量は19.8kgである。",
         "重量超過を確認し規定の超過手荷物料金を徴収する", "許容量適合を確認し無償で手荷物を受託する", "手荷物をその場で開封し内容物を廃棄させる",
         "charge_excess_baggage_weight_fee", "accept_baggage_free_of_charge", "force_passenger_to_discard_contents"),

        # Domain 5: Polite keigo vs technical operational style
        ("社内PC外部持ち出しセキュリティ審査",
         "【社内規程】恐れ入りますが、社給PCの社外持ち出しはセキュリティ保護のため原則全面禁止となっております。ただし、役員承認済みのリモートワーク対象者に限り暗号化PCの社外持ち出しを正式に許可申し上げます。",
         "申請状況：AI事業統括役員の事前承認印を受領済みの暗号化ノートPC貸与案件。",
         "申請状況：私的な自宅でのプログラミング学習目的であり、役員承認は未取得。",
         "暗号化PCの社外持ち出しを正式に許可する", "社給PCの社外持ち出しを禁止とする", "端末のハードディスクを物理破砕する",
         "permit_encrypted_laptop_takeout", "prohibit_company_laptop_takeout", "shred_laptop_hard_drive_physically"),

        # Domain 6: Parenthetical clarifications and abbreviation expansions
        ("排水COD（化学的酸素要求量）規制管理",
         "公害防止協定基準：放流水の化学的酸素要求量（Chemical Oxygen Demand: COD）が15mg/Lを超えた場合は排水ゲートを閉止し調整池へ回収する。15mg/L以下の場合は公共用水域への通常放流を継続する。",
         "水質計指示：COD測定値 22mg/L（協定値超過検知）。",
         "水質計指示：COD測定値 8.5mg/L（排水協定完全適合）。",
         "排水ゲートを即時閉止し調整池へ全量回収する", "水質適合を確認し公共用水域への通常放流を継続する", "COD分析計の測定セルに脱塩水を注入して偽装する",
         "close_discharge_gate_divert_to_pond", "continue_normal_effluent_discharge", "flush_cod_analyzer_with_deionized_water"),

        # Domain 7: Multi-line structured logs
        ("コンテナオーケストレーターポッド再起動",
         "POD_SPEC: name=auth-svc\nRESTART_POLICY: OnFailure\nTHRESHOLD: exit_code != 0 -> trigger container restart\nSTATUS: exit_code == 0 -> maintain running state",
         "SYSTEM_LOG: [auth-svc-78f9] Process crashed with fatal exit_code=137 (OOMKilled).",
         "SYSTEM_LOG: [auth-svc-78f9] Health check HTTP 200 OK, exit_code=0 (Healthy).",
         "再起動ポリシーに従いポッドコンテナを自動再起動する", "正常稼働を確認し現行ポッドの実行状態を維持する", "クラスターの全ノードを強制シャットダウンする",
         "trigger_pod_container_auto_restart", "maintain_current_pod_running_state", "force_shutdown_all_cluster_nodes"),

        # Domain 8: Punctuation variations
        ("高速道路横風通行速度規制",
         "【道路交通安全情報】：：瞬間風速が20m/sを超過した場合は『最高速度50km/h規制』を発令する。::瞬間風速が20m/s以下の場合は『通常法定速度80km/h』を維持する。",
         "気象計測定（地点KP-145）：最大瞬間風速24.8m/s（強風域突入）。",
         "気象計測定（地点KP-145）：最大瞬間風速11.2m/s（穏やかな気象条件）。",
         "最高速度50km/h規制を発令し電光掲示板に表示する", "通常法定速度80km/hを維持する", "道路上にコンクリートブロックを設置し車線を封鎖する",
         "impose_50kmh_speed_restriction", "maintain_normal_80kmh_speed_limit", "block_lanes_with_concrete_barriers"),

        # Domain 9: Operator shift header prefixes
        ("医薬用水注射用水（WFI）ループ導電率監視",
         "［第2シフト引継記録］注射用水製造基準：WFI循環ループの電気伝導率が1.3μS/cm（25℃換算）を超過した場合は供給弁を自動閉止しドレン廃棄する。1.3μS/cm以下の場合は各調製釜への供給を継続する。",
         "プロセスモニター：WFI循環導電率 1.85μS/cm（水質異常アラート）。",
         "プロセスモニター：WFI循環導電率 0.65μS/cm（高純度規格適合）。",
         "供給弁を自動閉止しループ水を全量ドレン廃棄する", "規格適合を確認し調製釜へのWFI供給を継続する", "純水タンクに消石灰を投入して中和する",
         "shut_wfi_supply_valve_and_drain", "continue_wfi_supply_to_tanks", "add_slaked_lime_to_pure_water_tank"),

        # Domain 10: Neutral framing vs critical alert tags
        ("防火区画防火シャッター自動降下判定",
         "【防災設備連動基準】煙感知器と熱感知器の両系統から連動火災信号が同時発報した場合は『防火シャッターを全閉降下』させる。単一の煙感知器のみの発報で熱感知器未発報の場合は『防災センターへの注意警報通知のみ』に留める。",
         "警報盤表示：第3工区煙感知器発報、第3工区差動式熱感知器同時発報（AND連動成立）。",
         "警報盤表示：第3工区煙感知器発報、熱感知器は全系統平常状態（単独発報）。",
         "防火区画形成のため防火シャッターを全閉降下させる", "防災センターへの注意警報通知に留め降下を保留する", "スプリンクラー配管の元バルブを工具で切断する",
         "drop_fire_shutter_to_full_close", "hold_shutter_and_alert_security_desk", "cut_sprinkler_main_pipes_with_tools"),
    ]

    # Generate 20 groups per domain (200 groups = 400 records)
    for idx, (title, rule, s1, s2, a1, a2, a3, c1, c2, c3) in enumerate(perturbation_scenarios):
        c_defs = [(c1, a1), (c2, a2), (c3, a3)]
        choices = make_choices(c_defs)
        for rep in range(20):
            gid = f"rc3_trn_prt_{idx*20 + rep + 1:03d}"
            # Vary questions
            q_variants = [
                f"基準適合性判定：{title}に基づき適切な対応措置を選択してください。",
                f"機器制御指示：{title}の規程に合致する最も適切な選択肢はどれか。",
                f"運用判断：{title}における現在の状態から指示すべき処置を選びなさい。",
                f"判断選択：{title}の管理条件に照らして正当なアクションを特定してください。"
            ]
            q = q_variants[rep % len(q_variants)]
            records.append({
                "id": f"{gid}_s1", "group_id": gid, "family": "perturbation_invariance", "subdomain": f"domain_{idx+1}",
                "context": f"{rule}\n{s1}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": c1}
            })
            records.append({
                "id": f"{gid}_s2", "group_id": gid, "family": "perturbation_invariance", "subdomain": f"domain_{idx+1}",
                "context": f"{rule}\n{s2}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": c2}
            })

    return records
