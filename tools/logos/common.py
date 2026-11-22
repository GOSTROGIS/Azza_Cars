"""Shared paths, download and provenance helpers for the logo tools."""
import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / "logos" / "sources"
UA = "AzzaCarsLogoAudit/0.1 (logo provenance; python-urllib)"
ORIGINS = ("website", "brandfetch", "commons")   # also the order of preference for a master
RASTER = {".png", ".jpg", ".jpeg", ".webp"}


def download(url, attempts=4):
    """GET with retries on throttling (429, honouring Retry-After), 5xx and network errors."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 and e.code < 500 or attempt == attempts - 1:
                raise
            wait = int(e.headers.get("Retry-After") or 0) or 15 * (attempt + 1)
        except (urllib.error.URLError, TimeoutError):
            if attempt == attempts - 1:
                raise
            wait = 2 ** attempt
        time.sleep(wait)


def file_record(blob):
    return {"sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob),
            "retrieved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


def load_prov(slug):
    p = SOURCES / slug / "provenance.json"
    return json.loads(p.read_text()) if p.exists() else {}


def save_prov(slug, prov):
    (SOURCES / slug / "provenance.json").write_text(json.dumps(prov, indent=1, ensure_ascii=False))


def source_files(slug):
    """Downloaded source files for a brand, in ORIGINS order, as paths relative to its folder."""
    out = []
    for origin in ORIGINS:
        folder = SOURCES / slug / origin
        if folder.exists():
            out += ["%s/%s" % (origin, p.name) for p in sorted(folder.iterdir())
                    if p.suffix.lower() in RASTER | {".svg"}]
    return out
