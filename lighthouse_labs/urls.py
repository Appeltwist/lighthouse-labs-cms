from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from api.views import health


urlpatterns = [
    path("health/", health, name="health"),
    path("api/", include("api.urls")),
    path("cms/documents/", include(wagtaildocs_urls)),
    path("cms/", include(wagtailadmin_urls)),
    path(
        "admin/",
        RedirectView.as_view(url="/django-admin/", permanent=False, query_string=True),
        name="django_admin_compat",
    ),
    re_path(
        r"^admin/(?P<path>.+)$",
        RedirectView.as_view(url="/django-admin/%(path)s", permanent=False, query_string=True),
    ),
    path("django-admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
