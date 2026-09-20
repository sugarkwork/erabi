"""RC2.1 Training Data Synthesis: Stream B — General Choice (225 pairs = 450 records).

Covers 8 core general choice categories with realistic, non-joke options and span-level semantic relations:
1. routing_triage: 業務振り分け・インシデント一次振り分け (25 pairs)
2. short_nli: 自然言語推論・含意関係・矛盾判定 (25 pairs)
3. intent_classification: ユーザー発話・リクエスト意図分類 (25 pairs)
4. semantic_relation: 直接スパン抽出型 因果関係・問題と解決策・前提条件 (50 pairs)
5. policy_compliance: セキュリティ・法務・社内規則順守 (25 pairs)
6. instruction_separation: 前提条件・指示文・無関係データの分離判定 (25 pairs)
7. negative_goal: 否定的選定（対象外・不要・違反しないもの） (25 pairs)
8. reverse_criterion: 逆判定（最低優先度・最も負担が少ない・軽微） (25 pairs)

Total: 225 pairs (450 records). All contrastive pairs have distinct targets for s1/s2.
"""

from typing import Any, Dict, List, Tuple
from pathlib import Path
import random
import sys

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.rc2_1_train_data.generate_general_expansion import generate_general_expansion


def make_choices(defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in defs]


def generate_general_stream_b(seed: int = 4004) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    records = []

    # Category 1: routing_triage (25 pairs)
    routing_scenarios = [
        (
            "基盤インフラ障害",
            "【システム監視通知】『DBレプリケーションの遅延が60秒を超過。読み取り専用スレーブへの参照で古いデータが表示されるリスクがあります。』",
            "【システム監視通知】『フロントエンドの静的アセット配信CDNでキャッシュヒット率が急低下。オリジンサーバーの負荷が増加しています。』",
            "インフラ担当割り当て：対応すべき専門エンジニアチームを選択してください。",
            [("team_database_reliability", "データベース信頼性エンジニアチーム（DBRE）へ配任"), ("team_edge_cdn_performance", "エッジネットワーク・CDN配信チームへ配任"), ("team_general_it_helpdesk", "社内IT総合ヘルプデスク窓口へ配任")],
            "team_database_reliability", "team_edge_cdn_performance"
        ),
        (
            "経理伝票処理",
            "【伝票回覧】『営業交通費の立替精算申請です。Suica利用履歴のPDFと訪問先打合せ記録が添付されています。』",
            "【伝票回覧】『開発用サーバーラックの年間保守契約更新に伴う請求書です。金額は税込み330万円で請求元押印済みです。』",
            "経理業務振り分け：適切な処理フローを選択してください。",
            [("workflow_expense_reimbursement", "従業員経費立替精算ラインで承認・振込処理"), ("workflow_vendor_accounts_payable", "取引先買掛金・請求書支払ラインで稟議確認・振込処理"), ("workflow_audit_compliance_hold", "社内規程確認のため監査保留ラインへ回送")],
            "workflow_expense_reimbursement", "workflow_vendor_accounts_payable"
        ),
        (
            "法務契約相談",
            "【法務相談】『新規提携先候補との秘密情報交換に先立ち、先方提示のNDA（秘密保持契約書）の条項レビューをお願いします。』",
            "【法務相談】『当社の独自アルゴリズムを用いた新機能について、特許出願の可能性と先行技術調査を依頼したいです。』",
            "法務チーム配任：対応すべき法務専門ユニットを選択してください。",
            [("legal_corporate_contract_review", "企業法務・取引契約審査ユニットへ依頼"), ("legal_intellectual_property_patents", "知財・特許戦略ユニットへ依頼"), ("legal_general_corporate_consult", "法務総合相談窓口へ回付")],
            "legal_corporate_contract_review", "legal_intellectual_property_patents"
        ),
        (
            "総務オフィス管理",
            "【社内リクエスト】『執務エリアの空調設定温度を2度下げてほしいです。室温が28度まで上昇し熱気を感じます。』",
            "【社内リクエスト】『新規配属メンバー用のデスクチェアが1脚不足しています。予備倉庫からの搬出と設置をお願いします。』",
            "総務作業振り分け：依頼内容に適した対応作業を選択してください。",
            [("facility_adjust_hvac_temperature", "ビル空調制御システムの設定変更を手配する"), ("facility_deploy_office_furniture", "備品倉庫から事務用椅子を搬出して指定座席へ設置する"), ("facility_general_inquiry_log", "総務庶務の定期巡回確認簿へ記録する")],
            "facility_adjust_hvac_temperature", "facility_deploy_office_furniture"
        ),
        (
            "顧客サポートトリアージ",
            "【問い合わせ】『注文した商品の配送状況を確認したいです。追跡番号を入力しても該当なしと表示されます。』",
            "【問い合わせ】『届いた衣料品のサイズが合わなかったため、別のサイズへの交換を希望しています。』",
            "カスタマーサポート仕分け：適切な案内手順を選択してください。",
            [("support_logistics_tracking_inquiry", "配送キャリア照会・荷物追跡ステータス確認窓口で案内"), ("support_product_exchange_returns", "返品・サイズ交換受付手続き窓口で案内"), ("support_general_faq_portal", "公式FAQ総合案内ページへ案内")],
            "support_logistics_tracking_inquiry", "support_product_exchange_returns"
        ),
    ]
    for idx, (title, c1, c2, q, c_defs, t1, t2) in enumerate(routing_scenarios):
        for rep in range(5):
            gid = f"tb_gen_rtg_{idx*5 + rep + 1:03d}"
            pfx = f"【チケット番号 TK-{idx*10+rep+100}】"
            choices = make_choices(c_defs)
            records.append({
                "id": f"{gid}_s1",
                "group_id": gid,
                "family": "general_choice",
                "general_category": "routing_triage",
                "context": f"{pfx} {c1}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2",
                "group_id": gid,
                "family": "general_choice",
                "general_category": "routing_triage",
                "context": f"{pfx} {c2}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    # Category 2: short_nli (25 pairs)
    nli_scenarios = [
        (
            "プロジェクト進捗論理関係",
            "【前提】すべてのマイルストーンが予定通り完了し、顧客の最終受入テストも満点合格した。\n【仮説】このプロジェクトの納品は成功裏に承認された。",
            "【前提】すべてのマイルストーンが予定通り完了し、顧客の最終受入テストも満点合格した。\n【仮説】顧客から致命的な不合格通知を受け取り、プロジェクトは頓挫した。",
            "自然言語推論：前提文から仮説文への論理的関係（含意・矛盾・中立）を判定してください。",
            [("nli_entailment", "含意（前提が正しければ仮説は必然的に真）"), ("nli_contradiction", "矛盾（前提が正しければ仮説は必然的に偽）"), ("nli_neutral", "中立（前提から仮説の真偽は判断不能）")],
            "nli_entailment", "nli_contradiction"
        ),
        (
            "システムセキュリティ論理関係",
            "【前提】サーバー室への入室には指紋認証と暗証番号の双方が必須である。\n【仮説】暗証番号を知らない人物はサーバー室に入室できない。",
            "【前提】サーバー室への入室には指紋認証と暗証番号の双方が必須である。\n【仮説】指紋認証も暗証番号も持たない部外者が自由にサーバー室へ入室できる。",
            "論理含意判定：前提と仮説の関係を選択してください。",
            [("nli_relationship_entailment", "含意（論理的に成立する）"), ("nli_relationship_contradiction", "矛盾（論理的に不成立である）"), ("nli_relationship_irrelevant", "中立・判断不能（前提情報のみでは決定できない）")],
            "nli_relationship_entailment", "nli_relationship_contradiction"
        ),
        (
            "気象と屋外イベント論理関係",
            "【前提】明日は台風が直撃するため、すべての屋外アクティビティは全面的に中止される。\n【仮説】明日は屋外アクティビティが一切行われない。",
            "【前提】明日は台風が直撃するため、すべての屋外アクティビティは全面的に中止される。\n【仮説】明日は青空の下で予定通り屋外サッカー大会が開催される。",
            "真偽推論判定：前提に対する仮説の論理的整合性を選択してください。",
            [("logical_status_entailed", "含意（前提から直接導かれる）"), ("logical_status_contradictory", "矛盾（前提と明らかに衝突する）"), ("logical_status_undecidable", "中立（前提から真偽を決定できない）")],
            "logical_status_entailed", "logical_status_contradictory"
        ),
        (
            "受講資格論理関係",
            "【前提】この講座を受講するにはPythonプログラミング経験が3年以上あることが唯一の条件である。\n【仮説】Python経験が4年あるプログラマはこの講座を受講可能である。",
            "【前提】この講座を受講するにはPythonプログラミング経験が3年以上あることが唯一の条件である。\n【仮説】プログラミング未経験で一切コードを書いたことがない人物でも受講要件を満たしている。",
            "論理検証：仮説が前提とどのように関係しているか判定してください。",
            [("hypothesis_is_entailed", "仮説は前提から含意される（真）"), ("hypothesis_is_contradicted", "仮説は前提と矛盾する（偽）"), ("hypothesis_is_unrelated", "中立（どちらとも言えない）")],
            "hypothesis_is_entailed", "hypothesis_is_contradicted"
        ),
        (
            "在庫管理論理関係",
            "【前提】倉庫内の特定ロット製品は昨夜の火災により全数が焼失した。\n【仮説】その特定ロットの製品は1つも残っておらず出荷できない。",
            "【前提】倉庫内の特定ロット製品は昨夜の火災により全数が焼失した。\n【仮説】その特定ロットの製品は完全な状態で全品即日納品可能である。",
            "推論判定：前提情報と仮説の関係を選択してください。",
            [("eval_logical_entailment", "含意（前提から確実に帰結する）"), ("eval_logical_contradiction", "矛盾（前提の事実と正反対である）"), ("eval_logical_neutral", "中立（前提から真偽の確定は不能）")],
            "eval_logical_entailment", "eval_logical_contradiction"
        ),
    ]
    for idx, (title, c1, c2, q, c_defs, t1, t2) in enumerate(nli_scenarios):
        for rep in range(5):
            gid = f"tb_gen_nli_{idx*5 + rep + 1:03d}"
            choices = make_choices(c_defs)
            records.append({
                "id": f"{gid}_s1",
                "group_id": gid,
                "family": "general_choice",
                "general_category": "short_nli",
                "context": f"【事例ID: NL-{idx*10+rep+1}】\n{c1}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2",
                "group_id": gid,
                "family": "general_choice",
                "general_category": "short_nli",
                "context": f"【事例ID: NL-{idx*10+rep+1}】\n{c2}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    # Category 3: intent_classification (25 pairs)
    intent_scenarios = [
        (
            "有料プラン契約に関する発話",
            "『来月から使う見込みがなくなったので、今月いっぱいで有料プランを解約してアカウントを削除したいです。』",
            "『現在スタンダードプランですが、ユーザー数が50名に増えたため、来期からエンタープライズプランに切り替えたいです。』",
            "発話意図分類：顧客の発話から真の意図を選択してください。",
            [("intent_subscription_cancellation", "契約の解約・退会・アカウント抹消の申し出"), ("intent_subscription_upgrade", "上位プランへのアップグレード・契約規模拡大の相談"), ("intent_account_status_inquiry", "利用履歴や請求明細の照会要求")],
            "intent_subscription_cancellation", "intent_subscription_upgrade"
        ),
        (
            "パスワード・認証に関する発話",
            "『スマートフォンの機種変更をしたため、二段階認証アプリの引き継ぎができなくなりました。再設定用のリンクを送ってください。』",
            "『請求先として登録しているクレジットカードの有効期限が切れたため、新しいカード番号に更新したいです。』",
            "要望分類：顧客の要求意図を選択してください。",
            [("intent_mfa_credentials_reset", "多要素認証（MFA）・ログイン資格情報の再設定要求"), ("intent_payment_method_update", "決済手段・クレジットカード情報の変更要求"), ("intent_account_profile_update", "登録氏名や連絡先メールアドレスの変更要求")],
            "intent_mfa_credentials_reset", "intent_payment_method_update"
        ),
        (
            "配送・受取に関する発話",
            "『本日指定で注文していた荷物がまだ届いていません。現在の荷物の現在地を至急教えてください。』",
            "『急な出張が入って受け取れなくなったため、受取日時を今週末の土曜日の午前中に変更してください。』",
            "配送意図分類：問い合わせの意図を選択してください。",
            [("intent_track_delayed_shipment", "遅延荷物の現在位置・配送状況の追跡確認"), ("intent_reschedule_delivery_time", "配送日時・受取日時の変更依頼"), ("intent_package_redirection", "配送先住所の変更・受取営業所の指定依頼")],
            "intent_track_delayed_shipment", "intent_reschedule_delivery_time"
        ),
        (
            "セミナー受講に関する発話",
            "『来週開催のオンラインセミナーに参加するためのZoomリンク案内メールが届いていません。再送をお願いします。』",
            "『参加を申し込んでいたセミナーですが、同日時に社内会議が入り都合がつかなくなったためキャンセルさせてください。』",
            "イベント対応分類：参加者の意図を選択してください。",
            [("intent_resend_webinar_invitation", "セミナー参加用URL・招待メールの再送要求"), ("intent_cancel_event_attendance", "セミナー参加申込みのキャンセル・辞退連絡"), ("intent_recording_archive_request", "セミナー見逃し配信・録画アーカイブの視聴申請")],
            "intent_resend_webinar_invitation", "intent_cancel_event_attendance"
        ),
        (
            "製品保証・修理に関する発話",
            "『購入から半年しか経っていませんが、突然電源が入らなくなりました。無償保証の対象として修理を依頼したいです。』",
            "『操作マニュアルの15ページに書かれている初期セットアップの手順が分かりにくいので補足説明してください。』",
            "サポート意図分類：顧客の主目的を選択してください。",
            [("intent_warranty_repair_request", "製品故障に伴う保証修理・点検の依頼"), ("intent_usage_instruction_clarification", "製品の使い方・操作手順に関する質問・解説要求"), ("intent_trade_in_estimate", "旧型機器の下取り・リサイクル査定の相談")],
            "intent_warranty_repair_request", "intent_usage_instruction_clarification"
        ),
    ]
    for idx, (title, c1, c2, q, c_defs, t1, t2) in enumerate(intent_scenarios):
        for rep in range(5):
            gid = f"tb_gen_int_{idx*5 + rep + 1:03d}"
            choices = make_choices(c_defs)
            records.append({
                "id": f"{gid}_s1",
                "group_id": gid,
                "family": "general_choice",
                "general_category": "intent_classification",
                "context": f"【顧客メッセージ受領】\n{c1}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2",
                "group_id": gid,
                "family": "general_choice",
                "general_category": "intent_classification",
                "context": f"【顧客メッセージ受領】\n{c2}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    # Category 4: semantic_relation (Span-level Extraction, 50 pairs = 100 records)
    # 10 distinct scenarios covering Cause/Effect, Problem/Solution, Prerequisite/Goal
    span_relation_scenarios = [
        (
            "サーバー主電源断線",
            "【障害報告】『データセンターの外部幹線ケーブルが掘削工事により切断された。その結果、無停電電源装置の容量枯渇に伴い、クラウド基盤全体が緊急停止した。』",
            "因果関係判定：クラウド基盤停止の直接の根本原因（Cause）を選択してください。",
            "因果関係判定：根本原因から引き起こされた直接的結果（Effect）を選択してください。",
            [("cause_excavation_cable_cut", "掘削工事に伴う外部幹線ケーブルの物理的切断"), ("effect_cloud_infrastructure_halt", "無停電電源枯渇に伴うクラウド基盤全体の緊急停止"), ("cause_cyber_attack_ddos", "外部ネットワークからの大規模DDoS攻撃")],
            "cause_excavation_cable_cut", "effect_cloud_infrastructure_halt"
        ),
        (
            "EC購入離脱改善",
            "【改善分析】『決済画面の入力ステップが多くユーザーが離脱していた課題に対し、ワンクリック決済機能を導入したところ、購買完了率が前年同期比で40%改善した。』",
            "施策関係判定：実施された具体的な改善施策（Solution）を選択してください。",
            "課題と施策判定：改善施策によって解決・解消された当初の課題（Problem）を選択してください。",
            [("sol_one_click_checkout", "ワンクリック決済機能の新規導入"), ("prob_high_checkout_abandonment", "決済画面の入力ステップ過多によるユーザーの途中離脱"), ("sol_mandatory_survey_modal", "購入前のアンケート回答強制画面の追加")],
            "sol_one_click_checkout", "prob_high_checkout_abandonment"
        ),
        (
            "DBスキーマ移行前提",
            "【作業手順書】『本番クラスタのスキーマ移行を実行するには、事前に対象テーブルの静止点確保と全スナップショットの取得完了が必須条件となる。』",
            "前提条件判定：スキーマ移行に着手するために満たすべき前提要件（Prerequisite）を選択してください。",
            "前提条件判定：前提条件が満たされた後に実行可能となる対象工程・目標（Target / Goal）を選択してください。",
            [("prereq_table_quiesce_snapshot", "対象テーブルの静止点確保と全スナップショット取得の完了"), ("goal_execute_schema_migration", "本番クラスタにおけるDBスキーマ移行の実行"), ("prereq_server_hardware_upgrade", "物理サーバーハードウェアの全台交換")],
            "prereq_table_quiesce_snapshot", "goal_execute_schema_migration"
        ),
        (
            "工場搬送ロボット停止",
            "【設備調査】『自動搬送ロボット（AGV）が誘導路で急停止した原因は、床面反射テープが摩耗により剥離し走行ラインをロストしたためである。』",
            "要因分析：自動搬送ロボットが急停止するに至った直接の原因（Cause）を選択してください。",
            "結果判定：センサー遮光・ライン喪失によって生じた工場の結果（Effect / Result）を選択してください。",
            [("cause_floor_tape_wear_peeling", "床面反射テープの経年摩耗による剥離・走行ライン喪失"), ("effect_agv_sudden_stoppage", "誘導路路上における自動搬送ロボット（AGV）の急停止"), ("cause_battery_spontaneous_combustion", "リチウムイオンバッテリーの熱暴走発火")],
            "cause_floor_tape_wear_peeling", "effect_agv_sudden_stoppage"
        ),
        (
            "経理伝票処理の自動化",
            "【DX推進報告】『紙の領収書の目視確認による月末残業の慢性化を解消するため、AI領収書OCRと自動消込エンジンを導入し、残業時間を75%削減した。』",
            "問題解決分析：業務効率化のために導入された解決手段（Solution）を選択してください。",
            "問題解決分析：解決施策によって解消された業務上のボトルネック・課題（Problem）を選択してください。",
            [("sol_ai_ocr_auto_reconciliation", "AI領収書OCRおよび自動消込エンジンの導入"), ("prob_manual_paper_overtime", "紙領収書の目視確認に伴う月末残業の慢性化"), ("sol_outsource_to_temp_agency", "派遣スタッフの増員による人海戦術対応")],
            "sol_ai_ocr_auto_reconciliation", "prob_manual_paper_overtime"
        ),
        (
            "専門資格受験要件",
            "【資格規定】『シニアデータサイエンティスト認定試験を受験するためには、実務経験5年以上および所定の高度機械学習講座の修了が前提条件として定められている。』",
            "要件関係判定：認定試験を受験するために要求される前提要件（Prerequisite）を選択してください。",
            "要件関係判定：前提要件を満たすことで到達できる目標（Goal）を選択してください。",
            [("prereq_5yr_experience_and_course", "実務経験5年以上および高度機械学習講座の修了"), ("goal_senior_ds_certification_exam", "シニアデータサイエンティスト認定試験の受験・資格取得"), ("prereq_doctoral_degree_in_physics", "物理学博士号の取得")],
            "prereq_5yr_experience_and_course", "goal_senior_ds_certification_exam"
        ),
        (
            "原材料高騰と製品改定",
            "【市況分析】『原油価格の高騰と急激な為替変動に伴う輸入コスト急増を受け、化学工業各社は主力樹脂製品の出荷価格を引き上げた。』",
            "因果構造判定：製品価格引き上げを引き起こした直接の外部要因（Cause）を選択してください。",
            "因果構造判定：複合的要因によって生じた市場の結果（Effect）を選択してください。",
            [("cause_crude_oil_and_fx_surge", "原油価格高騰および為替変動による輸入コストの急増"), ("effect_resin_product_price_hike", "化学工業各社による主力樹脂製品の出荷価格引き上げ"), ("cause_labor_union_nationwide_strike", "全社労働組合による無期限ストライキ")],
            "cause_crude_oil_and_fx_surge", "effect_resin_product_price_hike"
        ),
        (
            "重症アレルギー救急介入",
            "【臨床記録】『蜂刺傷によるアナフィラキシーで血圧低下と呼吸不全に陥った患者に対し、アドレナリン筋肉注射を直ちに投与し、バイタルサインの安定を回復した。』",
            "治療関係判定：病態を改善させた直接の治療介入（Intervention / Solution）を選択してください。",
            "治療関係判定：介入により回復した患者の病態危機（Critical Condition / Problem）を選択してください。",
            [("intervention_adrenaline_im_shot", "アドレナリン筋肉注射の迅速な投与"), ("condition_anaphylactic_hypotension", "蜂刺傷によるアナフィラキシー血圧低下および呼吸不全"), ("intervention_oral_antibiotics", "経口抗生物質の予防的投与")],
            "intervention_adrenaline_im_shot", "condition_anaphylactic_hypotension"
        ),
        (
            "旅客船出航前提条件",
            "【運航規程】『旅客フェリーが港を出航するためには、全乗客の名簿照合および救命設備の点検合格証受領が法的な前提条件となる。』",
            "出航要件判定：出航を許可するために法的に定められた前提条件（Prerequisite）を選択してください。",
            "出航要件判定：要件充足によって許可される運航行為（Permitted Goal）を選択してください。",
            [("prereq_passenger_manifest_safety_pass", "全乗客名簿の照合および救命設備点検合格証の受領"), ("goal_passenger_ferry_departure", "旅客フェリーの港からの出航"), ("prereq_dry_dock_hull_repaint", "ドック入渠による船体全面再塗装")],
            "prereq_passenger_manifest_safety_pass", "goal_passenger_ferry_departure"
        ),
        (
            "工場境界騒音改善",
            "【環境保全】『近隣住宅街における夜間騒音基準超過の苦情に対応するため、冷却塔に高性能消音サイレンサーを設置した結果、環境基準値以下の40dBを達成した。』",
            "環境改善判定：騒音低減をもたらした工法的解決手段（Solution）を選択してください。",
            "環境改善判定：改善施策によって解決された当初の環境課題・問題（Problem）を選択してください。",
            [("sol_acoustic_silencer_installation", "冷却塔への高性能消音サイレンサーの設置施工"), ("prob_nighttime_noise_complaints", "夜間騒音基準超過に伴う近隣住宅街からの苦情発生"), ("sol_relocate_cooling_towers", "冷却塔を別敷地へ完全移設")],
            "sol_acoustic_silencer_installation", "prob_nighttime_noise_complaints"
        ),
    ]

    for idx, (title, ctx, q_s1, q_s2, c_defs, t1, t2) in enumerate(span_relation_scenarios):
        for rep in range(5):
            gid = f"tb_gen_rel_{idx*5 + rep + 1:03d}"
            choices = make_choices(c_defs)
            records.append({
                "id": f"{gid}_s1",
                "group_id": gid,
                "family": "general_choice",
                "general_category": "semantic_relation",
                "context": f"【事例分析: SR-{idx*5+rep+1}】\n{ctx}",
                "question": q_s1,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2",
                "group_id": gid,
                "family": "general_choice",
                "general_category": "semantic_relation",
                "context": f"【事例分析: SR-{idx*5+rep+1}】\n{ctx}",
                "question": q_s2,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    # Category 5: policy_compliance (25 pairs)
    policy_scenarios = [
        (
            "個人情報・社内データ持ち出し",
            "『業務で急ぎ確認するため、顧客の氏名・電話番号・住所を含むCSVファイルを私用の個人USBメモリにコピーして自宅へ持ち帰った。』",
            "『顧客データを含む分析作業を行うため、社内の認証済みセキュアVDI環境にログインし、許可された暗号化ストレージ内で作業を完結させた。』",
            "情報セキュリティ規程判定：この従業員の行動のコンプライアンス評価を選択してください。",
            [("policy_violation_unauthorized_export", "規程違反（未認可媒体による機密データの不正持ち出し）"), ("policy_compliant_secure_vdi", "規程遵守（認可された暗号化セキュア環境での適正利用）"), ("policy_conditional_approval", "事前申請と特例承認に基づく条件付き許可")],
            "policy_violation_unauthorized_export", "policy_compliant_secure_vdi"
        ),
        (
            "インサイダー取引規制",
            "『自社の画期的な新薬承認の内部情報を公表前に知り、知人の名義を借りて自社株を大量に買い付けた。』",
            "『会社の定期持株会を通じて、毎月一定額の給与天引きにより長期的な資産形成として自社株を積立購入した。』",
            "金融商品取引法コンプライアンス：該当する評価を選択してください。",
            [("compliance_breach_insider_trading", "重大法令違反（未公表重要事実を利用した不法取引・インサイダー）"), ("compliance_ok_periodic_shareholding", "法令適合（計画的かつ定額の持株会積立による合法的な取得）"), ("compliance_requires_prior_clearance", "役員売買事前届出審査ラインへの確認対象")],
            "compliance_breach_insider_trading", "compliance_ok_periodic_shareholding"
        ),
        (
            "贈答品受領ガイドライン",
            "『官公庁の入札案件の審査を担当している職員が、参加業者から10万円相当の高級料亭での接待と金券を受け取った。』",
            "『取引先からのお中元として届いた1,000円程度の卓上カレンダーについて、社内規定に従い受付窓口に受領報告を行い部署内で共有した。』",
            "倫理・贈答品規程判定：該当する評価を選択してください。",
            [("ethics_violation_bribery_kickback", "倫理規程違反（利害関係者からの過剰接待・収賄リスク）"), ("ethics_compliant_customary_gift", "倫理規程適合（社会通念上相当な範囲の贈答品の適正届出）"), ("ethics_unsolicited_return_to_sender", "相手方への礼状を添えた返送・辞退手続き対象")],
            "ethics_violation_bribery_kickback", "ethics_compliant_customary_gift"
        ),
        (
            "ソーシャルメディア利用規程",
            "『開発中の未発表新モデルの写真をスマートフォンで撮影し、自分の個人X（旧Twitter）アカウントで「今作ってます」と投稿した。』",
            "『休日に訪れた美術館の感想を、会社の業務や所属には一切触れず、個人SNSに投稿した。』",
            "SNS利用ガイドライン判定：この投稿行為の評価を選択してください。",
            [("social_media_violation_leakage", "SNS規程違反（開発中機密情報の無断公開・漏洩）"), ("social_media_compliant_private_life", "SNS規程適合（私生活の範囲内であり業務情報に抵触しない投稿）"), ("social_media_official_press_inquiry", "広報部門の公式ニュースリリース担当へ回付")],
            "social_media_violation_leakage", "social_media_compliant_private_life"
        ),
        (
            "著作権・OSSライセンス遵守",
            "『GPLライセンスで公開されているオープンソースコードを改変してプロプライエタリな商用製品に組み込み、ソースコードを開示せずに独占配布した。』",
            "『MITライセンスのライブラリを利用し、製品付属のドキュメントおよび画面内に所定の著作権表示と許諾表示を明記して商用利用した。』",
            "知的財産ライセンス遵守判定：該当するライセンス状態を選択してください。",
            [("license_infringement_gpl_violation", "ライセンス違反（GPL要件不履行による著作権侵害リスク）"), ("license_compliant_mit_attribution", "ライセンス遵守（MITライセンス要件を満たした適法利用）"), ("license_dual_commercial_negotiation", "商用デュアルライセンス契約の締結交渉")],
            "license_infringement_gpl_violation", "license_compliant_mit_attribution"
        ),
    ]
    for idx, (title, c1, c2, q, c_defs, t1, t2) in enumerate(policy_scenarios):
        for rep in range(5):
            gid = f"tb_gen_pol_{idx*5 + rep + 1:03d}"
            choices = make_choices(c_defs)
            records.append({
                "id": f"{gid}_s1",
                "group_id": gid,
                "family": "general_choice",
                "general_category": "policy_compliance",
                "context": f"【コンプライアンス監査案件: CP-{idx*5+rep+1}】\n{c1}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2",
                "group_id": gid,
                "family": "general_choice",
                "general_category": "policy_compliance",
                "context": f"【コンプライアンス監査案件: CP-{idx*5+rep+1}】\n{c2}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    # Category 6: instruction_separation (25 pairs)
    instruction_scenarios = [
        (
            "背景雑音と本質的指示の分離",
            "【背景】本日の外気温は35度で猛暑日です。オフィス内には多くの観葉植物があります。\n【作業指示】サーバーラックの主電源スイッチをOFFにしてください。",
            "【背景】本日の外気温は35度で猛暑日です。オフィス内には多くの観葉植物があります。\n【作業指示】観葉植物にジョウロで水を補給してください。",
            "指示抽出判定：背景情報に惑わされず、実行すべき真の作業指示を選択してください。",
            [("task_shutdown_server_power", "サーバーラックの電源をOFFにする作業を実行"), ("task_water_office_plants", "オフィス内の観葉植物に水やりを行う作業を実行"), ("task_record_facility_temperature", "施設管理記録簿へ室温を記録する")],
            "task_shutdown_server_power", "task_water_office_plants"
        ),
        (
            "否定文脈と肯定的指示の区別",
            "【注意事項】プリンターのカバーは絶対に開けないでください。インクカートリッジにも触れないでください。\n【指示】用紙トレイ2にA4用紙を500枚補充してください。",
            "【注意事項】用紙トレイには触れないでください。紙の補充は不要です。\n【指示】操作パネルの印刷キャンセルボタンを1回押してください。",
            "指示遂行選択：禁止事項を避け、求められている肯定的なタスクを選択してください。",
            [("exec_refill_paper_tray2", "用紙トレイ2にA4用紙を補充する"), ("exec_press_cancel_print_button", "操作パネルの印刷キャンセルボタンを押す"), ("exec_print_diagnostic_test_page", "テスト印刷診断パターンを出力する")],
            "exec_refill_paper_tray2", "exec_press_cancel_print_button"
        ),
        (
            "対立する2人の発言からの指示元特定",
            "【前提】現場監督の指示が最優先であり、見学者やアルバイトの発言には従わないこと。\n【発言A（見学者）】『この荷物を外の道路へ運んでください。』\n【発言B（現場監督）】『この荷物を第2倉庫の保管棚へ運んでください。』",
            "【前提】現場監督の指示が最優先であり、見学者やアルバイトの発言には従わないこと。\n【発言A（見学者）】『この荷物を第2倉庫の保管棚へ運んでください。』\n【発言B（現場監督）】『この荷物を検品室の作業台へ運んでください。』",
            "権限指示判定：最優先ルールに基づき、従うべき指示を選択してください。",
            [("action_follow_warehouse2", "第2倉庫の保管棚へ荷物を運搬する"), ("action_follow_inspection_room", "検品室の作業台へ荷物を運搬する"), ("action_standby_for_dispatch", "配車指示が出るまで所定位置で待機する")],
            "action_follow_warehouse2", "action_follow_inspection_room"
        ),
        (
            "更新指示と旧指示の上書き分離",
            "【旧指示】会議室Aを予約してください。（※取り消し）\n【最新指示（10分前）】役員面談のため、会議室Cを最優先で予約してください。",
            "【旧指示】会議室Cを予約してください。（※取り消し）\n【最新指示（10分前）】海外拠点との遠隔会議のため、会議室Aを最優先で予約してください。",
            "指示有効性判定：取り消された旧指示を無視し、有効な最新指示を選択してください。",
            [("reserve_conference_room_c", "最新指示に従い会議室Cを予約する"), ("reserve_conference_room_a", "最新指示に従い会議室Aを予約する"), ("reserve_tentative_hold", "空き状況を確認し仮予約として保持する")],
            "reserve_conference_room_c", "reserve_conference_room_a"
        ),
        (
            "仮定条件と確定実行の区別",
            "【検討メモ】もし予算が倍増した場合は新型サーバーを導入する。しかし現行予算の範囲内では、既存サーバーのメモリ増設のみを実行する。",
            "【検討メモ】メモリ増設のみでは対応できないことが判明した。承認が下りたため、予算を追加配分して新型サーバーを導入する。",
            "確定指示判定：仮定や検討案ではなく、現時点で確定している実行作業を選択してください。",
            [("exec_memory_expansion_only", "既存サーバーのメモリ増設を実行する"), ("exec_deploy_new_server", "新型サーバーの新規導入・配備を実行する"), ("exec_postpone_all_investments", "すべての設備投資計画を無期限凍結する")],
            "exec_memory_expansion_only", "exec_deploy_new_server"
        ),
    ]
    for idx, (title, c1, c2, q, c_defs, t1, t2) in enumerate(instruction_scenarios):
        for rep in range(5):
            gid = f"tb_gen_ins_{idx*5 + rep + 1:03d}"
            choices = make_choices(c_defs)
            records.append({
                "id": f"{gid}_s1",
                "group_id": gid,
                "family": "general_choice",
                "general_category": "instruction_separation",
                "context": f"【業務指示管理システム】\n{c1}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2",
                "group_id": gid,
                "family": "general_choice",
                "general_category": "instruction_separation",
                "context": f"【業務指示管理システム】\n{c2}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    # Category 7: negative_goal (25 pairs)
    negative_scenarios = [
        (
            "アレルゲン安全・危険選定",
            "【アレルギー制限】卵・乳製品・小麦を含む食品は厳禁。\n【問診】患者が安全に食べられる、アレルゲンを含まない食品を選定してください。",
            "【アレルギー制限】卵・乳製品・小麦を含む食品は厳禁。\n【問診】アレルギー発作を引き起こす危険があるため、絶対に与えてはならない食品を選定してください。",
            "選定判定：指示された条件を満たす食品を選択してください。",
            [("food_safe_rice_snack", "純米と大豆の煎餅（アレルゲンを含まず安全）"), ("food_danger_wheat_custard", "小麦粉と卵と牛乳を使用したカスタードパイ（危険）"), ("food_unlabeled_processed_snack", "原材料表示の確認が必要な未分類スナック")],
            "food_safe_rice_snack", "food_danger_wheat_custard"
        ),
        (
            "軽減税率適用・除外判定",
            "【税制区分】生活必需品（一般食料品）は軽減税率（8%）対象。アルコール酒類および外食は軽減税率【対象外（通常10%）】。\n【判定品目】夕食調理用の生鮮野菜および精肉パック。",
            "【税制区分】生活必需品（一般食料品）は軽減税率（8%）対象。アルコール酒類および外食は軽減税率【対象外（通常10%）】。\n【判定品目】飲食店店内での飲食サービス（外食）および瓶ビール。",
            "税率判定：判定品目に適用される税区分を選択してください。",
            [("tax_reduced_groceries", "生鮮野菜・精肉（生活必需食品として軽減税率8%適用）"), ("tax_standard_alcohol_dining", "外食・酒類（軽減税率の対象外・通常10%適用）"), ("tax_exempt_stamp_transaction", "印紙・証紙等の非課税取引品目")],
            "tax_reduced_groceries", "tax_standard_alcohol_dining"
        ),
        (
            "ビザ免除・必須判定",
            "【渡航管理】ビザ免除国の短期観光はビザ申請【不要（免除）】。就労目的の渡航は就労ビザが【必須】。\n【渡航者A】ビザ免除国パスポートを所持し、3日間の観光旅行目的で滞在する。",
            "【渡航管理】ビザ免除国の短期観光はビザ申請【不要（免除）】。就労目的の渡航は就労ビザが【必須】。\n【渡航者B】現地法人に採用され、フルタイムのエンジニアとして現地勤務する。",
            "渡航資格判定：事前のビザ取得要否を選択してください。",
            [("visa_exempt_tourist", "短期観光の渡航者（事前のビザ取得は不要・免除）"), ("visa_mandatory_work_permit", "現地就労予定の渡航者（事前の就労ビザ取得が必須）"), ("visa_transit_airside_passenger", "空港制限区域内での当日乗り継ぎ客（トランジット）")],
            "visa_exempt_tourist", "visa_mandatory_work_permit"
        ),
        (
            "公園規則の許可・禁止行為判定",
            "【公園利用規則】焚き火・直火でのバーベキューは【禁止】。ベンチでの読書や水分補給は【許可（自由）】。\n【行動A】木陰のベンチに座って静かに文庫本を読んでいる。",
            "【公園利用規則】焚き火・直火でのバーベキューは【禁止】。ベンチでの読書や水分補給は【許可（自由）】。\n【行動B】芝生の上で薪を組んで直火で焚き火を始めた。",
            "規則判定：利用者の行動が規則上どのように扱われるか選択してください。",
            [("park_allowed_quiet_reading", "ベンチでの読書（利用規約で禁止されておらず自由）"), ("park_prohibited_open_fire", "芝生での直火焚き火（利用規約で明確に禁止された違反行為）"), ("park_requires_event_permit", "団体イベント開催に伴う事前占用許可申請行為")],
            "park_allowed_quiet_reading", "park_prohibited_open_fire"
        ),
        (
            "手数料免除・有料判定",
            "【銀行手数料】ゴールド会員は他行宛振込手数料が【無料（月3回まで）】。一般会員は1回あたり220円の【有料】。\n【利用者】ゴールド会員ステータスで当月1回目の他行振込。",
            "【銀行手数料】ゴールド会員は他行宛振込手数料が【無料（月3回まで）】。一般会員は1回あたり220円の【有料】。\n【利用者】一般会員ステータスで他行口座へ振込。",
            "手数料判定：この振込取引における手数料の取り扱いを選択してください。",
            [("fee_waived_gold_status", "ゴールド会員特典により振込手数料無料"), ("fee_charged_regular_member", "一般会員規定に基づき所定の振込手数料220円を請求"), ("fee_special_foreign_remittance", "外国為替取扱手数料を要する海外送金")],
            "fee_waived_gold_status", "fee_charged_regular_member"
        ),
    ]
    for idx, (title, c1, c2, q, c_defs, t1, t2) in enumerate(negative_scenarios):
        for rep in range(5):
            gid = f"tb_gen_neg_{idx*5 + rep + 1:03d}"
            choices = make_choices(c_defs)
            records.append({
                "id": f"{gid}_s1",
                "group_id": gid,
                "family": "general_choice",
                "general_category": "negative_goal",
                "context": f"【事例確認】\n{c1}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t1}
            })
            records.append({
                "id": f"{gid}_s2",
                "group_id": gid,
                "family": "general_choice",
                "general_category": "negative_goal",
                "context": f"【事例確認】\n{c2}",
                "question": q,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t2}
            })

    # Category 8: reverse_criterion (25 pairs)
    rev_flip_scenarios = [
        (
            "システムトリアージ逆判定",
            "【状況照会】\n事象A：本番決済DBが停止し顧客の取引が停止中（Severity 1）。\n事象B：社内ブログのアイコン画像が1箇所表示されない（Severity 4）。",
            "逆選定指示：【最も優先順位が低く、緊急対応が不要な案件】を選択してください。",
            "通常指示：【最優先で即時対応しなければならない致命的インシデント】を選択してください。",
            [("triage_lowest_blog_icon_cosmetic", "事象B：社内ブログのアイコン表示崩れ（低優先・後回し対応）"), ("triage_critical_payment_db_halt", "事象A：本番決済DB停止（最高優先度・即時復旧必須）"), ("triage_medium_daily_report_delay", "事象C：日次集計バッチの30分遅延（通常優先度P2）")],
            "triage_lowest_blog_icon_cosmetic", "triage_critical_payment_db_halt"
        ),
        (
            "コスト負担逆選定",
            "【プラン比較】\nオプション甲：月額50万円で24時間365日の専任オンサイト保守サポート。\nオプション乙：月額0円（完全無料）のコミュニティ掲示板によるセルフサポート。",
            "逆選定指示：【初期および月額の金銭的負担が最も少ない（最も低コストな）】選択肢を選択してください。",
            "通常指示：【最も手厚く高コストな専任フルサポート】選択肢を選択してください。",
            [("cost_lowest_free_community", "オプション乙：月額0円のコミュニティセルフサポート（最低コスト）"), ("cost_highest_dedicated_onsite", "オプション甲：月額50万円の専任オンサイト保守（最高コスト）"), ("cost_standard_shared_support", "オプション丙：営業時間内メールサポート（標準コスト・月額3万円）")],
            "cost_lowest_free_community", "cost_highest_dedicated_onsite"
        ),
        (
            "審査難易度逆判定",
            "【認証審査】\n申請A：本人確認書類（運転免許証）の自動OCR照合（不備なし・10秒で機械判定可能）。\n申請B：海外法人設立に伴う複雑な定款・公証役場認証書類の目視厳密審査（数週間の専門審査が必要）。",
            "逆選定指示：【審査の手間が最も少なく、最も簡単に即時完了できる申請】を選択してください。",
            "通常指示：【最も厳格で専門的な人手審査を要する複雑な申請】を選択してください。",
            [("review_easiest_auto_ocr", "申請A：運転免許証の自動OCR照合（最短・最低難易度）"), ("review_hardest_cross_border_legal", "申請B：海外法人定款の厳密審査（最長・最高難易度）"), ("review_standard_document_check", "申請C：国内一般法人の印鑑証明書確認（標準審査・1営業日）")],
            "review_easiest_auto_ocr", "review_hardest_cross_border_legal"
        ),
        (
            "環境負荷逆判定",
            "【輸送手段比較】\n輸送手段X：貨物列車による鉄道輸送（CO2排出量が極めて少ない環境配慮型）。\n輸送手段Y：専用ジェットチャーター機による緊急航空空輸（大量の燃料を消費しCO2排出量が極大）。",
            "逆選定指示：【環境負荷（CO2排出量）が最も低くエコな輸送手段】を選択してください。",
            "通常指示：【最も多くのCO2を排出し環境負荷が最大となる輸送手段】を選択してください。",
            [("eco_lowest_emissions_rail_freight", "輸送手段X：鉄道輸送（CO2排出量最小・最も環境負荷が低い）"), ("eco_highest_emissions_air_charter", "輸送手段Y：航空空輸（CO2排出量最大・最も環境負荷が高い）"), ("eco_standard_diesel_truck", "輸送手段Z：大型ディーゼルトラック輸送（標準的排出量）")],
            "eco_lowest_emissions_rail_freight", "eco_highest_emissions_air_charter"
        ),
        (
            "業務工数負担逆判定",
            "【業務比較】\n業務1：深夜のDBバックアップログのスクリプト自動保存（人手介入ゼロ・完全自動）。\n業務2：利害関係者が対立する跨国プロジェクトの対面調停会議（数十名の人手調整と多大な工数が必要）。",
            "逆選定指示：【人間の作業工数が最も少なく（ゼロ）、完全に自動処理される業務】を選択してください。",
            "通常指示：【最も多くの人間が関与し、極めて多大な工数と調整を要する業務】を選択してください。",
            [("workload_lowest_auto_backup", "業務1：DBバックアップ自動保存（人手介入ゼロ・完全自動）"), ("workload_highest_cross_border_mediation", "業務2：対立プロジェクトの対面調停（多大な人手工数が必要）"), ("workload_medium_weekly_status_check", "業務3：週次定例での進捗ステータス確認（標準工数・30分）")],
            "workload_lowest_auto_backup", "workload_highest_cross_border_mediation"
        ),
    ]
    for idx, (title, ctx, q_rev, q_norm, c_defs, t_rev, t_norm) in enumerate(rev_flip_scenarios):
        for rep in range(5):
            gid = f"tb_gen_rev_{idx*5 + rep + 1:03d}"
            choices = make_choices(c_defs)
            records.append({
                "id": f"{gid}_s1",
                "group_id": gid,
                "family": "general_choice",
                "general_category": "reverse_criterion",
                "context": f"【案件検討: RC-{idx*5+rep+1}】\n{ctx}",
                "question": q_rev,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t_rev}
            })
            records.append({
                "id": f"{gid}_s2",
                "group_id": gid,
                "family": "general_choice",
                "general_category": "reverse_criterion",
                "context": f"【案件検討: RC-{idx*5+rep+1}】\n{ctx}",
                "question": q_norm,
                "choices": choices,
                "target": {"kind": "hard", "choice_id": t_norm}
            })

    from scripts.rc2_1_train_data.generate_general_expansion import generate_general_expansion
    expansion_records = generate_general_expansion()
    records.extend(expansion_records)

    return records


if __name__ == "__main__":
    records = generate_general_stream_b()
    print(f"Generated {len(records)} general_choice records ({len(records)//2} pairs).")
    gids = set(r["group_id"] for r in records)
    print(f"Unique groups: {len(gids)}")
