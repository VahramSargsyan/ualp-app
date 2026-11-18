"""Offline fixtures contain invented values only: no source data or personal results."""
import csv
import hashlib
import json
from pathlib import Path

import pytest

from career_kb.offline_reader import FILES, HEADERS, LICENSE, PREFIX, SourceLockError, parse_subset


CODE = "99-9999.99"  # fictional code in the O*NET-SOC syntactic shape
SECOND = "98-8888.88"


def make_sources(tmp_path):
    occupation = [
        [CODE, "Invented Researcher", "An entirely fictional job."],
        [SECOND, "Invented Builder", "Another invented occupation."],
    ]
    scales = [["IM", "Importance", "1", "5"], ["LV", "Level", "0", "7"]]
    def skill(code=CODE, element="9.FAKE.01", scale="IM", label="Importance", value="3.25",
              suppress="N", relevant="N"):
        return [code, "Invented Researcher" if code == CODE else "Invented Builder",
                element, "Fictional competency", scale, label, value, "", "", "", "",
                suppress, relevant, "11/2026", "SYNTHETIC_TEST"]
    skills = [skill(), skill(element="9.FAKE.02", scale="LV", label="Level", value="",
                            suppress="Y"),
              skill(code=SECOND, element="9.FAKE.03", value="1", relevant="Y")]
    fixtures = dict(zip(FILES, (occupation, skills, scales)))
    lock = {"schemaVersion": "UALP-ONET-31.0-OFFLINE-LOCK-v1",
            "provider": "O*NET Database", "release": "31.0",
            "licenseUrl": LICENSE, "files": {}}
    for name, content in fixtures.items():
        with (tmp_path / name).open("w", encoding="utf-8", newline="") as fp:
            w = csv.writer(fp)
            w.writerow(HEADERS[name])
            w.writerows(content)
        raw = (tmp_path / name).read_bytes()
        lock["files"][name] = {"sourceUrl": PREFIX + name,
                               "sizeBytes": len(raw), "rowCount": len(content), "sha256": hashlib.sha256(raw).hexdigest()}
    manifest = tmp_path / "source_lock.json"
    manifest.write_text(json.dumps(lock, indent=2), encoding="utf-8")
    return manifest


def test_pinned_local_subset_and_missingness(tmp_path):
    lock = make_sources(tmp_path)
    result = parse_subset(tmp_path, lock, [CODE, SECOND])
    assert result["officialOriginVerified"] is False
    assert result["integrityStatus"] == "LOCAL_BYTES_MATCH_DECLARED_SHA256"
    assert result["careerFitCalculated"] is False
    assert result["learnerEvidence"] == []
    assert len(result["occupations"]) == 2 and len(result["requirements"]) == 3
    assert [r["evidenceStatus"] for r in result["requirements"]] == ["OBSERVED", "SUPPRESSED", "NOT_RELEVANT"]
    assert result["requirements"][0]["value"] == "3.25"
    assert result["requirements"][1]["value"] is None
    assert result["requirements"][2]["value"] is None


def test_exact_hash_rejects_modified_bytes(tmp_path):
    lock = make_sources(tmp_path)
    path = tmp_path / "occupation_data.csv"
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(SourceLockError, match="size mismatch"):
        parse_subset(tmp_path, lock, [CODE])


def test_rejects_unpinned_hash(tmp_path):
    lock = make_sources(tmp_path)
    obj = json.loads(lock.read_text())
    obj["files"]["essential_skills.csv"]["sha256"] = "UNKNOWN"
    lock.write_text(json.dumps(obj))
    with pytest.raises(SourceLockError, match="exact SHA-256"):
        parse_subset(tmp_path, lock, [CODE])


def test_rejects_source_url_substitution(tmp_path):
    lock = make_sources(tmp_path)
    obj = json.loads(lock.read_text())
    obj["files"]["occupation_data.csv"]["sourceUrl"] = "https://example.invalid/mirror.csv"
    lock.write_text(json.dumps(obj))
    with pytest.raises(SourceLockError, match="Source URL mismatch"):
        parse_subset(tmp_path, lock, [CODE])


def test_unknown_occupation_and_duplicate_selection_fail(tmp_path):
    lock = make_sources(tmp_path)
    for codes in [["00-0000.00"], [CODE, CODE], ["not-a-code"], []]:
        with pytest.raises(SourceLockError):
            parse_subset(tmp_path, lock, codes)


