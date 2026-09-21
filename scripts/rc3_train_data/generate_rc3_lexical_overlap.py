"""RC3 Training Data Synthesis: Lexical Overlap Hard-Negative Contrastive Sets.

Directly targets the root cause identified in Milestone 27 (Factorial Exp C, -36.7pt collapse).
Distractors deliberately share high-salience keywords and entities with the context premise.
Forces the cross-encoder to attend to actual operational state and logic rather than
surface keyword matching.

Generates 300 contrastive groups (600 records) across 10 domains:
1. Patent Infringement Claims & Clearance (30 groups = 60 records)
2. Emergency Reactor / Boiler Overheat Alarms (30 groups = 60 records)
3. Contract Termination & Breach Notices (30 groups = 60 records)
4. Cyber Attack, Ransomware & Intrusion Detection (30 groups = 60 records)
5. Food Contamination & Product Recalls (30 groups = 60 records)
6. Anti-Money Laundering & Fraud Transactions (30 groups = 60 records)
7. Electrical Grid Surge & Breaker Trips (30 groups = 60 records)
8. Industrial Chemical Spills & Gas Leaks (30 groups = 60 records)
9. Clinical Trial Adverse Reaction Escalations (30 groups = 60 records)
10. Structural Scaffold Hazard & Collapse Alarms (30 groups = 60 records)

Zero joke distractors. Full lexical-overlap hard negatives.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Tuple


def make_choices(defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in defs]


def generate_rc3_lexical_overlap(seed: int = 3002) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    records: List[Dict[str, Any]] = []

    domains = [
        # Domain 1: Patent Infringement Claims & Clearance
        ("特許権侵害警告への対応方針",
         "知財管理規程：競合他社からの特許権侵害警告状に対し、弁理士による非侵害鑑定書が得られている場合は『特許権侵害の主張を正式に否認し通常販売を継続』する。侵害の蓋然性が高い場合は『対象製品の出荷停止と設計変更』に着手する。",
         "鑑定結果：独立した特許法律事務所より、相手方特許権の全請求項について非侵害鑑定書（充足性なし）が発行された。",
         "鑑定結果：侵害調査の結果、相手方特許権の独立項第1項および第3項を文言充足している可能性が極めて高いと判定された。",
         [
             ("deny_patent_infringement_and_continue_sales", "特許権侵害の主張を正式に否認し対象製品の通常販売を継続する"),
             ("halt_patent_infringement_sales_and_redesign", "特許権侵害の恐れがあるため対象製品の出荷を停止し設計変更に着手する"),
             ("negotiate_patent_infringement_cross_license", "特許権侵害の主張を受け入れ相手方とクロスライセンス契約を締結する"),
             ("petition_patent_infringement_invalidation_trial", "相手方特許権の特許庁に対する無効審判を先行請求する")
         ],
         "deny_patent_infringement_and_continue_sales",
         "halt_patent_infringement_sales_and_redesign"),

        # Domain 2: Emergency Reactor / Boiler Overheat Alarms
        ("原子炉炉心緊急冷却作動判定",
         "非常用炉心冷却設備運用規程：炉心非常用冷却系の作動信号が発報した際、複数センサーで圧力容器水位低下が裏付けられた場合は『非常用炉心冷却系（ECCS）の高圧注入弁を全開作動』させる。計器誤動作と確認された場合は『非常用炉心冷却系の誤発報を解除し通常給水を維持』する。",
         "監視盤状況：独立した3系統の水位計がいずれも正常水位を示しており、センサー単体の断線による計器誤動作と判明。",
         "監視盤状況：独立した3系統の水位計がすべて設定閾値を下回り、炉心水位の急速低下が裏付けられた。",
         [
             ("clear_eccs_false_alarm_and_maintain_feed", "非常用炉心冷却系の誤発報警報を解除し通常給水運転を維持する"),
             ("open_eccs_high_pressure_injection_valves", "非常用炉心冷却系（ECCS）の高圧注入弁を直ちに全開作動させる"),
             ("manual_trip_eccs_auxiliary_diesel_generator", "非常用炉心冷却系の非常用ディーゼル発電機を手動停止させる"),
             ("vent_reactor_pressure_vessel_containment", "非常用炉心冷却系を作動させず格納容器ベント弁のみを開放する")
         ],
         "clear_eccs_false_alarm_and_maintain_feed",
         "open_eccs_high_pressure_injection_valves"),

        # Domain 3: Contract Termination & Breach Notices
        ("売買基本契約解除通知の受領対応",
         "契約法務規程：取引先から債務不履行を理由とする契約解除通知を受領した際、当方に履行遅滞の事実がないことが立証された場合は『契約解除通知の効力を否認し履行受領を催告』する。当方に重大な不履行が存在する場合は『契約解除を受諾し損害賠償協議』を開始する。",
         "精査結果：当方の製品引き渡しは指定期日までに完了しており、受領印付き納品書により履行遅滞のないことが完全に立証された。",
         "精査結果：社内出荷管理の不備により、契約上の最終納期から1か月以上経過しても納品が未了のまま放置されていた。",
         [
             ("deny_contract_termination_and_demand_acceptance", "契約解除通知の法的主張を否認し相手方に目的物の履行受領を催告する"),
             ("accept_contract_termination_and_discuss_damages", "契約解除の効力を受諾し相手方との損害賠償協議の手続きを開始する"),
             ("suspend_contract_termination_for_arbitration", "契約解除通知の効力を争わず民間仲裁センターへ調停を申し立てる"),
             ("file_contract_termination_injunction_in_court", "契約解除通知の取り消しを求めて裁判所へ仮処分命令を申し立てる")
         ],
         "deny_contract_termination_and_demand_acceptance",
         "accept_contract_termination_and_discuss_damages"),

        # Domain 4: Cyber Attack, Ransomware & Intrusion Detection
        ("ランサムウェア感染検知インシデント初動",
         "情報セキュリティ危機管理基準：端末においてランサムウェアによるファイル暗号化挙動が検知された場合、実害活動が確認された端末は『社内LANおよびWi-Fiから即時物理切断・隔離』する。EDRの振る舞い検知の誤検知（False Positive）と立証された場合は『隔離措置を解除しEDR監視例外に登録』する。",
         "フォレンジック解析：社内独自開発スクリプトのハッシュ生成処理をEDRが誤検知したものであり、実害暗号化は皆無と証明された。",
         "フォレンジック解析：共有サーバー内の主要ドキュメントが拡張子.lockedへ急速に書き換えられている実害が確認された。",
         [
             ("release_quarantine_and_whitelist_script", "ランサムウェア隔離措置を解除し開発スクリプトを監視例外に登録する"),
             ("disconnect_and_isolate_infected_devices", "ランサムウェア感染拡大防止のため対象端末をネットワークから即時切断隔離する"),
             ("pay_ransomware_extortion_cryptocurrency", "ランサムウェア攻撃者の要求に従い身代金暗号資産の支払い手配を行う"),
             ("format_ransomware_server_without_backup", "ランサムウェア暗号化サーバーをバックアップ確認なしで即座に初期化する")
         ],
         "release_quarantine_and_whitelist_script",
         "disconnect_and_isolate_infected_devices"),

        # Domain 5: Food Contamination & Product Recalls
        ("食品アレルゲン混入疑惑と自主回収判断",
         "食品安全危機管理基準：出荷済み製品への特定原材料（そば）混入の疑いが生じた際、留保検体の精密検査で混入が否定された場合は『製品自主回収を行わず通常流通を継続』する。微量でも混入が確認された場合は『対象ロットの全量自主回収（リコール）を公表』する。",
         "検査結果：最新の高感度PCRおよびELISA検査において、同一製造バッチ全検体からそばタンパクは一切検出されなかった（陰性）。",
         "検査結果：同一バッチの複数検体から、規定値を超えるそばアレルゲンタンパクが明確に検出された（陽性）。",
         [
             ("continue_normal_distribution_without_recall", "混入なしを確認し製品自主回収を行わず通常流通をそのまま継続する"),
             ("announce_mandatory_product_recall_publicly", "アレルゲン混入確認に伴い対象ロットの全量自主回収（リコール）を公表する"),
             ("destroy_food_inventory_in_factory_secretly", "自主回収を公表せず自社倉庫内の在庫食品のみを秘密裏に焼却処分する"),
             ("relabel_food_packaging_with_warning_sticker", "店頭の食品パッケージに上からアレルゲン注意喚起シールを貼付して販売する")
         ],
         "continue_normal_distribution_without_recall",
         "announce_mandatory_product_recall_publicly"),

        # Domain 6: Anti-Money Laundering & Fraud Transactions
        ("マネーロンダリング疑わしい取引の届出判定",
         "AMLコンプライアンス規程：口座開設者の送金取引において、資金源の正当な裏付け証明書が提出された場合は『疑わしい取引の制限を解除し出金送金を承認』する。資金源が不透明かつ架空取引の疑いが強い場合は『出金を即時凍結し金融庁へ疑わしい取引届出』を提出する。",
         "確認書類：不動産売却契約書および納税証明書が提出され、数千万円の送金原資の正当性が完全に立証された。",
         "確認書類：取引実態のないダミー会社宛ての分散送金であり、提出書類は偽造と判明し資金源は不透明の極みである。",
         [
             ("approve_remittance_and_clear_suspicion", "資金源の正当性を確認し疑わしい取引の制限を解除して出金送金を承認する"),
             ("freeze_account_and_file_suspicious_transaction_report", "口座出金を即時凍結し監督官庁へ疑わしい取引の届出書を正式提出する"),
             ("return_illicit_funds_to_originator_silently", "疑わしい取引の届出を行わずに送金資金を無断で依頼人へ組戻し返金する"),
             ("charge_anti_money_laundering_investigation_fee", "疑わしい取引の調査費用として口座預金から特別手数料を引き落とす")
         ],
         "approve_remittance_and_clear_suspicion",
         "freeze_account_and_file_suspicious_transaction_report"),

        # Domain 7: Electrical Grid Surge & Breaker Trips
        ("高圧受電遮断器トリップ復旧指令",
         "電力保安管理基準：主受電遮断器が地絡過電流（SOG）によりトリップした際、構内高圧ケーブルの絶縁抵抗測定値が基準値以上の良品と確認された場合は『遮断器を投入し受電復旧』を実行する。地絡絶縁破壊が確認された場合は『遮断器投入を厳禁とし不良ケーブルを切り離し』修繕する。",
         "測定結果：構内全高圧電路の絶縁抵抗測定値は100MΩ以上であり、外部雷サージによる誤作動と判明（電路健全）。",
         "測定結果：受電キュービクル間の高圧引き込みケーブルの絶縁抵抗が0.01MΩ（完全地絡破壊状態）を示した。",
         [
             ("close_circuit_breaker_and_restore_power", "電路健全性を確認し主受電遮断器を再投入して受電復旧を実行する"),
             ("prohibit_breaker_closure_and_isolate_faulty_cable", "地絡事故電路への再送電を厳禁とし主受電遮断器を開放維持したまま不良系統を切り離す"),
             ("bypass_ground_fault_relay_protection", "主受電遮断器の地絡保護継電器を短絡バイパスして無理やり強制受電する"),
             ("replace_high_voltage_transformer_immediately", "絶縁測定を行わずに主受電変圧器本体を直ちに新品へ交換する")
         ],
         "close_circuit_breaker_and_restore_power",
         "prohibit_breaker_closure_and_isolate_faulty_cable"),

        # Domain 8: Industrial Chemical Spills & Gas Leaks
        ("危険物配管有害ガス漏洩警報の対応",
         "化学プラント保安規程：配管エリアの塩素ガス検知器が警報を発報した際、赤外線カメラによる目視点検で漏洩がなく検知器素子の故障と判明した場合は『緊急排気スクラバーの強制起動を抑止し通常換気を維持』する。実ガス漏洩が視認された場合は『緊急遮断弁を閉止しスクラバーを全開稼働』させる。",
         "現場調査：ポータブル検知器および赤外光学カメラにおいて塩素ガスは一切検知されず、固定センサーの素子劣化誤報と確定。",
         "現場調査：バルブフランジ部から白煙状の塩素ガスが連続噴出しているのが赤外光学カメラで明確に確認された。",
         [
             ("inhibit_emergency_scrubber_and_maintain_ventilation", "ガス漏洩なしを確認し緊急スクラバーの強制起動を抑止して通常換気を維持する"),
             ("close_emergency_shutoff_valve_and_run_scrubber", "配管緊急遮断弁を直ちに遠隔閉止し排気中和スクラバーを全開稼働させる"),
             ("spray_water_directly_onto_leaking_chlorine_valve", "防護具未着用で漏洩箇所に直接放水してガスを洗い流そうとする"),
             ("increase_chemical_reactor_feed_rate", "ガス漏洩警報を無視して化学反応器の原料供給流量を引き上げる")
         ],
         "inhibit_emergency_scrubber_and_maintain_ventilation",
         "close_emergency_shutoff_valve_and_run_scrubber"),

        # Domain 9: Clinical Trial Adverse Reaction Escalations
        ("治験薬重篤な副作用（SAE）発現時の治験中止判定",
         "GCP治験管理基準：治験薬投与後に重篤な有害事象（SAE）が発生した際、治験審査委員会（IRB）により治験薬との因果関係が完全否定された場合は『治験計画を変更せずプロトコル通り治験を継続』する。治験薬に起因する予期せぬ重篤な副作用と判定された場合は『当該治験の新規投与を即時中断』する。",
         "審議判定：有害事象は被験者の持病である既存心疾患の急性増悪であり、治験薬との因果関係は明確に否定された。",
         "審議判定：治験薬の肝毒性に起因する急性肝不全である可能性が極めて高く、因果関係が強く疑われると結論付けられた。",
         [
             ("continue_clinical_trial_per_protocol", "治験薬との因果関係なしを確認しプロトコル通り治験を継続する"),
             ("suspend_new_patient_enrollment_and_dosing", "治験薬に起因する重大リスクのため新規被験者への投与を即時中断する"),
             ("increase_investigational_drug_dosage_for_patient", "副作用を抑えるために治験薬の投与量を倍増させる"),
             ("conceal_serious_adverse_event_from_regulators", "重篤な有害事象の発生記録を破棄し医薬品医療機器総合機構へ報告しない")
         ],
         "continue_clinical_trial_per_protocol",
         "suspend_new_patient_enrollment_and_dosing"),

        # Domain 10: Structural Scaffold Hazard & Collapse Alarms
        ("建設現場大型足場強風安全管理",
         "労働安全衛生管理基準：建設現場の外部足場において、台風接近に伴い瞬間風速30m/s以上の暴風が予測される場合は『足場メッシュシートを全面結束開放し作業を完全中止』する。風速10m/s未満の穏やかな気象条件の場合は『通常防音シート展張状態を維持し作業を続行』する。",
         "気象観測：現在の現場風速は4.2m/sであり、終日穏やかな高気圧圏内で突風の恐れもない。",
         "気象観測：台風の中心付近が現場直撃コースにあり、最大瞬間風速38m/sの暴風警報が発令された。",
         [
             ("maintain_scaffold_soundproof_sheets_and_work", "気象条件良好を確認し足場シート展張状態を維持したまま通常作業を続行する"),
             ("bundle_scaffold_sheets_and_halt_all_work", "倒壊防止のため足場メッシュシートを速やかに全面結束開放し全高所作業を中止する"),
             ("erect_additional_heavy_advertising_tarps_on_scaffold", "強風が吹き荒れる中で足場に巨大な広告宣伝用防護シートを増設する"),
             ("remove_all_wall_tie_anchors_from_scaffold", "足場と躯体をつなぐ壁つなぎアンカーをすべて取り外して身軽にする")
         ],
         "maintain_scaffold_soundproof_sheets_and_work",
         "bundle_scaffold_sheets_and_halt_all_work"),
    ]

    for idx, (title, rule, s1, s2, c_defs, t1, t2) in enumerate(domains):
        for rep in range(30):
            gid = f"rc3_trn_lex_{idx*30 + rep + 1:03d}"
            choices = make_choices(c_defs)
            q = f"判断決定：{title}の事象に基づき、適切な対応を選択してください。"
            records.append({
                "id": f"{gid}_s1", "group_id": gid, "family": "lexical_overlap_resistance", "subdomain": f"domain_{idx+1}",
                "context": f"【{title}】{rule}\n現在の調査状況：{s1}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2", "group_id": gid, "family": "lexical_overlap_resistance", "subdomain": f"domain_{idx+1}",
                "context": f"【{title}】{rule}\n現在の調査状況：{s2}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    return records
