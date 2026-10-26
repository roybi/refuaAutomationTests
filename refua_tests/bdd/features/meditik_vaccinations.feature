@bdd @meditik @smoke @vaccinations
Feature: Meditik Vaccinations / חיסונים
  As a Meditik user
  I want to open the Vaccinations page and see its state clearly
  So that I know which vaccinations have been recorded for me

  Background:
    Given an authenticated "meditik" application user is on the home page

  Scenario: VACC-001 - Open the Vaccinations page successfully
    When the user navigates to the Vaccinations page
    Then the Vaccinations toolbar and empty-state title are displayed

  Scenario: VACC-002 - Display the correct Vaccinations empty-state text
    Given the user navigates to the Vaccinations page
    When the Vaccinations empty-state title is read
    Then the Vaccinations empty-state text matches the approved copy exactly

  Scenario: VACC-003 - Display the Vaccinations empty-state icon
    Given the user navigates to the Vaccinations page
    When the Vaccinations empty-state icon is located
    Then exactly one Vaccinations empty-state icon is rendered with a loaded image

  Scenario: VACC-014 - Refresh the Vaccinations page
    Given the user navigates to the Vaccinations page
    When the user refreshes the Vaccinations page
    Then the same Vaccinations route and empty state are shown exactly once
