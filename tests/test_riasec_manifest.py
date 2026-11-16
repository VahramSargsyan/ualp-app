"""Private RIASEC source-lock test data is wholly synthetic, never O*NET content."""
import copy
import json

import pytest

from webapp.riasec_manifest import (
    DRAFT_STATUS, FORM_KEY, LICENSE_URL, PRIVATE_SCOPE, SCHEMA_VERSION,
    ManifestError, check_local_file, validate_private_manifest,
)
from webapp.riasec_scoring import RIASEC_AREAS


def make_synthetic_manifest():
    return {
        "schemaVersion": SCHEMA_VERSION,
        "formKey": FORM_KEY,
        "formVersion": "synthetic-owner-draft-01",
        "sourceFormId": "SYNTHETIC_FORM_ONLY",
        "locale": "ru",
        "purpose": "VOLUNTARY_SELF_EXPLORATION",
        "distributionScope": PRIVATE_SCOPE,
        "validationStatus": DRAFT_STATUS,
        "algorithmVersion": "RIASEC-SUM-v1",
        "licenseUrl": LICENSE_URL,
        "items": [
            {
                "itemId": f"CI_ITEM_{i:02d}",
                "sourceIndex": i + 1,
                "prompt": f"Синтетическое занятие {i+1}",
                "scaleKey": RIASEC_AREAS[i // 10],
                "reviewStatus": DRAFT_STATUS,
            } for i in range(60)
        ],
        "options": [
            {
                "optionKey": f"CI_OPT_{i}",
                "label": f"Синтетический вариант {i}",
                "scoreValue": i,
                "reviewStatus": DRAFT_STATUS,
            } for i in range(5)
        ],
        "scales": [
            {"scaleKey": area, "label": f"Синтетическая шкала {area}"}
            for area in RIASEC_AREAS
        ],
    }


def test_receipt_only_digest_and_metadata_no_source_text():
    m = make_synthetic_manifest()
    receipt = validate_private_manifest(m)
    assert receipt.item_count == 60 and receipt.options_count == 5
    assert receipt.scales_count == 6 and receipt.scales_items_each == 10
    assert receipt.eligible_for_public_release is False
    assert receipt.validation_status == DRAFT_STATUS
    assert len(receipt.source_digest_sha256) == 64
    assert "Синтетическое занятие" not in repr(receipt)


def test_digest_canonical_json_and_changed_text_detected():
    m = make_synthetic_manifest()
    a = validate_private_manifest(m)
    reversed_keys = dict(reversed(list(m.items())))
    b = validate_private_manifest(reversed_keys, expected_digest=a.source_digest_sha256)
    assert a == b
    changed = copy.deepcopy(m)
    changed["items"][0]["prompt"] += " изменено"
    with pytest.raises(ManifestError, match="digest"):
        validate_private_manifest(changed, expected_digest=a.source_digest_sha256)
    assert validate_private_manifest(changed).source_digest_sha256 != a.source_digest_sha256


def test_private_json_roundtrip_and_duplicate_keys_blocked(tmp_path):
    path = tmp_path / "private-catalog.json"
    m = make_synthetic_manifest()
    path.write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
    lock = check_local_file(path)
    assert lock.item_count == 60
    assert check_local_file(path, expected_digest=lock.source_digest_sha256) == lock
    path.write_text('{"schemaVersion":"x","schemaVersion":"y"}', encoding="utf-8")
    with pytest.raises(ManifestError, match="Duplicated"):
        check_local_file(path)


def _omit_item(m): m["items"].pop()
def _duplicate_item(m): m["items"][1]["itemId"] = m["items"][0]["itemId"]
def _index_gap(m): m["items"][0]["sourceIndex"] = 2
def _wrong_scale(m): m["items"][0]["scaleKey"] = "I"
def _unknown_scale(m): m["items"][0]["scaleKey"] = "D"
def _wrong_order(m): m["items"].reverse()
def _wrong_option_count(m): m["options"].pop()
def _repeated_score(m): m["options"][0]["scoreValue"] = 1
def _bad_score_boolean(m): m["options"][0]["scoreValue"] = True
def _bad_option_key(m): m["options"][1]["optionKey"] = m["options"][0]["optionKey"]
def _blank_prompt(m): m["items"][0]["prompt"] = " "
def _hidden_linebreak(m): m["items"][0]["prompt"] = "Synthetic\nmalicious"
def _false_review_approval(m): m["items"][0]["reviewStatus"] = "VALIDATED"
def _false_option_review(m): m["options"][0]["reviewStatus"] = "VALIDATED"
def _public_scope(m): m["distributionScope"] = "PUBLIC"
def _different_locale(m): m["locale"] = "en"
def _license_missing(m): m["licenseUrl"] = ""
def _wrong_algorithm(m): m["algorithmVersion"] = "MEAN"
def _surprise_field(m): m["items"][0]["userSecret"] = "fake"
def _out_of_order_scales(m): m["scales"].reverse()
def _bad_source_id(m): m["sourceFormId"] = ""


@pytest.mark.parametrize("mutate", [
    _omit_item, _duplicate_item, _index_gap, _wrong_scale, _unknown_scale,
    _wrong_order, _wrong_option_count, _repeated_score, _bad_score_boolean,
    _bad_option_key, _blank_prompt, _hidden_linebreak, _false_review_approval,
    _false_option_review, _public_scope, _different_locale, _license_missing,
    _wrong_algorithm, _surprise_field, _out_of_order_scales, _bad_source_id,
])
def test_source_gate_fails_closed(mutate):
    m = make_synthetic_manifest()
    mutate(m)
    with pytest.raises(ManifestError):
        validate_private_manifest(m)


def test_extra_root_fields_and_incomplete_forms_fail():
    m = make_synthetic_manifest()
    m["respondentName"] = "Not allowed"
    with pytest.raises(ManifestError):
        validate_private_manifest(m)
    m = make_synthetic_manifest()
    m["validationStatus"] = "PASS"
    with pytest.raises(ManifestError):
        validate_private_manifest(m)
