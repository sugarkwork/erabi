"""Family 6: general_choice (30 pairs, 60 cases) - Blind v3
Distribution: K=2 (5 pairs), K=4 (5 pairs), K=6 (5 pairs), K=8 (5 pairs), K=12 (5 pairs), K=16 (5 pairs)
Prefix: rc2b3_gen_
Optimized concise choice texts to guarantee strict token count <= 400 (< 512 limit).
"""

from typing import Any, Dict, List, Tuple
from blind_v2_data.family_general_choice import get_general_choice_pairs as get_v2_gen


def make_choices(c_defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in c_defs]


def get_general_choice_pairs() -> List[Dict[str, Any]]:
    # Base 01-20 from v2 (K=2, 4, 6, 8)
    v2_pairs = get_v2_gen()
    v3_pairs = []
    for c in v2_pairs:
        gid = c["group_id"].replace("rc2b_gen_", "")
        idx = int(gid)
        if idx < 20:
            c_new = dict(c)
            c_new["id"] = c["id"].replace("rc2b_gen_", "rc2b3_gen_")
            c_new["group_id"] = c["group_id"].replace("rc2b_gen_", "rc2b3_gen_")
            v3_pairs.append(c_new)

    # Group 20 with concise choices
    g20_choices = [
        {"id": "lawful_school_educational_exception", "text": "適法（第35条学校教育目的利用）"},
        {"id": "blatant_commercial_copyright_infringement", "text": "違法（商業無許諾公衆送信侵害）"},
        {"id": "lawful_private_reproduction_home", "text": "適法（私的使用目的複製）"},
        {"id": "lawful_quotation_article_32", "text": "適法（第32条公正な引用）"},
        {"id": "lawful_library_reproduction_31", "text": "適法（第31条公共図書館複写）"},
        {"id": "lawful_disability_accessible_37", "text": "適法（障害者支援複製翻案）"},
        {"id": "lawful_judicial_administrative_procedure", "text": "適法（司法・行政手続利用）"},
        {"id": "lawful_ai_training_data_30_4", "text": "適法（第30条の4AI機械学習利用）"}
    ]
    v3_pairs.append({
        "id": "rc2b3_gen_20_s1",
        "group_id": "rc2b3_gen_20",
        "family": "general_choice",
        "context": "著作権・コンテンツ利用許諾：『教育機関。“中学校の公民科授業において、最新の新聞論説記事をプリントし、クラス30名の生徒に教材として無償配布したい。”』",
        "question": "著作権法第35条（学校教育利用）判定：この利用態様における著作権法上の適法性判定を選択してください。",
        "choices": g20_choices,
        "target": {"kind": "hard", "choice_id": "lawful_school_educational_exception"}
    })
    v3_pairs.append({
        "id": "rc2b3_gen_20_s2",
        "group_id": "rc2b3_gen_20",
        "family": "general_choice",
        "context": "著作権・コンテンツ利用許諾：『営利企業。“他社が莫大な費用をかけて制作した有料映像ソフトを無断で全編動画サイトにアップロードし広告収入を得たい。”』",
        "question": "著作権法適法性判定：この利用態様における判定を選択してください。",
        "choices": g20_choices,
        "target": {"kind": "hard", "choice_id": "blatant_commercial_copyright_infringement"}
    })

    # --- K=12 (Concise choices: groups 21 to 25) ---
    k12_concise_defs = [
        (
            "21",
            "国際特許分類（IPC）セクション付与：『特許出願。“完全自動航行型電気推進コンテナ貨物船の自動衝突防止ステアリングおよび船位保持操舵装置に関する技術”。』",
            "IPC技術分野分類：この発明が属する主たる技術セクション分類を選択してください。",
            "国際特許分類（IPC）セクション付与：『特許出願。“新規なアミノ酸配列からなる難治性自己免疫疾患治療用モノクローナル抗体医薬組成物”。』\nIPC技術分野分類：この発明が属する主たる技術セクション分類を選択してください。",
            [
                ("ipc_b_performing_transporting", "セクションB：運輸・処理操作"),
                ("ipc_a_human_necessities", "セクションA：生活必需品・医薬品"),
                ("ipc_c_chemistry_metallurgy", "セクションC：化学・冶金"),
                ("ipc_d_textiles_paper", "セクションD：繊維・紙"),
                ("ipc_e_fixed_constructions", "セクションE：固定構造物・土木"),
                ("ipc_f_mechanical_engineering", "セクションF：機械工学・照明・加熱"),
                ("ipc_g_physics_optics_computing", "セクションG：物理学・光学・情報"),
                ("ipc_h_electricity_telecom", "セクションH：電気・通信・半導体"),
                ("ipc_non_technical_artistic", "非技術的文芸著作物"),
                ("ipc_business_method_pure", "純粋事業スキーム"),
                ("ipc_pure_mathematics_theory", "純粋数学理論アルゴリズム"),
                ("ipc_scientific_discovery_law", "自然法則の純粋発見")
            ],
            "ipc_b_performing_transporting", "ipc_a_human_necessities"
        ),
        (
            "22",
            "企業コンプライアンス相談：『営業社員より相談。“大型公共調達入札の直前に、発注先官公庁の担当課長から高級料亭での接待および現金100万円の謝礼提供を要求された。”』",
            "不正リスク分類：この事案の法的リスク区分として最も適切なものを選択してください。",
            "企業コンプライアンス相談：『研究員より相談。“自社が莫大な投資を行って取得した最先端半導体製造プロセスの極秘設計図面を、競合海外企業へ5000万円で売却する交渉を進めている。”』\n不正リスク分類：この事案の法的リスク区分として最も適切なものを選択してください。",
            [
                ("bribery_and_corruption_risk", "公務員贈収賄・腐敗防止法違反"),
                ("trade_secret_theft_espionage", "営業秘密侵害・産業スパイ行為"),
                ("cartel_bid_rigging_antitrust", "独禁法違反（入札談合・カルテル）"),
                ("insider_trading_market_abuse", "金商法違反（インサイダー取引）"),
                ("labor_standards_unpaid_overtime", "労働基準法違反（残業代未払い）"),
                ("consumer_misleading_labeling", "景表法違反（優良誤認表示）"),
                ("subcontract_act_delayed_payment", "下請法違反（代金支払遅延）"),
                ("personal_data_gdpr_privacy_leak", "個人情報保護法・プライバシー違反"),
                ("environmental_hazardous_waste_act", "廃棄物処理法違反（不法投棄）"),
                ("product_liability_safety_breach", "製造物責任法（PL法）違反"),
                ("foreign_exchange_export_control", "外為法違反（無許可軍事転用輸出）"),
                ("tax_evasion_falsified_accounting", "法人税法違反（不正会計・脱税）")
            ],
            "bribery_and_corruption_risk", "trade_secret_theft_espionage"
        ),
        (
            "23",
            "気象警報・特別警報発表区分：『気象庁発表。“数十年に一度の猛烈な集中豪雨により、大河川の本川が決壊し、広範囲で浸水深3m以上の浸水が急速に拡大、多数の住宅が孤立。”』",
            "防災気象警戒レベル：住民が直ちに取るべき行動段階区分として最も適切なものを選択してください。",
            "気象警報・特別警報発表区分：『気象庁発表。“大型の台風が3日後に本州へ接近する見込み。沿岸部ではうねりを伴う波の高さが3mに達する見通し。”』\n防災気象警戒レベル：住民が直ちに取るべき行動段階区分として最も適切なものを選択してください。",
            [
                ("level_5_emergency_safety_action", "警戒レベル5：緊急安全確保"),
                ("level_1_early_awareness", "警戒レベル1：早期注意情報"),
                ("level_2_evacuation_readiness", "警戒レベル2：大雨注意報・確認"),
                ("level_3_elderly_evacuation", "警戒レベル3：高齢者等避難"),
                ("level_4_general_evacuation", "警戒レベル4：避難指示（全員避難）"),
                ("level_volcanic_ash_fall", "火山噴火警戒・降灰予報"),
                ("level_tsunami_major_warning", "大津波警報（高台緊急避難）"),
                ("level_tornado_advisory", "竜巻注意情報（屋内退避）"),
                ("level_dense_fog_advisory", "濃霧注意情報（徐行要請）"),
                ("level_frost_crop_damage", "晩霜注意報（農作物防霜）"),
                ("level_heatstroke_alert_emergency", "熱中症警戒アラート"),
                ("level_snowstorm_blizzard_warning", "暴風雪警報（ホワイトアウト警戒）")
            ],
            "level_5_emergency_safety_action", "level_1_early_awareness"
        ),
        (
            "24",
            "金融商品取引適合性原則：『顧客情報。“78歳無職、年金収入のみ、投資経験ゼロ。元本保証のない商品は絶対に避けたいと希望。”』",
            "商品提案適合性判定：この顧客への提案商品として最も適切なものを選択してください。",
            "金融商品取引適合性原則：『顧客情報。“32歳会社員、年収800万円、余剰資金3000万円、先物・FX取引歴10年、高いレバレッジと元本毀損リスクを熟知。”』\n商品提案適合性判定：この顧客への提案商品として最も適切なものを選択してください。",
            [
                ("principal_guaranteed_bank_deposit", "元本保証型円定期預金・国債"),
                ("high_leverage_crypto_derivatives", "高レバレッジ暗号資産先物取引"),
                ("leveraged_bull_bear_etf", "レバレッジ型ブルベアETF"),
                ("unrated_subordinated_junk_bonds", "無格付け高利回り劣後債"),
                ("private_equity_venture_fund", "未公開ベンチャー株ファンド"),
                ("commodity_gold_oil_spread_futures", "商品先物取引（原油・金）"),
                ("inverse_vix_volatility_swap", "VIX指数ボラティリティスワップ"),
                ("emerging_market_currency_carry", "新興国通貨高金利預金"),
                ("structured_knock_in_bear_note", "ノックイン条項付き仕組み債"),
                ("real_estate_syndicate_mezzanine", "私募不動産メザニンローン"),
                ("carbon_credit_emissions_token", "民間炭素クレジット排出枠"),
                ("distressed_debt_restructuring_fund", "破綻懸念企業再生ファンド")
            ],
            "principal_guaranteed_bank_deposit", "high_leverage_crypto_derivatives"
        ),
        (
            "25",
            "食品表示基準アレルゲン特定原材料判定：『原材料。“小麦粉、脱脂粉乳、鶏卵、バター、砂糖、落花生（ピーナッツ）、食塩。”』",
            "法定表示義務アレルゲン特定原材料（8品目）：この製品において表示義務が生じる品目群を選択してください。",
            "食品表示基準アレルゲン特定原材料判定：『原材料。“白米、精製水、大豆、食塩、米麹。”』\n法定表示義務アレルゲン特定原材料（8品目）：この製品における法定表示義務品目（特定原材料）の有無を判定してください。",
            [
                ("mandated_wheat_dairy_egg_peanut", "義務品目：小麦・乳・卵・落花生（4品目）"),
                ("mandated_none_soy_is_recommended", "義務品目なし（大豆は推奨表示品目）"),
                ("mandated_soba_buckwheat_only", "義務品目：そばのみ"),
                ("mandated_crustacean_shrimp_crab", "義務品目：えび・かに"),
                ("mandated_walnut_only", "義務品目：くるみのみ"),
                ("mandated_pork_beef_chicken_all", "義務品目：豚肉・牛肉・鶏肉"),
                ("mandated_fish_salmon_roe_tuna", "義務品目：さけ・いくら・マグロ"),
                ("mandated_fruit_apple_banana_kiwi", "義務品目：りんご・バナナ・キウイ"),
                ("mandated_gelatin_sesame_almond", "義務品目：ゼラチン・ごま・アーモンド"),
                ("mandated_mollusk_squid_octopus", "義務品目：いか・たこ"),
                ("mandated_mushroom_matsutake", "義務品目：まつたけのみ"),
                ("mandated_yam_sweet_potato_taro", "義務品目：やまいものみ")
            ],
            "mandated_wheat_dairy_egg_peanut", "mandated_none_soy_is_recommended"
        ),
    ]

    for gid, ctx, q1, q2, choices_raw, t1, t2 in k12_concise_defs:
        choices = make_choices(choices_raw)
        v3_pairs.append({
            "id": f"rc2b3_gen_{gid}_s1",
            "group_id": f"rc2b3_gen_{gid}",
            "family": "general_choice",
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        v3_pairs.append({
            "id": f"rc2b3_gen_{gid}_s2",
            "group_id": f"rc2b3_gen_{gid}",
            "family": "general_choice",
            "context": ctx,
            "question": q2,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    # --- K=16 (Concise choices: groups 26 to 30) ---
    k16_menus = [
        ("mynumber_pin_reset_unlock", "暗証番号初期化・ロック解除"),
        ("rabies_dog_registration_tag", "狂犬病予防注射・犬登録"),
        ("resident_certificate_copy_issue", "住民票の写し交付請求"),
        ("seal_registration_certificate_issue", "印鑑登録証明書交付"),
        ("family_register_koseki_transcript", "戸籍謄本・抄本請求"),
        ("national_health_insurance_enroll", "国民健康保険加入・脱退"),
        ("national_pension_exemption_apply", "国民年金保険料免除申請"),
        ("nursery_school_childcare_admission", "認可保育所入所利用申込"),
        ("senior_care_insurance_certification", "要介護認定新規申請"),
        ("property_tax_evaluation_certificate", "固定資産税台帳証明交付"),
        ("garbage_oversized_bulky_booking", "粗大ごみ戸別収集予約"),
        ("water_service_open_close_move", "水道使用開始・中止届"),
        ("bicycle_parking_commuter_pass", "市営駐輪場定期利用申請"),
        ("fire_prevention_manager_notification", "防火管理者選任届"),
        ("commercial_business_permit_food", "飲食店営業許可申請"),
        ("public_library_interlibrary_loan", "図書館相互貸借取寄予約")
    ]

    k16_hs = [
        ("hs_ch85_electrical_batteries", "第85類：電気機器・蓄電池"),
        ("hs_ch03_fish_molluscs_seafood", "第03類：生鮮魚介類・ホタテ"),
        ("hs_ch87_motor_vehicles_parts", "第87類：乗用自動車・部分品"),
        ("hs_ch84_nuclear_reactors_machinery", "第84類：機械類・ボイラー"),
        ("hs_ch90_optical_medical_precision", "第90類：光学機器・医療機器"),
        ("hs_ch27_mineral_fuels_petroleum", "第27類：石油鉱物燃料・LNG"),
        ("hs_ch39_plastics_polymers", "第39類：プラスチック成形品"),
        ("hs_ch72_iron_and_steel", "第72類：鉄鋼・熱延鋼板"),
        ("hs_ch30_pharmaceutical_products", "第30類：医薬品・ワクチン"),
        ("hs_ch28_inorganic_chemicals", "第28類：無機化学品・硫酸"),
        ("hs_ch71_precious_stones_metals", "第71類：貴金属・金・宝飾品"),
        ("hs_ch44_wood_and_timber_charcoal", "第44類：木材・製材・合板"),
        ("hs_ch61_apparel_knitted_crocheted", "第61類：ニット衣類・セーター"),
        ("hs_ch22_beverages_spirits_vinegar", "第22類：飲料・アルコール酒類"),
        ("hs_ch88_aircraft_spacecraft", "第88類：航空機・宇宙飛行体"),
        ("hs_ch95_toys_games_sports", "第95類：玩具・ゲーム機・用具")
    ]

    k16_roles = [
        ("mlops_ai_inference_engineer", "MLOps・AI推論基盤エンジニア"),
        ("cyber_security_penetration_tester", "サイバーセキュリティ診断技術者"),
        ("frontend_react_ui_developer", "フロントエンドUI開発者"),
        ("backend_microservice_api_engineer", "バックエンドAPI設計者"),
        ("site_reliability_engineer_sre", "SRE・インフラ信頼性担当"),
        ("data_warehouse_bi_analyst", "データ基盤・BIアナリスト"),
        ("embedded_firmware_iot_developer", "組込みファームウェア開発者"),
        ("mobile_ios_android_app_engineer", "モバイルアプリ開発者"),
        ("qa_test_automation_engineer", "QA品質保証・テスト自動化"),
        ("database_administrator_dba", "DBA・データベース管理者"),
        ("cloud_network_architect_aws", "クラウドネットワーク設計者"),
        ("scrum_agile_product_owner", "アジャイルプロダクトオーナー"),
        ("technical_writer_doc_specialist", "テクニカルライター"),
        ("devops_ci_cd_release_manager", "CI/CDリリースエンジニア"),
        ("blockchain_smart_contract_dev", "ブロックチェーン監査開発者"),
        ("hardware_fpga_asic_designer", "FPGA論理回路設計者")
    ]

    k16_depts = [
        ("dept_physics_quantum_condensed", "物理学科（量子・物性物理）"),
        ("dept_history_japanese_medieval", "歴史学科（日本中世史）"),
        ("dept_chemistry_organic_synthesis", "化学科（有機合成・触媒）"),
        ("dept_biology_molecular_genetics", "生物学科（分子遺伝学）"),
        ("dept_mathematics_pure_algebra", "数学科（代数幾何・数論）"),
        ("dept_law_constitutional_jurisprudence", "法学科（憲法・公法）"),
        ("dept_economics_econometric_macro", "経済学科（計量経済学）"),
        ("dept_mechanical_robotics_fluid", "機械工学科（流体・ロボット）"),
        ("dept_electrical_electronic_semiconductor", "電気電子工学科（半導体回路）"),
        ("dept_civil_structural_earthquake", "社会基盤工学科（耐震都市）"),
        ("dept_medicine_cardiovascular_surgery", "医学科（循環器内科）"),
        ("dept_pharmacy_pharmacokinetics", "薬学科（臨床薬理学）"),
        ("dept_agriculture_crop_breeding", "応用生物学科（作物育種）"),
        ("dept_sociology_media_communication", "メディア学科（社会情報学）"),
        ("dept_philosophy_ethics_phenomenology", "哲学科（現象学・応用倫理）"),
        ("dept_linguistics_cognitive_phonetics", "言語学科（認知言語学）")
    ]

    k16_signs = [
        ("international_flight_transfer_shuttle", "国際線乗り継ぎ・連絡バス"),
        ("customs_declaration_red_channel", "税関検査・課税申告（赤）"),
        ("passport_control_automated_gate", "出入国審査・自動化ゲート"),
        ("baggage_claim_carousel_domestic", "受託手荷物受取所"),
        ("currency_exchange_and_bank_atm", "外貨両替・国際ATM"),
        ("duty_free_liquor_tobacco_shop", "免税店（酒・たばこ）"),
        ("airline_business_lounge_priority", "ビジネスクラスラウンジ"),
        ("quarantine_animal_plant_inspection", "動植物検疫カウンター"),
        ("railway_skyliner_express_station", "鉄道連絡・空港特急改札"),
        ("taxi_limousine_bus_ticket_curb", "リムジンバス・タクシー乗り場"),
        ("rental_car_pickup_counter", "レンタカー受付カウンター"),
        ("pocket_wifi_sim_card_vending", "海外用Wi-Fi・SIM自販機"),
        ("lost_and_found_police_box", "空港警察・遺失物センター"),
        ("oversized_baggage_cloak_storage", "大型手荷物一時預かり"),
        ("prayer_room_interfaith_silence", "プレイヤールーム（礼拝室）"),
        ("medical_clinic_first_aid_station", "空港診療所・救護室")
    ]

    k16_scenarios = [
        (
            "26",
            "自治体総合行政手続オンライン窓口：『市民申請。“マイナンバーカードの暗証番号を連続3回間違えてロックがかかってしまったため、ロック解除と再設定を行いたい。”』",
            "オンライン行政メニュー選定：この手続きを管轄するオンライン申請メニューを選択してください。",
            "自治体総合行政手続オンライン窓口：『市民申請。“自宅で飼育している生後91日以上の飼い犬の狂犬病予防注射済票の交付と飼い犬登録申請を行いたい。”』\nオンライン行政メニュー選定：この手続きを管轄するオンライン申請メニューを選択してください。",
            k16_menus, "mynumber_pin_reset_unlock", "rabies_dog_registration_tag"
        ),
        (
            "27",
            "国際貿易通関統計品目番号（HSコード類別）：『通関貨物申告。“日本から輸出される、ハイブリッド乗用車用のリチウムイオン蓄電池パック（容量85kWh、単体）”。』",
            "HS条約品目類別（類判定）：この輸出品目を分類すべき正しいHS類を選択してください。",
            "国際貿易通関統計品目番号（HSコード類別）：『通関貨物申告。“北海道の港から冷蔵コンテナで輸出される、未加工の殻付き生食用生鮮ホタテガイ”。』\nHS条約品目類別（類判定）：この輸出品目を分類すべき正しいHS類を選択してください。",
            k16_hs, "hs_ch85_electrical_batteries", "hs_ch03_fish_molluscs_seafood"
        ),
        (
            "28",
            "ITシステムエンジニアリング職種役割定義：『職務記述書。“機械学習モデル（LLMや画像モデル）の分散学習パイプライン構築、モデル量子化、TensorRT/ONNXを用いた高スループット推論サービングの設計実装を担当する。”』",
            "ITエンジニア専門職能選定：この職務に最も合致する専門エンジニア職種を選択してください。",
            "ITシステムエンジニアリング職種役割定義：『職務記述書。“ペネトレーションテスト（侵入テスト）、Webアプリケーション脆弱性診断、SOC監視体制構築、セキュリティインシデントフォレンジック分析を担当する。”』\nITエンジニア専門職能選定：この職務に最も合致する専門エンジニア職種を選択してください。",
            k16_roles, "mlops_ai_inference_engineer", "cyber_security_penetration_tester"
        ),
        (
            "29",
            "総合大学学術学部・専攻分類：『研究室紹介。“量子もつれを用いた長距離量子テレポーテーション実験、極低温下でのトポロジカル絶縁体超伝導状態の精密測定。”』",
            "学術専門専攻分類：この研究室が所属する学問領域・専攻として最も適切なものを選択してください。",
            "総合大学学術学部・専攻分類：『研究室紹介。“中世鎌倉幕府の守護・地頭制の成立過程における古文書史料批判と社会構造の変容分析。”』\n学術専門専攻分類：この研究室が所属する学問領域・専攻として最も適切なものを選択してください。",
            k16_depts, "dept_physics_quantum_condensed", "dept_history_japanese_medieval"
        ),
        (
            "30",
            "国際空港ターミナル旅客動線サイン案内：『旅客要求。“成田空港に到着した国際線トランジット客。預け入れ手荷物を最終目的地までスルーで預けた状態で、第1ターミナルから第2ターミナルの乗継便ゲートへ移動したい。”』",
            "空港旅客動線サイン選定：この旅客が従うべき空港内の標識案内を選択してください。",
            "国際空港ターミナル旅客動線サイン案内：『旅客要求。“海外旅行から日本に帰国した旅行者。スイスで購入した高級腕時計2点（総額300万円）を身に着けて入国する。”』\n空港旅客動線サイン選定：この旅客が従うべき空港内の標識案内を選択してください。",
            k16_signs, "international_flight_transfer_shuttle", "customs_declaration_red_channel"
        ),
    ]

    for gid, ctx, q1, q2, ch_raw, t1, t2 in k16_scenarios:
        choices = make_choices(ch_raw)
        v3_pairs.append({
            "id": f"rc2b3_gen_{gid}_s1",
            "group_id": f"rc2b3_gen_{gid}",
            "family": "general_choice",
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        v3_pairs.append({
            "id": f"rc2b3_gen_{gid}_s2",
            "group_id": f"rc2b3_gen_{gid}",
            "family": "general_choice",
            "context": ctx,
            "question": q2,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    return v3_pairs
