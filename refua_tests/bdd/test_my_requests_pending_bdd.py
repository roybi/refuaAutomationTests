"""Pending My Requests specifications; no UI step implementations are claimed."""

import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.skip(
    reason=(
        "Blocked: Product/Security/API/Data-Model/Non-Functional/Accessibility "
        "confirmation is unavailable for these cases. See "
        "docs/setup/MY_REQUESTS_CASES.json for each case's Clarification Status."
    )
)

scenarios("features/meditik_my_requests_pending.feature", encoding="utf-8-sig")
