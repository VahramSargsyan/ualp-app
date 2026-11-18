"""Owner-only, O*NET 31.0 source-locked Career KB pilot read API.

No user scores, profile joins, career matching, DB writes or public endpoints.
Requires UALP's existing owner authentication and the exact frozen Neon TEST data.
"""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal, InvalidOperation
import os
from typing import Callable

from fastapi import APIRouter, Depends, HTTPException, Response

SNAPSHOT_ID = "ONET_DB_31_0"
MANIFEST_SHA256 = "03bbd9bd709eab4ac764a940f5110ab9292645b67d34c3ef600f28fcc3f9da78"
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
SOURCE_HASHES = {
    "occupation_data.csv": "a09eae1d6609686e44e05b7290993a1c8b523d8ca224bc0eedc194c855c3ee02",
    "essential_skills.csv": "68c4d31d8c55077238395dca40cc4e6d32e6a608b5474bb8264b1f98ae415bd7",
    "scales_reference.csv": "bcba23858ce21ecaacbde303a8993e35d46724b4afb8c9ec2b10e04f42adcfc9",
}
ALLOWED_CODES = {
    "15-2051.00": "Data Scientists",
    "15-2051.01": "Business Intelligence Analysts",
}
SCALES = {"IM": ("Importance", Decimal("1"), Decimal("5")),
          "LV": ("Level", Decimal("0"), Decimal("7"))}
EXPECTED_COUNTS = {
    "ualp_career_snapshots": 1,
    "ualp_career_occupations": 2,
    "ualp_career_occupation_versions": 2,
    "ualp_career_competencies": 10,
    "ualp_career_competency_versions": 10,
    "ualp_career_scales": 2,
    "ualp_career_requirements": 40,
}
# Verified after exact Neon TEST source import (008) against independent rehearsal.
# A changed snapshot requires a separate reviewed release, not fallback reads.
EXPECTED_DIGESTS = {
    "ualp_career_snapshots": "e8b18b07b6fd2caef4dc28d37c940941",
    "ualp_career_occupations": "29b3837cb9cc9b0ddeab0dfbe8b1ae78",
    "ualp_career_occupation_versions": "9eff4efbb10f82c681201e8b2896e10c",
    "ualp_career_competencies": "0d1b3574bd464cc7f87121bd443cb1b0",
    "ualp_career_competency_versions": "09bb0927486336582b6d938fb6831c55",
    "ualp_career_scales": "0f8e3d5d13f05ca14ec0814e85a5b376",
    "ualp_career_requirements": "a712185e9175bb215bb11a0e68221432",
}
ATTRIBUTION = "O*NET Database 31.0 (USDOL/ETA), CC BY 4.0; UALP selected and formatted the data. No endorsement."
NOTICE = ("Справочник профессий США, не оценка ваших навыков или пригодности. "
          "Показатели Importance (1–5) и Level (0–7) — разные исходные шкалы O*NET. "
          "Нет данных о рынке труда Армении, соответствии профилю или рекомендациях.")


def _unavailable() -> None:
    raise HTTPException(503, "Career KB source version unavailable or altered")


def _assert(condition: bool) -> None:
    if not condition:
        _unavailable()


def _decimal(value: object) -> Decimal:
    try:
        v = Decimal(str(value))
        _assert(v.is_finite())
        return v
    except (InvalidOperation, TypeError, ValueError):
        _unavailable()


def _db_gate(conn) -> None:
    info = conn.info
    host = info.host or ""
    _assert(os.getenv("UALP_ENV") == "TEST"
            and info.dbname == "ualp_test" and info.user == "ualp_test_owner"
            and host.endswith(".neon.tech")
            and "localhost" not in host)


