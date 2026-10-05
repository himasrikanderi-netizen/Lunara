"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CheckCircle2, MapPin, Phone, Share2 } from "lucide-react";
import type { RouteOption } from "@/lib/types";
import { isRapidoMode, travelModeLabels } from "@/lib/travel-mode";
import { googleMapsDirections } from "@/lib/maps";

export default function Journey() {
  const [route, setRoute] = useState<RouteOption | null>(null);
  const [ready, setReady] = useState(false);
  const [shareMessage, setShareMessage] = useState("");
  const [manualShare, setManualShare] = useState("");
  const [arrived, setArrived] = useState(false);

  async function shareJourney() {
    if (!route) return;
    const start = route.resolved_origin ?? route.geometry[0];
    const end = route.resolved_destination ?? route.geometry.at(-1);
    if (!start || !end) return;
    const url = googleMapsDirections(start, end, route.travel_mode);
    const text = `Lunara route to ${end.lat}, ${end.lng}. This is a static directions link, not live location tracking.`;
    try {
      if (navigator.share) { await navigator.share({ title: "My Lunara route", text, url }); setShareMessage("Route link shared. Live tracking is not active."); return; }
      if (navigator.clipboard?.writeText) { await navigator.clipboard.writeText(`${text} ${url}`); setShareMessage("Route link copied. Paste it into a message to a trusted contact."); return; }
    } catch (error) { if (error instanceof DOMException && error.name === "AbortError") return; }
    setManualShare(`${text} ${url}`); setShareMessage("Copy this route link and send it to a trusted contact.");
  }

  useEffect(() => {
    let cancelled = false;
    queueMicrotask(() => {
      if (cancelled) return;
      try {
        const stored = sessionStorage.getItem("lunara-route");
        const parsed = stored ? JSON.parse(stored) as RouteOption : null;
        if (parsed?.id?.startsWith("osm-") && parsed.geometry?.length > 1 && parsed.duration_minutes > 0) setRoute(parsed);
      } catch { /* Invalid session data is treated as no active journey. */ }
      setReady(true);
    });
    return () => { cancelled = true; };
  }, []);

  if (!ready) return <div className="container"><p>Loading journey…</p></div>;
  if (!route) return <div className="container form-page"><div className="card journey-card"><h1>No active journey</h1><p className="muted">Choose a live route before starting your journey.</p><Link href="/" className="secondary">Find a route</Link></div></div>;
  if (arrived) return <div className="container form-page"><div className="success"><CheckCircle2 size={32} /><h2>Glad you arrived</h2><p>Any route link you sent remains with its recipient; Lunara does not track or revoke it.</p><Link href="/" className="secondary">Plan another trip</Link></div></div>;

  return <div className="container">
    <section className="journey-hero"><div className="eyebrow" style={{ color: "#d9ccea" }}>{travelModeLabels[route.travel_mode ?? "driving"]} route · {route.label}</div><h1>{route.travel_mode && isRapidoMode(route.travel_mode) ? "Route preview" : "On your way"}</h1><div className="eta">{route.duration_minutes} min</div><p>OSRM route estimate without live traffic · {route.distance_km} km</p><p>Safety estimate: {route.safety_score}/100 · Confidence {route.confidence_label}</p></section>
    {route.travel_mode && isRapidoMode(route.travel_mode) && <div className="notice" style={{ marginTop: 15 }}>Route estimated by Lunara. Rapido booking/fare availability is not connected. This is not a booking confirmation or pickup ETA.</div>}
    <div className="sos"><button className="secondary" onClick={() => void shareJourney()}><Share2 /> Share route link</button><a className="secondary" href={googleMapsDirections(route.resolved_origin ?? route.geometry[0],route.resolved_destination ?? route.geometry[route.geometry.length-1],route.travel_mode)} target="_blank" rel="noopener noreferrer"><MapPin /> Navigate in Google Maps</a><Link className="secondary" href="/safety"><MapPin /> Find a safe place</Link><a className="danger" href="tel:112"><Phone /> Emergency 112</a></div>
    {shareMessage&&<p role="status" className="notice">{shareMessage}{manualShare&&<input readOnly value={manualShare} aria-label="Route sharing link" onFocus={event=>event.currentTarget.select()} />}</p>}
    <section className="card journey-card" style={{ marginTop: 18 }}><h3>Route context</h3><p className="muted">This route uses mapped road context. Live incident and traffic data are not available.</p><button className="primary" onClick={() => setArrived(true)}>Arrived safely</button></section>
  </div>;
}
