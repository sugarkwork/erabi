"""RC3 Training Data Synthesis: General Choice Tasks across Diverse Domains.

Generates 300 contrastive groups (600 records) across 10 multi-industry domains:
1. Pharmaceutical Cold-Chain Transport Temperature Excursion (30 groups)
2. Renewable Energy Solar/Wind Grid Curtailment (30 groups)
3. Customs Import Tariff Classification & Documentation (30 groups)
4. Commercial Banking Letter of Credit (L/C) Discrepancy (30 groups)
5. Aviation Aircraft Maintenance A-Check vs Grounding (30 groups)
6. Semiconductor Cleanroom Fab Yield Contamination (30 groups)
7. Corporate Whistleblower Hotline Protection & Escrow (30 groups)
8. Municipal Drinking Water Fluoride/Chlorine Excursion (30 groups)
9. Port Container Terminal Crane Congestion Routing (30 groups)
10. Hospital ICU Ventilator Resource Allocation Protocol (30 groups)

Zero joke distractors. Domain-accurate actions.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Tuple


def make_choices(defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in defs]


def generate_rc3_general(seed: int = 3006) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    records: List[Dict[str, Any]] = []

    domains = [
        # Domain 1: Pharmaceutical Cold-Chain Temperature Excursion
        ("生物学的製剤コールドチェーン温度逸脱管理",
         "GDP医薬品流通過程基準：輸送中データロガーにおいて2℃〜8℃の規定範囲が維持されているロットは『荷受承認し保冷倉庫へ格納』する。規定外の25℃環境に2時間以上曝露されたロットは『即時受入保留とし品質保証部門による有効性判定』に回付する。",
         "ロガー解析：輸送全行程を通じて2.8℃〜5.5℃で安定推移し、温度逸脱記録はゼロ。",
         "ロガー解析：保冷車故障により外気温31℃の直射日光下で3時間放置され、庫内温度が27℃まで急上昇。",
         [
             ("accept_delivery_and_store_in_cold_warehouse", "規定温度維持を確認し製品荷受を承認して保冷倉庫へ格納する"),
             ("quarantine_and_escalate_to_qa_assessment", "重大な温度逸脱のため受入を保留し品質保証部門の有効性判定へ回付する"),
             ("dispose_pharmaceuticals_into_municipal_trash", "品質判定を行わずに医薬品を一般ごみ集積所へ廃棄する"),
             ("heat_biological_products_to_boiling_point", "滅菌のため生物学的製剤を沸騰加熱する")
         ],
         "accept_delivery_and_store_in_cold_warehouse",
         "quarantine_and_escalate_to_qa_assessment"),

        # Domain 2: Renewable Energy Grid Curtailment
        ("再生可能エネルギー発電所出力制御指令",
         "電力需給調整規程：送配電網の受入余力が十分であり系統周波数が安定している時間帯は『太陽光発電の全量売電売電送電を継続』する。晴天休日等で軽負荷となり需給バランス崩壊が予測される時間帯は『出力制御指令に従いPCS出力を抑制遮断』する。",
         "需給見通し：平日ピーク時間帯、電力需要が旺盛であり送配電網の空き容量は100%余裕あり。",
         "需給見通し：春の大型連休の正午、全国的な電力需要低下と快晴が重なり周波数が許容上限へ急上昇。",
         [
             ("maintain_full_renewable_power_generation", "送配電網の余力を確認し太陽光発電の全量送電を継続する"),
             ("curtail_pcs_inverter_power_output", "需給バランス崩壊防止のため出力制御指令に従いPCS出力を抑制遮断する"),
             ("connect_unauthorized_high_load_heaters", "無許可で電力網に巨大な抵抗ヒーターを接続して消費する"),
             ("sever_substation_transmission_cables_physically", "変電所の送電高圧線を物理的に切断する")
         ],
         "maintain_full_renewable_power_generation",
         "curtail_pcs_inverter_power_output"),

        # Domain 3: Customs Import Tariff Classification
        ("輸入通関申告区分および事前教示適合",
         "税関通関審査基準：輸入申告品が税関長による事前教示回答書と完全一致し書類完備している場合は『輸入許可書を即時交付』する。品目分類（HSコード）に齟齬があり申告税率の脱漏が疑われる場合は『現品検査（開披検査）を実施し追徴課税審査』へ回付する。",
         "通関書類：事前教示回答書（関税分類9018.90）原本添付、インボイス記載仕様と完全一致。",
         "通関書類：インボイス上の申告HSコードが無税枠に指定されているが、実物は課税対象の精密電子機器と判明。",
         [
             ("issue_customs_import_permit_immediately", "事前教示との一致を確認し輸入許可書を即時交付する"),
             ("order_physical_inspection_and_tariff_review", "品目分類齟齬のため現品開披検査を実施し追徴課税審査へ回付する"),
             ("smuggle_cargo_through_fishing_harbor", "正規税関を迂回し漁港経由で貨物を密輸入する"),
             ("confiscate_all_freight_and_auction_privately", "正規手続きを経ずに貨物を没収し私的競売にかける")
         ],
         "issue_customs_import_permit_immediately",
         "order_physical_inspection_and_tariff_review"),

        # Domain 4: Commercial Banking Letter of Credit (L/C)
        ("信用状（L/C）取引ディスクレパンシー（不一致）処理",
         "国際貿易決済信用状統一規則（UCP600）：呈示された船積書類が信用状条件と厳格に一致（Strict Compliance）している場合は『為替手形を即時引受・代金決済』を実行する。船荷証券の日付が積載期限を超過している等の瑕疵がある場合は『不一致通知を発行し支払を保留』する。",
         "書類審査：商業送り状・B/L・保険証券の記載内容および日付が信用状条件と完全一致。",
         "書類審査：信用状記載の最終積載期日（8月15日）に対し、提出されたB/L日付が8月22日（船積遅延）。",
         [
             ("accept_clean_documents_and_settle_payment", "厳格一致を確認し為替手形を引き受けて貿易代金決済を実行する"),
             ("issue_discrepancy_notice_and_hold_payment", "船積遅延の不一致を発見したためディスクレ通知を発行し支払を保留する"),
             ("forge_shipping_dates_on_original_bills", "原本船荷証券の日付をボールペンで書き換えて偽造する"),
             ("transfer_funds_to_personal_account_of_officer", "決済資金を担当者の個人口座へ不正送金する")
         ],
         "accept_clean_documents_and_settle_payment",
         "issue_discrepancy_notice_and_hold_payment"),

        # Domain 5: Aviation Aircraft Maintenance A-Check
        ("航空機耐空性点検および飛行停止（AOG）判定",
         "航空整備安全基準：飛行前点検において最低機材仕様限界（MEL）の許容範囲内である場合は『航行可能（Ready for Flight）として出発承認』する。主翼動翼油圧系統からの作動油漏洩など安全飛行に直結する不具合が発見された場合は『飛行停止（AOG）を宣言しハンガー格納整備』を命じる。",
         "整備日誌：客室読書灯の不点灯が1件あるが、MEL基準上は運航許容項目であり主要操縦系統は全数正常。",
         "整備日誌：第1エンジンパイロン内部の高圧油圧配管フランジから、毎分30滴の作動油漏れが確認された。",
         [
             ("authorize_aircraft_departure_within_mel", "MEL許容範囲内を確認し航行可能として出発便の運航を承認する"),
             ("ground_aircraft_and_order_hangar_repair", "油圧配管漏洩に伴い直ちに飛行停止（AOG）を宣言し格納庫整備を命じる"),
             ("wipe_away_hydraulic_oil_with_tissue_and_fly", "作動油漏れを拭き取っただけで修理せずにそのまま離陸させる"),
             ("scrap_aircraft_on_runway_with_sledgehammer", "滑走路上で航空機をハンマーで叩き壊す")
         ],
         "authorize_aircraft_departure_within_mel",
         "ground_aircraft_and_order_hangar_repair"),

        # Domain 6: Semiconductor Cleanroom Fab Yield Contamination
        ("半導体前工程ウェハー異物混入ロット隔離",
         "クリーンルーム品質管理基準：インライン欠陥検査においてパーティクル数が管理限界線（UCL=15個/ウェハー）以下であるバッチは『次工程（薄膜エッチング）へ投入』する。UCLを超過する微小金属異物が検知されたバッチは『直ちにロット隔離し欠陥分析SEM解析』へ投入する。",
         "検査ウェハーデータ：平均パーティクル数4.2個/ウェハー（良好な管理状態）。",
         "検査ウェハーデータ：配線露光後のウェハー表面に粒径0.1μmのCu異物が85個/ウェハー検出された。",
         [
             ("advance_wafer_lot_to_next_etching_process", "パーティクル管理基準適合を確認しウェハーロットを次工程へ投入する"),
             ("quarantine_wafer_lot_for_sem_defect_analysis", "管理限界超過のためロットを緊急隔離しSEM欠陥解析へ投入する"),
             ("wash_wafers_with_unfiltered_tap_water", "超純水ではなく工場の水道水でウェハーを丸洗いする"),
             ("hide_inspection_alarm_from_yield_reports", "歩留まり報告書から欠陥警報データを改ざん隠蔽する")
         ],
         "advance_wafer_lot_to_next_etching_process",
         "quarantine_wafer_lot_for_sem_defect_analysis"),

        # Domain 7: Corporate Whistleblower Hotline Protection
        ("内部通報制度通報者保護および調査開始",
         "コンプライアンス公益通報規程：社内通報窓口へ証拠資料を伴う不正事実の申告があった際、通報者の氏名秘匿および不利益処分禁止を徹底し『独立調査委員会による本調査を開始』する。誹謗中傷を目的とする客観的根拠の全くない怪文書については『調査を行わず受理不受理記録のみ保管』する。",
         "通報内容：役員による交際費不正還流を示す会計伝票のPDFおよび銀行振込履歴が添付された通報。",
         "通報内容：特定同僚の容姿や性格に関する主観的な悪口のみが匿名で記載され、業務上の違法事実の記述は皆無。",
         [
             ("protect_whistleblower_and_launch_independent_investigation", "通報者保護措置を講じたうえで独立調査委員会による本調査を開始する"),
             ("archive_groundless_complaint_without_investigation", "客観的根拠のない誹謗文書として調査を開始せず記録保管のみとする"),
             ("expose_whistleblower_identity_on_company_bulletin", "通報者の氏名を社内掲示板に貼り出して公開する"),
             ("fire_whistleblower_immediately_for_reporting", "通報を行ったことに対する報復として通報者を即日懲戒解雇する")
         ],
         "protect_whistleblower_and_launch_independent_investigation",
         "archive_groundless_complaint_without_investigation"),

        # Domain 8: Municipal Drinking Water Fluoride/Chlorine Excursion
        ("水道事業浄水場残留塩素濃度管理",
         "水道水質管理基準：給水栓における遊離残留塩素濃度が0.1mg/L以上1.0mg/L以下に保たれている場合は『安全な上水として送水を継続』する。配水池での測定値が0.05mg/L未満に低下し消毒不十分の恐れがある場合は『次亜塩素酸注入ポンプの注入比率を即時増量』する。",
         "水質自動監視データ：末端給水栓の残留塩素濃度0.35mg/L（法定基準適合）。",
         "水質自動監視データ：第2配水池の残留塩素濃度が0.03mg/Lまで低下（基準下限割れ）。",
         [
             ("maintain_water_distribution_within_standard", "法定基準適合を確認し安全な上水として配水送水を継続する"),
             ("increase_sodium_hypochlorite_chlorination_dosing", "消毒不備防止のため次亜塩素酸注入ポンプの薬注比率を即時増量する"),
             ("shut_off_all_drinking_water_to_entire_city_permanently", "残留塩素のわずかな変動を理由に全市域への上水供給を永久遮断する"),
             ("dump_toxic_pesticides_into_water_reservoir", "水質改善と称して水源池に劇薬農薬を投入する")
         ],
         "maintain_water_distribution_within_standard",
         "increase_sodium_hypochlorite_chlorination_dosing"),

        # Domain 9: Port Container Terminal Crane Congestion Routing
        ("国際コンテナターミナル本船荷役バース指定",
         "港湾運用規程：入港コンテナ船の喫水が岸壁水深を満たしガントリークレーンの空きがある場合は『指定メインバースへの即時接岸を許可』する。バースが満杯で待機列が滞留している場合は『港外指定錨地での錨泊待機を指示』する。",
         "港湾管制通信：第3バース接岸中の先行船が荷役完了し離岸、クレーン2基の待機準備完了。",
         "港湾管制通信：台風避難の船舶が集中し、全バースが満隻で荷役完了見込みまで18時間以上待機。",
         [
             ("grant_docking_clearance_to_designated_berth", "空きバースを確認しガントリークレーン荷役のため接岸を許可する"),
             ("instruct_vessel_to_anchor_outside_harbor_and_wait", "バース満杯のため港外指定錨地での錨泊待機を指示する"),
             ("ram_vessel_into_wharf_at_full_speed", "全速力で岸壁コンクリートに船首を突入させて衝突させる"),
             ("jettison_all_shipping_containers_into_bay", "着岸スペースを空けるため積載コンテナを港湾海域へ投棄する")
         ],
         "grant_docking_clearance_to_designated_berth",
         "instruct_vessel_to_anchor_outside_harbor_and_wait"),

        # Domain 10: Hospital ICU Ventilator Resource Allocation Protocol
        ("災害医療ICU人工呼吸器重症度プロトコル",
         "救急集中治療基準：急性呼吸窮迫症候群（ARDS）によりP/F比が150未満に急悪化した重症患者には『ICUにおける侵襲的陽圧人工呼吸器を即時装着』する。自発呼吸が回復しSpO2が室内気で96%以上維持できている患者は『人工呼吸器の離脱（抜管）および一般病棟転床』を実施する。",
         "生体モニター：室内気SpO2が97%で安定、自発呼吸回数14回/分、P/F比350（全身状態良好）。",
         "生体モニター：高流量酸素マスク投与下でもSpO2が84%へ低下、P/F比110、重度の陥没呼吸を呈している。",
         [
             ("wean_off_ventilator_and_transfer_to_general_ward", "自発呼吸回復を確認し人工呼吸器を離脱抜管して一般病棟へ転床する"),
             ("initiate_invasive_mechanical_ventilation_in_icu", "呼吸不全急速進行のためICUにおける侵襲的人工呼吸器の装着を開始する"),
             ("administer_lethal_overdose_of_anesthetic_drugs", "致死量の麻酔薬を急速静注する"),
             ("discharge_patient_immediately_to_walk_home", "重症呼吸不全患者を治療せずそのまま徒歩で帰宅させる")
         ],
         "wean_off_ventilator_and_transfer_to_general_ward",
         "initiate_invasive_mechanical_ventilation_in_icu"),
    ]

    for idx, (title, rule, s1, s2, c_defs, t1, t2) in enumerate(domains):
        for rep in range(30):
            gid = f"rc3_trn_gen_{idx*30 + rep + 1:03d}"
            choices = make_choices(c_defs)
            q = f"専門判断：{title}の事象に基づき、適切な対応を選択してください。"
            records.append({
                "id": f"{gid}_s1", "group_id": gid, "family": "general_choice", "subdomain": f"domain_{idx+1}",
                "context": f"【{title}】{rule}\n現場確認情報：{s1}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2", "group_id": gid, "family": "general_choice", "subdomain": f"domain_{idx+1}",
                "context": f"【{title}】{rule}\n現場確認情報：{s2}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    return records
