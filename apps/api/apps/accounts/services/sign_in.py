"""Service — authenticate and either start a session or issue an MFA challenge."""

from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate as django_authenticate
from django.contrib.auth import login as django_login
from django.http import HttpRequest
from django.utils import timezone
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.audit import AuditAction, AuditContext
from apps.accounts.exceptions import InvalidCredentials
from apps.accounts.models import User
from apps.accounts.security import bypass_rls

from .mfa_verify_challenge import CHALLENGE_SESSION_KEY
from .record_audit_event import record_audit_event

# Partial-auth ticket TTL — see decisions-log for rationale.
MFA_CHALLENGE_TTL = timedelta(minutes=5)


def sign_in(
    *,
    request: HttpRequest,
    email: str,
    password: str,
    remember_me: bool,
    audit_context: AuditContext | None = None,
) -> User | None:
    """Authenticate; either complete the sign-in or queue an MFA challenge.

    Args:
        request: The HTTP request — Django binds the session to it.
        email: Login email.
        password: Plaintext password.
        remember_me: If True, extend session expiry to
            ``settings.REMEMBER_ME_DURATION`` after sign-in completes
            (whether immediately or after MFA verify).
        audit_context: Optional ``AuditContext`` for the audit-log entry.
            ``actor`` may be unset; this service binds the authenticated
            user as the actor before recording.

    Returns:
        The authenticated ``User`` if sign-in completed; ``None`` if the
        user has MFA enabled and a partial-auth ticket has been stashed
        in the session for ``mfa_verify_challenge`` to consume.

    Raises:
        InvalidCredentials: Authentication failed for any reason.
    """
    # Authentication queries the User table by email *before* a tenant
    # is known; bypass RLS for the lookup, then resume normal scoping.
    with bypass_rls():
        user = django_authenticate(
            request,
            username=email.lower().strip(),
            password=password,
        )
    if user is None or not isinstance(user, User):
        raise InvalidCredentials("Email or password is incorrect.")

    if TOTPDevice.objects.filter(user=user, confirmed=True).exists():
        request.session[CHALLENGE_SESSION_KEY] = {
            "user_id": str(user.pk),
            "remember_me": remember_me,
            "expires_at": (timezone.now() + MFA_CHALLENGE_TTL).isoformat(),
        }
        return None

    django_login(request, user)
    if remember_me:
        request.session.set_expiry(settings.REMEMBER_ME_DURATION)

    # Record audit on the success-no-MFA-needed path; the MFA path
    # records the sign-in inside ``verify_mfa_challenge`` instead so
    # ``auth.sign_in`` always represents *completed* authentication.
    bound_context = AuditContext(
        actor=user,
        ip=audit_context.ip if audit_context is not None else None,
        user_agent=audit_context.user_agent if audit_context is not None else None,
    )
    record_audit_event(
        tenant=user.tenant,
        action=AuditAction.AUTH_SIGN_IN,
        context=bound_context,
        target_id=user.pk,
        target_type="user",
        target_label=user.email,
    )
    return user
