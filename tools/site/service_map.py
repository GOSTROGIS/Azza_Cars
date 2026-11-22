#!/usr/bin/env python3
"""Draw the website's service-area map from the CONSULTING repository's Metro Vancouver capture.

Reads (read only) from a local checkout of GOSTROGIS/CONSULTING:
  data/ca/bc/metro-vancouver/<member>/overture/segment.parquet    road centrelines (Overture, ODbL)
  data/ca/bc/metro-vancouver/<member>/overture/building.parquet   building footprints (Overture, ODbL)
  data/ca/bc/metro-vancouver/<member>/derived/building-attributes.parquet   use per building
and the municipality polygons in market/municipalities.geojson (this repository).

Writes site/public/service-area.svg (major roads as hairlines, mapped industrial buildings as ember
dots, municipal outlines) and site/public/service-area.json (counts, sources, hashes, attribution).

Usage:  python3 tools/site/service_map.py [/home/user/consulting]
"""
import json
import math
import sys
from pathlib import Path

import duckdb
from shapely import wkb
from shapely.geometry import shape

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "catalog"))
from common import sha256  # noqa: E402
OUT = ROOT / "site" / "public"
SERVICE = ["surrey", "delta", "white-rock", "langley-city", "langley-district"]
# Short map labels: (text, font size, nudge in px). Langley City sits inside the Township, so it is nudged down.
LABELS = {"surrey": ("SURREY", 22, (0, 0)), "delta": ("DELTA", 18, (0, 0)), "white-rock": ("WHITE ROCK", 11, (0, 16)),
          "langley-city": ("LANGLEY CITY", 10, (0, 22)), "langley-district": ("LANGLEY TOWNSHIP", 15, (-30, 40))}
ROADS = {"motorway": (1.6, 0.62), "trunk": (1.4, 0.55), "primary": (0.9, 0.34), "secondary": (0.55, 0.18)}
WIDTH = 1000
SIMPLIFY_DEG = 0.00012  # about 10 m, finer than one pixel at this scale
ATTRIBUTION = "© OpenStreetMap contributors, Overture Maps Foundation. Available under the Open Database License."


def main(consulting):
    mv = consulting / "data/ca/bc/metro-vancouver"
    munis = json.loads((ROOT / "market/municipalities.geojson").read_text())["features"]
    service = [f for f in munis if f["properties"]["slug"] in SERVICE]
    minx = min(shape(f["geometry"]).bounds[0] for f in service)
    miny = min(shape(f["geometry"]).bounds[1] for f in service)
    maxx = max(shape(f["geometry"]).bounds[2] for f in service)
    maxy = max(shape(f["geometry"]).bounds[3] for f in service)
    pad = 0.015
    minx, miny, maxx, maxy = minx - pad, miny - pad, maxx + pad, maxy + pad
    kx = math.cos(math.radians((miny + maxy) / 2))
    scale = WIDTH / ((maxx - minx) * kx)
    height = round((maxy - miny) * scale)

    def xy(lon, lat):
        return f"{(lon - minx) * kx * scale:.1f},{(maxy - lat) * scale:.1f}"

    def path(geom):
        geom = geom.simplify(SIMPLIFY_DEG)
        parts = []
        for line in getattr(geom, "geoms", [geom]):
            rings = [line.exterior, *line.interiors] if line.geom_type == "Polygon" else [line]
            for r in rings:
                pts = [xy(x, y) for x, y in r.coords]
                parts.append("M" + "L".join(pts) + ("Z" if line.geom_type == "Polygon" else ""))
        return "".join(parts)

    db = duckdb.connect()
    db.sql("load spatial")
    sources, counts = [], {}
    layers = {c: [] for c in ROADS}
    dots = []
    for m in SERVICE:
        seg = mv / m / "overture/segment.parquet"
        bld = mv / m / "overture/building.parquet"
        att = mv / m / "derived/building-attributes.parquet"
        for cls, geom in db.sql(f"""select class, ST_AsWKB(geometry) from '{seg}'
                                    where subtype = 'road' and class in ('motorway','trunk','primary','secondary')""").fetchall():
            layers[cls].append(path(wkb.loads(bytes(geom))))
        pts = db.sql(f"""select ST_X(ST_PointOnSurface(b.geometry)), ST_Y(ST_PointOnSurface(b.geometry))
                         from '{bld}' b join '{att}' a using (id) where a.use = 'industrial'""").fetchall()
        dots += pts
        counts[m] = len(pts)
        sources += [{"file": str(p.relative_to(consulting)), "sha256": sha256(p.read_bytes())} for p in (seg, bld, att)]

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" role="img" '
           f'aria-label="Service area: Surrey, Delta, White Rock and the Langleys, with major roads and mapped industrial buildings">',
           '<defs><filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2"/></filter></defs>',
           '<g fill="none" stroke="#3d3d42" stroke-width="0.8">']
    for f in munis:
        if f["properties"]["slug"] not in SERVICE:
            svg.append(f'<path d="{path(shape(f["geometry"]))}"/>')
    svg.append('</g><g fill="#161618">')
    for f in service:
        svg.append(f'<path d="{path(shape(f["geometry"]))}"/>')
    svg.append("</g>")
    for cls in ("secondary", "primary", "trunk", "motorway"):
        w, o = ROADS[cls]
        svg.append(f'<path fill="none" stroke="#eee8dc" stroke-width="{w}" stroke-opacity="{o}" stroke-linecap="round" d="{"".join(layers[cls])}"/>')
    dot_xy = [xy(x, y).split(",") for x, y in dots]
    svg.append('<g fill="#ff4b1f" filter="url(#glow)" opacity="0.55">' +
               "".join(f'<circle cx="{a}" cy="{b}" r="2.4"/>' for a, b in dot_xy) + "</g>")
    svg.append('<g fill="#ff8a66">' + "".join(f'<circle cx="{a}" cy="{b}" r="1"/>' for a, b in dot_xy) + "</g>")
    svg.append('<g fill="none" stroke="#cfc4ae" stroke-width="1" stroke-opacity="0.5" stroke-dasharray="4 3">')
    for f in service:
        svg.append(f'<path d="{path(shape(f["geometry"]))}"/>')
    svg.append("</g>")
    for f in service:
        text, size, (dx, dy) = LABELS[f["properties"]["slug"]]
        c = shape(f["geometry"]).centroid
        x, y = (float(v) for v in xy(c.x, c.y).split(","))
        svg.append(f'<text x="{x + dx:.0f}" y="{y + dy:.0f}" text-anchor="middle" font-family="Archivo, sans-serif" font-weight="800" '
                   f'font-size="{size}" letter-spacing="3" fill="#f7f4ee" stroke="#111112" stroke-width="5" paint-order="stroke">{text}</text>')
    svg.append("</svg>")
    (OUT / "service-area.svg").write_text("".join(svg) + "\n")

    release = json.loads((mv / "overture-manifest.json").read_text())["release"]
    (OUT / "service-area.json").write_text(json.dumps({
        "attribution": ATTRIBUTION, "overture_release": release,
        "source_repository": "GOSTROGIS/CONSULTING", "industrial_buildings": counts, "industrial_buildings_total": len(dots),
        "industrial_definition": "Overture buildings whose derived use is 'industrial' in the CONSULTING building-attributes layer. Volunteer and partner mapping: unmapped buildings are not counted.",
        "boundaries": "market/municipalities.geojson", "sources": sources,
    }, indent=1) + "\n")
    print("industrial buildings", counts, "total", len(dots), "svg bytes", (OUT / "service-area.svg").stat().st_size)


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "/home/user/consulting"))
