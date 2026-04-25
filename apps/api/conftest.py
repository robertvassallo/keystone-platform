"""Repo-wide pytest fixtures."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def _clear_cache_between_tests() -> Generator[None, None, None]:
    """Ensure DRF throttles + any other cache state don't leak between tests."""
    cache.clear()
    yield
    cache.clear()
