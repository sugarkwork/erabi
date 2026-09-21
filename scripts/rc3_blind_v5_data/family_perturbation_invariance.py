"""Blind v5 Family: Perturbation Invariance (30 pairs, 60 cases).

Choice count distribution:
- K=3: 5 pairs (pert_01 to pert_05)
- K=4: 15 pairs (pert_06 to pert_20)
- K=6: 10 pairs (pert_21 to pert_30)

Zero model inference during authoring; 100% fresh domain scenarios.
Token length strictly controlled (all <= 350 tokens).
Injects realistic surface perturbations (timestamps, telemetry headers, sensor metadata,
bracketed environmental noise, operator shifts) while maintaining strict semantic clarity.
"""

from __future__ import annotations
from typing import Any, Dict, List


def get_perturbation_invariance_pairs() -> List[Dict[str, Any]]:
    pairs = []

    # K=3: 5 pairs (01..05)
    k3_defs = [
        (
            "01",
            "LNG受入ターミナル気化器（ORV）の海水散水ポンプ運用基準。[環境ログ：外気温14.2℃、湿度65%、海水塩分濃度3.2%、シフトB班点呼済]。基準：『気化ガス送出圧力が5.5MPa以上のときは散水海水ポンプを定格2台運転、5.0〜5.5MPaの間は1台運転、5.0MPa未満のときは温水浸漬ヒーター補助へ切り替える』。",
            "[テレメトリ 14:02:15 UTC | センサID: P-902] 送出圧力センサ値は5.82MPaを記録している。ポンプ運転を選択せよ。",
            "orv_pump_two_units_rated",
            "[テレメトリ 23:45:08 UTC | センサID: P-902] 送出圧力センサ値は4.65MPaへ落ち込んだ。設備運転を選択せよ。",
            "orv_switch_submerged_heater",
            [
                ("orv_pump_two_units_rated", "散水ポンプ定格2台運転"),
                ("orv_pump_single_unit_run", "散水ポンプ1台運転"),
                ("orv_switch_submerged_heater", "温水浸漬ヒーター補助切替"),
            ],
        ),
        (
            "02",
            "特別高圧受電変電所の力率改善進相コンデンサ（SC）自動投入規程。[監視タグ：受電電圧66kV、周波数50.02Hz、日報作成完了、盤内照明点灯]。規程：『受電端遅れ力率が85%未満のときは高圧SCバンク全投入、85〜95%の間はSCバンク半数投入、95%以上（進み力率含む）のときはフェランチ効果防止のため全SC開放とする』。",
            "【系統ログ 10:15:30 JST】受電点パワーアナライザ：現在の受電端力率は遅れ78%である。SC制御を選択せよ。",
            "sc_bank_full_connect_in",
            "【系統ログ 19:40:12 JST】受電点パワーアナライザ：現在の受電端力率は進み98%である。SC制御を選択せよ。",
            "sc_bank_full_disconnect_out",
            [
                ("sc_bank_full_connect_in", "高圧SCバンク全投入"),
                ("sc_bank_half_connect_step", "SCバンク半数投入"),
                ("sc_bank_full_disconnect_out", "フェランチ防止全SC開放"),
            ],
        ),
        (
            "03",
            "医薬品製剤固形造粒機の流動層スプレーノズル噴霧規程。[ロット情報：バッチ番号AB-9201、結合剤HPC溶液、吸気露点5.4℃、作業員ID:OP-44]。規程：『流動層内排気温度が45℃以上のときはスプレー噴霧流量を毎分80mLに増量、38〜45℃の間は毎分50mL標準噴霧、38℃未満の結露危険時は噴霧即時停止・温風乾燥待機とする』。",
            "《造粒モニタ 11:20:05》排気温度センサは48.5℃を計測し粉体は軽快に流動中。スプレー噴霧を選択せよ。",
            "granulator_spray_increase_80ml",
            "《造粒モニタ 11:58:30》急激な吸熱により排気温度が34.2℃まで低下した。スプレー噴霧を選択せよ。",
            "granulator_spray_halt_drying",
            [
                ("granulator_spray_increase_80ml", "噴霧流量80mL増量"),
                ("granulator_spray_standard_50ml", "標準50mL噴霧維持"),
                ("granulator_spray_halt_drying", "噴霧即時停止温風乾燥"),
            ],
        ),
        (
            "04",
            "高速鉄道ATC信号受信アンテナの感度切替ポリシー。[列車情報：列車番号102A、編成16両、GPS同期済、架線電圧25kV]。ポリシー：『レール信号レベルが25dBμV以上のときは通常入力アッテネータ（減衰）モード、15〜25dBμVの間は標準感度直結モード、15dBμV未満の微弱電波区間はRFプリアンプ増幅モードを起動する』。",
            "[ATCアンテナ診断 #01] 地上子電界強度受信レベルは32dBμVを安定受信中。アンテナ感度を選択せよ。",
            "atc_antenna_attenuator_mode",
            "[ATCアンテナ診断 #01] トンネル坑口付近で地上子受信レベルが8dBμVに減衰した。アンテナ感度を選択せよ。",
            "atc_antenna_rf_preamp_boost",
            [
                ("atc_antenna_attenuator_mode", "通常入力アッテネータモード"),
                ("atc_antenna_standard_direct", "標準感度直結モード"),
                ("atc_antenna_rf_preamp_boost", "RFプリアンプ増幅モード"),
            ],
        ),
        (
            "05",
            "大規模下水処理場の消化ガス発電機空燃比制御規程。[プラントタグ：バイオガス槽内圧2.8kPa、硫化水素50ppm、消化温度37℃、保安責任者立会]。規程：『メタンガス濃度が60%以上のときは定格希薄燃焼リーンバーン運転、50〜60%の間は理論空燃比ストイキ運転、50%未満のカロリー低下時は補助都市ガス混焼パイロット運転へ移行する』。",
            "【ガス分析計サンプリング 08:30】消化ガス中メタン濃度分析値は64.2%である。発電機燃焼を選択せよ。",
            "biogas_rated_lean_burn",
            "【ガス分析計サンプリング 16:45】スラッジ性状変化によりメタン濃度分析値が43.0%へ低下した。発電機燃焼を選択せよ。",
            "biogas_auxiliary_city_gas_pilot",
            [
                ("biogas_rated_lean_burn", "定格希薄燃焼リーンバーン"),
                ("biogas_stoichiometric_run", "理論空燃比ストイキ運転"),
                ("biogas_auxiliary_city_gas_pilot", "補助都市ガス混焼パイロット"),
            ],
        ),
    ]

    for pid, ctx, q1, t1, q2, t2, chs in k3_defs:
        choices = [{"id": cid, "text": ctxt} for cid, ctxt in chs]
        pairs.append({
            "pair_id": f"rc3_blind5_pert_{pid}",
            "family": "perturbation_invariance",
            "k": 3,
            "case_1": {
                "id": f"rc3_blind5_pert_{pid}_s1",
                "group_id": f"rc3_blind5_pert_{pid}",
                "family": "perturbation_invariance",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1},
            },
            "case_2": {
                "id": f"rc3_blind5_pert_{pid}_s2",
                "group_id": f"rc3_blind5_pert_{pid}",
                "family": "perturbation_invariance",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2},
            },
        })

    # K=4: 15 pairs (06..20)
    k4_defs = [
        (
            "06",
            "データセンター免震建屋の層間変位監視基準。[外気環境：風速3.5m/s、気圧1012hPa、免震オイルダンパー油温22℃、保守員待機中]。基準：『層間変位量が200mm以上のときは全館非常停止・自家発ロック、100〜200mmの間はサーバ空調全機低振動運転、30〜100mmの間はエレベーター最寄階停止、30mm未満のときは通常免震追従維持とする』。",
            "【免震レーザー変位計 14:22:10】強震動時の層間変位計測値は240mmに達した。防災措置を選択せよ。",
            "seismic_emergency_datacenter_lock",
            "【免震レーザー変位計 15:05:00】余震収束後の層間変位計測値は12mmに復帰した。防災措置を選択せよ。",
            "seismic_normal_isolation_keep",
            [
                ("seismic_emergency_datacenter_lock", "全館非常停止自家発ロック"),
                ("seismic_hvac_low_vibration_run", "空調低振動運転"),
                ("seismic_elevator_nearest_floor_stop", "エレベーター最寄階停止"),
                ("seismic_normal_isolation_keep", "通常免震追従維持"),
            ],
        ),
        (
            "07",
            "火力発電所ボイラー給水脱酸素装置のヒドラジン注入基準。[水質ログ：給水pH 9.2、電気伝導率0.12μS/cm、復水器真空度96kPa、分析者印済]。基準：『溶存酸素（DO）濃度が7ppb以上のときはヒドラジン注入ポンプ全速、4〜7ppbの間は通常比例注入、2〜4ppbの間は微量注入、2ppb未満の極低酸素時は注入一時停止とする』。",
            "《溶存酸素計チャンネル#2》ボイラーエコノマイザー入口DO濃度は11.5ppbを測定。薬注制御を選択せよ。",
            "hydrazine_dosing_full_speed",
            "《溶存酸素計チャンネル#2》脱気器健全運転により入口DO濃度は1.1ppbまで低下。薬注制御を選択せよ。",
            "hydrazine_dosing_pause_temporary",
            [
                ("hydrazine_dosing_full_speed", "ヒドラジン注入ポンプ全速"),
                ("hydrazine_dosing_standard_proportional", "通常比例注入"),
                ("hydrazine_dosing_micro_trickle", "微量注入"),
                ("hydrazine_dosing_pause_temporary", "注入一時停止"),
            ],
        ),
        (
            "08",
            "製鉄所熱延ラインの鋼板デスケーリング高圧水ポンプ規程。[操業パラメータ：圧延速度15m/s、鋼種高張力鋼板、冷却水温18℃、ミルライン#3]。規程：『ノズルヘッダー吐出圧力が18MPa以上のときは定常高速デスケーリング、15〜18MPaの間は圧延速度20%減速、12〜15MPaの間は予備ポンプ並列投入、12MPa未満のときは圧延即時トリップとする』。",
            "[デスケーラー圧力計 P-401] 吐出実圧は19.4MPaを安定保持。熱延ライン制御を選択せよ。",
            "descaler_rated_high_speed_run",
            "[デスケーラー圧力計 P-401] 配管リークにより吐出実圧が10.2MPaまで急落。熱延ライン制御を選択せよ。",
            "descaler_immediate_rolling_trip",
            [
                ("descaler_rated_high_speed_run", "定常高速デスケーリング"),
                ("descaler_derate_rolling_speed_20", "圧延速度20%減速"),
                ("descaler_parallel_standby_pump", "予備ポンプ並列投入"),
                ("descaler_immediate_rolling_trip", "圧延即時トリップ停止"),
            ],
        ),
        (
            "09",
            "港湾石油桟橋のローディングアーム緊急離脱（ERS）規程。[気象データ：北東の風6m/s、潮位満潮、波高0.4m、安全保安監督員常駐]。規程：『荷役船ドリフト離反距離が5.0m以上のときはERS緊急カプラー切断離脱、3.0〜5.0mの間は荷役ポンプ緊急停止・バルブ全閉、1.5〜3.0mの間は警戒警報アラーム吹鳴、1.5m未満のときは定常荷役送油を維持する』。",
            "【アーム位置光学センサ 03:15】タンカーの係留索弛みにより船体離反距離が1.1mを記録。荷役制御を選択せよ。",
            "loading_arm_steady_transfer_keep",
            "【アーム位置光学センサ 03:42】うねり波浪によりタンカーが急激に外海側へ6.3m押し流された。ERS制御を選択せよ。",
            "loading_arm_ers_emergency_decouple",
            [
                ("loading_arm_ers_emergency_decouple", "ERS緊急カプラー切断離脱"),
                ("loading_arm_emergency_stop_valves_close", "荷役停止バルブ全閉"),
                ("loading_arm_warning_alarm_horn", "警戒警報アラーム吹鳴"),
                ("loading_arm_steady_transfer_keep", "定常荷役送油維持"),
            ],
        ),
        (
            "10",
            "半導体ウェットエッチング装置の薬液温調バス循環規程。[装置ステータス：ウェーハサイズ300mm、槽内石英ガラス、クリーン度Class1、排気差圧正常]。規程：『薬液槽内温度が85℃以上のときは冷却熱交換器バルブ全開、80〜85℃の間はPIDヒーター微調、75〜80℃の間は循環加熱ヒーター強投入、75℃未満のときはエッチング処理シーケンスを一時待機とする』。",
            "《薬液温度センサ RTD-03》フッ硝酸混合液の実測温度は88.4℃に達した。温調制御を選択せよ。",
            "bath_cooling_heat_exchanger_open",
            "《薬液温度センサ RTD-03》夜間ロット切り替え直後につき実測温度は71.2℃である。温調制御を選択せよ。",
            "bath_pause_etching_standby",
            [
                ("bath_cooling_heat_exchanger_open", "冷却熱交換器バルブ全開"),
                ("bath_pid_heater_fine_adjust", "PIDヒーター微調"),
                ("bath_heater_high_power_inject", "循環加熱ヒーター強投入"),
                ("bath_pause_etching_standby", "エッチング処理一時待機"),
            ],
        ),
        (
            "11",
            "超高圧電力ケーブル送電洞（洞道）の強制排気換気規程。[洞道環境：深度地下35m、延長4.2km、湿度82%、作業員入坑なし]。規程：『洞道内可燃性ガス濃度が0.8%以上のときは防爆ファン最大急速排気、0.4〜0.8%の間は換気ファン定格運転、0.2〜0.4%の間は低騒音微風換気、0.2%未満のときは自然換気ダンパー開待機とする』。",
            "[ガス検知局 GA-07] 赤外線メタン検知センサ値は0.95%を示している。洞道換気を選択せよ。",
            "tunnel_fan_explosion_proof_max",
            "[ガス検知局 GA-07] 赤外線メタン検知センサ値は0.05%で清浄大気である。洞道換気を選択せよ。",
            "tunnel_fan_natural_damper_open",
            [
                ("tunnel_fan_explosion_proof_max", "防爆ファン最大急速排気"),
                ("tunnel_fan_rated_speed_run", "換気ファン定格運転"),
                ("tunnel_fan_low_noise_breeze", "低騒音微風換気"),
                ("tunnel_fan_natural_damper_open", "自然換気ダンパー開待機"),
            ],
        ),
        (
            "12",
            "原子力研究炉の制御棒引き抜き速度インターロック規程。[炉心データ：冷却水導電率0.08μS/cm、炉周期60秒、中性子束測定系健全、当直長承認済]。規程：『中性子束倍増時間（ペリオド）が15秒未満のときは制御棒引き抜き即時阻止・スクラム、15〜30秒の間は引き抜き阻止・現状位置保持、30〜60秒の間は極低速微小引き抜き、60秒超の安定時は定格引き抜き速度を許可する』。",
            "【核計装チャンネル NI-104】現在の炉心ペリオド計は95秒で極めて安定。制御棒操作を選択せよ。",
            "control_rod_rated_speed_pull",
            "【核計装チャンネル NI-104】急激な反応度投入により炉心ペリオドが9.2秒に急縮した。制御棒操作を選択せよ。",
            "control_rod_immediate_scram",
            [
                ("control_rod_immediate_scram", "制御棒引き抜き阻止スクラム"),
                ("control_rod_inhibit_hold_position", "引き抜き阻止位置保持"),
                ("control_rod_ultra_slow_fine_pull", "極低速微小引き抜き"),
                ("control_rod_rated_speed_pull", "定格引き抜き速度許可"),
            ],
        ),
        (
            "13",
            "自動化コンテナターミナルAGVの衝突防止LiDAR減速制御基準。[車両テレメトリ：AGV-12、走行速度18km/h、バッテリSOC 74%、無線RSSI -55dBm]。基準：『前方障害物距離が30m以上のときは通常巡航速度18km/h維持、15〜30mの間は10km/hへ回生減速、5〜15mの間は4km/hクリープ微速、5m未満のときは非常停止メカブレーキ即時作動とする』。",
            "《LiDARスキャナ前方クラスタ 16:30》障害物までの最近接距離は38.5mで走路クリア。AGV速度を選択せよ。",
            "agv_maintain_cruise_18kmh",
            "《LiDARスキャナ前方クラスタ 16:35》他車AGVの急停止により車間距離が3.2mに接近した。AGV動作を選択せよ。",
            "agv_emergency_mechanical_brake_stop",
            [
                ("agv_maintain_cruise_18kmh", "通常巡航18km/h維持"),
                ("agv_regen_decelerate_10kmh", "10km/h回生減速"),
                ("agv_creep_crawl_4kmh", "4km/hクリープ微速"),
                ("agv_emergency_mechanical_brake_stop", "非常停止メカブレーキ作動"),
            ],
        ),
        (
            "14",
            "医薬品バイオ原薬晶析槽のアジテーター回転数制御規程。[バッチログ：結晶化工程第4フェーズ、母液比重1.12、晶析槽内圧常圧、監視責任者サイン]。規程：『結晶平均粒径が250μm以上のときは結晶破砕防止のため回転数を毎分30回転（低速）、150〜250μmの間は毎分60回転（標準）、80〜150μmの間は毎分100回転（結晶成長促進）、80μm未満の微結晶時は毎分150回転（高剪断過飽和解消）とする』。",
            "[FBRMインライン粒径プローブ 09:12] 結晶カウント平均弦長は285μmに到達。攪拌速度を選択せよ。",
            "crystallizer_low_speed_30rpm",
            "[FBRMインライン粒径プローブ 09:40] 核発生初期につき微結晶平均弦長は42μmである。攪拌速度を選択せよ。",
            "crystallizer_high_shear_150rpm",
            [
                ("crystallizer_low_speed_30rpm", "毎分30回転低速攪拌"),
                ("crystallizer_standard_60rpm", "毎分60回転標準攪拌"),
                ("crystallizer_growth_100rpm", "毎分100回転成長促進"),
                ("crystallizer_high_shear_150rpm", "毎分150回転高剪断攪拌"),
            ],
        ),
        (
            "15",
            "LNG大型外航船のボイルオフガス（BOG）再液化圧縮機規程。[航海テレメトリ：船速19.5ノット、貨物積載率98%、外気湿度78%、機関当直員立会]。規程：『タンク内圧力が18kPa以上のときは再液化圧縮機2系列フル運転、12〜18kPaの間は1系列定格運転、8〜12kPaの間はガス燃焼ユニット（GCU）焚き落とし、8kPa未満のときは圧縮機停止・減圧待機とする』。",
            "【カーゴタンク圧力トランスミッタ 13:00】タンク内圧力は21.4kPaまで上昇した。BOG処理を選択せよ。",
            "bog_reliquefaction_two_trains_full",
            "【カーゴタンク圧力トランスミッタ 21:15】寒冷海域航行により内圧が5.8kPaまで低下した。BOG処理を選択せよ。",
            "bog_compressor_stop_standby",
            [
                ("bog_reliquefaction_two_trains_full", "再液化圧縮機2系列フル運転"),
                ("bog_reliquefaction_single_train", "再液化圧縮機1系列定格運転"),
                ("bog_burn_gcu_flare_off", "ガス燃焼ユニット焚き落とし"),
                ("bog_compressor_stop_standby", "圧縮機停止減圧待機"),
            ],
        ),
        (
            "16",
            "火力発電所排煙脱硫装置（FGD）の吸収塔循環ポンプ運用基準。[環境排ガス：SO2入口濃度850ppm、吸収液pH 5.4、循環タンク液位88%、環境計量士検定]。基準：『排ガス入口流量が1,200,000Nm3/h以上のときは循環ポンプ全台（4台）運転、900,000〜1,200,000Nm3/hの間は3台運転、500,000〜900,000Nm3/hの間は2台運転、500,000Nm3/h未満のときは1台運転とする』。",
            "[FGD排ガス流量計 FT-101] 発電プラント最大定格出力につき排ガス流量は1,350,000Nm3/hである。ポンプ台数を選択せよ。",
            "fgd_pump_all_four_units_run",
            "[FGD排ガス流量計 FT-101] 夜間最低負荷追従運転につき排ガス流量は380,000Nm3/hである。ポンプ台数を選択せよ。",
            "fgd_pump_single_unit_only",
            [
                ("fgd_pump_all_four_units_run", "循環ポンプ全4台運転"),
                ("fgd_pump_three_units_run", "循環ポンプ3台運転"),
                ("fgd_pump_two_units_run", "循環ポンプ2台運転"),
                ("fgd_pump_single_unit_only", "循環ポンプ1台運転"),
            ],
        ),
        (
            "17",
            "超音速航空機用ジェットエンジンのアフターバーナー（AB）点火基準。[FADECステータス：高度11,000m、マッハ1.4、燃料温度-15℃、スロットルMAX位置]。規程：『圧縮機吐出全圧（P3）が1.8MPa以上のときはAB最大推力点火（ステージ5）、1.4〜1.8MPaの間は中間推力点火（ステージ3）、1.0〜1.4MPaの間は最小点火（ステージ1）、1.0MPa未満のときは失火防止のためAB点火禁止とする』。",
            "《エンジン制御コンピュータ FADEC-A》測定されたP3全圧は2.15MPaに達している。アフターバーナー制御を選択せよ。",
            "afterburner_ignition_stage_5_max",
            "《エンジン制御コンピュータ FADEC-A》高高度急上昇によりP3全圧が0.78MPaまで低下した。アフターバーナー制御を選択せよ。",
            "afterburner_inhibit_ignition_cut",
            [
                ("afterburner_ignition_stage_5_max", "AB最大推力ステージ5点火"),
                ("afterburner_ignition_stage_3_mid", "AB中間推力ステージ3点火"),
                ("afterburner_ignition_stage_1_min", "AB最小推力ステージ1点火"),
                ("afterburner_inhibit_ignition_cut", "失火防止AB点火禁止"),
            ],
        ),
        (
            "18",
            "メガワット級産業用蓄電池（BESS）の直流過昇温冷却規程。[設備環境：屋外コンテナ設置、外気温32℃、直流バス電圧850V、消防点検済証]。規程：『モジュール最高温度が55℃以上のときは充放電即時遮断・空調チラー最大全開、45〜55℃の間は充放電レート50%制限・空調ブースト、35〜45℃の間は定常定格運転、35℃未満のときは空調エコファン間欠モードとする』。",
            "【バッテリーセル熱電対アレイ 14:10】モジュール最高測定温度は58.2℃を検出。BESS制御を選択せよ。",
            "bess_trip_charge_chiller_max",
            "【バッテリーセル熱電対アレイ 04:30】未明の冷え込みによりモジュール最高温度は28.5℃である。BESS制御を選択せよ。",
            "bess_chiller_eco_fan_intermittent",
            [
                ("bess_trip_charge_chiller_max", "充放電即時遮断チラー全開"),
                ("bess_derate_power_half_boost", "充放電50%制限空調ブースト"),
                ("bess_maintain_rated_operation", "定常定格運転維持"),
                ("bess_chiller_eco_fan_intermittent", "空調エコファン間欠モード"),
            ],
        ),
        (
            "19",
            "超精密空気浮上除振台のレベリングサーボバルブ追従規程。[クリーンルーム環境：室温23.0℃±0.1℃、除振台搭載電子顕微鏡、床振動加速度0.02Gal]。規程：『定盤傾斜角が50μrad以上のときは電磁ピエゾ高速レベリング弁駆動、20〜50μradの間は空圧サーボ弁比例補正、5〜20μradの間は積分ゲイン微小追従、5μrad未満の水平静止時は制御弁クランプ待機とする』。",
            "[光てこ傾斜計 Tilt-X] 除振天板の傾斜変位は64μradを記録。レベリング制御を選択せよ。",
            "leveling_piezo_high_speed_valve",
            "[光てこ傾斜計 Tilt-X] 除振天板の傾斜変位は1.8μradで極めて水平静止。レベリング制御を選択せよ。",
            "leveling_clamp_valves_standby",
            [
                ("leveling_piezo_high_speed_valve", "電磁ピエゾ高速レベリング"),
                ("leveling_pneumatic_proportional", "空圧サーボ比例補正"),
                ("leveling_integral_fine_tracking", "積分ゲイン微小追従"),
                ("leveling_clamp_valves_standby", "制御弁クランプ待機"),
            ],
        ),
        (
            "20",
            "海底掘削リグのライザーパイプ張力自動調整規程。[海洋海象：水深1,500m、潮流1.8ノット、波周期8.5秒、リグ動揺ヒーブ±0.8m]。規程：『トップテンショナー張力が2,500kN以上のときは張力リリーフ弁ブロー、2,000〜2,500kNの間はヒーブ補償シリンダー減圧、1,500〜2,000kNの間は定常自動張力維持、1,500kN未満の座屈危険時はアキュムレータ急速加圧とする』。",
            "《テンショナーロードセル TL-04》ライザー天端張力実測値は2,720kNに達した。張力制御を選択せよ。",
            "tensioner_relief_valve_blow",
            "《テンショナーロードセル TL-04》リグの波乗り沈降により張力実測値が1,280kNに落ち込んだ。張力制御を選択せよ。",
            "tensioner_accumulator_rapid_pressurize",
            [
                ("tensioner_relief_valve_blow", "張力リリーフ弁ブロー"),
                ("tensioner_heave_cylinder_depressurize", "ヒーブ補償シリンダー減圧"),
                ("tensioner_maintain_steady_auto", "定常自動張力維持"),
                ("tensioner_accumulator_rapid_pressurize", "アキュムレータ急速加圧"),
            ],
        ),
    ]

    for pid, ctx, q1, t1, q2, t2, chs in k4_defs:
        choices = [{"id": cid, "text": ctxt} for cid, ctxt in chs]
        pairs.append({
            "pair_id": f"rc3_blind5_pert_{pid}",
            "family": "perturbation_invariance",
            "k": 4,
            "case_1": {
                "id": f"rc3_blind5_pert_{pid}_s1",
                "group_id": f"rc3_blind5_pert_{pid}",
                "family": "perturbation_invariance",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1},
            },
            "case_2": {
                "id": f"rc3_blind5_pert_{pid}_s2",
                "group_id": f"rc3_blind5_pert_{pid}",
                "family": "perturbation_invariance",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2},
            },
        })

    # K=6: 10 pairs (21..30)
    k6_defs = [
        (
            "21",
            "超臨界圧火力発電所主蒸気減温器スプレー弁規程。[ボイラーログ：蒸気圧力25.4MPa、定格蒸気流量1,800t/h、再熱蒸気温度565℃、制御室当直A班]。規程：『主蒸気温度が575℃超のときはスプレー注水弁全開、570〜575℃は注水弁徐開増量、565〜570℃は定常微小開度維持、560〜565℃は注水弁絞り、560℃未満は注水弁全閉、タービントリップ時はインターロック緊急全閉を実行する』。",
            "【中央監視盤 蒸気温度計 TI-101】主蒸気過熱器出口温度が582.4℃に達した。減温器スプレー操作を選択せよ。",
            "attemperator_spray_valve_full_open",
            "【中央監視盤 蒸気温度計 TI-101】負荷変動により主蒸気出口温度が552.1℃まで降下した。減温器スプレー操作を選択せよ。",
            "attemperator_spray_valve_full_close",
            [
                ("attemperator_spray_valve_full_open", "スプレー注水弁全開"),
                ("attemperator_spray_valve_step_open", "注水弁徐開増量"),
                ("attemperator_spray_valve_steady_hold", "定常微小開度維持"),
                ("attemperator_spray_valve_throttle_down", "注水弁絞り減少"),
                ("attemperator_spray_valve_full_close", "注水弁全閉遮断"),
                ("attemperator_emergency_interlock_trip", "緊急インターロック全閉"),
            ],
        ),
        (
            "22",
            "都市モノレール跨座式軌道の自動転轍機（ポイント）制御規程。[気象条件：降水量12mm/h、軌道桁温度15℃、列車在線監視閉塞クリア、保線区承認]。規程：『本線開通指令時は本線直線側へ電動転換ロック、副本線指令時は分岐側へ電動転換ロック、豪雪警報時は融雪ヒーター連続通電・反復転換、トングレール氷結検知時は転換強制停止・係員出動、列車通過中は転換完全ロックアウト、停電時は手動ハンドル転換とする』。",
            "[進路制御連動盤 07:15] 営業列車直通運行のため本線直線側への進路開通コマンドを受信。転轍機動作を選択せよ。",
            "monorail_switch_main_line_straight_lock",
            "[進路制御連動盤 07:22] 列車が転轍機直上閉塞区間を通過中である。転轍機制御を選択せよ。",
            "monorail_switch_train_passing_lockout",
            [
                ("monorail_switch_main_line_straight_lock", "本線直線側転換ロック"),
                ("monorail_switch_branch_line_side_lock", "副本線分岐側転換ロック"),
                ("monorail_switch_snow_heater_cycling", "融雪ヒーター反復転換"),
                ("monorail_switch_freeze_stop_patrol", "転換強制停止係員出動"),
                ("monorail_switch_train_passing_lockout", "列車通過中完全ロックアウト"),
                ("monorail_switch_manual_crank_handle", "手動ハンドル転換"),
            ],
        ),
        (
            "23",
            "高炉ガス乾式バグフィルター除塵設備の逆圧パルス逆洗規程。[高炉操業：銑鉄出湯中、炉頂圧240kPa、排ガス温度140℃、計装エア圧力0.6MPa]。規程：『ろ室差圧が2.5kPa超のときはパルス弁最高頻度逆洗、2.0〜2.5kPaは標準パルス逆洗、1.5〜2.0kPaは間欠逆洗、1.0〜1.5kPaは待機アイドリング、1.0kPa未満は逆洗休止、ろ布破損差圧急減時は該当ろ室隔離ダンパー全閉とする』。",
            "《差圧トランスミッタ DP-302》第3ろ室の差圧測定値が2.85kPaへ上昇した。逆洗シーケンスを選択せよ。",
            "bagfilter_max_frequency_pulse_clean",
            "《差圧トランスミッタ DP-302》定期逆洗完了直後につき差圧測定値は0.62kPaである。逆洗シーケンスを選択せよ。",
            "bagfilter_suspend_cleaning_standby",
            [
                ("bagfilter_max_frequency_pulse_clean", "最高頻度パルス逆洗"),
                ("bagfilter_standard_pulse_clean", "標準パルス逆洗"),
                ("bagfilter_intermittent_pulse_clean", "間欠パルス逆洗"),
                ("bagfilter_idle_standby_run", "待機アイドリング"),
                ("bagfilter_suspend_cleaning_standby", "逆洗休止"),
                ("bagfilter_isolate_broken_compartment", "ろ布破損ろ室隔離全閉"),
            ],
        ),
        (
            "24",
            "石油精製水素製造装置（SMR）改質炉触媒管温度保護規程。[プラントパラメータ：天然ガスフィード流量50t/h、スチームカーボン比3.0、炉内負圧50Pa]。規程：『改質管表面温度が940℃以上のときは燃料ガス緊急カット・スチームパージ、920〜940℃はバーナー燃焼率15%絞り、880〜920℃は定常改質運転、850〜880℃はバーナー燃焼率増量、850℃未満はフィード低減低温待機、炉圧正圧時は誘引ファン全開とする』。",
            "【管壁放射温度計 IRT-08】第4バーナー列改質管温度が958℃の限界超過を示した。保全制御を選択せよ。",
            "smr_emergency_fuel_cut_steam_purge",
            "【管壁放射温度計 IRT-08】改質管表面温度は902℃で設計中心値を維持。保全制御を選択せよ。",
            "smr_maintain_steady_reforming",
            [
                ("smr_emergency_fuel_cut_steam_purge", "燃料緊急カットスチームパージ"),
                ("smr_throttle_burners_15_percent", "バーナー燃焼率15%絞り"),
                ("smr_maintain_steady_reforming", "定常改質運転維持"),
                ("smr_increase_burner_firing_rate", "バーナー燃焼率増量"),
                ("smr_derate_feed_low_temp_idle", "フィード低減低温待機"),
                ("smr_id_fan_full_open_positive_pressure", "誘引ファン全開排風"),
            ],
        ),
        (
            "25",
            "宇宙ステーション実験モジュール内部環境制御系（ECLSS）CO2吸着基準。[ステーション環境：船内気圧101.3kPa、酸素分圧21.2kPa、搭乗クルー6名、実験ラック全稼働]。規程：『船内CO2分圧が0.6kPa以上のときはCDRA吸着塔を2系列全開吸着、0.4〜0.6kPaは1系列定格吸着、0.2〜0.4kPaは低速省電力吸着、0.2kPa未満は吸着パージ休止待機、吸着ベッド過熱時は窒素急速冷却、チャンバーリーク時は隔離弁緊急遮断とする』。",
            "《船内大気分光分析計 ECLSS-CO2》キャビン内CO2分圧測定値は0.78kPaに達した。CDRA吸着を選択せよ。",
            "cdra_two_trains_full_adsorption",
            "《船内大気分光分析計 ECLSS-CO2》連続吸着完了によりキャビン内CO2分圧は0.14kPaに低下した。CDRA吸着を選択せよ。",
            "cdra_pause_purge_idle_standby",
            [
                ("cdra_two_trains_full_adsorption", "2系列全開吸着運転"),
                ("cdra_single_train_rated_run", "1系列定格吸着運転"),
                ("cdra_low_power_economy_run", "低速省電力吸着運転"),
                ("cdra_pause_purge_idle_standby", "吸着パージ休止待機"),
                ("cdra_nitrogen_quench_overheat", "窒素急速冷却"),
                ("cdra_emergency_isolation_valves", "隔離弁緊急遮断"),
            ],
        ),
        (
            "26",
            "原子力空調排気系ヨウ素フィルタ銀添着ゼオライト塔バイパス規程。[放射線モニタリング：排気筒ダストモニタ0.01Bq/cm3、相対湿度40%、系統ファン風量正常]。規程：『排気放射性希ガス・ヨウ素濃度が基準値以上のときは銀ゼオライト塔へ全量通風吸着、基準値未満かつ通常運転時は通常HEPAフィルタ通風、フィルタ差圧過大時は予備フィルタ切替、吸着塔入口湿度70%超時は除湿ヒーター投入、火災報知時は防火ダンパー閉止、全停電時は重力ダンパー自重閉止とする』。",
            "[排気放射線検出器 RI-202] 燃料取扱時の微小ヨウ素放出により放射能濃度が基準値の2.5倍を記録。通風流路を選択せよ。",
            "filter_silver_zeolite_adsorption_flow",
            "[排気放射線検出器 RI-202] 放射能レベルは検出下限未満の完全清浄バックグラウンドである。通風流路を選択せよ。",
            "filter_standard_hepa_draft_keep",
            [
                ("filter_silver_zeolite_adsorption_flow", "銀ゼオライト塔全量吸着通風"),
                ("filter_standard_hepa_draft_keep", "通常HEPAフィルタ通風維持"),
                ("filter_switch_standby_bank", "予備フィルタ切替"),
                ("filter_heater_on_high_humidity", "除湿ヒーター投入"),
                ("filter_fire_damper_close", "防火ダンパー閉止"),
                ("filter_gravity_damper_drop_blackout", "重力ダンパー自重閉止"),
            ],
        ),
        (
            "27",
            "大規模下水処理場初沈汚泥引抜ポンプの超音波濃度計連動規程。[設備監視：沈殿池No.2、掻寄機稼働中、引抜弁エア圧0.5MPa、当直日誌記録済]。規程：『引抜汚泥濃度が4.0%以上のときは引抜継続・濃縮槽送泥、2.5〜4.0%は引抜ポンプ低速減速、1.5〜2.5%は間欠引抜運転、1.0〜1.5%は引抜即時停止・洗浄、1.0%未満（上澄水吸引時）は引抜弁閉止インターロック、配管閉塞時は高圧水逆洗とする』。",
            "【汚泥超音波濃度計 SD-10】引抜管路内の汚泥濃度測定値は4.8%で濃厚汚泥である。引抜動作を選択せよ。",
            "sludge_pump_continue_transfer_thickener",
            "【汚泥超音波濃度計 SD-10】汚泥引抜完了に伴い濃度計が0.4%（希薄上澄水）まで急落した。引抜動作を選択せよ。",
            "sludge_pump_close_valve_interlock",
            [
                ("sludge_pump_continue_transfer_thickener", "引抜継続濃縮槽送泥"),
                ("sludge_pump_slow_down_speed", "ポンプ低速減速運転"),
                ("sludge_pump_intermittent_run", "間欠引抜運転"),
                ("sludge_pump_stop_and_flush", "引抜停止管路洗浄"),
                ("sludge_pump_close_valve_interlock", "引抜弁閉止インターロック"),
                ("sludge_pump_high_pressure_backwash", "配管高圧水逆洗"),
            ],
        ),
        (
            "28",
            "超電導リニア実験線ヘリウム冷凍機コールドボックス減圧弁規程。[極低温テレメトリ：液体ヘリウム残量85%、断熱真空度1e-5Pa、コンプレッサー三相電流正常]。規程：『JT弁前流圧力が1.6MPa以上のときはJT減圧弁徐開、1.4〜1.6MPaは弁開度保持、1.2〜1.4MPaは弁微小絞り、1.2MPa未満は圧縮機ロードアップ、膨張機異常停止時はバイパス弁全開、熱交換器凍結時はデフロストヒーター投入とする』。",
            "《極低温SCADA JT圧力トランスデューサ》JT弁前ヘリウム圧力は1.82MPaを記録。JT減圧弁操作を選択せよ。",
            "jt_expansion_valve_step_open",
            "《極低温SCADA 膨張タービンログ》磁気軸受異常によりヘリウム膨張タービンが非常停止した。コールドボックス制御を選択せよ。",
            "jt_bypass_valve_full_open",
            [
                ("jt_expansion_valve_step_open", "JT減圧弁徐開"),
                ("jt_expansion_valve_hold_opening", "JT弁開度保持"),
                ("jt_expansion_valve_throttle_down", "JT弁微小絞り"),
                ("jt_compressor_load_up_boost", "圧縮機ロードアップ"),
                ("jt_bypass_valve_full_open", "膨張機停止バイパス全開"),
                ("jt_defrost_heater_heat_up", "デフロストヒーター投入"),
            ],
        ),
        (
            "29",
            "長大道路トンネル防災設備の泡消火設備放射規程。[トンネル防災監視：火災感知器熱発報、トンネル内滞留車両なし、ジェットファン逆転送風]。規程：『火災ゾーン確定かつ押しボタン起動時は泡ヘッド放射弁全開・消火ポンプ起動、ゾーン確定前は予告サイレン・監視カメラ手動確認、熱感知器単独発報時は現地確認要請、誤報確認時は警報復旧リセット、消火配管圧力低下時は補助加圧ポンプ起動、水源水槽減水時は上水補給弁全開とする』。",
            "【トンネル防災指令盤 23:14】第3区間火災ゾーン確定、現地の赤色消火起動ボタンが押下された。消火動作を選択せよ。",
            "foam_open_deluge_valve_pump_start",
            "【トンネル防災指令盤 02:40】保守点検業者のテスト器誤操作による誤報と判明した。指令盤操作を選択せよ。",
            "foam_alarm_reset_restore",
            [
                ("foam_open_deluge_valve_pump_start", "泡放射弁全開ポンプ起動"),
                ("foam_warning_siren_camera_check", "予告サイレンカメラ確認"),
                ("foam_request_local_patrol", "現地確認要請"),
                ("foam_alarm_reset_restore", "警報復旧リセット"),
                ("foam_start_auxiliary_pressure_pump", "補助加圧ポンプ起動"),
                ("foam_open_water_supply_makeup", "水源水槽上水補給弁全開"),
            ],
        ),
        (
            "30",
            "バイオ医薬品注射剤凍結乾燥機の真空破壊ベントフィルター制御規程。[CIP/SIP完了ログ：滅菌保証レベル10^-6、チャンバー温度常温21℃、作業者2名ダブルチェック]。規程：『凍結乾燥乾燥完了かつ打栓完了時は無菌窒素ベント弁徐開、過大差圧検知時はベント弁微小絞り、窒素ガス圧力不足時はガスボンベ自動切替、パーティクル異常検知時はベント即時遮断、ベントフィルター差圧過大時はフィルター交換、停電時はフェイルクローズ密閉とする』。",
            "《凍結乾燥機PLC シーケンス工程#14》乾燥および全バイアル打栓が完了し大気復帰工程に移行。ベント弁制御を選択せよ。",
            "lyo_sterile_n2_vent_valve_open",
            "《凍結乾燥機PLC アラーム監視》ベントライン気中パーティクルカウンタが基準値超過（異物混入兆候）を検出。ベント弁制御を選択せよ。",
            "lyo_instant_vent_shutoff_abort",
            [
                ("lyo_sterile_n2_vent_valve_open", "無菌窒素ベント弁徐開"),
                ("lyo_throttle_vent_valve_diff_press", "過大差圧ベント微小絞り"),
                ("lyo_auto_switch_gas_cylinder", "ガスボンベ自動切替"),
                ("lyo_instant_vent_shutoff_abort", "ベント即時遮断"),
                ("lyo_replace_vent_filter_alarm", "フィルター交換アラーム"),
                ("lyo_fail_close_tight_seal", "フェイルクローズ密閉"),
            ],
        ),
    ]

    for pid, ctx, q1, t1, q2, t2, chs in k6_defs:
        choices = [{"id": cid, "text": ctxt} for cid, ctxt in chs]
        pairs.append({
            "pair_id": f"rc3_blind5_pert_{pid}",
            "family": "perturbation_invariance",
            "k": 6,
            "case_1": {
                "id": f"rc3_blind5_pert_{pid}_s1",
                "group_id": f"rc3_blind5_pert_{pid}",
                "family": "perturbation_invariance",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1},
            },
            "case_2": {
                "id": f"rc3_blind5_pert_{pid}_s2",
                "group_id": f"rc3_blind5_pert_{pid}",
                "family": "perturbation_invariance",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2},
            },
        })

    return pairs
