# AGENTS.md — jocho-iro

kokoro-graph の姉妹アプリ(8 情緒分析)。分析は開発時 Python で前計算し、web は静的ビューア。
正しさの正本は pytest(選定・情緒数理ゲート)+ vitest + verify.mjs。仕様は SPEC.md、テストは TEST_SPEC.md。

## 1. 技術構成

- pipeline/(Python 3.12): kokoro-graph から流用(正規化・分割・スコア)+ 本作固有(情緒集計・再選出・gold)
- dict/kokoro_dict.json: kokoro-graph v1.1.0 の同梱コピー(共通資産)。改版は感度分析付きのみ
- web/(Next.js 15 静的 export + trailingSlash)。bronze はコミットしない・gold はコミットする
- bronze 317 件は kokoro-graph からローカル複製済み。追加候補のみ手動取得(N-02)

## 2. looplog 運用の注意

- EVENT_SPECS / ENUMS を初回使用前に確認。test_run の数値は出力から転記し、実行と記録は別コマンド(HC-002)。

## 3. 品質ゲート(完了条件)

- Python: `python -m pytest -q tests/` 全緑 / web: `node scripts/verify.mjs` green
- 選定規則(F-02)・情緒数理(F-03/F-04)は SPEC が正。テストは実装から転記しない
- ゲート緩和(閾値引き下げ・テスト削除/skip・較正証拠なしの基準変更)は人間の承認なしに行わない

## 4. アーキテクチャ規約

- 青空文庫アクセスは手動コマンドのみ・≥0.8s 間隔。テストはフィクスチャ駆動
- 行テキストは逐語。否定反転ヒットは情緒集計から除外(F-05)— 極性とは別勘定であることを崩さない
- 選定は決定論(F-02 の順序適用)。「なぜこの 300 か」を manifest で常に再現可能にする
- web の純粋コアは DOM 非依存・useEffect 規律(HC-002)・keyed remount・非有限値は正常系
- デプロイ前にサブドメインの空きを curl で確認する(kokoro-graph の教訓)

## 5. 変更禁止領域

- `logs/loops/*.jsonl`(append-only)/ AGENTS 末尾 scaffold ブロック / `.wt/gate.json` 上限 / `data/bronze/`

## 6. よく使うコマンド

```bash
python -m pipeline.match            # selection.tsv と索引の照合
python -m pipeline.fetch_bronze     # 追加候補のみ取得(手動)
python -m pipeline.build_corpus     # 評価母集団の正規化・分割
python -m pipeline.profile          # 全候補の情緒プロファイル採点
python -m pipeline.select300        # 選定規則 F-02 で 300 確定
python -m pipeline.build_gold       # gold 生成
python -m pytest -q tests/
cd web && node scripts/verify.mjs
```

<!-- scaffold:block agents_core v1.8.0 -->
## 共通規律(scaffold 管理領域 — 手動編集禁止)

このセクションはスキャフォールド・レジストリが管理する。内容を変更したい場合は、
このファイルを直接編集せず、失敗ログ → HARNESS_CHANGELOG 起票 → レジストリ改訂 → `scaffoldctl update` の経路で行うこと。

### 7 段階ループプロトコル

| 段階 | 名称 | 完了条件 |
|---|---|---|
| 1 | 計画 | 対象の要求 ID を特定し、`loop_start` を記録した |
| 2 | 文脈読込 | SPEC.md / IMPLEMENTATION_GUIDE.md の該当箇所と、直近ループのログを読んだ |
| 3 | テスト先行 | TEST_SPEC.md にトレースする失敗するテストを書き、赤を確認した |
| 4 | 実装 | ファイル編集 2 回ごとにテストを実行し、赤のまま次の編集に進んでいない |
| 5 | 検証 | 全テスト合格 + 独立再計算(該当時)を確認した |
| 6 | 文書同期 | SPEC/docs と実装の乖離(SPEC-DRIFT)を解消し、生成ドキュメントを再生成した |
| 7 | 完了 | `loop_end` を記録し、ループログ validate に合格し、専用コミットを積んだ |

### ループ可観測性

全ループは loop-observability の規律(LOOP_LOG_SPEC / FAILURE_TAXONOMY)に従い
`logs/loops/{loop_id}.jsonl` に記録する。失敗は気づいた瞬間に分類コード付きで記録する。
ツーストライク(LL-10)と S1 即時起票(LL-12)は本プロジェクトでも有効である。

### エスカレーション規範

以下の場合は作業を止め、`escalation` を記録してから人間に確認する:
仕様の複数解釈(SPEC-AMB 相当)/ スコープ外ファイルへの変更が必要になった /
破壊的操作(履歴改変・データ削除・強制 push)/ 同種の修正の 3 回目の失敗(PROC-LOOP)。

### コミット規約

Conventional Commits(feat/fix/test/docs/refactor/chore)。スキャフォールド更新は
`chore: scaffold vX.Y.Z` の専用コミットで行い、機能変更と混ぜない。
<!-- /scaffold:block agents_core -->
