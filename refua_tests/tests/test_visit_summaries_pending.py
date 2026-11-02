"""Visit Summaries cases awaiting clarification before implementation.

8 of the 14 VSUM-001..014 cases (see docs/setup/VISIT_SUMMARIES_CASES.json,
Clarification Status column) need Security / API-Contract / UX / Product /
Business-Rule / Performance confirmation that is not yet available. Registering
them here — collected and skipped, never executed — preserves the source case
IDs and blocking reason without inventing unapproved behavior. The 6 Ready
cases live in meditikVisitSummariesSanity.py.

What blocks them
----------------
The workbook's Limitations line is the root cause for the list-side cases: "no
visit-summary list item, viewer, search, filter, download, or share
data-testid was present in the supplied inventory." So the POPULATED list
surface is entirely ungrounded, which is why 012 (a completed encounter
produces a summary), 013 (failed generation) and 014 (high-volume boundary) are
blocked on product/API/data-model/performance rather than on a locator.

The cheapest subset to unblock needs only UX sign-off on already-visible
elements:
  * VSUM-009 — the approved Hebrew heading/empty-state rendering expectation.
  * VSUM-010 — the expected accessible names and focus order.
Both surfaces already resolve and are asserted unique/visible by the Ready
cases; only the EXPECTED OUTCOME is missing.

The rest need decisions the test side cannot make: VSUM-005 the
unauthenticated-access response, VSUM-006/007 the 5xx and timeout contracts.
"""

import json
from pathlib import Path

import allure
import pytest

CASES = json.loads(
    (
        Path(__file__).resolve().parents[2] / "docs/setup/VISIT_SUMMARIES_CASES.json"
    ).read_text(encoding="utf-8-sig")
)
PENDING_CASES = [c for c in CASES if c["Clarification Status"] != "Ready"]
READY_CASES = [c for c in CASES if c["Clarification Status"] == "Ready"]

# The TC_IDs implemented in meditikVisitSummariesSanity.py.
IMPLEMENTED_IDS = {
    "VSUM-001",
    "VSUM-002",
    "VSUM-003",
    "VSUM-004",
    "VSUM-008",
    "VSUM-011",
}


@pytest.mark.meditik
@pytest.mark.visit_summaries
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
def test_visit_summaries_pending_case(case):
    """Report a blocked VSUM case without invoking untested workflows."""
    allure.dynamic.title(f'{case["TC_ID"]}: {case["Scenario"]}')
    allure.dynamic.description(case.get("Detailed Automation Steps", ""))
    allure.attach(
        json.dumps(case, ensure_ascii=False, indent=2),
        name="VSUM case detail and blocking reason",
        attachment_type=allure.attachment_type.JSON,
    )
    pytest.skip(case["Clarification Status"])


@pytest.mark.meditik
@pytest.mark.visit_summaries
def test_no_visit_summaries_case_is_silently_skipped():
    """Fail loudly if a workbook revision marks a case Ready but nobody implemented it.

    Guards the split between this module and meditikVisitSummariesSanity.py: a
    case that becomes Ready must gain a real test, not keep sitting in the
    pending list where a reader would mistake its skip for an approved gap.
    """
    unimplemented_ready = sorted(
        case["TC_ID"] for case in READY_CASES if case["TC_ID"] not in IMPLEMENTED_IDS
    )
    assert not unimplemented_ready, (
        "These Visit Summaries cases are marked Ready in "
        "docs/setup/VISIT_SUMMARIES_CASES.json but have no implementation in "
        f"meditikVisitSummariesSanity.py: {unimplemented_ready}"
    )

    stale = sorted(IMPLEMENTED_IDS - {case["TC_ID"] for case in READY_CASES})
    assert not stale, (
        "These cases are implemented as Ready but the workbook no longer marks "
        f"them Ready: {stale}"
    )

    assert len(CASES) == len(PENDING_CASES) + len(READY_CASES) == 14, (
        f"Expected 14 Visit Summaries cases, found {len(CASES)}"
    )
