from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
INDEX_CACHE = DATA / "index_cache"
BRONZE = DATA / "bronze"
SELECTION = DATA / "selection.tsv"
CATALOG = DATA / "catalog.json"
MATCH_REPORT = DATA / "match_report.md"
MANIFEST = DATA / "corpus_manifest.json"
LINES_DIR = DATA / "lines"

INDEX_URL = "https://www.aozora.gr.jp/index_pages/list_person_all_extended_utf8.zip"
USER_AGENT = "kokoro-graph corpus builder (personal research; contact: twill3c@gmail.com)"
FETCH_INTERVAL_SEC = 0.8
