#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MEDIA_DIR="${MEDIA_DIR:-${ROOT_DIR}/media}"

if [[ -z "${AWS_STORAGE_BUCKET_NAME:-}" || -z "${AWS_S3_ENDPOINT_URL:-}" ]]; then
  echo "Set AWS_STORAGE_BUCKET_NAME and AWS_S3_ENDPOINT_URL before running this script."
  exit 1
fi

if ! command -v aws >/dev/null 2>&1; then
  echo "aws CLI is required."
  exit 1
fi

aws s3 sync "${MEDIA_DIR}/" "s3://${AWS_STORAGE_BUCKET_NAME}/" \
  --endpoint-url "${AWS_S3_ENDPOINT_URL}" \
  --delete

echo "Media sync complete."
