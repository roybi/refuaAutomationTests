"""Meditik menu destination page objects — data-testid mapping."""

from playwright.sync_api import expect

from refua_tests.pages.automation_ids import MeditikIds as Ids
from refua_tests.pages.meditek_base_page import MeditekBasePage
from refua_tests.pages.meditek_content_page import MeditekContentPage


class UrgentCarePage(MeditekContentPage):
    PAGE_TITLE = "פניה לרפואה דחופה"
    PATH = "/urgent-care"
    PAGE_TEST_ID = Ids.URGENT_CARE_PAGE

    def assert_content_loaded(self):
        expect(self.page_marker()).to_be_visible()
        assert self.PATH in self.page.url
        self.assert_no_app_error(context=self.PAGE_TITLE)


class LabResultsPage(MeditekContentPage):
    PAGE_TITLE = "תוצאות בדיקות"
    PATH = "/lab-results"
    PAGE_TEST_ID = Ids.LAB_RESULTS_PAGE
    TAB_TEST_IDS = (
        Ids.LAB_RESULTS_TAB_REGULAR,
        Ids.LAB_RESULTS_TAB_CULTURE,
        Ids.LAB_RESULTS_TAB_IMAGING,
    )
    TAB_LABELS = ("בדיקות רגילות", "תרביות", "הדמיה")
    ROW_PREFIX = Ids.LAB_RESULTS_ROW_PREFIX
    EMPTY_MARKERS = ("אין לך", "לא נמצאו", "יופיעו כאן")


class MedicinesPage(MeditekContentPage):
    PAGE_TITLE = "תרופות ומרשמים"
    PATH = "/medicines"
    PAGE_TEST_ID = Ids.MEDICINES_PAGE
    # Mapping has no tabs; live UI may still show Hebrew tabs — optional via labels
    TAB_LABELS = ("המרשמים שלי", "תרופות קבועות", "מרשמים קודמים")
    ROW_PREFIX = Ids.MEDICINES_ROW_PREFIX
    EMPTY_MARKERS = ("אין לך", "יופיעו כאן", "לא נמצאו")


class VisitSummariesPage(MeditekContentPage):
    """סיכומי ביקור — page id not in mapping yet."""

    PAGE_TITLE = "סיכומי ביקור"
    PATH = "/appointments"
    EMPTY_MARKERS = ("אין לך", "יופיעו כאן", "לא נמצאו")


class ExemptionsPage(MeditekContentPage):
    PAGE_TITLE = "פטורים"
    PATH = "/exemptions"
    PAGE_TEST_ID = Ids.EXEMPTIONS_PAGE
    TAB_LABELS = ("הפטורים שלי", "פטורים קודמים")
    ROW_PREFIX = Ids.EXEMPTIONS_ROW_PREFIX
    EMPTY_MARKERS = ("אין לך פטורים", "יופיעו כאן", "אין לך")


class SickDaysPage(MeditekContentPage):
    PAGE_TITLE = "ימי מחלה"
    PATH = "/sick-days"
    PAGE_TEST_ID = Ids.SICK_DAYS_PAGE
    ROW_PREFIX = Ids.SICK_DAYS_ROW_PREFIX
    EMPTY_MARKERS = ("אין לך", "יופיעו כאן", "לא נמצאו")


class ReferralsPage(MeditekContentPage):
    PAGE_TITLE = "הפניות"
    PATH = "/referrals"
    PAGE_TEST_ID = Ids.REFERRALS_PAGE
    TAB_LABELS = ("הפניות שלי", "הפניות שממתינות לאישור", "הפניות קודמות")
    ROW_PREFIX = Ids.REFERRALS_ROW_PREFIX
    EMPTY_MARKERS = ("אין לך הפניה", "אין לך הפניות", "יופיעו כאן")


class VaccinationsPage(MeditekContentPage):
    PAGE_TITLE = "חיסונים"
    PATH = "/vaccinations"
    PAGE_TEST_ID = Ids.VACCINATIONS_PAGE
    ROW_PREFIX = Ids.VACCINATIONS_ROW_PREFIX
    EMPTY_MARKERS = ("אין לך", "יופיעו כאן", "לא נמצאו")


class BookAppointmentPage(MeditekBasePage):
    """זימון תור — external Torim app (same tab)."""

    EXTERNAL_HOST = "torim.test.prat.idf.il"
    EXPECTED_TITLE = "זימון תורים"

    def run_menu_sanity(self, *, session_ready: bool = False):
        if not session_ready:
            self.open_home()
            self.ensure_logged_in()
        self.navigate_via_menu(self.MENU_BOOK_APPOINTMENT)
        self.page.wait_for_url(f"**{self.EXTERNAL_HOST}**", timeout=60000)
        assert self.EXTERNAL_HOST in self.page.url, (
            f"Expected external Torim host, got {self.page.url}"
        )
        # Title may lag slightly after navigation
        try:
            self.page.wait_for_function(
                "() => (document.title || '').includes('זימון')",
                timeout=10000,
            )
        except Exception:
            self.page.wait_for_timeout(1500)
        title = self.page.title() or ""
        assert self.EXPECTED_TITLE in title or "זימון" in title, (
            f"Expected Torim booking title, got {title!r}"
        )
