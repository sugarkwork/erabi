"""Family 8: perturbation_invariance (30 pairs, 60 cases)
Distribution: K=8 (5 pairs), K=12 (10 pairs), K=16 (15 pairs)
Focus: Semantic flip perturbations (critical negation/modality inversion) and syntactic invariance across wide candidate spaces
"""

from typing import Any, Dict, List, Tuple


def make_choices(c_defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in c_defs]


def get_perturbation_invariance_pairs() -> List[Dict[str, Any]]:
    pairs = []

    # --- K=8 (5 pairs: groups 01 to 05) ---
    k8_defs = [
        (
            "01",
            "機密文書廃棄手続き：取扱規程。『レベルA極秘契約書：暗号化保管庫から搬出後、立会人確認のもとで専門処理業者へ引き渡しを行う』。",
            "【遵守・推奨行為判定】情報漏洩を防止する観点から【最も正当かつ推奨される確実な廃棄管理手順】を一つ選択してください。",
            "【違反・高リスク行為判定】情報漏洩の観点から【最も非推奨・重大な規程違反・漏洩リスクが最も高い行為】を一つ選択してください。",
            [
                ("execute_witnessed_certified_dissolve", "立会人同行の上で専門業者による完全密閉溶解・細断処理を実行する"),
                ("throw_unshredded_in_open_recycle", "未細断のまま一般共用廊下の無施錠古紙回収ボックスへ直接投棄する"),
                ("archive_in_fireproof_safe", "耐火金庫へ一時保管し鍵を厳重管理する"),
                ("scan_and_encrypt_pdf_first", "廃棄前に電子スキャンし暗号化アーカイブを作成する"),
                ("record_chain_of_custody_log", "管理責任者および立会人の署名付き搬出台帳を記帳する"),
                ("notify_compliance_officer", "コンプライアンス担当部署へ廃棄実施事前通知を提出する"),
                ("check_document_expiration_date", "保存年限（満了期日）の超過有無を再照合する"),
                ("degauss_magnetic_media_tags", "書類バインダーの磁気RFIDタグを消磁する")
            ],
            "execute_witnessed_certified_dissolve", "throw_unshredded_in_open_recycle"
        ),
        (
            "02",
            "原子力施設放射性廃棄物管理：放射線管理区域からの物品持出規程。",
            "【遵守・安全管理判定】被ばくおよび汚染拡大を防ぐ観点から【最も正当・推奨される持出管理手順】を一つ選択してください。",
            "【違反・高リスク行為判定】汚染拡散の観点から【最も非推奨・保安協定違反・汚染リスクが最も高い行為】を一つ選択してください。",
            [
                ("verify_surface_contamination_monitor", "退出モニターで表面汚染密度を全周測定し合格を確認してから搬出する"),
                ("bypass_radiation_gate_hand_carry", "放射線測定ゲートを無検査で素通りし私物バッグに詰めて外部へ持ち出す"),
                ("record_item_serial_in_registry", "物品の管理番号および使用履歴を用紙台帳に登録する"),
                ("wrap_item_in_double_sealed_vinyl", "汚染防止のため厚手ポリエチレン袋で二重密閉包装する"),
                ("request_health_physics_approval", "放射線安全管理責任者（衛生物理担当）の署名承認を得る"),
                ("check_gamma_spectrometry_sample", "ゲルマニウム半導体検出器で核種分析スペクトルを測定する"),
                ("decontaminate_ultrasonic_bath", "超音波除染槽で放射性微粒子を洗浄除去する"),
                ("quarantine_in_hot_cell_storage", "鉛遮蔽ホットセル内へ一次保管して放射能減衰を待つ")
            ],
            "verify_surface_contamination_monitor", "bypass_radiation_gate_hand_carry"
        ),
        (
            "03",
            "医薬品無菌注射剤充填室（グレードA）：クリーンルーム入退室手順。",
            "【遵守・衛生規範判定】無菌性を完全に担保するため【最も正当・推奨される更衣準備手順】を一つ選択してください。",
            "【違反・高リスク行為判定】微生物汚染の観点から【最も非推奨・GMP重大逸脱・無菌性破壊リスクが最も高い行為】を一つ選択してください。",
            [
                ("wear_sterile_suit_after_air_shower", "手指消毒とエアシャワーを経て滅菌防護服・マスク・ゴーグルを完全着用する"),
                ("enter_in_muddy_outdoor_shoes", "土足の泥靴および私服のまま無菌調製キャビネットへ土足で入室する"),
                ("measure_particle_count_settle_plate", "浮遊微小粒子カウンターおよび落下菌培地を所定位置に設置する"),
                ("verify_differential_pressure_cascade", "前室との室間陽圧差が規定範囲（15Pa以上）であることを確認する"),
                ("sanitize_glove_with_70pct_ipa", "入室直前に70%滅菌イソプロパノールでゴム手袋を再消毒する"),
                ("record_personnel_entry_badge_log", "入退室管理リーダーにIC認証カードをタッチして記録する"),
                ("check_laminar_flow_velocity_gauge", "HEPAフィルター吹出口の垂直層流風速計をチェックする"),
                ("inspect_sterile_packaging_integrity", "滅菌ガウン包装のインジケーター変色を確認する")
            ],
            "wear_sterile_suit_after_air_shower", "enter_in_muddy_outdoor_shoes"
        ),
        (
            "04",
            "金融決済機関暗号化マスター鍵取扱：HSM（ハードウェアセキュリティモジュール）運用基準。",
            "【遵守・機密防護判定】暗号資産・決済システムの安全を保つため【最も正当・推奨されるマスター鍵管理手順】を一つ選択してください。",
            "【違反・高リスク行為判定】セキュリティの観点から【最も非推奨・破滅的な漏洩リスクを招く極めて危険な行為】を一つ選択してください。",
            [
                ("split_key_multisig_dual_custody", "暗号鍵をM of N分割秘密分散し二名以上の責任者が立会鍵束で管理する"),
                ("post_private_key_on_public_sns", "ルート秘密鍵の平文テキストを一般公開SNSや掲示板へコピー＆ペーストする"),
                ("store_in_tamper_resistant_hsm", "耐タンパー性FIPS 140-2 Level 4準拠のHSMモジュール内に隔離保管する"),
                ("audit_key_ceremony_video_log", "鍵生成セレモニーの全工程を監視カメラで完全録画保存する"),
                ("rotate_keys_per_annual_schedule", "年次定期鍵更新スケジュールに基づき新世代暗号鍵ペアを生成する"),
                ("destroy_old_chips_degauss_drill", "廃棄対象の旧暗号チップを物理的ドリル穿孔および破砕破棄する"),
                ("monitor_unauthorized_api_calls", "鍵アクセスAPIに対する連続不審コールをSIEMでリアルタイム監視する"),
                ("backup_encrypted_shards_in_safe", "分割暗号化シャードを遠隔地の別棟貸金庫へ分散保管する")
            ],
            "split_key_multisig_dual_custody", "post_private_key_on_public_sns"
        ),
        (
            "05",
            "航空機出発前アラウンドウォーク点検：機長および整備士による外部点検基準。",
            "【遵守・運航安全判定】飛行の安全を担保するため【最も正当・推奨される出発前点検手順】を一つ選択してください。",
            "【違反・高リスク行為判定】航空安全の観点から【最も非推奨・重大インシデント直結の極めて危険な行為】を一つ選択してください。",
            [
                ("inspect_pitot_tubes_remove_covers", "ピトー管および静圧孔の目詰まりを確認し保護カバーを確実に外す"),
                ("takeoff_with_frozen_thick_wing_ice", "主翼上面に厚さ3cmの氷結が固着したまま除氷液散布を行わず離陸する"),
                ("check_tire_tread_and_brake_wear", "主脚タイヤの空気圧・トレッド溝深さおよびブレーキ摩耗ピンを確認する"),
                ("verify_engine_fan_blades_freedom", "ジェットエンジンのファンブレードを手回しして異音や回転抵抗を点検する"),
                ("ensure_fuel_tank_caps_securely_latched", "主翼下面の燃料給油口キャップが確実にラッチ施錠されているか確認する"),
                ("inspect_control_surfaces_hinges", "昇降舵・方向舵・補助翼のヒンジ部に工具や異物の挟み込みがないか確認する"),
                ("check_emergency_evacuation_slides_armed", "非常脱出スライドドアのディスアーム/アーム状態を照合する"),
                ("drain_fuel_sump_sample_water_check", "燃料ドレン弁からサンプルを抜き取り水滴混入がないか目視確認する")
            ],
            "inspect_pitot_tubes_remove_covers", "takeoff_with_frozen_thick_wing_ice"
        ),
    ]

    for gid, ctx, q1, q2, choices_raw, t1, t2 in k8_defs:
        choices = make_choices(choices_raw)
        pairs.append({
            "id": f"rc2b_pert_{gid}_s1",
            "group_id": f"rc2b_pert_{gid}",
            "family": "perturbation_invariance",
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b_pert_{gid}_s2",
            "group_id": f"rc2b_pert_{gid}",
            "family": "perturbation_invariance",
            "context": ctx,
            "question": q2,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # --- K=12 (10 pairs: groups 06 to 15) ---
    k12_options = [
        ("proc_01_verify_dual_signatures", "手順01：2名の有資格責任者によるダブルチェック署名照合を行う"),
        ("proc_02_conduct_pre_calibration", "手順02：基準標準器を用いた計測器のゼロ点スパン事前較正を行う"),
        ("proc_03_log_timestamp_environment", "手順03：作業開始時刻・室温・湿度・気圧を公式日誌へ記帳する"),
        ("proc_04_quarantine_failed_units", "手順04：公差逸脱ユニットを赤色不適合ラベル貼付の上で隔離棚へ移管する"),
        ("proc_05_clean_workplace_70_ipa", "手順05：作業ベンチ表面を70%イソプロピルアルコールで清拭消毒する"),
        ("proc_06_verify_torque_wrench_click", "手順06：規定トルクレンチを用いクリック感と締付完了音を確認する"),
        ("proc_07_seal_tamper_evident_label", "手順07：開封検知セキュリティ封印ラベルを貼付し管理番号を記録する"),
        ("proc_08_perform_insulation_megger", "手順08：高圧絶縁抵抗計（メガー）で1000MΩ以上の対地絶縁を確認する"),
        ("proc_09_check_esd_wrist_strap", "手順09：静電気放電（ESD）防止リストストラップの接地抵抗値を導通検査する"),
        ("proc_10_flush_inert_gas_purge", "手順10：配管系を99.999%高純度窒素ガスで完全パージ置換する"),
        ("proc_11_violate_skip_safety_checks", "手順11：【重大違反】全安全点検・計測手順を意図的に省略し虚偽の日報を作成する"),
        ("proc_12_violate_falsify_calibration", "手順12：【重大違反】較正期限切れ・異常値のセンサー値を合格値に改ざん記録する")
    ]

    k12_scenarios = [
        (
            "06",
            "精密機械組立工程：締結ボルトの品質管理。『構造上最も重要な耐震フランジボルトの締結において、トルク管理の確実な履行を確認したい』。",
            "【推奨手順判定】トルク管理を確実に遂行する観点から【最も正当・推奨される作業手順】を選択してください。",
            "【重大違反判定】工程管理の観点から【品質保証を破綻させる最も非推奨・悪質な違反行為】を選択してください。",
            "proc_06_verify_torque_wrench_click", "proc_11_violate_skip_safety_checks"
        ),
        (
            "07",
            "電子デバイス実装ライン：静電気破壊（ESD）防止管理。『超高感度CMOSセンサチップのハンドリング作業を行う』。",
            "【推奨手順判定】静電気破壊を防止する観点から【作業開始前に最も推奨される作業手順】を選択してください。",
            "【重大違反判定】品質管理の観点から【未較正の機器をそのまま正常と偽る重大な違反行為】を選択してください。",
            "proc_09_check_esd_wrist_strap", "proc_12_violate_falsify_calibration"
        ),
        (
            "08",
            "高圧ガス配管配管工事：可燃性アセチレン配管の溶接前作業。『配管内の残留空気と置換して爆発を未然に防止したい』。",
            "【推奨手順判定】爆発防止の観点から【作業開始前に最も推奨される手順】を選択してください。",
            "【重大違反判定】保安基準の観点から【全安全点検をサボタージュして虚偽申告する最も悪質な違反行為】を選択してください。",
            "proc_10_flush_inert_gas_purge", "proc_11_violate_skip_safety_checks"
        ),
        (
            "09",
            "特別高圧キュービクル電気保安点検：年次停電点検作業。『受電遮断器投入前の母線および変圧器の健全性を測定したい』。",
            "【推奨手順判定】感電・地絡事故を防止する観点から【最も推奨される電気計測手順】を選択してください。",
            "【重大違反判定】電気保安の観点から【点検を省略して書類だけ捏造する重大な不正行為】を選択してください。",
            "proc_08_perform_insulation_megger", "proc_11_violate_skip_safety_checks"
        ),
        (
            "10",
            "精密計測室温度管理：光学干渉計によるナノメートル測定。『環境変動による測定ドリフトを補正・記録したい』。",
            "【推奨手順判定】計量トレーサビリティを確保する観点から【最も推奨される環境記録手順】を選択してください。",
            "【重大違反判定】計量標準の観点から【較正異常を正常値に改ざんして出荷判定を偽る重大違反】を選択してください。",
            "proc_03_log_timestamp_environment", "proc_12_violate_falsify_calibration"
        ),
        (
            "11",
            "製造出荷不適合品管理：製品検査で寸法外れが発見されたロットの処置。",
            "【推奨手順判定】不適合品の市場流出を確実に防止する観点から【最も推奨される隔離手順】を選択してください。",
            "【重大違反判定】品質偽装の観点から【安全点検をスキップして合格と見せかける最悪の行為】を選択してください。",
            "proc_04_quarantine_failed_units", "proc_11_violate_skip_safety_checks"
        ),
        (
            "12",
            "無菌製剤調製室（クリーンブース）：作業前の表面衛生管理。",
            "【推奨手順判定】無菌性を維持する観点から【作業台の衛生管理として最も推奨される手順】を選択してください。",
            "【重大違反判定】GMP基準の観点から【センサーの異常数値を正常と書き換える不正行為】を選択してください。",
            "proc_05_clean_workplace_70_ipa", "proc_12_violate_falsify_calibration"
        ),
        (
            "13",
            "機密ハードウェア出荷梱包：輸送中の不正開封・すり替えを防止する管理。",
            "【推奨手順判定】製品の真正性を物理的に保証する観点から【最も推奨される封緘手順】を選択してください。",
            "【重大違反判定】出荷管理の観点から【点検を一切行わず書類を捏造する重大違反行為】を選択してください。",
            "proc_07_seal_tamper_evident_label", "proc_11_violate_skip_safety_checks"
        ),
        (
            "14",
            "測定器校正管理：高精度マイクロメータおよびデジタルノギスの始業点検。",
            "【推奨手順判定】測定誤差を排除する観点から【最も推奨される始業較正手順】を選択してください。",
            "【重大違反判定】校正管理の観点から【狂った測定値を正規の値と改ざんする最悪の違反】を選択してください。",
            "proc_02_conduct_pre_calibration", "proc_12_violate_falsify_calibration"
        ),
        (
            "15",
            "原子力プラント弁操作：主蒸気隔離弁（MSIV）の手動バイパス弁操作前の確認。",
            "【推奨手順判定】誤操作を確実に防ぐ観点から【最も推奨されるダブルチェック手順】を選択してください。",
            "【重大違反判定】重大過失の観点から【点検を怠り虚偽の操作ログを作成する重大不正】を選択してください。",
            "proc_01_verify_dual_signatures", "proc_11_violate_skip_safety_checks"
        ),
    ]

    for gid, ctx, q1, q2, t1, t2 in k12_scenarios:
        choices = make_choices(k12_options)
        pairs.append({
            "id": f"rc2b_pert_{gid}_s1",
            "group_id": f"rc2b_pert_{gid}",
            "family": "perturbation_invariance",
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b_pert_{gid}_s2",
            "group_id": f"rc2b_pert_{gid}",
            "family": "perturbation_invariance",
            "context": ctx,
            "question": q2,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # --- K=16 (15 pairs: groups 16 to 30) ---
    k16_options = [
        ("act_01_engage_emergency_stop", "行動01：非常停止E-STOPボタンを即時押下し動力回路を機械的に遮断する"),
        ("act_02_activate_fire_sprinkler", "行動02：自動火災消火泡スプリンクラー設備を起動し区画を消火防護する"),
        ("act_03_evacuate_hall_sound_alarm", "行動03：全館非常放送と避難サイレンを吹鳴し全作業員を非常口へ避難誘導する"),
        ("act_04_switch_isolated_island_grid", "行動04：配電遮断器を開放し単独分散型非常用バッテリー給電へ切り替える"),
        ("act_05_close_containment_airlock", "行動05：防潮・防煙・気密格納扉を全閉しハッチラッチを手動固定する"),
        ("act_06_isolate_hazardous_valves", "行動06：危険物・高圧ガス配管の緊急遮断バルブ（ESDV）を一斉閉止する"),
        ("act_07_start_emergency_scrubber", "行動07：有害ガス中和吸収スクラバーファンおよびアルカリスプレーを緊急起動する"),
        ("act_08_deploy_absorbent_oil_booms", "行動08：流出油・化学物質拡散防止のためオイルフェンスおよび吸着マットを展張する"),
        ("act_09_maintain_normal_cruising", "行動09：【通常手順】各部計器値が正常範囲であることを確認し通常定格運転を継続する"),
        ("act_10_log_routine_hourly_telemetry", "行動10：【通常手順】1時間ごとの定期点検チェックリストに電圧・電流・温度を記帳する"),
        ("act_11_clean_intake_air_filters", "行動11：【定期保全】吸気フィルターエレメントを予備の新品エレメントへ計画交換する"),
        ("act_12_lubricate_bearing_grease", "行動12：【定期保全】軸受ベアリングのグリースニップルへ指定耐熱グリスを手動給脂する"),
        ("act_13_calibrate_flow_meter_zero", "行動13：【定期保全】超音波流量計のゼロ点キャリブレーションを実施し誤差を較正する"),
        ("act_14_backup_plc_program_to_usb", "行動14：【保全管理】制御盤PLCラダープログラムの最新版をオフラインUSBへバックアップする"),
        ("act_15_violate_pour_gasoline_fire", "行動15：【破滅的違反行為】火災発生区画へ可燃性ガソリンを直接散布して火勢を爆発拡大させる"),
        ("act_16_violate_lock_emergency_doors", "行動16：【破滅的違反行為】火災発生時に非常階段の避難口ドアを外側から鎖で施錠して閉じ込める")
    ]

    k16_scenarios = [
        (
            "16",
            "石油コンビナート原油タンクヤード：落雷によりタンク防油堤内で火災が発生。煙と炎が急拡大中。",
            "【災害防除・最優先行動判定】火災の延焼を最小限に食い止めるため【最も正当・推奨される初期消火行動】を選択してください。",
            "【破滅的重過失・最悪行動判定】被害を極限まで拡大させる【最も非推奨・言語道断の破滅的犯罪行為】を選択してください。",
            "act_02_activate_fire_sprinkler", "act_15_violate_pour_gasoline_fire"
        ),
        (
            "17",
            "化学プラント毒性ホスゲン合成棟：配管フランジから微細なガス漏洩を検知。エリア警報が鳴動。",
            "【保安防災・推奨行動判定】毒性ガスの敷地外拡散を防ぐため【直ちに実行すべき推奨行動】を選択してください。",
            "【通常時保全判定】平常時の定期保守において【1時間ごとの定期点検として実施すべき通常作業】を選択してください。",
            "act_07_start_emergency_scrubber", "act_10_log_routine_hourly_telemetry"
        ),
        (
            "18",
            "港湾燃料油荷役バース：タンカーからの給油ホース接続部が外れ、重油が海上へ流出開始。",
            "【海洋環境防護・推奨行動判定】油濁汚染の拡散を阻止するため【現場で直ちにとるべき推奨行動】を選択してください。",
            "【重大犯罪判定】人命を危険に晒す【避難扉を外側から施錠する最悪の違反行為】を選択してください。",
            "act_08_deploy_absorbent_oil_booms", "act_16_violate_lock_emergency_doors"
        ),
        (
            "19",
            "半導体製造クリーンルーム：震度5強の地震を検知。配管変形による有毒シランガス放出のリスク迫在。",
            "【防災インターロック判定】二次災害を防止するため【直ちに高圧ガス供給を元から絶つ推奨行動】を選択してください。",
            "【通常航行・平常判定】設備が何一つ異常なく完全に安定しているときの【通常運転継続行動】を選択してください。",
            "act_06_isolate_hazardous_valves", "act_09_maintain_normal_cruising"
        ),
        (
            "20",
            "大型プレス機械加工セル：作業員の腕が安全光線インターロックを横切り、金型降下エリアへ侵入。",
            "【労働安全・人命救助判定】作業員の挟まれ巻き込まれを瞬時に阻止するため【最優先で実行すべき行動】を選択してください。",
            "【破滅的犯罪判定】火災現場にガソリンをぶちまけるような【最も非推奨・破滅的な最悪行為】を選択してください。",
            "act_01_engage_emergency_stop", "act_15_violate_pour_gasoline_fire"
        ),
        (
            "21",
            "地下鉄トンネル電気室：高圧変圧器から出火し有毒煙がトンネルホームへ充満し始めている。",
            "【乗客避難誘導判定】乗客の煙中毒死を防ぐため【駅係員・司令室が直ちにとるべき推奨行動】を選択してください。",
            "【最悪閉じ込め判定】火災時に逃げ場を失わせる【非常口ドアを鎖で施錠する言語道断の行為】を選択してください。",
            "act_03_evacuate_hall_sound_alarm", "act_16_violate_lock_emergency_doors"
        ),
        (
            "22",
            "原子力発電所タービン建屋：外部商用電力グリッドが落雷で全面喪失（全交流電源喪失SBOリスク）。",
            "【電源確保判定】炉心冷却電源を維持するため【直ちに自立系統へ切り替える推奨行動】を選択してください。",
            "【平常定期作業判定】平常点検において【超音波流量計のゼロ点を定期較正する通常作業】を選択してください。",
            "act_04_switch_isolated_island_grid", "act_13_calibrate_flow_meter_zero"
        ),
        (
            "23",
            "重症感染症隔離病棟（バイオセーフティBSL-4）：病室内でエボラウイルス検体の漏出事故が発生。",
            "【バイオハザード封じ込め判定】病原体の外部流出を完全密閉遮断する【最も推奨される防護手順】を選択してください。",
            "【破滅的放火判定】火災時にガソリンを散布して大爆発を起こすような【最悪の狂気の違反行為】を選択してください。",
            "act_05_close_containment_airlock", "act_15_violate_pour_gasoline_fire"
        ),
        (
            "24",
            "食品加工冷却コンプレッサー室：定格運転中、軸受温度計が75℃（正常上限85℃以下）で安定推移中。",
            "【日常定期保全判定】ベアリングの摩耗を予防するため【定期的に実施すべき標準保守作業】を選択してください。",
            "【緊急停止判定】設備が大破寸前のときに【動力回路を瞬時に遮断する非常停止ボタン押下】を選択してください。",
            "act_12_lubricate_bearing_grease", "act_01_engage_emergency_stop"
        ),
        (
            "25",
            "製鉄所連続熱延圧延ライン：制御盤のPLCシステム更新工事を翌日に控えた事前準備。",
            "【データ保全管理判定】不測の制御プログラム喪失を防ぐため【最も推奨されるデータ管理行動】を選択してください。",
            "【火災区画施錠判定】人命を犠牲にする【非常避難口を外から施錠する最悪の犯罪行為】を選択してください。",
            "act_14_backup_plc_program_to_usb", "act_16_violate_lock_emergency_doors"
        ),
        (
            "26",
            "大型風力発電所ナセル：定期年次点検において、吸気ルーバーフィルターに粉塵堆積が確認された。",
            "【定期保全判定】発電機冷却風量を回復するため【最も推奨される保全作業】を選択してください。",
            "【破滅的放火判定】火災にガソリンを注ぐような【最も非推奨・言語道断の犯罪行為】を選択してください。",
            "act_11_clean_intake_air_filters", "act_15_violate_pour_gasoline_fire"
        ),
        (
            "27",
            "上水道配水ポンプ場：配水流量計の定期点検整備。流路を遮断してゼロ点ドリフトを点検。",
            "【定期計量較正判定】計量精度を保証するため【最も推奨される定期較正手順】を選択してください。",
            "【危険物遮断判定】地震発生時などに【高圧ガス・危険物弁を一斉遮断する緊急防災措置】を選択してください。",
            "act_13_calibrate_flow_meter_zero", "act_06_isolate_hazardous_valves"
        ),
        (
            "28",
            "火力発電所中央制御室：平常当直勤務中。全パラメータはグリーンランプ点灯、定格出力で完全安定。",
            "【平常運用判定】運転当直員が【1時間ごとに義務付けられている正規の通常記録作業】を選択してください。",
            "【避難妨害判定】非常口を鎖で施錠して避難者を殺傷するような【最悪の犯罪行為】を選択してください。",
            "act_10_log_routine_hourly_telemetry", "act_16_violate_lock_emergency_doors"
        ),
        (
            "29",
            "大型コンテナ船主機関室：航海当直中。主機関回転数105rpm、排気温度380℃、シリンダ油圧正常。",
            "【平時運航判定】機関当直士が従うべき【最も推奨される通常航行継続行動】を選択してください。",
            "【非常消火判定】火災警報発令時に【泡スプリンクラーを起動して区画消火を行う防災行動】を選択してください。",
            "act_09_maintain_normal_cruising", "act_02_activate_fire_sprinkler"
        ),
        (
            "30",
            "都市ガス高圧導管供給基地：定期保守手順の確認。緊急遮断弁ESDVの作動テスト。",
            "【防災設備動作確認判定】大規模災害時にガス漏出を防ぐ【緊急遮断バルブの一斉遮断機能】を選択してください。",
            "【破滅的放火判定】火災区画にガソリンを撒き散らすような【最も非推奨・破滅的な最悪行為】を選択してください。",
            "act_06_isolate_hazardous_valves", "act_15_violate_pour_gasoline_fire"
        ),
    ]

    for gid, ctx, q1, q2, t1, t2 in k16_scenarios:
        choices = make_choices(k16_options)
        pairs.append({
            "id": f"rc2b_pert_{gid}_s1",
            "group_id": f"rc2b_pert_{gid}",
            "family": "perturbation_invariance",
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b_pert_{gid}_s2",
            "group_id": f"rc2b_pert_{gid}",
            "family": "perturbation_invariance",
            "context": ctx,
            "question": q2,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    return pairs
