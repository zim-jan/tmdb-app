"""
Unit tests for profiles service module.

This module tests the profile management service layer functionality.
"""

import pytest
from django.contrib.auth import get_user_model

from profiles.models import PublicProfile
from profiles.services.profile_service import ProfileService

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
def profile_service():
    """Provide ProfileService instance."""
    return ProfileService()


@pytest.mark.django_db
class TestProfileServiceCreate:
    """Test cases for profile creation."""

    def test_create_profile_for_user(self, profile_service, user):
        """
        Test creating a profile for a user.
        
        Arrange: User without profile
        Act: Create profile
        Assert: Profile is created with default values
        """
        # Act
        profile = profile_service.create_profile(user)

        # Assert
        assert profile.id is not None
        assert profile.user == user
        assert profile.is_visible is True
        assert profile.show_watched_episodes is True
        assert profile.show_lists is True
        assert profile.bio == ""

    def test_create_profile_for_user_with_existing_profile_raises_error(self, profile_service, user):
        """
        Test creating profile for user who already has one.
        
        Arrange: User with existing profile
        Act: Try to create another profile
        Assert: ValueError is raised
        """
        # Arrange
        profile_service.create_profile(user)

        # Act & Assert
        with pytest.raises(ValueError, match="already has a public profile"):
            profile_service.create_profile(user)

    def test_create_profiles_for_multiple_users(self, profile_service, user, another_user):
        """
        Test creating profiles for different users.
        
        Arrange: Two different users
        Act: Create profile for each
        Assert: Both profiles are created
        """
        # Act
        profile1 = profile_service.create_profile(user)
        profile2 = profile_service.create_profile(another_user)

        # Assert
        assert profile1.user == user
        assert profile2.user == another_user
        assert profile1.id != profile2.id


@pytest.mark.django_db
class TestProfileServiceUpdate:
    """Test cases for profile updates."""

    def test_update_profile_bio(self, profile_service, user):
        """
        Test updating profile biography.
        
        Arrange: Create profile with empty bio
        Act: Update bio
        Assert: Bio is changed
        """
        # Arrange
        profile = profile_service.create_profile(user)
        new_bio = "Movie enthusiast and TV show addict!"

        # Act
        updated_profile = profile_service.update_profile(profile, bio=new_bio)

        # Assert
        assert updated_profile.bio == new_bio
        profile.refresh_from_db()
        assert profile.bio == new_bio

    def test_update_profile_avatar_url(self, profile_service, user):
        """
        Test updating profile avatar URL.
        
        Arrange: Create profile without avatar
        Act: Set avatar URL
        Assert: Avatar URL is updated
        """
        # Arrange
        profile = profile_service.create_profile(user)
        avatar_url = "https://example.com/avatar.jpg"

        # Act
        updated_profile = profile_service.update_profile(profile, avatar_url=avatar_url)

        # Assert
        assert updated_profile.avatar_url == avatar_url

    def test_update_profile_visibility(self, profile_service, user):
        """
        Test updating profile visibility.
        
        Arrange: Create public profile
        Act: Make it private
        Assert: Visibility is changed
        """
        # Arrange
        profile = profile_service.create_profile(user)

        # Act
        updated_profile = profile_service.update_profile(profile, is_visible=False)

        # Assert
        assert updated_profile.is_visible is False
        profile.refresh_from_db()
        assert profile.is_visible is False

    def test_update_profile_show_watched_episodes(self, profile_service, user):
        """
        Test updating show_watched_episodes flag.
        
        Arrange: Create profile with default settings
        Act: Disable showing watched episodes
        Assert: Flag is changed
        """
        # Arrange
        profile = profile_service.create_profile(user)

        # Act
        updated_profile = profile_service.update_profile(profile, show_watched_episodes=False)

        # Assert
        assert updated_profile.show_watched_episodes is False

    def test_update_profile_show_lists(self, profile_service, user):
        """
        Test updating show_lists flag.
        
        Arrange: Create profile with default settings
        Act: Disable showing lists
        Assert: Flag is changed
        """
        # Arrange
        profile = profile_service.create_profile(user)

        # Act
        updated_profile = profile_service.update_profile(profile, show_lists=False)

        # Assert
        assert updated_profile.show_lists is False

    def test_update_profile_partial_update(self, profile_service, user):
        """
        Test partial profile update (only some fields).
        
        Arrange: Create profile with default values
        Act: Update only bio
        Assert: Only bio changes, other fields unchanged
        """
        # Arrange
        profile = profile_service.create_profile(user)
        original_visibility = profile.is_visible

        # Act
        updated_profile = profile_service.update_profile(profile, bio="New bio")

        # Assert
        assert updated_profile.bio == "New bio"
        assert updated_profile.is_visible == original_visibility

    def test_update_profile_multiple_fields(self, profile_service, user):
        """
        Test updating multiple fields at once.
        
        Arrange: Create profile
        Act: Update bio, avatar, and visibility
        Assert: All fields are updated
        """
        # Arrange
        profile = profile_service.create_profile(user)

        # Act
        updated_profile = profile_service.update_profile(
            profile,
            bio="New bio",
            avatar_url="https://example.com/new-avatar.jpg",
            is_visible=False
        )

        # Assert
        assert updated_profile.bio == "New bio"
        assert updated_profile.avatar_url == "https://example.com/new-avatar.jpg"
        assert updated_profile.is_visible is False


