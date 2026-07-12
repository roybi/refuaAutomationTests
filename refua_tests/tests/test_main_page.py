"""
Test cases for MainPage
Demonstrates how to use MainPage with dynamic environment URLs
"""

import pytest
from refua_core.core import BaseTest
from refua_core.core.base_test import BaseTest

from refua_tests.pages.mainPage import MainPage


@pytest.mark.smoke
class TestMainPage(BaseTest):
    """Main page tests with environment-aware URLs"""

    def setUp(self):
        """Setup before each test"""
        super().setUp()
        self.main_page = MainPage(self.page)

    def test_environment_url_resolution_test(self):
        """
        Test: Verify correct URL is used for test environment

        Execution:
            TEST_ENV=test pytest refua_tests/tests/test_main_page.py::TestMainPage::test_environment_url_resolution_test -v

        Expected:
            - URL contains 'meditik.test.medical.idf.il'
        """
        # Arrange
        main_page = MainPage(self.page)

        # Act
        url = main_page.items_base_url
        env = main_page.get_current_environment()

        # Assert
        assert env == "test", f"Environment should be 'test', got '{env}'"
        assert "meditik.test.medical.idf.il" in url, (
            f"Test URL should contain 'meditik.test.medical.idf.il', got {url}"
        )
        assert url == "https://meditik.test.medical.idf.il/home", (
            f"Expected 'https://meditik.test.medical.idf.il/home', got {url}"
        )

    def test_environment_url_resolution_preprod(self):
        """
        Test: Verify correct URL is used for preprod environment

        Execution:
            TEST_ENV=preprod pytest refua_tests/tests/test_main_page.py::TestMainPage::test_environment_url_resolution_preprod -v

        Expected:
            - URL contains 'meditik.preprod.medical.idf.il'
        """
        # This test will pass when run with TEST_ENV=preprod
        main_page = MainPage(self.page)
        url = main_page.items_base_url
        env = main_page.get_current_environment()

        # Assert URL structure for preprod
        if env == "preprod":
            assert "meditik.preprod.medical.idf.il" in url
            assert url == "https://meditik.preprod.medical.idf.il/home"

    def test_page_object_inherits_from_base_page(self):
        """
        Test: MainPage properly inherits from BasePage

        Verifies that MainPage has access to BasePage methods like goto()
        """
        main_page = MainPage(self.page)

        # Verify BasePage methods are available
        assert hasattr(main_page, "goto"), (
            "MainPage should have goto() method from BasePage"
        )
        assert hasattr(main_page, "wait_for_url"), (
            "MainPage should have wait_for_url() method from BasePage"
        )
        assert callable(main_page.goto), "goto should be callable"

    def test_main_page_has_environment_manager(self):
        """
        Test: MainPage has EnvironmentManager instance

        Verifies that MainPage can access current environment
        """
        main_page = MainPage(self.page)

        # Verify environment manager is available
        assert hasattr(main_page, "env_manager"), "MainPage should have env_manager"
        assert main_page.env_manager is not None, "env_manager should be initialized"

    def test_get_current_environment_returns_string(self):
        """
        Test: get_current_environment() returns the correct environment string

        The environment string matches the TEST_ENV variable
        """
        main_page = MainPage(self.page)

        # Get environment
        env = main_page.get_current_environment()

        # Assert it's a string and has expected value
        assert isinstance(env, str), f"Environment should be string, got {type(env)}"
        assert env in ["test", "preprod", "prod"], (
            f"Environment should be one of ['test', 'preprod', 'prod'], got '{env}'"
        )

    def test_items_base_url_is_property(self):
        """
        Test: items_base_url is a property that doesn't require calling

        Verifies that we access items_base_url as property not method
        """
        main_page = MainPage(self.page)

        # Get URL as property (not method call)
        url = main_page.items_base_url

        # Assert it's a string and valid URL
        assert isinstance(url, str), f"URL should be string, got {type(url)}"
        assert url.startswith("https://"), f"URL should start with https://, got {url}"
        assert url.endswith("/home"), f"URL should end with /home, got {url}"

    def test_logo_locator_exists(self):
        """
        Test: logo locator is defined

        Verifies MainPage has logo element locator
        """
        main_page = MainPage(self.page)

        # Verify logo property exists and returns Locator
        assert hasattr(main_page, "logo"), "MainPage should have logo property"
        logo = main_page.logo
        assert logo is not None, "logo property should not be None"

    def test_main_menu_locator_exists(self):
        """
        Test: main_menu locator is defined

        Verifies MainPage has main navigation menu locator
        """
        main_page = MainPage(self.page)

        assert hasattr(main_page, "main_menu"), (
            "MainPage should have main_menu property"
        )
        menu = main_page.main_menu
        assert menu is not None, "main_menu property should not be None"

    def test_items_list_locator_exists(self):
        """
        Test: items_list locator is defined

        Verifies MainPage has items list locator
        """
        main_page = MainPage(self.page)

        assert hasattr(main_page, "items_list"), (
            "MainPage should have items_list property"
        )
        items = main_page.items_list
        assert items is not None, "items_list property should not be None"


class TestMainPageNavigation(BaseTest):
    """Navigation tests for MainPage"""

    def test_navigate_to_items_method_exists(self):
        """
        Test: navigate_to_items() method exists

        Verifies the navigation method is available
        """
        main_page = MainPage(self.page)

        # Verify method exists
        assert hasattr(main_page, "navigate_to_items"), (
            "MainPage should have navigate_to_items() method"
        )
        assert callable(main_page.navigate_to_items), (
            "navigate_to_items should be callable"
        )

    def test_is_loaded_method_exists(self):
        """
        Test: is_loaded() method exists

        Verifies the page load check method is available
        """
        main_page = MainPage(self.page)

        # Verify method exists
        assert hasattr(main_page, "is_loaded"), (
            "MainPage should have is_loaded() method"
        )
        assert callable(main_page.is_loaded), "is_loaded should be callable"


# Parametrized test for multiple environments
@pytest.mark.regression
class TestMainPageEnvironments(BaseTest):
    """Test MainPage URLs across environments"""

    def test_url_contains_correct_domain(self):
        """
        Test: URL contains correct domain for environment

        This test runs for all environments:
            TEST_ENV=test pytest refua_tests/tests/test_main_page.py::TestMainPageEnvironments::test_url_contains_correct_domain -v
            TEST_ENV=preprod pytest refua_tests/tests/test_main_page.py::TestMainPageEnvironments::test_url_contains_correct_domain -v
            TEST_ENV=prod pytest refua_tests/tests/test_main_page.py::TestMainPageEnvironments::test_url_contains_correct_domain -v
        """
        main_page = MainPage(self.page)
        url = main_page.items_base_url
        env = main_page.get_current_environment()

        # Verify URL contains appropriate domain
        if env == "test":
            assert ".test.medical.idf.il" in url
        elif env == "preprod":
            assert ".preprod.medical.idf.il" in url
        elif env == "prod":
            assert "meditik.medical.idf.il" in url
            assert ".test" not in url
            assert ".preprod" not in url

    def test_url_has_https_protocol(self):
        """
        Test: All URLs use HTTPS protocol
        """
        main_page = MainPage(self.page)
        url = main_page.items_base_url

        assert url.startswith("https://"), f"URL should use HTTPS protocol: {url}"

    def test_url_ends_with_home_path(self):
        """
        Test: URL ends with /home path
        """
        main_page = MainPage(self.page)
        url = main_page.items_base_url

        assert url.endswith("/home"), f"URL should end with '/home': {url}"
