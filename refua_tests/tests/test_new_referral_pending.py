"""New Referral Request cases — ALL 30 awaiting clarification.

Unlike the other MediTik workbooks, this one has NO Ready cases: all 30
NEW-REFERRAL-001..030 are blocked, and they share a single root cause — the
New Referral Request FORM has no captured element ids. Every case's
Error / Validation column says so, e.g.:

  * NEW-REFERRAL-002: "Form URL, page container, and action locator are absent
    from elements.json"
  * NEW-REFERRAL-003: "Form fields, mandatory rules, and submit locator are
    absent"
  * NEW-REFERRAL-008: "Field and validation-message locators are absent"
  * NEW-REFERRAL-026/027: "Attachment controls and limits are absent"

The ids the workbook CAN cite cover only the entry point (navbar chrome,
meditik-speed-dial-btn-trigger / -fab) and the verification surface
(meditik-tabs-panel-active-requests, 0-user-requests-list-*). Nothing between
them — no route, no page container, no field, no submit control — is grounded.

Therefore this module registers every case with its blocking reason instead of
asserting invented locators. Writing form automation against guessed selectors
would produce tests that pass or fail for reasons unrelated to the product.

UNBLOCK PATH: capture the form's ids with the element scraper that already
exists in the sibling framework repo —
    refuaAutomationCore/scripts/scrape_elements.py --cdp http://127.0.0.1:9222
— driven through the New Referral Request flow. Feeding the resulting
elements.json back into this workbook would convert a large share of these
cases (notably 001-005, 008, 011-013) into implementable ones.

Blocking breakdown: Product Confirmation 11, API Contract 6, Business Rule 5,
UX Confirmation 3, Security Confirmation 3, Data Model Confirmation 2.
"""

import json
from pathlib import Path

import allure
import pytest

CASES = json.loads(
    (
        Path(__file__).resolve().parents[2] / "docs/setup/NEW_REFERRAL_CASES.json"
    ).read_text(encoding="utf-8-sig")
)
PENDING_CASES = [c for c in CASES if c["Clarification Status"] != "Ready"]

# Guard the documented invariant: if a future workbook revision marks cases
# Ready, this module must not silently keep skipping them.
READY_CASES = [c["TC_ID"] for c in CASES if c["Clarification Status"] == "Ready"]


def test_no_new_referral_case_is_silently_skipped():
    """Fail loudly if the workbook gains Ready cases needing implementation."""
    assert not READY_CASES, (
        "The New Referral Request workbook now contains Ready cases "
        f"({', '.join(READY_CASES)}) — implement them in a sanity suite instead "
        "of leaving them registered as pending."
    )


@pytest.mark.meditik
@pytest.mark.new_referral
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
def test_new_referral_pending_case(case):
    """Report a blocked NEW-REFERRAL case without invoking untested workflows."""
    allure.dynamic.title(f'{case["TC_ID"]}: {case["Scenario"]}')
    allure.dynamic.description(case.get("Detailed Automation Steps", ""))
    allure.attach(
        json.dumps(case, ensure_ascii=False, indent=2),
        name="NEW-REFERRAL case detail and blocking reason",
        attachment_type=allure.attachment_type.JSON,
    )
    pytest.skip(case["Clarification Status"])