def _snapshot_and_digest(conn) -> None:
    source = conn.execute(
        """SELECT snapshot_id,provider,release,license_url,geography,
                  manifest_sha256,file_checks FROM public.ualp_career_snapshots
           WHERE snapshot_id=%s""", (SNAPSHOT_ID,)
    ).fetchall()
    _assert(len(source) == 1)
    s = source[0]
    _assert(s["snapshot_id"] == SNAPSHOT_ID and s["provider"] == "O*NET Database"
            and s["release"] == "31.0" and s["license_url"] == LICENSE_URL
            and s["manifest_sha256"] == MANIFEST_SHA256
            and s["geography"] == "United States / O*NET-SOC taxonomy")
    checks = s["file_checks"]
    _assert(isinstance(checks, dict) and set(checks) == set(SOURCE_HASHES))
    for filename, sha in SOURCE_HASHES.items():
        _assert(isinstance(checks[filename], dict)
                and checks[filename].get("sha256") == sha)

    # One server-side aggregate over exactly seven approved tables, no user data.
    parts = [
        "SELECT '" + table + "' AS name,count(*)::bigint AS n,"
        "md5(coalesce(string_agg(md5(row_to_json(t)::text),'' "
        "ORDER BY md5(row_to_json(t)::text)),'')) AS digest "
        "FROM public." + table + " t"
        for table in EXPECTED_COUNTS
    ]
    rows = conn.execute(" UNION ALL ".join(parts)).fetchall()
    _assert(len(rows) == 7 and {r["name"] for r in rows} == set(EXPECTED_COUNTS))
    for r in rows:
        _assert(int(r["n"]) == EXPECTED_COUNTS[r["name"]]
                and r["digest"] == EXPECTED_DIGESTS[r["name"]])


def _catalog(conn) -> tuple[list[dict], dict[str, list[dict]]]:
    _snapshot_and_digest(conn)
    roles = conn.execute(
        """SELECT o.occupation_id,o.taxonomy,o.source_external_code AS code,
                  v.occupation_version_id,v.source_locale,v.title,v.description
           FROM public.ualp_career_occupations o
           JOIN public.ualp_career_occupation_versions v
             ON v.occupation_id=o.occupation_id
           WHERE v.snapshot_id=%s ORDER BY o.source_external_code""",
        (SNAPSHOT_ID,),
    ).fetchall()
    _assert(len(roles) == 2 and {r["code"] for r in roles} == set(ALLOWED_CODES))
    for r in roles:
        code = r["code"]
        _assert(r["taxonomy"] == "O*NET-SOC" and r["title"] == ALLOWED_CODES[code]
                and r["source_locale"] == "en" and bool(r["description"].strip())
                and r["occupation_id"] == f"UALP_OCC_ONET_SOC:{code}"
                and r["occupation_version_id"] == f"ONET_31_0_OCC:{code}")

    measures = conn.execute(
        """SELECT o.source_external_code AS code,r.requirement_id,r.source_record_id,
                  c.provider_element_id AS element_id,v.label AS skill_label,
                  r.scale_id,s.label AS scale_label,s.minimum,s.maximum,
                  r.scale_minimum,r.scale_maximum,r.raw_value,r.evidence_status,
                  r.source_updated_at,r.domain_source
           FROM public.ualp_career_requirements r
           JOIN public.ualp_career_occupation_versions o
             ON o.occupation_version_id=r.occupation_version_id
             AND o.snapshot_id=r.snapshot_id
           JOIN public.ualp_career_competency_versions v
             ON v.competency_version_id=r.competency_version_id
             AND v.snapshot_id=r.snapshot_id
           JOIN public.ualp_career_competencies c
             ON c.competency_id=v.competency_id
           JOIN public.ualp_career_scales s
             ON s.snapshot_id=r.snapshot_id AND s.scale_id=r.scale_id
           WHERE r.snapshot_id=%s
           ORDER BY o.source_external_code,c.provider_element_id,r.scale_id""",
        (SNAPSHOT_ID,),
    ).fetchall()
    _assert(len(measures) == 40)
    by_role: dict[str, list[dict]] = defaultdict(list)
    seen: set[tuple[str, str, str]] = set()
    suppressed = 0
    for r in measures:
        code, element, scale_id = r["code"], r["element_id"], r["scale_id"]
        _assert(code in ALLOWED_CODES and scale_id in SCALES
                and isinstance(element, str) and element.startswith("2.A.")
                and isinstance(r["skill_label"], str) and bool(r["skill_label"].strip()))
        key = code, element, scale_id
        _assert(key not in seen)
        seen.add(key)
        name, minimum, maximum = SCALES[scale_id]
        _assert(r["scale_label"] == name
                and _decimal(r["minimum"]) == minimum
                and _decimal(r["maximum"]) == maximum
                and _decimal(r["scale_minimum"]) == minimum
                and _decimal(r["scale_maximum"]) == maximum
                and r["requirement_id"] == f"ONET_31_0_REQ:{code}:{element}:{scale_id}"
                and r["source_record_id"] == f"O-NET31:ESSENTIAL_SKILLS:{code}:{element}:{scale_id}")
        status = r["evidence_status"]
        if status == "SUPPRESSED":
            suppressed += 1
            _assert(r["raw_value"] is None)
            value = None
        else:
            _assert(status == "OBSERVED" and r["raw_value"] is not None)
            value = _decimal(r["raw_value"])
            _assert(minimum <= value <= maximum)
        by_role[code].append({
            "elementId": element, "skill": r["skill_label"],
            "scaleId": scale_id, "scaleName": name,
            "minimum": str(minimum), "maximum": str(maximum),
            "rawValue": None if value is None else str(value),
            "evidenceStatus": status,
            "updatedAtSource": r["source_updated_at"],
        })
    _assert(suppressed == 1 and len(by_role) == 2)
    for code, items in by_role.items():
        _assert(len(items) == 20)
        skills: dict[str, set[str]] = defaultdict(set)
        for item in items:
            skills[item["elementId"]].add(item["scaleId"])
        _assert(len(skills) == 10 and all(v == {"IM", "LV"} for v in skills.values()))
    return roles, by_role


