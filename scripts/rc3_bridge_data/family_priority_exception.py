"""Family 3: priority_exception (30 pairs, 60 cases) - RC3 Bridge Benchmark
Prefix: rc3b_prio_
Distribution: K=3 (10 pairs), K=4 (15 pairs), K=6 (5 pairs)
Focus: Multi-tier rule hierarchies, emergency precedence over standard regulations, exception clauses.
Zero leakage against all past datasets.
"""

from typing import Any, Dict, List, Tuple


def make_choices(c_defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in c_defs]


def get_priority_exception_pairs() -> List[Dict[str, Any]]:
    pairs: List[Dict[str, Any]] = []

    # --- K=3 (10 pairs: groups 01 to 10) ---
    k3_defs = [
        (
            "01",
            "超高層ビル中央監視室の空調防災優先制御規則。優先度第1位『火災感知器連動排煙モード』、優先度第2位『電力デマンドピークカット節電モード』、優先度第3位『標準スケジュール換気モード』。",
            "システム状況：火災感知器は非作動、デマンド警報が発令された。空調系統制御を決定せよ。",
            "システム状況：デマンド警報発令中であるが、同時に地下2階火災感知器が作動した。空調系統制御を決定せよ。",
            [("hvac_fire_exhaust", "防災排煙モード強制起動"), ("hvac_demand_shedding", "デマンドピークカット節電稼働"), ("hvac_nominal_schedule", "標準スケジュール換気運転")],
            "hvac_demand_shedding", "hvac_fire_exhaust"
        ),
        (
            "02",
            "港湾コンテナクレーンの自律荷役優先制御規則。第1優先『風速計18m/s超過による非常強風固定』、第2優先『作業員エリア侵入レーザー遮光停止』、第3優先『最適コンテナ荷積み自動サイクル』。",
            "稼働状況：風速は8m/sで穏やかだが、岸壁作業員が荷役警戒エリアへ誤進入した。クレーン動作を指示せよ。",
            "稼働状況：作業員侵入はないが、突発ガストにより風速21m/sが計測された。クレーン動作を指示せよ。",
            [("crane_storm_lockdown", "非常強風固定レールクランプ緊定"), ("crane_intrusion_estop", "安全柵侵入検知非常停止"), ("crane_auto_loading_run", "最適コンテナ荷積み自動サイクル続行")],
            "crane_intrusion_estop", "crane_storm_lockdown"
        ),
        (
            "03",
            "航空機自動操縦装置の対地接近警報（GPWS）優先規程。第1優先『地形接近警告（PULL UP強制機首引き上げ）』、第2優先『進入進入角逸脱警報（GLIDESLOPE警告音）』、第3優先『FMS規定降下パス追従』。",
            "フライト状況：対地レーダー高度計が急速接近を感知し『PULL UP』警報が発報された。操縦介入を決定せよ。",
            "フライト状況：対地接近危険はなく、グライドスロープから1ドット下方に逸脱した。操縦介入を決定せよ。",
            [("gpws_max_pitch_pullup", "PULL UP強制最大出力機首引き上げ"), ("gpws_glideslope_correct", "グライドスロープ進入角是正微調整"), ("gpws_fms_descent_keep", "FMS規定降下パス自動追従維持")],
            "gpws_max_pitch_pullup", "gpws_glideslope_correct"
        ),
        (
            "04",
            "半導体エッチング装置の異常処理優先順位。第1位『高周波RFマッチング放電異常即時プラズマ消弧』、第2位『チャンバー壁面温度上限超過温調調整』、第3位『ロットウェハ通常エッチング処理』。",
            "アラーム状態：RFマッチングは安定しているが、チャンバー壁面温度が上限閾値を0.5℃超過した。装置制御を指示せよ。",
            "アラーム状態：チャンバー壁面温度が上限超過し、同時にRF整合ボックスで内部放電スパークが検知された。装置制御を指示せよ。",
            [("etch_plasma_extinguish", "RF異常即時放電消弧・プロセス中断"), ("etch_wall_cool_tune", "チャンバー壁面温調冷却PID調整"), ("etch_batch_continue", "ロットウェハエッチング通常続行")],
            "etch_wall_cool_tune", "etch_plasma_extinguish"
        ),
        (
            "05",
            "無人自動巡回警備ロボットの行動優先度。最優先『人命危険・火炎検知通報』、第2位『低バッテリー自律帰還充電』、第3位『フロア定期巡回警備』。",
            "ロボットステータス：バッテリー残量が15%（帰還閾値以下）となり、火炎や煙の兆候はない。行動を決定せよ。",
            "ロボットステータス：バッテリー残量は12%で帰還中であったが、給湯室にてサーモカメラが炎を捕捉した。行動を決定せよ。",
            [("patrol_fire_report_alarm", "火炎検知現場直行・防災センター緊急通報"), ("patrol_auto_dock_charge", "巡回中断・自律充電ドック帰還"), ("patrol_routine_inspection", "フロア定期巡回監視継続")],
            "patrol_auto_dock_charge", "patrol_fire_report_alarm"
        ),
        (
            "06",
            "製薬精製水注射用水（WFI）ループの殺菌優先規則。最優先『定期85℃熱水循環熱殺菌シーケンス』、第2優先『ユースポイントオンデマンド採水給水』、第3優先『冷水自己循環待機』。",
            "配管タイマー：熱殺菌スケジュール時刻に到達した。ユースポイントでの採水要求フラグが入力された。弁制御を判定せよ。",
            "配管タイマー：熱殺菌時間帯ではなく、調剤室ユースポイントから採水弁開要求が入力された。弁制御を判定せよ。",
            [("wfi_heat_sanitization", "熱水殺菌優先・全ユースポイント採水ロック"), ("wfi_dispense_water", "採水弁開放・注射用水給水開始"), ("wfi_idle_recirculate", "冷水自己循環待機維持")],
            "wfi_heat_sanitization", "wfi_dispense_water"
        ),
        (
            "07",
            "大型プレス機械の安全装置優先順位規程。最優先『光線安全装置光軸遮断時即時スライド停止』、第2位『金型交換インチング微小寸動モード』、第3位『両手操作押しボタン連続自動加工』。",
            "運転状況：金型交換スイッチが選択され、光軸エリアは完全にクリアである。操作モードを決定せよ。",
            "運転状況：金型交換インチング操作中であったが、作業者の腕が光線安全装置を横切った。操作モードを決定せよ。",
            [("press_light_curtain_estop", "光軸遮断検知・スライド即時強制停止"), ("press_die_change_inch", "金型交換微小寸動モード実行"), ("press_continuous_stamp", "両手押しボタン連続プレス自動実行")],
            "press_die_change_inch", "press_light_curtain_estop"
        ),
        (
            "08",
            "配電系統自動電圧調整器（SVR）の制御優先規程。第1優先『配電線路過電圧保護急速タップ下げ』、第2優先『力率改善用進相コンデンサ投入協調』、第3優先『標準反限時タップ切替』。",
            "系統計測：受電電圧が整定上限を突発的に6V超過した。コンデンサ投入指令は出ていない。タップ動作を指示せよ。",
            "系統計測：過電圧はなく、系統力率が85%へ低下したため進相コンデンサが投入された。タップ動作を指示せよ。",
            [("svr_emergency_tap_down", "過電圧保護・急速タップ下げ動作"), ("svr_capacitor_coord_tune", "コンデンサ投入連動・無効電力適正化"), ("svr_time_delay_tap", "標準反限時タップ切替待機")],
            "svr_emergency_tap_down", "svr_capacitor_coord_tune"
        ),
        (
            "09",
            "製鉄高炉ガスホルダーの安全放散優先規程。最優先『ホルダー上限満杯防止緊急ガス放散弁開放』、第2優先『コークス炉ガス混合熱量調整』、第3優先『発電ボイラー定格ガス供給』。",
            "計装モニタ：ピストン位置が危険上限の98%に達した。ボイラー燃料要求は継続中である。放散制御を決定せよ。",
            "計装モニタ：ピストン位置は安全領域の65%であり、カロリー計が発熱量低下を検出した。放散制御を決定せよ。",
            [("blast_furnace_vent_open", "ホルダー過充填防止・緊急放散弁強制全開"), ("blast_furnace_cal_blend", "コークス炉ガス混合比率増量熱量補正"), ("blast_furnace_boiler_feed", "発電ボイラー定格ガス供給継続")],
            "blast_furnace_vent_open", "blast_furnace_cal_blend"
        ),
        (
            "10",
            "病院救急搬送トリアージ優先規則。最優先『赤（最優先治療：気道閉塞・大量出血）』、第2優先『黄（待機可能重症：骨折・中等度熱傷）』、第3優先『緑（軽症歩行可能）』。",
            "患者バイタル：意識清明、下腿開放骨折で歩行不能だが呼吸・循環動態は安定している。トリアージ区分を決定せよ。",
            "患者バイタル：意識混濁、血圧70/40mmHg、浅表呼吸で気道狭窄音が聴取される。トリアージ区分を決定せよ。",
            [("triage_tag_yellow", "黄タグ交付・二次救急処置室収容"), ("triage_tag_red", "赤タグ交付・初療室緊急気道確保処置"), ("triage_tag_green", "緑タグ交付・外来待合待機")],
            "triage_tag_yellow", "triage_tag_red"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k3_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_prio_{gid}_s1",
                "group_id": f"rc3b_prio_{gid}",
                "family": "priority_exception",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_prio_{gid}_s2",
                "group_id": f"rc3b_prio_{gid}",
                "family": "priority_exception",
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
            "自動運転商用トラックの軌道制御優先順位。第1優先『前方衝突不可避時の緊急操舵回避または最大制動』、第2優先『車線逸脱防止ステアリングアシスト』、第3優先『高速道路追従クルーズ走行』、第4優先『燃料節約惰性走行エココースティング』。",
            "カメラセンシング：前方150mクリア、左側白線を跨ぎそうになっている。操舵制御を指示せよ。",
            "カメラセンシング：左側白線を跨ぎそうになった瞬間、前方15mの先行車が急停止した。操舵制御を指示せよ。",
            [("truck_lane_keep_assist", "車線逸脱防止ステアリング自動復帰"), ("truck_crash_evasion_brake", "衝突不可避・緊急自動急制動および回避操舵"), ("truck_acc_cruise_keep", "高速道路車間追従クルーズ維持"), ("truck_eco_coast_roll", "燃料節約エココースティング")],
            "truck_lane_keep_assist", "truck_crash_evasion_brake"
        ),
        (
            "12",
            "医薬品原薬晶析槽の撹拌冷却優先規程。第1優先『槽内圧力急上昇時ベントライン全開開放』、第2優先『過冷却突沸防止晶析シード添加温度保持』、第3優先『規定冷却速度プログラム降温』、第4優先『晶析完了スラリー排出』。",
            "プロセス記録：槽内圧力は常圧で安定、結晶化温度到達によりシード添加指令が出ている。晶析制御を決定せよ。",
            "プロセス記録：シード添加準備中、突然の副反応ガス発生により槽内圧力が設計限界へ急上昇した。晶析制御を決定せよ。",
            [("crystallizer_seed_hold", "晶析シード添加温度保温保持"), ("crystallizer_vent_burst", "過圧緊急ベント弁全開開放"), ("crystallizer_ramp_cooling", "規定降温プログラム冷却"), ("crystallizer_slurry_drain", "晶析スラリー自動排出")],
            "crystallizer_seed_hold", "crystallizer_vent_burst"
        ),
        (
            "13",
            "航空機ジェットエンジンの燃料調速（FADEC）優先順位。第1優先『タービン過熱EGT超過防止燃料制限』、第2優先『コンプレッサーサージ検知時ブリード弁開放』、第3優先『パイロット推力レバー指令追従』、第4優先『地上アイドル燃料最小化』。",
            "フライト状況：スロットル全開上昇中、第2段コンプレッサーに圧力脈動サージが検知された。燃料制御を指示せよ。",
            "フライト状況：サージ兆候はなく、排気ガス温度EGTがレッドライン限界温度に達した。燃料制御を指示せよ。",
            [("fadec_bleed_surge_relief", "サージ検知・過渡ブリード弁自動開放"), ("fadec_egt_fuel_cutback", "EGT超過防止・燃料流量強制リミットカット"), ("fadec_throttle_track", "推力レバー指令燃料流量設定"), ("fadec_ground_idle_min", "地上アイドル最小燃料供給")],
            "fadec_bleed_surge_relief", "fadec_egt_fuel_cutback"
        ),
        (
            "14",
            "データストレージ管理のIOPS優先制御（QoS）規程。第1優先『オンライン基幹トランザクションDB』、第2優先『基幹バッチ夜間集計処理』、第3優先『分析基盤BIクエリ』、第4優先『外部クラウド遠隔バックアップ同期』。",
            "ストレージ負荷：コントローラIOPS使用率が90%に達し、DB処理と分析BIクエリが競合した。優先帯域を割り当てよ。",
            "ストレージ負荷：DB処理は低負荷だが、夜間集計バッチと外部バックアップ同期が帯域上限で競合した。優先帯域を割り当てよ。",
            [("qos_tier1_database", "最優先帯域・オンライン基幹DB専有割当"), ("qos_tier2_batch", "第2優先帯域・夜間集計バッチ割当"), ("qos_tier3_analytics", "第3優先帯域・分析BIクエリ割当"), ("qos_tier4_backup", "第4優先帯域・遠隔バックアップ割当")],
            "qos_tier1_database", "qos_tier2_batch"
        ),
        (
            "15",
            "下水終末処理場雨水ポンプの自動運転優先順位。第1優先『外水潮位高潮逆流防止ゲート緊急閉鎖』、第2優先『流入幹線雨水ポンプ最大揚水排水』、第3優先『沈砂池除塵機連続掻き揚げ』、第4優先『通常晴天時汚水ポンプ運転』。",
            "豪雨時テレメトリ：河川潮位は堤防余裕内であるが、雨水幹線水位が危険浸水域へ急上昇した。ポンプ場制御を指示せよ。",
            "豪雨時テレメトリ：幹線水位上昇に加え、高潮により河川潮位が防潮堤天端を越流する危険に直面した。ポンプ場制御を指示せよ。",
            [("drain_storm_pump_max", "雨水幹線ポンプ最大出力揚水排水"), ("drain_tidal_gate_close", "高潮逆流防止防潮ゲート即時閉鎖"), ("drain_screen_rake_auto", "沈砂池除塵スクリーン連続掻き揚げ"), ("drain_nominal_sewage", "通常晴天時汚水ポンプ運転")],
            "drain_storm_pump_max", "drain_tidal_gate_close"
        ),
        (
            "16",
            "半導体製造クリーンルームの排気インターロック優先順位。第1優先『シラン系可燃性毒性ガス漏洩時即時窒素緊急パージ』、第2優先『排気ダクト負圧低下時予備ファン起動』、第3優先『酸アルカリ系統排気風量制御』、第4優先『外気導入給気ファン自動風量調節』。",
            "監視コンソール：ガス漏洩はなく、排気ダクト内の静圧が-50Paまで低下（排気力減退）した。防災処置を決定せよ。",
            "監視コンソール：排気ダクト負圧低下のアラート中、シランガスセンサーが漏洩警報を発報した。防災処置を決定せよ。",
            [("cleanroom_duct_backup_fan", "予備排気ファン並列緊急起動"), ("cleanroom_silane_n2_purge", "シランガス漏洩・即時高圧窒素パージ"), ("cleanroom_acid_exhaust", "酸アルカリ排気風量調整"), ("cleanroom_air_supply_adjust", "給気ファン風量絞り込み")],
            "cleanroom_duct_backup_fan", "cleanroom_silane_n2_purge"
        ),
        (
            "17",
            "新幹線ATC（自動列車制御装置）ブレーキ制御優先規程。第1優先『地震P波早期検知による非常制動指令』、第2優先『前方閉塞区間制限速度超過による保安減速』、第3優先『駅停車定位置停止パターン制御』、第4優先『通常定速走行制御』。",
            "運行状況：区間速度285km/hで走行中、前方曲線制限230km/hパターンに接近した。地震検知はない。ブレーキ制御を指示せよ。",
            "運行状況：制限速度追従減速中、海底地震計がP波初動を検知し即時警報が入力された。ブレーキ制御を指示せよ。",
            [("atc_overspeed_service_brake", "速度制限超過防止常用保安ブレーキ"), ("atc_earthquake_emergency_stop", "地震早期検知即時非常ブレーキ作動"), ("atc_station_stop_pattern", "定位置停止支援減速制御"), ("atc_nominal_cruising", "通常定速ノッチ制御")],
            "atc_overspeed_service_brake", "atc_earthquake_emergency_stop"
        ),
        (
            "18",
            "太陽電池パネル製造ラインのラミネーター熱圧着優先順位。第1優先『チャンバーダイヤフラム破れ検出時即時大気開放』、第2優先『EVA樹脂架橋硬化温度時間プロファイル制御』、第3優先『真空脱泡引き抜き工程』、第4優先『モジュール搬出コンベア送り』。",
            "プロセスモニタ：脱泡完了後、EVAシート架橋のための150℃加熱保持ステップへ移行した。ダイヤフラム健全。工程を指示せよ。",
            "プロセスモニタ：架橋保持工程中、加圧ダイヤフラムゴムシートの裂傷により空気漏洩が感知された。工程を指示せよ。",
            [("laminator_eva_cure_profile", "EVA架橋温度プロファイル加圧保持"), ("laminator_rupture_abort_vent", "ダイヤフラム破損・緊急真空遮断大気開放"), ("laminator_vacuum_degas", "チャンバー内真空脱泡排気"), ("laminator_eject_conveyor", "熱圧着モジュール搬出移送")],
            "laminator_eva_cure_profile", "laminator_rupture_abort_vent"
        ),
        (
            "19",
            "無人潜水探査艇（ROV）の油圧マニピュレータ優先順位。第1優先『母船アンビリカルケーブル絡まり防止自己アーム緊急切り離し』、第2優先『海底サンプル把持過負荷リリーフ』、第3優先『ジョイスティック操縦追従動作』、第4優先『アーム原点格納モード』。",
            "作業状況：海底岩石把持中、グリッパーの油圧把持力が許容トルク上限に達した。絡まりはない。油圧制御を決定せよ。",
            "作業状況：岩石把持の最中、潮流によりテザーケーブルがマニピュレータ手首関節に巻き込まれた。油圧制御を決定せよ。",
            [("rov_grip_force_relief", "把持力過負荷リリーフ弁逃がし動作"), ("rov_tether_tangle_jettison", "テザー絡まり危険・アーム緊急パージ切り離し"), ("rov_joystick_manual_track", "ジョイスティック手動操縦追従"), ("rov_arm_home_stow", "油圧アーム規定原点格納")],
            "rov_grip_force_relief", "rov_tether_tangle_jettison"
        ),
        (
            "20",
            "大規模病院自家発電機の重要負荷給電優先度。最優先『ICU・手術室・人工呼吸器用非常無停電回路』、第2優先『薬品保冷庫・血液バンク冷却回路』、第3優先『一般病棟照明・エレベーター常用回路』、第4優先『外来ホール空調・事務系コンセント回路』。",
            "商用停電時：発電機容量の50%を使用中、第1優先と第2優先のみ給電されている。容量制約により次に給電すべき回路を選択せよ。",
            "商用停電時：発電機過負荷トリップを避けるため、給電遮断（負荷制限）を最も先に行うべき回路を選択せよ。",
            [("hospital_power_icu", "ICU・手術室非常無停電回路"), ("hospital_power_cold_storage", "薬品保冷庫・血液バンク回路"), ("hospital_power_elevator_lights", "一般病棟照明・エレベーター回路"), ("hospital_power_outpatient_hvac", "外来ホール空調・事務系回路")],
            "hospital_power_elevator_lights", "hospital_power_outpatient_hvac"
        ),
        (
            "21",
            "バイオ医薬品精製クロマトグラフィー分離カラム保護優先規程。第1優先『カラム入口圧力上限到達時フィードポンプ即時停止』、第2優先『吸光度ピーク検出時フラクション自動分取』、第3優先『グラジエント溶出バッファー混合比率制御』、第4優先『カラム平衡化洗浄ステップ』。",
            "クロマトグラフィ状況：カラム入口圧力は0.15MPaで安定、目的タンパク質のUV280nm吸光度が立ち上がった。制御を決定せよ。",
            "クロマトグラフィ状況：吸光度ピーク分取中、カラム目詰まりにより入口圧力が許容耐圧0.35MPaに急激に到達した。制御を決定せよ。",
            [("chromato_fraction_collect", "吸光度ピーク連動・分取バルブ切替回収"), ("chromato_overpressure_pump_stop", "カラム過圧保護・フィードポンプ即時停止"), ("chromato_gradient_mix", "溶出バッファーグラジエント混合"), ("chromato_equilibrate_rinse", "平衡化洗浄バッファー通液")],
            "chromato_fraction_collect", "chromato_overpressure_pump_stop"
        ),
        (
            "22",
            "ドローン自律飛行制御のフェイルセーフ優先度。第1優先『バッテリー臨界残量即時その場パラシュート開傘不時着』、第2優先『通信途絶時フェイルセーフ自動ホーム帰還（RTH）』、第3優先『GPS測位低下時オプティカルフロー高度維持』、第4優先『ウェイポイント空撮自律飛行』。",
            "フライトログ：バッテリー残量は60%であるが、基地局との2.4GHz制御通信が20秒間完全に途絶した。ドローン制御を決定せよ。",
            "フライトログ：通信は正常であるが、バッテリーセル電圧が急落し飛行維持不能の臨界残量5%に達した。ドローン制御を決定せよ。",
            [("drone_failsafe_rth", "通信途絶フェイルセーフ・自律ホーム帰還"), ("drone_parachute_forced_land", "バッテリー臨界残量・パラシュート開傘緊急不時着"), ("drone_optical_flow_hover", "オプティカルフロー姿勢ホバリング"), ("drone_waypoint_mission", "ウェイポイント自律ミッション継続")],
            "drone_failsafe_rth", "drone_parachute_forced_land"
        ),
        (
            "23",
            "水力発電用ペルトン水車の過速度保護優先順位。第1優先『水撃防止デフレクター（水流そらし板）即時全開投入』、第2優先『ニードルバルブ緩速閉止制御』、第3優先『ガバナー定格回転数追従調速』、第4優先『無負荷励磁運転』。",
            "発電機事故時：送電線落雷により全負荷遮断が発生し、水車回転数が定格の130%へ跳ね上がった。保護制御を決定せよ。",
            "発電機事故時：デフレクターが作動して水流をそらした後、管路水撃圧を抑えながら行うべき次期減水動作を決定せよ。",
            [("pelton_deflector_emergency_cut", "デフレクター即時全開・ランナー直撃遮断"), ("pelton_needle_slow_close", "水撃緩衝・ニードルバルブプログラム緩閉止"), ("pelton_governor_speed_control", "調速機回転数追従制御"), ("pelton_no_load_idle", "無負荷アイドリング待機")],
            "pelton_deflector_emergency_cut", "pelton_needle_slow_close"
        ),
        (
            "24",
            "クリーンルーム用自動搬送天井走行車（OHT）の走行優先度。最優先『火災防火シャッター降下区間即時進入回避停止』、第2優先『合流交差点先着搬送車優先通過』、第3優先『後続搬送車車間距離センシング減速』、第4優先『配分指令経路定速走行』。",
            "軌道運行管理：防火シャッター動作はなく、分岐合流点にて先行OHTが右側軌道から先に合流エリアへ進入した。OHT制御を決定せよ。",
            "軌道運行管理：合流交差点へのアプローチ中、直前の防火区画シャッター連動信号が作動しシャッター降下が開始された。OHT制御を決定せよ。",
            [("oht_junction_yield_wait", "合流交差点一時停止・先着車通過待機"), ("oht_shutter_fire_emergency_stop", "防火シャッター直前即時非常停止"), ("oht_inter_vehicle_slowdown", "車間距離保持減速走行"), ("oht_dispatch_route_cruise", "配分指令経路定速走行")],
            "oht_junction_yield_wait", "oht_shutter_fire_emergency_stop"
        ),
        (
            "25",
            "石油精製水素製造炉の緊急遮断（ESD）優先規程。第1優先『改質炉チューブ破裂検出時全バーナー燃料弁即時遮断』、第2優先『原料炭化水素フィード遮断およびスチームパージ』、第3優先『炉内通風ダンパー開放冷却』、第4優先『定常原料比率運転』。",
            "プラント計測：改質チューブ健全性モニタにて微小な圧力差が検知されたが、破裂フラグは未検知。原料比率制御を継続中である。",
            "プラント計測：改質炉チューブ監視カメラにて高温赤熱管の突発破裂が検知され炉内圧力が急落した。緊急処置を指示せよ。",
            [("reformer_nominal_feed_keep", "定常原料スチーム比率運転継続"), ("reformer_esd_fuel_gas_trip", "緊急遮断・全バーナー燃料ガス電磁弁即時遮断"), ("reformer_feed_cutoff_steam_purge", "原料フィード遮断・高圧スチームパージ"), ("reformer_damper_open_cool", "通風ダンパー全開自然通風冷却")],
            "reformer_nominal_feed_keep", "reformer_esd_fuel_gas_trip"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k4_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_prio_{gid}_s1",
                "group_id": f"rc3b_prio_{gid}",
                "family": "priority_exception",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_prio_{gid}_s2",
                "group_id": f"rc3b_prio_{gid}",
                "family": "priority_exception",
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
            "宇宙ステーション環境制御生命維持システム（ECLSS）の優先序列。最優先『モジュール急減圧検知時ハッチ隔離密閉』、第2『アンモニア冷媒船内漏洩検知時換気ループ完全遮断』、第3『船内火災時酸素供給遮断消火』、第4『二酸化炭素除去キャニスター自動再生』、第5『温度湿度通常空調』、第6『実験廃熱ラジエーター冷却』。",
            "船内状況テレメトリ：気密は正常、第2実験モジュールにてアンモニア冷媒ラインの微小漏洩が検知された。直ちに処置を決定せよ。",
            "船内状況テレメトリ：デブリ衝突音とともに第1モジュール気圧が毎秒10kPaで急激に低下した。直ちに処置を決定せよ。",
            [("eclss_ammonia_vent_isolate", "アンモニア漏洩・当該モジュール換気隔離遮断"), ("eclss_decompression_hatch_seal", "船体急減圧・気密ハッチ自動緊急閉止密閉"), ("eclss_fire_o2_cutoff", "船内火災消火・酸素供給遮断"), ("eclss_co2_scrubber_cycle", "CO2除去キャニスター再生サイクル"), ("eclss_nominal_ac_tune", "温湿度通常空調ループ調整"), ("eclss_radiator_thermal_reject", "外部ラジエーター放熱循環")],
            "eclss_ammonia_vent_isolate", "eclss_decompression_hatch_seal"
        ),
        (
            "27",
            "自動車自動溶接ライン安全制御盤の優先順位。最優先『セーフティエリア非常停止非常停止ボタン押下』、第2『安全ライトカーテン光軸遮断』、第3『インターロック安全プラグ抜去』、第4『溶接トーチ衝突干渉検知』、第5『治具クランプ着座確認未達』、第6『通常タクトタイム連続自動溶接』。",
            "ライン保全ログ：非常停止ボタンは押されていないが、作業員がエリア扉の安全プラグを抜いて目視確認に入った。ロボット動作を判定せよ。",
            "ライン保全ログ：非常停止ボタンが現場作業者により直接強打された。ロボット動作を判定せよ。",
            [("welder_safety_plug_inhibit", "安全プラグ抜去検知・サーボ電源遮断待機"), ("welder_estop_button_trip", "非常停止ボタン押下・全軸機械ブレーキ即時締結"), ("welder_light_curtain_hold", "ライトカーテン光軸遮断減速停止"), ("welder_torch_collision_abort", "トーチ干渉衝突検知退避"), ("welder_clamp_seating_wait", "治具クランプ着座確認待機"), ("welder_nominal_cycle_run", "タクトタイム自動溶接続行")],
            "welder_safety_plug_inhibit", "welder_estop_button_trip"
        ),
        (
            "28",
            "原子力発電設備デジタル安全保護系（RPS）の作動優先度。最優先『原子炉手動トリップスイッチ』、第2『原子炉圧力容器過圧スクラム』、第3『主蒸気隔離弁（MSIV）急閉止スクラム』、第4『給水喪失低水位スクラム』、第5『中性子束高スクラム』、第6『制御棒通常制御プログラム』。",
            "プラント過渡監視：主蒸気隔離弁の誤閉止信号が発生した。手動スイッチは非作動である。スクラム要因を判定せよ。",
            "プラント過渡監視：主蒸気隔離弁は開いているが、蒸気発生器チューブ破断により原子炉圧力容器圧力が設定限界を超過した。スクラム要因を判定せよ。",
            [("rps_msiv_closure_scram", "主蒸気隔離弁急閉止トリップ・全制御棒挿入"), ("rps_overpressure_scram", "原子炉容器過圧スクラム・高圧注入起動"), ("rps_manual_switch_scram", "手動トリップスイッチ作動スクラム"), ("rps_low_water_scram", "給水喪失低水位スクラム"), ("rps_high_flux_scram", "中性子束高スクラム"), ("rps_normal_rod_adjust", "制御棒通常位置調整")],
            "rps_msiv_closure_scram", "rps_overpressure_scram"
        ),
        (
            "29",
            "製鉄熱間圧延ライン自動板厚制御（AGC）の優先順位。最優先『ロール胴折損時油圧圧下急速開放』、第2『板噛み込みミス・ミスロール時通板急停止』、第3『板破断ルーパージャンプ防止』、第4『マスフロ板厚フィードバック制御』、第5『油圧ベンディング板クラウン制御』、第6『圧延ロール定格通板』。",
            "ラインセンシング：圧延中の鋼板後端がガイドに引っかかりミスロール座屈が発生した。ロール折損はない。処置を指示せよ。",
            "ラインセンシング：圧延荷重が設計耐荷重の3倍に達し、下ワークロール軸受ハウジングで折損音と急激な傾斜が検出された。処置を指示せよ。",
            [("agc_misroll_emergency_stop", "ミスロール検知・ミルスタンド即時非常停止"), ("agc_roll_break_quick_open", "ロール折損検知・油圧圧下シリンダー急速開放"), ("agc_strip_break_looper_drop", "ストリップ破断・ルーパー降下退避"), ("agc_mass_flow_thickness_tune", "マスフロ板厚フィードバック補正"), ("agc_roll_bending_crown", "ワークロールベンディング制御"), ("agc_nominal_strip_rolling", "熱間圧延定格通板継続")],
            "agc_misroll_emergency_stop", "agc_roll_break_quick_open"
        ),
        (
            "30",
            "バイオセーフティレベル4（BSL-4）最高機密実験室の気流制御優先度。最優先『実験室内陽圧転換阻止緊急ダンパー全開排気』、第2『HEPAフィルター破断検知時バックアップフィルタ即時流路切替』、第3『エアロック扉差圧破壊時強制陰圧引き』、第4『給気風量と排気風量の連動インバータ自動調整』、第5『温湿度精密空調』、第6『省エネナイトパージモード』。",
            "陰圧モニタ：実験室陰圧は-80Paで維持されているが、排気HEPA差圧センサーが突然0Pa（フィルター破断リーク）を示した。対応を決定せよ。",
            "陰圧モニタ：給気ファンの暴走故障により室内圧力が-10Paへ急上昇し、陽圧転換の危機に達した。対応を決定せよ。",
            [("bsl4_hepa_rupture_divert", "HEPA破断検知・予備タンデムフィルタ緊急切替"), ("bsl4_positive_prevention_exhaust", "陽圧化阻止・排気緊急ダンパー全開最大排気"), ("bsl4_airlock_diff_evac", "エアロック差圧復旧強制排気"), ("bsl4_fan_inverter_balance", "給排気風量バランス自動調速"), ("bsl4_nominal_hvac_control", "実験室温湿度精密空調"), ("bsl4_night_purge_eco", "夜間省エネ換気モード")],
            "bsl4_hepa_rupture_divert", "bsl4_positive_prevention_exhaust"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k6_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_prio_{gid}_s1",
                "group_id": f"rc3b_prio_{gid}",
                "family": "priority_exception",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_prio_{gid}_s2",
                "group_id": f"rc3b_prio_{gid}",
                "family": "priority_exception",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2}
            }
        ])

    return pairs
