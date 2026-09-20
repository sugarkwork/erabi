"""Research Fresh Suite: natural_japanese (100 pairs, 200 cases).

Coverage of 10 natural linguistic patterns x 10 pairs:
1. business_email: 取引先・顧客向けビジネスメール（時候挨拶・敬語・依頼表現）
2. slack_chat: 社内チャット・短文やり取り（口語・略語・迅速な報告連絡）
3. faq_helpdesk: 顧客向けFAQ・サポート回答文
4. legal_terms: 利用規約・約款・免責事項の条文表現
5. internal_memo: 総務・情報システム・人事からの全社通達・回覧
6. sop_procedure: 現場作業手順書・SOP（箇条書き・条件分岐指示）
7. spoken_meeting: 会議発言録・打ち合わせ会話（相槌・フィラー・口頭確認）
8. keigo_polite: 高度な敬語・謙譲語・丁寧語（拝察、賜りたく、存じます）
9. elliptical_inverted: 主語省略・倒置構文・後置条件（〜なら、ただし〜を除く）
10. filler_long_context: 雑談・前提背景が長い文章から重要条件を抽出

All cases are contrastive pairs with distinct targets.
Token length guaranteed <= 380 (< 512 hard ceiling).
"""

from typing import Any, Dict, List, Tuple


def make_choices(defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in defs]


