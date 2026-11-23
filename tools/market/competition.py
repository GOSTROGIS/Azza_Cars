#!/usr/bin/env python3
"""Competition index and plan charts for Metro Vancouver rental supply.

Reads (this repository):
  market/municipalities.csv       population, rental counts by category, business counts (build_market.py)
  market/municipalities.geojson   municipal polygons
  market/supply.geojson           every rental and dealer location, with category and brand

Method, per municipality:
  1. Rental supply is split by what it rents out: cars, consumer moving trucks (U-Haul) and commercial
     trucks and vans (every other truck rental outlet: Penske, Ryder, independents).
  2. Expected supply per kind is a logarithmic curve fitted across Metro municipalities by least squares:
       car outlets               = a + b * ln(residents)
       moving outlets            = a + b * ln(households)
       commercial truck outlets  = a + b * ln(trade businesses)   trade = NAICS 484 + 23 + 493 with employees
  3. The residual (actual minus expected) is divided by the fit's RMSE and clipped to [-2, 2].
  4. The competition index is the mean of the three scores. Above 0 means more outlets than the curve
     expects for a place of that size (competitive), below 0 means fewer (underserved).

Writes:
  market/competition.json            per-municipality scores, fits and gaps
  market/competition.geojson         polygons with the index and its colour, for SlipCurve GIS
  site/charts/*.svg                  map, three log-curve charts and the rental-mix chart

Usage:  python3 tools/market/competition.py
"""
import csv
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# Inlined into the plan page at build time (site/vite.config.js), so kept out of site/public.
OUT = ROOT / "site" / "charts"
BONE, BLOOD = "#eee8dc", "#a3220c"  # underserved, competitive
INK, MUTED, GRID, SURFACE = "#f7f4ee", "#9a958c", "#2a2a2e", "#111112"
FONT = "Inter, system-ui, sans-serif"
DISPLAY = "Archivo, Inter, sans-serif"
CATS = [("car_rental", "Car"), ("truck_rental", "Truck and van"), ("rv_rental", "RV"), ("carshare", "Car share")]
# What each outlet rents out, for the mix chart: truck rental is split into U-Haul (consumer moving) and the rest.
MIX = [("car_rental", "Car"), ("moving", "U-Haul moving"), ("commercial", "Commercial truck and van"), ("rv_rental", "RV"), ("carshare", "Car share")]
ORANGE, STEEL, SAND, STONE = "#ff4b1f", "#6f8fd0", "#b08a3a", "#8a847a"
CAT_FILL = {"car_rental": BONE, "moving": STONE, "commercial": ORANGE, "rv_rental": STEEL, "carshare": SAND}
SHORT = {"north-vancouver-city": "N. Van City", "north-vancouver-district": "N. Van District", "langley-district": "Langley Twp",
         "langley-city": "Langley City", "new-westminster": "New West", "port-coquitlam": "Port Coquitlam",
         "west-vancouver": "West Van", "mvrd-ea-a": "Electoral Area A", "pitt-meadows": "Pitt Meadows",
         "maple-ridge": "Maple Ridge", "port-moody": "Port Moody", "white-rock": "White Rock", "bowen-island": "Bowen Island"}


def num(v):
    return int(v) if str(v).strip() not in ("", "None") else 0


def name(slug):
    return SHORT.get(slug, slug.replace("-", " ").title())


# ---- colour: interpolate bone -> blood orange in OKLab ----
def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gam(c):
    c = c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
    return max(0, min(255, round(c * 255)))


