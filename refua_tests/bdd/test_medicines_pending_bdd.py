"""Pending Medicines specifications; no UI step implementations are claimed."""

import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.skip(
    reason=(
        "Blocked: Security/API/UX/Business-Rule confirmation is unavailable for "
        "these cases. See docs/setup/MEDICINES_CASES.json for each case's "
        "Clarification Status."
    )
)

scenarios("features/meditik_medicines_pending.feature", encoding="utf-8-sig")
