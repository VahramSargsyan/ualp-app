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



def test_05_history_paginates_and_reopens_exact_scores(api, isolated_postgres):
    # The prior tests intentionally created two synthetic completed runs.
    # All entries are generated through the real API in the disposable DB.
    assert counts(isolated_postgres) == (2, 42, 54)
    assert api.get("/api/history").status_code == 401
    assert api.get("/api/history", headers={"X-UALP-Access-Key": "bad"}).status_code == 401
    assert api.get("/api/history?cursor=bad", headers=headers()).status_code == 422
    assert api.get("/api/history?cursor=2026-11-16T00%3A00%3A00%7C"+
                   str(uuid.uuid4()), headers=headers()).status_code == 422

    added = []
    for _ in range(11):
        r = api.post("/api/runs", json=payload(), headers=headers())
        assert r.status_code == 201, r.text
        added.append(r.json()["runId"])
    before = counts(isolated_postgres)
    assert before == (13, 273, 351)

    p1 = api.get("/api/history", headers=headers())
    assert p1.status_code == 200, p1.text
    page1 = p1.json()
    assert len(page1["items"]) == 10
    assert page1["pageSize"] == 10
    assert page1["nextCursor"]
    assert all(x["status"] == "COMPLETED" for x in page1["items"])
    assert all(x["formVersion"] == "ci-v1" for x in page1["items"])
    assert all("completedAt" in x and "runId" in x for x in page1["items"])
    assert "answers" not in p1.text and "optionKey" not in p1.text
    assert "raw_score" not in p1.text
    ids1 = [x["runId"] for x in page1["items"]]
    assert len(set(ids1)) == 10

    p2 = api.get("/api/history", params={"cursor": page1["nextCursor"]},
                 headers=headers())
    assert p2.status_code == 200, p2.text
    page2 = p2.json()
    assert len(page2["items"]) == 3
    assert page2["nextCursor"] is None
    ids2 = [x["runId"] for x in page2["items"]]
    assert len(set(ids1 + ids2)) == 13
    assert set(added).issubset(ids1 + ids2)

    # Previously saved scores must reopen byte-for-byte as the stored API,
    # without a new assessment or any DB writes.
    selected = page2["items"][-1]["runId"]
    reopened = api.get("/api/runs/" + selected, headers=headers())
    assert reopened.status_code == 200
    assert reopened.json()["runId"] == selected
    assert reopened.json()["status"] == "COMPLETED"
    assert len(reopened.json()["scores"]) == 6
    assert counts(isolated_postgres) == before



