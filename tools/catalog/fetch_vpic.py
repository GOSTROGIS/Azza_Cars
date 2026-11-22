#!/usr/bin/env python3
"""Fetch every model NHTSA vPIC lists for each register brand, per model year, plus each model's vehicle type.

Endpoints (https://vpic.nhtsa.dot.gov/api/):
  GetModelsForMakeIdYear/makeId/{id}/modelyear/{year}      one call per brand and year, 1981 to FIRST_YEAR..LAST_YEAR
  GetVehicleTypesForMakeId/{id}                            which vehicle types the make uses
  GetModelsForMakeIdYear/makeId/{id}/vehicletype/{type}    model to vehicle type, one call per type

Every response body is archived verbatim, with its URL, retrieval time and SHA-256,
in catalog/sources/vpic/<slug>.jsonl.gz. Nothing is parsed or merged here, see build_catalog.py.

Usage:  python3 tools/catalog/fetch_vpic.py [--years 1981-2027] [--only slug,slug]
"""
import argparse
import json
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from common import SOURCES, brands, get, now_utc, save_provenance, sha256, write_jsonl_gz

API = "https://vpic.nhtsa.dot.gov/api/vehicles/"


def fetch(url):
    body = get(url)
    return {"url": url, "retrieved_utc": now_utc(), "sha256": sha256(body), "body": body.decode("utf-8")}


def fetch_brand(row, years):
    mid = row["vpic_make_id"]
    urls = [f"{API}GetModelsForMakeIdYear/makeId/{mid}/modelyear/{y}?format=json" for y in years]
    types_url = f"{API}GetVehicleTypesForMakeId/{mid}?format=json"
    with ThreadPoolExecutor(4) as pool:
        records = list(pool.map(fetch, urls + [types_url]))
    types = [t["VehicleTypeName"] for t in json.loads(records[-1]["body"])["Results"]]
    type_urls = [f"{API}GetModelsForMakeIdYear/makeId/{mid}/vehicletype/{urllib.parse.quote(t)}?format=json"
                 for t in types]
    with ThreadPoolExecutor(4) as pool:
        records += list(pool.map(fetch, type_urls))
    return records


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", default="1981-2027")
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    lo, hi = map(int, args.years.split("-"))
    years = range(lo, hi + 1)
    only = set(filter(None, args.only.split(",")))
    prov = []
    for row in brands():
        if not row["vpic_make_id"] or (only and row["slug"] not in only):
            continue
        records = fetch_brand(row, years)
        path = SOURCES / "vpic" / f"{row['slug']}.jsonl.gz"
        write_jsonl_gz(path, records)
        n = sum(json.loads(r["body"]).get("Count", 0) for r in records[: len(years)])
        print(f"{row['slug']:>16}  make {row['vpic_make_id']:>6}  {len(records)} responses  {n} model-year rows", flush=True)
        prov.append({"file": f"vpic/{path.name}", "committed": True, "responses": len(records),
                     "url_pattern": API + "GetModelsForMakeIdYear/makeId/{id}/modelyear/{year} | vehicletype/{type}",
                     "retrieved_utc": records[-1]["retrieved_utc"],
                     "sha256_of_each_response": "stored per line in the archive"})
    if not only:
        save_provenance("vpic", prov)


if __name__ == "__main__":
    main()
