"""Reusable base for MediTik "simple module" pages built around an empty state.

Several MediTik modules share one shape: a non-tabbed route whose grounded
coverage is the shell chrome plus a single page-level empty state (icon +
title), with workbooks that require failing on a MISSING, DUPLICATED or HIDDEN
element and that pin the empty-state copy exactly.

Sick Days (/sick-days) and Vaccinations (/vaccinations) are both instances, and
their workbooks are case-for-case twins. Rather than maintain near-identical
page objects, a subclass supplies four class attributes and inherits every
assertion:

    class VaccinationsModulePage(EmptyStateModulePage):
        MODULE_NAME = "Vaccinations"
        PATH = Ids.VACCINATIONS_MODULE_PATH
        PAGE_TEST_ID = Ids.VACCINATIONS_PAGE
        EXPECTED_EMPTY_TEXT = Ids.VACCINATIONS_EXPECTED_EMPTY_TEXT

Copy is asserted HARD here because these strings are Hebrew — the application's
native language — and the source workbooks explicitly require failing when the
text differs. That is deliberately different from workbooks whose expected copy
is an English translation of a Hebrew UI, where a mismatch is a soft note.
"""

from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import Locator, Page, expect

from refua_tests.pages.automationIds import MeditikIds as Ids
from refua_tests.pages.meditikBasePage import MeditekBasePage


@dataclass(frozen=True)
class ModuleEmptyState:
    """Whether the module is in its empty-state branch or shows records."""

    empty_state_visible: bool
    has_content: bool


