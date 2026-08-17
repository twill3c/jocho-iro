// 情緒レーダーの座標(SPEC F-08 / T-110)。8 軸・真上から時計回り。
// 半径 = clamp(リフト, 0, maxLift) × baseR(リフト 1 = 基準円 baseR)。
// 非有限値は 0(縁は正常系)。
import { CATEGORIES } from "./color8";

export type RadarPoint = { x: number; y: number; cat: string };

export function radarPoints(
  lifts: Record<string, number>,
  center: number,
  baseR: number,
  maxLift: number,
): RadarPoint[] {
  return CATEGORIES.map((cat, i) => {
    const raw = lifts[cat] ?? 0;
    const v = Number.isFinite(raw) ? Math.max(0, Math.min(maxLift, raw)) : 0;
    const radius = v * baseR;
    const angle = -Math.PI / 2 + (2 * Math.PI * i) / CATEGORIES.length;
    return {
      x: center + radius * Math.cos(angle),
      y: center + radius * Math.sin(angle),
      cat,
    };
  });
}
