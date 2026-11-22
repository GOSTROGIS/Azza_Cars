# Brand logos

Verified SVG logos for every brand in `register/brands.csv`.

**Use only files in `svg/`.** Each one passed the audit below. Brands not in `svg/`
are either not yet processed or flagged. The reason is recorded in
`audit/<slug>/report.json`, and `STATUS.md` summarises every brand.

## Folders

| Folder | Contents | Edited by hand? |
|---|---|---|
| `svg/` | Final logos, one `<slug>.svg` per brand that passed | No, written by `tools/logos/audit.py` |
| `sources/<slug>/` | Source files exactly as downloaded, grouped by origin, plus `provenance.json` (URL, SHA-256, date) | No, written by the fetch tools |
| `audit/<slug>/` | `rebuilt.svg`, renders, deviation map, `sheet.png` (side-by-side evidence) and `report.json` | No, written by `audit.py` |
| `audit/_review/` | Candidate sheets used to pick each brand's master and reference | No |
| `selection.csv` | Per brand: which source file is the master and which is the independent reference | Yes, after visual review |
| `website_targets.csv` | Which page to capture each brand's logo from, with the reason for any override | Yes |
| `proposals.json` | Scored master/reference pairings, the input to that review | No |

## Where the source artwork comes from

Three origins, kept apart so they can check each other:

1. **website**: captured from the brand's own homepage in a headless browser
   (`tools/logos/fetch_website.mjs`). Inline SVGs are saved with the colours the
   browser actually paints, and image files are downloaded unchanged. Sites that refuse
   automated visitors (for example ford.com, acura.com) are not worked around.
2. **brandfetch**: logo files Brandfetch collected from the brand's website
   (`tools/logos/fetch_brandfetch.py`). The signing token in each file URL is not committed.
3. **commons**: the files Wikidata lists as the brand's logo (property P154), from
   Wikimedia Commons (`tools/logos/fetch_commons.py`). Many are volunteer traces rather
   than official artwork, which is why they never count as confirmation on their own.

## Which logo counts as "the" logo

The **primary logo** is the brand's full logo as it appears on its North American
consumer website (listed in `website_targets.csv`, with the Mexican site for
Mexico-only brands), in its **positive** colours, i.e. the version used on light
backgrounds.

- Corporate or global sites are not used when a consumer site exists. For example,
  nissan-global.com shows "NISSAN MOTOR CORPORATION", not the Nissan vehicle logo.
- A **reversed** variant is made for dark backgrounds: at least 30% of its edge pixels
  would vanish on a white page (for example BMW's white ring and letters, or white
  lettering). White enclosed inside darker artwork, like the text in Peterbilt's oval, does
  not count. A reversed file can confirm a shape, but it is never the primary master.
- A full logo is chosen before a standalone symbol when both exist.

## What "verified" means

A logo in `svg/` is the artwork the brand publishes, rebuilt without changing a pixel.
Its shape and every painted hex value were matched by a second copy collected separately,
from a different origin than the master. The website and Brandfetch both ultimately come
from the brand's own site, so their agreement confirms that the capture is faithful to
what the brand publishes. It is not an outside opinion of what the logo should be.
Colours that only one origin shows, or that two origins clearly disagree on, keep the logo
out of `svg/` until a brand guide or media kit settles them.

**Colour note (owner's rule, 2026-11-22).** When a painted colour has no exact independent
match but is within CIEDE2000 2.0 of one (about the smallest difference a trained eye can
see side by side), the logo still ships. It passes with a note, shown as `pass, with note` in `STATUS.md`, and the
note is embedded in the SVG as a `<metadata>` element, for example: "colour not 100%
verified: #6f6f6f matches #707070 ... only to CIEDE2000 0.39". The colour difference code
(`tools/logos/color_difference.py`) reproduces the published reference values of Sharma,
Wu and Dalal (2005).

## How a logo is rebuilt and audited

For each brand, `selection.csv` names a vector **master** and a **reference** from a
*different* origin. `tools/logos/audit.py` then:

1. **Rebuilds** the master with svgo 4.0.0 (`tools/logos/svgo.config.mjs`). It removes
   editor metadata, writes colours as `#rrggbb`, keeps path precision at 5 decimals,
   and crops the viewBox to the artwork. No shape is redrawn by hand.
2. **Checks fidelity.** Master and rebuild are rendered (resvg) through the same viewBox
   at the same size and compared pixel by pixel. Required: no edge moves by more than
   1 px at 2048 px artwork width, and the painted colours are identical.
3. **Checks agreement.** The rebuild and the independent reference are each rendered
   so the artwork is 2048 px wide and compared as they would look on a white page. A
   reversed (white) reference can only be compared by silhouette. For every pixel where
   the shapes differ, the distance to the other shape is measured. Required: at most 0.01% of artwork pixels farther than
   3 px (0.15% of the logo's width) and an aspect ratio within 1%. A raster reference
   gets a wider tolerance in proportion to its own resolution.
4. **Audits colours.** Every flat colour actually painted in the rebuild (any colour
   covering at least 0.2% of the artwork) must appear exactly, hex for hex, in the
   reference's render, or in Brandfetch's published palette when the master is not
   itself from Brandfetch.
5. **Flags** embedded bitmaps, live text (which depends on installed fonts), scripts,
   gradients or shading (more than 12 flat colours), and reversed masters,
   all of which need a person to look.
6. **Writes evidence** to `audit/<slug>/` and copies a passing rebuild to `svg/<slug>.svg`.

Every `sheet.png` was also inspected by eye before a brand was marked done.

## Re-running

```
pip install pillow numpy resvg_py defusedxml
(cd tools/logos && npm install)
python3 tools/logos/fetch_commons.py          # slow: Wikimedia throttles uncached files
python3 tools/logos/fetch_brandfetch.py       # needs work/brandfetch.json (see that script)
node tools/logos/fetch_website.mjs
python3 tools/logos/propose_selection.py      # writes proposals.json
python3 tools/logos/review_candidates.py batch-01 acura audi ...   # look at it
python3 tools/logos/propose_selection.py --accept acura audi ...    # after review
python3 tools/logos/audit.py
```

## Trademarks

These logos are trademarks of their owners. Show them only to identify the makes
Azza Cars rents, do not alter them, and follow each owner's published usage rules.
