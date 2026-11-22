# Catalog tools

Scripts that build `catalog/`. See `catalog/README.md` for what they produce and the rules they follow.

| Script | Does |
|---|---|
| `common.py` | HTTP with retries and the project User-Agent, hashing, gzip JSON-lines archives |
| `fetch_vpic.py` | Downloads vPIC models per register make and model year, plus vehicle types |
| `fetch_sources.py` | Downloads EPA, NRCan, INEGI and Wikidata, records hashes in `provenance.json` |
| `build_catalog.py` | Merges everything into `catalog/models.json`, `brands.json` and `build_report.json` |
| `sales_us/` | One-off scripts used to download and check the automaker sales releases in `catalog/sources/sales_us/` |

Requirements: Python 3.11 or newer, standard library only.
