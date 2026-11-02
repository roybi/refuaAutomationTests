"""Meditik My Appointments (התורים שלי) — tabbed /zimun-torim page object.

Models the tabbed My Appointments screen from the My Appointments workbook
(APPT-001..034): Upcoming / Waiting Lists / Past Appointments tabs, a shared
scoped empty state, a Past-appointments card list, a filter entry, a booking
link and the Home future-appointments widget.

Design principles (identical to the My Requests suite, which these mirror):
  * Generic list/panel/card/widget checks are DATA-AGNOSTIC. The page never
    seeds or deletes appointments — it detects whether records exist and
    validates the populated branch, otherwise the scoped empty state.
  * Populated and empty states are mutually exclusive within a scoped
    component; :meth:`assert_panel_data_state` enforces exactly one branch.
  * Only verified data-testid locators are used, and shared locators
    (empty-state, list cards) are scoped to the relevant panel/widget.

Like My Requests, MediTik renders every tab panel simultaneously (swipeable
carousel), so tab SELECTION — not panel visibility — is the authoritative
active-category signal. See :meth:`assert_only_panel_active`.

Everything is parameterized by a category key so one set of helpers serves
every tab — no per-tab duplication, no hardcoded record expectations.
"""

from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import Locator, Page, expect

from refua_tests.pages.automationIds import MeditikIds as Ids
from refua_tests.pages.meditikBasePage import MeditekBasePage


@dataclass(frozen=True)
class AppointmentTab:
    """One appointment category: tab testid, panel testid, Hebrew label.

    ``card_prefix`` is set only for categories whose cards carry an indexed
    data-testid in the mapping (Past Appointments). Categories without one are
    validated through their scoped empty state / panel content instead.
    """

    key: str
    tab_test_id: str
    panel_test_id: str
    label: str
    card_prefix: str = ""


# Category registry — iterate this instead of repeating tab logic per test.
APPOINTMENT_TABS: dict[str, AppointmentTab] = {
    "upcoming": AppointmentTab(
        key="upcoming",
        tab_test_id=Ids.MY_APPOINTMENTS_TAB_UPCOMING,
        panel_test_id=Ids.MY_APPOINTMENTS_PANEL_UPCOMING,
        label="תורים עתידיים",
    ),
    "waiting_lists": AppointmentTab(
        key="waiting_lists",
        tab_test_id=Ids.MY_APPOINTMENTS_TAB_WAITING_LISTS,
        panel_test_id=Ids.MY_APPOINTMENTS_PANEL_WAITING_LISTS,
        label="רשימות המתנה",
    ),
    "past": AppointmentTab(
        key="past",
        tab_test_id=Ids.MY_APPOINTMENTS_TAB_PAST,
        panel_test_id=Ids.MY_APPOINTMENTS_PANEL_PAST,
        label="תורים שעברו",
        card_prefix=Ids.MY_APPOINTMENTS_PAST_CARD_PREFIX,
    ),
}

# Upcoming Appointments is the documented default context (APPT-006).
DEFAULT_TAB_KEY = "upcoming"


@dataclass(frozen=True)
class PanelDataState:
    """Result of inspecting one panel's data-state branch."""

    has_records: bool
    record_count: int
    empty_state_visible: bool


