"""
Views for user authentication and management.

This module contains views for user registration, login, logout,
and profile management.
"""


from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from users.forms import UserLoginForm, UserRegistrationForm
from users.services import UserService


def register_view(request: HttpRequest) -> HttpResponse:
    """
    Handle user registration.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        Rendered registration page or redirect to index.
    """
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user_service = UserService()
            try:
                user = user_service.register_user(
                    username=form.cleaned_data["username"],
                    email=form.cleaned_data["email"],
                    nickname=form.cleaned_data["nickname"],
                    password=form.cleaned_data["password1"],
                )
                login(request, user)
                messages.success(request, "Registration successful! Welcome!")
                return redirect("index")
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = UserRegistrationForm()

    return render(request, "users/register.html", {"form": form})


def login_view(request: HttpRequest) -> HttpResponse:
    """
    Handle user login.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        Rendered login page or redirect to index.
    """
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user_service = UserService()
            user = user_service.authenticate_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                next_url = request.GET.get("next", "index")
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()

    return render(request, "users/login.html", {"form": form})


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    """
    Handle user logout.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        Redirect to index page.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("index")


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    """
    Display user profile.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        Rendered profile page.
    """
    return render(request, "users/profile.html", {"user": request.user})
