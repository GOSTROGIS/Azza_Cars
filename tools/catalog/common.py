"""Shared helpers for the catalog workstream: polite HTTP and source archiving."""
import csv
import gzip
import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "catalog"
SOURCES = CATALOG / "sources"
UA = "AzzaCarsCatalog/0.1 (https://github.com/GOSTROGIS/Azza_Cars) python-urllib"


def now_utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256(blob):
    return hashlib.sha256(blob).hexdigest()


def get(url, data=None, accept=None, tries=6):
    """GET (or POST when data is given) with retries on 429, 5xx and network errors."""
    headers = {"User-Agent": UA}
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, data=data, headers=headers)
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if (e.code != 429 and e.code < 500) or attempt == tries - 1:
                raise
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt == tries - 1:
                raise
        time.sleep(2 ** attempt)


def brands():
    with open(ROOT / "register" / "brands.csv", newline="") as f:
        return list(csv.DictReader(f))


def write_jsonl_gz(path, records):
    """Archive raw responses: one JSON object per line, gzip with a fixed mtime so reruns diff cleanly."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as gz:
        for rec in records:
            gz.write((json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n").encode())


def read_jsonl_gz(path):
    with gzip.open(path, "rt") as f:
        return [json.loads(line) for line in f]


def save_provenance(name, entries):
    """Write catalog/sources/<name>/provenance.json, one entry per archived blob."""
    path = SOURCES / name / "provenance.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, indent=1, ensure_ascii=False) + "\n")
