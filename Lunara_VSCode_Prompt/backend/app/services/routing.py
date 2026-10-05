"""Rank mode-specific real OSRM paths using limited OSM road context."""

from hashlib import sha256
import logging
from math import asin, cos, isfinite, radians, sin, sqrt

from app.config import Settings
from app.models import Coordinate, RiskSegment, RouteOption, RouteSearch
from app.services.providers import Geocoder, OSRMRouter, ProviderError
from app.services.scoring import label_confidence

log = logging.getLogger("lunara.routing")

UNAVAILABLE_FACTORS = [
    "historical incidents", "verified citizen reports", "street lighting",
    "visibility", "public activity", "safe-place proximity",
    "public transport availability", "temporary hotspots",
]


def _geometry(route: dict) -> list[Coordinate]:
    try:
        points = route["geometry"]["coordinates"]
        geometry = [Coordinate(lat=float(lat), lng=float(lng)) for lng, lat in points]
    except (KeyError, TypeError, ValueError) as exc:
        raise ProviderError("Routing provider returned invalid geometry") from exc
    if len(geometry) < 2 or len(geometry) > 5000:
        raise ProviderError("Routing provider returned an unusable geometry")
    return geometry


def _meters(a: Coordinate, b: Coordinate) -> float:
    lat1, lat2 = radians(a.lat), radians(b.lat)
    dlat, dlng = lat2 - lat1, radians(b.lng - a.lng)
    h = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    return 12742000 * asin(min(1, sqrt(h)))


def _validate_route(route: dict, origin: Coordinate, destination: Coordinate) -> list[Coordinate]:
    geometry = _geometry(route)
    try:
        distance, duration = float(route["distance"]), float(route["duration"])
    except (KeyError, ValueError, TypeError) as exc:
        raise ProviderError("Routing provider returned invalid distance or duration") from exc
    direct = _meters(origin, destination)
    if not all(isfinite(value) and value > 0 for value in (distance, duration)):
        raise ProviderError("Routing provider returned invalid distance or duration")
    if _meters(origin, geometry[0]) > 1500 or _meters(destination, geometry[-1]) > 1500:
        raise ProviderError("Routing provider snapped an endpoint too far from the requested coordinates")
    if distance < direct * .95 or distance > max(10000, direct * 5):
        raise ProviderError("Routing provider returned geographically implausible geometry or distance")
    return geometry


