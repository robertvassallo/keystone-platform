"""URL routes for the v1 API.

Each Django app mounts its own ``urls`` here as it ships.
"""

from django.urls import URLPattern, URLResolver, include, path

urlpatterns: list[URLPattern | URLResolver] = [
    path("auth/", include("apps.accounts.urls", namespace="accounts")),
]
