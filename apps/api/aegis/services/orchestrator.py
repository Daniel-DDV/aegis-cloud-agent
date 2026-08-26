"""Orchestrates parallel specialist agents for a scan."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from aegis.agents.runners import (
    run_bias_auditor,
    run_documentation_gap,
    run_red_team,
    run_report_generator,
    run_risk_classifier,
)
from aegis.db import export_scan_files, save_scan
from aegis.models.schemas import (
    AgentName,
    AgentResult,
    AgentStatus,
    ScanRecord,
    ScanRequest,
    ScanStatus,
)
from aegis.services.corpus import load_corpus

REPO_ROOT = Path(__file__).resolve().parents[4]


def _pending(name: AgentName) -> AgentResult:
    return AgentResult(agent=name, status=AgentStatus.pending)


def create_scan(req: ScanRequest) -> ScanRecord:
    target = Path(req.target_path)
    if not target.is_absolute():
        target = (REPO_ROOT / target).resolve()
    label = req.label or target.name
    if req.self_audit:
        label = f"Self-audit: {label}"

    scan = ScanRecord(
        label=label,
        target_path=str(target),
        self_audit=req.self_audit,
        status=ScanStatus.queued,
        agents=[
            _pending(AgentName.risk_classifier),
            _pending(AgentName.documentation_gap),
            _pending(AgentName.bias_auditor),
            _pending(AgentName.red_team),
            _pending(AgentName.report_generator),
        ],
    )
    save_scan(scan)
    return scan


def run_scan(scan_id: str, metadata: dict | None = None) -> ScanRecord:
    from aegis.db import get_scan

    scan = get_scan(scan_id)
    if scan is None:
        raise KeyError(scan_id)

    scan.status = ScanStatus.running
    scan.updated_at = datetime.now(timezone.utc)
    save_scan(scan)

    try:
        excludes: list[str] | None = None
        if scan.self_audit:
            # Avoid false positives from regulatory corpus, fixtures, and demo stubs.
            excludes = [
                "samples",
                "reports",
                "corpus",
                "packages/eval",
                "packages/rubric",
                "node_modules",
                ".git",
            ]
        corpus, files = load_corpus(scan.target_path, exclude_prefixes=excludes)
        meta = dict(metadata or {})
        if scan.self_audit:
            meta.setdefault("is_chatbot", False)
            # Aegis advises on essential public services → governance adjacency
            meta.setdefault("annex_iii_domains", ["essential_services"])
            # Inject an explicit self-description so documentation/oversight gaps are visible
            corpus = (
                "# Aegis self-description\n"
                "Aegis is a multi-agent EU AI Act governance assistant used in professional "
                "advisory contexts. It produces draft conformity assessments for humans to review.\n"
                "Human-in-the-loop is required before any compliance claim.\n\n"
            ) + corpus

        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {
                pool.submit(run_risk_classifier, corpus, meta, files): AgentName.risk_classifier,
                pool.submit(run_documentation_gap, corpus, files): AgentName.documentation_gap,
                pool.submit(run_bias_auditor, corpus): AgentName.bias_auditor,
                pool.submit(run_red_team, corpus): AgentName.red_team,
            }
            completed: dict[AgentName, AgentResult] = {}
            for fut in as_completed(futures):
                name = futures[fut]
                try:
                    completed[name] = fut.result()
                except Exception as exc:  # noqa: BLE001
                    completed[name] = AgentResult(
                        agent=name,
                        status=AgentStatus.failed,
                        error=str(exc),
                        finished_at=datetime.now(timezone.utc),
                    )

        ordered = [
            completed[AgentName.risk_classifier],
            completed[AgentName.documentation_gap],
            completed[AgentName.bias_auditor],
            completed[AgentName.red_team],
        ]

        report_agent = AgentResult(
            agent=AgentName.report_generator,
            status=AgentStatus.running,
            started_at=datetime.now(timezone.utc),
            trace=["Composing audit-ready Markdown + JSON bundle"],
        )
        md, payload, remediations, overall = run_report_generator(
            scan.label, scan.target_path, ordered, scan.self_audit
        )
        report_agent.status = AgentStatus.completed
        report_agent.finished_at = datetime.now(timezone.utc)
        report_agent.risk_tier = overall
        report_agent.rationale = "Audit bundle composed from specialist agent outputs."
        report_agent.trace.append("Report written to audit trail")
        report_agent.articles = payload["articles"]
        report_agent.article_refs = payload["article_refs"]

        scan.agents = ordered + [report_agent]
        scan.report_markdown = md
        scan.report_json = payload
        scan.top_remediations = remediations
        scan.overall_risk_tier = overall
        scan.status = ScanStatus.completed
        scan.updated_at = datetime.now(timezone.utc)
        save_scan(scan)
        export_scan_files(scan)
        return scan
    except Exception as exc:  # noqa: BLE001
        scan.status = ScanStatus.failed
        scan.updated_at = datetime.now(timezone.utc)
        if scan.agents:
            scan.agents[-1].status = AgentStatus.failed
            scan.agents[-1].error = str(exc)
        save_scan(scan)
        raise
