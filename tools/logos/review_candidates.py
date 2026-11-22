#!/usr/bin/env python3
"""Draw every source file for a set of brands on one sheet, for visual review.

One row per brand, one tile per downloaded file (Commons, Brandfetch, website),
labelled with origin and file name. The proposed master and reference, if any,
are outlined in green and blue. Output: logos/audit/_review/<name>.png

Usage:  python3 tools/logos/review_candidates.py <sheet-name> slug [slug ...]
"""
import json
import sys

from PIL import Image, ImageDraw

import audit as A
from common import ROOT, SOURCES, source_files

TILE, LABEL, PAD = 190, 28, 8


def tile_image(path):
    try:
        return A.artwork(path, 400)[0]
    except Exception:
        return None


def main(name, slugs):
    prop_path = ROOT / "logos" / "proposals.json"
    props = json.loads(prop_path.read_text()) if prop_path.exists() else {}
    rows = [(s, [SOURCES / s / rel for rel in source_files(s)]) for s in slugs]
    cols = max([len(f) for _, f in rows] + [1])
    W = 140 + cols * (TILE + PAD)
    H = len(rows) * (TILE + LABEL + PAD) + PAD
    sheet = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(sheet)
    for i, (s, files) in enumerate(rows):
        y = PAD + i * (TILE + LABEL + PAD)
        prop = (props.get(s) or {}).get("proposal") or {}
        d.text((8, y + TILE // 2), s, fill="black")
        d.text((8, y + TILE // 2 + 14), (props.get(s) or {}).get("status", ""), fill="#666666")
        for j, p in enumerate(files):
            x = 140 + j * (TILE + PAD)
            img = tile_image(p)
            board = A.backdrop_for(img, (TILE, TILE), square=10)
            if img is not None:
                img.thumbnail((TILE - 12, TILE - 12))
                board.paste(img, ((TILE - img.width) // 2, (TILE - img.height) // 2), img)
            sheet.paste(board, (x, y))
            rel = "%s/%s" % (p.parent.name, p.name)
            colour = "#00a000" if rel == prop.get("master") else "#0050d0" if rel == prop.get("reference") else None
            if colour:
                d.rectangle([x - 3, y - 3, x + TILE + 2, y + TILE + 2], outline=colour, width=3)
            d.text((x, y + TILE + 2), rel[:32], fill="black")
            d.text((x, y + TILE + 14), rel[32:64], fill="black")
    out = A.AUDIT / "_review"
    out.mkdir(parents=True, exist_ok=True)
    sheet.save(out / (name + ".png"))
    print(out / (name + ".png"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
