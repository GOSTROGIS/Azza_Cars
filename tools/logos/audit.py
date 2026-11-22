#!/usr/bin/env python3
"""Rebuild one brand's master SVG and audit it against an independent reference.

Inputs come from logos/selection.csv, one row per brand, chosen after visual review:
  slug, master (path under logos/sources/<slug>/), reference (same), note

Steps:
  1. Rebuild: the master SVG goes through svgo (pinned in package.json, config in
     svgo.config.mjs). Metadata and editor data are removed, colours become #rrggbb,
     and the viewBox is cropped to the artwork. Geometry is not edited by hand.
  2. Fidelity: master and rebuild are rendered with resvg and compared pixel by pixel.
  3. Agreement: the rebuild is compared with the reference from a different origin
     (shape IoU and colour difference after both are cropped and scaled alike).
  4. Colour audit: every fill, stroke and stop colour in the rebuild is listed and
     checked against the reference's colours and the Brandfetch palette.
  5. Evidence: renders, a diff heatmap, a comparison sheet and report.json are written
     to logos/audit/<slug>/. A passing rebuild is copied to logos/svg/<slug>.svg.

Usage:  python3 tools/logos/audit.py [slug ...]
"""
import csv
import io
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape

import defusedxml.ElementTree as ET
import numpy as np
import resvg_py
from PIL import Image, ImageDraw

from color_difference import delta_e_hex
from common import RASTER, ROOT, SOURCES, independent, load_prov

TOOLS = Path(__file__).resolve().parent
AUDIT = ROOT / "logos" / "audit"
FINAL = ROOT / "logos" / "svg"
SVGO = TOOLS / "node_modules" / ".bin" / "svgo"

RENDER_W = 1024          # render width used for the comparison sheet panels
ART_W = 2048             # comparisons render the artwork itself at this width, natively, no rescaling
FG_ALPHA = 128           # alpha at or above this counts as artwork
BG_DISTANCE = 60         # RGB distance from the border colour that counts as artwork in opaque rasters
MIN_COLOR_SHARE = 0.002  # a rendered colour must cover 0.2% of artwork pixels to count as a fill colour
PASS = {                 # thresholds a rebuild must meet to ship
    "fidelity_max_deviation_px": 1,         # master vs rebuild, at ART_W: edges may move by at most 1 px (0.05%)
    "agreement_tolerance_frac": 0.0015,     # rebuild vs independent vector reference: 0.15% of artwork width
    "agreement_raster_px": 1.5,             # a raster reference is trusted to 1.5 of its own pixels, if wider
    "agreement_max_outlier_pct": 0.01,      # share of artwork pixels allowed beyond that tolerance
    "agreement_max_aspect_diff": 0.01,      # relative difference in width/height ratio
    "max_flat_colors": 12,                  # more painted colours than this means gradients or shading
    "reversed_min_invisible_edge": 0.3,     # if this share of the artwork's edge vanishes on white, it is a dark-background variant
    "color_note_max_delta_e": 2.0,          # an unconfirmed colour within this CIEDE2000 distance of an independent one ships with a note
}
PASS_RESULT, FLAGGED, NOT_AUDITED = "pass", "flagged", "not audited"
COLOR_ATTRS = ("fill", "stroke", "stop-color", "color", "flood-color", "lighting-color")
HEX = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b")


# ---------- rendering and masks ----------

ROOT_TAG = re.compile(r"<svg\b(?:[^>\"']|\"[^\"]*\"|'[^']*')*>", re.S)


