#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/srv/lighthouse-labs-cms}"
VENV_DIR="${VENV_DIR:-${APP_DIR}/.venv}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
BRANCH="${BRANCH:-main}"

cd "${APP_DIR}"

if [[ ! -d .git ]]; then
  echo "Expected a git checkout at ${APP_DIR}"
  exit 1
fi

git fetch origin
git checkout "${BRANCH}"
git pull --ff-only origin "${BRANCH}"

if [[ ! -d "${VENV_DIR}" ]]; then
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

python manage.py migrate --noinput
python manage.py collectstatic --noinput

sudo systemctl restart lighthouse-labs-cms
sudo systemctl reload nginx

echo "Deployment complete."
