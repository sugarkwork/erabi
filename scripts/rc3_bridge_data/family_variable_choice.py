"""Family 7: variable_choice (30 pairs, 60 cases) - RC3 Bridge Benchmark
Prefix: rc3b_var_
Distribution: K=2 (5 pairs), K=3 (5 pairs), K=4 (5 pairs), K=6 (5 pairs), K=8 (5 pairs), K=12 (5 pairs)
Focus: Systematic variability across choice cardinalities (K=2 to K=12) with realistic operational targets.
Zero leakage against all past datasets.
"""

from typing import Any, Dict, List, Tuple


def make_choices(c_defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in c_defs]


def get_variable_choice_pairs() -> List[Dict[str, Any]]:
    pairs: List[Dict[str, Any]] = []

    # --- K=2 (5 pairs: groups 01 to 05) ---
    k2_defs = [
        (
            "01",
            "超高圧送電線路の自動再閉路リレー（ARC）投入判定。判定条件は『無電圧確認時間1.0秒経過かつ対向端遮断完了』である。",
            "事故波形ログ：瞬時地絡故障除去後、無電圧時間1.2秒が経過し、対向端遮断完了信号を受信した。再閉路判定を行え。",
            "事故波形ログ：無電圧時間0.4秒時点で再発弧アークが検知され、対向端遮断信号は未着である。再閉路判定を行え。",
            [("arc_reclose_execute", "高速自動再閉路シーケンス投入実行"), ("arc_lockout_abort", "再閉路阻止・遮断器最終永久ロックアウト")],
            "arc_reclose_execute", "arc_lockout_abort"
        ),
        (
            "02",
            "船舶バラスト水処理システム（BWTS）のUV紫外線照射量基準。基準は『紫外線透過率UVT75%以上かつ有効照射線量400J/m2以上』である。",
            "処理ユニットモニタ：UVTは82%、実測照射線量は460J/m2である。港湾内バラスト水船外排出可否を判定せよ。",
            "処理ユニットモニタ：濁度上昇によりUVTは64%に低下、照射線量は310J/m2にとどまった。港湾内バラスト水船外排出可否を判定せよ。",
            [("bwts_discharge_permit", "バラスト水処理合格・港湾海域船外排出許可"), ("bwts_discharge_prohibit", "照射線量不足・船外排出禁止および船内再循環")],
            "bwts_discharge_permit", "bwts_discharge_prohibit"
        ),
        (
            "03",
            "高架鉄道橋の伸縮継手（エキスパンションジョイント）クリアランス管理。基準は『遊間隙間幅15mm以上80mm以内』である。",
            "季節点検計測：盛夏時のレール温度上昇下で実測遊間隙間は24mmを維持している。軌道健全性を判定せよ。",
            "季節点検計測：厳冬期のレール熱収縮により実測遊間隙間が94mmへ拡大開口した。軌道健全性を判定せよ。",
            [("expansion_joint_normal", "遊間寸法適正・通常列車運行継続承認"), ("expansion_joint_gap_alarm", "遊間過大逸脱・軌道徐行規制および継手調整")],
            "expansion_joint_normal", "expansion_joint_gap_alarm"
        ),
        (
            "04",
            "高炉水砕スラグ微粉末のブレーン比表面積基準。JIS規格は『比表面積4000cm2/g以上かつ強熱減量1.0%以下』である。",
            "粉末試験成績書：ブレーン比表面積は4350cm2/g、強熱減量は0.4%である。高炉セメント用骨材出荷判定を行え。",
            "粉末試験成績書：ブレーン比表面積は3620cm2/gにとどまり、強熱減量は1.8%を記録した。高炉セメント用骨材出荷判定を行え。",
            [("slag_cement_pass_ship", "JIS規格適合・高炉セメント用混合材出荷承認"), ("slag_cement_mill_regrind", "粉末度規格未達・ミル再粉砕工程回送")],
            "slag_cement_pass_ship", "slag_cement_mill_regrind"
        ),
        (
            "05",
            "光ファイバー海底ケーブル海底中継器（リピーター）の給電電流安定性基準。基準は『定電流給電偏差±10mA以内を常時維持』である。",
            "陸上給電端局PFE監視：主給電電流は公称1.000Aに対し1.004Aで極めて安定している。海底中継系運用を判定せよ。",
            "陸上給電端局PFE監視：海底地殻変動によるケーブル絶縁破壊で給電電流が0.850Aへ急落変動した。海底中継系運用を判定せよ。",
            [("subsea_repeater_power_ok", "給電電流定格安定・光信号増幅通信継続"), ("subsea_ground_fault_isolate", "海中地絡事故・給電電源緊急遮断探査モード移行")],
            "subsea_repeater_power_ok", "subsea_ground_fault_isolate"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k2_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_var_{gid}_s1",
                "group_id": f"rc3b_var_{gid}",
                "family": "variable_choice",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_var_{gid}_s2",
                "group_id": f"rc3b_var_{gid}",
                "family": "variable_choice",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2}
            }
        ])

    # --- K=3 (5 pairs: groups 06 to 10) ---
    k3_defs = [
        (
            "06",
            "下水管路埋設シールド推進工法の泥水加圧管理基準。基準は『切羽泥水圧が設計地下水圧+20kPa以上+50kPa以下』である。",
            "切羽水圧計モニタ：現在泥水圧は設計水圧+35kPaを保持している。推進ジャッキ運用を指示せよ。",
            "切羽水圧計モニタ：泥水圧が設計水圧-15kPaへ急落し、切羽崩壊の兆候が感知された。推進ジャッキ運用を指示せよ。",
            [("slurry_pressure_hold", "切羽圧適正・シールド推進定格続行"), ("slurry_emergency_charge", "切羽減圧危険・高濃度泥水緊急加圧注入"), ("slurry_bypass_drain", "送排泥パイプライン逆循環洗浄")],
            "slurry_pressure_hold", "slurry_emergency_charge"
        ),
        (
            "07",
            "大型変圧器絶縁油のフルフラール分析による絶縁紙経年劣化判定。基準は『油中フルフラール濃度0.1mg/L未満なら健全、0.1以上0.5未満なら要注意、0.5以上なら寿命限界』である。",
            "ガスクロ油分析報告：稼働25年変圧器の測定フルフラール濃度は0.04mg/Lであった。寿命診断を下せ。",
            "ガスクロ油分析報告：稼働35年変圧器の測定フルフラール濃度は0.78mg/Lを検出した。寿命診断を下せ。",
            [("transformer_life_healthy", "絶縁紙健全・通常インターバル定期点検継続"), ("transformer_life_critical", "セルロース重合度限界・変圧器更新計画策定"), ("transformer_life_watch", "劣化兆候検出・6ヶ月毎短縮油分析監視")],
            "transformer_life_healthy", "transformer_life_critical"
        ),
        (
            "08",
            "人工衛星のリアクションホイール脱飽和（アンローディング）運用基準。基準は『ホイール回転数定格85%到達時磁気トルカ通電脱飽和』である。",
            "姿勢制御AOCSログ：第2ホイールの回転数は定格の42%であり、蓄積角運動量は十分小さい。制御を指示せよ。",
            "姿勢制御AOCSログ：第2ホイールの回転数が定格の92%に達し、飽和速度限界に接近した。制御を指示せよ。",
            [("wheel_nominal_spin", "角運動量余裕内・ホイール通常姿勢制御維持"), ("wheel_desat_magnetic_torquer", "ホイール回転数飽和・磁気トルカ励磁脱飽和実行"), ("wheel_thruster_emergency_dump", "スラスター強制パルス緊急ダンプ")],
            "wheel_nominal_spin", "wheel_desat_magnetic_torquer"
        ),
        (
            "09",
            "コンクリートダム堤体の揚圧力（アップリフト）観測基準。基準は『基礎排水孔間隙水圧が設計許容水頭の60%以下』である。",
            "堤体埋設ピエゾメータ：実測揚水頭は設計許容値の38%を示している。ダム保安判定を行え。",
            "堤体埋設ピエゾメータ：集中豪雨により実測揚水頭が設計許容値の82%へ跳ね上がった。ダム保安判定を行え。",
            [("dam_uplift_sound", "基礎揚圧力安全域・堤体安定性合格確認"), ("dam_drain_drill_relief", "揚圧力異常上昇・基礎排水孔緊急再削孔洗浄"), ("dam_grout_curtain_reseal", "グラウトカーテン高圧セメント再注入")],
            "dam_uplift_sound", "dam_drain_drill_relief"
        ),
        (
            "10",
            "半導体パッケージングのワイヤーボンディング接合強度基準。基準は『金線プル強度8.0gf以上かつステッチネック破断率90%以上』である。",
            "自動破壊プルテスター：ロット抜取サンプルの平均プル強度は11.5gf、破断モードは全てステッチネック部破断であった。工程判定を下せ。",
            "自動破壊プルテスター：平均プル強度は4.2gfに低下、破断の80%がパッド界面リフト（剥離）であった。工程判定を下せ。",
            [("wire_bond_lot_accept", "接合強度規格合格・樹脂封止トランスファモールド移送"), ("wire_bond_lift_reject", "界面密着不全不合格・キャピラリ交換および超音波出力再校正"), ("wire_bond_pad_clean", "プラズマクリーニング再照射")],
            "wire_bond_lot_accept", "wire_bond_lift_reject"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k3_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_var_{gid}_s1",
                "group_id": f"rc3b_var_{gid}",
                "family": "variable_choice",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_var_{gid}_s2",
                "group_id": f"rc3b_var_{gid}",
                "family": "variable_choice",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2}
            }
        ])

    # --- K=4 (5 pairs: groups 11 to 15) ---
    k4_defs = [
        (
            "11",
            "石油コンビナートの浮屋根式原油タンクのシール部点検基準。基準は『リムシール間隙寸法30mm以上150mm以下かつ気相部可燃性炭化水素ガス濃度LEL10%以下』である。",
            "タンク点検記録：実測リムシール間隙は85mm、ガス濃度はLEL2.1%である。タンク運用判定を行え。",
            "タンク点検記録：実測リムシール間隙が210mmへ局部拡大し、ガス濃度はLEL45%へ漏出急増した。タンク運用判定を行え。",
            [("tank_rim_seal_pass", "シール健全・原油受払配管運用継続承認"), ("tank_rim_seal_fault_alert", "シール破損ガス漏出・緊急フォーム泡消火待機および補修"), ("tank_roof_drain_clear", "浮屋根雨水ドレン管水抜き弁開"), ("tank_mixer_swivel_rotate", "タンク底部スラッジ攪拌ミキサー起動")],
            "tank_rim_seal_pass", "tank_rim_seal_fault_alert"
        ),
        (
            "12",
            "火力発電所排煙脱硫装置（FGD）の石灰石スラリー循環pH基準。基準は『吸収塔抜出pH5.2以上5.8以下かつ石膏結晶酸化率98%以上』である。",
            "化学分析計データ：スラリーpHは5.45、石膏酸化率は99.2%である。脱硫スラリー運用を決定せよ。",
            "化学分析計データ：スラリーpHは4.10へ急減酸性化、石膏酸化率は82%へ悪化した。脱硫スラリー運用を決定せよ。",
            [("fgd_slurry_ph_nominal", "脱硫吸収反応適正・石灰石フィード定格維持"), ("fgd_limestone_boost_inject", "吸収液酸性化・炭酸カルシウムスラリー急速増量"), ("fgd_oxidation_air_blower", "酸化空気ブロワ吐出風量増圧"), ("fgd_gypsum_centrifuge_dewater", "石膏脱水遠心分離機ケーキ回収")],
            "fgd_slurry_ph_nominal", "fgd_limestone_boost_inject"
        ),
        (
            "13",
            "高精度CNC円筒研削盤の工作物真円度・円筒度基準。基準は『外径真円度公差0.8μm以内かつ表面うねり波長1mm未満』である。",
            "三次元測定機レポート：測定真円度は0.45μm、表面うねりは検出限界未満である。加工ワーク判定を行え。",
            "三次元測定機レポート：砥石アンバランスにより測定真円度は2.6μmへ真円崩れを記録した。加工ワーク判定を行え。",
            [("grind_part_dimension_accept", "幾何公差高精度合格・最終検査洗浄ライン移送"), ("grind_wheel_truing_rebalance", "真円度不良・ロータリーダイヤモンドドレッサ目立て修正"), ("grind_tailstock_thrust_adjust", "心押台押しコップ圧力再調整"), ("grind_coolant_chiller_service", "研削液クーラントクーラー温度管理")],
            "grind_part_dimension_accept", "grind_wheel_truing_rebalance"
        ),
        (
            "14",
            "産業用大型リチウムイオン蓄電池コンテナの温度均一性基準。基準は『コンテナ内全セル温度差ΔTが3.0℃以内かつ最高セル温度35.0℃以下』である。",
            "BMS温度マトリクス：最高セル温度は28.4℃、最大温度偏差ΔTは1.6℃である。充放電サイクル運用を決定せよ。",
            "BMS温度マトリクス：モジュール奥側の一部セルが42.5℃へ発熱、全体ΔTは9.8℃へ拡大した。充放電サイクル運用を決定せよ。",
            [("bess_container_charge_proceed", "セル温度均一冷却適合・系統連系充電充当"), ("bess_thermal_runaway_derate", "局所熱集中危険・インバータ出力半減および空調ファン最大稼働"), ("bess_coolant_glycol_loop_vent", "液冷配管冷却液エア抜き"), ("bess_insulation_resistance_tare", "直流対地絶縁抵抗メガ測定")],
            "bess_container_charge_proceed", "bess_thermal_runaway_derate"
        ),
        (
            "15",
            "鉄道車両車輪のフランジ摩耗・踏面き裂検査基準。基準は『フランジ厚さ22mm以上かつ踏面フレーキング剥離深さ1.0mm以下』である。",
            "車輪形状測定レーザー：フランジ厚は26.4mm、踏面に剥離損傷は皆無である。車両運用判定を行え。",
            "車輪形状測定レーザー：フランジ厚が19.5mmへ限界摩耗、踏面には深さ2.5mmの熱き裂が認められた。車両運用判定を行え。",
            [("wheelset_service_pass", "車輪幾何形状適合・次期仕業検査まで本線運用"), ("wheelset_underfloor_lathe_cut", "フランジ限界摩耗・車輪転削盤削正加工回送"), ("wheelset_acoustic_bearing_diag", "車軸軸受音響異常振動診断"), ("wheelset_brake_shoe_replace", "合成制輪子シュー交換")],
            "wheelset_service_pass", "wheelset_underfloor_lathe_cut"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k4_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_var_{gid}_s1",
                "group_id": f"rc3b_var_{gid}",
                "family": "variable_choice",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_var_{gid}_s2",
                "group_id": f"rc3b_var_{gid}",
                "family": "variable_choice",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2}
            }
        ])

    # --- K=6 (5 pairs: groups 16 to 20) ---
    k6_defs = [
        (
            "16",
            "風力発電機ナセル内ドライブトレイン振動診断基準。ISO基準は『主軸受振動速度RMSが2.8mm/s以下かつ遊星ギヤ噛合周波数側帯波ピーク1.0G以下』である。",
            "状態監視CMSレポート：軸受振動RMSは1.3mm/s、側帯波ピークは0.32Gである。風力タービン運用を指示せよ。",
            "状態監視CMSレポート：軸受振動RMSは4.9mm/sへ跳ね上がり、遊星歯車内歯車の歯面剥離を示す側帯波が2.4Gを記録した。風力タービン運用を指示せよ。",
            [("wind_turbine_generate_ok", "ドライブトレイン機械健全・定格風速発電継続"), ("wind_gearbox_service_trip", "ギヤボックス歯面破損・ナセル緊急トリップ停止点検"), ("wind_generator_slipring_clean", "誘導発電機スリップリングカーボン清掃"), ("wind_yaw_brake_lining_check", "ヨーブレーキパッド摩耗ライニング検査"), ("wind_oil_filter_differential", "増速機潤滑油フィルター差圧エレメント交換"), ("wind_blade_pitch_cal_zero", "ブレード可変ピッチ角度エンコーダ原点校正")],
            "wind_turbine_generate_ok", "wind_gearbox_service_trip"
        ),
        (
            "17",
            "製薬用粉体気流乾燥機（フラッシュドライヤー）の爆発防護基準。基準は『乾燥管内粉塵濃度MEC以下維持かつ消火火花検知器応答時間10ms以内』である。",
            "防爆計装テレメトリ：粉塵濃度は爆発下限界の30%、光学火花検知器は健全（0）である。乾燥工程を決定せよ。",
            "防爆計装テレメトリ：乾燥管下流にて赤外線火花検知器が火花発光を感知した。爆発抑制処置を決定せよ。",
            [("dryer_powder_feed_run", "防爆環境適合・原薬粉体連続投入乾燥続行"), ("dryer_explosion_suppression_fire", "火花検知・消火剤高速キャニスター即時爆破噴射"), ("dryer_bag_filter_reverse_pulse", "集塵バグフィルター逆洗パルスエア打込み"), ("dryer_hot_air_temperature_tune", "熱風発生炉バーナー供給熱風調温"), ("dryer_rotary_valve_speed_adj", "ロータリーバルブ排出回転数調整"), ("dryer_inert_n2_flow_monitor", "不活性化窒素パージ流量モニタ確認")],
            "dryer_powder_feed_run", "dryer_explosion_suppression_fire"
        ),
        (
            "18",
            "高分子化学における重合反応熱除去ループ制御。基準は『ジャケット冷却水温度差ΔTが8.0℃以内かつ反応液粘度上昇率20%/h以内』である。",
            "DCSプロセス監視：冷却水ΔTは5.1℃、重合粘度上昇率は12%/hである。重合釜運用を決定せよ。",
            "DCSプロセス監視：重合熱の除熱が追いつかずΔTは14.2℃へ激増、重合液粘度は毎時65%で暴走硬化を始めた。重合釜運用を決定せよ。",
            [("polymer_polymerization_continue", "除熱安定・単量体モノマー定率連続重合"), ("polymer_thermal_runaway_quench", "重合暴走危険・重合禁止剤緊急重合停止注入"), ("polymer_agitator_dual_speed", "撹拌機回転数トルク追従インバータ切替"), ("polymer_reflux_condenser_vent", "還流冷却器凝縮液戻し弁開度調整"), ("polymer_initiator_pump_prime", "重合開始剤微量定量ポンプエア抜き"), ("polymer_jacket_steam_warm", "反応開始ジャケット温水循環加熱")],
            "polymer_polymerization_continue", "polymer_thermal_runaway_quench"
        ),
        (
            "19",
            "都市ガス導管網のSNG（合成天然ガス）熱量・ウォッベ指数（WI）調整基準。供給基準は『ウォッベ指数52.5以上54.0以下かつ燃焼速度MCP35以上40以下』である。",
            "熱量カロリー計測定：測定WIは53.2、MCPは37.5である。導管網送出弁制御を決定せよ。",
            "熱量カロリー計測定：測定WIは50.8へ基準割れ、MCPは31.2へ低下した。導管網送出弁制御を決定せよ。",
            [("gas_grid_sendout_nominal", "燃焼熱量性状適合・都市ガス幹線高圧送出承認"), ("gas_lpg_enrichment_boost", "熱量不足・高カロリーLPG増熱混合比率引き上げ"), ("gas_air_dilution_compress", "過熱量是正・空気希釈コンプレッサ注入"), ("gas_odorant_injection_tare", "付臭剤THT/TBM微量滴下比率確認"), ("gas_filter_separator_drain", "ガスフィルターセパレーター凝縮水ドレン"), ("gas_governor_pressure_tune", "地区整圧器ガバナー二次側供給圧整定")],
            "gas_grid_sendout_nominal", "gas_lpg_enrichment_boost"
        ),
        (
            "20",
            "大規模下水処理場の消化ガス発電（バイオガス）脱硫脱湿基準。基準は『硫化水素H2S濃度50ppm以下かつ相対湿度40%以下（シロキサン吸着前）』である。",
            "ガス精製分析計：H2S濃度は18ppm、脱湿後相対湿度は28%である。ガスエンジン発電機運用を決定せよ。",
            "ガス精製分析計：脱硫塔破過によりH2S濃度は240ppmへ急増、相対湿度は75%へ結露過湿となった。ガスエンジン発電機運用を決定せよ。",
            [("biogas_genset_run_grid", "バイオガス精製良好・全量ガスエンジン売電発電"), ("biogas_desulf_breakthrough_trip", "脱硫剤破過・エンジン吸気遮断およびバイオガスフレア放散"), ("biogas_siloxane_filter_swap", "シロキサン活性炭吸着塔切替"), ("biogas_chiller_drain_trap", "ガス冷却チラー凝縮水自動トラップブロー"), ("biogas_holder_seal_water_top", "有水式ホルダー水封水位自動給水"), ("biogas_digester_sludge_mix", "嫌気性消化槽汚泥循環撹拌ポンプ運転")],
            "biogas_genset_run_grid", "biogas_desulf_breakthrough_trip"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k6_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_var_{gid}_s1",
                "group_id": f"rc3b_var_{gid}",
                "family": "variable_choice",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_var_{gid}_s2",
                "group_id": f"rc3b_var_{gid}",
                "family": "variable_choice",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2}
            }
        ])

    # --- K=8 (5 pairs: groups 21 to 25) ---
    k8_defs = [
        (
            "21",
            "発電用大型蒸気タービンの軸受メタルトリップ基準。基準は『全ジャーナル軸受温度105℃以下かつスラスト軸受摩耗変位±0.5mm以内』である。",
            "タービン監視計装：全ジャーナル温度は84〜92℃、スラスト変位は+0.12mmである。タービン運用を指示せよ。",
            "タービン監視計装：第3ジャーナル軸受温度が118℃へ急上昇、スラスト変位は-0.85mmを記録した。タービン運用を指示せよ。",
            [("steam_turbine_full_load", "軸受温度変位正常・主蒸気弁全開定格発電継続"), ("steam_turbine_trip_estop", "軸受メタル過熱摩耗・主蒸気止め弁緊急トリップ遮断"), ("steam_turbine_turning_gear", "タービン停止後ターニングギア電動旋回"), ("steam_turbine_jacking_oil", "起動時ローター浮上油圧ジャッキングポンプ"), ("steam_turbine_gland_steam", "軸封グランド蒸気復水器抽気弁調整"), ("steam_turbine_vacuum_breaker", "復水器真空破壊弁緊急開放"), ("steam_turbine_exhaust_hood_spray", "低圧車室排気室温度過熱防止スプレー弁"), ("steam_turbine_bleed_heater", "給水加熱器抽気逆止弁動作テスト")],
            "steam_turbine_full_load", "steam_turbine_trip_estop"
        ),
        (
            "22",
            "半導体クリーンルームのケミカル汚染（AMC）モニタリング基準。基準は『気中アンモニア濃度1.0ppb以下かつ酸性ガス濃度0.5ppb以下』である。",
            "IMS（イオン移動度分光）計器：アンモニア濃度は0.35ppb、酸性ガスは0.12ppbである。露光工程運用を決定せよ。",
            "IMS（イオン移動度分光）計器：隣接薬液交換時の漏出によりアンモニアが8.4ppbへ急増した。露光工程運用を決定せよ。",
            [("amc_clean_exposure_proceed", "AMC清浄度適合・最先端リソグラフィ露光工程続行"), ("amc_ammonia_filter_boost", "アンモニア汚染検知・ケミカルフィルター循環風量最大加速"), ("amc_foop_nitrogen_purge", "FOOPカセット高純度窒素自動置換"), ("amc_air_washer_water_swap", "外気処理空調機エアワッシャー純水更新"), ("amc_ion_chromato_recal", "イオンクロマトグラフィーオンライン校正"), ("amc_cleanroom_intake_shut", "外気取込ダンパー全閉完全循環モード切替"), ("amc_organic_carbon_bake", "活性炭フィルターVOC脱着ベーキング"), ("amc_wafer_reject_clean", "表面汚染ウェハ再洗浄ライン排出")],
            "amc_clean_exposure_proceed", "amc_ammonia_filter_boost"
        ),
        (
            "23",
            "航空機燃料補給ラインのサージリリーフおよび静電気安全基準。基準は『給油ノズル流量1200L/min以下かつ静電気電位100V以下』である。",
            "給油ハイドラント計装：給油流量は1150L/min、実測静電気電位は24Vである。ジェット燃料給油を指示せよ。",
            "給油ハイドラント計装：燃料ポンプ急動により給油圧力脈動サージが発生、電位が450Vへ帯電増大した。ジェット燃料給油を指示せよ。",
            [("aviation_refuel_proceed_nominal", "流速電位適合・主翼燃料タンク給油続行"), ("aviation_refuel_emergency_shutoff", "サージ帯電危険・ハイドラント緊急遮断弁（EFSO）作動"), ("aviation_fuel_defuel_reverse", "給油ノズル逆送デフューエリング排出"), ("aviation_fuel_sample_clear_bright", "燃料水分沈殿サンプリング目視確認"), ("aviation_bonding_cable_recheck", "静電気ボンディング接地クランプ再導通確認"), ("aviation_fuel_coalescer_drain", "水分離フィルターコアレッサー自動ドレン"), ("aviation_fuel_density_meter", "ジェット燃料密度計比重確認"), ("aviation_fuel_additive_anti_ice", "防氷添加剤FSII濃度検定")],
            "aviation_refuel_proceed_nominal", "aviation_refuel_emergency_shutoff"
        ),
        (
            "24",
            "製鉄所連続焼鈍ライン（CAL）の炉内還元雰囲気ガス制御。基準は『水素濃度3.0%以上7.0%以下（残部窒素）かつ露点-40℃以下』である。",
            "炉気分析計テレメトリ：H2濃度は5.2%、露点は-48℃である。鋼板連続焼鈍通板を決定せよ。",
            "炉気分析計テレメトリ：大気漏入によりH2濃度は1.8%へ希薄化、露点は-15℃へ多湿酸化した。鋼板連続焼鈍通板を決定せよ。",
            [("cal_furnace_atmosphere_pass", "還元雰囲気適合・自動車用高張力鋼板連続焼鈍"), ("cal_furnace_h2_boost_purge", "露点悪化酸化危険・高純度H2/N2緊急パージ増量"), ("cal_furnace_roll_seal_adjust", "入側ハースロールガスシールボックス調整"), ("cal_furnace_radiant_tube_gas", "ラジアントチューブバーナー燃焼排気点検"), ("cal_furnace_dew_point_zero_cal", "酸化ジルコニア露点計ゼロスパン校正"), ("cal_furnace_tension_bridle_sync", "ブライドルロール張力速度同期補正"), ("cal_furnace_water_quench_dip", "水焼入れタンク循環冷却水温調整"), ("cal_furnace_snout_dross_clean", "スナウト溶融亜鉛ドロス自動掻き取り")],
            "cal_furnace_atmosphere_pass", "cal_furnace_h2_boost_purge"
        ),
        (
            "25",
            "大規模上水道導水トンネルの自然流下動水勾配基準。基準は『トンネル内流速1.0m/s以上2.5m/s以下かつ管頂空間率15%以上』である。",
            "水理テレメトリ観測：実測流速は1.65m/s、管頂空間率は22%である。導水ゲート運用を指示せよ。",
            "水理テレメトリ観測：流速は0.62m/sへ泥砂沈降失速、上流ダム放水により空間率は2%へ満管水没寸前となった。導水ゲート運用を指示せよ。",
            [("water_tunnel_flow_nominal", "自然流下適正・取水調整ゲート現行開度維持"), ("water_tunnel_sluice_gate_throttle", "満管越流流速失速・取水口制水ゲート急速絞り込み"), ("water_tunnel_sediment_flush", "排砂管サンドフラッシュゲート開放"), ("water_tunnel_air_vent_shaft", "空気抜き立坑通気吸気状態目視点検"), ("water_tunnel_turbidity_sonar", "濁度音響プロファイラ自動測定"), ("water_tunnel_trash_rack_rake", "除塵スクリーン自動除塵機連続運転"), ("water_tunnel_chlorine_pre_dosing", "原水塩素前処理注入ポンプ比率調整"), ("water_tunnel_fish_screen_return", "迷入魚類バイパス魚道誘導")],
            "water_tunnel_flow_nominal", "water_tunnel_sluice_gate_throttle"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k8_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_var_{gid}_s1",
                "group_id": f"rc3b_var_{gid}",
                "family": "variable_choice",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_var_{gid}_s2",
                "group_id": f"rc3b_var_{gid}",
                "family": "variable_choice",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2}
            }
        ])

    # --- K=12 (5 pairs: groups 26 to 30) ---
    k12_defs = [
        (
            "26",
            "無人自動運転フォークリフト（AGV）のSLAMレーザー誘導ステータス判定。障害物・バッテリー・測位・積荷の12状態を識別する。",
            "SLAMコントローラログ：全方位LiDARによる反射柱自己位置同定信頼度が98%、走行経路クリア、荷役パレット満載正常。走行制御を決定せよ。",
            "SLAMコントローラログ：走行経路上前方1.2mに作業員が急停止、超音波・LiDARの両方で安全停止停止ゾーン侵入がトリガーされた。走行制御を決定せよ。",
            [
                ("agv_state_cruise_nominal", "正常SLAM自己位置同定・定格速度自動走行"),
                ("agv_state_safety_stop_obstruction", "安全停止ゾーン侵入・自動ブレーキ即時停止"),
                ("agv_state_battery_low_return", "バッテリー低下・自律充電ステーション帰還"),
                ("agv_state_lost_localization", "自己位置見失い・低速旋回リロカリゼーション"),
                ("agv_state_pallet_misalign", "パレット荷崩れ傾斜・フォーク昇降停止待機"),
                ("agv_state_interlock_door_wait", "自動シャッター開扉待ち・一時停止待機"),
                ("agv_state_traffic_yield", "交差点優先車両通過待ち・一時停止待機"),
                ("agv_state_manual_override_mode", "手動ペンダント操作切替・自律制御解除"),
                ("agv_state_fork_height_cal", "フォーク高さエンコーダキャリブレーション"),
                ("agv_state_bumper_contact_estop", "メカニカルバンパー接触・非常停止ラッチ"),
                ("agv_state_floor_slip_detect", "車輪スリップ空転・トラクションコントロール"),
                ("agv_state_fleet_replan_route", "上位管制サーバー通信経路再割り当て待機")
            ],
            "agv_state_cruise_nominal", "agv_state_safety_stop_obstruction"
        ),
        (
            "27",
            "スマートメーター電力消費プロファイル解析における需要家家電動作分類。リアルタイム高周波電流波形から負荷機器を特定する。",
            "電流シグネチャ分析：電源投入時に数十アンペアの誘導性突入電流が発生し、力率0.75でインバータ駆動圧縮機が連続回転している。動作機器を選定せよ。",
            "電流シグネチャ分析：力率がほぼ1.0（純抵抗負荷）であり、1200Wの一定電力がサーモスタット周期で矩形波状にON/OFFしている。動作機器を選定せよ。",
            [
                ("appliance_heat_pump_ac", "ヒートポンプエアコン（インバータ駆動圧縮機）"),
                ("appliance_pure_resistive_heater", "電熱シーズヒーター（電気ストーブ・トースター純抵抗）"),
                ("appliance_induction_cooktop", "電磁調理器（IH高周波インバータ共振負荷）"),
                ("appliance_microwave_magnetron", "電子レンジ（高圧トランス・マグネトロンパルス負荷）"),
                ("appliance_refrigerator_cycle", "小型家庭用冷蔵庫（レシプロコンプレッサー周期）"),
                ("appliance_washing_machine_blldc", "ドラム式洗濯機（BLDCブラシレスモーター加減速）"),
                ("appliance_led_lighting_smps", "LED照明器具群（力率改善アクティブPFCスイッチング電源）"),
                ("appliance_pc_server_switching", "デスクトップPC電源（キャパシタ入力型整流平滑電源）"),
                ("appliance_vacuum_cleaner_universal", "掃除機（高速ユニバーサル整流子モーター負荷）"),
                ("appliance_ev_charger_level2", "電気自動車普通充電器（200V単相PWM制御大電力充電）"),
                ("appliance_water_heater_storage", "電気温水器（大容量貯湯タンク深夜電力ヒーター）"),
                ("appliance_solar_inverter_backfeed", "住宅用太陽光発電パワーコンディショナ（系統逆潮流）")
            ],
            "appliance_heat_pump_ac", "appliance_pure_resistive_heater"
        ),
        (
            "28",
            "海洋音響ソナー信号処理における水中音源類別。周波数スペクトル、ロファグラム（LOFAR）、復調音（DEMON）から音源を判定する。",
            "音響スペクトル解析：キャビテーション雑音は皆無であり、極めて規則的な60Hz電源高調波と4枚羽根プロペラ軸回転数（120rpm）の基本線スペクトルが明瞭に観測された。音源を類別せよ。",
            "音響スペクトル解析：20kHzから100kHzにわたる高周波超音波クリック音列が数十ミリ秒間隔で規則的に反復探査されている。音源を類別せよ。",
            [
                ("sonar_submarine_electric_shaft", "原子力潜水艦推進軸音（低速単軸スキュードプロペラ）"),
                ("sonar_cetacean_echolocating", "ハクジラ類生体エコーロケーション（高周波クリック音）"),
                ("sonar_commercial_container_vessel", "大型コンテナ商船（高速大出力プロペラキャビテーション）"),
                ("sonar_fishing_trawler_winch", "漁船トロール網巻上げ油圧ウインチ音"),
                ("sonar_seismic_airgun_survey", "海洋地質探査エアガン音響パルス衝撃波"),
                ("sonar_torpedo_high_speed_turbine", "魚雷用高速蒸気・ガスタービン推進器音"),
                ("sonar_active_dipping_sonar_ping", "対潜ヘリコプター吊下式アクティブソナーピン音"),
                ("sonar_underwater_volcano_tremor", "海底火山性微動・マグマ破砕低周波音"),
                ("sonar_iceberg_calving_crush", "氷山分離崩壊・海氷破砕スクラッチ音"),
                ("sonar_surface_breaking_waves", "海面波浪崩壊広帯域バックグラウンドノイズ"),
                ("sonar_offshore_pile_driving", "洋上風力発電基礎杭打撃ハンマー衝撃波"),
                ("sonar_diver_scuba_regulator", "スクーバダイバー呼吸レギュレーター排気気泡音")
            ],
            "sonar_submarine_electric_shaft", "sonar_cetacean_echolocating"
        ),
        (
            "29",
            "製薬クリーンルーム空調設備におけるHEPA/ULPAフィルター捕集機構選定。粒子径と空気流速に応じた物理的分離メカニズムを特定する。",
            "物理捕集機構：粒子径が0.1μm以下の極微小ナノ粒子が、気体分子との衝突によるブラウン運動で激しくジグザグ拡散し、フィルター繊維表面に接触捕集される主メカニズム。機構名を選べ。",
            "物理捕集機構：粒子径が1.0μm以上の大粒子が、空気流線の急激な曲がりに追従できず、自らの運動慣性によって流線を離脱して繊維に衝突する主メカニズム。機構名を選べ。",
            [
                ("hepa_diffusional_brownian", "ブラウン拡散効果（0.1μm以下極微小粒子拡散捕集）"),
                ("hepa_inertial_impaction", "慣性衝突効果（1.0μm以上大質量粒子慣性捕集）"),
                ("hepa_interception_streamline", "直接遮断効果（気流線上粒径幾何学的接触捕集）"),
                ("hepa_electrostatic_attraction", "静電引力効果（エレクトレット荷電繊維クーロン力）"),
                ("hepa_gravitational_settling", "重力沈降効果（低流速下大粒子自重落下）"),
                ("hepa_sieving_mechanical_screen", "ふるい分け効果（繊維間隙より大きい粗大粒子通過阻止）"),
                ("hepa_thermophoresis_gradient", "熱泳動効果（温度勾配による低温側熱移動沈着）"),
                ("hepa_diffusiophoresis_vapor", "拡散泳動効果（水蒸気濃度勾配同伴沈着）"),
                ("hepa_coagulation_agglomerate", "音波凝集効果（高音圧下粒子相互衝突合体）"),
                ("hepa_turbulent_deposition", "乱流沈着効果（ダクト内渦剥離による壁面沈着）"),
                ("hepa_van_der_waals_adhesion", "ファンデルワールス分子間力（繊維表面接触後固着）"),
                ("hepa_capillary_liquid_bridge", "毛管凝縮液架橋効果（高湿度多孔質微小液橋結合）")
            ],
            "hepa_diffusional_brownian", "hepa_inertial_impaction"
        ),
        (
            "30",
            "石油精製触媒接触分解装置（FCC）のプロセス異常診断。圧力バランス、触媒循環、再生塔熱収支の12状態を分類する。",
            "計装診断データ：反応器-再生塔間の差圧が逆転し、酸素を含む高温再生排ガスが炭化水素を含む反応器側へ逆流する極めて危険な現象が感知された。異常事象を選定せよ。",
            "計装診断データ：原料油中のニッケル・バナジウム等の重金属汚染によりゼオライト触媒活性点が被毒され、水素およびコークの生成量が異常増大した。異常事象を選定せよ。",
            [
                ("fcc_reversal_pressure_flow", "差圧逆転（スラントスライド弁逆流・爆発危険）"),
                ("fcc_heavy_metal_poisoning", "重金属触媒被毒（Ni/V沈着・過剰脱水素コーク生成）"),
                ("fcc_afterburning_regenerator", "アフターバーニング（再生塔希薄相後燃焼過熱）"),
                ("fcc_catalyst_attrition_loss", "触媒微粉化損耗（サイクロン摩耗・排煙触媒飛散）"),
                ("fcc_feed_nozzle_plugging", "原料油噴射ノズルコーキング閉塞（噴霧不良）"),
                ("fcc_main_column_flooding", "主分留塔フラッディング（気液負荷過剰棚段溢水）"),
                ("fcc_wet_gas_compressor_surge", "ウェットガスコプレッサーサージング（吸込流量低下）"),
                ("fcc_slide_valve_erosion", "スライド弁弁体エロージョン摩耗（触媒高速噴流壊食）"),
                ("fcc_stripper_steam_channeling", "ストリッパー蒸気チャンネリング（脱離不良炭化水素同伴）"),
                ("fcc_air_blower_trip_fail", "主燃焼空気ブロワトリップ（再生塔酸素供給喪失）"),
                ("fcc_spent_catalyst_bridging", "使用済み触媒スタンドパイプブリッジング（循環停止）"),
                ("fcc_slurry_heat_exchanger_foul", "スラリーオイル熱交換器ファウリング目詰まり")
            ],
            "fcc_reversal_pressure_flow", "fcc_heavy_metal_poisoning"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k12_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_var_{gid}_s1",
                "group_id": f"rc3b_var_{gid}",
                "family": "variable_choice",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_var_{gid}_s2",
                "group_id": f"rc3b_var_{gid}",
                "family": "variable_choice",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2}
            }
        ])

    return pairs
