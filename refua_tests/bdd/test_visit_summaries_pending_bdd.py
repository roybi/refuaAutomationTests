"""Pending Visit Summaries specifications; no UI step implementations are claimed."""

import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.skip(
    reason=(
        "Blocked: Security/API-Contract/UX/Product/Business-Rule/Performance "
        "confirmation is unavailable for these cases. See "
        "docs/setup/VISIT_SUMMARIES_CASES.json for each case's Clarification "
        "Status."
    )
)

scenarios("features/meditik_visit_summaries_pending.feature", encoding="utf-8-sig")
