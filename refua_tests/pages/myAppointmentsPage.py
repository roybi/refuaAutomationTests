"""Meditik my-appointments (התורים שלי) — data-testid mapping."""

from refua_tests.pages.automationIds import MeditikIds as Ids
from refua_tests.pages.meditikContentPage import MeditekContentPage


class MyAppointmentsPage(MeditekContentPage):
    PAGE_TITLE = "התורים שלי"
    PATH = "/zimun-torim"
    PAGE_TEST_ID = Ids.APPOINTMENTS_PAGE
    TAB_TEST_IDS = (
        Ids.APPOINTMENTS_TAB_UPCOMING,
        Ids.APPOINTMENTS_TAB_WAITING_LIST,
        Ids.APPOINTMENTS_TAB_HISTORY,
    )
    TAB_LABELS = ("תורים קרובים", "רשימות המתנה", "תורים קודמים")
    ROW_PREFIX = Ids.APPOINTMENTS_ROW_PREFIX
    EMPTY_MARKERS = (
        "יומן התורים שלך ריק",
        "כשיהיו לך רשימות המתנה הן יופיעו כאן",
        "יופיעו כאן",
    )
