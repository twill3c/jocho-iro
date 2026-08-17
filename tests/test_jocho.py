# T-060 / T-070 / T-071: 情緒数理(SPEC F-03 / F-04 / F-05)
# 期待値は SPEC の定義から手計算(実装からの転記ではない)。
import math

from pipeline.jocho import entropy, lifts, river, shares
from pipeline.score import Scorer

EPS = 1e-9

MINI_DICT = {
    "version": "test",
    "entries": [
        {"w": "嬉しい", "p": 0.7, "c": "joy"},
        {"w": "悲しい", "p": -0.7, "c": "sadness"},
    ],
}


def test_t060_negated_hit_excluded_from_emotion():
    s = Scorer(MINI_DICT).score_line("嬉しくない。")
    # 極性は反転して負(kokoro と同一)…
    assert s["p"] < 0
    # …だが情緒集計では否定フラグ付きヒットを除外できる(第 4 要素 = negated)
    assert s["h"][0][3] == 1
    active = [h for h in s["h"] if not h[3]]
    assert active == []


def test_t070_shares_and_entropy():
    counts = {"joy": 2, "sadness": 2, "fear": 0, "anger": 0,
              "like": 0, "surprise": 0, "dislike": 0, "calm": 0}
    sh = shares(counts)
    assert abs(sh["joy"] - 0.5) < EPS and abs(sh["sadness"] - 0.5) < EPS
    assert abs(entropy(sh) - 1.0) < EPS  # 2 等分 → H = 1 bit
    # 単色 → H = 0
    assert entropy(shares({"joy": 5})) == 0.0
    # 8 等分 → H = 3
    even = shares({c: 1 for c in ["joy", "anger", "sadness", "fear", "like", "surprise", "dislike", "calm"]})
    assert abs(entropy(even) - 3.0) < EPS
    # ヒット 0 → 全シェア 0・H = 0
    assert entropy(shares({})) == 0.0


def test_t070_lifts():
    work = {"joy": 3, "sadness": 1}
    base = {"joy": 0.25, "sadness": 0.5, "fear": 0.25}
    lf = lifts(shares(work), base)
    # joy: シェア 0.75 / 基準 0.25 = 3.0、sadness: 0.25 / 0.5 = 0.5
    assert abs(lf["joy"] - 3.0) < EPS
    assert abs(lf["sadness"] - 0.5) < EPS
    # 基準 0 の情緒はリフト 0(縁は正常系)
    assert lf.get("anger", 0.0) == 0.0


def test_t071_river_windowing():
    # 8 区間・joy のヒット位置 [0,0,0,0,1,0,0,0](区間 4 に 1 件)を半径 2 で平滑化:
    # 区間 2: 窓 [0..4] → 1/5、区間 4: 窓 [2..6] → 1/5、区間 7: 窓 [5..7] → 0/3
    hits = [("joy", 4)]
    rv = river(hits, n_lines=8, bins=8)
    joy = rv["joy"]
    assert len(joy) == 8
    assert abs(joy[2] - 1 / 5) < EPS
    assert abs(joy[4] - 1 / 5) < EPS
    assert joy[0] == 0.0  # 窓 [0..2] にヒットなし
    assert joy[7] == 0.0  # 窓 [5..7] にヒットなし


def test_t071_river_empty():
    rv = river([], n_lines=0, bins=8)
    assert all(len(v) == 8 and all(x == 0.0 for x in v) for v in rv.values())
