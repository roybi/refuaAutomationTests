"""Pytest-BDD scenario loader for the Meditik application."""

from pytest_bdd import scenarios

from refua_tests.bdd.step_defs.medicinesSteps import *  # noqa: F403
from refua_tests.bdd.step_defs.meditikSteps import *  # noqa: F403
from refua_tests.bdd.step_defs.myAppointmentsSteps import *  # noqa: F403
from refua_tests.bdd.step_defs.myRequestsSteps import *  # noqa: F403
from refua_tests.bdd.step_defs.referralsSteps import *  # noqa: F403
from refua_tests.bdd.step_defs.schedulingSteps import *  # noqa: F403
from refua_tests.bdd.step_defs.sickDaysSteps import *  # noqa: F403
from refua_tests.bdd.step_defs.vaccinationsSteps import *  # noqa: F403

scenarios("features/meditik_home.feature")
scenarios("features/meditik_menu.feature")
scenarios("features/meditik_request_forms.feature")
scenarios("features/meditik_my_requests.feature")
scenarios("features/meditik_my_appointments.feature")
scenarios("features/meditik_referrals_tabs.feature")
scenarios("features/meditik_medicines_tabs.feature")
scenarios("features/meditik_scheduling.feature")
scenarios("features/meditik_sick_days.feature")
scenarios("features/meditik_vaccinations.feature")
