import type { Coordinate,TravelMode } from "./types";

export function googleMapsDirections(origin:Coordinate,destination:Coordinate,mode:TravelMode="driving") {
  const params=new URLSearchParams({api:"1",origin:`${origin.lat},${origin.lng}`,destination:`${destination.lat},${destination.lng}`,travelmode:mode==="walking"?"walking":mode==="cycling"?"bicycling":"driving",dir_action:"navigate"});
  return `https://www.google.com/maps/dir/?${params}`;
}
