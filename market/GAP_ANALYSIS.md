# Metro Vancouver car and truck rental: market gap analysis

Prepared 2026-11-22 for Azza Cars. Every figure links to a file in `market/sources/`, whose URL, retrieval time and SHA-256 are in [`sources/provenance.json`](sources/provenance.json). Numbers come from `tools/market/build_market.py` (written to [`analysis.json`](analysis.json)) and `tools/market/tam_sam_som.py`. The market sizing is in [TAM_SAM_SOM.md](TAM_SAM_SOM.md).

## The answer

**Open first south of the Fraser, in Surrey, with a mixed fleet of cars plus cargo vans and light trucks aimed at trade and logistics businesses. Stay out of the airport and downtown, where supply is densest.**

1. **Car rental supply is concentrated where the visitors are, not where the residents are.** Vancouver and Richmond hold 33.1% of Metro population but 59.0% of counted car rental locations (95 of 161). The south of Fraser municipalities (Surrey, both Langleys, Delta, White Rock) hold 32.7% of population but only 19.9% of car rental locations, 0.37 per 10,000 residents against 1.09 in Vancouver and Richmond. [1][2]
2. **Surrey is the clearest gap.** It has 21.6% of Metro population (568,322 people) and 12.4% of car rental locations, 0.35 per 10,000 residents against a Metro average of 0.61. [1][2]
3. **The truck gap is commercial, not consumer.** 127 of 149 counted truck rental locations (85%) are U-Haul, a consumer moving brand. Commercial truck brands are thin: 6 Penske, 1 Ryder. Meanwhile Surrey has 1,418 trucking businesses with employees (NAICS 484), 57.9% of the Metro total, and south of Fraser has 76.4% of Metro trucking businesses and 48.0% of construction businesses. Surrey has 6.0 truck rental locations per 1,000 trucking, warehousing and construction businesses against 9.0 Metro wide. [1][3]
4. **The airport and cruise terminal are saturated by the majors.** 18 counted car rental locations sit within 3 km of YVR and 39 rental locations within 3 km of the cruise terminal, almost all of them the large brands (Hertz, Alamo, Enterprise, National, Avis, Budget, Sixt, Thrifty). [1][4] Demand there is large (YVR handled 24,725,572 passengers from January to November 2025 [5] and 26.914 million for the full year as reported by Daily Hive [6], and Canada Place handled 1.2 million cruise passengers on 301 visits in 2025 [7]), but a new independent would enter at the point of strongest competition.
5. **The sized market is roughly C$650 to 700 million a year in Metro Vancouver**, from C$1,320.2 million of BC automotive rental and leasing revenue in 2024, allocated by four cited drivers that agree within 4 percentage points. See [TAM_SAM_SOM.md](TAM_SAM_SOM.md). This figure includes passenger car leasing, which the published data does not separate.

## Supporting evidence

### Where rental supply is thin relative to population

Counted car rental, truck rental and carshare locations per municipality, from [`municipalities.csv`](municipalities.csv). Population is the 2021 Census [2]. Business counts are Statistics Canada table 33-10-1176, reference date 2026-01 [3].

| Municipality | Population 2021 | Rental locations | Car | Truck | Carshare | Per 10k residents | Trucking firms (484) | Construction firms (23) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Vancouver | 662,248 | 83 | 47 | 31 | 5 | 1.25 | 115 | 2,185 |
| Surrey | 568,322 | 57 | 20 | 37 | 0 | 1.00 | 1,418 | 4,648 |
| Burnaby | 249,125 | 30 | 15 | 14 | 1 | 1.20 | 83 | 1,123 |
| Richmond | 209,937 | 57 | 48 | 9 | 0 | 2.72 | 140 | 854 |
| Coquitlam | 148,625 | 13 | 6 | 7 | 0 | 0.87 | 45 | 635 |
| Langley (Township) | 132,603 | 11 | 1 | 10 | 0 | 0.83 | 222 | 1,036 |
| Delta | 108,455 | 14 | 3 | 11 | 0 | 1.29 | 204 | 731 |
| Maple Ridge | 90,990 | 9 | 3 | 6 | 0 | 0.99 | 51 | 557 |
| North Vancouver (District) | 88,168 | 4 | 2 | 2 | 0 | 0.45 | 21 | 455 |
| New Westminster | 78,916 | 9 | 2 | 7 | 0 | 1.14 | 51 | 234 |
| Port Coquitlam | 61,498 | 4 | 1 | 3 | 0 | 0.65 | 30 | 411 |
| North Vancouver (City) | 58,120 | 7 | 4 | 3 | 0 | 1.20 | 12 | 260 |
| West Vancouver | 44,122 | 1 | 1 | 0 | 0 | 0.23 | 2 | 185 |
| Port Moody | 33,535 | 0 | 0 | 0 | 0 | 0.00 | 8 | 132 |
| Langley (City) | 28,963 | 12 | 8 | 4 | 0 | 4.14 | 20 | 149 |
| White Rock | 21,939 | 0 | 0 | 0 | 0 | 0.00 | 9 | 83 |
| Pitt Meadows | 19,146 | 4 | 0 | 4 | 0 | 2.09 | 16 | 96 |

