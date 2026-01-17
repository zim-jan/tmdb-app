"""
Unit tests for media factory module.

This module tests the Abstract Factory pattern implementation for Media objects.
"""

import pytest
from datetime import date

from media.factories.media_factory import (
    MediaFactory,
    MediaFactoryProvider,
    MovieFactory,
    TVShowFactory,
)
from media.models import Movie, TVShow, MediaType


@pytest.mark.django_db
class TestMovieFactory:
    """Test cases for MovieFactory."""

    def test_create_movie_with_minimal_data(self):
        """
        Test creating a movie with only required fields.
        
        Arrange: Prepare minimal movie data
        Act: Create movie via factory
        Assert: Movie is created with correct type
        """
        # Arrange
        factory = MovieFactory()
        data = {
            "title": "The Matrix",
            "original_title": "The Matrix",
            "tmdb_id": 603
        }
        
        # Act
        movie = factory.create_media(**data)
        
        # Assert
        assert isinstance(movie, Movie)
        assert movie.title == "The Matrix"
        assert movie.media_type == MediaType.MOVIE
        assert movie.id is not None

    def test_create_movie_with_full_data(self):
        """
        Test creating a movie with all available fields.
        
        Arrange: Prepare complete movie data
        Act: Create movie via factory
        Assert: All fields are correctly set
        """
        # Arrange
        factory = MovieFactory()
        data = {
            "title": "Inception",
            "original_title": "Inception",
            "tmdb_id": 27205,
            "overview": "A thief who steals corporate secrets...",
            "poster_path": "/path/to/poster.jpg",
            "backdrop_path": "/path/to/backdrop.jpg",
            "release_date": date(2010, 7, 16),
            "popularity": 85.5,
            "vote_average": 8.4,
            "vote_count": 32000,
            "original_language": "en",
            "runtime": 148,
            "budget": 160000000,
            "revenue": 829895144
        }
        
        # Act
        movie = factory.create_media(**data)
        
        # Assert
        assert movie.title == "Inception"
        assert movie.runtime == 148
        assert movie.budget == 160000000
        assert movie.revenue == 829895144
        assert movie.vote_average == 8.4
        assert movie.media_type == MediaType.MOVIE

    def test_create_multiple_movies(self):
        """
        Test creating multiple distinct movies.
        
        Arrange: Prepare data for 3 different movies
        Act: Create all movies
        Assert: All movies are created with unique IDs
        """
        # Arrange
        factory = MovieFactory()
        movies_data = [
            {"title": "Movie 1", "original_title": "Movie 1", "tmdb_id": 1001},
            {"title": "Movie 2", "original_title": "Movie 2", "tmdb_id": 1002},
            {"title": "Movie 3", "original_title": "Movie 3", "tmdb_id": 1003},
        ]
        
        # Act
        movies = [factory.create_media(**data) for data in movies_data]
        
        # Assert
        assert len(movies) == 3
        assert len({m.id for m in movies}) == 3  # All unique IDs


@pytest.mark.django_db
class TestTVShowFactory:
    """Test cases for TVShowFactory."""

    def test_create_tv_show_with_minimal_data(self):
        """
        Test creating a TV show with only required fields.
        
        Arrange: Prepare minimal TV show data
        Act: Create TV show via factory
        Assert: TV show is created with correct type
        """
        # Arrange
        factory = TVShowFactory()
        data = {
            "title": "Breaking Bad",
            "original_title": "Breaking Bad",
            "tmdb_id": 1396
        }
        
        # Act
        tv_show = factory.create_media(**data)
        
        # Assert
        assert isinstance(tv_show, TVShow)
        assert tv_show.title == "Breaking Bad"
        assert tv_show.media_type == MediaType.TV_SHOW
        assert tv_show.id is not None

    def test_create_tv_show_with_full_data(self):
        """
        Test creating a TV show with all available fields.
        
        Arrange: Prepare complete TV show data
        Act: Create TV show via factory
        Assert: All fields are correctly set
        """
        # Arrange
        factory = TVShowFactory()
        data = {
            "title": "Game of Thrones",
            "original_title": "Game of Thrones",
            "tmdb_id": 1399,
            "overview": "Seven noble families fight for control...",
            "poster_path": "/path/to/poster.jpg",
            "backdrop_path": "/path/to/backdrop.jpg",
            "release_date": date(2011, 4, 17),
            "popularity": 90.8,
            "vote_average": 8.3,
            "vote_count": 22000,
            "original_language": "en",
            "number_of_seasons": 8,
            "number_of_episodes": 73,
            "episode_run_time": 60,
            "status": "Ended"
        }
        
        # Act
        tv_show = factory.create_media(**data)
        
        # Assert
        assert tv_show.title == "Game of Thrones"
        assert tv_show.number_of_seasons == 8
        assert tv_show.number_of_episodes == 73
        assert tv_show.vote_average == 8.3
        assert tv_show.media_type == MediaType.TV_SHOW

    def test_create_multiple_tv_shows(self):
        """
        Test creating multiple distinct TV shows.
        
        Arrange: Prepare data for 3 different TV shows
        Act: Create all TV shows
        Assert: All TV shows are created with unique IDs
        """
        # Arrange
        factory = TVShowFactory()
        shows_data = [
            {"title": "Show 1", "original_title": "Show 1", "tmdb_id": 2001},
            {"title": "Show 2", "original_title": "Show 2", "tmdb_id": 2002},
            {"title": "Show 3", "original_title": "Show 3", "tmdb_id": 2003},
        ]
        
        # Act
        shows = [factory.create_media(**data) for data in shows_data]
        
        # Assert
        assert len(shows) == 3
        assert len({s.id for s in shows}) == 3  # All unique IDs


