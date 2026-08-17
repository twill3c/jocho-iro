"use client";

// 一覧(F-07): 色相バーコードの壁 + 支配情緒フィルタ + 並べ替え
import { useEffect, useMemo, useState } from "react";
import { CATEGORIES, catCss, JP_NAME } from "@/core/color8";
import { filterByDominant, sortByAuthor, sortByEntropy, sortByLift } from "@/core/rank";
import type { WorksIndex } from "@/core/types";
import { dataUrl } from "@/lib/basePath";
import Footer from "./Footer";
import RibbonCard from "./RibbonCard";

const SORTS: { key: string; label: string }[] = [
  { key: "entropy", label: "彩り豊かな順(エントロピー)" },
  ...CATEGORIES.map((c) => ({ key: `lift:${c}`, label: `${JP_NAME[c]}が濃い順` })),
  { key: "author", label: "作者順" },
];

export default function WallPage() {
  const [index, setIndex] = useState<WorksIndex | null>(null);
  const [sortKey, setSortKey] = useState("entropy");
  const [doms, setDoms] = useState<string[]>([]);

  useEffect(() => {
    fetch(dataUrl("index.json"))
      .then((r) => r.json())
      .then(setIndex)
      .catch(() => setIndex(null));
  }, []);

  const shown = useMemo(() => {
    if (!index) return [];
    const f = filterByDominant(index.works, doms);
    if (sortKey === "author") return sortByAuthor(f);
    if (sortKey.startsWith("lift:")) return sortByLift(f, sortKey.slice(5));
    return sortByEntropy(f);
  }, [index, doms, sortKey]);

  const toggle = (c: string) =>
    setDoms((cur) => (cur.includes(c) ? cur.filter((x) => x !== c) : [...cur, c]));

  return (
    <main className="hall">
      <header className="masthead">
        <p className="eyebrow">青空文庫 300 作品 × 八情緒分析</p>
        <h1>情緒の色</h1>
        <p className="lede">
          物語を八つの情緒 — 喜・怒・哀・怖・好・驚・厭・安 — の色で染めた色見本帖。
          リボンの色の移ろいが、その物語の情緒の変遷です。気になる一本から、
          レーダーと「情緒の川」へ。
        </p>
        <div className="palette-legend">
          {CATEGORIES.map((c) => (
            <span key={c} className="sw">
              <span className="dot" style={{ background: catCss(c) }} />
              {JP_NAME[c]}
            </span>
          ))}
        </div>
      </header>

      <div className="controls">
        <div className="row">
          <span className="label">並べ替え</span>
          <select value={sortKey} onChange={(e) => setSortKey(e.target.value)}>
            {SORTS.map((s) => (
              <option key={s.key} value={s.key}>
                {s.label}
              </option>
            ))}
          </select>
          <span className="count">{index ? `${shown.length} / ${index.n_works} 作品` : ""}</span>
        </div>
        <div className="row">
          <span className="label">支配情緒</span>
          {CATEGORIES.map((c) => (
            <button key={c} className={`emochip ${doms.includes(c) ? "on" : ""}`} onClick={() => toggle(c)}>
              <span className="dot" style={{ background: catCss(c) }} />
              {JP_NAME[c]}
            </button>
          ))}
        </div>
      </div>

      {!index && <p className="loading">読み込み中…</p>}
      {index && (
        <div className="wall">
          {shown.map((w) => (
            <RibbonCard key={w.id} work={w} />
          ))}
        </div>
      )}
      <Footer />
    </main>
  );
}