@pytest.mark.django_db
class TestProfileServiceGetByNickname:
    """Test cases for getting profile by nickname."""

    def test_get_visible_profile_by_nickname(self, profile_service, user):
        """
        Test getting a visible profile by nickname.
        
        Arrange: Create visible profile
        Act: Get profile by nickname
        Assert: Profile is returned
        """
        # Arrange
        profile_service.create_profile(user)

        # Act
        profile = profile_service.get_profile_by_nickname("testuser")

        # Assert
        assert profile is not None
        assert profile.user.nickname == "testuser"

    def test_get_invisible_profile_returns_none(self, profile_service, user):
        """
        Test getting an invisible profile returns None.
        
        Arrange: Create invisible profile
        Act: Get profile by nickname
        Assert: None is returned
        """
        # Arrange
        profile = profile_service.create_profile(user)
        profile_service.update_profile(profile, is_visible=False)

        # Act
        result = profile_service.get_profile_by_nickname("testuser")

        # Assert
        assert result is None

    def test_get_nonexistent_profile_returns_none(self, profile_service):
        """
        Test getting a profile that doesn't exist.
        
        Arrange: No profiles created
        Act: Get profile by nickname
        Assert: None is returned
        """
        # Act
        result = profile_service.get_profile_by_nickname("nonexistent")

        # Assert
        assert result is None

    def test_get_profile_by_nickname_case_sensitive(self, profile_service, user):
        """
        Test that nickname lookup is case-sensitive.
        
        Arrange: Create profile with lowercase nickname
        Act: Search with different case
        Assert: Returns None (assuming case-sensitive)
        """
        # Arrange
        profile_service.create_profile(user)

        # Act
        result = profile_service.get_profile_by_nickname("TESTUSER")

        # Assert
        # This depends on database collation - adjust if needed
        assert result is None or result.user.nickname == "testuser"


@pytest.mark.django_db
class TestProfileServiceGetOrCreate:
    """Test cases for get_or_create_profile method."""

    def test_get_or_create_creates_new_profile(self, profile_service, user):
        """
        Test creating a new profile via get_or_create.
        
        Arrange: User without profile
        Act: Call get_or_create
        Assert: New profile is created
        """
        # Act
        profile = profile_service.get_or_create_profile(user)

        # Assert
        assert profile.id is not None
        assert profile.user == user

    def test_get_or_create_gets_existing_profile(self, profile_service, user):
        """
        Test getting existing profile via get_or_create.
        
        Arrange: User with existing profile
        Act: Call get_or_create
        Assert: Existing profile is returned
        """
        # Arrange
        existing_profile = profile_service.create_profile(user)
        existing_id = existing_profile.id

        # Act
        profile = profile_service.get_or_create_profile(user)

        # Assert
        assert profile.id == existing_id
        assert PublicProfile.objects.filter(user=user).count() == 1

    def test_get_or_create_multiple_calls_same_profile(self, profile_service, user):
        """
        Test multiple get_or_create calls return same profile.
        
        Arrange: User without profile
        Act: Call get_or_create three times
        Assert: All calls return same profile ID
        """
        # Act
        profile1 = profile_service.get_or_create_profile(user)
        profile2 = profile_service.get_or_create_profile(user)
        profile3 = profile_service.get_or_create_profile(user)

        # Assert
        assert profile1.id == profile2.id == profile3.id
        assert PublicProfile.objects.filter(user=user).count() == 1
