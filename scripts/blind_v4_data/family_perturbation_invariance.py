"""Family 8: perturbation_invariance (30 pairs, 60 cases) - Blind v4
Distribution: K=8 (5 pairs), K=12 (10 pairs), K=16 (15 pairs)
Prefix: rc2b4_pert_
Zero inference during authoring; 100% fresh scenarios.
Concise choice texts for K=12 and K=16 to guarantee strict token count <= 350.
"""

from typing import Any, Dict, List, Tuple


def make_choices(c_defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in c_defs]


def get_perturbation_invariance_pairs() -> List[Dict[str, Any]]:
    pairs = []

    # --- K=8 (5 pairs: groups 01 to 05) ---
    k8_defs = [
        (
            "01",
            "港湾コンテナ埠頭における大型コンテナ船の係船索（係留ワイヤー）張力監視タスク。[環境ログ：気温18℃、南西の風4m/s、潮位干潮、港湾作業員無線交信良好]",
            "張力センサ所見：係船索の張力変動幅は許容荷重の28%で均等に負荷分散され、船舶動揺も極小である。荷役保安判定を行え。",
            "張力センサ所見：突風波浪により1番係船索に許容引張限度95%の過大サージ張力が連続印加され破断前兆を検知した。荷役保安判定を行え。",
            [
                ("mooring_tension_normal", "係留張力正常・荷役荷揚げ定常続行"),
                ("mooring_tension_alarm_stop", "係船索破断危険・荷役即時全面中止"),
                ("mooring_winch_free_wheel", "ウインチフリーホイール脱線"),
                ("mooring_anchor_drop_harbor", "港内錨地アンカー即時投錨"),
                ("mooring_tugboat_push_all", "タグボート全船最大出力押し付け"),
                ("mooring_fender_deflate", "空気式防舷材エアー緊急減圧"),
                ("mooring_bollard_bolt_torque", "係船柱ボルト手動再締結"),
                ("mooring_gangway_disconnect", "タラップ手動切り離し")
            ],
            "mooring_tension_normal", "mooring_tension_alarm_stop"
        ),
        (
            "02",
            "製薬工場注射用水（WFI）製造蒸留システムの純度インライン監視タスク。[付帯情報：ボイラー蒸気圧0.45MPa、循環ループ通水流量120L/min、外気清浄度正常]",
            "水質モニタ所見：25℃換算導電率は0.65μS/cm（薬局方基準1.3μS/cm以下）を満たし極めて清澄。WFI供給判定を行え。",
            "水質モニタ所見：蒸留塔コンデンサー微小ピンホールリークにより導電率が2.85μS/cmに急上昇した。WFI供給判定を行え。",
            [
                ("wfi_quality_pass_dispense", "WFI水質規格合格・製造ループ送水供給"),
                ("wfi_quality_fail_drain", "水質異常排水・供給遮断自動ブロー"),
                ("wfi_heat_exchanger_cold", "熱交換器冷水直接導入冷却"),
                ("wfi_nitrogen_seal_burst", "貯留タンク窒素シール急速破壊"),
                ("wfi_circulation_pump_stop", "循環ポンプ即時完全停止"),
                ("wfi_ozone_generator_boost", "オゾン発生器手動全負荷運転"),
                ("wfi_membrane_ultrafilter_clog", "限外ろ過膜バイパス全閉"),
                ("wfi_sampling_valve_jam", "サンプリング弁強制固着")
            ],
            "wfi_quality_pass_dispense", "wfi_quality_fail_drain"
        ),
        (
            "03",
            "新幹線総合試験車（ドクターイエロー）による軌道変位（高低狂い・通り狂い）の自動診断タスク。[測定時速270km/h、天候曇り、測定台車光学センサ作動中]",
            "検測結果：高低狂い+1.2mm、通り狂い+0.8mmであり、保守基準値（±7.0mm）を大幅に下回り極めて平滑。軌道保守判定を決定せよ。",
            "検測結果：道床バラスト緩みにより特定キロポストの高低狂いが+9.8mmを記録し、緊急保守基準を逸脱した。軌道保守判定を決定せよ。",
            [
                ("track_geometry_pass_nominal", "軌道狂い許容内・通常走行適合"),
                ("track_geometry_urgent_repair", "基準逸脱・軌道緊急保守保線手配"),
                ("track_speed_limit_20kph", "全列車徐行制限20km/h指令"),
                ("track_rail_grinding_full", "レール削正車全線手配"),
                ("track_tie_tamper_standby", "マルチプルタイタンパー夜間待機"),
                ("track_fastener_replace_all", "レール締結装置全数交換"),
                ("track_insulation_joint_cut", "絶縁継目板物理切断"),
                ("track_switch_lock_reverse", "分岐器定位鎖錠強制転換")
            ],
            "track_geometry_pass_nominal", "track_geometry_urgent_repair"
        ),
        (
            "04",
            "都市部下水道管網マンホールポンプ場の浸水防止自動制御タスク。[雨量レーダー予報：降水量毎時0mm、上流ポンプ正常稼働、臭気抑制装置オン]",
            "ポンプ井水位計：流入水位は基準LWL（低水位）付近を推移し、平常時乾候期流入量である。ポンプ運転を指示せよ。",
            "ポンプ井水位計：集中豪雨鉄砲水により流入水位がHWL（高水位警報線）を突破し満水警戒に達した。ポンプ運転を指示せよ。",
            [
                ("pump_run_routine_dry", "平常時間欠排水運転維持"),
                ("pump_run_storm_full_blast", "全排水ポンプ最大台数全開排水"),
                ("pump_isolate_screen_closed", "粗目除塵機スクリーン全閉"),
                ("pump_sediment_air_blast", "沈砂池エアーリフト強制停止"),
                ("pump_backwash_valve_open", "逆洗配管ドレン弁開放"),
                ("pump_power_transfer_solar", "太陽光パネル単独給電切替"),
                ("pump_generator_idle_test", "非常用エンジン無負荷暖機"),
                ("pump_sluice_gate_drop_down", "流入制水ゲート自重完全降下")
            ],
            "pump_run_routine_dry", "pump_run_storm_full_blast"
        ),
        (
            "05",
            "産業用窒素ガスPSA（圧力スイング吸着）発生装置の工程制御タスク。[供給空気コンプレッサ圧0.75MPa、露点マイナス40℃、分子篩吸着剤健全]",
            "プロセス計装：吸着塔内圧サイクル正常、出口窒素純度99.995%で製品タンクへ定常送ガス中。PSAサイクルを決定せよ。",
            "プロセス計装：脱着排気弁の弁座噛み込みにより塔内パージ不完全となり、出口窒素純度が94.0%へ急落した。PSAサイクルを決定せよ。",
            [
                ("psa_production_cycle_keep", "定常PSA吸着脱着サイクル継続"),
                ("psa_purity_alarm_offgas_vent", "純度低下警報・製品弁閉止オフガス放散"),
                ("psa_compressor_unloader_trip", "原料エアコンプレッサ無負荷停止"),
                ("psa_desiccant_heater_burn", "乾燥器ヒーター強制連続通電"),
                ("psa_adsorbent_vacuum_bake", "カーボンモレキュラーシーブ真空焼成"),
                ("psa_nitrogen_booster_stall", "窒素昇圧機手動減速"),
                ("psa_oxygen_analyzer_zero_cal", "ガルバニ電池酸素計強制校正"),
                ("psa_silencer_exhaust_damper", "消音器マフラー出口閉鎖")
            ],
            "psa_production_cycle_keep", "psa_purity_alarm_offgas_vent"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k8_defs:
        pairs.append({
            "id": f"rc2b4_pert_{gid}_s1", "group_id": f"rc2b4_pert_{gid}", "family": "perturbation_invariance",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_pert_{gid}_s2", "group_id": f"rc2b4_pert_{gid}", "family": "perturbation_invariance",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=12 (10 pairs: groups 06 to 15) Concise choices! ---
    k12_defs = [
        (
            "06",
            "航空機ターボファンエンジンFADEC制御。[飛行高度35,000ft、外気温度-50℃、対気速度M0.82]",
            "タービン計測：排気ガス温度（EGT）および回転数N1/N2は全て巡航制限値内。エンジン制御を決定せよ。",
            "タービン計測：燃料調量弁固着による過熱失速サージでEGTが限界値850℃を超過急上昇。エンジン制御を決定せよ。",
            [
                ("fadec_cruise_thrust_steady", "定常巡航推力供給維持"),
                ("fadec_fuel_cutoff_trip", "高圧燃料緊急遮断トリップ"),
                ("fadec_igniter_dual_continuous", "両系統点火プラグ連続放電"),
                ("fadec_vane_actuator_reverse", "可変静翼逆相駆動"),
                ("fadec_bleed_valve_slam_open", "圧縮機抽気弁急全開"),
                ("fadec_oil_scavenge_boost", "潤滑油回収ポンプ増速"),
                ("fadec_starter_generator_crank", "スターターモータ再始動"),
                ("fadec_thrust_reverser_deploy", "逆推力装置空中強制展開"),
                ("fadec_bypass_fan_lock", "ファンブレード電磁ロック"),
                ("fadec_hydraulic_pump_depress", "補機油圧ポンプアンロード"),
                ("fadec_fadec_channel_swap", "二重化FADECチャンネル切替"),
                ("fadec_fuel_filter_bypass", "燃料フィルター全バイパス")
            ],
            "fadec_cruise_thrust_steady", "fadec_fuel_cutoff_trip"
        ),
        (
            "07",
            "極低温液体水素燃料タンク断熱材保全。[地上待機中、周辺湿度60%、パージガス流量正常]",
            "真空ジャケット計装：真空度1.0×10^-4 Paを保ち、外壁結露ゼロ。タンク断熱制御を決定せよ。",
            "真空ジャケット計装：シール部微小リークにより真空度が1.0Paまで急落し外壁に激しい結氷発生。タンク断熱制御を決定せよ。",
            [
                ("lh2_tank_vacuum_steady", "高真空断熱性能維持"),
                ("lh2_tank_boil_off_vent", "気化ガス緊急減圧排気"),
                ("lh2_tank_pressurize_helium", "ヘリウム高圧加圧送液"),
                ("lh2_tank_dump_flare", "水素燃料全量フレア燃焼"),
                ("lh2_tank_fill_valve_burst", "充填配管逆止弁全開"),
                ("lh2_tank_heater_blanket_on", "電気加温ヒーター投入"),
                ("lh2_tank_slosh_baffle_shake", "防波板機械強制加振"),
                ("lh2_tank_inner_vessel_drain", "内槽水素急速ドレン"),
                ("lh2_tank_burst_disc_replace", "破裂板予備手動換装"),
                ("lh2_tank_capacitance_gauge_cut", "静電容量液面計遮断"),
                ("lh2_tank_vacuum_pump_restart", "真空ポンプ大気吸引"),
                ("lh2_tank_vacuum_jacket_flood", "外槽ジャケット注水冷却")
            ],
            "lh2_tank_vacuum_steady", "lh2_tank_boil_off_vent"
        ),
        (
            "08",
            "浮体式洋上風力発電セミサブ型バラスト制御。[波高2.5m、波周期8秒、係留チェーン張力適正]",
            "動揺計測ジャイロ：プラットフォーム傾斜角0.8度、動揺加速度は許容範囲内。バラスト制御を決定せよ。",
            "動揺計測ジャイロ：特定バラストタンク注排水弁故障による浸水で浮体傾斜が8.5度へ急激に傾斜。バラスト制御を決定せよ。",
            [
                ("floating_wind_ballast_keep", "定常バラスト水位維持"),
                ("floating_wind_counter_trim", "対向側急速注水トリム復原"),
                ("floating_wind_release_mooring", "係留索全軸一括緊急切断"),
                ("floating_wind_flood_all_tanks", "全区画自沈注水弁開放"),
                ("floating_wind_feather_turbine", "風車ブレード水平固定"),
                ("floating_wind_yaw_brake_free", "ナセル旋回フリー回転"),
                ("floating_wind_subsea_cable_jettison", "海底送電ケーブル投棄"),
                ("floating_wind_air_compressor_blow", "バラスト加圧排水ブロー"),
                ("floating_wind_bilge_pump_reverse", "ビルジポンプ逆相注水"),
                ("floating_wind_anchor_winch_haul", "アンカーウインチ最大巻込"),
                ("floating_wind_acoustic_transponder", "音響測位ピン送出停止"),
                ("floating_wind_navigation_buoy", "周囲航行ブイ消灯")
            ],
            "floating_wind_ballast_keep", "floating_wind_counter_trim"
        ),
        (
            "09",
            "メガワット級蓄電所リチウムイオンBMS熱管理。[外気30℃、SOC 80%、定格放電モード]",
            "セル温度テレメトリ：全セル温度差2.0℃以内、最高温度32.5℃で均一冷却。熱マネジメントを決定せよ。",
            "セル温度テレメトリ：特定ラック内セルが熱暴走前兆急昇温（毎分15℃上昇、現在85℃突破）を検知。熱マネジメントを決定せよ。",
            [
                ("bms_cooling_chiller_normal", "定格冷却水循環冷却維持"),
                ("bms_rack_fire_breaker_trip", "該当ラック直流遮断器遮断"),
                ("bms_discharge_max_current", "全容量強制短絡最大放電"),
                ("bms_heater_on_preheat", "セル予熱ヒーター全開"),
                ("bms_inverter_lead_lag_flip", "PCS力率急変極性反転"),
                ("bms_aerosol_extinguisher_fire", "消火エアロゾル全室放出"),
                ("bms_cell_bypass_transistor_short", "パッシブバランス短絡"),
                ("bms_can_bus_broadcast_mute", "通信バスパケット無音"),
                ("bms_high_voltage_interlock_cut", "高圧連動ループ強制切断"),
                ("bms_fan_duct_reverse_spin", "空調ダクト逆流排気"),
                ("bms_module_voltage_sense_off", "電圧検出回路基板遮断"),
                ("bms_ground_detector_bypass", "地絡検出リレー無効化")
            ],
            "bms_cooling_chiller_normal", "bms_rack_fire_breaker_trip"
        ),
        (
            "10",
            "鉄道架線（き電線）自動張力調整バランサー管理。[気温24℃、架線電流300A、通過列車なし]",
            "張力センサ所見：すずらん式バランサー重錘位置は適正中央で、架線張力19.6kNを維持。架線判定を行え。",
            "張力センサ所見：プーリー滑車ワイヤ破断により重錘が急落下し、架線張力が急激に半減喪失。架線判定を行え。",
            [
                ("catenary_tension_rated_ok", "架線定格張力適合維持"),
                ("catenary_wire_drop_alarm", "張力喪失事故警報発令"),
                ("catenary_power_short_rail", "架線レール間強制接地短絡"),
                ("catenary_substation_feeder_boost", "変電所送電電圧過大昇圧"),
                ("catenary_dropper_wire_cut", "ドロッパーワイヤー切断"),
                ("catenary_disconnect_switch_pull", "断路器通電中手動開放"),
                ("catenary_pantograph_scrape_test", "パンタグラフ摺動試験"),
                ("catenary_vibration_damper_strip", "ダンパー防振ウェイト撤去"),
                ("catenary_span_wire_shorten", "径間支持ワイヤ急短縮"),
                ("catenary_lightning_arrester_trip", "避雷器接地線切り離し"),
                ("catenary_messenger_wire_unwind", "ちょう架線撚り戻し"),
                ("catenary_feeder_loop_isolate", "き電区分所給電遮断")
            ],
            "catenary_tension_rated_ok", "catenary_wire_drop_alarm"
        ),
        (
            "11",
            "半導体超純水製造逆浸透（RO）膜分離プロセス。[給水水温20℃、回収率80%、供給ポンプ正常]",
            "差圧計モニタ：一次側二次側膜間差圧（TMP）は0.15MPaで膜目詰まりなし。RO運転を決定せよ。",
            "差圧計モニタ：微粒子スケーリング堆積により膜間差圧が0.42MPaに急上昇し透過流束が半減。RO運転を決定せよ。",
            [
                ("ro_membrane_flux_nominal", "定格高圧逆浸透分離継続"),
                ("ro_membrane_cip_clean_cycle", "造水停止・CIP薬品定置洗浄"),
                ("ro_membrane_feed_acid_shock", "塩酸ショック注入過負荷"),
                ("ro_membrane_permeate_backflush", "透過水側超高圧逆圧破壊"),
                ("ro_membrane_reject_valve_shut", "濃縮水排水弁完全閉塞"),
                ("ro_membrane_chlorine_disinfect", "遊離塩素直接注入浸漬"),
                ("ro_membrane_high_temp_steam", "高圧生蒸気直接滅菌"),
                ("ro_membrane_cartridge_filter_drop", "前段フィルターエレメント抜去"),
                ("ro_membrane_energy_recovery_stall", "エネルギー回収装置停止"),
                ("ro_membrane_decarbonate_tower_air", "脱炭酸塔送風ブロワー停止"),
                ("ro_membrane_ediser_bypass", "後段EDI装置バイパス"),
                ("ro_membrane_uv_lamp_extinguish", "殺菌用紫外線ランプ消灯")
            ],
            "ro_membrane_flux_nominal", "ro_membrane_cip_clean_cycle"
        ),
        (
            "12",
            "自律航行貨物船の海上衝突予防衝突回避ロジック。[視程良好、公海上、レーダーARPA稼働中]",
            "AISおよびレーダー追尾：他船との最接近距離（CPA）は5.2海里、最接近時間（TCPA）28分で余裕大。航行を決定せよ。",
            "AISおよびレーダー追尾：右舷前方15度より相手船が同一速力で反航接近中、CPA 0.1海里の衝突針路を算出。航行を決定せよ。",
            [
                ("colreg_maintain_course_speed", "現在針路および速力維持"),
                ("colreg_alter_course_starboard", "右舷大幅変針・衝突回避"),
                ("colreg_crash_stop_astern", "機関全速後進急制動停止"),
                ("colreg_alter_course_port_tight", "左舷緊急急変針回避"),
                ("colreg_drop_port_anchor_drift", "左舷アンカー海中投下"),
                ("colreg_extinguish_running_lights", "航海灯全消灯灯火管制"),
                ("colreg_rudder_hard_oscillation", "舵角最大周期往復運動"),
                ("colreg_sound_whistle_continuous", "汽笛長音連続永久吹鳴"),
                ("colreg_ais_transponder_power_off", "AIS発信機電源切断"),
                ("colreg_ballast_transfer_port", "左舷バラスト急速偏重移送"),
                ("colreg_satellite_comm_silence", "衛星通信無通信待機"),
                ("colreg_propeller_pitch_zero", "可変ピッチプロペラ中立")
            ],
            "colreg_maintain_course_speed", "colreg_alter_course_starboard"
        ),
        (
            "13",
            "道路トンネル内防災換気ジェットファン連動管理。[通行車両量中程度、CO濃度3ppm、煙霧透過率正常]",
            "環境センサ：視程測定器（VI計）透過率は95%、排気風速適正。換気ファン制御を決定せよ。",
            "環境センサ：トンネル内多重追突火災発生により煙濃度急増、透過率が15%に急落。換気ファン制御を決定せよ。",
            [
                ("tunnel_vent_routine_standby", "平常時低速換気待機維持"),
                ("tunnel_vent_emergency_smoke_purge", "火災排煙・後方高速排気送風"),
                ("tunnel_vent_reverse_all_fans", "全ファン逆転入口吸込"),
                ("tunnel_vent_shutoff_deluge_water", "スプリンクラー水消火遮断"),
                ("tunnel_vent_entry_barrier_open", "トンネル入口信号青開放"),
                ("tunnel_vent_evacuation_door_lock", "避難連絡坑扉電磁施錠"),
                ("tunnel_vent_lighting_off_black", "坑内非常照明全面消灯"),
                ("tunnel_vent_radio_rebroadcast_stop", "路側ラジオ再送信停止"),
                ("tunnel_vent_hydrant_pipe_drain", "消火栓配管全ドレン排水"),
                ("tunnel_vent_vms_display_blank", "情報表示板全消灯案内"),
                ("tunnel_vent_co_scrubber_bypass", "一酸化炭素吸着塔バイパス"),
                ("tunnel_vent_fan_vibration_ignore", "ファン軸受過大振動放置")
            ],
            "tunnel_vent_routine_standby", "tunnel_vent_emergency_smoke_purge"
        ),
        (
            "14",
            "重質油水素化脱硫反応塔の温度暴走インターロック。[水素分圧12MPa、触媒層循環正常、LHSV適正]",
            "触媒層多点熱電対：各ベッド間温度差は8℃以内で均一な脱硫発熱を制御中。反応制御を指示せよ。",
            "触媒層多点熱電対：第2触媒層で急激な局所発熱ホットスポット（450℃突破・毎分30℃昇温）を検出。反応制御を指示せよ。",
            [
                ("desulfur_steady_reaction_run", "定常温度水素化脱硫反応維持"),
                ("desulfur_cold_quench_hydrogen_max", "緊急水素クエンチ弁全開急冷"),
                ("desulfur_raw_oil_feed_double", "重質油原料供給量倍増投入"),
                ("desulfur_steam_reformer_cut", "水素製造プラント即時停止"),
                ("desulfur_recycle_compressor_stop", "循環コンプレッサ即時停止"),
                ("desulfur_catalyst_dump_hopper", "触媒高温燃焼落下投下"),
                ("desulfur_separator_liquid_vent", "高圧気液分離器高圧ドレン"),
                ("desulfur_offgas_amine_scrubber_stop", "アミン洗浄塔停止"),
                ("desulfur_reactor_air_bleed", "反応塔内部大気空気導入"),
                ("desulfur_sulfiding_agent_inject", "予備硫化剤直接急速注入"),
                ("desulfur_furnace_damper_close", "加熱炉排煙ダンパー密閉"),
                ("desulfur_guard_bed_bypass", "ガードリアクター完全遮断")
            ],
            "desulfur_steady_reaction_run", "desulfur_cold_quench_hydrogen_max"
        ),
        (
            "15",
            "電力系統周波数維持事故波及防止リレー（UFR）運用。[系統容量50Hz、基底電源安定、連系線潮流適正]",
            "周波数リレー計測値：母線周波数は50.01Hzで安定、周波数低下率（df/dt）ゼロ。系統制御を指示せよ。",
            "周波数リレー計測値：基幹大型発電所（100万kW）急停止により周波数が48.60Hzへ急落中。系統制御を指示せよ。",
            [
                ("grid_frequency_healthy_maintain", "全系統定格給電連系維持"),
                ("grid_ufr_load_shedding_act", "UFR周波数低下負荷緊急遮断"),
                ("grid_pumped_storage_pump_start", "揚水発電所揚水動力全開投入"),
                ("grid_tie_line_disconnect_instant", "他社地域間連系線即時解列"),
                ("grid_substation_capacitor_trip", "電力用コンデンサ一斉開放"),
                ("grid_generator_governor_lock", "全発電機調速機手動ロック"),
                ("grid_solar_inverter_curtail_zero", "全太陽光PCS一括出力抑制"),
                ("grid_busbar_tie_breaker_open", "母線連絡遮断器全面開放"),
                ("grid_synchronous_condenser_stop", "同期調相機界磁強制遮断"),
                ("grid_black_start_diesel_fire", "全停時非常復旧電源起動"),
                ("grid_voltage_tap_change_low", "変圧器タップ急激降圧"),
                ("grid_static_var_compensator_off", "無効電力補償装置停止")
            ],
            "grid_frequency_healthy_maintain", "grid_ufr_load_shedding_act"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k12_defs:
        pairs.append({
            "id": f"rc2b4_pert_{gid}_s1", "group_id": f"rc2b4_pert_{gid}", "family": "perturbation_invariance",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_pert_{gid}_s2", "group_id": f"rc2b4_pert_{gid}", "family": "perturbation_invariance",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=16 (15 pairs: groups 16 to 30) Concise choices! ---
    k16_defs = [
        (
            "16",
            "原子力発電所非常用炉心冷却設備（ECCS）待機判定。[定格熱出力100%、原子炉圧力7.0MPa、水位正常]",
            "安全保護系ロジック：冷却材喪失事故（LOCA）兆候なし、格納容器圧力正常。ECCS制御を決定せよ。",
            "安全保護系ロジック：主蒸気管破断により原子炉水位低下および格納容器圧力高（第1トリップ信号）が成立。ECCS制御を決定せよ。",
            [
                ("eccs_standby_ready_keep", "ECCS自動待機待機状態維持"),
                ("eccs_high_pressure_cool_start", "高圧炉心注水系HPCI自動起動"),
                ("eccs_low_pressure_spray_start", "低圧炉心スプレー系LPCS起動"),
                ("eccs_auto_depressurize_valves", "逃がし安全弁自動減圧ADS開"),
                ("eccs_residual_heat_remove_cool", "残留熱除去系RHR海水冷却"),
                ("eccs_containment_spray_actuate", "格納容器スプレイ薬液注入"),
                ("eccs_diesel_generator_emergency", "非常用ディーゼル給電起動"),
                ("eccs_boron_standby_liquid_pump", "ほう酸水注入ポンプ起動"),
                ("eccs_isolate_clean_up_system", "原子炉冷却材浄化系遮断"),
                ("eccs_main_steam_isolate_close", "主蒸気隔離弁MSIV全閉"),
                ("eccs_feedwater_pump_high_trip", "主給水ポンプ非常トリップ"),
                ("eccs_recirculation_pump_trip", "原子炉再循環ポンプ停止"),
                ("eccs_control_rod_scram_verify", "全制御棒全挿入緊急確認"),
                ("eccs_torus_water_cooling_mode", "サプレッションプール冷却"),
                ("eccs_standby_gas_treatment_run", "非常用ガス処理系換気運転"),
                ("eccs_vent_hardened_pipe_open", "耐圧強化ベント弁強制全開")
            ],
            "eccs_standby_ready_keep", "eccs_high_pressure_cool_start"
        ),
        (
            "17",
            "大型液体燃料ロケット第1段推進薬充填シークエンス。[打上げカウントダウンT-60分、天候晴れ]",
            "地上充填テレメトリ：液体酸素（LOX）および液体水素（LH2）充填配管圧・温度健全。充填制御を指示せよ。",
            "地上充填テレメトリ：打上げ機体側充填アンビリカルコネクタから極低温水素ガス漏洩アラーム（爆発下限界突破）が発生。充填制御を指示せよ。",
            [
                ("launch_propellant_fill_run", "極低温推進薬充填シーケンス継続"),
                ("launch_abort_drain_purge", "カウントダウン緊急停止・排出掃気"),
                ("launch_fire_main_engines", "第1段メインエンジン即時点火"),
                ("launch_pyro_holddown_release", "射点固定クランプ火工品解除"),
                ("launch_pressurize_tank_helium", "推進薬タンク高圧ヘリウム加圧"),
                ("launch_chilldown_engine_turbopump", "エンジンターボポンプ極低温予冷"),
                ("launch_ignite_solid_boosters", "固体ロケットブースター点火"),
                ("launch_deploy_payload_fairing", "衛星フェアリング射点開放"),
                ("launch_internal_battery_switch", "機体内蔵バッテリ給電切替"),
                ("launch_inertial_guidance_align", "慣性誘導ジャイロ最終アライメント"),
                ("launch_ground_water_deluge_spray", "消音放水サイレントスプレイ噴射"),
                ("launch_vent_arm_retract_swing", "頂部ベントアーム退避旋回"),
                ("launch_telemetry_transmitter_boost", "テレメトリ送信機ハイパワー切替"),
                ("launch_destruct_package_arm", "指令破壊システム安全プラグ装填"),
                ("launch_payload_air_condition_off", "衛星フェアリング空調給気停止"),
                ("launch_ground_power_cable_drop", "外部地上電源アンビリカル自重離脱")
            ],
            "launch_propellant_fill_run", "launch_abort_drain_purge"
        ),
        (
            "18",
            "超伝導3.0テスラMRI診断装置の磁場励磁ヘリウム管理。[検査待機中、RFシールドルーム密閉良好]",
            "クライオ計装モニタ：液体ヘリウム残量92%、冷媒回収コンプレッサー正常動作。MRI装置制御を決定せよ。",
            "クライオ計装モニタ：超伝導マグネットコイル内部でホットスポット局所過熱が発生、急速クエンチ気化圧力が安全弁を押し開いた。MRI装置制御を決定せよ。",
            [
                ("mri_magnet_field_stable", "静磁場励磁スキャン待機維持"),
                ("mri_quench_exhaust_vent_run", "クエンチ緊急排気ダクト全開"),
                ("mri_gradient_amplifier_overdrive", "傾斜磁場アンプ最大過駆動"),
                ("mri_rf_body_coil_transmit", "RFボディコイル高出力照射"),
                ("mri_shim_coil_current_zero", "シムコイル補正電流遮断"),
                ("mri_patient_table_fast_eject", "患者寝台最高速強制引抜"),
                ("mri_helium_compressor_power_off", "ヘリウム冷凍コンプレッサ停止"),
                ("mri_chilled_water_circulate_max", "傾斜磁場冷却水最大循環"),
                ("mri_faraday_cage_door_interlock", "電磁シールド扉緊急ロック"),
                ("mri_acoustics_noise_canceller_on", "能動騒音キャンセラー起動"),
                ("mri_ecg_gating_pulse_sync", "心電図同期トリガー取得"),
                ("mri_docking_station_battery_charge", "移動式寝台充電ドックイン"),
                ("mri_laser_localizer_cross_light", "位置決めレーザー投光点灯"),
                ("mri_emergency_power_off_mushroom", "赤色キノコ型非常停止押下"),
                ("mri_pickup_coil_preamp_tune", "受信アレイコイル同調調整"),
                ("mri_dewar_burst_disk_replate", "圧力開放弁封入プレート換装")
            ],
            "mri_magnet_field_stable", "mri_quench_exhaust_vent_run"
        ),
        (
            "19",
            "ハイパーコンバージドインフラ（HCI）分散ストレージクラスタ管理。[ノード数16台、ネットワーク健全]",
            "クラスタヘルスモニタ：データ整合性チェックサム合格、全ディスクレプリカは三重化同期を維持。ストレージ制御を決定せよ。",
            "クラスタヘルスモニタ：スプリットブレイン発生によりクラスタ心拍分断、クォーラム喪失でデータ競合破壊の危機。ストレージ制御を決定せよ。",
            [
                ("hci_storage_sync_nominal", "分散ボリューム定常書込継続"),
                ("hci_quorum_fence_isolate", "クォーラム不整合ノード隔離フェンシング"),
                ("hci_format_all_nvme_disks", "全NVMeストレージ強制初期化"),
                ("hci_rebuild_parity_resync", "パリティ再同期リビルド実行"),
                ("hci_migrate_vm_live_motion", "稼働中仮想マシンライブマイグレーション"),
                ("hci_expand_cluster_add_node", "新規追加ノード自動プロビジョニング"),
                ("hci_dedup_compression_engine_run", "重複排除圧縮バックグラウンド処理"),
                ("hci_snapshot_rollback_latest", "最新整合性スナップショット復元"),
                ("hci_rdma_roce_traffic_throttle", "RDMA帯域輻輳制御スロットリング"),
                ("hci_storage_cache_flush_ram", "不揮発性キャッシュ全フラッシュ"),
                ("hci_witness_server_failover", "外部監視ウィットネスサーバー切替"),
                ("hci_rebalance_storage_capacity", "ディスク容量自動平準化リバランス"),
                ("hci_firmware_rolling_upgrade", "SSDファームウェアローリング更新"),
                ("hci_scrub_silent_corruption", "サイレントデータ破壊自動修復"),
                ("hci_block_storage_target_export", "iSCSIターゲット外部エクスポート"),
                ("hci_chassis_power_off_cluster", "シャーシ主電源一括強制遮断")
            ],
            "hci_storage_sync_nominal", "hci_quorum_fence_isolate"
        ),
        (
            "20",
            "超高層スマートビルBEMS（ビルエネルギー管理システム）熱源最適化。[外気温26℃、全館冷房負荷適正]",
            "熱源設備モニタ：氷蓄熱槽からの冷水供給と高効率インバータチラーの協調運転が計画通り推移。熱源制御を決定せよ。",
            "熱源設備モニタ：主冷水循環配管の溶接フランジ破断により大量の冷水が機械室に噴出し、系統圧力がゼロへ急落。熱源制御を決定せよ。",
            [
                ("bems_thermal_storage_optimal_run", "氷蓄熱高効率協調冷房運転継続"),
                ("bems_pipe_burst_isolation_trip", "冷水ポンプ緊急停止・破断区画遮断弁閉"),
                ("bems_start_absorption_chiller_gas", "都市ガス直焚き吸収式冷凍機追加"),
                ("bems_cooling_tower_fan_step_up", "冷却塔ファン回転数強制全開"),
                ("bems_heat_pump_hot_water_boost", "給湯用ヒートポンプフル稼働"),
                ("bems_ahu_inverter_speed_minimum", "各階空調機インバータ最小風量"),
                ("bems_free_cooling_outside_air", "外気冷房エコノマイザ全開導入"),
                ("bems_demand_controller_shed_sub", "契約電力デマンド監視非重要負荷遮断"),
                ("bems_secondary_pump_variable_flow", "二次ポンプ変流量制御追従"),
                ("bems_expansion_tank_fill_water", "密閉式膨張タンク純水自動補給"),
                ("bems_chemical_dosing_scale_prevent", "防食防スケール剤自動薬注"),
                ("bems_steam_boiler_pilot_ignite", "蒸気ボイラー点火パイロット点火"),
                ("bems_plate_heat_exchanger_bypass", "プレート式熱交換器全バイパス"),
                ("bems_chilled_water_crossover_valve", "冷温水ヘッダー連絡弁開放"),
                ("bems_exhaust_heat_recovery_run", "マイクロガスタービン排熱回収"),
                ("bems_drain_sump_pump_emergency", "地下機械室ピット湧水ポンプ起動")
            ],
            "bems_thermal_storage_optimal_run", "bems_pipe_burst_isolation_trip"
        ),
        (
            "21",
            "自律走行長距離大型フルトレーラートラックの隊列走行制御。[高速道路クルーズ中、車間距離15m、晴天]",
            "車載センサフュージョン：ミリ波レーダー、LiDAR、カメラ全て正常。前走車と協調追従通信中。走行制御を決定せよ。",
            "車載センサフュージョン：路面落下物との接触により右前操舵輪の空気圧が瞬間バーストゼロ喪失。走行制御を決定せよ。",
            [
                ("truck_platooning_cruise_keep", "車間15m電子連結隊列自動追従維持"),
                ("truck_tire_blowout_safe_stop", "隊列離脱・非常ハザード点滅緊急路肩退避停車"),
                ("truck_accelerate_pass_overtake", "追越車線進出自動追い越し加速"),
                ("truck_decelerate_fall_back_far", "隊列解除・一般車間距離60m後退"),
                ("truck_steer_evasive_slalom", "障害物スラローム急回避操舵"),
                ("truck_trailer_coupling_pin_pull", "トレーラーカプラー走行中緊急分離"),
                ("truck_exhaust_brake_retarder_full", "排気ブレーキリターダー満制動"),
                ("truck_air_suspension_height_dump", "エアサスペンション車高全落とし"),
                ("truck_inter_axle_diff_lock_on", "軸間デフロック強制直結投入"),
                ("truck_v2v_dsrc_mesh_retransmit", "車車間通信パケット中継再送"),
                ("truck_horn_air_blast_continuous", "高圧エアホーン緊急警笛吹鳴"),
                ("truck_fuel_tank_selector_switch", "予備燃料タンク燃料切替"),
                ("truck_windshield_washer_spray", "フロントガラスウォッシャー噴射"),
                ("truck_headlight_high_beam_flash", "パッシングハイビーム警告点滅"),
                ("truck_battery_cutoff_relay_open", "メインバッテリー遮断リレー開放"),
                ("truck_cab_tilt_hydraulics_unlock", "キャブチルト油圧ロック解除")
            ],
            "truck_platooning_cruise_keep", "truck_tire_blowout_safe_stop"
        ),
        (
            "22",
            "大陸間光海底ケーブル光増幅中継器（リピーター）の直列高圧定電流給電管理。[水深5,000m、給電線440mA]",
            "陸上陸揚局給電装置モニタ：全120基の中継器端子電圧およびエルビウム添加光ファイバ増幅器利得は定格安定。給電制御を決定せよ。",
            "陸上陸揚局給電装置モニタ：沖合200km地点で海底地滑りによるケーブル完全断線事故（受電電圧ゼロ・開放地絡）が発生。給電制御を決定せよ。",
            [
                ("submarine_repeater_feed_steady", "定電流440mA高圧連続給電維持"),
                ("submarine_cable_cut_earth_loop", "断線検出・片端給電接地ループへ自動切替"),
                ("submarine_increase_current_1a", "給電電流1.0A強制過大増幅"),
                ("submarine_laser_pump_diode_kill", "励起半導体レーザー全停止"),
                ("submarine_otdr_fault_locate_shot", "コヒーレントOTDR断線位置測距パルス"),
                ("submarine_polarity_reversal_test", "給電電圧直流極性急速反転"),
                ("submarine_supervisory_tone_modulate", "中継器監視トーン周波数変調"),
                ("submarine_gain_equalizer_tune", "光利得等化器動的チルト補正"),
                ("submarine_branching_unit_switch", "海底分岐装置光パス切替"),
                ("submarine_cable_ship_beacon_fire", "敷設船誘導音響ピン発信"),
                ("submarine_shore_terminal_bypass", "陸揚局終端伝送装置バイパス"),
                ("submarine_wavelength_add_drop", "ROADM光波長直接挿入分岐"),
                ("submarine_dispersion_fiber_spool", "波長分散補償ファイバ投入"),
                ("submarine_optical_attenuation_step", "受光アッテネータ動的減衰"),
                ("submarine_surge_protection_zener", "ツェナーダイオード過電圧バイパス"),
                ("submarine_chassis_ground_lift", "局内通信用アース絶縁浮かし")
            ],
            "submarine_repeater_feed_steady", "submarine_cable_cut_earth_loop"
        ),
        (
            "23",
            "製鉄所高炉（溶鉱炉）の出銑口開孔・閉塞マッドガン操業管理。[銑鉄温度1,520℃、炉内圧0.28MPa、出銑中]",
            "炉前作業計装モニタ：出銑樋を流れる溶銑・スラグの流速・温度安定、開孔部損耗なし。出銑口制御を決定せよ。",
            "炉前作業計装モニタ：出銑終了予定時刻到達、または出銑口周囲カーボン耐火煉瓦の異常侵食兆候を検知。出銑口制御を決定せよ。",
            [
                ("blast_furnace_tapping_keep_open", "溶銑樋への定常出銑流下継続"),
                ("blast_furnace_mud_gun_plug_tap", "マッドガン旋回前進・耐火マッド材高圧圧入閉塞"),
                ("blast_furnace_drill_open_taphole", "開孔削岩ドリル前進打撃開孔"),
                ("blast_furnace_oxygen_lance_burn", "高圧酸素ランス直接吹込み溶断"),
                ("blast_furnace_trough_cover_lift", "出銑樋集塵フードホイスト巻上"),
                ("blast_furnace_slag_skimmer_adjust", "スラグ分離スキンマーゲート調整"),
                ("blast_furnace_tuyere_inject_pulverized", "羽口微粉炭吹込み量倍増"),
                ("blast_furnace_blast_air_moisture_cut", "送風高圧空気調湿蒸気停止"),
                ("blast_furnace_bell_top_dump_coke", "炉頂ベル原料コークス装入"),
                ("blast_furnace_stave_cool_water_boost", "冷却ステーブ注水流量最大"),
                ("blast_furnace_torpedo_car_switch", "トーピードカー受銑鍋台車転線"),
                ("blast_furnace_tilting_runner_flip", "傾注樋反転反対側出銑樋送湯"),
                ("blast_furnace_snort_valve_open", "送風バイパス大気放風弁急開"),
                ("blast_furnace_gas_cleaning_venturi", "高炉ガス洗浄ベンチュリ水圧調整"),
                ("blast_furnace_throat_camera_purge", "炉口カメラ窒素パージ掃気"),
                ("blast_furnace_hearth_thermocouple_cal", "炉底熱電対起電力再較正")
            ],
            "blast_furnace_tapping_keep_open", "blast_furnace_mud_gun_plug_tap"
        ),
        (
            "24",
            "商用大型水素ステーションの超高圧ダイヤフラム圧縮機（82MPa級）監視。[吸気圧力20MPa、吐出目標82MPa]",
            "圧縮機計装モニタ：各段ピストン間多段インタークーラー温度・油圧・振動値すべて正常。圧縮機運転を決定せよ。",
            "圧縮機計装モニタ：第3段金属ダイヤフラム隔膜の微小疲労亀裂を検知（油側水素検知センサ作動）。圧縮機運転を決定せよ。",
            [
                ("compressor_82mpa_run_steady", "多段ダイヤフラム超高圧水素圧縮継続"),
                ("compressor_diaphragm_rupture_trip", "隔膜破損異常トリップ・緊急全系減圧停止"),
                ("compressor_bypass_recycle_open", "アンローダー圧縮機内部バイパス"),
                ("compressor_inlet_gas_suction_boost", "吸入水素バッファタンク昇圧"),
                ("compressor_crankcase_oil_drain", "クランクケース潤滑油全排水"),
                ("compressor_nitrogen_purge_piping", "高圧水素配管不活性窒素置換"),
                ("compressor_pulse_damper_bleed", "脈動防止アキュムレータガス抜き"),
                ("compressor_water_jacket_chiller_drop", "ジャケット冷水供給停止"),
                ("compressor_safety_relief_lift_hand", "82MPa安全逃がし弁手動開放"),
                ("compressor_motor_vfd_speed_max", "防爆インバータ最高周波数駆動"),
                ("compressor_oil_mist_separator_clean", "油分捕集セパレータ逆洗"),
                ("compressor_suction_strainer_blow", "吸込ストレーナー残渣ブロー"),
                ("compressor_dispenser_bank_switch", "高圧蓄圧器バンク切替充填"),
                ("compressor_hydrogen_chiller_precool", "水素プレクーラー急冷マイナス40℃"),
                ("compressor_emergency_depress_flare", "フレアスタック緊急放出大気放散"),
                ("compressor_fire_deluge_foam_spray", "防消火水成膜泡消火薬剤放射")
            ],
            "compressor_82mpa_run_steady", "compressor_diaphragm_rupture_trip"
        ),
        (
            "25",
            "臼田・美笹級大型深宇宙探査用パラボラアンテナ（口径64m）の微弱電波自動追尾。[目標天体：木星探査機、Xバンド/Kaバンド]",
            "アンテナ管制モニタ：モノパルス方式電波到来角追尾誤差0.002度、超伝導極低温低雑音増幅器（LNA）利得良好。追尾指示を決定せよ。",
            "アンテナ管制モニタ：突発局地突風（瞬間風速22m/s）を風速計が検知し、主反射鏡構造歪み警戒レベルを超過。追尾指示を決定せよ。",
            [
                ("antenna_spacecraft_monopulse_track", "深宇宙電波高精度自動モノパルス追尾継続"),
                ("antenna_wind_stow_lockdown", "追尾中止・主反射鏡天頂真上固定ロック（Stow）"),
                ("antenna_azimuth_drive_max_slew", "方位角アジマス軸最高速全周旋回"),
                ("antenna_elevation_drive_zero_flat", "仰角エレベーション水平真横指向"),
                ("antenna_subreflector_focus_sweep", "副反射鏡可動機構焦点スイープ"),
                ("antenna_cryo_lna_refrigerator_warm", "LNA冷却ヘリウム圧縮機停止昇温"),
                ("antenna_transmitter_klystron_high", "アップリンク用クライストロン高出力照射"),
                ("antenna_feed_horn_band_select_rotate", "フィードホーンKaバンド受光ターレット回転"),
                ("antenna_deicing_hot_air_blower_run", "主鏡着雪防止温風ブロワー全開"),
                ("antenna_optical_telescope_collimation", "同軸光学望遠鏡恒星コリメーション"),
                ("antenna_rail_wheel_brake_manual_free", "円形走行台車レールブレーキ手動解放"),
                ("antenna_polarization_rotator_flip", "円偏波左右旋偏波手動反転"),
                ("antenna_counterweight_lead_drop", "釣合カウンターウェイト緊急分離"),
                ("antenna_rotary_joint_cable_unwind", "同軸ロータリージョイントケーブル巻戻し"),
                ("antenna_ground_hydrogen_maser_sync", "水素メーザー原子時計外部同期切替"),
                ("antenna_signal_spectrum_correlator", "デジタル相関器サンプリング積算開始")
            ],
            "antenna_spacecraft_monopulse_track", "antenna_wind_stow_lockdown"
        ),
        (
            "26",
            "医薬品バイアル無菌充填アイソレータ内部のロボット充填工程管理。[無菌クリーン度ISOクラス1、過酸化水素除染済]",
            "環境環境モニタ：アイソレータ内陽圧+45Pa維持、パーティクルカウンタ微粒子数0個、充填針正常動作。充填ライン制御を決定せよ。",
            "環境環境モニタ：作業グローブポートのゴム裂け微小破損により室内差圧がゼロへ消失し外気混入アラーム発生。充填ライン制御を決定せよ。",
            [
                ("isolator_sterile_fill_run", "定常無菌分注充填キャッピング継続"),
                ("isolator_seal_breach_abort", "無菌性喪失・ライン即時緊急停止ロット隔離"),
                ("isolator_vhps_decontam_cycle_start", "過酸化水素ガス循環自動除染開始"),
                ("isolator_exhaust_hepa_filter_purge", "排気HEPAフィルター最大吸引排気"),
                ("isolator_needle_dosing_pump_reverse", "定量セラミック充填ポンプ逆回転"),
                ("isolator_stopper_bowl_vibrate_max", "ゴム栓パーツフィーダー過大加振"),
                ("isolator_conveyor_star_wheel_drop", "スターホイール搬送ギア手動空転"),
                ("isolator_uv_sterilization_light_on", "内部UV殺菌灯自動点灯照射"),
                ("isolator_nitrogen_purge_sparge_boost", "バイアル窒素置換ノズル噴射倍増"),
                ("isolator_capping_roller_torque_free", "アルミキャップ巻締めトルクゼロ解除"),
                ("isolator_loadcell_weight_tare_zero", "インライン電子天秤動的風袋引き"),
                ("isolator_chamber_interlock_door_force", "パスボックス出入口扉強制開放"),
                ("isolator_cleaning_pure_water_spray", "CIP純水スプレーシャワー全開"),
                ("isolator_glove_leak_tester_inflate", "グローブリークテスター空気圧測定"),
                ("isolator_conveyor_reject_gate_flip", "不適バイアルリジェクトゲート転換"),
                ("isolator_ambient_air_blower_direct", "一般外気ファン直接吸込開放")
            ],
            "isolator_sterile_fill_run", "isolator_seal_breach_abort"
        ),
        (
            "27",
            "大規模系統連系蓄電池システム（BESS）のアンシラリーサービス高速周波数応答（FFR）。[系統連系端50.0Hz、待機中]",
            "系統検出器テレメトリ：系統周波数50.00Hz、電圧変動なし、給電指令待機電力正常。BESS制御を指示せよ。",
            "系統検出器テレメトリ：送電線落雷多重事故に伴う広域停電により系統周波数が49.30Hzに急落（低下限界到達）。BESS制御を指示せよ。",
            [
                ("bess_grid_support_standby", "グリッド連系待機維持"),
                ("bess_ffr_emergency_discharge_max", "全PCS高速放電最大出力周波数緊急支援"),
                ("bess_absorb_over_frequency_charge", "過周波数抑制最大急速充電吸い込み"),
                ("bess_disconnect_island_microgrid", "解列単独運転移行アイランド形成"),
                ("bess_reactive_power_var_inject", "無効電力進相供給電圧昇圧"),
                ("bess_static_switch_bypass_cut", "半導体高速スイッチ完全遮断"),
                ("bess_battery_container_aircon_max", "蓄電コンテナ空調最大冷却"),
                ("bess_insulation_resistance_meter_test", "絶縁抵抗測定回路自動テスト"),
                ("bess_black_start_generator_sync", "ブラックスタート非常発電機同期"),
                ("bess_transformer_tap_step_down", "連系変圧器タップ降圧"),
                ("bess_grounding_transformer_open", "接地変圧器中性点遮断"),
                ("bess_modbus_rtu_timeout_reset", "監視制御通信タイムアウトリセット"),
                ("bess_harmonic_filter_bank_trip", "高調波フィルターバンク開放"),
                ("bess_cell_balancing_resistor_heat", "ブリーダ放電抵抗全通電"),
                ("bess_emergency_dc_contactors_pull", "全ストリング主電磁接触器強制開放"),
                ("bess_smoke_detector_halon_dump", "コンテナ内ハロン消火設備起動")
            ],
            "bess_grid_support_standby", "bess_ffr_emergency_discharge_max"
        ),
        (
            "28",
            "航空宇宙炭素繊維複合材（CFRP）の大型産業用高分解能X線CT非破壊検査。[管電圧225kV、焦点寸法3μm、回転台正常]",
            "検査画像再構成プロセッサ：X線受光量適正、ボクセル分解能5μm、アーティファクトなし。CTスキャン制御を決定せよ。",
            "検査画像再構成プロセッサ：X線照射室の安全防護鉛扉のリミットスイッチが誤作動開放接点を検知。CTスキャン制御を決定せよ。",
            [
                ("xray_ct_scan_continue_acquire", "3次元透過画像データ収集スキャン継続"),
                ("xray_interlock_shutter_trip_off", "被ばく防止インターロック・X線高圧即時遮断"),
                ("xray_tube_filament_preheat_max", "X線管フィラメント予熱過電流"),
                ("xray_flat_panel_detector_gain_high", "フラットパネル検出器ゲイン過大増幅"),
                ("xray_rotary_stage_spin_uncontrolled", "精密回転ステージ無制御高速回転"),
                ("xray_oil_cooling_pump_shutdown", "ターゲット油冷ポンプ停止"),
                ("xray_target_tungsten_tilt_angle", "タングステンターゲット角度急傾斜"),
                ("xray_collimator_slits_shut_blind", "コリメータスリット完全閉口遮光"),
                ("xray_filter_copper_plate_drop", "散乱線除去銅フィルター落下"),
                ("xray_lead_glass_window_shatter", "鉛ガラス観察窓機械的粉砕"),
                ("xray_sample_manipulator_home_seek", "試料把持アーム原点復帰動作"),
                ("xray_radiation_area_monitor_alarm", "管理区域外放射線警報サイレン吹鳴"),
                ("xray_laser_centering_pointer_off", "中心位置決め赤色レーザー消灯"),
                ("xray_high_voltage_generator_crowbar", "高圧発生器クローバー放電"),
                ("xray_reconstruction_gpu_cluster_reboot", "画像再構成GPUクラスタ再起動"),
                ("xray_lead_shield_curtain_retract", "放射線防護鉛のれん強制巻取")
            ],
            "xray_ct_scan_continue_acquire", "xray_interlock_shutter_trip_off"
        ),
        (
            "29",
            "都市高速道路長大トンネルの進入照明・坑内照明適応調光制御。[トンネル坑口外照度80,000ルクス（真夏の直射日光）]",
            "照度センサ測定：野外輝度計と連動し、明暗順応のための野外追従調光モードが正常稼働中。調光制御を決定せよ。",
            "照度センサ測定：受電所停電事故により常用電源が喪失し、トンネル内主要調光回路の全給電が遮断。調光制御を決定せよ。",
            [
                ("tunnel_lighting_adaptive_bright", "明暗順応インバータ高照度調光点灯維持"),
                ("tunnel_lighting_ups_emergency_lights", "停電検出・無瞬断UPS蓄電池非常灯点灯"),
                ("tunnel_lighting_all_circuits_blackout", "全坑内照明即時完全消灯"),
                ("tunnel_lighting_low_beam_night_mode", "深夜用減光省エネ低照度点灯"),
                ("tunnel_lighting_evacuation_strobe_flash", "非常口誘導緑色ストロボ点滅"),
                ("tunnel_lighting_portal_deluge_spray", "トンネル坑口散水設備起動"),
                ("tunnel_lighting_high_mast_lamp_raise", "坑口外高ポール照明柱上昇"),
                ("tunnel_lighting_solar_cell_inverter_run", "太陽光発電インバータ給電"),
                ("tunnel_lighting_dali_bus_broadcast_reset", "DALI照明通信バスリセット"),
                ("tunnel_lighting_light_sensor_shade_cover", "照度センサ受光部遮光カバー密閉"),
                ("tunnel_lighting_sodium_lamp_preheat", "高圧ナトリウムランプ予熱通電"),
                ("tunnel_lighting_phase_control_triac_short", "サイリスタ調光器完全短絡"),
                ("tunnel_lighting_diesel_generator_crank", "非常用ディーゼル発電機始動"),
                ("tunnel_lighting_emergency_telephone_call", "非常電話一斉呼出通話"),
                ("tunnel_lighting_toll_gate_indicator_red", "料金所進入表示赤色転換"),
                ("tunnel_lighting_traffic_signal_yellow_blink", "信号機黄色点滅徐行誘導")
            ],
            "tunnel_lighting_adaptive_bright", "tunnel_lighting_ups_emergency_lights"
        ),
        (
            "30",
            "超臨界地熱バイナリー発電プラント低沸点媒体熱交換サイクル管理。[地熱熱水温度140℃、ペンタン冷媒媒体]",
            "熱流体計装モニタ：蒸発器内ペンタン圧力・温度安定、バイナリータービンは定格1,800rpmで発電中。サイクル制御を決定せよ。",
            "熱流体計装モニタ：蒸発器伝熱管内部リークにより、引火性ペンタンガスが熱水ラインへ高圧逆流混入した。サイクル制御を決定せよ。",
            [
                ("binary_cycle_power_generation_run", "定常バイナリー蒸発発電サイクル維持"),
                ("binary_cycle_emergency_isolate_flare", "熱水遮断・可燃性冷媒回収タンク退避隔離"),
                ("binary_cycle_turbine_trip_overspeed", "バイナリータービン機械式過速度トリップ"),
                ("binary_cycle_cooling_water_tower_stop", "復水用冷却塔ファン全面停止"),
                ("binary_cycle_feed_pump_vfd_max_flow", "低沸点媒体循環ポンプ最高速増速"),
                ("binary_cycle_condenser_hotwell_drain", "復水器ホットウェル大気排水"),
                ("binary_cycle_nitrogen_purge_turbine", "タービンケーシング窒素パージ封入"),
                ("binary_cycle_lube_oil_cooler_isolate", "軸受潤滑油冷却器通水遮断"),
                ("binary_cycle_reinjection_pump_halt", "地熱熱水還元井圧入ポンプ停止"),
                ("binary_cycle_generator_breaker_reverse", "発電機連系遮断器逆電力トリップ"),
                ("binary_cycle_silica_scale_acid_clean", "シリカスケール酸洗浄ポンプ起動"),
                ("binary_cycle_pentane_makeup_charge", "新規ペンタン冷媒ドラム缶充填"),
                ("binary_cycle_degassing_vacuum_pump_run", "不凝縮ガス真空排気ポンプ起動"),
                ("binary_cycle_safety_relief_burst_vent", "媒体安全弁高所大気放散ベント"),
                ("binary_cycle_heat_pipe_thermosiphon", "ヒートパイプサーモサイフォン始動"),
                ("binary_cycle_plant_fire_deluge_spray", "防爆エリア消火スプリンクラー散水")
            ],
            "binary_cycle_power_generation_run", "binary_cycle_emergency_isolate_flare"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k16_defs:
        pairs.append({
            "id": f"rc2b4_pert_{gid}_s1", "group_id": f"rc2b4_pert_{gid}", "family": "perturbation_invariance",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_pert_{gid}_s2", "group_id": f"rc2b4_pert_{gid}", "family": "perturbation_invariance",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    return pairs
