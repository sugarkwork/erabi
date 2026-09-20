"""RC2.1 Training Data Synthesis: Stream B — General Choice Expansion (240 pairs = 480 records).

Categories:
9. explicit_nli_entailment_contradiction (60 pairs = 120 records)
10. causal_semantic_relation_span (60 pairs = 120 records)
11. exemption_and_mandatory_polarity (60 pairs = 120 records)
12. extreme_ranking_reverse_criteria (60 pairs = 120 records)

Total: 240 pairs = 480 records.
"""

from typing import Any, Dict, List, Tuple


def make_choices(defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in defs]


def generate_general_expansion() -> List[Dict[str, Any]]:
    records = []

    # Category 9: Explicit NLI Entailment vs Contradiction (60 pairs = 120 records)
    nli_templates = [
        (
            "数学的論理含意と矛盾",
            "前提文：『工場内の全機械（A号機、B号機、C号機）が定常運転中であり、異常停止している機械は一台も存在しない。』",
            "仮説：『少なくともB号機は正常に稼働している。』",
            "仮説：『A号機とC号機が故障により停止している。』",
            "論理関係判定：前提文と提示された仮説の論理的整合性を選択してください。",
            [("entailment_mathematically_true", "前提から必然的に導かれ論理的に真（含意・妥当）"), ("contradiction_mathematically_false", "前提と真っ向から衝突し論理的に偽（矛盾・背理）"), ("unrelated_neutral_statement", "前提からは真偽判定不能な無関係の命題（中立）")],
            "entailment_mathematically_true", "contradiction_mathematically_false"
        ),
        (
            "契約履行の含意判定",
            "前提文：『受託者は成果物納品期日である2026年9月15日までに全設計書とソースコードを完全な状態で提出完了した。』",
            "仮説：『受託者は契約上の期日までにソースコードを提出した。』",
            "仮説：『受託者は期日に遅延し、設計書を一切提出しなかった。』",
            "命題検証：前提事実に基づく仮説の真偽関係を選択してください。",
            [("logically_entailed_true", "前提の事実から論理的に演繹される（含意関係）"), ("logically_contradicted_false", "前提の事実と明白に矛盾する（矛盾関係）"), ("undetermined_contingent_claim", "前提の記述からは判定できない推測（未確定）")],
            "logically_entailed_true", "logically_contradicted_false"
        ),
        (
            "在庫状況の論理含意",
            "前提文：『全倉庫の在庫製品は厳格な品質検査に合格した特級品のみで構成されており、不良品はゼロである。』",
            "仮説：『第1倉庫に保管されている製品は品質検査に合格している。』",
            "仮説：『第2倉庫の製品には多数の不良品が含まれている。』",
            "推論判定：前提情報と仮説との論理的推論関係を選択してください。",
            [("nli_entailment_derived", "前提から直接演繹的に導出される（含意・正当）"), ("nli_contradiction_denied", "前提と両立せず完全に否定される（矛盾・虚偽）"), ("nli_neutral_independent", "前提の範囲外で独立した言明（中立）")],
            "nli_entailment_derived", "nli_contradiction_denied"
        ),
        (
            "法的手続きの含意判定",
            "前提文：『被告人は公判廷において公訴事実を全面的に否認し、無罪を一貫して主張している。』",
            "仮説：『被告人は公訴事実を認めて自白してはいない。』",
            "仮説：『被告人は裁判官の前で罪を自白し全面的に認めた。』",
            "言明照合：公判前提と仮説の論理関係を選択してください。",
            [("strict_entailment_valid", "前提から厳密に帰結する妥当な命題（含意）"), ("strict_contradiction_invalid", "前提と正面から対立する背理命題（矛盾）"), ("unrelated_legal_hearsay", "公判事実と無関係な伝聞陳述（無関係）")],
            "strict_entailment_valid", "strict_contradiction_invalid"
        ),
        (
            "入館資格の論理帰結",
            "前提文：『研究所の地下実験エリアへ入室したすべての研究員は、生体虹彩認証を通過済みである。』",
            "仮説：『地下実験エリアにいる研究員佐藤は虹彩認証を通過した。』",
            "仮説：『地下実験エリアにいる研究員田中は認証を行わずに入室した。』",
            "論理帰結判定：前提条件からの論理的帰結を選択してください。",
            [("deductive_entailment_proven", "前提の全称命題から個別命題として必然的に導かれる（含意）"), ("deductive_contradiction_refuted", "前提の全称命題と直接衝突し否定される（矛盾）"), ("unverifiable_external_fact", "前提からは検証不能な外部情報（未検証）")],
            "deductive_entailment_proven", "deductive_contradiction_refuted"
        ),
        (
            "決算監査の事実推論",
            "前提文：『当社の当期純利益は前年同期比でプラス25%の大幅増益を達成し、黒字決算となった。』",
            "仮説：『当社の当期業績は最終赤字には陥っていない。』",
            "仮説：『当社は当期において深刻な巨額赤字決算となった。』",
            "財務推論判定：前提事実から導かれる命題の真偽を選択してください。",
            [("financial_entailment_verified", "決算事実から直接支持される真の記述（含意）"), ("financial_contradiction_clash", "決算事実と真っ向から衝突する虚偽の記述（矛盾）"), ("speculative_market_rumor", "決算数値とは無関係な市場の憶測（中立）")],
            "financial_entailment_verified", "financial_contradiction_clash"
        ),
        (
            "安全基準の整合判定",
            "前提文：『高圧ガス容器置場の周囲5メートル以内は火気厳禁であり、いかなる喫煙や溶接作業も禁止されている。』",
            "仮説：『容器置場の真横で溶接トーチを使用することは認められていない。』",
            "仮説：『容器置場の3メートル地点で自由にタバコを喫煙できる。』",
            "安全規則照合：前提規則と提示記述の整合性を選択してください。",
            [("safety_rule_entailed", "安全規則の内容から自明に導出される（含意合致）"), ("safety_rule_contradicted", "安全規則の禁止事項と正面から違反衝突する（矛盾）"), ("safety_rule_neutral", "安全規則の対象外事項（中立）")],
            "safety_rule_entailed", "safety_rule_contradicted"
        ),
        (
            "治験プロトコルの含意",
            "前提文：『第2相臨床試験に参加した被験者は全員、過去に同系統の薬剤投与歴がない初発患者である。』",
            "仮説：『被験者ID-105は同系統薬剤の過去投与歴を持たない。』",
            "仮説：『被験者ID-202は過去に同系統薬剤を3回反復投与された経験がある。』",
            "プロトコル検証：前提から導かれる論理的判断を選択してください。",
            [("protocol_entailment_true", "治験選択基準の前提と合致し必然的に真（含意）"), ("protocol_contradiction_false", "治験選択基準と両立せず必然的に偽（矛盾）"), ("protocol_neutral_unrecorded", "治験選択基準からは判定不能（中立）")],
            "protocol_entailment_true", "protocol_contradiction_false"
        ),
        (
            "ソフトウェアテスト網羅性",
            "前提文：『コア決済エンジンの全単体テストケース1,500件を実行し、エラー率0.00%で全件パスした。』",
            "仮説：『少なくとも為替換算モジュールの単体テストは正常終了した。』",
            "仮説：『決済トランザクションテストの半数以上がアサーションエラーで失敗した。』",
            "テスト結果判定：前提実績に基づくテスト成否の判定を選択してください。",
            [("qa_entailment_certified", "全件パスの実績から必然的に導かれる（含意合致）"), ("qa_contradiction_denied", "全件パスの実績と完全に矛盾し虚偽（矛盾）"), ("qa_neutral_unexecuted", "テスト結果とは無関係な未定義領域（中立）")],
            "qa_entailment_certified", "qa_contradiction_denied"
        ),
        (
            "運行管理の論理帰結",
            "前提文：『本日の長距離夜行高速バス全便は、道路凍結防止対策および安全チェーン装着を完了して定刻運行中である。』",
            "仮説：『東京発博多行きの夜行バスは安全チェーン等の対策を施している。』",
            "仮説：『大阪行きの夜行バスは一切の凍結対策を行わずに走行している。』",
            "運行記録照合：前提情報に基づく論理帰結を選択してください。",
            [("transit_entailment_proven", "全便対応の前提から論理的に正当（含意）"), ("transit_contradiction_refuted", "全便対応の前提と明白に対立（矛盾）"), ("transit_neutral_unknown", "運行実績とは無関係な仮定（中立）")],
            "transit_entailment_proven", "transit_contradiction_refuted"
        ),
    ]

    for idx, (title, premise, h_ent, h_cont, q, c_defs, t_ent, t_cont) in enumerate(nli_templates):
        choices = make_choices(c_defs)
        for rep in range(6):
            gid = f"tb_gen_xnli_{idx*6 + rep + 1:03d}"
            ctx1 = f"【論理推論課題: {title}】\n{premise}\n提示された仮説：『{h_ent}』"
            ctx2 = f"【論理推論課題: {title}】\n{premise}\n提示された仮説：『{h_cont}』"
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "general_choice", "general_category": "short_nli", "context": ctx1, "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t_ent}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "general_choice", "general_category": "short_nli", "context": ctx2, "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t_cont}})

    # Category 10: Explicit Causal & Semantic Relation (Cause vs Effect, Problem vs Solution, 60 pairs = 120 records)
    causal_templates = [
        (
            "データセンター給電障害",
            "【インシデント報告】『配線管路内に侵入したネズミ等の小動物が基幹給電ケーブルの被覆を激しくかじり銅線を短絡損壊させたため、無停電電源装置（UPS）が自動トリップし、サーバーラック群の一時停電遮断が発生した。』",
            "因果分析設問：【本事象の根本原因（Cause）】に該当する要素を選択してください。",
            "因果分析設問：【本事象の最終結果・影響（Effect/Result）】に該当する要素を選択してください。",
            [("cause_rodent_cable_chewing", "根本原因：小動物による基幹給電ケーブル被覆の短絡損壊"), ("effect_temporary_server_shutdown", "最終結果：サーバーラック群の一時停電停止・電源遮断"), ("preventive_pest_barrier_installation", "事後対策：防鼠金網および超音波忌避装置の設置工事")],
            "cause_rodent_cable_chewing", "effect_temporary_server_shutdown"
        ),
        (
            "ECサイト離脱問題と解決策",
            "【改善分析】『決済フォームの入力項目が多すぎて購入直前でのユーザー離脱率が高騰している問題に対し、入力項目を必須3項目に半減させるワンステップ決済画面への改修を実施してコンバージョン率を劇的に改善した。』",
            "課題解決分析：【直面していた根本問題（Problem）】を選択してください。",
            "課題解決分析：【採用された具体的解決策（Solution）】を選択してください。",
            [("problem_low_checkout_conversion", "直面問題：入力過多による決済直前での高いユーザー離脱率"), ("solution_reduce_form_fields", "解決手段：入力項目を必須3点に絞るワンステップ決済導入"), ("kpi_monthly_gross_revenue", "評価指標：月間総取扱高の集計ダッシュボード")],
            "problem_low_checkout_conversion", "solution_reduce_form_fields"
        ),
        (
            "自動車製造ラインアーム停止",
            "【保全報告】『塗装ロボットアームの光学位置決めセンサー表面にミスト状の機械潤滑油が付着堆積したことが原因で、レーザー測定光が乱反射して位置を見失い、安全インターロックが作動して溶接ライン全体が緊急停止した。』",
            "要因分析設問：【ライン停止を招いた物理的原因（Cause）】を選択してください。",
            "要因分析設問：【引き起こされた最終的結果（Result）】を選択してください。",
            [("cause_oil_coating_on_sensor", "直接原因：光学位置決めセンサー表面への潤滑油ミスト付着堆積"), ("result_robot_arm_stoppage", "最終結果：安全インターロック作動による溶接ライン緊急停止"), ("replace_mechanical_fasteners", "無関係作業：ボルトナット類の定期締め付け確認")],
            "cause_oil_coating_on_sensor", "result_robot_arm_stoppage"
        ),
        (
            "食品メーカー定番商品値上げ",
            "【経営発表】『主原料である輸入小麦粉の国際取引価格高騰と為替の大幅な円安進行が原価を圧迫したため、企業努力のみでの吸収が困難となり、旗艦主力食品5品目の希望小売価格を12%引き上げる値上げ改定に踏み切った。』",
            "経済因果分析：【価格改定の直接的要因・背景（Cause）】を選択してください。",
            "経済因果分析：【最終的に決定された措置・結果（Effect）】を選択してください。",
            [("cause_material_cost_and_weak_yen", "直接要因：輸入小麦粉の国際価格高騰と急速な円安進行"), ("effect_price_hike_on_flagship_foods", "最終結果：主力商品5品目の希望小売価格12%値上げ改定"), ("launch_new_green_tea_beverage", "無関係施策：緑茶飲料の季節限定パッケージ発売")],
            "cause_material_cost_and_weak_yen", "effect_price_hike_on_flagship_foods"
        ),
        (
            "重症アレルギー緊急救命処置",
            "【救急カルテ】『そばアレルゲン誤食により急速な呼吸困難と血圧急降下を伴うアナフィラキシーショック危機に陥った患者に対し、直ちにアドレナリン筋注（エピネフリン）を大腿部前外側へ緊急注射投与した。』",
            "救急医学分析：【患者が直面した危機的病態（Condition/Problem）】を選択してください。",
            "救急医学分析：【実施された救命介入治療（Intervention/Solution）】を選択してください。",
            [("condition_anaphylactic_shock_crisis", "危機病態：誤食によるアナフィラキシーショックと呼吸困難"), ("intervention_epinephrine_im_injection", "救命介入：大腿部へのアドレナリン（エピネフリン）緊急筋肉注射"), ("routine_annual_health_screening", "通常業務：一般的な定期健康診断の問診票記入")],
            "condition_anaphylactic_shock_crisis", "intervention_epinephrine_im_injection"
        ),
        (
            "通信基地局停電と非常発電",
            "【通信障害記録】『落雷による商用配電線の地絡事故により山間部通信基地局への商用受電が途絶したため、局舎内の自動始動ディーゼル非常用発電機が起動し、無線通信サービスの継続給電を維持した。』",
            "障害分析設問：【受電途絶の直接原因（Cause）】を選択してください。",
            "障害分析設問：【実行された復旧措置・成果（Effect/Solution）】を選択してください。",
            [("cause_lightning_strike_ground_fault", "直接原因：落雷による商用配電線の地絡事故と給電途絶"), ("effect_diesel_generator_backup_power", "対処成果：非常用ディーゼル発電機自動始動による無線給電維持"), ("trim_branches_along_highway", "別個作業：国道沿いの街路樹剪定作業の完了")],
            "cause_lightning_strike_ground_fault", "effect_diesel_generator_backup_power"
        ),
        (
            "ソフトウェア脆弱性とセキュリティパッチ",
            "【セキュリティ勧告】『認証トークンの検証ルーチンにバッファオーバーフロー脆弱性が存在したため、攻撃者による遠隔コード実行の脅威が生じていたが、セキュリティ修正パッチv2.4を適用して脆弱性を恒久修正した。』",
            "脆弱性分析：【特定されたシステム課題（Problem）】を選択してください。",
            "脆弱性分析：【適用された恒久解決策（Solution）】を選択してください。",
            [("problem_buffer_overflow_vulnerability", "システム課題：認証トークン検証時のバッファオーバーフロー欠陥"), ("solution_apply_security_patch_v24", "恒久解決策：セキュリティ修正パッチv2.4の適用とコード修正"), ("upgrade_office_monitors_to_4k", "社内備品：事務用液晶モニターの解像度向上")],
            "problem_buffer_overflow_vulnerability", "solution_apply_security_patch_v24"
        ),
        (
            "水道水濁り水と排水フラッシング",
            "【上水道点検】『水道本管の緊急修繕に伴う急激な水流逆転により管底の鉄錆堆積物が巻き上がって赤水（濁水）が発生したため、消火栓管末ドレン弁を開放して配管内の濁水を全量強制フラッシング排出した。』",
            "水道工学分析：【濁水発生の原因（Cause）】を選択してください。",
            "水道工学分析：【濁水除去の対処措置（Solution/Action）】を選択してください。",
            [("cause_water_hammer_rust_churn", "発生原因：水流逆転による管底鉄錆堆積物の巻き上がり"), ("solution_hydrant_drain_flushing", "対処措置：消火栓ドレン弁開放による管内濁水の強制排水フラッシング"), ("issue_monthly_water_utility_bill", "庶務事務：当月分水道料金検針票のポスティング")],
            "cause_water_hammer_rust_churn", "solution_hydrant_drain_flushing"
        ),
        (
            "物流倉庫誤出荷とバーコード検品",
            "【物流品質会議】『類似品番商品の棚番接近配置によるピッキング誤認出荷が頻発していた問題に対し、ハンディターミナルによる出荷前二重バーコードスキャン照合を義務化して誤出荷率をゼロにした。』",
            "品質分析設問：【発生していた現場課題（Problem）】を選択してください。",
            "品質分析設問：【導入された再発防止策（Solution）】を選択してください。",
            [("problem_proximity_picking_mismatch", "現場課題：類似品番商品の近接配置による誤ピッキング出荷頻発"), ("solution_double_barcode_scan_mandatory", "防止手段：ハンディ端末による出荷前二重バーコードスキャン義務化"), ("repaint_warehouse_exterior_walls", "営繕作業：倉庫外壁の遮熱塗料塗り替え工事")],
            "problem_proximity_picking_mismatch", "solution_double_barcode_scan_mandatory"
        ),
        (
            "航空便着陸やり直しと急激なウインドシア",
            "【運航報告】『滑走路進入直下に急激な低層ウインドシア（局地的な下降気流・風向急変）が発生し対気速度が急落したため、機長は即座に着陸を中止しエンジンスラスト全開でのゴーアラウンド（着陸復行）を敢行した。』",
            "運航分析設問：【着陸中止を強いられた気象的原因（Cause）】を選択してください。",
            "運航分析設問：【機長が選択した安全回避操縦（Action/Result）】を選択してください。",
            [("cause_low_level_windshear_downdraft", "気象要因：進入直下の低層ウインドシア発生と急激な対気速度低下"), ("action_immediate_go_around_max_thrust", "回避操縦：着陸即時中止と全推力によるゴーアラウンド着陸復行"), ("distribute_inflight_headphones", "客室サービス：機内オーディオ用ヘッドホンの回収配布")],
            "cause_low_level_windshear_downdraft", "action_immediate_go_around_max_thrust"
        ),
    ]

    for idx, (title, text_case, q_cause, q_effect, c_defs, t_cause, t_effect) in enumerate(causal_templates):
        choices = make_choices(c_defs)
        for rep in range(6):
            gid = f"tb_gen_xcau_{idx*6 + rep + 1:03d}"
            ctx = f"【技術事例分析: {title} (事例No.{idx*6+rep+1})】\n{text_case}"
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "general_choice", "general_category": "semantic_relation", "context": ctx, "question": q_cause, "choices": choices, "target": {"kind": "hard", "choice_id": t_cause}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "general_choice", "general_category": "semantic_relation", "context": ctx, "question": q_effect, "choices": choices, "target": {"kind": "hard", "choice_id": t_effect}})

    # Category 11: Exemption and Mandatory Polarity (Taxable vs Exempt, Mandatory vs Waived, 60 pairs = 120 records)
    exemption_polarity_templates = [
        (
            "消費税課税判定",
            "【税務規定】国内における事業者の資産の譲渡・役務提供は消費税課税対象。ただし居住用賃貸住宅の家賃は非課税。",
            "取引内容：都内オフィスビルの月額テナント賃料（商業用スペース貸付）。",
            "取引内容：個人が居住するワンルームマンションの月額居住用家賃。",
            "消費税区分判定：当該取引の消費税課税区分を選択してください。",
            [("tax_subject_taxable_transaction", "商業利用のため消費税の課税対象取引に該当する"), ("tax_exempt_non_taxable_transaction", "居住用住宅家賃のため消費税の非課税取引に該当する"), ("tax_confiscate_asset_penalty", "脱税とみなし資産全額を追徴没収する")],
            "tax_subject_taxable_transaction", "tax_exempt_non_taxable_transaction"
        ),
        (
            "入国検疫PCR検査",
            "【検疫規則】流行危険指定地域からの入国者は検疫所指定のPCR検査を義務付ける。非指定地域からの入国で証明書所持者は検疫検査を免除。",
            "渡航者状況：高リスク変異株流行指定国からの直行便帰国者。",
            "渡航者状況：安全指定地域からの帰国で有効な陰性証明書を所持。",
            "検疫措置判定：入国時の検疫検査要否を選択してください。",
            [("quarantine_test_mandatory", "流行指定地域からの入国のため検疫検査の受検を義務付ける"), ("quarantine_test_not_required", "安全地域かつ証明書所持のため検疫受検は不要・免除とする"), ("imprison_traveler_in_dungeon", "入国者を地下牢へ無期限収監する")],
            "quarantine_test_mandatory", "quarantine_test_not_required"
        ),
        (
            "銀行他行振込手数料",
            "【手数料規定】他行宛て電信振込は所定の手数料330円を徴収する。ただしプレミアム口座会員で月3回以内の振込は手数料無料。",
            "顧客ステータス：一般口座会員、他行宛て振込1回目。",
            "顧客ステータス：プレミアム会員、当月1回目の他行宛て振込。",
            "振込手数料判定：適用すべき振込手数料を選択してください。",
            [("transfer_fee_charged_standard", "一般会員のため規定の振込手数料330円を課金徴収する"), ("transfer_fee_zero_free", "プレミアム会員優遇枠内のため手数料ゼロ（無料）とする"), ("drain_entire_account_balance", "口座残高を全額国庫へ強制没収する")],
            "transfer_fee_charged_standard", "transfer_fee_zero_free"
        ),
        (
            "患者事前同意書取得",
            "【医療同意規程】侵襲的手術の実施に際しては患者または法定代理人の事前書面同意が必須。ただし生命危機が急迫し本人意識不明の緊急時は同意免除。",
            "患者状態：意識清明、予定されている白内障の日帰り手術。",
            "患者状態：交通事故多発外傷による出血性ショック意識不明、緊急開腹止血術。",
            "手術同意判定：手術前の書面同意取得の要否を選択してください。",
            [("consent_mandatory_prior", "予定手術のため術前の事前書面同意取得が必須である"), ("consent_not_required_emergency", "生命救急の緊急免責事由に該当するため同意取得なしで手術可能"), ("eject_patient_into_street", "患者を治療せず路傍へ投げ捨てる")],
            "consent_mandatory_prior", "consent_not_required_emergency"
        ),
        (
            "建築確認申請手続",
            "【建築基準法】都市計画区域内での建築物新築は着工前の建築確認申請が必須。ただし防火地域外の10平米以内の増築は確認申請不要。",
            "建築計画：準工業地域内における延床面積150平米の木造2階建て住宅新築。",
            "建築計画：防火指定なし区域の住宅敷地内における6平米の物置増築。",
            "建築行政判定：建築確認申請手続きの要否を選択してください。",
            [("building_permit_mandatory_prior", "新築工事のため着工前の建築確認申請が法的に必須である"), ("building_permit_exempt_small_addition", "適用除外の小規模増築に該当するため確認申請は不要・免除"), ("demolish_entire_neighborhood", "近隣家屋をすべてブルドーザーで倒壊させる")],
            "building_permit_mandatory_prior", "building_permit_exempt_small_addition"
        ),
        (
            "契約クーリングオフ",
            "【消費者保護】訪問販売による契約は契約書面受領から8日以内であれば無条件解除（クーリングオフ）可能。自ら店舗に来訪した店頭購入は対象外。",
            "契約形態：突然自宅に訪問してきた業者との屋根塗装リフォーム契約（3日前）。",
            "契約形態：家電量販店の店頭で店員と商談し現金購入したテレビ。",
            "解除権利判定：クーリングオフ制度の適用可否を選択してください。",
            [("cooling_off_valid_and_applicable", "訪問販売かつ期間内のためクーリングオフによる無条件解除が可能"), ("cooling_off_not_applicable_in_store", "店舗での店頭対面購入のためクーリングオフ適用対象外とする"), ("file_criminal_charges_on_buyer", "購入者を詐欺未遂容疑で刑事告訴する")],
            "cooling_off_valid_and_applicable", "cooling_off_not_applicable_in_store"
        ),
        (
            "食品アレルギー表示義務",
            "【食品表示基準】特定原材料8品目（卵、乳、小麦、そば等）を含む加工食品はアレルギー表示が義務。特定原材料非含有の生鮮野菜は表示不要。",
            "製造商品：原材料に小麦粉・全卵・バターを使用した洋菓子クッキー。",
            "製造商品：近郊農家から仕入れた未加工の生鮮泥付き長ネギ。",
            "食品表示判定：アレルギー特定原材料の義務表示要否を選択してください。",
            [("allergen_labeling_mandatory", "特定原材料（小麦・卵）を含むためアレルギー表示が義務である"), ("allergen_labeling_not_required", "単一生鮮農産物であり特定原材料非含有のため表示義務なし"), ("burn_food_processing_plant", "食品加工工場を放火焼却する")],
            "allergen_labeling_mandatory", "allergen_labeling_not_required"
        ),
        (
            "マイナンバー提出要求",
            "【番号利用法】源泉徴収票作成や社会保険手続きのため雇用主は従業員のマイナンバー提出を求める義務がある。私的な友人間の金銭貸借での収集は違法・禁止。",
            "収集場面：新卒採用した正社員の入社雇用手続きおよび社会保険加入。",
            "収集場面：同僚同士での飲み会代金の立て替え精算の送金。",
            "マイナンバー管理：個人番号の提出要請の適法性を選択してください。",
            [("my_number_collection_mandatory_legal", "雇用・税務法定事務のためマイナンバーの提出要請が適法・義務である"), ("my_number_collection_unlawful_prohibited", "法定事務に該当しない私的事由のため収集は違法・禁止である"), ("publish_my_numbers_on_billboards", "全社員のマイナンバーを街頭ビジョンで公開する")],
            "my_number_collection_mandatory_legal", "my_number_collection_unlawful_prohibited"
        ),
        (
            "深夜残業割増賃金",
            "【労働基準法】午後22時から午前5時までの労働は25%以上の深夜割増賃金の支払いが義務。日中時間帯の所定労働は深夜割増の対象外。",
            "勤務実績：午後23時から翌朝4時までの深夜メンテナンス作業。",
            "勤務実績：午前10時から午後17時までの日中オフィス勤務。",
            "給与計算判定：深夜労働割増賃金の支給要否を選択してください。",
            [("night_overtime_premium_mandatory", "法定深夜時間帯の労働のため25%以上の深夜割増手当支給が必須"), ("night_overtime_premium_not_applicable", "日中時間帯の労働のため深夜割増手当の支給対象外とする"), ("deduct_total_wages_to_zero", "基本給を含む全賃金を没収しゼロにする")],
            "night_overtime_premium_mandatory", "night_overtime_premium_not_applicable"
        ),
        (
            "公害環境アセスメント",
            "【環境影響評価法】出力10万kW以上の火力発電所新設は環境アセスメント手続きが義務。出力1,000kWの小型非常用発電設備はアセス対象外。",
            "事業計画：沿岸部における出力60万kWのLNG火力発電所新設工事。",
            "事業計画：総合病院の屋上における出力800kWの非常用発電機設置。",
            "環境法務判定：環境影響評価（アセスメント）手続きの要否を選択してください。",
            [("environmental_assessment_mandatory", "法定規模以上の大規模火力発電所のため環境アセス実施が義務である"), ("environmental_assessment_not_required", "小規模非常用設備のため環境影響評価手続きは不要・対象外"), ("submerge_entire_coastal_city", "沿岸都市全体を海面下へ水没させる")],
            "environmental_assessment_mandatory", "environmental_assessment_not_required"
        ),
    ]

    for idx, (title, rule, s1, s2, q, c_defs, t1, t2) in enumerate(exemption_polarity_templates):
        choices = make_choices(c_defs)
        for rep in range(6):
            gid = f"tb_gen_xpol_{idx*6 + rep + 1:03d}"
            ctx1 = f"【制度適用判定: {title}】\n{rule}\n事案：{s1}"
            ctx2 = f"【制度適用判定: {title}】\n{rule}\n事案：{s2}"
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "general_choice", "general_category": "policy_compliance", "context": ctx1, "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t1}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "general_choice", "general_category": "policy_compliance", "context": ctx2, "question": q, "choices": choices, "target": {"kind": "hard", "choice_id": t2}})

    # Category 12: Extreme Ranking Reverse Criteria (Lowest vs Highest, 60 pairs = 120 records)
    reverse_ranking_templates = [
        (
            "タスク緊急度選定",
            "タスクA：1ヶ月後に開催される社内レクリエーションの会場候補地選定（納期に十分な余裕あり）。\nタスクB：本日正午締切の全社売上確定報告書の提出（残り30分、遅延不可）。",
            "逆選定判定：【最も緊急度が低く、後回しにできるタスク】を選択してください。",
            "優先判定：【最も緊急度が高く、直ちに最優先で着手すべきタスク】を選択してください。",
            [("task_a_lowest_urgency", "タスクA：1ヶ月後のレクリエーション会場選定（最低緊急度・後回し可）"), ("task_b_highest_urgency", "タスクB：本日正午締切の売上確定報告書（最高緊急度・即時着手必須）"), ("task_c_medium_routine", "タスクC：明日の定期朝会の議題確認（標準的緊急度・通常処理）")],
            "task_a_lowest_urgency", "task_b_highest_urgency"
        ),
        (
            "情報機密性格付け",
            "文書X：自社ホームページで全世界に公開されている公式会社概要パンフレット。\n文書Y：次世代量子半導体の未公開設計図および最高機密ソースコード（社外秘・漏洩厳禁）。",
            "逆選定判定：【機密性レベルが最も低く、誰でも自由に閲覧可能な文書】を選択してください。",
            "保護判定：【機密性レベルが最も高く、最高水準の暗号化と厳重保護が求められる文書】を選択してください。",
            [("doc_x_lowest_confidentiality", "文書X：一般公開済みの会社概要パンフレット（最低機密・一般公開情報）"), ("doc_y_highest_confidentiality", "文書Y：次世代量子半導体設計図（最高機密・厳重漏洩防止情報）"), ("doc_z_internal_memo", "文書Z：社内向け食堂利用マナーの回覧メモ（部外秘・通常社内情報）")],
            "doc_x_lowest_confidentiality", "doc_y_highest_confidentiality"
        ),
        (
            "システム自動化度選定",
            "工程1：夜間の全自動バッチスクリプト処理（人手介入ゼロ、クラウド上で完全自動実行）。\n工程2：数十名の関係者間の利害対立を調整する現地対面調停会議（多大な人手工数と手動判断が必須）。",
            "逆選定判定：【人間の手動介入が不要で、完全に自動化されている工程】を選択してください。",
            "負荷判定：【最も多くの人手・手作業を要し、手動対応の負担が最大となる工程】を選択してください。",
            [("process_1_fully_automated", "工程1：夜間バッチスクリプト処理（人手介入ゼロ・完全自動化）"), ("process_2_manual_labor_required", "工程2：対立関係者間の現地対面調停（多大な手動人手工数が必要）"), ("process_3_semi_automated", "工程3：半自動入力フォームの人間による最終承認（部分自動化）")],
            "process_1_fully_automated", "process_2_manual_labor_required"
        ),
        (
            "財務投資リスク比較",
            "金融商品M：元本および利息支払いが国によって保証された短期国債（デフォルトリスク極小）。\n金融商品N：財務危機に瀕した新興ベンチャー企業の無担保劣後債（債務不履行リスクが極大）。",
            "逆選定判定：【元本毀損リスクが最も低く、最も安全な金融資産】を選択してください。",
            "投機判定：【債務不履行リスクが最も高く、元本喪失の危険性が最大の金融資産】を選択してください。",
            [("asset_m_lowest_risk_treasury", "金融商品M：短期国債（元本保証・信用リスク最低・最高安全性）"), ("asset_n_highest_risk_junk_bond", "金融商品N：破綻懸念ベンチャー劣後債（元本喪失リスク最大）"), ("asset_o_blue_chip_stock", "金融商品O：東証プライム上場大企業の優良配当株（中リスク中リターン）")],
            "asset_m_lowest_risk_treasury", "asset_n_highest_risk_junk_bond"
        ),
        (
            "医療トリアージ重症度",
            "患者P：指先の小さな擦り傷で出血も止まっておりバイタル完全安定（軽症・歩行可能）。\n患者Q：大動脈解離による激痛と意識レベル低下、血圧ショック状態（最重症・生命危機）。",
            "逆選定判定：【重症度が最も低く、待合室で後回し待機が可能な患者】を選択してください。",
            "救命判定：【直ちに集中治療室へ搬送すべき最重症（トリアージ赤）の患者】を選択してください。",
            [("patient_p_lowest_severity_green", "患者P：指先の小擦り傷（トリアージ緑・最低重症度・待機可能）"), ("patient_q_highest_severity_red", "患者Q：大動脈解離ショック（トリアージ赤・最高重症度・即時蘇生必須）"), ("patient_r_medium_yellow", "患者R：手首骨折の疑い（トリアージ黄・中等症・待機可能処置）")],
            "patient_p_lowest_severity_green", "patient_q_highest_severity_red"
        ),
        (
            "サイバーセキュリティ危険度",
            "事象S：社内Wikiの目次ページで文字化けが発生した（業務影響軽微、外部脅威なし）。\n事象T：基幹DBの全管理者パスワードがダークウェブ上に漏洩した（全社破滅的侵害危機）。",
            "逆選定判定：【セキュリティ脅威度が最も低く、システムへの実害が皆無な事象】を選択してください。",
            "緊急遮断判定：【セキュリティ脅威度が最大で、全社緊急事態宣言を発令すべき事象】を選択してください。",
            [("incident_s_lowest_threat_cosmetic", "事象S：Wikiの文字化け（セキュリティ脅威最低・単なる表示不具合）"), ("incident_t_highest_threat_catastrophic", "事象T：管理者権限情報の外部流出（セキュリティ脅威最大・壊滅的危機）"), ("incident_u_spam_email", "事象U：社員1名へのスパムメール着信（脅威度中・フィルター隔離済み）")],
            "incident_s_lowest_threat_cosmetic", "incident_t_highest_threat_catastrophic"
        ),
        (
            "サプライヤー調達リードタイム",
            "仕入先A：近隣自社倉庫からの即日納品（発注から納品まで所要時間2時間）。\n仕入先B：海外特注鋳造品で受注生産（発注から納品まで所要期間6ヶ月）。",
            "逆選定判定：【調達所要時間が最も短く、最短で納品される仕入先】を選択してください。",
            "長期判定：【調達に最も長い期間を要し、最長リードタイムとなる仕入先】を選択してください。",
            [("vendor_a_shortest_lead_time", "仕入先A：近隣自社倉庫（所要2時間・最短即時調達）"), ("vendor_b_longest_lead_time", "仕入先B：海外特注鋳造（所要6ヶ月・最長長期調達）"), ("vendor_c_standard_lead_time", "仕入先C：国内標準代理店（所要3営業日・標準調達）")],
            "vendor_a_shortest_lead_time", "vendor_b_longest_lead_time"
        ),
        (
            "航空機座席騒音レベル",
            "座席X：最前列プレミアムファーストクラス（防音構造・エンジンから最も離れた静寂空間）。\n座席Y：主翼真後ろのジェットエンジン排気口直近エコノミー席（エンジン轟音が最大）。",
            "逆選定判定：【機内騒音レベルが最も低く、最も静かな環境の座席】を選択してください。",
            "騒音判定：【ジェットエンジンの排気騒音が最も大きく、騒音レベルが最大の座席】を選択してください。",
            [("seat_x_quietest_first_class", "座席X：最前列プレミアム席（エンジンから最遠・騒音最小・最静寂）"), ("seat_y_loudest_engine_exhaust", "座席Y：エンジン排気直近席（エンジン直近・騒音最大・最大轟音）"), ("seat_z_standard_aisle", "座席Z：主翼前方中央通路側席（標準的騒音レベル）")],
            "seat_x_quietest_first_class", "seat_y_loudest_engine_exhaust"
        ),
        (
            "自然災害被害規模",
            "事象E：瞬間風速12mの心地よい春一番（看板の揺れのみ、家屋損壊ゼロ）。\n事象F：震度7の直下型大地震（大都市全域の家屋倒壊、橋梁崩落、大火災発生）。",
            "逆選定判定：【被害が最も軽微で、危険性が極小の自然現象】を選択してください。",
            "激甚判定：【破滅的な壊滅被害をもたらし、最大規模の災害となる事象】を選択してください。",
            [("disaster_e_minimal_impact_breeze", "事象E：春一番の強風（被害最小・危険性極小・安全）"), ("disaster_f_catastrophic_megaquake", "事象F：震度7直下型地震（被害最大・壊滅的激甚災害）"), ("disaster_g_localized_shower", "事象G：局地的な通り雨（軽度影響・一時的降雨）")],
            "disaster_e_minimal_impact_breeze", "disaster_f_catastrophic_megaquake"
        ),
        (
            "薬品保管温度要求",
            "薬品1：常温保管可能（15度〜25度の通常の室内薬品棚で安定）。\n薬品2：超極低温凍結保管が必須（マイナス80度のディープフリーザー保管必須）。",
            "逆選定判定：【温度管理の制約が最も緩く、通常の室温で保管可能な薬品】を選択してください。",
            "厳格判定：【最も過酷な極低温冷却が必要で、厳格な温度管理を要する薬品】を選択してください。",
            [("drug_1_easiest_room_temp", "薬品1：常温保存薬（15〜25度・最低管理制約・室温保管可能）"), ("drug_2_strictest_deep_freeze", "薬品2：ディープフリーザー保存薬（マイナス80度・最高厳格冷却必須）"), ("drug_3_standard_refrigerated", "薬品3：標準冷蔵保管薬（2〜8度・標準的冷蔵管理）")],
            "drug_1_easiest_room_temp", "drug_2_strictest_deep_freeze"
        ),
    ]

    for idx, (title, comp_text, q_min, q_max, c_defs, t_min, t_max) in enumerate(reverse_ranking_templates):
        choices = make_choices(c_defs)
        for rep in range(6):
            gid = f"tb_gen_xrnk_{idx*6 + rep + 1:03d}"
            ctx = f"【比較評価: {title}】\n{comp_text}"
            records.append({"id": f"{gid}_s1", "group_id": gid, "family": "general_choice", "general_category": "reverse_criterion", "context": ctx, "question": q_min, "choices": choices, "target": {"kind": "hard", "choice_id": t_min}})
            records.append({"id": f"{gid}_s2", "group_id": gid, "family": "general_choice", "general_category": "reverse_criterion", "context": ctx, "question": q_max, "choices": choices, "target": {"kind": "hard", "choice_id": t_max}})

    return records
