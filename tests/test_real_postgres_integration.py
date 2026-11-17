"""Real PostgreSQL integration, using disposable CI database and synthetic material only.

This suite MUST NEVER connect to Neon or any remote host. No real item text or
respondent data is present. The DB is a local PostgreSQL service container.
"""
import concurrent.futures
import os
import uuid
from datetime import datetime
from pathlib import Path

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.conninfo import conninfo_to_dict

from webapp.main import app, ENABLED_FORM, OWNER_RIASEC_VERSION

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
    empty_profile = api.get("/api/profile", headers=headers())
    assert empty_profile.status_code == 200
    assert empty_profile.json()["methods"] == []
    assert empty_profile.json()["methodCount"] == 0
    assert empty_profile.json()["completedRuns"] == 0
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
    assert result["formKey"] == ENABLED_FORM
    assert result["formVersion"] == "ci-v1"
    assert result["validationStatus"] == "NOT_REVIEWED"
    assert datetime.fromisoformat(result["recordedAt"]).tzinfo is not None
    assert "answers" not in first.text and "optionKey" not in first.text
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
    assert r.headers.get("cache-control") == "no-store, private"
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



def test_07_synthetic_riasec_catalog_install_keeps_work_values_intact(
    api, isolated_postgres,
):
    """Preview a *future* additive 60-item catalog install in disposable PostgreSQL.

    No O*NET question text, translation, release, or live Neon migration.
    The production API's pilot allowlist MUST still reject the second form.
    """
    from webapp.riasec_scoring import RIASEC_AREAS, score_short_form

    prior = counts(isolated_postgres)
    assert prior == (15, 295, 379)
    form_id = "CI-RIASEC-CATALOG-ONLY"
    key = "CI_RIASEC_60_SYNTHETIC"
    items = [f"CI_RIASEC_ITEM_{n:02d}" for n in range(60)]
    links = [(item, RIASEC_AREAS[n // 10]) for n, item in enumerate(items)]
    options = {f"OPT_{n}": n for n in range(5)}
    answers = {
        item: f"OPT_{n % 5}"
        for n, item in enumerate(items)
    }
    computed = score_short_form(answers, links, options)
    assert computed == dict.fromkeys(RIASEC_AREAS, 20)
    run_id = uuid.uuid4()

    with psycopg.connect(isolated_postgres) as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO ualp_catalog_forms
                 (form_id,form_key,form_version,locale,status,validation_status,
                  item_count,algorithm_version)
                 VALUES (%s,%s,'synthetic-only','ru','DRAFT','NOT_REVIEWED',60,'RIASEC-SUM-v1')
            """, (form_id, key))
            cur.executemany("""INSERT INTO ualp_catalog_items
                 (item_id,form_id,prompt,display_order,required)
                 VALUES (%s,%s,%s,%s,true)""",
                 [(item, form_id, f"CI synthetic placeholder {n + 1}", n + 1)
                  for n, item in enumerate(items)])
            cur.executemany("""INSERT INTO ualp_catalog_options
                 (form_id,option_key,label,score_value,display_order)
                 VALUES (%s,%s,%s,%s,%s)""",
                 [(form_id, name, f"CI synthetic option {value}", value, value + 1)
                  for name, value in options.items()])
            cur.executemany("""INSERT INTO ualp_catalog_scales
                 (scale_id,form_id,scale_key,label,is_parent)
                 VALUES (%s,%s,%s,%s,true)""",
                 [(f"CI_RIASEC_SCALE_{area}",form_id,area,f"CI synthetic {area}")
                  for area in RIASEC_AREAS])
            cur.executemany("""INSERT INTO ualp_catalog_links
                 (item_id,scale_id,weight,direction)
                 VALUES (%s,%s,1,'POSITIVE')""",
                 [(item, f"CI_RIASEC_SCALE_{area}") for item, area in links])
            cur.executemany("""INSERT INTO ualp_catalog_scoring_rules
                 (form_id,scale_id,method,min_items,algorithm_version,status)
                 VALUES (%s,%s,'SUM',10,'RIASEC-SUM-v1','DRAFT')""",
                 [(form_id, f"CI_RIASEC_SCALE_{area}")
                  for area in RIASEC_AREAS])
            cur.execute("""INSERT INTO ualp_assessment_runs
                 (run_id,request_id,form_id,payload_sha256,consent,status,algorithm_version)
                 VALUES (%s,%s,%s,%s,true,'COMPLETED','RIASEC-SUM-v1')""",
                 (run_id, uuid.uuid4(), form_id, "a" * 64))
            cur.executemany("""INSERT INTO ualp_responses
                 (run_id,item_id,option_key) VALUES (%s,%s,%s)""",
                 [(run_id,item,answer) for item,answer in answers.items()])
            cur.executemany("""INSERT INTO ualp_scale_scores
                 (run_id,scale_id,raw_score,answered_count,algorithm_version)
                 VALUES (%s,%s,%s,10,'RIASEC-SUM-v1')""",
                 [(run_id, f"CI_RIASEC_SCALE_{area}",score)
                  for area, score in computed.items()])

    assert counts(isolated_postgres) == (
        prior[0] + 1, prior[1] + 60, prior[2] + 6
    )
    with psycopg.connect(isolated_postgres) as conn:
        counts_by_form = conn.execute(
            """SELECT f.form_key, COUNT(*) AS complete
               FROM ualp_assessment_runs r
               JOIN ualp_catalog_forms f ON f.form_id = r.form_id
               GROUP BY f.form_key""").fetchall()
        assert dict(counts_by_form) == {
            ENABLED_FORM: 14,
            "CI_PROFILE_EXTRA": 1,
            key: 1,
        }
        independent = conn.execute(
            """SELECT s.scale_key, count(*)::int AS items, sum(o.score_value)
               FROM ualp_responses resp
               JOIN ualp_catalog_items item ON item.item_id = resp.item_id
               JOIN ualp_catalog_options o
                 ON o.form_id = item.form_id AND o.option_key=resp.option_key
               JOIN ualp_catalog_links l ON l.item_id = item.item_id
               JOIN ualp_catalog_scales s ON s.scale_id = l.scale_id
               WHERE resp.run_id=%s
               GROUP BY s.scale_key""", (run_id,)).fetchall()
        assert {x[0]: (x[1],int(x[2])) for x in independent} == {
            area: (10, 20) for area in RIASEC_AREAS
        }
        assert conn.execute(
            "SELECT count(*) FROM ualp_scale_scores WHERE run_id=%s",
            (run_id,),
        ).fetchone()[0] == 6

    profile = api.get("/api/profile", headers=headers())
    assert profile.status_code == 200, profile.text
    by_key = {m["formKey"]: m for m in profile.json()["methods"]}
    assert set(by_key) == {ENABLED_FORM, "CI_PROFILE_EXTRA", key}
    assert by_key[ENABLED_FORM]["completedRuns"] == 14
    assert len(by_key[ENABLED_FORM]["parentScores"]) == 6
    assert by_key[key]["completedRuns"] == 1
    assert len(by_key[key]["parentScores"]) == 6
    assert {s["key"]: int(s["mean"]) for s in by_key[key]["parentScores"]} == computed

    # Even a populated catalog MUST NOT unlock an unreviewed questionnaire.
    assert api.get(f"/api/forms/{key}", headers=headers()).status_code == 404
    submission = {
        "requestId": str(uuid.uuid4()), "formKey": key,
        "consent": True,
        "answers": [
            {"itemId": item,"optionKey":answer}
            for item, answer in answers.items()
        ],
    }
    assert api.post("/api/runs", headers=headers(), json=submission).status_code == 404
    assert counts(isolated_postgres) == (
        prior[0] + 1, prior[1] + 60, prior[2] + 6
    )



def test_08_riasec_complete_http_atomic_idempotency_under_ci_guard(
    api, isolated_postgres, monkeypatch,
):
    """Real HTTP -> PG 18 synthetic RIASEC in strictly gated localhost CI only."""
    from webapp.riasec_scoring import RIASEC_AREAS
    key = "CI_RIASEC_60_SYNTHETIC"
    prior = counts(isolated_postgres)
    assert prior == (16, 355, 385)
    assert api.get(f"/api/forms/{key}", headers=headers()).status_code == 404

    # Only temporary local CI; never set this flag on Vercel, Neon or real users.
    monkeypatch.setenv("UALP_CI_RIASEC_INTEGRATION", "1")
    form = api.get(f"/api/forms/{key}", headers=headers())
    assert form.status_code == 200, form.text
    assert len(form.json()["items"]) == 60
    assert len(form.json()["options"]) == 5
    assert "score_value" not in form.text and "weight" not in form.text

    def answers():
        return [
            {"itemId": f"CI_RIASEC_ITEM_{n:02d}", "optionKey": f"OPT_{n // 10 % 5}"}
            for n in range(60)
        ]

    request = {
        "requestId": str(uuid.uuid4()),
        "formKey": key,
        "consent": True,
        "answers": answers(),
    }
    saved = api.post("/api/runs", headers=headers(), json=request)
    assert saved.status_code == 201, saved.text
    out = saved.json()
    assert out["status"] == "COMPLETED"
    assert out["formKey"] == key
    assert out["formVersion"] == OWNER_RIASEC_VERSION
    assert out["validationStatus"] == "NOT_REVIEWED"
    assert datetime.fromisoformat(out["recordedAt"]).tzinfo is not None
    assert "answers" not in saved.text and "optionKey" not in saved.text
    assert out["scoringAlgorithmVersion"] == "RIASEC-SUM-v1"
    scores = {s["key"]: int(s["mean"]) for s in out["scores"]}
    assert scores == {"R": 0, "I": 10, "A": 20, "S": 30, "E": 40, "C": 0}
    assert all(s["answered"] == 10 for s in out["scores"])
    assert counts(isolated_postgres) == (17, 415, 391)

    repeat = api.post("/api/runs", headers=headers(), json=request)
    assert repeat.status_code == 201
    assert repeat.json() == out
    assert counts(isolated_postgres) == (17, 415, 391)

    conflicting = dict(request, answers=answers())
    conflicting["answers"][0]["optionKey"] = "OPT_4"
    error = api.post("/api/runs", headers=headers(), json=conflicting)
    assert error.status_code == 409
    assert counts(isolated_postgres) == (17, 415, 391)

    incomplete = dict(request, requestId=str(uuid.uuid4()), answers=answers()[:-1])
    assert api.post("/api/runs", headers=headers(), json=incomplete).status_code == 422
    unknown = dict(request, requestId=str(uuid.uuid4()), answers=answers())
    unknown["answers"][0]["optionKey"] = "NO_SUCH_OPTION"
    assert api.post("/api/runs", headers=headers(), json=unknown).status_code == 422
    assert counts(isolated_postgres) == (17, 415, 391)

    with psycopg.connect(isolated_postgres) as conn:
        recomputed = conn.execute(
            """SELECT s.scale_key, count(*)::int,
                      sum(o.score_value)
               FROM ualp_responses r
               JOIN ualp_catalog_items i ON i.item_id=r.item_id
               JOIN ualp_catalog_options o ON o.form_id=i.form_id
                  AND o.option_key=r.option_key
               JOIN ualp_catalog_links l ON l.item_id=r.item_id
               JOIN ualp_catalog_scales s ON s.scale_id=l.scale_id
               WHERE r.run_id=%s GROUP BY s.scale_key""",
            (uuid.UUID(out["runId"]),),
        ).fetchall()
    assert {k:(cnt,int(total)) for k,cnt,total in recomputed} == {
        k: (10,v) for k,v in scores.items()
    }

    profile = api.get("/api/profile", headers=headers())
    assert profile.status_code == 200
    by_form = {m["formKey"]:m for m in profile.json()["methods"]}
    assert by_form[key]["completedRuns"] == 2
    assert by_form[key]["latestRunId"] == out["runId"]
    assert len(by_form[key]["parentScores"]) == len(RIASEC_AREAS)
    assert len(by_form[ENABLED_FORM]["parentScores"]) == 6
    assert by_form[ENABLED_FORM]["completedRuns"] == 14
    assert api.get("/api/history", headers=headers()).status_code == 200

    # Same-request concurrent writes serialize on PostgreSQL's UNIQUE index.
    simultaneous_request = dict(request, requestId=str(uuid.uuid4()))
    def send(_):
        with TestClient(app) as client:
            response = client.post("/api/runs", headers=headers(), json=simultaneous_request)
            return response.status_code, response.json()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        twins = list(pool.map(send, [0,1]))
    assert [x[0] for x in twins] == [201,201], twins
    assert twins[0][1] == twins[1][1]
    assert counts(isolated_postgres) == (18, 475, 397)

    monkeypatch.delenv("UALP_CI_RIASEC_INTEGRATION")
    assert api.get(f"/api/forms/{key}", headers=headers()).status_code == 404
    assert api.post("/api/runs", headers=headers(), json=dict(
        simultaneous_request, requestId=str(uuid.uuid4()))).status_code == 404
    assert counts(isolated_postgres) == (18, 475, 397)



def test_09_unused_catalog_guarded_rollback_in_ephemeral_postgres(
    api, isolated_postgres,
):
    """Rehearse *unused* RIASEC catalog-only rollback, never delete a real run.

    CI-local PostgreSQL only. All new IDs are unique synthetic placeholders.
    The real owner's Neon backups, rows and catalog are never touched here.
    """
    from webapp.riasec_scoring import RIASEC_AREAS
    old_runs = counts(isolated_postgres)
    assert old_runs == (18, 475, 397)
    form_id, form_key = "CI_ROLLBACK_FORM_60", "CI_ROLLBACK_RIASEC_60"
    item_ids = [f"CI_ROLLBACK_ITEM_{i:02d}" for i in range(60)]
    scale_ids = [f"CI_ROLLBACK_SCALE_{area}" for area in RIASEC_AREAS]
    with psycopg.connect(isolated_postgres) as conn:
        old_catalog = tuple(conn.execute(
            """SELECT
               (SELECT count(*) FROM ualp_catalog_forms),
               (SELECT count(*) FROM ualp_catalog_items),
               (SELECT count(*) FROM ualp_catalog_options),
               (SELECT count(*) FROM ualp_catalog_scales),
               (SELECT count(*) FROM ualp_catalog_links),
               (SELECT count(*) FROM ualp_catalog_scoring_rules)"""
        ).fetchone())
        # Existing old user Work Values data is also preserved by the rollback.
        old_work_values = tuple(conn.execute(
            """SELECT count(*),
               (SELECT count(*) FROM ualp_responses
                 WHERE run_id IN (
                   SELECT run_id FROM ualp_assessment_runs
                   WHERE form_id=%s)),
               (SELECT count(*) FROM ualp_scale_scores
                 WHERE run_id IN (
                   SELECT run_id FROM ualp_assessment_runs
                   WHERE form_id=%s))
               FROM ualp_assessment_runs WHERE form_id=%s""",
            (FORM, FORM, FORM),
        ).fetchone())
        assert old_work_values[0] == 14
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO ualp_catalog_forms
                (form_id,form_key,form_version,locale,status,validation_status,
                 item_count,algorithm_version)
                VALUES (%s,%s,'CI-ROLLBACK-only','ru','DRAFT',
                        'NOT_REVIEWED',60,'RIASEC-SUM-v1')""",
                (form_id, form_key))
            cur.executemany("""INSERT INTO ualp_catalog_items
                (item_id,form_id,prompt,display_order,required)
                VALUES (%s,%s,%s,%s,true)""",
                [(item, form_id, f"Synthetic rollback placeholder {i+1}", i+1)
                 for i,item in enumerate(item_ids)])
            cur.executemany("""INSERT INTO ualp_catalog_options
                (form_id,option_key,label,score_value,display_order)
                VALUES (%s,%s,%s,%s,%s)""",
                [(form_id, f"CI_OPT_{i}", f"Dummy {i}", i, i+1)
                 for i in range(5)])
            cur.executemany("""INSERT INTO ualp_catalog_scales
                (scale_id,form_id,scale_key,label,is_parent)
                VALUES (%s,%s,%s,%s,true)""",
                [(sid,form_id,area,f"Dummy scale {area}")
                 for area,sid in zip(RIASEC_AREAS, scale_ids)])
            cur.executemany("""INSERT INTO ualp_catalog_links
                (item_id,scale_id,weight,direction)
                VALUES (%s,%s,1,'POSITIVE')""",
                [(item, scale_ids[i // 10]) for i,item in enumerate(item_ids)])
            cur.executemany("""INSERT INTO ualp_catalog_scoring_rules
                (form_id,scale_id,method,min_items,algorithm_version,status)
                VALUES (%s,%s,'SUM',10,'RIASEC-SUM-v1','DRAFT')""",
                [(form_id,scale_id) for scale_id in scale_ids])
            assert conn.execute(
                "SELECT count(*) FROM ualp_catalog_items WHERE form_id=%s",
                (form_id,),
            ).fetchone()[0] == 60
            # A rollback is allowed only when no live user run references this form.
            assert conn.execute(
                "SELECT count(*) FROM ualp_assessment_runs WHERE form_id=%s",
                (form_id,),
            ).fetchone()[0] == 0
            cur.execute("DELETE FROM ualp_catalog_scoring_rules WHERE form_id=%s",
                        (form_id,))
            assert cur.rowcount == 6
            cur.execute("""DELETE FROM ualp_catalog_links WHERE item_id IN
                           (SELECT item_id FROM ualp_catalog_items WHERE form_id=%s)""",
                        (form_id,))
            assert cur.rowcount == 60
            cur.execute("DELETE FROM ualp_catalog_options WHERE form_id=%s",
                        (form_id,))
            assert cur.rowcount == 5
            cur.execute("DELETE FROM ualp_catalog_items WHERE form_id=%s",
                        (form_id,))
            assert cur.rowcount == 60
            cur.execute("DELETE FROM ualp_catalog_scales WHERE form_id=%s",
                        (form_id,))
            assert cur.rowcount == 6
            cur.execute("DELETE FROM ualp_catalog_forms WHERE form_id=%s",
                        (form_id,))
            assert cur.rowcount == 1
        new_catalog = tuple(conn.execute(
            """SELECT
               (SELECT count(*) FROM ualp_catalog_forms),
               (SELECT count(*) FROM ualp_catalog_items),
               (SELECT count(*) FROM ualp_catalog_options),
               (SELECT count(*) FROM ualp_catalog_scales),
               (SELECT count(*) FROM ualp_catalog_links),
               (SELECT count(*) FROM ualp_catalog_scoring_rules)"""
        ).fetchone())
        assert new_catalog == old_catalog
        new_work_values = tuple(conn.execute(
            """SELECT count(*),
               (SELECT count(*) FROM ualp_responses
                 WHERE run_id IN (
                   SELECT run_id FROM ualp_assessment_runs
                   WHERE form_id=%s)),
               (SELECT count(*) FROM ualp_scale_scores
                 WHERE run_id IN (
                   SELECT run_id FROM ualp_assessment_runs
                   WHERE form_id=%s))
               FROM ualp_assessment_runs WHERE form_id=%s""",
            (FORM, FORM, FORM),
        ).fetchone())
        assert new_work_values == old_work_values
    assert counts(isolated_postgres) == old_runs



def test_10_private_source_locked_riasec_http_in_ephemeral_ci(
    api, isolated_postgres, monkeypatch,
):
    """Synthetic source-locked private RIASEC; no O*NET text or remote Neon writes."""
    from webapp import main as server
    from webapp.riasec_manifest import (
        DRAFT_STATUS, PRIVATE_SCOPE, LICENSE_URL, SCHEMA_VERSION,
        validate_private_manifest,
    )
    from webapp.riasec_scoring import RIASEC_AREAS

    assert counts(isolated_postgres) == (18, 475, 397)
    real_key = server.OWNER_RIASEC_FORM
    assert real_key == "ONET_SHORT_60_DIGITAL"
    # The production guard MUST reject the local CI DB even when the form exists.
    with psycopg.connect(isolated_postgres) as check:
        assert not server._owner_riasec_allowed(check, real_key)

    items = [f"CI_PERSONAL_SOURCE_{i:02d}" for i in range(60)]
    scales = [f"SCALE-{i+1:06d}" for i in range(6)]
    choices = [f"CI_PERSONAL_OPT_{i}" for i in range(5)]
    synthetic_manifest = {
        "schemaVersion": SCHEMA_VERSION,
        "formKey": real_key,
        "formVersion": server.OWNER_RIASEC_VERSION,
        "sourceFormId": "FORM-000001",
        "locale": "ru",
        "purpose": "VOLUNTARY_SELF_EXPLORATION",
        "distributionScope": PRIVATE_SCOPE,
        "validationStatus": DRAFT_STATUS,
        "algorithmVersion": "RIASEC-SUM-v1",
        "licenseUrl": LICENSE_URL,
        "items": [
            {"itemId": item, "sourceIndex": i+1,
             "prompt": f"Синтетическая задача для CI {i+1}",
             "scaleKey": RIASEC_AREAS[i // 10],
             "reviewStatus": DRAFT_STATUS}
            for i,item in enumerate(items)
        ],
        "options": [
            {"optionKey": choice,"label":f"Синтетический выбор {i}",
             "scoreValue": i, "reviewStatus": DRAFT_STATUS}
            for i,choice in enumerate(choices)
        ],
        "scales": [
            {"scaleKey": area, "label": f"Синтетическая шкала {area}"}
            for area in RIASEC_AREAS
        ],
    }
    receipt = validate_private_manifest(synthetic_manifest)
    with psycopg.connect(isolated_postgres) as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO ualp_catalog_forms
                (form_id,form_key,form_version,locale,status,validation_status,
                 item_count,algorithm_version)
                VALUES (%s,%s,%s,'ru','DRAFT','NOT_REVIEWED',60,'RIASEC-SUM-v1')""",
                ("FORM-000001", real_key, server.OWNER_RIASEC_VERSION))
            cur.executemany("""INSERT INTO ualp_catalog_items
                (item_id,form_id,prompt,display_order,required)
                VALUES (%s,'FORM-000001',%s,%s,true)""",
                [(item,synthetic_manifest["items"][i]["prompt"],i+1)
                 for i,item in enumerate(items)])
            cur.executemany("""INSERT INTO ualp_catalog_options
                (form_id,option_key,label,score_value,display_order)
                VALUES ('FORM-000001',%s,%s,%s,%s)""",
                [(choice, synthetic_manifest["options"][i]["label"],i,i+1)
                 for i,choice in enumerate(choices)])
            cur.executemany("""INSERT INTO ualp_catalog_scales
                (scale_id,form_id,scale_key,label,is_parent)
                VALUES (%s,'FORM-000001',%s,%s,true)""",
                [(sid,area,synthetic_manifest["scales"][i]["label"])
                 for i,(sid,area) in enumerate(zip(scales,RIASEC_AREAS))])
            cur.executemany("""INSERT INTO ualp_catalog_links
                (item_id,scale_id,weight,direction)
                VALUES (%s,%s,1,'POSITIVE')""",
                [(item, scales[i // 10]) for i,item in enumerate(items)])
            cur.executemany("""INSERT INTO ualp_catalog_scoring_rules
                (form_id,scale_id,method,min_items,algorithm_version,status)
                VALUES ('FORM-000001',%s,'SUM',10,'RIASEC-SUM-v1','DRAFT')""",
                [(sid,) for sid in scales])

    # Explicitly blocked until owner-only server gate and exact source lock agree.
    assert api.get("/api/forms/"+real_key, headers=headers()).status_code == 404
    monkeypatch.setattr(server, "OWNER_RIASEC_SHA256", "0"*64)
    monkeypatch.setattr(server, "_owner_riasec_allowed",
                        lambda conn, key: key == real_key)
    assert api.get("/api/forms/"+real_key, headers=headers()).status_code == 503
    monkeypatch.setattr(server, "OWNER_RIASEC_SHA256",
                        receipt.source_digest_sha256)
    response = api.get("/api/forms/"+real_key, headers=headers())
    assert response.status_code == 200, response.text
    assert len(response.json()["items"]) == 60
    assert len(response.json()["options"]) == 5
    assert response.json()["validationStatus"] == "NOT_REVIEWED"
    assert response.json()["sourceLicense"] == LICENSE_URL
    for hidden in ("score_value", "weight", "payload_sha256", "isCorrect"):
        assert hidden not in response.text
    assert api.get("/api/forms/"+real_key).status_code == 401

    request = {
        "requestId": str(uuid.uuid4()),
        "formKey": real_key, "consent": True,
        "answers": [
            {"itemId": item, "optionKey": choices[(i // 10) % 5]}
            for i,item in enumerate(items)
        ],
    }
    saved = api.post("/api/runs",json=request,headers=headers())
    assert saved.status_code == 201, saved.text
    out = saved.json()
    assert out["scoringAlgorithmVersion"] == "RIASEC-SUM-v1"
    assert {x["key"]:int(x["mean"]) for x in out["scores"]} == {
        "R":0, "I":10, "A":20, "S":30, "E":40, "C":0
    }
    assert counts(isolated_postgres) == (19, 535, 403)
    retry = api.post("/api/runs",json=request,headers=headers())
    assert retry.status_code == 201 and retry.json() == out
    assert counts(isolated_postgres) == (19, 535, 403)
    altered = dict(request, answers=[dict(v) for v in request["answers"]])
    altered["answers"][0]["optionKey"] = choices[4]
    assert api.post("/api/runs",json=altered,headers=headers()).status_code == 409
    assert counts(isolated_postgres) == (19, 535, 403)

    profile = api.get("/api/profile",headers=headers())
    assert profile.status_code == 200
    grouped = {x["formKey"]:x for x in profile.json()["methods"]}
    assert grouped[real_key]["completedRuns"] == 1
    assert len(grouped[real_key]["parentScores"]) == 6
    assert grouped[ENABLED_FORM]["completedRuns"] == 14
    assert api.get("/api/runs/"+out["runId"],headers=headers()).status_code == 200

    # History crosses existing real-form keys, not unrelated synthetic catalog rows.
    before_history = counts(isolated_postgres)
    assert api.get("/api/history", params={"formKey": "CI_PROFILE_EXTRA"},
                   headers=headers()).status_code == 422
    assert api.get("/api/history", params={"formKey": "ICAR16_DIGITAL"},
                   headers=headers()).status_code == 422
    assert api.get("/api/history", params={"formKey": "ALL"}).status_code == 401
    riasec_history = api.get("/api/history", params={"formKey": real_key},
                             headers=headers())
    assert riasec_history.status_code == 200
    assert riasec_history.json()["formKeyFilter"] == real_key
    assert [x["runId"] for x in riasec_history.json()["items"]] == [out["runId"]]
    assert all(x["formKey"] == real_key for x in riasec_history.json()["items"])
    default_history = api.get("/api/history", headers=headers())
    assert default_history.status_code == 200
    assert default_history.json()["formKeyFilter"] == ENABLED_FORM
    assert all(x["formKey"] == ENABLED_FORM for x in default_history.json()["items"])
    combined_1 = api.get("/api/history", params={"formKey": "ALL"},
                         headers=headers())
    assert combined_1.status_code == 200, combined_1.text
    assert len(combined_1.json()["items"]) == 10
    assert combined_1.json()["nextCursor"]
    combined_2 = api.get("/api/history", params={
        "formKey": "ALL", "cursor": combined_1.json()["nextCursor"],
    }, headers=headers())
    assert combined_2.status_code == 200, combined_2.text
    combined_entries = combined_1.json()["items"] + combined_2.json()["items"]
    assert len(combined_entries) == 15
    assert len({x["runId"] for x in combined_entries}) == 15
    assert {x["formKey"] for x in combined_entries} == {real_key, ENABLED_FORM}
    assert out["runId"] in {x["runId"] for x in combined_entries}
    assert combined_2.json()["nextCursor"] is None
    for response in (riasec_history, default_history, combined_1, combined_2):
        for secret_field in ("answers", "optionKey", "payload_sha256", "raw_score"):
            assert secret_field not in response.text
    assert counts(isolated_postgres) == before_history

    # Disabling private gate affects new reads and writes, not saved Work Values.
    monkeypatch.setattr(server, "_owner_riasec_allowed",
                        lambda conn, key: False)
    assert api.get("/api/forms/"+real_key, headers=headers()).status_code == 404
    request["requestId"] = str(uuid.uuid4())
    assert api.post("/api/runs", json=request, headers=headers()).status_code == 404
    assert api.get("/api/forms/"+ENABLED_FORM, headers=headers()).status_code == 200
    assert counts(isolated_postgres) == (19, 535, 403)



def test_11_cookie_session_reads_and_saves_without_access_key(api, isolated_postgres):
    """Real SQL save/retry/reopen/profile through the browser session boundary."""
    origin = 'https://testserver'
    browser_headers = {'X-UALP-Request': '1', 'Origin': origin}
    before = counts(isolated_postgres)
    with TestClient(app, base_url=origin) as browser:
        login = browser.post('/api/session', json={'remember': True},
                             headers={**headers(), **browser_headers})
        assert login.status_code == 200, login.text
        assert browser.get('/api/session').status_code == 200
        assert browser.get(f'/api/forms/{ENABLED_FORM}').status_code == 200
        request = payload()
        assert browser.post('/api/runs', json=request).status_code == 403
        assert counts(isolated_postgres) == before
        saved = browser.post('/api/runs', json=request, headers=browser_headers)
        assert saved.status_code == 201, saved.text
        run_id = saved.json()['runId']
        again = browser.post('/api/runs', json=request, headers=browser_headers)
        assert again.json()['runId'] == run_id
        assert counts(isolated_postgres) == (before[0]+1, before[1]+21, before[2]+27)
        assert browser.get('/api/runs/'+run_id).status_code == 200
        assert browser.get('/api/history').status_code == 200
        assert browser.get('/api/profile').status_code == 200
        assert browser.delete('/api/session', headers=browser_headers).status_code == 200
        assert browser.get('/api/profile').status_code == 401
        assert counts(isolated_postgres) == (before[0]+1, before[1]+21, before[2]+27)
