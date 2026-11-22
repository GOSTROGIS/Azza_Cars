#!/usr/bin/env python3
"""Propose a master and an independent reference for each brand.

Every pairing of a vector master from one origin with a reference from another
origin is scored at a reduced resolution, using the audit's own agreement test
(audit.agreement_verdict), so a proposed pair is one the audit would also accept. The proposal
is written to logos/proposals.json for visual review. Rows are only copied into
logos/selection.csv (the audit input) after a person has looked at them, using
--accept slug [slug ...].

Origins: website (captured from the brand's own homepage), brandfetch, commons.
Preference among pairs that agree: a master from the brand's website, then from
Brandfetch (which also takes its files from the brand's site), then a Commons
file that Wikidata marks as current (no end date). An SVG reference is preferred
over a raster one.

Usage:
  python3 tools/logos/propose_selection.py [slug ...]          score and propose
  python3 tools/logos/propose_selection.py --accept slug ...   copy reviewed proposals into selection.csv
"""
import csv
import json
import sys

import audit as A
from common import ORIGINS, ROOT, SOURCES, load_prov, source_files

PROPOSALS = ROOT / "logos" / "proposals.json"
SELECTION = ROOT / "logos" / "selection.csv"
SCORE_W = 768            # artwork width used for scoring pairs (the audit itself uses 2048)


def historical_commons_files(slug):
    """Commons files whose Wikidata statement has an end date (former logos)."""
    files = load_prov(slug).get("wikidata", {}).get("files", [])
    return {f["saved_as"] for f in files if f.get("end") and "saved_as" in f}


def candidates(slug):
    old = historical_commons_files(slug)
    out = []
    for rel in source_files(slug):
        is_svg = rel.endswith(".svg")
        flags = A.svg_flags((SOURCES / slug / rel).read_text(encoding="utf-8", errors="replace")) if is_svg else []
        out.append({"file": rel, "origin": rel.split("/")[0], "kind": "svg" if is_svg else "raster",
                    "historical": rel in old, "flags": flags})
    return out


def score(slug):
    cands = candidates(slug)
    images = {}
    for c in cands:
        try:
            images[c["file"]] = A.artwork(SOURCES / slug / c["file"], SCORE_W)
        except Exception as e:
            c["error"] = "%s: %s" % (type(e).__name__, e)
    pairs = []
    for m in cands:
        if m["kind"] != "svg" or m["flags"] or m["historical"] or images.get(m["file"], (None,))[0] is None:
            continue
        for r in cands:
            if r["origin"] == m["origin"] or images.get(r["file"], (None,))[0] is None:
                continue
            metrics, problems, _, _ = A.agreement_verdict(images[m["file"]][0], *images[r["file"]])
            pairs.append({"master": m["file"], "reference": r["file"], "problems": problems,
                          "beyond_pct": metrics["pixels_beyond_tolerance_pct"], "aspect_diff": metrics["aspect_diff"]})
    agree = [p for p in pairs if not p["problems"]]

    def rank(p):
        # official site first, then Brandfetch (scraped from the site), then Commons
        return ORIGINS.index(p["master"].split("/")[0]), not p["reference"].endswith(".svg"), p["beyond_pct"]

    best = min(agree, key=rank) if agree else None
    singles = [c["file"] for c in cands if c["kind"] == "svg" and not c["flags"] and not c["historical"]]
    if best:
        status = "agreeing pair"
    elif pairs:
        status = "no agreeing pair"
    elif singles:
        status = "single origin only"
    else:
        status = "no usable vector source"
    return {"candidates": cands, "pairs": sorted(pairs, key=lambda p: p["beyond_pct"]), "proposal": best,
            "status": status}


def accept(slugs):
    props = json.loads(PROPOSALS.read_text())
    rows = {}
    if SELECTION.exists():
        with open(SELECTION, encoding="utf-8") as f:
            rows = {r["slug"]: r for r in csv.DictReader(f)}
    for s in slugs:
        p = props[s]["proposal"]
        if not p:
            print("%s has no proposal. Add it to selection.csv by hand after review." % s)
            continue
        rows[s] = {"slug": s, "master": p["master"], "reference": p["reference"], "note": "reviewed proposal"}
    with open(SELECTION, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["slug", "master", "reference", "note"])
        w.writeheader()
        w.writerows(sorted(rows.values(), key=lambda r: r["slug"]))


def main(args):
    if args[:1] == ["--accept"]:
        return accept(args[1:])
    with open(ROOT / "register" / "brands.csv", encoding="utf-8") as f:
        slugs = [b["slug"] for b in csv.DictReader(f) if not args or b["slug"] in args]
    props = json.loads(PROPOSALS.read_text()) if PROPOSALS.exists() else {}
    for s in slugs:
        props[s] = score(s) if (SOURCES / s).exists() else {"status": "no sources downloaded", "proposal": None}
        p = props[s]["proposal"]
        detail = "%s vs %s (%.3f%%)" % (p["master"], p["reference"], p["beyond_pct"]) if p else ""
        print("%-16s %-24s %s" % (s, props[s]["status"], detail))
        PROPOSALS.write_text(json.dumps(props, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
