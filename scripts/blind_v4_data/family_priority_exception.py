"""Family 3: priority_exception (30 pairs, 60 cases) - Blind v4
Distribution: K=3 (5 pairs), K=4 (15 pairs), K=6 (5 pairs), K=8 (5 pairs)
Prefix: rc2b4_prio_
Zero inference during authoring; 100% fresh scenarios.
"""

from typing import Any, Dict, List, Tuple


def make_choices(c_defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in c_defs]


def get_priority_exception_pairs() -> List[Dict[str, Any]]:
    pairs = []

    # --- K=3 (5 pairs: groups 01 to 05) ---
    k3_defs = [
        (
            "01",
            "港湾自動荷役クレーンの運用基準：『通常規則：コンテナ自動荷役サイクルを定常実行する。ただし【最優先例外】：気象台から暴風特別警報が発令された場合は、荷役を全面中断しアームを格納固定する』。",
            "現地状況：湾岸地域に暴風特別警報が発令され、風速計警報が連続点灯した。クレーン指示を決定せよ。",
            "現地状況：天候は穏やかな晴天であり、特別警報・気象注意報は一切発令されていない。クレーン指示を決定せよ。",
            [
                ("crane_lockdown_storm", "荷役全面中断・ブーム格納締結固定"),
                ("crane_execute_routine", "コンテナ自動荷役定常実行"),
                ("crane_standby_idle", "アイドリング待機")
            ],
            "crane_lockdown_storm", "crane_execute_routine"
        ),
        (
            "02",
            "病院ICU輸液ポンプ投与基準：『通常規則：術後プロトコルに従い規定速度（20mL/h）で定時持続輸液を行う。ただし【最優先例外】：平均動脈圧（MAP）が55mmHg未満へ急落した場合は、輸液を一時中止し緊急昇圧剤ラインへ即時切り替える』。",
            "バイタルサイン：平均動脈圧が48mmHgに急低下した。輸液ポンプ制御を決定せよ。",
            "バイタルサイン：平均動脈圧は78mmHgで安定推移している。輸液ポンプ制御を決定せよ。",
            [
                ("switch_vasopressor_emergency", "持続輸液中止・緊急昇圧剤ライン即時切替"),
                ("continue_routine_infusion", "プロトコル定時持続輸液継続"),
                ("flush_catheter_saline", "カテーテル生食フラッシュ")
            ],
            "switch_vasopressor_emergency", "continue_routine_infusion"
        ),
        (
            "03",
            "金融機関セキュアゲートウェイ通信規程：『通常規則：全外部IPアドレスからの接続パケットは不正侵入防止のため遮断する。ただし【特権例外】：社内VPN二重要素認証を通過した特権保守端末IDからの通信は無条件で許可する』。",
            "パケット属性：接続元は社内VPN二重要素認証を完全に通過した特権保守端末である。接続判定を行え。",
            "パケット属性：接続元は海外ホスティングプロバイダの未認証一般外部IPである。接続判定を行え。",
            [
                ("gateway_allow_privilege", "特権保守セッション接続許可"),
                ("gateway_block_drop", "不正アクセス防止・パケット破棄遮断"),
                ("gateway_throttle_bandwidth", "通信帯域制限待機")
            ],
            "gateway_allow_privilege", "gateway_block_drop"
        ),
        (
            "04",
            "自律飛行型監視ドローンの航路制御：『通常規則：目的地への最短直線ウェイポイントを追従飛行する。ただし【最優先例外】：上空制限区域（ジオフェンス）境界から50m以内に進入した場合は、最短直進を放棄し安全迂回航路へ旋回する』。",
            "航法テレメトリ：ジオフェンス境界まで直進距離32mまで接近した。航路指示を決定せよ。",
            "航法テレメトリ：直近の制限区域境界まで3.5km離れており、飛行空域は全方位クリアである。航路指示を決定せよ。",
            [
                ("drone_divert_perimeter", "直線直進放棄・外周迂回航路旋回"),
                ("drone_fly_straight_direct", "目的地最短直線ウェイポイント直進"),
                ("drone_auto_parachute", "非常用パラシュート開傘降下")
            ],
            "drone_divert_perimeter", "drone_fly_straight_direct"
        ),
        (
            "05",
            "製鉄所熱間圧延ラインの剪断判定：『通常規則：高品位鋼板の連続圧延シーケンスを完遂させる。ただし【品質例外】：光学表面探傷カメラが深部クラックを検出した場合は、後続スタンドへの噛み込みを防ぐためフライングシアーで直ちにリジェクト剪断する』。",
            "探傷ロジック出力：表面カメラが深さ2.5mmの縦クラック欠陥を連続検知した。処置を指示せよ。",
            "探傷ロジック出力：表面欠陥スコア0、平滑性判定Aランク合格である。処置を指示せよ。",
            [
                ("shear_scrap_defect", "フライングシアー直ちリジェクト剪断"),
                ("continue_hot_rolling", "連続熱間圧延パス完遂"),
                ("cooling_water_soak", "水冷ピット浸漬待機")
            ],
            "shear_scrap_defect", "continue_hot_rolling"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k3_defs:
        pairs.append({
            "id": f"rc2b4_prio_{gid}_s1", "group_id": f"rc2b4_prio_{gid}", "family": "priority_exception",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_prio_{gid}_s2", "group_id": f"rc2b4_prio_{gid}", "family": "priority_exception",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=4 (15 pairs: groups 06 to 20) ---
    k4_defs = [
        (
            "06",
            "空港進入管制（APP）規則：『通常規則：着陸進入中の航空機に対し滑走路着陸許可（Cleared to Land）を発出する。ただし【最優先例外】：先行機によるバードストライクまたは滑走路異物残存報告があった場合は、着陸許可を取り消し即時進入復行（ゴーアラウンド）を指示する』。",
            "滑走路モニタ：直前の着陸機より滑走路上に鳥の群れと衝突痕跡の緊急無線報告が入った。進入指示を決定せよ。",
            "滑走路モニタ：滑走路全面検査完了、先行機離脱済みで滑走路クリアが確認されている。進入指示を決定せよ。",
            [
                ("atc_order_go_around", "着陸許可取消・即時進入復行ゴーアラウンド指示"),
                ("atc_clear_to_land", "滑走路着陸許可発出"),
                ("atc_hold_overhead", "空港上空旋回待機指示"),
                ("atc_divert_alternate", "代替空港ダイバート指示")
            ],
            "atc_order_go_around", "atc_clear_to_land"
        ),
        (
            "07",
            "証券取引所マッチングエンジン約定基準：『通常規則：注文帳の価格優先・時間優先原則に従い発注注文を即時約定マッチングする。ただし【規制例外】：個別銘柄の株価急変によりサーキットブレーカー（特別気配停止）が発動された場合は、マッチングを一時停止し売買注文を保留待機とする』。",
            "取引所シグナル：対象銘柄に特別気配制限値幅到達によるサーキットブレーカー発動通知が届いた。注文処理を決定せよ。",
            "取引所シグナル：対象銘柄は気配制限範囲内で正常に価格更新されており、制限措置は未発動である。注文処理を決定せよ。",
            [
                ("halt_order_matching", "マッチング一時停止・注文保留待機"),
                ("execute_instant_match", "価格・時間優先による即時約定実行"),
                ("cancel_all_open_orders", "未約定注文全件強制失効"),
                ("split_iceberg_order", "アイスバーグ分割注文展開")
            ],
            "halt_order_matching", "execute_instant_match"
        ),
        (
            "08",
            "抗体バイオリアクター培養槽管理規定：『通常規則：培地栄養液を規定循環速度で定量送液する。ただし【汚染例外】：オンライン迅速PCRセンサが外来ウイルス・コンタミネーション疑い陽性を検知した場合は、送液を即時遮断し槽内高圧蒸気不活性化滅菌シーケンスへ移行する』。",
            "生化学センシング：培養槽出口液から外来マイコプラズマDNA陽性反応が検出された。制御指示を決定せよ。",
            "生化学センシング：全生菌・外来遺伝子検査は陰性（未検出）、細胞生存率98%を維持している。制御指示を決定せよ。",
            [
                ("containment_steam_inactivate", "送液即時遮断・高圧蒸気不活性化滅菌"),
                ("steady_nutrient_perfusion", "培地栄養液定常定量送液継続"),
                ("temperature_shift_hypothermia", "低温誘導培養シフト"),
                ("harvest_filter_membrane", "中空糸膜回収濃縮")
            ],
            "containment_steam_inactivate", "steady_nutrient_perfusion"
        ),
        (
            "09",
            "新幹線自動列車制御装置（ATC）の速度照査：『通常規則：車内信号の指示速度（270km/h）まで加速・力行運転を許容する。ただし【保全例外】：沿線地震計または落石検知ワイヤ断線を受信した場合は、信号速度に関わらず非常ブレーキを最大出力で自動印加する』。",
            "保安装置入力：沿線落石検知ネットのワイヤ断線接点作動を受信した。列車制御を決定せよ。",
            "保安装置入力：沿線警報は全線正常、軌道回路も連続導通で障害なし。列車制御を決定せよ。",
            [
                ("atc_emergency_brake_full", "指示速度無効化・非常ブレーキ最大自動印加"),
                ("atc_allow_speed_acceleration", "車内信号指示速度までの力行加速許容"),
                ("atc_coasting_regenerative", "惰行回生ブレーキ減速"),
                ("atc_pantograph_lower_all", "パンタグラフ強制降下")
            ],
            "atc_emergency_brake_full", "atc_allow_speed_acceleration"
        ),
        (
            "10",
            "クラウドデータセンター特高受電盤の無瞬断給電規定：『通常規則：電力会社からの商用受電本線より各サーバルームへ常用受電する。ただし【系統例外】：商用受電電圧が瞬時電圧低下（定格の70%未満）した場合は、無瞬断高速スイッチで瞬時にUPS蓄電池給電系へ切り替える』。",
            "受電計測器：送電線落雷事故により本線受電電圧が定格の30%まで瞬低した。給電切替を判定せよ。",
            "受電計測器：受電電圧・周波数ともに規定値中央を安定維持している。給電切替を判定せよ。",
            [
                ("transfer_ups_battery_instant", "無瞬断高速スイッチによるUPS蓄電池給電切替"),
                ("maintain_commercial_grid", "商用電力本線常用受電継続"),
                ("shed_non_essential_chillers", "非重要補機負荷手動遮断"),
                ("start_diesel_generator_sync", "非常用ディーゼル発電機並列投入")
            ],
            "transfer_ups_battery_instant", "maintain_commercial_grid"
        ),
        (
            "11",
            "真空薄膜スパッタ装置のクライオポンプ再生手順：『通常規則：極低温凝縮面により高真空排気運転を維持する。ただし【飽和例外】：凝縮面温度が20Kを超過し吸着ガス飽和警報が成立した場合は、真空仕切りバルブを全閉しヒーター加熱ガスパージ再生を開始する』。",
            "熱電対温度計：クライオポンプヘッド温度が24.5Kへ上昇し飽和警報が出力された。ポンプ制御を決定せよ。",
            "熱電対温度計：ヘッド温度は11.2Kの極低温で安定維持されている。ポンプ制御を決定せよ。",
            [
                ("cryo_isolate_regeneration", "仕切り弁全閉・ヒーター加熱ガスパージ再生"),
                ("cryo_maintain_high_vacuum", "極低温凝縮面による高真空排気維持"),
                ("turbo_molecular_pump_boost", "ターボ分子ポンプ直列排気"),
                ("roughing_valve_vent_air", "荒引き弁大気解放")
            ],
            "cryo_isolate_regeneration", "cryo_maintain_high_vacuum"
        ),
        (
            "12",
            "自律型無人深海探査機（AUV）の安全浮上ロジック：『通常規則：事前プログラムされた深海マッピング測線軌道を音響測位で自動潜航する。ただし【通信断例外】：母船からのアコースティック通信パケット途絶が30分以上継続した場合は、任務を破棄し投棄型電磁バラストを切り離して強制緊急浮上する』。",
            "音響モデム状態：母船との定期通信ハンドシェイクが38分間途絶している。探査機シーケンスを決定せよ。",
            "音響モデム状態：母船との双方向通信遅延は2秒、正常な制御キープアライブを常時受信中である。探査機シーケンスを決定せよ。",
            [
                ("auv_drop_ballast_surface", "任務破棄・電磁バラスト切り離し緊急自律浮上"),
                ("auv_continue_survey_grid", "事前プログラム測線軌道の自動潜航継続"),
                ("auv_thruster_reverse_spin", "推進器逆転水深保持"),
                ("auv_light_strobe_flash_only", "LED探照灯点滅のみ実行")
            ],
            "auv_drop_ballast_surface", "auv_continue_survey_grid"
        ),
        (
            "13",
            "超高層複合施設のエレベーター運行管理：『通常規則：各階ホール呼び出しに対し待ち時間を最小化するAI群管理割当を行う。ただし【消防VIP例外】：1階専用キースイッチにより消防活動モードが投入された場合は、群管理割当を全面解除し全かごを1階ロビーへ直行降下させる』。",
            "防災盤インターフェース：消防隊操作盤の直行呼び戻しキースイッチがONに回された。エレベーター制御を指示せよ。",
            "防災盤インターフェース：キースイッチはOFF（通常位置）であり、各階から呼び出しが入力中である。エレベーター制御を指示せよ。",
            [
                ("recall_all_cars_lobby", "群管理解除・全エレベーター1階ロビー直行降下"),
                ("ai_dispatch_minimum_wait", "AI群管理による最適かご自動配車継続"),
                ("park_cars_mid_height", "中間階待機ポジション自動分散"),
                ("slow_speed_energy_saving", "省エネルギー深夜低速運転")
            ],
            "recall_all_cars_lobby", "ai_dispatch_minimum_wait"
        ),
        (
            "14",
            "産業用協働ロボットの安全防護規格：『通常規則：ワーク搬送のため最高設計速度（2,000mm/s）でマニピュレータを高速軌道動作させる。ただし【協働例外】：光線式安全柵内へ作業員の接近を検知した場合は、安全協働モードへ移行し動作速度を250mm/s以下に制限する』。",
            "安全レーザースキャナ：防護ゾーン内に作業員の上半身進入を検知した。ロボット速度を決定せよ。",
            "安全レーザースキャナ：防護ゾーン全域に遮光物なし、作業員接近ゼロが確認されている。ロボット速度を決定せよ。",
            [
                ("limit_speed_collaborative", "安全協働モード切替・速度250mm/s以下制限"),
                ("run_full_speed_transfer", "最高設計速度による高速マテリアルハンドリング"),
                ("robot_power_cut_off", "制御盤主ブレーカー手動遮断"),
                ("gripper_forced_release", "エンドエフェクタ把持物即時解放")
            ],
            "limit_speed_collaborative", "run_full_speed_transfer"
        ),
        (
            "15",
            "水素燃料電池車（FCV）充填ディスペンサー基準：『通常規則：車載容器へ目標圧力70MPaまで昇圧しながら水素を自動急速充填する。ただし【危険例外】：赤外線炎感知器または水素濃度センサが漏洩火災を検知した場合は、充填弁を緊急遮断し配管内水素を不活性窒素で掃気する』。",
            "防災受信用基板：ノズル充填口付近の赤外線検知器が炎特有の波長スパイクを検知した。ディスペンサー動作を決定せよ。",
            "防災受信用基板：漏洩濃度0.0%、炎検知なし、配管耐圧・気密テスト完了。ディスペンサー動作を決定せよ。",
            [
                ("emergency_shutoff_nitrogen_purge", "充填緊急遮断・配管内窒素パージ掃気"),
                ("resume_70mpa_fast_dispense", "70MPa目標自動急速充填シーケンス実行"),
                ("pre_cool_hydrogen_minus40", "充填水素マイナス40℃予冷強化"),
                ("recalibrate_coriolis_meter", "コリオリ質量流量計ゼロ点校正")
            ],
            "emergency_shutoff_nitrogen_purge", "resume_70mpa_fast_dispense"
        ),
        (
            "16",
            "スマートコミュニティ蓄電所の需給調整ルール：『通常規則：深夜余剰電力帯に蓄電池群を充電し、朝夕のピーク需要時に放電供給する。ただし【逆潮例外】：晴天昼間に太陽光発電が急増し配電線過電圧逆潮流が発生した場合は、計画スケジュールを中断し全容量で急速充電吸い上げを行う』。",
            "系統監視テレメトリ：太陽光急増によりフィーダー電圧が制限上限に達し逆潮流警報が出された。蓄電所運転を指示せよ。",
            "系統監視テレメトリ：夕方需要ピーク帯にあり、太陽光出力はゼロ、系統周波数は低下傾向である。蓄電所運転を指示せよ。",
            [
                ("absorb_excess_solar_charge", "スケジュール中断・過剰太陽光の急速充電吸い上げ"),
                ("discharge_grid_peak_support", "ピーク需要対応の計画放電供給実行"),
                ("island_microgrid_disconnect", "系統連系解列独立運転"),
                ("battery_cell_balancing_mode", "セルバランシング均等化充電")
            ],
            "absorb_excess_solar_charge", "discharge_grid_peak_support"
        ),
        (
            "17",
            "遠隔外科手術支援システムの安全インターロック：『通常規則：執刀医コンソールのマスタ手先座標をスレーブ手術鉗子へリアルタイム追従伝送する。ただし【通信遅延例外】：専用回線の往復伝送遅延（RTT）が50msを超過した場合は、誤切開を防ぐため鉗子アームを直ちに自動フリーズ保持する』。",
            "ネットワークQoSプローブ：回線混雑によりRTTが82msへ悪化した。手術ロボットアーム制御を決定せよ。",
            "ネットワークQoSプローブ：RTTは12msでジッター極小、超低遅延を安定確保している。手術ロボットアーム制御を決定せよ。",
            [
                ("freeze_surgical_arms_instantly", "追従中断・鉗子アーム直ちに自動フリーズ保持"),
                ("track_master_motion_realtime", "マスタ手先座標のリアルタイム高精度追従"),
                ("invert_roll_pitch_axes", "手首回転軸座標反転"),
                ("increase_haptic_force_gain", "触覚フォースフィードバック倍率増幅")
            ],
            "freeze_surgical_arms_instantly", "track_master_motion_realtime"
        ),
        (
            "18",
            "都市ガス地域導管ガバナ（整圧器）保全規則：『通常規則：中圧ガスを一般家庭用低圧ガスへ減圧調圧して安定供給する。ただし【地震例外】：設置地震計の計測SI値が60kine（震度6弱相当以上）を記録した場合は、二次災害防止のため緊急遮断弁（閉止弁）を自動トリップ遮断する』。",
            "地震計テレメトリ：直下型地震波により計測SI値68.5kineを検知した。ガバナステーション制御を指示せよ。",
            "地震計テレメトリ：計測SI値0.0kine（無震動）、管内圧力変動なし。ガバナステーション制御を指示せよ。",
            [
                ("trip_emergency_shutoff_valve", "二次災害防止・緊急遮断弁自動トリップ遮断"),
                ("maintain_district_pressure_control", "中圧から低圧への安定整圧調圧供給継続"),
                ("vent_gas_to_atmosphere", "都市ガス大気緊急放散"),
                ("inject_odorant_double", "付臭剤注入量手動倍増")
            ],
            "trip_emergency_shutoff_valve", "maintain_district_pressure_control"
        ),
        (
            "19",
            "クレジットカード海外不正防止セキュリティ：『通常規則：海外加盟店からのオンライン・対面カード決済要求は不正防止のため自動拒否（ディクライン）する。ただし【事前渡航届例外】：会員マイページにて該当渡航期間および滞在国の事前利用申請が登録済みである場合は、正常承認する』。",
            "取引ログ：フランスでの決済要求に対し、会員情報には今週有効なフランス渡航申請が事前登録されている。承認判定を行え。",
            "取引ログ：東南アジアでの対面決済要求に対し、会員の渡航届申請履歴は存在しない（未申請）。承認判定を行え。",
            [
                ("approve_transaction_registered", "事前登録合致・海外利用正常承認"),
                ("decline_transaction_unregistered", "不正防止ポリシー・海外決済自動拒絶"),
                ("lock_cardholder_account_permanently", "会員カード完全凍結失効"),
                ("require_wire_transfer_deposit", "銀行振込前受金請求")
            ],
            "approve_transaction_registered", "decline_transaction_unregistered"
        ),
        (
            "20",
            "スマート施設園芸ハウスの環境制御規定：『通常規則：日射センサー値に連動して光合成促進のため炭酸ガス（CO2）をハウス内に施用供給する。ただし【換気窓例外】：温湿度調整のため天窓または側窓の開放率が20%以上の場合は、ガスの外部散逸を防ぐためCO2発生器を停止する』。",
            "ハウス環境センサ：日射量は十分高いが、高温換気のため側窓が50%開放中である。CO2施用制御を決定せよ。",
            "ハウス環境センサ：日射量は十分高く、全換気窓は全閉（密閉状態）である。CO2施用制御を決定せよ。",
            [
                ("stop_co2_generator_venting", "散逸防止・換気窓開放のためCO2発生器停止"),
                ("inject_co2_enrichment", "光合成促進・日射連動CO2供給実行"),
                ("fogging_nozzle_full_spray", "細霧冷房ノズル高圧噴霧"),
                ("curtain_blackout_draw", "遮光カーテン全面展張")
            ],
            "stop_co2_generator_venting", "inject_co2_enrichment"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k4_defs:
        pairs.append({
            "id": f"rc2b4_prio_{gid}_s1", "group_id": f"rc2b4_prio_{gid}", "family": "priority_exception",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_prio_{gid}_s2", "group_id": f"rc2b4_prio_{gid}", "family": "priority_exception",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=6 (5 pairs: groups 21 to 25) ---
    k6_defs = [
        (
            "21",
            "自動立体倉庫スタッカークレーンの入出庫ルール：『通常規則：入庫指示されたパレットを棚奥へ自動格納する。ただし【積載過大例外】：荷物重量センサが許容耐荷重（1,200kg）超過を検知した場合は、格納を拒否しリジェクト台へ返送する』。",
            "フォーク計測値：パレット総重量が1,480kgと計量された。スタッカークレーン動作を決定せよ。",
            "フォーク計測値：パレット総重量は620kgで許容内である。スタッカークレーン動作を決定せよ。",
            [
                ("pallet_reject_overweight", "耐荷重超過・格納拒否リジェクト返送"),
                ("pallet_store_routine", "規定棚奥へのパレット自動格納実行"),
                ("crane_hoist_free_fall", "昇降台自重フリーフォール"),
                ("mast_sway_damper_lock", "マスト振れ止め油圧固定"),
                ("aisle_light_extinguish", "走行通路照明消灯待機"),
                ("rfid_tag_erase_memory", "パレット電子タグ情報消去")
            ],
            "pallet_reject_overweight", "pallet_store_routine"
        ),
        (
            "22",
            "有人宇宙ステーション生命維持装置（ECLSS）制御規定：『通常規則：船内大気をファン循環し微小粒子を除去する定常循環を行う。ただし【酸素欠乏例外】：居住区酸素分圧が18.0kPa未満へ低下した場合は、最優先で高圧酸素タンクから緊急酸素パルス放出を行う』。",
            "ガス分圧センサ：居住モジュールの酸素分圧が16.8kPaへ異常低下した。ECLSS動作を指示せよ。",
            "ガス分圧センサ：居住モジュールの酸素分圧は21.3kPaの至適正常値を維持している。ECLSS動作を指示せよ。",
            [
                ("eclss_emergency_o2_injection", "最優先・高圧酸素タンク緊急パルス放出"),
                ("eclss_routine_air_circulation", "ファン微小粒子除去・定常空気循環維持"),
                ("eclss_cabin_depressurize", "船内大気真空排気減圧"),
                ("eclss_co2_scrubber_bypass", "二酸化炭素吸着キャニスター遮断"),
                ("eclss_trace_contaminant_burn", "微量有害ガス触媒燃焼器停止"),
                ("eclss_water_recovery_dump", "水再生システム排水船外投棄")
            ],
            "eclss_emergency_o2_injection", "eclss_routine_air_circulation"
        ),
        (
            "23",
            "半導体CMP（化学機械研磨）装置の研磨シーケンス：『通常規則：ウェハ表面を研磨ヘッドで均一加圧研磨する。ただし【スラリー枯渇例外】：研磨剤（スラリー）供給ラインの液面センサが空検知を発報した場合は、スクラッチ防止のため研磨ヘッドを直ちに退避上昇させる』。",
            "研磨剤供給ユニット：スラリーバッファタンクの空検知センサがオンになった。CMPヘッド動作を選択せよ。",
            "研磨剤供給ユニット：スラリー供給圧0.25MPa、流量安定、空検知なし。CMPヘッド動作を選択せよ。",
            [
                ("cmp_head_retract_emergency", "スクラッチ防止・研磨ヘッド直ちに退避上昇"),
                ("cmp_continue_polishing", "均一加圧による定常CMP研磨シーケンス継続"),
                ("cmp_pad_conditioner_overload", "ドレッサー加圧力上限超過"),
                ("cmp_rinse_pure_water_off", "超純水リンスノズル全閉"),
                ("cmp_vacuum_chuck_release", "研磨中ウェハ吸着真空即時解除"),
                ("cmp_platen_reverse_speed", "研磨定盤急激逆回転")
            ],
            "cmp_head_retract_emergency", "cmp_continue_polishing"
        ),
        (
            "24",
            "自律走行車ADAS（先進運転支援システム）制御規定：『通常規則：前走車との車間距離を維持しつつ設定巡航速度で追従走行する。ただし【歩行者飛び出し例外】：歩行者急接近衝突予測時間が1.2秒未満となった場合は、追従クルーズを強制解除し自動緊急ブレーキ（AEB）を満制動でかける』。",
            "フュージョンセンサ：側方物陰から歩行者が飛び出し、衝突予測時間0.8秒を算出した。車両制御を選択せよ。",
            "フュージョンセンサ：前走車追従中、歩行者飛び出しリスクなし、衝突予測時間は未検出である。車両制御を選択せよ。",
            [
                ("adas_aeb_full_braking", "クルーズ強制解除・自動緊急ブレーキ満制動"),
                ("adas_adaptive_cruise_follow", "前走車車間維持・設定巡航追従走行継続"),
                ("adas_high_beam_continuous", "ハイビーム照射固定"),
                ("adas_airbag_pre_deploy", "エアバッグ事前展開爆破"),
                ("adas_handbrake_drift_turn", "パーキングブレーキ急引込"),
                ("adas_horn_sound_only", "クラクションのみ連続吹鳴")
            ],
            "adas_aeb_full_braking", "adas_adaptive_cruise_follow"
        ),
        (
            "25",
            "地熱発電所生産井（蒸気井）の安全規則：『通常規則：坑口セパレータで熱水と分離した過熱蒸気を主発電タービンへ連続送気する。ただし【硫化水素高濃度例外】：大気検知器の硫化水素（H2S）濃度が10ppmを超過した場合は、タービンバイパス弁を開放し消石灰中和スクラバーへ緊急誘導する』。",
            "大気環境モニタ：坑口周辺の硫化水素濃度が18.5ppmに急上昇した。蒸気ハンドリングを指示せよ。",
            "大気環境モニタ：硫化水素濃度は0.3ppmの極低濃度であり、蒸気質は良好である。蒸気ハンドリングを指示せよ。",
            [
                ("divert_scrubber_neutralize", "バイパス弁開放・消石灰中和スクラバー緊急誘導"),
                ("send_steam_main_turbine", "主発電タービンへの過熱蒸気連続送気"),
                ("quench_geothermal_well_cement", "坑井内セメントプラグ完全密閉"),
                ("open_cooling_tower_overflow", "冷却塔温排水河川直放流"),
                ("hot_water_reinjection_cut", "還元熱水地下圧入ポンプ停止"),
                ("generator_excitation_max", "発電機界磁励磁電流強制最大")
            ],
            "divert_scrubber_neutralize", "send_steam_main_turbine"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k6_defs:
        pairs.append({
            "id": f"rc2b4_prio_{gid}_s1", "group_id": f"rc2b4_prio_{gid}", "family": "priority_exception",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_prio_{gid}_s2", "group_id": f"rc2b4_prio_{gid}", "family": "priority_exception",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=8 (5 pairs: groups 26 to 30) ---
    k8_defs = [
        (
            "26",
            "高速道路ETCレーン制御規定：『通常規則：車載器アンテナ通信正常で有効期限内カードを確認した場合は、発進制御バーを開放し通過許可とする。ただし【不正・未納例外】：通信不一致またはブラックリスト未納車両IDを検出した場合は、バーを閉止維持し赤色進入禁止シグナルと警告ブザーを作動させる』。",
            "車側アンテナ通信結果：通信パケットチェックサムエラーおよび無効カードフラグが検出された。ETCレーン制御を選択せよ。",
            "車側アンテナ通信結果：正規クレジットカード会社発行ETCカード認証完了、未納照合クリアである。ETCレーン制御を選択せよ。",
            [
                ("etc_barrier_close_deny", "発進バー閉止維持・赤色禁止シグナル・警告音作動"),
                ("etc_barrier_open_pass", "発進制御バー自動開放・通過許可"),
                ("etc_deploy_tire_shredder", "路面スパイクタイヤ破砕器起動"),
                ("etc_toll_double_penalty", "通行料金自動3倍追徴"),
                ("etc_camera_flash_destroy", "車番撮影ストロボ高電圧過負荷"),
                ("etc_reboot_linux_controller", "レーンコントローラー即時再起動"),
                ("etc_manual_cash_collect", "自動硬貨釣銭釣銭機受入開放"),
                ("etc_flood_lane_drain", "レーン側溝散水消火")
            ],
            "etc_barrier_close_deny", "etc_barrier_open_pass"
        ),
        (
            "27",
            "総合病院中央材料室（滅菌サプライ）払出基準：『通常規則：化学的インジケータ（CI）が変色合格した滅菌済み手術器械セットを各手術室へ払出出庫する。ただし【インジケータ不合格例外】：パック内CIの変色が不完全または変色なしの場合は、滅菌無効としロット全体を再洗浄・再滅菌へ差し戻す』。",
            "器械パック検品：CIテープの基準変色境界に達しておらず、未変色の黄色が残存している。材料室処置を決定せよ。",
            "器械パック検品：クラス5総合インジケータが完全に変色黒化し、合格マークが出現している。材料室処置を決定せよ。",
            [
                ("sterilization_fail_remand", "滅菌無効判定・ロット全体再洗浄再滅菌差戻し"),
                ("sterilization_pass_dispense", "滅菌合格確認・手術室への払出出庫実施"),
                ("discard_surgical_instruments", "高額手術器具全品即時金属ゴミ廃棄"),
                ("autoclave_air_vent_seal", "滅菌缶排気フィルター完全封鎖"),
                ("soak_formalin_liquid", "ホルマリン原液槽への浸漬保管"),
                ("peel_pouch_retape_pack", "不合格パウチの上からテープ貼り隠蔽"),
                ("manual_sign_falsify", "点検記録簿の手書き偽装捺印"),
                ("ultrasonic_cleaner_dry_heat", "超音波洗浄機空焚き加熱")
            ],
            "sterilization_fail_remand", "sterilization_pass_dispense"
        ),
        (
            "28",
            "石油精製コンビナート常圧蒸留装置（トッパー）の運転規定：『通常規則：原料原油を加熱炉で360℃に加熱し蒸留塔へ装入して分留する。ただし【原油水分・塩分急増例外】：原油脱塩装置（デソルター）出口の水分が0.5%を超過した場合は、塔内突沸・圧力サージを防ぐため原油供給量を緊急半減し加熱炉熱量を絞る』。",
            "脱塩プロセスモニタ：原油タンカー荷繰り変化によりデソルター出口水分が1.4%に急上昇した。トッパー制御を指示せよ。",
            "脱塩プロセスモニタ：脱塩後原油の水分は0.08%で極めて清澄、塩分濃度も管理値内である。トッパー制御を指示せよ。",
            [
                ("cutback_crude_feed_furnace", "突沸防止・原油供給量緊急半減・加熱炉熱量減衰"),
                ("steady_crude_fractionation", "定常温度による原料原油連続装入・分留継続"),
                ("dump_crude_slop_ocean", "原油スロップ油海洋緊急投棄"),
                ("side_stream_naphtha_boil", "ナフサ留出弁全開過熱"),
                ("reboiler_steam_max_flow", "塔底リボイラ高圧蒸気最大供給"),
                ("quench_column_with_cold_water", "蒸留塔頂部への冷水直接注入"),
                ("heavy_oil_pump_stop_dry", "重油抜出ポンプ空運転停止"),
                ("sulfur_recovery_bypass_air", "硫黄回収装置バイパス直接放散")
            ],
            "cutback_crude_feed_furnace", "steady_crude_fractionation"
        ),
        (
            "29",
            "火力発電所ボイラー給水ポンプ（BFP）の切替連動：『通常規則：主軸駆動給水ポンプ（MBFP）によりボイラー缶内へ給水を定格連続供給する。ただし【主機故障例外】：MBFPの軸受油圧低下または吸込弁誤閉塞アラームが発生した場合は、缶水枯渇を防ぐため予備電動給水ポンプ（EBFP）を自動瞬時起動する』。",
            "ポンプ監視計装：主給水ポンプMBFPの軸受潤滑油圧がトリップ設定値未満に低下した。ボイラー給水制御を指示せよ。",
            "ポンプ監視計装：主給水ポンプMBFPの軸受温度・油圧・吐出圧いずれも健全値である。ボイラー給水制御を指示せよ。",
            [
                ("ebfp_auto_instant_start", "缶水枯渇防止・予備電動給水ポンプEBFP自動起動"),
                ("mbfp_maintain_feed_steady", "主軸給水ポンプMBFPによる定格連続給水維持"),
                ("boiler_blowdown_open_full", "ボイラー缶水全量一括緊急ブロー"),
                ("steam_superheater_isolate", "過熱器蒸気止め弁全閉"),
                ("fuel_gas_burner_overfire", "微粉炭バーナー燃料供給最大過熱"),
                ("deaerator_safety_valve_lift", "脱気器安全弁手動強制吹出し"),
                ("condenser_cooling_water_stop", "復水器海水ポンプ停止"),
                ("economizer_flue_gas_bypass", "節炭器煙道ダンパー全閉")
            ],
            "ebfp_auto_instant_start", "mbfp_maintain_feed_steady"
        ),
        (
            "30",
            "超電導磁気浮上式鉄道（リニア）の浮上案内制御：『通常規則：車載超電導磁石と軌道側地上コイルの電磁誘導により目標浮上高（100mm）を保ち超高速走行する。ただし【クエンチ前兆例外】：いずれかの車載超電導コイルに微小抵抗発生（常電導転移前兆）を検知した場合は、地上変電所電力供給を回生制動減速へ切り替え機械式非常着地車輪を展開する』。",
            "磁気ヘリウム計装：右台車第2極超電導コイルの電圧バランス回路がクエンチ前兆不平衡電圧を検知した。運行制御を決定せよ。",
            "磁気ヘリウム計装：全16極の超電導コイル起電力は完全ゼロ（無抵抗）、真空度・極低温も正常である。運行制御を決定せよ。",
            [
                ("linear_deploy_emergency_skids", "回生制動減速移行・機械式非常着地車輪緊急展開"),
                ("linear_maintain_maglev_speed", "目標浮上高維持による超電導磁気浮上超高速走行"),
                ("linear_invert_propulsion_phase", "推進コイル3相位相逆相急制動"),
                ("linear_quench_dump_resistor", "超電導全エネルギー放電抵抗投入"),
                ("linear_dewar_vacuum_break", "断熱デュワー大気真空破壊"),
                ("linear_pantograph_arcing", "非接触集電ギャップ強制短絡"),
                ("linear_cabin_door_jettison", "客室ドア緊急投棄解放"),
                ("linear_turnaround_switch_run", "渡り線分岐器高速割り出し突入")
            ],
            "linear_deploy_emergency_skids", "linear_maintain_maglev_speed"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k8_defs:
        pairs.append({
            "id": f"rc2b4_prio_{gid}_s1", "group_id": f"rc2b4_prio_{gid}", "family": "priority_exception",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_prio_{gid}_s2", "group_id": f"rc2b4_prio_{gid}", "family": "priority_exception",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    return pairs
