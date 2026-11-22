#!/usr/bin/env python3
"""Cross-check register/candidates.csv against three independent public sources.

Sources (all fetched live, raw responses archived under register/sources/):
  1. NHTSA vPIC  GetAllMakes            (US federal make registry, 17-digit VIN era)
  2. INEGI RAIAVL venta mensual CSV     (Mexico light-vehicle sales by company, 2005+)
  3. Wikidata SPARQL                    (QID, logo file P154, website P856, inception P571, dissolved P576)

A brand is "sourced" only if at least one of the three confirms it. Nothing is
inferred: missing matches are written as blanks and flagged, never guessed.

Usage:  python3 tools/register/build_register.py
"""
import csv
import hashlib
import io
import itertools
import json
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "register"
SRC = REG / "sources"
UA = "AzzaCarsLogoAudit/0.1 (brand-register provenance; python-urllib)"
VPIC_ALL = "https://vpic.nhtsa.dot.gov/api/vehicles/GetAllMakes?format=json"
INEGI_ZIP = ("https://www.inegi.org.mx/contenidos/investigacion/datosprimarios/raiavl/"
             "datosabiertos/conjunto_de_datos_raiavl_mensual_venta_csv.zip")
SPARQL = "https://query.wikidata.org/sparql"
SPARQL_BATCH = 40

QUERY = """SELECT ?article ?item ?itemLabel ?logo ?logoStart ?logoEnd ?logoRank ?inception ?dissolved ?website WHERE {
  VALUES ?article { %s }
  ?article schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> .
  OPTIONAL { ?item p:P154 ?ls . ?ls ps:P154 ?logo ; wikibase:rank ?logoRank .
             OPTIONAL { ?ls pq:P580 ?logoStart } OPTIONAL { ?ls pq:P582 ?logoEnd } }
  OPTIONAL { ?item wdt:P856 ?website } OPTIONAL { ?item wdt:P571 ?inception } OPTIONAL { ?item wdt:P576 ?dissolved }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }"""


def get(url, data=None, accept=None):
    headers = {"User-Agent": UA}
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, data=data, headers=headers)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 and e.code < 500 or attempt == 4:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == 4:
                raise
        time.sleep(2 ** attempt)


def tail(iri, sep="/"):
    """Last segment of an IRI, URL-decoded."""
    return urllib.parse.unquote(iri.rsplit(sep, 1)[1])


