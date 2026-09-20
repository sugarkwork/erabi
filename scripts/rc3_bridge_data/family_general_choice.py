"""Family 6: general_choice (30 pairs, 60 cases) - RC3 Bridge Benchmark
Prefix: rc3b_gen_
Distribution: K=4 (10 pairs), K=8 (10 pairs), K=16 (10 pairs)
Focus: High-cardinality candidate interference (K=8, K=16) with fine-grained in-domain competitors.
Zero leakage against all past datasets.
"""

from typing import Any, Dict, List, Tuple


def make_choices(c_defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in c_defs]


def get_general_choice_pairs() -> List[Dict[str, Any]]:
    pairs: List[Dict[str, Any]] = []

    # --- K=4 (10 pairs: groups 01 to 10) ---
    k4_defs = [
        (
            "01",
            "機械工学における材料硬度測定試験の選定。試験基準は『薄板めっき層（厚み10μm以下）の微小局所硬さ測定』である。",
            "測定対象：膜厚5μmのDLC（ダイヤモンドライクカーボン）超硬質コーティングの薄膜硬度を測定したい。最適な試験法を選べ。",
            "測定対象：大型船舶用ディーゼルエンジン鋳鉄製クランクシャフト母材の全体平均硬度を現場で測定したい。最適な試験法を選べ。",
            [("hardness_micro_vickers", "マイクロビッカース微小硬さ試験"), ("hardness_brinell", "ブリネル押込硬さ試験"), ("hardness_rockwell_c", "ロックウェルCスケール硬さ試験"), ("hardness_shore_sclero", "ショア反発式硬さ試験")],
            "hardness_micro_vickers", "hardness_brinell"
        ),
        (
            "02",
            "電子回路におけるノイズ対策受動部品の選定。設計基準は『高周波電源ライン（100MHz帯）の伝導差動コモンモードノイズ除去』である。",
            "回路要件：USB3.0高速差動信号ラインに重畳する高周波放射ノイズを除去し、信号波形崩れを防ぎたい。適用素子を選べ。",
            "回路要件：DC-DCコンバータ出力の低周波リプル（50kHz）を平滑化し大電流を蓄積したい。適用素子を選べ。",
            [("noise_common_mode_choke", "コモンモードチョークコイル"), ("noise_low_esr_al_cap", "低ESR大容量アルミ電解コンデンサ"), ("noise_ferrite_bead_single", "単線フェライトビーズ"), ("noise_zener_surge_diode", "ツェナーバリスタサージ保護ダイオード")],
            "noise_common_mode_choke", "noise_low_esr_al_cap"
        ),
        (
            "03",
            "非破壊検査（NDT）における溶接欠陥探傷手法の選定。検査基準は『オーステナイト系ステンレス配管溶接部の内部微小ブローホール立体検出』である。",
            "検査要件：非磁性体ステンレス厚肉配管の溶接内部に存在する球状気孔の位置と深さを非破壊で精密可視化したい。検査法を選定せよ。",
            "検査要件：強磁性体炭素鋼構造物溶接ビードの最表面に開口した極微細クラックを現場で目視検出したい。検査法を選定せよ。",
            [("ndt_phased_array_ultrasonic", "フェーズドアレイ超音波探傷試験（PAUT）"), ("ndt_magnetic_particle", "湿式蛍光磁粉探傷試験（MT）"), ("ndt_eddy_current_array", "渦電流アレイ探傷試験（ECT）"), ("ndt_liquid_penetrant", "染色浸透探傷試験（PT）")],
            "ndt_phased_array_ultrasonic", "ndt_magnetic_particle"
        ),
        (
            "04",
            "熱交換器の流体流向設計。基準は『高温側流体と低温側流体の出口温度差を最小化し熱交換効率（対数平均温度差LMTD）を極大化する』である。",
            "流動設計：向流型配置（Counter-current）を採用し、流体同士が互いに逆方向へ流動するよう配管接続した。流向型式を判定せよ。",
            "流動設計：並流型配置（Co-current）を採用し、高温入口と低温入口を同一側に配置して同方向へ流動させた。流向型式を判定せよ。",
            [("hex_counter_current_flow", "向流型熱交換配置（最大熱交換効率）"), ("hex_co_current_flow", "並流型熱交換配置（壁面温度均一緩和）"), ("hex_cross_flow_single", "直交流型配置（ダクト送風直交）"), ("hex_divided_flow_shell", "分割流型シェルアンドチューブ配置")],
            "hex_counter_current_flow", "hex_co_current_flow"
        ),
        (
            "05",
            "金属防食技術における電気防食方式の選定。基準は『外部商用電源のない港湾海中鋼管杭における長期メンテナンスフリー防食』である。",
            "設計条件：外部電源供給が不可能であり、海水中で卑な電位を持つ金属板を鋼管杭に直接接続して自己犠牲的に溶解させ防食したい。防食方式を選べ。",
            "設計条件：直流電源装置を陸上に設置し、不溶性チタン電極から防食電流を広域埋設パイプラインへ強制的に通電したい。防食方式を選べ。",
            [("corrosion_galvanic_anode", "流電陽極方式（犠牲陽極法：亜鉛・アルミニウム合金）"), ("corrosion_impressed_current", "外部電源方式（不溶性陽極・直流定電位供給法）"), ("corrosion_epoxy_heavy_coat", "重防食エポキシガラスフレーク塗装塗膜"), ("corrosion_inhibitor_dosing", "インヒビター防食剤連続薬液注入")],
            "corrosion_galvanic_anode", "corrosion_impressed_current"
        ),
        (
            "06",
            "ポンプ工学におけるキャビテーション防止基準。基準は『有効吸込揚程NPSHaが必要吸込揚程NPSHrを常に上回るよう設計マージンを確保する』である。",
            "流体状態：液温上昇により飽和蒸気圧が急上昇し、吸込側配管の圧力損失過大により羽根車入口で気泡が発生・壊食音が発生した。現象を判定せよ。",
            "流体状態：吐出側弁の急閉止により管路内流動慣性が急停止し、管壁を叩く激しい衝撃圧力波（サージ圧）が発生した。現象を判定せよ。",
            [("pump_cavitation_flashing", "キャビテーション現象（吸込減圧気泡壊食）"), ("pump_water_hammer_surge", "水撃現象（ウォーターハンマー急閉塞サージ）"), ("pump_air_binding_lock", "エアバインディング（気体混入揚水不能）"), ("pump_thermal_expansion_vent", "熱膨張過圧リリーフ")],
            "pump_cavitation_flashing", "pump_water_hammer_surge"
        ),
        (
            "07",
            "機械要素設計における締結用ねじの緩み止め機構の選定。基準は『高振動環境下におけるねじ軸力低下防止機構』である。",
            "設計要件：鉄道車両台車枠の激しい振動環境において、楔効果（カム面傾斜角＞ねじリード角）により振動で自然に増し締めされる構造を採用したい。部品を選べ。",
            "設計要件：ボルト先端に割ピンを貫通させてナットの完全脱落を物理的に阻止するクラウン形状ナットを採用したい。部品を選べ。",
            [("fastener_wedge_lock_washer", "ウェッジロッキングワッシャー（ノルトロック座金）"), ("fastener_slotted_castle_nut", "溝付きナットおよびコッター割ピン締結"), ("fastener_spring_split_washer", "一般ばね座金（スプリングワッシャー）"), ("fastener_double_nut_jam", "ダブルナット共回り締め付け")],
            "fastener_wedge_lock_washer", "fastener_slotted_castle_nut"
        ),
        (
            "08",
            "流体制御バルブのトリム流量特性の選定。設計基準は『プロセス負荷変動に応じた弁開度と流量変化率の相関特性』である。",
            "プロセス要件：配管圧力損失が大きく、低開度から高開度まで弁開度増分に対する流量変化の割合が常に等しい比率（対数関数的）で増加する特性を要求。弁特性を選べ。",
            "プロセス要件：弁差圧がほぼ一定の熱水混合ラインにおいて、弁開度に完全に正比例して直線的に流量が増加する特性を要求。弁特性を選べ。",
            [("valv_equal_percentage", "イコールパーセンテージ流量特性（等百分率弁）"), ("valv_linear_flow_trim", "リニア流量特性（直線的流量比例弁）"), ("valv_quick_opening_disc", "クイックオープニング特性（急速全開ON/OFF弁）"), ("valv_hyperbolic_blowdown", "双曲線ブローダウン減圧特性")],
            "valv_equal_percentage", "valv_linear_flow_trim"
        ),
        (
            "09",
            "高電圧受電設備における避雷器（アレスター）の特性選定。基準は『電力系統への雷サージおよび開閉サージ侵入時の機器絶縁保護』である。",
            "素子選定：非線形抵抗特性に極めて優れ、通常課電時はほぼ絶縁状態を保ち、サージ過電圧印加時に瞬時に大電流を大地へ放電する焼結セラミックスを採用。素子を選べ。",
            "素子選定：主母線と大地の間に空気間隙を設け、過電圧飛来時に火花放電を起こして後続機器を保護する伝統的放電電極を採用。素子を選べ。",
            [("arrester_zno_varistor", "酸化亜鉛（ZnO）非線形素子ギャップレス避雷器"), ("arrester_spark_gap_horn", "放電ギャップ（アークホーン火花電極）"), ("arrester_silicon_carbide", "炭化ケイ素（SiC）直列ギャップ付き避雷器"), ("arrester_gas_discharge_tube", "ガス放電管（GDTサージアブソーバー）")],
            "arrester_zno_varistor", "arrester_spark_gap_horn"
        ),
        (
            "10",
            "冷凍空調サイクルにおける膨張弁の作動方式選定。基準は『蒸発器出口冷媒の過熱度（スーパーヒート）追従制御』である。",
            "制御方式：蒸発器出口に感温筒を取り付け、封入ガスの熱膨張によるダイヤフラム変位でオリフィス開度を自律機械的に調整する弁を採用。方式を選定せよ。",
            "制御方式：マイクロプロセッサが温度・圧力センサー値から過熱度を常時演算し、ステッピングモーターでニードル開度をパルス駆動制御する弁を採用。方式を選定せよ。",
            [("expansion_thermostatic_txv", "温度式自動膨張弁（TXVメカニカルダイヤフラム）"), ("expansion_electronic_eev", "電子膨張弁（EEVステッピングモーター制御）"), ("expansion_fixed_capillary", "固定キャピラリーチューブ細管絞り"), ("expansion_float_chamber_valv", "低圧フロート式液面制御膨張弁")],
            "expansion_thermostatic_txv", "expansion_electronic_eev"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k4_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_gen_{gid}_s1",
                "group_id": f"rc3b_gen_{gid}",
                "family": "general_choice",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_gen_{gid}_s2",
                "group_id": f"rc3b_gen_{gid}",
                "family": "general_choice",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2}
            }
        ])

    # --- K=8 (10 pairs: groups 11 to 20) ---
    k8_defs = [
        (
            "11",
            "ネットワークOSI参照モデルにおけるレイヤー選定。通信障害の発生箇所を階層別に特定する。",
            "障害診断：Ethernetフレームヘッダ内の送信元MACアドレス学習テーブルがオーバーフローし、フレームが全ポートへフラッディングされた。該当レイヤーを選べ。",
            "障害診断：TCPスリーウェイハンドシェイク時のSYNパケット再送タイムアウトにより、エンドツーエンドの仮想接続が確立できない。該当レイヤーを選べ。",
            [("osi_layer1_physical", "第1層：物理層（ビット伝送・電気信号）"), ("osi_layer2_datalink", "第2層：データリンク層（MACアドレス・フレーム）"), ("osi_layer3_network", "第3層：ネットワーク層（IPルーティング・パケット）"), ("osi_layer4_transport", "第4層：トランスポート層（TCP/UDP・セグメント）"), ("osi_layer5_session", "第5層：セッション層（通信セッション確立管理）"), ("osi_layer6_presentation", "第6層：プレゼンテーション層（データ表現・暗号化）"), ("osi_layer7_application", "第7層：アプリケーション層（HTTP/DNS・ユーザーIF）"), ("osi_cross_plane_mgmt", "クロスレイヤー管理プレーン")],
            "osi_layer2_datalink", "osi_layer4_transport"
        ),
        (
            "12",
            "材料力学における金属結晶格子のすべり変形機構選定。塑性変形の結晶構造別特性を判定する。",
            "材料特性：面心立方格子（FCC）構造を持ち、{111}最密面上に12個の独立すべり系を有するため、極低温環境下でも脆性破壊を起こさず極めて延性に富む。金属結晶系を選べ。",
            "材料特性：稠密六方格子（HCP）構造を持ち、底面{0001}すべり系が3個に限定されるため、室温での加工性が乏しく双晶変形を伴いやすい。金属結晶系を選べ。",
            [("crystal_fcc_austenitic", "面心立方格子（FCC：オーステナイト鋼・アルミニウム・銅）"), ("crystal_bcc_ferritic", "体心立方格子（BCC：フェライト普通鋼・タングステン・モリブデン）"), ("crystal_hcp_hexagonal", "稠密六方格子（HCP：チタン・マグネシウム・亜鉛）"), ("crystal_bct_martensite", "体心正方格子（BCT：焼入れマルテンサイト組織）"), ("crystal_amorphous_glass", "アモルファス非晶質構造（金属ガラス）"), ("crystal_diamond_cubic", "ダイヤモンド立方格子（シリコン・ゲルマニウム）"), ("crystal_perovskite_oxide", "ペロブスカイト酸化物強誘電相"), ("crystal_intermetallic_sigma", "金属間化合物脆性シグマ相")],
            "crystal_fcc_austenitic", "crystal_hcp_hexagonal"
        ),
        (
            "13",
            "熱処理工学における鋼の恒温変態（TTT曲線）組織選定。目標機械的性質に応じた冷却速度・保持温度組織を決定する。",
            "熱処理工程：オーステナイト化温度からMS点（マルテンサイト変態開始点）直上の350℃塩浴へ急冷し等温保持して、羽毛状・針状の高靭性組織を得た。組織名を選べ。",
            "熱処理工程：オーステナイト化温度から臨界冷却速度以上で室温水中へ急冷焼入れし、過飽和固溶体による極めて硬く脆い針状組織を得た。組織名を選べ。",
            [("micro_bainite_structure", "ベイナイト組織（等温変態高強度・高靭性相）"), ("micro_martensite_quench", "マルテンサイト組織（無拡散剪断変態・最高硬度相）"), ("micro_pearlite_lamellar", "パーライト組織（フェライト＋セメンタイト層状相）"), ("micro_sorbite_tempered", "ソルバイト組織（高温焼戻し調質微細炭化物相）"), ("micro_troostite_nodular", "トルースタイト組織（中温焼戻し結節状相）"), ("micro_ferrite_proeutectoid", "初析フェライト組織（軟質純鉄基質相）"), ("micro_cementite_grain_boundary", "網状粒界セメンタイト組織（過共析脆化相）"), ("micro_retained_austenite", "残留オーステナイト組織（未変態不安定相）")],
            "micro_bainite_structure", "micro_martensite_quench"
        ),
        (
            "14",
            "熱力学サイクルにおける理想機関サイクル選定。作動流体と加熱・膨張行程の組合せを評価する。",
            "サイクル構成：2つの可逆等温変化と2つの可逆等容変化から構成され、再生器によって熱効率をカルノーサイクルと同等に高める外燃ガスサイクル。名称を選べ。",
            "サイクル構成：2つの断熱変化と2つの等圧変化（等圧加熱・等圧放熱）から構成され、航空ガスタービンやジェットエンジンの基本となるサイクル。名称を選べ。",
            [("thermo_stirling_cycle", "スターリングサイクル（等温変化＋等容再生外燃）"), ("thermo_brayton_cycle", "ブレイトンサイクル（等圧加熱＋断熱膨張ガスタービン）"), ("thermo_rankine_cycle", "ランキンサイクル（相変化蒸気タービン基盤）"), ("thermo_otto_cycle", "オットーサイクル（等容燃焼ガソリン火花点火）"), ("thermo_diesel_cycle", "ディーゼルサイクル（等圧燃焼低速圧縮着火）"), ("thermo_sabathe_dual_cycle", "サバテ複合サイクル（等容＋等圧燃焼高速ディーゼル）"), ("thermo_ericsson_cycle", "エリクソンサイクル（等温変化＋等圧再生）"), ("thermo_kalina_ammonia_cycle", "カリーナサイクル（アンモニア水混合媒体多段蒸発）")],
            "thermo_stirling_cycle", "thermo_brayton_cycle"
        ),
        (
            "15",
            "計測工学における温度センサー動作原理選定。測定温度域と感度・直線性を考慮する。",
            "原理要件：2種の異なる金属線の両端を接合し、両接点間に温度差が生じたときに熱起電力が生じる効果（ゼーベック効果）を利用するセンサー。選定せよ。",
            "原理要件：金属導線（高純度白金）の電気抵抗値が温度上昇に正比例して直線的に増加する特性を利用し、高精度基準温度計として用いるセンサー。選定せよ。",
            [("sensor_thermocouple_seebeck", "熱電対（ゼーベック効果熱起電力センサー）"), ("sensor_rtd_pt100_linear", "白金測温抵抗体（Pt100抵抗線形変化センサー）"), ("sensor_ntc_thermistor_oxide", "NTCサーミスタ（負の温度係数半導体センサー）"), ("sensor_pyrometer_infrared_optic", "放射温度計（ステファン・ボルツマン放射光センサー）"), ("sensor_bimetal_strip_mechanical", "バイメタル膨張式メカニカル温度計"), ("sensor_fiber_bragg_grating", "FBG光ファイバーブラッグ格子波長シフトセンサー"), ("sensor_acoustic_gas_thermometer", "超音波音速伝播気体温度センサー"), ("sensor_liquid_crystal_thermo", "コレステリック液晶変色温度センサー")],
            "sensor_thermocouple_seebeck", "sensor_rtd_pt100_linear"
        ),
        (
            "16",
            "化学工学における蒸留塔内部構造選定。処理気液比、圧力損失、ファウリング耐性を評価する。",
            "塔内構造：金網や規則的な波板シートを規則的に積み重ねた充填物を塔内に配置し、極めて低い圧力損失で高理論段数を稼ぐ構造。構造型式を選べ。",
            "塔内構造：塔内に水平な棚段を設け、開孔の上に可動式バルブキャップを配置して蒸気流速に応じ開閉するトレイ構造。構造型式を選べ。",
            [("distill_structured_packing", "規則充填物（構造化メラパック・超低圧損真空蒸留）"), ("distill_valve_tray_plate", "バルブトレイ（可動弁トレイ・広運転範囲棚段）"), ("distill_bubble_cap_tray", "バブルキャップトレイ（液シール確実・極低流量保持）"), ("distill_sieve_perforated_plate", "シーブトレイ（多孔板単純構造・低コスト）"), ("distill_random_raschig_ring", "不規則充填物（ラシヒリング・ポールリング散布）"), ("distill_dualflow_baffle_tray", "デュアルフロートレイ（降液管なし逆流構造）"), ("distill_spinning_band_ultra", "回転バンド式超精密小容量蒸留カラム"), ("distill_membrane_pervaporation", "浸透気化パーバポレーション分離膜モジュール")],
            "distill_structured_packing", "distill_valve_tray_plate"
        ),
        (
            "17",
            "制御工学における古典制御PID補償器の各動作要素選定。目標値追従性と外乱抑制を評価する。",
            "動作要素：偏差の積分値に比例して制御出力を増減させ、比例帯内に残る定常偏差（オフセット）を完全にゼロへと収束させる要素。要素名を選べ。",
            "動作要素：偏差の変化速度（微分値）に比例して制御出力を与え、急激な外乱変動に対して先行的にブレーキをかけてオーバーシュートを抑制する要素。要素名を選べ。",
            [("control_integral_action", "積分動作（I動作：定常偏差オフセット完全除去）"), ("control_derivative_action", "微分動作（D動作：外乱速応制動・オーバーシュート抑制）"), ("control_proportional_action", "比例動作（P動作：現在偏差比例基本フィードバック）"), ("control_feedforward_action", "フィードフォワード要素（外乱事前測定先行補償）"), ("control_deadbeat_action", "有限時間整定デッドビートアルゴリズム"), ("control_anti_windup_clamp", "アンチワインドアップ（積分飽和リミットクランプ）"), ("control_smith_predictor", "スミス予測器（むだ時間遅延要素事前補償）"), ("control_notch_filter_suppress", "ノッチフィルタ（機械共振周波数選択的減衰）")],
            "control_integral_action", "control_derivative_action"
        ),
        (
            "18",
            "航空力学における主翼翼型空力パラメータ選定。迎え角と失速特性を評価する。",
            "空力特性：揚力係数CLが最大値に達した直後、翼上面の気流が前縁付近から剥離して揚力が急減し抗力が跳ね上がる現象。名称を選べ。",
            "空力特性：有限翼の翼端において、下面の高圧領域から上面の低圧領域へ気流が巻き込むことで発生する誘導抗力の主因となる現象。名称を選べ。",
            [("aero_stall_boundary_layer", "翼面失速（前縁剥離・最大揚力急落失速）"), ("aero_wingtip_vortex_drag", "翼端渦（翼端誘導渦・渦誘導抗力発生源）"), ("aero_wave_drag_shock", "造波抗力（遷音速垂直衝撃波抵抗）"), ("aero_laminar_separation_bubble", "層流剥離泡（局所剥離再付着バブル）"), ("aero_mach_tuck_pitch", "マックタック（風圧中心後退機首下げ現象）"), ("aero_coanda_effect_circulation", "コアンダ効果（曲面追従噴流循環増強）"), ("aero_ground_effect_cushion", "地面効果（地表接近揚抗比急増）"), ("aero_flutter_aeroelastic", "フラッター（空力弾性発散自励振動）")],
            "aero_stall_boundary_layer", "aero_wingtip_vortex_drag"
        ),
        (
            "19",
            "油圧システムにおける作動油選定。引火危険性と潤滑性、使用環境温度を評価する。",
            "作動油種：製鉄所の高炉近傍など火災危険の極めて高い環境で使用され、水滴を鉱油中に分散させたW/Oエマルジョン難燃性作動油。油種を選定せよ。",
            "作動油種：高度に精製されたパラフィン系鉱物油に各種酸化防止剤・耐摩耗剤（ZDDP）を添加した最も一般的な汎用耐摩耗性作動油。油種を選定せよ。",
            [("hydraulic_fire_resistant_w_o", "油中水滴型難燃性作動油（W/Oエマルジョン難燃油）"), ("hydraulic_mineral_antiwear_iso", "高引火点鉱物系耐摩耗性作動油（ISO VG32/46）"), ("hydraulic_phosphate_ester", "りん酸エステル系難燃性作動油（合成難燃油）"), ("hydraulic_water_glycol", "水・グリコール系難燃性作動油（水溶性難燃油）"), ("hydraulic_polyol_ester_bio", "ポリオールエステル系生分解性作動油"), ("hydraulic_synthetic_hydrocarbon", "合成炭化水素PAO極低温作動油"), ("hydraulic_silicone_fluid_high_t", "高耐熱シリコーン絶縁作動液"), ("hydraulic_fluorocarbon_inert", "フッ素系超不活性非引火性作動液")],
            "hydraulic_fire_resistant_w_o", "hydraulic_mineral_antiwear_iso"
        ),
        (
            "20",
            "機械工作における切削工具刃先摩耗メカニズム選定。高速加工時の劣化要因を分析する。",
            "摩耗形態：工具すくい面上の切屑擦過部が高温高圧となり、工具材（炭化物）の炭素やコバルトが切屑側へ熱拡散浸透して形成される凹み摩耗。名称を選べ。",
            "摩耗形態：工具逃げ面と被削材仕上げ面との機械的摩擦摩耗により、切れ刃先端に沿って平行に帯状に進行する摩耗。寿命判定の主基準となる。名称を選べ。",
            [("wear_crater_rake_diffusion", "クレーター摩耗（すくい面高温熱拡散凹み摩耗）"), ("wear_flank_relief_abrasion", "逃げ面摩耗（逃げ面アブレシブ摩擦摩耗VB）"), ("wear_built_up_edge_chipping", "構成刃先（溶着剥離チッピング破壊）"), ("wear_thermal_crack_comb", "熱き裂摩耗（熱応力繰返しコームクラック）"), ("wear_notch_depth_cut", "境界摩耗（切込み境界部ノッチ偏摩耗）"), ("wear_plastic_deformation_nose", "ノーズ塑性変形（高温過負荷刃先ダレ）"), ("wear_oxidation_scaling", "高温酸化摩耗（超硬合金酸化膜脆化）"), ("wear_spalling_delamination", "PVD/CVDコーティング膜剥離スポーリング")],
            "wear_crater_rake_diffusion", "wear_flank_relief_abrasion"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k8_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_gen_{gid}_s1",
                "group_id": f"rc3b_gen_{gid}",
                "family": "general_choice",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_gen_{gid}_s2",
                "group_id": f"rc3b_gen_{gid}",
                "family": "general_choice",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2}
            }
        ])

    # --- K=16 (10 pairs: groups 21 to 30) ---
    k16_defs = [
        (
            "21",
            "恒星天文学におけるハーバード天体分光スペクトル分類判定。表面温度と吸収線特徴から恒星のスペクトル型を特定する。",
            "分光観測データ：表面有効温度は約35,000K、中性ヘリウム線や電離ヘリウム（He II）吸収線が明瞭に観測される超高温の青色巨星。スペクトル型を選べ。",
            "分光観測データ：表面有効温度は約5,800K、中性水素線は中程度で中性鉄や電離カルシウムH・K吸収線が顕著な黄色主系列星（太陽型）。スペクトル型を選べ。",
            [
                ("spec_o_type", "O型星（青色超高温）"),
                ("spec_b_early", "B0型星（青白色）"),
                ("spec_b_late", "B5型星（青白主系列）"),
                ("spec_a_early", "A0型星（白色水素線）"),
                ("spec_a_late", "A5型星（白色金属線）"),
                ("spec_f_early", "F0型星（黄白色）"),
                ("spec_f_late", "F5型星（黄白金属線）"),
                ("spec_g_early", "G0型星（黄色）"),
                ("spec_g_sun", "G2型星（黄色主系列太陽型）"),
                ("spec_k_early", "K0型星（橙色）"),
                ("spec_k_late", "K5型星（橙色巨星）"),
                ("spec_m_early", "M0型星（赤色酸化チタン）"),
                ("spec_m_late", "M5型星（赤色矮星）"),
                ("spec_l_dwarf", "L型褐色矮星"),
                ("spec_t_methane", "T型メタン矮星"),
                ("spec_y_ultra_cool", "Y型極低温星")
            ],
            "spec_o_type", "spec_g_sun"
        ),
        (
            "22",
            "材料工学における金属特殊合金および高機能構造材料の選定。耐食性、耐熱性、比強度、加工性を評価する。",
            "材料要求：航空宇宙ガスタービンエンジンの高圧タービンディスクに使用され、650℃の高温下でも極めて優れた耐クリープ破断強度を示すNi基超合金。合金種を選べ。",
            "材料要求：航空機構造材の主翼外板に使用され、亜鉛を主添加元素として時効硬化させた最高強度レベルのアルミニウム合金（超々ジュラルミン）。合金種を選べ。",
            [
                ("alloy_sus304_austenitic", "SUS304（18Cr-8Ni鋼）"),
                ("alloy_sus316l_low_carbon", "SUS316L（耐孔食鋼）"),
                ("alloy_ti6al4v_alpha_beta", "Ti-6Al-4V（チタン合金）"),
                ("alloy_inconel_718_super", "Inconel 718（Ni基超合金）"),
                ("alloy_hastelloy_c276_corrosion", "Hastelloy C-276（耐食合金）"),
                ("alloy_a7075_t6_duralumin", "A7075-T6（超々ジュラルミン）"),
                ("alloy_a6061_t6_structural", "A6061-T6（耐食アルミ合金）"),
                ("alloy_scm440_chromo_steel", "SCM440（クロモリ鋼）"),
                ("alloy_skd11_tool_die", "SKD11（冷間金型鋼）"),
                ("alloy_c1100_tough_copper", "C1100（タフピッチ銅）"),
                ("alloy_cube25_beryllium_cu", "Cu-Be25（ベリリウム銅）"),
                ("alloy_az31b_magnesium_sheet", "AZ31B（マグネシウム合金）"),
                ("alloy_nitinol_shape_memory", "Ni-Ti Nitinol（形状記憶合金）"),
                ("alloy_monel_400_marine", "Monel 400（海洋耐食合金）"),
                ("alloy_stellite_6_cobalt_hard", "Stellite 6（Co基耐摩耗合金）"),
                ("alloy_maraging_steel_250", "マレージング鋼（超高張力鋼）")
            ],
            "alloy_inconel_718_super", "alloy_a7075_t6_duralumin"
        ),
        (
            "23",
            "情報通信ネットワークにおけるプロトコルスタックの機能選定。ルーティング、トンネリング、シグナリング機能を識別する。",
            "プロトコル要件：自律システム（AS）間を接続するEGPであり、パス属性（AS-PATH）を用いてルーティングループを防止するインターネット基幹プロトコル。プロトコルを選べ。",
            "プロトコル要件：データセンターオーバーレイネットワークにおいて、L2イーサネットフレームをL3/UDPパケットでカプセル化して論理網を延伸するプロトコル。プロトコルを選べ。",
            [
                ("proto_bgp4_exterior", "BGP-4（外部GWプロトコル）"),
                ("proto_ospfv3_link_state", "OSPFv3（リンクステートIGP）"),
                ("proto_isis_clnp_igp", "IS-IS（中間システムIGP）"),
                ("proto_eigrp_cisco_dual", "EIGRP（拡張距離ベクトル）"),
                ("proto_ripng_distance_vector", "RIPng（距離ベクトル型）"),
                ("proto_ldp_mpls_label", "LDP（ラベル配布プロトコル）"),
                ("proto_rsvp_te_traffic_eng", "RSVP-TE（帯域予約プロトコル）"),
                ("proto_vxlan_udp_overlay", "VXLAN（UDPトンネリング）"),
                ("proto_evpn_control_plane", "EVPN（Ethernet VPN）"),
                ("proto_vrrp_router_redundancy", "VRRP（ルータ冗長プロトコル）"),
                ("proto_lacp_ieee8023ad", "LACP（リンクアグリゲーション）"),
                ("proto_pim_sm_multicast", "PIM-SM（マルチキャスト）"),
                ("proto_igmpv3_host_multicast", "IGMPv3（グループ管理）"),
                ("proto_lldp_topology_discover", "LLDP（隣接機器探索）"),
                ("proto_snmpv3_network_manage", "SNMPv3（暗号監視プロトコル）"),
                ("proto_radius_aaa_auth", "RADIUS（認証認可サービス）")
            ],
            "proto_bgp4_exterior", "proto_vxlan_udp_overlay"
        ),
        (
            "24",
            "量子エレクトロニクスにおけるレーザー媒質および発振波長の選定。産業・医療・半導体加工用途を特定する。",
            "レーザー選定：先端半導体ArF液浸露光装置の光源として使用される発振波長193nmの深紫外線希ガスハロゲンレーザー。レーザー種を選定せよ。",
            "レーザー選定：炭酸ガスレーザー（CO2レーザー）の特徴的波長であり、波長10.6μmの遠赤外線によりアクリル樹脂切断や厚鋼板溶接に広く用いられる光源。波長を選定せよ。",
            [
                ("laser_hene_632_red", "He-Ne（632.8nm赤色）"),
                ("laser_ndyag_1064_ir", "Nd:YAG（1064nm近赤外）"),
                ("laser_tisapphire_800_femt", "Ti:サファイア（800nm短パルス）"),
                ("laser_ar_ion_488_cyan", "Arイオン（488nmシアン）"),
                ("laser_krf_248_duv", "KrFエキシマ（248nm深紫外）"),
                ("laser_arf_193_duv_immersion", "ArFエキシマ（193nm液浸露光）"),
                ("laser_co2_10600_far_ir", "CO2（10.6μm遠赤外）"),
                ("laser_eryag_2940_dental", "Er:YAG（2940nm歯科医療）"),
                ("laser_fiber_yb_1030_sheet", "Ybファイバー（1030nm板金）"),
                ("laser_ingan_405_bluray", "InGaN（405nm青紫色）"),
                ("laser_gaas_850_vcsel", "GaAs（850nm光通信）"),
                ("laser_hoyag_2100_holmium", "Ho:YAG（2100nm結石破砕）"),
                ("laser_ruby_694_historical", "ルビー（694.3nm固体）"),
                ("laser_n2_337_uv_pulse", "窒素パルス（337nm紫外）"),
                ("laser_alexandrite_755_hair", "アレキサンドライト（755nm医療）"),
                ("laser_dye_rhodamine_590", "色素ローダミン6G（可変波長）")
            ],
            "laser_arf_193_duv_immersion", "laser_co2_10600_far_ir"
        ),
        (
            "25",
            "機械構造物における接合工法の選定。強度、気密性、分解可能性、熱影響を評価する。",
            "工法要件：回転ツールをアルミ合金突合せ部に圧入・移動させ、材料を溶融させずに塑性流動摩擦熱で強固に固相接合する新幹線構体工法。工法を選べ。",
            "工法要件：高張力ボルトを所定の締付けトルクで導入し、部材接触面間の摩擦抵抗力によってせん断力を伝達する建築鉄骨工法。工法を選べ。",
            [
                ("joint_butt_weld_groove", "開先突合せアーク溶接"),
                ("joint_lap_fillet_weld", "重ね隅肉溶接"),
                ("joint_tee_fillet_joint", "T形隅肉溶接"),
                ("joint_corner_groove_weld", "角継手溝溶接"),
                ("joint_edge_flange_weld", "へり継手溶接"),
                ("joint_fsw_friction_stir", "摩擦攪拌接合（FSW）"),
                ("joint_blind_structural_rivet", "ブラインドリベット締結"),
                ("joint_high_tensile_friction_bolt", "高力ボルト摩擦接合"),
                ("joint_precision_dowel_pin", "焼入れノックピン位置決め"),
                ("joint_cotter_wedge_pin", "コッターピン楔継手"),
                ("joint_involute_spline_shaft", "インボリュートスプライン軸"),
                ("joint_parallel_keyway_drive", "平行キー溝締結"),
                ("joint_snap_fit_cantilever", "カンチレバースナップフィット"),
                ("joint_interference_press_fit", "しまりばめ圧入接合"),
                ("joint_structural_epoxy_bond", "構造用エポキシ接着接合"),
                ("joint_bolted_flange_gasket", "ボルト締めフランジガスケット")
            ],
            "joint_fsw_friction_stir", "joint_high_tensile_friction_bolt"
        ),
        (
            "26",
            "生化学における国際生化学・分子生物学連合（IUBMB）EC番号酵素分類選定。触媒反応形式を同定する。",
            "酵素機能：ATP等の高エネルギーリン酸結合の加水分解エネルギーを利用することなく、基質から原子団を非加水分解的に脱離させて二重結合を生成する酵素群。EC分類を選べ。",
            "酵素機能：ATPなどのヌクレオシド三リン酸の切断に共役して、2つの分子を共有結合で連結（合成）する酵素群。EC分類を選べ。",
            [
                ("enzyme_ec1_oxidoreductase", "EC 1：酸化還元酵素"),
                ("enzyme_ec2_transferase", "EC 2：転移酵素"),
                ("enzyme_ec3_hydrolase", "EC 3：加水分解酵素"),
                ("enzyme_ec4_lyase_elimination", "EC 4：脱離酵素（リアーゼ）"),
                ("enzyme_ec5_isomerase_convert", "EC 5：異性化酵素"),
                ("enzyme_ec6_ligase_atp_synth", "EC 6：合成酵素（リガーゼ）"),
                ("enzyme_ec7_translocase_ion", "EC 7：輸送酵素"),
                ("enzyme_sub_protein_kinase", "プロテインキナーゼ"),
                ("enzyme_sub_phosphatase_hydro", "ホスファターゼ"),
                ("enzyme_sub_dna_polymerase", "DNAポリメラーゼ"),
                ("enzyme_sub_serine_protease", "セリンプロテアーゼ"),
                ("enzyme_sub_triacylglycerol_lipase", "リパーゼ"),
                ("enzyme_sub_alpha_amylase", "α-アミラーゼ"),
                ("enzyme_sub_alcohol_dehydrogenase", "アルコール脱水素酵素"),
                ("enzyme_sub_dna_methyltransferase", "DNAメチルトランスフェラーゼ"),
                ("enzyme_sub_amino_acid_decarboxylase", "アミノ酸脱炭酸酵素")
            ],
            "enzyme_ec4_lyase_elimination", "enzyme_ec6_ligase_atp_synth"
        ),
        (
            "27",
            "クラウドインフラストラクチャにおける仮想マシンインスタンスファミリー選定。ワークロード要件に最適化する。",
            "負荷要件：数億行の大規模インメモリデータベース（Redis/SAP HANA）を常駐させるため、vCPU数に対して超大容量のRAM帯域とメモリ容量を最優先とするインスタンス型。選定せよ。",
            "負荷要件：LLMの大規模深層学習モデルの並列分散トレーニングを実行するため、最新の高性能テンソルコアGPUと広帯域NVLinkを備えたインスタンス型。選定せよ。",
            [
                ("cloud_inst_general_purpose", "汎用インスタンス（M系）"),
                ("cloud_inst_compute_optimized", "コンピュート最適化（C系）"),
                ("cloud_inst_memory_optimized", "メモリ最適化（R系）"),
                ("cloud_inst_accelerated_gpu", "GPUアクセラレーテッド（P系）"),
                ("cloud_inst_storage_optimized", "ストレージ最適化（I系）"),
                ("cloud_inst_hpc_interconnect", "HPCクラスター（Hpc系）"),
                ("cloud_inst_arm_graviton", "Armインスタンス（Graviton系）"),
                ("cloud_inst_fpga_custom_logic", "FPGAアクセラレータ（F系）"),
                ("cloud_inst_bare_metal_direct", "ベアメタルインスタンス"),
                ("cloud_inst_burstable_t_credits", "バースト可能（T系）"),
                ("cloud_inst_quantum_braket_sim", "量子回路エミュレータ"),
                ("cloud_inst_network_bandwidth_100g", "ネットワーク特化（100Gbps）"),
                ("cloud_inst_dense_local_storage", "高密度ストレージ（D系）"),
                ("cloud_inst_high_memory_terabytes", "超巨大メモリ（U系）"),
                ("cloud_inst_ml_inference_inferentia", "推論特化ASIC（Inferentia系）"),
                ("cloud_inst_confidential_computing", "コンフィデンシャル隔離")
            ],
            "cloud_inst_memory_optimized", "cloud_inst_accelerated_gpu"
        ),
        (
            "28",
            "国際航路標識協会（IALA）海上浮標式における航路標識ブイ選定。水路障害物の回避方位および安全水域を示す。",
            "水標意味：障害物の北側に設置され、標識の北側が通航可能水域（安全側）であることを示す頭標（黒色上向き三角2個）の頭標を持つ方位標識。選定せよ。",
            "水標意味：航路の安全な中心線または中央部を示し、周囲の全水域が航行可能であることを示す赤白縦縞模様の安全水域標識。選定せよ。",
            [
                ("iala_cardinal_north", "北方位標識（黒黄黒）"),
                ("iala_cardinal_south", "南方位標識（黄黒）"),
                ("iala_cardinal_east", "東方位標識（黒黄黒対向）"),
                ("iala_cardinal_west", "西方位標識（黄黒黄頂点）"),
                ("iala_port_lateral_mark", "左舷標識（円筒形）"),
                ("iala_starboard_lateral_mark", "右舷標識（円錐形）"),
                ("iala_preferred_channel_port", "主航路左舷優先標識"),
                ("iala_preferred_channel_starboard", "主航路右舷優先標識"),
                ("iala_isolated_danger_mark", "孤立障害標識（黒赤黒）"),
                ("iala_safe_water_fairway", "安全水域標識（赤白縦縞）"),
                ("iala_special_mark_yellow", "特殊標識（黄色X頭標）"),
                ("iala_emergency_wreck_marking", "新沈船応急標識（青黄縦縞）"),
                ("iala_anchorage_boundary_mark", "錨泊地境界標識"),
                ("iala_military_exercise_zone", "演習区域制限標識"),
                ("iala_submarine_cable_reserve", "海底ケーブル保護標識"),
                ("iala_marine_nature_sanctuary", "海洋環境保護区標識")
            ],
            "iala_cardinal_north", "iala_safe_water_fairway"
        ),
        (
            "29",
            "分離分析化学におけるクロマトグラフィー固定相分離モード選定。化合物極性と分離メカニズムを評価する。",
            "分離モード：シリカゲル担体にオクタデシル基（C18）を化学結合させた非極性固定相を用い、水-有機溶媒移動相により化合物の疎水性の強さに応じて保持する最も一般的なモード。選定せよ。",
            "分離モード：多孔性ゲル粒子が充填されたカラムに高分子ポリマー溶液を通液し、分子サイズの大きい成分ほど空孔に入り込めず早く溶出するサイズ分画モード。選定せよ。",
            [
                ("chrom_reversed_phase_c18", "逆相HPLC（ODS/C18）"),
                ("chrom_normal_phase_silica", "順相クロマト（シリカ）"),
                ("chrom_anion_exchange_wax", "陰イオン交換（WAX）"),
                ("chrom_cation_exchange_scx", "陽イオン交換（SCX）"),
                ("chrom_size_exclusion_sec", "サイズ排除（SEC/GPC）"),
                ("chrom_hydrophobic_interaction_hic", "疎水性相互作用（HIC）"),
                ("chrom_affinity_protein_a", "アフィニティ（プロテインA）"),
                ("chrom_hilic_hydrophilic_polar", "親水性相互作用（HILIC）"),
                ("chrom_chiral_optical_isomer", "キラル固定相クロマト"),
                ("chrom_supercritical_fluid_sfc", "超臨界流体（SFC）"),
                ("chrom_gas_liquid_partition_gc", "気液分配ガスクロマト"),
                ("chrom_thin_layer_tlc_plate", "薄層クロマト（TLC）"),
                ("chrom_capillary_electrophoresis", "キャピラリー電気泳動"),
                ("chrom_mixed_mode_rp_ion", "ミックスモード（RP+IEX）"),
                ("chrom_imac_metal_chelating", "固定化金属アフィニティ（IMAC）"),
                ("chrom_gel_permeation_solvent", "ゲル浸透クロマト（GPC）")
            ],
            "chrom_reversed_phase_c18", "chrom_size_exclusion_sec"
        ),
        (
            "30",
            "地盤工学および土質力学における統一土質分類（USCS）土質区分選定。粒度分布と塑性指数を評価する。",
            "土質分類：細粒分が5%未満の砂質土であり、均等係数Cuが6以上かつ曲率係数Ccが1〜3の範囲にあって粒径が均等に混在し締固め性に優れた砂。分類群を選定せよ。",
            "土質分類：塑性図においてA線の上側に位置し、液性限界wLが50%以上である塑性・圧縮性の極めて高い高塑性無機質粘土。分類群を選定せよ。",
            [
                ("soil_gw_well_graded_gravel", "GW（粒度良好礫）"),
                ("soil_gp_poorly_graded_gravel", "GP（粒度不良礫）"),
                ("soil_gm_silty_gravel", "GM（シルト質礫）"),
                ("soil_gc_clayey_gravel", "GC（粘土質礫）"),
                ("soil_sw_well_graded_sand", "SW（粒度良好砂）"),
                ("soil_sp_poorly_graded_sand", "SP（粒度不良砂）"),
                ("soil_sm_silty_sand", "SM（シルト質砂）"),
                ("soil_sc_clayey_sand", "SC（粘土質砂）"),
                ("soil_ml_low_plastic_silt", "ML（低塑性シルト）"),
                ("soil_mh_high_plastic_silt", "MH（高塑性シルト）"),
                ("soil_cl_low_plastic_clay", "CL（低塑性粘土）"),
                ("soil_ch_high_plastic_clay", "CH（高塑性粘土）"),
                ("soil_ol_organic_silt_clay", "OL（有機質シルト・粘土）"),
                ("soil_oh_organic_high_plastic", "OH（有機質高塑性粘土）"),
                ("soil_pt_peat_fibrous_bog", "Pt（泥炭ピート）"),
                ("soil_rock_sound_granite", "Sound Rock（健全岩盤）")
            ],
            "soil_sw_well_graded_sand", "soil_ch_high_plastic_clay"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k16_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_gen_{gid}_s1",
                "group_id": f"rc3b_gen_{gid}",
                "family": "general_choice",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_gen_{gid}_s2",
                "group_id": f"rc3b_gen_{gid}",
                "family": "general_choice",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2}
            }
        ])

    return pairs
