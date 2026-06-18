#!/bin/bash
# Rootlabs POC Data Portal — deploy script
#
# Usage:   VPS_HOST=portal.rootlabs.co VPS_USER=deploy ./portal/deploy.sh
# Expects: VPS already provisioned with Docker + Docker Compose,
#          .env present at $VPS_PATH/portal/.env (NOT synced — copy manually once),
#          DNS A record pointing to the VPS,
#          $VPS_PATH/_private/ already populated with Supabase creds (copy manually once).
#
# Run from the observer-test repo root.

set -euo pipefail

VPS_HOST="${VPS_HOST:?Set VPS_HOST=<ip-or-hostname>}"
VPS_USER="${VPS_USER:-deploy}"
VPS_PATH="${VPS_PATH:-/opt/observer-test}"

echo "→ syncing repo to $VPS_USER@$VPS_HOST:$VPS_PATH ..."
rsync -avz --delete \
  --exclude='.git/' \
  --exclude='.venv/' \
  --exclude='**/.venv/' \
  --exclude='**/__pycache__/' \
  --exclude='**/node_modules/' \
  --exclude='UI data.bak/' \
  --exclude='ui-data/' \
  --exclude='apps/' \
  --exclude='hackathonkit/' \
  --exclude='cmo-agent/' \
  --exclude='cmo-agent*/' \
  --exclude='_private/' \
  --exclude='_research/' \
  --exclude='*.tar.gz' \
  --exclude='*.zip' \
  --exclude='archive/' \
  ./ "$VPS_USER@$VPS_HOST:$VPS_PATH/"

echo "→ verifying .env + _private/ exist on VPS (NOT synced; you set these once) ..."
ssh "$VPS_USER@$VPS_HOST" "test -f $VPS_PATH/portal/.env && test -d $VPS_PATH/_private || (echo 'MISSING: portal/.env and/or _private/. Copy manually and rerun.' && exit 1)"

echo "→ building + restarting Docker Compose ..."
ssh "$VPS_USER@$VPS_HOST" "cd $VPS_PATH/portal && docker compose up -d --build"

echo "→ waiting for /healthz ..."
for i in 1 2 3 4 5 6 7 8 9 10; do
    if ssh "$VPS_USER@$VPS_HOST" "curl -fsS http://localhost/healthz" >/dev/null 2>&1; then
        echo "✓ portal up at https://$VPS_HOST/healthz"
        exit 0
    fi
    sleep 3
done

echo "✗ /healthz never returned 200. Check logs:"
echo "  ssh $VPS_USER@$VPS_HOST 'cd $VPS_PATH/portal && docker compose logs --tail=80'"
exit 1
