# Website and dashboard

The public Azza Cars website, which is also the internal dashboard: brand selector, model search,
filters and a 3D viewer. It is a static site, so it can be hosted anywhere (no server code).

## Stack and why

- **Vite + React.** Fast static builds and a small first load (about 55 kB gzipped of JavaScript before the 3D viewer).
- **three.js through react-three-fiber and drei.** three.js has the most complete glTF/GLB support on the web.
  react-three-fiber keeps the viewer declarative inside React. The viewer is lazy-loaded, so the page
  does not download three.js until a 3D vehicle is on screen.
- **No search library.** `src/search.js` is a small fuzzy matcher tuned for vehicle names: it ignores
  punctuation and spacing ("crv" finds CR-V, "f150" finds F-150), tolerates one or two typos ("camery"),
  combines brand and model words ("toyota rav") and treats a four-digit year as a filter ("civic 1998").

## Layout

| Path | What it is |
|---|---|
| `src/App.jsx` | Page: hero search, featured 3D, brand grid, filters, results, model detail |
| `src/search.js` | Fuzzy search index and scoring |
| `src/Viewer.jsx` | 3D viewer: studio lighting from local light panels (no HDR download), orbit, zoom, turntable, paint presets |
| `src/labels.js` | Display labels for body types, markets, sources |
| `src/app.css` | Page layout. Colours, depth and components come from `design/` |
| `scripts/copy-data.mjs` | Copies `catalog/`, audited `logos/svg/` files and `vehicles/` output into `public/` |

`public/data`, `public/logos` and `public/vehicles` are generated at build time and are not committed.

## Run

```
cd site
npm install
npm run dev      # copies data, starts a dev server
npm run build    # copies data, writes dist/
```

## Accessibility

- The search is a WAI-ARIA combobox: `/` focuses it, arrow keys move, Enter opens, Escape closes or clears.
- Every control is a real button with `aria-pressed` state. Focus rings are always visible.
- Result counts are announced to screen readers. The 3D canvas has a text label.
- Layout works from 320 px phones (single column, detail as a full-screen sheet) to wide desktops (three columns).
