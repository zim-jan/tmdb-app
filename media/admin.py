"""Admin configuration for media app."""

from django.contrib import admin

from media.models import Media, Movie, TVShow, WatchedEpisode


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    """Admin interface for Media model."""

    list_display = ["title", "media_type", "release_date", "popularity", "created_at"]
    list_filter = ["media_type", "release_date", "created_at"]
    search_fields = ["title", "original_title", "tmdb_id"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """Admin interface for Movie model."""

    list_display = ["title", "release_date", "runtime", "popularity", "created_at"]
    list_filter = ["release_date", "created_at"]
    search_fields = ["title", "original_title", "tmdb_id"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(TVShow)
class TVShowAdmin(admin.ModelAdmin):
    """Admin interface for TVShow model."""

    list_display = ["title", "number_of_seasons", "number_of_episodes", "status", "created_at"]
    list_filter = ["status", "first_air_date", "created_at"]
    search_fields = ["title", "original_title", "tmdb_id"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(WatchedEpisode)
class WatchedEpisodeAdmin(admin.ModelAdmin):
    """Admin interface for WatchedEpisode model."""

    list_display = ["user", "tv_show", "season_number", "episode_number", "watched_at"]
    list_filter = ["watched_at"]
    search_fields = ["user__username", "tv_show__title"]
    ordering = ["-watched_at"]
    readonly_fields = ["watched_at"]
