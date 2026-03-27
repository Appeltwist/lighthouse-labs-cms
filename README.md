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
