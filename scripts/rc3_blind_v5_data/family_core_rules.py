"""Blind v5 Family: Core Rules (30 pairs, 60 cases).

Choice count distribution:
- K=2: 5 pairs (core_01 to core_05)
- K=3: 10 pairs (core_06 to core_15)
- K=4: 10 pairs (core_16 to core_25)
- K=6: 5 pairs (core_26 to core_30)
"""

from __future__ import annotations
from typing import Any, Dict, List


def get_core_rules_pairs() -> List[Dict[str, Any]]:
    pairs = []

    # K=2: 5 pairs (01..05)
    k2_defs = [
        (
            "01",
            "軌道投入衛星のリアクションホイール脱飽和規程。規程：『ホイール積算回転数が4,800rpm以上のときは磁気トルカによる連続脱飽和シーケンスを開始し、4,800rpm未満の場合は定常姿勢フィードバック制御を継続する』。",
            "テレメトリ受信：現在第2リアクションホイールの積算回転数は5,120rpmを記録している。指示を選択せよ。",
            "desat_magnetic_exec",
            "テレメトリ受信：現在第2リアクションホイールの積算回転数は3,640rpmで安定している。指示を選択せよ。",
            "desat_feedback_keep",
            [
                ("desat_magnetic_exec", "磁気トルカ脱飽和開始"),
                ("desat_feedback_keep", "定常姿勢制御を継続"),
            ],
        ),
        (
            "02",
            "極低温液体水素リクィファクション圧縮機の吸入圧保護規程。規程：『吸入バッファ圧力が0.15MPa以下のときは低温パージバイパス弁を全開とし、0.15MPa超のときは主段圧縮運転を維持する』。",
            "計測データ：吸入バッファ圧力センサは0.11MPaを示している。適切な弁制御を選択せよ。",
            "purge_bypass_open",
            "計測データ：吸入バッファ圧力センサは0.28MPaを示している。適切な弁制御を選択せよ。",
            "main_compressor_keep",
            [
                ("purge_bypass_open", "低温バイパス弁を全開"),
                ("main_compressor_keep", "主段圧縮運転を維持"),
            ],
        ),
        (
            "03",
            "海底掘削防噴装置（BOP）の剪断ラム作動油圧基準。基準：『アキュムレータ残圧が21.0MPa以上のときは即時剪断コマンドを受理し、21.0MPa未満の場合は補助ブースターポンプ加圧を先行する』。",
            "圧力センサ測定：アキュムレータバンク実圧は24.2MPaである。剪断指令時の動作を選択せよ。",
            "bop_shear_execute",
            "圧力センサ測定：アキュムレータバンク実圧は18.6MPaである。剪断指令時の動作を選択せよ。",
            "bop_booster_pressurize",
            [
                ("bop_shear_execute", "即時剪断コマンド受理"),
                ("bop_booster_pressurize", "補助ブースター加圧先行"),
            ],
        ),
        (
            "04",
            "超伝導マグネットのクエンチ保護規程。規程：『コイル両端電圧差が500mV以上のときは速やかに保護放電抵抗へエネルギー転換し、500mV未満のときは励磁電源接続を維持する』。",
            "モニタリングログ：電圧差検出回路が780mVの不平衡電位差を検知した。指令を選択せよ。",
            "quench_dump_resistor",
            "モニタリングログ：電圧差検出回路の電位差は12mVで閾値以下である。指令を選択せよ。",
            "quench_power_maintain",
            [
                ("quench_dump_resistor", "保護放電抵抗へ転換"),
                ("quench_power_maintain", "励磁電源接続を維持"),
            ],
        ),
        (
            "05",
            "トンネル掘削シールド機の泥水圧管理規程。規程：『切羽チャンバー泥水圧力が地下水圧プラス0.05MPa以上のときは掘進ジャッキ推力を維持し、下回る場合は泥水圧加圧弁を作動させる』。",
            "測定報告：地下水圧0.30MPaに対しチャンバー実圧0.28MPa（差圧-0.02MPa）である。指令せよ。",
            "tbm_pressurize_valve",
            "測定報告：地下水圧0.30MPaに対しチャンバー実圧0.38MPa（差圧+0.08MPa）である。指令せよ。",
            "tbm_thrust_maintain",
            [
                ("tbm_pressurize_valve", "泥水圧加圧弁を作動"),
                ("tbm_thrust_maintain", "掘進ジャッキ推力維持"),
            ],
        ),
    ]

    for pid, ctx, q1, t1, q2, t2, chs in k2_defs:
        choices = [{"id": cid, "text": ctxt} for cid, ctxt in chs]
        pairs.append({
            "pair_id": f"rc3_blind5_core_{pid}",
            "family": "core_rules",
            "k": 2,
            "case_1": {
                "id": f"rc3_blind5_core_{pid}_s1",
                "group_id": f"rc3_blind5_core_{pid}",
                "family": "core_rules",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1},
            },
            "case_2": {
                "id": f"rc3_blind5_core_{pid}_s2",
                "group_id": f"rc3_blind5_core_{pid}",
                "family": "core_rules",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2},
            },
        })

    # K=3: 10 pairs (06..15)
    k3_defs = [
        (
            "06",
            "半導体液浸露光装置の温調純水供給規程。規程：『水温偏差が±0.002℃以内のときは露光照射を続行、+0.002℃超過のときはペルチェ冷却増速、-0.002℃未満のときは精密ヒーター昇温を実行する』。",
            "センサ報告：液浸純水温度偏差は+0.0045℃を記録した。制御操作を指示せよ。",
            "immersion_peltier_cool",
            "センサ報告：液浸純水温度偏差は-0.0038℃を記録した。制御操作を指示せよ。",
            "immersion_heater_warm",
            [
                ("immersion_exposure_go", "露光照射を続行"),
                ("immersion_peltier_cool", "ペルチェ冷却増速"),
                ("immersion_heater_warm", "精密ヒーター昇温"),
            ],
        ),
        (
            "07",
            "電気機関車の回生ブレーキ制御規程。規程：『架線電圧が1,650V以下のときは全回生制動、1,650V超1,750V以下のときは抑速抵抗併用、1,750V超のときは機械式空気制動へ完全切り替えとする』。",
            "運行データ：架線電圧モニタが1,710Vを示している。適切な制動モードを選択せよ。",
            "regen_resistor_blend",
            "運行データ：架線電圧モニタが1,580Vを示している。適切な制動モードを選択せよ。",
            "regen_full_electric",
            [
                ("regen_full_electric", "全回生制動を実行"),
                ("regen_resistor_blend", "抑速抵抗併用制動"),
                ("regen_air_mechanical", "機械式空気制動へ切替"),
            ],
        ),
        (
            "08",
            "クリーンルーム差圧ダンパー制御規程。規程：『隣接エリアとの差圧が+15Pa以上のときは給気排気バランス維持、+10Pa以上+15Pa未満のときは給気ダンパー微開、+10Pa未満のときは給気ファン緊急増速とする』。",
            "差圧計ログ：陽圧差圧が+7.5Paまで低下している。ダンパー・ファン制御を選択せよ。",
            "cr_fan_emergency_boost",
            "差圧計ログ：陽圧差圧が+18.2Paで基準内に保たれている。ダンパー・ファン制御を選択せよ。",
            "cr_balance_maintain",
            [
                ("cr_balance_maintain", "給排気バランス維持"),
                ("cr_damper_micro_open", "給気ダンパー微開"),
                ("cr_fan_emergency_boost", "給気ファン緊急増速"),
            ],
        ),
        (
            "09",
            "バイオ医薬品培養槽の溶存酸素（DO）制御規程。規程：『DOが40%以上のときは定常通気維持、25%以上40%未満のときは酸素富化スパージング開始、25%未満のときは撹拌翼回転数上限増速とする』。",
            "電極測定値：溶存酸素計が31.5%を示している。適切なリアクター制御を決定せよ。",
            "bio_o2_sparge_start",
            "電極測定値：溶存酸素計が18.0%まで急落した。適切なリアクター制御を決定せよ。",
            "bio_agitator_boost",
            [
                ("bio_steady_aeration", "定常通気維持"),
                ("bio_o2_sparge_start", "酸素富化通気開始"),
                ("bio_agitator_boost", "撹拌翼上限増速"),
            ],
        ),
        (
            "10",
            "風力発電機のヨー旋回方位制御規程。規程：『風向偏角が±10度以内のときはナセル保持、+10度超過のときは時計回りヨー駆動、-10度超過（左偏角）のときは反時計回りヨー駆動とする』。",
            "風向風速計：風向計とナセル方位の偏差が+16.5度（右偏角）を検出した。ナセル動作を指示せよ。",
            "yaw_drive_clockwise",
            "風向風速計：風向計とナセル方位の偏差が-14.2度（左偏角）を検出した。ナセル動作を指示せよ。",
            "yaw_drive_counterclockwise",
            [
                ("yaw_nacelle_hold", "ナセル方位保持"),
                ("yaw_drive_clockwise", "時計回りヨー旋回"),
                ("yaw_drive_counterclockwise", "反時計回りヨー旋回"),
            ],
        ),
        (
            "11",
            "排熱回収ボイラー蒸気ドラム水位保護規程。規程：『ドラム水位偏差が±25mm以内のときは給水三要素自動制御、+50mm以上のときは緊急ブロー弁開放、-50mm以下のときは非常用補助給水ポンプ即時投入とする』。",
            "監視盤測定：ドラム水位偏差が+68mmまで急上昇した。操作を選択せよ。",
            "drum_emergency_blowdown",
            "監視盤測定：ドラム水位偏差が-62mmまで急低下した。操作を選択せよ。",
            "drum_aux_feedwater_pump",
            [
                ("drum_auto_control_norm", "給水自動制御継続"),
                ("drum_emergency_blowdown", "緊急ブロー弁開放"),
                ("drum_aux_feedwater_pump", "非常用給水ポンプ投入"),
            ],
        ),
        (
            "12",
            "宇宙ステーション環境制御水再生触媒酸化炉規程。規程：『触媒床温度が125℃以上のときは有機物完全酸化モード、115℃以上125℃未満のときは予熱ヒーター通電、115℃未満のときは原水流入遮断弁閉鎖とする』。",
            "温度測定：触媒反応器入口温度計が108℃を示している。制御操作を指示せよ。",
            "water_inlet_valve_close",
            "温度測定：触媒反応器入口温度計が128℃で安定している。制御操作を指示せよ。",
            "water_catalytic_oxidize",
            [
                ("water_catalytic_oxidize", "触媒酸化モード実行"),
                ("water_preheat_heater_on", "予熱ヒーター通電"),
                ("water_inlet_valve_close", "原水流入遮断弁閉鎖"),
            ],
        ),
        (
            "13",
            "ファイバーレーザー切断ノズルのスタンドオフ距離制御規程。規程：『静電容量センサ距離が0.8mm〜1.2mmのときはレーザー照射継続、1.2mm超のときはZ軸下降補正、0.8mm未満のときは切断ヘッド即時上昇退避とする』。",
            "加工中ステータス：ノズル先端ギャップ測定値は1.55mmである。加工機動作を選択せよ。",
            "laser_z_down_adjust",
            "加工中ステータス：ノズル先端ギャップ測定値は0.42mmである。加工機動作を選択せよ。",
            "laser_head_retract_up",
            [
                ("laser_cutting_continue", "レーザー照射継続"),
                ("laser_z_down_adjust", "Z軸下降補正"),
                ("laser_head_retract_up", "切断ヘッド上昇退避"),
            ],
        ),
        (
            "14",
            "大型コンテナクレーンの振れ止め（アンチスウェイ）ケーブル張力規程。規程：『対向ワイヤ張力比が0.9〜1.1のときは主巻き上げ連動、1.3以上のときはスウェイトルク打ち消し補正、0.7以下のときはトロリ横行速度制限とする』。",
            "吊り荷監視：左右ワイヤ張力比が1.45を記録し荷揺れが発生している。制御指示を選択せよ。",
            "crane_antisway_counter",
            "吊り荷監視：左右ワイヤ張力比が0.98で荷振れは極めて小さい。制御指示を選択せよ。",
            "crane_hoist_interlock",
            [
                ("crane_hoist_interlock", "主巻き上げ連動継続"),
                ("crane_antisway_counter", "スウェイトルク補正"),
                ("crane_trolley_speed_limit", "トロリ横行速度制限"),
            ],
        ),
        (
            "15",
            "重粒子線がん治療装置のシンクロトロン出射ビーム電流管理規程。規程：『ビーム強度計が3.0nA〜5.0nAのときは患部照射シャッター開放、5.0nA超のときはデチューン偏向器作動、3.0nA未満のときは加速高周波再同期とする』。",
            "照射室ログ：出射ビーム測定値が5.8nAを検出した。インターロック動作を決定せよ。",
            "beam_detune_deflector",
            "照射室ログ：出射ビーム測定値が2.1nAで規定値を下回っている。インターロック動作を決定せよ。",
            "beam_rf_resynchronize",
            [
                ("beam_shutter_open_treat", "患部照射シャッター開放"),
                ("beam_detune_deflector", "デチューン偏向器作動"),
                ("beam_rf_resynchronize", "高周波再同期"),
            ],
        ),
    ]

    for pid, ctx, q1, t1, q2, t2, chs in k3_defs:
        choices = [{"id": cid, "text": ctxt} for cid, ctxt in chs]
        pairs.append({
            "pair_id": f"rc3_blind5_core_{pid}",
            "family": "core_rules",
            "k": 3,
            "case_1": {
                "id": f"rc3_blind5_core_{pid}_s1",
                "group_id": f"rc3_blind5_core_{pid}",
                "family": "core_rules",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1},
            },
            "case_2": {
                "id": f"rc3_blind5_core_{pid}_s2",
                "group_id": f"rc3_blind5_core_{pid}",
                "family": "core_rules",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2},
            },
        })

    # K=4: 10 pairs (16..25)
    k4_defs = [
        (
            "16",
            "高電圧直流送電（HVDC）サイリスタバルブホールの冷却水導電率規程。規程：『冷却水導電率が0.10μS/cm以下のときは全定格送電維持、0.10μS/cm超0.25μS/cm以下のときはイオン交換樹脂バイパス循環投入、0.25μS/cm超0.50μS/cm以下のときは送電容量50%制限、0.50μS/cm超のときはバルブ即時ゲートブロック緊急停止とする』。",
            "水質分析器：バルブ冷却水導電率は0.18μS/cmを示している。運転モードを決定せよ。",
            "hvdc_ion_exchange_run",
            "水質分析器：バルブ冷却水導電率は0.65μS/cmまで悪化している。運転モードを決定せよ。",
            "hvdc_gate_block_trip",
            [
                ("hvdc_full_rated_power", "全定格送電維持"),
                ("hvdc_ion_exchange_run", "イオン交換循環投入"),
                ("hvdc_curtail_power_50", "送電容量50%制限"),
                ("hvdc_gate_block_trip", "バルブ即時ゲートブロック"),
            ],
        ),
        (
            "17",
            "海洋石油生産プラットフォームのフレアガス回収コンプレッサー規程。規程：『ヘッダー圧力が0.08MPa以下のときはコンプレッサーアイドリング待機、0.08MPa超0.20MPa以下のときは単段回収運転、0.20MPa超0.35MPa以下のときは二段圧縮回収、0.35MPa超のときは高圧フレア点火弁開放とする』。",
            "計装記録：フレアヘッダー実圧は0.28MPaを検出した。コンプレッサー制御を決定せよ。",
            "flare_compressor_dual_stage",
            "計装記録：フレアヘッダー実圧は0.04MPaで低圧である。コンプレッサー制御を決定せよ。",
            "flare_compressor_idle_wait",
            [
                ("flare_compressor_idle_wait", "アイドリング待機"),
                ("flare_compressor_single_stage", "単段回収運転"),
                ("flare_compressor_dual_stage", "二段圧縮回収運転"),
                ("flare_ignite_relief_valve", "高圧フレア点火弁開放"),
            ],
        ),
        (
            "18",
            "自動倉庫の高速スタッカークレーン走行車輪スリップ監視規程。規程：『従動輪エンコーダと駆動輪速度偏差が2%以下のときは通常加減速走行、2%超5%以下のときはレール砂撒きトラクション補正、5%超10%以下のときは速度半減クリープ運転、10%超のときは非常電磁吸着ブレーキ作動とする』。",
            "台車テレメトリ：速度偏差率が13.5%の空転スリップを検出した。クレーン停止制御を選択せよ。",
            "crane_electromag_brake_trip",
            "台車テレメトリ：速度偏差率が3.8%で軽度の滑走傾向を示している。台車制御を選択せよ。",
            "crane_rail_sand_traction",
            [
                ("crane_normal_accel_travel", "通常加減速走行"),
                ("crane_rail_sand_traction", "レール砂撒き補正"),
                ("crane_creep_speed_half", "速度半減クリープ"),
                ("crane_electromag_brake_trip", "非常電磁吸着ブレーキ"),
            ],
        ),
        (
            "19",
            "石油精製水素化脱硫反応器の触媒層差圧管理規程。規程：『触媒床差圧が0.15MPa以下のときは通常通油維持、0.15MPa超0.30MPa以下のときはリサイクルガス流量増速、0.30MPa超0.45MPa以下のときは処理量20%減量、0.45MPa超のときは緊急減圧脱圧シーケンスとする』。",
            "運転日報：反応器床差圧が0.38MPaを指針している。精製プラント運転措置を選択せよ。",
            "hds_feed_curtail_20",
            "運転日報：反応器床差圧が0.52MPaに急達した。精製プラント運転措置を選択せよ。",
            "hds_emergency_depressurize",
            [
                ("hds_normal_oil_flow", "通常通油維持"),
                ("hds_recycle_gas_boost", "リサイクルガス増速"),
                ("hds_feed_curtail_20", "処理量20%減量"),
                ("hds_emergency_depressurize", "緊急減圧脱圧シーケンス"),
            ],
        ),
        (
            "20",
            "原子力発電所余熱除去系（RHR）熱交換器海水供給規程。規程：『冷却海水出口温度が32℃以下のときは定常流量循環、32℃超36℃以下のときは第2海水ポンプ並入、36℃超40℃以下のときはRHR系統流量絞り弁開度調整、40℃超のときは代替原子炉補機冷却系（RCW）への流路切替とする』。",
            "現場指示盤：熱交換器海水出口温度が42.5℃を記録した。冷却系流路制御を選択せよ。",
            "rhr_rcw_alternate_align",
            "現場指示盤：熱交換器海水出口温度が34.2℃を示している。海水ポンプ操作を選択せよ。",
            "rhr_seawater_pump2_start",
            [
                ("rhr_seawater_normal_flow", "定常流量循環維持"),
                ("rhr_seawater_pump2_start", "第2海水ポンプ並入"),
                ("rhr_throttle_valve_adjust", "RHR流量絞り弁調整"),
                ("rhr_rcw_alternate_align", "代替補機冷却系へ流路切替"),
            ],
        ),
        (
            "21",
            "データセンター蓄電池室の水冷インバーター液漏れ検知規程。規程：『液漏れセンサ抵抗が100kΩ以上のときは正常監視継続、50kΩ以上100kΩ未満のときは警報発信および巡回点検指示、10kΩ以上50kΩ未満のときは対象ラックインバーター出力停止、10kΩ未満のときは蓄電池直流遮断器トリップとする』。",
            "センサネットワーク：受電室センサ抵抗値が8.2kΩ（重度漏水短絡）を示した。遮断動作を選択せよ。",
            "dc_breaker_trip_scram",
            "センサネットワーク：受電室センサ抵抗値が68kΩ（軽微結露の疑い）を示した。対応を選択せよ。",
            "alarm_patrol_dispatch",
            [
                ("normal_monitor_continue", "正常監視継続"),
                ("alarm_patrol_dispatch", "警報発信と点検指示"),
                ("inverter_rack_output_halt", "インバーター出力停止"),
                ("dc_breaker_trip_scram", "直流遮断器トリップ"),
            ],
        ),
        (
            "22",
            "鉄道電子連動装置の軌道回路受電端電圧基準。基準：『軌道受電電圧が2.5V〜4.0Vのときは在線なし（クリア）、1.0V〜2.5V未満のときは警戒信号現示、0.3V〜1.0V未満のときは列車在線占有現示、0.3V未満のときは軌道回路断線・故障停止現示とする』。",
            "連動盤テレメトリ：第4閉塞区間の軌道受電電圧は0.65Vを計測している。連動現示を決定せよ。",
            "track_train_occupied",
            "連動盤テレメトリ：第4閉塞区間の軌道受電電圧は0.12Vを示している。連動現示を決定せよ。",
            "track_circuit_fault_stop",
            [
                ("track_clear_normal", "在線なしクリア現示"),
                ("track_caution_signal", "警戒信号現示"),
                ("track_train_occupied", "列車在線占有現示"),
                ("track_circuit_fault_stop", "軌道回路断線故障停止"),
            ],
        ),
        (
            "23",
            "超臨界水酸化廃棄物処理プラントの反応器圧力制御規程。規程：『システム圧力が22.1MPa〜24.0MPaのときは廃棄物連続注入維持、24.0MPa超25.0MPa以下のときは背圧調節弁微開、25.0MPa超26.0MPa以下のときは廃液注入停止、26.0MPa超のときは主減圧オリフィス安全弁作動とする』。",
            "中央操作卓：超臨界反応管内圧センサが24.6MPaを指示した。制御弁操作を選択せよ。",
            "scwo_backpressure_micro_open",
            "中央操作卓：超臨界反応管内圧センサが25.5MPaを指示した。廃棄物供給操作を選択せよ。",
            "scwo_feed_injection_halt",
            [
                ("scwo_continuous_feed_run", "連続注入維持"),
                ("scwo_backpressure_micro_open", "背圧調節弁微開"),
                ("scwo_feed_injection_halt", "廃液注入停止"),
                ("scwo_relief_orifice_pop", "安全減圧弁作動"),
            ],
        ),
        (
            "24",
            "半導体エッチング装置の排気ターボ分子ポンプ（TMP）温度規程。規程：『TMPモーター温度が65℃以下のときは全速定常排気、65℃超80℃以下のときはケーシング水冷流量増量、80℃超95℃以下のときはプロセスガス導入制限、95℃超のときはTMP即時緊急停止とする』。",
            "TMPコントローラ：ポンプ内部温度センサが88℃を記録した。エッチングチャンバー動作を選択せよ。",
            "tmp_process_gas_throttle",
            "TMPコントローラ：ポンプ内部温度センサが58℃で安定している。エッチングチャンバー動作を選択せよ。",
            "tmp_full_speed_steady",
            [
                ("tmp_full_speed_steady", "全速定常排気維持"),
                ("tmp_water_flow_boost", "水冷流量増量"),
                ("tmp_process_gas_throttle", "プロセスガス導入制限"),
                ("tmp_emergency_power_cut", "TMP即時緊急停止"),
            ],
        ),
        (
            "25",
            "高架水路トンネルの放水ゲート開度制御規程。規程：『流入流量が50m3/s以下のときは自然流下、50m3/s超120m3/s以下のときは放水ゲート25%開度、120m3/s超200m3/s以下のときは放水ゲート60%開度、200m3/s超のときは放水ゲート100%全開および下流警報鳴動とする』。",
            "超音波流量計：トンネル流入流量は165m3/sを計測している。ゲート開度指令を選択せよ。",
            "spillway_gate_open_60",
            "超音波流量計：トンネル流入流量は85m3/sを計測している。ゲート開度指令を選択せよ。",
            "spillway_gate_open_25",
            [
                ("spillway_natural_flow", "自然流下維持"),
                ("spillway_gate_open_25", "放水ゲート25%開度"),
                ("spillway_gate_open_60", "放水ゲート60%開度"),
                ("spillway_gate_full_open", "放水ゲート100%全開"),
            ],
        ),
    ]

    for pid, ctx, q1, t1, q2, t2, chs in k4_defs:
        choices = [{"id": cid, "text": ctxt} for cid, ctxt in chs]
        pairs.append({
            "pair_id": f"rc3_blind5_core_{pid}",
            "family": "core_rules",
            "k": 4,
            "case_1": {
                "id": f"rc3_blind5_core_{pid}_s1",
                "group_id": f"rc3_blind5_core_{pid}",
                "family": "core_rules",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1},
            },
            "case_2": {
                "id": f"rc3_blind5_core_{pid}_s2",
                "group_id": f"rc3_blind5_core_{pid}",
                "family": "core_rules",
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
            "宇宙探査機の深宇宙光通信ポインティング精度規程。規程：『角度追尾誤差が0.5μrad以内のときは超高速レーザー通信続行、0.5〜1.5μradは微小圧電アクチュエータ補正、1.5〜3.0μradは粗動ジンバル旋回追従、3.0〜5.0μradは光学同期再捕捉ビーコン照射、5.0〜8.0μradは地上局への測距トーン切替、8.0μrad超は全光リンク断絶・セーフホールドとする』。",
            "四分割フォトダイオード測定値：追尾角度誤差は2.2μradを計測した。姿勢制御機構動作を指示せよ。",
            "laser_gimbal_coarse_track",
            "四分割フォトダイオード測定値：追尾角度誤差は6.4μradまで拡大した。通信モード切替を選択せよ。",
            "laser_ranging_tone_fallback",
            [
                ("laser_comm_high_rate", "超高速レーザー通信続行"),
                ("laser_piezo_fine_adjust", "微小圧電補正"),
                ("laser_gimbal_coarse_track", "粗動ジンバル追従"),
                ("laser_beacon_reacquire", "同期再捕捉ビーコン照射"),
                ("laser_ranging_tone_fallback", "測距トーン切替"),
                ("laser_safe_hold_isolate", "全光リンク切断セーフホールド"),
            ],
        ),
        (
            "27",
            "原子力核融合トカマク型実験炉のダイバータ表面熱負荷監視規程。規程：『赤外熱カメラ測定温度が600℃以下のときは主加熱継続、600〜800℃は窒素ガスパフ放射冷却、800〜1,000℃はネオン注入エッジプラズマ冷却、1,000〜1,200℃は中性粒子入射（NBI）ビーム出力25%低減、1,200〜1,400℃は電子サイクロトロン加熱遮断、1,400℃超はディスラプション緩和ガス緊急注入とする』。",
            "プラズマ計測記録：外側ダイバータ板表面局所温度が920℃を記録した。プラズマ制御を選択せよ。",
            "tokamak_neon_edge_cool",
            "プラズマ計測記録：外側ダイバータ板表面局所温度が1,480℃に達した。緊急防護措置を選択せよ。",
            "tokamak_disruption_gas_puff",
            [
                ("tokamak_main_heat_normal", "主加熱継続"),
                ("tokamak_nitrogen_radiate", "窒素ガスパフ放射冷却"),
                ("tokamak_neon_edge_cool", "ネオン注入冷却"),
                ("tokamak_nbi_reduce_25", "NBI出力25%低減"),
                ("tokamak_ecrh_power_trip", "電子サイクロトロン遮断"),
                ("tokamak_disruption_gas_puff", "ディスラプション緩和ガス注入"),
            ],
        ),
        (
            "28",
            "大規模浮体式洋上風力発電プラットフォームの傾斜角バラスト規程。規程：『傾斜角が1.0度未満のときは定常発電維持、1.0〜2.0度は自動バラストポンプ注排水、2.0〜3.5度はブレードピッチフェザー角絞り込み、3.5〜5.0度は風車ロータ緊急空転移行、5.0〜7.0度は係留索油圧テンショナー緊急弛緩、7.0度超はプラットフォーム全系統電源緊急遮断とする』。",
            "傾斜センサ報告：現在浮体のロール角は2.8度を検出している。風車制御指令を選択せよ。",
            "fowt_pitch_feather_limit",
            "傾斜センサ報告：荒天波浪により現在浮体のロール角は6.1度に達した。係留系制御を選択せよ。",
            "fowt_mooring_tension_release",
            [
                ("fowt_normal_generation", "定常発電維持"),
                ("fowt_ballast_pump_auto", "自動バラスト注排水"),
                ("fowt_pitch_feather_limit", "ピッチフェザー角絞り込み"),
                ("fowt_rotor_freewheel_mode", "ロータ緊急空転移行"),
                ("fowt_mooring_tension_release", "係留索油圧緊急弛緩"),
                ("fowt_emergency_blackout_trip", "プラットフォーム電源遮断"),
            ],
        ),
        (
            "29",
            "医薬品凍結乾燥機の乾燥工程真空度制御規程。規程：『乾燥室内真空度が5.0Pa〜8.0Paのときは一次乾燥継続、8.0〜12.0Paはコンデンサー冷凍機2系統並入、12.0〜20.0Paは窒素微量ブリード調整、20.0〜35.0Paは棚温昇温プログラム一時停止、35.0〜50.0Paは棚温冷却降温モード、50.0Pa超は真空ブレーク保護停止とする』。",
            "ピラニ真空計データ：一次乾燥室圧力が28.4Paまで上昇した。棚温制御指示を選択せよ。",
            "lyo_shelf_ramp_hold",
            "ピラニ真空計データ：一次乾燥室圧力が6.2Paで最適領域にある。乾燥工程指示を選択せよ。",
            "lyo_primary_dry_keep",
            [
                ("lyo_primary_dry_keep", "一次乾燥継続"),
                ("lyo_condenser_dual_run", "冷凍機2系統並入"),
                ("lyo_nitrogen_micro_bleed", "窒素微量ブリード調整"),
                ("lyo_shelf_ramp_hold", "棚温昇温プログラム一時停止"),
                ("lyo_shelf_cooldown_mode", "棚温冷却降温モード"),
                ("lyo_vacuum_break_abort", "真空ブレーク保護停止"),
            ],
        ),
        (
            "30",
            "下水終末処理場の活性汚泥ディフューザー送気圧制御規程。規程：『エア供給圧力が35kPa〜45kPaのときはブロワ定常自動運転、45〜55kPaはディフューザー膜面逆洗パージ、55〜65kPaは余剰空気バイパス弁開放、65〜75kPaはブロワ吸入ガイドベーン絞り、75〜85kPaは稼働ブロワ1台降段停止、85kPa超は全ブロワ緊急非常停止弁全開とする』。",
            "空気母管圧力測定：送気圧力が51.2kPaを記録し目詰まり傾向を示す。配管動作を選択せよ。",
            "diffuser_membrane_backwash",
            "空気母管圧力測定：送気圧力が78.4kPaまで過大上昇した。ブロワ台数制御を選択せよ。",
            "blower_stepdown_stop_one",
            [
                ("blower_normal_auto_run", "ブロワ定常自動運転"),
                ("diffuser_membrane_backwash", "ディフューザー膜面逆洗"),
                ("air_bypass_valve_open", "余剰空気バイパス開放"),
                ("blower_inlet_vane_choke", "吸入ガイドベーン絞り"),
                ("blower_stepdown_stop_one", "稼働ブロワ1台降段停止"),
                ("blower_emergency_trip_vent", "全ブロワ緊急非常停止"),
            ],
        ),
    ]

    for pid, ctx, q1, t1, q2, t2, chs in k6_defs:
        choices = [{"id": cid, "text": ctxt} for cid, ctxt in chs]
        pairs.append({
            "pair_id": f"rc3_blind5_core_{pid}",
            "family": "core_rules",
            "k": 6,
            "case_1": {
                "id": f"rc3_blind5_core_{pid}_s1",
                "group_id": f"rc3_blind5_core_{pid}",
                "family": "core_rules",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1},
            },
            "case_2": {
                "id": f"rc3_blind5_core_{pid}_s2",
                "group_id": f"rc3_blind5_core_{pid}",
                "family": "core_rules",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2},
            },
        })

    return pairs
