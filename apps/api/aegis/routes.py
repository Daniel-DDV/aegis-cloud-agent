"""HTTP routes for Aegis."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException

from aegis.db import get_scan, list_scans
from aegis.models.schemas import ScanRecord, ScanRequest, ScanSummary
from aegis.services.orchestrator import REPO_ROOT, create_scan, run_scan

router = APIRouter(prefix="/api")


def _run_in_background(scan_id: str, metadata: dict) -> None:
    run_scan(scan_id, metadata)


@router.post("/scans", response_model=ScanRecord)
def start_scan(req: ScanRequest, background: BackgroundTasks) -> ScanRecord:
    scan = create_scan(req)
    background.add_task(_run_in_background, scan.id, req.metadata)
    return get_scan(scan.id) or scan


@router.post("/scans/sync", response_model=ScanRecord)
def start_scan_sync(req: ScanRequest) -> ScanRecord:
    """Synchronous scan — used by demo-scan.sh and evals."""
    scan = create_scan(req)
    return run_scan(scan.id, req.metadata)


@router.get("/scans", response_model=list[ScanSummary])
def scans(limit: int = 50) -> list[ScanSummary]:
    return [
        ScanSummary(
            id=s.id,
            label=s.label,
            status=s.status,
            overall_risk_tier=s.overall_risk_tier,
            created_at=s.created_at,
            self_audit=s.self_audit,
        )
        for s in list_scans(limit)
    ]


@router.get("/scans/{scan_id}", response_model=ScanRecord)
def scan_detail(scan_id: str) -> ScanRecord:
    scan = get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


@router.get("/scans/{scan_id}/report.md")
def scan_report_md(scan_id: str):
    from fastapi.responses import PlainTextResponse

    scan = get_scan(scan_id)
    if not scan or not scan.report_markdown:
        raise HTTPException(status_code=404, detail="Report not found")
    return PlainTextResponse(scan.report_markdown, media_type="text/markdown")


@router.get("/meta")
def meta():
    return {
        "name": "Aegis",
        "purpose": "EU AI Act multi-agent governance lab",
        "repo_root": str(REPO_ROOT),
        "disclaimer": "Draft conformity assessment for demonstration — not legal advice.",
        "locales": ["en", "nl"],
        "agents": [
            "RiskClassifier",
            "DocumentationGap",
            "BiasAuditor",
            "RedTeam",
            "ReportGenerator",
        ],
    }
