"""Service — replace the user's MFA recovery codes."""

from __future__ import annotations

from django.db import transaction
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.audit import AuditAction, AuditContext
from apps.accounts.exceptions import MFANotEnrolled, WrongCurrentPassword
from apps.accounts.models import MFARecoveryCode, User

from ._mfa_helpers import generate_recovery_codes, hash_recovery_code
from .record_audit_event import record_audit_event


def regenerate_recovery_codes(
    *,
    user: User,
    current_password: str,
    audit_context: AuditContext | None = None,
) -> list[str]:
    """Replace recovery codes; returns the new plaintext set (shown once).

    Raises:
        WrongCurrentPassword: If the password does not validate.
        MFANotEnrolled: If the user has no confirmed TOTP device.
    """
    if not user.check_password(current_password):
        raise WrongCurrentPassword("Current password is incorrect.")

    if not TOTPDevice.objects.filter(user=user, confirmed=True).exists():
        raise MFANotEnrolled(
            "MFA is not enabled — there are no recovery codes to regenerate.",
        )

    with transaction.atomic():
        MFARecoveryCode.objects.filter(user=user).delete()

        codes = generate_recovery_codes()
        MFARecoveryCode.objects.bulk_create(
            MFARecoveryCode(user=user, code_hash=hash_recovery_code(code))
            for code in codes
        )

    record_audit_event(
        tenant=user.tenant,
        action=AuditAction.MFA_RECOVERY_CODES_REGENERATED,
        context=audit_context,
        target_id=user.pk,
        target_type="user",
        target_label=user.email,
    )
    return codes
