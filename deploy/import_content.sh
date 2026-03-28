#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 /path/to/content.json"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONTENT_FILE="$1"

cd "${ROOT_DIR}"

python manage.py migrate --noinput
python manage.py loaddata "${CONTENT_FILE}"

if [[ -n "${SITE_HOSTNAME:-}" ]]; then
  python manage.py shell -c "from wagtail.models import Site; site = Site.objects.first(); site.hostname='${SITE_HOSTNAME}'; site.port=443; site.site_name='Lighthouse Labs'; site.save(update_fields=['hostname','port','site_name'])"
fi

echo "Content import complete."
