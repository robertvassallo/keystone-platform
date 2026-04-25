"""URL routes for the current tenant — mounted under ``/api/v1/account/``."""

from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from apps.accounts.api.views import AccountView

app_name = "account"

urlpatterns: list[URLPattern | URLResolver] = [
    path("", AccountView.as_view(), name="get"),
]
