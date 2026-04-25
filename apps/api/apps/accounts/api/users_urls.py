"""URL routes for the users resource — mounted under ``/api/v1/users/``.

Lives in the ``accounts`` Django app because that app owns the ``User``
model. The auth flow URLs stay in ``urls.py``; this file holds the
resource view of users (read-only list today; detail / mutations later).
"""

from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from apps.accounts.api.views import UsersListView

app_name = "users"

urlpatterns: list[URLPattern | URLResolver] = [
    path("", UsersListView.as_view(), name="list"),
]
