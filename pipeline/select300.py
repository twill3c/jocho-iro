"""選定規則 F-02 による 300 作品の機械選出(SPEC G-01)。

適用順(すべて決定論・タイブレークは指標降順 → id 昇順):
① 総有効ヒット ≥ min_hits かつ ヒット行率 ≥ min_hitrate ② 正規化後 ≤ max_chars
③ 各情緒の支配作を per_emotion 作確保(その情緒のリフト降順)
④ 残枠はエントロピー降順 ⑤ 同一作者上限 author_cap
"""

from __future__ import annotations

import json

from .jocho import CATEGORIES
from .paths import DATA

PROFILES = DATA / "profiles.json"
MANIFEST = DATA / "corpus_manifest.json"


def select_works(
    population: list[dict],
    target: int,
    per_emotion: int,
    author_cap: int,
    min_hits: int,
    min_hitrate: float,
    max_chars: int,
) -> dict:
    excluded, eligible = [], []
    for w in sorted(population, key=lambda w: w["id"]):
        if w.get("total_hits", 0) < min_hits:
            excluded.append({"id": w["id"], "author": w["author"], "title": w["title"],
                             "reason": "few_hits", "total_hits": w.get("total_hits", 0)})
        elif w["hitrate"] < min_hitrate:
            excluded.append({"id": w["id"], "author": w["author"], "title": w["title"],
                             "reason": "low_hitrate", "hitrate": w["hitrate"]})
        elif w["chars"] > max_chars:
            excluded.append({"id": w["id"], "author": w["author"], "title": w["title"],
                             "reason": "over_length", "chars": w["chars"]})
        else:
            eligible.append(w)

    chosen: list[dict] = []
    chosen_ids: set[str] = set()
    author_count: dict[str, int] = {}
    shortfalls: dict[str, int] = {}

    def take(w: dict, why: str) -> None:
        chosen.append({**w, "selected_by": why})
        chosen_ids.add(w["id"])
        author_count[w["author"]] = author_count.get(w["author"], 0) + 1

    # ③ 情緒代表の確保(作者上限は代表確保でも尊重)
    for cat in CATEGORIES:
        cands = sorted(
            (w for w in eligible if w["dominant"] == cat and w["id"] not in chosen_ids),
            key=lambda w: (-w["lifts"][cat], w["id"]),
        )
        got = 0
        for w in cands:
            if got >= per_emotion or len(chosen) >= target:
                break
            if author_count.get(w["author"], 0) >= author_cap:
                continue
            take(w, f"exemplar:{cat}")
            got += 1
        if got < per_emotion:
            shortfalls[cat] = per_emotion - got

    # ④⑤ 残枠: エントロピー降順 + 作者上限
    rest = sorted(
        (w for w in eligible if w["id"] not in chosen_ids),
        key=lambda w: (-w["entropy"], w["id"]),
    )
    for w in rest:
        if len(chosen) >= target:
            break
        if author_count.get(w["author"], 0) >= author_cap:
            excluded.append({"id": w["id"], "author": w["author"], "title": w["title"],
                             "reason": "author_cap"})
            continue
        take(w, "entropy")
    not_selected = [w for w in eligible if w["id"] not in chosen_ids
                    and not any(e["id"] == w["id"] for e in excluded)]
    for w in not_selected:
        excluded.append({"id": w["id"], "author": w["author"], "title": w["title"],
                         "reason": "capacity"})

    return {"works": chosen, "excluded": excluded, "shortfalls": shortfalls}


def main() -> None:
    prof = json.loads(PROFILES.read_text(encoding="utf-8"))
    result = select_works(
        prof["works"], target=300, per_emotion=8, author_cap=26,
        min_hits=30, min_hitrate=0.08, max_chars=200_000,
    )
    manifest = {
        "target": 300,
        "rules": {"min_hits": 30, "min_hitrate": 0.08, "max_chars": 200_000, "per_emotion": 8, "author_cap": 26},
        "baseline": prof["baseline"],
        "dict_version": prof["dict_version"],
        "n_works": len(result["works"]),
        "works": result["works"],
        "excluded": result["excluded"],
        "shortfalls": result["shortfalls"],
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    from collections import Counter
    dom = Counter(w["dominant"] for w in result["works"])
    print(f"選出 {len(result['works'])} / 除外 {len(result['excluded'])} / 不足 {result['shortfalls']}")
    print("支配情緒分布:", dict(dom))


if __name__ == "__main__":
    main()