Smaller members (Electoral Area A, Bowen Island, Anmore, Lions Bay, Belcarra) are in the CSV. Metro total: 316 counted rental locations inside member boundaries for 2,632,013 residents, 1.20 per 10,000. Two more lie on First Nations lands outside member boundaries. [1][2]

What stands out:

* **Langley Township** has one counted car rental location for 132,603 residents (0.08 per 10,000), plus 222 trucking and 1,036 construction businesses. Langley City next door has 8 car rental locations, so part of the township is served across the boundary.
* **Tri-Cities and the north shore** are thin for cars: Coquitlam 0.40, Port Coquitlam 0.16, Port Moody 0, North Vancouver District 0.23 and West Vancouver 0.23 car rental locations per 10,000 residents. [1][2]
* **Richmond** (2.72 per 10,000) and **Langley City** (4.14) are over-supplied relative to their residents, Richmond because of the airport and Langley City because of its dealer and auto mall cluster.

### Demand drivers

| Driver | Figure | Source |
|---|---|---|
| YVR passengers, January to November 2025 (preliminary) | 24,725,572 | YVR traffic update, November 2025 [5] |
| YVR passengers, full year 2025 | 26.914 million, 73,736 a day | Daily Hive, quoting YVR [6] |
| Cruise passengers at Canada Place, 2025 season | 1.2 million on 301 ship visits | Daily Hive, quoting the port authority [7] |
| Overnight visitors to Vancouver, 2025 | 11.3 million | Destination Vancouver [8] |
| Vancouver Coast and Mountains share of BC tourism gross spending, 2024 | 49% | Destination BC regional profile, citing BC Stats [9] |
| Rapid transit stations with no counted rental within 2 km | 3 of 64: Pitt Meadows (2,351 m), Production Way-University (2,192 m), Burquitlam (2,028 m) | TransLink GTFS [10] with [1] |
| Rapid transit stations with no counted rental within 1 km | 13 of 64 | same |

SkyTrain coverage is not the gap: 61 of 64 stations have a counted rental location within 2 km. The thin areas are the car-dependent suburbs and industrial lands south of the Fraser, which the rapid transit network barely reaches.

### Which segments are underserved

| Segment | Verdict | Evidence |
|---|---|---|
| Commercial trucks and cargo vans | **Underserved, supported by the data** | 127 of 149 truck rental locations are U-Haul. 7 are Penske or Ryder. South of Fraser holds 76.4% of Metro trucking businesses (1,873 of 2,451). [1][3] |
| Everyday car rental for residents outside the core | **Underserved, supported by the data** | Car rental locations per 10,000 residents: 0.35 Surrey, 0.08 Langley Township, 0.28 Delta, 0.40 Coquitlam, against 0.71 Vancouver and 2.29 Richmond. [1][2] |
| Airport and cruise visitors | **Not underserved** | 18 rental brands within 3 km of YVR and 39 within 3 km of the cruise terminal. [1][4] |
| Urban short trips (carshare) | **Served by carshare** | Evo had roughly 2,300 vehicles and Modo 1,000 vehicles and 30,000 members in August 2023 [11]. Modo reports 1 in 5 of its vehicles are electric [12]. Overture maps carshare poorly (6 points), so this rests on the operator figures. |
| Peer-to-peer | **Present, not measured** | Turo operates in British Columbia under ICBC blanket insurance [13]. No listing counts were sourced. |
| One-way, long-term, premium, EV rental, delivery and gig drivers | **Not assessable** | No source in this analysis measures demand or supply for these. They are hypotheses for customer interviews, not findings. |

### Competitor landscape

Counted rental locations by brand inside Metro Vancouver, from [`supply.geojson`](supply.geojson). "Locations" are brand storefronts after deduplication, so co-located counters (for example Enterprise, National and Alamo at one desk) count once per brand. [1][4]

