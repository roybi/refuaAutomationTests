from playwright.sync_api import Page
from refua_core.config.environment import EnvironmentManager
from refua_core.core.base_page import BasePage


class MainPage(BasePage):
    """Main page object for MEDITEK application"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.env_manager = EnvironmentManager()

        # Page Locators
        self.logo = page.locator("img[alt='MEDITEK']")
        self.main_content = page.locator("main")
        self.navigation_menu = page.locator("[role='navigation']")
        self.main_menu = page.locator("[role='navigation']")
        self.items_list = page.locator("[data-testid='items-list']")
        self.user_profile = page.locator("[data-testid='user-profile']")
        self.sidebar = page.locator("[data-testid='sidebar']")

    @property
    def items_base_url(self):
        """Get the full main page URL from environment"""
        return self.env_manager.get_base_url()

    def get_current_environment(self):
        """Get the current test environment name"""
        return self.env_manager.current_env.value

    def navigate_to_items(self):
        """Navigate to items page"""
        self.goto(self.items_base_url)

    def is_loaded(self):
        """Check if the main page is loaded"""
        return self.logo.is_visible()