def set_root_attrs(svg_text, **attrs):
    """Replace (or add) attributes on the root <svg> element only, leaving the rest byte-identical.

    Text surgery rather than an XML round trip, because re-serializing renames unknown
    namespace prefixes. Handles single and double quotes. Pass None to remove an attribute.
    Use view_box= for viewBox.
    """
    tag = ROOT_TAG.search(svg_text).group(0)
    names = {("viewBox" if k == "view_box" else k): v for k, v in attrs.items()}
    new = tag
    for name in names:
        new = re.sub(r"\s%s\s*=\s*(\"[^\"]*\"|'[^']*')" % re.escape(name), "", new)
    added = "".join(' %s="%s"' % (k, v) for k, v in names.items() if v is not None)
    new = new[:4] + added + new[4:]
    return svg_text.replace(tag, new, 1)


def fmt(*vals):
    return " ".join(("%.4f" % v).rstrip("0").rstrip(".") for v in vals)


def sized(svg_text, width):
    """Exact pixel size on the root, proportional to the viewBox.

    resvg rounds an SVG's natural size to whole units before scaling, which distorts the
    aspect ratio of small viewBoxes. Giving the exact pixel size avoids that.
    """
    x, y, w, h = view_box(svg_text)
    return set_root_attrs(svg_text, view_box="%r %r %r %r" % (x, y, w, h), width=repr(float(width)),
                          height=repr(width * h / w))


def with_view_box(svg_text, vb):
    """Same SVG, viewed through another window."""
    return set_root_attrs(svg_text, view_box="%r %r %r %r" % tuple(vb), width=None, height=None)


def render_svg(svg_text, width=RENDER_W):
    png = resvg_py.svg_to_bytes(svg_string=sized(svg_text, width))
    return Image.open(io.BytesIO(bytes(png))).convert("RGBA")


def artwork(path, art_w=ART_W):
    """Cropped artwork of a source file, art_w pixels wide. Returns (image, native width).

    SVGs render natively at that width (native width None). Rasters are cropped and
    scaled. Returns (None, 0) for unsupported or empty files.
    """
    ext = path.suffix.lower()
    if ext == ".svg":
        return render_artwork(path.read_text(encoding="utf-8"), art_w), None
    if ext in RASTER:
        return raster_artwork(path, art_w)
    return None, 0


