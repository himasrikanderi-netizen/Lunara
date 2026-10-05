// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { SearchForm } from "./search-form";

const push = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ push }) }));

beforeEach(() => {
  push.mockReset();
});
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

it("resolves Current location before navigation", async () => {
  const getCurrentPosition = vi.fn((success: PositionCallback) => success({ coords: { latitude: 17.411568, longitude: 78.527463 } } as GeolocationPosition));
  vi.stubGlobal("navigator", { ...navigator, geolocation: { getCurrentPosition } });
  render(<SearchForm />);
  fireEvent.change(screen.getByLabelText("To"), { target: { value: "Secunderabad Railway Station, Hyderabad" } });
  fireEvent.click(screen.getByText("Find My Route"));
  await waitFor(() => expect(push).toHaveBeenCalledOnce());
  const url = new URL(push.mock.calls[0][0], "http://localhost");
  expect(url.searchParams.get("origin")).toBe("17.411568, 78.527463");
  expect(url.searchParams.get("origin_label")).toBe("My Current Location");
  expect(url.searchParams.get("destination")).toBe("Secunderabad Railway Station, Hyderabad");
  expect(url.searchParams.get("travel_mode")).toBe("driving");
  expect(getCurrentPosition).toHaveBeenCalledOnce();
});

it("shows denied permission and accepts a manually typed origin", async () => {
  const getCurrentPosition = vi.fn((_success: PositionCallback, failure: PositionErrorCallback) => failure({ code: 1 } as GeolocationPositionError));
  vi.stubGlobal("navigator", { ...navigator, geolocation: { getCurrentPosition } });
  render(<SearchForm />);
  fireEvent.change(screen.getByLabelText("To"), { target: { value: "Secunderabad Railway Station, Hyderabad" } });
  fireEvent.click(screen.getByText("Find My Route"));
  await waitFor(() => expect(screen.getByRole("alert").textContent).toMatch(/permission was denied/i));
  expect(push).not.toHaveBeenCalled();
  fireEvent.change(screen.getByLabelText("From"), { target: { value: "Osmania University, Hyderabad" } });
  fireEvent.click(screen.getByRole("radio", { name: "Cycling" }));
  fireEvent.click(screen.getByText("Find My Route"));
  await waitFor(() => expect(push).toHaveBeenCalledOnce());
  expect(new URL(push.mock.calls[0][0], "http://localhost").searchParams.get("origin")).toBe("Osmania University, Hyderabad");
  expect(new URL(push.mock.calls[0][0], "http://localhost").searchParams.get("origin_label")).toBeNull();
  expect(new URL(push.mock.calls[0][0], "http://localhost").searchParams.get("travel_mode")).toBe("cycling");
  expect(getCurrentPosition).toHaveBeenCalledOnce();
});

it.each([
  ["Driving", "driving"], ["Walking", "walking"], ["Cycling", "cycling"],
  ["Rapido Bike", "rapido_bike"], ["Rapido Auto", "rapido_auto"], ["Rapido Cab", "rapido_cab"],
])("preserves endpoints and submits %s mode", async (label, mode) => {
  render(<SearchForm />);
  fireEvent.change(screen.getByLabelText("From"), { target: { value: "Osmania University, Hyderabad" } });
  fireEvent.change(screen.getByLabelText("To"), { target: { value: "Secunderabad Railway Station, Hyderabad" } });
  fireEvent.click(screen.getByRole("radio", { name: label }));
  fireEvent.click(screen.getByText("Find My Route"));
  await waitFor(() => expect(push).toHaveBeenCalledOnce());
  const url = new URL(push.mock.calls[0][0], "http://localhost");
  expect(url.searchParams.get("origin")).toBe("Osmania University, Hyderabad");
  expect(url.searchParams.get("destination")).toBe("Secunderabad Railway Station, Hyderabad");
  expect(url.searchParams.get("travel_mode")).toBe(mode);
});
