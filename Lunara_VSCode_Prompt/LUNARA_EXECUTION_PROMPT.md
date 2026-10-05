# PROJECT EXECUTION COMMAND

## 1. EXECUTION ROLE

You are the autonomous senior engineering organization responsible for designing, implementing, integrating, testing, hardening, and documenting **Lunara**.

Operate simultaneously as:

- Principal Software Architect
- Senior Next.js / TypeScript Engineer
- Senior Python / FastAPI Engineer
- PostgreSQL / Supabase Architect
- Geospatial Systems Engineer
- AI / ML Engineer
- Routing Algorithm Engineer
- Security Engineer
- Privacy Engineer
- DevOps / SRE Engineer
- QA Architect
- Product Engineer
- UI/UX Engineer
- Accessibility Engineer
- Technical Reviewer

Do not behave like a code generator producing disconnected files.

Operate against the repository as a real engineering team.

Your execution loop is:

**AUDIT → UNDERSTAND → ARCHITECT → IMPLEMENT → INTEGRATE → TEST → DEBUG → HARDEN → VERIFY → DOCUMENT → REPORT**

Do not stop after producing a plan.

Do not declare success without evidence.

---

## 2. PROJECT IDENTITY

### Product Name
**Lunara**

### Product Description
**Lunara — AI-Powered Safety-Aware Route Recommendation System for Women**

### Product Tagline
**Your safer way home.**

### Product Category
Mobile-first safety navigation web application / Progressive Web App.

### Primary Users
Women travelling through urban areas, especially students, employees, late-evening commuters, public transport users, hostel residents, solo travellers, and users travelling through unfamiliar areas.

The architecture should remain extensible to broader personal-safety use cases without removing the women-first product identity.

---

## 3. PROJECT OBJECTIVE

Build a production-quality mobile-first web application that recommends routes based not only on time and distance but also on predicted safety.

Lunara must answer:

> “Which practical route is safer for this user at the time she is expected to travel through each part of it?”

Lunara must evaluate routes using combinations of:

- open incident data
- historical incidents
- recent citizen reports
- report reliability
- street lighting / visibility
- time of day
- day of week
- road isolation
- surrounding public activity
- public transport access
- nearby safe infrastructure
- recent hotspot activity
- known temporary events when available
- route arrival time at individual road segments
- confidence and freshness of available data

The platform must produce:

1. possible routes
2. route safety scores
3. confidence scores
4. risk explanations
5. safer alternatives
6. active journey monitoring
7. dynamic re-routing
8. citizen safety reporting
9. trusted-contact journey sharing
10. hotspot and authority analytics

---

## 4. BUSINESS CONTEXT

Traditional navigation systems primarily optimize time, distance, and traffic.

Lunara introduces another dimension: **safety-aware mobility**.

The core differentiation is not merely displaying crime markers.

The product must combine predictive safety, explainable safety, confidence-aware recommendations, dynamic intelligence, community intelligence, and last-mile safety.

---

## 5. SOURCE OF TRUTH

Use this precedence:

1. Latest explicit requirements in this prompt.
2. Actual repository for implementation state.
3. This prompt for architecture unless repository compatibility requires deliberate adaptation.
4. Actual runtime/test results for behaviour.

Do not assume intended functionality already exists.

Unknown implementation details must be treated as:
`VERIFY FROM REPOSITORY`

Never invent APIs, endpoints, credentials, tables, deployment status, completed features, third-party integrations, datasets, or emergency-service integrations.

---

## 6. TECHNOLOGY BASELINE

### Frontend
**Next.js + TypeScript**

Prefer current stable Next.js and App Router unless repository evidence justifies preserving another architecture.

Frontend owns:
- UI
- rendering
- routing
- user interaction
- frontend state
- forms
- client validation
- maps
- journey visualisation
- accessibility
- PWA behaviour
- browser geolocation
- API consumption

Do not place authoritative business logic in the frontend.

### Backend
**Python + FastAPI**

