"""Regression: full save path uses Psycopg Cursor.executemany, not Connection.

These are deterministic adapter tests. Real Vercel/Neon integration is a separate gate.
"""
import uuid
from contextlib import nullcontext

import pytest
from fastapi import HTTPException
from webapp import main as backend


class _Result:
    def __init__(self, single=None, many=None):
        self.single = single
        self.many = many if many is not None else []

    def fetchone(self):
        return self.single

    def fetchall(self):
        return self.many


class _Cursor:
    def __init__(self, db):
        self.db = db

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def executemany(self, sql, params):
        # Crucial regression: connection itself intentionally has no executemany().
        batch = list(params)
        if "INSERT INTO ualp_responses" in sql:
            assert len(batch) == 21
            self.db.responses.extend(batch)
        elif "INSERT INTO ualp_scale_scores" in sql:
            assert len(batch) == 27
            self.db.scores.extend(batch)
        else:
            raise AssertionError("Unexpected batch statement")


class _FakeDB:
    def __init__(self):
        self.run = None
        self.responses = []
        self.scores = []
        self.options = [
            {"option_key": f"V{i}", "score_value": i} for i in range(5)
        ]
        # 21 items, six parent scales + 21 facets = 27 scales, 42 links.
        self.links = []
        self.rules = []
        size_by_parent = [4, 4, 4, 3, 3, 3]
        position = 0
        for parent, n in enumerate(size_by_parent):
            parent_id = f"PAR{parent}"
            self.rules.append(dict(
                scale_id=parent_id, method="MEAN", min_items=n,
                algorithm_version="WORKVALUES-MEAN-v1", status="DRAFT"
            ))
            for _ in range(n):
                item_id = f"I{position:02d}"
                facet_id = f"FAC{position:02d}"
                for scale_id in (parent_id, facet_id):
                    self.links.append(dict(
                        item_id=item_id, scale_id=scale_id, weight=1,
                        direction="POSITIVE"
                    ))
                self.rules.append(dict(
                    scale_id=facet_id, method="MEAN", min_items=1,
                    algorithm_version="WORKVALUES-MEAN-v1", status="DRAFT"
                ))
                position += 1
        assert len(self.links) == 42 and len(self.rules) == 27

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def transaction(self):
        return nullcontext()

    def cursor(self):
        return _Cursor(self)

    def execute(self, sql, params=()):
        if "SELECT run_id,form_id,payload_sha256 FROM ualp_assessment_runs" in sql:
            if self.run and self.run["request_id"] == params[0]:
                return _Result(self.run)
            return _Result()
        if "SELECT option_key,score_value FROM ualp_catalog_options" in sql:
            return _Result(many=self.options)
        if "SELECT l.item_id,l.scale_id,l.weight,l.direction" in sql:
            return _Result(many=self.links)
        if "SELECT scale_id,method,min_items,algorithm_version,status" in sql:
            return _Result(many=self.rules)
        if "INSERT INTO ualp_assessment_runs" in sql:
            run_id, request_id, form_id, digest, alg = params
            self.run = dict(
                run_id=run_id, request_id=request_id,
                form_id=form_id, payload_sha256=digest, algorithm_version=alg
            )
            return _Result()
        if "SELECT form_key FROM ualp_catalog_forms" in sql:
            return _Result(dict(form_key=backend.ENABLED_FORM))
        raise AssertionError(f"Unexpected SQL in test: {sql[:85]}")


@pytest.fixture
def isolated_db(monkeypatch):
    db = _FakeDB()
    monkeypatch.setattr(backend, "connect", lambda _url: db)
    items = [{"item_id": f"I{i:02d}"} for i in range(21)]
    form = dict(form_id="FORM-000004", algorithm_version="WORKVALUES-MEAN-v1")
    monkeypatch.setattr(backend, "fetch_form", lambda *_args: (form, items, db.options))

    def saved(_conn, run_id):
        assert db.run["run_id"] == run_id
        assert len(db.responses) == 21
        assert len(db.scores) == 27
        return dict(runId=str(run_id), status="COMPLETED", scoreCount=len(db.scores))

    monkeypatch.setattr(backend, "stored_result", saved)
    return db


def _payload(request_id=None, first_option="V4", count=21):
    choices = [backend.Answer(itemId=f"I{i:02d}",
                              optionKey=first_option if i == 0 else "V4")
               for i in range(count)]
    return backend.Submission(
        requestId=request_id or uuid.uuid4(),
        formKey=backend.ENABLED_FORM, consent=True, answers=choices
    )