def test_06_profile_aggregates_only_stored_assessments(api, isolated_postgres):
    """Actual HTTP+PG: empty coverage not invented, latest updates, second method is independent."""
    assert api.get("/api/profile").status_code == 401
    assert api.get("/api/profile", headers={"X-UALP-Access-Key":"incorrect"}).status_code == 401

    before = counts(isolated_postgres)
    assert before == (13, 273, 351)
    r = api.get("/api/profile", headers=headers())
    assert r.status_code == 200, r.text
    assert r.headers.get("cache-control") == "private, no-store"
    profile = r.json()
    assert profile["ownerMode"] == "SINGLE_OWNER_TEST"
    assert profile["methodCount"] == 1
    assert profile["completedRuns"] == 13
    assert profile["hasMoreMethods"] is False
    assert len(profile["methods"]) == 1
    values = profile["methods"][0]
    assert values["formKey"] == ENABLED_FORM
    assert values["completedRuns"] == 13
    assert values["validationStatus"] == "NOT_REVIEWED"
    assert len(values["parentScores"]) == 6
    assert "ONET_SHORT_60_DIGITAL" not in r.text
    assert "ICAR16_DIGITAL" not in r.text
    for leaked in ("requestId","payload_sha256","optionKey","answers","score_value","weight"):
        assert leaked not in r.text
    assert counts(isolated_postgres) == before

    more = payload()
    more["answers"][0]["optionKey"] = "V4"
    saved = api.post("/api/runs", json=more, headers=headers())
    assert saved.status_code == 201, saved.text
    newest_id = saved.json()["runId"]
    newer = api.get("/api/profile", headers=headers())
    assert newer.status_code == 200
    state = newer.json()
    assert state["methodCount"] == 1 and state["completedRuns"] == 14
    latest = state["methods"][0]
    assert latest["latestRunId"] == newest_id
    original_scores = {x["scaleId"]: x["mean"] for x in saved.json()["scores"]}
    latest_scores = {x["scaleId"]: x["mean"] for x in latest["parentScores"]}
    assert original_scores == latest_scores

    # A SECOND synthetic assessment is stored with its own valid parent score.
    # It does not imply that RIASEC/ICAR is supported or validated.
    second_form = "CI-PROFILE-EXTRA"
    second_key = "CI_PROFILE_EXTRA"
    second_item = "CI-PROFILE-ITEM"
    second_scale = "CI-PROFILE-PARENT"
    second_run = uuid.uuid4()
    with psycopg.connect(isolated_postgres) as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO ualp_catalog_forms
                (form_id,form_key,form_version,locale,status,validation_status,item_count,algorithm_version)
                VALUES (%s,%s,'synthetic-v1','ru','DRAFT','NOT_REVIEWED',1,'SYNTHETIC-v1')""",
                (second_form,second_key))
            cur.execute("""INSERT INTO ualp_catalog_items
                (item_id,form_id,prompt,display_order,required) VALUES (%s,%s,'Synthetic',1,true)""",
                (second_item,second_form))
            cur.execute("""INSERT INTO ualp_catalog_options
                (form_id,option_key,label,score_value,display_order) VALUES (%s,'V2','Synthetic',2,1)""",
                (second_form,))
            cur.execute("""INSERT INTO ualp_catalog_scales
                (scale_id,form_id,scale_key,label,is_parent) VALUES (%s,%s,'P1','Only synthetic score',true)""",
                (second_scale,second_form))
            cur.execute("""INSERT INTO ualp_catalog_links
                (item_id,scale_id,weight,direction) VALUES (%s,%s,1,'POSITIVE')""",
                (second_item,second_scale))
            cur.execute("""INSERT INTO ualp_catalog_scoring_rules
                (form_id,scale_id,method,min_items,algorithm_version,status)
                VALUES (%s,%s,'MEAN',1,'SYNTHETIC-v1','DRAFT')""",
                (second_form,second_scale))
            cur.execute("""INSERT INTO ualp_assessment_runs
                (run_id,request_id,form_id,payload_sha256,consent,status,algorithm_version)
                VALUES (%s,%s,%s,%s,true,'COMPLETED','SYNTHETIC-v1')""",
                (second_run,uuid.uuid4(),second_form,"f"*64))
            cur.execute("""INSERT INTO ualp_responses
                (run_id,item_id,option_key) VALUES (%s,%s,'V2')""",
                (second_run,second_item))
            cur.execute("""INSERT INTO ualp_scale_scores
                (run_id,scale_id,raw_score,answered_count,algorithm_version)
                VALUES (%s,%s,2,1,'SYNTHETIC-v1')""",
                (second_run,second_scale))

    final_count = counts(isolated_postgres)
    assert final_count == (15, 295, 379)
    response = api.get("/api/profile", headers=headers())
    assert response.status_code == 200, response.text
    final_profile = response.json()
    assert final_profile["methodCount"] == 2
    assert final_profile["completedRuns"] == 15
    by_method = {m["formKey"]:m for m in final_profile["methods"]}
    assert set(by_method) == {ENABLED_FORM, second_key}
    assert by_method[ENABLED_FORM]["completedRuns"] == 14
    assert by_method[ENABLED_FORM]["latestRunId"] == newest_id
    assert by_method[second_key]["completedRuns"] == 1
    assert by_method[second_key]["latestRunId"] == str(second_run)
    assert len(by_method[second_key]["parentScores"]) == 1
    assert float(by_method[second_key]["parentScores"][0]["mean"]) == 2
    assert counts(isolated_postgres) == final_count
