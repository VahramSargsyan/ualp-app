"""Private Career KB API contract: entirely fabricated DB rows, no personal records."""
import copy
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import FastAPI, Header, HTTPException
from fastapi.testclient import TestClient
from career_kb.owner_read_api import (
    ALLOWED_CODES, EXPECTED_COUNTS, EXPECTED_DIGESTS, MANIFEST_SHA256,
    LICENSE_URL, SNAPSHOT_ID, SOURCE_HASHES, build_owner_router,
)


class Rows:
    def __init__(self, rows):
        self.rows = rows

    def fetchall(self):
        return copy.deepcopy(self.rows)


class FakeDB:
    def __init__(self):
        self.info = SimpleNamespace(host="test-example.neon.tech", dbname="ualp_test", user="ualp_test_owner")
        self.started_read_only = False
        self.queries = []
        self.snapshot = {
            "snapshot_id": SNAPSHOT_ID, "provider": "O*NET Database", "release": "31.0",
            "license_url": LICENSE_URL, "geography": "United States / O*NET-SOC taxonomy",
            "manifest_sha256": MANIFEST_SHA256,
            "file_checks": {name: {"sha256": sha} for name, sha in SOURCE_HASHES.items()},
        }
        self.digests = [dict(name=name, n=count, digest=EXPECTED_DIGESTS[name])
                        for name, count in EXPECTED_COUNTS.items()]
        self.roles = [
            {"occupation_id": f"UALP_OCC_ONET_SOC:{code}", "taxonomy": "O*NET-SOC",
             "code": code, "occupation_version_id": f"ONET_31_0_OCC:{code}",
             "source_locale": "en", "title": title,
             "description": "Synthetic description, not O*NET text"}
            for code, title in sorted(ALLOWED_CODES.items())
        ]
        self.measures = []
        for code in sorted(ALLOWED_CODES):
            for i in range(10):
                element = f"2.A.1.{chr(97+i)}"
                for scale_id in ["IM", "LV"]:
                    is_suppressed = code.endswith("01") and i == 9 and scale_id == "LV"
                    mn, mx = (1, 5) if scale_id == "IM" else (0, 7)
                    self.measures.append({
                        "code": code, "requirement_id": f"ONET_31_0_REQ:{code}:{element}:{scale_id}",
                        "source_record_id": f"O-NET31:ESSENTIAL_SKILLS:{code}:{element}:{scale_id}",
                        "element_id": element, "skill_label": f"Synthetic skill {i}",
                        "scale_id": scale_id,
                        "scale_label": "Importance" if scale_id == "IM" else "Level",
                        "minimum": Decimal(mn), "maximum": Decimal(mx),
                        "scale_minimum": Decimal(mn), "scale_maximum": Decimal(mx),
                        "raw_value": None if is_suppressed else Decimal('3.2500'),
                        "evidence_status": "SUPPRESSED" if is_suppressed else "OBSERVED",
                        "source_updated_at": "08/2026", "domain_source": "Analyst",
                    })

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def execute(self, sql, parameters=()):
        self.queries.append(sql)
        if sql == "SET TRANSACTION READ ONLY":
            self.started_read_only = True
            return Rows([])
        assert self.started_read_only, "No business SELECT before read-only transaction gate"
        if "FROM public.ualp_career_snapshots\n" in sql:
            return Rows([self.snapshot])
        if " UNION ALL " in sql:
            return Rows(self.digests)
        if "FROM public.ualp_career_occupations o" in sql:
            return Rows(self.roles)
        if "FROM public.ualp_career_requirements r" in sql:
            return Rows(self.measures)
        raise AssertionError("Unrecognized SQL: " + sql[:100])


@pytest.fixture
def api(monkeypatch):
    monkeypatch.setenv("UALP_ENV", "TEST")
    fake = FakeDB()
    calls = []

    def owner(x_ualp_access_key: str | None = Header(default=None)):
        if x_ualp_access_key != "test-owner":
            raise HTTPException(401, "Access denied")
        return "postgresql://a-secret-never-returned"

    def connect(url):
        calls.append(url)
        return fake

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.include_router(build_owner_router(owner, connect))
    with TestClient(app, base_url="https://testserver") as client:
        yield client, fake, calls


