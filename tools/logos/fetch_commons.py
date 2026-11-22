#!/usr/bin/env python3
"""Download every Wikidata logo file (P154) listed in register/brands.csv.

Files are saved unmodified under logos/sources/<slug>/commons/, with their
URL, SHA-256 and Wikidata statement details in logos/sources/<slug>/provenance.json.

The MediaWiki API is rate-limited from this network, so file URLs are built
the way MediaWiki stores uploads: /<md5[0]>/<md5[0:2]>/<File_name>.
Uncached files are throttled hard (HTTP 429, Retry-After 600), so the script is
slow and resumable: files already on disk are not fetched again.

Usage:  python3 tools/logos/fetch_commons.py [slug ...]
"""
import csv
import hashlib
import re
import sys
import time
import urllib.error
import urllib.parse

from common import ROOT, SOURCES, download, file_record, load_prov, save_prov

CELL = re.compile(r"^(?P<file>.+?) \[(?P<rank>\w+)(?:, (?P<start>\d*|unknown)-(?P<end>\d*|unknown))?\]$")


def commons_url(filename):
    name = filename.replace(" ", "_")
    h = hashlib.md5(name.encode("utf-8")).hexdigest()
    return "https://upload.wikimedia.org/wikipedia/commons/%s/%s/%s" % (h[0], h[:2], urllib.parse.quote(name))


def parse_logos(cell):
    """Parse the wikidata_logo_files column written by tools/register/build_register.py (logo_cell)."""
    out = []
    for part in filter(None, cell.split(" | ")):
        m = CELL.match(part)
        if not m:
            raise ValueError("unparseable logo cell: %r" % part)
        out.append({k: (v or None) for k, v in m.groupdict().items()})
    return out


def fetch(slug, qid, logos):
    folder = SOURCES / slug / "commons"
    folder.mkdir(parents=True, exist_ok=True)
    prov = load_prov(slug)
    previous = {e["file"]: e for e in prov.get("wikidata", {}).get("files", []) if "sha256" in e}
    entries = []
    for lg in logos:
        url = commons_url(lg["file"])
        name = lg["file"].replace(" ", "_")
        saved = folder / name
        if saved.exists() and lg["file"] in previous:
            entries.append(previous[lg["file"]])  # keep the original retrieval record
            continue
        try:
            blob = download(url)
        except urllib.error.HTTPError as e:
            entries.append({**lg, "url": url, "error": "HTTP %d" % e.code})
            print("  %-16s FAIL %s (%s)" % (slug, lg["file"], e.code))
            continue
        saved.write_bytes(blob)
        entries.append({**lg, "url": url, "saved_as": "commons/" + name,
                        "commons_page": "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(name),
                        **file_record(blob)})
        time.sleep(20)  # uncached files are throttled hard from this network
    prov["wikidata"] = {"qid": qid, "property": "P154", "files": entries}
    save_prov(slug, prov)
    return sum("sha256" in e for e in entries), len(entries)


def main(only):
    with open(ROOT / "register" / "brands.csv", encoding="utf-8") as f:
        brands = [b for b in csv.DictReader(f) if not only or b["slug"] in only]
    for b in brands:
        logos = parse_logos(b["wikidata_logo_files"])
        if logos:
            ok, total = fetch(b["slug"], b["wikidata_qid"], logos)
            print("%-16s %d/%d downloaded" % (b["slug"], ok, total))


if __name__ == "__main__":
    main(set(sys.argv[1:]))
