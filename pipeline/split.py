"""行(文)分割(SPEC F-03)。

規則:
- 段落(改行)境界は常に文境界
- 「。」「!」「?」(全角)の直後で分割。直後に閉じ括弧 」』 が続く場合は
  連続する分だけ前の文に含める
- 各文の先頭・末尾の空白(全角含む)を除去し、空になった文は捨てる
"""

from __future__ import annotations

TERMINATORS = {"。", "!", "?"}
CLOSERS = {"」", "』"}
WS = " \t　"


def _split_paragraph(par: str) -> list[str]:
    out: list[str] = []
    buf: list[str] = []
    i = 0
    n = len(par)
    while i < n:
        ch = par[i]
        buf.append(ch)
        if ch in TERMINATORS:
            j = i + 1
            while j < n and par[j] in CLOSERS:
                buf.append(par[j])
                j += 1
            out.append("".join(buf))
            buf = []
            i = j
        else:
            i += 1
    if buf:
        out.append("".join(buf))
    return out


def split_sentences(text: str) -> list[str]:
    sentences: list[str] = []
    for par in text.split("\n"):
        for s in _split_paragraph(par):
            s = s.strip(WS)
            if s:
                sentences.append(s)
    return sentences