Python owns:
- business logic
- route evaluation
- safety scoring
- confidence scoring
- report classification
- report reliability
- hotspot detection
- route ranking
- authorization decisions
- external integrations
- AI/ML
- background processing

### Database
**Supabase PostgreSQL + PostGIS**

Use reproducible migrations, constraints, indexes, foreign keys, geospatial indexes, transactions, timestamps, audit fields where needed, and RLS where appropriate.

Never expose privileged Supabase credentials to browser code.

---

## 7. ARCHITECTURAL BOUNDARIES

Target flow:

USER / PWA
↓
NEXT.JS + TYPESCRIPT
↓
FASTAPI / PYTHON
↓
SUPABASE POSTGRESQL + POSTGIS

Do not create a second authoritative backend inside Next.js.

---

## 8. KNOWN PROJECT CONTEXT

Lunara begins as a **mobile-first web application / Progressive Web App**, not a native mobile application.

The UI should feel feminine, modern, reassuring, elegant, clean, premium, and approachable.

Avoid stereotypical or childish design.

Do not make the interface visually frightening.

Safety information must be clear without creating panic.

Product name: **Lunara**

Tagline: **Your safer way home.**

Formal title: **Lunara — AI-Powered Safety-Aware Route Recommendation System for Women**

---

## 9. REQUIREMENTS

### P0 — Core Route Search
Users can provide source/current location, destination, departure time, and safety preference.

Generate practical route alternatives and present:
- Safest
- Balanced
- Fastest

### P0 — Road-Segment Safety Analysis
Evaluate route segments using available:
- historical incidents
- recent verified reports
- severity
- freshness
- lighting
- visibility
- isolation
- safe-place proximity
- public activity
- transport availability
- time/day
- temporary hotspots

### P0 — Time-Aware Safety
Safety depends on predicted arrival time at each segment.

### P0 — Predictive Safety Corridor
Evaluate the full route according to expected traversal time.

### P0 — Route Safety Score
Return a clear comparative score such as `Safety: 86/100`.

Never claim guaranteed safety.

### P0 — Confidence Score
Show confidence based on data quantity, freshness, reliability, coverage, and consistency.

### P0 — Explainable Recommendation
Explain why a route is safer using human-readable contributing factors.

### P0 — Citizen Incident Reporting
Support reports for:
- stalking
- harassment
- suspicious following
- verbal harassment
- unsafe transport location
- poor lighting
- isolated road
- suspicious activity
- infrastructure problems
- other safety concern

Include location, approximate time, category, severity, optional text, and privacy-preserving identity behaviour.

### P0 — Report Reliability
Implement:
- duplicate detection
- proximity correlation
- community verification
- account/source behaviour checks
- freshness
- spam controls

### P1 — AI-Assisted Report Classification
Extract category, severity, time context, location context, and risk window from free text where useful.

### P1 — Incident Decay
Older incidents should gradually contribute less to immediate-risk calculations unless repeated patterns justify persistent risk.

### P1 — Community Verification
Allow users to mark reports as still relevant, no longer present, or duplicate/inaccurate where justified.

### P1 — Temporary Hotspot Detection
Detect geographic and temporal clusters.

### P1 — Safety Heatmap
Display relative safety:
- green = relatively safer
- yellow = caution
- red = elevated risk

Never imply guaranteed safety.

### P1 — Time-Based Heatmap
Allow morning, afternoon, evening, and late-night comparison.

### P1 — Safety vs Time Slider
Implement a real backend-connected:
**Safest ←→ Balanced ←→ Fastest**

### P1 — Dynamic Re-Routing
During active journeys, monitor meaningful risk changes and recalculate alternatives.

### P1 — Safe Haven Routing
Provide “Take Me Somewhere Safe” routing toward appropriate categories such as police stations, hospitals, major transport hubs, petrol stations, and verified busy public locations.

### P1 — Last-Mile Safety Mode
Give additional weight to isolation, lighting, activity, nearby safe places, and recent reports during the final part of a journey.

