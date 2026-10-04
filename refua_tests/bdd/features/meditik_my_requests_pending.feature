@bdd @meditik @my_requests
Feature: My Requests workflows awaiting approved clarification
  Pending specifications, not implemented UI or backend coverage.

  Scenario: MYREQ-009 - Open hamburger navigation
    Given MYREQ case "MYREQ-009" has approved execution contracts
    Given My Requests is visible in any valid data state
    When the user activates meditik-navbar-btn-hamburger
    Then the shared application navigation opens

  Scenario: MYREQ-012 - Expand My Requests Speed Dial
    Given MYREQ case "MYREQ-012" has approved execution contracts
    Given My Requests is visible in any valid data state
    When the user activates meditik-speed-dial-btn-fab
    Then the quick-actions container expands

  Scenario: MYREQ-013 - Protect unauthenticated direct access
    Given MYREQ case "MYREQ-013" has approved execution contracts
    Given no valid session exists
    When the user navigates directly to /user-requests
    Then request panels and request records are not exposed

  Scenario: MYREQ-014 - Handle New Requests service failure
    Given MYREQ case "MYREQ-014" has approved execution contracts
    Given the New Requests service is configured to return 5xx
    When the user opens My Requests
    Then the application remains stable and does not present stale records as current

  Scenario: MYREQ-015 - Handle Approved Requests timeout
    Given MYREQ case "MYREQ-015" has approved execution contracts
    Given the Approved Requests service is configured to time out
    When the user opens Approved Requests
    Then active content is not misrepresented as approved content and the app remains stable

  Scenario: MYREQ-016 - Prevent cross-user request exposure
    Given MYREQ case "MYREQ-016" has approved execution contracts
    Given owned and foreign-user requests are prepared because isolation is the test objective
    When the authenticated user traverses the request panels
    Then only owned requests are rendered

  Scenario: MYREQ-017 - Reject duplicate virtual-index locators
    Given MYREQ case "MYREQ-017" has approved execution contracts
    Given a controlled render state contains at least two request cards because uniqueness is the test objective
    When automation collects every card data-testid
    Then each rendered card has a unique data-testid

  Scenario: MYREQ-020 - Traverse the current request collection safely
    Given MYREQ case "MYREQ-020" has approved execution contracts
    Given the authenticated user opens New Requests without assuming a record count
    When the user traverses the loaded panel
    Then if records exist all rendered cards remain reachable and unique; otherwise the empty state remains valid

  Scenario: MYREQ-021 - Use My Requests on the supported mobile viewport
    Given MYREQ case "MYREQ-021" has approved execution contracts
    Given the viewport is configured to the supported mobile size and data is not controlled
    When the user opens and traverses My Requests
    Then navbar, tabs and the current populated or empty state remain reachable without clipping

  Scenario: MYREQ-022 - Navigate request tabs with keyboard
    Given MYREQ case "MYREQ-022" has approved execution contracts
    Given My Requests tabs are visible regardless of panel data
    When the user uses Tab, Shift+Tab, Enter and supported arrow keys
    Then focus is visible and selected state matches the visible panel

  Scenario: MYREQ-024 - Move one request from New to Approved
    Given MYREQ case "MYREQ-024" has approved execution contracts
    Given an isolated owned request exists in New state because the transition is the test objective
    When the same request is approved and the panels are refreshed
    Then the same business request disappears from New and appears exactly once in Approved

  Scenario: MYREQ-025 - Move one request from New to Declined
    Given MYREQ case "MYREQ-025" has approved execution contracts
    Given an isolated owned request exists in New state because the transition is the test objective
    When the same request is declined and the panels are refreshed
    Then the same business request disappears from New and appears exactly once in Declined

  Scenario: MYREQ-027 - Prevent conflicting request states across tabs
    Given MYREQ case "MYREQ-027" has approved execution contracts
    Given a controlled partial status refresh is configured because consistency is the test objective
    When the user traverses all request tabs
    Then the same request is not simultaneously represented in conflicting states

  Scenario: MYREQ-028 - Prevent duplicate My Requests navigation
    Given MYREQ case "MYREQ-028" has approved execution contracts
    Given the user is on Home and the widget is enabled regardless of its data state
    When the user activates the widget arrow twice rapidly
    Then one My Requests page context and one tabs header are rendered

  Scenario: MYREQ-029 - Refresh the selected category safely
    Given MYREQ case "MYREQ-029" has approved execution contracts
    Given Approved Requests is selected without assuming whether records exist
    When the browser refreshes
    Then the app preserves Approved or returns to the documented default; the resulting populated or empty state is valid

  Scenario: MYREQ-031 - Use the Home-widget action in the current state
    Given MYREQ case "MYREQ-031" has approved execution contracts
    Given the My Requests Home widget has finished loading in either valid state
    When the user uses the available scoped navigation action
    Then the configured My Requests or doctor-request destination opens according to the rendered widget state
