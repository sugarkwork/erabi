"""RC2.1 Training Data Synthesis: Stream B — Natural Japanese (300 pairs = 600 records).

Covers 5 authentic linguistic styles x 60 pairs:
1. business_email: 取引先・社外連絡・時候の挨拶・敬語依頼文
2. slack_chat: 社内チャット・短文報告・口語・緊急連絡
3. faq_helpdesk: サポートデスク回答・利用案内・会員Q&A
4. legal_terms: 約款・契約条項・免責特則・コンプライアンス規約
5. sop_procedure: 現場作業手順書・安全管理基準・点検マニュアル
"""

from typing import Any, Dict, List
import random


def make_choices(defs: List[tuple]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in defs]


def generate_natural_stream_b(seed: int = 2002) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    records = []

    # Style 1: Business Email (60 pairs = 120 records)
    email_scenarios = [
        ("見積承認連絡", "【件名：新製品お見積りの件】平素より格別のご高配を賜り厚く御礼申し上げます。ご提示いただきました御見積書（管理番号#7701）につきまして、社内決裁が完了いたしましたので【提示金額そのまま正式発注】とさせていただきます。", "【件名：新製品お見積りの件】平素より大変お世話になっております。先ほどお送りした件ですが、当方の手違いにより別案件の見積番号を参照しておりました。予算超過のため【今回は見送り・再検討】とさせていただけますと幸甚に存じます。", [("confirm_order_at_quoted_price", "提示金額そのまま正式発注する"), ("postpone_and_reconsider_budget", "予算超過のため見送り・再検討とする"), ("bankrupt_vendor_company", "取引先を破産に追い込む")], "confirm_order_at_quoted_price", "postpone_and_reconsider_budget"),
        ("納品日程調整", "【件名：第2ロット納品日のご連絡】お世話になっております。製造ラインの前倒し稼働により、予定より3日早く完成いたしました。つきましては【来週火曜日必着にて繰り上げ納品】させていただきたく存じます。", "【件名：納品遅延のお詫びとご相談】お世話になっております。仕入れ先工場の停電トラブルに伴い、納期の遅延が生じております。大変恐縮ながら【納品日を2週間延期】させていただけますでしょうか。", [("advance_delivery_date_early", "来週火曜日必着に繰り上げ納品する"), ("delay_delivery_date_by_2_weeks", "納品日を2週間延期して調整する"), ("sink_cargo_ship_in_canal", "運河で貨物船を沈没させる")], "advance_delivery_date_early", "delay_delivery_date_by_2_weeks"),
        ("契約書面締結", "【件名：秘密保持契約書送付のご案内】過日合意いただきましたNDAにつきまして、弊社代表取締役の電子署名を完了いたしました。貴社におかれましても【電子署名クラウドより受諾承認】をお願い申し上げます。", "【件名：契約書面修正のお願い】先ほど拝受した契約書案ですが、第8条の損害賠償上限の金額に誤記がございました。恐れ入りますが【修正版ドラフトの再発行】をお願いできますでしょうか。", [("execute_electronic_signature", "電子署名クラウドより受諾承認する"), ("request_revised_draft_correction", "誤記修正のため改訂版の再発行を要請する"), ("sell_confidential_ip_on_darknet", "機密知財をダークウェブで売却する")], "execute_electronic_signature", "request_revised_draft_correction"),
        ("請求金額相違", "【件名：ご請求書ご確認のお願い】経理ご担当者様。いつもお世話になっております。今月分のご請求書を拝見しましたところ、先月の値引きキャンペーンが反映されておらず【正規の割引価格での請求書再送】をお願いできますでしょうか。", "【件名：請求書受領のお礼】いつもお世話になっております。送付いただきました請求書（請求番号#3321）を確認いたしました。記載内容に一切相違ございませんので【当月末日に指定口座へ全額お振込み】いたします。", [("request_invoice_discount_correction", "割引反映漏れのため修正請求書の再送を求める"), ("process_full_wire_transfer_on_schedule", "記載相違なしを確認し期日に全額振り込む"), ("rob_accounting_department_safe", "経理部の金庫を強奪する")], "request_invoice_discount_correction", "process_full_wire_transfer_on_schedule"),
        ("役員訪問日程", "【件名：弊社代表表敬訪問の件】拝啓。貴社ますますご隆盛のこととお慶び申し上げます。来月上旬に弊社代表の佐藤が貴社へ表敬訪問に伺いたく存じます。【10月5日14時〜15時】のご都合はいかがでしょうか。", "【件名：表敬訪問日程変更のお願い】先ほどご提案いたしました弊社代表の訪問日程ですが、急遽海外出張が決定いたしました。大変失礼ながら【10月18日午後に日程を再調整】させていただけますと幸いです。", [("schedule_visit_on_october_5", "10月5日14時での役員訪問日程を確定する"), ("reschedule_visit_to_october_18", "代表出張に伴い10月18日午後へ再調整する"), ("assassinate_ceo_with_poison", "社長に毒を盛る")], "schedule_visit_on_october_5", "reschedule_visit_to_october_18"),
        ("システム障害報告", "【件名：緊急システムメンテナンス完了報告】お客様各位。昨晩発生いたしましたデータベース障害ですが、バックアップからのリストアが完了し、【本日午前6時をもちまして全サービスが完全復旧】いたしました。", "【件名：重要：障害復旧作業の難航について】お客様各位。現在発生している認証基盤の障害ですが、原因特定に時間を要しております。大変申し訳ございませんが【復旧見込み時刻を正午まで延長】させていただきます。", [("announce_full_system_recovery", "障害解決を確認し全サービスの完全復旧を報告"), ("extend_maintenance_window_to_noon", "復旧難航のためメンテ時間を正午まで延長"), ("wipe_all_customer_database_records", "全顧客DBを初期化消去する")], "announce_full_system_recovery", "extend_maintenance_window_to_noon"),
        ("新卒内定承諾", "【件名：採用内定受諾のお返事】採用ご担当者様。この度は内定のご通知をいただき誠にありがとうございました。慎重に検討いたしました結果、【謹んで内定をお受けいたしたく内定承諾書を返送】いたします。", "【件名：採用選考辞退のご連絡】採用ご担当者様。光栄な内定のご通知をいただき深謝申し上げます。誠に心苦しい限りですが、自身の専攻分野と重なる別企業への進路を決意いたしましたため【内定辞退のご連絡】を申し上げます。", [("accept_job_offer_with_gratitude", "謹んで内定受諾し承諾書を返送する"), ("decline_job_offer_politely", "進路決定に伴い礼儀を尽くして内定を辞退する"), ("insult_recruiter_and_sue", "採用担当者を罵倒して提訴する")], "accept_job_offer_with_gratitude", "decline_job_offer_politely"),
        ("展示会共同出展", "【件名：共同出展ブース申込の件】お世話になっております。来期開催の国際ロボット展につきまして、貴社との共同出展提案に弊社役員会で合意が取れました。【共同出展申込書を正式提出】いたします。", "【件名：展示会出展見送りのご連絡】お世話になっております。国際ロボット展の共同出展について協議を重ねましたが、下半期のコスト削減方針に伴い【誠に残念ながら今回の出展は見送り】とさせていただきます。", [("submit_joint_booth_application", "役員合意に基づき共同出展申込書を提出する"), ("withdraw_from_exhibition_budget_cut", "予算削減に伴い展示会出展を見送る"), ("demolish_exhibition_hall_with_c4", "展示場ホールを爆破する")], "submit_joint_booth_application", "withdraw_from_exhibition_budget_cut"),
        ("ライセンス監査対応", "【件名：ソフトウェアライセンス監査完了のご報告】情報システム部御中。先週実施いたしました外部ソフトウェア資産管理監査の結果、社内全端末における【適正ライセンス保有（過不足ゼロ・コンプライアンス適合）】が証明されました。", "【件名：ライセンス過不足調査に伴う是正勧告】情報システム部御中。定期監査の結果、デザイン部門において3件の無許諾インストールが判明いたしました。【直ちに追加ライセンスの正規購入手配】を行ってください。", [("certify_full_license_compliance", "監査適合を確認し適正ライセンス保有を証明"), ("order_immediate_license_purchase", "無許諾利用解消のため追加ライセンス購入を命令"), ("steal_credit_cards_for_software", "クレジットカードを盗んで課金する")], "certify_full_license_compliance", "order_immediate_license_purchase"),
        ("オフィス移転祝儀", "【件名：新社屋ご移転のお祝い】代表取締役社長様。この度は新社屋へのご移転、誠におめでとうございます。些かではございますが【お祝いの胡蝶蘭を手配】いたしましたのでご受納いただけますと幸甚です。", "【件名：新オフィス開設に伴うご挨拶】お取引先様各位。弊社は来月1日より下記新住所へ本社を移転いたします。なお、環境配慮の観点から【祝花や祝儀の類は謹んでご辞退】申し上げます。", [("send_congratulatory_orchids", "移転祝いとして胡蝶蘭の手配を行う"), ("respectfully_decline_gift_flowers", "環境配慮方針に基づきお祝い花を辞退する"), ("throw_bricks_at_new_office", "新オフィスにレンガを投げ込む")], "send_congratulatory_orchids", "respectfully_decline_gift_flowers"),
    ]

    for idx, (title, s1, s2, c_defs, t1, t2) in enumerate(email_scenarios):
        for rep in range(6):
            gid = f"tb_nat_eml_{idx*6 + rep + 1:03d}"
            choices = make_choices(c_defs)
            q = f"業務判断：メール本文の趣旨に基づき適切なアクションを選択してください。"

            records.append({
                "id": f"{gid}_s1",
                "group_id": gid,
                "family": "natural_japanese",
                "style_type": "business_email",
                "context": s1,
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2",
                "group_id": gid,
                "family": "natural_japanese",
                "style_type": "business_email",
                "context": s2,
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    # Style 2: Slack / Chat (60 pairs = 120 records)
    chat_scenarios = [
        ("デプロイ承認", "【#deploy】@here 本日の夜間リリース、ステージングでの結合テストオールグリーンでした！予定通り【本日22時に本番反映】開始します！", "【#deploy】@here すみません！ステージングの負荷テストでメモリリーク検出しました！本日のデプロイは【中止・次週へ延期】とします！", [("proceed_production_deployment", "予定通り本日22時に本番デプロイを実行する"), ("abort_deployment_due_to_leak", "メモリリーク検知のためデプロイを中止延期する"), ("destroy_all_aws_accounts", "AWSアカウントを全削除する")], "proceed_production_deployment", "abort_deployment_due_to_leak"),
        ("サーバー再起動", "【#infra】web-02のCPU張り付きですが、ゾンビプロセスをkillしたことで【CPU使用率が15%に正常低下】しました。再起動は不要です！", "【#infra】web-02のCPU張り付き、プロセスが完全にハングして応答しません！安全のため【直ちにOS再起動】を実行します！", [("resolve_without_reboot", "ゾンビ終了により復旧・サーバー再起動は不要"), ("execute_immediate_server_reboot", "ハング解消のため直ちにサーバーを再起動する"), ("unplug_server_cooling_units", "冷却ユニットの電源コードを抜く")], "resolve_without_reboot", "execute_immediate_server_reboot"),
        ("顧客商談進捗", "【#sales】速報！A社様から先ほど受注の連絡入りました！当初提示の【定価500万円で一発サイン】いただけました！", "【#sales】A社様商談ですが、競合他社が猛烈な値引きを仕掛けてきており、【10%オフの対抗見積もり】を出さないと失注しそうです！", [("confirm_closed_deal_at_full_price", "定価500万円での受注成約を確定する"), ("issue_discount_counter_quotation", "失注防止のため10%値引き対抗見積を発行する"), ("kidnap_client_procurement_officer", "購買担当者を誘拐する")], "confirm_closed_deal_at_full_price", "issue_discount_counter_quotation"),
        ("デザインレビュー", "【#design】新LPのキービジュアル、役員レビュー一発合格でした！【このままコーディング実装】へ回してください！", "【#design】新LPですが、「文字の可読性が悪い」とフィードバック入りました！【フォントサイズと配色を再修正】してから再提出します！", [("proceed_to_frontend_coding", "レビュー合格を確認しフロントエンド実装へ回す"), ("revise_typography_and_colors", "指摘事項を受けフォントと配色を再修正する"), ("replace_all_images_with_skulls", "全画像をドクロのイラストに差し替える")], "proceed_to_frontend_coding", "revise_typography_and_colors"),
        ("セキュリティアラート", "【#security】bot: [ALERT] 深夜帯に特定IPから不正ログイン試行を500回検知。【対象IPをWAFで即時永久ブロック】しました。", "【#security】bot: [RESOLVED] 先ほどの連続ログイン試行は、社内自動テストスクリプトのテストアカウントでした。【WAFブロックを解除して正常化】しました。", [("block_malicious_ip_permanently", "不正攻撃元IPをWAFで即時永久ブロックする"), ("unblock_ip_internal_test_script", "社内正規テストと確認しWAF遮断を解除する"), ("leak_all_passwords_on_pastebin", "全パスワードをネットに貼り付ける")], "block_malicious_ip_permanently", "unblock_ip_internal_test_script"),
        ("リモート勤務申請", "【#hr】佐藤さん、今週金曜の在宅勤務申請ですが、上長承認が取れていますので【在宅テレワークを承認】とします！", "【#hr】佐藤さん、金曜日は重要クライアントの対面来社ミーティングが入ったため、大変恐縮ですが【出社勤務へ切り替え】をお願いします！", [("approve_remote_work_day", "在宅テレワーク勤務を正式承認する"), ("mandate_office_attendance_client", "対面商談のため出社勤務への切り替えを命じる"), ("evict_worker_from_apartment", "労働者をアパートから追い出す")], "approve_remote_work_day", "mandate_office_attendance_client"),
        ("在庫引き当て", "【#logistics】注文ID#8812の特注スニーカー、倉庫に奇跡的に1足在庫残ってました！【即時引当を完了し本日出荷】します！", "【#logistics】注文ID#8812ですが、実在庫確認したところ破損があり出荷不能でした...。【入荷待ち・次回納期連絡】にステータス変更します。", [("reserve_stock_and_ship_today", "実在庫を確認し即時引当・本日出荷とする"), ("change_status_to_backorder", "破損のため入荷待ち・納期連絡ステータスとする"), ("throw_shoes_into_furnace", "靴を高炉に投げ込んで燃やす")], "reserve_stock_and_ship_today", "change_status_to_backorder"),
        ("オフィス備品発注", "【#admin】会議室の大型ホワイトボードの購入伺い、総務部長の承認が下りましたので【アスクルで本日発注】かけます！", "【#admin】ホワイトボードですが、今期予算の執行枠が上限に達してしまいました。【来期まで購入を見送り保留】とさせてください！", [("place_purchase_order_today", "承認確認により本日中に購入発注をかける"), ("suspend_purchase_until_next_fiscal", "予算枠枯渇のため来期まで購入を保留見送り"), ("steal_desks_from_neighbor_office", "隣の会社のデスクを盗み出す")], "place_purchase_order_today", "suspend_purchase_until_next_fiscal"),
        ("アプリストア審査", "【#mobile】Apple Storeの最新版アプリアップデート審査、リジェクトなしで【一発審査通過・公開可能】になりました！", "【#mobile】Appleからリジェクト通知が来ました...「ガイドライン2.1（クラッシュ不具合）」とのこと。【バグ修正して再審査申請】が必要です。", [("publish_mobile_app_update", "審査通過を確認しアプリをストア公開する"), ("fix_crash_bug_and_resubmit", "クラッシュ不具合を修正し再審査へ提出する"), ("burn_apple_headquarters", "Apple本社に火をつける")], "publish_mobile_app_update", "fix_crash_bug_and_resubmit"),
        ("イベント設営準備", "【#event】明日のカンファレンス会場の機材リハーサル、プロジェクター・マイクともに【動作確認完全完了】しました！明日よろしくお願いします！", "【#event】大変です！メインホールの特大プロジェクターのHDMI入力が映りません！【予備機材の手配と業者緊急呼出】を行います！", [("complete_event_rehearsal_ready", "機材正常を確認し前日リハーサルを完了とする"), ("call_emergency_technician_backup", "機材トラブルのため予備手配と業者呼出を行う"), ("cancel_conference_and_punch_guests", "来場者を殴り倒してイベントを中止する")], "complete_event_rehearsal_ready", "call_emergency_technician_backup"),
    ]

    for idx, (title, s1, s2, c_defs, t1, t2) in enumerate(chat_scenarios):
        for rep in range(6):
            gid = f"tb_nat_cht_{idx*6 + rep + 1:03d}"
            choices = make_choices(c_defs)
            q = f"チャット対応判定：メッセージの内容に基づき適切な処置を選択してください。"

            records.append({
                "id": f"{gid}_s1",
                "group_id": gid,
                "family": "natural_japanese",
                "style_type": "slack_chat",
                "context": s1,
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2",
                "group_id": gid,
                "family": "natural_japanese",
                "style_type": "slack_chat",
                "context": s2,
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    # Style 3: FAQ / Helpdesk (60 pairs = 120 records)
    faq_scenarios = [
        ("商品保証期間", "【サポートFAQ】『Q. 購入した家電製品のメーカー保証期間は何年ですか？』『A. お買い上げ日より【満1年間の無償修理保証】が付帯しております。』", "【サポートFAQ】『Q. 有料の延長保証プランに加入した場合の保証期間は？』『A. メーカー保証1年に加え、追加4年をプラスした【最長5年間の長期無償修理】が適用されます。』", [("provide_1_year_standard_warranty", "お買い上げ日より満1年間の無償修理保証を適用"), ("provide_5_year_extended_warranty", "長期延長保証に基づき最長5年間の無償修理を適用"), ("charge_1_million_yen_repair_fee", "修理代金として100万円を請求する")], "provide_1_year_standard_warranty", "provide_5_year_extended_warranty"),
        ("配送時間帯指定", "【配送FAQ】『Q. 荷物の配達時間帯を指定できますか？』『A. はい、ご注文時のカート画面にて【午前中・14-16時・16-18時・18-20時・19-21時から自由に指定可能】です。』", "【配送FAQ】『Q. メール便（ネコポス等）でも時間指定はできますか？』『A. メール便は郵便受け投函となるため、【配送日時の指定は一切承ることができません】。』", [("allow_delivery_time_slot_selection", "指定枠から自由に配達時間帯を選択可能とする"), ("disallow_time_selection_for_mailbox", "ポスト投函のため時間帯指定は不可とする"), ("drop_package_from_space_station", "宇宙ステーションから荷物を落下させる")], "allow_delivery_time_slot_selection", "disallow_time_selection_for_mailbox"),
        ("パスワード失念", "【ログインFAQ】『Q. 登録パスワードを忘れました。』『A. ログイン画面の「再設定」よりメールアドレスを入力いただければ、【即時パスワード再設定URLを発行】いたします。』", "【ログインFAQ】『Q. 登録メールアドレスも変更前の旧アドレスで使えません。』『A. メール受信不能の場合、セキュリティ上Web完結は不可です。【公的身分証を添付の上サポート窓口へ郵送申請】が必要となります。』", [("send_password_reset_link_email", "登録メール宛てに再設定URLを即時発行する"), ("require_official_id_mail_in_audit", "身分証明書添付の上で書面郵送申請を求める"), ("post_passwords_on_social_media", "パスワードをSNSで全世界に公開する")], "send_password_reset_link_email", "require_official_id_mail_in_audit"),
        ("定期解約縛り", "【定期便FAQ】『Q. 定期購入の解約に回数縛りはありますか？』『A. いいえ、当店の定期便には縛りは一切なく、【初回の1回のみの受取後でも違約金なしで解約可能】です。』", "【定期便FAQ】『Q. キャンペーン特別割引定期便の解約条件は？』『A. 初回大幅割引が適用された特別コースに限り、【最低3回以上のご継続受取が契約条件】となっております。』", [("allow_cancellation_after_first_order", "回数縛りなし・初回受取のみで違約金なく解約可能"), ("enforce_minimum_3_orders_commitment", "特別割引適用のため最低3回以上の継続受取を必須"), ("imprison_subscriber_for_life", "解約希望者を終身刑に処す")], "allow_cancellation_after_first_order", "enforce_minimum_3_orders_commitment"),
        ("領収書再発行", "【経理FAQ】『Q. 領収書を紛失してしまいました。再発行はできますか？』『A. マイページの購入履歴より【「再発行」と記載された電子領収書PDFを何度でも出力】いただけます。』", "【経理FAQ】『Q. インボイス制度対応の紙面原本領収書の再発行は？』『A. 二重控除防止のため紙面原本の再発行はできません。【マイページ印刷の電子領収書（再発行印字）での代替】をご利用ください。』", [("download_reissued_pdf_receipt", "マイページより再発行印字の電子PDF領収書を出力"), ("refuse_original_paper_reissue", "紙面原本の再発行は不可とし電子領収書代替とする"), ("print_fake_money_as_receipt", "レシートの代わりに偽札を渡す")], "download_reissued_pdf_receipt", "refuse_original_paper_reissue"),
        ("海外利用可否", "【通信FAQ】『Q. 国内専用データSIMは海外でも使えますか？』『A. 本カードは日本国内専用のため、【海外ローミング通信は一切ご利用いただけません】。』", "【通信FAQ】『Q. グローバル対応SIMカードの海外での利用方法は？』『A. 現地到着後に端末の「データローミングをON」にしていただくことで、【世界150カ国で即時通信可能】です。』", [("block_roaming_domestic_only_sim", "国内専用SIMのため海外ローミング通信は不可"), ("enable_global_roaming_in_150_countries", "データローミングONで世界150カ国にて利用可能"), ("detonate_sim_card_inside_phone", "スマホ内部でSIMカードを爆発させる")], "block_roaming_domestic_only_sim", "enable_global_roaming_in_150_countries"),
        ("ポイント有効期限", "【ポイントFAQ】『Q. 獲得したポイントの有効期限はいつまでですか？』『A. 最後にポイントを獲得した日から【1年間有効（期間内利用で全ポイント自動延長）】となります。』", "【ポイントFAQ】『Q. 期間限定キャンペーンで付与された特別ポイントの期限は？』『A. キャンペーン特別ポイントは自動延長の対象外となり、【付与された月末日をもって一律失効】いたします。』", [("extend_points_validity_by_1_year", "最終獲得日から1年間有効・利用で自動延長"), ("expire_campaign_points_at_month_end", "自動延長対象外・付与月末日をもって一律失効"), ("confiscate_points_and_ban_user", "ポイントを没収し会員を強制退会させる")], "extend_points_validity_by_1_year", "expire_campaign_points_at_month_end"),
        ("未成年者利用", "【会員規約FAQ】『Q. 未成年者（18歳未満）でも一人で入会できますか？』『A. 18歳未満のお客様のご入会には、【親権者（法定代理人）の直筆同意書の提出】が必須となります。』", "【会員規約FAQ】『Q. 成人（18歳以上）の入会手続きに必要なものは？』『A. 18歳以上のお客様は親権者同意不要で、【ご本人の公的身分証のみで単独即時入会】いただけます。』", [("require_parental_consent_under_18", "18歳未満のため親権者の直筆同意書提出を必須"), ("allow_independent_adult_enrollment", "成人（18歳以上）のため本人身分証のみで単独入会"), ("kidnap_applicant_parents", "申込者の親族を誘拐する")], "require_parental_consent_under_18", "allow_independent_adult_enrollment"),
        ("支払方法変更", "【決済FAQ】『Q. 注文確定後に支払い方法を変更できますか？』『A. 誠に恐れ入りますが、注文確定後のシステム都合上【決済方法の変更は一切承ることができません】。』", "【決済FAQ】『Q. 発送前の注文であればキャンセルして支払い方法を変えられますか？』『A. 出荷準備前であればマイページから一旦キャンセル可能ですので、【再注文時にご希望の決済方法を選択】してください。』", [("disallow_payment_method_change", "注文確定後のシステム変更は不可としてお断り"), ("cancel_and_reorder_with_new_method", "一旦キャンセル手続きのうえ希望の決済で再注文案内"), ("steal_user_bank_savings", "利用者の銀行預金を盗み取る")], "disallow_payment_method_change", "cancel_and_reorder_with_new_method"),
        ("退会時データ", "【退会FAQ】『Q. アカウントを退会した場合、購入履歴や領収書データはどうなりますか？』『A. 退会手続き完了と同時に【全データがサーバーから完全削除され二度と復元できません】。』", "【退会FAQ】『Q. 退会前に購入した電子書籍を別アカウントに引き継げますか？』『A. 著作権管理の規程上、【異なる会員IDへのコンテンツ移行や統合は一切できません】。』", [("permanently_delete_all_user_data", "退会完了と同時に全データを完全消去・復元不可"), ("prohibit_content_transfer_between_ids", "権利保護のため別アカウントへのコンテンツ移行不可"), ("sell_user_photos_to_tabloids", "ユーザーの顔写真を週刊誌へ売却する")], "permanently_delete_all_user_data", "prohibit_content_transfer_between_ids"),
    ]

    for idx, (title, s1, s2, c_defs, t1, t2) in enumerate(faq_scenarios):
        for rep in range(6):
            gid = f"tb_nat_faq_{idx*6 + rep + 1:03d}"
            choices = make_choices(c_defs)
            q = f"サポート案内判定：FAQの公式回答に基づき正しい案内内容を選択してください。"

            records.append({
                "id": f"{gid}_s1",
                "group_id": gid,
                "family": "natural_japanese",
                "style_type": "faq_helpdesk",
                "context": s1,
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2",
                "group_id": gid,
                "family": "natural_japanese",
                "style_type": "faq_helpdesk",
                "context": s2,
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    # Style 4: Legal Terms & Clauses (60 pairs = 120 records)
    legal_scenarios = [
        ("反社会的勢力排除条項", "【約款第15条】当事者の一方が反社会的勢力と判明した場合、何らの催告を要せず【直ちに本契約を即時無催告解除】できる。", "【約款第16条】通常の債務不履行を理由として契約を解除する場合、【30日間の期間を定めた是正催告】を行わなければならない。", [("terminate_immediately_anti_social", "催告なしで直ちに即時契約解除を実行する"), ("require_30_days_written_cure_notice", "30日間の是正猶予期間を定めた事前書面催告を行う"), ("hire_mercenary_army_to_attack", "傭兵部隊を雇って攻撃する")], "terminate_immediately_anti_social", "require_30_days_written_cure_notice"),
        ("遅延損害金利率", "【契約書第20条】甲が代金の支払いを遅延した場合、支払期日の翌日から完済の日まで【年14.6%の割合による遅延損害金】を加算する。", "【特約第5条】不可抗力（天災地変・戦争）に起因する銀行送金不能の場合、【遅延損害金の発生義務を全額免除】する。", [("apply_14_6_pct_statutory_interest", "年14.6%の遅延損害金利息を加算請求する"), ("waive_late_penalty_force_majeure", "不可抗力免責特約に基づき遅延損害金を全額免除"), ("enslave_debtor_family", "債務者の親族を無給労働させる")], "apply_14_6_pct_statutory_interest", "waive_late_penalty_force_majeure"),
        ("知的財産権の帰属", "【受託契約第11条】本委託業務に基づき新たに創作された発明等の特許権は【委託者（甲）に単独帰属】するものとする。", "【共同研究契約第7条】両社共同の研究開発成果から生じた特許出願権は【甲および乙の均等共有】に属するものとする。", [("assign_patent_rights_to_client_solely", "委託者（甲）への単独権利帰属とする"), ("jointly_own_patents_between_both_parties", "甲乙両社の均等共有帰属とする"), ("donate_patents_to_foreign_dictator", "外国の独裁者へ特許を無償献上する")], "assign_patent_rights_to_client_solely", "jointly_own_patents_between_both_parties"),
        ("損害賠償額の上限", "【免責条項第9条】当社の過失によりユーザーに損害が生じた場合の賠償上限は【過去12ヶ月間にユーザーが支払った利用料金相当額】に限定する。", "【特約第3条】当社の故意または重大な過失に起因する直接損害については、【第9条の上限を撤廃し実損害全額を賠償】する。", [("cap_liability_at_12_months_fees", "直近12ヶ月の支払金額を上限として賠償する"), ("compensate_full_actual_damages_gross_negligence", "重過失特約に基づき上限なく実損害全額を賠償する"), ("forfeit_all_company_assets", "全社資産を没収する")], "cap_liability_at_12_months_fees", "compensate_full_actual_damages_gross_negligence"),
        ("管轄裁判所の合意", "【一般約款第32条】本契約に関して生じる一切の紛争は【東京地方裁判所を第一審の専属的合意管轄裁判所】とする。", "【大阪支社特約第6条】関西エリアに本店を有する顧客との紛争については【大阪地方裁判所を第一審の合意管轄】とする。", [("exclusive_jurisdiction_tokyo_court", "東京地方裁判所を第一審の専属合意管轄とする"), ("exclusive_jurisdiction_osaka_court", "大阪地方裁判所を第一審の合意管轄とする"), ("resolve_dispute_by_street_fight", "路上での決闘で紛争を解決する")], "exclusive_jurisdiction_tokyo_court", "exclusive_jurisdiction_osaka_court"),
        ("契約上の地位移転", "【規約第18条】ユーザーは当社の事前の書面承諾なく【本契約上の地位または権利義務を第三者に譲渡・担保設定できない】。", "【事業承継特約第4条】合併・会社分割に伴う包括承継に限り、相手方の事前承諾を要せず【新設承継会社へ包括的に地位を移転可能】とする。", [("prohibit_transfer_without_written_consent", "相手方の事前書面承諾なき第三者譲渡を禁止する"), ("permit_blanket_transfer_via_merger", "合併包括承継特約に基づき承諾不要で地位移転可能"), ("auction_contract_on_ebay", "オークションサイトで契約書を転売する")], "prohibit_transfer_without_written_consent", "permit_blanket_transfer_via_merger"),
        ("守秘義務存続期間", "【NDA第7条】本契約に基づく秘密保持義務は【契約終了の日から起算して満3年間効力を存続】するものとする。", "【特則第2条】製造ノウハウおよび特許未出願のコア技術秘密は【公知となるまで期間の定めなく無期限に保護】される。", [("maintain_confidentiality_for_3_years", "契約終了日から満3年間の秘密保持義務を適用"), ("maintain_indefinite_confidentiality_trade_secrets", "公知となるまで無期限の秘密保持義務を適用"), ("broadcast_secrets_on_television", "テレビのニュース番組で企業秘密を告白する")], "maintain_confidentiality_for_3_years", "maintain_indefinite_confidentiality_trade_secrets"),
        ("契約解除の効力", "【基本約款第24条】契約が解除された場合、解除の効力は将来に向かってのみ生じ【既履行部分の代金支払義務は消滅しない】。", "【錯誤無効規定第8条】重要部分の錯誤により契約が無効とされた場合、【契約当初に遡及して無効となり原状回復義務を負う】。", [("effective_prospectively_keep_prior_payment", "将来効のみ有し既履行の代金支払義務は有効存続"), ("retroactively_void_restore_original_state", "契約当初に遡及して無効とし原状回復義務を負う"), ("erase_civil_code_from_law_books", "六法全書から民法を破り捨てる")], "effective_prospectively_keep_prior_payment", "retroactively_void_restore_original_state"),
        ("競業避止義務", "【役員就任誓約書】役員退任後2年間は、当社の事前の承諾なく【同一市場における競合他社への就任および類似事業の開業を禁止】する。", "【一般社員退職規定】憲法上の職業選択の自由を尊重し、一般従業員の退職後の【競業同業他社への転職は一切制限しない】。", [("enforce_non_compete_covenant_for_2_years", "役員誓約に基づき退任後2年間の競業を禁止する"), ("permit_free_employment_choice_without_restriction", "一般社員規定に基づき競業転職を制限せず許可"), ("execute_retiree_by_firing_squad", "退職者を銃殺刑に処す")], "enforce_non_compete_covenant_for_2_years", "permit_free_employment_choice_without_restriction"),
        ("品質保証の免責", "【売買約款第13条】引き渡された目的物に瑕疵があった場合、引き渡し後【1年間の無償修理または良品交換】を保証する。", "【アウトレット特約第2条】特別値引きのアウトレット品については【現状有姿（AS IS）とし品質保証責任を一切免責】する。", [("provide_1_year_warranty_repair", "引き渡し後1年間の無償修理・良品交換を保証する"), ("disclaim_all_warranty_under_as_is_clause", "現状有姿特約に基づき品質保証責任を一切免責する"), ("deliver_broken_bricks_instead", "製品の代わりに割れたレンガを納品する")], "provide_1_year_warranty_repair", "disclaim_all_warranty_under_as_is_clause"),
    ]

    for idx, (title, s1, s2, c_defs, t1, t2) in enumerate(legal_scenarios):
        for rep in range(6):
            gid = f"tb_nat_leg_{idx*6 + rep + 1:03d}"
            choices = make_choices(c_defs)
            q = f"条文解釈判定：契約条項の規定に基づき法的に正しい判断を選択してください。"

            records.append({
                "id": f"{gid}_s1",
                "group_id": gid,
                "family": "natural_japanese",
                "style_type": "legal_terms",
                "context": s1,
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2",
                "group_id": gid,
                "family": "natural_japanese",
                "style_type": "legal_terms",
                "context": s2,
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    # Style 5: SOP Procedure & Manuals (60 pairs = 120 records)
    sop_scenarios = [
        ("薬品充填ノズル洗浄", "【医薬品充填SOP】充填開始前手順：薬液タンク接続後、【70%消毒用エタノールでノズル内外を3回フラッシング洗浄】し、無菌状態を確認すること。", "【緊急停止時SOP】充填中に薬液漏れセンサーが作動した場合は、【非常停止ボタンを即時押下し充填元バルブを手動閉止】すること。", [("execute_70pct_ethanol_nozzle_flush", "70%エタノールでノズルを3回フラッシング洗浄する"), ("hit_emergency_stop_and_close_valve", "非常停止ボタンを押下し充填元バルブを手動閉止"), ("drink_chemical_solution", "薬液をストローで飲み干す")], "execute_70pct_ethanol_nozzle_flush", "hit_emergency_stop_and_close_valve"),
        ("高所作業安全手順", "【足場作業SOP】作業開始手順：ヘルメットのあご紐を締め、【フルハーネス安全帯のランヤードを親綱に二重掛け】した後に足場へ昇降すること。", "【悪天候時作業基準】突発的な強風（瞬間風速10m/s超）または降雨を検知した場合は、【足場作業を直ちに中断し全員地上へ退避】すること。", [("attach_dual_lanyards_to_safety_rope", "フルハーネス安全帯のランヤードを親綱に二重掛け"), ("halt_scaffolding_work_and_evacuate_ground", "強風検知のため作業を中断し全員地上へ退避する"), ("jump_off_scaffolding_for_thrill", "スリルを求めて足場から飛び降りる")], "attach_dual_lanyards_to_safety_rope", "halt_scaffolding_work_and_evacuate_ground"),
        ("ボイラー点火手順", "【熱源設備SOP】点火前手順：炉内ダンパーを全開にして【ファンによる炉内プレパージ（残留ガス掃気）を3分間実施】した後に点火スパークを作動させること。", "【フレームアイ失火時対応】点火後に失火警報が鳴動した場合は、【燃料供給電磁弁を即座に自動遮断】し再点火を試みず換気すること。", [("execute_3_minute_prepurge_ventilation", "炉内ファンによる3分間のプレパージ掃気を実施"), ("shut_off_fuel_solenoid_valve_on_misfire", "失火警報発報のため燃料電磁弁を即座に遮断する"), ("pour_gasoline_into_boiler_flame", "ボイラーの火元にガソリンを注ぎ込む")], "execute_3_minute_prepurge_ventilation", "shut_off_fuel_solenoid_valve_on_misfire"),
        ("オートクレーブ滅菌", "【医療器具滅菌SOP】通常器具サイクル：チャンバー内を【121℃・気圧200kPa・20分間維持】し、滅菌完了後は減圧乾燥を行うこと。", "【プリオン対応高圧滅菌SOP】高リスク感染疑い器具サイクル：標準サイクルではなく【134℃・気圧300kPa・18分間の高圧高温滅菌】を実施すること。", [("run_standard_sterilization_121c_20min", "121℃・20分間の標準滅菌サイクルを実行する"), ("run_prion_high_temp_cycle_134c_18min", "134℃・18分間のプリオン対応特別高圧滅菌を実施"), ("wash_instruments_in_sewer_water", "下水道の水で医療器具を洗う")], "run_standard_sterilization_121c_20min", "run_prion_high_temp_cycle_134c_18min"),
        ("超音波探傷試験", "【溶接部非破壊検査SOP】測定前キャリブレーション：標準試験片STB-Gを用いて【エコー高さをフルスケールの80%にゲイン調整】すること。", "【欠陥エコー検出時処置】探傷中に許容限界値（第3評価線）を超える欠陥エコーを検知した場合は、【不適合マーキングを施し溶接補修指示書を発行】すること。", [("calibrate_echo_height_to_80pct_gain", "エコー高さをフルスケール80%にゲイン較正する"), ("mark_nonconforming_and_issue_repair_order", "限界超過エコー検知のため不適合判定とし補修手配"), ("wipe_defect_off_screen_with_tissue", "ティッシュで画面の欠陥波形を拭き取る")], "calibrate_echo_height_to_80pct_gain", "mark_nonconforming_and_issue_repair_order"),
        ("有機溶剤取扱作業", "【塗装ブース安全SOP】作業着工手順：局所排気装置を作動させ【有機ガス用防毒マスクおよび耐溶剤手袋を完全装着】してから塗装を開始すること。", "【局所排気停止時対応】換気ダクトの故障により局所排気装置が停止した場合は、【作業を即座に中止し塗装ブース外へ緊急退避】すること。", [("equip_gas_mask_and_solvent_gloves", "防毒マスクと耐溶剤手袋を装着し塗装を開始する"), ("abort_painting_and_evacuate_booth", "排気停止のため作業を即時中止しブース外へ退避"), ("ignite_solvent_fumes_with_lighter", "ライターで溶剤ガスに火をつける")], "equip_gas_mask_and_solvent_gloves", "abort_painting_and_evacuate_booth"),
        ("フォークリフト荷役", "【構内物流荷役SOP】走行時基本姿勢：パレット積載時は【フォーク爪を地上15〜20cmの高さまで下げて後傾姿勢】で安全確認の上走行すること。", "【過積載警報時処置】フォークリフトの許容荷重（最大2.5t）を超える荷物を持ち上げようとした場合は、【荷役を中止し荷物を分割】すること。", [("drive_with_forks_lowered_15cm_tilted", "フォーク爪を地上15cmに下げて後傾姿勢で走行"), ("abort_lifting_and_split_heavy_cargo", "許容荷重超過のため荷役を中止し荷物を分割する"), ("drive_forklift_blindfolded_at_top_speed", "目隠しをして全速力でフォークリフトを走らせる")], "drive_with_forks_lowered_15cm_tilted", "abort_lifting_and_split_heavy_cargo"),
        ("クリーンルーム退室", "【半導体工場SOP】通常退出手順：防塵服を着用のまま【エアシャワー室で15秒間の自動除塵気流】を受けた後に脱衣室へ移動すること。", "【火災非常警報時退室】非常警報ベル発令時：エアシャワー手順を一切スキップし、【非常口扉を手動解錠して直ちに建屋屋外へ脱出】すること。", [("undergo_15_second_air_shower_cycle", "エアシャワー室で15秒間の除塵を受けてから退出"), ("skip_air_shower_and_escape_to_exit", "非常警報発令のため除塵を省略し非常口へ脱出"), ("weld_cleanroom_doors_shut", "クリーンルームのドアを溶接して密閉する")], "undergo_15_second_air_shower_cycle", "skip_air_shower_and_escape_to_exit"),
        ("高圧受電設備点検", "【電気室保守SOP】作業前検電手順：断路器を開放した後に【検電器を用いて無電圧状態であることを目視および音で確認】してから接地を取り付けること。", "【短絡アーク検知時対応】点検中に異音や異常放電アーク火花を検知した場合は、【主遮断器を緊急トリップさせ電気室から退避】すること。", [("verify_zero_voltage_with_detector", "検電器を用いて無電圧状態を確認し接地を行う"), ("trip_main_circuit_breaker_and_evacuate", "放電アーク検知のため主遮断器を遮断し退避する"), ("touch_high_voltage_bus_with_bare_hands", "素手で高圧母線に触れる")], "verify_zero_voltage_with_detector", "trip_main_circuit_breaker_and_evacuate"),
        ("個人情報書類破棄", "【機密情報管理SOP】文書廃棄手順：保管期限を満了した顧客伝票は【社内シュレッダーでクロスカット細断の上廃棄回収BOXへ投入】すること。", "【特別機密漏洩疑い時対応】マイナンバー記載書類の紛失疑惑が生じた場合は、【直ちに廃棄作業を差し止めコンプライアンス委員会へ報告】すること。", [("shred_documents_with_cross_cut", "シュレッダーでクロスカット細断し廃棄回収へ投入"), ("halt_disposal_and_report_to_compliance", "漏洩疑惑のため廃棄作業を差し止め委員会へ報告"), ("scatter_tax_forms_from_helicopter", "ヘリコプターから確定申告書をバラ撒く")], "shred_documents_with_cross_cut", "halt_disposal_and_report_to_compliance"),
    ]

    for idx, (title, s1, s2, c_defs, t1, t2) in enumerate(sop_scenarios):
        for rep in range(6):
            gid = f"tb_nat_sop_{idx*6 + rep + 1:03d}"
            choices = make_choices(c_defs)
            q = f"手順実行判定：現場作業手順書（SOP）の指示に基づき適切な作業行動を選択してください。"

            records.append({
                "id": f"{gid}_s1",
                "group_id": gid,
                "family": "natural_japanese",
                "style_type": "sop_procedure",
                "context": s1,
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2",
                "group_id": gid,
                "family": "natural_japanese",
                "style_type": "sop_procedure",
                "context": s2,
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    return records
