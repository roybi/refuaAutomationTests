@bdd @meditik @referrals
Feature: Referrals workflows awaiting approved clarification
  Pending specifications, not implemented UI or backend coverage.

  Scenario: REFERRALS-005 - Access the page without authentication
    Given REFERRALS case "REFERRALS-005" has approved execution contracts
    Given the user does not have a valid session
    When the Referrals URL is accessed
    Then no medical information is exposed and the approved authentication behavior is triggered

  Scenario: REFERRALS-006 - Service failure while loading My Referrals
    Given REFERRALS case "REFERRALS-006" has approved execution contracts
    Given the referrals service returns a failure
    When the user opens My Referrals
    Then the system does not display incorrect information or perform a mutation

  Scenario: REFERRALS-007 - Timeout while loading Waiting for Approval
    Given REFERRALS case "REFERRALS-007" has approved execution contracts
    Given the referrals service exceeds the timeout threshold
    When the user opens the Waiting for Approval tab
    Then the UI does not remain indefinitely blocked and displays the approved behavior

  Scenario: REFERRALS-008 - Access with missing authorization
    Given REFERRALS case "REFERRALS-008" has approved execution contracts
    Given the user is authenticated but not authorized
    When the user accesses the Referrals page
    Then referral information is not exposed

  Scenario: REFERRALS-012 - Basic tab accessibility
    Given REFERRALS case "REFERRALS-012" has approved execution contracts
    Given the Referrals page is displayed in RTL
    When the user navigates between tabs using the keyboard
    Then every tab is accessible, visible, keyboard-operable, and indicates its active state

  Scenario: REFERRALS-013 - E2E entry to Referrals and return to Home
    Given REFERRALS case "REFERRALS-013" has approved execution contracts
    Given the user is on the Home page
    When the user navigates to Referrals, checks My Referrals, and returns using the logo
    Then each transition ends on the correct page without mutation

  Scenario: REFERRALS-014 - E2E open Speed Dial
    Given REFERRALS case "REFERRALS-014" has approved execution contracts
    Given the user is on the Referrals page
    When the user activates the quick-actions button
    Then the action mechanism opens and offers Schedule Appointment and New Referral

  Scenario: REFERRALS-016 - E2E refresh of the Referrals page
    Given REFERRALS case "REFERRALS-016" has approved execution contracts
    Given the user is on My Referrals
    When the user refreshes the browser
    Then the page reloads and displays a valid and accessible state

  Scenario: REFERRALS-017 - E2E tab-failure isolation
    Given REFERRALS case "REFERRALS-017" has approved execution contracts
    Given My Referrals loads and Waiting for Approval fails
    When the user continues to Past Referrals
    Then the failure does not contaminate the next panel

  Scenario: REFERRALS-018 - E2E race between tab requests
    Given REFERRALS case "REFERRALS-018" has approved execution contracts
    Given service responses arrive in a different order than the clicks
    When the user rapidly clicks multiple tabs
    Then the displayed panel corresponds to the last selected tab

  Scenario: REFERRALS-019 - E2E navigation failure from Referrals to Home
    Given REFERRALS case "REFERRALS-019" has approved execution contracts
    Given the user is on the Referrals page
    When clicking the logo does not complete navigation
    Then the system remains in a safe state without data loss

  Scenario: REFERRALS-020 - E2E double-click on quick actions
    Given REFERRALS case "REFERRALS-020" has approved execution contracts
    Given Speed Dial is closed
    When the user rapidly clicks the FAB twice
    Then the UI remains deterministic and no duplicate action is created

  Scenario: REFERRALS-021 - E2E refresh during a request
    Given REFERRALS case "REFERRALS-021" has approved execution contracts
    Given a tab transition is still loading
    When the user refreshes the page
    Then the page returns to a usable state without partial data

  Scenario: REFERRALS-022 - E2E responsive RTL tabs
    Given REFERRALS case "REFERRALS-022" has approved execution contracts
    Given the page is displayed in RTL at a narrow viewport
    When the user navigates through all tabs
    Then every tab remains accessible and is not clipped in a way that blocks use

  Scenario: REFERRALS-023 - E2E browser history
    Given REFERRALS case "REFERRALS-023" has approved execution contracts
    Given the user navigated from Home to Referrals
    When the user selects Back and then Forward
    Then each page loads in a usable state without mutation

  Scenario: REFERRALS-024 - E2E locator uniqueness by panel
    Given REFERRALS case "REFERRALS-024" has approved execution contracts
    Given the same data-testid is used for empty-state titles in multiple panels
    When each panel is activated in turn
    Then the locator scoped to the active panel returns exactly one match
