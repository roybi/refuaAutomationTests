"""Meditik Medical Profile (פרופיל רפואי) — /medical-profile page object.

This class already existed as a thin data-testid mapping used by the older
side-menu sanity suite (``refua_tests/tests/meditikMenuSanity.py``). It is
EXTENDED here rather than duplicated, so the Medical_Profile_Test_Cases_1
workbook and the menu suite share one locator surface: a testid change is
fixed once.

What the workbook does and does not ground
------------------------------------------
The workbook's own Coverage Summary is explicit: "the supplied inventory does
not expose dedicated Medical Profile content fields or cards. Content-specific
expectations are marked for confirmation." The grounded surface is therefore
only the shared application shell (navbar toolbar, hamburger, logo, tabs
portal) plus the global quick-action control whose supplied content includes
זימון תור.

Consequently just 3 of the 14 cases are Ready (001, 004, 011) and all three are
chrome/navigation level. The assertions below deliberately stop at that
boundary: no profile field, label or card is asserted, because none is
specified. Inventing those locators would produce tests that pass or fail for
reasons unrelated to the product.

Persistence expectations
------------------------
Every case carries a "Verify no mutation" persistence check. This suite has no
credentialed data-store reader, so :meth:`assert_no_profile_mutation_signals`
implements the honest UI-level subset of that expectation — route unchanged,
single page instance, no error shell, no duplicated chrome — and says so in its
docstring. The data-store half of the check remains an open item rather than a
silently-passing assertion.
"""

from __future__ import annotations

from playwright.sync_api import Locator, expect

from refua_tests.pages.automationIds import MeditikIds as Ids
from refua_tests.pages.meditikContentPage import MeditekContentPage
from refua_tests.pages.softNotes import report_soft_note


