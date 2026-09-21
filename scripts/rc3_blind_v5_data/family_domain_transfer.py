"""Blind v5 Family: Domain Transfer (30 pairs, 60 cases).

Choice count distribution:
- K=2: 5 pairs (dom_01 to dom_05)
- K=3: 10 pairs (dom_06 to dom_15)
- K=4: 10 pairs (dom_16 to dom_25)
- K=6: 5 pairs (dom_26 to dom_30)

Zero model inference during authoring; 100% fresh domain scenarios.
Token length strictly controlled (all <= 350 tokens).
Features specialized scientific, industrial, aerospace, and biomedical technical domains.
"""

from __future__ import annotations
from typing import Any, Dict, List


def get_domain_transfer_pairs() -> List[Dict[str, Any]]:
    pairs = []

    # K=2: 5 pairs (01..05)
    k2_defs = [
        (
            "01",
            "大型放射光施設のアンジュレータ磁気ギャップ保護規程。規程：『蓄積電子ビーム電流が450mA以上のときは最小磁気ギャップ開度を10.0mm以上に制限し、450mA未満のときは高輝度モード開度7.5mmまでの接近を許可する』。",
            "マシンステータス：リング蓄積電流値は482mAを記録している。アンジュレータギャップ制御を選択せよ。",
            "gap_limit_ten_mm",
            "マシンステータス：リング蓄積電流値は310mAまで減衰している。アンジュレータギャップ制御を選択せよ。",
            "gap_permit_seven_half_mm",
            [
                ("gap_limit_ten_mm", "最小ギャップ10mm制限"),
                ("gap_permit_seven_half_mm", "高輝度7.5mm接近許可"),
            ],
        ),
        (
            "02",
            "極低温電子顕微鏡（Cryo-EM）の液体窒素コールドステージ温度維持基準。基準：『試料グリッド温度が-170℃以下を維持しているときは高分解能単粒子画像連続撮影を実行し、-170℃を超過したときは試料結晶化防止のため撮影を中断しスラッシュ再充填を行う』。",
            "モニタ温度：試料ステージ測温抵抗体は-182℃で安定している。顕微鏡動作を選択せよ。",
            "cryo_continue_image_capture",
            "モニタ温度：試料ステージ測温抵抗体が-164℃まで上昇した。顕微鏡動作を選択せよ。",
            "cryo_abort_refill_nitrogen",
            [
                ("cryo_continue_image_capture", "高分解能単粒子撮影続行"),
                ("cryo_abort_refill_nitrogen", "撮影中断スラッシュ再充填"),
            ],
        ),
        (
            "03",
            "トカマク型磁気核融合実験炉のダイバータ熱負荷制御規程。規程：『タングステンターゲット板の局所熱流束が15MW/m2以上のときは磁気ストライクポイントスイープ周波数を10Hzに増速し、15MW/m2未満のときは定常スイープ2Hzを維持する』。",
            "熱赤外カメラ計測：ダイバータ外側ストライクポイント熱流束は18.4MW/m2を記録。スイープ制御を選択せよ。",
            "divertor_sweep_fast_ten_hz",
            "熱赤外カメラ計測：ダイバータ外側ストライクポイント熱流束は8.7MW/m2で許容域。スイープ制御を選択せよ。",
            "divertor_sweep_steady_two_hz",
            [
                ("divertor_sweep_fast_ten_hz", "スイープ周波数10Hz増速"),
                ("divertor_sweep_steady_two_hz", "定常スイープ2Hz維持"),
            ],
        ),
        (
            "04",
            "深海熱水噴出孔自律探査機（AUV）のチタン耐圧殻腐食電位判定規程。規程：『参照電極対比の自然腐食電位が-650mV以下のときは印加電流型アノード防食出力を増加し、-650mV超のときは現在の防食電流出力を保持する』。",
            "探査機自己診断：チタン殻の腐食電位モニタが-720mVを示している。カソード防食出力を選択せよ。",
            "cathodic_increase_current",
            "探査機自己診断：チタン殻の腐食電位モニタが-590mVを示している。カソード防食出力を選択せよ。",
            "cathodic_maintain_current",
            [
                ("cathodic_increase_current", "アノード防食電流増加"),
                ("cathodic_maintain_current", "現在の防食電流を保持"),
            ],
        ),
        (
            "05",
            "量子アニーリング計算機希釈冷凍機のパルスタブコンプレッサ保護規程。規程：『冷却ヘリウム循環系統の高圧側圧力が2.2MPa以上のときは圧力逃がしバイパス弁を微開し、2.2MPa未満のときは主循環圧縮を全負荷維持する』。",
            "圧力トランスデューサ：コンプレッサ吐出圧力は2.41MPaに達した。循環系統制御を選択せよ。",
            "pulse_tube_open_bypass",
            "圧力トランスデューサ：コンプレッサ吐出圧力は1.95MPaで推移している。循環系統制御を選択せよ。",
            "pulse_tube_maintain_full_load",
            [
                ("pulse_tube_open_bypass", "圧力逃がしバイパス弁微開"),
                ("pulse_tube_maintain_full_load", "主循環圧縮全負荷維持"),
            ],
        ),
    ]

    for pid, ctx, q1, t1, q2, t2, chs in k2_defs:
        choices = [{"id": cid, "text": ctxt} for cid, ctxt in chs]
        pairs.append({
            "pair_id": f"rc3_blind5_dom_{pid}",
            "family": "domain_transfer",
            "k": 2,
            "case_1": {
                "id": f"rc3_blind5_dom_{pid}_s1",
                "group_id": f"rc3_blind5_dom_{pid}",
                "family": "domain_transfer",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1},
            },
            "case_2": {
                "id": f"rc3_blind5_dom_{pid}_s2",
                "group_id": f"rc3_blind5_dom_{pid}",
                "family": "domain_transfer",
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
            "植物工場養液栽培の電気伝導度（EC）自動調整基準。基準：『養液EC値が1.2mS/cm未満のときはA/B原液同時定量注入、1.2〜1.8mS/cmの適正範囲では原水補給のみによる循環維持、1.8mS/cm超の過濃縮時は原水強制希釈フラッシングを実行する』。",
            "養液センサ計測：ベッド循環液のEC値は0.95mS/cmを示している。薬液ポンプ動作を選択せよ。",
            "fertigation_dose_concentrates",
            "養液センサ計測：ベッド循環液のEC値は2.35mS/cmを示している。薬液ポンプ動作を選択せよ。",
            "fertigation_flush_dilution_water",
            [
                ("fertigation_dose_concentrates", "原液同時定量注入"),
                ("fertigation_circulate_fresh_only", "原水補給循環維持"),
                ("fertigation_flush_dilution_water", "原水強制希釈フラッシング"),
            ],
        ),
        (
            "07",
            "金属3Dプリンター（電子ビーム粉末床溶融結合）の真空チャンバー運用規定。規定：『チャンバー内真空度が1.0e-3Pa以下のときは電子銃フィラメント点火を許可、1.0e-3〜5.0e-2Paの間はターボ分子ポンプ排気継続、5.0e-2Pa超のリーク時はフィラメント遮断および不活性ガスベントを実行する』。",
            "ペニング真空計計測：チャンバー圧力は4.2e-4Paに到達した。電子ビーム制御を選択せよ。",
            "eb_permit_filament_ignition",
            "ペニング真空計計測：チャンバー圧力が1.8e-1Paまで急激に悪化した。電子ビーム制御を選択せよ。",
            "eb_trip_filament_vent_inert",
            [
                ("eb_permit_filament_ignition", "電子銃フィラメント点火許可"),
                ("eb_continue_turbo_evacuate", "ターボ分子ポンプ排気継続"),
                ("eb_trip_filament_vent_inert", "フィラメント遮断ガスベント"),
            ],
        ),
        (
            "08",
            "超臨界水熱酸化（SCWO）排水処理反応器の温度・圧力インターロック。規程：『反応温度が400℃以上かつ圧力が25MPa以上のときは難分解性廃液の定常送液を許可、温度374〜400℃の間は予熱純水循環モードを維持、温度が臨界点374℃未満または圧力22MPa未満に低下したときは緊急純水クエンチパージを実行する』。",
            "プロセスログ：反応器温度418℃、圧力26.2MPaを安定計測。送液ポンプ動作を選択せよ。",
            "scwo_feed_hazardous_waste",
            "プロセスログ：反応器温度352℃、圧力20.1MPaに低下し亜臨界領域に突入。送液ポンプ動作を選択せよ。",
            "scwo_emergency_pure_water_quench",
            [
                ("scwo_feed_hazardous_waste", "難分解性廃液定常送液許可"),
                ("scwo_preheat_pure_water_circulate", "予熱純水循環モード維持"),
                ("scwo_emergency_pure_water_quench", "緊急純水クエンチパージ"),
            ],
        ),
        (
            "09",
            "宇宙ステーション水再生システム（WPA）の接触酸化触媒塔制御。規程：『全有機炭素（TOC）濃度が200ppb以下のときは処理水を飲料水貯蔵タンクへ送水、200〜1,000ppbの間は触媒塔再循環ループへ戻す、1,000ppb超の汚染時はイオン交換吸着ベッドへ即時隔離迂回させる』。",
            "インラインTOC計：出口水のTOC測定値は65ppbを記録。送水バルブを選択せよ。",
            "wpa_route_potable_tank",
            "インラインTOC計：出口水のTOC測定値は1,420ppbに跳ね上がった。送水バルブを選択せよ。",
            "wpa_divert_ion_exchange_bed",
            [
                ("wpa_route_potable_tank", "飲料水貯蔵タンク送水"),
                ("wpa_recirculate_catalytic_loop", "触媒塔再循環ループ戻し"),
                ("wpa_divert_ion_exchange_bed", "イオン交換ベッド隔離迂回"),
            ],
        ),
        (
            "10",
            "航空機用ガスタービンエンジンの可変静翼（VSV）開度制御規程。規程：『補正高圧圧縮機回転数（N2）が92%以上のときはVSVを全開設計位置に保持、80〜92%の間は部分絞りスケジュール追従、80%未満の低回転時はサージング防止のためVSVを最大クローズ位置に設定する』。",
            "エンジンFADECモニタ：高圧軸N2補正回転数は95.4%である。VSVアクチュエータ指令を選択せよ。",
            "vsv_command_full_open",
            "エンジンFADECモニタ：高圧軸N2補正回転数は74.8%（アイドル降下中）である。VSVアクチュエータ指令を選択せよ。",
            "vsv_command_max_close",
            [
                ("vsv_command_full_open", "VSV全開設計位置保持"),
                ("vsv_command_schedule_tracking", "部分絞りスケジュール追従"),
                ("vsv_command_max_close", "サージ防止最大クローズ"),
            ],
        ),
        (
            "11",
            "海洋調査船のマルチビーム音響測深機（MBES）ピング送信レート基準。基準：『直下水深が500m未満のときは送信周波数を400kHz高分解能モード、500〜2,000mの間は200kHz中深度モード、2,000m超の深海域では70kHz大水深モードへ切り替える』。",
            "ナブソナー水深測定：現在海底までの水深は320mである。MBES動作モードを選択せよ。",
            "mbes_high_res_400khz",
            "ナブソナー水深測定：海溝横断中につき現在水深は4,850mである。MBES動作モードを選択せよ。",
            "mbes_deep_water_70khz",
            [
                ("mbes_high_res_400khz", "400kHz高分解能モード"),
                ("mbes_mid_depth_200khz", "200kHz中深度モード"),
                ("mbes_deep_water_70khz", "70kHz大水深モード"),
            ],
        ),
        (
            "12",
            "医薬品バイオリアクター培養液の溶存酸素（DO）カスケーディング制御基準。基準：『DOが40%未満に低下したときは攪拌翼回転数を段階増速、40〜60%の適正域では現行回転数と通気量を維持、60%超過時はスパージャーへの純酸素供給バルブを絞り空気通気に切り替える』。",
            "インラインDOプローブ計測：培養液中DO濃度は28%まで低下した。カスケーディング動作を選択せよ。",
            "do_cascade_increase_rpm",
            "インラインDOプローブ計測：培養液中DO濃度は72%まで過剰上昇した。カスケーディング動作を選択せよ。",
            "do_cascade_throttle_o2_air_switch",
            [
                ("do_cascade_increase_rpm", "攪拌翼回転数段階増速"),
                ("do_cascade_maintain_steady", "現行回転数通気量維持"),
                ("do_cascade_throttle_o2_air_switch", "酸素供給絞り空気通気切替"),
            ],
        ),
        (
            "13",
            "炭素繊維複合材料（CFRP）高圧オートクレーブ成形規程。規程：『エポキシ樹脂硬化度示差熱分析値が85%以上のときは降温冷却シーケンスを開始、50〜85%の間は等温保持圧力0.7MPaを継続、50%未満かつ昇温速度不足時は加熱ヒーター出力をブーストする』。",
            "熱電対・硬化センサ監視：硬化度は91%に達し重合発熱が収束した。オートクレーブ制御を選択せよ。",
            "autoclave_start_cooling_cycle",
            "熱電対・硬化センサ監視：硬化度は34%にとどまり昇温勾配が設定曲線より遅延している。オートクレーブ制御を選択せよ。",
            "autoclave_boost_heating_power",
            [
                ("autoclave_start_cooling_cycle", "降温冷却シーケンス開始"),
                ("autoclave_hold_isothermal_pressure", "等温保持圧力維持"),
                ("autoclave_boost_heating_power", "加熱ヒーター出力ブースト"),
            ],
        ),
        (
            "14",
            "半導体プラズマエッチング装置の終点検出（EPD）分光基準。基準：『特定波長（405nm）発光強度がバックグラウンド比10%以下に減衰したときはエッチング終点判定としオーバーエッチングタイマーへ移行、10〜80%の間は主エッチング高周波出力を維持、80%以上で反射波過大時はインピーダンス整合器再同調を実行する』。",
            "EPD分光器ログ：405nm発光強度がピーク値の6%まで急減した。エッチングシーケンスを選択せよ。",
            "epd_transition_overetch_timer",
            "EPD分光器ログ：発光強度95%の高出力中だがプラズマ反射波電力が200Wに増大した。エッチングシーケンスを選択せよ。",
            "epd_retune_impedance_matcher",
            [
                ("epd_transition_overetch_timer", "終点判定オーバーエッチ移行"),
                ("epd_maintain_main_rf_etch", "主エッチング高周波出力維持"),
                ("epd_retune_impedance_matcher", "インピーダンス整合器再同調"),
            ],
        ),
        (
            "15",
            "法医学DNA型鑑定におけるキャピラリー電気泳動注入電圧規程。規程：『標準ラダーDNA断片の蛍光強度が3,000RFU以上のときは動電サンプリング電圧を3kVに低減、1,000〜3,000RFUの間は標準注入電圧5kVを適用、1,000RFU未満の微量ピーク時はサンプリング電圧を8kVへ増圧して注入時間を延長する』。",
            "キャピラリー検出信号：先行ラダーピーク強度は4,500RFUを記録した。サンプル注入条件を選択せよ。",
            "dna_voltage_reduce_3kv",
            "キャピラリー検出信号：微量陳旧骨サンプルのラダーピーク強度は420RFUにとどまる。サンプル注入条件を選択せよ。",
            "dna_voltage_boost_8kv_extend",
            [
                ("dna_voltage_reduce_3kv", "注入電圧3kV低減"),
                ("dna_voltage_standard_5kv", "標準注入電圧5kV適用"),
                ("dna_voltage_boost_8kv_extend", "注入電圧8kV増圧時間延長"),
            ],
        ),
    ]

    for pid, ctx, q1, t1, q2, t2, chs in k3_defs:
        choices = [{"id": cid, "text": ctxt} for cid, ctxt in chs]
        pairs.append({
            "pair_id": f"rc3_blind5_dom_{pid}",
            "family": "domain_transfer",
            "k": 3,
            "case_1": {
                "id": f"rc3_blind5_dom_{pid}_s1",
                "group_id": f"rc3_blind5_dom_{pid}",
                "family": "domain_transfer",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1},
            },
            "case_2": {
                "id": f"rc3_blind5_dom_{pid}_s2",
                "group_id": f"rc3_blind5_dom_{pid}",
                "family": "domain_transfer",
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
            "リチウムイオン二次電池ドライルームの露点管理基準。基準：『給気露点が-60℃以下のときは極板塗工乾燥ラインの全速稼働を許可、-60〜-50℃の間は露点注意アラーム下で塗工速度を30%減速、-50〜-40℃の間は塗工即時停止・極板巻き取り退避、-40℃超の水分混入時は除湿ローター再生加熱ヒーターを全開し外気遮断ダンパーを閉鎖する』。",
            "鏡面冷却式露点計計測：ドライルーム露点は-68.5℃を維持。生産指示を選択せよ。",
            "dryroom_full_speed_coating",
            "鏡面冷却式露点計計測：ドライルーム露点が-36.2℃まで急激に上昇した。設備制御を選択せよ。",
            "dryroom_heater_full_damper_close",
            [
                ("dryroom_full_speed_coating", "塗工乾燥ライン全速稼働"),
                ("dryroom_derate_coating_speed", "塗工速度30%減速稼働"),
                ("dryroom_stop_coating_evacuate", "塗工停止極板巻き取り退避"),
                ("dryroom_heater_full_damper_close", "ヒーター全開外気遮断ダンパー閉鎖"),
            ],
        ),
        (
            "17",
            "連続製鋼鋳造設備（CCM）のモールドパウダー厚みおよび湯面レベル制御規程。規程：『溶鋼湯面レベル変動が±2mm以内のときは引抜速度を定格1.6m/minで維持、変動±2〜±5mmの間は引抜速度を1.2m/minへ減速、変動±5〜±10mmの間はモールド電磁ブレーキ磁場を最大印加、変動±10mm超またはブレークアウト予知発報時は自動非常停止シーケンスを実行する』。",
            "渦流式湯面レベル計：溶鋼表面の上下動は±0.8mmで極めて平穏。鋳造制御を選択せよ。",
            "ccm_maintain_rated_speed",
            "渦流式湯面計：溶鋼レベルが短時間で±14mm乱高下し熱電対が局所凝固殻破断（ブレークアウト兆候）を検知。鋳造制御を選択せよ。",
            "ccm_emergency_abort_sequence",
            [
                ("ccm_maintain_rated_speed", "引抜速度定格1.6m/min維持"),
                ("ccm_reduce_speed_1_2", "引抜速度1.2m/min減速"),
                ("ccm_max_em_brake_field", "電磁ブレーキ磁場最大印加"),
                ("ccm_emergency_abort_sequence", "自動非常停止シーケンス実行"),
            ],
        ),
        (
            "18",
            "海底光海底ケーブル敷設船のダイナミックポジショニング（DP）スラスタ運用規程。規程：『船位偏向誤差が1.0m未満のときは省電力DPグリーンモード運用、1.0〜3.0mの間は追従ゲインを強めて標準DPモード、3.0〜5.0mの間は全予備アジマススラスタを急速並入、5.0m超過時はケーブル破断防止のため繰出ウィンチをフリーホイール緊急展張する』。",
            "DGPS・音響測位演算：現在船位の敷設ルート中心線からの偏位は0.35mである。DPモードを選択せよ。",
            "dp_green_economy_mode",
            "DGPS・音響測位演算：急な潮流変化により船位偏位が6.8mに達し海底ケーブル張力が危険域に迫る。対応を選択せよ。",
            "dp_freewheel_cable_winch",
            [
                ("dp_green_economy_mode", "省電力DPグリーン運用"),
                ("dp_standard_tracking_mode", "標準DPモード追従ゲイン強化"),
                ("dp_parallel_auxiliary_thrusters", "全予備アジマススラスタ急速並入"),
                ("dp_freewheel_cable_winch", "繰出ウィンチフリーホイール緊急展張"),
            ],
        ),
        (
            "19",
            "石油天然ガス採掘海底パイプラインのインテリジェントピグ（管内検査器）走行規程。規程：『ピグ差圧推進速度が1.5〜2.5m/sのときは高解像度漏洩磁束（MFL）探傷を連続記録、速度1.5m/s未満のときは元圧昇圧弁を微開して速度加速、速度2.5〜4.0m/sの間はバイパス弁を開いて減速調整、速度4.0m/s超またはスタック検知時は管路受入トラップ緊急受入弁を全開する』。",
            "ピグ超音波オドメーター計測：管内走行実速度は2.05m/sを維持。探傷記録を選択せよ。",
            "pig_mfl_continuous_record",
            "ピグ超音波オドメーター計測：速度が急低下し0.3m/sとなり管内スラッジによる固着（スタック）傾向を示す。速度制御を選択せよ。",
            "pig_boost_inlet_pressure_valve",
            [
                ("pig_mfl_continuous_record", "高解像度MFL探傷連続記録"),
                ("pig_boost_inlet_pressure_valve", "元圧昇圧弁微開速度加速"),
                ("pig_open_bypass_valve_slow", "バイパス弁開減速調整"),
                ("pig_open_trap_emergency_receive", "受入トラップ緊急受入弁全開"),
            ],
        ),
        (
            "20",
            "極小人工衛星用パルスプラズマスラスター（PPT）放電管理規程。規程：『メインコンデンサ充電電圧が1,800V以上のときは放電点火トリガーを許可、1,500〜1,800Vの間はDC-DC昇圧コンバータ充電継続、1,200〜1,500Vの間は点火禁止・バス電圧監視、1,200V未満のときはコンデンサ内部短絡保護のため主給電リレーを完全開放遮断する』。",
            "テレメトリ計測：パルスコイルコンデンサ両端電圧は1,920Vを記録。PPT制御を選択せよ。",
            "ppt_permit_ignition_trigger",
            "テレメトリ計測：充電コマンド投入後もコンデンサ電圧が980Vまで降下し漏洩電流急増を検知。PPT制御を選択せよ。",
            "ppt_open_main_power_relay",
            [
                ("ppt_permit_ignition_trigger", "放電点火トリガー許可"),
                ("ppt_continue_dcdc_charging", "DC-DC昇圧充電継続"),
                ("ppt_inhibit_ignition_monitor", "点火禁止バス電圧監視"),
                ("ppt_open_main_power_relay", "主給電リレー完全開放遮断"),
            ],
        ),
        (
            "21",
            "医薬品凍結乾燥注射剤バイアルの打栓（ストッパー打込み）圧力規程。規程：『油圧シェルフ下降圧力が35〜45kNの範囲内のときは正常打栓完了シーケンスを実行、25〜35kNの間は打栓不完全とみなし加圧ストローク微小追加、45〜60kNの間はバイアル破損防止のため加圧停止・位置保持、60kN超過時は油圧リリーフ弁緊急開放および真空破壊窒素パージを行う』。",
            "油圧ロードセル計測：打栓棚の全荷重は41.2kNで均等にかかっている。打栓制御を選択せよ。",
            "lyo_complete_stopper_sequence",
            "油圧ロードセル計測：ガラスバイアルの噛み込みにより加圧荷重が68.5kNへ過大跳ね上がりを記録。安全処置を選択せよ。",
            "lyo_relief_valve_nitrogen_purge",
            [
                ("lyo_complete_stopper_sequence", "正常打栓完了シーケンス"),
                ("lyo_add_micro_stroke_pressure", "加圧ストローク微小追加"),
                ("lyo_hold_shelf_position_stop", "加圧停止位置保持"),
                ("lyo_relief_valve_nitrogen_purge", "油圧開放窒素パージ実行"),
            ],
        ),
        (
            "22",
            "水素ステーションの超高圧複合容器蓄圧器（90MPa）充填安全基準。基準：『蓄圧器内部ガス温度が40℃以下のときは最大流量急速差圧充填を許可、40〜65℃の間はプレクール熱交換器温度を-40℃へ下げて中速充填、65〜85℃の間は充填一時停止・自然放冷待機、85℃超過時は非常遮断弁全閉・安全弁大気放散ラインを開放する』。",
            "水素温度センサ：蓄圧バンク内部水素ガス温度は28.5℃である。車両充填制御を選択せよ。",
            "h2_rapid_max_flow_fill",
            "水素温度センサ：外気温上昇と断熱圧縮熱により内部温度が89.2℃に達した。安全処置を選択せよ。",
            "h2_emergency_shutdown_vent",
            [
                ("h2_rapid_max_flow_fill", "最大流量急速差圧充填許可"),
                ("h2_precool_throttle_mid_fill", "プレクール強化中速充填"),
                ("h2_pause_cooling_standby", "充填一時停止自然放冷待機"),
                ("h2_emergency_shutdown_vent", "非常遮断弁閉放散ライン開放"),
            ],
        ),
        (
            "23",
            "鉱山坑内換気立坑のメタンガス自動排出ファン制御基準。基準：『立坑坑道メタン濃度が0.5%未満のときはインバータ排風ファン低速定常換気、0.5〜1.0%の間は排風ファン全速ブースト運転、1.0〜1.5%の間は坑内作業員退避勧告・入気ダンパー増開、1.5%超過時は全電気系統強制停電・防爆ファン単独最大排気配分を実行する』。",
            "ガス検知器アレイ：立坑排気中のメタン濃度は0.18%で推移。排風ファン制御を選択せよ。",
            "mine_fan_low_speed_steady",
            "ガス検知器アレイ：採掘切羽の落盤に伴いメタン濃度が2.4%に急伸した。保安制御を選択せよ。",
            "mine_blackout_explosion_proof_max",
            [
                ("mine_fan_low_speed_steady", "排風ファン低速定常換気"),
                ("mine_fan_full_speed_boost", "排風ファン全速ブースト"),
                ("mine_evacuate_workers_open_damper", "作業員退避入気ダンパー増開"),
                ("mine_blackout_explosion_proof_max", "強制停電防爆ファン最大排気"),
            ],
        ),
        (
            "24",
            "超電導量子ビット制御用極低温高周波（RF）配線の熱遮蔽管理基準。基準：『4Kステージ熱アンカー温度が4.2K以下のときはRFパルスシーケンス実行を承認、4.2〜5.0Kの間はパルス間隔を倍増して熱負荷低減、5.0〜6.0Kの間は量子ビット初期化待機モード、6.0K超の断熱真空破壊時はRFクライオアンプ電源遮断と極低温サーキュレータ保護接地を実行する』。",
            "ルテニウム酸化物温度計：4Kアンカーステージは3.85Kを指示している。量子測定制御を選択せよ。",
            "rf_approve_pulse_sequence",
            "ルテニウム酸化物温度計：断熱劣化により4Kステージ温度が6.72Kに達した。保全処置を選択せよ。",
            "rf_trip_amplifier_protect_ground",
            [
                ("rf_approve_pulse_sequence", "RFパルスシーケンス実行承認"),
                ("rf_double_pulse_spacing_reduce", "パルス間隔倍増熱負荷低減"),
                ("rf_qubit_init_standby", "量子ビット初期化待機"),
                ("rf_trip_amplifier_protect_ground", "アンプ遮断サーキュレータ保護接地"),
            ],
        ),
        (
            "25",
            "宇宙望遠鏡CMOS撮像素子の受光冷却ペルチェ素子駆動規程。規程：『素子暗電流温度が-90℃以下のときは科学観測長時間露光を許可、-90〜-75℃の間はペルチェ駆動電流を段階増加、-75〜-60℃の間は観測休止・ホットピクセル較正フレーム取得、-60℃超の冷却不能時は撮像シャッター全閉・ラジエーターデフロストヒーターを投入する』。",
            "検出器テレメトリ：CMOSセンサ温度は-94.2℃で極低温維持。観測指示を選択せよ。",
            "space_permit_long_exposure",
            "検出器テレメトリ：ペルチェ電源系不調によりセンサ温度が-52.0℃まで過熱した。保全指示を選択せよ。",
            "space_close_shutter_heaters_on",
            [
                ("space_permit_long_exposure", "科学観測長時間露光許可"),
                ("space_step_up_peltier_current", "ペルチェ駆動電流段階増加"),
                ("space_hot_pixel_calibration", "観測休止較正フレーム取得"),
                ("space_close_shutter_heaters_on", "シャッター全閉ヒーター投入"),
            ],
        ),
    ]

    for pid, ctx, q1, t1, q2, t2, chs in k4_defs:
        choices = [{"id": cid, "text": ctxt} for cid, ctxt in chs]
        pairs.append({
            "pair_id": f"rc3_blind5_dom_{pid}",
            "family": "domain_transfer",
            "k": 4,
            "case_1": {
                "id": f"rc3_blind5_dom_{pid}_s1",
                "group_id": f"rc3_blind5_dom_{pid}",
                "family": "domain_transfer",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1},
            },
            "case_2": {
                "id": f"rc3_blind5_dom_{pid}_s2",
                "group_id": f"rc3_blind5_dom_{pid}",
                "family": "domain_transfer",
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
            "超音速風洞実験設備のシュリーレン光学測定および衝撃波制御規程。規程：『測定部マッハ数が設計値M=2.5±0.05のときはシュリーレン高速度カメラ撮影、M=2.0〜2.45の間は超音速ノズル可動ディフューザー開度調整、M=1.5〜2.0の間は第2スロート絞り、M=1.0〜1.5の間はプレナム室排気ブローダウン増圧、M<1.0の遷音速閉塞時は模型迎角をゼロ度戻し、風洞吸入全圧が定格超過時は非常クイックベント弁を開放する』。",
            "ピトー管静圧・全圧計測：測定部マッハ数はM=2.52を記録し衝撃波が安定形成。光学測定を選択せよ。",
            "wind_tunnel_schlieran_capture",
            "ピトー管計測：模型の失速剥離により測定部マッハ数がM=0.85に急落し窒息現象（チョーキング）が発生。風洞制御を選択せよ。",
            "wind_tunnel_zero_aoa_unblock",
            [
                ("wind_tunnel_schlieran_capture", "シュリーレン高速撮影実行"),
                ("wind_tunnel_diffuser_adjust", "ノズル可動ディフューザー調整"),
                ("wind_tunnel_throat_choke", "第2スロート絞り調整"),
                ("wind_tunnel_plenum_boost", "プレナム室ブローダウン増圧"),
                ("wind_tunnel_zero_aoa_unblock", "模型迎角ゼロ戻し閉塞解除"),
                ("wind_tunnel_quick_vent_dump", "全圧超過クイックベント開放"),
            ],
        ),
        (
            "27",
            "高密度プラズマ核融合実験装置の電子サイクロトロン加熱（ECH）ジャイロトロン保護基準。基準：『出力導波管内アーク光検知器が全点消灯のときは高周波出力1MW連続注入、アーク反射電力50〜100kWの間はパルス変調幅を20%間引き、100〜200kWの間はビーム加速電圧低減、真空度劣化警報時はコレクタ掃引磁場増磁、導波管アーク検知時はジャイロトロン高圧電源を10マイクロ秒以内遮断、冷却水喪失時は本体超電導マグネット緊急消磁を実行する』。",
            "高周波モニタ：導波管内アーク光検知なし、反射波電力は15kWで正常。ECH制御を選択せよ。",
            "ech_gyrotron_inject_1mw",
            "高速受光素子：ミリ波導波管窓直前で猛烈なアーク放電閃光が検知された。直ちに実行すべき保護動作を選択せよ。",
            "ech_fast_crowbar_trip_10us",
            [
                ("ech_gyrotron_inject_1mw", "高周波出力1MW連続注入"),
                ("ech_derate_pulse_width_20", "パルス変調幅20%間引き"),
                ("ech_reduce_beam_voltage", "ビーム加速電圧低減"),
                ("ech_boost_collector_sweep", "コレクタ掃引磁場増磁"),
                ("ech_fast_crowbar_trip_10us", "高圧電源10マイクロ秒高速遮断"),
                ("ech_quench_supercon_magnet", "超電導マグネット緊急消磁"),
            ],
        ),
        (
            "28",
            "超高真空走査透過型電子顕微鏡（STEM）の冷陰極電界放出型電子銃（CFEG）フラッシング規程。規程：『エミッション電流変動率が2%以下のときは原子分解能EDS元素マッピング分析を実行、変動率2〜5%の間は収差補正器オートチューニング、変動率5〜10%の間はチップ加熱フラッシング待機シーケンス、変動率10〜20%の間は電子銃バルブ閉止、真空度1e-8Pa悪化時はゲッターポンプ再活性化、高圧放電アーク発生時は加速管バイアス緊急アース接地を実行する』。",
            "エミッションモニタ：タングステン単結晶チップ放出電流変動は0.8%で極めて安定。顕微鏡制御を選択せよ。",
            "stem_atomic_eds_mapping",
            "エミッションモニタ：残留ガス分子のチップ吸着により電流変動率が7.4%に増大した。推奨される処置を選択せよ。",
            "stem_flashing_standby_cycle",
            [
                ("stem_atomic_eds_mapping", "原子分解能EDSマッピング実行"),
                ("stem_autotune_corrector", "収差補正器オートチューニング"),
                ("stem_flashing_standby_cycle", "チップ加熱フラッシング待機"),
                ("stem_close_gun_valve", "電子銃真空バルブ閉止"),
                ("stem_reactivate_getter_pump", "ゲッターポンプ再活性化"),
                ("stem_emergency_ground_bias", "加速管バイアス緊急接地"),
            ],
        ),
        (
            "29",
            "バイオ医薬品ダウンストリームの限外ろ過・タンジェンシャルフロー（TFC/UF）膜濃縮規程。規程：『膜間差圧（TMP）が0.08MPa以下のときは定格循環流速での目的タンパク質連続濃縮、TMPが0.08〜0.12MPaの間はフィードポンプ流量15%低減、TMPが0.12〜0.18MPaの間は透過液透過弁を微小絞り、TMPが0.18〜0.25MPaの間はバッファー循環モード一時切替、TMPが0.25MPa超のゲル層形成時はCIP定置薬品洗浄シーケンス、配管内圧0.35MPa超時は安全リリーフ弁全開を実行する』。",
            "差圧トランスミッタ計測：膜モジュールTMPは0.052MPaで膜面ファウリングなし。ろ過制御を選択せよ。",
            "uf_continue_protein_concentration",
            "差圧トランスミッタ計測：タンパク質凝集体の堆積によりTMPが0.285MPaに達し膜面透過が閉塞。ろ過制御を選択せよ。",
            "uf_execute_cip_chemical_wash",
            [
                ("uf_continue_protein_concentration", "目的タンパク質連続濃縮"),
                ("uf_reduce_feed_flow_15", "フィード流量15%低減"),
                ("uf_throttle_permeate_valve", "透過液透過弁微小絞り"),
                ("uf_switch_buffer_circulation", "バッファー循環一時切替"),
                ("uf_execute_cip_chemical_wash", "CIP定置薬品洗浄シーケンス"),
                ("uf_open_safety_relief_valve", "安全リリーフ弁全開"),
            ],
        ),
        (
            "30",
            "深宇宙探査機の姿勢軌道制御系（AOCS）スターラッカー恒星同定アルゴリズム規程。規程：『観測視野内恒星照合数が6星以上のときは最高精度カルマンフィルタ姿勢推定モード、照合4〜5星の間はジャイロ積算補正追従モード、照合2〜3星の間は太陽センサ姿勢確定補助、照合1星以下のときはスターカタログ空間探索範囲拡張、迷光雑音過大時はバッフルヒーター温度調整、全天同定完全喪失時は慣性モーメンタムホイールスピンアンロード・セーフモード移行を実行する』。",
            "スタースフィア画像処理ログ：カメラ視野内で高信頼度に同定されたガイド星数は8星である。AOCSモードを選択せよ。",
            "aocs_kalman_high_precision_attitude",
            "スタースフィア画像処理ログ：太陽フレア高エネルギー粒子照射により全天同定星数がゼロとなり完全ロストした。AOCS制御を選択せよ。",
            "aocs_safe_mode_spin_unload",
            [
                ("aocs_kalman_high_precision_attitude", "高精度カルマン姿勢推定"),
                ("aocs_gyro_assist_tracking", "ジャイロ積算補正追従"),
                ("aocs_sun_sensor_assist", "太陽センサ姿勢確定補助"),
                ("aocs_expand_catalog_search", "カタログ空間探索範囲拡張"),
                ("aocs_baffle_heater_adjust", "バッフルヒーター温度調整"),
                ("aocs_safe_mode_spin_unload", "セーフモード移行スピンアンロード"),
            ],
        ),
    ]

    for pid, ctx, q1, t1, q2, t2, chs in k6_defs:
        choices = [{"id": cid, "text": ctxt} for cid, ctxt in chs]
        pairs.append({
            "pair_id": f"rc3_blind5_dom_{pid}",
            "family": "domain_transfer",
            "k": 6,
            "case_1": {
                "id": f"rc3_blind5_dom_{pid}_s1",
                "group_id": f"rc3_blind5_dom_{pid}",
                "family": "domain_transfer",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1},
            },
            "case_2": {
                "id": f"rc3_blind5_dom_{pid}_s2",
                "group_id": f"rc3_blind5_dom_{pid}",
                "family": "domain_transfer",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2},
            },
        })

    return pairs
