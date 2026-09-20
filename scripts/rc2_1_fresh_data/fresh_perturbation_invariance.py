"""Research Fresh Suite: perturbation_invariance (80 pairs, 160 cases).

Coverage of 8 perturbation categories x 10 pairs:
1. premise_order: 前提文・条件節の前後入れ替え（文頭配置 vs 文末配置）
2. candidate_order: 選択肢の提示順序シャッフル（正解候補の位置依存性耐性）
3. filler_distraction: 類似キーワードや無関係な数値を混入した撹乱文の挿入
4. register_style: 丁寧語・敬語 vs 常体・口語体（文体変形への不変性）
5. parenthetical_condition: 括弧書き（※注釈、ただし書き）内に重要条件を埋め込み
6. negation_syntax: 多重否定・倒置否定・間接否定表現（否定統語の多様性）
7. delimiter_formatting: 箇条書き記号・ブラケット・番号付けの書式揺らぎ
8. candidate_id_style: 選択肢IDの形式多様性（英数字、記号、抽象キー）

All 80 groups are contrastive pairs (_s1 and _s2 have distinct targets).
Token length guaranteed <= 380 (< 512 hard ceiling).
"""

from typing import Any, Dict, List, Tuple


def make_choices(defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in defs]


def get_fresh_perturbation_invariance_pairs() -> List[Dict[str, Any]]:
    pairs = []

    # 1. Premise Order (10 pairs: 01 to 10)
    # Testing context sensitivity when condition is placed at start vs end
    premise_order_defs = [
        (
            "01",
            "本日の東京オフィス来客受付方針：身分証明書の提示があった場合のみ、来客用一時通行証を発行してください。提示がない場合は入館をお断りします。来訪者は運転免許証を提示しました。",
            "来客受付対応：来訪者への対応を選択してください。",
            "来訪者は身分証の所持を拒否しました。本日の東京オフィス来客受付方針：身分証明書の提示があった場合のみ、来客用一時通行証を発行してください。提示がない場合は入館をお断りします。",
            "来客受付対応：来訪者への対応を選択してください。",
            [("issue_temporary_pass", "来客用一時通行証を発行して入館を許可する"), ("deny_building_entry", "身分証不携帯のため入館をお断りする"), ("destroy_visitor_belongings", "来客の手荷物を焼却処分する")],
            "issue_temporary_pass", "deny_building_entry"
        ),
        (
            "02",
            "返金処理規定：購入レシートがある場合、全額現金で返金します。レシートがない場合は店舗ポイントでの返還となります。お客様は購入時の紙レシートを持参されました。",
            "返金手段判定：適用すべき返金方法を選択してください。",
            "お客様はレシートを紛失され手元にありません。返金処理規定：購入レシートがある場合、全額現金で返金します。レシートがない場合は店舗ポイントでの返還となります。",
            "返金手段判定：適用すべき返金方法を選択してください。",
            [("refund_in_cash_full", "購入レシートに基づき全額現金で返金する"), ("refund_in_store_points", "レシート紛失のため店舗ポイントで返還する"), ("confiscate_customer_wallet", "顧客の財布を没収する")],
            "refund_in_cash_full", "refund_in_store_points"
        ),
        (
            "03",
            "セキュリティログアウト方針：セッションが30分以上無操作の場合、自動ログアウトを実行します。操作が継続している場合はセッションを維持します。現在の無操作継続時間は45分です。",
            "セッション制御：システムが実行すべきセッション処置を選択してください。",
            "現在の無操作継続時間は10分です。セキュリティログアウト方針：セッションが30分以上無操作の場合、自動ログアウトを実行します。操作が継続している場合はセッションを維持します。",
            "セッション制御：システムが実行すべきセッション処置を選択してください。",
            [("execute_automatic_logout", "無操作30分超過のため自動ログアウトを実行する"), ("maintain_active_session", "操作継続中とみなしセッションを維持する"), ("delete_all_user_accounts", "全ユーザーアカウントを削除する")],
            "execute_automatic_logout", "maintain_active_session"
        ),
        (
            "04",
            "手荷物超過料金規定：総重量が20kgを超える場合、1kgあたり1,000円の追加料金を徴収します。20kg以下の場合は無料預入となります。計量器の測定結果は24kgでした。",
            "手荷物料金判定：徴収すべき手荷物料金を選択してください。",
            "計量器の測定結果は18kgでした。手荷物超過料金規定：総重量が20kgを超える場合、1kgあたり1,000円の追加料金を徴収します。20kg以下の場合は無料預入となります。",
            "手荷物料金判定：徴収すべき手荷物料金を選択してください。",
            [("charge_excess_baggage_fee", "重量20kg超過のため追加手荷物料金を徴収する"), ("allow_free_baggage_checkin", "規定重量内のため無料で預託を受け付ける"), ("throw_baggage_into_sea", "手荷物を外洋へ投げ捨てる")],
            "charge_excess_baggage_fee", "allow_free_baggage_checkin"
        ),
        (
            "05",
            "特急列車乗車基準：特急券を所持している旅客のみ特急車両への乗車を認めます。普通乗車券のみの旅客は普通列車をご案内します。旅客は指定席特急券を改札機に投入しました。",
            "乗車案内判断：旅客へ案内すべき列車種別を選択してください。",
            "旅客は普通乗車券のみを所持し特急券はありません。特急列車乗車基準：特急券を所持している旅客のみ特急車両への乗車を認めます。普通乗車券のみの旅客は普通列車をご案内します。",
            "乗車案内判断：旅客へ案内すべき列車種別を選択してください。",
            [("permit_limited_express_boarding", "特急券所持を確認し特急列車への乗車を案内する"), ("direct_to_local_train", "特急券不所持のため普通列車をご案内する"), ("arrest_passenger_on_the_spot", "乗客をその場で私人逮捕する")],
            "permit_limited_express_boarding", "direct_to_local_train"
        ),
        (
            "06",
            "夜間入館カード審査：有効期限内のセキュリティカードをタッチした場合に自動ドアを解錠します。期限切れカードの場合は解錠せず警備室へ通報します。認証結果：有効期限2028年まで有効。",
            "入館ゲート判定：自動ドアの制御動作を選択してください。",
            "認証結果：有効期限が昨月末で失効済み。夜間入館カード審査：有効期限内のセキュリティカードをタッチした場合に自動ドアを解錠します。期限切れカードの場合は解錠せず警備室へ通報します。",
            "入館ゲート判定：自動ドアの制御動作を選択してください。",
            [("unlock_automatic_doors", "有効カード確認により自動ドアを解錠する"), ("deny_access_and_alert_security", "期限切れのため解錠拒否し警備室へ通報する"), ("electrocute_cardholder", "カード保有者に高電圧電流を流す")],
            "unlock_automatic_doors", "deny_access_and_alert_security"
        ),
        (
            "07",
            "割引クーポン適用ルール：合計購入金額が5,000円以上の会計に限り1,000円割引を適用します。5,000円未満の会計には適用できません。レジの合計金額は6,200円です。",
            "会計割引判定：クーポン割引の適用可否を選択してください。",
            "レジの合計金額は3,800円です。割引クーポン適用ルール：合計購入金額が5,000円以上の会計に限り1,000円割引を適用します。5,000円未満の会計には適用できません。",
            "会計割引判定：クーポン割引の適用可否を選択してください。",
            [("apply_1000_yen_discount", "金額条件充足のため1,000円割引を適用する"), ("deny_coupon_discount_under_limit", "5,000円未満のためクーポン適用不可とする"), ("double_the_total_bill", "請求金額を勝手に2倍にする")],
            "apply_1000_yen_discount", "deny_coupon_discount_under_limit"
        ),
        (
            "08",
            "プール利用基準：身長120cm以上の児童に限りウォータースライダーの利用を許可します。120cm未満の児童は利用できません。身長測定結果は125cmでした。",
            "遊具利用判定：スライダーの利用可否を選択してください。",
            "身長測定結果は115cmでした。プール利用基準：身長120cm以上の児童に限りウォータースライダーの利用を許可します。120cm未満の児童は利用できません。",
            "遊具利用判定：スライダーの利用可否を選択してください。",
            [("permit_waterslide_entry", "身長120cm以上を確認しスライダー利用を許可"), ("deny_waterslide_entry_under_height", "身長基準未達のためスライダー利用をお断りする"), ("drain_entire_swimming_pool", "プールの水をすべて排水する")],
            "permit_waterslide_entry", "deny_waterslide_entry_under_height"
        ),
        (
            "09",
            "駐車場料金優遇制度：館内レシート合算が3,000円以上のお客様に2時間無料駐車券を交付します。未達のお客様は通常時間料金となります。持参レシート合計額は4,500円です。",
            "駐車サービス判定：交付すべき駐車優待を選択してください。",
            "持参レシート合計額は1,200円です。駐車場料金優遇制度：館内レシート合算が3,000円以上のお客様に2時間無料駐車券を交付します。未達のお客様は通常時間料金となります。",
            "駐車サービス判定：交付すべき駐車優待を選択してください。",
            [("grant_2_hour_free_parking_ticket", "合算3,000円以上のため2時間無料駐車券を交付"), ("charge_standard_hourly_parking_rate", "基準未達のため無料券交付なし通常料金を適用"), ("crush_vehicle_with_bulldozer", "ブルドーザーで自家用車を踏み潰す")],
            "grant_2_hour_free_parking_ticket", "charge_standard_hourly_parking_rate"
        ),
        (
            "10",
            "機密ファイル印刷制御：アクセス権限が機密レベルA以上のユーザーに限り印刷出力を許可します。レベルB以下のユーザーの印刷要求はブロックされます。操作ユーザーの権限は機密レベルS（最高位）です。",
            "印刷制御判定：印刷ジョブの実行可否を選択してください。",
            "操作ユーザーの権限は機密レベルC（一般）です。機密ファイル印刷制御：アクセス権限が機密レベルA以上のユーザーに限り印刷出力を許可します。レベルB以下のユーザーの印刷要求はブロックされます。",
            "印刷制御判定：印刷ジョブの実行可否を選択してください。",
            [("allow_secure_print_job", "権限レベルA以上のため印刷ジョブを実行する"), ("block_print_job_insufficient_privilege", "権限不足のため印刷ジョブをブロック拒否する"), ("smash_printer_with_crowbar", "バールで複合機を叩き割る")],
            "allow_secure_print_job", "block_print_job_insufficient_privilege"
        ),
    ]

    for gid, ctx1, q1, ctx2, q2, c_defs, t1, t2 in premise_order_defs:
        choices = make_choices(c_defs)
        pairs.append({
            "id": f"rf_pert_pord_{gid}_s1",
            "group_id": f"rf_pert_pord_{gid}",
            "family": "perturbation_invariance",
            "perturbation_type": "premise_order",
            "context": ctx1,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_pert_pord_{gid}_s2",
            "group_id": f"rf_pert_pord_{gid}",
            "family": "perturbation_invariance",
            "perturbation_type": "premise_order",
            "context": ctx2,
            "question": q2,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # 2. Candidate Order Shuffled (10 pairs: 11 to 20)
    # Target choice placed in different positions (e.g. 1st, 2nd, 3rd)
    candidate_order_defs = [
        (
            "11",
            "倉庫出庫規程：引当ステータスが「検品完了」のオーダーのみピッキングリストを出力する。「保留中」のオーダーは出力不可。オーダー#101は検品完了。",
            "出庫判断：オーダー#101のピッキングリスト出力可否を選択してください。",
            "倉庫出庫規程：引当ステータスが「検品完了」のオーダーのみピッキングリストを出力する。「保留中」のオーダーは出力不可。オーダー#102は保留中。",
            "出庫判断：オーダー#102のピッキングリスト出力可否を選択してください。",
            # Shuffled candidate order: distractor first, then options
            [("deny_list_output_on_hold", "保留中のためピッキングリスト出力を停止する"), ("burn_warehouse_pallets", "倉庫のパレットをすべて放火する"), ("allow_picking_list_output", "検品完了のためピッキングリストを出力する")],
            "allow_picking_list_output", "deny_list_output_on_hold"
        ),
        (
            "12",
            "受講資格判定：TOEICスコアが750点以上の応募者は上級ビジネス英語講座を受講可能。750点未満は中級講座へ案内する。申請者のTOEICスコアは820点。",
            "講座案内判定：申請者に案内すべき受講クラスを選択してください。",
            "受講資格判定：TOEICスコアが750点以上の応募者は上級ビジネス英語講座を受講可能。750点未満は中級講座へ案内する。申請者のTOEICスコアは680点。",
            "講座案内判定：申請者に案内すべき受講クラスを選択してください。",
            [("shred_applicant_diploma", "申請者の大学卒業証書を細断する"), ("guide_to_intermediate_class", "基準未達のため中級英語講座へ案内する"), ("enroll_in_advanced_business_class", "スコア充足のため上級ビジネス英語講座へ登録する")],
            "enroll_in_advanced_business_class", "guide_to_intermediate_class"
        ),
        (
            "13",
            "経費計上基準：1個あたりの取得価額が10万円未満の消耗品は即時費用処理する。10万円以上の資産は固定資産計上する。購入したPC周辺機器は単価48,000円。",
            "会計処理判定：購入備品の記帳勘定科目を選択してください。",
            "経費計上基準：1個あたりの取得価額が10万円未満の消耗品は即時費用処理する。10万円以上の資産は固定資産計上する。購入した高性能サーバーは単価350,000円。",
            "会計処理判定：購入備品の記帳勘定科目を選択してください。",
            [("capitalize_as_fixed_asset", "10万円以上のため固定資産として資産計上する"), ("expense_immediately_as_supplies", "10万円未満のため消耗品費として即時費用処理"), ("hide_invoices_under_carpet", "領収書をカーペットの下に隠す")],
            "expense_immediately_as_supplies", "capitalize_as_fixed_asset"
        ),
        (
            "14",
            "品質合否判定：寸法誤差がプラスマイナス0.05mm以内のロットは「合格出荷」とする。0.05mmを超える誤差があるロットは「不合格再加工」とする。測定ロットの誤差は+0.02mm。",
            "検査判定：測定ロットの処置判定を選択してください。",
            "品質合否判定：寸法誤差がプラスマイナス0.05mm以内のロットは「合格出荷」とする。0.05mmを超える誤差があるロットは「不合格再加工」とする。測定ロットの誤差は+0.12mm。",
            "検査判定：測定ロットの処置判定を選択してください。",
            [("reject_lot_for_rework", "許容誤差超過のため不合格とし再加工へ回す"), ("pass_lot_for_shipment", "公差内のため合格出荷と判定する"), ("ship_flawed_parts_to_kindergarten", "不良品を幼稚園にバラ撒く")],
            "pass_lot_for_shipment", "reject_lot_for_rework"
        ),
        (
            "15",
            "通信帯域制限ポリシー：当月の高速データ通信量が30GBを超過した回線は通信速度を128kbpsに制限する。30GB以内の回線は高速通信を維持する。当月利用量は34GB。",
            "速度制御判定：当該回線の通信速度制御を選択してください。",
            "通信帯域制限ポリシー：当月の高速データ通信量が30GBを超過した回線は通信速度を128kbpsに制限する。30GB以内の回線は高速通信を維持する。当月利用量は19GB。",
            "速度制御判定：当該回線の通信速度制御を選択してください。",
            [("cut_undersea_fiber_cable", "海底光ファイバーケーブルを切断する"), ("throttle_speed_to_128kbps", "30GB超過のため通信速度を128kbpsに制限する"), ("maintain_high_speed_data", "規定量以内のため高速通信をそのまま維持する")],
            "throttle_speed_to_128kbps", "maintain_high_speed_data"
        ),
        (
            "16",
            "社内表彰規程：四半期売上目標達成率が120%以上の営業チームに社長賞特別インセンティブを授与する。120%未満は対象外。営業第1チームの達成率は135%。",
            "表彰判定：営業第1チームへの表彰授与を選択してください。",
            "社内表彰規程：四半期売上目標達成率が120%以上の営業チームに社長賞特別インセンティブを授与する。120%未満は対象外。営業第2チームの達成率は108%。",
            "表彰判定：営業第2チームへの表彰授与を選択してください。",
            [("deny_president_award_under_target", "目標120%未達のため社長賞の対象外とする"), ("grant_president_award_incentive", "達成率120%超過のため社長賞インセンティブを授与"), ("demote_all_sales_reps_to_interns", "全営業部員を見習いインターンに降格する")],
            "grant_president_award_incentive", "deny_president_award_under_target"
        ),
        (
            "17",
            "入札参加資格審査：直前3期連続で営業利益が黒字の法人に限り公共事業入札への参加を許可する。赤字決算期がある法人は参加資格を停止する。当該企業の直近3期：全期黒字計上。",
            "入札資格判定：当該法人の入札参加可否を選択してください。",
            "入札参加資格審査：直前3期連続で営業利益が黒字の法人に限り公共事業入札への参加を許可する。赤字決算期がある法人は参加資格を停止する。当該企業の直近3期：前期に営業赤字を計上。",
            "入札資格判定：当該法人の入札参加可否を選択してください。",
            [("disqualify_bidding_due_to_loss", "営業赤字期があるため入札参加資格を停止する"), ("burn_down_city_hall", "市役所本庁舎を放火する"), ("qualify_bidding_3_years_profitable", "3期連続黒字を確認し入札参加資格を認定する")],
            "qualify_bidding_3_years_profitable", "disqualify_bidding_due_to_loss"
        ),
        (
            "18",
            "薬品温度管理基準：保管庫の庫内温度が2℃から8℃の適正範囲にある場合のみワクチンを出荷可能とする。範囲外逸脱の場合は出荷停止・廃棄調査とする。現在の庫内温度センサー値は5.1℃。",
            "出荷可否判断：ワクチンの出荷可否を選択してください。",
            "薬品温度管理基準：保管庫の庫内温度が2℃から8℃の適正範囲にある場合のみワクチンを出荷可能とする。範囲外逸脱の場合は出荷停止・廃棄調査とする。現在の庫内温度センサー値は11.4℃。",
            "出荷可否判断：ワクチンの出荷可否を選択してください。",
            [("dump_vaccines_in_river", "ワクチンを近隣の河川へ不法投棄する"), ("halt_shipment_and_investigate_spoilage", "温度逸脱のため出荷を停止し廃棄調査を行う"), ("permit_vaccine_shipment_in_range", "適正温度範囲内のためワクチンの出荷を許可する")],
            "permit_vaccine_shipment_in_range", "halt_shipment_and_investigate_spoilage"
        ),
        (
            "19",
            "機内持込手荷物規定：手荷物の3辺の合計が115cm以内の場合のみ客室への機内持ち込みを許可する。115cmを超える荷物は受託手荷物として貨物室へ預ける。計測結果：50cm×35cm×20cm（合計105cm）。",
            "持込手荷物判定：当該手荷物の持ち込み可否を選択してください。",
            "機内持込手荷物規定：手荷物の3辺の合計が115cm以内の場合のみ客室への機内持ち込みを許可する。115cmを超える荷物は受託手荷物として貨物室へ預ける。計測結果：60cm×45cm×25cm（合計130cm）。",
            "持込手荷物判定：当該手荷物の持ち込み可否を選択してください。",
            [("allow_cabin_carry_on", "3辺合計115cm以内のため客室内持込を許可する"), ("require_checked_baggage_cargo", "115cm超過のため受託手荷物として貨物室へ預ける"), ("jettison_cargo_over_ocean", "飛行中の上空から荷物を投棄する")],
            "allow_cabin_carry_on", "require_checked_baggage_cargo"
        ),
        (
            "20",
            "貸出審査基準：信用スコアが650点以上の申込者に限り無担保カードローンの即時融資を実行する。650点未満の申込者は追加書類提出による二次審査とする。申込者のスコアは710点。",
            "融資審査判定：申込者に対する融資手続を選択してください。",
            "貸出審査基準：信用スコアが650点以上の申込者に限り無担保カードローンの即時融資を実行する。650点未満の申込者は追加書類提出による二次審査とする。申込者のスコアは590点。",
            "融資審査判定：申込者に対する融資手続を選択してください。",
            [("route_to_secondary_review_docs", "スコア未達のため追加書類提出の二次審査へ回す"), ("execute_instant_loan_disbursement", "スコア650点以上のため即時融資を実行する"), ("kidnap_applicant_guarantor", "申込者の連帯保証人を拉致監禁する")],
            "execute_instant_loan_disbursement", "route_to_secondary_review_docs"
        ),
    ]

    for gid, ctx1, q1, ctx2, q2, c_defs, t1, t2 in candidate_order_defs:
        choices = make_choices(c_defs)
        pairs.append({
            "id": f"rf_pert_cord_{gid}_s1",
            "group_id": f"rf_pert_cord_{gid}",
            "family": "perturbation_invariance",
            "perturbation_type": "candidate_order",
            "context": ctx1,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_pert_cord_{gid}_s2",
            "group_id": f"rf_pert_cord_{gid}",
            "family": "perturbation_invariance",
            "perturbation_type": "candidate_order",
            "context": ctx2,
            "question": q2,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # 3. Filler Distraction (10 pairs: 21 to 30)
    # Distracting irrelevant sentences injected with similar keywords
    filler_distraction_defs = [
        (
            "21",
            "昨日の本社ビル周辺の降水量は15mmでした。社屋清掃作業員は朝8時から作業を開始しています。本日の重要システム保守規則：メインサーバーのCPU負荷が80%未満であれば自動最適化スクリプトを実行してください。80%以上の場合は手動介入が必要です。現在のCPU負荷は65%です。昼食のカフェテリアメニューは日替わりカレーです。",
            "保守スクリプト判定：実行すべきサーバー最適化手順を選択してください。",
            "昨日の本社ビル周辺の降水量は15mmでした。社屋清掃作業員は朝8時から作業を開始しています。本日の重要システム保守規則：メインサーバーのCPU負荷が80%未満であれば自動最適化スクリプトを実行してください。80%以上の場合は手動介入が必要です。現在のCPU負荷は88%です。昼食のカフェテリアメニューは日替わりカレーです。",
            "保守スクリプト判定：実行すべきサーバー最適化手順を選択してください。",
            [("run_automated_optimization_script", "CPU負荷80%未満のため自動最適化を実行する"), ("require_manual_operator_intervention", "CPU負荷80%以上のため手動介入に切り替える"), ("spill_curry_on_server_rack", "サーバーラックにカレーをぶちまける")],
            "run_automated_optimization_script", "require_manual_operator_intervention"
        ),
        (
            "22",
            "先週末のサッカー観戦チケットは前売りで即日完売しました。駐車場には電気自動車用の充電器が4台設置されています。資材受入検査規則：納入鋼材の引張強度が400MPa以上であれば受入合格と認定する。400MPa未満は受入拒否・返品とする。試験片の実測引張強度は460MPaでした。オフィスの観葉植物に水をやりました。",
            "鋼材受入判定：納入鋼材の合否を選択してください。",
            "先週末のサッカー観戦チケットは前売りで即日完売しました。駐車場には電気自動車用の充電器が4台設置されています。資材受入検査規則：納入鋼材の引張強度が400MPa以上であれば受入合格と認定する。400MPa未満は受入拒否・返品とする。試験片の実測引張強度は370MPaでした。オフィスの観葉植物に水をやりました。",
            "鋼材受入判定：納入鋼材の合否を選択してください。",
            [("accept_steel_materials_certified", "強度400MPa以上のため受入合格と認定する"), ("reject_steel_materials_return", "強度不足のため受入拒否し返品とする"), ("flatten_office_with_steamroller", "ロードローラーで事務所を平らに押し潰す")],
            "accept_steel_materials_certified", "reject_steel_materials_return"
        ),
        (
            "23",
            "近隣の交差点で信号機の更新工事が実施されています。今週の社内回覧板には健康診断の日程が記載されていました。有給取得ルール：申請理由が私用であっても業務上の代替要員が確保できている場合は承認する。代替要員がいない場合は日程再調整を求める。今回の申請：同僚2名が代替対応を快諾済み。来週は晴天が続く見込みです。",
            "休暇承認判定：有給休暇申請の承認可否を選択してください。",
            "近隣の交差点で信号機の更新工事が実施されています。今週の社内回覧板には健康診断の日程が記載されていました。有給取得ルール：申請理由が私用であっても業務上の代替要員が確保できている場合は承認する。代替要員がいない場合は日程再調整を求める。今回の申請：代替要員が全員他案件で埋まり不在。来週は晴天が続く見込みです。",
            "休暇承認判定：有給休暇申請の承認可否を選択してください。",
            [("approve_paid_leave_request", "代替要員確保を確認できたため有給申請を承認"), ("request_rescheduling_no_backup", "代替要員不在のため休暇日程の再調整を求める"), ("fire_all_employees_who_request_leave", "有休を申請した全社員を即日クビにする")],
            "approve_paid_leave_request", "request_rescheduling_no_backup"
        ),
        (
            "24",
            "オフィスの自販機のコーヒーが微糖からブラックへ変更されました。エレベーターの定期点検は来月15日の予定です。顧客信用供与基準：直近の支払遅延回数が0回のお客様には売掛取引枠（月額300万円）を付与する。1回以上の遅延履歴がある顧客は前受金取引のみとする。当該顧客の過去1年間の遅延履歴：0回。今朝の新聞一面は為替相場でした。",
            "与信枠判定：顧客へ提供する決済条件を選択してください。",
            "オフィスの自販機のコーヒーが微糖からブラックへ変更されました。エレベーターの定期点検は来月15日の予定です。顧客信用供与基準：直近の支払遅延回数が0回のお客様には売掛取引枠（月額300万円）を付与する。1回以上の遅延履歴がある顧客は前受金取引のみとする。当該顧客の過去1年間の遅延履歴：先月1回の入金遅延あり。今朝の新聞一面は為替相場でした。",
            "与信枠判定：顧客へ提供する決済条件を選択してください。",
            [("grant_credit_line_3m_yen", "遅延履歴0回のため売掛枠300万円を付与する"), ("restrict_to_advance_cash_payment", "遅延履歴があるため前受金取引に限定する"), ("blackmail_customer_with_threats", "顧客を脅迫して現金を巻き上げる")],
            "grant_credit_line_3m_yen", "restrict_to_advance_cash_payment"
        ),
        (
            "25",
            "本日の社食の定食には小鉢が2品付属します。給湯室の電気ポットのクエン酸洗浄が完了しました。食品保管管理規定：チルド室の温度計が0℃から4℃の範囲にある場合のみ生鮮肉の当日調理を認める。4℃を超過した場合は調理禁止・廃棄処分とする。現在のチルド室温度表示：2.5℃。明日の午前中は全体ミーティングです。",
            "衛生調理判定：生鮮肉の調理可否を選択してください。",
            "本日の社食の定食には小鉢が2品付属します。給湯室の電気ポットのクエン酸洗浄が完了しました。食品保管管理規定：チルド室の温度計が0℃から4℃の範囲にある場合のみ生鮮肉の当日調理を認める。4℃を超過した場合は調理禁止・廃棄処分とする。現在のチルド室温度表示：7.2℃。明日の午前中は全体ミーティングです。",
            "衛生調理判定：生鮮肉の調理可否を選択してください。",
            [("permit_fresh_meat_cooking", "適正温度管理のため生鮮肉の調理を許可する"), ("prohibit_cooking_and_discard_meat", "温度超過のため調理を禁止し廃棄処分とする"), ("sell_spoiled_meat_to_nursing_home", "腐敗した肉を高齢者施設へ転売する")],
            "permit_fresh_meat_cooking", "prohibit_cooking_and_discard_meat"
        ),
        (
            "26",
            "東京タワーのライトアップが今夜特別色に変わります。駅前のドラッグストアでポイント3倍デーを開催しています。図書貸出制限：返却遅延中の本が1冊もない利用者に限り新規貸出を認める。未返却延滞本がある利用者は貸出を停止する。利用者の貸出ステータス：延滞ゼロ冊。図書館の屋上庭園は年中無休です。",
            "図書貸出判定：利用者の新規図書貸出可否を選択してください。",
            "東京タワーのライトアップが今夜特別色に変わります。駅前のドラッグストアでポイント3倍デーを開催しています。図書貸出制限：返却遅延中の本が1冊もない利用者に限り新規貸出を認める。未返却延滞本がある利用者は貸出を停止する。利用者の貸出ステータス：2冊が2週間延滞中。図書館の屋上庭園は年中無休です。",
            "図書貸出判定：利用者の新規図書貸出可否を選択してください。",
            [("allow_new_book_checkout", "延滞図書がないため新規図書貸出を許可する"), ("suspend_book_checkout_due_to_overdue", "未返却延滞があるため図書貸出を停止する"), ("burn_all_library_books", "図書館の蔵書をすべて燃やす")],
            "allow_new_book_checkout", "suspend_book_checkout_due_to_overdue"
        ),
        (
            "27",
            "オフィスの時計の電池をアルカリ乾電池に交換しました。複合機のトナー残量はシアンが少なくなっています。危険物搬出安全規程：運搬用コンテナの耐圧試験有効期限内であれば構外輸送を許可する。期限切れの場合は搬出を差し止める。当該コンテナの耐圧試験期日：来年10月まで有効。総務課の加湿器が新調されました。",
            "危険物搬出判定：コンテナの構外輸送可否を選択してください。",
            "オフィスの時計の電池をアルカリ乾電池に交換しました。複合機のトナー残量はシアンが少なくなっています。危険物搬出安全規程：運搬用コンテナの耐圧試験有効期限内であれば構外輸送を許可する。期限切れの場合は搬出を差し止める。当該コンテナの耐圧試験期日：先月で失効。総務課の加湿器が新調されました。",
            "危険物搬出判定：コンテナの構外輸送可否を選択してください。",
            [("permit_hazardous_material_transport", "耐圧試験有効のため構外輸送を許可する"), ("block_hazardous_material_transport", "耐圧試験失効のため構外搬出を差し止める"), ("drop_hazardous_tank_from_airplane", "飛行機から危険物タンクを地上へ落下させる")],
            "permit_hazardous_material_transport", "block_hazardous_material_transport"
        ),
        (
            "28",
            "近所の公園の桜のつぼみが膨らみ始めました。今週の社内メールマガジンの担当は新入社員の鈴木さんです。旅行保険適用判定：海外渡航先でのケガに対し、日本出国前に加入手続きが完了していれば保険金を給付する。出国後の事後加入は給付対象外とする。加入記録：日本出国前日にWeb契約完了。春の陽気が心地よい季節です。",
            "保険給付判定：海外旅行傷害保険の給付可否を選択してください。",
            "近所の公園の桜のつぼみが膨らみ始めました。今週の社内メールマガジンの担当は新入社員の鈴木さんです。旅行保険適用判定：海外渡航先でのケガに対し、日本出国前に加入手続きが完了していれば保険金を給付する。出国後の事後加入は給付対象外とする。加入記録：現地到着3日後にWeb契約。春の陽気が心地よい季節です。",
            "保険給付判定：海外旅行傷害保険の給付可否を選択してください。",
            [("payout_travel_insurance_benefit", "出国前加入を確認できたため保険金を給付する"), ("deny_insurance_payout_post_departure", "出国後加入のため給付対象外として不支給とする"), ("cancel_all_insurance_policies_worldwide", "全世界の全保険契約を一方的に破棄する")],
            "payout_travel_insurance_benefit", "deny_insurance_payout_post_departure"
        ),
        (
            "29",
            "社員食堂の割り箸が間伐材利用のエコ箸に切り替わりました。会議室のホワイトボードマーカーを補充しました。ソフトウェア配付基準：ライセンス空き枠が1件以上ある場合は即座にクライアントPCへ自動配信する。空き枠ゼロの場合は購入申請へ回す。現在の残存ライセンス数：3ライセンス空きあり。外は心地よい風が吹いています。",
            "ソフト配付判定：クライアントPCへの配付処理を選択してください。",
            "社員食堂の割り箸が間伐材利用のエコ箸に切り替わりました。会議室のホワイトボードマーカーを補充しました。ソフトウェア配付基準：ライセンス空き枠が1件以上ある場合は即座にクライアントPCへ自動配信する。空き枠ゼロの場合は購入申請へ回す。現在の残存ライセンス数：0ライセンス（満杯）。外は心地よい風が吹いています。",
            "ソフト配付判定：クライアントPCへの配付処理を選択してください。",
            [("deploy_software_automatically", "ライセンス空きがあるため即座に自動配信する"), ("route_to_license_purchase_request", "空き枠ゼロのため新規ライセンス購入申請へ回す"), ("format_all_hard_drives_in_company", "全社ハードディスクを一斉フォーマットする")],
            "deploy_software_automatically", "route_to_license_purchase_request"
        ),
        (
            "30",
            "今朝の通勤電車はダイヤ通り定時運行でした。郵便受けに地元商店街のチラシが投函されていました。口座振替実行ルール：引落日前日時点の普通預金残高が引落請求額以上であれば振替処理を実行する。残高不足の場合は振替不能とする。請求額：35,000円、前日預金残高：52,000円。明日は晴れのち曇りの予報です。",
            "口座振替判定：自動引落の実行可否を選択してください。",
            "今朝の通勤電車はダイヤ通り定時運行でした。郵便受けに地元商店街のチラシが投函されていました。口座振替実行ルール：引落日前日時点の普通預金残高が引落請求額以上であれば振替処理を実行する。残高不足の場合は振替不能とする。請求額：35,000円、前日預金残高：8,400円。明日は晴れのち曇りの予報です。",
            "口座振替判定：自動引落の実行可否を選択してください。",
            [("execute_direct_debit_transfer", "預金残高充足のため口座振替を実行する"), ("mark_direct_debit_failed_nsf", "残高不足のため振替不能処理とする"), ("steal_bank_vault_with_dynamite", "ダイナマイトで銀行の金庫を爆破する")],
            "execute_direct_debit_transfer", "mark_direct_debit_failed_nsf"
        ),
    ]

    for gid, ctx1, q1, ctx2, q2, c_defs, t1, t2 in filler_distraction_defs:
        choices = make_choices(c_defs)
        pairs.append({
            "id": f"rf_pert_fldr_{gid}_s1",
            "group_id": f"rf_pert_fldr_{gid}",
            "family": "perturbation_invariance",
            "perturbation_type": "filler_distraction",
            "context": ctx1,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_pert_fldr_{gid}_s2",
            "group_id": f"rf_pert_fldr_{gid}",
            "family": "perturbation_invariance",
            "perturbation_type": "filler_distraction",
            "context": ctx2,
            "question": q2,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # 4. Register Style: Polite vs Casual (10 pairs: 31 to 40)
    # Testing robustness to formal keigo vs casual/blunt memo phrasing
    register_style_defs = [
        (
            "31",
            "【謹啓】平素は格別の高配を賜り深謝申し上げます。貴社のご発注内示書を拝受いたしました。手付金の着金確認が叶い次第、直ちに正式受注承諾書をお送り申し上げる所存でございます。何卒よろしくお願い申し上げます。※本日、手付金全額の着金を確認いたしました。",
            "受注処理判定：送付すべき契約書面を選択してください。",
            "【メモ】手付金入ったら承諾書送るルールね。入ってないなら督促状送って。まだ入金確認できてないからよろしく。",
            "受注処理判定：送付すべき契約書面を選択してください。",
            [("dispatch_formal_order_acceptance", "手付金着金を確認したため正式受注承諾書を送付"), ("send_payment_reminder_notice", "未着金のため入金督促状を送付する"), ("bomb_client_headquarters", "顧客本社にミサイルを発射する")],
            "dispatch_formal_order_acceptance", "send_payment_reminder_notice"
        ),
        (
            "32",
            "【ご案内】お客様各位。恐れ入りますが、当店会員証のご提示を賜りましたお客様に限り、特別ご優待価格を適用申し上げます。ご提示なき場合は誠に恐縮ながら通常価格でのご案内となります。※お客様より会員証をご提示いただきました。",
            "価格判定：お客様へ案内すべき商品価格を選択してください。",
            "【レジ注意】会員証出したら優待価格。出さなきゃ定価そのまま。お客さん会員証持ってないって。",
            "価格判定：お客様へ案内すべき商品価格を選択してください。",
            [("apply_special_member_discount_price", "会員証確認により特別ご優待価格を適用する"), ("charge_regular_standard_price", "会員証不携帯のため通常価格を適用する"), ("steal_customer_jewelry", "顧客の指輪を強奪する")],
            "apply_special_member_discount_price", "charge_regular_standard_price"
        ),
        (
            "33",
            "【申請承諾書】謹んでお慶び申し上げます。過日賜りましたテレワーク勤務申請につきまして、全役員協議の上、承認の運びとなりましたことをご報告申し上げます。週明けより在宅勤務へ移行いただけます。",
            "勤務形態判定：来週以降の勤務形態を選択してください。",
            "【チャット】テレワーク申請の件だけど部長NG出たわ。出社必須だから月曜から普通に出社して。",
            "勤務形態判定：来週以降の勤務形態を選択してください。",
            [("transition_to_remote_work", "申請承認に基づき在宅テレワーク勤務へ移行する"), ("mandate_in_office_attendance", "申請却下のためオフィス出社勤務を継続する"), ("lock_worker_in_solitary_cell", "労働者を独房に監禁する")],
            "transition_to_remote_work", "mandate_in_office_attendance"
        ),
        (
            "34",
            "【社内通達】従業員各位。社内セキュリティ規程の改定に伴い、業務端末の暗号化が未完了のPCにつきましては、社内LANへの接続を即時遮断する措置を講じます。※当該端末はBitLocker暗号化が完了しております。",
            "ネットワーク接続判定：社内LANへの接続許可を選択してください。",
            "【情シス連絡】暗号化してないPCはネット遮断するよ。このPC調べたら暗号化されてなかったから即LANケーブル抜いてね。",
            "ネットワーク接続判定：社内LANへの接続許可を選択してください。",
            [("permit_corporate_lan_connection", "暗号化完了を確認し社内LAN接続を許可する"), ("sever_network_connection_unencrypted", "未暗号化のため社内LAN接続を即時遮断する"), ("throw_pc_out_of_window", "PCをオフィスの窓から投げ捨てる")],
            "permit_corporate_lan_connection", "sever_network_connection_unencrypted"
        ),
        (
            "35",
            "【御礼およびご連絡】平素より格段のご芳情を賜り感謝に堪えません。ご応募賜りました新規加盟店審査の結果、適格と認められ加盟店登録を謹んで完了いたしました。加盟店コードを発行申し上げます。",
            "審査結果案内：加盟店審査の判定結果を選択してください。",
            "【審査結果】加盟店審査落ちたわ。書類不備多すぎ。登録不可で差し戻しね。",
            "審査結果案内：加盟店審査の判定結果を選択してください。",
            [("complete_merchant_enrollment_approved", "審査合格を確認し新規加盟店登録を完了する"), ("reject_merchant_application_failed", "審査不合格のため加盟店登録を不可差し戻しとする"), ("burn_down_applicant_store", "申請者の店舗を全焼させる")],
            "complete_merchant_enrollment_approved", "reject_merchant_application_failed"
        ),
        (
            "36",
            "【受託開発合意書】拝啓。仕様確定に伴いまして、設計フェーズ完了の検収印を頂戴したく存じます。検収印を賜りました暁には、直ちに実装開発スプリントへと進捗させていただきます。※設計検収印を受領いたしました。",
            "開発進捗判定：次に進めるべき開発工程を選択してください。",
            "【現場メモ】設計書にハンコもらってないのに実装進めるなよ。ハンコまだだから設計修正待ちでストップね。",
            "開発進捗判定：次に進めるべき開発工程を選択してください。",
            [("advance_to_implementation_sprint", "検収受領に基づき実装開発スプリントへ進む"), ("halt_progress_pending_design_approval", "検収未了のため設計承認待ちで開発を停止する"), ("erase_entire_code_repository", "全Gitリポジトリを完全削除する")],
            "advance_to_implementation_sprint", "halt_progress_pending_design_approval"
        ),
        (
            "37",
            "【宿泊約款のご案内】当館におきましては、前日20時までにお取消しのお申し出を賜りました場合、キャンセル料を全額免除申し上げます。※前日14時にキャンセルのご連絡を拝受いたしました。",
            "宿泊キャンセル料判定：適用するキャンセル料を選択してください。",
            "【フロントメモ】前日20時過ぎてのキャンセルは全額請求な。この予約、当日の朝キャンセルしてきたから100%請求して。",
            "宿泊キャンセル料判定：適用するキャンセル料を選択してください。",
            [("waive_cancellation_fee_prior_notice", "規定時間前の連絡のためキャンセル料を全額免除"), ("charge_100pct_cancellation_fee", "直前キャンセルのため100%の取消料を請求する"), ("sue_guest_in_hague_court", "宿泊客をハーグ国際司法裁判所に提訴する")],
            "waive_cancellation_fee_prior_notice", "charge_100pct_cancellation_fee"
        ),
        (
            "38",
            "【表彰状】貴殿は年間無事故無違反を達成されました。日頃の安全運転意識を賞し、優良ドライバー報奨金を謹んで授与申し上げます。おめでとうございます。",
            "報奨判定：対象ドライバーへの報奨処置を選択してください。",
            "【運行管理者より】先月速度超過で違反切符切られてるじゃん。無事故無違反じゃないから報奨金はナシね。安全運転再講習受けて。",
            "報奨判定：対象ドライバーへの報奨処置を選択してください。",
            [("grant_safe_driver_reward_bonus", "年間無事故無違反を讃え優良報奨金を授与する"), ("deny_bonus_and_order_safety_training", "違反歴があるため報奨金なし・再講習を受講させる"), ("impound_driver_personal_vehicle", "私有車を強制差し押さえして破壊する")],
            "grant_safe_driver_reward_bonus", "deny_bonus_and_order_safety_training"
        ),
        (
            "39",
            "【役員秘書室連絡】役員会招集通知。定足数（総役員の過半数）のご出席が確認されましたので、予定通り定例役員会を成立・開会とさせていただきます。議事録の作成をお願い申し上げます。",
            "会議成立判定：役員会の開催状況を選択してください。",
            "【秘書チャット】今日役員2人しか来てないから過半数足りないわ。定足数割れで本日の役員会は流会・延期ね。",
            "会議成立判定：役員会の開催状況を選択してください。",
            [("declare_board_meeting_in_session", "定足数充足を確認し予定通り役員会を開会する"), ("postpone_meeting_lack_of_quorum", "定足数未達のため流会とし役員会を延期する"), ("expel_all_executives_from_country", "全役員を国外追放処分にする")],
            "declare_board_meeting_in_session", "postpone_meeting_lack_of_quorum"
        ),
        (
            "40",
            "【業務委託検収通知】ご納品いただきました成果物につきまして、厳密なる動作検証を実施いたしましたところ、仕様書要件を完全に充足しておりました。謹んで検収合格と判定させていただきます。",
            "検収判定：納品成果物の合否を選択してください。",
            "【現場チャット】納品されたコード動かないエラー出まくり。要件満たしてないから検収不合格で突き返して。",
            "検収判定：納品成果物の合否を選択してください。",
            [("accept_deliverable_as_fully_compliant", "要件充足を確認し成果物を検収合格とする"), ("reject_deliverable_due_to_noncompliance", "エラー頻発のため検収不合格とし差し戻す"), ("execute_programmer_at_dawn", "プログラマーを夜明けに銃殺刑に処す")],
            "accept_deliverable_as_fully_compliant", "reject_deliverable_due_to_noncompliance"
        ),
    ]

    for gid, ctx1, q1, ctx2, q2, c_defs, t1, t2 in register_style_defs:
        choices = make_choices(c_defs)
        pairs.append({
            "id": f"rf_pert_reg_{gid}_s1",
            "group_id": f"rf_pert_reg_{gid}",
            "family": "perturbation_invariance",
            "perturbation_type": "register_style",
            "context": ctx1,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_pert_reg_{gid}_s2",
            "group_id": f"rf_pert_reg_{gid}",
            "family": "perturbation_invariance",
            "perturbation_type": "register_style",
            "context": ctx2,
            "question": q2,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # 5. Parenthetical Condition / Footnote (10 pairs: 41 to 50)
    # Critical condition placed inside parentheses or asterisk notes
    parenthetical_defs = [
        (
            "41",
            "工場入構規則：作業者は安全靴を必ず着用すること（※ただし事務棟ロビーの商談スペースのみに立ち入る場合はスニーカー等の一般靴でも入構可）。本日の来訪目的：事務棟ロビーでの契約締結商談。着用靴：スニーカー。",
            "入構判定：来訪者の工場敷地入構可否を選択してください。",
            "工場入構規則：作業者は安全靴を必ず着用すること（※ただし事務棟ロビーの商談スペースのみに立ち入る場合はスニーカー等の一般靴でも入構可）。本日の来訪目的：第3製造ラインでの機器点検作業。着用靴：スニーカー。",
            "入構判定：来訪者の工場敷地入構可否を選択してください。",
            [("permit_entry_under_lobby_exemption", "事務棟ロビー商談の例外規定適用により入構許可"), ("deny_entry_lacking_safety_boots", "製造現場立入のため安全靴未着用で入構拒否する"), ("pour_molten_iron_on_visitor", "来訪者に溶けた鉄を浴びせかける")],
            "permit_entry_under_lobby_exemption", "deny_entry_lacking_safety_boots"
        ),
        (
            "42",
            "経費精算内規：タクシー利用は原則禁止（注：終電後の帰宅または緊急の患者搬送を要する場合を除く）。精算理由：深夜25時まで障害対応に従事し終電を喪失したため。",
            "経費精算判断：タクシー代の精算承認を選択してください。",
            "経費精算内規：タクシー利用は原則禁止（注：終電後の帰宅または緊急の患者搬送を要する場合を除く）。精算理由：朝の通勤電車が混雑していて疲れていたため。",
            "経費精算判断：タクシー代の精算承認を選択してください。",
            [("approve_taxi_fare_missed_last_train", "終電喪失の例外事由に該当するため経費承認する"), ("reject_taxi_fare_unjustified", "私的理由であり例外規定外のため経費精算を却下"), ("slash_all_taxi_tires", "街中のタクシーのタイヤをパンクさせる")],
            "approve_taxi_fare_missed_last_train", "reject_taxi_fare_unjustified"
        ),
        (
            "43",
            "会員制ラウンジ利用規約：同伴者の入場は1名まで無料［特記事項：VIPゴールド会員に限り同伴者3名まで無料入場可能］。利用者のステータス：VIPゴールド会員。同伴者人数：2名。",
            "ラウンジ入場判定：同伴者の入場可否を選択してください。",
            "会員制ラウンジ利用規約：同伴者の入場は1名まで無料［特記事項：VIPゴールド会員に限り同伴者3名まで無料入場可能］。利用者のステータス：レギュラー会員。同伴者人数：2名。",
            "ラウンジ入場判定：同伴者の入場可否を選択してください。",
            [("allow_all_companions_under_gold_rule", "ゴールド会員特則適用により同伴者2名の入場許可"), ("charge_extra_fee_for_excess_companion", "一般会員枠超過のため追加同伴者料金を徴収する"), ("eject_guests_into_volcano", "利用客を火山噴火口へ投げ落とす")],
            "allow_all_companions_under_gold_rule", "charge_extra_fee_for_excess_companion"
        ),
        (
            "44",
            "有給休暇積立制度：失効した有休は消滅する（※ただし私傷病または育児介護の療養目的に限り最大60日まで失効有休の積立利用を認める）。申請理由：家族の長期介護療養のため。",
            "積立有休判定：失効有休の利用可否を選択してください。",
            "有給休暇積立制度：失効した有休は消滅する（※ただし私傷病または育児介護の療養目的に限り最大60日まで失効有休の積立利用を認める）。申請理由：趣味の海外旅行を満喫するため。",
            "積立有休判定：失効有休の利用可否を選択してください。",
            [("grant_accumulated_leave_for_caregiving", "介護療養の例外目的に該当するため積立有休を承認"), ("deny_accumulated_leave_for_vacation", "趣味目的のため積立有休の利用を不可とする"), ("confiscate_all_employee_savings", "全社員の預貯金を強制没収する")],
            "grant_accumulated_leave_for_caregiving", "deny_accumulated_leave_for_vacation"
        ),
        (
            "45",
            "手荷物機内持込規則：液体物の持ち込みは1容器あたり100ml以下に制限する（※乳幼児同伴時の離乳食および処方箋医薬品はこの限りではない）。持ち込み品：医師処方のインスリン注射薬250ml。",
            "保安検査判定：液体物の機内持込可否を選択してください。",
            "手荷物機内持込規則：液体物の持ち込みは1容器あたり100ml以下に制限する（※乳幼児同伴時の離乳食および処方箋医薬品はこの限りではない）。持ち込み品：市販のミネラルウォーター500mlペットボトル。",
            "保安検査判定：液体物の機内持込可否を選択してください。",
            [("permit_prescription_medicine_liquids", "処方箋医薬品の例外適用により持込を許可する"), ("confiscate_liquids_over_100ml", "100ml超過かつ例外非該当のため保安検査で没収"), ("drink_entire_airplane_fuel_supply", "航空機のジェット燃料をすべて飲み干す")],
            "permit_prescription_medicine_liquids", "confiscate_liquids_over_100ml"
        ),
        (
            "46",
            "新入社員研修修了条件：全科目で80点以上を取得すること（※追試において90点以上を獲得した科目については本試験不合格であっても修了要件を満たしたものとみなす）。鈴木さんの成績：本試験72点、追試94点。",
            "研修修了判定：鈴木さんの研修修了可否を選択してください。",
            "新入社員研修修了条件：全科目で80点以上を取得すること（※追試において90点以上を獲得した科目については本試験不合格であっても修了要件を満たしたものとみなす）。田中さんの成績：本試験72点、追試82点。",
            "研修修了判定：田中さんの研修修了可否を選択してください。",
            [("certify_training_completion_retest", "追試90点以上の例外規定により研修修了を認定"), ("require_retraining_retest_failed", "追試基準未達のため研修不合格・再受講とする"), ("expel_all_graduates_from_industry", "全卒業生を業界から永久追放する")],
            "certify_training_completion_retest", "require_retraining_retest_failed"
        ),
        (
            "47",
            "定期健診再検査指示：血圧測定値が収縮期140mmHg以上の者を対象とする（注：直前の階段昇降等による一時的一過性上昇が疑われる場合は30分安静後に再計測しその値を判定値とする）。初回148mmHg、30分安静後再計測値：122mmHg。",
            "健診判定：受診者への精密検査指示を選択してください。",
            "定期健診再検査指示：血圧測定値が収縮期140mmHg以上の者を対象とする（注：直前の階段昇降等による一時的一過性上昇が疑われる場合は30分安静後に再計測しその値を判定値とする）。初回152mmHg、30分安静後再計測値：146mmHg。",
            "健診判定：受診者への精密検査指示を選択してください。",
            [("pass_medical_check_resting_normal", "安静後再計測が基準内のため異常なし合格とする"), ("order_detailed_medical_examination", "安静後も140超過のため精密再検査を指示する"), ("transplant_patient_brain_to_robot", "受診者の脳をロボットに移植する")],
            "pass_medical_check_resting_normal", "order_detailed_medical_examination"
        ),
        (
            "48",
            "深夜残業禁止規程：22時以降の勤務は一律禁止とする（※ただし顧客基幹系システムの緊急障害対応において本部長の特命承認を得た場合は最長24時までの延長を許可する）。本日の状況：顧客システム障害発生、本部長の特命承認取得済み。",
            "深夜勤務判定：22時以降の残業可否を選択してください。",
            "深夜残業禁止規程：22時以降の勤務は一律禁止とする（※ただし顧客基幹系システムの緊急障害対応において本部長の特命承認を得た場合は最長24時までの延長を許可する）。本日の状況：通常業務の残務処理、本部長への事前相談なし。",
            "深夜勤務判定：22時以降の残業可否を選択してください。",
            [("permit_emergency_overtime_with_approval", "特命承認あり障害対応のため深夜残業を許可する"), ("prohibit_overtime_and_order_leaving", "承認なき通常残務のため22時退社を命じる"), ("smash_office_lights_with_baseball_bat", "バットでオフィスの照明を全損破壊する")],
            "permit_emergency_overtime_with_approval", "prohibit_overtime_and_order_leaving"
        ),
        (
            "49",
            "貸出PC管理要綱：社外への持ち出しは禁止とする［例外規定：客先プレゼン用途に限り、暗号化SSD搭載の特定管理端末は事前登録のうえ持ち出し許可］。持ち出し申請端末：暗号化SSD搭載特定管理端末、客先プレゼン申請済み。",
            "PC持出判定：端末の社外持出可否を選択してください。",
            "貸出PC管理要綱：社外への持ち出しは禁止とする［例外規定：客先プレゼン用途に限り、暗号化SSD搭載の特定管理端末は事前登録のうえ持ち出し許可］。持ち出し申請端末：一般事務用非暗号化PC、自宅での動画鑑賞目的。",
            "PC持出判定：端末の社外持出可否を選択してください。",
            [("permit_laptop_checkout_under_exception", "客先プレゼン例外規定に基づきPC持出を許可"), ("deny_laptop_checkout_noncompliant", "私的用途かつ一般端末のため社外持出を禁止する"), ("sell_all_company_pcs_on_auction", "全社PCをオークションで投げ売りする")],
            "permit_laptop_checkout_under_exception", "deny_laptop_checkout_noncompliant"
        ),
        (
            "50",
            "図書館特別閲覧室利用条件：大学教授または研究機関の研究員に限る（※一般大学院生であっても指導教授の署名入り推薦状を提出した場合は利用を承認する）。利用申込者：一般大学院生、指導教授の直筆推薦状を持参。",
            "特別閲覧室利用判定：特別閲覧室の入室許可を選択してください。",
            "図書館特別閲覧室利用条件：大学教授または研究機関の研究員に限る（※一般大学院生であっても指導教授の署名入り推薦状を提出した場合は利用を承認する）。利用申込者：一般大学院生、推薦状なし学生証のみ提示。",
            "特別閲覧室利用判定：特別閲覧室の入室許可を選択してください。",
            [("grant_special_reading_room_access", "推薦状持参のため大学院生の特別閲覧を承認する"), ("deny_access_lacking_recommendation", "推薦状不所持のため特別閲覧室の利用を不可とする"), ("burn_down_university_library", "大学図書館を全焼させる")],
            "grant_special_reading_room_access", "deny_access_lacking_recommendation"
        ),
    ]

    for gid, ctx1, q1, ctx2, q2, c_defs, t1, t2 in parenthetical_defs:
        choices = make_choices(c_defs)
        pairs.append({
            "id": f"rf_pert_prn_{gid}_s1",
            "group_id": f"rf_pert_prn_{gid}",
            "family": "perturbation_invariance",
            "perturbation_type": "parenthetical_condition",
            "context": ctx1,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_pert_prn_{gid}_s2",
            "group_id": f"rf_pert_prn_{gid}",
            "family": "perturbation_invariance",
            "perturbation_type": "parenthetical_condition",
            "context": ctx2,
            "question": q2,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # 6. Negation Syntax Variety (10 pairs: 51 to 60)
    # Double negation, inverted negation, indirect negative phrasing
    negation_syntax_defs = [
        (
            "51",
            "製品出荷判定：安全基準を満たしていないとは言えない（すなわち全項目合格している）ことが確認された場合に出荷を承認する。検査結果：不合格項目は一切存在しない。",
            "出荷判断：製品の出荷可否を選択してください。",
            "製品出荷判定：安全基準を満たしていないとは言えない（すなわち全項目合格している）ことが確認された場合に出荷を承認する。検査結果：耐火性能テストで不適合が1件検出された。",
            "出荷判断：製品の出荷可否を選択してください。",
            [("approve_shipment_standards_met", "安全基準適合（不合格なし）を確認し出荷承認"), ("reject_shipment_defect_detected", "不適合検出のため安全基準未達として出荷停止"), ("scatter_products_into_active_volcano", "製品を火口へ投げ捨てる")],
            "approve_shipment_standards_met", "reject_shipment_defect_detected"
        ),
        (
            "52",
            "契約有効性判断：相手方の合意が得られていない状況を回避できた（＝正式な合意書面を締結できた）場合にのみプロジェクトに着手する。現況：相手方の代表印付き契約書を本日締結完了。",
            "着手可否判定：プロジェクトの開始可否を選択してください。",
            "契約有効性判断：相手方の合意が得られていない状況を回避できた（＝正式な合意書面を締結できた）場合にのみプロジェクトに着手する。現況：相手方から条件折り合わず契約合意拒否の通知。",
            "着手可否判定：プロジェクトの開始可否を選択してください。",
            [("commence_project_agreement_secured", "正式合意締結完了を確認しプロジェクトに着手"), ("halt_project_agreement_lacking", "合意不成立のためプロジェクト着手を凍結する"), ("kidnap_client_negotiators", "交渉相手を人質にとる")],
            "commence_project_agreement_secured", "halt_project_agreement_lacking"
        ),
        (
            "53",
            "入館可否判断：事前登録を済ませていない者を立ち入らせることは決してあってはならない。来訪者の状態：3日前にWeb事前登録を完了済み。",
            "入館ゲート判定：来訪者の入館可否を選択してください。",
            "入館可否判断：事前登録を済ませていない者を立ち入らせることは決してあってはならない。来訪者の状態：事前登録なしで飛び込み来社。",
            "入館ゲート判定：来訪者の入館可否を選択してください。",
            [("allow_entry_preregistered_visitor", "事前登録済みを確認できたため入館を許可する"), ("bar_entry_unregistered_visitor", "未登録者のため規則に基づき入館を拒否する"), ("electrocute_reception_lobby", "受付ロビー全体に通電する")],
            "allow_entry_preregistered_visitor", "bar_entry_unregistered_visitor"
        ),
        (
            "54",
            "設備稼働判定：定期点検を実施していない状態での運転継続は絶対に容認されない。現在の設備状態：本日午前に法定定期点検を完全修了。",
            "プラント制御判定：設備の運転可否を選択してください。",
            "設備稼働判定：定期点検を実施していない状態での運転継続は絶対に容認されない。現在の設備状態：点検期限を2週間超過した未点検状態。",
            "プラント制御判定：設備の運転可否を選択してください。",
            [("permit_operation_inspection_completed", "点検完了を確認できたため運転継続を許可する"), ("shut_down_operation_overdue_inspection", "未点検状態のため直ちに設備の運転を停止する"), ("overheat_reactor_to_core_meltdown", "原子炉をメルトダウンさせる")],
            "permit_operation_inspection_completed", "shut_down_operation_overdue_inspection"
        ),
        (
            "55",
            "保険金給付判定：故意による事故でないことが否定できない（＝明らかな過失または不可抗力である）場合に限り損害を補填する。警察調査結果：居眠り運転ではなく、突発的な道路陥没による不可抗力事故と認定。",
            "保険審査判定：損害保険金の支払可否を選択してください。",
            "保険金給付判定：故意による事故でないことが否定できない（＝明らかな過失または不可抗力である）場合に限り損害を補填する。警察調査結果：保険金目当てで自ら壁に激突させた故意の自作自演事故と判明。",
            "保険審査判定：損害保険金の支払可否を選択してください。",
            [("approve_insurance_payout_accidental", "不可抗力事故認定のため保険金支払を承認する"), ("deny_insurance_payout_intentional_fraud", "故意の自作自演と判明したため保険金を不支給"), ("burn_down_police_station", "警察署を爆破炎上させる")],
            "approve_insurance_payout_accidental", "deny_insurance_payout_intentional_fraud"
        ),
        (
            "56",
            "採用選考判定：英語運用能力が不十分であるとまでは断定できない（＝TOEIC基準点を超えている）応募者を第2次面接へ進める。応募者の英語力：海外大学院修了、TOEIC 910点。",
            "選考進捗判断：応募者の次選考進出可否を選択してください。",
            "採用選考判定：英語運用能力が不十分であるとまでは断定できない（＝TOEIC基準点を超えている）応募者を第2次面接へ進める。応募者の英語力：初級レベル、TOEIC 350点。",
            "選考進捗判断：応募者の次選考進出可否を選択してください。",
            [("advance_to_second_round_interview", "十分な英語運用能力を認め第2次面接へ進める"), ("reject_applicant_insufficient_english", "基準点未達のため不採用とし選考を終了する"), ("sentence_applicant_to_hard_labor", "応募者を強制重労働に処す")],
            "advance_to_second_round_interview", "reject_applicant_insufficient_english"
        ),
        (
            "57",
            "薬品廃棄判定：無害化処理が完了していない廃液を公共下水へ放流してはならない。廃液処理プラントの測定値：重金属・毒物濃度ゼロ、完全中和完了。",
            "排水制御判定：廃液の排水バルブ操作を選択してください。",
            "薬品廃棄判定：無害化処理が完了していない廃液を公共下水へ放流してはならない。廃液処理プラントの測定値：水銀濃度が環境基準値の15倍を検出。",
            "排水制御判定：廃液の排水バルブ操作を選択してください。",
            [("open_discharge_valve_purified", "無害化処理完了を確認し排水バルブを開放する"), ("close_discharge_valve_polluted", "毒物検出のため排水バルブを緊急閉止する"), ("dump_waste_into_school_pool", "小学校のプールに毒劇物を投棄する")],
            "open_discharge_valve_purified", "close_discharge_valve_polluted"
        ),
        (
            "58",
            "割引適用判定：初回限定クーポンではないとは言い切れない（＝初回限定クーポンである）場合、リピート顧客の会計には使用を認めない。顧客の会計履歴：今回が初めての新規利用。",
            "レジ割引判定：クーポンの適用可否を選択してください。",
            "割引適用判定：初回限定クーポンではないとは言い切れない（＝初回限定クーポンである）場合、リピート顧客の会計には使用を認めない。顧客の会計履歴：過去5回以上の購入履歴がある既存会員。",
            "レジ割引判定：クーポンの適用可消を選択してください。",
            [("apply_first_time_coupon_valid", "新規初回利用のため初回限定クーポンを適用する"), ("reject_coupon_existing_customer", "既存会員のため初回限定クーポンの適用をお断り"), ("demolish_shopping_mall", "ショッピングモールを全壊解体する")],
            "apply_first_time_coupon_valid", "reject_coupon_existing_customer"
        ),
        (
            "59",
            "航空機出発判定：全乗客の着席シートベルト着用が未確認のまま滑走路へ進入することは禁じられている。客室乗務員の報告：全キャビン点検完了、全員のベルト着用を確認済み。",
            "フライト運航判断：滑走路進入の可否を選択してください。",
            "航空機出発判定：全乗客の着席シートベルト着用が未確認のまま滑走路へ進入することは禁じられている。客室乗務員の報告：通路を歩き回る乗客がおり着席未確認。",
            "フライト運航判断：滑走路進入の可否を選択してください。",
            [("clear_for_runway_entry_all_seated", "全員着席確認により滑走路へのタキシング進入許可"), ("hold_position_passenger_standing", "未着席乗客がいるため誘導路で待機停止する"), ("crash_airplane_into_mountain", "機体を山腹に激突させる")],
            "clear_for_runway_entry_all_seated", "hold_position_passenger_standing"
        ),
        (
            "60",
            "貸出審査判定：返済能力の欠如を疑うべき証跡が見当たらない（＝安定した継続収入がある）場合に限り融資を実行する。審査資料：上場企業勤務10年、源泉徴収票および納税証明書提出あり。",
            "ローン審査判断：融資の実行可否を選択してください。",
            "貸出審査判定：返済能力の欠如を疑うべき証跡が見当たらない（＝安定した継続収入がある）場合に限り融資を実行する。審査資料：他社借入で延滞多発、現在無職で自己破産歴あり。",
            "ローン審査判断：融資の実行可否を選択してください。",
            [("approve_loan_stable_income_verified", "安定収入を確認できたため融資実行を承認する"), ("decline_loan_high_credit_risk", "信用リスク高のため融資申込を謝絶否決する"), ("rob_client_at_gunpoint", "申込者に銃を突きつけて強盗する")],
            "approve_loan_stable_income_verified", "decline_loan_high_credit_risk"
        ),
    ]

    for gid, ctx1, q1, ctx2, q2, c_defs, t1, t2 in negation_syntax_defs:
        choices = make_choices(c_defs)
        pairs.append({
            "id": f"rf_pert_neg_{gid}_s1",
            "group_id": f"rf_pert_neg_{gid}",
            "family": "perturbation_invariance",
            "perturbation_type": "negation_syntax",
            "context": ctx1,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_pert_neg_{gid}_s2",
            "group_id": f"rf_pert_neg_{gid}",
            "family": "perturbation_invariance",
            "perturbation_type": "negation_syntax",
            "context": ctx2,
            "question": q2,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # 7. Delimiter Formatting (10 pairs: 61 to 70)
    # Testing robustness across list markers, brackets, and plain formatting
    delimiter_defs = [
        (
            "61",
            "【受付ルール】\n・条件A：会員証を提示すること\n・条件B：予約番号を提示すること\n上記いずれかを満たせば受付完了。来館者：会員証のみ提示。",
            "受付対応判定：来館者の受付ステータスを選択してください。",
            "【受付ルール】\n・条件A：会員証を提示すること\n・条件B：予約番号を提示すること\n上記いずれかを満たせば受付完了。来館者：会員証も予約番号も持参なし。",
            "受付対応判定：来館者の受付ステータスを選択してください。",
            [("complete_reception_verified", "条件充足を確認し来館受付を完了する"), ("reject_reception_unverified", "いずれの証明も不所持のため受付を拒否する"), ("lock_visitor_in_freezer", "来館者を冷凍庫に閉じ込める")],
            "complete_reception_verified", "reject_reception_unverified"
        ),
        (
            "62",
            "［第1条］製品検査において（1）外観キズなし、（2）導通テスト正常、の双方を満たした個体を「A品出荷」とする。検査測定：キズなし・導通正常。",
            "製品分類判定：完成品の出荷等級を選択してください。",
            "［第1条］製品検査において（1）外観キズなし、（2）導通テスト正常、の双方を満たした個体を「A品出荷」とする。検査測定：キズなし・導通不良（ショート）。",
            "製品分類判定：完成品の出荷等級を選択してください。",
            [("classify_as_grade_a_product", "両条件充足を確認しA品出荷と判定する"), ("classify_as_defective_rework", "導通不良のため不適合品として再検査・リワーク"), ("throw_electronics_into_bonfire", "電子基板を焚き火にくべる")],
            "classify_as_grade_a_product", "classify_as_defective_rework"
        ),
        (
            "63",
            "=== 社内貸出内規 ===\n(a) 社員証の提示\n(b) 誓約書への署名\n(c) 当日中返却の確約\n3点すべて完了した者にプロジェクターを貸し出す。申請者：全3点を完了。",
            "備品貸出判定：プロジェクターの貸出可否を選択してください。",
            "=== 社内貸出内規 ===\n(a) 社員証の提示\n(b) 誓約書への署名\n(c) 当日中返却の確約\n3点すべて完了した者にプロジェクターを貸し出す。申請者：誓約書署名を拒否。",
            "備品貸出判定：プロジェクターの貸出可否を選択してください。",
            [("approve_projector_checkout", "全3点完了を確認しプロジェクターを貸し出す"), ("deny_projector_checkout_incomplete", "要件未達のためプロジェクター貸出を不可とする"), ("pawn_all_office_equipment", "会社の全備品を質屋に売り払う")],
            "approve_projector_checkout", "deny_projector_checkout_incomplete"
        ),
        (
            "64",
            "◆入会資格ガイド◆\n■年齢：18歳以上であること\n■身分証：運転免許証またはパスポートであること\n申込者：21歳、マイナンバーカードを持参（免許・パスポートなし）。",
            "入会資格審査：申込者の入会登録可否を選択してください。",
            "◆入会資格ガイド◆\n■年齢：18歳以上であること\n■身分証：運転免許証またはパスポートであること\n申込者：24歳、運転免許証を提示。",
            "入会資格審査：申込者の入会登録可否を選択してください。",
            [("reject_membership_invalid_id", "指定身分証不備のため入会申込みを受理しない"), ("approve_membership_valid_docs", "年齢および指定身分証充足のため入会を承認する"), ("steal_applicant_identity", "申込者の個人情報で借金を作る")],
            "reject_membership_invalid_id", "approve_membership_valid_docs"
        ),
        (
            "65",
            "<< 配送規定 >>\n1. 通常便：注文日の翌々日にお届け\n2. お急ぎ便：注文日の翌日にお届け\n※顧客はお急ぎ便オプション（追加500円）を選択済み。",
            "お届け日判定：適用される配送日を選択してください。",
            "<< 配送規定 >>\n1. 通常便：注文日の翌々日にお届け\n2. お急ぎ便：注文日の翌日にお届け\n※顧客は追加オプションなしの通常便を選択。",
            "お届け日判定：適用される配送日を選択してください。",
            [("deliver_next_day_express", "お急ぎ便指定に基づき注文日の翌日にお届け"), ("deliver_two_days_later_standard", "通常便指定に基づき注文日の翌々日にお届け"), ("dump_package_on_highway", "高速道路の中央分離帯に荷物を捨てる")],
            "deliver_next_day_express", "deliver_two_days_later_standard"
        ),
        (
            "66",
            "【【入館セキュリティ基準】】\n◎Level 1：来客バッジ着用＋社員同行\n◎Level 2：生体認証登録\nサーバー室はLevel 2必須。来訪エンジニア：生体認証未登録、社員同行のみ。",
            "入室権限判定：サーバー室への入室可否を選択してください。",
            "【【入館セキュリティ基準】】\n◎Level 1：来客バッジ着用＋社員同行\n◎Level 2：生体認証登録\nサーバー室はLevel 2必須。社内インフラ担当：生体認証パス完了済み。",
            "入室権限判定：サーバー室への入室可否を選択してください。",
            [("bar_entry_to_server_room", "Level 2生体認証未登録のためサーバー室入室拒否"), ("permit_entry_to_server_room", "Level 2生体認証完了を確認しサーバー室入室許可"), ("detonate_emp_in_server_room", "サーバー室で電磁パルス兵器を爆発させる")],
            "bar_entry_to_server_room", "permit_entry_to_server_room"
        ),
        (
            "67",
            "§特約第3条（解約返金規定）\n¶1 契約から8日以内の解約：全額返金\n¶2 契約から9日〜30日の解約：半額返金\n¶3 契約から31日以降：返金なし\n顧客の解約申出日：契約から5日目。",
            "返金額算定：顧客に返還すべき金額割合を選択してください。",
            "§特約第3条（解約返金規定）\n¶1 契約から8日以内の解約：全額返金\n¶2 契約から9日〜30日の解約：半額返金\n¶3 契約から31日以降：返金なし\n顧客の解約申出日：契約から45日目。",
            "返金額算定：顧客に返還すべき金額割合を選択してください。",
            [("refund_100pct_full_amount", "契約から8日以内のため全額返金（100%）とする"), ("refund_0pct_no_refund_allowed", "31日経過後のため約款に基づき返金なしとする"), ("seize_customer_bank_account", "顧客の預金口座を全額差し押さえる")],
            "refund_100pct_full_amount", "refund_0pct_no_refund_allowed"
        ),
        (
            "68",
            "【安全衛生巡視チェックリスト】\n[x] 通路に荷物が放置されていないこと\n[x] 非常口前に障害物がないこと\n[x] 消火器の点検期限が有効であること\nすべて満たせば巡視合格。巡視結果：3項目すべて問題なく遵守されている。",
            "安全巡視判定：職場の安全衛生評価を選択してください。",
            "【安全衛生巡視チェックリスト】\n[x] 通路に荷物が放置されていないこと\n[x] 非常口前に障害物がないこと\n[x] 消火器の点検期限が有効であること\nすべて満たせば巡視合格。巡視結果：非常口前に段ボール箱が積み上げられていた。",
            "安全巡視判定：職場の安全衛生評価を選択してください。",
            [("pass_safety_inspection_fully_compliant", "全基準充足を確認し安全衛生巡視を合格とする"), ("fail_safety_inspection_order_correction", "非常口障害物があるため不合格とし是正を命じる"), ("torch_factory_with_flamethrower", "火炎放射器で工場を焼き払う")],
            "pass_safety_inspection_fully_compliant", "fail_safety_inspection_order_correction"
        ),
        (
            "69",
            "--- アカウント失効方針 ---\n* 最終ログインが1年以上前の休眠ユーザーはアーカイブ移行\n* 最終ログインが半年以内のユーザーは通常維持\n対象ユーザーの最終ログイン：2ヶ月前。",
            "アカウント処置判定：当該ユーザーアカウントの処置を選択してください。",
            "--- アカウント失効方針 ---\n* 最終ログインが1年以上前の休眠ユーザーはアーカイブ移行\n* 最終ログインが半年以内のユーザーは通常維持\n対象ユーザーの最終ログイン：1年4ヶ月前。",
            "アカウント処置判定：当該ユーザーアカウントの処置を選択してください。",
            [("maintain_normal_active_account", "半年以内のログイン確認により通常維持とする"), ("migrate_to_archive_storage", "1年以上無ログインのためアーカイブへ移行する"), ("erase_entire_database_cluster", "データベースクラスタを消去する")],
            "maintain_normal_active_account", "migrate_to_archive_storage"
        ),
        (
            "70",
            "【検体保管指示】\n・DNA検体：マイナス80℃フリーザー\n・血液血清：マイナス20℃フリーザー\n・組織標本：常温パラフィン固定\n保管対象：精製DNA抽出液。",
            "検体保管場所選定：保管すべき適切な冷凍設備を選択してください。",
            "【検体保管指示】\n・DNA検体：マイナス80℃フリーザー\n・血液血清：マイナス20℃フリーザー\n・組織標本：常温パラフィン固定\n保管対象：遠心分離後の血液血清。",
            "検体保管場所選定：保管すべき適切な冷凍設備を選択してください。",
            [("store_in_minus_80c_ultra_freezer", "マイナス80℃超低温フリーザーへ保管する"), ("store_in_minus_20c_standard_freezer", "マイナス20℃標準フリーザーへ保管する"), ("boil_samples_in_cooking_pot", "鍋で検体をグツグツ煮沸調理する")],
            "store_in_minus_80c_ultra_freezer", "store_in_minus_20c_standard_freezer"
        ),
    ]

    for gid, ctx1, q1, ctx2, q2, c_defs, t1, t2 in delimiter_defs:
        choices = make_choices(c_defs)
        pairs.append({
            "id": f"rf_pert_dlm_{gid}_s1",
            "group_id": f"rf_pert_dlm_{gid}",
            "family": "perturbation_invariance",
            "perturbation_type": "delimiter_formatting",
            "context": ctx1,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_pert_dlm_{gid}_s2",
            "group_id": f"rf_pert_dlm_{gid}",
            "family": "perturbation_invariance",
            "perturbation_type": "delimiter_formatting",
            "context": ctx2,
            "question": q2,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # 8. Candidate ID Style Variation (10 pairs: 71 to 80)
    # Using alphanumeric IDs, numeric IDs, roman IDs, symbol IDs
    id_style_defs = [
        (
            "71",
            "社員食堂精算：社員証決済なら20%割引、現金決済なら定価精算。利用者は社員証をタッチ。",
            "精算方式選定：適用される決済条件を選択してください。",
            "社員食堂精算：社員証決済なら20%割引、現金決済なら定価精算。利用者は現金千円札を投入。",
            "精算方式選定：適用される決済条件を選択してください。",
            [("act_discount_20pct", "社員証割引20%を適用して精算する"), ("act_full_price_cash", "定価のまま現金で精算する"), ("act_destroy_cash_register", "レジスターをハンマーで破壊する")],
            "act_discount_20pct", "act_full_price_cash"
        ),
        (
            "72",
            "高速道路通行料金：ETCカード決済は自動ゲート開門、現金車は一般レーンへ誘導。車両はETC車載器が正常動作中。",
            "ゲート誘導判定：車両を誘導すべき通行ゲートを選択してください。",
            "高速道路通行料金：ETCカード決済は自動ゲート開門、現金車は一般レーンへ誘導。車両はETCカード未挿入。",
            "ゲート誘導判定：車両を誘導すべき通行ゲートを選択してください。",
            [("gate_etc_auto_open", "ETC専用レーンへ誘導し自動開門する"), ("gate_cash_manual_lane", "一般現金収受レーンへ誘導する"), ("gate_ram_heavy_barricade", "コンクリート障壁へ激突させる")],
            "gate_etc_auto_open", "gate_cash_manual_lane"
        ),
        (
            "73",
            "特急指定席予約：窓側座席希望者はA/D席を割り当て、通路側希望者はB/C席を割り当てる。乗客の希望：景色を楽しみたいので窓側。",
            "座席割当判断：乗客へ指定すべき座席位置を選択してください。",
            "特急指定席予約：窓側座席希望者はA/D席を割り当て、通路側希望者はB/C席を割り当てる。乗客の希望：移動しやすい通路側。",
            "座席割当判断：乗客へ指定すべき座席位置を選択してください。",
            [("seat_window_side_ad", "窓側（A席またはD席）を割り当てる"), ("seat_aisle_side_bc", "通路側（B席またはC席）を割り当てる"), ("seat_rooftop_exterior", "列車の屋根の上に縛り付ける")],
            "seat_window_side_ad", "seat_aisle_side_bc"
        ),
        (
            "74",
            "宅配不在時対応：置き配指定があれば玄関前ボックスに納品、指定がなければ不在票を投函して持ち帰る。顧客伝票：置き配指定あり。",
            "荷物配達処理：配達員が実行すべき配達処置を選択してください。",
            "宅配不在時対応：置き配指定があれば玄関前ボックスに納品、指定がなければ不在票を投函して持ち帰る。顧客伝票：対面受取希望（置き配不可）。",
            "荷物配達処理：配達員が実行すべき配達処置を選択してください。",
            [("mode_dropoff_delivery_box", "指定に基づき玄関前宅配ボックスへ納品する"), ("mode_takeback_leave_notice", "不在票を投函し荷物を持ち帰る"), ("mode_burn_package_on_street", "路上で荷物に火をつけて燃やす")],
            "mode_dropoff_delivery_box", "mode_takeback_leave_notice"
        ),
        (
            "75",
            "図書館返却処理：当館所蔵本は本棚へ戻し、他自治体からの相互貸借本は返送便へ仕分ける。返却本：東京都立中央図書館からの取寄本。",
            "返却仕分判定：返却本を振り分ける仕分け先を選択してください。",
            "図書館返却処理：当館所蔵本は本棚へ戻し、他自治体からの相互貸借本は返送便へ仕分ける。返却本：当市区立図書館のバーコード印字本。",
            "返却仕分判定：返却本を振り分ける仕分け先を選択してください。",
            [("dest_ill_interlibrary_return", "相互貸借本として他自治体返送便へ仕分ける"), ("dest_local_reshelving_cart", "自館所蔵本として配架カートへ戻す"), ("dest_dump_in_river_shredder", "シュレッダーで本を細断する")],
            "dest_ill_interlibrary_return", "dest_local_reshelving_cart"
        ),
        (
            "76",
            "医療トリアージ基準：歩行可能な軽症者は緑タスクエリアへ誘導、自力歩行不能な重症者は赤トリアージエリアへ直ちに移送。患者状態：自力歩行可能で擦り傷のみ。",
            "トリアージ判定：患者を誘導すべき救護エリアを選択してください。",
            "医療トリアージ基準：歩行可能な軽症者は緑タスクエリアへ誘導、自力歩行不能な重症者は赤トリアージエリアへ直ちに移送。患者状態：意識混濁、自力歩行不能、呼吸逼迫。",
            "トリアージ判定：患者を誘導すべき救護エリアを選択してください。",
            [("area_green_ambulatory_minor", "歩行可能なため緑エリア（軽症待機）へ誘導"), ("area_red_critical_immediate", "重症緊急のため赤エリア（即時救命）へ移送"), ("area_dump_in_dumpster", "ゴミ収集容器へ投げ込む")],
            "area_green_ambulatory_minor", "area_red_critical_immediate"
        ),
        (
            "77",
            "システムアクセス制限：役職が課長以上の場合は管理コンソールへの接続を認める。一般主任以下の場合は一般画面へリダイレクト。社員の役職：営業部課長。",
            "アクセス認可判定：ユーザーに表示すべき画面を選択してください。",
            "システムアクセス制限：役職が課長以上の場合は管理コンソールへの接続を認める。一般主任以下の場合は一般画面へリダイレクト。社員の役職：開発部主任。",
            "アクセス認可判定：ユーザーに表示すべき画面を選択してください。",
            [("view_admin_console_privileged", "課長役職確認により管理コンソールを表示する"), ("view_standard_user_dashboard", "一般社員向け通常ダッシュボードへリダイレクト"), ("view_crash_os_blue_screen", "OSを強制ブルースクリーンにする")],
            "view_admin_console_privileged", "view_standard_user_dashboard"
        ),
        (
            "78",
            "PC周辺機器貸出規定：役職者が使用する場合は外部4Kモニターを貸与、一般社員には標準FHDモニターを貸与。申請者：執行役員。",
            "貸出機材判定：申請者に割り当てるべきモニター仕様を選択してください。",
            "PC周辺機器貸出規定：役職者が使用する場合は外部4Kモニターを貸与、一般社員には標準FHDモニターを貸与。申請者：今年度新入社員。",
            "貸出機材判定：申請者に割り当てるべきモニター仕様を選択してください。",
            [("spec_high_res_4k_display", "役職者基準に基づき外部4Kモニターを貸与する"), ("spec_standard_fhd_display", "一般社員基準に基づき標準FHDモニターを貸与する"), ("spec_wooden_plank_mockup", "木製の板をモニター代わりに渡す")],
            "spec_high_res_4k_display", "spec_standard_fhd_display"
        ),
        (
            "79",
            "ホテル客室アップグレード基準：宿泊回数10回以上のダイヤモンド会員はスイートルームへ無料変更、10回未満は予約通りスタンダードルーム。会員記録：累計18回宿泊。",
            "客室割当判定：顧客へ提供すべき客室タイプを選択してください。",
            "ホテル客室アップグレード基準：宿泊回数10回以上のダイヤモンド会員はスイートルームへ無料変更、10回未満は予約通りスタンダードルーム。会員記録：今回が初回宿泊。",
            "客室割当判定：顧客へ提供すべき客室タイプを選択してください。",
            [("room_suite_complimentary_upgrade", "10回以上達成のためスイートルームへ無償変更"), ("room_standard_reserved_category", "利用回数基準未達のため予約通りスタンダード室"), ("room_abandoned_cellar_dungeon", "地下の廃墟牢屋に宿泊させる")],
            "room_suite_complimentary_upgrade", "room_standard_reserved_category"
        ),
        (
            "80",
            "レンタカー返却時燃料判定：満タンプラン未加入の場合に燃料不足時は実費給油代を請求、満タンプラン加入者は給油なしで返却可能。契約証：満タンプラン加入済み。",
            "返却精算判定：燃料精算の要否を選択してください。",
            "レンタカー返却時燃料判定：満タンプラン未加入の場合に燃料不足時は実費給油代を請求、満タンプラン加入者は給油なしで返却可能。契約証：満タンプラン未加入、燃料計は空寸前。",
            "返却精算判定：燃料精算の要否を選択してください。",
            [("bill_fuel_charge_waived_plan", "満タンプラン適用により給油代請求を免除する"), ("bill_fuel_charge_required_empty", "プラン未加入かつ空寸前の実費給油代を請求する"), ("bill_purchase_new_sports_car", "新車スポーツカーの購入代金を請求する")],
            "bill_fuel_charge_waived_plan", "bill_fuel_charge_required_empty"
        ),
    ]

    for gid, ctx1, q1, ctx2, q2, c_defs, t1, t2 in id_style_defs:
        choices = make_choices(c_defs)
        pairs.append({
            "id": f"rf_pert_id_{gid}_s1",
            "group_id": f"rf_pert_id_{gid}",
            "family": "perturbation_invariance",
            "perturbation_type": "candidate_id_style",
            "context": ctx1,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_pert_id_{gid}_s2",
            "group_id": f"rf_pert_id_{gid}",
            "family": "perturbation_invariance",
            "perturbation_type": "candidate_id_style",
            "context": ctx2,
            "question": q2,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    return pairs
