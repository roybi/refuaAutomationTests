"""Pending Referrals specifications; no UI step implementations are claimed."""

import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.skip(
    reason=(
        "Blocked: Security/API/UX/Business-Rule confirmation is unavailable for "
        "these cases. See docs/setup/REFERRALS_CASES.json for each case's "
        "Clarification Status."
    )
)

scenarios("features/meditik_referrals_pending.feature", encoding="utf-8-sig")
