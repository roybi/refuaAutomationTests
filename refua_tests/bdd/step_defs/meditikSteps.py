"""Executable BDD steps for application-specific Meditik behavior."""

from __future__ import annotations

import pytest
from pytest_bdd import given, parsers, then, when

from refua_tests.pages.allActionsPage import AllActionsPage
from refua_tests.pages.automationIds import MeditikIds as Ids
from refua_tests.pages.medicalProfilePage import MedicalProfilePage
from refua_tests.pages.meditikBasePage import MeditekBasePage
from refua_tests.pages.meditikHomePage import MeditekHomePage
from refua_tests.pages.menuPages import (BookAppointmentPage, ExemptionsPage,
                                         FeedbackPage, LabResultsPage,
                                         MedicinesPage, ReferralsPage,
                                         SickDaysPage, UrgentCarePage,
                                         VaccinationsPage, VisitSummariesPage)
from refua_tests.pages.myAppointmentsPage import MyAppointmentsPage
from refua_tests.pages.myRequestsPage import MyRequestsPage
from refua_tests.pages.requestForms import REQUEST_FORMS, RequestFormPage
from refua_tests.pages.speedDial import SPEED_DIAL_BY_PATH, SpeedDial

HOME_WIDGETS = {
    "requests": Ids.HOME_BTN_USER_REQUESTS_WIDGET,
    "appointments": Ids.HOME_BTN_FUTURE_APPOINTMENTS_WIDGET,
    "referrals": Ids.HOME_BTN_REFERRALS_WIDGET,
    "medicines": Ids.HOME_BTN_MEDICINES_WIDGET,
    "exemptions": Ids.HOME_BTN_EXEMPTIONS_WIDGET,
}

MENU_DESTINATIONS = {
    "appointment booking": lambda page: BookAppointmentPage(page).run_menu_sanity(
        session_ready=True
    ),
    "all actions": lambda page: AllActionsPage(page).run_menu_sanity(session_ready=True),
    "urgent care": lambda page: UrgentCarePage(page).run_menu_sanity(
        MeditekBasePage.MENU_URGENT_CARE, session_ready=True
    ),
    "my appointments": lambda page: MyAppointmentsPage(page).run_menu_sanity(
        MeditekBasePage.MENU_MY_APPOINTMENTS, session_ready=True
    ),
    "my requests": lambda page: MyRequestsPage(page).run_menu_sanity(
        MeditekBasePage.MENU_MY_REQUESTS, session_ready=True
    ),
    "lab results": lambda page: LabResultsPage(page).run_menu_sanity(
        MeditekBasePage.MENU_LAB_RESULTS, session_ready=True
    ),
    "medicines": lambda page: MedicinesPage(page).run_menu_sanity(
        MeditekBasePage.MENU_MEDICINES, session_ready=True
    ),
    "visit summaries": lambda page: VisitSummariesPage(page).run_menu_sanity(
        MeditekBasePage.MENU_VISIT_SUMMARIES, session_ready=True
    ),
    "exemptions": lambda page: ExemptionsPage(page).run_menu_sanity(
        MeditekBasePage.MENU_EXEMPTIONS, session_ready=True
    ),
    "sick days": lambda page: SickDaysPage(page).run_menu_sanity(
        MeditekBasePage.MENU_SICK_DAYS, session_ready=True
    ),
    "referrals": lambda page: ReferralsPage(page).run_menu_sanity(
        MeditekBasePage.MENU_REFERRALS, session_ready=True
    ),
    "vaccinations": lambda page: VaccinationsPage(page).run_menu_sanity(
        MeditekBasePage.MENU_VACCINATIONS, session_ready=True
    ),
    "medical profile": lambda page: MedicalProfilePage(page).run_menu_sanity(
        MeditekBasePage.MENU_MEDICAL_PROFILE, session_ready=True
    ),
    "feedback": lambda page: FeedbackPage(page).run_menu_sanity(session_ready=True),
}


@pytest.fixture
def bdd_context():
    """Keep scenario-specific page objects and outcomes between BDD steps."""
    return {}


@given(parsers.parse('an authenticated "{application}" application user is on the home page'))
def authenticated_user_is_home(application, browser_page, bdd_context):
    if application != "meditik":
        pytest.skip(f"No BDD adapter is implemented yet for application: {application}")

    shell = MeditekBasePage(browser_page)
    shell.open_home()
    shell.ensure_logged_in()
    shell.dismiss_blocking_dialogs()
    bdd_context["page"] = browser_page
    bdd_context["shell"] = shell


def _page(context):
    return context["page"]


def _form_for_path(context, form_path):
    spec = next((item for item in REQUEST_FORMS if item.path == form_path), None)
    assert spec is not None, f"No request-form contract is registered for {form_path}"
    form = RequestFormPage(_page(context), spec)
    context["form"] = form
    return form


@then("the Meditik home widgets are displayed")
def home_widgets_are_displayed(bdd_context):
    MeditekHomePage(_page(bdd_context)).assert_widgets_present()


@then("the Meditik home speed dial provides its actions")
def home_speed_dial_actions_are_available(bdd_context):
    MeditekHomePage(_page(bdd_context)).assert_speed_dial_actions()


