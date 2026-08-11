"""
Meditik Page Object Models.

Architecture:
    refua_core.pages.BasePage          (framework — do not edit)
        └── MeditekBasePage            (shared Meditik chrome / menu / login)
              ├── MeditekContentPage   (shared URL/title/tabs/content sanity)
              ├── MedicalProfilePage / AllActionsPage / MyAppointmentsPage / MyRequestsPage
              └── menu_pages.py        (remaining menu destinations)
"""

from refua_tests.pages.automation_ids import MeditikIds
from refua_tests.pages.meditek_base_page import MeditekBasePage
from refua_tests.pages.meditek_content_page import MeditekContentPage
from refua_tests.pages.medical_profile_page import MedicalProfilePage
from refua_tests.pages.all_actions_page import AllActionsPage
from refua_tests.pages.my_appointments_page import MyAppointmentsPage
from refua_tests.pages.my_requests_page import MyRequestsPage
from refua_tests.pages.home_page_meditek import MeditekHomePage
from refua_tests.pages.speed_dial import SpeedDial
from refua_tests.pages.request_forms import RequestFormPage, REQUEST_FORMS
from refua_tests.pages.menu_pages import (
    BookAppointmentPage,
    ExemptionsPage,
    LabResultsPage,
    MedicinesPage,
    ReferralsPage,
    SickDaysPage,
    UrgentCarePage,
    VaccinationsPage,
    VisitSummariesPage,
)

__all__ = [
    "MeditikIds",
    "MeditekBasePage",
    "MeditekContentPage",
    "MeditekHomePage",
    "SpeedDial",
    "RequestFormPage",
    "REQUEST_FORMS",
    "MedicalProfilePage",
    "AllActionsPage",
    "MyAppointmentsPage",
    "MyRequestsPage",
    "BookAppointmentPage",
    "UrgentCarePage",
    "LabResultsPage",
    "MedicinesPage",
    "VisitSummariesPage",
    "ExemptionsPage",
    "SickDaysPage",
    "ReferralsPage",
    "VaccinationsPage",
]
