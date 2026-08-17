// 8 情緒の固定パレット(SPEC F-07 / N-03)。未知・-1 は中立(生成り)。
export type Rgb = [number, number, number];

export const CATEGORIES = [
  "joy", "anger", "sadness", "fear", "like", "surprise", "dislike", "calm",
] as const;

export const JP_NAME: Record<string, string> = {
  joy: "喜", anger: "怒", sadness: "哀", fear: "怖",
  like: "好", surprise: "驚", dislike: "厭", calm: "安",
};

export const PALETTE: Record<string, Rgb> = {
  joy: [230, 159, 58],      // 橙(明)
  anger: [198, 62, 46],     // 緋
  sadness: [58, 96, 165],   // 藍
  fear: [122, 79, 160],     // 紫
  like: [214, 106, 140],    // 紅梅
  surprise: [214, 197, 66], // 黄(最明)
  dislike: [110, 125, 60],  // 鶯(暗)
  calm: [63, 155, 124],     // 若竹
};

export const NEUTRAL_RGB: Rgb = [201, 195, 181]; // 生成り(中立・薄め)

export function catColor(cat: string): Rgb {
  return PALETTE[cat] ?? NEUTRAL_RGB;
}

export function catCss(cat: string, alpha?: number): string {
  const [r, g, b] = catColor(cat);
  return alpha === undefined
    ? `rgb(${r}, ${g}, ${b})`
    : `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/** ribbon の情緒番号 → 色(-1 は中立) */
export function catIndexCss(i: number, alpha?: number): string {
  const cat = i >= 0 && i < CATEGORIES.length ? CATEGORIES[i] : "";
  return catCss(cat, alpha);
}
