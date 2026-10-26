"""Pending Vaccinations specifications; no UI step implementations are claimed."""

import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.skip(
    reason=(
        "Blocked: UX/Security/API/Product/Business-Rule confirmation is "
        "unavailable for these cases. See docs/setup/VACCINATIONS_CASES.json for "
        "each case's Clarification Status."
    )
)

scenarios("features/meditik_vaccinations_pending.feature", encoding="utf-8-sig")
