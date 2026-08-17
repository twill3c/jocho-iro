// 行テキストをヒット語で分割する(F-09 のハイライト用)。純関数。
import type { Hit } from "./types";

export type Segment = { text: string; hit: number | null }; // hit = hits 配列の添字

export function segmentLine(text: string, hits: readonly Hit[]): Segment[] {
  const segs: Segment[] = [];
  let cursor = 0;
  hits.forEach((h, idx) => {
    const at = text.indexOf(h[0], cursor);
    if (at < 0) return;
    if (at > cursor) segs.push({ text: text.slice(cursor, at), hit: null });
    segs.push({ text: h[0], hit: idx });
    cursor = at + h[0].length;
  });
  if (cursor < text.length) segs.push({ text: text.slice(cursor), hit: null });
  return segs;
}
