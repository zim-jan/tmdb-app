"""
List and ListItem models for user content organization.

This module contains models for user-created lists and their items.
"""

from django.db import models


class WatchStatus(models.TextChoices):
    """
    Enumeration of watch statuses for list items.

    Attributes
    ----------
    PLANNED : str
        User plans to watch this item.
    IN_PROGRESS : str
        User is currently watching this item.
    WATCHED : str
        User has finished watching this item.
    """

    PLANNED = "PLANNED", "Planned"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    WATCHED = "WATCHED", "Watched"


class List(models.Model):
    """
    Model for user-created lists.

    Lists are collections of movies or TV shows that users create
    to organize their content. Lists are private by default.

    Attributes
    ----------
    name : str
        Name of the list.
    user : User
        Owner of the list.
    is_public : bool
        Whether the list is publicly visible (default: False).
    created_at : datetime
        Timestamp when the list was created.
    updated_at : datetime
        Timestamp when the list was last updated.
    """

    name = models.CharField(
        max_length=255,
        help_text="Name of the list",
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="lists",
        help_text="Owner of the list",
    )
    is_public = models.BooleanField(
        default=False,
        help_text="Whether the list is publicly visible",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the list was created",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the list was last updated",
    )

    class Meta:
        """Meta options for List model."""

        db_table = "lists"
        ordering = ["-created_at"]
        verbose_name = "List"
        verbose_name_plural = "Lists"
        indexes = [
            models.Index(fields=["user", "is_public"]),
        ]

    def __str__(self) -> str:
        """
        Return string representation of the list.

        Returns
        -------
        str
            Name of the list.
        """
        return self.name


class ListItem(models.Model):
    """
    Model for items within a list.

    Represents a single movie or TV show added to a user's list.

    Attributes
    ----------
    list : List
        The list this item belongs to.
    media : Media
        The media content (Movie or TVShow) in this list item.
    added_at : datetime
        Timestamp when the item was added to the list.
    position : int
        Position of the item within the list for ordering.
    status : str
        Watch status (planned/in-progress/watched).
    """

    list = models.ForeignKey(
        List,
        on_delete=models.CASCADE,
        related_name="items",
        help_text="The list this item belongs to",
    )
    media = models.ForeignKey(
        "media.Media",
        on_delete=models.CASCADE,
        related_name="list_items",
        help_text="The media content (Movie or TVShow) in this list item",
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the item was added to the list",
    )
    position = models.IntegerField(
        default=0,
        help_text="Position of the item within the list for ordering",
    )
    status = models.CharField(
        max_length=20,
        choices=WatchStatus.choices,
        default=WatchStatus.PLANNED,
        help_text="Watch status of this item",
    )

    class Meta:
        """Meta options for ListItem model."""

        db_table = "list_items"
        ordering = ["position", "-added_at"]
        verbose_name = "List Item"
        verbose_name_plural = "List Items"
        unique_together = ["list", "media"]
        indexes = [
            models.Index(fields=["list", "position"]),
        ]

    def __str__(self) -> str:
        """
        Return string representation of the list item.

        Returns
        -------
        str
            Description of the list item.
        """
        return f"{self.media.title} in {self.list.name}"
