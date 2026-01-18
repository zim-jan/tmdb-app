"""
Custom template tags and filters for media app.

This module provides custom template tags and filters.
"""

from django import template

# Store the built-in range function before we shadow it with our filter
_builtin_range = range

register = template.Library()


def range_filter(value):
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
        return _builtin_range(1, int(value) + 1)
    except (ValueError, TypeError):
        return _builtin_range(0)


# Register with the original name "range" for template use
register.filter("range", range_filter)