class MedicalProfilePage(MeditekContentPage):
    """The /medical-profile screen: shared shell chrome plus quick actions."""

    PAGE_TITLE = "פרופיל רפואי"
    PATH = Ids.MEDICAL_PROFILE_PATH
    PAGE_TEST_ID = Ids.MEDICAL_PROFILE_PAGE
    EMPTY_MARKERS = ("אין לך עדיין פרופיל רפואי",)

    # The quick-action label the workbook states is present (MEDICAL-PROFILE-004).
    QUICK_ACTION_LABEL = "זימון תור"

    def __init__(self, page):
        super().__init__(page)
        self.navbar_toolbar = page.get_by_test_id(Ids.MEDICAL_PROFILE_NAVBAR_TOOLBAR)
        self.navbar_hamburger = page.get_by_test_id(
            Ids.MEDICAL_PROFILE_NAVBAR_BTN_HAMBURGER
        )
        self.navbar_hamburger_img = page.get_by_test_id(
            Ids.MEDICAL_PROFILE_NAVBAR_IMG_HAMBURGER
        )
        self.navbar_logo = page.get_by_test_id(Ids.MEDICAL_PROFILE_NAVBAR_BTN_LOGO)
        self.navbar_logo_img = page.get_by_test_id(Ids.MEDICAL_PROFILE_NAVBAR_IMG_LOGO)
        self.navbar_tabs_portal = page.get_by_test_id(
            Ids.MEDICAL_PROFILE_NAVBAR_TABS_PORTAL
        )
        self.speed_dial_trigger = page.get_by_test_id(
            Ids.MEDICAL_PROFILE_SPEED_DIAL_TRIGGER
        )
        self.speed_dial_fab = page.get_by_test_id(Ids.MEDICAL_PROFILE_SPEED_DIAL_FAB)
        self.speed_dial_add_icon = page.get_by_test_id(
            Ids.MEDICAL_PROFILE_SPEED_DIAL_ADD_ICON
        )
        self.speed_dial_book_appointment = page.get_by_test_id(
            Ids.SPEED_DIAL_BOOK_APPOINTMENT
        )

    # ------------------------------------------------------------------ #
    # Navigation
    # ------------------------------------------------------------------ #
    def open_direct(self, timeout: int = 60000):
        """Navigate straight to the module route (no menu interaction)."""
        base = self.env_manager.get_base_url().rstrip("/")
        target = base.replace("/home", "") + self.PATH
        self.page.goto(target, wait_until="domcontentloaded", timeout=timeout)
        self.dismiss_blocking_dialogs()
        return self

    def open_via_application_menu(self, timeout: int = 60000):
        """MEDICAL-PROFILE-011: reach the route through the side menu.

        Uses the shell's menu navigation so the hard check stays the menu
        item's data-testid, with the Hebrew label only soft-checked.
        """
        self.go_to_medical_profile()
        self.page.wait_for_url(f"**{self.PATH}**", timeout=timeout)
        self.dismiss_blocking_dialogs()
        return self

    # ------------------------------------------------------------------ #
    # Shared assertion helper
    # ------------------------------------------------------------------ #
    def _assert_unique_and_visible(self, locator: Locator, name: str, timeout: int):
        """The workbook's validation column rejects duplicate actionable locators."""
        count = locator.count()
        assert count == 1, (
            f"Medical Profile: expected exactly one {name!r}; found {count}"
        )
        expect(locator.first).to_be_visible(timeout=timeout)

    # ------------------------------------------------------------------ #
    # Assertions — MEDICAL-PROFILE-001 / 011
    # ------------------------------------------------------------------ #
    def assert_page_shell(self, timeout: int = 30000):
        """The route is /medical-profile and exactly one toolbar is displayed.

        MEDICAL-PROFILE-001's only grounded id is ``meditik-navbar-toolbar``,
        so page-ready is route + toolbar, not a content assertion.
        """
        assert self.PATH in self.page.url, (
            f"Expected URL to contain {self.PATH}, got {self.page.url}"
        )
        self._assert_unique_and_visible(
            self.navbar_toolbar, Ids.MEDICAL_PROFILE_NAVBAR_TOOLBAR, timeout
        )
        self.assert_no_app_error(context="Medical Profile shell")
        self._soft_check_page_title()
        return self

    def assert_navigation_chrome(self, timeout: int = 30000):
        """Hamburger and logo controls are each present once and usable.

        Grounded by MEDICAL-PROFILE-002/003/010. Those cases are themselves
        clarification-blocked on the resulting MENU CONTENT and LOGO
        DESTINATION, which this method never asserts — it only proves the
        controls resolve uniquely, are visible and are enabled.
        """
        for locator, name in (
            (self.navbar_hamburger, Ids.MEDICAL_PROFILE_NAVBAR_BTN_HAMBURGER),
            (self.navbar_hamburger_img, Ids.MEDICAL_PROFILE_NAVBAR_IMG_HAMBURGER),
            (self.navbar_logo, Ids.MEDICAL_PROFILE_NAVBAR_BTN_LOGO),
            (self.navbar_logo_img, Ids.MEDICAL_PROFILE_NAVBAR_IMG_LOGO),
        ):
            self._assert_unique_and_visible(locator, name, timeout)

        for locator, name in (
            (self.navbar_hamburger, Ids.MEDICAL_PROFILE_NAVBAR_BTN_HAMBURGER),
            (self.navbar_logo, Ids.MEDICAL_PROFILE_NAVBAR_BTN_LOGO),
        ):
            assert locator.first.is_enabled(timeout=timeout), (
                f"Medical Profile: {name!r} is visible but disabled"
            )
        return self

    # ------------------------------------------------------------------ #
    # Assertions — MEDICAL-PROFILE-004
    # ------------------------------------------------------------------ #
    def assert_quick_action_control(self, timeout: int = 30000):
        """Trigger, FAB and add icon each resolve exactly once and are visible."""
        for locator, name in (
            (self.speed_dial_trigger, Ids.MEDICAL_PROFILE_SPEED_DIAL_TRIGGER),
            (self.speed_dial_fab, Ids.MEDICAL_PROFILE_SPEED_DIAL_FAB),
            (self.speed_dial_add_icon, Ids.MEDICAL_PROFILE_SPEED_DIAL_ADD_ICON),
        ):
            self._assert_unique_and_visible(locator, name, timeout)
        return self

    def expand_quick_actions(self, timeout: int = 15000):
        """Open the quick-action control and confirm it reports itself expanded."""
        fab = (
            self.speed_dial_fab
            if self.speed_dial_fab.count() > 0
            else self.speed_dial_trigger
        )
        expect(fab.first).to_be_visible(timeout=timeout)
        fab.first.click(force=True)
        trigger = self.speed_dial_trigger.first
        try:
            expect(trigger).to_have_attribute("aria-expanded", "true", timeout=timeout)
        except Exception:
            # Fallback: at least one action button became visible.
            actions = self.page.locator(
                f'[data-testid^="{Ids.SPEED_DIAL_ACTION_PREFIX}"]'
            )
            expect(actions.first).to_be_visible(timeout=timeout)
        return self

    def assert_appointment_booking_action_exposed(self, timeout: int = 15000):
        """The opened control exposes the supplied appointment-booking action.

        Hard check is the project-grounded action testid when the environment
        renders it; the workbook supplies only the Hebrew content זימון תור,
        so a missing testid degrades to the label (recorded as a soft note)
        rather than inventing an id.
        """
        if self.speed_dial_book_appointment.count() > 0:
            expect(self.speed_dial_book_appointment.first).to_be_visible(
                timeout=timeout
            )
            return self

        report_soft_note(
            f"Quick-action testid {Ids.SPEED_DIAL_BOOK_APPOINTMENT!r} is not "
            f"rendered on {self.PATH}; falling back to the workbook's supplied "
            f"label {self.QUICK_ACTION_LABEL!r}."
        )
        by_label = self.page.get_by_text(self.QUICK_ACTION_LABEL, exact=True)
        assert by_label.count() > 0, (
            f"Medical Profile: the opened quick-action control exposes neither "
            f"{Ids.SPEED_DIAL_BOOK_APPOINTMENT!r} nor the supplied label "
            f"{self.QUICK_ACTION_LABEL!r}"
        )
        expect(by_label.first).to_be_visible(timeout=timeout)
        return self

    # ------------------------------------------------------------------ #
    # Persistence / side-effect proxy
    # ------------------------------------------------------------------ #
    def assert_no_profile_mutation_signals(self, timeout: int = 15000):
        """UI-observable subset of the workbook's "verify no mutation" check.

        Asserts the route did not move, the shell is not duplicated and no
        error page appeared. It deliberately does NOT claim to have verified
        the data store — this suite has no credentialed reader for it, and the
        store-level half of that expectation stays an open item.
        """
        assert self.PATH in self.page.url, (
            f"Expected to remain on {self.PATH}, got {self.page.url}"
        )
        self._assert_unique_and_visible(
            self.navbar_toolbar, Ids.MEDICAL_PROFILE_NAVBAR_TOOLBAR, timeout
        )
        if self.page_root is not None and self.page_root.count() > 1:
            raise AssertionError(
                f"Medical Profile: page root {self.PAGE_TEST_ID!r} is rendered "
                f"{self.page_root.count()} times — duplicated page instance"
            )
        self.assert_no_app_error(context="Medical Profile side-effect check")
        return self
