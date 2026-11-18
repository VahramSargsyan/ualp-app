# main.py | UALP 0.5.0-raw-score-trends-test
"""UALP PostgreSQL-only private assessment TEST (no Sheets or Apps Script)."""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, Response, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from webapp.riasec_scoring import RIASECContractError, score_catalog_short_form
from webapp.riasec_manifest import (
    LICENSE_URL, ManifestError, verify_private_postgres_catalog,
)

from webapp.owner_session import COOKIE_NAME, SESSION_SECONDS, issue_session, valid_session

APP_VERSION = "0.5.1-career-kb-readonly-test"
ENABLED_FORM = "UALP_WV21_RU_LIKERT"
CI_SYNTHETIC_FORM = "CI_RIASEC_60_SYNTHETIC"
OWNER_RIASEC_FORM = "ONET_SHORT_60_DIGITAL"
OWNER_RIASEC_VERSION = "RU-v0.2-editorial-DRAFT-20261116"
OWNER_RIASEC_SHA256 = "9d54adb24827f3902ba91858e711e92d343488b1863d22a695847dbdd47197be"
ROOT = Path(__file__).resolve().parent

app = FastAPI(
    title="UALP — Private PostgreSQL TEST", version=APP_VERSION,
    docs_url=None, redoc_url=None, openapi_url=None,
)

