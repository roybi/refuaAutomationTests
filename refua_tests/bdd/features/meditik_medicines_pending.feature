@bdd @meditik @medicines
Feature: Medicines and Prescriptions workflows awaiting approved clarification
  Pending specifications, not implemented UI or backend coverage.

  Scenario: MEDICINES-005 - Access Medicines without authentication
    Given MEDICINES case "MEDICINES-005" has approved execution contracts
    Given the user does not have a valid session
    When the Medicines and Prescriptions URL is requested
    Then medicine and prescription information is not exposed and the approved authentication behavior is triggered

  Scenario: MEDICINES-006 - Access Medicines without sufficient authorization
    Given MEDICINES case "MEDICINES-006" has approved execution contracts
    Given the user is authenticated but not authorized to view medicines
    When the user navigates to Medicines and Prescriptions
    Then no medicine or prescription details are exposed

  Scenario: MEDICINES-007 - API failure in My Prescriptions
    Given MEDICINES case "MEDICINES-007" has approved execution contracts
    Given the active-prescriptions service returns a failure
    When the user opens My Prescriptions
    Then the UI does not display incorrect prescription data or create a mutation

  Scenario: MEDICINES-008 - Timeout in Permanent Medicines
    Given MEDICINES case "MEDICINES-008" has approved execution contracts
    Given the permanent-medicines service does not respond within the approved threshold
    When the user opens Permanent Medicines
    Then the UI remains controlled and does not display incorrect data

  Scenario: MEDICINES-010 - Empty Permanent Medicines panel
    Given MEDICINES case "MEDICINES-010" has approved execution contracts
    Given the user has no permanent medicines
    When Permanent Medicines is displayed
    Then the Permanent Medicines panel remains valid, usable, and free of fabricated records

  Scenario: MEDICINES-011 - Empty Previous Prescriptions panel
    Given MEDICINES case "MEDICINES-011" has approved execution contracts
    Given the user has no previous prescriptions
    When Previous Prescriptions is displayed
    Then the Previous Prescriptions panel remains valid, usable, and free of fabricated records

  Scenario: MEDICINES-012 - Accessible tab navigation
    Given MEDICINES case "MEDICINES-012" has approved execution contracts
    Given the Medicines and Prescriptions page is displayed in RTL
    When the user navigates across the tabs using the keyboard and available arrow controls
    Then every tab remains visible, accessible, uniquely locatable, and keyboard-operable

  Scenario: MEDICINES-013 - E2E navigation to Medicines and back
    Given MEDICINES case "MEDICINES-013" has approved execution contracts
    Given the user is at a supported application entry point
    When the user navigates to Medicines, opens My Prescriptions, and selects the logo button
    Then each transition ends in the expected supported page state without medicine-data mutation

  Scenario: MEDICINES-015 - E2E open medicine quick actions
    Given MEDICINES case "MEDICINES-015" has approved execution contracts
    Given the user is on the Medicines and Prescriptions page
    When the user activates the quick-actions floating button
    Then the quick-actions mechanism opens for Get Prescription and Schedule Appointment

  Scenario: MEDICINES-016 - E2E refresh Medicines
    Given MEDICINES case "MEDICINES-016" has approved execution contracts
    Given the user is viewing My Prescriptions
    When the browser is refreshed
    Then the Medicines page reloads into a valid, accessible, and usable state

  Scenario: MEDICINES-017 - E2E tab failure isolation
    Given MEDICINES case "MEDICINES-017" has approved execution contracts
    Given My Prescriptions loads successfully and Permanent Medicines fails
    When the user continues to Previous Prescriptions
    Then the failed request does not contaminate the next panel

  Scenario: MEDICINES-018 - E2E tab request race
    Given MEDICINES case "MEDICINES-018" has approved execution contracts
    Given category responses arrive in a different order from the user selections
    When the user rapidly selects multiple medicine tabs
    Then the active panel corresponds to the last accepted user selection

  Scenario: MEDICINES-019 - E2E duplicate quick-action activation
    Given MEDICINES case "MEDICINES-019" has approved execution contracts
    Given the quick-actions control is closed
    When the user rapidly activates the floating button twice
    Then the UI remains deterministic and no duplicate business action is initiated

  Scenario: MEDICINES-020 - E2E logo navigation failure
    Given MEDICINES case "MEDICINES-020" has approved execution contracts
    Given the user is on the Medicines and Prescriptions page
    When the logo navigation cannot complete
    Then the application remains in a safe usable state without medicine-data loss

  Scenario: MEDICINES-021 - E2E refresh during category loading
    Given MEDICINES case "MEDICINES-021" has approved execution contracts
    Given the Permanent Medicines request is still in progress
    When the user refreshes the browser
    Then the page returns to a complete usable state without partial or duplicated data

  Scenario: MEDICINES-022 - E2E responsive RTL Medicines
    Given MEDICINES case "MEDICINES-022" has approved execution contracts
    Given the Medicines page is displayed in RTL at the minimum supported viewport
    When the user navigates across all tabs and opens quick actions
    Then required controls remain accessible and are not clipped in a way that blocks use

  Scenario: MEDICINES-023 - E2E browser history navigation
    Given MEDICINES case "MEDICINES-023" has approved execution contracts
    Given the user navigated from a supported route to Medicines
    When the user selects browser Back and then Forward
    Then each route returns to an approved usable state without data mutation

  Scenario: MEDICINES-024 - E2E panel-scoped locator uniqueness
    Given MEDICINES case "MEDICINES-024" has approved execution contracts
    Given shared empty-state data-testid values may exist in multiple panels
    When each medicine panel is activated in sequence
    Then every empty-state locator is scoped to the active panel and resolves to exactly one match
