import type { Report, RouteOption, RouteSearch, SafePlaceResults, Coordinate, PlaceSuggestion } from "./types";

const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 65000);
  try {
    const response = await fetch(`${base}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
      signal: controller.signal,
    });
    if (!response.ok) {
      const body = await response.json().catch(() => null) as { detail?: string } | null;
      throw new Error(body?.detail ?? `Routing service returned HTTP ${response.status}`);
    }
    return await response.json() as T;
  } finally {
    clearTimeout(timer);
  }
}

export async function searchRoutes(input: RouteSearch): Promise<{ routes: RouteOption[]; source: "live" }> {
  const { origin, destination, departure_time, preference, preferences, travel_mode } = input;
  const routes = await request<RouteOption[]>("/api/v1/routes/search", {
    method: "POST",
    body: JSON.stringify({ origin, destination, departure_time, preference, preferences, travel_mode }),
  });
  if (!routes.length || routes.some(route => !route.geometry?.length || !route.distance_km || !route.duration_minutes || !route.id.startsWith("osm-"))) {
    throw new Error("Routing provider did not return complete live routes");
  }
  return { routes, source: "live" };
}

export async function submitReport(input: Omit<Report, "id" | "status" | "reliability_score">) {
  return request<Report>("/api/v1/reports", { method: "POST", body: JSON.stringify(input) });
}
export function fetchSafePlaces(location:Coordinate,category:"hospital"|"police"|"transport") {
  const params=new URLSearchParams({lat:String(location.lat),lng:String(location.lng),category,radius_m:"5000"});
  return request<SafePlaceResults>(`/api/v1/safe-places/nearby?${params}`);
}
export function searchPlaces(query:string){return request<PlaceSuggestion[]>(`/api/v1/places/search?q=${encodeURIComponent(query)}`)}
export function reversePlace(point:Coordinate){return request<PlaceSuggestion>(`/api/v1/places/reverse?lat=${point.lat}&lng=${point.lng}`)}
