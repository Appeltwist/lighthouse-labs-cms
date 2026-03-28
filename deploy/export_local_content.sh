#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${1:-${ROOT_DIR}/backups/$(date +%Y%m%d-%H%M%S)}"

mkdir -p "${OUTPUT_DIR}"

cd "${ROOT_DIR}"

export DB_ENGINE="${DB_ENGINE:-django.db.backends.sqlite3}"
export DB_NAME="${DB_NAME:-${ROOT_DIR}/db.sqlite3}"

python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --exclude auth.permission \
  --exclude auth.group \
  --exclude contenttypes \
  --exclude sessions \
  --exclude admin.logentry \
  --exclude wagtailcore.groupapprovaltask \
  --exclude wagtailcore.groupcollectionpermission \
  --exclude wagtailcore.grouppagepermission \
  --exclude wagtailcore.modellogentry \
  --exclude wagtailcore.pagelogentry \
  --exclude wagtailcore.pagesubscription \
  --exclude wagtailcore.referenceindex \
  --exclude wagtailcore.task \
  --exclude wagtailcore.workflow \
  --exclude wagtailcore.workflowpage \
  --exclude wagtailcore.workflowtask \
  --exclude wagtailsearch \
  --indent 2 \
  > "${OUTPUT_DIR}/content.json"

if [[ -d "${ROOT_DIR}/media" ]]; then
  COPYFILE_DISABLE=1 tar -czf "${OUTPUT_DIR}/media.tar.gz" -C "${ROOT_DIR}" media
fi

if [[ -f "${ROOT_DIR}/db.sqlite3" ]]; then
  cp "${ROOT_DIR}/db.sqlite3" "${OUTPUT_DIR}/db.sqlite3"
fi

echo "Export complete: ${OUTPUT_DIR}"
