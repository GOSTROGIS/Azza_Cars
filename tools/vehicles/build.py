#!/usr/bin/env python3
"""Build a GLB recreation of one vehicle from its traced outlines (see trace.py).

Steps:
  1. Visual hull: a voxel grid at the cited length, width and height is carved by three silhouettes.
     Side (x, z) from the side outline. Across the length (y, z) from the union of the front outline
     and the mirrored rear outline, stretched to the cited width. Plan (x, y) from a traced top
     outline when one exists, otherwise an approximate rounded rectangle (recorded as approximate).
  2. Wheel arches are cut where the traced wheels sit, so wheels can be separate parts.
  3. The occupancy is blurred slightly and meshed with marching cubes, then Taubin smoothed and decimated.
  4. Faces are split into parts by the traced regions: glass (dark window areas in the side, front and
     rear photos), lights (red tail lamps in the rear photo) and body (everything else).
  5. Wheels are added as separate tyre and rim cylinders at the traced wheel centres and radius.

Output: vehicles/<slug>/<slug>.glb in metres, Y up, length along X with the front toward +X,
width along Z, ground at y = 0. Materials are named body (recolourable), glass, lights, tyres, rims.
Writes vehicles/<slug>/build.json with every parameter and every approximation used.

Usage:  python3 tools/vehicles/build.py <slug>
"""
import sys

import cv2
import fast_simplification
import numpy as np
import trimesh
from scipy.ndimage import gaussian_filter
from skimage.measure import marching_cubes

from common import VEHICLES, load_json, references, save_json

VOXEL_MM = 12
TARGET_FACES = 60000
ARCH_GAP = 1.07          # wheel arch radius as a multiple of the tyre radius
PLAN_CORNER = (0.16, 0.10)  # approximate plan corner radius, front and rear, as a fraction of width


def raster(polys, shape, to_px):
    """Fill polygons into a uint8 image of shape (rows, cols). to_px maps (a, b) mm to (col, row)."""
    img = np.zeros(shape, np.uint8)
    pts = [np.round(np.array([to_px(p) for p in poly])).astype(np.int32) for poly in polys if len(poly) > 2]
    if pts:
        cv2.fillPoly(img, pts, 1)
    return img.astype(bool)


def rounded_plan(ni, nj, v, front_r, rear_r):
    """Approximate plan view: a rectangle with rounded corners, front toward high i."""
    img = np.ones((nj, ni), np.uint8)
    ys, xs = np.mgrid[0:nj, 0:ni]
    for r_mm, at_front in ((front_r, True), (rear_r, False)):
        r = max(1, int(round(r_mm / v)))
        cx = ni - 1 - r if at_front else r
        for cy in (r, nj - 1 - r):
            corner = ((xs > cx) if at_front else (xs < cx)) & ((ys < cy) if cy == r else (ys > cy))
            img[corner & ((xs - cx) ** 2 + (ys - cy) ** 2 > r * r)] = 0
    return img.astype(bool)


def tyres_in_front_view(F, v, w):
    """Tyre width and half track measured from the across-length silhouette below the wheel hub.

    Returns (tyre width mm, half track mm) or None when the low rows show no gap between the tyres.
    """
    nj = F.shape[0]
    k_low = max(1, int((w["cz"] - 0.5 * w["r"]) / v))
    low = F[:, :k_low].any(axis=1)
    mid = (nj - 1) / 2
    if low[int(mid)]:
        return None
    sides = []
    for half in (np.nonzero(low[: int(mid)])[0], np.nonzero(low[int(mid) + 1:])[0] + int(mid) + 1):
        if half.size == 0:
            return None
        # the outermost run of occupied columns on this side
        run = np.split(half, np.nonzero(np.diff(half) > 1)[0] + 1)
        run = run[0] if half[0] < mid else run[-1]
        sides.append(((run[-1] - run[0] + 1) * v, abs((run[0] + run[-1]) / 2 - mid) * v))
    return float(np.mean([s[0] for s in sides])), float(np.mean([s[1] for s in sides]))


def tyre_dims(dims, wheel_r_mm, W, traced):
    """Tyre width and half track. Cited values win, then values traced from the front and rear
    photos, then approximations. Each choice is recorded."""
    notes = {}
    if dims.get("tyre_width_mm"):
        tw, notes["tyre_width"] = dims["tyre_width_mm"], "cited"
    elif traced:
        tw, notes["tyre_width"] = traced[0], "traced from the front and rear photos"
    else:
        tw = 0.26 * 2 * wheel_r_mm
        notes["tyre_width"] = "approximate: 0.26 x traced wheel diameter (no cited tyre size)"
    if dims.get("track_mm"):
        half_track, notes["track"] = dims["track_mm"] / 2, "cited"
    elif traced:
        half_track, notes["track"] = traced[1], "traced from the front and rear photos"
    else:
        half_track = W / 2 - tw / 2 - 0.035 * W
        notes["track"] = "approximate: tyre outer face 3.5% of width inside the body side (no cited track)"
    return tw, half_track, notes


