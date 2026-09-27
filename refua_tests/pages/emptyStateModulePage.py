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
    """

    MODULE_NAME: str = ""
    PATH: str = ""
    PAGE_TEST_ID: str = ""
    EXPECTED_EMPTY_TEXT: str = ""

    # Shared empty-state testids (identical across these modules).
    EMPTY_STATE_TITLE_ID: str = Ids.SICK_DAYS_EMPTY_STATE_TITLE
    EMPTY_STATE_ICON_ID: str = Ids.SICK_DAYS_EMPTY_STATE_ICON

    def __init__(self, page: Page):
        super().__init__(page)
        assert self.PATH and self.MODULE_NAME, (
            f"{type(self).__name__} must define MODULE_NAME and PATH"
        )
        self.page_root = (
            page.get_by_test_id(self.PAGE_TEST_ID) if self.PAGE_TEST_ID else None
        )
        self.navbar_toolbar = page.get_by_test_id(Ids.MY_REQUESTS_NAVBAR_TOOLBAR)
        self.navbar_hamburger = page.get_by_test_id(
            Ids.MY_REQUESTS_NAVBAR_BTN_HAMBURGER
        )
        self.navbar_logo = page.get_by_test_id(Ids.MY_REQUESTS_NAVBAR_BTN_LOGO)
        self.empty_state_title = page.get_by_test_id(self.EMPTY_STATE_TITLE_ID)
        self.empty_state_icon = page.get_by_test_id(self.EMPTY_STATE_ICON_ID)
        self.speed_dial_fab = page.get_by_test_id(Ids.MY_REQUESTS_SPEED_DIAL_FAB)
        self.speed_dial_trigger = page.get_by_test_id(
            Ids.MY_REQUESTS_SPEED_DIAL_TRIGGER
        )

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
            self.navbar_toolbar, Ids.MY_REQUESTS_NAVBAR_TOOLBAR, timeout
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

    def assert_single_page_instance(self, timeout: int = 15000):
        """After refresh: one route and one empty state — no duplicated UI."""
        assert self.PATH in self.page.url, (
            f"Expected to remain on {self.PATH} after refresh, got {self.page.url}"
        )
        self._assert_unique_and_visible(
            self.navbar_toolbar, Ids.MY_REQUESTS_NAVBAR_TOOLBAR, timeout
        )
        self._assert_unique_and_visible(
            self.empty_state_title, self.EMPTY_STATE_TITLE_ID, timeout
        )
        self.assert_no_app_error(context=f"{self.MODULE_NAME} after refresh")
        return self
