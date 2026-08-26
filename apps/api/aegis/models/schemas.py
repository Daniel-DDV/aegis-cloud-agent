"""Pydantic models for Aegis scans and agent outputs."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class RiskTier(str, Enum):
    prohibited = "prohibited"
    high = "high"
    limited = "limited"
    minimal = "minimal"
    unclassified = "unclassified"


class AgentName(str, Enum):
    risk_classifier = "RiskClassifier"
    documentation_gap = "DocumentationGap"
    bias_auditor = "BiasAuditor"
    red_team = "RedTeam"
    report_generator = "ReportGenerator"


class AgentStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class ScanRequest(BaseModel):
    target_path: str = Field(..., description="Path to directory or file to scan")
    label: str | None = Field(None, description="Human label for the scan target")
    metadata: dict[str, Any] = Field(default_factory=dict)
    self_audit: bool = False


class FindingOut(BaseModel):
    code: str
    title: str
    severity: str
    evidence: str
    articles: list[str]
    remediation: str


class AgentResult(BaseModel):
    agent: AgentName
    status: AgentStatus
    started_at: datetime | None = None
    finished_at: datetime | None = None
    risk_tier: RiskTier | None = None
    score: float | None = None
    rationale: str = ""
    findings: list[FindingOut] = Field(default_factory=list)
    articles: list[str] = Field(default_factory=list)
    article_refs: list[dict[str, Any]] = Field(default_factory=list)
    trace: list[str] = Field(default_factory=list)
    error: str | None = None


class ScanStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class ScanRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    label: str
    target_path: str
    self_audit: bool = False
    status: ScanStatus = ScanStatus.queued
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    overall_risk_tier: RiskTier | None = None
    agents: list[AgentResult] = Field(default_factory=list)
    report_markdown: str | None = None
    report_json: dict[str, Any] | None = None
    top_remediations: list[str] = Field(default_factory=list)
    disclaimer: str = (
        "Draft conformity assessment for demonstration — not legal advice."
    )


class ScanSummary(BaseModel):
    id: str
    label: str
    status: ScanStatus
    overall_risk_tier: RiskTier | None
    created_at: datetime
    self_audit: bool


class Locale(str, Enum):
    en = "en"
    nl = "nl"
