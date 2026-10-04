"""Executable BDD steps for the Meditik My Requests (הבקשות שלי) tabbed screen."""

from __future__ import annotations

import allure
from playwright.sync_api import expect
from pytest_bdd import given, parsers, then, when

from refua_tests.pages.myRequestsTabbedPage import (DEFAULT_TAB_KEY,
                                                     MyRequestsTabbedPage)


def _page(context):
    return context["page"]


def _tabbed(context) -> MyRequestsTabbedPage:
    tabbed = context.get("my_requests")
    if tabbed is None:
        tabbed = MyRequestsTabbedPage(_page(context))
        context["my_requests"] = tabbed
    return tabbed


@when("the user opens My Requests from the Home widget")
@allure.step("When the user opens My Requests from the Home widget")
def open_my_requests_from_widget(bdd_context):
    tabbed = _tabbed(bdd_context)
    tabbed.open_from_home_widget()
    tabbed.wait_until_loaded()


@given("the user opens My Requests directly")
@when("the user opens My Requests directly")
@allure.step("When the user opens My Requests directly")
def open_my_requests_directly(bdd_context):
    tabbed = _tabbed(bdd_context)
    tabbed.open_direct()
    tabbed.wait_until_loaded()


@then("the My Requests tabs header is visible")
@allure.step("Then the My Requests tabs header is visible")
def tabs_header_is_visible(bdd_context):
    expect(_tabbed(bdd_context).tabs_header.first).to_be_visible(timeout=30000)


@then("the My Requests page shell is fully rendered")
@allure.step("Then the My Requests page shell is fully rendered")
def page_shell_is_rendered(bdd_context):
    _tabbed(bdd_context).assert_page_shell()


@when(parsers.parse('the user activates the "{tab}" request tab'))
@allure.step("When the user activates a request tab")
def activate_request_tab(tab, bdd_context):
    _tabbed(bdd_context).activate_tab(tab)
    bdd_context["active_tab"] = tab


@then(parsers.parse('the "{tab}" request panel shows a valid data state'))
@allure.step("Then the request panel shows a valid data state")
def request_panel_has_valid_data_state(tab, bdd_context):
    tabbed = _tabbed(bdd_context)
    tabbed.assert_only_panel_active(tab)
    tabbed.assert_panel_data_state(tab)


@then("New Requests is the initial context with a valid data state")
@allure.step("Then New Requests is the initial context with a valid data state")
def new_requests_is_default_context(bdd_context):
    tabbed = _tabbed(bdd_context)
    tabbed.assert_only_panel_active(DEFAULT_TAB_KEY)
    tabbed.assert_panel_data_state(DEFAULT_TAB_KEY)


@then("the New Requests panel cards are validated when present")
@allure.step("Then the New Requests panel cards are validated when present")
def new_requests_cards_are_validated(bdd_context):
    _tabbed(bdd_context).assert_panel_data_state(DEFAULT_TAB_KEY)


@when("the user activates the navbar logo")
@allure.step("When the user activates the navbar logo")
def activate_navbar_logo(bdd_context):
    _tabbed(bdd_context).return_home_via_logo()


@then("the Meditik home page is visible")
@allure.step("Then the Meditik home page is visible")
def meditik_home_page_is_visible(bdd_context):
    expect(_tabbed(bdd_context).home_page_marker.first).to_be_visible(timeout=30000)


@when("the user rapidly switches between New, Approved, Declined and New")
@allure.step("When the user rapidly switches between request tabs")
def rapidly_switch_tabs(bdd_context):
    _tabbed(bdd_context).rapid_switch(["active", "approved", "declined", "active"])


@then("the final request panel matches the last-activated tab with a valid data state")
@allure.step("Then the final request panel matches the last-activated tab")
def final_panel_matches_last_tab(bdd_context):
    _tabbed(bdd_context).assert_only_panel_active("active")


@then("every request category shows a valid data state")
@allure.step("Then every request category shows a valid data state")
def every_category_has_valid_data_state(bdd_context):
    _tabbed(bdd_context).assert_all_categories_valid()


@then("the request tabs render correctly in Hebrew RTL")
@allure.step("Then the request tabs render correctly in Hebrew RTL")
def request_tabs_render_rtl(bdd_context):
    _tabbed(bdd_context).assert_hebrew_rtl_rendering()


@then("the My Requests home widget shows a valid data state")
@allure.step("Then the My Requests home widget shows a valid data state")
def home_widget_has_valid_data_state(bdd_context):
    _tabbed(bdd_context).assert_widget_data_state()
