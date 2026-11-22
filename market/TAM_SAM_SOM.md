# Metro Vancouver car and truck rental: TAM, SAM and SOM

Prepared 2026-11-22. Computed by `tools/market/tam_sam_som.py` into [`tam_sam_som.json`](tam_sam_som.json). Source hashes are in [`sources/provenance.json`](sources/provenance.json). All dollar figures are Canadian dollars.

## The answer

* **TAM: C$1,320.2 million in British Columbia and C$10,697.9 million in Canada (2024, preliminary).** This is operating revenue of the automotive equipment rental and leasing industry, NAICS 5321, from Statistics Canada table 21-10-0012. BC revenue grew from C$868.1 million in 2020 to C$1,320.2 million in 2024.
* **SAM: C$647 to 698 million a year in Metro Vancouver**, the BC figure allocated by four cited drivers (population, households, rental business locations, regional tourism spending). The drivers agree within 4 percentage points (49.0% to 52.8% of BC). Leasing cannot be removed from this figure with published data. If only the national share of sales to individuals and households (39.0%) is kept, the consumer slice is C$252 to 272 million.
* **SOM: not a sourced fact.** On owner placeholder inputs it ranges from C$0.2 million (low case, year 1) to C$3.2 million (high case, year 3), between 0.03% and 0.49% of SAM. A new independent's share is therefore set by how many vehicles it can fund and keep rented, not by market size.

## Waterfall

| Step | Value (C$ million) | Basis | Source |
|---|---:|---|---|
| Canada, NAICS 5321 operating revenue, 2024 | 10,697.9 | Published | StatCan 21-10-0012 [1] |
| British Columbia, NAICS 5321 operating revenue, 2024 | 1,320.2 | Published, 12.3% of Canada | StatCan 21-10-0012 [1] |
| Metro Vancouver share, low (tourism spending driver, 49.0%) | 646.9 | BC × 49.0% | Destination BC [3] |
| Metro Vancouver share, high (population driver, 52.8%) | 697.7 | BC × 52.8% | 2021 Census [2] |
| Excluding long-term leasing | not computable | NAICS 5321 is not split by product in any current published table | [1] |
| Consumer slice only (sales to individuals and households, Canada 2024: 39.0%) | 252.3 to 272.1 | SAM × 39.0% | StatCan 21-10-0014 [1] |
| SOM, years 1 to 3 | 0.2 to 3.2 | Bottom-up, owner inputs | see below |

## TAM detail

| Year | BC revenue (C$ million) |
|---|---:|
| 2019 | 1,108.2 |
| 2020 | 868.1 |
| 2021 | 1,016.1 |
| 2022 | 1,180.2 |
| 2023 | 1,271.9 |
| 2024 (preliminary) | 1,320.2 |

Operating profit margin in 2024 was 10.7% in BC and 13.0% in Canada, down from 16.8% and 17.6% in 2023 [1].

Canada 2024 client mix [1]: businesses 57.3%, individuals and households 39.0%, governments and not-for-profits 2.4%, exports 1.3%. No provincial split is published.

**Not found:** revenue for NAICS 532111 (passenger car rental), 532112 (passenger car leasing) and 532120 (truck, utility trailer and RV rental and leasing) separately. The current StatCan tables publish only the 4-digit total (checked against the full WDS cube list for rental and leasing titles). The TAM therefore includes leasing and RV rental.

## SAM: allocation methods side by side

| Method | Metro Vancouver | British Columbia | Share | SAM (C$ million) | Source |
|---|---:|---:|---:|---:|---|
| Population, 2021 Census (census division 5915, including reserves) | 2,642,825 | 5,000,879 | 52.8% | 697.7 | [2] |
| Private households, 2021 Census | 1,043,319 | 2,041,834 | 51.1% | 674.6 | [2] |
| Business locations with employees in NAICS 5321, 2026-01 | 154 | 296 | 52.0% | 686.9 | [4] |
| Tourism gross spending, Vancouver Coast and Mountains region, 2024 | | | 49% | 646.9 | [3] |
| YVR passenger volume | 26.914 million (2025) | not found | not computed | | [5] |

Notes on each driver:

* The population and household totals for BC are sums over all 751 BC census subdivisions in the same census layer, which gives 5,000,879 people.
* The BC business count denominator is a sum of published census subdivision values. Places with fewer than 10 businesses outside metropolitan areas are suppressed, so the BC total is understated and the Metro share slightly overstated.
* The tourism region (Vancouver Coast and Mountains) is larger than Metro Vancouver. It holds 62.5% of BC population by the same profile [3], against 52.8% for Metro Vancouver alone, so 49% is an upper bound for Metro's tourism share and the true tourism-based allocation is lower.
* YVR volume cannot become an allocation share without a BC-wide air passenger total, which was not sourced.

## SOM: bottom-up, years 1 to 3

Revenue = fleet × 365 × utilisation × average daily rate (ADR). Inputs live in [`tools/market/som_inputs.json`](../tools/market/som_inputs.json) so the owner can replace them and rerun.

