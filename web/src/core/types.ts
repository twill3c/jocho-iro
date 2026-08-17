// gold JSON の型(SPEC F-06)
export type Hit = [surface: string, polarity: number, category: string, negated: number];

export type Line = { t: string; p: number; h: Hit[] };

export type WorkIndexEntry = {
  id: string;
  author: string;
  title: string;
  category: string;
  kana_type: string;
  chars: number;
  n_lines: number;
  hitrate: number;
  total_hits: number;
  lifts: Record<string, number>;
  entropy: number;
  dominant: string;
  ribbon: [number, number][]; // 64 × [支配情緒番号(-1 = なし), 強度 0..1]
};

export type WorksIndex = {
  dict_version: string;
  baseline: Record<string, number>;
  categories: string[];
  n_works: number;
  works: WorkIndexEntry[];
};

export type WorkDetail = {
  id: string;
  author: string;
  title: string;
  category: string;
  kana_type: string;
  card_url: string;
  teihon: string;
  dict_version: string;
  lifts: Record<string, number>;
  entropy: number;
  dominant: string;
  river: Record<string, number[]>; // 8 情緒 × 64 区間
  lines: Line[];
};
