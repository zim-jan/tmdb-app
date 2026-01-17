"""
List management service.

This module provides service layer for managing user lists and list items.
"""

from django.db import transaction
from django.db.models import Max

from lists.models import List, ListItem
from media.models import Media
from users.models import User


class ListService:
    """
    Service for managing user lists.

    This service provides business logic for creating, updating,
    and managing user lists and their items.
    """

    @transaction.atomic
    def create_list(self, user: User, name: str, is_public: bool = False) -> List:
        """
        Create a new list for a user.

        Parameters
        ----------
        user : User
            Owner of the list.
        name : str
            Name of the list.
        is_public : bool
            Whether the list should be public (default: False).

        Returns
        -------
        List
            Created list object.
        """
        list_obj = List.objects.create(
            user=user,
            name=name,
            is_public=is_public,
        )
        return list_obj

    @transaction.atomic
    def update_list(self, list_obj: List, name: str | None = None, is_public: bool | None = None) -> List:
        """
        Update list properties.

        Parameters
        ----------
        list_obj : List
            List to update.
        name : str | None
            New name for the list (optional).
        is_public : bool | None
            New public status (optional).

        Returns
        -------
        List
            Updated list object.
        """
        if name is not None:
            list_obj.name = name

        if is_public is not None:
            list_obj.is_public = is_public

        list_obj.save()
        return list_obj

    @transaction.atomic
    def delete_list(self, list_obj: List) -> None:
        """
        Delete a list and all its items.

        Parameters
        ----------
        list_obj : List
            List to delete.
        """
        list_obj.delete()

    @transaction.atomic
    def add_media_to_list(self, list_obj: List, media: Media) -> ListItem:
        """
        Add media to a list.

        Parameters
        ----------
        list_obj : List
            List to add media to.
        media : Media
            Media to add to the list.

        Returns
        -------
        ListItem
            Created list item.

        Raises
        ------
        ValueError
            If media is already in the list.
        """
        # Check if media is already in the list
        if ListItem.objects.filter(list=list_obj, media=media).exists():
            raise ValueError("Media is already in this list")

        # Get the next position
        max_position = ListItem.objects.filter(list=list_obj).aggregate(Max("position"))["position__max"]
        next_position = (max_position or 0) + 1

        # Create list item
        list_item = ListItem.objects.create(
            list=list_obj,
            media=media,
            position=next_position,
        )

        return list_item

    @transaction.atomic
    def remove_media_from_list(self, list_obj: List, media: Media) -> bool:
        """
        Remove media from a list.

        Parameters
        ----------
        list_obj : List
            List to remove media from.
        media : Media
            Media to remove from the list.

        Returns
        -------
        bool
            True if media was removed, False if it wasn't in the list.
        """
        deleted_count, _ = ListItem.objects.filter(
            list=list_obj,
            media=media,
        ).delete()

        return deleted_count > 0

    @transaction.atomic
    def move_item_to_list(self, list_item: ListItem, target_list: List) -> ListItem:
        """
        Move an item from one list to another.

        Parameters
        ----------
        list_item : ListItem
            Item to move.
        target_list : List
            Target list to move the item to.

        Returns
        -------
        ListItem
            The list item in the new list.

        Raises
        ------
        ValueError
            If media is already in the target list or lists belong to different users.
        """
        # Verify lists belong to the same user
        if list_item.list.user != target_list.user:
            raise ValueError("Cannot move items between lists of different users")

        # Check if media is already in target list
        if ListItem.objects.filter(list=target_list, media=list_item.media).exists():
            raise ValueError("Media is already in the target list")

        # Get the next position in target list
        max_position = ListItem.objects.filter(list=target_list).aggregate(Max("position"))["position__max"]
        next_position = (max_position or 0) + 1

        # Move the item
        list_item.list = target_list
        list_item.position = next_position
        list_item.save()

        return list_item

    @transaction.atomic
    def reorder_items(self, list_obj: List, item_order: list[int]) -> None:
        """
        Reorder items in a list.

        Parameters
        ----------
        list_obj : List
            List to reorder items in.
        item_order : list[int]
            List of ListItem IDs in the desired order.
        """
        for position, item_id in enumerate(item_order, start=1):
            ListItem.objects.filter(
                id=item_id,
                list=list_obj,
            ).update(position=position)

    def get_user_lists(self, user: User, include_private: bool = True) -> list[List]:
        """
        Get all lists for a user.

        Parameters
        ----------
        user : User
            User whose lists to retrieve.
        include_private : bool
            Whether to include private lists (default: True).

        Returns
        -------
        list[List]
            List of user's lists.
        """
        queryset = List.objects.filter(user=user)

        if not include_private:
            queryset = queryset.filter(is_public=True)

        return list(queryset.order_by("-created_at"))

    def get_list_items(self, list_obj: List) -> list[ListItem]:
        """
        Get all items in a list.

        Parameters
        ----------
        list_obj : List
            List to get items from.

        Returns
        -------
        list[ListItem]
            List of items ordered by position.
        """
        return list(
            ListItem.objects.filter(list=list_obj)
            .select_related("media")
            .order_by("position")
        )
