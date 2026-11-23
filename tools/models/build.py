#!/usr/bin/env python3
"""Build the model catalogue images: real open-licence photos with the background removed.

For each entry in tools/models/photos.json (chosen by hand from Wikimedia Commons):
  1. Read the 1920 px Commons thumbnail from the cache folder (<slug>.jpg plus <slug>.json sidecar),
     or download it when the cache has no copy.
  2. Remove the background with rembg, keep the largest region, clear listed boxes and fill listed
     glass polygons with a clean tint (the same steps as tools/hero/cutouts.py).
  3. Save a full-resolution PNG for download, a 900 px WebP for the catalogue grid and an 1800 px WebP for the detail view.
  4. For white, silver and light grey paint, save a paint mask: light, low-saturation pixels of the
     body, minus the tyres. The page multiplies a chosen colour into the masked paint, so shading and
     reflections stay from the real photo.

Writes site/public/models/<slug>.png, <slug>.webp, <slug>-detail.webp, <slug>-paint.png and models.json (photo credit,
licence, sales figure and its sources for each model).

Usage:  python3 tools/models/build.py <cache folder> [slug ...]
"""
import json
import sys
from urllib.parse import urlparse
from importlib.metadata import version
from pathlib import Path

import cv2
import numpy as np
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
RECOLOURABLE = {"white", "silver", "light grey", "light gray", "grey", "gray"}


def paint_mask(rgba, wheel_factor, panes):
    """Light, low-saturation body pixels, without the tyres or the listed glass, small holes (glare, badges) filled."""
    rgb, alpha = rgba[..., :3], rgba[..., 3]
    h, w = alpha.shape
    light = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)[..., 0] / 255.0
    sat = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)[..., 1] / 255.0
    mask = ((alpha > 200) & (light > 0.42) & (sat < 0.22)).astype(np.uint8) * 255
    grey = cv2.GaussianBlur(cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY), (5, 5), 0)
    circles = cv2.HoughCircles(grey, cv2.HOUGH_GRADIENT, dp=1.2, minDist=w // 4, param1=120, param2=40,
                               minRadius=h // 7, maxRadius=h // 3)
    for x, y, r in ([] if circles is None else circles[0][:2]):
        if y > h * 0.45:
            cv2.circle(mask, (int(x), int(y)), int(r * wheel_factor), 0, -1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    keep = np.isin(labels, [i for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] > h * w * 0.002]).astype(np.uint8) * 255
    holes = ((keep == 0) & (alpha > 200)).astype(np.uint8)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(holes, 8)
    keep[np.isin(labels, [i for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] < h * w * 0.004])] = 255
    # Pull the edge in by 2 px over bright pixels only (glass is darker), so paint meets glass and trim without a white fringe.
    keep = np.where((cv2.dilate(keep, np.ones((5, 5), np.uint8)) > 0) & (light > 0.60) & (alpha > 200), 255, keep).astype(np.uint8)
    # Glass is excluded by geometry, not by colour: a window reflecting a light sky passes the colour test.
    for pane in panes:
        cv2.fillPoly(keep, [np.array([[x * w, y * h] for x, y in pane["polygon"]], np.int32)], 0)
    return cv2.GaussianBlur(keep, (3, 3), 0)


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
        recolour = item.get("paint", "").lower() in RECOLOURABLE and not item.get("no_recolour")
        if recolour:
            # CSS masks read the alpha channel, so the mask is saved as white with the paint mask as its alpha.
            # Saved at the detail image size: the page stretches the mask over the image, so the full resolution is not needed.
            mask = cv2.resize(paint_mask(rgba, item.get("wheel_factor", 0.95), item.get("glass", [])), detail_size, interpolation=cv2.INTER_AREA)
            Image.fromarray(np.dstack([np.full_like(mask, 255), mask]), "LA").save(OUT / f"{item['slug']}-paint.png", optimize=True)
        # Each photo names the sales row it belongs to by make and model, exactly as in sales.json.
        ref = item["sales_ref"]
        sale = next((s for s in sales["models"] + sales["vans"] if (s["make"], s["model"]) == (ref["make"], ref["model"])), None)
        if sale is None:
            sys.exit(f"{item['slug']}: no sales.json row for {ref}")
        if item["license"] not in LICENCE_URL:
            sys.exit(f"{item['slug']}: no licence URL for {item['license']}: add it to LICENCE_URL")
        built[item["slug"]] = {k: item[k] for k in ("slug", "label", "vehicle_type", "commons_page", "original_url", "author", "license", "date_taken", "paint", "facing")} | got | {
            "sha256": sha256(raw), "png": f"{item['slug']}.png", "webp": f"{item['slug']}.webp", "detail": f"{item['slug']}-detail.webp",
            "license_url": LICENCE_URL[item["license"]], "size": list(full.size),
            "paint_mask": f"{item['slug']}-paint.png" if recolour else None,
            "sales": {k: v for k, v in sale.items() if k not in ("sources", "source_urls")} | {"sources": resolve_sources(sale, sales)}}
        print(item["slug"], full.size, "recolourable" if recolour else "")
    order = [p["slug"] for p in photos]
    index_path.write_text(json.dumps({
        "generated_utc": now(), "generator": "tools/models/build.py with tools/models/photos.json and tools/models/sales.json",
        "tools": {"rembg": version("rembg"), "model": MODEL},
        "models": [built[s] for s in order if s in built],
    }, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main(Path(sys.argv[1]), set(sys.argv[2:]))
