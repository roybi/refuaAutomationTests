"""Executable BDD steps for the Meditik Visit Summaries (סיכומי ביקור) page.

Mirrors the 6 Ready cases in meditikVisitSummariesSanity.py one-to-one.

The route is /appointments, not /zimun-torim — see VisitSummariesModulePage.
"""

from __future__ import annotations

import allure
import pytest
from pytest_bdd import given, then, when

from refua_tests.pages.meditikBasePage import MeditekBasePage
from refua_tests.pages.visitSummariesModulePage import VisitSummariesModulePage


def _page(context):
    return context["page"]


def _summaries(context) -> VisitSummariesModulePage:
    summaries = context.get("visit_summaries")
    if summaries is None:
        summaries = VisitSummariesModulePage(_page(context))
        context["visit_summaries"] = summaries
    return summaries


def _skip_unless_empty(summaries):
    """The empty-state scenarios must not seed or delete data."""
    if not summaries.inspect().empty_state_visible:
        pytest.skip(
            "This account currently holds visit summaries, so the empty-state "
            "assertions cannot run; the suite does not seed data."
        )


@given("the user navigates to the Visit Summaries page")
@when("the user navigates to the Visit Summaries page")
@allure.step("When the user navigates to the Visit Summaries page")
def navigate_to_visit_summaries(bdd_context):
    summaries = _summaries(bdd_context)
    summaries.open_direct()
    summaries.wait_until_loaded()


@when("the user opens application navigation and selects Visit Summaries")
@allure.step("When the user opens application navigation and selects Visit Summaries")
def navigate_to_visit_summaries_via_menu(bdd_context):
    MeditekBasePage(_page(bdd_context)).dismiss_blocking_dialogs()
    summaries = _summaries(bdd_context)
    summaries.open_via_application_menu()
    summaries.wait_until_loaded()


@then("the Visit Summaries toolbar and empty-state title are displayed")
@allure.step("Then the Visit Summaries toolbar and empty-state title are displayed")
def visit_summaries_shell_displayed(bdd_context):
    summaries = _summaries(bdd_context)
    _skip_unless_empty(summaries)
    summaries.assert_page_shell()


@when("the Visit Summaries empty-state icon is located")
@allure.step("When the Visit Summaries empty-state icon is located")
def locate_visit_summaries_icon(bdd_context):
    summaries = _summaries(bdd_context)
    _skip_unless_empty(summaries)
    bdd_context["visit_summaries_icon_located"] = True


@then("exactly one Visit Summaries empty-state icon is rendered with a loaded image")
@allure.step("Then exactly one Visit Summaries empty-state icon is rendered and loaded")
def visit_summaries_icon_rendered(bdd_context):
    _summaries(bdd_context).assert_empty_state_icon()


@when("the Visit Summaries empty-state title is read")
@allure.step("When the Visit Summaries empty-state title is read")
def read_visit_summaries_empty_title(bdd_context):
    summaries = _summaries(bdd_context)
    _skip_unless_empty(summaries)
    bdd_context["visit_summaries_title_read"] = True


@then("the Visit Summaries empty-state text matches the approved copy exactly")
@allure.step("Then the Visit Summaries empty-state text matches exactly")
def visit_summaries_text_matches(bdd_context):
    _summaries(bdd_context).assert_empty_state_text()


@when("the Visit Summaries quick-actions control is located")
@allure.step("When the Visit Summaries quick-actions control is located")
def locate_visit_summaries_quick_actions(bdd_context):
    # Data-independent: VSUM-004 does not depend on the empty branch.
    bdd_context["visit_summaries_quick_actions_located"] = True


@then(
    "the Visit Summaries quick-action trigger, FAB and add icon are each "
    "present once and enabled"
)
@allure.step("Then the Visit Summaries quick-action control is present once and enabled")
def visit_summaries_quick_actions_present(bdd_context):
    _summaries(bdd_context).assert_quick_action_control()


@when("the Visit Summaries empty dataset is processed")
@allure.step("When the Visit Summaries empty dataset is processed")
def process_visit_summaries_empty_dataset(bdd_context):
    summaries = _summaries(bdd_context)
    _skip_unless_empty(summaries)
    bdd_context["visit_summaries_empty_processed"] = True


@then("the Visit Summaries empty state is complete with no phantom record")
@allure.step("Then the Visit Summaries empty state is complete with no phantom record")
def visit_summaries_complete_empty_state(bdd_context):
    _summaries(bdd_context).assert_complete_empty_state()
