"""Research Fresh Suite: logical_operator_generalization (100 pairs, 200 cases).

Coverage of 10 logical operators x 10 pairs:
1. and_logic: 両方の条件成立を要求
2. or_logic: いずれかの条件成立を要求
3. not_logic: 単一または二重の明示的否定
4. gte_boundary: 以上 (>=) vs 超過 (>)
5. lte_boundary: 以下 (<=) vs 未満 (<)
6. default_exception: 原則規定と例外規定の衝突
7. override_rule: 上位命令・緊急割り込みによる上書き
8. first_match: リスト順序に基づく最先頭適合ルール
9. priority_conflict: 複数ルール抵触時の明示的優先順位
10. reverse_criterion: 逆基準（最も非推奨・禁止・違反）

All cases are contrastive pairs with distinct targets.
Token length guaranteed <= 350 (< 512 hard ceiling).
"""

from typing import Any, Dict, List, Tuple


def make_choices(defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in defs]


def get_fresh_logical_operators_pairs() -> List[Dict[str, Any]]:
    pairs = []

    # 1. AND Logic (10 pairs: groups 01 to 10)
    # Target 1 vs Target 2 contrast based on whether BOTH conditions are met vs only ONE
    and_defs = [
        (
            "01",
            "クラウドDB自動フェイルオーバー規程：『レプリケーション遅延が1秒未満、かつセカンダリノードのCPU使用率が60%以下の場合に限り自動昇格を実行する』。現在の監視データ：レプリケーション遅延0.2秒、セカンダリCPU使用率52%。",
            "フェイルオーバー実行判定：自動昇格を実行すべきか判定してください。",
            "クラウドDB自動フェイルオーバー規程：『レプリケーション遅延が1秒未満、かつセカンダリノードのCPU使用率が60%以下の場合に限り自動昇格を実行する』。現在の監視データ：レプリケーション遅延0.2秒、セカンダリCPU使用率78%。\nフェイルオーバー実行判定：自動昇格を実行すべきか判定してください。",
            [("execute_auto_promote", "セカンダリを自動昇格する"), ("hold_manual_intervention", "自動昇格を見送り手動介入を要請する"), ("reboot_cluster_nodes", "クラスタ全ノードを強制再起動する")],
            "execute_auto_promote", "hold_manual_intervention"
        ),
        (
            "02",
            "製薬クリーンルーム入室基準：『入室バッジ認証が有効、かつ差圧計が15Pa以上を示している場合のみ自動ドアを解錠する』。計測値：認証OK、前室差圧18Pa。",
            "扉インターロック判定：自動解錠を許可するか選択してください。",
            "製薬クリーンルーム入室基準：『入室バッジ認証が有効、かつ差圧計が15Pa以上を示している場合のみ自動ドアを解錠する』。計測値：認証OK、前室差圧11Pa。\n扉インターロック判定：自動解錠を許可するか選択してください。",
            [("unlock_entrance_door", "入室ドアを解錠する"), ("keep_locked_alarm", "ドア施錠を維持し差圧警告を発報する"), ("vent_quarantine_room", "無菌室の空気を大気放散する")],
            "unlock_entrance_door", "keep_locked_alarm"
        ),
        (
            "03",
            "高精度3Dプリンタ造形開始条件：『チャンバー温度が65℃に達し、かつノズル先端のオートレベリング誤差が0.02mm以内のとき造形を開始する』。現在の状態：チャンバー66℃、レベリング誤差0.015mm。",
            "造形開始判定：プリントシーケンスを進めるべきか選択してください。",
            "高精度3Dプリンタ造形開始条件：『チャンバー温度が65℃に達し、かつノズル先端のオートレベリング誤差が0.02mm以内のとき造形を開始する』。現在の状態：チャンバー60℃、レベリング誤差0.012mm。\n造形開始判定：プリントシーケンスを進めるべきか選択してください。",
            [("start_print_sequence", "3Dプリント造形を開始する"), ("wait_chamber_heating", "造形を待機し加熱を継続する"), ("purge_filament_spool", "フィラメントを全量排出廃棄する")],
            "start_print_sequence", "wait_chamber_heating"
        ),
        (
            "04",
            "越境EC輸出税関申告：『インボイス記載価格が20万円以下、かつ該非判定書で非該当と証明されている貨物は簡易通関とする』。貨物情報：申告価格12万円、該非判定：非該当証明済み。",
            "通関手続き選択：適用すべき通関ルートを選択してください。",
            "越境EC輸出税関申告：『インボイス記載価格が20万円以下、かつ該非判定書で非該当と証明されている貨物は簡易通関とする』。貨物情報：申告価格18万円、該非判定：軍民両用リスト規制該当社内判定。\n通関手続き選択：適用すべき通関ルートを選択してください。",
            [("route_simplified_customs", "簡易通関ルートで申告する"), ("route_formal_export_license", "経済産業省個別輸出許可申請ルートへ回す"), ("confiscate_cargo_customs", "貨物を税関没収手続きにする")],
            "route_simplified_customs", "route_formal_export_license"
        ),
        (
            "05",
            "LNGタンカー着桟荷役基準：『平均風速が10m/s未満、かつ波高が1.0m未満のとき着桟荷役パイプを接続する』。気象実測値：風速7m/s、波高0.6m。",
            "荷役作業判定：ローディングアームの接続を行うか選択してください。",
            "LNGタンカー着桟荷役基準：『平均風速が10m/s未満、かつ波高が1.0m未満のとき着桟荷役パイプを接続する』。気象実測値：風速12m/s、波高0.7m。\n荷役作業判定：ローディングアームの接続を行うか選択してください。",
            [("connect_loading_arms", "ローディングアームを接続し荷役準備する"), ("abort_and_standoff", "接続を見送り洋上待機を指示する"), ("emergency_release_berth", "係留索を即時切断して緊急離桟する")],
            "connect_loading_arms", "abort_and_standoff"
        ),
        (
            "06",
            "自動車自動追従クルーズ（ACC）：『前方ミリ波レーダーが先行車を捕捉し、かつ車載カメラの白線認識が両側有効なときステアリング支援を起動する』。センサ状態：先行車補足あり、白線認識：左右ともに追従安定。",
            "制御モード指示：ステアリング支援の作動を選択してください。",
            "自動車自動追従クルーズ（ACC）：『前方ミリ波レーダーが先行車を捕捉し、かつ車載カメラの白線認識が両側有効なときステアリング支援を起動する』。センサ状態：先行車捕捉あり、白線認識：右側白線が逆光でロスト中。\n制御モード指示：ステアリング支援の作動を選択してください。",
            [("engage_steering_assist", "ステアリング操舵支援を作動する"), ("suppress_steering_assist", "ステアリング操舵支援を解除・待機する"), ("engage_hard_emergency_brake", "非常急ブレーキを急作動させる")],
            "engage_steering_assist", "suppress_steering_assist"
        ),
        (
            "07",
            "病院救急トリアージ迅速投薬：『収縮期血圧が90mmHg以上、かつ心拍数が50bpm以上のとき血管拡張薬ニトログリセリンを投与可能』。患者バイタル：血圧110/70mmHg、心拍数68bpm。",
            "投薬実施判断：ニトログリセリンの投与可否を選択してください。",
            "病院救急トリアージ迅速投薬：『収縮期血圧が90mmHg以上、かつ心拍数が50bpm以上のとき血管拡張薬ニトログリセリンを投与可能』。患者バイタル：血圧82/54mmHg、心拍数72bpm。\n投薬実施判断：ニトログリセリンの投与可否を選択してください。",
            [("administer_nitroglycerin", "指示通りニトログリセリンを投与する"), ("withhold_contraindicated", "投与を見送り昇圧措置を優先する"), ("administer_high_dose_potassium", "高濃度カリウム急速静注を行う")],
            "administer_nitroglycerin", "withhold_contraindicated"
        ),
        (
            "08",
            "太陽光発電蓄電池逆潮流制御：『蓄電池残量が95%以上、かつ日射強度が800W/m2以上の場合に余剰電力のグリッド売電を開始する』。計測値：残量98%、日射強度890W/m2。",
            "売電リレー操作：系統連系インバータの動作を選択してください。",
            "太陽光発電蓄電池逆潮流制御：『蓄電池残量が95%以上、かつ日射強度が800W/m2以上の場合に余剰電力のグリッド売電を開始する』。計測値：残量91%、日射強度920W/m2。\n売電リレー操作：系統連系インバータの動作を選択してください。",
            [("export_surplus_to_grid", "余剰電力を商用系統へ逆潮流売電する"), ("charge_battery_internal", "全発電量を蓄電池充電へ優先回送する"), ("trip_solar_panels_shunt", "全太陽光ストリングを接地短絡する")],
            "export_surplus_to_grid", "charge_battery_internal"
        ),
        (
            "09",
            "金融ローン自動与信審査：『勤続年数が3年以上、かつ年収負担率（返済比率）が30%以下の場合に自動承認とする』。申込者データ：勤続4年半、返済比率24%。",
            "与信判定結果：この申込に対する初期審査結果を選択してください。",
            "金融ローン自動与信審査：『勤続年数が3年以上、かつ年収負担率（返済比率）が30%以下の場合に自動承認とする』。申込者データ：勤続1年2ヶ月、返済比率22%。\n与信判定結果：この申込に対する初期審査結果を選択してください。",
            [("approve_instant_credit", "自動与信を即時承認する"), ("refer_manual_underwriting", "自動承認せず人手本審査へ回付する"), ("register_blacklist_fraud", "反社・不正名義疑いとして否決登録する")],
            "approve_instant_credit", "refer_manual_underwriting"
        ),
        (
            "10",
            "半導体露光装置ウェハーアライメント：『X軸位置決め精度が0.5nm以内、かつ真空度が1.0e-5Pa以下のときEUV露光パルスを発振する』。測定値：X軸偏差0.3nm、真空チャンバー8.5e-6Pa。",
            "露光シーケンス指示：露光トリガーの送信可否を選択してください。",
            "半導体露光装置ウェハーアライメント：『X軸位置決め精度が0.5nm以内、かつ真空度が1.0e-5Pa以下のときEUV露光パルスを発振する』。測定値：X軸偏差0.8nm、真空チャンバー7.0e-6Pa。\n露光シーケンス指示：露光トリガーの送信可否を選択してください。",
            [("trigger_euv_exposure", "EUV露光パルス照射を実行する"), ("realign_stage_position", "照射を保留しステージ微動再位置決めを行う"), ("vent_chamber_to_air", "露光チャンバーを大気開放する")],
            "trigger_euv_exposure", "realign_stage_position"
        ),
    ]

    for gid, ctx, q1, q2, c_defs, t1, t2 in and_defs:
        choices = make_choices(c_defs)
        if "\n" in q2:
            ctx2, q2_clean = q2.split("\n", 1)
        else:
            ctx2, q2_clean = ctx, q2
        pairs.append({
            "id": f"rf_op_and_{gid}_s1",
            "group_id": f"rf_op_and_{gid}",
            "family": "logical_operators",
            "operator_type": "and",
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_op_and_{gid}_s2",
            "group_id": f"rf_op_and_{gid}",
            "family": "logical_operators",
            "operator_type": "and",
            "context": ctx2,
            "question": q2_clean,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # 2. OR Logic (10 pairs: groups 11 to 20)
    # Either condition A OR condition B satisfies the action
    or_defs = [
        (
            "11",
            "データセンター緊急冷却ファン起動基準：『サーバルーム吸気温度が32℃以上、または室内湿度が75%以上のいずれかを満たしたとき補助チラーファンを起動する』。計測値：温度34℃、湿度50%。",
            "補助チラー制御指示：ファンの起動動作を選択してください。",
            "データセンター緊急冷却ファン起動基準：『サーバルーム吸気温度が32℃以上、または室内湿度が75%以上のいずれかを満たしたとき補助チラーファンを起動する』。計測値：温度28℃、湿度58%。\n補助チラー制御指示：ファンの起動動作を選択してください。",
            [("activate_auxiliary_chiller", "補助チラーファンを直ちに起動する"), ("maintain_standard_cooling", "通常冷却モードを維持し補助ファン停止"), ("shut_down_all_servers", "サーバ電源を一括強制遮断する")],
            "activate_auxiliary_chiller", "maintain_standard_cooling"
        ),
        (
            "12",
            "航空機滑走路進入許可条件：『風向横風成分が15ノット以上、または滑走路路面摩擦係数が0.25未満のいずれかであれば着陸復行（ゴーアラウンド）を命じる』。気象報告：横風18ノット、摩擦係数0.40。",
            "着陸進入指令：管制塔からの指示を選択してください。",
            "航空機滑走路進入許可条件：『風向横風成分が15ノット以上、または滑走路路面摩擦係数が0.25未満のいずれかであれば着陸復行（ゴーアラウンド）を命じる』。気象報告：横風8ノット、摩擦係数0.38。\n着陸進入指令：管制塔からの指示を選択してください。",
            [("order_go_around_immediate", "直ちに着陸復行（ゴーアラウンド）を指示する"), ("clear_to_land_continue", "滑走路着陸進入の継続を許可する"), ("jettison_aircraft_fuel", "上空での燃料海上投棄を緊急指示する")],
            "order_go_around_immediate", "clear_to_land_continue"
        ),
        (
            "13",
            "情報セキュリティSIEM自動隔離ルール：『同一IPからの不審ログイン試行が5分間に20回以上、または国外脅威インテリジェンスリスト一致のいずれかで端末通信を隔離する』。ログ分析：5分間試行回数4回、脅威リスト該当（一致判定）。",
            "SIEM自動防御アクション：ファイアウォール動作を選択してください。",
            "情報セキュリティSIEM自動隔離ルール：『同一IPからの不審ログイン試行が5分間に20回以上、または国外脅威インテリジェンスリスト一致のいずれかで端末通信を隔離する』。ログ分析：5分間試行回数6回、脅威リスト非該当。\nSIEM自動防御アクション：ファイアウォール動作を選択してください。",
            [("quarantine_ip_endpoint", "対象IPからの全パケットを即時遮断隔離する"), ("allow_and_audit_traffic", "通常通信を許可しアクセスログのみ記録する"), ("delete_entire_siem_database", "SIEMログデータベースを全消去する")],
            "quarantine_ip_endpoint", "allow_and_audit_traffic"
        ),
        (
            "14",
            "ボイラー安全弁作動要件：『ボイラー内蒸気圧が1.8MPa以上、または管壁表面温度が450℃以上のいずれかに達したら安全リリーフ弁を開放する』。プラント計装：蒸気圧1.92MPa、管壁温度380℃。",
            "蒸気安全制御：リリーフ弁の操作を選択してください。",
            "ボイラー安全弁作動要件：『ボイラー内蒸気圧が1.8MPa以上、または管壁表面温度が450℃以上のいずれかに達したら安全リリーフ弁を開放する』。プラント計装：蒸気圧1.50MPa、管壁温度410℃。\n蒸気安全制御：リリーフ弁の操作を選択してください。",
            [("open_safety_relief_valve", "安全リリーフ弁を開放し蒸気を放散する"), ("keep_relief_valve_closed", "弁を全閉維持し定格燃焼を継続する"), ("inject_cold_water_rapidly", "ボイラー内へ冷水を急激に直接注水する")],
            "open_safety_relief_valve", "keep_relief_valve_closed"
        ),
        (
            "15",
            "食品製造ライン金属異物検知：『金属検出器のアラームが鳴動したか、または重量チェッカーが±5%以上の誤差を検出した製品パッケージを自動リジェクトシューターで排除する』。製品検査：金属アラーム無、重量誤差+7.2%。",
            "コンベア選別指示：このパッケージの処置を選択してください。",
            "食品製造ライン金属異物検知：『金属検出器のアラームが鳴動したか、または重量チェッカーが±5%以上の誤差を検出した製品パッケージを自動リジェクトシューターで排除する』。製品検査：金属アラーム無、重量誤差-1.1%。\nコンベア選別指示：このパッケージの処置を選択してください。",
            [("reject_package_to_bin", "リジェクトシューターを作動させ不良箱へ排除する"), ("pass_package_to_packaging", "合格として下流の箱詰め工程へ送出する"), ("stop_entire_factory_power", "工場全体の主電源を即時遮断する")],
            "reject_package_to_bin", "pass_package_to_packaging"
        ),
        (
            "16",
            "ECサイト不正注文検知：『配送先住所が私書箱転送サービス、または決済クレジットカードの有効期限入力不一致のいずれかに該当する場合は決済を保留し目視確認に回す』。注文情報：配送先住所は一般個人宅、カード有効期限入力不一致。",
            "注文処理ルーティング：この注文の取り扱いを選択してください。",
            "ECサイト不正注文検知：『配送先住所が私書箱転送サービス、または決済クレジットカードの有効期限入力不一致のいずれかに該当する場合は決済を保留し目視確認に回す』。注文情報：配送先住所は一般個人宅、カード有効期限完全一致。\n注文処理ルーティング：この注文の取り扱いを選択してください。",
            [("hold_for_manual_risk_review", "注文を保留し不正対策担当者の目視審査へ送る"), ("process_instant_fulfillment", "通常注文として即時自動出荷処理を実行する"), ("auto_refund_and_ban_user", "即時返金した上で顧客アカウントを永久凍結する")],
            "hold_for_manual_risk_review", "process_instant_fulfillment"
        ),
        (
            "17",
            "化学工場排ガス無害化スクラバー：『排気ダクトの硫黄酸化物SOx濃度が50ppm以上、または煙突排気温度が200℃以上のいずれかで水酸化ナトリウムアルカリシャワーを全開にする』。排ガス計測：SOx濃度12ppm、排気温度225℃。",
            "スクラバー薬注ポンプ操作：散布バルブの動作を選択してください。",
            "化学工場排ガス無害化スクラバー：『排気ダクトの硫黄酸化物SOx濃度が50ppm以上、または煙突排気温度が200℃以上のいずれかで水酸化ナトリウムアルカリシャワーを全開にする』。排ガス計測：SOx濃度25ppm、排気温度160℃。\nスクラバー薬注ポンプ操作：散布バルブの動作を選択してください。",
            [("open_alkali_spray_fully", "アルカリ洗浄水シャワー弁を全開にする"), ("maintain_low_flow_circulation", "通常循環低流量モードを維持する"), ("vent_raw_gas_to_bypass", "中和塔を通さず排ガスを大気バイパス放出する")],
            "open_alkali_spray_fully", "maintain_low_flow_circulation"
        ),
        (
            "18",
            "自治体高齢者見守りアラート：『宅内水道メーターが24時間微動だにしない、または感震センサーが震度4以上を検知したとき緊急安否確認メールを民生委員へ配信する』。宅内センサー：直近水道使用ゼロ（丸26時間静止）、地震検知なし。",
            "見守りシステム動作：配信判断を選択してください。",
            "自治体高齢者見守りアラート：『宅内水道メーターが24時間微動だにしない、または感震センサーが震度4以上を検知したとき緊急安否確認メールを民生委員へ配信する』。宅内センサー：直近2時間前にトイレ給水検知あり、地震検知なし。\n見守りシステム動作：配信判断を選択してください。",
            [("send_welfare_officer_alert", "民生委員へ緊急安否確認メールを配信する"), ("suppress_alert_standby", "通知を保留し通常センサ監視を継続する"), ("dispatch_police_swat_team", "警察特殊急襲部隊を現場突入させる")],
            "send_welfare_officer_alert", "suppress_alert_standby"
        ),
        (
            "19",
            "原子力発電所非常用ディーゼル発電機（D/G）：『主母線電圧が定格の80%以下に低下したか、または格納容器圧力が150kPa以上に上昇した場合に非常用D/Gを自動起動する』。計測計装：母線電圧72%へ低下、格納容器圧力110kPa。",
            "D/G自動起動シーケンス：発電機の始動を選択してください。",
            "原子力発電所非常用ディーゼル発電機（D/G）：『主母線電圧が定格の80%以下に低下したか、または格納容器圧力が150kPa以上に上昇した場合に非常用D/Gを自動起動する』。計測計装：母線電圧98%、格納容器圧力115kPa。\nD/G自動起動シーケンス：発電機の始動を選択してください。",
            [("crank_emergency_diesel_gen", "非常用ディーゼル発電機を直ちに起動する"), ("hold_dg_in_standby_mode", "発電機の起動を見送り待機待機状態を維持する"), ("drain_fuel_from_diesel_tank", "D/G燃料タンクの軽油を海へ排出投棄する")],
            "crank_emergency_diesel_gen", "hold_dg_in_standby_mode"
        ),
        (
            "20",
            "精密工作機械主軸保護インターロック：『主軸回転振動加速度が4.0Gを超過したか、または軸受潤滑油圧が0.15MPaを下回ったとき主軸サーボを急停止する』。センサー監視：振動加速度1.2G、潤滑油圧0.08MPa。",
            "サーボコントローラ制御：主軸モーターの動作を選択してください。",
            "精密工作機械主軸保護インターロック：『主軸回転振動加速度が4.0Gを超過したか、または軸受潤滑油圧が0.15MPaを下回ったとき主軸サーボを急停止する』。センサー監視：振動加速度2.1G、潤滑油圧0.28MPa。\nサーボコントローラ制御：主軸モーターの動作を選択してください。",
            [("trip_spindle_motor_emergency", "主軸モーターサーボ電源を即時遮断急停止する"), ("maintain_cutting_feedrate", "現在の切削送り速度を維持して加工継続する"), ("reverse_tool_at_maximum_rpm", "工具を最高回転数で逆回転させる")],
            "trip_spindle_motor_emergency", "maintain_cutting_feedrate"
        ),
    ]

    for gid, ctx, q1, q2, c_defs, t1, t2 in or_defs:
        choices = make_choices(c_defs)
        if "\n" in q2:
            ctx2, q2_clean = q2.split("\n", 1)
        else:
            ctx2, q2_clean = ctx, q2
        pairs.append({
            "id": f"rf_op_or_{gid}_s1",
            "group_id": f"rf_op_or_{gid}",
            "family": "logical_operators",
            "operator_type": "or",
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_op_or_{gid}_s2",
            "group_id": f"rf_op_or_{gid}",
            "family": "logical_operators",
            "operator_type": "or",
            "context": ctx2,
            "question": q2_clean,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # 3. NOT / Negation Logic (10 pairs: groups 21 to 30)
    # Testing critical negative conditions and double negation
    not_defs = [
        (
            "21",
            "自動薬品調剤ロボット安全チェック：『患者の電子カルテにペニシリン系アレルギーの登録が【ない】場合に限りアンピシリンカプセルを調剤する』。患者カルテ：アレルギー情報欄は【登録なし・アレルギー既往歴なし】。",
            "調剤ロボット実行指示：アンピシリンの調剤可否を選択してください。",
            "自動薬品調剤ロボット安全チェック：『患者の電子カルテにペニシリン系アレルギーの登録が【ない】場合に限りアンピシリンカプセルを調剤する』。患者カルテ：アレルギー情報欄に【ペニシリンショック既往あり】と記載。\n調剤ロボット実行指示：アンピシリンの調剤可否を選択してください。",
            [("dispense_ampicillin_capsule", "アンピシリンカプセルの調剤を実行する"), ("abort_dispensing_contraindication", "調剤を中止し処方医へ禁忌疑義照会を出す"), ("substitute_with_cyanide_tablet", "青酸配糖体錠剤へ自動代替調剤する")],
            "dispense_ampicillin_capsule", "abort_dispensing_contraindication"
        ),
        (
            "22",
            "新世代暗号化通信プロトコル：『通信パケットに改ざん検知フラグが【立っていない】ことを確認できれば復号処理を継続する』。パケットヘッダ解析：改ざんチェックサム一致、改ざんフラグは0（未設定）。",
            "復号エンジン指示：暗号解読ステップを選択してください。",
            "新世代暗号化通信プロトコル：『通信パケットに改ざん検知フラグが【立っていない】ことを確認できれば復号処理を継続する』。パケットヘッダ解析：改ざんフラグが1（異常検知設定済み）。\n復号エンジン指示：暗号解読ステップを選択してください。",
            [("proceed_decrypt_payload", "ペイロードの復号処理を続行する"), ("drop_tampered_packet", "パケットを破棄し改ざん検知ログを記録する"), ("send_plain_secret_to_sender", "秘密鍵平文を送信元へ返信する")],
            "proceed_decrypt_payload", "drop_tampered_packet"
        ),
        (
            "23",
            "高電圧変電所開閉器点検規程：『母線接地スイッチが投入されて【いない】状態では主変圧器断路器の閉路を【行ってはならない】』。現在の現場状態：母線接地スイッチは【投入済・確実にアース接続中】。",
            "断路器操作判断：断路器の閉路操作が可能か選択してください。",
            "高電圧変電所開閉器点検規程：『母線接地スイッチが投入されて【いない】状態では主変圧器断路器の閉路を【行ってはならない】』。現在の現場状態：母線接地スイッチは【未投入・アース開放中】。\n断路器操作判断：断路器の閉路操作が可能か選択してください。",
            [("allow_disconnect_closure", "安全条件成立として断路器を閉路する"), ("strictly_forbid_closure", "インターロックに従い断路器閉路を禁止する"), ("short_circuit_all_three_phases", "三相高圧母線を直接短絡接地する")],
            "allow_disconnect_closure", "strictly_forbid_closure"
        ),
        (
            "24",
            "金融AML（反社・マネロン対策）送金ルール：『受取口座名義人が経済制裁対象者リストに含まれて【いない】ことが非該当証明されなければ送金を実行してはならない』。照会結果：制裁対象者リストに【該当なし（非該当確認完了）】。",
            "国際送金実行可否：送金トランザクションの処理を選択してください。",
            "金融AML（反社・マネロン対策）送金ルール：『受取口座名義人が経済制裁対象者リストに含まれて【いない】ことが非該当証明されなければ送金を実行してはならない』。照会結果：制裁対象者リストに【完全一致・制裁指定個人】。\n国際送金実行可否：送金トランザクションの処理を選択してください。",
            [("release_wire_transfer", "送金電文を発信し処理を完了する"), ("freeze_and_report_fiu", "送金を即時凍結し資金情報機関へ届出する"), ("bypass_aml_screening_cache", "AML照合を無効化して無審査送金する")],
            "release_wire_transfer", "freeze_and_report_fiu"
        ),
        (
            "25",
            "無人配送ロボット走行安全規程：『歩行者進行進路に障害物が【全く存在しない】ことが確認されない限り、時速6km以上への加速を【禁止する】』。ステレオカメラ判定：進路10m以内に【前方歩行者なし・障害物ゼロ】。",
            "速度制御指示：最高速度引き上げの可否を選択してください。",
            "無人配送ロボット走行安全規程：『歩行者進行進路に障害物が【全く存在しない】ことが確認されない限り、時速6km以上への加速を【禁止する】』。ステレオカメラ判定：進路4m前方に【ベビーカーを押す歩行者を検知】。\n速度制御指示：最高速度引き上げの可否を選択してください。",
            [("accelerate_to_rated_speed", "時速6kmへの加速を許可する"), ("keep_crawl_speed_or_stop", "加速を禁止し微速徐行または一時停止する"), ("disable_all_lidar_sensors", "安全LiDARセンサーを全停止して突進する")],
            "accelerate_to_rated_speed", "keep_crawl_speed_or_stop"
        ),
        (
            "26",
            "自治体建築確認申請審査：『敷地境界において接道長が2m【未満ではない（2m以上ある）】ことを確認できた場合に確認済証を交付する』。測量図面：道路境界接道長2.4m。",
            "確認済証交付判定：交付可能か選択してください。",
            "自治体建築確認申請審査：『敷地境界において接道長が2m【未満ではない（2m以上ある）】ことを確認できた場合に確認済証を交付する』。測量図面：道路境界接道長1.6m。\n確認済証交付判定：交付可能か選択してください。",
            [("issue_building_permit", "建築確認済証を交付する"), ("reject_insufficient_frontage", "接道長不足として交付を却下する"), ("demolish_adjacent_public_road", "公道を削って敷地を拡張する")],
            "issue_building_permit", "reject_insufficient_frontage"
        ),
        (
            "27",
            "有機溶剤タンク清掃作業許可：『酸素濃度が18%未満に【落ちていない（18%以上維持）】状態であり、かつ可燃性ガス濃度が爆発下限界の10%を【超えていない】ときのみ入槽を許可する』。ガス検知器：酸素20.9%、可燃性ガス0%。",
            "入槽作業許可判定：作業員のタンク内立ち入りを選択してください。",
            "有機溶剤タンク清掃作業許可：『酸素濃度が18%未満に【落ちていない（18%以上維持）】状態であり、かつ可燃性ガス濃度が爆発下限界の10%を【超えていない】ときのみ入槽を許可する』。ガス検知器：酸素16.5%（酸欠状態）、可燃性ガス0%。\n入槽作業許可判定：作業員のタンク内立ち入りを選択してください。",
            [("grant_tank_entry_permit", "タンク内立入作業許可証を発行する"), ("deny_entry_force_ventilation", "入槽を拒絶し強制換気を継続する"), ("ignite_flare_inside_tank", "タンク内部で裸火を着火させる")],
            "grant_tank_entry_permit", "deny_entry_force_ventilation"
        ),
        (
            "28",
            "特許出願の新規性喪失例外規程：『出願前に発明が公知となって【いない】場合、または公知となった日から1年を【徒過していない（1年以内）】場合は新規性喪失の例外適用が可能』。事実関係：学会発表で公知化してから8ヶ月経過。",
            "特許法第30条適用判定：新規性喪失の例外適用が可能か選択してください。",
            "特許法第30条適用判定：『出願前に発明が公知となって【いない】場合、または公知となった日から1年を【徒過していない（1年以内）】場合は新規性喪失の例外適用が可能』。事実関係：一般展示会で発表してから1年4ヶ月経過。\n特許法第30条適用判定：新規性喪失の例外適用が可能か選択してください。",
            [("eligible_article_30_exception", "特許法30条例外適用として適格と認める"), ("ineligible_lacking_novelty", "法定期間徒過により新規性喪失と判定する"), ("invalidate_all_prior_art_patents", "全世界の先行特許を無効審判請求する")],
            "eligible_article_30_exception", "ineligible_lacking_novelty"
        ),
        (
            "29",
            "高速道路ETC自動開閉バー：『車両ETCカードの有効期限が【切れていない】こと、および車載器との暗号通信エラーが【発生していない】とき進入バーを開く』。判定結果：有効期限来年まで有効、通信エラー無（正常応答）。",
            "ETC開閉バー制御：バーの開閉を選択してください。",
            "高速道路ETC自動開閉バー：『車両ETCカードの有効期限が【切れていない】こと、および車載器との暗号通信エラーが【発生していない】とき進入バーを開く』。判定結果：有効期限先月末で満了（失効済）、通信エラー無。\nETC開閉バー制御：バーの開閉を選択してください。",
            [("open_etc_tollgate_barrier", "ETC進入バーを開いて通行許可する"), ("keep_barrier_closed_stop", "バーを閉じたまま車両を停止誘導する"), ("drop_spike_strip_to_puncture", "タイヤパンク用スパイク板を展開する")],
            "open_etc_tollgate_barrier", "keep_barrier_closed_stop"
        ),
        (
            "30",
            "原子炉制御棒全挿入（スクラム）テスト：『安全保護系警報が【一件もクリアされていない（警報未発令ではない）】状態では手動テストを開始してはならない』。盤面ステータス：全警報正常クリア灯点灯（警報発令ゼロ）。",
            "スクラムテスト実行判断：手動テストを開始できるか選択してください。",
            "原子炉制御棒全挿入（スクラム）テスト：『安全保護系警報が【一件もクリアされていない（警報未発令ではない）】状態では手動テストを開始してはならない』。盤面ステータス：一次冷却材流量低下警報が点灯継続中。\nスクラムテスト実行判断：手動テストを開始できるか選択してください。",
            [("authorize_manual_scram_test", "条件クリアを確認し手動テストを開始する"), ("prohibit_test_due_to_alarm", "警報未解消のためテスト開始を厳禁する"), ("extract_all_control_rods_full", "全制御棒を炉心から一気に引き抜く")],
            "authorize_manual_scram_test", "prohibit_test_due_to_alarm"
        ),
    ]

    for gid, ctx, q1, q2, c_defs, t1, t2 in not_defs:
        choices = make_choices(c_defs)
        if "\n" in q2:
            ctx2, q2_clean = q2.split("\n", 1)
        else:
            ctx2, q2_clean = ctx, q2
        pairs.append({
            "id": f"rf_op_not_{gid}_s1",
            "group_id": f"rf_op_not_{gid}",
            "family": "logical_operators",
            "operator_type": "not",
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_op_not_{gid}_s2",
            "group_id": f"rf_op_not_{gid}",
            "family": "logical_operators",
            "operator_type": "not",
            "context": ctx2,
            "question": q2_clean,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # 4. GTE Boundary: >= vs > (10 pairs: groups 31 to 40)
    # Testing strict threshold comparison when actual == threshold
    gte_defs = [
        (
            "31",
            "倉庫在庫補充自動発注ルール：『有効在庫数が発注点【30個以上】残っていれば発注を保留し、【30個未満】になったら追加発注を出す』。現在の在庫棚卸数：ちょうど【30個】。",
            "資材発注判定：現在の在庫数に基づくアクションを選択してください。",
            "倉庫在庫補充自動発注ルール：『有効在庫数が発注点【30個より多い】場合に限り発注を保留し、【30個以下】であれば追加発注を出す』。現在の在庫棚卸数：ちょうど【30個】。\n資材発注判定：現在の在庫数に基づくアクションを選択してください。",
            [("hold_replenishment_order", "在庫十分として追加発注を保留する"), ("place_replenishment_order", "発注点を下回ったため追加発注を出す"), ("discard_entire_warehouse_stock", "倉庫の全在庫を廃棄処分する")],
            "hold_replenishment_order", "place_replenishment_order"
        ),
        (
            "32",
            "学術奨学金受給資格規程：『通算GPAが【3.50以上】であれば奨学金全額給付、【3.50未満】であれば半額給付とする』。申請学生のGPA実績：ちょうど【3.50】。",
            "給付額決定判定：この学生に適用する給付区分を選択してください。",
            "学術奨学金受給資格規程：『通算GPAが【3.50を超える】学生に限り全額給付とし、【3.50以下】は半額給付とする』。申請学生のGPA実績：ちょうど【3.50】。\n給付額決定判定：この学生に適用する給付区分を選択してください。",
            [("grant_full_scholarship", "全額給付を適用する"), ("grant_half_scholarship", "半額給付を適用する"), ("expel_student_from_university", "大学から退学処分とする")],
            "grant_full_scholarship", "grant_half_scholarship"
        ),
        (
            "33",
            "大型貨物船港湾水深クリアランス：『キール下余裕水深（UKC）が【1.50m以上】確保できる場合は入港を許可し、【1.50m未満】の場合は沖待ちを命じる』。潮位計算結果：UKCちょうど【1.50m】。",
            "入港管制指示：港湾への進入可否を選択してください。",
            "大型貨物船港湾水深クリアランス：『キール下余裕水深（UKC）が【1.50mより大きい】場合に限り入港を許可し、【1.50m以下】の場合は沖待ちを命じる』。潮位計算結果：UKCちょうど【1.50m】。\n入港管制指示：港湾への進入可否を選択してください。",
            [("permit_port_entry", "入港および着桟を許可する"), ("order_offshore_anchorage", "余裕水深不足として沖合投錨待機を命じる"), ("beach_ship_on_sandbar", "砂浜に故意に乗り上げ座礁させる")],
            "permit_port_entry", "order_offshore_anchorage"
        ),
        (
            "34",
            "半導体ウェハー膜厚品質検査：『酸化膜厚が規格下限【45.0nm以上】であれば合格ラインへ送り、【45.0nm未満】であればエッチング再処理へ回す』。エリプソメータ測定値：ちょうど【45.0nm】。",
            "検査工程振り分け：このロットの判定を選択してください。",
            "半導体ウェハー膜厚品質検査：『酸化膜厚が規格下限【45.0nmを超える】もののみ合格とし、【45.0nm以下】はエッチング再処理へ回す』。エリプソメータ測定値：ちょうど【45.0nm】。\n検査工程振り分け：このロットの判定を選択してください。",
            [("accept_to_next_process", "合格として次工程フォトリソへ送る"), ("reroute_to_etch_reprocess", "不合格としてエッチング再処理へ回す"), ("shatter_wafer_into_pieces", "ウェハーを金槌で物理破砕する")],
            "accept_to_next_process", "reroute_to_etch_reprocess"
        ),
        (
            "35",
            "金融信用スコア自動審査：『スコアが【700点以上】の申込者は低金利プレミアム枠とし、【700点未満】は通常金利枠とする』。信用情報機関スコア：ちょうど【700点】。",
            "金利プラン適用：適用すべき金利プランを選択してください。",
            "金融信用スコア自動審査：『スコアが【700点を上回る】申込者のみ低金利プレミアム枠とし、【700点以下】は通常金利枠とする』。信用情報機関スコア：ちょうど【700点】。\n金利プラン適用：適用すべき金利プランを選択してください。",
            [("apply_premium_low_interest", "低金利プレミアムプランを適用する"), ("apply_standard_interest_rate", "通常金利プランを適用する"), ("freeze_customer_bank_account", "顧客の預金口座を強制差押凍結する")],
            "apply_premium_low_interest", "apply_standard_interest_rate"
        ),
        (
            "36",
            "気象防災大雨避難基準：『時間降水量が【50mm以上】で高齢者等避難を発令し、【50mm未満】は大雨注意喚起に留める』。雨量レーダー実測：時間降水量ちょうど【50mm】。",
            "自治体避難情報発令：発令すべき防災レベルを選択してください。",
            "気象防災大雨避難基準：『時間降水量が【50mmを超えた】場合に限り高齢者等避難を発令し、【50mm以下】は大雨注意喚起に留める』。雨量レーダー実測：時間降水量ちょうど【50mm】。\n自治体避難情報発令：発令すべき防災レベルを選択してください。",
            [("issue_elderly_evacuation_alert", "高齢者等避難（警戒レベル3）を発令する"), ("maintain_weather_advisory_only", "大雨注意報の継続喚起に留める"), ("order_nuclear_bunker_evacuation", "地下核シェルターへの退避を命じる")],
            "issue_elderly_evacuation_alert", "maintain_weather_advisory_only"
        ),
        (
            "37",
            "ボイラー安全過熱保護：『排ガス温度が【300℃以上】に達したときエコノマイザバイパス弁を開き、【300℃未満】では全閉維持する』。熱電対計測温度：ちょうど【300℃】。",
            "排ガスダンパー操作：エコノマイザバイパス弁の動作を選択してください。",
            "ボイラー安全過熱保護：『排ガス温度が【300℃を超過した】場合に限りエコノマイザバイパス弁を開き、【300℃以下】では全閉維持する』。熱電対計測温度：ちょうど【300℃】。\n排ガスダンパー操作：エコノマイザバイパス弁の動作を選択してください。",
            [("open_economizer_bypass", "エコノマイザバイパス弁を開放する"), ("keep_economizer_bypass_closed", "エコノマイザバイパス弁を全閉維持する"), ("flood_factory_with_sewage", "工場敷地へ未処理下水を逆流させる")],
            "open_economizer_bypass", "keep_economizer_bypass_closed"
        ),
        (
            "38",
            "航空機燃料残量着陸優先権：『残余飛行可能時間が【45分以上】あれば標準進入経路を維持し、【45分未満】となったら燃料優先着陸を宣言する』。FMC計算残余時間：ちょうど【45分】。",
            "機長運航判断：航空管制への要求を選択してください。",
            "航空機燃料残量着陸優先権：『残余飛行可能時間が【45分より長い】間は標準進入経路を維持し、【45分以下】となったら燃料優先着陸を宣言する』。FMC計算残余時間：ちょうど【45分】。\n機長運航判断：航空管制への要求を選択してください。",
            [("maintain_standard_approach", "標準進入順序を維持して降下する"), ("declare_min_fuel_priority", "ミニマムフューエル宣言し優先進入を要求する"), ("shut_down_all_engines_glide", "全エンジンを自ら停止して滑空する")],
            "maintain_standard_approach", "declare_min_fuel_priority"
        ),
        (
            "39",
            "医薬品アンプル密封性検査：『内部真空度が【80kPa以上】であれば良品合格、【80kPa未満】であれば漏れ不良として廃棄する』。差圧検査器測定：ちょうど【80kPa】。",
            "品質合否判定：このアンプルの処置を選択してください。",
            "医薬品アンプル密封性検査：『内部真空度が【80kPaを上回る】製品のみ良品合格とし、【80kPa以下】は漏れ不良として廃棄する』。差圧検査器測定：ちょうど【80kPa】。\n品質合否判定：このアンプルの処置を選択してください。",
            [("accept_as_hermetic_pass", "気密合格として包装工程へ移送する"), ("reject_as_leak_failure", "気密不良として廃棄シューターへ落とす"), ("distribute_untested_to_patients", "未検査のまま患者へ緊急投与する")],
            "accept_as_hermetic_pass", "reject_as_leak_failure"
        ),
        (
            "40",
            "高圧送電線たるみ限界監視：『電線地上高が【7.0m以上】保たれていれば送電継続、【7.0m未満】に垂れ下がった場合は送電停止する』。レーザー測距測定：電線地上高ちょうど【7.0m】。",
            "送電指令操作：送電線路の運用を選択してください。",
            "高圧送電線たるみ限界監視：『電線地上高が【7.0mを超える】高さにある間のみ送電継続し、【7.0m以下】に垂れ下がった場合は送電停止する』。レーザー測距測定：電線地上高ちょうど【7.0m】。\n送電指令操作：送電線路の運用を選択してください。",
            [("continue_power_transmission", "通常通り送電を継続する"), ("trip_transmission_line_halt", "地上高不足のため送電を遮断停止する"), ("sever_support_towers_cables", "送電鉄塔の支線を切断して倒壊させる")],
            "continue_power_transmission", "trip_transmission_line_halt"
        ),
    ]

    for gid, ctx, q1, q2, c_defs, t1, t2 in gte_defs:
        choices = make_choices(c_defs)
        if "\n" in q2:
            ctx2, q2_clean = q2.split("\n", 1)
        else:
            ctx2, q2_clean = ctx, q2
        pairs.append({
            "id": f"rf_op_gte_{gid}_s1",
            "group_id": f"rf_op_gte_{gid}",
            "family": "logical_operators",
            "operator_type": "gte_boundary",
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_op_gte_{gid}_s2",
            "group_id": f"rf_op_gte_{gid}",
            "family": "logical_operators",
            "operator_type": "gte_boundary",
            "context": ctx2,
            "question": q2_clean,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # 5. LTE Boundary: <= vs < (10 pairs: groups 41 to 50)
    lte_defs = [
        (
            "41",
            "医薬品クリーンルーム微粒子管理：『0.5μm以上の浮遊微粒子数が【3,520個/m3以下】であればグレードB適格、【3,520個/m3超】であれば不適格とする』。パーティクルカウンター計測値：ちょうど【3,520個/m3】。",
            "清浄度適格判定：この部屋の適合状況を選択してください。",
            "医薬品クリーンルーム微粒子管理：『0.5μm以上の浮遊微粒子数が【3,520個/m3未満】に収まっている場合のみグレードB適格とし、【3,520個/m3以上】は不適格とする』。パーティクルカウンター計測値：ちょうど【3,520個/m3】。\n清浄度適格判定：この部屋の適合状況を選択してください。",
            [("certify_grade_b_compliant", "グレードB清浄度基準に適合と認定する"), ("declare_grade_b_noncompliant", "許容上限超過のため不適合と判定する"), ("fill_room_with_exhaust_smoke", "ディーゼル排気ガスを部屋へ充満させる")],
            "certify_grade_b_compliant", "declare_grade_b_noncompliant"
        ),
        (
            "42",
            "小型無人航空機（ドローン）重量規制：『機体総重量が【100g以下】であれば模型航空機（登録免除）、【100g超】であれば国交省機体登録必須とする』。精密電子天秤計測：ちょうど【100g】。",
            "機体登録判定：航空法に基づく登録義務を選択してください。",
            "小型無人航空機（ドローン）重量規制：『機体総重量が【100g未満】であれば模型航空機（登録免除）、【100g以上】であれば国交省機体登録必須とする』。精密電子天秤計測：ちょうど【100g】。\n機体登録判定：航空法に基づく登録義務を選択してください。",
            [("exempt_from_registration", "重量基準内として機体登録を免除する"), ("require_mandatory_registration", "重量基準到達のため国交省機体登録を義務付ける"), ("confiscate_and_destroy_drone", "機体を即座に没収しハンマーで粉砕する")],
            "exempt_from_registration", "require_mandatory_registration"
        ),
        (
            "43",
            "半導体製造露光マスク欠陥検査：『異物パーティクルサイズが【15nm以下】であれば修復不要で合格ラインとし、【15nm超】であればFIBレーザー修復へ回す』。光学レビュー測定値：最大欠陥ちょうど【15nm】。",
            "マスク合否判定：フォトマスクの処理工程を選択してください。",
            "半導体製造露光マスク欠陥検査：『異物パーティクルサイズが【15nm未満】であれば修復不要で合格ラインとし、【15nm以上】であればFIBレーザー修復へ回す』。光学レビュー測定値：最大欠陥ちょうど【15nm】。\nマスク合否判定：フォトマスクの処理工程を選択してください。",
            [("pass_mask_without_repair", "許容欠陥内として修復不要で合格とする"), ("route_to_fib_laser_repair", "許容上限のためFIBレーザー修復へ送る"), ("expose_mask_to_hydrofluoric_acid", "マスク表面へフッ酸原液を散布する")],
            "pass_mask_without_repair", "route_to_fib_laser_repair"
        ),
        (
            "44",
            "下水処理放流水水質汚濁基準：『放流水のBOD（生物化学的酸素要求量）が【10mg/L以下】であれば河川放流を許可し、【10mg/L超】であれば再曝気処理へ回す』。水質計分析値：BODちょうど【10mg/L】。",
            "放流ゲート制御：放流水の取り扱いを選択してください。",
            "下水処理放流水水質汚濁基準：『放流水のBOD（生物化学的酸素要求量）が【10mg/L未満】であれば河川放流を許可し、【10mg/L以上】であれば再曝気処理へ回す』。水質計分析値：BODちょうど【10mg/L】。\n放流ゲート制御：放流水の取り扱いを選択してください。",
            [("permit_discharge_to_river", "基準クリアとして河川への放流を許可する"), ("reroute_to_rebubbling_tank", "基準超過のため再曝気反応タンクへ返送する"), ("dump_raw_sludge_to_drinking_well", "生汚泥を上水道取水井戸へ直接投入する")],
            "permit_discharge_to_river", "reroute_to_rebubbling_tank"
        ),
        (
            "45",
            "特急列車カーブ進入速度制限：『半径400m曲線の制限速度は【85km/h以下】であり、【85km/h超】の場合はATS自動減速ブレーキが作動する』。現在の速度発電機計測値：ちょうど【85km/h】。",
            "保安装置動作：ATSの動作を選択してください。",
            "特急列車カーブ進入速度制限：『半径400m曲線の制限速度は【85km/h未満】であり、【85km/h以上】の場合はATS自動減速ブレーキが作動する』。現在の速度発電機計測値：ちょうど【85km/h】。\n保安装置動作：ATSの動作を選択してください。",
            [("allow_passage_no_brake", "制限範囲内としてブレーキ非作動で力行継続"), ("actuate_ats_speed_reduction", "制限速度超過としてATS常用ブレーキを作動"), ("derail_train_by_switch_flip", "ポイントを意図的に途中転換し脱線させる")],
            "allow_passage_no_brake", "actuate_ats_speed_reduction"
        ),
        (
            "46",
            "通信衛星バッテリー放電深度（DOD）管理：『日陰飛行中の放電深度が【60%以下】であれば通常ミッション運用を継続し、【60%超】の場合は非必須観測機器を省電力停止する』。テレメトリ値：DODちょうど【60%】。",
            "衛星電力運用：観測機器の電源状態を選択してください。",
            "通信衛星バッテリー放電深度（DOD）管理：『日陰飛行中の放電深度が【60%未満】であれば通常ミッション運用を継続し、【60%以上】の場合は非必須観測機器を省電力停止する』。テレメトリ値：DODちょうど【60%】。\n衛星電力運用：観測機器の電源状態を選択してください。",
            [("maintain_all_payload_instruments", "許容深度内として全観測機器の通電を継続する"), ("shed_non_essential_payloads", "バッテリー保護のため非必須観測機器を遮断する"), ("detonate_satellite_battery_cells", "衛星バッテリーセルを船上自爆爆破する")],
            "maintain_all_payload_instruments", "shed_non_essential_payloads"
        ),
        (
            "47",
            "臨床試験被験者年齢適格要件：『本治験に参加可能な被験者年齢は【65歳以下】とし、【65歳超】の高齢者は除外基準に抵触する』。志願者の生年月日換算年齢：同意取得日時点でちょうど【65歳0ヶ月】。",
            "治験登録適格判定：この志願者の登録可否を選択してください。",
            "臨床試験被験者年齢適格要件：『本治験に参加可能な被験者年齢は【65歳未満】とし、【65歳以上】の高齢者は除外基準に抵触する』。志願者の生年月日換算年齢：同意取得日時点でちょうど【65歳0ヶ月】。\n治験登録適格判定：この志願者の登録可否を選択してください。",
            [("enroll_eligible_subject", "参加適格として治験登録を実施する"), ("exclude_over_age_limit", "年齢上限超過として登録を除外する"), ("falsify_subject_birthdate", "年齢を公的書類で勝手に改ざんする")],
            "enroll_eligible_subject", "exclude_over_age_limit"
        ),
        (
            "48",
            "高精度金型放電加工電極消耗度：『銅電極の先端減耗量が【0.050mm以下】であれば仕上げ加工を継続し、【0.050mm超】であれば電極交換を実行する』。機上タッチプローブ計測：減耗量ちょうど【0.050mm】。",
            "NC加工シーケンス：放電電極の処置を選択してください。",
            "高精度金型放電加工電極消耗度：『銅電極の先端減耗量が【0.050mm未満】であれば仕上げ加工を継続し、【0.050mm以上】であれば電極交換を実行する』。機上タッチプローブ計測：減耗量ちょうど【0.050mm】。\nNC加工シーケンス：放電電極の処置を選択してください。",
            [("continue_finish_spark_erosion", "許容内として仕上げ放電加工を続行する"), ("execute_automatic_tool_change", "消耗限界到達として自動電極交換を行う"), ("weld_electrode_to_workpiece", "電極をワークに最大電流でアーク溶着させる")],
            "continue_finish_spark_erosion", "execute_automatic_tool_change"
        ),
        (
            "49",
            "産業用ロボット協働安全規格（ISO 10218）：『人との接触検知力が【150N以下】であれば安全一時停止からの自動復帰を許可し、【150N超】であれば非常停止ロックとする』。力覚センサ検出値：ちょうど【150N】。",
            "ロボット制御盤動作：リセット後の動作を選択してください。",
            "産業用ロボット協働安全規格（ISO 10218）：『人との接触検知力が【150N未満】であれば安全一時停止からの自動復帰を許可し、【150N以上】であれば非常停止ロックとする』。力覚センサ検出値：ちょうど【150N】。\nロボット制御盤動作：リセット後の動作を選択してください。",
            [("allow_auto_resume_cycle", "軽度接触として自動サイクル復帰を許可する"), ("engage_hard_safety_lockout", "過負荷衝撃として非常停止ロックアウトを維持する"), ("swing_robot_arm_at_max_speed", "ロボットアームを周囲へ全速力で振り回す")],
            "allow_auto_resume_cycle", "engage_hard_safety_lockout"
        ),
        (
            "50",
            "化学プラント配管肉厚減肉管理：『腐食による減肉深さが設計裕度【2.0mm以下】であれば次回定期点検まで運転継続し、【2.0mm超】であれば緊急補修パッチを施工する』。超音波厚さ計実測：減肉ちょうど【2.0mm】。",
            "保全工事判定：この配管スプールの処置を選択してください。",
            "化学プラント配管肉厚減肉管理：『腐食による減肉深さが設計裕度【2.0mm未満】であれば次回定期点検まで運転継続し、【2.0mm以上】であれば緊急補修パッチを施工する』。超音波厚さ計実測：減肉ちょうど【2.0mm】。\n保全工事判定：この配管スプールの処置を選択してください。",
            [("continue_operation_to_next_turnaround", "許容範囲内として次回定修まで運転を継続する"), ("apply_emergency_reinforce_patch", "裕度限界到達として緊急補修パッチを施工する"), ("pierce_pipe_with_welding_torch", "バーナーで配管に穴を開けて液漏れさせる")],
            "continue_operation_to_next_turnaround", "apply_emergency_reinforce_patch"
        ),
    ]

    for gid, ctx, q1, q2, c_defs, t1, t2 in lte_defs:
        choices = make_choices(c_defs)
        if "\n" in q2:
            ctx2, q2_clean = q2.split("\n", 1)
        else:
            ctx2, q2_clean = ctx, q2
        pairs.append({
            "id": f"rf_op_lte_{gid}_s1",
            "group_id": f"rf_op_lte_{gid}",
            "family": "logical_operators",
            "operator_type": "lte_boundary",
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_op_lte_{gid}_s2",
            "group_id": f"rf_op_lte_{gid}",
            "family": "logical_operators",
            "operator_type": "lte_boundary",
            "context": ctx2,
            "question": q2_clean,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # 6. Default + Exception (10 pairs: groups 51 to 60)
    # Default general rule applies UNLESS an explicit exception condition is triggered
    def_exc_defs = [
        (
            "51",
            "社内経費精算ポリシー：『【原則】宿泊費の精算上限は1泊12,000円とする。【例外】役員同行出張、または海外国際会議での公式指定ホテル宿泊の場合は実費全額精算を認める』。出張実績：単独国内出張、宿泊費1泊15,000円。",
            "経費精算承認判定：承認すべき宿泊費の精算額を選択してください。",
            "社内経費精算ポリシー：『【原則】宿泊費の精算上限は1泊12,000円とする。【例外】役員同行出張、または海外国際会議での公式指定ホテル宿泊の場合は実費全額精算を認める』。出張実績：海外国際学会での公式指定ホテル宿泊、宿泊費1泊28,000円。\n経費精算承認判定：承認すべき宿泊費の精算額を選択してください。",
            [("approve_capped_allowance", "原則上限の1泊12,000円までを承認する"), ("approve_full_actual_expense", "例外適用として実費全額を承認する"), ("refuse_entire_business_trip", "出張全体の全経費を不承認却下する")],
            "approve_capped_allowance", "approve_full_actual_expense"
        ),
        (
            "52",
            "港湾コンテナターミナル搬出入規定：『【原則】コンテナのターミナル外搬出は事前Web予約トラックに限る。【例外】冷蔵・冷凍（リーファー）生鮮貨物で電源断の恐れがある緊急貨物は予約なしの臨時ゲートインを許可する』。搬入車両：一般雑貨ドライコンテナ、Web予約なしで来場。",
            "ゲート通過判定：この車両のゲート進入を許可するか選択してください。",
            "港湾コンテナターミナル搬出入規定：『【原則】コンテナのターミナル外搬出は事前Web予約トラックに限る。【例外】冷蔵・冷凍（リーファー）生鮮貨物で電源断の恐れがある緊急貨物は予約なしの臨時ゲートインを許可する』。搬入車両：冷凍マグロ積載リーファーコンテナ（発電機故障で庫内温度上昇中）、予約なし来場。\nゲート通過判定：この車両のゲート進入を許可するか選択してください。",
            [("turn_back_unreserved_truck", "原則通り予約なしとして入場を断りUターンさせる"), ("grant_emergency_gate_access", "例外規定を適用し緊急臨時進入を許可する"), ("tip_over_container_truck", "トラックをクレーンで横転転覆させる")],
            "turn_back_unreserved_truck", "grant_emergency_gate_access"
        ),
        (
            "53",
            "図書館特別貴重書閲覧規程：『【原則】所蔵資料の館外貸出は禁止とする。【例外】学術研究機関が主催する公立博物館への企画展出品であり、かつ耐火輸送保険が付保されている場合は館外貸出を許可する』。利用申請：大学教授による個人研究室での論文執筆目的の閲覧。",
            "貸出審査判定：資料の館外持ち出しの可否を選択してください。",
            "図書館特別貴重書閲覧規程：『【原則】所蔵資料の館外貸出は禁止とする。【例外】学術研究機関が主催する公立博物館への企画展出品であり、かつ耐火輸送保険が付保されている場合は館外貸出を許可する』。利用申請：国立歴史民俗博物館の特別展展示、保険付保承認済み。\n貸出審査判定：資料の館外持ち出しの可否を選択してください。",
            [("deny_takeout_in_library_only", "原則通り館外貸出を不可とし館内閲覧に限定する"), ("permit_insured_museum_loan", "例外規程を満たすため館外特別貸出を許可する"), ("shred_rare_archival_book", "貴重古文書を手動シュレッダーで破棄する")],
            "deny_takeout_in_library_only", "permit_insured_museum_loan"
        ),
        (
            "54",
            "金融為替送金手数料規程：『【原則】外貨電信送金手数料は一律2,500円とする。【例外】預金残高1,000万円以上のプライベートバンク会員、または当月為替取引高5,000万円以上の顧客は手数料無料とする』。顧客ステータス：預金残高300万円、当月為替取引高200万円。",
            "手数料算出判定：適用すべき送金手数料を選択してください。",
            "金融為替送金手数料規程：『【原則】外貨電信送金手数料は一律2,500円とする。【例外】預金残高1,000万円以上のプライベートバンク会員、または当月為替取引高5,000万円以上の顧客は手数料無料とする』。顧客ステータス：預金残高1,800万円のプライベートバンク会員。\n手数料算出判定：適用すべき送金手数料を選択してください。",
            [("charge_standard_fee_2500", "原則手数料の2,500円を請求する"), ("waive_transfer_fee_completely", "例外適用として送金手数料を全額無料免除する"), ("confiscate_all_bank_deposits", "顧客の全預金を銀行収益として没収する")],
            "charge_standard_fee_2500", "waive_transfer_fee_completely"
        ),
        (
            "55",
            "公立学校施設休日利用規程：『【原則】体育館の休日一般団体利用は有料（1時間1,500円）とする。【例外】地域防災訓練、または市教育委員会が直接共催する青少年育成事業は利用料を免除する』。利用団体：近隣の社会人草バスケットボールサークル（一般同好会）。",
            "利用料金算定：適用すべき利用料区分を選択してください。",
            "公立学校施設休日利用規程：『【原則】体育館の休日一般団体利用は有料（1時間1,500円）とする。【例外】地域防災訓練、または市教育委員会が直接共催する青少年育成事業は利用料を免除する』。利用団体：自治会自主防災組織による住民初期消火・避難所設営訓練。\n利用料金算定：適用すべき利用料区分を選択してください。",
            [("charge_standard_hourly_fee", "原則規定の1時間1,500円を有料徴収する"), ("exempt_from_facility_fee", "例外規定を適用し体育館利用料を全額免除する"), ("lock_doors_and_trap_citizens", "避難住民を体育館内に閉じ込める")],
            "charge_standard_hourly_fee", "exempt_from_facility_fee"
        ),
        (
            "56",
            "医薬品治験薬処方プロトコル：『【原則】治験薬の処方間隔は28日以上あけること。【例外】被験者にグレード3以上の副作用（好中球減少等）が発現し医師が投薬中断を指示した場合は、予定期日を待たず直ちに休薬とする』。被験者状態：投与後21日目、副作用なし・バイタル極めて良好。",
            "処方管理判断：治験薬の休薬・投与管理を選択してください。",
            "医薬品治験薬処方プロトコル：『【原則】治験薬の処方間隔は28日以上あけること。【例外】被験者にグレード3以上の副作用（好中球減少等）が発現し医師が投薬中断を指示した場合は、予定期日を待たず直ちに休薬とする』。被験者状態：投与後14日目、グレード3の発熱性好中球減少症を発症。\n処方管理判断：治験薬の休薬・投与管理を選択してください。",
            [("continue_scheduled_protocol", "原則通り予定の28日間隔まで投与スケジュールを維持する"), ("immediate_safety_drug_interruption", "例外を適用し直ちに治験薬の休薬・中断を行う"), ("increase_drug_dose_tenfold", "治験薬の投与量を10倍に増量する")],
            "continue_scheduled_protocol", "immediate_safety_drug_interruption"
        ),
        (
            "57",
            "特許庁手続期間延長基準：『【原則】拒絶理由通知に対する意見書提出期間の延長は1回（1ヶ月）に限り認める。【例外】在外者（外国在住出願人）による出願、または天災地変等の不可抗力に起因する場合は最大3回（3ヶ月）までの延長を認める』。出願人：日本国内法人、2回目の延長請求を提出（天災なし）。",
            "期間延長可否判定：延長請求の取り扱いを選択してください。",
            "特許庁手続期間延長基準：『【原則】拒絶理由通知に対する意見書提出期間の延長は1回（1ヶ月）に限り認める。【例外】在外者（外国在住出願人）による出願、または天災地変等の不可抗力に起因する場合は最大3回（3ヶ月）までの延長を認める』。出願人：ドイツ国籍の在外企業、2回目の延長請求を提出。\n期間延長可否判定：延長請求の取り扱いを選択してください。",
            [("reject_extension_request", "原則上限（1回）超過として延長請求を却下する"), ("grant_additional_extension", "例外（在外者）を適用し追加延長を承認する"), ("cancel_all_examiner_patents", "特許審査官の全資格を剥奪する")],
            "reject_extension_request", "grant_additional_extension"
        ),
        (
            "58",
            "鉄道保線工事夜間作業規程：『【原則】線路上での重機作業は最終終電通過後から始発30分前までに限定する。【例外】線路変状・土砂崩れ等の即時脱線危険を伴う緊急インシデント復旧は日中時間帯でも運行停止手配の上で着手できる』。作業内容：定期レール削正メンテナンス（緊急性なし）。",
            "作業着手判断：重機の線路進入時間帯を選択してください。",
            "鉄道保線工事夜間作業規程：『【原則】線路上での重機作業は最終終電通過後から始発30分前までに限定する。【例外】線路変状・土砂崩れ等の即時脱線危険を伴う緊急インシデント復旧は日中時間帯でも運行停止手配の上で着手できる』。作業内容：大雨による路盤土砂流出、線路浮上を発見。\n作業着手判断：重機の線路進入時間帯を選択してください。",
            [("schedule_for_night_window", "原則通り終電後の夜間作業時間帯に実施する"), ("commence_emergency_daytime_repair", "例外を適用し直ちに運行停止の上緊急復旧着手する"), ("allow_passenger_train_at_top_speed", "崩落現場へ旅客列車を最高速度で突入させる")],
            "schedule_for_night_window", "commence_emergency_daytime_repair"
        ),
        (
            "59",
            "航空機手荷物持込制限：『【原則】液体物の客室持込は100ml以下の個別容器かつジッパー付透明袋封入に限定する。【例外】乳幼児同伴時のベビーミルク、および旅程に必要な処方箋薬品は100ml超過でも検査合格で持込可能』。旅客荷物：単身搭乗客の500mlペットボトル清涼飲料水（未開封市販品）。",
            "保安検査判定：液体物の機内持込可否を選択してください。",
            "航空機手荷物持込制限：『【原則】液体物の客室持込は100ml以下の個別容器かつジッパー付透明袋封入に限定する。【例外】乳幼児同伴時のベビーミルク、および旅程に必要な処方箋薬品は100ml超過でも検査合格で持込可能』。旅客荷物：生後6ヶ月の乳児同伴客の調乳用ベビーミルク200ml（液体検査器合格）。\n保安検査判定：液体物の機内持込可否を選択してください。",
            [("confiscate_liquid_at_checkpoint", "原則規定に従い持込不可として保安検査場で破棄する"), ("permit_liquid_carry_on", "例外規定を適用し機内持込を許可する"), ("detain_passenger_in_solitary", "単身客をテロ容疑で独房拘禁する")],
            "confiscate_liquid_at_checkpoint", "permit_liquid_carry_on"
        ),
        (
            "60",
            "公的統計データ非識別化提供：『【原則】学術調査目的の個人ミクロデータ提供は集計表形式のみとし個票は提供しない。【例外】統計法に基づく大臣認定共同研究であり、かつ専用オンサイト施設での分析に限定する場合は個票データの提供を認める』。申請：民間企業による自社新商品開発マーケティングのための個票請求。",
            "データ提供審査：ミクロデータ提供の可否を選択してください。",
            "公的統計データ非識別化提供：『【原則】学術調査目的の個人ミクロデータ提供は集計表形式のみとし個票は提供しない。【例外】統計法に基づく大臣認定共同研究であり、かつ専用オンサイト施設での分析に限定する場合は個票データの提供を認める』。申請：国立大学による統計法大臣認定共同研究（オンサイト利用誓約済）。\nデータ提供審査：ミクロデータ提供の可否を選択してください。",
            [("reject_microdata_request", "原則通り個票提供不可として集計表のみに制限する"), ("approve_secure_onsite_microdata", "例外要件充足としてオンサイト施設での個票利用を承認する"), ("leak_national_census_on_darkweb", "全世帯の国勢調査データをネット流出させる")],
            "reject_microdata_request", "approve_secure_onsite_microdata"
        ),
    ]

    for gid, ctx, q1, q2, c_defs, t1, t2 in def_exc_defs:
        choices = make_choices(c_defs)
        if "\n" in q2:
            ctx2, q2_clean = q2.split("\n", 1)
        else:
            ctx2, q2_clean = ctx, q2
        pairs.append({
            "id": f"rf_op_exc_{gid}_s1",
            "group_id": f"rf_op_exc_{gid}",
            "family": "logical_operators",
            "operator_type": "default_exception",
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_op_exc_{gid}_s2",
            "group_id": f"rf_op_exc_{gid}",
            "family": "logical_operators",
            "operator_type": "default_exception",
            "context": ctx2,
            "question": q2_clean,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # 7. Override Logic (10 pairs: groups 61 to 70)
    # Higher authority / emergency kill-switch completely overrides routine logic
    override_defs = [
        (
            "61",
            "自動航行コンテナ船機関室制御：『通常航行モードでは最適燃費アルゴリズムに従い主機関回転数を制御する。ただし【船長による手動非常停止E-STOP】が発令された場合は全自動制御を即時上書き無効化し主機トリップを実行する』。現在の状態：通常燃費航行中、船長E-STOP操作なし。",
            "推進制御指示：機関出力制御モードを選択してください。",
            "自動航行コンテナ船機関室制御：『通常航行モードでは最適燃費アルゴリズムに従い主機関回転数を制御する。ただし【船長による手動非常停止E-STOP】が発令された場合は全自動制御を即時上書き無効化し主機トリップを実行する』。現在の状態：操舵室にて船長がE-STOP非常停止ボタンを強打押下。\n推進制御指示：機関出力制御モードを選択してください。",
            [("maintain_auto_fuel_economy", "最適燃費アルゴリズムに従い自動運航を継続する"), ("execute_emergency_override_trip", "自動制御を上書き遮断し主機関を緊急トリップする"), ("ignite_fuel_tanks_intentionally", "燃料タンクへ点火爆破させる")],
            "maintain_auto_fuel_economy", "execute_emergency_override_trip"
        ),
        (
            "62",
            "ビル中央熱源自動スケジュール運転：『全館空調はタイマー設定に基づき18:00に自動減速送風へ切り替わる。ただし【消防連動火災感知器の作動信号】を受信した場合はタイマーを即時上書きし、全給排気ファン停止・防火ダンパー全閉とする』。時刻18:05、火災信号なし。",
            "空調ファン制御：熱源制御シーケンスを選択してください。",
            "ビル中央熱源自動スケジュール運転：『全館空調はタイマー設定に基づき18:00に自動減速送風へ切り替わる。ただし【消防連動火災感知器の作動信号】を受信した場合はタイマーを即時上書きし、全給排気ファン停止・防火ダンパー全閉とする』。時刻18:05、3階防災受信機より火災感知発報受信。\n空調ファン制御：熱源制御シーケンスを選択してください。",
            [("switch_to_evening_low_mode", "タイマー通り18時夜間低速運転モードへ切り替える"), ("fire_override_close_dampers", "火災連動上書きを実行し全ファン停止・防火ダンパー全閉"), ("pump_pure_oxygen_to_fire_zone", "火災発生階へ純酸素ガスを大量送風する")],
            "switch_to_evening_low_mode", "fire_override_close_dampers"
        ),
        (
            "63",
            "無人自動搬送車（AGV）群運行管理：『各AGVは最短配送ルートを自律計算して巡航する。ただし【走行エリア床面安全バンパーの障害物接触信号】を検知した場合は経路計算を上書き遮断し、10ミリ秒以内に機械的非常ブレーキを作動する』。状態：搬送中、バンパー接触なし。",
            "AGV走行制御：車両の駆動コマンドを選択してください。",
            "無人自動搬送車（AGV）群運行管理：『各AGVは最短配送ルートを自律計算して巡航する。ただし【走行エリア床面安全バンパーの障害物接触信号】を検知した場合は経路計算を上書き遮断し、10ミリ秒以内に機械的非常ブレーキを作動する』。状態：前側バンパーが落下パレットに接触。\nAGV走行制御：車両の駆動コマンドを選択してください。",
            [("continue_autonomous_routing", "自律計算ルートに沿って走行を継続する"), ("override_emergency_brake_stop", "自律計算を上書きし非常ブレーキで即時停止する"), ("accelerate_into_obstacle", "障害物に向かって最高速度で突入する")],
            "continue_autonomous_routing", "override_emergency_brake_stop"
        ),
        (
            "64",
            "金融高頻度自動取引（HFT）システム：『ミリ秒単位の板情報モメンタム予測に従い自動注文を発注する。ただし【証券取引所からのサーキットブレーカー発動電文】を受信した場合は全アルゴリズム発注を強制上書きし、全未約定注文を即座に全取消する』。取引状況：通常ザラ場、取引所通知なし。",
            "アルゴリズム発注指示：注文執行アクションを選択してください。",
            "金融高頻度自動取引（HFT）システム：『ミリ秒単位の板情報モメンタム予測に従い自動注文を発注する。ただし【証券取引所からのサーキットブレーカー発動電文】を受信した場合は全アルゴリズム発注を強制上書きし、全未約定注文を即座に全取消する』。取引状況：東証よりサーキットブレーカー発動通知受信。\nアルゴリズム発注指示：注文執行アクションを選択してください。",
            [("submit_algorithm_market_orders", "アルゴリズム予測に基づき通常注文を発注する"), ("circuit_breaker_override_cancel", "発注を強制上書き停止し全未約定注文を即座に取り消す"), ("borrow_unlimited_unhedged_credit", "信用枠の限度を超えて無限に買い建てる")],
            "submit_algorithm_market_orders", "circuit_breaker_override_cancel"
        ),
        (
            "65",
            "遠隔手術支援ロボットマニピュレータ：『執刀医のマスターコンソール操作に追従して鉗子アームを精密微動させる。ただし【患者生体モニタの心停止（アプネア・フラットライン）信号】を受信した場合は追従制御を緊急上書きし、鉗子を自動安全位置へロック退避する』。生体モニタ：心拍数72bpm、血圧正常。",
            "マニピュレータ追従指示：アーム動作を選択してください。",
            "遠隔手術支援ロボットマニピュレータ：『執刀医のマスターコンソール操作に追従して鉗子アームを精密微動させる。ただし【患者生体モニタの心停止（アプネア・フラットライン）信号】を受信した場合は追従制御を緊急上書きし、鉗子を自動安全位置へロック退避する』。生体モニタ：心拍ゼロ・心電図フラットライン検知。\nマニピュレータ追従指示：アーム動作を選択してください。",
            [("follow_surgeon_master_motion", "執刀医の操作に追従して微小切開鉗子を動かす"), ("lockout_and_retract_override", "追従を上書き停止し鉗子を自動ロック退避させる"), ("drive_forceps_into_vital_artery", "鉗子を主要動脈へ全開で突き刺す")],
            "follow_surgeon_master_motion", "lockout_and_retract_override"
        ),
        (
            "66",
            "水力発電ダム放水制御：『通常時は下流利水計画流量（毎秒30トン）を一定放流する。ただし【下流河川水位警戒所より避難警報（氾濫危険水位超過）】を受信した場合は通常流量計画を直ちに上書きし、ダム放水量を半減させて洪水を貯留する』。下流水位計：平常水位（避難警報なし）。",
            "ダムゲート放流制御：放水バルブ開度を選択してください。",
            "水力発電ダム放水制御：『通常時は下流利水計画流量（毎秒30トン）を一定放流する。ただし【下流河川水位警戒所より避難警報（氾濫危険水位超過）】を受信した場合は通常流量計画を直ちに上書きし、ダム放水量を半減させて洪水を貯留する』。下流水位計：氾濫危険水位超過警報受信。\nダムゲート放流制御：放水バルブ開度を選択してください。",
            [("maintain_normal_planned_outflow", "利水計画通りの定格毎秒30トン放流を維持する"), ("flood_control_override_cut_half", "計画を上書きし放水量を緊急半減させて貯水する"), ("dynamite_dam_wall_instantly", "ダム堤体をダイナマイトで爆破決壊させる")],
            "maintain_normal_planned_outflow", "flood_control_override_cut_half"
        ),
        (
            "67",
            "大規模分散ストレージ自動レプリカ再構築：『ノード障害時はバックグラウンド低優先度で別ノードへデータレプリカを再複製する。ただし【運用管理者による最優先保守モード（メンテロック）】が設定された場合は、バックグラウンド複製を即座に上書き中断する』。設定：通常運用中、メンテロック未設定。",
            "ストレージエンジン動作：レプリケーション処理を選択してください。",
            "大規模分散ストレージ自動レプリカ再構築：『ノード障害時はバックグラウンド低優先度で別ノードへデータレプリカを再複製する。ただし【運用管理者による最優先保守モード（メンテロック）】が設定された場合は、バックグラウンド複製を即座に上書き中断する』。設定：管理者によりメンテロックがON設定。\nストレージエンジン動作：レプリケーション処理を選択してください。",
            [("proceed_background_replication", "バックグラウンドでデータ再複製タスクを実行する"), ("pause_replication_override_lock", "メンテロック優先で再複製タスクを上書き一時中断する"), ("format_all_storage_disks_zero", "全ストレージディスクをゼロ埋め初期化する")],
            "proceed_background_replication", "pause_replication_override_lock"
        ),
        (
            "68",
            "半導体プラズマエッチング装置RF電源：『レシピプログラムに従いRF高周波電力を多段階照射する。ただし【真空チャンバーの反射波過大インターロック（反射電力20%超）】を検出した場合はレシピステップを上書き遮断し、RF電源を瞬時シャットダウンする』。高周波モニタ：反射電力3%（極めて安定）。",
            "RFジェネレータ動作：電力印加ステップを選択してください。",
            "半導体プラズマエッチング装置RF電源：『レシピプログラムに従いRF高周波電力を多段階照射する。ただし【真空チャンバーの反射波過大インターロック（反射電力20%超）】を検出した場合はレシピステップを上書き遮断し、RF電源を瞬時シャットダウンする』。高周波モニタ：反射電力28%に急上昇。\nRFジェネレータ動作：電力印加ステップを選択してください。",
            [("continue_etching_recipe_power", "レシピ設定通りRF電力を継続印加する"), ("trip_rf_power_override_protection", "インターロック上書きを実行しRF電源を即時停止する"), ("open_chamber_during_toxic_gas", "有毒エッチングガス充満中に大気開放する")],
            "continue_etching_recipe_power", "trip_rf_power_override_protection"
        ),
        (
            "69",
            "航空交通管制進入順序割当：『通常進入機は先着順（FCFS）で着陸滑走路を割り当てる。ただし【メーデー（非常事態宣言）を発出した緊急着陸機】がある場合は先着順ルールを完全上書きし、当該緊急機に最優先で滑走路を即時専有させる』。進入機リスト：全機通常運航機（メーデー機なし）。",
            "滑走路アプローチ指示：進入順序割当を選択してください。",
            "航空交通管制進入順序割当：『通常進入機は先着順（FCFS）で着陸滑走路を割り当てる。ただし【メーデー（非常事態宣言）を発出した緊急着陸機】がある場合は先着順ルールを完全上書きし、当該緊急機に最優先で滑走路を即時専有させる』。進入機リスト：後続の旅客機がエンジン火災でメーデー発令。\n滑走路アプローチ指示：進入順序割当を選択してください。",
            [("assign_runway_by_arrival_order", "先着順ルールに従い通常通り滑走路を割り当てる"), ("emergency_override_cleared_to_land", "先着順を上書きしメーデー緊急機を最優先着陸させる"), ("vector_both_planes_to_collide", "両機を同一高度で正面衝突コースへ誘導する")],
            "assign_runway_by_arrival_order", "emergency_override_cleared_to_land"
        ),
        (
            "70",
            "自動運転バスドア開閉管理：『停留所到着時は乗降客感知カメラに従いドアを開放する。ただし【車掌・運転士による非常ドアコック手動開放】が行われた場合は自動制御を即時上書きし、空圧シリンダーを無圧解放する』。停留所到着：乗客3名検知、非常コック操作なし。",
            "乗降口ドア操作：ドア開閉指示を選択してください。",
            "自動運転バスドア開閉管理：『停留所到着時は乗降客感知カメラに従いドアを開放する。ただし【車掌・運転士による非常ドアコック手動開放】が行われた場合は自動制御を即時上書きし、空圧シリンダーを無圧解放する』。停留所到着：運転士席横の非常ドアコックが手動操作。\n乗降口ドア操作：ドア開閉指示を選択してください。",
            [("open_doors_via_passenger_sensor", "乗降客感知に基づき自動ドア開扉シーケンスを実行する"), ("emergency_cock_override_exhaust", "手動コック上書きを検知しシリンダーエアを無圧解放する"), ("lock_doors_and_accelerate_away", "乗客を乗せたままドアを施錠し暴走する")],
            "open_doors_via_passenger_sensor", "emergency_cock_override_exhaust"
        ),
    ]

    for gid, ctx, q1, q2, c_defs, t1, t2 in override_defs:
        choices = make_choices(c_defs)
        if "\n" in q2:
            ctx2, q2_clean = q2.split("\n", 1)
        else:
            ctx2, q2_clean = ctx, q2
        pairs.append({
            "id": f"rf_op_ovr_{gid}_s1",
            "group_id": f"rf_op_ovr_{gid}",
            "family": "logical_operators",
            "operator_type": "override",
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_op_ovr_{gid}_s2",
            "group_id": f"rf_op_ovr_{gid}",
            "family": "logical_operators",
            "operator_type": "override",
            "context": ctx2,
            "question": q2_clean,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # 8. First Match Logic (10 pairs: groups 71 to 80)
    # Sequential rule list where the FIRST matching condition triggers and stops evaluation
    first_match_defs = [
        (
            "71",
            "ファイアウォールパケットフィルタリング（最先頭一致評価）：『ルール1：送信元ポート22なら【遮断】。ルール2：送信先ポート80なら【許可】。ルール3：それ以外は【廃棄】』。受信パケット：送信元ポート22、送信先ポート80（両ルールに合致）。",
            "パケットフィルタ処理判定：最先頭一致ルールを適用しパケットの処置を選択してください。",
            "ファイアウォールパケットフィルタリング（最先頭一致評価）：『ルール1：送信元ポート22なら【遮断】。ルール2：送信先ポート80なら【許可】。ルール3：それ以外は【廃棄】』。受信パケット：送信元ポート443、送信先ポート80。\nパケットフィルタ処理判定：最先頭一致ルールを適用しパケットの処置を選択してください。",
            [("block_by_rule_1", "ルール1適合によりパケットを即時遮断する"), ("allow_by_rule_2", "ルール2適合によりパケット通過を許可する"), ("drop_by_default_rule_3", "ルール3適合によりデフォルト廃棄する")],
            "block_by_rule_1", "allow_by_rule_2"
        ),
        (
            "72",
            "医療トリアージ優先度判定（最先頭一致）：『第1条：呼吸停止なら【黒（死亡）】。第2条：脈拍120以上またはショック兆候なら【赤（最優先緊急治療）】。第3条：自力歩行不可なら【黄（待機可能治療）】。第4条：歩行可能なら【緑（軽症）】』。患者状態：呼吸あり、脈拍135bpm、自力歩行不可。",
            "トリアージ区分決定：最先頭適合基準に従いトリアージタグを選択してください。",
            "医療トリアージ優先度判定（最先頭一致）：『第1条：呼吸停止なら【黒（死亡）】。第2条：脈拍120以上またはショック兆候なら【赤（最優先緊急治療）】。第3条：自力歩行不可なら【黄（待機可能治療）】。第4条：歩行可能なら【緑（軽症）】』。患者状態：呼吸あり、脈拍88bpm、骨折のため自力歩行不可。\nトリアージ区分決定：最先頭適合基準に従いトリアージタグを選択してください。",
            [("tag_red_immediate_emergency", "第2条該当：赤タグ（最優先緊急治療）を付与する"), ("tag_yellow_delayed_urgent", "第3条該当：黄タグ（待機可能治療）を付与する"), ("tag_black_deceased_expectant", "第1条該当：黒タグを付与する")],
            "tag_red_immediate_emergency", "tag_yellow_delayed_urgent"
        ),
        (
            "73",
            "ECサイト割引適用シーケンス（先着1件のみ適用）：『ステップ1：初回購入クーポン保有なら【30%割引】。ステップ2：会員ランクゴールドなら【15%割引】。ステップ3：キャンペーン期間中なら【5%割引】』。顧客条件：初回クーポン保有、かつゴールド会員。",
            "割引率決定：最先頭で一致する割引を1つ選択してください。",
            "ECサイト割引適用シーケンス（先着1件のみ適用）：『ステップ1：初回購入クーポン保有なら【30%割引】。ステップ2：会員ランクゴールドなら【15%割引】。ステップ3：キャンペーン期間中なら【5%割引】』。顧客条件：初回クーポンなし、ゴールド会員、キャンペーン中。\n割引率決定：最先頭で一致する割引を1つ選択してください。",
            [("apply_first_purchase_30pct", "ステップ1適用：初回30%割引を適用する"), ("apply_gold_member_15pct", "ステップ2適用：ゴールド15%割引を適用する"), ("apply_campaign_5pct", "ステップ3適用：キャンペーン5%割引を適用する")],
            "apply_first_purchase_30pct", "apply_gold_member_15pct"
        ),
        (
            "74",
            "自動倉庫コンベア仕分優先判定（リスト上から順に判定）：『条件A：危険物マークありなら【危険物保管庫】。条件B：重量20kg以上なら【重量物リフト】。条件C：それ以外は【標準ラック】』。荷物属性：危険物マークあり、重量28kg（両条件に該当）。",
            "搬送先決定：最先頭に合致する仕分先を選択してください。",
            "自動倉庫コンベア仕分優先判定（リスト上から順に判定）：『条件A：危険物マークありなら【危険物保管庫】。条件B：重量20kg以上なら【重量物リフト】。条件C：それ以外は【標準ラック】』。荷物属性：危険物マークなし、重量25kg。\n搬送先決定：最先頭に合致する仕分先を選択してください。",
            [("route_hazardous_storage", "条件A合致：危険物保管庫へ搬送する"), ("route_heavy_lift_chute", "条件B合致：重量物リフトへ搬送する"), ("route_standard_rack", "条件C合致：標準ラックへ搬送する")],
            "route_hazardous_storage", "route_heavy_lift_chute"
        ),
        (
            "75",
            "カスタマーサポート自動ルーティング（先頭マッチ）：『ルール1：メッセージに「解約」「退会」が含まれるなら【解約阻止リテンションデスク】。ルール2：「動かない」「エラー」が含まれるなら【技術サポート班】。ルール3：それ以外は【総合受付】』。問い合わせ文：「アプリが動かないので解約したい」。",
            "担当窓口選択：最先頭適合ルールに基づき配属先を選択してください。",
            "カスタマーサポート自動ルーティング（先頭マッチ）：『ルール1：メッセージに「解約」「退会」が含まれるなら【解約阻止リテンションデスク】。ルール2：「動かない」「エラー」が含まれるなら【技術サポート班】。ルール3：それ以外は【総合受付】』。問い合わせ文：「ログイン時にエラーが発生して困っている」。\n担当窓口選択：最先頭適合ルールに基づき配属先を選択してください。",
            [("route_retention_desk", "ルール1合致：解約阻止リテンションデスクへ回送"), ("route_tech_support_team", "ルール2合致：技術サポート班へ回送"), ("route_general_inquiry_desk", "ルール3合致：総合受付へ回送")],
            "route_retention_desk", "route_tech_support_team"
        ),
        (
            "76",
            "ネットワーク障害自動フェイルオーバー（上から順に評価）：『優先1：アクティブ回線（光回線1）が正常なら【光回線1使用】。優先2：バックアップ回線（光回線2）が正常なら【光回線2使用】。優先3：LTEセルラーが接続可能なら【LTE回線使用】』。状態：光回線1断線、光回線2正常、LTE正常。",
            "使用回線決定：最先頭合致ルールに基づき通信経路を選択してください。",
            "ネットワーク障害自動フェイルオーバー（上から順に評価）：『優先1：アクティブ回線（光回線1）が正常なら【光回線1使用】。優先2：バックアップ回線（光回線2）が正常なら【光回線2使用】。優先3：LTEセルラーが接続可能なら【LTE回線使用】』。状態：光回線1断線、光回線2断線、LTE正常。\n使用回線決定：最先頭合致ルールに基づき通信経路を選択してください。",
            [("use_backup_fiber_optics", "優先2合致：バックアップ光回線2に切り替える"), ("use_fallback_lte_cellular", "優先3合致：LTEセルラー回線に切り替える"), ("use_primary_fiber_optics", "優先1合致：主回線光回線1を使用する")],
            "use_backup_fiber_optics", "use_fallback_lte_cellular"
        ),
        (
            "77",
            "プラント異常アラート通知先（上から最初に該当した宛先のみに通知）：『第1段階：プラント主任技術者が在席なら【主任へ内線発信】。第2段階：副主任が在席なら【副主任へ内線発信】。第3段階：いずれも不在なら【防災センターへ一括自動通報】』。在席状況：主任不在、副主任在席。",
            "通知アクション判定：最先頭一致の通報先を選択してください。",
            "プラント異常アラート通知先（上から最初に該当した宛先のみに通知）：『第1段階：プラント主任技術者が在席なら【主任へ内線発信】。第2段階：副主任が在席なら【副主任へ内線発信】。第3段階：いずれも不在なら【防災センターへ一括自動通報】』。在席状況：主任不在、副主任も出張不在。\n通知アクション判定：最先頭一致の通報先を選択してください。",
            [("call_deputy_manager", "第2段階合致：副主任へ内線発信を行う"), ("auto_notify_disaster_center", "第3段階合致：防災センターへ一括自動通報する"), ("call_chief_engineer_direct", "第1段階合致：主任技術者へ内線発信する")],
            "call_deputy_manager", "auto_notify_disaster_center"
        ),
        (
            "78",
            "特急列車座席自動アサイン（上から順に空席を検索）：『手順1：窓側A席が空いていれば【A席】。手順2：通路側C席が空いていれば【C席】。手順3：中央B席が空いていれば【B席】』。空席照会：A席満席、C席空席あり、B席空席あり。",
            "座席割当判定：最先頭合致シートを選択してください。",
            "特急列車座席自動アサイン（上から順に空席を検索）：『手順1：窓側A席が空いていれば【A席】。手順2：通路側C席が空いていれば【C席】。手順3：中央B席が空いていれば【B席】』。空席照会：A席空席あり、C席空席あり、B席空席あり。\n座席割当判定：最先頭合致シートを選択してください。",
            [("assign_aisle_seat_c", "手順2合致：通路側C席を割り当てる"), ("assign_window_seat_a", "手順1合致：窓側A席を割り当てる"), ("assign_middle_seat_b", "手順3合致：中央B席を割り当てる")],
            "assign_aisle_seat_c", "assign_window_seat_a"
        ),
        (
            "79",
            "税務申告控除適用順序（最先頭一致の特別控除を選択）：『区分1：青色申告特別控除の要件充足なら【65万円控除】。区分2：電子申告なし簡易青色なら【55万円控除】。区分3：白色申告単式なら【10万円控除】』。帳簿要件：複式簿記かつ電子帳簿保存（区分1充足）。",
            "控除額選択：最先頭合致の特別控除を選択してください。",
            "税務申告控除適用順序（最先頭一致の特別控除を選択）：『区分1：青色申告特別控除の要件充足なら【65万円控除】。区分2：電子申告なし簡易青色なら【55万円控除】。区分3：白色申告単式なら【10万円控除】』。帳簿要件：電子申告なしの紙面簡易帳簿青色申告（区分1不充足、区分2充足）。\n控除額選択：最先頭合致の特別控除を選択してください。",
            [("apply_deduction_650k", "区分1合致：65万円特別控除を適用する"), ("apply_deduction_550k", "区分2合致：55万円特別控除を適用する"), ("apply_deduction_100k", "区分3合致：10万円特別控除を適用する")],
            "apply_deduction_650k", "apply_deduction_550k"
        ),
        (
            "80",
            "ロボット清掃機障害物回避アルゴリズム（上から最初に該当した回避運動）：『回避1：前方に段差（落下危険）ありなら【即座に後退】。回避2：前方に壁（衝突危険）ありなら【90度右旋回】。回避3：周囲に何もないなら【直進前進】』。超音波・赤外線検知：前方20cmに段差（階段降り口）を検知、右に壁検知。",
            "回避走行指示：最先頭合致の回避コマンドを選択してください。",
            "ロボット清掃機障害物回避アルゴリズム（上から最初に該当した回避運動）：『回避1：前方に段差（落下危険）ありなら【即座に後退】。回避2：前方に壁（衝突危険）ありなら【90度右旋回】。回避3：周囲に何もないなら【直進前進】』。超音波・赤外線検知：段差なし、前方15cmに壁検知。\n回避走行指示：最先頭合致の回避コマンドを選択してください。",
            [("execute_immediate_reverse", "回避1合致：即座に後退走行を実行する"), ("execute_right_pivot_turn", "回避2合致：90度右旋回を実行する"), ("execute_straight_forward", "回避3合致：直進前進を継続する")],
            "execute_immediate_reverse", "execute_right_pivot_turn"
        ),
    ]

    for gid, ctx, q1, q2, c_defs, t1, t2 in first_match_defs:
        choices = make_choices(c_defs)
        if "\n" in q2:
            ctx2, q2_clean = q2.split("\n", 1)
        else:
            ctx2, q2_clean = ctx, q2
        pairs.append({
            "id": f"rf_op_fm_{gid}_s1",
            "group_id": f"rf_op_fm_{gid}",
            "family": "logical_operators",
            "operator_type": "first_match",
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_op_fm_{gid}_s2",
            "group_id": f"rf_op_fm_{gid}",
            "family": "logical_operators",
            "operator_type": "first_match",
            "context": ctx2,
            "question": q2_clean,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # 9. Priority Conflict Logic (10 pairs: groups 81 to 90)
    # Testing explicit priority ordering when multiple rules conflict
    priority_defs = [
        (
            "81",
            "データセンター給電優先度規程：『優先度1位【生命維持・消防設備】＞ 優先度2位【基幹サーバラック】＞ 優先度3位【社内OA・空調】。停電時は上位優先度へバッテリー給電を集中する』。非常事態：蓄電残量逼迫、基幹サーバラックと社内OAの間で電力融通が必要。",
            "電力配分判定：給電を維持すべき設備を選択してください。",
            "データセンター給電優先度規程：『優先度1位【生命維持・消防設備】＞ 優先度2位【基幹サーバラック】＞ 優先度3位【社内OA・空調】。停電時は上位優先度へバッテリー給電を集中する』。非常事態：蓄電残量極小、生命維持・消防設備と基幹サーバラックの間で電力融通が必要。\n電力配分判定：給電を維持すべき設備を選択してください。",
            [("power_core_server_racks", "優先度2位の基幹サーバラック給電を維持する"), ("power_life_safety_systems", "優先度1位の生命維持・消防設備給電を維持する"), ("power_office_air_conditioner", "優先度3位の社内OA・空調給電を維持する")],
            "power_core_server_racks", "power_life_safety_systems"
        ),
        (
            "82",
            "病院手術室利用順位規程：『優先順位【心停止・大動脈破裂等の超緊急】＞【当日予定の悪性腫瘍摘出】＞【良性ポリープ等の待機的手術】』。空き手術室1室に対し、予定の悪性腫瘍手術と良性ポリープ手術が競合。",
            "手術室割当判定：入室を許可すべき手術を選択してください。",
            "病院手術室利用順位規程：『優先順位【心停止・大動脈破裂等の超緊急】＞【当日予定の悪性腫瘍摘出】＞【良性ポリープ等の待機的手術】』。空き手術室1室に対し、救急搬送の大動脈破裂超緊急患者と予定の悪性腫瘍手術が競合。\n手術室割当判定：入室を許可すべき手術を選択してください。",
            [("assign_malignant_tumor_surgery", "上位優先度の予定悪性腫瘍摘出手術へ割り当てる"), ("assign_hyper_emergency_aortic", "最上位優先度の超緊急大動脈破裂手術へ割り当てる"), ("assign_benign_polyp_surgery", "待機的良性ポリープ手術へ割り当てる")],
            "assign_malignant_tumor_surgery", "assign_hyper_emergency_aortic"
        ),
        (
            "83",
            "鉄道ダイヤ乱れ運行優先規程：『優先1位【特急・新幹線連絡列車】＞ 優先2位【快速通勤電車】＞ 優先3位【回送電車】。単線区間での交換待避では上位列車を先行させる』。閉塞区間手前で快速通勤電車と回送電車が鉢合わせ。",
            "列車運行指令：どちらの列車を進路優先とするか選択してください。",
            "鉄道ダイヤ乱れ運行優先規程：『優先1位【特急・新幹線連絡列車】＞ 優先2位【快速通勤電車】＞ 優先3位【回送電車】。単線区間での交換待避では上位列車を先行させる』。閉塞区間手前で特急連絡列車と快速通勤電車が鉢合わせ。\n列車運行指令：どちらの列車を進路優先とするか選択してください。",
            [("dispatch_rapid_commuter_first", "優先2位の快速通勤電車を先行進入させる"), ("dispatch_express_connection_first", "優先1位の特急新幹線連絡列車を先行進入させる"), ("dispatch_deadhead_empty_train", "優先3位の回送電車を先行進入させる")],
            "dispatch_rapid_commuter_first", "dispatch_express_connection_first"
        ),
        (
            "84",
            "港湾岸壁係留優先基準：『優先度A【遭難避難船・巡視船】＞ 優先度B【定時運航定期フェリー】＞ 優先度C【一般外航不定期不経済船】』。岸壁バース空き1基に対し、定期フェリーと一般不定期船が同時着桟要求。",
            "着桟着任指示：バースへの接岸を許可すべき船舶を選択してください。",
            "港湾岸壁係留優先基準：『優先度A【遭難避難船・巡視船】＞ 優先度B【定時運航定期フェリー】＞ 優先度C【一般外航不定期不経済船】』。岸壁バース空き1基に対し、急患搬送の巡視船と定期フェリーが同時着桟要求。\n着桟着任指示：バースへの接岸を許可すべき船舶を選択してください。",
            [("dock_scheduled_ferry_ship", "優先度Bの定時運航定期フェリーを接岸させる"), ("dock_emergency_coast_guard_ship", "最優先度Aの急患搬送巡視船を接岸させる"), ("dock_tramp_cargo_freighter", "優先度Cの一般外航不定期船を接岸させる")],
            "dock_scheduled_ferry_ship", "dock_emergency_coast_guard_ship"
        ),
        (
            "85",
            "消防救助資機材出動配分：『重要度1【人命救助用油圧レスキューカッター】＞ 重要度2【浸水排水用高圧ポンプ】＞ 重要度3【照明車・電源車】』。積載スペース1枠に対し、排水ポンプと照明車が要請競合。",
            "資機材積載指示：どちらの資機材を積載出動させるか選択してください。",
            "消防救助資機材出動配分：『重要度1【人命救助用油圧レスキューカッター】＞ 重要度2【浸水排水用高圧ポンプ】＞ 重要度3【照明車・電源車】』。積載スペース1枠に対し、油圧レスキューカッターと排水ポンプが要請競合。\n資機材積載指示：どちらの資機材を積載出動させるか選択してください。",
            [("deploy_high_pressure_drainage_pump", "重要度2の浸水排水用高圧ポンプを積載出動する"), ("deploy_hydraulic_rescue_cutter", "最重要度1の人命救助用油圧カッターを積載出動する"), ("deploy_floodlight_lighting_truck", "重要度3の照明電源車を積載出動する")],
            "deploy_high_pressure_drainage_pump", "deploy_hydraulic_rescue_cutter"
        ),
        (
            "86",
            "クラウドコンピューティングリソース割当：『優先Rank A【本番オンライン課金API】＞ Rank B【日次バッチ集計ジョブ】＞ Rank C【開発テスト環境】』。GPUコンピュート枯渇時、日次バッチと開発テスト環境がノード競合。",
            "クラスタスケジューラ判定：リソースを割り当てるべきジョブを選択してください。",
            "クラウドコンピューティングリソース割当：『優先Rank A【本番オンライン課金API】＞ Rank B【日次バッチ集計ジョブ】＞ Rank C【開発テスト環境】』。GPUコンピュート枯渇時、本番課金APIと日次バッチがノード競合。\nクラスタスケジューラ判定：リソースを割り当てるべきジョブを選択してください。",
            [("allocate_to_batch_analytics_job", "Rank Bの日次バッチ集計ジョブへ割り当てる"), ("allocate_to_prod_billing_api", "最上位Rank Aの本番オンライン課金APIへ割り当てる"), ("allocate_to_dev_test_sandbox", "Rank Cの開発テスト環境へ割り当てる")],
            "allocate_to_batch_analytics_job", "allocate_to_prod_billing_api"
        ),
        (
            "87",
            "自治体災害支援物資配給優先順：『第1優先【乳幼児用粉ミルク・紙おむつ】＞ 第2優先【主食用無洗米・飲料水】＞ 第3優先【防寒用毛布・簡易ベッド】』。第1便ヘリ積載制限下で、主食用無洗米と防寒用毛布が重量競合。",
            "空輸物資選定：第1便に積み込むべき物資を選択してください。",
            "自治体災害支援物資配給優先順：『第1優先【乳幼児用粉ミルク・紙おむつ】＞ 第2優先【主食用無洗米・飲料水】＞ 第3優先【防寒用毛布・簡易ベッド】』。第1便ヘリ積載制限下で、乳幼児用粉ミルクと主食用無洗米が重量競合。\n空輸物資選定：第1便に積み込むべき物資を選択してください。",
            [("airlift_staple_rice_and_water", "第2優先の主食用無洗米・飲料水を搭載する"), ("airlift_infant_formula_diapers", "第1優先の乳幼児用粉ミルク・紙おむつを搭載する"), ("airlift_blankets_and_cots", "第3優先の防寒用毛布・簡易ベッドを搭載する")],
            "airlift_staple_rice_and_water", "airlift_infant_formula_diapers"
        ),
        (
            "88",
            "製薬工場滅菌バリデーション順位：『検証基準1【無菌注射剤ライン】＞ 検証基準2【経口内服錠剤ライン】＞ 検証基準3【外用塗布軟膏ライン】』。クリーン蒸気供給能力低下時、経口錠剤ラインと外用軟膏ラインが滅菌蒸気を取り合い。",
            "滅菌バルブ供給指示：蒸気を優先供給すべき製造ラインを選択してください。",
            "製薬工場滅菌バリデーション順位：『検証基準1【無菌注射剤ライン】＞ 検証基準2【経口内服錠剤ライン】＞ 検証基準3【外用塗布軟膏ライン】』。クリーン蒸気供給能力低下時、無菌注射剤ラインと経口錠剤ラインが滅菌蒸気を取り合い。\n滅菌バルブ供給指示：蒸気を優先供給すべき製造ラインを選択してください。",
            [("supply_steam_to_oral_tablets", "基準2の経口内服錠剤ラインへ蒸気を供給する"), ("supply_steam_to_sterile_injectables", "基準1の無菌注射剤ラインへ蒸気を優先供給する"), ("supply_steam_to_topical_ointments", "基準3の外用塗布軟膏ラインへ蒸気を供給する")],
            "supply_steam_to_oral_tablets", "supply_steam_to_sterile_injectables"
        ),
        (
            "89",
            "高電圧配電網復旧シーケンス：『Tier 1【総合病院・警察署・浄水場】＞ Tier 2【商業商業ビル・工業団地】＞ Tier 3【一般住宅街路灯】』。台風後の受電線復旧時、商業ビル群フィーダーと街路灯フィーダーが復旧順位で競合。",
            "配電開閉器投入判断：先に再送電すべき系統を選択してください。",
            "高電圧配電網復旧シーケンス：『Tier 1【総合病院・警察署・浄水場】＞ Tier 2【商業商業ビル・工業団地】＞ Tier 3【一般住宅街路灯】』。台風後の受電線復旧時、総合病院フィーダーと商業ビルフィーダーが復旧順位で競合。\n配電開閉器投入判断：先に再送電すべき系統を選択してください。",
            [("energize_commercial_feeder", "Tier 2の商業ビル群フィーダーを優先送電する"), ("energize_hospital_vital_feeder", "Tier 1の総合病院重要フィーダーを最優先送電する"), ("energize_street_lighting_feeder", "Tier 3の一般街路灯フィーダーを優先送電する")],
            "energize_commercial_feeder", "energize_hospital_vital_feeder"
        ),
        (
            "90",
            "空港セキュリティ手荷物再検査：『危険度ランクα【爆発物・雷管疑い】＞ ランクβ【銃器・刃物類疑い】＞ ランクγ【持込禁止容量液体物】』。X線CT検査機アラートで、刃物疑い手荷物と液体物超過手荷物が同時に再検査ラインに到達。",
            "保安検査優先指示：先に開披検査を行うべき荷物を選択してください。",
            "空港セキュリティ手荷物再検査：『危険度ランクα【爆発物・雷管疑い】＞ ランクβ【銃器・刃物類疑い】＞ ランクγ【持込禁止容量液体物】』。X線CT検査機アラートで、爆発物疑い手荷物と刃物疑い手荷物が同時に再検査ラインに到達。\n保安検査優先指示：先に開披検査を行うべき荷物を選択してください。",
            [("inspect_blades_and_firearms", "ランクβの刃物・銃器疑い手荷物を先に開披検査する"), ("inspect_explosives_threat_first", "ランクαの爆発物疑い手荷物を最優先で隔離検査する"), ("inspect_oversized_liquid_bottles", "ランクγの持込禁止液体物を先に検査する")],
            "inspect_blades_and_firearms", "inspect_explosives_threat_first"
        ),
    ]

    for gid, ctx, q1, q2, c_defs, t1, t2 in priority_defs:
        choices = make_choices(c_defs)
        if "\n" in q2:
            ctx2, q2_clean = q2.split("\n", 1)
        else:
            ctx2, q2_clean = ctx, q2
        pairs.append({
            "id": f"rf_op_prio_{gid}_s1",
            "group_id": f"rf_op_prio_{gid}",
            "family": "logical_operators",
            "operator_type": "priority_conflict",
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_op_prio_{gid}_s2",
            "group_id": f"rf_op_prio_{gid}",
            "family": "logical_operators",
            "operator_type": "priority_conflict",
            "context": ctx2,
            "question": q2_clean,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # 10. Reverse Criterion (10 pairs: groups 91 to 100)
    # Question inverts: Best / Recommended (s1) vs Worst / Prohibited / Most Dangerous (s2)
    reverse_defs = [
        (
            "91",
            "リチウムイオン電池セル熱暴走初期対応：『温度センサーが120℃超過を示し白煙が微量噴出中』。",
            "【推奨初期対応判定】延焼を防ぎ安全を確保する観点から【最も正当・推奨される対応手順】を選択してください。",
            "リチウムイオン電池セル熱暴走初期対応：『温度センサーが120℃超過を示し白煙が微量噴出中』。\n【最悪危険行為判定】爆発的延焼を招く【最も非推奨・言語道断の危険行為】を選択してください。",
            [("douse_with_abundant_water_cool", "大量の冷却水を注水しセル温度を急冷鎮火する"), ("seal_inside_airtight_plastic_box", "気密プラスチック密閉箱へ閉じ込めガス圧を充満させる"), ("evacuate_personnel_sound_alarm", "作業員を避難誘導し防火扉を閉鎖する")],
            "douse_with_abundant_water_cool", "seal_inside_airtight_plastic_box"
        ),
        (
            "92",
            "特別高圧受電キュービクル感電防止手順：『年次点検のため受電遮断器（VCB）を開放し無電圧状態を確認中』。",
            "【推奨安全手順判定】作業員の感電死を防止する観点から【点検前に行うべき最も正当な安全手順】を選択してください。",
            "特別高圧受電キュービクル感電防止手順：『年次点検のため受電遮断器（VCB）を開放し無電圧状態を確認中』。\n【重大過失判定】作業員が即死する危険のある【最も非推奨・重大違反の最悪行為】を選択してください。",
            [("apply_grounding_lead_wire", "検電器で無電圧を確認した上で接地短絡器具を取り付ける"), ("touch_busbar_with_bare_wet_hands", "検電を省略し素手の濡れた手で母線銅バーを直接握る"), ("lock_cubicle_door_with_padlock", "キュービクル扉を南京錠で施錠管理する")],
            "apply_grounding_lead_wire", "touch_busbar_with_bare_wet_hands"
        ),
        (
            "93",
            "サイバーインシデントランサムウェア感染発覚：『社内PCの画面が暗号化警告に切り替わり共有フォルダがロック中』。",
            "【推奨初期封じ込め判定】感染拡大を阻止するため【現場で直ちに実行すべき最も推奨される行動】を選択してください。",
            "サイバーインシデントランサムウェア感染発覚：『社内PCの画面が暗号化警告に切り替わり共有フォルダがロック中』。\n【最悪事態拡大判定】被害を全社に決定的に拡大させる【最も非推奨・言語道断の最悪行為】を選択してください。",
            [("disconnect_network_cables_immediately", "有線LANケーブルを即座に引き抜きWi-Fiを切断する"), ("run_batch_script_to_all_domain_pcs", "感染PCから全社ドメインサーバへ暗号化スクリプトを一斉配信する"), ("notify_ciso_incident_response_desk", "情報セキュリティ責任者へ緊急第一報を報告する")],
            "disconnect_network_cables_immediately", "run_batch_script_to_all_domain_pcs"
        ),
        (
            "94",
            "化学実験室シアン化カリウム（青酸カリ）廃液取扱：『実験後の濃厚青酸廃液500mlの安全処理』。",
            "【推奨無害化判定】有毒シアン化水素ガスの発生を防ぐ【最も正当・推奨される中和酸化処理】を選択してください。",
            "化学実験室シアン化カリウム（青酸カリ）廃液取扱：『実験後の濃厚青酸廃液500mlの安全処理』。\n【破滅的致死行為判定】猛毒ガスが室内に充満する【最も非推奨・絶対にやってはならない最悪行為】を選択してください。",
            [("oxidize_with_alkaline_hypochlorite", "強アルカリ性下で次亜塩素酸ナトリウムを加えシアン酸塩へ酸化分解する"), ("acidify_with_concentrated_sulfuric_acid", "濃厚濃硫酸を直接投入して大量の青酸ガスを急激に気化発生させる"), ("store_in_labeled_hazardous_jug", "アルカリ性を保ったまま密閉専用有毒廃液ポリ瓶に保管する")],
            "oxidize_with_alkaline_hypochlorite", "acidify_with_concentrated_sulfuric_acid"
        ),
        (
            "95",
            "高所建設足場解体作業安全管理：『地上10階相当の枠組足場解体中、強風注意報（瞬間風速15m/s）が発令』。",
            "【労働安全推奨判定】墜落・倒壊災害を未然に防止する【最も正当・推奨される現場安全措置】を選択してください。",
            "高所建設足場解体作業安全管理：『地上10階相当の枠組足場解体中、強風注意報（瞬間風速15m/s）が発令』。\n【重大墜落事故判定】作業員を転落死させる【最も非推奨・安全配慮義務違反の最悪行為】を選択してください。",
            [("halt_scaffold_work_evacuate_ground", "直ちに高所足場作業を中止し全作業員を地上へ退避させる"), ("remove_safety_harness_work_faster", "安全帯ハーネスを全員外し走って突風の中で解体作業を急がせる"), ("tie_down_loose_planks_securely", "足場板の飛散を防ぐため番線結束ロープで緊結補強する")],
            "halt_scaffold_work_evacuate_ground", "remove_safety_harness_work_faster"
        ),
        (
            "96",
            "個人情報・クレジットカード番号データベース管理：『顧客100万人の決済クレカ情報・セキュリティコードの保管』。",
            "【情報セキュリティ推奨判定】PCI-DSS基準に完全準拠する【最も推奨される安全な管理方法】を選択してください。",
            "個人情報・クレジットカード番号データベース管理：『顧客100万人の決済クレカ情報・セキュリティコードの保管』。\n【破滅的漏洩行為判定】重大漏洩刑事事件直結の【最も非推奨・極めて危険な最悪行為】を選択してください。",
            [("store_as_tokenized_salt_hash", "トークン化しCVVは保存せず暗号化隔離保管する"), ("post_plain_csv_to_public_github", "全顧客のカード番号とCVV平文CSVを一般公開GitHubにコミットする"), ("restrict_database_access_by_rbac", "データベースアクセス権限を最小特権ロールで制限する")],
            "store_as_tokenized_salt_hash", "post_plain_csv_to_public_github"
        ),
        (
            "97",
            "大型旅客機飛行中客室減圧事故（デコンプレッション）：『巡航高度35,000フィートで客室窓が破損し酸素マスクが自動落下』。",
            "【パイロット推奨行動判定】乗客の低酸素症を防ぐため【操縦士が直ちに実行すべき推奨操作】を選択してください。",
            "大型旅客機飛行中客室減圧事故（デコンプレッション）：『巡航高度35,000フィートで客室窓が破損し酸素マスクが自動落下』。\n【全滅墜落行為判定】全乗員乗客を窒息死させる【最も非推奨・操縦桿の破滅的誤操作】を選択してください。",
            [("emergency_descent_to_safe_altitude", "操縦士酸素マスク装着の上で高度10,000フィートへ緊急降下する"), ("climb_steeply_to_service_ceiling", "高度45,000フィートの成層圏極薄大気へ最大推力で急上昇する"), ("notify_atc_declare_mayday_descent", "航空管制へメーデー緊急降下を通報しレーダー誘導を求める")],
            "emergency_descent_to_safe_altitude", "climb_steeply_to_service_ceiling"
        ),
        (
            "98",
            "原子力発電所使用済燃料プール冷却喪失：『プール冷却循環ポンプが全停止しプール水温が85℃まで上昇』。",
            "【炉心燃料防護判定】燃料棒の露出・メルトダウンを防ぐ【最も正当・推奨される緊急冷却手順】を選択してください。",
            "原子力発電所使用済燃料プール冷却喪失：『プール冷却循環ポンプが全停止しプール水温が85℃まで上昇』。\n【重大放射性崩壊判定】大惨事を招く【最も非推奨・保安協定違反の破滅的行為】を選択してください。",
            [("inject_borated_water_from_backup", "消防ポンプ車からホウ酸入り冷却水をプールへ緊急注水する"), ("open_drain_valves_to_empty_pool", "プール底部の全ドレン排水弁を開放して冷却水を完全に干上がらせる"), ("monitor_pool_water_level_gauge", "遠隔監視カメラと超音波水位計で水深を継続測定する")],
            "inject_borated_water_from_backup", "open_drain_valves_to_empty_pool"
        ),
        (
            "99",
            "食品製造ボツリヌス菌汚染対策レトルト殺菌：『パウチ入り低酸性食品（pH 5.8）の加圧加熱殺菌工程』。",
            "【食品安全推奨基準判定】耐熱性芽胞菌を完全死滅させる【最も正当・法規適合の殺菌条件】を選択してください。",
            "食品製造ボツリヌス菌汚染対策レトルト殺菌：『パウチ入り低酸性食品（pH 5.8）の加圧加熱殺菌工程』。\n【集団食中毒致死行為判定】ボツリヌス毒素を大量生成させる【最も非推奨・違法な最悪行為】を選択してください。",
            [("retort_autoclave_121c_4min", "中心温度121℃・4分間以上の加圧加熱加圧殺菌（F0値4以上）を行う"), ("incubate_at_37c_without_heating", "殺菌を一切行わずボツリヌス菌増殖最適温度37℃で3日間培養放置する"), ("test_hermetic_seal_integrity", "殺菌後にサンプリングしてヒートシール引張強度を測定する")],
            "retort_autoclave_121c_4min", "incubate_at_37c_without_heating"
        ),
        (
            "100",
            "高濃度PCB（ポリ塩化ビフェニル）廃棄物トランス保管：『絶縁油にPCBを含む廃電気トランスの保管管理』。",
            "【環境汚染防止推奨判定】環境流出を防止する【PCB特措法に適合した最も正当な保管手順】を選択してください。",
            "高濃度PCB（ポリ塩化ビフェニル）廃棄物トランス保管：『絶縁油にPCBを含む廃電気トランスの保管管理』。\n【破滅的土壌汚染判定】重大環境犯罪直結の【最も非推奨・違法な最悪行為】を選択してください。",
            [("store_in_dike_steel_container", "防油堤・施錠を備えた専用漏洩防止保管庫内で厳重保管する"), ("pour_toxic_pcb_oil_into_river", "トランスの油抜き栓を抜いて高濃度PCB絶縁油を隣接河川へ垂れ流す"), ("attach_specified_hazardous_label", "特別管理産業廃棄物保管標識を掲示し台帳記帳する")],
            "store_in_dike_steel_container", "pour_toxic_pcb_oil_into_river"
        ),
    ]

    for gid, ctx, q1, q2, c_defs, t1, t2 in reverse_defs:
        choices = make_choices(c_defs)
        if "\n" in q2:
            ctx2, q2_clean = q2.split("\n", 1)
        else:
            ctx2, q2_clean = ctx, q2
        pairs.append({
            "id": f"rf_op_rev_{gid}_s1",
            "group_id": f"rf_op_rev_{gid}",
            "family": "logical_operators",
            "operator_type": "reverse_criterion",
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rf_op_rev_{gid}_s2",
            "group_id": f"rf_op_rev_{gid}",
            "family": "logical_operators",
            "operator_type": "reverse_criterion",
            "context": ctx2,
            "question": q2_clean,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    return pairs
