"""Root conftest: command-line options must be registered here so every invocation sees them."""

import os


def pytest_addoption(parser):
    parser.addoption("--personal-number", default=None,
                     help="Today's test user: drives /automation/login/:personalNumber and the DB seed")


def pytest_configure(config):
    personal_number = config.getoption("--personal-number")
    if personal_number:
        os.environ["TEST_PERSONAL_NUMBER"] = personal_number.strip()
        # Same person for /automation/login/:personalNumber and the DB seed.
        os.environ.setdefault("TEST_AUTH_METHOD", "automation")
