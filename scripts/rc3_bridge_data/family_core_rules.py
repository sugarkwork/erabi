"""Family 1: core_rules (30 pairs, 60 cases) - RC3 Bridge Benchmark
Prefix: rc3b_core_
Distribution: K=3 (10 pairs), K=4 (15 pairs), K=6 (5 pairs)
Focus: Operational threshold boundaries, strict equality/inequality criteria, dual-metric validation.
Zero leakage against all past datasets.
"""

from typing import Any, Dict, List, Tuple


def make_choices(c_defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in c_defs]


def get_core_rules_pairs() -> List[Dict[str, Any]]:
    pairs: List[Dict[str, Any]] = []

    # --- K=3 (10 pairs: groups 01 to 10) ---
    k3_defs = [
        (
            "01",
            "LNG基地ボイルオフガス（BOG）再液化圧縮機運用基準。規定条件は『吸入圧力180kPa以上かつ吐出温度-40℃以下』である。",
            "監視モニタ：吸入圧力は185kPa、吐出温度は-42℃で安定推移している。圧縮機運用判定を行え。",
            "監視モニタ：吸入圧力は172kPaに降下し、吐出温度は-38℃へ上昇した。圧縮機運用判定を行え。",
            [("bog_compress_run", "再液化圧縮機通常定格運転継続"), ("bog_compress_halt", "再液化圧縮機緊急トリップ停止"), ("bog_compress_bypass", "バイパス循環減圧待機")],
            "bog_compress_run", "bog_compress_halt"
        ),
        (
            "02",
            "新幹線用パンタグラフすり板接触力モニタ基準。規定条件は『動的接触力70N以上120N以下を常時維持』である。",
            "テレメトリ計測：現在走行中の動的接触力は92Nで連続測定された。架線集電状態を判定せよ。",
            "テレメトリ計測：現在走行中の動的接触力は135Nへ突発的に過上昇した。架線集電状態を判定せよ。",
            [("pantograph_contact_normal", "集電接触力正常・走行継続承認"), ("pantograph_force_alarm", "接触力過大警報・降弓点検指令"), ("pantograph_standby_mode", "予備パンタグラフ切替準備")],
            "pantograph_contact_normal", "pantograph_force_alarm"
        ),
        (
            "03",
            "EV向けリチウムイオン角形電池の注液後脱ガス工程規定。合格基準は『チャンバー減圧到達度が-98.0kPa以下（絶対圧換算）かつ維持時間300秒以上』である。",
            "製造データ記録：ロットXの真空度は-98.6kPaに達し、330秒間の減圧保持を完了した。脱ガス判定を下せ。",
            "製造データ記録：ロットYの真空度は-96.2kPaにとどまり、到達後210秒でリーク感知された。脱ガス判定を下せ。",
            [("degas_pass_seal", "脱ガス合格・本封止ステーション移送"), ("degas_fail_vacuum", "減圧未達不合格・再排気工程回送"), ("degas_cell_quarantine", "電解液浸漬セル隔離検査保留")],
            "degas_pass_seal", "degas_fail_vacuum"
        ),
        (
            "04",
            "極紫外線（EUV）露光装置の光学系ミラー反射率基準。運用条件は『Mo/Si多層膜反射率68.5%以上を維持』である。",
            "光学センサー診断：第3コレクターミラーの計測反射率は69.1%である。露光光学系の処置を決定せよ。",
            "光学センサー診断：第3コレクターミラーの計測反射率は67.8%に劣化検知された。露光光学系の処置を決定せよ。",
            [("euv_optics_continue", "光学系正常・ウェハ露光シーケンス続行"), ("euv_mirror_clean", "反射率低下・水素ラジカル洗浄シーケンス実行"), ("euv_cassette_hold", "ウェハ搬送ロードロック一時停止")],
            "euv_optics_continue", "euv_mirror_clean"
        ),
        (
            "05",
            "加圧水型発電設備二次系給水脱酸素装置の管理基準。規定は『給水溶存酸素濃度5.0ppb以下かつpH9.0以上9.5以下』である。",
            "水質サンプリング結果：溶存酸素は2.8ppb、給水pHは9.25である。二次系水質管理判定を行え。",
            "水質サンプリング結果：溶存酸素は7.4ppbへ上昇、給水pHは8.70へ低下した。二次系水質管理判定を行え。",
            [("feedwater_pass", "二次系水質適合・通常給水運転継続"), ("feedwater_deox_boost", "水質基準逸脱・ヒドラジン注入増量処置"), ("feedwater_sampling_hold", "分析計ゼロ点校正再測定待機")],
            "feedwater_pass", "feedwater_deox_boost"
        ),
        (
            "06",
            "海底油田防噴装置（BOP）油圧アキュムレータ再充填基準。合格条件は『作動圧21.0MPa以上到達かつ圧力保持降下率0.1MPa/10分以内』である。",
            "充填テストログ：作動圧は21.8MPaに達し、10分間の降下量は0.03MPaであった。油圧健全性を判定せよ。",
            "充填テストログ：作動圧は21.4MPaに達したが、10分間の降下量は0.45MPaを記録した。油圧健全性を判定せよ。",
            [("bop_hydraulic_ok", "BOP油圧蓄圧健全・深海降下許可"), ("bop_leak_repair", "油圧保持不良・マニホールドシール修理"), ("bop_bleed_standby", "油圧配管エア抜きスタンバイ")],
            "bop_hydraulic_ok", "bop_leak_repair"
        ),
        (
            "07",
            "二段式宇宙ロケット用液体酸素ターボポンプ回転速度管理基準。定格条件は『主軸回転数28000rpm以上31000rpm以下』である。",
            "燃焼試験テレメトリ：ターボポンプ主軸回転数は29500rpmを維持している。推進系制御を指示せよ。",
            "燃焼試験テレメトリ：ターボポンプ主軸回転数は32400rpmへ暴走傾向を示した。推進系制御を指示せよ。",
            [("pump_throttle_nominal", "公称定格回転維持・燃焼継続承認"), ("pump_emergency_cutoff", "過回転危険・プレバーナー即時消火カットオフ"), ("pump_purge_standby", "ヘリウムパージライン待機待機")],
            "pump_throttle_nominal", "pump_emergency_cutoff"
        ),
        (
            "08",
            "自動化立体倉庫スタッカークレーンの制動減速区間センシング規則。基準は『減速ゾーン進入時速度0.8m/s以下かつレーザー測距誤差±5mm以内』である。",
            "走行制御PLCログ：進入速度は0.65m/s、測距誤差は+2mmである。荷受け棚停止制御を決定せよ。",
            "走行制御PLCログ：進入速度は1.15m/s、測距誤差は+14mmを検出した。荷受け棚停止制御を決定せよ。",
            [("crane_dock_nominal", "正常減速進入・目標棚番自動着床"), ("crane_abort_brake", "進入速度超過・非常機械ブレーキ作動"), ("crane_realign_mode", "荷爪フォーク原点復帰シーク")],
            "crane_dock_nominal", "crane_abort_brake"
        ),
        (
            "09",
            "製鉄連続鋳造ラインのモールドパウダー粘度制御基準。基準は『溶融粘度0.15Pa・s以上0.25Pa・s以下かつモールド液面変動±3mm以内』である。",
            "操業データ監視：計測パウダー粘度は0.19Pa・s、液面変動は±1.5mmである。鋳造運用判定を行え。",
            "操業データ監視：計測パウダー粘度は0.32Pa・sへ粘性増加、液面変動は±5.5mmを記録した。鋳造運用判定を行え。",
            [("casting_speed_keep", "モールド潤滑健全・定格引抜速度維持"), ("casting_slowdown_heat", "パウダー粘性過剰・引抜減速および保温材追加"), ("casting_tundish_hold", "タンディッシュノズル予熱スタンバイ")],
            "casting_speed_keep", "casting_slowdown_heat"
        ),
        (
            "10",
            "バイオ医薬品培養槽の溶存二酸化炭素（dCO2）管理基準。目標は『dCO2濃度40mmHg以上70mmHg以下かつスパージャー通気量0.1vvm以上』である。",
            "培養オンラインセンサ：dCO2は54mmHg、スパージャー通気量は0.15vvmである。通気ガス制御を判定せよ。",
            "培養オンラインセンサ：dCO2は88mmHgへ蓄積、スパージャー通気量は0.06vvmへ低下した。通気ガス制御を判定せよ。",
            [("bioreactor_gas_normal", "培養ガスバランス適合・通常通気維持"), ("bioreactor_aeration_boost", "CO2蓄積異常・スパージャー通気量急速増強"), ("bioreactor_media_feed", "グルコース培地連続添加開始")],
            "bioreactor_gas_normal", "bioreactor_aeration_boost"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k3_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_core_{gid}_s1",
                "group_id": f"rc3b_core_{gid}",
                "family": "core_rules",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_core_{gid}_s2",
                "group_id": f"rc3b_core_{gid}",
                "family": "core_rules",
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
            "浸漬冷却データセンターの絶縁油（合成フルード）絶縁破壊電圧判定。規格は『破壊電圧45kV以上かつ水分含有量30ppm以下』である。",
            "絶縁油定期オイル分析：破壊電圧は52kV、水分含有量は18ppmである。冷却ラック運用可否を判定せよ。",
            "絶縁油定期オイル分析：破壊電圧は38kV、水分含有量は42ppmである。冷却ラック運用可否を判定せよ。",
            [("coolant_fluid_pass", "絶縁性能適合・サーバー通電給電継続"), ("coolant_fluid_reject", "絶縁低下不適合・オイル循環脱水精製"), ("coolant_topup_wait", "油面レベル補充待機"), ("coolant_sample_retest", "予備フラスコ再分析委託")],
            "coolant_fluid_pass", "coolant_fluid_reject"
        ),
        (
            "12",
            "CVD半導体成膜装置のサセプタ（ウェハチャック）温度均一性基準。基準は『外周-中心間温度差ΔTが2.0℃以内かつヒーター応答時定数15秒以内』である。",
            "熱電対アレイ測定：測定ΔTは0.8℃、ヒーター応答は11秒を記録した。成膜レシピ実行可否を指示せよ。",
            "熱電対アレイ測定：測定ΔTは3.7℃に拡大、ヒーター応答は22秒へ遅延した。成膜レシピ実行可否を指示せよ。",
            [("cvd_recipe_execute", "均一性良好・CVD成膜レシピ実行開始"), ("cvd_zone_tune", "温度勾配不良・ゾーンヒーターPID補正停止"), ("cvd_wafer_unload", "ウェハ搬出カセット退避"), ("cvd_clean_standby", "チャンバーガスエッチング待機")],
            "cvd_recipe_execute", "cvd_zone_tune"
        ),
        (
            "13",
            "トンネルシールド掘進機の油圧推進ジャッキ推力バランス規則。基準は『左右推力偏差比が5%以内かつ掘進ピッチ20mm/min以上』である。",
            "掘進管理コンソール：左右推力偏差比は2.1%、掘進ピッチは24mm/minである。シールド推進制御を決定せよ。",
            "掘進管理コンソール：左右推力偏差比は8.4%へ偏向、掘進ピッチは12mm/minへ失速した。シールド推進制御を決定せよ。",
            [("shield_advance_nominal", "推力バランス良好・自動掘進推進続行"), ("shield_thrust_rebalance", "推力偏向逸脱・油圧ジャッキ圧力再配分"), ("shield_segment_erect", "セグメント組立てクレーン旋回待機"), ("shield_slurry_stop", "泥水送泥ポンプ一時休止")],
            "shield_advance_nominal", "shield_thrust_rebalance"
        ),
        (
            "14",
            "水力発電所調速機（ガバナー）の周波数ドループ応答規則。基準は『周波数偏差Δfに対する出力調整時間が3.0秒以内かつドループ整定値3.0%以上5.0%以下』である。",
            "電力系統擾乱シミュレーション：出力調整時間は2.1秒、ドループ整定値は4.0%を維持した。調速機能判定を下せ。",
            "電力系統擾乱シミュレーション：出力調整時間は4.8秒へ遅延、ドループ整定値は6.2%へ逸脱した。調速機能判定を下せ。",
            [("governor_cert_pass", "ガバナー応答適合・系統並入受電承認"), ("governor_recalibrate", "調速応答遅延・サーボPID整定再校正"), ("governor_manual_trip", "手動調速モード切替待機"), ("governor_valve_grease", "案内羽根スピンドル注油")],
            "governor_cert_pass", "governor_recalibrate"
        ),
        (
            "15",
            "臨床自動血液分析装置のフローサイトメトリー散乱光シグナル基準。基準は『前方散乱光FSC変動係数CVが4.0%以内かつ気泡フラグ未検知（0）』である。",
            "自己診断テスト結果：FSC変動係数CVは2.6%、気泡フラグは未検知（0）である。検体測定可否を判断せよ。",
            "自己診断テスト結果：FSC変動係数CVは6.3%へ悪化、気泡フラグが検知（1）された。検体測定可否を判断せよ。",
            [("analyzer_assay_ready", "光学系正常・患者検体バッチ測定開始"), ("analyzer_flush_cycle", "フローセル気泡混入・洗浄パージサイクル実行"), ("analyzer_lamp_replace", "励起半導体レーザー素子交換"), ("analyzer_reagent_prime", "シース液試薬プライミング充填")],
            "analyzer_assay_ready", "analyzer_flush_cycle"
        ),
        (
            "16",
            "高精度光学研磨における表面粗さ原子間力顕微鏡（AFM）検査基準。規格は『二乗平均面粗さRqが0.20nm以下かつスクラッチ欠陥数0個』である。",
            "AFMスキャンレポート：測定面粗さRqは0.12nm、スクラッチ欠陥は0個が確認された。光学素子判定を行え。",
            "AFMスキャンレポート：測定面粗さRqは0.31nm、スクラッチ欠陥が3箇所検出された。光学素子判定を行え。",
            [("optics_polish_pass", "超精密粗さ適合・次工程コーティング移送"), ("optics_repolish_req", "粗さ規格超過・修正研磨ラップ工程回送"), ("optics_ultrasonic_wash", "純水超音波脱脂洗浄待機"), ("optics_batch_scrap", "素材内部微小クラック判定廃棄")],
            "optics_polish_pass", "optics_repolish_req"
        ),
        (
            "17",
            "産業用六軸多関節溶接ロボットのアーク溶接モニタ基準。基準は『溶接電流180A以上210A以下かつシールドガス流量15L/min以上』である。",
            "溶接コントローラログ：実測電流は195A、ガス流量は18L/minである。自動溶接ライン処置を決定せよ。",
            "溶接コントローラログ：実測電流は165Aに低下、ガス流量は9L/minに激減した。自動溶接ライン処置を決定せよ。",
            [("welding_pass_continue", "アーク溶接正常・ワーク搬出シークエンス"), ("welding_gas_interlock", "ガス流量不足・溶接アーク停止およびインターロック"), ("welding_wire_feed", "溶接ワイヤトーチ自動繰り出し"), ("welding_tip_clean", "スパッター除去ノズルクリーニング")],
            "welding_pass_continue", "welding_gas_interlock"
        ),
        (
            "18",
            "薬品粉末乾式造粒打錠機のキャッパー成形圧力基準。基準は『主圧圧縮荷重12.0kN以上18.0kN以下かつ錠剤厚み偏差±0.05mm以内』である。",
            "打錠ロードセル測定：主圧荷重は15.2kN、厚み偏差は+0.02mmである。打錠工程運用を決定せよ。",
            "打錠ロードセル測定：主圧荷重は22.4kNへ異常過圧、厚み偏差は-0.11mmへ変動した。打錠工程運用を決定せよ。",
            [("tableting_run_normal", "打錠成形適合・充填包装ホッパー排出"), ("tableting_load_adjust", "圧縮過圧異常・打錠機ロール間隙再調整"), ("tableting_metal_detect", "金属異物混入センサー再検知"), ("tableting_lubricate_punch", "杵臼パンチ潤滑油滴下")],
            "tableting_run_normal", "tableting_load_adjust"
        ),
        (
            "19",
            "航空機炭素繊維複合材（CFRP）オートクレーブ硬化サイクル基準。基準は『昇温速度1.5℃/min以上2.5℃/min以下かつ加圧保持圧力0.60MPa以上』である。",
            "硬化データ記録：平均昇温速度は1.9℃/min、缶内圧力は0.65MPaを維持している。オートクレーブ制御を決定せよ。",
            "硬化データ記録：昇温速度は3.4℃/minへ急昇温、缶内圧力は0.48MPaへ失圧した。オートクレーブ制御を決定せよ。",
            [("autoclave_cure_proceed", "硬化サイクル適合・保温保持ステップ移行"), ("autoclave_vent_abort", "昇温過急および失圧・硬化中断排気モード"), ("autoclave_bag_retest", "真空バッグリーク再吸引確認"), ("autoclave_cool_quench", "強制窒素冷却ファン稼働")],
            "autoclave_cure_proceed", "autoclave_vent_abort"
        ),
        (
            "20",
            "大規模太陽光発電所（メガソーラー）の高圧受電インバータ単独運転検出基準。基準は『周波数変化率df/dtが1.0Hz/s以上または電圧ベクトル跳躍が10度以上で500ms以内に解列』である。",
            "系統過渡ログ：df/dtが1.8Hz/sを記録し、遮断機は280msで開放動作した。保護継電器動作を判定せよ。",
            "系統過渡ログ：df/dtは0.3Hz/s、電圧ベクトル跳躍は3度にとどまり、系統事故兆候は皆無である。保護継電器動作を判定せよ。",
            [("island_trip_verified", "単独運転検出合格・連系解列トリップ正当"), ("island_keep_intertied", "系統擾乱軽微・系統連系運転継続許可"), ("island_fault_log_clear", "過渡波形ログ消去・リセット操作"), ("island_reactive_support", "無効電力進相補償インバータ注入")],
            "island_trip_verified", "island_keep_intertied"
        ),
        (
            "21",
            "下水終末処理場の活性汚泥ディフューザー通気槽DO基準。基準は『溶存酸素DOが1.5mg/L以上2.5mg/L以下かつORP（酸化還元電位）が+100mV以上』である。",
            "水質計器データ：DOは2.0mg/L、ORPは+140mVである。曝気ブロワ制御を指示せよ。",
            "水質計器データ：DOは0.4mg/Lへ酸欠降下、ORPは-30mVへ嫌気化転落した。曝気ブロワ制御を指示せよ。",
            [("aeration_air_optimal", "好気消化正常・ブロワ現行風量維持"), ("aeration_blower_boost", "酸欠嫌気化・送風インバータ急速増量"), ("aeration_sludge_return", "余剰汚泥返送ポンプ停止"), ("aeration_coagulant_add", "凝集消泡剤滴下投入")],
            "aeration_air_optimal", "aeration_blower_boost"
        ),
        (
            "22",
            "超高真空（UHV）走査型トンネル顕微鏡（STM）の防振チャンバー基準。基準は『床振動速度RMSが0.5μm/s以下かつ音圧レベル40dB以下』である。",
            "振動音響計測：床振動RMSは0.28μm/s、室内音圧は34dBを記録した。原子分解能STM観測可否を決定せよ。",
            "振動音響計測：床振動RMSは1.42μm/sへ増幅、室内音圧は52dBへ上昇した。原子分解能STM観測可否を決定せよ。",
            [("stm_scan_authorized", "超低振動環境適合・原子イメージング観測開始"), ("stm_vibration_hold", "外部振動騒音過大・測定シーケンス待機保留"), ("stm_tip_retract", "STM探針クラッシュ防止自動退避"), ("stm_degas_filament", "脱ガスフィラメント通電通熱")],
            "stm_scan_authorized", "stm_vibration_hold"
        ),
        (
            "23",
            "生化学分析用マイクロ流路チップの送液シリンジポンプ流量基準。基準は『流速精度±1.5%以内かつ流路内気泡カウント0個』である。",
            "光学的流速センサ：流速精度偏差は+0.6%、気泡カウントは0個である。酵素反応試薬送液を実行せよ。",
            "光学的流速センサ：流速精度偏差は-4.2%、気泡カウントは5個検出された。酵素反応試薬送液を実行せよ。",
            [("microfluid_dispense_go", "流速安定・マイクロウェル滴下分注実行"), ("microfluid_prime_purge", "流量脈動気泡・プライミングパージ再充填"), ("microfluid_chip_eject", "流路詰まりチップ自動廃棄排出"), ("microfluid_zero_tare", "圧力トランスデューサ風袋引き")],
            "microfluid_dispense_go", "microfluid_prime_purge"
        ),
        (
            "24",
            "産業用ガスタービン発電設備の燃焼器排気NOx排出基準。基準は『NOx排出濃度25ppm以下（換算16%O2）かつ火炎安定度指数0.95以上』である。",
            "排ガス連続分析計（CEMS）：換算NOxは18.5ppm、火炎安定度は0.98である。燃焼制御を決定せよ。",
            "排ガス連続分析計（CEMS）：換算NOxは34.2ppmへ超過、火炎安定度は0.89へ動揺した。燃焼制御を決定せよ。",
            [("gas_turbine_combust_pass", "環境基準適合・発電定格負荷運転続行"), ("gas_turbine_water_inject", "NOx排出超過・水噴射ノズル弁開度増加"), ("gas_turbine_pilot_adjust", "パイロット燃料比率手動補正"), ("gas_turbine_flameout_trip", "失火警報・燃料遮断電磁弁閉止")],
            "gas_turbine_combust_pass", "gas_turbine_water_inject"
        ),
        (
            "25",
            "冷凍空調機向け冷媒充填ラインのヘリウムスニッファー漏洩検査基準。規格は『全漏洩量が1.0×10^-5 Pa・m3/s以下かつ真空到達度5Pa以下』である。",
            "質量分析計ヘリウム検出：漏洩量は3.2×10^-6 Pa・m3/s、到達真空度は2.8Paである。冷媒封入可否を判断せよ。",
            "質量分析計ヘリウム検出：漏洩量は8.5×10^-4 Pa・m3/sに急増、到達真空度は18Paにとどまった。冷媒封入可否を判断せよ。",
            [("refrigerant_charge_ok", "気密規格合格・HFO冷媒自動充填実行"), ("refrigerant_leak_fault", "漏洩過大不合格・ろう付け継手再検査"), ("refrigerant_pumpdown_retry", "真空引きポンプ再排気ステップ"), ("refrigerant_sensor_zero", "ヘリウム基準校正リーク調整")],
            "refrigerant_charge_ok", "refrigerant_leak_fault"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k4_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_core_{gid}_s1",
                "group_id": f"rc3b_core_{gid}",
                "family": "core_rules",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_core_{gid}_s2",
                "group_id": f"rc3b_core_{gid}",
                "family": "core_rules",
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
            "電子ビーム金属3D積層造形装置のチャンバー内不活性ガス基準。基準は『アルゴンガス純度99.999%以上かつ酸素濃度5.0ppm以下』である。",
            "ガス分析テレメトリ：実測Ar純度は99.9995%、酸素濃度は2.1ppmである。造形開始可否を判断せよ。",
            "ガス分析テレメトリ：実測Ar純度は99.985%、酸素濃度は14.8ppmである。造形開始可否を判断せよ。",
            [("am_build_start", "雰囲気高純度適合・金属粉末溶融造形開始"), ("am_argon_purge", "酸素混入不適合・アルゴンガス置換再パージ"), ("am_powder_rake", "リコータブレード粉末平滑化"), ("am_beam_align", "電子銃偏向コイルキャリブレーション"), ("am_bed_preheat", "造形ステージ予熱ヒーター昇温"), ("am_vacuum_seal", "ドアパッキン交換点検待機")],
            "am_build_start", "am_argon_purge"
        ),
        (
            "27",
            "水素燃料電池バス用70MPaCFRP複合容器の高速充填基準。基準は『水素充填圧力70.0MPa以上かつ充填時タンク内温度85.0℃以下』である。",
            "ディスペンサーデータ：タンク圧は72.4MPa、温度は68.2℃で充填完了した。車両発進許可を下せ。",
            "ディスペンサーデータ：タンク圧は71.0MPaに達したが、温度は89.5℃へ過熱した。車両発進許可を下せ。",
            [("fcv_dispense_complete", "充填安全規格適合・ノズル離脱および出庫承認"), ("fcv_overheat_cooling", "タンク過熱警報・冷却休止および安全弁点検"), ("fcv_pre_cool_retry", "プレクーリング熱交換器冷却強化"), ("fcv_nozzle_lock", "充填カプラーインターロック施錠"), ("fcv_pressure_bleed", "過充填水素ベント放出"), ("fcv_mass_flow_tare", "コリオリ流量計ゼロ点調整")],
            "fcv_dispense_complete", "fcv_overheat_cooling"
        ),
        (
            "28",
            "浮体式洋上風力発電プラットフォームのヒーブ動揺角基準。基準は『動揺ピッチ角±3.0度以内かつアンカーチェーン張力定格75%以下』である。",
            "浮体SCADAログ：動揺ピッチ角は±1.4度、アンカー張力は定格の58%である。風車発電制御を決定せよ。",
            "浮体SCADAログ：動揺ピッチ角は±5.2度に動揺、アンカー張力は定格の88%へ過負荷となった。風車発電制御を決定せよ。",
            [("floating_wind_generate", "浮体動揺許容内・最大電力追従発電継続"), ("floating_wind_feather", "荒天過動揺・ブレードフェザー停止および係留監視"), ("floating_ballast_trim", "バラスト水トリムポンプ移動"), ("floating_yaw_untangle", "ナセルヨー旋回ケーブル解線"), ("floating_brake_engage", "高速軸メカニカルブレーキ噛み合い"), ("floating_anemometer_cal", "ナセル超音波風速計校正")],
            "floating_wind_generate", "floating_wind_feather"
        ),
        (
            "29",
            "血液透析装置のダイアライザー透析液導電率・浸透圧基準。基準は『導電率13.5mS/cm以上14.5mS/cm以下かつ透析液温度36.0℃以上37.5℃以下』である。",
            "透析コンソール計測：実測導電率は13.9mS/cm、透析液温度は36.6℃である。透析治療開始可否を判断せよ。",
            "透析コンソール計測：実測導電率は15.2mS/cmに上昇、透析液温度は38.4℃に過昇温した。透析治療開始可否を判断せよ。",
            [("dialysis_treat_go", "透析液濃度適合・ダイアライザー血液灌流開始"), ("dialysis_bypass_alarm", "透析液浸透圧異常・バイパス流路切替警報"), ("dialysis_uf_rate_set", "除水ポンプ目標除水量設定"), ("dialysis_heparin_prime", "抗凝固剤ヘパリンラインプライミング"), ("dialysis_blood_leak_check", "血液漏れ検出光学センサーテスト"), ("dialysis_rinse_cycle", "酸性熱水消毒リンス待機")],
            "dialysis_treat_go", "dialysis_bypass_alarm"
        ),
        (
            "30",
            "半導体ウェット洗浄ステーションの超純水比抵抗・粒子数基準。基準は『比抵抗18.2MΩ・cm以上かつ0.05μm以上微粒子が10個/mL以下』である。",
            "水質モニタ報告：比抵抗は18.23MΩ・cm、0.05μm粒子数は3個/mLである。ロット洗浄実行可否を指示せよ。",
            "水質モニタ報告：比抵抗は17.6MΩ・cmへ低下、0.05μm粒子数は48個/mLへ急増した。ロット洗浄実行可否を指示せよ。",
            [("upw_rinse_proceed", "超純水高純度合格・半導体ウェハリンス開始"), ("upw_filter_replace", "水質純度規格外・限外ろ過膜交換および循環ブロー"), ("upw_uv_lamp_check", "紫外線殺菌ランプ照度点検"), ("upw_degas_membrane", "溶存ガス低減膜モジュール脱気"), ("upw_tank_overflow", "超純水サージタンクオーバーフロー開放"), ("upw_conductivity_zero", "比抵抗計電極セルゼロ点校正")],
            "upw_rinse_proceed", "upw_filter_replace"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k6_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_core_{gid}_s1",
                "group_id": f"rc3b_core_{gid}",
                "family": "core_rules",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_core_{gid}_s2",
                "group_id": f"rc3b_core_{gid}",
                "family": "core_rules",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2}
            }
        ])

    return pairs
