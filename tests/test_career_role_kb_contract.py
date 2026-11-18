"""Standalone, source-free tests for proposed Career KB synthetic contract.

These tests NEVER connect to Neon or import real O*NET rows.
"""
import copy
import json
import math
from pathlib import Path

import pytest


FIXTURE = Path(__file__).parent / "fixtures" / "career_role_kb_synthetic_v0_1.json"


def _unique(rows, field):
    values = [r[field] for r in rows]
    assert len(values) == len(set(values)), "duplicate " + field
    return set(values)


def validate_fixture(data):
    assert data["schemaVersion"] == "UALP-CAREER-KB-SYNTH-v0.1"
    assert data["datasetKind"] == "SYNTHETIC_ONLY"
    snapshots = _unique(data["sourceSnapshots"], "snapshotId")
    occupations = _unique(data["occupations"], "occupationId")
    versions = _unique(data["occupations"], "occupationVersionId")
    competencies = _unique(data["competencies"], "competencyId")
    _unique(data["requirements"], "requirementId")
    assert len(occupations) == 2 and len(competencies) == 3
    assert len(data["requirements"]) == 4
    assert all(s["provider"] == "SYNTHETIC_TEST_ONLY" and s["sourceVersion"]
               and s["retrievedAt"].endswith("Z") for s in data["sourceSnapshots"])
    for role in data["occupations"]:
        assert role["snapshotId"] in snapshots
        assert role["externalCode"].startswith("FAKE-")
        assert role["status"] == "SYNTHETIC_ONLY"
    for competency in data["competencies"]:
        assert competency["snapshotId"] in snapshots
        assert competency["sourceElementId"].startswith("FAKE-")
        assert competency["kind"] in {"SKILL", "KNOWLEDGE", "TASK", "ABILITY"}
    for req in data["requirements"]:
        assert req["occupationVersionId"] in versions
        assert req["competencyId"] in competencies
        assert req["snapshotId"] in snapshots
        assert req["sourceScaleId"].startswith("FAKE-")
        assert req["measureKind"] in {"IMPORTANCE", "LEVEL", "PRESENCE"}
        role = next(x for x in data["occupations"]
                    if x["occupationVersionId"] == req["occupationVersionId"])
        competency = next(x for x in data["competencies"]
                          if x["competencyId"] == req["competencyId"])
        assert role["snapshotId"] == req["snapshotId"] == competency["snapshotId"]
        low, high = req["scale"]["min"], req["scale"]["max"]
        assert type(low) in (int, float) and type(high) in (int, float)
        assert math.isfinite(low) and math.isfinite(high) and low < high
        if req["evidenceStatus"] == "OBSERVED":
            assert req["sourceRecordId"] and req["sourceRecordId"].startswith("FAKE-")
            assert type(req["value"]) in (int, float)
            assert math.isfinite(req["value"]) and low <= req["value"] <= high
        else:
            assert req["evidenceStatus"] == "NOT_REPORTED"
            assert req["sourceRecordId"] is None
            assert req["value"] is None  # unknown is never coerced to zero
    bridge = data["profileBridge"]
    assert bridge["existingEndpoint"] == "GET /api/profile"
    assert bridge["roleMatchingEnabled"] is False
    assert bridge["skillInferenceFromAssessmentEnabled"] is False
    assert bridge["userDataIncluded"] is False
    assert bridge["learnerEvidence"] == []
    assert bridge["roleGapScores"] == []
    return True


def load():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_synthetic_contract_passes():
    assert validate_fixture(load())


def test_unknown_is_not_zero():
    data = load()
    req = next(x for x in data["requirements"]
               if x["evidenceStatus"] == "NOT_REPORTED")
    assert req["value"] is None
    req["value"] = 0
    with pytest.raises(AssertionError):
        validate_fixture(data)


def test_orphan_competency_rejected():
    data = load()
    data["requirements"][0]["competencyId"] = "COMP-NONEXISTENT"
    with pytest.raises(AssertionError):
        validate_fixture(data)


def test_cross_snapshot_provenance_rejected():
    data = load()
    data["sourceSnapshots"].append({
        **copy.deepcopy(data["sourceSnapshots"][0]),
        "snapshotId": "SNAP-UNRELATED-002"
    })
    data["requirements"][0]["snapshotId"] = "SNAP-UNRELATED-002"
    with pytest.raises(AssertionError):
        validate_fixture(data)


def test_out_of_range_measurement_rejected():
    data = load()
    data["requirements"][0]["value"] = 6
    with pytest.raises(AssertionError):
        validate_fixture(data)


def test_real_source_claim_rejected():
    data = load()
    data["sourceSnapshots"][0]["provider"] = "ONET"
    with pytest.raises(AssertionError):
        validate_fixture(data)


def test_no_auto_career_fit_or_personal_data():
    data = load()
    data["profileBridge"]["skillInferenceFromAssessmentEnabled"] = True
    with pytest.raises(AssertionError):
        validate_fixture(data)
