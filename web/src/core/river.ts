// 情緒の川の積層データ(SPEC F-08 / T-111)。
// 区間ごとに 8 情緒の強度をシェア正規化し、CATEGORIES 順に積み上げる。
// 全零区間は空配列(描画側で余白になる)。
import { CATEGORIES } from "./color8";

export type StackSeg = { cat: string; y0: number; h: number };

export function riverStacks(
  river: Record<string, number[]>,
  bins: number,
): StackSeg[][] {
  const out: StackSeg[][] = [];
  for (let b = 0; b < bins; b++) {
    let total = 0;
    for (const c of CATEGORIES) total += river[c]?.[b] ?? 0;
    if (!(total > 0)) {
      out.push([]);
      continue;
    }
    const segs: StackSeg[] = [];
    let y0 = 0;
    for (const c of CATEGORIES) {
      const v = river[c]?.[b] ?? 0;
      if (v <= 0) continue;
      const h = v / total;
      segs.push({ cat: c, y0, h });
      y0 += h;
    }
    out.push(segs);
  }
  return out;
}
