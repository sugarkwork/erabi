"""Family 1: core_rules (30 pairs, 60 cases) - Blind v4
Distribution: K=3 (5 pairs), K=4 (15 pairs), K=6 (5 pairs), K=8 (5 pairs)
Prefix: rc2b4_core_
Zero inference during authoring; 100% fresh scenarios.
"""

from typing import Any, Dict, List, Tuple


def make_choices(c_defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in c_defs]


def get_core_rules_pairs() -> List[Dict[str, Any]]:
    pairs = []

    # --- K=3 (5 pairs: groups 01 to 05) ---
    k3_defs = [
        (
            "01",
            "医療用オートクレーブ（高圧蒸気滅菌器）の工程判定。規定滅菌条件は『槽内温度121℃以上かつ滅菌保持時間20分以上』である。",
            "滅菌記録：槽内温度は122℃に到達し、保持時間は22分を経過した。基準に適合しているか判定せよ。",
            "滅菌記録：槽内温度は116℃にとどまり、保持時間は14分で中断された。基準に適合しているか判定せよ。",
            [
                ("sterilization_complete", "滅菌工程完了承認"),
                ("sterilization_incomplete", "滅菌未達・再滅菌要求"),
                ("equipment_calibration_hold", "機器校正保留")
            ],
            "sterilization_complete", "sterilization_incomplete"
        ),
        (
            "02",
            "医薬品製剤クリーンルーム（クラス1000）の室間差圧管理。規定基準は『隣接室との差圧15Pa以上維持』である。",
            "差圧計モニタ：現在差圧は18.5Paで安定推移している。クリーンルーム運用判定を行え。",
            "差圧計モニタ：現在差圧は7.2Paへ急激に低下した。クリーンルーム運用判定を行え。",
            [
                ("room_pressure_normal", "差圧正常・入室許可"),
                ("room_pressure_alarm", "差圧低下警報・入室禁止"),
                ("filter_standby_mode", "予備換気待機")
            ],
            "room_pressure_normal", "room_pressure_alarm"
        ),
        (
            "03",
            "半導体ステッパー露光装置の焦点位置校正ルール。基準は『焦点オフセット誤差が±0.05μm以内なら露光継続、超過なら補正停止』である。",
            "リアルタイム計測：焦点オフセット誤差は+0.02μmである。装置制御の判断を行え。",
            "リアルタイム計測：焦点オフセット誤差は+0.18μmである。装置制御の判断を行え。",
            [
                ("exposure_proceed", "露光シーケンス継続"),
                ("exposure_halt_calibrate", "露光一時停止・自動焦点校正"),
                ("wafer_cassette_reject", "ロット全体廃棄")
            ],
            "exposure_proceed", "exposure_halt_calibrate"
        ),
        (
            "04",
            "自動運転無人フォークリフトの衝突防止ルール。基準は『進行方向2.0m以内に障害物検知時は即時停止、2.0m超なら通常走行』である。",
            "LiDARセンシング：直進レーン前方5.2mに障害物なし、検知領域はクリアである。走行制御を決定せよ。",
            "LiDARセンシング：直進レーン前方1.1mに作業パレットが突発検知された。走行制御を決定せよ。",
            [
                ("agv_cruise_normal", "規定速度巡航走行"),
                ("agv_emergency_stop", "非常停止ブレーキ作動"),
                ("agv_manual_override", "手動誘導切替")
            ],
            "agv_cruise_normal", "agv_emergency_stop"
        ),
        (
            "05",
            "食品冷凍工場の急速凍結ライン品質基準。基準は『パレット中心温度が-18℃以下で出荷保管可、-18℃超は追加冷凍』である。",
            "芯温プローブ測定結果：ロットAの中心温度は-21.5℃である。工程処置を選択せよ。",
            "芯温プローブ測定結果：ロットBの中心温度は-11.0℃である。工程処置を選択せよ。",
            [
                ("frozen_pass_storage", "冷凍合格・自動倉庫入庫"),
                ("frozen_re_chill", "追加急速凍結ライン回送"),
                ("batch_scrap_disposal", "品質異常廃棄処分")
            ],
            "frozen_pass_storage", "frozen_re_chill"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k3_defs:
        pairs.append({
            "id": f"rc2b4_core_{gid}_s1", "group_id": f"rc2b4_core_{gid}", "family": "core_rules",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_core_{gid}_s2", "group_id": f"rc2b4_core_{gid}", "family": "core_rules",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=4 (15 pairs: groups 06 to 20) ---
    k4_defs = [
        (
            "06",
            "クラウドクラスターのオートスケーリング運用ルール。基準は『5分平均CPU使用率が80%以上ならスケールアウト（増台）、30%未満ならスケールイン（縮小）、それ以外は維持』である。",
            "直近5分間のCPU使用率メトリクスは平均88%を記録した。スケーリング動作を判定せよ。",
            "直近5分間のCPU使用率メトリクスは平均19%を記録した。スケーリング動作を判定せよ。",
            [
                ("scale_out_node", "ワーカーノード即時追加増台"),
                ("scale_in_node", "アイドルノード安全縮小停止"),
                ("scale_maintain", "現行インスタンス数維持"),
                ("reboot_cluster_manager", "クラスタ管理ノード再起動")
            ],
            "scale_out_node", "scale_in_node"
        ),
        (
            "07",
            "上水道浄水場の薬品沈殿池における凝集剤（PAC）注入制御規定。原水濁度が『20度以上なら注入量増量、5度未満なら注入量減量、5〜20度は標準維持』とする。",
            "計測濁度：豪雨の影響により原水濁度が38度に急上昇した。PAC注入制御を選択せよ。",
            "計測濁度：水源安定により原水濁度は2.8度に清澄化した。PAC注入制御を選択せよ。",
            [
                ("flocculant_boost", "凝集剤PAC注入量20%増量"),
                ("flocculant_reduce", "凝集剤PAC注入量15%減量"),
                ("flocculant_keep", "凝集剤PAC基準量維持"),
                ("chlorine_shock_dose", "緊急次亜塩素酸過剰注入")
            ],
            "flocculant_boost", "flocculant_reduce"
        ),
        (
            "08",
            "空港国際線自動搭乗ゲートの搭乗可否チェックルール。『指定搭乗グループ一致かつパスポート照合有効ならゲート開放、無効またはグループ違いならゲート阻止』とする。",
            "旅客データ照合：現在呼び出し中のグループ2と一致し、パスポート認証ステータスは有効である。ゲート処置を決定せよ。",
            "旅客データ照合：現在呼び出し中のグループ2に対し、旅客券面はグループ5であり、認証エラーが返答された。ゲート処置を決定せよ。",
            [
                ("gate_open_pass", "搭乗ゲート自動開放・通過許可"),
                ("gate_deny_intercept", "ゲート閉止保持・地上係員呼出"),
                ("gate_maintenance_lock", "保守用機器ロック"),
                ("baggage_reclaim_alert", "手荷物返還通知")
            ],
            "gate_open_pass", "gate_deny_intercept"
        ),
        (
            "09",
            "救命救急ICU生体モニタのアラート出力規則。『経皮的動脈血酸素飽和度（SpO2）が90%未満なら高優先度警報発報、95%以上なら正常維持』である。",
            "ベッドサイド患者生体数値：SpO2は98%で心拍・血圧ともに安定している。モニタ制御を決定せよ。",
            "ベッドサイド患者生体数値：SpO2が84%へ急激に低下した。モニタ制御を決定せよ。",
            [
                ("monitor_stable_display", "正常波形表示維持"),
                ("monitor_high_urgency_alarm", "緊急高優先度アラーム発報"),
                ("monitor_battery_eco_mode", "省電力バッテリモード切替"),
                ("sensor_probe_disconnect", "プローブ断線表示")
            ],
            "monitor_stable_display", "monitor_high_urgency_alarm"
        ),
        (
            "10",
            "洋上風力発電タービンの保護制御規定。風速計の計測値が『瞬間風速25m/s以上なら非常フェザリング停止、12m/s以下なら定格発電継続』とする。",
            "洋上風況データ：現在平均風速8.5m/s、突風成分なし。タービン運転制御を決定せよ。",
            "洋上風況データ：急発達した低気圧により瞬間風速27.8m/sを検知した。タービン運転制御を決定せよ。",
            [
                ("wind_power_generate", "通常系統連系発電運転"),
                ("wind_feathering_stop", "ブレード全開フェザリング停止"),
                ("wind_yaw_manual_rotate", "ナセル手動旋回待機"),
                ("wind_grid_island_mode", "自立単独運転移行")
            ],
            "wind_power_generate", "wind_feathering_stop"
        ),
        (
            "11",
            "鉄道踏切保安装置の自動降下制御規定。『列車接近検知接点オンで警報開始・遮断桿降下、通過検知接点成立で警報停止・遮断桿上昇』とする。",
            "軌道回路信号：上り接近リレーが扛上（検知オン）した。踏切制御盤の動作を選択せよ。",
            "軌道回路信号：列車末尾が通過リレーを完全踏越（通過完了オン）した。踏切制御盤の動作を選択せよ。",
            [
                ("crossing_activate_down", "警報音吹鳴・遮断桿降下作動"),
                ("crossing_deactivate_up", "警報吹鳴停止・遮断桿全開上昇"),
                ("crossing_fault_flash", "保安装置故障表示点滅"),
                ("crossing_speed_restrict", "列車速度制限信号送信")
            ],
            "crossing_activate_down", "crossing_deactivate_up"
        ),
        (
            "12",
            "精密CNCマシニングセンタの主軸切削油（クーラント）循環保護基準。『液面下限フロート作動時は加工サイクル即時停止、液面満杯・適正時はサイクル継続』である。",
            "クーラントタンク液面センサ：液面レベルは80%を示しフロート正常である。加工運転判定を行え。",
            "クーラントタンク液面センサ：液面が下限基準値を割り込み、低液面フロート接点がオンになった。加工運転判定を行え。",
            [
                ("machining_cycle_run", "NCプログラム加工サイクル続行"),
                ("machining_halt_coolant_error", "主軸停止・切削液枯渇エラー報知"),
                ("spindle_warmup_idle", "主軸低速暖機アイドル"),
                ("tool_changer_forced_reset", "工具マガジン強制原点復帰")
            ],
            "machining_cycle_run", "machining_halt_coolant_error"
        ),
        (
            "13",
            "産業用太陽光発電パワーコンディショナ（PCS）の系統連系連動基準。『系統周波数49.5Hz〜50.5Hzなら連系維持、48.5Hz以下または51.5Hz超過なら解列分離』とする。",
            "電力品質アナライザ測定値：系統周波数は50.02Hzで安定している。PCS動作を選択せよ。",
            "電力品質アナライザ測定値：系統周波数は48.15Hzへ低下し異常離脱傾向を示している。PCS動作を選択せよ。",
            [
                ("grid_connection_keep", "系統連系インバータ給電維持"),
                ("grid_trip_disconnect", "系統解列保護遮断器トリップ"),
                ("power_factor_lead_bias", "進み力率強制制御"),
                ("dc_ground_fault_alarm", "直流地絡故障通知")
            ],
            "grid_connection_keep", "grid_trip_disconnect"
        ),
        (
            "14",
            "電算データセンター空調水配管チラー装置の切り替え手順。『主機チラー1号が故障異常警報を発した場合は直ちに待機系チラー2号を起動、1号正常時は2号停止維持』とする。",
            "空調監視システム：1号機は異常信号なし、冷水出口温度7.0℃で正常稼働中である。チラー2号機の状態を決めよ。",
            "空調監視システム：1号機で圧縮機オーバーロード異常警報が発生し自動トリップした。チラー2号機の状態を決めよ。",
            [
                ("standby_chiller_stay_off", "待機系チラー2号機停止維持"),
                ("standby_chiller_startup", "待機系チラー2号機自動始動切替"),
                ("cooling_tower_drain_all", "冷却塔配管全排水"),
                ("chilled_water_bypass_open", "冷水往還直結バイパス開放")
            ],
            "standby_chiller_stay_off", "standby_chiller_startup"
        ),
        (
            "15",
            "危険物薬品保管倉庫の空調監視規定。『庫内室温が25℃以下なら空調送風通常、30℃を超過した場合は冷房最大能力運転かつ高温警報出力』とする。",
            "温湿度ロガー測定：庫内温度21.5℃、湿度45%である。倉庫空調制御を選択せよ。",
            "温湿度ロガー測定：庫内温度33.2℃を記録し急上昇中である。倉庫空調制御を選択せよ。",
            [
                ("hvac_normal_ventilation", "空調定格通常運転"),
                ("hvac_maximum_cooling_alarm", "最大能力急速冷却・高温警報発令"),
                ("chemical_exhaust_damper_close", "有機溶剤排気ダンパー全閉"),
                ("warehouse_dehumidify_only", "除湿再熱専用運転")
            ],
            "hvac_normal_ventilation", "hvac_maximum_cooling_alarm"
        ),
        (
            "16",
            "フィンテック決済プラットフォームの不正検知判定規則。『直前利用から10分以内に500km以上離れた海外IPから決済要求があった場合は承認拒絶、同一国内正規端末なら即時承認』とする。",
            "トランザクション情報：直前決済（東京）から5分後、同一端末・東京の同一プロバイダから決済要求があった。判定せよ。",
            "トランザクション情報：直前決済（東京）から8分後、南米所在の匿名VPN経由で高額決済要求があった。判定せよ。",
            [
                ("payment_auto_approve", "即時オーソリ承認"),
                ("payment_fraud_decline", "不正検知フラグ立脚・決済拒絶"),
                ("cardholder_credit_increase", "限度額自動増枠"),
                ("transaction_split_invoice", "分割請求書自動発行")
            ],
            "payment_auto_approve", "payment_fraud_decline"
        ),
        (
            "17",
            "自動車製造ラインの産業用溶接ロボットにおけるシールドガス流量規則。『アルゴン混合ガス流量が12L/min以上ならアーク溶接実行、8L/min未満ならアーク放電禁止』とする。",
            "マスフローメータ実測：ガス流量は14.5L/minで規定範囲内である。ロボット溶接指示を決定せよ。",
            "マスフローメータ実測：供給圧低下によりガス流量は4.8L/minへ減少した。ロボット溶接指示を決定せよ。",
            [
                ("weld_strike_arc", "溶接アーク点弧・ビード溶接開始"),
                ("weld_gas_fault_abort", "溶接開始阻止・ガス流量不足停止"),
                ("wire_feed_inch_reverse", "溶接ワイヤ自動巻戻し"),
                ("torch_nozzle_clean_cycle", "トーチノズルスパッタ清掃")
            ],
            "weld_strike_arc", "weld_gas_fault_abort"
        ),
        (
            "18",
            "下水処理施設の曝気ブロワー自動制御規定。『曝気槽内の溶存酸素（DO）が1.0mg/L未満なら送風ブロワー増段、3.0mg/L超過なら減段、1.0〜3.0mg/Lは現状維持』とする。",
            "DO電極計測値：現在曝気槽DOは0.4mg/Lに酸欠低下している。ブロワー制御を決定せよ。",
            "DO電極計測値：現在曝気槽DOは4.2mg/Lに過剰上昇している。ブロワー制御を決定せよ。",
            [
                ("blower_step_up", "送風ブロワー1台追加増段"),
                ("blower_step_down", "送風ブロワー1台停止減段"),
                ("blower_hold_current", "現行ブロワー台数維持"),
                ("sludge_return_pump_stop", "返送汚泥ポンプ停止")
            ],
            "blower_step_up", "blower_step_down"
        ),
        (
            "19",
            "EC物流センターのクロスベルトソーター自動仕分けルール。『仕分け荷物の配送先バーコードが100%読み取り成功時は正規シュートへ排出、読取不可時は例外リジェクトシュートへ送出』とする。",
            "光学バーコードリーダ：配送先バーコードを正常デコードし、仕分け番線『シュート12』を特定した。仕分け動作を選択せよ。",
            "光学バーコードリーダ：ラベルかすれ・汚れのためチェックサム不一致・読取不能（NO READ）が発生した。仕分け動作を選択せよ。",
            [
                ("sorter_discharge_regular", "指定仕分けシュートへ正常排出"),
                ("sorter_discharge_reject", "例外リジェクトシュートへ搬送排出"),
                ("conveyor_line_pause", "全ソーターライン非常停止"),
                ("weight_re_calibration", "動的計量スケール再ゼロ点")
            ],
            "sorter_discharge_regular", "sorter_discharge_reject"
        ),
        (
            "20",
            "IP遠隔医療高精細映像伝送のネットワークQoS制御基準。『パケット損失率が0.1%未満なら4K非圧縮伝送維持、1.0%超過なら動的ビットレート圧縮モードへ切替』とする。",
            "ルーターSNMP統計：過去1分間のパケットロス率は0.00%を維持している。映像エンコーダ制御を決定せよ。",
            "ルーターSNMP統計：ネットワーク混雑によりパケットロス率が3.8%へ跳ね上がった。映像エンコーダ制御を決定せよ。",
            [
                ("video_stream_lossless_4k", "4K非圧縮高精細伝送継続"),
                ("video_stream_adaptive_compress", "低遅延適応圧縮ストリームへ切替"),
                ("network_port_shutdown", "光トランシーバポート強制切断"),
                ("audio_channel_mute_all", "音声通話チャンネル全消音")
            ],
            "video_stream_lossless_4k", "video_stream_adaptive_compress"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k4_defs:
        pairs.append({
            "id": f"rc2b4_core_{gid}_s1", "group_id": f"rc2b4_core_{gid}", "family": "core_rules",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_core_{gid}_s2", "group_id": f"rc2b4_core_{gid}", "family": "core_rules",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=6 (5 pairs: groups 21 to 25) ---
    k6_defs = [
        (
            "21",
            "スマート超高層ビルの防災設備連動規則。『火災報知器から確定発報信号を受信した場合は即時排煙ダンパー全開、発報なしまたは点検解除時はダンパー全閉維持』とする。",
            "防災盤ステータス：15階南側煙感知器より確定火災発報を受信した。排煙ダンパー制御を選択せよ。",
            "防災盤ステータス：感知器誤報点検が完了し全回線正常復帰信号を受信した。排煙ダンパー制御を選択せよ。",
            [
                ("damper_emergency_open", "該当フロア排煙ダンパー全開"),
                ("damper_keep_closed", "排煙ダンパー全閉待機維持"),
                ("sprinkler_main_valve_close", "スプリンクラー元弁閉塞"),
                ("elevator_express_run", "非常用エレベーター高速運行"),
                ("power_transformer_disconnect", "主変圧器強制電路遮断"),
                ("emergency_generator_test", "非常用発電機手動無負荷試運転")
            ],
            "damper_emergency_open", "damper_keep_closed"
        ),
        (
            "22",
            "超伝導マグネット用液体ヘリウムクライオスタットの真空断熱度監視規定。『外槽真空度が1.0×10^-3 Pa以下なら超伝導通電許可、1.0×10^-1 Pa以上へ悪化した場合は通電停止インターロック作動』とする。",
            "ペニング真空計測定値：真空度は3.5×10^-4 Paの極高真空を保っている。励磁電源制御を決定せよ。",
            "ペニング真空計測定値：真空シール部リークにより真空度は2.2×10^-1 Paまで悪化した。励磁電源制御を決定せよ。",
            [
                ("superconducting_power_on", "超伝導マグネット励磁通電許可"),
                ("superconducting_interlock_trip", "真空度低下インターロック作動・即時消磁"),
                ("helium_vent_valve_open", "ヘリウムガス大気緊急放出"),
                ("cryocooler_speed_override", "小型冷凍機回転数手動加速"),
                ("quench_heater_forced_fire", "クエンチヒーター全素子強制点火"),
                ("liquid_nitrogen_pre_cool", "液体窒素予冷循環開始")
            ],
            "superconducting_power_on", "superconducting_interlock_trip"
        ),
        (
            "23",
            "港湾コンテナターミナルのガントリークレーン強風作業安全基準。『10分間平均風速が16m/s以上で荷役作業全面中止・レールクランプ締結、10m/s未満で通常荷役実施』とする。",
            "気象観測タワー計測値：10分間平均風速は5.8m/sで穏やかである。クレーン荷役判断を行え。",
            "気象観測タワー計測値：10分間平均風速は18.4m/sに達し突風を伴っている。クレーン荷役判断を行え。",
            [
                ("crane_operation_normal", "コンテナ荷役通常作業実施"),
                ("crane_typhoon_lockdown", "荷役全面中断・レールクランプ締結固定"),
                ("crane_spreader_free_swing", "スプレッダー自由揺動モード"),
                ("trolley_high_speed_traverse", "トロリ最高速横行"),
                ("boom_hoist_midway_stop", "ブーム起伏中間角度保持"),
                ("diesel_generator_emergency_dump", "主発電機負荷急遮断")
            ],
            "crane_operation_normal", "crane_typhoon_lockdown"
        ),
        (
            "24",
            "化学品合成連続反応プラントの重合暴走防止安全インターロック。『反応釜内圧が0.8MPaを超過した場合は緊急重合停止剤注入、0.3MPa以下で安定運転継続』とする。",
            "圧力トランスミッタ計器値：釜内圧力は0.18MPaで定常圧力を推移している。プラント運転制御を決定せよ。",
            "圧力トランスミッタ計器値：発熱暴走により釜内圧力が1.05MPaを突破した。プラント運転制御を決定せよ。",
            [
                ("chemical_reaction_steady", "定常重合反応継続"),
                ("chemical_inhibitor_inject", "緊急重合停止剤（キラー）高圧注入"),
                ("steam_jacket_heating_max", "加熱スチーム弁最大開度"),
                ("feed_raw_monomer_boost", "原料モノマー供給倍増"),
                ("agitator_motor_stop", "撹拌機モーター完全停止"),
                ("distillation_column_vent_close", "精留塔ベント弁完全密閉")
            ],
            "chemical_reaction_steady", "chemical_inhibitor_inject"
        ),
        (
            "25",
            "自動搬送台車（AGV）フリートのバッテリー充電マネジメント規定。『バッテリー残量（SoC）が20%以下なら充電ステーションへ自動帰還、60%以上なら次期搬送タスク割り当て』とする。",
            "車載BMSテレメトリ：現在のSoCは85%であり異常セルなし。AGV管制指示を選択せよ。",
            "車載BMSテレメトリ：現在のSoCは14%に減少し警告域にある。AGV管制指示を選択せよ。",
            [
                ("agv_assign_next_mission", "次期搬送タスク割当・出走"),
                ("agv_dock_auto_charge", "搬送列離脱・自動充電ステーション帰還"),
                ("agv_sleep_hibernate", "主電源遮断スリープ移行"),
                ("agv_wheel_brake_manual_release", "車輪電磁ブレーキ手動解除"),
                ("agv_payload_emergency_dump", "積載荷物路上自動投下"),
                ("agv_speed_unlimited_mode", "最高速度制限解除")
            ],
            "agv_assign_next_mission", "agv_dock_auto_charge"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k6_defs:
        pairs.append({
            "id": f"rc2b4_core_{gid}_s1", "group_id": f"rc2b4_core_{gid}", "family": "core_rules",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_core_{gid}_s2", "group_id": f"rc2b4_core_{gid}", "family": "core_rules",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=8 (5 pairs: groups 26 to 30) ---
    k8_defs = [
        (
            "26",
            "高層オフィスビルにおけるエレベーター地震時管制運転規程。『地震計P波（初期微動）感知時は最寄り階に急行停止・戸開放、感知なし（平常時）は通常運行サービス継続』とする。",
            "防災盤地震計インターフェース：振動加速度0gal、地震波未検知信号を受信している。エレベーター制御を指示せよ。",
            "防災盤地震計インターフェース：震源断層からのP波感知器（閾値5gal超過）が発報した。エレベーター制御を指示せよ。",
            [
                ("elevator_service_normal", "通常自動群管理運転サービス継続"),
                ("elevator_p_wave_park", "最寄り階緊急着床・戸開放・乗客降車誘導"),
                ("elevator_cage_counterweight_drop", "釣合錘緊急切り離し"),
                ("elevator_hoist_motor_reverse", "巻上機主軸急逆転"),
                ("elevator_governor_manual_trip", "調速機手動強制トリップ"),
                ("elevator_door_lock_tight", "全階出入口扉強制施錠固定"),
                ("elevator_pit_flood_alarm", "昇降路ピット冠水警報出力"),
                ("elevator_car_top_inspection", "かご上保守点検手動モード")
            ],
            "elevator_service_normal", "elevator_p_wave_park"
        ),
        (
            "27",
            "病院電子カルテ処方オーダー支援システムの禁忌相互作用判定。『処方薬と併用禁忌（併用不可）の組み合わせが検出された場合は処方オーダー阻止・警告ダイアログ表示、禁忌なしは処方確定登録』とする。",
            "相互作用エンジン照合結果：併用禁忌相互作用は0件、相互作用データベース照合一致なし。オーダー確定処理を選択せよ。",
            "相互作用エンジン照合結果：抗不整脈薬と抗生物質による重篤なQT延長禁忌の相互作用が検出された。オーダー確定処理を選択せよ。",
            [
                ("prescription_commit_success", "処方オーダ承認・確定発行"),
                ("prescription_block_contraindication", "処方確定阻止・併用禁忌警告提示"),
                ("prescription_dosage_double", "処方用量自動倍加変更"),
                ("prescription_route_iv_switch", "経口薬から点滴静注へ自動変更"),
                ("prescription_anonymize_delete", "患者カルテ情報匿名消去"),
                ("pharmacy_dispense_bypass", "薬剤部調剤監査スキップ"),
                ("insurance_claim_instant_charge", "診療報酬即時全額請求"),
                ("prescription_generic_disable", "後発医薬品変更不可一括設定")
            ],
            "prescription_commit_success", "prescription_block_contraindication"
        ),
        (
            "28",
            "鉄道自動改札機のICカード入場判定規則。『定期券有効区間内またはSFチャージ残額が初乗り運賃（150円）以上の場合は入場扉開放、残額不足かつ区間外は入場阻止・赤色案内表示』とする。",
            "ICカード読み取り結果：定期券は区間外であるが、SFチャージ残高は2,450円ある。改札判定を決定せよ。",
            "ICカード読み取り結果：定期券は区間外であり、SFチャージ残高は40円である。改札判定を決定せよ。",
            [
                ("turnstile_gate_open", "改札通路扉開放・入場記録書込"),
                ("turnstile_gate_close_deny", "改札通路扉閉止・残額不足エラー案内"),
                ("turnstile_reboot_firmware", "改札機ファームウェア再起動"),
                ("turnstile_retain_card_physically", "ICカード物理回収没収"),
                ("turnstile_magnetic_ticket_slot", "磁気券投入スロット開通"),
                ("turnstile_emergency_free_pass", "災害時無賃開放モード"),
                ("turnstile_fare_refund_dispense", "過剰運賃現金自動払出"),
                ("turnstile_remote_lockdown", "駅務室一括全通路封鎖")
            ],
            "turnstile_gate_open", "turnstile_gate_close_deny"
        ),
        (
            "29",
            "石油化学コンビナートの可燃性ガス漏洩検知連動基準。『ガス濃度が爆発下限界（LEL）の20%以上を検出した場合は防消火放水銃自動照準・非常警報、LEL 2%以下は監視継続』とする。",
            "接触燃焼式センサテレメトリ：現在の炭化水素ガス濃度は0.0% LEL（バックグラウンド値）である。保安措置を決定せよ。",
            "接触燃焼式センサテレメトリ：配管フランジ周辺でガス濃度28% LELを検出した。保安措置を決定せよ。",
            [
                ("gas_monitor_standby_normal", "ガス漏洩平常監視ステータス維持"),
                ("gas_deluge_fire_monitor_alarm", "防災放水銃自動起動・事業所全域非常警報"),
                ("flare_stack_pilot_igniter_off", "フレアスタック消火パイロット停止"),
                ("crude_oil_tank_inlet_open_wide", "原油タンク受入弁全開"),
                ("process_furnace_damper_close", "加熱炉排気ダンパー密閉"),
                ("nitrogen_purge_header_drain", "窒素パージ配管全ドレン弁開放"),
                ("booster_pump_max_rpm", "昇圧ポンプ最高回転数増速"),
                ("cathodic_protection_reverse_polarity", "電気防食極性反転")
            ],
            "gas_monitor_standby_normal", "gas_deluge_fire_monitor_alarm"
        ),
        (
            "30",
            "特別高圧受変電設備の保護継電器（OCR/GR）連動基準。『高圧側地絡過電流（零相電流）が整定値0.5A以上検出時は主受電遮断器（VCB）即時トリップ、平衡電流時は送電受電維持』とする。",
            "保護継電器盤サンプリング：零相変流器（ZCT）出力電流は0.01A（ノイズ閾値未満）である。遮断器制御を指示せよ。",
            "保護継電器盤サンプリング：高圧ケーブル地絡により零相電流1.25Aが継続検出された。遮断器制御を指示せよ。",
            [
                ("vcb_close_power_maintain", "主受電遮断器VCB投入状態維持・給電継続"),
                ("vcb_trip_earth_fault", "主受電遮断器VCB地絡トリップ・保護遮断"),
                ("disconnecting_switch_hot_open", "断路器通電中手動開放"),
                ("capacitor_bank_discharge_earth", "進相コンデンサ即時地絡放電"),
                ("transformer_tap_change_max", "変圧器タップ急変最高段切替"),
                ("lightning_arrester_replace", "避雷器即時交換信号"),
                ("battery_charger_bypass_load", "蓄電池充電器バイパス直接給電"),
                ("analog_meter_scale_recalibrate", "アナログ指示計指針再調整")
            ],
            "vcb_close_power_maintain", "vcb_trip_earth_fault"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k8_defs:
        pairs.append({
            "id": f"rc2b4_core_{gid}_s1", "group_id": f"rc2b4_core_{gid}", "family": "core_rules",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_core_{gid}_s2", "group_id": f"rc2b4_core_{gid}", "family": "core_rules",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    return pairs