### P1 — Public Transport Safety Layer
Support safety context for bus stops, metro exits, railway access, interchanges, and last-mile paths where data exists.

### P1 — Trusted Contacts
Allow users to save trusted contacts securely.

### P1 — Live Trip Sharing
Use temporary, revocable, expiring journey-sharing links/sessions.

### P1 — Check-In Timer
Let users set expected arrival/check-in time and show:
- Arrived Safely
- Need Help

Do not claim authorities were contacted unless a real integration exists.

### P1 — Emergency Mode
Provide quick access to:
- emergency number
- trusted contacts
- location sharing
- nearest safe places
- nearest police/hospital

### P1 — Offline Emergency Snapshot
Cache appropriate route summary, destination, emergency numbers, selected safety information, and nearby safe places without storing excessive sensitive location history.

### P1 — Personalised Safety Preferences
Support options such as:
- avoid isolated roads
- prefer main roads
- prefer well-lit roads
- remain near public transport
- avoid underpasses
- prefer busy public areas
- minimise extra travel time

### P2 — Crowd Activity Score
Estimate relative activity only from legitimate available signals.

### P2 — Streetlight / Visibility Score
Use real data where available; do not fabricate coverage.

### P2 — Safe Travel Time Recommendation
Recommend alternate departure times when data supports lower estimated risk.

### P2 — Group Travel Mode
Only implement with privacy-preserving design; never expose identifiable stranger locations.

### P2 — Community Safety Notes
Allow moderated/validated location notes.

### P2 — Safety Trend Analytics
Provide 7/30/90-day area trends where data density supports it.

### P2 — Event-Aware Safety
Support temporary event overlays without fabricating event data.

### P2 — False Report Detection
Detect spam, duplicates, implausible submission velocity, and suspicious identical reports. Do not automatically accuse users solely from ML output.

### P2 — Authority / Campus Dashboard
Restricted role-based dashboard for hotspots, clusters, infrastructure problems, time patterns, trends, and priority areas.

### P2 — Infrastructure Issue Detection
Aggregate repeated concerns such as broken streetlights, unsafe bus stops, poor visibility, access problems, and road obstruction.

---

## 10. NON-FUNCTIONAL REQUIREMENTS

### Privacy
Location and journey data are highly sensitive. Apply data minimization.

### Reliability
Gracefully handle routing failure, missing safety data, invalid geolocation, stale feeds, map failure, and backend failure.

### Accessibility
Target WCAG-aligned behaviour with keyboard support, readable contrast, screen-reader labels, touch-friendly design, and non-colour-only risk indicators.

### Mobile First
Prioritise one-handed use, clear CTA hierarchy, large touch targets, readable route cards, and low cognitive load.

### Performance
Use lazy loading and efficient spatial queries. Avoid unnecessary recomputation.

---

## 11. UX / UI REQUIREMENTS

Visual direction:
- soft feminine modern identity
- premium minimal interface
- subtle moon-inspired branding acceptable
- rounded but not childish
- clean typography
- restrained animation
- clear maps
- strong route cards
- visible safety indicators
- explainable recommendations

Avoid:
- excessive pink
- fear-heavy red
- police/emergency aesthetics as the main brand
- generic hackathon dashboard styling
- fake statistics
- excessive glassmorphism

Suggested home screen:
**Lunara**
*Your safer way home.*

Inputs:
- From
- To
- Travel time
- Safety preference

CTA:
**Find Safer Routes**

---

## 12. SYSTEM ARCHITECTURE

Browser / PWA
↓
Next.js + TypeScript
↓
FastAPI
├── Routing Service
├── Safety Scoring Service
├── Confidence Service
├── Incident Service
├── Report Trust Service
├── Hotspot Service
├── Journey Service
├── Safe Place Service
├── Notification Service
└── Analytics Service
↓
Supabase PostgreSQL + PostGIS

Keep modules cohesive.

---

## 13. CURRENT IMPLEMENTATION STATE

Assume nothing.

At startup:
- inspect the repository
- determine whether it is empty, partial, prototype-quality, or already using parts of this stack
- preserve functioning systems where sensible
- do not blindly rewrite working code

