"""
Unit tests for lists service module.

This module tests the list management service layer functionality.
"""

import pytest
from django.contrib.auth import get_user_model

from lists.models import List, ListItem
from lists.services.list_service import ListService
from media.models import Movie, TVShow

User = get_user_model()


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        nickname="testuser"
    )


@pytest.fixture
def another_user(db):
    """Create another test user."""
    return User.objects.create_user(
        username="anotheruser",
        email="another@example.com",
        password="testpass456",
        nickname="anotheruser"
    )


@pytest.fixture
def list_service():
    """Provide ListService instance."""
    return ListService()


@pytest.fixture
def sample_movie(db):
    """Create a sample movie."""
    return Movie.objects.create(
        title="Inception",
        original_title="Inception",
        tmdb_id=27205
    )


@pytest.fixture
def sample_tv_show(db):
    """Create a sample TV show."""
    return TVShow.objects.create(
        title="Breaking Bad",
        original_title="Breaking Bad",
        tmdb_id=1396
    )


@pytest.mark.django_db
class TestListServiceCreate:
    """Test cases for list creation."""

    def test_create_list_with_default_visibility(self, list_service, user) -> None:
        """
        Test creating a private list (default behavior).

        Arrange: User and service
        Act: Create list with default visibility
        Assert: List is created and private by default
        """
        # Act
        list_obj = list_service.create_list(user, "My Favorites")

        # Assert
        assert list_obj.id is not None
        assert list_obj.name == "My Favorites"
        assert list_obj.user == user
        assert list_obj.is_public is False

    def test_create_public_list(self, list_service, user) -> None:
        """
        Test creating a public list.

        Arrange: User and service
        Act: Create list with is_public=True
        Assert: List is created and public
        """
        # Act
        list_obj = list_service.create_list(user, "Watch Later", is_public=True)

        # Assert
        assert list_obj.id is not None
        assert list_obj.name == "Watch Later"
        assert list_obj.is_public is True

    def test_create_multiple_lists_for_user(self, list_service, user) -> None:
        """
        Test creating multiple lists for the same user.

        Arrange: User and service
        Act: Create 3 different lists
        Assert: All lists are created with correct data
        """
        # Act
        list1 = list_service.create_list(user, "Favorites")
        list2 = list_service.create_list(user, "Watch Later")
        list3 = list_service.create_list(user, "Archive")

        # Assert
        assert list1.id != list2.id != list3.id
        assert List.objects.filter(user=user).count() == 3


@pytest.mark.django_db
class TestListServiceUpdate:
    """Test cases for list updates."""

    def test_update_list_name(self, list_service, user) -> None:
        """
        Test updating list name.

        Arrange: Create a list
        Act: Update the name
        Assert: Name is changed
        """
        # Arrange
        list_obj = list_service.create_list(user, "Old Name")

        # Act
        updated_list = list_service.update_list(list_obj, name="New Name")

        # Assert
        assert updated_list.name == "New Name"
        list_obj.refresh_from_db()
        assert list_obj.name == "New Name"

    def test_update_list_visibility(self, list_service, user) -> None:
        """
        Test updating list visibility.

        Arrange: Create a private list
        Act: Make it public
        Assert: Visibility is changed
        """
        # Arrange
        list_obj = list_service.create_list(user, "Private List", is_public=False)

        # Act
        updated_list = list_service.update_list(list_obj, is_public=True)

        # Assert
        assert updated_list.is_public is True
        list_obj.refresh_from_db()
        assert list_obj.is_public is True

    def test_update_list_partial_update(self, list_service, user) -> None:
        """
        Test partial update (only updating one field).

        Arrange: Create a list with specific properties
        Act: Update only the name
        Assert: Only name changes, visibility unchanged
        """
        # Arrange
        list_obj = list_service.create_list(user, "Original", is_public=True)

        # Act
        updated_list = list_service.update_list(list_obj, name="Updated")

        # Assert
        assert updated_list.name == "Updated"
        assert updated_list.is_public is True  # Unchanged


