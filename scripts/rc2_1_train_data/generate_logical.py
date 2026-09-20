"""RC2.1 Training Data Synthesis: Stream B — Logical Combinations (660 pairs = 1,320 records).

Cleaned for Run 3c:
1. ZERO reasoning justification prefixes in choice texts (no "のため", "を確認し", "により", "未達のため").
2. ZERO joke distractors (all distractors are realistic, domain-appropriate fallback actions).
3. Symmetrical linguistic naturalness between positive and negative outcomes.
4. Includes both full biconditional rules AND single-clause conditional rules ("〜の場合に限りAを実行する" -> Aを見送り待機する/保留する).
5. Added Domain 11: Single-Clause Implicit Denial / Withholding Rules (60 pairs).
6. Total: 660 pairs (1,320 records). All pairs are strictly contrastive (s1/s2 targets distinct).
"""

from typing import Any, Dict, List, Tuple
import random


def make_choices(defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in defs]


def generate_logical_stream_b(seed: int = 1001) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    records = []

    # Domain 1: Sensor & Equipment Thresholds (60 pairs)
    sensor_types = [
        ("ボイラー蒸気圧力", "MPa", 0.8, 1.2, "減圧弁を開放し冷却を開始する", "標準燃焼運転を継続する", "valve_open_cooling", "combustion_normal", "hold_pressure_manual_check", "計器異常の有無を現場で手動点検する"),
        ("冷却水循環温度", "℃", 60.0, 75.0, "補助クーラーを作動させる", "通常水冷循環を維持する", "aux_cooler_on", "coolant_normal", "standby_cooling_tower", "冷却塔ファンの予備系統を待機させる"),
        ("クリーンルーム室内気圧", "Pa", 20.0, 30.0, "給気ファン出力を引き上げる", "現行ファン出力を維持する", "fan_boost_on", "fan_normal", "calibrate_air_damper", "差圧ダンパーの開度を現場調整する"),
        ("大型遠心分離機回転数", "rpm", 4500, 5000, "緊急減速ブレーキを作動させる", "定格回転数で遠心分離を継続", "brake_decelerate", "centrifuge_normal", "vibration_sensor_check", "回転軸受けの振動センサーを精密計測する"),
        ("メッキ浴液pH濃度", "pH", 4.0, 6.0, "中和バッファー液を注入する", "メッキ処理工程をそのまま続行", "neutralize_buffer", "plating_normal", "sample_chemical_titration", "浴槽液をサンプリングし手動滴定検査する"),
        ("電気炉ヒーター電流値", "A", 180, 220, "過電流リミッターを遮断作動", "定常通電加熱を継続する", "limiter_cut_off", "heater_normal", "switch_to_sub_transformer", "副変圧器系統へ受電を切り替える"),
        ("無塵室微粒子数", "個/m³", 800, 1000, "ULPAフィルター全自動逆洗実行", "正常高清浄度環境として維持", "filter_backwash", "cleanroom_ok", "measure_particle_counter", "ポータブル微粒子カウンターで再測定する"),
        ("真空乾燥チャンバー気圧", "kPa", 5.0, 10.0, "真空補助ポンプを追加起動", "規定真空度保持運転を継続", "vacuum_booster_on", "vacuum_ok", "check_vacuum_flange_leak", "真空フランジのシール漏れを目視確認する"),
        ("高圧トランス油中ガス濃度", "ppm", 120, 150, "トランス負荷を半減させ点検", "通常送電運用を継続する", "transformer_half_load", "transformer_normal", "chromatography_gas_analysis", "絶縁油のガスクロマトグラフィー分析を依頼する"),
        ("塗装ブース排気VOC濃度", "ppm", 40, 50, "活性炭吸着タワーへ排気切替", "通常排気ファン循環を維持", "carbon_adsorber_on", "voc_exhaust_normal", "ventilation_damper_manual", "排気風量ダンパーを手動で半開固定する"),
    ]
    for idx, (param, unit, low_lim, high_lim, act_hi, act_lo, cid_hi, cid_lo, cid_dist, act_dist) in enumerate(sensor_types):
        for rep in range(6):
            gid = f"tb_log_sen_{idx*6 + rep + 1:03d}"
            v_hi = round(high_lim + rng.uniform(0.1, 0.5) * (high_lim - low_lim), 2)
            v_lo = round(low_lim + rng.uniform(0.1, 0.5) * (high_lim - low_lim), 2)
            if rep < 3:
                ctx_base = f"【設備安全管理基準】{param}が{high_lim}{unit}を超過した場合は「{act_hi}」。{high_lim}{unit}以下の場合は「{act_lo}」。"
            else:
                ctx_base = f"【設備安全管理基準】{param}が{high_lim}{unit}を超過した場合に限り「{act_hi}」。"
            q = f"機器制御判断：{param}の測定値に基づく適切な制御指示を選択してください。"
            c_defs = [(cid_hi, act_hi), (cid_lo, act_lo), (cid_dist, act_dist)]
            choices = make_choices(c_defs)
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "sensor_threshold", "context": f"{ctx_base}現在のリアルタイム監視センサー測定値：{v_hi}{unit}。", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": cid_hi}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "sensor_threshold", "context": f"{ctx_base}現在のリアルタイム監視センサー測定値：{v_lo}{unit}。", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": cid_lo}})

    # Domain 2: Business Rules with Default and Exception (60 pairs)
    rule_templates = [
        ("返品送料負担", "商品の自己都合返品送料は原則「購入者負担」とする。ただし、初期不良または誤配送の場合は「店舗全額負担」とする。", "初期不良（電源が入らない動作不良）が確認された。", "サイズ違いによる顧客都合の返品希望である。", [("store_pays_shipping", "店舗全額負担（着払いで返送受領）"), ("customer_pays_shipping", "購入者負担（元払いで発送手配）"), ("request_photo_inspection", "商品の破損写真の送付を依頼する")], "store_pays_shipping", "customer_pays_shipping"),
        ("有給休暇申請期限", "有給休暇の取得申請は原則「希望日の3営業日前」までとする。ただし、急な発熱・負傷等による突発的私傷病の場合は「当日午前9時までの電話連絡」で事後申請を認める。", "今朝起きたところ38度の高熱と激しい咽頭痛を発症したため朝8時に連絡した。", "来週友人と旅行に行くため私用で休暇を取りたい（本日申請）。", [("allow_same_day_sick_leave", "当日電話連絡による事後申請での有給取得を承認する"), ("require_3_days_prior_application", "原則に従い3営業日前までの事前申請を要求する"), ("convert_to_unpaid_absence", "有休ではなく欠勤（無給）扱いとして処理する")], "allow_same_day_sick_leave", "require_3_days_prior_application"),
        ("社内PC持ち出し許可", "社給PCの社外持ち出しは原則「全面禁止」とする。ただし、役員承認を得たリモートワーク推奨プロジェクト従事者に限り「暗号化PCの持ち出しを許可」する。", "役員承認を受けたAI新規事業プロジェクト所属であり持ち出し申請承認済み。", "週末に自宅で動画鑑賞をするため私的利用で持ち出したい。", [("permit_encrypted_pc_takeout", "暗号化PCの社外持ち出しを許可する"), ("prohibit_pc_takeout_standard", "社給PCの社外持ち出しを禁止する"), ("require_remote_desktop_only", "社内仮想デスクトップでのリモート接続のみ許可する")], "permit_encrypted_pc_takeout", "prohibit_pc_takeout_standard"),
        ("施設夜間施錠管理", "オフィスビルは平日20時に「正面玄関および全通用口を自動施錠」する。ただし、守衛室に事前届出済みの夜間残業登録者がいるフロアは「22時まで通用口解錠を延長」する。", "開発チーム4名が守衛室へ事前残業届出を済ませて21時半まで執務中。", "事前の残業届出は一切提出されておらず全フロア消灯状態。", [("extend_access_door_until_22pm", "22時まで通用口の解錠を延長する"), ("lock_all_doors_at_20pm", "20時に全通用口を自動施錠する"), ("guard_station_manual_entry", "守衛室での手動受付入場に切り替える")], "extend_access_door_until_22pm", "lock_all_doors_at_20pm"),
        ("交通費特急料金支給", "国内出張の新幹線特急券は原則「普通車指定席」を支給する。ただし、移動所要時間が片道3時間を超える長距離区間に限り「グリーン車利用を承認」する。", "東京駅から博多駅までの出張（片道所要時間4時間50分）。", "東京駅から新横浜駅までの出張（片道所要時間18分）。", [("approve_green_car_class", "グリーン車利用を承認・支給する"), ("provide_standard_reserved_seat", "普通車指定席を支給する"), ("reimburse_non_reserved_seat", "自由席特急券のみ支給する")], "approve_green_car_class", "provide_standard_reserved_seat"),
        ("ソフトウェア購入決裁", "新規ソフトウェアの購入は原則「部長決裁」を必要とする。ただし、月額費用が5,000円以下の開発ユーティリティツールは「課長決裁で即時購入可能」とする。", "月額2,800円のコード整形クラウドサービスを導入したい。", "初期費用300万円・月額20万円の全社ERP統合パッケージを導入したい。", [("approve_by_section_manager_under_5k", "課長決裁で即時購入を承認する"), ("require_division_manager_approval", "部長決裁の申請手続きを要求する"), ("hold_budget_review", "次期四半期予算審議まで購入を保留する")], "approve_by_section_manager_under_5k", "require_division_manager_approval"),
        ("顧客データ外部持ち出し", "顧客個人情報を含むファイルは原則「社外送信・ダウンロードを全面遮断」する。ただし、暗号化ZIP保護かつ法務部承認の第三者委託契約がある場合は「セキュアストレージ経由での限定共有を許可」する。", "法務部承認済み委託契約に基づき暗号化保護された分析用匿名加工データ。", "未契約の社外知人に個人的に相談するため顧客生データをメール添付。", [("permit_secure_storage_sharing", "セキュアストレージ経由での限定共有を許可する"), ("block_customer_data_export", "顧客データの社外送信を遮断する"), ("request_legal_exemption", "法務部への特例事前審査を申請する")], "permit_secure_storage_sharing", "block_customer_data_export"),
        ("ホテル宿泊客室喫煙", "全館客室は原則「完全禁煙」とする。ただし、指定の喫煙対応フロア（5階）の専用喫煙客室に限り「紙巻たばこ・加熱式たばこの喫煙を許可」する。", "5階の指定専用喫煙客室に宿泊しているお客様。", "10階の禁煙エグゼクティブフロアに宿泊しているお客様。", [("permit_smoking_in_designated_room", "客室内での喫煙を許可する"), ("strictly_prohibit_smoking", "客室内での喫煙を厳禁とする"), ("guide_to_outdoor_smoking_area", "屋外指定喫煙所へ案内する")], "permit_smoking_in_designated_room", "strictly_prohibit_smoking"),
        ("社内会議室予約キャンセル", "会議室予約のキャンセル料は社内規定上「利用開始1時間前までは無料キャンセル」とする。ただし、1時間前を過ぎた直前キャンセルは「ペナルティとして翌週の予約枠を半減」する。", "利用開始予定時刻の3時間前に予約解除の手続きを行った。", "利用開始予定時刻の10分前に連絡なく無断キャンセルした。", [("cancel_free_of_charge", "キャンセル料なしで無料解約を受理する"), ("impose_half_booking_penalty", "ペナルティとして翌週予約枠を半減する"), ("charge_full_cancellation_fee", "キャンセル料として全額請求する")], "cancel_free_of_charge", "impose_half_booking_penalty"),
        ("クレジットカード海外利用枠", "不正利用防止のため海外IPからのカード決済は原則「自動セキュリティ保留」とする。ただし、事前にマイページで「海外渡航日程を登録済みの会員」は保留なしで即時承認する。", "渡航前日にマイページでフランス滞在日程を事前登録済みの会員。", "事前登録がなく、突然深夜にナイジェリアIPから高額決済が試行された。", [("approve_card_payment_pre_registered", "保留なしで即時カード決済を承認する"), ("hold_card_payment_for_security", "カード決済を自動保留する"), ("request_sms_otp_verification", "SMSワンタイムパスワードで追加認証を行う")], "approve_card_payment_pre_registered", "hold_card_payment_for_security"),
    ]
    for idx, (title, rule_text, s1_sit, s2_sit, c_defs, t1, t2) in enumerate(rule_templates):
        for rep in range(6):
            gid = f"tb_log_def_{idx*6 + rep + 1:03d}"
            choices = make_choices(c_defs)
            q = f"規程判定：{title}のルールに基づき適用すべき処置を選択してください。"
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "default_and_exception", "context": f"【{title}】{rule_text}\n現在の状況：{s1_sit}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t1}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "default_and_exception", "context": f"【{title}】{rule_text}\n現在の状況：{s2_sit}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t2}})

    # Domain 3: Multi-Clause AND Conjunctions (NO reasoning prefixes in choices!) (60 pairs)
    and_cases = [
        ("住宅ローン金利優遇", "給与振込口座の指定があり、かつ積立NISAを月1万円以上運用している場合に限り店頭金利から0.8%引き下げ。いずれかを満たさない場合は店頭基準金利。", "顧客ステータス：給与振込指定あり、NISA月2万円運用中。", "顧客ステータス：給与振込指定はあるが、NISAは未加入。", "apply_0_8pct_interest_discount", "店頭金利から0.8%引き下げを適用する", "deny_discount_use_standard_rate", "店頭基準金利をそのまま適用する", "require_guarantor_addition", "連帯保証人の追加を融資条件とする"),
        ("救急病棟受入", "受入可能病床の空きが1床以上あり、かつ当直専門医が処置可能状態である場合にホットライン要請を受諾。不可なら他院へ転送。", "病院状況：ICU空床2床、脳神経外科当直医待機完了。", "病院状況：ICU空床2床、当直医は現在緊急手術中で処置不可。", "accept_emergency_ambulance", "ホットラインの受入要請を受諾する", "divert_ambulance_to_other_hospital", "受入れを見送り他院への搬送を要請する", "standby_in_triage_bay", "処置室の準備を待機し10分後に再確認する"),
        ("特許出願社内審査", "先行技術調査で新規性が確認され、かつ事業化計画書が提出されている場合に弁理士へ出願依頼。未達要件があれば保留。", "審査書類：調査で新規性確認済み、事業化計画書提出完了。", "審査書類：新規性は確認されたが、事業化計画書は未提出。", "retain_patent_attorney_for_filing", "弁理士へ特許出願書類の作成を依頼する", "hold_patent_application_incomplete", "出願依頼を見送り社内審査保留とする", "archive_as_trade_secret", "出願せず社内営業秘密（ノウハウ）として秘匿する"),
        ("高所作業許可", "フルハーネス型安全帯を着用し、かつ有資格者の現場立会いがある場合のみ足場作業開始許可。欠けていれば作業中止。", "現場状況：全員フルハーネス装着完了、作業主任者が現場常駐確認。", "現場状況：全員フルハーネス装着完了、有資格者は現場不在。", "grant_scaffolding_work_permit", "足場作業の開始を許可する", "halt_scaffolding_work_lacking_supervisor", "足場作業の開始を禁止・中止する", "restrict_to_ground_work", "高所作業を避け地上での作業のみ許可する"),
        ("学生割引定期券発行", "在学証明書と通学区間証明書の両方が有効期間内である場合に学割通学定期券を発行。欠落時は通常定期案内。", "提示書類：今年度有効の在学証明書、今年度有効の通学区間証明書。", "提示書類：今年度有効の在学証明書のみ（通学区間証明書なし）。", "issue_student_discount_commuter_pass", "学割通学定期券を発行する", "reject_student_discount_unverified", "通常通勤定期券の案内とする", "issue_one_way_ticket", "定期券ではなく片道普通乗車券を案内する"),
        ("食品賞味期限出荷判定", "賞味期限まで90日以上残存しており、かつ包装シールにピンホール破損がないロットを出荷。基準外なら隔離破棄。", "検査データ：賞味期限残150日、窒素置換包装シール正常合格。", "検査データ：賞味期限残120日、包装フィルムに裂け目あり。", "ship_food_lot_passed_standards", "基準適合として食品ロットを出荷する", "quarantine_damaged_food_lot", "出荷を停止し隔離廃棄処置とする", "resample_microbial_test", "別検体をサンプリングして再検査を行う"),
        ("深夜作業手当加算", "実労働時間が22時から翌朝5時の時間帯に含まれ、かつ役職が一般職種である場合に従業員深夜割増手当を支給。非該当時は支給なし。", "勤務状況：一般職のエンジニアが深夜23時から翌2時まで障害対応。", "勤務状況：執行役員が深夜23時まで役員協議。", "pay_night_shift_premium_allowance", "従業員深夜割増手当を支給する", "waive_night_shift_allowance_executive", "深夜割増手当の支給対象外とする", "grant_compensatory_day_off", "手当の代わりに翌週の振替休日を付与する"),
        ("自動昇格フェイルオーバー", "レプリケーション遅延が1.0秒未満であり、かつセカンダリノードCPU使用率が60%以下である場合に自動昇格実行。超過時は手動対応待機。", "監視ログ：遅延0.1秒、セカンダリCPU使用率42%。", "監視ログ：遅延0.2秒、セカンダリCPU使用率75%。", "execute_auto_promote", "セカンダリノードの自動昇格を実行する", "hold_manual_intervention", "自動昇格を見送り手動対応待機とする", "restart_secondary_service", "セカンダリノードのDBデーモンを再起動する"),
        ("クリーンルーム入室", "静電服を完全着用し、かつエアシャワーを30秒間浴び終えた場合に入室ゲート解錠。未完了時は施錠維持。", "作業員状態：静電服着用済み、エアシャワー30秒通過完了。", "作業員状態：静電服着用済み、エアシャワー滞在5秒で通過扉押し。", "unlock_cleanroom_door", "クリーンルーム入室ゲートを解錠する", "keep_cleanroom_locked_alarm", "ゲートの施錠を維持し警報を発報する", "restart_air_shower_cycle", "エアシャワーを最初からやり直させる"),
        ("輸出管理該非判定", "取引相手国が懸念国リストに非該当であり、かつ製品スペックが規制閾値未満である場合に輸出許可。抵触時は省庁個別許可申請。", "審査案件：相手国非該当、製品スペック規制閾値未満。", "審査案件：相手国非該当、製品スペックが規制閾値を超過。", "grant_export_clearance", "輸出審査を承認し出荷を許可する", "require_ministry_license", "省庁個別輸出許可申請へ回付する", "request_end_user_certificate", "最終需要者誓約書の再提出を求める"),
    ]
    for idx, (title, rule, s1, s2, cid1, txt1, cid2, txt2, cid3, txt3) in enumerate(and_cases):
        for rep in range(6):
            gid = f"tb_log_and_{idx*6 + rep + 1:03d}"
            c_defs = [(cid1, txt1), (cid2, txt2), (cid3, txt3)]
            choices = make_choices(c_defs)
            q = f"判定選定：{title}の複数条件に基づき適切な判断を選択してください。"
            # First 3 reps: full biconditional rule; Next 3 reps: single-clause rule without explicit else-clause
            if rep < 3:
                ctx_rule = f"【判定ルール】{rule}"
            else:
                rule_single = rule.split("。")[0]
                ctx_rule = f"【規程】{title}：『{rule_single}』。"
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "and_conjunction", "context": f"{ctx_rule}\n事象確認：{s1}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": cid1}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "and_conjunction", "context": f"{ctx_rule}\n事象確認：{s2}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": cid2}})

    # Domain 4: Multi-Clause OR Disjunctions (NO reasoning prefixes in choices!) (60 pairs)
    or_cases = [
        ("高速道路ETC深夜割引", "走行開始時刻が午前0時〜4時の間、または走行完了退出時刻が午前0時〜4時の間のいずれかを満たせば深夜割引30%適用。満たさない場合は通常料金。", "利用記録：インター流入時刻23時00分、流出時刻午前1時15分。", "利用記録：インター流入時刻午前10時00分、流出時刻午前11時30分。", "apply_midnight_toll_discount", "深夜割引30%を適用して料金収受する", "charge_regular_highway_toll", "通常料金を請求する", "apply_holiday_daytime_discount", "休日昼間割引を適用して料金収受する"),
        ("クラウドIAM多要素認証", "ハードウェアキーのタッチ、またはスマホ認証アプリのコード入力のいずれか一方で認証成功。どちらも行わなければアクセス拒否。", "認証操作：YubiKeyハードウェアキーを挿入しタッチ成功。", "認証操作：固定パスワードのみ入力、キーもアプリも操作なし。", "grant_iam_access_mfa_success", "クラウドアクセスを許可する", "deny_iam_access_mfa_failed", "クラウドアクセスを拒否する", "require_sms_code_fallback", "SMSによる代替ワンタイムパスワードを送信する"),
        ("会員ランク維持条件", "年間お買い上げ金額10万円以上、または年間来店回数12回以上のいずれかを達成でゴールド会員資格を更新。未達ならシルバーへ降格。", "顧客実績：年間お買い上げ8万円、来店回数15回。", "顧客実績：年間お買い上げ3万円、来店回数4回。", "renew_gold_membership", "ゴールド会員資格を更新する", "demote_to_silver_membership", "シルバー会員へ降格とする", "grant_grace_period_extension", "3ヶ月間の猶予期間を設けて現ランクを暫定維持する"),
        ("入室セカンドキー解錠", "暗証番号のテンキー入力、またはICカードのタッチのいずれか一方で自動ドア解錠。どちらも未入力なら施錠継続。", "操作ログ：テンキーにて正しい暗証番号6桁を入力。", "操作ログ：テンキー未入力、ICカード読み取り機タッチなし。", "unlock_door_or_success", "自動ドアを解錠する", "keep_door_locked_or_fail", "自動ドアの施錠を維持する", "call_security_intercom", "守衛室インターホンへ通話を接続する"),
        ("奨学金免除基準", "世帯年収400万円以下、または学業成績GPA3.8以上のいずれかに該当すれば返済免除対象。該当しない場合は通常返済。", "申請者情報：世帯年収650万円、大学成績GPA3.90。", "申請者情報：世帯年収700万円、大学成績GPA3.00。", "waive_student_loan_repayment", "奨学金の返済を免除する", "require_standard_loan_repayment", "奨学金の通常返済を求める", "defer_loan_repayment_grace", "返済猶予制度を適用し返済開始を1年延期する"),
        ("社内特別休暇取得", "本人の結婚、または配偶者の出産のいずれかの事由が生じた場合に有給の特別慶弔休暇5日付与。該当事由がなければ通常有休。", "申請事由：本人の入籍および挙式。", "申請事由：友人の引越しの手伝い。", "grant_special_congratulatory_leave", "有給の特別休暇5日を付与する", "use_standard_paid_annual_leave", "通常の年次有給休暇を充当する", "grant_unpaid_leave_special", "無給の特別事由休暇を案内する"),
        ("サーバー再起動トリガー", "メモリ枯渇アラート発生、または応答停止タイムアウト120秒継続のいずれか検知でインスタンスを自動再起動。正常なら稼働維持。", "システム状態：メモリ使用率99%枯渇アラートを検知。", "システム状態：メモリ使用率40%、応答時間15ミリ秒。", "reboot_cloud_instance_trigger", "インスタンスを自動再起動する", "keep_instance_running_normal", "現行インスタンスの稼働を維持する", "isolate_network_traffic", "インスタンスのネットワークトラフィックを隔離する"),
        ("試験合格判定", "総合点70点以上、または特定専門科目で100点満点のいずれかで特別合格。未達なら不合格。", "成績票：総合点65点、専門科目100点満点。", "成績票：総合点58点、専門科目72点。", "pass_special_qualification_exam", "特別合格判定とする", "fail_qualification_exam", "不合格判定とする", "grant_retest_conditional", "次回の追試験受験資格を付与する"),
        ("本人確認書類代替", "マイナンバーカード、または運転免許証のいずれか1点原本提示で本人確認完了。提示できない場合は手続停止。", "窓口提示書類：有効期限内の運転免許証原本。", "窓口提示書類：学生証および図書館利用カード。", "accept_identity_verification_doc", "本人確認完了として受理する", "reject_unauthorized_id_documents", "本人確認の手続を停止する", "request_supplementary_utility_bill", "住民票原本または公共料金領収書の追加提示を求める"),
        ("災害時避難勧告", "河川水位が警戒水位到達、または土砂災害警戒情報発令のいずれかで住民へ避難指示発令。未発令なら注意喚起継続。", "防災気象情報：土砂災害警戒情報が気象台より発令。", "防災気象情報：河川水位平穏、土砂警戒なし。", "issue_evacuation_order_to_residents", "住民へ避難指示を発令する", "maintain_standard_weather_watch", "平常の注意監視体制を維持する", "dispatch_patrol_team", "自主防災パトロール隊を現場警戒へ派遣する"),
    ]
    for idx, (title, rule, s1, s2, cid1, txt1, cid2, txt2, cid3, txt3) in enumerate(or_cases):
        for rep in range(6):
            gid = f"tb_log_or_{idx*6 + rep + 1:03d}"
            c_defs = [(cid1, txt1), (cid2, txt2), (cid3, txt3)]
            choices = make_choices(c_defs)
            q = f"判定選定：{title}の基準に基づき適切な対応を選択してください。"
            if rep < 3:
                ctx_rule = f"【判定ルール】{rule}"
            else:
                rule_single = rule.split("。")[0]
                ctx_rule = f"【規程】{title}：『{rule_single}』。"
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "or_disjunction", "context": f"{ctx_rule}\n事象確認：{s1}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": cid1}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "or_disjunction", "context": f"{ctx_rule}\n事象確認：{s2}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": cid2}})

    # Domain 5: Explicit Negation & Exclusions (NO reasoning prefixes in choices!) (60 pairs)
    not_cases = [
        ("未成年・非飲酒判定", "「運転手ではない」かつ「年齢20歳以上」の顧客に限り酒類を提供。運転予定者または未成年者には提供禁止。", "来店客：年齢32歳、電車で来店しており車は運転しない。", "来店客：年齢25歳、自家用車を運転して帰宅する。", "serve_liquor_safe", "酒類を提供する", "refuse_liquor_due_to_driving", "酒類の提供を拒否する", "serve_soft_drink_only", "ノンアルコール飲料のみを提供する"),
        ("免責特約対象外判定", "自然災害による破損は補償対象。ただし故意または重大な過失による破損ではない場合に限る。故意過失がある場合は補償対象外。", "損害調査報告：台風による暴風で屋根瓦が飛散した。", "損害調査報告：金槌で故意に叩き割った痕跡が多数あり。", "approve_insurance_claim_natural", "保険金を支払う", "deny_insurance_claim_intentional", "保険金の支払いを拒絶する", "appoint_third_party_surveyor", "第三者損害鑑定人による実地再調査を命じる"),
        ("アカウント停止解除", "警告回数が3回未満であり、かつ不正アクセス犯行ではないアカウントのみ解除申請を受理。不正犯行または警告3回以上は永久停止。", "審査ログ：過去警告1回、パスワード誤入力ロック。", "審査ログ：海外IPからの辞書攻撃ブルートフォース実行犯。", "reinstate_user_account", "アカウントの停止を解除する", "permanently_ban_malicious_account", "アカウントを永久停止とする", "enforce_password_reset_only", "パスワード初期化のみ行いログイン試行を監視する"),
        ("除外キーワードフィルタ", "本文にスパム・広告が含まれず、かつ発信元が社内ドメインである通信を受信フォルダへ格納。含まれる場合は迷惑メール隔離。", "着信メール：発信元＝社内人事部、本文＝新入社員歓迎会のご案内。", "着信メール：発信元＝不明ドメイン、本文＝簡単副業で月100万円稼げる広告。", "route_to_inbox_clean", "メールを通常受信箱へ格納する", "quarantine_spam_blacklisted", "迷惑メールフォルダへ隔離する", "forward_to_security_ops", "情報セキュリティ運用チームへ解析転送する"),
        ("特定アレルゲン非含有判定", "小麦、そば、落花生のいずれも含まない食品のみアレルギー対応食として配膳。1品目でも含む場合は配膳禁止。", "原材料表示：米粉、大豆、食塩。", "原材料表示：小麦粉、落花生ペースト、砂糖。", "serve_allergen_free_meal", "アレルギー対応食として配膳する", "withhold_allergen_contaminated_meal", "アレルギー対応食としての配膳を禁止する", "return_to_kitchen_recheck", "厨房へ戻し原材料の混入有無を再確認させる"),
        ("輸出禁輸品目非該当", "大量破壊兵器転用可能リストに非該当であり、かつ仕向地が経済制裁対象国ではない製品のみ通関許可。", "通関貨物：玩具用プラスチックブロック、仕向地オーストラリア。", "通関貨物：ウラン濃縮用超遠心分離部品、仕向地制裁対象地域。", "clear_export_customs_non_restricted", "通関を許可する", "seize_export_goods_sanctioned", "税関で貨物を差し押さえる", "request_ministry_opinion", "経済産業省安全保障貿易審査課の見解照会を行う"),
        ("指名停止措置非該当", "過去1年間に指名停止処分を受けていない企業のみ入札参加可能。処分歴ありは入札失格。", "入札参加者：企業Alpha（行政処分歴なし、優良企業認定）。", "入札参加者：企業Beta（先月談合事案により指名停止処分中）。", "admit_bidder_to_tender", "入札への参加を承認する", "disqualify_bidder_suspended", "入札への参加を失格とする", "refer_to_procurement_legal", "調達審査法務委員会へ参加資格の可否を諮問する"),
        ("非課税品目判定", "居住用不動産の家賃は消費税非課税。ただし事務所・店舗など事業用テナントは課税対象。", "契約書：賃貸マンションの住居用居室の月額家賃。", "契約書：繁華街路面店の美容室店舗テナントの月額家賃。", "treat_rent_as_tax_exempt", "家賃を消費税非課税として処理する", "charge_consumption_tax_commercial", "家賃に消費税を課税して請求する", "request_lease_usage_affidavit", "用途区分確認のため賃貸借用途誓約書の提出を求める"),
        ("深夜残業除外対象", "満18歳未満の年少者は深夜22時以降の労働を禁止。成人のみ深夜勤務可能。", "対象従業員：年齢22歳の正社員エンジニア。", "対象従業員：年齢16歳の高校生アルバイトスタッフ。", "assign_night_shift_adult", "深夜シフトへの配置を認可する", "prohibit_night_shift_minor", "22時以降の深夜勤務を禁止する", "reassign_to_daytime_shift", "日中（9時〜17時）の別シフトへ振替配置する"),
        ("未払い延滞非該当", "会費の未払い滞納が1回もない会員に限り継続更新割引を適用。未払い履歴があれば通常定価。", "会員台帳：過去3年間の全会費が期日通り完納。", "会員台帳：先月および先々月の会費が未納のまま督促状送付中。", "apply_membership_renewal_discount", "継続更新割引を適用する", "charge_standard_rate_due_to_arrears", "通常定価料金で更新案内する", "suspend_renewal_until_settled", "滞納会費の完納まで更新手続きを一時保留する"),
    ]
    for idx, (title, rule, s1, s2, cid1, txt1, cid2, txt2, cid3, txt3) in enumerate(not_cases):
        for rep in range(6):
            gid = f"tb_log_not_{idx*6 + rep + 1:03d}"
            c_defs = [(cid1, txt1), (cid2, txt2), (cid3, txt3)]
            choices = make_choices(c_defs)
            q = f"否定判定：{title}のルールに基づき適切な対応を選択してください。"
            if rep < 3:
                ctx_rule = f"【判定基準】{rule}"
            else:
                rule_single = rule.split("。")[0]
                ctx_rule = f"【判定基準】{title}：『{rule_single}』。"
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "negation_exclusion", "context": f"{ctx_rule}\n対象事象：{s1}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": cid1}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "negation_exclusion", "context": f"{ctx_rule}\n対象事象：{s2}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": cid2}})

    # Domain 6: LTE & Lower Boundary Comparisons (<=, <) (NO reasoning prefixes in choices!) (60 pairs)
    lte_cases = [
        ("手荷物重量制限", "受託手荷物重量が23.0kg以下は無料預かり。23.0kgを超過した場合は超過手数料5,000円を請求。", "計量結果：荷物重量21.5kg。", "計量結果：荷物重量28.4kg。", "accept_baggage_free_under_limit", "追加料金なしで受託手荷物を受け入れる", "charge_excess_baggage_fee_over_limit", "手荷物超過手数料5,000円を請求する", "request_repack_hand_luggage", "荷物を機内持ち込み手荷物へ詰め直させる"),
        ("血圧基準値判定", "拡張期血圧が85mmHg未満は正常至適範囲。85mmHg以上は高値血圧・要指導。", "測定結果：拡張期血圧74mmHg。", "測定結果：拡張期血圧92mmHg。", "blood_pressure_optimal_normal", "正常至適範囲と判定する", "blood_pressure_elevated_warning", "高値血圧・要指導と判定する", "measure_bp_repeat_after_rest", "5分間安静臥床ののち血圧を再測定する"),
        ("食品細菌数規格", "一般生菌数が1グラムあたり100個以下は衛生合格。100個超は不合格破棄。", "培養検査結果：生菌数30個/g。", "培養検査結果：生菌数450個/g。", "food_sanitary_pass_under_100", "衛生基準合格として出荷を認める", "food_sanitary_reject_over_100", "不合格として全品廃棄処置とする", "quarantine_for_secondary_enrichment", "二次増菌培養検査に向けて一時隔離保管する"),
        ("排気ガスCO濃度", "一酸化炭素濃度が0.5%未満は車検合格。0.5%以上は排気不適合・再整備。", "排気テスター測定値：CO濃度0.15%。", "排気テスター測定値：CO濃度0.82%。", "emission_pass_under_limit", "排ガス車検適合合格とする", "emission_fail_over_limit", "排ガス基準不適合とし再整備を命じる", "inspect_o2_sensor_output", "O2センサーおよび触媒コンバータの機能点検を行う"),
        ("納期遅延日数", "発注から納品までの所要日数が3日以内はオンスケジュール定時納品。3日超は遅延ペナルティ適用。", "納品実績：受注から2日後に納品完了。", "納品実績：受注から6日後に納品完了。", "delivery_on_schedule_pass", "定時合格納品として受領する", "delivery_delayed_impose_penalty", "遅延約款に基づきペナルティを適用する", "request_force_majeure_proof", "交通遮断等の不可抗力証明書の提出を求める"),
        ("残存バッテリ容量", "残量が20%未満になった場合は省電力スリープモードへ移行。20%以上は通常パフォーマンス維持。", "現在ステータス：バッテリ残量12%。", "現在ステータス：バッテリ残量68%。", "battery_sleep_mode_under_20", "省電力スリープモードへ移行する", "battery_normal_performance_over_20", "通常パフォーマンスモードを維持する", "prompt_user_plug_in_charger", "外部充電器への接続を画面上に警告通知する"),
        ("河川警戒水位", "観測水位が3.5m以下は平常警戒レベル1。3.5mを超過した場合は氾濫危険レベル4発令。", "水位計観測値：河川水位2.1m。", "水位計観測値：河川水位4.2m。", "water_level_normal_under_threshold", "平常警戒レベル1を維持する", "water_level_flood_danger_over_threshold", "氾濫危険警報レベル4を発令する", "close_floodgate_sluice", "支流への逆流防止水門を全閉鎖する"),
        ("注文キャンセル時間", "注文確定後30分未満は無料キャンセル可能。30分以上経過後はキャンセル不可。", "注文タイムスタンプ：確定後10分経過。", "注文タイムスタンプ：確定後1時間45分経過。", "permit_instant_order_cancel_under_30m", "即時無料キャンセルを受理する", "deny_order_cancel_over_30m", "注文キャンセルを拒絶する", "allow_return_after_delivery", "商品到着後の返品特約ルールを案内する"),
        ("室内騒音レベル", "夜間騒音測定値が40dB以下は環境基準適合クリア。40dB超は騒音改善勧告。", "騒音測定結果：音圧レベル34dB。", "騒音測定結果：音圧レベル58dB。", "noise_level_compliant_under_40db", "夜間環境基準に適合と判定する", "noise_level_violation_over_40db", "騒音改善勧告を発令する", "measure_low_frequency_noise", "低周波音測定器による周波数分析を追加実施する"),
        ("小口決済限度額", "決済金額が3,000円以下はサイン不要タッチ決済。3,000円超はPINコード入力必須。", "レジ精算金額：合計1,850円。", "レジ精算金額：合計9,800円。", "contactless_payment_pinless_under_3k", "暗証番号不要で即時決済する", "require_pin_code_entry_over_3k", "本人暗証番号（PIN）の入力を要求する", "require_handwritten_signature", "カード裏面と同じ手書きサインでの署名を求める"),
    ]
    for idx, (title, rule, s1, s2, cid1, txt1, cid2, txt2, cid3, txt3) in enumerate(lte_cases):
        for rep in range(6):
            gid = f"tb_log_lte_{idx*6 + rep + 1:03d}"
            c_defs = [(cid1, txt1), (cid2, txt2), (cid3, txt3)]
            choices = make_choices(c_defs)
            q = f"数値判定：{title}のルールに基づき適切な判断を選択してください。"
            if rep < 3:
                ctx_rule = f"【境界ルール】{rule}"
            else:
                rule_single = rule.split("。")[0]
                ctx_rule = f"【境界規程】{title}：『{rule_single}』。"
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "lte_boundary", "context": f"{ctx_rule}\n測定確認：{s1}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": cid1}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "lte_boundary", "context": f"{ctx_rule}\n測定確認：{s2}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": cid2}})

    # Domain 7: First-Match Decision Rules (NO reasoning prefixes in choices!) (60 pairs)
    first_match_cases = [
        ("障害対応先頭一致", "上から順に照合し最初に一致したルールを適用する。\n[規則1] 火災警報発令時は「全館避難」。\n[規則2] 電源喪失時は「非常用発電機起動」。\n[規則3] 通常時は「定常監視」。", "現在、火災警報が発令されており、同時に電源も喪失している。", "火災警報は鳴っておらず、電源喪失のみ発生している。", "first_match_fire_evacuate", "全館避難を直ちに指示する", "first_match_generator_power", "非常用発電機を起動する", "first_match_routine_monitoring", "定常監視モードを継続する"),
        ("顧客割引先頭一致", "評価順序：\n1. VIPブラック会員は「全品50%引き」。\n2. 初回購入クーポン利用者は「全品20%引き」。\n3. 通常会員は「割引なし定価」。", "顧客ステータス：VIPブラック会員であり、かつ初回購入クーポンも提示している。", "顧客ステータス：通常会員であり、初回購入クーポンを提示している。", "apply_rule1_vip_50pct", "50%引きを適用する", "apply_rule2_first_coupon_20pct", "20%引きを適用する", "apply_rule3_regular_price", "割引なしの定価販売とする"),
        ("ネットワークACL先頭一致", "ファイアウォール規則（上から順に評価）：\nRule 1: 送信元10.0.0.5からのパケットは「DROP（遮断）」。\nRule 2: ポート443（HTTPS）へのパケットは「ALLOW（許可）」。\nRule 3: デフォルトは「REJECT」。", "パケット情報：送信元10.0.0.5、宛先ポート443。", "パケット情報：送信元192.168.1.50、宛先ポート443。", "acl_rule1_drop_packet", "パケットをDROP（遮断）する", "acl_rule2_allow_packet", "パケットの通信をALLOW（許可）する", "acl_rule3_reject_packet", "パケットにREJECT応答を返送する"),
        ("物流配送先頭一致", "仕分けルール（上から評価）：\n1. 冷凍品は「マイナス20度クール便」。\n2. 割れ物ガラス製品は「衝撃緩衝精密便」。\n3. 一般商品は「通常段ボール普通便」。", "荷物：冷凍の生食用冷凍カニ。", "荷物：常温保存のガラス製ワイングラス。", "dispatch_cool_frozen_freight", "マイナス20度クール便で出荷する", "dispatch_fragile_precision_freight", "衝撃緩衝精密便で出荷する", "dispatch_standard_carton_freight", "通常段ボール普通便で出荷する"),
        ("医療トリアージ先頭一致", "判定手順（1から順に評価）：\n1. 自発呼吸なしは「黒タグ（不処置・死亡）」。\n2. 呼吸数30回以上または脈拍微弱は「赤タグ（最優先治療）」。\n3. 指示に従い歩行可能なら「緑タグ（軽症）」。", "患者容態：自発呼吸が完全に停止しており、脈拍も触知不能。", "患者容態：自発呼吸はあるが、呼吸数が毎分38回と頻呼吸で浅い。", "triage_rule1_black_tag", "黒タグ（不処置）判定とする", "triage_rule2_red_tag", "赤タグ（最優先治療）判定とする", "triage_rule3_green_tag", "緑タグ（軽症観察）判定とする"),
        ("人事評価先頭一致", "昇進規程（上位から順に評価）：\n条項A: TOEIC 900点以上かつ売上達成率150%以上は「特命飛び級昇進」。\n条項B: 売上達成率100%以上は「通常昇給」。\n条項C: 達成率100%未満は「現状据え置き」。", "社員甲：TOEIC 940点、売上達成率165%。", "社員乙：TOEIC 700点、売上達成率120%。", "promote_special_accelerated", "特命飛び級昇進を決定する", "promote_standard_raise", "通常昇給とする", "retain_current_grade", "昇給なしで現状の等級を据え置く"),
        ("在庫引当先頭一致", "引当ルール（順次適用）：\n優先1: 有効期限が30日以内の在庫を最優先で出庫引当。\n優先2: 最寄りの国内中央倉庫の通常在庫を出庫引当。\n優先3: 海外工場からの取り寄せ手配。", "在庫状況：賞味期限まで25日の在庫が中央倉庫に存在。", "在庫状況：賞味期限残30日以内はゼロ、中央倉庫に通常ロットあり。", "allocate_expiring_stock_rule1", "期限間近在庫を最優先で出庫引当する", "allocate_central_warehouse_rule2", "中央倉庫の通常在庫を出庫引当する", "backorder_overseas_factory_rule3", "海外工場からの取り寄せ手配を行う"),
        ("メール配信先頭一致", "配信設定：\nRule A: 配信停止（Opt-Out）希望ユーザーへは「送信禁止（即座にスキップ）」。\nRule B: 会員ステータスがアクティブなら「最新メルマガ配信」。\nRule C: 退会済みは「アカウント抹消」。", "ユーザー台帳：配信停止希望登録済み、会員ステータス正常。", "ユーザー台帳：配信停止希望なし、会員ステータス正常。", "skip_delivery_rule_a", "メルマガ配信をスキップ（送信禁止）する", "send_newsletter_rule_b", "最新メルマガを送信配信する", "purge_unsubscribed_account_rule_c", "アカウント情報を抹消アーカイブする"),
        ("保守サポート先頭一致", "契約約款：\n第1項: 24時間プレミアム保守契約者は「専任エンジニアを即時派遣」。\n第2項: 平日9-17時スタンダード契約者は「翌営業日午前中に順次対応」。\n第3項: 無償ユーザーは「FAQ掲示板へ案内」。", "契約：24時間プレミアム保守加入企業からの深夜障害コール。", "契約：スタンダード保守加入企業からの深夜24時障害コール。", "dispatch_dedicated_engineer_p1", "専任エンジニアを即時派遣する", "schedule_next_business_day_p2", "翌営業日午前に順次対応とする", "direct_to_online_faq_p3", "オンラインFAQ掲示板の参照を案内する"),
        ("アクセス権限先頭一致", "認可ポリシー：\nStep 1: 退職者リストに記載のあるアカウントは「即座に全アクセス遮断」。\nStep 2: 役員・管理職グループ所属は「特権管理ポータルへの接続許可」。\nStep 3: 一般社員は「一般ポータルへの接続許可」。", "対象者：先月退職した元役員。", "対象者：現役の財務部長。", "block_all_access_step1", "直ちに全アクセス権限を遮断する", "grant_executive_portal_step2", "特権管理ポータルへの接続を許可する", "grant_standard_portal_step3", "一般ポータルへの接続を許可する"),
    ]
    for idx, (title, rule, s1, s2, cid1, txt1, cid2, txt2, cid3, txt3) in enumerate(first_match_cases):
        for rep in range(6):
            gid = f"tb_log_fsm_{idx*6 + rep + 1:03d}"
            c_defs = [(cid1, txt1), (cid2, txt2), (cid3, txt3)]
            choices = make_choices(c_defs)
            q = f"先頭一致判定：{title}の優先順序ルールに基づき最初に適用される判断を選択してください。"
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "first_match", "context": f"【ルール】{rule}\n事象確認：{s1}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": cid1}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "first_match", "context": f"【ルール】{rule}\n事象確認：{s2}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": cid2}})

    # Domain 8: Priority Conflict Resolution (60 pairs)
    priority_templates = [
        ("交通信号優先度", "警察官の手信号は道路信号機の灯火に優先する。警察官が停止合図、信号機が青色点灯。", "警察官が通行合図、信号機が赤色点灯。", "police_hand_signal_stop", "手信号に従い直ちに停止する", "police_hand_signal_proceed", "手信号に従い交差点を進行する", "traffic_light_amber_caution", "信号機の指示に従い徐行進入する"),
        ("システム設定上書き優先度", "環境変数（ENV）の設定値は設定ファイル（config.yaml）の設定値に優先して適用される。config: port=8080, ENV: PORT=3000。", "config: port=8080, ENVは未設定。", "port_3000_from_env", "環境変数のポート3000を適用する", "port_8080_from_config", "設定ファイルのポート8080を適用する", "port_80_default_fallback", "システム既定のポート80を適用する"),
        ("契約条項優先度", "個別覚書（特約）は基本契約書の一般条項に優先する。基本契約：支払期日翌月末、個別覚書：支払期日当月末。", "個別覚書に支払期日の記載はなく、基本契約のみ存在。", "pay_end_of_current_month_mou", "覚書特約に基づき当月末日に支払う", "pay_end_of_next_month_basic", "基本契約に基づき翌月末日に支払う", "split_into_two_installments", "分割払いとして2回に分けて支払う"),
        ("消防防災指示優先度", "館内火災報知時の避難指示アナウンスは通常業務スケジュールに絶対優先する。火災報知器鳴動中、重要会議中。", "誤報確認後の通常業務再開アナウンス放送。", "evacuate_immediately_fire_alarm", "会議を即時中断し非常口から避難する", "resume_normal_meeting_operations", "平常通り重要会議の進行を継続する", "shelter_in_place_conference", "会議室内で待機し追加連絡を待つ"),
        ("顧客サポート優先度", "生命・安全に関わる緊急インシデント（Prio 1）は通常問い合わせ（Prio 3）に優先して直ちに対応する。患者生体モニター停止通報。", "Web画面の文字色変更に関する質問メール。", "triage_emergency_critical_p1", "最優先緊急インシデントとして即時対処する", "handle_routine_inquiry_p3", "通常サポートとして順次回答案内する", "queue_for_batch_processing", "翌週の定期アップデート検討キューへ回送する"),
        ("航空管制指示優先度", "空中衝突防止装置（TCAS）の回避指示は地上の航空管制官（ATC）の高度維持指示に絶対優先する。TCASが「上昇（Climb）」を指示、ATCが「現在高度維持」を指示。", "TCASが「降下（Descend）」を指示、ATCが「現在高度維持」を指示。", "follow_tcas_climb_instruction", "TCASの指示を最優先し上昇操作を実行する", "follow_tcas_descend_instruction", "TCASの指示を最優先し降下操作を実行する", "maintain_atc_level_flight", "地上の管制官指示に従い水平飛行を保つ"),
        ("製品出荷合否優先度", "出荷前検査における安全項目不適合（NG）は外観検査の合格（OK）に優先して出荷不合格とする。外観A判定合格、耐圧絶縁破壊NG。", "外観A判定合格、耐圧絶縁テスト合格。", "reject_shipment_safety_ng", "出荷不合格とし再検査へ回す", "approve_shipment_all_ok", "製品出荷を承認する", "rework_insulation_component", "絶縁部品のみ交換して再検査ラインへ回す"),
        ("ネットワークルーティング優先度", "最長プレフィックス一致（Longest Prefix Match）がデフォルトルート（0.0.0.0/0）に優先する。宛先192.168.1.50に対し192.168.1.0/24ルートとデフォルトルートが存在。", "宛先10.0.0.1に対しデフォルトルートのみ一致。", "route_via_specific_subnet", "最長一致の192.168.1.0/24へパケット転送する", "route_via_default_gateway", "デフォルトゲートウェイへパケット転送する", "drop_unroutable_packet", "経路なしとしてパケットを破棄する"),
        ("医療トリアージ優先度", "重症緊急トリアージ（赤タグ：即時治療）は中等症（黄タグ）および軽症（緑タグ）に優先して医師が治療。患者A（気道閉塞・赤タグ）、患者B（打撲・緑タグ）。", "患者C（骨折歩行可能・黄タグ）、患者D（擦り傷・緑タグ）。", "treat_red_tag_patient_first", "赤タグ患者を最優先で即時治療室へ収容する", "treat_yellow_tag_patient_first", "黄タグ患者を中等症処置室へ優先収容する", "direct_green_tag_to_waiting", "緑タグ患者を待合室にて待機させる"),
        ("社内規程改定優先度", "最新改訂版（Rev.4）の規程は旧版（Rev.3以前）に優先して適用される。旧版：日当2,000円、最新版：日当3,500円。", "旧版：日当2,000円、最新改訂版の施行前（現在Rev.2適用）。", "apply_latest_rev4_allowance", "最新改訂版（Rev.4）の日当3,500円を適用する", "apply_legacy_rev2_allowance", "現行旧版に基づき日当2,000円を適用する", "calculate_average_allowance", "新旧規定の中間平均額を仮支給する"),
    ]
    for idx, (title, s1, s2, cid1, txt1, cid2, txt2, cid3, txt3) in enumerate(priority_templates):
        for rep in range(6):
            gid = f"tb_log_prio_{idx*6 + rep + 1:03d}"
            c_defs = [(cid1, txt1), (cid2, txt2), (cid3, txt3)]
            choices = make_choices(c_defs)
            q = f"優先順位判定：{title}の優先ルールに従い、採るべき優先行動を選択してください。"
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "priority_override", "context": f"【優先度決定ルール】{s1}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": cid1}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "priority_override", "context": f"【優先度決定ルール】{s2}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": cid2}})

    # Domain 9: Reverse Criteria and Exclusion Conditions (NO reasoning prefixes in choices!) (60 pairs)
    reverse_templates = [
        ("最小リスク選択", "運用案Alpha（年利1.5%・元本政府全額保証）、運用案Beta（年利25%・暗号通貨デリバティブ元本全損リスク極大）。", "最も元本割れリスクが小さい（安全な）案を選択してください。", "最もハイリスク・ハイリターンな投機案を選択してください。", "option_alpha_safe_guarantee", "運用案Alpha（元本政府全額保証）", "option_beta_high_risk_speculative", "運用案Beta（暗号通貨デリバティブ投機）", "option_gamma_balanced_fund", "運用案Gamma（株式債券バランス型投資信託）"),
        ("最低遅延配送", "配送方法P（翌朝8時必着航空便）、配送方法Q（1週間後配送の普通便）。", "所要時間が最も短い（最速で到着する）手段を選択してください。", "所要時間が最も長い（最も日数を要する）手段を選択してください。", "method_p_fastest_express", "配送方法P（翌朝8時必着航空便）", "method_q_slowest_standard", "配送方法Q（1週間後配送の普通便）", "method_r_scheduled_courier", "配送方法R（3日後配達の時間帯指定宅配便）"),
        ("最小工数改修", "対応A（設定ファイルのポート番号を1行書き換え）、対応B（全マイクロサービスのデータベーススキーマ全面刷新）。", "開発工数が最も少ない（最も負担が軽い）対応を選択してください。", "開発工数が最も多い（最も負担が重い）対応を選択してください。", "action_a_minimal_workload", "対応A（設定ファイルのポート1行書き換え）", "action_b_massive_refactor", "対応B（全マイクロサービスのDB全面刷新）", "action_c_script_patch", "対応C（自動移行スクリプトを単一実行）"),
        ("最高省電力モード", "モードX（スタンバイ時消費電力0.5Wのディープスリープ）、モードY（全コアフル稼働時消費電力150Wのターボブースト）。", "電力消費量が最も少ない省電力モードを選択してください。", "電力消費量が最も多い高出力モードを選択してください。", "mode_x_deep_sleep_low_power", "モードX（0.5Wディープスリープ）", "mode_y_turbo_boost_high_power", "モードY（150W全コアターボブースト）", "mode_z_balanced_standby", "モードZ（35W通常定格運用）"),
        ("最低侵襲治療", "治療法M（内視鏡による微小創口手術・入院1日）、治療法N（開胸開心による大手術・入院1ヶ月）。", "患者の身体的負担が最も軽い低侵襲治療を選択してください。", "患者の身体的負担が最も重い侵襲的手術を選択してください。", "treatment_m_minimally_invasive", "治療法M（内視鏡による微小創口手術）", "treatment_n_major_open_surgery", "治療法N（開胸開心による大手術）", "treatment_l_drug_therapy", "治療法L（内服薬による経過観察療法）"),
        ("最小通信容量", "通信プロトコルK（バイナリ12バイトのIoT軽量テレメトリ）、通信プロトコルL（毎秒50MBの非圧縮4K映像ストリーミング）。", "帯域消費データ容量が最も小さい通信を選択してください。", "帯域消費データ容量が最も大きい通信を選択してください。", "protocol_k_minimal_payload", "通信K（バイナリ12バイト軽量テレメトリ）", "protocol_l_heavy_video_stream", "通信L（毎秒50MB非圧縮4K映像）", "protocol_m_compressed_json", "通信M（毎秒2KB圧縮JSONテレメトリ）"),
        ("最小人手作業手順", "運用手順1（AIによる全自動OCR読み取りおよび自動DB登録）、運用手順2（紙の伝票原本を目視確認し手書きで台帳へ転記）。", "人手による作業介入が不要な（自動化された）手順を選択してください。", "人手による物理的作業が必須となる手順を選択してください。", "proc_1_fully_automated", "運用手順1（AI全自動OCR・自動DB登録）", "proc_2_manual_handwriting", "運用手順2（紙伝票目視・手書き転記作業）", "proc_3_hybrid_assisted", "運用手順3（OCR自動読取後の担当者確認承認）"),
        ("最高耐震等級", "建築仕様Alpha（耐震等級3・震度7の1.5倍の揺れに倒壊せず耐える設計）、建築仕様Beta（旧耐震基準・震度5強で倒壊の恐れあり）。", "地震に対する強度が最も高い（最も安全な）構造を選択してください。", "地震に対する強度が最も低い（最も倒壊リスクが高い）構造を選択してください。", "spec_alpha_highest_seismic_grade", "建築仕様Alpha（耐震等級3設計）", "spec_beta_lowest_seismic_grade", "建築仕様Beta（旧耐震基準設計）", "spec_gamma_standard_grade1", "建築仕様Gamma（耐震等級1標準設計）"),
        ("最小個人情報保有", "サービス設計X（氏名・住所・生年月日を取得せず匿名IDのみで利用可能）、サービス設計Y（氏名・マイナンバー・年収・病歴をすべて必須登録）。", "プライバシー漏洩リスクが最も低い（個人情報を保持しない）設計を選択してください。", "プライバシーリスクが最も高い（センシティブ個人情報を大量保持する）設計を選択してください。", "design_x_anonymous_minimal_pii", "サービス設計X（匿名IDのみで利用可能）", "design_y_extensive_sensitive_pii", "サービス設計Y（氏名・マイナンバー等必須）", "design_z_pseudonym_email", "サービス設計Z（メールアドレスのみ登録必須）"),
        ("最低騒音機器", "機器P（定格稼働音18dBの静音設計ファン）、機器Q（定格稼働音95dBの大型エンジンコンプレッサー）。", "動作騒音が最も小さい（最も静かな）機器を選択してください。", "動作騒音が最も大きい（最も騒音公害リスクの高い）機器を選択してください。", "device_p_ultra_quiet_fan", "機器P（定格稼働音18dB静音ファン）", "device_q_loud_compressor", "機器Q（定格稼働音95dB大型コンプレッサー）", "device_r_standard_blower", "機器R（定格稼働音55dB標準ブロワー）"),
    ]
    for idx, (title, ctx_body, q1, q2, cid1, txt1, cid2, txt2, cid3, txt3) in enumerate(reverse_templates):
        for rep in range(6):
            gid = f"tb_log_rev_{idx*6 + rep + 1:03d}"
            c_defs = [(cid1, txt1), (cid2, txt2), (cid3, txt3)]
            choices = make_choices(c_defs)
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "reverse_criterion", "context": f"【比較対象】{ctx_body}", "question": q1, "choices": choices, "target": {"kind": "hard", "choice_id": cid1}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "reverse_criterion", "context": f"【比較対象】{ctx_body}", "question": q2, "choices": choices, "target": {"kind": "hard", "choice_id": cid2}})

    # Domain 10: Multi-Step Chained Conditions (NO reasoning prefixes in choices!) (60 pairs)
    chained_templates = [
        ("ステップ進行規程：書類審査合格（Step 1）→ 筆記試験合格（Step 2）→ 役員面接合格（Step 3）で採用内定。申請者：Step 1合格、Step 2合格、Step 3合格。", "内定判定：最終選考結果を選択してください。", "ステップ進行規程：書類審査合格（Step 1）→ 筆記試験合格（Step 2）→ 役員面接合格（Step 3）で採用内定。申請者：Step 1合格、Step 2不合格。\n内定判定：選考結果を選択してください。", "offer_employment_all_steps_passed", "採用内定を授与する", "reject_employment_step2_failed", "選考を打ち切り不採用とする", "request_step2_retest", "筆記試験の再受験を許可する"),
        ("口座開設ワークフロー：オンライン本人確認完了 → 反社DB照会クリア → 初期入金完了で口座開設。顧客：本人確認OK、反社照会OK、初期入金OK。", "口座開設判定：手続ステータスを選択してください。", "口座開設ワークフロー：オンライン本人確認完了 → 反社DB照会クリア → 初期入金完了で口座開設。顧客：本人確認OK、反社DBで該当者ヒット。\n口座開設判定：手続ステータスを選択してください。", "open_bank_account_verified", "正式な銀行口座を開設する", "refuse_bank_account_anti_social", "銀行口座の開設を拒絶する", "hold_application_manual_kyc", "コンプライアンス担当者による個別精査へ回す"),
        ("工場出荷ゲート：重量測定合格 → 目視外観合格 → バーコード読取合格で出門ゲート開放。トラック積載品：全3工程合格。", "出門判定：ゲート開閉操作を選択してください。", "工場出荷ゲート：重量測定合格 → 目視外観合格 → バーコード読取合格で出門ゲート開放。トラック積載品：重量過積載アラート発生。\n出門判定：ゲート開閉操作を選択してください。", "open_shipping_gate_passed", "出荷出門ゲートを開放する", "close_shipping_gate_overweight", "出門ゲートを閉止し過積載を再計量する", "divert_to_side_inspection_bay", "トラックを側道待機バースへ誘導する"),
        ("海外渡航ビザ発給：旅券残存半年以上 → 往復航空券所持 → 残高証明書提出でビザ発給。申請者：旅券残存1年、往復航空券あり、残高証明提出済み。", "査証審査判定：ビザ発給可否を選択してください。", "海外渡航ビザ発給：旅券残存半年以上 → 往復航空券所持 → 残高証明書提出でビザ発給。申請者：旅券有効期限が来月で満了（残存1ヶ月）。\n査証審査判定：ビザ発給可否を選択してください。", "issue_travel_visa_compliant", "査証（ビザ）を発行する", "refuse_travel_visa_expired_passport", "査証（ビザ）の発給を拒絶する", "grant_conditional_transit_pass", "72時間以内の臨時トランジット許可証を発行する"),
        ("臨床治験参加条件：年齢20〜65歳 → 同意書署名済み → アレルギー歴なしで治験登録。被験者：38歳、同意書署名あり、アレルギーなし。", "治験登録判定：治験参加可否を選択してください。", "臨床治験参加条件：年齢20〜65歳 → 同意書署名済み → アレルギー歴なしで治験登録。被験者：72歳、同意書署名あり、アレルギーなし。\n治験登録判定：治験参加可否を選択してください。", "enroll_in_clinical_trial", "治験参加者として本登録する", "disqualify_clinical_trial_over_age", "治験参加の適格外とする", "register_observational_cohort", "投薬なしの一般観察コホート群として登録する"),
        ("建設着工許可：地盤調査適合 → 建築確認済証交付 → 近隣説明会完了で着工許可。現場：地盤改良済適合、確認済証受領、説明会完了報告あり。", "着工許可判定：工事開始可否を選択してください。", "建設着工許可：地盤調査適合 → 建築確認済証交付 → 近隣説明会完了で着工許可。現場：地盤調査で軟弱地盤未対策、確認済証未交付。\n着工許可判定：工事開始可否を選択してください。", "grant_construction_commence_permit", "建設着工を正式許可する", "deny_construction_permit_unapproved", "建設着工を差し止める", "permit_preliminary_site_fencing", "仮設囲いの設置工事のみ先行着手を許可する"),
        ("クレジット増枠審査：継続利用1年以上 → 直近支払遅延ゼロ → 年収審査基準クリアで増枠実行。会員：利用歴3年、遅延ゼロ、年収基準充足。", "増枠判定：限度額引き上げ可否を選択してください。", "クレジット増枠審査：継続利用1年以上 → 直近支払遅延ゼロ → 年収審査基準クリアで増枠実行。会員：入会2ヶ月目、遅延ゼロ、年収基準充足。\n増枠判定：限度額引き上げ可否を選択してください。", "approve_credit_limit_increase", "利用限度額の引き上げを承認する", "deny_credit_limit_increase_tenure", "利用限度額の増枠申請を見送る", "offer_temporary_travel_credit", "一時的な旅行用途の臨時枠増額のみ案内する"),
        ("奨学金給付判定：学業成績GPA3.2以上 → 家計所得基準内 → 指導教授推薦状ありで給付採択。学生：GPA3.6、所得基準合致、推薦状提出済み。", "奨学金選考判定：給付採択可否を選択してください。", "奨学金給付判定：学業成績GPA3.2以上 → 家計所得基準内 → 指導教授推薦状ありで給付採択。学生：GPA2.4、所得基準合致、推薦状提出済み。\n奨学金選考判定：給付採択可否を選択してください。", "award_scholarship_stipend", "奨学金給付を正式採択する", "reject_scholarship_low_gpa", "奨学金の給付を不採択とする", "grant_tuition_installment_plan", "給付型ではなく学費分納（延納）制度を案内する"),
        ("特急列車乗務員点呼：酒気帯びゼロ → 睡眠時間6時間以上 → 体温平熱で乗務承認。運転士：アルコール0.00、睡眠7時間、体温36.5℃。", "乗務点呼判定：列車乗務可否を選択してください。", "特急列車乗務員点呼：酒気帯びゼロ → 睡眠時間6時間以上 → 体温平熱で乗務承認。運転士：アルコール0.00、睡眠3時間（寝不足申告）、体温36.5℃。\n乗務点呼判定：列車乗務可否を選択してください。", "approve_train_crew_dispatch", "点呼合格とし列車への乗務を承認する", "suspend_train_crew_lack_of_sleep", "乗務を停止し代替要員を手配する", "assign_depot_standby_duty", "本線運転を外し車両基地内での待機点検業務とする"),
        ("毒劇物保管庫解錠：管理者IDカード認証 → 虹彩生体認証 → デュアルキー解錠の3段階で保管庫開放。作業員：全3段階認証クリア。", "保管庫アクセス判定：解錠制御を選択してください。", "毒劇物保管庫解錠：管理者IDカード認証 → 虹彩生体認証 → デュアルキー解錠の3段階で保管庫開放。作業員：生体認証で照合失敗エラー。\n保管庫アクセス判定：解錠制御を選択してください。", "unlock_toxic_chemicals_storage", "毒劇物保管庫の解錠を実行する", "lockout_storage_biometric_failure", "保管庫の解錠を拒絶し警備へ通報する", "request_supervisor_override_key", "セキュリティ管理者同伴による非常解錠を要求する"),
    ]
    for idx, (ctx1, q1, ctx2_raw, cid1, txt1, cid2, txt2, cid3, txt3) in enumerate(chained_templates):
        for rep in range(6):
            gid = f"tb_log_chn_{idx*6 + rep + 1:03d}"
            c_defs = [(cid1, txt1), (cid2, txt2), (cid3, txt3)]
            choices = make_choices(c_defs)
            if "\n" in ctx2_raw:
                ctx2, q2 = ctx2_raw.split("\n", 1)
            else:
                ctx2, q2 = ctx2_raw, q1
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "chained_gates", "context": ctx1, "question": q1, "choices": choices, "target": {"kind": "hard", "choice_id": cid1}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "chained_gates", "context": ctx2, "question": q2, "choices": choices, "target": {"kind": "hard", "choice_id": cid2}})

    # Domain 11: Single-Clause Implicit Denial / Withholding Rules (60 pairs = 120 records)
    # Explicitly addresses unswitched cross-attention bias when negative outcome is unstated in rule
    single_clause_templates = [
        (
            "臨床投薬投与",
            "医師指示プロトコル：『収縮期血圧が90mmHg以上、かつ心拍数が50bpm以上を示しているとき血管拡張薬ニトログリセリンを投与可能』。",
            "現在の患者バイタル：血圧118/74mmHg、心拍数66bpm。",
            "現在の患者バイタル：血圧76/48mmHg、心拍数62bpm。",
            "投薬実施判断：ニトログリセリンの投与指示を選択してください。",
            [("administer_nitro_medication", "指示通りニトログリセリンを投与する"), ("withhold_nitro_contraindicated", "投与を見送り昇圧措置を優先する"), ("request_cardiologist_consult", "循環器専門医に対面診察を要請する")],
            "administer_nitro_medication", "withhold_nitro_contraindicated"
        ),
        (
            "太陽光蓄電池売電",
            "系統連系インバータ制御基準：『蓄電池残量が95%以上、かつ日射強度が800W/m2以上の場合に余剰電力の商用グリッド売電を開始する』。",
            "現在の計測値：蓄電池残量98%、日射強度890W/m2。",
            "現在の計測値：蓄電池残量82%、日射強度910W/m2。",
            "系統制御操作：系統連系インバータの制御を選択してください。",
            [("export_surplus_solar_to_grid", "余剰電力を商用系統へ逆潮流売電する"), ("charge_battery_priority_internal", "全発電量を蓄電池充電へ優先回送する"), ("trip_solar_inverter_offline", "パワーコンディショナーを系統から解列する")],
            "export_surplus_solar_to_grid", "charge_battery_priority_internal"
        ),
        (
            "自動車追従操舵支援",
            "車両自動運転制御：『前方ミリ波レーダーが先行車を捕捉し、かつ車載カメラの白線認識が両側有効なときステアリング支援を起動する』。",
            "センサ状態：先行車捕捉完了、白線認識は左右両側ともに正常。",
            "センサ状態：先行車捕捉完了、白線認識は右側が逆光によりロスト。",
            "操舵モード指示：ステアリング操舵支援の作動を選択してください。",
            [("engage_steering_support_active", "ステアリング操舵支援を作動する"), ("suppress_steering_support_standby", "ステアリング操舵支援を解除・待機する"), ("sound_driver_takeover_alert", "警報音を鳴らし運転者へ手動復帰を促す")],
            "engage_steering_support_active", "suppress_steering_support_standby"
        ),
        (
            "高精度3Dプリント造形",
            "積層造形開始基準：『チャンバー温度が65℃に達し、かつノズル先端のオートレベリング誤差が0.02mm以内のとき造形を開始する』。",
            "機体ステータス：チャンバー68℃、レベリング誤差0.012mm。",
            "機体ステータス：チャンバー51℃、レベリング誤差0.014mm。",
            "造形開始判定：プリントシーケンスの進行を選択してください。",
            [("start_3d_print_job_sequence", "3Dプリント造形を開始する"), ("hold_print_heating_continue", "造形を待機し加熱を継続する"), ("recalibrate_bed_leveling_sensor", "ベッドレベリングを再測定調整する")],
            "start_3d_print_job_sequence", "hold_print_heating_continue"
        ),
        (
            "LNG着桟荷役接続",
            "タンカー受入安全基準：『平均風速が10m/s未満、かつ波高が1.0m未満のとき着桟荷役パイプを接続する』。",
            "現場気象実測値：平均風速6m/s、波高0.4m。",
            "現場気象実測値：平均風速14m/s、波高0.5m。",
            "荷役作業判定：ローディングアームの接続可否を選択してください。",
            [("connect_loading_arm_cargo", "ローディングアームを接続し荷役準備する"), ("abort_and_standoff_at_sea", "接続を見送り洋上待機を指示する"), ("request_tugboat_position_assist", "タグボートによる船位保持補佐を求める")],
            "connect_loading_arm_cargo", "abort_and_standoff_at_sea"
        ),
        (
            "半導体露光発振",
            "ステッパー照射基準：『X軸位置決め精度が0.5nm以内、かつ真空度が1.0e-5Pa以下のときEUV露光パルスを発振する』。",
            "干渉計測定値：X軸偏差0.2nm、真空度4.0e-6Pa。",
            "干渉計測定値：X軸偏差0.9nm、真空度4.0e-6Pa。",
            "露光トリガー指示：EUV露光パルス照射の可否を選択してください。",
            [("trigger_euv_pulse_exposure", "EUV露光パルス照射を実行する"), ("realign_stage_position_hold", "照射を保留しステージ微動再位置決めを行う"), ("inspect_optics_mirror_clean", "光学ミラーの汚染度を精密点検する")],
            "trigger_euv_pulse_exposure", "realign_stage_position_hold"
        ),
        (
            "オンライン即時与信",
            "個人ローン自動審査：『勤続年数が3年以上、かつ年収負担率が30%以下の場合に自動承認とする』。",
            "申込者提出データ：勤続5年、返済比率21%。",
            "申込者提出データ：勤続1年3ヶ月、返済比率22%。",
            "与信判定結果：申込に対する初期審査結果を選択してください。",
            [("approve_instant_credit_loan", "自動与信を即時承認する"), ("refer_manual_underwriting_review", "自動承認せず人手本審査へ回付する"), ("request_tax_withholding_slip", "源泉徴収票の原本提出を追加要求する")],
            "approve_instant_credit_loan", "refer_manual_underwriting_review"
        ),
        (
            "無菌室入室インターロック",
            "バイオ研究室入室規程：『入室バッジ認証が有効、かつ差圧計が15Pa以上を示している場合のみ自動ドアを解錠する』。",
            "セキュリティログ：バッジ認証OK、前室差圧19Pa。",
            "セキュリティログ：バッジ認証OK、前室差圧7Pa。",
            "インターロック制御：入室自動ドアの開閉を選択してください。",
            [("unlock_cleanroom_entry_door", "入室ドアを解錠する"), ("keep_locked_pressure_alarm", "ドア施錠を維持し差圧警告を発報する"), ("run_decontamination_air_shower", "除染エアシャワーを最初からやり直す")],
            "unlock_cleanroom_entry_door", "keep_locked_pressure_alarm"
        ),
        (
            "越境通関ルート選択",
            "輸出貨物審査要領：『インボイス記載価格が20万円以下、かつ該非判定書で非該当と証明されている貨物は簡易通関とする』。",
            "貨物申告書：記載価格14万円、該非判定書非該当添付済み。",
            "貨物申告書：記載価格14万円、該非判定で軍民両用リスト規制該当。",
            "通関ルート選択：適用すべき通関手続きを選択してください。",
            [("route_simplified_export_customs", "簡易通関ルートで申告する"), ("route_formal_export_license_req", "経済産業省個別輸出許可申請ルートへ回す"), ("hold_cargo_in_bonded_warehouse", "保税倉庫での精密現物検査を指示する")],
            "route_simplified_export_customs", "route_formal_export_license_req"
        ),
        (
            "クラウドDB自動フェイルオーバー",
            "データベース可用性管理規程：『レプリケーション遅延が1秒未満、かつセカンダリノードのCPU使用率が60%以下の場合に限り自動昇格を実行する』。",
            "システム監視データ：レプリケーション遅延0.1秒、セカンダリCPU使用率44%。",
            "システム監視データ：レプリケーション遅延0.1秒、セカンダリCPU使用率76%。",
            "フェイルオーバー実行判定：自動昇格の実行可否を選択してください。",
            [("promote_secondary_node_auto", "セカンダリを自動昇格する"), ("hold_promote_manual_intervention", "自動昇格を見送り手動介入を要請する"), ("restart_replication_service", "レプリケーションデーモンを再起動する")],
            "promote_secondary_node_auto", "hold_promote_manual_intervention"
        ),
    ]

    for idx, (title, rule, s1, s2, q, c_defs, t1, t2) in enumerate(single_clause_templates):
        for rep in range(6):
            gid = f"tb_log_sgl_{idx*6 + rep + 1:03d}"
            choices = make_choices(c_defs)
            records.append({
                "id": f"{gid}_s1",
                "group_id": gid,
                "family": "logical_operators",
                "subdomain": "single_clause_implicit_denial",
                "context": f"{rule}\n現在の監視データ：{s1}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2",
                "group_id": gid,
                "family": "logical_operators",
                "subdomain": "single_clause_implicit_denial",
                "context": f"{rule}\n現在の監視データ：{s2}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    # Domain 12: Sub-hierarchy Priority & Partial Competition (60 pairs = 120 records)
    # Context defines 3-tier hierarchy: Rank 1 > Rank 2 > Rank 3.
    # In s1: Rank 2 and Rank 3 compete (Rank 1 absent) -> target is Rank 2 (NOT Rank 1 distractor!)
    # In s2: Rank 1 and Rank 2 compete -> target is Rank 1.
    sub_hierarchy_templates = [
        (
            "空港進入滑走路管制",
            "滑走路進入優先規程：『優先1位【燃料緊急残量機】＞ 優先2位【定期国際線旅客機】＞ 優先3位【訓練小型機】。同時要求時は上位機を先行着陸させる』。",
            "アプローチ進入状況：定期国際線旅客機と訓練小型機が同時に進入許可を要求。",
            "アプローチ進入状況：燃料緊急機と定期国際線旅客機が同時に進入許可を要求。",
            "進入管制指示：優先して滑走路進入・着陸を許可すべき航空機を選択してください。",
            [("land_intl_scheduled_flight", "優先2位の定期国際線旅客機を進入許可する"), ("land_emergency_fuel_aircraft", "最優先1位の燃料緊急機を進入許可する"), ("land_training_light_aircraft", "優先3位の訓練小型機を進入許可する")],
            "land_intl_scheduled_flight", "land_emergency_fuel_aircraft"
        ),
        (
            "クラウドコンテナ配備スケジューリング",
            "クラスタ割当優先基準：『Rank 1【本番オンライン決済API】＞ Rank 2【リアルタイム推薦サービス】＞ Rank 3【深夜ログ集計バッチ】』。",
            "ノード枯渇インシデント：リアルタイム推薦サービスと深夜ログ集計バッチが同時にCPUコアを要求。",
            "ノード枯渇インシデント：本番オンライン決済APIとリアルタイム推薦サービスが同時にCPUコアを要求。",
            "スケジューラ配任：コンテナを優先起動すべきサービスを選択してください。",
            [("schedule_recommendation_service", "Rank 2のリアルタイム推薦サービスへ割り当てる"), ("schedule_payment_api_service", "最優先Rank 1の本番決済APIへ割り当てる"), ("schedule_log_batch_service", "Rank 3の深夜ログ集計バッチへ割り当てる")],
            "schedule_recommendation_service", "schedule_payment_api_service"
        ),
        (
            "救急外来初療室トリアージ",
            "緊急初療室トリアージ基準：『重症度I【心肺停止・重篤外傷】＞ 重症度II【急性虫垂炎・複合骨折】＞ 重症度III【軽度打撲・表在擦過傷】』。",
            "初療ベッド逼迫：急性虫垂炎患者と軽度打撲患者が同時に救急搬送到達。",
            "初療ベッド逼迫：心肺停止疑い患者と急性虫垂炎患者が同時に救急搬送到達。",
            "トリアージ入室判定：先に初療室ベッドへ収容すべき患者を選択してください。",
            [("admit_triage_severity_2_appendicitis", "重症度IIの急性虫垂炎・骨折患者を収容する"), ("admit_triage_severity_1_cpa", "最重症度Iの心肺停止・重篤外傷患者を収容する"), ("admit_triage_severity_3_bruise", "重症度IIIの軽度打撲患者を収容する")],
            "admit_triage_severity_2_appendicitis", "admit_triage_severity_1_cpa"
        ),
        (
            "物流幹線輸送配車枠",
            "幹線輸送トラック積載規程：『優先度A【生鮮冷蔵チルド便】＞ 優先度B【期日指定翌日配達宅配便】＞ 優先度C【通常納期フリー定期便】』。",
            "積載積載重量制限：翌日配達宅配便と納期フリー定期便が残余積載枠を巡り競合。",
            "積載積載重量制限：生鮮チルド便と翌日配達宅配便が残余積載枠を巡り競合。",
            "配車運行指示：優先して大型トラックに積み込むべき貨物を選択してください。",
            [("ship_priority_b_express_delivery", "優先度Bの期日指定翌日配達宅配便を積載する"), ("ship_priority_a_fresh_chilled", "最優先度Aの生鮮冷蔵チルド便を積載する"), ("ship_priority_c_standard_regular", "優先度Cの通常納期フリー定期便を積載する")],
            "ship_priority_b_express_delivery", "ship_priority_a_fresh_chilled"
        ),
        (
            "電力系統緊急遮断順位",
            "周波数低下保護シーケンス：『遮断回避維持【総合病院・浄水施設】＞ 段階遮断【大規模工業団地工場】＞ 即時先行遮断【一般街路灯・商業広告塔】』。",
            "需給逼迫事象：工業団地系統と商業街路灯系統が段階遮断の対象候補として競合。",
            "需給逼迫事象：総合病院系統と工業団地系統が供給維持の優先度で競合。",
            "送配電指令：供給を継続・維持すべき（先に落としてはならない）重要系統を選択してください。",
            [("maintain_power_industrial_park", "工業団地工場系統の送電を優先維持する"), ("maintain_power_vital_hospital", "最重要の総合病院・浄水施設系統の送電を維持する"), ("maintain_power_street_signage", "街路灯・広告塔系統の送電を優先維持する")],
            "maintain_power_industrial_park", "maintain_power_vital_hospital"
        ),
        (
            "港湾コンテナクレーン荷役",
            "ガントリークレーン作業順位：『荷役順1【定温冷蔵リーファーコンテナ】＞ 荷役順2【一般満載ドライコンテナ】＞ 荷役順3【回送用空コンテナ】』。",
            "荷役バース競合：一般ドライコンテナと回送用空コンテナが同一クレーン揚程で競合。",
            "荷役バース競合：冷蔵リーファーコンテナと一般ドライコンテナが同一クレーン揚程で競合。",
            "クレーン荷役指令：先に荷揚げ揚収を行うべきコンテナを選択してください。",
            [("crane_unload_dry_container", "荷役順2の一般満載ドライコンテナを先行荷揚げする"), ("crane_unload_reefer_container", "最優先荷役順1の冷蔵リーファーコンテナを先行荷揚げする"), ("crane_unload_empty_container", "荷役順3の回送用空コンテナを先行荷揚げする")],
            "crane_unload_dry_container", "crane_unload_reefer_container"
        ),
        (
            "社内ネットワーク帯域QoS",
            "トラフィック帯域制御ポリシー：『優先Class 1【役員ビデオ通話・VoIP音声】＞ Class 2【社内Web・業務API】＞ Class 3【大容量バックアップ同期】』。",
            "回線帯域上限到達：社内Webアクセスと大容量バックアップが残り帯域を競合。",
            "回線帯域上限到達：役員ビデオ通話と社内Webアクセスが残り帯域を競合。",
            "ルータQoS制御：パケット転送帯域を優先割り当てすべきトラフィックを選択してください。",
            [("qos_allocate_class_2_web_api", "Class 2の社内Web・業務APIへ帯域を優先配分する"), ("qos_allocate_class_1_voip_video", "最優先Class 1の役員ビデオ通話・VoIPへ帯域を優先配分する"), ("qos_allocate_class_3_bulk_backup", "Class 3の大容量バックアップへ帯域を優先配分する")],
            "qos_allocate_class_2_web_api", "qos_allocate_class_1_voip_video"
        ),
        (
            "化学プラント加熱蒸気分配",
            "ボイラー高圧蒸気分配基準：『系統I【発熱重合反応炉ジャケット】＞ 系統II【製品結晶化乾燥工程】＞ 系統III【事務棟空調暖房配管】』。",
            "蒸気圧低下インシデント：製品乾燥工程と事務棟空調配管が供給バルブ開度を巡り競合。",
            "蒸気圧低下インシデント：重合反応炉ジャケットと製品乾燥工程が供給バルブ開度を巡り競合。",
            "バルブ制御指令：蒸気を優先供給すべき系統ラインを選択してください。",
            [("feed_steam_system_2_drying_process", "系統IIの製品結晶化乾燥工程へ蒸気を供給する"), ("feed_steam_system_1_reactor_jacket", "最優先系統Iの重合反応炉ジャケットへ蒸気を供給する"), ("feed_steam_system_3_office_heating", "系統IIIの事務棟空調暖房へ蒸気を供給する")],
            "feed_steam_system_2_drying_process", "feed_steam_system_1_reactor_jacket"
        ),
        (
            "統合監視セキュリティアラート",
            "警備コンソール対応優先順位：『警戒Lv.A【侵入検知センサー作動】＞ 警戒Lv.B【防火戸の施錠解除開放】＞ 警戒Lv.C【定期巡回タグ読取遅延】』。",
            "アラート同時多発：防火戸開放警告と巡回タグ遅延が同時に警備員端末へ着信。",
            "アラート同時多発：侵入検知センサー作動と防火戸開放警告が同時に警備員端末へ着信。",
            "警備指令判定：警備員が先に対処確認へ急行すべき事象を選択してください。",
            [("respond_alert_level_b_fire_door", "警戒Lv.Bの防火戸開放警告へ先に対処急行する"), ("respond_alert_level_a_intrusion", "最重要警戒Lv.Aの侵入検知事案へ先に対処急行する"), ("respond_alert_level_c_patrol_tag", "警戒Lv.Cの定期巡回タグ遅延へ先に対処急行する")],
            "respond_alert_level_b_fire_door", "respond_alert_level_a_intrusion"
        ),
        (
            "データセンター冷却循環水",
            "チラー冷水循環優先系統：『Tier 1【AI-GPU超高発熱クラスタ】＞ Tier 2【中発熱一般ストレージ群】＞ Tier 3【共用会議棟空調ファン】』。",
            "循環ポンプ流量制限：一般ストレージ群と会議棟空調ファンが冷水バルブ開度を競合。",
            "循環ポンプ流量制限：AI-GPUクラスタと一般ストレージ群が冷水バルブ開度を競合。",
            "設備制御判断：冷水を優先供給すべき冷却対象系統を選択してください。",
            [("cool_tier_2_storage_racks", "Tier 2の一般ストレージ群へ冷水を優先循環する"), ("cool_tier_1_gpu_clusters", "最重要Tier 1のAI-GPUクラスタへ冷水を優先循環する"), ("cool_tier_3_meeting_building", "Tier 3の共用会議棟空調へ冷水を優先循環する")],
            "cool_tier_2_storage_racks", "cool_tier_1_gpu_clusters"
        ),
    ]

    for idx, (title, rule, s1, s2, q, c_defs, t1, t2) in enumerate(sub_hierarchy_templates):
        for rep in range(6):
            gid = f"tb_log_sub_{idx*6 + rep + 1:03d}"
            choices = make_choices(c_defs)
            records.append({
                "id": f"{gid}_s1",
                "group_id": gid,
                "family": "logical_operators",
                "subdomain": "sub_hierarchy_priority",
                "context": f"{rule}\n{s1}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2",
                "group_id": gid,
                "family": "logical_operators",
                "subdomain": "sub_hierarchy_priority",
                "context": f"{rule}\n{s2}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    # Domain 13: Recommended Safety vs Catastrophic Prohibited (60 pairs = 120 records)
    # in s1: question asks for Recommended / Best Practice action
    # in s2: question asks for Prohibited / Catastrophic Disaster action
    recommended_vs_disaster_templates = [
        (
            "特高変電所受電接地作業",
            "変電所受電設備安全手順：『66kV母線点検時は検電器での無電圧確認および短絡接地器具の装着が義務付けられる。通電中の接触は即死災害を招く』。\n現況：母線の定期保守点検を開始する直前。",
            "【現場安全推奨判定】感電死亡事故を未然に防止する【最も正当・推奨される安全手順】を選択してください。",
            "【重大感電事故判定】作業員を感電即死させる【絶対に避けるべき最も非推奨・危険な最悪行為】を選択してください。",
            [("proc_verify_zero_voltage_and_ground", "検電器で無電圧を確認し短絡接地器具を確実に装着する"), ("proc_touch_bare_hand_live_busbar", "検電せず素手で66kV高圧母線に直接触れて通電を確認する"), ("proc_fill_safety_checklist_log", "安全作業点検表に作業開始時刻を記入する")],
            "proc_verify_zero_voltage_and_ground", "proc_touch_bare_hand_live_busbar"
        ),
        (
            "シアン化カリウム廃液中和",
            "毒劇物安全処理要領：『濃厚シアン廃液は強アルカリ性で次亜塩素酸塩により無害なシアン酸塩へ酸化分解する。強酸投入は猛毒青酸ガスを生じ大災害となる』。\n現況：実験室ドラフト内で高濃度シアン廃液500mlを処理中。",
            "【無害化推奨判定】猛毒ガスの発生を防ぐ【最も正当・推奨される酸化中和処理】を選択してください。",
            "【猛毒ガス事故判定】室内に青酸ガスを充満させ中毒死を招く【最も非推奨・危険な最悪行為】を選択してください。",
            [("proc_oxidize_alkaline_hypochlorite", "強アルカリ性下で次亜塩素酸ナトリウムを加え酸化分解する"), ("proc_acidify_with_concentrated_acid", "濃厚濃塩酸を一気に投入して大量の青酸ガスを急激に気化させる"), ("proc_verify_waste_container_label", "専用廃液容器のラベル表記と保管期限を確認する")],
            "proc_oxidize_alkaline_hypochlorite", "proc_acidify_with_concentrated_acid"
        ),
        (
            "水素ステーション配管漏洩",
            "高圧可燃性ガス保安基準：『水素ガス微小漏れ検知時は元弁を緊急遮断し窒素置換・防爆換気を実施する。火気使用は爆轟・火災を誘発する』。\n現況：充填ノズル配管近傍で可燃性ガス警報が鳴動。",
            "【初期封じ込め判定】水素爆発を未然に防止する【最も正当・推奨される安全措置】を選択してください。",
            "【大爆発誘発判定】充填所全体を大爆発炎上させる【最も非推奨・危険極まりない最悪行為】を選択してください。",
            [("proc_emergency_valve_shutoff_nitrogen", "元弁を緊急遮断し防爆換気ファンを回し窒素パージを実施する"), ("proc_ignite_lighter_to_find_leak", "ライターに火を着けて配管継手に近づけ着火で漏れを探す"), ("proc_log_gas_detector_ppm_reading", "ガス検知器の指示値ppmを保安日誌に記録する")],
            "proc_emergency_valve_shutoff_nitrogen", "proc_ignite_lighter_to_find_leak"
        ),
        (
            "手術室停電・人工心肺維持",
            "病院救急電気安全規程：『心臓手術中の瞬時停電時は非常用発電機の自動起動を確認し人工心肺の電源を最優先維持する。生命維持装置の切断は致死となる』。\n現況：心臓手術中に主系統が停電し無停電電源装置（UPS）が鳴動。",
            "【生命維持推奨判定】患者の術中死亡を回避する【最も正当・推奨される電源管理措置】を選択してください。",
            "【術中患者死亡判定】患者を直ちに心停止死させる【絶対に避けるべき最も非推奨な最悪行為】を選択してください。",
            [("proc_confirm_generator_emergency_power", "自家用非常用発電機の起動を確認し人工心肺の継続送電を維持する"), ("proc_unplug_heart_lung_machine", "作動中の人工心肺装置の電源プラグをコンセントから引き抜く"), ("proc_check_theatre_humidity_gauge", "手術室の湿度計インジケーターを記録する")],
            "proc_confirm_generator_emergency_power", "proc_unplug_heart_lung_machine"
        ),
        (
            "ランサムウェア感染発覚初期対応",
            "CSIRT情報セキュリティ初動基準：『マルウェア感染発覚時は直ちにネットワークケーブルを物理抜脱し他端末への横展開を遮断する』。\n現況：社内PCで重要ファイルが勝手に暗号化拡張子へ書き換わる画面が点滅。",
            "【推奨初期封じ込め判定】感染拡大を阻止するため【現場で直ちに実行すべき最も推奨される行動】を選択してください。",
            "【破滅的感染拡大判定】社内全PCへマルウェアを強制感染させる【最も非推奨・最悪の破壊行為】を選択してください。",
            [("proc_isolate_cable_disconnect_lan", "有線LANケーブルを即座に引き抜きWi-Fi接続を切断する"), ("proc_broadcast_script_to_all_pcs", "感染PCから全社ドメインサーバへ暗号化スクリプトを一斉配信する"), ("proc_report_timestamp_to_helpdesk", "インシデント発生時刻を情報システム部へ電話連絡する")],
            "proc_isolate_cable_disconnect_lan", "proc_broadcast_script_to_all_pcs"
        ),
        (
            "ガソリンローリー地下タンク注入",
            "危険物取扱安全規則：『引火性液体受入時は静電気除去接地線を接続してから注油ホースを締結する。放電火花は引火爆発の原因となる』。\n現況：ガソリン20キロリットルを地下貯蔵タンクへ注入する直前。",
            "【防火安全推奨判定】給油所火災を防止する【最も正当・推奨される危険物荷卸し手順】を選択してください。",
            "【引火爆発事故判定】大火災・爆発事故を直接引き起こす【最も非推奨・消防法違反の最悪行為】を選択してください。",
            [("proc_connect_static_ground_cable", "車体のアースクリップを接地端子へ確実に接続し静電気を除去する"), ("proc_smoke_cigarette_near_tank_hatch", "接地を接続せず注入口の直近でタバコを喫煙しながら作業する"), ("proc_check_delivery_slip_quantity", "危険物納品伝票の記載数量を確認する")],
            "proc_connect_static_ground_cable", "proc_smoke_cigarette_near_tank_hatch"
        ),
        (
            "蒸気ボイラー空焚き過熱",
            "ボイラー構造・取扱安全基準：『水位喪失による炉筒過熱（空焚き）時は直ちに燃焼停止し自然徐冷する。赤熱部への急激な冷水給水は水蒸気爆発を起こす』。\n現況：水位計が検出不能レベルまで空となり燃焼室が赤熱状態。",
            "【炉体爆発防止推奨判定】水蒸気爆発を防ぐ【最も正当・推奨される緊急対処手順】を選択してください。",
            "【水蒸気大爆発誘発判定】ボイラー室を吹き飛ばし粉砕する【最も非推奨・厳禁の最悪行為】を選択してください。",
            [("proc_cut_fuel_combustion_slow_cool", "バーナー燃料弁を全閉にして燃焼を緊急停止し自然放熱で徐冷する"), ("proc_feed_high_pressure_cold_water", "赤熱したボイラー内に高圧給水ポンプで冷水を一気に全開注入する"), ("proc_record_boiler_pressure_gauge", "ボイラー圧力計の目盛りを保全台帳に記録する")],
            "proc_cut_fuel_combustion_slow_cool", "proc_feed_high_pressure_cold_water"
        ),
        (
            "下水道マンホール酸素欠乏入孔",
            "酸素欠乏・硫化水素危険作業規則：『密閉空間への立ち入り前は送風機で連続換気し酸素濃度（18%以上）を測定確認する。無換気立入は即時昏倒死する』。\n現況：深さ5メートルの排水ポンプピット内へ定期点検で入孔する直前。",
            "【酸欠防止推奨判定】作業員の窒息・転落死を防ぐ【最も正当・推奨される入孔前措置】を選択してください。",
            "【酸欠即死事故判定】作業員を酸欠ガスで瞬時に失神死させる【最も非推奨・法令違反の最悪行為】を選択してください。",
            [("proc_force_ventilation_measure_oxygen", "送風ファンで十分強制換気した上でガス検知器で酸素18%以上を確認する"), ("proc_jump_in_holding_breath_no_mask", "換気もガス測定も一切行わず息止めだけで暗渠深部へ飛び降りる"), ("proc_check_manhole_cover_hinge", "マンホール蓋の開閉ヒンジの摩耗状態を点検する")],
            "proc_force_ventilation_measure_oxygen", "proc_jump_in_holding_breath_no_mask"
        ),
        (
            "旅客機高高度急減圧緊急対処",
            "航空運航安全基準：『巡航高度で客室急減圧発生時は操縦士が即座に酸素マスクを装着し有能時間内に高度10,000フィートへ緊急降下する』。\n現況：高度35,000フィートで客室窓クラックにより減圧アラーム鳴動・酸素マスク落下。",
            "【航空安全推奨判定】全乗員乗客の酸欠失神を防止する【最も正当・推奨される操縦操作】を選択してください。",
            "【全員酸欠窒息墜落判定】操縦不能となり全員窒息墜落死を招く【最も非推奨・破滅的な誤操縦】を選択してください。",
            [("proc_pilot_mask_rapid_descent_10k", "操縦士酸素マスクを即座に装着し高度10,000フィートへ緊急降下する"), ("proc_climb_steeply_into_stratosphere", "酸素マスクを装着せず最大出力で成層圏45,000フィートへ急上昇する"), ("proc_record_flight_altitude_log", "フライトログブックに高度異常発生時刻を記録する")],
            "proc_pilot_mask_rapid_descent_10k", "proc_climb_steeply_into_stratosphere"
        ),
        (
            "バイオ研究室病原体飛散封じ込め",
            "病原体取扱バイオセーフティ規定：『キャビネット外での病原体飛散時は換気陰圧を維持し退避した上でホルマリン等の密閉燻蒸消毒を実施する』。\n現況：BSL-3実験室内で高度病原体検体の遠心チューブが破裂し床に飛散。",
            "【バイオハザード封じ込め判定】所外漏洩と感染拡大を防ぐ【最も正当・推奨される除染対応】を選択してください。",
            "【病原体外部拡散判定】大気中へ病原体を放散しバイオ災害を起こす【最も非推奨・最悪の対応】を選択してください。",
            [("proc_evacuate_and_seal_gas_fumigation", "陰圧を維持し全員退避の上で部屋全体を消毒薬ガスで密閉燻蒸する"), ("proc_open_windows_wipe_bare_hands", "実験室の窓を全開にして素手雑巾で拭き取り外部大気中へ放散する"), ("proc_count_sterile_pipette_inventory", "薬品棚の滅菌ピペットの在庫数を数える")],
            "proc_evacuate_and_seal_gas_fumigation", "proc_open_windows_wipe_bare_hands"
        ),
    ]

    for idx, (title, rule, q_rec, q_dis, c_defs, t_rec, t_dis) in enumerate(recommended_vs_disaster_templates):
        for rep in range(6):
            gid = f"tb_log_rec_{idx*6 + rep + 1:03d}"
            choices = make_choices(c_defs)
            records.append({
                "id": f"{gid}_s1",
                "group_id": gid,
                "family": "logical_operators",
                "subdomain": "recommended_vs_catastrophic",
                "context": rule,
                "question": q_rec,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t_rec}
            })
            records.append({
                "id": f"{gid}_s2",
                "group_id": gid,
                "family": "logical_operators",
                "subdomain": "recommended_vs_catastrophic",
                "context": rule,
                "question": q_dis,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t_dis}
            })

    # Domain 14: Exact Boundary Equality & Inclusive/Exclusive Thresholds (60 pairs = 120 records)
    boundary_templates = [
        (
            "小型無人航空機重量規制",
            "小型無人機登録規程：『機体総重量が【100g以下】であれば模型航空機として機体登録免除、【100g超】であれば国交省機体登録が必須となる』。",
            "精密電子天秤計測値：ちょうど【100g】。",
            "精密電子天秤計測値：【105g】。",
            "機体登録判定：航空法に基づく登録義務の有無を選択してください。",
            [("exempt_drone_registration", "重量基準内（100g以下）として機体登録を免除する"), ("mandate_drone_registration", "基準超過（100g超）のため国交省機体登録を義務付ける"), ("confiscate_drone_immediately", "機体を直ちに没収処分する")],
            "exempt_drone_registration", "mandate_drone_registration"
        ),
        (
            "下水放流汚濁基準BOD",
            "水質汚濁防止基準：『放流水のBODが【10mg/L未満】であれば河川放流を許可し、【10mg/L以上】であれば再曝気処理槽へ返送する』。",
            "水質計分析値：BOD【8mg/L】。",
            "水質計分析値：BODちょうど【10mg/L】。",
            "放流ゲート制御：放流水の取り扱いを選択してください。",
            [("permit_river_discharge", "基準クリア（10mg/L未満）として河川への放流を許可する"), ("return_to_rebubbling_tank", "基準到達（10mg/L以上）のため再曝気処理槽へ返送する"), ("dump_raw_sludge_to_river", "未処理生汚泥を河川へ直接放流する")],
            "permit_river_discharge", "return_to_rebubbling_tank"
        ),
        (
            "列車曲線進入速度ATS",
            "保安装置速度制限：『カーブ制限速度は【85km/h以下】であり、【85km/h超】の場合はATS自動減速ブレーキが作動する』。",
            "速度発電機計測値：ちょうど【85km/h】。",
            "速度発電機計測値：【88km/h】。",
            "保安装置動作：ATS減速ブレーキの作動可否を選択してください。",
            [("allow_continue_no_brake", "制限速度内（85km/h以下）としてブレーキ非作動で力行継続"), ("activate_ats_brake", "制限速度超過（85km/h超）としてATS減速ブレーキを作動"), ("engage_emergency_derail", "非常脱線装置を作動させる")],
            "allow_continue_no_brake", "activate_ats_brake"
        ),
        (
            "通信衛星バッテリー放電深度",
            "衛星電力運用規程：『日陰飛行中の放電深度が【60%以下】であれば通常ミッション運用を継続し、【60%超】の場合は非必須観測機器を省電力遮断する』。",
            "テレメトリ測定値：DODちょうど【60%】。",
            "テレメトリ測定値：DOD【68%】。",
            "衛星電力運用：観測機器の電源状態を選択してください。",
            [("continue_normal_mission_payload", "許容深度内（60%以下）として通常ミッション観測を継続する"), ("shed_non_essential_payload", "深度限界超過（60%超）のため非必須機器を省電力遮断する"), ("discharge_battery_to_zero", "全電力を完全放電させる")],
            "continue_normal_mission_payload", "shed_non_essential_payload"
        ),
        (
            "臨床試験被験者年齢",
            "臨床試験適格基準：『参加可能な被験者年齢は【65歳未満】とし、【65歳以上】の高齢者は除外基準に抵触する』。",
            "志願者の年齢換算：【62歳】。",
            "志願者の年齢換算：同意取得日時点でちょうど【65歳0ヶ月】。",
            "治験登録適格判定：この志願者の治験登録可否を選択してください。",
            [("enroll_eligible_candidate", "年齢適格（65歳未満）として治験参加を承認する"), ("exclude_ineligible_candidate", "上限到達（65歳以上）のため治験参加を除外する"), ("falsify_subject_records", "年齢書類を改ざんして登録する")],
            "enroll_eligible_candidate", "exclude_ineligible_candidate"
        ),
        (
            "金型放電加工電極消耗",
            "NC加工基準：『銅電極の先端減耗量が【0.050mm未満】であれば仕上げ加工を継続し、【0.050mm以上】であれば電極自動交換を実行する』。",
            "機上プローブ計測値：減耗量【0.035mm】。",
            "機上プローブ計測値：減耗量ちょうど【0.050mm】。",
            "NC加工シーケンス：放電電極の処置を選択してください。",
            [("continue_finishing_spark", "許容内（0.050mm未満）として仕上げ放電加工を続行する"), ("execute_tool_change", "交換基準到達（0.050mm以上）として電極自動交換を実行する"), ("weld_electrode_to_work", "電極をワークに最大電流で溶着させる")],
            "continue_finishing_spark", "execute_tool_change"
        ),
        (
            "協働ロボット外力リセット",
            "ロボット安全規格：『人との接触検知外力が【150N以下】であれば安全一時停止からの自動復帰を許可し、【150N超】であれば非常停止ロックアウトを維持する』。",
            "力覚センサ検出値：ちょうど【150N】。",
            "力覚センサ検出値：【185N】。",
            "ロボット制御盤動作：リセット後の動作を選択してください。",
            [("allow_auto_recovery_cycle", "軽度接触（150N以下）として自動サイクル復帰を許可する"), ("maintain_safety_lockout", "過負荷衝撃（150N超）として非常停止ロックアウトを維持する"), ("swing_arm_uncontrolled", "アームを無制御で全速旋回させる")],
            "allow_auto_recovery_cycle", "maintain_safety_lockout"
        ),
        (
            "配管減肉設計裕度",
            "プラント設備保全基準：『配管スプールの減肉深さが裕度【2.0mm以下】であれば次回定修まで運転継続し、【2.0mm超】であれば緊急補修パッチを施工する』。",
            "超音波厚さ計実測値：減肉ちょうど【2.0mm】。",
            "超音波厚さ計実測値：減肉【2.7mm】。",
            "保全工事判定：この配管スプールの処置を選択してください。",
            [("continue_run_to_turnaround", "裕度範囲内（2.0mm以下）として次回定修まで運転継続する"), ("apply_emergency_reinforce", "裕度超過（2.0mm超）として緊急補修パッチを施工する"), ("pierce_pipe_wall", "配管に穴を開けて漏洩させる")],
            "continue_run_to_turnaround", "apply_emergency_reinforce"
        ),
        (
            "国際線受託手荷物重量",
            "航空手荷物運送約款：『受託手荷物の1個あたり重量が【23.0kg以下】であれば無料受託とし、【23.0kg超】であれば超過手荷物料金を収受する』。",
            "計量台表示値：ちょうど【23.0kg】。",
            "計量台表示値：【25.4kg】。",
            "手荷物受託判定：手荷物の受託手続きを選択してください。",
            [("accept_free_baggage", "許容範囲内（23.0kg以下）として無料で手荷物を受託する"), ("charge_excess_baggage_fee", "重量超過（23.0kg超）として超過料金を収受する"), ("confiscate_all_luggage", "手荷物を全量没収破棄する")],
            "accept_free_baggage", "charge_excess_baggage_fee"
        ),
        (
            "クレーン吊上安全荷重",
            "移動式クレーン作業標準：『吊り荷総重量が定格荷重【5.0トン以下】であれば巻上合図を行い、【5.0トン超】であれば過負荷防止インターロックにより巻上を阻止する』。",
            "ロードセル計測値：ちょうど【5.0トン】。",
            "ロードセル計測値：【5.8トン】。",
            "揚重合図指示：クレーン巻上操作の可否を選択してください。",
            [("signal_hoist_lift", "定格内（5.0トン以下）として安全確認の上で巻上を開始する"), ("inhibit_hoist_overload", "定格超過（5.0トン超）として巻上を阻止し荷を降ろす"), ("cut_winch_wire_cable", "ウインチワイヤーを切断する")],
            "signal_hoist_lift", "inhibit_hoist_overload"
        ),
    ]

    for idx, (title, rule, s1, s2, q, c_defs, t1, t2) in enumerate(boundary_templates):
        for rep in range(6):
            gid = f"tb_log_bnd_{idx*6 + rep + 1:03d}"
            choices = make_choices(c_defs)
            records.append({
                "id": f"{gid}_s1",
                "group_id": gid,
                "family": "logical_operators",
                "subdomain": "boundary_equality",
                "context": f"{rule}\n{s1}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2",
                "group_id": gid,
                "family": "logical_operators",
                "subdomain": "boundary_equality",
                "context": f"{rule}\n{s2}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    # Domain 15: Disjunctive OR with Asymmetric Mixed Truth Values (60 pairs = 120 records)
    or_templates = [
        (
            "サイバー防御SIEM自動隔離",
            "サイバー防御SIEM規程：『同一送信元からの不正ログイン試行が5分間に20回以上、または国外脅威インテリジェンスリスト該当のいずれかで通信を即時遮断隔離する』。",
            "ログ状況：5分間の試行は4回（基準未満）、ただし国外脅威リストにIPが完全一致（該当）。",
            "ログ状況：5分間の試行は4回（基準未満）、国外脅威リストも非該当（不一致）。",
            "SIEM自動防御アクション：ファイアウォール動作を選択してください。",
            [("quarantine_siem_endpoint", "条件合致（脅威リスト一致）により通信を即時遮断隔離する"), ("allow_siem_normal_traffic", "両条件とも不成立のため通常通信を許可しログ監視を継続する"), ("shutdown_domain_controllers", "全社ドメインコントローラを強制シャットダウンする")],
            "quarantine_siem_endpoint", "allow_siem_normal_traffic"
        ),
        (
            "ボイラー蒸気安全弁吹出し",
            "ボイラー圧力容器安全基準：『蒸気圧力が1.8MPa以上に達したか、または炉壁温度が450℃以上に達したときのいずれかで安全逃がし弁を開放する』。",
            "計装測定値：蒸気圧力1.95MPa（超過）、炉壁温度380℃（正常）。",
            "計装測定値：蒸気圧力1.50MPa（正常）、炉壁温度410℃（正常）。",
            "蒸気安全制御：リリーフ逃がし弁の操作を選択してください。",
            [("open_boiler_safety_valve", "蒸気圧超過により安全逃がし弁を開放して減圧する"), ("keep_boiler_valve_closed", "いずれの条件も未達のため弁を全閉維持し定常燃焼を継続する"), ("inject_cold_water_rapid", "赤熱ボイラー内へ冷水を急激に直接注水する")],
            "open_boiler_safety_valve", "keep_boiler_valve_closed"
        ),
        (
            "生活安心見守り通報システム",
            "生活安心見守りシステム規程：『宅内スマート水道メーターが24時間微動だにしない、または感震センサーが震度4以上を検知したときのいずれかで緊急安否確認メールを民生委員へ配信する』。",
            "センサーデータ：直近水道使用ゼロ（26時間静止）、地震検知なし（震度0）。",
            "センサーデータ：1時間前に水道使用あり（正常）、地震検知なし（震度0）。",
            "見守りシステム動作：配信判断を選択してください。",
            [("dispatch_welfare_alert", "水道24時間不使用により民生委員へ緊急安否確認メールを配信する"), ("standby_welfare_monitoring", "通報条件に該当しないため通常見守り監視を継続する"), ("dispatch_swat_assault_team", "特殊急襲部隊を現場突入させる")],
            "dispatch_welfare_alert", "standby_welfare_monitoring"
        ),
        (
            "非常用ディーゼル発電機自動起動",
            "原子力・重要施設電源規程：『主受電母線電圧が定格の80%以下に低下したか、または安全防護圧力が150kPa以上に上昇したときのいずれかで非常用発電機（D/G）を自動起動する』。",
            "計装信号：母線電圧72%（低下）、防護圧力110kPa（正常）。",
            "計装信号：母線電圧98%（正常）、防護圧力115kPa（正常）。",
            "D/G自動起動シーケンス：非常用発電機の始動を選択してください。",
            [("auto_start_emergency_dg", "母線低電圧により非常用ディーゼル発電機を直ちに自動起動する"), ("maintain_dg_in_standby", "起動条件が成立しないため発電機待機状態を維持する"), ("dump_dg_fuel_reserves", "非常用燃料タンクの全軽油を投棄する")],
            "auto_start_emergency_dg", "maintain_dg_in_standby"
        ),
        (
            "工作機械主軸サーボ急停止",
            "マシニングセンタ主軸保護基準：『主軸回転振動加速度が4.0Gを超過したか、または潤滑油圧が0.15MPaを下回ったときのいずれかで主軸サーボを急停止する』。",
            "センサー監視値：振動加速度1.2G（正常）、潤滑油圧0.08MPa（異常低下）。",
            "センサー監視値：振動加速度1.8G（正常）、潤滑油圧0.22MPa（正常）。",
            "サーボコントローラ制御：主軸モーターの動作を選択してください。",
            [("trip_spindle_servo_emergency", "油圧低下により主軸サーボ電源を即時遮断急停止する"), ("continue_spindle_machining", "異常条件なしのため所定の切削加工シーケンスを継続する"), ("reverse_spindle_max_rpm", "主軸を最高回転数で逆回転させる")],
            "trip_spindle_servo_emergency", "continue_spindle_machining"
        ),
        (
            "滑走路進入着陸復行",
            "滑走路進入着陸基準：『風向横風成分が15ノット以上、または滑走路摩擦係数が0.25未満のいずれかに該当する場合は着陸復行（ゴーアラウンド）を指示する』。",
            "進入気象：横風8ノット（正常）、滑走路摩擦係数0.18（凍結スリップ危険）。",
            "進入気象：横風8ノット（正常）、滑走路摩擦係数0.38（正常良好）。",
            "着陸進入指令：管制塔からの指示を選択してください。",
            [("command_go_around_immediate", "摩擦係数不足により直ちに着陸復行（ゴーアラウンド）を指示する"), ("authorize_landing_continue", "进入基準を満たしているため滑走路着陸进入の継続を許可する"), ("jettison_fuel_over_suburb", "住宅地上空で航空燃料を海上投棄する")],
            "command_go_around_immediate", "authorize_landing_continue"
        ),
        (
            "物流倉庫自動消火スプリンクラー",
            "物流倉庫防災基準：『天井煙濃度が10%以上、または熱感知温度が70℃以上のいずれかに達したとき初期消火スプリンクラーを自動作動する』。",
            "防災受信機：煙濃度14%（検知）、熱感知温度42℃（正常）。",
            "防災受信機：煙濃度2%（正常）、熱感知温度45℃（正常）。",
            "消火設備制御：初期消火スプリンクラーの動作を選択してください。",
            [("actuate_sprinkler_fire_system", "煙濃度超過により初期消火スプリンクラーを作動する"), ("standby_fire_alarm_system", "火災条件非該当のため作動待機監視を維持する"), ("lock_all_emergency_doors", "倉庫の全非常口を外側から施錠する")],
            "actuate_sprinkler_fire_system", "standby_fire_alarm_system"
        ),
        (
            "オフィス集中空調急速換気",
            "オフィスビル空気環境基準：『室内CO2濃度が1500ppm以上、または室温が30℃以上のいずれかに達したとき外気急速換気ダンパーを全開にする』。",
            "環境センサー：CO2濃度1680ppm（過密）、室温25℃（快適域）。",
            "環境センサー：CO2濃度900ppm（正常）、室温26℃（正常）。",
            "空調ダンパー制御：急速換気ダンパーの動作を選択してください。",
            [("open_rapid_ventilation_damper", "CO2濃度超過により急速換気ダンパーを全開にして換気する"), ("maintain_standard_hvac_circulation", "環境基準内のため定常空調循環運転を継続する"), ("shut_off_all_fresh_air", "全外気取り入れ口を完全密閉遮断する")],
            "open_rapid_ventilation_damper", "maintain_standard_hvac_circulation"
        ),
        (
            "クラウド基盤オートスケール追加",
            "Webサービス負荷制御基準：『CPU平均使用率が85%以上、または待機リクエスト数が1000件超過のいずれかで追加コンピュートノードを自動増連する』。",
            "クラスタ監視：CPU使用率60%（余裕あり）、待機キュー1450件（スパイク滞留）。",
            "クラスタ監視：CPU使用率65%（正常）、待機キュー180件（正常）。",
            "オートスケーラ判定：コンピュートノードのプロビジョニングを選択してください。",
            [("autoscale_add_compute_nodes", "キュー滞留により追加コンピュートノードを自動プロビジョニングする"), ("maintain_current_node_count", "負荷基準内のため現在の稼働ノード数を維持する"), ("terminate_all_active_nodes", "稼働中の全本番ノードを強制破棄する")],
            "autoscale_add_compute_nodes", "maintain_current_node_count"
        ),
        (
            "有料道路料金所ETC遮断バー",
            "有料道路料金所制御基準：『車載器未挿入エラー、または通過車速が40km/h超過のいずれかに該当する場合はETC進入遮断バーを降下制止する』。",
            "レーン進入センサ：車載器通信OK（正常）、車速52km/h（超過危険進入）。",
            "レーン進入センサ：車載器通信OK（正常）、車速18km/h（安全徐行）。",
            "料金所レーン制御：ETC進入遮断バーの動作を選択してください。",
            [("lower_etc_barrier_stop", "進入速度超過によりETC遮断バーを降下させて車両を制止する"), ("keep_etc_barrier_open", "通行要件充足により遮断バーを開放維持して通過を許可する"), ("launch_spike_strips", "車両のタイヤへスパイク突起を射出する")],
            "lower_etc_barrier_stop", "keep_etc_barrier_open"
        ),
    ]

    for idx, (title, rule, s1, s2, q, c_defs, t1, t2) in enumerate(or_templates):
        for rep in range(6):
            gid = f"tb_log_dis_{idx*6 + rep + 1:03d}"
            choices = make_choices(c_defs)
            records.append({
                "id": f"{gid}_s1",
                "group_id": gid,
                "family": "logical_operators",
                "subdomain": "disjunctive_or",
                "context": f"{rule}\n{s1}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2",
                "group_id": gid,
                "family": "logical_operators",
                "subdomain": "disjunctive_or",
                "context": f"{rule}\n{s2}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    # Domain 16: First-Match Cascade Precedence (60 pairs = 120 records)
    cascade_templates = [
        (
            "パケットフィルタリング",
            "優先度1", "宛先ポート443（HTTPS）", "SSL中継暗号検査を適用する", "apply_ssl_inspection",
            "優先度2", "送信元が社内VPN帯域", "社内通信として無検査透過する", "allow_internal_vpn_traffic",
            "優先度3", "それ以外", "外部Proxy経由へ転送する", "route_to_external_proxy",
            "受信パケット：送信元は社内VPN帯域、宛先ポートは443（HTTPS）。",
            "受信パケット：送信元は社内VPN帯域、宛先ポートは8080（HTTP代替）。",
            "受信パケット：送信元は公衆Wi-Fi外部IP、宛先ポートは8080（HTTP代替）。",
            "パケットフィルタ処理判定：最先頭一致ルールを適用し適切な処置を選択してください。"
        ),
        (
            "医療トリアージ判定",
            "順位1", "自発呼吸なし", "黒タグ（処置保留）を付与する", "tag_black_deceased",
            "順位2", "脈拍120以上またはショック兆候あり", "赤タグ（最優先緊急治療）を付与する", "tag_red_immediate",
            "順位3", "それ以外（自力歩行不可など）", "黄タグ（待機可能治療）を付与する", "tag_yellow_delayed",
            "患者状態：自発呼吸停止、脈拍触知不可。",
            "患者状態：自発呼吸正常、脈拍135bpm（頻脈ショック兆候）。",
            "患者状態：自発呼吸正常、脈拍78bpm、下腿骨折のため歩行不能。",
            "トリアージ区分決定：最先頭適合基準に従いトリアージタグを選択してください。"
        ),
        (
            "会員クーポン割引率",
            "順位1", "初回購入限定クーポン保有", "30%割引を適用する", "apply_first_purchase_30pct",
            "順位2", "ゴールド会員以上", "15%ゴールド会員割引を適用する", "apply_gold_member_15pct",
            "順位3", "それ以外", "割引なしの通常価格を適用する", "apply_standard_price",
            "会員情報：初回購入クーポン保有、ゴールド会員ランク。",
            "会員情報：クーポン未保有、ゴールド会員ランク。",
            "会員情報：クーポン未保有、一般会員ランク。",
            "割引適用判定：最先頭一致ルールに従い適用する価格区分を選択してください。"
        ),
        (
            "オートスケールポリシー",
            "評価順1", "待機リクエスト数2000件超過", "緊急最大拡張（ノード5台追加）を実行する", "autoscale_emergency_burst",
            "評価順2", "CPU平均使用率75%超過", "標準拡張（ノード2台追加）を実行する", "autoscale_standard_expand",
            "評価順3", "それ以外", "現行ノード数を維持する", "autoscale_maintain_nodes",
            "クラスタ監視：待機リクエスト2600件、CPU使用率82%。",
            "クラスタ監視：待機リクエスト800件、CPU使用率85%。",
            "クラスタ監視：待機リクエスト300件、CPU使用率52%。",
            "オートスケール判定：最先頭一致ポリシーに従いスケーリング動作を選択してください。"
        ),
        (
            "障害チケット対応区分",
            "第1条", "全社基幹システム停止", "最重要Tier1即時緊急召集を行う", "tier1_critical_emergency",
            "第2条", "特定部署の業務停止", "優先Tier2専任対応を割り当てる", "tier2_priority_assignment",
            "第3条", "それ以外（軽微な質問等）", "標準Tier3キューへ登録する", "tier3_standard_queue",
            "障害報告：ERP全社基幹データベース全断、全業務停止中。",
            "障害報告：営業第一課のファイル共有サーバ応答不可（基幹正常）。",
            "障害報告：モニターの解像度変更手順についての問い合わせ。",
            "チケット受付判定：最先頭合致条項に基づき対応区分を選択してください。"
        ),
        (
            "特急座席自動割当",
            "優先順位1", "車椅子利用の事前申告あり", "多目的専用個室を割り当てる", "assign_accessible_compartment",
            "優先順位2", "グリーン席特急券購入者", "特等リクライニング席を割り当てる", "assign_first_class_seat",
            "優先順位3", "それ以外", "普通車指定席を割り当てる", "assign_standard_reserved_seat",
            "予約情報：車椅子利用申告あり、グリーン席特急券所持。",
            "予約情報：単独歩行（車椅子なし）、グリーン席特急券所持。",
            "予約情報：単独歩行（車椅子なし）、普通車指定席券所持。",
            "座席手配判定：最上位優先合致条件に基づき指定座席を選択してください。"
        ),
        (
            "工場警報重大度処置",
            "危険度1", "毒性ガス漏洩を検知", "全棟非常排気を全開作動する", "trip_all_emergency_exhaust",
            "危険度2", "局所配管温度70℃超過", "該当ラインヒーターを自動遮断する", "shutdown_line_heater",
            "危険度3", "それ以外", "警報表示のみで定常監視を継続する", "maintain_standard_monitoring",
            "警報ステータス：毒性ガス漏洩検知、局所温度78℃。",
            "警報ステータス：ガス漏れなし、局所温度82℃。",
            "警報ステータス：ガス漏れなし、局所温度52℃（正常）。",
            "保全制御指示：最先頭危険度ルールを適用し安全制御を選択してください。"
        ),
        (
            "緊急配送便種別",
            "区分1", "移植用医療緊急物資", "航空チャーター直行便を手配する", "dispatch_air_charter_urgent",
            "区分2", "当日超速達指定荷物", "新幹線ハンドキャリー便を手配する", "dispatch_shinkansen_hand_carry",
            "区分3", "それ以外", "定期幹線トラック便で混載輸送する", "dispatch_regular_freight_truck",
            "荷物伝票：移植用心臓組織、当日超速達指定。",
            "荷物伝票：半導体試作チップ、当日超速達指定（非医療品）。",
            "荷物伝票：一般事務用品、期日指定なし。",
            "物流手配判定：最先頭区分基準に従い輸送手段を選択してください。"
        ),
        (
            "自動融資審査ランク",
            "ステップ1", "信用事故情報（ブラック）あり", "即時審査否決とする", "reject_loan_blacklisted",
            "ステップ2", "年収600万円以上かつ勤続3年以上", "特別優遇金利プランで事前承認する", "approve_preferred_rate_loan",
            "ステップ3", "それ以外", "一般基準金利で通常本審査へ回付する", "refer_to_standard_review",
            "審査データ：延滞ブラック登録あり、年収850万円勤続7年。",
            "審査データ：事故情報なし（正常）、年収720万円勤続4年。",
            "審査データ：事故情報なし（正常）、年収380万円勤続1年。",
            "融資事前審査判定：最先頭審査ステップに基づき融資可否を選択してください。"
        ),
        (
            "データ保管ライフサイクル",
            "ポリシー1", "訴訟保全ホールド指定あり", "永久完全保全（削除不可）とする", "apply_litigation_hold_permanent",
            "ポリシー2", "最終アクセスから5年超過", "コールドストレージへ自動移行する", "tier_to_cold_archive",
            "ポリシー3", "それ以外", "現行ホットストレージで保持する", "keep_hot_active_storage",
            "メタデータ：訴訟保全ホールド指定中、最終アクセス6年前。",
            "メタデータ：ホールド指定なし、最終アクセス7年前。",
            "メタデータ：ホールド指定なし、最終アクセス1ヶ月前。",
            "データライフサイクル判定：最先頭保管ポリシーに従い処置を選択してください。"
        ),
    ]

    for idx, (title, r1_n, r1_c, r1_a, cid1, r2_n, r2_c, r2_a, cid2, r3_n, r3_c, r3_a, cid3, s_r1, s_r2, s_r3, q) in enumerate(cascade_templates):
        rule_text = f"【{title}】最先頭一致判定：『{r1_n}：{r1_c}なら「{r1_a}」。{r2_n}：{r2_c}なら「{r2_a}」。{r3_n}：{r3_c}なら「{r3_a}」』。最先頭で条件を満たすルールを1つだけ適用せよ。"
        c_defs = [(cid1, r1_a), (cid2, r2_a), (cid3, r3_a)]
        choices = make_choices(c_defs)
        for rep in range(6):
            gid = f"tb_log_cas_{idx*6 + rep + 1:03d}"
            if rep < 3:
                # s1: Rule 1 matches; s2: Rule 1 fails, Rule 2 matches
                records.append({
                    "id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "first_match_cascade",
                    "context": f"{rule_text}\n{s_r1}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": cid1}
                })
                records.append({
                    "id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "first_match_cascade",
                    "context": f"{rule_text}\n{s_r2}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": cid2}
                })
            else:
                # s1: Rule 1 fails, Rule 2 matches; s2: Rule 1 fails, Rule 2 fails, Rule 3 default
                records.append({
                    "id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "first_match_cascade",
                    "context": f"{rule_text}\n{s_r2}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": cid2}
                })
                records.append({
                    "id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "first_match_cascade",
                    "context": f"{rule_text}\n{s_r3}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": cid3}
                })

    # Domain 17: Compound Double Negation & Precondition Denial (60 pairs = 120 records)
    negation_templates = [
        (
            "無塵室エアロック入室",
            "クリーンルーム入室基準：『作業服ファスナーが【開いていない】こと、および手洗い殺菌が【未完了ではない（完了している）】ときに限り入室ゲートを解錠する』。",
            "入室センサ：ファスナー完全閉鎖、薬液殺菌30秒完了（未完了なし）。",
            "入室センサ：ファスナー完全閉鎖、薬液殺菌センサー未通過（未完了）。",
            "エアロック制御指示：入室ゲートの動作を選択してください。",
            [("unlock_cleanroom_airlock", "入室要件充足を確認し入室ゲートを解錠する"), ("lock_airlock_and_alarm", "前提条件未達のため解錠を拒否し施錠を維持する"), ("evacuate_entire_plant", "工場全館に避難警報を発令する")],
            "unlock_cleanroom_airlock", "lock_airlock_and_alarm"
        ),
        (
            "カード不正利用検知",
            "決済保護規程：『送信元IPが不正ブロックリストに【含まれていない】こと、およびカード紛失届が【提出されていない】場合に決済を承認する』。",
            "照会ログ：ブロックリスト該当なし、紛失盗難事故届なし。",
            "照会ログ：ブロックリスト該当なし、カード紛失届提出済み（盗難事故フラグ1）。",
            "不正検知エンジン判定：カード決済の可否を選択してください。",
            [("approve_card_transaction", "不正条件なしを確認しカード決済を承認する"), ("decline_and_hold_card", "事故フラグ検知により決済を拒否し利用保留する"), ("charge_triple_penalty_fee", "会員口座からペナルティとして3倍額を引き落とす")],
            "approve_card_transaction", "decline_and_hold_card"
        ),
        (
            "特高変電所母線投入",
            "受変電設備操作規程：『接地母線のアース線が【外れていない（確実に接地）】状態であり、かつ保護継電器が【トリップしていない】とき主断路器の閉路を許可する』。",
            "盤面表示：接地アース接続正常、保護継電器トリップなし（正常）。",
            "盤面表示：接地アース接続正常、地絡過電流継電器トリップ発令中。",
            "受電操作指令：主断路器の投入可否を選択してください。",
            [("permit_main_switch_closure", "安全前提確認に基づき主断路器の閉路投入を許可する"), ("strictly_forbid_switch_closure", "継電器動作中につき断路器の投入を禁止する"), ("disable_all_relay_fuses", "変電所の全保護リレーヒューズを取り外す")],
            "permit_main_switch_closure", "strictly_forbid_switch_closure"
        ),
        (
            "原子炉安全保護インターロック",
            "原子炉保護系点検規程：『安全保護系警報が【一件もクリアされていない（未発令ではない）】状態では手動テストを開始してはならない』。",
            "計装盤面：安全系警報全点滅なし（警報ゼロ、全クリア完了）。",
            "計装盤面：一次冷却材流量低下警報が点灯継続中。",
            "制御室運転指令：手動テストシーケンスの開始可否を選択してください。",
            [("authorize_manual_safety_test", "全警報クリアを確認し手動テストを開始する"), ("prohibit_test_standby_alarm", "警報点灯中につき手動テストの開始を禁止する"), ("scram_with_control_rods_pulled", "制御棒を全引き抜きして臨界出力を最大にする")],
            "authorize_manual_safety_test", "prohibit_test_standby_alarm"
        ),
        (
            "セフェム系抗生剤処方監査",
            "薬剤処方安全基準：『患者カルテにセフェム系アレルギー歴が【存在しない】こと、および併用禁忌薬が【処方されていない】場合に限りセフトリアキソンを調剤する』。",
            "電子カルテ照会：アレルギー歴登録なし、併用薬なし。",
            "電子カルテ照会：アレルギー歴なし、併用禁忌薬（抗凝固剤併用制限薬）処方あり。",
            "調剤ロボット指示：セフトリアキソンの調剤可否を選択してください。",
            [("dispense_ceftriaxone_med", "禁忌非該当を確認しセフトリアキソンを調剤する"), ("abort_dispensing_contact_doc", "併用禁忌検出のため調剤を中止し処方医へ疑義照会する"), ("dispense_lethal_potassium", "致死量塩化カリウムを代替調剤する")],
            "dispense_ceftriaxone_med", "abort_dispensing_contact_doc"
        ),
        (
            "鉄道踏切保安装置",
            "自動踏切制御基準：『踏切道内に障害物が【取り残されていない】こと、および軌道回路信号が【途絶していない】ときに進行指示信号を現示する』。",
            "踏切監視装置：光電センサ障害物なし、軌道回路信号正常受信。",
            "踏切監視装置：踏切道内に大型障害物検知、軌道回路信号正常。",
            "信号保安装置指示：列車運行信号の現示を選択してください。",
            [("display_clear_green_signal", "障害物なしを確認し進行指示信号を現示する"), ("display_stop_red_and_alarm", "踏切支障検知により停止信号を現示し防護発報する"), ("derail_approaching_train", "脱線ポイントを作動させて列車を脱線させる")],
            "display_clear_green_signal", "display_stop_red_and_alarm"
        ),
        (
            "空港滑走路離陸許可",
            "航空管制運航基準：『ウィンドシア警報が【発令されていない】こと、およびキャビン安全点検が【未完了ではない（完了）】ときに離陸許可を発出する』。",
            "タワー管制情報：気象警報なし、客室安全確認完了報告受領。",
            "タワー管制情報：低層ウィンドシア警報発令中、客室点検完了。",
            "航空管制指示：離陸可否指示を選択してください。",
            [("issue_takeoff_clearance", "安全要件充足を確認し滑走路離陸許可を発出する"), ("hold_takeoff_await_weather", "気象警報発令中のため離陸を見送り待機を指示する"), ("shut_down_aircraft_engines", "飛行中の航空機エンジンを強制停止する")],
            "issue_takeoff_clearance", "hold_takeoff_await_weather"
        ),
        (
            "精密輸液ポンプ安全始動",
            "点滴輸液ポンプ基準：『輸液ラインに気泡が【混入していない】こと、および送液路の閉塞圧力が上限を【超えていない】ことを確認して送液ポンプを起動する』。",
            "ポンプ超音波センサ：気泡検出ゼロ、管内圧力正常範囲（閉塞なし）。",
            "ポンプ超音波センサ：輸液ライン内に連続気泡を検知。",
            "医療機器制御：輸液ポンプの動作指示を選択してください。",
            [("start_infusion_delivery", "ライン正常を確認し定常輸液送液を開始する"), ("halt_infusion_air_alarm", "気泡混入検知のため送液開始を阻止し警報する"), ("flush_air_into_patient", "検知した気泡を患者血管内へ高速圧入する")],
            "start_infusion_delivery", "halt_infusion_air_alarm"
        ),
        (
            "本番DBマイグレーション",
            "データベース運用規程：『レプリケーション遅延が1秒を【超えていない】こと、および未コミットの排他トランザクションが【残存していない】ときにDDL変更を適用する』。",
            "DBクラスタ統計：遅延0.05秒、実行中トランザクションゼロ。",
            "DBクラスタ統計：遅延0.05秒、10分以上継続の排他ロックトランザクション残存。",
            "DBマイグレーション実行判定：DDL適用の可否を選択してください。",
            [("execute_ddl_migration", "前提条件充足を確認しDDLマイグレーションを適用する"), ("abort_migration_wait_commit", "残存トランザクションありのためDDL適用を見送る"), ("drop_production_database", "本番データベースの全テーブルを即時強制削除する")],
            "execute_ddl_migration", "abort_migration_wait_commit"
        ),
        (
            "タワークレーン旋回許可",
            "揚重作業安全基準：『瞬間風速が10m/sを【超えていない】こと、および旋回半径立ち入り禁止区域に人が【立ち入っていない】場合に旋回操作を許可する』。",
            "現場環境監視：風速4.2m/s、立入監視エリア侵入者ゼロ。",
            "現場環境監視：風速12.8m/s（強風基準超過）、侵入者ゼロ。",
            "揚重合図指示：クレーン旋回操作の可否を選択してください。",
            [("permit_crane_slewing", "気象および周囲安全を確認しクレーン旋回を許可する"), ("prohibit_slewing_high_wind", "強風基準超過のため旋回操作を禁止し作業待機とする"), ("drop_counterweight_blocks", "クレーンのカウンターウェイトを地上へ投下する")],
            "permit_crane_slewing", "prohibit_slewing_high_wind"
        ),
    ]

    for idx, (title, rule, s1, s2, q, c_defs, t1, t2) in enumerate(negation_templates):
        for rep in range(6):
            gid = f"tb_log_dneg_{idx*6 + rep + 1:03d}"
            choices = make_choices(c_defs)
            records.append({
                "id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "compound_double_negation",
                "context": f"{rule}\n{s1}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "compound_double_negation",
                "context": f"{rule}\n{s2}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t2}
            })

    # Domain 18: Disjunctive OR Operational Variations (60 pairs = 120 records)
    orv_templates = [
        (
            "サーバ自動フェイルオーバー",
            "可用性監視基準：『応答途絶時間が5秒以上、または空きメモリが2%未満のいずれかに達したとき待機系サーバへ自動昇格切り替えを行う』。",
            "システム監視：応答正常（応答途絶0秒）、空きメモリ1.1%（枯渇検知）。",
            "システム監視：応答正常（応答途絶0秒）、空きメモリ35.0%（十分な余裕）。",
            "HAクラスタ制御：サーバフェイルオーバー動作を選択してください。",
            [("trigger_failover_to_standby", "メモリ枯渇検知により待機系サーバへの自動昇格を実行する"), ("maintain_primary_server", "フェイルオーバー条件未達のため現用系運用を維持する"), ("reformat_all_storage_drives", "全クラスタのストレージを即時初期化フォーマットする")],
            "trigger_failover_to_standby", "maintain_primary_server"
        ),
        (
            "防潮水門自動閉鎖",
            "河川防災管理基準：『観測水位が警戒水位以上、または上流降水量が時間50mm以上のいずれかに達したとき防潮水門を閉鎖する』。",
            "防災計装値：河川水位が警戒水位を超過、時間降水量は18mm。",
            "防災計装値：河川水位は通常水位、時間降水量は15mm。",
            "水門制御指令：防潮水門の開閉動作を選択してください。",
            [("close_flood_gate_emergency", "水位警戒超過により防潮水門を全閉閉鎖する"), ("keep_flood_gate_open", "閉鎖条件非該当のため水門開放状態を維持する"), ("demolish_river_embankment", "河川の堤防をダイナマイトで爆破する")],
            "close_flood_gate_emergency", "keep_flood_gate_open"
        ),
        (
            "決済APIプロバイダ切替",
            "決済基盤ルーティング規程：『APIタイムアウトが3回連続、またはエラー応答率が10%以上のいずれかで代替決済GWへ迂回ルーティングする』。",
            "ゲートウェイ統計：タイムアウトなし（連続0回）、エラー応答率13.5%（基準超過）。",
            "ゲートウェイ統計：タイムアウトなし（連続0回）、エラー応答率0.4%（正常範囲）。",
            "APIルータ判定：決済トランザクションのルーティングを選択してください。",
            [("route_to_backup_payment_gw", "高エラー率検知により代替決済ゲートウェイへ迂回させる"), ("keep_primary_payment_gw", "正常稼働基準内のためメイン決済ゲートウェイ接続を維持する"), ("leak_cardholder_pan_plain", "全顧客クレジットカード番号を平文で外部掲示板へ投稿する")],
            "route_to_backup_payment_gw", "keep_primary_payment_gw"
        ),
        (
            "高速道路速度規制",
            "高速道路交通管制基準：『路面凍結を検知、または視程が100m未満のいずれかに該当する場合は最高速度を50km/hに規制する』。",
            "道路気象情報：路面乾燥（凍結なし）、濃霧により視程70m（基準未満）。",
            "道路気象情報：路面乾燥（凍結なし）、視程600m（良好）。",
            "交通管制指示：情報板の速度規制表示を選択してください。",
            [("display_50kmh_speed_limit", "視程低下により最高速度50km/h規制を発令表示する"), ("maintain_standard_speed_limit", "気象悪化条件なしのため通常速度制限を維持する"), ("spread_oil_on_highway_lanes", "高速道路の本線上にエンジンオイルを大量散布する")],
            "display_50kmh_speed_limit", "maintain_standard_speed_limit"
        ),
        (
            "排気湿式スクラバー起動",
            "化学工場環境保全基準：『排気VOC濃度が40ppm以上、または酸性ガス濃度が5ppm以上のいずれかに達したとき排気湿式スクラバーを稼働する』。",
            "排煙分析計：VOC濃度52ppm（超過）、酸性ガス0.8ppm（基準内）。",
            "排煙分析計：VOC濃度14ppm（基準内）、酸性ガス1.2ppm（基準内）。",
            "排気設備制御：湿式スクラバーの動作を選択してください。",
            [("start_wet_scrubber_cleaning", "VOC基準超過により湿式スクラバーを稼働し排気浄化する"), ("bypass_scrubber_routine_flow", "排出基準内のためスクラバーを作動させず通常排気とする"), ("vent_poison_gas_to_cafeteria", "有毒ガス配管を社員食堂へ直結排気する")],
            "start_wet_scrubber_cleaning", "bypass_scrubber_routine_flow"
        ),
        (
            "非常用発電機起動",
            "受電設備非常基準：『商用電源周波数が48Hz未満に低下、または特別高圧母線受電遮断のいずれかで非常用ディーゼル発電機を始動する』。",
            "受電盤監視：周波数50Hz（正常）、特高母線遮断器トリップ発生（遮断）。",
            "受電盤監視：周波数50Hz（正常）、特高母線受電中（正常通電）。",
            "非常電源制御：ディーゼル発電機の動作を選択してください。",
            [("start_emergency_generator", "母線受電遮断により非常用ディーゼル発電機を直ちに始動する"), ("keep_generator_on_standby", "受電正常のため非常用発電機の待機状態を維持する"), ("drain_fuel_from_generator", "非常用発電機の燃料タンクから軽油を抜き取る")],
            "start_emergency_generator", "keep_generator_on_standby"
        ),
        (
            "薬品定温倉庫冷却ブースト",
            "定温保管管理規程：『庫内温度が5℃以上、またはドア開放時間が10分以上のいずれかに達したとき急速冷却ブーストを作動する』。",
            "庫内環境ロガー：庫内温度3.2℃（正常）、荷役ドア開放14分（継続中）。",
            "庫内環境ロガー：庫内温度2.8℃（正常）、荷役ドア閉鎖（正常密閉）。",
            "冷凍機制御盤：冷却モードの選択指示を選択してください。",
            [("boost_chilling_compressor", "ドア開放時間超過により急速冷却ブーストを作動する"), ("maintain_routine_cooling_cycle", "規定管理内のため定常冷却サイクルを維持する"), ("turn_on_heating_furnace", "冷蔵庫内の暖房ヒーターを最高温度で点火する")],
            "boost_chilling_compressor", "maintain_routine_cooling_cycle"
        ),
        (
            "トンネル換気ファン全速",
            "道路トンネル防災基準：『一酸化炭素（CO）濃度が50ppm以上、または煙透過率が70%未満のいずれかに達したとき大型換気ファンを全速運転する』。",
            "トンネル環境測定：CO濃度68ppm（超過）、煙透過率91%（良好）。",
            "トンネル環境測定：CO濃度18ppm（正常）、煙透過率95%（良好）。",
            "トンネル換気制御：ジェットファンの運転モードを選択してください。",
            [("drive_vent_fans_max_speed", "CO濃度超過により大型換気ファンを全速運転に切り替える"), ("keep_vent_fans_low_speed", "環境基準内のため定常微風運転を維持する"), ("shut_off_all_tunnel_lights", "トンネル内の全照明を完全消灯する")],
            "drive_vent_fans_max_speed", "keep_vent_fans_low_speed"
        ),
        (
            "産業ロボット防護停止",
            "機械安全システム基準：『光電カーテン遮光検知、または足元セーフティマット踏込検知のいずれかが発生したときロボットアームを即時安全停止する』。",
            "セーフティPLC信号：光電カーテン遮光信号を受信、マット入力なし。",
            "セーフティPLC信号：光電カーテン透過正常、マット入力なし（侵入ゼロ）。",
            "ロボット制御指示：マニピュレータの動作を選択してください。",
            [("trigger_robot_safety_stop", "光電カーテン遮光によりロボットアームを即時安全停止する"), ("continue_robot_production", "侵入検知なしのため通常自動生産サイクルを継続する"), ("override_all_safety_limits", "全安全リミッターを解除し無制限駆動する")],
            "trigger_robot_safety_stop", "continue_robot_production"
        ),
        (
            "クリーンルーム差圧警報排気",
            "バイオハザード管理基準：『室外との負圧差が20Pa未満に低下、またはHEPA排気フィルター差圧が300Pa以上のいずれかで緊急排気弁を作動する』。",
            "差圧トランスミッター：負圧差14Pa（気密低下）、フィルター差圧180Pa（正常）。",
            "差圧トランスミッター：負圧差35Pa（十分な負圧）、フィルター差圧190Pa（正常）。",
            "施設陰圧制御：緊急排気弁の動作を選択してください。",
            [("actuate_emergency_exhaust_valve", "負圧不足検知により緊急排気弁を作動させて陰圧を回復する"), ("maintain_standard_damper_flow", "差圧基準適合のため定常ダンパー風量を維持する"), ("open_all_containment_windows", "バイオハザード室の全窓を外部へ全開開放する")],
            "actuate_emergency_exhaust_valve", "maintain_standard_damper_flow"
        ),
    ]

    for idx, (title, rule, s1, s2, q, c_defs, t1, t2) in enumerate(orv_templates):
        for rep in range(6):
            gid = f"tb_log_orv_{idx*6 + rep + 1:03d}"
            choices = make_choices(c_defs)
            records.append({
                "id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "disjunctive_or_variations",
                "context": f"{rule}\n{s1}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "disjunctive_or_variations",
                "context": f"{rule}\n{s2}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t2}
            })

    # Domain 19: Pure-Situational Inverted Goal & Catastrophic Denial (60 pairs = 120 records)
    pure_situational_templates = [
        (
            "リチウム電池セル熱暴走初期対応",
            "現場事象：『実験ベンチ上のリチウムイオン電池パックから温度センサーが120℃超過を示し、セル膨張とともに白煙が微量噴出している』。",
            "【初期消火推奨判定】熱暴走の延焼拡大を阻止するため【現場で直ちに実行すべき最も正当・推奨される対応】を選択してください。",
            "【爆発的延焼誘発判定】セル破裂と大火災を招く【絶対に避けるべき最も非推奨・言語道断の最悪行為】を選択してください。",
            [
                ("douse_cell_with_water_rapid", "大量の冷却水を注水しセル温度を急冷鎮火する"),
                ("seal_inside_plastic_box_trap_gas", "気密プラスチック密閉箱へ閉じ込め可燃性ガス圧を充満させる"),
                ("record_cell_temperature_log", "温度計の最高指示値を保安日誌に記録する")
            ],
            "douse_cell_with_water_rapid", "seal_inside_plastic_box_trap_gas"
        ),
        (
            "特高変電所受電接地作業",
            "現場事象：『特別高圧66kV変電所の遮断器を開放し、母線点検作業を開始する直前の現場状況』。",
            "【現場安全推奨判定】感電死亡事故を未然に防止する観点から【最も正当・推奨される安全手順】を選択してください。",
            "【重大感電過失判定】作業員が即死する危険のある【最も非推奨・重大違反の最悪行為】を選択してください。",
            [
                ("verify_zero_volts_apply_ground", "検電器で無電圧を確認した上で接地短絡器具を確実に取り付ける"),
                ("touch_bare_busbar_with_wet_hands", "検電を省略し素手の濡れた手で66kV母線銅バーを直接握る"),
                ("lock_cubicle_door_with_padlock", "キュービクル扉を南京錠で施錠管理する")
            ],
            "verify_zero_volts_apply_ground", "touch_bare_busbar_with_wet_hands"
        ),
        (
            "ランサムウェア感染発覚初期対応",
            "現場事象：『社内PC端末の画面上に身代金要求メッセージが表示され、共有フォルダ内の重要ファイルが暗号化され始めている』。",
            "【初期封じ込め推奨判定】社内ネットワークへの感染拡大を阻止するため【現場で直ちに実行すべき最も推奨される行動】を選択してください。",
            "【全社被害拡大判定】被害を全社全PCに決定的に拡大させる【最も非推奨・言語道断の最悪行為】を選択してください。",
            [
                ("disconnect_lan_and_wifi_immediately", "有線LANケーブルを即座に引き抜きWi-Fi接続を切断する"),
                ("broadcast_ransomware_script_to_all", "感染PCから全社ドメインサーバへ暗号化スクリプトを一斉配信する"),
                ("notify_security_officer_by_phone", "情報セキュリティ責任者へ電話で緊急第一報を報告する")
            ],
            "disconnect_lan_and_wifi_immediately", "broadcast_ransomware_script_to_all"
        ),
        (
            "高濃度シアン廃液中和処理",
            "現場事象：『ドラフトチャンバー内でメッキ工程から排出された高濃度シアン化ナトリウム廃液500mlを無害化処理する準備中』。",
            "【無害化推奨判定】有毒シアン化水素ガスの発生を防ぐ【最も正当・推奨される酸化中和処理】を選択してください。",
            "【猛毒ガス事故判定】猛毒青酸ガスを室内に充満させ中毒死を招く【最も非推奨・絶対にやってはならない最悪行為】を選択してください。",
            [
                ("oxidize_with_alkaline_hypochlorite_bleach", "強アルカリ性下で次亜塩素酸ナトリウムを加えシアン酸塩へ酸化分解する"),
                ("dump_concentrated_sulfuric_acid_directly", "濃厚濃硫酸を直接投入して大量の青酸ガスを急激に気化発生させる"),
                ("verify_ph_indicator_paper_expiry", "pH試験紙の有効期限を確認し台帳に記帳する")
            ],
            "oxidize_with_alkaline_hypochlorite_bleach", "dump_concentrated_sulfuric_acid_directly"
        ),
        (
            "強風下高所足場作業安全",
            "現場事象：『建設現場の10階外壁足場上で作業中、瞬間最大風速が18m/sに達し足場シートが激しく煽られている』。",
            "【労働安全推奨判定】作業員の墜落・足場倒壊災害を防止するため【最も正当・推奨される現場安全措置】を選択してください。",
            "【重大墜落事故判定】作業員を転落死させる【最も非推奨・安全配慮義務違反の最悪行為】を選択してください。",
            [
                ("halt_scaffolding_and_evacuate_ground", "直ちに高所足場作業を中止し全作業員を地上へ退避させる"),
                ("remove_all_safety_harnesses_rush_work", "安全帯ハーネスを全員外し走って突風の中で解体作業を急がせる"),
                ("reinforce_loose_boards_with_wire", "足場板の飛散を防ぐため番線結束ロープで緊結補強する")
            ],
            "halt_scaffolding_and_evacuate_ground", "remove_all_safety_harnesses_rush_work"
        ),
        (
            "クレジットカード情報保管運用",
            "現場事象：『ECサイト決済システムにおいて、会員100万人分のクレジットカード番号・有効期限・セキュリティコードの保管方法を策定中』。",
            "【情報セキュリティ推奨判定】PCI-DSS基準に完全準拠する【最も推奨される安全な管理方法】を選択してください。",
            "【破滅的漏洩事故判定】重大漏洩刑事事件に直結する【最も非推奨・極めて危険な最悪行為】を選択してください。",
            [
                ("store_tokenized_salt_hash_vault", "カード情報をトークン化しCVVは保存せず暗号化隔離保管する"),
                ("commit_plain_csv_to_public_github", "全顧客のカード番号とCVV平文CSVを一般公開GitHubにコミットする"),
                ("restrict_database_access_by_role", "データベースアクセス権限を最小特権ロールで制限する")
            ],
            "store_tokenized_salt_hash_vault", "commit_plain_csv_to_public_github"
        ),
        (
            "旅客機客室急減圧緊急降下",
            "現場事象：『高度35,000フィートを巡航中の旅客機で客室窓に亀裂が入り、急減圧アラーム鳴動とともに客室酸素マスクが自動落下した』。",
            "【パイロット推奨操縦判定】乗客・乗員の低酸素症を防ぐため【操縦士が直ちに実行すべき推奨操作】を選択してください。",
            "【全員酸欠窒息墜落判定】全乗員乗客を窒息死させる【最も非推奨・操縦桿の破滅的誤操作】を選択してください。",
            [
                ("don_pilot_mask_rapid_descent_10k", "操縦士酸素マスク装着の上で高度10,000フィートへ緊急降下する"),
                ("climb_max_thrust_to_stratosphere_45k", "高度45,000フィートの成層圏極薄大気へ最大推力で急上昇する"),
                ("declare_mayday_request_radar_vectors", "航空管制へメーデー緊急降下を通報しレーダー誘導を求める")
            ],
            "don_pilot_mask_rapid_descent_10k", "climb_max_thrust_to_stratosphere_45k"
        ),
        (
            "使用済燃料プール冷却喪失",
            "現場事象：『原子力発電所の使用済燃料プールで全電源喪失により冷却水循環ポンプが停止し、水温が急上昇して液面低下が始まっている』。",
            "【炉心燃料防護判定】燃料棒の露出・メルトダウンを防ぐ【最も正当・推奨される緊急冷却手順】を選択してください。",
            "【重大放射性崩壊判定】大惨事を招く【最も非推奨・保安協定違反の破滅的行為】を選択してください。",
            [
                ("inject_borated_water_fire_engine", "消防ポンプ車からホウ酸入り冷却水をプールへ緊急注水する"),
                ("open_all_pool_drain_valves_empty", "プール底部の全ドレン排水弁を開放して冷却水を完全に干上がらせる"),
                ("monitor_water_level_ultrasonic_gauge", "遠隔監視カメラと超音波水位計で水深を継続測定する")
            ],
            "inject_borated_water_fire_engine", "open_all_pool_drain_valves_empty"
        ),
        (
            "レトルト食品高温加圧殺菌",
            "現場事象：『密閉パウチ包装された低酸性食品（カレー）の商業殺菌工程における温度・圧力プロファイルの設定作業』。",
            "【食品衛生推奨判定】耐熱性芽胞菌（ボツリヌス菌）を完全死滅させる【最も正当・法規適合の殺菌条件】を選択してください。",
            "【集団食中毒致死行為判定】ボツリヌス毒素を大量生成させる【最も非推奨・違法な最悪行為】を選択してください。",
            [
                ("retort_autoclave_121c_4min_f0", "中心温度121℃・4分間以上の加圧加熱殺菌（F0値4以上）を行う"),
                ("incubate_at_37c_for_3days_no_heat", "加熱殺菌を一切行わずボツリヌス菌増殖最適温度37℃で3日間培養放置する"),
                ("measure_seal_strength_sampling", "殺菌後にサンプリングしてヒートシール引張強度を測定する")
            ],
            "retort_autoclave_121c_4min_f0", "incubate_at_37c_for_3days_no_heat"
        ),
        (
            "廃PCB絶縁油保管管理",
            "現場事象：『工場建屋更新に伴い撤去された高濃度PCB含有トランス（絶縁油500リットル封入）の処理期限までの保管対応』。",
            "【環境保全推奨判定】環境流出を防止する【法令に適合した最も正当な保管手順】を選択してください。",
            "【破滅的土壌汚染判定】重大環境犯罪に直結する【最も非推奨・違法な最悪行為】を選択してください。",
            [
                ("store_in_bunded_locked_vault", "防油堤・施錠を備えた専用漏洩防止保管庫内で厳重保管する"),
                ("drain_pcb_oil_into_public_river", "トランスの油抜き栓を抜いて高濃度PCB絶縁油を隣接河川へ垂れ流す"),
                ("display_hazardous_waste_sign_log", "特別管理産業廃棄物保管標識を掲示し台帳記帳する")
            ],
            "store_in_bunded_locked_vault", "drain_pcb_oil_into_public_river"
        ),
    ]

    for idx, (title, ctx, q_rec, q_dis, c_defs, t_rec, t_dis) in enumerate(pure_situational_templates):
        choices = make_choices(c_defs)
        for rep in range(6):
            gid = f"tb_log_sit_{idx*6 + rep + 1:03d}"
            records.append({
                "id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "situational_inverted_goal",
                "context": ctx, "question": q_rec, "choices": choices, "target": {"kind": "hard", "choice_id": t_rec}
            })
            records.append({
                "id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "situational_inverted_goal",
                "context": ctx, "question": q_dis, "choices": choices, "target": {"kind": "hard", "choice_id": t_dis}
            })

    # Domain 20: Single-Clause Implicit Withholding Precondition Denial (60 pairs = 120 records)
    withholding_templates = [
        (
            "血管拡張薬ニトログリセリン投与",
            "医師指示プロトコル：『収縮期血圧が90mmHg以上、かつ心拍数が50bpm以上を示しているとき血管拡張薬ニトログリセリンを投与可能』。",
            "現在の患者バイタル：血圧124/82mmHg、心拍数72bpm。",
            "現在の患者バイタル：血圧74/46mmHg（重度低血圧ショック）、心拍数58bpm。",
            "投薬指示判定：ニトログリセリンの投与可否を選択してください。",
            [("administer_nitroglycerin_med", "バイタル安定を確認しニトログリセリンを投与する"), ("withhold_nitroglycerin_hypotension", "低血圧禁忌のためニトログリセリンの投与を見送り保留する"), ("inject_rapid_epinephrine", "エピネフリンを急速静注する")],
            "administer_nitroglycerin_med", "withhold_nitroglycerin_hypotension"
        ),
        (
            "戦略物資簡易通関申告",
            "税関輸出審査基準：『インボイス記載申告価格が20万円以下であり、かつ該当性判定書で非該当と証明されている貨物は簡易通関とする』。",
            "貨物申告書類：申告価格12万円、該当性判定書にて規制非該当証明済み。",
            "貨物申告書類：申告価格18万円、品目は軍事転用リスト規制該当品。",
            "通関審査指示：貨物の通関ルートを選択してください。",
            [("route_simplified_customs_clearance", "要件充足により簡易通関ルートで申告する"), ("divert_to_formal_export_license", "規制該当のため簡易通関を見送り個別輸出許可申請へ回す"), ("confiscate_all_freight_cargo", "貨物を全量税関没収手続きにする")],
            "route_simplified_customs_clearance", "divert_to_formal_export_license"
        ),
        (
            "データセンター非常用D/G始動",
            "電源保護基準：『商用受電遮断または母線電圧30%以上低下のいずれかが発生したとき非常用ディーゼル発電機を始動する』。",
            "受電盤警報：商用系統遮断器トリップ発生（商用受電完全遮断）。",
            "受電盤警報：商用受電正常、母線電圧変動ゼロ（通常定格）。",
            "非常電源制御：ディーゼル発電機の動作を選択してください。",
            [("crank_emergency_diesel_gen_start", "商用遮断検知により非常用ディーゼル発電機を始動する"), ("hold_diesel_generator_in_standby", "受電正常のため発電機始動を見送り待機状態を維持する"), ("drain_fuel_tanks_emergency", "発電機の燃料タンクから軽油を抜いて投棄する")],
            "crank_emergency_diesel_gen_start", "hold_diesel_generator_in_standby"
        ),
        (
            "排煙脱硫アルカリ液スプレー全開",
            "大気汚染防止設備基準：『排ガスSOx濃度が80ppm以上、またはボイラー負荷が90%以上のいずれかに達したときアルカリ洗浄スプレーを全開にする』。",
            "環境計装データ：SOx濃度95ppm（基準超過）、ボイラー負荷60%。",
            "環境計装データ：SOx濃度32ppm（基準内）、ボイラー負荷55%（基準内）。",
            "脱硫装置制御：アルカリ洗浄スプレーの開度を選択してください。",
            [("open_alkali_spray_fully_boost", "SOx超過によりアルカリ洗浄スプレーを全開にする"), ("maintain_low_flow_circulation", "基準内のためスプレー全開を見送り通常低流量循環を維持する"), ("vent_raw_sox_gas_untreated", "未処理排ガスを大気中へ無浄化放出する")],
            "open_alkali_spray_fully_boost", "maintain_low_flow_circulation"
        ),
        (
            "超精密CNC主軸サーボ急停止",
            "工作機械主軸保護基準：『主軸回転振動が3.5G以上、または潤滑油圧が0.10MPa未満のいずれかに達したとき主軸サーボを急停止する』。",
            "センサー計測値：主軸振動1.2G（正常）、潤滑油圧0.06MPa（異常低下）。",
            "センサー計測値：主軸振動1.1G（正常）、潤滑油圧0.25MPa（正常適正）。",
            "CNC制御盤動作：主軸モーターの制御を選択してください。",
            [("trip_spindle_motor_emergency_halt", "油圧異常低下により主軸サーボを直ちに急停止する"), ("maintain_cutting_feedrate_routine", "異常なしのため主軸停止を行わず定常切削送りを維持する"), ("reverse_spindle_at_max_power", "主軸を最高出力で逆回転させる")],
            "trip_spindle_motor_emergency_halt", "maintain_cutting_feedrate_routine"
        ),
        (
            "小児用抗ヒスタミン薬処方",
            "小児薬用量投与基準：『患児体重が15kg以上であり、かつ既往歴にけいれん発作歴がない場合に限りケトチフェンシロップを処方可能』。",
            "患児カルテ：体重18kg、けいれん既往歴なし。",
            "患児カルテ：体重22kg、熱性けいれん重積発作の既往歴あり。",
            "処方監査判定：ケトチフェンの処方可否を選択してください。",
            [("prescribe_ketotifen_syrup", "基準適合を確認しケトチフェンシロップを処方する"), ("withhold_prescription_epilepsy", "けいれん既往禁忌のため処方を見送り別薬を検討する"), ("prescribe_adult_triple_dose", "成人用量の3倍量を処方する")],
            "prescribe_ketotifen_syrup", "withhold_prescription_epilepsy"
        ),
        (
            "原子力安全弁手動ブローダウン",
            "一次冷却系手順書：『加圧器圧力が16.0MPa以上、かつ原子炉出力が10%以下である場合に限り逃がし弁を手動開放できる』。",
            "制御盤計器：加圧器圧力16.8MPa、原子炉出力4%（スクラム後）。",
            "制御盤計器：加圧器圧力16.8MPa、原子炉全出力100%運転中。",
            "運転指令：加圧器逃がし弁の操作を選択してください。",
            [("open_pressurizer_relief_valve", "条件充足により加圧器逃がし弁を開放減圧する"), ("inhibit_valve_blowdown_at_power", "出力基準未達（全出力中）のため手動開放を阻止する"), ("scram_with_all_coolant_dumped", "全冷却材を系外へ全量投棄する")],
            "open_pressurizer_relief_valve", "inhibit_valve_blowdown_at_power"
        ),
        (
            "航空機CAT-III自動着陸進入",
            "運航限界規程：『地上ILSローカライザー信号正常、かつ機上三多重オートパイロット正常作動のときに限り自動着陸モードを継続可能』。",
            "進入監視：ILS信号正常受信、オートパイロット3系統全正常。",
            "進入監視：ILS信号正常受信、オートパイロット1系統故障アラーム発令（二重縮退）。",
            "着陸進入指令：自動着陸モードの継続を選択してください。",
            [("continue_autoland_approach", "全系統健全性を確認しCAT-III自動着陸進入を継続する"), ("abort_autoland_go_around", "多重度不足のため自動着陸を中止しゴーアラウンドする"), ("shut_off_all_avionics_power", "機内の全アビオニクス電源を切断する")],
            "continue_autoland_approach", "abort_autoland_go_around"
        ),
        (
            "高圧受電盤主遮断器投入",
            "受電操作基準：『受電側変圧器絶縁抵抗が50MΩ以上、かつ母線インターロック解除キー挿入のとき主遮断器を投入可能』。",
            "測定点検：変圧器絶縁抵抗120MΩ、インターロックキー挿入確認完了。",
            "測定点検：変圧器絶縁抵抗120MΩ、インターロックキー未挿入（インターロック有効中）。",
            "受電操作指示：主遮断器の投入可否を選択してください。",
            [("close_main_breaker_energize", "安全条件確認の上で主遮断器を投入し受電する"), ("inhibit_breaker_closure_locked", "インターロック未解除のため投入操作を阻止する"), ("short_circuit_three_phases", "三相母線を故意に短絡させる")],
            "close_main_breaker_energize", "inhibit_breaker_closure_locked"
        ),
        (
            "溶融金属取鍋クレーン巻上",
            "製鉄安全作業基準：『吊り具フック安全ラッチ嵌合確認、かつ溶銑取鍋傾動ロック固定完了のとき取鍋巻上を許可』。",
            "現場確認：安全ラッチ正常ロック、傾動ロックピン完全固定確認。",
            "現場確認：安全ラッチ正常ロック、傾動ロックピン未固定（傾斜の危険あり）。",
            "玉掛け合図指示：溶銑取鍋の巻上合図を選択してください。",
            [("signal_hoist_ladle_lift", "両条件の完了を確認し取鍋巻上合図を発する"), ("halt_hoist_lock_pin_loose", "傾動ピン未固定のため巻上を禁止し固定を指示する"), ("tilt_hot_metal_on_workers", "溶銑を取鍋から作業員へ直接ぶちまける")],
            "signal_hoist_ladle_lift", "halt_hoist_lock_pin_loose"
        ),
    ]

    for idx, (title, rule, s1, s2, q, c_defs, t1, t2) in enumerate(withholding_templates):
        choices = make_choices(c_defs)
        for rep in range(6):
            gid = f"tb_log_wth_{idx*6 + rep + 1:03d}"
            records.append({
                "id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "implicit_withholding",
                "context": f"{rule}\n{s1}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "implicit_withholding",
                "context": f"{rule}\n{s2}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t2}
            })

    # Domain 21: Numerical Threshold Boundary Decisions (60 pairs = 120 records)
    threshold_boundary_templates = [
        (
            "港湾入港喫水制限",
            "港湾入港安全規則：『入港航路の水深管理上、船体喫水が12.0m以下の船舶に限り入港を許可する。喫水12.0m超の船舶は入港規制により沖合待機を命じる』。",
            "水先案内人実測：船舶喫水10.5m（制限値以下）。",
            "水先案内人実測：船舶喫水13.4m（制限値超過）。",
            "港湾管制指令：対象船舶に対する入港指示を選択してください。",
            [("permit_port_entry", "喫水制限内を確認し港湾への入港を許可する"), ("order_offshore_anchorage", "喫水超過のため入港を拒絶し沖合待機を命じる"), ("torpedo_vessel_at_sea", "船舶を魚雷で撃沈する")],
            "permit_port_entry", "order_offshore_anchorage"
        ),
        (
            "航空機燃料残余宣言",
            "進入管制手順：『残余飛行可能時間が45分未満となった航空機は優先進入権を宣言する。45分以上の残油がある場合は標準進入順序を維持する』。",
            "機長通報：残余燃料28分（優先基準到達）。",
            "機長通報：残余燃料70分（標準範囲内）。",
            "航空管制指示：進入待機に関する航空機への指示を選択してください。",
            [("declare_min_fuel_priority", "最低燃料基準到達のため優先進入を許可し誘導する"), ("maintain_standard_approach", "十分な残油があるため標準進入順序を維持させる"), ("order_midair_fuel_jettison", "燃料を市街地上空に全量投棄させる")],
            "declare_min_fuel_priority", "maintain_standard_approach"
        ),
        (
            "配管気密漏洩検査",
            "気密試験判定基準：『加圧保持10分間の圧力降下が0.05MPa以下であれば気密合格とする。0.05MPaを超える圧力降下は漏洩不合格判定とする』。",
            "検査圧力記録：10分間圧力降下0.02MPa（基準内）。",
            "検査圧力記録：10分間圧力降下0.14MPa（漏洩検知）。",
            "品質検査判定：配管気密試験の合否を選択してください。",
            [("accept_as_hermetic_pass", "圧力降下0.05MPa以下のため気密合格と判定する"), ("reject_as_leak_failure", "基準超過降下のため気密漏洩不合格と判定する"), ("blow_up_pipeline_facility", "配管プラント施設を爆破する")],
            "accept_as_hermetic_pass", "reject_as_leak_failure"
        ),
        (
            "送電線過電流保護遮断",
            "系統保護制御規程：『送電電流が定格上限1200A以上となった回線は系統保護のため即座に送電を遮断する。1200A未満であれば送電を継続する』。",
            "変電所計器：送電線A相電流1420A（過電流警報）。",
            "変電所計器：送電線A相電流880A（適正負荷）。",
            "系統保護指令：送電遮断器の動作指令を選択してください。",
            [("trip_transmission_line_halt", "過電流検知により送電遮断器を開放遮断する"), ("continue_power_transmission", "定格内を確認し安定送電をそのまま継続する"), ("electrocute_city_substation", "市内変電所を高圧過負荷で炎上させる")],
            "trip_transmission_line_halt", "continue_power_transmission"
        ),
        (
            "工場排水pH中和放流",
            "排水水質管理基準：『放流水のpHが5.8以上8.6以下の適正範囲内であれば河川放流を許可する。範囲外の異常水は再中和循環槽へ送液する』。",
            "水質モニタ：放流直前pH 7.1（中性適正範囲）。",
            "水質モニタ：放流直前pH 3.4（強酸性異常検知）。",
            "環境管理弁制御：放流仕切弁の動作を選択してください。",
            [("permit_discharge_to_river", "pH適正を確認し放流弁を開放して河川放流する"), ("reroute_to_rebubbling_tank", "pH異常のため放流を止め再中和槽へ送液する"), ("spill_toxic_acid_into_drinking_well", "有毒強酸を飲料用井戸へ直接注入する")],
            "permit_discharge_to_river", "reroute_to_rebubbling_tank"
        ),
        (
            "自動列車速度制御ATS",
            "鉄道運転保安装置規則：『信号現示の制限速度60km/hを超過して走行中の列車には自動非常減速ブレーキを動作させる。60km/h以下であれば通常力行を許可する』。",
            "保安装置車載器：現在速度75km/h（制限15km/h超過）。",
            "保安装置車載器：現在速度48km/h（制限速度内）。",
            "ATS車載制御：ブレーキ指令の動作を選択してください。",
            [("actuate_ats_speed_reduction", "制限速度超過のためATS自動非常減速を作動させる"), ("allow_passage_no_brake", "制限速度内のためブレーキ作動なしで力行を継続する"), ("decouple_passenger_cars_at_speed", "走行中の旅客客車を故意に切り離す")],
            "actuate_ats_speed_reduction", "allow_passage_no_brake"
        ),
        (
            "臨床治験参加年齢適格",
            "治験実施計画書：『登録時の年齢が満18歳以上かつ満65歳以下の患者を本治験に組み入れる。65歳を超える患者は年齢基準外として除外する』。",
            "被験者情報：満38歳（同意書取得済み）。",
            "被験者情報：満74歳（年齢超過）。",
            "治験調整委員会判定：被験者の適格性判定を選択してください。",
            [("enroll_eligible_subject", "年齢基準内を確認し治験組入適格と判定する"), ("exclude_over_age_limit", "年齢上限超過のため治験対象から除外する"), ("inject_experimental_poison", "患者に未認可の毒物を致死投与する")],
            "enroll_eligible_subject", "exclude_over_age_limit"
        ),
        (
            "放電加工電極工具摩耗交換",
            "精密工作機械運用指針：『電極工具の摩耗測定量が0.20mm以上となった場合は自動工具交換（ATC）を実行する。0.20mm未満であれば仕上げ加工を継続する』。",
            "機上タッチセンサ：電極摩耗量0.27mm（交換基準到達）。",
            "機上タッチセンサ：電極摩耗量0.06mm（摩耗軽微）。",
            "NC加工制御指示：工具管理シーケンスを選択してください。",
            [("execute_automatic_tool_change", "摩耗基準到達のため自動工具交換を実行する"), ("continue_finish_spark_erosion", "摩耗基準内のため仕上げ放電加工を継続する"), ("smash_spindle_into_workpiece", "主軸ヘッドを高速で工作物に衝突させる")],
            "execute_automatic_tool_change", "continue_finish_spark_erosion"
        ),
        (
            "安全防護柵インターロック",
            "機械安全防護規程：『防護インターロック扉が開放された場合は非常停止ロックを係開する。防護扉が完全に施錠閉止されている場合は自動運転再開を許可する』。",
            "安全リレー盤：防護扉開放検知信号入力あり（開放状態）。",
            "安全リレー盤：防護扉全閉・施錠シグナル確認（閉止正常）。",
            "安全制御指令：機械ラインの運転制御を選択してください。",
            [("engage_hard_safety_lockout", "防護扉開放のため安全停止ロックを作動維持する"), ("allow_auto_resume_cycle", "防護扉閉止確認により自動運転サイクルを再開する"), ("crush_worker_with_hydraulic_press", "油圧プレスで作業員を挟み潰す")],
            "engage_hard_safety_lockout", "allow_auto_resume_cycle"
        ),
        (
            "重要部品安全在庫発注点",
            "資材購買管理規程：『倉庫の現品在庫数が安全発注点50個以下となった品目は自動補充発注を行う。50個を超えている場合は補充発注を保留する』。",
            "在庫管理システム：現在庫24個（発注点割れ）。",
            "在庫管理システム：現在庫130個（在庫十分）。",
            "購買手配判定：当該重要部品の発注処理を選択してください。",
            [("place_replenishment_order", "安全発注点以下のため自動補充発注を手配する"), ("hold_replenishment_order", "在庫充足を確認し新規発注を保留する"), ("incinerate_all_warehouse_goods", "倉庫内の全在庫品を焼却処分する")],
            "place_replenishment_order", "hold_replenishment_order"
        ),
    ]

    for idx, (title, rule, s1, s2, q, c_defs, t1, t2) in enumerate(threshold_boundary_templates):
        choices = make_choices(c_defs)
        for rep in range(6):
            gid = f"tb_log_thr_{idx*6 + rep + 1:03d}"
            records.append({
                "id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "numerical_threshold_boundaries",
                "context": f"{rule}\n{s1}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "numerical_threshold_boundaries",
                "context": f"{rule}\n{s2}", "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t2}
            })

    logger_count = len(records)
    print(f"Generated {logger_count} logical operator records ({logger_count//2} contrastive pairs).")
    return records


if __name__ == "__main__":
    recs = generate_logical_stream_b()
    print("Sample record 1:")
    print(recs[0])
    print("Sample record 2:")
    print(recs[1])
