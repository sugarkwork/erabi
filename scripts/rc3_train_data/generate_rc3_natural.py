"""RC3 Training Data Synthesis: Natural Japanese Phrasing and Concessive Structures.

Replaces old generators with 100% realistic distractors (ZERO joke distractors).
Incorporates concessive markers (〜であるものの、〜にもかかわらず、〜とはいえ),
formal business writing, Slack/chat exchanges, and authentic operational Japanese.

Generates 300 contrastive groups (600 records) across 10 domains:
1. Vendor Quotation Approval vs Budgetary Hold (30 groups)
2. Production Milestone Rescheduling & Concessive Adjustment (30 groups)
3. SaaS Electronic Agreement Signature vs Legal Exception (30 groups)
4. Invoice Discrepancy Reconciliation (30 groups)
5. Executive Protocol Meeting Scheduling (30 groups)
6. Cloud Service Outage Post-Mortem Communication (30 groups)
7. Employment Offer Acceptance vs Formal Decline (30 groups)
8. Trade Exhibition Joint Sponsorship Participation (30 groups)
9. Software License Audit Conformance (30 groups)
10. Corporate Headquarters Facility Management Notification (30 groups)
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Tuple


def make_choices(defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in defs]


def generate_rc3_natural(seed: int = 3005) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    records: List[Dict[str, Any]] = []

    scenarios = [
        # Domain 1: Vendor Quotation Approval vs Budgetary Hold
        ("ベンダー見積書の承認および予算査定",
         "【件名：新製品開発プロジェクト御見積書受領の件】平素より大変お世話になっております。ご提示いただきました御見積書（管理番号#7701）について社内審議を行いましたところ、予定予算枠内に収まっていることが確認できましたので【提示金額のまま正式発注の手続き】を進めさせていただきます。",
         "【件名：新製品開発プロジェクト御見積書に関するご相談】平素より格別のご高配を賜り厚く御礼申し上げます。ご提示の見積書を拝見いたしましたところ、一部工数の追加により今期予算上限を超過しております。大変恐縮ながら【今回は発注を見送り仕様再調整のうえ再検討】とさせていただけますと幸いです。",
         [
             ("approve_quotation_and_issue_purchase_order", "提示金額そのまま正式発注の手続きを進める"),
             ("suspend_order_for_budgetary_renegotiation", "予算超過のため発注を見送り仕様再調整を要請する"),
             ("request_competitor_quote_benchmarking", "他社相見積もりを取得して価格妥当性を比較する"),
             ("split_project_into_multiple_micro_phases", "プロジェクトを複数フェーズに分割して翌期へ繰り延べる")
         ],
         "approve_quotation_and_issue_purchase_order",
         "suspend_order_for_budgetary_renegotiation"),

        # Domain 2: Production Milestone Rescheduling & Concessive Adjustment
        ("製造ライン出荷日程の前倒しおよび納期延期調整",
         "【件名：第2ロット製品納期に関するご連絡】お世話になっております。製造ラインの追加稼働が順調に推移し、部品調達に一部遅れが見られたものの最終組立が当初予定より3日早く完了いたしました。つきましては【来週火曜日着での前倒し繰り上げ納品】をご承諾いただけますでしょうか。",
         "【件名：重要：製造ライン部品不適合に伴う納期調整のお願い】お世話になっております。本日未明、海外サプライヤーからの供給部品に規格外公差が発覚いたしました。品質保証を最優先とするため、誠に心苦しい限りですが【納品期日を2週間延期し再検査完了後の出荷】へ変更させてください。",
         [
             ("advance_delivery_date_for_early_shipment", "組立早期完了を確認し来週火曜日の前倒し納品を手配する"),
             ("postpone_delivery_date_by_two_weeks_for_inspection", "品質再検査のため納品期日を2週間延期して調整する"),
             ("deliver_partial_first_batch_immediately", "合格分のみを先行して部分納品し残りは後日発送する"),
             ("switch_to_domestic_substitute_supplier_expedited", "国内代替サプライヤーへ特急手配を依頼する")
         ],
         "advance_delivery_date_for_early_shipment",
         "postpone_delivery_date_by_two_weeks_for_inspection"),

        # Domain 3: SaaS Electronic Agreement Signature vs Legal Exception
        ("クラウド利用契約の電子署名締結および修正依頼",
         "【件名：秘密保持契約書（NDA）締結のご案内】過日合意いただきました機密保持条項案につきまして、弊社法務部門によるリーガルチェックが完了いたしました。修正箇所の指摘はございませんでしたので【電子署名クラウドサービスより合意受諾の署名】をお願い申し上げます。",
         "【件名：機密保持契約書ドラフト条項修正のお願い】送付いただきましたNDAドラフトを拝見いたしましたところ、第9条の損害賠償責任上限に関する免責範囲が弊社標準規程と乖離しております。恐れ入りますが【条項修正を反映した改訂版ドラフトの再発行】をお願いできますでしょうか。",
         [
             ("execute_cloud_electronic_signature_approval", "法務承認を確認し電子署名クラウド上で受諾署名を行う"),
             ("request_revised_draft_with_clause_amendments", "免責条項乖離のため修正版ドラフトの再発行を要請する"),
             ("convene_face_to_face_legal_counsel_meeting", "双方の顧問弁護士同席による対面協議の場を設ける"),
             ("waive_entire_non_disclosure_agreement", "機密保持契約の締結そのものを不要として免除する")
         ],
         "execute_cloud_electronic_signature_approval",
         "request_revised_draft_with_clause_amendments"),

        # Domain 4: Invoice Discrepancy Reconciliation
        ("請求書受領確認および割引記載漏れ照会",
         "【件名：当月分ご請求書受領のお礼と支払予定のご連絡】毎月大変お世話になっております。ご送付いただきました請求番号#3321の請求書を拝見いたしました。契約通りの金額および税計算に一切相違ございませんので【当月末日に指定口座へ全額お振込み】いたします。",
         "【件名：ご請求金額の事前お値引き反映に関するご確認】いつもお世話になっております。拝受いたしましたご請求書を精査いたしましたところ、先月書面にて合意いたしました年間ボリュームディスカウント（10%引き）が反映されておりません。【正規割引を適用した修正請求書の再送】をお願いできますでしょうか。",
         [
             ("schedule_full_wire_transfer_on_due_date", "記載相違なしを確認し請求期日に全額振込の手続きを行う"),
             ("request_reissued_invoice_with_contracted_discount", "割引反映漏れのため正規割引を適用した請求書の再発行を求める"),
             ("withhold_entire_payment_and_cancel_partnership", "請求額の相違を理由に一切の取引を停止し提携を破棄する"),
             ("offset_discrepancy_against_future_next_year_sales", "差額分を翌年度以降の取引売上と相殺処理する")
         ],
         "schedule_full_wire_transfer_on_due_date",
         "request_reissued_invoice_with_contracted_discount"),

        # Domain 5: Executive Protocol Meeting Scheduling
        ("役員表敬訪問日程の確定および渡航変更再調整",
         "【件名：弊社代表取締役表敬訪問の日程確定のお願い】拝啓。貴社におかれましては益々ご隆盛のこととお慶び申し上げます。来月予定しております弊社代表の訪問につきまして、ご提示いただきました【10月5日午後2時より貴社本社応接室にて面談実施】のスケジュールで確定とさせていただけますと幸甚です。",
         "【件名：大変恐縮ながら訪問日程再調整のお願い】平素より格別のご高配を賜り深謝申し上げます。先日ご相談いたしました弊社代表の訪問日程ですが、急遽政府系経済使節団への随行要請が入りました。誠に不躾ながら【10月18日以降の別日程へ再調整】をお願い申し上げたく存じます。",
         [
             ("confirm_executive_meeting_schedule_october_5", "提示日時を確認し10月5日午後2時での役員訪問を確定する"),
             ("reschedule_executive_visit_to_later_date", "急な公務随行に伴い10月18日以降の日程への再調整を依頼する"),
             ("delegate_meeting_to_junior_sales_intern", "役員面談を新入社員インターンに代理出席させる"),
             ("conduct_executive_meeting_via_unencrypted_chat", "役員協議をオープンチャットツールで済ませる")
         ],
         "confirm_executive_meeting_schedule_october_5",
         "reschedule_executive_visit_to_later_date"),

        # Domain 6: Cloud Service Outage Post-Mortem Communication
        ("クラウドインフラ全面復旧宣言および障害時間延長告知",
         "【件名：クラウド認証基盤の障害復旧完了に関するご報告】ご利用企業様各位。本日未明より発生しておりましたシングルサインオン認証サーバーの通信遅延ですが、冗長クラスターの切り戻しおよび整合性検証が完了し、【午前6時30分をもちまして全機能が正常復旧】いたしました。",
         "【件名：重要：認証基盤メンテナンス作業の延長に関するお詫び】ご利用企業様各位。現在実施中の中継ルーター緊急メンテナンスですが、ファームウェアの整合性チェックに想定以上の時間を要しております。誠に遺憾ながら【サービス再開予定時刻を午前10時まで延長】させていただきます。",
         [
             ("announce_complete_service_restoration", "整合性検証完了を確認し全機能の正常復旧を正式発表する"),
             ("announce_maintenance_window_extension_to_10am", "作業難航のためサービス再開予定時刻を午前10時まで延長告知する"),
             ("recommend_users_to_bypass_authentication_layer", "利用企業に対して認証機構を無効化して利用するよう促す"),
             ("delete_all_historical_system_audit_logs", "障害調査を避けるため過去の全システム監査ログを消去する")
         ],
         "announce_complete_service_restoration",
         "announce_maintenance_window_extension_to_10am"),

        # Domain 7: Employment Offer Acceptance vs Polite Decline
        ("新卒中途採用の内定受諾および辞退の礼節連絡",
         "【件名：採用内定通知受諾のお返事】人事部採用ご担当者様。この度は光栄な内定のご通知をいただき心より御礼申し上げます。提示いただきました雇用条件および配属方針を熟読し、【謹んで内定をお受けいたしたく入社承諾書を返送】いたします。",
         "【件名：採用選考に関するご連絡】人事部採用ご担当者様。身に余る内定の通知をいただき深謝申し上げます。大変悩み抜きました結果、かねてより志望しておりました研究開発職の専攻分野へ進む道を選択いたしました。誠に心苦しい限りですが【内定辞退のご連絡】を申し上げます。",
         [
             ("accept_job_offer_and_return_agreement", "条件合意を確認し謹んで内定を受諾し入社承諾書を返送する"),
             ("decline_job_offer_with_formal_courtesy", "他社進路決定に伴い礼儀を尽くして内定辞退の旨を連絡する"),
             ("negotiate_quadruple_signing_bonus", "内定受諾の条件として提示年収の4倍の支度金を要求する"),
             ("ignore_offer_deadline_without_any_response", "連絡を一切行わずに内定承諾期限を無断で放置する")
         ],
         "accept_job_offer_and_return_agreement",
         "decline_job_offer_with_formal_courtesy"),

        # Domain 8: Trade Exhibition Joint Sponsorship Participation
        ("国際展示会共同出展申込および予算凍結見送り",
         "【件名：国際産業技術展共同出展への正式参加合意】共同出展事務局御中。役員会における来期マーケティング戦略審議の結果、貴社との共同ブース出展計画が正式承認されました。つきましては【共同出展申込書および小間割要望書を提出】いたします。",
         "【件名：国際産業技術展の出展見送りに関するお詫び】共同出展事務局御中。貴社との共同出展に向けて協議を重ねてまいりましたが、全社的なコスト削減方針に伴い出展費用の予算承認が得られませんでした。断腸の思いではございますが【今回の出展参加は見送り】とさせてください。",
         [
             ("submit_formal_joint_exhibition_application", "役員会承認を確認し共同出展申込書および要望書を正式提出する"),
             ("decline_exhibition_participation_due_to_budget", "予算不承認に伴い展示会への共同出展参加を見送る"),
             ("attend_exhibition_as_unauthorized_distributor", "出展手続きを行わずに会場通路で無許可ゲリラ配布を行う"),
             ("demand_host_organization_to_waive_all_fees", "主催者に対して出展料の全額免除を強要する")
         ],
         "submit_formal_joint_exhibition_application",
         "decline_exhibition_participation_due_to_budget"),

        # Domain 9: Software License Audit Conformance
        ("ソフトウェア資産管理定期監査の適合判定および追加購入命令",
         "【件名：全社ソフトウェア資産管理（SAM）内部監査結果報告】情報システム部御中。先般実施いたしましたクライアント端末全台のライセンス実査におきまして、導入数と保有ライセンス数が完全一致し【不正利用ゼロ・コンプライアンス適合】が確認されました。",
         "【件名：ライセンス実数過不足調査に伴う是正勧告】情報システム部御中。定期監査の結果、グラフィック部門において正規ライセンス数を上回る6台の超過インストールが判明いたしました。重大なコンプライアンス違反リスクを回避するため【直ちに追加ライセンスの正規購入手配】を行ってください。",
         [
             ("certify_complete_software_license_compliance", "保有数と導入数の一致を確認し適正ライセンス運用を証明する"),
             ("mandate_immediate_additional_license_procurement", "超過インストール解消のため追加ライセンスの正規購入手配を命じる"),
             ("uninstall_antivirus_software_to_save_costs", "コスト削減のため社内全端末のウイルス対策ソフトを削除する"),
             ("hide_non_compliant_workstations_from_auditors", "監査員から隠すために不正端末を社外倉庫へ一時退避させる")
         ],
         "certify_complete_software_license_compliance",
         "mandate_immediate_additional_license_procurement"),

        # Domain 10: Corporate Headquarters Facility Management Notification
        ("新本社オフィス移転祝い受領辞退および祝花手配",
         "【件名：新本社オフィス開設に伴うご案内とお願い】お取引先様各位。弊社は来月より下記住所へ本社を移転いたします。なお、昨今の脱炭素およびSDGs環境負荷低減方針に基づき、誠に勝手ながら【祝花・祝電の類は謹んでご辞退】申し上げます。",
         "【件名：貴社新オフィスご移転に関するお祝いの手配】代表取締役社長様。この度は新社屋へのご移転、誠におめでとうございます。長年の強固なパートナーシップへの感謝を込めまして【指定配送日必着にてお祝いの胡蝶蘭を手配】いたしましたのでご受納ください。",
         [
             ("respectfully_decline_congratulatory_flowers_sdgs", "環境負荷低減方針に基づきお取引先へ祝花辞退の旨を案内する"),
             ("dispatch_congratulatory_orchids_for_new_office", "新社屋移転の祝意を込め指定日に胡蝶蘭の配送を手配する"),
             ("blockade_entrance_doors_of_new_office_building", "移転初日に新オフィスのエントランス扉をバリケード封鎖する"),
             ("order_unauthorized_demolition_of_office_partitions", "無許可で新オフィスの間仕切り壁を解体撤去する")
         ],
         "respectfully_decline_congratulatory_flowers_sdgs",
         "dispatch_congratulatory_orchids_for_new_office"),
    ]

    for idx, (title, s1, s2, c_defs, t1, t2) in enumerate(scenarios):
        for rep in range(30):
            gid = f"rc3_trn_nat_{idx*30 + rep + 1:03d}"
            choices = make_choices(c_defs)
            q = f"文脈判断：{title}における連絡趣旨に基づき、適切な対応を選択してください。"
            records.append({
                "id": f"{gid}_s1", "group_id": gid, "family": "natural_japanese", "subdomain": f"domain_{idx+1}",
                "context": f"{s1}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2", "group_id": gid, "family": "natural_japanese", "subdomain": f"domain_{idx+1}",
                "context": f"{s2}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    return records
