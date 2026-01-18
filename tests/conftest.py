"""
Pytest configuration and shared fixtures for all tests.

This module provides common test fixtures and configuration for the entire test suite.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory

User = get_user_model()


@pytest.fixture
def user(db):
    """Create a test user for testing."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )


@pytest.fixture
def another_user(db):
    """Create another test user for testing."""
    return User.objects.create_user(
        username="anotheruser",
        email="another@example.com",
        password="testpass456"
    )


@pytest.fixture
def client():
    """Provide Django test client."""
    return Client()


@pytest.fixture
def request_factory():
    """Provide Django RequestFactory."""
    return RequestFactory()