@app.middleware("http")
async def private_api_responses(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store, private"
    return response


def secure_config() -> tuple[str, str]:
    if os.getenv("UALP_ENV", "") != "TEST":
        raise HTTPException(503, "UALP_TEST_ONLY: deployment must be TEST")
    url = os.getenv("DATABASE_URL", "")
    secret = os.getenv("UALP_ACCESS_KEY", "")
    if not url.startswith(("postgresql://", "postgres://")) or len(secret) < 32:
        raise HTTPException(503, "UALP_CONFIG_MISSING: TEST setup required")
    return url, secret

def browser_mutation(request: Request) -> None:
    # A custom header is required even when Origin is absent. No CORS is enabled.
    # Cross-origin pages cannot send it without an approved preflight.
    if request.headers.get("x-ualp-request") != "1":
        raise HTTPException(403, "Same-origin request required")
    if request.headers.get("sec-fetch-site") not in (None, "same-origin"):
        raise HTTPException(403, "Cross-origin request denied")
    origin = request.headers.get("origin")
    if origin and origin != str(request.base_url).rstrip("/"):
        raise HTTPException(403, "Cross-origin request denied")


def authorized(x_ualp_access_key: str | None = Header(default=None),
               request: Request = None) -> str:
    url, key = secure_config()
    # Preserve existing explicit-header clients and CI; never fall back from a bad key.
    if isinstance(x_ualp_access_key, str):
        if secrets.compare_digest(x_ualp_access_key, key):
            return url
        raise HTTPException(401, "Access denied")
    if request is not None and valid_session(
        request.cookies.get(COOKIE_NAME, ""), key, request.url.netloc
    ):
        if request.method not in ("GET", "HEAD", "OPTIONS"):
            browser_mutation(request)
        return url
    raise HTTPException(401, "Access denied")


class SessionLogin(BaseModel):
    remember: bool = False


@app.post("/api/session")
def login(data: SessionLogin, request: Request, response: Response,
          x_ualp_access_key: str | None = Header(default=None)):
    browser_mutation(request)
    _, key = secure_config()
    if not x_ualp_access_key or not secrets.compare_digest(x_ualp_access_key, key):
        raise HTTPException(401, "Access denied")
    response.set_cookie(
        COOKIE_NAME, issue_session(key, request.url.netloc),
        max_age=SESSION_SECONDS if data.remember else None,
        secure=True, httponly=True, samesite="strict", path="/",
    )
    response.headers["Cache-Control"] = "no-store, private"
    return {"authenticated": True, "remembered": data.remember}


@app.get("/api/session")
def session_status(response: Response, url: str = Depends(authorized)):
    response.headers["Cache-Control"] = "no-store, private"
    return {"authenticated": True}


@app.delete("/api/session")
def logout(request: Request, response: Response):
    # Permit clearing an expired cookie without a functioning DB or access key.
    browser_mutation(request)
    response.delete_cookie(COOKIE_NAME, path="/", secure=True,
                           httponly=True, samesite="strict")
    response.headers["Cache-Control"] = "no-store, private"
    return {"authenticated": False}


def connect(url: str):
    return psycopg.connect(url, row_factory=dict_row, connect_timeout=10)

class Answer(BaseModel):
    itemId: str = Field(min_length=1, max_length=80)
    optionKey: str = Field(min_length=1, max_length=80)

class Submission(BaseModel):
    requestId: uuid.UUID
    formKey: str
    consent: bool
    answers: list[Answer] = Field(min_length=1, max_length=100)

@app.get("/")
def home():
    return FileResponse(ROOT / "index.html")

@app.get("/health")
def health():
    return {"status": "TEST_ONLY", "version": APP_VERSION, "database": "PostgreSQL"}

def _ci_synthetic_riasec_allowed(conn, key: str) -> bool:
    """P0 firewall: synthetic RIASEC can run ONLY against disposable localhost CI.

    Cannot unlock the owner's Neon or Vercel database from environment alone.
    """
    return (
        key == CI_SYNTHETIC_FORM
        and os.getenv("UALP_ENV") == "TEST"
        and os.getenv("UALP_CI_MODE") == "EPHEMERAL_POSTGRES"
        and os.getenv("UALP_CI_RIASEC_INTEGRATION") == "1"
        and conn.info.host in ("127.0.0.1", "localhost")
        and conn.info.dbname == "ualp_ci"
        and conn.info.user == "postgres"
    )


def _owner_riasec_allowed(conn, key: str) -> bool:
    """Owner-only experimental TEST on the exact separate Neon TEST database."""
    host = conn.info.host or ""
    return (
        key == OWNER_RIASEC_FORM
        and os.getenv("UALP_ENV") == "TEST"
        and conn.info.dbname == "ualp_test"
        and host.endswith(".neon.tech")
    )


def _verify_owner_riasec_catalog(conn, form_row, items) -> None:
    """Reconstruct private source-lock from DB, fail closed if any text drifts."""
    if (
        form_row["form_id"] != "FORM-000001"
        or form_row["form_version"] != OWNER_RIASEC_VERSION
        or form_row["locale"] != "ru"
        or form_row["algorithm_version"] != "RIASEC-SUM-v1"
        or form_row["validation_status"] != "NOT_REVIEWED"
    ):
        raise HTTPException(503, "Private RIASEC catalog version mismatch")
    scales = conn.execute(
        """SELECT scale_id,scale_key,label,is_parent FROM ualp_catalog_scales
           WHERE form_id=%s ORDER BY scale_id""", (form_row["form_id"],)
    ).fetchall()
    links = conn.execute(
        """SELECT l.item_id,s.scale_key,l.weight,l.direction
           FROM ualp_catalog_links l JOIN ualp_catalog_scales s
             ON s.scale_id=l.scale_id WHERE s.form_id=%s""",
        (form_row["form_id"],),
    ).fetchall()
    option_rows = conn.execute(
        """SELECT option_key,label,score_value FROM ualp_catalog_options
           WHERE form_id=%s ORDER BY display_order""", (form_row["form_id"],)
    ).fetchall()
    rules = conn.execute(
        """SELECT scale_id,method,min_items,algorithm_version,status
           FROM ualp_catalog_scoring_rules WHERE form_id=%s""",
        (form_row["form_id"],),
    ).fetchall()
    if (len(links) != 60 or len(rules) != 6
            or len(scales) != 6 or len(option_rows) != 5
            or any(x["direction"] != "POSITIVE" or x["weight"] != 1
                   for x in links)
            or any(x["is_parent"] is not True for x in scales)
            or {x["scale_id"] for x in rules} != {x["scale_id"] for x in scales}
            or any(x["score_value"] != int(x["score_value"]) for x in option_rows)
            or any(x["method"] != "SUM" or x["min_items"] != 10
                   or x["algorithm_version"] != "RIASEC-SUM-v1"
                   or x["status"] != "DRAFT" for x in rules)):
        raise HTTPException(503, "Private RIASEC catalog relationships invalid")
    mapping = {x["item_id"]: x["scale_key"] for x in links}
    if len(mapping) != 60:
        raise HTTPException(503, "Private RIASEC link identities invalid")
    try:
        receipt = verify_private_postgres_catalog(
            form_row, items, option_rows, scales, mapping, OWNER_RIASEC_SHA256
        )
    except (ManifestError, KeyError, ValueError, TypeError, ArithmeticError):
        raise HTTPException(503, "Private RIASEC source-lock mismatch") from None
    if receipt.eligible_for_public_release:
        raise HTTPException(503, "RIASEC release status invalid")


def fetch_form(conn, key: str):
    form = conn.execute(
        """SELECT form_id,form_key,form_version,locale,status,item_count,
                  algorithm_version,validation_status
           FROM ualp_catalog_forms WHERE form_key = %s""", (key,)
    ).fetchone()
    if not form or (key != ENABLED_FORM and not _ci_synthetic_riasec_allowed(conn, key)
                    and not _owner_riasec_allowed(conn, key)) or form["status"] != "DRAFT":
        raise HTTPException(404, "Pilot form not available")
    items = conn.execute(
        """SELECT item_id,prompt,display_order,required FROM ualp_catalog_items
           WHERE form_id=%s ORDER BY display_order""", (form["form_id"],)
    ).fetchall()
    options = conn.execute(
        """SELECT option_key,label FROM ualp_catalog_options
           WHERE form_id=%s ORDER BY display_order""", (form["form_id"],)
    ).fetchall()
    item_count = 60 if key in (CI_SYNTHETIC_FORM, OWNER_RIASEC_FORM) else 21
    if (form["item_count"] != item_count or len(items) != item_count or len(options) != 5
            or len({x["item_id"] for x in items}) != item_count
            or (key == CI_SYNTHETIC_FORM and
                (form["algorithm_version"] != "RIASEC-SUM-v1" or
                 form["validation_status"] != "NOT_REVIEWED" or
                 form["form_version"] != "synthetic-only"))):
        raise HTTPException(503, "Pilot form catalog incomplete")
    if key == OWNER_RIASEC_FORM:
        _verify_owner_riasec_catalog(conn, form, items)
    return form, items, options

@app.get("/api/catalog")
def catalog(url: str = Depends(authorized)):
    with connect(url) as conn:
        keys = [ENABLED_FORM]
        if _owner_riasec_allowed(conn, OWNER_RIASEC_FORM):
            keys.append(OWNER_RIASEC_FORM)
        rows = conn.execute(
            """SELECT form_key,form_version,validation_status,status,item_count
               FROM ualp_catalog_forms WHERE form_key=ANY(%s) ORDER BY form_key""",
            (keys,)
        ).fetchall()
    return {"version": APP_VERSION, "forms": rows,
            "notice": "Черновой исследовательский тест. Не использовать для найма."}

@app.get("/api/forms/{form_key}")
def form(form_key: str, url: str = Depends(authorized)):
    with connect(url) as conn:
        f, items, options = fetch_form(conn, form_key)
    # Strict allowlist: score values, rule weights and answer keys never enter this payload.
    return {
        "formKey": f["form_key"], "formVersion": f["form_version"],
        "locale": f["locale"], "validationStatus": f["validation_status"],
        "pilotOnly": True,
        "sourceAttribution": (
            "O*NET Interest Profiler, USDOL/ETA; русский экспериментальный перевод "
            "не валидирован. O*NET не одобряет UALP."
            if form_key == OWNER_RIASEC_FORM else None
        ),
        "sourceLicense": LICENSE_URL if form_key == OWNER_RIASEC_FORM else None,
        "items": [{"itemId": x["item_id"], "prompt": x["prompt"],
                   "position": x["display_order"], "required": x["required"]}
                  for x in items],
        "options": [{"optionKey": x["option_key"], "label": x["label"]} for x in options],
    }

def compute_scores(answer_map: dict, option_scores: dict, links: list, rules: list):
    """Only approved experimental 0–4 option weights, POSITIVE links and MEAN."""
    gathered = defaultdict(list)
    for link in links:
        if link["item_id"] not in answer_map:
            continue
        if link["direction"] != "POSITIVE" or float(link["weight"]) != 1:
            raise ValueError("Unapproved link direction or weight")
        value = option_scores.get(answer_map[link["item_id"]])
        if value is None or float(value) < 0 or float(value) > 4:
            raise ValueError("Invalid source option score")
        gathered[link["scale_id"]].append(float(value))
    if len(rules) != 27 or len(links) != 42:
        raise ValueError("Pilot scale/link count changed")
    result = []
    for rule in rules:
        values = gathered[rule["scale_id"]]
        if (rule["method"] != "MEAN"
                or rule["algorithm_version"] != "WORKVALUES-MEAN-v1"
                or rule["status"] != "DRAFT"
                or len(values) != rule["min_items"]):
            raise ValueError("Incomplete or altered source scale rule")
        result.append({
            "scaleId": rule["scale_id"], "mean": round(sum(values) / len(values), 4),
            "answered": len(values), "algorithmVersion": rule["algorithm_version"],
        })
    if len({r["scaleId"] for r in result}) != len(result):
        raise ValueError("Duplicate source scale")
    return result

def stored_result(conn, run_id: str):
    run = conn.execute(
        """SELECT r.run_id,r.form_id,r.algorithm_version,r.status,r.created_at,
                  f.form_key,f.form_version,f.validation_status
           FROM ualp_assessment_runs AS r
           JOIN ualp_catalog_forms AS f ON f.form_id=r.form_id
           WHERE r.run_id=%s""", (run_id,)
    ).fetchone()
    if not run:
        raise HTTPException(404, "Run not found")
    scores = conn.execute(
        """SELECT s.scale_id,c.scale_key,c.label,s.raw_score,s.answered_count
           FROM ualp_scale_scores AS s JOIN ualp_catalog_scales AS c
             ON c.scale_id=s.scale_id
           WHERE s.run_id=%s AND c.is_parent=true
           ORDER BY s.raw_score DESC,c.scale_key""", (run_id,)
    ).fetchall()
    return {
        "runId": str(run["run_id"]), "status": run["status"],
        "formKey": run["form_key"], "formVersion": run["form_version"],
        "validationStatus": run["validation_status"],
        "recordedAt": run["created_at"].isoformat(),
        "scoringAlgorithmVersion": run["algorithm_version"],
        "scores": [{"scaleId": s["scale_id"], "key": s["scale_key"],
                    "label": s["label"], "mean": s["raw_score"],
                    "answered": s["answered_count"]} for s in scores],
        "notice": ("Суммы интересов 0–40; русский перевод экспериментальный, не валидирован."
                   if run["form_id"] == "FORM-000001"
                   else "Сырые суммы 0–40 для синтетического CI, без интерпретации."
                   if run["algorithm_version"] == "RIASEC-SUM-v1"
                   else "Сырые оценки 0–4, только исследовательский TEST. Без норм и прогнозов профессий."),
    }

@app.post("/api/runs", status_code=status.HTTP_201_CREATED)
def submit(data: Submission, url: str = Depends(authorized)):
    if data.formKey not in (ENABLED_FORM, CI_SYNTHETIC_FORM, OWNER_RIASEC_FORM):
        raise HTTPException(404, "Form unavailable")
    if data.consent is not True:
        raise HTTPException(422, "Explicit pilot consent required")
    answer_map = {a.itemId: a.optionKey for a in data.answers}
    if len(answer_map) != len(data.answers):
        raise HTTPException(422, "Duplicate item IDs")
    digest = hashlib.sha256(json.dumps(
        sorted(answer_map.items()), ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    request_id = data.requestId
    with connect(url) as conn:
        if (data.formKey == CI_SYNTHETIC_FORM and not _ci_synthetic_riasec_allowed(conn, data.formKey)
                or data.formKey == OWNER_RIASEC_FORM and not _owner_riasec_allowed(conn, data.formKey)):
            raise HTTPException(404, "Form unavailable")
        old = conn.execute(
            """SELECT run_id,form_id,payload_sha256 FROM ualp_assessment_runs
               WHERE request_id=%s""", (request_id,)
        ).fetchone()
        if old:
            if old["payload_sha256"] != digest:
                raise HTTPException(409, "Retry payload mismatch")
            source = conn.execute(
                "SELECT form_key FROM ualp_catalog_forms WHERE form_id=%s",
                (old["form_id"],)
            ).fetchone()
            if not source or source["form_key"] != data.formKey:
                raise HTTPException(409, "Retry form mismatch")
            return stored_result(conn, old["run_id"])
        form_row, items, _ = fetch_form(conn, data.formKey)
        required = {x["item_id"] for x in items}
        if set(answer_map) != required:
            raise HTTPException(422, "All required form items must be answered exactly once")
        scored_options = conn.execute(
            """SELECT option_key,score_value FROM ualp_catalog_options
               WHERE form_id=%s""", (form_row["form_id"],)
        ).fetchall()
        option_map = {x["option_key"]: x["score_value"] for x in scored_options}
        if len(option_map) != 5 or any(v not in option_map for v in answer_map.values()):
            raise HTTPException(422, "Unknown answer option")
        links = conn.execute(
            """SELECT l.item_id,l.scale_id,l.weight,l.direction
               FROM ualp_catalog_links AS l
               JOIN ualp_catalog_items AS i ON l.item_id=i.item_id
               WHERE i.form_id=%s ORDER BY l.item_id,l.scale_id""", (form_row["form_id"],)
        ).fetchall()
        rules = conn.execute(
            """SELECT scale_id,method,min_items,algorithm_version,status
               FROM ualp_catalog_scoring_rules WHERE form_id=%s ORDER BY scale_id""",
            (form_row["form_id"],)
        ).fetchall()
        try:
            if data.formKey in (CI_SYNTHETIC_FORM, OWNER_RIASEC_FORM):
                scales = conn.execute(
                    """SELECT scale_id,scale_key,is_parent FROM ualp_catalog_scales
                       WHERE form_id=%s ORDER BY scale_key""",
                    (form_row["form_id"],),
                ).fetchall()
                computed = score_catalog_short_form(
                    answer_map, option_map, links, rules, scales
                )
            else:
                computed = compute_scores(answer_map, option_map, links, rules)
        except (ValueError, RIASECContractError):
            raise HTTPException(503, "Pilot scoring catalog has not passed consistency checks")
        run_id = uuid.uuid4()
        try:
            with conn.transaction():
                conn.execute(
                    """INSERT INTO ualp_assessment_runs
                       (run_id,request_id,form_id,payload_sha256,consent,status,algorithm_version)
                       VALUES (%s,%s,%s,%s,true,'COMPLETED',%s)""",
                    (run_id,request_id,form_row["form_id"],digest,form_row["algorithm_version"])
                )
                # Psycopg 3 executemany() is a Cursor method, not a Connection method.
                # Keep both batch inserts inside the existing database transaction.
                with conn.cursor() as cur:
                    cur.executemany(
                        """INSERT INTO ualp_responses(run_id,item_id,option_key)
                           VALUES (%s,%s,%s)""",
                        [(run_id,k,v) for k,v in answer_map.items()]
                    )
                    cur.executemany(
                        """INSERT INTO ualp_scale_scores
                           (run_id,scale_id,raw_score,answered_count,algorithm_version)
                           VALUES (%s,%s,%s,%s,%s)""",
                        [(run_id,x["scaleId"],x["mean"],x["answered"],x["algorithmVersion"])
                         for x in computed]
                    )
        except psycopg.errors.UniqueViolation:
            # Competing same-request writes are serialized by PostgreSQL's UNIQUE index.
            conn.rollback()
            with connect(url) as recovered:
                existing = recovered.execute(
                    "SELECT run_id,payload_sha256,form_id FROM ualp_assessment_runs WHERE request_id=%s",
                    (request_id,)
                ).fetchone()
                if existing and existing["payload_sha256"] == digest \
                        and existing["form_id"] == form_row["form_id"]:
                    return stored_result(recovered, existing["run_id"])
            raise HTTPException(409, "Conflicting concurrent submission")
        return stored_result(conn, run_id)

@app.get("/api/runs/{run_id}")
def result(run_id: uuid.UUID, url: str = Depends(authorized)):
    with connect(url) as conn:
        return stored_result(conn, run_id)


HISTORY_PAGE_SIZE = 10
HISTORY_ALL_FORMS = "ALL"


@app.get("/api/history")
def history(
    response: Response,
    cursor: str | None = Query(default=None, min_length=1, max_length=128),
    form_key: str = Query(default=ENABLED_FORM, alias="formKey", min_length=1, max_length=64),
    url: str = Depends(authorized),
):
    """Read-only owner TEST history across the two approved exploratory forms.

    Default preserves old Work Values-only clients. The explicit ALL filter
    combines only these two owner TEST methods, not arbitrary database forms.
    Keyset pagination stays deterministic across both assessments.
    """
    response.headers["Cache-Control"] = "no-store, private"
    if form_key not in (HISTORY_ALL_FORMS, ENABLED_FORM, OWNER_RIASEC_FORM):
        raise HTTPException(422, "Invalid history form filter")
    forms = [ENABLED_FORM, OWNER_RIASEC_FORM] if form_key == HISTORY_ALL_FORMS else [form_key]
    params = [forms]
    paging = ""
    if cursor is not None:
        try:
            timestamp_text, run_text = cursor.split("|")
            timestamp = datetime.fromisoformat(timestamp_text)
            run_id = uuid.UUID(run_text)
            if timestamp.tzinfo is None or timestamp.utcoffset() is None:
                raise ValueError("Cursor must have timezone")
        except (TypeError, ValueError) as exc:
            raise HTTPException(422, "Invalid history cursor") from exc
        paging = "AND (r.created_at, r.run_id) < (%s, %s)"
        params.extend([timestamp, run_id])
    params.append(HISTORY_PAGE_SIZE + 1)
    with connect(url) as conn:
        rows = conn.execute(
            """SELECT r.run_id, r.created_at, r.status, r.algorithm_version,
                      f.form_key, f.form_version
               FROM ualp_assessment_runs AS r
               JOIN ualp_catalog_forms AS f ON f.form_id = r.form_id
               WHERE f.form_key = ANY(%s) AND r.status = 'COMPLETED'
            """ + paging +
            """ ORDER BY r.created_at DESC, r.run_id DESC LIMIT %s""",
            tuple(params),
        ).fetchall()
    page = rows[:HISTORY_PAGE_SIZE]
    next_cursor = None
    if len(rows) > HISTORY_PAGE_SIZE and page:
        last = page[-1]
        next_cursor = last["created_at"].isoformat() + "|" + str(last["run_id"])
    return {
        "items": [
            {
                "runId": str(row["run_id"]),
                "completedAt": row["created_at"].isoformat(),
                "status": row["status"],
                "formKey": row["form_key"],
                "formVersion": row["form_version"],
                "scoringAlgorithmVersion": row["algorithm_version"],
            }
            for row in page
        ],
        "nextCursor": next_cursor,
        "pageSize": HISTORY_PAGE_SIZE,
        "formKeyFilter": form_key,
        "notice": "История только для владельца TEST. Оценки экспериментальные.",
    }


MAX_PROFILE_METHODS = 12


@app.get("/api/profile")
def owner_profile(response: Response, url: str = Depends(authorized)):
    """Derive a private single-owner snapshot from actual persisted completions.

    No identity, prediction, norms, answer replay, or cross-instrument scoring.
    A shared TEST key must never be mistaken for multi-user authorization.
    """
    response.headers["Cache-Control"] = "private, no-store"
    with connect(url) as conn:
        latest = conn.execute(
            """WITH ranked AS (
                 SELECT r.run_id, r.form_id, r.created_at, r.algorithm_version,
                        count(*) OVER (PARTITION BY r.form_id) AS run_count,
                        row_number() OVER (
                            PARTITION BY r.form_id
                            ORDER BY r.created_at DESC, r.run_id DESC
                        ) AS position
                 FROM ualp_assessment_runs AS r
                 WHERE r.status = 'COMPLETED'
               )
               SELECT ranked.run_id, ranked.created_at, ranked.algorithm_version,
                      ranked.run_count, f.form_key, f.form_version,
                      f.status AS form_status, f.validation_status
               FROM ranked
               JOIN ualp_catalog_forms AS f ON f.form_id = ranked.form_id
               WHERE ranked.position = 1
               ORDER BY ranked.created_at DESC, ranked.run_id DESC
               LIMIT %s""",
            (MAX_PROFILE_METHODS + 1,),
        ).fetchall()
        has_more = len(latest) > MAX_PROFILE_METHODS
        latest = latest[:MAX_PROFILE_METHODS]
        scores_by_run = defaultdict(list)
        if latest:
            run_ids = [row["run_id"] for row in latest]
            parent_scores = conn.execute(
                """SELECT sc.run_id, sc.scale_id, c.scale_key, c.label,
                          sc.raw_score, sc.answered_count
                   FROM ualp_scale_scores AS sc
                   JOIN ualp_catalog_scales AS c ON c.scale_id = sc.scale_id
                   WHERE sc.run_id = ANY(%s::uuid[]) AND c.is_parent = true
                   ORDER BY sc.run_id, c.scale_key""",
                (run_ids,),
            ).fetchall()
            for score in parent_scores:
                scores_by_run[score["run_id"]].append({
                    "scaleId": score["scale_id"],
                    "key": score["scale_key"],
                    "label": score["label"],
                    "mean": score["raw_score"],
                    "answered": score["answered_count"],
                })
    methods = [
        {
            "formKey": row["form_key"],
            "formVersion": row["form_version"],
            "formStatus": row["form_status"],
            "validationStatus": row["validation_status"],
            "completedRuns": row["run_count"],
            "latestRunId": str(row["run_id"]),
            "latestAt": row["created_at"].isoformat(),
            "scoringAlgorithmVersion": row["algorithm_version"],
            "parentScores": scores_by_run[row["run_id"]],
        }
        for row in latest
    ]
    return {
        "ownerMode": "SINGLE_OWNER_TEST",
        "methods": methods,
        "methodCount": len(methods),
        "completedRuns": sum(row["completedRuns"] for row in methods),
        "hasMoreMethods": has_more,
        "notice": (
            "Исследовательские сырые результаты без норм, IQ, "
            "диагнозов и рекомендаций. Значения разных методик "
            "нельзя непосредственно сравнивать."
        ),
    }

# Reuse signed owner session; Career KB never joins assessment data.
from career_kb.owner_read_api import build_owner_router
app.include_router(build_owner_router(authorized, connect))
