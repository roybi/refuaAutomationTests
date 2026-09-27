@bdd @meditik @smoke @my_requests
Feature: Meditik My Requests / הבקשות שלי tabbed screen
  As a Meditik user
  I want to view and navigate my New, Approved and Declined requests
  So that I can track the status of everything I have submitted

  Background:
    Given an authenticated "meditik" application user is on the home page

  Scenario: MYREQ-001 - Open My Requests from Home
    When the user opens My Requests from the Home widget
    Then the My Requests tabs header is visible

  Scenario: MYREQ-002 - Render My Requests page shell
    When the user opens My Requests directly
    Then the My Requests page shell is fully rendered

  Scenario Outline: A request tab displays a valid data state
    When the user opens My Requests directly
    And the user activates the "<tab>" request tab
    Then the "<tab>" request panel shows a valid data state

    Examples:
      | tab      |
      | active   |
      | approved |
      | declined |

  Scenario: MYREQ-006 - Show New Requests as the default context
    When the user opens My Requests directly
    Then New Requests is the initial context with a valid data state

  Scenario: MYREQ-007 - Validate request cards when present without requiring data
    When the user opens My Requests directly
    Then the New Requests panel cards are validated when present

  Scenario: MYREQ-008 - Return to Home using the navbar logo
    Given the user opens My Requests directly
    When the user activates the navbar logo
    Then the Meditik home page is visible

  Scenario Outline: A request panel is validated without assuming its record count
    When the user opens My Requests directly
    And the user activates the "<tab>" request tab
    Then the "<tab>" request panel shows a valid data state

    Examples:
      | tab      |
      | approved |
      | declined |

  Scenario: MYREQ-018 - Keep final tab active during rapid switching
    When the user opens My Requests directly
    And the user rapidly switches between New, Approved, Declined and New
    Then the final request panel matches the last-activated tab with a valid data state

  Scenario: MYREQ-019 - Validate each category in its current data state
    When the user opens My Requests directly
    Then every request category shows a valid data state

  Scenario: MYREQ-023 - Render Hebrew RTL in the current data state
    When the user opens My Requests directly
    Then the request tabs render correctly in Hebrew RTL

  Scenario: MYREQ-026 - Navigate from the Home widget to My Requests
    When the user opens My Requests from the Home widget
    Then New Requests is the initial context with a valid data state

  Scenario: MYREQ-030 - Display the My Requests widget in its current data state
    Then the My Requests home widget shows a valid data state