def _oklab(h):
    r, g, b = (_lin(int(h[i:i + 2], 16)) for i in (1, 3, 5))
    l, m, s = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b, 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b,
               0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    l, m, s = (x ** (1 / 3) for x in (l, m, s))
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s, 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def _hex(L, a, b):
    l, m, s = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3, (L - 0.1055613458 * a - 0.0638541728 * b) ** 3, (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    r, g, bl = (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s, -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
                -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)
    return "#%02x%02x%02x" % (_gam(r), _gam(g), _gam(bl))


A, B = _oklab(BONE), _oklab(BLOOD)


def ramp(t):
    t = max(0.0, min(1.0, t))
    return _hex(*(A[i] + (B[i] - A[i]) * t for i in range(3)))


# The scores spread across about -1.25 to +1.25, so the ramp spans that range and both ends of it get used.
SPAN = 1.25


def colour(index):
    return ramp((index + SPAN) / (2 * SPAN))


# ---- fit ----
def logfit(pairs):
    xs = [math.log(x) for x, _ in pairs]
    ys = [y for _, y in pairs]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    a = my - b * mx
    pred = [a + b * x for x in xs]
    ss_res = sum((y - p) ** 2 for y, p in zip(ys, pred))
    ss_tot = sum((y - my) ** 2 for y in ys)
    return {"a": a, "b": b, "r2": 1 - ss_res / ss_tot, "rmse": math.sqrt(ss_res / n), "n": n}


def expected(fit, x):
    return max(0.0, fit["a"] + fit["b"] * math.log(x)) if x > 0 else 0.0


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;")


# ---- SVG helpers, shared with tools/market/rental_charts.py ----
def svg_open(w, h, label):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}" class="chart">']


def text(x, y, s, anchor="start", fill=INK, size=13, weight=400, family=FONT):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}">{esc(s)}</text>')


def save(name, o):
    o.append("</svg>")
    (OUT / name).write_text("".join(o) + "\n")


