"""Source-locked, read-only import-plan tests. No DB/Neon or API calls."""
import csv
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest

from career_kb.import_plan import make_import_plan
from career_kb.offline_reader import FILES, HEADERS, LICENSE, PREFIX, SourceLockError

CODE_A = "15-2051.00"
CODE_B = "15-2051.01"


def fixture(tmp_path):
    occs = [[CODE_A, "Fictional Scientist", "Synthetic analyst description"],
            [CODE_B, "Fictional BI Specialist", "Synthetic business description"]]
    scales = [["IM", "Importance", "1", "5"], ["LV", "Level", "0", "7"]]
    skills = []
    for code, title in [(CODE_A, "Fictional Scientist"), (CODE_B, "Fictional BI Specialist")]:
        for n in range(10):
            for scale, label, raw in [("IM", "Importance", "3.0"), ("LV", "Level", "4.0")]:
                suppress = "Y" if (code, n, scale) == (CODE_A, 3, "LV") else "N"
                skills.append([code, title, f"2.A.SYNTH.{n}", f"Synthetic skill {n}",
                               scale, label, raw, "8", "", "", "",
                               suppress, "N", "08/2026", "SYNTHETIC_ONLY"])
    contents = dict(zip(FILES, [occs, skills, scales]))
    manifest = {"schemaVersion": "UALP-ONET-31.0-OFFLINE-LOCK-v1",
                "provider": "O*NET Database", "release": "31.0",
                "licenseUrl": LICENSE, "files": {}}
    receipt = {"release": "31.0", "officialURLsOnly": True,
               "status": "OFFICIAL_HTTPS_ACQUIRED_AND_OFFLINE_READER_PASS",
               "noDatabaseWrites": True, "noCareerScoring": True,
               "triggerCommit": "a" * 40,
               "completedAtUTC": "2026-11-18T14:16:55+00:00", "files": {}}
    for name, rows in contents.items():
        with (tmp_path / name).open("w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(HEADERS[name])
            writer.writerows(rows)
        raw = (tmp_path / name).read_bytes()
        info = {"sourceUrl": PREFIX + name, "sha256": hashlib.sha256(raw).hexdigest(),
                "sizeBytes": len(raw), "rowCount": len(rows)}
        manifest["files"][name] = info
        receipt["files"][name] = {**info, "finalUrl": PREFIX + name,
                                   "httpStatus": 200}
    m = tmp_path / "source_lock.json"
    m.write_text(json.dumps(manifest), encoding="utf-8")
    r = tmp_path / "acquisition_receipt.json"
    r.write_text(json.dumps(receipt), encoding="utf-8")
    return m, r


def test_plan_shape_and_missingness(tmp_path):
    m, r = fixture(tmp_path)
    plan = make_import_plan(tmp_path, m, [CODE_B, CODE_A], r)
    assert plan["readOnly"] is True and plan["mutationAuthorized"] is False
    assert plan["personalData"] is False and plan["careerFitCalculated"] is False
    assert len(plan["occupations"]) == len(plan["occupationVersions"]) == 2
    assert len(plan["competencies"]) == len(plan["competencyVersions"]) == 10
    assert len(plan["scales"]) == 2 and len(plan["requirements"]) == 40
    assert [x["scaleId"] for x in plan["scales"]] == ["IM", "LV"]
    assert plan["sourceAttestation"]["status"] == "GITHUB_HTTPS_RECEIPT_MATCHES_LOCK"
    assert sum(x["evidenceStatus"] == "SUPPRESSED" for x in plan["requirements"]) == 1
    assert all(x["rawValue"] is None for x in plan["requirements"]
               if x["evidenceStatus"] != "OBSERVED")
    assert len(set(x["requirementId"] for x in plan["requirements"])) == 40
    assert all(r["snapshotId"] == "ONET_DB_31_0" for r in plan["requirements"])


def test_deterministic_even_with_reversed_role_order(tmp_path):
    m, r = fixture(tmp_path)
    x = make_import_plan(tmp_path, m, [CODE_A, CODE_B], r)
    y = make_import_plan(tmp_path, m, [CODE_B, CODE_A], r)
    assert x == y
    assert len(x["planSha256"]) == 64


def test_no_receipt_is_explicitly_unattested(tmp_path):
    m, _ = fixture(tmp_path)
    x = make_import_plan(tmp_path, m, [CODE_A])
    assert x["sourceAttestation"]["status"] == "NOT_ATTESTED"
    assert len(x["requirements"]) == 20


def test_reject_unknown_occupation(tmp_path):
    m, r = fixture(tmp_path)
    with pytest.raises(SourceLockError, match="pre-reviewed"):
        make_import_plan(tmp_path, m, ["11-1011.00"], r)


def test_reject_duplicate_codes(tmp_path):
    m, r = fixture(tmp_path)
    with pytest.raises(SourceLockError, match="distinct"):
        make_import_plan(tmp_path, m, [CODE_A, CODE_A], r)


def test_reject_modified_source_after_lock(tmp_path):
    m, r = fixture(tmp_path)
    p = tmp_path / "essential_skills.csv"
    p.write_bytes(p.read_bytes() + b"fake data")
    with pytest.raises(SourceLockError, match="size mismatch"):
        make_import_plan(tmp_path, m, [CODE_A], r)


def test_reject_mismatched_receipt_hash(tmp_path):
    m, r = fixture(tmp_path)
    record = json.loads(r.read_text())
    record["files"]["essential_skills.csv"]["sha256"] = "a" * 64
    r.write_text(json.dumps(record))
    with pytest.raises(SourceLockError, match="receipt/hash mismatch"):
        make_import_plan(tmp_path, m, [CODE_A], r)


def test_reject_nonofficial_final_redirect(tmp_path):
    m, r = fixture(tmp_path)
    record = json.loads(r.read_text())
    record["files"]["occupation_data.csv"]["finalUrl"] = "https://random.example/other.csv"
    r.write_text(json.dumps(record))
    with pytest.raises(SourceLockError, match="receipt/hash mismatch"):
        make_import_plan(tmp_path, m, [CODE_A], r)


def test_no_overwrite_cli(tmp_path):
    m, r = fixture(tmp_path)
    dest = tmp_path / "plan.json"
    dest.write_text("EXISTING", encoding="utf-8")
    completed = subprocess.run([
        sys.executable, "-m", "career_kb.import_plan", "--source-dir", str(tmp_path),
        "--manifest", str(m), "--receipt", str(r),
        "--occupation-code", CODE_A, "--output", str(dest)
    ], cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True)
    assert completed.returncode != 0
    assert dest.read_text() == "EXISTING"


def test_proposal_schema_guard_and_rollback_files():
    root = Path(__file__).resolve().parents[1]
    schema = (root / "docs/migration_candidates/UALP_CAREER_KB_004_SCHEMA_CANDIDATE.sql").read_text()
    rollback = (root / "docs/migration_candidates/UALP_CAREER_KB_004_SCHEMA_ROLLBACK_DISPOSABLE_ONLY.sql").read_text()
    assert "ualp.career_migration_gate" in schema
    assert "APPROVED_DISPOSABLE_TEST" in schema
    assert "FOREIGN KEY (occupation_version_id,snapshot_id)" in schema
    assert "FOREIGN KEY (competency_version_id,snapshot_id)" in schema
    assert "FOREIGN KEY (snapshot_id,scale_id,scale_minimum,scale_maximum)" in schema
    assert "raw_value IS NULL" in schema
    assert "ualp_assessment_runs" not in schema
    assert "ON DELETE CASCADE" not in schema
    assert "ualp.career_rollback_gate" in rollback
    assert "nonempty tables" in rollback


def test_real_source_if_explicitly_provided(tmp_path):
    path = os.environ.get("UALP_ONET_SOURCE_ZIP")
    if not path:
        pytest.skip("No source archive specified; synthetic tests run independently")
    p = Path(path)
    assert p.is_file(), "Expected pre-acquired, locally mounted artifact"
    expected_zip_sha = "4d010c11479112c99fb44bd41890484259916b9093b83c3c614a77ab3c620f5d"
    assert hashlib.sha256(p.read_bytes()).hexdigest() == expected_zip_sha
    with ZipFile(p) as z:
        assert z.testzip() is None
        for name in FILES:
            (tmp_path / name).write_bytes(z.read("sources/" + name))
        m = tmp_path / "source_lock.json"
        r = tmp_path / "acquisition_receipt.json"
        m.write_bytes(z.read("receipt/source_lock.json"))
        r.write_bytes(z.read("receipt/acquisition_receipt.json"))
    plan = make_import_plan(tmp_path, m, [CODE_B, CODE_A], r)
    assert plan["sourceAttestation"]["runCommit"] == "1171ece481fde70a7493ddf581fb0a54d9f6fa68"
    assert len(plan["occupations"]) == 2
    assert [x["title"] for x in plan["occupationVersions"]] == [
        "Data Scientists", "Business Intelligence Analysts"]
    assert len(plan["requirements"]) == 40
    assert len(plan["competencies"]) == 10
    assert len(plan["scales"]) == 2
    assert sum(x["evidenceStatus"] == "SUPPRESSED" for x in plan["requirements"]) == 1
    assert plan["sourceSnapshot"]["files"]["essential_skills.csv"]["rowCount"] == 18200
    assert plan["sourceSnapshot"]["files"]["occupation_data.csv"]["rowCount"] == 1016
    assert plan["sourceSnapshot"]["files"]["scales_reference.csv"]["rowCount"] == 33
