// Popular models page: reads models/models.json (tools/models/build.py) and shows the cutouts.
// White and silver photos carry a paint mask, so a chosen colour is multiplied into the real paint.
import "./landing.js";

const TYPES = [["all", "All"], ["car", "Cars"], ["SUV", "SUVs"], ["pickup truck", "Pickups"], ["minivan", "Minivans"], ["cargo van", "Vans"]];
// Real factory colours are not claimed: these are neutral paint swatches, the first one is the photo as taken.
const PAINT = [["As photographed", null], ["Ember red", "#b3261e"], ["Deep blue", "#1f4b99"], ["Forest green", "#2f5d3a"], ["Graphite", "#3a3d42"], ["Sand", "#c9b48a"]];

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const fmt = (n) => (n == null ? null : n.toLocaleString("en-CA"));

function salesLine(s) {
  if (!s) return "No 2025 figure found";
  if (s.units == null) return esc(s.units_text);
  return s.units_alt ? `${fmt(s.units)} or ${fmt(s.units_alt)} (sources differ)` : fmt(s.units);
}

// build.py resolves every source to {name, url?, note?}.
const sourceLinks = (s) => (s?.sources || [])
  .map((x) => (x.url ? `<a href="${esc(x.url)}" rel="noopener">${esc(x.name)}</a>` : esc(x.name)) + (x.note ? ` (${esc(x.note)})` : "")).join(", ");

function card(m) {
  const s = m.sales;
  return `<li><button class="mcard" data-slug="${esc(m.slug)}">
    <img src="models/${esc(m.webp)}" alt="${esc(m.label)}, side view" loading="lazy" width="900" height="${Math.round(900 * m.size[1] / m.size[0])}" />
    <span class="mcard__name">${esc(m.label)}</span>
    <span class="mcard__meta">${s?.rank ? `#${s.rank} · ` : ""}${salesLine(s)} sold in 2025</span>
  </button></li>`;
}

function open(m) {
  $("detail-title").textContent = m.label;
  const ratio = (m.size[1] / m.size[0]) * 100;
  // The paint mask is attached on the first colour pick (see the paint handler), so it is only downloaded when used.
  $("stage").innerHTML = `<div class="model__car" style="padding-top:${ratio}%">
      <img src="models/${esc(m.detail)}" alt="${esc(m.label)}, side view, real photo with the background removed" />
      ${m.paint_mask ? `<div class="model__tint" data-mask="models/${esc(m.paint_mask)}"></div>` : ""}
    </div>`;
  $("paint").innerHTML = m.paint_mask
    ? PAINT.map(([name, hex], i) => `<button class="swatch" aria-pressed="${i === 0}" data-hex="${hex || ""}" title="${name}" style="--c:${hex || "#e9e6df"}"><span class="az-visually-hidden">${name}</span></button>`).join("")
    : `<p class="model__note">Photographed in ${esc(m.paint)}. Colour change works on white and silver photos only.</p>`;
  const s = m.sales;
  $("facts").innerHTML = `
    <div><dt>2025 sales in Canada</dt><dd>${salesLine(s)}${s?.rank ? `, rank ${s.rank}` : ""}. Sources: ${sourceLinks(s)}</dd></div>
    <div><dt>Type</dt><dd>${esc(m.vehicle_type)}</dd></div>
    <div><dt>Image</dt><dd><a href="models/${esc(m.png)}" download>PNG, ${m.size[0]} × ${m.size[1]} px</a></dd></div>`;
  $("credit").innerHTML = `Photo: <a href="${esc(m.commons_page)}" rel="noopener">${esc(m.author)}</a>, <a href="${esc(m.license_url)}" rel="noopener">${esc(m.license)}</a>, Wikimedia Commons. Background removed.`;
  $("detail").showModal();
}

async function main() {
  // models.json exists once tools/models/build.py has published the first photos.
  const res = await fetch("models/models.json");
  if (!res.ok) {
    $("count").textContent = "No models are published yet.";
    return;
  }
  const data = await res.json();
  const models = data.models;
  const present = new Set(models.map((m) => m.vehicle_type));
  let type = "all";
  $("types").innerHTML = TYPES.filter(([k]) => k === "all" || present.has(k))
    .map(([k, label]) => `<button class="az-chip" data-type="${k}" aria-pressed="${k === "all"}">${label}</button>`).join("");

  const render = () => {
    const q = $("q").value.trim().toLowerCase();
    const shown = models.filter((m) => (type === "all" || m.vehicle_type === type) && m.label.toLowerCase().includes(q));
    $("grid").innerHTML = shown.map(card).join("");
    $("count").textContent = `${shown.length} of ${models.length} models`;
  };
  $("q").addEventListener("input", render);
  $("types").addEventListener("click", (e) => {
    const b = e.target.closest("[data-type]");
    if (!b) return;
    type = b.dataset.type;
    $("types").querySelectorAll("[data-type]").forEach((x) => x.setAttribute("aria-pressed", x === b));
    render();
  });
  $("grid").addEventListener("click", (e) => {
    const b = e.target.closest("[data-slug]");
    if (b) open(models.find((m) => m.slug === b.dataset.slug));
  });
  $("paint").addEventListener("click", (e) => {
    const b = e.target.closest(".swatch");
    if (!b) return;
    $("paint").querySelectorAll(".swatch").forEach((x) => x.setAttribute("aria-pressed", x === b));
    const tint = $("stage").querySelector(".model__tint");
    // An inline url() resolves against the page, so the relative path works.
    if (!tint.style.maskImage) tint.style.webkitMaskImage = tint.style.maskImage = `url("${tint.dataset.mask}")`;
    tint.style.background = b.dataset.hex || "transparent";
  });
  render();
}

main().catch((e) => { $("count").textContent = `Could not load the models (${e.message}).`; });
