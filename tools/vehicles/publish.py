#!/usr/bin/env python3
"""Write each built vehicle's provenance.json and thumbnails, then vehicles/manifest.json for the site.

provenance.json records, per reference image, its source URL, author, licence, SHA-256 and what it was
used for, plus the cited dimensions with their sources, the trace scales and every build approximation.

Usage:  python3 tools/vehicles/publish.py
"""
import hashlib
import platform
from importlib.metadata import version

from PIL import Image

from common import ROOT, VEHICLES, load_json, references, save_json

THUMB_WIDTH = 480
USES = {
    "side": "traced side silhouette (scaled to cited length and height), wheel centres, side glass",
    "front": "traced front silhouette (across-length hull, tyre width and track), windscreen",
    "rear": "traced rear silhouette (across-length hull, tyre width and track), rear glass, tail lamps",
    "top": "traced plan silhouette",
}
STATEMENT = ("A recreation built from public photos and published dimensions. It is not factory CAD "
             "and is not identical to the real vehicle.")


def tool_versions():
    names = ["rembg", "opencv-python-headless", "numpy", "scipy", "scikit-image", "trimesh", "fast-simplification"]
    return {"python": platform.python_version(), **{n: version(n) for n in names}}


def publish():
    manifest = []
    tools = tool_versions()
    for cfg_path in sorted(VEHICLES.glob("*/vehicle.json")):
        slug = cfg_path.parent.name
        glb = cfg_path.parent / f"{slug}.glb"
        if slug.startswith("_") or not glb.exists():
            continue
        cfg = load_json(cfg_path)
        refs = references(slug)
        outlines = load_json(cfg_path.parent / "outlines" / "outlines.json")
        build = load_json(cfg_path.parent / "build.json")
        thumbs_dir = cfg_path.parent / "thumbs"
        thumbs_dir.mkdir(exist_ok=True)

        images = []
        for im in refs["images"]:
            src = VEHICLES / "references" / slug / im["file"]
            used = im["view"] in cfg["views"]
            entry = {**im, "sha256_local": hashlib.sha256(src.read_bytes()).hexdigest(),
                     "used_for": USES.get(im["view"], "not traced") if used else "not used in this build"}
            if used:
                vc = cfg["views"][im["view"]]
                entry["trace"] = {k: vc[k] for k in ("crop", "mirror", "ground_crop", "wheels_px") if k in vc}
                thumb = thumbs_dir / f"{im['view']}.jpg"
                with Image.open(src) as pic:
                    pic = pic.convert("RGB")
                    pic.thumbnail((THUMB_WIDTH, THUMB_WIDTH))
                    pic.save(thumb, quality=82)
                entry["thumb"] = str(thumb.relative_to(ROOT))
            images.append(entry)

        views = {v: {k: d[k] for k in d if k in ("image", "pixels", "scale_mm_per_px", "traced_width_mm",
                                                  "cited_width_mm", "wheels_source", "wheelbase_traced_mm")}
                 for v, d in outlines["views"].items()}
        save_json(cfg_path.parent / "provenance.json", {
            "slug": slug, "catalog_id": cfg["catalog_id"], "name": cfg["name"], "generation": cfg["generation"],
            "statement": STATEMENT, "dimensions": refs["dimensions"], "images": images,
            "trace": {"segmentation": outlines["segmentation"], "views": views},
            "build": build, "tools": tools, "glb": str(glb.relative_to(ROOT)),
            "glb_sha256": hashlib.sha256(glb.read_bytes()).hexdigest(),
        })
        manifest.append({
            "slug": slug, "catalog_id": cfg["catalog_id"], "name": cfg["name"], "short": cfg["short"],
            "generation": cfg["generation"], "glb": str(glb.relative_to(ROOT)),
            "approximations": build["approximations"],
            "references": [{"view": i["view"], "thumb": i["thumb"], "source": i.get("page_url") or i.get("url"),
                            "author": i.get("author"), "license": i.get("license")}
                           for i in images if "thumb" in i],
        })
    save_json(VEHICLES / "manifest.json", manifest)
    print("manifest:", [m["slug"] for m in manifest])


if __name__ == "__main__":
    publish()
