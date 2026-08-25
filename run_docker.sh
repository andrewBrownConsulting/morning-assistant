#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -f .env ]] || ! grep -q '^CLOUDFLARE_TUNNEL_TOKEN=.' .env; then
  echo "Missing CLOUDFLARE_TUNNEL_TOKEN in .env. Create a Cloudflare Tunnel token first." >&2
  echo "See .env.example for the expected format." >&2
  exit 1
fi

cron_job='0 6 * * * curl -fsS -X POST http://localhost:8000/run > /tmp/bbc-news-cron.log 2>&1 || true'
if ! crontab -l 2>/dev/null | grep -Fqx "$cron_job"; then
  (crontab -l 2>/dev/null; echo "$cron_job") | crontab -
fi

docker compose build

docker compose up -d

echo "Home assistant app is running."
echo "Access Home Assistant at http://localhost:8123"
echo "Remote access is provided by the configured Cloudflare Tunnel."
echo "BBC News app is running."
echo "Daily cron trigger: 06:00 -> POST http://localhost:8000/run"
echo "Endpoints:"
echo "  http://localhost:8000/run"
echo "  http://localhost:8000/stop"
echo "  http://localhost:8000/status"
echo "  http://localhost:8000/headlines"
echo "  http://localhost:8000/test-audio"
