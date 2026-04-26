"""URL routes for invite admin actions — mounted under ``/api/v1/invites/``."""

from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from apps.accounts.api.views import InviteDetailView, InvitesListCreateView

app_name = "invites"

urlpatterns: list[URLPattern | URLResolver] = [
    path("", InvitesListCreateView.as_view(), name="list-create"),
    path("<uuid:invite_id>/", InviteDetailView.as_view(), name="detail"),
]
