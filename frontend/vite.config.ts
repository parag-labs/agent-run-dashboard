import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "./",
  server: {
    // Proxy API calls to the FastAPI backend during local development.
    proxy: { "/api": "http://localhost:8000", "/health": "http://localhost:8000" },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./tests/setup.ts"],
  },
});
