"""Family 5: domain_transfer (30 pairs, 60 cases) - Blind v3
Distribution: K=3 (5 pairs), K=4 (10 pairs), K=6 (5 pairs), K=8 (5 pairs), K=12 (5 pairs)
Prefix: rc2b3_dom_
Optimized concise choice texts for K=12 to guarantee strict token count <= 350 (< 512 limit).
"""

from typing import Any, Dict, List, Tuple
from blind_v2_data.family_domain_transfer import get_domain_transfer_pairs as get_v2_dom


def make_choices(c_defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in c_defs]


def get_domain_transfer_pairs() -> List[Dict[str, Any]]:
    v2_pairs = get_v2_dom()
    v3_pairs = []

    # Groups 01 to 25 from v2 (K=3, 4, 6, 8)
    for c in v2_pairs:
        gid = c["group_id"].replace("rc2b_dom_", "")
        idx = int(gid)
        if idx <= 25:
            c_new = dict(c)
            c_new["id"] = c["id"].replace("rc2b_dom_", "rc2b3_dom_")
            c_new["group_id"] = c["group_id"].replace("rc2b_dom_", "rc2b3_dom_")
            v3_pairs.append(c_new)

    # Groups 26 to 30 (K=12) with concise choices
    k12_concise_defs = [
        (
            "26",
            "海洋海底熱水鉱床掘削サンプラー『V-DEEP』のドリルビット温度は78℃（許容100℃未満）。海水冷却ポンプ循環吐出圧は2.8MPa（基準2.5MPa以上）。",
            "サンプリング手順：①【最優先】冷却圧基準：2.5MPa以上なら「油圧コアリング採取」。②【次点】熱水温度監視：70℃超なら「冷却海水ポンプ15%増量」。優先順位に従い選択してください。",
            "サンプリング手順：①【最優先】熱水温度監視：70℃超なら「冷却海水ポンプ15%増量」。②【次点】冷却圧基準：2.5MPa以上なら「油圧コアリング採取」。優先順位に従い選択してください。",
            [
                ("core_drill_rated_sample", "油圧コアリング採取"),
                ("boost_cool_seawater_15pct", "冷却海水ポンプ15%増量"),
                ("dump_core_barrel_sea_floor", "コアバレル海底投棄"),
                ("reverse_drill_bit_max_torque", "ドリル逆回転引抜"),
                ("close_sampling_gate_valve", "ゲート弁緊急閉止"),
                ("flush_drill_string_with_glycol", "不凍液フラッシング"),
                ("jettison_rov_tether_cable", "テザーケーブル切断"),
                ("blow_ballast_ascent_now", "バラスト緊急放出浮上"),
                ("shut_down_hydraulic_power_pack", "水中油圧主電動機停止"),
                ("illuminate_high_intensity_led", "大光量LED深海探照灯点灯"),
                ("calibrate_acoustic_transponder", "音響トランスポンダ再較正"),
                ("lock_manipulator_wrist_joint", "手首関節ラチェット固定")
            ],
            "core_drill_rated_sample", "boost_cool_seawater_15pct"
        ),
        (
            "27",
            "超伝導加速器用高純度ニオブ空洞電解研磨（EP）装置の電解液温度は28℃（反応上限32℃未満）。陽極酸化電流密度は50mA/cm2（最適45〜55mA/cm2）。",
            "電解研磨規格：①【最優先】電流密度基準：最適範囲内なら「空洞電解研磨継続」。②【次点】電解液温度警戒：27℃超なら「冷媒三方弁開度10%開」。優先順位に従い選択してください。",
            "電解研磨規格：①【最優先】電解液温度警戒：27℃超なら「冷媒三方弁開度10%開」。②【次点】電流密度基準：最適範囲内なら「空洞電解研磨継続」。優先順位に従い選択してください。",
            [
                ("maintain_ep_rotation_sequence", "空洞電解研磨継続"),
                ("open_chiller_threeway_valve", "冷媒三方弁開度10%開"),
                ("dump_acid_electrolyte_quench", "混酸電解液緊急排出"),
                ("short_circuit_niobium_cavity", "空洞と陰極を直接短絡"),
                ("stop_cavity_rotation_motor", "回転駆動モーター即時停止"),
                ("purge_system_with_boiling_water", "熱水直接注入"),
                ("blow_pressurized_air_acid", "酸液表面へ高圧空気吹付"),
                ("shut_off_scrubber_exhaust", "排ガススクラバー停止"),
                ("heat_electrolyte_with_immersion", "投げ込みヒーター加熱"),
                ("retract_cathode_rod_now", "陰極ロッド回転中引抜"),
                ("flush_pure_nitrogen_blanket", "乾燥純窒素パージ維持"),
                ("sample_acid_concentration_manual", "電解液手動サンプリング")
            ],
            "maintain_ep_rotation_sequence", "open_chiller_threeway_valve"
        ),
        (
            "28",
            "大規模水素製造水電解スタック（PEM型）の膜電極接合体（MEA）水素側圧力は3.0MPa（定格3.0MPa）。酸素側との差圧は0.04MPa（許容差圧0.10MPa未満）。",
            "水素製造運用指針：①【最優先】差圧安全基準：0.10MPa未満なら「整流器定格全負荷運転継続」。②【次点】水素純度管理：出口酸素混入率0.1%超なら「脱酸素触媒ヒーター予熱」。現在酸素混入率は0.12%です。優先順位に従い選択してください。",
            "水素製造運用指針：①【最優先】水素純度管理：出口酸素混入率0.1%超なら「脱酸素触媒ヒーター予熱」。②【次点】差圧安全基準：0.10MPa未満なら「整流器定格全負荷運転継続」。現在酸素混入率は0.12%です。優先順位に従い選択してください。",
            [
                ("continue_pem_rated_rectifier", "整流器定格全負荷運転継続"),
                ("preheat_deox_catalyst_tower", "脱酸素触媒ヒーター予熱"),
                ("vent_hydrogen_to_flare_stack", "製造水素フレア燃焼放散"),
                ("shut_down_deionized_water_pump", "超純水ポンプ緊急停止"),
                ("equalize_membrane_differential_valve", "差圧均圧弁強制全開"),
                ("reverse_stack_polarity_current", "電解スタック直流逆転印加"),
                ("purge_pem_stack_with_ambient_air", "スタック大気空気送込"),
                ("drain_glycol_cooling_loop", "純水冷却ループ全量ドレン"),
                ("disconnect_high_voltage_transformer", "特高一次側遮断器開放"),
                ("seal_hydrogen_buffer_tank", "水素バッファタンク元弁閉止"),
                ("calibrate_gas_chromatograph", "ガスクロ分析計較正"),
                ("activate_building_gas_scavenge", "建屋屋根換気ファン最大")
            ],
            "continue_pem_rated_rectifier", "preheat_deox_catalyst_tower"
        ),
        (
            "29",
            "超電導量子干渉計（SQUID）磁気シールドルーム内残留磁束密度は1.2pT（許容下限2.0pT未満）。センサーピックアップコイルRFバイアス周波数は150MHz（適正同調域）。",
            "生体磁気計測指針：①【最優先】バイアス同調基準：適正同調域なら「自発脳磁図全306ch計測開始」。②【次点】磁場ドリフト基準：1.0pT超なら「相殺ヘルムホルツ電流微調整」。優先順位に従い選択してください。",
            "生体磁気計測指針：①【最優先】磁場ドリフト基準：1.0pT超なら「相殺ヘルムホルツ電流微調整」。②【次点】バイアス同調基準：適正同調域なら「自発脳磁図全306ch計測開始」。優先順位に従い選択してください。",
            [
                ("start_meg_continuous_recording", "自発脳磁図全306ch計測開始"),
                ("trim_active_helmholtz_coil", "相殺ヘルムホルツ電流微調整"),
                ("quench_all_squid_sensors_heater", "ヒーター加熱常伝導破壊"),
                ("open_heavy_magnetic_shield_door", "パーマロイ扉開放"),
                ("turn_on_fluorescent_room_lights", "室内商用交流蛍光灯点灯"),
                ("disconnect_dewar_liquid_helium", "液体ヘリウム断熱真空破壊"),
                ("inject_high_current_noise_line", "ピックアップ配線大電流注入"),
                ("demagnetize_shield_walls_ac", "シールド壁交流消磁開始"),
                ("reset_dsp_filter_coefficients", "DSPフィルタ係数初期化"),
                ("ground_patient_bed_electrically", "被験者ベッド接地棒点検"),
                ("vent_exhaust_quench_tube", "クエンチ管バルブテスト開放"),
                ("check_liquid_level_he4_meter", "ヘリウム残量計読取")
            ],
            "start_meg_continuous_recording", "trim_active_helmholtz_coil"
        ),
        (
            "30",
            "半導体極端紫外線（EUV）光源錫液滴ジェネレーターの液滴吐出周波数は50kHz（設計50kHz）。CO2プリパルスレーザーパルス幅は12ps（適正10〜15ps）。",
            "EUV光源照射制御：①【最優先】パルス幅基準：適正範囲内なら「CO2レーザー照射プラズマ点火」。②【次点】液滴位置精密安定：液滴変動2%超なら「ピエゾ加振振幅1%微増」。現在変動は2.5%です。優先順位に従い選択してください。",
            "EUV光源照射制御：①【最優先】液滴位置精密安定：液滴変動2%超なら「ピエゾ加振振幅1%微増」。②【次点】パルス幅基準：適正範囲内なら「CO2レーザー照射プラズマ点火」。現在変動は2.5%です。優先順位に従い選択してください。",
            [
                ("fire_main_co2_laser_plasma", "CO2レーザー照射プラズマ点火"),
                ("boost_piezo_oscillator_amplitude", "ピエゾ加振振幅1%微増"),
                ("vent_euv_vessel_vacuum_door", "真空チャンバー大気開放"),
                ("dump_molten_tin_reservoir", "溶融スズタンク緊急ドレン"),
                ("deflect_laser_beam_dump", "レーザー水冷ダンプ全偏向"),
                ("purge_collector_mirror_hydrogen", "集光ミラー水素ラジカルパージ"),
                ("cut_high_voltage_prepulse_amp", "プリパルス高圧電源落とす"),
                ("stop_turbomolecular_vacuum_pumps", "ターボ分子ポンプブレーキ停止"),
                ("recalibrate_droplet_camera_focus", "液滴カメラ焦点レンズ移動"),
                ("flush_tin_catcher_coolant", "デブリキャッチャー冷却水全閉"),
                ("lock_beam_steering_mirror_stages", "ピエゾミラー中立固定"),
                ("record_spectrum_euv_spectrometer", "EUV分光計波長測定")
            ],
            "fire_main_co2_laser_plasma", "boost_piezo_oscillator_amplitude"
        ),
    ]

    for gid, ctx, q1, q2, choices_raw, t1, t2 in k12_concise_defs:
        choices = make_choices(choices_raw)
        v3_pairs.append({
            "id": f"rc2b3_dom_{gid}_s1",
            "group_id": f"rc2b3_dom_{gid}",
            "family": "domain_transfer",
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        v3_pairs.append({
            "id": f"rc2b3_dom_{gid}_s2",
            "group_id": f"rc2b3_dom_{gid}",
            "family": "domain_transfer",
            "context": ctx,
            "question": q2,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    return v3_pairs
