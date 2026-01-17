"""
Custom User model for the application.

This module extends Django's AbstractUser to provide custom user
functionality for the movie tracking application.
"""


from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.

    Attributes
    ----------
    email : str
        User's email address (required and unique).
    nickname : str
        User's public nickname for profile sharing (unique).
    is_2fa_enabled : bool
        Whether two-factor authentication is enabled.
    created_at : datetime
        Timestamp when the user account was created.
    updated_at : datetime
        Timestamp when the user account was last updated.
    """

    email = models.EmailField(
        unique=True,
        help_text="User's email address",
    )
    nickname = models.CharField(
        max_length=50,
        unique=True,
        help_text="User's public nickname for profile sharing",
    )
    is_2fa_enabled = models.BooleanField(
        default=False,
        help_text="Whether two-factor authentication is enabled",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the user account was created",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the user account was last updated",
    )

    class Meta:
        """Meta options for User model."""

        db_table = "users"
        ordering = ["-created_at"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        """
        Return string representation of the user.

        Returns
        -------
        str
            Username of the user.
        """
        return self.username
