#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

cron_job='0 6 * * * curl -fsS -X POST http://localhost:8000/run > /tmp/bbc-news-cron.log 2>&1 || true'
if ! crontab -l 2>/dev/null | grep -Fqx "$cron_job"; then
  (crontab -l 2>/dev/null; echo "$cron_job") | crontab -
fi

docker compose build

docker compose up -d

echo "BBC News app is running."
echo "Daily cron trigger: 06:00 -> POST http://localhost:8000/run"
echo "Endpoints:"
echo "  http://localhost:8000/run"
echo "  http://localhost:8000/stop"
echo "  http://localhost:8000/status"
echo "  http://localhost:8000/headlines"
