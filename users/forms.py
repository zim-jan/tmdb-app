"""
Forms for user registration and authentication.

This module contains Django forms for user management operations.
"""

from typing import Any

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from users.models import User


class UserRegistrationForm(UserCreationForm):
    """
    Form for user registration.

    Extends Django's UserCreationForm to include custom fields
    like email and nickname.

    Attributes
    ----------
    email : EmailField
        User's email address.
    nickname : CharField
        User's public nickname.
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-input",
            "placeholder": "Email address",
        }),
        help_text="Required. Enter a valid email address.",
    )
    nickname = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Public nickname",
        }),
        help_text="Required. 50 characters or fewer.",
    )

    class Meta:
        """Meta options for UserRegistrationForm."""

        model = User
        fields = ["username", "email", "nickname", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Username",
            }),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the registration form.

        Parameters
        ----------
        args : Any
            Positional arguments.
        kwargs : Any
            Keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({
            "class": "form-input",
            "placeholder": "Password",
        })
        self.fields["password2"].widget.attrs.update({
            "class": "form-input",
            "placeholder": "Confirm password",
        })

    def clean_email(self) -> str:
        """
        Validate email uniqueness.

        Returns
        -------
        str
            Cleaned email address.

        Raises
        ------
        ValidationError
            If email already exists.
        """
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already registered.")
        return email

    def clean_nickname(self) -> str:
        """
        Validate nickname uniqueness.

        Returns
        -------
        str
            Cleaned nickname.

        Raises
        ------
        ValidationError
            If nickname already exists.
        """
        nickname = self.cleaned_data.get("nickname")
        if nickname and User.objects.filter(nickname=nickname).exists():
            raise ValidationError("This nickname is already taken.")
        return nickname


class UserLoginForm(forms.Form):
    """
    Form for user login.

    Attributes
    ----------
    username : CharField
        Username or email address.
    password : CharField
        User's password.
    """

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Username or email",
            "autofocus": True,
        }),
        label="Username or Email",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "placeholder": "Password",
        }),
    )
