"""Unaudited brand logos for catalogue brands that have no audited logo in logos/svg/.

Owner's decision (2026-11-24): logos taken from the manufacturers' own websites, backgrounds
removed, are good enough for the catalogue where the audit has not passed a logo.

Each pick below was chosen by eye from a contact sheet of every downloaded candidate.
Sources are the files already captured from each brand's website, either directly
(origin "website") or through Brandfetch, which collects them from the brand's own site
(origin "brandfetch"). Wikimedia Commons files are not used. logos/ is only read.

Processing, and nothing else:
  SVG: scripts and foreignObject elements are dropped. Backgrounds are already transparent.
  Raster: if the four corners share one colour, pixels connected to the edge within a small
          tolerance of it become transparent. The image is then trimmed to its content.
ON_DARK lists logos drawn in white or light colours: the site shows them on a dark chip
instead of recolouring them. The flags are hand-set from the same contact sheet, not computed
with tools/logos/audit.py, so this script does not depend on the audit's renderer.

Writes catalog/logos/<slug>.svg or .png and catalog/logos/index.json.
Usage: python3 tools/catalog/fallback_logos.py
"""
import io
import json
import re

import numpy as np
from PIL import Image
from scipy import ndimage

from common import CATALOG, ROOT, sha256

OUT = CATALOG / "logos"
SRC_AUDIT = ROOT / "logos" / "sources"       # read only
SRC_OWN = OUT / "sources"                    # captures made for this folder

# slug: source file, relative to the brand's source folder
PICKS = {
    "alfa-romeo": "brandfetch/logo-dark.png", "aston-martin": "brandfetch/logo-dark.svg", "audi": "brandfetch/logo-light.svg",
    "bentley": "brandfetch/logo-dark.png", "bugatti": "brandfetch/logo-dark.svg", "buick": "brandfetch/logo-dark.png",
    "cadillac": "brandfetch/logo-dark.svg", "chevrolet": "brandfetch/logo-dark.svg", "dodge": "brandfetch/logo-light.svg",
    "ferrari": "brandfetch/logo-dark.svg", "fiat": "brandfetch/logo-dark.svg", "ford": "brandfetch/logo-dark.svg",
    "genesis": "brandfetch/logo-light.png", "gmc": "brandfetch/logo-dark.png", "honda": "brandfetch/logo-dark.svg",
    "hyundai": "brandfetch/logo-dark.svg", "infiniti": "brandfetch/logo-dark.svg", "ineos": "website/logo-1.svg",
    "jeep": "brandfetch/logo-dark.svg", "kia": "brandfetch/logo-dark.svg", "koenigsegg": "brandfetch/logo-dark.svg",
    "lamborghini": "brandfetch/logo-dark.svg", "lexus": "brandfetch/logo-dark.svg", "lincoln": "brandfetch/logo-dark.svg",
    "lotus": "brandfetch/logo-light.svg", "lucid": "brandfetch/logo-dark.svg", "maserati": "brandfetch/logo-dark.svg",
    "mazda": "brandfetch/logo-dark.svg", "mclaren": "brandfetch/logo-dark.svg", "mercedes-benz": "brandfetch/logo-dark.svg",
    "mitsubishi": "website/logo-2.svg", "morgan": "brandfetch/logo-light.svg", "polestar": "brandfetch/logo-dark.svg",
    "porsche": "brandfetch/logo-dark.svg", "ram": "brandfetch/logo-dark.png", "rimac": "brandfetch/logo-dark.svg",
    "rolls-royce": "brandfetch/logo-dark.svg", "subaru": "website/logo-2.jpg", "tesla": "brandfetch/logo-dark.svg",
    "toyota": "website/logo-1.svg", "scion": "website/logo-3.svg", "vinfast": "brandfetch/logo-dark.svg",
    "volkswagen": "brandfetch/logo-dark.svg", "volvo": "brandfetch/logo-dark.svg", "scout": "website/logo-1.svg",
    "slate": "brandfetch/logo-dark.svg", "czinger": "website/logo-1.svg", "saleen": "brandfetch/logo-dark.svg",
    "ssc": "brandfetch/logo-dark.png", "glickenhaus": "brandfetch/logo-light.png", "mahindra": "brandfetch/logo-dark.svg",
    "zeekr": "brandfetch/logo-dark.svg", "byd": "website/logo-1.svg", "kandi": "brandfetch/logo-dark.png",
    "karma": "website/logo-1.png", "lordstown": "brandfetch/logo-dark.svg", "cupra": "website/logo-1.svg",
    "peugeot": "website/logo-2.png", "renault": "website/logo-1.svg", "suzuki": "brandfetch/logo-dark.svg",
    "mg": "website/logo-1.svg", "chirey": "website/logo-1.svg", "jaecoo": "brandfetch/logo-dark.svg",
    "gwm": "brandfetch/logo-dark.png", "changan": "brandfetch/logo-light.png", "geely": "brandfetch/logo-dark.svg",
    "lynk-co": "brandfetch/logo-dark.svg", "leapmotor": "brandfetch/logo-dark.svg", "jetour": "brandfetch/logo-dark.svg",
    "soueast": "brandfetch/logo-dark.png", "baic": "brandfetch/logo-dark.png", "dfsk": "website/logo-1.png",
    "jmc": "brandfetch/logo-dark.png", "seres": "brandfetch/logo-dark.svg", "daihatsu": "brandfetch/logo-dark.svg",
    "smart": "brandfetch/logo-dark.svg", "lada": "brandfetch/logo-light.svg", "checker": "website/logo-1.png",
    "holden": "brandfetch/logo-dark.png", "panoz": "website/logo-1.png", "shelby": "website/logo-1.png",
    "spyker": "brandfetch/logo-light.svg", "freightliner": "website/logo-1.svg", "western-star": "website/logo-1.png",
    "peterbilt": "website/logo-1.svg", "kenworth": "brandfetch/logo-dark.png", "mack": "website/logo-1.svg",
    "international": "brandfetch/logo-dark.svg", "hino": "website/logo-1.svg", "fuso": "brandfetch/logo-dark.svg",
    "autocar": "website/logo-1.png", "oshkosh": "website/logo-1.png", "workhorse": "brandfetch/logo-dark.png",
    "nikola": "brandfetch/logo-dark.svg", "xos": "brandfetch/logo-dark.svg", "lion": "website/logo-1.png",
    "dina": "website/logo-4.svg", "jac": "website/logo-1.png", "lancia": "website/logo-1.jpg",
}
# Logos in white or light colours, shown on a dark chip.
ON_DARK = {
    "audi", "byd", "changan", "cupra", "czinger", "dfsk", "dodge", "genesis", "ineos", "jac",
    "karma", "lada", "lotus", "morgan", "peugeot", "renault", "spyker", "western-star",
}
# Brands whose file sits in another brand's source folder.
SOURCE_BRAND = {"scion": "toyota"}  # the Scion badge served on toyota.com
# Brands whose solid edge colour is part of the logo, not a background.
KEEP_EDGE = {"kenworth"}

