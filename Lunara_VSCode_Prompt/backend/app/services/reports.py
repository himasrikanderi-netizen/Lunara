"""Persistent citizen reports. Public reads mirror the existing RLS visibility rule."""

import logging
import re
import struct
from datetime import datetime, timedelta, timezone
from math import asin, cos, radians, sin, sqrt
from uuid import uuid4

from postgrest.exceptions import APIError
from supabase import Client

from app.config import Settings
from app.models import Coordinate, Report, ReportCreate
from app.services.supabase_client import DatabaseUnavailable, make_supabase_client

log = logging.getLogger(__name__)
REPORT_COLUMNS = "id,category,severity,description,occurred_at,location,status,reliability_score,created_at"
PUBLIC_STATUSES = ["verified", "resolved"]


def distance_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    p1, p2 = radians(a[0]), radians(b[0])
    dp, dl = radians(b[0] - a[0]), radians(b[1] - a[1])
    h = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
    return 12742000 * asin(sqrt(h))


def _location(point: object) -> Coordinate:
    """Decode the EWKB geography value returned by PostgREST."""
    if isinstance(point, dict):
        lon, lat = point["coordinates"]
        return Coordinate(lat=lat, lng=lon)
    if not isinstance(point, str):
        raise ValueError("Report location has an unsupported format")
    match = re.fullmatch(r"(?:SRID=4326;)?POINT\((-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\)", point, re.I)
    if match:
        return Coordinate(lat=float(match.group(2)), lng=float(match.group(1)))
    raw = bytes.fromhex(point.removeprefix("\\x"))
    endian = "<" if raw[0] == 1 else ">" if raw[0] == 0 else None
    if endian is None:
        raise ValueError("Report location has invalid byte order")
    kind = struct.unpack_from(endian + "I", raw, 1)[0]
    if kind & 0xFF != 1:
        raise ValueError("Report location is not a point")
    offset = 5 + (4 if kind & 0x20000000 else 0)
    lon, lat = struct.unpack_from(endian + "dd", raw, offset)
    return Coordinate(lat=lat, lng=lon)


def _report(row: dict) -> Report:
    point = _location(row["location"])
    return Report(
        id=row["id"], category=row["category"], severity=row["severity"],
        description=row.get("description"), occurred_at=row["occurred_at"],
        latitude=point.lat, longitude=point.lng, status=row["status"],
        reliability_score=row["reliability_score"], created_at=row["created_at"],
    )


