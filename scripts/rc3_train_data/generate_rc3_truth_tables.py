"""RC3 Training Data Synthesis: Formal Truth Tables & Question-Contrastive Operator Rules.

Directly trains the model on truth-table operator reasoning (AND, OR, NOT, NOR, XOR, NAND)
under question-level contrastive pairs (same context state, distinct logical operators in Q1/Q2).

Generates 300 contrastive groups (600 records) across 10 distinct industrial/technical domains:
1. Satellite Telemetry & Deep-Space Downlink Channels (30 groups)
2. Semiconductor Chemical Vapor Deposition (CVD) Plasma Chambers (30 groups)
3. Thermal Power Supercritical Steam Bypass Valves (30 groups)
4. Railway Electronic Interlocking & Signal Switches (30 groups)
5. Nuclear Secondary Coolant Loop Makeup Pumps (30 groups)
6. Marine Diesel Engine Emergency Governor Tripping (30 groups)
7. Fiber Optic Dense Wavelength Division (DWDM) Transponders (30 groups)
8. High-Voltage Direct Current (HVDC) Converter Stations (30 groups)
9. Surgical Robotic Arm Articulation Safety Interlocks (30 groups)
10. Bioreactor Fermentation Dissolved Oxygen Aeration Loops (30 groups)

Zero overlap with data/rc3_bridge/. Zero joke distractors.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Tuple


def make_choices(defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in defs]


def generate_rc3_truth_tables(seed: int = 3008) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    records: List[Dict[str, Any]] = []

    domains = [
        # Domain 1: Satellite Telemetry & Downlink Channels
        ("人工衛星深宇宙通信ダウンリンク中継系",
         "テレメトリ受信ステータス：主中継器トランスポンダAはロック確立中（True）、予備トランスポンダBはビット同期外れ（False）。",
         "論理ルール：『主中継器Aと予備中継器Bの両方が同期（AND）』のときは『高精細画像データ全速伝送』、片方でも不成立なら『低速重要テレメトリ優先伝送へ退避』。指示せよ。",
         "論理ルール：『主中継器Aまたは予備中継器Bの少なくとも一方が同期（OR）』のときは『地上管制局受信セッションを継続』、双方が同期外れなら『衛星セーフホールド姿勢移行』。指示せよ。",
         [
             ("downlink_telemetry_safe_mode", "低速重要テレメトリ優先伝送へ退避"),
             ("downlink_high_speed_broadband", "高精細画像データ全速伝送"),
             ("downlink_ground_session_continue", "地上管制局受信セッションを継続"),
             ("downlink_safe_hold_attitude_trip", "衛星セーフホールド姿勢移行")
         ],
         "downlink_telemetry_safe_mode",
         "downlink_ground_session_continue"),

        # Domain 2: Semiconductor CVD Plasma Chambers
        ("半導体CVDプラズマ成膜チャンバー真空排気",
         "真空チャンバー排気系ステータス：ドライポンプ粗引き完了フラグは成立（True）、ターボ分子ポンプ定格回転到達フラグは未達（False）。",
         "論理ルール：『ドライポンプ粗引き完了かつターボ分子ポンプ定格到達（AND）』のときのみ『高周波プラズマ放電を開始』、片方でも未達なら『放電開始をインターロック阻止』。判定せよ。",
         "論理ルール：『ドライポンプ粗引きまたはターボ分子ポンプ定格のどちらか一方のみ成立（XOR）』のときは『チャンバー排気待機ステップを維持』、双方成立または双方未達なら『次工程判定へスキップ』。判定せよ。",
         [
             ("cvd_plasma_discharge_start", "高周波プラズマ放電を開始"),
             ("cvd_plasma_interlock_block", "放電開始をインターロック阻止"),
             ("cvd_pump_standby_maintain", "チャンバー排気待機ステップを維持"),
             ("cvd_advance_to_next_step", "次工程判定へスキップ")
         ],
         "cvd_plasma_interlock_block",
         "cvd_pump_standby_maintain"),

        # Domain 3: Thermal Power Supercritical Steam Bypass Valves
        ("火力発電超臨界蒸気バイパス配管安全弁",
         "高圧タービン蒸気弁センサー：第1高圧バイパス弁開度は基準内（False＝未開）、第2バイパス弁開度も基準内（False＝未開）。",
         "論理ルール：『第1バイパス弁も第2バイパス弁も共に全閉維持（NOR：否定論理和）』のときは『主タービン定常負荷運転を継続』、何らかの開弁があれば『負荷抑制制御』。判定せよ。",
         "論理ルール：『第1バイパス弁または第2バイパス弁のいずれか一方でも開弁（OR）』したときは『再熱器温度制御弁を作動』、両方未開なら『標準弁開度維持』。判定せよ。",
         [
             ("steam_steady_turbine_continue", "主タービン定常負荷運転を継続"),
             ("steam_load_curtailment_mode", "負荷抑制制御"),
             ("steam_reheater_temp_valve_run", "再熱器温度制御弁を作動"),
             ("steam_standard_valve_maintain", "標準弁開度維持")
         ],
         "steam_steady_turbine_continue",
         "steam_standard_valve_maintain"),

        # Domain 4: Railway Electronic Interlocking & Signal Switches
        ("鉄道電子連動装置進路制御ポイント転換",
         "軌道回路および転轍機ステータス：進路鎖錠フラグは確立中（True）、対向列車占有フラグは未占有（False）。",
         "論理ルール：『進路鎖錠確立かつ対向列車未占有（A AND NOT B）』のときのみ『出発信号機に進行現示（青信号）を出力』、それ以外なら『停止現示（赤信号）を維持』。指示せよ。",
         "論理ルール：『進路未鎖錠（NOT A）または対向列車占有（B）』のときは『転轍機転換インターロックを施錠』、両方正常なら『ポイント転換許可』。指示せよ。",
         [
             ("railway_signal_clear_green", "出発信号機に進行現示（青信号）を出力"),
             ("railway_signal_stop_red", "停止現示（赤信号）を維持"),
             ("railway_switch_interlock_lock", "転轍機転換インターロックを施錠"),
             ("railway_switch_permit_unlock", "ポイント転換許可")
         ],
         "railway_signal_clear_green",
         "railway_switch_permit_unlock"),

        # Domain 5: Nuclear Secondary Coolant Loop Makeup Pumps
        ("原子力二次冷却系補助給水ポンプ自動起動",
         "給水喪失検知信号：蒸気発生器低水位信号は発報中（True）、主給水ポンプ全台トリップ信号も発報中（True）。",
         "論理ルール：『低水位信号かつ主給水全台トリップの双方が成立（AND）』のとき『非常用ディーゼル駆動補助給水ポンプを即時自動起動』、片方のみなら『手動確認待機』。指示せよ。",
         "論理ルール：『低水位信号と主給水トリップ信号の不一致（XOR）』のときは『計装センサー不整合アラームを出力』、一致しているときは『一括シーケンス実行』。指示せよ。",
         [
             ("aux_feedwater_auto_start_trip", "非常用ディーゼル駆動補助給水ポンプを即時自動起動"),
             ("aux_feedwater_manual_verify_wait", "手動確認待機"),
             ("aux_feedwater_sensor_mismatch_alarm", "計装センサー不整合アラームを出力"),
             ("aux_feedwater_batch_sequence_run", "一括シーケンス実行")
         ],
         "aux_feedwater_auto_start_trip",
         "aux_feedwater_batch_sequence_run"),

        # Domain 6: Marine Diesel Engine Emergency Governor Tripping
        ("大型船舶ディーゼル主機関電子ガバナー過回転遮断",
         "機関回転センサー：電磁式ピックアップ回転数は過回転検知（True）、光電式クランク角センサーも過回転検知（True）。",
         "論理ルール：『電磁式または光電式のいずれか一方でも正常（NAND：否定論理積）』のときは『通常燃料噴射制御を維持』、双方が過回転検知なら『燃料噴射ラック急速遮断トリップ』。決定せよ。",
         "論理ルール：『電磁式と光電式の双方が同時に過回転検知（AND）』のとき『緊急遮断弁を作動し主機停止』、不一致なら『センサー個別キャリブレーション』。決定せよ。",
         [
             ("marine_maintain_normal_fuel_injection", "通常燃料噴射制御を維持"),
             ("marine_trip_fuel_rack_emergency_stop", "燃料噴射ラック急速遮断トリップ"),
             ("marine_shut_emergency_fuel_valve", "緊急遮断弁を作動し主機停止"),
             ("marine_individual_sensor_calibration", "センサー個別キャリブレーション")
         ],
         "marine_trip_fuel_rack_emergency_stop",
         "marine_shut_emergency_fuel_valve"),

        # Domain 7: Fiber Optic DWDM Transponders
        ("光海底ネットワークDWDM光トランスポンダー監視",
         "光シグナル品質メトリクス：光信号対雑音比（OSNR）規格割れ警報は非作動（False）、誤り訂正後BER超過警報も非作動（False）。",
         "論理ルール：『OSNR警報もBER超過も共に発生していない（NOR）』ときは『コヒーレント100Gbps伝送を定常維持』、何らかの警報があれば『変調多値度自動フォールバック』。判定せよ。",
         "論理ルール：『OSNR警報またはBER超過のいずれか一方が発生（OR）』したときは『予備波長光路へ保護切替（APS）』、両方正常なら『現用光路を保持』。判定せよ。",
         [
             ("dwdm_coherent_transmission_steady", "コヒーレント100Gbps伝送を定常維持"),
             ("dwdm_modulation_rate_fallback", "変調多値度自動フォールバック"),
             ("dwdm_aps_protection_switch", "予備波長光路へ保護切替（APS）"),
             ("dwdm_working_channel_retain", "現用光路を保持")
         ],
         "dwdm_coherent_transmission_steady",
         "dwdm_working_channel_retain"),

        # Domain 8: HVDC Converter Stations
        ("高圧直流送電（HVDC）交直変換所サイリスタ保護",
         "コンバータブリッジ異常検知：転流失敗（Commutation Failure）信号は検知（True）、直流過電圧信号は未検知（False）。",
         "論理ルール：『転流失敗検知または直流過電圧のいずれか一方でも発生（OR）』したときは『サイリスタゲートパルスを即時ブロック』、双方未発生なら『交直変換を継続』。指示せよ。",
         "論理ルール：『転流失敗かつ直流過電圧の双方が同時発生（AND）』のときのみ『主交流遮断器を開放し系統解列』、単独事象なら『自動リカバリーシーケンス』。指示せよ。",
         [
             ("hvdc_block_thyristor_gate_pulses", "サイリスタゲートパルスを即時ブロック"),
             ("hvdc_continue_conversion_steady", "交直変換を継続"),
             ("hvdc_trip_main_ac_breaker_isolate", "主交流遮断器を開放し系統解列"),
             ("hvdc_auto_recovery_sequence_run", "自動リカバリーシーケンス")
         ],
         "hvdc_block_thyristor_gate_pulses",
         "hvdc_auto_recovery_sequence_run"),

        # Domain 9: Surgical Robotic Arm Articulation Interlocks
        ("手術支援ロボットアーム関節可動域インターロック",
         "関節エンコーダー監視：第3関節角速度超過フラグは成立（True）、術者フットスイッチ押下フラグは非押下（False）。",
         "論理ルール：『角速度超過フラグとフットスイッチ押下の双方が成立（AND）』のとき『アクティブコンプライアンス制御を作動』、片方でも不成立なら『アーム関節電磁ブレーキを即時ロック』。指示せよ。",
         "論理ルール：『角速度超過またはフットスイッチ非押下のいずれか一方でも発生（OR）』のときは『術者コンソールに警告ダイアログを表示』、両方正常なら『警告なしで動作継続』。指示せよ。",
         [
             ("robot_active_compliance_run", "アクティブコンプライアンス制御を作動"),
             ("robot_joint_brake_immediate_lock", "アーム関節電磁ブレーキを即時ロック"),
             ("robot_display_warning_dialog", "術者コンソールに警告ダイアログを表示"),
             ("robot_continue_motion_without_warning", "警告なしで動作継続")
         ],
         "robot_joint_brake_immediate_lock",
         "robot_display_warning_dialog"),

        # Domain 10: Bioreactor Fermentation Dissolved Oxygen Aeration
        ("抗体医薬培養バイオリアクター溶存酸素（DO）制御",
         "溶存酸素センサー信号：光学DOプローブ低濃度フラグは未検知（False）、電気化学DOプローブ低濃度フラグも未検知（False）。",
         "論理ルール：『光学DOプローブも電気化学プローブも共に低濃度未検知（NOR）』のときは『純酸素ガス供給を抑止し通常空気スパージングを維持』、いずれか検知時は『酸素富化ライン全開』。判定せよ。",
         "論理ルール：『光学DOプローブまたは電気化学プローブのどちらか一方のみ低濃度検知（XOR）』のときは『二重化センサー整合性チェックを実施』、双方一致なら『自動制御継続』。判定せよ。",
         [
             ("bioreactor_air_sparging_normal_maintain", "純酸素ガス供給を抑止し通常空気スパージングを維持"),
             ("bioreactor_oxygen_enrichment_valve_open", "酸素富化ライン全開"),
             ("bioreactor_dual_sensor_consistency_check", "二重化センサー整合性チェックを実施"),
             ("bioreactor_auto_control_continue", "自動制御継続")
         ],
         "bioreactor_air_sparging_normal_maintain",
         "bioreactor_auto_control_continue"),
    ]

    for idx, (title, ctx, q1, q2, c_defs, t1, t2) in enumerate(domains):
        for rep in range(30):
            gid = f"rc3_trn_tt_{idx*30 + rep + 1:03d}"
            # Choices for s1
            s1_choices = [c for c in c_defs if c[0] in (t1, c_defs[1][0] if t1 == c_defs[0][0] else c_defs[0][0])]
            # Choices for s2
            s2_choices = [c for c in c_defs if c[0] in (t2, c_defs[3][0] if t2 == c_defs[2][0] else c_defs[2][0])]
            
            # If s1 choices don't have target, use full choices
            c1_list = make_choices(c_defs[:2] if t1 in (c_defs[0][0], c_defs[1][0]) else c_defs[2:])
            c2_list = make_choices(c_defs[2:] if t2 in (c_defs[2][0], c_defs[3][0]) else c_defs[:2])

            records.append({
                "id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": f"truth_table_{idx+1}",
                "context": f"【{title}】\n{ctx}", "question": q1, "choices": c1_list,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": f"truth_table_{idx+1}",
                "context": f"【{title}】\n{ctx}", "question": q2, "choices": c2_list,
                "target": {"kind": "hard", "choice_id": t2}
            })

    return records
