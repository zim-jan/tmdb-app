"""
Custom template tags for checking watched episodes.

This module provides template tags for episode tracking.
"""

from django import template

register = template.Library()


@register.filter
def is_watched(watched_episodes_set, episode_key):
    """
    Check if an episode is in the watched set.

    Parameters
    ----------
    watched_episodes_set : set
        Set of (season, episode) tuples.
    episode_key : str
        String in format "season,episode".

    Returns
    -------
    bool
        True if episode is watched.
    """
    try:
        season, episode = map(int, episode_key.split(','))
        return (season, episode) in watched_episodes_set
    except (ValueError, AttributeError):
        return False