def material(name, rgba, metallic, roughness, emissive=None):
    return trimesh.visual.material.PBRMaterial(
        name=name, baseColorFactor=rgba, metallicFactor=metallic, roughnessFactor=roughness,
        emissiveFactor=emissive, doubleSided=False)


MATERIALS = {
    "body": material("body", [216, 64, 26, 255], 0.55, 0.32),
    "glass": material("glass", [18, 20, 24, 255], 0.1, 0.05),
    "lights": material("lights", [200, 20, 16, 255], 0.0, 0.25, [0.55, 0.04, 0.02]),
    "tyres": material("tyres", [22, 22, 24, 255], 0.0, 0.85),
    "rims": material("rims", [190, 192, 198, 255], 0.9, 0.28),
}


def part(mesh, name):
    mesh.visual = trimesh.visual.TextureVisuals(material=MATERIALS[name])
    return mesh


def build(slug):
    out = load_json(VEHICLES / slug / "outlines" / "outlines.json")
    dims = references(slug)["dimensions"]
    L, W, H = dims["length_mm"], dims["width_mm"], dims["height_mm"]
    v = VOXEL_MM
    ni, nj, nk = int(np.ceil(L / v)) + 1, int(np.ceil(W / v)) + 1, int(np.ceil(H / v)) + 1
    views = out["views"]
    log = {"slug": slug, "voxel_mm": v, "grid": [ni, nj, nk], "cited_mm": {"length": L, "width": W, "height": H},
           "approximations": []}

    side = views["side"]
    S = raster([side["body"]], (nk, ni), lambda p: (p[0] / v, p[1] / v)).T          # [i, k]

    # Across-length silhouette: front and mirrored rear, each stretched to the cited width.
    def lateral(view, mirror):
        vw = views[view]
        s = W / vw["traced_width_mm"]
        return lambda p: (((vw["traced_width_mm"] - p[0]) if mirror else p[0]) * s / v, p[1] / v)
    F = np.zeros((nk, nj), bool)
    for view, mirror in (("front", False), ("rear", True)):
        if view in views:
            F |= raster([views[view]["body"]], (nk, nj), lateral(view, mirror))
            log[f"{view}_width_stretch"] = round(W / views[view]["traced_width_mm"], 4)
    F = F.T                                                                           # [j, k]

    if "top" in views:
        T = raster([views["top"]["body"]], (nj, ni), lambda p: (p[0] / v, p[1] / v)).T
        log["plan"] = "traced top view"
    else:
        T = rounded_plan(ni, nj, v, PLAN_CORNER[0] * W, PLAN_CORNER[1] * W).T
        log["plan"] = f"approximate rounded rectangle, corner radius {PLAN_CORNER[0]} x width front, {PLAN_CORNER[1]} x width rear"
        log["approximations"].append("No top-view photo: plan silhouette is an approximate rounded rectangle at cited length and width.")

    occ = S[:, None, :] & F[None, :, :] & T[:, :, None]

    # Wheel arches, cut only near the body sides so the cut does not tunnel through the car.
    wheels = side.get("wheels") or []
    if not wheels:
        log["approximations"].append("No wheels traced: the model has no separate wheels.")
    ii, kk = np.mgrid[0:ni, 0:nk]
    jj = np.arange(nj)
    wheel_parts = []
    for n, w in enumerate(wheels):
        r = w["r"]
        tw, half_track, notes = tyre_dims(dims, r, W, tyres_in_front_view(F, v, w))
        log.setdefault("wheel_notes", notes)
        for note in notes.values():
            if note.startswith("approximate") and note not in log["approximations"]:
                log["approximations"].append(note)
        disc = ((ii * v - w["cx"]) ** 2 + (kk * v - w["cz"]) ** 2) < (r * ARCH_GAP) ** 2
        inner = (half_track - tw * 0.75) / v
        outer_band = np.abs(jj - (nj - 1) / 2) > inner
        occ[disc[:, None, :] & outer_band[None, :, None]] = False
        for sign in (1, -1):
            wheel_parts.append(wheel(w["cx"], w["cz"], r, tw, sign * half_track, L, f"wheel_{n}_{'right' if sign > 0 else 'left'}"))

    vol = gaussian_filter(np.pad(occ, 2).astype(np.float32), 1.1)
    verts, faces, _, _ = marching_cubes(vol, 0.5)
    verts = (verts - 2) * v                                       # mm in (x, y across, z up)
    mesh = trimesh.Trimesh(verts, faces[:, ::-1], process=True)   # flip winding so normals face out
    trimesh.smoothing.filter_taubin(mesh, iterations=12)
    if len(mesh.faces) > TARGET_FACES:
        pts, fcs = fast_simplification.simplify(mesh.vertices, mesh.faces, 1 - TARGET_FACES / len(mesh.faces))
        mesh = trimesh.Trimesh(pts, fcs, process=True)
    log["faces_after_decimation"] = int(len(mesh.faces))

    # Part masks on the same grids, looked up by each face's centroid and facing.
    G_side = raster(side.get("glass", []), (nk, ni), lambda p: (p[0] / v, p[1] / v)).T
    G_lat, Lamps = {}, np.zeros((nj, nk), bool)
    for view, mirror in (("front", False), ("rear", True)):
        if view in views:
            G_lat[view] = raster(views[view].get("glass", []), (nk, nj), lateral(view, mirror)).T
    if "rear" in views:
        Lamps = raster(views["rear"].get("lamps", []), (nk, nj), lateral("rear", True)).T
    c = mesh.triangles_center
    nrm = mesh.face_normals
    i = np.clip((c[:, 0] / v).round().astype(int), 0, ni - 1)
    j = np.clip((c[:, 1] / v).round().astype(int), 0, nj - 1)
    k = np.clip((c[:, 2] / v).round().astype(int), 0, nk - 1)
    label = np.zeros(len(c), np.int8)                      # 0 body, 1 glass, 2 lights
    sideways = np.abs(nrm[:, 1]) > 0.55
    label[sideways & G_side[i, k]] = 1
    fwd, back = nrm[:, 0] > 0.3, nrm[:, 0] < -0.3
    if "front" in G_lat:
        label[fwd & (c[:, 0] > L * 0.5) & G_lat["front"][j, k]] = 1
    if "rear" in G_lat:
        label[back & (c[:, 0] < L * 0.5) & G_lat["rear"][j, k]] = 1
    label[back & (c[:, 0] < L * 0.25) & Lamps[j, k] & (label == 0)] = 2
    if not Lamps.any():
        log["approximations"].append("No tail lamps were detected in the rear photo: no light parts.")
    log["approximations"].append("Headlamps are not traced: no reliable colour cue separates them in the front photo.")
    log["faces_by_part"] = {"body": int((label == 0).sum()), "glass": int((label == 1).sum()), "lights": int((label == 2).sum())}

    scene = trimesh.Scene()
    for name, lab in (("body", 0), ("glass", 1), ("lights", 2)):
        sel = np.nonzero(label == lab)[0]
        if len(sel):
            sub = mesh.submesh([sel], append=True)
            scene.add_geometry(part(to_metres(sub, L, W), name), node_name=name, geom_name=name)
    for name, meshes in wheel_parts:
        for mat, m in meshes:
            scene.add_geometry(part(m, mat), node_name=f"{name}_{mat}", geom_name=f"{name}_{mat}")

    glb = VEHICLES / slug / f"{slug}.glb"
    glb.write_bytes(scene.export(file_type="glb"))
    b = scene.bounds
    log["bounds_m"] = [[round(float(x), 3) for x in row] for row in b]
    log["glb_bytes"] = glb.stat().st_size
    save_json(VEHICLES / slug / "build.json", log)
    print(slug, "faces", log["faces_by_part"], "bounds", log["bounds_m"], "bytes", log["glb_bytes"])


def to_metres(mesh, L, W):
    """mm (x along length, y across, z up) to metres (X length centred, Y up, Z across centred)."""
    m = mesh.copy()
    x, y, z = m.vertices[:, 0], m.vertices[:, 1], m.vertices[:, 2]
    m.vertices = np.column_stack([(x - L / 2) / 1000, z / 1000, (y - W / 2) / 1000])
    m.invert()  # swapping y and z mirrors the mesh, so restore outward normals
    return m


def wheel(cx, cz, r, tw, zc, L, name):
    """Tyre and rim as separate cylinders, axis across the car, in metres."""
    rot = trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])
    at = trimesh.transformations.translation_matrix([(cx - L / 2) / 1000, cz / 1000, zc / 1000])
    tyre = trimesh.creation.cylinder(radius=r / 1000, height=tw / 1000, sections=48)
    rim = trimesh.creation.cylinder(radius=r * 0.62 / 1000, height=tw * 1.02 / 1000, sections=36)
    for m in (tyre, rim):
        m.apply_transform(rot)
        m.apply_transform(at)
    return name, [("tyres", tyre), ("rims", rim)]


if __name__ == "__main__":
    build(sys.argv[1])
