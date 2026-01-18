
"""
Views for media browsing and management.

This module contains views for searching and adding media to lists.
"""

import logging

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from lists.models import List, ListItem, WatchStatus
from lists.services import ListService
from media.forms import ManualMediaForm
from media.models import Media, TVShow, WatchedEpisode
from media.services import EpisodeTrackingService, MediaService, TMDbService

logger = logging.getLogger(__name__)


def validate_episode_numbers(season: str | None, episode: str | None) -> tuple[int, int] | None:
    """
    Validate and convert season/episode numbers to integers.

    Parameters
    ----------
    season : str | None
        Season number as string.
    episode : str | None
        Episode number as string.

    Returns
    -------
    tuple[int, int] | None
        Tuple of (season, episode) as integers, or None if invalid.
    """
    if not season or not episode:
        return None

    try:
        season_num = int(season)
        episode_num = int(episode)

        # Validate ranges
        if season_num <= 0 or episode_num <= 0:
            return None

        # Reasonable upper limits
        if season_num > 1000 or episode_num > 1000:
            return None

        return season_num, episode_num
    except (ValueError, TypeError):
        return None


@login_required
def browse_view(request: HttpRequest) -> HttpResponse:
    """
    Browse media from user's lists.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        Rendered browse page.
    """
    media_type = request.GET.get("type", "all")
    sort_by = request.GET.get("sort", "-added_at")

    # Get media from user's lists
    media_list = ListItem.objects.filter(
        list__user=request.user
    ).select_related('media').values_list('media', flat=True).distinct()
    
    # Apply media type filter
    if media_type == "movie":
        media_list = Media.objects.filter(
            id__in=media_list,
            media_type="MOVIE"
        )
    elif media_type == "tv":
        media_list = Media.objects.filter(
            id__in=media_list,
            media_type="TV_SHOW"
        )
    else:
        media_list = Media.objects.filter(id__in=media_list)
    
    # Apply sorting
    if sort_by == "title":
        media_list = media_list.order_by("title")
    elif sort_by == "-title":
        media_list = media_list.order_by("-title")
    elif sort_by == "rating":
        media_list = media_list.order_by("vote_average")
    elif sort_by == "-rating":
        media_list = media_list.order_by("-vote_average")
    else:
        media_list = media_list.order_by("-created_at")
    
    media_list = media_list[:50]

    # Enrich media using data already in database
    # (poster_path, backdrop_path, vote_average are synced from TMDb)
    enriched_media = []
    for media in media_list:
        media_dict = {
            'id': media.id,
            'tmdb_id': media.tmdb_id,
            'title': media.title,
            'media_type': media.media_type.lower().replace('_show', ''),
            'overview': media.overview or '',
            'release_date': media.release_date,
            'poster_path': media.poster_path or None,
            'backdrop_path': media.backdrop_path or None,
            'rating': media.vote_average or 0,
        }
        enriched_media.append(media_dict)

    # Get user's lists for the dropdown
    user_lists = List.objects.filter(user=request.user).order_by('name')

    return render(request, "media/browse.html", {
        "media_list": enriched_media,
        "media_type": media_type,
        "sort_by": sort_by,
        "user_lists": user_lists,
    })


@login_required
def search_view(request: HttpRequest) -> HttpResponse:
    """
    Search for media using TMDb API.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        Rendered search page with results.
    """
    query = request.GET.get("q", "")
    media_type = request.GET.get("type")
    sort_by = request.GET.get("sort", "relevance")
    results = []

    if query:
        media_service = MediaService()
        try:
            results = media_service.search_media(query, media_type, enrich=True)

            # Apply sorting
            if sort_by == "title":
                results.sort(key=lambda x: x.get("title", "").lower())
            elif sort_by == "rating":
                results.sort(key=lambda x: x.get("rating", 0), reverse=True)
            elif sort_by == "date":
                results.sort(key=lambda x: x.get("release_date") or x.get("first_air_date", ""), reverse=True)
            # Default is relevance (TMDb order)

        except Exception as e:
            messages.error(request, f"Search error: {str(e)}")
            messages.info(request, "TMDb API is currently unavailable. You can add media manually.")


    # Get user's lists for the dropdown
    user_lists = List.objects.filter(user=request.user).order_by('name')

    return render(request, "media/search.html", {
        "query": query,
        "results": results,
        "media_type": media_type,
        "sort_by": sort_by,
        "user_lists": user_lists,
    })


