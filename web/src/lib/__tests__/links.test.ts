// T-120: フッタ 5 リンク + 姉妹リンク(F-09)
import { describe, expect, it } from "vitest";
import { FOOTER_LINKS, FOOTER_NOTICE } from "../links";

describe("T-120 footer", () => {
  it("MIT License 表記", () => {
    expect(FOOTER_NOTICE).toBe("MIT License © 2026 坂田哲朗");
  });

  it("アンカーが正しいラベルと href を持つ", () => {
    expect(FOOTER_LINKS).toEqual([
      { label: "GitHub", href: "https://github.com/twill3c/jocho-iro" },
      {
        label: "jocho-iro の眺め方",
        href: "https://claude.ai/code/artifact/eb775e45-fc63-4098-a5bb-28f6f7b41ddd",
      },
      {
        label: "jocho-iro 設計図",
        href: "https://claude.ai/code/artifact/eeae0d3e-674c-4e90-b3aa-9ce4dfd8ad38",
      },
      { label: "姉妹アプリ kokoro-graph", href: "https://kokorograph.vercel.app/" },
      { label: "App Menu", href: "https://app-menu-amber.vercel.app/" },
    ]);
  });
});
