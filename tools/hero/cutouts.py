#!/usr/bin/env python3
"""Build the website hero cutouts: open-licence vehicle photos with the background removed.

For each entry in tools/hero/cutouts.json:
  1. Download a 1920 px thumbnail of the original from upload.wikimedia.org and record its SHA-256.
  2. Optional crop of the source (fractions of width and height) to leave out other vehicles.
  3. Remove the background with rembg (isnet-general-use) and keep the largest region.
  4. Clear any listed boxes (fractions of the cutout) that still hold fragments of other objects,
     keep the largest region again and crop to the vehicle.
  4b. Fill any listed glass polygons (fractions of the cutout) with a flat tint, so reflections of the
     photo's surroundings in a window do not read as dirt. The tint is sampled from clean glass on the
     same vehicle and recorded in cutouts.json.
  5. Resize to at most MAX_WIDTH and save WebP with alpha.

The fade into the page is a CSS mask on the site, not baked into the files.
Writes site/public/hero/<slug>.webp and site/public/hero/provenance.json.

Usage:  python3 tools/hero/cutouts.py [cache folder]
"""
import io
import json
import sys
from importlib.metadata import version
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "catalog"))
from common import get as fetch, now_utc as now, sha256  # noqa: E402  (retries on 429, 5xx and network errors)
OUT = ROOT / "site" / "public" / "hero"
CONFIG = Path(__file__).with_name("cutouts.json")
MODEL = "isnet-general-use"
MAX_WIDTH = 1200
# Wikimedia asks automated clients to fetch thumbnails in its standard widths, not originals.
THUMB_WIDTH = 1920
WEBP = {"quality": 60, "alpha_quality": 60, "method": 6}


def thumb_url(original):
    """The standard-width thumbnail of a Commons original: .../commons/a/ab/Name -> .../commons/thumb/a/ab/Name/1920px-Name."""
    head, name = original.rsplit("/", 1)
    return f"{head.replace('/commons/', '/commons/thumb/')}/{name}/{THUMB_WIDTH}px-{name}"


def largest_region(rgba):
    n, labels, stats, _ = cv2.connectedComponentsWithStats((rgba[..., 3] > 10).astype(np.uint8), 8)
    keep = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    rgba[..., 3] = np.where(labels == keep, rgba[..., 3], 0)
    ys, xs = np.nonzero(rgba[..., 3] > 10)
    return rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def boxes_cleared(rgba, boxes):
    h, w = rgba.shape[:2]
    for x0, y0, x1, y1 in boxes:
        rgba[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w), 3] = 0
    return largest_region(rgba)


def source(item, cache):
    """The photo bytes plus where and when they were downloaded.

    With a cache folder, <slug>.jpg is reused when its sidecar <slug>.json records the URL and
    retrieval time, and a fresh download is saved there with its sidecar.
    """
    jpg, meta = (cache / f"{item['slug']}.jpg", cache / f"{item['slug']}.json") if cache else (None, None)
    if jpg and jpg.exists() and meta.exists():
        return json.loads(meta.read_text()), jpg.read_bytes()
    got = {"url": thumb_url(item["original_url"])}
    raw = fetch(got["url"])
    got["retrieved_utc"] = now()
    if cache:
        cache.mkdir(parents=True, exist_ok=True)
        jpg.write_bytes(raw)
        meta.write_text(json.dumps(got) + "\n")
    return got, raw


def glass_filled(rgba, panes):
    h, w = rgba.shape[:2]
    for pane in panes:
        mask = np.zeros((h, w), np.uint8)
        cv2.fillPoly(mask, [np.array([[x * w, y * h] for x, y in pane["polygon"]], np.int32)], 255)
        soft = cv2.GaussianBlur(mask, (5, 5), 0)[..., None] / 255.0
        rgba[..., :3] = (rgba[..., :3] * (1 - soft) + np.array(pane["tint"]) * soft).astype(np.uint8)
    return rgba


def cutout(item, cache, session):
    """Steps 1 to 4b for one entry: (download record, source bytes, RGBA cutout at the working size)."""
    got, raw = source(item, cache)
    src = Image.open(io.BytesIO(raw)).convert("RGB")
    if src.width > THUMB_WIDTH:
        # Same working size whether the photo is an original or the thumbnail, so the clear boxes hold.
        src = src.resize((THUMB_WIDTH, round(src.height * THUMB_WIDTH / src.width)), Image.LANCZOS)
    if item.get("source_crop"):
        a, b, c, d = item["source_crop"]
        src = src.crop((int(a * src.width), int(b * src.height), int(c * src.width), int(d * src.height)))
    rgba = largest_region(np.array(remove(src, session=session, post_process_mask=True)))
    for boxes in item.get("clear_passes", []):
        rgba = boxes_cleared(rgba, boxes)
    return got, raw, glass_filled(rgba, item.get("glass", []))


def main(cache=None):
    cfg = json.loads(CONFIG.read_text())
    session = new_session(MODEL)
    OUT.mkdir(parents=True, exist_ok=True)
    images = []
    for item in cfg["images"]:
        got, raw, rgba = cutout(item, cache, session)
        out = Image.fromarray(rgba)
        if out.width > MAX_WIDTH:
            out = out.resize((MAX_WIDTH, round(out.height * MAX_WIDTH / out.width)), Image.LANCZOS)
        dst = OUT / f"{item['slug']}.webp"
        out.save(dst, "WEBP", **WEBP)
        images.append({k: item[k] for k in ("slug", "label", "vehicle_type", "commons_page", "original_url", "author", "license", "date_taken")}
                      | got | {"sha256": sha256(raw),
                         "bytes": len(raw), "file": dst.name})
        print(item["slug"], out.size, dst.stat().st_size, "bytes")
    prov = {
        "generated_utc": now(),
        "generator": "tools/hero/cutouts.py with tools/hero/cutouts.json",
        "tools": {"rembg": version("rembg"), "model": MODEL, "pillow": version("pillow")},
        "licence_note": "Each cutout is an adaptation of its source photo. CC BY-SA sources are shared under the same licence. Credit is shown on the page where the images appear.",
        "images": images,
    }
    (OUT / "provenance.json").write_text(json.dumps(prov, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    # Optional: a cache folder of <slug>.jpg photos with <slug>.json sidecars (url, retrieved_utc).
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
