"""Tests for the Postgres Row-Level Security policies.

The pytest-django test suite runs as the container superuser with
ambient ``app.bypass_rls = 'on'`` — both exempt from RLS. To exercise
the policies these tests temporarily switch to the non-superuser
``keystone_app`` role via ``SET ROLE`` and turn bypass off. The
``rls_runtime_role`` context manager bundles both.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any
from uuid import UUID

import pytest
from django.db import connection
from django.db.utils import InternalError, ProgrammingError

from apps.accounts.audit import AuditAction
from apps.accounts.models import AuditEvent, Invite, User
from apps.accounts.security import bypass_rls
from apps.accounts.services import record_audit_event
from apps.accounts.services._invite_token import (
    generate_invite_token,
    hash_invite_token,
)
from apps.accounts.tests.factories import AccountFactory, UserFactory


@contextmanager
def rls_runtime_role(tenant_id: UUID) -> Any:
    """Drop to ``keystone_app``, set the tenant scope, run; restore on exit."""
    with connection.cursor() as cursor:
        cursor.execute("SET ROLE keystone_app")
        cursor.execute("SET app.bypass_rls = 'off'")
        cursor.execute("SET app.current_tenant_id = %s", [str(tenant_id)])
    try:
        yield
    finally:
        with connection.cursor() as cursor:
            cursor.execute("RESET ROLE")
            cursor.execute("SET app.bypass_rls = 'on'")
            cursor.execute("RESET app.current_tenant_id")


@pytest.fixture
def two_tenants():  # type: ignore[no-untyped-def]
    """Two tenants, each with one user, one invite, one audit event."""
    tenant_a = AccountFactory()
    tenant_b = AccountFactory()
    user_a = UserFactory(tenant=tenant_a)
    user_b = UserFactory(tenant=tenant_b)
    invite_a = Invite.objects.create(
        tenant=tenant_a,
        email="invitee_a@example.com",
        invited_by=user_a,
        token_hash=hash_invite_token(generate_invite_token()),
    )
    invite_b = Invite.objects.create(
        tenant=tenant_b,
        email="invitee_b@example.com",
        invited_by=user_b,
        token_hash=hash_invite_token(generate_invite_token()),
    )
    record_audit_event(tenant=tenant_a, action=AuditAction.AUTH_SIGN_IN)
    record_audit_event(tenant=tenant_b, action=AuditAction.AUTH_SIGN_IN)
    return {
        "tenant_a": tenant_a,
        "tenant_b": tenant_b,
        "user_a": user_a,
        "user_b": user_b,
        "invite_a": invite_a,
        "invite_b": invite_b,
    }


@pytest.mark.django_db(transaction=True)
def test_rls_blocks_cross_tenant_user_reads(two_tenants) -> None:  # type: ignore[no-untyped-def]
    tenant_a = two_tenants["tenant_a"]
    user_b = two_tenants["user_b"]

    with rls_runtime_role(tenant_a.pk):
        visible_users = list(
            User.objects.filter(pk=user_b.pk).values_list("pk", flat=True),
        )

    assert visible_users == []


@pytest.mark.django_db(transaction=True)
def test_rls_blocks_cross_tenant_invite_reads(two_tenants) -> None:  # type: ignore[no-untyped-def]
    tenant_a = two_tenants["tenant_a"]
    invite_b = two_tenants["invite_b"]

    with rls_runtime_role(tenant_a.pk):
        visible_invites = list(
            Invite.objects.filter(pk=invite_b.pk).values_list("pk", flat=True),
        )

    assert visible_invites == []


@pytest.mark.django_db(transaction=True)
def test_rls_blocks_cross_tenant_audit_reads(two_tenants) -> None:  # type: ignore[no-untyped-def]
    tenant_a = two_tenants["tenant_a"]
    tenant_b = two_tenants["tenant_b"]

    with rls_runtime_role(tenant_a.pk):
        own = AuditEvent.objects.filter(tenant_id=tenant_a.pk).count()
        other = AuditEvent.objects.filter(tenant_id=tenant_b.pk).count()

    assert own == 1
    assert other == 0


@pytest.mark.django_db(transaction=True)
def test_rls_allows_in_tenant_user_reads(two_tenants) -> None:  # type: ignore[no-untyped-def]
    tenant_a = two_tenants["tenant_a"]
    user_a = two_tenants["user_a"]

    with rls_runtime_role(tenant_a.pk):
        ids = list(User.objects.values_list("pk", flat=True))

    assert user_a.pk in ids


@pytest.mark.django_db(transaction=True)
def test_rls_blocks_cross_tenant_writes(two_tenants) -> None:  # type: ignore[no-untyped-def]
    """WITH CHECK should reject inserts targeting another tenant."""
    tenant_a = two_tenants["tenant_a"]
    user_a = two_tenants["user_a"]
    tenant_b = two_tenants["tenant_b"]

    with (
        rls_runtime_role(tenant_a.pk),
        pytest.raises((InternalError, ProgrammingError)),
    ):
        Invite.objects.create(
            tenant=tenant_b,
            email="forged@example.com",
            invited_by=user_a,
            token_hash=hash_invite_token(generate_invite_token()),
        )


@pytest.mark.django_db(transaction=True)
def test_bypass_sees_all_tenants(two_tenants) -> None:  # type: ignore[no-untyped-def]
    """The escape valve is what migrations / management commands ride."""
    with bypass_rls():
        count = User.objects.count()

    # Two users from the fixture plus any factory-side detritus.
    assert count >= 2
