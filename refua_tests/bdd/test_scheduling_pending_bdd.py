"""Pending Appointment Scheduling specs; no UI step implementations are claimed."""

import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.skip(
    reason=(
        "Blocked: Product/Security/API/UX/Business-Rule/Data-Model confirmation "
        "is unavailable for these cases. See docs/setup/SCHEDULING_CASES.json "
        "for each case's Clarification Status."
    )
)

scenarios("features/meditik_scheduling_pending.feature", encoding="utf-8-sig")
