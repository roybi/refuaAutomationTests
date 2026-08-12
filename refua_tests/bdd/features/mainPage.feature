Feature: Main Page Functionality
  As a QA engineer
  I want to verify the Main Page works correctly across all environments
  So that users can access the application reliably

  Background:
    Given the test environment is configured
    And the browser is launched

  @smoke @main_page
  Scenario: Test environment URL resolution
    Given I am testing the main page
    When I get the items base URL for "test" environment
    Then the URL should contain "meditik.test.medical.idf.il"
    And the full URL should be "https://meditik.test.medical.idf.il/home"
    And the current environment should be "test"

  @smoke @main_page
  Scenario: Preprod environment URL resolution
    Given I am testing the main page
    When I get the items base URL for "preprod" environment
    Then the URL should contain "meditik.preprod.medical.idf.il"
    And the full URL should be "https://meditik.preprod.medical.idf.il/home"

  @smoke @main_page
  Scenario: Main page inherits from base page
    Given I have a main page object
    Then the main page should have the "goto" method
    And the main page should have the "wait_for_url" method
    And the "goto" method should be callable

  @smoke @main_page
  Scenario: Main page has environment manager
    Given I have a main page object
    Then the main page should have "env_manager" attribute
    And the "env_manager" should be initialized

  @smoke @main_page
  Scenario: Get current environment returns valid string
    Given I have a main page object
    When I get the current environment
    Then the environment should be a string
    And the environment should be one of "test,preprod,prod"

  @smoke @main_page
  Scenario: Items base URL is a property
    Given I have a main page object
    When I access the "items_base_url" property
    Then it should return a string
    And it should start with "https://"
    And it should end with "/home"

  @smoke @main_page
  Scenario: Logo locator exists
    Given I have a main page object
    Then the main page should have "logo" property
    And the "logo" property should not be None

  @smoke @main_page
  Scenario: Main menu locator exists
    Given I have a main page object
    Then the main page should have "main_menu" property
    And the "main_menu" property should not be None

  @smoke @main_page
  Scenario: Items list locator exists
    Given I have a main page object
    Then the main page should have "items_list" property
    And the "items_list" property should not be None

  @smoke @main_page
  Scenario: Navigate to items method exists
    Given I have a main page object
    Then the main page should have "navigate_to_items" method
    And the "navigate_to_items" method should be callable

  @smoke @main_page
  Scenario: Is loaded method exists
    Given I have a main page object
    Then the main page should have "is_loaded" method
    And the "is_loaded" method should be callable

  @regression @main_page
  Scenario Outline: URL contains correct domain for each environment
    Given I am testing the main page for "<environment>" environment
    When I get the items base URL
    Then the URL should contain the "<domain_pattern>" domain

    Examples:
      | environment | domain_pattern            |
      | test        | .test.medical.idf.il      |
      | preprod     | .preprod.medical.idf.il   |
      | prod        | meditik.medical.idf.il    |

  @regression @main_page
  Scenario: All URLs use HTTPS protocol
    Given I have a main page object
    When I get the items base URL
    Then the URL should use HTTPS protocol

  @regression @main_page
  Scenario: URL ends with home path
    Given I have a main page object
    When I get the items base URL
    Then the URL should end with "/home" path
