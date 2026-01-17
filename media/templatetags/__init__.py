"""
Custom template tags and filters for media app.

This module provides custom template tags and filters.
"""

from django import template

register = template.Library()


@register.filter
def range(value):
    """
    Generate a range of numbers from 1 to value.

    Parameters
    ----------
    value : int
        The upper limit of the range (inclusive).

    Returns
    -------
    range
        A range object from 1 to value+1.

    Examples
    --------
    {% for i in 5|range %}
        {{ i }}  # Outputs: 1 2 3 4 5
    {% endfor %}
    """
    try:
        return range(1, int(value) + 1)
    except (ValueError, TypeError):
        return range(0)
