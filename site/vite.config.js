import { defineConfig } from "vite";
import path from "node:path";
import fs from "node:fs";
import { marked } from "marked";

// Facts on the pages come from the data files that tools/ write, never typed by hand.
// %INDUSTRIAL_TOTAL% is the count of mapped industrial buildings in public/service-area.json.
const serviceArea = JSON.parse(fs.readFileSync(path.resolve(__dirname, "public/service-area.json"), "utf8"));
const facts = { INDUSTRIAL_TOTAL: () => serviceArea.industrial_buildings_total.toLocaleString("en-CA") };
// %BRAND_LINK% is the logo and wordmark link shared by every page header.
facts.BRAND_LINK = () => fs.readFileSync(path.resolve(__dirname, "partials/brand-link.html"), "utf8").trim();
// renderPlan turns a file in plan/ into HTML at build time, so the plan page follows every edit.
// Links to the plan files shown on the page become tab links. Links to other repository files become GitHub links,
// since only the site itself is published.
const REPO = "https://github.com/GOSTROGIS/Azza_Cars/blob/main/";
// Charts in site/charts/ (tools/market/*.py) are inlined, so their hover titles work and they take the page fonts.
const CHART = /^\.\.\/site\/charts\/([\w-]+\.svg)$/;
marked.use({
  renderer: {
    image({ href, text }) {
      const m = CHART.exec(href);
      if (!m) return false;
      return `<figure class="chart-fig">${fs.readFileSync(path.resolve(__dirname, "charts", m[1]), "utf8").trim()}<figcaption>${text}</figcaption></figure>`;
    },
  },
});
const renderPlan = (file) => marked.parse(fs.readFileSync(path.resolve(__dirname, "../plan", file), "utf8"))
  .replace(/<p>(<figure class="chart-fig">[\s\S]*?<\/figure>)<\/p>/g, "$1")
  .replace(/href="(BUSINESS|RENTAL)_PLAN\.md"/g, (m, p) => `href="#${p === "RENTAL" ? "rental" : "plan"}"`)
  .replace(/href="\.\.\/site\/public\//g, 'href="./')
  .replace(/href="\.\.\/([^"#]+)/g, (m, p) => `href="${REPO}${p}`);
// %PLAN_HTML% and %RENTAL_HTML% are the two tabs of the plan page.
facts.PLAN_HTML = () => renderPlan("BUSINESS_PLAN.md");
facts.RENTAL_HTML = () => renderPlan("RENTAL_PLAN.md");
// %PHOTO_CREDITS% credits every hero cutout the page references, from public/hero/provenance.json (tools/hero/cutouts.py).
const heroImages = JSON.parse(fs.readFileSync(path.resolve(__dirname, "public/hero/provenance.json"), "utf8")).images;
const LICENCE_URL = { "CC BY 2.0": "https://creativecommons.org/licenses/by/2.0/", "CC BY-SA 4.0": "https://creativecommons.org/licenses/by-sa/4.0/" };
facts.PHOTO_CREDITS = (html) => {
  const hero = heroImages.filter((i) => html.includes(`hero/${i.file}`));
  const missing = hero.filter((i) => !LICENCE_URL[i.license]).map((i) => i.license);
  if (missing.length) throw new Error(`No licence URL for ${missing.join(", ")}: add it to LICENCE_URL in vite.config.js`);
  const lines = hero.map((i) => `${i.label} by <a href="${i.commons_page}">${i.author}</a>, ${i.license}.`);
  const sa = [...new Set(hero.map((i) => i.license).filter((l) => l.includes("BY-SA")))];
  if (sa.length) lines.push(`The CC BY-SA adaptations are shared under ${sa.map((l) => `<a href="${LICENCE_URL[l]}">${l}</a>`).join(", ")}.`);
  return lines.join("\n        ");
};
const factsPlugin = {
  name: "facts",
  transformIndexHtml: (html) => html.replace(/%([A-Z_]+)%/g, (m, k) => facts[k]?.(html) ?? m),
};

// base "./" keeps the build portable: it works from any sub-path or straight from disk hosting.
export default defineConfig({
  base: "./",
  plugins: [factsPlugin],
  resolve: { alias: { "@design": path.resolve(__dirname, "../design") } },
  server: { fs: { allow: [".."] } },
  build: {
    // Every page is plain HTML with a small script, for speed and search.
    rollupOptions: { input: Object.fromEntries(["index", "explorer", "status", "plan"].map((n) => [n, path.resolve(__dirname, `${n}.html`)])) },
  },
});
