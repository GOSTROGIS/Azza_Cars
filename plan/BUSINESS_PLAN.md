# Ember Rent business plan

Car, van and truck rental for Surrey, BC, south of the Fraser in Metro Vancouver.

## 1. Executive summary

**The answer: launch Ember Rent as a single Surrey location renting cargo vans, pickups and light trucks to trade and logistics businesses, with a smaller car fleet for residents. Stay away from the airport and downtown. Expand to Langley Township, then the Tri-Cities, only once the Surrey unit economics are proven.**

Why this is the right first move:

1. **Surrey is the largest supply gap in Metro Vancouver.** It holds 21.6% of Metro population (568,322 people) but has 0.35 car rental locations per 10,000 residents, against a Metro average of 0.61 ([GAP_ANALYSIS](../market/GAP_ANALYSIS.md)).
2. **The truck gap is commercial.** 127 of 149 counted truck rental locations in Metro Vancouver are U-Haul, a consumer moving brand. Penske has 6 and Ryder 1. Surrey alone has 1,418 trucking businesses with employees, 57.9% of the Metro total, and 4,648 construction businesses ([GAP_ANALYSIS](../market/GAP_ANALYSIS.md), [municipalities.csv](../market/municipalities.csv)). The service area holds 3,295 mapped industrial buildings, 1,616 of them in Surrey ([service-area.json](../site/public/service-area.json)).
3. **The market is large relative to any plausible fleet.** Metro Vancouver's share of BC automotive rental and leasing revenue is C$647 to 698 million a year. A new operator's year 1 to 3 revenue on placeholder inputs is C$0.2 to 3.2 million, under 0.5% of that ([TAM_SAM_SOM](../market/TAM_SAM_SOM.md)). Growth is limited by capital and utilisation, not by demand.
4. **Surrey is short of exactly what Ember Rent rents.** Against logarithmic curves fitted across Metro, Surrey has 20 car outlets where 28.7 are expected and 0.49 commercial truck and van outlets per 1,000 trade businesses against 1.32 Metro wide, while its truck supply is 34 of 37 U-Haul (section 4.1).
5. **The airport is the wrong fight.** 18 counted car rental locations sit within 3 km of YVR, almost all majors ([GAP_ANALYSIS](../market/GAP_ANALYSIS.md)).

What could sink it: under-utilised vehicles financed with debt, rates set without a full survey (only U-Haul and Home Depot publish Surrey prices, section 4.2), insurance cost and availability for a small U-Drive fleet, and the closed ICBC replacement-rental channel (ICBC's preferred suppliers are Budget and Enterprise from 1 September 2026, per [MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)). Section 6 states these plainly.

Decisions before launch: fleet size and mix, capital and financing (Ford Credit excludes rental units from commercial purchase financing, section 11.6), site, insurance carrier, legal entity. Turo is both a price competitor and a channel for idle winter days, and owner-sourced vehicles are a phase 2 option for summer capacity (section 4.3).

## 2. Business strategy

### 2.1 Positioning

Ember Rent is a local, design-led rental brand for jobs that car share and the airport majors serve badly: a van for a day's work, a pickup for a half-day haul, a weekly car while your own is in the shop. Its promise is a clear all-in price and a fast handover ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)).

The marketing review found that the majors segment by price tier and by airport versus neighbourhood, car share by trip length and U-Haul by moving job, and that nobody positions on a fast, transparent handover for mixed cars, vans and trucks in the neighbourhoods. The gap is qualitative, not measured ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)).

### 2.2 Target segments

| Priority | Segment | Evidence | Status |
|---|---|---|---|
| 1 | Trades, contractors and small logistics firms needing vans and pickups on account | Surrey 1,418 trucking (NAICS 484) and 4,648 construction (NAICS 23) businesses. South of Fraser holds 76.4% of Metro trucking businesses ([GAP_ANALYSIS](../market/GAP_ANALYSIS.md)) | Supported by data |
| 2 | Residents renting cars for the day, weekend or week | Surrey 0.35 car rental locations per 10,000 residents, Langley Township 0.08, Delta 0.28 ([GAP_ANALYSIS](../market/GAP_ANALYSIS.md)) | Supported by data |
| 3 | Moving and hourly-job renters | Autocomplete shows "cargo van rental", "moving van rental" and "home depot van rental" intent ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)) | Qualitative only, no search volumes |
| 4 | Private-repair replacement (non-ICBC), film and event production, property managers | Named as open B2B channels in [MARKETING_REVIEW](../brand/MARKETING_REVIEW.md) | Hypothesis to test |
| Not targeted at launch | Airport and cruise visitors | 18 rental locations within 3 km of YVR and 39 within 3 km of the cruise terminal ([GAP_ANALYSIS](../market/GAP_ANALYSIS.md)) | Saturated |

One-way, long-term, EV and gig-driver demand could not be assessed from any source ([GAP_ANALYSIS](../market/GAP_ANALYSIS.md)). They are interview questions, not segments.

### 2.3 Value proposition

| For | Ember Rent offers | Versus |
|---|---|---|
| Trade accounts | Vans and pickups by the hour, half-day, day and month, monthly invoicing, named-driver lists | U-Haul's consumer moving model, Penske and Ryder's thin local presence |
| Residents | Weekly and weekend cars close to home, all-in price, quick handover | Majors concentrated in Vancouver and Richmond |
| Everyone | One price that includes every mandatory fee except government charges | Drip pricing, which is unlawful in Canada and has been penalised in car rental (section 7) |

Not yet set: rate cards, deposit, mileage policy, age rules, delivery.

### 2.4 Phased launch

| Phase | Where | What | Gate to the next phase |
|---|---|---|---|
| 1 | Surrey, near industrial and trucking employment | Vans, pickups, light trucks and a smaller car fleet | Fleet utilisation and revenue per day at or above break-even (section 11), sustained |
| 2 | Langley Township, same south of Fraser corridor | Same mix | 1 counted car rental location for 132,603 residents, 222 trucking and 1,036 construction businesses ([GAP_ANALYSIS](../market/GAP_ANALYSIS.md)) |
| 3 | Tri-Cities, near Burquitlam or Coquitlam Central | Resident car rental | Northeast sector at 0.28 car rental locations per 10,000. Burquitlam is one of three stations with no counted rental within 2 km ([GAP_ANALYSIS](../market/GAP_ANALYSIS.md)) |
| Avoid at launch | YVR, Richmond airport district, downtown, cruise terminal | | Densest concentration of majors |

Langley City is over-supplied (4.14 rental locations per 10,000, an auto-mall cluster), so phase 2 should sit in the Township away from it ([GAP_ANALYSIS](../market/GAP_ANALYSIS.md)).

## 3. Market sizing

All figures are from [TAM_SAM_SOM](../market/TAM_SAM_SOM.md) and [tam_sam_som.json](../market/tam_sam_som.json), in Canadian dollars.

