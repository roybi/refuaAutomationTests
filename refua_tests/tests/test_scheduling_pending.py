"""Appointment Scheduling cases awaiting clarification before implementation.

22 of the 30 APPOINTMENTS-001..030 cases (see docs/setup/SCHEDULING_CASES.json,
Clarification Status column) need Product/Security/API/UX/Business-Rule/
Data-Model confirmation that is not yet available. Registering them here —
collected and skipped, never executed — preserves the source case IDs and
blocking reason without inventing unapproved behavior. The 8 Ready cases live
in meditikSchedulingSanity.py.

This workbook overlaps the earlier My Appointments workbook (APPT-001..034):
both spec the /zimun-torim screen. Several APPOINTMENTS cases are blocked for
the same reasons as their APPT counterparts (booking destination, filter
interface, speed-dial action ids, viewport matrix, a11y criteria), so unblocking
one contract typically unblocks cases in both suites.
"""

import json
from pathlib import Path

import allure
import pytest

CASES = json.loads(
    (Path(__file__).resolve().parents[2] / "docs/setup/SCHEDULING_CASES.json").read_text(
        encoding="utf-8-sig"
    )
)
PENDING_CASES = [c for c in CASES if c["Clarification Status"] != "Ready"]


@pytest.mark.meditik
@pytest.mark.scheduling
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
def test_scheduling_pending_case(case):
    """Report a blocked APPOINTMENTS case without invoking untested workflows."""
    allure.dynamic.title(f'{case["TC_ID"]}: {case["Scenario"]}')
    allure.dynamic.description(case.get("Detailed Automation Steps", ""))
    allure.attach(
        json.dumps(case, ensure_ascii=False, indent=2),
        name="APPOINTMENTS case detail and blocking reason",
        attachment_type=allure.attachment_type.JSON,
    )
    pytest.skip(case["Clarification Status"])
