"""情緒数理(SPEC F-03 / F-04)。定義は SPEC §2 が正。"""

from __future__ import annotations

import math

CATEGORIES = ["joy", "anger", "sadness", "fear", "like", "surprise", "dislike", "calm"]
RIVER_RADIUS = 2  # 川の平滑化: 中心窓・半径 2(端は縮小窓)


def shares(counts: dict) -> dict:
    """カテゴリ別ヒット数 → シェア。総ヒット 0 は全シェア 0(縁は正常系)。"""
    total = sum(counts.get(c, 0) for c in CATEGORIES)
    if total == 0:
        return {c: 0.0 for c in CATEGORIES}
    return {c: counts.get(c, 0) / total for c in CATEGORIES}


def entropy(sh: dict) -> float:
    """H = −Σ s log2 s(0 log 0 = 0)。"""
    h = 0.0
    for c in CATEGORIES:
        s = sh.get(c, 0.0)
        if s > 0:
            h -= s * math.log2(s)
    return h


def lifts(sh: dict, baseline: dict) -> dict:
    """リフト r_e = s_e / b_e。基準 0 の情緒は 0。"""
    out = {}
    for c in CATEGORIES:
        b = baseline.get(c, 0.0)
        out[c] = (sh.get(c, 0.0) / b) if b > 0 else 0.0
    return out


def dominant(lf: dict) -> str:
    """支配情緒 = リフト最大(同率は CATEGORIES 順で先勝ち・決定論)。"""
    best, best_v = CATEGORIES[0], -1.0
    for c in CATEGORIES:
        v = lf.get(c, 0.0)
        if v > best_v:
            best, best_v = c, v
    return best


def river(hits: list[tuple[str, int]], n_lines: int, bins: int) -> dict:
    """情緒の川(F-04): (カテゴリ, 行番号) の列を bins 区間に集計し、
    区間あたり件数を半径 RIVER_RADIUS の縮小窓で平滑化した強度列を返す。"""
    raw = {c: [0.0] * bins for c in CATEGORIES}
    if n_lines > 0:
        for cat, line_no in hits:
            if cat not in raw:
                continue
            b = min(bins - 1, int(line_no * bins / n_lines))
            raw[cat][b] += 1.0
    out = {}
    for c in CATEGORIES:
        xs = raw[c]
        sm = []
        for i in range(bins):
            lo = max(0, i - RIVER_RADIUS)
            hi = min(bins, i + RIVER_RADIUS + 1)
            sm.append(sum(xs[lo:hi]) / (hi - lo))
        out[c] = sm
    return out
