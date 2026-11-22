# Vehicle selection

Which vehicles got 3D recreations first, and the data behind the choice.

## Rule

1. Rank the nameplates in the collected US sales data by 2024 calendar-year US sales.
2. Take the top six, skipping the Ram pickup because a full-size pickup is already covered by the Ford F-150.
3. Add the best-selling model in Mexico in 2025 according to INEGI RAIAVL, the Nissan Versa.

The US figures only cover automakers whose year-end releases could be retrieved and archived.
They are not a complete US ranking. See the gaps below.

## US sales in the collected data

| Rank (2024) | Make | Nameplate | 2024 | 2025 | Chosen |
|---|---|---|---:|---:|---|
| 1 | Ford | F-Series | 765,649 | 828,832 | yes |
| 2 | Toyota | RAV4 | 475,193 | 479,288 | yes |
| 3 | Honda | CR-V | 402,791 | 403,768 | yes |
| 4 | Ram | Ram pickup | 373,120 | 374,059 | skipped, pickup already covered |
| 5 | Toyota | Camry | 309,876 | 316,185 | yes |
| 6 | Nissan | Rogue | 245,724 | 217,896 | yes |
| 7 | Honda | Civic | 242,005 | 238,661 |  |
| 8 | Toyota | Corolla | 232,908 | 248,088 |  |
| 9 | Jeep | Grand Cherokee | 216,148 | 210,082 |  |
| 10 | Hyundai | Tucson | 206,126 | 234,230 |  |
| 11 | Toyota | Tacoma | 192,813 | 274,638 |  |

Notes on the US figures:

- Ram's row label is "Ram P/U" in the 2024 chart and "TOTAL Ram PU" in the 2025 chart.
- Ford reports the F-Series as one family, so its figure includes Super Duty trucks, not only the F-150.
- In 2025 the Rogue fell behind the Tacoma, Corolla, Civic and Tucson in this data. It was chosen on the 2024 ranking.
- Every figure, its source URL, retrieval time, SHA-256 and the quoted table line are in `catalog/sources/sales_us/us_sales.json`. The raw releases are archived in `catalog/sources/sales_us/raw/`.

## Gaps

These nameplates had no retrievable per-model US figure, so they could not be ranked:

- Chevrolet Equinox. Tried: https://investor.gm.com/static-files/e1bb38a4-aaf9-4141-b44a-4c61c1f2ec54, https://investor.gm.com/static-files/23adce96-ea26-4a6e-82dd-68a0042df51c, https://pressroom.gm.com/gmbx/us/en/pressroom/home/news.detail.html/Pages/news/us/en/2025/jan/0103-gmsales.html, https://investor.gm.com/news-releases/news-release-details/gm-leads-us-industry-2025-sales-6
- Chevrolet Silverado. Tried: https://investor.gm.com/static-files/e1bb38a4-aaf9-4141-b44a-4c61c1f2ec54, https://investor.gm.com/static-files/23adce96-ea26-4a6e-82dd-68a0042df51c, https://pressroom.gm.com/gmbx/us/en/pressroom/home/news.detail.html/Pages/news/us/en/2025/jan/0103-gmsales.html, https://investor.gm.com/news-releases/news-release-details/gm-leads-us-industry-2025-sales-6
- GMC Sierra. Tried: https://investor.gm.com/static-files/e1bb38a4-aaf9-4141-b44a-4c61c1f2ec54, https://investor.gm.com/static-files/23adce96-ea26-4a6e-82dd-68a0042df51c, https://pressroom.gm.com/gmbx/us/en/pressroom/home/news.detail.html/Pages/news/us/en/2025/jan/0103-gmsales.html, https://investor.gm.com/news-releases/news-release-details/gm-leads-us-industry-2025-sales-6
- Tesla Model 3. Tried: https://ir.tesla.com/press-release/tesla-fourth-quarter-2024-production-deliveries-and-deployments
- Tesla Model Y. Tried: https://ir.tesla.com/press-release/tesla-fourth-quarter-2024-production-deliveries-and-deployments

GM's release pages and PDFs returned HTTP 403 to this network. Tesla publishes global deliveries, not US sales per model.

## Mexico (INEGI RAIAVL, retail sales units)

| Catalog id | 2023 | 2024 | 2025 |
|---|---:|---:|---:|
| ford/f150 | not available | not available | not available |
| toyota/rav4 | 15,438 | 15,768 | 15,784 |
| honda/crv | 12,405 | 11,988 | 11,103 |
| toyota/camry | 2,819 | 3,923 | 3,804 |
| nissan/rogue | not available | not available | not available |
| nissan/versa | 76,926 | 93,278 | 90,223 |

Top five models in Mexico in 2025 in the INEGI data: nissan/versa (90,223), chevrolet/aveo (61,064), nissan/np300 (58,422), kia/kiak3 (56,575), nissan/march (31,401).

The F-150 and Rogue show no INEGI rows under those names. INEGI lists some sales under the selling company rather than the brand, see `catalog/README.md`.
