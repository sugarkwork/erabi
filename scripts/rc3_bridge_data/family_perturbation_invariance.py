"""Family 8: perturbation_invariance (30 pairs, 60 cases) - RC3 Bridge Benchmark
Prefix: rc3b_pert_
Distribution: K=3 (10 pairs), K=4 (15 pairs), K=6 (5 pairs)
Focus: Semantic invariance under linguistic perturbations (active/passive, syntax reordering, synonymous substitutions, adversarial surface cues).
Zero leakage against all past datasets.
"""

from typing import Any, Dict, List, Tuple


def make_choices(c_defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in c_defs]


def get_perturbation_invariance_pairs() -> List[Dict[str, Any]]:
    pairs: List[Dict[str, Any]] = []

    # --- K=3 (10 pairs: groups 01 to 10) ---
    k3_defs = [
        (
            "01",
            "超臨界二酸化炭素地中貯留（CCS）圧入井の圧力健全性。保安基準：圧入圧力は地層破砕圧の80%未満を堅持すること。これを超過したときは圧入ポンプを即時停止する。",
            "観測ログ（能動表現）：現在の坑底圧入圧力は破砕圧力の71%にとどまっている。圧入井の運転制御を決定せよ。",
            "観測ログ（受動・倒置表現）：地層破砕圧の86%に達する過大圧力が坑底センサーによって検出された。圧入井の運転制御を決定せよ。",
            [("ccs_inject_continue", "破砕圧未満・超臨界CO2地中圧入続行"), ("ccs_inject_emergency_halt", "破砕圧超過・高圧圧入ポンプ緊急停止"), ("ccs_vent_choke_standby", "圧入井坑口チョーク弁減圧放散待機")],
            "ccs_inject_continue", "ccs_inject_emergency_halt"
        ),
        (
            "02",
            "大型変電所の油入変圧器ブッシング部分放電（PD）監視。運用規則：部分放電電荷量が500pCを超えた場合は絶縁破壊防止のため直ちに負荷移行遮断を実施する。未満であれば通常監視を維持する。",
            "診断記録（直接的表現）：高周波CT計測において測定放電電荷量は280pCであり、放電進展は見られない。変電運用を決定せよ。",
            "診断記録（迂回的表現）：絶縁油中HFCT検出器により680pCに達する激しい放電電荷パルスが捕捉された。変電運用を決定せよ。",
            [("bushing_pd_normal_keep", "放電基準未満・通常監視送電維持"), ("bushing_pd_trip_isolate", "放電過大・変圧器緊急負荷移行解列"), ("bushing_gas_chromato_req", "油中ガス分析緊急サンプリング")],
            "bushing_pd_normal_keep", "bushing_pd_trip_isolate"
        ),
        (
            "03",
            "全自動化学分析装置の比色分析セル温度制御。仕様基準：反応キュベット温度は37.0±0.2℃（36.8℃〜37.2℃）の許容範囲内に収まること。範囲外では酵素反応速度異常となるため測定を中断する。",
            "機器テレメトリ（平叙文）：恒温水槽温度計の実測値は37.05℃を示しており、温度変動は極めて小さい。検体測定処置を決定せよ。",
            "機器テレメトリ（結果先置文）：酵素試薬の変性温度である36.45℃までキュベット温度が低下したことが検知された。検体測定処置を決定せよ。",
            [("cuvette_assay_proceed", "温調基準適合・患者検体比色測定開始"), ("cuvette_temp_out_abort", "温度範囲逸脱・測定シーケンス緊急中断"), ("cuvette_water_bath_prime", "恒温水槽純水循環脱気")],
            "cuvette_assay_proceed", "cuvette_temp_out_abort"
        ),
        (
            "04",
            "クリーンルーム用自動搬送AGVの車輪接地圧モニタ。安全規程：車輪スリップ防止のため、接地荷重が定格の60%を下回った場合は直ちに走行を一時停止すること。十分な荷重があれば走行を承認する。",
            "センサー報告（標準文）：4輪の独立ロードセル計測値はいずれも定格荷重の78%以上を確保している。AGV走行を指示せよ。",
            "センサー報告（否定条件文）：片輪が段差に乗り上げた結果、対角輪の接地荷重が定格の42%まで減少した。AGV走行を指示せよ。",
            [("agv_traction_authorized", "接地荷重十分・搬送自動走行承認"), ("agv_traction_slip_stop", "接地荷重不足・スリップ防止一時停止"), ("agv_chassis_level_tune", "サスペンションエアレベリング補正")],
            "agv_traction_authorized", "agv_traction_slip_stop"
        ),
        (
            "05",
            "半導体エッチング装置の排気トラップ温度管理。保全規程：副生成物結晶化による配管閉塞を防ぐため、排気トラップジャケット温度は150℃以上を保持すること。150℃未満に降下したときはガス導入を遮断する。",
            "ライン監視（技術調）：温調ヒーター実測温度は158℃を安定して推移している。プロセスガス導入を判断せよ。",
            "ライン監視（警報調）：ヒーター断線によりトラップ温度が132℃へ低下している異常が警報された。プロセスガス導入を判断せよ。",
            [("trap_heat_pass_feed", "配管保温良好・エッチングガス導入開始"), ("trap_cold_block_cutoff", "温度降下閉塞危険・ガス導入弁緊急遮断"), ("trap_roughing_line_purge", "真空排気ライン窒素パージ排気")],
            "trap_heat_pass_feed", "trap_cold_block_cutoff"
        ),
        (
            "06",
            "洋上風力発電設備のナセル内火災防護システム。安全規程：光電式煙感知器および熱感知器の両方が作動した場合に限り不活性ガス消火剤全域放出を実行する。単一検知のみでは放出せず警報確認を行う。",
            "防災コンソール（対比表現）：煙感知器は警報を発しているものの、熱感知器は通常温度を示し作動していない。消火システム動作を決定せよ。",
            "防災コンソール（同時表現）：濃煙の充満に伴い煙感知器が作動し、直後に熱感知器も設定温度（70℃）に達して同時発報した。消火システム動作を決定せよ。",
            [("fire_confirm_alarm_only", "単一検知・火災警報発令およびカメラ現場確認"), ("fire_gas_extinguish_release", "複合検知成立・不活性ガス消火剤全域放出"), ("fire_manual_override_lock", "消火システム手動ロックアウト施錠")],
            "fire_confirm_alarm_only", "fire_gas_extinguish_release"
        ),
        (
            "07",
            "製薬用精製水ラインのオゾン水殺菌濃度管理。バリデーション基準：配管ループ内溶存オゾン濃度は0.20mg/L以上を20分間維持すること。濃度未達の場合は殺菌工程不合格とする。",
            "殺菌工程ログ（時系列文）：20分間の循環サイクル全体を通じて溶存オゾン濃度は0.24〜0.28mg/Lを維持完了した。殺菌判定を下せ。",
            "殺菌工程ログ（逆接文）：殺菌開始12分後にオゾン発生器の放電が低下し、濃度が0.11mg/Lへ落ち込んだ。殺菌判定を下せ。",
            [("ozone_sanitize_pass", "オゾン濃度時間充足・定期殺菌工程合格承認"), ("ozone_sanitize_fail_repeat", "オゾン濃度未達・殺菌不合格再サイクル要求"), ("ozone_destruct_uv_run", "オゾン分解紫外線ランプ強制照射")],
            "ozone_sanitize_pass", "ozone_sanitize_fail_repeat"
        ),
        (
            "08",
            "港湾荷役ガントリークレーンの過負荷防止装置。安全規程：定格吊り上げ荷重の110%を超過した場合は巻き上げ動作を自動停止すること。許容荷重内であれば荷役を続行する。",
            "荷重計モニタ（順接文）：現在吊り上げ中の40ftコンテナ総重量は定格の84%であり、安全係数内である。荷役動作を決定せよ。",
            "荷重計モニタ（過負荷文）：コンテナ内荷崩れによる偏荷重が加わり、実測吊り上げ荷重が定格の116%を記録した。荷役動作を決定せよ。",
            [("crane_hoist_permitted", "定格荷重内・巻き上げ荷役作業続行"), ("crane_hoist_overload_cut", "定格超過過負荷・巻き上げ自動停止インターロック"), ("crane_spreader_twistlock_free", "スプレッダーツイストロック強制解錠")],
            "crane_hoist_permitted", "crane_hoist_overload_cut"
        ),
        (
            "09",
            "水力発電所水圧鉄管の自動空気弁作動基準。保安規定：水圧鉄管急速排水時、管内圧力が大気圧以下（負圧）となることを防ぐため空気弁を自動全開吸気すること。正圧保持時は閉止を維持する。",
            "鉄管圧力テレメトリ（定常文）：水圧鉄管内水圧は静水圧+0.8MPaの正圧を維持している。空気弁動作を指示せよ。",
            "鉄管圧力テレメトリ（過渡文）：発電機緊急トリップに伴い下流ガイドベーンが急閉止後、反射波により管内が-30kPaの負圧へ転じた。空気弁動作を指示せよ。",
            [("air_valve_remain_closed", "正圧維持・空気弁全閉シート維持"), ("air_valve_full_open_inhale", "負圧圧潰危険・空気弁緊急全開自動吸気"), ("air_valve_oil_damper_lock", "油圧ダンパー急開防止ラッチ")],
            "air_valve_remain_closed", "air_valve_full_open_inhale"
        ),
        (
            "10",
            "高所作業車のブーム伸長転倒防止モーメントリミッタ。作業基準：車両安定度モーメントが許容限界の90%に達した場合はブーム伸長・倒伏動作を強制制限すること。安全範囲内であれば操作を許可する。",
            "安全制御盤（通常文）：現在の転倒モーメントは許容限界の62%であり、アウトリガー反力も均等である。ブーム操作を判断せよ。",
            "安全制御盤（警告文）：作業員がバケットを最大半径へ張り出した結果、モーメントが許容限界の94%へ急接近した。ブーム操作を判断せよ。",
            [("boom_operation_allow", "モーメント許容内・ブーム自由操作許可"), ("boom_operation_limit_lock", "転倒限界接近・危険側動作自動停止制限"), ("boom_outrigger_relevel", "アウトリガー油圧自動水平復帰")],
            "boom_operation_allow", "boom_operation_limit_lock"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k3_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_pert_{gid}_s1",
                "group_id": f"rc3b_pert_{gid}",
                "family": "perturbation_invariance",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_pert_{gid}_s2",
                "group_id": f"rc3b_pert_{gid}",
                "family": "perturbation_invariance",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2}
            }
        ])

    # --- K=4 (15 pairs: groups 11 to 25) ---
    k4_defs = [
        (
            "11",
            "特別高圧受電設備の真空遮断器（VCB）開閉サージ抑制。技術規程：励磁突入電流による過電圧を抑制するため、投入フェーズ位相角がゼロクロス点±5度以内であることを確認して投入すること。位相不整合時は投入を待機する。",
            "位相制御装置ログ（正常投入）：A相電圧ゼロクロス点との位相差は+1.8度で完全に同期捕捉された。遮断器制御を指示せよ。",
            "位相制御装置ログ（同期不整合）：系統擾乱によりゼロクロス点との位相差が+24度に大きく開いている。遮断器制御を指示せよ。",
            [("vcb_sync_close_fire", "位相角同期適合・VCB同期投入パルス送信"), ("vcb_sync_close_wait", "位相不整合・同期捕捉完了まで投入待機"), ("vcb_surge_absorber_check", "サージアブソーバー放電耐量点検"), ("vcb_trip_coil_continuity", "トリップコイル断線導通試験")],
            "vcb_sync_close_fire", "vcb_sync_close_wait"
        ),
        (
            "12",
            "半導体ウェハ化学機械研磨（CMP）のスラリー流量モニタ。研磨基準：研磨ヘッド摩擦熱によるウェハ焼けを防ぐため、研磨布上スラリー流量は200mL/min以上を供給すること。流量不足時は研磨ヘッドを即時リフト退避させる。",
            "流量センサテレメトリ（定格供給）：電磁流量計は235mL/minの安定供給を記録している。CMP研磨工程を決定せよ。",
            "流量センサテレメトリ（供給途絶）：スラリー供給配管ノズルの固着閉塞により、流量が45mL/minへ急落した。CMP研磨工程を決定せよ。",
            [("cmp_polishing_continue", "スラリー流量適正・ウェハ研磨ヘッド加圧続行"), ("cmp_head_lift_abort", "流量不足ウェハ焼損防止・ヘッド即時上昇退避"), ("cmp_dresser_pad_clean", "ダイヤモンドドレッサコンディショニング"), ("cmp_slurry_recirculate", "スラリー供給ループバイパス循環")],
            "cmp_polishing_continue", "cmp_head_lift_abort"
        ),
        (
            "13",
            "LNGローリー車出荷受入設備の静電気アースインターロック。受入基準：タンクローリー車体の対地接地抵抗値が10Ω以下であることを検知しない限り、受入荷役弁を開放してはならない。接地不良時は受入を禁止する。",
            "インターロック監視（良導体接地）：クランプ接続後の実測対地接地抵抗は2.8Ωであり、アースリレーが導通した。荷役弁制御を指示せよ。",
            "インターロック監視（接地不良）：クランプ先端の錆付着により、実測接地抵抗は85Ωを示している。荷役弁制御を指示せよ。",
            [("lng_unloading_valve_open", "接地抵抗規格適合・LNG受入液送弁全開"), ("lng_unloading_interlock_block", "接地不良静電気危険・受入弁開閉ロック閉止"), ("lng_vapor_return_line_vent", "気相リターン配管窒素パージ"), ("lng_loading_arm_purge_standby", "ローディングアーム配管加圧待機")],
            "lng_unloading_valve_open", "lng_unloading_interlock_block"
        ),
        (
            "14",
            "産業用大型蒸気ボイラーの水位低下防止保全。保安規程：炉筒煙管の過熱破裂を防ぐため、缶水水位が最低安全低水位（LWL）を下回った場合は直ちに燃料供給を遮断すること。水位正常時は自動給水を継続する。",
            "水位電極モニタ（正常水位）：実測缶水水位は常用水位中央部で安定推移している。燃焼制御を指示せよ。",
            "水位電極モニタ（渇水検知）：給水ポンプ故障により水位が急速低下し、最低安全低水位LWL電極から水面が離脱した。燃焼制御を指示せよ。",
            [("boiler_feedwater_run", "水位適正・バーナー燃焼および給水自動継続"), ("boiler_low_water_fuel_cut", "渇水過熱危険・燃料供給電磁弁即時遮断"), ("boiler_bottom_blowdown", "ボイラー底部缶底ブロー弁開"), ("boiler_safety_valve_test", "蒸気安全弁手動吹出しテスト")],
            "boiler_feedwater_run", "boiler_low_water_fuel_cut"
        ),
        (
            "15",
            "超精密非球面レンズ成形機の金型真空度管理。光学基準：転写面のマイクロボイド欠陥を防ぐため、キャビティ内真空度は10Pa以下に到達してから型締め加圧を開始すること。真空未達時は加圧を待機する。",
            "成形機PLCモニタ（真空完了）：ピラニ真空計の指示値は3.5Paに達した。型締め加圧シーケンスを決定せよ。",
            "成形機PLCモニタ（リーク遅延）：ガスケット劣化により真空引き開始後30秒経過しても圧力は85Paにとどまっている。型締め加圧シーケンスを決定せよ。",
            [("mold_clamping_press_start", "真空度到達・型締め加圧およびコアヒーター昇温"), ("mold_press_wait_vacuum", "真空未達ボイド懸念・加圧待機および排気続行"), ("mold_purge_inert_argon", "不活性アルゴンチャンバーパージ"), ("mold_core_cooling_quench", "金型コア強制冷却水通水")],
            "mold_clamping_press_start", "mold_press_wait_vacuum"
        ),
        (
            "16",
            "水処理プラントのオゾン分解触媒塔入口排ガス加温。プロセス基準：結露による触媒失活を防止するため、触媒塔入口ガス温度は露点+15℃以上を維持すること。温度不足時は電気ヒーター出力を増強する。",
            "温湿度計データ（露点乖離十分）：排ガス露点は25℃であり、触媒入口ヒーター後温度は48℃を維持している。ヒーター制御を指示せよ。",
            "温湿度計データ（結露危険温度）：高湿度ガス流入により露点が38℃まで上昇したにもかかわらず、入口温度は42℃まで低下した。ヒーター制御を指示せよ。",
            [("ozone_cat_heater_nominal", "結露防止温度十分・ヒーター定格制御維持"), ("ozone_cat_heater_power_up", "温度余裕不足結露危険・電気ヒーター最大出力増強"), ("ozone_cat_bypass_flare", "分解触媒バイパスライン切替"), ("ozone_cat_blower_derate", "排気ファンインバータ回転数絞り")],
            "ozone_cat_heater_nominal", "ozone_cat_heater_power_up"
        ),
        (
            "17",
            "化学工場廃液焼却炉のキルン出口排ガス温度維持。環境基準：ダイオキシン類の完全熱分解を担保するため、二次燃焼室温度は850℃以上かつ滞留時間2秒以上を維持すること。850℃未満では助燃バーナーを点火増強する。",
            "熱電対アレイ記録（完全熱分解温度）：二次燃焼室最頂部の計測温度は920℃を安定保持している。燃焼運用を決定せよ。",
            "熱電対アレイ記録（温度降下基準割れ）：高含水廃液の急投入により、二次燃焼室温度が815℃まで急落した。燃焼運用を決定せよ。",
            [("incinerator_combustion_pass", "ダイオキシン分解温度適合・廃液定格焼却継続"), ("incinerator_aux_burner_fire", "温度基準逸脱・助燃重油バーナー緊急点火増強"), ("incinerator_sludge_feed_boost", "焼却スラッジ投入ポンプ増量"), ("incinerator_induced_fan_stop", "誘引通風ファン急停止待機")],
            "incinerator_combustion_pass", "incinerator_aux_burner_fire"
        ),
        (
            "18",
            "新幹線軌道のレール締結装置バネ脱落検知。軌道保守基準：列車走行安全性を確保するため、同一まくらぎ上で締結バネの脱落・折損が検知された場合は当該区間の列車速度を徐行規制すること。健全時は通常速度を維持する。",
            "軌道検測車画像処理ログ（締結健全）：まくらぎ全箇所の締結バネは所定位置にあり、締結力低下は検出されない。列車運行を指示せよ。",
            "軌道検測車画像処理ログ（バネ折損検出）：第402号まくらぎ外軌側において、板バネの折損脱落が画像解析で確定検知された。列車運行を指示せよ。",
            [("track_nominal_speed_clear", "締結部健全・通常最高速度営業運転承認"), ("track_speed_restriction_apply", "締結バネ折損・制限速度適用徐行運行指令"), ("track_ballast_tamp_order", "バラストマルタイ突き固め指令"), ("track_rail_grind_schedule", "レール削正車夜間出動手配")],
            "track_nominal_speed_clear", "track_speed_restriction_apply"
        ),
        (
            "19",
            "食品レトルト殺菌釜のF値（加熱致死時間効果）演算管理。殺菌基準：ボツリヌス菌芽胞の完全死滅を担保するため、缶中心累積F値が4.0以上を達成してから冷却工程へ移行すること。F値未達時は加熱保持を延長する。",
            "レトルト記録計モニタ（目標F値達成）：ロットAの最冷点缶内積算F値は4.8に到達した。工程移行を決定せよ。",
            "レトルト記録計モニタ（F値未達継続）：ロットBの積算F値は現在2.6であり、目標値に未達である。工程移行を決定せよ。",
            [("retort_cool_phase_proceed", "目標F値達成・加圧冷却水注入工程移行"), ("retort_heat_phase_extend", "F値未達殺菌不足・蒸気加圧加熱時間延長"), ("retort_emergency_vent_blow", "レトルト缶内蒸気緊急ブロー排気"), ("retort_basket_unload_air", "殺菌カゴ台車即時搬出")],
            "retort_cool_phase_proceed", "retort_heat_phase_extend"
        ),
        (
            "20",
            "大型射出成形機の型締力ロードセル監視。成形基準：金型バリ発生および金型破損を防ぐため、型締力は設定値の±5%以内を維持すること。過大時は油圧クランプ力を減圧補正する。",
            "成形機モニタ（定格型締力）：実測型締力は設定3500kNに対し3520kN（+0.6%偏差）である。成形射出を指示せよ。",
            "成形機モニタ（異常過加圧）：金型熱膨張により型締力が3880kN（+10.9%超過）へ跳ね上がった。成形射出を指示せよ。",
            [("molding_inject_proceed", "型締力適正・溶融樹脂スクリュー射出実行"), ("molding_clamp_force_reduce", "型締力過大金型保護・クランプ油圧シリンダ減圧補正"), ("molding_barrel_heater_cut", "バレルバンドヒーター全電源遮断"), ("molding_ejector_pin_advance", "エジェクターピン前進離型待機")],
            "molding_inject_proceed", "molding_clamp_force_reduce"
        ),
        (
            "21",
            "データセンター非常用ガスタービン発電機の燃料油デイタンク油位。燃料基準：全負荷連続運転時間を確保するため、デイタンク油位は80%以上を常時維持すること。80%未満に低下した場合は主燃料タンクから自動補給する。",
            "油位発信器データ（満杯維持）：フロート油位計は92%を示している。燃料移送ポンプ制御を決定せよ。",
            "油位発信器データ（補給基準割れ）：定期試験運転によりデイタンク油位が68%まで消費低下した。燃料移送ポンプ制御を決定せよ。",
            [("fuel_day_tank_standby", "デイタンク油位十分・移送ポンプ停止待機"), ("fuel_transfer_pump_start", "油位基準低下・主貯油槽移送ポンプ自動起動補給"), ("fuel_oil_purifier_bypass", "燃料遠心分離清浄機バイパス循環"), ("fuel_emergency_dump_line", "燃料デイタンク緊急ドレン排出弁開")],
            "fuel_day_tank_standby", "fuel_transfer_pump_start"
        ),
        (
            "22",
            "医薬品凍結乾燥バイアル巻締機のキャッピングトルク検査。包装基準：ゴム栓密封性とアルミキャップ完全性を両立するため、巻締トルクは0.35〜0.55N・mの範囲内であること。範囲外は不良品として自動排除する。",
            "トルク測定モニタ（基準内適合）：オンライン測定トルクは0.46N・mを記録した。バイアル搬送処置を指示せよ。",
            "トルク測定モニタ（トルク不足）：巻締ローラー摩耗により測定トルクが0.22N・mにとどまった。バイアル搬送処置を指示せよ。",
            [("capping_torque_accept_pass", "巻締トルク適合・製品トレイ自動集積移送"), ("capping_torque_reject_eject", "トルク規格外気密不良・不良品排出レーン排除"), ("capping_crimping_roller_lube", "巻締ローラーベアリング注油"), ("capping_vial_stopper_depth", "ゴム栓打栓深さセンサー再校正")],
            "capping_torque_accept_pass", "capping_torque_reject_eject"
        ),
        (
            "23",
            "航空機胴体与圧室の安全流出弁（アウトフローバルブ）差圧制御。アビオニクス基準：機体構造過圧を防ぐため、内外差圧ΔPは設計上限60kPa以下を維持すること。60kPa超過時はアウトフローバルブを開放する。",
            "フライトデッキ計器（通常巡航差圧）：現在巡航高度でのキャビン内外差圧は54kPaで安定している。与圧弁制御を指示せよ。",
            "フライトデッキ計器（過圧検知）：与圧制御器の故障により内外差圧が64kPaへ上昇し超過した。与圧弁制御を指示せよ。",
            [("cabin_press_nominal_cruise", "内外差圧正常・アウトフローバルブ自動開度維持"), ("cabin_press_relief_open", "構造過圧危険・安全流出弁手動強制全開"), ("cabin_pack_flow_max", "エアコンパック給気流量最大増量"), ("cabin_ram_air_inlet_open", "ラムエア吸気口全開減圧")],
            "cabin_press_nominal_cruise", "cabin_press_relief_open"
        ),
        (
            "24",
            "原子力発電所燃料プール冷却浄化系（FPC）のイオン交換樹脂差圧。水質基準：放射性核種除去性能低下と通水閉塞を防ぐため、樹脂塔差圧は0.15MPa以下を維持すること。超過時は樹脂逆洗再生または交換を行う。",
            "計装制御盤（差圧正常）：イオン交換樹脂塔の前後差圧は0.06MPaを示している。FPC通水運用を指示せよ。",
            "計装制御盤（差圧目詰まり超過）：クラッド堆積により樹脂塔差圧が0.19MPaへ上昇した。FPC通水運用を指示せよ。",
            [("fpc_resin_flow_continue", "通水差圧健全・燃料プール水冷却浄化継続"), ("fpc_resin_backwash_req", "差圧過大目詰まり・通水停止および樹脂逆洗交換"), ("fpc_skimmer_surge_pump", "スキマサージタンクポンプ起動"), ("fpc_heat_exchanger_cool", "海水系熱交換器冷却水通水増量")],
            "fpc_resin_flow_continue", "fpc_resin_backwash_req"
        ),
        (
            "25",
            "超純水製造プラントの逆浸透（RO）膜モジュール塩阻止率管理。造水基準：比抵抗確保のため、RO膜の塩阻止率は99.0%以上を維持すること。阻止率低下時は膜洗浄またはモジュール交換を実施する。",
            "水質分析モニタ（阻止率合格）：給水電導度と透過水電導度から算出した塩阻止率は99.6%である。RO通水制御を決定せよ。",
            "水質分析モニタ（阻止率劣化）：シリカスケール析出により塩阻止率が97.8%まで劣化した。RO通水制御を決定せよ。",
            [("ro_permeate_service_run", "塩阻止率適合・高圧ポンプ連続造水承認"), ("ro_membrane_cip_clean", "阻止率低下水質不適合・CIP薬品洗浄工程回送"), ("ro_concentrate_valve_open", "濃縮水フラッシング弁全開"), ("ro_antiscalant_pump_tare", "スケール防止剤注入ポンプ校正")],
            "ro_permeate_service_run", "ro_membrane_cip_clean"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k4_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_pert_{gid}_s1",
                "group_id": f"rc3b_pert_{gid}",
                "family": "perturbation_invariance",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_pert_{gid}_s2",
                "group_id": f"rc3b_pert_{gid}",
                "family": "perturbation_invariance",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2}
            }
        ])

    # --- K=6 (5 pairs: groups 26 to 30) ---
    k6_defs = [
        (
            "26",
            "石油精製水素化分解装置の高圧分離器（HPセパレータ）液位制御。保安基準：液位高による水素圧縮機液撃および液位低による低圧段への高圧ガス吹き抜け（ガスブローバイ）の両方を厳重防止すること。",
            "計装ループモニタ（定常液位）：差圧式液位計の測定値は設計中央値48%（許容域30〜70%）で完全に平衡している。分離器運用を指示せよ。",
            "計装ループモニタ（ガスブローバイ危機）：液位調節弁の開固着により液位が12%まで急低下し、ガス巻き込み危険域に達した。分離器運用を指示せよ。",
            [("hp_separator_nominal_level", "液位平衡安定・底抜油量自動PID調節維持"), ("hp_separator_emergency_dump_trip", "低液位ガスブローバイ危険・底抜出弁緊急全閉遮断"), ("hp_separator_high_level_cut", "高液位オーバーフロー・原料フィード停止"), ("hp_separator_wash_water_pump", "塩析防止洗浄水注入ポンプ増量"), ("hp_separator_sour_gas_flare", "酸性サワーガスフレア弁開放"), ("hp_separator_sampling_drain", "油水分離界面サンプリング確認")],
            "hp_separator_nominal_level", "hp_separator_emergency_dump_trip"
        ),
        (
            "27",
            "鉄道地上変電所のシリコン整流器（SMR）素子破壊保護。電気鉄道基準：ダイオード素子逆方向耐圧破壊を防ぐため、整流素子短絡検出器が動作したときは直流高速度遮断器（HSCB）および交流側遮断器を連動トリップすること。",
            "受変電監視盤（素子健全）：全相の整流アーム漏洩電流およびヒューズ溶断センサは正常である。整流器運用を指示せよ。",
            "受変電監視盤（短絡検出）：U相アームの素子短絡センサが動作し、逆流電流が検出された。整流器運用を指示せよ。",
            [("smr_rectifier_energize_pass", "整流素子健全・直流1500Vき電線給電継続"), ("smr_diode_short_circuit_trip", "素子短絡事故・交流遮断器およびHSCB連動即時トリップ"), ("smr_cooling_fan_boost", "整流器風冷ファンインバータ高速化"), ("smr_reverse_current_relay_cal", "逆流継電器動作限時特性点検"), ("smr_rc_snubber_measure", "素子保護RCスナバコンデンサ容量測定"), ("smr_surge_absorber_arrester", "直流避雷器放電カウンター確認")],
            "smr_rectifier_energize_pass", "smr_diode_short_circuit_trip"
        ),
        (
            "28",
            "浮体式天然ガス生産貯蔵積出設備（FLNG）の低温ローディングアーム緊急切断。海洋基準：荒天ヒーブ動揺による荷役アーム許容包絡域（エンベロープ）逸脱時は、二重遮断弁を閉止後パワード緊急離脱カプラ（PERC）を切離すること。",
            "荷役監視テレメトリ（定常包絡内）：アーム関節角度センサの合成位置は安全グリーンゾーンの中央にある。LNG移送を決定せよ。",
            "荷役監視テレメトリ（限界逸脱警報）：強風動揺によりアームが許容レッドゾーン限界角度（伸長98%）に到達した。緊急安全処置を決定せよ。",
            [("flng_transfer_nominal_pumping", "荷役包絡域内安定・LNG積込移送ポンプ運転"), ("flng_perc_emergency_disconnect", "包絡限界逸脱・緊急遮断弁急閉およびPERC即時離脱"), ("flng_mooring_winch_tension", "係留索油圧ウインチ張力巻き締め"), ("flng_arm_hydraulic_damping", "アーム動揺減衰油圧ダンパー圧調整"), ("flng_nitrogen_purge_arm", "アーム配管高圧窒素急速パージ"), ("flng_ballast_trim_heel", "FLNG船体ヒール傾斜バラスト調整")],
            "flng_transfer_nominal_pumping", "flng_perc_emergency_disconnect"
        ),
        (
            "29",
            "自動車衝突安全試験におけるインフレータブルカーテンエアバッグ展開判定。アルゴリズム基準：側面衝突時のポール側面衝突G波形積分値（ΔV）が展開閾値を超過した場合は点火点火スクイブへ即時通電すること。",
            "エアバッグECU内部ログ（非展開事象）：路面凹凸段差通過によるフロアGピークが検知されたが、速度変化量ΔVは閾値の15%である。点火判定を下せ。",
            "エアバッグECU内部ログ（側面衝突確定）：Bピラー加速度センサが15ms以内にΔV=25km/hの急減速を検知し展開判定閾値を超過した。点火判定を下せ。",
            [("airbag_igniter_hold_disarm", "非衝突路面衝撃・エアバッグ不展開維持"), ("airbag_igniter_fire_deploy", "側面衝突確定・カーテンエアバッグ即時点火展開"), ("airbag_seatbelt_pretension_only", "プリテンショナー単独微小引き込み"), ("airbag_crash_log_flash_save", "事故記録不揮発性メモリ書き込み"), ("airbag_squib_resistance_diag", "点火回路スキュー抵抗常時診断"), ("airbag_can_hazard_broadcast", "ハザード点滅衝突信号CAN通知")],
            "airbag_igniter_hold_disarm", "airbag_igniter_fire_deploy"
        ),
        (
            "30",
            "大規模下水処理場の消化汚泥脱水ケーキ含水率管理。環境基準：焼却炉の自燃性を維持するため、遠心脱水機出口ケーキ含水率は78.0%以下を達成すること。含水率超過時は高分子凝集剤注入率を引き上げる。",
            "脱水機分析レポート（含水率適合）：赤外線水分計によるケーキ含水率は75.2%を記録した。脱水汚泥移送を決定せよ。",
            "脱水機分析レポート（含水率過剰）：汚泥性状悪化によりケーキ含水率が82.4%まで悪化した。脱水機運転を決定せよ。",
            [("sludge_cake_incinerate_transfer", "含水率基準適合・自燃焼却炉ホッパー移送"), ("sludge_polymer_dosing_boost", "含水率超過不適合・カチオン高分子凝集剤注入率増強"), ("sludge_centrifuge_diff_speed_tune", "遠心脱水機差速インバータ再調整"), ("sludge_feed_rate_throttle", "生汚泥供給ポンプ流量絞り込み"), ("sludge_centrate_turbidity_alarm", "分離液脱水濾液濁度監視"), ("sludge_cake_storage_silo_vent", "ケーキ貯留サイロ臭気吸引換気")],
            "sludge_cake_incinerate_transfer", "sludge_polymer_dosing_boost"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k6_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_pert_{gid}_s1",
                "group_id": f"rc3b_pert_{gid}",
                "family": "perturbation_invariance",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_pert_{gid}_s2",
                "group_id": f"rc3b_pert_{gid}",
                "family": "perturbation_invariance",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2}
            }
        ])

    return pairs