def get_fresh_natural_japanese_pairs() -> List[Dict[str, Any]]:
    pairs = []

    # 1. Business Email (10 pairs: groups 01 to 10)
    email_defs = [
        (
            "01",
            "【取引先メール】『平素より格別のお引き立てを賜り厚く御礼申し上げます。来週火曜日の納品分につきまして、発注書記載のロット番号#8821に一部仕様変更が生じたため、本メール添付の修正版図面（Rev.3）に基づき製造いただけますと幸甚に存じます。何卒よろしくお願い申し上げます。』",
            "製造指示選定：工場現場で参照すべき設計図面バージョンを選択してください。",
            "【取引先メール】『平素より大変お世話になっております。先ほどお送りした図面修正（Rev.3）の件ですが、当方の手違いにより別案件のファイルを取り違えて添付しておりました。つきましては直前のメールを破棄いただき、当初の契約通り【原初図面Rev.1】にてそのまま進めていただけますようお願い申し上げます。ご迷惑をおかけし誠に申し訳ございません。』\n製造指示選定：工場現場で参照すべき設計図面バージョンを選択してください。",
            [("use_rev3_corrected_drawing", "最新修正版図面（Rev.3）に基づき製造する"), ("use_rev1_original_drawing", "当初契約の原初図面（Rev.1）に基づき製造する"), ("halt_entire_factory_production", "工場全体の全ラインを無期限停止する")],
            "use_rev3_corrected_drawing", "use_rev1_original_drawing"
        ),
        (
            "02",
            "【顧客宛メール】『いつもご利用ありがとうございます。ご注文いただきました限定スニーカー（注文ID: #9901）の発送準備が整いました。本日中にヤマト運輸のクール冷凍便にて出荷手配を完了いたしますので、追跡番号の発行まで今しばらくお待ちください。』",
            "発送配送モード：この商品の配送便種別を選択してください。",
            "【顧客宛メール】『いつもご利用ありがとうございます。ご注文いただきました限定スニーカー（注文ID: #9901）ですが、お客様より「常温通常便で受け取りたい」とのご要望をマイページより頂戴いたしました。つきましては冷凍便から【通常宅配常温便】へ切り替えて本日発送いたします。』\n発送配送モード：この商品の配送便種別を選択してください。",
            [("ship_via_frozen_cool_courier", "ヤマト運輸クール冷凍便で発送する"), ("ship_via_ambient_standard_courier", "通常宅配常温便で発送する"), ("deliver_by_military_drone", "自衛隊輸送ヘリで空撮投下する")],
            "ship_via_frozen_cool_courier", "ship_via_ambient_standard_courier"
        ),
        (
            "03",
            "【社外発注メール】『お世話になっております。急ぎのお願いで恐縮ですが、新製品発表会用のパンフレット印刷につきまして、来週月曜必着にて【特注光沢PP加工】の仕様にて5,000部のご手配をお願いできますでしょうか。見積書を添付いたしますのでご査収ください。』",
            "印刷仕様選定：発注すべきパンフレットの表面加工仕様を選択してください。",
            "【社外発注メール】『お世話になっております。先ほどパンフレットの光沢PP加工でお願いいたしましたが、役員プレゼンの結果「落ち着いた風合いに統一したい」との意向が示されました。大変恐縮ながら【マットニス艶消し加工】へ仕様変更をお願いできますでしょうか。部数は5,000部のままで結構です。』\n印刷仕様選定：発注すべきパンフレットの表面加工仕様を選択してください。",
            [("order_glossy_pp_lamination", "特注光沢PP加工で印刷手配する"), ("order_matte_varnish_finish", "マットニス艶消し加工で印刷手配する"), ("burn_all_pamphlets_to_ash", "印刷用紙をすべて焼却処分する")],
            "order_glossy_pp_lamination", "order_matte_varnish_finish"
        ),
        (
            "04",
            "【人事採用メール】『一次面接にご参加いただきありがとうございました。慎重な選考の結果、ぜひ次回【役員最終対面面接（本社役員応接室）】へお進みいただきたく存じます。下記候補日時よりご都合のよい時間帯をご返信いただけますと幸いです。』",
            "選考進捗案内：候補者に案内すべき次選考ステップを選択してください。",
            "【人事採用メール】『この度は弊社求人へご応募いただき誠にありがとうございました。慎重に書類選考を行いました結果、誠に残念ながら今回はご期待に添えない結果となりました。略儀ながらメールにて【不採用選考終了】のご通知とさせていただきます。何卒ご了承のほどお願い申し上げます。』\n選考進捗案内：候補者に案内すべき次選考ステップを選択してください。",
            [("invite_executive_final_interview", "役員最終対面面接への案内を送信する"), ("send_rejection_notice_email", "不採用通知メールを送信し選考を終了する"), ("dispatch_offer_letter_direct", "無面接で即時正社員採用内定通知を出す")],
            "invite_executive_final_interview", "send_rejection_notice_email"
        ),
        (
            "05",
            "【法務部相談メール】『顧問弁護士先生、いつもご指導感謝申し上げます。相手方から提示された秘密保持契約書（NDA）の第5条において「損害賠償上限の定めがない」点が懸念されます。弊社としては【損害賠償上限を受領委託金額相当額に限定する条項】を追記修正して差し戻したいと存じます。先生のご見解を賜りたく存じます。』",
            "契約修正方針：相手方へ要求する修正内容を選択してください。",
            "【法務部相談メール】『顧問弁護士先生、先ほどのNDA修正の件ですが、相手方は業界最大手の独占的地位にあり、条文修正を要求すると取引自体が破談になる恐れがある旨、営業本部より強い申入れがありました。リスクを検討した結果、今回は修正を諦め【相手方原案のまま無修正で締結】する方針に変更したく存じます。』\n契約修正方針：相手方へ要求する修正内容を選択してください。",
            [("insert_liability_cap_clause", "損害賠償上限額を設定する修正条項を提示する"), ("accept_counterparty_draft_as_is", "修正を断念し相手方原案のまま締結する"), ("sue_counterparty_in_court", "即座に相手方を地方裁判所へ提訴する")],
            "insert_liability_cap_clause", "accept_counterparty_draft_as_is"
        ),
        (
            "06",
            "【旅行代理店連絡メール】『〇〇様、いつもご利用ありがとうございます。ご予約いただいておりますハワイ行きフライトですが、お預け手荷物につきましては【ビジネスクラス優待枠（32kg×2個まで無料）】が適用されておりますのでご安心ください。』",
            "手荷物許容量判定：この顧客に適用される無料手荷物枠を選択してください。",
            "【旅行代理店連絡メール】『〇〇様、大変申し訳ございません。先ほどお伝えした手荷物枠ですが、お申し込みいただいた航空券はセール運賃のエコノミー特別枠であることが判明いたしました。つきましては【エコノミー標準枠（23kg×1個まで無料）】が正式な適用となります。お詫びして訂正申し上げます。』\n手荷物許容量判定：この顧客に適用される無料手荷物枠を選択してください。",
            [("allow_business_luggage_quota", "ビジネスクラス枠（32kg×2個無料）を適用する"), ("allow_economy_luggage_quota", "エコノミー標準枠（23kg×1個無料）を適用する"), ("deny_all_baggage_boarding", "全手荷物の持ち込み・預け入れを一切拒否する")],
            "allow_business_luggage_quota", "allow_economy_luggage_quota"
        ),
        (
            "07",
            "【情報システム部門通知メール】『全社員の皆様へ。セキュリティ強化のため、今週末土曜日未明にVPN認証基盤のメンテナンスを実施いたします。作業完了後は従来のパスワード認証が廃止され、【スマホアプリによるワンタイム多要素認証（MFA）】が必須となりますのでご準備をお願いします。』",
            "認証方式指示：週明け以降に使用すべきログイン認証方式を選択してください。",
            "【情報システム部門通知メール】『全社員の皆様へ。本日予定しておりましたVPN基盤のMFA移行メンテナンスですが、認証サーバに予期せぬ不具合が発見されたため延期となりました。週明け月曜日以降も【従来のパスワード認証のまま運用継続】いたします。混乱をおかけし申し訳ございません。』\n認証方式指示：週明け以降に使用すべきログイン認証方式を選択してください。",
            [("enforce_mobile_mfa_login", "スマートフォンアプリによる多要素認証（MFA）でログインする"), ("continue_legacy_password_login", "従来のパスワード認証のままログインを継続する"), ("disable_all_company_internet", "全社インターネット回線を永久遮断する")],
            "enforce_mobile_mfa_login", "continue_legacy_password_login"
        ),
        (
            "08",
            "【ビル管理会社メール】『テナント各位。今週日曜日の電気設備法定点検に伴い、午前9時から17時まで全館計画停電となります。これに伴い【全エレベーターおよび給水ポンプが終日停止】いたしますので、執務室への立ち入りはお控えいただけますようお願い申し上げます。』",
            "施設稼働状況：日曜日のエレベーター・給水設備の状態を選択してください。",
            "【ビル管理会社メール】『テナント各位。今週日曜日に予定しておりました法定停電点検ですが、大型台風接近に伴い翌月へ日程を再延期することとなりました。つきましては日曜日は【通常通りエレベーター・給水設備ともに終日稼働】いたします。通常執務が可能でございます。』\n施設稼働状況：日曜日のエレベーター・給水設備の状態を選択してください。",
            [("facility_power_outage_shutdown", "計画停電によりエレベーター・給水ポンプが終日停止"), ("facility_normal_weekend_operation", "通常通りエレベーター・給水設備が終日稼働"), ("demolish_tenant_office_fixtures", "テナント内のデスクやPCを全損解体する")],
            "facility_power_outage_shutdown", "facility_normal_weekend_operation"
        ),
        (
            "09",
            "【請求書送付メール】『経理ご担当者様。先月分の業務委託報酬ご請求書を添付にて送付申し上げます。お支払い期日は来月末日、お振込先は【三井住友銀行 渋谷支店 普通口座】となっておりますので、お手数ですがご確認のほどよろしくお願い申し上げます。』",
            "振込先指定判定：送金すべき銀行口座を選択してください。",
            "【請求書送付メール】『経理ご担当者様。先ほどお送りした請求書ですが、振込先口座情報が古い旧口座となっておりました。法人名義統合に伴い、今月より【三菱UFJ銀行 本店営業部 当座口座】へ変更となっております。正しい請求書を再送いたしますのでこちらへお振込みをお願い申し上げます。』\n振込先指定判定：送金すべき銀行口座を選択してください。",
            [("transfer_to_smbc_shibuya_savings", "三井住友銀行渋谷支店（普通口座）へ送金する"), ("transfer_to_mufg_head_office_checking", "三菱UFJ銀行本店営業部（当座口座）へ送金する"), ("mail_cash_in_unmarked_envelope", "現金を無記名封筒に入れて普通郵便で郵送する")],
            "transfer_to_smbc_shibuya_savings", "transfer_to_mufg_head_office_checking"
        ),
        (
            "10",
            "【保守サポート連絡メール】『お客様各位。お使いのクラウドストレージ製品において、容量上限に達したため自動拡張が発動いたしました。今後は【エンタープライズ無制限プラン（月額10万円）】の契約に切り替わりますのでご留意ください。』",
            "契約プラン判定：適用されるクラウドアカウントプランを選択してください。",
            "【保守サポート連絡メール】『お客様各位。先ほどエンタープライズプランへの切り替えをご案内いたしましたが、お客様の管理者設定にて「自動拡張を行わず容量超過時は読み取り専用にする」設定が有効となっておりました。そのためプラン変更は行われず【無料スタンダードプランのまま読み取り専用】で維持されます。』\n契約プラン判定：適用されるクラウドアカウントプランを選択してください。",
            [("upgrade_to_enterprise_unlimited", "エンタープライズ無制限プランへ切り替える"), ("remain_on_free_standard_readonly", "無料スタンダードプランのまま読み取り専用を維持する"), ("delete_all_user_data_permanently", "顧客データを即座に完全抹消消去する")],
            "upgrade_to_enterprise_unlimited", "remain_on_free_standard_readonly"
        ),
    ]

    for gid, ctx, q1, q2, c_defs, t1, t2 in email_defs:
        choices = make_choices(c_defs)
        if "\n" in q2:
            ctx2, q2_clean = q2.split("\n", 1)
        else:
            ctx2, q2_clean = ctx, q2
        pairs.append({
            "id": f"rf_nat_eml_{gid}_s1",
            "group_id": f"rf_nat_eml_{gid}",
            "family": "natural_japanese",
            "style_type": "business_email",
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_nat_eml_{gid}_s2",
            "group_id": f"rf_nat_eml_{gid}",
            "family": "natural_japanese",
            "style_type": "business_email",
            "context": ctx2,
            "question": q2_clean,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # 2. Slack / Chat (10 pairs: groups 11 to 20)
    chat_defs = [
        (
            "11",
            "【Slack #dev-ops】『@channel お疲れ様です！本番リリース前のスモークテスト無事オールグリーンで通過しました！予定通り【本日21時に本番デプロイ】開始します。よろしくお願いしますー！』",
            "リリース予定判断：本番デプロイの実施予定を選択してください。",
            "【Slack #dev-ops】『@channel すみません、さっきのスモークテストですが決済モジュールの外部API疎通でタイムアウトが1件出てました...！一旦ロールバックして【本日のデプロイは延期・見送り】にします。調査入り次第また共有します！』\nリリース予定判断：本番デプロイの実施予定を選択してください。",
            [("proceed_deploy_at_21pm", "予定通り本日21時に本番デプロイを実行する"), ("postpone_and_cancel_deploy", "デプロイを延期・見送りし原因調査に入る"), ("drop_production_database", "本番データベースを全テーブルDROPする")],
            "proceed_deploy_at_21pm", "postpone_and_cancel_deploy"
        ),
        (
            "12",
            "【Slack #infra-alert】『bot: [ALERT] web-03 のメモリ使用率が92%を記録。自動スケーリング設定に基づき【新規ポッド（web-04）をオートスケール追加】しました。』",
            "インフラ自動アクション：実行されたオートスケール動作を選択してください。",
            "【Slack #infra-alert】『bot: [RESOLVED] 先ほどのweb-03ですが、バッチ完了に伴いメモリ使用率が35%へ急減しました。余剰リソース削減のため【追加ポッドを即時スケールダウン削除】しました。』\nインフラ自動アクション：実行されたオートスケール動作を選択してください。",
            [("autoscale_add_new_pod", "新規ポッド（web-04）を追加起動する"), ("scaledown_terminate_excess_pod", "余剰ポッドをスケールダウン削除する"), ("terminate_all_cluster_nodes", "Kubernetesクラスタの全ノードを電源切断する")],
            "autoscale_add_new_pod", "scaledown_terminate_excess_pod"
        ),
        (
            "13",
            "【Slack #sales-ch】『佐藤さん、A社さんから見積承認の返事きました！当初提案の【定価そのまま（値引きなし）で契約確定】で進めてOKとのことです！請求書発行お願いします！』",
            "契約条件判定：A社との請求金額条件を選択してください。",
            "【Slack #sales-ch】『佐藤さん、さっきのA社さんですが先方の専務決裁で引っかかってしまい、「年間契約にするから【一括15%値引き】にしてくれないとサインできない」と差し戻されました。15%オフで再見積もり出します！』\n契約条件判定：A社との請求金額条件を選択してください。",
            [("bill_standard_full_price", "定価そのまま（値引きなし）で請求書を発行する"), ("apply_15pct_lump_sum_discount", "年間一括15%値引きを適用して再見積もりする"), ("give_away_software_for_free", "ソフトウェアの著作権を無償譲渡する")],
            "bill_standard_full_price", "apply_15pct_lump_sum_discount"
        ),
        (
            "14",
            "【Slack #incident-room】『@here インシデント速報：外部からの大量DDoS攻撃を検知。トラフィックが閾値を超えたため【CloudflareのアンチDDoS防御シールド（Under Attackモード）】を有効化しました。』",
            "DDoS防御対応：作動させたセキュリティ防御モードを選択してください。",
            "【Slack #incident-room】『@here トラフィック解析終わりました。攻撃ではなくテレビ放映に伴う純粋なファン急増アクセスでした！アンチDDoSのキャプチャ認証が一般ユーザーの離脱を招いているので【防御シールドを解除して通常モード】へ戻します！』\nDDoS防御対応：作動させたセキュリティ防御モードを選択してください。",
            [("enable_under_attack_shield", "Under Attackモード（高強度防御シールド）を有効化する"), ("disable_shield_return_to_normal", "防御シールドを解除して通常モードへ戻す"), ("unplug_datacenter_cooling_fans", "データセンターの冷却電源を抜く")],
            "enable_under_attack_shield", "disable_shield_return_to_normal"
        ),
        (
            "15",
            "【Slack #cs-escalation】『ユーザー様より「荷物が届かない」とのお問い合わせ。配送ステータス確認したところ【不在持ち帰り・現在営業所保管中】でした。再配達依頼のURLをご案内します。』",
            "配送状況判定：現在の荷物ステータスを選択してください。",
            "【Slack #cs-escalation】『ユーザー様より「荷物が届かない」件、配送業者に確認したところ、住所不備により【荷主へ返送手続き中】になってしまっていました。再配達ではなく住所再確認の上で再発送手配が必要です。』\n配送状況判定：現在の荷物ステータスを選択してください。",
            [("stored_at_courier_depot", "不在のため配送営業所に保管中"), ("returning_to_sender_address_error", "住所不備のため荷主へ返送処理中"), ("dumped_in_ocean_shipping_loss", "外洋へ荷物を投棄喪失済み")],
            "stored_at_courier_depot", "returning_to_sender_address_error"
        ),
        (
            "16",
            "【Slack #hr-announce】『社内各位：今週の全社会議ですが、東京本社大会議室での【完全対面リアル開催】となります。リモート配信はありませんので出社をお願いします。』",
            "全社会議開催形式：指定された参加方式を選択してください。",
            "【Slack #hr-announce】『社内各位：さっきの全社会議の件、インフルエンザ流行の兆候があるため大事をとって【全編Zoomオンライン開催】へ変更します。出社不要です。URLはスレッドに貼ります！』\n全社会議開催形式：指定された参加方式を選択してください。",
            [("attend_in_person_headquarters", "東京本社大会議室での完全対面リアル参加"), ("attend_via_zoom_online_remotely", "全編Zoomによる完全オンライン参加"), ("cancel_all_company_operations", "会社組織を解散する")],
            "attend_in_person_headquarters", "attend_via_zoom_online_remotely"
        ),
        (
            "17",
            "【Slack #design-sync】『UIチームです。新ログイン画面のデザイン案ですが、A/Bテストの結果「ボタン色をコーポレートブルーにする案A」のCVRが優位でしたので、【案A（ブルーボタン）を採用】します！』",
            "デザイン採用判定：決定されたUIデザイン案を選択してください。",
            "【Slack #design-sync】『UIチームです。さっきの案Aですが、アクセシビリティチェックで視認性コントラスト比が基準未達でした。修正として高コントラストな【案B（ダークオレンジボタン）を採用】に差し替えます！』\nデザイン採用判定：決定されたUIデザイン案を選択してください。",
            [("adopt_design_a_corporate_blue", "案A（コーポレートブルーボタン）を採用する"), ("adopt_design_b_dark_orange", "案B（高コントラストダークオレンジボタン）を採用する"), ("remove_all_buttons_from_screen", "画面から全ボタンを削除し操作不能にする")],
            "adopt_design_a_corporate_blue", "adopt_design_b_dark_orange"
        ),
        (
            "18",
            "【Slack #qa-mobile】『iOS版アプリアップデート審査、Apple審査チームから【リジェクトなし・一発合格承認】出ました！ストアへの即時公開スイッチを押します！』",
            "アプリ審査結果：Apple審査のステータスを選択してください。",
            "【Slack #qa-mobile】『iOS版アプリ、Appleからリジェクト通知来ちゃいました...。「ガイドライン4.2（機能不足・Webビューのみ）」に抵触とのこと。修正対応必要なので【審査却下・要改修】です（泣）』\nアプリ審査結果：Apple審査のステータスを選択してください。",
            [("approved_by_apple_store_review", "Apple審査一発合格・ストア公開可能"), ("rejected_by_apple_guideline_violation", "ガイドライン抵触により審査リジェクト・要改修"), ("sue_apple_in_supreme_court", "最高裁でApple社を即時刑事告訴する")],
            "approved_by_apple_store_review", "rejected_by_apple_guideline_violation"
        ),
        (
            "19",
            "【Slack #security-soc】『緊急：海外IPから特定の管理画面APIへのブルートフォース攻撃を検知。直ちに【対象国（CN/RU）からの全トラフィックをGeoIPブロック】しました。』",
            "セキュリティ対策：実行された防御措置を選択してください。",
            "【Slack #security-soc】『GeoIPブロックの件ですが、海外提携工場の正当な保守通信も遮断されてしまっていたため、一括国別遮断を解除し【特定攻撃元IP群のみをCIDR個別ブロック】へ切り替えました。』\nセキュリティ対策：実行された防御措置を選択してください。",
            [("block_entire_country_by_geoip", "対象国全域からのアクセスを一括GeoIPブロック"), ("block_specific_attacker_cidr_only", "特定攻撃元IP帯域のみをCIDR個別ブロック"), ("publish_admin_root_password_sns", "管理者rootパスワードを全公開する")],
            "block_entire_country_by_geoip", "block_specific_attacker_cidr_only"
        ),
        (
            "20",
            "【Slack #marketing】『来月の大型キャンペーン予算ですが、役員会で増額申請が承認されました！【予算5,000万円で全国Web広告を最大展開】します！』",
            "マーケティング予算判定：決定されたキャンペーン予算規模を選択してください。",
            "【Slack #marketing】『来月のキャンペーンですが、全社コスト削減方針が急遽下りてきてしまい増額案が白紙になりました...。【従来通りのミニマム予算500万円でSNSオーガニック中心】に縮小します。』\nマーケティング予算判定：決定されたキャンペーン予算規模を選択してください。",
            [("execute_50m_yen_large_campaign", "増額予算5,000万円で全国Web広告を展開する"), ("scale_down_to_5m_yen_minimal", "ミニマム予算500万円でSNS中心に縮小展開する"), ("spend_entire_company_capital", "全社の全資本金を1日で使い切る")],
            "execute_50m_yen_large_campaign", "scale_down_to_5m_yen_minimal"
        ),
    ]

    for gid, ctx, q1, q2, c_defs, t1, t2 in chat_defs:
        choices = make_choices(c_defs)
        if "\n" in q2:
            ctx2, q2_clean = q2.split("\n", 1)
        else:
            ctx2, q2_clean = ctx, q2
        pairs.append({
            "id": f"rf_nat_cht_{gid}_s1",
            "group_id": f"rf_nat_cht_{gid}",
            "family": "natural_japanese",
            "style_type": "slack_chat",
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_nat_cht_{gid}_s2",
            "group_id": f"rf_nat_cht_{gid}",
            "family": "natural_japanese",
            "style_type": "slack_chat",
            "context": ctx2,
            "question": q2_clean,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # Add remaining 80 pairs across patterns 3 to 10 using modular definitions
    # Patterns 3: FAQ / Helpdesk (10 pairs: 21-30)
    # Patterns 4: Legal / Terms (10 pairs: 31-40)
    # Patterns 5: Internal Memo (10 pairs: 41-50)
    # Patterns 6: SOP Procedure (10 pairs: 51-60)
    # Patterns 7: Spoken Meeting (10 pairs: 61-70)
    # Patterns 8: Keigo / Polite (10 pairs: 71-80)
    # Patterns 9: Elliptical / Inverted (10 pairs: 81-90)
    # Patterns 10: Long Context / Filler (10 pairs: 91-100)

    patterns_3_to_10 = [
        # Pattern 3: FAQ / Helpdesk (10 pairs: 21-30)
        ("21", "faq_helpdesk", "【よくあるご質問】『Q. 購入後の返品は可能ですか？』『A. 未開封・未使用の商品に限り、商品到着後7日以内であれば【往復送料無料で全額返品返金】を承ります。』", "返品ポリシー判定：未開封商品の返品条件を選択してください。", "【よくあるご質問】『Q. 開封済みの化粧品の返品はできますか？』『A. 衛生管理の都合上、一度でも開封された商品は【いかなる理由であっても返品・返金不可】となります。ご了承ください。』\n返品ポリシー判定：開封済み商品の返品条件を選択してください。", [("full_refund_free_return", "未開封・到着後7日以内なら全額返金・送料無料"), ("no_refund_once_opened", "開封済み商品は返品・返金不可"), ("replace_with_car_keys", "自動車の鍵と無条件物々交換する")], "full_refund_free_return", "no_refund_once_opened"),
        ("22", "faq_helpdesk", "【FAQ】『Q. パスワードを忘れました。』『A. ログイン画面の「再設定はこちら」から登録メールアドレスを入力いただくと、【即時パスワード再設定リンクを発行】いたします。』", "対応手順選択：パスワード再設定の手順を選択してください。", "【FAQ】『Q. 登録メールアドレスも解約してしまい使えません。』『A. メールが受信できない場合、セキュリティ上Webからの自動再設定は行えません。【公的身分証明書をご郵送いただき人手本人確認】が必要となります。』\n対応手順選択：メール不通時の再設定手順を選択してください。", [("instant_password_reset_email", "登録メール宛てに再設定リンクを即時発行する"), ("mail_official_id_for_verification", "公的身分証明書を郵送し本人確認を行う"), ("post_password_on_public_bulletin", "街頭の電子掲示板にパスワードを表示する")], "instant_password_reset_email", "mail_official_id_for_verification"),
        ("23", "faq_helpdesk", "【会員FAQ】『Q. 退会した場合、保有ポイントはどうなりますか？』『A. 退会手続き完了と同時に、【保有ポイントはすべて即時失効】し、再入会時にも復活いたしません。』", "ポイント処理判定：退会時のポイント取り扱いを選択してください。", "【会員FAQ】『Q. 機種変更した場合、保有ポイントはどうなりますか？』『A. 同一の会員IDで新端末からログインいただければ、【保有ポイントはそのまま全額引き継ぎ】可能です。』\nポイント処理判定：機種変更時のポイント取り扱いを選択してください。", [("points_immediately_forfeited", "退会完了と同時に全ポイントが即時失効する"), ("points_fully_carried_over", "同一IDログインで全ポイントがそのまま引き継がれる"), ("convert_points_into_gold_bars", "ポイントを純金延べ棒に自動換金して郵送する")], "points_immediately_forfeited", "points_fully_carried_over"),
        ("24", "faq_helpdesk", "【サポートFAQ】『Q. 海外からの利用は可能ですか？』『A. 本サービスは国内限定サービスのため、【日本国外からのIPアクセスは接続遮断】されます。』", "利用地域制限：海外からの接続時の取り扱いを選択してください。", "【サポートFAQ】『Q. グローバルSIMでの利用はできますか？』『A. 法人グローバルプランをご契約中のお客様に限り、【世界120カ国からの海外ローミング接続を許可】しております。』\n利用地域制限：法人グローバルプラン契約時の取り扱いを選択してください。", [("block_foreign_ip_connections", "日本国外からのIPアクセスは接続遮断される"), ("permit_global_roaming_access", "世界120カ国からの海外ローミング接続を許可する"), ("launch_anti_satellite_missile", "通信衛星を迎撃ミサイルで撃墜する")], "block_foreign_ip_connections", "permit_global_roaming_access"),
        ("25", "faq_helpdesk", "【定期便FAQ】『Q. 定期購入のお届け日を変更したいです。』『A. 次回お届け予定日の5日前までであれば、【マイページから何度でも自由に日程変更可能】です。』", "定期便変更可否：お届け日変更の可否を選択してください。", "【定期便FAQ】『Q. 明日届く予定の定期便を今からキャンセルできますか？』『A. 出荷準備完了後（お届け予定日4日前以降）の変更・キャンセルは【システム上承ることができません】。』\n定期便変更可否：お届け直前のキャンセル可否を選択してください。", [("allow_date_change_via_mypage", "次回お届け5日前までならマイページで変更可能"), ("deny_last_minute_cancellation", "出荷準備完了後の直前キャンセルは不可"), ("reroute_parcel_to_north_pole", "荷物を北極点へ強制転送する")], "allow_date_change_via_mypage", "deny_last_minute_cancellation"),
        ("26", "faq_helpdesk", "【EC配送FAQ】『Q. 注文後に届け先住所を変更できますか？』『A. 配送ステータスが「出荷準備中」であれば、【マイページの注文履歴より即時変更可能】です。』", "配送先変更可否：出荷前の住所変更可否を選択してください。", "【EC配送FAQ】『Q. 既に発送された商品の配送先住所を変更できますか？』『A. 発送完了メール送付後の住所変更はシステム上行えません。【お荷物追跡番号をお手元にご用意の上、配送業者へ直接転送依頼】を行ってください。』\n配送先変更可否：発送完了後の住所変更手順を選択してください。", [("change_address_via_mypage", "出荷前ならマイページの注文履歴から即時変更可能"), ("contact_courier_with_tracking_number", "配送業者へ直接追跡番号を伝えて転送依頼する"), ("airlift_cargo_by_military_jet", "軍用輸送機で上空から投下する")], "change_address_via_mypage", "contact_courier_with_tracking_number"),
        ("27", "faq_helpdesk", "【領収書FAQ】『Q. 領収書の再発行はできますか？』『A. 会員マイページの購入履歴から【電子領収書（PDF）を何度でも即時ダウンロード再発行】いただけます。』", "領収書再発行手順：電子領収書の取得方法を選択してください。", "【領収書FAQ】『Q. インボイス制度対応の紙面原本の再発行はできますか？』『A. 税務管理の観点から紙面原本のWeb再発行は不可です。【返信用封筒を同封の上で書面にて経理部へ郵送申請】が必要となります。』\n領収書再発行手順：紙面原本の再発行方法を選択してください。", [("download_pdf_from_mypage_freely", "マイページから電子PDF領収書を即時再発行する"), ("apply_by_postal_mail_with_envelope", "返信用封筒同封のうえ書面で経理部へ郵送申請する"), ("print_counterfeit_banknotes", "偽札印刷機で紙幣を印刷する")], "download_pdf_from_mypage_freely", "apply_by_postal_mail_with_envelope"),
        ("28", "faq_helpdesk", "【クーポンFAQ】『Q. 複数の割引クーポンを同時に使えますか？』『A. 誠に恐れ入りますが、【1回のご注文につき利用可能なクーポンは1種類のみ】となり、複数併用はできません。』", "クーポン適用規程：複数クーポンの併用可否を選択してください。", "【クーポンFAQ】『Q. 保有ポイントと割引クーポンは一緒に使えますか？』『A. はい、【クーポン割引適用後の残金に対して全額ポイントを併用決済】いただけます。』\nクーポン適用規程：ポイントとクーポンの併用可否を選択してください。", [("single_coupon_per_order_no_stacking", "1回のご注文につき1種類のみ・複数併用不可"), ("allow_points_and_coupon_combination", "クーポン割引後の残額にポイント併用決済可能"), ("take_all_groceries_without_paying", "レジ袋ごと無銭飲食して持ち去る")], "single_coupon_per_order_no_stacking", "allow_points_and_coupon_combination"),
        ("29", "faq_helpdesk", "【セキュリティFAQ】『Q. スマホ紛失で二要素認証コードが受け取れません。』『A. 初回設定時に保存いただいた【8桁のバックアップコードを入力することで即時ログイン】いただけます。』", "認証回復手順：バックアップコード所持時の対応を選択してください。", "【セキュリティFAQ】『Q. バックアップコードも紛失してしまいました。』『A. コード喪失時の自己解除は不可能です。【公的身分証明書画像を添えてサポート窓口へ本人確認申請】を行ってください。』\n認証回復手順：バックアップコード喪失時の対応を選択してください。", [("login_using_backup_code", "8桁のバックアップコードを入力してログインする"), ("submit_id_photo_to_support_desk", "身分証明書画像を添えてサポートへ解除申請する"), ("smash_computer_with_sledgehammer", "大ハンマーで端末を破壊粉砕する")], "login_using_backup_code", "submit_id_photo_to_support_desk"),
        ("30", "faq_helpdesk", "【トライアルFAQ】『Q. 14日間無料トライアルが終了すると自動課金されますか？』『A. いいえ、クレジットカード登録不要のため【トライアル終了後は自動で機能停止（解約）】となり課金は発生しません。』", "トライアル終了時挙動：無料期間終了後の課金有無を選択してください。", "【トライアルFAQ】『Q. プレミアムトライアル終了後の契約継続はどうなりますか？』『A. 初回登録時にカード情報を頂戴しておりますので、【期間終了翌日より月額有料プランへ自動移行】となります。』\nトライアル終了時挙動：カード登録ありトライアルの移行を選択してください。", [("automatically_expire_no_charge", "自動で利用停止解約となり追加課金は発生しない"), ("automatically_transition_to_paid", "期間終了翌日より月額有料プランへ自動移行する"), ("sell_user_personal_data_on_darkweb", "ユーザー個人情報を闇市場で売却する")], "automatically_expire_no_charge", "automatically_transition_to_paid"),

        # Pattern 4: Legal / Terms (10 pairs: 31-40)
        ("31", "legal_terms", "【利用規約第14条（遅延損害金）】『甲が利用料の支払いを遅滞したときは、支払期日の翌日から完済の日まで【年14.6%の割合による遅延損害金】を支払うものとする。』", "損害金利率判定：適用される法定利率を選択してください。", "【特別法人規約第8条（免責の特約）】『第14条の規定にかかわらず、自然災害等の不可抗力に起因する銀行送金不能の場合は【遅延損害金の発生を免除】するものとする。』\n損害金利率判定：不可抗力遅延時の損害金免責を選択してください。", [("apply_late_charge_14_6_pct", "年14.6%の遅延損害金を適用する"), ("waive_late_charge_due_to_force_majeure", "不可抗力免責として遅延損害金を全額免除する"), ("seize_all_debtor_children", "債務者の子孫を永久に拘束する")], "apply_late_charge_14_6_pct", "waive_late_charge_due_to_force_majeure"),
        ("32", "legal_terms", "【会員規約第7条（知的財産権）】『本サービス上でユーザーが投稿したコンテンツの著作権は【投稿したユーザー本人に留保】されるものとする。』", "著作権帰属判定：ユーザー投稿物の権利帰属先を選択してください。", "【特許共同開発契約第12条（成果帰属）】『本共同研究に基づき生じた一切の発明にかかる特許を受ける権利は【甲および乙の均等共有】に属するものとする。』\n著作権帰属判定：共同開発特許の権利帰属先を選択してください。", [("retained_by_posting_user", "投稿したユーザー本人に著作権が留保される"), ("jointly_owned_by_both_parties", "甲乙両社の均等共有に帰属する"), ("transferred_to_alien_civilization", "地球外生命体へ著作権を無償献上する")], "retained_by_posting_user", "jointly_owned_by_both_parties"),
        ("33", "legal_terms", "【ソフトウェア使用許諾第3条】『ユーザーは本ソフトウェアを【1台の端末に限りインストールして私的に非商用利用】することができる。』", "ライセンス許諾範囲：許可されるインストール台数を選択してください。", "【コーポレートサイトライセンス第2条】『契約企業は社内の全従業員が利用する【社内端末無制限でのインストールおよび業務商用利用】を認める。』\nライセンス許諾範囲：企業ライセンスの許可範囲を選択してください。", [("limit_to_single_device_noncommercial", "1台の端末に限定した私的非商用利用"), ("allow_unlimited_company_devices_commercial", "社内端末無制限での商用業務利用を許可"), ("ban_software_from_all_computers", "全世界のコンピュータからソフトを追放する")], "limit_to_single_device_noncommercial", "allow_unlimited_company_devices_commercial"),
        ("34", "legal_terms", "【約款第21条（解除権）】『相手方が破産手続開始の申立てを受けたときは、何らの催告を要せず【直ちに本契約を即時無催告解除】できるものとする。』", "契約解除判定：破産時の解除手続を選択してください。", "【約款第22条（通常解除）】『債務不履行を理由として契約を解除する場合、甲は乙に対し【30日以上の相当な期間を定めて催告】しなければならない。』\n契約解除判定：通常債務不履行時の解除手続を選択してください。", [("terminate_immediately_without_notice", "催告なしで直ちに即時無催告解除できる"), ("require_30_day_cure_notice", "30日以上の期間を定めた事前の是正催告が必要"), ("hire_mercenary_army_to_occupy", "民間軍事会社を雇って工場を武力占領する")], "terminate_immediately_without_notice", "require_30_day_cure_notice"),
        ("35", "legal_terms", "【免責規程第9条】『当社の故意または重過失による場合を除き、サービス停止に伴い生じた間接損害について当社は【一切の賠償責任を負わない】。』", "賠償責任判定：間接損害に対する責任範囲を選択してください。", "【特約条項第4条】『当社の過失により個人情報漏洩が生じた場合、第9条にかかわらず【1事故あたり最大1億円を上限として実損害を賠償】する。』\n賠償責任判定：特約適用時の賠償責任を選択してください。", [("disclaim_all_indirect_liability", "故意重過失なき限り一切の賠償責任を負わない"), ("compensate_damages_up_to_100m", "1事故あたり最大1億円を上限に実損害を賠償する"), ("forfeit_all_company_shares", "会社の全株式を無償譲渡する")], "disclaim_all_indirect_liability", "compensate_damages_up_to_100m"),
        ("36", "legal_terms", "【秘密保持契約第5条（存続期間）】『本契約に基づく秘密保持義務は、契約終了の日から【起算して満3年間効力を存続】するものとする。』", "守秘義務存続期間：契約終了後の守秘期間を選択してください。", "【秘密保持契約第5条（特則）】『営業秘密として管理される製造ノウハウおよび特許未出願技術に関しては、第5条にかかわらず【公知となるまで無期限に守秘義務を負う】ものとする。』\n守秘義務存続期間：営業秘密の守秘期間を選択してください。", [("expire_after_3_years_from_termination", "契約終了の日から起算して満3年間存続する"), ("indefinite_obligation_until_public", "公知となるまで期間の定めなく無期限に守秘する"), ("leak_all_blueprints_on_sns", "SNSで設計図を全世界に無料公開する")], "expire_after_3_years_from_termination", "indefinite_obligation_until_public"),
        ("37", "legal_terms", "【一般取引約款第28条（管轄）】『本契約に関して生じた一切の紛争については、【東京地方裁判所を第一審の専属的合意管轄裁判所】とする。』", "管轄裁判所判定：合意管轄裁判所を選択してください。", "【関西支社特約条項第6条】『甲および乙の双方が関西圏に本社を有する場合、第28条にかかわらず【大阪地方裁判所を第一審の専属的合意管轄裁判所】とする。』\n管轄裁判所判定：関西特約時の管轄裁判所を選択してください。", [("exclusive_jurisdiction_tokyo_district", "東京地方裁判所を第一審の専属的合意管轄とする"), ("exclusive_jurisdiction_osaka_district", "大阪地方裁判所を第一審の専属的合意管轄とする"), ("appeal_to_intergalactic_tribunal", "銀河連邦最高法廷へ上訴する")], "exclusive_jurisdiction_tokyo_district", "exclusive_jurisdiction_osaka_district"),
        ("38", "legal_terms", "【反社会的勢力排除条項第18条】『相手方が反社会的勢力であることが判明した場合、何らの催告を要せず【直ちに本契約を即時解除し損害賠償を請求】できるものとする。』", "反社排除解除手続：反社該当時の契約解除方法を選択してください。", "【契約不履行一般条項第17条】『軽微な金銭債務不履行を理由として契約解除を行う場合、相手方に対し【14日間の猶予期間を定めた書面催告】を行わなければならない。』\n解除手続判定：軽微債務不履行時の契約解除方法を選択してください。", [("terminate_immediately_no_notice_anti_social", "催告なしで直ちに即時契約解除し賠償請求する"), ("require_14_day_written_cure_notice", "14日間の猶予期間を定めた事前の書面催告を要する"), ("hire_hitman_to_assassinate_ceo", "刺客を放って相手役員を暗殺する")], "terminate_immediately_no_notice_anti_social", "require_14_day_written_cure_notice"),
        ("39", "legal_terms", "【契約上の地位の移転条項第12条】『当事者は相手方の事前の書面による承諾なく、【本契約上の地位または権利義務を第三者に譲渡・承継できない】。』", "権利譲渡制限：第三者への契約譲渡条件を選択してください。", "【事業統合特約条項第4条】『合併・会社分割その他の事業譲渡に伴う包括承継の場合に限り、相手方の事前承諾を要せず【契約上の地位を新会社へ包括承継可能】とする。』\n権利譲渡制限：事業包括承継時の条件を選択してください。", [("prohibit_transfer_without_written_consent", "相手方の事前書面承諾なき譲渡・承継を禁止する"), ("allow_transfer_via_merger_without_consent", "事業承継・合併に伴う包括承継は承諾不要で可能"), ("sell_contract_in_pawn_shop", "質屋に契約書を質入れして換金する")], "prohibit_transfer_without_written_consent", "allow_transfer_via_merger_without_consent"),
        ("40", "legal_terms", "【品質保証条項第10条】『納入機器に瑕疵が発見された場合、納入後【1年間の無償修理または良品交換保証】を適用するものとする。』", "品質保証期間：機器の無償保証期間を選択してください。", "【特売免責条項第3条】『特別値引きのアウトレット品については、第10条の保証は適用されず【現状有姿（AS IS）での引き渡しとし品質保証を免責】する。』\n品質保証期間：アウトレット品の保証条件を選択してください。", [("provide_1_year_free_repair_warranty", "納入後1年間の無償修理・良品交換を保証する"), ("deliver_as_is_with_no_warranty", "現状有姿での引き渡しとし品質保証を一切免責する"), ("detonate_equipment_upon_delivery", "納品完了と同時に機器を自爆させる")], "provide_1_year_free_repair_warranty", "deliver_as_is_with_no_warranty"),

        # Pattern 5: Internal Memo (10 pairs: 41-50)
        ("41", "internal_memo", "【総務部通達】『クールビズ実施について。5月1日より9月30日までの期間、【ノーネクタイ・ノージャケット軽装での執務を推奨】いたします。』", "ドレスコード規定：夏季の推奨服装を選択してください。", "【総務部通達】『重要式典開催に伴うドレスコード指定について。創立記念式典当日は、クールビズ期間中であっても【正装（濃紺・黒のスーツおよびネクタイ着用）】を義務付けます。』\nドレスコード規定：式典当日の指定服装を選択してください。", [("recommend_cool_biz_casual", "ノーネクタイ・ノージャケットの軽装を推奨する"), ("mandate_formal_suit_and_tie", "正装（スーツおよびネクタイ着用）を義務付ける"), ("wear_swimsuit_to_boardroom", "役員会に水着で出席する")], "recommend_cool_biz_casual", "mandate_formal_suit_and_tie"),
        ("42", "internal_memo", "【情報セキュリティ通知】『USBメモリの私物持ち込みは【原則全面禁止】とします。業務上どうしても必要な場合は情シス課長承認の暗号化USBのみ貸与します。』", "外部メディア管理：私物USBの取り扱いを選択してください。", "【情シス通知】『客先オンサイト環境（インターネット完全隔離環境）へのデータ移行に限り、【事前申請済みの承認暗号化USBの利用を許可】します。』\n外部メディア管理：承認済みUSBの取り扱いを選択してください。", [("prohibit_all_personal_usb_media", "私物USBメモリの持ち込み・使用を全面禁止する"), ("permit_preapproved_encrypted_usb", "事前申請済みの承認暗号化USBに限り利用を許可する"), ("swallow_usb_stick_whole", "USBメモリを丸呑みして体内に隠す")], "prohibit_all_personal_usb_media", "permit_preapproved_encrypted_usb"),
        ("43", "internal_memo", "【人事労務部回覧】『残業申請ルール厳格化について。18時以降の残業は【前日17時までの事前承認制】とし、当日突発の残業は原則認めません。』", "残業手続ルール：残業申請の期限を選択してください。", "【人事労務部回覧】『システム障害・重大インシデント対応時に限り、事前の残業申請を免除し【翌営業日午前中の事後残業申請を認める】特例措置を適用します。』\n残業手続ルール：緊急障害時の残業手続を選択してください。", [("require_prior_approval_by_yesterday", "前日17時までの事前残業申請を必須とする"), ("allow_post_incident_next_day_approval", "緊急障害時は翌営業日午前中の事後申請を認める"), ("work_72_hours_without_sleep", "72時間不眠不休で強制労働させる")], "require_prior_approval_by_yesterday", "allow_post_incident_next_day_approval"),
        ("44", "internal_memo", "【経理部通知】『領収書精算の電子化について。今月より紙の領収書提出は廃止し、【スマホでスキャンした電子領収書画像アップロードのみ受付】とします。』", "精算提出形式：領収書の提出方式を選択してください。", "【経理部通知】『税務監査対応のため、10万円以上の高額領収書に関しては電子スキャンに加え【原本の紙面領収書も糊付け台帳にて要提出】となります。』\n精算提出形式：高額領収書の提出方式を選択してください。", [("accept_electronic_scan_upload_only", "スマホスキャンの電子画像アップロードのみ受付"), ("require_both_scan_and_original_paper", "電子スキャンに加え原本紙面領収書も要提出"), ("burn_receipts_in_wastebasket", "領収書をごみ箱で燃やす")], "accept_electronic_scan_upload_only", "require_both_scan_and_original_paper"),
        ("45", "internal_memo", "【安全衛生委員会】『社内インフルエンザ感染拡大防止のため、発熱（37.5℃以上）が確認された従業員は【解熱後48時間経過まで出社停止】とします。』", "就業制限判定：発熱時の就業可能時期を選択してください。", "【安全衛生委員会】『無症状の濃厚接触者につきましては、毎朝の抗原定性検査で陰性が確認できれば【出社停止とせず通常通り出勤可能】といたします。』\n就業制限判定：無症状濃厚接触者の就業判定を選択してください。", [("suspend_attendance_until_48h_afebrile", "解熱後48時間経過まで出社停止とする"), ("permit_work_with_negative_antigen_test", "抗原検査陰性を条件に通常通り出勤可能とする"), ("quarantine_employee_on_desert_island", "無人島へ従業員を永久隔離する")], "suspend_attendance_until_48h_afebrile", "permit_work_with_negative_antigen_test"),
        ("46", "internal_memo", "【総務人事通達】『有給休暇の取得手続について。原則として【取得希望日前週の金曜日17時までに勤怠システムにて申請】を行ってください。』", "有休申請期限：通常の有給休暇申請期限を選択してください。", "【総務人事通達】『急病等の突発事由による当日有給休暇の取得について。当日の【始業時刻（午前9時）までに直属上長へ電話連絡】すれば事後申請を認めます。』\n有休申請期限：突発的な病欠時の有休連絡期限を選択してください。", [("apply_by_previous_friday_17pm", "前週金曜日17時までに勤怠システムで事前申請する"), ("notify_manager_by_9am_same_day", "当日始業時刻（午前9時）までに上長へ電話連絡する"), ("disappear_without_notice_for_a_month", "無断欠勤のまま1か月間消息を絶つ")], "apply_by_previous_friday_17pm", "notify_manager_by_9am_same_day"),
        ("47", "internal_memo", "【社内公募ガイドライン】『次期海外プロジェクト公募要件：現部署での【勤続2年以上かつ直近の人事評価がB以上】の正社員を対象とします。』", "社内公募要件：通常の応募資格基準を選択してください。", "【社内公募特則】『戦略特命案件について。本案件に限り勤続年数基準を撤廃し、【本部長の推薦状を提出した者であれば年数不問で応募可能】とします。』\n社内公募要件：特命案件の応募資格基準を選択してください。", [("require_2_years_service_and_grade_b", "現部署勤続2年以上かつ直近評価B以上を必須とする"), ("allow_any_tenure_with_division_recommendation", "本部長推薦状があれば勤続年数不問で応募可能"), ("kidnap_interviewer_family", "面接官の家族を人質に取って応募する")], "require_2_years_service_and_grade_b", "allow_any_tenure_with_division_recommendation"),
        ("48", "internal_memo", "【情報システム部告知】『社内コミュニケーションツールの運用統一について。全社に向けた公式アナウンスは【Slackの #general チャンネルへの投稿のみを公式通達と認定】します。』", "公式発信基準：全社公式アナウンスの媒体を選択してください。", "【緊急時連絡網ポリシー】『全社システム障害等によりSlackが利用不能となった場合に限り、【緊急安否確認メールシステムによる一斉配信】を公式連絡とします。』\n公式発信基準：Slack障害時の公式発信媒体を選択してください。", [("broadcast_via_slack_general_channel", "Slackの #general チャンネル投稿を公式認定する"), ("broadcast_via_emergency_safety_mail", "緊急安否確認メールシステムの一斉配信を使用する"), ("write_message_on_pigeon_carrier", "伝書鳩の足に手紙を結んで飛ばす")], "broadcast_via_slack_general_channel", "broadcast_via_emergency_safety_mail"),
        ("49", "internal_memo", "【テレワーク環境支援制度】『在宅勤務環境改善のため、外部モニターや椅子の購入費用として【年度あたり上限3万円の実費補助（領収書精算）】を支給します。』", "テレワーク補助形態：什器購入補助の支給方法を選択してください。", "【新入社員特別支援】『今年度新入社員に対しては、個別領収書精算ではなく【会社指定の高機能モニターおよびヘッドセットの現物無償貸与】を行います。』\nテレワーク補助形態：新入社員向け支援形態を選択してください。", [("reimburse_actual_costs_up_to_30k", "年度あたり上限3万円の実費補助（領収書精算）"), ("distribute_designated_hardware_loan", "会社指定のモニター・ヘッドセットの現物無償貸与"), ("sell_employee_personal_belongings", "社員の私物を勝手にフリーマーケットで売却する")], "reimburse_actual_costs_up_to_30k", "distribute_designated_hardware_loan"),
        ("50", "internal_memo", "【健康増進オフィス規程】『敷地内喫煙ルールの改定について。受動喫煙防止のため、【加熱式たばこを含め敷地内全面禁煙（禁煙エリア）】に指定します。』", "社内喫煙ルール：敷地内での喫煙規制範囲を選択してください。", "【工場敷地内喫煙ルール】『製造工場敷地内においては、防爆エリア外の【屋外指定喫煙専用室内に限り排煙設備稼働下での喫煙を許可】します。』\n社内喫煙ルール：工場敷地内の喫煙許可範囲を選択してください。", [("enforce_total_smoking_ban_including_vape", "加熱式たばこを含め敷地内を完全全面禁煙とする"), ("permit_smoking_inside_designated_outdoor_room", "屋外の指定喫煙専用室内に限り喫煙を許可する"), ("smoke_inside_chemical_explosives_store", "火薬保管庫の真上で花火に点火する")], "enforce_total_smoking_ban_including_vape", "permit_smoking_inside_designated_outdoor_room"),

        # Pattern 6: SOP Procedure (10 pairs: 51-60)
        ("51", "sop_procedure", "【薬品充填SOP】『ステップ1：ノズルを70%エタノールで清拭。ステップ2：充填量を500mlにキャリブレーション。ステップ3：【全自動充填ボタンを押下】してボトル充填開始。』", "充填操作指示：キャリブレーション完了後の次手順を選択してください。", "【薬品充填SOP】『安全インターロック作動時：充填中に重量リミット超過（520ml超）を検知した場合は、ステップ3を即座に中断し【充填バルブを手動緊急閉止】すること。』\n充填操作指示：重量超過時の緊急手順を選択してください。", [("push_automatic_fill_button", "全自動充填ボタンを押下して充填を開始する"), ("manually_close_emergency_fill_valve", "充填バルブを手動で即時緊急閉止する"), ("drink_chemical_solution_directly", "充填薬液を直接ストローで飲む")], "push_automatic_fill_button", "manually_close_emergency_fill_valve"),
        ("52", "sop_procedure", "【高所作業車SOP】『作業開始前手順：アウトリガー（支持脚）を最大幅まで張り出し、【車輪が地面から完全に浮いた水平状態】を確認した後にブームを上昇させること。』", "アウトリガー確認：ブーム上昇前の必須条件を選択してください。", "【高所作業車SOP】『強風時作業中止基準：瞬間風速が10m/sを超えた場合は、直ちに作業を中断し【ブームを最下部格納位置まで降下】させエンジンを停止すること。』\n強風時対応：風速10m/s超過時の対応を選択してください。", [("verify_wheels_lifted_horizontally", "車輪が完全に浮いた水平状態を確認する"), ("lower_boom_to_lowest_stowed_position", "ブームを最下部格納位置まで降下させ停止する"), ("jump_from_work_platform_to_ground", "高所バケットから地上へ飛び降りる")], "verify_wheels_lifted_horizontally", "lower_boom_to_lowest_stowed_position"),
        ("53", "sop_procedure", "【超音波探傷検査SOP】『校正標準試験片（STB-G）を用い、測定ゲインを調整して【エコー高さをスクリーンの80%に較正】した後に実機溶接部の探傷を開始する。』", "探傷較正手順：較正時のエコー高さ目標を選択してください。", "【超音波探傷検査SOP】『実機探傷中にエコー高さが第3評価ライン（F線）を超過する欠陥波形を検知した場合は、【即座に不適合マーキングを施し再検査判定】とする。』\n欠陥検出対応：F線超過時の処置を選択してください。", [("calibrate_echo_height_to_80pct", "エコー高さをスクリーンの80%に較正する"), ("mark_nonconformity_and_order_retest", "不適合マーキングを施し再検査判定とする"), ("erase_flaw_echo_with_whiteout", "画面の欠陥波形を修正液で消す")], "calibrate_echo_height_to_80pct", "mark_nonconformity_and_order_retest"),
        ("54", "sop_procedure", "【高圧蒸気滅菌器（オートクレーブ）SOP】『標準滅菌サイクル：チャンバー内を【121℃・20分間維持】し、滅菌完了後は内圧が0kPaまで下がるのを待ってドアを開ける。』", "標準滅菌条件：通常器具の滅菌条件を選択してください。", "【高圧蒸気滅菌器SOP】『プリオン病原体等汚染器具の特別滅菌サイクル：標準サイクルではなく【134℃・18分間の高圧過熱滅菌】を実行すること。』\n特別滅菌条件：高リスク病原体の滅菌条件を選択してください。", [("run_standard_cycle_121c_20min", "121℃・20分間の標準滅菌サイクルを実行する"), ("run_prion_cycle_134c_18min", "134℃・18分間のプリオン特別滅菌サイクルを実行する"), ("submerge_autoclave_in_lake", "オートクレーブ本体を湖に沈める")], "run_standard_cycle_121c_20min", "run_prion_cycle_134c_18min"),
        ("55", "sop_procedure", "【産業廃棄物マニフェストSOP】『運搬受領時：収集運搬業者はA票を控えとして手元に残し、【B1票・B2票・C1票・C2票・D票・E票を中間処理業者へ引き渡す】こと。』", "マニフェスト受渡：運搬業者が中間処理へ渡す伝票を選択してください。", "【産業廃棄物マニフェストSOP】『最終処分完了時：処分業者は最終処分が終了した日から10日以内に、【処分終了を記載したE票を排出事業者へ返送】すること。』\nマニフェスト返送：最終処分完了時に排出者へ送る伝票を選択してください。", [("hand_over_b_to_e_manifest_slips", "B1〜E票の伝票を中間処理業者へ引き渡す"), ("return_completed_slip_e_to_generator", "処分終了記載のE票を排出事業者へ返送する"), ("burn_all_manifests_to_destroy_evidence", "証拠隠滅のためマニフェストを全焼却する")], "hand_over_b_to_e_manifest_slips", "return_completed_slip_e_to_generator"),
        ("56", "sop_procedure", "【無菌クリーンルーム退出SOP】『退出手順：防塵服を脱ぐ前に【エアシャワーボックス内で15秒間の除塵気流】を受け、その後脱衣室へ移動すること。』", "クリーンルーム退出：必須の除塵手順を選択してください。", "【非常脱出時SOP】『火災警報発令時：エアシャワー手順は一切省略し、【非常口ドアを手動開放して直ちに屋外へ避難】すること。命を最優先とする。』\nクリーンルーム退出：火災警報時の避難手順を選択してください。", [("undergo_15_second_air_shower", "エアシャワー内で15秒間の除塵を受けてから退出"), ("evacuate_immediately_skipping_shower", "除塵を省略し非常口から直ちに屋外へ避難する"), ("lock_all_emergency_exits_permanently", "全非常口を外側から溶接して脱出不能にする")], "undergo_15_second_air_shower", "evacuate_immediately_skipping_shower"),
        ("57", "sop_procedure", "【データベースパッチ適用SOP】『事前保護手順：パッチ適用コマンドを実行する直前に、【ストレージスナップショットを必ず完全取得】しリストアポイントを作成すること。』", "パッチ前必須作業：パッチ適用前の保護手順を選択してください。", "【緊急脆弱性ゼロデイ対応SOP】『本番停止を防ぐための緊急パッチにおいて、バックアップ領域枯渇時は【事前スナップショットをスキップし即時パッチ適用】を例外的に承認する。』\nパッチ前必須作業：緊急領域枯渇時の対応を選択してください。", [("take_full_storage_snapshot_prior", "実行直前にストレージスナップショットを完全取得する"), ("skip_snapshot_and_apply_immediately", "スナップショットをスキップし即時パッチ適用する"), ("delete_all_primary_databases", "メインデータベースを全行無条件DELETEする")], "take_full_storage_snapshot_prior", "skip_snapshot_and_apply_immediately"),
        ("58", "sop_procedure", "【フォークリフト始動前点検SOP】『毎朝の運行前点検：ブレーキの効き・ホーンの吹鳴・油圧シリンダの油漏れ有無を点検し、【始動前点検チェック表へ押印記録】すること。』", "日常点検指示：毎朝の始動前点検手順を選択してください。", "【フォークリフト定期整備SOP】『月次定期点検：毎朝の日常点検項目に加え、【マストチェーンのテンション測定および給油グリスアップ】を実施すること。』\n日常点検指示：月次定期点検の追加手順を選択してください。", [("inspect_brakes_horn_and_sign_log", "毎朝のブレーキ・ホーン確認を実施し記録表へ押印"), ("measure_chain_tension_and_lubricate", "マストチェーンのテンション測定と給油を実施する"), ("drive_forklift_off_high_cliff", "フォークリフトで崖からダイブする")], "inspect_brakes_horn_and_sign_log", "measure_chain_tension_and_lubricate"),
        ("59", "sop_procedure", "【濃硫酸希釈混合SOP】『安全混合規則：発熱による突沸・飛散を防ぐため、【必ず純水の中に濃硫酸を攪拌しながら少量ずつ徐々に滴下投入】すること。』", "薬品混合手順：安全な濃硫酸希釈手順を選択してください。", "【希釈液中和SOP】『廃液処理手順：酸性廃液のpHを中和するため、【水酸化ナトリウム希釈液をpHが6〜8に安定するまで滴下】すること。』\n廃液中和手順：酸性廃液の中和処理を選択してください。", [("pour_sulfuric_acid_slowly_into_water", "純水の中に濃硫酸を少量ずつ徐々に滴下投入する"), ("add_sodium_hydroxide_until_ph_neutral", "水酸化ナトリウムを滴下しpH6〜8へ中和する"), ("pour_water_directly_into_hot_acid", "高熱濃硫酸に一気に水道水を注ぎ込む")], "pour_sulfuric_acid_slowly_into_water", "add_sodium_hydroxide_until_ph_neutral"),
        ("60", "sop_procedure", "【機密書類破棄SOP】『機密廃棄手順：個人情報記載文書は社内シュレッダーで細断後、【産業廃棄物業者による溶解処理証明書を受領】して完了とする。』", "書類廃棄手順：機密文書の廃棄手続きを選択してください。", "【一般社内報廃棄SOP】『公開情報印刷物：機密指定のない社内報やパンフレットの余剰分は、【古紙リサイクル回収BOXへ直接投入】して資源回収に回すこと。』\n書類廃棄手順：一般広報物の廃棄手続きを選択してください。", [("shred_and_obtain_melting_certificate", "シュレッダー細断のうえ溶解処理証明書を受領する"), ("place_in_paper_recycling_box_directly", "古紙リサイクル回収BOXへ直接投入する"), ("scatter_documents_from_rooftop", "ビルの屋上から重要文書をバラ撒く")], "shred_and_obtain_melting_certificate", "place_in_paper_recycling_box_directly"),

        # Pattern 7: Spoken Meeting (10 pairs: 61-70)
        ("61", "spoken_meeting", "【プロジェクト打ち合わせ発言】『えー、議事録確認しますね。A案のデザイン刷新とB案の機能追加ですが、田中専務から「納期を最優先に」とのお達しがありましたので、今回は【開発工数の短いB案を採択】ということで合意形成でよろしいですかね。』", "採択案判定：会議で合意されたプロジェクト案を選択してください。", "【プロジェクト打ち合わせ発言】『あ、ちょっと待ってください！先ほどマーケの鈴木部長から内線入って、「競合が来月類似機能を出してくるから、工数かかっても【差別化できるA案デザイン刷新】に方針転換してほしい」とのことです。A案採用でひっくり返します！』\n採択案判定：会議で合意されたプロジェクト案を選択してください。", [("adopt_plan_b_short_leadtime", "工数が短いB案（機能追加）を採択する"), ("adopt_plan_a_design_refresh", "差別化できるA案（デザイン刷新）を採択する"), ("fire_all_software_engineers", "全エンジニアを即時懲戒解雇する")], "adopt_plan_b_short_leadtime", "adopt_plan_a_design_refresh"),
        ("62", "spoken_meeting", "【役員会合意録】『海外拠点展開について議論がまとまりました。為替リスクと現地サプライチェーンを考慮し、来期は【ベトナム・ハノイ工場への新設投資】を優先実行いたします。』", "海外進出先選定：決定された投資先拠点を選択してください。", "【役員会合意録】『先ほどのベトナム案件ですが、現地の法改正により外資出資比率規制が急遽厳格化されたとの速報が入りました。リスクが高すぎるため、投資先を【タイ・アユタヤ既存工場のライン増強】へ変更決定といたします。』\n海外進出先選定：決定された投資先拠点を選択してください。", [("invest_in_hanoi_vietnam_plant", "ベトナム・ハノイ新工場への新設投資を実行する"), ("expand_ayutthaya_thailand_line", "タイ・アユタヤ既存工場のライン増強へ変更する"), ("buy_private_island_for_ceo", "社長個人用の無人島を会社資金で購入する")], "invest_in_hanoi_vietnam_plant", "expand_ayutthaya_thailand_line"),
        ("63", "spoken_meeting", "【開発定例MTG】『えーっと、次期スマホアプリの対応OSバージョンですが、古い端末のサポートコストを削減したいので【iOS 16以降およびAndroid 13以降に限定】という方針で固めましょう。』", "対応OS決定：合意されたサポート対象OSを選択してください。", "【開発定例MTG】『さっきのOS切り捨ての件、営業から「地方自治体の導入端末にAndroid 11がまだ大量に残っている」と強い要望が出ました。やむを得ないので【Android 11以降までサポート範囲を拡大維持】します。』\n対応OS決定：合意されたサポート対象OSを選択してください。", [("restrict_to_ios16_and_android13", "iOS 16以降およびAndroid 13以降に限定する"), ("broaden_support_to_include_android11", "Android 11以降までサポート範囲を拡大維持する"), ("port_app_to_msdos_floppy", "MS-DOS用フロッピーディスクに移植する")], "restrict_to_ios16_and_android13", "broaden_support_to_include_android11"),
        ("64", "spoken_meeting", "【調達購買会議】『半導体部材の調達先ですが、サプライチェーン単一化を避けるため、メインサプライヤーのA社から60%、【サブのB社から40%の複数購買】で発注契約を締結します。』", "調達方針決定：合意された購買比率を選択してください。", "【調達購買会議】『B社から連絡があり、工場火災で向こう半年の供給が絶望的とのことです。緊急措置として、今回はリスク分散を諦めて【A社へ100%全量集中発注】に切り替えます。』\n調達方針決定：合意された購買比率を選択してください。", [("split_sourcing_60_40_ratio", "A社60%・B社40%の複数購買で発注する"), ("consolidate_100pct_to_vendor_a", "A社へ100%全量集中発注に切り替える"), ("smuggle_semiconductors_in_luggage", "密輸品をスーツケースで買い付ける")], "split_sourcing_60_40_ratio", "consolidate_100pct_to_vendor_a"),
        ("65", "spoken_meeting", "【広報危機管理会議】『新製品の不具合報道についてですが、隠蔽と受け取られるのを防ぐため、明日の朝一番で【記者会見を開いて全情報と回収方針を全面開示】しましょう。』", "記者発表方針：合意された広報対応を選択してください。", "【広報危機管理会議】『さっきの記者会見ですが、顧問弁護士から「法的な原因特定が済んでいない段階での会見は訴訟リスクが極めて高い」と制止されました。会見は見送り【公式Webサイトでの事実経過リリース掲載のみ】に留めます。』\n記者発表方針：合意された広報対応を選択してください。", [("hold_press_conference_full_disclosure", "記者会見を開き全面開示と自主回収を発表する"), ("publish_web_statement_only", "記者会見は見送り公式Webリリース掲載のみとする"), ("threaten_journalists_with_violence", "取材記者を暴力で脅迫する")], "hold_press_conference_full_disclosure", "publish_web_statement_only"),
        ("66", "spoken_meeting", "【進捗定例会議】『納期の件ですが、クライアントから仕様追加の要望が重なっています。品質を妥協するわけにはいかないので、【顧客合意を取り付けた上でリリース日を2週間延期】しましょう。』", "納期調整方針：定例で合意された納期対応を選択してください。", "【進捗定例会議】『先ほどの延期案ですが、役員会から「他社より先に市場投入しなければ事業戦略が破綻する」と厳命が下りました。【他チームからシニアエンジニア3名を緊急アサインし納期を死守】します！』\n納期調整方針：定例で合意された納期対応を選択してください。", [("postpone_release_date_by_2_weeks", "顧客合意の上でリリース日を2週間延期する"), ("reinforce_senior_engineers_keep_deadline", "シニアエンジニアを緊急増員し納期を死守する"), ("assassinate_client_project_manager", "クライアントの担当者を暗殺する")], "postpone_release_date_by_2_weeks", "reinforce_senior_engineers_keep_deadline"),
        ("67", "spoken_meeting", "【デザイン検討会】『今回の医療従事者向けダッシュボードですが、緊急時の誤認を防ぐことが最優先です。見た目の華やかさよりも【視認性とアクセシビリティ重視のハイコントラストUI】に決定します。』", "デザイン方針合意：UIの採用方針を選択してください。", "【デザイン検討会】『若年層向け新規ブランドアプリのUI方針ですが、競合との差別化のため最新の流行を取り入れ、【半透明のすりガラス風グラスモーフィズムデザイン】を全面採用することになりました。』\nデザイン方針合意：UIの採用方針を選択してください。", [("adopt_high_contrast_accessible_ui", "視認性とアクセシビリティ重視のUIを採用する"), ("adopt_frosted_glassmorphism_design", "すりガラス風グラスモーフィズムデザインを採用する"), ("render_entire_ui_in_solid_black", "画面全体を真っ黒にして文字を一切見えなくする")], "adopt_high_contrast_accessible_ui", "adopt_frosted_glassmorphism_design"),
        ("68", "spoken_meeting", "【アーキテクチャ選定会議】『新サービスのデータ永続化基盤ですが、複雑なリレーショナル結合クエリとACIDトランザクションが不可欠なので、【PostgreSQLをメインデータベースに選定】します。』", "DB選定決定：採択されたデータベースを選択してください。", "【アーキテクチャ選定会議】『IoTセンサーデータの毎秒数十万件の書き込みストリームを捌くため、リレーショナルではなく【分散キーバリューストアのApache Cassandraを採用】することに決定しました。』\nDB選定決定：採択されたデータベースを選択してください。", [("select_postgresql_for_acid_transactions", "PostgreSQLをメインデータベースに選定する"), ("select_cassandra_for_high_write_throughput", "分散KVSのApache Cassandraを採用する"), ("store_all_records_in_paper_notebooks", "全データを手書きの大学ノートにボールペンで記録する")], "select_postgresql_for_acid_transactions", "select_cassandra_for_high_write_throughput"),
        ("69", "spoken_meeting", "【DevOps改善MTG】『リグレッションバグの流出を防ぐため、今後は【すべてのプルリクエストに対してE2E自動テストの全件通過を必須化】します。』", "テストパイプライン方針：CIでのテスト実行基準を選択してください。", "【DevOps改善MTG】『PRごとの全件E2Eテストは待ち時間が長すぎて開発効率が激減しています。PR時は単体テストのみとし、【E2Eテストは毎晩の夜間定期バッチ実行に集約】する方針に見直します。』\nテストパイプライン方針：CIでのテスト実行基準を選択してください。", [("mandate_full_e2e_tests_for_every_pr", "全プルリクエストでE2Eテスト全件通過を必須化する"), ("relegate_e2e_tests_to_nightly_batch", "PR時は単体のみとしE2Eは夜間定期バッチに集約する"), ("delete_all_automated_unit_tests", "全単体テストコードをGitから完全削除する")], "mandate_full_e2e_tests_for_every_pr", "relegate_e2e_tests_to_nightly_batch"),
        ("70", "spoken_meeting", "【ユーザーカンファレンス企画】『今年の年次デベロッパーカンファレンスですが、地方や海外からの参加者を最大化するため【完全オンライン配信（ウェビナー形式）】での開催を決定します。』", "イベント開催形態：合意されたカンファレンス形式を選択してください。", "【ユーザーカンファレンス企画】『スポンサー各社から「直接開発者と名刺交換やネットワーキングができる場を設けてほしい」との強い要請がありました。【現地会場での対面展示を併設したハイブリッド開催】へ変更します。』\nイベント開催形態：合意されたカンファレンス形式を選択してください。", [("host_full_online_webinar_event", "完全オンライン配信（ウェビナー形式）で開催する"), ("host_hybrid_event_with_in_person_venue", "現地会場での対面展示を併設したハイブリッド開催とする"), ("cancel_conference_and_insult_users", "イベントを突然中止して参加希望者を愚弄する")], "host_full_online_webinar_event", "host_hybrid_event_with_in_person_venue"),

        # Pattern 8: Keigo / Polite (10 pairs: 71-80)
        ("71", "keigo_polite", "【敬語文】『平素は格別のご高配を賜り厚く御礼申し上げます。ご依頼いただきました技術顧問就任の件、甚だ微力ではございますが【謹んでお引き受けいたしたく存じます】。』", "受諾可否判定：顧問就任の返答を選択してください。", "【敬語文】『平素は格別のご高配を賜り厚く御礼申し上げます。誠に光栄なお話ではございますが、現職の兼業規程に抵触いたしますため、断腸の思いながら【ご辞退申し上げざるを得ません】。何卒ご海容のほどお願い申し上げます。』\n受諾可否判定：顧問就任の返答を選択してください。", [("respectfully_accept_appointment", "謹んで就任依頼をお引き受けする"), ("regretfully_decline_appointment", "兼業抵触のため遺憾ながら辞退申し上げる"), ("leak_confidential_files_to_press", "依頼元の機密文書を週刊誌へ売却する")], "respectfully_accept_appointment", "regretfully_decline_appointment"),
        ("72", "keigo_polite", "【敬語文】『拝啓。貴社ますますご隆盛のこととお慶び申し上げます。新社屋落成式典のご案内を賜り誠に光栄に存じます。当日は代表取締役の山田が【喜んでご出席させていただきます】。』", "出欠判定：式典への出欠回答を選択してください。", "【敬語文】『拝啓。新社屋落成式典のご案内をいただき深謝申し上げます。生憎当日は海外出張と重なっておりまして、甚だ非礼とは存じますが【欠席のお返事を差し上げたく存じます】。ご盛会を祈念申し上げます。』\n出欠判定：式典への出欠回答を選択してください。", [("gladly_attend_ceremony", "代表取締役が喜んで式典に出席する"), ("respectfully_absent_due_to_travel", "海外出張のため失礼ながら欠席申し上げる"), ("demolish_new_building_overnight", "新社屋を一晩で解体倒壊させる")], "gladly_attend_ceremony", "respectfully_absent_due_to_travel"),
        ("73", "keigo_polite", "【敬語文】『お伺い申し上げます。過日ご提出いただきました仕様変更見積書につきまして、弊社取締役会にて審議の結果【満場一致にて原案通り承認の運びとなりました】。ご手配のほどお願い申し上げます。』", "見積審議判定：見積書の決裁結果を選択してください。", "【敬語文】『お伺い申し上げます。ご提示の見積書につきまして社内にて慎重に検討を重ねましたところ、昨今の業績悪化を鑑み【誠に不本意ながら今回は見送りとさせていただきたく存じます】。ご容赦のほどお願い申し上げます。』\n見積審議判定：見積書の決裁結果を選択してください。", [("unanimously_approve_quotation", "満場一致にて原案通り見積もりを承認する"), ("regretfully_reject_quotation", "業績悪化を鑑み誠に不本意ながら見送る"), ("forge_signature_of_ceo", "社長の印鑑を偽造して勝手に契約する")], "unanimously_approve_quotation", "regretfully_reject_quotation"),
        ("74", "keigo_polite", "【敬語文】『先生におかれましてはご健勝のことと存じます。来月開催の学術シンポジウムにて、ぜひ基調講演の労を【賜りたく存じ上げます】。ご多忙中恐縮ながらご快諾いただけますと幸甚に存じます。』", "講演依頼判定：講演依頼の可否を選択してください。", "【敬語文】『ご案内をいただき恐縮に存じます。あいにくその期間は海外学会の座長を務める予定が入っておりまして、まことに心苦しい限りですが【ご期待に沿いかねる次第でございます】。』\n講演依頼判定：講演依頼の可否を選択してください。", [("request_keynote_speech_honor", "基調講演の登壇を正式に依頼する"), ("decline_speech_due_to_clashing_schedule", "先約重複のため遺憾ながら辞退する"), ("ban_professor_from_all_universities", "教授を全世界の大学から追放する")], "request_keynote_speech_honor", "decline_speech_due_to_clashing_schedule"),
        ("75", "keigo_polite", "【敬語文】『お客様各位。長らくご愛顧賜りました旧型ポイントサービスでございますが、この度新システムへの統合に伴い【全ポイントを無条件で新ポイントへ等価交換させていただきます】。』", "ポイント移行判定：ポイントの移行処理を選択してください。", "【敬語文】『お客様各位。誠に遺憾ではございますが、長らくご利用いただきましたプレミアム会員割引サービスは、諸般の事情により来月末をもちまして【サービス提供を完全終了とさせていただきます】。』\nサービス存廃判定：プレミアム割引の取り扱いを選択してください。", [("convert_points_to_new_system", "全ポイントを新システムへ等価交換する"), ("terminate_service_completely", "来月末をもってサービス提供を完全終了する"), ("charge_customers_million_yen_fee", "会員全員から100万円の罰金を徴収する")], "convert_points_to_new_system", "terminate_service_completely"),
        ("76", "keigo_polite", "【取材依頼への返信】『拝復。貴誌からの取材のご依頼、大変光栄に存じます。弊社代表の山田も喜んでお受けいたしたく存じますので、【来週水曜日14時にてインタビューの日程を設定】させていただければと存じます。』", "取材受諾可否：取材依頼への回答方針を選択してください。", "【取材依頼への返信】『拝復。ご丁重なご依頼を賜り感謝申し上げます。誠に恐縮ながら、当件は現在特許出願の係争中につき機密性が高く、【甚だ不本意ながら今回は取材のご辞退を申し上げたく存じます】。』\n取材受諾可否：取材依頼への回答方針を選択してください。", [("accept_interview_schedule_next_wednesday", "取材を快諾し来週水曜日の日程を設定する"), ("respectfully_decline_due_to_patent_secrecy", "特許係争中のため遺憾ながら取材を辞退申し上げる"), ("detonate_dynamite_at_press_office", "出版社本社にダイナマイトを仕掛ける")], "accept_interview_schedule_next_wednesday", "respectfully_decline_due_to_patent_secrecy"),
        ("77", "keigo_polite", "【役員歓送迎会案内への返答】『幹事の皆様、連日のご差配誠にありがとうございます。山田でございます。当日は【是非とも出席させていただき、皆様と親睦を深めたく存じます】。会費は当日受付にてお納めいたします。』", "懇親会出欠表明：歓送迎会への出欠を選択してください。", "【役員歓送迎会案内への返答】『幹事の皆様、ご案内痛み入ります。生憎当夜は兼ねてより所用がございまして、万障繰り合わせましたが都合がつかず、【無念ながら欠席の御礼を申し上げます】。盛会を心よりお祈り申し上げます。』\n懇親会出欠表明：歓送迎会への出欠を選択してください。", [("joyfully_attend_farewell_party", "喜んで歓送迎会に出席を表明する"), ("regretfully_absent_due_to_prior_engagement", "先約都合のため遺憾ながら欠席申し上げる"), ("burn_down_the_restaurant_venue", "宴会場のレストランを放火炎上させる")], "joyfully_attend_farewell_party", "regretfully_absent_due_to_prior_engagement"),
        ("78", "keigo_polite", "【共同研究提案への回答】『大学産学連携本部様。ご提案書を拝読いたしました。弊社の次世代バッテリー開発方針と見事に合致しておりますので、【ぜひ前向きに共同研究契約の締結に向け協議を進めたく存じます】。』", "共同研究受託可否：提案に対する回答姿勢を選択してください。", "【共同研究提案への回答】『大学産学連携本部様。貴重なご提案を賜り厚く御礼申し上げます。社内技術委員会にて慎重に検討いたしましたところ、自社競合技術との重複が判明し、【誠に残念ながら本件の採用は見送らせていただく運びとなりました】。』\n共同研究受託可否：提案に対する回答姿勢を選択してください。", [("positively_advance_joint_research_agreement", "前向きに共同研究契約の締結協議を進める"), ("regretfully_decline_joint_research_proposal", "自社技術重複のため誠に残念ながら見送る"), ("sue_the_university_for_copyright", "大学を特許侵害で無根拠に提訴する")], "positively_advance_joint_research_agreement", "regretfully_decline_joint_research_proposal"),
        ("79", "keigo_polite", "【支払条件交渉への回答】『お取引先様各位。資材前払いのご要望につきまして、昨今の原材料高騰の実情を鑑み、【今回に限り全額事前前払いの条件を謹んで承諾申し上げます】。』", "支払条件受諾：代金決済条件の合意内容を選択してください。", "【支払条件交渉への回答】『お取引先様各位。前払いのご要望につきましては社内与信管理規程上認めることが叶いません。【通常通りの月末締め翌月末払いを固持いただけますようお願い申し上げる次第でございます】。』\n支払条件受諾：代金決済条件の合意内容を選択してください。", [("respectfully_accept_advance_payment_terms", "今回に限り全額事前前払いの条件を承諾する"), ("firmly_request_standard_end_of_month_payment", "通常通りの月末締め翌月末払いの維持を要請する"), ("pay_counterparty_in_monopoly_money", "ボードゲームの偽札で代金を支払う")], "respectfully_accept_advance_payment_terms", "firmly_request_standard_end_of_month_payment"),
        ("80", "keigo_polite", "【推薦状依頼への回答】『教え子の山田君へ。大学院進学の推薦状の件、君の研究室での卓越した功績を高く評価しておりますので、【喜んで強力な推薦書をしたため送付させていただきます】。』", "推薦状執筆諾否：推薦状作成の返答を選択してください。", "【推薦状依頼への回答】『山田様。推薦状のご依頼を拝受いたしました。誠に心苦しい限りではございますが、公職倫理規定により特定個人への推薦文作成は禁じられており、【ご要望にお応えいたしかねる旨ご寛恕願いたく存じます】。』\n推薦状執筆諾否：推薦状作成の返答を選択してください。", [("gladly_write_and_send_recommendation", "卓越した功績を認め喜んで推薦状を執筆送付する"), ("decline_recommendation_due_to_ethics_rule", "倫理規程遵守のため遺憾ながら推薦文作成を辞退する"), ("report_student_as_criminal_fugitive", "教え子を指名手配犯として警察へ通報する")], "gladly_write_and_send_recommendation", "decline_recommendation_due_to_ethics_rule"),

        # Pattern 9: Elliptical / Inverted (10 pairs: 81-90)
        ("81", "elliptical_inverted", "【現場会話】『出荷しちゃって大丈夫だよ、伝票のハンコさえ押してあればね。』※伝票には責任者の押印が確認できる。", "出荷可否判定：製品を出荷すべきか選択してください。", "【現場会話】『出荷しちゃって大丈夫だよ、伝票のハンコさえ押してあればね。ただし赤伝票は別だけど。』※対象の伝票は赤伝票である。\n出荷可否判定：製品を出荷すべきか選択してください。", [("proceed_with_shipment", "押印を確認し製品を出荷する"), ("hold_shipment_red_invoice", "赤伝票のため出荷を保留停止する"), ("dump_cargo_into_garbage_compactor", "荷物をゴミ収集パッカー車へ投げ込む")], "proceed_with_shipment", "hold_shipment_red_invoice"),
        ("82", "elliptical_inverted", "【操作手順】『再起動をかけてください、冷却ファンが回り始めたら。先に電源落としちゃダメですよ。』※冷却ファンは現在定格回転中。", "再起動手順判断：システム再起動を実行すべきか選択してください。", "【操作手順】『再起動をかけてください、冷却ファンが回り始めたら。先に電源落としちゃダメですよ。』※冷却ファンは現在完全に停止している。\n再起動手順判断：システム再起動を実行すべきか選択してください。", [("execute_system_reboot_now", "ファン回転確認の上でシステム再起動を実行する"), ("wait_fan_rotation_before_reboot", "ファン未回転のため再起動を見送り待機する"), ("pour_salt_water_on_motherboard", "マザーボードに食塩水を注ぎ込む")], "execute_system_reboot_now", "wait_fan_rotation_before_reboot"),
        ("83", "elliptical_inverted", "【社内指示】『経費で落として構いません、事前に上長の口頭了解さえ取ってあれば。領収書は後回しでいいから。』※上長の口頭了解は昨日取得済み。", "経費精算判断：立替経費を申請できるか選択してください。", "【社内指示】『経費で落として構いません、事前に上長の口頭了解さえ取ってあれば。領収書は後回しでいいから。』※上長への事前相談は一切行っていない。\n経費精算判断：立替経費を申請できるか選択してください。", [("approve_expense_with_verbal_consent", "事前口頭了解ありとして経費精算を認める"), ("deny_expense_lacking_prior_consent", "事前了解がないため経費精算を不可とする"), ("report_to_police_for_embezzlement", "横領未遂として即座に110番通報する")], "approve_expense_with_verbal_consent", "deny_expense_lacking_prior_consent"),
        ("84", "elliptical_inverted", "【整備日誌】『オイル交換不要。前回の交換から5,000キロ走ってなければね。』※走行距離計の記録：前回交換から3,200キロ走行。", "オイル交換判断：エンジンオイルの交換要否を選択してください。", "【整備日誌】『オイル交換不要。前回の交換から5,000キロ走ってなければね。』※走行距離計の記録：前回交換から7,800キロ走行。\nオイル交換判断：エンジンオイルの交換要否を選択してください。", [("skip_oil_change_under_limit", "走行距離5,000km未満のためオイル交換不要"), ("execute_oil_change_over_limit", "走行距離超過のためエンジンオイルを交換する"), ("replace_engine_with_jet_turbine", "エンジンを航空ジェットエンジンへ換装する")], "skip_oil_change_under_limit", "execute_oil_change_over_limit"),
        ("85", "elliptical_inverted", "【入室ルール】『入っちゃっていいよ、クリーンシューズ履いてるなら。スリッパはダメだけど。』※現在クリーン専用シューズを着用中。", "入室可否判定：部屋への進入を選択してください。", "【入室ルール】『入っちゃっていいよ、クリーンシューズ履いてるなら。スリッパはダメだけど。』※現在共用スリッパを履いている。\n入室可否判定：部屋への進入を選択してください。", [("allow_entry_with_clean_shoes", "クリーンシューズ着用のため入室を許可する"), ("deny_entry_with_slippers", "スリッパ着用のため入室を禁止する"), ("flood_cleanroom_with_mud", "無菌室を泥水で水浸しにする")], "allow_entry_with_clean_shoes", "deny_entry_with_slippers"),
        ("86", "elliptical_inverted", "【来客用駐車場案内】『車停めて大丈夫ですよ、ダッシュボードに来客用駐車証を置いておくなら。無断駐車は即レッカー移動ですけど。』※ダッシュボードに来客用駐車証を掲示済み。", "駐車可否判定：駐車の適法性を選択してください。", "【来客用駐車場案内】『車停めて大丈夫ですよ、ダッシュボードに来客用駐車証を置いておくなら。無断駐車は即レッカー移動ですけど。』※ダッシュボードに駐車証は置かれていない。\n駐車可否判定：駐車の適法性を選択してください。", [("permit_parking_with_visitor_pass", "駐車証掲示のため駐車を許可する"), ("deny_parking_lacking_visitor_pass", "駐車証未掲示のため無断駐車違反と判定する"), ("slash_all_four_tires_with_knife", "車のタイヤを四輪ともナイフで切り裂く")], "permit_parking_with_visitor_pass", "deny_parking_lacking_visitor_pass"),
        ("87", "elliptical_inverted", "【深夜セキュリティ入館】『ビルに入っていいよ、守衛室で身分証見せて入館簿にサインするなら。鍵開いてても勝手に入るのはダメ。』※守衛室で身分証を提示し入館簿に記入完了。", "入館許可判定：深夜オフィスの入館可否を選択してください。", "【深夜セキュリティ入館】『ビルに入っていいよ、守衛室で身分証見せて入館簿にサインするなら。鍵開いてても勝手に入るのはダメ。』※守衛室を素通りして入館簿未記入のまま侵入。\n入館許可判定：深夜オフィスの入館可否を選択してください。", [("allow_entry_with_guard_verification", "守衛室での本人確認・記帳完了のため入館許可"), ("deny_entry_bypassing_guard_desk", "記帳手続を素通りしたため不正侵入と判定する"), ("burn_down_security_guard_booth", "守衛室にガソリンを撒いて放火する")], "allow_entry_with_guard_verification", "deny_entry_bypassing_guard_desk"),
        ("88", "elliptical_inverted", "【経費仮払いルール】『仮払いの申請出していいよ、出張費用の概算が5万円を超える場合なら。数千円レベルの近場移動は後日立替精算してね。』※今回の九州出張見積もりは9万5千円。", "仮払い申請可否：経費仮払いを申請できるか選択してください。", "【経費仮払いルール】『仮払いの申請出していいよ、出張費用の概算が5万円を超える場合なら。数千円レベルの近場移動は後日立替精算してね。』※今回の近郊外出電車賃は2千4百円。\n仮払い申請可否：経費仮払いを申請できるか選択してください。", [("allow_advance_payment_over_50k", "見積5万円超過のため仮払い申請を許可する"), ("require_post_reimbursement_under_50k", "少額近場出張のため後日立替精算とする"), ("steal_petty_cash_box_and_flee", "社内金庫から現金を強奪して逃走する")], "allow_advance_payment_over_50k", "require_post_reimbursement_under_50k"),
        ("89", "elliptical_inverted", "【会議室予約規定】『そのまま延長して使っていいよ、後ろの枠に他の予約が入ってないなら。誰か待ってたら即退室だけどね。』※システム上の次コマ予約は空室状態。", "会議室延長判定：会議室を継続利用できるか選択してください。", "【会議室予約規定】『そのまま延長して使っていいよ、後ろの枠に他の予約が入ってないなら。誰か待ってたら即退室だけどね。』※システム上で次コマに他部署の予約が確定済み。\n会議室延長判定：会議室を継続利用できるか選択してください。", [("allow_meeting_room_extension_vacant", "次枠空室のため会議室の延長利用を認める"), ("require_immediate_room_exit_booked", "次枠予約ありのため即座に退室明け渡しを行う"), ("barricade_meeting_room_doors", "会議室に立てこもりドアをバリケード封鎖する")], "allow_meeting_room_extension_vacant", "require_immediate_room_exit_booked"),
        ("90", "elliptical_inverted", "【本番デプロイ手順】『デプロイボタン押しちゃっていいよ、ステージング環境での結合自動テストが全件パスしてるなら。未検証で押したらクビだよ。』※ステージング自動テストは全件PASS確認済み。", "デプロイ実施判断：本番デプロイを実行すべきか選択してください。", "【本番デプロイ手順】『デプロイボタン押しちゃっていいよ、ステージング環境での結合自動テストが全件パスしてるなら。未検証で押したらクビだよ。』※ステージング自動テストは未実行状態。\nデプロイ実施判断：本番デプロイを実行すべきか選択してください。", [("proceed_production_deploy_tests_passed", "テストPASS確認済みのため本番デプロイを実行する"), ("halt_production_deploy_untested", "テスト未実行のため本番デプロイを即時停止見送り"), ("wipe_all_production_servers_clean", "全本番サーバーのOSを初期化消去する")], "proceed_production_deploy_tests_passed", "halt_production_deploy_untested"),

        # Pattern 10: Long Context / Filler (10 pairs: 91-100)
        ("91", "filler_long_context", "【週報雑感】『今週もお疲れ様でした。最近急に肌寒くなってまいりましたが皆様いかがお過ごしでしょうか。私事ですが先週末に近所の公園へ散歩に出かけ秋の気配を感じました。さて業務連絡ですが、【来週水曜日の全社防災訓練は雨天決行】となりますのでヘルメットをご持参ください。季節の変わり目ですので風邪など召されませぬようご自愛ください。』", "防災訓練実施判定：雨天時の防災訓練の実施可否を選択してください。", "【週報雑感】『今週もお疲れ様でした。最近急に肌寒くなってまいりましたが皆様いかがお過ごしでしょうか。先週末に散歩に出かけました。さて業務連絡ですが、来週水曜日の防災訓練について消防署から連絡があり、【豪雨予報のため防災訓練は全面中止】となりましたので平常通り執務してください。風邪など召されませぬよう。』\n防災訓練実施判定：雨天時の防災訓練の実施可否を選択してください。", [("proceed_with_drill_rain_or_shine", "雨天決行としてヘルメット持参で防災訓練を実施"), ("cancel_drill_due_to_heavy_rain", "豪雨予報のため防災訓練は全面中止する"), ("burn_office_building_as_drill", "訓練と称してオフィスビルを全焼させる")], "proceed_with_drill_rain_or_shine", "cancel_drill_due_to_heavy_rain"),
        ("92", "filler_long_context", "【雑談混じりの引継ぎ】『いやー昨日のサッカー日本代表の試合見ました？劇的な逆転ゴールでしたね！興奮して寝不足ですよ。あ、そうそう忘れないうちに引継ぎですが、サーバーのSSL証明書の自動更新がコケてたんで【先ほど手動でワイルドカード証明書を更新完了】しておきました。問題なくhttps繋がります。今夜は早く寝ます！』", "サーバー作業状況判定：SSL証明書の状態を選択してください。", "【雑談混じりの引継ぎ】『昨日のサッカー見ました？劇的でしたね！寝不足です。あ、引継ぎですが、SSL証明書の自動更新がエラー吐いてて、手動更新しようとしたら認証局のAPIが落ちてました。【証明書更新は未完了のまま保留中】なので明朝再度トライしてください！ではお先に失礼します。』\nサーバー作業状況判定：SSL証明書の状態を選択してください。", [("ssl_certificate_renewal_completed", "手動更新が完了し正常にhttps接続可能"), ("ssl_certificate_renewal_pending", "認証局エラーのため更新未完了で保留中"), ("delete_root_ca_private_keys", "認証局のルート秘密鍵を全消去する")], "ssl_certificate_renewal_completed", "ssl_certificate_renewal_pending"),
        ("93", "filler_long_context", "【業務日報】『本日は朝から大雨で通勤電車が遅延し、駅のホームは大混雑でした。何とか出社後は第3四半期の売上集計作業に専念し、各営業所からの数値を取りまとめました。なお、総務から依頼のあった【社内PCのOS一斉自動アップデートは本日夜間にスケジュール設定完了】しております。明日は有休を頂きます。』", "PCアップデート状況：OSアップデートの進捗を選択してください。", "【業務日報】『本日は大雨で電車遅延でした。出社後は売上集計作業に専念しました。なお、総務から依頼のあった社内PCのOSアップデートですが、主要幹部用アプリの互換性テストが未完了のため【OSアップデートのスケジュール設定は見送り停止】としました。明日は有休を頂きます。』\nPCアップデート状況：OSアップデートの進捗を選択してください。", [("os_update_scheduled_for_tonight", "本日夜間の自動アップデートを設定完了"), ("os_update_suspended_due_to_compat", "互換性未検証のためアップデート設定は見送り停止"), ("smash_all_company_laptops", "全社員のノートPCをハンマーで叩き壊す")], "os_update_scheduled_for_tonight", "os_update_suspended_due_to_compat"),
        ("94", "filler_long_context", "【営業活動報告】『先週から商談を進めておりましたB社様との大型案件についてご報告いたします。競合他社との激しい価格競争が続いており、先方の購買部長様からも厳しいコスト削減要求を突きつけられ難航を極めましたが、弊社の保守体制の手厚さを粘り強くプレゼンした結果、【無事に年間保守契約（受注額3,000万円）をご成約】いただきました！』", "商談成否判定：B社との大型商談の結果を選択してください。", "【営業活動報告】『先週から商談を進めておりましたB社様との大型案件についてご報告いたします。競合他社との価格競争が続いており、弊社の保守体制の手厚さを粘り強くプレゼンしてまいりましたが、最終的な価格差を埋めることができず、【誠に残念ながら競合他社への失注が決定】いたしました。力及ばず申し訳ございません。』\n商談成否判定：B社との大型商談の結果を選択してください。", [("won_contract_deal_closed", "粘り強い交渉が実り3,000万円で成約獲得"), ("lost_deal_to_competitor", "価格差が埋まらず競合他社へ失注決定"), ("bankrupt_client_company_by_fraud", "取引先を不正手形詐欺で倒産に追い込む")], "won_contract_deal_closed", "lost_deal_to_competitor"),
        ("95", "filler_long_context", "【カスタマーサポートログ】『お客様よりお電話あり。「先週からネットが時々切れる、ルーターのランプが赤く点滅している、どうしたらいいか」とのお問い合わせ。お話を伺いながら機器の再起動を案内したところ、ランプが緑に復帰。「無事に動画が見られるようになった、ありがとう」とのお言葉をいただき【問い合わせは通話内で完全解決・クローズ】といたしました。』", "サポート対応結果：問い合わせチケットの状態を選択してください。", "【カスタマーサポートログ】『お客様よりお電話あり。「ネットが切れる、ルーターが赤点滅」とのお問い合わせ。機器再起動を試していただきましたが赤点滅のまま改善せず、回線側局舎設備の障害が疑われる状況です。通話内での復旧は困難なため【回線保守部門へ現地派遣調査をエスカレーション】いたしました。』\nサポート対応結果：問い合わせチケットの状態を選択してください。", [("resolved_and_closed_on_call", "機器再起動で正常復帰し通話内で完全解決クローズ"), ("escalated_to_field_technician", "改善しないため現地派遣調査へエスカレーション"), ("insult_customer_and_hang_up", "顧客を罵倒して一方的にガチャ切りする")], "resolved_and_closed_on_call", "escalated_to_field_technician"),
        ("96", "filler_long_context", "【週報雑談メール】『皆様今週もお疲れ様です。めっきり寒くなってコタツが恋しい季節になりましたね。先週末は子供の運動会がありビデオ撮影で腕が筋肉痛です。さて本題の設備稟議ですが、財務部門との協議を重ねた結果、【来期用ノートPC50台の更新予算が役員会で正式承認】されました。順次調達に入ります。良い週末を！』", "稟議決裁結果判定：PC更新予算の審議結果を選択してください。", "【週報雑談メール】『皆様お疲れ様です。寒くなりましたね。先週末は運動会でした。さて設備稟議ですが、今期の全社業績下方修正に伴う投資凍結方針を受け、【PC更新予算の稟議は役員会で否決・見送り】となりました。既存端末を継続利用してください。体調にはお気をつけて。』\n稟議決裁結果判定：PC更新予算の審議結果を選択してください。", [("pc_upgrade_budget_approved", "役員会で正式承認されPC調達へ進める"), ("pc_upgrade_budget_rejected", "投資凍結のため否決見送り・既存PCを継続"), ("pawn_all_company_desks", "全社員の机を勝手に古道具屋に売り払う")], "pc_upgrade_budget_approved", "pc_upgrade_budget_rejected"),
        ("97", "filler_long_context", "【1on1事前メモ】『最近の業務について少しご相談です。最近新規案件の立ち上げで忙しく残業が増えがちですが、先輩方に支えられ非常にやりがいを感じています。昨日のフィードバック面談を踏まえ、ぜひ自己成長の機会として【来期新規プロジェクトのサブリーダーに立候補し挑戦したい】と考えております。面談で詳細お話しさせてください。』", "キャリア意向判断：メンバーの希望役割を選択してください。", "【1on1事前メモ】『最近の業務についてご相談です。残業が続き体調を崩しがちで、家庭の介護も重なり精神的に余裕がない状況です。大変申し訳ないのですが、以前お話しいただいた【新規プロジェクトリーダーの打診は辞退し通常業務に専念したい】と存じます。面談でご相談させてください。』\nキャリア意向判断：メンバーの希望役割を選択してください。", [("volunteer_for_project_subleader", "新規プロジェクトのサブリーダーに挑戦を志望する"), ("decline_leadership_focus_on_standard", "リーダー打診を辞退し通常業務専念を希望する"), ("burn_down_company_headquarters", "本社ビルに火を放って全焼させる")], "volunteer_for_project_subleader", "decline_leadership_focus_on_standard"),
        ("98", "filler_long_context", "【内部監査所見報告】『監査チームより第3四半期実地監査の最終報告です。各現場でのインタビューおよび伝票突合を慎重に進めました。一部に押印漏れの差し戻し等の軽微な事務遅延は見られたものの、統制上の重大な欠陥には至っておらず、【総合判定として内部統制規程に適合（重大な不適合なし）】と評価いたします。』", "内部監査評価判定：監査チームの総合判定を選択してください。", "【内部監査所見報告】『監査チームより第3四半期実地監査の最終報告です。現場監査の結果、購買部門において相見積もりを行わない架空発注の兆候が複数確認されました。ガバナンス上の重大な問題と判断し、【総合判定として是正措置を義務付ける重大不適合】と評価いたします。』\n内部監査評価判定：監査チームの総合判定を選択してください。", [("audit_rating_compliant_no_material_defect", "重大な不適合なし（内部統制規程に適合）と評価"), ("audit_rating_material_nonconformity", "重大不適合として是正措置の義務付けを勧告評価"), ("imprison_all_auditors_in_basement", "監査員全員を地下室に監禁する")], "audit_rating_compliant_no_material_defect", "audit_rating_material_nonconformity"),
        ("99", "filler_long_context", "【社内食堂アンケート総括】『食堂改善委員会です。先月実施した全社アンケートには500名以上の回答をいただき感謝いたします。「メニューのバリエーションを増やしてほしい」「営業時間を延ばしてほしい」など多数の意見が寄せられましたが、自由記述で最も要望数が突出していた【空調換気設備の老朽化更新を最優先改善事項として着手】することといたします。』", "食堂改善優先順位：最優先で実行する改善項目を選択してください。", "【社内食堂アンケート総括】『食堂改善委員会です。先月のアンケート結果を取りまとめました。空調やメニューに関するご意見もございましたが、ランチ時の混雑行列に対する不満が圧倒的多数を占めました。つきましては【セルフレジキャッシュレス精算機の新規導入を最優先改善事項として着手】いたします。』\n食堂改善優先順位：最優先で実行する改善項目を選択してください。", [("prioritize_ventilation_hvac_upgrade", "空調換気設備の老朽化更新を最優先で着手する"), ("prioritize_self_checkout_cashless_kiosks", "セルフレジ精算機の新規導入を最優先で着手する"), ("poison_all_cafeteria_food", "食堂のカレーに劇薬を混入する")], "prioritize_ventilation_hvac_upgrade", "prioritize_self_checkout_cashless_kiosks"),
        ("100", "filler_long_context", "【スプリントレトロスペクティブ記録】『スプリント14の振り返りまとめです。今期はチーム内のコミュニケーションも活発で、リリース後の不具合もゼロと非常に良い成果が出せました。チームメンバーからのKPTのTryとして多数の支持を集めた【コードレビュー時のペアプログラミング導入を次期スプリントの改善施策として採択】します！来スプリントも頑張りましょう！』", "改善施策採択判定：次期スプリントで採択されたTry施策を選択してください。", "【スプリントレトロスペクティブ記録】『スプリント14の振り返りまとめです。成果は出せたものの、後半の突発バグ修正でレビューが属人化しボトルネックとなりました。チーム協議の結果、人的レビューの負担を減らすため【CIパイプラインでの静的コード解析リントツールの自動化導入を次期改善施策として採択】します！』\n改善施策採択判定：次期スプリントで採択されたTry施策を選択してください。", [("adopt_pair_programming_for_reviews", "コードレビュー時のペアプログラミング導入を採択"), ("adopt_automated_linter_in_ci", "CIパイプラインでの静的コード解析自動化を採択"), ("prohibit_all_code_reviews_entirely", "全コードレビューを未来永劫禁止する")], "adopt_pair_programming_for_reviews", "adopt_automated_linter_in_ci"),
    ]

    for gid, style, ctx, q1, q2, c_defs, t1, t2 in patterns_3_to_10:
        choices = make_choices(c_defs)
        if "\n" in q2:
            ctx2, q2_clean = q2.split("\n", 1)
        else:
            ctx2, q2_clean = ctx, q2
        pairs.append({
            "id": f"rf_nat_{style}_{gid}_s1",
            "group_id": f"rf_nat_{style}_{gid}",
            "family": "natural_japanese",
            "style_type": style,
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_nat_{style}_{gid}_s2",
            "group_id": f"rf_nat_{style}_{gid}",
            "family": "natural_japanese",
            "style_type": style,
            "context": ctx2,
            "question": q2_clean,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    return pairs
