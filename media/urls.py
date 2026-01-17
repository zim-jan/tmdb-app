"""
URLs for media app.

This module defines URL patterns for media browsing and management.
"""

from django.urls import path

from media import views

app_name = "media"

urlpatterns = [
    path("browse/", views.browse_view, name="browse"),
    path("search/", views.search_view, name="search"),
    path("add-manual/", views.add_manual_media_view, name="add_manual"),
    path("<int:media_id>/", views.media_detail_view, name="detail"),
    path("add-to-list/", views.add_to_list_view, name="add_to_list"),
    path("tv/<int:tv_show_id>/mark-watched/", views.mark_episode_watched_view, name="mark_watched"),
    path("tv/<int:tv_show_id>/unmark-watched/", views.unmark_episode_watched_view, name="unmark_watched"),
    path("watch-history/", views.watch_history_view, name="watch_history"),
]
