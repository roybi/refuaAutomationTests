"""Medicines & Prescriptions cases awaiting clarification before implementation.

18 of the 24 MEDICINES-001..024 cases (see docs/setup/MEDICINES_CASES.json,
Clarification Status column) need Security/API/UX/Business-Rule confirmation
that is not yet available. Registering them here — collected and skipped, never
executed — preserves the source case IDs and blocking reason without inventing
unapproved behavior. The 6 Ready cases live in meditikMedicinesSanity.py.

Notes on two pending cases whose risk is nonetheless covered:
  * MEDICINES-024 (panel-scoped locator uniqueness): the invariant is enforced
    inside MedicinesTabbedPage.assert_scoped_empty_state(), which requires the
    scoped empty-state locators to resolve to exactly one match.
  * MEDICINES-010/011 (empty Permanent / Previous panels): blocked because the
    workbook defines NO empty-state title for those categories. The page object
    deliberately refuses to assert one — see
    MedicinesTabbedPage.assert_panel_free_of_fabricated_records().
"""

import json
from pathlib import Path

import allure
import pytest

CASES = json.loads(
    (Path(__file__).resolve().parents[2] / "docs/setup/MEDICINES_CASES.json").read_text(
        encoding="utf-8-sig"
    )
)
PENDING_CASES = [c for c in CASES if c["Clarification Status"] != "Ready"]


@pytest.mark.meditik
@pytest.mark.medicines
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
def test_medicines_pending_case(case):
    """Report a blocked MEDICINES case without invoking untested workflows."""
    allure.dynamic.title(f'{case["TC_ID"]}: {case["Scenario"]}')
    allure.dynamic.description(case.get("Detailed Automation Steps", ""))
    allure.attach(
        json.dumps(case, ensure_ascii=False, indent=2),
        name="MEDICINES case detail and blocking reason",
        attachment_type=allure.attachment_type.JSON,
    )
    pytest.skip(case["Clarification Status"])
