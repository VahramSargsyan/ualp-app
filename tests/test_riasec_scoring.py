"""Synthetic-only QA; no original/translated O*NET item text or users."""
import pytest

from webapp.riasec_scoring import (
    ALGORITHM_VERSION,
    RIASEC_AREAS,
    RIASECContractError,
    score_short_form,
)


def fixture():
    links = [
        (f"SYNTHETIC_{i:02d}", RIASEC_AREAS[i // 10])
        for i in range(60)
    ]
    values = {f"CHOICE_{i}": i for i in range(5)}
    answers = {item: "CHOICE_4" for item, _ in links}
    return answers, links, values


def test_ria_sec_algorithm_is_explicit_and_unmodified():
    assert ALGORITHM_VERSION == "RIASEC-SUM-v1"
    assert RIASEC_AREAS == ("R", "I", "A", "S", "E", "C")


def test_all_high_and_all_low_yield_six_sums_in_range():
    answers, links, values = fixture()
    assert score_short_form(answers, links, values) == dict.fromkeys(RIASEC_AREAS, 40)
    answers = dict.fromkeys(answers, "CHOICE_0")
    assert score_short_form(answers, links, values) == dict.fromkeys(RIASEC_AREAS, 0)


def test_six_scales_are_independent_not_normalized_or_averaged():
    answers, links, values = fixture()
    # Ten answers per category: all possible scores 0..4, twice.
    for i, (item_id, _area) in enumerate(links):
        answers[item_id] = f"CHOICE_{i % 5}"
    assert score_short_form(answers, links, values) == dict.fromkeys(RIASEC_AREAS, 20)
    for item_id, area in links:
        if area == "R":
            answers[item_id] = "CHOICE_1"
    assert score_short_form(answers, links, values) == {
        "R": 10, "I": 20, "A": 20, "S": 20, "E": 20, "C": 20
    }


@pytest.mark.parametrize("mutation", [
    lambda a, l, v: a.pop(next(iter(a))),
    lambda a, l, v: a.update({"UNKNOWN_ITEM": "CHOICE_4"}),
    lambda a, l, v: a.update({next(iter(a)): "INVALID"}),
    lambda a, l, v: l.__setitem__(0, l[1]),  # Duplicate ID, missing original
    lambda a, l, v: l.__setitem__(0, (l[0][0], "INVALID_AREA")),
    lambda a, l, v: l.__setitem__(0, (l[0][0], "I")),  # 9 R and 11 I
    lambda a, l, v: v.update({"CHOICE_4": 3}),  # Non-bijective scale
    lambda a, l, v: v.update({"CHOICE_4": True}),  # Avoid bool-as-integer
    lambda a, l, v: v.update({"CHOICE_4": 4.0}),
])
def test_noncanonical_input_fails_closed(mutation):
    answers, links, values = fixture()
    mutation(answers, links, values)
    with pytest.raises(RIASECContractError):
        score_short_form(answers, links, values)


def test_preparation_does_not_enable_riasec_in_server_routes():
    from webapp import main
    assert main.ENABLED_FORM == "UALP_WV21_RU_LIKERT"
    assert not hasattr(main, "submit_riasec")
    assert not hasattr(main, "load_riasec")
