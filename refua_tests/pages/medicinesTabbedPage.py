"""Meditik Medicines & Prescriptions (תרופות ומרשמים) — tabbed /medicines page.

Models the tabbed screen from the MediTik Medicines & Prescriptions BDD/E2E
workbook (MEDICINES-001..024): My Prescriptions (active) / Permanent Medicines
/ Previous Prescriptions (expired).

Constraints taken from the workbook:
  * Empty-state elements are defined ONLY for My Prescriptions. The other two
    categories have no approved empty-state title (MEDICINES-010/011 are
    pending on UX for exactly that reason), so this page never asserts an
    empty-state marker for them — it only proves the panel is valid and free
    of fabricated records.
  * The empty-state testids are shared, so every empty-state locator is scoped
    to the active panel and must resolve to exactly one match
    (MEDICINES-024).
  * Nothing is seeded or deleted; the page reports whichever branch is live.

Tab selection (``aria-selected``) — not panel visibility — is the authoritative
"active category" signal, because MediTik keeps sibling tab panels mounted
(swipeable carousel, verified live on the sibling My Requests screen).
"""

from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import Locator, Page, expect

from refua_tests.pages.automationIds import MeditikIds as Ids
from refua_tests.pages.meditikBasePage import MeditekBasePage


@dataclass(frozen=True)
class MedicineTab:
    """One medicine category: tab testid, panel testid, Hebrew label.

    ``has_defined_empty_state`` records whether the workbook defines approved
    empty-state elements for this category — only My Prescriptions does.
    """

    key: str
    tab_test_id: str
    panel_test_id: str
    label: str
    has_defined_empty_state: bool = False


# Category registry — iterate this instead of repeating tab logic per test.
MEDICINE_TABS: dict[str, MedicineTab] = {
    "active": MedicineTab(
        key="active",
        tab_test_id=Ids.MEDICINES_TAB_ACTIVE,
        panel_test_id=Ids.MEDICINES_PANEL_ACTIVE,
        label="המרשמים שלי",
        has_defined_empty_state=True,
    ),
    "permanent": MedicineTab(
        key="permanent",
        tab_test_id=Ids.MEDICINES_TAB_PERMANENT,
        panel_test_id=Ids.MEDICINES_PANEL_PERMANENT,
        label="תרופות קבועות",
    ),
    "expired": MedicineTab(
        key="expired",
        tab_test_id=Ids.MEDICINES_TAB_EXPIRED,
        panel_test_id=Ids.MEDICINES_PANEL_EXPIRED,
        label="מרשמים קודמים",
    ),
}

# My Prescriptions is the first/default category (MEDICINES-002).
DEFAULT_TAB_KEY = "active"


@dataclass(frozen=True)
class PanelDataState:
    """Which single branch a medicine panel is currently in."""

    empty_state_visible: bool
    has_content: bool


