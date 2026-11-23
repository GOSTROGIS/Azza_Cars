// Copies generated data into site/public so the static build is self-contained.
//   market/map.html (self-contained Leaflet map) -> public/market/map.html
// The popular-models images and models.json are written straight into public/models by tools/models/build.py.
// Nothing here creates data. It only copies files produced elsewhere.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..", "..");
const pub = path.resolve(here, "..", "public");

// The market gap map embeds its own data, so it can be served as it is.
fs.mkdirSync(path.join(pub, "market"), { recursive: true });
fs.copyFileSync(path.join(root, "market", "map.html"), path.join(pub, "market", "map.html"));
