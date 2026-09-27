"""Executable BDD steps for the Meditik Medicines & Prescriptions screen."""

from __future__ import annotations

import allure
import pytest
from pytest_bdd import given, parsers, then, when

from refua_tests.pages.medicinesTabbedPage import (DEFAULT_TAB_KEY,
                                                   MedicinesTabbedPage)


def _page(context):
    return context["page"]


def _medicines(context) -> MedicinesTabbedPage:
    medicines = context.get("medicines")
    if medicines is None:
        medicines = MedicinesTabbedPage(_page(context))
        context["medicines"] = medicines
    return medicines


@given("the user navigates to the Medicines page")
@when("the user navigates to the Medicines page")
@allure.step("When the user navigates to the Medicines page")
def navigate_to_medicines(bdd_context):
    medicines = _medicines(bdd_context)
    medicines.open_direct()
    medicines.wait_until_loaded()


@then("the Medicines page container, navigation shell and three tabs are displayed")
@allure.step("Then the Medicines page shell and three tabs are displayed")
def medicines_shell_is_displayed(bdd_context):
    _medicines(bdd_context).assert_page_shell()


@given(parsers.parse('the user selects the "{tab}" medicine tab'))
@when(parsers.parse('the user selects the "{tab}" medicine tab'))
@allure.step("When the user selects a medicine tab")
def select_medicine_tab(tab, bdd_context):
    _medicines(bdd_context).activate_tab(tab)
    bdd_context["active_medicine_tab"] = tab


@then(parsers.parse('the "{tab}" medicine panel is the active content'))
@allure.step("Then the medicine panel is the active content")
def medicine_panel_is_active_content(tab, bdd_context):
    _medicines(bdd_context).assert_panel_is_active_content(tab)


@then("the My Prescriptions panel shows a scoped empty-state icon and title")
@allure.step("Then the My Prescriptions panel shows a scoped empty state")
def my_prescriptions_empty_state(bdd_context):
    medicines = _medicines(bdd_context)
    state = medicines.inspect_panel(DEFAULT_TAB_KEY)
    if not state.empty_state_visible:
        pytest.skip(
            "My Prescriptions currently holds active prescriptions in this "
            "environment and this suite does not seed or delete medicine data."
        )
    medicines.assert_scoped_empty_state(DEFAULT_TAB_KEY)


@when("the user opens every medicine category in sequence")
@allure.step("When the user opens every medicine category in sequence")
def open_every_medicine_category(bdd_context):
    _medicines(bdd_context).walk_all_categories()


@then("exactly one medicine panel is active at each step")
@allure.step("Then exactly one medicine panel is active at each step")
def one_medicine_panel_per_step(bdd_context):
    # walk_all_categories asserts exclusivity at every step; re-assert the final
    # category so this Then step carries its own verification.
    _medicines(bdd_context).assert_panel_is_active_content("expired")