# ---- charts ----
def curve_chart(rows, key_x, key_y, fit, xlabel, ylabel, title, fname):
    W, H, L, R, T, Bm = 1000, 520, 70, 30, 30, 60
    xmax = max(r[key_x] for r in rows) * 1.08
    ymax = max(max(r[key_y] for r in rows), max(expected(fit, r[key_x]) for r in rows) + fit["rmse"]) * 1.12
    sx = lambda x: L + x / xmax * (W - L - R)
    sy = lambda y: H - Bm - y / ymax * (H - T - Bm)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)}" class="chart">']
    step = 10 ** math.floor(math.log10(ymax / 4))
    ystep = next(s * step for s in (1, 2, 5, 10) if ymax / (s * step) <= 6)
    for i in range(0, int(ymax / ystep) + 1):
        y = i * ystep
        o.append(f'<line x1="{L}" x2="{W - R}" y1="{sy(y):.1f}" y2="{sy(y):.1f}" stroke="{GRID}" stroke-width="1"/>'
                 f'<text x="{L - 10}" y="{sy(y) + 4:.1f}" text-anchor="end" font-family="{FONT}" font-size="13" fill="{MUTED}">{y:g}</text>')
    xstep = 10 ** math.floor(math.log10(xmax / 4))
    xstep = next(s * xstep for s in (1, 2, 5, 10) if xmax / (s * xstep) <= 7)
    i = 0
    while i * xstep <= xmax:
        x = i * xstep
        lab = f"{x / 1000:g}k" if x >= 1000 else f"{x:g}"
        o.append(f'<text x="{sx(x):.1f}" y="{H - Bm + 22}" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{MUTED}">{lab}</text>')
        i += 1
    o.append(f'<text x="{(L + W - R) / 2}" y="{H - 12}" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{MUTED}">{esc(xlabel)}</text>')
    o.append(f'<text x="18" y="{(T + H - Bm) / 2}" transform="rotate(-90 18 {(T + H - Bm) / 2})" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{MUTED}">{esc(ylabel)}</text>')
    # band and curve
    xs = [xmax * k / 200 for k in range(1, 201)]
    top = [(sx(x), sy(min(ymax, expected(fit, x) + fit["rmse"]))) for x in xs]
    bot = [(sx(x), sy(max(0, expected(fit, x) - fit["rmse"]))) for x in xs]
    o.append('<path d="M' + "L".join(f"{a:.1f},{b:.1f}" for a, b in top + bot[::-1]) + f'Z" fill="{INK}" fill-opacity="0.06"/>')
    o.append('<path d="M' + "L".join(f"{sx(x):.1f},{sy(expected(fit, x)):.1f}" for x in xs) + f'" fill="none" stroke="{INK}" stroke-width="2" stroke-opacity="0.7"/>')
    o.append(f'<line x1="{L}" x2="{W - R}" y1="{sy(0)}" y2="{sy(0)}" stroke="{MUTED}" stroke-width="1"/>')
    lx = sx(xmax * 0.97)
    o.append(f'<text x="{lx:.1f}" y="{sy(expected(fit, xmax * 0.97)) - 12:.1f}" text-anchor="end" font-family="{FONT}" font-size="13" fill="{INK}">'
             f'Expected: {fit["a"]:.1f} + {fit["b"]:.2f} ln x  (R² {fit["r2"]:.2f})</text>')
    score_key = key_y + "_score"
    labelled = sorted(rows, key=lambda r: -r[key_x])[:7] + [r for r in rows if abs(r[score_key]) >= 1.2]
    placed = [(lx - 7.2 * 44, sy(expected(fit, xmax * 0.97)) - 26, lx, sy(expected(fit, xmax * 0.97)) - 8)]
    placed += [(sx(r[key_x]) - 7, sy(r[key_y]) - 7, sx(r[key_x]) + 7, sy(r[key_y]) + 7) for r in rows]
    for r in sorted(rows, key=lambda r: r[key_x]):
        cx, cy = sx(r[key_x]), sy(r[key_y])
        tip = (f'{r["name"]}: {r[key_y]} outlets, curve expects {expected(fit, r[key_x]):.1f}. '
               f'{xlabel} {r[key_x]:,}. Score {r[score_key]:+.2f}')
        o.append(f'<g><title>{esc(tip)}</title><circle cx="{cx:.1f}" cy="{cy:.1f}" r="14" fill="transparent"/>'
                 f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6" fill="{colour(r[score_key])}" stroke="{SURFACE}" stroke-width="2"/></g>')
        if r in labelled:
            w = 7.2 * len(r["short"])
            for dx, dy, anchor in ((10, -9, "start"), (10, 18, "start"), (-10, -9, "end"), (-10, 18, "end")):
                x0 = cx + dx if anchor == "start" else cx + dx - w
                box = (x0, cy + dy - 12, x0 + w, cy + dy + 3)
                if box[2] < W - 4 and not any(box[0] < b[2] and b[0] < box[2] and box[1] < b[3] and b[1] < box[3] for b in placed):
                    placed.append(box)
                    o.append(f'<text x="{cx + dx:.1f}" y="{cy + dy:.1f}" text-anchor="{anchor}" font-family="{FONT}" font-size="13" fill="{INK}">{esc(r["short"])}</text>')
                    break
    o.append("</svg>")
    (OUT / fname).write_text("".join(o) + "\n")


def mix_chart(rows, fname):
    rows = [r for r in rows if r["mix_total"] > 0]
    rows.sort(key=lambda r: -r["mix_total"])
    W, rowh, L, R, T = 1000, 30, 170, 70, 46
    H = T + rowh * len(rows) + 16
    vmax = max(r["mix_total"] for r in rows)
    sx = lambda v: v / vmax * (W - L - R)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="Rental outlets by what they rent out" class="chart">']
    x = L
    for k, lab in MIX:
        o.append(f'<rect x="{x}" y="8" width="14" height="14" rx="3" fill="{CAT_FILL[k]}"/><text x="{x + 20}" y="20" font-family="{FONT}" font-size="13" fill="{INK}">{lab}</text>')
        x += 34 + len(lab) * 7.4
    for i, r in enumerate(rows):
        y = T + i * rowh
        o.append(f'<text x="{L - 12}" y="{y + 17}" text-anchor="end" font-family="{FONT}" font-size="13" fill="{INK}">{esc(r["short"])}</text>')
        x = L
        for k, lab in MIX:
            v = r["mix"][k]
            if not v:
                continue
            w = sx(v)
            o.append(f'<g><title>{esc(r["name"])}: {v} {lab.lower()} outlets</title>'
                     f'<rect x="{x:.1f}" y="{y + 4}" width="{max(w - 2, 1):.1f}" height="{rowh - 10}" rx="3" fill="{CAT_FILL[k]}"/></g>')
            x += w
        o.append(f'<text x="{x + 8:.1f}" y="{y + 17}" font-family="{FONT}" font-size="13" fill="{MUTED}">{r["mix_total"]}</text>')
    o.append("</svg>")
    (OUT / fname).write_text("".join(o) + "\n")


def map_chart(features, rows_by_slug, points, fname):
    from shapely.geometry import shape
    geoms = {f["properties"]["slug"]: shape(f["geometry"]) for f in features}
    # Frame the scored municipalities, so the unincorporated north does not fill the picture.
    framed = [g for k, g in geoms.items() if rows_by_slug.get(k, {}).get("scored")]
    minx = min(g.bounds[0] for g in framed) - 0.01; miny = min(g.bounds[1] for g in framed) - 0.01
    maxx = max(g.bounds[2] for g in framed) + 0.01; maxy = max(g.bounds[3] for g in framed) + 0.01
    kx = math.cos(math.radians((miny + maxy) / 2))
    W = 1000
    scale = W / ((maxx - minx) * kx)
    H = round((maxy - miny) * scale) + 60
    xy = lambda lon, lat: ((lon - minx) * kx * scale, (maxy - lat) * scale)

    def path(g):
        g = g.simplify(0.0004)
        parts = []
        for poly in getattr(g, "geoms", [g]):
            for ring in [poly.exterior, *poly.interiors]:
                parts.append("M" + "L".join("%.1f,%.1f" % xy(x, y) for x, y in ring.coords) + "Z")
        return "".join(parts)

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="Competition index by municipality" class="chart">',
         f'<defs><clipPath id="frame"><rect width="{W}" height="{H - 60}"/></clipPath></defs><g clip-path="url(#frame)">']
    for slug, g in geoms.items():
        r = rows_by_slug.get(slug)
        fill = colour(r["index"]) if r and r["scored"] else "#2a2a2e"
        tip = (f'{r["name"]}: index {r["index"]:+.2f}. {r["car_rental"]} car, {r["moving"]} U-Haul, {r["commercial"]} commercial truck outlets, '
               f'{r["population_2021"]:,} residents, {r["trade"]:,} trade businesses') if r and r["scored"] else (r["name"] if r else slug) + ": not scored"
        o.append(f'<g><title>{esc(tip)}</title><path d="{path(g)}" fill="{fill}" stroke="{SURFACE}" stroke-width="1.5"/></g>')
    o.append(f'<g fill="{SURFACE}" stroke="{INK}" stroke-width="0.8">')
    for p in points:
        x, y = xy(*p["xy"])
        if p["cat"] == "truck_rental":
            o.append(f'<rect x="{x - 2.5:.1f}" y="{y - 2.5:.1f}" width="5" height="5"><title>{esc(p["title"])}</title></rect>')
        else:
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6"><title>{esc(p["title"])}</title></circle>')
    o.append("</g></g>")
    for slug, g in geoms.items():
        r = rows_by_slug.get(slug)
        if not r or not r["scored"] or r["population_2021"] < 40000:
            continue
        c = g.representative_point()
        x, y = xy(c.x, c.y)
        o.append(f'<text x="{x:.0f}" y="{y:.0f}" text-anchor="middle" font-family="{DISPLAY}" font-weight="800" font-size="13" letter-spacing="1.5" '
                 f'fill="{SURFACE}" stroke="{INK}" stroke-width="3" paint-order="stroke">{esc(r["short"].upper())}</text>')
    # legend
    ly = H - 40
    for i in range(41):
        o.append(f'<rect x="{20 + i * 6}" y="{ly}" width="6" height="12" fill="{ramp(i / 40)}"/>')
    o.append(f'<text x="20" y="{ly + 30}" font-family="{FONT}" font-size="13" fill="{INK}">Underserved</text>'
             f'<text x="266" y="{ly + 30}" text-anchor="end" font-family="{FONT}" font-size="13" fill="{INK}">Competitive</text>'
             f'<circle cx="320" cy="{ly + 6}" r="3" fill="{SURFACE}" stroke="{INK}"/><text x="330" y="{ly + 10}" font-family="{FONT}" font-size="13" fill="{INK}">Car rental</text>'
             f'<rect x="420" y="{ly + 3}" width="6" height="6" fill="{SURFACE}" stroke="{INK}"/><text x="432" y="{ly + 10}" font-family="{FONT}" font-size="13" fill="{INK}">Truck and van rental</text>')
    o.append("</svg>")
    (OUT / fname).write_text("".join(o) + "\n")


