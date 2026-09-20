"""Family 5: domain_transfer (30 pairs, 60 cases) - RC3 Bridge Benchmark
Prefix: rc3b_dom_
Distribution: K=3 (10 pairs), K=4 (15 pairs), K=6 (5 pairs)
Focus: Cross-domain transfer to novel technical frontiers (quantum cryogenics, tokamak divertors, orbital space tugs, cryo-EM).
Zero leakage against all past datasets.
"""

from typing import Any, Dict, List, Tuple


def make_choices(c_defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in c_defs]


def get_domain_transfer_pairs() -> List[Dict[str, Any]]:
    pairs: List[Dict[str, Any]] = []

    # --- K=3 (10 pairs: groups 01 to 10) ---
    k3_defs = [
        (
            "01",
            "希釈冷凍機を用いた超伝導量子コンピュータ制御。混合室温度基準は『定常15mK以下を維持』である。20mKを超過した場合は量子ビットのコヒーレンス時間T1が急落するため測定を一時凍結する。",
            "希釈機テレメトリ：混合室RuO2温度計は11.4mKを示し、3He循環圧は安定している。量子計算実験可否を判定せよ。",
            "希釈機テレメトリ：混合室RuO2温度計は23.8mKへ過熱上昇した。量子計算実験可否を判定せよ。",
            [("qubit_exp_execute", "極低温安定・量子アルゴリズム演算実行承認"), ("qubit_exp_freeze_cool", "温度上昇コヒーレンス喪失・演算一時凍結待機"), ("qubit_exp_3he_purge", "ヘリウム3循環凝縮サイクル再起動")],
            "qubit_exp_execute", "qubit_exp_freeze_cool"
        ),
        (
            "02",
            "トカマク型磁気閉じ込め核融合実験炉のダイバータ熱流束制御。規定は『ダイバータ板受熱流束10MW/m2以下を維持』である。超過時はタングステン装荷板溶損防止のため不純物ガスパフを行う。",
            "赤外線サーモグラフィ監視：外側ストライクポイント受熱流束は7.2MW/m2である。プラズマ加熱運用を決定せよ。",
            "赤外線サーモグラフィ監視：外側ストライクポイント受熱流束は13.5MW/m2へ跳ね上がった。プラズマ加熱運用を決定せよ。",
            [("divertor_nominal_heating", "熱負荷許容内・高周波追加加熱継続"), ("divertor_argon_puff_radiate", "熱流束過大・アルゴン不純物ガスパフ放射冷却"), ("divertor_emergency_quench", "プラズマ電流即時ディスラプション停止")],
            "divertor_nominal_heating", "divertor_argon_puff_radiate"
        ),
        (
            "03",
            "クライオ電子顕微鏡（Cryo-EM）用単粒子解析グリッド凍結膜厚制御。基準は『急速凍結アモルファス氷薄膜厚さ20nm以上50nm以下』である。薄すぎるとタンパク質変性、厚すぎると非弾性散乱で分解能が低下する。",
            "電子線回折膜厚計：測定氷厚は32nmであり、完全な非晶質ガラス状氷が形成されている。データ収集を決定せよ。",
            "電子線回折膜厚計：測定氷厚は85nmに達し、結晶質氷の回折リングが観察された。データ収集を決定せよ。",
            [("cryo_em_auto_acquisition", "氷厚最適・自動グリッド高分解能撮影開始"), ("cryo_em_grid_reject", "氷厚過大・結晶化不良グリッド廃棄除外"), ("cryo_em_blotting_retime", "液体エタンプランジブロッティング時間再調整")],
            "cryo_em_auto_acquisition", "cryo_em_grid_reject"
        ),
        (
            "04",
            "静止トランスファ軌道（GTO）投入用小型軌道離脱推進機（OTV）。基準は『過酸化水素スラスタ室圧1.5MPa以上かつ触媒床温度180℃以上』である。",
            "推進系テレメトリ：スラスタ燃焼室圧は1.72MPa、銀触媒床温度は195℃を記録している。アポジキック噴射を指示せよ。",
            "推進系テレメトリ：スラスタ燃焼室圧は0.88MPaへ減衰、触媒床温度は130℃へ低下した。アポジキック噴射を指示せよ。",
            [("otv_burn_proceed", "推進系パラメータ適合・アポジキック噴射点火"), ("otv_burn_abort_preheat", "触媒失効失圧・噴射中止および触媒予熱"), ("otv_rcs_attitude_tumble", "リアクションホイール脱飽和スピン")],
            "otv_burn_proceed", "otv_burn_abort_preheat"
        ),
        (
            "05",
            "放射光大型加速器（SPring-8）の真空アンジュレータ磁場ギャップ制御。基準は『磁気ギャップ5.0mm以上かつビーム軌道偏向角0.5μrad以内』である。",
            "ビーム位置モニタ（BPM）：ギャップ間隔は5.2mm、軌道偏向は0.18μradである。X線ビームライン運用を決定せよ。",
            "ビーム位置モニタ（BPM）：ギャップ間隔は4.3mmに狭小化し、軌道偏向は1.4μradへ逸脱した。X線ビームライン運用を決定せよ。",
            [("undulator_beam_shutter_open", "ビーム軌道安定・X線主シャッター開放実験開始"), ("undulator_gap_interlock_trip", "ビーム偏向逸脱・アンジュレータ緊急ギャップ離隔"), ("undulator_steer_magnet_tune", "ステアリング電磁石微調電流補正")],
            "undulator_beam_shutter_open", "undulator_gap_interlock_trip"
        ),
        (
            "06",
            "全固体リチウム金属電池のスタック拘束圧制御。基準は『セル面圧2.0MPa以上5.0MPa以下を常時維持』である。不足すると界面剥離、過大になると固体電解質の微細クラックから短絡が生じる。",
            "ロードセル測定：スタック加圧面圧は3.4MPaで維持されている。急速充電プロトコルを指示せよ。",
            "ロードセル測定：リチウム析出膨張により面圧が7.8MPaへ異常増大した。急速充電プロトコルを指示せよ。",
            [("solid_battery_fast_charge", "界面拘束圧適合・大電流急速充電開始"), ("solid_battery_overpressure_cut", "異常面圧過大・充電即時カットオフ保護"), ("solid_battery_spring_relax", "スプリング拘束治具手動開放")],
            "solid_battery_fast_charge", "solid_battery_overpressure_cut"
        ),
        (
            "07",
            "超伝導RFリニアック加速空洞のローレンツ力離調補正。基準は『空洞共振周波数離調量Δfが±20Hz以内かつピエゾチューナー追従時間5ms以内』である。",
            "空洞低電力RF制御（LLRF）：Δfは+6Hz、ピエゾ応答は3.2msである。大電力RFパルス注入を指示せよ。",
            "空洞低電力RF制御（LLRF）：Δfは-84Hzへ大離調、ピエゾ変位素子は飽和状態を示した。大電力RFパルス注入を指示せよ。",
            [("srf_cavity_rf_power_on", "共振整合良好・クライストロン大電力パルス投入"), ("srf_cavity_piezo_recenter", "離調超過・ステッピングモーター機械式粗調復帰"), ("srf_helium_bath_derate", "液体ヘリウム槽減圧沸騰停止")],
            "srf_cavity_rf_power_on", "srf_cavity_piezo_recenter"
        ),
        (
            "08",
            "遺伝子治療用アデノ随伴ウイルス（AAV）超遠心分離の塩化セシウム密度勾配基準。基準は『完全粒子バンド屈折率nDが1.3700以上1.3725以下』である。中空カプシドとDNA充填粒子を分離する。",
            "アベ屈折計測定：分取画分の屈折率は1.3712を記録した。分取液の処置を指示せよ。",
            "アベ屈折計測定：分取画分の屈折率は1.3665（中空粒子領域）であった。分取液の処置を指示せよ。",
            [("aav_full_capsid_pool", "完全粒子カプシド分取プール・透析脱塩移送"), ("aav_empty_capsid_discard", "中空カプシド画分判定・廃棄ドレイン回送"), ("aav_respin_ultracentrifuge", "超遠心分離機再回転ステップ")],
            "aav_full_capsid_pool", "aav_empty_capsid_discard"
        ),
        (
            "09",
            "月面極域探査ローバーの太陽電池パドル日照追尾制御。基準は『入射角誤差±2.0度以内かつスリップリング温度-120℃以上』である。月極域の低仰角日光を連続受光する。",
            "姿勢追尾センサ：太陽光入射角誤差は+0.8度、スリップリング温度は-75℃である。電力生成制御を決定せよ。",
            "姿勢追尾センサ：太陽光入射角誤差は+6.5度へ追従遅れ、スリップリング温度は-142℃へ凍結降下した。電力生成制御を決定せよ。",
            [("rover_solar_track_nominal", "太陽追尾正常・リチウム蓄電池満充電チャージ"), ("rover_gimbal_heater_engage", "追尾誤差過大・パドル駆動ヒーター通電復帰"), ("rover_sleep_mode_hibernate", "極低温冬眠スリープモード移行")],
            "rover_solar_track_nominal", "rover_gimbal_heater_engage"
        ),
        (
            "10",
            "深海熱水噴出孔自律探査AUVの酸化還元電位（ORP）プルーム探索。基準は『ORP負勾配ΔORPが-50mV/10m以上検知かつメタン濃度0.1μmol/L以上』である。",
            "電気化学センサログ：ΔORPは-78mV/10mを記録し、レーザーメタン計は0.35μmol/Lを検知した。航法モードを決定せよ。",
            "電気化学センサログ：ΔORPは-8mV/10mにとどまり、メタン濃度はバックグラウンド値（0.01μmol/L）である。航法モードを決定せよ。",
            [("auv_plume_homing_track", "熱水プルーム中心軸自動ホーミング追尾潜航"), ("auv_grid_survey_cruise", "プルーム未検知・広域グリッド探査巡航継続"), ("auv_seabed_landing_anchor", "海底着底アンカー係留待機")],
            "auv_plume_homing_track", "auv_grid_survey_cruise"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k3_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_dom_{gid}_s1",
                "group_id": f"rc3b_dom_{gid}",
                "family": "domain_transfer",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_dom_{gid}_s2",
                "group_id": f"rc3b_dom_{gid}",
                "family": "domain_transfer",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2}
            }
        ])

    # --- K=4 (15 pairs: groups 11 to 25) ---
    k4_defs = [
        (
            "11",
            "宇宙用光格子時計のストロンチウム原子レーザー冷却捕集基準。基準は『原子数1×10^4個以上かつ冷却温度3.0μK以下』である。周波数基準発振器としての絶対精度を担保する。",
            "光電子増倍管計測：冷却捕集原子数は2.4×10^4個、飛行時間法温度は1.8μKである。時計分光シーケンスを決定せよ。",
            "光電子増倍管計測：冷却捕集原子数は3.1×10^3個へ減少、温度は8.5μKへ過熱した。時計分光シーケンスを決定せよ。",
            [("lattice_clock_spectroscopy", "原子数・温度適合・時計遷移クロック分光開始"), ("lattice_clock_re_mot_cycle", "原子捕集不足・磁気光学トラップ再冷却サイクル"), ("lattice_zeeman_slower_tune", "ゼーマンスローワー磁場勾配最適化"), ("lattice_laser_relock_hold", "光共振器レーザー周波数再ロック待機")],
            "lattice_clock_spectroscopy", "lattice_clock_re_mot_cycle"
        ),
        (
            "12",
            "海洋石油掘削ライザー管の渦励振（VIV）抑制フェアード運用基準。基準は『無次元周波数ストローハル振動振幅0.15D以下かつ潮流偏角±10度以内』である。",
            "音響水中ドップラー流速計（ADCP）：実測振動振幅は0.06D、潮流偏角は+4度である。ライザー運用を決定せよ。",
            "音響水中ドップラー流速計（ADCP）：実測振動振幅は0.32Dへ激増、潮流偏角は+22度へ斜流化した。ライザー運用を決定せよ。",
            [("riser_drilling_nominal", "渦励振抑制良好・掘削ドリル回転継続"), ("riser_fairing_weathervane", "共振振幅過大・フェアリング自動風見回転追従"), ("riser_disconnect_eds", "緊急切断システムEDS離脱"), ("riser_tensioner_pull_up", "トップテンショナー揚圧力最大引き上げ")],
            "riser_drilling_nominal", "riser_fairing_weathervane"
        ),
        (
            "13",
            "超臨界水酸化（SCWO）有害廃棄物分解反応器の腐食防護基準。基準は『反応器ヘッド温度550℃以上620℃以下かつ塩素イオン濃度500ppm以下』である。",
            "オンラインサンプリング計器：ヘッド温度は585℃、塩素濃度は180ppmである。難分解性排水処理を指示せよ。",
            "オンラインサンプリング計器：ヘッド温度は645℃へ過熱、塩素濃度は1200ppmへ激増した。難分解性排水処理を指示せよ。",
            [("scwo_feed_proceed", "超臨界分解条件適合・原水連続注入処理開始"), ("scwo_alkali_quench_stop", "高温塩素腐食危険・水酸化ナトリウム急冷中和停止"), ("scwo_preheater_bypass", "予熱器バイパスライン循環"), ("scwo_co2_stripper_vent", "炭酸ガス放散スクラバー待機")],
            "scwo_feed_proceed", "scwo_alkali_quench_stop"
        ),
        (
            "14",
            "重粒子線がん治療装置の炭素イオンビームエネルギーシンクロトロン出射基準。基準は『出射ビーム運動量広がりΔp/pが±0.1%以内かつ照射アイソセンター位置精度±0.3mm以内』である。",
            "ビーム診断プロファイルモニタ：Δp/pは±0.04%、位置精度は+0.12mmである。患者患部スキャニング照射を指示せよ。",
            "ビーム診断プロファイルモニタ：Δp/pは±0.25%へ拡大、位置精度は+0.85mmへ位置ズレした。患者患部スキャニング照射を指示せよ。",
            [("hadron_beam_irradiate_go", "ビームパラメータ高精度適合・患部ペンシルスキャン照射"), ("hadron_beam_abort_interlock", "ビームプロファイル逸脱・高速ビームチョッパー即時遮断"), ("hadron_gantry_reposition", "回転ガントリー角度アライメント再調整"), ("hadron_rf_knockout_tune", "RFノックアウト出射周波数再整定")],
            "hadron_beam_irradiate_go", "hadron_beam_abort_interlock"
        ),
        (
            "15",
            "成層圏疑似衛星（HAPS）ソーラー無人機の成層圏夜間高度維持基準。基準は『高度18500m以上かつ機体エネルギー収支マージン12%以上』である。",
            "フライトテレメトリ：現在高度19200m、夜間蓄電池残量に基づくエネルギーマージンは16%である。飛行制御を指示せよ。",
            "フライトテレメトリ：現在高度17800mへ滑空沈下、エネルギーマージンは4%へ危険減少した。飛行制御を指示せよ。",
            [("haps_strato_cruise_nominal", "夜間高度維持適合・成層圏通信カバレッジ旋回継続"), ("haps_energy_saver_glide", "高度エネルギー低下・低高度省エネ滑空モード移行"), ("haps_emergency_prop_burst", "プロペラ緊急全開フルパワー上昇"), ("haps_recover_dive_spiral", "対気速度回復スパイラル降下")],
            "haps_strato_cruise_nominal", "haps_energy_saver_glide"
        ),
        (
            "16",
            "大型液化水素輸送船の貨物タンク真空断熱層健全性基準。基準は『真空二重殻間圧力0.01Pa以下かつ外殻温度計霜付き未検知』である。",
            "真空断熱モニタ：二重殻間圧力は0.004Pa、外殻表面温度は+15℃（常温安定）である。航行運用判定を行え。",
            "真空断熱モニタ：二重殻間圧力は0.45Paへ真空破壊、外殻表面温度は-25℃へ局所急冷霜付き検知。航行運用判定を行え。",
            [("lh2_tanker_voyage_pass", "真空断熱完全合格・水素輸送定期航行続行"), ("lh2_cargo_emergency_transfer", "真空破壊断熱破綻・隣接タンク緊急水素移送"), ("lh2_boiloff_flare_vent", "安全弁開放・BOGフレア焼却放出"), ("lh2_vacuum_getter_fire", "ゲッターポンプ活性化通電加熱")],
            "lh2_tanker_voyage_pass", "lh2_cargo_emergency_transfer"
        ),
        (
            "17",
            "磁気浮上式フライホイール電力貯蔵システムの磁気軸受安定性基準。基準は『ローター軸ブレ変位10μm以下かつステーターコイル温度65℃以下』である。",
            "渦電流変位センサ：軸ブレ変位は4.2μm、コイル温度は48℃である。系統瞬低補償待機を指示せよ。",
            "渦電流変位センサ：軸ブレ変位は28μmへ振動励起、コイル温度は82℃へ過熱した。系統瞬低補償待機を指示せよ。",
            [("flywheel_standby_ready", "磁気浮上完全安定・高速チャージ放電待機"), ("flywheel_touchdown_brake", "軸ブレ共振過大・タッチダウンベアリング緊急機械制動"), ("flywheel_vacuum_purge", "フライホイール真空チャンバー再排気"), ("flywheel_dsp_gain_tune", "アクティブ磁気軸受DSPフィードバックゲイン補正")],
            "flywheel_standby_ready", "flywheel_touchdown_brake"
        ),
        (
            "18",
            "微小重力環境宇宙バイオ3Dプリンターの生体組織造形基準。基準は『ハイドロゲル粘弾性貯蔵弾性率Gが1200Pa以上かつ細胞生存率92%以上』である。",
            "宇宙実験モジュール解析：G値は1450Pa、トリパンブルー細胞生存率は95.4%である。人工毛細血管造形を指示せよ。",
            "宇宙実験モジュール解析：G値は650Pa（ゲル化不良流動）、細胞生存率は78%へ低下した。人工毛細血管造形を指示せよ。",
            [("space_bioprint_print_run", "バイオインク性状適合・血管組織立体積層プリント開始"), ("space_bioprint_cartridge_purge", "ゲル化不全細胞死・カートリッジ廃棄パージ"), ("space_bioprint_uv_crosslink", "光架橋UVレーザー照射強度増大"), ("space_bioprint_thermal_warm", "シリンジバレル保温温度37℃復帰")],
            "space_bioprint_print_run", "space_bioprint_cartridge_purge"
        ),
        (
            "19",
            "深宇宙光無線通信（Deep Space Optical Comm）の光地上局ダウンリンク受信基準。基準は『ビット誤り率BERが1.0×10^-5以下かつ補償光学AOストレール比0.65以上』である。",
            "地上局望遠鏡レーザー受信：実測BERは2.3×10^-6、ストレール比は0.78である。火星データ受信を指示せよ。",
            "地上局望遠鏡レーザー受信：実測BERは4.8×10^-3に劣化、大気揺らぎによりストレール比は0.32に崩壊した。火星データ受信を指示せよ。",
            [("optical_comm_downlink_acquire", "光リンク品質合格・大容量科学観測データ高速受信"), ("optical_comm_rf_switchover", "大気乱流光途絶・Kaバンド電波通信へ自動フォールバック"), ("optical_comm_ao_deform_reset", "可変形鏡デフォーマブルミラーアクチュエータ原点復帰"), ("optical_comm_narrow_filter", "太陽迷光遮光狭帯域光学フィルタ切替")],
            "optical_comm_downlink_acquire", "optical_comm_rf_switchover"
        ),
        (
            "20",
            "海洋温度差発電（OTEC）サイクルにおけるアンモニア作動流体ランキンサイクル効率基準。基準は『表層温水蒸発器ピンチポイント温度差2.0℃以内かつタービン入口乾き度0.99以上』である。",
            "プラント計測データ：ピンチポイント差は1.4℃、タービン入口乾き度は0.998である。発電タービン負荷制御を決定せよ。",
            "プラント計測データ：ピンチポイント差は4.2℃へ拡大、タービン入口乾き度は0.92（湿り蒸気液滴混入）へ低下した。発電タービン負荷制御を決定せよ。",
            [("otec_turbine_load_up", "熱交換効率優良・発電機最大出力並入発電"), ("otec_liquid_knockout_trip", "タービン液撃コロージョン防止・蒸気入口弁緊急遮断"), ("otec_deep_cold_pump_boost", "深層冷水取水ポンプ周波数増強"), ("otec_degas_warm_intake", "表層温水取水ストレーナー逆洗")],
            "otec_turbine_load_up", "otec_liquid_knockout_trip"
        ),
        (
            "21",
            "ペロブスカイト太陽電池大面積スロットダイ塗布工程の結晶化制御基準。基準は『ウェット膜乾燥窒素ガスナイフ風速18m/s以上かつ中間体反射スペクトル平坦度0.95以上』である。",
            "インライン分光カメラ：ガスナイフ風速は21m/s、反射スペクトル平坦度は0.98である。ロールツーロール製膜を指示せよ。",
            "インライン分光カメラ：ガスナイフ風速は12m/sへ低下、不均一乾燥による膜厚ムラで平坦度は0.81へ乱れた。ロールツーロール製膜を指示せよ。",
            [("perovskite_coating_proceed", "均質薄膜乾燥結晶化・連続スロットダイ塗布続行"), ("perovskite_slot_die_abort", "乾燥不均一結晶欠陥・塗布ヘッド停止および基板排出"), ("perovskite_antisolvent_dosing", "貧溶媒滴下量微調整"), ("perovskite_hotplate_bake", "ステージアニール温度昇温")],
            "perovskite_coating_proceed", "perovskite_slot_die_abort"
        ),
        (
            "22",
            "核融合炉中性子増殖ブランケットの液体リチウム鉛（Pb-Li）電磁ポンプ流量基準。基準は『流速0.5m/s以上かつトリチウム透過回収分圧1.0×10^-2 Pa以下』である。",
            "電磁流量計・透過セルモニタ：流速は0.65m/s、透過分圧は4.2×10^-3 Paである。増殖ブランケットループ運用を判定せよ。",
            "電磁流量計・透過セルモニタ：流速は0.18m/sへ圧力損失失速、トリチウム分圧は5.8×10^-2 Paへ蓄積超過した。増殖ブランケットループ運用を判定せよ。",
            [("blanket_loop_nominal_run", "液体金属流動適合・定常熱交換トリチウム回収"), ("blanket_mhd_pressure_trip", "MHD圧損閉塞・電磁ポンプ電力遮断循環停止"), ("blanket_getter_bed_replace", "トリチウム真空ゲッター吸着剤交換"), ("blanket_freeze_quench", "LiPb共晶固化冷却待機")],
            "blanket_loop_nominal_run", "blanket_mhd_pressure_trip"
        ),
        (
            "23",
            "超高純度ガスクロマトグラフィー質量分析（GC-MS/MS）による半導体特殊ガス分析。基準は『ベースラインS/N比500以上かつピークテーリング係数0.9以上1.2以下』である。",
            "分析検量線レポート：S/N比は1200、ピークテーリング係数は1.04である。不純物定量分析を指示せよ。",
            "分析検量線レポート：S/N比は180へノイズ増大、テーリング係数は1.65（極性吸着ピーク引き）へ崩れた。不純物定量分析を指示せよ。",
            [("gcms_quant_report_approved", "高分離能達成・ppb極微量不純物定量承認"), ("gcms_column_bakeout_req", "カラム汚染活性点発生・ベーキングエージングおよび再分析"), ("gcms_filament_bias_tune", "イオン源フィラメントエミッション電流調整"), ("gcms_split_ratio_modify", "スプリット比手動変更設定")],
            "gcms_quant_report_approved", "gcms_column_bakeout_req"
        ),
        (
            "24",
            "無人飛行艇による海洋大気エアロゾルサンプリング飛行基準。基準は『海面高度15m以下かつ対気対地ドリフト角3.0度以内』である。波頭エアロゾル薄層を直接採取する。",
            "電波高度計・IMU航法データ：対水面高度は11.5m、対地ドリフト角は1.8度である。サンプリング採取バルブを指示せよ。",
            "電波高度計・IMU航法データ：対水面高度は6.2mへ沈下危険、横風によりドリフト角は7.5度へ吹き流された。サンプリング採取バルブを指示せよ。",
            [("aerosol_intake_open", "超低高度安定・インパクター大気サンプリング採取開始"), ("aerosol_pull_up_wave_avoid", "海面波浪衝突回避・即時最大上昇機首上げ"), ("aerosol_pitot_heater_boost", "ピトー管海塩結氷ヒーター過熱"), ("aerosol_payload_drop", "非常時投棄バラスト投下")],
            "aerosol_intake_open", "aerosol_pull_up_wave_avoid"
        ),
        (
            "25",
            "バイオ人工肝臓リアクターの中空糸膜肝細胞潅流圧基準。基準は『膜間差圧TMPが20mmHg以上45mmHg以下かつアンモニアクリアランス85%以上』である。",
            "リアクター生化学モニタ：TMPは31mmHg、アンモニアクリアランスは91.4%である。患者体外循環継続可否を判定せよ。",
            "リアクター生化学モニタ：TMPは68mmHgへ目詰まり過圧、アンモニアクリアランスは52%へ代謝低下した。患者体外循環継続可否を判定せよ。",
            [("bio_liver_perfusion_continue", "人工肝代謝機能健全・体外潅流治療続行"), ("bio_liver_module_replace", "中空糸膜閉塞機能不全・リアクターモジュール緊急交換"), ("bio_liver_oxygen_boost", "中空糸膜酸素加圧器酸素濃度増強"), ("bio_liver_heparin_flush", "抗凝固ヘパリン生食フラッシュ")],
            "bio_liver_perfusion_continue", "bio_liver_module_replace"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k4_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_dom_{gid}_s1",
                "group_id": f"rc3b_dom_{gid}",
                "family": "domain_transfer",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_dom_{gid}_s2",
                "group_id": f"rc3b_dom_{gid}",
                "family": "domain_transfer",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2}
            }
        ])

    # --- K=6 (5 pairs: groups 26 to 30) ---
    k6_defs = [
        (
            "26",
            "大型ハドロン衝突型加速器（LHC）電磁カロリメータのトリガー決定。基準は『横方向エネルギー堆積ETが50GeV以上かつ単離度アイソレーション比0.1以下』である。ヒッグス粒子崩壊ガンマ線対事象を記録する。",
            "レベル1トリガープロセッサ：ETは68GeV、単離度比は0.04である。データストレージ記録判定を行え。",
            "レベル1トリガープロセッサ：ETは24GeV、近傍ジェット破砕粒子混入により単離度比は0.45である。データストレージ記録判定を行え。",
            [("lhc_event_record_accept", "孤立高エネルギー光子事象合格・RAWデータ恒久保存"), ("lhc_event_filter_reject", "背景雑音パイルアップ・トリガー不合格イベント廃棄"), ("lhc_crystal_hv_ramp", "鉛タングステン酸結晶光電子増倍管高圧昇圧"), ("lhc_timing_sync_clock", "バンチ衝突クロック位相同期補正"), ("lhc_zero_suppress_tare", "ゼロサプレッション閾値ノイズカット"), ("lhc_luminosity_recal", "衝突輝度オンライン再較正")],
            "lhc_event_record_accept", "lhc_event_filter_reject"
        ),
        (
            "27",
            "次世代宇宙望遠鏡赤外線センサー（JWST型）極低温パルス管冷凍機制御。基準は『冷却検出器温度6.4K以下かつ機械振動加速度0.005G以下』である。中間赤外線迷光とブレを除去する。",
            "天文台機器テレメトリ：検出器温度は5.9K、振動センサは0.002Gを記録している。天体長時間露光を指示せよ。",
            "天文台機器テレメトリ：パルス管弁の位相ズレにより温度は8.7Kへ昇温、振動は0.024Gへ揺動した。天体長時間露光を指示せよ。",
            [("space_telescope_expose_go", "極低温無振動適合・深宇宙赤外線長時間露光開始"), ("space_telescope_cryo_tune", "温度振動逸脱・冷凍機圧縮機位相弁PID同調"), ("space_telescope_mirror_tilt", "主鏡セグメントピエゾチルト補正"), ("space_telescope_star_tracker", "ファインガイダンスセンサ恒星再捕捉"), ("space_telescope_sunshield_turn", "サンシールド日傘姿勢ロール転換"), ("space_telescope_dark_current_cal", "暗電流オフセット較正フレーム撮影")],
            "space_telescope_expose_go", "space_telescope_cryo_tune"
        ),
        (
            "28",
            "超音速旅客機用可変インテークダクトの衝撃波位置制御。基準は『ダクト内斜め衝撃波スロート着座圧比2.8以上かつインテーク圧力回復率0.92以上』である。エンジン吸気サージ不始動（アンスタート）を防止する。",
            "飛行マッハ数2.2計装ログ：衝撃波圧比は3.1、圧力回復率は0.945である。インテーク可変ランプ制御を指示せよ。",
            "飛行マッハ数2.2計装ログ：衝撃波圧比は1.9へ後退、圧力回復率は0.78へ激減した。インテーク可変ランプ制御を指示せよ。",
            [("intake_ramp_nominal_cruise", "斜め衝撃波適正着座・可変ランプ現行角度維持"), ("intake_unstart_bypass_dump", "アンスタート兆候・可変ドア緊急全開バイパス逃がし"), ("intake_bleed_slot_actuate", "境界層ブリードスロット吸引弁開度調整"), ("intake_throttle_fuel_cut", "アフターバーナー燃料流量緊急絞り"), ("intake_spill_flap_trim", "スピルドア空力トリム角度制御"), ("intake_mach_decelerate", "迎え角引き上げによる超音速減速")],
            "intake_ramp_nominal_cruise", "intake_unstart_bypass_dump"
        ),
        (
            "29",
            "深海熱水鉱床連続揚鉱システムの揚鉱管スラリーリフト制御。基準は『管内流速3.5m/s以上かつ固形物容積体積分率15%以下』である。鉱石粒子の沈降管内閉塞を防ぐ。",
            "船上音響トモグラフィモニタ：管内流速は4.2m/s、鉱石体積分率は11.8%である。連続揚鉱エアリフトを指示せよ。",
            "船上音響トモグラフィモニタ：管内流速は2.1m/sへ失速、鉱石体積分率は24%へ異常濃縮した。連続揚鉱エアリフトを指示せよ。",
            [("mining_slurry_lift_nominal", "スラリー流動健全・連続海底鉱石揚鉱運転"), ("mining_flush_water_blast", "管内閉塞危険・高圧海水フラッシング逆洗パージ"), ("mining_air_compressor_boost", "エアリフト圧縮空気注入ノズル増圧"), ("mining_crusher_feed_stop", "海底集鉱機クラッシャー給鉱一時停止"), ("mining_pipe_strain_check", "揚鉱管歪みロードセル応力監視"), ("mining_separator_screen_clean", "船上サイクロン分離スクリーン洗浄")],
            "mining_slurry_lift_nominal", "mining_flush_water_blast"
        ),
        (
            "30",
            "人工光合成による二酸化炭素電解還元セル効率基準。基準は『ファラデー効率FEが85%以上かつ一酸化炭素生成過電圧0.40V以下』である。選択的CO変換を達成する。",
            "ガスクロマトグラフ連続排ガス測定：CO選択ファラデー効率は92.3%、過電圧は0.28Vである。電解スタック運用を決定せよ。",
            "ガスクロマトグラフ連続排ガス測定：水素副生競争反応によりFEは61.0%へ失速、過電圧は0.58Vへ増大した。電解スタック運用を決定せよ。",
            [("co2_electrolyzer_pass_run", "高選択的CO還元適合・定電流電解スタック運転続行"), ("co2_electrolyzer_catalyst_regen", "水素副生劣化不適合・触媒電極パルス電位再生"), ("co2_membrane_water_hydrate", "陰イオン交換膜水分加湿バランス調整"), ("co2_gas_flow_rebalance", "CO2原料供給マスフローコントローラ増量"), ("co2_electrolyte_ph_buffer", "炭酸水素カリウム電解液pH緩衝液置換"), ("co2_cell_temperature_warm", "電解セルジャケット加温ヒーター昇温")],
            "co2_electrolyzer_pass_run", "co2_electrolyzer_catalyst_regen"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k6_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_dom_{gid}_s1",
                "group_id": f"rc3b_dom_{gid}",
                "family": "domain_transfer",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_dom_{gid}_s2",
                "group_id": f"rc3b_dom_{gid}",
                "family": "domain_transfer",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2}
            }
        ])

    return pairs
