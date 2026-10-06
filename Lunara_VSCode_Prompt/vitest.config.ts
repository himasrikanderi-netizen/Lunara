import { defineConfig } from "vitest/config";
import { fileURLToPath } from "node:url";

export default defineConfig({
  resolve: { alias: { "@": fileURLToPath(new URL(".", import.meta.url)) } },
  test: {
    testTimeout: 15000,
    include: ["lib/**/*.test.ts", "components/**/*.test.tsx"],
    exclude: ["**/node_modules/**", "**/.next/**", "**/backend/**"],
  },
});
