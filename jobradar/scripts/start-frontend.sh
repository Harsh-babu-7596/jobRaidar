#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/frontend"

if [[ ! -d node_modules ]]; then
  echo "Installing frontend dependencies…"
  npm install
fi

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created frontend/.env from .env.example"
fi

exec npm run dev
