"""Family 7: variable_choice (30 pairs, 60 cases) - Blind v4
Distribution: K=6 (5 pairs), K=8 (5 pairs), K=12 (10 pairs), K=16 (10 pairs)
Prefix: rc2b4_var_
Zero inference during authoring; 100% fresh scenarios.
Concise choice texts for K=12 and K=16 to guarantee strict token count <= 350.
"""

from typing import Any, Dict, List, Tuple


def make_choices(c_defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in c_defs]


def get_variable_choice_pairs() -> List[Dict[str, Any]]:
    pairs = []

    # --- K=6 (5 pairs: groups 01 to 05) ---
    k6_defs = [
        (
            "01",
            "救急隊の現場トリアージ判定に基づく最適搬送先医療機関の選定タスク。",
            "傷病者状況：『妊娠32週の妊婦が突然の激しい腹痛と大量性器出血を呈し胎児心拍急減が疑われる』。搬送先を特定せよ。",
            "傷病者状況：『突然の激しい頭痛とともに左半身麻痺が出現し、瞳孔不同を伴う急性脳内出血が強く疑われる』。搬送先を特定せよ。",
            [
                ("hosp_perinatal_center", "総合周産期母子医療センター"),
                ("hosp_stroke_center", "脳卒中急性期専門拠点病院"),
                ("hosp_trauma_icu", "高度救命救急外傷センター"),
                ("hosp_pediatric_emergency", "小児救命救急専門病院"),
                ("hosp_infectious_disease", "特定感染症指定医療機関"),
                ("hosp_local_clinic", "地域休日夜間急患診療所")
            ],
            "hosp_perinatal_center", "hosp_stroke_center"
        ),
        (
            "02",
            "マイクロサービス運用環境におけるコンテナポッド障害復旧アクションの決定タスク。",
            "監視アラート：『新バージョンデプロイ直後から全ポッドでクラッシュループ（CrashLoopBackOff）が多発している』。初動措置を特定せよ。",
            "監視アラート：『特定ワーカーノードのハードウェア障害により、稼働中ポッドを別ノードへ退避させる必要がある』。初動措置を特定せよ。",
            [
                ("k8s_rollback_version", "直前安定版イメージへのロールバック"),
                ("k8s_drain_node", "障害ノードの安全退避ドレイン（Drain）"),
                ("k8s_restart_pod_only", "ポッドの即時強制再起動"),
                ("k8s_scale_replicas_double", "レプリカ数の倍加スケールアウト"),
                ("k8s_block_ingress_traffic", "イングラストラフィックの完全遮断"),
                ("k8s_expand_cpu_limits", "CPUリソース上限の動的緩和")
            ],
            "k8s_rollback_version", "k8s_drain_node"
        ),
        (
            "03",
            "自動車メーカーにおける不具合事象に基づく対象リコール重点部位の特定タスク。",
            "不具合報告：『ステアリング操作時に異音とともに急激にアシスト力が喪失し操舵が重篤に困難となる』。不具合部位を特定せよ。",
            "不具合報告：『ブレーキペダルを踏み込んでも踏力が伝わらず、制動距離が異常に著しく増大する』。不具合部位を特定せよ。",
            [
                ("auto_part_eps_steering", "電動パワーステアリングアクチュエータ"),
                ("auto_part_brake_booster", "電子制御ブレーキ倍力マスターシリンダ"),
                ("auto_part_fuel_pump", "高圧直噴燃料ポンプ"),
                ("auto_part_airbag_igniter", "運転席側エアバッグ展開インフレーター"),
                ("auto_part_transmission_tcu", "無段変速機制御バルブボディ"),
                ("auto_part_door_latch", "後席スライドドア電気ラッチ機構")
            ],
            "auto_part_eps_steering", "auto_part_brake_booster"
        ),
        (
            "04",
            "鉄道高架橋梁脚部の耐震補強工事における最適施工工法の選定タスク。",
            "設計条件：『狭小地で重機の搬入が不可能な高架下において、橋脚のじん性を高め曲げ破壊を防止する』。工法を特定せよ。",
            "設計条件：『直下型巨大地震の地震動を根本から減衰・絶縁し、上部構造への地震力入力を遮断する』。工法を特定せよ。",
            [
                ("reinforce_carbon_fiber_wrap", "炭素繊維シート連続巻立補強工法"),
                ("reinforce_seismic_isolation", "免震ゴム支承への支承交換免震化工法"),
                ("reinforce_steel_jacket", "鋼板巻立モルタル注入補強工法"),
                ("reinforce_shear_wall", "鉄骨ブレース増設耐震壁新設工法"),
                ("reinforce_external_frame", "外付け鉄骨フレーム架台増設工法"),
                ("reinforce_damper_bracing", "粘性減衰ダンパー制震ブレース工法")
            ],
            "reinforce_carbon_fiber_wrap", "reinforce_seismic_isolation"
        ),
        (
            "05",
            "無人航空機（産業用大型ドローン）の運用電波帯域の選定タスク。",
            "通信要件：『山間僻地や長距離Beyond Visual Line of Sight（目視外飛行）において、遮蔽物に強い920MHz帯で高信頼性テレメトリを行う』。電波帯を特定せよ。",
            "通信要件：『電波不感地帯の上空において、軌道上の通信衛星ネットワークを中継して地球規模で直接管制制御を行う』。電波帯を特定せよ。",
            [
                ("drone_radio_920mhz", "920MHz特定小電力テレメトリ帯"),
                ("drone_radio_satellite", "衛星通信コンステレーション中継帯"),
                ("drone_radio_2_4ghz_ism", "2.4GHz産業科学医療ISMバンド"),
                ("drone_radio_5_7ghz_pro", "5.7GHz無人移動体画像伝送専用帯"),
                ("drone_radio_5_8ghz_fpv", "5.8GHzホビー用アナログFPV帯"),
                ("drone_radio_169mhz_vhf", "169MHz防災テレメータVHF帯")
            ],
            "drone_radio_920mhz", "drone_radio_satellite"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k6_defs:
        pairs.append({
            "id": f"rc2b4_var_{gid}_s1", "group_id": f"rc2b4_var_{gid}", "family": "variable_choice",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_var_{gid}_s2", "group_id": f"rc2b4_var_{gid}", "family": "variable_choice",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=8 (5 pairs: groups 06 to 10) ---
    k8_defs = [
        (
            "06",
            "半導体シリコンウェハ前工程（フロントエンド）の基幹製造プロセスの特定タスク。",
            "工程内容：『フォトマスクの微細回路パターンを感光性レジスト膜へ紫外線光照射により転写焼き付けする』。工程を特定せよ。",
            "工程内容：『レジストで保護されていない露出絶縁膜やシリコン層を反応性プラズマガスで選択的に削り取る』。工程を特定せよ。",
            [
                ("semi_step_photolithography", "フォトリソグラフィ露光転写工程"),
                ("semi_step_dry_etching", "ドライエッチングプラズマ微細加工工程"),
                ("semi_step_wafer_cleaning", "ウェハ薬液超純水洗浄工程"),
                ("semi_step_thermal_oxidation", "高温熱酸化膜形成工程"),
                ("semi_step_ion_implantation", "不純物ドーピングイオン注入工程"),
                ("semi_step_cvd_deposition", "CVD化学気相成長薄膜堆積工程"),
                ("semi_step_cmp_polishing", "CMP化学機械平坦化研磨工程"),
                ("semi_step_dicing_singulation", "ウェハダイシングチップ個片化工程")
            ],
            "semi_step_photolithography", "semi_step_dry_etching"
        ),
        (
            "07",
            "金属材料における代表的な腐食形態の診断特定タスク。",
            "腐食性状：『ステンレス鋼表面の不働態皮膜が塩素イオンにより局所破壊され、微小な針穴状の深い穴あきが発生する』。腐食を特定せよ。",
            "腐食性状：『引張応力を受けている金属部材が特定の腐食環境下において、脆性的にき裂が進展し突然破断に至る』。腐食を特定せよ。",
            [
                ("corrosion_pitting", "孔食（点食・局部浸食）"),
                ("corrosion_stress_cracking", "応力腐食割れ（SCC）"),
                ("corrosion_general_uniform", "全面腐食（均一減肉）"),
                ("corrosion_crevice", "すき間腐食"),
                ("corrosion_intergranular", "粒界腐食（結晶粒界浸食）"),
                ("corrosion_galvanic_bimetallic", "ガルバニック腐食（異種金属接触）"),
                ("corrosion_erosion", "エロージョン・コロージョン"),
                ("corrosion_hydrogen_embrittlement", "水素脆化割れ")
            ],
            "corrosion_pitting", "corrosion_stress_cracking"
        ),
        (
            "08",
            "産業廃棄物処理マニフェスト（産業廃棄物管理票）における法定廃棄物種類の分類タスク。",
            "廃棄物性状：『石炭火力発電所の集塵装置で捕集された石炭灰や焼却炉底から排出される焼却残渣灰』。法定区分を特定せよ。",
            "廃棄物性状：『金属部品の脱脂洗浄工程から排出されるトリクロロエチレンや廃シンナーなどの油状液体』。法定区分を特定せよ。",
            [
                ("waste_cinder_ash", "燃え殻（焼却残渣・灰）"),
                ("waste_oil_sludge", "廃油（鉱物油・動植物油）"),
                ("waste_sludge_mud", "汚泥（有機・無機汚泥）"),
                ("waste_acid_liquid", "廃酸（強酸・弱酸廃液）"),
                ("waste_alkali_liquid", "廃アルカリ（アルカリ廃液）"),
                ("waste_plastics_polymer", "廃プラスチック類"),
                ("waste_scrap_metal", "金属くず"),
                ("waste_glass_concrete", "ガラスくず・コンクリートくず")
            ],
            "waste_cinder_ash", "waste_oil_sludge"
        ),
        (
            "09",
            "東海道・山陽新幹線の主要ターミナル駅における停車・配線機能の特定タスク。",
            "駅の特徴：『日本最大の鉄道ターミナルであり、東海道新幹線の起点として全列車が始発・終着する駅』。駅名を特定せよ。",
            "駅の特徴：『東海道新幹線と山陽新幹線の相互直通運転の結節点であり、大阪府下のターミナル駅』。駅名を特定せよ。",
            [
                ("shinkansen_tokyo", "東京駅"),
                ("shinkansen_shin_osaka", "新大阪駅"),
                ("shinkansen_shin_yokohama", "新横浜駅"),
                ("shinkansen_nagoya", "名古屋駅"),
                ("shinkansen_kyoto", "京都駅"),
                ("shinkansen_shin_kobe", "新神戸駅"),
                ("shinkansen_okayama", "岡山駅"),
                ("shinkansen_hakata", "博多駅")
            ],
            "shinkansen_tokyo", "shinkansen_shin_osaka"
        ),
        (
            "10",
            "航空機整備における安全インシデントの重大度ランク付けタスク。",
            "事象：飛行中に両エンジンが完全停止し、緊急着陸を余儀なくされた重大インシデント。重大度ランクを特定せよ。",
            "事象：地上駐機中の定期点検において客室読書灯の球切れが発見され、即座に交換された軽微事象。重大度ランクを特定せよ。",
            [
                ("incident_rank_critical_a", "ランクA（破局的重大インシデント）"),
                ("incident_rank_minor_h", "ランクH（定常軽微保守事象）"),
                ("incident_rank_severe_b", "ランクB（深刻障害インシデント）"),
                ("incident_rank_major_c", "ランクC（主要機能停止インシデント）"),
                ("incident_rank_moderate_d", "ランクD（中度運用制限インシデント）"),
                ("incident_rank_low_e", "ランクE（軽度注意事象）"),
                ("incident_rank_negligible_f", "ランクF（影響極小事象）"),
                ("incident_rank_info_g", "ランクG（記録のみ情報事象）")
            ],
            "incident_rank_critical_a", "incident_rank_minor_h"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k8_defs:
        pairs.append({
            "id": f"rc2b4_var_{gid}_s1", "group_id": f"rc2b4_var_{gid}", "family": "variable_choice",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_var_{gid}_s2", "group_id": f"rc2b4_var_{gid}", "family": "variable_choice",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=12 (10 pairs: groups 11 to 20) Concise choices! ---
    k12_defs = [
        (
            "11",
            "十二平均律音楽理論におけるクロマチック半音階の音名同定タスク。",
            "音階位置：国際標準ピッチ440Hzに設定される基底音ラ（A音）を特定せよ。",
            "音階位置：ピアノ鍵盤中央の基準ハ音であるド（C音）を特定せよ。",
            [
                ("pitch_a", "A音（ラ）"),
                ("pitch_c", "C音（ド）"),
                ("pitch_c_sharp", "C#音（ド#）"),
                ("pitch_d", "D音（レ）"),
                ("pitch_d_sharp", "D#音（レ#）"),
                ("pitch_e", "E音（ミ）"),
                ("pitch_f", "F音（ファ）"),
                ("pitch_f_sharp", "F#音（ファ#）"),
                ("pitch_g", "G音（ソ）"),
                ("pitch_g_sharp", "G#音（ソ#）"),
                ("pitch_a_sharp", "A#音（ラ#）"),
                ("pitch_b", "B音（シ）")
            ],
            "pitch_a", "pitch_c"
        ),
        (
            "12",
            "電子部品固定抵抗器のカラーコード識別タスク。",
            "色帯表示：抵抗値の第1有効数字が『1』を表すカラー帯色を特定せよ。",
            "色帯表示：抵抗値の第1有効数字が『0』を表すカラー帯色を特定せよ。",
            [
                ("res_color_brown", "茶色（数値1）"),
                ("res_color_black", "黒色（数値0）"),
                ("res_color_red", "赤色（数値2）"),
                ("res_color_orange", "橙色（数値3）"),
                ("res_color_yellow", "黄色（数値4）"),
                ("res_color_green", "緑色（数値5）"),
                ("res_color_blue", "青色（数値6）"),
                ("res_color_violet", "紫色（数値7）"),
                ("res_color_gray", "灰色（数値8）"),
                ("res_color_white", "白色（数値9）"),
                ("res_color_gold", "金色（誤差5%）"),
                ("res_color_silver", "銀色（誤差10%）")
            ],
            "res_color_brown", "res_color_black"
        ),
        (
            "13",
            "有機化学における主要な官能基の構造同定タスク。",
            "構造特徴：酸素と水素が結合した『-OH』構造を持ち、アルコール類を構成する官能基を特定せよ。",
            "構造特徴：カルボニル炭素に窒素が直結した『-CONH2』構造を持つ官能基を特定せよ。",
            [
                ("func_hydroxyl", "ヒドロキシ基"),
                ("func_amide", "アミド結合"),
                ("func_carboxyl", "カルボキシ基"),
                ("func_amino", "アミノ基"),
                ("func_aldehyde", "アルデヒド基"),
                ("func_ketone", "ケトン基"),
                ("func_ester", "エステル結合"),
                ("func_ether", "エーテル結合"),
                ("func_nitro", "ニトロ基"),
                ("func_sulfo", "スルホ基"),
                ("func_thiol", "チオール基"),
                ("func_cyano", "シアノ基")
            ],
            "func_hydroxyl", "func_amide"
        ),
        (
            "14",
            "機械工作における切削工具インサートチップ材質の特定タスク。",
            "材質特性：炭化タングステン粒子をコバルトで焼結結合した、現代切削の標準工具材質を特定せよ。",
            "材質特性：ダイヤモンドに次ぐ硬度を持ち、焼入れ鋼の高速仕上げ切削に用いられる人工材質を特定せよ。",
            [
                ("insert_carbide", "超硬合金"),
                ("insert_cbn", "立方晶窒化ホウ素CBN"),
                ("insert_high_speed_steel", "高速度鋼ハイス"),
                ("insert_coated_carbide", "コーテッド超硬"),
                ("insert_cermet", "サーメット"),
                ("insert_ceramics", "アルミナ系セラミックス"),
                ("insert_pcd_diamond", "多結晶ダイヤモンドPCD"),
                ("insert_sapphire", "単結晶サファイア"),
                ("insert_stellite", "ステライト合金"),
                ("insert_silicon_nitride", "窒化ケイ素セラミックス"),
                ("insert_sialon", "サイアロン耐熱工具"),
                ("insert_whisker", "ウィスカー強化複合工具")
            ],
            "insert_carbide", "insert_cbn"
        ),
        (
            "15",
            "ネットワーク通信プロトコルの階層機能同定タスク。",
            "プロトコル機能：安全なシェル接続と暗号化トンネリングを提供する遠隔操作プロトコルを特定せよ。",
            "プロトコル機能：ドメイン名とIPアドレスの相互名前解決を行う基幹プロトコルを特定せよ。",
            [
                ("proto_ssh", "SSH（セキュアシェル）"),
                ("proto_dns", "DNS（名前解決）"),
                ("proto_http", "HTTP"),
                ("proto_https", "HTTPS"),
                ("proto_ftp", "FTP"),
                ("proto_smtp", "SMTP"),
                ("proto_imap", "IMAP"),
                ("proto_snmp", "SNMP"),
                ("proto_ntp", "NTP"),
                ("proto_dhcp", "DHCP"),
                ("proto_mqtt", "MQTT"),
                ("proto_websocket", "WebSocket")
            ],
            "proto_ssh", "proto_dns"
        ),
        (
            "16",
            "ビューフォート風力階級（風の強さの尺度）の判定タスク。",
            "風況：煙がまっすぐに昇り、風速0.3m/s未満の完全な静穏状態である風力階級を特定せよ。",
            "風況：陸上では大木が根こそぎ倒れ、家屋に大被害が生じる風速32.7m/s以上の最強階級を特定せよ。",
            [
                ("beaufort_0_calm", "風力0（静穏・平穏）"),
                ("beaufort_12_hurricane", "風力12（壊滅的台風暴風）"),
                ("beaufort_1_light_air", "風力1（至軽風）"),
                ("beaufort_2_light_breeze", "風力2（軽風）"),
                ("beaufort_3_gentle_breeze", "風力3（軟風）"),
                ("beaufort_4_moderate_breeze", "風力4（和風）"),
                ("beaufort_5_fresh_breeze", "風力5（疾風）"),
                ("beaufort_6_strong_breeze", "風力6（雄風）"),
                ("beaufort_7_near_gale", "風力7（強風）"),
                ("beaufort_8_gale", "風力8（疾強風）"),
                ("beaufort_9_strong_gale", "風力9（大強風）"),
                ("beaufort_10_storm", "風力10（暴風・全強風）")
            ],
            "beaufort_0_calm", "beaufort_12_hurricane"
        ),
        (
            "17",
            "ISO標準メートル並目ねじの呼び径サイズ照合タスク。",
            "規格値：呼び径6mm、標準ピッチ1.0mmの並目ねじ規格を特定せよ。",
            "規格値：呼び径12mm、標準ピッチ1.75mmの並目ねじ規格を特定せよ。",
            [
                ("metric_thread_m6", "M6並目ねじ"),
                ("metric_thread_m12", "M12並目ねじ"),
                ("metric_thread_m2", "M2並目ねじ"),
                ("metric_thread_m3", "M3並目ねじ"),
                ("metric_thread_m4", "M4並目ねじ"),
                ("metric_thread_m5", "M5並目ねじ"),
                ("metric_thread_m8", "M8並目ねじ"),
                ("metric_thread_m10", "M10並目ねじ"),
                ("metric_thread_m14", "M14並目ねじ"),
                ("metric_thread_m16", "M16並目ねじ"),
                ("metric_thread_m20", "M20並目ねじ"),
                ("metric_thread_m24", "M24並目ねじ")
            ],
            "metric_thread_m6", "metric_thread_m12"
        ),
        (
            "18",
            "光ファイバー多心ケーブルの識別カラーコード同定タスク。",
            "心線色：JIS規格多心光ファイバーコードで第1番心線に割り当てられる色を特定せよ。",
            "心線色：JIS規格多心光ファイバーコードで第2番心線に割り当てられる色を特定せよ。",
            [
                ("fiber_color_blue", "青（第1心線）"),
                ("fiber_color_yellow", "黄（第2心線）"),
                ("fiber_color_green", "緑（第3心線）"),
                ("fiber_color_red", "赤（第4心線）"),
                ("fiber_color_purple", "紫（第5心線）"),
                ("fiber_color_white", "白（第6心線）"),
                ("fiber_color_brown", "茶（第7心線）"),
                ("fiber_color_black", "黒（第8心線）"),
                ("fiber_color_gray", "灰（第9心線）"),
                ("fiber_color_cyan", "水（第10心線）"),
                ("fiber_color_pink", "桃（第11心線）"),
                ("fiber_color_orange", "橙（第12心線）")
            ],
            "fiber_color_blue", "fiber_color_yellow"
        ),
        (
            "19",
            "海上衝突予防法における船舶航行灯火信号の識別タスク。",
            "灯火配置：夜間航行中の動力船において、左舷（ポートサイド）側に表示が義務付けられている灯火の色を特定せよ。",
            "灯火配置：夜間航行中の動力船において、右舷（スターボードサイド）側に表示が義務付けられている灯火の色を特定せよ。",
            [
                ("nav_light_port_red", "左舷灯（紅・赤色）"),
                ("nav_light_starboard_green", "右舷灯（緑色）"),
                ("nav_light_masthead_white", "マスト灯（白色前方）"),
                ("nav_light_stern_white", "船尾灯（白色後方）"),
                ("nav_light_towing_yellow", "引き船灯（黄色）"),
                ("nav_light_allround_white", "全周白灯（停泊灯）"),
                ("nav_light_allround_red", "全周紅灯（危険物積載）"),
                ("nav_light_allround_green", "全周緑灯（水先船）"),
                ("nav_light_nuc_red_over_red", "運転不自由船（紅2灯）"),
                ("nav_light_ram_red_white_red", "操縦性能制限船（紅白紅）"),
                ("nav_light_fishing_red_white", "漁ろう船灯（紅白）"),
                ("nav_light_pilot_white_red", "水先案内船灯（白紅）")
            ],
            "nav_light_port_red", "nav_light_starboard_green"
        ),
        (
            "20",
            "機械工学における歯車機構（ギヤ減速機）の形式同定タスク。",
            "歯車構造：直交する2軸間で、ねじ状の円筒歯車とヘリカルギヤが噛み合い、極めて高い減速比とセルフロック性を発揮する機構を特定せよ。",
            "歯車構造：円筒外周に平行な直歯を持ち、平行な2軸間で最も一般的・高効率に動力を伝達する平歯車機構を特定せよ。",
            [
                ("gear_worm_and_wheel", "ウォームギヤ機構"),
                ("gear_spur_gear", "平歯車（スパーギヤ）"),
                ("gear_helical_gear", "はすば歯車（ヘリカル）"),
                ("gear_bevel_gear", "傘歯車（ベベルギヤ）"),
                ("gear_hypoid_gear", "ハイポイドギヤ"),
                ("gear_planetary_gear", "遊星歯車機構"),
                ("gear_rack_and_pinion", "ラックアンドピニオン"),
                ("gear_internal_ring", "内歯車（リングギヤ）"),
                ("gear_herringbone", "やまば歯車"),
                ("gear_harmonic_drive", "波動歯車装置"),
                ("gear_cycloidal_drive", "サイクロイド減速機構"),
                ("gear_non_circular", "非円形歯車機構")
            ],
            "gear_worm_and_wheel", "gear_spur_gear"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k12_defs:
        pairs.append({
            "id": f"rc2b4_var_{gid}_s1", "group_id": f"rc2b4_var_{gid}", "family": "variable_choice",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_var_{gid}_s2", "group_id": f"rc2b4_var_{gid}", "family": "variable_choice",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=16 (10 pairs: groups 21 to 30) Concise choices! ---
    k16_defs = [
        (
            "21",
            "マイクロプロセッサCPUの基本アセンブリ機械語命令同定タスク。",
            "命令動作：プログラム実行カウンタを無条件で指定ラベルアドレスへジャンプ移動させる命令を特定せよ。",
            "命令動作：何も処理を行わず、1クロックサイクルだけ実行時間を進める無操作命令を特定せよ。",
            [
                ("asm_op_jmp", "JMP（無条件分岐）"),
                ("asm_op_nop", "NOP（無操作待機）"),
                ("asm_op_add", "ADD（加算）"),
                ("asm_op_sub", "SUB（減算）"),
                ("asm_op_mul", "MUL（乗算）"),
                ("asm_op_div", "DIV（除算）"),
                ("asm_op_and", "AND（論理積）"),
                ("asm_op_or", "OR（論理和）"),
                ("asm_op_xor", "XOR（排他的論理和）"),
                ("asm_op_not", "NOT（ビット反転）"),
                ("asm_op_jz", "JZ（ゼロ時分岐）"),
                ("asm_op_jnz", "JNZ（非ゼロ分岐）"),
                ("asm_op_push", "PUSH（スタック積載）"),
                ("asm_op_pop", "POP（スタック取出）"),
                ("asm_op_call", "CALL（サブルーチン呼出）"),
                ("asm_op_ret", "RET（呼出元復帰）")
            ],
            "asm_op_jmp", "asm_op_nop"
        ),
        (
            "22",
            "国際単位系（SI）における10進接頭辞（倍数・分量）の同定タスク。",
            "単位倍率：基礎単位の10の9乗（10億倍）を表す接頭辞を特定せよ。",
            "単位倍率：基礎単位の10の-9乗（10億分の1）を表す接頭辞を特定せよ。",
            [
                ("si_prefix_giga", "ギガ（G・10^9）"),
                ("si_prefix_nano", "ナノ（n・10^-9）"),
                ("si_prefix_yotta", "ヨタ（Y・10^24）"),
                ("si_prefix_zetta", "ゼタ（Z・10^21）"),
                ("si_prefix_exa", "エクサ（E・10^18）"),
                ("si_prefix_peta", "ペタ（P・10^15）"),
                ("si_prefix_tera", "テラ（T・10^12）"),
                ("si_prefix_mega", "メガ（M・10^6）"),
                ("si_prefix_kilo", "キロ（k・10^3）"),
                ("si_prefix_milli", "ミリ（m・10^-3）"),
                ("si_prefix_micro", "マイクロ（μ・10^-6）"),
                ("si_prefix_pico", "ピコ（p・10^-12）"),
                ("si_prefix_femto", "フェムト（f・10^-15）"),
                ("si_prefix_atto", "アト（a・10^-18）"),
                ("si_prefix_zepto", "ゼプト（z・10^-21）"),
                ("si_prefix_yocto", "ヨクト（y・10^-24）")
            ],
            "si_prefix_giga", "si_prefix_nano"
        ),
        (
            "23",
            "化学周期表におけるアルカリ金属・ハロゲン元素の特定タスク。",
            "元素特性：原子番号3、最外殻電子1個を持ち、二次電池の電極材料として極めて重要な最軽量アルカリ金属を特定せよ。",
            "元素特性：原子番号9、電気陰性度が全元素中最大で、フッ素化合物の原料となるハロゲン元素を特定せよ。",
            [
                ("chem_elem_lithium", "リチウム（Li）"),
                ("chem_elem_fluorine", "フッ素（F）"),
                ("chem_elem_sodium", "ナトリウム（Na）"),
                ("chem_elem_potassium", "カリウム（K）"),
                ("chem_elem_rubidium", "ルビジウム（Rb）"),
                ("chem_elem_cesium", "セシウム（Cs）"),
                ("chem_elem_chlorine", "塩素（Cl）"),
                ("chem_elem_bromine", "臭素（Br）"),
                ("chem_elem_iodine", "ヨウ素（I）"),
                ("chem_elem_astatine", "アスタチン（At）"),
                ("chem_elem_beryllium", "ベリリウム（Be）"),
                ("chem_elem_magnesium", "マグネシウム（Mg）"),
                ("chem_elem_calcium", "カルシウム（Ca）"),
                ("chem_elem_strontium", "ストロンチウム（Sr）"),
                ("chem_elem_barium", "バリウム（Ba）"),
                ("chem_elem_radium", "ラジウム（Ra）")
            ],
            "chem_elem_lithium", "chem_elem_fluorine"
        ),
        (
            "24",
            "日本の都道府県庁所在地同定タスク。",
            "県庁位置：四国地方に属し、讃岐うどんの本場として知られる香川県の県庁所在地を特定せよ。",
            "県庁位置：北陸地方に属し、兼六園や加賀百万石の城下町として知られる石川県の県庁所在地を特定せよ。",
            [
                ("pref_capital_takamatsu", "高松市（香川県）"),
                ("pref_capital_kanazawa", "金沢市（石川県）"),
                ("pref_capital_sapporo", "札幌市（北海道）"),
                ("pref_capital_sendai", "仙台市（宮城県）"),
                ("pref_capital_niigata", "新潟市（新潟県）"),
                ("pref_capital_shizuoka", "静岡市（静岡県）"),
                ("pref_capital_nagoya", "名古屋市（愛知県）"),
                ("pref_capital_osaka", "大阪市（大阪府）"),
                ("pref_capital_kobe", "神戸市（兵庫県）"),
                ("pref_capital_hiroshima", "広島市（広島県）"),
                ("pref_capital_matsuyama", "松山市（愛媛県）"),
                ("pref_capital_fukuoka", "福岡市（福岡県）"),
                ("pref_capital_kumamoto", "熊本市（熊本県）"),
                ("pref_capital_naha", "那覇市（沖縄県）"),
                ("pref_capital_aomori", "青森市（青森県）"),
                ("pref_capital_nara", "奈良市（奈良県）")
            ],
            "pref_capital_takamatsu", "pref_capital_kanazawa"
        ),
        (
            "25",
            "総合病院における標榜診療科の専門領域同定タスク。",
            "主たる対象疾患：白内障、緑内障、加齢黄斑変性など眼球および視覚器の疾患を専門治療する診療科を特定せよ。",
            "主たる対象疾患：骨折、変形性関節症、椎間板ヘルニアなど骨・関節・筋肉・末梢神経を専門治療する診療科を特定せよ。",
            [
                ("med_dept_ophthalmology", "眼科"),
                ("med_dept_orthopedics", "整形外科"),
                ("med_dept_internal_med", "一般内科"),
                ("med_dept_general_surgery", "消化器一般外科"),
                ("med_dept_pediatrics", "小児科"),
                ("med_dept_obstetrics_gyne", "産婦人科"),
                ("med_dept_neurosurgery", "脳神経外科"),
                ("med_dept_dermatology", "皮膚科"),
                ("med_dept_ent_otolaryngology", "耳鼻咽喉科"),
                ("med_dept_urology", "泌尿器科"),
                ("med_dept_psychiatry", "精神神経科"),
                ("med_dept_radiology", "放射線診断科"),
                ("med_dept_anesthesiology", "麻酔科"),
                ("med_dept_pathology", "病理診断科"),
                ("med_dept_emergency_med", "救急科"),
                ("med_dept_rehabilitation", "リハビリテーション科")
            ],
            "med_dept_ophthalmology", "med_dept_orthopedics"
        ),
        (
            "26",
            "内燃機関自動車エンジン主要部品の機構的機能同定タスク。",
            "部品機能：燃焼室内の混合気に高電圧火花を放電させて点火する電極部品を特定せよ。",
            "部品機能：燃焼ガスの高圧力を受けてシリンダー内を往復運動する筒状部品を特定せよ。",
            [
                ("engine_part_spark_plug", "点火プラグ"),
                ("engine_part_piston", "ピストン"),
                ("engine_part_cylinder_block", "シリンダーブロック"),
                ("engine_part_con_rod", "コネクティングロッド"),
                ("engine_part_crankshaft", "クランクシャフト"),
                ("engine_part_camshaft", "カムシャフト"),
                ("engine_part_intake_valve", "吸気バルブ"),
                ("engine_part_exhaust_valve", "排気バルブ"),
                ("engine_part_turbocharger", "ターボチャージャー"),
                ("engine_part_intercooler", "インタークーラー"),
                ("engine_part_catalytic_converter", "三元触媒コンバータ"),
                ("engine_part_muffler", "消音器マフラー"),
                ("engine_part_flywheel", "フライホイール"),
                ("engine_part_timing_chain", "タイミングチェーン"),
                ("engine_part_oil_pump", "エンジンオイルポンプ"),
                ("engine_part_water_pump", "冷却水ウォーターポンプ")
            ],
            "engine_part_spark_plug", "engine_part_piston"
        ),
        (
            "27",
            "音響音色加工エフェクター機器の信号処理効果同定タスク。",
            "音響効果：原音を微小時間遅延させてピッチを変調し、複数人が同時に演奏しているような厚みと広がりを付加する効果を特定せよ。",
            "音響効果：残響音を人工的にシミュレートし、大聖堂やホールのような空間の広がりと響きを演出する効果を特定せよ。",
            [
                ("effect_chorus", "コーラスエフェクト"),
                ("effect_reverb", "リバーブエフェクト"),
                ("effect_delay", "ディレイ（エコー）"),
                ("effect_flanger", "フランジャー"),
                ("effect_phaser", "フェイザー"),
                ("effect_tremolo", "トレモロ振幅変調"),
                ("effect_vibrato", "ビブラート周波数変調"),
                ("effect_distortion", "ディストーション歪み"),
                ("effect_overdrive", "オーバードライブ"),
                ("effect_fuzz", "ファズ矩形波歪み"),
                ("effect_compressor", "ダイナミクスコンプレッサー"),
                ("effect_limiter", "ピークリミッター"),
                ("effect_wah_pedal", "ワウペダル帯域通過"),
                ("effect_equalizer", "パラメトリックイコライザー"),
                ("effect_noise_gate", "ノイズゲート"),
                ("effect_pitch_shifter", "ピッチシフター")
            ],
            "effect_chorus", "effect_reverb"
        ),
        (
            "28",
            "太陽系天体探査における惑星・衛星・準惑星の天文学的同定タスク。",
            "天体特徴：分厚い窒素大気と液体メタンの海や湖を有し、ホイヘンス探査機が着陸した土星最大の衛星を特定せよ。",
            "天体特徴：表面を氷殻で覆われ、内部に広大な液体の海（内部海）と熱水噴出孔の存在が有力視される木星の第2衛星を特定せよ。",
            [
                ("astro_titan", "タイタン（土星衛星）"),
                ("astro_europa", "エウロパ（木星衛星）"),
                ("astro_mercury", "水星"),
                ("astro_venus", "金星"),
                ("astro_moon", "月"),
                ("astro_mars", "火星"),
                ("astro_phobos", "フォボス（火星衛星）"),
                ("astro_ceres", "ケレス（準惑星）"),
                ("astro_jupiter", "木星"),
                ("astro_ganymede", "ガニメデ（木星衛星）"),
                ("astro_saturn", "土星"),
                ("astro_enceladus", "エンケラドゥス（土星衛星）"),
                ("astro_uranus", "天王星"),
                ("astro_neptune", "海王星"),
                ("astro_pluto", "冥王星（準惑星）"),
                ("astro_halley_comet", "ハレー彗星")
            ],
            "astro_titan", "astro_europa"
        ),
        (
            "29",
            "地質年代区分における顕生代（古生代・中生代・新生代）の『紀（Period）』同定タスク。",
            "地質時代：大型恐竜が最も繁栄し、鳥類の祖先が出現した約2億年前から1億4500万年前の中生代第2紀を特定せよ。",
            "地質時代：三葉虫やアノマロカリスなど多様な多細胞動物が一斉に出現した（カンブリア爆発）古生代最初の紀を特定せよ。",
            [
                ("geol_jurassic", "ジュラ紀（中生代）"),
                ("geol_cambrian", "カンブリア紀（古生代）"),
                ("geol_ordovician", "オルドビス紀"),
                ("geol_silurian", "シルル紀"),
                ("geol_devonian", "デボン紀"),
                ("geol_carboniferous", "石炭紀"),
                ("geol_permian", "ペルム紀"),
                ("geol_triassic", "三畳紀"),
                ("geol_cretaceous", "白亜紀"),
                ("geol_paleogene", "古第三紀"),
                ("geol_neogene", "新第三紀"),
                ("geol_quaternary", "第四紀"),
                ("geol_ediacaran", "エディアカラ紀"),
                ("geol_cryogenian", "クリオジェニアン紀"),
                ("geol_tonian", "トニアン紀"),
                ("geol_stenian", "ステニアン紀")
            ],
            "geol_jurassic", "geol_cambrian"
        ),
        (
            "30",
            "OSI参照モデルおよびインターネットプロトコルスタックの機能層同定タスク。",
            "プロトコル層：エンドツーエンドの信頼性あるデータ伝送やフロー制御（TCP、UDP等）を提供する階層を特定せよ。",
            "プロトコル層：異なるネットワーク間のルーティングやIPアドレッシング（IP、ICMP等）を司る階層を特定せよ。",
            [
                ("osi_layer_transport", "トランスポート層（第4層）"),
                ("osi_layer_network", "ネットワーク層（第3層）"),
                ("osi_layer_physical", "物理層（第1層）"),
                ("osi_layer_datalink", "データリンク層（第2層）"),
                ("osi_layer_session", "セッション層（第5層）"),
                ("osi_layer_presentation", "プレゼンテーション層（第6層）"),
                ("osi_layer_application", "アプリケーション層（第7層）"),
                ("osi_layer_link_mac", "MAC副層"),
                ("osi_layer_link_llc", "LLC副層"),
                ("osi_layer_ipsec", "IPsecセキュリティ層"),
                ("osi_layer_tls_ssl", "TLS/SSL暗号化層"),
                ("osi_layer_rpc", "RPCリモート呼出層"),
                ("osi_layer_routing_igp", "IGP内部ルーティング層"),
                ("osi_layer_routing_bgp", "BGP外部ルーティング層"),
                ("osi_layer_arp_rarp", "アドレス解決ARP層"),
                ("osi_layer_phy_pmd", "PMD物理媒体依存層")
            ],
            "osi_layer_transport", "osi_layer_network"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k16_defs:
        pairs.append({
            "id": f"rc2b4_var_{gid}_s1", "group_id": f"rc2b4_var_{gid}", "family": "variable_choice",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_var_{gid}_s2", "group_id": f"rc2b4_var_{gid}", "family": "variable_choice",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    return pairs
