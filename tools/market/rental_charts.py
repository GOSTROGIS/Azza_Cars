#!/usr/bin/env python3
"""Charts for the car sharing and rental tab of the plan (plan/RENTAL_PLAN.md).

Reads market/rental_stats.json (every figure there carries its source) and plan/rental_roadmap.json (a plan,
not data). Writes site/charts/rental-*.svg with the helpers and palette of tools/market/competition.py, so
the plan page inlines them and their hover titles work. A row with a "caveat" is drawn dashed and pale, and
the caveat is added to its hover title.

Usage:  python3 tools/market/rental_charts.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import competition as c  # noqa: E402
from competition import BONE, DISPLAY, GRID, INK, MUTED, ORANGE, ROOT, SURFACE, esc, save, svg_open, text  # noqa: E402

STATS = json.loads((ROOT / "market/rental_stats.json").read_text())
ROADMAPS = json.loads((ROOT / "plan/rental_roadmap.json").read_text())["roadmaps"]


def bar(r, fill, x, y, w, h, tip):
    """One rounded bar with a hover title. A caveated row is pale and dashed in its own colour."""
    style = f' fill-opacity="0.35" stroke="{fill}" stroke-dasharray="4 3"' if r.get("caveat") else ""
    tip += f'. {r["caveat"]}' if r.get("caveat") else ""
    return (f'<g><title>{esc(tip)}</title><rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 2):.1f}" height="{h:.1f}" '
            f'rx="4" fill="{fill}"{style}/></g>')


def trip_cost_chart():
    """One panel per standard trip, one bar per operator. A single series, so one fill and no legend."""
    tc = STATS["trip_costs"]
    W, L, R, rowh, head = 1000, 300, 90, 30, 34
    vmax = max(r["cad"] for r in tc["rows"]) * 1.05
    sx = lambda v: v / vmax * (W - L - R)
    y = 10
    body = []
    for trip in tc["trips"]:
        body.append(text(0, y + 18, trip["label"], weight=700, family=DISPLAY, size=14))
        y += head
        for r in sorted((r for r in tc["rows"] if r["trip"] == trip["key"]), key=lambda r: r["cad"]):
            w = sx(r["cad"])
            body.append(text(L - 12, y + 17, r["operator"], anchor="end"))
            body.append(bar(r, BONE, L, y + 4, w, rowh - 10, f'{r["operator"]}: C${r["cad"]:.2f} ({r["math"]})'))
            body.append(text(L + w + 8, y + 17, f"C${r['cad']:.2f}", fill=MUTED))
            y += rowh
        y += 14
    save("rental-trip-cost.svg", svg_open(W, y, "Cost of three standard trips by operator, published prices") + body)


def column_chart(rows, key, label, fname, fmt, fill=ORANGE):
    """Vertical columns for one series over time."""
    W, H, L, R, T, Bm = 1000, 360, 60, 20, 30, 50
    vmax = max(r[key] for r in rows) * 1.15
    bw = (W - L - R) / len(rows)
    sy = lambda v: H - Bm - v / vmax * (H - T - Bm)
    o = svg_open(W, H, label)
    o.append(f'<line x1="{L}" x2="{W - R}" y1="{sy(0)}" y2="{sy(0)}" stroke="{MUTED}" stroke-width="1"/>')
    for i, r in enumerate(rows):
        x, w = L + i * bw + bw * 0.18, bw * 0.64
        o.append(bar(r, fill, x, sy(r[key]), w, sy(0) - sy(r[key]), f'{r["label"]}: {fmt(r[key])}'))
        o.append(text(x + w / 2, sy(r[key]) - 8, fmt(r[key]), anchor="middle"))
        o.append(text(x + w / 2, H - Bm + 22, r["label"], anchor="middle", fill=MUTED))
    save(fname, o)


def roadmap_chart():
    W, L, R, rowh = 1000, 380, 20, 26
    m0, m1 = -6, 30
    sx = lambda m: L + (m - m0) / (m1 - m0) * (W - L - R)
    H = 40 + sum(len(r["phases"]) + 1 for r in ROADMAPS) * rowh + len(ROADMAPS) * 12
    o = svg_open(W, H, "Three roadmaps, in months from the first rental")
    for m in range(m0, m1 + 1, 6):
        o.append(f'<line x1="{sx(m):.1f}" x2="{sx(m):.1f}" y1="24" y2="{H - 4}" stroke="{GRID}"/>')
        o.append(text(sx(m), 16, "Launch" if m == 0 else f"{m:+d} mo", anchor="middle", fill=INK if m == 0 else MUTED))
    y = 34
    for rm in ROADMAPS:
        colour = getattr(c, rm["colour"])
        o.append(text(0, y + 17, rm["name"], weight=700, family=DISPLAY, size=14))
        y += rowh
        for m, g in rm["gates"]:
            o.append(f'<g><title>Gate at month {m}: {esc(g)}</title>'
                     f'<path d="M{sx(m):.1f},{y - 7} l7,7 l-7,7 l-7,-7 z" fill="{INK}" stroke="{SURFACE}" stroke-width="2"/></g>')
        for label, a, b in rm["phases"]:
            o.append(text(L - 12, y + 17, label, anchor="end", size=12.5))
            o.append(f'<g><title>{esc(rm["name"])}: {esc(label)}, month {a} to {b}</title>'
                     f'<rect x="{sx(a):.1f}" y="{y + 5}" width="{sx(b) - sx(a) - 2:.1f}" height="{rowh - 10}" rx="4" fill="{colour}"/></g>')
            y += rowh
        y += 12
    save("rental-roadmap.svg", o)


def main():
    trip_cost_chart()
    column_chart(STATS["canada_rental_revenue"]["rows"], "cad_b", "Canada automotive equipment rental and leasing revenue, C$ billion",
                 "rental-industry-revenue.svg", lambda v: f"C${v:.1f}B")
    column_chart([r | {"k": r["members"] / 1000} for r in STATS["canada_carshare"]["rows"]], "k",
                 "Canadian car-sharing members, thousands", "rental-carshare-members.svg", lambda v: f"{v:.0f}k", fill=BONE)
    column_chart(STATS["americas_rpd"]["rows"], "hertz", "Hertz Americas revenue per rental day, US$", "rental-rpd.svg",
                 lambda v: f"${v:.2f}", fill=BONE)
    column_chart(STATS["americas_utilisation"]["rows"], "hertz", "Hertz Americas vehicle utilisation", "rental-utilisation.svg",
                 lambda v: f"{v:.0f}%", fill=BONE)
    roadmap_chart()


if __name__ == "__main__":
    main()
