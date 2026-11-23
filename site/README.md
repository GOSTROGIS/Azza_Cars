# Website and dashboard

The public Ember Rent website: landing page, business plan, trip planner, project status, market map and the vehicle catalogue. It is a static site, so it can be hosted anywhere (no server code).

## Stack and why

- **Vite, plain HTML and small scripts.** Each page except the catalogue is HTML that search engines can read, with a few kilobytes of JavaScript.
- **React for the vehicle catalogue.** `explorer.html` is a searchable database of every brand and model in `catalog/`, with the audited logos from `logos/`. No 3D.
- **Photos only where a licensed one exists.** A model shows an open-licence photo from `tools/models/build.py` with its credit, otherwise the brand logo. Manufacturer and other open-licence images are added to the same slot.

## Layout

| Path | What it is |
|---|---|
| `index.html`, `src/landing.js` | Landing page |
| `trips.html`, `src/trips.js` | Trip planner: OSRM road route (FOSSGIS demo, one request a second, on a button press), live Surrey truck routes and closures and DriveBC events, snapshot layers from `tools/market/trip_layers.py`, prices from `market/trip_rates.json`, shared with the plan's trip-cost chart |
| `explorer.html`, `src/main.jsx`, `src/App.jsx`, `src/search.js`, `src/labels.js`, `src/app.css` | Vehicle catalogue: search, filters by country, segment, body, power and years, brand pages with logos, model detail with sources and photo credit |
| `plan.html`, `src/plan.js`, `status.html` | Business plan in two tabs (rendered from `plan/BUSINESS_PLAN.md` and `plan/RENTAL_PLAN.md`) and project status |
| `src/landing.css` | Styles for every page. Colours and type come from `design/` |
| `scripts/copy-data.mjs` | Copies the catalogue (`catalog/` as compact `public/data/catalog.json`), the logos, `market/map.html` and the trip planner layers (`market/trips/`) into `public/` |
| `public/models/` | Model photos and `models.json` (with `catalog_id`), written by `tools/models/build.py` |

## Run

```
cd site
npm install
npm run dev      # copies data, starts a dev server
npm run build    # copies data, writes dist/
```

## Accessibility

- The model search is a labelled search field and the type filters are real buttons with `aria-pressed` state. Focus rings are always visible.
- The model count is announced to screen readers. The model detail is a native `<dialog>`, closed with Escape or the close button.
- Layout works from 320 px phones to wide desktops.

## Ember Rent landing page

`index.html` is the Ember Rent landing page: plain HTML and CSS (`src/landing.js`, `src/landing.css`) so it loads fast and is easy for search engines to read.

The page follows the marketing plan in `brand/MARKETING_REVIEW.md`: vans and trucks first, Surrey first, all-in prices, business accounts, local business and FAQ structured data, and photo credits for the hero images.

Nothing on the page is invented. Every fact only the owner can supply is marked in the HTML with `OWNER INPUT` (rates, address, hours, phone, canonical URL, booking link). Promises that depend on how the business will operate are marked `OWNER CONFIRM`. Search the file for both before launch.
