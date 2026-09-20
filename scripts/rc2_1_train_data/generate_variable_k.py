"""RC2.1 Training Data Synthesis: Stream B — Variable Choice (180 pairs = 360 records).

Covers variable candidate set sizes K in {2, 3, 4, 5, 6, 7, 8, 10, 12, 16}:
- K = 2: 18 pairs
- K = 3: 18 pairs
- K = 4: 24 pairs (4 scenarios x 6 reps = 24 pairs)
- K = 5: 18 pairs
- K = 6: 18 pairs
- K = 7: 18 pairs
- K = 8: 24 pairs (4 scenarios x 6 reps = 24 pairs)
- K = 10: 15 pairs
- K = 12: 15 pairs
- K = 16: 12 pairs

Total: 180 pairs (360 records). All contrastive pairs have distinct targets for s1/s2.
"""

from typing import Any, Dict, List, Tuple
import random


def make_choices(defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in defs]


def generate_variable_k_stream_b(seed: int = 5005) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    records = []

    # 1. K = 2 (18 pairs)
    k2_scenarios = [
        ("健康診断再検査", "収縮期血圧が140mmHg以上または拡張期血圧が90mmHg以上の受診者は「要受診（精密検査）」、未満は「正常判定」。受診者測定値：148/92 mmHg。", "収縮期血圧が140mmHg以上または拡張期血圧が90mmHg以上の受診者は「要受診（精密検査）」、未満は「正常判定」。受診者測定値：118/76 mmHg。", [("bp_action_retest_clinic", "要受診判定（循環器専門医を受診）"), ("bp_action_normal_pass", "正常判定（特記事項なし）")], "bp_action_retest_clinic", "bp_action_normal_pass"),
        ("高速道路ETCゲート", "車載器のETCカードが有効期限内かつ正常挿入されている車両は「ゲート開放（通過）」、異常検知時は「バー閉鎖（停止）」。車両ステータス：カード期限切れ警告点灯。", "車載器のETCカードが有効期限内かつ正常挿入されている車両は「ゲート開放（通過）」、異常検知時は「バー閉鎖（停止）」。車両ステータス：通信正常・認証OK。", [("etc_gate_open_pass", "ETCバーを開放して通過許可"), ("etc_gate_close_halt", "ETCバーを閉鎖して一時停止誘導")], "etc_gate_close_halt", "etc_gate_open_pass"),
        ("入退館セキュリティ", "顔認証スコアが95%以上の来訪者は「入館ゲート解錠」、未満は「受付案内」。認証結果：スコア98.2%。", "顔認証スコアが95%以上の来訪者は「入館ゲート解錠」、未満は「受付案内」。認証結果：スコア62.1%。", [("security_gate_unlock", "ゲートを開錠して入館を許可"), ("security_direct_front_desk", "受付窓口へ案内して本人確認")], "security_gate_unlock", "security_direct_front_desk"),
    ]
    for idx, (title, s1, s2, c_defs, t1, t2) in enumerate(k2_scenarios):
        for rep in range(6):
            gid = f"tb_var_k02_{idx*6 + rep + 1:03d}"
            choices = make_choices(c_defs)
            q = f"判定選定：{title}の条件に基づき適切な対応を選択してください。"
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "variable_choice", "k_size": 2, "context": f"【ルール】{s1}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t1}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "variable_choice", "k_size": 2, "context": f"【ルール】{s2}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t2}})

    # 2. K = 3 (18 pairs)
    k3_scenarios = [
        ("受講コース推奨", "プログラミング初学者は「基礎入門コース」、実務経験1〜3年は「実践開発コース」、実務4年以上は「アーキテクト設計コース」。受講生：実務歴なし（完全初学者）。", "プログラミング初学者は「基礎入門コース」、実務経験1〜3年は「実践開発コース」、実務4年以上は「アーキテクト設計コース」。受講生：Web受託開発で実務歴2年半。", [("course_opt_intro_basics", "基礎入門コース（ゼロから学ぶ）"), ("course_opt_hands_on_practice", "実践開発コース（実務応用）"), ("course_opt_lead_architect", "アーキテクト設計コース（上級設計）")], "course_opt_intro_basics", "course_opt_hands_on_practice"),
        ("荷物配送オプション", "注文合計が1万円以上は「無料速達便」、5千円以上1万円未満は「通常無料便」、5千円未満は「有料普通便（送料500円）」。注文金額：7,500円。", "注文合計が1万円以上は「無料速達便」、5千円以上1万円未満は「通常無料便」、5千円未満は「有料普通便（送料500円）」。注文金額：12,000円。", [("delivery_opt_express_free", "無料速達便（最短翌日着）"), ("delivery_opt_standard_free", "通常無料便（送料無料）"), ("delivery_opt_paid_economy", "有料普通便（送料500円加算）")], "delivery_opt_standard_free", "delivery_opt_express_free"),
        ("空調基本モード", "室温28度以上は「冷房モード」、18度以下は「暖房モード」、19度〜27度は「送風モード」。現在の室温：15度。", "室温28度以上は「冷房モード」、18度以下は「暖房モード」、19度〜27度は「送風モード」。現在の室温：23度。", [("hvac_cooling_mode", "冷房モード（室温を下げる）"), ("hvac_heating_mode", "暖房モード（室温を上げる）"), ("hvac_fan_mode", "送風モード（風を循環させる）")], "hvac_heating_mode", "hvac_fan_mode"),
    ]
    for idx, (title, s1, s2, c_defs, t1, t2) in enumerate(k3_scenarios):
        for rep in range(6):
            gid = f"tb_var_k03_{idx*6 + rep + 1:03d}"
            choices = make_choices(c_defs)
            q = f"選択判定：{title}の基準に従い適切な選択肢を選択してください。"
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "variable_choice", "k_size": 3, "context": f"【条件照合】{s1}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t1}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "variable_choice", "k_size": 3, "context": f"【条件照合】{s2}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t2}})

    # 3. K = 4 (24 pairs) - Expanded to 4 rich scenarios
    k4_scenarios = [
        ("四季イベント手配", "対象月が3〜5月は「春の桜祭り企画」、6〜8月は「夏の納涼花火企画」、9〜11月は「秋の収穫祭企画」、12〜2月は「冬のイルミネーション企画」。対象月：10月。", "対象月が3〜5月は「春の桜祭り企画」、6〜8月は「夏の納涼花火企画」、9〜11月は「秋の収穫祭企画」、12〜2月は「冬のイルミネーション企画」。対象月：1月。", [("season_spring_cherry_blossom", "春の桜祭り企画の手配"), ("season_summer_fireworks", "夏の納涼花火企画の手配"), ("season_autumn_harvest_festival", "秋の収穫祭企画の手配"), ("season_winter_illumination", "冬のイルミネーション企画の手配")], "season_autumn_harvest_festival", "season_winter_illumination"),
        ("ユーザー権限グループ", "ゲストは「閲覧のみ」、一般社員は「作成・編集」、部門管理者は「承認・削除」、特権管理者は「全権限（インフラ含む）」。対象ユーザー：開発部門の部長（部門管理者）。", "ゲストは「閲覧のみ」、一般社員は「作成・編集」、部門管理者は「承認・削除」、特権管理者は「全権限（インフラ含む）」。対象ユーザー：今月入社した派遣社員（一般社員）。", [("role_perm_guest_read_only", "閲覧のみ権限（ゲスト）"), ("role_perm_employee_edit", "作成・編集権限（一般社員）"), ("role_perm_manager_approve_delete", "承認・削除権限（部門管理者）"), ("role_perm_super_admin_all", "システム全権限（特権管理者）")], "role_perm_manager_approve_delete", "role_perm_employee_edit"),
        ("交通信号の灯火表示", "赤色は「停止」、黄色は「注意して停止」、青色は「直進・右左折の進行可能」、黄点滅は「周囲に注意して進行」。信号機の表示：赤色の点灯。", "交通信号の灯火表示：赤色は「停止」、黄色は「注意して停止」、青色は「直進・右左折の進行可能」、黄点滅は「周囲に注意して進行」。信号機の表示：青色の点灯。", [("signal_aspect_stop_red", "停止（赤色信号に従い停止線で一時停止）"), ("signal_aspect_caution_yellow", "注意停止（黄色信号に従い停止）"), ("signal_aspect_proceed_blue", "進行可能（青色信号に従い安全に進行）"), ("signal_aspect_flashing_yellow", "徐行注意進行（黄点滅信号）")], "signal_aspect_stop_red", "signal_aspect_proceed_blue"),
        ("航空機座席クラス予約", "予算20万円超は「ファーストクラス」、10万〜20万円は「ビジネスクラス」、5万〜10万円は「プレミアムエコノミー」、5万円未満は「エコノミークラス」。顧客予算：15万円。", "航空機座席クラス予約：予算20万円超は「ファーストクラス」、10万〜20万円は「ビジネスクラス」、5万〜10万円は「プレミアムエコノミー」、5万円未満は「エコノミークラス」。顧客予算：3万5千円。", [("seat_grade_first_class", "ファーストクラス（最上位個室席）"), ("seat_grade_business_class", "ビジネスクラス（フルフラット席）"), ("seat_grade_premium_economy", "プレミアムエコノミー（ゆったり席）"), ("seat_grade_standard_economy", "エコノミークラス（標準座席）")], "seat_grade_business_class", "seat_grade_standard_economy"),
    ]
    for idx, (title, s1, s2, c_defs, t1, t2) in enumerate(k4_scenarios):
        for rep in range(6):
            gid = f"tb_var_k04_{idx*6 + rep + 1:03d}"
            choices = make_choices(c_defs)
            q = f"判定選定：{title}に基づき適切な選択肢を選択してください。"
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "variable_choice", "k_size": 4, "context": f"【基準規程】{s1}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t1}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "variable_choice", "k_size": 4, "context": f"【基準規程】{s2}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t2}})

    # 4. K = 5 (18 pairs)
    k5_scenarios = [
        ("ホテル客室グレード", "宿泊予算が1泊1万円未満は「エコノミーシングル」、1万〜2万円は「スーペリアダブル」、2万〜3.5万円は「デラックスツイン」、3.5万〜5万円は「エグゼクティブスイート」、5万円超は「プレジデンシャルスイート」。希望予算：28,000円。", "宿泊予算が1泊1万円未満は「エコノミーシングル」、1万〜2万円は「スーペリアダブル」、2万〜3.5万円は「デラックスツイン」、3.5万〜5万円は「エグゼクティブスイート」、5万円超は「プレジデンシャルスイート」。希望予算：8,500円。", [("room_grade_economy_single", "エコノミーシングル（1万円未満）"), ("room_grade_superior_double", "スーペリアダブル（1万〜2万円）"), ("room_grade_deluxe_twin", "デラックスツイン（2万〜3.5万円）"), ("room_grade_executive_suite", "エグゼクティブスイート（3.5万〜5万円）"), ("room_grade_presidential_suite", "プレジデンシャルスイート（5万円超）")], "room_grade_deluxe_twin", "room_grade_economy_single"),
        ("製品品質検査グレード", "傷・欠陥が0個は「特級Sランク」、1個は「1級Aランク」、2〜3個は「2級Bランク」、4〜5個は「3級Cランク」、6個以上は「廃棄不合格」。検査結果：欠陥3個検出。", "製品品質検査グレード：傷・欠陥が0個は「特級Sランク」、1個は「1級Aランク」、2〜3個は「2級Bランク」、4〜5個は「3級Cランク」、6個以上は「廃棄不合格」。検査結果：欠陥0個（完全無欠）。", [("inspect_grade_s_flawless", "特級Sランク（欠陥0個：最上級）"), ("inspect_grade_a_minor", "1級Aランク（欠陥1個：良品）"), ("inspect_grade_b_standard", "2級Bランク（欠陥2〜3個：並品）"), ("inspect_grade_c_subpar", "3級Cランク（欠陥4〜5個：訳あり）"), ("inspect_grade_reject_scrap", "廃棄不合格（欠陥6個以上：不良廃棄）")], "inspect_grade_b_standard", "inspect_grade_s_flawless"),
        ("顧客満足度評価5段階", "点数5点は「大変満足」、4点は「やや満足」、3点は「普通」、2点は「やや不満」、1点は「大変不満」。アンケート回答：点数4点。", "顧客満足度評価5段階：点数5点は「大変満足」、4点は「やや満足」、3点は「普通」、2点は「やや不満」、1点は「大変不満」。アンケート回答：点数1点。", [("csat_5_very_satisfied", "大変満足（最高評価）"), ("csat_4_somewhat_satisfied", "やや満足（良好）"), ("csat_3_neutral", "普通（標準）"), ("csat_2_somewhat_dissatisfied", "やや不満（改善要）"), ("csat_1_very_dissatisfied", "大変不満（要緊急対応）")], "csat_4_somewhat_satisfied", "csat_1_very_dissatisfied"),
    ]
    for idx, (title, s1, s2, c_defs, t1, t2) in enumerate(k5_scenarios):
        for rep in range(6):
            gid = f"tb_var_k05_{idx*6 + rep + 1:03d}"
            choices = make_choices(c_defs)
            q = f"ランク選定：{title}に従い適合するグレードを選択してください。"
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "variable_choice", "k_size": 5, "context": f"【査定基準】{s1}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t1}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "variable_choice", "k_size": 5, "context": f"【査定基準】{s2}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t2}})

    # 5. K = 6 (18 pairs)
    k6_defs = [
        ("eval_score_band_6", "バンド6（90〜100点：極めて優秀）"),
        ("eval_score_band_5", "バンド5（80〜89点：優秀）"),
        ("eval_score_band_4", "バンド4（70〜79点：良好）"),
        ("eval_score_band_3", "バンド3（60〜69点：平均水準）"),
        ("eval_score_band_2", "バンド2（50〜59点：要努力）"),
        ("eval_score_band_1", "バンド1（50点未満：不合格補習）"),
    ]
    k6_s1 = "評価基準：90点以上はバンド6、80点台はバンド5、70点台はバンド4、60点台はバンド3、50点台はバンド2、50点未満はバンド1。対象者得点：84点。"
    k6_s2 = "評価基準：90点以上はバンド6、80点台はバンド5、70点台はバンド4、60点台はバンド3、50点台はバンド2、50点未満はバンド1。対象者得点：45点。"
    for rep in range(18):
        gid = f"tb_var_k06_{rep + 1:03d}"
        choices = make_choices(k6_defs)
        q = "成績判定：評価基準に基づき得点に対応するバンドを選択してください。"
        records.append({"id": f"{gid}_s1", "group_id": gid, "family": "variable_choice", "k_size": 6, "context": f"【評定基準】{k6_s1}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": "eval_score_band_5"}})
        records.append({"id": f"{gid}_s2", "group_id": gid, "family": "variable_choice", "k_size": 6, "context": f"【評定基準】{k6_s2}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": "eval_score_band_1"}})

    # 6. K = 7 (18 pairs)
    k7_defs = [
        ("day_schedule_mon", "月曜日：全社朝礼および週次進捗報告会議"),
        ("day_schedule_tue", "火曜日：プロダクト開発スプリントレビュー"),
        ("day_schedule_wed", "水曜日：全社ノー残業デーおよび自己研鑽"),
        ("day_schedule_thu", "木曜日：社外パートナー定例打合せ"),
        ("day_schedule_fri", "金曜日：コードフリーズ・成果振り返り"),
        ("day_schedule_sat", "土曜日：オフィス休館日（緊急時のみ入館）"),
        ("day_schedule_sun", "日曜日：法定休日（全館消灯）"),
    ]
    k7_s1 = "曜日別定例業務：月曜＝朝礼、火曜＝レビュー、水曜＝ノー残業デー、木曜＝社外定例、金曜＝振り返り、土日＝休業。本日の指示：社外パートナー定例打合せを実施する曜日を選択してください。"
    k7_s2 = "曜日別定例業務：月曜＝朝礼、火曜＝レビュー、水曜＝ノー残業デー、木曜＝社外定例、金曜＝振り返り、土日＝休業。本日の指示：全社ノー残業デーとなる曜日を選択してください。"
    for rep in range(18):
        gid = f"tb_var_k07_{rep + 1:03d}"
        choices = make_choices(k7_defs)
        q = "スケジュール選定：業務ルールに基づき該当する曜日を選択してください。"
        records.append({"id": f"{gid}_s1", "group_id": gid, "family": "variable_choice", "k_size": 7, "context": f"【社内週間予定】{k7_s1}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": "day_schedule_thu"}})
        records.append({"id": f"{gid}_s2", "group_id": gid, "family": "variable_choice", "k_size": 7, "context": f"【社内週間予定】{k7_s2}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": "day_schedule_wed"}})

    # 7. K = 8 (24 pairs) - Expanded to 4 rich scenarios
    k8_scenarios = [
        (
            "物流地域ブロック",
            "納品先住所が「愛知県名古屋市中区」の荷物の管轄地方を選択してください。",
            "納品先住所が「香川県高松市番町」の荷物の管轄地方を選択してください。",
            [
                ("region_hokkaido", "北海道地方：札幌・道東・道北エリア"),
                ("region_tohoku", "東北地方：青森・秋田・岩手・宮城・山形・福島"),
                ("region_kanto", "関東地方：東京・神奈川・千葉・埼玉・茨城・栃木・群馬"),
                ("region_chubu", "中部地方：愛知・静岡・新潟・長野・岐阜・富山・石川・福井"),
                ("region_kinki", "近畿地方：大阪・京都・兵庫・奈良・滋賀・和歌山"),
                ("region_chugoku", "中国地方：広島・岡山・山口・鳥取・島根"),
                ("region_shikoku", "四国地方：香川・徳島・愛媛・高知"),
                ("region_kyushu_okinawa", "九州・沖縄地方：福岡・熊本・鹿児島・沖縄など"),
            ],
            "region_chubu", "region_shikoku"
        ),
        (
            "社内組織担当部門",
            "依頼内容：『全社員の就業規則改定に伴う労働組合との協定締結および労働基準監督署への届出手続き』",
            "依頼内容：『全社コアプロダクトの次世代マイクロサービス基盤アーキテクチャ設計およびKubernetesクラスタ構築』",
            [
                ("dept_human_resources", "人事労務部（採用・労務管理・福利厚生）"),
                ("dept_finance_accounting", "経理財務部（決算・税務・出納）"),
                ("dept_legal_compliance", "法務コンプライアンス部（契約審査・特許）"),
                ("dept_sales_marketing", "営業マーケティング部（顧客開拓・広告）"),
                ("dept_software_engineering", "ソフトウェア開発技術部（基盤設計・実装）"),
                ("dept_quality_assurance", "品質保証QA部（テスト自動化・検証）"),
                ("dept_customer_support", "カスタマーサポート部（問い合わせ・対応）"),
                ("dept_general_affairs", "総務管財部（ファシリティ・オフィス）"),
            ],
            "dept_human_resources", "dept_software_engineering"
        ),
        (
            "ネットワークOSI参照モデル層",
            "技術照会：『TCPプロトコルの3ウェイハンドシェイクおよびポート番号管理を行うプロトコル層』",
            "技術照会：『イーサネットフレームのMACアドレス照合および物理ケーブル上の信号制御を行う層』",
            [
                ("osi_layer_1_physical", "第1層：物理層（電圧・ケーブル・コネクタ）"),
                ("osi_layer_2_datalink", "第2層：データリンク層（MACアドレス・フレーム）"),
                ("osi_layer_3_network", "第3層：ネットワーク層（IPアドレス・ルーティング）"),
                ("osi_layer_4_transport", "第4層：トランスポート層（TCP/UDP・ポート番号）"),
                ("osi_layer_5_session", "第5層：セッション層（通信セッション確立管理）"),
                ("osi_layer_6_presentation", "第6層：プレゼンテーション層（暗号化・圧縮）"),
                ("osi_layer_7_application", "第7層：アプリケーション層（HTTP/DNS/SMTP）"),
                ("osi_layer_8_management", "管理プレーン：SNMPおよび帯域監視制御"),
            ],
            "osi_layer_4_transport", "osi_layer_2_datalink"
        ),
        (
            "システムアラート重大度8段階",
            "インシデント：『基幹データベースの全ノードが同時ダウンし全顧客の商取引が完全途絶中（最致命傷）』",
            "インシデント：『社内ポータルのフッターにあるアイコン画像が1箇所リンク切れで表示されない（極軽微）』",
            [
                ("syslog_sev_0_emerg", "Severity 0：Emergency（システム完全使用不能・最致命傷）"),
                ("syslog_sev_1_alert", "Severity 1：Alert（即時対処必須）"),
                ("syslog_sev_2_crit", "Severity 2：Critical（致命的状態）"),
                ("syslog_sev_3_err", "Severity 3：Error（エラー発生）"),
                ("syslog_sev_4_warn", "Severity 4：Warning（警告状態）"),
                ("syslog_sev_5_notice", "Severity 5：Notice（通常だが注目すべき状態）"),
                ("syslog_sev_6_info", "Severity 6：Informational（通常情報ログ）"),
                ("syslog_sev_7_debug", "Severity 7：Debug（デバッグ用極軽微情報）"),
            ],
            "syslog_sev_0_emerg", "syslog_sev_7_debug"
        ),
    ]
    for idx, (title, s1, s2, c_defs, t1, t2) in enumerate(k8_scenarios):
        for rep in range(6):
            gid = f"tb_var_k08_{idx*6 + rep + 1:03d}"
            choices = make_choices(c_defs)
            q = f"選択判定：{title}に基づき適切な項目を選択してください。"
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "variable_choice", "k_size": 8, "context": f"【事象概要】{s1}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t1}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "variable_choice", "k_size": 8, "context": f"【事象概要】{s2}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t2}})

    # 8. K = 10 (15 pairs)
    k10_defs = [
        ("dept_01_hr", "01. 人事総務部（採用・労務・オフィス）"),
        ("dept_02_finance", "02. 経理財務部（決算・税務・資金）"),
        ("dept_03_legal", "03. 法務コンプライアンス部（契約・訴訟）"),
        ("dept_04_sales", "04. 第一営業部（国内法人営業）"),
        ("dept_05_global", "05. グローバル事業部（海外展開）"),
        ("dept_06_marketing", "06. マーケティング推進部（広告・PR）"),
        ("dept_07_eng_core", "07. コアエンジニアリング部（基盤開発）"),
        ("dept_08_eng_qa", "08. 品質保証・QA部（テスト自動化）"),
        ("dept_09_customer_success", "09. カスタマーサクセス部（導入支援）"),
        ("dept_10_procurement", "10. 調達購買部（資材・ベンダー発注）"),
    ]
    k10_s1 = "社内稟議回覧：『海外の現地法人設立に伴う現地法規制の調査と契約書締結の審査を依頼したい。』"
    k10_s2 = "社内稟議回覧：『新製品リリース前の回帰テスト自動化スイートの設計と負荷テストを依頼したい。』"
    for rep in range(15):
        gid = f"tb_var_k10_{rep + 1:03d}"
        choices = make_choices(k10_defs)
        q = "主管部署選定：稟議内容に最も合致する担当部門を10部署の中から選択してください。"
        records.append({"id": f"{gid}_s1", "group_id": gid, "family": "variable_choice", "k_size": 10, "context": f"【申請概要】{k10_s1}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": "dept_03_legal"}})
        records.append({"id": f"{gid}_s2", "group_id": gid, "family": "variable_choice", "k_size": 10, "context": f"【申請概要】{k10_s2}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": "dept_08_eng_qa"}})

    # 9. K = 12 (15 pairs)
    k12_defs = [
        ("month_01_jan", "1月（睦月）：新春初売り・年頭所感"),
        ("month_02_feb", "2月（如月）：決算前中間レビュー"),
        ("month_03_mar", "3月（弥生）：本決算・期末棚卸し"),
        ("month_04_apr", "4月（卯月）：新入社員入社式・新年度開始"),
        ("month_05_may", "5月（皐月）：ゴールデンウィーク・夏物立ち上げ"),
        ("month_06_jun", "6月（水無月）：株主総会・夏季賞与支給"),
        ("month_07_jul", "7月（文月）：夏期商戦・中途採用本格化"),
        ("month_08_aug", "8月（葉月）：夏季休業・サーバー定期メンテ"),
        ("month_09_sep", "9月（長月）：中間決算・下半期方針発表"),
        ("month_10_oct", "10月（神無月）：内定式・新年度予算策定開始"),
        ("month_11_nov", "11月（霜月）：ブラックフライデーセール準備"),
        ("month_12_dec", "12月（師走）：冬季賞与支給・年次締め作業"),
    ]
    k12_s1 = "年間行事スケジュール：株主総会が開催され、夏季賞与（ボーナス）が支給される月を選択してください。"
    k12_s2 = "年間行事スケジュール：次年度新卒の内定式が執り行われ、来期予算策定がキックオフされる月を選択してください。"
    for rep in range(15):
        gid = f"tb_var_k12_{rep + 1:03d}"
        choices = make_choices(k12_defs)
        q = "月度選定：年間カレンダー規程に基づき、該当する実施月を選択してください。"
        records.append({"id": f"{gid}_s1", "group_id": gid, "family": "variable_choice", "k_size": 12, "context": f"【全社会計カレンダー】{k12_s1}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": "month_06_jun"}})
        records.append({"id": f"{gid}_s2", "group_id": gid, "family": "variable_choice", "k_size": 12, "context": f"【全社会計カレンダー】{k12_s2}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": "month_10_oct"}})

    # 10. K = 16 (12 pairs)
    k16_defs = [
        ("code_00_zero", "種別00：正常処理完了（ステータス200）"),
        ("code_01_bad_req", "種別01：リクエスト形式不正（構文エラー）"),
        ("code_02_unauth", "種別02：未認証エラー（トークン失効）"),
        ("code_03_forbidden", "種別03：権限不足エラー（アクセス拒否）"),
        ("code_04_not_found", "種別04：リソース未検出（該当データなし）"),
        ("code_05_method_not_allowed", "種別05：無効なHTTPメソッド"),
        ("code_06_conflict", "種別06：リソース競合（バージョン不整合）"),
        ("code_07_gone", "種別07：リソース永久消滅（廃止済み）"),
        ("code_08_payload_too_large", "種別08：ペイロード過大（上限超過）"),
        ("code_09_rate_limit", "種別09：レート制限超過（429リクエスト過多）"),
        ("code_10_internal_error", "種別10：サーバー内部エラー（500致命的）"),
        ("code_11_not_implemented", "種別11：未実装機能（501）"),
        ("code_12_bad_gateway", "種別12：不正なゲートウェイ応答（502）"),
        ("code_13_service_unavailable", "種別13：サービス利用不可（503過負荷保守中）"),
        ("code_14_gateway_timeout", "種別14：ゲートウェイタイムアウト（504無応答）"),
        ("code_15_version_not_supported", "種別15：プロトコルバージョン非対応（505）"),
    ]
    k16_s1 = "APIログ解析：上流のバックエンドAPIからの応答が30秒間途絶し、リバースプロキシが待機時間をタイムアウトした際に返すべきコードを選択してください。"
    k16_s2 = "APIログ解析：クライアントが1秒あたり1000回以上の連続リクエストを送信し、APIクォータを超過した際に返すべきコードを選択してください。"
    for rep in range(12):
        gid = f"tb_var_k16_{rep + 1:03d}"
        choices = make_choices(k16_defs)
        q = "ステータス選定：障害仕様書に基づき、該当する16種別のエラーコードを選択してください。"
        records.append({"id": f"{gid}_s1", "group_id": gid, "family": "variable_choice", "k_size": 16, "context": f"【API仕様書エラー定義】{k16_s1}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": "code_14_gateway_timeout"}})
        records.append({"id": f"{gid}_s2", "group_id": gid, "family": "variable_choice", "k_size": 16, "context": f"【API仕様書エラー定義】{k16_s2}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": "code_09_rate_limit"}})

    return records


if __name__ == "__main__":
    records = generate_variable_k_stream_b()
    print(f"Generated {len(records)} variable_k records ({len(records)//2} pairs).")
