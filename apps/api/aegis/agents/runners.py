"""Specialist EU AI Act agents (deterministic scorers + structured traces)."""

from __future__ import annotations

from datetime import datetime, timezone

from rubric.scorer import (
    article_labels,
    score_bias,
    score_documentation,
    score_red_team,
    score_risk_signals,
)

from aegis.models.schemas import (
    AgentName,
    AgentResult,
    AgentStatus,
    FindingOut,
    RiskTier,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _map_findings(raw) -> list[FindingOut]:
    return [
        FindingOut(
            code=f.code,
            title=f.title,
            severity=f.severity,
            evidence=f.evidence,
            articles=f.articles,
            remediation=f.remediation,
        )
        for f in raw
    ]


def _tier(value: str) -> RiskTier:
    return RiskTier(value)


def run_risk_classifier(corpus: str, metadata: dict, files: list[str]) -> AgentResult:
    started = _now()
    result = AgentResult(
        agent=AgentName.risk_classifier,
        status=AgentStatus.running,
        started_at=started,
        trace=[
            "Loading EU AI Act Articles 5/6 signals",
            f"Scanning {len(files)} files for Annex III / prohibited cues",
        ],
    )
    scored = score_risk_signals(corpus, metadata)
    result.status = AgentStatus.completed
    result.finished_at = _now()
    result.risk_tier = _tier(scored.risk_tier.value)
    result.score = scored.score
    result.rationale = scored.rationale
    result.findings = _map_findings(scored.findings)
    result.articles = scored.articles
    result.article_refs = article_labels(scored.articles)
    result.trace.append(f"Verdict: {result.risk_tier.value} (score={result.score:.2f})")
    return result


def run_documentation_gap(corpus: str, files: list[str]) -> AgentResult:
    started = _now()
    result = AgentResult(
        agent=AgentName.documentation_gap,
        status=AgentStatus.running,
        started_at=started,
        trace=["Checking Annex IV / Art. 11–14 documentation artefacts"],
    )
    scored = score_documentation(corpus, files)
    result.status = AgentStatus.completed
    result.finished_at = _now()
    result.risk_tier = _tier(scored.risk_tier.value)
    result.score = scored.score
    result.rationale = scored.rationale
    result.findings = _map_findings(scored.findings)
    result.articles = scored.articles
    result.article_refs = article_labels(scored.articles)
    result.trace.append(f"Gaps found: {len(result.findings)}")
    return result


def run_bias_auditor(corpus: str) -> AgentResult:
    started = _now()
    result = AgentResult(
        agent=AgentName.bias_auditor,
        status=AgentStatus.running,
        started_at=started,
        trace=["Examining Art. 10 data governance & fairness signals"],
    )
    scored = score_bias(corpus)
    result.status = AgentStatus.completed
    result.finished_at = _now()
    result.risk_tier = _tier(scored.risk_tier.value)
    result.score = scored.score
    result.rationale = scored.rationale
    result.findings = _map_findings(scored.findings)
    result.articles = scored.articles
    result.article_refs = article_labels(scored.articles)
    result.trace.append(f"Bias findings: {len(result.findings)}")
    return result


def run_red_team(corpus: str) -> AgentResult:
    started = _now()
    result = AgentResult(
        agent=AgentName.red_team,
        status=AgentStatus.running,
        started_at=started,
        trace=["Probing Art. 15 robustness / cybersecurity attack surface"],
    )
    scored = score_red_team(corpus)
    result.status = AgentStatus.completed
    result.finished_at = _now()
    result.risk_tier = _tier(scored.risk_tier.value)
    result.score = scored.score
    result.rationale = scored.rationale
    result.findings = _map_findings(scored.findings)
    result.articles = scored.articles
    result.article_refs = article_labels(scored.articles)
    result.trace.append(f"Attack vectors surfaced: {len(result.findings)}")
    return result


def run_report_generator(
    label: str,
    target_path: str,
    agent_results: list[AgentResult],
    self_audit: bool,
) -> tuple[str, dict, list[str], RiskTier]:
    """Compose Markdown + JSON audit bundle from specialist outputs."""
    tier_rank = {
        RiskTier.prohibited: 4,
        RiskTier.high: 3,
        RiskTier.limited: 2,
        RiskTier.minimal: 1,
        RiskTier.unclassified: 0,
    }
    overall = RiskTier.minimal
    for a in agent_results:
        if a.risk_tier and tier_rank[a.risk_tier] > tier_rank[overall]:
            overall = a.risk_tier

    all_findings = [f for a in agent_results for f in a.findings if f.severity != "info"]
    remediations: list[str] = []
    for f in sorted(all_findings, key=lambda x: {"critical": 0, "high": 1, "medium": 2}.get(x.severity, 3)):
        if f.remediation not in remediations:
            remediations.append(f.remediation)
        if len(remediations) >= 5:
            break

    articles = sorted({art for a in agent_results for art in a.articles})
    article_refs = []
    seen = set()
    for a in agent_results:
        for ref in a.article_refs:
            if ref["id"] not in seen:
                article_refs.append(ref)
                seen.add(ref["id"])

    title = "Aegis Self-Audit" if self_audit else "Aegis Conformity Assessment Draft"
    lines = [
        f"# {title}",
        "",
        f"**Target:** `{target_path}`  ",
        f"**Label:** {label}  ",
        f"**Overall risk tier:** `{overall.value}`  ",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}  ",
        "",
        "> Draft conformity assessment for demonstration — not legal advice.",
        "",
        "## Executive summary",
        "",
        f"Aegis ran {len(agent_results)} specialist agents against the target corpus. "
        f"The aggregate classification is **{overall.value}** with "
        f"{len(all_findings)} actionable finding(s) mapped to {len(articles)} EU AI Act article(s).",
        "",
        "## Top remediations",
        "",
    ]
    if remediations:
        for i, r in enumerate(remediations[:3], 1):
            lines.append(f"{i}. {r}")
    else:
        lines.append("1. Maintain monitoring and documentation hygiene.")
    lines.extend(["", "## Agent verdicts", ""])
    for a in agent_results:
        lines.extend(
            [
                f"### {a.agent.value}",
                "",
                f"- Status: `{a.status.value}`",
                f"- Risk tier: `{a.risk_tier.value if a.risk_tier else 'n/a'}`",
                f"- Score: `{a.score if a.score is not None else 'n/a'}`",
                f"- Rationale: {a.rationale}",
                "",
            ]
        )
        if a.findings:
            lines.append("| Code | Severity | Evidence | Articles |")
            lines.append("| --- | --- | --- | --- |")
            for f in a.findings:
                lines.append(
                    f"| `{f.code}` | {f.severity} | {f.evidence.replace('|', '/')} | "
                    f"{', '.join(f.articles)} |"
                )
            lines.append("")

    lines.extend(["## EU AI Act articles referenced", ""])
    for ref in article_refs:
        lines.append(f"- **{ref['id']} — {ref['title']}:** {ref['summary']}")
    lines.extend(
        [
            "",
            "## Human oversight note",
            "",
            "This draft must be reviewed by a qualified human before any compliance claim. "
            "Aegis does not replace legal counsel, notified-body assessment, or organisational governance.",
            "",
        ]
    )
    if self_audit:
        lines.extend(
            [
                "## Self-audit reflection",
                "",
                "Aegis analysed its own agent definitions and orchestration surface. "
                "Treat Aegis itself as an AI system used in a professional advisory context: "
                "disclose AI involvement to clients, keep humans in the loop on conclusions, "
                "and retain the audit trail for accountability.",
                "",
            ]
        )

    markdown = "\n".join(lines)
    payload = {
        "title": title,
        "label": label,
        "target_path": target_path,
        "self_audit": self_audit,
        "overall_risk_tier": overall.value,
        "articles": articles,
        "article_refs": article_refs,
        "top_remediations": remediations[:5],
        "agents": [a.model_dump(mode="json") for a in agent_results],
        "disclaimer": "Draft conformity assessment for demonstration — not legal advice.",
    }
    return markdown, payload, remediations[:5], overall
