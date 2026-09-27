"""
Meditik Sick Days (ימי מחלה) — /sick-days module page.

Implements the 4 "Ready" cases from the Sick_days workbook
(SICK-DAYS-001..020; see docs/setup/SICK_DAYS_CASES.json for every column).
The remaining 16 cases are registered as skipped/pending in
test_sick_days_pending.py — each needs UX/Security/API/Product/Business-Rule
confirmation that is not yet available.

Two notes specific to this workbook:
  * Its Error / Validation column demands failing on a MISSING, DUPLICATED or
    HIDDEN element, so the page object asserts uniqueness (exactly one match),
    not merely visibility.
  * SICK-DAYS-002 specifies the exact Hebrew empty-state copy and requires
    failing when the text differs. Hebrew is the app's native language, so that
    string is asserted HARD — this is the one workbook so far where copy is a
    hard check rather than a soft note.

All four Ready cases describe the EMPTY state, so each skips with a clear reason
if the account actually holds sick-day records; nothing is seeded or deleted.

Run:
    $env:TEST_ENV="test"; $env:TEST_APP="meditek"
    pytest refua_tests/tests/meditikSickDaysSanity.py -v
"""

import pytest

from refua_tests.pages.common.popUpInfo import PopUpInfo
from refua_tests.pages.meditikBasePage import MeditekBasePage
from refua_tests.pages.sickDaysModulePage import SickDaysModulePage


@pytest.fixture(scope="class")
def sick_days_page(app_session):
    page = app_session.ensure_page()
    shell = MeditekBasePage(page)
    shell.open_home()
    shell.ensure_logged_in()
    shell.dismiss_blocking_dialogs()
    yield page


@pytest.fixture(autouse=True)
def _return_home_after(sick_days_page):
    PopUpInfo.install_auto_dismiss(sick_days_page)
    PopUpInfo(sick_days_page).dismiss_if_present()
    yield
    try:
        shell = MeditekBasePage(sick_days_page)
        shell.dismiss_blocking_dialogs()
        shell.return_to_home()
    except Exception as error:
        print(f"[sick_days] return_to_home failed: {error}")


def _open_sick_days(page) -> SickDaysModulePage:
    sick_days = SickDaysModulePage(page).open_direct()
    sick_days.wait_until_loaded()
    return sick_days


def _skip_unless_empty(sick_days, case_id: str):
    """Every Ready case describes the empty state; never seed or delete data."""
    if not sick_days.inspect().empty_state_visible:
        pytest.skip(
            f"{case_id}: this account currently holds sick-day records, so the "
            f"empty-state assertions cannot run. The suite does not seed or "
            f"delete data — re-run with an account that has no sick days."
        )


@pytest.mark.meditik
@pytest.mark.sick_days
class MeditikSickDaysSanity:
    """The 4 Ready SICK-DAYS cases against the /sick-days page."""

    # SICK-DAYS-001 — Open the Sick Days page successfully
    def test_sick_days_page_opens(self, sick_days_page):
        sick_days = _open_sick_days(sick_days_page)
        _skip_unless_empty(sick_days, "SICK-DAYS-001")
        sick_days.assert_page_shell()

    # SICK-DAYS-002 — Exact empty-state text (hard Hebrew assertion)
    def test_sick_days_empty_state_text_is_exact(self, sick_days_page):
        sick_days = _open_sick_days(sick_days_page)
        _skip_unless_empty(sick_days, "SICK-DAYS-002")
        sick_days.assert_empty_state_text()

    # SICK-DAYS-003 — Exactly one visible empty-state icon, image loaded
    def test_sick_days_empty_state_icon(self, sick_days_page):
        sick_days = _open_sick_days(sick_days_page)
        _skip_unless_empty(sick_days, "SICK-DAYS-003")
        sick_days.assert_empty_state_icon()

    # SICK-DAYS-014 — Refresh keeps one route and one empty state
    def test_sick_days_survives_refresh(self, sick_days_page):
        sick_days = _open_sick_days(sick_days_page)
        _skip_unless_empty(sick_days, "SICK-DAYS-014")
        sick_days.refresh()
        sick_days.assert_single_page_instance()
        # The copy must still be correct after the reload.
        sick_days.assert_empty_state_text()
