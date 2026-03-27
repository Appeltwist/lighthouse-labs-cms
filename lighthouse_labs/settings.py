from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(key: str, default: bool = False) -> bool:
    return os.environ.get(key, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def env_list(key: str) -> list[str]:
    return [value.strip() for value in os.environ.get(key, "").split(",") if value.strip()]


SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-insecure-change-me")
DEBUG = env_bool("DJANGO_DEBUG", default=False)

allowed_hosts_env = env_list("DJANGO_ALLOWED_HOSTS")
if allowed_hosts_env:
    ALLOWED_HOSTS = allowed_hosts_env
elif DEBUG:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "::1", "0.0.0.0", "lighthouse-labs.local"]
else:
    ALLOWED_HOSTS = []

trusted_origins_env = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")
trusted_origins_from_hosts = [f"https://{host}" for host in ALLOWED_HOSTS if host and host != "*"]
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(trusted_origins_env + trusted_origins_from_hosts))

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "taggit",
    "modelcluster",
    "wagtail.contrib.forms",
    "wagtail.contrib.settings",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "rest_framework",
    "pages.apps.PagesConfig",
    "siteconfig.apps.SiteconfigConfig",
    "api.apps.ApiConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "lighthouse_labs.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "lighthouse_labs.wsgi.application"
ASGI_APPLICATION = "lighthouse_labs.asgi.application"

database_engine = os.environ.get("DB_ENGINE", "django.db.backends.postgresql")
if database_engine == "django.db.backends.sqlite3":
    database_name = os.environ.get("DB_NAME", str(BASE_DIR / "db.sqlite3"))
else:
    database_name = os.environ.get("DB_NAME", "lighthouse_labs")

DATABASES = {
    "default": {
        "ENGINE": database_engine,
        "NAME": database_name,
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "postgres"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", "English"),
    ("fr", "French"),
]
TIME_ZONE = "Europe/Brussels"
USE_I18N = True
USE_TZ = True

SITE_ID = 1
WAGTAIL_SITE_NAME = "Lighthouse Labs"
WAGTAILADMIN_BASE_URL = os.environ.get("WAGTAILADMIN_BASE_URL", "http://localhost:8000")

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
