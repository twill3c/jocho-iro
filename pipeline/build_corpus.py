"""評価母集団の正規化・分割・計測(SPEC F-01)。300 の絞り込みは select300 が行う。"""

from __future__ import annotations

import json

from .normalize import normalize_text
from .paths import BRONZE, CATALOG, LINES_DIR
from .split import split_sentences

EVAL = CATALOG.parent / "eval_manifest.json"


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    LINES_DIR.mkdir(parents=True, exist_ok=True)
    works, missing = [], []
    for c in catalog:
        path = BRONZE / f"{c['work_id']}.txt"
        if not path.exists():
            missing.append(f"{c['author']}『{c['title']}』")
            continue
        body, meta = normalize_text(path.read_text(encoding="utf-8"))
        lines = split_sentences(body)
        (LINES_DIR / f"{c['work_id']}.json").write_text(
            json.dumps(lines, ensure_ascii=False), encoding="utf-8")
        works.append({
            "id": c["work_id"], "author": c["author"], "title": c["title"],
            "category": c["category"], "kana_type": c["kana_type"],
            "card_url": c["card_url"], "teihon": meta["teihon"] or c.get("teihon_1", ""),
            "chars": sum(len(s) for s in lines), "n_lines": len(lines),
        })
    EVAL.write_text(json.dumps({"works": works, "missing": missing},
                               ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"評価母集団 {len(works)} 作品 / bronze 欠落 {len(missing)}")
    for m in missing:
        print(f"- 欠落: {m}")


if __name__ == "__main__":
    main()