Create an internal:
**CURRENT STATE → TARGET STATE → GAP MATRIX**

---

## 14. REPOSITORY AUDIT

Inspect:
- directories
- source files
- README
- package manifests
- Python dependency files
- lockfiles
- environment templates
- tests
- CI
- Docker
- migrations
- Next.js config
- TypeScript config
- Python framework/entry point
- Supabase config
- PostGIS availability
- RLS
- indexes

Where permitted:
- install dependencies
- run frontend
- run backend
- run migrations
- run tests
- lint
- type-check
- build
- inspect logs

---

## 15. GAP ANALYSIS

Classify every requested capability:
- COMPLETE
- PARTIAL
- MISSING
- BROKEN
- UNKNOWN
- FUTURE

Prioritise P0, then P1, then P2.

---

## 16. EXECUTION DEPENDENCY GRAPH

Repository Audit
→ Architecture Confirmation
→ Database Foundation
→ Backend Domain Models
→ Routing Integration
→ Safety Scoring Engine
→ Core API Contract
→ Frontend Map + Search
→ Route Comparison
→ Citizen Reporting
→ Journey Monitoring
→ Trusted Contacts / Check-In
→ Hotspots / Analytics
→ Offline/PWA
→ Security Hardening
→ Testing
→ Deployment
→ Final Audit

---

## 17. IMPLEMENTATION PHASES

### Phase 1 — Foundation
Create/preserve Next.js, FastAPI, Supabase, env config, API client, conventions, and development scripts.

### Phase 2 — Geospatial Database
Design minimum necessary schema around profiles, trusted contacts, incidents, citizen reports, verifications, hotspots, saved places, active trips, trip shares, preferences, infrastructure reports, and safe places.

These are conceptual entities, not mandatory table names.

### Phase 3 — Routing
Use an appropriate mapping/routing provider.

Prefer affordable/open technology where feasible:
- OpenStreetMap
- MapLibre
- suitable routing engine/provider

### Phase 4 — Safety Intelligence Engine
Implement a transparent deterministic baseline first. Add ML only where justified.

### Phase 5 — Confidence Engine
Keep confidence distinct from the safety score.

### Phase 6 — Explainability
Generate structured, human-readable route explanations.

### Phase 7 — Citizen Intelligence
Implement reporting, verification, decay, trust, spam protection, and hotspot aggregation.

### Phase 8 — Active Journey
Implement trip lifecycle, risk reevaluation, rerouting, and last-mile mode.

### Phase 9 — Safety Support
Implement trusted contacts, temporary trip sharing, check-in timer, safe-haven routing, and emergency screen.

### Phase 10 — Analytics
Implement heatmaps, time filters, hotspots, safety trends, and infrastructure issue aggregation.

### Phase 11 — PWA / Offline
Implement installable app behaviour and careful offline caching.

### Phase 12 — Hardening
Complete authorization, privacy review, abuse controls, rate limiting, testing, and deployment.

---

## 18. MULTI-AGENT ORCHESTRATION

If subagents are supported, use:
- Architecture Agent
- Frontend Agent
- Backend Agent
- Geospatial Agent
- Safety Intelligence Agent
- Security Agent
- QA Agent

Do not assign multiple agents to the same critical files concurrently without coordination.

---

## 19. NEXT.JS / TYPESCRIPT IMPLEMENTATION

Use:
- strict TypeScript
- reusable components
- coherent feature modules
- accessible components
- responsive layouts
- loading/error/empty states
- lazy-loaded maps where appropriate
- real validation

Potential pages:
- `/` route search
- `/routes` route comparison
- `/journey` active journey
- `/report` submit safety report
- `/community` heatmap/reports
- `/safety` safe places/emergency
- `/dashboard` user dashboard
- `/authority` restricted analytics dashboard

Adapt to repository structure.

---

## 20. PYTHON BACKEND IMPLEMENTATION

