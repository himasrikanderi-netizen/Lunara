"""Bounded, replaceable OpenStreetMap provider adapters for local development."""

import re
import threading
import time
from urllib.parse import quote

import httpx

from app.config import Settings
from app.models import Coordinate, TravelMode


class ProviderError(Exception):
    """A remote provider could not supply trustworthy route data."""


class Geocoder:
    _coordinate_pattern = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$")

    def __init__(self, settings: Settings, client: httpx.Client | None = None):
        self.settings = settings
        self.client = client or httpx.Client(timeout=settings.provider_timeout_seconds)
        self._cache: dict[str, Coordinate] = {}
        self._lock = threading.Lock()
        self._last_request = 0.0

    def locate(self, place: str) -> Coordinate:
        if place.strip().casefold() == "current location":
            raise ValueError("Current location requires browser coordinates; enter a place name or enable location access")
        match = self._coordinate_pattern.fullmatch(place)
        if match:
            return Coordinate(lat=float(match.group(1)), lng=float(match.group(2)))
        key = place.strip().casefold()
        if not key:
            raise ProviderError("A place name is required")
        with self._lock:
            if key in self._cache:
                return self._cache[key]
            # The public Nominatim service allows at most one request per second.
            delay = 1.05 - (time.monotonic() - self._last_request)
            if delay > 0:
                time.sleep(delay)
            self._last_request = time.monotonic()
            try:
                response = self.client.get(
                    f"{self.settings.nominatim_base_url.rstrip('/')}/search",
                    params={"q": place, "format": "jsonv2", "limit": 5},
                    headers={"User-Agent": self.settings.geocoder_user_agent},
                )
                response.raise_for_status()
                matches = response.json()
                if not matches:
                    raise ProviderError(f"Place not found: {place}")
                match = matches[0]
                if "secunderabad" in key and ("railway station" in key or "junction" in key):
                    match = next((item for item in matches if "secunderabad junction" in item.get("display_name", "").casefold() and item.get("type") == "station"), None)
                    if match is None:
                        raise ProviderError("Secunderabad Junction could not be verified in geocoding results")
                coordinate = Coordinate(lat=float(match["lat"]), lng=float(match["lon"]))
            except (httpx.HTTPError, KeyError, ValueError, TypeError) as exc:
                raise ProviderError("Geocoding provider is unavailable or returned invalid data") from exc
            self._cache[key] = coordinate
            return coordinate


class OSRMRouter:
    def __init__(self, settings: Settings, client: httpx.Client | None = None):
        self.settings = settings
        self.client = client or httpx.Client(timeout=settings.provider_timeout_seconds)
        self._lock = threading.Lock()
        self._last_request = 0.0

    def routes(self, points: list[Coordinate], mode: TravelMode, alternatives: bool = True) -> list[dict]:
        if len(points) < 2 or len(points) > 3:
            raise ValueError("Routing requires two or three coordinates")
        path = ";".join(f"{p.lng:.6f},{p.lat:.6f}" for p in points)
        base = {
            TravelMode.driving: self.settings.osrm_driving_base_url,
            TravelMode.walking: self.settings.osrm_walking_base_url,
            TravelMode.cycling: self.settings.osrm_cycling_base_url,
        }[mode]
        # The mounted OSRM graph, not the API's profile path text, determines the mode.
        url = f"{base.rstrip('/')}/route/v1/driving/{quote(path, safe=';,.-')}"
        try:
            with self._lock:
                delay = 1.05 - (time.monotonic() - self._last_request)
                if delay > 0:
                    time.sleep(delay)
                self._last_request = time.monotonic()
                response = self.client.get(
                    url,
                    params={"alternatives": "3" if alternatives else "false", "steps": "true", "overview": "full", "geometries": "geojson"},
                    headers={"User-Agent": self.settings.geocoder_user_agent},
                )
            response.raise_for_status()
            payload = response.json()
            if payload.get("code") != "Ok":
                raise ProviderError(f"No {mode.value} route was found between these locations")
            routes = payload.get("routes")
            if not isinstance(routes, list) or not routes:
                raise ProviderError("Routing provider returned no routes")
            return routes
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            raise ProviderError(f"{mode.value.title()} routing provider is unavailable or returned invalid data") from exc
