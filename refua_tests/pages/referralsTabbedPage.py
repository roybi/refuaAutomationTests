"""Meditik Referrals (הפניות) — tabbed /referrals page object.

Models the tabbed Referrals screen from the MediTik Referrals BDD/E2E workbook
(REFERRALS-001..024): My Referrals / Waiting for Approval / Past Referrals
tabs plus a shared empty state.

Key constraint from the workbook (REFERRALS-024): the SAME
``meditik-empty-state-title`` / ``meditik-empty-state-icon`` testids are used
by every panel, so every empty-state locator here is scoped to the active
panel and must resolve to exactly one match. ``assert_scoped_empty_state``
enforces that.

The workbook ships no referral-card testid, so a panel's populated branch is
detected as "panel has content but no scoped empty state" rather than by
counting cards. Nothing is ever seeded or deleted — the page reports whichever
branch is live and the tests decide what is assertable.

Expected empty-state COPY from the workbook is English while the application
runs in Hebrew, so copy is reported as a soft note (Allure) and never
hard-asserted; data-testid presence is the hard check, consistent with the
rest of this suite.
"""

from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import Locator, Page, expect

from refua_tests.pages.automationIds import MeditikIds as Ids
from refua_tests.pages.meditikBasePage import MeditekBasePage
from refua_tests.pages.softNotes import report_soft_note


@dataclass(frozen=True)
class ReferralTab:
    """One referral category: tab testid, panel testid, Hebrew label."""

    key: str
    tab_test_id: str
    panel_test_id: str
    label: str
    expected_empty_copy: str = ""


# Category registry — iterate this instead of repeating tab logic per test.
REFERRAL_TABS: dict[str, ReferralTab] = {
    "mine": ReferralTab(
        key="mine",
        tab_test_id=Ids.REFERRALS_TAB_MINE,
        panel_test_id=Ids.REFERRALS_PANEL_MINE,
        label="ההפניות שלי",
    ),
    "waiting_approval": ReferralTab(
        key="waiting_approval",
        tab_test_id=Ids.REFERRALS_TAB_WAITING_APPROVAL,
        panel_test_id=Ids.REFERRALS_PANEL_WAITING_APPROVAL,
        label="הפניות הממתינות לאישור",
        expected_empty_copy="You have no referral awaiting approval",
    ),
    "past": ReferralTab(
        key="past",
        tab_test_id=Ids.REFERRALS_TAB_PAST,
        panel_test_id=Ids.REFERRALS_PANEL_PAST,
        label="הפניות שעברו",
        expected_empty_copy="You have no past referrals",
    ),
}

# My Referrals is the first/default category (REFERRALS-002).
DEFAULT_TAB_KEY = "mine"


@dataclass(frozen=True)
class PanelDataState:
    """Which single branch a referral panel is currently in."""

    empty_state_visible: bool
    has_content: bool


