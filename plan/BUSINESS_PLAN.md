# Ember Rent business plan

Car, van and truck rental for Surrey, BC, south of the Fraser in Metro Vancouver. Draft 1, prepared 22 November 2026 for the owner to iterate.

**How to read this plan.** Every number links to the repository file it comes from, or to a web page checked while writing. Anything only the owner can decide or supply is marked **Owner input required**. Statements that rest on reasoning rather than a source are marked *(judgement)*. No financial result in this plan is a forecast. The financial section gives the structure and leaves the owner's numbers blank.

## 1. Executive summary

**The answer: launch Ember Rent as a single Surrey location renting cargo vans, pickups and light trucks to trade and logistics businesses, with a smaller car fleet for residents. Stay away from the airport and downtown. Expand to Langley Township, then the Tri-Cities, only once the Surrey unit economics are proven.**

Why this is the right first move:

1. **Surrey is the largest supply gap in Metro Vancouver.** It holds 21.6% of Metro population (568,322 people) but has 0.35 car rental locations per 10,000 residents, against a Metro average of 0.61 ([GAP_ANALYSIS](../market/GAP_ANALYSIS.md)).
2. **The truck gap is commercial.** 127 of 149 counted truck rental locations in Metro Vancouver are U-Haul, a consumer moving brand. Penske has 6 and Ryder 1. Surrey alone has 1,418 trucking businesses with employees, 57.9% of the Metro total, and 4,648 construction businesses ([GAP_ANALYSIS](../market/GAP_ANALYSIS.md), [municipalities.csv](../market/municipalities.csv)). The service area holds 3,295 mapped industrial buildings, 1,616 of them in Surrey ([service-area.json](../site/public/service-area.json)).
3. **The market is large relative to any plausible fleet.** Metro Vancouver's share of BC automotive rental and leasing revenue is C$647 to 698 million a year. A new operator's year 1 to 3 revenue on the owner's placeholder inputs is C$0.2 to 3.2 million, under 0.5% of that ([TAM_SAM_SOM](../market/TAM_SAM_SOM.md)). Growth is limited by capital and utilisation, not by demand.
4. **The airport is the wrong fight.** 18 counted car rental locations sit within 3 km of YVR, almost all majors ([GAP_ANALYSIS](../market/GAP_ANALYSIS.md)).

What could sink it: under-utilised vehicles financed with debt, rates set without a local survey, insurance cost and availability for a small U-Drive fleet, and the closed ICBC replacement-rental channel (ICBC's preferred suppliers are Budget and Enterprise from 1 September 2026, per [MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)). Section 6 states these plainly.

What the owner must decide before anything else: fleet size and mix, capital and financing, site, insurance carrier and legal entity. None of these are in the data, and the plan cannot be completed without them.

## 2. Business strategy

### 2.1 Positioning

Ember Rent is a local, design-led rental brand for jobs that car share and the airport majors serve badly: a van for a day's work, a pickup for a half-day haul, a weekly car while your own is in the shop. Its promise is a clear all-in price and a fast handover *(judgement, drawn from the positioning table in [MARKETING_REVIEW](../brand/MARKETING_REVIEW.md))*.

The marketing review found that the majors segment by price tier and by airport versus neighbourhood, car share by trip length and U-Haul by moving job, and that nobody positions on a fast, transparent handover for mixed cars, vans and trucks in the neighbourhoods. That gap is itself a judgement in the source, not a measurement ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)).

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

Product details (rate cards, deposit, mileage policy, age rules, delivery) are **Owner input required**.

### 2.4 Phased launch

| Phase | Where | What | Gate to the next phase *(judgement)* |
|---|---|---|---|
| 1 | Surrey, near industrial and trucking employment. Exact site **Owner input required** | Vans, pickups, light trucks and a smaller car fleet | Fleet utilisation and revenue per day at or above the owner's break-even (section 11) for a sustained period the owner sets |
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
| SOM, years 1 to 3 | C$0.2 to 3.2 million | Bottom-up: fleet × 365 × utilisation × average daily rate, on owner placeholder inputs |

Operating profit margin in 2024 was 10.7% in BC and 13.0% in Canada, down from 16.8% and 17.6% in 2023. Businesses bought 57.3% of national sales, which supports a B2B-led plan ([TAM_SAM_SOM](../market/TAM_SAM_SOM.md)).

