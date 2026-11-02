@bdd @meditik @smoke @medicines
Feature: Meditik Medicines and Prescriptions / תרופות ומרשמים tabbed screen
  As a Meditik user
  I want to review My Prescriptions, Permanent Medicines and Previous Prescriptions
  So that I can track my medication and prescription history

  Background:
    Given an authenticated "meditik" application user is on the home page

  Scenario: MEDICINES-001 - Load the Medicines and Prescriptions page
    When the user navigates to the Medicines page
    Then the Medicines page container, navigation shell and three tabs are displayed

  Scenario Outline: A medicine category is displayed as the active content
    When the user navigates to the Medicines page
    And the user selects the "<tab>" medicine tab
    Then the "<tab>" medicine panel is the active content

    Examples:
      | tab       |
      | active    |
      | permanent |
      | expired   |

  Scenario: MEDICINES-009 - My Prescriptions empty state
    Given the user navigates to the Medicines page
    And the user selects the "active" medicine tab
    Then the My Prescriptions panel shows a scoped empty-state icon and title

  Scenario: MEDICINES-014 - E2E medicine category navigation
    When the user navigates to the Medicines page
    And the user opens every medicine category in sequence
    Then exactly one medicine panel is active at each step
