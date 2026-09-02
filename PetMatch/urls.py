from django.contrib import admin
from django.urls import path
from web import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index_view, name="index"),
    path("backoffice/", views.backoffice_view, name="backoffice"),
    path("api/match/", views.api_match_view, name="api_match"),
    path("api/pet/<int:pet_id>/", views.pet_detail_api, name="api_pet_detail"),
]