**SOM scenarios, reproduced exactly from [TAM_SAM_SOM](../market/TAM_SAM_SOM.md).** Inputs are in [som_inputs.json](../tools/market/som_inputs.json). Every fleet figure, every daily rate and the low and base utilisation are owner placeholders, not facts. The high-case 81% utilisation is Hertz's company-wide full-year 2025 figure.

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
| Turo (peer to peer) | not counted | not counted | not counted | Marketplace with ICBC blanket insurance for BC hosts. Median Canadian host earning C$657 a month, January to October 2025 | Competitor on price and a possible channel for spare cars |

Positioning and carshare figures are from [MARKETING_REVIEW](../brand/MARKETING_REVIEW.md) and [GAP_ANALYSIS](../market/GAP_ANALYSIS.md). Zipcar and Car2Go records may be stale. Turo listing counts were not sourced. The majors' local rates are unknown, and a rate survey is the first open item in section 13.

## 5. Why it wins

1. **It enters where supply is thinnest and business demand is densest.** Surrey has 6.0 truck rental locations per 1,000 trucking, warehousing and construction businesses against 9.0 Metro wide ([GAP_ANALYSIS](../market/GAP_ANALYSIS.md)).
2. **It sells to businesses, which buy most of the market.** 57.3% of national NAICS 5321 sales go to businesses ([TAM_SAM_SOM](../market/TAM_SAM_SOM.md)). Trade accounts repeat, which lowers acquisition cost *(judgement)*.
3. **Local search cannot be bought.** Google ranks local results on relevance, distance and prominence, and review count and score feed prominence ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)). A well-run single location with steady reviews can outrank a distant major for "cargo van rental surrey" *(judgement)*.
4. **Compliance becomes the brand promise.** All-in pricing is mandatory under the Competition Act, so a transparent price costs nothing extra and contrasts with past enforcement against car rental companies ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)).
5. **Marketplaces can fill idle days from day one.** Rentalcars.com Marketplace, Discover Cars and Expedia accept smaller suppliers ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)).
6. **The fleet scales one vehicle at a time.** Revenue per vehicle is linear in utilisation and rate, so the owner can add capacity only when demand is shown *(judgement)*.

## 6. Why it fails

Stated honestly, in rough order of how likely each is to end the business *(judgement)*.

1. **Low utilisation on financed vehicles.** Revenue per vehicle at C$75 a day falls from C$19,162 at 70% utilisation to C$13,688 at 50% ([TAM_SAM_SOM](../market/TAM_SAM_SOM.md)). Financing, insurance and depreciation do not fall with it. The 81% benchmark is a US-dominated major and a new independent should not assume it.
2. **Rates set blind.** No Vancouver rate benchmark was found ([TAM_SAM_SOM](../market/TAM_SAM_SOM.md), [MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)). Pricing too low loses money on every day rented, too high leaves vehicles idle.
3. **Insurance cost or availability.** A U-Drive fleet is rated separately by ICBC (section 7) and optional coverage must be placed with a carrier. The cost is unknown until quoted, and it could break the unit economics for a small fleet.
4. **Thin margins industry wide.** BC operating margin fell from 16.8% in 2023 to 10.7% in 2024 ([TAM_SAM_SOM](../market/TAM_SAM_SOM.md)).
5. **Damage, theft and bad debt.** Vans and trucks used for trade work take more wear, and trade accounts on monthly invoice create receivables risk *(judgement)*.
6. **The majors respond.** Enterprise, Hertz and Alamo already have Surrey locations, and U-Haul has 34 ([supply.geojson](../market/supply.geojson)). They can discount locally.
7. **The ICBC channel stays closed.** Only preferred suppliers bill ICBC directly, and ICBC does not authorise EV loss-of-use rentals ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)). Replacement-rental revenue may be small.
8. **The name has to be changed.** The trademark search for Ember Rent is pending, and a UK transport company called Ember operates intercity buses ([NAMING](../brand/NAMING.md)). A forced rebrand after launch would waste the review history tied to the Google profile name *(judgement)*.
9. **Wrong site.** Zoning, visibility and parking capacity are not covered by any data in this repository ([GAP_ANALYSIS](../market/GAP_ANALYSIS.md)).
10. **Seasonality.** Not measured in any source. Moving and construction demand may peak in summer *(judgement)*.

