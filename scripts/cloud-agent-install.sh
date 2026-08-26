#!/usr/bin/env bash
# Idempotent Cloud Agent install for Aegis Governance Lab.
set -euo pipefail

export PATH="${HOME}/.local/bin:${PATH}"

resolve_root() {
  if [[ -f "/workspace/apps/api/main.py" ]]; then
    echo "/workspace"
  elif [[ -f "/agent/apps/api/main.py" ]]; then
    echo "/agent"
  elif [[ -f "./apps/api/main.py" ]]; then
    pwd
  else
    echo ""
  fi
}

ROOT="$(resolve_root)"

if [[ -z "$ROOT" ]]; then
  echo "[aegis] source tree missing — cloning public repo"
  CLONE_DIR="${AEGIS_CLONE_DIR:-/workspace/aegis-cloud-agent}"
  mkdir -p "$(dirname "$CLONE_DIR")"
  if [[ ! -d "$CLONE_DIR/.git" ]]; then
    git clone --depth 1 --branch cursor/aegis-cloud-agent-2782 \
      https://github.com/Daniel-DDV/aegis-cloud-agent.git "$CLONE_DIR"
  else
    git -C "$CLONE_DIR" fetch --depth 1 origin cursor/aegis-cloud-agent-2782 || true
    git -C "$CLONE_DIR" checkout cursor/aegis-cloud-agent-2782 || true
    git -C "$CLONE_DIR" pull --ff-only origin cursor/aegis-cloud-agent-2782 || true
  fi
  ROOT="$CLONE_DIR"
fi

cd "$ROOT"
echo "[aegis] install starting from $ROOT"

python3 -m pip install --upgrade pip
python3 -m pip install -e "$ROOT/packages/rubric"
python3 -m pip install -r "$ROOT/apps/api/requirements.txt"
python3 -m pip install -e "$ROOT/apps/api"

# Materialize package-lock.json from compressed vendor blob when absent.
if [[ ! -f "$ROOT/apps/dashboard/package-lock.json" && -f "$ROOT/apps/dashboard/package-lock.json.gz.b64" ]]; then
  base64 -d "$ROOT/apps/dashboard/package-lock.json.gz.b64" | gzip -d > "$ROOT/apps/dashboard/package-lock.json"
  echo "[aegis] inflated package-lock.json ($(wc -c < "$ROOT/apps/dashboard/package-lock.json") bytes)"
fi

if [[ -f "$ROOT/apps/dashboard/package-lock.json" ]]; then
  if ! (cd "$ROOT/apps/dashboard" && npm ci); then
    echo "[aegis] npm ci failed; falling back to npm install"
    (cd "$ROOT/apps/dashboard" && npm install)
  fi
else
  (cd "$ROOT/apps/dashboard" && npm install)
fi

mkdir -p "$ROOT/reports"
echo "$ROOT" > /tmp/aegis-root
# Corpus is already vendored under corpus/eu-ai-act — nothing to download for offline demos.

echo "[aegis] install complete"
python3 -c "import fastapi, uvicorn, rubric; print('python ok', fastapi.__version__)"
node -v
npm -v
