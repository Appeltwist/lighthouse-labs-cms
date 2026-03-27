from django.urls import path

from api.views import HomeAPIView, NarrativePageAPIView, SiteConfigAPIView


urlpatterns = [
    path("site-config", SiteConfigAPIView.as_view(), name="site_config"),
    path("home", HomeAPIView.as_view(), name="home"),
    path("pages/<slug:route_key>", NarrativePageAPIView.as_view(), name="narrative_page"),
]
