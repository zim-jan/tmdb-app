"""
Views for list management.

This module contains views for creating, editing, and managing user lists.
"""

import logging

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from lists.forms import ListForm
from lists.models import List, ListItem, WatchStatus
from lists.services import ListService
from media.models import Media

logger = logging.getLogger(__name__)

@login_required
def my_lists_view(request: HttpRequest) -> HttpResponse:
    """
    Display user's lists.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        Rendered my lists page.
    """
    list_service = ListService()
    user_lists = list_service.get_user_lists(request.user)

    return render(request, "lists/my_lists.html", {
        "lists": user_lists,
    })


@login_required
def create_list_view(request: HttpRequest) -> HttpResponse:
    """
    Create a new list.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        Rendered create list page or redirect to list detail.
    """
    if request.method == "POST":
        form = ListForm(request.POST)
        if form.is_valid():
            list_service = ListService()
            try:
                new_list = list_service.create_list(
                    user=request.user,
                    name=form.cleaned_data["name"],
                    is_public=form.cleaned_data["is_public"],
                )
                messages.success(request, f"List '{new_list.name}' created successfully!")
                return redirect("lists:detail", list_id=new_list.id)
            except Exception as e:
                messages.error(request, f"Error creating list: {str(e)}")
    else:
        form = ListForm()

    return render(request, "lists/create_list.html", {"form": form})


@login_required
def list_detail_view(request: HttpRequest, list_id: int) -> HttpResponse:
    """
    Display list details with items.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    list_id : int
        ID of the list to display.

    Returns
    -------
    HttpResponse
        Rendered list detail page.
    """
    from media.services import TMDbService

    list_obj = get_object_or_404(List, id=list_id, user=request.user)
    list_service = ListService()
    items = list_service.get_list_items(list_obj)
    user_lists = list_service.get_user_lists(request.user)

    # Enrich items with TMDb data
    tmdb_service = TMDbService()
    enriched_items = []

    for item in items:
        item_data = {
            'item': item,
            'poster_path': None,
            'backdrop_path': None,
            'rating': 0,
            'imdb_id': None,
        }

        # Only fetch TMDb data if tmdb_id exists
        if item.media.tmdb_id:
            try:
                if item.media.media_type == 'MOVIE':
                    details = tmdb_service.get_movie_details(item.media.tmdb_id)
                    # Get TMDb external IDs
                    external_ids = tmdb_service._make_request(f'/movie/{item.media.tmdb_id}/external_ids')
                    item_data['imdb_id'] = external_ids.get('imdb_id')
                else:
                    details = tmdb_service.get_tv_details(item.media.tmdb_id)
                    # Get TMDb external IDs
                    external_ids = tmdb_service._make_request(f'/tv/{item.media.tmdb_id}/external_ids')
                    item_data['imdb_id'] = external_ids.get('imdb_id')

                item_data['poster_path'] = details.get('poster_path')
                item_data['backdrop_path'] = details.get('backdrop_path')
                item_data['rating'] = details.get('vote_average', 0)
            except requests.RequestException as e:
                logger.warning(
                    "Failed to fetch TMDb data for media_id=%s: %s",
                    item.media.id,
                    str(e),
                    extra={'media_id': item.media.id, 'tmdb_id': item.media.tmdb_id}
                )
            except Exception as e:
                logger.error(
                    "Unexpected error fetching TMDb data for media_id=%s",
                    item.media.id,
                    exc_info=True,
                    extra={'media_id': item.media.id, 'tmdb_id': item.media.tmdb_id}
                )

        enriched_items.append(item_data)

    return render(request, "lists/list_detail.html", {
        "list": list_obj,
        "items": enriched_items,
        "user_lists": user_lists,
    })


@login_required
def edit_list_view(request: HttpRequest, list_id: int) -> HttpResponse:
    """
    Edit an existing list.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    list_id : int
        ID of the list to edit.

    Returns
    -------
    HttpResponse
        Rendered edit list page or redirect to list detail.
    """
    list_obj = get_object_or_404(List, id=list_id, user=request.user)

    if request.method == "POST":
        form = ListForm(request.POST, instance=list_obj)
        if form.is_valid():
            list_service = ListService()
            try:
                list_service.update_list(
                    list_obj=list_obj,
                    name=form.cleaned_data["name"],
                    is_public=form.cleaned_data["is_public"],
                )
                messages.success(request, f"List '{list_obj.name}' updated successfully!")
                return redirect("lists:detail", list_id=list_obj.id)
            except Exception as e:
                messages.error(request, f"Error updating list: {str(e)}")
    else:
        form = ListForm(instance=list_obj)

    return render(request, "lists/edit_list.html", {
        "form": form,
        "list": list_obj,
    })


@login_required
@require_POST
def delete_list_view(request: HttpRequest, list_id: int) -> HttpResponse:
    """
    Delete a list.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    list_id : int
        ID of the list to delete.

    Returns
    -------
    HttpResponse
        Redirect to my lists page.
    """
    list_obj = get_object_or_404(List, id=list_id, user=request.user)
    list_name = list_obj.name

    list_service = ListService()
    list_service.delete_list(list_obj)

    messages.success(request, f"List '{list_name}' deleted successfully!")
    return redirect("lists:my_lists")


@login_required
@require_POST
def remove_from_list_view(request: HttpRequest, list_id: int, media_id: int) -> HttpResponse:
    """
    Remove media from a list.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    list_id : int
        ID of the list.
    media_id : int
        ID of the media to remove.

    Returns
    -------
    HttpResponse
        Redirect to list detail page.
    """
    list_obj = get_object_or_404(List, id=list_id, user=request.user)
    media = get_object_or_404(Media, id=media_id)

    list_service = ListService()
    removed = list_service.remove_media_from_list(list_obj, media)

    if removed:
        messages.success(request, f"'{media.title}' removed from '{list_obj.name}'")
    else:
        messages.warning(request, "Item not found in this list")

    return redirect("lists:detail", list_id=list_id)


@login_required
@require_POST
def move_item_view(request: HttpRequest, item_id: int) -> HttpResponse:
    """
    Move an item to another list.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    item_id : int
        ID of the list item to move.

    Returns
    -------
    HttpResponse
        JSON response or redirect.
    """
    item = get_object_or_404(ListItem, id=item_id, list__user=request.user)
    target_list_id = request.POST.get("target_list_id")

    if not target_list_id:
        messages.error(request, "No target list specified")
        return redirect("lists:detail", list_id=item.list.id)

    target_list = get_object_or_404(List, id=target_list_id, user=request.user)

    list_service = ListService()
    try:
        list_service.move_item_to_list(item, target_list)
        messages.success(request, f"'{item.media.title}' moved to '{target_list.name}'")
    except ValueError as e:
        messages.error(request, str(e))

    return redirect("lists:detail", list_id=target_list.id)


@login_required
@require_POST
def update_item_status_view(request: HttpRequest, item_id: int) -> HttpResponse:
    """
    Update the watch status of a list item.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    item_id : int
        ID of the list item to update.

    Returns
    -------
    HttpResponse
        JSON response with updated status.
    """
    item = get_object_or_404(ListItem, id=item_id, list__user=request.user)
    new_status = request.POST.get("status")

    if new_status not in [choice[0] for choice in WatchStatus.choices]:
        return JsonResponse({"error": "Invalid status"}, status=400)

    item.status = new_status
    item.save()

    return JsonResponse({
        "success": True,
        "item_id": item_id,
        "status": new_status,
        "status_display": item.get_status_display(),
    })
