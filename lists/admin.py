"""Admin configuration for lists app."""

from django.contrib import admin

from lists.models import List, ListItem


@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    """Admin interface for List model."""

    list_display = ["name", "user", "is_public", "created_at"]
    list_filter = ["is_public", "created_at"]
    search_fields = ["name", "user__username"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(ListItem)
class ListItemAdmin(admin.ModelAdmin):
    """Admin interface for ListItem model."""

    list_display = ["media", "list", "position", "added_at"]
    list_filter = ["added_at"]
    search_fields = ["media__title", "list__name"]
    ordering = ["list", "position"]
    readonly_fields = ["added_at"]
