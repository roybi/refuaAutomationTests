"""Meditik My Requests (הבקשות שלי) — tabbed /user-requests page object.

This models the tabbed My Requests screen described in
``My_Requset_Test_cases.xlsx`` (New / Approved / Declined tabs, a shared
scoped empty-state, and a virtual request-card list).

Design principles (from the workbook's Requirements_Instructions sheet):
  * INST-002 / INST-003: generic list/panel/card checks are DATA-AGNOSTIC.
    The page never seeds or deletes data — it detects whether records exist
    and validates the populated branch, otherwise it validates the scoped
    empty state.
  * INST-005: populated and empty states are mutually exclusive within a
    scoped component; :meth:`assert_panel_data_state` enforces exactly one
    branch.
  * INST-006: only verified data-testid locators are used, and shared
    locators (empty-state, list cards) are scoped to the active panel.

Everything is parameterized by a status key so the same helpers serve every
tab — no per-tab duplication and no hardcoded record expectations.
"""

from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import Locator, Page, expect

from refua_tests.pages.automationIds import MeditikIds as Ids
from refua_tests.pages.meditikBasePage import MeditekBasePage


@dataclass(frozen=True)
class RequestTab:
    """One request category: its tab testid, panel testid and Hebrew label."""

    key: str
    tab_test_id: str
    panel_test_id: str
    label: str


# Status registry — iterate this instead of repeating tab logic per test.
REQUEST_TABS: dict[str, RequestTab] = {
    "active": RequestTab(
        key="active",
        tab_test_id=Ids.MY_REQUESTS_TAB_ACTIVE,
        panel_test_id=Ids.MY_REQUESTS_PANEL_ACTIVE,
        label="בקשות חדשות",
    ),
    "approved": RequestTab(
        key="approved",
        tab_test_id=Ids.MY_REQUESTS_TAB_APPROVED,
        panel_test_id=Ids.MY_REQUESTS_PANEL_APPROVED,
        label="בקשות שאושרו",
    ),
    "declined": RequestTab(
        key="declined",
        tab_test_id=Ids.MY_REQUESTS_TAB_DECLINED,
        panel_test_id=Ids.MY_REQUESTS_PANEL_DECLINED,
        label="בקשות שנדחו",
    ),
}

# "active" (New Requests) is the documented default context.
DEFAULT_TAB_KEY = "active"


@dataclass(frozen=True)
class PanelDataState:
    """Result of inspecting one panel's data-state branch."""

    has_records: bool
    record_count: int
    empty_state_visible: bool