| Brand | Locations | Segment | Where they cluster (top 3 municipalities) |
|---|---:|---|---|
| U-Haul | 127 | Consumer truck, van and trailer | Surrey 34, Vancouver 27, Burnaby 11 |
| Independents and unbranded | 59 | Car, some truck | Richmond 21, Vancouver 14, Langley Township 6 |
| Alamo | 24 | Car | Vancouver 8, Richmond 5, Surrey 3 |
| Enterprise | 23 | Car | Vancouver 5, Richmond 4, Langley City 3 |
| Hertz | 22 | Car | Vancouver 7, Richmond 5, Surrey 4 |
| Avis | 12 | Car | Richmond 3, Vancouver 3, Surrey 2 |
| Budget | 10 | Car | Richmond 3, Burnaby 2, Vancouver 2 |
| National | 7 | Car | Richmond 2, Vancouver 2, Burnaby 1 |
| Discount Car and Truck Rentals | 6 | Car and truck | Richmond 2, Vancouver 2, Burnaby 1 |
| Penske | 6 | Commercial truck | Vancouver 2, Burnaby 1, Delta 1 |
| Thrifty | 5 | Car | Vancouver 3, Richmond 1, Surrey 1 |
| Dollar, Sixt | 3 each | Car | Vancouver, Richmond, Burnaby, Surrey |
| Mr. Rent-A-Car, Routes | 2 each | Car | Burnaby, Vancouver, Richmond, Surrey |
| Ryder | 1 | Commercial truck | Delta |
| Evo, Zipcar, Car2Go, Modo | 6 points in total | Carshare | Vancouver, Burnaby |

The Zipcar and Car2Go points are Overture records that may be stale. Their current operating status was not checked against a source.

Context on the majors' economics: Hertz reported company-wide vehicle utilisation of 81% for full year 2025 [14]. Avis Budget reported fourth quarter 2025 revenue per day down 2% excluding exchange rate effects [15]. Both are US-dominated, company-wide figures.

## Recommended first locations and segments

| Priority | Where | What | Why (cited) |
|---|---|---|---|
| 1 | Surrey, near its industrial and trucking employment (exact site to be chosen by the owner) | Cars plus cargo vans and light trucks, daily and weekly, sold to trade and logistics businesses as well as residents | Largest population gap (0.35 car rental locations per 10,000 against 0.61 Metro wide) and 57.9% of Metro trucking businesses, with commercial truck rental limited to Penske and Ryder elsewhere [1][2][3] |
| 2 | Langley Township, along the same south of Fraser corridor | Same mix | 0.08 car rental locations per 10,000 residents, 222 trucking and 1,036 construction businesses [1][2][3] |
| 3 | Tri-Cities (Coquitlam, Port Coquitlam, Port Moody), near Burquitlam or Coquitlam Central | Resident car rental | 0.28 car rental locations per 10,000 across the northeast sector, and Burquitlam is one of three stations with no counted rental within 2 km [1][2][10] |
| Avoid at launch | YVR, Richmond airport district, downtown and the cruise terminal | | Densest concentration of the majors, 18 and 39 locations within 3 km [1][4] |

These are screening results. Before signing a lease the owner should check zoning, site visibility and actual rates at the nearest competitors, none of which this data covers.

## Limits of this data

* **Overture coverage.** Overture places are conflated from Meta, Microsoft, Foursquare and other feeds. They miss some locations and keep some closed ones. Only 1 of the 1,787 extracted records carried a closed flag (removed), so records like Zipcar and Car2Go may be stale without being flagged. Some records are misclassified (for example a bus maker and a detailing shop under car rental). Records below 0.5 confidence (in the layer, marked `counted = false`) are excluded from all counts.
* **Carshare is invisible in point data.** Evo is free floating and Modo uses hundreds of on-street and building stations. Neither shows up as more than a handful of points, so carshare is described from operator figures, which date from August 2023 [11].
* **AllThePlaces adds little here.** Its BC extract covers Enterprise, Hertz, National, Alamo and Sixt and the main dealer brands. The U-Haul, Avis and Penske spiders hold no Canadian Metro Vancouver points, and Budget, Thrifty, Dollar and Zipcar have no spider output (all checked, see provenance).
* **Locations are not fleet.** A U-Haul neighbourhood dealer with two trucks and a YVR counter with hundreds of cars both count as one location. Business counts count establishments with employees, not vehicles or revenue.
* **Business counts are coarse.** Statistics Canada publishes NAICS 5321 (automotive equipment rental and leasing) at census subdivision level, not 532111, 532112 or 532120, so passenger rental, leasing and truck rental cannot be separated in the counts. The reference date is 2026-01 as published, in the June 2026 edition.
* **The census is from 2021.** Population and households are 2021 counts. Growth since then, especially in Surrey and Langley Township, is not reflected, which if anything understates the south of Fraser gap.
* **Municipal totals hide sub-municipal geography.** Surrey and Langley Township are large. A site choice needs neighbourhood-level work.
* **Web figures are secondary in places.** The full-year YVR total and cruise figures come from Daily Hive quoting the operators, because the YVR December sheet and the City of Vancouver 2025 transportation snapshot returned HTTP 403. The Destination Vancouver and Destination BC figures are their own publications.
* **Not found:** a BC-wide airport passenger total, Metro Vancouver ADRs or utilisation, one-way or long-term rental volumes, Turo listing counts, EV rental supply, and gig-driver rental demand.

