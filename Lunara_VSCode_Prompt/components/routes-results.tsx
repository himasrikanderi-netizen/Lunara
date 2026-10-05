"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Clock, Route, ShieldCheck } from "lucide-react";
import { searchRoutes } from "@/lib/api";
import type { RouteOption, RouteSearch } from "@/lib/types";
import { RouteMap } from "@/components/route-map";
import { isRapidoMode, travelModeLabels } from "@/lib/travel-mode";
import { googleMapsDirections } from "@/lib/maps";

export function RoutesResults({ query }: { query: RouteSearch | null }) {
  const [routes, setRoutes] = useState<RouteOption[]>([]);
  const [selected, setSelected] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(Boolean(query));

  useEffect(() => {
    if (!query) return;
    let cancelled = false;
    void (async () => {
      try {
        const result = await searchRoutes(query);
        if (cancelled) return;
        if (!result.routes.length) {
          setError("The routing provider returned no routes.");
          return;
        }
        setRoutes(result.routes);
        setSelected(result.routes[0]?.id ?? "");
      } catch (reason) {
        if (!cancelled) setError(reason instanceof Error ? reason.message : "The routing service could not return a live route.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [query]);

  if (loading) return <div className="container"><p>Evaluating routes and safety context…</p></div>;
  if (!query) return <div className="container form-page"><div className="card journey-card"><h1>Plan a journey</h1><p className="muted">Enter a starting point and destination to compare routes.</p><Link href="/" className="primary" style={{ display: "grid", placeContent: "center", textDecoration: "none" }}>Go to route search</Link></div></div>;

  return <div className="container">
    <div className="page-head"><div><div className="eyebrow">Route comparison</div><h1>Choose with context</h1><p className="muted">{query.origin} → {query.destination} · {new Date(query.departure_time).toLocaleString()}</p></div><Link href="/" className="secondary" style={{ textDecoration: "none", display: "grid", placeContent: "center" }}>Edit search</Link></div>
    {error && <div className="notice" role="alert" style={{ marginBottom: 16 }}><strong>Live route unavailable.</strong> {error} No distance or travel time is shown without a genuine routing-provider response. Check your locations and try again.</div>}
    {isRapidoMode(query.travel_mode) && <div className="notice rapido-notice" role="note"><strong>Route estimated by Lunara. Rapido booking/fare availability is not connected.</strong> No driver availability, pickup ETA, or live Rapido traffic is included. {routes.length > 0 && <div><a className="secondary rapido-book-button" href="https://www.rapido.bike/" target="_blank" rel="noopener noreferrer">Book with Rapido</a><span> Opens the official site; enter pickup and drop-off there. No booking has been made.</span></div>}</div>}
    {!error && routes.length > 0 && <p className="muted" style={{ fontSize: 13 }}>Travel mode: {travelModeLabels[query.travel_mode]}. OSRM estimates do not include live traffic.</p>}
    {!error && routes[0]?.resolved_origin && routes[0]?.resolved_destination && <p className="confidence">Resolved endpoints: {routes[0].resolved_origin.lat.toFixed(6)}, {routes[0].resolved_origin.lng.toFixed(6)} → {routes[0].resolved_destination.lat.toFixed(6)}, {routes[0].resolved_destination.lng.toFixed(6)}</p>}
    {routes.length > 0 && <div className="routes-layout"><div className="route-list">{routes.map(route => <article key={route.id} className={`card route-card ${selected === route.id ? "selected" : ""}`} onClick={() => setSelected(route.id)} tabIndex={0} onKeyDown={event => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); setSelected(route.id); } }} aria-label={`${route.label} route, ${route.duration_minutes} minutes, safety estimate ${route.safety_score} out of 100`}>
      <div className="route-top"><div className="route-title"><span className="badge">{route.label}</span>{route.label === "Safest" && <span className="badge" style={{ background: "var(--sage)", color: "var(--green)" }}>Recommended</span>}</div><strong>{route.duration_minutes} min</strong></div>
      <p className="route-mode-label">Travel mode: {travelModeLabels[route.travel_mode ?? query.travel_mode]}</p>
      <p className="route-estimate-label">Estimated route duration{isRapidoMode(query.travel_mode) ? " · car-road profile, not pickup ETA" : ""}</p>
      <p className="muted" style={{ margin: "8px 0 0", fontSize: 13 }}>{route.distance_km} km estimated</p>
      <div className="score-row" style={{ marginTop: 14 }}><div><span className="score">{route.safety_score}<small>/100</small></span><div className="confidence">Safety estimate · Confidence {route.confidence_score}/100 ({route.confidence_label})</div></div><ShieldCheck color="#397154" /></div>
      <div className="meter"><span style={{ width: `${route.safety_score}%` }} /></div><strong style={{ fontSize: 14 }}>{route.summary}</strong><ul className="factor-list">{route.factors.map(factor => <li key={factor}>{factor}</li>)}</ul>
      {route.data_sources?.length ? <p className="confidence">Real map data: {route.data_sources.join(", ")}.</p> : null}
      {route.unavailable_factors?.length ? <p className="confidence">Unavailable: {route.unavailable_factors.join(", ")}.</p> : null}
      {selected === route.id && route.geometry.length > 1 && <a className="secondary" href={googleMapsDirections(route.resolved_origin ?? route.geometry[0],route.resolved_destination ?? route.geometry[route.geometry.length-1],query.travel_mode)} target="_blank" rel="noopener noreferrer">Navigate in Google Maps</a>}
      {selected === route.id && <Link href="/journey" className="primary" style={{ textDecoration: "none", display: "grid", placeContent: "center" }} onClick={() => sessionStorage.setItem("lunara-route", JSON.stringify(route))}><Route size={17} /> Start Journey</Link>}
    </article>)}</div><RouteMap routes={routes} selected={selected} originName={query.origin_label ?? query.origin} destinationName={query.destination} /></div>}
    <div className="notice" style={{ marginTop: 18 }}><Clock size={15} /> Safety estimates are comparative and cannot guarantee personal safety.</div>
  </div>;
}
