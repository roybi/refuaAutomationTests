"""My Appointments workbook cases awaiting clarification before implementation.

21 of the 34 APPT-001..034 cases (see docs/setup/MY_APPOINTMENTS_CASES.json,
Clarification Status column) need Product/Security/API/Data-Model/
Non-Functional/Accessibility confirmation that is not yet available.
Registering them here — collected and skipped, never executed — preserves the
source case IDs and blocking reason without inventing unapproved behavior.
The 13 Ready cases are implemented in meditikMyAppointmentsSanity.py.
"""

import json
from pathlib import Path

import allure
import pytest

CASES = json.loads(
    (
        Path(__file__).resolve().parents[2] / "docs/setup/MY_APPOINTMENTS_CASES.json"
    ).read_text(encoding="utf-8-sig")
)
PENDING_CASES = [c for c in CASES if not c["Clarification Status"].startswith("Ready")]


@pytest.mark.meditik
@pytest.mark.my_appointments
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
def test_my_appointments_pending_case(case):
    """Report a blocked APPT case without invoking untested workflows."""
    allure.dynamic.title(f'{case["TC_ID"]}: {case["Scenario"]}')
    allure.dynamic.description(case["Detailed Automation Steps"])
    allure.attach(
        json.dumps(case, ensure_ascii=False, indent=2),
        name="APPT case detail and blocking reason",
        attachment_type=allure.attachment_type.JSON,
    )
    pytest.skip(case["Clarification Status"])