| Input | Low | Base | High | Status |
|---|---:|---:|---:|---|
| Fleet, year 1 / 2 / 3 | 15 / 25 / 35 | 25 / 45 / 70 | 40 / 80 / 120 | **Owner input required** |
| Utilisation | 60% | 70% | 81% | Low and base: **owner input required**. High: Hertz company-wide full year 2025 [6] |
| ADR (C$) | 60 | 75 | 90 | **Owner input required**. No Metro Vancouver or Canadian ADR was found |

| Scenario | Year | Fleet | Revenue (C$) | Share of SAM |
|---|---:|---:|---:|---|
| Low | 1 | 15 | 197,100 | 0.028% to 0.030% |
| Low | 2 | 25 | 328,500 | 0.047% to 0.051% |
| Low | 3 | 35 | 459,900 | 0.066% to 0.071% |
| Base | 1 | 25 | 479,062 | 0.069% to 0.074% |
| Base | 2 | 45 | 862,312 | 0.124% to 0.133% |
| Base | 3 | 70 | 1,341,375 | 0.192% to 0.207% |
| High | 1 | 40 | 1,064,340 | 0.153% to 0.165% |
| High | 2 | 80 | 2,128,680 | 0.305% to 0.329% |
| High | 3 | 120 | 3,193,020 | 0.458% to 0.494% |

The share range uses the high and low SAM (C$697.7 and 646.9 million).

### Sensitivity: annual revenue per vehicle (C$)

| Utilisation \ ADR | 50 | 60 | 75 | 90 | 110 |
|---|---:|---:|---:|---:|---:|
| 50% | 9,125 | 10,950 | 13,688 | 16,425 | 20,075 |
| 60% | 10,950 | 13,140 | 16,425 | 19,710 | 24,090 |
| 70% | 12,775 | 15,330 | 19,162 | 22,995 | 28,105 |
| 81% | 14,783 | 17,739 | 22,174 | 26,609 | 32,522 |

Multiply by the fleet to get annual revenue. Every 10 points of utilisation moves revenue per vehicle by C$1,825 at C$50 a day and by C$4,015 at C$110 a day.

## Limits

* **TAM includes leasing and RV rental.** NAICS 5321 bundles passenger car rental, passenger car leasing and truck, trailer and RV rental and leasing. The share of each is not published, so the SAM cannot be narrowed to short-term rental from data.
* **2024 is preliminary** and will be revised. 2025 had not been published at retrieval.
* **Allocation drivers are proxies.** None measures rental spending in Metro Vancouver directly. Their agreement (49% to 53%) narrows the range but does not prove it. Business rental (57.3% of national sales) may concentrate in Metro Vancouver more than population suggests, and visitor rental at YVR serves trips across the whole province.
* **Utilisation benchmark is from a US-dominated major.** Hertz's 81% is company-wide for 2025. A new independent should not assume it.
* **Daily rates were not found.** Hertz's Americas revenue per day was visible in search results for its 2025 10-K, but SEC EDGAR refused the download (HTTP 403), so it was not archived or used. A local rate survey of the competitors named in [GAP_ANALYSIS.md](GAP_ANALYSIS.md) is the right way to fill this.
* **SOM ignores competition response, seasonality and ramp-up.** It is a capacity calculation, not a forecast.

## Sources

1. Statistics Canada, table 21-10-0012 (Automotive equipment rental and leasing, summary statistics) and table 21-10-0014 (sales by type of client), Annual Survey of Service Industries, downloaded through WDS from https://www150.statcan.gc.ca/n1/tbl/csv/21100012-eng.zip (SHA-256 `7af77519d55b37891074d02f5c573dfdd941e9e489708224787b4b733316f789`) and https://www150.statcan.gc.ca/n1/tbl/csv/21100014-eng.zip (SHA-256 `683d793dfae743e6f657e3eca5059c42ca70c58f578bcee9eb45f30b8747bc3a`), retrieved 2026-11-22T22:47:36Z. Extracts in `sources/statcan/`.
2. Statistics Canada, 2021 Census Profile by census subdivision, local layer SHA-256 `1458ba509f748e0e75e9252f8f22f6036ab79b8a4ce446b2c813e14caaa16c24` (consulting repository capture of 2026-10-27). Extracts `sources/census/csd-profile-2021-metro-vancouver.csv` and `sources/census/bc-totals-2021.csv`.
3. Destination BC, Vancouver Coast and Mountains regional profile 2026, https://www.destinationbc.ca/content/uploads/2026/08/DBC-Regional-Profile-VCM-2026.pdf, retrieved 2026-11-22T22:47:38Z, SHA-256 `12e10feefadd315bae8805d31e8610eec230c3f5f53f06a9729b2d00b27dffc4`.
4. Statistics Canada, Canadian Business Counts June 2026 (table 33-10-1176), REF_DATE 2026-01, local file SHA-256 `b3119eb9cb06178d2ea1837c2ac609bc014672e2cb2745fdb4806f30c075d586`. Extracts in `sources/business-counts/`.
5. Daily Hive quoting YVR, https://dailyhive.com/vancouver/vancouver-international-airport-yvr-all-time-passenger-record-2025-statistics, SHA-256 `d7af8a6ee6adbdcd6eaa4b1731c9e8925f0dc0a19460ee490be2284f9e3c96fc`.
6. Hertz newsroom, fourth quarter and full year 2025 results, SHA-256 `96a69c8dfec0dc3c2d5538901033a7b619474c1a9007c2e59b9720b8d828c335`.
