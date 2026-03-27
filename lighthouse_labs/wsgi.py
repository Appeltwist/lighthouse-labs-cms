"""
WSGI config for lighthouse_labs project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from lighthouse_labs.env import load_env_file

load_env_file()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lighthouse_labs.settings')

application = get_wsgi_application()