def _signature(geometry: list[Coordinate]) -> str:
    sample = geometry[:: max(1, len(geometry) // 25)]
    return sha256(repr([(round(p.lat, 4), round(p.lng, 4)) for p in sample]).encode()).hexdigest()


def _named_coverage(route: dict) -> tuple[float, float]:
    steps = [step for leg in route.get("legs", []) for step in leg.get("steps", [])]
    distance = sum(max(0, float(step.get("distance", 0))) for step in steps)
    named = sum(max(0, float(step.get("distance", 0))) for step in steps if str(step.get("name", "")).strip())
    longest_unnamed = max((max(0, float(step.get("distance", 0))) for step in steps if not str(step.get("name", "")).strip()), default=0)
    return (named / distance if distance else 0, longest_unnamed)


def _detour_points(origin: Coordinate, destination: Coordinate) -> list[Coordinate]:
    midpoint_lat = (origin.lat + destination.lat) / 2
    midpoint_lng = (origin.lng + destination.lng) / 2
    lat_delta = destination.lat - origin.lat
    lng_delta = (destination.lng - origin.lng) * cos(radians(midpoint_lat))
    length = max((lat_delta**2 + lng_delta**2) ** .5, .001)
    scale = min(.006, max(.0025, length * .35))
    return [
        Coordinate(lat=midpoint_lat + sign * (-lng_delta / length) * scale,
                   lng=midpoint_lng + sign * (lat_delta / length) * scale / max(.2, cos(radians(midpoint_lat))))
        for sign in (1, -1, 1.8, -1.8)
    ]


class RoutingService:
    def __init__(self, settings: Settings, geocoder: Geocoder | None = None, router: OSRMRouter | None = None):
        self.geocoder = geocoder or Geocoder(settings)
        self.router = router or OSRMRouter(settings)

    def search(self, query: RouteSearch) -> list[RouteOption]:
        origin = self.geocoder.locate(query.origin)
        destination = self.geocoder.locate(query.destination)
        log.info("resolved route endpoints mode=%s routing_profile=%s origin_lat=%.6f origin_lng=%.6f destination_lat=%.6f destination_lng=%.6f", query.travel_mode.value, query.travel_mode.routing_profile.value, origin.lat, origin.lng, destination.lat, destination.lng)
        if abs(origin.lat - destination.lat) + abs(origin.lng - destination.lng) < .0002:
            raise ValueError("Origin and destination are too close together")
        profile = query.travel_mode.routing_profile
        candidates = self.router.routes([origin, destination], profile)
        seen = {_signature(_validate_route(route, origin, destination)) for route in candidates}
        # OSRM may supply one or two alternatives. Ask it to route via nearby
        # map coordinates until three distinct *provider-generated* paths exist.
        for via in _detour_points(origin, destination):
            if len(candidates) >= 3:
                break
            try:
                extra = self.router.routes([origin, via, destination], profile, alternatives=False)
            except ProviderError:
                continue
            for route in extra:
                try:
                    signature = _signature(_validate_route(route, origin, destination))
                except ProviderError:
                    continue
                if signature not in seen and route.get("duration", 0) <= min(r["duration"] for r in candidates) * 2.2:
                    candidates.append(route)
                    seen.add(signature)
                    break
        if len(candidates) < 3:
            raise ProviderError(f"The {profile.value} provider could not find three distinct route alternatives")

        options: list[RouteOption] = []
        for idx, route in enumerate(candidates):
            geometry = _validate_route(route, origin, destination)
            duration = float(route["duration"])
            distance = float(route["distance"])
            coverage, longest_unnamed = _named_coverage(route)
            # An intentionally conservative map-context proxy, not an incident
            # prediction. Named-road coverage is observable, but not proof of safety.
            late = query.departure_time.hour >= 20 or query.departure_time.hour < 6
            score = round(max(35, min(65, 48 + 12 * coverage - (5 if late and longest_unnamed > 400 else 0))))
            confidence = round(max(15, min(40, 20 + 18 * coverage)))
            factors = [
                f"{coverage:.0%} of {profile.value} distance has a mapped street name; this is a navigation proxy, not proof of safety.",
                f"{profile.value.title()} distance and time come from the OpenStreetMap road network; live traffic is not included.",
            ]
            if query.travel_mode.is_rapido:
                factors.append("This is a Lunara car-road route estimate, not a Rapido quote, pickup ETA, booking, or live traffic estimate.")
            if late and longest_unnamed > 400:
                factors.append("A long unnamed stretch falls during evening or late-night travel; lighting is unknown.")
            else:
                factors.append("Incident, lighting and activity data are unavailable for this corridor.")
            stride = max(1, (len(geometry) - 1) // 12)
            sampled = geometry[::stride]
            if sampled[-1] != geometry[-1]:
                sampled.append(geometry[-1])
            options.append(RouteOption(
                id=f"osm-{idx}-{_signature(geometry)[:10]}", label="Balanced",
                duration_minutes=max(1, round(duration / 60)), distance_km=round(distance / 1000, 2),
                safety_score=score, confidence_score=confidence, confidence_label=label_confidence(confidence),
                summary=f"Limited safety data; compared using mapped {profile.value}-route context",
                factors=factors, geometry=geometry,
                risk_segments=[RiskSegment(**{"from": sampled[i], "to": sampled[i + 1], "level": "caution"}) for i in range(len(sampled) - 1)],
                travel_mode=query.travel_mode, routing_profile=profile.value, resolved_origin=origin, resolved_destination=destination,
                data_sources=["OpenStreetMap geocoding (Nominatim)", f"OpenStreetMap {profile.value} routing (OSRM)", "OSRM street names"],
                unavailable_factors=UNAVAILABLE_FACTORS + (["Rapido fare", "driver availability", "pickup ETA", "live Rapido traffic", "booking status"] if query.travel_mode.is_rapido else []),
            ))

        fastest = min(options, key=lambda r: r.duration_minutes)
        safest = max((r for r in options if r.id != fastest.id), key=lambda r: (r.safety_score, -r.duration_minutes))
        balanced = min((r for r in options if r.id not in {fastest.id, safest.id}), key=lambda r: abs(r.safety_score - safest.safety_score) + abs(r.duration_minutes - fastest.duration_minutes))
        safest.label, balanced.label, fastest.label = "Safest", "Balanced", "Fastest"
        by_label = {route.label: route for route in (safest, balanced, fastest)}
        # Preference affects display order, while all three comparison roles remain available.
        return [by_label[label] for label in (["Fastest", "Balanced", "Safest"] if query.preference >= 67 else ["Safest", "Balanced", "Fastest"])]
