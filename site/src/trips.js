// Trip planner: road route between stops, checks along it, and what the trip costs at published prices.
import { price } from "./pricing.js";
// Static layers come from public/trips/ (tools/market/trip_layers.py). Live layers are fetched from their
// publishers when switched on or when a route is checked: Surrey truck routes and road obstructions
// (Open Government License – City of Surrey) and DriveBC events (Open511, Open Government Licence – BC).
// Routing uses the FOSSGIS OSRM demo service under its policy: requests only on a button press, at most
// one per second, with OpenStreetMap attribution (the same choice as CONSULTING's Route & risk tool).
import "./landing.js";

const L = window.L;
const ROUTER = "https://routing.openstreetmap.de/routed-car/route/v1/driving/";
const ROUTER_TIMEOUT_MS = 20000;
const SURREY = "https://gisservices.surrey.ca/arcgis/rest/services/";
const OPEN511 = "https://api.open511.gov.bc.ca/events";
const BOX = "-123.35,48.95,-122.2,49.45"; // as tools/market/trip_layers.py BOX
const MAX_STOPS = 6;
const STEP = 50; // metres between route samples for the truck route check
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const money = (v) => `C$${v.toFixed(2)}`;

// ---- geometry: metres on a local plane, good to well under 1% across Metro Vancouver ----
const KX = Math.cos((49.2 * Math.PI) / 180) * 111320, KY = 110574;
const xy = ([lon, lat]) => [lon * KX, lat * KY];
function segDist([px, py], [ax, ay], [bx, by]) {
  const dx = bx - ax, dy = by - ay, len = dx * dx + dy * dy;
  const t = len ? Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / len)) : 0;
  return Math.hypot(px - ax - t * dx, py - ay - t * dy);
}
function lineDist(p, line) {
  let best = Infinity;
  for (let i = 1; i < line.length; i++) best = Math.min(best, segDist(p, line[i - 1], line[i]));
  return best;
}
// Every line of a GeoJSON geometry in local metres. A point becomes a zero-length segment.
function lines(g) {
  if (!g) return [];
  if (g.type === "Point") return [[xy(g.coordinates), xy(g.coordinates)]];
  if (g.type === "LineString" || g.type === "MultiPoint") return [g.coordinates.map(xy)];
  if (g.type === "MultiLineString" || g.type === "Polygon") return g.coordinates.map((l) => l.map(xy));
  if (g.type === "MultiPolygon") return g.coordinates.flat().map((l) => l.map(xy));
  if (g.type === "GeometryCollection") return g.geometries.flatMap(lines);
  return [];
}
const boxOf = (pts) => pts.reduce((b, [x, y]) => [Math.min(b[0], x), Math.min(b[1], y), Math.max(b[2], x), Math.max(b[3], y)], [Infinity, Infinity, -Infinity, -Infinity]);
const overlaps = (a, b, pad) => a[0] - pad <= b[2] && b[0] - pad <= a[2] && a[1] - pad <= b[3] && b[1] - pad <= a[3];
// Projected lines and a bounding box for every feature, built once per dataset.
const indexed = new WeakMap();
function index(fc) {
  if (!indexed.has(fc)) indexed.set(fc, fc.features.map((f) => { const ls = lines(f.geometry); return { f, ls, box: boxOf(ls.flat()) }; }));
  return indexed.get(fc);
}
// Points every `step` metres along the route, in metres.
function samples(route, step) {
  const out = [route[0]];
  for (let i = 1; i < route.length; i++) {
    const [ax, ay] = route[i - 1], [bx, by] = route[i], d = Math.hypot(bx - ax, by - ay);
    for (let s = step; s < d; s += step) out.push([ax + ((bx - ax) * s) / d, ay + ((by - ay) * s) / d]);
    out.push(route[i]);
  }
  return out;
}
// Features within `metres` of the route. Both directions are tested, because the closest point between
// two lines can sit mid-segment on either one. The box test skips the features nowhere near the route.
function nearRoute(fc, route, metres) {
  const rbox = boxOf(route);
  return index(fc).filter(({ ls, box }) => overlaps(box, rbox, metres)
    && ls.some((l) => l.some((p) => lineDist(p, route) <= metres) || (l.length > 1 && route.some((p) => lineDist(p, l) <= metres))))
    .map(({ f }) => f);
}

