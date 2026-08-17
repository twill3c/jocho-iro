// T-130 補: 行テキストのヒット語分割(F-09 ハイライト用・純関数)
import { describe, expect, it } from "vitest";
import { segmentLine } from "../segment";

describe("segmentLine", () => {
  it("ヒット表層を出現順に 1 回ずつ切り出す", () => {
    const segs = segmentLine("嬉しくない朝だが嬉しい。", [
      ["嬉しく", -0.7, "joy", 1],
      ["嬉しい", 0.7, "joy", 0],
    ]);
    expect(segs).toEqual([
      { text: "嬉しく", hit: 0 },
      { text: "ない朝だが", hit: null },
      { text: "嬉しい", hit: 1 },
      { text: "。", hit: null },
    ]);
  });

  it("ヒットなし・見つからない表層は素通しする", () => {
    expect(segmentLine("ただの朝。", [])).toEqual([{ text: "ただの朝。", hit: null }]);
    expect(segmentLine("ただの朝。", [["夜", -0.4, "fear", 0]])).toEqual([
      { text: "ただの朝。", hit: null },
    ]);
  });

  it("空行は空配列", () => {
    expect(segmentLine("", [])).toEqual([]);
  });
});