def request(client, path):
    return client.get(path, headers={"X-UALP-Access-Key": "test-owner"})


def test_owner_only_and_private_cache(api):
    client, fake, calls = api
    assert client.get("/api/careers").status_code == 401
    assert client.get("/api/careers/15-2051.00").status_code == 401
    assert calls == []
    r = request(client, "/api/careers")
    assert r.status_code == 200
    assert r.headers["cache-control"] == "no-store, private"
    d = r.json()
    assert [x["code"] for x in d["roles"]] == ["15-2051.00", "15-2051.01"]
    assert all(x["skillCount"] == 10 for x in d["roles"])
    assert d["careerFitCalculated"] is False
    assert d["source"]["release"] == "31.0"
    assert "личн" not in str(d).lower() or "личн" in d["notice"].lower()
    assert "postgresql://" not in str(d)
    assert all("INSERT INTO" not in q and "UPDATE " not in q and "DELETE FROM" not in q for q in fake.queries)


def test_both_roles_no_fit_and_suppressed_null(api):
    client, fake, _ = api
    for code in ALLOWED_CODES:
        data = request(client, "/api/careers/" + code).json()
        assert data["title"] == ALLOWED_CODES[code]
        assert data["skillCount"] == 10 and data["measurementCount"] == 20
        assert len(data["measurements"]) == 20
        assert data["careerFitCalculated"] is False
        assert all(v["scaleId"] in ("IM", "LV") for v in data["measurements"])
        assert all(isinstance(v["rawValue"], str) for v in data["measurements"] if v["rawValue"] is not None)
        if code.endswith("01"):
            no_value = [v for v in data["measurements"] if v["evidenceStatus"] == "SUPPRESSED"]
            assert len(no_value) == 1 and no_value[0]["rawValue"] is None
    assert request(client, "/api/careers/15-9999.00").status_code == 404
    assert client.post("/api/careers", headers={"X-UALP-Access-Key":"test-owner"}).status_code == 405


@pytest.mark.parametrize("mutation", [
    lambda db: db.info.__setattr__("host", "neon.example.com"),
    lambda db: db.info.__setattr__("dbname", "not_ualp_test"),
    lambda db: db.info.__setattr__("user", "other_owner"),
    lambda db: db.snapshot.__setitem__("manifest_sha256", "0"*64),
    lambda db: db.snapshot["file_checks"]["essential_skills.csv"].__setitem__("sha256", "f"*64),
    lambda db: db.digests[0].__setitem__("digest", "wrong"),
    lambda db: db.digests[-1].__setitem__("n", 39),
    lambda db: db.measures[0].__setitem__("raw_value", Decimal("99")),
    lambda db: db.measures[0].__setitem__("evidence_status", "SUPPRESSED"),
    lambda db: db.measures[-1].__setitem__("raw_value", Decimal("0")),
    lambda db: db.roles[0].__setitem__("title", "Wrong profession"),
])
def test_source_or_destination_drift_denied(api, mutation):
    client, db, calls = api
    mutation(db)
    r = request(client, "/api/careers")
    assert r.status_code == 503
    assert r.json()["detail"] == "Career KB source version unavailable or altered"
    assert "postgresql://" not in r.text


def test_non_test_environment_denied(api, monkeypatch):
    client, _, _ = api
    monkeypatch.setenv("UALP_ENV", "PROD")
    assert request(client, "/api/careers").status_code == 503


def test_failed_database_never_returns_sql_or_secrets(api):
    client, db, _ = api
    def broken(sql, params=()):
        raise RuntimeError("postgresql://SECRET@host.example/secret")
    db.execute = broken
    r = request(client,"/api/careers")
    assert r.status_code == 503
    assert "SECRET" not in r.text