// ---- data loading ----
const cache = new Map();
function load(url, transform = (x) => x) {
  if (!cache.has(url)) {
    const p = fetch(url).then((r) => { if (!r.ok) throw new Error(`${r.status}`); return r.json(); }).then(transform);
    p.catch(() => cache.delete(url));
    cache.set(url, p);
  }
  return cache.get(url);
}
const surrey = (layer, fields) => `${SURREY}${layer}/query?${new URLSearchParams({ where: "1=1", outFields: fields, outSR: "4326", f: "geojson" })}`;
// A publisher that stops at its record limit flags it. The checks then say the list may be incomplete.
const surreyFC = (d) => ({ ...d, partial: Boolean(d.exceededTransferLimit || d.properties?.exceededTransferLimit) });
let closures = null;
const DATA = {
  truck: () => load(surrey("Public/Transportation/MapServer/18", "ROAD_NAME,TRUCK_ROUTE,SPEED,MAJOR_ROAD_NETWORK"), surreyFC),
  // Surrey also publishes permit holders' and managers' names, which the licence excludes, so they are not requested.
  // Active closures and detours, merged once. The index of a merged collection needs one stable object.
  closures: () => (closures ||= Promise.all([0, 1].map((n) => load(surrey(`RoadObstructions/MapServer/${n}`, "ROAD_NAME,OBSTRUCTIONTYPE,WORKTYPE,PERMITTEDHOURS,TORPDATES"), surreyFC)))
    .then((layers) => ({ type: "FeatureCollection", partial: layers.some((c) => c.partial), features: [["Closure", layers[0]], ["Detour", layers[1]]].flatMap(([kind, c]) => c.features.map((f) => ({ ...f, kind }))) }))
    .catch((e) => { closures = null; throw e; })),
  events: () => load(`${OPEN511}?${new URLSearchParams({ format: "json", status: "ACTIVE", limit: "500", bbox: BOX })}`,
    (d) => ({ type: "FeatureCollection", partial: Boolean(d.pagination?.next_url), features: d.events.filter((e) => e.geography).map((e) => ({ type: "Feature", geometry: e.geography, properties: { headline: e.headline, description: e.description, severity: e.severity, roads: (e.roads || []).map((r) => r.name).join(", ") } })) })),
};
for (const name of ["structures", "rentals", "competition", "stations", "ferries"]) DATA[name] = () => load(`trips/${name}.geojson`);
DATA.rates = () => load("trips/rates.json");

// ---- map ----
const map = L.map("map", { zoomControl: true }).setView([49.16, -122.84], 11);
// OpenStreetMap's own tiles, darkened in CSS (.trips__map .leaflet-tile-pane), as CONSULTING's "osm-dark" basemap does.
// Light, interactive use with attribution fits the OSM tile usage policy. CARTO's dark style now needs a key.
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

