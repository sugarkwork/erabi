"""Build a small, original NPC action-routing candidate corpus; no external APIs."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "npc_tool_routing_v1"

# Worlds, rather than individual rows, are held out. Paired states stay together.
WORLDS = [
    ("harbor", "train", "霧港", "港の案内人ミオ"),
    ("forest", "train", "樹冠の村", "森の案内人リネ"),
    ("desert", "train", "砂鐘の街", "街の案内人サラ"),
    ("island", "dev", "波音島", "島の案内人ユイ"),
    ("castle", "eval", "黒曜城下", "城下の案内人ノア"),
]

ACTIONS = {
    "talk": "会話だけで返答する（外部ツールを使わない）",
    "web": "Web検索で現実世界の最新情報を調べる",
    "image_create": "イラスト生成ツールで新しい画像を作る",
    "video_create": "動画生成ツールで短い映像を作る",
    "command": "許可された開発環境のコマンドを実行する",
    "screenshot": "現在のゲーム画面のスクリーンショットを取得する",
    "image_analyze": "添付された画像を解析する",
    "game_state": "ゲーム状態APIで現在の所持品・位置・天候を照会する",
    "quest_log": "クエスト記録APIで達成状況を照会する",
    "pathfind": "ゲーム内経路探索ツールで現在地からの道順を計算する",
}

# A longer, coherent conversation: the current request must override earlier topics.
LONG_HISTORY = "\n".join(
    f"プレイヤー: {topic}。今はまだ確認や制作を頼まず、旅の思い出として話しているよ。\n"
    f"NPC: {reply}。必要になったら、その時点の目的に合わせて手伝うね。"
    for topic, reply in [
        ("最初の朝、宿屋で古い旅帳を見つけた", "旅帳にはこの土地の昔の祭りが記されていた"),
        ("二日目、石畳の広場で吟遊詩人の歌を聞いた", "歌は失われた橋を渡る商人の物語だった"),
        ("市場では赤い布を売る店主に話しかけた", "店主は布の染め方を丁寧に教えてくれた"),
        ("北の門から丘の上の風車を眺めた", "風車は夜になると青い灯りをともすらしい"),
        ("途中で薬草師に温かいお茶をもらった", "お茶は旅の疲れを和らげると評判だ"),
        ("小道に並んだ石碑の文字を写した", "古い文字は今の地名の由来を伝えている"),
        ("夕暮れに宿へ戻って靴を乾かした", "雨はすぐに上がって空に星が見えた"),
        ("翌朝は書庫でこの土地の歴史を読んだ", "書庫には旅人の手紙も保管されていた"),
        ("古い地図と新しい地図で川の形が違った", "昔の洪水で流れが変わったと説明されている"),
        ("仲間が落とした手袋を道端で見つけた", "手袋は仲間に返したので今は所持していない"),
        ("鍛冶屋で銀色の飾りを見せてもらった", "飾りは注文品で店にはまだ並んでいない"),
        ("橋の修理を手伝う人々を見かけた", "工事は掲示板の依頼と関係しているかもしれない"),
        ("夜の広場で紙の灯籠を眺めた", "灯籠は毎年違う絵柄で作られるそうだ"),
        ("小さな船に乗って向こう岸へ渡った", "船頭は川の流れに詳しい人だった"),
        ("遠くの塔の鐘を三回聞いた", "鐘は日没を知らせるもので危険の合図ではない"),
        ("旅帳に今日の出会いを短く書き足した", "旅帳の記述は物語だが進行記録の代わりにはならない"),
        ("またいつか同じ道を歩こうと思った", "道は季節によって違う景色を見せてくれる"),
        ("最後に掲示板の前を通ったが表示は読まなかった", "依頼の達成状況は会話だけでは分からない"),
    ]
)

# Each pair changes the decisive fact or request, not merely the wording.
# Histories are fictional and intentionally do not refer to real players.
SCENES = [
    {
        "id": "weather",
        "history": "プレイヤー: 今夜のお祭りは何時？\nNPC: ゲーム内では鐘が三回鳴る頃です。\nプレイヤー: 了解。外の予定も立てたい。",
        "variants": [
            ("ゲーム状態: 雨の演出は固定ではなくサーバーごとに変わる。", "このゲームの今の天候を教えて。", "game_state"),
            ("ゲーム状態: 現実の天気データはゲーム内に保存されていない。", "現実の宮崎市の今日の天気を教えて。", "web"),
        ],
        "choices": ["talk", "web", "game_state", "screenshot", "quest_log"],
    },
    {
        "id": "map",
        "history": "プレイヤー: 東門の近くにいる。\nNPC: 地図に印はつけておきました。\nプレイヤー: いま出口が見当たらない。",
        "variants": [
            ("ゲーム状態: 現在地と閉鎖中の通路は経路探索APIで取得できる。", "ここから鍛冶屋まで、通れる道で案内して。", "pathfind"),
            ("ゲーム状態: プレイヤーは古地図の凡例について聞いている。現在地は関係しない。", "地図に描かれた青い鳥の印は、物語上どういう意味？", "talk"),
        ],
        "choices": ["talk", "web", "pathfind", "game_state", "screenshot"],
    },
    {
        "id": "quest",
        "history": "プレイヤー: 依頼の木箱を運んだよ。\nNPC: ありがとう。掲示板で受領されるまで報酬は確定しません。\nプレイヤー: 受領されたか覚えていない。",
        "variants": [
            ("ゲーム状態: クエストの最新記録はNPCの会話履歴に含まれない。", "この依頼、もう達成扱いになってる？", "quest_log"),
            ("ゲーム状態: 一般的なクエストの説明はNPCの設定に記載済み。", "木箱運びの依頼って、どういう話だったっけ？", "talk"),
        ],
        "choices": ["talk", "quest_log", "game_state", "web", "command"],
    },
    {
        "id": "inventory",
        "history": "プレイヤー: 薬草を拾ったはず。\nNPC: 所持品を開くと残数が見えます。\nプレイヤー: 戦闘中でメニューを開けない。",
        "variants": [
            ("ゲーム状態: 所持数は戦闘中に変化する。NPCに現在値は渡されていない。", "いま薬草を何個持っている？", "game_state"),
            ("ゲーム状態: 薬草の用途はNPCの知識に含まれる。", "薬草はどんなときに使うといい？", "talk"),
        ],
        "choices": ["talk", "game_state", "quest_log", "screenshot", "web"],
    },
    {
        "id": "attachment",
        "history": "プレイヤー: 古い紋章を見つけた。\nNPC: 形が分かれば由来を絞れるよ。\nプレイヤー: 見せてみるね。",
        "variants": [
            ("添付: プレイヤーが紋章の画像をこの発言に添付した。画像内容はテキストには記載されていない。", "この画像の紋章に何が描かれているか見て。", "image_analyze"),
            ("添付: なし。紋章の画像はまだ共有されていない。", "紋章の画像を送る前に、見分け方だけ教えて。", "talk"),
        ],
        "choices": ["talk", "image_analyze", "screenshot", "image_create", "web"],
    },
    {
        "id": "screenshot",
        "history": "プレイヤー: 画面右上の印が読みにくい。\nNPC: 私には今の画面が自動では見えていないよ。\nプレイヤー: じゃあ確認してみて。",
        "variants": [
            ("権限: ゲーム画面の取得が許可されている。画像添付はまだない。", "今の画面を撮って、印の位置を確認して。", "screenshot"),
            ("権限: 画像添付あり。すでに取得済みのスクリーンショットがこの発言に付いている。", "この添付スクリーンショットの印を読んで。", "image_analyze"),
        ],
        "choices": ["talk", "screenshot", "image_analyze", "game_state", "image_create"],
    },
    {
        "id": "portrait",
        "history": "プレイヤー: ギルドの仲間に紹介状を渡したい。\nNPC: 紹介状の文章なら一緒に考えられるよ。\nプレイヤー: いいね。",
        "variants": [
            ("素材: 架空の人物だけを扱う。既存画像の添付はない。", "私の新しいキャラクターの立ち絵を一枚描いて。", "image_create"),
            ("素材: 画像は不要。紹介状に書く文章だけを求めている。", "そのキャラクターの自己紹介文を短く考えて。", "talk"),
        ],
        "choices": ["talk", "image_create", "video_create", "image_analyze", "web"],
    },
    {
        "id": "cutscene",
        "history": "プレイヤー: 竜が橋を渡る場面が好き。\nNPC: 記念に場面を残してみようか。\nプレイヤー: どんな形がいいかな。",
        "variants": [
            ("制作条件: 架空の竜。動きと時間経過が必要な表現。", "竜が橋を飛び越える5秒の動画を作って。", "video_create"),
            ("制作条件: 動きは不要。一枚の静止画がほしい。", "竜が橋を飛び越える瞬間のイラストを描いて。", "image_create"),
        ],
        "choices": ["talk", "image_create", "video_create", "screenshot", "web"],
    },
    {
        "id": "developer",
        "history": "プレイヤー: 私はこのテスト環境の開発者です。\nNPC: 実行権限のある作業だけ対応できます。\nプレイヤー: 手順を確認したい。",
        "variants": [
            ("環境: ローカルのテスト用サンドボックス。読み取り専用コマンドの実行が許可されている。", "テスト用ディレクトリのファイル一覧をコマンドで表示して。", "command"),
            ("環境: コマンド実行は要求されていない。説明だけでよい。", "ファイル一覧を表示する一般的なコマンド名を教えて。", "talk"),
        ],
        "choices": ["talk", "command", "web", "game_state", "quest_log"],
    },
    {
        "id": "recency",
        "history": "プレイヤー: 本物のニュースをゲーム内の台詞と混ぜないでね。\nNPC: 分かった。現実の情報は確認してから話すよ。\nプレイヤー: 明日旅に出るつもり。",
        "variants": [
            ("情報源: 現実世界のイベント日程はNPCの設定には存在しない。", "今年の近くの花火大会の開催日を調べて。", "web"),
            ("情報源: ゲーム内の祭りの日程は会話設定にある。祭りは次の満月の夜。", "この世界のお祭りはいつ？", "talk"),
        ],
        "choices": ["talk", "web", "game_state", "quest_log", "pathfind"],
    },
    {
        "id": "multiturn_switch",
        "history": "プレイヤー: こんばんは。\nNPC: こんばんは、何か手伝える？\nプレイヤー: 今日は疲れた。\nNPC: それは大変だったね。少し休もうか。\nプレイヤー: ところで次の相談をしていい？\nNPC: もちろん。",
        "variants": [
            ("状態: 最新の質問は現実の最新情報を必要とする。", "今夜の現実の交通機関の運行状況を検索して。", "web"),
            ("状態: 最新の質問は共感を求めるだけで、情報照会は不要。", "ありがとう。少し話を聞いてくれる？", "talk"),
        ],
        "choices": ["talk", "web", "game_state", "image_create", "command"],
    },
    {
        "id": "state_vs_visual",
        "history": "プレイヤー: 宝箱が開かない。\nNPC: 鍵の所持と画面上の仕掛けは別の情報だよ。\nプレイヤー: どちらを確認すればいい？",
        "variants": [
            ("状態: 鍵の有無は所持品APIで分かる。画面画像はない。", "開錠の鍵をいま所持しているか確認して。", "game_state"),
            ("状態: 宝箱の仕掛けは画像にしか表示されない。現在画面取得が許可されている。画像添付はない。", "画面に出ている仕掛けを確認するため、今の画面を撮って。", "screenshot"),
        ],
        "choices": ["talk", "game_state", "screenshot", "image_analyze", "quest_log"],
    },
    {
        "id": "long_history",
        "history": LONG_HISTORY,
        "variants": [
            ("現在: プレイヤーは掲示板の橋修理依頼を受けた。最新の進行状態は会話に含まれない。", "さっき受けた橋修理の依頼は、いま達成済みになった？", "quest_log"),
            ("現在: プレイヤーは日記の文面を整えたい。最新の進行状態は不要。", "今の旅の思い出を二文で優しくまとめてくれる？", "talk"),
        ],
        "choices": ["talk", "quest_log", "game_state", "web", "pathfind", "command"],
    },
]


def make_record(scene: dict, world: tuple, variant_index: int) -> dict:
    world_id, split, place, npc = world
    state, question, target = scene["variants"][variant_index]
    action_ids = list(scene["choices"])
    # Keep ID/text correspondence while rotating positions by world and variant.
    shift = (WORLDS.index(world) * 2 + variant_index) % len(action_ids)
    action_ids = action_ids[shift:] + action_ids[:shift]
    return {
        "id": f"npcv1_{world_id}_{scene['id']}_{variant_index}",
        "group_id": f"npcv1_{world_id}_{scene['id']}",
        "split": split,
        "family": "npc_multiturn_tool_routing",
        "subcategory": scene["id"],
        "language": "ja",
        "context": f"【舞台】{place}。NPCは{npc}。\n【これまでの会話】\n{scene['history']}\n【現在の状況】{state}",
        "question": f"プレイヤー（最新発言）: {question}\nNPCが次に取るべき行動を一つ選んでください。",
        "choices": [{"id": action_id, "text": ACTIONS[action_id]} for action_id in action_ids],
        "target": {"kind": "hard", "choice_id": target},
        "source_type": "original_synthetic_local",
        "review_status": "provisional_unreviewed",
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    splits = {"train": [], "dev": [], "eval": []}
    for world in WORLDS:
        for scene in SCENES:
            for variant_index in range(2):
                splits[world[1]].append(make_record(scene, world, variant_index))

    seen_ids: set[str] = set()
    seen_groups: dict[str, str] = {}
    for split, rows in splits.items():
        for row in rows:
            assert row["id"] not in seen_ids
            seen_ids.add(row["id"])
            group_id = row["group_id"]
            assert seen_groups.setdefault(group_id, split) == split
            choice_ids = [choice["id"] for choice in row["choices"]]
            assert 2 <= len(choice_ids) <= 16 and len(choice_ids) == len(set(choice_ids))
            assert row["target"]["choice_id"] in choice_ids
    assert all(sum(row["group_id"] == group for row in rows) == 2 for rows in splits.values() for group in {row["group_id"] for row in rows})

    manifest = {
        "status": "synthetic_provisional_not_human_gold",
        "provenance": "Locally authored deterministic templates; no API, private transcript, or existing game dialogue.",
        "split_policy": "world-disjoint; paired opposite states remain in one group/split; scene templates recur across worlds",
        "worlds": {world_id: split for world_id, split, _, _ in WORLDS},
        "splits": {},
        "action_counts": {},
        "limitations": ["Template overlap across splits; not an independent real-world benchmark.", "Labels are author-provisional, not human-reviewed gold."],
    }
    for split, rows in splits.items():
        path = OUT / f"{split}.jsonl"
        data = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
        path.write_text(data, encoding="utf-8")
        manifest["splits"][split] = {
            "records": len(rows),
            "groups": len({row["group_id"] for row in rows}),
            "sha256": hashlib.sha256(data.encode("utf-8")).hexdigest(),
            "max_context_characters": max(len(row["context"]) for row in rows),
        }
        manifest["action_counts"][split] = dict(Counter(row["target"]["choice_id"] for row in rows))
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