| Level | Value | Method |
|---|---:|---|
| TAM, Canada | C$10,697.9 million (2024, preliminary) | StatCan table 21-10-0012, NAICS 5321 automotive equipment rental and leasing operating revenue |
| TAM, British Columbia | C$1,320.2 million (2024, preliminary) | Same table. BC grew from C$868.1 million in 2020 |
| SAM, Metro Vancouver | C$646.9 to 697.7 million | BC revenue allocated by four drivers: tourism spending 49.0%, households 51.1%, NAICS 5321 business locations 52.0%, population 52.8% |
| SAM, consumer slice only | C$252.3 to 272.1 million | SAM × 39.0%, the Canadian share of sales to individuals and households |
| SOM, years 1 to 3 | C$0.2 to 3.2 million | Bottom-up: fleet × 365 × utilisation × average daily rate, on placeholder inputs |

Operating profit margin in 2024 was 10.7% in BC and 13.0% in Canada, down from 16.8% and 17.6% in 2023. Businesses bought 57.3% of national sales, which supports a B2B-led plan ([TAM_SAM_SOM](../market/TAM_SAM_SOM.md)).

**SOM scenarios, reproduced exactly from [TAM_SAM_SOM](../market/TAM_SAM_SOM.md).** Inputs are in [som_inputs.json](../tools/market/som_inputs.json). Every fleet figure, every daily rate and the low and base utilisation are placeholders, not facts. The high-case 81% utilisation is Hertz's company-wide full-year 2025 figure.

| Scenario | Year | Fleet | Revenue (C$) | Share of SAM |
|---|---:|---:|---:|---|
| Low (60%, C$60) | 1 | 15 | 197,100 | 0.028% to 0.030% |
| Low | 2 | 25 | 328,500 | 0.047% to 0.051% |
| Low | 3 | 35 | 459,900 | 0.066% to 0.071% |
| Base (70%, C$75) | 1 | 25 | 479,062 | 0.069% to 0.074% |
| Base | 2 | 45 | 862,312 | 0.124% to 0.133% |
| Base | 3 | 70 | 1,341,375 | 0.192% to 0.207% |
| High (81%, C$90) | 1 | 40 | 1,064,340 | 0.153% to 0.165% |
| High | 2 | 80 | 2,128,680 | 0.305% to 0.329% |
| High | 3 | 120 | 3,193,020 | 0.458% to 0.494% |

**Limits.** The TAM includes passenger car leasing and RV rental, which no published table separates. 2024 is preliminary. The allocation drivers are proxies. No Metro Vancouver daily rate or utilisation figure was found. The SOM is a capacity calculation that ignores competitor response, seasonality and ramp-up ([TAM_SAM_SOM](../market/TAM_SAM_SOM.md)).

## 4. Competitive analysis

Counted rental locations (`counted = true`) in the Ember Rent service area (Surrey, Delta, White Rock, Langley City, Langley Township) were tallied for this plan from [supply.geojson](../market/supply.geojson). Metro totals are from [GAP_ANALYSIS](../market/GAP_ANALYSIS.md). Locations are storefronts, not fleet: a two-truck U-Haul dealer and a busy airport counter each count once.

| Competitor | Metro locations | Service area | Surrey | Positioning | Ember Rent angle |
|---|---:|---:|---:|---|---|
| U-Haul | 127 | 51 | 34 | "No. 1 choice of do-it-yourself movers" ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)) | Compete on in-town hourly and half-day van and pickup jobs, vehicle quality and trade accounts, not one-way moves |
| Enterprise | 23 | 6 | 3 | Neighbourhood network and body-shop replacement. ICBC preferred supplier from 1 September 2026 | Do not chase ICBC replacement. Compete on speed, trade vans and private-repair customers |
| Hertz (with Dollar, Thrifty) | 22 (Dollar 3, Thrifty 5) | 6 (Dollar 1, Thrifty 1) | 4 (Dollar 1, Thrifty 1) | Three-tier ladder, premium to deep value | One brand with a good, better, best fleet ladder |
| Alamo, National | 24, 7 | 4, 1 | 3, 1 | Enterprise group car brands, leisure and corporate | Residents' weekly and weekend cars, all-in price |
| Avis, Budget | 12, 10 | 3, 1 | 2, 1 | Avis above value brands, Budget value-conscious. Budget is an ICBC preferred supplier | Same as Enterprise |
| Penske | 6 | 2 | 1 | Commercial truck | Closest direct rival for trade trucks. Ember Rent adds vans, pickups and cars in one place |
| Ryder | 1 | 1 (Delta) | 0 | Commercial truck | Same |
| Sixt | 3 | 0 | 0 | Premium fleet, downtown Vancouver since 2022 | Premium in experience, not in fleet price |
| Discount Car and Truck Rentals | 6 | 1 | 1 | Independent car and truck | Direct like-for-like rival. Benchmark its rates |
| Routes | 2 | 1 | 1 | Independent car | Shows independents appear in local search |
| Independents and unbranded | 59 | 15 | 4 | Mixed | Win on reviews, price clarity and handover |
| Evo, Modo, Zipcar, Car2Go (carshare) | 6 points | 0 | 0 | Trips of a few hours, Vancouver and Burnaby. Evo about 2,300 and Modo 1,000 vehicles in August 2023 | Target the day, week and the jobs car share cannot do |
| Turo (peer to peer) | not counted | not counted | not counted | Marketplace with ICBC blanket insurance for BC hosts. Median Canadian host earning C$657 a month, January to October 2025 | Competitor on price and a channel for idle days. See section 4.3 |

Positioning and carshare figures are from [MARKETING_REVIEW](../brand/MARKETING_REVIEW.md) and [GAP_ANALYSIS](../market/GAP_ANALYSIS.md). Zipcar and Car2Go records may be stale. Turo listing counts were not sourced. The majors' local rates are unknown, and a rate survey is the first open item in section 13.

### 4.1 Where competition is thin

Each municipality's rental supply is measured against a logarithmic curve fitted across Metro Vancouver: the number of outlets a place of that size usually has. Supply is split by what it rents out, because a U-Haul dealer and a commercial van counter serve different customers. Above the curve is competitive (deep blood orange), below it is underserved (bone white). Method, fits and per-municipality scores: [competition.json](../market/competition.json), built by [competition.py](../tools/market/competition.py) from [municipalities.csv](../market/municipalities.csv) and [supply.geojson](../market/supply.geojson).

![Competition index by municipality: bone white is underserved, deep blood orange is competitive, with every car and truck rental outlet](../site/charts/competition-map.svg)

The index is the mean of three scores, each the distance from its curve in units of the curve's error, clipped to ±2. Hover a municipality or an outlet for its numbers. The same polygons load into [SlipCurve GIS](https://gostrogis.github.io/SLIPCURVE/modules/module-gis.html) from [competition.geojson](../market/competition.geojson).

**Cars: short everywhere outside Vancouver and Richmond.** Expected car outlets = −109.5 + 10.43 ln(residents), R² 0.49 over 17 municipalities.

![Car rental outlets against residents, with the fitted logarithmic curve](../site/charts/curve-car.svg)