Use clear layers:
- API routers
- Pydantic schemas
- domain services
- data access
- integrations
- config

Potential services:
- RoutingService
- SafetyScoringService
- ConfidenceService
- IncidentService
- ReportTrustService
- HotspotService
- JourneyService
- SafePlaceService
- NotificationService
- AnalyticsService

Avoid god classes.

---

## 21. SUPABASE / POSTGRESQL IMPLEMENTATION

Use PostGIS where appropriate.

Index based on real queries, including geospatial GiST indexes.

Use RLS for appropriate user-owned data such as trusted contacts, saved places, trips, profile, and report ownership.

Do not rely on UI hiding for authority restrictions.

---

## 22. API CONTRACT

Define a stable typed contract between Next.js and FastAPI.

Potential conceptual endpoints:
- `POST /routes/search`
- `GET /routes/{route_id}/explanation`
- `POST /reports`
- `GET /reports/nearby`
- `POST /reports/{id}/verify`
- `GET /heatmap`
- `GET /hotspots`
- `POST /journeys`
- `GET /journeys/{id}`
- `POST /journeys/{id}/recalculate`
- `POST /journeys/{id}/complete`
- `POST /trusted-contacts`
- `GET /trusted-contacts`
- `POST /journeys/{id}/share`
- `DELETE /journeys/{id}/share`
- `GET /safe-places/nearby`
- `GET /analytics/safety-trends`

These are illustrative. Confirm actual needs before creating endpoints.

---

## 23. AUTHENTICATION / AUTHORIZATION

Determine whether Supabase Auth fits the project.

If used:
**Next.js → FastAPI → Supabase**

Validate identity consistently.

Never trust frontend-provided user IDs or roles.

Potential roles only where justified:
- regular user
- moderator
- authorised campus/authority user
- admin

---

## 24. SECURITY

Review:
- location privacy
- trip sharing token security
- citizen report abuse
- doxxing risk
- trusted contact protection
- authority dashboard access
- XSS
- SQL injection
- IDOR
- rate limiting
- CORS
- CSRF where applicable
- secret leakage
- sensitive logs
- privileged Supabase key exposure

Never expose exact private trip histories unnecessarily.

---

## 25. PERFORMANCE

Watch for:
- map bundle size
- repeated spatial queries
- too many map markers
- large route geometries
- repeated safety calculations
- expensive heatmap queries

Use:
- clustering
- bounded spatial queries
- geospatial indexes
- cached aggregates
- background hotspot calculations
- lazy-loaded maps
- sensible route-evaluation limits

Never invent performance measurements.

---

## 26. TESTING

### Frontend
Test:
- route search
- safety slider
- route cards
- explanations
- heatmap filters
- report form
- journey state
- check-in
- trusted contacts
- accessibility

### Backend
Test:
- safety scoring
- confidence
- incident decay
- route ranking
- hotspot detection
- report validation
- auth
- trip lifecycle

### Database
Test:
- constraints
- relationships
- spatial queries
- RLS
- role access

### End-to-End Critical Flows
1. Search → routes → safety evaluation → safest route → explanation
2. Citizen report → validation → storage → risk influence
3. Start journey → risk change → alternative route
4. Trusted contact → temporary share → expiry/revocation
5. Authority login → restricted analytics → unauthorized access denied

---

## 27. OBSERVABILITY

Implement appropriate:
- structured logs
- API error logs
- health endpoint
- startup validation
- critical background-task logging

Never log secrets, exact private trip history unnecessarily, or sensitive contact data.

---

## 28. DEPLOYMENT

Suggested:
- Frontend: Vercel or equivalent
- Backend: Render or equivalent
- Database: Supabase

Verify:
- environment variables
- CORS
- HTTPS
- migrations
- startup
- API URL
- production build
- map provider config
- health checks

Maintain `.env.example`.

Never commit secrets.

---

## 29. DOCUMENTATION

Update README with:
- what Lunara is
- architecture
- features
- stack
- setup
- env variables
- local development
- testing
- deployment

Document the safety model at a high level.

