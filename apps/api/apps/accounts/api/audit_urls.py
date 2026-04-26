"""URL routes for the audit log — mounted under ``/api/v1/audit/``."""

from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from apps.accounts.api.views import AuditListView

app_name = "audit"

urlpatterns: list[URLPattern | URLResolver] = [
    path("", AuditListView.as_view(), name="list"),
]
