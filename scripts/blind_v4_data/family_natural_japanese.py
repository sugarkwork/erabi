"""Family 4: natural_japanese (30 pairs, 60 cases) - Blind v4
Distribution: K=2 (10 pairs), K=3 (5 pairs), K=4 (10 pairs), K=6 (5 pairs)
Prefix: rc2b4_nat_
Zero inference during authoring; 100% fresh scenarios.
"""

from typing import Any, Dict, List, Tuple


def make_choices(c_defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in c_defs]


def get_natural_japanese_pairs() -> List[Dict[str, Any]]:
    pairs = []

    # --- K=2 (10 pairs: groups 01 to 10) ---
    k2_defs = [
        (
            "01",
            "新規システム移行プロジェクトに関する役員発言のニュアンス解析。",
            "発言内容：『準備の念を入れるに越したことはないが、費用対効果を鑑みれば、現段階での拙速な本格移行は見送るのが賢明な判断だ』。発言者の結論を判定せよ。",
            "発言内容：『準備の念を入れるに越したことはないので、競合に先んじるためにも、現段階から直ちに本格移行へ着手すべきだ』。発言者の結論を判定せよ。",
            [
                ("decision_postpone_migration", "システム移行の現時点見送り・延期"),
                ("decision_launch_migration", "システム移行の直ち着手・本格推進")
            ],
            "decision_postpone_migration", "decision_launch_migration"
        ),
        (
            "02",
            "業務提携の打診に対する老舗取引先の返答書面の意図解釈。",
            "返書文面：『貴社からのご提案につきましては大変光栄に存じ、ぜひ前向きに検討させていただきたいところではございますが、諸般の事情により今回は誠に遺憾ながらご意向に沿いかねます』。書面の主旨を解釈せよ。",
            "返書文面：『貴社からのご提案を謹んで拝受いたしました。両社の発展に資する好機と存じますので、ぜひ前向きに合意締結へ向けて進めさせていただきたく存じます』。書面の主旨を解釈せよ。",
            [
                ("business_decline_proposal", "丁重な謝絶・提案辞退"),
                ("business_accept_partnership", "受諾合意・提携前向き推進")
            ],
            "business_decline_proposal", "business_accept_partnership"
        ),
        (
            "03",
            "機密研究施設への入室許可申請に対する保安管理規程の適用判定。",
            "審査コメント：『申請者の提示した理由は業務上の利便性に留まり、やむを得ない緊急事態の要件を満たしているとは到底認めがたい』。入室許諾判定を行え。",
            "審査コメント：『現地機器故障によるデータ滅失の恐れがあり、まさにやむを得ない緊急事情であると認められる』。入室許諾判定を行え。",
            [
                ("access_denied_standard", "入室不許可・申請却下"),
                ("access_granted_special", "特別入室許可・ゲート解錠")
            ],
            "access_denied_standard", "access_granted_special"
        ),
        (
            "04",
            "工場廃液の環境基準適合性に関する技術報告書の評価判定。",
            "報告所見：『今回の水質数値の微増傾向は、測定機器の校正誤差による一時的なゆらぎにほかならない』。水質評価の結論を特定せよ。",
            "報告所見：『今回の水質数値の微増傾向について、単なる測定機器の校正誤差によるゆらぎとみなすことは到底できない』。水質評価の結論を特定せよ。",
            [
                ("eval_minor_noise_acceptable", "測定誤差の範囲・異常なしと判定"),
                ("eval_significant_anomaly", "有意な水質異常懸念・再調査判定")
            ],
            "eval_minor_noise_acceptable", "eval_significant_anomaly"
        ),
        (
            "05",
            "顧客クレームにおける契約違反該当性に関する法務見解。",
            "法務意見：『本件の納品遅延について、当社の帰責事由が全く存在しないとは言い切れない（二重否定肯定）』。帰責性の所在を結論付けよ。",
            "法務意見：『本件の納品遅延について、不可抗力災害によるものであり、当社の帰責事由には一切該当しない（全面否定）』。帰責性の所在を結論付けよ。",
            [
                ("liability_acknowledged", "当社側の責任・帰責事由あり"),
                ("liability_disclaimed", "当社側の免責・帰責事由なし")
            ],
            "liability_acknowledged", "liability_disclaimed"
        ),
        (
            "06",
            "不採算事業の継続可否に関する取締役会諮問答申。",
            "答申文書：『累損の拡大傾向に歯止めがかからず、早期の事業撤退を決断せずにはいられない状況である』。取締役会の採るべき方針を導け。",
            "答申文書：『新製品の引き合いが増加基調にあり、現局面での拙速な事業撤退は厳に差し控えるべきである』。取締役会の採るべき方針を導け。",
            [
                ("action_withdraw_business", "事業撤退・早期清算の断行"),
                ("action_continue_business", "撤退見合わせ・事業継続の維持")
            ],
            "action_withdraw_business", "action_continue_business"
        ),
        (
            "07",
            "サプライチェーン寸断に伴う生産計画の見直し指示。",
            "経営指示：『重要部品の調達網途絶により、当面の減産と工場の一時稼働停止を余儀なくされた』。生産ラインの対応を決定せよ。",
            "経営指示：『代替部材の確保が極めて順調に進捗し、当初の増産計画目標を余すところなく達成した』。生産ラインの対応を決定せよ。",
            [
                ("prod_curtail_and_idle", "減産措置および一時稼働停止"),
                ("prod_meet_expansion_target", "計画通りの増産稼働継続")
            ],
            "prod_curtail_and_idle", "prod_meet_expansion_target"
        ),
        (
            "08",
            "学術調査における新仮説の妥当性評価判定。",
            "査読所見：『提示された実験データを見る限り、提唱者の新説はあながち的外れな誤謬とは言い切れない』。仮説の評価を決定せよ。",
            "査読所見：『対照実験の不備が致命的であり、提示された新説は明白な誤謬であると断定せざるを得ない』。仮説の評価を決定せよ。",
            [
                ("hypothesis_plausible", "一理あり・検討に値する妥当な仮説"),
                ("hypothesis_refuted", "明白な誤謬・却下すべき無効な仮説")
            ],
            "hypothesis_plausible", "hypothesis_refuted"
        ),
        (
            "09",
            "歴史的建造物の老朽化改修方針に関する有識者審議。",
            "審議まとめ：『先人たちの貴重な意匠を解体撤去することは忍びなく、可能な限り原形保存修復を図るべきである』。施工方針を選択せよ。",
            "審議まとめ：『耐震強度の根本的不足を放置することは許されず、安全確保のため全面解体新築を毅然と遂行すべきである』。施工方針を選択せよ。",
            [
                ("preserve_original_structure", "解体回避・原形保存修復の推進"),
                ("demolish_and_rebuild", "安全優先・全面解体新築の断行")
            ],
            "preserve_original_structure", "demolish_and_rebuild"
        ),
        (
            "10",
            "情報漏洩インシデントに関する第三者調査委員会の報告。",
            "中間報告：『アクセスログの不自然な消去痕跡から見て、内部犯行による意図的持ち出しであると言わざるを得ない』。事案の性質を判断せよ。",
            "中間報告：『暗号化キーの漏洩はなく、外部への流出が生じたとの懸念には当たらないと判断される』。事案の性質を判断せよ。",
            [
                ("leak_intentional_confirmed", "悪質な意図的持ち出し事案"),
                ("leak_threat_cleared", "漏洩懸念の解消・非インシデント")
            ],
            "leak_intentional_confirmed", "leak_threat_cleared"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k2_defs:
        pairs.append({
            "id": f"rc2b4_nat_{gid}_s1", "group_id": f"rc2b4_nat_{gid}", "family": "natural_japanese",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_nat_{gid}_s2", "group_id": f"rc2b4_nat_{gid}", "family": "natural_japanese",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=3 (5 pairs: groups 11 to 15) ---
    k3_defs = [
        (
            "11",
            "納入先企業からの納期延長要望に対する返信メールの文面査定。",
            "返信文面：『不測の事態とのこと、拝察申し上げます。工程調整の上、ご要望の納期限まで快くお待ちいたします』。対応方針を分類せよ。",
            "返信文面：『度重なる遅延は甚だ遺憾であり、これ以上の猶予は致しかねますので、基本契約解除の通告とさせていただきます』。対応方針を分類せよ。",
            [
                ("reply_accept_postpone", "納期延長の無条件快諾"),
                ("reply_terminate_contract", "猶予拒否・即時契約解除通知"),
                ("reply_conditional_grace", "違約金前提の条件付き猶予")
            ],
            "reply_accept_postpone", "reply_terminate_contract"
        ),
        (
            "12",
            "新規設備投資の社内稟議書に対する決裁権限者の査定押印所見。",
            "査定所見：『事業計画の整合性・投資回収性ともに申し分なく、原案の通り直ちに承認可決とする』。稟議結果を決定せよ。",
            "査定所見：『前提条件の試算が非現実的であり、抜本的な事業モデルの破綻が認められるため、本件は不承認否決とする』。稟議結果を決定せよ。",
            [
                ("ringi_approved_original", "原案承認・決裁可決"),
                ("ringi_rejected_discarded", "不承認・稟議否決廃案"),
                ("ringi_amend_resubmit", "条件付き保留・修正再提出指示")
            ],
            "ringi_approved_original", "ringi_rejected_discarded"
        ),
        (
            "13",
            "製品初期不良クレームに対するカスタマーサポート特例措置の決定。",
            "窓口対応記録：『お客様に重大なご不快と実害をおかけしたため、特例として購入代金の全額を即日返金する』。処置を選択せよ。",
            "窓口対応記録：『初期不良の不具合箇所を確認したため、保証規定に基づき未開封の良品現物と即座に無償交換する』。処置を選択せよ。",
            [
                ("cs_full_refund_cash", "特例全額返金処理"),
                ("cs_replace_fresh_unit", "良品現物無償交換"),
                ("cs_disclaim_user_fault", "免責条項適用による有償修理案内")
            ],
            "cs_full_refund_cash", "cs_replace_fresh_unit"
        ),
        (
            "14",
            "エンジニア中途採用面接における面接官の総合評価判定。",
            "評価シート所見：『技術力・リーダーシップともに群を抜いており、当社が求める水準を完璧に満たすため、即時内定を強く推薦する』。判定を導け。",
            "評価シート所見：『実務経験の申告内容に客観的根拠を欠き、組織適応性にも極めて深刻な懸念があるため、不採用と判定する』。判定を導け。",
            [
                ("hire_instant_offer", "即時採用内定"),
                ("hire_reject_candidate", "不採用見送り"),
                ("hire_refer_final_board", "最終役員面接へ推薦継続")
            ],
            "hire_instant_offer", "hire_reject_candidate"
        ),
        (
            "15",
            "企業危機管理広報における重大不祥事のプレスリリース公表判断。",
            "広報委員会決定：『被害拡大の抑止と社会的責任を最優先とし、隠蔽の疑義を挟む余地のないよう本日付で直ちに全面公表する』。公表方針を決定せよ。",
            "広報委員会決定：『事実関係の裏付け調査が不十分な段階での拙速な公表は二次被害を招くため、監査委員会見解が出るまで公表を差し止める』。公表方針を決定せよ。",
            [
                ("press_release_immediate", "プレスリリース即時全面公表"),
                ("press_withhold_pending", "事実確認完了まで公表差し止め保留"),
                ("press_cancel_indefinitely", "公表計画の完全中止破棄")
            ],
            "press_release_immediate", "press_withhold_pending"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k3_defs:
        pairs.append({
            "id": f"rc2b4_nat_{gid}_s1", "group_id": f"rc2b4_nat_{gid}", "family": "natural_japanese",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_nat_{gid}_s2", "group_id": f"rc2b4_nat_{gid}", "family": "natural_japanese",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=4 (10 pairs: groups 16 to 25) ---
    k4_defs = [
        (
            "16",
            "研究開発助成金プログラムの審査委員会通知書面の査定結果。",
            "通知文面：『厳正なる外部審査の結果、貴提案の独創性と実用性が極めて高く評価され、本年度の助成対象として採択交付を決定いたしました』。判定を特定せよ。",
            "通知文面：『慎重に選考を重ねました結果、限られた採択枠の都合上、誠に遺憾ながら今回は不採択の運びとなりました』。判定を特定せよ。",
            [
                ("grant_award_adopted", "助成対象採択・交付決定"),
                ("grant_reject_declined", "不採択・選外却下通知"),
                ("grant_hold_clarify", "審査保留・追加積算補正指示"),
                ("grant_ineligible_dismiss", "応募要件不備による門前不受理")
            ],
            "grant_award_adopted", "grant_reject_declined"
        ),
        (
            "17",
            "オフィスビル賃貸借契約の期間満了に伴う更新合意の書面審査。",
            "合意調書：『貸主・借主双方が現行契約と同一条件での継続利用に合意したため、無修正のまま次期契約期間の更新手続きを締結する』。処理方針を特定せよ。",
            "合意調書：『貸主からの再三の明渡し勧告に対し借主が応諾したため、契約期間満了をもって速やかに原状回復明渡しを執行する』。処理方針を特定せよ。",
            [
                ("lease_renew_identical", "同条件無修正での契約更新締結"),
                ("lease_vacate_premises", "期間満了による原状回復明渡し執行"),
                ("lease_rent_revision_agree", "賃料増額改定承諾更新"),
                ("lease_mediation_dispute", "裁判所民事調停手続申立て")
            ],
            "lease_renew_identical", "lease_vacate_premises"
        ),
        (
            "18",
            "病院外来診療におけるインフォームドコンセント（説明と同意）の患者意思確認。",
            "カルテ記録：『外科的根治手術のリスクと予後について十分な説明を受け、納得した上で手術同意書に自筆署名がなされた』。患者方針を選択せよ。",
            "カルテ記録：『侵襲的手術は一切望まず、症状緩和のための低侵襲な薬物対症療法を強く希望された』。患者方針を選択せよ。",
            [
                ("patient_consent_surgery", "外科的手術の同意・実施"),
                ("patient_prefer_medication", "低侵襲薬物療法の選択"),
                ("patient_seek_second_opinion", "他院セカンドオピニオン照会"),
                ("patient_refuse_discharge", "全治療拒否による自己退院")
            ],
            "patient_consent_surgery", "patient_prefer_medication"
        ),
        (
            "19",
            "国際学術ジャーナル査読エディターからの判定通知レター。",
            "エディター通信：『両査読者ともに本論文の新規性と実証を絶賛しており、一切の修正を要することなく原稿受理（採録）と決定いたしました』。査読結果を判定せよ。",
            "エディター通信：『論理展開に重大な論理的跳躍と統計の誤謬が複数認められ、修正による回復は不可能であるため、掲載不採録（リジェクト）といたします』。査読結果を判定せよ。",
            [
                ("journal_accept_as_is", "無修正採録（Accept as is）"),
                ("journal_reject_fatal", "掲載不可却下（Reject）"),
                ("journal_minor_revisions", "軽微修正（Minor Revision）"),
                ("journal_major_revisions", "大幅改訂再査読（Major Revision）")
            ],
            "journal_accept_as_is", "journal_reject_fatal"
        ),
        (
            "20",
            "年次人事考課委員会における幹部候補生の昇格審議結果。",
            "審議記録：『卓越した事業推進力と周囲からの信望を有しており、全会一致で統括部長職への特別抜擢昇格を決定する』。考課結果を判定せよ。",
            "審議記録：『度重なるコンプライアンス逸脱事案に関与しており、現職責の遂行も困難と認められるため、降格および再教育を命じる』。考課結果を判定せよ。",
            [
                ("promo_executive_advance", "統括管理職への抜擢昇格"),
                ("promo_demote_reeducate", "役職降格およびコンプライアンス再教育"),
                ("promo_stay_same_grade", "現級据え置き・通常昇給のみ"),
                ("promo_transfer_branch", "地方拠点への同位横滑り異動")
            ],
            "promo_executive_advance", "promo_demote_reeducate"
        ),
        (
            "21",
            "クラウドサービス大規模障害における顧客向け広報ステータス判定。",
            "障害アナウンス：『基幹データベースの再同期が完了し、全系システムは通常運用状態へ完全復旧いたしました。長時間の停止を深くお詫び申し上げます』。報知レベルを選択せよ。",
            "障害アナウンス：『現在も障害原因の究明を進めており、復旧見込み時刻は未定となっております。進捗が判明次第、第3報をお知らせいたします』。報知レベルを選択せよ。",
            [
                ("status_fully_resolved", "障害全面復旧完了報"),
                ("status_investigating_progress", "原因究明中の中間経過報告"),
                ("status_temporary_workaround", "暫定回避策の案内周知"),
                ("status_unfounded_rumor", "誤報・影響皆無の訂正告知")
            ],
            "status_fully_resolved", "status_investigating_progress"
        ),
        (
            "22",
            "上場企業の有価証券報告書に対する監査法人の監査意見表明。",
            "監査報告書：『財務諸表は我が国において一般に公正妥当と認められる企業会計の基準に準拠し、財政状態および経営成績を適正に表示していると認める』。監査意見を判定せよ。",
            "監査報告書：『重要な不適正事項が広範に及んでおり、財務諸表が適正に表示されているとは認められない』。監査意見を判定せよ。",
            [
                ("audit_unqualified_clean", "無限定適正意見（クリーンオピニオン）"),
                ("audit_adverse_opinion", "不適正意見（アドバースオピニオン）"),
                ("audit_qualified_except", "除外事項付限定適正意見"),
                ("audit_disclaimer_refused", "監査意見不表明（意見表明拒絶）")
            ],
            "audit_unqualified_clean", "audit_adverse_opinion"
        ),
        (
            "23",
            "地方自治体総合計画基本方針に対するパブリックコメント（市民意見）の取扱い。",
            "行政回答：『市民皆様から寄せられた建設的なご提言を踏まえ、基本方針の条項に新たな施策目標を加筆修正して反映いたします』。対応方針を特定せよ。",
            "行政回答：『本施策の趣旨については現行案において既に織り込み済みであり、原案の文言通りの推進を維持させていただきます』。対応方針を特定せよ。",
            [
                ("public_amend_policy_plan", "意見を踏まえた基本計画の加筆修正反映"),
                ("public_maintain_original", "原案維持・施策趣旨の再説明"),
                ("public_archive_reference", "今後の参考記録としての内部保管"),
                ("public_out_of_scope_reject", "所管外意見としての審議対象除外")
            ],
            "public_amend_policy_plan", "public_maintain_original"
        ),
        (
            "24",
            "企業M&A買収監査（デューデリジェンス）結果報告に基づく投資委員会答申。",
            "答申所見：『財務・法務・事業の全分野において簿外債務等の隠れた瑕疵は皆無であり、当初予定価格での無条件買収推進を満場一致で答申する』。委員会の結論を特定せよ。",
            "答申所見：『巨額の未払い残業代および係争中の知財訴訟リスクが判明し、企業価値を致命的に損ねているため、買収計画の中止撤回を答申する』。委員会の結論を特定せよ。",
            [
                ("mna_proceed_unconditional", "当初条件通りの無条件買収推進"),
                ("mna_terminate_deal", "買収交渉の全面中止・撤回"),
                ("mna_reduce_purchase_price", "偶発債務織り込みによる買収価格減額要求"),
                ("mna_re_audit_forensic", "フォレンジック追加監査の実施")
            ],
            "mna_proceed_unconditional", "mna_terminate_deal"
        ),
        (
            "25",
            "精密機器メーカーの新世代フラグシップ製品の市場投入判断。",
            "経営会議決定：『量産歩留まりの目標達成とサプライチェーンの万全な体制を確認したため、予定通り全国一斉本格発売を開始する』。販売戦略を決定せよ。",
            "経営会議決定：『核心部品の耐久性試験において初期不良が多発したため、現設計での販売を断念し、製品開発計画を完全凍結する』。販売戦略を決定せよ。",
            [
                ("launch_nationwide_full", "全国一斉本格発売の開始"),
                ("launch_freeze_program", "販売断念・開発計画の完全凍結"),
                ("launch_regional_pilot", "特定主要都市での限定テスト先行販売"),
                ("launch_delay_redesign", "仕様再検討に伴う発売時期延期")
            ],
            "launch_nationwide_full", "launch_freeze_program"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k4_defs:
        pairs.append({
            "id": f"rc2b4_nat_{gid}_s1", "group_id": f"rc2b4_nat_{gid}", "family": "natural_japanese",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_nat_{gid}_s2", "group_id": f"rc2b4_nat_{gid}", "family": "natural_japanese",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    # --- K=6 (5 pairs: groups 26 to 30) ---
    k6_defs = [
        (
            "26",
            "学術図書の著作権二次利用許諾申請に対する著作者・権利者の回答文面の判定。",
            "権利者書面：『教育・学術の振興を目的とした利用であることに鑑み、ロイヤリティ無償にて営利・非営利を問わず商用転載を全面許諾いたします』。許諾方針を特定せよ。",
            "権利者書面：『無断転載および事後承諾要求は断固として容認できず、直ちに出版物の回収を行わなければ法的措置を講じる旨警告いたします』。許諾方針を特定せよ。",
            [
                ("copyright_grant_free_commercial", "無償商用二次利用の包括許諾"),
                ("copyright_warn_infringement", "許諾拒否・著作権侵害警告法的通知"),
                ("copyright_grant_credit_required", "クレジット明記を条件とする許諾"),
                ("copyright_demand_royalty_fee", "規定利用料支払い前提の条件付許諾"),
                ("copyright_grant_noncommercial_only", "非営利学術目的に限る限定許諾"),
                ("copyright_refer_to_agency", "著作権管理仲介団体への窓口移送")
            ],
            "copyright_grant_free_commercial", "copyright_warn_infringement"
        ),
        (
            "27",
            "都市幹線道路の橋梁架け替え工事に伴う交通規制広報の判定。",
            "道路管理者通達：『大型クレーンによる主桁架設作業の安全確保のため、終日にわたり全車両・歩行者を含め完全通行止め規制を実施いたします』。規制内容を特定せよ。",
            "道路管理者通達：『舗装復旧工事がすべて完了し、路面安全点検に合格したため、すべての車線規制を解除し通常通行を再開いたします』。規制内容を特定せよ。",
            [
                ("traffic_full_road_closure", "全車両歩行者完全通行止め規制"),
                ("traffic_restore_normal_flow", "規制全面解除・通常通行再開"),
                ("traffic_alternate_single_lane", "片側交互通行による交通誘導規制"),
                ("traffic_night_hours_only", "深夜時間帯限定車線規制"),
                ("traffic_pedestrian_only_pass", "車両通行止め歩行者通路のみ確保"),
                ("traffic_detour_bypass_route", "広域バイパス迂回ルート誘導")
            ],
            "traffic_full_road_closure", "traffic_restore_normal_flow"
        ),
        (
            "28",
            "企業内部通報ホットラインに寄せられた不正疑惑通報の受付審査判定。",
            "通報審査所見：『最高経営幹部による組織的な粉飾決算の関与を裏付ける具体的帳票が添付されており、監査役会直属の特別外部調査委員会を直ちに立ち上げる』。対応を特定せよ。",
            "通報審査所見：『個人的な感情的誹謗中傷に終始しており、不正を疑うべき客観的事実の記載が一切存在しないため、通報不受理として処理を終了する』。対応を特定せよ。",
            [
                ("whistle_external_special_probe", "監査役直属特別外部調査委員会設置"),
                ("whistle_dismiss_unfounded", "客観的根拠皆無による通報不受理終結"),
                ("whistle_internal_audit_referral", "内部監査室による通常事実確認調査"),
                ("whistle_hr_labor_interview", "人事労務担当による当事者ヒアリング"),
                ("whistle_legal_counsel_review", "顧問弁護士による法務意見照会"),
                ("whistle_police_criminal_report", "警察当局への即時刑事告発")
            ],
            "whistle_external_special_probe", "whistle_dismiss_unfounded"
        ),
        (
            "29",
            "家電リコール対象機器の発煙事故に伴うメーカー公式告知の判定。",
            "告知文面：『重大な火災事故に至る危険性があるため、対象製品のご使用を直ちに中止いただき、対策済みの新品良品と無償にて全数交換させていただきます』。対応種別を選択せよ。",
            "告知文面：『当該型番につきましては対策済み回路を標準搭載しており、今回のリコール自主回収の対象には一切該当いたしません』。対応種別を選択せよ。",
            [
                ("recall_replace_fresh_product", "使用即時中止・新品対策良品との無償交換"),
                ("recall_exempt_safe_model", "対象外型番・継続使用可の告知"),
                ("recall_repair_circuit_onsite", "出張訪問による部品無償交換修理"),
                ("recall_full_purchase_refund", "製品回収に伴う購入代金全額返金"),
                ("recall_warning_inspect_firmware", "ファームウェア更新と注意喚起告知"),
                ("recall_customer_scrap_proof", "廃棄証明書提出による金券進呈")
            ],
            "recall_replace_fresh_product", "recall_exempt_safe_model"
        ),
        (
            "30",
            "大雨洪水災害に伴う自治体防災無線による避難情報発令判定。",
            "緊急広報アナウンス：『河川水位が氾濫危険水位を突破し氾濫が発生しました。警戒レベル5、緊急安全確保を発令します。直ちに身の安全を確保してください』。発令レベルを選択せよ。",
            "緊急広報アナウンス：『降雨は収束し河川水位は平常水位まで減水、土砂災害の危険も去ったため、市内全域に出されていた避難指示をすべて解除します』。発令レベルを選択せよ。",
            [
                ("evac_level5_emergency_safety", "警戒レベル5緊急安全確保発令"),
                ("evac_all_orders_rescinded", "避難情報全面解除・安全確認"),
                ("evac_level4_evacuation_order", "警戒レベル4避難指示発令"),
                ("evac_level3_elderly_evacuate", "警戒レベル3高齢者等避難発令"),
                ("evac_shelter_open_advisory", "自主避難所開設および準備案内"),
                ("evac_weather_watch_standby", "気象台注意報継続に伴う経過観察")
            ],
            "evac_level5_emergency_safety", "evac_all_orders_rescinded"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k6_defs:
        pairs.append({
            "id": f"rc2b4_nat_{gid}_s1", "group_id": f"rc2b4_nat_{gid}", "family": "natural_japanese",
            "context": ctx, "question": q1, "choices": make_choices(cdefs), "target": {"choice_id": t1}
        })
        pairs.append({
            "id": f"rc2b4_nat_{gid}_s2", "group_id": f"rc2b4_nat_{gid}", "family": "natural_japanese",
            "context": ctx, "question": q2, "choices": make_choices(cdefs), "target": {"choice_id": t2}
        })

    return pairs
