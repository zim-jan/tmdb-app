"""
URLs for profiles app.

This module defines URL patterns for public profiles.
"""

from django.urls import path

from profiles import views

app_name = "profiles"

urlpatterns = [
    path("u/<str:nickname>/", views.public_profile_view, name="public"),
    path("edit/", views.edit_profile_view, name="edit"),
]
