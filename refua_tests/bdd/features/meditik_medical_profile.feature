@bdd @meditik @smoke @medical_profile
Feature: Meditik Medical Profile / פרופיל רפואי
  As a Meditik user
  I want to reach the Medical Profile page and use its shell controls
  So that I can read my medical profile without altering any of it

  Background:
    Given an authenticated "meditik" application user is on the home page

  Scenario: MEDICAL-PROFILE-001 - Open the Medical Profile page
    When the user navigates to the Medical Profile page
    Then the Medical Profile route and toolbar are displayed
    And no Medical Profile mutation signal is observed

  Scenario: MEDICAL-PROFILE-004 - Appointment-booking quick action is available
    Given the user navigates to the Medical Profile page
    When the user opens the Medical Profile quick-action control
    Then the supplied appointment-booking quick action is exposed
    And no Medical Profile mutation signal is observed

  Scenario: MEDICAL-PROFILE-011 - Reach Medical Profile through application navigation
    When the user opens application navigation and selects Medical Profile
    Then the Medical Profile route and toolbar are displayed
    And no Medical Profile mutation signal is observed
