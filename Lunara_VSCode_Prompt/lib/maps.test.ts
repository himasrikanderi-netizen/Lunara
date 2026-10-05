import {expect,it} from "vitest";
import {googleMapsDirections} from "./maps";
const origin={lat:17.411568,lng:78.527463},destination={lat:17.433859,lng:78.502051};
it.each(["driving","walking","cycling","rapido_bike","rapido_auto","rapido_cab"] as const)("creates real-coordinate Google Maps directions for %s",mode=>{
 const url=new URL(googleMapsDirections(origin,destination,mode));
 expect(url.hostname).toBe("www.google.com");
 expect(url.searchParams.get("origin")).toBe("17.411568,78.527463");
 expect(url.searchParams.get("destination")).toBe("17.433859,78.502051");
 expect(url.searchParams.get("travelmode")).toBe(mode==="walking"?"walking":mode==="cycling"?"bicycling":"driving");
});
