import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

// base "./" keeps the build portable: it works from any sub-path or straight from disk hosting.
export default defineConfig({
  base: "./",
  plugins: [react()],
  resolve: { alias: { "@design": path.resolve(__dirname, "../design") } },
  server: { fs: { allow: [".."] } },
  build: {
    chunkSizeWarningLimit: 1200,
    // The landing page is plain HTML for speed and search. The model explorer stays a React app.
    rollupOptions: { input: { index: path.resolve(__dirname, "index.html"), explorer: path.resolve(__dirname, "explorer.html"), status: path.resolve(__dirname, "status.html") } },
  },
});
