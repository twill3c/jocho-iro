"""行スコアリング(SPEC F-05)。

- ヒット = fugashi(unidic-lite)トークンの lemma(語彙素)または表層が辞書語と一致
- 行極性 = ヒット語極性の平均。ヒット 0 は 0(中立)
- 否定反転: ヒット語の直後 2 形態素以内に否定(ない/ぬ/ん/ず/ざる 系)があれば
  当該ヒットの極性を反転する
"""

from __future__ import annotations

import fugashi

NEGATION_SURFACES = {"ない", "無い", "ぬ", "ん", "ず", "ざる", "なかっ", "なけれ", "ねえ", "ねば"}
NEGATION_LEMMAS = {"ない", "無い", "ぬ", "ず"}
NEG_WINDOW = 2


class Scorer:
    def __init__(self, dictionary: dict):
        self.version = dictionary["version"]
        self.table = {e["w"]: (float(e["p"]), e["c"]) for e in dictionary["entries"]}
        self.tagger = fugashi.Tagger()

    def _lemma(self, word) -> str:
        lemma = word.feature.lemma
        return lemma if lemma else word.surface

    def _is_negation(self, word) -> bool:
        return word.surface in NEGATION_SURFACES or self._lemma(word) in NEGATION_LEMMAS

    def score_line(self, line: str) -> dict:
        words = list(self.tagger(line))
        hits: list[list] = []  # [表層, 実効極性, カテゴリ, 否定フラグ(0/1)]
        for i, w in enumerate(words):
            key = None
            if w.surface in self.table:
                key = w.surface
            else:
                lemma = self._lemma(w)
                if lemma in self.table:
                    key = lemma
            if key is None:
                continue
            p, c = self.table[key]
            negated = 0
            for j in range(i + 1, min(i + 1 + NEG_WINDOW, len(words))):
                if self._is_negation(words[j]):
                    p = -p
                    negated = 1
                    break
            hits.append([w.surface, round(p, 3), c, negated])
        polarity = sum(h[1] for h in hits) / len(hits) if hits else 0.0
        return {"p": round(polarity, 4), "h": hits}
