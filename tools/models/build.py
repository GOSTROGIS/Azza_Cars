#!/usr/bin/env python3
"""Build the model catalogue images: real open-licence photos with the background removed.

For each entry in tools/models/photos.json (chosen by hand from Wikimedia Commons):
  1. Read the 1920 px Commons thumbnail from the cache folder (<slug>.jpg plus <slug>.json sidecar),
     or download it when the cache has no copy.
  2. Remove the background with rembg, keep the largest region, clear listed boxes and fill listed
     glass polygons with a clean tint (the same steps as tools/hero/cutouts.py).
  3. Save a full-resolution PNG for download, a 900 px WebP for the catalogue grid and an 1800 px WebP for the detail view.

Writes site/public/models/<slug>.png, <slug>.webp, <slug>-detail.webp and models.json: photo credit, licence, the
changes made to the photo (shown in the credit, as the licences require), sales figure and its sources, and the
catalog/ id the vehicle catalogue matches it to.

Usage:  python3 tools/models/build.py <cache folder> [slug ...]
"""
import json
import sys
from urllib.parse import urlparse
from importlib.metadata import version
from pathlib import Path

from PIL import Image
from rembg import new_session

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "hero"))
from cutouts import MODEL, cutout, now, sha256  # noqa: E402

HERE = Path(__file__).parent
OUT = ROOT / "site" / "public" / "models"
GRID_WIDTH = 900
DETAIL_WIDTH = 1800
WEBP = {"quality": 70, "alpha_quality": 70, "method": 6}
LICENCE_URL = {"CC BY 2.0": "https://creativecommons.org/licenses/by/2.0/", "CC BY 4.0": "https://creativecommons.org/licenses/by/4.0/",
               "CC BY-SA 2.0": "https://creativecommons.org/licenses/by-sa/2.0/", "CC BY-SA 3.0": "https://creativecommons.org/licenses/by-sa/3.0/",
               "CC BY-SA 4.0": "https://creativecommons.org/licenses/by-sa/4.0/", "CC0": "https://creativecommons.org/publicdomain/zero/1.0/"}


def modifications(item):
    """The changes made to the photo, from the steps cutout() runs for this item."""
    done = ["background removed"]
    if item.get("clear_passes"):
        done.append("stray objects removed")
    if item.get("glass"):
        done.append("windows tinted")
    return ", ".join(done)


def resolve_sources(sale, sales):
    """Turn a sales row's sources into [{name, url, note}] so the page only renders a list.

    Model rows cite source codes, sometimes followed by a note ("GCBC (consistent with ...)"). A source that
    starts with no known code is kept as plain text. Van rows cite URLs directly.
    """
    if "source_urls" in sale:
        return [{"name": urlparse(u).netloc.removeprefix("www."), "url": u} for u in sale["source_urls"]]
    codes = sorted(set(sales["source_urls"]) | set(sales["source_names"]), key=len, reverse=True)
    out = []
    for text in sale.get("sources", []):
        code = next((c for c in codes if text == c or text.startswith(c + " ")), None)
        if code is None:
            out.append({"name": text})
            continue
        note = text[len(code):].strip().removeprefix("(").removesuffix(")")
        out.append({"name": sales["source_names"].get(code, code), "url": sales["source_urls"].get(code)} | ({"note": note} if note else {}))
    return out


def main(cache, only):
    photos = json.loads((HERE / "photos.json").read_text())["images"]
    sales = json.loads((HERE / "sales.json").read_text())
    session = new_session(MODEL)
    OUT.mkdir(parents=True, exist_ok=True)
    index_path = OUT / "models.json"
    built = {m["slug"]: m for m in json.loads(index_path.read_text())["models"]} if index_path.exists() else {}
    for item in photos:
        if only and item["slug"] not in only:
            continue
        got, raw, rgba = cutout(item, cache, session)
        full = Image.fromarray(rgba)
        full.save(OUT / f"{item['slug']}.png", optimize=True)
        grid = full.resize((GRID_WIDTH, round(full.height * GRID_WIDTH / full.width)), Image.LANCZOS)
        grid.save(OUT / f"{item['slug']}.webp", "WEBP", **WEBP)
        detail_size = (min(DETAIL_WIDTH, full.width), round(full.height * min(DETAIL_WIDTH, full.width) / full.width))
        full.resize(detail_size, Image.LANCZOS).save(OUT / f"{item['slug']}-detail.webp", "WEBP", **WEBP)
        # Each photo names the sales row it belongs to by make and model, exactly as in sales.json.
        ref = item["sales_ref"]
        sale = next((s for s in sales["models"] + sales["vans"] if (s["make"], s["model"]) == (ref["make"], ref["model"])), None)
        if sale is None:
            sys.exit(f"{item['slug']}: no sales.json row for {ref}")
        if item["license"] not in LICENCE_URL:
            sys.exit(f"{item['slug']}: no licence URL for {item['license']}: add it to LICENCE_URL")
        built[item["slug"]] = {"catalog_id": item.get("catalog_id")} | {k: item[k] for k in ("slug", "label", "vehicle_type", "commons_page", "original_url", "author", "license", "date_taken")} | got | {
            "modifications": modifications(item),
            "sha256": sha256(raw), "png": f"{item['slug']}.png", "webp": f"{item['slug']}.webp", "detail": f"{item['slug']}-detail.webp",
            "license_url": LICENCE_URL[item["license"]], "size": list(full.size),
            "sales": {k: v for k, v in sale.items() if k not in ("sources", "source_urls")} | {"sources": resolve_sources(sale, sales)}}
        print(item["slug"], full.size)
    order = [p["slug"] for p in photos]
    index_path.write_text(json.dumps({
        "generated_utc": now(), "generator": "tools/models/build.py with tools/models/photos.json and tools/models/sales.json",
        "tools": {"rembg": version("rembg"), "model": MODEL},
        "models": [built[s] for s in order if s in built],
    }, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main(Path(sys.argv[1]), set(sys.argv[2:]))
