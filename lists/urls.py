"""
URLs for lists app.

This module defines URL patterns for list management.
"""

from django.urls import path

from lists import views

app_name = "lists"

urlpatterns = [
    path("", views.my_lists_view, name="my_lists"),
    path("create/", views.create_list_view, name="create"),
    path("<int:list_id>/", views.list_detail_view, name="detail"),
    path("<int:list_id>/edit/", views.edit_list_view, name="edit"),
    path("<int:list_id>/delete/", views.delete_list_view, name="delete"),
    path("<int:list_id>/remove/<int:media_id>/", views.remove_from_list_view, name="remove_item"),
    path("item/<int:item_id>/move/", views.move_item_view, name="move_item"),
    path("item/<int:item_id>/status/", views.update_item_status_view, name="update_status"),
]