@pytest.mark.django_db
class TestListServiceDelete:
    """Test cases for list deletion."""

    def test_delete_empty_list(self, list_service, user) -> None:
        """
        Test deleting a list with no items.

        Arrange: Create an empty list
        Act: Delete the list
        Assert: List is removed from database
        """
        # Arrange
        list_obj = list_service.create_list(user, "To Delete")
        list_id = list_obj.id

        # Act
        list_service.delete_list(list_obj)

        # Assert
        assert not List.objects.filter(id=list_id).exists()

    def test_delete_list_with_items(self, list_service, user, sample_movie) -> None:
        """
        Test deleting a list with items (cascade delete).

        Arrange: Create list with items
        Act: Delete the list
        Assert: List and all items are removed
        """
        # Arrange
        list_obj = list_service.create_list(user, "With Items")
        list_service.add_media_to_list(list_obj, sample_movie)
        list_id = list_obj.id

        # Act
        list_service.delete_list(list_obj)

        # Assert
        assert not List.objects.filter(id=list_id).exists()
        assert not ListItem.objects.filter(list_id=list_id).exists()


@pytest.mark.django_db
class TestListServiceAddMedia:
    """Test cases for adding media to lists."""

    def test_add_movie_to_list(self, list_service, user, sample_movie) -> None:
        """
        Test adding a movie to a list.

        Arrange: Create list and movie
        Act: Add movie to list
        Assert: Movie is in list with correct position
        """
        # Arrange
        list_obj = list_service.create_list(user, "Movies")

        # Act
        list_item = list_service.add_media_to_list(list_obj, sample_movie)

        # Assert
        assert list_item.media == sample_movie
        assert list_item.list == list_obj
        assert list_item.position == 1

    def test_add_tv_show_to_list(self, list_service, user, sample_tv_show) -> None:
        """
        Test adding a TV show to a list.

        Arrange: Create list and TV show
        Act: Add TV show to list
        Assert: TV show is in list
        """
        # Arrange
        list_obj = list_service.create_list(user, "TV Shows")

        # Act
        list_item = list_service.add_media_to_list(list_obj, sample_tv_show)

        # Assert
        assert list_item.media == sample_tv_show
        assert list_item.list == list_obj

    def test_add_multiple_media_increments_position(self, list_service, user, sample_movie, sample_tv_show) -> None:
        """
        Test adding multiple media items increments position correctly.

        Arrange: Create list and two media items
        Act: Add both to list
        Assert: Positions are sequential (1, 2)
        """
        # Arrange
        list_obj = list_service.create_list(user, "Mixed")

        # Act
        item1 = list_service.add_media_to_list(list_obj, sample_movie)
        item2 = list_service.add_media_to_list(list_obj, sample_tv_show)

        # Assert
        assert item1.position == 1
        assert item2.position == 2

    def test_add_duplicate_media_raises_error(self, list_service, user, sample_movie) -> None:
        """
        Test adding the same media twice raises ValueError.

        Arrange: Add media to list
        Act: Try to add same media again
        Assert: ValueError is raised
        """
        # Arrange
        list_obj = list_service.create_list(user, "No Duplicates")
        list_service.add_media_to_list(list_obj, sample_movie)

        # Act & Assert
        with pytest.raises(ValueError, match="already in this list"):
            list_service.add_media_to_list(list_obj, sample_movie)


@pytest.mark.django_db
class TestListServiceRemoveMedia:
    """Test cases for removing media from lists."""

    def test_remove_media_from_list(self, list_service, user, sample_movie) -> None:
        """
        Test removing media from a list.

        Arrange: Add media to list
        Act: Remove media
        Assert: Media is no longer in list
        """
        # Arrange
        list_obj = list_service.create_list(user, "Test List")
        list_service.add_media_to_list(list_obj, sample_movie)

        # Act
        removed = list_service.remove_media_from_list(list_obj, sample_movie)

        # Assert
        assert removed is True
        assert not ListItem.objects.filter(list=list_obj, media=sample_movie).exists()

    def test_remove_nonexistent_media_returns_false(self, list_service, user, sample_movie) -> None:
        """
        Test removing media that isn't in the list.

        Arrange: Create empty list
        Act: Try to remove media
        Assert: Returns False
        """
        # Arrange
        list_obj = list_service.create_list(user, "Empty")

        # Act
        removed = list_service.remove_media_from_list(list_obj, sample_movie)

        # Assert
        assert removed is False


