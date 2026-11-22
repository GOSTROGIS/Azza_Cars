#!/usr/bin/env python3
"""Download the Brandfetch logo files listed in work/brandfetch.json.

work/brandfetch.json is collected through the Brandfetch MCP tools (get_brands),
because the API is only reachable from the assistant session. It holds signed
asset URLs and is therefore kept out of git (work/ is ignored).

Files are saved unmodified under logos/sources/<slug>/brandfetch/. Provenance
goes into logos/sources/<slug>/provenance.json with the signing token (?c=...)
removed from the recorded URL.

Usage:  python3 tools/logos/fetch_brandfetch.py [slug ...]
"""
import json
import sys
import urllib.parse

from common import ROOT, SOURCES, download, file_record, load_prov, save_prov

INDEX = ROOT / "work" / "brandfetch.json"
WANTED = {"svg", "png"}


def unsigned(url):
    return urllib.parse.urlunsplit(urllib.parse.urlsplit(url)._replace(query=""))


def fetch(slug, rec, logos):
    folder = SOURCES / slug / "brandfetch"
    folder.mkdir(parents=True, exist_ok=True)
    prov = load_prov(slug)
    previous = {e["saved_as"]: e for e in prov.get("brandfetch", {}).get("files", [])}
    entries, seen = [], set()
    for lg in logos:
        name = "%s-%s.%s" % (lg["type"], lg["theme"] or "default", lg["format"])
        if name in seen:  # several "other" assets can share type and theme
            name = name.replace(".", "-%d." % len(seen), 1)
        seen.add(name)
        rel = "brandfetch/" + name
        if (folder / name).exists() and rel in previous:
            entries.append(previous[rel])
            continue
        try:
            blob = download(lg["src"])
        except Exception as e:
            print("  %-16s FAIL %s (%s)" % (slug, name, e))
            continue
        (folder / name).write_bytes(blob)
        entries.append({"saved_as": rel, "type": lg["type"], "theme": lg["theme"], "format": lg["format"],
                        "url_unsigned": unsigned(lg["src"]), **file_record(blob)})
    prov["brandfetch"] = {"brand_id": rec.get("brandfetch_id"), "name": rec.get("brandfetch_name"),
                          "domain": rec.get("brandfetch_domain"), "claimed_by_brand": rec.get("claimed"),
                          "colors": rec.get("colors", []), "files": entries}
    save_prov(slug, prov)
    return len(entries)


def main(only):
    index = json.loads(INDEX.read_text())
    for slug, rec in sorted(index.items()):
        logos = [lg for lg in rec.get("logos", []) if lg["format"] in WANTED and lg["type"] != "icon"]
        if (only and slug not in only) or rec.get("status") != "ok" or not logos:
            continue
        print("%-16s %d files" % (slug, fetch(slug, rec, logos)))


if __name__ == "__main__":
    main(set(sys.argv[1:]))
