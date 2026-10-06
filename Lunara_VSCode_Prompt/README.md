# Lunara

Safety-aware route comparison built with Next.js, FastAPI, OpenStreetMap/Nominatim, and OSRM. Routes are real provider geometry; safety scores are comparative estimates, never guarantees.

## Local development

Run `npm install` and `npm run dev` for the frontend. In `backend/`, install `requirements.txt` and run `uvicorn app.main:app --reload --port 8000`. Copy `.env.example` to `.env.local` and set `NEXT_PUBLIC_API_URL` to the API port. Public providers are rate-limited and have no production SLA; set a distinct `GEOCODER_USER_AGENT` for deployment.

For persistent reports, put `SUPABASE_URL` and `SUPABASE_SECRET_KEY` in `backend/.env` only. Never use the secret key in a `NEXT_PUBLIC_*` variable or browser code. `/health/db` checks server-side table access without revealing credentials. Normal backend tests override these environment values and use a fake database.

For indexed nearby reports, apply [the report geospatial migration](supabase/migrations/20261006063239_lunara_report_geo_query.sql) to the configured Supabase project using its SQL Editor or an authorized Supabase CLI connection. It creates a `SECURITY INVOKER` function executable only by `service_role`; it does not change existing RLS policies. Until applied, `/api/v1/reports/nearby` searches at most 500 recent rows and sets `X-Lunara-Data-Completeness: bounded-to-500-recent-reports`, so results can be incomplete on a larger dataset.

## Available features

- Driving, walking, and cycling via the corresponding OSRM road graph. Rapido Bike, Auto, and Cab retain their labels but use the car-road graph. This is not a Rapido quote, pickup estimate, availability check, or booking. The official Rapido site link does not prefill a trip.
- Current-location, typed, autocomplete, or in-app MapLibre map selection for both endpoints. Nominatim provides place search and reverse geocoding; chosen map coordinates go directly to routing while readable names remain in the UI. Live OSRM distance, duration, and geometry exclude traffic. Route failures show no invented results.
- Deterministic safety baseline using mapped road context. Incident, lighting, activity, and verified report factors are explicitly unavailable. Confidence is conservative.
- Nearby hospital, police, and transport searches using bounded OpenStreetMap queries. Results may be incomplete; opening hours and staffing are unknown.
- Trusted contacts with phone numbers stored only in the current browser. A 30-minute check-in timer persists its deadline locally and can be reset or cancelled. It is a foreground reminder, not automatic emergency notification.
- Static route-link sharing via Web Share API, clipboard, or manual copy; Google Maps directions links for routes and nearby places. There is no live location tracking.
- Reports use the server-only Supabase client and persist in `public.citizen_reports` when configured. Public nearby results include only verified/resolved reports, matching the existing RLS visibility rule. Authenticated verifications also write `public.report_verifications`; anonymous verifications preserve the prior score/status API behavior but cannot create a user-attributed verification record. The community page still does not fabricate a hotspot map. Apply the optional nearby-query migration for indexed PostGIS searches; until then, results are explicitly marked as a bounded 500-row fallback.

## Validation

`npm test`, `npm run lint`, `npm run typecheck`, `npm run build`, and `cd backend && python -m pytest tests -q`.

Lunara cannot guarantee personal safety. If in immediate danger, contact local emergency services.
