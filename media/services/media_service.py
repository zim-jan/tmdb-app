"""
Media service layer for business logic.

This module contains service classes for managing media objects
and integrating with TMDb API.
"""

import contextlib
from datetime import datetime
from typing import Any

from django.db import transaction

from media.factories import MediaFactoryProvider
from media.models import Media
from media.services.tmdb_service import TMDbService


class MediaService:
    """
    Service for managing media objects.

    This service provides business logic for creating, updating,
    and retrieving media objects using the Abstract Factory pattern.
    """

    def __init__(self) -> None:
        """Initialize media service."""
        self.tmdb_service = TMDbService()

    @transaction.atomic
    def create_media_from_tmdb(self, tmdb_id: int, media_type: str) -> Media:
        """
        Create media object from TMDb data.

        Parameters
        ----------
        tmdb_id : int
            TMDb identifier for the media.
        media_type : str
            Type of media ("MOVIE" or "TV_SHOW").

        Returns
        -------
        Media
            Created media object.

        Raises
        ------
        ValueError
            If media_type is invalid or TMDb data is unavailable.
        """
        # Check if media already exists
        existing_media = Media.objects.filter(tmdb_id=tmdb_id, media_type=media_type).first()
        if existing_media:
            return existing_media

        # Fetch data from TMDb
        if media_type == "MOVIE":
            tmdb_data = self.tmdb_service.get_movie_details(tmdb_id)
        elif media_type == "TV_SHOW":
            tmdb_data = self.tmdb_service.get_tv_details(tmdb_id)
        else:
            raise ValueError(f"Invalid media type: {media_type}")

        # Get appropriate factory
        factory = MediaFactoryProvider.get_factory(media_type)

        # Prepare common data
        media_data = self._parse_tmdb_data(tmdb_data, media_type)

        # Create media using factory
        return factory.create_media(**media_data)

    def _parse_tmdb_data(self, tmdb_data: dict[str, Any], media_type: str) -> dict[str, Any]:
        """
        Parse TMDb API data into model fields.

        Parameters
        ----------
        tmdb_data : dict[str, Any]
            Raw data from TMDb API.
        media_type : str
            Type of media ("MOVIE" or "TV_SHOW").

        Returns
        -------
        dict[str, Any]
            Parsed data ready for model creation.
        """
        # Parse release date
        release_date_str = tmdb_data.get("release_date") or tmdb_data.get("first_air_date")
        release_date = None
        if release_date_str:
            with contextlib.suppress(ValueError):
                release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date()

        # Common fields
        data: dict[str, Any] = {
            "tmdb_id": tmdb_data["id"],
            "title": tmdb_data.get("title") or tmdb_data.get("name", ""),
            "original_title": tmdb_data.get("original_title") or tmdb_data.get("original_name", ""),
            "overview": tmdb_data.get("overview", ""),
            "poster_path": tmdb_data.get("poster_path", ""),
            "backdrop_path": tmdb_data.get("backdrop_path", ""),
            "release_date": release_date,
            "popularity": tmdb_data.get("popularity", 0.0),
            "vote_average": tmdb_data.get("vote_average", 0.0),
            "vote_count": tmdb_data.get("vote_count", 0),
            "original_language": tmdb_data.get("original_language", ""),
        }

        # Movie-specific fields
        if media_type == "MOVIE":
            data["runtime"] = tmdb_data.get("runtime")
            data["budget"] = tmdb_data.get("budget", 0)
            data["revenue"] = tmdb_data.get("revenue", 0)

        # TV Show-specific fields
        elif media_type == "TV_SHOW":
            data["number_of_seasons"] = tmdb_data.get("number_of_seasons", 0)
            data["number_of_episodes"] = tmdb_data.get("number_of_episodes", 0)

            episode_run_times = tmdb_data.get("episode_run_time", [])
            data["episode_run_time"] = episode_run_times[0] if episode_run_times else None

            data["status"] = tmdb_data.get("status", "")

            # Parse dates
            first_air_date_str = tmdb_data.get("first_air_date")
            if first_air_date_str:
                try:
                    data["first_air_date"] = datetime.strptime(first_air_date_str, "%Y-%m-%d").date()
                except ValueError:
                    data["first_air_date"] = None

            last_air_date_str = tmdb_data.get("last_air_date")
            if last_air_date_str:
                try:
                    data["last_air_date"] = datetime.strptime(last_air_date_str, "%Y-%m-%d").date()
                except ValueError:
                    data["last_air_date"] = None

        return data

    def search_media(self, query: str, media_type: str | None = None, enrich: bool = True) -> list[dict[str, Any]]:
        """
        Search for media by title.

        Parameters
        ----------
        query : str
            Search query.
        media_type : str | None
            Type of media to search ("movie", "tv", or None for both).
        enrich : bool
            Whether to enrich results with additional details (credits, images).

        Returns
        -------
        list[dict[str, Any]]
            List of search results from TMDb.
        """
        results: list[dict[str, Any]] = []

        # Normalize media_type to uppercase format
        normalized_type = None
        if media_type:
            if media_type.lower() == "movie":
                normalized_type = "MOVIE"
            elif media_type.lower() == "tv":
                normalized_type = "TV_SHOW"

        if normalized_type is None or normalized_type == "MOVIE":
            movie_results = self.tmdb_service.search_movie(query)
            for result in movie_results:
                result["media_type"] = "movie"
                result["title"] = result.get("title", "")
                result["rating"] = result.get("vote_average", 0)
                # Enrich with credits and images if requested
                if enrich:
                    result = self.tmdb_service.enrich_search_result(result, "movie")
            results.extend(movie_results)

        if normalized_type is None or normalized_type == "TV_SHOW":
            tv_results = self.tmdb_service.search_tv_show(query)
            for result in tv_results:
                result["media_type"] = "tv"
                result["title"] = result.get("name", "")
                result["rating"] = result.get("vote_average", 0)
                # Enrich with credits and images if requested
                if enrich:
                    result = self.tmdb_service.enrich_search_result(result, "tv")
            results.extend(tv_results)

        return results

    @transaction.atomic
    def update_media_metadata(self, media: Media) -> Media:
        """
        Update media metadata from TMDb.

        Parameters
        ----------
        media : Media
            Media object to update.

        Returns
        -------
        Media
            Updated media object.
        """
        # Fetch fresh data from TMDb
        tmdb_data = self.tmdb_service.get_movie_details(media.tmdb_id) if media.media_type == "MOVIE" else self.tmdb_service.get_tv_details(media.tmdb_id)

        # Parse and update
        parsed_data = self._parse_tmdb_data(tmdb_data, media.media_type)

        for field, value in parsed_data.items():
            setattr(media, field, value)

        media.save()
        return media