const popup = (title, rows) => `<strong>${esc(title)}</strong>${rows.filter(([, v]) => v).map(([k, v]) => `<br>${esc(k)}: ${esc(v)}`).join("")}`;
const TRUCK_COLOUR = { "Truck Routes": "#ff8a5c", "Dangerous Goods Routes": "#d9a441", "Truck Routes with Restrictions": "#e0453a" };
// Each layer: which DATA set, how to draw it (style for lines and areas, dot for points) and its popup.
const LAYERS = [
  { id: "competition", label: "Competition index (orange = crowded, bone = underserved)", on: true,
    style: (p) => ({ color: "#2a2a2e", weight: 1, fillColor: p.colour || "#2a2a2e", fillOpacity: p.colour ? 0.35 : 0.1 }),
    title: (p) => p.name, rows: (p) => [["Index", p.index == null ? "not scored" : p.index.toFixed(2)], ["Car outlets", `${p.car}`], ["Gaps", p.gaps]] },
  { id: "rentals", label: "Rental outlets by type", on: true, dot: (p) => ({ radius: 5, fill: p.colour }),
    title: (p) => p.name, rows: (p) => [["Type", p.label], ["Brand", p.brand], ["Address", p.address]] },
  { id: "truck", label: "Surrey truck routes (live)", live: true, style: (p) => ({ color: TRUCK_COLOUR[p.TRUCK_ROUTE] || "#ff8a5c", weight: 3, opacity: 0.85 }),
    title: (p) => p.ROAD_NAME, rows: (p) => [["Class", p.TRUCK_ROUTE], ["Speed", p.SPEED]] },
  { id: "closures", label: "Surrey road closures and detours (live)", live: true, style: () => ({ color: "#b3261e", weight: 5, opacity: 0.9, dashArray: "6 4" }),
    title: (p) => p.ROAD_NAME, rows: (p) => [["Type", p.OBSTRUCTIONTYPE], ["Work", p.WORKTYPE], ["Hours", p.PERMITTEDHOURS], ["Dates", p.TORPDATES]] },
  { id: "events", label: "DriveBC road events (live)", live: true, on: true, style: () => ({ color: "#ffd166", weight: 4 }), dot: () => ({ radius: 6, fill: "#ffd166" }),
    title: (p) => p.headline, rows: (p) => [["Roads", p.roads], ["Severity", p.severity], ["Details", p.description]] },
  { id: "structures", label: "Highway bridges and tunnels", style: (p) => ({ color: p.open ? "#8ab4f8" : "#e0453a", weight: 4 }),
    title: (p) => p.BMIS_STRUCTURE_NAME, rows: (p) => [["Type", p.BMIS_STRUCTURE_TYPE], ["Highway", p.HIGHWAY_NUMBER], ["Status", p.BMIS_STRUCT_STATUS_TYPE_DESC]] },
  { id: "stations", label: "SkyTrain stations", dot: () => ({ radius: 4, fill: "#6f8fd0" }),
    title: (p) => p.name, rows: (p) => [["Lines", p.lines], ["Rental outlets within 1 km", `${p.rent_1km}`]] },
];
const build = async (layer) => L.geoJSON(await DATA[layer.id](), {
  ...(layer.style && { style: (f) => layer.style(f.properties) }),
  ...(layer.dot && { pointToLayer: (f, ll) => { const d = layer.dot(f.properties); return L.circleMarker(ll, { radius: d.radius, weight: 1, color: "#111112", fillColor: d.fill, fillOpacity: 1 }); } }),
  onEachFeature: (f, l) => l.bindPopup(popup(layer.title(f.properties), layer.rows(f.properties))),
});
const built = new Map();
async function toggle(layer, on) {
  const status = $(`st-${layer.id}`);
  try {
    if (!built.has(layer.id)) { status.textContent = "loading…"; built.set(layer.id, await build(layer)); }
    const l = built.get(layer.id);
    if (on) l.addTo(map); else map.removeLayer(l);
    status.textContent = on && layer.live ? `${l.getLayers().length} now` : "";
  } catch {
    status.textContent = "unavailable";
    built.delete(layer.id);
  }
}
$("layers").innerHTML = LAYERS.map((l) => `<label class="trips__layer"><input type="checkbox" id="ly-${l.id}" ${l.on ? "checked" : ""} /> ${esc(l.label)} <span class="trips__hint" id="st-${l.id}"></span></label>`).join("");
for (const l of LAYERS) {
  $(`ly-${l.id}`).addEventListener("change", (e) => toggle(l, e.target.checked));
  if (l.on) toggle(l, true);
}

