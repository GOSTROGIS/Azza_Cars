#!/usr/bin/env python3
"""Merge the archived sources into catalog/models.json and catalog/brands.json.

Inputs (all under catalog/sources/, fetched by fetch_vpic.py and fetch_sources.py):
  vpic/<slug>.jsonl.gz       NHTSA vPIC models per make and model year (US VIN registry, 1981+)
  epa/vehicles.csv.zip       EPA fueleconomy.gov (US, 1984+), size class VClass, grouped by EPA baseModel
  nrcan/*.csv                NRCan Fuel Consumption Ratings (Canada, 1995+), vehicle class
  inegi/raiavl_*.json        INEGI RAIAVL sales by company and model (Mexico, 2005+), segment
  wikidata/models_*.json     Wikidata automobile models of each register brand (any era, any market)

Rules (see catalog/README.md for the full list):
  - A model row exists only if at least one source lists it. Every row carries its sources.
  - Brands come from register/brands.csv only. Source makes outside the register are skipped and counted.
  - Names are matched across sources by a normalized key (letters and digits, upper case).
    Matching may drop trailing trim, body or drivetrain words from a fixed list (MATCH_DROP).
    It never renames a model: the displayed name is the first source's own spelling.
  - Body type comes only from a source's own class label, through the fixed table BODY_MAP.
  - Market flags: US = vPIC or EPA lists it, CA = NRCan lists it, MX = INEGI reports sales.
  - Status: "current" if any source lists the latest model year or INEGI reports sales in the
    latest year, "discontinued" if a dated source ends earlier, "unknown" otherwise.

Usage:  python3 tools/catalog/build_catalog.py
"""
import collections
import csv
import glob
import io
import json
import re
import unicodedata
import zipfile

from common import CATALOG, ROOT, SOURCES, brands, read_jsonl_gz

VPIC_URL = "https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMakeId/{}?format=json"
EPA_URL = "https://www.fueleconomy.gov/feg/download.shtml"
NRCAN_URL = "https://open.canada.ca/data/en/dataset/98f1a129-f628-4ce4-b24d-6f16bf24dd64"
INEGI_URL = "https://www.inegi.org.mx/datosprimarios/iavl/"
WD_URL = "https://www.wikidata.org/wiki/{}"

# Words that may be dropped from the END of a source name when looking for a match in another
# source. They describe trims, cabs, bodies, drivetrains or fuels, not distinct models.
MATCH_DROP = {
    "SEDAN", "HB", "HATCHBACK", "SUV", "VAN", "DC", "CS", "CABINA", "DOBLE", "REGULAR", "CHASIS",
    "PICKUP", "PICK", "UP", "HYBRID", "HIBRIDO", "EV", "BEV", "PHEV", "HEV", "REEV", "AWD", "4WD",
    "4X4", "2WD", "4X2", "FWD", "RWD", "FFV", "CNG", "DIESEL", "COUPE", "CONVERTIBLE", "WAGON",
    "CAB", "CHASSIS", "4MATIC", "XDRIVE", "SDRIVE", "QUATTRO", "LWB", "SWB", "EXT", "CREW",
    "2PTS", "3PTS", "4PTS", "5PTS", "2P", "3P", "4P", "5P", "TA", "TM", "IMA", "UUV", "SUT",
}
# INEGI writes door counts as two words ("4 Ptas"). Both words may be dropped together.
DOOR_WORDS = {"PTAS", "PTS", "PUERTAS"}
# vPIC also lists motorcycles, trailers and off-road vehicles. A vPIC-only model whose every
# vPIC vehicle type is in this set is out of scope (cars and trucks) and is counted, not kept.
VPIC_OUT_OF_SCOPE = {"Motorcycle", "Off Road Vehicle", "Trailer"}
MATCH_DROP_LEAD = {"NUEVO", "NUEVA", "NEW", "ALL"}

