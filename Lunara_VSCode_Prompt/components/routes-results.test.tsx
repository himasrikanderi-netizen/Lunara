// @vitest-environment jsdom
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { RoutesResults } from "./routes-results";
import { demoRoutes } from "@/lib/demo";

const searchRoutes = vi.fn();
vi.mock("@/lib/api", () => ({ searchRoutes: (...args: unknown[]) => searchRoutes(...args) }));
vi.mock("@/components/route-map", () => ({ RouteMap: () => <div>Route map</div> }));

beforeEach(() => searchRoutes.mockReset());
afterEach(cleanup);

it("renders provider routes without a demo notice when the API succeeds", async () => {
  searchRoutes.mockResolvedValue({ routes: demoRoutes(), source: "live" });
  render(<RoutesResults query={{ origin: "Campus", destination: "Home", departure_time: "2026-10-05T13:45:00Z", preference: 30, travel_mode: "driving" }} />);
  await waitFor(() => expect(screen.getByText("Route map")).toBeTruthy());
  expect(screen.queryByText(/DEMO DATA/)).toBeNull();
  expect(screen.getByText("Recommended")).toBeTruthy();
  expect(screen.getByText("Safest")).toBeTruthy();
  expect(screen.getByText("Balanced")).toBeTruthy();
  expect(screen.getByText("Fastest")).toBeTruthy();
});

it("shows no invented route cards when the live provider returns nothing", async () => {
  searchRoutes.mockResolvedValue({ routes: [], source: "live" });
  render(<RoutesResults query={{ origin: "17.41, 78.52", destination: "Secunderabad Junction", departure_time: "2026-10-05T13:45:00Z", preference: 30, travel_mode: "driving" }} />);
  await waitFor(() => expect(screen.getByRole("alert").textContent).toMatch(/Live route unavailable/));
  expect(screen.queryByText("31 min")).toBeNull();
  expect(screen.queryByText("8.1 km estimated")).toBeNull();
  expect(document.querySelectorAll(".route-card")).toHaveLength(0);
});

it.each([
  ["rapido_bike", "Rapido Bike"], ["rapido_auto", "Rapido Auto"], ["rapido_cab", "Rapido Cab"],
] as const)("labels %s as a Lunara estimate without fare or booking claims", async (mode, label) => {
  searchRoutes.mockResolvedValue({ routes: demoRoutes().map(route => ({ ...route, travel_mode: mode, routing_profile: "driving" })), source: "live" });
  render(<RoutesResults query={{ origin: "Campus", destination: "Station", departure_time: "2026-10-05T13:45:00Z", preference: 30, travel_mode: mode }} />);
  await waitFor(() => expect(screen.getAllByText(`Travel mode: ${label}`)).toHaveLength(3));
  expect(screen.getByText(/Route estimated by Lunara\. Rapido booking\/fare availability is not connected/)).toBeTruthy();
  const booking = screen.getByRole("link", { name: "Book with Rapido" });
  expect(booking.getAttribute("href")).toBe("https://www.rapido.bike/");
  expect(screen.queryByText(/₹|fare estimate|pickup ETA:|booking confirmed/i)).toBeNull();
});
