import pytest
from playwright.sync_api import expect
from refua_core.pages.home_Page import homePage


@pytest.mark.smoke
@pytest.mark.ui
class TestSmoke:
    """Smoke tests for opening MEDITEK with a captured (2FA-bypass) session."""

    # SpeedDial label rendered only on the logged-in dashboard
    DASHBOARD_QUICK_ACTIONS = "פעולות מהירות"

    def test_open_app_with_session_no_2fa(self, browser_page):
        """Open /home and verify we reach the app without a 2FA prompt.

        With a valid captured session the app behaves in one of two ways:
        1. MSAL picks up the stored tokens and signs in silently — the
           logged-in dashboard renders immediately.
        2. The login page renders first — clicking התחברות must SSO through
           Microsoft and land back in the app without a 2FA prompt.
        """
        browser_page.goto(homePage.PAGE_URL)
        home = homePage(browser_page)

        login_button = browser_page.locator("#login-button")
        dashboard = browser_page.get_by_text(self.DASHBOARD_QUICK_ACTIONS).first

        # Wait until the app settles on one of the two known states
        expect(login_button.or_(dashboard).first).to_be_visible(timeout=60000)

        if login_button.is_visible():
            # Path 2: login page shown — verify the login card, then SSO in
            expect(home.locate(home.LOGIN_TITLE)).to_be_visible()
            expect(home.locate(home.LOGIN_SUBTITLE)).to_be_visible()
            expect(home.locate(home.REGISTER_MYIDF_BUTTON)).to_be_visible()
            home.close_pwa_dialog()

            expect(login_button).to_be_enabled()
            expect(login_button).to_contain_text("התחברות")
            home.click_login()

        # Both paths must end authenticated inside the app, never on a 2FA page
        expect(dashboard).to_be_visible(timeout=60000)
        assert "microsoftonline" not in browser_page.url, (
            f"Ended on a Microsoft login/2FA page instead of the app: {browser_page.url}"
        )