def test_real_save_path_inserts_run_21_responses_27_scores(isolated_db):
    payload = _payload()
    result = backend.submit(payload, "mock://test")
    assert result["status"] == "COMPLETED"
    assert result["scoreCount"] == 27
    assert isolated_db.run["request_id"] == payload.requestId
    assert {x[1] for x in isolated_db.responses} == {
        f"I{i:02d}" for i in range(21)
    }
    assert {x[1] for x in isolated_db.scores} == {
        r["scale_id"] for r in isolated_db.rules
    }


def test_duplicate_request_returns_same_run_without_duplicate_writes(isolated_db):
    payload = _payload()
    first = backend.submit(payload, "mock://test")
    second = backend.submit(payload, "mock://test")
    assert first == second
    assert len(isolated_db.responses) == 21
    assert len(isolated_db.scores) == 27


def test_same_request_with_different_payload_fails_conflict(isolated_db):
    original = _payload()
    backend.submit(original, "mock://test")
    different = _payload(original.requestId, first_option="V0")
    with pytest.raises(HTTPException) as ex:
        backend.submit(different, "mock://test")
    assert ex.value.status_code == 409
    assert len(isolated_db.responses) == 21


def test_incomplete_form_does_not_insert_a_run(isolated_db):
    with pytest.raises(HTTPException) as ex:
        backend.submit(_payload(count=20), "mock://test")
    assert ex.value.status_code == 422
    assert isolated_db.run is None
    assert isolated_db.responses == []


# HTTP-layer regression cases: same deployed FastAPI routes, deterministic mocked DB.
# Not equivalent to authenticated HTTP against the real Vercel Preview runtime.
from fastapi.testclient import TestClient


def test_http_requires_secret_and_test_environment(monkeypatch):
    monkeypatch.setenv("UALP_ENV", "TEST")
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/unused")
    monkeypatch.setenv("UALP_ACCESS_KEY", "s" * 48)
    with TestClient(backend.app) as client:
        assert client.get("/api/forms/UALP_WV21_RU_LIKERT").status_code == 401
        assert client.get("/api/forms/UALP_WV21_RU_LIKERT",
                          headers={"X-UALP-Access-Key": "wrong"}).status_code == 401
        assert client.get("/api/runs/" + str(uuid.uuid4())).status_code == 401
        monkeypatch.setenv("UALP_ENV", "PROD")
        assert client.get("/api/forms/UALP_WV21_RU_LIKERT",
                          headers={"X-UALP-Access-Key": "s" * 48}).status_code == 503


def test_http_retry_conflict_and_persisted_counts(isolated_db):
    backend.app.dependency_overrides[backend.authorized] = lambda: "mock://test"
    try:
        with TestClient(backend.app) as client:
            payload = _payload().model_dump(mode="json")
            first = client.post("/api/runs", json=payload)
            assert first.status_code == 201, first.text
            assert first.json()["scoreCount"] == 27
            again = client.post("/api/runs", json=payload)
            assert again.status_code == 201, again.text
            assert again.json()["runId"] == first.json()["runId"]
            assert len(isolated_db.responses) == 21
            assert len(isolated_db.scores) == 27
            altered = _payload(uuid.UUID(payload["requestId"]), first_option="V0").model_dump(mode="json")
            conflict = client.post("/api/runs", json=altered)
            assert conflict.status_code == 409
            assert len(isolated_db.responses) == 21
            assert len(isolated_db.scores) == 27
    finally:
        backend.app.dependency_overrides.pop(backend.authorized, None)


def test_http_negative_inputs_never_write(isolated_db):
    backend.app.dependency_overrides[backend.authorized] = lambda: "mock://test"
    try:
        with TestClient(backend.app) as client:
            full = _payload().model_dump(mode="json")
            bad = [
                ({**full, "consent": False}, 422),
                ({**full, "answers": full["answers"][:-1]}, 422),
                ({**full, "answers": full["answers"][:-1] + [full["answers"][0]]}, 422),
                ({**full, "formKey": "NOT_AN_ENABLED_FORM"}, 404),
                ({**full, "answers": [{**full["answers"][0], "optionKey": "INVALID"}] +
                  full["answers"][1:]}, 422)
            ]
            for payload, expected in bad:
                response = client.post("/api/runs", json=payload)
                assert response.status_code == expected, (expected, response.text)
            assert isolated_db.run is None
            assert isolated_db.responses == []
            assert isolated_db.scores == []
    finally:
        backend.app.dependency_overrides.pop(backend.authorized, None)
