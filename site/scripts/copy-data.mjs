// Copies generated data into site/public so the static build is self-contained.
//   catalog/models.json + catalog/brands.json -> public/data/catalog.json (compact keys)
//   logos/svg/<slug>.svg for audited logos     -> public/logos/<slug>.svg
//   vehicles/manifest.json + GLB files          -> public/vehicles/
//   market/map.html (self-contained Leaflet map) -> public/market/map.html
// Nothing here creates data. It only reshapes and copies files produced elsewhere.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..", "..");
const pub = path.resolve(here, "..", "public");
const read = (p) => JSON.parse(fs.readFileSync(path.join(root, p), "utf8"));

fs.mkdirSync(path.join(pub, "data"), { recursive: true });
fs.mkdirSync(path.join(pub, "logos"), { recursive: true });
fs.mkdirSync(path.join(pub, "vehicles"), { recursive: true });

const brands = read("catalog/brands.json");
const models = read("catalog/models.json");
const report = read("catalog/build_report.json");

for (const b of brands) {
  if (!b.logo) continue;
  fs.copyFileSync(path.join(root, b.logo), path.join(pub, "logos", `${b.slug}.svg`));
  b.logo = `logos/${b.slug}.svg`;
}

const compact = models.map((m) => ({
  i: m.id,
  b: m.brand,
  n: m.name,
  a: m.aliases,
  y: [m.year_min, m.year_max],
  yb: m.years_basis,
  t: m.bodies,
  c: m.classes,
  k: m.markets,
  s: m.status,
  src: m.sources,
  ...(m.inegi_company ? { co: m.inegi_company } : {}),
  ...(m.mx_units_by_year ? { mx: m.mx_units_by_year } : {}),
}));

const manifestPath = path.join(root, "vehicles", "manifest.json");
const vehicles = fs.existsSync(manifestPath) ? JSON.parse(fs.readFileSync(manifestPath, "utf8")) : [];
for (const v of vehicles) {
  fs.copyFileSync(path.join(root, v.glb), path.join(pub, "vehicles", path.basename(v.glb)));
  v.glb = `vehicles/${path.basename(v.glb)}`;
  for (const r of v.references || []) {
    if (!r.thumb) continue;
    fs.copyFileSync(path.join(root, r.thumb), path.join(pub, "vehicles", `${v.slug}-${path.basename(r.thumb)}`));
    r.thumb = `vehicles/${v.slug}-${path.basename(r.thumb)}`;
  }
}

const out = { built: report, brands, models: compact, vehicles };
fs.writeFileSync(path.join(pub, "data", "catalog.json"), JSON.stringify(out));
console.log(`catalog.json: ${brands.length} brands, ${compact.length} models, ${vehicles.length} 3D vehicles`);

// The market gap map embeds its own data, so it can be served as it is.
fs.mkdirSync(path.join(pub, "market"), { recursive: true });
fs.copyFileSync(path.join(root, "market", "map.html"), path.join(pub, "market", "map.html"));
