"""Sick Days cases awaiting clarification before implementation.

16 of the 20 SICK-DAYS-001..020 cases (see docs/setup/SICK_DAYS_CASES.json,
Clarification Status column) need UX/Security/API/Product/Business-Rule
confirmation that is not yet available. Registering them here — collected and
skipped, never executed — preserves the source case IDs and blocking reason
without inventing unapproved behavior. The 4 Ready cases live in
meditikSickDaysSanity.py.

Worth noting for whoever unblocks these: several are blocked only on a MISSING
LOCATOR rather than a policy decision. SICK-DAYS-016/017 need the side-menu
"ימי מחלה" item's data-testid, and SICK-DAYS-006/015 need the individual
quick-action ids for "אישור ימי מחלה" / "זימון תור". Those are capturable with
refuaAutomationCore/scripts/scrape_elements.py rather than requiring a product
decision, so they are the cheapest of this set to unblock.
"""

import json
from pathlib import Path

import allure
import pytest

CASES = json.loads(
    (Path(__file__).resolve().parents[2] / "docs/setup/SICK_DAYS_CASES.json").read_text(
        encoding="utf-8-sig"
    )
)
PENDING_CASES = [c for c in CASES if c["Clarification Status"] != "Ready"]


@pytest.mark.meditik
@pytest.mark.sick_days
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
def test_sick_days_pending_case(case):
    """Report a blocked SICK-DAYS case without invoking untested workflows."""
    allure.dynamic.title(f'{case["TC_ID"]}: {case["Scenario"]}')
    allure.dynamic.description(case.get("Detailed Automation Steps", ""))
    allure.attach(
        json.dumps(case, ensure_ascii=False, indent=2),
        name="SICK-DAYS case detail and blocking reason",
        attachment_type=allure.attachment_type.JSON,
    )
    pytest.skip(case["Clarification Status"])