## 7. Risk matrix

Likelihood and impact ratings are **(judgement)**. Owners are roles, because staffing is not yet decided.

| # | Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|---|
| R1 | Utilisation below break-even | High | High | Start with a small fleet, lease or finance on short terms, list cars on one marketplace for fill, add vehicles only when utilisation holds | Owner |
| R2 | Rates set without a benchmark | High | Med | Rate survey of Enterprise, Budget, U-Haul, Penske and two independents for identical dates before launch | Owner |
| R3 | **Drip pricing.** Under Competition Act amendments in force since June 2022, mandatory fees must be in the advertised price and only government-imposed charges such as sales tax may be added. Car rental companies have paid a total of C$5.95 million in penalties over drip pricing ([Competition Bureau, 2022](https://www.canada.ca/en/competition-bureau/news/2022/06/important-amendments-to-the-competition-act-come-into-effect.html), [Competition Bureau, 2018](https://www.canada.ca/en/competition-bureau/news/2018/10/discount-car-rental-penalised-for-advertising-unattainable-prices.html), via [MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)) | Low if designed in | High | Every advertised and quoted price includes all mandatory fees. Legal review of the booking flow, ads and marketplace listings | Owner with lawyer |
| R4 | **BC Passenger Vehicle Rental Tax.** C$1.50 per day or portion of a day on passenger vehicles rented for more than 8 consecutive hours and 28 consecutive days or less, collected on top of PST and remitted on the PST return, with GST charged on it ([BC PST small business guide](https://www2.gov.bc.ca/gov/content/taxes/sales-taxes/pst/publications/small-business-guide)). The page returned HTTP 503 when fetched on 22 November 2026, so this rests on its indexed text and on [MARKETING_REVIEW](../brand/MARKETING_REVIEW.md) | Med | Med | Register for PST before launch. Confirm PVRT scope (which vehicle classes count as passenger vehicles, the 8-hour and 28-day rules) with the Ministry of Finance. Build it into the booking system as a separate government charge | Owner with accountant |
| R5 | **ICBC rental-vehicle insurance and licensing.** ICBC's Basic Insurance Tariff rates "U-Drive" vehicles, defined as "a vehicle available for hire or rental, without driver, by the hour or otherwise, for a period of less than one month", in their own rate classes (including 008, 018, 058, 160, 161 and 170), split by vehicle type and gross vehicle weight ([ICBC Basic Insurance Tariff](https://www.icbc.com/assets/en/6PyY5DEcoIT7z2ujjlwb3d/basic-tariff.pdf)). Fleetplan "is required for customers with more than 20 eligible vehicles", and non-fleet commercial coverage applies below that ([ICBC commercial insurance](https://icbc.com/insurance/commercial)) | Med | High | Quote U-Drive Basic and optional coverage through an Autoplan broker before ordering vehicles. Plan for the switch to Fleetplan above 20 vehicles. Rentals of a month or more fall outside the U-Drive definition, so price and insure long-term rentals separately | Owner with broker |
| R6 | **Commercial vehicle safety.** Commercial vehicles licensed above 5,000 kg gross vehicle weight need a National Safety Code certificate in BC ([CVSE](https://www.cvse.ca/national_safety_code.htm)). How the rule applies to a rental company versus its renter was not found in any source | Med | Med | Keep the launch truck fleet at or below 5,000 kg GVW until a CVSE or legal opinion is in hand | Owner |
| R7 | Surrey zoning and business licence. Surrey advises a Zoning Inquiry Form before signing any lease, and all open permits must be finalised before a licence is issued ([City of Surrey](https://www.surrey.ca/business-economy/business-licensing)) | Med | High | Zoning inquiry on every shortlisted site before a lease is signed | Owner |
| R8 | Insurance cost too high for a small fleet | Med | High | Get two or more quotes for optional and garage coverage. Model the premium per vehicle in section 11 before committing | Owner with broker |
| R9 | Trademark conflict over "Ember" | Med | High | CIPO and USPTO searches by a trademark agent in Nice classes 12, 35 and 39 before signage and the Google profile go live ([NAMING](../brand/NAMING.md)) | Owner with agent |
| R10 | Damage, theft, unpaid invoices | Med | Med | Deposits, driver checks, telematics, credit limits and terms for accounts | Operations lead |
| R11 | Majors cut prices locally | Med | Med | Compete on vans, trade accounts and service rather than car price | Owner |
| R12 | Marketplace dependence | Low | Med | Cap the share of fleet days sold through marketplaces | Owner |
| R13 | Privacy of driver licence and payment data | Med | Med | Not verified in this plan. Obtain legal advice on BC private-sector privacy law and payment-card rules before collecting customer data | Owner with lawyer |

## 8. Prerequisites and launch checklist

Status: **done** means evidence is in the repository, **open** means work to do, **owner input** means a decision only the owner can make.

| Area | Item | Status | Note |
|---|---|---|---|
| Market | Gap analysis and market sizing | done | [GAP_ANALYSIS](../market/GAP_ANALYSIS.md), [TAM_SAM_SOM](../market/TAM_SAM_SOM.md) |
| Market | Competitor rate survey | open | No rate data exists |
| Market | 10 to 20 customer interviews with trades and logistics firms | open | Tests segments 1 and 4 |
| Legal | Legal entity (sole proprietorship, partnership, corporation) | owner input | |
| Legal | BC Registry name approval and registration as "Ember Rent" | open | Name must match signage and Google profile ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)) |
| Legal | Rental agreement, damage policy, deposit terms, privacy policy | open | Lawyer to draft |
| Legal | All-in pricing review of site, ads and listings | open | R3 |
| Tax | GST and PST registration, PVRT setup | open | R4 |
| Licensing | Surrey zoning inquiry and business licence | open | R7 |
| Licensing | ICBC U-Drive registration and insurance for each vehicle | open | R5 |
| Licensing | National Safety Code certificate, if any vehicle over 5,000 kg GVW | open | R6 |
| Insurance | Carrier or broker for optional, garage and general liability coverage | owner input | |
| Financing | Capital available and financing structure (cash, lease, loan, fleet line) | owner input | |
| Fleet | Size and mix by class | owner input | Section 10 |
| Location | Site in Surrey near industrial employment | owner input | 1,616 mapped industrial buildings in Surrey ([service-area.json](../site/public/service-area.json)) |
| Systems | Booking, fleet and payments system | owner input | Section 10 |
| Brand | Name chosen: Ember Rent | done | Owner decision. [NAMING](../brand/NAMING.md) recommended Keyhand, with Ember second |
| Brand | Trademark search (CIPO, USPTO) | open | Pending ([NAMING](../brand/NAMING.md)) |
| Brand | emberrent.com and emberrent.ca registered | open | Reported available by GoDaddy on 22 November 2026, which is not a reservation ([NAMING](../brand/NAMING.md)) |
| Brand | X handle @emberrent claimed | open | Free on 22 November 2026 ([NAMING](../brand/NAMING.md)) |
| Brand | Logo and mark | done | [brand/logo](../brand/logo/README.md) |
| Digital | Website with all-in prices, city and vehicle pages | open | Landing page exists in `site/`. Prices and inventory pending |
| Digital | Google Business Profile verified at the real address | open | Needs the site and signage first |
| Digital | Booking conversion tracking with value | open | |
| Sales | List of 30 trade, production and property-management prospects | open | [MARKETING_REVIEW](../brand/MARKETING_REVIEW.md) |
| Staffing | Roles, hours, hiring | owner input | Section 10 |

## 9. Go-to-market plan

Taken from the prioritised plan in [MARKETING_REVIEW](../brand/MARKETING_REVIEW.md), narrowed to phase 1 in Surrey. Priorities in that source are ranked by expected impact for cost, a judgement.

| # | When | Action | Metric |
|---|---|---|---|
| 1 | Weeks −8 to 0 | Clear and register the name, domains and handles. Register the trade name exactly as it will appear on signage | Name cleared, domains held |
| 2 | Weeks −8 to 0 | Verify one Google Business Profile at the Surrey site, most specific primary category, vehicle types as services, real photos. Keywords cannot go in the profile name ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)) | Profile verified |
| 3 | Weeks −8 to 0 | Site pages for Surrey and each vehicle type (cargo van, pickup, moving truck, car), all-in prices, booking tracked with value | Booking conversion tracked |
| 4 | Months 0 to 3 | Search ads on van and truck terms around Surrey, location assets with call buttons, manual or maximise-conversions bidding first | Cost per booking, revenue per day |
| 5 | Months 0 to 3 | Text a review link at every return. Steady weekly flow, never paid reviews | Reviews per week, rating |
| 6 | Months 0 to 6 | Field sales to 30 trade, production and property-management accounts, and body shops for non-ICBC repairs, with monthly invoicing | Active accounts, share of revenue |
| 7 | Months 3 to 9 | List cars, not trucks, on one marketplace for weekday and shoulder-season fill. Consider Turo for spare units | Utilisation, marketplace share of days |
| 8 | Months 3 to 9 | Referral credit for customers and accounts | Referred bookings |
| 9 | Phase 2 | Repeat steps 2 to 6 for Langley Township | Same |

Search volumes and cost per click were not available, so no ad budget is set here. Run Google Ads Keyword Planner once the account exists ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)). Marketing budget is **Owner input required**.

## 10. Operations plan outline

### 10.1 Fleet mix

| Class | Purpose | Units at launch | Notes |
|---|---|---|---|
| Cargo vans | Trade, moving, hourly jobs | **Owner input required** | Lead class *(judgement, from segment 1)* |
| Pickups | Hauling, trade | **Owner input required** | Autocomplete shows distinct pickup demand ([NAMING](../brand/NAMING.md)) |
| Light trucks, 5,000 kg GVW or less | Moving, logistics | **Owner input required** | Weight cap avoids NSC uncertainty (R6) |
| Cars, good, better, best classes | Residents, repair-period renters | **Owner input required** | ICBC loss-of-use rentals are limited to similar-size vehicles and exclude EVs ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)) |