class MyAppointmentsTabbedPage(MeditekBasePage):
    """Tabbed My Appointments screen: Upcoming / Waiting Lists / Past."""

    PATH = Ids.MY_APPOINTMENTS_PATH

    def __init__(self, page: Page):
        super().__init__(page)
        # Page-level markers.
        self.page_root = page.get_by_test_id(Ids.MY_APPOINTMENTS_PAGE)
        self.tabs_header = page.get_by_test_id(Ids.MY_APPOINTMENTS_TABS_HEADER)
        self.navbar_toolbar = page.get_by_test_id(Ids.MY_REQUESTS_NAVBAR_TOOLBAR)
        self.navbar_logo = page.get_by_test_id(Ids.MY_REQUESTS_NAVBAR_BTN_LOGO)
        self.navbar_hamburger = page.get_by_test_id(
            Ids.MY_REQUESTS_NAVBAR_BTN_HAMBURGER
        )
        self.navbar_tabs_portal = page.get_by_test_id(Ids.MY_REQUESTS_NAVBAR_TABS_PORTAL)
        self.home_page_marker = page.get_by_test_id(Ids.HOME_PAGE)
        # Booking entry + filter.
        self.book_appointment_link = page.get_by_test_id(Ids.MY_APPOINTMENTS_LINK_BOOK)
        self.filter_open_button = page.get_by_test_id(
            Ids.MY_APPOINTMENTS_FILTER_BTN_OPEN
        )
        self.filter_label = page.get_by_test_id(Ids.MY_APPOINTMENTS_FILTER_LABEL)
        # Speed dial.
        self.speed_dial_fab = page.get_by_test_id(Ids.MY_REQUESTS_SPEED_DIAL_FAB)
        self.speed_dial_trigger = page.get_by_test_id(
            Ids.MY_REQUESTS_SPEED_DIAL_TRIGGER
        )
        # Home future-appointments widget.
        self.home_widget = page.get_by_test_id(Ids.MY_APPOINTMENTS_HOME_BTN_WIDGET)
        self.home_widget_arrow = page.get_by_test_id(
            Ids.MY_APPOINTMENTS_HOME_WIDGET_ARROW
        )
        self.widget_empty_state = page.get_by_test_id(
            Ids.MY_APPOINTMENTS_WIDGET_EMPTY_STATE
        )

    # ------------------------------------------------------------------ #
    # Navigation
    # ------------------------------------------------------------------ #
    def open_direct(self, timeout: int = 60000):
        """Navigate straight to /zimun-torim (clean-context entry)."""
        base = self.env_manager.get_base_url().rstrip("/")
        target = base.replace("/home", "") + self.PATH
        self.page.goto(target, wait_until="domcontentloaded", timeout=timeout)
        self.dismiss_blocking_dialogs()
        return self

    def open_from_home_widget(self, timeout: int = 60000):
        """Activate the Home future-appointments widget (arrow when present)."""
        expect(self.home_widget.first).to_be_visible(timeout=timeout)
        arrow = self.home_widget_arrow
        target = arrow.first if arrow.count() > 0 else self.home_widget.first
        target.click(force=True)
        self.wait_for_loading_done()
        self.dismiss_blocking_dialogs()
        return self

    def wait_until_loaded(self, timeout: int = 60000):
        """Page-ready: URL is /zimun-torim and the page root + tabs are up."""
        self.page.wait_for_url(f"**{self.PATH}**", timeout=timeout)
        self.dismiss_blocking_dialogs()
        expect(self.page_root.or_(self.tabs_header).first).to_be_visible(
            timeout=timeout
        )
        assert self.PATH in self.page.url, (
            f"Expected URL to contain {self.PATH}, got {self.page.url}"
        )
        self.assert_no_app_error(context="My Appointments")
        self.wait_for_loading_done(timeout=timeout)
        return self

    def assert_page_shell(self, timeout: int = 30000):
        """Page root, toolbar, navigation controls and tab header are visible."""
        for marker in (
            self.page_root,
            self.navbar_toolbar,
            self.navbar_hamburger,
            self.navbar_logo,
            self.tabs_header,
        ):
            expect(marker.first).to_be_visible(timeout=timeout)
        # Correct scoping: the page-level shell markers resolve to one node.
        for unique, name in (
            (self.page_root, Ids.MY_APPOINTMENTS_PAGE),
            (self.navbar_toolbar, Ids.MY_REQUESTS_NAVBAR_TOOLBAR),
            (self.tabs_header, Ids.MY_APPOINTMENTS_TABS_HEADER),
        ):
            assert unique.count() == 1, (
                f"Expected exactly one {name}; found {unique.count()}"
            )
        self.assert_no_app_error(context="My Appointments shell")
        return self

    # ------------------------------------------------------------------ #
    # Tabs
    # ------------------------------------------------------------------ #
    def resolve_tab(self, tab_key: str) -> AppointmentTab:
        tab = APPOINTMENT_TABS.get(tab_key)
        assert tab is not None, f"Unknown appointment tab key: {tab_key!r}"
        return tab

    def tab_locator(self, tab_key: str) -> Locator:
        return self.page.get_by_test_id(self.resolve_tab(tab_key).tab_test_id)

    def panel_locator(self, tab_key: str) -> Locator:
        return self.page.get_by_test_id(self.resolve_tab(tab_key).panel_test_id)

    def activate_tab(self, tab_key: str, timeout: int = 30000):
        """Click a category tab and wait for its panel to become visible."""
        tab = self.resolve_tab(tab_key)
        tab_el = self.page.get_by_test_id(tab.tab_test_id)
        expect(tab_el.first).to_be_visible(timeout=timeout)
        tab_el.first.click()
        expect(self.page.get_by_test_id(tab.panel_test_id).first).to_be_visible(
            timeout=timeout
        )
        self.wait_for_loading_done(timeout=timeout)
        self.assert_no_app_error(context=f"My Appointments / {tab.key}")
        return self

    def assert_tab_selected(self, tab_key: str, timeout: int = 15000):
        """The tab for tab_key is selected and its siblings are not."""
        expect(self.tab_locator(tab_key).first).to_have_attribute(
            "aria-selected", "true", timeout=timeout
        )
        for key in APPOINTMENT_TABS:
            if key == tab_key:
                continue
            other = self.tab_locator(key)
            if other.count() > 0:
                expect(other.first).to_have_attribute(
                    "aria-selected", "false", timeout=timeout
                )
        return self

    def assert_only_panel_active(self, tab_key: str):
        """Assert tab_key is the single active category.

        MediTik keeps every ``meditik-tabs-panel-*`` mounted and visible
        simultaneously (swipeable carousel — verified live on the My Requests
        screen, same tab component). Panel visibility therefore cannot
        distinguish active from inactive; the authoritative signal is the tab's
        ``aria-selected``. So: target panel present + target tab selected +
        every sibling tab unselected.
        """
        expect(self.panel_locator(tab_key).first).to_be_visible()
        self.assert_tab_selected(tab_key)
        return self

    def rapid_switch(self, sequence: list[str], timeout: int = 30000):
        """Click tabs back-to-back; only the final tab's outcome is verified."""
        for tab_key in sequence:
            self.tab_locator(tab_key).first.click()
        final_key = sequence[-1]
        expect(self.panel_locator(final_key).first).to_be_visible(timeout=timeout)
        self.wait_for_loading_done(timeout=timeout)
        self.assert_only_panel_active(final_key)
        self.assert_panel_data_state(final_key, timeout=timeout)
        return self

    def assert_all_categories_valid(self, timeout: int = 20000):
        """Activate every appointment category and validate its branch."""
        for tab_key in APPOINTMENT_TABS:
            self.activate_tab(tab_key, timeout=timeout)
            self.assert_panel_data_state(tab_key, timeout=timeout)
        return self

    def assert_hebrew_rtl_rendering(self, timeout: int = 20000):
        """The document flows RTL and each panel renders a valid branch."""
        doc_dir = self.page.evaluate(
            "() => document.documentElement.dir"
            " || getComputedStyle(document.documentElement).direction"
        )
        assert doc_dir == "rtl", f"Expected RTL document direction, got {doc_dir!r}"
        for tab_key in APPOINTMENT_TABS:
            self.activate_tab(tab_key, timeout=timeout)
            self.assert_panel_data_state(tab_key, timeout=timeout)
        return self

    # ------------------------------------------------------------------ #
    # Data-agnostic panel content
    # ------------------------------------------------------------------ #
    def _scoped_cards(self, tab_key: str) -> Locator | None:
        """Indexed cards scoped to the panel, or None when the category has none."""
        tab = self.resolve_tab(tab_key)
        if not tab.card_prefix:
            return None
        panel = self.panel_locator(tab_key).first
        return panel.locator(f'[data-testid^="{tab.card_prefix}"]')

    def _scoped_empty_state(self, tab_key: str) -> Locator:
        """Empty-state title scoped to the panel (shared component)."""
        panel = self.panel_locator(tab_key).first
        return panel.get_by_test_id(Ids.MY_REQUESTS_EMPTY_STATE_TITLE)

    def inspect_panel(self, tab_key: str, timeout: int = 15000) -> PanelDataState:
        """Detect which single data-state branch a panel is in — no seeding."""
        panel = self.panel_locator(tab_key).first
        expect(panel).to_be_visible(timeout=timeout)
        self.wait_for_loading_done(timeout=timeout)

        cards = self._scoped_cards(tab_key)
        empty_title = self._scoped_empty_state(tab_key)

        card_count = cards.count() if cards is not None else 0
        empty_visible = empty_title.count() > 0 and empty_title.first.is_visible()
        return PanelDataState(
            has_records=card_count > 0,
            record_count=card_count,
            empty_state_visible=empty_visible,
        )

    def card_testids(self, tab_key: str) -> list[str | None]:
        """Every scoped card's data-testid, for uniqueness assertions."""
        cards = self._scoped_cards(tab_key)
        if cards is None:
            return []
        return [cards.nth(i).get_attribute("data-testid") for i in range(cards.count())]

    def assert_panel_data_state(
        self, tab_key: str, timeout: int = 15000
    ) -> PanelDataState:
        """Validate exactly ONE valid branch (records XOR scoped empty state).

        Populated branch: every scoped card has a unique data-testid and
        non-empty content, and the scoped empty state is absent.
        Empty branch: the scoped empty-state marker is visible and no stale
        cards remain.

        For a category with no indexed card locator in the mapping (Upcoming,
        Waiting Lists) the populated branch is proven by non-empty panel
        content instead of card testids — the workbook grounds indexed cards
        only for Past Appointments.
        """
        state = self.inspect_panel(tab_key, timeout=timeout)
        cards = self._scoped_cards(tab_key)

        if state.has_records and cards is not None:
            testids = self.card_testids(tab_key)
            assert len(testids) == len(set(testids)), (
                f"Duplicate appointment-card data-testid values in {tab_key} "
                f"panel: {testids!r}"
            )
            expect(cards.first).to_be_visible(timeout=timeout)
            first_text = (cards.first.inner_text(timeout=5000) or "").strip()
            assert first_text and first_text.lower() != "null", (
                f"{tab_key} panel: first card empty/null content: {first_text!r}"
            )
            assert not state.empty_state_visible, (
                f"{tab_key} panel: records AND empty state both active"
            )
            return state

        if state.empty_state_visible:
            # Empty branch: no stale indexed cards may remain.
            assert not state.has_records, (
                f"{tab_key} panel: empty state visible while cards are rendered"
            )
            return state

        # No scoped empty state and no indexed cards: valid only when the panel
        # itself renders content (categories without an indexed card locator).
        panel_text = (
            self.panel_locator(tab_key).first.inner_text(timeout=5000) or ""
        ).strip()
        assert panel_text, (
            f"{tab_key} panel: no records, no scoped empty state and no panel "
            f"content — the category did not load"
        )
        return state

    def assert_widget_data_state(self, timeout: int = 20000):
        """Home widget: populated content XOR the scoped widget empty state."""
        expect(self.home_widget.first).to_be_visible(timeout=timeout)
        empty_visible = (
            self.widget_empty_state.count() > 0
            and self.widget_empty_state.first.is_visible()
        )
        if empty_visible:
            extra = self.page.get_by_test_id(
                Ids.MY_APPOINTMENTS_WIDGET_EMPTY_STATE_EXTRA_INFO
            )
            if extra.count() > 0:
                expect(extra.first).to_be_visible(timeout=timeout)
        else:
            widget_text = (
                self.home_widget.first.inner_text(timeout=5000) or ""
            ).strip()
            assert widget_text, (
                "Future-appointments widget: no empty state and no visible content"
            )
        return self

    # ------------------------------------------------------------------ #
    # Scoped empty state / shared-locator scoping
    # Used by the Appointment Scheduling workbook (APPOINTMENTS-011/012/014),
    # which specs this same screen with explicit empty-state coverage.
    # ------------------------------------------------------------------ #
    def scoped_empty_title(self, tab_key: str) -> Locator:
        panel = self.panel_locator(tab_key).first
        return panel.get_by_test_id(Ids.MY_REQUESTS_EMPTY_STATE_TITLE)

    def scoped_empty_icon(self, tab_key: str) -> Locator:
        panel = self.panel_locator(tab_key).first
        return panel.get_by_test_id(Ids.MY_REQUESTS_EMPTY_STATE_ICON)

    def assert_scoped_empty_state(
        self, tab_key: str, *, require_icon: bool = True, timeout: int = 15000
    ):
        """Validate the empty state SCOPED to this panel, uniquely.

        The empty-state testids are shared across panels, so the scoped locator
        must resolve to exactly one match (APPOINTMENTS-014).
        """
        checks = [(self.scoped_empty_title(tab_key), Ids.MY_REQUESTS_EMPTY_STATE_TITLE)]
        if require_icon:
            checks.append(
                (self.scoped_empty_icon(tab_key), Ids.MY_REQUESTS_EMPTY_STATE_ICON)
            )
        for locator, name in checks:
            assert locator.count() == 1, (
                f"{tab_key} panel: expected exactly one scoped {name}; "
                f"found {locator.count()}"
            )
            expect(locator.first).to_be_visible(timeout=timeout)

        title_text = (
            self.scoped_empty_title(tab_key).first.inner_text(timeout=5000) or ""
        ).strip()
        assert title_text, f"{tab_key} panel: empty-state title is blank"
        return self

    def assert_shared_empty_state_scoping(
        self, tab_keys: list[str], timeout: int = 20000
    ):
        """APPOINTMENTS-014: the shared title locator scopes to one match each.

        Switches between the given categories and asserts that, whenever the
        shared empty-state title is present in the active panel, the panel-scoped
        locator resolves to exactly one element — never to a sibling panel's copy.
        """
        for tab_key in tab_keys:
            self.activate_tab(tab_key, timeout=timeout)
            title = self.scoped_empty_title(tab_key)
            if title.count() > 0:
                assert title.count() == 1, (
                    f"{tab_key} panel: shared empty-state title must scope to one "
                    f"match, found {title.count()}"
                )
        return self

    # ------------------------------------------------------------------ #
    # Past Appointments panel controls (APPOINTMENTS-004/017)
    # ------------------------------------------------------------------ #
    def past_card(self, index: int = 0) -> Locator:
        """A specific indexed past-appointment card, scoped to its panel."""
        panel = self.panel_locator("past").first
        return panel.get_by_test_id(
            Ids.MY_APPOINTMENTS_PAST_CARD_TEMPLATE.format(index=index)
        )

    def past_card_extra_info(self, index: int = 0) -> Locator:
        """The location/extra-info card bound to a given past-appointment card."""
        panel = self.panel_locator("past").first
        return panel.get_by_test_id(
            Ids.MY_APPOINTMENTS_PAST_CARD_EXTRA_INFO_TEMPLATE.format(index=index)
        )

    def assert_past_panel_controls(self, timeout: int = 20000):
        """APPOINTMENTS-004: filter control and booking link are available."""
        panel = self.panel_locator("past").first
        expect(panel).to_be_visible(timeout=timeout)
        for locator, name in (
            (self.filter_open_button, Ids.MY_APPOINTMENTS_FILTER_BTN_OPEN),
            (self.book_appointment_link, Ids.MY_APPOINTMENTS_LINK_BOOK),
        ):
            assert locator.count() > 0, (
                f"Past Appointments: required control {name} is absent"
            )
            expect(locator.first).to_be_visible(timeout=timeout)
        return self

    def assert_past_card_with_location(self, index: int = 0, timeout: int = 20000):
        """APPOINTMENTS-004: the card and its location/extra-info both render."""
        card = self.past_card(index)
        assert card.count() == 1, (
            f"Past Appointments: expected exactly one card at index {index}; "
            f"found {card.count()}"
        )
        expect(card.first).to_be_visible(timeout=timeout)
        card_text = (card.first.inner_text(timeout=5000) or "").strip()
        assert card_text and card_text.lower() != "null", (
            f"Past Appointments card {index}: empty/null content: {card_text!r}"
        )

        extra = self.past_card_extra_info(index)
        assert extra.count() == 1, (
            f"Past Appointments: expected exactly one extra-info card for index "
            f"{index}; found {extra.count()}"
        )
        expect(extra.first).to_be_visible(timeout=timeout)
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
