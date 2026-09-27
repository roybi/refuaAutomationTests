"""Executable BDD steps for the Meditik My Appointments (התורים שלי) screen."""

from __future__ import annotations

import allure
from playwright.sync_api import expect
from pytest_bdd import given, parsers, then, when

from refua_tests.pages.myAppointmentsTabbedPage import (DEFAULT_TAB_KEY,
                                                        MyAppointmentsTabbedPage)


def _page(context):
    return context["page"]


def _appts(context) -> MyAppointmentsTabbedPage:
    appts = context.get("my_appointments")
    if appts is None:
        appts = MyAppointmentsTabbedPage(_page(context))
        context["my_appointments"] = appts
    return appts


@when("the user opens My Appointments from the Home widget")
@allure.step("When the user opens My Appointments from the Home widget")
def open_my_appointments_from_widget(bdd_context):
    appts = _appts(bdd_context)
    appts.open_from_home_widget()
    appts.wait_until_loaded()


@given("the user opens My Appointments directly")
@when("the user opens My Appointments directly")
@allure.step("When the user opens My Appointments directly")
def open_my_appointments_directly(bdd_context):
    appts = _appts(bdd_context)
    appts.open_direct()
    appts.wait_until_loaded()


@then("the My Appointments page is loaded")
@allure.step("Then the My Appointments page is loaded")
def my_appointments_page_is_loaded(bdd_context):
    appts = _appts(bdd_context)
    expect(appts.page_root.or_(appts.tabs_header).first).to_be_visible(timeout=30000)


@then("the My Appointments page shell is fully rendered")
@allure.step("Then the My Appointments page shell is fully rendered")
def my_appointments_shell_is_rendered(bdd_context):
    _appts(bdd_context).assert_page_shell()


@when(parsers.parse('the user activates the "{tab}" appointment tab'))
@allure.step("When the user activates an appointment tab")
def activate_appointment_tab(tab, bdd_context):
    _appts(bdd_context).activate_tab(tab)
    bdd_context["active_appointment_tab"] = tab


@then(parsers.parse('the "{tab}" appointment panel shows a valid data state'))
@allure.step("Then the appointment panel shows a valid data state")
def appointment_panel_has_valid_data_state(tab, bdd_context):
    appts = _appts(bdd_context)
    appts.assert_only_panel_active(tab)
    appts.assert_panel_data_state(tab)


@then("Upcoming Appointments is the initial context with a valid data state")
@allure.step("Then Upcoming Appointments is the initial context")
def upcoming_is_default_context(bdd_context):
    appts = _appts(bdd_context)
    appts.assert_only_panel_active(DEFAULT_TAB_KEY)
    appts.assert_panel_data_state(DEFAULT_TAB_KEY)


@then("the past appointment cards are uniquely located when present")
@allure.step("Then the past appointment cards are uniquely located when present")
def past_cards_uniquely_located(bdd_context):
    appts = _appts(bdd_context)
    state = appts.assert_panel_data_state("past")
    if state.has_records:
        testids = appts.card_testids("past")
        assert len(testids) == len(set(testids)), (
            f"Past appointment cards must be uniquely located: {testids!r}"
        )


@when("the user activates the appointments navbar logo")
@allure.step("When the user activates the appointments navbar logo")
def activate_appointments_navbar_logo(bdd_context):
    _appts(bdd_context).return_home_via_logo()


@when("the user rapidly switches between Upcoming, Waiting Lists, Past and Upcoming")
@allure.step("When the user rapidly switches between appointment tabs")
def rapidly_switch_appointment_tabs(bdd_context):
    _appts(bdd_context).rapid_switch(
        ["upcoming", "waiting_lists", "past", "upcoming"]
    )


@then(
    "the final appointment panel matches the last-activated tab with a valid data state"
)
@allure.step("Then the final appointment panel matches the last-activated tab")
def final_appointment_panel_matches_last_tab(bdd_context):
    _appts(bdd_context).assert_only_panel_active(DEFAULT_TAB_KEY)


@then("every appointment category shows a valid data state")
@allure.step("Then every appointment category shows a valid data state")
def every_appointment_category_valid(bdd_context):
    _appts(bdd_context).assert_all_categories_valid()


@then("the appointment tabs render correctly in Hebrew RTL")
@allure.step("Then the appointment tabs render correctly in Hebrew RTL")
def appointment_tabs_render_rtl(bdd_context):
    _appts(bdd_context).assert_hebrew_rtl_rendering()


@then("the future-appointments home widget shows a valid data state")
@allure.step("Then the future-appointments home widget shows a valid data state")
def future_appointments_widget_valid(bdd_context):
    _appts(bdd_context).assert_widget_data_state()