class MyRequestsTabbedPage(MeditekBasePage):
    """Tabbed My Requests screen: New / Approved / Declined + shared empty state.

    Inherits the shared shell (navbar, hamburger, logo, speed dial, login,
    error detection) from :class:`MeditekBasePage`.
    """

    PATH = Ids.MY_REQUESTS_PATH

    def __init__(self, page: Page):
        super().__init__(page)
        # Page-level markers.
        self.tabs_header = page.get_by_test_id(Ids.MY_REQUESTS_TABS_HEADER)
        self.navbar_toolbar = page.get_by_test_id(Ids.MY_REQUESTS_NAVBAR_TOOLBAR)
        self.navbar_logo = page.get_by_test_id(Ids.MY_REQUESTS_NAVBAR_BTN_LOGO)
        self.navbar_hamburger = page.get_by_test_id(Ids.MY_REQUESTS_NAVBAR_BTN_HAMBURGER)
        self.home_page_marker = page.get_by_test_id(Ids.MY_REQUESTS_HOME_PAGE)
        # Speed dial FAB (My Requests screen).
        self.speed_dial_fab = page.get_by_test_id(Ids.MY_REQUESTS_SPEED_DIAL_FAB)
        self.speed_dial_trigger = page.get_by_test_id(Ids.MY_REQUESTS_SPEED_DIAL_TRIGGER)
        # Home widget.
        self.home_widget = page.get_by_test_id(Ids.MY_REQUESTS_HOME_BTN_WIDGET)
        self.home_widget_arrow = page.get_by_test_id(Ids.MY_REQUESTS_HOME_WIDGET_ARROW)
        self.widget_empty_state = page.get_by_test_id(Ids.MY_REQUESTS_WIDGET_EMPTY_STATE)

    # ------------------------------------------------------------------ #
    # Navigation
    # ------------------------------------------------------------------ #
    def open_direct(self, timeout: int = 60000):
        """Navigate straight to /user-requests (clean-context entry)."""
        base = self.env_manager.get_base_url().rstrip("/")
        # base_url is the /home root; swap to the My Requests path on same host.
        target = base.replace("/home", "") + self.PATH
        self.page.goto(target, wait_until="domcontentloaded", timeout=timeout)
        self.dismiss_blocking_dialogs()
        return self

    def open_from_home_widget(self, timeout: int = 60000):
        """Activate the Home My Requests widget arrow to reach the page."""
        expect(self.home_widget.first).to_be_visible(timeout=timeout)
        arrow = self.home_widget_arrow.first
        target = arrow if arrow.count() > 0 else self.home_widget.first
        target.click(force=True)
        self.wait_for_loading_done()
        self.dismiss_blocking_dialogs()
        return self

    def wait_until_loaded(self, timeout: int = 60000):
        """Page-ready: URL is /user-requests and the tabs header is visible."""
        self.page.wait_for_url(f"**{self.PATH}**", timeout=timeout)
        self.dismiss_blocking_dialogs()
        expect(self.tabs_header.first).to_be_visible(timeout=timeout)
        assert self.PATH in self.page.url, (
            f"Expected URL to contain {self.PATH}, got {self.page.url}"
        )
        self.assert_no_app_error(context="My Requests")
        self.wait_for_loading_done(timeout=timeout)
        return self

    def assert_page_shell(self, timeout: int = 30000):
        """Toolbar, hamburger, logo and tabs header are visible and unique."""
        for marker in (
            self.navbar_toolbar,
            self.navbar_hamburger,
            self.navbar_logo,
            self.tabs_header,
        ):
            expect(marker.first).to_be_visible(timeout=timeout)
        # Uniqueness: the page shell markers must resolve to exactly one node.
        for unique in (self.navbar_toolbar, self.tabs_header):
            assert unique.count() == 1, (
                f"Expected exactly one {unique}; found {unique.count()}"
            )
        self.assert_no_app_error(context="My Requests shell")
        return self

    # ------------------------------------------------------------------ #
    # Tabs
    # ------------------------------------------------------------------ #
    def resolve_tab(self, tab_key: str) -> RequestTab:
        tab = REQUEST_TABS.get(tab_key)
        assert tab is not None, f"Unknown request tab key: {tab_key!r}"
        return tab

    def tab_locator(self, tab_key: str) -> Locator:
        return self.page.get_by_test_id(self.resolve_tab(tab_key).tab_test_id)

    def panel_locator(self, tab_key: str) -> Locator:
        return self.page.get_by_test_id(self.resolve_tab(tab_key).panel_test_id)

    def activate_tab(self, tab_key: str, timeout: int = 30000):
        """Click a status tab and wait for its panel to become visible."""
        tab = self.resolve_tab(tab_key)
        tab_el = self.page.get_by_test_id(tab.tab_test_id)
        expect(tab_el.first).to_be_visible(timeout=timeout)
        tab_el.first.click()
        expect(self.page.get_by_test_id(tab.panel_test_id).first).to_be_visible(
            timeout=timeout
        )
        self.wait_for_loading_done(timeout=timeout)
        self.assert_no_app_error(context=f"My Requests / {tab.key}")
        return self

    def assert_tab_selected(self, tab_key: str, timeout: int = 15000):
        """The MUI tab for tab_key is marked selected (aria-selected)."""
        tab = self.tab_locator(tab_key)
        expect(tab.first).to_have_attribute("aria-selected", "true", timeout=timeout)
        for key in REQUEST_TABS:
            if key == tab_key:
                continue
            other = self.tab_locator(key)
            if other.count() > 0:
                expect(other.first).to_have_attribute("aria-selected", "false", timeout=timeout)
        return self

    def assert_only_panel_active(self, tab_key: str):
        """Assert tab_key is the single active category.

        MediTik renders all three request panels simultaneously (a swipeable
        carousel: every ``meditik-tabs-panel-*`` node stays mounted, visible
        and ``display:flex`` regardless of selection — verified against the
        live DOM). Panel presence therefore cannot distinguish active from
        inactive; the authoritative signal is the tab's ``aria-selected``.

        So: the target panel must be present, the target tab must be selected,
        and every sibling tab must be unselected (exactly one active category).
        """
        expect(self.panel_locator(tab_key).first).to_be_visible()
        self.assert_tab_selected(tab_key)
        return self

    def rapid_switch(self, sequence: list[str], timeout: int = 30000):
        """Click a sequence of tabs back-to-back (no settle wait between clicks).

        Only the final tab's outcome is verified — MYREQ-018 tests that fast
        switching still converges on the last-clicked tab, not every
        intermediate render.
        """
        for tab_key in sequence:
            self.tab_locator(tab_key).first.click()
        final_key = sequence[-1]
        expect(self.panel_locator(final_key).first).to_be_visible(timeout=timeout)
        self.wait_for_loading_done(timeout=timeout)
        self.assert_only_panel_active(final_key)
        self.assert_panel_data_state(final_key, timeout=timeout)
        return self

    def assert_all_categories_valid(self, timeout: int = 20000):
        """Activate every request category and validate its data-state branch."""
        for tab_key in REQUEST_TABS:
            self.activate_tab(tab_key, timeout=timeout)
            self.assert_panel_data_state(tab_key, timeout=timeout)
        return self

    def assert_hebrew_rtl_rendering(self, timeout: int = 20000):
        """Hebrew tab labels render correctly and the document flows RTL."""
        doc_dir = self.page.evaluate("() => document.documentElement.dir || getComputedStyle(document.documentElement).direction")
        assert doc_dir == "rtl", f"Expected RTL document direction, got {doc_dir!r}"

        for tab_key, tab in REQUEST_TABS.items():
            self.activate_tab(tab_key, timeout=timeout)
            tab_text = (self.tab_locator(tab_key).first.inner_text(timeout=5000) or "").strip()
            assert tab.label in tab_text, (
                f"Expected Hebrew label {tab.label!r} in {tab_key} tab text, got {tab_text!r}"
            )
            self.assert_panel_data_state(tab_key, timeout=timeout)
        return self

    def assert_widget_data_state(self, timeout: int = 20000):
        """Home widget: populated content XOR the scoped widget empty state."""
        expect(self.home_widget.first).to_be_visible(timeout=timeout)
        empty_visible = (
            self.widget_empty_state.count() > 0 and self.widget_empty_state.first.is_visible()
        )
        if empty_visible:
            extra_info = self.page.get_by_test_id(Ids.MY_REQUESTS_WIDGET_EMPTY_STATE_EXTRA_INFO)
            expect(extra_info.first).to_be_visible(timeout=timeout)
        else:
            widget_text = (self.home_widget.first.inner_text(timeout=5000) or "").strip()
            assert widget_text, "My Requests widget: no empty state and no visible content"
        return self

    # ------------------------------------------------------------------ #
    # Data-agnostic panel content (INST-002/003/005)
    # ------------------------------------------------------------------ #
    def _scoped_cards(self, tab_key: str) -> Locator:
        """Request cards scoped to the active panel (shared prefix locator)."""
        panel = self.panel_locator(tab_key).first
        return panel.locator(
            f'[data-testid^="{Ids.MY_REQUESTS_LIST_CARD_PREFIX}"]'
        )

    def _scoped_empty_state(self, tab_key: str) -> Locator:
        """Empty-state title scoped to the active panel (shared component)."""
        panel = self.panel_locator(tab_key).first
        return panel.get_by_test_id(Ids.MY_REQUESTS_EMPTY_STATE_TITLE)

    def inspect_panel(self, tab_key: str, timeout: int = 15000) -> PanelDataState:
        """Detect which single data-state branch a panel is in — no seeding."""
        panel = self.panel_locator(tab_key).first
        expect(panel).to_be_visible(timeout=timeout)
        self.wait_for_loading_done(timeout=timeout)

        cards = self._scoped_cards(tab_key)
        empty_title = self._scoped_empty_state(tab_key)

        card_count = cards.count()
        empty_visible = empty_title.count() > 0 and empty_title.first.is_visible()
        return PanelDataState(
            has_records=card_count > 0,
            record_count=card_count,
            empty_state_visible=empty_visible,
        )

    def assert_panel_data_state(self, tab_key: str, timeout: int = 15000) -> PanelDataState:
        """Validate exactly ONE valid branch (records XOR scoped empty state).

        Populated branch: every scoped card has a unique data-testid and
        non-empty content, and the empty state is absent.
        Empty branch: the scoped empty-state marker is visible and no stale
        cards remain.
        """
        state = self.inspect_panel(tab_key, timeout=timeout)

        if state.has_records:
            cards = self._scoped_cards(tab_key)
            # Uniqueness of virtual-index locators (MYREQ-017).
            testids = []
            for i in range(state.record_count):
                tid = cards.nth(i).get_attribute("data-testid")
                testids.append(tid)
            assert len(testids) == len(set(testids)), (
                f"Duplicate request-card data-testid values in {tab_key} panel: "
                f"{testids!r}"
            )
            expect(cards.first).to_be_visible(timeout=timeout)
            first_text = (cards.first.inner_text(timeout=5000) or "").strip()
            assert first_text and first_text.lower() != "null", (
                f"{tab_key} panel: first card empty/null content: {first_text!r}"
            )
            # Mutual exclusivity: scoped empty state must be absent.
            assert not state.empty_state_visible, (
                f"{tab_key} panel: records AND empty state both active"
            )
        else:
            assert state.empty_state_visible, (
                f"{tab_key} panel: no records and no scoped empty state visible"
            )
        return state

    # ------------------------------------------------------------------ #
    # Speed dial / quick actions
    # ------------------------------------------------------------------ #
    def expand_speed_dial(self, timeout: int = 15000):
        """Activate the FAB and confirm the quick-actions container expands."""
        fab = self.speed_dial_fab if self.speed_dial_fab.count() > 0 else self.speed_dial_trigger
        expect(fab.first).to_be_visible(timeout=timeout)
        fab.first.click(force=True)
        # MUI SpeedDial marks the trigger expanded via aria-expanded=true.
        trigger = self.speed_dial_trigger.first
        try:
            expect(trigger).to_have_attribute("aria-expanded", "true", timeout=timeout)
        except Exception:
            # Fallback: at least one action button becomes visible.
            actions = self.page.locator(
                f'[data-testid^="{Ids.SPEED_DIAL_ACTION_PREFIX}"]'
            )
            expect(actions.first).to_be_visible(timeout=timeout)
        return self

    # ------------------------------------------------------------------ #
    # Navigation back to Home
    # ------------------------------------------------------------------ #
    def return_home_via_logo(self, timeout: int = 30000):
        expect(self.navbar_logo.first).to_be_visible(timeout=timeout)
        self.navbar_logo.first.click(force=True)
        expect(self.home_page_marker.first).to_be_visible(timeout=timeout)
        self.assert_no_app_error(context="home after logo")
        return self

    def open_hamburger(self, timeout: int = 30000):
        expect(self.navbar_hamburger.first).to_be_visible(timeout=timeout)
        self.navbar_hamburger.first.click(force=True)
        expect(self.side_drawer.first).to_be_visible(timeout=timeout)
        return self