// ---- stops ----
const stops = [];
let routeLayer = null, lastRequest = 0;
const coordName = (ll) => `${ll.lat.toFixed(4)}, ${ll.lng.toFixed(4)}`;
function renderStops() {
  $("stops").innerHTML = stops.map((s, i) => `<li><span>${esc(s.name)}</span><button type="button" class="trips__x" data-i="${i}" aria-label="Remove ${esc(s.name)}">×</button></li>`).join("");
  stops.forEach((s, i) => s.marker.setTooltipContent(`${i + 1}`));
  $("route").disabled = stops.length < 2;
}
function addStop(latlng, name = coordName(latlng)) {
  if (stops.length >= MAX_STOPS) return;
  const marker = L.marker(latlng, { draggable: true, title: name }).addTo(map).bindTooltip("", { permanent: true, direction: "top", className: "trips__pin" });
  const stop = { latlng, name, marker };
  marker.on("dragend", () => { stop.latlng = marker.getLatLng(); stop.name = coordName(stop.latlng); renderStops(); });
  stops.push(stop);
  renderStops();
}
map.on("click", (e) => addStop(e.latlng));
$("stops").addEventListener("click", (e) => {
  const i = e.target.dataset?.i;
  if (i === undefined) return;
  map.removeLayer(stops[i].marker);
  stops.splice(i, 1);
  renderStops();
});
$("clear").addEventListener("click", () => {
  for (const s of stops) map.removeLayer(s.marker);
  stops.length = 0;
  if (routeLayer) map.removeLayer(routeLayer);
  $("result").innerHTML = "";
  renderStops();
});
Promise.all([DATA.ferries(), DATA.stations()]).then(([ferries, stations]) => {
  const opts = (group, feats, nameOf) => `<optgroup label="${group}">${feats.map((f) => `<option value="${f.geometry.coordinates[1]},${f.geometry.coordinates[0]}">${esc(nameOf(f))}</option>`).join("")}</optgroup>`;
  $("pick").insertAdjacentHTML("beforeend", opts("Ferry terminals", ferries.features, (f) => f.properties.TERMINAL_NAME)
    + opts("SkyTrain stations", [...stations.features].sort((a, b) => a.properties.name.localeCompare(b.properties.name)), (f) => f.properties.name));
});
$("pick").addEventListener("change", (e) => {
  if (!e.target.value) return;
  const [lat, lng] = e.target.value.split(",").map(Number);
  addStop(L.latLng(lat, lng), e.target.selectedOptions[0].textContent);
  e.target.value = "";
});

// ---- route and checks ----
async function planRoute() {
  const wait = lastRequest + 1000 - Date.now();
  if (wait > 0) await new Promise((r) => setTimeout(r, wait));
  lastRequest = Date.now();
  $("route").disabled = true;
  $("result").innerHTML = "<p>Routing…</p>";
  // The check layers are cached promises: start them now so they load while the router answers.
  for (const k of ["truck", "closures", "events", "structures"]) DATA[k]().catch(() => {});
  const coords = stops.map((s) => `${s.latlng.lng.toFixed(6)},${s.latlng.lat.toFixed(6)}`).join(";");
  try {
    const res = await fetch(`${ROUTER}${coords}?overview=full&geometries=geojson&steps=false`, { signal: AbortSignal.timeout(ROUTER_TIMEOUT_MS) });
    const data = await res.json();
    if (data.code !== "Ok") throw new Error(data.message || data.code);
    const r = data.routes[0];
    if (routeLayer) map.removeLayer(routeLayer);
    routeLayer = L.geoJSON(r.geometry, { style: { color: "#ff4b1f", weight: 6, opacity: 0.9 } }).addTo(map);
    map.fitBounds(routeLayer.getBounds(), { padding: [40, 40] });
    await showResult(r.geometry.coordinates.map(xy), r.distance / 1000, r.duration / 60);
  } catch (e) {
    $("result").innerHTML = `<p class="trips__warn">The routing service did not answer (${esc(e.message)}). Try again in a moment.</p>`;
  } finally {
    renderStops();
  }
}
$("route").addEventListener("click", planRoute);

async function check(label, data, run) {
  let body;
  try {
    const fc = await data();
    body = await run(fc) + (fc.partial ? ". The publisher returned a partial list, so this may be incomplete" : "");
  } catch { body = "could not be loaded just now"; }
  return `<li><strong>${esc(label)}:</strong> ${body}.</li>`;
}

