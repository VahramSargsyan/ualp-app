import uuid
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from webapp.main import app, compute_scores, secure_config, authorized, APP_VERSION

def pilot_fixture():
    """Synthetic 21 items, 6 parent domains, 21 facets, 42 links, 27 rules."""
    item_ids = [f"I{x:02d}" for x in range(21)]
    domain_sizes = [4, 4, 4, 3, 3, 3]
    links = []
    rules = []
    position = 0
    for domain, n in enumerate(domain_sizes):
        scale = f"D{domain}"
        rules.append(dict(scale_id=scale, method="MEAN", min_items=n,
                          algorithm_version="WORKVALUES-MEAN-v1", status="DRAFT"))
        for _ in range(n):
            item = item_ids[position]
            links.append(dict(item_id=item, scale_id=scale, weight=1, direction="POSITIVE"))
            facet = f"F{position:02d}"
            links.append(dict(item_id=item, scale_id=facet, weight=1, direction="POSITIVE"))
            rules.append(dict(scale_id=facet, method="MEAN", min_items=1,
                              algorithm_version="WORKVALUES-MEAN-v1", status="DRAFT"))
            position += 1
    assert len(links) == 42 and len(rules) == 27
    return {item: "V4" for item in item_ids}, {"V0": 0, "V4": 4}, links, rules

def test_deterministic_all_high_scores():
    args = pilot_fixture()
    a = compute_scores(*args)
    b = compute_scores(*args)
    assert a == b and len(a) == 27
    assert all(x["mean"] == 4 for x in a)

def test_score_is_mean_not_sum():
    answers, option_scores, links, rules = pilot_fixture()
    answers["I00"] = "V0"
    out = {s["scaleId"]: s for s in compute_scores(answers, option_scores, links, rules)}
    assert out["D0"]["mean"] == 3
    assert out["D0"]["answered"] == 4

def test_unknown_answer_cannot_be_scored():
    answers, options, links, rules = pilot_fixture()
    answers["I00"] = "INVALID"
    with pytest.raises(ValueError):
        compute_scores(answers, options, links, rules)

def test_missing_scale_link_rejected():
    answers, options, links, rules = pilot_fixture()
    with pytest.raises(ValueError):
        compute_scores(answers, options, links[:-1], rules)

def test_unapproved_negative_scoring_rejected():
    answers, options, links, rules = pilot_fixture()
    links[0]["direction"] = "NEGATIVE"
    with pytest.raises(ValueError):
        compute_scores(answers, options, links, rules)

def test_scoring_algorithm_is_version_locked():
    answers, options, links, rules = pilot_fixture()
    rules[0]["algorithm_version"] = "UNKNOWN-v3"
    with pytest.raises(ValueError):
        compute_scores(answers, options, links, rules)

def test_no_config_fails_closed(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("UALP_ACCESS_KEY", raising=False)
    monkeypatch.setenv("UALP_ENV", "TEST")
    with pytest.raises(HTTPException) as e:
        secure_config()
    assert e.value.status_code == 503

def test_non_test_environment_fails_closed(monkeypatch):
    monkeypatch.setenv("UALP_ENV", "PROD")
    with pytest.raises(HTTPException) as e:
        secure_config()
    assert e.value.status_code == 503

def test_unauthed_requests_rejected(monkeypatch):
    monkeypatch.setenv("UALP_ENV", "TEST")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test.invalid/not_reachable")
    monkeypatch.setenv("UALP_ACCESS_KEY", "x" * 48)
    with pytest.raises(HTTPException) as e:
        authorized("wrong")
    assert e.value.status_code == 401

def test_only_public_health_and_shell_without_secrets(monkeypatch):
    monkeypatch.delenv("UALP_ACCESS_KEY", raising=False)
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["database"] == "PostgreSQL"
        assert health.json()["version"] == APP_VERSION
        assert client.get("/").status_code == 200
        assert "DATABASE_URL" not in client.get("/").text
        assert client.get("/api/catalog").status_code == 503

def test_safelist_form_server_does_not_return_scoring_keys():
    from pathlib import Path
    src = Path("webapp/main.py").read_text(encoding="utf-8")
    assert '"scoreValue"' not in src
    assert '"isCorrect"' not in src
    assert "compute_scores" in src
