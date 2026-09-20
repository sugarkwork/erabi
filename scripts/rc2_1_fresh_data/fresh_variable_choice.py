"""Research Fresh Suite: variable_choice (40 pairs, 80 cases).

Coverage of variable choice set sizes:
- K = 2: 6 pairs (groups 01-06)
- K = 3: 6 pairs (groups 07-12)
- K = 4: 6 pairs (groups 13-18)
- K = 6: 6 pairs (groups 19-24)
- K = 8: 6 pairs (groups 25-30)
- K = 12: 5 pairs (groups 31-35)
- K = 16: 5 pairs (groups 36-40)

All 40 groups are contrastive pairs (_s1 and _s2 have distinct targets).
Token length guaranteed <= 380 (< 512 hard ceiling even at K=16).
"""

from typing import Any, Dict, List, Tuple


def make_choices(defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in defs]


def get_fresh_variable_choice_pairs() -> List[Dict[str, Any]]:
    pairs = []

    # 1. K = 2 (6 pairs: 01 to 06)
    k2_defs = [
        (
            "01",
            "【二者択一判定】通信ステータスが暗号化（TLS 1.3）されている接続は許可し、平文通信（HTTP）は遮断する。対象パケット：HTTPS/TLS 1.3接続。",
            "アクセス制御判定：通信の許可または遮断を選択してください。",
            "【二者択一判定】通信ステータスが暗号化（TLS 1.3）されている接続は許可し、平文通信（HTTP）は遮断する。対象パケット：ポート80平文HTTP通信。\nアクセス制御判定：通信の許可または遮断を選択してください。",
            [("action_allow_traffic", "通信を許可する"), ("action_block_traffic", "通信を遮断する")],
            "action_allow_traffic", "action_block_traffic"
        ),
        (
            "02",
            "【決済成否判定】口座残高が引き落とし請求額以上であれば決済成功、未満であれば残高不足で決済失敗。残高：10,000円、請求：8,000円。",
            "決済処理ステータス：決済結果を選択してください。",
            "【決済成否判定】口座残高が引き落とし請求額以上であれば決済成功、未満であれば残高不足で決済失敗。残高：3,000円、請求：8,000円。\n決済処理ステータス：決済結果を選択してください。",
            [("payment_status_success", "決済成功（引き落とし完了）"), ("payment_status_failure_nsf", "決済失敗（残高不足エラー）")],
            "payment_status_success", "payment_status_failure_nsf"
        ),
        (
            "03",
            "【契約更新可否】解約の申し出が更新日の30日前までになければ自動更新、あれば契約終了。顧客ステータス：期日までに解約申請なし。",
            "契約処理判定：契約のステータスを選択してください。",
            "【契約更新可否】解約の申し出が更新日の30日前までになければ自動更新、あれば契約終了。顧客ステータス：45日前に解約申請を受理済み。\n契約処理判定：契約のステータスを選択してください。",
            [("contract_auto_renewed", "契約を自動更新する"), ("contract_terminated", "契約を終了解約とする")],
            "contract_auto_renewed", "contract_terminated"
        ),
        (
            "04",
            "【入室認証判定】静脈認証が一致した場合は開錠、不一致の場合は施錠維持。照合スコア：一致率99.8%（合格）。",
            "生体ドア制御：電気錠の動作を選択してください。",
            "【入室認証判定】静脈認証が一致した場合は開錠、不一致の場合は施錠維持。照合スコア：一致率12.3%（不合格）。\n生体ドア制御：電気錠の動作を選択してください。",
            [("door_lock_open", "ドアを開錠する"), ("door_lock_keep_closed", "施錠を維持する")],
            "door_lock_open", "door_lock_keep_closed"
        ),
        (
            "05",
            "【受診要否判定】体温が37.5℃以上の場合は発熱外来を受診、未満の場合は通常経過観察。測定体温：38.6℃。",
            "医療トリアージ判定：適切な対応を選択してください。",
            "【受診要否判定】体温が37.5℃以上の場合は発熱外来を受診、未満の場合は通常経過観察。測定体温：36.4℃。\n医療トリアージ判定：適切な対応を選択してください。",
            [("action_visit_fever_clinic", "発熱外来を受診する"), ("action_standard_observation", "通常の経過観察とする")],
            "action_visit_fever_clinic", "action_standard_observation"
        ),
        (
            "06",
            "【車両通行判定】車高が2.5m以下の車両は地下駐車場へ進入可能、2.5m超は進入禁止。車両の実測車高：2.1m。",
            "駐車場進入制御：車両の進入可否を選択してください。",
            "【車両通行判定】車高が2.5m以下の車両は地下駐車場へ進入可能、2.5m超は進入禁止。車両の実測車高：3.2m。\n駐車場進入制御：車両の進入可否を選択してください。",
            [("vehicle_entry_permitted", "地下駐車場への進入を許可する"), ("vehicle_entry_prohibited", "車高制限超過のため進入を禁止する")],
            "vehicle_entry_permitted", "vehicle_entry_prohibited"
        ),
    ]

    for gid, ctx1, q1, q2, c_defs, t1, t2 in k2_defs:
        choices = make_choices(c_defs)
        if "\n" in q2:
            ctx2, q2_clean = q2.split("\n", 1)
        else:
            ctx2, q2_clean = ctx1, q2
        pairs.append({
            "id": f"rf_varch_k2_{gid}_s1",
            "group_id": f"rf_varch_k2_{gid}",
            "family": "variable_choice",
            "choice_count": 2,
            "context": ctx1,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_varch_k2_{gid}_s2",
            "group_id": f"rf_varch_k2_{gid}",
            "family": "variable_choice",
            "choice_count": 2,
            "context": ctx2,
            "question": q2_clean,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # 2. K = 3 (6 pairs: 07 to 12)
    k3_defs = [
        (
            "07",
            "【信号指示判定】赤は停止、黄は注意して停止、青は進行可能。現示信号：青色点灯。",
            "交通制御指示：ドライバーがとるべき運転操作を選択してください。",
            "【信号指示判定】赤は停止、黄は注意して停止、青は進行可能。現示信号：赤色点灯。\n交通制御指示：ドライバーがとるべき運転操作を選択してください。",
            [("signal_proceed_green", "交差点へ進行する"), ("signal_caution_yellow", "安全に停止準備する"), ("signal_stop_red", "停止位置で完全停止する")],
            "signal_proceed_green", "signal_stop_red"
        ),
        (
            "08",
            "【製品グレード判定】傷なし・寸法正常は良品（A）、傷あり・寸法正常は訳あり品（B）、寸法異常は廃棄品（C）。検査結果：微細な表面傷があるが寸法は規格内。",
            "製品仕分判定：製品の出荷等級を選択してください。",
            "【製品グレード判定】傷なし・寸法正常は良品（A）、傷あり・寸法正常は訳あり品（B）、寸法異常は廃棄品（C）。検査結果：無傷で寸法も完全規格内。\n製品仕分判定：製品の出荷等級を選択してください。",
            [("grade_a_standard_pass", "良品（グレードA）として正規出荷"), ("grade_b_discount_outlet", "訳あり品（グレードB）として特売出荷"), ("grade_c_discard_scrap", "廃棄品（グレードC）として破棄処分")],
            "grade_b_discount_outlet", "grade_a_standard_pass"
        ),
        (
            "09",
            "【座席予約クラス】予算3万円超はファースト、1万円〜3万円はビジネス、1万円未満はエコノミー。顧客予算：22,000円。",
            "座席手配判定：案内すべき搭乗クラスを選択してください。",
            "【座席予約クラス】予算3万円超はファースト、1万円〜3万円はビジネス、1万円未満はエコノミー。顧客予算：7,500円。\n座席手配判定：案内すべき搭乗クラスを選択してください。",
            [("seat_first_class", "ファーストクラスを手配する"), ("seat_business_class", "ビジネスクラスを手配する"), ("seat_economy_class", "エコノミークラスを手配する")],
            "seat_business_class", "seat_economy_class"
        ),
        (
            "10",
            "【アラート重大度】サービス全面停止はCritical、部分機能低下はWarning、単なる通知はInfo。障害状況：全社DBクラスタが全損ダウンしサービス全面停止。",
            "アラート判定：インシデントの重大度レベルを選択してください。",
            "【アラート重大度】サービス全面停止はCritical、部分機能低下はWarning、単なる通知はInfo。状況：日次バックアップが定刻に正常完了。\nアラート判定：インシデントの重大度レベルを選択してください。",
            [("level_critical_alert", "Critical（最優先の致命的障害）"), ("level_warning_alert", "Warning（部分機能の警戒警告）"), ("level_info_alert", "Info（通常の定期完了通知）")],
            "level_critical_alert", "level_info_alert"
        ),
        (
            "11",
            "【温度管理判定】15℃以上は冷房、10℃未満は暖房、10℃〜14℃は送風で維持。現在の室内温度：8℃。",
            "空調モード選定：エアコンの運転モードを選択してください。",
            "【温度管理判定】15℃以上は冷房、10℃未満は暖房、10℃〜14℃は送風で維持。現在の室内温度：22℃。\n空調モード選定：エアコンの運転モードを選択してください。",
            [("hvac_mode_cooling", "冷房モードで運転する"), ("hvac_mode_ventilation", "送風モードで運転する"), ("hvac_mode_heating", "暖房モードで運転する")],
            "hvac_mode_heating", "hvac_mode_cooling"
        ),
        (
            "12",
            "【会員ランク判定】年間購入100万円以上はゴールド、30万円以上はシルバー、30万円未満はブロンズ。年間購入額：45万円。",
            "ステータス認定：付与すべき会員ランクを選択してください。",
            "【会員ランク判定】年間購入100万円以上はゴールド、30万円以上はシルバー、30万円未満はブロンズ。年間購入額：120万円。\nステータス認定：付与すべき会員ランクを選択してください。",
            [("rank_gold_vip", "ゴールド会員ランクを付与する"), ("rank_silver_regular", "シルバー会員ランクを付与する"), ("rank_bronze_entry", "ブロンズ会員ランクを付与する")],
            "rank_silver_regular", "rank_gold_vip"
        ),
    ]

    for gid, ctx1, q1, q2, c_defs, t1, t2 in k3_defs:
        choices = make_choices(c_defs)
        if "\n" in q2:
            ctx2, q2_clean = q2.split("\n", 1)
        else:
            ctx2, q2_clean = ctx1, q2
        pairs.append({
            "id": f"rf_varch_k3_{gid}_s1",
            "group_id": f"rf_varch_k3_{gid}",
            "family": "variable_choice",
            "choice_count": 3,
            "context": ctx1,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_varch_k3_{gid}_s2",
            "group_id": f"rf_varch_k3_{gid}",
            "family": "variable_choice",
            "choice_count": 3,
            "context": ctx2,
            "question": q2_clean,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # 3. K = 4 (6 pairs: 13 to 18)
    k4_defs = [
        (
            "13",
            "【春夏秋冬判定】3月〜5月は春、6月〜8月は夏、9月〜11月は秋、12月〜2月は冬。本日の日付：10月15日。",
            "季節判定：現在の日付が属する季節区分を選択してください。",
            "【春夏秋冬判定】3月〜5月は春、6月〜8月は夏、9月〜11月は秋、12月〜2月は冬。本日の日付：7月20日。\n季節判定：現在の日付が属する季節区分を選択してください。",
            [("season_spring", "春（3月〜5月）"), ("season_summer", "夏（6月〜8月）"), ("season_autumn", "秋（9月〜11月）"), ("season_winter", "冬（12月〜2月）")],
            "season_autumn", "season_summer"
        ),
        (
            "14",
            "【東西南北判定】東京から見て札幌は北、那覇は南、千葉は東、山梨は西。目的地：沖縄県那覇市。",
            "方角判定：目的地の東京から見た方角を選択してください。",
            "【東西南北判定】東京から見て札幌は北、那覇は南、千葉は東、山梨は西。目的地：北海道札幌市。\n方角判定：目的地の東京から見た方角を選択してください。",
            [("direction_north", "北（North）"), ("direction_south", "南（South）"), ("direction_east", "東（East）"), ("direction_west", "西（West）")],
            "direction_south", "direction_north"
        ),
        (
            "15",
            "【四半期判定】4月〜6月は第1四半期（Q1）、7月〜9月はQ2、10月〜12月はQ3、1月〜3月はQ4。取引日：5月25日。",
            "決算期判定：取引が計上される会計四半期を選択してください。",
            "【四半期判定】4月〜6月は第1四半期（Q1）、7月〜9月はQ2、10月〜12月はQ3、1月〜3月はQ4。取引日：2月10日。\n決算期判定：取引が計上される会計四半期を選択してください。",
            [("quarter_q1", "第1四半期（Q1）"), ("quarter_q2", "第2四半期（Q2）"), ("quarter_q3", "第3四半期（Q3）"), ("quarter_q4", "第4四半期（Q4）")],
            "quarter_q1", "quarter_q4"
        ),
        (
            "16",
            "【血液型判定】抗A凝集・抗B非凝集はA型、逆はB型、両方凝集はAB型、両方非凝集はO型。検査結果：抗A抗体・抗B抗体の両方に強く凝集した。",
            "血液型分類：判定される血液型を選択してください。",
            "【血液型判定】抗A凝集・抗B非凝集はA型、逆はB型、両方凝集はAB型、両方非凝集はO型。検査結果：抗A抗体・抗B抗体のどちらにも全く凝集しなかった。\n血液型分類：判定される血液型を選択してください。",
            [("blood_type_a", "A型"), ("blood_type_b", "B型"), ("blood_type_ab", "AB型"), ("blood_type_o", "O型")],
            "blood_type_ab", "blood_type_o"
        ),
        (
            "17",
            "【トランプスート判定】赤いカードでハート形はハート、ダイヤ形はダイヤ、黒いカードで三つ葉はクラブ、槍先はスペード。手札：黒色の三つ葉マーク。",
            "カード絵柄判定：手札のスート記号を選択してください。",
            "【トランプスート判定】赤いカードでハート形はハート、ダイヤ形はダイヤ、黒いカードで三つ葉はクラブ、槍先はスペード。手札：赤色のひし形ダイヤマーク。\nカード絵柄判定：手札のスート記号を選択してください。",
            [("suit_spade", "スペード（黒・槍先）"), ("suit_heart", "ハート（赤・心臓）"), ("suit_diamond", "ダイヤ（赤・ひし形）"), ("suit_club", "クラブ（黒・三つ葉）")],
            "suit_club", "suit_diamond"
        ),
        (
            "18",
            "【評価等級判定】評点90点以上は優（S）、80点〜89点は良（A）、70点〜79点は可（B）、70点未満は不可（F）。受講者の得点：84点。",
            "成績等級認定：付与すべき成績評価を選択してください。",
            "【評価等級判定】評点90点以上は優（S）、80点〜89点は良（A）、70点〜79点は可（B）、70点未満は不可（F）。受講者の得点：58点。\n成績等級認定：付与すべき成績評価を選択してください。",
            [("grade_s_superior", "優（グレードS）"), ("grade_a_good", "良（グレードA）"), ("grade_b_pass", "可（グレードB）"), ("grade_f_fail", "不可（グレードF）")],
            "grade_a_good", "grade_f_fail"
        ),
    ]

    for gid, ctx1, q1, q2, c_defs, t1, t2 in k4_defs:
        choices = make_choices(c_defs)
        if "\n" in q2:
            ctx2, q2_clean = q2.split("\n", 1)
        else:
            ctx2, q2_clean = ctx1, q2
        pairs.append({
            "id": f"rf_varch_k4_{gid}_s1",
            "group_id": f"rf_varch_k4_{gid}",
            "family": "variable_choice",
            "choice_count": 4,
            "context": ctx1,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_varch_k4_{gid}_s2",
            "group_id": f"rf_varch_k4_{gid}",
            "family": "variable_choice",
            "choice_count": 4,
            "context": ctx2,
            "question": q2_clean,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # 4. K = 6 (6 pairs: 19 to 24)
    # Six continents, six working days, etc.
    k6_choices_days = [
        ("day_mon", "月曜日"), ("day_tue", "火曜日"), ("day_wed", "水曜日"),
        ("day_thu", "木曜日"), ("day_fri", "金曜日"), ("day_sat", "土曜日")
    ]
    k6_choices_roles = [
        ("role_admin", "管理者（Admin）"), ("role_editor", "編集者（Editor）"),
        ("role_author", "投稿者（Author）"), ("role_contributor", "寄稿者（Contributor）"),
        ("role_subscriber", "閲覧者（Subscriber）"), ("role_banned", "停止者（Banned）")
    ]
    k6_defs = [
        (
            "19",
            "【当番割当規定】燃えるゴミ収集は毎週水曜日の朝に実施する。本日のゴミ出し：燃えるゴミ。",
            "収集曜日判定：燃えるゴミを出すべき該当曜日を選択してください。",
            "【当番割当規定】粗大ゴミ特別収集は毎週土曜日の午前中に実施する。本日のゴミ出し：粗大ゴミ。\n収集曜日判定：粗大ゴミを出すべき該当曜日を選択してください。",
            k6_choices_days, "day_wed", "day_sat"
        ),
        (
            "20",
            "【定例会議日程】全社経営会議は毎週月曜日の午前9時より開催する。参加会議：全社経営会議。",
            "会議日程判定：参加すべき該当曜日を選択してください。",
            "【定例会議日程】開発スプリント振り返りMTGは毎週金曜日の夕方に開催する。参加会議：スプリント振り返りMTG。\n会議日程判定：参加すべき該当曜日を選択してください。",
            k6_choices_days, "day_mon", "day_fri"
        ),
        (
            "21",
            "【定期清掃日】共有フロアのワックスがけ清掃は毎週火曜日の夜間に実施。対象清掃：フロアワックスがけ。",
            "清掃曜日判定：作業を実施すべき曜日を選択してください。",
            "【定期清掃日】観葉植物の水やりメンテナンスは毎週木曜日の午後に実施。対象清掃：植物水やり。\n清掃曜日判定：作業を実施すべき曜日を選択してください。",
            k6_choices_days, "day_tue", "day_thu"
        ),
        (
            "22",
            "【システム権限付与】ユーザー全権管理および決済設定権限を持つのは管理者のみ。ユーザー要求：全権限の管理。",
            "権限ロール選定：付与すべきアカウントロールを選択してください。",
            "【システム権限付与】記事の閲覧のみが可能で編集・投稿ができないのは閲覧者。ユーザー要求：記事閲覧専用アカウント。\n権限ロール選定：付与すべきアカウントロールを選択してください。",
            k6_choices_roles, "role_admin", "role_subscriber"
        ),
        (
            "23",
            "【アカウント管理】記事の新規執筆および公開権限を持つのは投稿者。ユーザー要求：自力での記事執筆と公開。",
            "権限ロール選定：付与すべきアカウントロールを選択してください。",
            "【アカウント管理】記事の執筆はできるが下書き保存のみで公開権限がないのは寄稿者。ユーザー要求：下書き提出のみの外部ライター。\n権限ロール選定：付与すべきアカウントロールを選択してください。",
            k6_choices_roles, "role_author", "role_contributor"
        ),
        (
            "24",
            "【規約違反制裁】重大なスパム行為を行ったアカウントは直ちにアクセス権を完全剥奪し停止者とする。処分対象：スパム連投アカウント。",
            "権限ロール選定：変更すべきアカウントロールを選択してください。",
            "【編集体制設定】他者の記事の修正・レイアウト変更・承認公開を行えるのは編集者。ユーザー要求：校正および公開承認業務。\n権限ロール選定：付与すべきアカウントロールを選択してください。",
            k6_choices_roles, "role_banned", "role_editor"
        ),
    ]

    for gid, ctx1, q1, q2, c_defs, t1, t2 in k6_defs:
        choices = make_choices(c_defs)
        if "\n" in q2:
            ctx2, q2_clean = q2.split("\n", 1)
        else:
            ctx2, q2_clean = ctx1, q2
        pairs.append({
            "id": f"rf_varch_k6_{gid}_s1",
            "group_id": f"rf_varch_k6_{gid}",
            "family": "variable_choice",
            "choice_count": 6,
            "context": ctx1,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_varch_k6_{gid}_s2",
            "group_id": f"rf_varch_k6_{gid}",
            "family": "variable_choice",
            "choice_count": 6,
            "context": ctx2,
            "question": q2_clean,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # 5. K = 8 (6 pairs: 25 to 30)
    # 8 Japanese regions
    k8_choices_regions = [
        ("reg_hokkaido", "北海道地方"), ("reg_tohoku", "東北地方"),
        ("reg_kanto", "関東地方"), ("reg_chubu", "中部地方"),
        ("reg_kinki", "近畿地方"), ("reg_chugoku", "中国地方"),
        ("reg_shikoku", "四国地方"), ("reg_kyushu", "九州・沖縄地方")
    ]
    k8_defs = [
        (
            "25",
            "【配送エリア区分】青森県・岩手県・秋田県・宮城県・山形県・福島県への配送は東北地方管轄便に仕分ける。お届け先住所：宮城県仙台市青葉区。",
            "配送管轄仕分：仕分けるべき地方区分を選択してください。",
            "【配送エリア区分】福岡県・佐賀県・長崎県・熊本県・大分県・宮崎県・鹿児島県・沖縄県は九州地方管轄便に仕分ける。お届け先住所：福岡県福岡市博多区。\n配送管轄仕分：仕分けるべき地方区分を選択してください。",
            k8_choices_regions, "reg_tohoku", "reg_kyushu"
        ),
        (
            "26",
            "【拠点配属判断】大阪府・京都府・兵庫県・奈良県・滋賀県・和歌山県の営業所は近畿地方支社が統括する。配属先：京都営業所。",
            "統括支社判定：管轄する地方支社を選択してください。",
            "【拠点配属判断】愛知県・静岡県・岐阜県・長野県・新潟県・富山県・石川県・福井県・山梨県は中部地方支社が統括。配属先：愛知県名古屋支社。\n統括支社判定：管轄する地方支社を選択してください。",
            k8_choices_regions, "reg_kinki", "reg_chubu"
        ),
        (
            "27",
            "【観光プロモーション】香川県・徳島県・愛媛県・高知県を対象としたお遍路観光キャンペーンを企画。対象エリア：徳島県鳴門市。",
            "観光地方判定：対象となる地方ブロックを選択してください。",
            "【観光プロモーション】広島県・岡山県・山口県・鳥取県・島根県を対象とした山陽山陰観光キャンペーンを企画。対象エリア：広島県尾道市。\n観光地方判定：対象となる地方ブロックを選択してください。",
            k8_choices_regions, "reg_shikoku", "reg_chugoku"
        ),
        (
            "28",
            "【気象予報警報】東京都・神奈川県・埼玉県・千葉県・茨城県・栃木県・群馬県に大雨洪水注意報を発令。対象自治体：神奈川県横浜市。",
            "気象警報ブロック：注意報が適用される地方ブロックを選択してください。",
            "【気象予報警報】道央・道北・道東・道南を含む全域に大雪暴風警報を発令。対象自治体：札幌市中央区。\n気象警報ブロック：注意報が適用される地方ブロックを選択してください。",
            k8_choices_regions, "reg_kanto", "reg_hokkaido"
        ),
        (
            "29",
            "【農業出荷連盟】四国温州みかんの出荷管理協議会は四国地方連盟が運営する。生産農家：愛媛県八幡浜市のみかん園。",
            "農業連盟判定：所属する地方連盟を選択してください。",
            "【農業出荷連盟】博多あまおう苺の出荷管理協議会は九州地方連盟が運営する。生産農家：福岡県八女市の苺農家。\n農業連盟判定：所属する地方連盟を選択してください。",
            k8_choices_regions, "reg_shikoku", "reg_kyushu"
        ),
        (
            "30",
            "【電力送配電エリア】中部電力パワーグリッドの供給エリア（愛知・岐阜・三重・長野・静岡富士川以西）は中部地方。所在地：岐阜県岐阜市。",
            "電力エリア判定：送配電事業者エリアを選択してください。",
            "【電力送配電エリア】関西電力送配電の供給エリア（大阪・京都・兵庫・奈良・滋賀・和歌山）は近畿地方。所在地：兵庫県神戸市中央区。\n電力エリア判定：送配電事業者エリアを選択してください。",
            k8_choices_regions, "reg_chubu", "reg_kinki"
        ),
    ]

    for gid, ctx1, q1, q2, c_defs, t1, t2 in k8_defs:
        choices = make_choices(c_defs)
        if "\n" in q2:
            ctx2, q2_clean = q2.split("\n", 1)
        else:
            ctx2, q2_clean = ctx1, q2
        pairs.append({
            "id": f"rf_varch_k8_{gid}_s1",
            "group_id": f"rf_varch_k8_{gid}",
            "family": "variable_choice",
            "choice_count": 8,
            "context": ctx1,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_varch_k8_{gid}_s2",
            "group_id": f"rf_varch_k8_{gid}",
            "family": "variable_choice",
            "choice_count": 8,
            "context": ctx2,
            "question": q2_clean,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # 6. K = 12 (5 pairs: 31 to 35)
    # 12 Months of the year
    k12_choices_months = [
        ("month_01", "1月（睦月）"), ("month_02", "2月（如月）"), ("month_03", "3月（弥生）"),
        ("month_04", "4月（卯月）"), ("month_05", "5月（皐月）"), ("month_06", "6月（水無月）"),
        ("month_07", "7月（文月）"), ("month_08", "8月（葉月）"), ("month_09", "9月（長月）"),
        ("month_10", "10月（神無月）"), ("month_11", "11月（霜月）"), ("month_12", "12月（師走）")
    ]
    k12_defs = [
        (
            "31",
            "【全社行事暦】新入社員入社式および新年度キックオフは4月初旬に執り行う。対象行事：新入社員入社式。",
            "行事開催月選定：開催すべき該当月を選択してください。",
            "【全社行事暦】年間業績総括忘年会および納会は12月下旬に執り行う。対象行事：年間納会。\n行事開催月選定：開催すべき該当月を選択してください。",
            k12_choices_months, "month_04", "month_12"
        ),
        (
            "32",
            "【季節イベント】七夕まつりおよび夏季賞与の支給は7月に実施する。対象行事：七夕イベント。",
            "イベント月判定：実施すべき該当月を選択してください。",
            "【季節イベント】ハロウィンパレードおよび期末棚卸しは10月末に実施する。対象行事：ハロウィンパレード。\nイベント月判定：実施すべき該当月を選択してください。",
            k12_choices_months, "month_07", "month_10"
        ),
        (
            "33",
            "【法定手続日程】前年所得の確定申告書提出期間は2月16日から3月15日まで。対象月：申告開始月（2月）。",
            "税務日程判定：申告受付が開始される該当月を選択してください。",
            "【法定手続日程】労働保険年度更新申告書の提出期間は6月1日から7月10日まで。対象月：申告開始月（6月）。\n税務日程判定：申告受付が開始される該当月を選択してください。",
            k12_choices_months, "month_02", "month_06"
        ),
        (
            "34",
            "【社内健康管理】全社員インフルエンザ予防接種の推奨期間は11月中に完了すること。対象月：予防接種月。",
            "健康月間判定：接種を実施すべき該当月を選択してください。",
            "【社内健康管理】熱中症予防強化月間として全現場に塩分補給タブレットを配布するのは8月中。対象月：熱中症予防月。\n健康月間判定：接種を実施すべき該当月を選択してください。",
            k12_choices_months, "month_11", "month_08"
        ),
        (
            "35",
            "【防災点検日程】年始の全社初出式および安全祈願祭は1月4日に挙行する。対象行事：年初安全祈願祭。",
            "月次日程選定：挙行すべき該当月を選択してください。",
            "【防災点検日程】防災の日（9月1日）に伴う総合防災避難訓練は9月第1週に実施する。対象行事：総合防災訓練。\n月次日程選定：挙行すべき該当月を選択してください。",
            k12_choices_months, "month_01", "month_09"
        ),
    ]

    for gid, ctx1, q1, q2, c_defs, t1, t2 in k12_defs:
        choices = make_choices(c_defs)
        if "\n" in q2:
            ctx2, q2_clean = q2.split("\n", 1)
        else:
            ctx2, q2_clean = ctx1, q2
        pairs.append({
            "id": f"rf_varch_k12_{gid}_s1",
            "group_id": f"rf_varch_k12_{gid}",
            "family": "variable_choice",
            "choice_count": 12,
            "context": ctx1,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_varch_k12_{gid}_s2",
            "group_id": f"rf_varch_k12_{gid}",
            "family": "variable_choice",
            "choice_count": 12,
            "context": ctx2,
            "question": q2_clean,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # 7. K = 16 (5 pairs: 36 to 40)
    # 16 Categories (e.g. EC product categories or company departments)
    k16_choices_depts = [
        ("dept_01", "総務部"), ("dept_02", "人事労務部"), ("dept_03", "経理財務部"), ("dept_04", "法務知財部"),
        ("dept_05", "情報システム部"), ("dept_06", "広報IR部"), ("dept_07", "経営企画部"), ("dept_08", "営業第1部"),
        ("dept_09", "営業第2部"), ("dept_10", "海外事業部"), ("dept_11", "購買調達部"), ("dept_12", "製造技術部"),
        ("dept_13", "品質保証部"), ("dept_14", "研究開発部"), ("dept_15", "物流管理部"), ("dept_16", "CSサポート部")
    ]
    k16_defs = [
        (
            "36",
            "【社内稟議ルーティング】特許出願および商標権侵害の調査に関する申請は法務知財部へ提出する。申請案件：新商標のクリアランス調査。",
            "所管部門選定：稟議を提出すべき担当部署を選択してください。",
            "【社内稟議ルーティング】自社製品のISO9001品質不適合調査および是正措置報告は品質保証部へ提出する。申請案件：ロット不良の是正報告。\n所管部門選定：稟議を提出すべき担当部署を選択してください。",
            k16_choices_depts, "dept_04", "dept_13"
        ),
        (
            "37",
            "【全社業務分掌】海外現地法人の設立および外為法規制の照会は海外事業部が担当する。案件：ベトナム子会社設立。",
            "主管部署判定：担当すべき管轄部署を選択してください。",
            "【全社業務分掌】有価証券報告書の作成および決算短信の東証開示は経理財務部が担当する。案件：四半期決算短信開示。\n主管部署判定：担当すべき管轄部署を選択してください。",
            k16_choices_depts, "dept_10", "dept_03"
        ),
        (
            "38",
            "【社内窓口案内】新卒・中途採用の面接日程調整および給与査定は人事労務部が管轄する。相談：中途採用のオファー面談。",
            "担当部署選定：相談すべき社内窓口を選択してください。",
            "【社内窓口案内】社内ネットワークのVPN接続障害およびPC貸与は情報システム部が管轄する。相談：リモート用VPNが繋がらない。\n担当部署選定：相談すべき社内窓口を選択してください。",
            k16_choices_depts, "dept_02", "dept_05"
        ),
        (
            "39",
            "【資材調達規程】製造用原材料のサプライヤー相見積もりおよび購入契約交渉は購買調達部が行う。案件：半導体部材の新規調達先交渉。",
            "業務所管選定：担当すべき調達部門を選択してください。",
            "【資材調達規程】完成品の全国倉庫間輸送およびトラック配送の手配は物流管理部が行う。案件：福岡倉庫への幹線トラック手配。\n業務所管選定：担当すべき調達部門を選択してください。",
            k16_choices_depts, "dept_11", "dept_15"
        ),
        (
            "40",
            "【顧客対応方針】製品購入後のエンドユーザーからの使い方クレーム対応はCSサポート部が一次対応する。案件：操作方法の苦情電話。",
            "窓口判定：対応すべきカスタマー部門を選択してください。",
            "【顧客対応方針】次世代全固体電池の基礎物理化学実験および特許試作は研究開発部が担当する。案件：新規電解質材料の合成実験。\n窓口判定：対応すべきカスタマー部門を選択してください。",
            k16_choices_depts, "dept_16", "dept_14"
        ),
    ]

    for gid, ctx1, q1, q2, c_defs, t1, t2 in k16_defs:
        choices = make_choices(c_defs)
        if "\n" in q2:
            ctx2, q2_clean = q2.split("\n", 1)
        else:
            ctx2, q2_clean = ctx1, q2
        pairs.append({
            "id": f"rf_varch_k16_{gid}_s1",
            "group_id": f"rf_varch_k16_{gid}",
            "family": "variable_choice",
            "choice_count": 16,
            "context": ctx1,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_varch_k16_{gid}_s2",
            "group_id": f"rf_varch_k16_{gid}",
            "family": "variable_choice",
            "choice_count": 16,
            "context": ctx2,
            "question": q2_clean,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    return pairs