class ReportService:
    def __init__(self, settings: Settings, client: Client | None = None):
        self.settings = settings
        self._client = client
        self.nearby_strategy = "not_checked"

    @property
    def client(self) -> Client:
        if self._client is None:
            self._client = make_supabase_client(self.settings)
        return self._client

    def health(self) -> bool:
        if not self.settings.supabase_configured and self._client is None:
            return False
        try:
            self.client.table("citizen_reports").select("id").limit(0).execute()
            return True
        except Exception:
            return False

    def authenticated_user_id(self, access_token: str) -> str:
        try:
            user = self.client.auth.get_user(access_token).user
            if user is None or not user.id:
                raise PermissionError("Invalid Supabase access token")
            return str(user.id)
        except PermissionError:
            raise
        except Exception as exc:
            raise PermissionError("Invalid Supabase access token") from exc

    def get(self, report_id: str) -> Report:
        try:
            rows = self.client.table("citizen_reports").select(REPORT_COLUMNS).eq("id", report_id).limit(1).execute().data
            if not rows:
                raise KeyError(report_id)
            return _report(rows[0])
        except KeyError:
            raise
        except Exception as exc:
            log.warning("Report database read failed (%s)", type(exc).__name__)
            raise DatabaseUnavailable("Report database read failed") from exc

    def _nearby_rows(
        self, lat: float, lng: float, radius_m: int, *,
        public_only: bool = False, category: str | None = None,
        since: datetime | None = None, until: datetime | None = None,
    ) -> list[dict]:
        Coordinate(lat=lat, lng=lng)
        if not 50 <= radius_m <= 5000:
            raise ValueError("radius_m must be 50–5000")
        try:
            response = self.client.rpc("lunara_nearby_reports", {
                "p_lat": lat, "p_lng": lng, "p_radius_m": radius_m,
                "p_limit": 500, "p_public_only": public_only,
            }).execute()
            self.nearby_strategy = "postgis"
            rows = response.data or []
        except APIError as exc:
            if getattr(exc, "code", None) not in {"PGRST202", "42883"}:
                log.warning("Report geospatial query failed (%s)", type(exc).__name__)
                raise DatabaseUnavailable("Report geospatial query failed") from exc
            # Existing projects may not yet have the optional indexed RPC. Never
            # download the whole table; the bounded fallback is explicitly reported.
            self.nearby_strategy = "bounded_fallback"
            try:
                query = self.client.table("citizen_reports").select(REPORT_COLUMNS)
                if public_only:
                    query = query.in_("status", PUBLIC_STATUSES)
                if category:
                    query = query.eq("category", category)
                if since:
                    query = query.gte("occurred_at", since.isoformat())
                if until:
                    query = query.lte("occurred_at", until.isoformat())
                response = query.order("occurred_at", desc=True).limit(500).execute()
                rows = response.data or []
            except Exception as fallback_exc:
                log.warning("Report bounded query failed (%s)", type(fallback_exc).__name__)
                raise DatabaseUnavailable("Report nearby query failed") from fallback_exc
        except DatabaseUnavailable:
            raise
        except Exception as exc:
            log.warning("Report geospatial query failed (%s)", type(exc).__name__)
            raise DatabaseUnavailable("Report geospatial query failed") from exc
        selected = []
        for row in rows:
            try:
                point = _location(row["location"])
                if distance_m((lat, lng), (point.lat, point.lng)) > radius_m:
                    continue
                if public_only and row["status"] not in PUBLIC_STATUSES:
                    continue
                if category and row["category"] != category:
                    continue
                occurred = datetime.fromisoformat(row["occurred_at"].replace("Z", "+00:00"))
                if since and occurred < since:
                    continue
                if until and occurred > until:
                    continue
                selected.append(row)
            except (KeyError, ValueError, TypeError, struct.error):
                continue
        return selected

    def create(self, data: ReportCreate) -> Report:
        now = datetime.now(timezone.utc)
        if data.occurred_at.tzinfo is None:
            raise ValueError("occurred_at must include a timezone")
        if abs((now - data.occurred_at).total_seconds()) > 365 * 86400:
            raise ValueError("Reports must relate to the last year")
        nearby = self._nearby_rows(
            data.latitude, data.longitude, 100, category=data.category.value,
            since=data.occurred_at - timedelta(hours=1),
            until=data.occurred_at + timedelta(hours=1),
        )
        duplicate_of = nearby[0]["id"] if nearby else None
        identifier = str(uuid4())
        payload = {
            "id": identifier, "category": data.category.value,
            "severity": data.severity, "description": data.description,
            "occurred_at": data.occurred_at.isoformat(),
            "location": f"SRID=4326;POINT({data.longitude:.8f} {data.latitude:.8f})",
            "status": "possible_duplicate" if duplicate_of else "pending",
            "reliability_score": 20 if duplicate_of else 35,
            "duplicate_of": duplicate_of,
        }
        try:
            response = self.client.table("citizen_reports").insert(payload).execute()
            if response.data:
                return _report(response.data[0])
            return self.get(identifier)
        except DatabaseUnavailable:
            raise
        except Exception as exc:
            log.warning("Report database write failed (%s)", type(exc).__name__)
            raise DatabaseUnavailable("Report database write failed") from exc

    def nearby(self, lat: float, lng: float, radius_m: int) -> list[Report]:
        # The original RLS policy makes only verified/resolved reports public.
        return [_report(row) for row in self._nearby_rows(lat, lng, radius_m, public_only=True)]

    def verify(self, report_id: str, verdict: str, user_id: str | None = None) -> Report:
        report = self.get(report_id)
        if verdict not in {"still_relevant", "no_longer_present", "duplicate_inaccurate"}:
            raise ValueError("invalid verdict")
        if user_id:
            try:
                self.client.table("report_verifications").upsert({
                    "report_id": report_id, "user_id": user_id, "verdict": verdict,
                }, on_conflict="report_id,user_id").execute()
            except Exception as exc:
                log.warning("Report verification record failed (%s)", type(exc).__name__)
                raise DatabaseUnavailable("Report verification record failed") from exc
        changes: dict[str, int | str] = {}
        if verdict == "still_relevant":
            changes["reliability_score"] = min(95, report.reliability_score + 10)
        elif verdict == "duplicate_inaccurate":
            changes["reliability_score"] = max(5, report.reliability_score - 12)
        else:
            changes["status"] = "resolved"
        try:
            response = self.client.table("citizen_reports").update(changes).eq("id", report_id).execute()
            if response.data:
                return _report(response.data[0])
            return self.get(report_id)
        except Exception as exc:
            log.warning("Report verification update failed (%s)", type(exc).__name__)
            raise DatabaseUnavailable("Report verification update failed") from exc
