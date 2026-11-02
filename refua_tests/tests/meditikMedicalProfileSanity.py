"""
Meditik Medical Profile (פרופיל רפואי) — /medical-profile page.

Implements the 3 "Ready" cases from the Medical Profile workbook
(MEDICAL-PROFILE-001..014; see docs/setup/MEDICAL_PROFILE_CASES.json for every
column). The remaining 11 cases are registered as skipped/pending in
test_medical_profile_pending.py — each needs Security / API-Contract /
Data-Model / Product / UX / Performance confirmation that is not yet available.

Why only 3 of 14 are executable
-------------------------------
The workbook's Coverage Summary states it outright: "the supplied inventory does
not expose dedicated Medical Profile content fields or cards. Content-specific
expectations are marked for confirmation." The grounded surface is the shared
application shell plus the global quick-action control, so the Ready set is
chrome and navigation only (001 page opens, 004 quick action available, 011
reached through application navigation). No profile field, label or card is
asserted anywhere in this file, because none is specified.

Two rules carried over from the earlier MediTik workbooks:
  * The validation column rejects duplicate actionable locators, so assertions
    check uniqueness (exactly one match), not merely visibility.
  * "Verify no mutation" is asserted only to the extent the UI can prove it —
    see MedicalProfilePage.assert_no_profile_mutation_signals, which documents
    that the data-store half of the check is still an open item.

Run:
    $env:TEST_ENV="test"; $env:TEST_APP="meditek"
    pytest refua_tests/tests/meditikMedicalProfileSanity.py -v
"""

import allure
import pytest

from refua_tests.pages.common.popUpInfo import PopUpInfo
from refua_tests.pages.medicalProfilePage import MedicalProfilePage
from refua_tests.pages.meditikBasePage import MeditekBasePage


@pytest.fixture(scope="class")
def medical_profile_page(app_session):
    page = app_session.ensure_page()
    shell = MeditekBasePage(page)
    shell.open_home()
    shell.ensure_logged_in()
    shell.dismiss_blocking_dialogs()
    yield page


@pytest.fixture(autouse=True)
def _return_home_after(medical_profile_page):
    PopUpInfo.install_auto_dismiss(medical_profile_page)
    PopUpInfo(medical_profile_page).dismiss_if_present()
    yield
    try:
        shell = MeditekBasePage(medical_profile_page)
        shell.dismiss_blocking_dialogs()
        shell.return_to_home()
    except Exception as error:
        print(f"[medical-profile] return_to_home failed: {error}")


def _open_medical_profile(page) -> MedicalProfilePage:
    profile = MedicalProfilePage(page).open_direct()
    profile.wait_until_loaded()
    return profile


@allure.epic("Meditik")
@allure.feature("Medical Profile")
@pytest.mark.meditik
@pytest.mark.medical_profile
class MeditikMedicalProfileSanity:
    """The 3 Ready MEDICAL-PROFILE cases against the /medical-profile page."""

    # MEDICAL-PROFILE-001 — User can open the Medical Profile page
    @allure.story("Open the Medical Profile page")
    @allure.title("MEDICAL-PROFILE-001: the Medical Profile page opens")
    def test_medical_profile_page_opens(self, medical_profile_page):
        profile = _open_medical_profile(medical_profile_page)
        with allure.step("The route is /medical-profile and the toolbar is visible"):
            profile.assert_page_shell()
        with allure.step("No navigation or page-load error, no duplicated shell"):
            profile.assert_no_profile_mutation_signals()

    # MEDICAL-PROFILE-004 — Quick action for appointment booking is available
    @allure.story("Quick actions")
    @allure.title("MEDICAL-PROFILE-004: the appointment-booking quick action is available")
    def test_medical_profile_quick_action_available(self, medical_profile_page):
        profile = _open_medical_profile(medical_profile_page)
        with allure.step("Trigger, FAB and add icon each resolve exactly once"):
            profile.assert_quick_action_control()
        with allure.step("The quick-action control opens"):
            profile.expand_quick_actions()
        with allure.step("The supplied appointment-booking action is exposed"):
            profile.assert_appointment_booking_action_exposed()
        with allure.step("No profile mutation signal before an action is chosen"):
            profile.assert_no_profile_mutation_signals()

    # MEDICAL-PROFILE-011 — Reach Medical Profile through application navigation
    @allure.story("Critical path")
    @allure.title("MEDICAL-PROFILE-011: application navigation reaches Medical Profile")
    def test_medical_profile_reached_via_application_navigation(
        self, medical_profile_page
    ):
        shell = MeditekBasePage(medical_profile_page)
        shell.open_home()
        shell.ensure_logged_in()
        shell.dismiss_blocking_dialogs()

        profile = MedicalProfilePage(medical_profile_page)
        with allure.step("Open navigation and select פרופיל רפואי"):
            profile.open_via_application_menu()
        with allure.step("The URL is /medical-profile and the toolbar is displayed"):
            profile.wait_until_loaded()
            profile.assert_page_shell()
        with allure.step("No wrong-module content and no duplicated shell"):
            profile.assert_no_profile_mutation_signals()
