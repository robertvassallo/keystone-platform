"""URL routes for the accounts API — mounted under ``/api/v1/auth/``."""

from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from apps.accounts.api.views import MeView, SignInView, SignOutView, SignUpView

app_name = "accounts"

urlpatterns: list[URLPattern | URLResolver] = [
    path("sign-up/", SignUpView.as_view(), name="sign-up"),
    path("sign-in/", SignInView.as_view(), name="sign-in"),
    path("sign-out/", SignOutView.as_view(), name="sign-out"),
    path("me/", MeView.as_view(), name="me"),
]
