#!/usr/bin/env python3
"""Write vehicles/SELECTION.md: why these vehicles got 3D recreations, from the archived sales data.

US figures come from catalog/sources/sales_us/us_sales.json (automaker releases, each row with its
source URL, retrieval time, SHA-256 and quoted table line). Mexico figures come from the INEGI RAIAVL
extract already joined into catalog/models.json (mx_units_by_year).
"""
from common import ROOT, VEHICLES, load_json

US = load_json(ROOT / "catalog/sources/sales_us/us_sales.json")
MODELS = {m["id"]: m for m in load_json(ROOT / "catalog/models.json")}

CHOSEN = [
    ("ford-f150", "Ford F-150", "Ford", "F-Series"),
    ("toyota-rav4", "Toyota RAV4", "Toyota", "RAV4"),
    ("honda-crv", "Honda CR-V", "Honda", "CR-V"),
    ("toyota-camry", "Toyota Camry", "Toyota", "Camry"),
    ("nissan-rogue", "Nissan Rogue", "Nissan", "Rogue"),
    ("nissan-versa", "Nissan Versa", "Nissan", None),
]


def fmt(n):
    return f"{n:,}" if n is not None else "not available"


def main():
    rows = [r for r in US if r.get("units") is not None]
    missing = sorted({(r["make"], r["model"]) for r in US if r.get("units") is None})
    by = {}
    for r in rows:
        # "Ram pickup (Ram P/U)" and "Ram pickup (TOTAL Ram PU)" are the release's own row labels
        # for the same nameplate in different years, so group on the name before the label.
        by.setdefault((r["make"], r["model"].split(" (")[0]), {})[r["year"]] = r
    ranked = sorted(by.items(), key=lambda kv: -(kv[1].get(2024, {}).get("units") or 0))

    out = ["# Vehicle selection", "",
           "Which vehicles got 3D recreations first, and the data behind the choice.", "",
           "## Rule", "",
           "1. Rank the nameplates in the collected US sales data by 2024 calendar-year US sales.",
           "2. Take the top six, skipping the Ram pickup because a full-size pickup is already covered by the Ford F-150.",
           "3. Add the best-selling model in Mexico in 2025 according to INEGI RAIAVL, the Nissan Versa.", "",
           "The US figures only cover automakers whose year-end releases could be retrieved and archived.",
           "They are not a complete US ranking. See the gaps below.", "",
           "## US sales in the collected data", "",
           "| Rank (2024) | Make | Nameplate | 2024 | 2025 | Chosen |",
           "|---|---|---|---:|---:|---|"]
    chosen_us = {(make, name) for _, _, make, name in CHOSEN if name}
    for n, ((make, model), years) in enumerate(ranked, 1):
        mark = "yes" if (make, model) in chosen_us else ("skipped, pickup already covered" if make == "Ram" else "")
        out.append(f"| {n} | {make} | {model} | {fmt(years.get(2024, {}).get('units'))} | "
                   f"{fmt(years.get(2025, {}).get('units'))} | {mark} |")
    out += ["", "Notes on the US figures:", "",
            "- Ram's row label is \"Ram P/U\" in the 2024 chart and \"TOTAL Ram PU\" in the 2025 chart.",
            "- Ford reports the F-Series as one family, so its figure includes Super Duty trucks, not only the F-150.",
            "- In 2025 the Rogue fell behind the Tacoma, Corolla, Civic and Tucson in this data. It was chosen on the 2024 ranking.",
            "- Every figure, its source URL, retrieval time, SHA-256 and the quoted table line are in "
            "`catalog/sources/sales_us/us_sales.json`. The raw releases are archived in `catalog/sources/sales_us/raw/`.", "",
            "## Gaps", "",
            "These nameplates had no retrievable per-model US figure, so they could not be ranked:", ""]
    for make, model in missing:
        urls = next(r for r in US if (r["make"], r["model"]) == (make, model)).get("source_url")
        tried = ", ".join(urls) if isinstance(urls, list) else urls
        out.append(f"- {make} {model}. Tried: {tried}")
    out += ["", "GM's release pages and PDFs returned HTTP 403 to this network. Tesla publishes global deliveries, not US sales per model.", "",
            "## Mexico (INEGI RAIAVL, retail sales units)", "",
            "| Catalog id | 2023 | 2024 | 2025 |", "|---|---:|---:|---:|"]
    for slug, label, make, _ in CHOSEN:
        cid = slug.replace("-", "/", 1)
        mx = (MODELS.get(cid) or {}).get("mx_units_by_year") or {}
        out.append(f"| {cid} | {fmt(mx.get('2023'))} | {fmt(mx.get('2024'))} | {fmt(mx.get('2025'))} |")
    top = sorted(((m.get("mx_units_by_year") or {}).get("2025", 0), m["id"]) for m in MODELS.values())[-5:][::-1]
    out += ["", "Top five models in Mexico in 2025 in the INEGI data: " +
            ", ".join(f"{cid} ({fmt(u)})" for u, cid in top) + ".", "",
            "The F-150 and Rogue show no INEGI rows under those names. INEGI lists some sales under the "
            "selling company rather than the brand, see `catalog/README.md`.", ""]
    (VEHICLES / "SELECTION.md").write_text("\n".join(out))
    print("wrote", VEHICLES / "SELECTION.md")


if __name__ == "__main__":
    main()
