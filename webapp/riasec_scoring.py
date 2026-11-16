"""Synthetic-data-only scorer contract for future O*NET 60-item digital RIASEC.

NOT wired into UALP runtime or Neon. Does not contain licensed item text,
option translations, respondent data, or ready-to-deploy assessment content.

Source: UALP canonical ASSESS-001 / FORM-000001 / RIASEC-SUM-v1.
Official API answer transport is 1..5; the catalog adapter supplies 0..4.
The separate 60-item paper questionnaire uses binary responses and MUST NOT
use this scorer. Russian adaptation remains DRAFT/NOT_REVIEWED.
"""

from collections import Counter
from collections.abc import Mapping, Sequence


RIASEC_AREAS = ("R", "I", "A", "S", "E", "C")
ITEM_COUNT = 60
ITEMS_PER_AREA = 10
SCORE_RANGE = range(5)
ALGORITHM_VERSION = "RIASEC-SUM-v1"


class RIASECContractError(ValueError):
    """Fail closed on incomplete or noncanonical form/scoring metadata."""


def score_short_form(
    answers: Mapping[str, str],
    item_scales: Sequence[tuple[str, str]],
    option_scores: Mapping[str, int],
) -> dict[str, int]:
    """Return six unnormed raw scores 0..40 (ten 0..4 items per scale).

    The caller must validate source provenance, licence/translation status,
    version and consent BEFORE enabling any stored form or real respondent run.
    """
    if len(option_scores) != 5 or set(option_scores.values()) != set(SCORE_RANGE) \
            or any(type(value) is not int for value in option_scores.values()):
        raise RIASECContractError("Expected five distinct integer values 0..4")

    if len(item_scales) != ITEM_COUNT:
        raise RIASECContractError("Expected exactly 60 item/scale links")
    ids = [item_id for item_id, _ in item_scales]
    if any(not isinstance(item_id, str) or not item_id for item_id in ids):
        raise RIASECContractError("Invalid item identity")
    if len(set(ids)) != ITEM_COUNT:
        raise RIASECContractError("Duplicate item/link identity")
    membership = Counter(scale for _, scale in item_scales)
    if set(membership) != set(RIASEC_AREAS) or any(
        membership[area] != ITEMS_PER_AREA for area in RIASEC_AREAS
    ):
        raise RIASECContractError("Expected exactly ten distinct items per RIASEC scale")
    if len(answers) != ITEM_COUNT or set(answers) != set(ids):
        raise RIASECContractError("All 60 source-indexed items must be answered once")
    if any(key not in option_scores for key in answers.values()):
        raise RIASECContractError("Invalid answer option")

    scores = dict.fromkeys(RIASEC_AREAS, 0)
    for item_id, area in item_scales:
        scores[area] += option_scores[answers[item_id]]
    if any(not 0 <= value <= 40 for value in scores.values()):
        raise RIASECContractError("Scoring range violated")
    return scores



def score_catalog_short_form(
    answers: Mapping[str, str],
    option_scores: Mapping[str, object],
    links: Sequence[Mapping[str, object]],
    rules: Sequence[Mapping[str, object]],
    scales: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Validate *synthetic CI* PostgreSQL catalog and return six stored-scale rows.

    This adapter is NOT a licence or validation gate: the HTTP boundary separately
    denies this form outside localhost-only disposable CI, even if catalog rows exist.
    """
    if len(scales) != 6:
        raise RIASECContractError("Expected exactly six parent scales")
    by_id = {}
    by_area = {}
    for s in scales:
        area, sid = s["scale_key"], s["scale_id"]
        if (area not in RIASEC_AREAS or area in by_area
                or sid in by_id or s["is_parent"] is not True):
            raise RIASECContractError("Invalid scale identity or parent status")
        by_id[sid] = area
        by_area[area] = sid
    if set(by_area) != set(RIASEC_AREAS):
        raise RIASECContractError("Missing RIASEC parent scale")

    if len(rules) != 6:
        raise RIASECContractError("Expected six SUM rules")
    if {r["scale_id"] for r in rules} != set(by_id):
        raise RIASECContractError("Scale/rule mismatch")
    for rule in rules:
        if (rule["method"] != "SUM" or rule["min_items"] != 10
                or rule["algorithm_version"] != ALGORITHM_VERSION
                or rule["status"] != "DRAFT"):
            raise RIASECContractError("Unapproved scoring rule")

    pairs = []
    for l in links:
        if (l["scale_id"] not in by_id
                or l["direction"] != "POSITIVE"
                or l["weight"] != 1):
            raise RIASECContractError("Unapproved link weight/direction")
        pairs.append((l["item_id"], by_id[l["scale_id"]]))

    clean_options = {}
    for key, value in option_scores.items():
        # PostgreSQL numeric is Decimal: require exact integer, never round.
        if value is None or value != int(value):
            raise RIASECContractError("Nonintegral response score")
        clean_options[key] = int(value)
    scores = score_short_form(answers, pairs, clean_options)
    return [
        {"scaleId": by_area[area], "mean": scores[area],
         "answered": 10, "algorithmVersion": ALGORITHM_VERSION}
        for area in RIASEC_AREAS
    ]
