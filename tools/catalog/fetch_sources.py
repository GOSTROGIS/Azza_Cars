#!/usr/bin/env python3
"""Download the non-vPIC catalog sources and archive them with SHA-256 hashes.

  EPA fueleconomy.gov  vehicles.csv.zip        US light-duty models 1984+, with EPA size class (VClass)
  NRCan                Fuel Consumption Ratings Canada light-duty models 1995+, with vehicle class
  INEGI                RAIAVL venta mensual     Mexico light-vehicle sales by company and model, 2005+
  Wikidata             SPARQL                   automobile models of each register brand (all eras)

Large zips (INEGI about 22 MB) are not committed. Their URL and hash are, plus a
compact extract (model, year, units, segment) that build_catalog.py reads.

Usage:  python3 tools/catalog/fetch_sources.py [epa nrcan inegi wikidata]
"""
import collections
import csv
import io
import json
import sys
import urllib.parse
import zipfile

from common import SOURCES, brands, get, now_utc, save_provenance, sha256

EPA_ZIP = "https://www.fueleconomy.gov/feg/epadata/vehicles.csv.zip"
NRCAN_PKG = "https://open.canada.ca/data/api/action/package_show?id=98f1a129-f628-4ce4-b24d-6f16bf24dd64"
INEGI_ZIP = ("https://www.inegi.org.mx/contenidos/investigacion/datosprimarios/raiavl/"
             "datosabiertos/conjunto_de_datos_raiavl_mensual_venta_csv.zip")
SPARQL = "https://query.wikidata.org/sparql"
WD_BATCH = 12

WD_QUERY = """SELECT ?brand ?model ?modelLabel ?inception ?start ?end ?discontinued ?bodyLabel WHERE {
  VALUES ?brand { %s }
  ?model wdt:P31/wdt:P279* wd:Q3231690 .
  { ?model wdt:P1716 ?brand } UNION { ?model wdt:P176 ?brand }
  OPTIONAL { ?model wdt:P571 ?inception }
  OPTIONAL { ?model wdt:P2031 ?start }
  OPTIONAL { ?model wdt:P2032 ?end }
  OPTIONAL { ?model wdt:P2669 ?discontinued }
  OPTIONAL { ?model wdt:P4519 ?body }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }"""


def entry(name, blob, url, committed):
    return {"file": name, "committed": committed, "url": url, "sha256": sha256(blob),
            "bytes": len(blob), "retrieved_utc": now_utc()}


def fetch_epa():
    blob = get(EPA_ZIP)
    out = SOURCES / "epa"
    out.mkdir(parents=True, exist_ok=True)
    (out / "vehicles.csv.zip").write_bytes(blob)
    save_provenance("epa", [entry("vehicles.csv.zip", blob, EPA_ZIP, True)])


def fetch_nrcan():
    pkg = get(NRCAN_PKG)
    out = SOURCES / "nrcan"
    out.mkdir(parents=True, exist_ok=True)
    (out / "package_show.json").write_bytes(pkg)
    prov = [entry("package_show.json", pkg, NRCAN_PKG, True)]
    for res in json.loads(pkg)["result"]["resources"]:
        # English CSV tables only. "Original" 2-cycle 1995-2014 duplicates the 5-cycle table's models.
        url = res["url"]
        if res["format"] != "CSV" or "en" not in res.get("language", []) or "/original-" in url:
            continue
        name = url.rsplit("/", 1)[1]
        blob = get(url)
        (out / name).write_bytes(blob)
        prov.append(entry(name, blob, url, True))
        print("nrcan", name, len(blob), flush=True)
    save_provenance("nrcan", prov)


def fetch_inegi():
    blob = get(INEGI_ZIP)
    z = zipfile.ZipFile(io.BytesIO(blob))
    units = collections.Counter()
    meta = {}
    for name in sorted(z.namelist()):
        if not name.startswith("conjunto_de_datos/"):
            continue
        if not name.endswith(".csv"):
            continue
        for r in csv.DictReader(io.StringIO(z.read(name).decode("utf-8-sig", errors="replace"))):
            key = (r["MARCA"], r["MODELO"], int(r["ANIO"]))
            units[key] += int(float(r["UNI_VEH"] or 0))
            meta[key] = (r["TIPO"], r["SEGMENTO"], r["ESTATUS"])
    rows = [{"company": k[0], "model": k[1], "year": k[2], "units": v, "tipo": meta[k][0],
             "segmento": meta[k][1], "estatus": meta[k][2]} for k, v in sorted(units.items())]
    out = SOURCES / "inegi"
    out.mkdir(parents=True, exist_ok=True)
    extract = json.dumps(rows, ensure_ascii=False, indent=0).encode()
    (out / "raiavl_venta_by_model_year.json").write_bytes(extract)
    save_provenance("inegi", [
        entry("conjunto_de_datos_raiavl_mensual_venta_csv.zip", blob, INEGI_ZIP, False),
        {**entry("raiavl_venta_by_model_year.json", extract, INEGI_ZIP, True),
         "derived": "sum of UNI_VEH per MARCA, MODELO, ANIO over all months, by tools/catalog/fetch_sources.py"}])
    print("inegi", len(rows), "company-model-year rows", flush=True)


def fetch_wikidata():
    qids = sorted({b["wikidata_qid"] for b in brands() if b["wikidata_qid"]})
    out = SOURCES / "wikidata"
    out.mkdir(parents=True, exist_ok=True)
    prov = []
    for i in range(0, len(qids), WD_BATCH):
        n = i // WD_BATCH
        q = WD_QUERY % " ".join("wd:" + x for x in qids[i:i + WD_BATCH])
        blob = get(SPARQL, data=urllib.parse.urlencode({"query": q}).encode(),
                   accept="application/sparql-results+json")
        (out / f"models_{n:02d}.rq").write_text(q + "\n")
        (out / f"models_{n:02d}.json").write_bytes(blob)
        prov.append(entry(f"models_{n:02d}.json", blob, SPARQL + " (POST, query saved alongside as .rq)", True))
        print("wikidata batch", n, len(json.loads(blob)["results"]["bindings"]), flush=True)
    save_provenance("wikidata", prov)


if __name__ == "__main__":
    steps = {"epa": fetch_epa, "nrcan": fetch_nrcan, "inegi": fetch_inegi, "wikidata": fetch_wikidata}
    for s in sys.argv[1:] or steps:
        steps[s]()
