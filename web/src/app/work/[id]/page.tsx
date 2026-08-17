import { readFileSync } from "node:fs";
import { join } from "node:path";
import WorkView from "@/components/WorkView";

export function generateStaticParams() {
  const raw = readFileSync(join(process.cwd(), "public", "data", "index.json"), "utf-8");
  const idx = JSON.parse(raw) as { works: { id: string }[] };
  return idx.works.map((w) => ({ id: w.id }));
}

export default async function WorkPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <WorkView id={id} />;
}
