"""Executable BDD steps for the Meditik Vaccinations (חיסונים) page."""

from __future__ import annotations

import allure
import pytest
from pytest_bdd import given, then, when

from refua_tests.pages.vaccinationsModulePage import VaccinationsModulePage


def _page(context):
    return context["page"]


def _vaccinations(context) -> VaccinationsModulePage:
    vaccinations = context.get("vaccinations")
    if vaccinations is None:
        vaccinations = VaccinationsModulePage(_page(context))
        context["vaccinations"] = vaccinations
    return vaccinations


def _skip_unless_empty(vaccinations):
    """Every Ready scenario describes the empty state; never seed data."""
    if not vaccinations.inspect().empty_state_visible:
        pytest.skip(
            "This account currently holds vaccination records, so the "
            "empty-state assertions cannot run; the suite does not seed data."
        )


@given("the user navigates to the Vaccinations page")
@when("the user navigates to the Vaccinations page")
@allure.step("When the user navigates to the Vaccinations page")
def navigate_to_vaccinations(bdd_context):
    vaccinations = _vaccinations(bdd_context)
    vaccinations.open_direct()
    vaccinations.wait_until_loaded()


@then("the Vaccinations toolbar and empty-state title are displayed")
@allure.step("Then the Vaccinations toolbar and empty-state title are displayed")
def vaccinations_shell_displayed(bdd_context):
    vaccinations = _vaccinations(bdd_context)
    _skip_unless_empty(vaccinations)
    vaccinations.assert_page_shell()


@when("the Vaccinations empty-state title is read")
@allure.step("When the Vaccinations empty-state title is read")
def read_vaccinations_empty_title(bdd_context):
    vaccinations = _vaccinations(bdd_context)
    _skip_unless_empty(vaccinations)
    bdd_context["vaccinations_title_read"] = True


@then("the Vaccinations empty-state text matches the approved copy exactly")
@allure.step("Then the Vaccinations empty-state text matches exactly")
def vaccinations_text_matches(bdd_context):
    _vaccinations(bdd_context).assert_empty_state_text()


@when("the Vaccinations empty-state icon is located")
@allure.step("When the Vaccinations empty-state icon is located")
def locate_vaccinations_icon(bdd_context):
    vaccinations = _vaccinations(bdd_context)
    _skip_unless_empty(vaccinations)
    bdd_context["vaccinations_icon_located"] = True


@then("exactly one Vaccinations empty-state icon is rendered with a loaded image")
@allure.step("Then exactly one Vaccinations empty-state icon is rendered and loaded")
def vaccinations_icon_rendered(bdd_context):
    _vaccinations(bdd_context).assert_empty_state_icon()


@when("the user refreshes the Vaccinations page")
@allure.step("When the user refreshes the Vaccinations page")
def refresh_vaccinations(bdd_context):
    vaccinations = _vaccinations(bdd_context)
    _skip_unless_empty(vaccinations)
    vaccinations.refresh()


@then("the same Vaccinations route and empty state are shown exactly once")
@allure.step("Then the same Vaccinations route and empty state are shown once")
def vaccinations_single_instance(bdd_context):
    vaccinations = _vaccinations(bdd_context)
    vaccinations.assert_single_page_instance()
    vaccinations.assert_empty_state_text()