@when("the user opens the doctor request call to action")
def open_doctor_request_cta(bdd_context):
    MeditekHomePage(_page(bdd_context)).assert_send_doctor_request_cta()


@then("the All Actions page is displayed")
def all_actions_page_is_displayed(bdd_context):
    assert "/all-actions" in _page(bdd_context).url


@then("the last update timestamp is displayed")
def last_update_timestamp_is_displayed(bdd_context):
    MeditekHomePage(_page(bdd_context)).assert_last_update_time()


@when(parsers.parse('the user opens the "{widget}" home widget'))
def open_home_widget(widget, bdd_context):
    test_id = HOME_WIDGETS[widget]
    MeditekHomePage(_page(bdd_context)).open_widget(test_id)


@then(parsers.parse('the browser is on "{path}"'))
def browser_is_on_path(path, bdd_context):
    page = _page(bdd_context)
    page.wait_for_url(f"**{path}**", timeout=60000)
    assert path in page.url


@when(parsers.parse('the user opens the Meditik content page "{path}"'))
def open_meditik_content_page(path, bdd_context):
    page = _page(bdd_context)
    shell = MeditekBasePage(page)
    base_url = shell.home_url.removesuffix("/home")
    page.goto(f"{base_url}{path}", wait_until="domcontentloaded", timeout=60000)
    shell.dismiss_blocking_dialogs()
    page.wait_for_url(f"**{path}**", timeout=60000)
    shell.wait_for_loading_done()
    shell.assert_no_app_error(context=path)
    bdd_context["content_path"] = path


@then("that page provides the expected speed-dial actions")
def content_page_speed_dial_actions_are_available(bdd_context):
    page = _page(bdd_context)
    path = bdd_context["content_path"]
    dial = SpeedDial(page)
    assert dial.is_present(timeout=30000), f"Speed dial is missing on {path}"
    dial.assert_actions_present(SPEED_DIAL_BY_PATH[path])
    dial.close()


@when(parsers.parse('the user opens the "{destination}" Meditik side-menu destination'))
def open_menu_destination(destination, bdd_context):
    assert destination in MENU_DESTINATIONS, f"Unknown Meditik destination: {destination}"
    MENU_DESTINATIONS[destination](_page(bdd_context))
    bdd_context["destination"] = destination


@then(parsers.parse('the "{destination}" Meditik destination content is loaded'))
def menu_destination_content_is_loaded(destination, bdd_context):
    assert bdd_context["destination"] == destination


@when(parsers.parse('the user opens the "{form_path}" request form from All Actions'))
def open_request_form(form_path, bdd_context):
    _form_for_path(bdd_context, form_path).open_from_all_actions(session_ready=True)


@then("the request form is loaded")
def request_form_is_loaded(bdd_context):
    bdd_context["form"].assert_form_loaded()


@then("all required request form controls are visible")
def request_form_controls_are_visible(bdd_context):
    bdd_context["form"].assert_required_controls_visible()


@then("non-submit request form controls are interactive")
def request_form_controls_are_interactive(bdd_context):
    bdd_context["form"].assert_input_controls_interactive()


@then("all required request form content is displayed")
def request_form_content_is_displayed(bdd_context):
    bdd_context["form"].assert_required_content_present()


@then("the request form accepts a valid phone number")
def request_form_accepts_valid_phone(bdd_context):
    bdd_context["form"].assert_valid_phone_input()


@then("the request form rejects an invalid phone number")
def request_form_rejects_invalid_phone(bdd_context):
    bdd_context["form"].assert_invalid_phone_input()


@then("the request form additional controls are usable")
def request_form_extra_controls_are_usable(bdd_context):
    bdd_context["form"].assert_extra_controls_are_usable()


@when("the user opens Urgent Care from All Actions")
def open_urgent_care_from_all_actions(bdd_context):
    page = _page(bdd_context)
    shell = MeditekBasePage(page)
    shell.go_to_all_actions()
    shell.close_menu()
    tile = page.locator("button").filter(has_text="רפואה דחופה").first
    tile.click(force=True)
    page.wait_for_url("**/urgent-care**", timeout=60000)
    shell.wait_for_loading_done()
    shell.assert_no_app_error(context="רפואה דחופה")


@then("the Urgent Care page is loaded")
def urgent_care_page_is_loaded(bdd_context):
    page = _page(bdd_context)
    assert "/urgent-care" in page.url
    assert "דף זה לא נמצא" not in MeditekBasePage(page)._body_text(timeout=10000)


@when("the user opens the prescription request from the speed dial")
def open_prescription_from_speed_dial(bdd_context):
    page = _page(bdd_context)
    dial = SpeedDial(page)
    dial.open()
    action = page.get_by_test_id(Ids.SPEED_DIAL_PRESCRIPTION)
    action.wait_for(state="attached", timeout=10000)
    action.evaluate("element => element.click()")
    page.wait_for_url("**/prescription-request**", timeout=60000)
    dial.close()
    _form_for_path(bdd_context, "/prescription-request")


@then("the prescription request form is loaded")
def prescription_request_form_is_loaded(bdd_context):
    form = bdd_context["form"]
    form._wait_for_form_shell()
    form.assert_form_loaded()
