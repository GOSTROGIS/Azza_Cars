#!/usr/bin/env python3
"""Static layers for the trip planner (site/trips.html).

Writes market/trips/ (copied into site/public/trips/ by site/scripts/copy-data.mjs):
  rentals.geojson     counted rental outlets from market/supply.geojson (car, truck, RV, car share): name, brand,
                      address, and the label and colour of
                      what it rents out, as in the mix chart of tools/market/competition.py
  ferries.geojson     ferry terminals in the same box, from DataBC, for the quick-pick destinations
  structures.geojson  BC Ministry of Transportation highway bridges and tunnels (open, closed or under construction) in the Metro
                      Vancouver box, from DataBC (Open Government Licence - British Columbia). Snapshot,
                      because the provincial services do not send a usable CORS header to the public site.
  provenance.json     what each file is, its source, licence, retrieval time and feature count

Live layers (Surrey truck routes and road obstructions, DriveBC events) are fetched by the page itself.

Usage:  python3 tools/market/trip_layers.py
"""
import json
import urllib.parse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from competition import CAT_FILL, MIX, mix_kind  # noqa: E402
from fetch_sources import get, now  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "market" / "trips"
BOX = (-123.35, 48.95, -122.2, 49.45)  # west, south, east, north: Metro Vancouver and the Fraser Valley edge
WFS = "https://openmaps.gov.bc.ca/geo/pub/wfs"
OGL = {"licence": "Open Government Licence - British Columbia",
       "attribution": "Contains information licensed under the Open Government Licence – British Columbia."}
STRUCTURES = ("pub:WHSE_IMAGERY_AND_BASE_MAPS.MOT_ROAD_STRUCTURE_SP",
              ["BMIS_STRUCTURE_NAME", "BMIS_STRUCTURE_TYPE", "BMIS_STRUCT_STATUS_TYPE_DESC", "HIGHWAY_NUMBER"], "GEOMETRY")
FERRIES = ("pub:WHSE_IMAGERY_AND_BASE_MAPS.GSR_FERRY_TERMINALS_SV", ["TERMINAL_NAME"], "SHAPE")
# Bridges and tunnels only, in a state a driver meets: the inventory also holds sign gantries, retaining walls
# and culverts, and records marked replaced, transferred, aggregated or due for deletion. Filtered by DataBC,
# so the truncation guard counts only what is kept.
ROAD_STATES = ("OPEN/IN USE", "CLOSED", "UNDER CONSTRUCTION")
STRUCTURE_FILTER = ("BMIS_STRUCTURE_TYPE IN ('BRIDGE','TUNNEL') AND BMIS_STRUCT_STATUS_TYPE_DESC IN ("
                    + ",".join(f"'{v}'" for v in ROAD_STATES) + ")")


def wfs(layer, keep, geometry, cql=None):
    """Every feature of a DataBC layer inside BOX that passes the CQL filter, with the listed attributes only."""
    w, s, e, n = BOX
    q = {"service": "WFS", "version": "2.0.0", "request": "GetFeature", "typeName": layer, "outputFormat": "application/json",
         "srsName": "EPSG:4326", "count": "5000", "propertyName": ",".join(keep + [geometry]),
         # GeoServer takes either bbox or CQL_FILTER, so the box goes into the filter.
         "CQL_FILTER": f"BBOX({geometry},{w},{s},{e},{n},'EPSG:4326')" + (f" AND {cql}" if cql else "")}
    data = json.loads(get(f"{WFS}?{urllib.parse.urlencode(q)}"))
    if data.get("numberMatched") not in (None, len(data["features"])):
        raise SystemExit(f"DataBC returned {len(data['features'])} of {data['numberMatched']} for {layer}: raise count")
    return [{"type": "Feature", "geometry": {"type": f["geometry"]["type"], "coordinates": round_coords(f["geometry"]["coordinates"])},
             "properties": {k: f["properties"].get(k) for k in keep}} for f in data["features"] if f.get("geometry")]


def round_coords(c):
    return [round(c[0], 6), round(c[1], 6)] if isinstance(c[0], (int, float)) else [round_coords(x) for x in c]


def structures():
    feats = wfs(*STRUCTURES, cql=STRUCTURE_FILTER)
    for f in feats:
        f["properties"]["open"] = f["properties"]["BMIS_STRUCT_STATUS_TYPE_DESC"] == "OPEN/IN USE"
    return feats


def rentals():
    """Counted rental outlets, with the mix chart's label and colour for what each rents out (competition.py)."""
    supply = json.loads((ROOT / "market/supply.geojson").read_text())["features"]
    labels = dict(MIX)
    out = []
    for f in supply:
        p = f["properties"]
        kind = mix_kind(p)
        if p["counted"] and kind in labels:
            out.append({"type": "Feature", "geometry": f["geometry"],
                        "properties": {k: p.get(k) for k in ("name", "brand", "address")} | {"label": labels[kind], "colour": CAT_FILL[kind]}})
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files = {
        "rentals.geojson": (rentals(), {"source": "market/supply.geojson (this repository)",
                                        "licence": "As market/supply.geojson: OpenStreetMap contributors (ODbL), Overture Maps Foundation and the sources listed in market/README.md"}),
        "structures.geojson": (structures(), {"source": f"{WFS} layer {STRUCTURES[0]}", "filter": STRUCTURE_FILTER} | OGL),
        "ferries.geojson": (wfs(*FERRIES), {"source": f"{WFS} layer {FERRIES[0]}"} | OGL),
    }
    prov = {"generated_utc": now(), "generator": "tools/market/trip_layers.py", "files": {}}
    for name, (feats, meta) in files.items():
        (OUT / name).write_text(json.dumps({"type": "FeatureCollection", "features": feats}, separators=(",", ":")) + "\n")
        prov["files"][name] = meta | {"features": len(feats)}
        print(name, len(feats))
    (OUT / "provenance.json").write_text(json.dumps(prov, indent=1) + "\n")


if __name__ == "__main__":
    main()
