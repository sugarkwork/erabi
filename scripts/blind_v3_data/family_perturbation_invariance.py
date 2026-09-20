"""Family 8: perturbation_invariance (30 pairs, 60 cases) - Blind v3
Distribution: K=8 (5 pairs), K=12 (10 pairs), K=16 (15 pairs)
Prefix: rc2b3_pert_
Focus: Semantic flip perturbations (critical negation/modality inversion) and syntactic invariance across wide candidate spaces.
Optimized concise choice texts to guarantee strict token count <= 350 (< 512 limit).
"""

from typing import Any, Dict, List, Tuple


def make_choices(c_defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in c_defs]


def get_perturbation_invariance_pairs() -> List[Dict[str, Any]]:
    pairs = []

    # --- K=8 (5 pairs: groups 01 to 05) with concise choices ---
    k8_defs = [
        (
            "01",
            "機密文書廃棄手続き：取扱規程。『レベルA極秘契約書：暗号化保管庫から搬出後、立会人確認のもとで専門処理業者へ引き渡しを行う』。",
            "【遵守・推奨行為判定】情報漏洩を防止する観点から【最も正当かつ推奨される確実な廃棄管理手順】を一つ選択してください。",
            "【違反・高リスク行為判定】情報漏洩の観点から【最も非推奨・重大な規程違反・漏洩リスクが最も高い行為】を一つ選択してください。",
            [
                ("execute_witnessed_certified_dissolve", "立会人同行での密閉溶解・細断処理"),
                ("throw_unshredded_in_open_recycle", "未細断で共用古紙回収ボックス投棄"),
                ("archive_in_fireproof_safe", "耐火金庫へ一時保管し鍵を管理"),
                ("scan_and_encrypt_pdf_first", "電子スキャンし暗号化保管"),
                ("record_chain_of_custody_log", "管理責任者署名付き台帳記帳"),
                ("notify_compliance_officer", "コンプライアンス部署へ事前通知"),
                ("check_document_expiration_date", "保存年限満了期日を再照合"),
                ("degauss_magnetic_media_tags", "書類バインダーRFIDタグ消磁")
            ],
            "execute_witnessed_certified_dissolve", "throw_unshredded_in_open_recycle"
        ),
        (
            "02",
            "原子力施設放射性廃棄物管理：放射線管理区域からの物品持出規程。",
            "【遵守・安全管理判定】被ばくおよび汚染拡大を防ぐ観点から【最も正当・推奨される持出管理手順】を一つ選択してください。",
            "【違反・高リスク行為判定】汚染拡散の観点から【最も非推奨・保安協定違反・汚染リスクが最も高い行為】を一つ選択してください。",
            [
                ("verify_surface_contamination_monitor", "退出モニターで表面汚染を測定確認"),
                ("bypass_radiation_gate_hand_carry", "測定ゲートを無検査素通りで持出"),
                ("record_item_serial_in_registry", "物品管理番号を用紙台帳に登録"),
                ("wrap_item_in_double_sealed_vinyl", "厚手ポリエチレン袋で二重密閉"),
                ("request_health_physics_approval", "放射線安全管理責任者の署名承認"),
                ("check_gamma_spectrometry_sample", "半導体検出器で核種分析スペクトル測定"),
                ("decontaminate_ultrasonic_bath", "超音波除染槽で放射性微粒子洗浄"),
                ("quarantine_in_hot_cell_storage", "遮蔽ホットセル内で放射能減衰保管")
            ],
            "verify_surface_contamination_monitor", "bypass_radiation_gate_hand_carry"
        ),
        (
            "03",
            "医薬品無菌注射剤充填室（グレードA）：クリーンルーム入退室手順。",
            "【遵守・衛生規範判定】無菌性を完全に担保するため【最も正当・推奨される更衣準備手順】を一つ選択してください。",
            "【違反・高リスク行為判定】微生物汚染の観点から【最も非推奨・GMP重大逸脱・無菌性破壊リスクが最も高い行為】を一つ選択してください。",
            [
                ("wear_sterile_suit_after_air_shower", "エアシャワー経て滅菌防護服完全着用"),
                ("enter_in_muddy_outdoor_shoes", "土足の泥靴・私服のまま無菌室入室"),
                ("measure_particle_count_settle_plate", "微粒子カウンター・落下菌培地設置"),
                ("verify_differential_pressure_cascade", "前室との陽圧差15Pa以上を確認"),
                ("sanitize_glove_with_70pct_ipa", "70%滅菌IPAで手袋を再消毒"),
                ("record_personnel_entry_badge_log", "入退室管理リーダーにICカード認証"),
                ("check_laminar_flow_velocity_gauge", "HEPAフィルター層流風速計チェック"),
                ("inspect_sterile_packaging_integrity", "滅菌ガウン包装インジケーター確認")
            ],
            "wear_sterile_suit_after_air_shower", "enter_in_muddy_outdoor_shoes"
        ),
        (
            "04",
            "金融決済機関暗号化マスター鍵取扱：HSM（ハードウェアセキュリティモジュール）運用基準。",
            "【遵守・機密防護判定】暗号資産・決済システムの安全を保つため【最も正当・推奨されるマスター鍵管理手順】を一つ選択してください。",
            "【違反・高リスク行為判定】セキュリティの観点から【最も非推奨・破滅的な漏洩リスクを招く極めて危険な行為】を一つ選択してください。",
            [
                ("split_key_multisig_dual_custody", "暗号鍵を分割秘密分散し複数人で管理"),
                ("post_private_key_on_public_sns", "秘密鍵平文を一般公開SNSへ投稿"),
                ("store_in_tamper_resistant_hsm", "耐タンパー性HSMモジュール内隔離"),
                ("audit_key_ceremony_video_log", "鍵生成セレモニーの録画記録保存"),
                ("rotate_keys_per_annual_schedule", "年次定期鍵更新で新暗号鍵ペア生成"),
                ("destroy_old_chips_degauss_drill", "廃棄対象旧チップのドリル穿孔破砕"),
                ("monitor_unauthorized_api_calls", "鍵アクセス不審コールをSIEM監視"),
                ("backup_encrypted_shards_in_safe", "分割シャードを別棟金庫へ分散保管")
            ],
            "split_key_multisig_dual_custody", "post_private_key_on_public_sns"
        ),
        (
            "05",
            "航空機出発前アラウンドウォーク点検：機長および整備士による外部点検基準。",
            "【遵守・運航安全判定】飛行の安全を担保するため【最も正当・推奨される出発前点検手順】を一つ選択してください。",
            "【違反・高リスク行為判定】航空安全の観点から【最も非推奨・重大インシデント直結の極めて危険な行為】を一つ選択してください。",
            [
                ("inspect_pitot_tubes_remove_covers", "ピトー管目詰まり点検・カバー取外"),
                ("takeoff_with_frozen_thick_wing_ice", "主翼に3cm氷結固着のまま離陸"),
                ("check_tire_tread_and_brake_wear", "主脚タイヤ空気圧・ブレーキ摩耗確認"),
                ("verify_engine_fan_blades_freedom", "ジェットエンジンファン手回し点検"),
                ("ensure_fuel_tank_caps_securely_latched", "主翼下面燃料給油口キャップ施錠確認"),
                ("inspect_control_surfaces_hinges", "動翼ヒンジ部の異物挟み込み点検"),
                ("check_emergency_evacuation_slides_armed", "非常脱出スライドドア状態照合"),
                ("drain_fuel_sump_sample_water_check", "燃料ドレン弁から水分混入確認")
            ],
            "inspect_pitot_tubes_remove_covers", "takeoff_with_frozen_thick_wing_ice"
        ),
    ]

    for gid, ctx, q1, q2, choices_raw, t1, t2 in k8_defs:
        choices = make_choices(choices_raw)
        pairs.append({
            "id": f"rc2b3_pert_{gid}_s1",
            "group_id": f"rc2b3_pert_{gid}",
            "family": "perturbation_invariance",
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b3_pert_{gid}_s2",
            "group_id": f"rc2b3_pert_{gid}",
            "family": "perturbation_invariance",
            "context": ctx,
            "question": q2,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # --- K=12 (10 pairs: groups 06 to 15) with concise choices ---
    k12_options = [
        ("proc_01_verify_dual_signatures", "手順01（2名ダブルチェック署名）"),
        ("proc_02_conduct_pre_calibration", "手順02（基準器による事前較正）"),
        ("proc_03_log_timestamp_environment", "手順03（作業開始時刻・環境記帳）"),
        ("proc_04_quarantine_failed_units", "手順04（不適合品の赤札隔離移管）"),
        ("proc_05_clean_workplace_70_ipa", "手順05（70%IPA作業台清拭消毒）"),
        ("proc_06_verify_torque_wrench_click", "手順06（規定トルク締付完了確認）"),
        ("proc_07_seal_tamper_evident_label", "手順07（開封検知封印ラベル貼付）"),
        ("proc_08_perform_insulation_megger", "手順08（メガー高圧絶縁抵抗測定）"),
        ("proc_09_check_esd_wrist_strap", "手順09（静電防止リストバンド検査）"),
        ("proc_10_flush_inert_gas_purge", "手順10（高純度窒素パージ置換）"),
        ("proc_11_violate_skip_safety_checks", "手順11（点検省略・虚偽日報作成）"),
        ("proc_12_violate_falsify_calibration", "手順12（較正異常値の合格改ざん）")
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
            "id": f"rc2b3_pert_{gid}_s1",
            "group_id": f"rc2b3_pert_{gid}",
            "family": "perturbation_invariance",
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b3_pert_{gid}_s2",
            "group_id": f"rc2b3_pert_{gid}",
            "family": "perturbation_invariance",
            "context": ctx,
            "question": q2,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # --- K=16 (15 pairs: groups 16 to 30) with concise choices ---
    k16_options = [
        ("act_01_engage_emergency_stop", "行動01（非常停止ボタン即時押下）"),
        ("act_02_activate_fire_sprinkler", "行動02（自動泡消火設備起動）"),
        ("act_03_evacuate_hall_sound_alarm", "行動03（全館避難サイレン吹鳴）"),
        ("act_04_switch_isolated_island_grid", "行動04（非常用独立電源へ切替）"),
        ("act_05_close_containment_airlock", "行動05（防煙気密扉を全閉固定）"),
        ("act_06_isolate_hazardous_valves", "行動06（緊急遮断バルブ一斉閉止）"),
        ("act_07_start_emergency_scrubber", "行動07（有害排ガス吸収装置起動）"),
        ("act_08_deploy_absorbent_oil_booms", "行動08（油拡散防止フェンス展張）"),
        ("act_09_maintain_normal_cruising", "行動09（通常定格運転を継続）"),
        ("act_10_log_routine_hourly_telemetry", "行動10（定期チェックリスト記帳）"),
        ("act_11_clean_intake_air_filters", "行動11（吸気フィルター新品交換）"),
        ("act_12_lubricate_bearing_grease", "行動12（軸受ベアリング手動給脂）"),
        ("act_13_calibrate_flow_meter_zero", "行動13（流量計ゼロ点キャリブ）"),
        ("act_14_backup_plc_program_to_usb", "行動14（制御PLCプログラム退避）"),
        ("act_15_violate_pour_gasoline_fire", "行動15（火災区画へのガソリン散布）"),
        ("act_16_violate_lock_emergency_doors", "行動16（非常口ドアを鎖で施錠）")
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
            "id": f"rc2b3_pert_{gid}_s1",
            "group_id": f"rc2b3_pert_{gid}",
            "family": "perturbation_invariance",
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b3_pert_{gid}_s2",
            "group_id": f"rc2b3_pert_{gid}",
            "family": "perturbation_invariance",
            "context": ctx,
            "question": q2,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    return pairs
