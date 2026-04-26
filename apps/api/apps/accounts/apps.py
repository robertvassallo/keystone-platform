"""Django AppConfig for the accounts app."""

from __future__ import annotations

import os
import sys
from typing import Any

from django.apps import AppConfig
from django.db.backends.signals import connection_created

# Management commands that legitimately operate cross-tenant; running
# under any of these implies an ambient RLS bypass for the connection.
MIN_ARGV_FOR_COMMAND = 2

SYSTEM_COMMANDS = frozenset(
    {
        "migrate",
        "makemigrations",
        "showmigrations",
        "shell",
        "shell_plus",
        "dbshell",
        "createsuperuser",
        "changepassword",
        "loaddata",
        "dumpdata",
        "flush",
        "test",
        "collectstatic",
        "check",
    },
)


def _is_system_context() -> bool:
    """True if the process is a management command or test runner.

    Tests get the same ambient bypass — per-test RLS posture is set by
    fixtures that explicitly toggle ``app.bypass_rls`` and
    ``app.current_tenant_id``.
    """
    if "PYTEST_CURRENT_TEST" in os.environ:
        return True
    # ``pytest`` discovers tests before running them; the test harness
    # sets this env var only after collection. Catch the broader case
    # by also checking the entry point.
    if sys.argv and sys.argv[0].endswith("pytest"):
        return True
    return (
        len(sys.argv) >= MIN_ARGV_FOR_COMMAND
        and sys.argv[1] in SYSTEM_COMMANDS
    )


def _set_bypass_on_connection(
    sender: Any,
    connection: Any,
    **kwargs: Any,
) -> None:
    """Apply ambient RLS bypass when the process is a system context."""
    if connection.vendor != "postgresql":
        return
    if not _is_system_context():
        return
    with connection.cursor() as cursor:
        cursor.execute("SET app.bypass_rls = 'on'")


class AccountsConfig(AppConfig):
    """Domain app for user accounts and authentication."""

    name = "apps.accounts"
    label = "accounts"
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name = "Accounts"

    def ready(self) -> None:
        """Wire the connection-init signal once at app load."""
        connection_created.connect(_set_bypass_on_connection)