@login_required
def media_detail_view(request: HttpRequest, media_id: int) -> HttpResponse:
    """
    Display media details.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    media_id : int
        ID of the media to display.

    Returns
    -------
    HttpResponse
        Rendered media detail page.
    """
    media = get_object_or_404(Media, id=media_id)
    list_service = ListService()
    user_lists = list_service.get_user_lists(request.user)

    # Get TMDb details for enriched display
    tmdb_service = TMDbService()
    tmdb_data = None
    cast = []
    directors = []

    # Only fetch TMDb data if tmdb_id exists
    if media.tmdb_id:
        try:
            if media.media_type == 'MOVIE':
                details = tmdb_service.get_movie_details(media.tmdb_id)

                # Get TMDb external IDs
                external_ids = tmdb_service.get_movie_external_ids(media.tmdb_id)
                details['imdb_id'] = external_ids.get('imdb_id')

                # Get credits (cast and crew)
                credits = tmdb_service.get_movie_credits(media.tmdb_id)
                cast = credits.get('cast', [])[:15]  # Top 15 cast members
                crew = credits.get('crew', [])
                directors = [person['name'] for person in crew if person.get('job') == 'Director'][:3]
            else:
                details = tmdb_service.get_tv_details(media.tmdb_id)
                # Get TMDb external IDs
                external_ids = tmdb_service.get_tv_external_ids(media.tmdb_id)
                details['imdb_id'] = external_ids.get('imdb_id')

                # Get credits (cast and crew)
                credits = tmdb_service.get_tv_credits(media.tmdb_id)
                cast = credits.get('cast', [])[:15]  # Top 15 cast members
                crew = credits.get('crew', [])
                directors = [person['name'] for person in crew if person.get('job') == 'Director'][:3]

            tmdb_data = details
        except requests.RequestException as e:
            logger.warning(
                "Failed to fetch TMDb details for media_id=%s: %s",
                media.id,
                str(e),
                extra={'media_id': media.id, 'tmdb_id': media.tmdb_id}
            )
            pass  # Use basic data if TMDb fails
        except Exception as e:
            logger.error(
                "Unexpected error fetching TMDb details for media_id=%s",
                media.id,
                exc_info=True,
                extra={'media_id': media.id, 'tmdb_id': media.tmdb_id}
            )
            pass  # Use basic data if TMDb fails

    # Check if it's a TV show and get watch progress
    watched_episodes = []
    watched_episodes_set = set()
    progress = None
    tv_show = None
    if media.media_type == "TV_SHOW":
        try:
            tv_show = TVShow.objects.get(id=media_id)
        except TVShow.DoesNotExist:
            # In case media_id refers to the parent Media of a TVShow
            try:
                tv_show = media.tvshow
            except TVShow.DoesNotExist:
                pass
        
        if tv_show:
            tracking_service = EpisodeTrackingService()
            watched_episodes = tracking_service.get_watched_episodes(request.user, tv_show)
            # Create a set of (season, episode) tuples for easy lookup
            watched_episodes_set = {(ep.season_number, ep.episode_number) for ep in watched_episodes}
            progress = tracking_service.get_watch_progress(request.user, tv_show)

    # Prepare seasons data with episode counts for TV shows
    seasons_with_episodes = []
    if media.media_type == "TV_SHOW":
        if tmdb_data and tmdb_data.get('seasons'):
            for season in tmdb_data.get('seasons', []):
                season_num = season.get('season_number', 0)
                episode_count = season.get('episode_count', 20)  # Default to 20 if not available
                seasons_with_episodes.append({
                    'season_number': season_num,
                    'episode_count': episode_count
                })
        else:
            # Fallback: assume 20 episodes per season
            if tv_show:
                for i in range(tv_show.number_of_seasons):
                    seasons_with_episodes.append({
                        'season_number': i,
                        'episode_count': 20
                    })

    return render(request, "media/detail.html", {
        "media": media,
        "tv_show": tv_show,
        "user_lists": user_lists,
        "watched_episodes": watched_episodes,
        "watched_episodes_set": watched_episodes_set,
        "progress": progress,
        "tmdb_data": tmdb_data,
        "cast": cast,
        "directors": directors,
        "seasons_with_episodes": seasons_with_episodes,
    })


@login_required
@require_POST
def add_to_list_view(request: HttpRequest) -> HttpResponse:
    """
    Add media to a list from TMDb or existing media.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        Redirect to appropriate page.
    """
    list_id = request.POST.get("list_id")
    tmdb_id = request.POST.get("tmdb_id")
    media_type = request.POST.get("media_type")
    media_id = request.POST.get("media_id")

    if not list_id:
        messages.error(request, "No list specified")
        return redirect("lists:my_lists")

    list_obj = get_object_or_404(List, id=list_id, user=request.user)
    list_service = ListService()
    media_service = MediaService()

    try:
        # If media already exists in DB
        if media_id:
            media = get_object_or_404(Media, id=media_id)
        # Otherwise fetch from TMDb
        elif tmdb_id and media_type:
            # Normalize media_type from template format (movie/tv) to model format (MOVIE/TV_SHOW)
            normalized_type = "MOVIE" if media_type.lower() == "movie" else "TV_SHOW"
            media = media_service.create_media_from_tmdb(
                tmdb_id=int(tmdb_id),
                media_type=normalized_type,
            )
        else:
            messages.error(request, "Invalid media information")
            return redirect("lists:detail", list_id=list_id)

        list_service.add_media_to_list(list_obj, media)
        messages.success(request, f"'{media.title}' added to '{list_obj.name}'")
        return redirect("lists:detail", list_id=list_id)

    except ValueError as e:
        messages.error(request, str(e))
        return redirect("lists:detail", list_id=list_id)
    except Exception as e:
        messages.error(request, f"Error adding media: {str(e)}")
        return redirect("lists:detail", list_id=list_id)


