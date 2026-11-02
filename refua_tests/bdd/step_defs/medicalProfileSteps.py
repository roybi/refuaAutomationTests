"""Executable BDD steps for the Meditik Medical Profile (פרופיל רפואי) page.

Mirrors the 3 Ready cases in meditikMedicalProfileSanity.py one-to-one. The
steps stop at the shell-chrome boundary for the same reason the pytest cases
do: the workbook grounds no Medical Profile content fields or cards.
"""

from __future__ import annotations

import allure
from pytest_bdd import given, then, when

from refua_tests.pages.medicalProfilePage import MedicalProfilePage
from refua_tests.pages.meditikBasePage import MeditekBasePage


def _page(context):
    return context["page"]


def _profile(context) -> MedicalProfilePage:
    profile = context.get("medical_profile")
    if profile is None:
        profile = MedicalProfilePage(_page(context))
        context["medical_profile"] = profile
    return profile


@given("the user navigates to the Medical Profile page")
@when("the user navigates to the Medical Profile page")
@allure.step("When the user navigates to the Medical Profile page")
def navigate_to_medical_profile(bdd_context):
    profile = _profile(bdd_context)
    profile.open_direct()
    profile.wait_until_loaded()


@when("the user opens application navigation and selects Medical Profile")
@allure.step("When the user opens application navigation and selects Medical Profile")
def navigate_to_medical_profile_via_menu(bdd_context):
    shell = MeditekBasePage(_page(bdd_context))
    shell.dismiss_blocking_dialogs()
    profile = _profile(bdd_context)
    profile.open_via_application_menu()
    profile.wait_until_loaded()


@then("the Medical Profile route and toolbar are displayed")
@allure.step("Then the Medical Profile route and toolbar are displayed")
def medical_profile_shell_displayed(bdd_context):
    _profile(bdd_context).assert_page_shell()


@when("the user opens the Medical Profile quick-action control")
@allure.step("When the user opens the Medical Profile quick-action control")
def open_medical_profile_quick_actions(bdd_context):
    profile = _profile(bdd_context)
    profile.assert_quick_action_control()
    profile.expand_quick_actions()


@then("the supplied appointment-booking quick action is exposed")
@allure.step("Then the supplied appointment-booking quick action is exposed")
def medical_profile_booking_action_exposed(bdd_context):
    _profile(bdd_context).assert_appointment_booking_action_exposed()


@then("no Medical Profile mutation signal is observed")
@allure.step("Then no Medical Profile mutation signal is observed")
def medical_profile_no_mutation_signal(bdd_context):
    _profile(bdd_context).assert_no_profile_mutation_signals()
