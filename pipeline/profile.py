"""全候補の情緒プロファイル採点(SPEC F-03)。

- ヒットは否定フラグ付きを除外して集計(F-05)
- 基準シェア b_e は評価母集団全体のヒット総計から算出し、manifest に記録
"""

from __future__ import annotations

import json

from .jocho import CATEGORIES, dominant, entropy, lifts, shares
from .paths import DATA, LINES_DIR, ROOT
from .score import Scorer

EVAL = DATA / "eval_manifest.json"
PROFILES = DATA / "profiles.json"
HITS_DIR = DATA / "hits"
DICT_PATH = ROOT / "dict" / "kokoro_dict.json"


def main() -> None:
    dictionary = json.loads(DICT_PATH.read_text(encoding="utf-8"))
    scorer = Scorer(dictionary)
    ev = json.loads(EVAL.read_text(encoding="utf-8"))
    HITS_DIR.mkdir(parents=True, exist_ok=True)

    per_work = []
    total_counts = {c: 0 for c in CATEGORIES}
    for i, w in enumerate(ev["works"], 1):
        lines = json.loads((LINES_DIR / f"{w['id']}.json").read_text(encoding="utf-8"))
        scored = [scorer.score_line(s) for s in lines]
        counts = {c: 0 for c in CATEGORIES}
        hit_lines = 0
        for s in scored:
            active = [h for h in s["h"] if not h[3]]  # 否定除外(F-05)
            if s["h"]:
                hit_lines += 1
            for h in active:
                counts[h[2]] += 1
                total_counts[h[2]] += 1
        # 行ごとのスコア・ヒットは gold 生成でも使うため中間保存
        (HITS_DIR / f"{w['id']}.json").write_text(
            json.dumps([{"p": s["p"], "h": s["h"]} for s in scored], ensure_ascii=False),
            encoding="utf-8")
        per_work.append({**w, "counts": counts,
                         "hitrate": round(hit_lines / len(lines), 4) if lines else 0.0})
        if i % 60 == 0:
            print(f"{i}/{len(ev['works'])}")

    baseline = shares(total_counts)
    out = []
    for w in per_work:
        sh = shares(w["counts"])
        lf = lifts(sh, baseline)
        out.append({
            **{k: w[k] for k in ("id", "author", "title", "category", "kana_type",
                                  "card_url", "teihon", "chars", "n_lines", "hitrate")},
            "counts": w["counts"],
            "total_hits": sum(w["counts"].values()),
            "shares": {c: round(sh[c], 4) for c in CATEGORIES},
            "lifts": {c: round(lf[c], 4) for c in CATEGORIES},
            "entropy": round(entropy(sh), 4),
            "dominant": dominant(lf),
        })
    PROFILES.write_text(json.dumps({
        "dict_version": scorer.version,
        "baseline": {c: round(baseline[c], 5) for c in CATEGORIES},
        "works": out,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print("基準シェア:", {c: round(baseline[c], 3) for c in CATEGORIES})


if __name__ == "__main__":
    main()
