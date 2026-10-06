# Lunara

Safety-aware route comparison built with Next.js, FastAPI, OpenStreetMap/Nominatim, and OSRM. Routes are real provider geometry; safety scores are comparative estimates, never guarantees.

## Local development

Run `npm install` and `npm run dev` for the frontend. In `backend/`, install `requirements.txt` and run `uvicorn app.main:app --reload --port 8000`. Copy `.env.example` to `.env.local` and set `NEXT_PUBLIC_API_URL` to the API port. Public providers are rate-limited and have no production SLA; set a distinct `GEOCODER_USER_AGENT` for deployment.

## Available features

- Driving, walking, and cycling via the corresponding OSRM road graph. Rapido Bike, Auto, and Cab retain their labels but use the car-road graph. This is not a Rapido quote, pickup estimate, availability check, or booking. The official Rapido site link does not prefill a trip.
- Current-location, typed, autocomplete, or in-app MapLibre map selection for both endpoints. Nominatim provides place search and reverse geocoding; chosen map coordinates go directly to routing while readable names remain in the UI. Live OSRM distance, duration, and geometry exclude traffic. Route failures show no invented results.
- Deterministic safety baseline using mapped road context. Incident, lighting, activity, and verified report factors are explicitly unavailable. Confidence is conservative.
- Nearby hospital, police, and transport searches using bounded OpenStreetMap queries. Results may be incomplete; opening hours and staffing are unknown.
- Trusted contacts with phone numbers stored only in the current browser. A 30-minute check-in timer persists its deadline locally and can be reset or cancelled. It is a foreground reminder, not automatic emergency notification.
- Static route-link sharing via Web Share API, clipboard, or manual copy; Google Maps directions links for routes and nearby places. There is no live location tracking.
- Reports are held only in the current API process. The community page does not fabricate a hotspot map. The PostGIS migration is a future schema and is not wired into the current prototype.

## Validation

`npm test`, `npm run lint`, `npm run typecheck`, `npm run build`, and `cd backend && python -m pytest tests -q`.

Lunara cannot guarantee personal safety. If in immediate danger, contact local emergency services.
