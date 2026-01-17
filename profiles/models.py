"""
Public Profile model for user profile sharing.

This module contains the PublicProfile model that represents
a user's public profile accessible via /u/<nickname>.
"""

from django.db import models


class PublicProfile(models.Model):
    """
    Model for user public profiles.

    Public profiles allow users to share their viewing activity
    and lists with others. The profile is read-only for viewers.

    Attributes
    ----------
    user : User
        The user this profile belongs to (one-to-one relationship).
    bio : str
        User's biography or description.
    avatar_url : str
        URL to the user's avatar image.
    is_visible : bool
        Whether the profile is publicly visible (default: True).
    show_watched_episodes : bool
        Whether to show watched episodes on the public profile.
    show_lists : bool
        Whether to show public lists on the public profile.
    created_at : datetime
        Timestamp when the profile was created.
    updated_at : datetime
        Timestamp when the profile was last updated.
    """

    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="public_profile",
        help_text="The user this profile belongs to",
    )
    bio = models.TextField(
        blank=True,
        max_length=500,
        help_text="User's biography or description",
    )
    avatar_url = models.URLField(
        blank=True,
        help_text="URL to the user's avatar image",
    )
    is_visible = models.BooleanField(
        default=True,
        help_text="Whether the profile is publicly visible",
    )
    show_watched_episodes = models.BooleanField(
        default=True,
        help_text="Whether to show watched episodes on the public profile",
    )
    show_lists = models.BooleanField(
        default=True,
        help_text="Whether to show public lists on the public profile",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the profile was created",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the profile was last updated",
    )

    class Meta:
        """Meta options for PublicProfile model."""

        db_table = "public_profiles"
        verbose_name = "Public Profile"
        verbose_name_plural = "Public Profiles"

    def __str__(self) -> str:
        """
        Return string representation of the public profile.

        Returns
        -------
        str
            Username of the profile owner.
        """
        return f"{self.user.nickname}'s profile"
