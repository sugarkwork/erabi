"""Blind v5 Family: Logical Operators (30 pairs, 60 cases).

Choice count distribution:
- K=2: 10 pairs (op_01 to op_10)
- K=3: 10 pairs (op_11 to op_20)
- K=4: 10 pairs (op_21 to op_30)
"""

from __future__ import annotations
from typing import Any, Dict, List


def get_logical_operators_pairs() -> List[Dict[str, Any]]:
    pairs = []

    # K=2: 10 pairs (01..10)
    k2_defs = [
        (
            "01",
            "マイクログリッドの自立単独運転判定基準。主遮断器補助接点Aは開路（True）、系統電圧ゼロクロス不検出Bは停電検知（True）。",
            "論理規程：『主接点開路Aかつ系統停電Bの両方成立（AND）』のとき『自立給電モードへ移行』、不成立なら『系統連系待機を維持』。指示せよ。",
            "grid_island_supply_mode",
            "マイクログリッドの自立単独運転判定基準。主遮断器補助接点Aは開路（True）、系統電圧ゼロクロス不検出Bは定常健全（False）。",
            "論理規程：『主接点開路Aかつ系統停電Bの両方成立（AND）』のとき『自立給電モードへ移行』、不成立なら『系統連系待機を維持』。指示せよ。",
            "grid_intertie_wait_maintain",
            [
                ("grid_island_supply_mode", "自立給電モードへ移行"),
                ("grid_intertie_wait_maintain", "系統連系待機を維持"),
            ],
        ),
        (
            "02",
            "無人搬送船の自動離着桟スラスタ安全論理。岸壁レーザー距離計Aは安全距離確保（False）、超音波近接センサBは接触域検知（True）。",
            "論理規程：『距離計Aまたは近接センサBのいずれか一方でも接触検知（OR）』のとき『自動スラスタ逆噴射停止』、両方未検知なら『定速接桟アプローチ継続』。指示せよ。",
            "tug_reverse_thrust_stop",
            "無人搬送船の自動離着桟スラスタ安全論理。岸壁レーザー距離計Aは安全距離確保（False）、超音波近接センサBも安全域（False）。",
            "論理規程：『距離計Aまたは近接センサBのいずれか一方でも接触検知（OR）』のとき『自動スラスタ逆噴射停止』、両方未検知なら『定速接桟アプローチ継続』。指示せよ。",
            "tug_berth_approach_keep",
            [
                ("tug_reverse_thrust_stop", "自動スラスタ逆噴射停止"),
                ("tug_berth_approach_keep", "定速接桟アプローチ継続"),
            ],
        ),
        (
            "03",
            "UPS静止形同期切替バイパス回路論理。商用電源周波数同期Aは同期完了（True）、インバーター直流過電圧フラグBは過電圧検出（True）。",
            "論理規程：『周波数同期A成立かつ直流過電圧B不発生（A AND NOT B）』のとき『直送バイパス切替承認』、不成立なら『バイパス切替阻止待機』。判断せよ。",
            "ups_bypass_inhibit_wait",
            "UPS静止形同期切替バイパス回路論理。商用電源周波数同期Aは同期完了（True）、インバーター直流過電圧フラグBは正常（False）。",
            "論理規程：『周波数同期A成立かつ直流過電圧B不発生（A AND NOT B）』のとき『直送バイパス切替承認』、不成立なら『バイパス切替阻止待機』。判断せよ。",
            "ups_bypass_transfer_ok",
            [
                ("ups_bypass_transfer_ok", "直送バイパス切替承認"),
                ("ups_bypass_inhibit_wait", "バイパス切替阻止待機"),
            ],
        ),
        (
            "04",
            "自律飛行ドローン編隊の衝突回避調停論理。左翼センサー警報Aは障害物検知（True）、右翼センサー警報Bは障害物検知（True）。",
            "論理規程：『警報Aと警報Bの不一致（XOR）』のとき『偏向回避ヨーイング旋回』、一致（両方検知または両方非検知）なら『垂直上昇緊急ホバリング』。指示せよ。",
            "drone_vertical_hover_climb",
            "自律飛行ドローン編隊の衝突回避調停論理。左翼センサー警報Aは障害物検知（True）、右翼センサー警報Bはクリア（False）。",
            "論理規程：『警報Aと警報Bの不一致（XOR）』のとき『偏向回避ヨーイング旋回』、一致（両方検知または両方非検知）なら『垂直上昇緊急ホバリング』。指示せよ。",
            "drone_yaw_evasive_turn",
            [
                ("drone_yaw_evasive_turn", "偏向回避ヨーイング旋回"),
                ("drone_vertical_hover_climb", "垂直上昇緊急ホバリング"),
            ],
        ),
        (
            "05",
            "体外式膜型人工肺（ECMO）の空気塞栓防止回路。超音波気泡検出器Aは気泡混入検知（True）、血液回路内圧センサBは陽圧過剰検知（False）。",
            "論理規程：『気泡検出Aまたは過剰内圧Bのいずれも非検知（NOR）』のとき『血液送血ポンプ継続』、一方でも検知なら『即時クランプ弁遮断作動』。決定せよ。",
            "ecmo_clamp_valve_trip",
            "体外式膜型人工肺（ECMO）の空気塞栓防止回路。超音波気泡検出器Aは気泡未検知（False）、血液回路内圧センサBも正常域（False）。",
            "論理規程：『気泡検出Aまたは過剰内圧Bのいずれも非検知（NOR）』のとき『血液送血ポンプ継続』、一方でも検知なら『即時クランプ弁遮断作動』。決定せよ。",
            "ecmo_blood_pump_maintain",
            [
                ("ecmo_blood_pump_maintain", "血液送血ポンプ継続"),
                ("ecmo_clamp_valve_trip", "即時クランプ弁遮断作動"),
            ],
        ),
        (
            "06",
            "半導体プラズマCVD排気系安全論理。毒性シランガス検知Aは漏洩検知（False）、除害装置燃焼筒フレームアイBは失火検知（False）。",
            "論理規程：『シラン漏洩Aと除害失火Bの両方非発生（NANDの逆、NOR）』のとき『原料ガス供給弁開通』、いずれか一方でも発生なら『緊急窒素ガスパージ遮断』。指示せよ。",
            "cvd_precursor_valve_open",
            "半導体プラズマCVD排気系安全論理。毒性シランガス検知Aは漏洩検知（False）、除害装置燃焼筒フレームアイBは失火検知（True）。",
            "論理規程：『シラン漏洩Aと除害失火Bの両方非発生（NANDの逆、NOR）』のとき『原料ガス供給弁開通』、いずれか一方でも発生なら『緊急窒素ガスパージ遮断』。指示せよ。",
            "cvd_emergency_purge_trip",
            [
                ("cvd_precursor_valve_open", "原料ガス供給弁開通"),
                ("cvd_emergency_purge_trip", "緊急窒素ガスパージ遮断"),
            ],
        ),
        (
            "07",
            "鉄道電子踏切制御器の方向判別論理。第1接近検知リレーAは扛上励磁（True）、第2進出検知リレーBは落下無励磁（False）。",
            "論理規程：『A成立かつB不成立（A AND NOT B）』のとき『下り列車警報灯点滅開始』、それ以外なら『踏切遮断桿全開維持』。指示せよ。",
            "crossing_alarm_flashing_on",
            "鉄道電子踏切制御器の方向判別論理。第1接近検知リレーAは落下無励磁（False）、第2進出検知リレーBは落下無励磁（False）。",
            "論理規程：『A成立かつB不成立（A AND NOT B）』のとき『下り列車警報灯点滅開始』、それ以外なら『踏切遮断桿全開維持』。指示せよ。",
            "crossing_gate_open_maintain",
            [
                ("crossing_alarm_flashing_on", "下り列車警報灯点滅開始"),
                ("crossing_gate_open_maintain", "踏切遮断桿全開維持"),
            ],
        ),
        (
            "08",
            "大型プレス機械の安全ライトカーテン両手押しボタン論理。ライトカーテン受光ビーム遮断Aは非遮断（False）、両手押しボタン同期押下Bは非同期（False）。",
            "論理規程：『受光ビーム非遮断（NOT A）かつ両手同期押下B（AND）』のとき『スライド下降プレス実行』、不成立なら『下降油圧クラッチ解放阻止』。決定せよ。",
            "press_clutch_release_hold",
            "大型プレス機械の安全ライトカーテン両手押しボタン論理。ライトカーテン受光ビーム遮断Aは非遮断（False）、両手押しボタン同期押下Bは完全同期押下（True）。",
            "論理規程：『受光ビーム非遮断（NOT A）かつ両手同期押下B（AND）』のとき『スライド下降プレス実行』、不成立なら『下降油圧クラッチ解放阻止』。決定せよ。",
            "press_slide_down_exec",
            [
                ("press_slide_down_exec", "スライド下降プレス実行"),
                ("press_clutch_release_hold", "下降油圧クラッチ解放阻止"),
            ],
        ),
        (
            "09",
            "LNG運搬船のタンク内圧パージ燃焼論理。ボイルオフガス（BOG）圧縮機運転Aは停止中（False）、再液化装置冷熱源Bは停止中（False）。",
            "論理規程：『BOG圧縮機Aまたは再液化装置Bのどちらか一方が稼働（OR）』のとき『タンク内ガス回収維持』、両方停止なら『ガス燃焼ユニット（GCU）逃がし点火』。指示せよ。",
            "lng_gcu_flare_vent_light",
            "LNG運搬船のタンク内圧パージ燃焼論理。ボイルオフガス（BOG）圧縮機運転Aは定常運転（True）、再液化装置冷熱源Bは停止中（False）。",
            "論理規程：『BOG圧縮機Aまたは再液化装置Bのどちらか一方が稼働（OR）』のとき『タンク内ガス回収維持』、両方停止なら『ガス燃焼ユニット（GCU）逃がし点火』。指示せよ。",
            "lng_tank_recovery_maintain",
            [
                ("lng_tank_recovery_maintain", "タンク内ガス回収維持"),
                ("lng_gcu_flare_vent_light", "ガス燃焼ユニット逃がし点火"),
            ],
        ),
        (
            "10",
            "極超音速風洞の主吸気急速弁開放論理。高温高圧空気蓄圧タンク圧力Aは規定圧到達（True）、下流真空球室真空度Bは高真空到達（True）。",
            "論理規程：『高圧タンクAと真空球室Bの双方が目標到達（同値・AND）』のとき『主急速弁トリガー点火』、一方でも未達なら『真空加圧プリチャージ継続』。指示せよ。",
            "hypersonic_main_valve_fire",
            "極超音速風洞の主吸気急速弁開放論理。高温高圧空気蓄圧タンク圧力Aは規定圧到達（True）、下流真空球室真空度Bは真空未達漏れ（False）。",
            "論理規程：『高圧タンクAと真空球室Bの双方が目標到達（同値・AND）』のとき『主急速弁トリガー点火』、一方でも未達なら『真空加圧プリチャージ継続』。指示せよ。",
            "hypersonic_precharge_continue",
            [
                ("hypersonic_main_valve_fire", "主急速弁トリガー点火"),
                ("hypersonic_precharge_continue", "真空加圧プリチャージ継続"),
            ],
        ),
    ]

    for pid, ctx1, q1, t1, ctx2, q2, t2, chs in k2_defs:
        choices = [{"id": cid, "text": ctxt} for cid, ctxt in chs]
        pairs.append({
            "pair_id": f"rc3_blind5_op_{pid}",
            "family": "logical_operators",
            "k": 2,
            "case_1": {
                "id": f"rc3_blind5_op_{pid}_s1",
                "group_id": f"rc3_blind5_op_{pid}",
                "family": "logical_operators",
                "context": ctx1,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1},
            },
            "case_2": {
                "id": f"rc3_blind5_op_{pid}_s2",
                "group_id": f"rc3_blind5_op_{pid}",
                "family": "logical_operators",
                "context": ctx2,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2},
            },
        })

    # K=3: 10 pairs (11..20)
    k3_defs = [
        (
            "11",
            "高炉ガス乾式除塵系統の切替論理。バグフィルター差圧高Aは正常（False）、集塵灰ホッパー満杯Bは満杯検知（True）。",
            "論理規程：『差圧高Aかつホッパー満杯B（AND）』なら『即時逆洗・排灰サイクル同時作動』、『いずれか一方のみ成立（XOR）』なら『単独機器重点対応』、『双方正常（NOR）』なら『定常集塵通気維持』。指令せよ。",
            "bfg_single_equip_handle",
            "高炉ガス乾式除塵系統の切替論理。バグフィルター差圧高Aは正常（False）、集塵灰ホッパー満杯Bも正常（False）。",
            "論理規程：『差圧高Aかつホッパー満杯B（AND）』なら『即時逆洗・排灰サイクル同時作動』、『いずれか一方のみ成立（XOR）』なら『単独機器重点対応』、『双方正常（NOR）』なら『定常集塵通気維持』。指令せよ。",
            "bfg_steady_dust_collect",
            [
                ("bfg_dual_cycle_exec", "即時逆洗排灰同時作動"),
                ("bfg_single_equip_handle", "単独機器重点対応"),
                ("bfg_steady_dust_collect", "定常集塵通気維持"),
            ],
        ),
        (
            "12",
            "原子力研究炉の一次冷却材漏洩早期警戒論理。格納容器ダスト放射能Aは基準超過（True）、サンプ水位上昇率Bは基準内（False）。",
            "論理規程：『放射能Aと水位上昇Bの双方成立（AND）』なら『即時原子炉スクラム隔離』、『いずれか一方のみ超過（XOR）』なら『漏洩箇所特定調査モード』、『双方基準内（NOR）』なら『定常運転監視』。指示せよ。",
            "leak_locate_survey_mode",
            "原子力研究炉の一次冷却材漏洩早期警戒論理。格納容器ダスト放射能Aは基準超過（True）、サンプ水位上昇率Bも基準超過（True）。",
            "論理規程：『放射能Aと水位上昇Bの双方成立（AND）』なら『即時原子炉スクラム隔離』、『いずれか一方のみ超過（XOR）』なら『漏洩箇所特定調査モード』、『双方基準内（NOR）』なら『定常運転監視』。指示せよ。",
            "reactor_scram_isolate",
            [
                ("reactor_scram_isolate", "即時原子炉スクラム隔離"),
                ("leak_locate_survey_mode", "漏洩箇所特定調査モード"),
                ("reactor_steady_watch", "定常運転監視"),
            ],
        ),
        (
            "13",
            "医薬品注射用水（WFI）ループのオゾン殺菌完了判定。溶存オゾン濃度Aは要求値維持（True）、循環温度Bは常温範囲内（False）。",
            "論理規程：『オゾンAかつ常温B（AND）』なら『オゾン分解紫外線ランプ点灯』、『オゾンAかつ高温（A AND NOT B）』なら『熱水併用滅菌移行』、『オゾン未達（NOT A）』なら『オゾン発生器出力増強』。指示せよ。",
            "wfi_thermal_sterilize_shift",
            "医薬品注射用水（WFI）ループのオゾン殺菌完了判定。溶存オゾン濃度Aは目標未達（False）、循環温度Bは常温範囲内（True）。",
            "論理規程：『オゾンAかつ常温B（AND）』なら『オゾン分解紫外線ランプ点灯』、『オゾンAかつ高温（A AND NOT B）』なら『熱水併用滅菌移行』、『オゾン未達（NOT A）』なら『オゾン発生器出力増強』。指示せよ。",
            "wfi_ozone_generator_boost",
            [
                ("wfi_uv_destruct_lamp_on", "オゾン分解UVランプ点灯"),
                ("wfi_thermal_sterilize_shift", "熱水併用滅菌移行"),
                ("wfi_ozone_generator_boost", "オゾン発生器出力増強"),
            ],
        ),
        (
            "14",
            "航空自律着陸進入システムの風向風速判定。横風成分Aは制限超過（True）、滑走路視程Bは制限良好（False）。",
            "論理規程：『横風A超過かつ視程B不良（AND）』なら『代替着陸空港へダイバート』、『横風Aまたは視程Bのどちらか一方のみ超過（XOR）』なら『進入復行（ゴーアラウンド）』、『双方良好（NOR）』なら『自動着陸進入を継続』。指示せよ。",
            "autoland_go_around_exec",
            "航空自律着陸進入システムの風向風速判定。横風成分Aは制限良好（False）、滑走路視程Bも制限良好（False）。",
            "論理規程：『横風A超過かつ視程B不良（AND）』なら『代替着陸空港へダイバート』、『横風Aまたは視程Bのどちらか一方のみ超過（XOR）』なら『進入復行（ゴーアラウンド）』、『双方良好（NOR）』なら『自動着陸進入を継続』。指示せよ。",
            "autoland_continue_approach",
            [
                ("autoland_divert_alternate", "代替空港へダイバート"),
                ("autoland_go_around_exec", "進入復行ゴーアラウンド"),
                ("autoland_continue_approach", "自動着陸進入を継続"),
            ],
        ),
        (
            "15",
            "水素ステーション充填ノズルの赤外線通信・気密論理。赤外線通信リンクAは正常確立（True）、パージ気密テストBは漏洩検出（True）。",
            "論理規程：『通信A正常かつ漏洩Bなし（A AND NOT B）』なら『70MPa水素急速充填開始』、『漏洩B検知（B成立）』なら『ノズル脱圧緊急パージ』、『通信A不成立かつ漏洩なし（NOT A AND NOT B）』なら『手動通信同期モード』。選択せよ。",
            "h2_nozzle_emergency_depressurize",
            "水素ステーション充填ノズルの赤外線通信・気密論理。赤外線通信リンクAは正常確立（True）、パージ気密テストBは漏洩なし（False）。",
            "論理規程：『通信A正常かつ漏洩Bなし（A AND NOT B）』なら『70MPa水素急速充填開始』、『漏洩B検知（B成立）』なら『ノズル脱圧緊急パージ』指示せよ。",
            "h2_rapid_charge_70mpa",
            [
                ("h2_rapid_charge_70mpa", "70MPa水素急速充填開始"),
                ("h2_nozzle_emergency_depressurize", "ノズル脱圧緊急パージ"),
                ("h2_manual_comm_sync_mode", "手動通信同期モード"),
            ],
        ),
        (
            "16",
            "変電所受電変圧器の過負荷自動制限論理。巻線油温高フラグAは発令（True）、系統潮流潮流量超過Bは未超過（False）。",
            "論理規程：『油温A高かつ潮流量B超過（AND）』なら『下位フィーダー緊急負荷遮断』、『油温Aのみ高（A AND NOT B）』なら『強制送風冷却ファン全機投入』、『潮流量Bのみ超過（B AND NOT A）』なら『他系統母線タイ連系切替』。指示せよ。",
            "transformer_forced_fan_all",
            "変電所受電変圧器の過負荷自動制限論理。巻線油温高フラグAは未発令（False）、系統潮流潮流量超過Bは超過検知（True）。",
            "論理規程：『油温A高かつ潮流量B超過（AND）』なら『下位フィーダー緊急負荷遮断』、『油温Aのみ高（A AND NOT B）』なら『強制送風冷却ファン全機投入』、『潮流量Bのみ超過（B AND NOT A）』なら『他系統母線タイ連系切替』。指示せよ。",
            "transformer_bus_tie_transfer",
            [
                ("transformer_feeder_shed_load", "下位フィーダー負荷遮断"),
                ("transformer_forced_fan_all", "強制送風ファン全機投入"),
                ("transformer_bus_tie_transfer", "他系統母線タイ連系切替"),
            ],
        ),
        (
            "17",
            "自律採掘重機の前方障害物検知とスリップ制御。LiDAR障害物検知Aは検知（False）、履帯回転トルク不一致Bは不一致検知（True）。",
            "論理規程：『障害物Aかつトルク不一致B（AND）』なら『全停止非常電磁ロック』、『障害物Aのみ（A AND NOT B）』なら『その場緩旋回ピボット』、『トルク不一致Bのみ（B AND NOT A）』なら『履帯左右差動トルク補正』。決定せよ。",
            "mining_crawler_differential_trim",
            "自律採掘重機の前方障害物検知とスリップ制御。LiDAR障害物検知Aは検知（True）、履帯回転トルク不一致Bは正常一致（False）。",
            "論理規程：『障害物Aかつトルク不一致B（AND）』なら『全停止非常電磁ロック』、『障害物Aのみ（A AND NOT B）』なら『その場緩旋回ピボット』、『トルク不一致Bのみ（B AND NOT A）』なら『履帯左右差動トルク補正』。決定せよ。",
            "mining_pivot_turn_avoid",
            [
                ("mining_full_stop_electromag", "全停止非常電磁ロック"),
                ("mining_pivot_turn_avoid", "その場緩旋回ピボット"),
                ("mining_crawler_differential_trim", "左右差動トルク補正"),
            ],
        ),
        (
            "18",
            "半導体超純水循環配管の溶存酸素と全有機炭素（TOC）警報。DO限界超過Aは正常範囲内（False）、TOC限界超過Bは超過検知（True）。",
            "論理規程：『DO超過AかつTOC超過B（AND）』なら『ユースポイント全弁遮断』、『いずれか一方のみ超過（XOR）』なら『再循環精製カートリッジ切替』、『双方正常（NOR）』なら『定常採水供給維持』。指示せよ。",
            "upw_purify_cartridge_switch",
            "半導体超純水循環配管の溶存酸素と全有機炭素（TOC）警報。DO限界超過Aは正常範囲内（False）、TOC限界超過Bも正常範囲内（False）。",
            "論理規程：『DO超過AかつTOC超過B（AND）』なら『ユースポイント全弁遮断』、『いずれか一方のみ超過（XOR）』なら『再循環精製カートリッジ切替』、『双方正常（NOR）』なら『定常採水供給維持』。指示せよ。",
            "upw_steady_sample_supply",
            [
                ("upw_isolate_use_points", "ユースポイント全弁遮断"),
                ("upw_purify_cartridge_switch", "精製カートリッジ切替"),
                ("upw_steady_sample_supply", "定常採水供給維持"),
            ],
        ),
        (
            "19",
            "浮体式天然ガス液化設備（FLNG）の洋上荷役安全回路。係留索過張力Aは正常内（False）、移送アーム変位過大Bは過大検出（True）。",
            "論理規程：『過張力Aかつアーム変位B（AND）』なら『緊急離脱カプラー（ERC）瞬時切断』、『変位Bのみ過大（B AND NOT A）』なら『移送ポンプ緊急停止』、『過張力Aのみ（A AND NOT B）』なら『係留ウインチテンション開放』。指示せよ。",
            "flng_transfer_pump_stop",
            "浮体式天然ガス液化設備（FLNG）の洋上荷役安全回路。係留索過張力Aは過張力検出（True）、移送アーム変位過大Bは正常内（False）。",
            "論理規程：『過張力Aかつアーム変位B（AND）』なら『緊急離脱カプラー（ERC）瞬時切断』、『変位Bのみ過大（B AND NOT A）』なら『移送ポンプ緊急停止』、『過張力Aのみ（A AND NOT B）』なら『係留ウインチテンション開放』。指示せよ。",
            "flng_mooring_winch_release",
            [
                ("flng_erc_instant_disconnect", "緊急離脱カプラー瞬時切断"),
                ("flng_transfer_pump_stop", "移送ポンプ緊急停止"),
                ("flng_mooring_winch_release", "係留ウインチテンション開放"),
            ],
        ),
        (
            "20",
            "化学品バッチ合成反応炉の撹拌モータートルク・内圧保護。撹拌トルク高Aは高負荷検知（True）、反応炉内圧急上昇Bは急上昇検知（True）。",
            "論理規程：『トルク高Aかつ内圧上昇B（AND）』なら『重合停止キラー剤緊急注入』、『トルク高Aのみ（A AND NOT B）』なら『モノマー滴下速度半減』、『内圧上昇Bのみ（B AND NOT A）』なら『凝縮器還流冷却弁全開』。指令せよ。",
            "reactor_shortstop_killer_feed",
            "化学品バッチ合成反応炉の撹拌モータートルク・内圧保護。撹拌トルク高Aは正常（False）、反応炉内圧急上昇Bは急上昇検知（True）。",
            "論理規程：『トルク高Aかつ内圧上昇B（AND）』なら『重合停止キラー剤緊急注入』、『トルク高Aのみ（A AND NOT B）』なら『モノマー滴下速度半減』、『内圧上昇Bのみ（B AND NOT A）』なら『凝縮器還流冷却弁全開』。指令せよ。",
            "condenser_reflux_valve_full",
            [
                ("reactor_shortstop_killer_feed", "重合停止剤緊急注入"),
                ("monomer_feed_rate_half", "モノマー滴下速度半減"),
                ("condenser_reflux_valve_full", "還流冷却弁全開"),
            ],
        ),
    ]

    for pid, ctx1, q1, t1, ctx2, q2, t2, chs in k3_defs:
        choices = [{"id": cid, "text": ctxt} for cid, ctxt in chs]
        pairs.append({
            "pair_id": f"rc3_blind5_op_{pid}",
            "family": "logical_operators",
            "k": 3,
            "case_1": {
                "id": f"rc3_blind5_op_{pid}_s1",
                "group_id": f"rc3_blind5_op_{pid}",
                "family": "logical_operators",
                "context": ctx1,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1},
            },
            "case_2": {
                "id": f"rc3_blind5_op_{pid}_s2",
                "group_id": f"rc3_blind5_op_{pid}",
                "family": "logical_operators",
                "context": ctx2,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2},
            },
        })

    # K=4: 10 pairs (21..30)
    k4_defs = [
        (
            "21",
            "水素燃料電池バスの高圧水素タンク電磁弁シーケンス。衝突加速度G超過Aは非検知（False）、水素濃度リークBは漏洩検知（True）。",
            "論理規程：『衝突G超過AかつリークB（A AND B）』なら『元バルブ瞬時火薬遮断』、『衝突G超過Aのみ（A AND NOT B）』なら『衝突遮断弁閉止』、『リークBのみ（B AND NOT A）』なら『換気ファン急速排気および通常弁遮断』、『双方不成立（NOT A AND NOT B）』なら『燃料供給ライン開通維持』。指示せよ。",
            "fcv_vent_fan_and_normal_close",
            "水素燃料電池バスの高圧水素タンク電磁弁シーケンス。衝突加速度G超過Aは検知（True）、水素濃度リークBは漏洩検知（True）。",
            "論理規程：『衝突G超過AかつリークB（A AND B）』なら『元バルブ瞬時火薬遮断』、『衝突G超過Aのみ（A AND NOT B）』なら『衝突遮断弁閉止』、『リークBのみ（B AND NOT A）』なら『換気ファン急速排気および通常弁遮断』、『双方不成立（NOT A AND NOT B）』なら『燃料供給ライン開通維持』。指示せよ。",
            "fcv_pyro_valve_instant_cutoff",
            [
                ("fcv_pyro_valve_instant_cutoff", "元バルブ瞬時火薬遮断"),
                ("fcv_crash_valve_shut", "衝突遮断弁閉止"),
                ("fcv_vent_fan_and_normal_close", "換気排気及び通常弁遮断"),
                ("fcv_fuel_line_supply_keep", "燃料供給ライン開通維持"),
            ],
        ),
        (
            "22",
            "データセンター免震ビルの免震オイルダンパー減衰力切替。地動加速度Aは中地震規模（True）、建物層間変形角Bは許容限界内（False）。",
            "論理規程：『大加速度Aかつ大層間変形B（AND）』なら『セミアクティブダンパー最大減衰硬化』、『大加速度Aのみ（A AND NOT B）』なら『中減衰モード追従』、『大変形Bのみ（B AND NOT A）』なら『長周期共振抑制ソフト減衰』、『双方非超過（NOR）』なら『非減衰ベース待機』。判定せよ。",
            "damper_medium_damping_track",
            "データセンター免震ビルの免震オイルダンパー減衰力切替。地動加速度Aは未検知微小（False）、建物層間変形角Bは風揺れによる大層間変形（True）。",
            "論理規程：『大加速度Aかつ大層間変形B（AND）』なら『セミアクティブダンパー最大減衰硬化』、『大加速度Aのみ（A AND NOT B）』なら『中減衰モード追従』、『大変形Bのみ（B AND NOT A）』なら『長周期共振抑制ソフト減衰』、『双方非超過（NOR）』なら『非減衰ベース待機』。判定せよ。",
            "damper_long_period_soft_damp",
            [
                ("damper_max_stiff_lock", "ダンパー最大減衰硬化"),
                ("damper_medium_damping_track", "中減衰モード追従"),
                ("damper_long_period_soft_damp", "長周期共振抑制減衰"),
                ("damper_base_idle_wait", "非減衰ベース待機"),
            ],
        ),
        (
            "23",
            "衛星間光通信追尾鏡の粗動・精動協調制御。広角CCDスポット偏差Aは画角内（False）、ファインポインティングPSD偏差Bは中心ずれ（True）。",
            "論理規程：『粗追尾Aずれかつ精追尾Bずれ（AND）』なら『ジンバル粗動とピエゾ精動の同期駆動』、『粗追尾Aのみずれ（A AND NOT B）』なら『ジンバル粗動再センタリング』、『精追尾Bのみずれ（B AND NOT A）』なら『ピエゾアクチュエータ閉ループ補正』、『双方一致中心（NOR）』なら『光リンク捕捉固定ロック』。指示せよ。",
            "piezo_fine_closed_loop_steer",
            "衛星間光通信追尾鏡の粗動・精動協調制御。広角CCDスポット偏差Aは画角外外れ（True）、ファインポインティングPSD偏差Bは完全ロスト（True）。",
            "論理規程：『粗追尾Aずれかつ精追尾Bずれ（AND）』なら『ジンバル粗動とピエゾ精動の同期駆動』、『粗追尾Aのみずれ（A AND NOT B）』なら『ジンバル粗動再センタリング』、『精追尾Bのみずれ（B AND NOT A）』なら『ピエゾアクチュエータ閉ループ補正』、『双方一致中心（NOR）』なら『光リンク捕捉固定ロック』。指示せよ。",
            "gimbal_and_piezo_sync_drive",
            [
                ("gimbal_and_piezo_sync_drive", "粗動精動同期駆動"),
                ("gimbal_coarse_recenter", "ジンバル粗動再センタリング"),
                ("piezo_fine_closed_loop_steer", "ピエゾ閉ループ補正"),
                ("opt_link_acquire_lock", "光リンク捕捉固定ロック"),
            ],
        ),
        (
            "24",
            "原子力乾式キャスク貯蔵施設の熱対流監視。キャスク吸気ダスト閉塞Aは正常開口（False）、排気口表面放射線率Bは基準値内（False）。",
            "論理規程：『吸気閉塞Aかつ放射線B上昇（AND）』なら『緊急キャスク格納容器移送再装填』、『吸気閉塞Aのみ（A AND NOT B）』なら『吸気グリル高圧エア除塵ブロワー作動』、『放射線B上昇のみ（B AND NOT A）』なら『遮蔽シールド追加設置』、『双方健全（NOR）』なら『定常自然対流除熱確認』。決定せよ。",
            "cask_natural_convection_ok",
            "原子力乾式キャスク貯蔵施設の熱対流監視。キャスク吸気ダスト閉塞Aは閉塞検知（True）、排気口表面放射線率Bは基準値内（False）。",
            "論理規程：『吸気閉塞Aかつ放射線B上昇（AND）』なら『緊急キャスク格納容器移送再装填』、『吸気閉塞Aのみ（A AND NOT B）』なら『吸気グリル高圧エア除塵ブロワー作動』、『放射線B上昇のみ（B AND NOT A）』なら『遮蔽シールド追加設置』、『双方健全（NOR）』なら『定常自然対流除熱確認』。決定せよ。",
            "cask_air_blower_purge",
            [
                ("cask_emergency_reload_transfer", "キャスク移送再装填"),
                ("cask_air_blower_purge", "吸気グリルエア除塵作動"),
                ("cask_shield_add_place", "遮蔽シールド追加設置"),
                ("cask_natural_convection_ok", "定常自然対流除熱確認"),
            ],
        ),
        (
            "25",
            "バイオセイフティレベル4（BSL-4）実験室の負圧排気HEPAフィルタ制御。前段排気HEPA差圧過大Aは過大（True）、後段安全HEPA差圧過大Bは正常（False）。",
            "論理規程：『前段A過大かつ後段B過大（AND）』なら『実験室排気ファン即時停止ダンパー気密ロック』、『前段Aのみ過大（A AND NOT B）』なら『後段HEPA単独通過バイパス切替』、『後段Bのみ過大（B AND NOT A）』なら『後段HEPAユニット予備機自動並入』、『双方正常（NOR）』なら『二重HEPA定常全量排気』。指示せよ。",
            "hepa_bypass_to_second_stage",
            "バイオセイフティレベル4（BSL-4）実験室の負圧排気HEPAフィルタ制御。前段排気HEPA差圧過大Aは過大（True）、後段安全HEPA差圧過大Bも過大（True）。",
            "論理規程：『前段A過大かつ後段B過大（AND）』なら『実験室排気ファン即時停止ダンパー気密ロック』、『前段Aのみ過大（A AND NOT B）』なら『後段HEPA単独通過バイパス切替』、『後段Bのみ過大（B AND NOT A）』なら『後段HEPAユニット予備機自動並入』、『双方正常（NOR）』なら『二重HEPA定常全量排気』。指示せよ。",
            "bsl4_exhaust_fan_scram_lock",
            [
                ("bsl4_exhaust_fan_scram_lock", "排気ファン停止ダンパー気密ロック"),
                ("hepa_bypass_to_second_stage", "後段HEPA単独通過切替"),
                ("hepa_standby_unit_auto_align", "後段予備機自動並入"),
                ("hepa_dual_normal_exhaust", "二重HEPA定常全量排気"),
            ],
        ),
        (
            "26",
            "海洋掘削船のダイナミックポジショニング（DP）スラスタ電源脱落保護。第1高圧バスバー停電Aは通電正常（False）、スラスタ可変周波数ドライブ（VFD）地絡Bは地絡検出（True）。",
            "論理規程：『母線停電Aかつドライブ地絡B（AND）』なら『船位保持断念エマージェンシードロップ』、『母線停電Aのみ（A AND NOT B）』なら『母線連系タイ遮断器投入バックアップ』、『ドライブ地絡Bのみ（B AND NOT A）』なら『該当スラスタ単基電気的切離し』、『双方正常（NOR）』なら『全8基同期推力分配』。決定せよ。",
            "thruster_isolate_single_unit",
            "海洋掘削船のダイナミックポジショニング（DP）スラスタ電源脱落保護。第1高圧バスバー停電Aは母線停電トリップ（True）、スラスタ可変周波数ドライブ（VFD）地絡Bは正常（False）。",
            "論理規程：『母線停電Aかつドライブ地絡B（AND）』なら『船位保持断念エマージェンシードロップ』、『母線停電Aのみ（A AND NOT B）』なら『母線連系タイ遮断器投入バックアップ』、『ドライブ地絡Bのみ（B AND NOT A）』なら『該当スラスタ単基電気的切離し』、『双方正常（NOR）』なら『全8基同期推力分配』。決定せよ。",
            "bus_tie_breaker_close_backup",
            [
                ("emergency_riser_disconnect", "エマージェンシードロップ"),
                ("bus_tie_breaker_close_backup", "母線タイ遮断器投入"),
                ("thruster_isolate_single_unit", "該当スラスタ単基切離し"),
                ("thruster_full_sync_thrust", "全基同期推力分配"),
            ],
        ),
        (
            "27",
            "大規模太陽光・蓄電池ハイブリッド発電所の出力平滑化論理。PV急激出力低下フラグAは急低下検知（True）、蓄電池残量SoC下限フラグBは下限到達（True）。",
            "論理規程：『PV低下Aかつ蓄電池枯渇B（AND）』なら『電力会社給電指令所へ即時出力抑制通報』、『PV低下Aのみ（A AND NOT B）』なら『蓄電池急速放電サポート』、『蓄電池枯渇Bのみ（B AND NOT A）』なら『PV余剰電力による蓄電池低レート充電』、『双方健全（NOR）』なら『目標出力定数自動追従』。指示せよ。",
            "grid_notify_curtailment_alert",
            "大規模太陽光・蓄電池ハイブリッド発電所の出力平滑化論理。PV急激出力低下フラグAは急低下検知（True）、蓄電池残量SoC下限フラグBは残量余裕あり（False）。",
            "論理規程：『PV低下Aかつ蓄電池枯渇B（AND）』なら『電力会社給電指令所へ即時出力抑制通報』、『PV低下Aのみ（A AND NOT B）』なら『蓄電池急速放電サポート』、『蓄電池枯渇Bのみ（B AND NOT A）』なら『PV余剰電力による蓄電池低レート充電』、『双方健全（NOR）』なら『目標出力定数自動追従』。指示せよ。",
            "bess_rapid_discharge_support",
            [
                ("grid_notify_curtailment_alert", "給電所即時出力抑制通報"),
                ("bess_rapid_discharge_support", "蓄電池急速放電サポート"),
                ("bess_pv_trickle_charge", "余剰電力低レート充電"),
                ("hybrid_target_auto_track", "目標出力定数自動追従"),
            ],
        ),
        (
            "28",
            "半導体ウェハー研磨CMP装置のスラリー供給流路切替。研磨パッド摩耗厚み限界Aは限界到達（False）、スラリーライン圧力低下Bは低下検出（True）。",
            "論理規程：『パッド限界Aかつ圧力低下B（AND）』なら『ウェハーリフト即時退避及びシーケンス非常停止』、『パッド限界Aのみ（A AND NOT B）』なら『自動パッドコンディショニングダイヤモンド研削』、『圧力低下Bのみ（B AND NOT A）』なら『予備スラリーダイヤフラムポンプ自動起動』、『双方正常（NOR）』なら『鏡面研磨レシピ実行継続』。決定せよ。",
            "cmp_standby_slurry_pump_start",
            "半導体ウェハー研磨CMP装置のスラリー供給流路切替。研磨パッド摩耗厚み限界Aは限界到達（True）、スラリーライン圧力低下Bは低下検出（True）。",
            "論理規程：『パッド限界Aかつ圧力低下B（AND）』なら『ウェハーリフト即時退避及びシーケンス非常停止』、『パッド限界Aのみ（A AND NOT B）』なら『自動パッドコンディショニングダイヤモンド研削』、『圧力低下Bのみ（B AND NOT A）』なら『予備スラリーダイヤフラムポンプ自動起動』、『双方正常（NOR）』なら『鏡面研磨レシピ実行継続』。決定せよ。",
            "cmp_wafer_lift_emergency_abort",
            [
                ("cmp_wafer_lift_emergency_abort", "ウェハー退避シーケンス停止"),
                ("cmp_pad_conditioning_grind", "パッド研削コンディショニング"),
                ("cmp_standby_slurry_pump_start", "予備スラリーポンプ起動"),
                ("cmp_mirror_polish_continue", "鏡面研磨レシピ継続"),
            ],
        ),
        (
            "29",
            "LNG受入基地の冷熱利用発電膨張タービン制御。LNG流量過少フラグAは未達（False）、タービン振動振幅過大Bは過大検出（True）。",
            "論理規程：『流量過少Aかつ振動過大B（AND）』なら『主遮断弁急速閉止およびタービントリップ』、『流量過少Aのみ（A AND NOT B）』なら『LNG循環バイパス弁開度増加』、『振動過大Bのみ（B AND NOT A）』なら『可変ノズルベーン開度絞り込み減速』、『双方健全（NOR）』なら『定格冷熱発電継続』。指示せよ。",
            "expander_vane_choke_decel",
            "LNG受入基地の冷熱利用発電膨張タービン制御。LNG流量過少フラグAは流量低下（True）、タービン振動振幅過大Bは振動正常（False）。",
            "論理規程：『流量過少Aかつ振動過大B（AND）』なら『主遮断弁急速閉止およびタービントリップ』、『流量過少Aのみ（A AND NOT B）』なら『LNG循環バイパス弁開度増加』、『振動過大Bのみ（B AND NOT A）』なら『可変ノズルベーン開度絞り込み減速』、『双方健全（NOR）』なら『定格冷熱発電継続』。指示せよ。",
            "lng_bypass_valve_open_increase",
            [
                ("expander_turbine_trip_shut", "主弁急速閉止タービントリップ"),
                ("lng_bypass_valve_open_increase", "LNG循環バイパス弁開度増加"),
                ("expander_vane_choke_decel", "可変ノズル開度絞り込み"),
                ("expander_rated_power_gen", "定格冷熱発電継続"),
            ],
        ),
        (
            "30",
            "自動運転トラックの隊列走行車車間通信と車間レーダー論理。V2V無線通信タイムアウトAはタイムアウト（True）、ミリ波レーダー捕捉ロストBは正常捕捉（False）。",
            "論理規程：『通信断AかつレーダーロストB（AND）』なら『隊列離脱非常自動減速停止』、『通信断Aのみ（A AND NOT B）』なら『レーダー追尾単独自律車間拡大走行』、『レーダーロストBのみ（B AND NOT A）』なら『通信協調加速度連動走行』、『双方正常（NOR）』なら『最短距離緊密隊列走行維持』。判定せよ。",
            "platoon_radar_autonomous_expand",
            "自動運転トラックの隊列走行車車間通信と車間レーダー論理。V2V無線通信タイムアウトAは通信正常（False）、ミリ波レーダー捕捉ロストBは捕捉ロスト（True）。",
            "論理規程：『通信断AかつレーダーロストB（AND）』なら『隊列離脱非常自動減速停止』、『通信断Aのみ（A AND NOT B）』なら『レーダー追尾単独自律車間拡大走行』、『レーダーロストBのみ（B AND NOT A）』なら『通信協調加速度連動走行』、『双方正常（NOR）』なら『最短距離緊密隊列走行維持』。判定せよ。",
            "platoon_v2v_coop_accel_track",
            [
                ("platoon_emergency_abort_stop", "隊列離脱非常減速停止"),
                ("platoon_radar_autonomous_expand", "レーダー単独車間拡大走行"),
                ("platoon_v2v_coop_accel_track", "通信協調加速度連動走行"),
                ("platoon_close_spacing_keep", "緊密隊列走行維持"),
            ],
        ),
    ]

    for pid, ctx1, q1, t1, ctx2, q2, t2, chs in k4_defs:
        choices = [{"id": cid, "text": ctxt} for cid, ctxt in chs]
        pairs.append({
            "pair_id": f"rc3_blind5_op_{pid}",
            "family": "logical_operators",
            "k": 4,
            "case_1": {
                "id": f"rc3_blind5_op_{pid}_s1",
                "group_id": f"rc3_blind5_op_{pid}",
                "family": "logical_operators",
                "context": ctx1,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1},
            },
            "case_2": {
                "id": f"rc3_blind5_op_{pid}_s2",
                "group_id": f"rc3_blind5_op_{pid}",
                "family": "logical_operators",
                "context": ctx2,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2},
            },
        })

    return pairs
