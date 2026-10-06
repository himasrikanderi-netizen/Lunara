from datetime import datetime, timezone
import struct

import pytest
from postgrest.exceptions import APIError
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app
from app.models import ReportCreate
from app.services.reports import ReportService, _location
from app.services.supabase_client import DatabaseUnavailable


def report_data(**changes):
    data = {
        "category": "poor_lighting", "severity": 3, "description": "unit-test-only",
        "latitude": 17.411568, "longitude": 78.527463,
        "occurred_at": datetime.now(timezone.utc),
    }
    return ReportCreate(**{**data, **changes})


def test_report_and_verification_persist_across_service_instances(fake_supabase):
    settings = Settings(_env_file=None)
    first = ReportService(settings, fake_supabase)
    created = first.create(report_data())
    assert created.status == "pending"
    assert created.created_at is not None
    second = ReportService(settings, fake_supabase)
    assert second.get(created.id).description == "unit-test-only"
    changed = second.verify(created.id, "still_relevant")
    assert changed.reliability_score == 45
    third = ReportService(settings, fake_supabase)
    assert third.get(created.id).reliability_score == 45
    assert third.nearby(17.411568, 78.527463, 1000) == []  # Mirrors public RLS visibility.
    third.verify(created.id, "no_longer_present")
    nearby = third.nearby(17.411568, 78.527463, 1000)
    assert len(nearby) == 1 and nearby[0].status == "resolved"
    assert third.nearby_strategy == "postgis"


def test_duplicate_detection_uses_persistent_nearby_records(fake_supabase):
    service = ReportService(Settings(_env_file=None), fake_supabase)
    first = service.create(report_data())
    duplicate = ReportService(Settings(_env_file=None), fake_supabase).create(report_data())
    assert duplicate.status == "possible_duplicate"
    assert duplicate.reliability_score == 20
    assert fake_supabase.reports[duplicate.id]["duplicate_of"] == first.id


def test_authenticated_verification_records_user_and_anonymous_does_not(fake_supabase):
    service = ReportService(Settings(_env_file=None), fake_supabase)
    created = service.create(report_data())
    service.verify(created.id, "still_relevant")
    assert fake_supabase.verifications == []
    user_id = service.authenticated_user_id("valid-test-token")
    service.verify(created.id, "duplicate_inaccurate", user_id)
    assert fake_supabase.verifications[-1] == {
        "report_id": created.id, "user_id": user_id, "verdict": "duplicate_inaccurate"
    }
    with pytest.raises(PermissionError):
        service.authenticated_user_id("bad-token")


def test_missing_configuration_fails_closed():
    service = ReportService(Settings(_env_file=None, supabase_url=None, supabase_secret_key=None))
    assert not service.health()
    with pytest.raises(DatabaseUnavailable, match="not configured"):
        service.create(report_data())


def test_geography_ewkb_decodes_longitude_then_latitude():
    raw = struct.pack("<BII2d", 1, 0x20000001, 4326, 78.527463, 17.411568)
    assert _location(raw.hex()).model_dump() == {"lat": 17.411568, "lng": 78.527463}


def test_missing_geo_rpc_uses_bounded_database_fallback(fake_supabase):
    def missing_rpc(*_):
        raise APIError({"code": "PGRST202", "message": "missing function", "details": None, "hint": None})
    fake_supabase.rpc = missing_rpc
    service = ReportService(Settings(_env_file=None), fake_supabase)
    created = service.create(report_data())
    assert service.nearby_strategy == "bounded_fallback"
    service.verify(created.id, "no_longer_present")
    assert [row.id for row in service.nearby(17.411568, 78.527463, 1000)] == [created.id]
    assert service.nearby_strategy == "bounded_fallback"


def test_database_health_and_public_nearby_api_use_fake(fake_supabase):
    client = TestClient(app)
    assert client.get("/health/db").status_code == 200
    created = client.post("/api/v1/reports", json=report_data().model_dump(mode="json"))
    assert created.status_code == 201
    nearby = client.get("/api/v1/reports/nearby", params={"lat": 17.411568, "lng": 78.527463})
    assert nearby.status_code == 200 and nearby.json() == []
    assert nearby.headers["x-lunara-nearby-strategy"] == "postgis"
    verified = client.post(
        f"/api/v1/reports/{created.json()['id']}/verify",
        json={"verdict": "no_longer_present"},
        headers={"Authorization": "Bearer valid-test-token"},
    )
    assert verified.status_code == 200
    assert len(fake_supabase.verifications) == 1
    assert len(client.get("/api/v1/reports/nearby", params={"lat": 17.411568, "lng": 78.527463}).json()) == 1
