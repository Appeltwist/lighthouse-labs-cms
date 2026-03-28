# Lighthouse Labs CMS

Lighthouse Labs CMS is a foundation starter for a bilingual cinema and film website.

## Stack
- Django 5
- Wagtail 6
- PostgreSQL
- Django REST Framework

## Local setup
1. Add a local hostname to `/etc/hosts`:
   ```txt
   127.0.0.1 lighthouse-labs.local
   ```
2. Create and activate a virtualenv:
   ```bash
   /opt/homebrew/bin/python3.12 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and adjust the database settings if needed.
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Seed the starter site:
   ```bash
   python manage.py seed_lighthouse_labs_site
   ```
7. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
8. Start the server:
   ```bash
   python manage.py runserver
   ```

## Key URLs
- API root: `http://localhost:8000/api/`
- Wagtail admin: `http://localhost:8000/cms/`
- Django admin: `http://localhost:8000/django-admin/`
- Health: `http://localhost:8000/health/`

## Production deployment

Production is designed for:
- Django/Wagtail on a VPS behind `nginx + gunicorn`
- PostgreSQL on the VPS
- static files served by WhiteNoise
- uploaded media stored in Cloudflare R2 or another S3-compatible bucket

Key production files:
- `.env.production.example`
- `deploy/bootstrap_vps.sh`
- `deploy/deploy_cms.sh`
- `deploy/backup_postgres.sh`
- `deploy/export_local_content.sh`
- `deploy/import_content.sh`
- `deploy/sync_media_to_r2.sh`
- `deploy/lighthouse-labs-cms.service`
- `deploy/nginx.cms.lighthouse-labs.be.conf`

Suggested first production flow:
1. Push the repo to GitHub.
2. Add this machine's SSH key to the VPS.
3. Run `deploy/bootstrap_vps.sh` as `root` on the VPS.
4. Clone the repo to `/srv/lighthouse-labs-cms`.
5. Copy `.env.production.example` to `.env` and fill in real secrets.
6. Install the systemd and nginx templates from `deploy/`.
7. Run `deploy/deploy_cms.sh`.
8. Run `certbot --nginx -d cms.lighthouse-labs.be`.

## Content migration

To promote the current local content into production:
1. Export local content:
   ```bash
   ./deploy/export_local_content.sh
   ```
2. Import the JSON dump on the VPS after the production database is ready:
   ```bash
   SITE_HOSTNAME=lighthouse-labs.be ./deploy/import_content.sh /path/to/content.json
   ```
3. Sync the local `media/` directory to R2:
   ```bash
   ./deploy/sync_media_to_r2.sh
   ```
4. Create the production superuser:
   ```bash
   python manage.py createsuperuser
   ```