Total fleet, makes and models, buy versus lease, and the year 1 to 3 growth path are **Owner input required**. The SOM placeholders range from 15 to 40 vehicles in year 1 ([som_inputs.json](../tools/market/som_inputs.json)). The vehicles modelled in [SELECTION.md](../vehicles/SELECTION.md) were chosen by US and Mexico sales rank for the website's 3D catalogue and are not a BC fleet recommendation.

### 10.2 Location requirements

| Requirement | Specification |
|---|---|
| Area | Surrey, near industrial and trucking employment. Exact site **Owner input required** |
| Zoning | Confirmed through Surrey's Zoning Inquiry Form before a lease ([City of Surrey](https://www.surrey.ca/business-economy/business-licensing)) |
| Parking | Space for the full fleet plus customer vehicles. Size **Owner input required** |
| Access | Clearance and turning room for trucks *(judgement)* |
| Visibility | Signage matching the registered name ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)) |
| Handover | Staffed counter or key boxes. Keycafe, a Vancouver firm, sells key systems to rental companies ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)) |
| Address, lease term and rent | **Owner input required** |

### 10.3 Staffing

Roles needed *(judgement)*: counter and handover, cleaning and turnaround, maintenance coordination, B2B sales, bookkeeping. Headcount, hours, wages, and which roles the owner covers personally are **Owner input required**.

