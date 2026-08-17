"""gold 生成(SPEC F-06): 選出 300 を web/public/data へ出力。

- works/{id}.json: 行(t, p, h[表層, 極性, カテゴリ, 否定])+ river(64 区間 × 8 情緒)
- index.json: メタ + リフト/エントロピー/支配/ヒット率 + ribbon(64 区間の [支配情緒番号, 強度])
"""

from __future__ import annotations

import json

from .jocho import CATEGORIES, river
from .paths import DATA, LINES_DIR, ROOT

MANIFEST = DATA / "corpus_manifest.json"
HITS_DIR = DATA / "hits"
OUT_DIR = ROOT / "web" / "public" / "data"
BINS = 64


def ribbon_of(rv: dict) -> list[list]:
    """区間ごとの [支配情緒番号, 強度 0..1]。全情緒 0 の区間は [-1, 0]。
    強度 = 区間合計強度を作品内最大で正規化。"""
    totals = [sum(rv[c][b] for c in CATEGORIES) for b in range(BINS)]
    peak = max(totals) if totals and max(totals) > 0 else 1.0
    out = []
    for b in range(BINS):
        if totals[b] <= 0:
            out.append([-1, 0.0])
            continue
        best = max(range(len(CATEGORIES)), key=lambda i: (rv[CATEGORIES[i]][b], -i))
        out.append([best, round(totals[b] / peak, 3)])
    return out


def main() -> None:
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    (OUT_DIR / "works").mkdir(parents=True, exist_ok=True)
    index_entries = []
    for i, w in enumerate(m["works"], 1):
        lines = json.loads((LINES_DIR / f"{w['id']}.json").read_text(encoding="utf-8"))
        scored = json.loads((HITS_DIR / f"{w['id']}.json").read_text(encoding="utf-8"))
        hits_pos = [(h[2], li) for li, s in enumerate(scored) for h in s["h"] if not h[3]]
        rv = river(hits_pos, n_lines=len(lines), bins=BINS)
        rv_round = {c: [round(v, 3) for v in rv[c]] for c in CATEGORIES}
        (OUT_DIR / "works" / f"{w['id']}.json").write_text(json.dumps({
            "id": w["id"], "author": w["author"], "title": w["title"],
            "category": w["category"], "kana_type": w["kana_type"],
            "card_url": w["card_url"], "teihon": w["teihon"],
            "dict_version": m["dict_version"],
            "lifts": w["lifts"], "entropy": w["entropy"], "dominant": w["dominant"],
            "river": rv_round,
            "lines": [{"t": t, "p": s["p"], "h": s["h"]} for t, s in zip(lines, scored)],
        }, ensure_ascii=False), encoding="utf-8")
        index_entries.append({
            **{k: w[k] for k in ("id", "author", "title", "category", "kana_type",
                                  "chars", "n_lines", "hitrate", "total_hits",
                                  "lifts", "entropy", "dominant")},
            "ribbon": ribbon_of(rv),
        })
        if i % 60 == 0:
            print(f"{i}/300")
    (OUT_DIR / "index.json").write_text(json.dumps({
        "dict_version": m["dict_version"],
        "baseline": m["baseline"],
        "categories": CATEGORIES,
        "n_works": len(index_entries),
        "works": index_entries,
    }, ensure_ascii=False), encoding="utf-8")
    print(f"→ {OUT_DIR}")


if __name__ == "__main__":
    main()
