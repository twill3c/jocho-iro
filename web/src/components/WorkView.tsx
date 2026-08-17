"use client";

// 作品詳細(F-08): 情緒レーダー + 情緒の川 × 本文リーダーの双方向シンクロ
import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { CATEGORIES, catCss, JP_NAME } from "@/core/color8";
import { radarPoints } from "@/core/radar";
import { riverStacks } from "@/core/river";
import { segmentLine } from "@/core/segment";
import type { WorkDetail } from "@/core/types";
import { dataUrl } from "@/lib/basePath";
import Footer from "./Footer";

const RW = 960;
const RH = 220;
const BINS = 64;
const RADAR_SIZE = 260;
const RADAR_BASE = 52;
const MAX_LIFT = 2.4;

export default function WorkView({ id }: { id: string }) {
  const [work, setWork] = useState<WorkDetail | null>(null);
  const [failed, setFailed] = useState(false);
  const [selected, setSelected] = useState(0);
  const readerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch(dataUrl(`works/${id}.json`))
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then(setWork)
      .catch(() => setFailed(true));
  }, [id]);

  useEffect(() => {
    const el = readerRef.current?.querySelector(`[data-line="${selected}"]`);
    el?.scrollIntoView({ block: "center", behavior: "smooth" });
  }, [selected]);

  const stacks = useMemo(() => (work ? riverStacks(work.river, BINS) : []), [work]);
  const radar = useMemo(
    () => (work ? radarPoints(work.lifts, RADAR_SIZE / 2, RADAR_BASE, MAX_LIFT) : []),
    [work],
  );

  if (failed) return <main className="hall"><p className="loading">読み込みに失敗しました。</p></main>;
  if (!work) return <main className="hall"><p className="loading">読み込み中…</p></main>;

  const c = RADAR_SIZE / 2;
  const selBin = Math.min(BINS - 1, Math.floor((selected / Math.max(1, work.lines.length)) * BINS));

  return (
    <main className="hall" key={work.id}>
      <nav className="crumbs">
        <Link href="/">← 色見本帖へ戻る</Link>
      </nav>
      <header className="work-head">
        <h1>{work.title}</h1>
        <p className="work-author">{work.author}</p>
        <p className="work-meta">
          支配情緒 {JP_NAME[work.dominant]} ・ 彩り {work.entropy.toFixed(2)} ・ {work.lines.length.toLocaleString()} 行 ・ {work.kana_type} ・ 辞書 v{work.dict_version}
          {work.card_url && (
            <>
              {" ・ "}
              <a href={work.card_url} target="_blank" rel="noreferrer">青空文庫 図書カード</a>
            </>
          )}
        </p>
      </header>

      <div className="panels">
        <section className="panel">
          <h2>情緒プロファイル</h2>
          <svg viewBox={`0 0 ${RADAR_SIZE} ${RADAR_SIZE}`} role="img" aria-label="八情緒のレーダーチャート">
            {[0.5, 1, 2].map((lv) => (
              <circle key={lv} cx={c} cy={c} r={lv * RADAR_BASE} fill="none"
                stroke={lv === 1 ? "rgba(217,179,106,0.45)" : "var(--border)"}
                strokeDasharray={lv === 1 ? "" : "3 3"} />
            ))}
            {radar.map((p) => (
              <line key={p.cat} x1={c} y1={c}
                x2={c + (MAX_LIFT * RADAR_BASE) * Math.cos(Math.atan2(p.y - c, p.x - c) || -Math.PI / 2)}
                y2={c + (MAX_LIFT * RADAR_BASE) * Math.sin(Math.atan2(p.y - c, p.x - c) || -Math.PI / 2)}
                stroke="var(--border)" strokeWidth={0.5} />
            ))}
            <polygon points={radar.map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ")}
              fill="rgba(217,179,106,0.18)" stroke="var(--gold)" strokeWidth={1.5} />
            {radar.map((p, i) => {
              const angle = -Math.PI / 2 + (2 * Math.PI * i) / 8;
              const lx = c + (MAX_LIFT * RADAR_BASE + 14) * Math.cos(angle);
              const ly = c + (MAX_LIFT * RADAR_BASE + 14) * Math.sin(angle);
              return (
                <g key={p.cat}>
                  <circle cx={p.x} cy={p.y} r={3} fill={catCss(p.cat)} />
                  <text x={lx} y={ly + 4} textAnchor="middle" fontSize={13} fill={catCss(p.cat)}>
                    {JP_NAME[p.cat]}
                  </text>
                </g>
              );
            })}
          </svg>
          <p className="panel-hint">金の円 = コーパス平均(リフト 1)。外へ張り出すほどその情緒が濃い</p>
        </section>

        <section className="panel">
          <h2>情緒の川 — 物語の進行 × 情緒の配合</h2>
          <svg
            className="river-svg"
            viewBox={`0 0 ${RW} ${RH}`}
            role="img"
            aria-label="情緒の川(積層ストリームグラフ)"
            onClick={(e) => {
              const rect = e.currentTarget.getBoundingClientRect();
              const bin = Math.max(0, Math.min(BINS - 1, Math.floor(((e.clientX - rect.left) / rect.width) * BINS)));
              setSelected(Math.min(work.lines.length - 1, Math.floor(((bin + 0.5) / BINS) * work.lines.length)));
            }}
          >
            {stacks.map((segs, b) =>
              segs.map((seg) => (
                <rect
                  key={`${b}-${seg.cat}`}
                  x={(b * RW) / BINS}
                  y={seg.y0 * RH}
                  width={RW / BINS + 0.5}
                  height={seg.h * RH}
                  fill={catCss(seg.cat, 0.85)}
                />
              )),
            )}
            <rect x={(selBin * RW) / BINS} y={0} width={RW / BINS} height={RH}
              fill="none" stroke="var(--fg)" strokeWidth={1.5} />
          </svg>
          <p className="panel-hint">クリックでその場面の本文へ。帯の太さ = その区間の情緒の配合</p>
        </section>
      </div>

      <div className="reader" ref={readerRef}>
        {work.lines.map((line, i) => (
          <button key={i} type="button" data-line={i}
            className={`line ${i === selected ? "sel" : ""}`}
            onClick={() => setSelected(i)}>
            {segmentLine(line.t, line.h).map((seg, j) =>
              seg.hit === null ? (
                <span key={j}>{seg.text}</span>
              ) : (
                <mark key={j}
                  className={line.h[seg.hit][3] ? "neg" : ""}
                  style={{ color: catCss(line.h[seg.hit][2]) }}
                  title={`${JP_NAME[line.h[seg.hit][2]]}${line.h[seg.hit][3] ? "(否定・集計外)" : ""}`}>
                  {seg.text}
                </mark>
              ),
            )}
          </button>
        ))}
      </div>

      {work.teihon && <p className="teihon">{work.teihon}(青空文庫)</p>}
      <Footer />
    </main>
  );
}