async function showResult(route, km, minutes) {
  const rates = await DATA.rates();
  const job = rates.jobs[$("job").value], hours = Math.max(1, Number($("hours").value) || 1);
  const checks = await Promise.all([
    check("Surrey truck routes", DATA.truck, async (fc) => {
      const rbox = boxOf(route);
      const truck = index(fc).filter(({ box }) => overlaps(box, rbox, 20));
      let on = 0, dg = 0;
      const restricted = new Set();
      for (const p of samples(route, STEP)) {
        const hit = truck.find(({ ls, box }) => overlaps(box, [p[0], p[1], p[0], p[1]], 20) && ls.some((l) => lineDist(p, l) <= 20));
        if (!hit) continue;
        on++;
        if (hit.f.properties.TRUCK_ROUTE === "Truck Routes with Restrictions") restricted.add(hit.f.properties.ROAD_NAME);
        if (hit.f.properties.TRUCK_ROUTE === "Dangerous Goods Routes") dg++;
      }
      if (!on) return `the route does not use Surrey's designated truck network${job.heavy ? ". Check local truck restrictions before sending a truck" : ""}`;
      return `about ${((on * STEP) / 1000).toFixed(1)} km of the route runs on Surrey's truck network${dg ? `, ${((dg * STEP) / 1000).toFixed(1)} km of it dangerous goods routes` : ""}${restricted.size ? `. Restricted segments: ${esc([...restricted].join(", "))}. Surrey's Highway and Traffic Bylaw sets the restriction` : ""}`;
    }),
    check("Surrey closures and detours", DATA.closures, async (fc) => {
      const hits = nearRoute(fc, route, 50);
      return hits.length ? hits.map((f) => `${esc(f.kind)} on ${esc(f.properties.ROAD_NAME)} (${esc(f.properties.PERMITTEDHOURS || "hours not stated")})`).join(", ") : "none on the route right now";
    }),
    check("DriveBC events", DATA.events, async (fc) => {
      const hits = nearRoute(fc, route, 300);
      return hits.length ? hits.slice(0, 6).map((f) => `${esc(f.properties.headline)} on ${esc(f.properties.roads || "the route")}`).join(", ") + (hits.length > 6 ? `, and ${hits.length - 6} more` : "") : "none within 300 m of the route right now";
    }),
    check("Highway bridges and tunnels", DATA.structures, async (fc) => {
      const hits = nearRoute(fc, route, 15);
      const names = (fs) => esc([...new Set(fs.map((f) => f.properties.BMIS_STRUCTURE_NAME))].join(", "));
      const closed = hits.filter((f) => !f.properties.open);
      const tunnels = hits.filter((f) => /TUNNEL/i.test(f.properties.BMIS_STRUCTURE_TYPE || ""));
      return `about ${hits.length} on or beside the route${tunnels.length ? `, including ${names(tunnels)}` : ""}${closed.length ? `. Closed or under construction in the provincial record: ${names(closed)}` : ""}. Clearance heights are not in the provincial data`;
    }),
  ]);
  const rows = job.operators.map((id) => rates.operators[id]).map((o) => ({ o, v: price(o, hours, km, rates.pvrt_from_hours) })).sort((a, b) => a.v - b.v);
  $("result").innerHTML = `
    <h2>${km.toFixed(1)} km, about ${Math.round(minutes)} min driving</h2>
    <p class="trips__hint">Router time without live traffic. Hours on hire: ${hours}.</p>
    <h3>Along the route</h3><ul class="trips__checks">${checks.join("")}</ul>
    <h3>${esc(job.label)}: published prices for this trip</h3>
    <table class="trips__prices"><tbody>
      <tr><th scope="row">Ember Rent</th><td>${esc(rates.ember_rent)}</td></tr>
      ${rows.map(({ o, v }) => `<tr><th scope="row"><a href="${esc(o.source)}" rel="noopener">${esc(o.name)}</a></th><td><strong>${money(v)}</strong><br><span class="trips__hint">${esc(o.terms)}</span></td></tr>`).join("")}
    </tbody></table>
    <p class="trips__hint">Before GST and PST. Uses ${km.toFixed(1)} km and ${hours} hours. Evo and Modo cost a round trip from their own spots, and Evo rents cars only. Rates retrieved ${esc(rates.retrieved)}.</p>`;
}

DATA.rates().then((rates) => {
  $("job").innerHTML = Object.entries(rates.jobs).map(([k, j]) => `<option value="${k}">${esc(j.label)}</option>`).join("");
  $("job").value = "van";
});
