# T-010: 行(文)分割の決定論(SPEC F-03 / G-02)
from pipeline.split import split_sentences


def test_t010_basic():
    assert split_sentences("春が来た。鳥が鳴く。") == ["春が来た。", "鳥が鳴く。"]


def test_t010_closing_quote_attaches():
    text = "「もう行くのか。」彼は言った。「ああ。」"
    assert split_sentences(text) == ["「もう行くのか。」", "彼は言った。", "「ああ。」"]


def test_t010_exclaim_question():
    assert split_sentences("なぜだ!知らない?そうか。") == ["なぜだ!", "知らない?", "そうか。"]


def test_t010_paragraph_always_boundary():
    text = "終わりのない行\nつぎの段落。"
    assert split_sentences(text) == ["終わりのない行", "つぎの段落。"]


def test_t010_empty_and_whitespace_dropped():
    # 句点のみの断片も 1 文字あるので文として残る。空白のみの行は捨てる
    text = "。。\n\n 本文。\n　\n"
    assert split_sentences(text) == ["。", "。", "本文。"]


def test_t010_leading_fullwidth_space_stripped():
    assert split_sentences("　朝が来た。") == ["朝が来た。"]


def test_t010_double_closer():
    # 閉じ括弧(」』)は連続していても全て前の文に付く
    assert split_sentences("『声。』」と読んだ。") == ["『声。』」", "と読んだ。"]