### 10.4 Booking system

Requirements: online booking with all-in prices, PVRT and taxes as separate government charges, deposits and card pre-authorisation, driver licence capture, account billing for trade customers, utilisation and revenue-per-day reporting by class, and a marketplace connection later. Vendor choice is **Owner input required**. No vendor was evaluated for this plan.

### 10.5 Maintenance

Schedule by manufacturer interval, a check and clean at every return, damage photos at handover and return, and a target turnaround time per class. The service provider (in-house or a Surrey shop) and tyre and repair budgets are **Owner input required**. Commercial vehicles above 5,000 kg GVW bring CVSE inspection duties (R6).

## 11. Financial plan skeleton

No owner cost data exists, so this section gives formulas and leaves inputs blank. Cited inputs are marked with their source. Everything else is **Owner input required**.

### 11.1 Inputs

| Symbol | Input | Value | Source |
|---|---|---|---|
| N | Fleet size | ___ | Owner input required |
| U | Time utilisation (rented days ÷ available days) | ___ | Owner input required. Benchmark only: 81%, Hertz company-wide 2025 ([TAM_SAM_SOM](../market/TAM_SAM_SOM.md)) |
| R | Average daily rate, all-in, excluding taxes and PVRT | ___ | Owner input required. No local rate found |
| v | Variable cost per rented day (cleaning, card fees, wear, fuel loss, marketplace commission) | ___ | Owner input required |
| H | Annual holding cost per vehicle (depreciation or lease, interest, ICBC and optional insurance, registration, scheduled maintenance) | ___ | Owner input required |
| F | Annual fixed cost (rent, wages, software, marketing, professional fees) | ___ | Owner input required |
| t | PVRT per passenger-vehicle rental day | C$1.50 | Pass-through, not revenue (R4) |

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

