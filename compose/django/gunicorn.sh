#!/bin/sh
set -e

# Start SSH only in images that include an init script for it. Azure App Service
# health checks should not fail just because SSH support is unavailable.
if command -v service >/dev/null 2>&1 && service --status-all 2>/dev/null | grep -q '[[:space:]]ssh$'; then
    service ssh start || true
fi

# Azure custom containers do not always provide PORT. Listen on WEBSITES_PORT
# when configured, otherwise default to the Dockerfile's exposed HTTP port.
BIND_PORT="${PORT:-${WEBSITES_PORT:-80}}"
WORKERS="${GUNICORN_WORKERS:-4}"
TIMEOUT="${GUNICORN_TIMEOUT:-60}"
LOG_LEVEL="${GUNICORN_LOG_LEVEL:-info}"

exec gunicorn config.wsgi:application \
    --workers="$WORKERS" \
    --bind="0.0.0.0:${BIND_PORT}" \
    --timeout="$TIMEOUT" \
    --log-level="$LOG_LEVEL"