class EmptyStateModulePage(MeditekBasePage):
    """A non-tabbed module page whose coverage centres on a unique empty state.

    Subclasses MUST set MODULE_NAME, PATH and EXPECTED_EMPTY_TEXT.
    PAGE_TEST_ID is optional — some modules expose a page-root testid, others
    are identified by the toolbar plus the route.
    MENU_LABEL is optional and only needed for the "reached through application
    navigation" cases (e.g. VSUM-011).
    ROW_PREFIX is optional and only used to prove the EMPTY branch really has
    no records (e.g. VSUM-008's "no list card or phantom record").
    """

    MODULE_NAME: str = ""
    PATH: str = ""
    PAGE_TEST_ID: str = ""
    EXPECTED_EMPTY_TEXT: str = ""
    MENU_LABEL: str = ""
    ROW_PREFIX: str = ""

    # Shared empty-state testids (identical across these modules).
    EMPTY_STATE_TITLE_ID: str = Ids.EMPTY_STATE_TITLE
    EMPTY_STATE_ICON_ID: str = Ids.EMPTY_STATE_ICON

    def __init__(self, page: Page):
        super().__init__(page)
        assert self.PATH and self.MODULE_NAME, (
            f"{type(self).__name__} must define MODULE_NAME and PATH"
        )
        self.page_root = (
            page.get_by_test_id(self.PAGE_TEST_ID) if self.PAGE_TEST_ID else None
        )
        self.navbar_toolbar = page.get_by_test_id(Ids.NAVBAR_TOOLBAR)
        self.navbar_hamburger = page.get_by_test_id(Ids.NAVBAR_BTN_HAMBURGER)
        self.navbar_logo = page.get_by_test_id(Ids.NAVBAR_BTN_LOGO)
        self.empty_state_title = page.get_by_test_id(self.EMPTY_STATE_TITLE_ID)
        self.empty_state_icon = page.get_by_test_id(self.EMPTY_STATE_ICON_ID)
        self.speed_dial_fab = page.get_by_test_id(Ids.SPEED_DIAL_FAB)
        self.speed_dial_trigger = page.get_by_test_id(Ids.SPEED_DIAL_TRIGGER)
        self.speed_dial_add_icon = page.get_by_test_id(Ids.SPEED_DIAL_ADD_ICON)

    # ------------------------------------------------------------------ #
    # Navigation
    # ------------------------------------------------------------------ #
    def open_direct(self, timeout: int = 60000):
        """Navigate straight to the module route."""
        base = self.env_manager.get_base_url().rstrip("/")
        target = base.replace("/home", "") + self.PATH
        self.page.goto(target, wait_until="domcontentloaded", timeout=timeout)
        self.dismiss_blocking_dialogs()
        return self

    def open_via_application_menu(self, timeout: int = 60000):
        """Reach the route through the side menu instead of a direct URL.

        Needed by the "reached through application navigation" cases. The hard
        check stays the menu item's data-testid (MeditekBasePage maps label ->
        testid); the Hebrew label is only soft-checked.
        """
        assert self.MENU_LABEL, (
            f"{type(self).__name__} must define MENU_LABEL to navigate via the menu"
        )
        self.navigate_via_menu(self.MENU_LABEL)
        self.page.wait_for_url(f"**{self.PATH}**", timeout=timeout)
        self.dismiss_blocking_dialogs()
        return self

    def wait_until_loaded(self, timeout: int = 60000):
        """Page-ready: the route matches and the toolbar is visible."""
        self.page.wait_for_url(f"**{self.PATH}**", timeout=timeout)
        self.dismiss_blocking_dialogs()
        expect(self.navbar_toolbar.first).to_be_visible(timeout=timeout)
        assert self.PATH in self.page.url, (
            f"Expected URL to contain {self.PATH}, got {self.page.url}"
        )
        self.assert_no_app_error(context=self.MODULE_NAME)
        self.wait_for_loading_done(timeout=timeout)
        return self

    def refresh(self, timeout: int = 60000):
        """Reload and wait for the page to settle again."""
        self.page.reload(wait_until="domcontentloaded", timeout=timeout)
        self.dismiss_blocking_dialogs()
        self.wait_until_loaded(timeout=timeout)
        return self

    # ------------------------------------------------------------------ #
    # State inspection
    # ------------------------------------------------------------------ #
    def inspect(self, timeout: int = 15000) -> ModuleEmptyState:
        """Report which branch the page is in — never seeds or deletes data."""
        self.wait_for_loading_done(timeout=timeout)
        empty_visible = (
            self.empty_state_title.count() > 0
            and self.empty_state_title.first.is_visible()
        )
        body = self._body_text(timeout=5000)
        return ModuleEmptyState(
            empty_state_visible=empty_visible,
            has_content=bool(body) and not empty_visible,
        )

    # ------------------------------------------------------------------ #
    # Assertions
    # ------------------------------------------------------------------ #
    def _assert_unique_and_visible(self, locator: Locator, name: str, timeout: int):
        """These workbooks fail on missing, duplicated OR hidden elements."""
        count = locator.count()
        assert count == 1, (
            f"{self.MODULE_NAME}: expected exactly one {name}; found {count}"
        )
        expect(locator.first).to_be_visible(timeout=timeout)

    def assert_page_shell(self, timeout: int = 30000):
        """Toolbar and empty-state title are displayed, each uniquely."""
        self._assert_unique_and_visible(
            self.navbar_toolbar, Ids.NAVBAR_TOOLBAR, timeout
        )
        self._assert_unique_and_visible(
            self.empty_state_title, self.EMPTY_STATE_TITLE_ID, timeout
        )
        self.assert_no_app_error(context=f"{self.MODULE_NAME} shell")
        return self

    def assert_empty_state_text(self, timeout: int = 15000):
        """The empty-state copy matches EXACTLY (hard assertion by design)."""
        assert self.EXPECTED_EMPTY_TEXT, (
            f"{type(self).__name__} must define EXPECTED_EMPTY_TEXT to assert copy"
        )
        self._assert_unique_and_visible(
            self.empty_state_title, self.EMPTY_STATE_TITLE_ID, timeout
        )
        actual = (
            self.empty_state_title.first.inner_text(timeout=timeout) or ""
        ).strip()
        normalised = " ".join(actual.split())
        assert normalised == self.EXPECTED_EMPTY_TEXT, (
            f"{self.MODULE_NAME} empty-state text mismatch.\n"
            f"  expected: {self.EXPECTED_EMPTY_TEXT!r}\n"
            f"  actual:   {normalised!r}"
        )
        return self

    def assert_empty_state_icon(self, timeout: int = 15000):
        """Exactly one visible icon whose image actually loaded."""
        self._assert_unique_and_visible(
            self.empty_state_icon, self.EMPTY_STATE_ICON_ID, timeout
        )
        # "the image is loaded" — a broken <img> is visible but has no pixels.
        loaded = self.empty_state_icon.first.evaluate(
            """
            element => {
                const img = element.tagName === 'IMG'
                    ? element
                    : element.querySelector('img');
                if (!img) {
                    // An inline SVG / icon font has no naturalWidth; treat a
                    // rendered box as loaded.
                    const box = element.getBoundingClientRect();
                    return box.width > 0 && box.height > 0;
                }
                return img.complete && img.naturalWidth > 0;
            }
            """
        )
        assert loaded, (
            f"{self.MODULE_NAME} empty-state icon is present but its image did "
            f"not load (broken image or zero-sized element)"
        )
        return self

    def assert_quick_action_control(self, timeout: int = 30000):
        """Trigger, FAB and add icon each resolve exactly once and are usable.

        Grounded by VSUM-004, whose validation column rejects a duplicate
        actionable locator. Deliberately does NOT open the control or assert
        which actions it contains — the individual action ids are not supplied
        by these module workbooks.
        """
        for locator, name in (
            (self.speed_dial_trigger, Ids.SPEED_DIAL_TRIGGER),
            (self.speed_dial_fab, Ids.SPEED_DIAL_FAB),
            (self.speed_dial_add_icon, Ids.SPEED_DIAL_ADD_ICON),
        ):
            self._assert_unique_and_visible(locator, name, timeout)

        actionable = (
            self.speed_dial_fab
            if self.speed_dial_fab.count() > 0
            else self.speed_dial_trigger
        )
        assert actionable.first.is_enabled(timeout=timeout), (
            f"{self.MODULE_NAME}: the quick-action control is visible but disabled"
        )
        return self

    def assert_complete_empty_state(self, timeout: int = 15000):
        """Icon AND exact title shown once, with no list card or phantom record.

        This is the zero-result case (VSUM-008): the empty branch must be
        complete, and the page must not simultaneously render a record.
        """
        self.assert_empty_state_icon(timeout=timeout)
        self.assert_empty_state_text(timeout=timeout)

        if self.ROW_PREFIX:
            rows = self.page.locator(f'[data-testid^="{self.ROW_PREFIX}"]')
            assert rows.count() == 0, (
                f"{self.MODULE_NAME}: the empty state is displayed but "
                f"{rows.count()} row(s) matching {self.ROW_PREFIX!r} are also "
                f"rendered — phantom record"
            )

        # Legacy list cards (pre-row-testid rollout) must not coexist either.
        cards = self.page.locator("[id$='-card-title']")
        visible_cards = [
            index for index in range(cards.count()) if cards.nth(index).is_visible()
        ]
        assert not visible_cards, (
            f"{self.MODULE_NAME}: the empty state is displayed but "
            f"{len(visible_cards)} list card(s) are visible — phantom record"
        )
        return self

    def assert_single_page_instance(self, timeout: int = 15000):
        """After refresh: one route and one empty state — no duplicated UI."""
        assert self.PATH in self.page.url, (
            f"Expected to remain on {self.PATH} after refresh, got {self.page.url}"
        )
        self._assert_unique_and_visible(
            self.navbar_toolbar, Ids.NAVBAR_TOOLBAR, timeout
        )
        self._assert_unique_and_visible(
            self.empty_state_title, self.EMPTY_STATE_TITLE_ID, timeout
        )
        self.assert_no_app_error(context=f"{self.MODULE_NAME} after refresh")
        return self
