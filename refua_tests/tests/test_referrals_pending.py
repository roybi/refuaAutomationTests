"""Referrals workbook cases awaiting clarification before implementation.

16 of the 24 REFERRALS-001..024 cases (see docs/setup/REFERRALS_CASES.json,
Clarification Status column) need Security/API/UX/Business-Rule confirmation
that is not yet available. Registering them here — collected and skipped, never
executed — preserves the source case IDs and blocking reason without inventing
unapproved behavior. The 8 Ready cases live in meditikReferralsSanity.py.

Note on REFERRALS-024 (locator uniqueness by panel): the workbook marks it
pending, so it is not executed as its own case here, but the invariant it
describes IS enforced inside every Ready empty-state assertion via
ReferralsTabbedPage.assert_scoped_empty_state().
"""

import json
from pathlib import Path

import allure
import pytest

CASES = json.loads(
    (Path(__file__).resolve().parents[2] / "docs/setup/REFERRALS_CASES.json").read_text(
        encoding="utf-8-sig"
    )
)
PENDING_CASES = [c for c in CASES if c["Clarification Status"] != "Ready"]


@pytest.mark.meditik
@pytest.mark.referrals
@pytest.mark.parametrize(
    "case",
    [
        pytest.param(
            case,
            id=case["TC_ID"],
            marks=pytest.mark.skip(reason=case["Clarification Status"]),
        )
        for case in PENDING_CASES
    ],
)
def test_referrals_pending_case(case):
    """Report a blocked REFERRALS case without invoking untested workflows."""
    allure.dynamic.title(f'{case["TC_ID"]}: {case["Scenario"]}')
    allure.dynamic.description(case.get("Detailed Automation Steps", ""))
    allure.attach(
        json.dumps(case, ensure_ascii=False, indent=2),
        name="REFERRALS case detail and blocking reason",
        attachment_type=allure.attachment_type.JSON,
    )
    pytest.skip(case["Clarification Status"])
