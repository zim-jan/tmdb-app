"""
Core views for the application.

This module contains views that are not specific to any particular app.
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from lists.models import List, ListItem
from media.models import WatchedEpisode


def index_view(request: HttpRequest) -> HttpResponse:
    """
    Display the home page.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        Rendered index page.
    """
    context = {}

    if request.user.is_authenticated:
        # Get user statistics
        total_lists = List.objects.filter(user=request.user).count()
        total_items = ListItem.objects.filter(list__user=request.user).count()
        total_watched = WatchedEpisode.objects.filter(user=request.user).count()
        
        # Get recent lists
        recent_lists = List.objects.filter(user=request.user).order_by('-updated_at')[:5]

        context = {
            "total_lists": total_lists,
            "total_items": total_items,
            "total_watched": total_watched,
            "recent_lists": recent_lists,
        }

    return render(request, "index.html", context)


def custom_404(request: HttpRequest, exception: Exception) -> HttpResponse:
    """
    Custom 404 error handler.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    exception : Exception
        The exception that triggered the 404 error.

    Returns
    -------
    HttpResponse
        Rendered 404 page with 404 status code.
    """
    return render(request, "404.html", status=404)

def custom_500(request: HttpRequest) -> HttpResponse:
    """
    Custom 500 error handler.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        Rendered 500 page with 500 status code.
    """
    return render(request, "500.html", status=500)


def custom_403(request: HttpRequest, exception: Exception) -> HttpResponse:
    """
    Custom 403 error handler.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    exception : Exception
        The exception that triggered the 403 error.

    Returns
    -------
    HttpResponse
        Rendered 403 page with 403 status code.
    """
    return render(request, "403.html", status=403)


def custom_400(request: HttpRequest, exception: Exception) -> HttpResponse:
    """
    Custom 400 error handler.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    exception : Exception
        The exception that triggered the 400 error.

    Returns
    -------
    HttpResponse
        Rendered 400 page with 400 status code.
    """
    return render(request, "400.html", status=400)