## Open in SlipCurve GIS

The spatial outputs are WGS 84 GeoJSON with short field names, so they load directly into [SlipCurve GIS](https://gostrogis.github.io/SLIPCURVE/modules/module-gis.html).

Files and raw URLs (the repository is private, so a URL load may fail without access. If it does, download the file and add it from disk):

* `supply.geojson`: https://raw.githubusercontent.com/GOSTROGIS/Azza_Cars/main/market/supply.geojson
* `municipalities.geojson`: https://raw.githubusercontent.com/GOSTROGIS/Azza_Cars/main/market/municipalities.geojson
* `stations.geojson`: https://raw.githubusercontent.com/GOSTROGIS/Azza_Cars/main/market/stations.geojson

Steps:

1. Choose **Map → Add data** and select `municipalities.geojson` and `supply.geojson` (or use **Add Data From Path** with the raw URLs above).
2. Open **Feature Layer → Symbology** on `municipalities`, choose **graduated colors** on `rent_p10k` (rental locations per 10,000 residents), with natural breaks or manual limits at 0.25, 0.5, 1 and 2.
3. On `supply`, use **unique values** on `category` and **Select By Attributes** with `counted = true` to hide low-confidence points.
4. Buffer example: add `stations.geojson`. Open **Map → Select By Location**, input layer `stations`, selecting layer `supply` (with the counted rental selection), relationship within a distance of 2 kilometres, and tick **Invert Spatial Relationship**. The result is the stations with no rental within 2 km: Pitt Meadows, Production Way-University and Burquitlam, matching the `rent_2km = 0` field. The guide notes the Buffer tool needs a projected input layer, so if you want visible 2 km rings, project `supply` to NAD83 / UTM zone 10N first, then run **Analysis → Tools → Buffer** at 2,000 metres.

Key fields: `municipalities` has `pop21`, `hh21`, `rent_all`, `rent_car`, `rent_trk`, `rent_cshr`, `rent_p10k`, `dealers`, `deal_p10k`, `bc5321`, `bc4411`, `bc484`, `bc23`, `bc_ref`, `stations`, `st_no2km`, `trk_p1kt`. `supply` has `name`, `brand`, `category`, `source`, `src_id`, `conf`, `counted`, `muni`.

## Sources

Hashes are the SHA-256 of the raw file used. All files are listed with full detail in [`sources/provenance.json`](sources/provenance.json).

1. Overture Maps places, release 2026-11-18.0, theme places, file `part-00002-5783d80c-d44a-5845-9057-3a39013540b0-c000.zstd.parquet` (S3 ETag `4deda9314cbe9252124f6c0967072f1a-13`), read by HTTP range request 2026-11-22T22:47:29Z. CDLA-Permissive-2.0. Extract `sources/overture/places-2026-11-18.0-metro-vancouver.geojson`, SHA-256 `daf6c4f8ae6abe7469367102acff1d8e532cc465118cbeff22f37eb7a2bbfe72`. Deduplicated with [4] into `supply.geojson`.
2. Statistics Canada, 2021 Census Profile by census subdivision, https://api.statcan.gc.ca/census-recensement/profile/sdmx/rest/data/STC_CP,DF_CSD/, retrieved by the consulting repository 2026-10-27T13:34:54Z. Local layer SHA-256 `1458ba509f748e0e75e9252f8f22f6036ab79b8a4ce446b2c813e14caaa16c24`. Statistics Canada Open Licence. Boundaries: Province of BC ABMS municipalities and regional districts (OGL-BC), local file SHA-256 `2a10ac9a40ee05488a82e8f8a639c2377e293d8f812b9febff6804acfc9897d3`.
3. Statistics Canada, Canadian Business Counts, with employees, census metropolitan areas and census subdivisions, June 2026 (table 33-10-1176), https://www150.statcan.gc.ca/n1/tbl/csv/33101176-eng.zip, REF_DATE 2026-01. Local file SHA-256 `b3119eb9cb06178d2ea1837c2ac609bc014672e2cb2745fdb4806f30c075d586`, upstream zip SHA-256 `10940a0fb569fd5c02ac7e16290101b9c28b27b5eda08515c9b505a5cf701ca7`.
4. AllThePlaces run 2026-11-14-13-32-33, https://alltheplaces-data.openaddresses.io/runs/2026-11-14-13-32-33, BC chain file SHA-256 `806354ef419a003ed487e24b67e118181483c894f72cbd0e1895c4d540803847`. CC0.
5. YVR, Traffic Update November 2025, https://www.yvr.ca/-/media/yvr/documents/facts-sheets/2025/11---november/traffic-update-nov25.pdf, retrieved 2026-11-22T22:47:36Z, SHA-256 `1183224b117dd8c7c0363ff6d97f8ae4307b81c8240cb65c19901da98dd7ee81`.
6. Daily Hive, YVR 2025 passenger record, https://dailyhive.com/vancouver/vancouver-international-airport-yvr-all-time-passenger-record-2025-statistics, retrieved 2026-11-22T22:47:36Z, SHA-256 `d7af8a6ee6adbdcd6eaa4b1731c9e8925f0dc0a19460ee490be2284f9e3c96fc`.
7. Daily Hive, Vancouver 2025 cruise season, https://dailyhive.com/vancouver/vancouver-cruise-ship-season-2025-statistics, retrieved 2026-11-22T22:47:37Z, SHA-256 `3d2263630452e52c16032c1f10e0f78c9bcfcaf9a4b22c671ac4460452502270`.
8. Destination Vancouver, fast facts, https://www.destinationvancouver.com/vancouver/fast-facts/, retrieved 2026-11-22T22:47:37Z, SHA-256 `173c959c81e6e41e37dd17360c59e7888082517de8a9ec8d474e03ff2b5be3c3`.
9. Destination BC, Vancouver Coast and Mountains regional profile 2026, https://www.destinationbc.ca/content/uploads/2026/08/DBC-Regional-Profile-VCM-2026.pdf, retrieved 2026-11-22T22:47:38Z, SHA-256 `12e10feefadd315bae8805d31e8610eec230c3f5f53f06a9729b2d00b27dffc4`.
10. TransLink GTFS static feed, version 26SEP_20261120, https://gtfs-static.translink.ca/gtfs/google_transit.zip, retrieved 2026-11-22T22:47:33Z, SHA-256 `57ed32faf8941ad5ae5a62daf70c0402ffb7387b235186ceccbce2027177b3a2`.
11. Daily Hive, Modo fleet reaches 1,000 vehicles (22 August 2023), https://dailyhive.com/vancouver/modo-carshare-fleet-size, retrieved 2026-11-22T22:47:38Z, SHA-256 `60a39f2ab87855092daa02e22aa72faec819a2a4617f0eeb9639e020808491a4`.
12. Modo, impact report page, https://www.modo.coop/our-impact, retrieved 2026-11-22T22:47:38Z, SHA-256 `b797c24c876225fd1320580a57e1795f31b0988b180f1056eb6e2d2b2b5eb746`.
13. Turo help centre, sharing your car (Canada hosts), https://help.turo.com/en_us/sharing-your-car-canada-hosts-S1uY7_OIc.md, retrieved 2026-11-22T22:47:38Z, SHA-256 `7ad86a6746f291494ed4622fd950f08d4192bd21ccb652cde4be908634bd6340`.
14. Hertz newsroom, fourth quarter and full year 2025 results, https://newsroom.hertz.com/press-releases/press-release-details/hertz-transformation-drives-structural-revenue-gains-and-builds-sustainable-momentum/, retrieved 2026-11-22T22:47:40Z, SHA-256 `96a69c8dfec0dc3c2d5538901033a7b619474c1a9007c2e59b9720b8d828c335`.
15. Avis Budget Group, fourth quarter and full year results, https://www.avisbudgetgroup.com/home/news-and-media/press-release/avis-budget-group-reports-fourth-quarter-and-full-year-results, retrieved 2026-11-22T22:47:40Z, SHA-256 `d862e6e67fd7e78fd3562602092c6d0b312ce4eb3013487ff5ab3e07e7a30db7`.

Retrieval times and hashes above are from the build run on 2026-11-22. Rerunning `fetch_sources.py` refreshes them in `provenance.json`, which is authoritative.
