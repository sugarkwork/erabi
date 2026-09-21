"""Family 2: logical_operators (30 pairs, 60 cases) - RC3 Bridge Benchmark
Prefix: rc3b_op_
Distribution: K=2 (15 pairs), K=3 (10 pairs), K=4 (5 pairs)
Focus: Truth-table discernment, logical operators (AND, OR, NOT, NOR, XOR, NAND), condition polarity reversal.
Zero leakage against all past datasets.
"""

from typing import Any, Dict, List, Tuple


def make_choices(c_defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in c_defs]


def get_logical_operators_pairs() -> List[Dict[str, Any]]:
    pairs: List[Dict[str, Any]] = []

    # --- K=2 (15 pairs: groups 01 to 15) ---
    k2_defs = [
        (
            "01",
            "航空電子航法データバスの二重系統ステータス：主系統バスAは正常通信中（True）、副系統バスBは通信途絶（False）。",
            "論理ルール：『主系統バスAと副系統バスBの両方が正常（AND）』のとき『全二重冗長モードを維持』、片方でも不成立なら『単一系統フォールバックへ移行』。指示せよ。",
            "論理ルール：『主系統バスAまたは副系統バスBの少なくとも一方が正常（OR）』のとき『全二重冗長モードを維持』、両方途絶なら『単一系統フォールバックへ移行』。指示せよ。",
            [("bus_dual_redundant", "全二重冗長モードを維持"), ("bus_single_fallback", "単一系統フォールバックへ移行")],
            "bus_single_fallback", "bus_dual_redundant"
        ),
        (
            "02",
            "バイオクリーンルーム前室のインターロック扉ステータス：第1扉（外側）は開扉検知（True）、第2扉（内側）は閉止状態（False）。",
            "論理ルール：『第1扉と第2扉の双方が同時に閉止（NOR）』のときのみ『前室UV殺菌照射を開始』、いずれかが開いていれば『殺菌照射インターロック停止』。判定せよ。",
            "論理ルール：『第1扉または第2扉のどちらか一方のみが開扉（XOR）』のときは『前室UV殺菌照射を開始』、両方開扉または両方閉止なら『殺菌照射インターロック停止』。判定せよ。",
            [("airlock_uv_run", "前室UV殺菌照射を開始"), ("airlock_uv_block", "殺菌照射インターロック停止")],
            "airlock_uv_block", "airlock_uv_run"
        ),
        (
            "03",
            "ガスタービン発電機失火検知センサー：光学的火炎検出器は受光検知（True）、音響燃焼振動センサーも燃焼振動検知（True）。",
            "論理ルール：『光検出器と音響センサーの検出結果が不一致（XOR）』のとき『センサー不整合警報を出力』、一致しているときは『火炎判定正常維持』。決定せよ。",
            "論理ルール：『光検出器と音響センサーの双方が非検知（NOR）』のとき『センサー不整合警報を出力』、少なくとも一方が検知なら『火炎判定正常維持』。決定せよ。",
            [("flame_mismatch_alarm", "センサー不整合警報を出力"), ("flame_steady_normal", "火炎判定正常維持")],
            "flame_steady_normal", "flame_steady_normal"
        ),
        (
            "04",
            "産業用大型冷凍倉庫の冷媒アンモニア漏洩検知器：ゾーン1検知器は基準内（False＝非検知）、ゾーン2検知器も基準内（False＝非検知）。",
            "論理ルール：『ゾーン1またはゾーン2のいずれか一方でも漏洩検知（OR）』されたときは『強制緊急排風機を作動』、両方とも非検知なら『換気ファン通常維持』。判定せよ。",
            "論理ルール：『ゾーン1およびゾーン2の双方が漏洩検知（AND）』のときのみ『換気ファン通常維持』、未成立なら『強制緊急排風機を作動』。判定せよ。",
            [("nh3_fan_boost", "強制緊急排風機を作動"), ("nh3_fan_normal", "換気ファン通常維持")],
            "nh3_fan_normal", "nh3_fan_boost"
        ),
        (
            "05",
            "無人自動搬送台車（AGV）の安全停止信号：バンパー接触スイッチは非作動（False）、レーザースキャナー減速エリア物体検知は作動中（True）。",
            "論理ルール：『バンパー接触またはレーザースキャナー検知のいずれか一方でも成立（OR）』したときは『減速クリープ走行モードへ移行』、両方不成立なら『定格速度走行維持』。指示せよ。",
            "論理ルール：『バンパー接触かつレーザースキャナー検知の双方が成立（AND）』のときのみ『減速クリープ走行モードへ移行』、それ以外なら『定格速度走行維持』。指示せよ。",
            [("agv_creep_mode", "減速クリープ走行モードへ移行"), ("agv_cruise_keep", "定格速度走行維持")],
            "agv_creep_mode", "agv_cruise_keep"
        ),
        (
            "06",
            "変電所高圧遮断器（VCB）の自動投入シーケンス：母線電圧健全フラグは確立（True）、保護継電器動作ロックフラグは解除（False）。",
            "論理ルール：『母線電圧が確立かつ保護継電器ロックが解除（A AND NOT B）』のときのみ『遮断器自動投入シーケンスを開始』、それ以外なら『投入阻止待機』。判定せよ。",
            "論理ルール：『保護継電器ロック解除かつ母線電圧未確立（NOT A AND NOT B）』のときのみ『遮断器自動投入シーケンスを開始』、それ以外なら『投入阻止待機』。判定せよ。",
            [("vcb_close_sequence", "遮断器自動投入シーケンスを開始"), ("vcb_close_inhibit", "投入阻止待機")],
            "vcb_close_sequence", "vcb_close_inhibit"
        ),
        (
            "07",
            "データバックアップ整合性チェック：SHA-256ダイジェストは一致（True）、ファイルサイズバイト数は一致（True）。",
            "論理ルール：『ハッシュ不一致またはサイズ不一致のいずれか一方でも発生（NAND：否定論理積）』のときは『再送リカバリを実行』、両方一致なら『整合性承認』。判定せよ。",
            "論理ルール：『ハッシュ一致かつサイズ一致の両方が成立（AND）』のとき『整合性承認』、それ以外なら『再送リカバリを実行』。判定せよ。",
            [("backup_sync_pass", "整合性承認"), ("backup_resync_retry", "再送リカバリを実行")],
            "backup_sync_pass", "backup_sync_pass"
        ),
        (
            "08",
            "自動車自動ブレーキシステムの歩行者検知：単眼カメラ画像認識は歩行者検出（True）、ミリ波レーダーは未検出（False）。",
            "論理ルール：『単眼カメラとミリ波レーダーの判定が不一致（XOR）』のときは『センサーフュージョン詳細追跡モードへ移行』、一致なら『現行判定を確定』。指示せよ。",
            "論理ルール：『単眼カメラとミリ波レーダーの判定が一致（XNOR）』のときは『センサーフュージョン詳細追跡モードへ移行』、不一致なら『現行判定を確定』。指示せよ。",
            [("fusion_track_detail", "センサーフュージョン詳細追跡モードへ移行"), ("fusion_confirm_decision", "現行判定を確定")],
            "fusion_track_detail", "fusion_confirm_decision"
        ),
        (
            "09",
            "医薬品凍結乾燥機（フリーズドライヤー）の真空開放判定：乾燥時間完了タイマーは満了（True）、棚板復圧弁開度センサは閉止（False）。",
            "論理ルール：『乾燥時間満了かつ復圧弁閉止（A AND NOT B）』のとき『乾燥終了承認・窒素復圧ベント開始』、それ以外は『工程維持』。判定せよ。",
            "論理ルール：『乾燥時間満了かつ復圧弁開放（A AND B）』のとき『乾燥終了承認・窒素復圧ベント開始』、それ以外は『工程維持』。判定せよ。",
            [("lyo_vent_proceed", "乾燥終了承認・窒素復圧ベント開始"), ("lyo_maintain_cycle", "工程維持")],
            "lyo_vent_proceed", "lyo_maintain_cycle"
        ),
        (
            "10",
            "LNGタンカー積込アーム緊急離脱システム（ERS）：積込バルブ閉止完了信号は未完了（False）、アーム位置リミットスイッチ超過は未超過（False）。",
            "論理ルール：『バルブ閉止完了かつ位置リミット正常（A AND NOT B）』のときのみ『手動ディスコネクト許可』、そうでなければ『ディスコネクト不可』。決定せよ。",
            "論理ルール：『バルブ未閉止または位置リミット正常（NOT A OR NOT B）』のときのみ『手動ディスコネクト許可』、両方未成立なら『ディスコネクト不可』。決定せよ。",
            [("ers_disconnect_ready", "手動ディスコネクト許可"), ("ers_disconnect_locked", "ディスコネクト不可")],
            "ers_disconnect_locked", "ers_disconnect_ready"
        ),
        (
            "11",
            "工作機械マシニングセンタの主軸保護：潤滑油圧低下警報は非作動（False）、スピンドル過負荷トルク検出は非作動（False）。",
            "論理ルール：『油圧低下警報も過負荷トルクも共に発生していない（NOR）』ときは『自動切削サイクル継続』、いずれか発生時は『主軸回転停止』。判定せよ。",
            "論理ルール：『油圧低下警報も過負荷トルクも共に非作動（NOR）』のときは『主軸回転停止』、何らかの作動時は『自動切削サイクル継続』。判定せよ。",
            [("machining_continue_cut", "自動切削サイクル継続"), ("machining_spindle_stop", "主軸回転停止")],
            "machining_continue_cut", "machining_spindle_stop"
        ),
        (
            "12",
            "高所クレーン作業の風速警報：瞬間最大風速15m/s超過フラグは成立（True）、作業責任者強風中止指示フラグは未指示（False）。",
            "論理ルール：『15m/s超過または責任者中止指示のいずれか一方でも成立（OR）』のときは『揚重作業即時中止・ジブ旋回固定』、両方不成立なら『作業続行』。判定せよ。",
            "論理ルール：『15m/s超過かつ責任者中止指示の双方が成立（AND）』のときのみ『揚重作業即時中止・ジブ旋回固定』、そうでなければ『作業続行』。判定せよ。",
            [("crane_halt_typhoon", "揚重作業即時中止・ジブ旋回固定"), ("crane_safe_continue", "作業続行")],
            "crane_halt_typhoon", "crane_safe_continue"
        ),
        (
            "13",
            "リチウムイオン蓄電システムのセル保護基盤（BMS）：第1セル過充電検出は作動（True）、第2セル過充電検出も作動（True）。",
            "論理ルール：『第1セル過充電と第2セル過充電の不一致（XOR）』のときは『個別セル診断モードへ移行』、一致しているときは『充電コンタクタ即時遮断トリップ』。指示せよ。",
            "論理ルール：『第1セル過充電かつ第2セル過充電（AND）』のときは『個別セル診断モードへ移行』、それ以外なら『充電コンタクタ即時遮断トリップ』。指示せよ。",
            [("bms_individual_diag", "個別セル診断モードへ移行"), ("bms_master_trip", "充電コンタクタ即時遮断トリップ")],
            "bms_master_trip", "bms_individual_diag"
        ),
        (
            "14",
            "半導体クリーンルーム排気スクラバー：酸性排気中和液循環ポンプ作動は作動中（True）、pH中和不全警報は発生中（True）。",
            "論理ルール：『ポンプ作動中かつpH中和不全警報（A AND B）』のときは『中和薬液緊急追加注入ポンプを起動』、警報未発生なら『スクラバー系統警報を発報』。指示せよ。",
            "論理ルール：『ポンプ停止（NOT A）または中和不全警報発生（B）』のときは『スクラバー系統警報を発報』、それ以外なら『中和薬液緊急追加注入ポンプを起動』。指示せよ。",
            [("scrubber_emergency_dosing", "中和薬液緊急追加注入ポンプを起動"), ("scrubber_alarm_broadcast", "スクラバー系統警報を発報")],
            "scrubber_emergency_dosing", "scrubber_alarm_broadcast"
        ),
        (
            "15",
            "高速道路トンネル内非常設備監視：非常口扉開放フラグは未開放（False）、押しボタン式通報装置作動フラグは未作動（False）。",
            "論理ルール：『非常口開放または通報装置作動のいずれか一方でも発生（OR）』したときは『トンネル進入禁止赤信号を作動』、両方未発生なら『通常青信号維持』。指示せよ。",
            "論理ルール：『非常口開放または通報装置作動のいずれか一方でも未発生（NAND）』のときは『トンネル進入禁止赤信号を作動』、両方発生なら『通常青信号維持』。指示せよ。",
            [("tunnel_red_inhibit", "トンネル進入禁止赤信号を作動"), ("tunnel_green_clear", "通常青信号維持")],
            "tunnel_green_clear", "tunnel_red_inhibit"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k2_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_op_{gid}_s1",
                "group_id": f"rc3b_op_{gid}",
                "family": "logical_operators",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_op_{gid}_s2",
                "group_id": f"rc3b_op_{gid}",
                "family": "logical_operators",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2}
            }
        ])

    # --- K=3 (10 pairs: groups 16 to 25) ---
    k3_defs = [
        (
            "16",
            "宇宙探査機の姿勢制御スラスター点火論理：太陽センサ姿勢捕捉フラグは捕捉中（True）、スタートラッカー星図照合フラグは未照合（False）。",
            "論理ルール：『両センサーとも正常（AND）』なら『高精度姿勢制御スラスター噴射』、『少なくとも一方が正常（OR）』なら『粗姿勢維持スラスター噴射』、両方喪失なら『セーフホールドスピンモード』。決定せよ。",
            "論理ルール：『両センサーとも喪失（NOR）』なら『セーフホールドスピンモード』、『片方のみ正常（XOR）』なら『粗姿勢維持スラスター噴射』、両方正常なら『高精度姿勢制御スラスター噴射』。決定せよ。",
            [("attitude_precision_fire", "高精度姿勢制御スラスター噴射"), ("attitude_coarse_fire", "粗姿勢維持スラスター噴射"), ("attitude_safe_spin", "セーフホールドスピンモード")],
            "attitude_coarse_fire", "attitude_coarse_fire"
        ),
        (
            "17",
            "核融合実験装置トカマク磁場コイル保護論理：超伝導クエンチ検知は非検知（False）、クライオ冷却系統過圧警報は非検知（False）。",
            "論理ルール：『クエンチまたは冷却過圧のいずれかが発生（OR）』なら『急速放電抵抗器投入』、『両方未発生（NOR）』なら『定格磁場励磁継続』、両方同時発生なら『緊急真空破壊弁開放』。判定せよ。",
            "論理ルール：『クエンチかつ冷却過圧の同時発生（AND）』なら『緊急真空破壊弁開放』、『片方のみ発生（XOR）』なら『急速放電抵抗器投入』、いずれも未発生なら『定格磁場励磁継続』。判定せよ。",
            [("quench_dump_resistor", "急速放電抵抗器投入"), ("quench_nominal_plasma", "定格磁場励磁継続"), ("quench_vacuum_vent", "緊急真空破壊弁開放")],
            "quench_nominal_plasma", "quench_nominal_plasma"
        ),
        (
            "18",
            "自動改札機のICカード決済判定：残高不足フラグは未検知（False＝残高十分）、定期券有効区間外フラグは未検知（False＝区間内）。",
            "論理ルール：『残高不足かつ区間外（AND）』なら『進入拒絶ゲート完全閉止』、『残高不足または区間外（OR）』なら『精算機誘導黄ランプ』、両方なしなら『通常進入開扉』。判定せよ。",
            "論理ルール：『残高不足も区間外も共に未検知（NOR）』なら『通常進入開扉』、『どちらか片方のみ検知（XOR）』なら『精算機誘導黄ランプ』、両方検知なら『進入拒絶ゲート完全閉止』。判定せよ。",
            [("gate_pass_open", "通常進入開扉"), ("gate_fare_adjust", "精算機誘導黄ランプ"), ("gate_block_close", "進入拒絶ゲート完全閉止")],
            "gate_pass_open", "gate_pass_open"
        ),
        (
            "19",
            "石油精製プラント水素化脱硫反応塔の圧力安全論理：安全弁入口手動弁開度確認は全開（True）、フレアスタック点火火炎は非点火（False）。",
            "論理ルール：『手動弁全開かつフレア点火（AND）』なら『過圧緊急ベント放出』、『手動弁全開だがフレア未点火（A AND NOT B）』なら『フレア自動再点火要求』、それ以外は『保安待機』。決定せよ。",
            "論理ルール：『手動弁未全開（NOT A）』なら『手動弁点検指示』、『手動弁全開かつフレア未点火（A AND NOT B）』なら『フレア自動再点火要求』、両方正常なら『過圧緊急ベント放出』。決定せよ。",
            [("desulf_vent_proceed", "過圧緊急ベント放出"), ("desulf_flare_ignite", "フレア自動再点火要求"), ("desulf_valve_check", "手動弁点検指示")],
            "desulf_flare_ignite", "desulf_flare_ignite"
        ),
        (
            "20",
            "スマートグリッド蓄電池充放電スケジューラ：電力市場価格スパイクフラグは発生中（True）、蓄電池充電率SoC高位フラグは未達（False＝残量中位）。",
            "論理ルール：『価格スパイクかつSoC高位（AND）』なら『系統へ最大出力放電売電』、『価格スパイクかつSoC非高位（A AND NOT B）』なら『自家消費優先部分放電』、スパイク未発生なら『充電待機』。指示せよ。",
            "論理ルール：『価格スパイク未発生（NOT A）』なら『充電待機』、『価格スパイクまたはSoC高位のどちらか片方のみ（XOR）』なら『自家消費優先部分放電』、両方成立なら『系統へ最大出力放電売電』。指示せよ。",
            [("bess_grid_discharge_max", "系統へ最大出力放電売電"), ("bess_self_consume_discharge", "自家消費優先部分放電"), ("bess_charge_standby", "充電待機")],
            "bess_self_consume_discharge", "bess_self_consume_discharge"
        ),
        (
            "21",
            "病院手術室の陰圧差圧制御インターロック：感染症隔離モードスイッチはON（True）、HEPAフィルター目詰まり差圧警報は発生中（True）。",
            "論理ルール：『隔離モードかつ目詰まり警報（AND）』なら『予備HEPAファン並列切替運転』、『隔離モードかつ目詰まり未発生（A AND NOT B）』なら『標準陰圧換気維持』、隔離モードOFFなら『通常正圧換気』。決定せよ。",
            "論理ルール：『隔離モードOFF（NOT A）』なら『通常正圧換気』、『隔離モードかつ目詰まり警報（AND）』なら『予備HEPAファン並列切替運転』、目詰まりなしなら『標準陰圧換気維持』。決定せよ。",
            [("or_dual_hepa_boost", "予備HEPAファン並列切替運転"), ("or_nominal_negative", "標準陰圧換気維持"), ("or_positive_switch", "通常正圧換気")],
            "or_dual_hepa_boost", "or_dual_hepa_boost"
        ),
        (
            "22",
            "鉄道踏切保安装置の自動障害検知：光電センサ踏切内物体検知は未検知（False）、ループコイル車両検知は未検知（False）。",
            "論理ルール：『光電センサまたはループコイルのいずれか検知（OR）』なら『列車非常停止信号発信』、『両方とも未検知（NOR）』なら『踏切遮断機正常降下維持』、センサ故障なら『徐行信号発信』。指示せよ。",
            "論理ルール：『両方未検知（NOR）』なら『踏切遮断機正常降下維持』、『片方のみ検知（XOR）』なら『現場カメラ即時確認起動』、両方検知なら『列車非常停止信号発信』。指示せよ。",
            [("crossing_halt_train", "列車非常停止信号発信"), ("crossing_lower_nominal", "踏切遮断機正常降下維持"), ("crossing_slow_signal", "徐行信号発信")],
            "crossing_lower_nominal", "crossing_lower_nominal"
        ),
        (
            "23",
            "無人自動運転トラクターの圃場エンドターン制御：境界ジオフェンス到達フラグは到達（True）、牽引プラウ油圧揚力完了フラグは未完了（False）。",
            "論理ルール：『境界到達かつ油圧揚力完了（AND）』なら『180度自動旋回シーケンス実行』、『境界到達だが油圧未完了（A AND NOT B）』なら『車速減速停止・揚力完了待機』、境界未達なら『直線耕耘走行維持』。指示せよ。",
            "論理ルール：『境界未達（NOT A）』なら『直線耕耘走行維持』、『境界到達かつ揚力未完了（A AND NOT B）』なら『車速減速停止・揚力完了待機』、両方完了なら『180度自動旋回シーケンス実行』。指示せよ。",
            [("tractor_turn_execute", "180度自動旋回シーケンス実行"), ("tractor_wait_plow_lift", "車速減速停止・揚力完了待機"), ("tractor_tillage_cruise", "直線耕耘走行維持")],
            "tractor_wait_plow_lift", "tractor_wait_plow_lift"
        ),
        (
            "24",
            "半導体製造クリーンルームの薬液バルブ制御：純水リンス終了タイマーは満了（True）、廃液排出口中和槽pH適正フラグは不適正（False）。",
            "論理ルール：『リンス満了かつpH適正（AND）』なら『メイン排液弁全開排出』、『リンス満了だがpH不適正（A AND NOT B）』なら『中和薬液槽バイパス循環』、リンス未了なら『リンス継続』。指示せよ。",
            "論理ルール：『リンス未了（NOT A）』なら『リンス継続』、『リンス満了かつpH不適正（A AND NOT B）』なら『中和薬液槽バイパス循環』、両方適正なら『メイン排液弁全開排出』。指示せよ。",
            [("drain_discharge_open", "メイン排液弁全開排出"), ("drain_bypass_neutralize", "中和薬液槽バイパス循環"), ("drain_rinse_continue", "リンス継続")],
            "drain_bypass_neutralize", "drain_bypass_neutralize"
        ),
        (
            "25",
            "火力発電所ボイラー給水ポンプの自動切替論理：常用Aポンプ吐出圧力低下フラグは発生（True）、予備Bポンプ待機健全フラグは健全（True）。",
            "論理ルール：『Aポンプ圧低下かつBポンプ健全（AND）』なら『予備Bポンプ自動起動切替』、『Aポンプ圧低下だがBポンプ不健全（A AND NOT B）』なら『ボイラー急速減負荷トリップ』、Aポンプ正常なら『常用運転継続』。判定せよ。",
            "論理ルール：『Aポンプ圧低下なし（NOT A）』なら『常用運転継続』、『Aポンプ圧低下かつBポンプ健全（AND）』なら『予備Bポンプ自動起動切替』、Bポンプも不健全なら『ボイラー急速減負荷トリップ』。判定せよ。",
            [("pump_auto_swap_b", "予備Bポンプ自動起動切替"), ("pump_boiler_derate_trip", "ボイラー急速減負荷トリップ"), ("pump_nominal_keep_a", "常用運転継続")],
            "pump_auto_swap_b", "pump_auto_swap_b"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k3_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_op_{gid}_s1",
                "group_id": f"rc3b_op_{gid}",
                "family": "logical_operators",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_op_{gid}_s2",
                "group_id": f"rc3b_op_{gid}",
                "family": "logical_operators",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2}
            }
        ])

    # --- K=4 (5 pairs: groups 26 to 30) ---
    k4_defs = [
        (
            "26",
            "高信頼性フォールトトレラントクラスタのノードフェイルオーバー論理：心拍信号途絶フラグは途絶検知（True）、ストレージ排他ロック保持フラグは喪失検知（True）。",
            "論理ルール：『心拍途絶かつロック喪失（AND）』なら『スタンバイ系即時テイクオーバー』、『心拍途絶だがロック保持中（A AND NOT B）』なら『スプリットブレイン防止フェンシング待機』、『心拍正常かつロック喪失（NOT A AND B）』なら『ストレージ再アタッチ要求』、両方正常なら『通常運用』。指示せよ。",
            "論理ルール：『心拍正常かつロック保持中（NOR）』なら『通常運用』、『心拍途絶かつロック喪失（AND）』なら『スタンバイ系即時テイクオーバー』、それ以外は『警告ログ記録』。指示せよ。",
            [("cluster_takeover_immediate", "スタンバイ系即時テイクオーバー"), ("cluster_fence_wait", "スプリットブレイン防止フェンシング待機"), ("cluster_storage_reattach", "ストレージ再アタッチ要求"), ("cluster_nominal_run", "通常運用")],
            "cluster_takeover_immediate", "cluster_takeover_immediate"
        ),
        (
            "27",
            "洋上風力発電変電プラットフォームのGIS（ガス絶縁開閉装置）ガス圧管理：SF6ガス圧低下警報は非検知（False）、ガス水分露点異常は非検知（False）。",
            "論理ルール：『ガス圧低下も露点異常も共に未検知（NOR）』なら『定格電力送電継続承認』、『ガス圧低下のみ検知（A AND NOT B）』なら『SF6ガス自動再補充』、『露点異常のみ検知（NOT A AND B）』なら『ガス循環乾燥脱水』、両方検知なら『主回路即時遮断』。決定せよ。",
            "論理ルール：『ガス圧低下または露点異常のいずれか一方のみ（XOR）』なら『メンテナンス予告発令』、『両方未検知（NOR）』なら『定格電力送電継続承認』、両方検知なら『主回路即時遮断』。決定せよ。",
            [("gis_transmission_pass", "定格電力送電継続承認"), ("gis_gas_replenish", "SF6ガス自動再補充"), ("gis_gas_dehydrate", "ガス循環乾燥脱水"), ("gis_circuit_trip", "主回路即時遮断")],
            "gis_transmission_pass", "gis_transmission_pass"
        ),
        (
            "28",
            "自律型海底探査機（AUV）の母船音響通信リンク：音響コマンド受信成功フラグは成功（True）、慣性航法INS推測位置誤差超過フラグは未超過（False）。",
            "論理ルール：『コマンド受信成功かつ位置誤差正常（A AND NOT B）』なら『自律潜航ミッション計画実行』、『コマンド途絶かつ位置誤差超過（NOT A AND B）』なら『緊急海面自動浮上』、『コマンド途絶だが位置誤差正常（NOT A AND NOT B）』なら『推測航法デッドレコニング続行』、コマンド受信だが誤差超過なら『音響測位再較正』。決定せよ。",
            "論理ルール：『位置誤差超過（B）』なら『緊急海面自動浮上』、『位置誤差正常かつコマンド受信成功（NOT B AND A）』なら『自律潜航ミッション計画実行』、それ以外は『母船誘導要求』。決定せよ。",
            [("auv_mission_proceed", "自律潜航ミッション計画実行"), ("auv_abort_surface", "緊急海面自動浮上"), ("auv_dead_reckon", "推測航法デッドレコニング続行"), ("auv_acoustic_recal", "音響測位再較正")],
            "auv_mission_proceed", "auv_mission_proceed"
        ),
        (
            "29",
            "製薬クリーン蒸気発生器の凝縮水純度モニタ：電気伝導率上限超過フラグは超過（True）、全有機炭素TOC上限超過フラグは未超過（False）。",
            "論理ルール：『伝導率超過かつTOC正常（A AND NOT B）』なら『蒸気トラップブロー弁強制開放』、『伝導率超過かつTOC超過（AND）』なら『クリーン蒸気ライン全遮断』、『伝導率正常だがTOC超過（NOT A AND B）』なら『UV分解セル出力増強』、両方正常なら『蒸気供給ライン開放継続』。決定せよ。",
            "論理ルール：『両方正常（NOR）』なら『蒸気供給ライン開放継続』、『伝導率超過かつTOC正常（A AND NOT B）』なら『蒸気トラップブロー弁強制開放』、それ以外なら『品質管理保留』。決定せよ。",
            [("steam_trap_blow", "蒸気トラップブロー弁強制開放"), ("steam_line_isolate", "クリーン蒸気ライン全遮断"), ("steam_uv_boost", "UV分解セル出力増強"), ("steam_supply_pass", "蒸気供給ライン開放継続")],
            "steam_trap_blow", "steam_trap_blow"
        ),
        (
            "30",
            "超伝導リニア浮上式鉄道の地上コイルき電制御：区間列車検知フラグは検知中（True）、インバータ同期周波数ロックフラグは未確立（False）。",
            "論理ルール：『列車検知かつ同期確立（AND）』なら『地上推進コイル大電力通電開始』、『列車検知だが同期未確立（A AND NOT B）』なら『周波数追従同期PLL整合待機』、『列車未検知かつ同期確立（NOT A AND B）』なら『無負荷励磁待機』、両方未成立なら『変電所系統遮断』。指示せよ。",
            "論理ルール：『列車未検知（NOT A）』なら『変電所系統遮断』、『列車検知かつ同期未確立（A AND NOT B）』なら『周波数追従同期PLL整合待機』、両方成立なら『地上推進コイル大電力通電開始』。指示せよ。",
            [("maglev_power_energize", "地上推進コイル大電力通電開始"), ("maglev_sync_wait", "周波数追従同期PLL整合待機"), ("maglev_idle_excitation", "無負荷励磁待機"), ("maglev_substation_trip", "変電所系統遮断")],
            "maglev_sync_wait", "maglev_sync_wait"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k4_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_op_{gid}_s1",
                "group_id": f"rc3b_op_{gid}",
                "family": "logical_operators",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_op_{gid}_s2",
                "group_id": f"rc3b_op_{gid}",
                "family": "logical_operators",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2}
            }
        ])

    return pairs
