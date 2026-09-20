"""Family 5: domain_transfer (30 pairs, 60 cases) - Blind v4
Distribution: K=3 (5 pairs), K=4 (10 pairs), K=6 (5 pairs), K=8 (5 pairs), K=12 (5 pairs)
Prefix: rc2b4_dom_
Zero inference during authoring; 100% fresh scenarios.
Concise choice texts for K=12 to guarantee strict token count <= 350.
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
            "陽子線がん治療用シンクロトロン加速器の照射管理：『規定：腫瘍深部ブラッグピーク位置と照射エネルギーが整合し、アイソセンター線量率が許容誤差±1.0%以内ならビーム照射ゲート開放、それ以外はビームゲーティング阻止』とする。",
            "線量モニタ実測値：照射エネルギー215MeV、アイソセンター線量率誤差+0.3%で合致。照射制御を指示せよ。",
            "線量モニタ実測値：高周波キャビティ位相乱れによりエネルギーが180MeVに偏位し、線量率誤差-4.2%となった。照射制御を指示せよ。",
            [
                ("proton_beam_gate_open", "陽子線ビーム照射ゲート開放"),
                ("proton_beam_gate_block", "照射阻止・ビームダンプ偏向"),
                ("synchrotron_magnet_reset", "主電磁石励磁リセット")
            ],
            "proton_beam_gate_open", "proton_beam_gate_block"
        ),
        (
            "02",
            "希釈冷凍機クライオスタットにおける超伝導量子ビット冷却制御：『規定：ミキシングチャンバー温度が15mK以下に到達した場合は量子演算シーケンス開始、25mKを超過した場合は熱雑音デコヒーレンス防止のため演算保留』とする。",
            "ルテニウム酸化物温度計：現在ミキシングチャンバー温度は11.8mKを示している。量子プロセッサ制御を決定せよ。",
            "ルテニウム酸化物温度計：循環冷媒ガス不純物混入により温度が34.0mKまで悪化した。量子プロセッサ制御を決定せよ。",
            [
                ("qubit_quantum_gate_run", "量子ゲート演算シーケンス実行"),
                ("qubit_decoherence_hold", "量子演算保留・極低温再凝縮待機"),
                ("cryo_gas_dump_reservoir", "冷媒混合ガス緊急貯蔵タンク回収")
            ],
            "qubit_quantum_gate_run", "qubit_decoherence_hold"
        ),
        (
            "03",
            "放射性医薬品（18F-FDG）自動合成モジュールの検品出荷基準：『規定：放射化学的純度が95%以上かつ崩壊補正後放射能濃度が所定規格を満たす場合は医療機関出荷承認、純度未達は全量廃棄』とする。",
            "HPLCラジオアイソトープ検出器：放射化学的純度98.6%、エンドトキシン陰性、比放射能規格適合を確認。判定せよ。",
            "HPLCラジオアイソトープ検出器：未反応遊離フッ化物イオンが残存し、放射化学的純度は88.2%にとどまった。判定せよ。",
            [
                ("pet_drug_ship_approved", "放射性薬剤出荷搬送承認"),
                ("pet_drug_scrap_disposal", "規格未達ロット全量減衰廃棄"),
                ("cyclotron_target_flush", "サイクロトロン照射ターゲット洗浄")
            ],
            "pet_drug_ship_approved", "pet_drug_scrap_disposal"
        ),
        (
            "04",
            "深宇宙探査機の恒星天測スタートラッカー姿勢制御：『規定：CCD視野内の3基以上の目標ガイド星が星表カタログと合致同定された場合は星姿勢三軸高精度ロックを確立、同定不能時は太陽センサ粗姿勢維持へフォールバック』とする。",
            "星同定プロセッサ：視野内の5個の主要恒星が星表と完全合致し、姿勢決定誤差0.001度を達成した。姿勢制御を決定せよ。",
            "星同定プロセッサ：高エネルギー銀河宇宙線ノイズにより星像パターン照合が失敗し、同定星数は0個となった。姿勢制御を決定せよ。",
            [
                ("attitude_star_lock_high", "スタートラッカー三軸高精度ロック確立"),
                ("attitude_sun_sensor_coarse", "粗姿勢フォールバック・太陽指向維持"),
                ("attitude_reaction_wheel_dump", "リアクションホイール角運動量脱飽和")
            ],
            "attitude_star_lock_high", "attitude_sun_sensor_coarse"
        ),
        (
            "05",
            "トカマク型核融合実験炉の高ベータプラズマ平衡制御：『規定：ポロイダル磁場コイル群によりプラズマ位置垂直変位が±10mm以内に維持されている場合は加熱中性粒子入射（NBI）継続、変位30mm超過時はディスラプション防止キルペレット打ち込み』とする。",
            "磁気プローブ・プラズマ診断：垂直位置ずれは+2.5mmで安定した磁気面を形成している。炉制御を指示せよ。",
            "磁気プローブ・プラズマ診断：プラズマ垂直変位が急激に+42mmに達し、垂直不安定性（VDE）の暴走が検出された。炉制御を指示せよ。",
            [
                ("plasma_nbi_heating_keep", "中性粒子入射NBI加熱定常継続"),
                ("plasma_kill_pellet_inject", "ディスラプション回避不活性ガス急冷ペレット注入"),
                ("plasma_divertor_water_drain", "ダイバータ冷却水緊急ドレン")
            ],
            "plasma_nbi_heating_keep", "plasma_kill_pellet_inject"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k3_defs:
        pairs.append({
            "id": f"rc2b4_dom_{gid}_s1", "group_id": f"rc2b4_dom_{gid}", "family": "domain_transfer",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_dom_{gid}_s2", "group_id": f"rc2b4_dom_{gid}", "family": "domain_transfer",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=4 (10 pairs: groups 06 to 15) ---
    k4_defs = [
        (
            "06",
            "極端紫外線（EUV）露光用スズプラズマ光源の射出制御：『規定：CO2高出力レーザーがスズ液滴へ直撃し波長13.5nmのEUV光スペクトル強度が規定閾値以上なら露光チャンバーシャッター開放、ターゲットミス時は照射中断』とする。",
            "分光光度計モニタ：13.5nmにおけるインバンド変換効率は4.2%に達し極めて強い発光を検出した。光源制御を選択せよ。",
            "分光光度計モニタ：スズ液滴供給ジェネレーターのノズル揺らぎによりレーザー照射が空振りし、EUV光強度はゼロである。光源制御を選択せよ。",
            [
                ("euv_shutter_open_expose", "EUV露光シャッター開放・ウェハ露光進行"),
                ("euv_laser_abort_shot", "レーザー照射中断・ドロップレット再同期"),
                ("euv_tin_catcher_heat", "スズ捕集コレクター強制加熱溶融"),
                ("euv_hydrogen_debris_flush", "水素デブリパージ流量最大")
            ],
            "euv_shutter_open_expose", "euv_laser_abort_shot"
        ),
        (
            "07",
            "大深度広帯域地震観測網の震源メカニズム解の自動解析：『規定：P波初動押し引き極性と長周期表面波の振幅スペクトルがプレート境界浅部アスペリティ破壊に合致した場合は巨大地震津波警報フラグ出力、深発無感なら通常記録』とする。",
            "インバージョン計算結果：震源深さ15km、正断層すべり量4.5m、Mw7.8のアスペリティ連動破壊モデルと判定。警報処理を決定せよ。",
            "インバージョン計算結果：震源深さ420kmのマントル遷移層内微小破壊、規模M2.1、津波励起ゼロ。警報処理を決定せよ。",
            [
                ("tsunami_megathrust_warning", "巨大津波警報即時出力"),
                ("deep_event_routine_archive", "深発微小地震通常データ記録"),
                ("strainmeter_recalibrate_zero", "地殻歪計ゼロ点手動校正"),
                ("borehole_tilt_filter_reset", "傾斜計ノイズフィルターリセット")
            ],
            "tsunami_megathrust_warning", "deep_event_routine_archive"
        ),
        (
            "08",
            "法医毒物鑑定における高分解能飛行時間型質量分析（TOF-MS）の判定：『規定：未知試料の精密質量（Exact Mass）誤差が±2ppm以内かつ同位体存在比パターンが禁止有機薬物データベースと一致した場合は薬物同定陽性、不一致は陰性』とする。",
            "マススペクトル解析：精密質量誤差+0.4ppm、フラグメントイオンスペクトル照合スコア99.2%で規制薬物と合致。鑑定結果を判定せよ。",
            "マススペクトル解析：バックグラウンド溶媒ノイズ以外の特異的イオンピークは検出されず、保持時間一致ピークなし。鑑定結果を判定せよ。",
            [
                ("toxicology_positive_identified", "規制対象有機薬毒物同定陽性確定"),
                ("toxicology_negative_cleared", "該当薬物不検出（ブランク陰性）"),
                ("ms_quadrupole_tune_drift", "四重極マスフィルタ手動再調整"),
                ("electrospray_voltage_reverse", "エレクトロスプレーイオン化極性反転")
            ],
            "toxicology_positive_identified", "toxicology_negative_cleared"
        ),
        (
            "09",
            "宇宙往還機（有翼スペースプレーン）の大気圏再突入熱防護管理：『規定：ノーズコーン炭素炭素（C/C）複合材の表面よどみ点温度が1,650℃以下なら通常再突入滑空角維持、1,750℃超過時は揚力傾斜角（バンク角）を増して高度維持減速へ変更』とする。",
            "機体表面熱電対テレメトリ：現在のノーズ温度は1,480℃で耐熱設計裕度内である。飛行制御を決定せよ。",
            "機体表面熱電対テレメトリ：大気密度急変によりノーズ温度が1,810℃に急騰し制限限界を突破した。飛行制御を決定せよ。",
            [
                ("reentry_nominal_glide_slope", "定常滑空突入プロファイル維持"),
                ("reentry_high_bank_shallow", "揚力制御・浅角バンク旋回減速"),
                ("reentry_parachute_eject", "超音速ドラッグシュート強制射出"),
                ("reentry_rcs_purge_helium", "反動制御系ヘリウム全放出")
            ],
            "reentry_nominal_glide_slope", "reentry_high_bank_shallow"
        ),
        (
            "10",
            "高レベル放射性廃棄物地層処分場の人工バリア健全性評価：『規定：オーバーパック周囲の圧縮ベントナイト緩衝材の透水係数が1.0×10^-12 m/s以下を維持している場合は止水健全性合格、透水係数が基準を超過した場合は二次ボーリング隔離』とする。",
            "地下研究坑道ピエゾメータ測定：水理伝導度は3.2×10^-13 m/sと極めて低く、完全な止水封じ込めを確認。判定を導け。",
            "地下研究坑道ピエゾメータ測定：断層割れ目帯からの地下水浸潤により、局所透水係数が8.5×10^-10 m/sまで劣化した。判定を導け。",
            [
                ("buffer_containment_certified", "人工バリア止水健全性適合承認"),
                ("buffer_leak_secondary_isolate", "局所透水劣化・二次ボーリング隔離施工"),
                ("canister_crane_retrieval", "キャニスター直ち引上回収"),
                ("backfill_tunnel_cement_grout", "処分坑道セメント注入固化")
            ],
            "buffer_containment_certified", "buffer_leak_secondary_isolate"
        ),
        (
            "11",
            "クライオ電子顕微鏡（Cryo-EM）用生体タンパク質氷包埋サンプルの評価：『規定：急速凍結グリッド上の氷薄膜が均一な非晶質（アモルファス）ガラス状氷を形成している場合は高分解能データ収集開始、結晶氷化は再作製』とする。",
            "電子線回折パターン：鋭いブラッグ結晶回折環は一切見られず、アモルファス特有のブロードなハロー環のみを確認。判定せよ。",
            "電子線回折パターン：ヘキサゴナル（六方晶）結晶氷の明瞭なスポット回折が出現し、タンパク質立体構造が破壊されている。判定せよ。",
            [
                ("cryo_grid_vitreous_proceed", "非晶質氷良品・高分解能自動撮影開始"),
                ("cryo_grid_crystalline_reject", "結晶氷化不良・グリッド破棄再作製"),
                ("tem_field_emission_gun_bake", "電界放出型電子銃高温ベーキング"),
                ("camera_direct_detector_anneal", "直接検出器アニール処理")
            ],
            "cryo_grid_vitreous_proceed", "cryo_grid_crystalline_reject"
        ),
        (
            "12",
            "固体高分子形水電解（PEMEC）スタックの酸素発生反応（OER）運転基準：『規定：セル平均作動電圧が1.75V〜1.85Vの最適効率範囲内なら連続定格水素製造、2.00Vを超過した場合は触媒劣化防止のため負荷低減』とする。",
            "スタックインピーダンスモニタ：定格電流密度2.0A/cm2におけるセル電圧は1.78Vで極めて高効率である。電解運転を決定せよ。",
            "スタックインピーダンスモニタ：アノード触媒溶出により過電圧が増大し、平均セル電圧が2.08Vまで跳ね上がった。電解運転を決定せよ。",
            [
                ("pemec_rated_production_run", "定格高効率水素製造運転継続"),
                ("pemec_derate_catalyst_protect", "電流密度半減・触媒保護負荷低減"),
                ("pemec_deionize_water_reverse", "純水供給極性逆流洗浄"),
                ("pemec_membrane_acid_pickle", "電解質膜希硫酸酸洗処理")
            ],
            "pemec_rated_production_run", "pemec_derate_catalyst_protect"
        ),
        (
            "13",
            "大型放射光施設（Spring-8級）挿入光源（真空封止アンジュレータ）の波長同調：『規定：磁場ギャップ値と偏向パラメータKがビームライン要求X線エネルギーに同調完了した場合はビームラインフロントエンド開、脱調時は閉』とする。",
            "高精度リニアスケール：磁場ギャップは要求の10.500mmにミリミクロン精度で収束し、高輝度硬X線共鳴を確認。フロントエンドを決定せよ。",
            "高精度リニアスケール：パルスモータ脱調によりギャップ値に0.45mmの偏差が残り、所定波長から大きく外れている。フロントエンドを決定せよ。",
            [
                ("synchrotron_frontend_open", "フロントエンド開・X線照射実験開始"),
                ("synchrotron_frontend_close", "フロントエンド全閉・ビーム入射阻止"),
                ("storage_ring_beam_abort", "蓄積リング電子ビーム強制キックダンプ"),
                ("rf_cavity_buncher_sweep", "高周波加速空洞周波数スイープ")
            ],
            "synchrotron_frontend_open", "synchrotron_frontend_close"
        ),
        (
            "14",
            "超伝導線形重イオン加速器（SRF LINAC）の空洞クエンチ検出連動：『規定：ニオブ超伝導キャビティの無負荷品質係数（Q0値）が1.0×10^10以上なら高周波大電力励振継続、急激なQ値低下時は即座に高周波ドライブ遮断』とする。",
            "クライオRF測定系：空洞加速電界勾配18MV/mにおいてQ0値は1.8×10^10の極めて良好な超伝導性能を示している。高周波電力を指示せよ。",
            "クライオRF測定系：局部発熱による常伝導転移前兆を検知し、Q0値が10^7オーダーまで急激に3桁墜落した。高周波電力を指示せよ。",
            [
                ("srf_rf_power_drive_keep", "超伝導高周波大電力励振継続"),
                ("srf_quench_rf_trip_instant", "クエンチ保護・高周波入力即時遮断"),
                ("srf_liquid_helium_vent", "空洞ジャケット液体ヘリウム全放散"),
                ("srf_piezo_tuner_full_stroke", "ピエゾ同調器フルストローク駆動")
            ],
            "srf_rf_power_drive_keep", "srf_quench_rf_trip_instant"
        ),
        (
            "15",
            "海洋調査船搭載超音波水中測位システム（USBL）の海底トランスポンダ同期：『規定：探査機位置の測位残差RMSが0.5m以内かつ音速プロファイル整合率が98%以上なら音響トラッキング有効追尾、測位発散時は追尾中断』とする。",
            "音響信号処理プロセッサ：マルチパス波除去アルゴリズムが成功し、音響測位残差RMSは0.22mに収束した。測位判定を決定せよ。",
            "音響信号処理プロセッサ：海洋内部波と水温躍層の急変により音線屈折が激しく、測位残差が8.4mまで発散した。測位判定を決定せよ。",
            [
                ("usbl_tracking_valid_lock", "水中音響航法トラッキング追尾維持"),
                ("usbl_tracking_lost_abort", "音響追尾中断・位置推定無効フラグ"),
                ("usbl_ping_power_overboost", "送受波器パルス音圧過大送出"),
                ("usbl_hull_transducer_retract", "船底送受波器昇降ポール強制格納")
            ],
            "usbl_tracking_valid_lock", "usbl_tracking_lost_abort"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k4_defs:
        pairs.append({
            "id": f"rc2b4_dom_{gid}_s1", "group_id": f"rc2b4_dom_{gid}", "family": "domain_transfer",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_dom_{gid}_s2", "group_id": f"rc2b4_dom_{gid}", "family": "domain_transfer",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=6 (5 pairs: groups 16 to 20) ---
    k6_defs = [
        (
            "16",
            "大型極低温重力波望遠鏡のサファイア主鏡防振懸架制御：『規定：サファイア鏡温度が20K以下かつ光共振器ファブリ・ペロー干渉アライメントがロックされた場合は観測モード移行、光軸外れ時は再同調待機』とする。",
            "干渉計レーザー受光系：サファイア鏡温度18.2K、共振器フィネス整合、重力波干渉フリンジ完全ロックを達成。望遠鏡ステータスを決定せよ。",
            "干渉計レーザー受光系：地震動による吊り下げワイヤー共振で主鏡光軸が偏位し、干渉計ロックが完全に外れた。望遠鏡ステータスを決定せよ。",
            [
                ("kagra_observation_mode_run", "重力波天体観測サイエンスモード移行"),
                ("kagra_relock_alignment_wait", "観測中断・光共振器再同調ロック待機"),
                ("kagra_dump_laser_source", "メインレーザー光源強制消光"),
                ("kagra_cryocooler_heater_full", "冷凍機コンプレッサーヒーター過熱"),
                ("kagra_vacuum_duct_air_bleed", "長大真空パイプライン大気導入"),
                ("kagra_suspension_brake_clamp", "多段防振吊り架振り子機械クランプ")
            ],
            "kagra_observation_mode_run", "kagra_relock_alignment_wait"
        ),
        (
            "17",
            "高効率1600℃級ガスタービン・コンバインドサイクル（CCGT）の燃焼振動モニタ：『規定：燃焼器動圧センサの低周波音響変動（ハンチング）が許容値未満なら定格全負荷発電、振動ピーク急増時は燃料流量トリム絞り込み』とする。",
            "動圧スペクトラムアナライザ：燃焼器固有振動数における圧力変動振幅は0.8kPa（管理限界の20%）で静粛。発電制御を決定せよ。",
            "動圧スペクトラムアナライザ：火炎不安定性により120Hzの低周波音響共鳴ピークが急成長し、振幅が危険基準値を突破した。発電制御を決定せよ。",
            [
                ("ccgt_rated_full_load_keep", "定格全負荷発電運転継続"),
                ("ccgt_trim_fuel_nozzle_suppress", "燃料ノズル流量トリム絞込・振動抑制"),
                ("ccgt_trip_compressor_emergency", "空気圧縮機非常トリップ"),
                ("ccgt_steam_turbine_bypass_dump", "蒸気タービン排気復水器バイパス"),
                ("ccgt_bypass_scr_catalyst", "脱硝触媒排ガスバイパス開放"),
                ("ccgt_igniter_spark_continuous", "点火プラグ連続高圧放電")
            ],
            "ccgt_rated_full_load_keep", "ccgt_trim_fuel_nozzle_suppress"
        ),
        (
            "18",
            "軌道上人工衛星モノプロペラント・スラスタのヒドラジン触媒反応管理：『規定：イリジウム触媒ベッド予熱温度が180℃以上ならスラスタパルス点射を許可、予熱未達は不完全分解による触媒被毒防止のため点射禁止』とする。",
            "熱電対テレメトリ：触媒ベッドヒーターによりベッド温度は215℃に達し昇温完了。姿勢スラスタ点射を指示せよ。",
            "熱電対テレメトリ：衛星日陰通過に伴う電力制限でヒーターが未作動であり、ベッド温度はマイナス10℃である。姿勢スラスタ点射を指示せよ。",
            [
                ("thruster_pulse_fire_allow", "軌道制御スラスタパルス点射許可"),
                ("thruster_fire_inhibit_cold", "点射禁止・触媒ベッド予熱継続"),
                ("thruster_blowdown_hydrazine_vent", "推進薬タンクヒドラジン全量宇宙放出"),
                ("thruster_pressurant_helium_vent", "加圧ヘリウム高圧パージ弁開放"),
                ("thruster_pyro_valve_fire", "火工品パイロ弁点火破断"),
                ("thruster_nozzle_gimbal_free", "ノズルジンバルフリーロック解除")
            ],
            "thruster_pulse_fire_allow", "thruster_fire_inhibit_cold"
        ),
        (
            "19",
            "第三世代DNAナノポアシーケンサーのイオン電流変調解析：『規定：ポア通過時の塩基特異的ピコアンペア電流変調が正常観測される場合は配列リード記録、ポア閉塞による無通電時は逆パルス脱着』とする。",
            "パッチクランプ電流計：平均電流110pA、四塩基（A,C,G,T）固有のステップ状電流変調波形が高速で順調に推移している。判定せよ。",
            "パッチクランプ電流計：高分子凝集体がナノ細孔口に強固に吸着し、イオン電流が0pAにクランプ（目詰まり）した。判定せよ。",
            [
                ("nanopore_read_sequence_stream", "DNA塩基配列リアルタイム解析記録"),
                ("nanopore_reverse_pulse_unblock", "ポア閉塞・逆バイアス電圧パルス脱着"),
                ("nanopore_membrane_puncture_zap", "生体脂質二重膜高電圧破壊"),
                ("nanopore_buffer_flush_surfactant", "界面活性剤全量バッファ置換"),
                ("nanopore_laser_pinpoint_ablate", "レーザーアブレーション細孔再穿孔"),
                ("nanopore_chassis_drain_electrolyte", "電解液ドレン回収")
            ],
            "nanopore_read_sequence_stream", "nanopore_reverse_pulse_unblock"
        ),
        (
            "20",
            "超硬合金材料の熱間静水圧加圧（HIP）プロセス制御：『規定：アルゴン加圧雰囲気150MPa・均熱1,250℃に到達し保持時間内に圧力漏洩がなければHIPサイクル完了、漏洩発生時は降温減圧』とする。",
            "高圧圧力計・放射温度計：炉内圧力152MPa、温度1,250℃を厳密に維持し、保持時間120分を満了した。プロセス制御を指示せよ。",
            "高圧圧力計・放射温度計：圧力容器シール材熱劣化により、アルゴン圧力が毎分5MPaのペースで急落漏洩した。プロセス制御を指示せよ。",
            [
                ("hip_cycle_complete_anneal", "HIP高密度化サイクル正常完了・徐冷工程移行"),
                ("hip_leak_emergency_depressurize", "圧力漏洩・加熱停止強制排気減圧"),
                ("hip_vent_hot_argon_direct", "高温アルゴン大気直排弁急開"),
                ("hip_charge_oxygen_purge", "炉内酸素ガス急速置換"),
                ("hip_molybdenum_heater_overload", "モリブデンヒーター定格超過通電"),
                ("hip_coolant_jacket_isolate", "冷却水ジャケット給水遮断")
            ],
            "hip_cycle_complete_anneal", "hip_leak_emergency_depressurize"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k6_defs:
        pairs.append({
            "id": f"rc2b4_dom_{gid}_s1", "group_id": f"rc2b4_dom_{gid}", "family": "domain_transfer",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_dom_{gid}_s2", "group_id": f"rc2b4_dom_{gid}", "family": "domain_transfer",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=8 (5 pairs: groups 21 to 25) ---
    k8_defs = [
        (
            "21",
            "高エネルギー加速器実験の高分解能ミューオントラッカー（RPCガス検出器）判定：『規定：テトラフルオロエタン混合ガスの高圧印加ストリーマー放電が電極ストリップで検出され、時間分解能が1ナノ秒以内ならミューオン飛跡登録、偽放電はノイズ除去』とする。",
            "TDC（時間デジタル変換器）信号：衝突ビームバンチに同期して0.6ナノ秒の鋭い時間一致パルスを検出した。飛跡処理を決定せよ。",
            "TDC（時間デジタル変換器）信号：宇宙線バックグラウンドまたは電磁暗雑音によるランダムな幅広パルス（時間相関なし）である。飛跡処理を決定せよ。",
            [
                ("rpc_muon_track_accepted", "ミューオン事象飛跡登録・トリガー通過"),
                ("rpc_noise_pulse_vetoed", "非相関ノイズパルス排除・トリガー拒絶"),
                ("rpc_high_voltage_trip_cut", "検出器高圧電源保護トリップ"),
                ("rpc_gas_purge_argon_pure", "純アルゴンガス緊急パージ"),
                ("rpc_preamp_bias_inversion", "プリアンプ入力バイアス反転"),
                ("rpc_scintillator_test_light", "シンチレータ点検LED強制点灯"),
                ("rpc_strip_ground_short", "読み出しストリップ電極全地絡"),
                ("rpc_discriminator_threshold_zero", "弁別器閾値ゼロ固定")
            ],
            "rpc_muon_track_accepted", "rpc_noise_pulse_vetoed"
        ),
        (
            "22",
            "国際宇宙ステーション（ISS）日本実験棟の二相流アンモニア熱制御ループ：『規定：ポンプ入口サブクール度が5K以上を確保しベーパートルクのない液相単相流なら放熱ラジエーター循環維持、キャビテーション気泡発生時はアキュムレータ加圧』とする。",
            "熱流体計装テレメトリ：サブクール度7.2K、ポンプ吸込圧力安定、液相単相流が保証されている。熱制御を決定せよ。",
            "熱流体計装テレメトリ：配管受熱過多によりサブクール度が0.3Kまで低下し、インペラー部にキャビテーション気泡が発生した。熱制御を決定せよ。",
            [
                ("iss_radiator_loop_steady", "アンモニア放熱ループ定格循環維持"),
                ("iss_accumulator_pressurize", "アキュムレータ窒素加圧・気泡再凝縮"),
                ("iss_ammonia_jettison_space", "アンモニア冷媒船外緊急投棄"),
                ("iss_radiator_panel_jettison", "ラジエーターパネル切り離し投棄"),
                ("iss_evaporator_electric_heater_max", "蒸発器ヒーター全開過熱"),
                ("iss_bypass_valve_reverse_flow", "バイパス弁逆流開放"),
                ("iss_cooling_pump_speed_zero", "冷却ポンプ即時完全停止"),
                ("iss_thermal_blanket_strip", "多層断熱材MLI機械剥離")
            ],
            "iss_radiator_loop_steady", "iss_accumulator_pressurize"
        ),
        (
            "23",
            "生体適合性チタン合金人工骨の粉末床溶融結合（PBF-LB）レーザー造形：『規定：チャンバー内酸素濃度が50ppm以下かつ造形テーブル予熱温度200℃維持ならレーザースキャン実行、酸素混入時は酸化防止停止』とする。",
            "微量酸素分析計：アルゴン循環精製により酸素濃度18ppm、テーブル温度202℃で高純度を維持。造形指示を指示せよ。",
            "微量酸素分析計：チャンバー気密ガスケット不良により酸素濃度が350ppmに急上昇した。造形指示を指示せよ。",
            [
                ("pbf_laser_scan_melt_run", "チタン粉末レーザー溶融スキャン実行"),
                ("pbf_abort_oxidation_safety", "造形中断・レーザー照射緊急停止"),
                ("pbf_powder_recoater_max_force", "リコーターブレード最大力強制前進"),
                ("pbf_build_platform_drop_fast", "造形ステージ最下点急降下"),
                ("pbf_purge_chamber_with_air", "造形チャンバーへの大気急送"),
                ("pbf_filter_blowback_disabled", "集塵フィルター逆洗機能強制無効"),
                ("pbf_optical_scanner_uncalibrated", "ガルバノミラー原点未補正スキャン"),
                ("pbf_powder_hopper_vibrate_max", "原料ホッパー過大振動")
            ],
            "pbf_laser_scan_melt_run", "pbf_abort_oxidation_safety"
        ),
        (
            "24",
            "超伝導単一光子検出器（SSPD）の微弱近赤外光フォトンカウンティング：『規定：ナノワイヤバイアス電流が臨界電流の95%に設定され超伝導クエンチスパイクのみを計数する場合はフォトンパルス加算、連続常電導ラッチ時はリセット』とする。",
            "高速パルス計測系：単一光子吸収による急峻な電圧パルス（半値幅2ナノ秒）が観測され、正常に超伝導復帰した。計数判定を決定せよ。",
            "高速パルス計測系：熱暴走により超伝導復帰せず、常電導ラッチ（連続抵抗状態）に陥り計数が永久停止した。計数判定を決定せよ。",
            [
                ("sspd_photon_count_accumulate", "フォトンパルス正常積算加算"),
                ("sspd_reset_bias_unlatch", "バイアス電流瞬時ゼロ遮断リセット"),
                ("sspd_quench_overdrive_bias", "バイアス電流限界超過印加"),
                ("sspd_attenuator_optical_bypass", "光アッテネータ完全バイパス直撃"),
                ("sspd_cryostat_heater_warmup", "クライオスタット常温昇温"),
                ("sspd_preamp_gain_attenuate", "プリアンプゲイン最小減衰"),
                ("sspd_time_tagger_corrupt", "時間記録タイムタガー誤作動"),
                ("sspd_fiber_connector_unplug", "受光光ファイバー手動抜去")
            ],
            "sspd_photon_count_accumulate", "sspd_reset_bias_unlatch"
        ),
        (
            "25",
            "放射性廃棄物ガラス固化溶融炉（JSM）のジュール直接通電加熱制御：『規定：溶融ガラス中心温度が1,150℃〜1,200℃に保持され電極電流インピーダンスが正常範囲内なら固化溶融継続、導電率異常時は通電トリム』とする。",
            "熱電対・インピーダンス計：ガラス温度1,165℃、モリブデン主電極間の抵抗値は規定中央値で安定。溶融炉制御を指示せよ。",
            "熱電対・インピーダンス計：貴金属白金族元素の底部沈降堆積により電極間が短絡し、異常大電流サージが発生した。溶融炉制御を指示せよ。",
            [
                ("jsm_vitrification_steady_run", "ジュール加熱定常ガラス溶融運転継続"),
                ("jsm_trim_power_short_protect", "電極短絡防止・通電電力緊急絞込遮断"),
                ("jsm_drain_valve_freeze_burst", "炉底流下ノズル冷却管破裂"),
                ("jsm_offgas_scrubber_shutdown", "オフガス処理系排気ブロワー停止"),
                ("jsm_canister_turntable_spin_max", "キャニスター回転台最高速回転"),
                ("jsm_melter_refractory_quench_cold", "耐火レンガ冷水急冷破壊"),
                ("jsm_add_dry_powder_unmixed", "未混合ガラス原料乾粉一括投入"),
                ("jsm_induction_heater_reverse", "誘導加熱コイル逆相結線")
            ],
            "jsm_vitrification_steady_run", "jsm_trim_power_short_protect"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k8_defs:
        pairs.append({
            "id": f"rc2b4_dom_{gid}_s1", "group_id": f"rc2b4_dom_{gid}", "family": "domain_transfer",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_dom_{gid}_s2", "group_id": f"rc2b4_dom_{gid}", "family": "domain_transfer",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=12 (5 pairs: groups 26 to 30) Concise choices! ---
    k12_defs = [
        (
            "26",
            "宇宙太陽光発電（SSPS）フェーズドアレイのマイクロ波ビーム送電：パイロット信号追尾で受電レクテナとの位相差が許容内なら送電継続、位相拡散時は送電停止。",
            "レクテナ位相測定：位相同期ループ（PLL）は0.1度の高精度で同期合致。送電アンテナの指示を決定せよ。",
            "レクテナ位相測定：電離層外乱によりパイロット信号の位相が激しく乱高下し同期喪失。送電アンテナの指示を決定せよ。",
            [
                ("ssps_beam_transmit_on", "マイクロ波大電力送電継続"),
                ("ssps_beam_abort_off", "送電緊急停止・位相クリア"),
                ("ssps_solar_cell_disconnect", "太陽電池パドル電路遮断"),
                ("ssps_attitude_yaw_spin", "衛星本体高速スピン反転"),
                ("ssps_ground_horn_invert", "地上受信ホーン極性反転"),
                ("ssps_heat_pipe_freeze", "ヒートパイプ冷媒固化"),
                ("ssps_frequency_drift_high", "周波数帯域高調波変調"),
                ("ssps_tether_wire_cut", "テザーケーブル緊急切断"),
                ("ssps_battery_trickle_dump", "蓄電池トリクル放電"),
                ("ssps_ion_thruster_ignite", "イオンエンジン全開点火"),
                ("ssps_telemetry_encryption_reset", "テレメトリ暗号鍵消去"),
                ("ssps_star_sensor_shutter_close", "天測センサー遮光蓋密閉")
            ],
            "ssps_beam_transmit_on", "ssps_beam_abort_off"
        ),
        (
            "27",
            "高速点火レーザー核融合のターゲットチェンバー：爆縮用重水素（DT）球ペレットの真球度・位置整合が満たされれば点火ピコ秒レーザー照射、位置ズレ時は照射中止。",
            "高速画像診断：ペレットは炉心中心に到達、位置誤差3μmで完全捕捉。点火レーザーを指示せよ。",
            "高速画像診断：ペレット注入ノズル軌道偏位により中心から150μm外れて落下中。点火レーザーを指示せよ。",
            [
                ("fusion_igniter_laser_fire", "点火レーザー超高強度照射"),
                ("fusion_igniter_abort_shot", "点火トリガー中止安全退避"),
                ("fusion_chamber_vacuum_vent", "燃焼容器大気急速解放"),
                ("fusion_debris_shield_retract", "デブリ防護板強制後退"),
                ("fusion_cryo_target_heat", "ペレット高温急速加熱"),
                ("fusion_magnetic_cusp_off", "磁気カスプコイル消磁"),
                ("fusion_streak_camera_blank", "ストリークカメラ遮光"),
                ("fusion_tritium_getter_dump", "三重水素ゲッター投棄"),
                ("fusion_amplifier_flash_burst", "増幅器キセノン過負荷"),
                ("fusion_spatial_filter_block", "空間フィルター全ピン閉"),
                ("fusion_calorimeter_dry_fire", "熱量計空焚き計測"),
                ("fusion_pellet_dropper_jam", "燃料供給機強制詰まり")
            ],
            "fusion_igniter_laser_fire", "fusion_igniter_abort_shot"
        ),
        (
            "28",
            "核融合トカマク定常プラズマ電子サイクロトロン加熱（ECRH）：ジャイロトロン高周波発振周波数と共鳴層が合致なら入射継続、アーク放電発生時は導波管遮断。",
            "ミリ波導波管光センサ：アーク放電光ゼロ、高周波パワー1.0MW定常透過。ミリ波入射を決定せよ。",
            "ミリ波導波管光センサ：導波管ベリリウム窓付近で激しいアーク放電発光を検知。ミリ波入射を決定せよ。",
            [
                ("ecrh_gyrotron_rf_inject", "ミリ波ビームプラズマ入射"),
                ("ecrh_arc_trip_shutoff", "アーク遮断器即時トリップ"),
                ("ecrh_anode_voltage_surge", "陽極電圧過大サージ印加"),
                ("ecrh_collector_cooling_stop", "コレクター冷却水停止"),
                ("ecrh_launcher_mirror_flip", "可動ミラー最大角反転"),
                ("ecrh_cryomagnet_quench_vent", "超電導磁石ヘリウム放出"),
                ("ecrh_dummy_load_drain", "ダミーロード水冷却遮断"),
                ("ecrh_polarizer_grating_jam", "偏波器回折格子固着"),
                ("ecrh_electron_gun_heater_off", "電子銃ヒーター加熱遮断"),
                ("ecrh_window_chiller_drain", "窓冷却回路空焚き運転"),
                ("ecrh_gate_valve_pinch_slam", "真空バルブ急閉塞切断"),
                ("ecrh_modulator_crowbar_fire", "クローバー回路強制放電")
            ],
            "ecrh_gyrotron_rf_inject", "ecrh_arc_trip_shutoff"
        ),
        (
            "29",
            "量子コンピュータ極微弱マイクロ波読み出し（JPA増幅器）：ポンプ周波数とジョセフソンパラメトリック利得が最適なら量子状態読み出し、飽和時はポンプ減衰。",
            "マイクロ波Sパラメータ測定：利得22dB、量子限界雑音温度を達成。読み出し処理を決定せよ。",
            "マイクロ波Sパラメータ測定：入力過大により1dB圧縮点を超過し、非線形飽和歪みが発生。読み出し処理を決定せよ。",
            [
                ("jpa_qubit_readout_execute", "低雑音量子ビット状態読出"),
                ("jpa_pump_power_attenuate", "ポンプ電力減衰・非線形解除"),
                ("jpa_magnetic_flux_coil_max", "磁束バイアス最大通電"),
                ("jpa_circulator_reverse_port", "サーキュレータ端子入替"),
                ("jpa_hemt_amplifier_overheat", "極低温HEMT高電圧過熱"),
                ("jpa_attenuator_zero_direct", "直結無減衰マイクロ波過熱"),
                ("jpa_local_oscillator_unlock", "局発周波数完全離調"),
                ("jpa_dc_block_dielectric_melt", "DC阻止コンデンサ溶損"),
                ("jpa_resonator_frequency_sweep", "超伝導共振器広域走査"),
                ("jpa_iq_mixer_imbalance_max", "IQミキサ直交バランス崩壊"),
                ("jpa_bias_tee_inductor_burn", "バイアスTチョーク焼損"),
                ("jpa_qubit_reset_microwave_pulse", "量子ビット強制励起パルス")
            ],
            "jpa_qubit_readout_execute", "jpa_pump_power_attenuate"
        ),
        (
            "30",
            "深海熱水噴出孔インサイチュ電気化学センサ：金・硫黄電極の酸化還元電位が熱水プルームを捉えていれば自動サンプリング開始、海水浸食時はセンサ保護待機。",
            "ポテンショスタット測定：硫化水素酸化ピーク電流が明瞭に出現し、熱水プルーム中と確認。深海サンプラーを決定せよ。",
            "ポテンショスタット測定：耐圧電極隔膜が深海高圧海水で微小リークし、電位が海水電位へドリフト。深海サンプラーを決定せよ。",
            [
                ("hydrothermal_sample_start", "熱水プルーム自動採取開始"),
                ("hydrothermal_sensor_protect", "電極保護回路作動・測定待機"),
                ("hydrothermal_titanium_bottle_drop", "チタン採水ボトル海底投棄"),
                ("hydrothermal_rov_thruster_all_stop", "探査機全推進スラスタ停止"),
                ("hydrothermal_glass_electrode_break", "ガラス比較電極耐圧破壊"),
                ("hydrothermal_battery_pod_flood", "耐圧蓄電池ポッド浸水浸食"),
                ("hydrothermal_ctd_conductivity_zero", "塩分計ゼロスパン異常"),
                ("hydrothermal_methane_sensor_burn", "メタン熱線素子焼損"),
                ("hydrothermal_turbidity_led_off", "後方散乱濁度計LED消灯"),
                ("hydrothermal_ph_isopotential_drift", "等電位点補正急変動"),
                ("hydrothermal_buoyancy_foam_strip", "浮力材シンタクチック剥離"),
                ("hydrothermal_cable_insulation_short", "耐水アーマード導線短絡")
            ],
            "hydrothermal_sample_start", "hydrothermal_sensor_protect"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k12_defs:
        pairs.append({
            "id": f"rc2b4_dom_{gid}_s1", "group_id": f"rc2b4_dom_{gid}", "family": "domain_transfer",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_dom_{gid}_s2", "group_id": f"rc2b4_dom_{gid}", "family": "domain_transfer",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    return pairs
