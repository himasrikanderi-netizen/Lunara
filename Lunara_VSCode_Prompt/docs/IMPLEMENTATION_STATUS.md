# Implementation status

The repository began as an empty prompt package. This MVP establishes the full system boundary and implements the core vertical slice. “Partial” means the user flow and contract exist but production data/auth/provider configuration is still required.

| Requirement | Priority | Implementation | Validation | Result |
|---|---|---|---|---|
| Core route search | P0 | Nominatim names, OSRM pedestrian alternatives, demo fallback | API test and live HTTP | Complete for local development |
| Road-segment analysis | P0 | Real route geometry; most segment risk signals not available | scoring/API tests | Partial |
| Time-aware safety | P0 | Departure-time caution for long unnamed stretches; full segment arrival model not yet wired to live route | scoring/API tests | Partial |
| Predictive corridor | P0 | Real walking geometry with sampled corridor segments; limited safety data | API tests | Partial: data coverage |
| Safety score | P0 | Conservative mapped-street proxy, bounded and labeled as limited | API tests | Partial: incident and environment data unavailable |
| Confidence score | P0 | Separate low confidence for sparse route context | API tests | Partial: richer data unavailable |
| Explainability | P0 | Structured route factors and caveats | UI/typecheck | Complete |
| Citizen reporting | P0 | Form and API; API uses volatile memory until database wired | API tests | Partial |
| Report reliability | P0 | duplicate/proximity/freshness hooks, verification score | API tests | Partial: account behavior requires auth |
| AI classification | P1 | deterministic category input only | — | Future (no unjustified ML) |
| Incident decay | P1 | exponential half-life | unit tests | Complete |
| Community verification | P1 | three verdicts + unique DB constraint | API tests | Complete baseline |
| Temporary hotspots | P1 | geospatial storage/model | migration review | Partial: batch detector pending |
| Safety heatmap | P1 | semantic time-filtered community map | build/UI | Partial: production tiles pending |
| Time-based heatmap | P1 | four time periods | build/UI | Complete UI |
| Safety/time slider | P1 | search value reaches backend ranking | type/API test | Complete |
| Dynamic rerouting | P1 | journey recheck endpoint/UI | build/API | Partial: live provider pending |
| Safe haven routing | P1 | categories/API honest empty state | build/API | Partial: provider pending |
| Last-mile safety | P1 | model signals/UI journey mode | scoring tests | Partial: explicit weighting pending |
| Public transport layer | P1 | transport signal/schema-ready UI | scoring tests | Partial: data source pending |
| Trusted contacts | P1 | UI and encrypted-field RLS schema | migration review | Partial: auth persistence pending |
| Live trip sharing | P1 | expiring hashed-token schema/UI lifecycle | migration review | Partial: authenticated API pending |
| Check-in timer | P1 | explicit local flow and non-activation warning | build/UI | Partial |
| Emergency mode | P1 | 112, trusted contact, safe-place actions | build/UI | Complete UI |
| Offline snapshot | P1 | conservative service worker shell | build | Partial: selected route snapshot pending |
| Preferences | P1 | weighted slider and preference schema | tests/migration | Partial |

## Privacy/security notes

- Browser code receives no privileged Supabase credential.
- Sensitive tables use user-scoped RLS; anonymous access is revoked for contacts, trips, and shares.
- Public reports expose only verified/resolved rows; exact reporter identity is not part of public UI.
- Share tokens are designed for hashes, expiry, and revocation.
- CORS is allow-listed and request logs omit payloads, coordinates, tokens, and contact details.
