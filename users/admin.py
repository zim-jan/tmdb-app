"""Admin configuration for users app."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""

    list_display = ["username", "email", "nickname", "created_at"]
    list_filter = ["is_staff", "is_active", "created_at"]
    search_fields = ["username", "email", "nickname"]
    ordering = ["-created_at"]

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Custom Fields",
            {
                "fields": ("nickname",),
            },
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Custom Fields",
            {
                "fields": ("email", "nickname"),
            },
        ),
    )