| Municipality | Car outlets | Curve expects |
|---|---:|---:|
| Richmond | 48 | 18.3 |
| Vancouver | 47 | 30.3 |
| Surrey | 20 | 28.7 |
| Coquitlam | 6 | 14.7 |
| Langley Township | 1 | 13.5 |
| Delta | 3 | 11.4 |
| Maple Ridge | 3 | 9.6 |
| North Vancouver District | 2 | 9.2 |
| New Westminster | 2 | 8.1 |

**Consumer moving: saturated by one brand.** Expected U-Haul outlets = −72.8 + 7.65 ln(households), R² 0.68. U-Haul is 127 of 149 truck rental outlets in Metro. Surrey has 34 against 20.0 expected, the most over-supplied place on any of the three curves.

![U-Haul outlets against households, with the fitted logarithmic curve](../site/charts/curve-moving.svg)

**Commercial trucks and vans: thin everywhere, thinnest per business in Surrey.** Expected outlets = −5.9 + 1.16 ln(trucking, construction and warehousing businesses), R² 0.64. Metro has 22 commercial truck and van outlets for 16,631 such businesses, 1.32 per 1,000. Surrey has 3 for 6,125, 0.49 per 1,000, against Vancouver 1.71, Delta 3.06 and Langley Township 3.92. The curve flattens with size, so on the curve Surrey reads 3 against 4.2 expected: close to it, but the largest base of trade customers in Metro.

![Commercial truck and van outlets against trade businesses, with the fitted logarithmic curve](../site/charts/curve-commercial.svg)

**What each place rents out.** Grey is U-Haul, orange is commercial truck and van.

![Rental outlets by municipality and by what they rent out](../site/charts/rental-mix.svg)

| Municipality | Index | Notable gaps |
|---|---:|---|
| North Vancouver District | −0.97 | No commercial truck or van rental. 2 car outlets against 9.2 expected |
| Coquitlam | −0.82 | 6 of 7 truck outlets are U-Haul. No car share. Burquitlam Station has no rental within 2 km |
| Maple Ridge | −0.51 | 5 of 6 truck outlets are U-Haul |
| New Westminster | −0.47 | All 7 truck outlets are U-Haul. No commercial truck or van rental |
| North Vancouver City | −0.39 | All 3 truck outlets are U-Haul |
| Port Coquitlam | −0.33 | 1 car outlet against 5.5 expected |
| West Vancouver | −0.23 | No truck or van rental |
| Burnaby | −0.21 | Production Way-University Station has no rental within 2 km |
| Richmond | −0.10 | Car supply 48 against 18.3, truck supply 8 of 9 U-Haul. No car share |
| Surrey | −0.02 | 34 of 37 truck outlets are U-Haul. 0.49 commercial outlets per 1,000 trade businesses. No car share |
| Langley Township | −0.02 | 1 car outlet against 13.5 expected. No car share |
| Port Moody | 0.00 | No car or truck rental |
| White Rock | 0.00 | No car or truck rental |
| Delta | +0.07 | No car share |
| Pitt Meadows | +0.26 | No car rental. All 4 truck outlets are U-Haul |
| Langley City | +0.50 | Auto-mall cluster. All 4 truck outlets are U-Haul |
| Vancouver | +1.06 | 27 of 31 truck outlets are U-Haul |

**What this means for the launch.** Surrey's index is neutral because a surplus of U-Haul dealers offsets a shortage of cars and commercial vehicles. Ember Rent's fleet is cars, vans and pickups for trade, the two kinds Surrey is short of, and nothing that competes with U-Haul's one-way moves. The deepest bone-white areas, North Vancouver District and Coquitlam, are resident car markets with little trade base. They suit the phase 3 Tri-Cities car location, not a trade fleet. The index counts outlets, not vehicles, and treats a two-truck dealer the same as a large depot.

### 4.2 Published rates

Retrieved 23 November 2026. Before tax.

