"""Look up real, mapped nearby facilities without inventing availability or staffing."""

import httpx
import threading
import time
from math import cos, radians

from app.config import Settings
from app.models import Coordinate, SafePlace
from app.services.providers import ProviderError
from app.services.reports import distance_m

FILTERS = {
    "hospital": ['nwr["amenity"="hospital"]'],
    "police": ['nwr["amenity"="police"]'],
    "transport": ['nwr["railway"="station"]', 'nwr["amenity"="bus_station"]', 'nwr["public_transport"="station"]'],
}


class SafePlaceService:
    def __init__(self, settings: Settings, client: httpx.Client | None = None):
        self.settings = settings
        self.client = client or httpx.Client(timeout=max(25, settings.provider_timeout_seconds))
        self._cache: dict[tuple, tuple[list[SafePlace], str]] = {}
        self._lock = threading.Lock()
        self._last_nominatim_request = 0.0

    def nearby(self, lat: float, lng: float, category: str, radius_m: int = 5000) -> tuple[list[SafePlace], str]:
        if category not in FILTERS:
            raise ValueError("category must be hospital, police, or transport")
        if not 100 <= radius_m <= 10000:
            raise ValueError("radius_m must be between 100 and 10000")
        origin = Coordinate(lat=lat, lng=lng)
        key = (round(lat, 4), round(lng, 4), category, radius_m)
        with self._lock:
            if key in self._cache:
                return self._cache[key]
        try:
            result = (self._nominatim_nearby(origin, category, radius_m), "OpenStreetMap via Nominatim (limited search results)")
            if result[0]:
                with self._lock:
                    self._cache[key] = result
                return result
        except ProviderError:
            pass
        result = (self._overpass_nearby(origin, category, radius_m), "OpenStreetMap via Overpass")
        with self._lock:
            self._cache[key] = result
        return result

    def _nominatim_nearby(self, origin: Coordinate, category: str, radius_m: int) -> list[SafePlace]:
        lat, lng = origin.lat, origin.lng
        lat_delta = radius_m / 111320
        lng_delta = radius_m / max(1, 111320 * cos(radians(lat)))
        viewbox = f"{lng-lng_delta:.6f},{lat+lat_delta:.6f},{lng+lng_delta:.6f},{lat-lat_delta:.6f}"
        term = {"hospital": "hospital", "police": "police station", "transport": "railway station"}[category]
        try:
            with self._lock:
                delay = 1.05 - (time.monotonic() - self._last_nominatim_request)
                if delay > 0:
                    time.sleep(delay)
                self._last_nominatim_request = time.monotonic()
                response = self.client.get(
                    f"{self.settings.nominatim_base_url.rstrip('/')}/search",
                    params={"q": term, "format": "jsonv2", "limit": 10, "viewbox": viewbox, "bounded": 1},
                    headers={"User-Agent": self.settings.geocoder_user_agent},
                )
            response.raise_for_status()
            items = response.json()
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            raise ProviderError("Nearby Nominatim search is unavailable") from exc
        places: list[SafePlace] = []
        osm_types = {"N": "node", "W": "way", "R": "relation", "node": "node", "way": "way", "relation": "relation"}
        for item in items:
            try:
                location = Coordinate(lat=float(item["lat"]), lng=float(item["lon"]))
                distance = round(distance_m((lat, lng), (location.lat, location.lng)))
                kind = osm_types.get(item.get("osm_type"))
                identifier = int(item["osm_id"])
                name = str(item.get("name") or item["display_name"].split(",")[0]).strip()
                if not kind or not name or distance > radius_m:
                    continue
                places.append(SafePlace(id=f"{kind}/{identifier}",category=category,name=name,
                                        location=location,distance_m=distance,
                                        osm_url=f"https://www.openstreetmap.org/{kind}/{identifier}"))
            except (KeyError, ValueError, TypeError):
                continue
        places.sort(key=lambda place: place.distance_m)
        return places

    def _overpass_nearby(self, origin: Coordinate, category: str, radius_m: int) -> list[SafePlace]:
        lat, lng = origin.lat, origin.lng
        selectors = "".join(f"{tag}(around:{radius_m},{lat:.6f},{lng:.6f});" for tag in FILTERS[category])
        query = f"[out:json][timeout:20];({selectors});out center 100;"
        try:
            response = self.client.post(
                self.settings.overpass_base_url,
                data={"data": query},
                headers={"User-Agent": self.settings.geocoder_user_agent},
            )
            response.raise_for_status()
            elements = response.json()["elements"]
        except (httpx.HTTPError, KeyError, ValueError, TypeError) as exc:
            raise ProviderError("Nearby OpenStreetMap place search is unavailable") from exc
        places: list[SafePlace] = []
        for item in elements:
            tags = item.get("tags") or {}
            name = tags.get("name") or tags.get("official_name")
            point = item.get("center") or item
            if not name or "lat" not in point or "lon" not in point:
                continue
            try:
                location = Coordinate(lat=float(point["lat"]), lng=float(point["lon"]))
                distance = round(distance_m((origin.lat, origin.lng), (location.lat, location.lng)))
            except (ValueError, TypeError):
                continue
            if distance > radius_m:
                continue
            kind, identifier = item.get("type"), item.get("id")
            if kind not in {"node", "way", "relation"} or not isinstance(identifier, int):
                continue
            places.append(SafePlace(id=f"{kind}/{identifier}", category=category, name=name,
                                    location=location, distance_m=distance,
                                    osm_url=f"https://www.openstreetmap.org/{kind}/{identifier}"))
        places.sort(key=lambda place: place.distance_m)
        return places[:10]
