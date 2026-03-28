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

python manage.py shell <<PY
from wagtail.models import Page, Site

site = Site.objects.exclude(hostname="localhost").order_by("-id").first() or Site.objects.order_by("-id").first()

if site and "${SITE_HOSTNAME:-}":
    Site.objects.exclude(id=site.id).delete()
    site.hostname = "${SITE_HOSTNAME}"
    site.port = 443
    site.site_name = "Lighthouse Labs"
    site.is_default_site = True
    site.save(update_fields=["hostname", "port", "site_name", "is_default_site"])

    default_page = Page.objects.filter(id=2).exclude(id=site.root_page_id)
    if default_page.exists():
        default_page.delete()
PY

python manage.py fixtree

echo "Content import complete."
