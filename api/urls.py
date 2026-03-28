from django.urls import path

from api.views import HomeAPIView, PageAPIView, PersonDetailAPIView, ProjectDetailAPIView, SiteConfigAPIView


urlpatterns = [
    path("site-config", SiteConfigAPIView.as_view(), name="site_config"),
    path("home", HomeAPIView.as_view(), name="home"),
    path("pages/<slug:route_key>", PageAPIView.as_view(), name="page"),
    path("projects/<slug:slug>", ProjectDetailAPIView.as_view(), name="project_detail"),
    path("people/<slug:slug>", PersonDetailAPIView.as_view(), name="person_detail"),
]
