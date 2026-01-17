"""
User management service.

This module provides service layer for user registration and authentication.
"""

from django.contrib.auth import authenticate
from django.db import transaction

from users.models import User


class UserService:
    """
    Service for managing users.

    This service provides business logic for user registration,
    authentication, and profile management.
    """

    @transaction.atomic
    def register_user(
        self,
        username: str,
        email: str,
        nickname: str,
        password: str,
    ) -> User:
        """
        Register a new user.

        Parameters
        ----------
        username : str
            Desired username.
        email : str
            User's email address.
        nickname : str
            User's public nickname.
        password : str
            User's password (will be hashed).

        Returns
        -------
        User
            Created user object.

        Raises
        ------
        ValueError
            If username, email, or nickname already exists.
        """
        # Check if username exists
        if User.objects.filter(username=username).exists():
            raise ValueError("Username already exists")

        # Check if email exists
        if User.objects.filter(email=email).exists():
            raise ValueError("Email already exists")

        # Check if nickname exists
        if User.objects.filter(nickname=nickname).exists():
            raise ValueError("Nickname already exists")

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.nickname = nickname
        user.save()

        return user

    def authenticate_user(self, username: str, password: str) -> User | None:
        """
        Authenticate a user.

        Parameters
        ----------
        username : str
            Username or email.
        password : str
            User's password.

        Returns
        -------
        User | None
            Authenticated user or None if authentication failed.
        """
        # Try to authenticate with username
        user = authenticate(username=username, password=password)

        # If failed, try with email
        if user is None:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        return user # pyright: ignore[reportReturnType]

    @transaction.atomic
    def update_user_profile(
        self,
        user: User,
        email: str | None = None,
        nickname: str | None = None,
    ) -> User:
        """
        Update user profile information.

        Parameters
        ----------
        user : User
            User to update.
        email : str | None
            New email address (optional).
        nickname : str | None
            New nickname (optional).

        Returns
        -------
        User
            Updated user object.

        Raises
        ------
        ValueError
            If email or nickname already exists.
        """
        if email is not None and email != user.email:
            if User.objects.filter(email=email).exists():
                raise ValueError("Email already exists")
            user.email = email

        if nickname is not None and nickname != user.nickname:
            if User.objects.filter(nickname=nickname).exists():
                raise ValueError("Nickname already exists")
            user.nickname = nickname

        user.save()
        return user

    @transaction.atomic
    def enable_2fa(self, user: User) -> User:
        """
        Enable two-factor authentication for a user.

        Parameters
        ----------
        user : User
            User to enable 2FA for.

        Returns
        -------
        User
            Updated user object.
        """
        user.is_2fa_enabled = True
        user.save()
        return user

    @transaction.atomic
    def disable_2fa(self, user: User) -> User:
        """
        Disable two-factor authentication for a user.

        Parameters
        ----------
        user : User
            User to disable 2FA for.

        Returns
        -------
        User
            Updated user object.
        """
        user.is_2fa_enabled = False
        user.save()
        return user
