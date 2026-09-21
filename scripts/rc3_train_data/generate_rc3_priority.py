"""RC3 Training Data Synthesis: Priority Exceptions and Rule Precedence.

Generates 300 contrastive groups (600 records) across 10 priority and override domains:
1. Standard Return Policy vs Defective Goods Exception (30 groups)
2. General Remote Work Policy vs Security Incident Mandatory Attendance (30 groups)
3. Standard Procurement Approval vs Disaster Relief Emergency Fast-Track (30 groups)
4. Normal Air Ticket Non-Refundable vs Medical Ground Emergency Waiver (30 groups)
5. Tenant Lease Renewal Notice vs Habitual Non-Payment Eviction Override (30 groups)
6. Standard Cargo Weight Allowance vs Perishable Cold-Chain Priority (30 groups)
7. Standard Software Change Freeze vs Critical Security Patch Immediate Deploy (30 groups)
8. Regular Overtime Application vs Life-Saving Emergency Response Exemption (30 groups)
9. Standard Building Permit Review vs Disaster Reconstruction Fast-Pass (30 groups)
10. Normal Loan Underwriting Criteria vs Public Natural Disaster Relief Financing (30 groups)

Zero joke distractors. All distractors are domain-appropriate choices.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Tuple


def make_choices(defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in defs]


def generate_rc3_priority(seed: int = 3003) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    records: List[Dict[str, Any]] = []

    priority_domains = [
        # Domain 1: Return Policy vs Defective Goods Exception
        ("EC通販商品の返品・交換規程",
         "返品特約：購入者都合による商品返品は原則として『商品到着後7日以内の未開封品に限り受付（返送料購入者負担）』とする。ただし、製品初期不良または誤配送の例外事由に該当する場合は『開封後・使用後であっても30日間全額返金または無償交換（店舗全額負担）』とする。",
         "申請事由：サイズが思ったより大きくイメージと合わなかったため未開封のまま到着後3日目に返品希望。",
         "申請事由：到着直後に通電したところ内部から異臭と発煙が生じる初期不良が確認された（到着後10日目）。",
         [
             ("accept_standard_return_customer_pays_shipping", "原則に基づき7日以内未開封品として受領し返送料は購入者負担とする"),
             ("process_defective_return_free_replacement_store_pays", "初期不良例外を適用し開封後であっても無償交換し返送料は店舗負担とする"),
             ("reject_return_application_outright", "いかなる理由であっても返品・交換申請を一切拒絶する"),
             ("issue_partial_shopping_points_refund", "商品代金の20%を社内ポイントで部分返金する")
         ],
         "accept_standard_return_customer_pays_shipping",
         "process_defective_return_free_replacement_store_pays"),

        # Domain 2: Remote Work Policy vs Security Incident Attendance
        ("在宅テレワーク勤務および緊急出社規程",
         "就業規則：全従業員は週3日までの『在宅リモート勤務を申請・実施可能』とする。ただし、管轄サーバーへの不正アクセス検知等の重要セキュリティインシデントが発生した場合は『全特例に優先して担当エンジニアのオフィス即時出社』を命じる。",
         "勤務状況：平常通りの開発スプリント運用中であり、セキュリティ障害や警報等は一切発生していない。",
         "勤務状況：未明に本番DBサーバーへの特権昇格攻撃が検知され、重大セキュリティ事故対応チームが招集された。",
         [
             ("permit_standard_remote_work_schedule", "平常時の原則就業規則に基づき在宅リモート勤務の実施を認可する"),
             ("mandate_immediate_office_attendance_incident", "重要セキュリティインシデント発生に伴い優先命令としてオフィス即時出社を命じる"),
             ("prohibit_any_form_of_work_and_suspend_employee", "就業を全面禁止し従業員を出勤停止処分とする"),
             ("instruct_employee_to_work_from_public_cafe", "情報保護を無視して近隣の公共カフェでの作業を指示する")
         ],
         "permit_standard_remote_work_schedule",
         "mandate_immediate_office_attendance_incident"),

        # Domain 3: Standard Procurement Approval vs Disaster Fast-Track
        ("資材購買決裁権限および特例緊急購買",
         "購買規程：1,000万円を超える大型設備資材の購入は原則『常務取締役会での事前決裁を必須』とする。ただし、震度6以上の自然災害等による生産ライン復旧に必要な資材は『工場長の専決処分により即日発注可能』とする。",
         "発注案件：次世代量産ライン向けの最新型CNC旋盤の新規導入（購入予算4,500万円、平常時計画）。",
         "発注案件：直下型地震により第2工場の主送水管が破断、緊急復旧用高圧バルブ資材の購入（見積1,800万円）。",
         [
             ("require_board_of_directors_approval", "購買原則に従い常務取締役会での正式事前決裁を要求する"),
             ("authorize_immediate_emergency_order_by_plant_manager", "震災復旧の特例に基づき工場長の専決処分による即日発注を承認する"),
             ("cancel_procurement_and_shut_down_plant_permanently", "購買計画を永久白紙化し工場全体を閉鎖する"),
             ("order_materials_without_specifying_supplier", "取引先を指定せずに匿名で資材購入契約を締結する")
         ],
         "require_board_of_directors_approval",
         "authorize_immediate_emergency_order_by_plant_manager"),

        # Domain 4: Normal Air Ticket Non-Refundable vs Medical Ground Emergency Waiver
        ("航空券払戻手数料および病気特例取消",
         "運送約款：早期割引航空券の自己都合取消は原則『出発前であっても払戻手数料100%（全額没収・返金不可）』とする。ただし、搭乗者本人または同行家族が医師の診断により旅行不能と証明された場合は『手数料全額免除で航空券代金を全額払戻』する。",
         "払戻申請：仕事の都合がつかなくなったため、出発3日前に自己都合によるキャンセルを希望（診断書なし）。",
         "払戻申請：搭乗前日に急な急性虫垂炎で緊急入院となり、医師による搭乗不能診断書原本が提出された。",
         [
             ("enforce_non_refundable_cancellation_fee", "約款原則を適用し払戻手数料100%として返金不可とする"),
             ("waive_cancellation_fee_fully_on_medical_grounds", "病気特例を適用し払戻手数料を全額免除して航空券代金を全額返金する"),
             ("charge_double_penalty_fee_for_cancellation", "キャンセル違約金として航空券代金の2倍の金額を追加請求する"),
             ("convert_airfare_into_hotel_gift_coupons", "航空券代金を他社のホテル宿泊利用券へ無断振替する")
         ],
         "enforce_non_refundable_cancellation_fee",
         "waive_cancellation_fee_fully_on_medical_grounds"),

        # Domain 5: Tenant Lease Renewal Notice vs Habitual Non-Payment Eviction Override
        ("賃貸借契約更新および信頼関係破壊による解除特則",
         "借家契約規程：借主が契約満了2か月前までに更新拒絶通知を行わない場合は原則『従前と同一条件で2年間の自動更新』とする。ただし、借主による賃料滞納が連続3か月以上におよび催告後も弁済がない場合は『更新拒絶および即時契約解除・退去要求』を発動する。",
         "入居状況：これまで賃料の遅延は一度もなく、契約満了月を迎えるにあたり更新手続きの時期となった。",
         "入居状況：通算4か月にわたり家賃が未納であり、内容証明郵便による弁済催告期限も徒過している。",
         [
             ("approve_automatic_lease_renewal_for_two_years", "原則規程に基づき同一条件での2年間の賃貸契約自動更新を受理する"),
             ("enforce_lease_termination_and_demand_eviction", "長期賃料滞納の特則に基づき契約更新を拒絶し即時退去を要求する"),
             ("seize_tenant_personal_belongings_by_force", "法的手続きを経ずに借主の家財道具を勝手に路上へ搬出処分する"),
             ("increase_monthly_rent_by_ten_times", "ペナルティとして翌月からの家賃を10倍に増額請求する")
         ],
         "approve_automatic_lease_renewal_for_two_years",
         "enforce_lease_termination_and_demand_eviction"),

        # Domain 6: Standard Cargo Weight Allowance vs Perishable Cold-Chain Priority
        ("国際航空貨物搭載優先順位",
         "航空貨物輸送基準：貨物便の搭載スペースは原則『予約受領順（先着順）での搭載割当』とする。ただし、冷凍定温輸送が必要な生鮮医薬品・移植用検体は『一般予約貨物に優先して最優先搭載枠を割り当て』る。",
         "貨物種別：平常通りの一般工業用機械部品（プラスチック成型品）、先週事前予約済み。",
         "貨物種別：緊急搬送が必要な新型コロナワクチン冷凍コンテナ（-70℃維持）、当日急遽搬入。",
         [
             ("allocate_cargo_space_by_standard_booking_order", "原則基準に従い通常予約順序に基づいて搭載スペースを割り当てる"),
             ("grant_top_priority_cargo_space_to_perishable_medical", "医薬品特例に基づき一般貨物に優先して最優先搭載枠を直ちに割り当てる"),
             ("dump_medical_cargo_in_open_air_tarmac", "冷凍医薬品コンテナを屋外の炎天下駐機場に放置する"),
             ("refuse_all_cargo_loading_and_ground_fleet", "全貨物の搭載を拒絶し航空機を地上留め置く")
         ],
         "allocate_cargo_space_by_standard_booking_order",
         "grant_top_priority_cargo_space_to_perishable_medical"),

        # Domain 7: Standard Software Change Freeze vs Critical Security Patch Deploy
        ("システム本番環境変更凍結期間の特例運用",
         "ITサービス管理基準：四半期末の決算処理期間中は原則『本番環境への一切の機能改修・パッチ適用を凍結（Change Freeze）』とする。ただし、CVSSスコア9.0以上の緊急脆弱性（ゼロデイ）に対する修正パッチは『セキュリティ担当役員の承認により凍結を解除し即時適用』する。",
         "改修案件：営業管理ダッシュボードのUIボタン配色変更およびグラフ描画改善パッチ（通常改修）。",
         "改修案件：認証ライブラリにおけるリモートコード実行（RCE）の緊急ゼロデイ脆弱性（CVSS 9.8）対応パッチ。",
         [
             ("freeze_deployment_until_fiscal_closing_ends", "決算期変更凍結ルールを遵守し本番環境へのパッチ適用を延期凍結する"),
             ("authorize_emergency_patch_deployment_security_exemption", "緊急脆弱性特則に基づき凍結を解除し本番環境へセキュリティパッチを即時適用する"),
             ("shut_down_all_corporate_servers_indefinitely", "パッチ適用を行わず全社サーバーを無期限に電源遮断する"),
             ("deploy_untested_source_code_directly_to_production", "検証を行わずに未テストのソースコードをそのまま本番公開する")
         ],
         "freeze_deployment_until_fiscal_closing_ends",
         "authorize_emergency_patch_deployment_security_exemption"),

        # Domain 8: Regular Overtime Application vs Life-Saving Emergency Exemption
        ("時間外労働事前申請および人命救助緊急作業特例",
         "労務規程：時間外労働は原則『所定終業時刻の1時間前までに上長へ残業理由を明記して事前申請』しなければならない。ただし、突発的な人命救助活動または大規模災害防除に従事した場合は『事前申請なしで事後報告による残業手当全額支給』を認める。",
         "残業状況：翌日の定例会議用パワーポイント資料の体裁修正のため終業後に残業を行いたい（平常業務）。",
         "残業状況：隣接ビルでの火災発生に伴い、避難誘導および初期消火救護活動に深夜まで従事した。",
         [
             ("mandate_prior_overtime_approval_before_work", "労務原則を適用し所定時刻前の事前残業申請および上長承認を必須とする"),
             ("approve_ex_post_overtime_pay_for_life_saving_emergency", "人命救助特例を適用し事前申請なしでの事後報告による時間外手当全額支給を承認する"),
             ("penalize_employee_for_staying_after_hours", "救助活動に従事した従業員に対して無断残業として減給処分を課す"),
             ("force_employee_to_delete_attendance_timestamps", "タイムカードの打刻履歴を強制的に改ざん消去させる")
         ],
         "mandate_prior_overtime_approval_before_work",
         "approve_ex_post_overtime_pay_for_life_saving_emergency"),

        # Domain 9: Standard Building Permit Review vs Disaster Reconstruction Fast-Pass
        ("建築確認申請の標準審査期間および被災復旧特例",
         "建築行政規程：特定行政庁による新築建築確認申請の審査は原則『申請受理から35日以内の標準期間で交付判定』を行う。ただし、激甚災害指定を受けた地域の倒壊住家再建申請については『最優先特別審査ラインを適用し7日以内に即時交付判定』を行う。",
         "申請物件：東京都郊外の住宅街における木造2階建て個人住宅の新築計画（平常時申請）。",
         "申請物件：先月の大型台風で全壊判定を受けた被災者が、激甚指定特別区域内に生活再建のため自宅を再建する申請。",
         [
             ("process_building_permit_within_standard_35_days", "標準審査規程に従い受理後35日以内の期間で通常審査を実施する"),
             ("fast_track_building_permit_within_7_days_disaster_relief", "被災復旧特則を適用し特別審査ラインにより7日以内での迅速交付判定を行う"),
             ("deny_building_permit_indefinitely_without_reason", "理由を開示せずに建築確認申請を無期限に放置却下する"),
             ("waive_all_structural_safety_calculations", "耐震構造計算書などの必須書類の提出を一切不要として免除する")
         ],
         "process_building_permit_within_standard_35_days",
         "fast_track_building_permit_within_7_days_disaster_relief"),

        # Domain 10: Normal Loan Underwriting vs Disaster Relief Financing
        ("事業資金融資審査および自然災害緊急復興融資特則",
         "金融審査基準：運転資金融資の実行は原則『直近2期連続黒字かつ自己資本比率20%以上を必須条件』とする。ただし、公的激甚災害被災証明書を所持する事業者の再建資金については『財務要件を全面適用除外とし無利子緊急融資を実行』する。",
         "借入申請：通常運転資金の拡大希望、直近決算は2期連続黒字、自己資本比率32%（基準適合）。",
         "借入申請：大水害により工場が浸水全壊、直近は赤字だが自治体発行の被災証明書原本を添付して再建資金を希望。",
         [
             ("approve_business_loan_under_standard_credit_criteria", "通常審査基準適合を確認し標準金利での運転資金融資を実行する"),
             ("disburse_zero_interest_emergency_disaster_relief_loan", "被災復興特則を適用し財務要件を免除して無利子緊急融資を実行する"),
             ("confiscate_borrower_collateral_without_default", "返済期日前にもかかわらず担保不動産を強制差し押さえする"),
             ("demand_cash_bribe_for_loan_approval", "融資審査を通過させる見返りとして担当者への現金を要求する")
         ],
         "approve_business_loan_under_standard_credit_criteria",
         "disburse_zero_interest_emergency_disaster_relief_loan"),
    ]

    for idx, (title, rule, s1, s2, c_defs, t1, t2) in enumerate(priority_domains):
        for rep in range(30):
            gid = f"rc3_trn_prio_{idx*30 + rep + 1:03d}"
            choices = make_choices(c_defs)
            q = f"優先規程判断：{title}に基づき適切な処置を選択してください。"
            records.append({
                "id": f"{gid}_s1", "group_id": gid, "family": "priority_exception", "subdomain": f"domain_{idx+1}",
                "context": f"【{title}】{rule}\n案件審査：{s1}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2", "group_id": gid, "family": "priority_exception", "subdomain": f"domain_{idx+1}",
                "context": f"【{title}】{rule}\n案件審査：{s2}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    return records
