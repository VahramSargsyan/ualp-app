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
