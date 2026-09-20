"""Family 6: general_choice (30 pairs, 60 cases) - Blind v4
Distribution: K=2 (5 pairs), K=4 (5 pairs), K=6 (5 pairs), K=8 (5 pairs), K=12 (5 pairs), K=16 (5 pairs)
Prefix: rc2b4_gen_
Zero inference during authoring; 100% fresh scenarios.
Concise choice texts for K=12 and K=16 to guarantee strict token count <= 350.
"""

from typing import Any, Dict, List, Tuple


def make_choices(c_defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in c_defs]


def get_general_choice_pairs() -> List[Dict[str, Any]]:
    pairs = []

    # --- K=2 (5 pairs: groups 01 to 05) ---
    k2_defs = [
        (
            "01",
            "前提事実：『佐藤教授は過去25年間、国内外のあらゆる物理学会年次大会に皆勤しており、一度の欠席記録もない』。",
            "検証仮説：『佐藤教授は先週開催された物理学会年次大会に間違いなく出席していた』。前提と仮説の論理的関係を判定せよ。",
            "検証仮説：『佐藤教授は先週開催された物理学会年次大会を旅行のため欠席していた』。前提と仮説の論理的関係を判定せよ。",
            [("nli_entailment", "含意関係（前提から確実に導かれる）"), ("nli_contradiction", "矛盾関係（前提と論理的に両立しない）")],
            "nli_entailment", "nli_contradiction"
        ),
        (
            "02",
            "事象の因果分析：『列島を覆った観測史上最強の寒波の襲来により、家庭用暖房需要が急伸し、電力需給逼迫警報が発令された』。",
            "要素関係の照合：『暖房需要急伸と電力需給逼迫警報の発令』に対して『最強の寒波の襲来』が果たす論理的役割を特定せよ。",
            "要素関係の照合：『最強の寒波の襲来』に対して『暖房需要急伸と電力需給逼迫警報の発令』が果たす論理的役割を特定せよ。",
            [("role_primary_cause", "直接の原因・契機"), ("role_result_consequence", "派生した結果・帰結")],
            "role_primary_cause", "role_result_consequence"
        ),
        (
            "03",
            "技術製品レビューにおける評価者の感情・評価トーンの極性分類。",
            "レビュー文：『革新的な排熱構造と洗練された操作体系が見事に融合しており、業界積年の難問を克服した出色の傑作である』。評価極性を判定せよ。",
            "レビュー文：『宣伝文句ばかりが先行し、実際には初期不良が頻発する極めて粗雑な作りで、購入したことを痛切に後悔している』。評価極性を判定せよ。",
            [("tone_positive_praise", "称賛・肯定的評価"), ("tone_negative_criticism", "酷評・否定的批判")],
            "tone_positive_praise", "tone_negative_criticism"
        ),
        (
            "04",
            "地域行政施策の構造分析：『旧市街商店街の再生を図るため、市は空き店舗改装に対する補助金支給制度を新設した』。",
            "目的・手段の判定：本施策において『空き店舗改装に対する補助金支給制度の新設』が位置づけられる役割を特定せよ。",
            "目的・手段の判定：本施策において『旧市街商店街の再生』が位置づけられる役割を特定せよ。",
            [("category_instrument_means", "達成のための具体的手段"), ("category_ultimate_goal", "目指すべき上位目的")],
            "category_instrument_means", "category_ultimate_goal"
        ),
        (
            "05",
            "概念間の包摂関係分析：『電子計算機中央処理装置（CPU）』と『算術論理演算装置（ALU）』の概念階層。",
            "関係の特定：『算術論理演算装置（ALU）』に対して『電子計算機中央処理装置（CPU）』が占める概念的階層を特定せよ。",
            "関係の特定：『電子計算機中央処理装置（CPU）』に対して『算術論理演算装置（ALU）』が占める概念的階層を特定せよ。",
            [("hierarchy_hypernym", "全体を包括する上位概念"), ("hierarchy_hyponym", "構成要素となる下位概念")],
            "hierarchy_hypernym", "hierarchy_hyponym"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k2_defs:
        pairs.append({
            "id": f"rc2b4_gen_{gid}_s1", "group_id": f"rc2b4_gen_{gid}", "family": "general_choice",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_gen_{gid}_s2", "group_id": f"rc2b4_gen_{gid}", "family": "general_choice",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=4 (5 pairs: groups 06 to 10) ---
    k4_defs = [
        (
            "06",
            "自然言語推論（NLI）タスク：前提文『展示会場のメインホールには最新型EV自動車が3台展示されている』。",
            "仮説文：『メインホールには少なくとも1台以上の乗り物が展示されている』。前提と仮説の論理的推論関係を判定せよ。",
            "仮説文：『メインホールには自動車は1台も置かれておらず完全に空室である』。前提と仮説の論理的推論関係を判定せよ。",
            [
                ("nli_label_entailment", "含意（真であることが論理的に必然）"),
                ("nli_label_contradiction", "矛盾（前提と絶対に両立しない）"),
                ("nli_label_neutral", "中立（真偽を判断する根拠不足）"),
                ("nli_label_irrelevant", "無関係（論理的対象が完全に乖離）")
            ],
            "nli_label_entailment", "nli_label_contradiction"
        ),
        (
            "07",
            "テキスト文書の文体および文書種別ジャンルの自動判定タスク。",
            "文書サンプル：『本稿では、有限要素法を用いた非線形弾塑性解析により、亀裂進展挙動の数値的シミュレーション結果を報告する』。文書ジャンルを分類せよ。",
            "文書サンプル：『今だけ限定！驚きの軽さと圧倒的な吸引力を両立した新次元掃除機が特別価格29,800円！今すぐお電話を！』。文書ジャンルを分類せよ。",
            [
                ("genre_academic_abstract", "学術論文要旨アブストラクト"),
                ("genre_advertising_copy", "商業宣伝セールスコピー"),
                ("genre_official_statute", "行政法規公用通達文"),
                ("genre_personal_epistle", "日常私信親愛レター")
            ],
            "genre_academic_abstract", "genre_advertising_copy"
        ),
        (
            "08",
            "製造業工場の生産性阻害要因（ボトルネック）の特定診断タスク。",
            "診断所見：『特定工程の熟練溶接工が定年退職し、代替作業員の技能不足により溶接不良率が前年比4倍に急増している』。主たる制約要因を特定せよ。",
            "診断所見：『完成品の品質・生産効率ともに最高水準にあるが、製品在庫が倉庫に山積みで卸先販路が極めて限定的である』。主たる制約要因を特定せよ。",
            [
                ("bottleneck_skilled_labor", "熟練技能人材の不足"),
                ("bottleneck_sales_channel", "販売流通チャネルの狭小"),
                ("bottleneck_raw_material", "原材料部材の調達遅延"),
                ("bottleneck_cash_flow", "運転資金の調達困難逼迫")
            ],
            "bottleneck_skilled_labor", "bottleneck_sales_channel"
        ),
        (
            "09",
            "ニュース速報記事の主たる報道分野（カテゴリ）の自動判定タスク。",
            "記事本文：『中央銀行は政策金利を0.25%引き上げる決定を下し、長期国債利回りの急上昇を受けて主要株価指数は全面安となった』。報道分野を分類せよ。",
            "記事本文：『温室効果ガス排出量実質ゼロに向け、洋上風力発電と次世代ペロブスカイト太陽電池の導入支援策を閣議決定した』。報道分野を分類せよ。",
            [
                ("news_cat_finance_market", "金融・株式市場経済"),
                ("news_cat_environment_energy", "環境・エネルギー政策"),
                ("news_cat_foreign_diplomacy", "国際外交・首脳会談"),
                ("news_cat_space_science", "宇宙開発・天文学探査")
            ],
            "news_cat_finance_market", "news_cat_environment_energy"
        ),
        (
            "10",
            "クラウドサービス利用者の問い合わせチケットの意図分類タスク。",
            "チケット内容：『昨晩のアップデート以降、請求管理ダッシュボードを開くとHTTP 500エラーが表示され画面が真っ白になります』。問い合わせ種別を特定せよ。",
            "チケット内容：『月間契約から年間契約に切り替えた場合の割引率と、部署追加時の追加シートライセンス料金体系を教えてください』。問い合わせ種別を特定せよ。",
            [
                ("ticket_bug_error_report", "システム不具合バグ報告"),
                ("ticket_pricing_plan_query", "料金プラン・ライセンス相談"),
                ("ticket_feature_proposal", "新規機能要望提案"),
                ("ticket_account_termination", "アカウント解約退会申込み")
            ],
            "ticket_bug_error_report", "ticket_pricing_plan_query"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k4_defs:
        pairs.append({
            "id": f"rc2b4_gen_{gid}_s1", "group_id": f"rc2b4_gen_{gid}", "family": "general_choice",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_gen_{gid}_s2", "group_id": f"rc2b4_gen_{gid}", "family": "general_choice",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=6 (5 pairs: groups 11 to 15) ---
    k6_defs = [
        (
            "11",
            "意思決定心理学における認知バイアスの類型同定タスク。",
            "事例記述：『自説を支持する肯定的データばかりを熱心に検索・引用し、自説を否定する有力な反証データを無意識に無視・軽視する』。該当する認知バイアスを特定せよ。",
            "事例記述：『既に巨額の資金と時間を投じて開発してきたプロジェクトであるため、事業の失敗が確実視されても開発を中止できない』。該当する認知バイアスを特定せよ。",
            [
                ("bias_confirmation", "確証バイアス"),
                ("bias_sunk_cost_fallacy", "サンクコスト効果（埋没費用）"),
                ("bias_normalcy", "正常性バイアス"),
                ("bias_anchoring", "アンカリング効果"),
                ("bias_bandwagon", "バンドワゴン効果"),
                ("bias_halo_effect", "ハロー効果（後光効果）")
            ],
            "bias_confirmation", "bias_sunk_cost_fallacy"
        ),
        (
            "12",
            "事業継続マネジメント（BCM）におけるリスク対応戦略の分類タスク。",
            "対応策：『工場火災による巨額の物的損害や操業停止損失に備え、大手損害保険会社と企業総合賠償責任保険を契約した』。リスク対応方針を分類せよ。",
            "対応策：『政情不安とテロの危険性が極めて高い危険地帯への新規工場進出計画そのものを白紙撤回し、完全に取りやめた』。リスク対応方針を分類せよ。",
            [
                ("risk_strategy_transfer", "リスク移転（保険付保・外部委託）"),
                ("risk_strategy_avoidance", "リスク回避（活動自体の取りやめ）"),
                ("risk_strategy_mitigation", "リスク低減（防護壁設置・訓練）"),
                ("risk_strategy_acceptance", "リスク受容（自己資本での許容保有）"),
                ("risk_strategy_dispersion", "リスク分散（拠点の地理的分散）"),
                ("risk_strategy_sharing", "リスク共有（JV共同出資）")
            ],
            "risk_strategy_transfer", "risk_strategy_avoidance"
        ),
        (
            "13",
            "企業間取引基本契約書における個別条項の法的分類タスク。",
            "契約条文：『本契約の履行過程で相手方から開示された一切の技術上・営業上の情報を厳重に秘匿し、第三者へ開示してはならない』。条項分類を特定せよ。",
            "契約条文：『当事者の一方が本契約の重大な義務に違反し、相当の期間を定めて催告したにも拘らず是正されないときは、直ちに本契約を解除できる』。条項分類を特定せよ。",
            [
                ("clause_confidentiality_nda", "秘密保持義務条項（NDA）"),
                ("clause_termination_breach", "契約解除事由条項"),
                ("clause_damages_liability_cap", "損害賠償責任上限条項"),
                ("clause_governing_law_forum", "準拠法および合意管轄裁判所条項"),
                ("clause_force_majeure", "不可抗力免責条項"),
                ("clause_intellectual_property", "知的財産権の帰属条項")
            ],
            "clause_confidentiality_nda", "clause_termination_breach"
        ),
        (
            "14",
            "都市計画法に基づく用途地域制限の指定区分分類タスク。",
            "地域特性：『主として低層住宅の良好な住居環境を保護するため指定され、高層ビルや大規模店舗の建設が厳格に禁止されている地域』。用途地域を特定せよ。",
            "地域特性：『主として商業その他の業務の利便を増進するため指定され、百貨店・飲食店・銀行・オフィスビルが高度に集積している地域』。用途地域を特定せよ。",
            [
                ("zoning_low_rise_residential", "第一種低層住居専用地域"),
                ("zoning_commercial_district", "商業地域"),
                ("zoning_quasi_industrial", "準工業地域"),
                ("zoning_urbanization_control", "市街化調整区域"),
                ("zoning_exclusive_industrial", "工業専用地域"),
                ("zoning_neighborhood_commercial", "近隣商業地域")
            ],
            "zoning_low_rise_residential", "zoning_commercial_district"
        ),
        (
            "15",
            "大規模災害・多数傷病者事故における医療トリアージ（START法）判定タスク。",
            "傷病者所見：『自発呼吸なし。気道確保を実施したところ微弱な自発呼吸が再開し、橈骨動脈拍動微弱、意識障害あり』。トリアージタッグ色を判定せよ。",
            "傷病者所見：『呼びかけに対し清明に応答し、下肢の擦過傷のみで自力で歩行して安全な広場へ移動できる』。トリアージタッグ色を判定せよ。",
            [
                ("triage_tag_red_immediate", "赤（最優先治療・緊急搬送）"),
                ("triage_tag_green_minor", "緑（軽症・保留歩行可能）"),
                ("triage_tag_yellow_delayed", "黄（待機可能・準緊急重症）"),
                ("triage_tag_black_deceased", "黒（不処置・死亡確認）"),
                ("triage_tag_white_uninjured", "白（非傷病・治療不要）"),
                ("triage_tag_purple_decontam", "紫（化学物質汚染除染優先）")
            ],
            "triage_tag_red_immediate", "triage_tag_green_minor"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k6_defs:
        pairs.append({
            "id": f"rc2b4_gen_{gid}_s1", "group_id": f"rc2b4_gen_{gid}", "family": "general_choice",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_gen_{gid}_s2", "group_id": f"rc2b4_gen_{gid}", "family": "general_choice",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=8 (5 pairs: groups 16 to 20) ---
    k8_defs = [
        (
            "16",
            "日本史における主要な時代区分および考古学・歴史的時期の特定タスク。",
            "時代所見：『打製石器から磨製石器へ移行し、縄文土器が製作され、狩猟採集・定住集落が営まれた約1万数千年前の時代』。時代名を特定せよ。",
            "時代所見：『源頼朝が幕府を開き、武家政権が誕生して御家人制度に基づく封建社会が確立された時代』。時代名を特定せよ。",
            [
                ("era_jomon_period", "縄文時代"),
                ("era_kamakura_period", "鎌倉時代"),
                ("era_yayoi_period", "弥生時代"),
                ("era_kofun_period", "古墳時代"),
                ("era_nara_period", "奈良時代"),
                ("era_heian_period", "平安時代"),
                ("era_muromachi_period", "室町時代"),
                ("era_edo_period", "江戸時代")
            ],
            "era_jomon_period", "era_kamakura_period"
        ),
        (
            "17",
            "ソフトウェア開発ライフサイクル（ウォーターフォール工程）の段階分類タスク。",
            "工程内容：『ユーザーやステークホルダーへのヒアリングを行い、システムが備えるべき業務機能や非機能要件を定義・文書化する』。工程を特定せよ。",
            "工程内容：『単体テストをパスした各独立モジュールを結合し、サブシステム間のデータ受け渡しやインターフェース整合性を検証する』。工程を特定せよ。",
            [
                ("sdlc_req_analysis", "要求分析・要件定義工程"),
                ("sdlc_integration_test", "結合テスト工程"),
                ("sdlc_basic_design", "基本設計工程"),
                ("sdlc_detail_design", "詳細設計工程"),
                ("sdlc_implementation", "実装コーディング工程"),
                ("sdlc_unit_test", "単体テスト工程"),
                ("sdlc_acceptance_test", "システム受入検証工程"),
                ("sdlc_ops_maintenance", "運用保守工程")
            ],
            "sdlc_req_analysis", "sdlc_integration_test"
        ),
        (
            "18",
            "組織行動学におけるリーダーシップ類型の分類タスク。",
            "リーダーの行動様式：『部下に細かな指示を与えず、目標と権限を委譲して意思決定の裁量を全面的に部下の自主性に任せる』。リーダーシップ型を特定せよ。",
            "リーダーの行動様式：『強いビジョンを掲げ、変革の意義を熱狂的に説き、組織全体の価値観や意識を根本から革新する』。リーダーシップ型を特定せよ。",
            [
                ("lead_delegating_style", "委任型リーダーシップ"),
                ("lead_transformational", "変革型リーダーシップ"),
                ("lead_directing_directive", "指示型リーダーシップ"),
                ("lead_coaching_persuasive", "説得指導型リーダーシップ"),
                ("lead_participative", "参加型リーダーシップ"),
                ("lead_autocratic", "専制型リーダーシップ"),
                ("lead_servant_supportive", "サーバント型リーダーシップ"),
                ("lead_bureaucratic_rules", "官僚型リーダーシップ")
            ],
            "lead_delegating_style", "lead_transformational"
        ),
        (
            "19",
            "企業財務諸表（貸借対照表・損益計算書）における会計勘定科目の大区分判定タスク。",
            "財務項目：『1年以内に現金化または費用化される見込みの売掛金、棚卸資産、受取手形などの資産項目』。勘定大区分を特定せよ。",
            "財務項目：『製品やサービスの製造・調達のために直接要した原材料費、労務費、外注加工費の総額』。勘定大区分を特定せよ。",
            [
                ("acc_current_assets", "流動資産"),
                ("acc_cost_of_goods_sold", "売上原価"),
                ("acc_non_current_assets", "固定資産"),
                ("acc_current_liabilities", "流動負債"),
                ("acc_long_term_liabilities", "固定負債"),
                ("acc_shareholders_equity", "株主資本・剰余金"),
                ("acc_operating_expenses", "販売費及び一般管理費"),
                ("acc_non_operating_income", "営業外収益")
            ],
            "acc_current_assets", "acc_cost_of_goods_sold"
        ),
        (
            "20",
            "情報セキュリティにおけるサイバーサイバー攻撃ベクターの分類タスク。",
            "攻撃手法：『Webアプリケーションの入力フォームに悪意あるデータベース操作命令を混入させ、不正に会員情報を全件奪取する』。攻撃手法を特定せよ。",
            "攻撃手法：『標的組織の従業員に実在の金融機関を騙った緊急確認メールを送信し、偽ログイン画面へ誘導してIDとパスワードを詐取する』。攻撃手法を特定せよ。",
            [
                ("cyber_sql_injection", "SQLインジェクション攻撃"),
                ("cyber_phishing_fraud", "フィッシング詐欺攻撃"),
                ("cyber_xss_scripting", "クロスサイトスクリプティング（XSS）"),
                ("cyber_ddos_flooding", "DDoS分散サービス拒否攻撃"),
                ("cyber_ransomware_encrypt", "ランサムウェア暗号化恐喝"),
                ("cyber_mitm_eavesdrop", "中間者攻撃（Man-in-the-Middle）"),
                ("cyber_zero_day_exploit", "ゼロデイ脆弱性攻撃"),
                ("cyber_dns_spoofing", "DNSスプーフィング偽装")
            ],
            "cyber_sql_injection", "cyber_phishing_fraud"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k8_defs:
        pairs.append({
            "id": f"rc2b4_gen_{gid}_s1", "group_id": f"rc2b4_gen_{gid}", "family": "general_choice",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_gen_{gid}_s2", "group_id": f"rc2b4_gen_{gid}", "family": "general_choice",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=12 (5 pairs: groups 21 to 25) Concise choices! ---
    k12_defs = [
        (
            "21",
            "黄道十二星座の天文位置判定タスク。",
            "特徴：春分点に位置し、ギリシャ神話の金色の羊に由来する黄道第1星座を特定せよ。",
            "特徴：秋分点に位置し、正義の女神アストライアの天秤に由来する黄道第7星座を特定せよ。",
            [
                ("zodiac_aries", "おひつじ座"),
                ("zodiac_libra", "てんびん座"),
                ("zodiac_taurus", "おうし座"),
                ("zodiac_gemini", "ふたご座"),
                ("zodiac_cancer", "かに座"),
                ("zodiac_leo", "しし座"),
                ("zodiac_virgo", "おとめ座"),
                ("zodiac_scorpio", "さそり座"),
                ("zodiac_sagittarius", "いて座"),
                ("zodiac_capricorn", "やぎ座"),
                ("zodiac_aquarius", "みずがめ座"),
                ("zodiac_pisces", "うお座")
            ],
            "zodiac_aries", "zodiac_libra"
        ),
        (
            "22",
            "日本の旧暦和風月名の同定タスク。",
            "季節：草木がいよいよ生い茂る月という意味を持つ、陰暦3月の和風月名を特定せよ。",
            "季節：師匠の僧侶も走り回るほど忙しい月という意味を持つ、陰暦12月の和風月名を特定せよ。",
            [
                ("lunar_yayoi", "弥生（3月）"),
                ("lunar_shiwasu", "師走（12月）"),
                ("lunar_mutsuki", "睦月（1月）"),
                ("lunar_kisaragi", "如月（2月）"),
                ("lunar_uzuki", "卯月（4月）"),
                ("lunar_satsuki", "皐月（5月）"),
                ("lunar_minazuki", "水無月（6月）"),
                ("lunar_fumizuki", "文月（7月）"),
                ("lunar_hazuki", "葉月（8月）"),
                ("lunar_nagatsuki", "長月（9月）"),
                ("lunar_kannazuki", "神無月（10月）"),
                ("lunar_shimotsuki", "霜月（11月）")
            ],
            "lunar_yayoi", "lunar_shiwasu"
        ),
        (
            "23",
            "日本標準産業分類の大分類同定タスク。",
            "業種：ソフトウェア開発、情報処理サービス、インターネット附随サービス業が属する産業大分類を特定せよ。",
            "業種：病院、診療所、介護老人保健施設、社会福祉事業所が属する産業大分類を特定せよ。",
            [
                ("ind_info_comm", "情報通信業"),
                ("ind_medical_welfare", "医療福祉業"),
                ("ind_agriculture", "農業林業"),
                ("ind_mining", "鉱業採石業"),
                ("ind_construction", "建設業"),
                ("ind_manufacturing", "製造業"),
                ("ind_utilities", "電気ガス業"),
                ("ind_transport", "運輸郵便業"),
                ("ind_wholesale_retail", "卸売小売業"),
                ("ind_finance_insurance", "金融保険業"),
                ("ind_real_estate", "不動産業"),
                ("ind_education", "教育学習支援業")
            ],
            "ind_info_comm", "ind_medical_welfare"
        ),
        (
            "24",
            "材料工学における主要金属・無機元素の特定タスク。",
            "元素特性：原子番号29、極めて高い電気伝導性と熱伝導率を持ち、電線や配管に汎用される赤色光沢の金属元素を特定せよ。",
            "元素特性：原子番号22、高比強度と卓越した耐食性を持ち、航空機機体や人工骨に多用される軽量遷移金属元素を特定せよ。",
            [
                ("elem_copper", "銅（Cu）"),
                ("elem_titanium", "チタン（Ti）"),
                ("elem_carbon", "炭素（C）"),
                ("elem_silicon", "ケイ素（Si）"),
                ("elem_iron", "鉄（Fe）"),
                ("elem_aluminum", "アルミニウム（Al）"),
                ("elem_nickel", "ニッケル（Ni）"),
                ("elem_gold", "金（Au）"),
                ("elem_platinum", "白金（Pt）"),
                ("elem_tungsten", "タングステン（W）"),
                ("elem_uranium", "ウラン（U）"),
                ("elem_gallium", "ガリウム（Ga）")
            ],
            "elem_copper", "elem_titanium"
        ),
        (
            "25",
            "地球科学における自然災害・気象現象の分類タスク。",
            "現象：熱帯海洋上で発生し、中心気圧が低下して最大風速17.2m/s以上となった猛烈な暴風雨を伴う熱帯低気圧を特定せよ。",
            "現象：海底地震や海底地滑りにより海水全体が押し上げられ、長波となって海岸に急激に押し寄せる大波を特定せよ。",
            [
                ("phenom_typhoon", "台風（熱帯低気圧）"),
                ("phenom_tsunami", "津波（海洋長波）"),
                ("phenom_tornado", "竜巻（局所突風）"),
                ("phenom_drought", "干魃（長期少雨）"),
                ("phenom_blizzard", "豪雪暴風雪"),
                ("phenom_thunderstorm", "雷雲突風豪雨"),
                ("phenom_dense_fog", "濃霧視程障害"),
                ("phenom_volcano_eruption", "火山噴火降灰"),
                ("phenom_landslide", "地滑り土石流"),
                ("phenom_cold_wave", "寒波極低温"),
                ("phenom_heat_wave", "熱波高温猛暑"),
                ("phenom_storm_surge", "高潮潮位上昇")
            ],
            "phenom_typhoon", "phenom_tsunami"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k12_defs:
        pairs.append({
            "id": f"rc2b4_gen_{gid}_s1", "group_id": f"rc2b4_gen_{gid}", "family": "general_choice",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_gen_{gid}_s2", "group_id": f"rc2b4_gen_{gid}", "family": "general_choice",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=16 (5 pairs: groups 26 to 30) Concise choices! ---
    k16_defs = [
        (
            "26",
            "16方位コンパスによる航路方位の幾何学的判定タスク。",
            "方位角：真北を0度として時計回りに45度の方位を特定せよ。",
            "方位角：真北を0度として時計回りに225度の方位を特定せよ。",
            [
                ("dir_ne", "北東"),
                ("dir_sw", "南西"),
                ("dir_n", "北"),
                ("dir_nne", "北北東"),
                ("dir_ene", "東北東"),
                ("dir_e", "東"),
                ("dir_ese", "東南東"),
                ("dir_se", "南東"),
                ("dir_sse", "南南東"),
                ("dir_s", "南"),
                ("dir_ssw", "南南西"),
                ("dir_wsw", "西南西"),
                ("dir_w", "西"),
                ("dir_wnw", "西北西"),
                ("dir_nw", "北西"),
                ("dir_nnw", "北北西")
            ],
            "dir_ne", "dir_sw"
        ),
        (
            "27",
            "16進数（Hexadecimal）1桁シンボルの10進数値対応タスク。",
            "数値照合：16進数のシンボル『A』に対応する10進数値を特定せよ。",
            "数値照合：16進数のシンボル『F』に対応する10進数値を特定せよ。",
            [
                ("hex_val_10", "10進数10"),
                ("hex_val_15", "10進数15"),
                ("hex_val_0", "10進数0"),
                ("hex_val_1", "10進数1"),
                ("hex_val_2", "10進数2"),
                ("hex_val_3", "10進数3"),
                ("hex_val_4", "10進数4"),
                ("hex_val_5", "10進数5"),
                ("hex_val_6", "10進数6"),
                ("hex_val_7", "10進数7"),
                ("hex_val_8", "10進数8"),
                ("hex_val_9", "10進数9"),
                ("hex_val_11", "10進数11"),
                ("hex_val_12", "10進数12"),
                ("hex_val_13", "10進数13"),
                ("hex_val_14", "10進数14")
            ],
            "hex_val_10", "hex_val_15"
        ),
        (
            "28",
            "日本の伝統色彩名（和色）の色彩同定タスク。",
            "色相特徴：タデ科の植物の葉を発酵させた染料に由来し、深く落ち着いた濃い青色を特定せよ。",
            "色相特徴：アカネの根で染め上げた、夕焼けのような深みのある鮮やかな赤色を特定せよ。",
            [
                ("color_indigo_ai", "藍色"),
                ("color_madder_akane", "茜色"),
                ("color_yamabuki", "山吹色"),
                ("color_moegi", "萌黄色"),
                ("color_fuji", "藤色"),
                ("color_sakura", "桜色"),
                ("color_kohaku", "琥珀色"),
                ("color_rikyu_grey", "利休鼠"),
                ("color_jet_black", "漆黒"),
                ("color_pure_white", "純白"),
                ("color_ni_iro", "丹色"),
                ("color_tsuyukusa", "露草色"),
                ("color_kogane", "黄金色"),
                ("color_shinku", "真紅"),
                ("color_asagi", "浅葱色"),
                ("color_bengara", "弁柄色")
            ],
            "color_indigo_ai", "color_madder_akane"
        ),
        (
            "29",
            "生化学におけるタンパク質構成アミノ酸の構造・性質同定タスク。",
            "側鎖構造：側鎖が水素原子（-H）のみで構成され、最も分子量が小さく不斉炭素を持たないアミノ酸を特定せよ。",
            "側鎖構造：側鎖にチオール基（-SH）を持ち、ジスルフィド結合（-S-S-）を形成して三次構造を安定化させるアミノ酸を特定せよ。",
            [
                ("amino_glycine", "グリシン"),
                ("amino_cysteine", "システイン"),
                ("amino_alanine", "アラニン"),
                ("amino_valine", "バリン"),
                ("amino_leucine", "ロイシン"),
                ("amino_isoleucine", "イソロイシン"),
                ("amino_proline", "プロリン"),
                ("amino_phenylalanine", "フェニルアラニン"),
                ("amino_tyrosine", "チロシン"),
                ("amino_tryptophan", "トリプトファン"),
                ("amino_serine", "セリン"),
                ("amino_threonine", "スレオニン"),
                ("amino_methionine", "メチオニン"),
                ("amino_asparagine", "アスパラギン"),
                ("amino_glutamine", "グルタミン"),
                ("amino_lysine", "リシン")
            ],
            "amino_glycine", "amino_cysteine"
        ),
        (
            "30",
            "コンピュータサイエンスにおける基本データ構造の特性同定タスク。",
            "操作特性：後入れ先出し（LIFO：Last In, First Out）の原則に従い、プッシュとポップ操作を行うデータ構造を特定せよ。",
            "操作特性：先入れ先出し（FIFO：First In, First Out）の原則に従い、エンキューとデキュー操作を行うデータ構造を特定せよ。",
            [
                ("ds_stack", "スタック"),
                ("ds_queue", "キュー"),
                ("ds_array", "配列"),
                ("ds_linked_list", "リンクリスト"),
                ("ds_ring_buffer", "リングバッファ"),
                ("ds_binary_search_tree", "二分探索木"),
                ("ds_red_black_tree", "赤黒木"),
                ("ds_b_tree", "B木"),
                ("ds_binary_heap", "バイナリヒープ"),
                ("ds_hash_table", "ハッシュテーブル"),
                ("ds_trie", "トライ木"),
                ("ds_graph_adj_list", "隣接リストグラフ"),
                ("ds_union_find", "素集合データ構造"),
                ("ds_bloom_filter", "ブルームフィルタ"),
                ("ds_segment_tree", "セグメント木"),
                ("ds_skip_list", "スキップリスト")
            ],
            "ds_stack", "ds_queue"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k16_defs:
        pairs.append({
            "id": f"rc2b4_gen_{gid}_s1", "group_id": f"rc2b4_gen_{gid}", "family": "general_choice",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_gen_{gid}_s2", "group_id": f"rc2b4_gen_{gid}", "family": "general_choice",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    return pairs
