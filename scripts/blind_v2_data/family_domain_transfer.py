"""Family 5: domain_transfer (30 pairs, 60 cases)
Distribution: K=3 (5 pairs), K=4 (10 pairs), K=6 (5 pairs), K=8 (5 pairs), K=12 (5 pairs)
Focus: Completely unseen technical domains (quantum optics, subsea robotics, orbital mechanics, bioreactors, etc.)
"""

from typing import Any, Dict, List, Tuple


def make_choices(c_defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in c_defs]


def get_domain_transfer_pairs() -> List[Dict[str, Any]]:
    pairs = []

    # --- K=3 (5 pairs: groups 01 to 05) ---
    k3_defs = [
        (
            "01",
            "量子鍵配送（QKD）装置『Q-KEY-01』の量子ビット誤り率（QBER）は3.2%（セキュリティ閾値5.0%未満）。単一光子検出器のダークカウント率は正常。",
            "QKDプロトコル規定：①【最優先】QBER安全基準：5.0%未満なら「鍵蒸留・誤り訂正シーケンスを実行する」。②【次点】暗号更新基準：暗号鍵残量1000bit未満なら「パルスレーザー出力をブーストする」。優先順位に従い選択してください。",
            "QKDプロトコル規定：①【最優先】鍵量確保基準：暗号鍵残量1000bit未満なら「パルスレーザー出力をブーストする」。②【次点】QBER安全基準：5.0%未満なら「鍵蒸留・誤り訂正シーケンスを実行する」。現在暗号鍵残量は850bitです。優先順位に従い選択してください。",
            [("distill_secret_key", "鍵蒸留・誤り訂正シーケンスを実行する"), ("boost_pulse_laser", "パルスレーザー出力をブーストする"), ("abort_and_dump_entropy", "通信を破棄しエントロピーをリセットする")],
            "distill_secret_key", "boost_pulse_laser"
        ),
        (
            "02",
            "深海無人探査機（ROV）の油圧マニピュレータ先端把持力は420N（制限500N以下）。海底堆積物サンプリングコア管の挿入深度は18cm（目標15cm以上）。",
            "海洋掘削手順：①【最優先】把持力基準：500N以下なら「コア管封止キャップを嵌合する」。②【次点】深度基準：15cm以上なら「マニピュレータを引き抜き回収する」。優先順位に従い選択してください。",
            "海洋掘削手順：①【最優先】深度回収基準：15cm以上なら「マニピュレータを引き抜き回収する」。②【次点】把持力基準：500N以下なら「コア管封止キャップを嵌合する」。優先順位に従い選択してください。",
            [("seal_core_cap", "コア管封止キャップを嵌合する"), ("retract_manipulator", "マニピュレータを引き抜き回収する"), ("jettison_sampling_basket", "サンプルバスケットを船外投棄する")],
            "seal_core_cap", "retract_manipulator"
        ),
        (
            "03",
            "微細藻類連続バイオリアクター『ALG-08』の培養液吸光度（OD680）は4.2（最適増殖域3.5〜5.0）。溶存二酸化炭素分圧は1.2kPa（下限1.0kPa以上）。",
            "リアクター制御規定：①【最優先】二酸化炭素供給：1.0kPa以上なら「LED照射光量を最大増強する」。②【次点】バイオマス回収：OD680が4.0超なら「遠心濃縮抜出ポンプを作動する」。優先順位に従い選択してください。",
            "リアクター制御規定：①【最優先】バイオマス回収：OD680が4.0超なら「遠心濃縮抜出ポンプを作動する」。②【次点】二酸化炭素供給：1.0kPa以上なら「LED照射光量を最大増強する」。優先順位に従い選択してください。",
            [("maximize_led_lighting", "LED照射光量を最大増強する"), ("start_harvest_pump", "遠心濃縮抜出ポンプを作動する"), ("sterilize_reactor_steam", "リアクターへ高圧蒸気を吹き込む")],
            "maximize_led_lighting", "start_harvest_pump"
        ),
        (
            "04",
            "低軌道周回衛星のリアクションホイール『RW-3』の回転数は3800rpm（飽和上限5000rpm以下）。磁気トルカは地磁気同調モードで待機中。",
            "姿勢制御則：①【最優先】ホイール余裕基準：5000rpm以下なら「ホイール加減速による精密指向を継続する」。②【次点】脱飽和ルーチン：3500rpm超なら「磁気トルカによるアンローディングを開始する」。優先順位に従い選択してください。",
            "姿勢制御則：①【最優先】脱飽和ルーチン：3500rpm超なら「磁気トルカによるアンローディングを開始する」。②【次点】ホイール余裕基準：5000rpm以下なら「ホイール加減速による精密指向を継続する」。優先順位に従い選択してください。",
            [("continue_rw_pointing", "ホイール加減速による精密指向を継続する"), ("start_magnetorquer_unload", "磁気トルカによるアンローディングを開始する"), ("fire_hydrazine_thruster", "ヒドラジンスラスタを全開噴射する")],
            "continue_rw_pointing", "start_magnetorquer_unload"
        ),
        (
            "05",
            "地下超深層ボーリングリグの泥水循環圧は28MPa（破砕限界35MPa以下）。ドリルストリングのトルク変動幅は4.2%（安定域5%以内）。",
            "掘進管理指針：①【最優先】トルク安定基準：変動幅5%以内なら「トップドライブ回転数を毎分120回転へ増速する」。②【次点】泥水圧警戒：25MPa超なら「泥水循環ポンプ吐出量を10%減圧する」。優先順位に従い選択してください。",
            "掘進管理指針：①【最優先】泥水圧警戒：25MPa超なら「泥水循環ポンプ吐出量を10%減圧する」。②【次点】トルク安定基準：変動幅5%以内なら「トップドライブ回転数を毎分120回転へ増速する」。優先順位に従い選択してください。",
            [("increase_rpm_to_120", "トップドライブ回転数を毎分120回転へ増速する"), ("reduce_mud_pump_10pct", "泥水循環ポンプ吐出量を10%減圧する"), ("shear_drill_pipe_bop", "BOPでドリルパイプを緊急剪断する")],
            "increase_rpm_to_120", "reduce_mud_pump_10pct"
        ),
    ]

    # --- K=4 (10 pairs: groups 06 to 15) ---
    k4_defs = [
        (
            "06",
            "超伝導トカマク核融合実験炉のダイバータ表面熱負荷は8.5MW/m2（工学限界10MW/m2以下）。プラズマコア電子密度は1.2×10^20 m^-3（目標到達）。",
            "炉心プラズマ制御則：①【最優先】電子密度基準：目標到達時は「中性粒子ビーム入射（NBI）加熱を維持する」。②【次点】熱負荷防護：8.0MW/m2超なら「ネオンガスパフによる放射冷却を注入する」。優先順位に従い選択してください。",
            "炉心プラズマ制御則：①【最優先】ダイバータ保護至上則：8.0MW/m2超なら「ネオンガスパフによる放射冷却を注入する」。②【次点】電子密度基準：目標到達時は「中性粒子ビーム入射（NBI）加熱を維持する」。優先順位に従い選択してください。",
            [
                ("maintain_nbi_heating", "中性粒子ビーム入射（NBI）加熱を維持する"),
                ("inject_neon_puff_cooling", "ネオンガスパフによる放射冷却を注入する"),
                ("trigger_massive_pellet_injection", "超大型ペレットを緊急入射しプラズマを強制消滅させる"),
                ("vent_cryostat_vacuum", "クライオスタット真空容器を大気開放する")
            ],
            "maintain_nbi_heating", "inject_neon_puff_cooling"
        ),
        (
            "07",
            "宇宙探査機イオンスラスタ『ION-X』のキセノン放電室電圧は1200V（定格1200V）。グリッド電極のスクリーンスパッタ電流は0.02A（微小安定域）。",
            "スラスタ運用仕様：①【最優先】放電電圧基準：1200V到達時は「ビームイオン加速グリッド電圧を印加する」。②【次点】電極劣化監視：電流0.015A超なら「キセノン供給マスフローを微減する」。優先順位に従い選択してください。",
            "スラスタ運用仕様：①【最優先】電極劣化監視：電流0.015A超なら「キセノン供給マスフローを微減する」。②【次点】放電電圧基準：1200V到達時は「ビームイオン加速グリッド電圧を印加する」。優先順位に従い選択してください。",
            [
                ("apply_beam_accel_voltage", "ビームイオン加速グリッド電圧を印加する"),
                ("reduce_xenon_mass_flow", "キセノン供給マスフローを微減する"),
                ("short_grid_discharge_arc", "グリッド電極をアーク放電短絡させる"),
                ("vent_xenon_tank_to_space", "キセノン高圧タンクを宇宙空間へ全量放出する")
            ],
            "apply_beam_accel_voltage", "reduce_xenon_mass_flow"
        ),
        (
            "08",
            "海洋温度差発電（OTEC）プラントの表層温海水温度は28℃（取水基準26℃以上）。深層冷海水取水流量は12000m3/h（定格下限10000m3/h以上）。",
            "タービンサイクル規定：①【最優先】表層水温基準：26℃以上なら「作動流体アンモニア循環弁を全開にする」。②【次点】深水流量管理：11000m3/h超なら「凝縮器冷海水スプレー圧を1段階絞る」。優先順位に従い選択してください。",
            "タービンサイクル規定：①【最優先】深水流量管理：11000m3/h超なら「凝縮器冷海水スプレー圧を1段階絞る」。②【次点】表層水温基準：26℃以上なら「作動流体アンモニア循環弁を全開にする」。優先順位に従い選択してください。",
            [
                ("open_ammonia_cycle_valve", "作動流体アンモニア循環弁を全開にする"),
                ("throttle_condenser_spray", "凝縮器冷海水スプレー圧を1段階絞る"),
                ("dump_ammonia_to_ocean", "アンモニア作動流体を海洋へ緊急排出する"),
                ("reverse_warm_water_pump", "表層温水ポンプを逆回転させて逆流させる")
            ],
            "open_ammonia_cycle_valve", "throttle_condenser_spray"
        ),
        (
            "09",
            "極低温量子アニーリングマシン『Q-ANN-04』の希釈冷凍機ミキシングチャンバー温度は12mK（目標15mK以下）。超伝導磁気シールド内残留磁場は0.4nT（基準1.0nT未満）。",
            "量子プロセッサ運用手順：①【最優先】残留磁場基準：1.0nT未満なら「量子アニーリングスケジュール磁場パルスを印加する」。②【次点】極低温安定化：10mK超なら「ヘリウム3循環濃縮比を微調整する」。優先順位に従い選択してください。",
            "量子プロセッサ運用手順：①【最優先】極低温安定化：10mK超なら「ヘリウム3循環濃縮比を微調整する」。②【次点】残留磁場基準：1.0nT未満なら「量子アニーリングスケジュール磁場パルスを印加する」。優先順位に従い選択してください。",
            [
                ("apply_annealing_pulse", "量子アニーリングスケジュール磁場パルスを印加する"),
                ("tune_he3_circulation_ratio", "ヘリウム3循環濃縮比を微調整する"),
                ("turn_on_thermal_switch_heater", "熱スイッチヒーターを起動し素子を室温へ昇温する"),
                ("open_cryostat_o_ring_seal", "真空断熱外槽のOリングシールを開放する")
            ],
            "apply_annealing_pulse", "tune_he3_circulation_ratio"
        ),
        (
            "10",
            "鉱山自律ダンプトラック『ADT-50』のレーダーミリ波センサは障害物なしを報告。タイヤ空気圧モニタは右後輪で内圧1100kPa（適正1000〜1200kPa）。",
            "鉱山運行管制：①【最優先】タイヤ空気圧基準：適正範囲内なら「破砕プラントへ向けて積載全速自律走行する」。②【次点】斜面勾配制御：運搬路傾斜が8度超なら「リターダー油圧ブレーキを予備加圧する」。現在運搬路傾斜は9度です。優先順位に従い選択してください。",
            "鉱山運行管制：①【最優先】斜面勾配制御：運搬路傾斜が8度超なら「リターダー油圧ブレーキを予備加圧する」。②【次点】タイヤ空気圧基準：適正範囲内なら「破砕プラントへ向けて積載全速自律走行する」。現在運搬路傾斜は9度です。優先順位に従い選択してください。",
            [
                ("proceed_full_autonomous_haul", "破砕プラントへ向けて積載全速自律走行する"),
                ("pre_pressurize_retarder", "リターダー油圧ブレーキを予備加圧する"),
                ("dump_ore_on_haul_road", "積載している鉱石を走行路面へ路上投下する"),
                ("emergency_steer_off_cliff", "車両を崖外郭側へ意図的に脱輪突入させる")
            ],
            "proceed_full_autonomous_haul", "pre_pressurize_retarder"
        ),
        (
            "11",
            "放射光加速器蓄積リングの電子ビーム電流値は450mA（定格500mA以下）。超高真空ダクト内圧力は3.0×10^-8 Pa（基準5.0×10^-8 Pa以下）。",
            "加速器運転マニュアル：①【最優先】真空度基準：5.0×10^-8 Pa以下なら「アンジュレータ磁気ギャップを縮小して高輝度X線を生成する」。②【次点】ビーム減衰補充：460mA未満なら「入射器シンクロトロンからトップアップ追加入射を行う」。優先順位に従い選択してください。",
            "加速器運転マニュアル：①【最優先】トップアップ入射基準：460mA未満なら「入射器シンクロトロンからトップアップ追加入射を行う」。②【次点】真空度基準：5.0×10^-8 Pa以下なら「アンジュレータ磁気ギャップを縮小して高輝度X線を生成する」。優先順位に従い選択してください。",
            [
                ("close_undulator_gap_xray", "アンジュレータ磁気ギャップを縮小して高輝度X線を生成する"),
                ("trigger_topup_injection", "入射器シンクロトロンからトップアップ追加入射を行う"),
                ("fire_beam_abort_kicker", "アボートキッカー電磁石で電子ビームをダンプへ廃棄する"),
                ("de_energize_rf_cavity", "高周波加速空洞の給電クライストロンを停止する")
            ],
            "close_undulator_gap_xray", "trigger_topup_injection"
        ),
        (
            "12",
            "成層圏気球観測ポッド『STRATO-9』のヘリウムガス嚢内圧は外気圧比+120Pa（破裂限界+200Pa未満）。太陽電池パドル発電電力は320W（観測所要電力250W以上）。",
            "気球飛行管制：①【最優先】電力充足基準：250W以上なら「赤外線望遠鏡指向追尾シーケンスを開始する」。②【次点】高度気圧制御：過圧+100Pa超なら「排気スプールバルブを2秒間パルス開放する」。優先順位に従い選択してください。",
            "気球飛行管制：①【最優先】気球破壊防止基準：過圧+100Pa超なら「排気スプールバルブを2秒間パルス開放する」。②【次点】電力充足基準：250W以上なら「赤外線望遠鏡指向追尾シーケンスを開始する」。優先順位に従い選択してください。",
            [
                ("start_infrared_tracking", "赤外線望遠鏡指向追尾シーケンスを開始する"),
                ("pulse_open_gas_spool_valve", "排気スプールバルブを2秒間パルス開放する"),
                ("cut_payload_flight_string", "火薬カッターでゴンドラを切り離しパラシュート降下させる"),
                ("vent_all_ballast_weights", "バラスト鉄粉パックを全量船外投棄する")
            ],
            "start_infrared_tracking", "pulse_open_gas_spool_valve"
        ),
        (
            "13",
            "メタンハイドレート海洋掘削生産船の坑口フラッシュセパレータ液面は52%（標準45〜60%）。ガス生産ラインの差圧は0.45MPa（基準0.6MPa以下）。",
            "生産分離制御基準：①【最優先】ガス差圧基準：0.6MPa以下なら「ガス圧縮機へメタンガスを送気する」。②【次点】液面微小変動：50%超なら「底面脱砂排水バルブ開度を微増する」。優先順位に従い選択してください。",
            "生産分離制御基準：①【最優先】液面微小変動：50%超なら「底面脱砂排水バルブ開度を微増する」。②【次点】ガス差圧基準：0.6MPa以下なら「ガス圧縮機へメタンガスを送気する」。優先順位に従い選択してください。",
            [
                ("send_gas_to_compressor", "ガス圧縮機へメタンガスを送気する"),
                ("increase_sand_drain_valve", "底面脱砂排水バルブ開度を微増する"),
                ("flare_methane_at_derrick", "生産メタンをデリック頂部フレアで直接燃焼処分する"),
                ("inject_glycol_inhibitor", "ハイドレート解離防止グリコールを配管へ高圧注入する")
            ],
            "send_gas_to_compressor", "increase_sand_drain_valve"
        ),
        (
            "14",
            "全固体電池パイロットラインの超乾燥ドライルーム露点は-85℃（要求規格-70℃以下）。ドライルーム給気風速は0.38m/s（適正0.30〜0.50m/s）。",
            "ドライルーム環境指針：①【最優先】風速基準：適正範囲内なら「固体電解質薄膜連続積層ロボットを稼働する」。②【次点】露点超清浄監視：-80℃以下なら「除湿ローター再生ヒーター出力を10%絞る」。優先順位に従い選択してください。",
            "ドライルーム環境指針：①【最優先】省エネルギー指針：-80℃以下なら「除湿ローター再生ヒーター出力を10%絞る」。②【次点】風速基準：適正範囲内なら「固体電解質薄膜連続積層ロボットを稼働する」。優先順位に従い選択してください。",
            [
                ("operate_stacking_robot", "固体電解質薄膜連続積層ロボットを稼働する"),
                ("throttle_regeneration_heater", "除湿ローター再生ヒーター出力を10%絞る"),
                ("spray_water_into_dryroom", "露点調整のためドライルーム室内へ加湿スプレーを噴射する"),
                ("open_emergency_dock_doors", "外気荷解き搬入ドックのシャッターを全開にする")
            ],
            "operate_stacking_robot", "throttle_regeneration_heater"
        ),
        (
            "15",
            "自動航行貨物船のソナー障害物検知深度は120m（浅瀬警戒40m以上）。自動舵角アクチュエータ偏差は0.8度（許容2.0度以内）。",
            "自動操船プロトコル：①【最優先】ソナー水深基準：40m以上なら「主機関巡航航行出力を維持する」。②【次点】舵角追従制御：0.5度超なら「油圧サーボポンプのアンチバックラッシュ補正を作動する」。優先順位に従い選択してください。",
            "自動操船プロトコル：①【最優先】舵角追従制御：0.5度超なら「油圧サーボポンプのアンチバックラッシュ補正を作動する」。②【次点】ソナー水深基準：40m以上なら「主機関巡航航行出力を維持する」。優先順位に従い選択してください。",
            [
                ("maintain_cruise_engine_power", "主機関巡航航行出力を維持する"),
                ("activate_anti_backlash_servo", "油圧サーボポンプのアンチバックラッシュ補正を作動する"),
                ("drop_bow_emergency_anchors", "全速前進中に船首双錨を緊急投錨する"),
                ("scuttle_ship_by_sea_valves", "機関室キングストン弁を開放して自沈させる")
            ],
            "maintain_cruise_engine_power", "activate_anti_backlash_servo"
        ),
    ]

    # --- K=6 (5 pairs: groups 16 to 20) ---
    k6_defs = [
        (
            "16",
            "超臨界水熱酸化（SCWO）反応器の流体温度は420℃（臨界点374℃超、上限450℃）。酸化剤過酸化水素供給流量は45L/h（定格範囲内）。",
            "SCWO制御規程：①【最優先】酸化剤流量基準：定格範囲内なら「PCB分解高圧スラリー供給を継続する」。②【次点】温度上限余裕：410℃超なら「冷却水ジャケットバイパス弁を微開する」。優先順位に従い選択してください。",
            "SCWO制御規程：①【最優先】温度上限余裕：410℃超なら「冷却水ジャケットバイパス弁を微開する」。②【次点】酸化剤流量基準：定格範囲内なら「PCB分解高圧スラリー供給を継続する」。優先順位に従い選択してください。",
            [
                ("continue_pcb_slurry_feed", "PCB分解高圧スラリー供給を継続する"),
                ("open_cooling_jacket_bypass", "冷却水ジャケットバイパス弁を微開する"),
                ("blowdown_reactor_rupture_disc", "ラプチャーディスク放散弁を手動強制破壊する"),
                ("quench_feed_with_cold_oil", "可燃性軽油を反応器へ投入して急冷する"),
                ("vent_effluent_to_factory_hall", "高温高圧排液を工場建屋内へ直接放出する"),
                ("trip_high_pressure_slurry_pump", "高圧スラリーポンプを非常停止する")
            ],
            "continue_pcb_slurry_feed", "open_cooling_jacket_bypass"
        ),
        (
            "17",
            "宇宙ステーション環境制御・生命維持システム（ECLSS）のキャビン酸素分圧は21.2kPa（公称21.0±0.5kPa）。水電解酸素発生装置のセル温度は58℃（上限65℃以下）。",
            "生命維持運用規定：①【最優先】セル温度基準：65℃以下なら「電解スタック電流を定格維持する」。②【次点】酸素分圧管理：21.0kPa超なら「酸素補給調圧弁開度を10%絞る」。優先順位に従い選択してください。",
            "生命維持運用規定：①【最優先】酸素分圧管理：21.0kPa超なら「酸素補給調圧弁開度を10%絞る」。②【次点】セル温度基準：65℃以下なら「電解スタック電流を定格維持する」。優先順位に従い選択してください。",
            [
                ("maintain_electrolyzer_rated_current", "電解スタック電流を定格維持する"),
                ("throttle_oxygen_supply_valve_10pct", "酸素補給調圧弁開度を10%絞る"),
                ("vent_cabin_atmosphere_to_space", "船内気体を真空宇宙空間へ全量排気する"),
                ("flood_cabin_with_pure_nitrogen", "船内へ窒素ガスを過剰注入して無酸素状態にする"),
                ("dump_precious_drinking_water", "浄化再生飲料水タンクを船外投棄する"),
                ("turn_off_all_co2_scrubbers", "全二酸化炭素吸着キャニスターを停止する")
            ],
            "maintain_electrolyzer_rated_current", "throttle_oxygen_supply_valve_10pct"
        ),
        (
            "18",
            "極超音速風洞実験設備『HYP-MACH7』のノズル総温度は1850K（目標1800〜1900K）。自由流静圧は2.2kPa（測定基準2.0〜2.5kPa）。",
            "風洞運転手順：①【最優先】静圧基準：測定範囲内なら「模型空気力データロガー高速サンプリングを開始する」。②【次点】総温度精密管理：1830K超なら「アーク加熱ヒーター電源出力を2%減衰する」。優先順位に従い選択してください。",
            "風洞運転手順：①【最優先】総温度精密管理：1830K超なら「アーク加熱ヒーター電源出力を2%減衰する」。②【次点】静圧基準：測定範囲内なら「模型空気力データロガー高速サンプリングを開始する」。優先順位に従い選択してください。",
            [
                ("start_aerodynamic_data_logging", "模型空気力データロガー高速サンプリングを開始する"),
                ("reduce_arc_heater_power_2pct", "アーク加熱ヒーター電源出力を2%減衰する"),
                ("eject_test_model_during_flow", "超音速気流中に風洞模型を気流外へ強制投下する"),
                ("close_throat_diffuser_shutter", "風洞スロート部シャッターを閉鎖して衝撃波を反射する"),
                ("quench_tunnel_with_liquid_co2", "測定部に液体二酸化炭素を噴霧する"),
                ("vent_vacuum_tank_blast", "下流真空球体タンクを大気開放破砕する")
            ],
            "start_aerodynamic_data_logging", "reduce_arc_heater_power_2pct"
        ),
        (
            "19",
            "液体水素ロケット発射台充填系（LH2ローディング）の配管温度は22K（沸点20.3K近傍）。充填配管ヘリウムパージ純度は99.995%（合格99.99%以上）。",
            "発射準備手順：①【最優先】パージ純度基準：99.99%以上なら「液体水素本充填バルブを開放する」。②【次点】ライン保冷基準：21K超なら「液体水素プレクール循環時間を5分延長する」。優先順位に従い選択してください。",
            "発射準備手順：①【最優先】ライン保冷基準：21K超なら「液体水素プレクール循環時間を5分延長する」。②【次点】パージ純度基準：99.99%以上なら「液体水素本充填バルブを開放する」。優先順位に従い選択してください。",
            [
                ("open_main_lh2_loading_valve", "液体水素本充填バルブを開放する"),
                ("extend_precool_circulation_5min", "液体水素プレクール循環時間を5分延長する"),
                ("ignite_hydrogen_burnoff_flare", "水素フレアスタック点火器を最大出力にする"),
                ("disconnect_umbilical_arm_now", "燃料充填中にアンビリカルアームを緊急機械切離する"),
                ("flood_launch_pad_acoustic_water", "発射台消音散水設備を全開散水する"),
                ("abort_rocket_launch_countdown", "ロケット打ち上げカウントダウンをアボート中止する")
            ],
            "open_main_lh2_loading_valve", "extend_precool_circulation_5min"
        ),
        (
            "20",
            "高輝度放射線がん治療用重粒子線加速器の炭素ビームエネルギーは400MeV/u（処方深部到達基準）。照射ターゲットアイソセンターのビーム重心ズレは0.3mm（許容0.5mm以内）。",
            "照射治療規程：①【最優先】重心精度基準：0.5mm以内なら「呼吸同期ビームゲートを開放し患部照射する」。②【次点】エネルギー管理：395MeV/u超なら「電磁石偏向コイル電流を0.1A微調整する」。優先順位に従い選択してください。",
            "照射治療規程：①【最優先】エネルギー管理：395MeV/u超なら「電磁石偏向コイル電流を0.1A微調整する」。②【次点】重心精度基準：0.5mm以内なら「呼吸同期ビームゲートを開放し患部照射する」。優先順位に従い選択してください。",
            [
                ("open_respiratory_gate_irradiate", "呼吸同期ビームゲートを開放し患部照射する"),
                ("trim_deflection_coil_current", "電磁石偏向コイル電流を0.1A微調整する"),
                ("dump_heavy_ion_beam_faraday", "重粒子線をファラデーカップへ全量偏向ダンプする"),
                ("rotate_gantry_during_beam_on", "ビーム出射中に照射ガントリーを最高速で急旋回させる"),
                ("move_patient_couch_randomly", "治療台カウチを任意方向に大きく移動させる"),
                ("shut_down_synchrotron_cooling", "シンクロトロン冷却水ポンプを停止する")
            ],
            "open_respiratory_gate_irradiate", "trim_deflection_coil_current"
        ),
    ]

    # --- K=8 (5 pairs: groups 21 to 25) ---
    k8_defs = [
        (
            "21",
            "高温ガス冷却原子炉（HTGR）ヘリウム一次冷却系の循環流量は85kg/s（定格80〜90kg/s）。原子炉入口ヘリウム温度は320℃（設計値325℃±10℃）。",
            "原子炉熱流動基準：①【最優先】入口温度基準：設計範囲内なら「制御棒微動による出力98%定格保持を行う」。②【次点】ヘリウム流量精密制御：83kg/s超なら「ガスサーキュレータインバータ周波数を1Hz絞る」。優先順位に従い選択してください。",
            "原子炉熱流動基準：①【最優先】ヘリウム流量精密制御：83kg/s超なら「ガスサーキュレータインバータ周波数を1Hz絞る」。②【次点】入口温度基準：設計範囲内なら「制御棒微動による出力98%定格保持を行う」。優先順位に従い選択してください。",
            [
                ("maintain_power_via_control_rod", "制御棒微動による出力98%定格保持を行う"),
                ("throttle_circulator_inverter_1hz", "ガスサーキュレータインバータ周波数を1Hz絞る"),
                ("drop_all_control_rods_gravity", "重力落下式全制御棒を炉心へ一斉全挿入する"),
                ("vent_helium_to_quench_tank", "一次系ヘリウムをクエンチタンクへ緊急放散する"),
                ("open_reactor_containment_doors", "原子炉格納容器の機密ハッチを開放する"),
                ("inject_liquid_poison_boron", "液体ホウ酸中性子毒を炉心へ加圧注入する"),
                ("isolate_intermediate_heat_exchanger", "中間熱交換器IHX二次側を完全隔離する"),
                ("trip_turbine_generator_breaker", "発電用ヘリウムガスタービン受電遮断器を開放する")
            ],
            "maintain_power_via_control_rod", "throttle_circulator_inverter_1hz"
        ),
        (
            "22",
            "超高圧電子顕微鏡（HVEM）加速管電圧は3.0MV（定格3.0MV）。電子銃エミッション電流は15μA（安定域10〜20μA）。",
            "電子顕微鏡運用基準：①【最優先】エミッション電流基準：安定範囲内なら「対物レンズ超伝導磁場を励磁して原子分解能撮像を行う」。②【次点】加速管耐圧警戒：2.8MV超なら「SF6絶縁ガス加圧ポンプを作動しガス圧を昇圧する」。優先順位に従い選択してください。",
            "電子顕微鏡運用基準：①【最優先】加速管耐圧警戒：2.8MV超なら「SF6絶縁ガス加圧ポンプを作動しガス圧を昇圧する」。②【次点】エミッション電流基準：安定範囲内なら「対物レンズ超伝導磁場を励磁して原子分解能撮像を行う」。優先順位に従い選択してください。",
            [
                ("excite_objective_lens_imaging", "対物レンズ超伝導磁場を励磁して原子分解能撮像を行う"),
                ("boost_sf6_insulation_gas_pump", "SF6絶縁ガス加圧ポンプを作動しガス圧を昇圧する"),
                ("vent_column_ultra_high_vacuum", "鏡体超高真空チャンバーへ大気を一気に突入させる"),
                ("short_high_voltage_stack_ground", "超高圧発生コッククロフト回路を高圧接地バーで短絡する"),
                ("deflect_electron_beam_shutter", "電子ビームを静電シャッターで完全に遮蔽偏向する"),
                ("heat_sample_stage_to_destruction", "加熱試料ホルダーの温度を最大限界まで急激に過熱する"),
                ("turn_off_water_chiller_circuit", "レンズ冷却水循環チラーの主電源を遮断する"),
                ("retract_cmos_camera_sensor", "CMOS直接検出カメラを撮影位置から引き抜く")
            ],
            "excite_objective_lens_imaging", "boost_sf6_insulation_gas_pump"
        ),
        (
            "23",
            "大型ペロブスカイト太陽電池ロールツーロール製造装置のスロットダイ塗布ギャップは35μm（規格30〜40μm）。窒素ナイフ乾燥風量は80m3/h（基準70〜90m3/h）。",
            "薄膜製造仕様：①【最優先】乾燥風量基準：基準範囲内なら「PETフィルムウェブ巻き出しテンションを維持する」。②【次点】塗布ギャップ微調整：32μm超なら「ピエゾステージアクチュエータでギャップを2μm縮小する」。優先順位に従い選択してください。",
            "薄膜製造仕様：①【最優先】塗布ギャップ微調整：32μm超なら「ピエゾステージアクチュエータでギャップを2μm縮小する」。②【次点】乾燥風量基準：基準範囲内なら「PETフィルムウェブ巻き出しテンションを維持する」。優先順位に従い選択してください。",
            [
                ("maintain_web_rewind_tension", "PETフィルムウェブ巻き出しテンションを維持する"),
                ("piezo_reduce_gap_2um", "ピエゾステージアクチュエータでギャップを2μm縮小する"),
                ("slice_pet_web_with_rotary_knife", "ロータリーカッターで走行中のウェブを全幅切断する"),
                ("dump_perovskite_ink_to_waste", "ペロブスカイト前駆体インクを高圧排出口から全量廃棄する"),
                ("flood_chamber_with_humid_air", "塗布チャンバー内へ湿度80%の湿潤空気を吹き込む"),
                ("bake_substrate_excessive_heat", "近赤外線焼成ヒーターを定格の3倍の出力で過熱する"),
                ("reverse_die_metering_pump", "シリンジ定量ポンプを最大速度で逆回転させる"),
                ("stop_clean_air_laminar_flow", "クリーンブース層流FFU送風ファンを全面停止する")
            ],
            "maintain_web_rewind_tension", "piezo_reduce_gap_2um"
        ),
        (
            "24",
            "磁気浮上式超高速鉄道（リニアモーターカー）の軌道上車両浮上量は102mm（目標100±5mm）。地上推進コイル相間電流不平衡率は1.2%（許容2.0%以内）。",
            "リニア浮上推進管理：①【最優先】電流不平衡基準：許容範囲内なら「地上インバータ周波数を上げて時速505km巡航へ加速する」。②【次点】浮上高余裕調整：101mm超なら「車載超伝導磁石ダンパーコイル電流を微調整する」。優先順位に従い選択してください。",
            "リニア浮上推進管理：①【最優先】浮上高余裕調整：101mm超なら「車載超伝導磁石ダンパーコイル電流を微調整する」。②【次点】電流不平衡基準：許容範囲内なら「地上インバータ周波数を上げて時速505km巡航へ加速する」。優先順位に従い選択してください。",
            [
                ("accelerate_to_505kmh_cruise", "地上インバータ周波数を上げて時速505km巡航へ加速する"),
                ("trim_damper_coil_current", "車載超伝導磁石ダンパーコイル電流を微調整する"),
                ("drop_mechanical_landing_gear", "時速500km走行中にゴムタイヤ着陸車輪を軌道へ緊急接地する"),
                ("quench_superconducting_magnet", "超伝導磁石保護スイッチを動作させ磁場を強制消磁する"),
                ("deploy_aerodynamic_drag_brakes", "車体上部の空力ブレーキ板を全開展開する"),
                ("trip_trackside_substation", "軌道沿線変電所の主変圧器真空遮断器を開放する"),
                ("reverse_linear_thrust_full", "回生制動用インバータ出力を逆相全開で急制動する"),
                ("short_guideway_propulsion_coils", "地上推進コイル端子間を直接短絡する")
            ],
            "accelerate_to_505kmh_cruise", "trim_damper_coil_current"
        ),
        (
            "25",
            "小惑星サンプルリターン探査機カプセル大気圏再突入管制：アブレーション熱シールド表面後退厚は12mm（許容30mm以下）。減速Gセンサ値は8.2G（ピーク設計12G以内）。",
            "突入降下シーケンス：①【最優先】減速G設計基準：12G以内なら「突入カプセル姿勢制御スラスタによる弾道維持を行う」。②【次点】熱シールド余裕：10mm超なら「空力トリムフラップを作動させて突入角を0.2度浅くする」。優先順位に従い選択してください。",
            "突入降下シーケンス：①【最優先】熱シールド余裕：10mm超なら「空力トリムフラップを作動させて突入角を0.2度浅くする」。②【次点】減速G設計基準：12G以内なら「突入カプセル姿勢制御スラスタによる弾道維持を行う」。優先順位に従い選択してください。",
            [
                ("maintain_ballistic_rcs_attitude", "突入カプセル姿勢制御スラスタによる弾道維持を行う"),
                ("trim_aerodynamic_flap_shallower", "空力トリムフラップを作動させて突入角を0.2度浅くする"),
                ("deploy_drogue_chute_at_mach5", "超音速マッハ5の極高圧気流中でパラシュートを開く"),
                ("eject_heatshield_at_hypersonic", "極超音速飛行中にアブレーション熱シールドを前倒し投棄する"),
                ("blow_sample_container_pyro", "火薬ボルトでサンプル格納コンテナを空中解体する"),
                ("disable_gps_beacon_transmitter", "着地回収捜索用GPSビーコン発信機の電源を切断する"),
                ("spin_capsule_violently", "姿勢制御スラスタを偏噴射させてカプセルを高速スピンさせる"),
                ("cut_parachute_suspension_lines", "パラシュート吊り索カッターを作動させてパラシュートを切断する")
            ],
            "maintain_ballistic_rcs_attitude", "trim_aerodynamic_flap_shallower"
        ),
    ]

    # --- K=12 (5 pairs: groups 26 to 30) ---
    k12_defs = [
        (
            "26",
            "海洋海底熱水鉱床掘削サンプラー『V-DEEP』のドリルビット温度は78℃（許容100℃未満）。海水冷却ポンプ循環吐出圧は2.8MPa（基準2.5MPa以上）。",
            "サンプリング手順：①【最優先】冷却圧基準：2.5MPa以上なら「油圧コアリングモーターを定格回転して鉱体を掘削採取する」。②【次点】熱水温度監視：70℃超なら「冷却海水吸引ポンプ流量を15%増量する」。優先順位に従い選択してください。",
            "サンプリング手順：①【最優先】熱水温度監視：70℃超なら「冷却海水吸引ポンプ流量を15%増量する」。②【次点】冷却圧基準：2.5MPa以上なら「油圧コアリングモーターを定格回転して鉱体を掘削採取する」。優先順位に従い選択してください。",
            [
                ("core_drill_rated_sample", "油圧コアリングモーターを定格回転して鉱体を掘削採取する"),
                ("boost_cool_seawater_15pct", "冷却海水吸引ポンプ流量を15%増量する"),
                ("dump_core_barrel_sea_floor", "コアバレルを海底面に投棄して切り離す"),
                ("reverse_drill_bit_max_torque", "ドリルビットを最大トルクで逆回転させて引き抜く"),
                ("close_sampling_gate_valve", "サンプリングゲートバルブを緊急閉止する"),
                ("flush_drill_string_with_glycol", "ドリルパイプ内を不凍液で全量フラッシングする"),
                ("jettison_rov_tether_cable", "ROVアンビリカルテザーケーブルを切断する"),
                ("blow_ballast_ascent_now", "浮力材バラストを緊急放出全速浮上させる"),
                ("shut_down_hydraulic_power_pack", "水中油圧パワーパックの主電動機を停止する"),
                ("illuminate_high_intensity_led", "大光量LED深海探照灯を全点灯する"),
                ("calibrate_acoustic_transponder", "長基線音響測位トランスポンダを再較正する"),
                ("lock_manipulator_wrist_joint", "マニピュレータ手首関節を機械ラチェット固定する")
            ],
            "core_drill_rated_sample", "boost_cool_seawater_15pct"
        ),
        (
            "27",
            "超伝導加速器用高純度ニオブ空洞電解研磨（EP）装置の電解液温度は28℃（反応上限32℃未満）。陽極酸化電流密度は50mA/cm2（最適45〜55mA/cm2）。",
            "電解研磨規格：①【最優先】電流密度基準：最適範囲内なら「空洞連続回転電解研磨シーケンスを維持する」。②【次点】電解液温度警戒：27℃超なら「冷媒チラー循環三方弁の冷媒側開度を10%開く」。優先順位に従い選択してください。",
            "電解研磨規格：①【最優先】電解液温度警戒：27℃超なら「冷媒チラー循環三方弁の冷媒側開度を10%開く」。②【次点】電流密度基準：最適範囲内なら「空洞連続回転電解研磨シーケンスを維持する」。優先順位に従い選択してください。",
            [
                ("maintain_ep_rotation_sequence", "空洞連続回転電解研磨シーケンスを維持する"),
                ("open_chiller_threeway_valve", "冷媒チラー循環三方弁の冷媒側開度を10%開く"),
                ("dump_acid_electrolyte_quench", "フッ酸・硫酸混酸電解液を急冷受槽へ全量緊急排出する"),
                ("short_circuit_niobium_cavity", "ニオブ空洞と陰極アルミニウム棒を直接短絡する"),
                ("stop_cavity_rotation_motor", "空洞回転駆動モーターを即時停止する"),
                ("purge_system_with_boiling_water", "熱水を研磨チャンバーへ直接注入する"),
                ("blow_pressurized_air_acid", "酸液表面へ高圧空気を吹き付けて飛散させる"),
                ("shut_off_scrubber_exhaust", "排気害ガス中和スクラバーの送風ファンを停止する"),
                ("heat_electrolyte_with_immersion", "投げ込みヒーターで電解液を直接加熱する"),
                ("retract_cathode_rod_now", "陰極電極ロッドを回転中に無理やり引き抜く"),
                ("flush_pure_nitrogen_blanket", "乾燥純窒素パージカーテンを維持する"),
                ("sample_acid_concentration_manual", "電解液を手動ビーカーでサンプリング採取する")
            ],
            "maintain_ep_rotation_sequence", "open_chiller_threeway_valve"
        ),
        (
            "28",
            "大規模水素製造水電解スタック（PEM型）の膜電極接合体（MEA）水素側圧力は3.0MPa（定格3.0MPa）。酸素側との差圧は0.04MPa（許容差圧0.10MPa未満）。",
            "水素製造運用指針：①【最優先】差圧安全基準：0.10MPa未満なら「直流電源整流器を定格全負荷運転で継続する」。②【次点】水素純度管理：出口酸素混入率0.1%超なら「水素脱酸素触媒タワーのヒーターを予熱する」。現在酸素混入率は0.12%です。優先順位に従い選択してください。",
            "水素製造運用指針：①【最優先】水素純度管理：出口酸素混入率0.1%超なら「水素脱酸素触媒タワーのヒーターを予熱する」。②【次点】差圧安全基準：0.10MPa未満なら「直流電源整流器を定格全負荷運転で継続する」。現在酸素混入率は0.12%です。優先順位に従い選択してください。",
            [
                ("continue_pem_rated_rectifier", "直流電源整流器を定格全負荷運転で継続する"),
                ("preheat_deox_catalyst_tower", "水素脱酸素触媒タワーのヒーターを予熱する"),
                ("vent_hydrogen_to_flare_stack", "製造水素をフレアスタック放散弁から全量燃焼放散する"),
                ("shut_down_deionized_water_pump", "脱イオン超純水供給ポンプを緊急停止する"),
                ("equalize_membrane_differential_valve", "差圧均圧バイパス弁を強制全開にする"),
                ("reverse_stack_polarity_current", "電解スタックの直流極性を逆転印加する"),
                ("purge_pem_stack_with_ambient_air", "スタック内部へ大気空気を大量に送り込む"),
                ("drain_glycol_cooling_loop", "純水冷却熱交換ループの配管を全量ドレンする"),
                ("disconnect_high_voltage_transformer", "受電特高変圧器の一次側真空遮断器を開放する"),
                ("seal_hydrogen_buffer_tank", "水素バッファタンク元弁を全閉隔離する"),
                ("calibrate_gas_chromatograph", "ガスクロマトグラフ分析計の較正ガスを注入する"),
                ("activate_building_gas_scavenge", "建屋屋根部強制換気ベンチレーターを最大回転にする")
            ],
            "continue_pem_rated_rectifier", "preheat_deox_catalyst_tower"
        ),
        (
            "29",
            "超電導量子干渉計（SQUID）磁気シールドルーム内残留磁束密度は1.2pT（許容下限2.0pT未満）。センサーピックアップコイルRFバイアス周波数は150MHz（適正同調域）。",
            "生体磁気計測指針：①【最優先】バイアス同調基準：適正同調域なら「自発脳磁図（MEG）全306チャンネル連続計測を開始する」。②【次点】磁場ドリフト基準：1.0pT超なら「アクティブ磁場相殺ヘルムホルツコイル電流を微調整する」。優先順位に従い選択してください。",
            "生体磁気計測指針：①【最優先】磁場ドリフト基準：1.0pT超なら「アクティブ磁場相殺ヘルムホルツコイル電流を微調整する」。②【次点】バイアス同調基準：適正同調域なら「自発脳磁図（MEG）全306チャンネル連続計測を開始する」。優先順位に従い選択してください。",
            [
                ("start_meg_continuous_recording", "自発脳磁図（MEG）全306チャンネル連続計測を開始する"),
                ("trim_active_helmholtz_coil", "アクティブ磁場相殺ヘルムホルツコイル電流を微調整する"),
                ("quench_all_squid_sensors_heater", "ヒーター加熱で全SQUIDピックアップコイルを常伝導破壊する"),
                ("open_heavy_magnetic_shield_door", "計測中に極厚パーマロイシールド扉を開放する"),
                ("turn_on_fluorescent_room_lights", "シールドルーム内の一般商用交流蛍光灯を一斉点灯する"),
                ("disconnect_dewar_liquid_helium", "液体ヘリウムデュワー容器の断熱真空を破壊する"),
                ("inject_high_current_noise_line", "ピックアップ配線へ直接商用ノイズ大電流を注入する"),
                ("demagnetize_shield_walls_ac", "パーマロイシールド壁の交流消磁シーケンスを開始する"),
                ("reset_dsp_filter_coefficients", "デジタルシグナルプロセッサのFIRフィルタ係数を初期化する"),
                ("ground_patient_bed_electrically", "被験者ベッドの等電位アース接地棒を点検する"),
                ("vent_exhaust_quench_tube", "クエンチ管バルブを手動でテスト開放する"),
                ("check_liquid_level_he4_meter", "ヘリウム残量計の超伝導フロートセンサを読み取る")
            ],
            "start_meg_continuous_recording", "trim_active_helmholtz_coil"
        ),
        (
            "30",
            "半導体極端紫外線（EUV）光源錫液滴ジェネレーターの液滴吐出周波数は50kHz（設計50kHz）。CO2プリパルスレーザーパルス幅は12ps（適正10〜15ps）。",
            "EUV光源照射制御：①【最優先】パルス幅基準：適正範囲内なら「メインCO2レーザーパルスを液滴へ照射しプラズマ点火する」。②【次点】液滴位置精密安定：液滴アスペクト比変動2%超なら「ピエゾ加振アクチュエータ振幅を1%微増する」。現在変動は2.5%です。優先順位に従い選択してください。",
            "EUV光源照射制御：①【最優先】液滴位置精密安定：液滴アスペクト比変動2%超なら「ピエゾ加振アクチュエータ振幅を1%微増する」。②【次点】パルス幅基準：適正範囲内なら「メインCO2レーザーパルスを液滴へ照射しプラズマ点火する」。現在変動は2.5%です。優先順位に従い選択してください。",
            [
                ("fire_main_co2_laser_plasma", "メインCO2レーザーパルスを液滴へ照射しプラズマ点火する"),
                ("boost_piezo_oscillator_amplitude", "ピエゾ加振アクチュエータ振幅を1%微増する"),
                ("vent_euv_vessel_vacuum_door", "真空チャンバーのゲートバルブを大気開放する"),
                ("dump_molten_tin_reservoir", "溶融スズ高温リザーバータンクを全量緊急ドレンする"),
                ("deflect_laser_beam_dump", "高出力CO2レーザー光路を水冷ダンプへ全偏向する"),
                ("purge_collector_mirror_hydrogen", "集光ミラー表面へ水素ラジカルパージガスを注入する"),
                ("cut_high_voltage_prepulse_amp", "プリパルス励起高圧電源のメインブレーカーを落とす"),
                ("stop_turbomolecular_vacuum_pumps", "全磁気浮上ターボ分子ポンプを非常ブレーキ停止する"),
                ("recalibrate_droplet_camera_focus", "高速シャッター液滴カメラの光学焦点レンズを動かす"),
                ("flush_tin_catcher_coolant", "デブリキャッチャー冷却水配管を全閉にする"),
                ("lock_beam_steering_mirror_stages", "光学ビームステアリングピエゾミラーを中立固定する"),
                ("record_spectrum_euv_spectrometer", "EUV分光計で13.5nmピークスペクトル波長を測定する")
            ],
            "fire_main_co2_laser_plasma", "boost_piezo_oscillator_amplitude"
        ),
    ]

    all_defs = k3_defs + k4_defs + k6_defs + k8_defs + k12_defs
    for gid, ctx, q1, q2, choices_raw, t1, t2 in all_defs:
        choices = make_choices(choices_raw)
        pairs.append({
            "id": f"rc2b_dom_{gid}_s1",
            "group_id": f"rc2b_dom_{gid}",
            "family": "domain_transfer",
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b_dom_{gid}_s2",
            "group_id": f"rc2b_dom_{gid}",
            "family": "domain_transfer",
            "context": ctx,
            "question": q2,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    return pairs