@login_required
@require_POST
def mark_episode_watched_view(request: HttpRequest, tv_show_id: int) -> HttpResponse:
    """
    Mark an episode as watched.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    tv_show_id : int
        ID of the TV show.

    Returns
    -------
    HttpResponse
        Redirect to media detail page.
    """
    tv_show = get_object_or_404(TVShow, id=tv_show_id)
    season = request.POST.get("season")
    episode = request.POST.get("episode")

    # Validate episode numbers
    result = validate_episode_numbers(season, episode)
    if result is None:
        messages.error(request, "Invalid season or episode numbers. Must be positive integers.")
        return redirect("media:detail", media_id=tv_show_id)

    season_num, episode_num = result

    tracking_service = EpisodeTrackingService()
    try:
        tracking_service.mark_episode_watched(
            user=request.user,
            tv_show=tv_show,
            season_number=season_num,
            episode_number=episode_num,
        )
        messages.success(request, f"Marked {tv_show.title} S{season_num}E{episode_num} as watched")
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")

    return redirect("media:detail", media_id=tv_show_id)


@login_required
@require_POST
def unmark_episode_watched_view(request: HttpRequest, tv_show_id: int) -> HttpResponse:
    """
    Unmark an episode as watched.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    tv_show_id : int
        ID of the TV show.

    Returns
    -------
    HttpResponse
        Redirect to media detail page.
    """
    tv_show = get_object_or_404(TVShow, id=tv_show_id)
    season = request.POST.get("season")
    episode = request.POST.get("episode")

    # Validate episode numbers
    result = validate_episode_numbers(season, episode)
    if result is None:
        messages.error(request, "Invalid season or episode numbers. Must be positive integers.")
        return redirect("media:detail", media_id=tv_show_id)

    season_num, episode_num = result

    tracking_service = EpisodeTrackingService()
    try:
        tracking_service.unmark_episode_watched(
            user=request.user,
            tv_show=tv_show,
            season_number=season_num,
            episode_number=episode_num,
        )
        messages.success(request, f"Unmarked {tv_show.title} S{season_num}E{episode_num}")
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")

    return redirect("media:detail", media_id=tv_show_id)


@login_required
def watch_history_view(request: HttpRequest) -> HttpResponse:
    """
    Display user's watch history.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        Rendered watch history page.
    """
    # Get watched episodes
    watched_episodes = WatchedEpisode.objects.filter(user=request.user).select_related("tv_show").order_by("-watched_at")[:50]
    
    # Get watched movies from lists
    watched_movies = ListItem.objects.filter(
        list__user=request.user,
        status=WatchStatus.WATCHED.value,
        media__media_type="MOVIE"
    ).select_related("media").order_by("-added_at")[:50]
    
    # Combine and sort by timestamp
    watched_list = []
    for episode in watched_episodes:
        watched_list.append({
            'type': 'episode',
            'title': f"{episode.tv_show.title} - S{episode.season_number}E{episode.episode_number}",
            'media': episode.tv_show,
            'timestamp': episode.watched_at,
            'episode': episode
        })
    
    for movie_item in watched_movies:
        watched_list.append({
            'type': 'movie',
            'title': movie_item.media.title,
            'media': movie_item.media,
            'timestamp': movie_item.added_at,
            'item': movie_item
        })
    
    # Sort by timestamp descending
    watched_list.sort(key=lambda x: x['timestamp'], reverse=True)

    return render(request, "media/watch_history.html", {
        "watched_list": watched_list,
    })


@login_required
def add_manual_media_view(request: HttpRequest) -> HttpResponse:
    """
    Add media manually without TMDb ID.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        Rendered manual media form or redirect.
    """
    if request.method == "POST":
        form = ManualMediaForm(request.POST)
        if form.is_valid():
            media = form.save()
            messages.success(request, f"Added '{media.title}' to database!")

            # If list_id is provided, add to that list
            list_id = request.POST.get("list_id")
            if list_id:
                try:
                    list_obj = List.objects.get(id=list_id, user=request.user)
                    list_service = ListService()
                    list_service.add_media_to_list(list_obj, media)
                    messages.success(request, f"Added to list '{list_obj.name}'")
                    return redirect("lists:detail", list_id=list_id)
                except List.DoesNotExist:
                    pass

            return redirect("media:detail", media_id=media.id)
        else:
            messages.error(request, "Form error. Please check the entered data.")
    else:
        form = ManualMediaForm()

    # Get user's lists for the dropdown
    user_lists = List.objects.filter(user=request.user).order_by('name')

    return render(request, "media/add_manual.html", {
        "form": form,
        "user_lists": user_lists,
    })
