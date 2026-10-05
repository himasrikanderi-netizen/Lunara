import { RoutesResults } from "@/components/routes-results";
import type { RouteSearch } from "@/lib/types";
import { travelModeLabels } from "@/lib/travel-mode";
import type { TravelMode } from "@/lib/types";

type Params = Record<string, string | string[] | undefined>;
function value(params: Params, key: string): string | undefined {
  const item = params[key];
  return typeof item === "string" ? item : undefined;
}

export default async function RoutesPage({ searchParams }: { searchParams: Promise<Params> }) {
  const params = await searchParams;
  const origin = value(params, "origin")?.trim();
  const destination = value(params, "destination")?.trim();
  const rawTime = value(params, "departure_time");
  const rawPreference = value(params, "preference");
  const rawMode = value(params, "travel_mode");
  let query: RouteSearch | null = null;
  if (origin && origin.toLowerCase() !== "current location" && destination && rawTime) {
    const date = new Date(rawTime);
    const preference = Number(rawPreference ?? 50);
    if (!Number.isNaN(date.getTime())) query = {
      origin,
      origin_label: value(params, "origin_label") === "My Current Location" ? "My Current Location" : undefined,
      destination,
      departure_time: date.toISOString(),
      preference: Number.isFinite(preference) ? Math.max(0, Math.min(100, preference)) : 50,
      travel_mode: rawMode && rawMode in travelModeLabels ? rawMode as TravelMode : "driving",
    };
  }
  return <RoutesResults query={query} />;
}
