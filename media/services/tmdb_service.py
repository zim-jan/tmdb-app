"""
TMDb API integration service.

This module provides service layer for interacting with The Movie Database API.
"""

import logging
from typing import Any

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class TMDbService:
    """
    Service for interacting with The Movie Database (TMDb) API.

    This service handles all communication with TMDb API for fetching
    movie and TV show metadata with caching support.

    Attributes
    ----------
    api_key : str
        TMDb API key from settings.
    base_url : str
        Base URL for TMDb API.
    timeout : int
        Request timeout in seconds.
    cache_timeout : int
        Cache timeout in seconds.
    """

    def __init__(self) -> None:
        """Initialize TMDb service with API credentials."""
        self.api_key = settings.TMDB_API_KEY
        self.base_url = settings.TMDB_BASE_URL
        self.timeout = settings.TMDB_TIMEOUT
        self.cache_timeout = settings.TMDB_CACHE_TIMEOUT

        # Validate API key is configured
        if not self.api_key:
            logger.warning(
                "TMDB_API_KEY is not configured. "
                "Get your API key at https://www.themoviedb.org/settings/api"
            )

    def _get_cache_key(self, endpoint: str, params: dict[str, Any] | None) -> str:
        """
        Generate a cache key for API request.

        Parameters
        ----------
        endpoint : str
            API endpoint.
        params : dict[str, Any] | None
            Query parameters.

        Returns
        -------
        str
            Cache key.
        """
        # Exclude api_key from cache key for security
        params_copy = {k: v for k, v in (params or {}).items() if k != "api_key"}
        params_str = "|".join(f"{k}={v}" for k, v in sorted(params_copy.items()))
        return f"tmdb:{endpoint}:{params_str}"

    def _make_request(self, endpoint: str, params: dict[str, Any] | None = None, use_cache: bool = True) -> dict[str, Any]:
        """
        Make a request to TMDb API with optional caching.

        Parameters
        ----------
        endpoint : str
            API endpoint to call.
        params : dict[str, Any] | None
            Query parameters for the request.
        use_cache : bool
            Whether to use cached results (default: True).

        Returns
        -------
        dict[str, Any]
            JSON response from the API.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """
        if params is None:
            params = {}

        # Validate API key before making request
        if not self.api_key:
            raise ValueError(
                "TMDB_API_KEY is not configured. "
                "Get your API key at https://www.themoviedb.org/settings/api"
            )

        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(endpoint, params)
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        params["api_key"] = self.api_key
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()

        result = response.json()

        # Cache successful response
        if use_cache:
            cache_key = self._get_cache_key(endpoint, {k: v for k, v in params.items() if k != "api_key"})
            cache.set(cache_key, result, self.cache_timeout)

        return result

    def search_movie(self, query: str) -> list[dict[str, Any]]:
        """
        Search for movies by title.

        Parameters
        ----------
        query : str
            Movie title to search for.

        Returns
        -------
        list[dict[str, Any]]
            List of movie results from TMDb.
        """
        data = self._make_request("search/movie", {"query": query})
        return data.get("results", [])

    def search_tv_show(self, query: str) -> list[dict[str, Any]]:
        """
        Search for TV shows by title.

        Parameters
        ----------
        query : str
            TV show title to search for.

        Returns
        -------
        list[dict[str, Any]]
            List of TV show results from TMDb.
        """
        data = self._make_request("search/tv", {"query": query})
        return data.get("results", [])

    def get_movie_details(self, tmdb_id: int) -> dict[str, Any]:
        """
        Get detailed information about a movie.

        Parameters
        ----------
        tmdb_id : int
            TMDb movie ID.

        Returns
        -------
        dict[str, Any]
            Detailed movie information from TMDb.
        """
        return self._make_request(f"movie/{tmdb_id}")

    def get_tv_details(self, tmdb_id: int) -> dict[str, Any]:
        """
        Get detailed information about a TV show.

        Parameters
        ----------
        tmdb_id : int
            TMDb TV show ID.

        Returns
        -------
        dict[str, Any]
            Detailed TV show information from TMDb.
        """
        return self._make_request(f"tv/{tmdb_id}")

    def get_movie_credits(self, tmdb_id: int) -> dict[str, Any]:
        """
        Get credits (cast and crew) for a movie.

        Parameters
        ----------
        tmdb_id : int
            TMDb movie ID.

        Returns
        -------
        dict[str, Any]
            Credits information including cast and crew.
        """
        return self._make_request(f"movie/{tmdb_id}/credits")

    def get_tv_credits(self, tmdb_id: int) -> dict[str, Any]:
        """
        Get credits (cast and crew) for a TV show.

        Parameters
        ----------
        tmdb_id : int
            TMDb TV show ID.

        Returns
        -------
        dict[str, Any]
            Credits information including cast and crew.
        """
        return self._make_request(f"tv/{tmdb_id}/credits")

    def get_movie_images(self, tmdb_id: int) -> dict[str, Any]:
        """
        Get images for a movie.

        Parameters
        ----------
        tmdb_id : int
            TMDb movie ID.

        Returns
        -------
        dict[str, Any]
            Images information including posters and backdrops.
        """
        return self._make_request(f"movie/{tmdb_id}/images")

    def get_tv_images(self, tmdb_id: int) -> dict[str, Any]:
        """
        Get images for a TV show.

        Parameters
        ----------
        tmdb_id : int
            TMDb TV show ID.

        Returns
        -------
        dict[str, Any]
            Images information including posters and backdrops.
        """
        return self._make_request(f"tv/{tmdb_id}/images")

    def enrich_search_result(self, result: dict[str, Any], media_type: str) -> dict[str, Any]:
        """
        Enrich search result with additional details.

        Parameters
        ----------
        result : dict[str, Any]
            Basic search result from TMDb.
        media_type : str
            Type of media ("movie" or "tv").

        Returns
        -------
        dict[str, Any]
            Enriched result with credits and images.
        """
        tmdb_id = result["id"]

        try:
            # Get credits
            credits = self.get_movie_credits(tmdb_id) if media_type == "movie" else self.get_tv_credits(tmdb_id)

            # Extract director and top cast
            crew = credits.get("crew", [])
            cast = credits.get("cast", [])

            # Get director(s)
            directors = [c["name"] for c in crew if c.get("job") == "Director"][:2]
            result["directors"] = directors

            # Get top cast (first 5)
            top_cast = [c["name"] for c in cast[:5]]
            result["cast"] = top_cast

            # Get images
            images = self.get_movie_images(tmdb_id) if media_type == "movie" else self.get_tv_images(tmdb_id)

            # Get first poster or backdrop
            posters = images.get("posters", [])
            backdrops = images.get("backdrops", [])

            if posters:
                result["poster_path"] = posters[0].get("file_path")
            elif backdrops:
                result["backdrop_path"] = backdrops[0].get("file_path")

        except requests.RequestException as e:
            logger.warning(
                "Failed to enrich search result for %s %s: %s",
                media_type,
                tmdb_id,
                str(e),
                extra={'tmdb_id': tmdb_id, 'media_type': media_type}
            )
            # If enrichment fails, continue with basic data
        except Exception as e:
            logger.error(
                "Unexpected error enriching search result for %s %s",
                media_type,
                tmdb_id,
                exc_info=True,
                extra={'tmdb_id': tmdb_id, 'media_type': media_type}
            )
            # If enrichment fails, continue with basic data

        return result
