"""Vaccinations cases awaiting clarification before implementation.

16 of the 20 VACC-001..020 cases (see docs/setup/VACCINATIONS_CASES.json,
Clarification Status column) need UX/Security/API/Product/Business-Rule
confirmation that is not yet available. Registering them here — collected and
skipped, never executed — preserves the source case IDs and blocking reason
without inventing unapproved behavior. The 4 Ready cases live in
meditikVaccinationsSanity.py.

As with Sick Days, several of these are blocked only on a MISSING LOCATOR rather
than a policy decision: VACC-016/017 need the side-menu "חיסונים" item's
data-testid, and VACC-006/015 need the individual quick-action ids for
"זימון תור" / "הפניה חדשה". Those are capturable with
refuaAutomationCore/scripts/scrape_elements.py, making them the cheapest of this
set to unblock. Because this workbook mirrors Sick_days case-for-case, one
scraping pass over the side menu and quick actions would unblock the equivalent
cases in BOTH suites.
"""

import json
from pathlib import Path

import allure
import pytest

CASES = json.loads(
    (
        Path(__file__).resolve().parents[2] / "docs/setup/VACCINATIONS_CASES.json"
    ).read_text(encoding="utf-8-sig")
)
PENDING_CASES = [c for c in CASES if c["Clarification Status"] != "Ready"]


@pytest.mark.meditik
@pytest.mark.vaccinations
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
def test_vaccinations_pending_case(case):
    """Report a blocked VACC case without invoking untested workflows."""
    allure.dynamic.title(f'{case["TC_ID"]}: {case["Scenario"]}')
    allure.dynamic.description(case.get("Detailed Automation Steps", ""))
    allure.attach(
        json.dumps(case, ensure_ascii=False, indent=2),
        name="VACC case detail and blocking reason",
        attachment_type=allure.attachment_type.JSON,
    )
    pytest.skip(case["Clarification Status"])