@pytest.mark.django_db
class TestListServiceMoveItems:
    """Test cases for moving items between lists."""

    def test_move_item_to_another_list(self, list_service, user, sample_movie) -> None:
        """
        Test moving an item from one list to another.

        Arrange: Create two lists, add item to first
        Act: Move item to second list
        Assert: Item is in second list, not in first
        """
        # Arrange
        list1 = list_service.create_list(user, "List 1")
        list2 = list_service.create_list(user, "List 2")
        list_item = list_service.add_media_to_list(list1, sample_movie)

        # Act
        moved_item = list_service.move_item_to_list(list_item, list2)

        # Assert
        assert moved_item.list == list2
        assert not ListItem.objects.filter(list=list1, media=sample_movie).exists()

    def test_move_item_between_different_users_raises_error(self, list_service, user, another_user, sample_movie) -> None:
        """
        Test moving item between lists of different users raises error.

        Arrange: Create lists for two users
        Act: Try to move item from user1's list to user2's list
        Assert: ValueError is raised
        """
        # Arrange
        list1 = list_service.create_list(user, "User 1 List")
        list2 = list_service.create_list(another_user, "User 2 List")
        list_item = list_service.add_media_to_list(list1, sample_movie)

        # Act & Assert
        with pytest.raises(ValueError, match="different users"):
            list_service.move_item_to_list(list_item, list2)

    def test_move_item_to_list_with_duplicate_raises_error(self, list_service, user, sample_movie) -> None:
        """
        Test moving item to list that already has that media.

        Arrange: Add same media to two lists
        Act: Try to move item from list1 to list2
        Assert: ValueError is raised
        """
        # Arrange
        list1 = list_service.create_list(user, "List 1")
        list2 = list_service.create_list(user, "List 2")
        list_item = list_service.add_media_to_list(list1, sample_movie)
        list_service.add_media_to_list(list2, sample_movie)

        # Act & Assert
        with pytest.raises(ValueError, match="already in the target list"):
            list_service.move_item_to_list(list_item, list2)


@pytest.mark.django_db
class TestListServiceGetLists:
    """Test cases for retrieving user lists."""

    def test_get_user_lists_all(self, list_service, user) -> None:
        """
        Test getting all lists for a user.

        Arrange: Create 3 lists (2 private, 1 public)
        Act: Get all user lists
        Assert: All 3 lists are returned
        """
        # Arrange
        list_service.create_list(user, "Private 1", is_public=False)
        list_service.create_list(user, "Public", is_public=True)
        list_service.create_list(user, "Private 2", is_public=False)

        # Act
        lists = list_service.get_user_lists(user, include_private=True)

        # Assert
        assert len(lists) == 3

    def test_get_user_lists_public_only(self, list_service, user) -> None:
        """
        Test getting only public lists.

        Arrange: Create 2 private and 1 public list
        Act: Get public lists only
        Assert: Only 1 list is returned
        """
        # Arrange
        list_service.create_list(user, "Private 1", is_public=False)
        list_service.create_list(user, "Public", is_public=True)
        list_service.create_list(user, "Private 2", is_public=False)

        # Act
        lists = list_service.get_user_lists(user, include_private=False)

        # Assert
        assert len(lists) == 1
        assert lists[0].name == "Public"


@pytest.mark.django_db
class TestListServiceGetItems:
    """Test cases for retrieving list items."""

    def test_get_list_items_ordered_by_position(self, list_service, user, sample_movie, sample_tv_show) -> None:
        """
        Test getting list items ordered by position.

        Arrange: Create list with 2 items
        Act: Get list items
        Assert: Items are in correct order
        """
        # Arrange
        list_obj = list_service.create_list(user, "Ordered")
        list_service.add_media_to_list(list_obj, sample_movie)
        list_service.add_media_to_list(list_obj, sample_tv_show)

        # Act
        items = list_service.get_list_items(list_obj)

        # Assert
        assert len(items) == 2
        assert items[0].media.id == sample_movie.id
        assert items[1].media.id == sample_tv_show.id
        assert items[0].position < items[1].position

    def test_get_empty_list_items(self, list_service, user) -> None:
        """
        Test getting items from an empty list.

        Arrange: Create empty list
        Act: Get list items
        Assert: Empty list is returned
        """
        # Arrange
        list_obj = list_service.create_list(user, "Empty")

        # Act
        items = list_service.get_list_items(list_obj)

        # Assert
        assert len(items) == 0
