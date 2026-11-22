#!/usr/bin/env python3
"""Trace reference photos of one vehicle into clean vector outlines (side, front, rear, top).

For each view listed in vehicles/<slug>/vehicle.json:
  1. Separate the vehicle from the background with the rembg segmentation model (isnet-general-use).
  2. Keep the largest region, fill holes, and take its outer contour.
  3. Simplify the contour (Douglas-Peucker) and round it (Chaikin), then scale it to the cited
     dimensions in vehicles/references/<slug>/references.json.
  4. For the side view, find the two wheels (Hough circles in the lower body), unless the config
     gives them. For side, front and rear views, find glass as the dark region inside the upper body.
     For the rear view, find tail lamps as saturated red regions.

Writes vehicles/<slug>/outlines/<view>.svg (viewBox in millimetres) and outlines.json, plus
vehicles/<slug>/outlines/<view>_check.png overlays for review.

Usage:  python3 tools/vehicles/trace.py <slug>
"""
import functools
import sys

import cv2
import numpy as np
from PIL import Image

from common import VEHICLES, load_json, references, save_json

REMBG_MODEL = "isnet-general-use"


@functools.cache
def rembg_session():
    from rembg import new_session
    return new_session(REMBG_MODEL)


def segment(img_rgb):
    from rembg import remove
    rgba = np.array(remove(Image.fromarray(img_rgb), session=rembg_session()))
    return rgba[..., 3] > 128


def clean(mask):
    mask = mask.astype(np.uint8)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    if n <= 1:
        raise SystemExit("segmentation found nothing")
    keep = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    mask = (labels == keep).astype(np.uint8)
    # Fill holes: flood the background from the border, everything else is the vehicle.
    pad = np.pad(mask, 1)
    cv2.floodFill(pad, None, (0, 0), 2)
    holes = pad[1:-1, 1:-1] == 0
    mask[holes] = 1
    return mask.astype(bool)


def chaikin(pts, rounds=2):
    for _ in range(rounds):
        q = 0.75 * pts + 0.25 * np.roll(pts, -1, axis=0)
        r = 0.25 * pts + 0.75 * np.roll(pts, -1, axis=0)
        pts = np.stack([q, r], axis=1).reshape(-1, 2)
    return pts


def outline(mask, eps_frac=0.0015):
    cs, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)
    eps = eps_frac * cv2.arcLength(c, True)
    simp = cv2.approxPolyDP(c, eps, True)[:, 0, :].astype(float)
    return chaikin(simp, 2)


def detect_wheels(img_rgb, mask, x0, x1, y0, y1):
    """Two wheel circles in the lower part of the side silhouette."""
    h = y1 - y0
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    gray = cv2.medianBlur(gray, 5)
    band_top = y0 + int(0.45 * h)
    roi = gray[band_top:y1 + 1, x0:x1 + 1]
    circles = cv2.HoughCircles(roi, cv2.HOUGH_GRADIENT, dp=1.2, minDist=(x1 - x0) * 0.35,
                               param1=120, param2=30, minRadius=int(0.16 * h), maxRadius=int(0.30 * h))
    if circles is None:
        return None
    cs = [(float(cx + x0), float(cy + band_top), float(r)) for cx, cy, r in circles[0]]
    # Keep circles that touch the ground line area and sit inside the silhouette.
    cs = [c for c in cs if abs((c[1] + c[2]) - y1) < 0.12 * h and mask[int(c[1]), int(c[0])]]
    if len(cs) < 2:
        return None
    rear = min(cs, key=lambda c: c[0])
    front = max(cs, key=lambda c: c[0])
    if front[0] - rear[0] < 0.35 * (x1 - x0):
        return None
    return [rear, front]


def keep_components(mask, min_area, max_area):
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    keep = np.zeros(mask.shape, bool)
    for i in range(1, n):
        if min_area <= stats[i, cv2.CC_STAT_AREA] <= max_area:
            keep |= labels == i
    return keep


