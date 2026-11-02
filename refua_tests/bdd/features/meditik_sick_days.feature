@bdd @meditik @smoke @sick_days
Feature: Meditik Sick Days / ימי מחלה
  As a Meditik user
  I want to open the Sick Days page and see its state clearly
  So that I know which sick days have been recorded for me

  Background:
    Given an authenticated "meditik" application user is on the home page

  Scenario: SICK-DAYS-001 - Open the Sick Days page successfully
    When the user navigates to the Sick Days page
    Then the Sick Days toolbar and empty-state title are displayed

  Scenario: SICK-DAYS-002 - Display the correct Sick Days empty-state text
    Given the user navigates to the Sick Days page
    When the Sick Days empty-state title is read
    Then the Sick Days empty-state text matches the approved copy exactly

  Scenario: SICK-DAYS-003 - Display the Sick Days empty-state icon
    Given the user navigates to the Sick Days page
    When the Sick Days empty-state icon is located
    Then exactly one Sick Days empty-state icon is rendered with a loaded image

  Scenario: SICK-DAYS-014 - Refresh the Sick Days page
    Given the user navigates to the Sick Days page
    When the user refreshes the Sick Days page
    Then the same Sick Days route and empty state are shown exactly once
