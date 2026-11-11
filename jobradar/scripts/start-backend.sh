#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/backend"

if [[ ! -d .venv ]]; then
  echo "Creating virtualenv…"
  if command -v uv >/dev/null 2>&1; then
    uv venv .venv
  else
    python3 -m venv .venv
  fi
fi

# shellcheck disable=SC1091
source .venv/bin/activate

if command -v uv >/dev/null 2>&1; then
  uv pip install -r requirements.txt
else
  pip install -q -r requirements.txt
fi

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created backend/.env from .env.example"
fi

exec python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
