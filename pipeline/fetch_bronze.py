"""catalog.json の全作品の本文 zip を取得・展開する(手動実行のみ・N-02)。

- リクエスト間隔 FETCH_INTERVAL_SEC(≥0.7s)
- 既取得(data/bronze/{work_id}.txt が存在)はスキップ(再実行可能)
- zip 内の最初の .txt を Shift_JIS(cp932)で読んで UTF-8 で保存
"""

from __future__ import annotations

import io
import json
import time
import urllib.request
import zipfile

from .paths import BRONZE, CATALOG, FETCH_INTERVAL_SEC, USER_AGENT


def main() -> None:
    BRONZE.mkdir(parents=True, exist_ok=True)
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    todo = [c for c in catalog if not (BRONZE / f"{c['work_id']}.txt").exists()]
    print(f"対象 {len(catalog)} 件 / 未取得 {len(todo)} 件")
    errors = []
    for i, c in enumerate(todo, 1):
        url = c["text_url"]
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as res:
                blob = res.read()
            if url.endswith(".zip"):
                with zipfile.ZipFile(io.BytesIO(blob)) as zf:
                    txt_name = next(n for n in zf.namelist() if n.lower().endswith(".txt"))
                    raw = zf.read(txt_name)
            else:
                raw = blob
            text = raw.decode("cp932", errors="replace")
            (BRONZE / f"{c['work_id']}.txt").write_text(text, encoding="utf-8", newline="\n")
            print(f"[{i}/{len(todo)}] {c['author']}『{c['title']}』 OK ({len(text)//1000}k 字)")
        except Exception as e:  # noqa: BLE001 — 取得失敗は記録して続行
            errors.append((c, str(e)))
            print(f"[{i}/{len(todo)}] {c['author']}『{c['title']}』 ERROR: {e}")
        time.sleep(FETCH_INTERVAL_SEC)
    if errors:
        print(f"\n失敗 {len(errors)} 件:")
        for c, e in errors:
            print(f"- {c['author']}『{c['title']}』: {e}")
    else:
        print("\n全件取得完了")


if __name__ == "__main__":
    main()
