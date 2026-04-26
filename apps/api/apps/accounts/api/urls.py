"""URL routes for the accounts API — mounted under ``/api/v1/auth/``."""

from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from apps.accounts.api.views import (
    ChangePasswordView,
    EmailVerificationConfirmView,
    EmailVerificationRequestView,
    InviteAcceptView,
    InvitePreviewView,
    MeView,
    MFADisableView,
    MFARegenerateRecoveryCodesView,
    MFASetupConfirmView,
    MFASetupStartView,
    MFAStatusView,
    MFAVerifyView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    SignInView,
    SignOutView,
    SignUpView,
)

app_name = "accounts"

urlpatterns: list[URLPattern | URLResolver] = [
    path("sign-up/", SignUpView.as_view(), name="sign-up"),
    path("sign-in/", SignInView.as_view(), name="sign-in"),
    path("sign-out/", SignOutView.as_view(), name="sign-out"),
    path("me/", MeView.as_view(), name="me"),
    path(
        "password-reset/request/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "password/change/",
        ChangePasswordView.as_view(),
        name="password-change",
    ),
    path(
        "email-verification/request/",
        EmailVerificationRequestView.as_view(),
        name="email-verification-request",
    ),
    path(
        "email-verification/confirm/",
        EmailVerificationConfirmView.as_view(),
        name="email-verification-confirm",
    ),
    path(
        "invite/preview/",
        InvitePreviewView.as_view(),
        name="invite-preview",
    ),
    path(
        "invite/accept/",
        InviteAcceptView.as_view(),
        name="invite-accept",
    ),
    path("mfa/status/", MFAStatusView.as_view(), name="mfa-status"),
    path("mfa/verify/", MFAVerifyView.as_view(), name="mfa-verify"),
    path("mfa/setup/", MFASetupStartView.as_view(), name="mfa-setup-start"),
    path(
        "mfa/setup/confirm/",
        MFASetupConfirmView.as_view(),
        name="mfa-setup-confirm",
    ),
    path("mfa/disable/", MFADisableView.as_view(), name="mfa-disable"),
    path(
        "mfa/recovery-codes/regenerate/",
        MFARegenerateRecoveryCodesView.as_view(),
        name="mfa-recovery-codes-regenerate",
    ),
]
