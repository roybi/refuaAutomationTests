"""
Page Objects Module

Contains Page Object Models (POM) for MEDITEK application UI.
All page objects inherit from refua_core.pages.BasePage.

Example:
    from refua_tests.pages.login_page import LoginPage
    from playwright.sync_api import Page

    def test_login(page: Page):
        login_page = LoginPage(page)
        login_page.goto("/login")
        login_page.login("user@test.com", "password")
"""
