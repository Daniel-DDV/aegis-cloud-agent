"""Pytest suite for EU AI Act rubric + Aegis eval fixtures."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "rubric"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "rubric"))

# Also allow importing from packages/rubric as module path
sys.path.insert(0, str(ROOT / "packages"))

from rubric.scorer import (  # noqa: E402
    score_bias,
    score_documentation,
    score_red_team,
    score_risk_signals,
)

FIXTURES = json.loads((Path(__file__).parent / "fixtures.json").read_text(encoding="utf-8"))


def _by_id(fid: str) -> dict:
    for f in FIXTURES:
        if f["id"] == fid:
            return f
    raise KeyError(fid)


@pytest.mark.parametrize(
    "fid",
    [
        "prohibited-social-scoring",
        "high-employment-cv",
        "high-essential-services-chatbot",
        "limited-generic-chatbot",
        "minimal-static-site",
        "high-biometric",
        "high-education",
        "high-law-enforcement",
    ],
)
def test_risk_classifier_fixtures(fid: str):
    fx = _by_id(fid)
    result = score_risk_signals(fx["corpus"], fx.get("metadata", {}))
    assert result.risk_tier.value == fx["expected_risk_tier"], (
        f"{fid}: expected {fx['expected_risk_tier']}, got {result.risk_tier.value} ({result.rationale})"
    )
    for art in fx.get("must_include_articles", []):
        assert art in result.articles, f"{fid}: missing article {art} in {result.articles}"


def test_documentation_gaps_empty():
    fx = _by_id("doc-gaps-empty")
    result = score_documentation(fx["corpus"], fx.get("files", []))
    assert len(result.findings) >= fx["expected_doc_gaps_min"]


def test_documentation_complete():
    fx = _by_id("doc-complete")
    result = score_documentation(fx["corpus"], fx.get("files", []))
    assert len(result.findings) <= fx["expected_doc_gaps_max"]


def test_bias_risk():
    fx = _by_id("bias-risk")
    result = score_bias(fx["corpus"])
    actionable = [f for f in result.findings if f.severity != "info"]
    assert len(actionable) >= fx["expected_bias_findings_min"]


def test_red_team_secrets():
    fx = _by_id("red-team-secrets")
    result = score_red_team(fx["corpus"])
    assert len(result.findings) >= fx["expected_red_findings_min"]
    codes = {f.code for f in result.findings}
    assert "SECRET_LEAK" in codes or "UNBOUNDED_TOOL" in codes or "NO_RATE_LIMIT" in codes


def test_municipal_sample_end_to_end():
    """Integration: load sample stub through rubric scorers."""
    sample = ROOT / "samples" / "municipal-chatbot-stub"
    text_parts = []
    files = []
    for p in sample.rglob("*"):
        if p.is_file():
            files.append(p.name)
            text_parts.append(p.read_text(encoding="utf-8", errors="ignore"))
    corpus = "\n".join(text_parts)
    risk = score_risk_signals(
        corpus,
        {"is_chatbot": True, "annex_iii_domains": ["essential_services"]},
    )
    assert risk.risk_tier.value in {"high", "limited", "prohibited"}
    red = score_red_team(corpus)
    assert len(red.findings) >= 2
    docs = score_documentation(corpus, files)
    assert len(docs.findings) >= 1
