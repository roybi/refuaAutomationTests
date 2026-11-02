"""Medical Profile cases awaiting clarification before implementation.

11 of the 14 MEDICAL-PROFILE-001..014 cases (see
docs/setup/MEDICAL_PROFILE_CASES.json, Clarification Status column) need
Security / API-Contract / Data-Model / Product / UX / Performance confirmation
that is not yet available. Registering them here — collected and skipped, never
executed — preserves the source case IDs and blocking reason without inventing
unapproved behavior. The 3 Ready cases live in meditikMedicalProfileSanity.py.

Why this workbook's blocked share is unusually high (11 of 14)
--------------------------------------------------------------
Unlike the tabbed MediTik screens, this workbook has NO grounded content
surface at all. Its own Coverage Summary says "the supplied inventory does not
expose dedicated Medical Profile content fields or cards", so every case about
what the page DISPLAYS (008 null/empty payload, 012 successful retrieval, 014
boundary payload) is blocked on the data model rather than on a locator.

The cheapest subset to unblock is the two that need only UX sign-off on already
visible chrome:
  * MEDICAL-PROFILE-002 — the menu content reached from the hamburger.
  * MEDICAL-PROFILE-003 — the destination after activating the logo.
Both controls already resolve and are asserted unique/visible/enabled by
MedicalProfilePage.assert_navigation_chrome; only the EXPECTED OUTCOME is
missing. 009/010 similarly need the approved Hebrew heading text and the
expected accessible names / focus order.

The remaining seven (005, 006, 007, 012, 013, 014) need decisions nobody on the
test side can make: the unauthenticated-access response, the 5xx and timeout
contracts, the approved profile data model, and the cross-user authorization
response.
"""

import json
from pathlib import Path

import allure
import pytest

CASES = json.loads(
    (
        Path(__file__).resolve().parents[2] / "docs/setup/MEDICAL_PROFILE_CASES.json"
    ).read_text(encoding="utf-8-sig")
)
PENDING_CASES = [c for c in CASES if c["Clarification Status"] != "Ready"]
READY_CASES = [c for c in CASES if c["Clarification Status"] == "Ready"]

# The TC_IDs implemented in meditikMedicalProfileSanity.py.
IMPLEMENTED_IDS = {
    "MEDICAL-PROFILE-001",
    "MEDICAL-PROFILE-004",
    "MEDICAL-PROFILE-011",
}


@pytest.mark.meditik
@pytest.mark.medical_profile
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
def test_medical_profile_pending_case(case):
    """Report a blocked MEDICAL-PROFILE case without invoking untested workflows."""
    allure.dynamic.title(f'{case["TC_ID"]}: {case["Scenario"]}')
    allure.dynamic.description(case.get("Detailed Automation Steps", ""))
    allure.attach(
        json.dumps(case, ensure_ascii=False, indent=2),
        name="MEDICAL-PROFILE case detail and blocking reason",
        attachment_type=allure.attachment_type.JSON,
    )
    pytest.skip(case["Clarification Status"])


@pytest.mark.meditik
@pytest.mark.medical_profile
def test_no_medical_profile_case_is_silently_skipped():
    """Fail loudly if a workbook revision marks a case Ready but nobody implemented it.

    Guards the split between this module and meditikMedicalProfileSanity.py: a
    case that becomes Ready must gain a real test, not keep sitting in the
    pending list where a reader would mistake its skip for an approved gap.
    """
    unimplemented_ready = sorted(
        case["TC_ID"] for case in READY_CASES if case["TC_ID"] not in IMPLEMENTED_IDS
    )
    assert not unimplemented_ready, (
        "These Medical Profile cases are marked Ready in "
        "docs/setup/MEDICAL_PROFILE_CASES.json but have no implementation in "
        f"meditikMedicalProfileSanity.py: {unimplemented_ready}"
    )

    stale = sorted(IMPLEMENTED_IDS - {case["TC_ID"] for case in READY_CASES})
    assert not stale, (
        "These cases are implemented as Ready but the workbook no longer marks "
        f"them Ready: {stale}"
    )

    assert len(CASES) == len(PENDING_CASES) + len(READY_CASES) == 14, (
        f"Expected 14 Medical Profile cases, found {len(CASES)}"
    )
