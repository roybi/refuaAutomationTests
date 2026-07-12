"""
First browser test — MEDITEK Login / Home Page

Tests the login screen (https://meditik.test.medical.idf.il/home) using the
homePage Page Object Model.  No authentication is required — the login page
is publicly accessible.

Run a single test:
    TEST_ENV=test pytest refua_tests/tests/test_home_page.py::TestHomePage::test_login_page_loads -v

Run the full suite:
    TEST_ENV=test pytest refua_tests/tests/test_home_page.py -v
"""

import pytest

from refua_core.pages.home_Page import homePage


@pytest.mark.smoke
@pytest.mark.ui
class TestHomePage:
    """Smoke tests for the MEDITEK login / home screen.

    Uses the ``browser_page`` fixture (provided by the refua-core plugin)
    which launches a Chromium browser, optionally loads a saved session, and
    yields a Playwright :class:`Page` object.
    """

    def test_login_page_loads(self, browser_page):
        """
        Test: login page loads and shows the expected title.

        Steps:
          1. Navigate to the home / login URL
          2. Wait for the page to be fully loaded (networkidle)
          3. Verify the login card title is 'כניסה למערכת'

        Expected: title text contains 'כניסה למערכת'
        """
        browser_page.goto(homePage.PAGE_URL, wait_until="networkidle")
        home = homePage(browser_page)

        title = home.get_login_title_text()

        assert "כניסה למערכת" in title, (
            f"Login page title should contain 'כניסה למערכת', got: {title!r}"
        )

    def test_login_button_is_visible(self, browser_page):
        """
        Test: the SSO login button (התחברות) is visible on the login page.

        Expected: LOGIN_BUTTON resolves via SmartLocator and is visible
        """
        browser_page.goto(homePage.PAGE_URL, wait_until="networkidle")
        home = homePage(browser_page)

        assert home.locate(home.LOGIN_BUTTON).is_visible(), (
            "Login button ('התחברות') should be visible on the page"
        )

    def test_register_button_is_visible(self, browser_page):
        """
        Test: the MyIDF registration link (הרשמה כאן!) is visible.

        Expected: REGISTER_MYIDF_BUTTON resolves and is visible
        """
        browser_page.goto(homePage.PAGE_URL, wait_until="networkidle")
        home = homePage(browser_page)

        assert home.locate(home.REGISTER_MYIDF_BUTTON).is_visible(), (
            "Register button ('הרשמה כאן!') should be visible on the page"
        )

    def test_login_subtitle_has_content(self, browser_page):
        """
        Test: the login subtitle paragraph has non-empty text.

        Expected: LOGIN_SUBTITLE has text content
        """
        browser_page.goto(homePage.PAGE_URL, wait_until="networkidle")
        home = homePage(browser_page)

        subtitle = home.locate(home.LOGIN_SUBTITLE).text_content() or ""

        assert len(subtitle.strip()) > 0, (
            "Login subtitle should contain descriptive text"
        )

    def test_main_logo_is_visible(self, browser_page):
        """
        Test: the MEDITEK branding logo is visible on the login page.

        Expected: MAIN_LOGO resolves and is visible
        """
        browser_page.goto(homePage.PAGE_URL, wait_until="networkidle")
        home = homePage(browser_page)

        assert home.locate(home.MAIN_LOGO).is_visible(), (
            "Main logo should be visible on the login page"
        )

    def test_page_title_is_meditik(self, browser_page):
        """
        Test: the browser tab title is 'MediTik'.

        Expected: page.title() == 'MediTik'
        """
        browser_page.goto(homePage.PAGE_URL, wait_until="networkidle")

        assert browser_page.title() == "MediTik", (
            f"Browser tab title should be 'MediTik', got: {browser_page.title()!r}"
        )

    def test_smart_locator_fallback_chain(self, browser_page):
        """
        Test: SmartLocator correctly falls back from TEST_ID to XPATH.

        Since the login page has no data-testid on the login button yet,
        the SmartLocator should resolve via XPATH and the element should be
        both visible and enabled.

        Expected: LOGIN_BUTTON resolves, is_visible(), is_enabled()
        """
        browser_page.goto(homePage.PAGE_URL, wait_until="networkidle")
        home = homePage(browser_page)

        locator = home.locate(home.LOGIN_BUTTON)

        assert locator.is_visible(), "SmartLocator should resolve LOGIN_BUTTON via XPATH"
        assert locator.is_enabled(), "LOGIN_BUTTON should be enabled (clickable)"
