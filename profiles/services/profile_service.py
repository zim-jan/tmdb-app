"""
Profile management service.

This module provides service layer for managing user public profiles.
"""

from django.db import transaction

from profiles.models import PublicProfile
from users.models import User


class ProfileService:
    """
    Service for managing user public profiles.

    This service provides business logic for creating, updating,
    and managing user public profiles.
    """

    @transaction.atomic
    def create_profile(self, user: User) -> PublicProfile:
        """
        Create a public profile for a user.

        Parameters
        ----------
        user : User
            User to create profile for.

        Returns
        -------
        PublicProfile
            Created public profile.

        Raises
        ------
        ValueError
            If user already has a profile.
        """
        if hasattr(user, "public_profile"):
            raise ValueError("User already has a public profile")

        profile = PublicProfile.objects.create(user=user)
        return profile

    @transaction.atomic
    def update_profile(
        self,
        profile: PublicProfile,
        bio: str | None = None,
        avatar_url: str | None = None,
        is_visible: bool | None = None,
        show_watched_episodes: bool | None = None,
        show_lists: bool | None = None,
    ) -> PublicProfile:
        """
        Update public profile properties.

        Parameters
        ----------
        profile : PublicProfile
            Profile to update.
        bio : str | None
            New biography (optional).
        avatar_url : str | None
            New avatar URL (optional).
        is_visible : bool | None
            New visibility status (optional).
        show_watched_episodes : bool | None
            Whether to show watched episodes (optional).
        show_lists : bool | None
            Whether to show lists (optional).

        Returns
        -------
        PublicProfile
            Updated profile.
        """
        if bio is not None:
            profile.bio = bio

        if avatar_url is not None:
            profile.avatar_url = avatar_url

        if is_visible is not None:
            profile.is_visible = is_visible

        if show_watched_episodes is not None:
            profile.show_watched_episodes = show_watched_episodes

        if show_lists is not None:
            profile.show_lists = show_lists

        profile.save()
        return profile

    def get_profile_by_nickname(self, nickname: str) -> PublicProfile | None:
        """
        Get public profile by user nickname.

        Parameters
        ----------
        nickname : str
            User's nickname.

        Returns
        -------
        PublicProfile | None
            Public profile if found and visible, None otherwise.
        """
        try:
            profile = PublicProfile.objects.select_related("user").get(
                user__nickname=nickname,
                is_visible=True,
            )
            return profile
        except PublicProfile.DoesNotExist:
            return None

    def get_or_create_profile(self, user: User) -> PublicProfile:
        """
        Get or create a public profile for a user.

        Parameters
        ----------
        user : User
            User to get or create profile for.

        Returns
        -------
        PublicProfile
            User's public profile.
        """
        profile, _ = PublicProfile.objects.get_or_create(user=user)
        return profile
