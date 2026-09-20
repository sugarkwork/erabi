"""RC2.1 Training Data Synthesis: Stream B — Perturbation Variants (240 pairs = 480 records).

Covers 4 perturbation categories x 60 pairs:
1. candidate_permutation_and_id: 選択肢のシャッフル提示・非自明なID命名 (60 pairs)
2. filler_and_sentence_order: 無関係な雑談・背景情報の挿入と前提文頭/文末の倒置・クリーンな選択肢 (60 pairs)
3. register_and_syntax: 敬語丁寧体 vs 常体簡潔体の表現揺らぎ（正確な対照ラベル付け） (60 pairs)
4. parenthetical_caveats: 括弧書き（※ただし書き）による条件修飾 (60 pairs)

Total: 240 pairs (480 records). All contrastive pairs have distinct targets for s1/s2 and realistic choices.
"""

from typing import Any, Dict, List
import random


def make_choices(defs: List[tuple]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in defs]


def generate_perturbation_stream_b(seed: int = 3003) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    records = []

    # Category 1: Candidate Permutation & Varied IDs (60 pairs = 120 records)
    perm_scenarios = [
        (
            "受講コース選定",
            "TOEICスコアが700点以上なら「上級ビジネス英語」、700点未満なら「基礎文法英語」。受講生スコア：780点。",
            "TOEICスコアが700点以上なら「上級ビジネス英語」、700点未満なら「基礎文法英語」。受講生スコア：550点。",
            [("opt_basic_grammar", "基礎文法英語コースへ案内する"), ("opt_intermediate_communication", "中級日常会話コースへ案内する"), ("opt_advanced_business", "上級ビジネス英語コースへ案内する")],
            "opt_advanced_business", "opt_basic_grammar"
        ),
        (
            "駐車場優遇",
            "お買い上げ3,000円以上で「2時間無料券」、3,000円未満なら「通常時間料金」。レシート合計：4,200円。",
            "お買い上げ3,000円以上で「2時間無料券」、3,000円未満なら「通常時間料金」。レシート合計：1,500円。",
            [("parking_standard_hourly", "通常時間料金を請求する"), ("parking_free_2_hours", "2時間無料駐車券を交付する"), ("parking_valet_luxury", "有料バレーパーキングを利用案内する")],
            "parking_free_2_hours", "parking_standard_hourly"
        ),
        (
            "入館セキュリティ",
            "入館証を首から下げている場合は「入場許可」、不携帯の場合は「受付へ誘導」。来訪者：入館証着用。",
            "入館証を首から下げている場合は「入場許可」、不携帯の場合は「受付へ誘導」。来訪者：入館証なし。",
            [("gate_admit_permitted", "セキュリティゲートを開けて入場許可する"), ("gate_direct_to_front_desk", "総合受付窓口へ誘導する"), ("gate_temporary_guest_pass", "臨時ビジター入館証を発行する")],
            "gate_admit_permitted", "gate_direct_to_front_desk"
        ),
        (
            "手荷物受託",
            "手荷物重量23kg以下は「追加料金なし受託」、23kg超過は「超過料金3,000円請求」。計量値：20kg。",
            "手荷物重量23kg以下は「追加料金なし受託」、23kg超過は「超過料金3,000円請求」。計量値：28kg。",
            [("bag_charge_excess_3000", "超過料金3,000円を請求する"), ("bag_special_cargo_declaration", "大型特殊手荷物として別窓口へ案内する"), ("bag_accept_free_standard", "追加料金なしで受託荷物を受け入れる")],
            "bag_accept_free_standard", "bag_charge_excess_3000"
        ),
        (
            "通信帯域制御",
            "月間データ通信量が50GBを超えた場合は「速度128kbps制限」、50GB以内は「高速通信維持」。当月利用：62GB。",
            "月間データ通信量が50GBを超えた場合は「速度128kbps制限」、50GB以内は「高速通信維持」。当月利用：31GB。",
            [("net_maintain_high_speed", "高速通信をそのまま維持する"), ("net_throttle_to_128kbps", "通信速度を128kbpsに制限する"), ("net_additional_data_purchase", "追加データパケット購入ページへ誘導する")],
            "net_throttle_to_128kbps", "net_maintain_high_speed"
        ),
        (
            "図書館貸出",
            "延滞図書がない利用者は「新規貸出可能」、1冊でも延滞がある利用者は「新規貸出停止」。利用者：延滞ゼロ。",
            "延滞図書がない利用者は「新規貸出可能」、1冊でも延滞がある利用者は「新規貸出停止」。利用者：延滞が2冊あり。",
            [("lib_deny_due_to_overdue", "延滞図書があるため新規貸出を停止する"), ("lib_allow_checkout_normal", "延滞なしを確認し新規貸出を許可する"), ("lib_in_library_reading_only", "館内閲覧のみ利用を許可する")],
            "lib_allow_checkout_normal", "lib_deny_due_to_overdue"
        ),
        (
            "夜間入館",
            "管理職は夜間カード解錠で「直接入館可能」、一般社員は「警備室記帳が必須」。対象者：営業部長（管理職）。",
            "管理職は夜間カード解錠で「直接入館可能」、一般社員は「警備室記帳が必須」。対象者：入社1年目社員。",
            [("acc_direct_card_entry", "管理職カード解錠により直接入館を許可する"), ("acc_require_guard_log", "警備室での入館簿記帳を必須とする"), ("acc_escort_by_colleague", "所属部門社員による同伴入館を要請する")],
            "acc_direct_card_entry", "acc_require_guard_log"
        ),
        (
            "割増手当",
            "法定休日の勤務は「35%割増賃金を支給」、通常平日の所定労働は「通常賃金を支給」。本日の勤務：日曜日（法定休日）。",
            "法定休日の勤務は「35%割増賃金を支給」、通常平日の所定労働は「通常賃金を支給」。本日の勤務：水曜日（通常平日）。",
            [("wage_pay_standard_rate", "通常賃金を支給する"), ("wage_pay_35pct_premium", "法定休日労働として35%割増賃金を支給する"), ("wage_pay_25pct_night_premium", "深夜労働として25%割増賃金を支給する")],
            "wage_pay_35pct_premium", "wage_pay_standard_rate"
        ),
        (
            "健康診断",
            "BMIが25以上かつ空腹時血糖値126以上の受診者は「要精密検査判定」、それ以外は「異常なし合格判定」。受診者：BMI 28、血糖値145。",
            "BMIが25以上かつ空腹時血糖値126以上の受診者は「要精密検査判定」、それ以外は「異常なし合格判定」。受診者：BMI 22、血糖値95。",
            [("med_pass_healthy_normal", "基準内を確認し異常なし合格判定とする"), ("med_order_detailed_retest", "基準超過のため要精密検査判定とする"), ("med_lifestyle_guidance", "特定保健指導・生活習慣改善指導を案内する")],
            "med_order_detailed_retest", "med_pass_healthy_normal"
        ),
        (
            "出張宿泊費",
            "海外出張は「1泊18,000円を定額支給」、国内出張は「1泊10,000円を定額支給」。今回の出張：ドイツ（海外出張）。",
            "海外出張は「1泊18,000円を定額支給」、国内出張は「1泊10,000円を定額支給」。今回の出張：大阪（国内出張）。",
            [("travel_domestic_10k_yen", "国内出張として1泊10,000円を支給する"), ("travel_overseas_18k_yen", "海外出張として1泊18,000円を支給する"), ("travel_day_trip_allowance", "日帰り出張手当として3,000円を支給する")],
            "travel_overseas_18k_yen", "travel_domestic_10k_yen"
        ),
    ]

    for idx, (title, s1, s2, c_defs, t1, t2) in enumerate(perm_scenarios):
        for rep in range(6):
            gid = f"tb_prt_prm_{idx*6 + rep + 1:03d}"
            c_shuffled = list(c_defs)
            rng.shuffle(c_shuffled)
            choices = make_choices(c_shuffled)
            q = f"判定選定：{title}のルールに基づき適切な選択肢を選択してください。"

            records.append({
                "id": f"{gid}_s1",
                "group_id": gid,
                "family": "perturbation_invariance",
                "perturbation_type": "candidate_permutation_and_id",
                "context": f"【ルール】{s1}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2",
                "group_id": gid,
                "family": "perturbation_invariance",
                "perturbation_type": "candidate_permutation_and_id",
                "context": f"【ルール】{s2}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    # Category 2: Filler Context & Inverted Sentence Order (Clean actionable choices, 60 pairs = 120 records)
    fillers = [
        "今日は朝から青空が広がり穏やかな天候です。オフィスの花瓶の花を交換しました。",
        "近隣の幹線道路で水道管の埋設工事が行われています。昼休みは近所のパン屋が人気です。",
        "社内報の今月号には新設されたフットサル部の活動報告が写真付きで掲載されています。",
        "自動販売機に新商品の緑茶が補充されました。エレベーターホールにマットが敷かれています。",
        "昨夜のプロ野球中継は延長戦の末に劇的なサヨナラ勝ちでした。今朝の新聞一面でした。",
        "会議室のプロジェクターの電源コードが新品に交換されました。快適に利用できます。"
    ]

    core_conds = [
        ("受入判定", "資材の受入検査において、傷なし・寸法正常であれば「受入合格」、異常があれば「受入不合格・返品」。", "検査結果：傷なし寸法正常。", "検査結果：表面に大きな亀裂あり。", "accept_materials_passed", "受入合格として倉庫棚へ格納する", "reject_materials_defect", "受入不合格として業者へ返品する"),
        ("決済判定", "引き落とし口座の残高が請求金額以上なら「振替実行」、不足なら「振替不能エラー」。", "残高5万円、請求3万円。", "残高1万円、請求3万円。", "debit_execute_success", "口座振替を正常実行する", "debit_error_insufficient_funds", "残高不足により振替不能とする"),
        ("返金判定", "レシート持参なら「全額現金返金」、レシートなしなら「店舗ポイント返還」。", "購入時のレシートを持参。", "レシート紛失のため持参なし。", "refund_cash_full", "全額現金で返金対応を行う", "refund_points_store", "店舗ポイントで返還対応を行う"),
        ("アクセス判定", "セキュリティトークン有効なら「ログイン承認」、期限切れなら「ログイン拒否」。", "トークン有効期限内。", "トークンは先週で期限切れ。", "auth_approve_login", "ログインを承認し管理画面へ遷移する", "auth_deny_expired", "ログインを拒絶しエラーを表示する"),
        ("割引判定", "会員証提示なら「10%優待割引」、提示なしなら「定価精算」。", "ゴールド会員証を提示。", "会員証不携帯・提示なし。", "apply_10pct_member_discount", "10%優待割引を適用して精算する", "charge_full_regular_price", "通常定価で精算処理を行う"),
        ("乗車案内", "特急券所持なら「特急列車へ誘導」、普通乗車券のみなら「普通列車へ誘導」。", "特急指定席券を提示。", "普通乗車券のみ提示。", "guide_to_express_train", "特急列車への乗車をご案内する", "guide_to_local_train", "普通列車への乗車をご案内する"),
        ("審査結果", "信用スコア650以上なら「即時融資承認」、650未満なら「二次審査書類提出」。", "申込者スコア：720点。", "申込者スコア：580点。", "approve_instant_loan_disbursement", "即時融資実行を承認する", "route_to_secondary_document_review", "二次審査・追加書類確認へ回す"),
        ("手荷物判定", "3辺合計115cm以内なら「機内持込許可」、超過なら「貨物室受託」。", "手荷物合計：100cm。", "手荷物合計：135cm。", "permit_cabin_baggage", "機内持込手荷物として許可する", "check_baggage_to_cargo", "貨物室受託手荷物として預かる"),
        ("出社判定", "解熱後24時間経過なら「出社可能」、発熱継続なら「自宅待機」。", "昨日朝解熱し24時間経過。", "現在も38.2度の発熱中。", "allow_office_attendance", "通常通りの出社を許可する", "mandate_home_quarantine", "自宅待機を指示する"),
        ("入会判定", "年齢18歳以上なら「単独入会許可」、18歳未満なら「保護者同意要」。", "申込者年齢：22歳。", "申込者年齢：16歳。", "admit_independent_member", "単独での本入会を許可する", "require_guardian_consent_form", "保護者同意書の提出を求める"),
    ]

    for idx, (title, rule, s1, s2, cid1, txt1, cid2, txt2) in enumerate(core_conds):
        for rep in range(6):
            gid = f"tb_prt_flr_{idx*6 + rep + 1:03d}"
            f_sent = fillers[rep % len(fillers)]
            c_defs = [(cid1, txt1), (cid2, txt2), ("refer_to_supervisor_review", "判断保留として上席責任者の確認を仰ぐ")]
            choices = make_choices(c_defs)
            q = f"判定選定：{title}のルールに従い適切な対応を選択してください。"

            records.append({
                "id": f"{gid}_s1",
                "group_id": gid,
                "family": "perturbation_invariance",
                "perturbation_type": "filler_and_sentence_order",
                "context": f"{f_sent}【判定基準】{rule}現況の確認：{s1}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": cid1}
            })
            records.append({
                "id": f"{gid}_s2",
                "group_id": gid,
                "family": "perturbation_invariance",
                "perturbation_type": "filler_and_sentence_order",
                "context": f"現況の確認：{s2}【判定基準】{rule}{f_sent}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": cid2}
            })

    # Category 3: Register & Syntax Variations (Clean Contrastive Facts, 60 pairs = 120 records)
    register_scenarios = [
        (
            "受領・締結確認",
            "【丁寧体】ご送付いただきました契約書原本を無事に拝受いたしました。内容に問題ございませんので、速やかに捺印・締結手続きを進めさせていただきます。",
            "【簡潔体】送付書類を確認したが、署名捺印欄に不備あり。捺印欄を修正の上、至急再送されたし。",
            [("confirm_receipt_and_process_seal", "契約書原本の受領を確認し捺印・締結手続きを進める"), ("reject_and_request_resubmission", "書類不備を確認し修正・再送を要求する"), ("archive_unrelated_general_record", "定型記録として保管棚へ収納する")],
            "confirm_receipt_and_process_seal", "reject_and_request_resubmission"
        ),
        (
            "納期対応",
            "【丁寧体】平素は格別のお引き立てを賜り厚く御礼申し上げます。昨日納期の資材が未着となっております。現在の配送状況をご教示いただけますでしょうか。",
            "【簡潔体】資材の受入検査完了。全品仕様通りにつき検収書を発行する。",
            [("inquire_overdue_delivery_status", "納期遅延につき配送状況の至急確認を求める"), ("accept_delivery_and_issue_certificate", "納品受入を検収し検収書を発行する"), ("cancel_purchase_agreement", "売買契約の即時解除を通告する")],
            "inquire_overdue_delivery_status", "accept_delivery_and_issue_certificate"
        ),
        (
            "パッチ適用作業",
            "【丁寧体】ご依頼いただきました基幹サーバーのセキュリティパッチ適用作業ですが、予定通り無事に全工程が完了いたしましたことをご報告申し上げます。",
            "【簡潔体】パッチ適用後にDB応答遅延が多発。直ちに直前バージョンへのロールバックを実行されたし。",
            [("report_patch_installation_complete", "セキュリティパッチの正常完了を報告する"), ("request_emergency_rollback", "障害発生のため緊急ロールバックを指示する"), ("schedule_next_routine_maintenance", "次期定期メンテナンスの予定に組み込む")],
            "report_patch_installation_complete", "request_emergency_rollback"
        ),
        (
            "面談日程",
            "【丁寧体】過日賜りましたご面談のお申し込み、大変光栄に存じます。来週水曜日の14時より、弊社応接室にてお迎えさせていただきたく存じます。",
            "【簡潔体】当日は急な出張が入ったため来訪不可。翌週以降への日程リスケジュールを求む。",
            [("confirm_meeting_schedule", "指定日時での対面面談日程を確定する"), ("reschedule_interview_to_next_week", "都合により面談日程の延期・再調整を依頼する"), ("conduct_interview_remotely", "オンラインWeb会議への切り替えを打診する")],
            "confirm_meeting_schedule", "reschedule_interview_to_next_week"
        ),
        (
            "経費精算",
            "【丁寧体】ご提出いただきました立替経費申請につきまして、領収書の宛名が空欄となっておりました。大変恐縮ながら修正の上で再提出をお願い申し上げます。",
            "【簡潔体】経費申請確認。添付領収書および金額整合性OK。本日付で振込承認完了。",
            [("reject_expense_for_missing_recipient", "宛名不備のため経費申請を差し戻し再提出を求める"), ("approve_expense_reimbursement", "添付証憑の整合性を確認し経費精算を承認する"), ("hold_for_tax_accountant_review", "顧問税理士による精査のため一時保留とする")],
            "reject_expense_for_missing_recipient", "approve_expense_reimbursement"
        ),
        (
            "休日出勤",
            "【丁寧体】突発的な障害対応に伴い、誠に心苦しい限りではございますが、今週土曜日の休日出勤にご協力賜りたく伏してお願い申し上げます。",
            "【簡潔体】障害復旧完了につき土曜の臨時体制は解除。各自所定の通常休日を取得されたし。",
            [("request_weekend_overtime_attendance", "障害対応に伴う休日出勤の要請を行う"), ("stand_down_weekend_shift", "休日出勤態勢を解除し通常休暇の取得を指示する"), ("convert_to_remote_on_call", "自宅での電話待機（オンコール）体制へ移行する")],
            "request_weekend_overtime_attendance", "stand_down_weekend_shift"
        ),
        (
            "値引き要請",
            "【丁寧体】ご提示の値引き要求につきまして、原材料高騰の折、甚だ不本意ながらご要望に沿いかねる次第でございます。何卒ご理解賜りたく存じます。",
            "【簡潔体】年間包括契約の締結を条件として、提示の5%値引きを承諾する。",
            [("decline_discount_request_firmly", "原価高騰を理由に値引き要求をお断りする"), ("grant_conditional_volume_discount", "条件付きで値引き要請を承諾する"), ("refer_to_headquarters_pricing_board", "本社価格決定委員会へ判断を委ねる")],
            "decline_discount_request_firmly", "grant_conditional_volume_discount"
        ),
        (
            "振込予定",
            "【丁寧体】誠に遺憾ながら、弊社の資金決済システムの不具合により、本日予定のお振込みが明朝へ遅延する見込みとなりました。深くお詫び申し上げます。",
            "【簡潔体】請求書記載の指定口座へ本日付で送金完了。振込明細書を添付送付。",
            [("apologize_for_payment_delay", "システム障害による振込遅延をお詫び報告する"), ("confirm_payment_transfer_completed", "指定口座への送金手続き完了を通知する"), ("request_vendor_bank_account_change", "振込先金融機関口座の再確認を求める")],
            "apologize_for_payment_delay", "confirm_payment_transfer_completed"
        ),
        (
            "有休申請",
            "【丁寧体】過日いただきました有給休暇取得のご申請、業務調整がつきましたので謹んで承認とさせていただきます。ごゆっくりご静養ください。",
            "【簡潔体】同日は重要システムの全社リリース日につき休暇取得不可。別日への変更を求む。",
            [("approve_paid_time_off_leave", "有給休暇の取得申請を承認する"), ("deny_paid_leave_critical_release", "リリース日重複のため休暇日時の変更を求める"), ("request_half_day_leave_compromise", "午前半休への振替を打診する")],
            "approve_paid_time_off_leave", "deny_paid_leave_critical_release"
        ),
        (
            "退職手続き",
            "【丁寧体】ご提出いただきました退職届、長年のご貢献に深く敬意を表しつつ、正式に受理させていただく運びとなりました。今後のご健勝をお祈り申し上げます。",
            "【簡潔体】退職届は受理保留。処遇見直しの面談日程を来週設定されたし。",
            [("accept_resignation_notice_officially", "退職届を正式に受理し手続きへ進める"), ("hold_resignation_for_counteroffer", "退職届を保留とし条件見直し面談を実施する"), ("transfer_to_subsidiary_company", "関連子会社への転籍出向を提案する")],
            "accept_resignation_notice_officially", "hold_resignation_for_counteroffer"
        ),
    ]

    for idx, (title, s1, s2, c_defs, t1, t2) in enumerate(register_scenarios):
        for rep in range(6):
            gid = f"tb_prt_reg_{idx*6 + rep + 1:03d}"
            choices = make_choices(c_defs)
            q = f"文脈判定：{title}のメッセージから読み取れる適切な対応を選択してください。"

            records.append({
                "id": f"{gid}_s1",
                "group_id": gid,
                "family": "perturbation_invariance",
                "perturbation_type": "register_and_syntax",
                "context": s1,
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2",
                "group_id": gid,
                "family": "perturbation_invariance",
                "perturbation_type": "register_and_syntax",
                "context": s2,
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    # Category 4: Parenthetical Caveats (60 pairs = 120 records)
    caveat_scenarios = [
        (
            "手荷物持込液体制限",
            "液体物の機内持ち込みは100ml以下の容器に制限する（※ただし医師処方のインスリン注射薬等の医薬品はこの限りではない）。所持品：処方箋付きインスリン注射器。",
            "液体物の機内持ち込みは100ml以下の容器に制限する（※ただし医師処方のインスリン注射薬等の医薬品はこの限りではない）。所持品：市販のミネラルウォーター500ml。",
            [("permit_prescription_medicine_liquid", "医薬品例外規定に基づき機内持込を許可する"), ("confiscate_excess_liquid_at_security", "100ml超過かつ例外非該当のため保安検査で没収する"), ("permit_duty_free_sealed_liquid", "免税店専用密閉袋に封入された液体として持込許可する")],
            "permit_prescription_medicine_liquid", "confiscate_excess_liquid_at_security"
        ),
        (
            "工場敷地内安全靴",
            "構内では安全靴の着用を義務付ける［注釈：事務棟本館の受付ロビー商談のみの場合はスニーカー等の一般靴でも可］。来館目的：事務棟ロビーでの打ち合わせ。",
            "構内では安全靴の着用を義務付ける［注釈：事務棟本館の受付ロビー商談のみの場合はスニーカー等の一般靴でも可］。来館目的：第2工場製造ラインでの機器点検。",
            [("permit_entry_lobby_exemption", "ロビー商談の例外規定適用によりスニーカーで入館許可する"), ("deny_entry_lacking_safety_boots", "製造現場立入のため安全靴未着用で入館を拒否する"), ("lend_temporary_visitor_boots", "来訪者用貸出安全靴を貸与して入場許可する")],
            "permit_entry_lobby_exemption", "deny_entry_lacking_safety_boots"
        ),
        (
            "深夜残業禁止規程",
            "22時以降の勤務は禁止とする（※ただしシステム緊急障害対応で本部長の事前承認を得た場合を除く）。状況：障害発生・本部長承認済み。",
            "22時以降の勤務は禁止とする（※ただしシステム緊急障害対応で本部長の事前承認を得た場合を除く）。状況：通常業務の残務処理・本部長承認なし。",
            [("approve_emergency_overtime_approved", "本部長承認ありのため22時以降の緊急残業を承認する"), ("forbid_overtime_and_order_leaving", "承認なき通常残業のため22時退勤を命じる"), ("request_next_morning_early_shift", "翌朝の早朝勤務へ業務を振り替える")],
            "approve_emergency_overtime_approved", "forbid_overtime_and_order_leaving"
        ),
        (
            "宿泊予約取消料",
            "前日20時までのキャンセルは無料とする（※ただし年末年始・GWの特別繁忙期予約は7日前から50%の取消料が発生する）。通常期の予約、前日15時にキャンセル連絡。",
            "前日20時までのキャンセルは無料とする（※ただし年末年始・GWの特別繁忙期予約は7日前から50%の取消料が発生する）。年末年始特別プラン、前日15時にキャンセル連絡。",
            [("waive_cancellation_fee_normal_period", "通常期かつ前日20時前の連絡のため取消料を免除する"), ("charge_50pct_cancellation_fee_holiday", "年末年始特約に基づき50%の取消料を請求する"), ("charge_100pct_cancellation_fee_noshow", "連絡なし不泊として100%の取消料を請求する")],
            "waive_cancellation_fee_normal_period", "charge_50pct_cancellation_fee_holiday"
        ),
        (
            "タクシー代経費精算",
            "タクシーの利用は原則不認可とする（※終電を喪失した場合または重い機材を搬送する場合を除く）。精算理由：深夜25時まで障害復旧に当たり終電喪失。",
            "タクシーの利用は原則不認可とする（※終電を喪失した場合または重い機材を搬送する場合を除く）。精算理由：朝の通勤で満員電車を避けたかったため。",
            [("reimburse_taxi_fare_missed_train", "終電喪失の例外事由に合致するため経費精算を認める"), ("deny_taxi_fare_unjustified_reason", "私的理由のため原則通りタクシー代の精算を却下する"), ("reimburse_public_transit_only", "始発以降の公共交通機関の運賃のみ精算する")],
            "reimburse_taxi_fare_missed_train", "deny_taxi_fare_unjustified_reason"
        ),
        (
            "受講修了基準",
            "全科目80点以上で修了認定とする（※追試で90点以上を獲得した科目は本試験不合格でも合格とみなす）。鈴木さん：本試験75点、追試92点。",
            "全科目80点以上で修了認定とする（※追試で90点以上を獲得した科目は本試験不合格でも合格とみなす）。高橋さん：本試験75点、追試85点。",
            [("certify_completion_under_retest_rule", "追試90点以上の特例に基づき受講修了を認定する"), ("fail_completion_retest_under_90", "追試90点未達のため受講不合格・再受講とする"), ("grant_conditional_credit_assignment", "追加課題レポート提出を条件に仮修了とする")],
            "certify_completion_under_retest_rule", "fail_completion_retest_under_90"
        ),
        (
            "会員ラウンジ同伴者",
            "同伴者の入場は1名まで無料とする［特記：ダイヤモンド会員に限り同伴者3名まで無料］。来場者：ダイヤモンド会員、同伴者2名。",
            "同伴者の入場は1名まで無料とする［特記：ダイヤモンド会員に限り同伴者3名まで無料］。来場者：一般レギュラー会員、同伴者2名。",
            [("admit_all_companions_diamond_perk", "ダイヤモンド会員特典により同伴者2名の入場を許可する"), ("charge_extra_fee_for_second_companion", "一般枠超過のため同伴者2人目の追加料金を請求する"), ("guide_to_public_cafe_lounge", "一般有料カフェラウンジへ同伴者を案内する")],
            "admit_all_companions_diamond_perk", "charge_extra_fee_for_second_companion"
        ),
        (
            "返金受付条件",
            "開封後の商品は返品不可とする（※商品自体に製造上の初期不良・欠損があった場合を除く）。商品状態：開封済み、通電しない初期不良あり。",
            "開封後の商品は返品不可とする（※商品自体に製造上の初期不良・欠損があった場合を除く）。商品状態：開封済み、色やデザインが好みに合わなかった私的都合。",
            [("accept_return_for_defective_product", "初期不良の例外適用により開封後も返品返金を受け付ける"), ("refuse_return_for_opened_cosmetic", "自己都合かつ開封済みのため返品受付を拒否する"), ("offer_exchange_for_equal_value", "同等額の別商品への交換のみ受け付ける")],
            "accept_return_for_defective_product", "refuse_return_for_opened_cosmetic"
        ),
        (
            "特急指定席変更",
            "発車時刻前の乗車券変更は1回に限り手数料無料（※セール特別企画乗車券はこの限りでなく変更不可）。乗車券種別：通常購入の指定席特急券。",
            "発車時刻前の乗車券変更は1回に限り手数料無料（※セール特別企画乗車券はこの限りでなく変更不可）。乗車券種別：トクだ値50%引き特別企画乗車券。",
            [("permit_free_ticket_modification", "通常特急券のため1回目の無料日程変更を許可する"), ("prohibit_ticket_modification_promo", "企画乗車券特約に基づき日程変更を不可とお断りする"), ("refund_with_standard_cancellation_fee", "所定の払戻手数料を差し引いて払い戻す")],
            "permit_free_ticket_modification", "prohibit_ticket_modification_promo"
        ),
        (
            "図書館特別資料閲覧",
            "貴重古文書の閲覧は大学教授等に限る（※一般研究員であっても機関長の推薦状を所持する場合は閲覧を許可する）。申請者：一般研究員、推薦状持参。",
            "貴重古文書の閲覧は大学教授等に限る（※一般研究員であっても機関長の推薦状を所持する場合は閲覧を許可する）。申請者：一般研究員、推薦状なし身分証のみ提示。",
            [("grant_rare_manuscript_access", "推薦状持参の例外規定に基づき貴重古文書の閲覧を許可する"), ("deny_access_lacking_recommendation_letter", "推薦状不所持のため貴重資料の閲覧をお断りする"), ("permit_digital_replica_viewing", "原本ではなくデジタル高精細複製版の閲覧を案内する")],
            "grant_rare_manuscript_access", "deny_access_lacking_recommendation_letter"
        ),
    ]

    for idx, (title, s1, s2, c_defs, t1, t2) in enumerate(caveat_scenarios):
        for rep in range(6):
            gid = f"tb_prt_cav_{idx*6 + rep + 1:03d}"
            choices = make_choices(c_defs)
            q = f"条文解釈判定：{title}の括弧書き・注記の特例に基づき適切な判断を選択してください。"

            records.append({
                "id": f"{gid}_s1",
                "group_id": gid,
                "family": "perturbation_invariance",
                "perturbation_type": "parenthetical_caveats",
                "context": f"【規定】{s1}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2",
                "group_id": gid,
                "family": "perturbation_invariance",
                "perturbation_type": "parenthetical_caveats",
                "context": f"【規定】{s2}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    # Category 5: Prompt Order & Premise Inversion (60 pairs = 120 records)
    order_templates = [
        (
            "返品特約",
            "商品タグ未切断かつレシート持参なら「良品交換」、タグ切断または使用済みなら「交換不可案内」。",
            "顧客持参：購入3日後、タグ付き・レシートあり・未使用。",
            "顧客持参：購入3日後、タグ切断済み・一度着用し洗濯済み。",
            [("exchange_item_accepted", "良品交換を受付いたします"), ("refuse_exchange_used", "使用済みのため交換不可と案内いたします"), ("issue_gift_card_half", "購入額の半額金券を案内いたします")],
            "exchange_item_accepted", "refuse_exchange_used"
        ),
        (
            "深夜勤務手当",
            "実労働が22時から翌5時までの時間帯を含むなら「深夜割増支給」、含まないなら「通常時間給」。",
            "勤務実績：午後21時から翌朝6時までの夜勤シフト。",
            "勤務実績：午前9時から午後18時までの日勤シフト。",
            [("pay_night_shift_premium", "深夜割増手当を支給する"), ("pay_standard_hourly_rate", "通常時間給で支給する"), ("grant_comp_time_off", "代休付与で処理する")],
            "pay_night_shift_premium", "pay_standard_hourly_rate"
        ),
        (
            "手荷物機内持込",
            "三辺合計115cm以内かつ重量10kg以下なら「機内持込許可」、超過時は「受託手荷物預け入れ」。",
            "手荷物測定：三辺合計98cm、重量7.5kg。",
            "手荷物測定：三辺合計135cm、重量14.0kg。",
            [("permit_cabin_carry_on", "機内持ち込みを許可する"), ("check_in_at_baggage_counter", "受託手荷物として預け入れを指示する"), ("confiscate_oversize_bag", "荷物を没収破棄する")],
            "permit_cabin_carry_on", "check_in_at_baggage_counter"
        ),
        (
            "高所作業安全帯",
            "作業床の高さが2m以上なら「フルハーネス型安全帯着用」、2m未満なら「任意着用」。",
            "現場測定：足場作業床の高さ5.5m。",
            "現場測定：脚立作業床の高さ1.2m。",
            [("mandate_full_body_harness", "フルハーネス型安全帯の着用を義務付ける"), ("allow_optional_harness", "安全帯の着用を任意とする"), ("prohibit_all_climbing", "すべての昇降を禁止する")],
            "mandate_full_body_harness", "allow_optional_harness"
        ),
        (
            "高速道路ETC割引",
            "通過時刻が0時から4時までの深夜なら「深夜割引30%適用」、それ以外の時間帯は「通常料金」。",
            "料金所通過：午前2時15分（ETC通信正常）。",
            "料金所通過：午後14時30分（ETC通信正常）。",
            [("apply_late_night_30pct_discount", "深夜割引30%を適用する"), ("charge_standard_toll_rate", "通常料金を請求する"), ("impound_etc_vehicle", "車両を料金所で差し押さえる")],
            "apply_late_night_30pct_discount", "charge_standard_toll_rate"
        ),
        (
            "図書館図書貸出",
            "利用カード有効期限内かつ延滞本ゼロなら「貸出承認」、延滞本ありなら「貸出停止」。",
            "利用者状況：有効カード所持、延滞本なし。",
            "利用者状況：有効カード所持、2週間前の本を1冊延滞中。",
            [("approve_book_checkout", "図書の貸出を承認する"), ("suspend_checkout_overdue", "延滞解消まで新規貸出を停止する"), ("cancel_library_membership", "利用登録を永久抹消する")],
            "approve_book_checkout", "suspend_checkout_overdue"
        ),
        (
            "オフィス入退館",
            "社員証ICカード所持なら「フラッパーゲート通過許可」、不携帯なら「守衛窓口で仮証発行」。",
            "来社状況：社員証ICカードをリーダーにかざした。",
            "来社状況：社員証を自宅に忘れ携帯していない。",
            [("permit_gate_entry_pass", "フラッパーゲートの通過を許可する"), ("direct_to_guard_desk_pass", "守衛窓口で仮入館証を発行させる"), ("report_to_police_trespass", "不法侵入として警察に通報する")],
            "permit_gate_entry_pass", "direct_to_guard_desk_pass"
        ),
        (
            "特急指定席子供料金",
            "満6歳以上12歳未満の小学生なら「小児半額料金」、満12歳以上なら「大人全額料金」。",
            "乗客年齢：10歳の小学4年生。",
            "乗客年齢：16歳の高校1年生。",
            [("charge_child_half_fare", "小児半額料金を適用する"), ("charge_adult_full_fare", "大人全額料金を適用する"), ("provide_free_luxury_suite", "最上級個室を無償提供する")],
            "charge_child_half_fare", "charge_adult_full_fare"
        ),
        (
            "定期健診再検査",
            "空腹時血糖値が126mg/dL以上なら「精密再検査受診指示」、110mg/dL未満なら「正常判定」。",
            "検診結果：空腹時血糖値148mg/dL。",
            "検診結果：空腹時血糖値92mg/dL。",
            [("mandate_followup_glucose_exam", "医療機関での精密再検査受診を指示する"), ("certify_normal_glucose_level", "正常範囲として判定を完了する"), ("admit_to_icu_immediately", "集中治療室へ緊急搬送入院させる")],
            "mandate_followup_glucose_exam", "certify_normal_glucose_level"
        ),
        (
            "オンライン送金限度額",
            "ワンタイムパスワード（OTP）認証完了なら「1回あたり送金上限500万円」、未設定なら「上限50万円」。",
            "送金認証：スマホアプリOTP認証完了。",
            "送金認証：OTP未設定・パスワードのみ入力。",
            [("allow_high_limit_5m_transfer", "送金上限500万円として送金を実行する"), ("restrict_to_low_limit_500k", "送金上限50万円に制限し過剰分を保留する"), ("freeze_entire_bank_account", "顧客の口座を全面凍結する")],
            "allow_high_limit_5m_transfer", "restrict_to_low_limit_500k"
        ),
    ]

    for idx, (title, rule, s1, s2, c_defs, t1, t2) in enumerate(order_templates):
        choices = make_choices(c_defs)
        for rep in range(6):
            gid = f"tb_pert_ord_{idx*6 + rep + 1:03d}"
            if rep % 2 == 0:
                ctx1 = f"【規程】{rule}\n事象確認：{s1}"
                ctx2 = f"【規程】{rule}\n事象確認：{s2}"
            else:
                ctx1 = f"事象確認：{s1}\nなお、【社内規程】『{rule}』と定められています。"
                ctx2 = f"事象確認：{s2}\nなお、【社内規程】『{rule}』と定められています。"
            q = f"判定処理：{title}の基準に従い適切な判断を選択してください。"
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "perturbation_invariance", "subdomain": "premise_ordering", "context": ctx1, "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t1}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "perturbation_invariance", "subdomain": "premise_ordering", "context": ctx2, "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t2}})

    # Category 6: Delimiters & Formats Robustness (60 pairs = 120 records)
    delim_templates = [
        (
            "倉庫出庫安全靴",
            "物流倉庫規程：荷役エリアへ立ち入る際は安全靴の着用を義務付ける。一般スニーカーでの進入は禁止する。",
            "作業員装具：つま先鋼板入りJIS規格安全靴を着用。",
            "作業員装具：布製ランニングスニーカーを着用。",
            [("admit_safety_shoes_passed", "安全靴着用を確認し荷役エリア進入を許可する"), ("block_sneakers_entry_warn", "スニーカー着用のため進入を禁止し履き替えを命じる"), ("revoke_driver_license", "作業員の運転免許証を失効させる")],
            "admit_safety_shoes_passed", "block_sneakers_entry_warn"
        ),
        (
            "クリーンルーム防塵マスク",
            "製造環境基準：クラス1000高清浄度ルームでは二重防塵マスク装着が必須である。マスク未着用は入室不可。",
            "更衣室確認：規定の二重防塵マスクを正しく鼻まで装着。",
            "更衣室確認：マスクを着用せず顎にかけている（口鼻露出）。",
            [("unlock_cleanroom_airshower", "マスク装着確認により入室エアシャワーを作動する"), ("lock_airshower_require_mask", "マスク不備のためエアシャワーを施錠し入室を拒絶する"), ("sterilize_with_gamma_ray", "作業員にガンマ線を照射する")],
            "unlock_cleanroom_airshower", "lock_airshower_require_mask"
        ),
        (
            "アルコール呼気チェック",
            "運行管理基準：点呼時の呼気アルコール濃度が0.00mg/L（検知ゼロ）なら運行許可。数値検知時は乗務禁止。",
            "測定結果：アルコール検知器測定値0.00mg/L（正常）。",
            "測定結果：アルコール検知器測定値0.18mg/L（基準超過）。",
            [("dispatch_driver_cleared", "アルコールゼロを確認し車両運行を許可する"), ("prohibit_driving_call_sub", "アルコール検知のため乗務を禁止し代務運転手を手配する"), ("seize_commercial_truck", "事業用トラックをその場で解体処分する")],
            "dispatch_driver_cleared", "prohibit_driving_call_sub"
        ),
        (
            "危険物タンク液位管理",
            "タンク保安基準：タンク内液位が上限90%以下であれば注入継続。90%超過時は緊急遮断弁を閉止する。",
            "液位計測定：現在液位74%（適正範囲）。",
            "液位計測定：現在液位93%（上限超過）。",
            [("continue_tank_filling", "液位適正を確認し危険物注入を継続する"), ("trip_emergency_shutoff_valve", "上限超過検知により緊急遮断弁を閉止する"), ("puncture_tank_bottom", "タンク底部に穴を開けて漏洩させる")],
            "continue_tank_filling", "trip_emergency_shutoff_valve"
        ),
        (
            "サーバールーム入室権限",
            "セキュリティポリシー：特権管理者ICカードかつ指紋認証一致でドア解錠。認証不一致時は警報を発報する。",
            "生体認証機：特権ICカード確認、指紋認証一致（OK）。",
            "生体認証機：特権ICカード確認、指紋認証不一致（NG）。",
            [("unlock_server_room_door", "認証成功を確認しサーバールーム扉を解錠する"), ("lock_door_raise_alert", "生体認証不一致のため施錠を維持し警報を発報する"), ("cut_main_power_grid", "地域全体の商用送電線を切断する")],
            "unlock_server_room_door", "lock_door_raise_alert"
        ),
        (
            "産業廃棄物マニフェスト",
            "産廃処理規程：マニフェストE票の返送受領確認完了で処分完了報告。未受領時は処理業者へ照会連絡を行う。",
            "管理台帳照会：処分業者よりE票返送確認済み。",
            "管理台帳照会：期日経過もE票未返送（未受領）。",
            [("close_manifest_record_done", "処分完了を確認しマニフェスト台帳を完了登録する"), ("inquire_waste_contractor_late", "E票未達のため処理業者へ照会確認の連絡を行う"), ("dump_waste_in_forest_illegal", "産業廃棄物を近隣山林へ不法投棄する")],
            "close_manifest_record_done", "inquire_waste_contractor_late"
        ),
        (
            "生体認証決済上限",
            "電子決済約款：顔認証または指紋認証による生体確認が取れている取引は即時決済承認。未確認はSMS認証へ誘導。",
            "決済端末：顔認証照合一致（生体確認完了）。",
            "決済端末：生体認証スキップ（パスコード未入力）。",
            [("approve_biometric_payment", "生体認証完了を確認し即時決済を承認する"), ("route_to_sms_otp_challenge", "生体未確認のためSMS追加認証へ誘導する"), ("delete_user_bank_account", "利用者の銀行預金口座を即時抹消する")],
            "approve_biometric_payment", "route_to_sms_otp_challenge"
        ),
        (
            "エレベーター過負荷制御",
            "昇降機安全基準：積載定員が15名以下かつ定格荷重1000kg以下なら通常昇降。過負荷ブザー鳴動時は扉開放維持。",
            "エレベーター計量：現在乗車11名、荷重780kg。",
            "エレベーター計量：現在乗車16名、荷重1050kg（過負荷）。",
            [("operate_elevator_doors_close", "定格内を確認し扉を閉め昇降を開始する"), ("hold_doors_open_overload", "過負荷警報のため扉を開放維持し降車を促す"), ("sever_elevator_cables", "エレベーターの主索ワイヤーを切断する")],
            "operate_elevator_doors_close", "hold_doors_open_overload"
        ),
        (
            "自動火災報知器鳴動",
            "防災管理規程：受信機で2カ所以上の感知器発報または手動通報ボタン押下で全館非常放送。1カ所のみは現場確認先行。",
            "受信盤：1階熱感知器および2階煙感知器の2カ所同時発報。",
            "受信盤：3階煙感知器1カ所のみ発報（手動ボタンなし）。",
            [("broadcast_emergency_evacuation", "複数感知器発報を確認し全館非常放送を起動する"), ("dispatch_staff_to_investigate", "単一発報のため非常放送を保留し現場確認員を急派する"), ("weld_fire_doors_shut", "防火戸を溶接して住民を閉じ込める")],
            "broadcast_emergency_evacuation", "dispatch_staff_to_investigate"
        ),
        (
            "水道水残留塩素濃度",
            "水道水質基準：給水栓末端の遊離残留塩素が0.10mg/L以上なら給水適正。0.10mg/L未満は塩素次亜注入ポンプ増量。",
            "水質測定値：蛇口残留塩素0.35mg/L（基準適合）。",
            "水質測定値：蛇口残留塩素0.04mg/L（消毒不足）。",
            [("certify_water_supply_safe", "水質基準適合を確認し給水を適正継続する"), ("boost_chlorine_dosing_pump", "残留塩素不足検知により次亜塩素酸注入ポンプを増量する"), ("contaminate_reservoir_with_sewage", "配水池へ下水生汚水を直接混入させる")],
            "certify_water_supply_safe", "boost_chlorine_dosing_pump"
        ),
    ]

    for idx, (title, rule, s1, s2, c_defs, t1, t2) in enumerate(delim_templates):
        choices = make_choices(c_defs)
        for rep in range(6):
            gid = f"tb_pert_del_{idx*6 + rep + 1:03d}"
            if rep < 3:
                ctx1 = f"※社内通達文書【{title}】\n内容：『{rule}』\n確認データ：[{s1}]"
                ctx2 = f"※社内通達文書【{title}】\n内容：『{rule}』\n確認データ：[{s2}]"
            else:
                ctx1 = f"（管理基準メモ）{rule} 現状把握→ {s1}"
                ctx2 = f"（管理基準メモ）{rule} 現状把握→ {s2}"
            q = f"指示選択：{title}の規程に基づき適切なアクションを選択してください。"
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "perturbation_invariance", "subdomain": "delimiters_formatting", "context": ctx1, "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t1}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "perturbation_invariance", "subdomain": "delimiters_formatting", "context": ctx2, "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t2}})

    # Category 7: Surrounding Discourse Noise (Filler at both start & end, 60 pairs = 120 records)
    surround_templates = [
        (
            "鋼材受入引張強度",
            "資材受入検査規則：納入鋼材の引張強度が400MPa以上であれば受入合格と認定する。400MPa未満は受入拒否・返品とする。",
            "試験片の実測引張強度は460MPaでした。",
            "試験片の実測引張強度は340MPaでした。",
            [("accept_steel_materials_certified", "強度400MPa以上のため受入合格と認定する"), ("reject_steel_materials_return", "強度不足のため受入拒否し返品とする"), ("flatten_office_with_steamroller", "ロードローラーで事務所を平らに押し潰す")],
            "accept_steel_materials_certified", "reject_steel_materials_return"
        ),
        (
            "海外旅行傷害保険",
            "旅行保険適用判定：海外渡航先でのケガに対し、日本出国前に加入手続きが完了していれば保険金を給付する。出国後の事後加入は給付対象外とする。",
            "加入記録：日本出国前日21時にWeb契約完了。",
            "加入記録：現地到着3日後にWeb契約。",
            [("payout_travel_insurance_benefit", "出国前加入を確認できたため保険金を給付する"), ("deny_insurance_payout_post_departure", "出国後加入のため給付対象外として不支給とする"), ("cancel_all_insurance_policies_worldwide", "全世界の全保険契約を一方的に破棄する")],
            "payout_travel_insurance_benefit", "deny_insurance_payout_post_departure"
        ),
        (
            "ソフトウェアライセンス配付",
            "ソフトウェア配付基準：ライセンス空き枠が1件以上ある場合は即座にクライアントPCへ自動配信する。空き枠ゼロの場合は購入申請へ回す。",
            "現在の残存ライセンス数：3ライセンス（余裕あり）。",
            "現在の残存ライセンス数：0ライセンス（満杯）。",
            [("deploy_software_automatically", "ライセンス空きがあるため即座に自動配信する"), ("route_to_license_purchase_request", "空き枠ゼロのため新規ライセンス購入申請へ回す"), ("format_all_hard_drives_in_company", "全社ハードディスクを一斉フォーマットする")],
            "deploy_software_automatically", "route_to_license_purchase_request"
        ),
        (
            "口座自動振替実行",
            "口座振替実行ルール：引落日前日時点の普通預金残高が引落請求額以上であれば振替処理を実行する。残高不足の場合は振替不能とする。",
            "請求額：35,000円、前日預金残高：58,000円。",
            "請求額：35,000円、前日預金残高：8,400円。",
            [("execute_direct_debit_transfer", "預金残高充足のため口座振替を実行する"), ("mark_direct_debit_failed_nsf", "残高不足のため振替不能処理とする"), ("steal_bank_vault_with_dynamite", "ダイナマイトで銀行の金庫を爆破する")],
            "execute_direct_debit_transfer", "mark_direct_debit_failed_nsf"
        ),
        (
            "特権サーバールーム入室",
            "入退室管理規定：特権管理者ICカードを所持し指紋認証が一致した技術者のみサーバールームの入室を許可する。認証不一致または未登録者は入室を拒絶する。",
            "本人確認：特権ICカード所持、生体指紋認証一致。",
            "本人確認：一般来訪者カード所持、指紋未登録のため認証不一致。",
            [("permit_datacenter_entry_verified", "生体認証一致を確認しサーバールーム入室を許可する"), ("deny_datacenter_entry_unauthorized", "生体認証不一致のため入室を拒絶する"), ("destroy_all_backup_tapes", "保管中の全バックアップ磁気テープを焼却する")],
            "permit_datacenter_entry_verified", "deny_datacenter_entry_unauthorized"
        ),
        (
            "医薬品保管冷凍庫温度",
            "医薬品保管基準：ワクチン保管用冷凍庫の庫内温度がマイナス20度以下に維持されている場合は品質合格。マイナス20度を超過している場合は品質異常としてロット保留とする。",
            "温度センサー測定値：マイナス24.5度（安定維持）。",
            "温度センサー測定値：マイナス14.0度（温度上昇検知）。",
            [("certify_vaccine_storage_compliant", "規定温度以下を確認しワクチン品質適正と判定する"), ("quarantine_vaccine_temperature_drift", "温度上限超過のため当該ロットを即時保留隔離する"), ("turn_off_hospital_power", "病院の主電源ブレーカーを故意に遮断する")],
            "certify_vaccine_storage_compliant", "quarantine_vaccine_temperature_drift"
        ),
        (
            "危険物タンクローリー乗務",
            "安全輸送規則：危険物取扱者免状（乙種4類以上）を携帯している乗務員に限り給油運行を許可する。免状不携帯または無資格者は乗務不可とする。",
            "乗務員点呼：乙種4類危険物取扱者免状原本を提示携帯。",
            "乗務員点呼：免状を自宅に忘れ不携帯（確認不可）。",
            [("allow_hazmat_tanker_departure", "免状携帯確認によりタンクローリーの出発運行を許可する"), ("prohibit_tanker_departure_no_license", "免状不携帯のため乗務を禁止し代務者を手配する"), ("dump_fuel_into_river", "積載燃料を近隣河川へ投棄する")],
            "allow_hazmat_tanker_departure", "prohibit_tanker_departure_no_license"
        ),
        (
            "注文即日発送締切",
            "出荷管理規定：当日14時00分までに決済確認が完了した注文は即日発送手配を行う。14時00分以降の注文は翌営業日発送とする。",
            "注文確定タイムスタンプ：本日11時25分（決済完了）。",
            "注文確定タイムスタンプ：本日15時40分（決済完了）。",
            [("process_same_day_order_dispatch", "締切時刻前のため本日中に即日発送手配を行う"), ("schedule_next_day_order_dispatch", "14時以降の確定のため翌営業日の発送手配とする"), ("confiscate_ordered_merchandise", "注文商品を倉庫で没収処分する")],
            "process_same_day_order_dispatch", "schedule_next_day_order_dispatch"
        ),
        (
            "役員フロア来訪アポイント",
            "本社セキュリティ規定：秘書課への事前来訪登録がある面談客のみ役員フロアへ案内する。未登録の飛び込み来訪者は1階ロビーで待機させる。",
            "受付照会：秘書課アポイント名簿に企業名および氏名登録あり。",
            "受付照会：事前登録なしの飛び込み営業来訪。",
            [("escort_to_executive_suite", "事前登録確認により役員応接フロアへご案内する"), ("hold_at_ground_lobby_waiting", "事前登録なしのため1階ロビーでの待機を要請する"), ("call_riot_police_immediately", "警備機動隊を即時出動要請する")],
            "escort_to_executive_suite", "hold_at_ground_lobby_waiting"
        ),
        (
            "血液検体遠心分離時間",
            "生化学検査手順：採血完了から30分以内に遠心分離処理を開始した検体は検査有効とする。30分を超過放置した検体は再採血を依頼する。",
            "検体経過時間：採血後18分で検査室受領・遠心分離開始。",
            "検体経過時間：採血後55分経過（搬送遅延）。",
            [("proceed_with_blood_sample_testing", "規定時間内を確認し遠心分離および生化学検査を実行する"), ("request_patient_blood_redraw", "時間超過放置のため検体無効とし再採血を依頼する"), ("drink_blood_sample_in_lab", "検査技師が検体を直接飲み干す")],
            "proceed_with_blood_sample_testing", "request_patient_blood_redraw"
        ),
    ]

    fillers_start = [
        "先週末のサッカー観戦チケットは前売りで即日完売しました。駐車場には電気自動車用の充電器が4台設置されています。",
        "近所の公園の桜のつぼみが膨らみ始めました。今週の社内メールマガジンの担当は新入社員の鈴木さんです。",
        "社員食堂の割り箸が間伐材利用のエコ箸に切り替わりました。会議室のホワイトボードマーカーを補充しました。",
        "今朝の通勤電車はダイヤ通り定時運行でした。郵便受けに地元商店街のチラシが投函されていました。",
        "オフィスの加湿器に水を補給しました。社内チャットツールの通知設定を更新しました。",
        "昨日は部署内の月次定例報告会が実施されました。エレベーターホールの照明が省エネLEDに交換されました。",
    ]

    fillers_end = [
        "オフィスの観葉植物に水をやりました。明日の会議室予約を確認しました。",
        "春の陽気が心地よい季節です。来期の営業目標が発表されました。",
        "外は心地よい風が吹いています。デスクの書類整理を行いました。",
        "明日は晴れのち曇りの予報です。今週末は地域の清掃活動があります。",
        "コーヒーメーカーの清掃が完了しました。午後からの業務に集中します。",
        "来週の出張旅費の申請書を作成しました。夕方の気温は15度でした。",
    ]

    for idx, (title, rule, s1, s2, c_defs, t1, t2) in enumerate(surround_templates):
        choices = make_choices(c_defs)
        for rep in range(6):
            gid = f"tb_pert_sur_{idx*6 + rep + 1:03d}"
            f_s = fillers_start[rep % len(fillers_start)]
            f_e = fillers_end[rep % len(fillers_end)]
            if rep % 2 == 0:
                ctx1 = f"{f_s} {rule} {s1} {f_e}"
                ctx2 = f"{f_s} {rule} {s2} {f_e}"
            else:
                ctx1 = f"{f_s} {s1} {rule} {f_e}"
                ctx2 = f"{f_s} {s2} {rule} {f_e}"
            q = f"実務判定：{title}の規程に基づき適切な判断を選択してください。"
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "perturbation_invariance", "subdomain": "surrounding_discourse_noise", "context": ctx1, "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t1}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "perturbation_invariance", "subdomain": "surrounding_discourse_noise", "context": ctx2, "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t2}})

    # Category 8: Dual Clause Threshold Boundaries (60 pairs = 120 records)
    dual_threshold_templates = [
        (
            "割引クーポン適用判定",
            "割引クーポン適用ルール：合計購入金額が5,000円以上の会計に限り1,000円割引を適用します。5,000円未満の会計には適用できません。",
            "レジの合計金額は6,200円です。",
            "レジの合計金額は3,800円です。",
            [("apply_1000_yen_discount", "金額条件充足のため1,000円割引を適用する"), ("deny_coupon_discount_under_limit", "5,000円未満のためクーポン適用不可とする"), ("double_the_total_bill", "請求金額を勝手に2倍にする")],
            "apply_1000_yen_discount", "deny_coupon_discount_under_limit"
        ),
        (
            "遊具スライダー利用基準",
            "プール利用基準：身長120cm以上の児童に限りウォータースライダーの利用を許可します。120cm未満の児童は利用できません。",
            "身長測定結果は125cmでした。",
            "身長測定結果は112cmでした。",
            [("permit_waterslide_entry", "身長120cm以上を確認しスライダー利用を許可"), ("deny_waterslide_entry_under_height", "身長基準未達のためスライダー利用をお断りする"), ("drain_entire_swimming_pool", "プールの水をすべて排水する")],
            "permit_waterslide_entry", "deny_waterslide_entry_under_height"
        ),
        (
            "駐車場料金優遇制度",
            "駐車場料金優遇制度：館内レシート合算が3,000円以上のお客様に2時間無料駐車券を交付します。未達のお客様は通常時間料金となります。",
            "持参レシート合計額は4,800円です。",
            "持参レシート合計額は1,200円です。",
            [("grant_2_hour_free_parking_ticket", "合算3,000円以上のため2時間無料駐車券を交付"), ("charge_standard_hourly_parking_rate", "基準未達のため無料券交付なし通常料金を適用"), ("crush_vehicle_with_bulldozer", "ブルドーザーで自家用車を踏み潰す")],
            "grant_2_hour_free_parking_ticket", "charge_standard_hourly_parking_rate"
        ),
        (
            "機密ファイル印刷制御",
            "機密ファイル印刷制御：アクセス権限が機密レベルA以上のユーザーに限り印刷出力を許可します。レベルB以下のユーザーの印刷要求はブロックされます。",
            "操作ユーザーの権限は機密レベルA（最高特権）です。",
            "操作ユーザーの権限は機密レベルC（一般）です。",
            [("allow_secure_print_job", "権限レベルA以上のため印刷ジョブを実行する"), ("block_print_job_insufficient_privilege", "権限不足のため印刷ジョブをブロック拒否する"), ("smash_printer_with_crowbar", "バールで複合機を叩き割る")],
            "allow_secure_print_job", "block_print_job_insufficient_privilege"
        ),
        (
            "備品勘定科目記帳",
            "経費計上基準：1個あたりの取得価額が10万円未満の消耗品は即時費用処理する。10万円以上の資産は固定資産計上する。",
            "購入した事務用シュレッダーは単価38,000円。",
            "購入した高性能サーバーは単価350,000円。",
            [("expense_immediately_as_supplies", "10万円未満のため消耗品費として即時費用処理"), ("capitalize_as_fixed_asset", "10万円以上のため固定資産として資産計上する"), ("hide_invoices_under_carpet", "領収書をカーペットの下に隠す")],
            "expense_immediately_as_supplies", "capitalize_as_fixed_asset"
        ),
        (
            "無担保カードローン審査",
            "貸出審査基準：信用スコアが650点以上の申込者に限り無担保カードローンの即時融資を実行する。650点未満の申込者は追加書類提出による二次審査とする。",
            "申込者のスコアは710点。",
            "申込者のスコアは590点。",
            [("execute_instant_loan_disbursement", "スコア650点以上のため即時融資を実行する"), ("route_to_secondary_review_docs", "スコア未達のため追加書類提出の二次審査へ回す"), ("kidnap_applicant_guarantor", "申込者の連帯保証人を拉致監禁する")],
            "execute_instant_loan_disbursement", "route_to_secondary_review_docs"
        ),
        (
            "返品返金受付手段",
            "返金処理規定：購入レシートがある場合、全額現金で返金します。レシートがない場合は店舗ポイントでの返還となります。",
            "お客様は購入時のレシートを持参されました。",
            "お客様はレシートを紛失され手元にありません。",
            [("refund_in_cash_full", "購入レシートに基づき全額現金で返金する"), ("refund_in_store_points", "レシート紛失のため店舗ポイントで返還する"), ("confiscate_customer_wallet", "顧客の財布を没収する")],
            "refund_in_cash_full", "refund_in_store_points"
        ),
        (
            "就業時間残業手当",
            "割増賃金算定規則：実労働時間が1日8時間を超過した時間分について時間外割増手当を支給する。8時間以下の労働は所定内給与のみ支給とする。",
            "本日のタイムカード記録：実労働時間9時間30分（1時間30分超過）。",
            "本日のタイムカード記録：実労働時間7時間15分（8時間以内）。",
            [("pay_overtime_premium_allowance", "8時間超過を確認し時間外割増手当を支給する"), ("pay_regular_wage_only_standard", "8時間以内のため所定内通常給与のみ支給する"), ("withhold_entire_monthly_salary", "当月の全給与の支払いを拒絶する")],
            "pay_overtime_premium_allowance", "pay_regular_wage_only_standard"
        ),
        (
            "高速モバイル通信制御",
            "ネットワーク帯域管理：当月のデータ使用量が30GB以下であれば高速4G/5G通信を維持する。30GBを超過した回線は月末まで128kbpsに速度制限する。",
            "当月データ通信実績：現在18.4GB利用（30GB以内）。",
            "当月データ通信実績：現在38.2GB利用（30GB超過）。",
            [("maintain_full_speed_connection", "通信量上限内のため高速通信をそのまま維持する"), ("throttle_to_128kbps_speed_limit", "30GB超過検知により月末まで128kbpsに帯域制限する"), ("permanently_terminate_contract", "通信回線契約を予告なく即時強制解約する")],
            "maintain_full_speed_connection", "throttle_to_128kbps_speed_limit"
        ),
        (
            "国際線預入手荷物料金",
            "受託手荷物重量規定：荷物1個の重量が23.0kg以下であれば無料で預託を受け入れる。23.0kgを超過した手荷物は超過手荷物料金5,000円を徴収する。",
            "チェックインカウンター計量：荷物重量19.5kg（基準内）。",
            "チェックインカウンター計量：荷物重量27.8kg（超過）。",
            [("accept_checked_bag_free_of_charge", "23kg以下を確認し無料手荷物として預かる"), ("levy_excess_baggage_charge_5000", "重量超過のため超過料金5,000円を徴収する"), ("toss_baggage_into_ocean_trench", "旅客手荷物を深海海溝へ投棄する")],
            "accept_checked_bag_free_of_charge", "levy_excess_baggage_charge_5000"
        ),
    ]

    for idx, (title, rule, s1, s2, c_defs, t1, t2) in enumerate(dual_threshold_templates):
        choices = make_choices(c_defs)
        for rep in range(6):
            gid = f"tb_pert_thr_{idx*6 + rep + 1:03d}"
            if rep % 2 == 0:
                ctx1 = f"{rule} 現況：{s1}"
                ctx2 = f"{rule} 現況：{s2}"
            else:
                ctx1 = f"現況：{s1} なお、{rule}"
                ctx2 = f"現況：{s2} なお、{rule}"
            q = f"判定選定：{title}に従い適切な措置を選択してください。"
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "perturbation_invariance", "subdomain": "dual_clause_threshold_boundary", "context": ctx1, "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t1}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "perturbation_invariance", "subdomain": "dual_clause_threshold_boundary", "context": ctx2, "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t2}})

    # Category 9: Unmet Parenthetical Trap Rejection (60 pairs = 120 records)
    unmet_trap_scenarios = [
        (
            "タクシー代経費精算",
            "経費精算内規：タクシー利用は原則禁止（注：終電後の帰宅または緊急の患者搬送を要する場合を除く）。",
            "精算理由：深夜24時半を過ぎ終電電車がすでになかったため。",
            "精算理由：朝の通勤電車が混雑していて疲れていたため。",
            [("approve_taxi_fare_missed_last_train", "終電喪失の例外事由に該当するため経費承認する"), ("reject_taxi_fare_unjustified", "私的理由であり例外規定外のため経費精算を却下"), ("slash_all_taxi_tires", "街中のタクシーのタイヤをパンクさせる")],
            "approve_taxi_fare_missed_last_train", "reject_taxi_fare_unjustified"
        ),
        (
            "空港VIPラウンジ同伴者",
            "会員制ラウンジ利用規約：同伴者の入場は1名まで無料［特記事項：VIPゴールド会員に限り同伴者3名まで無料入場可能］。",
            "利用者のステータス：VIPゴールド会員。同伴者人数：2名。",
            "利用者のステータス：レギュラー会員。同伴者人数：2名。",
            [("allow_all_companions_under_gold_rule", "ゴールド会員特則適用により同伴者2名の入場許可"), ("charge_extra_fee_for_excess_companion", "一般会員枠超過のため追加同伴者料金を徴収する"), ("eject_guests_into_volcano", "利用客を火山噴火口へ投げ落とす")],
            "allow_all_companions_under_gold_rule", "charge_extra_fee_for_excess_companion"
        ),
        (
            "航空機液体物持込制限",
            "手荷物機内持込規則：液体物の持ち込みは1容器あたり100ml以下に制限する（※乳幼児同伴時の離乳食および処方箋医薬品はこの限りではない）。",
            "持ち込み品：医師処方のインスリン注射薬250ml。",
            "持ち込み品：市販の美容液化粧水200ml。",
            [("permit_prescription_medicine_liquids", "処方箋医薬品の例外適用により持込を許可する"), ("confiscate_liquids_over_100ml", "100ml超過かつ例外非該当のため保安検査で没収"), ("drink_entire_airplane_fuel_supply", "航空機のジェット燃料をすべて飲み干す")],
            "permit_prescription_medicine_liquids", "confiscate_liquids_over_100ml"
        ),
        (
            "休日夜間入館許可",
            "全社防犯規定：休日の深夜帯入館は原則禁止とする（ただし事前に役員決裁を得たシステム障害対応要員を除く）。",
            "入館理由：基幹DB停止に伴う緊急復旧作業、役員事前決裁承認書あり。",
            "入館理由：翌週提出の社内報記事を静かなオフィスで執筆するため、決裁なし。",
            [("permit_emergency_night_entry_approved", "役員決裁確認により障害対応要員の夜間入館を許可する"), ("block_night_entry_lacking_approval", "決裁なき私的残業のため入館を不許可とし退館させる"), ("call_demolition_crew_on_office", "解体業者を呼んで社屋を取り壊す")],
            "permit_emergency_night_entry_approved", "block_night_entry_lacking_approval"
        ),
        (
            "高速道路緊急路肩停車",
            "道路交通法運用：高速道路の路肩停車は原則禁止［特例：車両故障・事故等で運転継続不能な緊急事態を除く］。",
            "停車状況：エンジンのオーバーヒート白煙発生により走行不能。",
            "停車状況：後部座席でスマートフォンを操作しゲームをしたかったため。",
            [("permit_shoulder_stop_breakdown", "車両故障による緊急事態のため路肩停車を認める"), ("penalize_illegal_shoulder_stop", "私的理由による違法路肩停車のため違反取締を行う"), ("push_car_into_incoming_traffic", "停車車両を対向車線へ突き飛ばす")],
            "permit_shoulder_stop_breakdown", "penalize_illegal_shoulder_stop"
        ),
        (
            "宿泊予約直前取消料",
            "ホテル宿泊約款：宿泊前日以降のキャンセルは取消料100%を収受する（※自然災害等による交通機関の運休証明書提出時は全額免除）。",
            "取消申告：台風直撃により乗車予定の特急列車が終日計画運休（証明書あり）。",
            "取消申告：個人的な所用が長引き行くのが面倒になったため（運休なし）。",
            [("waive_cancellation_fee_with_certificate", "運休証明書確認により取消手数料を全額免除とする"), ("charge_100pct_cancellation_penalty", "私的事情のため約款通り100%の取消料を請求する"), ("liquidate_guest_bank_holdings", "宿泊客の金融資産を全額没収する")],
            "waive_cancellation_fee_with_certificate", "charge_100pct_cancellation_penalty"
        ),
        (
            "特別指定席無料変更",
            "座席予約規定：発券完了後の指定席変更は変更手数料500円を申し受ける［特則：列車の遅延が30分以上発生した場合に限り無料変更可能］。",
            "運行状況：踏切事故により接続予定列車に45分の遅延発生中。",
            "運行状況：列車は定時運行中、窓側席から通路側席へ移りたい顧客希望。",
            [("change_seat_free_of_charge_delayed", "30分以上遅延のため特則に基づき無手数料で席を変更する"), ("levy_500_yen_change_fee_normal", "定時運行時の自己都合変更のため手数料500円を徴収する"), ("derail_all_bullet_trains", "すべての新幹線を故意に脱線させる")],
            "change_seat_free_of_charge_delayed", "levy_500_yen_change_fee_normal"
        ),
        (
            "社用車私的目的貸出",
            "車両管理内規：業務目的以外の社用車運転は一切禁止する（注：災害時の帰宅困難者緊急搬送支援を命じられた場合を除く）。",
            "利用申請：震度6地震による公共交通全面麻痺時の帰宅困難避難者送迎支援。",
            "利用申請：週末に家族で近郊アウトレットモールへ買い物に行くため。",
            [("authorize_emergency_vehicle_dispatch", "災害時緊急支援任務のため社用車出動を許可する"), ("forbid_private_vehicle_use_strictly", "私用目的のため規程違反として貸出を固く拒絶する"), ("set_fire_to_parking_garage", "社用車駐車場に放火する")],
            "authorize_emergency_vehicle_dispatch", "forbid_private_vehicle_use_strictly"
        ),
        (
            "図書館特別貴重書閲覧",
            "貴重書保存規程：貴重古文書の原本出納は厳禁とする［例外：大学教授発行の推薦研究書を所持する学術調査員を除く］。",
            "申請者：国立大学文学部教授の公印入り推薦書を所持する研究者。",
            "申請者：趣味の歴史愛好家で推薦書なし（身分証のみ提示）。",
            [("grant_rare_manuscript_inspection", "大学教授の推薦書確認により原本出納閲覧を認める"), ("deny_inspection_lacking_recommendation", "推薦書なしのため原本閲覧を不可とし複製版を案内する"), ("burn_historical_archives_to_ashes", "歴史的古文書をすべて焼却処分する")],
            "grant_rare_manuscript_inspection", "deny_inspection_lacking_recommendation"
        ),
        (
            "定期健診当日再検査",
            "健診受診基準：精密再検査は別日予約を原則とする（※受診値が緊急危険域収縮期血圧180mmHg以上を示した場合は当日即時対応）。",
            "測定値：血圧測定結果195mmHg（緊急危険域到達）。",
            "測定値：血圧測定結果138mmHg（軽度高値、緊急域未満）。",
            [("order_immediate_same_day_examination", "緊急危険域当確のため当日の緊急再検査を実施する"), ("schedule_regular_followup_appointment", "通常予約枠での後日精密再検査を案内予約する"), ("bury_patient_alive", "患者を生きたまま地中に埋める")],
            "order_immediate_same_day_examination", "schedule_regular_followup_appointment"
        ),
    ]

    for idx, (title, rule, s1, s2, c_defs, t1, t2) in enumerate(unmet_trap_scenarios):
        choices = make_choices(c_defs)
        for rep in range(6):
            gid = f"tb_pert_trp_{idx*6 + rep + 1:03d}"
            if rep % 2 == 0:
                ctx1 = f"{rule} 申請確認：{s1}"
                ctx2 = f"{rule} 申請確認：{s2}"
            else:
                ctx1 = f"申請確認：{s1} 【適用規程】{rule}"
                ctx2 = f"申請確認：{s2} 【適用規程】{rule}"
            q = f"審査判定：{title}の内規に基づき適切な判断を選択してください。"
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "perturbation_invariance", "subdomain": "unmet_parenthetical_trap_rejection", "context": ctx1, "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t1}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "perturbation_invariance", "subdomain": "unmet_parenthetical_trap_rejection", "context": ctx2, "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t2}})

    return records


if __name__ == "__main__":
    records = generate_perturbation_stream_b()
    print(f"Generated {len(records)} perturbation records ({len(records)//2} pairs).")
    gids = set(r["group_id"] for r in records)
    print(f"Unique groups: {len(gids)}")

