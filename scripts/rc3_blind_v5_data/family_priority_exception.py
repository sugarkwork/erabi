"""Blind v5 Family: Priority Exception (30 pairs, 60 cases).

Choice count distribution:
- K=3: 10 pairs (prio_01 to prio_10)
- K=4: 15 pairs (prio_11 to prio_25)
- K=6: 5 pairs (prio_26 to prio_30)

Zero model inference during authoring; 100% fresh domain scenarios.
Token length strictly controlled (all <= 350 tokens).
"""

from __future__ import annotations
from typing import Any, Dict, List


def get_priority_exception_pairs() -> List[Dict[str, Any]]:
    pairs = []

    # K=3: 10 pairs (01..10)
    k3_defs = [
        (
            "01",
            "半導体クリーンルームの排気ダクト防火防煙制御規定。通常規定：『排気温度が65℃を超過した場合はダクト内防火ダンパーを自動閉止する』。特例優先規定：『ただしシランガス漏洩警報が発報中の場合は、有毒ガス滞留防止を最優先とし防火ダンパーの自動閉止をインターロック阻止して強制排気送風を継続する』。",
            "排気ダクト温度センサが74℃を検知した。シランガス検知警報器は全点正常（非発報）である。ダンパー制御を選択せよ。",
            "damper_auto_close_fire",
            "排気ダクト温度センサが74℃を検知した。同時にシランガス検知器が第3ゾーン漏洩（15ppm）を発報中である。ダンパー制御を選択せよ。",
            "damper_inhibit_forced_exhaust",
            [
                ("damper_auto_close_fire", "防火ダンパー自動閉止"),
                ("damper_inhibit_forced_exhaust", "閉止阻止強制排気継続"),
                ("damper_routine_standby", "通常風量維持待機"),
            ],
        ),
        (
            "02",
            "商用航空機の飛行管理コンピュータ（FMC）降下率規程。通常規程：『アプローチ降下中はキャビン気圧変化率制限に従い降下率2,000fpmを維持する』。緊急優先規程：『ただしTCAS（空中衝突防止装置）の降下Resolution Advisory（RA）発令時は、TCAS目標垂直速度（3,000fpm以上）への即時追従を最優先とする』。",
            "アプローチ降下中、気圧調整要求を受信。TCAS監視画面はトラフィックなし（緑色通常）。降下指示を選択せよ。",
            "fmc_standard_descent_rate",
            "アプローチ降下中、気圧調整要求を受信。同時にTCAS降下RA警告音（Descend!）が最大音量で発令された。降下指示を選択せよ。",
            "tcas_ra_immediate_descent",
            [
                ("fmc_standard_descent_rate", "標準降下率維持"),
                ("tcas_ra_immediate_descent", "TCAS降下RA即時追従"),
                ("fmc_level_off_hold", "即時水平飛行移行"),
            ],
        ),
        (
            "03",
            "バイオ医薬品注射剤充填ラインのオートクレーブ滅菌扉制御。通常規程：『滅菌完了後はチャンバー内温度が50℃未満に低下するまで外側扉のアンロックを禁止する』。保安優先規程：『ただし停電バックアップ移行かつ室内差圧逆転警報（交差汚染リスク）発報時は、陽圧維持のため全扉を強制施錠維持しアンロックを無効化する』。",
            "滅菌工程終了後、チャンバー温度が42℃まで低下した。室内差圧および商用電源は正常である。扉操作を選択せよ。",
            "door_unlock_permit",
            "滅菌工程終了後、チャンバー温度が42℃まで低下したが、商用停電により非常電源稼働中で室内差圧逆転警報が発報している。扉操作を選択せよ。",
            "door_lock_override_keep",
            [
                ("door_unlock_permit", "外側扉アンロック許可"),
                ("door_lock_override_keep", "全扉強制施錠維持"),
                ("door_manual_release_vent", "手動ベント開放扉開放"),
            ],
        ),
        (
            "04",
            "石油化学プラント高圧蒸留塔の過圧放散制御。通常規程：『塔頂圧力が3.2MPaを超えた場合は大気放散フレア弁を自動開とする』。環境特例規程：『ただしフレアスタック点火トーチの失火警報が作動している場合は、未燃炭化水素放出防止のため大気放散を阻止し、密閉クローズド回収系への緊急バイパス切替を先行する』。",
            "塔頂圧力が3.45MPaまで上昇した。フレア点火トーチ監視カメラおよび炎検知器は点火維持を示している。放散制御を選択せよ。",
            "flare_release_valve_open",
            "塔頂圧力が3.45MPaまで上昇した。しかしフレアスタックの炎検知器が失火警報を出力している。放散制御を選択せよ。",
            "flare_inhibit_closed_recovery",
            [
                ("flare_release_valve_open", "大気放散フレア弁自動開"),
                ("flare_inhibit_closed_recovery", "放散阻止密閉回収切替"),
                ("flare_standby_steady_state", "放散弁閉維持定常運転"),
            ],
        ),
        (
            "05",
            "都市高速鉄道の自動列車停止装置（ATS）速度超過介入規程。通常規程：『信号現示速度照査パターンを超過した列車は非常ブレーキ（EB）を即時自動印加する』。防災優先規程：『ただし列車が長大海底トンネル内（浸水避難指定区間）を走行中の場合は、トンネル内停車を避けるためEB印加を30秒間保留し常用最大ブレーキ（B7）による前方駅進入を優先する』。",
            "地上区間走行中、列車速度が照査パターンを8km/h超過した。保安装置の介入動作を選択せよ。",
            "ats_emergency_brake_apply",
            "長大海底トンネル浸水避難指定区間を走行中、列車速度が照査パターンを8km/h超過した。保安装置の介入動作を選択せよ。",
            "ats_service_brake_station_advance",
            [
                ("ats_emergency_brake_apply", "非常ブレーキ即時印加"),
                ("ats_service_brake_station_advance", "常用最大制動駅進入優先"),
                ("ats_traction_power_keep", "力行加速維持走行"),
            ],
        ),
        (
            "06",
            "データセンター液冷チラー設備の凍結防止運転基準。通常規程：『外気温度が2℃以下に低下した場合は冷水循環ポンプの低速凍結防止循環を自動起動する』。節電特例規程：『ただし蓄熱水槽の蓄熱材充填温度が15℃以上を保持している間は、ポンプを起動せず蓄熱自然対流バイパスを開放する』。",
            "外気温センサが-1.5℃を計測した。蓄熱水槽温度は7.2℃である。チラー保全制御を選択せよ。",
            "chiller_pump_freeze_protect_run",
            "外気温センサが-1.5℃を計測した。蓄熱水槽温度は18.5℃で十分な熱量を保持している。チラー保全制御を選択せよ。",
            "chiller_thermal_bypass_open",
            [
                ("chiller_pump_freeze_protect_run", "ポンプ凍結防止循環起動"),
                ("chiller_thermal_bypass_open", "蓄熱自然対流バイパス開放"),
                ("chiller_heater_emergency_burn", "非常電熱ヒーター最大投入"),
            ],
        ),
        (
            "07",
            "深海潜水調査艇のスラスター電力配分優先規程。通常規程：『メインバッテリ残容量が20%未満になった場合はスラスター出力を定格の40%に制限して母船帰還航行を行う』。生命維持最優先規程：『ただし艇内酸素分圧が18kPa未満に低下した場合は、航行制限を解除し全電力供給をバラスト急速投棄および浮上スラスター全開（100%）へ振り分ける』。",
            "バッテリ残容量が17%まで減少した。艇内酸素分圧は21.2kPaで正常域にある。スラスター出力を選択せよ。",
            "thruster_economy_return_limit",
            "バッテリ残容量が17%まで減少した。さらに艇内酸素分圧が16.8kPaまで急低下した。スラスター出力を選択せよ。",
            "thruster_full_ascent_ballast",
            [
                ("thruster_economy_return_limit", "スラスター出力40%制限"),
                ("thruster_full_ascent_ballast", "浮上スラスター全開バラスト投棄"),
                ("thruster_normal_cruise_mode", "定常巡航出力維持"),
            ],
        ),
        (
            "08",
            "原子力発電所タービン建屋の給水加熱器ドレン逆流防止規程。通常規程：『ドレンタンク水位が高水位（H）に達した場合はドレン非常ダンプ弁を自動全開する』。蒸気発生器保護最優先：『ただし蒸気発生器（SG）給水流量喪失警報が作動中は、給水枯渇防止のためダンプ弁開放を阻止し復水器バイパスへ再循環させる』。",
            "ドレンタンク水位がHレベルに到達した。給水系流量は定常運転値を維持している。弁制御を選択せよ。",
            "drain_dump_valve_open",
            "ドレンタンク水位がHレベルに到達した。しかし同時に給水流量喪失警報（Trip事前兆候）が点滅している。弁制御を選択せよ。",
            "drain_dump_inhibit_recirculate",
            [
                ("drain_dump_valve_open", "ドレン非常ダンプ弁全開"),
                ("drain_dump_inhibit_recirculate", "ダンプ阻止復水器再循環"),
                ("drain_normal_level_control", "通常水位制御弁調整"),
            ],
        ),
        (
            "09",
            "救急医療ヘリコプターの悪天候出動基準。通常基準：『現場の雲底高度が300m以上かつ視程1,500m以上の場合に出動承認する』。災害救助特例基準：『ただし大規模震災に伴うトリアージ赤（重篤救命救急）患者の要請であり、運航管理者が目視飛行可能と承認した場合は、視程1,000mまで出動基準を緩和して承認する』。",
            "現場雲底350m、視程1,200m。要請は通常の一般交通事故（トリアージ黄・骨折疑い）。出動可否を選択せよ。",
            "helo_dispatch_deny",
            "現場雲底350m、視程1,200m。要請は大震災倒壊現場のトリアージ赤患者で運航管理者が特別承認済みである。出動可否を選択せよ。",
            "helo_dispatch_special_approve",
            [
                ("helo_dispatch_deny", "気象基準未達出動不承認"),
                ("helo_dispatch_special_approve", "特例緩和基準出動承認"),
                ("helo_dispatch_auto_standby", "基地前進待機指示"),
            ],
        ),
        (
            "10",
            "下水終末処理場の流入ゲート雨天制御。通常規程：『流入管路水位が危険水位（HWL）を超過した場合は放流ゲートを開き自然越流を許可する』。水質環境優先規程：『ただし初期降雨指数が基準値未満（初回高濃度汚濁水路段）の場合は越流を禁止し、雨水滞水池への全量一時貯留弁を開放する』。",
            "流入管路水位がHWLを超えた。初期降雨指数は十分高く汚濁ピークは通過済み（通常希釈水）。制御を選択せよ。",
            "influent_gate_overflow_permit",
            "流入管路水位がHWLを超えた。しかし降雨開始直後であり初期降雨指数は基準値未満の未希釈高濃度状態である。制御を選択せよ。",
            "influent_basin_detention_store",
            [
                ("influent_gate_overflow_permit", "放流ゲート自然越流許可"),
                ("influent_basin_detention_store", "越流禁止雨水滞水池貯留"),
                ("influent_throttle_close_main", "流入主弁全閉遮断"),
            ],
        ),
    ]

    for pid, ctx, q1, t1, q2, t2, chs in k3_defs:
        choices = [{"id": cid, "text": ctxt} for cid, ctxt in chs]
        pairs.append({
            "pair_id": f"rc3_blind5_prio_{pid}",
            "family": "priority_exception",
            "k": 3,
            "case_1": {
                "id": f"rc3_blind5_prio_{pid}_s1",
                "group_id": f"rc3_blind5_prio_{pid}",
                "family": "priority_exception",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1},
            },
            "case_2": {
                "id": f"rc3_blind5_prio_{pid}_s2",
                "group_id": f"rc3_blind5_prio_{pid}",
                "family": "priority_exception",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2},
            },
        })

    # K=4: 15 pairs (11..25)
    k4_defs = [
        (
            "11",
            "メガソーラー蓄電連携発電所の充電管理ポリシー。通常規程：『売電単価がオフピーク帯（10円/kWh以下）のときは蓄電池へ最大レート充電を行う』。系統安定優先規程：『ただし送配電事業者からの系統周波数低下（49.8Hz以下）緊急警報受信時は、充電を即時停止して蓄電池放電による周波数制御支援を最優先する』。",
            "現在オフピーク深夜帯（8円/kWh）。系統周波数は50.0Hzで安定している。蓄電池制御指令を選択せよ。",
            "bess_max_charge_exec",
            "現在オフピーク深夜帯（8円/kWh）。しかし系統周波数が49.6Hzに急低下し周波数支援指令が発令された。蓄電池制御指令を選択せよ。",
            "bess_emergency_discharge_grid",
            [
                ("bess_max_charge_exec", "蓄電池最大レート充電"),
                ("bess_emergency_discharge_grid", "充電停止周波数放電支援"),
                ("bess_standby_float", "浮動充電待機維持"),
                ("bess_island_disconnect", "系統解列単独運転"),
            ],
        ),
        (
            "12",
            "LNG受入基地の超低温ポンプ保全基準。通常基準：『軸受振動加速度が4.5mm/sを超えた場合は速やかに予備ポンプへ切り替え主ポンプを通常停止する』。送出確保最優先：『ただし都市ガス送出ラインの圧力が下限閾値（1.8MPa）を割っている非常時は、ポンプ緊急停止をインターロック阻止しアラーム鳴動下で送出運転を継続する』。",
            "主ポンプの軸受振動が5.2mm/sを記録した。送出ライン圧力は2.4MPaで正常域である。保全対応を選択せよ。",
            "lng_pump_switch_standby_stop",
            "主ポンプの軸受振動が5.2mm/sを記録した。しかし送出ライン圧力が1.6MPaまで落ち込んでおりガス供給逼迫中である。保全対応を選択せよ。",
            "lng_pump_inhibit_stop_keep_send",
            [
                ("lng_pump_switch_standby_stop", "予備切替主ポンプ通常停止"),
                ("lng_pump_inhibit_stop_keep_send", "停止阻止送出運転継続"),
                ("lng_pump_emergency_vent_dump", "ライン全ベント緊急放出"),
                ("lng_pump_speed_reduce_idle", "アイドリング低速回転"),
            ],
        ),
        (
            "13",
            "国際貨物コンテナ船のバラスト水排出規定。通常規定：『排水分照濁度計が10NTU以下かつUV殺菌装置通過時のみ港湾内排出を許可する』。復原力保安優先：『ただし突風波浪による横傾斜角が12度を超え転覆危険警報が発動したときは、水質基準に関わらず緊急傾側復元バラスト排水を即時実行する』。",
            "入港前排水準備。濁度は7NTU、UV照射正常。船体傾斜角は1.2度で安定。バラスト弁制御を選択せよ。",
            "ballast_harbor_discharge_permit",
            "入港前排水準備。濁度は18NTU（水質不適合）。しかし突風により船体が14.5度傾斜し転覆警報が鳴動した。バラスト弁制御を選択せよ。",
            "ballast_emergency_righting_drain",
            [
                ("ballast_harbor_discharge_permit", "港湾内バラスト排出許可"),
                ("ballast_emergency_righting_drain", "緊急傾側復元排水即時実行"),
                ("ballast_internal_transfer_only", "船内タンク間移送限定"),
                ("ballast_valve_all_close_hold", "全バラスト弁閉鎖保持"),
            ],
        ),
        (
            "14",
            "半導体製造露光装置（EUV）のレーザー発振冷却水規程。通常規程：『冷却水出口温度が22.0℃を超過したときはレーザー励起出力を半減させて温度上昇を抑制する』。アライメント維持特例：『ただしロット最終ウェーハの露光シーケンス実行中（露光終了まで残り90秒以内）は、重ね合わせ精度破綻を防ぐため励起出力を維持しチラー循環量を上限まで増量する』。",
            "露光待機中、冷却水温度が22.4℃に上昇した。現在ウェーハ交換工程中である。レーザー冷却制御を選択せよ。",
            "laser_derate_half_power",
            "露光工程中、冷却水温度が22.4℃に上昇した。現在ロット最終ウェーハ露光中で残り時間は40秒である。レーザー冷却制御を選択せよ。",
            "laser_keep_power_max_coolant",
            [
                ("laser_derate_half_power", "励起出力50%制限"),
                ("laser_keep_power_max_coolant", "出力維持チラー流量最大化"),
                ("laser_emergency_beam_dump", "ビームダンプ緊急遮断"),
                ("laser_standby_purge_cycle", "パージサイクル待機移行"),
            ],
        ),
        (
            "15",
            "高潮防潮水門の自動閉鎖規程。通常規程：『外洋潮位がT.P.+3.5mに達した場合は河川防潮水門を全閉位置へ降下する』。避難船舶退避特例：『ただし水門通過中の避難船舶感知レーダーが作動中で、潮位上昇率が許容限界内（0.5m/h未満）の場合は、水門降下を10分間待機して船舶退避を優先する』。",
            "外洋潮位がT.P.+3.6mを記録した。水門通過レーダーに船舶エコーは検出されていない。水門操作を選択せよ。",
            "gate_auto_full_close_drop",
            "外洋潮位がT.P.+3.6mを記録した。現在避難漁船群が水門通過中であり潮位上昇率は0.2m/hである。水門操作を選択せよ。",
            "gate_delay_evacuation_vessel",
            [
                ("gate_auto_full_close_drop", "防潮水門全閉降下"),
                ("gate_delay_evacuation_vessel", "10分待機船舶退避優先"),
                ("gate_lock_full_open", "水門全開ロック維持"),
                ("gate_step_throttle_half", "半開位置中間保持"),
            ],
        ),
        (
            "16",
            "化学品合成リアクターの攪拌機フェイルセーフ規程。通常規程：『攪拌モータートルクが定格の130%を超えた場合は過負荷保護のためモータートリップ停止する』。暴走反応防止最優先：『ただし反応器内温度が自己発熱暴走閾値（180℃以上）にある場合は、モータートリップを無効化し粘度上昇固着を防ぐため最大トルクで強制連続回転する』。",
            "攪拌トルクが定格138%に達した。反応温度は145℃で制御範囲内である。モータ保護動作を選択せよ。",
            "agitator_motor_overload_trip",
            "攪拌トルクが定格138%に達した。しかし反応温度は192℃まで跳ね上がっており熱暴走兆候を示す。モータ保護動作を選択せよ。",
            "agitator_override_forced_max_run",
            [
                ("agitator_motor_overload_trip", "過負荷モータートリップ停止"),
                ("agitator_override_forced_max_run", "トリップ無効強制連続回転"),
                ("agitator_reverse_jog_mode", "逆転寸動解離モード"),
                ("agitator_emergency_quench_dump", "冷媒クエンチ緊急投下"),
            ],
        ),
        (
            "17",
            "医薬品固形製剤コーティング機の吸気湿度制御。通常規程：『吸気露点が12℃を超えた場合は除湿ローター再生ヒーターを強運転へ切り替える』。粉塵爆発防止優先：『ただしコーティングパン内有機溶剤ガス濃度が下限界25%を超過した場合は、除湿ヒーターを強制即時遮断し窒素不活性ガス置換を最優先する』。",
            "吸気露点が14.2℃を記録した。有機溶剤ガス濃度センサは3%（清浄域）である。吸気設備制御を選択せよ。",
            "dehum_heater_high_power",
            "吸気露点が14.2℃を記録した。同時に有機溶剤ガス濃度が爆発下限界の32%へ急上昇した。吸気設備制御を選択せよ。",
            "dehum_heater_cut_n2_purge",
            [
                ("dehum_heater_high_power", "除湿ヒーター強運転切替"),
                ("dehum_heater_cut_n2_purge", "ヒーター遮断窒素置換最優先"),
                ("dehum_exhaust_bypass_full", "全量外気バイパス排気"),
                ("dehum_steady_state_keep", "定常運転パラメータ維持"),
            ],
        ),
        (
            "18",
            "超高圧送電線用ガス絶縁開閉装置（GIS）の再閉路規程。通常規程：『送電線地絡事故検出時は1秒後に高速度無電圧再閉路シーケンスを実行する』。重度内部事故特例：『ただしGIS遮断器ベイのSF6ガス圧力低下警報（絶縁破壊危険）が併発している場合は、再閉路を完全にロックアウトし遮断状態を固定する』。",
            "275kV送電線瞬時地絡トリップ発生。SF6ガス圧力センサは定常健全値（0.55MPa）を維持している。再閉路制御を選択せよ。",
            "reclose_auto_high_speed_exec",
            "275kV送電線地絡トリップ発生。同時に遮断器主室のSF6ガス圧低下警報（0.41MPa）が点滅している。再閉路制御を選択せよ。",
            "reclose_lockout_trip_hold",
            [
                ("reclose_auto_high_speed_exec", "高速度再閉路自動実行"),
                ("reclose_lockout_trip_hold", "再閉路ロックアウト遮断固定"),
                ("reclose_manual_delayed_try", "手動時限再閉路移行"),
                ("reclose_bus_tie_split", "母線連絡遮断器開放"),
            ],
        ),
        (
            "19",
            "自動運転商用トラックの車線変更アルゴリズム。通常規程：『後続車接近余裕時間が5秒以上確保されている場合、隣接車線への車線変更マニューバを実行する』。緊急退避優先規程：『ただし自車線前方に完全静止障害物（玉突き事故）を検知し衝突余裕時間が2秒未満の場合は、後続余裕に関わらず回避可能領域へ即時緊急操舵退避を行う』。",
            "前走低速車に追いついた。後続接近余裕時間は7.5秒である。前方障害物はない。走行制御を選択せよ。",
            "lane_change_standard_exec",
            "前走車の急激な玉突き衝突で静止障害物が出現し衝突まで1.4秒。後続接近余裕は3.2秒。走行制御を選択せよ。",
            "emergency_steering_evasion",
            [
                ("lane_change_standard_exec", "通常車線変更実行"),
                ("emergency_steering_evasion", "緊急操舵回避退避"),
                ("lane_follow_steady_brake", "車線維持定常減速"),
                ("shoulder_parking_stop", "路肩完全停車"),
            ],
        ),
        (
            "20",
            "地域冷暖房プラントの蒸気タービン排熱回収規程。通常規程：『排気蒸気エンタルピーが基準以上の場合、低圧蒸気ヘッダーへ全量を供給回収する』。白煙公害防止特例：『ただし地域気象警報で湿度95%超かつ逆転層形成時は、蒸気回収を一時減少し過熱器バイパスで全量ドレン冷却凝縮させて煙突白煙放出を阻止する』。",
            "排気エンタルピー良好。気象条件は晴天湿度55%で大気拡散良好である。排熱回収弁制御を選択せよ。",
            "steam_waste_heat_recovery_run",
            "排気エンタルピー良好。しかし気象警報発令中で湿度98%の濃厚逆転層（白煙公害リスク高）である。排熱回収弁制御を選択せよ。",
            "steam_condense_drain_anti_plume",
            [
                ("steam_waste_heat_recovery_run", "低圧ヘッダー排熱回収"),
                ("steam_condense_drain_anti_plume", "凝縮冷却白煙防止バイパス"),
                ("steam_direct_flare_vent", "大気直接全量放出"),
                ("steam_turbine_bypass_cut", "蒸気タービン入口遮断"),
            ],
        ),
        (
            "21",
            "病院中央滅菌室（CSSD）の過酸化水素プラズマ滅菌器扉制御。通常規程：『減圧排気完了後にチャンバー気圧が大気圧（101.3kPa±2kPa）へ復帰したとき扉インターロックを解除する』。漏洩毒性最優先：『ただしチャンバー内過酸化水素ガス残留濃度が1.0ppmを超過している場合は、大気圧復帰後であっても解錠を阻止し循環分解触媒パージを継続する』。",
            "チャンバー気圧は大気圧（101.1kPa）に復帰。残留ガス濃度は0.05ppmである。扉制御を選択せよ。",
            "sterilizer_door_unlock",
            "チャンバー気圧は大気圧（101.2kPa）に復帰。しかし残留ガス濃度センサが4.8ppmを示している。扉制御を選択せよ。",
            "sterilizer_lock_catalyst_purge",
            [
                ("sterilizer_door_unlock", "滅菌室扉インターロック解除"),
                ("sterilizer_lock_catalyst_purge", "解錠阻止触媒パージ継続"),
                ("sterilizer_vacuum_pump_restart", "高真空排気再開始"),
                ("sterilizer_nitrogen_flood", "窒素ガス加圧封入"),
            ],
        ),
        (
            "22",
            "水力発電所サージタンクの制水ゲート運用規程。通常規程：『水圧管路流量が定格の110%を超えた場合は管路保護のため制水ゲートを急速全閉する』。水撃圧緩和最優先：『ただし下流側水圧脈動周波数が共振危険帯（1.2〜1.8Hz）にある場合は、水撃破壊を防ぐため急速全閉を阻止し、2段階ステップ緩慢閉鎖シーケンスへ切り替える』。",
            "管路流量が定格115%を記録した。水圧脈動センサは0.3Hz（非共振域）である。ゲート操作を選択せよ。",
            "gate_rapid_full_close",
            "管路流量が定格115%を記録した。しかし脈動センサが1.5Hzの顕著な共振ピークを検知している。ゲート操作を選択せよ。",
            "gate_step_slow_close_cushion",
            [
                ("gate_rapid_full_close", "制水ゲート急速全閉"),
                ("gate_step_slow_close_cushion", "急閉阻止2段階緩慢閉鎖"),
                ("gate_full_open_relief", "ゲート全開水圧放流"),
                ("gate_hold_current_opening", "現在開度一時固定"),
            ],
        ),
        (
            "23",
            "トンネル掘削シールドマシンの土圧保持ポリシー。通常規程：『切羽土圧が基準値（0.25MPa）を下回った場合は排土スクリュー回転数を減速させて切羽土圧を回復する』。地表面沈下抑止優先：『ただしトンネル直上地表面沈下計が累積変位-5mm警戒値に達した場合は、減速ではなく裏込注入グラウト材を高圧連続注入し地盤崩壊を先行阻止する』。",
            "切羽土圧センサが0.21MPaに低下。地表面沈下量は-0.8mmで安定している。シールド制御を選択せよ。",
            "shield_screw_speed_reduce",
            "切羽土圧センサが0.21MPaに低下。直上の地表面沈下計が-6.2mmの沈下を検知した。シールド制御を選択せよ。",
            "shield_grout_injection_priority",
            [
                ("shield_screw_speed_reduce", "スクリュー減速土圧保持"),
                ("shield_grout_injection_priority", "裏込グラウト高圧注入先行"),
                ("shield_thrust_jack_max", "推進ジャッキ最大推力"),
                ("shield_cutterhead_stop", "カッターヘッド即時停止"),
            ],
        ),
        (
            "24",
            "高炉ガス乾式除塵設備（TRT）のバイパス放散規程。通常規程：『除塵器入側差圧が15kPaを超過した場合はバグフィルター保護のためTRTバイパス弁を全開する』。一酸化炭素中毒防止優先：『ただし大気逆転層警報発令かつ周辺風速1m/s以下の無風時は、大気放散をインターロック阻止し高炉炉頂圧発電機での減圧燃焼放散系へ全量迂回させる』。",
            "除塵入側差圧が17.2kPaに達した。気象条件は北風4m/sで拡散良好。バイパス制御を選択せよ。",
            "trt_bypass_valve_open",
            "除塵入側差圧が17.2kPaに達した。しかし無風逆転層により地上CO停滞危険警報が発報している。バイパス制御を選択せよ。",
            "trt_inhibit_bypass_generator_burn",
            [
                ("trt_bypass_valve_open", "TRTバイパス弁全開放散"),
                ("trt_inhibit_bypass_generator_burn", "放散阻止発電減圧燃焼迂回"),
                ("trt_bag_filter_shaking_clean", "バグフィルター逆洗払落"),
                ("trt_emergency_steam_quench", "蒸気クエンチ消火弁開"),
            ],
        ),
        (
            "25",
            "浮体式洋上風力発電設備（FOWT）のピッチ制御規程。通常規程：『風速がカットアウト閾値（25m/s）を超えた場合はブレードフェザー（フルフェザー90度）としローターをフリー空転待機させる』。タワー共振破壊抑止優先：『ただし波浪ピッチング運動がタワー固有周期（0.12Hz）と完全同調している場合は、完全フリー空転を禁止し動的機械ブレーキによる微小制動抵抗を与えて構造共振を減衰させる』。",
            "瞬間風速が26.5m/sに達した。波浪動揺周期は0.04Hzで構造共振はない。ピッチ・制動制御を選択せよ。",
            "pitch_full_feather_free_idle",
            "瞬間風速が26.5m/sに達した。浮体ピッチングが0.12Hzでタワー固有共振と同調増幅している。ピッチ・制動制御を選択せよ。",
            "pitch_dynamic_brake_damping",
            [
                ("pitch_full_feather_free_idle", "フルフェザー空転待機"),
                ("pitch_dynamic_brake_damping", "動的ブレーキ共振減衰制動"),
                ("pitch_emergency_mechanical_lock", "機械ブレーキ完全ロック"),
                ("pitch_yaw_offset_steer", "ヨー旋回風向直交整定"),
            ],
        ),
    ]

    for pid, ctx, q1, t1, q2, t2, chs in k4_defs:
        choices = [{"id": cid, "text": ctxt} for cid, ctxt in chs]
        pairs.append({
            "pair_id": f"rc3_blind5_prio_{pid}",
            "family": "priority_exception",
            "k": 4,
            "case_1": {
                "id": f"rc3_blind5_prio_{pid}_s1",
                "group_id": f"rc3_blind5_prio_{pid}",
                "family": "priority_exception",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1},
            },
            "case_2": {
                "id": f"rc3_blind5_prio_{pid}_s2",
                "group_id": f"rc3_blind5_prio_{pid}",
                "family": "priority_exception",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2},
            },
        })

    # K=6: 5 pairs (26..30)
    k6_defs = [
        (
            "26",
            "重粒子線がん治療装置の照射安全インターロック規程。通常規程：『呼吸同期センサが呼気終末安定ウィンドウ（ゲート幅内）を検出したときビームゲートを開く』。患者変位即時遮断最優先：『ただし光学患者位置追従カメラが2mm以上の体動変位を検知した場合は、呼吸ゲート信号に関わらずビームゲートを即時非常遮断する』。",
            "呼吸同期センサは呼気安定ウィンドウ内を検出。体動追従カメラの変位量は0.4mmである。照射制御を選択せよ。",
            "beam_gate_open_irradiate",
            "呼吸同期センサは呼気安定ウィンドウ内を検出。しかし体動追従カメラが患者の体動変位2.7mmを検知した。照射制御を選択せよ。",
            "beam_gate_emergency_interlock_cut",
            [
                ("beam_gate_open_irradiate", "ビームゲート開・照射実行"),
                ("beam_gate_emergency_interlock_cut", "インターロック即時非常遮断"),
                ("beam_energy_degrade_step", "ビームエネルギー減衰待機"),
                ("beam_gantry_reposition_jog", "回転ガントリ再位置決め"),
                ("beam_calibration_phantom_run", "校正ファントム測定切替"),
                ("beam_accelerator_rf_stop", "高周波加速器完全停止"),
            ],
        ),
        (
            "27",
            "石油精製水素化脱硫プロセスのリサイクルガス圧縮機トリップ後シーケンス。通常規程：『圧縮機停止時は触媒コーキング防止のため速やかに加熱炉バーナーを最小燃焼へ絞る』。水素脆化破裂防止最優先：『ただし脱硫反応塔壁温度が脆性破壊遷移温度（150℃以下）まで降下しかつ水素分圧が高圧維持されている場合は、炉消火を阻止しパージ脱圧ベント弁全開を最優先して減圧する』。",
            "圧縮機トリップ停止。反応塔壁温度は280℃を保持している。加熱炉・ベント制御を選択せよ。",
            "furnace_burner_min_throttle",
            "圧縮機トリップ停止。反応塔壁温度が135℃まで低下しており水素高圧残留下で脆化リスクがある。加熱炉・ベント制御を選択せよ。",
            "vent_rapid_depressurize_priority",
            [
                ("furnace_burner_min_throttle", "加熱炉最小燃焼絞り"),
                ("vent_rapid_depressurize_priority", "消火阻止パージ急速減圧最優先"),
                ("furnace_emergency_steam_purge", "炉内スチーム窒息消火"),
                ("compressor_auxiliary_motor_start", "補助モーター即時起動"),
                ("quench_oil_flush_tower", "クエンチオイル緊急循環"),
                ("flare_header_isolation_valve_close", "フレア隔離弁全閉"),
            ],
        ),
        (
            "28",
            "極低温超電導リニアモーターカー浮上電磁石励磁規程。通常規程：『車上超電導磁石の永久電流スイッチ（PCS）は定常浮上走行時に閉路（持続電流モード）とする』。対向列車接近急減速優先：『ただし線路前方閉塞区間に先行列車接近警報を受信した場合は、持続電流モードを解除し外部地上推進コイル回生ブレーキへの高レート逆励磁電力を注入する』。",
            "時速500km/h定常巡航走行中。先行閉塞区間はクリアで軌道障害はない。超電導磁石制御を選択せよ。",
            "magnet_persistent_current_mode",
            "時速500km/h定常巡航走行中。前方閉塞区間に先行列車停止警報を受信し即時制動が要求された。超電導磁石制御を選択せよ。",
            "magnet_counter_excitation_regen",
            [
                ("magnet_persistent_current_mode", "永久電流持続モード維持"),
                ("magnet_counter_excitation_regen", "持続解除回生逆励磁注入"),
                ("magnet_quench_protection_dump", "保護抵抗緊急クエンチ放電"),
                ("magnet_cryostat_vent_gas", "クライオスタット気化放出"),
                ("magnet_mechanical_skid_drop", "機械式スキッド接地制動"),
                ("magnet_auxiliary_inverter_idle", "補助インバータ待機"),
            ],
        ),
        (
            "29",
            "原子力空調排気活性炭ホールドアップ塔の窒素パージ基準。通常規程：『排気放射能濃度が検出下限値以下の場合、通常外気ドラフト通風を継続する』。自然発火防止最優先：『ただし活性炭吸着ベッド内部温度センサが自己蓄熱（85℃以上）を検出した場合は、放射能測定値に関わらず通風弁を全閉遮断し窒素不活性ガス封入弁を全開する』。",
            "排気モニタの放射能レベルは検出限界未満。活性炭ベッド温度は32℃で安定。排気弁制御を選択せよ。",
            "carbon_bed_normal_draft_keep",
            "排気モニタの放射能レベルは検出限界未満。しかし活性炭内部温度が91℃に達し自己蓄熱発火兆候を示した。排気弁制御を選択せよ。",
            "carbon_bed_nitrogen_flood_close",
            [
                ("carbon_bed_normal_draft_keep", "通常外気ドラフト通風継続"),
                ("carbon_bed_nitrogen_flood_close", "通風全閉遮断窒素封入全開"),
                ("carbon_bed_water_deluge_spray", "炭酸ガス・水噴霧直接消火"),
                ("carbon_bed_bypass_filter_switch", "HEPAフィルターバイパス切替"),
                ("carbon_bed_exhaust_fan_boost", "排気ファン最大風量増速"),
                ("carbon_bed_vacuum_evacuate", "塔内真空引き脱気"),
            ],
        ),
        (
            "30",
            "超臨界地熱発電プラントの蒸気井減圧弁制御規程。通常規程：『蒸気セパレータ入側圧力が8.0MPaを超過した場合はバイパス減圧弁を徐開して圧力を整定する』。シリカスケール析出閉塞防止優先：『ただし蒸気温度が過熱度低下によりシリカ急析出危険域（230℃未満）に落ち込んだ場合は、減圧弁開放を禁止し塩酸スケール防止剤高圧注入弁を緊急全開する』。",
            "セパレータ入側圧力が8.4MPaに達した。蒸気温度は275℃で過熱蒸気域にある。減圧弁操作を選択せよ。",
            "geothermal_bypass_throttle_open",
            "セパレータ入側圧力が8.4MPaに達した。しかし地層湧水混入により蒸気温度が222℃まで低下しシリカ析出危機にある。減圧弁操作を選択せよ。",
            "geothermal_inhibit_valve_inhibitor_inject",
            [
                ("geothermal_bypass_throttle_open", "バイパス減圧弁徐開"),
                ("geothermal_inhibit_valve_inhibitor_inject", "減圧弁開阻止スケール防止剤注入"),
                ("geothermal_wellhead_master_shut", "生産井主坑口弁緊急全閉"),
                ("geothermal_condenser_vacuum_break", "復水器真空破壊"),
                ("geothermal_turbine_governor_trip", "タービンガバナートリップ"),
                ("geothermal_reinjection_pump_max", "還元井注水ポンプ最大加圧"),
            ],
        ),
    ]

    for pid, ctx, q1, t1, q2, t2, chs in k6_defs:
        choices = [{"id": cid, "text": ctxt} for cid, ctxt in chs]
        pairs.append({
            "pair_id": f"rc3_blind5_prio_{pid}",
            "family": "priority_exception",
            "k": 6,
            "case_1": {
                "id": f"rc3_blind5_prio_{pid}_s1",
                "group_id": f"rc3_blind5_prio_{pid}",
                "family": "priority_exception",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1},
            },
            "case_2": {
                "id": f"rc3_blind5_prio_{pid}_s2",
                "group_id": f"rc3_blind5_prio_{pid}",
                "family": "priority_exception",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2},
            },
        })

    return pairs
