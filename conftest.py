"""Root conftest: command-line options must be registered here so every invocation sees them."""

import os
import warnings

import pytest

from refua_tests.systems import (ALL, SYSTEMS, describe, owners_of,
                                 resolve_system, system_names)


def pytest_addoption(parser):
    parser.addoption("--personal-number", default=None,
                     help="Today's test user: drives /automation/login/:personalNumber and the DB seed")
    parser.addoption(
        "--system", default=None,
        help=f"System under test: {', '.join(system_names() + [ALL])}. Required whenever "
             "system-owned tests are collected; selects only that system's tests.")


def pytest_configure(config):
    personal_number = config.getoption("--personal-number")
    if personal_number:
        os.environ["TEST_PERSONAL_NUMBER"] = personal_number.strip()
        # Same person for /automation/login/:personalNumber and the DB seed.
        os.environ.setdefault("TEST_AUTH_METHOD", "automation")

    config._refua_system = None
    config._refua_active_systems = None
    requested = config.getoption("--system")
    if requested:
        try:
            selected = resolve_system(requested)
        except ValueError as error:
            raise pytest.UsageError(str(error)) from None
        config._refua_system = selected
        if selected is not None:
            os.environ["TEST_APP"] = selected.app_id


def pytest_report_header(config):
    system = config.getoption("--system")
    if not system:
        return None
    user = config.getoption("--personal-number") or "-"
    return f"System: {system} | User: {user} | Env: {os.getenv('TEST_ENV', 'test')}"


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config, items):
    """Keep only the selected system's tests and record which systems are active."""
    requested = config.getoption("--system")
    owners = {id(item): owners_of(item) for item in items}
    any_owned = any(owners.values())

    if not requested:
        if any_owned:
            pytest.exit(
                "--system is required. Choose one of: "
                f"{', '.join(system_names() + [ALL])}. "
                "Example: python run_tests.py --system meditik --user <personalNumber>",
                returncode=4,
            )
        return

    selected = config._refua_system
    available = set().union(*owners.values()) if owners else set()
    if selected is not None:
        dropped = [item for item in items if selected.name not in owners[id(item)]]
        if dropped:
            config.hook.pytest_deselected(items=dropped)
            items[:] = [item for item in items if selected.name in owners[id(item)]]
    else:
        unowned = [item for item in items if not owners[id(item)]]
        if unowned and any_owned:
            warnings.warn(
                f"{len(unowned)} collected tests carry no system marker "
                f"({', '.join(spec.marker for spec in SYSTEMS.values())}); "
                f"first: {unowned[0].nodeid}"
            )

    config._refua_active_systems = set().union(*(owners[id(item)] for item in items)) if items else set()
    if not items:
        warnings.warn(
            f"No tests selected for system '{requested}'. Systems with collected tests: "
            f"{describe(available)}."
        )
