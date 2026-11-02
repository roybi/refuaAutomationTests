@bdd @meditik @smoke @scheduling
Feature: Meditik Appointment Scheduling / זימון תורים
  As a Meditik user
  I want to review Upcoming Appointments, Waiting Lists and Past Appointments
  So that I can manage my scheduling and start a new booking

  Background:
    Given an authenticated "meditik" application user is on the home page

  Scenario: APPOINTMENTS-001 - Load Appointment Scheduling
    When the user navigates to Appointment Scheduling
    Then the Appointment Scheduling shell and three appointment tabs are displayed

  Scenario Outline: An appointment category panel becomes active
    When the user navigates to Appointment Scheduling
    And the user selects the "<tab>" appointment tab
    Then the "<tab>" appointment panel is active

    Examples:
      | tab           |
      | upcoming      |
      | waiting_lists |

  Scenario: APPOINTMENTS-004 - Open Past Appointments
    When the user navigates to Appointment Scheduling
    And the user selects the "past" appointment tab
    Then the Past Appointments panel exposes its filter control and booking link
    And the past appointment card and its location information are validated when present

  Scenario: APPOINTMENTS-011 - Upcoming Appointments empty state
    Given the user navigates to Appointment Scheduling
    And the user selects the "upcoming" appointment tab
    Then the "upcoming" panel shows a scoped empty-state icon and title

  Scenario: APPOINTMENTS-012 - Waiting Lists empty state
    Given the user navigates to Appointment Scheduling
    And the user selects the "waiting_lists" appointment tab
    Then the "waiting_lists" panel shows a scoped empty-state title

  Scenario: APPOINTMENTS-014 - Panel-scoped shared empty-state title
    When the user navigates to Appointment Scheduling
    And the user switches between Upcoming Appointments and Waiting Lists
    Then each shared empty-state locator resolves to exactly one match

  Scenario: APPOINTMENTS-017 - Complete appointment category navigation
    When the user navigates to Appointment Scheduling
    And the user visits all three appointment tabs in sequence
    Then exactly one appointment panel is active with category-correct data at each step
