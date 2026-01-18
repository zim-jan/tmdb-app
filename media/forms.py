"""
Forms for media app.

This module defines forms for manual media entry.
"""

from django import forms

from media.models import Media, MediaType


class ManualMediaForm(forms.ModelForm):
    """
    Form for manually adding media without TMDb ID.

    Fields
    ------
    title : str
        Media title (required).
    media_type : str
        Type of media (MOVIE or TV_SHOW).
    original_title : str
        Original title (optional).
    overview : str
        Description/synopsis (optional).
    release_date : date
        Release date (optional).
    """

    class Meta:
        model = Media
        fields = [
            "title",
            "media_type",
            "original_title",
            "original_language",
            "overview",
            "release_date",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter movie or TV series title",
                }
            ),
            "media_type": forms.Select(
                attrs={"class": "form-control"},
                choices=MediaType.choices,
            ),
            "original_title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Original title (optional)",
                }
            ),
            "original_language": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "ISO 639-1 code (e.g., en, pl, es)",
                    "maxlength": "10",
                }
            ),
            "overview": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Description (optional)",
                    "rows": 4,
                }
            ),
            "release_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "placeholder": "Release date (optional)",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        """Initialize form with custom styling and default values."""
        super().__init__(*args, **kwargs)
        self.fields["original_title"].required = False
        self.fields["original_language"].required = False
        self.fields["overview"].required = False
        self.fields["release_date"].required = False

        # Set default language to 'en' if not provided
        if not self.initial.get("original_language"):
            self.fields["original_language"].initial = "en"
