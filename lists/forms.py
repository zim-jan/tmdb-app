"""
Forms for list management.

This module contains Django forms for creating and managing user lists.
"""


from django import forms

from lists.models import List


class ListForm(forms.ModelForm):
    """
    Form for creating and editing lists.

    Attributes
    ----------
    name : CharField
        Name of the list.
    is_public : BooleanField
        Whether the list is publicly visible.
    """

    class Meta:
        """Meta options for ListForm."""

        model = List
        fields = ["name", "is_public"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "My Awesome List",
            }),
            "is_public": forms.CheckboxInput(attrs={
                "class": "form-checkbox",
            }),
        }
        labels = {
            "name": "List Name",
            "is_public": "Make this list public",
        }
        help_texts = {
            "name": "Give your list a descriptive name",
            "is_public": "Public lists can be seen by anyone with the link",
        }
