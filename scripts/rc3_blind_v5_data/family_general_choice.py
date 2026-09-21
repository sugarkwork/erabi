"""Blind v5 Family: General Choice (30 pairs, 60 cases).

Choice count distribution:
- K=3: 5 pairs (gen_01 to gen_05)
- K=4: 15 pairs (gen_06 to gen_20)
- K=6: 10 pairs (gen_21 to gen_30)

Zero model inference during authoring; 100% fresh domain scenarios.
Token length strictly controlled (all <= 350 tokens).
Features municipal infrastructure, corporate operations, IT services,
logistics, facilities management, and administrative workflows.
"""

from __future__ import annotations
from typing import Any, Dict, List


def get_general_choice_pairs() -> List[Dict[str, Any]]:
    pairs = []

    # K=3: 5 pairs (01..05)
    k3_defs = [
        (
            "01",
            "大型複合商業施設の館内空調デマンドレスポンス（DR）規程。規程：『電力逼迫警報レベル1（契約電力90%到達）のときは共用部設定温度を1℃緩和し、レベル2（95%到達）のときは空調送風ファンを間欠運転へ移行、通常時（80%未満）は快適性優先の定常設定を維持する』。",
            "BEMS電力モニタ：受電電力が契約電力の91.4%に達した。空調デマンド制御を選択せよ。",
            "dr_relax_temp_one_degree",
            "BEMS電力モニタ：受電電力が契約電力の72.0%で安定推移している。空調デマンド制御を選択せよ。",
            "dr_maintain_steady_comfort",
            [
                ("dr_relax_temp_one_degree", "共用部設定温度1℃緩和"),
                ("dr_intermittent_fan_run", "送風ファン間欠運転移行"),
                ("dr_maintain_steady_comfort", "定常設定快適性維持"),
            ],
        ),
        (
            "02",
            "クラウドデータセンターのインシデントエスカレーション規程。規程：『サービス停止影響ユーザー数が10,000人以上の重大インシデントはC-Level役員へ即報・全社対策本部立ち上げ、1,000〜10,000人未満はオンコールSREチームへ緊急招集通知、1,000人未満の局所影響時は通常チケット発行・日中保守対応とする』。",
            "障害監視ダッシュボード：認証APIエラーにより現在25,000アカウントがログイン不能。エスカレーションを選択せよ。",
            "incident_clevel_executive_brief",
            "障害監視ダッシュボード：特定管理コンソールの稀少レポート出力機能で一部ユーザー（80人）のみ500エラー。エスカレーションを選択せよ。",
            "incident_routine_ticket_dispatch",
            [
                ("incident_clevel_executive_brief", "役員即報全社対策本部"),
                ("incident_sre_oncall_page", "オンコールSRE緊急招集"),
                ("incident_routine_ticket_dispatch", "通常チケット日中保守"),
            ],
        ),
        (
            "03",
            "都市ごみ焼却工場の排ガス窒素酸化物（NOx）脱硝管理規程。規程：『煙突出口NOx濃度が50ppm超のときはアンモニア還元剤注入ポンプを増段増量、30〜50ppmの間は現状の適正注入量を維持、30ppm未満のときはアンモニアスリップ（未反応放出）防止のため注入量を段階的に絞る』。",
            "連続排ガス測定装置（CEMS）：出口NOx濃度は62ppmを示している。薬品注入制御を選択せよ。",
            "cems_increase_ammonia_feed",
            "連続排ガス測定装置（CEMS）：出口NOx濃度は18ppmまで低下している。薬品注入制御を選択せよ。",
            "cems_throttle_ammonia_slip_prevent",
            [
                ("cems_increase_ammonia_feed", "アンモニア注入増段増量"),
                ("cems_maintain_steady_injection", "適正注入量維持"),
                ("cems_throttle_ammonia_slip_prevent", "注入量絞りスリップ防止"),
            ],
        ),
        (
            "04",
            "自治体水道局の配水管ネットワーク水圧遠隔調整基準。基準：『末端給水栓動水圧が0.15MPa未満のときは管路加圧インラインポンプを起動、0.15〜0.40MPaの適正域では現行減圧弁開度を固定、0.40MPa超の過高圧時は漏水・破裂防止のため電動減圧弁を絞り開度へ調整する』。",
            "管網SCADA遠隔テレメータ：高台住宅街の末端水圧が0.11MPaまで低下した。水圧制御を選択せよ。",
            "scada_start_incline_booster_pump",
            "管網SCADA遠隔テレメータ：夜間需要減少に伴い幹線末端水圧が0.52MPaまで上昇した。水圧制御を選択せよ。",
            "scada_throttle_pressure_reducing_valve",
            [
                ("scada_start_incline_booster_pump", "インライン加圧ポンプ起動"),
                ("scada_hold_steady_valve_opening", "現行減圧弁開度固定"),
                ("scada_throttle_pressure_reducing_valve", "減圧弁絞り過高圧防止"),
            ],
        ),
        (
            "05",
            "空港旅客手荷物自動搬送システム（BHS）のトレイ合流規程。規程：『合流合流点手前の荷詰まりセンサがトレイ滞留20個以上を検知したときは上流フィーダーコンベアを一時停止、滞留5〜19個の間はフィーダー搬送速度を50%減速、滞留5個未満のときは通常設計速度で連続搬入する』。",
            "光学通過センサログ：合流直前のトレイ滞留数は現在2個で合流クリア。コンベア搬送速度を選択せよ。",
            "bhs_normal_design_speed_run",
            "光学通過センサログ：手荷物タグ読取エラーにより合流部にトレイ28個が数珠繋ぎで滞留。コンベア搬送速度を選択せよ。",
            "bhs_stop_upstream_feeder_halt",
            [
                ("bhs_normal_design_speed_run", "通常設計速度連続搬入"),
                ("bhs_derate_half_speed_flow", "フィーダー50%減速搬送"),
                ("bhs_stop_upstream_feeder_halt", "上流フィーダー一時停止"),
            ],
        ),
    ]

    for pid, ctx, q1, t1, q2, t2, chs in k3_defs:
        choices = [{"id": cid, "text": ctxt} for cid, ctxt in chs]
        pairs.append({
            "pair_id": f"rc3_blind5_gen_{pid}",
            "family": "general_choice",
            "k": 3,
            "case_1": {
                "id": f"rc3_blind5_gen_{pid}_s1",
                "group_id": f"rc3_blind5_gen_{pid}",
                "family": "general_choice",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1},
            },
            "case_2": {
                "id": f"rc3_blind5_gen_{pid}_s2",
                "group_id": f"rc3_blind5_gen_{pid}",
                "family": "general_choice",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2},
            },
        })

    # K=4: 15 pairs (06..20)
    k4_defs = [
        (
            "06",
            "総合物流フルフィルメントセンターの自動仕分ソーター投入ポリシー。ポリシー：『シュート満杯率が90%以上のときは該当仕向け先への小包投入を一時拒絶、70〜89%の間は投入ピッチを3秒から6秒へ間引き、50〜69%の間は標準投入ピッチ3秒維持、50%未満のときは空きシュート優先投入バッチを割り当てる』。",
            "ソーターカメラ所見：第3関東向けシュートの荷物充填率は現在94%である。ソーター制御を選択せよ。",
            "sorter_reject_chute_inflow",
            "ソーターカメラ所見：第7東北向けシュートの充填率は現在32%でガラ空きである。ソーター制御を選択せよ。",
            "sorter_assign_empty_priority_batch",
            [
                ("sorter_reject_chute_inflow", "該当仕向け先投入一時拒絶"),
                ("sorter_throttle_double_pitch", "投入ピッチ間引き減速"),
                ("sorter_maintain_standard_pitch", "標準投入ピッチ維持"),
                ("sorter_assign_empty_priority_batch", "空きシュート優先バッチ割当"),
            ],
        ),
        (
            "07",
            "スマートオフィスビルのブラインド自動追尾調光基準。基準：『外部日射照度が60,000lx以上のときは窓側ブラインドスラット角を水平遮蔽（75度）に設定、30,000〜60,000lxの間は眩しさ防止スラット角45度、10,000〜30,000lxの間は採光優先スラット角15度、10,000lx未満の曇天時はブラインド全開アップ格納とする』。",
            "屋上日射計計測：快晴直射日光により外光照度は78,000lxに達した。ブラインド角度を選択せよ。",
            "blind_tilt_horizontal_75deg",
            "屋上日射計計測：厚い雨雲に覆われ外光照度は4,500lxまで低下した。ブラインド角度を選択せよ。",
            "blind_retract_full_open_up",
            [
                ("blind_tilt_horizontal_75deg", "スラット角75度水平遮蔽"),
                ("blind_tilt_glare_prevent_45deg", "スラット角45度防眩設定"),
                ("blind_tilt_daylight_15deg", "スラット角15度採光優先"),
                ("blind_retract_full_open_up", "ブラインド全開格納アップ"),
            ],
        ),
        (
            "08",
            "都市ガス供給ネットワークの付臭剤（TBM/DMS）自動注入規程。規程：『ガス送出流量が10,000Nm3/h以上のときは高圧多連ダイヤフラム注入ポンプ連動、3,000〜10,000Nm3/hの間は単機定格注入、1,000〜3,000Nm3/hの間は微小パルス注入、1,000Nm3/h未満の夜間極小流量時は配管内滞留防止のため注入を一時休止する』。",
            "超音波ガス流量計：現在基幹高圧ラインの送出流量は14,200Nm3/hである。付臭剤ポンプを選択せよ。",
            "odor_multi_diaphragm_gang_run",
            "超音波ガス流量計：深夜未明の需要減退により送出流量は650Nm3/hとなった。付臭剤ポンプを選択せよ。",
            "odor_pause_temporary_standby",
            [
                ("odor_multi_diaphragm_gang_run", "多連ダイヤフラム連動注入"),
                ("odor_single_rated_injection", "単機定格注入運転"),
                ("odor_micro_pulse_dosing", "微小パルス精密注入"),
                ("odor_pause_temporary_standby", "注入一時休止待機"),
            ],
        ),
        (
            "09",
            "自治体清掃工場の粗大ごみ破砕機過負荷保護規程。規程：『破砕油圧モータ主回路電流が定格の120%以上のときは即時正転停止・5秒間逆転吐き出し、100〜120%の間は投入プッシャー停止・破砕単独継続、70〜100%の間は投入プッシャー低速前進、70%未満の軽負荷時はプッシャー全速投入とする』。",
            "油圧制御盤モニタ：金庫噛み込みによりモータ電流が定格138%へ急上昇。破砕機動作を選択せよ。",
            "shredder_reverse_eject_instant",
            "油圧制御盤モニタ：木製家具の破砕によりモータ電流は55%と極めて軽快。破砕機動作を選択せよ。",
            "shredder_pusher_full_speed_feed",
            [
                ("shredder_reverse_eject_instant", "即時停止5秒逆転吐き出し"),
                ("shredder_stop_pusher_crush_alone", "プッシャー停止単独破砕"),
                ("shredder_pusher_slow_advance", "プッシャー低速前進"),
                ("shredder_pusher_full_speed_feed", "プッシャー全速投入"),
            ],
        ),
        (
            "10",
            "エンタープライズVoIP電話システムのネットワークQoSトラフィック制御規程。規程：『音声パケットジッターが50ms以上のときは音声コーデックを高圧縮低帯域（G.729）へフォールバック、20〜50msの間は優先キューイング帯域保証増額、5〜20msの間は標準コーデック（G.711）維持、5ms未満の高品質時は広帯域HD音声（G.722）を適用する』。",
            "WANプローブ監視：パケット遅延ジッターが68msまで悪化し音声途切れ兆候。QoS制御を選択せよ。",
            "qos_fallback_g729_low_bw",
            "WANプローブ監視：専用光回線増強によりジッターは2.4msの極小値で極めて安定。QoS制御を選択せよ。",
            "qos_apply_g722_hd_voice",
            [
                ("qos_fallback_g729_low_bw", "高圧縮G.729フォールバック"),
                ("qos_boost_priority_queue_bw", "優先キュー帯域保証増額"),
                ("qos_maintain_g711_standard", "標準G.711コーデック維持"),
                ("qos_apply_g722_hd_voice", "広帯域G.722_HD音声適用"),
            ],
        ),
        (
            "11",
            "地下鉄駅舎の浸水防止止水板（防水扉）自動起立基準。基準：『外部出入口道路冠水深が30cm以上のときは電動油圧止水板を最大全起立（90度）ロック、15〜30cmの間は警報鳴動下で半起立（45度）、5〜15cmの間は注意ランプ点灯・係員手動準備、5cm未満のときは床面フラット完全格納とする』。",
            "出入口超音波水位センサ：道路側冠水深が38cmに達し階段へ流入寸前。止水板動作を選択せよ。",
            "flood_barrier_full_erect_90deg",
            "出入口超音波水位センサ：小雨が降るものの道路冠水はなくセンサ値は0cmである。止水板動作を選択せよ。",
            "flood_barrier_recessed_flat_store",
            [
                ("flood_barrier_full_erect_90deg", "止水板最大全起立ロック"),
                ("flood_barrier_half_erect_45deg", "警報鳴動半起立位置"),
                ("flood_barrier_manual_prep_lamp", "注意点灯係員手動準備"),
                ("flood_barrier_recessed_flat_store", "床面フラット完全格納"),
            ],
        ),
        (
            "12",
            "製薬GMP工場純水製造設備（RO/EDI）の循環殺菌管理規程。規程：『循環ループ内オゾン水濃度が0.10mg/L以上のときは定期オゾン殺菌サーキュレーション実行、0.05〜0.10mg/Lの間はオゾン発生器出力増強、0.02〜0.05mg/Lの間は紫外線（UV）分解ランプ点灯・ユースポイント給水待機、0.02mg/L未満の脱オゾン完了時は製造ラインへの純水供給を承認する』。",
            "水質計モニタ：ループ内オゾン濃度は0.14mg/Lを測定。純水システム制御を選択せよ。",
            "edi_execute_ozone_disinfection",
            "水質計モニタ：UV照射後オゾン濃度は0.005mg/Lとなり完全消失を確認。純水システム制御を選択せよ。",
            "edi_approve_production_feed",
            [
                ("edi_execute_ozone_disinfection", "定期オゾン殺菌循環実行"),
                ("edi_boost_ozone_generator", "オゾン発生器出力増強"),
                ("edi_uv_lamp_destruct_standby", "UV分解ユース待機"),
                ("edi_approve_production_feed", "製造ライン純水供給承認"),
            ],
        ),
        (
            "13",
            "立体自動倉庫のスタッカークレーン制動減速制御基準。基準：『停止目標位置までの残り距離が500mm以上のときは定速走行、100〜500mmの間はインバータ回生S字減速、20〜100mmの間はクリープ極微速アプローチ、20mm以内の目標到達時はメカニカルブレーキ噛み合い・位置決めピン挿入とする』。",
            "レーザー測距計：目的パレット棚までの残り距離は12mmである。クレーン駆動制御を選択せよ。",
            "crane_mechanical_brake_pin_insert",
            "レーザー測距計：目的棚まで残り2,400mmを走行中。クレーン駆動制御を選択せよ。",
            "crane_constant_speed_travel",
            [
                ("crane_constant_speed_travel", "定速走行維持"),
                ("crane_s_curve_regen_decelerate", "インバータ回生S字減速"),
                ("crane_creep_approach_speed", "クリープ極微速アプローチ"),
                ("crane_mechanical_brake_pin_insert", "メカニカル制動ピン挿入"),
            ],
        ),
        (
            "14",
            "高層オフィスビルの非常用エレベーター地震時管制運転基準。基準：『地震計P波感知（主要動前）時は最寄り階に急停止・扉開放、S波低ガル（50〜100gal）時は全館一斉非常停止アナウンス下で全扉開、S波高ガル（100gal以上）時は昇降路内安全点検完了まで完全運行休止ロック、地震計無検知時は定常自動運行を維持する』。",
            "ビル防災センター地震計：直下型地震の強烈なS波加速度185galを記録。エレベーター管制を選択せよ。",
            "elv_lockout_until_shaft_inspect",
            "ビル防災センター地震計：全チャンネル平常（0gal）。エレベーター管制を選択せよ。",
            "elv_maintain_normal_operation",
            [
                ("elv_p_wave_nearest_floor_open", "P波最寄り階急停止扉開"),
                ("elv_s_wave_all_doors_evacuate", "低ガル非常停止扉全開"),
                ("elv_lockout_until_shaft_inspect", "高ガル運行休止完全ロック"),
                ("elv_maintain_normal_operation", "定常自動運行維持"),
            ],
        ),
        (
            "15",
            "高速道路トンネル換気ジェットファンの視程連動制御規程。規程：『トンネル内透過率計（VI計）が50%未満のときは全ジェットファンを最大順送風運転、50〜70%の間は半数台数を交互間欠運転、70〜85%の間は低速換気運転、85%以上の清浄大気時はジェットファン全台停止・自然通風待機とする』。",
            "防災管制モニタ：大型トラック通行集中により視程VI計が42%まで悪化。ジェットファン制御を選択せよ。",
            "tunnel_fan_all_max_forward_run",
            "防災管制モニタ：夜間交通量僅少により視程VI計は96%で空気清浄。ジェットファン制御を選択せよ。",
            "tunnel_fan_all_stop_natural_draft",
            [
                ("tunnel_fan_all_max_forward_run", "全台最大順送風運転"),
                ("tunnel_fan_half_alternate_run", "半数台数交互間欠運転"),
                ("tunnel_fan_low_speed_vent", "低速換気運転"),
                ("tunnel_fan_all_stop_natural_draft", "全台停止自然通風待機"),
            ],
        ),
        (
            "16",
            "都市ごみ収集車の塵芥投入口安全バー連動規程。規程：『緊急停止非常停止ボタン押下時はパッカー板油圧回路即時圧抜き停止、安全バー障害物接触時はパッカー板50mm緊急上昇反転、手動積込スイッチ作動時は単動1サイクル積込、異常なし待機時は回転板アイドリング停止とする』。",
            "安全センサ：積込口の安全バーに作業員の作業着が接触した。パッカー機構制御を選択せよ。",
            "packer_emergency_reverse_50mm",
            "作業盤信号：非常停止押しボタンスイッチが作業員により強く叩き込まれた。パッカー機構制御を選択せよ。",
            "packer_depressurize_hydraulic_stop",
            [
                ("packer_depressurize_hydraulic_stop", "油圧即時圧抜き停止"),
                ("packer_emergency_reverse_50mm", "安全バー緊急上昇反転"),
                ("packer_single_cycle_load", "単動1サイクル積込"),
                ("packer_idle_standby_stop", "回転板アイドリング停止"),
            ],
        ),
        (
            "17",
            "浄水場の急速ろ過池逆洗シーケンス規程。規程：『ろ過砂層損失水頭が2.0m以上のときは逆洗排水弁全開・洗浄水ポンプ起動、1.5〜2.0mの間は逆洗待機キュー登録、1.0〜1.5mの間は次期逆洗予告ランプ点灯、1.0m未満のときは定常急速ろ過継続とする』。",
            "ろ過池差圧トランスミッタ：第4池の損失水頭が2.25mに達した。ろ過池シーケンスを選択せよ。",
            "filter_start_backwash_sequence",
            "ろ過池差圧トランスミッタ：新砂投入直後につき損失水頭は0.35mである。ろ過池シーケンスを選択せよ。",
            "filter_continue_normal_filtration",
            [
                ("filter_start_backwash_sequence", "逆洗排水弁開洗浄ポンプ起動"),
                ("filter_register_backwash_queue", "逆洗待機キュー登録"),
                ("filter_turn_on_warning_lamp", "次期逆洗予告点灯"),
                ("filter_continue_normal_filtration", "定常急速ろ過継続"),
            ],
        ),
        (
            "18",
            "コンテナターミナルガントリークレーンの風速退避規程。規程：『瞬間風速が20m/s以上のときはレールクランプ締結・アンカーピン完全固縛、16〜20m/sの間はコンテナ荷役即時中止・ブーム巻き上げ、12〜16m/sの間は空コンテナ取扱中止、12m/s未満のときは全コンテナ荷役通常作業とする』。",
            "気象観測タワー風速計：低気圧急襲により瞬間風速23.4m/sを観測。クレーン保安動作を選択せよ。",
            "gantry_rail_clamp_anchor_pin_lock",
            "気象観測タワー風速計：穏やかな海風で瞬間風速は6.2m/sである。クレーン荷役指示を選択せよ。",
            "gantry_continue_all_operations",
            [
                ("gantry_rail_clamp_anchor_pin_lock", "レールクランプアンカー固縛"),
                ("gantry_abort_cargo_boom_up", "荷役中止ブーム巻き上げ"),
                ("gantry_suspend_empty_containers", "空コンテナ取扱中止"),
                ("gantry_continue_all_operations", "全コンテナ荷役通常作業"),
            ],
        ),
        (
            "19",
            "大型データセンター非常用ディーゼル発電機（EDG）無停電給電切替基準。基準：『本線特別高圧受電停電かつ母線低電圧時はEDG自動起動・40秒以内VCB投入、電圧不平衡3%以上のときは受電受入一時保留・蓄電池給電維持、瞬時電圧低下（瞬低）時は受電継続・無停電電源装置（UPS）補償、正常受電時は受電遮断器投入維持とする』。",
            "保護継電器ログ：台風により特高2回線が同時トリップ停電した。所内電力切替を選択せよ。",
            "edg_auto_start_vcb_close_40s",
            "電力品質アナライザー：特別高圧三相電圧は完全平衡で停電兆候なし。所内電力切替を選択せよ。",
            "edg_maintain_grid_intake",
            [
                ("edg_auto_start_vcb_close_40s", "EDG自動起動40秒内投入"),
                ("edg_hold_intake_ups_battery", "受電保留蓄電池給電維持"),
                ("edg_ride_through_ups_comp", "瞬低受電継続UPS補償"),
                ("edg_maintain_grid_intake", "正常商用受電遮断器維持"),
            ],
        ),
        (
            "20",
            "下水道中継ポンプ場の汚水流入量制御規程。規程：『吸水井水位が危険満水深（HWL）以上のときは全台数（4台）フル稼働排水、中水位（MWL）以上のときは2台並列運転、低水位（LWL）以上のときは1台単独運転、LWL未満のときはキャビテーション防止のため全ポンプ完全停止とする』。",
            "水位計超音波測定：ゲリラ豪雨流入により吸水井水位がHWLを突破。ポンプ台数制御を選択せよ。",
            "pump_run_all_four_units_max",
            "水位計超音波測定：渇水深夜により水位がLWLを下回った。ポンプ台数制御を選択せよ。",
            "pump_stop_all_prevent_cavitation",
            [
                ("pump_run_all_four_units_max", "全4台フル稼働排水"),
                ("pump_run_two_parallel_units", "2台並列運転"),
                ("pump_run_single_unit_only", "1台単独運転"),
                ("pump_stop_all_prevent_cavitation", "全ポンプ完全停止"),
            ],
        ),
    ]

    for pid, ctx, q1, t1, q2, t2, chs in k4_defs:
        choices = [{"id": cid, "text": ctxt} for cid, ctxt in chs]
        pairs.append({
            "pair_id": f"rc3_blind5_gen_{pid}",
            "family": "general_choice",
            "k": 4,
            "case_1": {
                "id": f"rc3_blind5_gen_{pid}_s1",
                "group_id": f"rc3_blind5_gen_{pid}",
                "family": "general_choice",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1},
            },
            "case_2": {
                "id": f"rc3_blind5_gen_{pid}_s2",
                "group_id": f"rc3_blind5_gen_{pid}",
                "family": "general_choice",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2},
            },
        })

    # K=6: 10 pairs (21..30)
    k6_defs = [
        (
            "21",
            "空港滑走路のバードストライク防止運用規程。規程：『滑走路直上に大型鳥類群（サギ・カラス50羽以上）視認時は滑走路一時閉鎖・空砲威嚇出動、中型鳥類10〜49羽視認時は離着陸便へバードアラート通知・巡回車両駆逐、小型鳥類1〜9羽時は離陸滑走間隔拡大、鳥類ゼロ時は定常滑走路運用、夜間渡り鳥レーダー探知時はバード探知レーダー追尾強化、滑走路内鳥衝突死骸発見時は路面清掃車急行・回収を実行する』。",
            "滑走路監視タワー視認：滑走路端の上空にカラスの群れ約80羽が旋回停滞中。滑走路管制を選択せよ。",
            "bird_close_runway_pyro_dispatch",
            "バードパトロール報告：滑走路全面およびアプローチ空間に鳥影は全く見当たらない。滑走路管制を選択せよ。",
            "bird_steady_runway_operations",
            [
                ("bird_close_runway_pyro_dispatch", "滑走路一時閉鎖空砲出動"),
                ("bird_alert_traffic_patrol_chase", "バードアラート巡回駆逐"),
                ("bird_extend_takeoff_separation", "離陸滑走間隔拡大"),
                ("bird_steady_runway_operations", "定常滑走路運用維持"),
                ("bird_radar_tracking_boost", "夜間レーダー追尾強化"),
                ("bird_sweeper_truck_carcass_clean", "清掃車急行死骸回収"),
            ],
        ),
        (
            "22",
            "都市高速道路料金所のETCレーン自動開閉バー運用規程。規程：『ETC車載器無線通信が正常決済完了時は発進誘導青信号点灯・開閉バー開放、通信未完了ETCカード未挿入時はバー閉止固定・後続追突防止赤信号、ETCカード有効期限切れ時は警告チャイム吹鳴・係員インターホン呼出、不正通行車両強行突破時はタイヤ突起スパイク展開・防犯カメラ連写、レーン通信機器故障時は隣接ETCレーンへ誘導切替、料金所一斉火災報知時は全バー開放フェイルオープンを実行する』。",
            "ETC路側アンテナ処理：ETC2.0無線ハンドシェイク成功、決済即時完了。レーン制御を選択せよ。",
            "etc_green_lamp_open_barrier",
            "ETC路側アンテナ処理：カード未挿入のまま車両が30km/hでバー直前へ進入。レーン制御を選択せよ。",
            "etc_barrier_close_red_light",
            [
                ("etc_green_lamp_open_barrier", "青信号点灯開閉バー開放"),
                ("etc_barrier_close_red_light", "バー閉止固定追突防止赤信号"),
                ("etc_warning_chime_intercom", "警告チャイム係員呼出"),
                ("etc_spike_deploy_photo_capture", "スパイク展開防犯連写"),
                ("etc_divert_adjacent_lane", "隣接ETCレーン誘導切替"),
                ("etc_fire_alarm_fail_open_all", "火災全バー開放フェイルオープン"),
            ],
        ),
        (
            "23",
            "超高層タワー展望台のエレベーター混雑制御ポリシー。ポリシー：『展望デッキ滞留客数が定員の95%以上のときは上りエレベーター搭乗券発券一時停止、85〜95%の間は上り搬送レート半減・下り優先運行、70〜85%の間は通常定時運行、50〜70%の間はグループ相乗り誘導、50%未満の閑散時は低速省エネ運行、緊急強風時は展望台即時閉鎖・全客下りピストン輸送を実行する』。",
            "チケットゲートカウンタ：展望デッキ内の現在入場者数は定員97%の超満員。運行指示を選択せよ。",
            "tower_halt_inbound_ticketing",
            "チケットゲートカウンタ：平日雨天により現在滞留者は定員25%のみ。運行指示を選択せよ。",
            "tower_low_speed_economy_run",
            [
                ("tower_halt_inbound_ticketing", "上り発券一時停止"),
                ("tower_derate_inbound_half_rate", "上り搬送半減下り優先"),
                ("tower_normal_scheduled_run", "通常定時運行"),
                ("tower_group_rideshare_guide", "グループ相乗り誘導"),
                ("tower_low_speed_economy_run", "低速省エネ運行"),
                ("tower_evacuate_piston_down", "展望台閉鎖下りピストン輸送"),
            ],
        ),
        (
            "24",
            "港湾コンテナヤードのトランスファークレーン（RTG）自動荷役ディスパッチ基準。基準：『外部トレーラー待機台数が20台以上のときは全RTGヤード荷役最優先配分、10〜19台の間は本船荷役とヤード荷役均等配分、5〜9台の間は本船荷役70%優先、5台未満のときは空きRTGを予防保全点検待機、バッテリ残量20%未満時は急速充電ステーション直行、ヤード強風25m/s超時はRTGアンカー固定完全退避を実行する』。",
            "ゲート前ヤードカメラ：搬入待ちコンテナトレーラーが26台の長蛇の列を形成。ディスパッチを選択せよ。",
            "rtg_all_priority_yard_intake",
            "ゲート前ヤードカメラ：深夜搬入完了によりゲート待機トレーラーは2台のみ。ディスパッチを選択せよ。",
            "rtg_standby_preventive_maintenance",
            [
                ("rtg_all_priority_yard_intake", "全機ヤード荷役最優先配分"),
                ("rtg_equal_split_ship_yard", "本船ヤード均等配分"),
                ("rtg_priority_vessel_70", "本船荷役70%優先"),
                ("rtg_standby_preventive_maintenance", "空き機予防保全点検待機"),
                ("rtg_route_fast_charge_station", "急速充電ステーション直行"),
                ("rtg_anchor_clamp_typhoon_lock", "RTGアンカー固定退避"),
            ],
        ),
        (
            "25",
            "自治体総合コールセンターの自動音声応答（IVR）ルーティング規程。規程：『電話保留待ち件数が30件以上のときは全職員への緊急自動着信分配およびWEB案内SMS自動送信、15〜29件の間は管理職への通話ヘルプ要請、5〜14件の間は通常オペレーター待ち呼キューイング、5件未満のときは新人オペレーターへの優先通話割当、自然災害警報発令時は災害専用避難所案内自動アナウンス切替、通話録音容量逼迫時は過去アーカイブクラウド退避を実行する』。",
            "ACDテレフォニーモニタ：現在保留待ち件数が42件に膨れ上がり溢れ呼寸前。IVR制御を選択せよ。",
            "ivr_emergency_sms_all_staff_distribute",
            "ACDテレフォニーモニタ：保留待ち件数はわずか1件で席に十分な余裕あり。IVR制御を選択せよ。",
            "ivr_assign_rookie_operator_priority",
            [
                ("ivr_emergency_sms_all_staff_distribute", "緊急自動着信分配SMS送信"),
                ("ivr_request_supervisor_help", "管理職通話ヘルプ要請"),
                ("ivr_normal_queueing_call", "通常オペレーター待ち呼"),
                ("ivr_assign_rookie_operator_priority", "新人オペレーター優先割当"),
                ("ivr_switch_disaster_shelter_announcement", "災害避難案内自動アナウンス"),
                ("ivr_archive_recording_cloud_save", "通話録音クラウド退避"),
            ],
        ),
        (
            "26",
            "自治体図書館の自動貸出返却返送ブックコンベア規程。規程：『返却ポスト内冊数が300冊以上のときは自動仕分コンベア最高速ピッチ運転、150〜299冊の間は定格搬送仕分、50〜149冊の間は省電力低速仕分、50冊未満のときはコンベア停止アイドリング待機、ICタグ読取不可本検出時はリジェクトBOX排出、コンベア詰まり検知時は非常停止・係員報知を実行する』。",
            "返却ポスト光学センサ：月曜朝の返却集中によりポスト内蔵冊数が410冊を記録。コンベア速度を選択せよ。",
            "library_conveyor_max_pitch_run",
            "返却ポスト光学センサ：開館中につき返却ポスト内は現在15冊のみ。コンベア速度を選択せよ。",
            "library_conveyor_idle_standby_stop",
            [
                ("library_conveyor_max_pitch_run", "自動仕分最高速ピッチ運転"),
                ("library_conveyor_rated_speed_run", "定格搬送仕分運転"),
                ("library_conveyor_low_power_speed", "省電力低速仕分運転"),
                ("library_conveyor_idle_standby_stop", "コンベア停止アイドリング"),
                ("library_conveyor_reject_box_eject", "IC読取不可リジェクト排出"),
                ("library_conveyor_emergency_stop_alarm", "非常停止係員報知"),
            ],
        ),
        (
            "27",
            "複合オフィスビルの雨水再利用中水ろ過システム運用基準。基準：『中水貯水槽水位が満水位（HWL）以上のときは雨水流入自動バイパス放流、中水位（MWL）以上のときは通常ろ過殺菌給水運転、低水位（LWL）未満のときは水道上水緊急自動補給弁開放、原水濁度50度超のときは砂ろ過逆洗シーケンス、残留塩素0.1mg/L未満時は次亜塩素酸注入ポンプ増量、停電時は中水全系安全停止を実行する』。",
            "水槽フロートスイッチ：大雨により中水受水槽がHWL満水に達した。雨水バルブ制御を選択せよ。",
            "greywater_auto_bypass_drain",
            "水槽フロートスイッチ：連日晴天で水位がLWLを下回りトイレ洗浄水枯渇リスク。給水制御を選択せよ。",
            "greywater_open_city_water_makeup_valve",
            [
                ("greywater_auto_bypass_drain", "雨水流入自動バイパス放流"),
                ("greywater_normal_filter_supply_run", "通常ろ過殺菌給水運転"),
                ("greywater_open_city_water_makeup_valve", "水道上水緊急自動補給弁開放"),
                ("greywater_execute_sand_backwash", "原水濁度砂ろ過逆洗"),
                ("greywater_boost_hypochlorite_pump", "次亜塩素酸注入ポンプ増量"),
                ("greywater_power_loss_safe_shutdown", "停電全系安全停止"),
            ],
        ),
        (
            "28",
            "新幹線駅ホーム可動式ホームドア（PSD）挟み込み検知規程。規程：『戸先光学センサが異物挟み込み（厚み10mm以上）を検知したときはドア即時200mm自動再開扉反転、ドア全閉確認信号不一致時は列車出発抑止インターロック発動、手荷物引きずり検知時は車掌非常列車停止スイッチ連動、戸閉力過負荷検知時はモータートルク制限、全ドア正常施錠時は列車出発可信号現示、ホーム非常停止ボタン押下時は全ドア強制全開を実行する』。",
            "ホームドアセンサ：乗客のリュックの紐（厚み15mm）を挟み込み検知。ドア制御を選択せよ。",
            "psd_reopen_reverse_200mm",
            "ホームドア保安装置：全ドアの機械ラッチが完全に閉塞施錠完了。信号制御を選択せよ。",
            "psd_display_departure_clear_signal",
            [
                ("psd_reopen_reverse_200mm", "ドア即時200mm自動再開扉"),
                ("psd_inhibit_train_departure_interlock", "列車出発抑止インターロック"),
                ("psd_conductor_emergency_train_stop", "車掌非常停止スイッチ連動"),
                ("psd_limit_motor_torque_overload", "モータートルク制限"),
                ("psd_display_departure_clear_signal", "全施錠列車出発可信号現示"),
                ("psd_force_open_all_emergency_button", "非常ボタン全ドア強制全開"),
            ],
        ),
        (
            "29",
            "大規模多目的スタジアムの芝生育成用可動式照明昇降規程。規程：『グラウンド日照積算量が基準値未満のときは育成LED照明を最下段（地上2m）降下照射、日照十分かつイベント開催時は照明を天井トラス格納位置（地上40m）へ巻き上げ、芝生散水スプリンクラー稼働時は照明を地上10mへ退避上昇、強風警報時は中間ロックピン固定、照明電源過熱時はファン空冷待機、地震発生時は自動昇降停止・全ワイヤーロックを実行する』。",
            "アグロウェザーモニタ：長雨により芝生の日照積算量が基準値の30%と極端に不足。照明位置を選択せよ。",
            "stadium_lower_lights_2m_irradiate",
            "イベント進行指示：今夜サッカー国際試合を開催。芝生照明制御を選択せよ。",
            "stadium_hoist_lights_roof_truss_40m",
            [
                ("stadium_lower_lights_2m_irradiate", "最下段2m降下照射"),
                ("stadium_hoist_lights_roof_truss_40m", "天井トラス40m格納巻き上げ"),
                ("stadium_raise_lights_10m_sprinkler", "地上10m退避上昇"),
                ("stadium_lock_intermediate_pins_wind", "中間ロックピン強風固定"),
                ("stadium_fan_cooling_standby_overheat", "電源過熱ファン空冷待機"),
                ("stadium_seismic_emergency_stop_wire_lock", "地震昇降停止ワイヤーロック"),
            ],
        ),
        (
            "30",
            "スマート水道メーター広域自動検針（AMI）無線通信規程。規程：『集中検針パケット受信成功率が98%以上のときは定時時間帯別検針データ収集完了、85〜97%の間はマルチホップ中継ルート再探索、70〜84%の間は無線送信電力を最大ブースト、70%未満の電波障害時は近接ハンディ検針員出動アラート、水道漏水アラーム検知時は即時警報メール自動発信、電池残量警告時はメーター交換作業指示書自動発行を実行する』。",
            "AMIネットワーク管理画面：地域集中ゲートウェイの受信成功率は99.2%を記録。通信処理を選択せよ。",
            "ami_complete_hourly_metering_collection",
            "AMIネットワーク管理画面：宅地配管継続流動フラグにより24時間連続通水（漏水兆候）を検知。通信処理を選択せよ。",
            "ami_dispatch_instant_leak_alert_email",
            [
                ("ami_complete_hourly_metering_collection", "定時検針データ収集完了"),
                ("ami_reroute_multihop_mesh", "マルチホップルート再探索"),
                ("ami_boost_wireless_tx_power_max", "無線送信電力最大ブースト"),
                ("ami_alert_handy_reader_dispatch", "近接ハンディ検針員出動"),
                ("ami_dispatch_instant_leak_alert_email", "即時漏水警報メール発信"),
                ("ami_generate_battery_swap_workorder", "電池警告メーター交換指示"),
            ],
        ),
    ]

    for pid, ctx, q1, t1, q2, t2, chs in k6_defs:
        choices = [{"id": cid, "text": ctxt} for cid, ctxt in chs]
        pairs.append({
            "pair_id": f"rc3_blind5_gen_{pid}",
            "family": "general_choice",
            "k": 6,
            "case_1": {
                "id": f"rc3_blind5_gen_{pid}_s1",
                "group_id": f"rc3_blind5_gen_{pid}",
                "family": "general_choice",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1},
            },
            "case_2": {
                "id": f"rc3_blind5_gen_{pid}_s2",
                "group_id": f"rc3_blind5_gen_{pid}",
                "family": "general_choice",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2},
            },
        })

    return pairs
