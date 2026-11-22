# tools/vehicles

Scripts that turn reference photos into 3D vehicle recreations for the site viewer.

The models are faithful recreations built from photos and cited dimensions. They are not factory CAD
and are never described as identical to the real vehicle.

## Pipeline

| Step | Script | Reads | Writes |
|---|---|---|---|
| 1. Trace | `trace.py <slug>` | `vehicles/references/<slug>/` photos and `references.json`, `vehicles/<slug>/vehicle.json` | `vehicles/<slug>/outlines/` |
| 2. Build | `build.py <slug>` | the outlines and cited dimensions | `vehicles/<slug>/<slug>.glb`, `build.json` |
| 3. Publish | `publish.py` | every vehicle folder | `vehicles/<slug>/provenance.json`, thumbnails, `vehicles/manifest.json` |
| Selection | `selection.py` | archived sales data | `vehicles/SELECTION.md` |
| Review | `compare.html?slug=<slug>` | the GLB and reference photos | a page with each photo beside a render from the same angle |

### Trace

For each view named in `vehicle.json` (side, front, rear, top):

1. Optional crop box, to leave out other vehicles, and optional mirror, so the front faces right in the side view.
2. Background removal with the rembg `isnet-general-use` model. The largest region is kept and its holes are filled.
3. The outer contour is simplified (Douglas-Peucker) and rounded (Chaikin), then scaled to millimetres.
   The side view is scaled to the cited length and height. Front and rear are scaled uniformly from the
   cited height, and their traced width is recorded next to the cited width as a check.
4. Side view: two wheel circles from a Hough transform, or `wheels_px` from the config when detection fails.
5. Side, front and rear: glass is the darker Otsu class of brightness in the upper part of the silhouette.
   Nothing is marked when the classes are not clearly apart, as on a black vehicle.
6. Rear: tail lamps are saturated red regions. Nothing is marked when red covers the body.

Outputs per view: `<view>.svg` (viewBox in millimetres), `<view>_check.png` (the traced outline drawn
back on the photo, for review) and `outlines.json` with every polygon and scale.

### Build

1. A voxel grid (12 mm) at the cited length, width and height is carved by the side silhouette, the
   union of the front and mirrored rear silhouettes stretched to the cited width, and a plan silhouette.
   Without a top photo the plan is an approximate rounded rectangle, recorded in `build.json`.
2. Wheel arches are cut at the traced wheel centres, only near the body sides.
3. The occupancy is blurred slightly, meshed with marching cubes, Taubin smoothed and decimated to about 60,000 faces.
4. Faces are split into parts by the traced regions: `glass`, `lights` and `body`.
5. Tyres and rims are added as separate cylinders. Tyre width and track come from cited values when
   present, otherwise from the front and rear silhouettes below the hub, otherwise an approximation that is recorded.

The GLB is in metres, Y up, length along X with the front toward +X, ground at y = 0. The material named
`body` is the one the site recolours.

## Limits

- Photos have perspective. A three-quarter photo used as a front or rear view widens the near side.
  Each model's `build.json` records the width stretch applied, which shows the size of that error.
- A visual hull cannot show concave shapes the silhouettes hide, such as a pickup bed or door recesses.
- Headlamps are not traced. There is no reliable colour cue for them in a front photo.

## Requirements

Python packages: `rembg[cpu]`, `opencv-python-headless`, `numpy`, `scipy`, `scikit-image`, `trimesh`,
`fast-simplification`, `pillow`. The rembg model downloads once to `~/.u2net`.

Run from this folder, for example `python3 trace.py ford-f150 && python3 build.py ford-f150`.
