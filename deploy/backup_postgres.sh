#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/var/backups/lighthouse-labs-cms}"
KEEP_DAYS="${KEEP_DAYS:-14}"
DB_NAME="${DB_NAME:-lighthouse_labs}"
DB_USER="${DB_USER:-lighthouse_labs}"
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-5432}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

install -d -m 0755 "${BACKUP_DIR}"
export PGPASSWORD="${DB_PASSWORD:-}"

pg_dump \
  -Fc \
  -h "${DB_HOST}" \
  -p "${DB_PORT}" \
  -U "${DB_USER}" \
  -d "${DB_NAME}" \
  -f "${BACKUP_DIR}/${DB_NAME}-${TIMESTAMP}.dump"

find "${BACKUP_DIR}" -type f -name "${DB_NAME}-*.dump" -mtime +"${KEEP_DAYS}" -delete

echo "Backup written to ${BACKUP_DIR}/${DB_NAME}-${TIMESTAMP}.dump"
