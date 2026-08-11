"""Shared Meditik base page — chrome, login, menu via data-testid mapping."""

from playwright.sync_api import Page, expect
from urllib.parse import urlparse

from refua_core.config.environment import EnvironmentManager
from refua_core.pages.base_page import BasePage

from refua_tests.pages.automation_ids import MeditikIds as Ids
from refua_tests.pages.common.pop_up_info import PopUpInfo
from refua_tests.pages.soft_notes import report_soft_note


class MeditekBasePage(BasePage):
    """Meditik application shell shared across screens."""

    # Expected Hebrew labels (soft-checked; navigation uses data-testid).
    MENU_BOOK_APPOINTMENT = "זימון תור"
    MENU_SEND_DOCTOR_REQUEST = "שליחת בקשה לרופא"
    MENU_URGENT_CARE = "רפואה דחופה"
    MENU_MY_APPOINTMENTS = "התורים שלי"
    MENU_MY_REQUESTS = "הבקשות שלי"
    MENU_LAB_RESULTS = "תוצאות בדיקות"
    MENU_MEDICINES = "תרופות ומרשמים"
    MENU_VISIT_SUMMARIES = "סיכומי ביקור"
    MENU_EXEMPTIONS = "פטורים"
    MENU_SICK_DAYS = "ימי מחלה"
    MENU_REFERRALS = "הפניות"
    MENU_VACCINATIONS = "חיסונים"
    MENU_MEDICAL_PROFILE = "פרופיל רפואי"

    # data-testid is the source of truth for "does this menu entry exist".
    MENU_TEST_IDS: dict[str, str] = {
        MENU_BOOK_APPOINTMENT: Ids.MENU_COMMON_BOOK_APPOINTMENT,
        MENU_SEND_DOCTOR_REQUEST: Ids.MENU_COMMON_SEND_DOCTOR_REQUEST,
        MENU_URGENT_CARE: Ids.MENU_COMMON_URGENT_CARE,
        MENU_MY_APPOINTMENTS: Ids.MENU_ITEM_MY_APPOINTMENTS,
        MENU_MY_REQUESTS: Ids.MENU_ITEM_MY_REQUESTS,
        MENU_LAB_RESULTS: Ids.MENU_ITEM_LAB_RESULTS,
        MENU_MEDICINES: Ids.MENU_ITEM_MEDICINES,
        MENU_VISIT_SUMMARIES: Ids.MENU_ITEM_VISIT_SUMMARIES,
        MENU_EXEMPTIONS: Ids.MENU_ITEM_EXEMPTIONS,
        MENU_SICK_DAYS: Ids.MENU_ITEM_SICK_DAYS,
        MENU_REFERRALS: Ids.MENU_ITEM_REFERRALS,
        MENU_VACCINATIONS: Ids.MENU_ITEM_VACCINATIONS,
        MENU_MEDICAL_PROFILE: Ids.MENU_ITEM_MEDICAL_PROFILE,
    }

    def __init__(self, page: Page):
        super().__init__(page)
        self.env_manager = EnvironmentManager()
        self.popup = PopUpInfo(page)
        # Close PWA overlay whenever it appears (mid-action / any screen).
        PopUpInfo.install_auto_dismiss(page)

        self.menu_button = page.get_by_test_id(Ids.NAVBAR_BTN_HAMBURGER)
        self.close_menu_button = page.get_by_test_id(Ids.NAVBAR_BTN_CLOSE_MENU)
        self.home_menu_button = page.get_by_test_id(Ids.NAVBAR_BTN_HOME)
        self.side_drawer = page.get_by_test_id(Ids.NAVBAR_DRAWER_MENU)
        self.main_toolbar = page.get_by_test_id(Ids.NAVBAR_TOOLBAR)
        self.logout_button = page.get_by_test_id(Ids.NAVBAR_BTN_LOGOUT)
        self.speed_dial = page.get_by_test_id(Ids.SPEED_DIAL_TRIGGER)
        self.home_page_root = page.get_by_test_id(Ids.HOME_PAGE)
        # Login is not in the mapping yet — keep legacy id + Hebrew name.
        self.login_button = page.locator("#login-button").or_(
            page.get_by_role("button", name="התחברות")
        ).first
        # Any of these means "home is up / logged in shell is ready".
        self.dashboard_marker = (
            self.speed_dial.or_(self.home_page_root).or_(
                page.get_by_text("פעולות מהירות").first
            )
        ).first
        self.loading_spinner = page.locator(".MuiCircularProgress-root")
        self.skeleton = page.locator(".MuiSkeleton-root")

    @property
    def home_url(self) -> str:
        return self.env_manager.get_base_url()

    def wait_for_loading_done(self, timeout: int = 60000):
        if self.loading_spinner.count() > 0:
            try:
                self.loading_spinner.first.wait_for(state="visible", timeout=3000)
            except Exception:
                pass
            try:
                expect(self.loading_spinner.first).to_be_hidden(timeout=timeout)
            except Exception:
                pass
        if self.skeleton.count() > 0:
            try:
                expect(self.skeleton.first).to_be_hidden(timeout=timeout)
            except Exception:
                pass
        return self

    def dismiss_blocking_dialogs(self):
        self.popup.dismiss_if_present()
        return self

    def open_home(self):
        self.page.goto(self.home_url, wait_until="domcontentloaded", timeout=60000)
        return self

    # Full-page / content failure messages that must never count as "loaded".
    APP_ERROR_MARKERS = (
        "יש לנו תקלה",
        "מגבלת הבקשות",
        "לא הצלחנו לטעון את הנתונים",
        "אפשר לרענן, או לחזור מאוחר יותר",
        "הגעתם למגבלת הבקשות",
    )

    def _body_text(self, timeout: int = 5000) -> str:
        try:
            return (self.page.locator("body").inner_text(timeout=timeout) or "").strip()
        except Exception:
            return ""

    def _is_app_error_or_rate_limited(self) -> bool:
        body = self._body_text(timeout=3000)
        if "429" in body:
            return True
        return any(marker in body for marker in self.APP_ERROR_MARKERS)

    def assert_no_app_error(self, context: str = ""):
        """Fail the test if Meditik shows a fault / rate-limit / load-error page."""
        body = self._body_text(timeout=8000)
        matched = [m for m in self.APP_ERROR_MARKERS if m in body]
        if "429" in body and "429" not in matched:
            matched.append("429")
        where = f" ({context})" if context else ""
        assert not matched, (
            f"Meditik error page shown{where}: matched {matched!r}. "
            f"Body snip: {body[:350]!r}"
        )
        # Fault shell often exposes רענן without the dashboard chrome we expect.
        refresh = self.page.get_by_role("button", name="רענן")
        try:
            if refresh.is_visible(timeout=800) and (
                "תקלה" in body or "Error image" in body or "רענן" in body
            ):
                # Only treat as hard error when title/error copy is present,
                # not every screen that might reuse a refresh control later.
                if "תקלה" in body or "מגבלת" in body:
                    assert False, (
                        f"Meditik fault/refresh page shown{where}. "
                        f"Body snip: {body[:350]!r}"
                    )
        except AssertionError:
            raise
        except Exception:
            pass
        return self

    def ensure_logged_in(self, timeout: int = 60000):
        """Reach authenticated dashboard (silent MSAL or SSO via התחברות).

        Reloads only on real error / rate-limit pages — not while the home
        screen is still settling.
        """
        ready = self.login_button.or_(self.dashboard_marker).first

        for attempt in range(3):
            self.dismiss_blocking_dialogs()

            if self._is_app_error_or_rate_limited():
                refresh = self.page.get_by_role("button", name="רענן")
                try:
                    if refresh.is_visible(timeout=1500):
                        refresh.click()
                        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
                        continue
                except Exception:
                    pass
                self.page.wait_for_timeout(8000 * (attempt + 1))
                self.page.goto(self.home_url, wait_until="domcontentloaded", timeout=60000)
                continue

            try:
                if ready.is_visible(timeout=8000):
                    break
            except Exception:
                pass

            # Still loading (not an error page) — wait, don't reload.
            try:
                expect(ready).to_be_visible(timeout=timeout)
                break
            except Exception:
                if attempt == 2:
                    raise
                self.page.goto(self.home_url, wait_until="domcontentloaded", timeout=60000)

        expect(ready).to_be_visible(timeout=timeout)
        if self.login_button.is_visible():
            self.dismiss_blocking_dialogs()
            expect(self.login_button).to_be_enabled()
            self.login_button.click()
        expect(self.dashboard_marker).to_be_visible(timeout=timeout)
        assert "microsoftonline" not in self.page.url, (
            f"Still on Microsoft login/2FA instead of the app: {self.page.url}"
        )
        self.dismiss_blocking_dialogs()
        return self

    def return_to_home(self):
        """Back to Meditik home on the same browser tab (no new Chrome session).

        Prefers navbar home/logo; falls back to goto (e.g. after external Torim).
        """
        self.dismiss_blocking_dialogs()
        on_meditik = "meditik" in (urlparse(self.page.url).netloc or "")
        if on_meditik:
            logo = self.page.get_by_test_id(Ids.NAVBAR_BTN_LOGO)
            for btn in (self.home_menu_button, logo):
                try:
                    if btn.count() > 0 and btn.first.is_visible(timeout=1500):
                        btn.first.click()
                        break
                except Exception:
                    continue
            else:
                self.page.goto(self.home_url, wait_until="domcontentloaded", timeout=60000)
        else:
            self.page.goto(self.home_url, wait_until="domcontentloaded", timeout=60000)

        expect(self.dashboard_marker).to_be_visible(timeout=60000)
        assert "microsoftonline" not in self.page.url, (
            f"Lost session while returning home: {self.page.url}"
        )
        self.dismiss_blocking_dialogs()
        self.wait_for_loading_done()
        return self

    def is_menu_open(self) -> bool:
        try:
            return self.side_drawer.is_visible(timeout=500)
        except Exception:
            return False

    def close_menu(self):
        """Close side drawer if open (Escape, then close button). Always best-effort."""
        for _ in range(2):
            try:
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(200)
            except Exception:
                pass
            if not self.is_menu_open():
                return self
            try:
                if self.close_menu_button.count() > 0:
                    self.close_menu_button.first.click(force=True, timeout=2000)
                    self.page.wait_for_timeout(200)
            except Exception:
                pass
            if not self.is_menu_open():
                return self
        return self

    def open_menu(self):
        expect(self.menu_button).to_be_visible(timeout=15000)
        if self.is_menu_open():
            return self
        self.menu_button.click(force=True)
        expect(self.side_drawer).to_be_visible(timeout=10000)
        return self

    def menu_button_by_testid(self, test_id: str):
        return self.page.get_by_test_id(test_id)

    def menu_button_by_name(self, label: str):
        """Fallback: locate drawer item by Hebrew label (when testid unknown)."""
        drawer_items = self.side_drawer.locator(
            f'[data-testid^="{Ids.NAVBAR_MENU_ITEM_PREFIX}"], '
            f'[data-testid^="{Ids.NAVBAR_BTN_COMMON_PREFIX}"]'
        )
        return drawer_items.filter(has_text=label).first

    def _soft_check_menu_label(self, item, expected_label: str, test_id: str):
        try:
            actual = (item.inner_text(timeout=3000) or "").strip()
            actual = " ".join(actual.split())
        except Exception:
            actual = ""
        if expected_label and expected_label not in actual:
            report_soft_note(
                f"Menu label mismatch for {test_id}: "
                f"expected text containing {expected_label!r}, got {actual!r}. "
                f"Continuing by data-testid (element is visible)."
            )

    def navigate_via_menu(self, label: str, test_id: str | None = None):
        """Open side menu and click an item.

        Existence/visibility = data-testid (hard).
        Hebrew label = soft note in Allure if it differs.
        """
        self.open_menu()
        tid = test_id or self.MENU_TEST_IDS.get(label)
        if tid:
            item = self.menu_button_by_testid(tid)
            expect(item).to_be_visible(timeout=10000)
            self._soft_check_menu_label(item, label, tid)
        else:
            item = self.menu_button_by_name(label)
            expect(item).to_be_visible(timeout=10000)
            report_soft_note(
                f"No data-testid mapped for menu label {label!r}; "
                f"fell back to text match."
            )
        item.click()
        # Drawer often stays open and intercepts the next click (tiles / FAB).
        self.close_menu()
        self.dismiss_blocking_dialogs()
        self.wait_for_loading_done()
        return self

    def go_to_medical_profile(self):
        return self.navigate_via_menu(self.MENU_MEDICAL_PROFILE)

    def go_to_my_appointments(self):
        return self.navigate_via_menu(self.MENU_MY_APPOINTMENTS)

    def go_to_my_requests(self):
        return self.navigate_via_menu(self.MENU_MY_REQUESTS)

    def go_to_all_actions(self):
        return self.navigate_via_menu(self.MENU_SEND_DOCTOR_REQUEST)

    def go_to_urgent_care(self):
        return self.navigate_via_menu(self.MENU_URGENT_CARE)

    def go_to_lab_results(self):
        return self.navigate_via_menu(self.MENU_LAB_RESULTS)

    def go_to_medicines(self):
        return self.navigate_via_menu(self.MENU_MEDICINES)

    def go_to_visit_summaries(self):
        return self.navigate_via_menu(self.MENU_VISIT_SUMMARIES)

    def go_to_exemptions(self):
        return self.navigate_via_menu(self.MENU_EXEMPTIONS)

    def go_to_sick_days(self):
        return self.navigate_via_menu(self.MENU_SICK_DAYS)

    def go_to_referrals(self):
        return self.navigate_via_menu(self.MENU_REFERRALS)

    def go_to_vaccinations(self):
        return self.navigate_via_menu(self.MENU_VACCINATIONS)

    def rows_by_prefix(self, prefix: str):
        return self.page.locator(f'[data-testid^="{prefix}"]')
