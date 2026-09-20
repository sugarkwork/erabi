"""Family 6: general_choice (30 pairs, 60 cases)
Distribution: K=2 (5 pairs), K=4 (5 pairs), K=6 (5 pairs), K=8 (5 pairs), K=12 (5 pairs), K=16 (5 pairs)
Focus: Non-rule multi-choice tasks (NLI, support routing, intent classification, incident triage, policy classification)
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
            "前提文：『当社の提供するAPIサービスは、月間10万リクエストまでは完全無料で利用可能ですが、10万リクエストを超過した分については従量課金が発生します。』",
            "論理的帰結判定：以下の仮説の真偽を判定してください。\n仮説：『月間リクエスト数が5万回にとどまる利用者は、APIの利用料金を請求されない。』",
            "論理的帰結判定：以下の仮説の真偽を判定してください。\n仮説：『月間リクエスト数が何回であっても、すべての利用者に一律の基本料金が請求される。』",
            [("true_claim", "真（前提文から論理的に確実に導かれる）"), ("false_claim", "偽（前提文の内容と明らかに矛盾する）")],
            "true_claim", "false_claim"
        ),
        (
            "02",
            "前提文：『社内ネットワークへのリモートVPN接続を行う際には、パスワード認証に加えてスマートフォンアプリによるワンタイムパスワード（二要素認証）の入力が必須となります。』",
            "論理的帰結判定：以下の仮説の真偽を判定してください。\n仮説：『パスワードのみを入力し二要素認証を行わなかった場合、リモートVPN接続は完了しない。』",
            "論理的帰結判定：以下の仮説の真偽を判定してください。\n仮説：『パスワードさえ正しければ、二要素認証を行わなくても社内ネットワークへ自由に接続できる。』",
            [("true_claim", "真（前提文から論理的に確実に導かれる）"), ("false_claim", "偽（前提文の内容と明らかに矛盾する）")],
            "true_claim", "false_claim"
        ),
        (
            "03",
            "前提文：『本割引キャンペーンは、2026年10月1日以降に新規で定期購入をお申し込みいただいた初回のお客様のみを対象として適用されます。』",
            "論理的帰結判定：以下の仮説の真偽を判定してください。\n仮説：『2026年9月に既に定期購入を利用していた既存顧客には、本割引キャンペーンは適用されない。』",
            "論理的帰結判定：以下の仮説の真偽を判定してください。\n仮説：『過去数年間にわたって継続利用している既存会員も、本割引キャンペーンの対象に含まれる。』",
            [("true_claim", "真（前提文から論理的に確実に導かれる）"), ("false_claim", "偽（前提文の内容と明らかに矛盾する）")],
            "true_claim", "false_claim"
        ),
        (
            "04",
            "前提文：『航空機の手荷物検査において、100mlを超える液体物は保安検査場を通過できませんが、保安検査場通過後の免税店等で購入した飲料は機内へ持ち込みが可能です。』",
            "論理的帰結判定：以下の仮説の真偽を判定してください。\n仮説：『保安検査場を通過した後の制限エリア内売店で購入した500mlのペットボトル飲料は、機内に持ち込める。』",
            "論理的帰結判定：以下の仮説の真偽を判定してください。\n仮説：『自宅から持参した500mlの未開封ミネラルウォーターは、保安検査場をそのまま通過して機内へ持ち込める。』",
            [("true_claim", "真（前提文から論理的に確実に導かれる）"), ("false_claim", "偽（前提文の内容と明らかに矛盾する）")],
            "true_claim", "false_claim"
        ),
        (
            "05",
            "前提文：『当ホテルの駐車場は完全予約制となっており、宿泊予約とは別に事前に車両情報の登録と駐車枠の確保を行っていただく必要があります。』",
            "論理的帰結判定：以下の仮説の真偽を判定してください。\n仮説：『宿泊予約を完了していても、駐車場の事前予約を行っていなければ駐車スペースの利用は保証されない。』",
            "論理的帰結判定：以下の仮説の真偽を判定してください。\n仮説：『宿泊予約を完了した時点で、駐車場の事前予約や車両登録を行わなくても自動的に駐車スペースが確保される。』",
            [("true_claim", "真（前提文から論理的に確実に導かれる）"), ("false_claim", "偽（前提文の内容と明らかに矛盾する）")],
            "true_claim", "false_claim"
        ),
    ]

    # --- K=4 (5 pairs: groups 06 to 10) ---
    k4_defs = [
        (
            "06",
            "ユーザーからの問い合わせ：『先月解約したはずの有料会員プランの月額料金が、今月分のクレジットカード明細に再度引き落とされていました。確認と返金をお願いします。』",
            "カスタマーサポート窓口振り分け：この問い合わせを最初に担当すべき部署として最も適切なものを選択してください。",
            "ユーザーからの問い合わせ：『自社の業務用基幹システムと貴社サービスをOAuth2.0でシングルサインオン連携したいのですが、開発者向けAPI仕様書はどこにありますか？』\n担当窓口振り分け：この問い合わせに最も適切な窓口を選択してください。",
            [
                ("billing_refund", "請求・決済・返金窓口"),
                ("developer_api", "開発者向けAPI・技術連携窓口"),
                ("hardware_repair", "ハードウェア故障・物理修理窓口"),
                ("recruitment_hr", "採用・人事エントリー窓口")
            ],
            "billing_refund", "developer_api"
        ),
        (
            "07",
            "システム監視アラートログ：『全リージョン（US-East, EU-West, AP-North）のロードバランサーがヘルスチェックに失敗。主要WEBサービスおよび決済APIが全面アクセス不能。』",
            "インシデント緊急度トリアージ：上記アラートに対するインシデント重大度レベルを選択してください。",
            "システム監視アラートログ：『開発用ステージング環境の社内Wikiサーバーでディスク使用率が82%に到達。本番稼働サービスや一般顧客への影響は一切なし。』\nインシデント緊急度トリアージ：上記アラートに対するインシデント重大度レベルを選択してください。",
            [
                ("p0_critical_outage", "P0：致命的障害（全社主要サービス停止・即時全社召集）"),
                ("p1_major_degradation", "P1：大規模縮退（重要機能の部分不通・2時間以内対応）"),
                ("p2_minor_defect", "P2：軽微事象（冗長系縮退・翌営業日内対応）"),
                ("p3_info_warning", "P3：情報警告（社内開発環境の容量注意・計画的対応）")
            ],
            "p0_critical_outage", "p3_info_warning"
        ),
        (
            "08",
            "社内セキュリティ診断報告：『インターネットから認証なしでリモートコード実行が可能な深刻なゼロデイ脆弱性（CVSSスコア 9.8）が本番Webサーバーで確認された。』",
            "セキュリティ脅威レベル格付け：この脆弱性のリスクレーティングとして最も適切なものを選択してください。",
            "社内セキュリティ診断報告：『社内イントラネット限定の社内報表示画面において、HTMLタグの不適切なエスケープ（自己XSS、CVSSスコア 2.5）が発見された。』\nセキュリティ脅威レベル格付け：この脆弱性のリスクレーティングとして最も適切なものを選択してください。",
            [
                ("sev_critical", "緊急（Critical：即座にパッチ適用またはシステム隔離が必要）"),
                ("sev_high", "高（High：外部侵害リスクあり・数日以内の対策が必要）"),
                ("sev_medium", "中（Medium：条件付き悪用リスク・次期リリースで修正）"),
                ("sev_low", "低（Low：悪用困難または影響極小・定期保守で対応）")
            ],
            "sev_critical", "sev_low"
        ),
        (
            "09",
            "前提文：『この製品は、防塵・防水規格IP68に準拠しており、水深1.5メートルの真水に30分間浸漬しても内部に浸水しない構造となっています。』",
            "論理関係判定（NLI）：仮説文『この製品は雨天の屋外環境でも問題なく使用することができる。』に対する論理関係を選択してください。",
            "論理関係判定（NLI）：仮説文『この製品は水滴がわずかでも付着すると直ちにショートして内部回路が全壊する。』に対する論理関係を選択してください。",
            [
                ("entailment", "含意（前提文から論理的に導かれる）"),
                ("contradiction", "矛盾（前提文の内容と真っ向から衝突する）"),
                ("neutral", "中立（前提文の情報だけでは真偽を断定できない）"),
                ("unrelated", "無関係（前提文と論理的接点を持たない）")
            ],
            "entailment", "contradiction"
        ),
        (
            "10",
            "顧客発言ログ：『パスワードの再設定メールが届かないためログインできず、本日中に提出すべき確定申告の電子書類が作成できなくて非常に焦っています！』",
            "ユーザー感情・意図分類：発話者の主たる感情および意図状態として最も適切なものを選択してください。",
            "顧客発言ログ：『長年この家計簿アプリにお世話になっています。使いやすくて家計管理が劇的に楽になりました。開発チームの皆様、素晴らしいアプリをありがとうございます！』\nユーザー感情・意図分類：発話者の主たる感情および意図状態として最も適切なものを選択してください。",
            [
                ("urgent_distress_frustration", "切迫・焦燥・ログイン救済要請"),
                ("positive_gratitude_compliment", "感謝・好意的評価・開発者への賛辞"),
                ("cancellation_threat_angry", "怒号・契約即時解除の威嚇"),
                ("feature_request_casual", "将来機能追加の気さくな雑談提案")
            ],
            "urgent_distress_frustration", "positive_gratitude_compliment"
        ),
    ]

    # --- K=6 (5 pairs: groups 11 to 15) ---
    k6_defs = [
        (
            "11",
            "お客様サポートチケット：『新しく購入したWi-Fiルーターの初期設定を行いましたが、SSIDのパスワードを入力しても「認証に失敗しました」と表示されて繋がりません。』",
            "窓口分類：この問い合わせを最初に担当すべきカテゴリーを選択してください。",
            "お客様サポートチケット：『先月購入したスマートウォッチの画面に横線のノイズが走り、タッチパネルが全く反応しなくなりました。保証期間内ですので本体交換をお願いしたいです。』\n窓口分類：この問い合わせを最初に担当すべきカテゴリーを選択してください。",
            [
                ("network_setup_support", "Wi-Fi・ネットワーク接続設定サポート"),
                ("hardware_defect_warranty", "ハードウェア初期不良・無償修理交換窓口"),
                ("billing_credit_dispute", "請求金額相違・クレジットカード決済調査"),
                ("account_deletion_gdpr", "アカウント完全退会・個人情報消去申請"),
                ("corporate_sales_bulk", "法人大口導入・特別価格商談窓口"),
                ("press_public_relations", "広報メディア取材・プレスリリース窓口")
            ],
            "network_setup_support", "hardware_defect_warranty"
        ),
        (
            "12",
            "人事・総務申請区分：『従業員が業務中に階段で足を滑らせて転倒し、足首の骨折により全治1ヶ月の休業を要する怪我を負いました。労災保険の請求書類を作成したいです。』",
            "申請種別判定：人事総務システムで選択すべき届出申請区分を選択してください。",
            "人事・総務申請区分：『来年4月より海外支社（シンガポール現地法人）への3年間の出向が決まりました。赴任に伴う転居手当および語学研修支援の申請を行います。』\n申請種別判定：人事総務システムで選択すべき届出申請区分を選択してください。",
            [
                ("workers_compensation_accident", "業務上労働災害（労災）補償・休業損害申請"),
                ("overseas_assignment_relocation", "海外赴任・現地法人出向支援申請"),
                ("annual_paid_leave_carryover", "年次有給休暇残日数翌期繰越申請"),
                ("commuter_pass_fare_change", "通勤定期券区間変更・交通費改定申請"),
                ("marriage_congratulatory_gift", "本人慶弔・結婚祝金支給申請"),
                ("club_activity_subsidy_annual", "社内公認サークル・部活動年間活動費補助申請")
            ],
            "workers_compensation_accident", "overseas_assignment_relocation"
        ),
        (
            "13",
            "ITサービス運用ログ：『社内共有ファイルサーバーの特定のフォルダ「2026_経理」に対して、退職予定の社員アカウントから深夜に大量のファイル一括ダウンロード試行を検知。』",
            "セキュリティインシデント種別：検知された事象の分類として最も適切なものを選択してください。",
            "ITサービス運用ログ：『全社宛ての電子メールにおいて、取引先銀行を装った不審な送信元から「口座情報更新のお願い」というURL付きメールが数十名に着弾。』\nセキュリティインシデント種別：検知された事象の分類として最も適切なものを選択してください。",
            [
                ("insider_data_exfiltration_threat", "内部不正・退職者による機密データ持出試行"),
                ("phishing_credential_harvesting", "標的型フィッシング詐欺メール着弾事案"),
                ("ddos_volumetric_network_attack", "外部からの大規模分散型サービス妨害（DDoS）攻撃"),
                ("ransomware_crypto_infection", "ランサムウェアによるファイル暗号化破壊被害"),
                ("physical_tailgating_breach", "入退室ゲートにおける共連れ不正侵入検知"),
                ("hardware_fan_thermal_runaway", "サーバーラック内ファンの物理的経年回転不良")
            ],
            "insider_data_exfiltration_threat", "phishing_credential_harvesting"
        ),
        (
            "14",
            "EC物流倉庫作業指示：『商品バーコードをスキャンしたところ、該当商品の賞味期限が「本日より30日後」となっており、出荷基準（残存60日以上）を下回っていました。』",
            "在庫管理アクション：検品スタッフが取るべき最も適切な処置を選択してください。",
            "EC物流倉庫作業指示：『ピッキングした商品の段ボール外装に破れがあり、中の化粧箱の角が潰れて変形しています。』\n在庫管理アクション：検品スタッフが取るべき最も適切な処置を選択してください。",
            [
                ("quarantine_short_expiry_lot", "賞味期限切迫品として出荷停止・隔離棚へ移動する"),
                ("damage_defect_routing", "外装破損・化粧箱不良品として交換検品へ回送する"),
                ("ship_to_customer_as_is", "欠陥を無視してそのまま通常通り顧客へ出荷する"),
                ("eat_item_in_warehouse", "スタッフがその場で開封して自家消費する"),
                ("falsify_barcode_label_sticker", "偽のバーコードシールを上から貼り付けて偽装する"),
                ("burn_entire_warehouse_inventory", "倉庫内の全商品を焼却処分する")
            ],
            "quarantine_short_expiry_lot", "damage_defect_routing"
        ),
        (
            "15",
            "宿泊施設フロント対応：『宿泊客よりチェックイン時。“愛犬のトイプードルと一緒に泊まりたいのですが、ペット同伴可能のお部屋は空いていますか？”とのこと。予約は一般客室。』",
            "宿泊施設案内：一般客室予約のお客様からのペット同伴申し出に対する適切な対応を選択してください。",
            "宿泊施設案内：全館完全禁煙の施設において、客室内で煙草の煙と吸い殻が確認された場合の対応を選択してください。",
            [
                ("check_pet_friendly_room_upgrade", "ペット専用客室の空き状況を確認し差額でのアップグレードをご案内する"),
                ("charge_smoking_cleaning_fine", "禁煙規約違反として特別脱臭清掃費用および違約金を請求する"),
                ("allow_pet_in_standard_room_secret", "清掃員に内緒で一般禁煙ルームにペットを無断で持ち込ませる"),
                ("abandon_pet_on_street", "ペットをホテル前の路上に放流して置き去りにさせる"),
                ("shut_down_hotel_business_perm", "保健所へ営業許可取消を自主申請してホテルを閉館する"),
                ("force_guest_sleep_in_lobby", "お客様にロビーの床で就寝するよう命じる")
            ],
            "check_pet_friendly_room_upgrade", "charge_smoking_cleaning_fine"
        ),
    ]

    # --- K=8 (5 pairs: groups 16 to 20) ---
    k8_defs = [
        (
            "16",
            "官公庁市民総合窓口：『来庁者。“先月子どもが生まれました。児童手当の新規受給申請と、出生届の提出後の住民票の写しを取得したいのですが、どの窓口に行けばよいですか。”』",
            "庁舎窓口案内：この来庁者に案内すべき最初の総合窓口を選択してください。",
            "官公庁市民総合窓口：『来庁者。“自宅の敷地に木造2階建て住宅を新築予定です。建築基準法に基づく建築確認申請書の提出と斜線制限の確認を行いたいです。”』\n庁舎窓口案内：この来庁者に案内すべき最初の総合窓口を選択してください。",
            [
                ("family_welfare_and_registry", "子育て支援・児童福祉課および市民課窓口"),
                ("building_guidance_and_urban", "建築指導課・都市計画課窓口"),
                ("tax_assessment_collection", "市民税・固定資産税・収税課窓口"),
                ("environment_waste_recycling", "環境衛生・一般廃棄物・リサイクル対策課窓口"),
                ("disaster_prevention_crisis", "防災安全・危機管理・消防総務課窓口"),
                ("commercial_tourism_promotion", "商工振興・観光プロモーション課窓口"),
                ("waterworks_sewerage_bureau", "上下水道局・給排水設備受付窓口"),
                ("election_commission_secretariat", "選挙管理委員会事務局窓口")
            ],
            "family_welfare_and_registry", "building_guidance_and_urban"
        ),
        (
            "17",
            "図書館図書管理システム：『寄贈図書受入審査。“1920年代に発行された地域郷土史の貴重な手書き古文書原本（劣化あり、重要文化財指定候補）”を受贈。』",
            "所蔵管理区分：この資料の配架・保存区分として最も適切なものを選択してください。",
            "図書館図書管理システム：『購入図書受入審査。“最新の今週発売の週間コミック雑誌および一般ファッション月刊誌の最新号”を受贈。』\n所蔵管理区分：この資料の配架・保存区分として最も適切なものを選択してください。",
            [
                ("special_rare_archival_vault", "特別郷土資料・貴重書閉架温湿度管理書庫"),
                ("periodical_magazine_reading_rack", "最新号逐次刊行物・一般雑誌開架ブラウジングコーナー"),
                ("general_open_stack_circulating", "一般図書開架書架（通常貸出可能コーナー）"),
                ("children_picture_book_room", "児童・乳幼児向け大型絵本コーナー"),
                ("audiovisual_media_booth", "CD・DVD・ブルーレイ視聴覚メディアブース"),
                ("large_print_barrier_free", "大活字本・点字・バリアフリー読書支援資料室"),
                ("digital_microfilm_reader", "官報・縮刷版新聞マイクロフィルム保管庫"),
                ("recycle_free_distribution_cart", "市民向けリサイクル無償譲渡ワゴン")
            ],
            "special_rare_archival_vault", "periodical_magazine_reading_rack"
        ),
        (
            "18",
            "総合病院トリアージ外来：『救急搬送患者。胸部激痛を訴え冷や汗、心電図にて広範なST上昇（急性心筋梗塞疑い）。血圧80/50mmHg。』",
            "院内初療診療科選定：直ちにコールすべき専門診療科として最も適切なものを選択してください。",
            "総合病院トリアージ外来：『初診患者。昨夜から右耳の閉塞感と回転性めまい、難聴を自覚し歩行がふらつく（突発性難聴疑い）。意識清明、バイタル安定。』\n院内初療診療科選定：直ちにコールすべき専門診療科として最も適切なものを選択してください。",
            [
                ("cardiovascular_emergency_intervention", "循環器内科・心臓血管カテーテル緊急治療班"),
                ("otolaryngology_head_neck", "耳鼻咽喉科・頭頸部外科"),
                ("orthopedic_trauma_surgery", "整形外科・外傷骨折治療班"),
                ("dermatology_allergy_clinic", "皮膚科・アレルギー疾患外来"),
                ("psychiatry_behavioral_medicine", "精神神経科・心身医療外来"),
                ("ophthalmology_vitreoretinal", "眼科・硝子体網膜専門外来"),
                ("pediatric_neonatal_care", "小児科・新生児集中治療外来"),
                ("dental_oral_maxillofacial", "歯科口腔外科・顎関節外来")
            ],
            "cardiovascular_emergency_intervention", "otolaryngology_head_neck"
        ),
        (
            "19",
            "大学入試出願資格審査：『出願者書類。“日本国内の高等学校を2026年3月に卒業見込みであり、調査書の評定平均値は4.5、英検準1級取得済み。”（一般公募推薦入試出願）』",
            "出願資格適格判定：この出願者の出願資格可否判定を選択してください。",
            "大学入試出願資格審査：『出願者書類。“中学校卒業後に就職し、高等学校卒業程度認定試験（高認）も未受験のまま出願してきた。”』\n出願資格適格判定：この出願者の出願資格可否判定を選択してください。",
            [
                ("eligible_recommendation_quota", "出願資格適合（公募推薦入試の受審要件を完全に満たす）"),
                ("ineligible_lacking_highschool_equiv", "出願資格不適合（高等学校卒業と同等以上の基礎資格を欠く）"),
                ("conditional_foreign_applicant", "留学生特別選抜枠への出願変更を要する条件付き適合"),
                ("adult_continuing_education_quota", "社会人特別選抜（実務経験3年以上必須）枠への該当"),
                ("athletic_scholarship_candidate", "体育会指定強化種目特待生枠への該当"),
                ("returnee_overseas_student_quota", "帰国生入試（外国学校在籍2年以上）枠への該当"),
                ("transfer_third_year_quota", "他大学2年修了者対象の3年次編入学枠への該当"),
                ("doctorate_postgraduate_quota", "大学院博士後期課程研究指導委託生枠への該当")
            ],
            "eligible_recommendation_quota", "ineligible_lacking_highschool_equiv"
        ),
        (
            "20",
            "著作権・コンテンツ利用許諾：『教育機関。“中学校の公民科授業において、最新の新聞論説記事をプリントし、クラス30名の生徒に教材として無償配布したい。”』",
            "著作権法第35条（学校教育利用）判定：この利用態様における著作権法上の適法性判定を選択してください。",
            "著作権・コンテンツ利用許諾：『営利企業。“他社が莫大な費用をかけて制作した有料映像ソフトを無断で全編動画サイトにアップロードし広告収入を得たい。”』\n著作権法適法性判定：この利用態様における判定を選択してください。",
            [
                ("lawful_school_educational_exception", "適法（著作権法第35条の学校教育機関における授業目的複製として無許諾・無償で利用可能）"),
                ("blatant_commercial_copyright_infringement", "完全違法（公衆送信権侵害・重大な刑事罰および損害賠償請求の対象となる海賊版侵害行為）"),
                ("lawful_private_reproduction_home", "適法（個人的または家庭内その他これに準ずる限られた範囲内での私的使用複製）"),
                ("lawful_quotation_article_32", "適法（報道・批評・研究のための正当な範囲内での公正な慣行に合致する引用）"),
                ("lawful_library_reproduction_31", "適法（公共図書館等における調査研究目的の図書一部分の複写提供）"),
                ("lawful_disability_accessible_37", "適法（視覚障害者・聴覚障害者等のための点字・拡大文字翻案提供）"),
                ("lawful_judicial_administrative_procedure", "適法（裁判手続・行政審判手続等の内部資料としての必要限度の複製）"),
                ("lawful_ai_training_data_30_4", "適法（著作権法第30条の4に基づく情報解析・AIモデル機械学習のための非享受利用）")
            ],
            "lawful_school_educational_exception", "blatant_commercial_copyright_infringement"
        ),
    ]

    # --- K=12 (5 pairs: groups 21 to 25) ---
    k12_defs = [
        (
            "21",
            "国際特許分類（IPC）セクション付与：『特許出願。“完全自動航行型電気推進コンテナ貨物船の自動衝突防止ステアリングおよび船位保持操舵装置に関する技術”。』",
            "IPC技術分野分類：この発明が属する主たる技術セクション分類を選択してください。",
            "IPC技術分野分類：『特許出願。“新規なアミノ酸配列からなる難治性自己免疫疾患治療用モノクローナル抗体医薬組成物”。』\nIPC技術分野分類：この発明が属する主たる技術セクション分類を選択してください。",
            [
                ("ipc_b_performing_transporting", "セクションB：処理操作・運輸（船舶操縦・車両・航空・分離混合）"),
                ("ipc_a_human_necessities", "セクションA：生活必需品（農水産・医薬品・医療器具・食品）"),
                ("ipc_c_chemistry_metallurgy", "セクションC：化学・冶金（無機化学・高分子化合物・合金製錬）"),
                ("ipc_d_textiles_paper", "セクションD：繊維・紙（糸・織物・製紙・縫製）"),
                ("ipc_e_fixed_constructions", "セクションE：固定構造物（建築・土木・掘削・基礎工事）"),
                ("ipc_f_mechanical_engineering", "セクションF：機械工学・照明・加熱・兵器（エンジン・ポンプ・弁）"),
                ("ipc_g_physics_optics_computing", "セクションG：物理学（光学・電子計測・コンピュータ・暗号）"),
                ("ipc_h_electricity_telecom", "セクションH：電気（電力網・半導体回路・無線通信・電池）"),
                ("ipc_non_technical_artistic", "非技術的文芸著作物（特許分類付与対象外）"),
                ("ipc_business_method_pure", "純粋事業スキーム（自然法則を利用した技術的思想を欠くため出願却下）"),
                ("ipc_pure_mathematics_theory", "純粋数学理論・抽象的計算アルゴリズム（単体では特許非該当）"),
                ("ipc_scientific_discovery_law", "自然界の客観的科学法則の純粋発見（特許付与対象外）")
            ],
            "ipc_b_performing_transporting", "ipc_a_human_necessities"
        ),
        (
            "22",
            "企業コンプライアンス相談：『営業社員より相談。“大型公共調達入札の直前に、発注先官公庁の担当課長から高級料亭での接待および現金100万円の謝礼提供を要求された。”』",
            "不正リスク分類：この事案の法的リスク区分として最も適切なものを選択してください。",
            "企業コンプライアンス相談：『研究員より相談。“自社が莫大な投資を行って取得した最先端半導体製造プロセスの極秘設計図面を、競合海外企業へ5000万円で売却する交渉を進めている。”』\n不正リスク分類：この事案の法的リスク区分として最も適切なものを選択してください。",
            [
                ("bribery_and_corruption_risk", "公務員贈収賄・腐敗防止法違反（重大な刑事罰および企業指名停止）"),
                ("trade_secret_theft_espionage", "営業秘密不正取得・不正競争防止法違反（産業スパイ重罪）"),
                ("cartel_bid_rigging_antitrust", "独占禁止法違反（入札談合・同業者カルテル協定）"),
                ("insider_trading_market_abuse", "金融商品取引法違反（未公開重要事実に基づくインサイダー取引）"),
                ("labor_standards_unpaid_overtime", "労働基準法違反（残業代未払い・36協定限度超過）"),
                ("consumer_misleading_labeling", "景品表示法違反（優良誤認・原産地虚偽表示）"),
                ("subcontract_act_delayed_payment", "下請代金支払遅延等防止法違反（買いたたき・支払遅延）"),
                ("personal_data_gdpr_privacy_leak", "個人情報保護法・GDPR違反（顧客データの無断目的外流出）"),
                ("environmental_hazardous_waste_act", "廃棄物処理法違反（有害産業廃棄物の無許可越境投棄）"),
                ("product_liability_safety_breach", "製造物責任法（PL法）違反（製品構造欠陥による対人事故損害）"),
                ("foreign_exchange_export_control", "外国為替及び外国貿易法（外為法）違反（軍事転用可能物資の無許可輸出）"),
                ("tax_evasion_falsified_accounting", "法人税法違反（架空経費計上・売上除外による脱税）")
            ],
            "bribery_and_corruption_risk", "trade_secret_theft_espionage"
        ),
        (
            "23",
            "気象警報・特別警報発表区分：『気象庁発表。“数十年に一度の猛烈な集中豪雨により、大河川の本川が決壊し、広範囲で浸水深3m以上の浸水が急速に拡大、多数の住宅が孤立。”』",
            "防災気象警戒レベル：住民が直ちに取るべき行動段階区分として最も適切なものを選択してください。",
            "気象警報・特別警報発表区分：『気象庁発表。“大型の台風が3日後に本州へ接近する見込み。沿岸部ではうねりを伴う波の高さが3mに達する見通し。”』\n防災気象警戒レベル：住民が直ちに取るべき行動段階区分として最も適切なものを選択してください。",
            [
                ("level_5_emergency_safety_action", "警戒レベル5：緊急安全確保（既に災害発生・命を守る最善の行動）"),
                ("level_1_early_awareness", "警戒レベル1：早期注意情報（台風接近等の最新気象情報への留意）"),
                ("level_2_evacuation_readiness", "警戒レベル2：大雨・洪水・高潮注意報（ハザードマップ・避難行動の確認）"),
                ("level_3_elderly_evacuation", "警戒レベル3：高齢者等避難（高齢者や避難に時間を要する者の早期避難）"),
                ("level_4_general_evacuation", "警戒レベル4：避難指示（対象地域の全住民が安全な場所へ全員避難）"),
                ("level_volcanic_ash_fall", "火山噴火警戒（火口周辺への立入規制・降灰予報）"),
                ("level_tsunami_major_warning", "大津波警報（3m超の津波来襲・高台への緊急避難）"),
                ("level_tornado_advisory", "竜巻注意情報（頑丈な建物内への退避・窓からの隔離）"),
                ("level_dense_fog_advisory", "濃霧注意情報（視程低下による自動車運転徐行要請）"),
                ("level_frost_crop_damage", "晩霜注意報（農作物凍霜害防止シート設置）"),
                ("level_heatstroke_alert_emergency", "熱中症警戒アラート（冷房の適切な使用・外出自粛）"),
                ("level_snowstorm_blizzard_warning", "暴風雪警報（不要不急の車両外出中止・ホワイトアウト警戒）")
            ],
            "level_5_emergency_safety_action", "level_1_early_awareness"
        ),
        (
            "24",
            "金融商品取引適合性原則：『顧客情報。“78歳無職、年金収入のみ、投資経験ゼロ。元本保証のない商品は絶対に避けたいと希望。”』",
            "商品提案適合性判定：この顧客への提案商品として最も適切なものを選択してください。",
            "金融商品取引適合性原則：『顧客情報。“32歳会社員、年収800万円、余剰資金3000万円、先物・FX取引歴10年、高いレバレッジと元本毀損リスクを熟知。”』\n商品提案適合性判定：この顧客への提案商品として最も適切なものを選択してください。",
            [
                ("principal_guaranteed_bank_deposit", "元本保証型円定期預金または個人向け国債"),
                ("high_leverage_crypto_derivatives", "高レバレッジ暗号資産・証拠金先物取引"),
                ("leveraged_bull_bear_etf", "原指数の3倍の値動きを目指すレバレッジ型ETF"),
                ("unrated_subordinated_junk_bonds", "無格付け新興国ハイイールド劣後債"),
                ("private_equity_venture_fund", "非上場スタートアップ特化型未公開株ファンド"),
                ("commodity_gold_oil_spread_futures", "商品先物（原油・穀物・金）現物受渡契約"),
                ("inverse_vix_volatility_swap", "VIX指数インバース型ボラティリティ・スワップ"),
                ("emerging_market_currency_carry", "新興国通貨超高金利外貨建て定期預金"),
                ("structured_knock_in_bear_note", "個別株ノックイン判定条項付き仕組み債"),
                ("real_estate_syndicate_mezzanine", "私募不動産メザニンローン型投資ファンド"),
                ("carbon_credit_emissions_token", "民間ボランタリー炭素クレジット排出枠トークン"),
                ("distressed_debt_restructuring_fund", "経営破綻懸念企業ディストレスト債権ファンド")
            ],
            "principal_guaranteed_bank_deposit", "high_leverage_crypto_derivatives"
        ),
        (
            "25",
            "食品表示基準アレルゲン特定原材料判定：『原材料。“小麦粉、脱脂粉乳、鶏卵、バター、砂糖、落花生（ピーナッツ）、食塩。”』",
            "法定表示義務アレルゲン特定原材料（8品目）：この製品において表示義務が生じる品目群を選択してください。",
            "食品表示基準アレルゲン特定原材料判定：『原材料。“白米、精製水、大豆、食塩、米麹。”』\n法定表示義務アレルゲン特定原材料（8品目）：この製品における法定表示義務品目（特定原材料）の有無を判定してください。",
            [
                ("mandated_wheat_dairy_egg_peanut", "義務品目表示：小麦、乳成分、卵、落花生の4品目を表示必須"),
                ("mandated_none_soy_is_recommended", "特定原材料（義務8品目）の該当なし（大豆は表示推奨20品目）"),
                ("mandated_soba_buckwheat_only", "義務品目表示：そばのみを表示必須"),
                ("mandated_crustacean_shrimp_crab", "義務品目表示：えび、かにの2品目を表示必須"),
                ("mandated_walnut_only", "義務品目表示：くるみのみを表示必須"),
                ("mandated_pork_beef_chicken_all", "義務品目表示：豚肉、牛肉、鶏肉の3品目を表示必須"),
                ("mandated_fish_salmon_roe_tuna", "義務品目表示：さけ、いくら、マグロの3品目を表示必須"),
                ("mandated_fruit_apple_banana_kiwi", "義務品目表示：りんご、バナナ、キウイの3品目を表示必須"),
                ("mandated_gelatin_sesame_almond", "義務品目表示：ゼラチン、ごま、アーモンドの3品目を表示必須"),
                ("mandated_mollusk_squid_octopus", "義務品目表示：いか、たこの2品目を表示必須"),
                ("mandated_mushroom_matsutake", "義務品目表示：まつたけのみを表示必須"),
                ("mandated_yam_sweet_potato_taro", "義務品目表示：やまいものみを表示必須")
            ],
            "mandated_wheat_dairy_egg_peanut", "mandated_none_soy_is_recommended"
        ),
    ]

    # --- K=16 (5 pairs: groups 26 to 30) ---
    k16_defs = [
        (
            "26",
            "自治体総合行政手続オンライン窓口：『市民申請。“マイナンバーカードの暗証番号を連続3回間違えてロックがかかってしまったため、ロック解除と再設定を行いたい。”』",
            "オンライン行政メニュー選定：この手続きを管轄するオンライン申請メニューを選択してください。",
            "自治体総合行政手続オンライン窓口：『市民申請。“自宅で飼育している生後91日以上の飼い犬の狂犬病予防注射済票の交付と飼い犬登録申請を行いたい。”』\nオンライン行政メニュー選定：この手続きを管轄するオンライン申請メニューを選択してください。",
            [
                ("mynumber_pin_reset_unlock", "マイナンバーカード電子証明書・暗証番号初期化ロック解除"),
                ("rabies_dog_registration_tag", "狂犬病予防注射済票交付・愛犬新規登録手続"),
                ("resident_certificate_copy_issue", "住民票の写し・住民票記載事項証明書交付請求"),
                ("seal_registration_certificate_issue", "印鑑登録証明書オンライン申請交付"),
                ("family_register_koseki_transcript", "戸籍全部事項証明書（戸籍謄本）・身分証明書請求"),
                ("national_health_insurance_enroll", "国民健康保険加入・脱退・被保険者証再交付"),
                ("national_pension_exemption_apply", "国民年金保険料免除・納付猶予特例申請"),
                ("nursery_school_childcare_admission", "認可保育所・認定こども園利用申込受入審査"),
                ("senior_care_insurance_certification", "要介護・要支援認定新規申請・介護保険証再交付"),
                ("property_tax_evaluation_certificate", "固定資産税課税台帳登録事項証明書交付"),
                ("garbage_oversized_bulky_booking", "粗大ごみ戸別収集予約・処理手数料納付"),
                ("water_service_open_close_move", "水道使用開始・中止・給水名義変更届"),
                ("bicycle_parking_commuter_pass", "市営自転車等駐車場定期利用申請・更新"),
                ("fire_prevention_manager_notification", "防火管理者選任届・消防計画作成届出"),
                ("commercial_business_permit_food", "飲食店営業許可・食品衛生管理者設置申請"),
                ("public_library_interlibrary_loan", "市営図書館相互貸借（ILL）資料取寄予約")
            ],
            "mynumber_pin_reset_unlock", "rabies_dog_registration_tag"
        ),
        (
            "27",
            "国際貿易通関統計品目番号（HSコード類別）：『通関貨物申告。“日本から輸出される、ハイブリッド乗用車用のリチウムイオン蓄電池パック（容量85kWh、単体）”。』",
            "HS条約品目類別（類判定）：この輸出品目を分類すべき正しいHS類を選択してください。",
            "国際貿易通関統計品目番号（HSコード類別）：『通関貨物申告。“北海道の港から冷蔵コンテナで輸出される、未加工の殻付き生食用生鮮ホタテガイ”。』\nHS条約品目類別（類判定）：この輸出品目を分類すべき正しいHS類を選択してください。",
            [
                ("hs_ch85_electrical_batteries", "第85類：電気機器及びその部分品（蓄電池・集積回路・半導体デバイス）"),
                ("hs_ch03_fish_molluscs_seafood", "第03類：魚及び甲殻類、軟体動物（生鮮ホタテ・サケ・エビ・カニ）"),
                ("hs_ch87_motor_vehicles_parts", "第87類：鉄道以外の車両及びその部分品（完成乗用車・トラック）"),
                ("hs_ch84_nuclear_reactors_machinery", "第84類：原子炉、ボイラー及び機械類（内燃機関・ポンプ・旋盤）"),
                ("hs_ch90_optical_medical_precision", "第90類：光学機器、写真用機器、医療用機器及び精密機器"),
                ("hs_ch27_mineral_fuels_petroleum", "第27類：鉱物性燃料、鉱物油及び歴青質物質（原油・LNG・石炭）"),
                ("hs_ch39_plastics_polymers", "第39類：プラスチック及びその製品（ポリエチレン・樹脂成形品）"),
                ("hs_ch72_iron_and_steel", "第72類：鉄鋼（鋼片・熱間圧延鋼板・ステンレス鋼条）"),
                ("hs_ch30_pharmaceutical_products", "第30類：医薬品（ワクチン・抗生物質・血清・包帯）"),
                ("hs_ch28_inorganic_chemicals", "第28類：無機化学品及び貴金属同位体（硫酸・水酸化ナトリウム）"),
                ("hs_ch71_precious_stones_metals", "第71類：天然真珠、貴石、貴金属及びその製品（金・プラチナ・宝飾品）"),
                ("hs_ch44_wood_and_timber_charcoal", "第44類：木材及びその製品並びに木炭（丸太・製材・合板）"),
                ("hs_ch61_apparel_knitted_crocheted", "第61類：衣類及び衣類附属品（メリヤス編み・ニットセーター）"),
                ("hs_ch22_beverages_spirits_vinegar", "第22類：飲料、アルコール及び食酢（清涼飲料水・日本酒・ワイン）"),
                ("hs_ch88_aircraft_spacecraft", "第88類：航空機、宇宙飛行体及びその部分品（人工衛星・ロケット）"),
                ("hs_ch95_toys_games_sports", "第95類：がん具、遊戯用具及び運動用具（テレビゲーム機・模型・ゴルフクラブ）")
            ],
            "hs_ch85_electrical_batteries", "hs_ch03_fish_molluscs_seafood"
        ),
        (
            "28",
            "ITシステムエンジニアリング職種役割定義：『職務記述書。“機械学習モデル（LLMや画像モデル）の分散学習パイプライン構築、モデル量子化、TensorRT/ONNXを用いた高スループット推論サービングの設計実装を担当する。”』",
            "ITエンジニア専門職能選定：この職務に最も合致する専門エンジニア職種を選択してください。",
            "ITシステムエンジニアリング職種役割定義：『職務記述書。“ペネトレーションテスト（侵入テスト）、Webアプリケーション脆弱性診断、SOC監視体制構築、セキュリティインシデントフォレンジック分析を担当する。”』\nITエンジニア専門職能選定：この職務に最も合致する専門エンジニア職種を選択してください。",
            [
                ("mlops_ai_inference_engineer", "MLOps・機械学習推論インフラストラクチャエンジニア"),
                ("cyber_security_penetration_tester", "サイバーセキュリティ・侵入脆弱性診断エンジニア"),
                ("frontend_react_ui_developer", "フロントエンド・UI/UX・Webアプリケーションエンジニア"),
                ("backend_microservice_api_engineer", "バックエンド・マイクロサービスAPIアーキテクト"),
                ("site_reliability_engineer_sre", "サイト信頼性エンジニア（SRE・Kubernetes運用）"),
                ("data_warehouse_bi_analyst", "データ基盤・ETLパイプライン・BIアナリスト"),
                ("embedded_firmware_iot_developer", "組込みファームウェア・リアルタイムOS（RTOS）開発者"),
                ("mobile_ios_android_app_engineer", "モバイルネイティブアプリケーション（iOS/Android）開発者"),
                ("qa_test_automation_engineer", "QA品質保証・テスト自動化フレームワークエンジニア"),
                ("database_administrator_dba", "リレーショナルDB管理スペシャリスト（DBA・性能調律）"),
                ("cloud_network_architect_aws", "クラウドネットワーク・DirectConnect・SDN設計者"),
                ("scrum_agile_product_owner", "アジャイル・スクラムプロダクトオーナー・PM"),
                ("technical_writer_doc_specialist", "テクニカルライター・APIドキュメンテーション担当"),
                ("devops_ci_cd_release_manager", "CI/CDパイプライン自動化・ビルドリリースエンジニア"),
                ("blockchain_smart_contract_dev", "ブロックチェーン・スマートコントラクト監査開発者"),
                ("hardware_fpga_asic_designer", "FPGA論理回路・ASICハードウェア設計エンジニア")
            ],
            "mlops_ai_inference_engineer", "cyber_security_penetration_tester"
        ),
        (
            "29",
            "総合大学学術学部・専攻分類：『研究室紹介。“量子もつれを用いた長距離量子テレポーテーション実験、極低温下でのトポロジカル絶縁体超伝導状態の精密測定。”』",
            "学術専門専攻分類：この研究室が所属する学問領域・専攻として最も適切なものを選択してください。",
            "総合大学学術学部・専攻分類：『研究室紹介。“中世鎌倉幕府の守護・地頭制の成立過程における古文書史料批判と社会構造の変容分析。”』\n学術専門専攻分類：この研究室が所属する学問領域・専攻として最も適切なものを選択してください。",
            [
                ("dept_physics_quantum_condensed", "理学部：物理学科（量子物理学・物性物理学専攻）"),
                ("dept_history_japanese_medieval", "文学部：歴史学科（日本中世史・史料批判専攻）"),
                ("dept_chemistry_organic_synthesis", "理学部：化学科（有機合成化学・触媒創薬専攻）"),
                ("dept_biology_molecular_genetics", "理学部：生物学科（分子遺伝学・細胞分化専攻）"),
                ("dept_mathematics_pure_algebra", "理学部：数学科（代数幾何学・数論専攻）"),
                ("dept_law_constitutional_jurisprudence", "法学部：法学科（憲法・公法学・法哲学専攻）"),
                ("dept_economics_econometric_macro", "経済学部：経済学科（計量経済学・マクロ動学専攻）"),
                ("dept_mechanical_robotics_fluid", "工学部：機械工学科（流体力学・ロボティクス専攻）"),
                ("dept_electrical_electronic_semiconductor", "工学部：電気電子工学科（半導体集積回路専攻）"),
                ("dept_civil_structural_earthquake", "工学部：社会基盤工学科（耐震構造・都市防災専攻）"),
                ("dept_medicine_cardiovascular_surgery", "医学部：医学科（循環器内科・胸部外科学専攻）"),
                ("dept_pharmacy_pharmacokinetics", "薬学部：薬学科（臨床薬理学・薬物動態学専攻）"),
                ("dept_agriculture_crop_breeding", "農学部：応用生物学科（作物育種学・植物病理専攻）"),
                ("dept_sociology_media_communication", "社会学部：メディア学科（情報社会学・計量世論分析専攻）"),
                ("dept_philosophy_ethics_phenomenology", "文学部：哲学科（現象学・現代応用倫理学専攻）"),
                ("dept_linguistics_cognitive_phonetics", "文学部：言語学科（認知言語学・実験音声学専攻）")
            ],
            "dept_physics_quantum_condensed", "dept_history_japanese_medieval"
        ),
        (
            "30",
            "国際空港ターミナル旅客動線サイン案内：『旅客要求。“成田空港に到着した国際線トランジット客。預け入れ手荷物を最終目的地までスルーで預けた状態で、第1ターミナルから第2ターミナルの乗継便ゲートへ移動したい。”』",
            "空港旅客動線サイン選定：この旅客が従うべき空港内の標識案内を選択してください。",
            "国際空港ターミナル旅客動線サイン案内：『旅客要求。“海外旅行から日本に帰国した旅行者。スイスで購入した高級腕時計2点（総額300万円）を身に着けて入国する。”』\n空港旅客動線サイン選定：この旅客が従うべき空港内の標識案内を選択してください。",
            [
                ("international_flight_transfer_shuttle", "国際線乗り継ぎ案内（International Flight Transfer / ターミナル連絡バス）"),
                ("customs_declaration_red_channel", "税関検査・課税申告手荷物受取（Goods to Declare / 赤の納税カウンター）"),
                ("passport_control_automated_gate", "出入国審査・顔認証自動化ゲート（Passport Control / Japanese Nationals）"),
                ("baggage_claim_carousel_domestic", "国内線受託手荷物受取所（Baggage Claim / ターンテーブル）"),
                ("currency_exchange_and_bank_atm", "外貨両替・トラベラーズチェック・国際ATMコーナー"),
                ("duty_free_liquor_tobacco_shop", "制限エリア内免税店（Duty Free Shop / 酒・たばこ・香水）"),
                ("airline_business_lounge_priority", "航空会社指定ビジネスクラス・上級会員専用ラウンジ"),
                ("quarantine_animal_plant_inspection", "動物検疫所・植物防疫所（Animal & Plant Quarantine）"),
                ("railway_skyliner_express_station", "鉄道連絡・空港特急成田エクスプレス・スカイライナー改札"),
                ("taxi_limousine_bus_ticket_curb", "空港リムジンバス乗車券販売所・タクシー乗り場"),
                ("rental_car_pickup_counter", "レンタカー各社受付カウンター・配車送迎乗り場"),
                ("pocket_wifi_sim_card_vending", "海外渡航用モバイルWi-Fiルーター受取・SIMカード自販機"),
                ("lost_and_found_police_box", "空港警察署・ターミナル案内所遺失物取扱センター"),
                ("oversized_baggage_cloak_storage", "大型手荷物一時預かり所・宅配スーツケース発送便"),
                ("prayer_room_interfaith_silence", "プレイヤールーム（礼拝室・各宗派共用瞑想室）"),
                ("medical_clinic_first_aid_station", "空港診療所・救急救護室・トラベルクリニック")
            ],
            "international_flight_transfer_shuttle", "customs_declaration_red_channel"
        ),
    ]

    all_defs = k2_defs + k4_defs + k6_defs + k8_defs + k12_defs + k16_defs
    for gid, ctx, q1, q2, choices_raw, t1, t2 in all_defs:
        choices = make_choices(choices_raw)
        pairs.append({
            "id": f"rc2b_gen_{gid}_s1",
            "group_id": f"rc2b_gen_{gid}",
            "family": "general_choice",
            "context": ctx,
            "question": q1,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b_gen_{gid}_s2",
            "group_id": f"rc2b_gen_{gid}",
            "family": "general_choice",
            "context": ctx,
            "question": q2,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": t2}
        })

    return pairs
