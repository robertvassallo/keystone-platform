"""UUID v7 helper.

Postgres 16 has no built-in v7 generator and Python's stdlib gains it only
in 3.14. We rely on `uuid-utils` here; promote to a shared package when a
second app needs it.
"""

from uuid import UUID

import uuid_utils


def uuid_v7() -> UUID:
    """Return a fresh, time-ordered UUID v7 as a stdlib UUID."""
    return UUID(str(uuid_utils.uuid7()))
