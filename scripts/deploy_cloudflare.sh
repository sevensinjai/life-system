#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEFAULT_ENV_FILE="$(cd "$PROJECT_ROOT/.." && pwd)/tomchan/infra/.env"
ENV_FILE="${CLOUDFLARE_ENV_FILE:-$DEFAULT_ENV_FILE}"
WRANGLER_CONFIG="$PROJECT_ROOT/wrangler.jsonc"

if [ ! -f "$ENV_FILE" ]; then
  echo "Error: Cloudflare credentials not found at $ENV_FILE"
  echo "Set CLOUDFLARE_ENV_FILE to use a different file."
  exit 1
fi

source "$ENV_FILE"

if [ -z "${CLOUDFLARE_API_TOKEN:-}" ] || [ -z "${CLOUDFLARE_ACCOUNT_ID:-}" ]; then
  echo "Error: CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID are required"
  exit 1
fi

if grep -q "REPLACE_WITH_D1_DATABASE_ID" "$WRANGLER_CONFIG"; then
  echo "Error: create the D1 database, then put its database_id in wrangler.jsonc:"
  echo "  npx wrangler d1 create life-system"
  exit 1
fi

echo "Building the Cloudflare frontend..."
cd "$PROJECT_ROOT/web"
npm ci
LIFE_SYSTEM_CLOUDFLARE=1 npm run build

echo "Applying D1 migrations..."
cd "$PROJECT_ROOT"
CLOUDFLARE_API_TOKEN="$CLOUDFLARE_API_TOKEN" \
CLOUDFLARE_ACCOUNT_ID="$CLOUDFLARE_ACCOUNT_ID" \
npx wrangler d1 migrations apply life-system --remote

echo "Deploying the Python Worker and static assets..."
UV_CACHE_DIR="${UV_CACHE_DIR:-/private/tmp/life-system-uv-cache}" \
"$PROJECT_ROOT/.venv/bin/uv" sync --group worker
UV_CACHE_DIR="${UV_CACHE_DIR:-/private/tmp/life-system-uv-cache}" \
CLOUDFLARE_API_TOKEN="$CLOUDFLARE_API_TOKEN" \
CLOUDFLARE_ACCOUNT_ID="$CLOUDFLARE_ACCOUNT_ID" \
"$PROJECT_ROOT/.venv/bin/uv" run --group worker pywrangler deploy

echo "Done. Attach system.tomchan.uk to the life-system Worker if needed."
