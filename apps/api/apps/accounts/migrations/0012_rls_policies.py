"""Enable Postgres Row-Level Security on tenant-scoped tables.

Tables in scope: ``user_accounts``, ``invites``, ``audit_events``.
``accounts`` itself is the tenant — RLS adds little when the row's
identity *is* the tenant context — so it's deliberately out of scope
for this migration.

Each policy is permissive: a row is visible iff its ``tenant_id``
matches ``app.current_tenant_id``, OR ``app.bypass_rls`` is ``'on'``.
The bypass flag covers legitimate pre-auth flows (sign-in lookup,
invite preview, password reset) and system contexts (migrations,
tests, Django admin).

``WITH CHECK`` mirrors ``USING`` so an INSERT or UPDATE can only land a
row in the current tenant — no cross-tenant write possible.

Reversible: forward enables RLS + creates policies; reverse drops the
policies and disables RLS. Both are pure DDL.
"""

from __future__ import annotations

from django.db import migrations

# The three tenant-scoped tables.
TABLES = ("user_accounts", "invites", "audit_events")

POLICY_NAME = "tenant_isolation"

POLICY_EXPRESSION = (
    "tenant_id::text = current_setting('app.current_tenant_id', TRUE)"
    " OR current_setting('app.bypass_rls', TRUE) = 'on'"
)


def _enable_sql(table: str) -> str:
    return (
        f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;\n"
        f"CREATE POLICY {POLICY_NAME} ON {table}\n"
        f"  FOR ALL\n"
        f"  USING ({POLICY_EXPRESSION})\n"
        f"  WITH CHECK ({POLICY_EXPRESSION});"
    )


def _disable_sql(table: str) -> str:
    return (
        f"DROP POLICY IF EXISTS {POLICY_NAME} ON {table};\n"
        f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;"
    )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0011_audit_event"),
    ]

    operations = [
        migrations.RunSQL(
            sql=_enable_sql(table),
            reverse_sql=_disable_sql(table),
        )
        for table in TABLES
    ]
