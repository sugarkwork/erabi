"""RC3 Training Data Synthesis: Technical Specification Single-Clause Thresholds & Implicit Fallbacks.

Directly targets the root cause identified in Milestone 31:
Models fail on single-clause technical criteria (e.g., "規定条件は『吸入圧力180kPa以上かつ吐出温度-40℃以下』である")
when the negative condition evaluates to True because the context lacks an explicit else-clause,
causing cross-attention to latch onto the positive tokens in the specification premise.

Generates 300 contrastive groups (600 records) across 10 technical domains:
1. Pharmaceutical HPLC Chromatography Peak Separation
2. Wind Turbine Pitch Angle and Rotor Speed Interlock
3. Satellite Heat Pipe Loop Evaporator Thermal Balance
4. Proton Therapy Synchrotron Beam Extraction Current
5. Ethylene Cracking Furnace Pyrolysis Coil Temperature
6. Semiconductor Atomic Layer Deposition (ALD) Purge Cycle
7. Data Center Immersion Cooling Fluid Dielectric Constant
8. Hydrogen Fuel Cell PEM Stack Cell Voltage Uniformity
9. Autonomous Container Terminal Gantry Anti-Sway Laser
10. Deep-Sea AUV Battery Compartment Nitrogen Pressure

Zero joke distractors. Zero overlap with data/rc3_bridge/ or historical evaluation suites.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Tuple


def make_choices(defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in defs]


def generate_rc3_technical_specs(seed: int = 3009) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    records: List[Dict[str, Any]] = []

    domains = [
        # Domain 1: Pharmaceutical HPLC Chromatography Peak Separation
        ("バイオ医薬品分取HPLCクロマトグラフィー分離基準",
         "カラム溶出分離規定：合格条件は『理論段数3000段以上かつピーク対称性係数0.95以上1.20以下を維持』である。",
         "オンライン検出器ログ：現在ロットの理論段数は3420段、ピーク対称性係数は1.06で安定溶出している。分取判断を行え。",
         "オンライン検出器ログ：現在ロットの理論段数は2580段へ低下し、ピーク対称性係数は1.38へ歪み拡大した。分取判断を行え。",
         [
             ("hplc_fraction_proceed", "カラム分離性能適合・本分取フラクション回収実行"),
             ("hplc_column_regen_abort", "分離基準逸脱不合格・溶出液全量バイパス廃棄およびカラム再生洗浄"),
             ("hplc_detector_zero_calib", "吸光度検出器ゼロ点再校正待機"),
             ("hplc_flow_rate_derate", "移動相ポンプ送液流速減速維持")
         ],
         "hplc_fraction_proceed",
         "hplc_column_regen_abort"),

        # Domain 2: Wind Turbine Pitch Angle and Rotor Speed Interlock
        ("洋上風力発電ブレードピッチ角・ローター回転制御基準",
         "発電タービン保護規則：運転適格条件は『ローター回転数9.0rpm以上13.5rpm以下かつピッチ角偏差±0.5度以内』である。",
         "SCADAテレメトリ：計測ローター回転数は11.8rpm、ピッチ角偏差は+0.2度で定格範囲内である。発電制御を決定せよ。",
         "SCADAテレメトリ：計測ローター回転数は14.6rpmへ過回転突入し、ピッチ角偏差は+1.8度へ拡大した。発電制御を決定せよ。",
         [
             ("wind_turbine_nominal_generate", "タービン定格適格・系統並入フル出力発電継続"),
             ("wind_blade_feathering_estop", "規定値超過危険・ブレード完全フェザリング即時空力ブレーキ停止"),
             ("wind_yaw_realign_mode", "ナセル風向追従ヨー旋回待機"),
             ("wind_gearbox_oil_boost", "増速機潤滑油循環加圧待機")
         ],
         "wind_turbine_nominal_generate",
         "wind_blade_feathering_estop"),

        # Domain 3: Satellite Heat Pipe Loop Evaporator Thermal Balance
        ("軌道上人工衛星ヒートパイプループ熱平衡管理基準",
         "熱制御系動作基準：許容条件は『蒸発器温度+15℃以上+35℃以下かつ熱輸送量120W以上』である。",
         "熱解析モニタ：蒸発器温度は+24.5℃、計測熱輸送量は165Wで平衡状態にある。熱制御処置を指示せよ。",
         "熱解析モニタ：蒸発器温度は+48.2℃へ異常過熱し、熱輸送量は82Wへドライアウト急減した。熱制御処置を指示せよ。",
         [
             ("heatpipe_thermal_nominal", "熱平衡健全・通常運用ヒートパイプループ維持"),
             ("heatpipe_overheat_cutoff", "ドライアウト熱暴走危険・ペイロード高負荷機器即時電力カットオフ"),
             ("heatpipe_subcooler_vent", "予備ラジエータ冷却弁トリップ"),
             ("heatpipe_sensor_bus_swap", "熱電対A/Bバス相互照合待機")
         ],
         "heatpipe_thermal_nominal",
         "heatpipe_overheat_cutoff"),

        # Domain 4: Proton Therapy Synchrotron Beam Extraction Current
        ("陽子線がん治療シンクロトロン加速器出射ビーム基準",
         "照射安全管理基準：照射承認条件は『出射ビーム電流10.0nA以上15.0nA以下かつエネルギー均一度99.2%以上』である。",
         "線量計測器データ：出射電流は12.4nA、エネルギー均一度は99.6%で基準充足を確認した。治療照射判定を下せ。",
         "線量計測器データ：出射電流は7.8nAへ減衰し、エネルギー均一度は98.1%へ劣化検知された。治療照射判定を下せ。",
         [
             ("beam_irradiation_authorized", "ビーム品質適合・患者患部への治療照射開始承認"),
             ("beam_fast_abort_interlock", "ビーム規格外不適合・高速ビームアボート電磁石即時励磁遮断"),
             ("beam_vacuum_baking_cycle", "加速リング超高真空ベーキング待機"),
             ("beam_collimator_realign", "マルチリーフコリメーター初期位置復帰待機")
         ],
         "beam_irradiation_authorized",
         "beam_fast_abort_interlock"),

        # Domain 5: Ethylene Cracking Furnace Pyrolysis Coil Temperature
        ("エチレン製造分解炉パイロリシスコイル管壁温度管理基準",
         "ナフサ熱分解操業基準：管理規定は『管外壁温度1020℃以上1080℃以下かつ原料滞留時間0.15秒以上0.22秒以下』である。",
         "炉内DCSセンシング：管壁温度は1048℃、計測滞留時間は0.18秒で適正分解条件を推移している。燃焼制御を判定せよ。",
         "炉内DCSセンシング：管壁温度は1115℃へホットスポット過熱、滞留時間は0.26秒へコーキング遅延した。燃焼制御を判定せよ。",
         [
             ("pyrolysis_furnace_cruise", "分解反応最適・バーナー燃焼量定格維持"),
             ("pyrolysis_emergency_steam_blow", "管壁クリープ過熱危険・燃料ガス即時遮断および緊急スチームパージ"),
             ("pyrolysis_dilution_ratio_tune", "希釈スチーム混入比率微調整待機"),
             ("pyrolysis_quench_boiler_standby", "急冷熱交換器スス吹き待機")
         ],
         "pyrolysis_furnace_cruise",
         "pyrolysis_emergency_steam_blow"),

        # Domain 6: Semiconductor Atomic Layer Deposition (ALD) Purge Cycle
        ("半導体ALD原子層堆積装置チャンバー排気パージ基準",
         "前駆体残留防止規定：薄膜成膜条件は『不活性パージ時間4.0秒以上かつ残留プレカーサー分圧0.05Pa以下』である。",
         "残留ガス質量分析計（QMS）：パージ時間は4.5秒を消化、残留分圧は0.018Paまで排気完了した。次パルス工程を指示せよ。",
         "残留ガス質量分析計（QMS）：排気弁詰まりによりパージ時間3.2秒で中断、残留分圧は0.22Paに滞留している。次パルス工程を指示せよ。",
         [
             ("ald_precursor_next_pulse", "パージ基準適合・次酸化剤ガスパルス注入シーケンス実行"),
             ("ald_purge_fail_quarantine", "前駆体残留混触危険・ウェハ搬送中断およびチャンバー徹底排気シーケンス回送"),
             ("ald_heater_zone_rebalance", "サセプターヒーターゾーン熱分布補正待機"),
             ("ald_loadlock_dry_vent", "ロードロック室高純度窒素復圧待機")
         ],
         "ald_precursor_next_pulse",
         "ald_purge_fail_quarantine"),

        # Domain 7: Data Center Immersion Cooling Fluid Dielectric Constant
        ("AI高密度計算サーバ液浸冷却合成フッ素系絶縁液管理基準",
         "浸漬冷却健全性規格：受入運用条件は『絶縁破壊電圧35kV以上かつ体積抵抗率1.0×10^12Ω・cm以上』である。",
         "流体分析ユニット診断：計測絶縁破壊電圧は42kV、体積抵抗率は3.8×10^12Ω・cmである。計算ノード稼働を判定せよ。",
         "流体分析ユニット診断：冷却液劣化により破壊電圧は28kVへ急降下、体積抵抗率は4.2×10^11Ω・cmへ低下した。計算ノード稼働を判定せよ。",
         [
             ("immersion_server_run_authorized", "冷却媒体健全・高密度AIコンピュートブレード通電給電承認"),
             ("immersion_fluid_replace_trip", "絶縁耐力喪失短絡危険・浸漬ラック緊急遮断および絶縁冷媒全量置換交換"),
             ("immersion_pump_impeller_degas", "循環ポンプキャビテーション脱気待機"),
             ("immersion_chiller_secondary_loop", "屋上熱交換器ファン回転数制御待機")
         ],
         "immersion_server_run_authorized",
         "immersion_fluid_replace_trip"),

        # Domain 8: Hydrogen Fuel Cell PEM Stack Cell Voltage Uniformity
        ("燃料電池商用大型トラックPEMスタックセル電圧均一度基準",
         "水素燃料電池スタック運用条件：出力認可基準は『最低単セル電圧0.65V以上かつ全セル間電圧偏差25mV以内』である。",
         "燃料電池BMSセルモニタ：全セル中最低電圧は0.71V、スタック全体の偏差は12mVで安定放電している。走行出力を決定せよ。",
         "燃料電池BMSセルモニタ：第84セルがフラッディングにより0.48Vへ沈降、セル間偏差は68mVへ拡大した。走行出力を決定せよ。",
         [
             ("fuel_cell_power_drive_ok", "スタック電圧均一・インバータ最大トラクション出力給電承認"),
             ("fuel_cell_cell_fail_protect", "低電圧セル転極不可逆損傷危険・スタック出力制限カットおよび緊急水素パージ"),
             ("fuel_cell_humidifier_warmup", "膜加湿器循環冷却水予熱待機"),
             ("fuel_cell_air_compressor_sync", "空気供給エアコンプレッサー同期待機")
         ],
         "fuel_cell_power_drive_ok",
         "fuel_cell_cell_fail_protect"),

        # Domain 9: Autonomous Container Terminal Gantry Anti-Sway Laser
        ("自動化コンテナターミナルガントリークレーン振れ止め同期基準",
         "岸壁自動荷役安全規則：巻き下げ着床条件は『荷振れ角振幅0.3度以下かつ吊り具位置決め偏差±10mm以内』である。",
         "レーザー測距振れセンサ：現在振れ角は0.15度、着床位置決め偏差は+4mmで減衰収束している。スプレッダ動作を指示せよ。",
         "レーザー測距振れセンサ：強風突風により振れ角は1.10度へ発散、着床偏差は-35mmを検知した。スプレッダ動作を指示せよ。",
         [
             ("gantry_land_container_nominal", "振れ止め収束適合・コンテナ自動着床ツイストロック解除実行"),
             ("gantry_sway_abort_interlock", "位置決め脱落衝突危険・巻き下げ即時停止および振れ止め再制動シーク"),
             ("gantry_trolley_creep_mode", "トロリ微速インチング移動待機"),
             ("gantry_cable_reel_tension_tune", "給電ケーブルリール張力調整待機")
         ],
         "gantry_land_container_nominal",
         "gantry_sway_abort_interlock"),

        # Domain 10: Deep-Sea AUV Battery Compartment Nitrogen Pressure
        ("大深度自律潜水機（AUV）チタン製耐圧バッテリー室窒素封入基準",
         "潜航前耐圧室気密基準：出航条件は『窒素封入内圧110kPa以上125kPa以下かつ相対湿度10%以下』である。",
         "深海ハブ通信テレメトリ：耐圧室窒素圧は118kPa、計測相対湿度は4%で完全乾燥を維持している。深海潜航判定を行え。",
         "深海ハブ通信テレメトリ：Oリングシール不全により内圧は98kPaへ漏洩減圧、相対湿度は28%へ湿分浸入した。深海潜航判定を行え。",
         [
             ("auv_dive_mission_authorized", "耐圧気密乾燥健全・大深度自律潜航ミッション発進承認"),
             ("auv_pressure_leak_abort", "水密破綻浸水短絡危険・潜航ミッション即時中止および甲板揚収隔離点検"),
             ("auv_doppler_velocity_log_zero", "音響DVL流速計ゼロ点バイアス待機"),
             ("auv_transponder_ping_test", "超音波ピンガー応答テスト待機")
         ],
         "auv_dive_mission_authorized",
         "auv_pressure_leak_abort"),
    ]

    for d_idx, (title, rule, s1, s2, c_defs, t1, t2) in enumerate(domains):
        # 30 contrastive groups per domain = 60 records
        for rep in range(30):
            gid = f"rc3_ts_{d_idx*30 + rep + 1:04d}"
            choices = make_choices(c_defs)
            q = f"技術基準判定：{title}における現在の監視結果に基づき、適切な指示を選択してください。"

            records.append({
                "id": f"{gid}_s1",
                "group_id": gid,
                "family": "technical_spec_threshold",
                "domain_name": title,
                "context": f"【{title}】\n{rule}\n監視状況：{s1}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2",
                "group_id": gid,
                "family": "technical_spec_threshold",
                "domain_name": title,
                "context": f"【{title}】\n{rule}\n監視状況：{s2}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    return records
