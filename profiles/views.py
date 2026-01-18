
"""
Views for public profiles.

This module contains views for managing and displaying public user profiles.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from lists.services import ListService
from media.models import WatchedEpisode
from profiles.services import ProfileService


def public_profile_view(request: HttpRequest, nickname: str) -> HttpResponse:
    """
    Display public profile by nickname.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    nickname : str
        User's nickname.

    Returns
    -------
    HttpResponse
        Rendered public profile page or 404.
    """
    profile_service = ProfileService()
    profile = profile_service.get_profile_by_nickname(nickname)

    if not profile:
        messages.error(request, "Profile not found or not public")
        return redirect("index")

    user = profile.user
    list_service = ListService()

    # Get public lists if allowed
    public_lists = []
    if profile.show_lists:
        public_lists = list_service.get_user_lists(user, include_private=False)

    # Get watched episodes if allowed
    watched_episodes = []
    if profile.show_watched_episodes:
        watched_episodes = WatchedEpisode.objects.filter(
            user=user
        ).select_related("tv_show").order_by("-watched_at")[:20]

    # Calculate stats
    total_lists = len(list_service.get_user_lists(user))
    total_watched = WatchedEpisode.objects.filter(user=user).count()

    return render(request, "profiles/public_profile.html", {
        "profile": profile,
        "profile_user": user,
        "public_lists": public_lists,
        "watched_episodes": watched_episodes,
        "total_lists": total_lists,
        "total_watched": total_watched,
    })


@login_required
def edit_profile_view(request: HttpRequest) -> HttpResponse:
    """
    Edit user profile and privacy settings.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        Rendered profile edit page.
    """
    profile_service = ProfileService()
    profile = profile_service.get_or_create_profile(request.user)

    if request.method == "POST":
        try:
            profile_service.update_profile(
                profile=profile,
                bio=request.POST.get("bio", ""),
                avatar_url=request.POST.get("avatar_url", ""),
                is_visible=request.POST.get("is_visible") == "on",
                show_watched_episodes=request.POST.get("show_watched_episodes") == "on",
                show_lists=request.POST.get("show_lists") == "on",
            )
            messages.success(request, "Profile updated successfully!")
            return redirect("users:profile")
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")

    return render(request, "profiles/edit_profile.html", {
        "profile": profile,
    })
