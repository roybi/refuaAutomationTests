"""Meditik medical profile — data-testid mapping."""

from refua_tests.pages.automationIds import MeditikIds as Ids
from refua_tests.pages.meditikContentPage import MeditekContentPage


class MedicalProfilePage(MeditekContentPage):
    PAGE_TITLE = "פרופיל רפואי"
    PATH = "/medical-profile"
    PAGE_TEST_ID = Ids.MEDICAL_PROFILE_PAGE
    EMPTY_MARKERS = ("אין לך עדיין פרופיל רפואי",)
