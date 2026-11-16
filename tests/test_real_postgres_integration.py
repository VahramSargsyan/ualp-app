"""Real PostgreSQL integration, using disposable CI database and synthetic material only.

This suite MUST NEVER connect to Neon or any remote host. No real item text or
respondent data is present. The DB is a local PostgreSQL service container.
"""
import concurrent.futures
import os
import uuid
from pathlib import Path

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.conninfo import conninfo_to_dict

from webapp.main import app, ENABLED_FORM

FORM = "CI-FORM-ONLY"
KEY = "CI_ONLY_SYNTHETIC_ACCESS_KEY_1234567890123456"
PARENTS = [4, 4, 4, 3, 3, 3]


@pytest.fixture(scope="module")
def isolated_postgres():
    if os.getenv("UALP_CI_MODE") != "EPHEMERAL_POSTGRES":
        pytest.skip("Real PostgreSQL integration is intentionally CI-only")
    url = os.environ.get("UALP_CI_DATABASE_URL", "")
    try:
        params = conninfo_to_dict(url)
    except Exception as exc:
        pytest.fail(f"Invalid integration database parameters: {type(exc).__name__}")
    if params.get("host") not in ("localhost", "127.0.0.1") \
       or params.get("dbname") != "ualp_ci" or params.get("user") != "postgres":
        pytest.fail("P0: integration refuses any non-local/non-ualp_ci PostgreSQL database")
    # The CI database and password are disposable, never derived from user/Neon secrets.
    with psycopg.connect(url, autocommit=True) as conn:
        if conn.execute("SELECT count(*) FROM pg_tables WHERE schemaname='public'").fetchone()[0]:
            pytest.fail("P0: CI integration database unexpectedly contains tables")
        conn.execute(Path("migrations/001_initial_postgres_test.sql").read_text(encoding="utf-8"))

    with psycopg.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO ualp_catalog_forms
                (form_id,form_key,form_version,locale,status,validation_status,item_count,algorithm_version)
                VALUES (%s,%s,'ci-v1','ru','DRAFT','NOT_REVIEWED',21,'WORKVALUES-MEAN-v1')""",
                (FORM, ENABLED_FORM))
            cur.executemany("""INSERT INTO ualp_catalog_options
                (form_id,option_key,label,score_value,display_order) VALUES (%s,%s,%s,%s,%s)""",
                [(FORM, f"V{i}", f"Synthetic option {i}", i, i + 1) for i in range(5)])
            cur.executemany("""INSERT INTO ualp_catalog_items
                (item_id,form_id,prompt,display_order,required) VALUES (%s,%s,%s,%s,true)""",
                [(f"CIITEM{i:02d}", FORM, f"Synthetic question {i+1}", i+1) for i in range(21)])
            scales = []
            links = []
            rules = []
            index = 0
            for group, num in enumerate(PARENTS):
                parent = f"CIPARENT{group}"
                scales.append((parent, FORM, f"P{group}", f"Parent {group}", True))
                rules.append((FORM, parent, "MEAN", num, "WORKVALUES-MEAN-v1", "DRAFT"))
                for _ in range(num):
                    facet = f"CIFACET{index:02d}"
                    item = f"CIITEM{index:02d}"
                    scales.append((facet, FORM, f"F{index:02d}", f"Facet {index}", False))
                    rules.append((FORM, facet, "MEAN", 1, "WORKVALUES-MEAN-v1", "DRAFT"))
                    links.append((item, parent, 1, "POSITIVE"))
                    links.append((item, facet, 1, "POSITIVE"))
                    index += 1
            assert len(scales) == 27 and len(links) == 42 and len(rules) == 27
            cur.executemany("""INSERT INTO ualp_catalog_scales
                (scale_id,form_id,scale_key,label,is_parent) VALUES (%s,%s,%s,%s,%s)""", scales)
            cur.executemany("""INSERT INTO ualp_catalog_links
                (item_id,scale_id,weight,direction) VALUES (%s,%s,%s,%s)""", links)
            cur.executemany("""INSERT INTO ualp_catalog_scoring_rules
                (form_id,scale_id,method,min_items,algorithm_version,status)
                VALUES (%s,%s,%s,%s,%s,%s)""", rules)
    yield url
    # Service container destroyed after CI; never delete external data.


@pytest.fixture(scope="module")
def api(isolated_postgres):
    previous = {k: os.getenv(k) for k in ("UALP_ENV", "DATABASE_URL", "UALP_ACCESS_KEY")}
    os.environ.update({
        "UALP_ENV": "TEST",
        "DATABASE_URL": isolated_postgres,
        "UALP_ACCESS_KEY": KEY,
    })
    try:
        yield TestClient(app)
    finally:
        for k, v in previous.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def headers():
    return {"X-UALP-Access-Key": KEY}


def payload(request_id=None):
    return {
        "requestId": str(request_id or uuid.uuid4()),
        "formKey": ENABLED_FORM,
        "consent": True,
        "answers": [{"itemId": f"CIITEM{i:02d}", "optionKey": f"V{i%5}"} for i in range(21)]
    }


def counts(url):
    with psycopg.connect(url) as conn:
        return conn.execute("""SELECT
            (SELECT count(*) FROM ualp_assessment_runs),
            (SELECT count(*) FROM ualp_responses),
            (SELECT count(*) FROM ualp_scale_scores)""").fetchone()


def test_01_exact_catalog_and_private_boundaries(api):
    response = api.get(f"/api/forms/{ENABLED_FORM}", headers=headers())
    assert response.status_code == 200, response.text
    body = response.json()
    assert len(body["items"]) == 21
    assert len(body["options"]) == 5
    assert body["validationStatus"] == "NOT_REVIEWED"
    serialized = response.text
    for forbidden in ("score_value", "scoreValue", "isCorrect", "weight"):
        assert forbidden not in serialized
    assert api.get(f"/api/forms/{ENABLED_FORM}").status_code == 401
    assert api.get(f"/api/forms/{ENABLED_FORM}",
                   headers={"X-UALP-Access-Key": "invalid"}).status_code == 401
    assert api.get("/api/catalog").status_code == 401
    assert api.get("/api/runs/" + str(uuid.uuid4())).status_code == 401


def test_02_actual_postgres_transaction_retry_conflict(api, isolated_postgres):
    req = payload()
    first = api.post("/api/runs", json=req, headers=headers())
    assert first.status_code == 201, first.text
    result = first.json()
    assert result["status"] == "COMPLETED"
    assert len(result["scores"]) == 6
    assert counts(isolated_postgres) == (1, 21, 27)

    repeat = api.post("/api/runs", json=req, headers=headers())
    assert repeat.status_code == 201, repeat.text
    assert repeat.json() == result
    assert counts(isolated_postgres) == (1, 21, 27)

    conflicting = payload(uuid.UUID(req["requestId"]))
    conflicting["answers"][0]["optionKey"] = "V4"
    error = api.post("/api/runs", json=conflicting, headers=headers())
    assert error.status_code == 409, error.text
    assert counts(isolated_postgres) == (1, 21, 27)

    stored = api.get("/api/runs/" + result["runId"], headers=headers())
    assert stored.status_code == 200
    assert stored.json() == result

    # Prove persisted scores match independent SQL arithmetic over real rows.
    with psycopg.connect(isolated_postgres) as conn:
        rows = conn.execute("""SELECT sc.scale_id,sc.raw_score,sc.answered_count,
                  round(avg(opt.score_value*link.weight),4) AS recomputed, count(*) AS actual
           FROM ualp_scale_scores sc
           JOIN ualp_catalog_links link ON link.scale_id=sc.scale_id
           JOIN ualp_responses resp ON resp.run_id=sc.run_id AND resp.item_id=link.item_id
           JOIN ualp_catalog_items item ON item.item_id=resp.item_id
           JOIN ualp_catalog_options opt ON opt.form_id=item.form_id
                                            AND opt.option_key=resp.option_key
           WHERE sc.run_id=%s
           GROUP BY sc.scale_id,sc.raw_score,sc.answered_count""", (uuid.UUID(result["runId"]),)).fetchall()
    assert len(rows) == 27
    assert all(x[1] == x[3] and x[2] == x[4] for x in rows)


def test_03_validation_errors_cause_no_writes(api, isolated_postgres):
    before = counts(isolated_postgres)
    examples = [
        (lambda p: p.update(consent=False), 422),
        (lambda p: p.update(answers=p["answers"][:-1]), 422),
        (lambda p: p["answers"].__setitem__(0, p["answers"][1]), 422),
        (lambda p: p["answers"][0].update(optionKey="WRONG"), 422),
        (lambda p: p["answers"][0].update(itemId="UNKNOWN"), 422),
        (lambda p: p.update(formKey="NO_SUCH_FORM"), 404),
    ]
    for change, expected in examples:
        test = payload()
        change(test)
        r = api.post("/api/runs", json=test, headers=headers())
        assert r.status_code == expected, (expected, r.status_code, r.text)
        assert counts(isolated_postgres) == before


def test_04_two_simultaneous_same_id_do_not_duplicate(api, isolated_postgres):
    request = payload()
    def send(_):
        with TestClient(app) as client:
            response = client.post("/api/runs", json=request, headers=headers())
            return response.status_code, response.json()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        both = list(executor.map(send, [0, 1]))
    assert [s for s, _ in both] == [201, 201], both
    assert both[0][1] == both[1][1]
    assert counts(isolated_postgres) == (2, 42, 54)