# Source class label -> site body category. Labels not listed map to nothing (shown raw only).
BODY_MAP = {
    "epa": [(r"Pickup", "pickup"), (r"Sport Utility", "suv"), (r"Minivan|Vans", "van"),
            (r"Station Wagon", "wagon"), (r"Special Purpose", "special"),
            (r"Cars$|Two Seaters", "car")],
    "nrcan": [(r"^Pickup", "pickup"), (r"^SUV|Sport utility", "suv"), (r"^Minivan|^Van", "van"),
              (r"^Station wagon", "wagon"), (r"^Special purpose", "special"),
              (r"^(Minicompact|Subcompact|Compact|Mid-size|Full-size|Two-seater)", "car")],
    "inegi": [(r"^Pick Ups$", "pickup"), (r"^SUV", "suv"), (r"^Minivans$", "van"),
              (r"^(Compactos|Subcompactos|Deportivos)$", "car")],
    "vpic": [(r"^Passenger Car$", "car"), (r"^Bus$", "bus"), (r"^Multipurpose", "mpv"),
             (r"^Truck$", "truck"), (r"^Incomplete Vehicle$", "truck"),
             (r"^Low Speed Vehicle", "lsv")],
}


def fold(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()


def words(name):
    return re.findall(r"[A-Z0-9]+", fold(name).upper())


def key(name):
    return "".join(words(name))


def trim_tail(ws):
    """Drop trailing MATCH_DROP words and INEGI door pairs ("4 Ptas"). Yields each shorter form."""
    w = list(ws)
    while len(w) > 1 and (w[-1] in MATCH_DROP or w[-1] in DOOR_WORDS):
        w = w[:-2] if w[-1] in DOOR_WORDS and len(w) > 2 and w[-2].isdigit() else w[:-1]
        yield list(w)


def body_of(source, label):
    for pattern, body in BODY_MAP[source]:
        if re.search(pattern, label or ""):
            return body
    return None


class Catalog:
    def __init__(self):
        self.brands = {b["slug"]: b for b in brands()}
        self.models = {}          # (slug, key) -> row
        self.index = collections.defaultdict(dict)   # slug -> key -> row key, includes aliases
        self.skipped = collections.Counter()
        with open(CATALOG / "make_aliases.csv", newline="") as f:
            self.make_aliases = {key(r["source_make"]): r["brand_slug"] for r in csv.DictReader(f)}

    def row(self, slug, name):
        k = (slug, key(name))
        if k not in self.models:
            self.models[k] = {"brand": slug, "name": name.strip(" -"), "aliases": set(),
                              "years": set(), "bodies": set(), "classes": collections.defaultdict(set),
                              "markets": set(), "sources": collections.defaultdict(dict),
                              "mx_units": {}, "wd_years": [None, None]}
            self.index[slug][k[1]] = k
        return self.models[k]

    def brand_words(self, slug):
        """Words of the brand name without a parenthetical, e.g. "GWM (Great Wall Motor)" -> GWM."""
        return words(self.brands[slug]["name"].split("(")[0])

    def without_brand(self, slug, name):
        """The source name minus a leading brand name ("Toyota Camry" -> "Camry"), else unchanged."""
        bw, ws = self.brand_words(slug), name.split()
        return " ".join(ws[len(bw):]) if words(" ".join(ws[: len(bw)])) == bw and len(ws) > len(bw) else name

    def find(self, slug, name):
        """Exact key, then the key with trailing MATCH_DROP words (and leading NUEVO) removed."""
        ws = words(name)
        brand_ws = self.brand_words(slug)
        candidates = [ws]
        if ws[: len(brand_ws)] == brand_ws and len(ws) > len(brand_ws):
            candidates.append(ws[len(brand_ws):])
        for base in list(candidates):
            w = list(base)
            while w and w[0] in MATCH_DROP_LEAD:
                w = w[1:]
            candidates += list(trim_tail(w))
            candidates.append(w)
        for w in candidates:
            k = "".join(w)
            if k in self.index[slug]:
                return self.models[self.index[slug][k]]
        return None

    def alias(self, row, name):
        name = name.strip(" -")
        if name and key(name) != key(row["name"]):
            row["aliases"].add(name)
        self.index[row["brand"]].setdefault(key(name), (row["brand"], key(row["name"])))

    # ---- sources -------------------------------------------------------------------------------
    def load_vpic(self):
        by_make = {}
        for slug, b in self.brands.items():
            if b["vpic_make_id"]:
                by_make[int(b["vpic_make_id"])] = slug
        for path in sorted(glob.glob(str(SOURCES / "vpic" / "*.jsonl.gz"))):
            for rec in read_jsonl_gz(path):
                body = json.loads(rec["body"])
                m = re.search(r"modelyear/(\d{4})", rec["url"])
                vt = re.search(r"vehicletype/([^?]+)", rec["url"])
                for r in body.get("Results", []):
                    if "Model_Name" not in r:
                        continue
                    slug = by_make.get(r["Make_ID"])
                    if not slug:
                        continue
                    row = self.find(slug, r["Model_Name"]) or self.row(slug, r["Model_Name"])
                    self.alias(row, r["Model_Name"])
                    src = row["sources"]["vpic"]
                    src.setdefault("model_ids", set()).add(r["Model_ID"])
                    src["url"] = VPIC_URL.format(r["Make_ID"])
                    if m:
                        y = int(m.group(1))
                        row["years"].add(y)
                        src.setdefault("years", set()).add(y)
                        row["markets"].add("US")
                    if vt and r.get("VehicleTypeName"):
                        row["classes"]["vpic"].add(r["VehicleTypeName"])

    def make_lookup(self, label):
        """Map a source's make string to a register slug by register name, vPIC make or slug,
        or by an explicit row in catalog/make_aliases.csv. The key table is built once."""
        if not hasattr(self, "_make_keys"):
            self._make_keys = {}
            for slug, b in self.brands.items():
                for k in (key(b["name"]), "".join(self.brand_words(slug)), key(b["vpic_make"] or ""), key(slug)):
                    if k:
                        self._make_keys.setdefault(k, slug)
            self._make_keys.update(self.make_aliases)
        return self._make_keys.get(key(label))

    def load_epa(self):
        z = zipfile.ZipFile(SOURCES / "epa" / "vehicles.csv.zip")
        rows = csv.DictReader(io.StringIO(z.read("vehicles.csv").decode("utf-8")))
        for r in rows:
            slug = self.make_lookup(r["make"])
            if not slug:
                self.skipped["epa:" + r["make"]] += 1
                continue
            base = r["baseModel"] or r["model"]
            row = self.find(slug, base) or self.row(slug, base)
            self.alias(row, base)
            y = int(r["year"])
            row["years"].add(y)
            row["markets"].add("US")
            row["classes"]["epa"].add(r["VClass"])
            src = row["sources"]["epa"]
            src.setdefault("years", set()).add(y)
            src["url"] = EPA_URL

    def load_nrcan(self):
        for path in sorted(glob.glob(str(SOURCES / "nrcan" / "*.csv"))):
            with open(path, encoding="utf-8-sig", errors="replace") as f:
                reader = csv.reader(f)
                header = next(reader)
                if header[:4] != ["Model year", "Make", "Model", "Vehicle class"]:
                    continue
                for r in reader:
                    if len(r) < 4 or not r[0].strip().isdigit():
                        continue
                    slug = self.make_lookup(r[1])
                    if not slug:
                        self.skipped["nrcan:" + r[1]] += 1
                        continue
                    row = self.find(slug, r[2]) or self.prefix_match(slug, r[2]) or self.row(slug, self.strip(r[2]))
                    self.alias(row, r[2])
                    y = int(r[0])
                    row["years"].add(y)
                    row["markets"].add("CA")
                    row["classes"]["nrcan"].add(r[3])
                    src = row["sources"]["nrcan"]
                    src.setdefault("years", set()).add(y)
                    src["url"] = NRCAN_URL

    def strip(self, name):
        """Source spelling with trailing trim, door and drivetrain words removed, used to name new rows."""
        ws = name.split()
        n = len(ws)
        for shorter in trim_tail(words(name)):
            n = len(shorter)
        return " ".join(ws[:n]) if len(words(name)) == len(ws) else name

    def prefix_match(self, slug, name):
        """Longest already-known model of this brand whose words start the source name."""
        ws = words(name)
        for n in range(len(ws) - 1, 0, -1):
            k = "".join(ws[:n])
            if k in self.index[slug] and all(w in MATCH_DROP or re.fullmatch(r"\d+", w) is None
                                             for w in ws[n:]):
                return self.models[self.index[slug][k]]
        return None

    def load_inegi(self):
        groups = {}
        with open(CATALOG / "inegi_company_brands.csv", newline="") as f:
            for r in csv.DictReader(f):
                groups[r["inegi_company"]] = r["brand_slugs"].split("|")
        for slug, b in self.brands.items():
            if b["inegi_marca"] and b["inegi_marca"] not in groups:
                groups[b["inegi_marca"]] = [slug]
        prefixes = {slug: b["inegi_model_prefix"] for slug, b in self.brands.items() if b["inegi_model_prefix"]}
        data = json.loads((SOURCES / "inegi" / "raiavl_venta_by_model_year.json").read_text())
        self.inegi_latest = max(r["year"] for r in data)
        for r in data:
            group = groups.get(r["company"])
            if not group:
                self.skipped["inegi:" + r["company"]] += 1
                continue
            row = None
            for slug in group:
                p = prefixes.get(slug)
                if p and fold(r["model"]).upper().startswith(fold(p).upper() + " "):
                    rest = r["model"][len(p):].strip()
                    row = self.find(slug, rest) or self.row(slug, self.strip(rest.strip(" -")))
                    break
            if row is None:
                hits = [h for h in (self.find(s, r["model"]) for s in group) if h]
                if len({h["brand"] for h in hits}) == 1:
                    row = hits[0]
                elif len(group) == 1:
                    row = self.row(group[0], self.strip(r["model"]))
            if row is None:
                row = self.row("_inegi_" + key(r["company"]).lower(), self.strip(r["model"]))
                row["company"] = r["company"]
            self.alias(row, r["model"])
            row["years"].add(r["year"])
            row["mx_units"][r["year"]] = row["mx_units"].get(r["year"], 0) + r["units"]
            if r["units"] > 0:
                row["markets"].add("MX")
            row["classes"]["inegi"].add(r["segmento"])
            src = row["sources"]["inegi"]
            src.setdefault("years", set()).add(r["year"])
            src["url"] = INEGI_URL
            src.setdefault("names", set()).add(r["model"])

    def load_wikidata(self):
        by_qid = collections.defaultdict(list)
        for slug, b in self.brands.items():
            if b["wikidata_qid"]:
                by_qid[b["wikidata_qid"]].append(slug)
        seen = set()
        for path in sorted(glob.glob(str(SOURCES / "wikidata" / "models_*.json"))):
            for b in json.loads(open(path).read())["results"]["bindings"]:
                qid = b["model"]["value"].rsplit("/", 1)[1]
                label = b.get("modelLabel", {}).get("value", "")
                bq = b["brand"]["value"].rsplit("/", 1)[1]
                if re.fullmatch(r"Q\d+", label):
                    self.skipped["wikidata:no English label"] += 1
                    continue
                for slug in by_qid[bq]:
                    base = re.sub(r"\s*\(.*?\)\s*", " ", label).strip()
                    row = self.find(slug, base) or self.row(slug, self.without_brand(slug, base))
                    if (slug, qid, id(row)) in seen:
                        continue
                    seen.add((slug, qid, id(row)))
                    src = row["sources"]["wikidata"]
                    src.setdefault("qids", set()).add(qid)
                    src["url"] = WD_URL.format(sorted(src["qids"])[0])
                    for field, idx in (("inception", 0), ("start", 0), ("discontinued", 1), ("end", 1)):
                        if field in b:
                            y = int(re.match(r"[+-]?(\d+)", b[field]["value"]).group(1))
                            if not 1885 <= y <= 2030:   # outside the automobile era: a data error, not a date
                                self.skipped["wikidata:implausible year"] += 1
                                continue
                            cur = row["wd_years"][idx]
                            if (cur is None or (y < cur if idx == 0 else y > cur)):
                                row["wd_years"][idx] = y
                    if label != row["name"]:
                        row["aliases"].add(label)

    # ---- output --------------------------------------------------------------------------------
    def finish(self):
        latest_my = max(y for row in self.models.values() for s, src in row["sources"].items()
                        if s in ("vpic", "epa", "nrcan") for y in src.get("years", ()))
        out = []
        for (slug, k), row in sorted(self.models.items(), key=lambda kv: (kv[0][0], kv[1]["name"].lower())):
            vt = row["classes"].get("vpic", set())
            if set(row["sources"]) <= {"vpic", "wikidata"} and "vpic" in row["sources"] and (
                    not vt or vt <= VPIC_OUT_OF_SCOPE):
                self.skipped["vpic:out of scope type " + ("/".join(sorted(vt)) or "none")] += 1
                continue
            # Light-vehicle class labels (EPA, NRCan, INEGI) take precedence. vPIC's broad vehicle
            # types (Truck, MPV, Bus) are used only when no other source classifies the model.
            light = {b for s, labels in row["classes"].items() if s != "vpic" for l in labels
                     if (b := body_of(s, l))}
            bodies = sorted(light or {b for l in row["classes"].get("vpic", ()) if (b := body_of("vpic", l))})
            years = sorted(row["years"])
            wd0, wd1 = row["wd_years"]
            y0 = years[0] if years else wd0
            y1 = years[-1] if years else wd1
            if row["mx_units"].get(self.inegi_latest, 0) > 0 or any(
                    latest_my in src.get("years", ()) for s, src in row["sources"].items() if s != "inegi"):
                status = "current"
            elif years or wd1:
                status = "discontinued"
            else:
                status = "unknown"
            sources = {}
            for s, src in sorted(row["sources"].items()):
                sources[s] = {kk: (sorted(v) if isinstance(v, set) else v) for kk, v in src.items()}
                if "years" in sources[s]:
                    ys = sources[s]["years"]
                    sources[s]["years"] = [ys[0], ys[-1]]
            entry = {
                "id": f"{slug}/{k.lower()}",
                "brand": slug,
                "name": row["name"],
                "aliases": sorted(row["aliases"]),
                "year_min": y0,
                "year_max": y1,
                "years_basis": "sources" if years else ("wikidata" if (wd0 or wd1) else None),
                "bodies": bodies,
                "classes": {s: sorted(v) for s, v in sorted(row["classes"].items())},
                "markets": sorted(row["markets"]),
                "status": status,
                "sources": sources,
            }
            if row.get("company"):
                entry["inegi_company"] = row["company"]
            if row["mx_units"]:
                entry["mx_units_by_year"] = {str(y): u for y, u in sorted(row["mx_units"].items())}
            out.append(entry)
        return out, latest_my


def logo_status():
    """Audited logos only: the audit's own report.json says "pass" and the SVG exists. Read-only use of logos/."""
    passed = set()
    for report in glob.glob(str(ROOT / "logos" / "audit" / "*" / "report.json")):
        r = json.loads(open(report).read())
        if r.get("result") == "pass" and (ROOT / "logos" / "svg" / f"{r['slug']}.svg").exists():
            passed.add(r["slug"])
    return passed


def main():
    cat = Catalog()
    cat.load_vpic()
    cat.load_epa()
    cat.load_nrcan()
    cat.load_inegi()
    cat.load_wikidata()
    models, latest_my = cat.finish()
    passed = logo_status()
    counts = collections.Counter(m["brand"] for m in models)
    brand_rows = [{"slug": s, "name": b["name"], "segment": b["segment"], "models": counts.get(s, 0),
                   "logo": f"logos/svg/{s}.svg" if s in passed else None,
                   "register_sources": int(b["sources_confirming"] or 0)}
                  for s, b in cat.brands.items()]
    for company_slug in sorted(s for s in counts if s.startswith("_inegi_")):
        company = next(m["inegi_company"] for m in models if m["brand"] == company_slug)
        brand_rows.append({"slug": company_slug, "name": f"{company} (INEGI company, brand not stated)",
                           "segment": "light", "models": counts[company_slug], "logo": None,
                           "register_sources": 0, "inegi_company": company})
    (CATALOG / "models.json").write_text(json.dumps(models, ensure_ascii=False, indent=0) + "\n")
    (CATALOG / "brands.json").write_text(json.dumps(brand_rows, ensure_ascii=False, indent=1) + "\n")
    report = {
        "models": len(models),
        "latest_model_year": latest_my,
        "inegi_latest_year": cat.inegi_latest,
        "by_source": dict(collections.Counter(s for m in models for s in m["sources"])),
        "by_status": dict(collections.Counter(m["status"] for m in models)),
        "by_market": dict(collections.Counter(mk for m in models for mk in m["markets"])),
        "no_market": sum(1 for m in models if not m["markets"]),
        "by_body": dict(collections.Counter(b for m in models for b in m["bodies"])),
        "no_body": sum(1 for m in models if not m["bodies"]),
        "logos_audited": sorted(passed),
        "skipped_source_makes": dict(sorted(cat.skipped.items(), key=lambda kv: -kv[1])),
    }
    (CATALOG / "build_report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "skipped_source_makes"}, indent=1))


if __name__ == "__main__":
    main()
