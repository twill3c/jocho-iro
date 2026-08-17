// 並べ替え・フィルタ(SPEC F-07)。純関数・入力非破壊。
import type { WorkIndexEntry } from "./types";

export function sortByEntropy(works: readonly WorkIndexEntry[]): WorkIndexEntry[] {
  return [...works].sort((a, b) => b.entropy - a.entropy || a.id.localeCompare(b.id));
}

export function sortByLift(works: readonly WorkIndexEntry[], cat: string): WorkIndexEntry[] {
  return [...works].sort(
    (a, b) => (b.lifts[cat] ?? 0) - (a.lifts[cat] ?? 0) || a.id.localeCompare(b.id),
  );
}

export function sortByAuthor(works: readonly WorkIndexEntry[]): WorkIndexEntry[] {
  return [...works].sort(
    (a, b) => a.author.localeCompare(b.author, "ja") || a.id.localeCompare(b.id),
  );
}

export function filterByDominant(
  works: readonly WorkIndexEntry[],
  dominants: readonly string[],
): WorkIndexEntry[] {
  if (dominants.length === 0) return [...works];
  return works.filter((w) => dominants.includes(w.dominant));
}
