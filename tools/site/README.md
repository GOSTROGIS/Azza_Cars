# tools/site

Builds data-driven assets for the website.

`service_map.py` draws `site/public/service-area.svg`, the service-area map on the landing page, from the
CONSULTING repository's Metro Vancouver capture (read only). Major roads come from Overture road
segments, ember dots are Overture buildings whose derived use is industrial, and the municipal
outlines come from `market/municipalities.geojson`. It also writes `site/public/service-area.json` with
the counts, the Overture release, the SHA-256 of every input file and the ODbL attribution the page shows.

```sh
python3 tools/site/service_map.py /home/user/consulting
```

Needs `duckdb` (with its spatial extension) and `shapely`. Only mapped buildings are counted, so an
area with sparse mapping shows fewer dots than it has industrial buildings.
