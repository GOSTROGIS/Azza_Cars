import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
import fs from "node:fs";

// Facts on the pages come from the data files that tools/ write, never typed by hand.
// %INDUSTRIAL_TOTAL% is the count of mapped industrial buildings in public/service-area.json.
const serviceArea = JSON.parse(fs.readFileSync(path.resolve(__dirname, "public/service-area.json"), "utf8"));
const facts = { INDUSTRIAL_TOTAL: serviceArea.industrial_buildings_total.toLocaleString("en-CA") };
const factsPlugin = { name: "facts", transformIndexHtml: (html) => html.replace(/%([A-Z_]+)%/g, (m, k) => facts[k] ?? m) };

// base "./" keeps the build portable: it works from any sub-path or straight from disk hosting.
export default defineConfig({
  base: "./",
  plugins: [react(), factsPlugin],
  resolve: { alias: { "@design": path.resolve(__dirname, "../design") } },
  server: { fs: { allow: [".."] } },
  build: {
    chunkSizeWarningLimit: 1200,
    // The landing page is plain HTML for speed and search. The model explorer stays a React app.
    rollupOptions: { input: { index: path.resolve(__dirname, "index.html"), explorer: path.resolve(__dirname, "explorer.html"), status: path.resolve(__dirname, "status.html") } },
  },
});
