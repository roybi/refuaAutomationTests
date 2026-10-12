"""Pytest-BDD scenario loader for the legacy MainPage feature."""

from pytest_bdd import scenarios

from refua_tests.bdd.step_defs.mainPageSteps import *  # noqa: F403

scenarios("features/mainPage.feature")
