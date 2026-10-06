"""All normal tests use an in-process Supabase fake, never the configured project."""

import os
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

# Pytest loads conftest before test modules import app.main. Environment
# overrides take precedence over backend/.env even when it contains a real key.
os.environ["SUPABASE_URL"] = ""
os.environ["SUPABASE_SECRET_KEY"] = ""


class FakeQuery:
    def __init__(self, client, table, action="select", payload=None):
        self.client, self.table, self.action, self.payload = client, table, action, payload
        self.filters = []
        self.max_rows = None
        self.desc = False

    def select(self, *_): return self
    def eq(self, key, value): self.filters.append(("eq", key, value)); return self
    def gte(self, key, value): self.filters.append(("gte", key, value)); return self
    def lte(self, key, value): self.filters.append(("lte", key, value)); return self
    def in_(self, key, value): self.filters.append(("in", key, value)); return self
    def limit(self, value): self.max_rows = value; return self
    def order(self, key, desc=False): self.order_key, self.desc = key, desc; return self
    def insert(self, payload): return FakeQuery(self.client, self.table, "insert", payload)
    def update(self, payload): return FakeQuery(self.client, self.table, "update", payload)
    def upsert(self, payload, **_): return FakeQuery(self.client, self.table, "upsert", payload)

    def execute(self):
        from app.services.reports import _location, distance_m
        if self.action == "rpc":
            rows = list(self.client.reports.values())
            point = (self.payload["p_lat"], self.payload["p_lng"])
            rows = [row for row in rows if distance_m(point, (_location(row["location"]).lat, _location(row["location"]).lng)) <= self.payload["p_radius_m"]]
            if self.payload["p_public_only"]:
                rows = [row for row in rows if row["status"] in {"verified", "resolved"}]
            return SimpleNamespace(data=rows[:self.payload["p_limit"]])
        if self.action == "insert":
            row = {**self.payload, "created_at": datetime.now(timezone.utc).isoformat()}
            self.client.reports[row["id"]] = row
            return SimpleNamespace(data=[row.copy()])
        if self.action == "upsert":
            self.client.verifications.append(self.payload.copy())
            return SimpleNamespace(data=[self.payload.copy()])
        rows = list(self.client.reports.values()) if self.table == "citizen_reports" else self.client.verifications
        for operator, key, value in self.filters:
            if operator == "eq": rows = [row for row in rows if row.get(key) == value]
            elif operator == "gte": rows = [row for row in rows if row.get(key) >= value]
            elif operator == "lte": rows = [row for row in rows if row.get(key) <= value]
            else: rows = [row for row in rows if row.get(key) in value]
        if self.action == "update":
            for row in rows: row.update(self.payload)
        if hasattr(self, "order_key"):
            rows.sort(key=lambda row: row[self.order_key], reverse=self.desc)
        if self.max_rows is not None: rows = rows[:self.max_rows]
        return SimpleNamespace(data=[row.copy() for row in rows])


class FakeSupabase:
    def __init__(self):
        self.reports = {}
        self.verifications = []
        self.auth = self

    def table(self, name): return FakeQuery(self, name)
    def rpc(self, name, payload):
        assert name == "lunara_nearby_reports"
        return FakeQuery(self, name, "rpc", payload)
    def get_user(self, token):
        if token != "valid-test-token": raise ValueError("Invalid token")
        return SimpleNamespace(user=SimpleNamespace(id="00000000-0000-4000-8000-000000000001"))


@pytest.fixture
def fake_supabase():
    return FakeSupabase()


@pytest.fixture(autouse=True)
def isolate_reports(monkeypatch, fake_supabase):
    from app import main
    from app.config import Settings
    from app.services.reports import ReportService
    monkeypatch.setattr(main, "reports", ReportService(Settings(_env_file=None), fake_supabase))
