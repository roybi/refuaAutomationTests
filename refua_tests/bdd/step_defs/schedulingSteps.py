"""Executable BDD steps for the Meditik Appointment Scheduling workbook.

These steps drive the SAME /zimun-torim screen as the My Appointments suite and
reuse MyAppointmentsTabbedPage. Step phrasings are distinct from
myAppointmentsSteps.py so pytest-bdd binds each workbook's feature to its own
steps without collision.
"""

from __future__ import annotations

import allure
import pytest
from pytest_bdd import given, parsers, then, when

from refua_tests.pages.myAppointmentsTabbedPage import (APPOINTMENT_TABS,
                                                        MyAppointmentsTabbedPage)


def _page(context):
    return context["page"]


def _scheduling(context) -> MyAppointmentsTabbedPage:
    scheduling = context.get("scheduling")
    if scheduling is None:
        scheduling = MyAppointmentsTabbedPage(_page(context))
        context["scheduling"] = scheduling
    return scheduling


@given("the user navigates to Appointment Scheduling")
@when("the user navigates to Appointment Scheduling")
@allure.step("When the user navigates to Appointment Scheduling")
def navigate_to_scheduling(bdd_context):
    scheduling = _scheduling(bdd_context)
    scheduling.open_direct()
    scheduling.wait_until_loaded()


@then("the Appointment Scheduling shell and three appointment tabs are displayed")
@allure.step("Then the Appointment Scheduling shell and three tabs are displayed")
def scheduling_shell_is_displayed(bdd_context):
    scheduling = _scheduling(bdd_context)
    scheduling.assert_page_shell()
    page = _page(bdd_context)
    for tab in APPOINTMENT_TABS.values():
        tab_el = page.get_by_test_id(tab.tab_test_id)
        assert tab_el.count() > 0 and tab_el.first.is_visible(), (
            f"Appointment tab {tab.tab_test_id} is not displayed"
        )


@given(parsers.parse('the user selects the "{tab}" appointment tab'))
@when(parsers.parse('the user selects the "{tab}" appointment tab'))
@allure.step("When the user selects an appointment tab")
def select_appointment_tab(tab, bdd_context):
    _scheduling(bdd_context).activate_tab(tab)
    bdd_context["active_scheduling_tab"] = tab


@then(parsers.parse('the "{tab}" appointment panel is active'))
@allure.step("Then the appointment panel is active")
def appointment_panel_is_active(tab, bdd_context):
    _scheduling(bdd_context).assert_only_panel_active(tab)


@then("the Past Appointments panel exposes its filter control and booking link")
@allure.step("Then the Past Appointments panel exposes filter and booking link")
def past_panel_exposes_controls(bdd_context):
    _scheduling(bdd_context).assert_past_panel_controls()


@then("the past appointment card and its location information are validated when present")
@allure.step("Then the past appointment card and location are validated when present")
def past_card_validated_when_present(bdd_context):
    scheduling = _scheduling(bdd_context)
    if scheduling.past_card(0).count() == 0:
        pytest.skip(
            "No past appointment exists for this account, so the card and "
            "location assertions cannot run; this suite does not seed data."
        )
    scheduling.assert_past_card_with_location(0)


def _skip_unless_empty(scheduling, tab):
    title = scheduling.scoped_empty_title(tab)
    if title.count() == 0 or not title.first.is_visible():
        pytest.skip(
            f"The {tab} category currently holds records in this environment "
            f"and this suite does not seed or delete appointment data."
        )


@then(parsers.parse('the "{tab}" panel shows a scoped empty-state icon and title'))
@allure.step("Then the panel shows a scoped empty-state icon and title")
def scheduling_panel_scoped_icon_and_title(tab, bdd_context):
    scheduling = _scheduling(bdd_context)
    _skip_unless_empty(scheduling, tab)
    scheduling.assert_scoped_empty_state(tab, require_icon=True)


@then(parsers.parse('the "{tab}" panel shows a scoped empty-state title'))
@allure.step("Then the panel shows a scoped empty-state title")
def scheduling_panel_scoped_title(tab, bdd_context):
    scheduling = _scheduling(bdd_context)
    _skip_unless_empty(scheduling, tab)
    scheduling.assert_scoped_empty_state(tab, require_icon=False)


@when("the user switches between Upcoming Appointments and Waiting Lists")
@allure.step("When the user switches between Upcoming Appointments and Waiting Lists")
def switch_between_upcoming_and_waiting(bdd_context):
    _scheduling(bdd_context).assert_shared_empty_state_scoping(
        ["upcoming", "waiting_lists"]
    )


@then("each shared empty-state locator resolves to exactly one match")
@allure.step("Then each shared empty-state locator resolves to exactly one match")
def shared_locator_resolves_once(bdd_context):
    # assert_shared_empty_state_scoping enforces this during the switch; re-run
    # it so this Then step carries its own verification.
    _scheduling(bdd_context).assert_shared_empty_state_scoping(
        ["upcoming", "waiting_lists"]
    )


@when("the user visits all three appointment tabs in sequence")
@allure.step("When the user visits all three appointment tabs in sequence")
def visit_all_appointment_tabs(bdd_context):
    scheduling = _scheduling(bdd_context)
    for tab_key in APPOINTMENT_TABS:
        scheduling.activate_tab(tab_key)
        scheduling.assert_only_panel_active(tab_key)
        scheduling.assert_panel_data_state(tab_key)


@then("exactly one appointment panel is active with category-correct data at each step")
@allure.step("Then exactly one appointment panel is active with correct data")
def one_appointment_panel_per_step(bdd_context):
    _scheduling(bdd_context).assert_only_panel_active("past")