def dark_glass(img_rgb, mask, y0, y1, upper_frac):
    """Glass: the darker Otsu class of brightness inside the upper part of the silhouette.

    Returns nothing when the two classes are not clearly apart (a dark body colour), so the
    model then has no glass part rather than a wrong one.
    """
    v = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)[..., 2]
    inside = mask.copy()
    inside[int(y0 + upper_frac * (y1 - y0)):, :] = False
    vals = v[inside]
    if vals.size == 0:
        return np.zeros_like(mask)
    thr, _ = cv2.threshold(vals.reshape(-1, 1), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    dark, light = vals[vals <= thr], vals[vals > thr]
    if dark.size == 0 or light.size == 0 or light.mean() - dark.mean() < 40:
        return np.zeros_like(mask)
    glass = (inside & (v <= thr)).astype(np.uint8)
    glass = cv2.morphologyEx(glass, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    glass = cv2.morphologyEx(glass, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    return keep_components(glass, 0.004 * mask.sum(), 0.5 * inside.sum())


def red_lamps(img_rgb, mask):
    """Tail lamps: saturated red regions. Nothing when red covers the body (a red car)."""
    hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
    hue, sat, val = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    red = ((hue < 8) | (hue > 170)) & (sat > 110) & (val > 60) & mask
    if red.sum() > 0.15 * mask.sum():
        return np.zeros_like(mask)
    red = cv2.morphologyEx(red.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return keep_components(red, 0.002 * mask.sum(), 0.06 * mask.sum())


def polys(mask, to_mm, eps_frac=0.004):
    cs, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cs:
        if cv2.contourArea(c) < 20:
            continue
        simp = cv2.approxPolyDP(c, eps_frac * cv2.arcLength(c, True), True)[:, 0, :].astype(float)
        out.append([to_mm(p) for p in chaikin(simp, 1)])
    return out


def svg(path, width_mm, height_mm, body, extra, note):
    def d(poly):
        return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in poly) + " Z"
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width_mm:.0f} {height_mm:.0f}">',
             f"<!-- {note} -->",
             f'<path id="body" d="{d(body)}" fill="#eee8dc" stroke="#111112" stroke-width="6"/>']
    for name, ps in extra.items():
        color = {"glass": "#242427", "lamps": "#ff4b1f"}.get(name, "#888")
        for i, p in enumerate(ps):
            parts.append(f'<path id="{name}-{i}" d="{d(p)}" fill="{color}" stroke="none"/>')
    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n")


def trace(slug):
    cfg = load_json(VEHICLES / slug / "vehicle.json")
    refs = references(slug)
    dims = refs["dimensions"]
    L, W, H = dims["length_mm"], dims["width_mm"], dims["height_mm"]
    out_dir = VEHICLES / slug / "outlines"
    out_dir.mkdir(parents=True, exist_ok=True)
    result = {"slug": slug, "units": "mm", "segmentation": f"rembg {REMBG_MODEL}", "views": {}}
    by_view = {im["view"]: im for im in refs["images"]}
    for view, vc in cfg["views"].items():
        img = np.array(Image.open(VEHICLES / "references" / slug / by_view[view]["file"]).convert("RGB"))
        if vc.get("crop"):
            # Crop box [left, top, right, bottom] in pixels of the original photo, to leave out other vehicles.
            l, t, r, b = vc["crop"]
            img = img[t:b, l:r].copy()
        if vc.get("mirror"):
            img = img[:, ::-1].copy()
        mask = clean(segment(img))
        if vc.get("ground_crop"):
            # Cut off a shadow or kerb the segmenter kept below the tyres (fraction of image height).
            mask[int(vc["ground_crop"] * mask.shape[0]):, :] = False
            mask = clean(mask)
        ys, xs = np.nonzero(mask)
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        pw, ph = x1 - x0, y1 - y0
        if view == "side":
            sx, sy = L / pw, H / ph   # scaled to cited length and height
            width_mm = L
        elif view == "top":
            sx, sy = L / pw, W / ph
            width_mm = L
        else:
            sx = sy = H / ph          # uniform scale from cited height, width is checked not forced
            width_mm = pw * sx
        height_mm = ph * sy if view != "top" else W

        def to_mm(p, x0=x0, y1=y1, sx=sx, sy=sy):
            # x from the left edge, y up from the ground (top view: y across the width)
            return (float((p[0] - x0) * sx), float((y1 - p[1]) * sy))

        body = [to_mm(p) for p in outline(mask)]
        v = {"image": by_view[view]["file"], "pixels": [int(pw), int(ph)],
             "scale_mm_per_px": [round(sx, 4), round(sy, 4)], "body": body}
        extra = {}
        if view == "side":
            wheels = vc.get("wheels_px") or detect_wheels(img, mask, x0, x1, y0, y1)
            if wheels:
                v["wheels"] = [{"cx": (c[0] - x0) * sx, "cz": (y1 - c[1]) * sy, "r": c[2] * sy} for c in wheels]
                v["wheels_source"] = "config" if vc.get("wheels_px") else "hough circles"
                v["wheelbase_traced_mm"] = round(v["wheels"][1]["cx"] - v["wheels"][0]["cx"])
        if view in ("side", "front", "rear"):
            g = dark_glass(img, mask, y0, y1, vc.get("glass_upper_frac", 0.55))
            extra["glass"] = polys(g, to_mm)
        if view == "rear":
            extra["lamps"] = polys(red_lamps(img, mask), to_mm)
        if view in ("front", "rear"):
            v["traced_width_mm"] = round(width_mm)
            v["cited_width_mm"] = W
        v.update(extra)
        result["views"][view] = v
        svg_body = [(x, height_mm - y) for x, y in body]
        svg_extra = {k: [[(x, height_mm - y) for x, y in p] for p in ps] for k, ps in extra.items()}
        svg(out_dir / f"{view}.svg", width_mm, height_mm, svg_body, svg_extra,
            f"Traced from {by_view[view]['file']} by tools/vehicles/trace.py. Units mm, y down as in SVG.")
        # Review overlay: traced outline drawn back on the photo.
        chk = img.copy()
        cv2.polylines(chk, [np.array([[x0 + x / sx, y1 - y / sy] for x, y in body], np.int32)], True, (255, 75, 31), 3)
        for k, ps in extra.items():
            col = (60, 200, 255) if k == "glass" else (255, 255, 0)
            for p in ps:
                cv2.polylines(chk, [np.array([[x0 + x / sx, y1 - y / sy] for x, y in p], np.int32)], True, col, 2)
        for w in v.get("wheels", []):
            cv2.circle(chk, (int(x0 + w["cx"] / sx), int(y1 - w["cz"] / sy)), int(w["r"] / sy), (0, 255, 0), 3)
        Image.fromarray(chk).save(out_dir / f"{view}_check.png")
        print(view, "traced", len(body), "points", {k: len(p) for k, p in extra.items()},
              "wheels" if "wheels" in v else "", v.get("traced_width_mm", ""))
    save_json(out_dir / "outlines.json", result)


if __name__ == "__main__":
    trace(sys.argv[1])
