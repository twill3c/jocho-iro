"""青空文庫の全作品索引 CSV を取得する(手動実行のみ・N-02)。"""

import io
import urllib.request
import zipfile

from .paths import INDEX_CACHE, INDEX_URL, USER_AGENT


def main() -> None:
    INDEX_CACHE.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(INDEX_URL, headers={"User-Agent": USER_AGENT})
    print(f"取得中: {INDEX_URL}")
    with urllib.request.urlopen(req, timeout=60) as res:
        blob = res.read()
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        names = zf.namelist()
        csv_name = next(n for n in names if n.endswith(".csv"))
        zf.extract(csv_name, INDEX_CACHE)
    print(f"展開 → {INDEX_CACHE / csv_name}({len(blob) // 1024} KB zip)")


if __name__ == "__main__":
    main()
