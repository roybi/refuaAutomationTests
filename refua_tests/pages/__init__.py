"""
Meditik Page Object Models.

Architecture:
    refua_core.pages.BasePage          (framework — do not edit)
        └── MeditekBasePage            (shared Meditik chrome / menu / login)
              ├── MeditekContentPage   (shared URL/title/tabs/content sanity)
              ├── MedicalProfilePage / AllActionsPage / MyAppointmentsPage / MyRequestsPage
              └── menu_pages.py        (remaining menu destinations)
"""

from refua_tests.pages.automationIds import MeditikIds
from refua_tests.pages.meditikBasePage import MeditekBasePage
from refua_tests.pages.meditikContentPage import MeditekContentPage
from refua_tests.pages.medicalProfilePage import MedicalProfilePage
from refua_tests.pages.allActionsPage import AllActionsPage
from refua_tests.pages.myAppointmentsPage import MyAppointmentsPage
from refua_tests.pages.myRequestsPage import MyRequestsPage
from refua_tests.pages.meditikHomePage import MeditekHomePage
from refua_tests.pages.speedDial import SpeedDial
from refua_tests.pages.requestForms import RequestFormPage, REQUEST_FORMS
from refua_tests.pages.menuPages import (
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
