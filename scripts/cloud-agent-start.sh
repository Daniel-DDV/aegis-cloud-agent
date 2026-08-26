#!/usr/bin/env bash
# Per-boot start for Aegis API + dashboard (idempotent readiness, then return).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PATH="${HOME}/.local/bin:${PATH}"
export PYTHONPATH="${ROOT}/packages:${ROOT}/apps/api:${PYTHONPATH:-}"
mkdir -p "${ROOT}/reports" /tmp/aegis-logs

start_if_needed() {
  local name="$1"
  local port="$2"
  local cmd="$3"
  if curl -sf "http://127.0.0.1:${port}/health" >/dev/null 2>&1 || \
     curl -sf "http://127.0.0.1:${port}" >/dev/null 2>&1; then
    echo "[aegis] ${name} already up on :${port}"
    return 0
  fi
  echo "[aegis] starting ${name} on :${port}"
  nohup bash -lc "$cmd" >"/tmp/aegis-logs/${name}.log" 2>&1 &
  echo $! >"/tmp/aegis-logs/${name}.pid"
}

start_if_needed "aegis-api" 8000 \
  "cd '${ROOT}/apps/api' && PYTHONPATH='${ROOT}/packages:${ROOT}/apps/api' uvicorn main:app --host 0.0.0.0 --port 8000"

start_if_needed "aegis-dashboard" 3000 \
  "cd '${ROOT}/apps/dashboard' && npm run dev -- --port 3000 --hostname 0.0.0.0"

for i in $(seq 1 60); do
  api_ok=0
  dash_ok=0
  curl -sf "http://127.0.0.1:8000/health" >/dev/null 2>&1 && api_ok=1
  curl -sf "http://127.0.0.1:3000" >/dev/null 2>&1 && dash_ok=1
  if [[ "$api_ok" == "1" && "$dash_ok" == "1" ]]; then
    echo "[aegis] API and dashboard ready"
    exit 0
  fi
  sleep 1
done

echo "[aegis] start timed out; check /tmp/aegis-logs/" >&2
tail -n 40 /tmp/aegis-logs/*.log >&2 || true
exit 1
