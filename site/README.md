# Website and dashboard

The public Ember Rent website: landing page, business plan, project status, market map and a popular-models page. It is a static site, so it can be hosted anywhere (no server code).

## Stack and why

- **Vite, plain HTML and small scripts.** No framework: each page is HTML that search engines can read, with a few kilobytes of JavaScript.
- **Real photos only.** The popular-models page shows open-licence Wikimedia Commons photos with the background removed by `tools/models/build.py`. White and silver photos carry a paint mask, so the page can multiply another colour into the real paint.

## Layout

| Path | What it is |
|---|---|
| `index.html`, `src/landing.js` | Landing page |
| `explorer.html`, `src/explorer.js` | Popular models: Canada's 2025 best sellers, search, type filter, detail with colour swatches and PNG download |
| `plan.html`, `status.html` | Business plan (rendered from `plan/BUSINESS_PLAN.md`) and project status |
| `src/landing.css` | Styles for every page. Colours and type come from `design/` |
| `scripts/copy-data.mjs` | Copies `market/map.html` into `public/` |
| `public/models/` | Cutouts and `models.json`, written by `tools/models/build.py` |

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
