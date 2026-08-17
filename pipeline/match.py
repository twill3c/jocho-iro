"""selection.tsv と青空文庫索引 CSV の照合(SPEC F-01)。

- 著者 = 姓+名 連結、題 = 作品名(空白除去・字体ゆれ正規化)で照合
- 同一(著者, 題)に複数カードがある場合は 文字遣い種別 の優先度
  (新字新仮名 > 新字旧仮名 > 旧字新仮名 > 旧字旧仮名)で 1 件選ぶ
- 完全一致がなければ「題で始まる作品」の一意候補を採用(副題つきカード対応)
- 結果: data/catalog.json + data/match_report.md
"""

from __future__ import annotations

import csv
import json
import unicodedata

from .paths import CATALOG, INDEX_CACHE, MATCH_REPORT, SELECTION

KANA_PRIORITY = {"新字新仮名": 0, "新字旧仮名": 1, "旧字新仮名": 2, "旧字旧仮名": 3}
# 字体・記号ゆれの正規化(照合専用。本文には触れない)
CHAR_MAP = str.maketrans({"燈": "灯", "瀧": "滝", "藪": "薮", "萠": "萌", "彌": "弥", "龍": "竜"})


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = s.replace(" ", "").replace("　", "")
    s = s.replace("『", "").replace("』", "").replace("「", "").replace("」", "")
    s = s.replace("ゝ", "").replace("ゞ", "")  # 踊り字は比較から除外(あゝ/ああ ゆれ)
    s = s.replace("ああ", "あ")  # ゝ 除外側と揃える(あゝ→あ / ああ→あ)
    return s.translate(CHAR_MAP)


def load_selection() -> list[dict]:
    rows = []
    for line in SELECTION.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        kind, author, title, category = line.split("\t")
        rows.append({"kind": kind, "author": author, "title": title, "category": category})
    return rows


def load_index() -> list[dict]:
    csv_path = next(INDEX_CACHE.glob("*.csv"))
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        return [r for r in csv.DictReader(f)]


def main() -> None:
    selection = load_selection()
    index = load_index()

    # (著者norm, 題norm) → カード候補列
    by_key: dict[tuple[str, str], list[dict]] = {}
    by_author: dict[str, list[dict]] = {}
    for r in index:
        if r.get("役割フラグ") != "著者":
            continue
        if not r.get("テキストファイルURL"):
            continue
        author = norm(r["姓"] + r["名"])
        title = norm(r["作品名"])
        by_key.setdefault((author, title), []).append(r)
        by_author.setdefault(author, []).append(r)

    def pick(cands: list[dict]) -> dict:
        return sorted(cands, key=lambda r: (KANA_PRIORITY.get(r.get("文字遣い種別", ""), 9), r["作品ID"]))[0]

    catalog, misses, fuzzy_notes = [], [], []
    for sel in selection:
        a, t = norm(sel["author"]), norm(sel["title"])
        cands = by_key.get((a, t), [])
        how = "exact"
        if not cands:
            # 前方一致(副題つきカード)
            starts = [r for r in by_author.get(a, []) if norm(r["作品名"]).startswith(t)]
            uniq_titles = {norm(r["作品名"]) for r in starts}
            if len(uniq_titles) == 1 and starts:
                cands, how = starts, "prefix"
                fuzzy_notes.append(f"- {sel['author']}『{sel['title']}』 → 前方一致『{starts[0]['作品名']}』")
        if not cands:
            misses.append(sel)
            continue
        r = pick(cands)
        catalog.append({
            **sel,
            "work_id": r["作品ID"],
            "aozora_title": r["作品名"],
            "aozora_author": f"{r['姓']} {r['名']}",
            "kana_type": r.get("文字遣い種別", ""),
            "card_url": r.get("図書カードURL", ""),
            "text_url": r["テキストファイルURL"],
            "teihon_1": r.get("底本名1", ""),
            "match": how,
        })

    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=1), encoding="utf-8")

    n_main = sum(1 for c in catalog if c["kind"] == "main")
    n_pool = sum(1 for c in catalog if c["kind"] == "pool")
    lines = [
        "# 照合レポート(pipeline.match)",
        "",
        f"- 照合成立: main {n_main} / pool {n_pool}(計 {len(catalog)})",
        f"- 照合不能: {len(misses)}",
        "",
    ]
    if misses:
        lines.append("## 照合不能(要対応: 表記修正 or プール補充)")
        lines += [f"- {m['kind']}: {m['author']}『{m['title']}』" for m in misses]
        lines.append("")
    if fuzzy_notes:
        lines.append("## 前方一致で解決(確認推奨)")
        lines += fuzzy_notes
    MATCH_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:8]))
    print(f"→ {CATALOG}")


if __name__ == "__main__":
    main()