def checkerboard(size, square=12, dark=False):
    """RGB checkerboard used behind transparent artwork on review sheets (dark for reversed artwork)."""
    w, h = size
    tiles = ((np.indices((h, w)) // square).sum(axis=0) % 2).astype(bool)
    base, tile = (40, (60, 60, 60)) if dark else (255, (230, 230, 230))
    a = np.full((h, w, 3), base, dtype=np.uint8)
    a[tiles] = tile
    return Image.fromarray(a)


def is_reversed_image(img):
    """True for a variant made for dark backgrounds: much of its edge would vanish on a white page.

    The edge is every artwork pixel next to a non-artwork pixel (outer outline and holes such as
    letter counters). "Vanishes on white" is the same test the agreement check uses
    (on_white_mask), so the two can never disagree about what is visible. Light areas enclosed
    by darker artwork, like the white text in Peterbilt's oval, are not on the edge.
    """
    if img is None:
        return False
    art = artwork_mask(img)
    edge = art & dilate(~art)
    if not edge.any():
        return False
    invisible = edge & ~on_white_mask(img)
    return float(invisible.sum() / edge.sum()) >= PASS["reversed_min_invisible_edge"]


def backdrop_for(img, size, square=12):
    """Checkerboard that keeps the artwork visible: dark behind reversed (light-only) artwork."""
    return checkerboard(size, square, dark=is_reversed_image(img))


def artwork_mask(img):
    """Boolean mask of artwork pixels.

    When the image border is mostly opaque, the file has a solid background (an opaque
    raster, or an SVG with a full-size background rectangle), and artwork is whatever differs
    from the border colour. Otherwise artwork is what has alpha. Judging by the border rather
    than by the single most transparent pixel keeps one anti-aliased edge from flipping the mode.
    """
    a = np.asarray(img)
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    if np.median(border[:, 3]) < 250:
        return a[..., 3] >= FG_ALPHA
    return differs_from(a[..., :3], np.median(border[:, :3], axis=0))


def differs_from(rgb, background):
    """Pixels whose colour is more than BG_DISTANCE away from the background colour."""
    return np.linalg.norm(np.asarray(rgb, dtype=float) - background, axis=2) > BG_DISTANCE


def crop_to_artwork(img):
    m = artwork_mask(img)
    ys, xs = np.nonzero(m)
    if not len(xs):
        return img, None
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    return img.crop(box), box


# ---------- rebuild ----------

def svg_flags(text):
    flags = []
    if re.search(r"<image\b", text):
        flags.append("embedded raster image")
    if re.search(r"<text\b", text):
        flags.append("live text (depends on installed fonts)")
    if re.search(r"<(script|foreignObject)\b", text):
        flags.append("script or foreignObject")
    return flags


def view_box(text):
    root = ET.fromstring(text)
    vb = root.get("viewBox")
    if vb:
        return [float(v) for v in re.split(r"[\s,]+", vb.strip())]
    w, h = (float(re.sub(r"[a-z%]+$", "", root.get(k, "0"))) for k in ("width", "height"))
    return [0.0, 0.0, w, h]


def rebuild(master_text):
    """svgo pass, then crop the viewBox to the rendered artwork bounds."""
    out = subprocess.run([str(SVGO), "--config", str(TOOLS / "svgo.config.mjs"), "-i", "-", "-o", "-"],
                         input=master_text, capture_output=True, text=True, check=True).stdout
    x, y, w, h = view_box(out)
    probe = render_svg(out, 4096)
    ys, xs = np.nonzero(np.asarray(probe)[..., 3] > 0)  # any coverage at all, so no edge is clipped
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    scale = probe.width / w
    pad = 2 / scale  # two probe pixels of margin
    nx, ny = x + box[0] / scale - pad, y + box[1] / scale - pad
    nw, nh = (box[2] - box[0]) / scale + 2 * pad, (box[3] - box[1]) / scale + 2 * pad
    return set_root_attrs(out, view_box=fmt(nx, ny, nw, nh))


# ---------- comparisons ----------

def render_artwork(svg_text, art_w=ART_W):
    """Render so the artwork alone is art_w pixels wide, then crop to it."""
    probe = render_svg(svg_text, 512)  # only locates the artwork, the final render is exact
    _, box = crop_to_artwork(probe)
    full_w = min(round(art_w * probe.width / (box[2] - box[0])), 20000)
    return crop_to_artwork(render_svg(svg_text, full_w))[0]


def raster_artwork(path, art_w=ART_W):
    """Crop a raster reference to its artwork and scale it to art_w. Returns (image, native width)."""
    img, box = crop_to_artwork(Image.open(path).convert("RGBA"))
    if box is None:
        return None, 0
    native = img.width
    return img.resize((art_w, max(1, round(img.height * art_w / img.width))), Image.LANCZOS), native


def dilate(m):
    out = m.copy()
    out[1:] |= m[:-1]
    out[:-1] |= m[1:]
    out[:, 1:] |= m[:, :-1]
    out[:, :-1] |= m[:, 1:]
    return out


def deviation_map(ma, mb, max_px=16):
    """Per mismatched pixel, its distance in pixels (city-block, capped) to the other shape."""
    dist = np.zeros(ma.shape, dtype=np.int16)
    extra, missing = mb & ~ma, ma & ~mb
    grow_a, grow_b = ma.copy(), mb.copy()
    pending_extra, pending_missing = extra.copy(), missing.copy()
    for k in range(1, max_px + 1):
        grow_a, grow_b = dilate(grow_a), dilate(grow_b)
        hit = (pending_extra & grow_a) | (pending_missing & grow_b)
        dist[hit] = k
        pending_extra &= ~grow_a
        pending_missing &= ~grow_b
        if not (pending_extra.any() or pending_missing.any()):
            break
    dist[pending_extra | pending_missing] = max_px + 1
    return dist


def on_white_mask(img):
    """Pixels that would be visible on a white page: white areas count the same as transparent ones."""
    on_white = Image.alpha_composite(Image.new("RGBA", img.size, "white"), img.convert("RGBA"))
    return differs_from(np.asarray(on_white)[..., :3], 255)


def compare(a, b, tolerance, mask=artwork_mask):
    """Shape comparison of two artwork crops rendered at the same scale, using the given mask."""
    aspect_a, aspect_b = a.width / a.height, b.width / b.height
    if b.size != a.size:
        b = b.resize(a.size, Image.LANCZOS)
    ma, mb = mask(a), mask(b)
    dist = deviation_map(ma, mb, max_px=tolerance + 1)  # measure past the tolerance, so "too far" is always counted
    mism = dist > 0
    art = max(int((ma | mb).sum()), 1)
    beyond = dist > tolerance
    heat = np.zeros(ma.shape + (4,), dtype=np.uint8)
    heat[ma | mb] = (0, 0, 0, 40)        # faint outline of the artwork for orientation
    heat[mism] = (255, 170, 0, 255)
    heat[beyond] = (220, 0, 0, 255)
    worst = int(dist.max())
    return {"max_deviation_px": worst if worst <= tolerance else ">%d" % tolerance,
            "pixels_beyond_tolerance_pct": round(100 * float(beyond.sum()) / art, 4),
            "tolerance_px": tolerance,
            "iou": round(float((ma & mb).sum()) / art, 4),
            "aspect_a": round(aspect_a, 4), "aspect_b": round(aspect_b, 4),
            "aspect_diff": round(abs(aspect_a - aspect_b) / aspect_b, 4)}, Image.fromarray(heat), b


def agreement_verdict(rebuilt_art, ref_art, ref_native_w=None):
    """Compare a rebuild with an independent reference, both cropped to artwork at the same width.

    Tolerances are fractions of the artwork width, so the verdict is the same at any
    render size. The comparison basis follows from the reference: against a reversed
    (white) reference only the silhouette can be compared, otherwise both are compared
    as they look on a white page, which also treats painted white and transparent alike.
    Returns (metrics, problems, deviation heat map, scaled reference).
    """
    # a raster can only pin its shape, width and height to about one of its own pixels
    tol_frac, aspect_tol = PASS["agreement_tolerance_frac"], PASS["agreement_max_aspect_diff"]
    if ref_native_w:
        ref_native_h = ref_native_w * ref_art.height / ref_art.width
        tol_frac = max(tol_frac, PASS["agreement_raster_px"] / ref_native_w)
        aspect_tol = max(aspect_tol, PASS["agreement_raster_px"] * (1 / ref_native_w + 1 / ref_native_h))
    tol = max(1, int(np.ceil(tol_frac * rebuilt_art.width)))
    # a reversed reference can only confirm the silhouette, a positive one is compared as it looks on a white page
    basis, mask = (("silhouette", artwork_mask) if is_reversed_image(ref_art)
                   else ("appearance on white", on_white_mask))
    metrics, heat, ref_scaled = compare(rebuilt_art, ref_art, tol, mask)
    metrics["shape_basis"] = basis
    metrics["tolerance_frac_of_width"] = round(tol_frac, 5)
    metrics["reference_native_width_px"] = ref_native_w
    problems = []
    if metrics["pixels_beyond_tolerance_pct"] > PASS["agreement_max_outlier_pct"]:
        problems.append("shape disagrees with reference: %.3f%% of artwork beyond %.2f%% of width"
                        % (metrics["pixels_beyond_tolerance_pct"], 100 * tol_frac))
    metrics["aspect_tolerance"] = round(aspect_tol, 4)
    if metrics["aspect_diff"] > aspect_tol:
        problems.append("aspect ratio disagrees with reference (%.2f%%, tolerance %.2f%%)"
                        % (100 * metrics["aspect_diff"], 100 * aspect_tol))
    return metrics, problems, heat, ref_scaled


def rendered_colors(img):
    """Flat fill colours actually painted: exact opaque RGB values covering MIN_COLOR_SHARE of the artwork."""
    a = np.asarray(img)
    opaque = a[a[..., 3] == 255][:, :3]
    if not len(opaque):
        return {}
    packed = (opaque[:, 0].astype(np.uint32) << 16) | (opaque[:, 1].astype(np.uint32) << 8) | opaque[:, 2]
    vals, counts = np.unique(packed, return_counts=True)
    total = artwork_mask(img).sum()
    return {"#%06x" % v: round(float(c) / total, 4) for v, c in zip(vals, counts) if c / total >= MIN_COLOR_SHARE}


def svg_colors(text):
    found = set()
    root = ET.fromstring(text)
    for el in root.iter():
        for attr in COLOR_ATTRS:
            v = el.get(attr)
            if v and v.startswith("#"):
                found.add(v.lower())
        for decl in (el.get("style") or "").split(";"):
            if ":" in decl:
                k, v = (s.strip() for s in decl.split(":", 1))
                if k in COLOR_ATTRS and v.startswith("#"):
                    found.add(v.lower())
    for block in re.findall(r"<style[^>]*>(.*?)</style>", text, re.S):
        found.update(h.lower() for h in HEX.findall(block))
    return sorted(expand(c) for c in found)


def expand(c):
    return "#" + "".join(ch * 2 for ch in c[1:]) if len(c) == 4 else c


# ---------- evidence ----------

def sheet(slug, panels, lines, path):
    """Side-by-side panels on a checkerboard, with metric lines underneath."""
    cell = 300
    W, H = cell * len(panels) + 20 * (len(panels) + 1), cell + 60 + 16 * len(lines)
    canvas = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(canvas)
    for i, (title, img, dark) in enumerate(panels):
        x0 = 20 + i * (cell + 20)
        board = checkerboard((cell, cell), dark=dark)
        if img is not None:
            im = img.copy()
            im.thumbnail((cell - 10, cell - 10))
            board.paste(im, ((cell - im.width) // 2, (cell - im.height) // 2), im if im.mode == "RGBA" else None)
        canvas.paste(board, (x0, 30))
        d.text((x0, 10), title, fill="black")
    for j, line in enumerate(lines):
        d.text((20, cell + 40 + 16 * j), line, fill="black")
    canvas.save(path)


def audit(row, palette):
    slug = row["slug"]
    out_dir = AUDIT / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    master_path = SOURCES / slug / row["master"]
    ref_path = SOURCES / slug / row["reference"] if row["reference"] else None
    master_text = master_path.read_text(encoding="utf-8")
    report = {"slug": slug, "master": row["master"], "reference": row["reference"] or None,
              "note": row.get("note", ""), "thresholds": PASS, "flags": svg_flags(master_text)}

    rebuilt = rebuild(master_text)
    (out_dir / "rebuilt.svg").write_text(rebuilt, encoding="utf-8")
    report["flags"] += [f + " (after rebuild)" for f in svg_flags(rebuilt) if f not in report["flags"]]

    # 1. fidelity: master and rebuild share one coordinate system, so both are rendered
    #    through the rebuild's viewBox at the same pixel size and compared pixel for pixel.
    master_same_window = with_view_box(master_text, view_box(rebuilt))
    master_full, rebuilt_full = render_svg(master_same_window, ART_W), render_svg(rebuilt, ART_W)
    report["fidelity"], _, _ = compare(rebuilt_full, master_full, PASS["fidelity_max_deviation_px"])
    diff = np.abs(np.asarray(rebuilt_full, dtype=int) - np.asarray(master_full, dtype=int)).max(axis=2)
    report["fidelity"]["max_channel_diff"] = int(diff.max())
    report["fidelity"]["pixels_changed_pct"] = round(100 * float((diff > 0).mean()), 4)
    # rebuilt's viewBox is the artwork box, so these renders already show the artwork at ART_W
    master_art, rebuilt_art = crop_to_artwork(master_full)[0], crop_to_artwork(rebuilt_full)[0]
    reversed_master = report["fidelity"]["reversed_master"] = is_reversed_image(master_art)
    report["fidelity"]["colors_master"] = rendered_colors(master_art)
    report["fidelity"]["colors_rebuilt"] = rendered_colors(rebuilt_art)
    rebuilt_full.resize((RENDER_W, round(rebuilt_full.height * RENDER_W / rebuilt_full.width)),
                        Image.LANCZOS).save(out_dir / "rebuilt.png")

    # 2. agreement with an independent reference
    report["declared_colors_rebuilt"] = svg_colors(rebuilt)
    report["brandfetch_palette"] = sorted({c["hex"].lower() for c in palette})
    panels = [("master (source)", master_art, reversed_master), ("rebuilt", rebuilt_art, reversed_master)]
    ref_colors, agreement_problems = {}, ["no independent reference"]
    report["agreement"] = None
    if ref_path and not independent(row["master"], row["reference"]):
        agreement_problems = ["reference comes from the same origin as the master"]
    elif ref_path:
        ref_art, native = artwork(ref_path)
        if ref_art is None:
            agreement_problems = ["reference has no detectable artwork"]
        else:
            report["agreement"], agreement_problems, heat, ref_scaled = agreement_verdict(rebuilt_art, ref_art, native)
            ref_colors = report["agreement"]["colors_reference"] = rendered_colors(ref_scaled)
            heat.save(out_dir / "shape_diff.png")
            panels += [("reference (independent)", ref_scaled, is_reversed_image(ref_scaled)),
                       ("deviation: orange within tol, red beyond", heat, False)]

    # 3. colour audit on the rendered fills of the rebuild
    painted = report["fidelity"]["colors_rebuilt"]
    # a colour only counts as confirmed by a source from another origin than the master
    pools = [(name, colors) for name, src, colors in (("reference render", row["reference"], ref_colors),
                                                      ("brandfetch palette", "brandfetch/", report["brandfetch_palette"]))
             if src and independent(row["master"], src)]
    confirmed_by = report["color_audit"] = {c: [n for n, pool in pools if c in pool] for c in painted}
    # nearest independent colour for anything not matched exactly (owner rule: slightly off ships with a note)
    near = report["color_near_matches"] = {}
    unconfirmed = [c for c, srcs in confirmed_by.items() if not srcs]
    for c in unconfirmed:
        candidates = [(delta_e_hex(c, o), o, n) for n, pool in pools for o in pool]
        if candidates:
            de, other, src = min(candidates)
            near[c] = {"nearest": other, "source": src, "delta_e_2000": round(de, 3)}

    fails = []
    fid = report["fidelity"]
    if fid["pixels_beyond_tolerance_pct"] > 0:
        fails.append("rebuild moves edges by %s px vs master" % fid["max_deviation_px"])
    if set(fid["colors_master"]) != set(painted):
        fails.append("rebuild changed the fill colours")
    ag = report["agreement"]
    fails += agreement_problems
    if reversed_master:
        fails.append("master is a reversed (light-on-dark) variant, not the primary logo")
    if len(painted) > PASS["max_flat_colors"]:
        fails.append("%d flat colours: gradient or shading, needs manual colour review" % len(painted))
    slight = [c for c in unconfirmed if c in near and near[c]["delta_e_2000"] <= PASS["color_note_max_delta_e"]]
    off = [c for c in unconfirmed if c not in slight]

    def nearest(c):
        return "dE00 %.2f to %s" % (near[c]["delta_e_2000"], near[c]["nearest"]) if c in near else "none"

    if off:
        fails.append("fill colours not confirmed by an independent source: "
                     + ", ".join("%s (nearest %s)" % (c, nearest(c)) for c in off))
    fails += report["flags"]
    report["notes"] = [  # a pass can carry notes, which ship inside the SVG
        "colour not 100%% verified: %s matches %s (%s) only to CIEDE2000 %.2f, not exactly"
        % (c, near[c]["nearest"], near[c]["source"], near[c]["delta_e_2000"]) for c in slight]
    report["result"] = FLAGGED if fails else PASS_RESULT
    report["reasons"] = fails

    lines = ["%s: %s" % (slug, report["result"].upper())] + ["- " + f for f in fails] + [
        "fidelity (master vs rebuild): max edge shift %s px at %d px artwork width"
        % (fid["max_deviation_px"], ART_W),
        "agreement (rebuild vs reference): %s" % ("none" if not ag else json.dumps(
            {k: v for k, v in ag.items() if k != "colors_reference"})),
        "colours painted: %s" % ", ".join("%s %.1f%% [%s]" % (c, 100 * painted[c], ", ".join(confirmed_by[c]) or "UNCONFIRMED")
                                          for c in painted),
        "brandfetch palette: %s" % ", ".join(report["brandfetch_palette"])]
    sheet(slug, panels, lines, out_dir / "sheet.png")
    (out_dir / "report.json").write_text(json.dumps(report, indent=1))
    FINAL.mkdir(parents=True, exist_ok=True)
    if report["result"] == PASS_RESULT:
        (FINAL / (slug + ".svg")).write_text(with_notes(rebuilt, report["notes"]), encoding="utf-8")
    elif (FINAL / (slug + ".svg")).exists():
        (FINAL / (slug + ".svg")).unlink()
    return report


def with_notes(svg_text, notes):
    """Embed audit notes in the shipped SVG as <metadata>, so they travel with the file."""
    if not notes:
        return svg_text
    body = escape("Azza Cars logo audit notes: %s. Evidence in logos/audit/." % "; ".join(notes))
    tag = ROOT_TAG.search(svg_text).group(0)
    return svg_text.replace(tag, tag + "<metadata>" + body + "</metadata>", 1)


def write_status():
    """logos/STATUS.md: one line per register brand with its current audit outcome."""
    with open(ROOT / "register" / "brands.csv", encoding="utf-8") as f:
        brands = list(csv.DictReader(f))
    lines, counts = [], Counter()
    for b in brands:
        rp = AUDIT / b["slug"] / "report.json"
        r = json.loads(rp.read_text()) if rp.exists() else {"result": NOT_AUDITED, "reasons": []}
        notes = r.get("notes", [])
        shown = r["result"] + (", with note" if notes and r["result"] == PASS_RESULT else "")
        counts[shown] += 1
        link = "[svg](svg/%s.svg)" % b["slug"] if r["result"] == PASS_RESULT else ""
        why = "; ".join(r["reasons"] + notes).replace("|", "/")
        lines.append("| %s | %s | %s | %s |" % (b["name"], shown, link, why))
    summary = ". ".join("%s: %d" % (k.capitalize(), v) for k, v in sorted(counts.items())) + "."
    head = ["# Logo status", "", "Generated by `tools/logos/audit.py`. Do not edit by hand.", "",
            summary, "", "| Brand | Result | File | Reasons and notes |", "|---|---|---|---|"]
    (ROOT / "logos" / "STATUS.md").write_text("\n".join(head + lines) + "\n", encoding="utf-8")


def main(only):
    with open(ROOT / "logos" / "selection.csv", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if not only or r["slug"] in only]
    for row in rows:
        palette = load_prov(row["slug"]).get("brandfetch", {}).get("colors", [])
        try:
            r = audit(row, palette)
            print("%-16s %-8s %s" % (row["slug"], r["result"], "; ".join(r["reasons"])))
        except Exception as e:
            print("%-16s ERROR    %s: %s" % (row["slug"], type(e).__name__, e))
    write_status()


if __name__ == "__main__":
    main(set(sys.argv[1:]))
