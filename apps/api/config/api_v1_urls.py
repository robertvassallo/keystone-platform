"""URL routes for the v1 API.

Each Django app mounts its own ``urls`` here as it ships. Empty until the
first feature lands.
"""

from django.urls import URLPattern, URLResolver

urlpatterns: list[URLPattern | URLResolver] = []
