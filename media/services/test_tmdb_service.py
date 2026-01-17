"""
Unit tests for TMDb service module.

This module tests the TMDb API integration service.
"""

import pytest
from unittest.mock import Mock, patch
import requests

from media.services.tmdb_service import TMDbService


@pytest.fixture
def tmdb_service():
    """Provide TMDbService instance."""
    with patch.object(TMDbService, '__init__', lambda x: None):
        service = TMDbService()
        service.api_key = "test_api_key_12345"
        service.base_url = "https://api.themoviedb.org/3"
        return service


@pytest.fixture
def mock_movie_search_response():
    """Mock response for movie search."""
    return {
        "results": [
            {
                "id": 603,
                "title": "The Matrix",
                "original_title": "The Matrix",
                "overview": "Set in the 22nd century...",
                "poster_path": "/path/to/poster.jpg",
                "release_date": "1999-03-31",
                "vote_average": 8.2,
                "vote_count": 24000
            },
            {
                "id": 604,
                "title": "The Matrix Reloaded",
                "original_title": "The Matrix Reloaded",
                "overview": "Six months after...",
                "poster_path": "/path/to/poster2.jpg",
                "release_date": "2003-05-15",
                "vote_average": 7.2,
                "vote_count": 12000
            }
        ]
    }


@pytest.fixture
def mock_movie_details_response():
    """Mock response for movie details."""
    return {
        "id": 27205,
        "title": "Inception",
        "original_title": "Inception",
        "overview": "Cobb, a skilled thief...",
        "poster_path": "/path/to/inception.jpg",
        "backdrop_path": "/path/to/backdrop.jpg",
        "release_date": "2010-07-16",
        "runtime": 148,
        "budget": 160000000,
        "revenue": 829895144,
        "vote_average": 8.4,
        "vote_count": 32000,
        "original_language": "en",
        "popularity": 85.5
    }


@pytest.fixture
def mock_tv_search_response():
    """Mock response for TV show search."""
    return {
        "results": [
            {
                "id": 1396,
                "name": "Breaking Bad",
                "original_name": "Breaking Bad",
                "overview": "A high school chemistry teacher...",
                "poster_path": "/path/to/bb.jpg",
                "first_air_date": "2008-01-20",
                "vote_average": 8.9,
                "vote_count": 15000
            }
        ]
    }


class TestTMDbServiceMakeRequest:
    """Test cases for _make_request method."""

    @patch('media.services.tmdb_service.requests.get')
    def test_make_request_success(self, mock_get, tmdb_service):
        """
        Test successful API request.
        
        Arrange: Mock successful API response
        Act: Make request
        Assert: Returns JSON data
        """
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Act
        result = tmdb_service._make_request("test/endpoint")
        
        # Assert
        assert result == {"success": True}
        mock_get.assert_called_once()

    @patch('media.services.tmdb_service.requests.get')
    def test_make_request_includes_api_key(self, mock_get, tmdb_service):
        """
        Test that API key is included in request.
        
        Arrange: Mock API response
        Act: Make request
        Assert: API key is in params
        """
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Act
        tmdb_service._make_request("test/endpoint", {"query": "test"})
        
        # Assert
        call_args = mock_get.call_args
        assert call_args[1]["params"]["api_key"] == "test_api_key_12345"
        assert call_args[1]["params"]["query"] == "test"

    @patch('media.services.tmdb_service.requests.get')
    def test_make_request_handles_http_error(self, mock_get, tmdb_service):
        """
        Test handling of HTTP errors.
        
        Arrange: Mock API error response
        Act: Make request
        Assert: HTTPError is raised
        """
        # Arrange
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        # Act & Assert
        with pytest.raises(requests.HTTPError):
            tmdb_service._make_request("invalid/endpoint")

    @patch('media.services.tmdb_service.requests.get')
    def test_make_request_timeout(self, mock_get, tmdb_service):
        """
        Test request timeout handling.
        
        Arrange: Mock timeout
        Act: Make request
        Assert: Timeout exception is raised
        """
        # Arrange
        mock_get.side_effect = requests.Timeout("Request timed out")
        
        # Act & Assert
        with pytest.raises(requests.Timeout):
            tmdb_service._make_request("test/endpoint")


