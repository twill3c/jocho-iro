# T-020 / T-021: 行スコアリングの厳密検証(SPEC F-05 / G-03)
# ミニ辞書 + 手書きの行。期待値は規則(ヒット平均・否定窓 2 形態素・中立 0)から手計算。
from pipeline.score import Scorer

MINI_DICT = {
    "version": "test",
    "entries": [
        {"w": "嬉しい", "p": 0.7, "c": "joy"},
        {"w": "悲しい", "p": -0.7, "c": "sadness"},
        {"w": "地獄", "p": -1.0, "c": "fear"},
    ],
}

EPS = 1e-9


def make() -> Scorer:
    return Scorer(MINI_DICT)


def test_t020_simple_hit():
    s = make().score_line("今日は嬉しい。")
    assert abs(s["p"] - 0.7) < EPS
    assert [h[0] for h in s["h"]] == ["嬉しく"] or [h[0] for h in s["h"]] == ["嬉しい"]


def test_t020_negation_flips():
    # 「嬉しくない」→ 直後 2 形態素以内の「ない」で反転
    s = make().score_line("嬉しくない。")
    assert abs(s["p"] - (-0.7)) < EPS


def test_t021_negation_at_distance_two():
    # 悲しく / は / ない → 距離 2 で反転(+0.7)
    s = make().score_line("悲しくはない。")
    assert abs(s["p"] - 0.7) < EPS


def test_t021_negation_out_of_window():
    # 嬉しい / こと / が / 何 / も / ない → 距離 > 2 は反転しない
    s = make().score_line("嬉しいことが何もない。")
    assert abs(s["p"] - 0.7) < EPS


def test_t020_mixed_average():
    # (+0.7 − 0.7) / 2 = 0
    s = make().score_line("嬉しくて悲しい。")
    assert abs(s["p"] - 0.0) < EPS
    assert len(s["h"]) == 2


def test_t020_neutral_zero():
    s = make().score_line("何の変哲もない朝。")
    assert s["p"] == 0.0
    assert s["h"] == []


def test_t020_noun_hit():
    s = make().score_line("そこは地獄であった。")
    assert abs(s["p"] - (-1.0)) < EPS
