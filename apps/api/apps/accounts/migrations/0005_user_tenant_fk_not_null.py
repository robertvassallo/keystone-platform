"""Convert ``User.tenant_id`` from a nullable UUID into a non-null FK to Account.

The column name stays ``tenant_id``; Django sees the field as ``tenant``
(a ForeignKey) from this migration on. We use ``SeparateDatabaseAndState``
so the model state matches the new shape while the SQL just adds the
constraints we need.
"""

from __future__ import annotations

import django.db.models.deletion
from django.db import migrations, models

ADD_CONSTRAINTS = [
    "ALTER TABLE user_accounts ALTER COLUMN tenant_id SET NOT NULL;",
    (
        "ALTER TABLE user_accounts ADD CONSTRAINT fk_user_accounts_tenant_id "
        "FOREIGN KEY (tenant_id) REFERENCES accounts(id) DEFERRABLE INITIALLY DEFERRED;"
    ),
]

DROP_CONSTRAINTS = [
    "ALTER TABLE user_accounts DROP CONSTRAINT IF EXISTS fk_user_accounts_tenant_id;",
    "ALTER TABLE user_accounts ALTER COLUMN tenant_id DROP NOT NULL;",
]


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_backfill_user_tenants"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="user",
                    name="tenant_id",
                ),
                migrations.AddField(
                    model_name="user",
                    name="tenant",
                    field=models.ForeignKey(
                        db_column="tenant_id",
                        help_text="The tenant this user belongs to. Required.",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="users",
                        to="accounts.account",
                    ),
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql=ADD_CONSTRAINTS,
                    reverse_sql=DROP_CONSTRAINTS,
                ),
            ],
        ),
    ]
