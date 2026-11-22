import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
import fs from "node:fs";
import { marked } from "marked";

// Facts on the pages come from the data files that tools/ write, never typed by hand.
// %INDUSTRIAL_TOTAL% is the count of mapped industrial buildings in public/service-area.json.
const serviceArea = JSON.parse(fs.readFileSync(path.resolve(__dirname, "public/service-area.json"), "utf8"));
const facts = { INDUSTRIAL_TOTAL: () => serviceArea.industrial_buildings_total.toLocaleString("en-CA") };
// %BRAND_LINK% is the logo and wordmark link shared by every page header.
facts.BRAND_LINK = () => fs.readFileSync(path.resolve(__dirname, "partials/brand-link.html"), "utf8").trim();
// %PLAN_HTML% is plan/BUSINESS_PLAN.md rendered to HTML, read at build time so the page follows every edit.
// Links to other repository files become GitHub links, since only the site itself is published.
const REPO = "https://github.com/GOSTROGIS/Azza_Cars/blob/main/";
facts.PLAN_HTML = () => marked.parse(fs.readFileSync(path.resolve(__dirname, "../plan/BUSINESS_PLAN.md"), "utf8"))
  .replace(/href="\.\.\/site\/public\//g, 'href="./')
  .replace(/href="\.\.\/([^"#]+)/g, (m, p) => `href="${REPO}${p}`);
const factsPlugin = {
  name: "facts",
  transformIndexHtml: (html) => html.replace(/%([A-Z_]+)%/g, (m, k) => facts[k]?.() ?? m),
};

// base "./" keeps the build portable: it works from any sub-path or straight from disk hosting.
export default defineConfig({
  base: "./",
  plugins: [react(), factsPlugin],
  resolve: { alias: { "@design": path.resolve(__dirname, "../design") } },
  server: { fs: { allow: [".."] } },
  build: {
    chunkSizeWarningLimit: 1200,
    // The landing page is plain HTML for speed and search. The model explorer stays a React app.
    rollupOptions: { input: Object.fromEntries(["index", "explorer", "status", "plan"].map((n) => [n, path.resolve(__dirname, `${n}.html`)])) },
  },
});
