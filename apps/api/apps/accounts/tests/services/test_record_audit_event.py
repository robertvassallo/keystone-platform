"""Tests for the record_audit_event service."""

from __future__ import annotations

from uuid import uuid4

import pytest

from apps.accounts.audit import AuditAction, AuditContext
from apps.accounts.models import AuditEvent
from apps.accounts.services import record_audit_event
from apps.accounts.tests.factories import AccountFactory, UserFactory


@pytest.mark.django_db
def test_writes_a_row_with_all_provided_fields() -> None:
    tenant = AccountFactory()
    actor = UserFactory(tenant=tenant)
    target_id = uuid4()

    event = record_audit_event(
        tenant=tenant,
        action=AuditAction.TENANT_RENAMED,
        context=AuditContext(actor=actor, ip="10.1.2.3", user_agent="curl/8"),
        target_id=target_id,
        target_type="account",
        target_label="Acme Co",
        metadata={"old_name": "old", "new_name": "new"},
    )

    assert event.tenant_id == tenant.pk
    assert event.actor_id == actor.pk
    assert event.actor_email == actor.email
    assert event.action == "tenant.renamed"
    assert event.target_id == target_id
    assert event.target_type == "account"
    assert event.target_label == "Acme Co"
    assert event.metadata == {"old_name": "old", "new_name": "new"}
    assert event.ip == "10.1.2.3"
    assert event.user_agent == "curl/8"


@pytest.mark.django_db
def test_writes_a_row_with_no_context() -> None:
    tenant = AccountFactory()

    event = record_audit_event(
        tenant=tenant,
        action=AuditAction.AUTH_SIGN_IN,
    )

    assert event.actor_id is None
    assert event.actor_email == ""
    assert event.ip is None
    assert event.user_agent == ""
    assert event.metadata == {}


@pytest.mark.django_db
def test_truncates_oversized_user_agent() -> None:
    tenant = AccountFactory()
    huge = "x" * 5000

    event = record_audit_event(
        tenant=tenant,
        action=AuditAction.AUTH_SIGN_IN,
        context=AuditContext(actor=None, user_agent=huge),
    )

    assert len(event.user_agent) == 500


@pytest.mark.django_db
def test_appends_chronologically() -> None:
    tenant = AccountFactory()

    record_audit_event(tenant=tenant, action=AuditAction.AUTH_SIGN_IN)
    record_audit_event(tenant=tenant, action=AuditAction.MFA_ENROLLED)
    record_audit_event(tenant=tenant, action=AuditAction.TENANT_RENAMED)

    actions = list(
        AuditEvent.objects.filter(tenant=tenant)
        .order_by("created_at")
        .values_list("action", flat=True),
    )
    assert actions == ["auth.sign_in", "mfa.enrolled", "tenant.renamed"]
