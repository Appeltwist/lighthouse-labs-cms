#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this script as root on the VPS."
  exit 1
fi

DEPLOY_USER="${DEPLOY_USER:-lighthouse}"
DEPLOY_HOME="/srv/lighthouse-labs-cms"
PYTHON_VERSION="${PYTHON_VERSION:-python3.12}"
POSTGRES_DB="${POSTGRES_DB:-lighthouse_labs}"
POSTGRES_USER="${POSTGRES_USER:-lighthouse_labs}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-change-me}"

apt-get update
apt-get install -y \
  nginx \
  postgresql \
  postgresql-contrib \
  git \
  curl \
  certbot \
  python3-certbot-nginx \
  python3-venv \
  python3-pip \
  ${PYTHON_VERSION}

if ! id -u "${DEPLOY_USER}" >/dev/null 2>&1; then
  adduser --system --group --home "${DEPLOY_HOME}" "${DEPLOY_USER}"
fi

install -d -m 0755 -o "${DEPLOY_USER}" -g "${DEPLOY_USER}" "${DEPLOY_HOME}"
install -d -m 0755 -o "${DEPLOY_USER}" -g "${DEPLOY_USER}" /var/log/lighthouse-labs-cms
install -d -m 0755 -o "${DEPLOY_USER}" -g "${DEPLOY_USER}" /var/backups/lighthouse-labs-cms

sudo -u postgres psql <<SQL
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${POSTGRES_USER}') THEN
      CREATE ROLE ${POSTGRES_USER} LOGIN PASSWORD '${POSTGRES_PASSWORD}';
   END IF;
END
\$\$;
SQL

if ! sudo -u postgres psql -Atqc "SELECT 1 FROM pg_database WHERE datname = '${POSTGRES_DB}'" | grep -q 1; then
  sudo -u postgres createdb --owner="${POSTGRES_USER}" "${POSTGRES_DB}"
fi

echo "Bootstrap complete."
echo "Next:"
echo "1. Clone the repo into ${DEPLOY_HOME}"
echo "2. Copy deploy templates into /etc/systemd/system and /etc/nginx/sites-available"
echo "3. Add /srv/lighthouse-labs-cms/.env"
echo "4. Run deploy/deploy_cms.sh as ${DEPLOY_USER}"
