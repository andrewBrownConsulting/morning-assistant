#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

docker compose build

docker compose up -d

echo "BBC News app is running."
echo "Endpoints:"
echo "  http://localhost:8000/run"
echo "  http://localhost:8000/stop"
echo "  http://localhost:8000/status"
echo "  http://localhost:8000/headlines"
