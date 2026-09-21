"""RC3 Training Data Synthesis: Logical Operators and Propositional Reasoning.

Generates 300 contrastive groups (600 records) across 10 logical subdomains:
1. NOT Negation & Exclusion (30 groups = 60 records)
2. Biconditional with Fallback (30 groups = 60 records)
3. Multi-Clause Conjunction (AND) (30 groups = 60 records)
4. Disjunction (OR / Any Met) (30 groups = 60 records)
5. Exclusive Disjunction (XOR / Exactly One) (30 groups = 60 records)
6. Joint Negation (NOR / Neither Met) (30 groups = 60 records)
7. Threshold Boundary Logic (30 groups = 60 records)
8. Majority Voting / Multi-Criteria (30 groups = 60 records)
9. State Transition Preconditions (30 groups = 60 records)
10. Symmetrical Prohibition vs Permission (30 groups = 60 records)

Zero joke distractors. Symmetrical actions. No reasoning prefixes in choices.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Tuple


def make_choices(defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in defs]


def generate_rc3_logical(seed: int = 3001) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    records: List[Dict[str, Any]] = []

    # Subdomain 1: NOT Negation & Exclusion (30 groups)
    not_templates = [
        ("反社会的勢力排除審査",
         "取引先審査規程：対象企業または役員が反社会的勢力との関係が【一切認められない】場合に限り取引基本契約を締結する。関係の疑義または該当事実がある場合は取引を全面謝絶する。",
         "調査結果：信用調査および公的照会の結果、反社関係の懸念や疑義事象は一切認められない。",
         "調査結果：信用調査の結果、主要株主が指定暴力団関連企業との親密交際先に指定されている。",
         "approve_master_transaction_contract", "取引基本契約の締結を承認する",
         "reject_transaction_outright", "コンプライアンス違反として取引を全面謝絶する",
         "hold_for_legal_consultation", "法務部による追加ヒアリングを実施し判断を保留する"),
        ("無農薬有機認証",
         "有機認証基準：過去3年間に化学合成農薬および化学肥料を【一切使用していない】圃場収穫物に限り『有機JASマーク』の貼付を承認する。微量でも使用履歴がある場合は通常慣行栽培品として出荷する。",
         "営農日誌検査：過去5年間にわたり化学合成農薬・化学肥料の使用履歴は一切確認されない。",
         "営農日誌検査：2年前に害虫駆除のため指定化学農薬を1回散布した記録が残っている。",
         "approve_organic_jas_label", "有機JAS認証マークの貼付を承認する",
         "ship_as_conventional_produce", "通常慣行栽培品としての出荷を指示する",
         "conduct_soil_residue_analysis", "土壌残留農薬の精密ガスクロ分析を実施する"),
        ("免震構造耐震等級特例",
         "建築基準規程：設計図書において構造上の欠陥および耐力壁の不足が【一切存在しない】場合に限り耐震等級3の証明書を交付する。軽微でも欠陥が指摘された場合は補強設計を命じる。",
         "構造審査：第三者機関の再計算により、構造欠陥および耐力壁不足は一切存在しないことが確認された。",
         "構造審査：東側耐力壁の配置バランスに偏りがあり、構造計算上の未充足箇所が指摘された。",
         "issue_grade_3_seismic_certificate", "耐震等級3の証明書を交付する",
         "order_structural_reinforcement_design", "指摘箇所の補強是正設計を命じる",
         "hold_building_permit_for_review", "建築確認申請の審査を一時保留とする"),
        ("食品アレルギー原材料不使用",
         "アレルゲン管理規定：製造ラインにおいて特定原材料8品目が【混入していない】ことが検査証明されたバッチに限り『特定原材料不使用』と表示する。混入の可能性がある場合は注意喚起表示を義務付ける。",
         "ELISA検査：特定原材料8品目の混入は検出限界未満（一切不検出）と判定された。",
         "ELISA検査：微量の小麦タンパクがコンタミネーションとして検出された。",
         "approve_allergen_free_label", "特定原材料不使用の強調表示を認可する",
         "mandate_cross_contamination_warning", "製造ライン共有に伴う注意喚起表示を義務付ける",
         "quarantine_production_lot_for_retest", "当該製造ロットを隔離し再検検査を行う"),
        ("インサイダー取引規制除外",
         "社内情報管理規程：未公表の重要事実を【知得していない】従業員に限り自社株の売買申請を承認する。重要事実を知得している役職員の売買申請は即時却下する。",
         "申請審査：業務分掌および閲覧権限の調査により、未公表重要事実の知得・関与は一切認められない。",
         "申請審査：明日開示予定の大規模業務提携プロジェクトの起草に関与している。",
         "approve_insider_stock_trading", "自社株売買の取引申請を承認する",
         "deny_stock_trading_application", "インサイダー取引防止のため売買申請を却下する",
         "escalate_to_compliance_committee", "コンプライアンス委員会へ照会を回付する"),
    ]
    for idx, (title, rule, s1, s2, c1, t1, c2, t2, c3, t3) in enumerate(not_templates):
        for rep in range(6):
            gid = f"rc3_log_not_{idx*6 + rep + 1:03d}"
            c_defs = [(c1, t1), (c2, t2), (c3, t3)]
            choices = make_choices(c_defs)
            q = f"規程適合判定：{title}における判断として適切な指示を選択してください。"
            records.append({
                "id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "not_negation",
                "context": f"【{title}】{rule}\n対象事案：{s1}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": c1}
            })
            records.append({
                "id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "not_negation",
                "context": f"【{title}】{rule}\n対象事案：{s2}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": c2}
            })

    # Subdomain 2: Biconditional with Fallback (30 groups)
    bicond_templates = [
        ("深夜特例割増運賃",
         "タクシー運行規程：乗車時刻が午後10時から翌朝午前5時までの間に開始された場合に限り『深夜割増料金（2割増）』を適用する。それ以外の昼間時間帯は『通常メーター運賃』で精算する。",
         "乗車メーター記録：乗車開始時刻は午後11時42分である。",
         "乗車メーター記録：乗車開始時刻は午後4時15分である。",
         "apply_late_night_surcharge", "深夜割増運賃（2割増）を適用する",
         "charge_standard_daytime_fare", "通常メーター運賃で精算する",
         "issue_flat_rate_airport_voucher", "定額空港アクセス運賃を案内する"),
        ("学術論文査読パス",
         "査読採択規程：2名の外部査読者の判定が【ともに採録（Accept）】である場合に限り本誌への掲載を決定する。いずれか一方でも修正要求または却下の場合は『改訂再審査または不採択』として処理する。",
         "査読結果：査読者A・査読者Bの双方が『無修正採録（Accept）』と評価した。",
         "査読結果：査読者Aは採録としたが、査読者Bは『大幅改訂（Major Revision）』を求めた。",
         "accept_paper_for_publication", "学術論文の本誌掲載を正式決定する",
         "return_for_revision_or_reject", "改訂再審査または不採択として処理する",
         "assign_third_adjudicator_review", "第3査読者を追加指名して判定を仰ぐ"),
        ("産業廃棄物特別管理委託",
         "廃棄物処理基準：排出物が重金属等有害物質の基準値を超過している場合に限り『特別管理産業廃棄物』として処分委託する。基準値未満の場合は『普通産業廃棄物』として処理委託する。",
         "検体分析値：鉛溶出量が基準値0.01mg/Lに対し0.08mg/Lを記録した。",
         "検体分析値：鉛溶出量は0.002mg/Lであり基準値を大幅に下回っている。",
         "delegate_as_specially_controlled_waste", "特別管理産業廃棄物として処分委託する",
         "delegate_as_general_industrial_waste", "普通産業廃棄物として処理委託する",
         "store_in_hermetic_buffer_drum", "密閉ドラム缶に一時保管し再測定する"),
        ("高額療養費現物給付",
         "健康保険適用基準：窓口にて『限度額適用認定証』が提示されている場合に限り自己負担限度額までの支払いで会計を完了する。未提示の場合は『法定自己負担割合（3割等）』で一旦全額請求する。",
         "患者受付：有効期限内の限度額適用認定証と保険証が提示された。",
         "患者受付：保険証のみの提示であり、限度額適用認定証は未持参である。",
         "bill_up_to_copayment_limit", "自己負担限度額までの支払いで会計する",
         "charge_standard_statutory_copay", "法定自己負担割合に基づき一旦全額請求する",
         "guide_to_municipal_medical_subsidy", "市区町村の医療費助成制度を案内する"),
        ("自動バックアップ世代交代",
         "ストレージ管理規程：フルバックアップの作成から7日以上が経過している場合に限り『新規フルバックアップ作成』を実行する。7日未満の場合は『日次差分バックアップ』を実行する。",
         "バックアップ台帳：直近のフルバックアップは10日前に実行完了している。",
         "バックアップ台帳：直近のフルバックアップは3日前に実行完了している。",
         "execute_full_system_backup", "新規フルバックアップ作成を実行する",
         "execute_daily_incremental_backup", "日次差分バックアップを実行する",
         "verify_backup_archive_integrity", "既存アーカイブのチェックサム整合性を検証する"),
    ]
    for idx, (title, rule, s1, s2, c1, t1, c2, t2, c3, t3) in enumerate(bicond_templates):
        for rep in range(6):
            gid = f"rc3_log_bic_{idx*6 + rep + 1:03d}"
            c_defs = [(c1, t1), (c2, t2), (c3, t3)]
            choices = make_choices(c_defs)
            q = f"運用判断：{title}の規程に基づき適切な処置を選択してください。"
            records.append({
                "id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "biconditional_fallback",
                "context": f"【{title}】{rule}\n確認情報：{s1}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": c1}
            })
            records.append({
                "id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "biconditional_fallback",
                "context": f"【{title}】{rule}\n確認情報：{s2}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": c2}
            })

    # Subdomain 3: Multi-Clause Conjunction (AND) (30 groups)
    and_templates = [
        ("医薬品臨床試験治験参加基準",
         "治験参加基準：年齢が20歳以上65歳以下であり、かつ直近のHbA1c値が7.0%以上8.5%未満の両方を満たす患者を治験群として登録する。いずれかを満たさない場合は治験対象外とする。",
         "患者データ：45歳、HbA1c測定値7.8%。",
         "患者データ：52歳、HbA1c測定値9.2%（上限超過）。",
         "enroll_patient_in_clinical_trial", "治験群の対象患者として正式登録する",
         "exclude_patient_from_clinical_trial", "治験参加の適格基準を満たさず対象外とする",
         "repeat_blood_sample_glucose_test", "1週間後に再度血糖検査を行い再評価する"),
        ("無担保融資実行判定",
         "融資審査基準：創業後3期以上の決算があり、かつ直近決算で債務超過がない場合に限り無担保融資を実行する。未達項目がある場合は保証人または担保設定を求める。",
         "財務状況：業歴5年（4期決算完了）、直近純資産2,500万円（資産超過）。",
         "財務状況：業歴4年（3期決算完了）、直近純資産-800万円（債務超過）。",
         "disburse_unsecured_business_loan", "無担保融資の実行を承認する",
         "require_guarantor_or_collateral", "信用保証人の追加または担保設定を要求する",
         "transfer_to_turnaround_support_desk", "経営改善支援デスクへ相談を回付する"),
        ("プラント高圧ガス充填開始",
         "ガス充填安全基準：ボンベ耐圧検査証が有効期間内であり、かつ接続配管の気密リークテストに合格している場合にガス充填を開始する。いずれか不備時は充填作業を停止する。",
         "点検報告：耐圧検査証の有効期間残8か月、ヘリウムリークテスト合格確認。",
         "点検報告：耐圧検査証は有効期間内だが、配管継手から微小リークを検知。",
         "commence_high_pressure_gas_filling", "安全基準適合として高圧ガスの充填を開始する",
         "halt_filling_and_repair_piping", "充填作業を直ちに停止し配管修繕を指示する",
         "purge_transfer_line_with_nitrogen", "配管内を不活性窒素ガスでパージする"),
        ("特急貨物便当日発送",
         "集荷締切基準：集荷依頼が午後2時までに完了しており、かつ荷物総重量が30kg以下である場合に限り当日航空特急便として発送する。超過時は翌日陸送便として振り替える。",
         "受付情報：依頼完了時刻は午後1時20分、荷物実測重量は18.5kg。",
         "受付情報：依頼完了時刻は午後1時40分、荷物実測重量は42.0kg（重量超過）。",
         "dispatch_same_day_air_express", "当日航空特急便として発送手続きを行う",
         "reroute_to_next_day_ground_freight", "翌日陸送通常便へ振り替えて手配する",
         "split_freight_into_multiple_packages", "荷物を複数個口に分割梱包可能か確認する"),
        ("サーバールーム入退室権限",
         "物理セキュリティ規程：生体認証（虹彩）に一致し、かつ入室予約承認コードを所持している場合にセキュリティドアを解錠する。いずれか不一致時は入室を拒絶する。",
         "認証端末：虹彩認証マッチング率99.8%、入室承認コード正常認証完了。",
         "認証端末：虹彩認証は一致したが、入室予約コードの有効期限が切れている。",
         "unlock_server_room_security_door", "セキュリティドアを解錠し入室を許可する",
         "deny_server_room_access_alarm", "入室を拒絶しセキュリティゲート施錠を維持する",
         "dispatch_facility_guard_for_verification", "警備員を呼び出して身元目視確認を行う"),
    ]
    for idx, (title, rule, s1, s2, c1, t1, c2, t2, c3, t3) in enumerate(and_templates):
        for rep in range(6):
            gid = f"rc3_log_and_{idx*6 + rep + 1:03d}"
            c_defs = [(c1, t1), (c2, t2), (c3, t3)]
            choices = make_choices(c_defs)
            q = f"審査判定：{title}における条件適合性に基づき適切な措置を選択してください。"
            records.append({
                "id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "conjunction_and",
                "context": f"【{title}】{rule}\n申請情報：{s1}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": c1}
            })
            records.append({
                "id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "conjunction_and",
                "context": f"【{title}】{rule}\n申請情報：{s2}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": c2}
            })

    # Subdomain 4: Disjunction (OR / Any Met) (30 groups)
    or_templates = [
        ("住宅取得給付金受給要件",
         "給付金支給要件：世帯主の前年年収が500万円以下であるか、または扶養親族が3名以上いるかの【いずれか一方でも】満たす場合に給付金を全額支給する。双方ともに満たさない場合は不支給とする。",
         "申請世帯：年収680万円（超過）、扶養親族4名（要件充足）。",
         "申請世帯：年収720万円（超過）、扶養親族1名（未充足）。",
         "approve_housing_grant_payment", "受給要件該当として給付金を全額支給する",
         "reject_housing_grant_application", "支給要件を満たさないため申請を不支給とする",
         "request_supplementary_tax_certificate", "過去の課税証明書の追加提出を求める"),
        ("産業機械緊急保護停止",
         "安全保全基準：ベアリング温度が85℃を超過するか、または振動加速度が4.5Gを超過した場合は【いずれか一方の発生でも】モーターを緊急遮断停止する。双方が正常値内なら運転を継続する。",
         "監視計器：温度72℃（正常）、振動加速度5.2G（閾値超過警報）。",
         "監視計器：温度68℃（正常）、振動加速度2.1G（正常）。",
         "trip_motor_emergency_cutoff", "安全保護のためモーターを緊急遮断停止する",
         "maintain_continuous_machine_operation", "異常なしと判定し機械の定常運転を継続する",
         "switch_to_auxiliary_lubrication_pump", "補助潤滑油ポンプを手動運転に切り替える"),
        ("高速道路通行止め規制",
         "交通規制基準：降雪量が1時間に10cmを超えるか、または瞬間風速が25m/sを超えた場合は【いずれか一方でも】高速道路を通行止めとする。双方が基準以下ならチェーン規制または速度規制に留める。",
         "気象レーダー：降雪量は毎時3cmだが、瞬間最大風速28m/sを記録した。",
         "気象レーダー：降雪量毎時4cm、瞬間風速12m/sで推移している。",
         "close_expressway_to_traffic", "全線通行止め規制を発令する",
         "impose_tire_chain_or_speed_limit", "チェーン規制または速度規制で通行を維持する",
         "dispatch_snow_removal_plow_trucks", "除雪パトロール車を先行出動させる"),
        ("システムフェイルオーバー発動",
         "高可用性規程：メインDBの応答タイムアウトが5秒以上継続するか、またはAPIエラー率が30%を超過した場合は【いずれか一方の検知でも】スタンバイ系へ切り替える。双方が安定値なら現行系を維持する。",
         "監視メトリクス：応答時間1.2秒（安定）、APIエラー率38%（急上昇）。",
         "監視メトリクス：応答時間0.8秒（安定）、APIエラー率2.1%（正常）。",
         "trigger_standby_failover_switch", "スタンバイ系への自動フェイルオーバーを発動する",
         "maintain_primary_system_operation", "現行系プライマリの運用を維持する",
         "restart_caching_layer_daemons", "キャッシュ層のデーモンを再起動する"),
        ("重要文化財特別公開許可",
         "文化財展示規程：学術研究目的での公的申請であるか、または年1回の指定特別公開日であるかの【いずれかに該当する場合】に限り一般立ち入りを認める。いずれにも非該当なら非公開とする。",
         "申請内容：公的大学の教授による学術研究調査のための申請書が提出された。",
         "申請内容：民間旅行会社の商業ツアーによる通常平日の立ち入り見学希望。",
         "grant_special_cultural_access", "要件充足により特別立ち入り公開を許可する",
         "deny_public_access_keep_closed", "非該当のため立ち入りを拒否し非公開を維持する",
         "schedule_digital_archive_viewing", "デジタルアーカイブの閲覧室利用を案内する"),
    ]
    for idx, (title, rule, s1, s2, c1, t1, c2, t2, c3, t3) in enumerate(or_templates):
        for rep in range(6):
            gid = f"rc3_log_dis_{idx*6 + rep + 1:03d}"
            c_defs = [(c1, t1), (c2, t2), (c3, t3)]
            choices = make_choices(c_defs)
            q = f"要件照合：{title}に基づき適切な判断を選択してください。"
            records.append({
                "id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "disjunction_or",
                "context": f"【{title}】{rule}\n事象状況：{s1}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": c1}
            })
            records.append({
                "id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "disjunction_or",
                "context": f"【{title}】{rule}\n事象状況：{s2}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": c2}
            })

    # Subdomain 5: Exclusive Disjunction (XOR / Exactly One Met) (30 groups)
    xor_templates = [
        ("省エネリフォーム重複助成排除",
         "補助金併用規定：窓断熱改修助成金または太陽光発電導入助成金の【どちらか一方のみ】を選択して申請できる。双方の重複申請または両方未申請の場合は不採択とする。",
         "申請内容：窓断熱改修のみを選択し、太陽光発電助成は未申請。",
         "申請内容：同一年度において窓断熱改修と太陽光発電助成の両方を重複受給申請。",
         "approve_single_subsidy_award", "単一助成選択を確認し給付申請を採択承認する",
         "reject_duplicate_subsidy_application", "重複受給禁止規定に基づき申請を不採択とする",
         "request_applicant_subsidy_selection", "申請者にいずれか一方の取り下げ選択を求める"),
        ("社内特別報奨制度",
         "表彰規程：年間MVP表彰または海外研修派遣の【いずれか一方のみ】を受賞できる。双方の候補に挙がった場合は海外研修枠を次点者へ譲渡しMVP表彰のみを授与する。",
         "候補者推薦：年間MVP単独の推薦であり、海外研修にはエントリーしていない。",
         "候補者推薦：年間MVPと海外研修派遣の両方に同時にノミネートされている。",
         "confer_mvp_award_exclusively", "単独受賞として年間MVP表彰を授与する",
         "reallocate_foreign_training_to_runnerup", "重複回避のため海外研修枠を次点者へ譲渡する",
         "defer_award_decision_to_executive_board", "役員選考委員会へ判断を保留委託する"),
        ("通信回線冗長化排他ルーティング",
         "ネットワーク規程：光ファイバー回線または衛星通信バックアップ回線の【いずれか一方のみ】をアクティブ経路として通信パケットを送出する。両方のアクティブ設定はパケットループ防止のため遮断する。",
         "ルーター設定：光ファイバー回線のみをゲートウェイに指定、衛星回線はコールドスタンバイ。",
         "ルーター設定：誤設定により光ファイバーと衛星回線の双方が同一宛先へアクティブ化。",
         "route_traffic_through_single_active_line", "単一アクティブ経路を通してパケットを送出する",
         "block_traffic_to_prevent_routing_loop", "ルーティングループ防止のためパケット送出を遮断する",
         "enable_bgp_route_flapping_dampening", "BGPルートフラップ制御を有効化する"),
        ("複業兼業時間外労働算定",
         "労務管理規程：本業企業または副業先企業の【いずれか一方のみ】において36協定の特別延長枠を適用できる。両社での重複適用が発覚した場合は副業先での時間外労働を全面制限する。",
         "申告状況：本業先のみで36協定特別条項を適用し、副業先は法定内労働に抑制。",
         "申告状況：本業先と副業先の双方が同時に36協定特別延長枠を適用して勤務。",
         "approve_single_employer_overtime_clause", "単独適用を確認し特別延長枠を適法承認する",
         "restrict_overtime_at_secondary_employer", "重複適用違反を避けるため副業先残業を制限する",
         "order_comprehensive_labor_time_audit", "全労働時間の総合精査監査を命令する"),
        ("学業成績優秀者授業料免除",
         "特待生規程：全額免除特待生枠または学外給付型奨学金の【どちらか一方のみ】を受給できる。学外奨学金と全額免除の双方が決定した場合は半額免除枠へ自動減額調整する。",
         "受給状況：全額免除特待生にのみ選抜され、学外奨学金は未受給。",
         "受給状況：全額免除特待生に選抜され、かつ月額10万円の学外給付奨学金も決定。",
         "grant_full_tuition_waiver", "単独受給を確認し授業料全額免除を適用する",
         "adjust_tuition_waiver_to_half_amount", "重複規程に基づき半額免除枠へ減額調整する",
         "hold_scholarship_disbursement_review", "奨学金給付委員会による審議まで保留とする"),
    ]
    for idx, (title, rule, s1, s2, c1, t1, c2, t2, c3, t3) in enumerate(xor_templates):
        for rep in range(6):
            gid = f"rc3_log_xor_{idx*6 + rep + 1:03d}"
            c_defs = [(c1, t1), (c2, t2), (c3, t3)]
            choices = make_choices(c_defs)
            q = f"排他規程判定：{title}に基づき適切な対応を選択してください。"
            records.append({
                "id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "exclusive_disjunction_xor",
                "context": f"【{title}】{rule}\n事案：{s1}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": c1}
            })
            records.append({
                "id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "exclusive_disjunction_xor",
                "context": f"【{title}】{rule}\n事案：{s2}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": c2}
            })

    # Subdomain 6: Joint Negation (NOR / Neither Met) (30 groups)
    nor_templates = [
        ("自然保護区開発許可制限",
         "環境保全条例：特別保護区内においては『樹木の伐採』および『工作物の新築』の【いずれも行わない】計画に限り簡易利用届出を受理する。いずれか一方でも行う場合は知事の特別許可申請を必要とする。",
         "届出内容：木道の手すり修繕のみであり、樹木の伐採も工作物の新築も一切行わない。",
         "届出内容：案内看板設置のため基礎コンクリートを打設し工作物を新築する計画。",
         "accept_simple_use_notification", "制限非該当として簡易利用届出をそのまま受理する",
         "require_special_prefectural_permit", "条例抵触として知事の特別許可申請手続きを要求する",
         "order_environmental_impact_assessment", "環境影響評価書の作成提出を指示する"),
        ("航空保安危険品手荷物持込",
         "航空手荷物規則：引火性液体および高圧ガスの【双方ともに含まない】携帯手荷物に限り機内持ち込みを許可する。いずれか一方が含まれる場合は保安検査場にて没収または受託貨物拒絶とする。",
         "手荷物X線検査：ノートPCと衣類のみであり、引火物やガススプレー缶は一切ない。",
         "手荷物X線検査：登山用ガス缶（高圧ガスボンベ）がバッグ内から発見された。",
         "permit_carry_on_baggage", "保安検査適合として機内持ち込みを許可する",
         "confiscate_prohibited_hazardous_material", "危険物持込禁止規程に基づき手荷物から没収する",
         "escort_passenger_to_security_office", "旅客を保安検査事務所へ案内し事情聴取する"),
        ("医薬品添加物安全性基準",
         "製剤設計規程：合成着色料および遺伝子組み換え賦形剤の【いずれも使用しない】処方に限り『特定成分無添加医薬品』としての表示を認可する。いずれかを使用する場合は全成分明記のみとする。",
         "処方設計書：天然由来色素とトウモロコシ非組換え澱粉のみを使用。",
         "処方設計書：安定性向上のため合成タール色素赤色102号を微量配合。",
         "authorize_additive_free_pharmaceutical_label", "特定成分無添加医薬品としての強調表示を認可する",
         "mandate_standard_full_ingredient_labeling", "強調表示を不認可とし全成分標準表示を指示する",
         "conduct_microbiological_stability_testing", "微生物学的安定性試験の追加データを要求する"),
        ("機密文書電子破棄証明",
         "情報セキュリティ手順：クラウドストレージの残存データおよびローカルキャッシュの【いずれも存在しない】ことが確認された場合に限り完全消去証明書を発行する。残存時は再消去を実行する。",
         "フォレンジック検証：クラウド上のファイルおよび端末キャッシュともに完全消去を確認。",
         "フォレンジック検証：クラウドは消去されたが、ローカルの一時フォルダに暗号化残骸が残存。",
         "issue_certificate_of_complete_data_erasure", "完全消去を確認しデータ破棄証明書を発行する",
         "execute_re_sanitization_process", "残存箇所を特定しデータ再消去プロセスを実行する",
         "quarantine_storage_media_physically", "記憶媒体を物理隔離しアクセスを遮断する"),
        ("無人搬送車自動発進インターロック",
         "工場安全基準：走行ルート上に障害物がなく、かつ非常停止ボタンが押されていない【両方の安全状態】が揃った場合に限りAGVの自動発進を許可する。いずれかが不安全なら発進を阻止する。",
         "センサー信号：ルート上障害物ゼロ、非常停止接点は全系統ノーマルクローズ（復帰状態）。",
         "センサー信号：障害物は検知されないが、第3コンベア非常停止ボタンが押下状態。",
         "authorize_agv_automatic_departure", "安全確認完了によりAGVの自動発進を許可する",
         "inhibit_agv_departure_due_to_interlock", "インターロック作動によりAGVの発進を阻止する",
         "sound_perimeter_warning_buzzer", "周辺作業員へ警告ブザーを鳴動させる"),
    ]
    for idx, (title, rule, s1, s2, c1, t1, c2, t2, c3, t3) in enumerate(nor_templates):
        for rep in range(6):
            gid = f"rc3_log_nor_{idx*6 + rep + 1:03d}"
            c_defs = [(c1, t1), (c2, t2), (c3, t3)]
            choices = make_choices(c_defs)
            q = f"安全基準判定：{title}に基づき適切な判断を選択してください。"
            records.append({
                "id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "joint_negation_nor",
                "context": f"【{title}】{rule}\n測定確認：{s1}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": c1}
            })
            records.append({
                "id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "joint_negation_nor",
                "context": f"【{title}】{rule}\n測定確認：{s2}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": c2}
            })

    # Subdomain 7: Threshold Boundary Logic (30 groups)
    threshold_templates = [
        ("ボイラー蒸気圧力安全弁",
         "圧力容器管理基準：蒸気圧力が1.50MPaを超過した場合は安全弁を直ちに開放し減圧する。1.50MPa以下の場合は燃焼制御を維持し定常運転を継続する。",
         "圧力計指示値：1.62MPa（管理限界超過）。",
         "圧力計指示値：1.38MPa（正常管理範囲内）。",
         "release_boiler_safety_valve", "安全弁を開放して急速減圧を実施する",
         "maintain_normal_combustion_operation", "燃焼制御を維持し定常運転を継続する",
         "inspect_pressure_gauge_calibration", "圧力計のゼロ点校正を目視点検する"),
        ("冷却水水質導電率ブローダウン",
         "冷却塔水質基準：循環水の電気伝導率が1200μS/cmを超過した場合は自動ブロー弁を開放し給水換水する。1200μS/cm以下の場合は循環ポンプをそのまま運転する。",
         "水質計指示値：1350μS/cm（濃縮限界超過）。",
         "水質計指示値：980μS/cm（基準値内）。",
         "open_automatic_blowdown_valve", "自動ブロー弁を開放し強制換水を実施する",
         "continue_coolant_circulation_pump", "循環ポンプをそのまま定常運転させる",
         "dose_corrosion_inhibitor_chemical", "防食剤の薬注ポンプ出力を手動調整する"),
        ("クリーンルーム差圧ダンパー制御",
         "無塵室空調基準：前室との差圧が15Pa未満に低下した場合は給気ファン出力を緊急昇圧する。15Pa以上が維持されている場合は現在のインバーター周波数を保持する。",
         "差圧計測定値：10Pa（設定差圧割れ）。",
         "差圧計測定値：22Pa（良好な陽圧状態）。",
         "boost_air_supply_fan_output", "給気ファン出力を緊急昇圧し陽圧を回復する",
         "maintain_inverter_frequency", "現在のインバーター周波数を維持する",
         "inspect_door_gasket_seal_integrity", "出入口ドアパッキンのシール劣化を点検する"),
        ("電気炉トランス過熱防止",
         "変圧器保護基準：トランス巻線温度が110℃を超過した場合は負荷出力を50%に強制抑制する。110℃以下の場合は定格100%出力通電を継続する。",
         "熱電対測定値：118℃（高温警報発令）。",
         "熱電対測定値：95℃（許容運転範囲内）。",
         "curtail_transformer_load_to_half", "トランス負荷出力を50%に強制抑制する",
         "continue_full_rated_power_output", "定格100%での通電加熱を継続する",
         "activate_forced_air_cooling_fans", "強制冷却ファンの手動バックアップを起動する"),
        ("排水COD規制濃度監視",
         "工場排水基準：放流水の化学的酸素要求量（COD）が20mg/Lを超過した場合は河川放流を遮断し調整池へ回収する。20mg/L以下の場合は通常放流を継続する。",
         "オンラインCOD計：26mg/L（公害防止協定超過）。",
         "オンラインCOD計：14mg/L（環境基準適合）。",
         "shut_effluent_gate_and_divert", "河川放流ゲートを遮断し調整池へ全量回収する",
         "continue_standard_effluent_discharge", "水質適合を確認し通常放流を継続する",
         "increase_biological_aeration_volume", "曝気槽のブロワー送風量を増量する"),
    ]
    for idx, (title, rule, s1, s2, c1, t1, c2, t2, c3, t3) in enumerate(threshold_templates):
        for rep in range(6):
            gid = f"rc3_log_thr_{idx*6 + rep + 1:03d}"
            c_defs = [(c1, t1), (c2, t2), (c3, t3)]
            choices = make_choices(c_defs)
            q = f"数値判定：{title}の閾値に基づき適切な機器制御を選択してください。"
            records.append({
                "id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "threshold_boundary",
                "context": f"【{title}】{rule}\n測定実績：{s1}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": c1}
            })
            records.append({
                "id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "threshold_boundary",
                "context": f"【{title}】{rule}\n測定実績：{s2}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": c2}
            })

    # Subdomain 8: Majority Voting / Multi-Criteria (30 groups)
    majority_templates = [
        ("役員会決議採択要件",
         "会社法定款規程：出席取締役5名のうち【過半数（3名以上）の賛成】を得た議案に限り可決承認とする。賛成が2名以下の議案は否決とする。",
         "採決結果：出席5名中、賛成4名、反対1名。",
         "採決結果：出席5名中、賛成2名、反対3名。",
         "declare_resolution_approved_by_majority", "過半数賛成により議案の可決承認を宣言する",
         "declare_resolution_rejected", "過半数未達により議案の否決を宣言する",
         "postpone_vote_to_extraordinary_meeting", "臨時株主総会まで採決を留保する"),
        ("システム障害三重冗長系合意",
         "耐障害性設計基準：3台の投票ノードのうち【2台以上の出力が一致】した場合にその合意値を確定トランザクションとしてコミットする。全ノード不一致の場合はロールバックする。",
         "ノード応答：Node1=OK, Node2=OK, Node3=ERROR（2台一致）。",
         "ノード応答：Node1=ACK_A, Node2=ACK_B, Node3=TIMEOUT（合意不成立）。",
         "commit_transaction_on_majority_consensus", "多数決合意値に基づきトランザクションをコミットする",
         "rollback_transaction_split_brain", "不一致と判定しトランザクションをロールバックする",
         "isolate_faulty_node_from_cluster", "異常ノードをクラスターから切り離す"),
        ("医療カンファレンス手術適応判定",
         "臨床合議基準：外科医3名および麻酔科医1名の計4名による症例検討において、【3名以上の賛成】が得られた場合に開心術を施行する。2名以下の場合は保存的薬物療法を選択する。",
         "カンファレンス判定：外科医3名全員賛成、麻酔科医条件付き賛成（計4名賛成）。",
         "カンファレンス判定：外科医1名賛成、外科医2名反対、麻酔科医保留（賛成1名）。",
         "schedule_cardiac_surgical_operation", "適応合議成立により開心術の施行を決定する",
         "select_conservative_pharmacotherapy", "手術を見送り保存的薬物療法を選択する",
         "request_external_hospital_second_opinion", "他大学病院へセカンドオピニオンを依頼する"),
        ("セキュリティインシデント重大度判定",
         "インシデント規程：評価4指標（情報漏洩・業務停止・金銭被害・社会的影響）のうち【2項目以上が重大（High）】と判定された場合は全社対策本部を設置する。1項目以下なら現場主管課対応に留める。",
         "評価結果：情報漏洩（High）、業務停止（High）、金銭被害（Low）、社会的影響（Low）。",
         "評価結果：情報漏洩（High）、業務停止（None）、金銭被害（Low）、社会的影響（Low）。",
         "establish_crisis_management_headquarters", "重大事態として全社対策本部を設置する",
         "delegate_response_to_department_desk", "主管部門のセキュリティデスク対応に留める",
         "report_incident_to_privacy_commission", "個人情報保護委員会へ速報を提出する"),
        ("新製品市場投入判定ゲート",
         "商品開発規程：発売判定会議において審査5分野（採算性・品質安定性・知財侵害性・法令適合・生産能力）のうち【4分野以上で合格判定】を得た製品に限り量産販売を開始する。未達時は発売延期とする。",
         "ゲート審査：採算性○、品質○、知財○、法令○、生産能力△（4分野合格）。",
         "ゲート審査：採算性○、品質△、知財○、法令△、生産能力△（2分野合格）。",
         "authorize_commercial_mass_production", "審査合格を確認し新製品の量産販売を開始する",
         "delay_product_launch_for_re_engineering", "基準未達のため発売を延期し再設計を指示する",
         "conduct_limited_regional_test_marketing", "特定地域での先行テスト販売を検討する"),
    ]
    for idx, (title, rule, s1, s2, c1, t1, c2, t2, c3, t3) in enumerate(majority_templates):
        for rep in range(6):
            gid = f"rc3_log_maj_{idx*6 + rep + 1:03d}"
            c_defs = [(c1, t1), (c2, t2), (c3, t3)]
            choices = make_choices(c_defs)
            q = f"判定合議：{title}に基づき適切な決定を選択してください。"
            records.append({
                "id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "majority_voting",
                "context": f"【{title}】{rule}\n審査結果：{s1}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": c1}
            })
            records.append({
                "id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "majority_voting",
                "context": f"【{title}】{rule}\n審査結果：{s2}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": c2}
            })

    # Subdomain 9: State Transition Preconditions (30 groups)
    state_templates = [
        ("産業ロボットティーチングモード移行",
         "安全規程：非常停止ボタンが解除され、かつイネーブルスイッチが中間位置に保持されている場合に限りロボットの『手動教示モード』への移行を許可する。いずれか欠落時は教示モード移行をロックする。",
         "安全回路状態：非常停止解除済み、3ポジションスイッチ中間ホールド確認。",
         "安全回路状態：非常停止は解除されているが、イネーブルスイッチが開放状態。",
         "permit_transition_to_teaching_mode", "安全インターロック解除を確認し教示モード移行を許可",
         "lock_and_inhibit_teaching_mode", "インターロック未成立のため教示モード移行をロック",
         "reset_servo_amplifier_fault_code", "サーボアンプのアラームコードをリセットする"),
        ("原子力設備燃料装荷前ステップ",
         "保安規定：制御棒が全数全挿入位置にあり、かつほう素濃度が規定値以上であることを確認した場合にのみ新規燃料集合体の装荷ステップを開始する。未確認時は装荷を禁止する。",
         "点検記録：制御棒全数全挿入表示確認、一次系ほう素濃度2,300ppm（規定値以上）。",
         "点検記録：制御棒全挿入は確認されたが、ほう素濃度が1,800ppmで規定値未満。",
         "commence_nuclear_fuel_loading_step", "保安条件満足を確認し燃料集合体の装荷ステップを開始",
         "prohibit_fuel_loading_operation", "保安条件未達により燃料装荷作業を禁止・停止する",
         "recirculate_primary_coolant_system", "一次冷却材系統を循環撹拌させる"),
        ("商用決済ゲートウェイ保守モード",
         "運用手順：未完了トランザクションがゼロ件であり、かつバッチ同期デーモンが停止完了している場合に限り決済ゲートウェイを『メンテナンス保守状態』へ移行する。残存処理時は移行を待機する。",
         "システム状態：キュー残0件、同期デーモン正常停止（EXIT_CODE=0）。",
         "システム状態：デーモンは停止したが、キューに処理中トランザクションが4件残存。",
         "transition_payment_gateway_to_maintenance", "全トランザクション完了を確認し保守状態へ移行する",
         "defer_maintenance_mode_and_wait_queue", "未処理残存のため保守移行を見送り処理完了を待機",
         "drain_and_redirect_active_traffic", "進行中トラフィックを別系統へ強制ドレインする"),
        ("高圧受電設備接地線接続",
         "電気安全規則：主受電遮断器（VCB）が開放（OFF）され、かつ検電器にて無電圧（停電）が確認された場合に限り高圧側接地線の接続作業を許可する。感電防止のためいずれか未確認時は作業を禁止する。",
         "作業現場確認：VCB開放表示確認、検電器3相すべて不点灯（無電圧確認）。",
         "作業現場確認：VCBは開放されたが、検電器による無電圧確認が未実施。",
         "authorize_high_voltage_grounding_wire_connection", "停電確認完了により高圧側接地線の接続作業を許可する",
         "strictly_prohibit_grounding_connection_work", "無電圧未確認による感電防止のため接地作業を厳禁とする",
         "lock_and_tagout_main_breaker_switch", "主遮断器の操作ハンドルに南京錠を施錠する"),
        ("医薬用水滅菌スチームパージ",
         "GMP管理手順：配管ドレン温度が121℃に達し、かつ滅菌タイマーが20分間積算された場合に滅菌工程を『完了』とし次工程へ遷移する。温度低下または時間不足時はタイマーをリセットし再加熱する。",
         "プロセスログ：配管ドレン温度122.5℃、滅菌保持時間20分30秒達成。",
         "プロセスログ：配管ドレン温度121.8℃、滅菌保持時間14分（目標20分未達）。",
         "mark_sterilization_complete_and_advance", "滅菌基準達成を確認し次工程へ正常遷移させる",
         "reset_sterilization_timer_and_reheat", "時間不足のため滅菌タイマーをリセットし再加熱する",
         "sample_condensate_water_for_endotoxin", "スチーム復水を採取してエンドトキシン検査を行う"),
    ]
    for idx, (title, rule, s1, s2, c1, t1, c2, t2, c3, t3) in enumerate(state_templates):
        for rep in range(6):
            gid = f"rc3_log_sta_{idx*6 + rep + 1:03d}"
            c_defs = [(c1, t1), (c2, t2), (c3, t3)]
            choices = make_choices(c_defs)
            q = f"状態遷移判定：{title}の前提条件に基づき適切な指示を選択してください。"
            records.append({
                "id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "state_transition",
                "context": f"【{title}】{rule}\n現場状態：{s1}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": c1}
            })
            records.append({
                "id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "state_transition",
                "context": f"【{title}】{rule}\n現場状態：{s2}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": c2}
            })

    # Subdomain 10: Symmetrical Prohibition vs Permission (30 groups)
    prohibit_templates = [
        ("化学工場構内火気使用",
         "火薬類管理規則：構内における溶接・グラインダー等の火気使用は原則『全面禁止』とする。ただし、防爆エリア外でありかつ防火責任者の立会許可書がある場合に限り『火気作業を許可』する。",
         "申請事案：防爆区域外の屋外資材ヤード、防火管理者の立会証明書受領済み。",
         "申請事案：防爆エリアに隣接する配管棟、立会者の申請書なしで作業希望。",
         "permit_hot_work_with_fire_supervisor", "立会確認済みにより火気使用作業を正式許可する",
         "strictly_prohibit_hot_work_operation", "原則規則に基づき火気使用作業を厳重に禁止する",
         "require_portable_fire_extinguisher_placement", "粉末消火器を現場に2本配備するよう命じる"),
        ("深夜時間帯航空機離着陸",
         "空港騒音防止規程：午後11時から翌朝6時までの航空機離着陸は原則『全面禁止』とする。ただし、急患搬送機または燃料枯渇等の緊急事態宣言機に限り『特例着陸を許可』する。",
         "管制通信：急患搬送ドクターヘリからの緊急受け入れ要請（深夜0時20分）。",
         "管制通信：出発遅延に伴い深夜0時15分に到着予定の一般定期旅客便。",
         "grant_emergency_landing_clearance", "人道緊急性に基づき特例着陸を許可する",
         "prohibit_landing_and_divert_aircraft", "深夜騒音規制に基づき着陸を禁止し代替空港へ回航",
         "instruct_aircraft_to_hold_in_holding_pattern", "上空待機ホールディングを指示する"),
        ("特定個人情報（マイナンバー）保管",
         "個人情報保護規程：退職者の個人番号データは法定保管期間経過後は原則『速やかな破棄削除』を義務付ける。ただし、進行中の税務訴訟に関わる関係者に限り『保管延長を許可』する。",
         "対象者状況：退職後7年経過、現在係争中の国税更正処分等取消訴訟の証拠関係者。",
         "対象者状況：退職後8年経過、退職後の関与や係争事件等は一切存在しない。",
         "permit_extending_mynumber_data_retention", "訴訟関係証拠としてマイナンバーの保管延長を認可",
         "mandate_immediate_destruction_of_mynumber", "保管期間満了に基づきマイナンバーを速やかに破棄",
         "encrypt_and_archive_to_cold_tape", "暗号化テープに退避し耐火金庫に施錠保管する"),
        ("社有車私的利用承認",
         "車両管理規程：休日の社有車利用は原則『全面禁止』とする。ただし、休日出勤承認済みかつ公共交通機関の運行がない早朝深夜業務に限り『社有車の利用を許可』する。",
         "利用申請：休日早朝4時からのサーバー緊急工事出勤、電車運行なし（上長承認済）。",
         "利用申請：休日に家族旅行の買い出しに私用で使いたいとの希望申告。",
         "approve_company_vehicle_weekend_use", "業務必要性を認め休日の社有車利用を許可する",
         "reject_vehicle_use_strictly_prohibited", "私的利用禁止規程に基づき社有車利用を不許可とする",
         "reimburse_taxi_expense_receipt", "タクシー利用での事後精算を案内する"),
        ("重要文化財撮影ストロボ使用",
         "美術館観覧規程：展示室におけるフラッシュ・ストロボ発光撮影は作品劣化防止のため原則『全面禁止』とする。ただし、学術調査認定を受けた研究員による無熱光LED撮影に限り『特別撮影を許可』する。",
         "撮影申請：国立博物館による学術調査認定証を所持、波長管理された無熱LED撮影。",
         "撮影申請：一般来館者によるスマートフォンでのフラッシュ撮影希望。",
         "permit_special_academic_flash_photography", "学術調査認定に基づき特別撮影を許可する",
         "prohibit_flash_photography_strictly", "作品保護規程に基づきフラッシュ撮影を禁止する",
         "provide_official_museum_catalog_images", "美術館公式写真アーカイブの利用を案内する"),
    ]
    for idx, (title, rule, s1, s2, c1, t1, c2, t2, c3, t3) in enumerate(prohibit_templates):
        for rep in range(6):
            gid = f"rc3_log_pro_{idx*6 + rep + 1:03d}"
            c_defs = [(c1, t1), (c2, t2), (c3, t3)]
            choices = make_choices(c_defs)
            q = f"禁止・許可判定：{title}に基づき適切な判断を選択してください。"
            records.append({
                "id": f"{gid}_s1", "group_id": gid, "family": "logical_operators", "subdomain": "prohibition_permission",
                "context": f"【{title}】{rule}\n事案状況：{s1}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": c1}
            })
            records.append({
                "id": f"{gid}_s2", "group_id": gid, "family": "logical_operators", "subdomain": "prohibition_permission",
                "context": f"【{title}】{rule}\n事案状況：{s2}", "question": q, "choices": choices,
                "target": {"kind": "hard", "choice_id": c2}
            })

    return records
