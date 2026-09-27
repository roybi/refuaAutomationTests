"""Executable BDD steps for the Meditik Referrals (הפניות) tabbed screen."""

from __future__ import annotations

import allure
import pytest
from pytest_bdd import given, parsers, then, when

from refua_tests.pages.referralsTabbedPage import ReferralsTabbedPage


def _page(context):
    return context["page"]


def _referrals(context) -> ReferralsTabbedPage:
    referrals = context.get("referrals")
    if referrals is None:
        referrals = ReferralsTabbedPage(_page(context))
        context["referrals"] = referrals
    return referrals


@given("the user navigates to the Referrals page")
@when("the user navigates to the Referrals page")
@allure.step("When the user navigates to the Referrals page")
def navigate_to_referrals(bdd_context):
    referrals = _referrals(bdd_context)
    referrals.open_direct()
    referrals.wait_until_loaded()


@then("the Referrals page shell and all three tabs are operational")
@allure.step("Then the Referrals page shell and all three tabs are operational")
def referrals_shell_is_operational(bdd_context):
    _referrals(bdd_context).assert_page_shell()


@given(parsers.parse('the user selects the "{tab}" referral tab'))
@when(parsers.parse('the user selects the "{tab}" referral tab'))
@allure.step("When the user selects a referral tab")
def select_referral_tab(tab, bdd_context):
    _referrals(bdd_context).activate_tab(tab)
    bdd_context["active_referral_tab"] = tab


@then(parsers.parse('the "{tab}" referral panel is displayed'))
@allure.step("Then the referral panel is displayed")
def referral_panel_is_displayed(tab, bdd_context):
    _referrals(bdd_context).assert_panel_displayed(tab)


def _skip_unless_empty(referrals, tab):
    """Empty-state scenarios need a zero-record category; never seed one."""
    state = referrals.inspect_panel(tab)
    if not state.empty_state_visible:
        pytest.skip(
            f"The {tab} referral category currently holds records in this "
            f"environment and this suite does not seed or delete referral data."
        )


@then(parsers.parse('the "{tab}" panel shows a scoped empty-state icon and title'))
@allure.step("Then the panel shows a scoped empty-state icon and title")
def panel_shows_scoped_icon_and_title(tab, bdd_context):
    referrals = _referrals(bdd_context)
    _skip_unless_empty(referrals, tab)
    referrals.assert_scoped_empty_state(tab, require_icon=True)


@then(parsers.parse('the "{tab}" panel shows a scoped empty-state title'))
@allure.step("Then the panel shows a scoped empty-state title")
def panel_shows_scoped_title(tab, bdd_context):
    referrals = _referrals(bdd_context)
    _skip_unless_empty(referrals, tab)
    referrals.assert_scoped_empty_state(tab, require_icon=False)


@when("the user walks through every referral category")
@allure.step("When the user walks through every referral category")
def walk_every_referral_category(bdd_context):
    _referrals(bdd_context).walk_all_categories()


@then("exactly one referral panel is displayed at each step")
@allure.step("Then exactly one referral panel is displayed at each step")
def one_referral_panel_per_step(bdd_context):
    # walk_all_categories asserts panel+tab exclusivity at every step; re-assert
    # the final category so the Then step carries its own verification.
    _referrals(bdd_context).assert_panel_displayed("past")
