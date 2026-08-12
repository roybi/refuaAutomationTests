"""Meditik all-actions hub — data-testid mapping."""

from playwright.sync_api import expect

from refua_tests.pages.automationIds import MeditikIds as Ids
from refua_tests.pages.meditikContentPage import MeditekContentPage


class AllActionsPage(MeditekContentPage):
    PAGE_TITLE = "כל הפעולות"
    PATH = "/all-actions"
    PAGE_TEST_ID = Ids.ALL_ACTIONS_PAGE

    # Live tile labels on /all-actions (Hebrew copy can change — match current UI).
    EXPECTED_ACTIONS = (
        "זימון תור",
        "שיננית עד הבית",
        "שינוי בהפניה קיימת",
        "הפניה חדשה",
        "קבלת מרשם",
        "החזרת תשובה להפניה",  # substring of longer combined label
        "אישור ימי מחלה",
        "אסמכתא",  # substring of בקשת אסמכתא למיון
        "שובר למדרסים",  # substring of קבלת שובר למדרסים
        "החזר כספי",
        "רפואה דחופה",
    )

    def wait_until_loaded(self, timeout: int = 60000):
        super().wait_until_loaded(timeout=timeout)
        # Below-the-fold tiles
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_timeout(300)
        self.page.evaluate("window.scrollTo(0, 0)")
        return self

    def assert_all_objects_loaded(self):
        self.dismiss_blocking_dialogs()
        expect(self.page_marker()).to_be_visible()
        assert self.PATH in self.page.url
        self.assert_no_app_error(context=self.PAGE_TITLE)
        assert self.loading_spinner.count() == 0 or not self.loading_spinner.first.is_visible(), (
            "כל הפעולות still shows a loading spinner"
        )

        body_text = self.page.locator("body").inner_text(timeout=15000) or ""
        missing = []
        for label in self.EXPECTED_ACTIONS:
            tile = self.page.locator("button").filter(has_text=label).first
            found = False
            try:
                if tile.count() > 0:
                    tile.scroll_into_view_if_needed(timeout=5000)
                    expect(tile).to_be_visible(timeout=5000)
                    found = True
            except Exception:
                found = False
            if not found and label not in body_text:
                missing.append(label)

        assert not missing, (
            "Not all page objects loaded on כל הפעולות. Missing: " + ", ".join(missing)
        )

    def run_menu_sanity(self, menu_label: str | None = None, *, session_ready: bool = False):
        """Menu → כל הפעולות tile sanity (uses tile assert, not generic content)."""
        if not session_ready:
            self.open_home()
            self.ensure_logged_in()
        self.go_to_all_actions()
        self.wait_until_loaded()
        self.assert_all_objects_loaded()
