"""My Requests workbook cases awaiting clarification before implementation.

16 of the 31 MYREQ-001..031 cases (see docs/setup/MY_REQUESTS_CASES.json,
Clarification Status column) need Product/Security/API/Data-Model/
Non-Functional/Accessibility confirmation that is not yet available.
Registering them here — collected and skipped, never executed — preserves
the source case IDs and blocking reason without inventing unapproved
behavior. The 15 Ready cases are implemented in meditikMyRequestsSanity.py.
"""

import json
from pathlib import Path

import allure
import pytest

CASES = json.loads(
    (Path(__file__).resolve().parents[2] / "docs/setup/MY_REQUESTS_CASES.json").read_text(
        encoding="utf-8-sig"
    )
)
PENDING_CASES = [c for c in CASES if not c["Clarification Status"].startswith("Ready")]


@pytest.mark.meditik
@pytest.mark.my_requests
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
def test_my_requests_pending_case(case):
    """Report a blocked MYREQ case without invoking untested workflows."""
    allure.dynamic.title(f'{case["TC_ID"]}: {case["Scenario"]}')
    allure.dynamic.description(case["Detailed Automation Steps"])
    allure.attach(
        json.dumps(case, ensure_ascii=False, indent=2),
        name="MYREQ case detail and blocking reason",
        attachment_type=allure.attachment_type.JSON,
    )
    pytest.skip(case["Clarification Status"])