@pytest.mark.django_db
class TestMediaFactoryProvider:
    """Test cases for MediaFactoryProvider."""

    def test_get_movie_factory(self):
        """
        Test getting MovieFactory from provider.
        
        Arrange: Provider and media type
        Act: Request movie factory
        Assert: Returns MovieFactory instance
        """
        # Act
        factory = MediaFactoryProvider.get_factory("MOVIE")
        
        # Assert
        assert isinstance(factory, MovieFactory)

    def test_get_tv_show_factory(self):
        """
        Test getting TVShowFactory from provider.
        
        Arrange: Provider and media type
        Act: Request TV show factory
        Assert: Returns TVShowFactory instance
        """
        # Act
        factory = MediaFactoryProvider.get_factory("TV_SHOW")
        
        # Assert
        assert isinstance(factory, TVShowFactory)

    def test_get_factory_with_invalid_type_raises_error(self):
        """
        Test that requesting unknown media type raises ValueError.
        
        Arrange: Invalid media type string
        Act: Request factory with invalid type
        Assert: ValueError is raised
        """
        # Act & Assert
        with pytest.raises(ValueError, match="Unknown media type"):
            MediaFactoryProvider.get_factory("INVALID_TYPE")

    def test_factories_return_different_instances(self):
        """
        Test that each call returns a new factory instance.
        
        Arrange: Multiple requests for same type
        Act: Get factory twice
        Assert: Different instances are returned
        """
        # Act
        factory1 = MediaFactoryProvider.get_factory("MOVIE")
        factory2 = MediaFactoryProvider.get_factory("MOVIE")
        
        # Assert
        assert factory1 is not factory2  # Different instances


@pytest.mark.django_db
class TestFactoryIntegration:
    """Integration tests for factory pattern usage."""

    def test_create_movie_via_provider(self):
        """
        Test creating a movie through the provider.
        
        Arrange: Get factory from provider
        Act: Create movie
        Assert: Movie is created correctly
        """
        # Arrange
        factory = MediaFactoryProvider.get_factory("MOVIE")
        data = {
            "title": "Interstellar",
            "original_title": "Interstellar",
            "tmdb_id": 157336,
            "runtime": 169
        }
        
        # Act
        movie = factory.create_media(**data)
        
        # Assert
        assert isinstance(movie, Movie)
        assert movie.title == "Interstellar"
        assert movie.runtime == 169

    def test_create_tv_show_via_provider(self):
        """
        Test creating a TV show through the provider.
        
        Arrange: Get factory from provider
        Act: Create TV show
        Assert: TV show is created correctly
        """
        # Arrange
        factory = MediaFactoryProvider.get_factory("TV_SHOW")
        data = {
            "title": "Stranger Things",
            "original_title": "Stranger Things",
            "tmdb_id": 66732,
            "number_of_seasons": 4
        }
        
        # Act
        tv_show = factory.create_media(**data)
        
        # Assert
        assert isinstance(tv_show, TVShow)
        assert tv_show.title == "Stranger Things"
        assert tv_show.number_of_seasons == 4

    def test_create_mixed_media_types(self):
        """
        Test creating both movies and TV shows in same session.
        
        Arrange: Get both factory types
        Act: Create one movie and one TV show
        Assert: Both are created with correct types
        """
        # Arrange
        movie_factory = MediaFactoryProvider.get_factory("MOVIE")
        tv_factory = MediaFactoryProvider.get_factory("TV_SHOW")
        
        # Act
        movie = movie_factory.create_media(
            title="Test Movie",
            original_title="Test Movie",
            tmdb_id=99001
        )
        tv_show = tv_factory.create_media(
            title="Test Show",
            original_title="Test Show",
            tmdb_id=99002
        )
        
        # Assert
        assert isinstance(movie, Movie)
        assert isinstance(tv_show, TVShow)
        assert movie.media_type == MediaType.MOVIE
        assert tv_show.media_type == MediaType.TV_SHOW
