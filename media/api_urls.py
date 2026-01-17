"""API URLs for media details."""

from django.urls import path

from media import api_views

urlpatterns = [
    path('details/<str:media_type>/<int:tmdb_id>/', api_views.media_details_api, name='media_details_api'),
]
