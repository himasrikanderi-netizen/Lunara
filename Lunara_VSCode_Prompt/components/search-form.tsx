"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Bike, CarFront, Clock, Footprints, MapPin, Navigation } from "lucide-react";
import type { TravelMode } from "@/lib/types";
import { rapidoModes, standardModes, travelModeLabels } from "@/lib/travel-mode";

function AutoRickshawIcon() {
  return <svg viewBox="0 0 32 32" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M5 22h23v-8h-7l-3-7H9l-3 7-1 8Z"/><path d="M7 14h16M12 7v7M21 14v8M5 18h23"/><circle cx="10" cy="24" r="3" fill="var(--card)"/><circle cx="24" cy="24" r="3" fill="var(--card)"/></svg>;
}

function modeIcon(mode: TravelMode) {
  if (mode === "rapido_auto") return <AutoRickshawIcon />;
  if (mode === "driving" || mode === "rapido_cab") return <CarFront size={22} aria-hidden="true" />;
  if (mode === "walking") return <Footprints size={22} aria-hidden="true" />;
  return <Bike size={22} aria-hidden="true" />;
}

function localDateTime() {
  const date = new Date(Date.now() + 15 * 60_000);
  return new Date(date.getTime() - date.getTimezoneOffset() * 60_000).toISOString().slice(0, 16);
}

function currentCoordinates(): Promise<string> {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("Your browser cannot access your location. Type a starting place instead."));
      return;
    }
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => resolve(`${coords.latitude.toFixed(6)}, ${coords.longitude.toFixed(6)}`),
      error => reject(new Error(error.code === 1
        ? "Location permission was denied. Type a starting place instead."
        : "Your location could not be found. Type a starting place instead.")),
      { enableHighAccuracy: false, timeout: 10000 },
    );
  });
}

export function SearchForm() {
  const router = useRouter();
  const [from, setFrom] = useState("Current location");
  const [to, setTo] = useState("");
  const [time, setTime] = useState(localDateTime);
  const [preference, setPreference] = useState(50);
  const [travelMode, setTravelMode] = useState<TravelMode>("driving");
  const [busy, setBusy] = useState(false);
  const [locationError, setLocationError] = useState("");
  const [currentLocationValue, setCurrentLocationValue] = useState("");

  async function locate() {
    setLocationError("");
    setBusy(true);
    try {
      const coordinates = await currentCoordinates();
      setCurrentLocationValue(coordinates);
      setFrom(coordinates);
    } catch (error) {
      setLocationError((error as Error).message);
      setFrom("");
    } finally {
      setBusy(false);
    }
  }

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const departure = new Date(time);
    if (Number.isNaN(departure.getTime())) return;
    setLocationError("");
    setBusy(true);
    try {
      const usingCurrentLocation = from.trim().toLowerCase() === "current location" || Boolean(currentLocationValue && from.trim() === currentLocationValue);
      const origin = from.trim().toLowerCase() === "current location" ? await currentCoordinates() : from.trim();
      const params = new URLSearchParams({
        origin,
        ...(usingCurrentLocation ? { origin_label: "My Current Location" } : {}),
        destination: to.trim(),
        departure_time: departure.toISOString(),
        preference: String(preference),
        travel_mode: travelMode,
      });
      router.push(`/routes?${params.toString()}`);
    } catch (error) {
      setLocationError((error as Error).message);
      setFrom("");
    } finally {
      setBusy(false);
    }
  }

  return <form className="search-card" onSubmit={submit}>
    <div className="field"><label htmlFor="from">From</label><div style={{ display: "flex", gap: 8 }}><input id="from" value={from} onChange={event => { setFrom(event.target.value); setCurrentLocationValue(""); setLocationError(""); }} required /><button type="button" className="secondary" aria-label="Use my location" disabled={busy} onClick={locate}><Navigation size={18} /></button></div>{locationError && <p role="alert" className="muted">{locationError}</p>}</div>
    <div className="field"><label htmlFor="to">To</label><input id="to" value={to} placeholder="Where are you going?" onChange={event => setTo(event.target.value)} required /></div>
    <div className="field"><label htmlFor="time"><Clock size={13} /> Travel time</label><input id="time" type="datetime-local" value={time} onChange={event => setTime(event.target.value)} required /></div>
    <fieldset className="travel-mode-field"><legend>Travel mode</legend>
      <div className="mode-section-label">YOUR OWN ROUTE</div>
      <div className="travel-mode-options">{standardModes.map(mode => <label key={mode} className={`travel-mode-choice ${travelMode === mode ? "active" : ""}`}><input type="radio" name="travel-mode" value={mode} checked={travelMode === mode} onChange={() => setTravelMode(mode)} /><span className="travel-mode-icon">{modeIcon(mode)}</span><span>{travelModeLabels[mode]}</span></label>)}</div>
      <div className="mode-section-label rapido-section-label">RAPIDO</div>
      <div className="travel-mode-options">{rapidoModes.map(mode => <label key={mode} className={`travel-mode-choice ${travelMode === mode ? "active" : ""}`}><input type="radio" name="travel-mode" value={mode} checked={travelMode === mode} onChange={() => setTravelMode(mode)} /><span className="travel-mode-icon">{modeIcon(mode)}</span><span>{travelModeLabels[mode]}</span></label>)}</div>
    </fieldset>
    <div className="field"><label htmlFor="preference">Route preference</label><input className="range" id="preference" type="range" min="0" max="100" value={preference} onChange={event => setPreference(Number(event.target.value))} /><div className="range-labels"><span>Safest</span><span>Balanced</span><span>Fastest</span></div></div>
    <button className="primary" disabled={busy}><MapPin size={17} style={{ verticalAlign: "middle", marginRight: 7 }} />Find My Route</button>
  </form>;
}
