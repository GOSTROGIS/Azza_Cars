// Copies generated data into site/public so the static build is self-contained.
//   catalog/models.json + catalog/brands.json -> public/data/catalog.json (compact keys)
//   logos/svg/<slug>.svg for audited logos, else catalog/logos/<slug>.svg|png (unaudited,
//   from the manufacturer's website)            -> public/logos/<slug>.<ext>
//   market/map.html (self-contained Leaflet map) -> public/market/map.html
//   market/trips/*.geojson, market/competition.geojson, market/stations.geojson, market/trip_rates.json -> public/trips/ (trip planner)
// Vehicle photos and their models.json are written straight into public/models by tools/models/build.py.
// Nothing here creates data. It only copies files produced elsewhere.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..", "..");
const pub = path.resolve(here, "..", "public");
const read = (p) => JSON.parse(fs.readFileSync(path.join(root, p), "utf8"));

// The vehicle catalogue (explorer.html): every brand and model with its sources, and its logos.
fs.mkdirSync(path.join(pub, "data"), { recursive: true });
fs.mkdirSync(path.join(pub, "logos"), { recursive: true });
const brands = read("catalog/brands.json");
const models = read("catalog/models.json");
const report = read("catalog/build_report.json");
for (const b of brands) {
  if (!b.logo) continue;
  const file = `${b.slug}${path.extname(b.logo)}`;
  fs.copyFileSync(path.join(root, b.logo), path.join(pub, "logos", file));
  b.logo = `logos/${file}`;
}
const compact = models.map((m) => ({
  i: m.id, b: m.brand, n: m.name, a: m.aliases, y: [m.year_min, m.year_max], yb: m.years_basis, t: m.bodies, c: m.classes,
  k: m.markets, s: m.status, src: m.sources,
  ...(m.inegi_company ? { co: m.inegi_company } : {}),
  ...(m.mx_units_by_year ? { mx: m.mx_units_by_year } : {}),
}));
fs.writeFileSync(path.join(pub, "data", "catalog.json"), JSON.stringify({ built: report, brands, models: compact }));
console.log(`catalog.json: ${brands.length} brands, ${compact.length} models`);

// The market gap map embeds its own data, so it can be served as it is.
fs.mkdirSync(path.join(pub, "market"), { recursive: true });
fs.copyFileSync(path.join(root, "market", "map.html"), path.join(pub, "market", "map.html"));

// Trip planner layers: snapshots from tools/market/trip_layers.py, the published rates, and the market layers it shares.
fs.mkdirSync(path.join(pub, "trips"), { recursive: true });
const TRIP_FILES = { "trips/rentals.geojson": "rentals.geojson", "trips/structures.geojson": "structures.geojson", "trips/ferries.geojson": "ferries.geojson",
  "competition.geojson": "competition.geojson", "stations.geojson": "stations.geojson", "trip_rates.json": "rates.json" };
for (const [from, to] of Object.entries(TRIP_FILES)) fs.copyFileSync(path.join(root, "market", from), path.join(pub, "trips", to));
