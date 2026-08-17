# T-090: gold 整合(SPEC F-06 / G-04)。生成前は fail が正(完了条件の一部)。
import json
from pathlib import Path

from pipeline.jocho import CATEGORIES, dominant, entropy, lifts, shares

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "web" / "public" / "data" / "index.json"
WORKS_DIR = ROOT / "web" / "public" / "data" / "works"

EPS = 1e-3  # index は 4 桁丸めのため


def test_t090_gold_consistency():
    idx = json.loads(INDEX.read_text(encoding="utf-8"))
    assert idx["n_works"] == 300
    assert len(idx["works"]) == 300
    for e in idx["works"]:
        assert len(e["ribbon"]) == 64
        for cat_i, inten in e["ribbon"]:
            assert 0 <= cat_i < len(CATEGORIES) or cat_i == -1
            assert 0.0 <= inten <= 1.0
        assert e["dominant"] in CATEGORIES
        assert e["entropy"] >= 0.0

    # 抜き取り 10 作品: works ファイルからリフト・エントロピーを再計算して一致
    for e in idx["works"][::30]:
        w = json.loads((WORKS_DIR / f"{e['id']}.json").read_text(encoding="utf-8"))
        assert len(w["lines"]) == e["n_lines"]
        counts = {c: 0 for c in CATEGORIES}
        for line in w["lines"]:
            for h in line["h"]:
                if not h[3]:
                    counts[h[2]] += 1
        sh = shares(counts)
        lf = lifts(sh, idx["baseline"])
        assert abs(entropy(sh) - e["entropy"]) < EPS, e["title"]
        assert dominant(lf) == e["dominant"], e["title"]
        for c in CATEGORIES:
            assert abs(lf[c] - e["lifts"][c]) < 0.01, (e["title"], c)
        assert len(w["river"][CATEGORIES[0]]) == 64
