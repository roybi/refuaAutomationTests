"""Meditik my-requests (הבקשות שלי) — data-testid mapping."""

from playwright.sync_api import Page, expect

from refua_tests.pages.automationIds import MeditikIds as Ids
from refua_tests.pages.meditikContentPage import MeditekContentPage


class MyRequestsPage(MeditekContentPage):
    """Page elements + assertions for /user-requests."""

    PAGE_TITLE = "הבקשות שלי"
    PATH = "/user-requests"
    PAGE_TEST_ID = Ids.USER_REQUESTS_PAGE
    ROW_PREFIX = Ids.USER_REQUESTS_ROW_PREFIX
    EMPTY_MARKERS = (
        "בקשות מהמרפאה יופיעו כאן",
        "יופיעו כאן",
    )

    # Action shortcuts from mapping (sanity: at least page root + optional rows)
    ACTION_BUTTON_IDS = (
        Ids.USER_REQUESTS_BTN_PRESCRIPTION,
        Ids.USER_REQUESTS_BTN_REFERRAL,
        Ids.USER_REQUESTS_BTN_SICK_DAYS,
        Ids.USER_REQUESTS_BTN_GLASSES,
        Ids.USER_REQUESTS_BTN_DENTIST,
        Ids.USER_REQUESTS_BTN_INSOLES,
        Ids.USER_REQUESTS_BTN_REFERRAL_ANSWERS,
        Ids.USER_REQUESTS_BTN_RETROACTIVE,
    )

    def __init__(self, page: Page):
        super().__init__(page)
        self.action_buttons = {
            tid: page.get_by_test_id(tid) for tid in self.ACTION_BUTTON_IDS
        }

    def assert_content_loaded(self):
        expect(self.page_marker()).to_be_visible()
        assert self.PATH in self.page.url
        self.assert_no_app_error(context=self.PAGE_TITLE)
        assert self.loading_spinner.count() == 0 or not self.loading_spinner.first.is_visible(), (
            "הבקשות שלי: still shows a loading spinner"
        )

        body = self._body_text(timeout=15000)
        if any(marker in body for marker in self.EMPTY_MARKERS):
            return

        rows = self.rows_by_prefix(self.ROW_PREFIX)
        if rows.count() > 0:
            expect(rows.first).to_be_visible(timeout=10000)
            row_text = (rows.first.inner_text(timeout=5000) or "").strip()
            assert row_text and row_text.lower() != "null", (
                f"הבקשות שלי: first row empty/null: {row_text!r}"
            )
            return

        cards = self.page.locator("[id$='-card-title']")
        if cards.count() > 0:
            expect(cards.first).to_be_visible(timeout=10000)
            return

        for btn in self.action_buttons.values():
            try:
                if btn.count() > 0 and btn.first.is_visible():
                    return
            except Exception:
                continue

        assert False, (
            f"הבקשות שלי: no rows/actions/empty-state found (body): {body[:300]!r}"
        )