class ReferralsTabbedPage(MeditekBasePage):
    """Tabbed Referrals screen: My / Waiting for Approval / Past."""

    PATH = Ids.REFERRALS_TABBED_PATH

    def __init__(self, page: Page):
        super().__init__(page)
        self.tabs_header = page.get_by_test_id(Ids.REFERRALS_TABS_HEADER)
        self.page_root = page.get_by_test_id(Ids.REFERRALS_PAGE)
        self.navbar_toolbar = page.get_by_test_id(Ids.MY_REQUESTS_NAVBAR_TOOLBAR)
        self.navbar_hamburger = page.get_by_test_id(
            Ids.MY_REQUESTS_NAVBAR_BTN_HAMBURGER
        )
        self.navbar_logo = page.get_by_test_id(Ids.MY_REQUESTS_NAVBAR_BTN_LOGO)
        self.navbar_tabs_portal = page.get_by_test_id(Ids.MY_REQUESTS_NAVBAR_TABS_PORTAL)
        self.home_page_marker = page.get_by_test_id(Ids.HOME_PAGE)
        self.speed_dial_fab = page.get_by_test_id(Ids.MY_REQUESTS_SPEED_DIAL_FAB)
        self.speed_dial_trigger = page.get_by_test_id(
            Ids.MY_REQUESTS_SPEED_DIAL_TRIGGER
        )

    # ------------------------------------------------------------------ #
    # Navigation
    # ------------------------------------------------------------------ #
    def open_direct(self, timeout: int = 60000):
        """Navigate straight to /referrals (a supported entry point)."""
        base = self.env_manager.get_base_url().rstrip("/")
        target = base.replace("/home", "") + self.PATH
        self.page.goto(target, wait_until="domcontentloaded", timeout=timeout)
        self.dismiss_blocking_dialogs()
        return self

    def wait_until_loaded(self, timeout: int = 60000):
        """Page-ready: URL is /referrals and the tabs header is visible."""
        self.page.wait_for_url(f"**{self.PATH}**", timeout=timeout)
        self.dismiss_blocking_dialogs()
        expect(self.tabs_header.or_(self.page_root).first).to_be_visible(
            timeout=timeout
        )
        assert self.PATH in self.page.url, (
            f"Expected URL to contain {self.PATH}, got {self.page.url}"
        )
        self.assert_no_app_error(context="Referrals")
        self.wait_for_loading_done(timeout=timeout)
        return self

    def assert_page_shell(self, timeout: int = 30000):
        """REFERRALS-001: shell chrome present and all three tabs operational."""
        for marker in (
            self.navbar_toolbar,
            self.navbar_hamburger,
            self.navbar_logo,
            self.tabs_header,
        ):
            expect(marker.first).to_be_visible(timeout=timeout)
        assert self.tabs_header.count() == 1, (
            f"Expected exactly one {Ids.REFERRALS_TABS_HEADER}; "
            f"found {self.tabs_header.count()}"
        )
        # All three tabs are displayed AND operational (visible + enabled).
        for tab_key, tab in REFERRAL_TABS.items():
            tab_el = self.page.get_by_test_id(tab.tab_test_id)
            expect(tab_el.first).to_be_visible(timeout=timeout)
            assert tab_el.first.is_enabled(), (
                f"Referrals tab {tab.tab_test_id} is present but not operational"
            )
        self.assert_no_app_error(context="Referrals shell")
        return self

    # ------------------------------------------------------------------ #
    # Tabs
    # ------------------------------------------------------------------ #
    def resolve_tab(self, tab_key: str) -> ReferralTab:
        tab = REFERRAL_TABS.get(tab_key)
        assert tab is not None, f"Unknown referral tab key: {tab_key!r}"
        return tab

    def tab_locator(self, tab_key: str) -> Locator:
        return self.page.get_by_test_id(self.resolve_tab(tab_key).tab_test_id)

    def panel_locator(self, tab_key: str) -> Locator:
        return self.page.get_by_test_id(self.resolve_tab(tab_key).panel_test_id)

    def activate_tab(self, tab_key: str, timeout: int = 30000):
        """Select a referral category and wait for its panel."""
        tab = self.resolve_tab(tab_key)
        tab_el = self.page.get_by_test_id(tab.tab_test_id)
        expect(tab_el.first).to_be_visible(timeout=timeout)
        tab_el.first.click()
        expect(self.page.get_by_test_id(tab.panel_test_id).first).to_be_visible(
            timeout=timeout
        )
        self.wait_for_loading_done(timeout=timeout)
        self.assert_no_app_error(context=f"Referrals / {tab.key}")
        return self

    def assert_tab_selected(self, tab_key: str, timeout: int = 15000):
        """The selected tab indicates its active state; siblings do not."""
        expect(self.tab_locator(tab_key).first).to_have_attribute(
            "aria-selected", "true", timeout=timeout
        )
        for key in REFERRAL_TABS:
            if key == tab_key:
                continue
            other = self.tab_locator(key)
            if other.count() > 0:
                expect(other.first).to_have_attribute(
                    "aria-selected", "false", timeout=timeout
                )
        return self

    def assert_panel_displayed(self, tab_key: str, timeout: int = 30000):
        """REFERRALS-002/003/004/015: exactly this category is displayed.

        MediTik keeps sibling tab panels mounted (swipeable carousel — verified
        live on the sibling My Requests screen), so panel visibility alone
        cannot prove exclusivity. Tab selection is the authoritative signal:
        target panel present + target tab selected + siblings unselected.
        """
        expect(self.panel_locator(tab_key).first).to_be_visible(timeout=timeout)
        self.assert_tab_selected(tab_key, timeout=timeout)
        return self

    # ------------------------------------------------------------------ #
    # Panel-scoped empty state (REFERRALS-009/010/011/024)
    # ------------------------------------------------------------------ #
    def scoped_empty_title(self, tab_key: str) -> Locator:
        panel = self.panel_locator(tab_key).first
        return panel.get_by_test_id(Ids.MY_REQUESTS_EMPTY_STATE_TITLE)

    def scoped_empty_icon(self, tab_key: str) -> Locator:
        panel = self.panel_locator(tab_key).first
        return panel.get_by_test_id(Ids.MY_REQUESTS_EMPTY_STATE_ICON)

    def inspect_panel(self, tab_key: str, timeout: int = 15000) -> PanelDataState:
        """Report which branch the panel is in — never seeds or deletes data."""
        panel = self.panel_locator(tab_key).first
        expect(panel).to_be_visible(timeout=timeout)
        self.wait_for_loading_done(timeout=timeout)

        title = self.scoped_empty_title(tab_key)
        empty_visible = title.count() > 0 and title.first.is_visible()
        panel_text = (panel.inner_text(timeout=5000) or "").strip()
        return PanelDataState(
            empty_state_visible=empty_visible,
            has_content=bool(panel_text) and not empty_visible,
        )

    def assert_scoped_empty_state(
        self, tab_key: str, *, require_icon: bool = True, timeout: int = 15000
    ):
        """Validate the empty state SCOPED to this panel, uniquely.

        REFERRALS-024: the empty-state testids are shared across panels, so the
        scoped locator must return exactly one match. Expected English copy
        from the workbook is soft-noted, not asserted, because the app is
        Hebrew.
        """
        tab = self.resolve_tab(tab_key)
        title = self.scoped_empty_title(tab_key)
        assert title.count() == 1, (
            f"{tab_key} panel: expected exactly one scoped "
            f"{Ids.MY_REQUESTS_EMPTY_STATE_TITLE}; found {title.count()}"
        )
        expect(title.first).to_be_visible(timeout=timeout)

        title_text = (title.first.inner_text(timeout=5000) or "").strip()
        assert title_text, f"{tab_key} panel: empty-state title is blank"

        if require_icon:
            icon = self.scoped_empty_icon(tab_key)
            assert icon.count() == 1, (
                f"{tab_key} panel: expected exactly one scoped "
                f"{Ids.MY_REQUESTS_EMPTY_STATE_ICON}; found {icon.count()}"
            )
            expect(icon.first).to_be_visible(timeout=timeout)

        if tab.expected_empty_copy and tab.expected_empty_copy not in title_text:
            report_soft_note(
                f"Referrals {tab_key} empty-state copy differs from the workbook: "
                f"expected text containing {tab.expected_empty_copy!r} "
                f"(English in the workbook; the app renders Hebrew), "
                f"got {title_text!r}. Continuing by data-testid."
            )
        return self

    def assert_all_panels_scope_uniquely(self, timeout: int = 20000):
        """REFERRALS-024 core: activate each panel, scoped locator is unique."""
        for tab_key in REFERRAL_TABS:
            self.activate_tab(tab_key, timeout=timeout)
            title = self.scoped_empty_title(tab_key)
            if title.count() > 0:
                assert title.count() == 1, (
                    f"{tab_key} panel: scoped empty-state title must resolve to "
                    f"one match, found {title.count()}"
                )
        return self

    def walk_all_categories(self, timeout: int = 30000):
        """REFERRALS-015: step through every category, one panel per step."""
        for tab_key in REFERRAL_TABS:
            self.activate_tab(tab_key, timeout=timeout)
            self.assert_panel_displayed(tab_key, timeout=timeout)
        return self

    # ------------------------------------------------------------------ #
    # Home navigation
    # ------------------------------------------------------------------ #
    def return_home_via_logo(self, timeout: int = 30000):
        expect(self.navbar_logo.first).to_be_visible(timeout=timeout)
        self.navbar_logo.first.click(force=True)
        expect(self.home_page_marker.first).to_be_visible(timeout=timeout)
        self.assert_no_app_error(context="home after logo")
        return self
