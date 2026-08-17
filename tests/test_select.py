# T-080: 選定規則 F-02 の決定論(SPEC G-01)
# ミニ母集団 12 作。期待値は F-02 の ①〜⑤ を手で順に適用して導いた。
from pipeline.select300 import select_works

CATS = ["joy", "anger", "sadness", "fear", "like", "surprise", "dislike", "calm"]


def mk(id_, author, hitrate, chars, dominant, dom_lift, ent, total_hits=100):
    return {
        "id": id_, "author": author, "title": f"作{id_}", "category": "x",
        "hitrate": hitrate, "chars": chars, "dominant": dominant, "total_hits": total_hits,
        "lifts": {c: (dom_lift if c == dominant else 0.5) for c in CATS},
        "entropy": ent,
    }


def test_t080_rules_in_order():
    pop = [
        mk("01", "A", 0.30, 1000, "joy", 3.0, 1.0),
        mk("02", "A", 0.30, 1000, "joy", 9.9, 3.0, total_hits=29),  # ① 総ヒット 29 → 落選
        mk("03", "A", 0.30, 300000, "joy", 9.9, 3.0), # ② 字数超過 → 落選
        mk("04", "B", 0.30, 1000, "anger", 2.0, 0.5),
        mk("05", "B", 0.30, 1000, "anger", 1.5, 0.4),
        mk("06", "C", 0.30, 1000, "sadness", 2.5, 2.0),
        mk("07", "C", 0.30, 1000, "fear", 2.2, 1.5),
        mk("08", "D", 0.30, 1000, "like", 2.1, 0.3),
        mk("09", "D", 0.30, 1000, "surprise", 1.8, 0.2),
        mk("10", "E", 0.30, 1000, "dislike", 1.7, 0.1),
        mk("11", "E", 0.30, 1000, "calm", 1.6, 2.5),
        mk("12", "F", 0.30, 1000, "calm", 1.2, 2.9),
    ]
    # 定員 10・情緒ごとの確保 1・作者上限 2
    pop.append(mk("13", "G", 0.07, 1000, "calm", 1.0, 0.5))  # ① 行率 0.07 → 落選
    result = select_works(pop, target=10, per_emotion=1, author_cap=2,
                          min_hits=30, min_hitrate=0.08, max_chars=200_000)
    ids = [w["id"] for w in result["works"]]
    # ① で 02(少ヒット)と 13(低行率)、② で 03 が落選 → 残 10 がちょうど定員
    assert sorted(ids) == ["01", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    # 除外理由が記録される
    reasons = {e["id"]: e["reason"] for e in result["excluded"]}
    assert reasons["02"] == "few_hits"
    assert reasons["03"] == "over_length"
    assert reasons["13"] == "low_hitrate"


def test_t080_author_cap_and_entropy_fill():
    pop = [
        mk("01", "A", 0.3, 1000, "joy", 5.0, 0.9),
        mk("02", "A", 0.3, 1000, "joy", 4.0, 0.8),
        mk("03", "A", 0.3, 1000, "joy", 3.0, 3.0),   # 作者上限 2 で落ちる(確保後の残枠補充時)
        mk("04", "B", 0.3, 1000, "sadness", 2.0, 0.1),
        mk("05", "C", 0.3, 1000, "sadness", 1.0, 2.0),
        mk("06", "D", 0.3, 1000, "calm", 1.0, 1.0),
    ]
    result = select_works(pop, target=5, per_emotion=1, author_cap=2, min_hits=30, min_hitrate=0.08, max_chars=200_000)
    ids = [w["id"] for w in result["works"]]
    # 確保: joy 代表 = 01(リフト最大)・sadness 代表 = 04(リフト最大)・calm 代表 = 06
    # 残枠 2: エントロピー降順で 03(A の 2 作目・上限内)→ 05 を採用して定員
    assert "01" in ids and "04" in ids and "06" in ids
    assert "03" in ids and "05" in ids
    assert "02" not in ids  # 作者上限 2(01, 03)で入れない


def test_t080_deterministic():
    pop = [mk(f"{i:02d}", f"X{i}", 0.3, 1000, "joy", 1.0, 1.0) for i in range(1, 7)]
    r1 = select_works(pop, target=4, per_emotion=0, author_cap=26, min_hits=30, min_hitrate=0.08, max_chars=200_000)
    r2 = select_works(list(reversed(pop)), target=4, per_emotion=0, author_cap=26, min_hits=30, min_hitrate=0.08, max_chars=200_000)
    assert [w["id"] for w in r1["works"]] == [w["id"] for w in r2["works"]]
