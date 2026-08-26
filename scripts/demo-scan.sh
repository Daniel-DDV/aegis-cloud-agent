#!/usr/bin/env bash
# 60-second wow demo for Aegis.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

API_URL="${AEGIS_API_URL:-http://127.0.0.1:8000}"
TARGET="samples/municipal-chatbot-stub"
SELF=0
LABEL="Municipal citizen chatbot (Mai-inspired stub)"

usage() {
  cat <<EOF
Usage: ./scripts/demo-scan.sh [--target PATH] [--self] [--api URL]

  --target PATH   Directory to scan (default: samples/municipal-chatbot-stub)
  --self          Self-audit Aegis itself
  --api URL       API base URL (default: $API_URL)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --self) SELF=1; TARGET="."; LABEL="Aegis self-audit"; shift ;;
    --api) API_URL="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 1 ;;
  esac
done

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Aegis — EU AI Act multi-agent governance demo           ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo "API:    $API_URL"
echo "Target: $TARGET"
echo

# Prefer sync endpoint so the script prints a finished report.
BODY=$(python3 - <<PY
import json
print(json.dumps({
  "target_path": "$TARGET",
  "label": "$LABEL",
  "self_audit": bool($SELF),
  "metadata": {
    "is_chatbot": True if $SELF == 0 else False,
    "annex_iii_domains": ["essential_services"],
  },
}))
PY
)

if curl -sf "$API_URL/health" >/dev/null 2>&1; then
  echo "→ Calling live API (sync scan)…"
  RESP=$(curl -sf -X POST "$API_URL/api/scans/sync" \
    -H "Content-Type: application/json" \
    -d "$BODY")
  python3 - <<'PY' "$RESP"
import json, sys
scan = json.loads(sys.argv[1])
print()
print(f"Scan ID:     {scan['id']}")
print(f"Status:      {scan['status']}")
print(f"Risk tier:   {scan.get('overall_risk_tier')}")
print("Top remediations:")
for i, r in enumerate(scan.get("top_remediations") or [], 1):
    print(f"  {i}. {r}")
print()
print(f"Dashboard: http://127.0.0.1:3000")
print(f"Report:    reports/{scan['id']}/report.md")
print()
print("Disclaimer: Draft conformity assessment for demonstration — not legal advice.")
PY
else
  echo "→ API not running; executing in-process orchestrator…"
  export PYTHONPATH="$ROOT/packages:$ROOT/apps/api:${PYTHONPATH:-}"
  python3 - <<PY
from aegis.db import init_db
from aegis.models.schemas import ScanRequest
from aegis.services.orchestrator import create_scan, run_scan

init_db()
req = ScanRequest(
    target_path="$TARGET",
    label="$LABEL",
    self_audit=bool($SELF),
    metadata={
        "is_chatbot": $SELF == 0,
        "annex_iii_domains": ["essential_services"],
    },
)
scan = create_scan(req)
scan = run_scan(scan.id, req.metadata)
print()
print(f"Scan ID:     {scan.id}")
print(f"Status:      {scan.status.value}")
print(f"Risk tier:   {scan.overall_risk_tier.value if scan.overall_risk_tier else None}")
print("Top remediations:")
for i, r in enumerate(scan.top_remediations or [], 1):
    print(f"  {i}. {r}")
print()
print(f"Report: reports/{scan.id}/report.md")
print("Disclaimer: Draft conformity assessment for demonstration — not legal advice.")
PY
fi
