"""Pending New Referral Request specs; no UI step implementations are claimed.

ALL 30 cases in this workbook are blocked on one root cause: the New Referral
Request form has no captured element ids (no route, page container, fields or
submit control). See refua_tests/tests/test_new_referral_pending.py for the
full rationale and the scraper-based unblock path.
"""

import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.skip(
    reason=(
        "Blocked: the New Referral Request form has no captured data-testid "
        "values (route, fields and submit control are absent from elements.json), "
        "plus Product/API/Business-Rule/UX/Security/Data-Model confirmation. See "
        "docs/setup/NEW_REFERRAL_CASES.json for each case's Clarification Status."
    )
)

scenarios("features/meditik_new_referral_pending.feature", encoding="utf-8-sig")
