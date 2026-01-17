"""
Abstract Factory pattern implementation for Media objects.

This module implements the Abstract Factory design pattern for creating
Movie and TVShow objects with proper type safety and extensibility.
"""

from abc import ABC, abstractmethod
from typing import Any

from media.models import Media, Movie, TVShow


class MediaFactory(ABC):
    """
    Abstract factory for creating media objects.

    This abstract base class defines the interface for creating
    media objects following the Abstract Factory pattern.
    """

    @abstractmethod
    def create_media(self, **kwargs: Any) -> Media:
        """
        Create a media object.

        Parameters
        ----------
        kwargs : Any
            Keyword arguments for media creation.

        Returns
        -------
        Media
            Created media object.
        """
        pass


class MovieFactory(MediaFactory):
    """
    Concrete factory for creating Movie objects.

    This factory creates Movie instances with appropriate
    movie-specific attributes.
    """

    def create_media(self, **kwargs: Any) -> Movie:
        """
        Create a Movie object.

        Parameters
        ----------
        kwargs : Any
            Keyword arguments for movie creation. Should include:
            - tmdb_id: int - TMDb identifier
            - title: str - Movie title
            - original_title: str - Original title
            - overview: str - Movie description
            - poster_path: str - Poster image path
            - backdrop_path: str - Backdrop image path
            - release_date: date - Release date
            - popularity: float - Popularity score
            - vote_average: float - Average rating
            - vote_count: int - Number of votes
            - original_language: str - Language code
            - runtime: int - Runtime in minutes
            - budget: int - Production budget
            - revenue: int - Movie revenue

        Returns
        -------
        Movie
            Created Movie object.
        """
        return Movie.objects.create(**kwargs)


class TVShowFactory(MediaFactory):
    """
    Concrete factory for creating TVShow objects.

    This factory creates TVShow instances with appropriate
    TV show-specific attributes.
    """

    def create_media(self, **kwargs: Any) -> TVShow:
        """
        Create a TVShow object.

        Parameters
        ----------
        kwargs : Any
            Keyword arguments for TV show creation. Should include:
            - tmdb_id: int - TMDb identifier
            - title: str - TV show title
            - original_title: str - Original title
            - overview: str - TV show description
            - poster_path: str - Poster image path
            - backdrop_path: str - Backdrop image path
            - release_date: date - First air date
            - popularity: float - Popularity score
            - vote_average: float - Average rating
            - vote_count: int - Number of votes
            - original_language: str - Language code
            - number_of_seasons: int - Total seasons
            - number_of_episodes: int - Total episodes
            - episode_run_time: int - Average episode runtime
            - status: str - Show status
            - first_air_date: date - First air date
            - last_air_date: date - Last air date

        Returns
        -------
        TVShow
            Created TVShow object.
        """
        return TVShow.objects.create(**kwargs)


class MediaFactoryProvider:
    """
    Provider for obtaining the appropriate media factory.

    This class acts as a factory of factories, returning the correct
    MediaFactory implementation based on the media type.
    """

    @staticmethod
    def get_factory(media_type: str) -> MediaFactory:
        """
        Get the appropriate factory for the given media type.

        Parameters
        ----------
        media_type : str
            Type of media ("MOVIE" or "TV_SHOW").

        Returns
        -------
        MediaFactory
            Appropriate factory for the media type.

        Raises
        ------
        ValueError
            If media_type is not recognized.
        """
        factories: dict[str, type[MediaFactory]] = {
            "MOVIE": MovieFactory,
            "TV_SHOW": TVShowFactory,
        }

        factory_class = factories.get(media_type)
        if factory_class is None:
            raise ValueError(f"Unknown media type: {media_type}")

        return factory_class()