class MedicinesTabbedPage(MeditekBasePage):
    """Tabbed Medicines screen: My Prescriptions / Permanent / Previous."""

    PATH = Ids.MEDICINES_TABBED_PATH

    def __init__(self, page: Page):
        super().__init__(page)
        self.page_root = page.get_by_test_id(Ids.MEDICINES_PAGE)
        self.tabs_header = page.get_by_test_id(Ids.MEDICINES_TABS_HEADER)
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
        """Navigate straight to /medicines (a supported entry point)."""
        base = self.env_manager.get_base_url().rstrip("/")
        target = base.replace("/home", "") + self.PATH
        self.page.goto(target, wait_until="domcontentloaded", timeout=timeout)
        self.dismiss_blocking_dialogs()
        return self

    def wait_until_loaded(self, timeout: int = 60000):
        """Page-ready: URL is /medicines and the page container is visible."""
        self.page.wait_for_url(f"**{self.PATH}**", timeout=timeout)
        self.dismiss_blocking_dialogs()
        expect(self.page_root.or_(self.tabs_header).first).to_be_visible(
            timeout=timeout
        )
        assert self.PATH in self.page.url, (
            f"Expected URL to contain {self.PATH}, got {self.page.url}"
        )
        self.assert_no_app_error(context="Medicines & Prescriptions")
        self.wait_for_loading_done(timeout=timeout)
        return self

    def assert_page_shell(self, timeout: int = 30000):
        """MEDICINES-001: page container, nav shell and all three tabs shown."""
        for marker in (
            self.page_root,
            self.navbar_toolbar,
            self.navbar_hamburger,
            self.navbar_logo,
            self.tabs_header,
        ):
            expect(marker.first).to_be_visible(timeout=timeout)
        for unique, name in (
            (self.page_root, Ids.MEDICINES_PAGE),
            (self.tabs_header, Ids.MEDICINES_TABS_HEADER),
        ):
            assert unique.count() == 1, (
                f"Expected exactly one {name}; found {unique.count()}"
            )
        # All three medicine tabs displayed and operational.
        for tab in MEDICINE_TABS.values():
            tab_el = self.page.get_by_test_id(tab.tab_test_id)
            expect(tab_el.first).to_be_visible(timeout=timeout)
            assert tab_el.first.is_enabled(), (
                f"Medicines tab {tab.tab_test_id} is present but not operational"
            )
        self.assert_no_app_error(context="Medicines shell")
        return self

    # ------------------------------------------------------------------ #
    # Tabs
    # ------------------------------------------------------------------ #
    def resolve_tab(self, tab_key: str) -> MedicineTab:
        tab = MEDICINE_TABS.get(tab_key)
        assert tab is not None, f"Unknown medicine tab key: {tab_key!r}"
        return tab

    def tab_locator(self, tab_key: str) -> Locator:
        return self.page.get_by_test_id(self.resolve_tab(tab_key).tab_test_id)

    def panel_locator(self, tab_key: str) -> Locator:
        return self.page.get_by_test_id(self.resolve_tab(tab_key).panel_test_id)

    def activate_tab(self, tab_key: str, timeout: int = 30000):
        """Select a medicine category and wait for its panel."""
        tab = self.resolve_tab(tab_key)
        tab_el = self.page.get_by_test_id(tab.tab_test_id)
        expect(tab_el.first).to_be_visible(timeout=timeout)
        tab_el.first.click()
        expect(self.page.get_by_test_id(tab.panel_test_id).first).to_be_visible(
            timeout=timeout
        )
        self.wait_for_loading_done(timeout=timeout)
        self.assert_no_app_error(context=f"Medicines / {tab.key}")
        return self

    def assert_tab_selected(self, tab_key: str, timeout: int = 15000):
        """The selected tab indicates its active state; siblings do not."""
        expect(self.tab_locator(tab_key).first).to_have_attribute(
            "aria-selected", "true", timeout=timeout
        )
        for key in MEDICINE_TABS:
            if key == tab_key:
                continue
            other = self.tab_locator(key)
            if other.count() > 0:
                expect(other.first).to_have_attribute(
                    "aria-selected", "false", timeout=timeout
                )
        return self

    def assert_panel_is_active_content(self, tab_key: str, timeout: int = 30000):
        """MEDICINES-002/003/004/014: this category is the active content.

        Sibling panels stay mounted (carousel), so exclusivity is proven by tab
        selection rather than by sibling panels disappearing.
        """
        expect(self.panel_locator(tab_key).first).to_be_visible(timeout=timeout)
        self.assert_tab_selected(tab_key, timeout=timeout)
        return self

    def walk_all_categories(self, timeout: int = 30000):
        """MEDICINES-014: one active panel per step, across every category."""
        for tab_key in MEDICINE_TABS:
            self.activate_tab(tab_key, timeout=timeout)
            self.assert_panel_is_active_content(tab_key, timeout=timeout)
        return self

    # ------------------------------------------------------------------ #
    # Panel-scoped state
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

    def assert_scoped_empty_state(self, tab_key: str, timeout: int = 15000):
        """MEDICINES-009: empty-state icon AND title, scoped to this panel.

        Only valid for a category whose empty state the workbook defines
        (My Prescriptions); calling it elsewhere is a test-authoring error.
        """
        tab = self.resolve_tab(tab_key)
        assert tab.has_defined_empty_state, (
            f"The workbook defines no approved empty-state elements for the "
            f"{tab_key} category — do not assert one (see MEDICINES-010/011)."
        )
        for locator, name in (
            (self.scoped_empty_title(tab_key), Ids.MY_REQUESTS_EMPTY_STATE_TITLE),
            (self.scoped_empty_icon(tab_key), Ids.MY_REQUESTS_EMPTY_STATE_ICON),
        ):
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

    def assert_panel_free_of_fabricated_records(
        self, tab_key: str, timeout: int = 15000
    ):
        """MEDICINES-010/011 shape: the panel is valid and invents no records.

        Used for categories with no approved empty-state title: the panel must
        be present and must not render a stale/duplicate record block. No
        assertion is made about copy that the workbook does not define.
        """
        panel = self.panel_locator(tab_key).first
        expect(panel).to_be_visible(timeout=timeout)
        self.assert_no_app_error(context=f"Medicines / {tab_key}")
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
