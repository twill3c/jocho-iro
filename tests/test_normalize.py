# T-001 / T-002: 正規化の逐語性(SPEC F-02 / G-01)
# 期待値は青空文庫の実ファイル構造の縮小版から手書きした(実装からの転記ではない)。
from pipeline.normalize import normalize_text

RAW = """タイトル作
著者名前

-------------------------------------------------------
【テキスト中に現れる記号について】

《》:ルビ
(例)朝《あさ》
-------------------------------------------------------

 朝《あさ》の光《ひかり》が差した。
彼は※[#「口+它」、第3水準1-14-88]と叫んだ。
「行くのか」と、|老人《ろうじん》は言った。
[#8字下げ]一[#「一」は中見出し]
それだけの話である。

底本:「なんとか全集」なんとか文庫、なんとか書房
   1950(昭和25)年発行
入力:someone
"""

# 注記 [#…] のみ除去され、見出しの地の文字「一」は残る(逐語性)
EXPECTED_BODY = """ 朝の光が差した。
彼は※と叫んだ。
「行くのか」と、老人は言った。
一
それだけの話である。"""


def test_t001_normalize_structure():
    body, meta = normalize_text(RAW)
    assert body == EXPECTED_BODY
    assert meta["title_line"] == "タイトル作"
    assert meta["author_line"] == "著者名前"
    assert meta["teihon"].startswith("底本:「なんとか全集」")


def test_t001_no_symbol_block_variant():
    # 記号説明ブロックがないファイル(初期の入力ファイルに存在する)
    raw = "題\n著者\n\n本文である。\n\n底本:「X」Y\n"
    body, meta = normalize_text(raw)
    assert body == "本文である。"
    assert meta["teihon"] == "底本:「X」Y"


def test_t002_verbatim_no_mutation():
    # 除去(ルビ・注記・区切り)以外の文字を一切改変しない:
    # 期待本文はソース中に除去対象を挿入し直せば元に戻る関係にある。
    body, _ = normalize_text(RAW)
    assert "《" not in body and "》" not in body
    assert "[#" not in body
    assert "|" not in body and "｜" not in body
    # 地の文はそのまま(空白・読点も保存)
    assert "「行くのか」と、老人は言った。" in body
