"""Blind v5 Family: Natural Japanese (30 pairs, 60 cases).

Choice count distribution:
- K=3: 10 pairs (nat_01 to nat_10)
- K=4: 15 pairs (nat_11 to nat_25)
- K=6: 5 pairs (nat_26 to nat_30)

Zero model inference during authoring; 100% fresh domain scenarios.
Token length strictly controlled (all <= 350 tokens).
Features realistic, nuanced Japanese operational vocabulary, indirect directives,
idiomatic expressions, and professional administrative/technical phrasing.
"""

from __future__ import annotations
from typing import Any, Dict, List


def get_natural_japanese_pairs() -> List[Dict[str, Any]]:
    pairs = []

    # K=3: 10 pairs (01..10)
    k3_defs = [
        (
            "01",
            "老舗酒造における大吟醸仕込みの醪（もろみ）品温管理指針。杜氏の伝承：『醪の湧き付きが穏やかで米の溶けが遅れ気味な折は、追い焚きにより品温をコンマ五度引き上げて発酵を促すべし。ただし泡立ちが過度に立ち上がり香気の抜けが懸念される場合は、むしろ冷水を回して品温の昇温を押し留めるが肝要である』。",
            "蔵人報告：『三日目の仕込みタンクですが、湧き付きが鈍く米粒の溶け出しも遅れております』。指図を選択せよ。",
            "sake_temp_raise_half_degree",
            "蔵人報告：『醪の泡が一気に盛り上がってきており、吟醸特有のエステル香が早くも飛び散りそうな気配です』。指図を選択せよ。",
            "sake_temp_cool_suppress",
            [
                ("sake_temp_raise_half_degree", "追い焚き品温引き上げ"),
                ("sake_temp_cool_suppress", "冷水循環昇温抑制"),
                ("sake_temp_natural_leave", "現状成り行き放置"),
            ],
        ),
        (
            "02",
            "地方自治体の窓口業務における住民票広域交付規程。手引き：『本人確認書類としてマイナンバーカードまたは運転免許証の提示を求めた際、券面記載事項と住民基本台帳の符号が確認できれば即座に交付手続きへ進めるものとする。しかしながら、提示書類の住所変更裏書きが未了であり現住所の確認が取れぬ場合は、交付を保留し本籍地への照会を案内されたい』。",
            "窓口来庁者：『運転免許証を提示します。先月引っ越しましたが裏面の公安印付き新住所記載も済んでいます』。対応を選択せよ。",
            "juminhyo_issue_proceed",
            "窓口来庁者：『免許証の住所は前住所のままで、裏書もまだ警察で更新していません』。対応を選択せよ。",
            "juminhyo_suspend_inquiry",
            [
                ("juminhyo_issue_proceed", "即座に交付手続き進行"),
                ("juminhyo_suspend_inquiry", "交付保留本籍照会案内"),
                ("juminhyo_reject_police_report", "警察通報不受理処分"),
            ],
        ),
        (
            "03",
            "精密機械加工現場における切削チップ摩耗判定内規。作業心得：『切削面の面粗度が良好でびびり振動の兆候もなければ、所定の規定寿命カウントに達するまでは刃具を交換せず加工を続行すること。一方で、仕上げ面に微小なむしれが生じ始め、刃先のホーニング摩耗が疑われる段階にあっては、規定寿命未達であっても躊躇なく刃具を更新すべし』。",
            "オペレーター点検：『切削面の光沢は極めて滑らかでびびり音も皆無、寿命カウントは75%です』。処置を選択せよ。",
            "tool_keep_machining_continue",
            "オペレーター点検：『まだ寿命カウントの半分ですが、ワーク表面にわずかなむしれ筋が目視されました』。処置を選択せよ。",
            "tool_replace_immediate_renew",
            [
                ("tool_keep_machining_continue", "刃具交換せず加工続行"),
                ("tool_replace_immediate_renew", "躊躇なく刃具を更新"),
                ("tool_increase_cutting_speed", "切削送り速度大幅増速"),
            ],
        ),
        (
            "04",
            "総合病院ICUの人工呼吸器離脱（ウィーニング）評価基準。主治医プロトコル：『自発呼吸トライアル（SBT）において呼吸回数が毎分30回未満に収まり浅速呼吸指数（RSBI）が105を下回っていれば、抜管に向けた覚醒プロトコルを進めて差し支えない。されど、呼吸努力に伴う肋間陥没が顕著となり酸素飽和度の維持に汲々とする様子が窺えるならば、直ちにPSV換気を再開し仕切り直すこと』。",
            "SBT開始30分後：呼吸数は毎分18回、RSBIは68で患者の表情も落ち着いている。方針を選択せよ。",
            "weaning_proceed_extubation",
            "SBT開始15分後：呼吸数は毎分34回に跳ね上がり、激しい下顎呼吸と著しい肋間陥没が出現した。方針を選択せよ。",
            "weaning_abort_resume_psv",
            [
                ("weaning_proceed_extubation", "抜管覚醒プロトコル進行"),
                ("weaning_abort_resume_psv", "直ちにPSV換気再開"),
                ("weaning_sedation_deepen_lock", "鎮静剤再投与完全固定"),
            ],
        ),
        (
            "05",
            "高級料亭の懐石料理における出汁取り秘伝書。板長訓示：『昆布出汁を引く折、鍋底に極小の気泡が湧き立つ沸騰直前の風情を見極めて昆布を速やかに引き上げるべし。引き上げを怠りグラグラと煮立たせてしまっては、ぬめりと雑味が溶け出し出汁の命たる清澄さが台無しとなるため、火を弱めて沸騰を未然に制するが肝心である』。",
            "煮方見習い報告：『鍋底の昆布周りから針の先ほどの泡が静かに立ち昇り始めました』。調理動作を選択せよ。",
            "dashi_pull_kombu_just_before",
            "煮方見習い報告：『火勢が強く、昆布を入れたまま全体が激しく煮立ち泡が吹きこぼれそうです』。調理動作を選択せよ。",
            "dashi_subdue_heat_suppress",
            [
                ("dashi_pull_kombu_just_before", "昆布速やか引き上げ"),
                ("dashi_subdue_heat_suppress", "火を弱め沸騰未然抑止"),
                ("dashi_add_strong_salt_boil", "強塩投入強火煮出し"),
            ],
        ),
        (
            "06",
            "地方信用金庫の融資回収管理マニュアル。営業方針：『取引先企業からの元利金返済遅延について、一時的な売掛金入金ズレに起因する確証が得られ資金繰り表の蓋然性が認められる間は、督促を猶予し柔軟にリスケジュール相談に応じる姿勢で臨む。他方で、代表者との連絡が杜撰となり事業実態の雲散霧消が懸念される事態に立ち至った際は、保全措置に間髪を入れず仮差押え手続きを着手されたい』。",
            "担当者報告：『老舗織物工場の社長から連絡あり、取引先官公庁の予算執行遅延証明書が提出されました』。対応を選択せよ。",
            "loan_grace_reschedule_consult",
            "担当者報告：『先週から社長の携帯電話が不通で工場も雨戸が閉ざされ、夜逃げの噂が近隣で立っています』。対応を選択せよ。",
            "loan_immediate_provisional_seizure",
            [
                ("loan_grace_reschedule_consult", "督促猶予リスケ相談応需"),
                ("loan_immediate_provisional_seizure", "間髪入れず仮差押え着手"),
                ("loan_full_debt_forgiveness", "元利金全額債権放棄"),
            ],
        ),
        (
            "07",
            "老舗旅館の客室おもてなし作法書。女将の教え：『お客様がお部屋にお着きになり旅の疲れを癒しておられる折は、手早くお茶を淹れて一礼し、過剰な言葉掛けを慎んで静謐な時間をお過ごしいただくよう心掛けること。ただし、お客様が館内施設の案内や周辺の見どころについて熱心に尋ねてこられた場合は、求めに応じて丁寧かつ淀みなくご案内を申し上げるべし』。",
            "客室状況：『長旅を終えたご夫婦が深く座椅子に腰掛け、窓外の庭園を無言で静かに眺めておられます』。接客を選択せよ。",
            "hospitality_quiet_tea_bow",
            "客室状況：『お客様がパンフレットを手に持ち、近くの美術館の開館時間や名所について質問されました』。接客を選択せよ。",
            "hospitality_detailed_guide_offer",
            [
                ("hospitality_quiet_tea_bow", "手早くお茶一礼静謐維持"),
                ("hospitality_detailed_guide_offer", "求めに応じ淀みなくご案内"),
                ("hospitality_immediate_meal_serve", "夕食配膳即時開始"),
            ],
        ),
        (
            "08",
            "伝統木造建築における宮大工の棟上げ規程。棟梁の言：『通し柱に狂いがなく下げ振りの鉛直が寸分の狂いもなく定まっているときは、掛け矢を振るって鼻栓・車知栓をきっちりと打ち込み架構を固めるべし。もしや材の反りにより微小な傾きが認められるときは、無理に栓を打ち込まず、仮筋交いの締め直しによりまず建ちの歪みを正すを先途とすべし』。",
            "現場確認：『四隅の通し柱に下げ振りを当てたところ、墨壺の墨線と下げ振り糸が寸分違わず一致しております』。作業を選択せよ。",
            "carpenter_drive_pins_fasten",
            "現場確認：『東側の通し柱が西に五厘ほど倒れ、下げ振りの振れ止めと柱芯にわずかな開きが認められます』。作業を選択せよ。",
            "carpenter_brace_correct_lean",
            [
                ("carpenter_drive_pins_fasten", "鼻栓車知栓きっちり打ち込み"),
                ("carpenter_brace_correct_lean", "仮筋交い締め直し建ち矯正"),
                ("carpenter_dismantle_all_timbers", "全木組み即時解体"),
            ],
        ),
        (
            "09",
            "都市河川舟運の小型遊覧船運航内規。船長心得：『河川水面の波立ちが穏やかで橋梁下通過時のクリアランスに余裕がある折は、定刻ダイヤ通りの遊覧周遊を継続する。されど上流ダムの放流通告を受信し浮遊ゴミの流下や急な引き波の兆候が見て取れる際は、遊覧を打ち切って速やかに最寄りの退避桟橋へ舫い綱を取るべし』。",
            "水上見張り報告：『川面は鏡のようで水深・桁下空間とも十分、風もそよ風程度です』。操船を選択せよ。",
            "boat_cruise_regular_schedule",
            "水上見張り報告：『上流から濁り水と流木が流下し始め、川底からゴロゴロと石の転がる音が響いております』。操船を選択せよ。",
            "boat_abort_berth_evacuate",
            [
                ("boat_cruise_regular_schedule", "定刻ダイヤ通り周遊継続"),
                ("boat_abort_berth_evacuate", "遊覧打ち切り最寄り退避"),
                ("boat_anchor_middle_river", "流心錨泊待機"),
            ],
        ),
        (
            "10",
            "老舗和菓子舗の餡練り指南書。菓子司の掟：『小豆が十分に煮崩れ銅釜の底で木べらに重みのある手応えが伝わってきた折は、一気に火を強めて仕上げの練り上げにかかり艶を出すべし。万一にも小豆の芯に硬さが残り水気が抜けきらぬうちは、強火を戒め中火でじっくりと差し水を加えつつ煮含めるを本分と心得よ』。",
            "釜場観察：『小豆は完全に破砕されて滑らかなペースト状となり、木べらを持ち上げると重厚な帯となって垂れます』。火加減を選択せよ。",
            "sweet_bean_high_heat_gloss",
            "釜場観察：『煮汁はまだしゃばしゃばしており、指で小豆を潰すと中央に白い芯の硬さが感じられます』。火加減を選択せよ。",
            "sweet_bean_mid_heat_water_simmer",
            [
                ("sweet_bean_high_heat_gloss", "一気に強火仕上げ練り艶出し"),
                ("sweet_bean_mid_heat_water_simmer", "中火じっくり差し水煮含め"),
                ("sweet_bean_ice_quench_stop", "氷水急冷作業中止"),
            ],
        ),
    ]

    for pid, ctx, q1, t1, q2, t2, chs in k3_defs:
        choices = [{"id": cid, "text": ctxt} for cid, ctxt in chs]
        pairs.append({
            "pair_id": f"rc3_blind5_nat_{pid}",
            "family": "natural_japanese",
            "k": 3,
            "case_1": {
                "id": f"rc3_blind5_nat_{pid}_s1",
                "group_id": f"rc3_blind5_nat_{pid}",
                "family": "natural_japanese",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1},
            },
            "case_2": {
                "id": f"rc3_blind5_nat_{pid}_s2",
                "group_id": f"rc3_blind5_nat_{pid}",
                "family": "natural_japanese",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2},
            },
        })

    # K=4: 15 pairs (11..25)
    k4_defs = [
        (
            "11",
            "茶道宗家の免状申請に関する取扱要綱。内規：『門下が茶名拝受の申請を行うにあたり、皆伝までの相伝を過不足なく修め師範の推薦状が添付されておる場合は、滞りなく家元の決裁へ上程するものとする。しかしながら、所定の稽古年数に不足があり相伝の履修履歴に疑義なしとせぬ折は、書類を門弟へ返付し再度の精進を促すべし』。",
            "事務局審査：『点前履歴簿の照合が完了し、十年の年季と全科目の相伝、ならびに正教授の自筆推薦状が整っております』。事務処理を選択せよ。",
            "chado_submit_iemoto_approval",
            "事務局審査：『申請者の在籍年数は三年で、中伝の修了印が帳面に見当たらず履修歴に看過できぬ欠落があります』。事務処理を選択せよ。",
            "chado_return_diligence_request",
            [
                ("chado_submit_iemoto_approval", "滞りなく家元決裁へ上程"),
                ("chado_return_diligence_request", "書類返付再修練促し"),
                ("chado_expel_from_school", "破門処分通達"),
                ("chado_grant_honorary_degree", "名誉皆伝即時追贈"),
            ],
        ),
        (
            "12",
            "老舗百貨店の外商部顧客応対基準。心得：『上顧客よりご贔屓の銘柄の特別調達を仰せつかった折、国内直営店に在庫の目処が立ち納期のご要望に添える算段がつくならば、速やかに確保の手続きを取る。しかしながら、全国完売にして海外アトリエへの特注すら叶わずご期待に背くことが明白な折は、無理な確約を慎み、代替の逸品を携えて丁重にお詫びとご提案を申し上げるのが筋である』。",
            "顧客相談：『限定生産の漆塗り万年筆を探している。納期は来月の記念日までで構わない』。銀座本店に手配可能な在庫が1点あり。対応を選択せよ。",
            "department_procure_and_secure",
            "顧客相談：『十年前の限定手織り絨毯と同じものを今週中に納品してほしい』。工房は閉鎖され世界在庫ゼロ。対応を選択せよ。",
            "department_apology_alternative_suggest",
            [
                ("department_procure_and_secure", "速やかに確保手続き実施"),
                ("department_apology_alternative_suggest", "お詫びと代替逸品ご提案"),
                ("department_demand_cash_advance", "全額前受金即時徴収"),
                ("department_ignore_customer_call", "連絡放置音信不通"),
            ],
        ),
        (
            "13",
            "地方自治体の消防団招集における出動判断基準。団長達し：『気象台より大雨洪水警報が発令され河川の水位観測所で警戒水位突破が視認された折は、団員に参集を命じ水防団待機所へ結集せよ。しかしながら、降雨が散発的で水位の急伸もなく一過性の通り雨と推察される折にあっては、むやみにサイレンを吹鳴させず各分団長による見回りに留めおくのが分別である』。",
            "河川状況：『上流水位計が氾濫警戒水位を突破し、堤防法面に激しい洗掘が視認されております』。措置を選択せよ。",
            "fire_corps_muster_flood_center",
            "河川状況：『雷鳴は聞こえますが雨足は弱く、水位は平水よりわずか十センチ高い程度で推移しております』。措置を選択せよ。",
            "fire_corps_patrol_only_keep",
            [
                ("fire_corps_muster_flood_center", "団員参集水防待機所結集"),
                ("fire_corps_patrol_only_keep", "むやみに出動せず見回りに留める"),
                ("fire_corps_retreat_home", "全団員即時解散帰宅"),
                ("fire_corps_dynamite_bank", "堤防爆破放水"),
            ],
        ),
        (
            "14",
            "歌舞伎興行における舞台進行の幕引き作法。狂言方内規：『役者の見得が極まり柝（き）の頭（かしら）が高らかに響き渡った瞬間を見逃さず、一文字に定式幕を引き切るべし。万一にも役者の台詞回しが引っ掛かり所定の極まりに至らぬうちは、幕を走らせて舞台の腰を折ることのなきよう、狂言方の合図があるまで柝番は手控えるが掟である』。",
            "舞台現況：『花道で弁慶の引っ込みの六方が出揃い、拍子木が鋭くトザイトザイと響いて見得が完全に決まりました』。進行を選択せよ。",
            "kabuki_draw_curtain_punctual",
            "舞台現況：『舞台中央の立役が長台詞の途中で言い淀み、まだ決めポーズの見得に入っておりません』。進行を選択せよ。",
            "kabuki_hold_clapper_standby",
            [
                ("kabuki_draw_curtain_punctual", "定式幕一文字引き切り"),
                ("kabuki_hold_clapper_standby", "幕を走らせず柝番手控え"),
                ("kabuki_blackout_all_lights", "舞台全暗転即時消灯"),
                ("kabuki_revolve_stage_fast", "廻り舞台急速回転"),
            ],
        ),
        (
            "15",
            "老舗旅館の温泉源泉管理における湯守の定め。湯守の口伝：『引き湯の樋（とい）に湯の花が適度に付き、湯口の湯温が四十三度を保ち肌触り滑らかな折は、バルブに手を触れず自然の恵みに任せて湯守りを全うすべし。しかしながら、源泉井戸の自噴圧が急に翳り湯温が四十度を割り込むような気配があれば、ただちに地中揚湯ポンプを微速で補佐起動し湯量の涸渇を救うべし』。",
            "今朝の湯口点検：『湯の花の付着もほどよく、湯温は四十三度二分、湯量も豊富に溢れ出ております』。湯守の作業を選択せよ。",
            "onsen_leave_natural_steady",
            "今朝の湯口点検：『湯口の勢いが目に見えて細り、湯温が三十八度五分までぬるくなっております』。湯守の作業を選択せよ。",
            "onsen_start_lift_pump_assist",
            [
                ("onsen_leave_natural_steady", "手触れず自然任せ維持"),
                ("onsen_start_lift_pump_assist", "揚湯ポンプ微速補佐起動"),
                ("onsen_pour_cold_tap_water", "水道水大量加水冷却"),
                ("onsen_drain_tub_completely", "浴槽全排水施錠"),
            ],
        ),
        (
            "16",
            "寺院における鐘楼の除夜の鐘撞き内規。執事通達：『参拝の信徒が列をなし厳かな気配が境内に満ちている折は、百八の梵鐘を一打一打百八秒の間隔を置いて余韻を味わうよう撞き継ぐこと。ただし、突風混じりの荒天により鐘木（しゅもく）が煽られ参拝者の安全に些かの危惧が生じた場合は、即座に撞球を中止して鐘楼周囲に立入規制の綱を張るべし』。",
            "境内気候：『風は微風、雪がちらつく静夜で参拝者が整然と手を合わせて並んでおります』。鐘楼の指図を選択せよ。",
            "temple_strike_bell_rhythm",
            "境内気候：『猛烈な地吹雪となり鐘木が大きく暴れ、足元の石段も凍結して参拝者が転倒しそうな危険があります』。鐘楼の指図を選択せよ。",
            "temple_halt_strike_cordon",
            [
                ("temple_strike_bell_rhythm", "余韻味わい撞き継ぎ"),
                ("temple_halt_strike_cordon", "撞球中止立入規制綱張り"),
                ("temple_speed_up_tenfold", "十倍速連続乱打"),
                ("temple_demolish_bell_tower", "鐘楼即時取り壊し"),
            ],
        ),
        (
            "17",
            "高級料亭の器（うつわ）手入れにおける帳場規程。器守り覚書：『名工の手による古伊万里や魯山人の焼き物は、使用後にぬるま湯と柔らかい綿布のみで優しく洗い自然乾燥を旨とすべし。間違っても現代の強力なアルカリ合成洗剤や食器洗浄乾燥機に投じるがごとき暴挙は、貫入を傷め金彩を剥落させる元凶なれば厳禁とする』。",
            "洗い場：『今宵の懐石で使われた江戸時代中期の染付古伊万里の向付を洗います』。適切な洗い方を選択せよ。",
            "pottery_warm_water_cotton_wash",
            "洗い場：『宴会が長引き洗い物が溜まっています。魯山人の鉢を早く片付けたいです』。適切な洗い方を選択せよ。",
            "pottery_forbid_dishwasher_detergent",
            [
                ("pottery_warm_water_cotton_wash", "ぬるま湯綿布優しく洗浄"),
                ("pottery_forbid_dishwasher_detergent", "食洗機合成洗剤厳禁手洗い"),
                ("pottery_sandpaper_polish", "紙やすり研磨磨き上げ"),
                ("pottery_boiling_bleach_soak", "熱湯塩素漂白浸け置き"),
            ],
        ),
        (
            "18",
            "地方鉄道のSL観光列車運行基準。機関士心得：『ボイラー罐圧が十六気圧を指し投炭の燃焼効率が極めて良好なる折は、シリンダーのドレンコックを閉じ加減にして力強いドラフト音とともに勾配を登坂すべし。万一、ボイラー水位計の下限ガラスに水面が見え隠れするような水切れの兆候があるときは、直ちに焚き口扉を開いて投炭を止め、インジェクター給水を全開にして空焚き爆発を食い止めよ』。",
            "機関台点検：『罐圧は十六気圧満載、水面はゲージ中央で安定し煙色は綺麗な薄灰色です』。機関操作を選択せよ。",
            "steam_loco_close_drain_climb",
            "機関台点検：『登坂途中に水位計の水面が急速に下端を割り込み、水鏡が消失しかけております』。機関操作を選択せよ。",
            "steam_loco_stop_coal_water_inject",
            [
                ("steam_loco_close_drain_climb", "ドレン閉じ力強く登坂"),
                ("steam_loco_stop_coal_water_inject", "投炭停止給水インジェクター全開"),
                ("steam_loco_overturn_boiler", "機関車脱線転転倒"),
                ("steam_loco_full_reverse_run", "全力後進暴走"),
            ],
        ),
        (
            "19",
            "日本庭園の名木手入れにおける植木職人の作法。庭師覚書：『五葉松の古木について、新芽の伸びが均一で樹勢が旺盛な折は、緑摘み（みどりづみ）と古葉むしりを丁寧に施して日当たりと風通しを整えるべし。されど、松喰い虫の穿孔痕が見出され葉先が赤褐色に黄変し始めた折は、呑気に葉透かしをしている場合ではなく、ただちに樹幹注入剤を打ち込み枯死の蔓延を防ぐが最優先である』。",
            "庭園巡回：『樹齢三百年五葉松の新梢は力強く青々と伸び、害虫の付着痕も皆無です』。職人の手入れを選択せよ。",
            "gardener_pine_midoritsumi_trim",
            "庭園巡回：『主幹の皮下に無数の木屑が吹き出し、上部の葉群が一斉に赤茶色に縮れ始めております』。職人の手入れを選択せよ。",
            "gardener_pine_trunk_injection",
            [
                ("gardener_pine_midoritsumi_trim", "緑摘み古葉むしり整定"),
                ("gardener_pine_trunk_injection", "樹幹注入剤即時施工"),
                ("gardener_pine_burn_all_roots", "根元火炎放射全焼却"),
                ("gardener_pine_chop_down_fast", "主幹即時チェーンソー伐採"),
            ],
        ),
        (
            "20",
            "老舗呉服店の仕立て直し（洗い張り）相談内規。番頭の心得：『お客様がお持ち込みになられた形見の訪問着について、八掛や胴裏の黄ばみはあるものの表地の絹糸に確かな張りがある折は、解き洗い張りを行い寸法を直して再生をお勧めする。しかしながら、長年の湿気で絹糸自体が脆化し指で軽く引くだけで裂けるような寿命枯渇にあっては、洗い張りに耐えられぬ旨を丁重に説明し額装や小物への仕立て替えをご提案するが誠実というものである』。",
            "反物鑑定：『昭和初期の加賀友禅ですが、裏地は色褪せているものの表地の縮緬はしなやかで十分な引張強度を保っています』。相談回答を選択せよ。",
            "kimono_unravel_wash_stretch",
            "反物鑑定：『大正時代の紋付縮緬ですが、折り目が粉を吹くように繊維崩壊を起こし布地を支えきれません』。相談回答を選択せよ。",
            "kimono_explain_fragile_suggest_frame",
            [
                ("kimono_unravel_wash_stretch", "解き洗い張り寸法再生お勧め"),
                ("kimono_explain_fragile_suggest_frame", "耐えられぬ旨説明額装提案"),
                ("kimono_bleach_hot_soak", "強アルカリ熱湯漂白浸け"),
                ("kimono_throw_into_trash", "無断廃棄処分"),
            ],
        ),
        (
            "21",
            "老舗造り酒屋の杜氏による酒母（生酛）育成指針。秘伝：『生酛の乳酸菌育成期において、品温が所定の経過線を辿り乳酸の酸味が清冽に立ち昇ってきた折は、暖気を止め自然放冷にて酵母の増殖を待つべし。万一、雑菌の繁殖により納豆様の異臭が漂い始め酸度が異常に急伸した折は、もはや酒母の立ち直りは望めぬゆえ、潔く当該醪桶を破棄し仕込み蔵の熱湯消毒を徹底せよ』。",
            "酒母室点検：『品温経過良好、清々しいヨーグルト様の乳酸香が漂い味もキリリと冴えております』。判断を選択せよ。",
            "kimoto_stop_warming_cool_yeast",
            "酒母室点検：『桶の縁から粘り気のある泡が吹き出し、明らかな納豆臭と腐敗酸敗味が検知されました』。判断を選択せよ。",
            "kimoto_discard_vat_disinfect",
            [
                ("kimoto_stop_warming_cool_yeast", "暖気停止自然放冷育成"),
                ("kimoto_discard_vat_disinfect", "潔く桶破棄熱湯消毒徹底"),
                ("kimoto_add_industrial_sugar", "工業用砂糖大量投入"),
                ("kimoto_bottle_and_ship_market", "そのまま瓶詰め即日出荷"),
            ],
        ),
        (
            "22",
            "漆工芸における本堅地（ほんかたじ）下地塗り指針。塗師の掟：『生漆に地の粉を練り合わせた下地漆について、布着せが完全に密着し乾き具合が手の甲に吸い付くような適度な締まりを見せた折は、研ぎ炭を用いて平滑に砥ぎ出すべし。もしや湿度が足りず下地が生乾きで爪がめり込むような状態にあっては、決して炭を当ててはならず、湿度七十五度の漆風呂に静かに戻して乾燥の熟成を待つが肝要である』。",
            "下地検査：『布着せの上に施した地の粉下地はカチカチに硬化し、手の甲を当てても一切べたつきません』。作業を選択せよ。",
            "urushi_charcoal_polish_smooth",
            "下地検査：『漆風呂から出した素地ですが、表面を指先で押すとわずかに弾力があり爪の跡が残ります』。作業を選択せよ。",
            "urushi_return_humid_chamber_wait",
            [
                ("urushi_charcoal_polish_smooth", "研ぎ炭用い平滑研ぎ出し"),
                ("urushi_return_humid_chamber_wait", "漆風呂に戻し乾燥熟成待機"),
                ("urushi_hair_dryer_heat_blast", "温風ドライヤー直当て強制乾燥"),
                ("urushi_scrape_off_metal_blade", "金属刃物削り落とし"),
            ],
        ),
        (
            "23",
            "老舗料亭の鮎炭火焼きにおける焼き方指南。炭火番の極意：『串打ちした鮎の肌に塩がほどよく馴染み、備長炭の熾火（おきび）の上で皮目がパリッと黄金色に焼き上がった折は、うちわで灰を煽ることなく遠火の強火で芯までじっくり火を通すべし。ただし、鮎の脂が落ちて炭火から黒煙と炎が立ち上がった折は、魚を炎から速やかに遠ざけ、灰を薄く撒いて火勢を鎮めるが先決である』。",
            "焼き場状況：『炭は赤々と熾り、鮎の表面は焦げ目なく香ばしい湯気が立ち上っております』。焼き番の動作を選択せよ。",
            "ayu_far_strong_heat_cook",
            "焼き場状況：『鮎の腹から落ちた脂に引火し、赤い炎が串の魚体に直接触れて黒焦げになりそうです』。焼き番の動作を選択せよ。",
            "ayu_move_away_scatter_ash",
            [
                ("ayu_far_strong_heat_cook", "遠火強火じっくり芯通し"),
                ("ayu_move_away_scatter_ash", "炎から遠ざけ灰撒き鎮火"),
                ("ayu_pour_cold_water_pot", "冷水バケツぶちまけ消火"),
                ("ayu_blow_pure_oxygen_blast", "高圧純酸素吹き付け"),
            ],
        ),
        (
            "24",
            "文楽（人形浄瑠璃）興行の太夫・三味線掛合規程。床（ゆか）の約束事：『太夫の語りが情感極まり、三味線の撥（ばち）の音が緊迫した間の手と呼応して劇場の空気を支配している折は、息の合った掛合をそのままクライマックスまで一気に引き締めて語り切るべし。されど三味線の三の糸が突然切損し音が途絶えた折は、太夫は独り善がりに喚き散らさず、撥音の復旧を静かに間を保って見守り呼吸を整えるべし』。",
            "舞台演奏：『太夫のクドキに三味線の重厚な三の糸がぴったり寄り添い、客席は水を打ったように静まり返っています』。演奏動作を選択せよ。",
            "bunraku_unison_climax_narrate",
            "舞台演奏：『盛り上がりの直前、鋭い音とともに三味線の細糸が千切れ、三味線弾きが予備の糸を掛け直しています』。太夫の動作を選択せよ。",
            "bunraku_pause_breath_await_repair",
            [
                ("bunraku_unison_climax_narrate", "息の合った掛合語り切り"),
                ("bunraku_pause_breath_await_repair", "静かに間を保ち復旧見守り"),
                ("bunraku_scream_karaoke_style", "絶叫マイクパフォーマンス"),
                ("bunraku_smash_shamisen_stage", "三味線叩き壊し退場"),
            ],
        ),
        (
            "25",
            "日本刀の鍛錬における刀匠の焼き入れ心得。鍛冶場口伝：『刀身を炭火で熱し、鋼の色が朝焼けの雲のごとき薄赤（約八百度）に均一に染まった刹那、迷わず舟（水槽）に一気に焼き刃を沈めるべし。もしや棟側と刃先で赤らみ方にムラがあり温度の偏りが認められる折は、決して水に入れてはならず、フイゴを調整して再度じっくりと熱を回し均一な温度を待つべし』。",
            "焼き入れ前：『鞴（ふいご）の風に煽られた刀身は切先から元まで一点の曇りもなく均一な薄紅色に輝いております』。刀匠の処置を選択せよ。",
            "swordsmith_quench_water_instant",
            "焼き入れ前：『切先ばかりが白熱し、元の方はまだ黒みが残って刀身前後の色合いが大きく乖離しております』。刀匠の処置を選択せよ。",
            "swordsmith_reheat_uniform_temp_wait",
            [
                ("swordsmith_quench_water_instant", "迷わず舟の水に焼き入れ"),
                ("swordsmith_reheat_uniform_temp_wait", "水入れず再加熱均一化待機"),
                ("swordsmith_strike_cold_hammer", "冷えた金敷で強打破砕"),
                ("swordsmith_dump_oil_barrel", "ガソリン缶へ投下"),
            ],
        ),
    ]

    for pid, ctx, q1, t1, q2, t2, chs in k4_defs:
        choices = [{"id": cid, "text": ctxt} for cid, ctxt in chs]
        pairs.append({
            "pair_id": f"rc3_blind5_nat_{pid}",
            "family": "natural_japanese",
            "k": 4,
            "case_1": {
                "id": f"rc3_blind5_nat_{pid}_s1",
                "group_id": f"rc3_blind5_nat_{pid}",
                "family": "natural_japanese",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1},
            },
            "case_2": {
                "id": f"rc3_blind5_nat_{pid}_s2",
                "group_id": f"rc3_blind5_nat_{pid}",
                "family": "natural_japanese",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2},
            },
        })

    # K=6: 5 pairs (26..30)
    k6_defs = [
        (
            "26",
            "能楽シテ方の装束付けにおける後見（こうけん）の掟。能楽堂規程：『シテが面（おもて）を掛け鏡の間で精神を統一し幕上がりの合図を出した折は、後見は速やかに揚幕（あげまく）を掲げ橋掛かりへの出を促すべし。ただし、面の紐に緩みが生じシテの眼と面の目の孔（めづら）に僅かでも狂いが認められる折は、決して幕を上げてはならず、紐を締め直して視野を完璧に正すを第一とせよ』。",
            "鏡の間：『シテは面を付け姿見を前に静止、深く息を吐いて「お幕」と小声で発声されました。面付けの狂いは皆無です』。後見の動作を選択せよ。",
            "noh_raise_curtain_hashigakari",
            "鏡の間：『シテが首を傾げた際、面の右紐がずれて面の右目が完全に塞がっているのが後見の目に入りました』。後見の動作を選択せよ。",
            "noh_retie_mask_cord_correct",
            [
                ("noh_raise_curtain_hashigakari", "揚幕掲げ橋掛かり出促し"),
                ("noh_retie_mask_cord_correct", "幕上げず面紐締め直し視野矯正"),
                ("noh_shout_cancel_performance", "大声で公演中止叫び"),
                ("noh_push_shite_back", "シテの背中を舞台へ突き飛ばす"),
                ("noh_strip_costume_immediately", "装束即座剥ぎ取り"),
                ("noh_switch_face_makeup", "白塗り化粧塗り替え"),
            ],
        ),
        (
            "27",
            "大相撲本場所における行司の軍配差違え防止内規。審判部内規：『立合いが成立し両力士の攻防の末、一方が完全に土俵外に踏み出し足の裏が蛇の目の砂を掃いた刹那、行司は確信を持って勝者に軍配を上げるべし。万一、両力士がもつれ合って同時に土俵外に転落し軍配の行方に疑念が残る際は、物言い（審判団の協議）を待って勝負審判の合議決定に全幅の信頼を預けるが筋目である』。",
            "土俵際攻防：『東方力士の上手投げが決まり、西方力士の右足が土俵の外へ明瞭に踏み出しました』。行司の所作を選択せよ。",
            "sumo_raise_gunbai_winner",
            "土俵際攻防：『両力士が組み合ったまま同体で激しく土俵下へ転落し、どちらの体が先に落ちたか目視困難です』。行司の所作を選択せよ。",
            "sumo_await_judges_conference",
            [
                ("sumo_raise_gunbai_winner", "確信持ち勝者へ軍配上げ"),
                ("sumo_await_judges_conference", "物言い待ち審判合議決定に預ける"),
                ("sumo_declare_draw_no_contest", "勝手引き分け無効宣言"),
                ("sumo_order_restart_immediately", "独断取り直し即座命令"),
                ("sumo_flee_from_dohyo", "土俵から逃走退席"),
                ("sumo_strike_wrestler_fan", "軍配で力士殴打"),
            ],
        ),
        (
            "28",
            "老舗線香・香木商の沈香（じんこう）鑑定指南書。当主の遺訓：『持ち込まれた伽羅・沈香について、銀葉（ぎんよう）の上で聞香（もんこう）した折、高雅な甘みと辛みが幾重にも立ち上がり後味の残り香が清らかならば、極上名香として帳面に記し相応の高値で買い受けるべし。もしや熱した際にツンと鼻を突く樹脂接着剤や粗悪油の刺激臭が混じる折は、贋作に間違いなきゆえ、決して手を出さず穏便にお引き取り願うが身の守りである』。",
            "聞香鑑定：『銀葉に乗せて温めたところ、幽玄極まりない甘露の香りが立ち、雑味のない至福の余韻が部屋を満たしました』。商家の対応を選択せよ。",
            "kodo_record_high_price_purchase",
            "聞香鑑定：『火にかざした途端、石油化学系の異臭と人工香料のけばけばしい刺激臭で鼻の奥が痛くなりました』。商家の対応を選択せよ。",
            "kodo_reject_counterfeit_decline",
            [
                ("kodo_record_high_price_purchase", "極上名香記帳高値買受"),
                ("kodo_reject_counterfeit_decline", "贋作見極め穏便引き取り願い"),
                ("kodo_burn_all_stock_fire", "店内全香木即時焼却"),
                ("kodo_report_police_arrest", "警察通報即時逮捕要求"),
                ("kodo_dilute_water_perfume", "水で薄めて香水化"),
                ("kodo_rebrand_cheap_incense", "大衆線香として格安叩き売り"),
            ],
        ),
        (
            "29",
            "京都西陣織の手機（てばた）職人による錦織製織内規。織元作法：『経糸（たていと）の開口が整い緯糸（よこいと）の杼（ひ）が滑らかに通り、打ち込み筬（おさ）の手応えが絹鳴りの音とともに均一に決まる折は、一定のリズムを保ちつつ一越一越丹念に織り進むべし。万一、経糸の極細絹糸が一筋でも切れ杼道（ひみち）に引っ掛かりが生じた折は、機織りを直ちに止め、機結び（はたむすび）にて糸を継ぎ直すを怠るべからず』。",
            "機織り現場：『杼の飛びは極めて快調、筬打ちの音も心地よく絹糸の張力は全幅にわたり寸分の乱れもありません』。職人の動作を選択せよ。",
            "nishijin_keep_rhythm_weave_steady",
            "機織り現場：『杼を通した瞬間、パチンと微かな糸切れの感触があり金糸の隣の経糸が弛んで垂れ下がりました』。職人の動作を選択せよ。",
            "nishijin_halt_loom_tie_knot",
            [
                ("nishijin_keep_rhythm_weave_steady", "リズム保ち一越丹念製織"),
                ("nishijin_halt_loom_tie_knot", "機止め機結び糸継ぎ直し"),
                ("nishijin_cut_all_warp_threads", "全経糸ハサミ切断"),
                ("nishijin_press_heavy_iron", "高温アイロン直接圧着"),
                ("nishijin_spray_chemical_glue", "化学接着剤噴霧固定"),
                ("nishijin_accelerate_motor_drive", "電動モーター超高速化"),
            ],
        ),
        (
            "30",
            "伝統和傘の骨組み張りにおける傘職人の掟。張師の伝授：『真竹の骨に和紙を糊付けする折、骨の間隔が扇状に均等に広がり和紙がたるみなくピント張られた折は、へらで骨筋に沿ってしっかりと扱き（こき）を入れ糊を馴染ませるべし。もしや和紙に寄り皺（しわ）が寄り骨から浮き上がっている箇所を見出した折は、乾燥する前にすぐさま和紙を一旦剥がし、糊の引き直しにより皺を丹念に伸ばすを職人の意地とせよ』。",
            "張り場点検：『貼り合わせた手漉き和紙は骨全体に太鼓の皮のように張り詰め、気泡や偏りは微塵もありません』。傘職人の作業を選択せよ。",
            "wagasa_smooth_along_ribs",
            "張り場点検：『親骨と小骨の継ぎ目付近の和紙に斜めの寄り皺が寄り、接着面が白く浮き上がっております』。傘職人の作業を選択せよ。",
            "wagasa_peel_repaste_remove_wrinkle",
            [
                ("wagasa_smooth_along_ribs", "へらで骨筋沿い扱き馴染ませ"),
                ("wagasa_peel_repaste_remove_wrinkle", "和紙剥がし糊引き直し皺伸ばし"),
                ("wagasa_crush_bamboo_frame", "竹骨足蹴りへし折り"),
                ("wagasa_staple_metal_clips", "金属ホチキス全周留め"),
                ("wagasa_bake_direct_flame", "直火強火乾燥"),
                ("wagasa_soak_oil_vat_drown", "油桶ドブ漬け放置"),
            ],
        ),
    ]

    for pid, ctx, q1, t1, q2, t2, chs in k6_defs:
        choices = [{"id": cid, "text": ctxt} for cid, ctxt in chs]
        pairs.append({
            "pair_id": f"rc3_blind5_nat_{pid}",
            "family": "natural_japanese",
            "k": 6,
            "case_1": {
                "id": f"rc3_blind5_nat_{pid}_s1",
                "group_id": f"rc3_blind5_nat_{pid}",
                "family": "natural_japanese",
                "context": ctx,
                "question": q1,
                "choices": choices,
                "target": {"choice_id": t1},
            },
            "case_2": {
                "id": f"rc3_blind5_nat_{pid}_s2",
                "group_id": f"rc3_blind5_nat_{pid}",
                "family": "natural_japanese",
                "context": ctx,
                "question": q2,
                "choices": choices,
                "target": {"choice_id": t2},
            },
        })

    return pairs
