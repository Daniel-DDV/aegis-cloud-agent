#!/usr/bin/env bash
# Idempotent Cloud Agent install for Aegis Governance Lab.
set -euo pipefail

export PATH="${HOME}/.local/bin:${PATH}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "[aegis] install starting from $ROOT"

python3 -m pip install --upgrade pip
python3 -m pip install -e "$ROOT/packages/rubric"
python3 -m pip install -r "$ROOT/apps/api/requirements.txt"
python3 -m pip install -e "$ROOT/apps/api"

if [[ -f "$ROOT/apps/dashboard/package-lock.json" ]]; then
  (cd "$ROOT/apps/dashboard" && npm ci)
else
  (cd "$ROOT/apps/dashboard" && npm install)
fi

mkdir -p "$ROOT/reports"
# Corpus is already vendored under corpus/eu-ai-act — nothing to download for offline demos.

echo "[aegis] install complete"
python3 -c "import fastapi, uvicorn, rubric; print('python ok', fastapi.__version__)"
node -v
npm -v
