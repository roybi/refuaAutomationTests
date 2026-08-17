"""Pytest-BDD scenario loader for the Meditik application."""

from pytest_bdd import scenarios

from refua_tests.bdd.step_defs.meditikSteps import *  # noqa: F403

scenarios("features/meditik_home.feature")
scenarios("features/meditik_menu.feature")
scenarios("features/meditik_request_forms.feature")
