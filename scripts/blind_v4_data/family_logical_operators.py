"""Family 2: logical_operators (30 pairs, 60 cases) - Blind v4
Distribution: K=2 (15 pairs), K=3 (10 pairs), K=4 (5 pairs)
Prefix: rc2b4_op_
Zero inference during authoring; 100% fresh scenarios.
"""

from typing import Any, Dict, List, Tuple


def make_choices(c_defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in c_defs]


def get_logical_operators_pairs() -> List[Dict[str, Any]]:
    pairs = []

    # --- K=2 (15 pairs: groups 01 to 15) ---
    k2_defs = [
        (
            "01",
            "設備状態判定：生体認証スキャンは合格（True）、IC身分証タッチは未完了（False）。",
            "論理規則：『生体認証スキャンとIC身分証の両方が成立（AND）』のとき『セキュリティゲートを開放する』、不成立なら『ゲートを閉止維持する』。判定せよ。",
            "論理規則：『生体認証スキャンまたはIC身分証のいずれか一方が成立（OR）』のとき『セキュリティゲートを開放する』、両方不成立なら『ゲートを閉止維持する』。判定せよ。",
            [("gate_open", "セキュリティゲートを開放する"), ("gate_close", "ゲートを閉止維持する")],
            "gate_close", "gate_open"
        ),
        (
            "02",
            "設備状態判定：第1系冷却ポンプは運転中（True）、第2系冷却ポンプは停止（False）。",
            "論理規則：『第1系と第2系の双方が同時に停止（NOR）』のときのみ『冷却全喪失警報を発令する』、少なくとも一方が運転中なら『通常運転を継続する』。判定せよ。",
            "論理規則：『第1系と第2系の双方が同時に運転（AND）』でなければ『冷却全喪失警報を発令する』、両方運転なら『通常運転を継続する』。判定せよ。",
            [("alarm_trip", "冷却全喪失警報を発令する"), ("normal_continue", "通常運転を継続する")],
            "normal_continue", "alarm_trip"
        ),
        (
            "03",
            "設備状態判定：主回路リレー接点Aは導通（True）、副回路リレー接点Bも導通（True）。",
            "論理規則：『接点Aと接点Bの導通状態が不一致（XOR：どちらか片方のみ導通）』のとき『回路不整合エラーを出力する』、一致なら『回路正常出力を維持する』。判定せよ。",
            "論理規則：『接点Aと接点Bの双方が導通（AND）』のとき『回路不整合エラーを出力する』、それ以外なら『回路正常出力を維持する』。判定せよ。",
            [("circuit_error", "回路不整合エラーを出力する"), ("circuit_normal", "回路正常出力を維持する")],
            "circuit_normal", "circuit_error"
        ),
        (
            "04",
            "設備状態判定：排気ガス濃度は基準内（False＝非検知）、ダクト内風速は基準内（False＝非検知）。",
            "論理規則：『ガス濃度超過または風速異常のいずれか一方でも発生（OR）』した場合は『排風機急速換気を起動する』、両方未発生なら『換気ファン通常維持とする』。判定せよ。",
            "論理規則：『ガス濃度超過も風速異常も共に発生していない（NOR：否定論理和）』場合は『排風機急速換気を起動する』、何らかの異常があれば『換気ファン通常維持とする』。判定せよ。",
            [("fan_boost", "排風機急速換気を起動する"), ("fan_normal", "換気ファン通常維持とする")],
            "fan_normal", "fan_boost"
        ),
        (
            "05",
            "設備状態判定：自動入札フラグは有効（True）、入札上限価格到達フラグは有効（True）。",
            "論理規則：『自動入札が有効かつ上限価格未到達（NOT B）』のときのみ『次期自動入札を実行する』、上限到達時は『入札シーケンスを停止する』。判定せよ。",
            "論理規則：『自動入札が無効（NOT A）または上限価格到達（B）』のとき『次期自動入札を実行する』、それ以外は『入札シーケンスを停止する』。判定せよ。",
            [("bid_execute", "次期自動入札を実行する"), ("bid_halt", "入札シーケンスを停止する")],
            "bid_halt", "bid_execute"
        ),
        (
            "06",
            "設備状態判定：非常用発電機エンジン起動接点はオン（True）、商用電源受電断路接点はオン（True）。",
            "論理規則：『エンジン起動接点と商用受電接点の両方が成立（AND）』のときはインターロック衝突のため『連系遮断器を開放遮断する』、それ以外は『遮断器を投入維持する』。判定せよ。",
            "論理規則：『エンジン起動接点と商用受電接点の双方が不成立（NOR）』のときのみ『連系遮断器を開放遮断する』、少なくとも一方が成立なら『遮断器を投入維持する』。判定せよ。",
            [("breaker_trip", "連系遮断器を開放遮断する"), ("breaker_closed", "遮断器を投入維持する")],
            "breaker_trip", "breaker_closed"
        ),
        (
            "07",
            "設備状態判定：倉庫内侵入赤外線センサは検知（True）、防犯カメラ動体検知は非検知（False）。",
            "論理規則：『赤外線センサまたは動体検知のいずれか一方でも検知（OR）』した場合は『防犯サイレンを鳴動する』、両方非検知なら『サイレン停止待機とする』。判定せよ。",
            "論理規則：『赤外線センサと動体検知の両方が揃って検知（AND）』したときのみ『防犯サイレンを鳴動する』、片方のみなら『サイレン停止待機とする』。判定せよ。",
            [("siren_sound", "防犯サイレンを鳴動する"), ("siren_standby", "サイレン停止待機とする")],
            "siren_sound", "siren_standby"
        ),
        (
            "08",
            "設備状態判定：油圧シリンダ前進端リミットスイッチはオン（True）、後退端リミットスイッチはオフ（False）。",
            "論理規則：『前進端スイッチまたは後退端スイッチのいずれか一方が成立（XOR）』なら『位置決め検出正常とする』、両方オフまたは両方オンなら『位置センサ異常警報とする』。判定せよ。",
            "論理規則：『前進端スイッチと後退端スイッチの両方が同時にオン（AND）』なら『位置決め検出正常とする』、不一致なら『位置センサ異常警報とする』。判定せよ。",
            [("pos_normal", "位置決め検出正常とする"), ("pos_fault", "位置センサ異常警報とする")],
            "pos_normal", "pos_fault"
        ),
        (
            "09",
            "設備状態判定：メインデータベース応答速度は正常（True）、リードレプリカ同期遅延はなし（True）。",
            "論理規則：『メインDB異常（NOT A）またはレプリカ同期遅延あり（NOT B）』のとき『キャッシュフォールバックを実行する』、両方正常なら『メインDB直接参照を継続する』。判定せよ。",
            "論理規則：『メインDB正常かつレプリカ同期健全（A AND B）』のとき『キャッシュフォールバックを実行する』、異常時は『メインDB直接参照を継続する』。判定せよ。",
            [("cache_fallback", "キャッシュフォールバックを実行する"), ("db_direct", "メインDB直接参照を継続する")],
            "db_direct", "cache_fallback"
        ),
        (
            "10",
            "設備状態判定：コンベア過負荷トルクリミッタ作動（False＝未作動）、非常停止ロープスイッチ引込（False＝未作動）。",
            "論理規則：『トルクリミッタまたは非常停止ロープのいずれか一方でも作動（OR）』した場合は『搬送ライン即時停止とする』、両方未作動なら『搬送ライン定速運転とする』。判定せよ。",
            "論理規則：『トルクリミッタと非常停止ロープの両方が作動（AND）』したときのみ『搬送ライン即時停止とする』、それ以外なら『搬送ライン定速運転とする』。判定せよ。",
            [("line_emergency_stop", "搬送ライン即時停止とする"), ("line_run_steady", "搬送ライン定速運転とする")],
            "line_run_steady", "line_run_steady"  # Wait! Notice this would be same target! We must fix!
        ),
        (
            "11",
            "設備状態判定：ユーザーアカウント凍結フラグは偽（False＝凍結なし）、パスワード誤り回数超過フラグは真（True＝超過あり）。",
            "論理規則：『アカウント凍結またはパスワード誤り超過のいずれか（OR）』なら『ログイン要求を拒否する』、両方なしなら『ログイン要求を認証処理する』。判定せよ。",
            "論理規則：『アカウント凍結かつパスワード誤り超過の両方が成立（AND）』のときのみ『ログイン要求を拒否する』、揃わないなら『ログイン要求を認証処理する』。判定せよ。",
            [("login_reject", "ログイン要求を拒否する"), ("login_process", "ログイン要求を認証処理する")],
            "login_reject", "login_process"
        ),
        (
            "12",
            "設備状態判定：外気温度35℃以上（True）、外気湿度80%以上（False＝現在湿度65%）。",
            "論理規則：『高温かつ高湿の両方が成立（AND）』のときは『熱中症厳重警戒モードへ移行する』、揃わないときは『一般換気モードを維持する』。判定せよ。",
            "論理規則：『高温または高湿のいずれか一方が成立（OR）』のときは『熱中症厳重警戒モードへ移行する』、両方不成立なら『一般換気モードを維持する』。判定せよ。",
            [("heatstroke_warning_mode", "熱中症厳重警戒モードへ移行する"), ("general_vent_mode", "一般換気モードを維持する")],
            "general_vent_mode", "heatstroke_warning_mode"
        ),
        (
            "13",
            "設備状態判定：給水タンク水位上限接点はオフ（False）、給水タンク水位下限接点はオン（True＝水枯渇手前）。",
            "論理規則：『水位上限接点または下限接点のいずれか一方のみ成立（XOR）』のときは『給水電磁弁を開放駆動する』、両方同一なら『給水電磁弁を閉止駆動する』。判定せよ。",
            "論理規則：『水位上限接点と下限接点の双方がオン（AND）』のときは『給水電磁弁を開放駆動する』、不揃いなら『給水電磁弁を閉止駆動する』。判定せよ。",
            [("solenoid_valve_open", "給水電磁弁を開放駆動する"), ("solenoid_valve_close", "給水電磁弁を閉止駆動する")],
            "solenoid_valve_open", "solenoid_valve_close"
        ),
        (
            "14",
            "設備状態判定：プロセス圧力基準超過（True）、プロセス温度基準超過（True）。",
            "論理規則：『圧力超過と温度超過の双方が成立（AND）』なら『安全逃がし弁を全開する』、片方のみなら『弁を閉止保持する』。判定せよ。",
            "論理規則：『圧力超過と温度超過が不一致（XOR：どちらか一方のみ超過）』なら『安全逃がし弁を全開する』、一致なら『弁を閉止保持する』。判定せよ。",
            [("relief_valve_open", "安全逃がし弁を全開する"), ("relief_valve_keep_close", "弁を閉止保持する")],
            "relief_valve_open", "relief_valve_keep_close"
        ),
        (
            "15",
            "設備状態判定：光センサ受光ビーム遮断（True）、レーザーエリアセンサ侵入検知（False）。",
            "論理規則：『ビーム遮断かつエリア侵入の両方が成立（AND）』のとき『ロボット動作をインターロック停止する』、片方なら『低速接近運転とする』。判定せよ。",
            "論理規則：『ビーム遮断またはエリア侵入のいずれか一方でも成立（OR）』したとき『ロボット動作をインターロック停止する』、両方未成立なら『低速接近運転とする』。判定せよ。",
            [("robot_interlock_halt", "ロボット動作をインターロック停止する"), ("robot_slow_creep", "低速接近運転とする")],
            "robot_slow_creep", "robot_interlock_halt"
        ),
    ]

    # Let's check group 10 in k2_defs above:
    # Context: Torque False, Rope False.
    # Q1: OR -> stop, else run. Since False OR False is False, result is run.
    # To make contrastive, Q2 should evaluate to stop!
    # Q2: NOR (neither active) -> stop, else run. False NOR False is True -> stop!
    k2_defs[9] = (
        "10",
        "設備状態判定：コンベア過負荷トルクリミッタ作動（False＝未作動）、非常停止ロープスイッチ引込（False＝未作動）。",
        "論理規則：『トルクリミッタまたは非常停止ロープのいずれか一方でも作動（OR）』した場合は『搬送ライン即時停止とする』、両方未作動なら『搬送ライン定速運転とする』。判定せよ。",
        "論理規則：『トルクリミッタも非常停止ロープも共に未作動（NOR：両方偽）』のとき『搬送ライン即時停止とする』、異常作動があれば『搬送ライン定速運転とする』。判定せよ。",
        [("line_emergency_stop", "搬送ライン即時停止とする"), ("line_run_steady", "搬送ライン定速運転とする")],
        "line_run_steady", "line_emergency_stop"
    )

    for gid, ctx, q1, q2, cdefs, t1, t2 in k2_defs:
        pairs.append({
            "id": f"rc2b4_op_{gid}_s1", "group_id": f"rc2b4_op_{gid}", "family": "logical_operators",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_op_{gid}_s2", "group_id": f"rc2b4_op_{gid}", "family": "logical_operators",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=3 (10 pairs: groups 16 to 25) ---
    k3_defs = [
        (
            "16",
            "監視項目：火災熱感知器作動（True）、排煙流動検知（False）。",
            "論理手順：①『熱感知器と排煙流動の両方が成立（AND）』なら『全館非常避難警報』。②『熱感知器のみ単独成立』なら『現地確認調査アラート』。それ以外は『監視維持』。判定せよ。",
            "論理手順：①『熱感知器または排煙流動のいずれか一方が成立（OR）』なら『全館非常避難警報』。②『両方不成立』なら『監視維持』。判定せよ。",
            [
                ("alarm_full_evacuate", "全館非常避難警報"),
                ("alarm_local_investigate", "現地確認調査アラート"),
                ("alarm_maintain_watch", "監視維持")
            ],
            "alarm_local_investigate", "alarm_full_evacuate"
        ),
        (
            "17",
            "監視項目：インバータ過電流信号（True）、過熱サーマル信号（True）。",
            "論理手順：①『過電流かつ過熱の両方が同時発生（AND）』なら『インバータ主回路即時遮断』。②『いずれか一方のみ（XOR）』なら『モータ減速トルク制限』。③未発生なら『定格運転』。判定せよ。",
            "論理手順：①『過電流と過熱が不一致（XOR：片方のみ）』なら『インバータ主回路即時遮断』。②『双方が同時発生（AND）』なら『モータ減速トルク制限』。③未発生なら『定格運転』。判定せよ。",
            [
                ("inverter_trip_cutoff", "インバータ主回路即時遮断"),
                ("motor_derate_limit", "モータ減速トルク制限"),
                ("inverter_rated_run", "定格運転")
            ],
            "inverter_trip_cutoff", "motor_derate_limit"
        ),
        (
            "18",
            "監視項目：上流ダンパー全開（True）、下流ファン吸気回転（False）。",
            "論理手順：①『ダンパー全開かつファン回転（AND）』なら『主風量送風指令』。②『ダンパー開だがファン停止（A AND NOT B）』なら『ファン起動待機指令』。③両方停止なら『送風停止指令』。判定せよ。",
            "論理手順：①『ダンパー全開またはファン回転（OR）』なら『主風量送風指令』。②『両方停止』なら『送風停止指令』。判定せよ。",
            [
                ("airflow_main_command", "主風量送風指令"),
                ("fan_start_standby", "ファン起動待機指令"),
                ("airflow_stop_command", "送風停止指令")
            ],
            "fan_start_standby", "airflow_main_command"
        ),
        (
            "19",
            "監視項目：冷却水入口流量低下（False＝正常流量）、出口水温高（False＝正常温度）。",
            "論理手順：①『流量低下または水温高のいずれか（OR）』なら『冷却水緊急バイパス弁開放』。②『流量低下もなく水温も正常（NOR）』なら『定常熱交換サイクル継続』。③異常センサ故障なら『手動弁操作』。判定せよ。",
            "論理手順：①『流量低下も水温高も未発生（NOR）』なら『冷却水緊急バイパス弁開放』。②『何らかの異常成立』なら『定常熱交換サイクル継続』。判定せよ。",
            [
                ("cooling_bypass_open", "冷却水緊急バイパス弁開放"),
                ("heat_exchange_steady", "定常熱交換サイクル継続"),
                ("manual_valve_override", "手動弁操作")
            ],
            "heat_exchange_steady", "cooling_bypass_open"
        ),
        (
            "20",
            "監視項目：主電源電圧正常（True）、副電源バッテリ満充電（False＝充電中）。",
            "論理手順：①『主電源正常かつ副電源満充電（AND）』なら『二重化完全給電承認』。②『主電源正常だが副電源未満充電（A AND NOT B）』なら『主系単独給電・バッテリ充電優先』。③主電源異常なら『副系非常放電』。判定せよ。",
            "論理手順：①『主電源または副電源のいずれか健全（OR）』なら『二重化完全給電承認』。②『主電源停止時』なら『副系非常放電』。判定せよ。",
            [
                ("dual_power_fully_approved", "二重化完全給電承認"),
                ("single_primary_battery_charge", "主系単独給電・バッテリ充電優先"),
                ("secondary_emergency_discharge", "副系非常放電")
            ],
            "single_primary_battery_charge", "dual_power_fully_approved"
        ),
        (
            "21",
            "監視項目：空調フィルタ目詰まり差圧高（True）、ファンモータ振動高（False）。",
            "論理手順：①『差圧高と振動高の両方成立（AND）』なら『空調ユニット緊急全停止』。②『差圧高のみ単独成立（A AND NOT B）』なら『フィルタ清掃予告通知』。③両方正常なら『通常空調運転』。判定せよ。",
            "論理手順：①『差圧高または振動高のいずれか成立（OR）』なら『空調ユニット緊急全停止』。②両方正常なら『通常空調運転』。判定せよ。",
            [
                ("hvac_emergency_shutdown", "空調ユニット緊急全停止"),
                ("filter_clean_notice", "フィルタ清掃予告通知"),
                ("hvac_run_normal", "通常空調運転")
            ],
            "filter_clean_notice", "hvac_emergency_shutdown"
        ),
        (
            "22",
            "監視項目：外部ファイアウォール通過（True）、内部WAF検閲通過（True）。",
            "論理手順：①『FW通過とWAF通過の両方が成立（AND）』なら『Webバックエンドパケット転送』。②『どちらか一方のみ通過（XOR）』なら『隔離サンドボックスへ迂回』。③両方拒否なら『パケット即時破棄』。判定せよ。",
            "論理手順：①『どちらか一方のみ通過（XOR）』なら『Webバックエンドパケット転送』。②『両方通過（AND）』なら『隔離サンドボックスへ迂回』。③両方拒否なら『パケット即時破棄』。判定せよ。",
            [
                ("packet_forward_backend", "Webバックエンドパケット転送"),
                ("packet_divert_sandbox", "隔離サンドボックスへ迂回"),
                ("packet_drop_immediate", "パケット即時破棄")
            ],
            "packet_forward_backend", "packet_divert_sandbox"
        ),
        (
            "23",
            "監視項目：ボイラー缶水pH基準外（False＝正常）、導電率基準外（True＝異常濃縮）。",
            "論理手順：①『pH基準外と導電率基準外の両方成立（AND）』なら『ボイラー緊急消火』。②『導電率基準外のみ成立（NOT A AND B）』なら『連続ブロー弁自動開度増量』。③両方正常なら『通常缶水ブロー』。判定せよ。",
            "論理手順：①『pH基準外または導電率基準外のいずれか成立（OR）』なら『ボイラー緊急消火』。②両方正常なら『通常缶水ブロー』。判定せよ。",
            [
                ("boiler_emergency_extinguish", "ボイラー緊急消火"),
                ("continuous_blowdown_boost", "連続ブロー弁自動開度増量"),
                ("boiler_blowdown_normal", "通常缶水ブロー")
            ],
            "continuous_blowdown_boost", "boiler_emergency_extinguish"
        ),
        (
            "24",
            "監視項目：クレーン旋回制限リミット（True＝制限到達）、荷吊り過荷重検知（False＝定格内）。",
            "論理手順：①『旋回制限かつ過荷重の両方成立（AND）』なら『主電源非常遮断』。②『旋回制限到達だが荷重適正（A AND NOT B）』なら『旋回のみインターロック停止』。③両方未検出なら『全軸運転許可』。判定せよ。",
            "論理手順：①『旋回制限または過荷重のいずれか成立（OR）』なら『主電源非常遮断』。②両方未検出なら『全軸運転許可』。判定せよ。",
            [
                ("crane_main_power_cut", "主電源非常遮断"),
                ("crane_slew_lock_only", "旋回のみインターロック停止"),
                ("crane_all_axes_permitted", "全軸運転許可")
            ],
            "crane_slew_lock_only", "crane_main_power_cut"
        ),
        (
            "25",
            "監視項目：蒸留塔頂部圧力高（False）、底部液面低（False）。",
            "論理手順：①『圧力高または液面低のいずれか成立（OR）』なら『原料フィード自動減量』。②『圧力も液面も共に正常（NOR）』なら『定常精留運転継続』。③塔底過熱なら『リボイラ蒸気弁遮断』。判定せよ。",
            "論理手順：①『圧力も液面も共に正常（NOR）』なら『原料フィード自動減量』。②『いずれか異常成立』なら『定常精留運転継続』。判定せよ。",
            [
                ("feed_rate_reduce", "原料フィード自動減量"),
                ("distillation_steady_continue", "定常精留運転継続"),
                ("reboiler_steam_shutoff", "リボイラ蒸気弁遮断")
            ],
            "distillation_steady_continue", "feed_rate_reduce"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k3_defs:
        pairs.append({
            "id": f"rc2b4_op_{gid}_s1", "group_id": f"rc2b4_op_{gid}", "family": "logical_operators",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_op_{gid}_s2", "group_id": f"rc2b4_op_{gid}", "family": "logical_operators",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=4 (5 pairs: groups 26 to 30) ---
    k4_defs = [
        (
            "26",
            "条件信号：受電系統周波数低下（True）、母線電圧低下（False）。",
            "制御規則：①『周波数低下かつ電圧低下の両方（AND）』なら『全負荷一括非常遮断』。②『周波数低下のみ単独（A AND NOT B）』なら『第1段選択負荷制限遮断』。③『電圧低下のみ単独』なら『無効電力補償器投入』。④正常なら『全系給電維持』。決定せよ。",
            "制御規則：①『周波数低下または電圧低下のいずれか（OR）』なら『全負荷一括非常遮断』。②『両方正常』なら『全系給電維持』。③『異常センサ無効時』なら『手動指令待機』。決定せよ。",
            [
                ("load_shedding_total", "全負荷一括非常遮断"),
                ("load_shedding_stage1", "第1段選択負荷制限遮断"),
                ("reactive_power_boost", "無効電力補償器投入"),
                ("power_feed_steady", "全系給電維持")
            ],
            "load_shedding_stage1", "load_shedding_total"
        ),
        (
            "27",
            "条件信号：無人搬送車LiDAR障害物検知（True）、超音波近接検知（True）。",
            "制御規則：①『LiDARと超音波の両方が同時に検知（AND）』なら『即時強制非常停止』。②『どちらか一方のみ検知（XOR）』なら『徐行徐動減速モード』。③『前方空間完全クリア』なら『最高巡航速度走行』。決定せよ。",
            "制御規則：①『LiDARと超音波が不一致（XOR：どちらか一方のみ）』なら『即時強制非常停止』。②『両方が同時に検知（AND）』なら『徐行徐動減速モード』。決定せよ。",
            [
                ("agv_halt_hard_stop", "即時強制非常停止"),
                ("agv_slow_creep_mode", "徐行徐動減速モード"),
                ("agv_max_cruise_speed", "最高巡航速度走行"),
                ("agv_rotate_turnaround", "その場超信地旋回")
            ],
            "agv_halt_hard_stop", "agv_slow_creep_mode"
        ),
        (
            "28",
            "条件信号：エンジン潤滑油油圧低（False）、冷却水水温高（True）。",
            "制御規則：①『油圧低かつ水温高の両方（AND）』なら『エンジン緊急自動停止』。②『油圧正常だが水温高（NOT A AND B）』なら『ラジエーター電動ファン強制全開』。③『油圧低だが水温正常』なら『潤滑油補助ポンプ起動』。決定せよ。",
            "制御規則：①『油圧低または水温高のいずれか一方でも成立（OR）』なら『エンジン緊急自動停止』。②『両方正常』なら『定格回転維持』。決定せよ。",
            [
                ("engine_emergency_trip", "エンジン緊急自動停止"),
                ("radiator_fan_full_blast", "ラジエーター電動ファン強制全開"),
                ("lube_aux_pump_start", "潤滑油補助ポンプ起動"),
                ("engine_rated_rpm_hold", "定格回転維持")
            ],
            "radiator_fan_full_blast", "engine_emergency_trip"
        ),
        (
            "29",
            "条件信号：原子炉制御棒全挿入リミット（False＝未挿入）、手動スクラムボタン押下（True）。",
            "制御規則：①『手動ボタン押下かつ全挿入未達（B AND NOT A）』なら『緊急水圧スクラム作動弁励磁』。②『全挿入完了』なら『スクラム完了表示』。③『ボタン未押下かつ未挿入』なら『制御棒自動位置制御』。決定せよ。",
            "制御規則：①『全挿入完了または手動未押下』なら『スクラム完了表示』。②『手動ボタン押下かつ未挿入』なら『緊急水圧スクラム作動弁励磁』。決定せよ。",  # Wait, contrastive!
            [
                ("scram_hydraulic_actuate", "緊急水圧スクラム作動弁励磁"),
                ("scram_complete_indicate", "スクラム完了表示"),
                ("rod_auto_position_control", "制御棒自動位置制御"),
                ("boron_injection_backup", "予備ほう酸水注入作動")
            ],
            "scram_hydraulic_actuate", "scram_hydraulic_actuate"  # Wait! Target 1 == Target 2! We must fix Q2!
        ),
        (
            "30",
            "条件信号：外気導入ダンパー開放（True）、循環還気ダンパー開放（True）。",
            "制御規則：①『外気ダンパーと還気ダンパーの両方が開放（AND）』なら『混合全風量換気運転』。②『どちらか一方のみ開放（XOR）』なら『単一吸気制限運転』。③両方閉鎖なら『空調ファン停止維持』。決定せよ。",
            "制御規則：①『外気ダンパーと還気ダンパーが不一致（XOR：片方のみ）』なら『混合全風量換気運転』。②『両方が開放（AND）』なら『単一吸気制限運転』。決定せよ。",
            [
                ("hvac_mixed_full_air", "混合全風量換気運転"),
                ("hvac_single_intake_restrict", "単一吸気制限運転"),
                ("hvac_fan_stay_stopped", "空調ファン停止維持"),
                ("hvac_dehumidifier_active", "全熱交換器バイパス切替")
            ],
            "hvac_mixed_full_air", "hvac_single_intake_restrict"
        ),
    ]

    # Let's fix group 29 in k4_defs to ensure crisp, clean contrast:
    k4_defs[3] = (
        "29",
        "条件信号：原子炉制御棒全挿入リミット（False＝未挿入）、手動スクラムボタン押下（True）。",
        "制御規則：①『手動ボタン押下かつ全挿入未達（B AND NOT A）』なら『緊急水圧スクラム作動弁励磁』。②『全挿入完了』なら『スクラム完了表示』。③『ボタン未押下』なら『制御棒自動位置制御』。決定せよ。",
        "制御規則：①『手動ボタン押下と全挿入完了の両方が成立（AND）』なら『緊急水圧スクラム作動弁励磁』。②『未完了（全挿入未達）』なら『ほう酸水注入バックアップ準備』。決定せよ。",
        [
            ("scram_hydraulic_actuate", "緊急水圧スクラム作動弁励磁"),
            ("boron_injection_backup", "ほう酸水注入バックアップ準備"),
            ("scram_complete_indicate", "スクラム完了表示"),
            ("rod_auto_position_control", "制御棒自動位置制御")
        ],
        "scram_hydraulic_actuate", "boron_injection_backup"
    )

    for gid, ctx, q1, q2, cdefs, t1, t2 in k4_defs:
        pairs.append({
            "id": f"rc2b4_op_{gid}_s1", "group_id": f"rc2b4_op_{gid}", "family": "logical_operators",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_op_{gid}_s2", "group_id": f"rc2b4_op_{gid}", "family": "logical_operators",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    return pairs
