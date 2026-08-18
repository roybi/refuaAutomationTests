"""BDD fixtures, markers, and Allure step trace shared by application suites."""

import pytest

from refua_tests.tests.conftest import (auth_state_session,  # noqa: F401
                                        browser_page)


def _bdd_trace(request):
    trace = getattr(request.node, "_bdd_step_trace", None)
    if trace is None:
        trace = []
        request.node._bdd_step_trace = trace
    return trace

@pytest.fixture(scope="function")
def setup_browser(browser_page):
    """Compatibility fixture for the legacy main-page BDD examples."""
    return browser_page


def pytest_collection_modifyitems(items):
    """Keep known product defects visible without failing every BDD smoke run."""
    for item in items:
        if item.get_closest_marker("known_issue"):
            item.add_marker(
                pytest.mark.xfail(
                    reason="Meditik phone input is disabled in the current TEST environment",
                    strict=False,
                )
            )


def pytest_bdd_before_step(request, feature, scenario, step, step_func):
    """Record every Gherkin action before it executes."""
    _bdd_trace(request).append(f"STARTED | {step.keyword} {step.name}")


def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args):
    """Mark the Gherkin action passed after its step definition returns."""
    action = f"PASSED  | {step.keyword} {step.name}"
    _bdd_trace(request).append(action)
    _attach_bdd_action(action)


def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    """Mark a failed Gherkin action so the Allure trace pinpoints the failure."""
    action = (
        f"FAILED  | {step.keyword} {step.name} | {type(exception).__name__}: {exception}"
    )
    _bdd_trace(request).append(action)
    _attach_bdd_action(action)


def _attach_bdd_action(action):
    """Create an Allure attachment while the BDD step is still executing."""
    try:
        import allure

        allure.attach(
            action,
            name="BDD scenario action",
            attachment_type=allure.attachment_type.TEXT,
        )
    except ImportError:
        pass



