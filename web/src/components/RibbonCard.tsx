"use client";

// 色相バーコード 1 枚(F-07)。canvas は useEffect 内のみ(HC-002)
import Link from "next/link";
import { useEffect, useRef } from "react";
import { catCss, catIndexCss, JP_NAME } from "@/core/color8";
import type { WorkIndexEntry } from "@/core/types";

export default function RibbonCard({ work }: { work: WorkIndexEntry }) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;
    const w = canvas.width;
    const h = canvas.height;
    ctx.fillStyle = "#141310";
    ctx.fillRect(0, 0, w, h);
    const n = work.ribbon.length || 1;
    for (let i = 0; i < n; i++) {
      const [cat, inten] = work.ribbon[i] ?? [-1, 0];
      ctx.fillStyle = catIndexCss(cat, cat < 0 ? 0.12 : 0.25 + 0.75 * inten);
      ctx.fillRect((i * w) / n, 0, w / n + 1, h);
    }
  }, [work]);

  return (
    <Link className="card" href={`/work/${work.id}/`}>
      <canvas ref={ref} width={256} height={34} aria-label={`${work.title} の情緒リボン`} />
      <div className="t">
        {work.title} <span style={{ color: "var(--muted)", fontSize: "0.78em" }}>{work.author}</span>
      </div>
      <div className="meta">
        <span className="dom">
          <span className="dot" style={{ background: catCss(work.dominant) }} />
          {JP_NAME[work.dominant]}
        </span>
        <span className="ent">彩 {work.entropy.toFixed(2)}</span>
        <span>{work.n_lines.toLocaleString()} 行</span>
      </div>
    </Link>
  );
}
