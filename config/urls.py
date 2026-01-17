"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path

from core.views import index_view

urlpatterns = [
    path("", index_view, name="index"),
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("lists/", include("lists.urls")),
    path("media/", include("media.urls")),
    path("api/media/", include("media.api_urls")),
    path("", include("profiles.urls")),
]

# Custom error handlers
handler404 = "core.views.custom_404"
