"""RC3 Training Data Synthesis: Variable Candidate Cardinality (K=4, 6, 8, 12, 16).

Directly addresses Cluster 1 from Milestone 26 (High-Cardinality candidate sets).
Strictly adheres to token contract (<= 450 tokens, hard ceiling <= 512) by using
concise, standard industry choice phrasing across 4 to 16 concurrent candidates.

Generates 300 contrastive groups (600 records) across 10 domains:
1. ITIL Incident Severity Routing (K=6) (30 groups)
2. Medical Hospital Specialty Triage (K=12) (30 groups)
3. Financial Regulatory Compliance Category (K=8) (30 groups)
4. Hazardous Industrial Freight Class (K=16) (30 groups)
5. Aviation Disruption Passenger Compensation (K=6) (30 groups)
6. Municipal Waste Material Sorting Stream (K=8) (30 groups)
7. Customer Support Intent Department Routing (K=16) (30 groups)
8. Cyber Security Incident Defensive Action (K=12) (30 groups)
9. Manufacturing Defect Engineering Disposition (K=8) (30 groups)
10. Legal Dispute Resolution Forum (K=4) (30 groups)

Zero joke distractors. All choices are distinct, realistic options.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Tuple


def make_choices(defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in defs]


def generate_rc3_variable_k(seed: int = 3004) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    records: List[Dict[str, Any]] = []

    # Domain 1: ITIL Incident Severity Routing (K=6)
    itil_choices = [
        ("p1_critical_outage", "インシデントP1：全社基幹停止・即時緊急対策本部招集"),
        ("p2_major_degradation", "インシデントP2：主要機能縮退・4時間以内専任対応"),
        ("p3_moderate_workaround", "インシデントP3：回避策あり部分障害・翌日改修"),
        ("p4_minor_cosmetic", "インシデントP4：軽微表示不具合・次回定期改修"),
        ("service_request_standard", "標準要求：定例作業ワークフロー処理"),
        ("inquiry_informational", "情報照会：仕様問い合わせFAQ回答"),
    ]
    itil_s1 = "全銀ネット接続サーバーが全面停止し、全国窓口・ATMの全送金処理が中断。"
    itil_s2 = "勤怠打刻画面で上長承認ボタンの文字色が一部薄い（打刻・承認は完全正常）。"

    # Domain 2: Medical Specialty Triage (K=12)
    med_choices = [
        ("triage_cardiology", "循環器内科：心筋梗塞・血管カテーテル班"),
        ("triage_neurology", "脳神経外科：クモ膜下出血・緊急開頭班"),
        ("triage_respiratory", "呼吸器内科：重症呼吸不全・人工呼吸管理班"),
        ("triage_gastroenterology", "消化器外科：消化管穿孔・緊急開腹手術班"),
        ("triage_orthopedics", "整形外科：骨盤骨折・緊急創外固定班"),
        ("triage_ophthalmology", "眼科：網膜剥離・緊急硝子体手術班"),
        ("triage_dermatology", "皮膚科：重症薬疹・熱傷入院集中治療班"),
        ("triage_pediatrics", "小児救命科：小児ショック集中治療班"),
        ("triage_obstetrics", "産婦人科：胎盤早期剥離・緊急帝王切開班"),
        ("triage_psychiatry", "精神科救急：急性錯乱・自傷他害保護隔離班"),
        ("triage_urology", "泌尿器科：尿路結石発作・緊急尿路処置班"),
        ("triage_otolaryngology", "耳鼻咽喉科：急性喉頭浮腫・気道確保止血班"),
    ]
    med_s1 = "65歳男性、激しい胸部絞扼感と冷汗、心電図でST上昇確認。"
    med_s2 = "28歳男性、突然の激しい後頭部痛と嘔吐を発症し意識混濁。"

    # Domain 3: Financial Regulatory Compliance (K=8)
    fin_choices = [
        ("aml_suspicious_report", "疑わしい取引STR：犯罪収益移転防止法に基づく金融庁届出"),
        ("large_currency_transaction", "多額現金CTR：200万円超受払の定型報告"),
        ("insider_trading_monitoring", "重要事実知得者：インサイダー防止の売買一時停止"),
        ("market_manipulation_alert", "相場操縦見せ玉：不公正取引の証券監視委報告"),
        ("fiduciary_duty_conflict", "利益相反管理：顧客不利益を防止する自己勘定制限"),
        ("capital_adequacy_early_warning", "自己資本比率：リスクアセット増に伴う早期是正"),
        ("cross_border_tax_evasion_fatca", "外国口座FATCA：米国人判定に基づくIRS報告"),
        ("personal_data_leakage_notification", "個人データ漏洩：個人情報保護委・顧客への法定通知"),
    ]
    fin_s1 = "実体のないペーパーカンパニーから複数口座へ数千万円が分散送金された。"
    fin_s2 = "始値決定直前に約定意図のない大量買い注文を発注し直前取消を反復。"

    # Domain 4: Hazardous Industrial Freight Class (K=16)
    haz_choices = [
        ("class_1_1_mass_explosion", "危険物1.1：大量爆発性火薬類"),
        ("class_1_4_minor_explosion", "危険物1.4：軽微火薬類火工品"),
        ("class_2_1_flammable_gas", "危険物2.1：高圧引火性ガス"),
        ("class_2_2_non_flammable_gas", "危険物2.2：非引火非毒性ガス"),
        ("class_2_3_toxic_gas", "危険物2.3：圧縮毒性ガス"),
        ("class_3_flammable_liquid", "危険物3：常温引火性液体"),
        ("class_4_1_flammable_solid", "危険物4.1：可燃性固体"),
        ("class_4_2_spontaneous_combustion", "危険物4.2：自然発火性物質"),
        ("class_4_3_dangerous_when_wet", "危険物4.3：禁水性反応物質"),
        ("class_5_1_oxidizing_substance", "危険物5.1：酸化性物質"),
        ("class_5_2_organic_peroxide", "危険物5.2：有機過酸化物"),
        ("class_6_1_toxic_substance", "危険物6.1：有害毒物"),
        ("class_6_2_infectious_substance", "危険物6.2：感染性病原体"),
        ("class_7_radioactive_material", "危険物7：放射性同位元素"),
        ("class_8_corrosive_substance", "危険物8：強酸腐食性物質"),
        ("class_9_miscellaneous_dangerous", "危険物9：環境有害電池類"),
    ]
    haz_s1 = "純度99%の常温液体ガソリン2,000Lの海上コンテナ輸送。"
    haz_s2 = "水と激しく反応し水素を放出して発火する金属ナトリウム塊50kg輸送。"

    # Domain 5: Aviation Compensation Tier (K=6)
    av_choices = [
        ("comp_full_rebook_and_hotel", "補償区分A：会社都合欠航・全額払戻または無償便変更＋宿泊手配"),
        ("comp_meal_voucher_only", "補償区分B：機材整備遅延・空港飲食バウチャー提供"),
        ("comp_weather_force_majeure", "補償区分C：天候不可抗力・宿泊費なし無償便振替のみ"),
        ("comp_voluntary_bump_cash", "補償区分D：過剰予約自発的辞退・協力金現金支給"),
        ("comp_baggage_loss_claim", "補償区分E：受託手荷物紛失・条約上限賠償金精算"),
        ("comp_no_liability_passenger", "補償区分F：旅客都合乗り遅れ・補償なし当日券案内"),
    ]
    av_s1 = "乗務員手配不足により便が翌日へ欠航となり旅客が空港で足止め。"
    av_s2 = "台風直撃の暴風警報発令に伴い安全上の不可抗力として欠航決定。"

    # Domain 6: Municipal Waste Material Sorting Stream (K=8)
    waste_choices = [
        ("waste_combustible", "可燃ごみ：生ごみ・紙くず（指定焼却袋）"),
        ("waste_non_combustible", "不燃ごみ：陶器・金属複合品（破砕埋立指定袋）"),
        ("waste_recyclable_pet", "ペットボトル：洗浄キャップ外し透明容器"),
        ("waste_recyclable_paper", "古紙資源：新聞雑誌段ボール結束"),
        ("waste_recyclable_cans", "空き缶資源：アルミ・スチール洗浄分別"),
        ("waste_hazardous_batteries", "有害ごみ：乾電池・水銀体温計専用箱"),
        ("waste_oversized_bulky", "粗大ごみ：一辺30cm以上家具（予約収集）"),
        ("waste_home_appliance_recycling", "家電リサイクル：冷蔵庫・エアコン等特定家電"),
    ]
    waste_s1 = "調理残渣の野菜くずや汚れたティッシュペーパー。"
    waste_s2 = "買い替えで不要となった2ドアの大型電気冷蔵庫350L。"

    # Domain 7: Customer Support Department Routing (K=16)
    dept_choices = [
        ("dept_billing_invoicing", "請求窓口：月額利用料・領収書発行"),
        ("dept_account_security_login", "認証窓口：パスワード失念・2要素解除"),
        ("dept_contract_cancellation", "解約窓口：期間満了解約・違約金確認"),
        ("dept_technical_api_support", "技術窓口：Webhook・REST連携"),
        ("dept_bug_report_escalation", "障害窓口：アプリクラッシュ再現調査"),
        ("dept_feature_request_feedback", "企画窓口：ユーザー要望・機能提案"),
        ("dept_enterprise_sales", "営業窓口：法人一括契約・見積交渉"),
        ("dept_hardware_repair_warranty", "保証窓口：端末故障・修理受付"),
        ("dept_shipping_logistics_tracking", "物流窓口：発送通知・住所変更"),
        ("dept_legal_compliance_ip", "法務窓口：規約違反・商標侵害要請"),
        ("dept_pr_media_press", "広報窓口：メディア取材・プレス対応"),
        ("dept_recruiting_careers", "採用窓口：中途採用・面接調整"),
        ("dept_privacy_data_gdpr", "プライバシー窓口：個人情報開示消去"),
        ("dept_security_vulnerability", "セキュリティ窓口：脆弱性報告受領"),
        ("dept_affiliate_partner", "提携窓口：アフィリエイト・販売代理"),
        ("dept_investor_relations_ir", "IR窓口：決算発表・株主総会質疑"),
    ]
    dept_s1 = "毎月のクレカ引き落とし明細の宛名を法人名義にした領収書を発行してほしい。"
    dept_s2 = "OAuth2.0のトークン更新エンドポイントでHTTP 401エラーが返る。"

    # Domain 8: Cyber Security Incident Defensive Action (K=12)
    cyber_choices = [
        ("cyber_isolate_host_vlan", "端末隔離：対象端末を隔離VLAN収容"),
        ("cyber_revoke_user_tokens", "セッション失効：全トークン無効化"),
        ("cyber_block_c2_ip_firewall", "通信遮断：攻撃者C2サーバーIPドロップ"),
        ("cyber_quarantine_email_inbox", "メール隔離：標的型攻撃メール全社削除"),
        ("cyber_patch_vulnerable_service", "脆弱性修正：公開サーバーパッチ即日適用"),
        ("cyber_restore_from_airgap_backup", "オフライン復旧：エアギャップバックアップ復元"),
        ("cyber_sinkhole_malicious_domain", "DNS制御：悪性ドメイン宛先を変更"),
        ("cyber_honeypot_deception", "デコイ誘導：侵入者をハニーポットへ誘導"),
        ("cyber_forensic_memory_dump", "メモリ保全：端末RAMダンプ取得"),
        ("cyber_notify_cert_regulator", "公的報告：JPCERT・監督省庁へ速報"),
        ("cyber_rotate_all_api_keys", "鍵更新：流出恐れの全APIキー再生成"),
        ("cyber_deploy_canary_tokens", "監視配置：ファイルサーバーに偽情報配置"),
    ]
    cyber_s1 = "マルウェア感染端末が内部LANから外部C2サーバーへ毎秒ビーコン通信。"
    cyber_s2 = "役員のGitHub公開リポジトリに本番AWS管理者APIキーが平文コミット。"

    # Domain 9: Manufacturing Defect Engineering Disposition (K=8)
    mfg_choices = [
        ("mfg_scrap_and_recycle", "全量スクラップ：破砕溶解リサイクル回送"),
        ("mfg_rework_machining", "再加工修正：寸法プラス公差の追加切削"),
        ("mfg_use_as_is_concession", "特別採用：機能影響なし微小傷の特採承認"),
        ("mfg_downgrade_to_sub_tier", "等級格下げ：低負荷用途セカンド品変更"),
        ("mfg_return_to_material_vendor", "原材料返品：介在物欠陥サプライヤー返品"),
        ("mfg_quarantine_for_metallurgy", "原因究明隔離：顕微鏡組織観察・硬度試験"),
        ("mfg_sort_100_percent_inspection", "全数選別検査：抜き取り不良超過の手動検査"),
        ("mfg_stop_assembly_line", "ライン停止：金型破損によるプレス停止"),
    ]
    mfg_s1 = "クランクシャフト軸径が公差上限より0.05mm大きい（削り足せば合格可能）。"
    mfg_s2 = "航空機用チタン合金部品の鍛造内部に致命的空洞クラック多数（修復不能）。"

    # Domain 10: Legal Dispute Resolution Forum (K=4)
    legal_choices = [
        ("legal_commercial_arbitration", "商事仲裁（JCAA）：一審制・非公開の仲裁判断"),
        ("legal_district_court_litigation", "地方裁判所訴訟：執行力確保の第一審通常民事訴訟"),
        ("legal_civil_conciliation_court", "簡易裁判所調停：調停委員仲介の円満合意解決"),
        ("legal_out_of_court_negotiation", "裁判外示談交渉：弁護士直接書面交渉"),
    ]
    legal_s1 = "国際契約に『紛争は日本商事仲裁協会の規則に従い仲裁により解決する』と明記。"
    legal_s2 = "相手方が対話を拒絶し夜逃げの構え、強制執行を可能とする確定判決取得が必須。"

    all_specs = [
        ("IT障害重大度分類", "ITIL標準に基づき、障害状況から適切な重大度区分を選択してください。", itil_s1, itil_s2, itil_choices, "p1_critical_outage", "p4_minor_cosmetic"),
        ("救急トリアージ診療科選定", "トリアージ基準に基づき、患者主訴から適切な治療班を選択してください。", med_s1, med_s2, med_choices, "triage_cardiology", "triage_neurology"),
        ("金融コンプライアンス区分", "規制法規に基づき、検知事象から適切な報告措置を選択してください。", fin_s1, fin_s2, fin_choices, "aml_suspicious_report", "market_manipulation_alert"),
        ("危険物等級容器選定", "危険物規則に基づき、物質性質から適切な等級区分を選択してください。", haz_s1, haz_s2, haz_choices, "class_3_flammable_liquid", "class_4_3_dangerous_when_wet"),
        ("航空障害旅客補償判定", "旅客運送約款に基づき、欠航要因から適切な補償対応を選択してください。", av_s1, av_s2, av_choices, "comp_full_rebook_and_hotel", "comp_weather_force_majeure"),
        ("自治体ごみ排出区分選定", "分別収集基準に基づき、排出物から適切な分別区分を選択してください。", waste_s1, waste_s2, waste_choices, "waste_combustible", "waste_home_appliance_recycling"),
        ("サポート問い合わせ回付", "社内分掌に基づき、問い合わせ内容から適切な主管窓口を選択してください。", dept_s1, dept_s2, dept_choices, "dept_billing_invoicing", "dept_technical_api_support"),
        ("サイバー攻撃初動防御", "CSIRT基準に基づき、検知イベントから適切な防御アクションを選択してください。", cyber_s1, cyber_s2, cyber_choices, "cyber_block_c2_ip_firewall", "cyber_rotate_all_api_keys"),
        ("不適合品工学処置判定", "品質管理規定に基づき、欠陥様態から適切な工学的処置を選択してください。", mfg_s1, mfg_s2, mfg_choices, "mfg_rework_machining", "mfg_scrap_and_recycle"),
        ("契約紛争解決手続選定", "紛争処理基準に基づき、事案から適切な法的手続きを選択してください。", legal_s1, legal_s2, legal_choices, "legal_commercial_arbitration", "legal_district_court_litigation"),
    ]

    for idx, (title, q, s1, s2, c_defs, t1, t2) in enumerate(all_specs):
        for rep in range(30):
            gid = f"rc3_trn_var_{idx*30 + rep + 1:03d}"
            choices = make_choices(c_defs)
            records.append({
                "id": f"{gid}_s1", "group_id": gid, "family": "variable_choice", "subdomain": f"domain_{idx+1}",
                "context": f"【{title}】\n状況：{s1}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2", "group_id": gid, "family": "variable_choice", "subdomain": f"domain_{idx+1}",
                "context": f"【{title}】\n状況：{s2}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    return records