CORNER_TOL = 24   # corners within this of each other (per channel) count as one background colour
FILL_TOL = 40     # edge-connected pixels within this of that colour become transparent
MAX_WIDTH = 600


def provenance(folder, rel):
    """The provenance.json entry for one file. Also covers catalog/logos/sources, which
    tools/logos/common.load_prov (fixed to logos/sources) cannot read."""
    origin = rel.split("/")[0]
    block = json.loads((folder / "provenance.json").read_text()).get(origin, {})
    f = next((f for f in block.get("files", []) if f["saved_as"] == rel), {})
    return {"origin": origin, "url": f.get("src") or f.get("url_unsigned") or block.get("page_requested"),
            "page": block.get("page_requested") or block.get("domain"),
            "retrieved_utc": f.get("retrieved_utc") or block.get("retrieved_utc"), "sha256": f.get("sha256")}


def clean_svg(text):
    return re.sub(r"<(script|foreignObject)\b.*?</\1>", "", text, flags=re.S | re.I)


def clear_edge_background(im):
    """Make the uniform background connected to the image edge transparent.
    Returns the image, the number of pixels cleared and the background colour."""
    a = np.asarray(im).copy()
    corners = a[[0, 0, -1, -1], [0, -1, 0, -1]].astype(int)
    if (corners[:, 3] <= 250).any() or np.ptp(corners[:, :3], axis=0).max() > CORNER_TOL:
        return im, 0, None
    near = (np.abs(a[..., :3].astype(int) - corners[0, :3]).max(-1) <= FILL_TOL) & (a[..., 3] > 0)
    labels, _ = ndimage.label(near)
    edge = np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))
    mask = np.isin(labels, edge[edge > 0])
    a[mask, 3] = 0
    return Image.fromarray(a), int(mask.sum()), corners[0]


def clean_raster(path, keep_edge):
    im = Image.open(path).convert("RGBA")
    steps = []
    if not keep_edge:
        im, cleared, r = clear_edge_background(im)
        if cleared:
            steps.append(f"background #{r[0]:02x}{r[1]:02x}{r[2]:02x} removed from {cleared} edge-connected pixels")
    box = im.getbbox()
    if box and box != (0, 0, *im.size):
        im = im.crop(box)
        steps.append("trimmed to content")
    if im.width > MAX_WIDTH:
        im = im.resize((MAX_WIDTH, round(im.height * MAX_WIDTH / im.width)), Image.LANCZOS)
        steps.append(f"scaled to {MAX_WIDTH} px wide")
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return buf.getvalue(), steps


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    index = {}
    for slug, rel in sorted(PICKS.items()):
        brand_dir = SOURCE_BRAND.get(slug, slug)
        folder = SRC_OWN / brand_dir if (SRC_OWN / brand_dir / rel).exists() else SRC_AUDIT / brand_dir
        src = folder / rel
        if src.suffix == ".svg":
            text = src.read_text()
            cleaned = clean_svg(text)
            data, ext = cleaned.encode(), ".svg"
            steps = ["script or foreignObject removed"] if cleaned != text else []
        else:
            (data, steps), ext = clean_raster(src, slug in KEEP_EDGE), ".png"
        dst = OUT / f"{slug}{ext}"
        dst.write_bytes(data)
        (OUT / f"{slug}{'.png' if ext == '.svg' else '.svg'}").unlink(missing_ok=True)
        index[slug] = {"file": dst.name, "on_dark": slug in ON_DARK, "source_file": str(src.relative_to(ROOT)),
                       **provenance(folder, rel), "processing": steps or ["none"], "output_sha256": sha256(data)}
    (OUT / "index.json").write_text(json.dumps(index, indent=1) + "\n")
    print(f"{len(index)} logos written to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
