"""SQLite audit trail for Aegis scans."""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

from aegis.models.schemas import ScanRecord

DB_PATH = Path(os.getenv("AEGIS_DB_PATH", Path(__file__).resolve().parents[3] / "reports" / "aegis.db"))


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS scans (
                id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_scan(scan: ScanRecord) -> None:
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO scans (id, payload, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              payload=excluded.payload,
              updated_at=excluded.updated_at
            """,
            (
                scan.id,
                scan.model_dump_json(),
                scan.created_at.isoformat(),
                scan.updated_at.isoformat(),
            ),
        )
        conn.commit()


def get_scan(scan_id: str) -> ScanRecord | None:
    with _conn() as conn:
        row = conn.execute("SELECT payload FROM scans WHERE id = ?", (scan_id,)).fetchone()
    if not row:
        return None
    return ScanRecord.model_validate_json(row["payload"])


def list_scans(limit: int = 50) -> list[ScanRecord]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT payload FROM scans ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [ScanRecord.model_validate_json(r["payload"]) for r in rows]


def export_scan_files(scan: ScanRecord, out_dir: Path | None = None) -> dict[str, str]:
    base = out_dir or (DB_PATH.parent / scan.id)
    base.mkdir(parents=True, exist_ok=True)
    md_path = base / "report.md"
    json_path = base / "report.json"
    if scan.report_markdown:
        md_path.write_text(scan.report_markdown, encoding="utf-8")
    json_path.write_text(
        json.dumps(scan.report_json or scan.model_dump(mode="json"), indent=2),
        encoding="utf-8",
    )
    return {"markdown": str(md_path), "json": str(json_path)}
