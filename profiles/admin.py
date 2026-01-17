"""Admin configuration for profiles app."""

from django.contrib import admin

from profiles.models import PublicProfile


@admin.register(PublicProfile)
class PublicProfileAdmin(admin.ModelAdmin):
    """Admin interface for PublicProfile model."""

    list_display = ["user", "is_visible", "show_watched_episodes", "show_lists", "created_at"]
    list_filter = ["is_visible", "show_watched_episodes", "show_lists", "created_at"]
    search_fields = ["user__username", "user__nickname"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]
