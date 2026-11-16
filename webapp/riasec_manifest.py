"""Private source-lock preflight for a future owner-only RU RIASEC catalog.

This module never writes to a database, enables an assessment, or sends data to
a network. Copyrighted or private questions are read from a private local JSON
file at execution time; do not commit that file to the public UALP repository.
A successful structural check does NOT validate the Russian questionnaire.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from webapp.riasec_scoring import ALGORITHM_VERSION, RIASEC_AREAS

SCHEMA_VERSION = "UALP-RIASEC-PRIVATE-CATALOG-v1"
LICENSE_URL = "https://www.onetcenter.org/license_toolsdev.html"
FORM_KEY = "ONET_SHORT_60_DIGITAL"
DRAFT_STATUS = "DRAFT_NOT_REVIEWED"
PRIVATE_SCOPE = "OWNER_ONLY_PRIVATE_TEST"


class ManifestError(ValueError):
    """Reject malformed and unauthorized catalog content without exposing text."""


@dataclass(frozen=True)
class ManifestReceipt:
    schema: str
    form_version: str
    source_digest_sha256: str
    item_count: int
    options_count: int
    scales_count: int
    scales_items_each: int
    validation_status: str
    distribution_scope: str
    eligible_for_public_release: bool = False


def _keys(value: Any, required: set[str], what: str) -> None:
    if type(value) is not dict or set(value) != required:
        raise ManifestError(f"{what}: unexpected or missing fields")


def _nonempty(value: Any, what: str, limit: int = 600) -> None:
    if (type(value) is not str or not value.strip()
            or value != value.strip() or len(value) > limit
            or any(ord(ch) < 32 for ch in value)):
        raise ManifestError(f"{what}: invalid text")


def validate_private_manifest(manifest: Any, *, expected_digest: str | None = None) -> ManifestReceipt:
    """Pure deterministic validation; never returns prompt/labels/scoring keys."""
    _keys(manifest, {
        "schemaVersion", "formKey", "formVersion", "sourceFormId",
        "locale", "purpose", "distributionScope", "validationStatus",
        "algorithmVersion", "licenseUrl", "items", "options", "scales",
    }, "manifest")
    if (manifest["schemaVersion"] != SCHEMA_VERSION
            or manifest["formKey"] != FORM_KEY
            or manifest["locale"] != "ru"
            or manifest["purpose"] != "VOLUNTARY_SELF_EXPLORATION"
            or manifest["distributionScope"] != PRIVATE_SCOPE
            or manifest["validationStatus"] != DRAFT_STATUS
            or manifest["algorithmVersion"] != ALGORITHM_VERSION
            or manifest["licenseUrl"] != LICENSE_URL):
        raise ManifestError("Manifest purpose, rights, or validation gate mismatch")
    _nonempty(manifest["formVersion"], "formVersion", 120)
    _nonempty(manifest["sourceFormId"], "sourceFormId", 120)

    items = manifest["items"]
    options = manifest["options"]
    scales = manifest["scales"]
    if type(items) is not list or len(items) != 60:
        raise ManifestError("Exactly 60 items are required")
    if type(options) is not list or len(options) != 5:
        raise ManifestError("Exactly five response options are required")
    if type(scales) is not list or len(scales) != 6:
        raise ManifestError("Exactly six RIASEC scales are required")

    source_ids, source_indexes, groups = [], [], []
    for entry in items:
        _keys(entry, {"itemId", "sourceIndex", "prompt", "scaleKey", "reviewStatus"}, "item")
        _nonempty(entry["itemId"], "itemId", 120)
        _nonempty(entry["prompt"], "prompt")
        if (type(entry["sourceIndex"]) is not int
                or not 1 <= entry["sourceIndex"] <= 60):
            raise ManifestError("Invalid item source index")
        if entry["scaleKey"] not in RIASEC_AREAS:
            raise ManifestError("Unknown scale for item")
        if entry["reviewStatus"] != DRAFT_STATUS:
            raise ManifestError("Item review status is not preserved")
        source_ids.append(entry["itemId"])
        source_indexes.append(entry["sourceIndex"])
        groups.append(entry["scaleKey"])
    if (len(set(source_ids)) != 60
            or source_indexes != list(range(1, 61))):
        raise ManifestError("Item ID uniqueness or source order violation")
    if Counter(groups) != Counter({area: 10 for area in RIASEC_AREAS}):
        raise ManifestError("RIASEC balance 10x6 violation")

    seen_scores, seen_keys = [], []
    for option in options:
        _keys(option, {"optionKey", "label", "scoreValue", "reviewStatus"}, "option")
        _nonempty(option["optionKey"], "optionKey", 120)
        _nonempty(option["label"], "label")
        if (type(option["scoreValue"]) is not int
                or not 0 <= option["scoreValue"] <= 4):
            raise ManifestError("Noninteger or out-of-range response score")
        if option["reviewStatus"] != DRAFT_STATUS:
            raise ManifestError("Option review status is not preserved")
        seen_scores.append(option["scoreValue"])
        seen_keys.append(option["optionKey"])
    if seen_scores != [0, 1, 2, 3, 4] or len(set(seen_keys)) != 5:
        raise ManifestError("Five ordered and distinct response choices required")

    seen_areas = []
    for scale in scales:
        _keys(scale, {"scaleKey", "label"}, "scale")
        _nonempty(scale["label"], "scaleLabel", 120)
        if scale["scaleKey"] not in RIASEC_AREAS:
            raise ManifestError("Unknown RIASEC scale")
        seen_areas.append(scale["scaleKey"])
    if tuple(seen_areas) != RIASEC_AREAS:
        raise ManifestError("Six RIASEC scales must be in canonical order")

    canonical = json.dumps(manifest, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":"), allow_nan=False).encode("utf-8")
    digest = hashlib.sha256(canonical).hexdigest()
    if expected_digest is not None:
        if (type(expected_digest) is not str
                or len(expected_digest) != 64
                or expected_digest.lower() != digest):
            raise ManifestError("Private catalog digest does not match exact source lock")

    return ManifestReceipt(
        schema=SCHEMA_VERSION,
        form_version=manifest["formVersion"],
        source_digest_sha256=digest,
        item_count=60,
        options_count=5,
        scales_count=6,
        scales_items_each=10,
        validation_status=DRAFT_STATUS,
        distribution_scope=PRIVATE_SCOPE,
    )


def verify_private_postgres_catalog(
    form_row, items, options, scales, source_scales, expected_digest,
) -> ManifestReceipt:
    """Compute a private source lock from stored catalog without returning text.

    Caller enforces database host, owner authorization and SQL link/rule integrity.
    This helper has no database/network access and is not a public API serializer.
    """
    private_manifest = {
        "schemaVersion": SCHEMA_VERSION,
        "formKey": FORM_KEY,
        "formVersion": form_row["form_version"],
        "sourceFormId": form_row["form_id"],
        "locale": "ru",
        "purpose": "VOLUNTARY_SELF_EXPLORATION",
        "distributionScope": PRIVATE_SCOPE,
        "validationStatus": DRAFT_STATUS,
        "algorithmVersion": ALGORITHM_VERSION,
        "licenseUrl": LICENSE_URL,
        "items": [
            {"itemId": x["item_id"], "sourceIndex": x["display_order"],
             "prompt": x["prompt"], "scaleKey": source_scales[x["item_id"]],
             "reviewStatus": DRAFT_STATUS}
            for x in items
        ],
        "options": [
            {"optionKey": x["option_key"], "label": x["label"],
             "scoreValue": int(x["score_value"]),
             "reviewStatus": DRAFT_STATUS}
            for x in options
        ],
        "scales": [
            {"scaleKey": x["scale_key"], "label": x["label"]}
            for x in scales
        ],
    }
    return validate_private_manifest(
        private_manifest, expected_digest=expected_digest
    )


def _reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict:
    value = {}
    for key, item in pairs:
        if key in value:
            raise ManifestError("Duplicated JSON object field")
        value[key] = item
    return value


def check_local_file(path: Path, *, expected_digest: str | None = None) -> ManifestReceipt:
    """No upload, DB connection, optional API, or filename disclosure."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"),
                          object_pairs_hook=_reject_duplicate_json_keys,
                          parse_constant=lambda _: (_ for _ in ()).throw(
                              ManifestError("Nonfinite JSON value")))
        return validate_private_manifest(data, expected_digest=expected_digest)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ManifestError(f"Private manifest cannot be read: {type(exc).__name__}") from None


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only source lock preflight")
    parser.add_argument("--private-manifest", required=True, type=Path)
    parser.add_argument("--expected-sha256", default=None)
    args = parser.parse_args()
    try:
        receipt = check_local_file(args.private_manifest, expected_digest=args.expected_sha256)
    except ManifestError as exc:
        print(f"RIASEC PRIVATE PREFLIGHT BLOCKED: {exc}")
        return 2
    print(json.dumps(asdict(receipt), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
