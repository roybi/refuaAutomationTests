"""
BDD Test Configuration

Provides pytest fixtures and configuration specifically for BDD tests.
Integrates with the main test framework (BaseTest) while supporting Gherkin features.
"""

import os
import pytest
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from refua_core.config.environment import get_env_manager


@pytest.fixture(scope="function")
def setup_browser():
    """
    Setup browser for BDD tests

    This fixture provides a Playwright page object for BDD step definitions.
    """
    env_manager = get_env_manager()

    with sync_playwright() as playwright:
        browser_type = env_manager.get_browser_type()

        if browser_type == "firefox":
            browser = playwright.firefox.launch(headless=False)
        elif browser_type == "webkit":
            browser = playwright.webkit.launch(headless=False)
        else:  # chromium (default)
            browser = playwright.chromium.launch(headless=False)

        record_video = os.getenv("RECORD_VIDEO", "false").lower() == "true"
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir="test-artifacts/videos" if record_video else None,
        )

        page = context.new_page()

        yield page

        page.close()
        context.close()
        browser.close()


@pytest.fixture(scope="session", autouse=True)
def configure_bdd_environment():
    """
    Configure environment for BDD tests

    Ensures environment is properly initialized before any BDD tests run.
    """
    env_manager = get_env_manager()
    print(f"\n[BDD] Running in environment: {env_manager.current_env.value}")
    print(f"[BDD] Base URL: {env_manager.get_base_url()}")
    return env_manager