Include:
**Lunara provides safety recommendations based on available data and cannot guarantee personal safety.**

---

## 30. VALIDATION GATES

After each major phase run relevant:
1. frontend lint
2. TypeScript checks
3. frontend tests
4. Python tests
5. API tests
6. migration checks
7. production build
8. critical workflow tests
9. authorization checks
10. regression tests

If validation fails:
**STOP → DIAGNOSE → FIX → RE-RUN**

---

## 31. FAILURE RECOVERY

For failures:
1. capture exact error
2. reproduce
3. identify root cause
4. inspect impacted dependencies
5. fix root cause
6. rerun failed test
7. run nearby regression tests
8. continue

Never:
- disable tests for green status
- swallow errors
- replace required features with unmarked mocks
- weaken security
- claim broken integrations are complete

---

## 32. STOP / ASK CONDITIONS

Continue autonomously unless:
- destructive production action is required
- essential credentials are unavailable
- irreversible architecture cannot be responsibly inferred
- explicit requirements fundamentally conflict
- real emergency-service activation requires authorization
- a paid service would create unavoidable financial commitment

For ordinary ambiguity, choose the safest reversible implementation and continue.

---

## 33. FINAL FORENSIC AUDIT

Verify:
- search
- route alternatives
- safety scoring
- confidence
- explanations
- reporting
- active journey
- trusted contacts
- heatmap
- responsiveness
- accessibility
- no dead buttons
- backend logic
- migrations
- RLS
- PostGIS queries
- secrets
- trip-sharing security
- role checks
- actual Next.js ↔ FastAPI ↔ Supabase integration

---

## 34. DEFINITION OF DONE

Lunara is complete only when required functionality is:

**IMPLEMENTED + INTEGRATED + TESTED + VERIFIED**

P0 and P1 features require evidence.

---

## 35. EVIDENCE MATRIX

Produce a final table:

| Requirement | Priority | Implementation | Validation | Evidence | Result |
|---|---|---|---|---|---|

Include every P0 and P1 requirement.

---

## 36. FINAL REPORT

Finish with:

### COMPLETED
What genuinely works.

### CHANGED
Important files/modules.

### ARCHITECTURE
Final system design.

### VERIFIED
Commands/tests/builds actually executed.

### SECURITY
Controls verified.

### DATA / AI
Clearly distinguish:
- real data
- seed/demo data
- simulated data

### REMAINING
Only genuinely incomplete work.

### RISKS
Known limitations.

### COMMANDS
How to run frontend/backend/tests/build/migrations.

### EVIDENCE
Final requirement evidence matrix.

---

# PRODUCT SAFETY PRINCIPLES

Never claim:
- “This route is completely safe.”
- “No crime will occur.”
- “This area is guaranteed safe.”

Prefer:
- “Lower estimated risk”
- “Safer according to available data”
- “Elevated risk reported”
- “Limited data available”
- “Confidence: Low / Medium / High”

Safety scores are comparative estimates, not guarantees.

---

# FINAL USER EXPERIENCE

Primary result should conceptually show:

**LUNARA**
*Your safer way home.*

Recommended:
**SAFEST ROUTE**

- travel time
- safety score
- confidence
- explanation
- start journey

Alternative cards:
- Balanced
- Fastest

During travel:
- active journey
- ETA
- current route safety
- share journey
- emergency
- find safe place

When conditions change:
- show safety update
- compare current vs alternative
- show extra travel time
- allow switching to safer route

---

# FINAL DIRECTIVE

Build **Lunara** as a coherent, polished, functioning system.

Prioritise:
1. correctness
2. safety
3. privacy
4. working integration
5. explainability
6. strong UX
7. maintainability
8. evidence-based completion

Do not build disconnected demos.
Do not produce fake functionality.
Do not over-engineer.
Use deterministic approaches when stronger than weak ML.
Use AI only where it adds real value.
Preserve working repository functionality.
Inspect before modifying.
Debug failures.
Continue through implementation rather than stopping at planning.

Execute the project now.
