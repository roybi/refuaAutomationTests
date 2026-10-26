"""Meditik home (דף הבית) — widgets and CTAs."""

from __future__ import annotations

import re

from playwright.sync_api import Page, expect

from refua_tests.pages.automationIds import MeditikIds as Ids
from refua_tests.pages.meditikBasePage import MeditekBasePage
from refua_tests.pages.softNotes import report_soft_note
from refua_tests.pages.speedDial import SpeedDial


class MeditekHomePage(MeditekBasePage):
    """Sanity helpers for /home widgets and primary CTAs."""

    PATH = "/home"
    LAST_UPDATE_LABEL = "זמן עדכון אחרון"
    LAST_UPDATE_STAMP_RE = re.compile(
        r"עודכן ב-\d{2}\.\d{2}\.\d{2}\s*\|\s*\d{1,2}:\d{2}"
    )

    # Widgets currently present on test (data-testid = hard existence).
    WIDGETS: dict[str, tuple[str, str]] = {
        # testid -> (expected soft label snippet, expected URL path after click)
        Ids.HOME_BTN_USER_REQUESTS_WIDGET: ("הבקשות שלי", "/user-requests"),
        Ids.HOME_BTN_FUTURE_APPOINTMENTS_WIDGET: ("התורים שלי", "/zimun-torim"),
        Ids.HOME_BTN_REFERRALS_WIDGET: ("הפניות", "/referrals"),
        Ids.HOME_BTN_MEDICINES_WIDGET: ("תרופות ומרשמים", "/medicines"),
        Ids.HOME_BTN_EXEMPTIONS_WIDGET: ("פטורים", "/exemptions"),
    }

    HOME_SPEED_DIAL_ACTIONS = (
        Ids.SPEED_DIAL_NEW_REFERRAL,
        Ids.SPEED_DIAL_PRESCRIPTION,
        Ids.SPEED_DIAL_REFERRAL_ANSWER,
        Ids.SPEED_DIAL_BARHAN,
        Ids.SPEED_DIAL_MOKED,
    )

    def __init__(self, page: Page):
        super().__init__(page)
        self.page_root = page.get_by_test_id(Ids.HOME_PAGE)
        self.speed_dial = SpeedDial(page)
        self.send_doctor_request_cta = page.get_by_text("שליחת בקשה לרופא", exact=False).first
        self.book_appointment_cta = page.get_by_text("לזימון תורים", exact=False).first
        self.last_update_link = page.locator("p.MuiTypography-root").filter(
            has_text=self.LAST_UPDATE_LABEL
        ).first
        self.last_update_row = page.locator('img[src*="version.svg"]').locator(
            'xpath=ancestor::div[contains(@class,"MuiStack-root")][1]'
        )

    def wait_until_loaded(self, timeout: int = 60000):
        self.page.wait_for_url(f"**{self.PATH}**", timeout=timeout)
        self.dismiss_blocking_dialogs()
        expect(self.page_root.or_(self.dashboard_marker).first).to_be_visible(timeout=timeout)
        self.assert_no_app_error(context="home")
        return self

    def assert_widgets_present(self):
        """Each home widget testid is visible; label mismatch = soft note."""
        self.wait_until_loaded()
        missing = []
        for tid, (label, _path) in self.WIDGETS.items():
            widget = self.page.get_by_test_id(tid)
            try:
                expect(widget.first).to_be_visible(timeout=15000)
            except Exception:
                missing.append(tid)
                continue
            try:
                text = (widget.first.inner_text(timeout=3000) or "").strip()
            except Exception:
                text = ""
            if label not in text:
                report_soft_note(
                    f"Home widget label mismatch for {tid}: "
                    f"expected text containing {label!r}, got {text[:80]!r}."
                )
        assert not missing, "Home widgets missing: " + ", ".join(missing)
        return self

    def open_widget(self, test_id: str):
        widget = self.page.get_by_test_id(test_id).first
        expect(widget).to_be_visible(timeout=15000)
        widget.click(force=True)
        self.wait_for_loading_done()
        self.dismiss_blocking_dialogs()
        return self

    def assert_widget_navigates(self, test_id: str):
        _label, expected_path = self.WIDGETS[test_id]
        self.open_widget(test_id)
        self.page.wait_for_url(f"**{expected_path}**", timeout=60000)
        assert expected_path in self.page.url, (
            f"Widget {test_id}: expected URL containing {expected_path}, got {self.page.url}"
        )
        self.assert_no_app_error(context=test_id)
        return self

    def assert_send_doctor_request_cta(self):
        """CTA on home → /all-actions."""
        self.wait_until_loaded()
        expect(self.send_doctor_request_cta).to_be_visible(timeout=15000)
        self.send_doctor_request_cta.click()
        self.page.wait_for_url("**/all-actions**", timeout=60000)
        assert "/all-actions" in self.page.url
        self.assert_no_app_error(context="שליחת בקשה לרופא")
        return self

    def assert_speed_dial_actions(self):
        self.wait_until_loaded()
        assert self.speed_dial.is_present(), "Speed dial FAB not present on home"
        self.speed_dial.assert_actions_present(self.HOME_SPEED_DIAL_ACTIONS)
        self.speed_dial.close()
        return self

    def assert_last_update_time(self, timeout: int = 45000):
        """Click זמן עדכון אחרון and assert the stamp (עודכן ב-…) appears."""
        self.wait_until_loaded()
        self.close_menu()
        self.page.keyboard.press("Escape")
        expect(self.last_update_link).to_be_visible(timeout=15000)
        expect(self.last_update_row).to_be_visible(timeout=15000)

        self.last_update_link.scroll_into_view_if_needed(timeout=5000)
        self.last_update_link.click()

        # Click shows a skeleton while POST /api/medical-center runs.
        skeleton = self.last_update_row.locator(".MuiSkeleton-root")
        try:
            skeleton.first.wait_for(state="attached", timeout=5000)
        except Exception:
            pass
        try:
            expect(skeleton).to_have_count(0, timeout=timeout)
        except Exception:
            pass

        row_text = ""
        polled = 0
        while polled < timeout:
            row_text = (self.last_update_row.inner_text(timeout=3000) or "").strip()
            row_text = " ".join(row_text.split())
            if self.LAST_UPDATE_STAMP_RE.search(row_text):
                break
            if "אירעה שגיאה בטעינת הנתונים" in row_text:
                break
            self.page.wait_for_timeout(1000)
            polled += 1000

        assert "אירעה שגיאה בטעינת הנתונים" not in row_text, (
            f"Last-update click loaded an error instead of a stamp. Got: {row_text!r}"
        )
        match = self.LAST_UPDATE_STAMP_RE.search(row_text)
        assert match, (
            f"Expected last-update stamp like 'עודכן ב-DD.MM.YY | HH:MM' after click. "
            f"Got: {row_text!r}"
        )
        if self.LAST_UPDATE_LABEL not in row_text:
            report_soft_note(
                f"Last-update label missing after click (stamp OK): {row_text!r}"
            )
        return self