def test_bad_scale_and_duplicate_row_fail(tmp_path):
    lock = make_sources(tmp_path)
    skill_path = tmp_path / "essential_skills.csv"
    with skill_path.open("a", encoding="utf-8", newline="") as fp:
        writer = csv.writer(fp)
        writer.writerow([CODE, "Invented Researcher", "9.FAKE.01", "Fictional competency",
                         "IM", "Importance", "2", "", "", "", "", "N", "N", "11/2026", "SYNTHETIC_TEST"])
    obj = json.loads(lock.read_text())
    raw = skill_path.read_bytes()
    obj["files"]["essential_skills.csv"].update(sizeBytes=len(raw), rowCount=4, sha256=hashlib.sha256(raw).hexdigest())
    lock.write_text(json.dumps(obj))
    with pytest.raises(SourceLockError, match="Duplicate occupation/skill/scale"):
        parse_subset(tmp_path, lock, [CODE])


def test_rejects_out_of_range_rating(tmp_path):
    lock = make_sources(tmp_path)
    skill_path = tmp_path / "essential_skills.csv"
    raw = skill_path.read_text().replace("3.25", "9.25")
    skill_path.write_text(raw)
    obj = json.loads(lock.read_text())
    obj["files"]["essential_skills.csv"].update(sizeBytes=len(skill_path.read_bytes()), sha256=hashlib.sha256(skill_path.read_bytes()).hexdigest())
    lock.write_text(json.dumps(obj))
    with pytest.raises(SourceLockError, match="Out-of-range"):
        parse_subset(tmp_path, lock, [CODE])


def test_fail_closed_when_required_columns_change(tmp_path):
    lock = make_sources(tmp_path)
    skill_path = tmp_path / "essential_skills.csv"
    skill_path.write_text(skill_path.read_text().replace("Element ID", "Fake Element ID"))
    obj = json.loads(lock.read_text())
    obj["files"]["essential_skills.csv"].update(sizeBytes=len(skill_path.read_bytes()), sha256=hashlib.sha256(skill_path.read_bytes()).hexdigest())
    lock.write_text(json.dumps(obj))
    with pytest.raises(SourceLockError, match="Unexpected columns"):
        parse_subset(tmp_path, lock, [CODE])


def test_no_network_or_database_import():
    from career_kb import offline_reader
    source = Path(offline_reader.__file__).read_text()
    for forbidden in ("requests", "urllib", "psycopg", "fastapi", "http.client", "subprocess"):
        assert f"import {forbidden}" not in source


def test_recomputed_hash_cannot_hide_truncated_records(tmp_path):
    lock = make_sources(tmp_path)
    name = "occupation_data.csv"
    path = tmp_path / name
    rows = path.read_text().splitlines()
    path.write_text("\n".join(rows[:-1]) + "\n")
    obj = json.loads(lock.read_text())
    obj["files"][name].update(sizeBytes=len(path.read_bytes()),
                                sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    lock.write_text(json.dumps(obj))
    with pytest.raises(SourceLockError, match="Row count mismatch"):
        parse_subset(tmp_path, lock, [CODE])

def test_nonfinite_source_value_rejected(tmp_path):
    lock = make_sources(tmp_path)
    name = "essential_skills.csv"
    path = tmp_path / name
    path.write_text(path.read_text().replace("3.25", "NaN"))
    obj = json.loads(lock.read_text())
    obj["files"][name].update(sizeBytes=len(path.read_bytes()),
                                sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    lock.write_text(json.dumps(obj))
    with pytest.raises(SourceLockError, match="Nonfinite"):
        parse_subset(tmp_path, lock, [CODE])

def test_orphan_scale_rejected(tmp_path):
    lock = make_sources(tmp_path)
    name = "essential_skills.csv"
    path = tmp_path / name
    path.write_text(path.read_text().replace(",IM,Importance,", ",ZZ,Importance,", 1))
    obj = json.loads(lock.read_text())
    obj["files"][name].update(sizeBytes=len(path.read_bytes()),
                                sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    lock.write_text(json.dumps(obj))
    with pytest.raises(SourceLockError, match="unknown scale"):
        parse_subset(tmp_path, lock, [CODE])
