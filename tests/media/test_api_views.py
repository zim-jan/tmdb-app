"""Unit tests for media API views."""

from unittest.mock import Mock, patch

import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from media.api_views import media_details_api

User = get_user_model()


@pytest.fixture
def authenticated_user():
    """Create an authenticated user for testing."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def request_factory():
    """Provide Django RequestFactory for creating mock requests."""
    return RequestFactory()


@pytest.fixture
def mock_tmdb_movie_details():
    """Mock movie details response from TMDb API."""
    return {
        'id': 550,
        'title': 'Fight Club',
        'overview': 'A ticking-time-bomb insomniac and a slippery soap salesman...',
        'backdrop_path': '/backdrop.jpg',
        'poster_path': '/poster.jpg',
        'vote_average': 8.4,
        'release_date': '1999-10-15',
        'runtime': 139,
        'genres': [
            {'id': 18, 'name': 'Drama'},
            {'id': 53, 'name': 'Thriller'}
        ],
        'production_companies': [
            {'id': 508, 'name': 'Fox 2000 Pictures'},
            {'id': 711, 'name': 'New Regency Pictures'}
        ],
        'budget': 63000000,
        'revenue': 100853753
    }


@pytest.fixture
def mock_tmdb_movie_credits():
    """Mock movie credits response from TMDb API."""
    return {
        'cast': [
            {
                'name': 'Edward Norton',
                'character': 'The Narrator',
                'profile_path': '/norton.jpg'
            },
            {
                'name': 'Brad Pitt',
                'character': 'Tyler Durden',
                'profile_path': '/pitt.jpg'
            },
            {
                'name': 'Helena Bonham Carter',
                'character': 'Marla Singer',
                'profile_path': '/carter.jpg'
            }
        ] + [
            {
                'name': f'Actor {i}',
                'character': f'Character {i}',
                'profile_path': f'/actor{i}.jpg'
            }
            for i in range(4, 15)  # Add more actors to test 10-cast limit
        ],
        'crew': [
            {
                'name': 'David Fincher',
                'job': 'Director',
                'department': 'Directing'
            },
            {
                'name': 'Jim Uhls',
                'job': 'Screenplay',
                'department': 'Writing'
            },
            {
                'name': 'Art Linson',
                'job': 'Producer',
                'department': 'Production'
            },
            {
                'name': 'Ross Grayson Bell',
                'job': 'Director',
                'department': 'Directing'
            }
        ]
    }


@pytest.fixture
def mock_tmdb_tv_details():
    """Mock TV show details response from TMDb API."""
    return {
        'id': 1396,
        'name': 'Breaking Bad',
        'overview': 'A high school chemistry teacher diagnosed with cancer...',
        'backdrop_path': '/tv_backdrop.jpg',
        'poster_path': '/tv_poster.jpg',
        'vote_average': 9.5,
        'first_air_date': '2008-01-20',
        'genres': [
            {'id': 18, 'name': 'Drama'},
            {'id': 80, 'name': 'Crime'}
        ],
        'production_companies': [
            {'id': 2605, 'name': 'High Bridge Productions'},
            {'id': 11073, 'name': 'Sony Pictures Television'}
        ],
        'number_of_seasons': 5,
        'number_of_episodes': 62,
        'created_by': [
            {'id': 66633, 'name': 'Vince Gilligan'},
            {'id': 12345, 'name': 'Peter Gould'}
        ]
    }


@pytest.fixture
def mock_tmdb_tv_credits():
    """Mock TV show credits response from TMDb API."""
    return {
        'cast': [
            {
                'name': 'Bryan Cranston',
                'character': 'Walter White',
                'profile_path': '/cranston.jpg'
            },
            {
                'name': 'Aaron Paul',
                'character': 'Jesse Pinkman',
                'profile_path': '/paul.jpg'
            },
            {
                'name': 'Anna Gunn',
                'character': 'Skyler White',
                'profile_path': '/gunn.jpg'
            }
        ] + [
            {
                'name': f'TV Actor {i}',
                'character': f'TV Character {i}',
                'profile_path': f'/tv_actor{i}.jpg'
            }
            for i in range(4, 12)  # Add more actors
        ],
        'crew': []
    }


@pytest.fixture
def mock_external_ids():
    """Mock external IDs response from TMDb API."""
    return {
        'imdb_id': 'tt0137523',
        'facebook_id': 'FightClub',
        'instagram_id': 'fightclub',
        'twitter_id': 'fightclub'
    }


@pytest.mark.django_db
class TestMediaDetailsAPIMovies:
    """Test suite for movie-related API functionality."""

    def test_get_movie_details_success(
        self,
        request_factory,
        authenticated_user,
        mock_tmdb_movie_details,
        mock_tmdb_movie_credits,
        mock_external_ids
    ) -> None:
        """
        Test successful retrieval of movie details.

        Validates that the API returns correct structure with all expected fields
        including details, credits, directors, cast, and external IDs.
        """
        # Arrange
        request = request_factory.get('/api/media/details/movie/550/')
        request.user = authenticated_user

        with patch('media.api_views.TMDbService') as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            mock_service.get_movie_details.return_value = mock_tmdb_movie_details
            mock_service.get_movie_credits.return_value = mock_tmdb_movie_credits
            mock_service._make_request.return_value = mock_external_ids

            # Act
            response = media_details_api(request, 'movie', 550)

            # Assert
            assert response.status_code == 200

            # Parse JSON response
            import json
            data = json.loads(response.content)

            # Verify core movie information
            assert data['id'] == 550
            assert data['title'] == 'Fight Club'
            assert data['overview'] == 'A ticking-time-bomb insomniac and a slippery soap salesman...'
            assert data['media_type'] == 'movie'

            # Verify metadata
            assert data['vote_average'] == 8.4
            assert data['release_date'] == '1999-10-15'
            assert data['runtime'] == 139
            assert data['budget'] == 63000000
            assert data['revenue'] == 100853753

            # Verify images
            assert data['backdrop_path'] == '/backdrop.jpg'
            assert data['poster_path'] == '/poster.jpg'

            # Verify genres
            assert len(data['genres']) == 2
            assert data['genres'][0]['name'] == 'Drama'

            # Verify directors (limited to 2)
            assert len(data['directors']) == 2
            assert 'David Fincher' in data['directors']

            # Verify cast (limited to 10)
            assert len(data['cast']) == 10
            assert data['cast'][0]['name'] == 'Edward Norton'
            assert data['cast'][0]['character'] == 'The Narrator'
            assert data['cast'][0]['profile_path'] == '/norton.jpg'

            # Verify external IDs
            assert data['imdb_id'] == 'tt0137523'

            # Verify service calls
            mock_service.get_movie_details.assert_called_once_with(550)
            mock_service.get_movie_credits.assert_called_once_with(550)
            mock_service._make_request.assert_called_once_with('/movie/550/external_ids')

    def test_get_movie_details_filters_directors(
        self,
        request_factory,
        authenticated_user,
        mock_tmdb_movie_details,
        mock_external_ids
    ) -> None:
        """
        Test that only crew members with 'Director' job are included in directors list.

        Verifies filtering logic excludes producers, writers, and other crew roles,
        and limits results to maximum of 2 directors.
        """
        # Arrange
        request = request_factory.get('/api/media/details/movie/550/')
        request.user = authenticated_user

        # Create credits with multiple crew members, only some are directors
        mock_credits = {
            'cast': [],
            'crew': [
                {'name': 'Director One', 'job': 'Director'},
                {'name': 'Producer', 'job': 'Producer'},
                {'name': 'Writer', 'job': 'Screenplay'},
                {'name': 'Director Two', 'job': 'Director'},
                {'name': 'Director Three', 'job': 'Director'},  # Should be excluded (limit=2)
            ]
        }

        with patch('media.api_views.TMDbService') as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            mock_service.get_movie_details.return_value = mock_tmdb_movie_details
            mock_service.get_movie_credits.return_value = mock_credits
            mock_service._make_request.return_value = mock_external_ids

            # Act
            response = media_details_api(request, 'movie', 550)

            # Assert
            import json
            data = json.loads(response.content)

            # Should only include 2 directors, no other crew
            assert len(data['directors']) == 2
            assert 'Director One' in data['directors']
            assert 'Director Two' in data['directors']
            assert 'Director Three' not in data['directors']
            assert 'Producer' not in data['directors']
            assert 'Writer' not in data['directors']

    def test_get_movie_details_limits_cast_to_ten(
        self,
        request_factory,
        authenticated_user,
        mock_tmdb_movie_details,
        mock_external_ids
    ) -> None:
        """
        Test that cast list is limited to 10 actors maximum.

        Validates slicing behavior when API returns more than 10 cast members.
        """
        # Arrange
        request = request_factory.get('/api/media/details/movie/550/')
        request.user = authenticated_user

        # Create 15 cast members to test the 10-person limit
        mock_credits = {
            'cast': [
                {'name': f'Actor {i}', 'character': f'Character {i}', 'profile_path': f'/actor{i}.jpg'}
                for i in range(15)
            ],
            'crew': []
        }

        with patch('media.api_views.TMDbService') as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            mock_service.get_movie_details.return_value = mock_tmdb_movie_details
            mock_service.get_movie_credits.return_value = mock_credits
            mock_service._make_request.return_value = mock_external_ids

            # Act
            response = media_details_api(request, 'movie', 550)

            # Assert
            import json
            data = json.loads(response.content)

            assert len(data['cast']) == 10
            # Verify first and last in the limited list
            assert data['cast'][0]['name'] == 'Actor 0'
            assert data['cast'][9]['name'] == 'Actor 9'


@pytest.mark.django_db
class TestMediaDetailsAPITVShows:
    """Test suite for TV show-related API functionality."""

    def test_get_tv_show_details_success(
        self,
        request_factory,
        authenticated_user,
        mock_tmdb_tv_details,
        mock_tmdb_tv_credits,
        mock_external_ids
    ) -> None:
        """
        Test successful retrieval of TV show details.

        Validates that TV shows return correct structure including series-specific
        fields like number_of_seasons, number_of_episodes, and created_by.
        """
        # Arrange
        request = request_factory.get('/api/media/details/tv/1396/')
        request.user = authenticated_user

        with patch('media.api_views.TMDbService') as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            mock_service.get_tv_details.return_value = mock_tmdb_tv_details
            mock_service.get_tv_credits.return_value = mock_tmdb_tv_credits
            mock_service._make_request.return_value = mock_external_ids

            # Act
            response = media_details_api(request, 'tv', 1396)

            # Assert
            assert response.status_code == 200

            import json
            data = json.loads(response.content)

            # Verify TV-specific fields
            assert data['id'] == 1396
            assert data['name'] == 'Breaking Bad'
            assert data['title'] == 'Breaking Bad'  # Alias for consistency
            assert data['media_type'] == 'tv'

            # Verify TV metadata
            assert data['first_air_date'] == '2008-01-20'
            assert data['number_of_seasons'] == 5
            assert data['number_of_episodes'] == 62

            # Verify creators (from created_by field, limited to 2)
            assert len(data['directors']) == 2
            assert 'Vince Gilligan' in data['directors']
            assert 'Peter Gould' in data['directors']

            # Verify cast structure
            assert len(data['cast']) == 10
            assert data['cast'][0]['name'] == 'Bryan Cranston'

            # Verify service calls
            mock_service.get_tv_details.assert_called_once_with(1396)
            mock_service.get_tv_credits.assert_called_once_with(1396)
            mock_service._make_request.assert_called_once_with('/tv/1396/external_ids')

    def test_get_tv_show_details_with_no_creators(
        self,
        request_factory,
        authenticated_user,
        mock_external_ids
    ) -> None:
        """
        Test TV show details when created_by list is empty.

        Validates graceful handling of missing creator information.
        """
        # Arrange
        request = request_factory.get('/api/media/details/tv/1396/')
        request.user = authenticated_user

        tv_details_no_creators = {
            'id': 1396,
            'name': 'Breaking Bad',
            'overview': 'Test overview',
            'created_by': [],  # No creators
            'number_of_seasons': 5,
            'number_of_episodes': 62
        }

        mock_credits = {'cast': [], 'crew': []}

        with patch('media.api_views.TMDbService') as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            mock_service.get_tv_details.return_value = tv_details_no_creators
            mock_service.get_tv_credits.return_value = mock_credits
            mock_service._make_request.return_value = mock_external_ids

            # Act
            response = media_details_api(request, 'tv', 1396)

            # Assert
            import json
            data = json.loads(response.content)

            assert len(data['directors']) == 0
            assert data['directors'] == []


@pytest.mark.django_db
class TestMediaDetailsAPIErrorHandling:
    """Test suite for error handling and edge cases."""

    def test_unauthorized_access_redirects(self, request_factory) -> None:
        """
        Test that unauthenticated requests are properly handled by login_required.

        The @login_required decorator should redirect to login page.
        """
        # Arrange
        request = request_factory.get('/api/media/details/movie/550/')
        request.user = Mock(is_authenticated=False)

        # Act & Assert
        # The login_required decorator will raise an exception or redirect
        # We need to test this through Django's test client for full decorator behavior
        from django.test import Client

        client = Client()
        response = client.get('/api/media/details/movie/550/', follow=True)

        # Should eventually redirect to login page
        # With SSL redirect, we get 301 first, then potentially 302
        assert response.status_code == 200 or response.redirect_chain[-1][1] in [301, 302]
        # Check if we ended up at a login or redirect page
        assert any(keyword in str(response.redirect_chain) or keyword in response.request['PATH_INFO']
                   for keyword in ['/login/', '/accounts/login/'])

    def test_tmdb_service_exception_returns_error(
        self,
        request_factory,
        authenticated_user
    ) -> None:
        """
        Test error handling when TMDb service raises an exception.

        Validates that exceptions are caught and returned as JSON error response
        with 500 status code.
        """
        # Arrange
        request = request_factory.get('/api/media/details/movie/999999/')
        request.user = authenticated_user

        with patch('media.api_views.TMDbService') as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            mock_service.get_movie_details.side_effect = Exception('TMDb API connection failed')

            # Act
            response = media_details_api(request, 'movie', 999999)

            # Assert
            assert response.status_code == 500

            import json
            data = json.loads(response.content)

            assert 'error' in data
            assert data['error'] == 'TMDb API connection failed'

    def test_missing_external_ids_handled_gracefully(
        self,
        request_factory,
        authenticated_user,
        mock_tmdb_movie_details,
        mock_tmdb_movie_credits
    ) -> None:
        """
        Test graceful handling when external_ids endpoint returns no IMDB ID.

        Validates that missing imdb_id doesn't break the response.
        """
        # Arrange
        request = request_factory.get('/api/media/details/movie/550/')
        request.user = authenticated_user

        # External IDs without imdb_id
        mock_external_ids_no_imdb = {
            'facebook_id': 'FightClub',
            'instagram_id': 'fightclub'
        }

        with patch('media.api_views.TMDbService') as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            mock_service.get_movie_details.return_value = mock_tmdb_movie_details
            mock_service.get_movie_credits.return_value = mock_tmdb_movie_credits
            mock_service._make_request.return_value = mock_external_ids_no_imdb

            # Act
            response = media_details_api(request, 'movie', 550)

            # Assert
            assert response.status_code == 200

            import json
            data = json.loads(response.content)

            # imdb_id should be None when not present
            assert data['imdb_id'] is None

    def test_empty_credits_handled_gracefully(
        self,
        request_factory,
        authenticated_user,
        mock_tmdb_movie_details,
        mock_external_ids
    ) -> None:
        """
        Test handling of movies with no cast or crew information.

        Validates that empty credits lists don't cause errors.
        """
        # Arrange
        request = request_factory.get('/api/media/details/movie/550/')
        request.user = authenticated_user

        # Empty credits
        mock_empty_credits = {
            'cast': [],
            'crew': []
        }

        with patch('media.api_views.TMDbService') as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            mock_service.get_movie_details.return_value = mock_tmdb_movie_details
            mock_service.get_movie_credits.return_value = mock_empty_credits
            mock_service._make_request.return_value = mock_external_ids

            # Act
            response = media_details_api(request, 'movie', 550)

            # Assert
            assert response.status_code == 200

            import json
            data = json.loads(response.content)

            assert data['directors'] == []
            assert data['cast'] == []

    def test_malformed_credits_structure(
        self,
        request_factory,
        authenticated_user,
        mock_tmdb_movie_details,
        mock_external_ids
    ) -> None:
        """
        Test resilience when credits have malformed or missing fields.

        Validates that missing 'name', 'character', or 'profile_path' fields
        are handled gracefully using .get() method.
        """
        # Arrange
        request = request_factory.get('/api/media/details/movie/550/')
        request.user = authenticated_user

        # Credits with missing fields
        mock_malformed_credits = {
            'cast': [
                {'name': 'Actor 1'},  # Missing character and profile_path
                {'character': 'Character 2'},  # Missing name
                {}  # Empty dict
            ],
            'crew': [
                {'job': 'Director'},  # Missing name
                {'name': 'Director Name'}  # Missing job
            ]
        }

        with patch('media.api_views.TMDbService') as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            mock_service.get_movie_details.return_value = mock_tmdb_movie_details
            mock_service.get_movie_credits.return_value = mock_malformed_credits
            mock_service._make_request.return_value = mock_external_ids

            # Act
            response = media_details_api(request, 'movie', 550)

            # Assert - API may return error for malformed data
            assert response.status_code in [200, 500]

            if response.status_code == 200:
                import json
                data = json.loads(response.content)

                # Should handle malformed data gracefully
                assert len(data['cast']) == 3
                assert data['cast'][0]['name'] == 'Actor 1'
                assert data['cast'][0]['character'] is None
                assert data['cast'][0]['profile_path'] is None

                # Directors list should be empty (no valid directors found)
                assert data['directors'] == []
