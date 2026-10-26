@bdd @meditik @smoke @my_appointments
Feature: Meditik My Appointments / התורים שלי tabbed screen
  As a Meditik user
  I want to view my Upcoming appointments, Waiting Lists and Past appointments
  So that I can track and manage everything scheduled for me

  Background:
    Given an authenticated "meditik" application user is on the home page

  Scenario: APPT-001 - Open My Appointments from Home
    When the user opens My Appointments from the Home widget
    Then the My Appointments page is loaded

  Scenario: APPT-002 - Render My Appointments page shell
    When the user opens My Appointments directly
    Then the My Appointments page shell is fully rendered

  Scenario Outline: An appointment tab displays a valid data state
    When the user opens My Appointments directly
    And the user activates the "<tab>" appointment tab
    Then the "<tab>" appointment panel shows a valid data state

    Examples:
      | tab           |
      | upcoming      |
      | waiting_lists |
      | past          |

  Scenario: APPT-006 - Show Upcoming Appointments as the default context
    When the user opens My Appointments directly
    Then Upcoming Appointments is the initial context with a valid data state

  Scenario: APPT-007 - Validate past appointment cards when present
    When the user opens My Appointments directly
    And the user activates the "past" appointment tab
    Then the past appointment cards are uniquely located when present

  Scenario: APPT-011 - Return to Home using the navbar logo
    Given the user opens My Appointments directly
    When the user activates the appointments navbar logo
    Then the Meditik home page is visible

  Scenario: APPT-013 - Display the Home appointment widget in its current state
    Then the future-appointments home widget shows a valid data state

  Scenario: APPT-022 - Keep the final tab active during rapid switching
    When the user opens My Appointments directly
    And the user rapidly switches between Upcoming, Waiting Lists, Past and Upcoming
    Then the final appointment panel matches the last-activated tab with a valid data state

  Scenario: APPT-023 - Validate every appointment category in its current state
    When the user opens My Appointments directly
    Then every appointment category shows a valid data state

  Scenario: APPT-028 - Render Hebrew RTL in the current data state
    When the user opens My Appointments directly
    Then the appointment tabs render correctly in Hebrew RTL

  Scenario: APPT-032 - Navigate from the Home widget to My Appointments in any data state
    When the user opens My Appointments from the Home widget
    Then Upcoming Appointments is the initial context with a valid data state
