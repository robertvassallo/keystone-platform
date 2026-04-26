"""Service — disable MFA after the user re-confirms with their password."""

from __future__ import annotations

from django.db import transaction
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.audit import AuditAction, AuditContext
from apps.accounts.exceptions import WrongCurrentPassword
from apps.accounts.models import MFARecoveryCode, User

from .record_audit_event import record_audit_event


def disable_mfa(
    *,
    user: User,
    current_password: str,
    audit_context: AuditContext | None = None,
) -> None:
    """Tear down all of the user's MFA state.

    Re-prompts for the password (rather than a current OTP) so a user who
    has lost their authenticator can still recover. All TOTP devices and
    every recovery code are removed.

    Raises:
        WrongCurrentPassword: If the password does not validate.
    """
    if not user.check_password(current_password):
        raise WrongCurrentPassword("Current password is incorrect.")

    with transaction.atomic():
        TOTPDevice.objects.filter(user=user).delete()
        MFARecoveryCode.objects.filter(user=user).delete()

    record_audit_event(
        tenant=user.tenant,
        action=AuditAction.MFA_DISABLED,
        context=audit_context,
        target_id=user.pk,
        target_type="user",
        target_label=user.email,
    )