class TestTMDbServiceSearchMovie:
    """Test cases for search_movie method."""

    @patch('media.services.tmdb_service.requests.get')
    def test_search_movie_returns_results(self, mock_get, tmdb_service, mock_movie_search_response):
        """
        Test searching for movies returns results.
        
        Arrange: Mock search response with multiple results
        Act: Search for "Matrix"
        Assert: Returns list of movie results
        """
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = mock_movie_search_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Act
        results = tmdb_service.search_movie("Matrix")
        
        # Assert
        assert len(results) == 2
        assert results[0]["title"] == "The Matrix"
        assert results[1]["title"] == "The Matrix Reloaded"

    @patch('media.services.tmdb_service.requests.get')
    def test_search_movie_no_results(self, mock_get, tmdb_service):
        """
        Test searching for movies with no results.
        
        Arrange: Mock empty search response
        Act: Search for non-existent movie
        Assert: Returns empty list
        """
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Act
        results = tmdb_service.search_movie("NonExistentMovie12345")
        
        # Assert
        assert results == []

    @patch('media.services.tmdb_service.requests.get')
    def test_search_movie_missing_results_key(self, mock_get, tmdb_service):
        """
        Test handling response without 'results' key.
        
        Arrange: Mock malformed response
        Act: Search for movie
        Assert: Returns empty list
        """
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {}  # No 'results' key
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Act
        results = tmdb_service.search_movie("test")
        
        # Assert
        assert results == []


class TestTMDbServiceSearchTVShow:
    """Test cases for search_tv_show method."""

    @patch('media.services.tmdb_service.requests.get')
    def test_search_tv_show_returns_results(self, mock_get, tmdb_service, mock_tv_search_response):
        """
        Test searching for TV shows returns results.
        
        Arrange: Mock search response
        Act: Search for "Breaking Bad"
        Assert: Returns list of TV show results
        """
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = mock_tv_search_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Act
        results = tmdb_service.search_tv_show("Breaking Bad")
        
        # Assert
        assert len(results) == 1
        assert results[0]["name"] == "Breaking Bad"
        assert results[0]["id"] == 1396

    @patch('media.services.tmdb_service.requests.get')
    def test_search_tv_show_no_results(self, mock_get, tmdb_service):
        """
        Test searching for TV shows with no results.
        
        Arrange: Mock empty search response
        Act: Search for non-existent show
        Assert: Returns empty list
        """
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Act
        results = tmdb_service.search_tv_show("NonExistentShow12345")
        
        # Assert
        assert results == []


class TestTMDbServiceGetDetails:
    """Test cases for get_movie_details and get_tv_details methods."""

    @patch('media.services.tmdb_service.requests.get')
    def test_get_movie_details(self, mock_get, tmdb_service, mock_movie_details_response):
        """
        Test getting movie details by TMDb ID.
        
        Arrange: Mock movie details response
        Act: Get details for movie ID 27205
        Assert: Returns complete movie data
        """
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = mock_movie_details_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Act
        details = tmdb_service.get_movie_details(27205)
        
        # Assert
        assert details["title"] == "Inception"
        assert details["runtime"] == 148
        assert details["budget"] == 160000000

    @patch('media.services.tmdb_service.requests.get')
    def test_get_tv_details(self, mock_get, tmdb_service):
        """
        Test getting TV show details by TMDb ID.
        
        Arrange: Mock TV details response
        Act: Get details for TV show
        Assert: Returns complete TV show data
        """
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": 1396,
            "name": "Breaking Bad",
            "number_of_seasons": 5,
            "number_of_episodes": 62
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Act
        details = tmdb_service.get_tv_details(1396)
        
        # Assert
        assert details["name"] == "Breaking Bad"
        assert details["number_of_seasons"] == 5
        assert details["number_of_episodes"] == 62


class TestTMDbServiceGetCredits:
    """Test cases for credits retrieval methods."""

    @patch('media.services.tmdb_service.requests.get')
    def test_get_movie_credits(self, mock_get, tmdb_service):
        """
        Test getting movie credits (cast and crew).
        
        Arrange: Mock credits response
        Act: Get credits for movie
        Assert: Returns cast and crew data
        """
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {
            "cast": [
                {"name": "Leonardo DiCaprio", "character": "Cobb"},
                {"name": "Joseph Gordon-Levitt", "character": "Arthur"}
            ],
            "crew": [
                {"name": "Christopher Nolan", "job": "Director"}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Act
        credits = tmdb_service.get_movie_credits(27205)
        
        # Assert
        assert len(credits["cast"]) == 2
        assert len(credits["crew"]) == 1
        assert credits["cast"][0]["name"] == "Leonardo DiCaprio"

    @patch('media.services.tmdb_service.requests.get')
    def test_get_tv_credits(self, mock_get, tmdb_service):
        """
        Test getting TV show credits.
        
        Arrange: Mock TV credits response
        Act: Get credits for TV show
        Assert: Returns cast and crew data
        """
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {
            "cast": [
                {"name": "Bryan Cranston", "character": "Walter White"}
            ],
            "crew": [
                {"name": "Vince Gilligan", "job": "Creator"}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Act
        credits = tmdb_service.get_tv_credits(1396)
        
        # Assert
        assert len(credits["cast"]) == 1
        assert credits["cast"][0]["name"] == "Bryan Cranston"
        assert credits["crew"][0]["job"] == "Creator"
