@bdd @meditik @smoke @home
Feature: Meditik home dashboard and quick actions
  As a Meditik user
  I want the home dashboard and its quick actions to work
  So that I can reach my medical information and requests

  Background:
    Given an authenticated "meditik" application user is on the home page

  Scenario: Home dashboard widgets are displayed
    Then the Meditik home widgets are displayed

  Scenario: Home speed dial provides its actions
    Then the Meditik home speed dial provides its actions

  Scenario: Doctor request opens All Actions
    When the user opens the doctor request call to action
    Then the All Actions page is displayed

  Scenario: Last update time is displayed
    Then the last update timestamp is displayed

  Scenario Outline: A dashboard widget navigates to its destination
    When the user opens the "<widget>" home widget
    Then the browser is on "<path>"

    Examples:
      | widget       | path           |
      | requests     | /user-requests |
      | appointments | /zimun-torim   |
      | referrals    | /referrals     |
      | medicines    | /medicines     |
      | exemptions   | /exemptions    |

  Scenario Outline: A content page provides speed-dial actions
    When the user opens the Meditik content page "<path>"
    Then that page provides the expected speed-dial actions

    Examples:
      | path           |
      | /user-requests |
      | /zimun-torim   |
      | /medicines     |
      | /referrals     |
      | /lab-results   |
      | /sick-days     |