def main():
    rows = list(csv.DictReader(open(ROOT / "market/municipalities.csv")))
    features = json.loads((ROOT / "market/municipalities.geojson").read_text())["features"]
    supply = json.loads((ROOT / "market/supply.geojson").read_text())["features"]
    rental = [f for f in supply if f["properties"]["counted"] and f["properties"]["category"] in dict(CATS)]
    mix = {}
    for f in rental:
        p = f["properties"]
        kind = p["category"]
        if kind == "truck_rental":
            kind = "moving" if p["brand"] == "U-Haul" else "commercial"
        mix.setdefault(p["muni"], Counter())[kind] += 1

    out = []
    for w in rows:
        r = {"slug": w["slug"], "name": w["name"], "short": name(w["slug"]), "population_2021": num(w["population_2021"]),
             "car_rental": num(w["car_rental"]), "truck_rental": num(w["truck_rental"]), "carshare": num(w["carshare"]),
             "households_2021": num(w["households_2021"]), "trade": num(w["bc_484"]) + num(w["bc_23"]) + num(w["bc_493"]),
             "stations_no_rental_2km": num(w["stations_no_rental_2km"])}
        r["mix"] = {k: mix.get(w["slug"], Counter())[k] for k, _ in MIX}
        r["mix_total"] = sum(r["mix"].values())
        r["moving"], r["commercial"] = r["mix"]["moving"], r["mix"]["commercial"]
        out.append(r)

    # Fit on municipalities of 10,000+ residents: the curve describes towns, not villages of a few hundred.
    # Electoral Area A (UBC and the unincorporated north shore wilderness) is not a municipality and is left out.
    fit_rows = [r for r in out if r["population_2021"] >= 10000 and r["trade"] > 0 and r["slug"] != "mvrd-ea-a"]
    KINDS = [("car_rental", "population_2021"), ("moving", "households_2021"), ("commercial", "trade")]
    fits = {k: logfit([(r[x], r[k]) for r in fit_rows]) for k, x in KINDS}
    for r in out:
        r["scored"] = r in fit_rows
        if not r["scored"]:
            r.update(index=0.0, **{f"{k}_score": 0.0 for k, _ in KINDS}, **{f"{k}_expected": None for k, _ in KINDS})
            continue
        for k, x in KINDS:
            r[f"{k}_expected"] = round(expected(fits[k], r[x]), 2)
            r[f"{k}_score"] = round(max(-2, min(2, (r[k] - r[f"{k}_expected"]) / fits[k]["rmse"])), 2)
        r["index"] = sum(r[f"{k}_score"] for k, _ in KINDS) / len(KINDS)
        gaps = []
        if r["car_rental"] == 0:
            gaps.append("no car rental")
        if r["truck_rental"] == 0:
            gaps.append("no truck or van rental")
        elif r["commercial"] == 0:
            gaps.append("no commercial truck or van rental")
        trucks = r["moving"] + r["commercial"]
        if trucks >= 3 and r["moving"] / trucks >= 0.8:
            gaps.append(f"truck supply is {r['moving']} of {trucks} U-Haul")
        if r["carshare"] == 0 and r["population_2021"] >= 100000:
            gaps.append("no car share")
        if r["stations_no_rental_2km"]:
            gaps.append(f"{r['stations_no_rental_2km']} rapid transit station(s) with no rental within 2 km")
        r["gaps"] = gaps
        r["colour"] = colour(r["index"])
        r["index"] = round(r["index"], 2)

    OUT.mkdir(parents=True, exist_ok=True)
    curve_chart(fit_rows, "population_2021", "car_rental", fits["car_rental"], "Residents (2021 census)", "Car rental outlets",
                "Car rental outlets against residents, with the fitted logarithmic curve", "curve-car.svg")
    curve_chart(fit_rows, "households_2021", "moving", fits["moving"], "Households (2021 census)", "U-Haul outlets",
                "Consumer moving outlets against households, with the fitted logarithmic curve", "curve-moving.svg")
    curve_chart(fit_rows, "trade", "commercial", fits["commercial"], "Trucking, construction and warehousing businesses", "Commercial truck and van outlets",
                "Commercial truck and van outlets against trade businesses, with the fitted logarithmic curve", "curve-commercial.svg")
    mix_chart(out, "rental-mix.svg")
    by_slug = {r["slug"]: r for r in out}
    pts = [{"cat": f["properties"]["category"], "xy": f["geometry"]["coordinates"],
            "title": f'{f["properties"]["name"]} ({dict(CATS)[f["properties"]["category"]].lower()} rental)'}
           for f in rental if f["properties"]["category"] in ("car_rental", "truck_rental")]
    map_chart(features, by_slug, pts, "competition-map.svg")

    gj = {"type": "FeatureCollection", "features": []}
    for f in features:
        r = by_slug.get(f["properties"]["slug"])
        if not r:
            continue
        gj["features"].append({"type": "Feature", "geometry": f["geometry"], "properties": {
            "slug": r["slug"], "name": r["name"], "index": r["index"] if r["scored"] else None,
            "car_scr": r["car_rental_score"] if r["scored"] else None, "mov_scr": r["moving_score"] if r["scored"] else None,
            "com_scr": r["commercial_score"] if r["scored"] else None,
            "car": r["car_rental"], "car_exp": r["car_rental_expected"], "moving": r["moving"], "mov_exp": r["moving_expected"],
            "comm": r["commercial"], "com_exp": r["commercial_expected"],
            "pop21": r["population_2021"], "trade": r["trade"], "colour": r.get("colour"), "gaps": "; ".join(r.get("gaps", []))}})
    (ROOT / "market/competition.geojson").write_text(json.dumps(gj) + "\n")

    fits = {k: {"a": round(v["a"], 3), "b": round(v["b"], 3), "r2": round(v["r2"], 3), "rmse": round(v["rmse"], 3), "n": v["n"]}
            for k, v in (("car_rental_vs_ln_residents", fits["car_rental"]), ("uhaul_moving_vs_ln_households", fits["moving"]),
                         ("commercial_truck_van_vs_ln_trade_businesses", fits["commercial"]))}
    (ROOT / "market/competition.json").write_text(json.dumps({
        "generator": "tools/market/competition.py",
        "inputs": ["market/municipalities.csv", "market/municipalities.geojson", "market/supply.geojson"],
        "method": "Expected outlets from a least-squares fit of outlets = a + b ln(x) over municipalities of 10,000+ residents. "
                  "Score = (actual - expected) / RMSE, clipped to [-2, 2]. Index = mean of the car, moving and commercial truck scores.",
        "fits": fits, "colours": {"underserved": BONE, "competitive": BLOOD},
        "municipalities": sorted(out, key=lambda r: r["index"]),
    }, indent=1) + "\n")
    print(json.dumps(fits, indent=1))
    for r in sorted([r for r in out if r["scored"]], key=lambda r: r["index"]):
        print(f'{r["slug"]:26} idx {r["index"]:+.2f} car {r["car_rental"]:3}/{r["car_rental_expected"]:5.1f} mov {r["moving"]:3}/{r["moving_expected"]:5.1f} com {r["commercial"]:3}/{r["commercial_expected"]:5.1f}  {"; ".join(r["gaps"])}')


if __name__ == "__main__":
    main()