Build one copy of this grid per vehicle class once the owner has class-level rates and costs, because vans, pickups and cars will not share R, v or H *(judgement)*.

### 11.5 Capital requirement

Start-up capital = vehicle down payments or purchase + site fit-out and deposit + insurance deposits + systems setup + pre-launch marketing + working capital for the months to break-even. Every term is **Owner input required**.

## 12. Milestones and KPIs

| Milestone | Target date | Exit criterion |
|---|---|---|
| Name cleared and registered | Owner input required | Agent's clearance, domains held, BC Registry name |
| Rate survey and customer interviews done | Owner input required | Rates and segment priorities set |
| Site signed | Owner input required | Zoning confirmed, licence applied |
| Insurance bound and fleet registered | Owner input required | ICBC U-Drive cover in force |
| Launch | Owner input required | Profile verified, booking live |
| Phase 2 decision | Owner input required | Phase 1 KPIs at target |

| KPI | Definition | Target |
|---|---|---|
| Utilisation by class | Rented days ÷ available days, weekly. The measure Hertz reports ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md)) | Owner input required, at or above U* |
| Revenue per day by class | Rental revenue ÷ rented days, weekly | At or above R* |
| Contribution per vehicle | Section 11.2 | Positive by class |
| Active trade accounts | Accounts with a rental in the last 90 days | Owner input required |
| B2B share of revenue | Account revenue ÷ total | Owner input required |
| Reviews per week and rating | Google profile | Owner input required |
| Cost per booking | Ad spend ÷ ad-attributed bookings | Owner input required |
| Damage and bad-debt cost | As % of revenue | Owner input required |

## 13. Open questions and next iteration

1. What do Enterprise, Budget, U-Haul, Penske and Discount charge in Surrey for the same dates? This sets R.
2. What will ICBC U-Drive Basic and optional coverage cost per class for a fleet under 20? This sets most of H.
3. How do the PVRT 8-hour and 28-day rules and the "passenger vehicle" definition apply to vans and pickups?
4. Does the rental company or the renter need the NSC certificate for a rented truck over 5,000 kg?
5. Will trades actually rent on account? Interview 10 to 20 Surrey firms.
6. Does "Ember Rent" clear CIPO and USPTO in classes 12, 35 and 39?
7. What capital is available, and on what financing terms?
8. Which sites in Surrey pass the zoning inquiry, and what do they cost?
9. How strong is seasonality? No source measures it.
10. How does a non-preferred supplier get paid on ICBC claims, and does ICBC run a supplier selection process ([MARKETING_REVIEW](../brand/MARKETING_REVIEW.md))?

Next iteration: once the owner supplies N, R, v, H and F, fill section 11, rerun `tools/market/tam_sam_som.py` with real inputs in [som_inputs.json](../tools/market/som_inputs.json), and replace the SOM placeholders in section 3.

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

Web sources cited through [MARKETING_REVIEW](../brand/MARKETING_REVIEW.md):

* Competition Bureau, Competition Act amendments, June 2022: https://www.canada.ca/en/competition-bureau/news/2022/06/important-amendments-to-the-competition-act-come-into-effect.html
* Competition Bureau, Discount Car Rental penalty, 2018: https://www.canada.ca/en/competition-bureau/news/2018/10/discount-car-rental-penalised-for-advertising-unattainable-prices.html
* ICBC rental vehicle partners: https://partners.icbc.com/material-damage/rental-vehicles
* ICBC rental cars and other transportation: https://icbc.com/claims/repair-replace/Rental-cars-and-other-transportation
