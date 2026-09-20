"""Family 4: natural_japanese (30 pairs, 60 cases) - RC3 Bridge Benchmark
Prefix: rc3b_nat_
Distribution: K=3 (10 pairs), K=4 (15 pairs), K=6 (5 pairs)
Focus: Nuanced business/operational Japanese syntax, concessive conjunctions, indirect conditions, double negations.
Zero leakage against all past datasets.
"""

from typing import Any, Dict, List, Tuple


def make_choices(c_defs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"id": cid, "text": text} for cid, text in c_defs]


def get_natural_japanese_pairs() -> List[Dict[str, Any]]:
    pairs: List[Dict[str, Any]] = []

    # --- K=3 (10 pairs: groups 01 to 10) ---
    k3_defs = [
        (
            "01",
            "品質保証規定：製造ロットの出荷承認は、全数検査において不良率が0.01%以下であることを要する。ただし、抜取再試験において合格判定基準を完全に満たし、かつ品質統括部長の特認印がある場合に限り、例外的に出荷を差し支えないものとする。",
            "ロットAの全数検査不良率は0.03%であったものの、抜取再試験に全数合格し、品質統括部長の特認印が正式に捺印された。出荷判定を行え。",
            "ロットBの全数検査不良率は0.02%であり、抜取再試験にも合格したものの、品質統括部長の特認印は未受領である。出荷判定を行え。",
            [("shipping_special_release", "特認条項適用による例外出荷承認"), ("shipping_quarantine_hold", "特認要件未充足による出荷保留隔離"), ("shipping_batch_scrap", "全数検査不適合によるロット全廃棄")],
            "shipping_special_release", "shipping_quarantine_hold"
        ),
        (
            "02",
            "情報セキュリティ規程：社外持ち出しPCへの機密データ保存は原則として禁止する。ただし、オフライン専用端末であり、かつBitLocker暗号化が施されている場合であって、所属長の事前承認が得られているときはこの限りではない。",
            "端末管理記録：持ち出しPCはオフライン専用であり、暗号化も完了しているが、所属長の事前承認申請が未決裁のままである。データ保存の可否を決定せよ。",
            "端末管理記録：持ち出しPCはオフライン専用かつBitLocker暗号化済みであり、所属長による事前承認がシステム上で確定している。データ保存の可否を決定せよ。",
            [("pc_save_inhibit", "承認未了につき機密データ保存禁止"), ("pc_save_exception_grant", "例外要件充足につき機密データ保存承認"), ("pc_device_revoke", "セキュリティ違反端末強制初期化")],
            "pc_save_inhibit", "pc_save_exception_grant"
        ),
        (
            "03",
            "契約審査指針：相手方から提示された秘密保持契約（NDA）について、裁判管轄が東京地方裁判所以外である場合は原則として法務修正を求めるものとする。ただし、管轄が大阪地方裁判所または名古屋地方裁判所である場合に限り、事業部門長の合意があればそのまま締結しても妨げない。",
            "契約書案：相手方の提示した合意管轄は大阪地方裁判所と記載されており、事業部門長からの締結合意文書が提出された。法務審査判断を下せ。",
            "契約書案：相手方の提示した合意管轄は福岡地方裁判所と記載されており、事業部門長からの締結合意文書が提出された。法務審査判断を下せ。",
            [("nda_accept_as_is", "例外要件該当・現行管轄条項のまま締結承認"), ("nda_request_jurisdiction_amend", "特例除外管轄・東京地裁への修正要求指示"), ("nda_reject_contract", "契約交渉打ち切り拒絶")],
            "nda_accept_as_is", "nda_request_jurisdiction_amend"
        ),
        (
            "04",
            "プラント安全管理規程：反応器の定期開放点検中は、内部ガス濃度が許容基準値未満であっても、酸素濃度が21.0%以上であることを確認できない限り、いかなる者も防毒マスクなしで立ち入ることはできない。",
            "点検前測定：毒性ガス濃度は検出限界未満であるが、酸素濃度計の指示値は19.8%にとどまっている。作業員の入槽措置を決定せよ。",
            "点検前測定：毒性ガス濃度は不検出であり、酸素濃度計の指示値は21.2%を示している。作業員の入槽措置を決定せよ。",
            [("confined_space_mask_required", "酸素濃度不足・防毒マスクなし立入禁止"), ("confined_space_normal_entry", "酸素濃度適合・通常装備立入許可"), ("confined_space_seal_purge", "換気不全・マンホール再封鎖窒素置換")],
            "confined_space_mask_required", "confined_space_normal_entry"
        ),
        (
            "05",
            "特許出願社内審査規程：新規考案については、先行技術文献調査で新規性喪失の恐れがないと判断されたもののみを出願対象とする。ただし、先行技術文献と類似する部分があるとしても、従来技術にない顕著な効果の定量的データが示されている場合は、例外として出願を推進する。",
            "審査対象案件X：先行文献と構成の一部に類似が認められるものの、従来比でエネルギー消費を40%削減した実測検証データが添付されている。知財出願判定を下せ。",
            "審査対象案件Y：先行文献と構成が類似しており、効果についても定性的な期待のみで定量的比較データが欠落している。知財出願判定を下せ。",
            [("patent_filing_proceed", "顕著な効果の定量的立証あり・出願推進決定"), ("patent_filing_reject", "新規性疑義・定量的根拠不足による出願見送り"), ("patent_trade_secret", "ノウハウ秘匿化指定保留")],
            "patent_filing_proceed", "patent_filing_reject"
        ),
        (
            "06",
            "設備保全指針：潤滑油交換周期は運転時間2000時間毎とする。ただし、定期油分析において全酸価の上昇が0.1mgKOH/g未満であり、かつ動粘度変化率が±5%以内に収まっていることが確認されている場合に限り、次回点検まで交換を猶予することができる。",
            "保全ログ：運転時間は2150時間に達しているが、油分析結果は全酸価上昇0.04mgKOH/g、粘度変化率+2.1%であった。潤滑油処置を決定せよ。",
            "保全ログ：運転時間は2050時間に達し、油分析結果は全酸価上昇0.28mgKOH/g、粘度変化率+8.5%であった。潤滑油処置を決定せよ。",
            [("oil_defer_replacement", "性状良好・次回点検まで潤滑油交換猶予"), ("oil_execute_replacement", "性状劣化・規定時間超過による潤滑油交換実行"), ("oil_flush_standby", "フラッシング洗浄剤循環待機")],
            "oil_defer_replacement", "oil_execute_replacement"
        ),
        (
            "07",
            "人事労務規程：特別深夜業務手当は、深夜勤務時間が累計3時間を超える場合に支給する。ただし、当直待機業務である場合については、実労働を伴う緊急呼出対応に従事した時間を除き、手当の算定対象としないものとする。",
            "勤務実績表：深夜時間帯に5時間在館していたが、これは当直待機であり、緊急呼出への実労働対応は45分間のみであった。手当支給判定を行え。",
            "勤務実績表：深夜時間帯に当直待機として勤務中、深夜の緊急トラブル呼出に対応して3時間30分の実稼働に従事した。手当支給判定を行え。",
            [("allowance_not_eligible", "実労働時間要件未達・特別深夜手当不支給"), ("allowance_eligible_grant", "実労働3時間超過・特別深夜手当支給承認"), ("allowance_comp_time", "代休振替付与手続移行")],
            "allowance_not_eligible", "allowance_eligible_grant"
        ),
        (
            "08",
            "医薬品治験実施要領：被験者への治験薬投与は、直近の血液検査において肝機能指標（AST/ALT）が基準値の2倍以内であることを確認した上で行わなければならない。いかなる理由があっても、この確認を経ずして投与を開始することは認められない。",
            "投与前カルテ：本日の採血結果は検査センター混雑のため未着であるが、主治医は前週の数値が極めて安定していたことを根拠に即時投与を求めている。治験薬調剤管理者の対応を決定せよ。",
            "投与前カルテ：直前の至急採血結果が報告され、AST/ALTともに基準値上限の1.3倍に収まっていることが確認された。治験薬調剤管理者の対応を決定せよ。",
            [("trial_drug_admin_hold", "必須直近採血未確認・治験薬投与保留中止"), ("trial_drug_admin_proceed", "基準値内確認完了・治験薬投与開始承認"), ("trial_subject_discontinue", "被験者適格性喪失による治験中止")],
            "trial_drug_admin_hold", "trial_drug_admin_proceed"
        ),
        (
            "09",
            "金融取引コンプライアンス規程：大口海外送金について、送金依頼人がPEP（重要な公的地位を有する者）に該当する場合であっても、送金原資が確認済みの遺産相続であり、かつ役員決裁を経ているときは、送金手続を執行して差し支えない。",
            "送金審査票：依頼人は外国PEPに該当するが、公証役場発行の遺産分割協議書により相続原資が証明され、コンプライアンス担当役員の決裁が完了している。送金処置を決定せよ。",
            "送金審査票：依頼人は外国PEPに該当し、送金原資は不動産売却益と申告されているが、売買契約書の原本確認および役員決裁が未了である。送金処置を決定せよ。",
            [("remittance_execute_approved", "要件充足・大口海外送金執行承認"), ("remittance_block_pending", "原資・決裁未了・送金手続き保留停止"), ("remittance_str_report", "疑わしい取引として当局届出")],
            "remittance_execute_approved", "remittance_block_pending"
        ),
        (
            "10",
            "建築構造設計指針：積雪荷重の算定において、屋根勾配が60度を超える場合は積雪荷重をゼロとして取り扱ってよい。ただし、雪止金具が設置されている屋根面については、勾配の如何にかかわらず通常の積雪荷重を見込まなければならない。",
            "設計図書：屋根勾配は65度の急勾配であるが、軒先からの落雪事故を防止するため全面に雪止アングル金物が配置されている。積雪荷重の算定方針を決定せよ。",
            "設計図書：屋根勾配は65度の急勾配であり、雪止金具等の突起物は一切設けられていない滑雪仕様である。積雪荷重の算定方針を決定せよ。",
            [("snow_load_standard_apply", "雪止金具設置あり・通常積雪荷重を算定計上"), ("snow_load_zero_exempt", "勾配60度超滑雪屋根・積雪荷重ゼロ免除適用"), ("snow_load_half_reduce", "勾配低減係数による積雪荷重半減算定")],
            "snow_load_standard_apply", "snow_load_zero_exempt"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k3_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_nat_{gid}_s1",
                "group_id": f"rc3b_nat_{gid}",
                "family": "natural_japanese",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_nat_{gid}_s2",
                "group_id": f"rc3b_nat_{gid}",
                "family": "natural_japanese",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2}
            }
        ])

    # --- K=4 (15 pairs: groups 11 to 25) ---
    k4_defs = [
        (
            "11",
            "貿易外為管理内規：輸出令別表第一の該非判定において、仕様が統制パラメータ未満である貨物であっても、仕向地が懸念国であり、かつ需要者が大量破壊兵器開発関与懸念リストに掲載されているときは、キャッチオール規制に基づき経済産業大臣の個別輸出許可を取得しなければならない。",
            "輸出審査票：貨物自体のスペックは規制値未満であるが、仕向地が懸念地域であり、需要者がエンドユーザーリスト掲載企業である。通関措置を指示せよ。",
            "輸出審査票：貨物スペックは規制値未満であり、仕向地は一般協調国であって、需要者の懸念情報も一切存在しない。通関措置を指示せよ。",
            [("export_metis_license_req", "個別輸出許可申請必須・通関手続保留"), ("export_general_blanket_pass", "キャッチオール非該当・一般包括出荷承認"), ("export_customs_seizure", "無許可輸出未遂による貨物没収"), ("export_reclassification_audit", "仕様該非再判定技術審査")],
            "export_metis_license_req", "export_general_blanket_pass"
        ),
        (
            "12",
            "臨床試験倫理指針：被験者への重大な予期せぬ副作用（SUSAR）が発現した場合、治験依頼者は発生を知った日から7日以内に規制当局へ緊急報告を行わなければならない。ただし、死亡または生命の危機に直結しない事象については、報告期限を15日以内とすることができる。",
            "安全性速報：治験薬投与群において重篤な肝機能障害が発生したが、入院加療により回復傾向にあり、生命の直接の危機には至っていない。報告期限区分を決定せよ。",
            "安全性速報：治験薬投与群において心停止による突然死事象が発生し、治験薬との因果関係が否定できないとされた。報告期限区分を決定せよ。",
            [("susar_15day_standard_report", "非致死的重篤事象・15日以内標準報告"), ("susar_7day_urgent_report", "死亡危篤直結事象・7日以内緊急報告"), ("susar_annual_periodic_summary", "年次定期安全性報告への一括掲載"), ("susar_internal_review_only", "学術委員会内部記録のみ")],
            "susar_15day_standard_report", "susar_7day_urgent_report"
        ),
        (
            "13",
            "クラウドシステム障害対応手順：サービス提供不能を伴う障害発生時、復旧見込みが30分を超えると判断された場合は、原因究明の完了を待つことなく、直ちに待機系リージョンへのフェイルオーバーを実施しなければならない。ただし、データ整合性の損失が不可避であると判明した場合は、統括責任者の承認を得るまで切り替えを見合わせるものとする。",
            "障害モニタ：主系DBストレージ破損により復旧見込みは2時間以上と推定されたが、待機系レプリケーションの整合性チェックは正常完了している。対応を指示せよ。",
            "障害モニタ：復旧見込みは1時間を超えるが、待機系への切り替えにより直近10分間のコミット済み取引データが消失する不整合が判明した。統括承認は未着である。対応を指示せよ。",
            [("failover_switch_immediate", "30分超復旧遅延・待機系即時フェイルオーバー実行"), ("failover_hold_integrity_risk", "データ損失リスク・統括承認まで切替見合わせ保留"), ("failover_primary_repair_wait", "主系サーバー現地原因究明復旧待機"), ("failover_client_maintenance_page", "顧客向けメンテナンス画面全停止切替")],
            "failover_switch_immediate", "failover_hold_integrity_risk"
        ),
        (
            "14",
            "労働安全衛生指針：夏季の屋外高所作業において、熱中症指数（WBGT）が28℃以上のときは原則として1時間ごとに15分以上の休息を取らせるものとする。ただし、WBGTが31℃以上となったときは、いかなる作業であっても直ちに作業を全面中断し、涼しい休憩所へ退避させなければならない。",
            "現場環境計：計測WBGTは29.5℃であり、直射日光下での鉄骨組立作業が連続45分経過した。作業指示を下せ。",
            "現場環境計：午後1時の計測にてWBGTが31.8℃を記録した。現場責任者の作業指示を下せ。",
            [("heat_mandatory_rest_break", "WBGT28超・15分間給水休息指示"), ("heat_abort_work_evacuate", "WBGT31超・作業全面即時中断退避"), ("heat_routine_continue", "通常ペース作業継続承認"), ("heat_misting_fan_setup", "ミストファン増設通常作業")],
            "heat_mandatory_rest_break", "heat_abort_work_evacuate"
        ),
        (
            "15",
            "原子力施設運転保安規定：主蒸気隔離弁の定期作動テストにおいて、全閉弁時間が規定値を超過した場合は、直ちに当該弁を全閉隔離位置でロックし、24時間以内に健全性を回復できなければ原子炉を冷温停止状態へ移行させなければならない。",
            "点検報告：第2主蒸気隔離弁の作動時間が5.8秒（規定値5.0秒以内）を記録し、初期調整での復旧に失敗した。直ちに採るべき初期保安措置を決定せよ。",
            "点検報告：第2主蒸気隔離弁の全閉弁時間は4.2秒であり、規定値内であることが確認された。初期保安措置を決定せよ。",
            [("msiv_lock_closed_isolate", "規定値超過・隔離弁全閉位置機械ロック"), ("msiv_nominal_pass_continue", "試験合格・主蒸気隔離弁通常開度復帰"), ("msiv_reactor_cold_shutdown", "原子炉即時冷温停止スクラム"), ("msiv_actuator_oil_flush", "油圧アクチュエータ作動油入替")],
            "msiv_lock_closed_isolate", "msiv_nominal_pass_continue"
        ),
        (
            "16",
            "食品製造GMP基準：異物混入防止管理において、製品通過ラインの金属検出器が警報を発した場合、当該製品のみならず、前回テストピース確認以降に通過した全ロットを隔離しなければならない。ただし、後段のX線検査装置によって全数再スキャンを行い異物が検出されなかった製品については、品質責任者の承認を経て隔離を解除できる。",
            "ライン事象：金属検出器が鳴動しラインが停止した。直前15分間に通過した製品について、X線再検査は未実施である。処置を決定せよ。",
            "ライン事象：金属検出器鳴動後に隔離されたロットについて、全品の高精度X線再スキャンを実施し異物皆無が証明され、品質責任者の解除承認が下りた。処置を決定せよ。",
            [("gmp_quarantine_entire_lot", "前回確認以降の通過ロット全品隔離"), ("gmp_release_quarantine_approved", "X線全数確認完了・隔離解除ライン復帰"), ("gmp_incinerate_all_products", "混入懸念品全ロット即時焼却破棄"), ("gmp_recalibrate_metal_detector", "金属検出器感度下げ再調整")],
            "gmp_quarantine_entire_lot", "gmp_release_quarantine_approved"
        ),
        (
            "17",
            "金融商品取引法適合性原則：75歳以上の高齢顧客に対しデリバティブ内包の仕組債を勧誘・販売することは原則として禁じられている。ただし、十分な金融資産を有し、かつ二等親以内の成年家族が同席してリスク説明に書面同意した場合は、支店長の特別面談決裁を経て販売することができる。",
            "適合性審査：顧客は78歳で金融資産2億円を保有するが、商談には単独で来店しており、家族の同席同意書は提出されていない。販売の可否を決定せよ。",
            "適合性審査：顧客は76歳で十分な資産を有し、長男が同席して元本毀損リスクに書面同意し、支店長による特別面談が完了した。販売の可否を決定せよ。",
            [("suitability_sales_prohibited", "家族同席要件未充足・仕組債販売禁止"), ("suitability_sales_granted", "特別要件完全充足・仕組債販売契約承認"), ("suitability_unhedged_waiver", "顧客自己責任誓約書による単独販売"), ("suitability_substitute_stock", "高配当個別株式への代替推奨")],
            "suitability_sales_prohibited", "suitability_sales_granted"
        ),
        (
            "18",
            "建築基準法第35条内装制限：特定防火対象物の居室の内装仕上げは準不燃材料以上としなければならない。ただし、床面から高さ1.2m以下の腰壁部分については、スプリンクラー設備が有効に設置されている居室にあっては木材等の可燃性材料であっても制限の適用を受けない。",
            "設計照査：スプリンクラー完備の高齢者福祉施設食堂において、床から高さ1.0mの腰壁に天然ヒノキ板仕上げを採用する計画である。内装制限適合性を判定せよ。",
            "設計照査：スプリンクラー未設置の集会場居室において、床から高さ1.0mの腰壁に天然ヒノキ板仕上げを採用する計画である。内装制限適合性を判定せよ。",
            [("interior_finish_exempt_approved", "SP設置・腰壁1.2m以下緩和適用適合"), ("interior_finish_code_violation", "SP未設置・可燃腰壁は内装制限法規違反"), ("interior_finish_fireproof_coat", "防火塗料塗布による準不燃化条件付承認"), ("interior_finish_plaster_replace", "石膏ボード直貼り変更指示")],
            "interior_finish_exempt_approved", "interior_finish_code_violation"
        ),
        (
            "19",
            "知的財産ライセンス契約：本特許技術のサブライセンスは書面による事前許諾のない限り一切禁止される。ただし、ライセンシーの完全子会社（議決権100%保有）への移転については、グループ内事業再編計画の書面通知がなされている限り、事前許諾を要さず自動的に承諾されたものとみなす。",
            "契約審査：ライセンシーは保有比率70%の関連会社への技術供与を計画し、事後通知のみで実施しようとしている。ライセンス効力を判定せよ。",
            "契約審査：ライセンシーは100%保有の完全子会社へ技術移転するにあたり、所定の事業再編計画書を事前に書面通知した。ライセンス効力を判定せよ。",
            [("license_unauthorized_infringement", "完全子会社要件未達・無許諾サブライセンス違反"), ("license_automatic_consent_valid", "100%子会社通知完了・みなし承諾有効"), ("license_arbitration_notice", "ライセンス料増額請求仲裁通知"), ("license_patent_invalidation", "特許無効審判請求")],
            "license_unauthorized_infringement", "license_automatic_consent_valid"
        ),
        (
            "20",
            "医薬品治験における盲検解除規程：二重盲検試験のコード開示は、被験者の生命を救うための医学的緊急処置に必要な場合を除き、試験の全症例データ固定が完了するまで厳密に封印されなければならない。治験責任医師が単なる治療方針の変更を目的として開示を要請することは認められない。",
            "治験管理モニタ：被験者がアナフィラキシー性ショックで心肺停止の危機に瀕し、救急担当医が即時の救命処置薬選択のためコード開示を強く求めた。コード開示可否を決定せよ。",
            "治験管理モニタ：被験者の病勢進行が認められたため、治験責任医師が次回治療レジメン検討の参考にする目的でコード開示を申請した。コード開示可否を決定せよ。",
            [("unblinding_emergency_rescue", "救命緊急事態・盲検コード即時開示承認"), ("unblinding_request_denied", "緊急性要件不充足・盲検コード開示却下"), ("unblinding_patient_withdraw", "被験者同意撤回による治験中止"), ("unblinding_safety_board_hold", "独立データモニタリング委員会招集待機")],
            "unblinding_emergency_rescue", "unblinding_request_denied"
        ),
        (
            "21",
            "個人情報保護法対応マニュアル：本人の同意を得ない個人データの第三者提供は原則として禁止される。ただし、法令に基づく場合、または人の生命・身体の保護のために緊急の必要があって本人の同意を得ることが困難であるときは、本人の事前の同意なく提供することができる。",
            "照会事案：意識不明の重体で救急搬送された身元不明患者について、警察署から親族への連絡のため医療機関が保有する連絡先情報の開示要請があった。情報提供の可否を決定せよ。",
            "照会事案：民間マーケティング調査会社から、製品アンケート分析の精度向上のため顧客氏名・住所リストの提供依頼が寄せられた。情報提供の可否を決定せよ。",
            [("privacy_emergency_disclosure_grant", "人命救護緊急性該当・第三者提供承認"), ("privacy_third_party_prohibited", "本人同意なし・個人情報第三者提供拒絶"), ("privacy_anonymized_provision", "仮名加工情報への加工後提供"), ("privacy_internal_legal_escalate", "法務部コンプライアンス委員会付議")],
            "privacy_emergency_disclosure_grant", "privacy_third_party_prohibited"
        ),
        (
            "22",
            "航空運送約款手荷物取扱規程：リチウムイオンバッテリー単体の受託手荷物（貨物室預け入れ）は一切認められない。機内持ち込み手荷物として携行する場合に限り、定格容量が100Wh以下であれば個数制限なく、100Wh超160Wh以下のものは航空会社の事前承認を得て2個まで持ち込むことができる。",
            "保安検査場：乗客が150Whのモバイルバッテリー1個を手荷物として機内に持ち込むことを申告し、航空会社カウンターでの事前承認証を提示した。持込可否を判定せよ。",
            "保安検査場：乗客が150Whのモバイルバッテリー2個をスーツケースに入れ、受託手荷物として預け入れようとした。持込可否を判定せよ。",
            [("battery_carry_on_approved", "容量・承認要件適合・機内持込承認"), ("battery_checked_bag_rejected", "受託手荷物預け入れ不可・受託拒絶"), ("battery_seize_destroy", "危険物無断所持による没収廃棄"), ("battery_pilot_waiver_req", "機長直接特任承認証取得要求")],
            "battery_carry_on_approved", "battery_checked_bag_rejected"
        ),
        (
            "23",
            "産業廃棄物適正処理マニュアル：特別管理産業廃棄物（廃強酸等）の委託処理は、当該許可を有する処理業者と直接書面契約を結ばなければならない。いかなる場合も仲介業者による又貸しや再委託を認めてはならず、マニフェスト原本の7年間保存を怠った場合は即時に排出事業停止勧告の対象となる。",
            "監査結果：廃硫酸の処分委託契約において、収集運搬許可業者と直接契約を結び、7年分の電子マニフェスト照合票が完全保管されていた。監査評価を下せ。",
            "監査結果：排出事業場はコンサルタント会社を仲介人として再委託処分を行い、現場に直接の委託契約書面が存在しなかった。監査評価を下せ。",
            [("waste_compliance_pass", "直契約・保管完備・法令適合承認"), ("waste_illegal_subcontract_alert", "無許可再委託違反・行政勧告改善命令"), ("waste_manifest_grace_period", "マニフェスト再提出猶予措置"), ("waste_temporary_storage_order", "事業場内ドラム缶一時保管指示")],
            "waste_compliance_pass", "waste_illegal_subcontract_alert"
        ),
        (
            "24",
            "港湾施設保安（ISPSコード）運用要領：保安レベル2（警戒強化）発令時においては、港湾保安区域への車両進入は事前に登録された港湾関係車両を除き全面的に禁止される。ただし、緊急指定車両（救急車・消防車・警察車両）については、身元確認手続きを簡略化して直ちに進入を許可するものとする。",
            "正門ゲート：保安レベル2発令中、臨海消防署の化学消防ポンプ車がコンテナヤード火災通報を受けて緊急走行で進入を要求した。警備対応を指示せよ。",
            "正門ゲート：保安レベル2発令中、未登録の民間宅配トラックが船用品配達のため進入を要求した。警備対応を指示せよ。",
            [("isps_emergency_vehicle_entry", "緊急指定車両・即時進入ゲート開放"), ("isps_unregistered_vehicle_deny", "レベル2規制・未登録車両進入拒絶"), ("isps_under_chassis_search", "車両底部ミラー検査後条件付通過"), ("isps_driver_id_fingerprint", "運転手指紋照合手続待機")],
            "isps_emergency_vehicle_entry", "isps_unregistered_vehicle_deny"
        ),
        (
            "25",
            "特定商取引法通信販売広告規定：インターネット通販サイトにおいては、商品の返品特約について広告上の明確な表示がない限り、商品受取後8日以内であれば消費者は送料自己負担にて契約の解除（返品）を行うことができる。事業者が一方的に「返品不可」と注文確認メールのみに後出し記載したとしても、広告表示の不備を免れることはできない。",
            "消費者相談：購入サイトの広告ページに返品に関する記載が一切なく、商品到着から4日目の購入者が自己負担送料での返品を申し出た。法約上の返品請求権を判定せよ。",
            "消費者相談：購入サイトの広告画面において、フォントサイズ・配色ともに目立つ態様で『返品不可（開封前後を問わず）』と明瞭に事前表示されていた。購入者が返品を申し出た。法約上の返品請求権を判定せよ。",
            [("ecommerce_return_right_valid", "広告表示欠落・法定返品権有効（返品可能）"), ("ecommerce_return_right_invalid", "事前明瞭特約有効・契約解除不可（返品拒否正当）"), ("ecommerce_cooling_off_cancel", "無条件全額返金クーリングオフ適用"), ("ecommerce_seller_reimburse_shipping", "事業者全額送料負担返品命令")],
            "ecommerce_return_right_valid", "ecommerce_return_right_invalid"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k4_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_nat_{gid}_s1",
                "group_id": f"rc3b_nat_{gid}",
                "family": "natural_japanese",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_nat_{gid}_s2",
                "group_id": f"rc3b_nat_{gid}",
                "family": "natural_japanese",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2}
            }
        ])

    # --- K=6 (5 pairs: groups 26 to 30) ---
    k6_defs = [
        (
            "26",
            "金融商品取引法大量保有報告書提出内規：上場会社の発行済株式総数の5%超を取得した保有者は、取得日から5営業日以内に大量保有報告書を提出しなければならない。保有割合が1%以上増減したときも同様とする。ただし、適格機関投資家が純投資目的で保有し、かつ保有割合が10%以下である場合は、特例報告として四半期ごとの提出にとどめることができる。",
            "株式保有状況：信託銀行が純投資目的でA社株式の7.5%を保有し、今週0.4%を追加取得した。特例対象の適格機関投資家である。報告対応を決定せよ。",
            "株式保有状況：投資ファンドが経営支配目的でB社株式の5.8%を新規取得した。純投資目的ではない。報告対応を決定せよ。",
            [("sec_quarterly_special_report", "特例要件適合・四半期まとめ特例報告対象"), ("sec_5day_mandatory_filing", "経営参加目的・5営業日以内大量保有報告書提出必須"), ("sec_amendment_1pct_filing", "1%増減変動報告書即時提出"), ("sec_insider_trading_hold", "インサイダー取引規制調査保留"), ("sec_short_swing_profit_return", "短期売買差益返還請求手続"), ("sec_shareholder_registry_lock", "株主名簿閲覧請求権停止")],
            "sec_quarterly_special_report", "sec_5day_mandatory_filing"
        ),
        (
            "27",
            "医療過誤防止医薬品取違え安全マニュアル：ハイリスク薬（インスリン・高濃度塩化カリウム等）の投与指示を受けた看護師は、ダブルチェックを行った後でなければ投与してはならない。ただし、医師が直接立ち会い、かつ口頭指示ではなく電子カルテで確定処方された緊急心肺蘇生時においては、ダブルチェックを省略して即座に投与することができる。",
            "救急処置室：患者が心室細動を起こし、立ち会った救急部長の確定電子指示のもと、アドレナリン急速静注が要請された。看護師の行動を決定せよ。",
            "一般病棟：夜勤帯において、インスリン皮下注射の定期指示が出ているが、同僚看護師が別室ナースコール対応中で不在である。看護師の行動を決定せよ。",
            [("nurse_administer_immediate_cpr", "蘇生時直接立会確定指示・即時投与実行"), ("nurse_wait_double_check", "ハイリスク薬・同僚復帰ダブルチェック待機"), ("nurse_verbal_order_administer", "医師口頭指示復唱単独投与"), ("nurse_dose_reduce_half", "過誤防止自己判断半量投与"), ("nurse_pharmacist_dispense_wait", "院内薬剤師調剤立ち会い要請"), ("nurse_incident_report_file", "インシデント報告書事前作成")],
            "nurse_administer_immediate_cpr", "nurse_wait_double_check"
        ),
        (
            "28",
            "都市計画法開発許可基準：市街化調整区域内における建築物の新築は原則として許可されない。ただし、農業・林業・漁業に従事する者の居住用住宅、または周辺住民の日常生活に必要な日用品店舗であって延べ床面積100m2以内のものについては、都道府県知事の許可を受けて建築することができる。",
            "申請審査：市街化調整区域内において、地元専業農家が自らの世帯の居住用として延べ150m2の木造住宅を新築する計画である。許可判断を行え。",
            "申請審査：市街化調整区域内において、IT企業が自社の郊外サテライトオフィスとして延べ200m2の事務所を新築する計画である。許可判断を行え。",
            [("zoning_farmer_house_permit", "農林漁業者居住用住宅・開発許可承認"), ("zoning_office_prohibited", "市街化調整区域原則禁止・事務所建築不許可"), ("zoning_retail_100sqm_permit", "日常生活店舗特例100m2許可"), ("zoning_urbanization_redistrict", "市街化区域編入都市計画決定待機"), ("zoning_demolition_order", "違法建築是正除却命令"), ("zoning_variance_public_hearing", "都市計画公聴会諮問")],
            "zoning_farmer_house_permit", "zoning_office_prohibited"
        ),
        (
            "29",
            "企業会計基準第18号資産除去債務実務指針：有形固定資産の取得等に伴い将来の除去に要する負債が生じる場合、合理的な見積りが可能である限り資産除去債務を負債として計上しなければならない。ただし、将来の除去義務が賃貸借契約満了時等の法的な原状回復義務等に起因しない単なる任意の廃棄予定にすぎない場合は、計上してはならない。",
            "会計監査：本社ビルの定期建物賃貸借契約書において、退去時のスケルトン原状回復義務が明確に定められており、工事業者から確度の高い解体見積書を入手した。会計処理を決定せよ。",
            "会計監査：自社工場内の汎用工作機械について、経営陣が将来的に新機種へ買い換えてスクラップ廃棄したいという経営方針メモを作成したが、法令や契約上の撤去義務は存在しない。会計処理を決定せよ。",
            [("aro_recognize_liability", "法的原状回復義務あり・資産除去債務計上"), ("aro_do_not_recognize", "任意廃棄方針・資産除去債務計上不可"), ("aro_capitalize_full_expense", "除去費用即時全額費用処理"), ("aro_contingent_liability_note", "偶発債務として財務諸表注記"), ("aro_impairment_write_down", "固定資産減損損失引当"), ("aro_fair_value_revalue", "時価再評価差額計上")],
            "aro_recognize_liability", "aro_do_not_recognize"
        ),
        (
            "30",
            "サイバーセキュリティインシデント公表指針：社内ネットワークへの不正アクセスにより顧客のクレジットカード情報が外部へ漏洩した可能性がある場合、不確定な段階であっても5日以内に初報を公表しなければならない。ただし、フォレンジック調査機関の初動調査において、当該サーバーから外部への通信パケットが暗号化通信路で一切流出していないことが技術的に立証された場合は、公表を保留し監視を継続することができる。",
            "インシデント報告：カード決済GWサーバーでマルウェア感染が確認されたが、出口ファイアウォールの全通信パケットキャプチャ解析により、暗号化通信を含め外部への流出データは皆無であることが完全立証された。広報対応を決定せよ。",
            "インシデント報告：カード決済GWサーバーに不正侵入の痕跡があり、外部の不審なC2サーバーへ数GBの暗号化パケットが送信された形跡がある。漏洩対象の特定はまだ完了していない。広報対応を決定せよ。",
            [("incident_withhold_monitor", "流出皆無技術立証・公表保留監視継続"), ("incident_public_notice_5days", "流出懸念大・5日以内初報公式公表必須"), ("incident_card_issuer_reissue", "全会員カード強制再発行通知"), ("incident_server_isolate_shutdown", "当該サーバー物理回線切断停止"), ("incident_press_conference_immediate", "即時緊急記者会見開催"), ("incident_law_enforcement_report", "警察庁サイバー特命隊告発")],
            "incident_withhold_monitor", "incident_public_notice_5days"
        ),
    ]

    for gid, ctx, q1, q2, cdefs, t1, t2 in k6_defs:
        choices = make_choices(cdefs)
        pairs.extend([
            {
                "id": f"rc3b_nat_{gid}_s1",
                "group_id": f"rc3b_nat_{gid}",
                "family": "natural_japanese",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1}
            },
            {
                "id": f"rc3b_nat_{gid}_s2",
                "group_id": f"rc3b_nat_{gid}",
                "family": "natural_japanese",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2}
            }
        ])

    return pairs
