import type { RoutingProfile, TravelMode } from "./types";

export const travelModeLabels: Record<TravelMode, string> = {
  driving: "Driving",
  walking: "Walking",
  cycling: "Cycling",
  rapido_bike: "Rapido Bike",
  rapido_auto: "Rapido Auto",
  rapido_cab: "Rapido Cab",
};

export const standardModes: TravelMode[] = ["driving", "walking", "cycling"];
export const rapidoModes: TravelMode[] = ["rapido_bike", "rapido_auto", "rapido_cab"];

export function isRapidoMode(mode: TravelMode): boolean {
  return rapidoModes.includes(mode);
}

export function routingProfile(mode: TravelMode): RoutingProfile {
  return isRapidoMode(mode) ? "driving" : mode as RoutingProfile;
}
