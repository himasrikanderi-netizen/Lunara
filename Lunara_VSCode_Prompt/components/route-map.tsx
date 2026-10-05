"use client";

import { useCallback, useEffect, useRef } from "react";
import type { Map as MapLibreMap, Marker as MapLibreMarker } from "maplibre-gl";
import type { Coordinate, RouteOption } from "@/lib/types";

type Props = { routes: RouteOption[]; selected: string; originName: string; destinationName: string };
type MapModule = typeof import("maplibre-gl");

function markerElement(kind: "start" | "destination", name: string): HTMLButtonElement {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `route-marker route-marker-${kind}`;
  button.setAttribute("aria-label", `${kind === "start" ? "Start" : "Destination"}: ${name}`);
  const icon = document.createElement("span");
  icon.className = "route-marker-icon";
  icon.setAttribute("aria-hidden", "true");
  icon.innerHTML = kind === "start"
    ? '<svg viewBox="0 0 24 24" width="23" height="23" fill="none" stroke="currentColor" stroke-width="2.4"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3" fill="currentColor"/></svg>'
    : '<svg viewBox="0 0 24 24" width="23" height="23" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/></svg>';
  const label = document.createElement("span");
  label.className = "route-marker-label";
  const eyebrow = document.createElement("strong");
  eyebrow.textContent = kind === "start" ? "START" : "DESTINATION";
  const title = document.createElement("span");
  title.textContent = name;
  label.append(eyebrow, title);
  button.append(icon, label);
  return button;
}

function popupContent(kind: "start" | "destination", name: string, point: Coordinate): HTMLElement {
  const content = document.createElement("div");
  content.className = "route-popup";
  const title = document.createElement("strong");
  title.textContent = kind === "start" ? "Start" : "Destination";
  const place = document.createElement("span");
  place.textContent = name;
  const coordinates = document.createElement("small");
  coordinates.textContent = `${point.lat.toFixed(5)}, ${point.lng.toFixed(5)}`;
  content.append(title, place, coordinates);
  return content;
}

function addMarker(ml: MapModule, map: MapLibreMap, kind: "start" | "destination", name: string, point: Coordinate): MapLibreMarker {
  const marker = new ml.Marker({ element: markerElement(kind, name), anchor: "bottom" })
    .setLngLat([point.lng, point.lat])
    .setPopup(new ml.Popup({ offset: 25, closeButton: true }).setDOMContent(popupContent(kind, name, point)))
    .addTo(map);
  return marker;
}

export function RouteMap({ routes, selected, originName, destinationName }: Props) {
  const container = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const moduleRef = useRef<MapModule | null>(null);
  const markerRef = useRef<{ start: MapLibreMarker; destination: MapLibreMarker } | null>(null);
  const selectedRef = useRef(selected);

  const highlight = useCallback((id: string) => {
    const map = mapRef.current;
    const ml = moduleRef.current;
    if (!map || !ml) return;
    const chosen = routes.find(route => route.id === id) ?? routes[0];
    if (!chosen?.geometry.length || !map.getLayer(chosen.id)) return;
    routes.forEach(route => {
      if (!map.getLayer(route.id)) return;
      const active = route.id === chosen.id;
      map.setPaintProperty(route.id, "line-color", active ? "#5c437d" : "#aaa0ae");
      map.setPaintProperty(route.id, "line-width", active ? 7 : 4);
      map.setPaintProperty(route.id, "line-opacity", active ? 1 : .55);
    });
    map.moveLayer(chosen.id);
    const first = chosen.geometry[0];
    const last = chosen.geometry[chosen.geometry.length - 1];
    markerRef.current?.start.setLngLat([first.lng, first.lat]);
    markerRef.current?.destination.setLngLat([last.lng, last.lat]);
    markerRef.current?.start.setPopup(new ml.Popup({ offset: 25 }).setDOMContent(popupContent("start", originName, first)));
    markerRef.current?.destination.setPopup(new ml.Popup({ offset: 25 }).setDOMContent(popupContent("destination", destinationName, last)));
    const bounds = new ml.LngLatBounds();
    chosen.geometry.forEach(point => bounds.extend([point.lng, point.lat]));
    bounds.extend([first.lng, first.lat]);
    bounds.extend([last.lng, last.lat]);
    map.fitBounds(bounds, { padding: { top: 135, bottom: 90, left: 95, right: 95 }, maxZoom: 16, duration: 400 });
  }, [routes, originName, destinationName]);

  useEffect(() => {
    if (!container.current || !routes.length || !routes[0].geometry.length) return;
    let cancelled = false;
    let map: MapLibreMap | null = null;
    import("maplibre-gl").then(ml => {
      if (cancelled || !container.current) return;
      moduleRef.current = ml;
      const first = routes[0].geometry[0];
      map = new ml.Map({
        container: container.current,
        style: process.env.NEXT_PUBLIC_MAP_STYLE ?? "https://demotiles.maplibre.org/style.json",
        center: [first.lng, first.lat], zoom: 13,
      });
      mapRef.current = map;
      map.addControl(new ml.NavigationControl({ showCompass: false }), "bottom-right");
      map.on("load", () => {
        if (!map || cancelled) return;
        routes.forEach(route => {
          map!.addSource(route.id, { type: "geojson", data: {
            type: "Feature", properties: {}, geometry: { type: "LineString", coordinates: route.geometry.map(point => [point.lng, point.lat]) },
          } });
          map!.addLayer({ id: route.id, type: "line", source: route.id, layout: { "line-cap": "round", "line-join": "round" }, paint: { "line-color": "#aaa0ae", "line-width": 4, "line-opacity": .55 } });
        });
        const route = routes.find(item => item.id === selectedRef.current) ?? routes[0];
        const start = route.geometry[0];
        const destination = route.geometry[route.geometry.length - 1];
        markerRef.current = {
          start: addMarker(ml, map, "start", originName, start),
          destination: addMarker(ml, map, "destination", destinationName, destination),
        };
        highlight(selectedRef.current);
      });
    }).catch(() => { /* Keep the route header visible if the map library cannot load. */ });
    return () => {
      cancelled = true;
      markerRef.current = null;
      mapRef.current = null;
      map?.remove();
    };
  }, [routes, originName, destinationName, highlight]);

  useEffect(() => { selectedRef.current = selected; highlight(selected); }, [selected, highlight]);

  return <div className="map" aria-label="Interactive route map">
    <div ref={container} className="map-canvas" />
    <div className="map-route-header" aria-label={`Route from ${originName} to ${destinationName}`}>
      <span className="map-route-from"><strong>START</strong>{originName}</span>
      <span className="map-route-arrow" aria-hidden="true">↓</span>
      <span className="map-route-to"><strong>DESTINATION</strong>{destinationName}</span>
    </div>
    <div className="map-legend"><span><i className="dot" style={{ background: "#5c437d" }} />Selected route</span> · Drag to pan · Scroll or use +/− to zoom</div>
  </div>;
}
