"""
Unit tests for core views module.

This module tests the main application views including home page and error handlers.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from lists.models import List, ListItem
from media.models import Movie, TVShow, WatchedEpisode

User = get_user_model()


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )


@pytest.fixture
def client():
    """Provide Django test client."""
    return Client()


@pytest.mark.django_db
class TestIndexView:
    """Test cases for index_view function."""

    def test_index_view_anonymous_user_returns_empty_context(self, client):
        """
        Test that anonymous users get an empty context on the home page.
        
        Arrange: Create request with anonymous user
        Act: Call index_view
        Assert: Response is successful and no user stats shown
        """
        # Arrange & Act
        response = client.get("/", follow=True)
        
        # Assert
        assert response.status_code == 200
        # Anonymous users shouldn't see stats
        assert "total_lists" not in response.context

    def test_index_view_authenticated_user_with_no_data(self, client, user):
        """
        Test authenticated user with no lists or watched episodes.
        
        Arrange: Create authenticated user with no data
        Act: Call index_view
        Assert: All counts are zero
        """
        # Arrange
        client.force_login(user)
        
        # Act
        response = client.get("/", follow=True)
        
        # Assert
        assert response.status_code == 200
        assert response.context["total_lists"] == 0
        assert response.context["total_items"] == 0
        assert response.context["total_watched"] == 0

    def test_index_view_authenticated_user_with_lists(self, client, user):
        """
        Test authenticated user with multiple lists and items.
        
        Arrange: Create user with 3 lists and 5 total items (different movies)
        Act: Call index_view
        Assert: Correct counts are displayed
        """
        # Arrange
        client.force_login(user)
        
        # Create test data
        list1 = List.objects.create(user=user, name="Favorites")
        list2 = List.objects.create(user=user, name="Watch Later")
        list3 = List.objects.create(user=user, name="Archive")
        
        # Create different movies to avoid unique constraint
        movie1 = Movie.objects.create(
            title="Test Movie 1",
            original_title="Test Movie 1",
            tmdb_id=12345
        )
        movie2 = Movie.objects.create(
            title="Test Movie 2",
            original_title="Test Movie 2",
            tmdb_id=12346
        )
        movie3 = Movie.objects.create(
            title="Test Movie 3",
            original_title="Test Movie 3",
            tmdb_id=12347
        )
        
        ListItem.objects.create(list=list1, media=movie1, position=1)
        ListItem.objects.create(list=list1, media=movie2, position=2)
        ListItem.objects.create(list=list2, media=movie3, position=1)
        ListItem.objects.create(list=list3, media=movie1, position=1)
        ListItem.objects.create(list=list3, media=movie2, position=2)
        
        # Act
        response = client.get("/", follow=True)
        
        # Assert
        assert response.status_code == 200
        assert response.context["total_lists"] == 3
        assert response.context["total_items"] == 5

    def test_index_view_authenticated_user_with_watched_episodes(self, client, user):
        """
        Test authenticated user with watched episodes.
        
        Arrange: Create user with 10 watched episodes
        Act: Call index_view
        Assert: Watched count is correct
        """
        # Arrange
        client.force_login(user)
        
        # Create TV show first
        tv_show = TVShow.objects.create(
            title="Test Show",
            original_title="Test Show",
            tmdb_id=98765
        )
        
        # Create watched episodes
        for i in range(10):
            WatchedEpisode.objects.create(
                user=user,
                tv_show=tv_show,
                season_number=1,
                episode_number=i + 1
            )
        
        # Act
        response = client.get("/", follow=True)
        
        # Assert
        assert response.status_code == 200
        assert response.context["total_watched"] == 10

    def test_index_view_recent_lists_ordered_by_updated_at(self, client, user):
        """
        Test that recent lists are ordered by updated_at descending.
        
        Arrange: Create 6 lists with different update times
        Act: Call index_view
        Assert: Only 5 most recent lists are returned in correct order
        """
        # Arrange
        client.force_login(user)
        
        # Create lists (older to newer)
        for i in range(6):
            List.objects.create(user=user, name=f"List {i}")
        
        # Act
        response = client.get("/", follow=True)
        
        # Assert
        assert response.status_code == 200
        recent_lists = list(response.context["recent_lists"])
        assert len(recent_lists) == 5
        # Most recent should be first
        assert recent_lists[0].name == "List 5"
        assert recent_lists[-1].name == "List 1"


@pytest.mark.django_db
class TestCustom404:
    """Test cases for custom_404 error handler."""

    def test_custom_404_returns_404_status(self, client):
        """
        Test that custom 404 handler returns 404 status code.
        
        Arrange: Request a non-existent page
        Act: Get response
        Assert: Status code is 404
        """
        # Arrange & Act
        response = client.get("/nonexistent-page-that-does-not-exist/", follow=True)
        
        # Assert
        assert response.status_code == 404

    def test_custom_404_for_different_paths(self, client):
        """
        Test that custom 404 handler works for various non-existent paths.
        
        Arrange: Request multiple non-existent pages
        Act: Get responses
        Assert: All return 404 status
        """
        # Arrange
        paths = [
            "/this/does/not/exist/",
            "/another/missing/page/",
            "/404test/",
        ]
        
        # Act & Assert
        for path in paths:
            response = client.get(path, follow=True)
            assert response.status_code == 404

