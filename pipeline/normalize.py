"""青空文庫テキストの正規化(SPEC F-02)。

規則(除去以外の文字は一切改変しない — 逐語性 G-01):
- 先頭: 1 行目 = 題、2 行目 = 著者(そのまま meta へ)。以後の空行を読み飛ばす
- 記号説明ブロック: 50 個以上のハイフンだけの行で挟まれた区画があれば丸ごと除去
- フッタ: 「底本:」または「底本:」で始まる最初の行以降を除去(meta.teihon に保持)
- ルビ《…》・ルビ起点 ｜/| ・入力者注 [#…](直前の外字マーク ※ は保持)を除去
- 本文先頭・末尾の空行を除去(行内の空白は保存)
"""

from __future__ import annotations

import re

RUBY_RE = re.compile(r"《[^》]*》")
NOTE_RE = re.compile(r"\[#[^\]]*\]")
BAR_RE = re.compile(r"[|｜]")
HR_RE = re.compile(r"^-{50,}\s*$")
TEIHON_RE = re.compile(r"^底本[::]")


def normalize_text(raw: str) -> tuple[str, dict]:
    lines = raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    meta: dict = {"title_line": "", "author_line": "", "teihon": ""}

    i = 0
    if i < len(lines):
        meta["title_line"] = lines[i].strip()
        i += 1
    if i < len(lines):
        meta["author_line"] = lines[i].strip()
        i += 1
    while i < len(lines) and lines[i].strip() == "":
        i += 1

    # 記号説明ブロック(あれば)
    if i < len(lines) and HR_RE.match(lines[i]):
        i += 1
        while i < len(lines) and not HR_RE.match(lines[i]):
            i += 1
        i += 1  # 閉じ罫線

    body_lines: list[str] = []
    footer_lines: list[str] = []
    in_footer = False
    for line in lines[i:]:
        if not in_footer and TEIHON_RE.match(line.strip()):
            in_footer = True
        if in_footer:
            footer_lines.append(line)
        else:
            body_lines.append(line)

    text = "\n".join(body_lines)
    text = NOTE_RE.sub("", text)
    text = RUBY_RE.sub("", text)
    text = BAR_RE.sub("", text)
    text = text.strip("\n")
    # 末尾に残る空白だけの行を落とす(先頭は strip("\n") 済み)
    out_lines = text.split("\n")
    while out_lines and out_lines[-1].strip() == "":
        out_lines.pop()
    while out_lines and out_lines[0].strip() == "":
        out_lines.pop(0)
    text = "\n".join(out_lines)

    for fl in footer_lines:
        if TEIHON_RE.match(fl.strip()):
            meta["teihon"] = fl.strip()
            break
    return text, meta
