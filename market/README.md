# Market: Metro Vancouver car and truck rental

A cited gap analysis and market sizing for a new car and truck rental business in Metro Vancouver. Read [GAP_ANALYSIS.md](GAP_ANALYSIS.md) first, then [TAM_SAM_SOM.md](TAM_SAM_SOM.md). Open [map.html](map.html) in a browser for the map.

## Files

| File | What it is |
|---|---|
| `GAP_ANALYSIS.md` | The answer, the evidence, the competitor table, recommended first locations, limits and the SlipCurve GIS steps |
| `TAM_SAM_SOM.md` | Market sizing: TAM from StatCan, SAM by four allocation methods side by side, bottom-up SOM with sensitivity |
| `supply.geojson` | Every car rental, truck rental, carshare, RV rental, leasing and dealer location found in Metro Vancouver, deduplicated. WGS 84 points |
| `municipalities.geojson` | The 22 Metro Vancouver members (21 municipalities and Electoral Area A) with population, households, rental and dealer counts, per 10,000 rates and business counts. WGS 84 polygons, simplified to about 10 m, field names of 10 characters or fewer |
| `municipalities.csv` | The same metrics with long field names |
| `stations.geojson` | SkyTrain, West Coast Express and SeaBus stations inside Metro Vancouver, with the distance to the nearest counted rental location |
| `analysis.json` | Every number the gap analysis quotes, as computed |
| `tam_sam_som.json` | Every number the sizing quotes, as computed |
| `competition.json` | Competition index per municipality: logarithmic-curve fits for car, U-Haul moving and commercial truck and van outlets, scores, index and gaps (`tools/market/competition.py`) |
| `competition.geojson` | The municipal polygons with the index (`index`), the three scores, actual and expected outlets, gaps and the map colour (`colour`) |
| `map.html` | Static Leaflet 1.9.4 map (cdnjs) with municipalities shaded by rental locations per 10,000 residents and the supply points. Data is embedded, so it opens from disk |
| `sources/` | Small Metro Vancouver extracts of every input, plus `provenance.json` with URL, retrieval time and SHA-256 of each raw file |

## How it is built

```
pip install duckdb shapely pypdf
python tools/market/fetch_sources.py --consulting /home/user/consulting
python tools/market/build_market.py
python tools/market/tam_sam_som.py
python tools/market/competition.py
```

* `fetch_sources.py` reads the consulting repository read only (boundaries, census profile, business counts, AllThePlaces) and fetches Overture places (DuckDB over HTTP range requests on the release's GeoParquet), the TransLink GTFS feed, StatCan tables 21-10-0012 and 21-10-0014 through WDS, and the web pages cited for demand drivers. It fails if a quoted phrase is missing from a page.
* `build_market.py` builds the layers, the CSV, `analysis.json` and the map from the archived extracts only.
* `tam_sam_som.py` builds the sizing from the archived extracts and the owner's assumptions in `tools/market/som_inputs.json`.
* `competition.py` fits the logarithmic curves, scores each municipality and draws the business plan charts in `site/public/plan/`.

All requests send the user agent `Azza_Cars-market-research/1.0 (+https://github.com/GOSTROGIS/Azza_Cars)`.

## Method notes

* **Categories.** Overture `car_rental_service` becomes `car_rental`. `truck_rental_service` and `trailer_rental_service` become `truck_rental`, as do `rental_service` records named U-Haul. `car_sharing` and the Evo, Modo, Zipcar and Car2Go brands become `carshare`. `rv_rental_service` is `rv_rental`. `auto_dealer` is `car_dealer`, `used_auto_dealer` is `used_dealer`, `truck_dealer` and `commercial_vehicle_dealer` are `truck_dealer`, `auto_leasing` is `car_leasing`. AllThePlaces `amenity=car_rental` is `car_rental` and `shop=car` or `shop=truck` is a dealer. Rental locations in every count are `car_rental`, `truck_rental` and `carshare`. Dealerships are `car_dealer`, `used_dealer` and `truck_dealer`.
* **Clipping.** Points outside the Metro Vancouver regional district polygon are dropped. Points inside it but outside every member polygon (First Nations lands) keep `muni = other`.
* **Counting.** Records flagged closed are removed. Overture records below 0.5 confidence stay in the layer with `counted = false` and are left out of every count. AllThePlaces records always count.
* **Deduplication.** AllThePlaces records are placed first, then Overture records by confidence. A record merges into an earlier one when they are in the same group (rental or dealer) and either share a rental brand within 250 m, or the AllThePlaces dealer make appears in the Overture name within 150 m, or their normalised names match within 100 m. The kept record lists the others in `dup_ids` and `source` shows every source that saw it. 1,678 records inside the region became 1,505, with 114 places confirmed by both sources.
* **Brands.** Rental brands are read from the name and the Overture brand by pattern (see `BRANDS` in `build_market.py`). Brand storefronts at a shared counter count once per brand.
* **Business counts** are the "Total, with employees" rows of the census subdivision matching each member. The member to census subdivision mapping is in `CSD` in `build_market.py` and is checked against the census names.

## Open in SlipCurve GIS

The GeoJSON outputs load into [SlipCurve GIS](https://gostrogis.github.io/SLIPCURVE/modules/module-gis.html) through **Map → Add data**, or through **Add Data From Path** with these raw URLs:

* https://raw.githubusercontent.com/GOSTROGIS/Azza_Cars/main/market/supply.geojson
* https://raw.githubusercontent.com/GOSTROGIS/Azza_Cars/main/market/municipalities.geojson
* https://raw.githubusercontent.com/GOSTROGIS/Azza_Cars/main/market/stations.geojson
* https://raw.githubusercontent.com/GOSTROGIS/Azza_Cars/main/market/competition.geojson

The repository is private, so a URL load may fail without access. Use the local files instead in that case.

1. Add `municipalities.geojson` and `supply.geojson`.
2. On `municipalities`, open **Feature Layer → Symbology**, choose graduated colors on `rent_p10k` (rental locations per 10,000 residents).
3. On `supply`, select `counted = true` and symbolise by `category`.
4. Competition: add `competition.geojson` and use graduated colours on `index`, from bone white (underserved, low) to deep blood orange (competitive, high). The `colour` field holds the exact colour the plan uses.
5. Buffer example: add `stations.geojson`, then **Map → Select By Location** with input `stations`, selecting layer `supply`, within a distance of 2 kilometres, with **Invert Spatial Relationship** ticked. This returns the three stations with no counted rental within 2 km (Pitt Meadows, Production Way-University, Burquitlam). For drawn 2 km rings, project `supply` to NAD83 / UTM zone 10N and run **Analysis → Tools → Buffer** at 2,000 metres, since the Buffer tool expects a projected layer.

## Licences

Overture Maps data is CDLA-Permissive-2.0, AllThePlaces output is CC0, Statistics Canada data is under the Statistics Canada Open Licence, BC boundaries are under the Open Government Licence - British Columbia, and the TransLink GTFS feed is under TransLink's open data terms. The map basemap is CARTO light tiles over OpenStreetMap data (© OpenStreetMap contributors, © CARTO).