class Provenance(list):
    """Saves each downloaded blob under register/sources/ and records its hash."""

    def record(self, name, blob, url, save=True):
        if save:
            (SRC / name).write_bytes(blob)
        self.append({"file": name, "committed": save, "url": url,
                     "sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob),
                     "retrieved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})


def load_vpic(prov):
    raw = get(VPIC_ALL)
    prov.record("vpic_getallmakes.json", raw, VPIC_ALL)
    return {r["Make_Name"].strip().upper(): r["Make_ID"] for r in json.loads(raw)["Results"]}


def load_inegi(prov):
    # The zip is about 22 MB, so only its hash and a per-company summary are kept.
    # INEGI reports by company (MARCA), so each company also keeps its model names:
    # sub-brands such as Tank or Ram are confirmed by model records, not by the company.
    blob = get(INEGI_ZIP)
    prov.record("conjunto_de_datos_raiavl_mensual_venta_csv.zip", blob, INEGI_ZIP, save=False)
    inegi = {}
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for n in z.namelist():
            if not n.endswith(".csv") or "conjunto_de_datos/" not in n:
                continue
            for r in csv.DictReader(io.TextIOWrapper(z.open(n), encoding="utf-8-sig", errors="replace")):
                try:
                    u = int(float(r["UNI_VEH"] or 0))
                except ValueError:
                    u = 0
                if u <= 0:
                    continue
                m, y = r["MARCA"].strip(), int(r["ANIO"])
                e = inegi.setdefault(m, {"first_year": y, "last_year": y, "units": 0, "models": {}})
                e["first_year"], e["last_year"] = min(e["first_year"], y), max(e["last_year"], y)
                e["units"] += u
                mo = r["MODELO"].strip()
                em = e["models"].setdefault(mo, {"first_year": y, "last_year": y, "units": 0})
                em["first_year"], em["last_year"] = min(em["first_year"], y), max(em["last_year"], y)
                em["units"] += u
    (SRC / "inegi_raiavl_venta_by_company.json").write_text(json.dumps(inegi, indent=1, sort_keys=True))
    return inegi


def load_wikidata(titles, prov):
    """Wikidata records keyed by English Wikipedia article title."""
    wd = {}
    for n, chunk in enumerate(itertools.batched(titles, SPARQL_BATCH)):
        if n:
            time.sleep(1)  # be polite to the public query service
        url_to_title = {"https://en.wikipedia.org/wiki/" + urllib.parse.quote(t.replace(" ", "_"), safe="(),'!.-_"): t
                        for t in chunk}
        q = QUERY % " ".join("<%s>" % u for u in url_to_title)
        raw = get(SPARQL, data=urllib.parse.urlencode({"query": q}).encode(), accept="application/sparql-results+json")
        name = "wikidata_sparql_%02d" % n
        (SRC / (name + ".rq")).write_text(q)
        prov.record(name + ".json", raw, SPARQL + " (POST, query saved alongside as .rq)")
        for b in json.loads(raw)["results"]["bindings"]:
            e = wd.setdefault(url_to_title[b["article"]["value"]],
                              {"qid": tail(b["item"]["value"]), "label": b["itemLabel"]["value"],
                               "logos": [], "websites": [], "inception": None, "dissolved": None})
            if "logo" in b:
                lg = {"file": tail(b["logo"]["value"]), "rank": tail(b["logoRank"]["value"], "#"),
                      "start": date_or_unknown(b.get("logoStart")), "end": date_or_unknown(b.get("logoEnd"))}
                if lg not in e["logos"]:
                    e["logos"].append(lg)
            if "website" in b and b["website"]["value"] not in e["websites"]:
                e["websites"].append(b["website"]["value"])
            for key in ("inception", "dissolved"):
                if key in b:
                    v = b[key]["value"][:10]
                    e[key] = min(e[key], v) if e[key] else v
    (SRC / "wikidata_by_title.json").write_text(json.dumps(wd, indent=1, ensure_ascii=False, sort_keys=True))
    return wd


def date_or_unknown(binding):
    """A Wikidata date value, or "unknown" for an unknown-value placeholder IRI."""
    if not binding:
        return None
    v = binding["value"]
    return v if binding.get("type") == "literal" else "unknown"


def year(v):
    return "" if not v else v if v == "unknown" else v.lstrip("+")[:4]


def logo_cell(logos):
    cells = []
    for lg in logos:
        span = ""
        if lg["start"] or lg["end"]:
            span = ", %s-%s" % (year(lg["start"]), year(lg["end"]))
        cells.append("%s [%s%s]" % (lg["file"], lg["rank"], span))
    return " | ".join(cells)


def main():
    SRC.mkdir(parents=True, exist_ok=True)
    with open(REG / "candidates.csv", encoding="utf-8") as f:
        cands = list(csv.DictReader(f))
    prov = Provenance()
    vpic = load_vpic(prov)
    inegi = load_inegi(prov)
    wd = load_wikidata([c["enwiki"] for c in cands if c["enwiki"]], prov)

    out = []
    for c in cands:
        row = dict(c)
        vm, im = c["vpic_make"].strip().upper(), c["inegi_marca"].strip()
        ie = inegi.get(im) if im else None
        prefix = c["inegi_model_prefix"].strip().casefold()
        models = sorted(m for m in (ie or {}).get("models", {}) if m.casefold().startswith(prefix)) if prefix else []
        if prefix:
            ms = [ie["models"][m] for m in models]
            ie = {"first_year": min(m["first_year"] for m in ms),
                  "last_year": max(m["last_year"] for m in ms)} if ms else None
        row["inegi_models_matched"] = " | ".join(models)
        w = wd.get(c["enwiki"], {})
        row["vpic_make_id"] = vpic.get(vm, "") if vm else ""
        row["inegi_years"] = "%s-%s" % (ie["first_year"], ie["last_year"]) if ie else ""
        row["wikidata_qid"] = w.get("qid", "")
        row["wikidata_inception"] = w.get("inception") or ""
        row["wikidata_dissolved"] = w.get("dissolved") or ""
        row["wikidata_websites"] = " | ".join(w.get("websites", []))
        row["wikidata_logo_files"] = logo_cell(w.get("logos", []))
        confirming = sum(map(bool, (row["vpic_make_id"], ie, w)))
        problems = []
        if vm and not row["vpic_make_id"]:
            problems.append("vpic make name not found")
        if im and not ie:
            problems.append("INEGI company or model prefix not found")
        if c["enwiki"] and not w:
            problems.append("enwiki title not resolved in Wikidata")
        if not confirming:
            problems.append("NO SOURCE CONFIRMS THIS BRAND")
        row["sources_confirming"] = confirming
        row["flags"] = " / ".join(problems)
        out.append(row)

    with open(REG / "brands.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        wr.writeheader()
        wr.writerows(out)
    (SRC / "provenance.json").write_text(json.dumps(prov, indent=1))

    flagged = [r for r in out if r["flags"]]
    print("%d candidates, %d flagged" % (len(out), len(flagged)))
    for r in flagged:
        print("  %-18s %s" % (r["slug"], r["flags"]))


if __name__ == "__main__":
    main()
