import { afterEach, expect, it, vi } from "vitest";
import { searchRoutes } from "./api";

afterEach(() => vi.unstubAllGlobals());

it("never substitutes demo distances when live routing fails", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 503, json: async () => ({ detail: "Driving provider unavailable" }) }));
  await expect(searchRoutes({ origin: "17.4, 78.5", destination: "Secunderabad Junction", departure_time: "2026-10-05T13:45:00Z", preference: 50, travel_mode: "driving" })).rejects.toThrow("Driving provider unavailable");
});
