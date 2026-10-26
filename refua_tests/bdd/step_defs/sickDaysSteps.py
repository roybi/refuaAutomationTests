"""Executable BDD steps for the Meditik Sick Days (ימי מחלה) page."""

from __future__ import annotations

import allure
import pytest
from pytest_bdd import given, then, when

from refua_tests.pages.sickDaysModulePage import SickDaysModulePage


def _page(context):
    return context["page"]


def _sick_days(context) -> SickDaysModulePage:
    sick_days = context.get("sick_days")
    if sick_days is None:
        sick_days = SickDaysModulePage(_page(context))
        context["sick_days"] = sick_days
    return sick_days


def _skip_unless_empty(sick_days):
    """Every Ready scenario describes the empty state; never seed data."""
    if not sick_days.inspect().empty_state_visible:
        pytest.skip(
            "This account currently holds sick-day records, so the empty-state "
            "assertions cannot run; the suite does not seed or delete data."
        )


@given("the user navigates to the Sick Days page")
@when("the user navigates to the Sick Days page")
@allure.step("When the user navigates to the Sick Days page")
def navigate_to_sick_days(bdd_context):
    sick_days = _sick_days(bdd_context)
    sick_days.open_direct()
    sick_days.wait_until_loaded()


@then("the Sick Days toolbar and empty-state title are displayed")
@allure.step("Then the Sick Days toolbar and empty-state title are displayed")
def sick_days_shell_displayed(bdd_context):
    sick_days = _sick_days(bdd_context)
    _skip_unless_empty(sick_days)
    sick_days.assert_page_shell()


@when("the Sick Days empty-state title is read")
@allure.step("When the Sick Days empty-state title is read")
def read_sick_days_empty_title(bdd_context):
    sick_days = _sick_days(bdd_context)
    _skip_unless_empty(sick_days)
    bdd_context["sick_days_title_read"] = True


@then("the Sick Days empty-state text matches the approved copy exactly")
@allure.step("Then the Sick Days empty-state text matches exactly")
def sick_days_text_matches(bdd_context):
    _sick_days(bdd_context).assert_empty_state_text()


@when("the Sick Days empty-state icon is located")
@allure.step("When the Sick Days empty-state icon is located")
def locate_sick_days_icon(bdd_context):
    sick_days = _sick_days(bdd_context)
    _skip_unless_empty(sick_days)
    bdd_context["sick_days_icon_located"] = True


@then("exactly one Sick Days empty-state icon is rendered with a loaded image")
@allure.step("Then exactly one Sick Days empty-state icon is rendered and loaded")
def sick_days_icon_rendered(bdd_context):
    _sick_days(bdd_context).assert_empty_state_icon()


@when("the user refreshes the Sick Days page")
@allure.step("When the user refreshes the Sick Days page")
def refresh_sick_days(bdd_context):
    sick_days = _sick_days(bdd_context)
    _skip_unless_empty(sick_days)
    sick_days.refresh()


@then("the same Sick Days route and empty state are shown exactly once")
@allure.step("Then the same Sick Days route and empty state are shown once")
def sick_days_single_instance(bdd_context):
    sick_days = _sick_days(bdd_context)
    sick_days.assert_single_page_instance()
    sick_days.assert_empty_state_text()
