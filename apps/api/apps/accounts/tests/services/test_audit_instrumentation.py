"""Each instrumented service emits the expected audit action.

Smoke-checks the wiring rather than re-testing each service's primary
behavior — those tests live in their own files.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework.test import APIClient

from apps.accounts.audit import AuditContext
from apps.accounts.models import AuditEvent, Invite
from apps.accounts.services import (
    confirm_mfa_setup,
    disable_mfa,
    regenerate_recovery_codes,
    revoke_invite,
    send_invite,
    update_tenant,
)
from apps.accounts.services._invite_token import (
    generate_invite_token,
    hash_invite_token,
)
from apps.accounts.tests.factories import AccountFactory, UserFactory

STRONG_PASSWORD = "Reliable-Password-7531"


@pytest.fixture
def context() -> AuditContext:
    return AuditContext(actor=None, ip="10.0.0.1", user_agent="vitest")


@pytest.mark.django_db
def test_update_tenant_records_tenant_renamed(context: AuditContext) -> None:
    tenant = AccountFactory(name="Old", slug="old")

    update_tenant(tenant=tenant, name="New", audit_context=context)

    event = AuditEvent.objects.get(tenant=tenant)
    assert event.action == "tenant.renamed"
    assert event.target_id == tenant.pk
    assert event.metadata["old_name"] == "Old"
    assert event.metadata["new_name"] == "New"


@pytest.mark.django_db
def test_change_password_records_auth_password_change() -> None:
    """End-to-end via the view so we get a real session for hash rotation."""
    user = UserFactory(password=STRONG_PASSWORD)
    client = APIClient()
    client.force_login(user)

    response = client.post(
        "/api/v1/auth/password/change/",
        {
            "current_password": STRONG_PASSWORD,
            "new_password": "Different-Password-9999",
        },
        format="json",
    )

    assert response.status_code == 204
    event = AuditEvent.objects.get(tenant=user.tenant)
    assert event.action == "auth.password_change"
    assert event.actor_id == user.pk


@pytest.mark.django_db
def test_disable_mfa_records_mfa_disabled(context: AuditContext) -> None:
    user = UserFactory(password=STRONG_PASSWORD)
    # No MFA device — disable is still a no-op success.

    disable_mfa(
        user=user,
        current_password=STRONG_PASSWORD,
        audit_context=context,
    )

    event = AuditEvent.objects.get(tenant=user.tenant)
    assert event.action == "mfa.disabled"


@pytest.mark.django_db(transaction=True)
def test_send_invite_records_invite_sent(context: AuditContext) -> None:
    tenant = AccountFactory()
    inviter = UserFactory(tenant=tenant)

    invite = send_invite(
        tenant=tenant,
        email="newhire@example.com",
        invited_by=inviter,
        audit_context=context,
    )

    event = AuditEvent.objects.get(tenant=tenant, action="invite.sent")
    assert event.target_id == invite.pk
    assert event.target_label == "newhire@example.com"


@pytest.mark.django_db
def test_revoke_invite_records_invite_revoked(context: AuditContext) -> None:
    tenant = AccountFactory()
    inviter = UserFactory(tenant=tenant)
    invite = Invite.objects.create(
        tenant=tenant,
        email="x@y.com",
        invited_by=inviter,
        token_hash=hash_invite_token(generate_invite_token()),
    )

    revoke_invite(invite=invite, revoked_by=inviter, audit_context=context)

    event = AuditEvent.objects.get(tenant=tenant, action="invite.revoked")
    assert event.target_id == invite.pk


@pytest.mark.django_db
def test_confirm_mfa_setup_records_mfa_enrolled(context: AuditContext) -> None:
    """Verify the audit emit happens; the device side is mocked."""
    user = UserFactory()

    with (
        patch(
            "apps.accounts.services.mfa_confirm_setup.TOTPDevice",
        ) as device_cls,
        patch(
            "apps.accounts.services.mfa_confirm_setup.MFARecoveryCode",
        ) as recovery_cls,
    ):
        device = device_cls.objects.filter.return_value.order_by.return_value.first.return_value
        device.verify_token.return_value = True
        device.confirmed = False
        device_cls.objects.filter.return_value.exists.return_value = False
        recovery_cls.objects.filter.return_value.delete.return_value = None
        recovery_cls.objects.bulk_create.return_value = None

        confirm_mfa_setup(user=user, code="123456", audit_context=context)

    event = AuditEvent.objects.get(tenant=user.tenant, action="mfa.enrolled")
    assert event.target_id == user.pk


@pytest.mark.django_db
def test_regenerate_recovery_codes_records_event(context: AuditContext) -> None:
    """Recovery code regen requires an existing confirmed TOTP device."""
    user = UserFactory(password=STRONG_PASSWORD)
    TOTPDevice.objects.create(user=user, name="primary", confirmed=True)

    regenerate_recovery_codes(
        user=user,
        current_password=STRONG_PASSWORD,
        audit_context=context,
    )

    event = AuditEvent.objects.get(
        tenant=user.tenant,
        action="mfa.recovery_codes_regenerated",
    )
    assert event.target_id == user.pk
