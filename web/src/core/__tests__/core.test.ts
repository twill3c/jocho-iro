// T-100 / T-101 / T-110 / T-111: 情緒色・並べ替え/フィルタ・レーダー・川の座標(SPEC F-07/F-08)
import { describe, expect, it } from "vitest";
import { CATEGORIES, catColor, catCss, catIndexCss, NEUTRAL_RGB, PALETTE } from "../color8";
import { filterByDominant, sortByAuthor, sortByEntropy, sortByLift } from "../rank";
import { radarPoints } from "../radar";
import { riverStacks } from "../river";
import type { WorkIndexEntry } from "../types";

const mk = (over: Partial<WorkIndexEntry>): WorkIndexEntry => ({
  id: "0", author: "a", title: "t", category: "c", kana_type: "新字新仮名",
  chars: 1, n_lines: 1, hitrate: 0.3, total_hits: 100,
  lifts: Object.fromEntries(CATEGORIES.map((c) => [c, 1])) as Record<string, number>,
  entropy: 1, dominant: "joy", ribbon: [], ...over,
});

describe("T-100 情緒パレット", () => {
  it("8 情緒すべてに固定色があり、未知/-1 は中立", () => {
    expect(CATEGORIES).toHaveLength(8);
    for (const c of CATEGORIES) expect(PALETTE[c]).toHaveLength(3);
    expect(catColor("joy")).toEqual(PALETTE.joy);
    expect(catColor("unknown")).toEqual(NEUTRAL_RGB);
    expect(catCss("anger")).toBe(`rgb(${PALETTE.anger[0]}, ${PALETTE.anger[1]}, ${PALETTE.anger[2]})`);
  });
});

describe("T-101 並べ替え・フィルタ", () => {
  const A = mk({ id: "1", entropy: 2.5, dominant: "joy", lifts: { ...mk({}).lifts, fear: 3 } });
  const B = mk({ id: "2", entropy: 0.5, dominant: "fear", lifts: { ...mk({}).lifts, fear: 9 } });
  const C = mk({ id: "3", entropy: 1.5, dominant: "joy", lifts: { ...mk({}).lifts, fear: 1 } });
  it("エントロピー降順・入力非破壊", () => {
    const src = [B, A, C];
    expect(sortByEntropy(src).map((w) => w.id)).toEqual(["1", "3", "2"]);
    expect(src.map((w) => w.id)).toEqual(["2", "1", "3"]);
  });
  it("情緒リフト降順", () => {
    expect(sortByLift([A, B, C], "fear").map((w) => w.id)).toEqual(["2", "1", "3"]);
  });
  it("支配情緒フィルタ(空 = 全通し)", () => {
    expect(filterByDominant([A, B, C], [])).toHaveLength(3);
    expect(filterByDominant([A, B, C], ["joy"]).map((w) => w.id)).toEqual(["1", "3"]);
  });
});

describe("T-110 レーダー座標", () => {
  it("8 角形: リフト 1 が基準半径・0 は中心・上限クランプ", () => {
    const lifts = Object.fromEntries(CATEGORIES.map((c) => [c, 1])) as Record<string, number>;
    const pts = radarPoints(lifts, 100, 50, 2);
    expect(pts).toHaveLength(8);
    // 全リフト 1 → 全点が半径 50(基準)。先頭は真上
    expect(pts[0].x).toBeCloseTo(100, 6);
    expect(pts[0].y).toBeCloseTo(100 - 50, 6);
    const zero = radarPoints({ ...lifts, joy: 0 }, 100, 50, 2);
    expect(zero[0].x).toBeCloseTo(100, 6);
    expect(zero[0].y).toBeCloseTo(100, 6);
    const big = radarPoints({ ...lifts, joy: 99 }, 100, 50, 2);
    expect(big[0].y).toBeCloseTo(0, 6); // クランプ最大 = maxLift 2 → 半径 100
  });
});

describe("T-111 川の積層", () => {
  it("区間内で 8 情緒をシェア正規化して積み上げる(全零区間は空)", () => {
    const river = Object.fromEntries(CATEGORIES.map((c) => [c, [0, 0]])) as Record<string, number[]>;
    river.joy = [3, 0];
    river.fear = [1, 0];
    const stacks = riverStacks(river, 2);
    // 区間 0: joy 0.75 → fear 0.25 の積層(合計 1)
    const s0 = stacks[0];
    expect(s0.reduce((a, seg) => a + seg.h, 0)).toBeCloseTo(1, 9);
    expect(s0.find((seg) => seg.cat === "joy")?.h).toBeCloseTo(0.75, 9);
    expect(s0.find((seg) => seg.cat === "fear")?.h).toBeCloseTo(0.25, 9);
    // 区間 1: 全零 → 空
    expect(stacks[1]).toEqual([]);
  });
});

describe("補: 縁と補助関数のカバレッジ", () => {
  it("catIndexCss: -1/範囲外は中立・alpha 付き書式", () => {
    expect(catIndexCss(-1)).toBe(`rgb(${NEUTRAL_RGB[0]}, ${NEUTRAL_RGB[1]}, ${NEUTRAL_RGB[2]})`);
    expect(catIndexCss(99, 0.5)).toBe(
      `rgba(${NEUTRAL_RGB[0]}, ${NEUTRAL_RGB[1]}, ${NEUTRAL_RGB[2]}, 0.5)`,
    );
    expect(catIndexCss(0, 0.25)).toContain("rgba(");
  });

  it("sortByAuthor はロケール順・同作者は id 順", () => {
    const a = mk({ id: "2", author: "い" });
    const b = mk({ id: "1", author: "あ" });
    const c = mk({ id: "3", author: "あ" });
    expect(sortByAuthor([a, b, c]).map((w) => w.id)).toEqual(["1", "3", "2"]);
  });

  it("radarPoints: 非有限値は 0 として扱う", () => {
    const lifts = Object.fromEntries(CATEGORIES.map((c) => [c, Number.NaN])) as Record<string, number>;
    const pts = radarPoints(lifts, 100, 50, 2);
    for (const p of pts) {
      expect(p.x).toBeCloseTo(100, 6);
      expect(p.y).toBeCloseTo(100, 6);
    }
  });

  it("riverStacks: 情緒キー欠落・強度 0 は無視される", () => {
    const stacks = riverStacks({ joy: [2] }, 1);
    expect(stacks[0]).toEqual([{ cat: "joy", y0: 0, h: 1 }]);
  });
});
