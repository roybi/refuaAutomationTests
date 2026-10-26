"""Shared Meditik content-page sanity helpers using data-testid mapping.

During rollout: prefer data-testid; fall back to Hebrew title/tabs when ids
are not yet present on the environment.
"""

from playwright.sync_api import Page, expect

from refua_tests.pages.meditikBasePage import MeditekBasePage
from refua_tests.pages.softNotes import report_soft_note


class MeditekContentPage(MeditekBasePage):
    """Base for in-app Meditik screens opened from the side menu.

    Subclasses set:
      PAGE_TITLE, PATH
      optional PAGE_TEST_ID
      optional TAB_TEST_IDS / TAB_LABELS (Hebrew fallback)
      optional ROW_PREFIX
      optional EMPTY_MARKERS

    data-testid / URL = hard existence checks.
    Hebrew titles/labels = soft notes in Allure when they differ.
    """

    PAGE_TITLE: str = ""
    PATH: str = ""
    PAGE_TEST_ID: str = ""
    TAB_TEST_IDS: tuple[str, ...] = ()
    TAB_LABELS: tuple[str, ...] = ()
    ROW_PREFIX: str = ""
    EMPTY_MARKERS: tuple[str, ...] = ()

    def __init__(self, page: Page):
        super().__init__(page)
        self.page_root = (
            page.get_by_test_id(self.PAGE_TEST_ID) if self.PAGE_TEST_ID else None
        )
        self.heading = page.get_by_text(self.PAGE_TITLE, exact=True).first
        self.toolbar_title = self.main_toolbar.get_by_text(self.PAGE_TITLE).first

    def page_marker(self):
        """Visible marker that the target screen is open.

        Prefer page data-testid when present; fall back to title/toolbar.
        """
        if self.page_root is not None:
            return self.page_root.or_(self.heading).or_(self.toolbar_title).first
        return self.heading.or_(self.toolbar_title).first

    def _soft_check_page_title(self):
        if not self.PAGE_TITLE:
            return
        try:
            body = self._body_text(timeout=5000)
        except Exception:
            body = ""
        if self.PAGE_TITLE not in body:
            report_soft_note(
                f"Page title mismatch on {self.PATH} "
                f"(testid={self.PAGE_TEST_ID or 'n/a'}): "
                f"expected text containing {self.PAGE_TITLE!r}. "
                f"Continuing by data-testid/URL."
            )

    def tab_by_id(self, test_id: str):
        return self.page.get_by_test_id(test_id)

    def tab_by_label(self, label: str):
        return self.page.get_by_role("tab", name=label, exact=True)

    def _testid_tabs_available(self) -> bool:
        return any(
            self.page.get_by_test_id(tid).count() > 0 for tid in self.TAB_TEST_IDS
        )

    def _label_tabs_available(self) -> bool:
        return any(self.tab_by_label(name).count() > 0 for name in self.TAB_LABELS)

    def wait_until_loaded(self, timeout: int = 60000):
        self.page.wait_for_url(f"**{self.PATH}**", timeout=timeout)
        self.dismiss_blocking_dialogs()
        expect(self.page_marker()).to_be_visible(timeout=timeout)
        assert self.PATH in self.page.url, (
            f"Expected URL to contain {self.PATH}, got {self.page.url}"
        )
        self._soft_check_page_title()
        self.assert_no_app_error(context=self.PAGE_TITLE or self.PATH)

        if self.TAB_TEST_IDS and self._testid_tabs_available():
            for tab_id in self.TAB_TEST_IDS:
                expect(self.tab_by_id(tab_id)).to_be_visible(timeout=timeout)
        elif self.TAB_LABELS and self._label_tabs_available():
            for name in self.TAB_LABELS:
                expect(self.tab_by_label(name)).to_be_visible(timeout=timeout)

        self.wait_for_loading_done(timeout=timeout)
        loaders = self.page.locator("[id$='-loader'], [id*='list-loader']")
        try:
            if loaders.count() > 0:
                expect(loaders.first).to_be_hidden(timeout=timeout)
        except Exception:
            pass
        self.assert_no_app_error(context=self.PAGE_TITLE or self.PATH)
        return self

    def open_sub_page_by_testid(self, tab_test_id: str, timeout: int = 30000):
        target = self.tab_by_id(tab_test_id)
        expect(target).to_be_visible(timeout=timeout)
        target.click()
        expect(target).to_have_attribute("aria-selected", "true", timeout=timeout)
        self.wait_for_loading_done(timeout=timeout)
        self.assert_no_app_error(context=f"{self.PAGE_TITLE}/{tab_test_id}")
        return self

    def open_sub_page_by_label(self, tab_name: str, timeout: int = 30000):
        target = self.tab_by_label(tab_name)
        expect(target).to_be_visible(timeout=timeout)
        target.click()
        expect(target).to_have_attribute("aria-selected", "true", timeout=timeout)
        self.wait_for_loading_done(timeout=timeout)
        self.assert_no_app_error(context=f"{self.PAGE_TITLE}/{tab_name}")
        return self

    def assert_content_loaded(self):
        expect(self.page_marker()).to_be_visible()
        assert self.PATH in self.page.url
        assert self.loading_spinner.count() == 0 or not self.loading_spinner.first.is_visible(), (
            f"{self.PAGE_TITLE}: still shows a loading spinner"
        )

        body = self._body_text(timeout=15000)
        self.assert_no_app_error(context=self.PAGE_TITLE or self.PATH)

        if any(marker in body for marker in self.EMPTY_MARKERS):
            return

        if self.ROW_PREFIX:
            rows = self.rows_by_prefix(self.ROW_PREFIX)
            if rows.count() > 0:
                rows.first.scroll_into_view_if_needed(timeout=5000)
                expect(rows.first).to_be_visible(timeout=10000)
                row_text = (rows.first.inner_text(timeout=5000) or "").strip()
                assert row_text and row_text.lower() != "null", (
                    f"{self.PAGE_TITLE}: first row has empty/null content: {row_text!r}"
                )
                return

        # Legacy list cards (pre-row-testid rollout)
        cards = self.page.locator("[id$='-card-title']")
        if cards.count() > 0:
            cards.first.scroll_into_view_if_needed(timeout=5000)
            expect(cards.first).to_be_visible(timeout=10000)
            card_text = (cards.first.inner_text(timeout=5000) or "").strip()
            assert card_text and card_text.lower() != "null", (
                f"{self.PAGE_TITLE}: first card has empty/null content: {card_text!r}"
            )
            return

        # Do NOT pass on speed-dial / page-root / title alone — that hid fault pages.
        assert False, (
            f"{self.PAGE_TITLE}: no list rows/cards and no empty-state — "
            f"content did not load. Body snip: {body[:300]!r}"
        )

    def assert_all_sub_pages_loaded(self):
        self.wait_until_loaded()

        if self.TAB_TEST_IDS and self._testid_tabs_available():
            for tab_id in self.TAB_TEST_IDS:
                self.open_sub_page_by_testid(tab_id)
                self.assert_content_loaded()
            return

        if self.TAB_LABELS and self._label_tabs_available():
            for name in self.TAB_LABELS:
                self.open_sub_page_by_label(name)
                self.assert_content_loaded()
            return

        self.assert_content_loaded()

    def run_menu_sanity(self, menu_label: str, *, session_ready: bool = False):
        """Menu → screen sanity. If session_ready, skip open/login (shared Chrome)."""
        if not session_ready:
            self.open_home()
            self.ensure_logged_in()
        self.navigate_via_menu(menu_label)
        self.assert_all_sub_pages_loaded()
