"""Create the application role used for RLS-enforced runtime queries.

Postgres exempts ``SUPERUSER`` and ``BYPASSRLS`` roles from row-level
security entirely — the policies in ``0012`` would do nothing if the
application connected as the superuser the dev container creates by
default. This migration adds a ``keystone_app`` role with neither
attribute and grants it the read/write privileges the application
needs.

The role has ``NOLOGIN`` — it isn't directly authenticatable. Instead,
the application connects as the existing superuser and immediately
``SET ROLE keystone_app`` (see ``apps/accounts/apps.py``). System
contexts (migrations, tests, shell) skip ``SET ROLE`` and stay as the
superuser; the policies themselves still allow them via the
``app.bypass_rls`` flag for completeness.

Reversible: forward creates the role + grants; reverse REVOKEs and
DROP ROLE.
"""

from __future__ import annotations

from django.db import migrations

CREATE_ROLE_SQL = """
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'keystone_app') THEN
        CREATE ROLE keystone_app NOSUPERUSER NOBYPASSRLS NOLOGIN;
    END IF;
END
$$;

GRANT USAGE ON SCHEMA public TO keystone_app;

GRANT SELECT, INSERT, UPDATE, DELETE
    ON ALL TABLES IN SCHEMA public
    TO keystone_app;

GRANT USAGE, SELECT
    ON ALL SEQUENCES IN SCHEMA public
    TO keystone_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO keystone_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO keystone_app;
"""

DROP_ROLE_SQL = """
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    REVOKE ALL ON TABLES FROM keystone_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    REVOKE ALL ON SEQUENCES FROM keystone_app;

REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM keystone_app;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM keystone_app;
REVOKE USAGE ON SCHEMA public FROM keystone_app;

DROP ROLE IF EXISTS keystone_app;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0012_rls_policies"),
    ]

    operations = [
        migrations.RunSQL(sql=CREATE_ROLE_SQL, reverse_sql=DROP_ROLE_SQL),
    ]