Sources: [U-Haul](https://www.uhaul.com/Truck-Rentals/) Surrey in-town quote for a 3 December 2026 pickup. [Home Depot](https://www.homedepot.ca/en/home/tool-and-vehicle-rental.html) national page, Surrey store not confirmed. [DOZR](https://dozr.com/rent/truck/cargo-van/Surrey-BC) listing from an unnamed Surrey supplier.

| Operator | Vehicle | Rate | Kilometres |
|---|---|---:|---|
| U-Haul | Cargo van | C$19.95 per rental | C$0.99/km |
| U-Haul | 10 ft truck | C$19.95 per rental | C$1.09/km |
| U-Haul | 15 ft truck | C$29.95 per rental | C$1.09/km |
| Home Depot | Small cargo van, pickup | C$24.95 first 90 min, C$79.95 4 h, C$119.95/day | Unlimited |
| Home Depot | Large cargo van | C$39.00 first 90 min, C$94.00 4 h, C$139.95/day | Unlimited |
| DOZR | Cargo van | C$126/day, C$756/week, C$3,024/4 weeks | Not stated |

U-Haul adds a C$1.00 environmental fee per rental.

Enterprise, Budget, Penske and Discount publish no Surrey rates outside their booking engines. KAYAK shows user-found Surrey car rates of C$24 to C$33 a day for small and midsize cars, and C$53 to C$92 for pickups, over the last 12 months ([KAYAK](https://www.ca.kayak.com/Surrey-Pickup-Truck-Rentals.6168.cpk.ksp)). These are historical searches, not quotes.

| Policy | Enterprise Surrey | Home Depot Canada |
|---|---|---|
| Minimum age | 21 | 21 |
| Under 25 | C$20/day, vans and pickups up to ¾ ton only | |
| Deposit | C$300 (non-commercial renters) | C$500 |
| Damage waiver | C$9.99 to 52.99/day, trucks. C$32.99 to 79.99/day, cars | Not sold. Renter must carry non-owned auto liability |
| Source | [Truck](https://www.enterprise.com/en/car-rental-locations/ca/bc/surrey-truck-rental-c45t.html), [cars](https://www.enterprise.com/en/car-rental-locations/ca/bc/surrey-newton-c402.html) | [Home Depot](https://www.homedepot.ca/en/home/tool-and-vehicle-rental.html) |

**Where Ember Rent sits.** U-Haul and Home Depot lead with short-hire prices under C$25. Ember Rent's all-in daily price competes against Home Depot's C$119.95 to C$139.95 day rate with unlimited kilometres and against Enterprise's day rate plus its waiver, not against U-Haul's per-rental headline.

### 4.3 Rent-by-owner

Rent-by-owner is the Airbnb model for vehicles: private owners list their own cars, vans and trucks on a platform, which takes a share and supplies insurance during the trip.

**The market in BC.** Turo is the only peer-to-peer vehicle platform found operating in BC ([Turo eligibility](https://help.turo.com/en_us/meeting-vehicle-requirements-or-canada-ryYjTRW8c.md)). Getaround wound down its US business in February 2025 ([PYMNTS](https://www.pymnts.com/transportation/ridesharing/2025/carsharing-marketplaces-getaround-and-hyrecar-wind-down-us-operations/)). No Canadian operation was found for Getaround or Fluid Truck. Evo, Modo and Communauto run their own fleets. Turo reported a 73% rise in Vancouver vehicles listed in March 2026 against a year earlier ([Canadian Auto Dealer](https://canadianautodealer.ca/?p=76738)). Canadian hosts passed C$300 million in cumulative earnings by July 2025 ([Auto Remarketing](https://www.autoremarketing.com/arcanada/canadian-car-owners-earnings-through-turo-reach-300-million-milestone/)). Canada is under 10% of Turo's net revenue ([Turo S-1/A](https://www.sec.gov/Archives/edgar/data/1514587/000162828024047889/turoinc-sx1a12.htm)). No BC host or vehicle count is published.

**How the host model works in BC.**

| Item | Terms | Source |
|---|---|---|
| Host share of trip price | 85%, 75% or 65%, by plan, since 31 March 2026 | [Turo](https://help.turo.com/en_us/earnings-plans-in-detail-canada-hosts-Hk8uLEgEq.md) |
| Host damage responsibility per claim, during the trip | C$2,000, C$250 or none, by plan | same |
| Third-party liability | C$2,000,000 through ICBC during the trip. None while the host delivers the vehicle in BC | same |
| ICBC blanket | Turo holds ICBC Basic and Optional blanket coverage. Basic blanket gives accident benefits and C$200,000 third-party liability. Owners must still declare the use to their Autoplan broker | [ICBC](https://icbc.com/insurance/commercial/peer-to-peer-vehicle-rental) |
| Weight limit | Peer-to-peer use only for vehicles of 5,000 kg GVW or less, and not for vehicles owned by or leased to the platform | [ICBC tariff, s. 2.15](https://www.icbc.com/assets/en/6PyY5DEcoIT7z2ujjlwb3d/basic-tariff.pdf) |
| Vehicle limits | Up to 12 years old, under 200,000 km, 9 seats or fewer, no commercial licence. Box trucks in BC up to 5,000 kg and under 26 ft | [Turo eligibility](https://help.turo.com/en_us/meeting-vehicle-requirements-or-canada-ryYjTRW8c.md), [box trucks](https://help.turo.com/en_us/box-trucks-hosts-Sk111wtlkl.md) |
| Account closure | Immediate for fraud or safety reasons. A cancellation rate above 5% unlists vehicles for 7 days, above 10% starts closure | [Turo](https://help.turo.com/en_us/turo-initiated-account-closures-hosts-H1VFT5tQp.md), [cancellations](https://help.turo.com/en_us/canceling-a-trip-with-your-guest-hosts-HkkzLVlE5.md) |
| BC rental tax | PVRT applies (R4), plus PST of 7% to 20% by vehicle value | [BC PST 116](https://www2.gov.bc.ca/assets/gov/taxes/sales-taxes/publications/pst-116-motor-vehicle-dealers-leasing-companies.pdf) |

**Turo prices for vans in Metro Vancouver.** One snapshot of 3-day trips: Ford Transit from C$70 to C$267 a day ([Turo](https://turo.com/ca/en/van-rental/canada/vancouver-bc), cached 10 November 2026). Hosts set prices, so this is a range, not an average.

**Three ways Ember Rent can use it.**

1. **Competitor.** Turo vans and pickups compete on price for residents and small jobs. The limits in the table above leave large vans, commercial-licence vehicles, heavier trucks and delivery outside what a Turo host can offer safely. Ember Rent's account billing and trade fleet are outside it too.
2. **Channel for idle days.** Cars that meet Turo's limits can be listed in the winter trough (section 6). On the highest-share plan Ember Rent keeps 85% of the trip price and carries up to C$2,000 per claim. A vehicle rated U-Drive for Ember Rent's own rentals and also used under Turo's blanket needs its use confirmed with an Autoplan broker first (ICBC tariff s. 2.15).
3. **Fleet-light sourcing, the host-management model.** Ember Rent rents owners' vehicles under its brand and splits revenue, as Airbnb management companies do for homes. The only published splits are Turo's US passive-income program, 70% to the owner and 30% to the manager ([Turo](https://turo.com/blog/news/turo-launches-passive-income-hosting-in-the-united-states/)), and one US manager's 30% fee. The program is US only. Ember Rent's 30% would have to cover cleaning, handover, claims handling and damage responsibility. It adds vehicles without capital, which matters most for the summer peak. Three questions decide whether it is legal and insurable: whether owners' vehicles rented through Ember Rent's own booking channel must each be rated U-Drive by ICBC, who collects PVRT and PST, and whether Surrey's Automobile/Truck Rental licence covers it.

**What this changes in the plan.** Phase 1 keeps an owned or leased trade fleet. The winter idle days go to Turo where vehicles qualify (go-to-market step 7). Fleet-light sourcing is a phase 2 option for summer capacity, after an ICBC broker and a lawyer answer the three questions above.

## 5. Why it wins

1. **It enters where supply is thinnest and business demand is densest.** Surrey has 6.0 truck rental locations per 1,000 trucking, warehousing and construction businesses against 9.0 Metro wide ([GAP_ANALYSIS](../market/GAP_ANALYSIS.md)).
2. **It sells to businesses, which buy most of the market.** 57.3% of national NAICS 5321 sales go to businesses ([TAM_SAM_SOM](../market/TAM_SAM_SOM.md)). Trade accounts repeat, which lowers acquisition cost.
3. **Local search cannot be bought.** Google ranks local results on relevance, distance and prominence, and review count and score feed prominence ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)). A well-run single location with steady reviews can outrank a distant major for "cargo van rental surrey".
4. **Compliance becomes the brand promise.** All-in pricing is mandatory under the Competition Act, so a transparent price costs nothing extra and contrasts with past enforcement against car rental companies ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)).
5. **Marketplaces can fill idle days from day one.** Rentalcars.com Marketplace, Discover Cars and Expedia accept smaller suppliers ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)).
6. **The fleet scales one vehicle at a time.** Revenue per vehicle is linear in utilisation and rate, so capacity is added only when demand is shown.

## 6. Why it fails

In rough order of how likely each is to end the business.

1. **Low utilisation on financed vehicles.** Revenue per vehicle at C$75 a day falls from C$19,162 at 70% utilisation to C$13,688 at 50% ([TAM_SAM_SOM](../market/TAM_SAM_SOM.md)). Financing, insurance and depreciation do not fall with it. The 81% benchmark is a US-dominated major and a new independent should not assume it.
2. **Rates set blind.** No Vancouver rate benchmark was found ([TAM_SAM_SOM](../market/TAM_SAM_SOM.md), [MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)). Pricing too low loses money on every day rented, too high leaves vehicles idle.
3. **Insurance cost or availability.** A U-Drive fleet is rated separately by ICBC (section 7) and optional coverage must be placed with a carrier. The cost is unknown until quoted, and it could break the unit economics for a small fleet.
4. **Thin margins industry wide.** BC operating margin fell from 16.8% in 2023 to 10.7% in 2024 ([TAM_SAM_SOM](../market/TAM_SAM_SOM.md)).
5. **Damage, theft and bad debt.** Vans and trucks used for trade work take more wear, and trade accounts on monthly invoice create receivables risk.
6. **The majors respond.** Enterprise, Hertz and Alamo already have Surrey locations, and U-Haul has 34 ([supply.geojson](../market/supply.geojson)). They can discount locally.
7. **The ICBC channel stays closed.** Only preferred suppliers bill ICBC directly, and ICBC does not authorise EV loss-of-use rentals ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)). Replacement-rental revenue may be small.
8. **The name has to be changed.** The trademark search for Ember Rent is pending, and a UK transport company called Ember operates intercity buses ([NAMING](../brand/NAMING.md)). A forced rebrand after launch would waste the review history tied to the Google profile name.
9. **Wrong site.** Only zone CHI expressly permits vehicle rental (R7). Visibility and parking capacity are not covered by any data in this repository ([GAP_ANALYSIS](../market/GAP_ANALYSIS.md)).
10. **Seasonality.** Demand peaks in summer. Canada's CPI for passenger vehicle rental ran 170.6 in June to August 2025 against 135.4 in January and February ([StatCan 18-10-0004](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401)). Overnight non-resident tourists entering through BC peaked at 728,338 in July 2025 against 258,141 in November ([StatCan 24-10-0053](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2410005301)). BC construction employment ranged from 250,600 in February 2025 to 284,900 in July 2026 ([StatCan 14-10-0022](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410002201)). A fleet sized for July sits idle in winter.

## 7. Risk matrix

| # | Risk | Likelihood | Impact | Mitigation | With |
|---|---|---|---|---|---|
| R1 | Utilisation below break-even | High | High | Start with a small fleet, lease or finance on short terms, list cars on one marketplace for fill, add vehicles only when utilisation holds | — |
| R2 | Rates set without a benchmark | High | Med | Rate survey of Enterprise, Budget, U-Haul, Penske and two independents for identical dates before launch | — |
| R3 | **Drip pricing.** Under Competition Act amendments in force since June 2022, mandatory fees must be in the advertised price and only government-imposed charges such as sales tax may be added. Car rental companies have paid a total of C$5.95 million in penalties over drip pricing ([Competition Bureau, 2022](https://www.canada.ca/en/competition-bureau/news/2022/06/important-amendments-to-the-competition-act-come-into-effect.html), [Competition Bureau, 2018](https://www.canada.ca/en/competition-bureau/news/2018/10/discount-car-rental-penalised-for-advertising-unattainable-prices.html), via [MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)) | Low if designed in | High | Every advertised and quoted price includes all mandatory fees. Legal review of the booking flow, ads and marketplace listings | Lawyer |
| R4 | **BC Passenger Vehicle Rental Tax.** C$1.50 per day or portion of a day on passenger vehicles rented for more than 8 consecutive hours and 28 consecutive days or less, collected on top of PST and with GST charged on it ([PST 116](https://www2.gov.bc.ca/assets/gov/taxes/sales-taxes/publications/pst-116-motor-vehicle-dealers-leasing-companies.pdf)). Passenger vehicles include trucks and vans of ¾ ton or less, so 1500- and 2500-series vans and pickups carry PVRT. Trucks and vans larger than ¾ ton do not ([PST 308](https://www2.gov.bc.ca/assets/gov/taxes/sales-taxes/publications/pst-308-vehicles.pdf)) | Med | Med | Register for PST before launch. Charge PVRT on every car and on ¾-ton-or-smaller vans and pickups as a separate government charge. Get a Consumer Taxation Branch ruling on borderline models | Accountant |
| R5 | **ICBC rental-vehicle insurance and licensing.** ICBC rates "U-Drive" vehicles, defined as "a vehicle available for hire or rental, without driver, by the hour or otherwise, for a period of less than one month", in class 008 for passenger vehicles and 018 for commercial vehicles of 5,000 kg GVW or less ([ICBC Basic Insurance Tariff](https://www.icbc.com/assets/en/6PyY5DEcoIT7z2ujjlwb3d/basic-tariff.pdf)). Fleetplan: optional from 5 vehicles, mandatory above 19 (tariff) or 20 ([ICBC page](https://icbc.com/insurance/commercial)). Estimated Basic: C$3,699 a vehicle a year (base rate C$903.55 × class 008 Lower Mainland factor 4.094), before fleet and vehicle multipliers and before optional coverage from ICBC or a private broker | Med | High | Quote U-Drive Basic and optional coverage through an Autoplan broker before ordering vehicles, and confirm Surrey's territory and the Fleetplan threshold. Rentals of a month or more fall outside the U-Drive definition, so price and insure long-term rentals separately | Broker |
| R6 | **Commercial vehicle safety.** A truck licensed above 5,000 kg GVW and used in business is a commercial motor vehicle, and its owner is a carrier that must hold a National Safety Code certificate. A lessee becomes a carrier only on a lease of one month or more ([MVA Regulations, Division 37](https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/26_58_12)). Trailers count toward licensed GVW | Med | Med | Licence every launch truck under 5,000 kg GVW, including any trailer, which also keeps it within zone CHI (R7). Ask the NSC Program Office whether a short-term business renter needs its own certificate before going heavier | — |
| R7 | **Surrey zoning and business licence.** The Automobile/Truck Rental licence is C$481 a year ([Business License By-law 13680](https://www.surrey.ca/city-government/bylaws/13680)). Zone CHI, outside the City Centre, permits "Sales and rentals of vehicles, less than 5,000 kg G.V.W." ([Zoning By-law 12000](https://www.surrey.ca/city-government/bylaws/12000)). Other zones allow "general service uses", defined to include rentals, unconfirmed for vehicle rental. Surrey advises a Zoning Inquiry Form before signing any lease ([City of Surrey](https://www.surrey.ca/business-economy/business-licensing)) | Med | High | Shortlist CHI sites first. Zoning inquiry on every shortlisted site before a lease is signed | — |
| R8 | Insurance cost too high for a small fleet | Med | High | Get two or more quotes for optional and garage coverage. Model the premium per vehicle in section 11 before committing | Broker |
| R9 | Trademark conflict over "Ember" | Med | High | CIPO and USPTO searches by a trademark agent in Nice classes 12, 35 and 39 before signage and the Google profile go live ([NAMING](../brand/NAMING.md)) | Agent |
| R10 | Damage, theft, unpaid invoices | Med | Med | Deposits, driver checks, telematics, credit limits and terms for accounts | Operations lead |
| R11 | Majors cut prices locally | Med | Med | Compete on vans, trade accounts and service rather than car price | — |
| R12 | Marketplace dependence, including Turo (R14) | Low | Med | Cap the share of fleet days sold through marketplaces | — |
| R13 | Privacy of driver licence and payment data | Med | Med | Obtain legal advice on BC private-sector privacy law and payment-card rules before collecting customer data | Lawyer |
| R14 | **Turo account closure or plan change.** Closure can be immediate and host shares are set by Turo (section 4.3) | Low | Med | Keep Turo to idle days only. Keep cancellations under 5%. Keep direct booking as the main channel | — |
| R15 | **Owner-sourced vehicles uninsured for rental use.** An owner who does not declare rental use risks the policy being cancelled for misrepresentation ([Turo S-1/A](https://www.sec.gov/Archives/edgar/data/1514587/000162828024047889/turoinc-sx1a12.htm)) | Med | High | No fleet-light vehicle goes live until ICBC rating, owner declaration and endorsements are confirmed by a broker | Broker |

## 8. Prerequisites and launch checklist

| Area | Item | Status | Note |
|---|---|---|---|
| Market | Gap analysis and market sizing | done | [GAP_ANALYSIS](../market/GAP_ANALYSIS.md), [TAM_SAM_SOM](../market/TAM_SAM_SOM.md) |
| Market | Competitor rate survey | partial | U-Haul and Home Depot published (section 4.2). Enterprise, Budget, Penske and Discount must be quoted by hand |
| Market | 10 to 20 customer interviews with trades and logistics firms | open | Tests segments 1 and 4 |
| Legal | Legal entity (sole proprietorship, partnership, corporation) | decision | |
| Legal | BC Registry name approval and registration as "Ember Rent" | open | Name must match signage and Google profile ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)) |
| Legal | Rental agreement, damage policy, deposit terms, privacy policy | open | Lawyer to draft |
| Legal | All-in pricing review of site, ads and listings | open | R3 |
| Tax | GST and PST registration, PVRT setup | open | R4 |
| Licensing | Surrey zoning inquiry, CHI sites first, and Automobile/Truck Rental licence (C$481 a year) | open | R7 |
| Licensing | ICBC U-Drive registration and insurance for each vehicle | open | R5 |
| Licensing | National Safety Code certificate, if any vehicle over 5,000 kg GVW including its trailer | open | R6 |
| Insurance | Carrier or broker for optional, garage and general liability coverage | decision | |
| Financing | Capital available and financing structure (cash, lease, loan, fleet line) | decision | |
| Fleet | Size and mix by class | decision | Section 10 |
| Location | Site in Surrey near industrial employment | decision | 1,616 mapped industrial buildings in Surrey ([service-area.json](../site/public/service-area.json)) |
| Systems | Booking, fleet and payments system | decision | Vendor prices in section 10.4 |
| Insurance | Broker confirms Turo listing of U-Drive-rated vehicles, and the rating for owner-sourced vehicles | open | Section 4.3, R15 |
| Brand | Name chosen: Ember Rent | done | [NAMING](../brand/NAMING.md) recommended Keyhand, with Ember second |
| Brand | Trademark search (CIPO, USPTO) | open | Pending ([NAMING](../brand/NAMING.md)) |
| Brand | emberrent.com and emberrent.ca registered | open | Reported available by GoDaddy on 22 November 2026, which is not a reservation ([NAMING](../brand/NAMING.md)) |
| Brand | X handle @emberrent claimed | open | Free on 22 November 2026 ([NAMING](../brand/NAMING.md)) |
| Brand | Logo and mark | done | [brand/logo](../brand/logo/README.md) |
| Digital | Website with all-in prices, city and vehicle pages | open | Landing page exists in `site/`. Prices and inventory pending |
| Digital | Google Business Profile verified at the real address | open | Needs the site and signage first |
| Digital | Booking conversion tracking with value | open | |
| Sales | List of 30 trade, production and property-management prospects | open | [MARKETING_REVIEW](../brand/MARKETING_REVIEW.md) |
| Staffing | Roles, hours, hiring | decision | Section 10 |

## 9. Go-to-market plan

Taken from the prioritised plan in [MARKETING_REVIEW](../brand/MARKETING_REVIEW.md), narrowed to phase 1 in Surrey. Ranked by expected impact for cost.

| # | When | Action | Metric |
|---|---|---|---|
| 1 | Weeks −8 to 0 | Clear and register the name, domains and handles. Register the trade name exactly as it will appear on signage | Name cleared, domains held |
| 2 | Weeks −8 to 0 | Verify one Google Business Profile at the Surrey site, most specific primary category, vehicle types as services, real photos. Keywords cannot go in the profile name ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)) | Profile verified |
| 3 | Weeks −8 to 0 | Site pages for Surrey and each vehicle type (cargo van, pickup, moving truck, car), all-in prices, booking tracked with value | Booking conversion tracked |
| 4 | Months 0 to 3 | Search ads on van and truck terms around Surrey, location assets with call buttons, manual or maximise-conversions bidding first | Cost per booking, revenue per day |
| 5 | Months 0 to 3 | Text a review link at every return. Steady weekly flow, never paid reviews | Reviews per week, rating |
| 6 | Months 0 to 6 | Field sales to 30 trade, production and property-management accounts, and body shops for non-ICBC repairs, with monthly invoicing | Active accounts, share of revenue |
| 7 | First winter | List vehicles that meet Turo's limits (section 4.3) on Turo, and cars on one rental marketplace, to fill the winter trough | Utilisation, marketplace share of days |
| 8 | Months 3 to 9 | Referral credit for customers and accounts | Referred bookings |
| 9 | Phase 2 | Repeat steps 2 to 6 for Langley Township | Same |

Search volumes and cost per click were not available, so no ad budget is set here. Run Google Ads Keyword Planner once the account exists ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)).

## 10. Operations plan outline

### 10.1 Fleet mix

| Class | Purpose | Units at launch | Notes |
|---|---|---|---|
| Cargo vans | Trade, moving, hourly jobs | — | Lead class, from segment 1 |
| Pickups | Hauling, trade | — | Autocomplete shows distinct pickup demand ([NAMING](../brand/NAMING.md)) |
| Light trucks, under 5,000 kg GVW including any trailer | Moving, logistics | — | Stays outside NSC (R6), in ICBC class 018 (R5) and within zone CHI's rental limit (R7) |
| Cars, good, better, best classes | Residents, repair-period renters | — | ICBC loss-of-use rentals are limited to similar-size vehicles and exclude EVs ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)) |

Total fleet, makes and models, buy versus lease, and the year 1 to 3 growth path are not set. The SOM placeholders range from 15 to 40 vehicles in year 1 ([som_inputs.json](../tools/market/som_inputs.json)). The vehicles modelled in [SELECTION.md](../vehicles/SELECTION.md) were chosen by US and Mexico sales rank for the website's 3D catalogue and are not a BC fleet recommendation.

### 10.2 Location requirements

| Requirement | Specification |
|---|---|
| Area | Surrey, near industrial and trucking employment |
| Zoning | Confirmed through Surrey's Zoning Inquiry Form before a lease. Zone CHI first (R7) |
| Parking | Space for the full fleet plus customer vehicles |
| Access | Clearance and turning room for trucks |
| Visibility | Signage matching the registered name ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)) |
| Handover | Staffed counter or key boxes. Keycafe, a Vancouver firm, sells key systems to rental companies ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)) |
| Address, lease term and rent | — |

### 10.3 Staffing

Roles: counter and handover, cleaning and turnaround, maintenance coordination, B2B sales, bookkeeping. Headcount, hours and wages are not set.

### 10.4 Booking system

Requirements: online booking with all-in prices, PVRT and taxes as separate government charges, deposits and card pre-authorisation, driver licence capture, account billing for trade customers, utilisation and revenue-per-day reporting by class, and a marketplace connection later.

| Vendor | Published price | Source |
|---|---|---|
| HQ Rental Software | US$120/month up to 10 vehicles, US$175 up to 25, US$250 up to 50. Onboarding US$550 to 1,500. Currency shown by a US flag, not stated | [HQ](https://hqrentalsoftware.com/pricing) |
| RentSyst | €55/month flat to 15 vehicles, then €3.00 per vehicle to 50. Excludes VAT | [RentSyst](https://rentsyst.com/price/) |
| Booqable | 35, 87 or 187 a month by tier. Currency not shown | [Booqable](https://booqable.com/pricing) |
| Rent Centric, TSD, RENTALL | Quote on request. RENTALL needs at least 10 vehicles | [Rent Centric](https://www.rentcentric.com/), [TSD](https://www.tsdweb.com/), [RENTALL](https://www.navotar.com/pricing) |

### 10.5 Maintenance

Schedule by manufacturer interval, a check and clean at every return, damage photos at handover and return, and a target turnaround time per class. Service provider (in-house or a Surrey shop) and tyre and repair budgets are not set. Commercial vehicles above 5,000 kg GVW bring CVSE inspection duties (R6).

## 11. Financial plan

Inputs stay blank until costs are quoted. Cited inputs carry their source.

### 11.1 Inputs

| Symbol | Input | Value | Source |
|---|---|---|---|
| N | Fleet size | ___ | |
| U | Time utilisation (rented days ÷ available days) | ___ | Benchmark only: 81%, Hertz company-wide 2025 ([TAM_SAM_SOM](../market/TAM_SAM_SOM.md)) |
| R | Average daily rate, all-in, excluding taxes and PVRT | ___ | Benchmarks in section 4.2 |
| v | Variable cost per rented day (cleaning, card fees, wear, fuel loss, marketplace commission) | ___ | |
| H | Annual holding cost per vehicle (depreciation or lease, interest, ICBC and optional insurance, registration, scheduled maintenance) | ___ | Vehicle prices, finance and residuals in section 11.6 |
| F | Annual fixed cost (rent, wages, software, marketing, professional fees) | ___ | |
| t | PVRT per rental day on cars and on vans and pickups of ¾ ton or less | C$1.50 | Pass-through, not revenue (R4) |

### 11.2 Unit economics

* Rented days per vehicle per year: D = 365 × U
* Revenue per vehicle per year: Rev = D × R
* Contribution per vehicle per year: C = D × (R − v) − H
* Business profit before tax: P = N × C − F

PVRT and sales taxes are collected and remitted, so they sit outside R.

### 11.3 Break-even

* Break-even fleet at a given utilisation and rate: N* = F ÷ [365 × U × (R − v) − H]
* Break-even utilisation for a given fleet: U* = (F ÷ N + H) ÷ [365 × (R − v)]
* Break-even daily rate: R* = v + (F ÷ N + H) ÷ (365 × U)

If 365 × U × (R − v) is less than or equal to H, each added vehicle loses money and no fleet size breaks even.

### 11.4 Sensitivity table structure

Revenue per vehicle per year (365 × U × R) is cited from [TAM_SAM_SOM](../market/TAM_SAM_SOM.md). The rates and the 50% to 70% utilisation rows are illustrative grid points, not facts. Contribution rows stay blank until v and H are known.

| Utilisation \ daily rate (C$) | 50 | 60 | 75 | 90 | 110 |
|---|---:|---:|---:|---:|---:|
| 50% revenue | 9,125 | 10,950 | 13,688 | 16,425 | 20,075 |
| 60% revenue | 10,950 | 13,140 | 16,425 | 19,710 | 24,090 |
| 70% revenue | 12,775 | 15,330 | 19,162 | 22,995 | 28,105 |
| 81% revenue | 14,783 | 17,739 | 22,174 | 26,609 | 32,522 |
| 50% contribution (C) | ___ | ___ | ___ | ___ | ___ |
| 60% contribution (C) | ___ | ___ | ___ | ___ | ___ |
| 70% contribution (C) | ___ | ___ | ___ | ___ | ___ |
| 81% contribution (C) | ___ | ___ | ___ | ___ | ___ |

Build one grid per vehicle class: vans, pickups and cars will not share R, v or H.

### 11.5 Capital requirement

Start-up capital = vehicle down payments or purchase + site fit-out and deposit + insurance deposits + systems setup + pre-launch marketing + working capital for the months to break-even.

### 11.6 Vehicle cost benchmarks

Retrieved 23 November 2026. Base MSRP before freight, PDI and taxes.

| Vehicle | Base MSRP (C$) | Freight and PDI (C$) | Source |
|---|---:|---:|---|
| Mercedes-Benz Sprinter cargo, 144 in | 58,990 | 6,995 | [Mercedes-Benz Vans](https://www.mercedes-benz-vans.ca/en/sprinter), freight via [Driving.ca](https://driving.ca/mercedes-benz/sprinter-cargo-van) |
| Ram ProMaster 1500 Tradesman, low roof 118 in | 58,520 | 3,095 | [Ram window sticker](https://www.ramtruck.ca/en/windowsticker/3c6lrvngxte202580?&campaign=) |
| Ford Transit T-150 cargo, low roof 130 in | 59,900 | 2,995 | [Driving.ca](https://driving.ca/ford/transit-van/2026) |
| Ford F-150 XL regular cab | 52,690 | 2,695 | [Driving.ca](https://driving.ca/ford/f-150/2026) |
| Ram 1500 Tradesman quad cab 4x4 | 59,495 | 2,695 | [Driving.ca](https://driving.ca/2026/cheapest-ram-cars) |
| Chevrolet Silverado 1500 WT regular cab | 48,999 | 2,700 | [Driving.ca](https://driving.ca/chevrolet/silverado-1500/2026) |
| Hyundai Elantra Essential | 23,499 | 1,900 | [Driving.ca](https://driving.ca/hyundai/elantra) |
| Toyota Corolla L | 25,020 | 1,760 | [Driving.ca](https://driving.ca/2026/cheapest-sedans). Toyota's launch release said 24,520 ([Toyota](https://media.toyota.ca/en/releases/2025/what-s-new--the-2026-toyota-corolla.html)) |
| Honda Civic LX | 28,440 | 1,830 | [Driving.ca](https://driving.ca/2026/cheapest-honda-cars) |

Driving.ca rows are not confirmed on the manufacturer's own price builder.

**Financing.** Prime was 4.70% on 18 November 2026 ([Bank of Canada](https://www.bankofcanada.ca/valet/observations/V39079,V80691311/json)). Ford Credit Canada lists "Rental units" as ineligible for Commercial Purchase financing ([Ford Credit](https://www.ford.ca/finance/commercial-financing/commercial-purchase)), so retail captive offers cannot be assumed for a rental fleet. Mercedes-Benz advertises 2.99% over 60 months on the Sprinter 2500 144 in cargo to 31 December 2026 ([Mercedes-Benz Vans](https://www.mercedes-benz-vans.ca/en/home)), eligibility for rental use not stated. An equipment-finance broker quotes 6.5% to 10% for credit scores of 700 and up ([Iron Finance](https://www.ironfinance.ca/guides/compare-equipment-loan-rates-canada)).

**Residual value.** Canadian Black Book: 2023 vehicles kept 57.0% of MSRP after 4 years on average, down from 67.5% a year earlier ([CBB](https://www.canadianblackbook.com/canadian-black-book-announces-2026-best-retained-value-awards/)). Published 36-month lease residuals: Elantra 53% to 56%, Civic 56% to 60%, Ram 1500 Tradesman 42% to 45%, Silverado WT 40% to 43%, depending on kilometres ([drivemybudget.ca](https://drivemybudget.ca/ca/on/ram/2026-1500dt-tradesman/), Ontario rate sheets). These are subsidised retail lease figures, not resale values for high-kilometre rental units. Model-level residuals for the cargo vans were not found.

## 12. Milestones and KPIs

| Milestone | Target date | Exit criterion |
|---|---|---|
| Name cleared and registered | — | Agent's clearance, domains held, BC Registry name |
| Majors' rate survey and customer interviews done | — | Rates and segment priorities set |
| Site signed | — | Zoning confirmed, licence applied |
| Insurance bound and fleet registered | — | ICBC U-Drive cover in force |
| Launch | — | Profile verified, booking live |
| Phase 2 decision | — | Phase 1 KPIs at target |

| KPI | Definition | Target |
|---|---|---|
| Utilisation by class | Rented days ÷ available days, weekly. The measure Hertz reports ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)) | At or above U* |
| Revenue per day by class | Rental revenue ÷ rented days, weekly | At or above R* |
| Contribution per vehicle | Section 11.2 | Positive by class |
| Active trade accounts | Accounts with a rental in the last 90 days | — |
| B2B share of revenue | Account revenue ÷ total | — |
| Reviews per week and rating | Google profile | — |
| Cost per booking | Ad spend ÷ ad-attributed bookings | — |
| Damage and bad-debt cost | As % of revenue | — |

## 13. Open questions

1. What do Enterprise, Budget, Penske and Discount charge in Surrey for the same dates? Their booking engines must be quoted by hand (section 4.2 has U-Haul and Home Depot). This sets R.
2. What will ICBC U-Drive Basic and optional coverage cost per class below the Fleetplan threshold (R5)? This sets most of H.
3. Does PVRT apply to rentals through Turo, and who collects it? The PST Act makes a registered online marketplace facilitator the collector, but no bulletin covers vehicles.
4. Does a short-term business renter of a truck over 5,000 kg need its own NSC certificate as well as Ember Rent's? The regulation and CVSE's guide differ.
5. Will trades actually rent on account? Interview 10 to 20 Surrey firms.
6. Does "Ember Rent" clear CIPO and USPTO in classes 12, 35 and 39?
7. What capital is available, and on what financing terms? Captive retail offers may not apply to rental units (section 11.6).
8. Which sites in Surrey pass the zoning inquiry, and what do they cost?
9. How large is the winter trough for vans and pickups specifically? National proxies show a summer peak (section 6), not a fleet-level figure.
10. How does a non-preferred supplier get paid on ICBC claims, and does ICBC run a supplier selection process ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md))?
11. Must owners' vehicles rented through Ember Rent's own booking channel each be rated U-Drive by ICBC?
12. On owner-sourced vehicles rented through Ember Rent, does Ember Rent or the owner collect and remit PVRT and PST?
13. Does the Automobile/Truck Rental licence cover renting owner-sourced vehicles, and does Surrey Planning treat vehicle rental as a general service use outside zone CHI?

## 14. Sources

Repository files:

* [market/GAP_ANALYSIS.md](../market/GAP_ANALYSIS.md), with sources and hashes in [market/sources/provenance.json](../market/sources/provenance.json)
* [market/TAM_SAM_SOM.md](../market/TAM_SAM_SOM.md) and [market/tam_sam_som.json](../market/tam_sam_som.json)
* [market/README.md](../market/README.md), [market/analysis.json](../market/analysis.json), [market/municipalities.csv](../market/municipalities.csv), [market/supply.geojson](../market/supply.geojson)
* [tools/market/som_inputs.json](../tools/market/som_inputs.json)
* [brand/MARKETING_REVIEW.md](../brand/MARKETING_REVIEW.md) and [brand/NAMING.md](../brand/NAMING.md)
* [site/public/service-area.json](../site/public/service-area.json), Overture release 2026-10-21.0, industrial buildings by derived use
* [vehicles/SELECTION.md](../vehicles/SELECTION.md)

Web sources checked while writing this plan, 22 November 2026:

* ICBC, Basic Insurance Tariff, U-Drive definition and rate classes: https://www.icbc.com/assets/en/6PyY5DEcoIT7z2ujjlwb3d/basic-tariff.pdf
* ICBC, commercial insurance, Fleetplan threshold: https://icbc.com/insurance/commercial
* CVSE, National Safety Code: https://www.cvse.ca/national_safety_code.htm
* City of Surrey, applying for a business licence: https://www.surrey.ca/business-economy/business-licensing
* Government of BC, PST small business guide, PVRT text (page returned HTTP 503 on fetch, text read from its search index): https://www2.gov.bc.ca/gov/content/taxes/sales-taxes/pst/publications/small-business-guide

Web sources checked 23 November 2026 (sections 4.2, 4.3, 10.4, 11.6 and R4 to R7):

* BC Bulletin PST 116, PVRT and rental PST: https://www2.gov.bc.ca/assets/gov/taxes/sales-taxes/publications/pst-116-motor-vehicle-dealers-leasing-companies.pdf
* BC Bulletin PST 308, passenger vehicle definition: https://www2.gov.bc.ca/assets/gov/taxes/sales-taxes/publications/pst-308-vehicles.pdf
* BC Motor Vehicle Act Regulations, Division 37 (NSC carriers): https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/26_58_12
* City of Surrey, Business License By-law 13680: https://www.surrey.ca/city-government/bylaws/13680
* City of Surrey, Zoning By-law 12000: https://www.surrey.ca/city-government/bylaws/12000
* ICBC, peer-to-peer vehicle rental: https://icbc.com/insurance/commercial/peer-to-peer-vehicle-rental
* Turo, Canadian host earnings plans: https://help.turo.com/en_us/earnings-plans-in-detail-canada-hosts-Hk8uLEgEq.md
* Turo, S-1/A amendment 12: https://www.sec.gov/Archives/edgar/data/1514587/000162828024047889/turoinc-sx1a12.htm
* Rate, cost and seasonality sources are linked in their tables in sections 4.2, 6, 10.4 and 11.6

Web sources cited through [MARKETING_REVIEW](../brand/MARKETING_REVIEW.md):

* Competition Bureau, Competition Act amendments, June 2022: https://www.canada.ca/en/competition-bureau/news/2022/06/important-amendments-to-the-competition-act-come-into-effect.html
* Competition Bureau, Discount Car Rental penalty, 2018: https://www.canada.ca/en/competition-bureau/news/2018/10/discount-car-rental-penalised-for-advertising-unattainable-prices.html
* ICBC rental vehicle partners: https://partners.icbc.com/material-damage/rental-vehicles
* ICBC rental cars and other transportation: https://icbc.com/claims/repair-replace/Rental-cars-and-other-transportation