def build_owner_router(auth: Callable, connect: Callable) -> APIRouter:
    """Wire into the existing session/key dependency, do not create a second auth."""
    router = APIRouter()

    def source_read(url: str):
        try:
            with connect(url) as conn:
                _db_gate(conn)
                # First statement inside a new transaction; no persistent DB writes.
                conn.execute("SET TRANSACTION READ ONLY")
                return _catalog(conn)
        except HTTPException:
            raise
        except Exception:
            _unavailable()

    @router.get("/api/careers")
    def careers(response: Response, url: str = Depends(auth)):
        roles, _ = source_read(url)
        response.headers["Cache-Control"] = "no-store, private"
        return {
            "source": {"snapshotId": SNAPSHOT_ID, "provider": "O*NET Database",
                       "release": "31.0", "licenseUrl": LICENSE_URL,
                       "geography": "United States", "attribution": ATTRIBUTION},
            "pilotOnly": True, "careerFitCalculated": False,
            "roles": [{"code": r["code"], "title": r["title"],
                       "description": r["description"], "skillCount": 10}
                      for r in roles],
            "notice": NOTICE,
        }

    @router.get("/api/careers/{code}")
    def career_detail(code: str, response: Response, url: str = Depends(auth)):
        if code not in ALLOWED_CODES:
            raise HTTPException(404, "Pilot occupation unavailable")
        roles, by_role = source_read(url)
        role = next(r for r in roles if r["code"] == code)
        response.headers["Cache-Control"] = "no-store, private"
        return {
            "source": {"snapshotId": SNAPSHOT_ID, "provider": "O*NET Database",
                       "release": "31.0", "licenseUrl": LICENSE_URL,
                       "geography": "United States", "attribution": ATTRIBUTION},
            "pilotOnly": True, "careerFitCalculated": False,
            "code": role["code"], "title": role["title"],
            "description": role["description"],
            "measurements": by_role[code], "measurementCount": 20,
            "skillCount": 10, "notice": NOTICE,
        }

    return router
