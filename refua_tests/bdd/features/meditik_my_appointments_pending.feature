@bdd @meditik @my_appointments
Feature: My Appointments workflows awaiting approved clarification
  Pending specifications, not implemented UI or backend coverage.

  Scenario: APPT-008 - Open the new-appointment entry from Past Appointments
    Given APPT case "APPT-008" has approved execution contracts
    Given the authenticated user is on My Appointments
    When the user opens Past Appointments and activates meditik-appointments-link-book-appointment
    Then the configured appointment-booking destination opens

  Scenario: APPT-009 - Open the Past Appointments filter
    Given APPT case "APPT-009" has approved execution contracts
    Given the authenticated user is on Past Appointments in either valid data state
    When the user activates meditik-filter-btn-open
    Then the filter UI opens and displays its filter context

  Scenario: APPT-010 - Expand the My Appointments Speed Dial
    Given APPT case "APPT-010" has approved execution contracts
    Given My Appointments is visible in any valid data state
    When the user activates meditik-speed-dial-btn-fab
    Then the quick-actions container expands

  Scenario: APPT-012 - Open hamburger navigation
    Given APPT case "APPT-012" has approved execution contracts
    Given My Appointments is visible in any valid data state
    When the user activates meditik-navbar-btn-hamburger
    Then the shared navigation opens

  Scenario: APPT-014 - Use the Home appointment widget action
    Given APPT case "APPT-014" has approved execution contracts
    Given the Home appointment widget has loaded in either valid state
    When the user uses the available scoped navigation action
    Then the configured My Appointments or booking destination opens according to the rendered state

  Scenario: APPT-015 - Protect unauthenticated direct access
    Given APPT case "APPT-015" has approved execution contracts
    Given no valid authenticated session exists
    When the user navigates directly to /zimun-torim
    Then appointment panels and appointment data are not exposed

  Scenario: APPT-016 - Handle Upcoming Appointments API failure
    Given APPT case "APPT-016" has approved execution contracts
    Given the Upcoming Appointments service is configured to return 5xx
    When the user opens My Appointments
    Then the application remains stable and stale appointments are not shown as current

  Scenario: APPT-017 - Handle Waiting Lists timeout
    Given APPT case "APPT-017" has approved execution contracts
    Given the Waiting Lists service is configured to time out
    When the user opens Waiting Lists
    Then content from another tab is not presented as waiting-list data and the app remains stable

  Scenario: APPT-018 - Handle Past Appointments partial response
    Given APPT case "APPT-018" has approved execution contracts
    Given the Past Appointments service returns a controlled incomplete or malformed record
    When the user opens Past Appointments
    Then the application does not crash or present invalid content as complete

  Scenario: APPT-019 - Prevent cross-user appointment exposure
    Given APPT case "APPT-019" has approved execution contracts
    Given owned and foreign-user appointments are prepared because isolation is the test objective
    When the user traverses all appointment categories
    Then only appointments belonging to the authenticated user are exposed

  Scenario: APPT-020 - Reject duplicate past-appointment index locators
    Given APPT case "APPT-020" has approved execution contracts
    Given a controlled render state contains at least two past appointment cards
    When automation collects all past-card testids
    Then each rendered appointment card has a unique data-testid

  Scenario: APPT-021 - Prevent duplicate booking navigation
    Given APPT case "APPT-021" has approved execution contracts
    Given the new-appointment link is available
    When the user activates the link twice rapidly
    Then only one booking context is opened

  Scenario: APPT-024 - Traverse the current Past Appointments collection
    Given APPT case "APPT-024" has approved execution contracts
    Given the authenticated user opens Past Appointments without assuming a record count
    When the user traverses the loaded panel
    Then if records exist all rendered cards remain reachable and unique; otherwise the empty state remains valid

  Scenario: APPT-025 - Use My Appointments on a supported mobile viewport
    Given APPT case "APPT-025" has approved execution contracts
    Given the viewport is set to a supported mobile size and data is not controlled
    When the user opens and traverses My Appointments
    Then navbar, tabs, current content and actions remain reachable without clipping

  Scenario: APPT-026 - Navigate appointment tabs by keyboard
    Given APPT case "APPT-026" has approved execution contracts
    Given My Appointments tabs are visible regardless of panel data
    When the user uses Tab, Shift+Tab, Enter and supported arrow keys
    Then focus is visible and selected state matches the visible panel

  Scenario: APPT-027 - Expose accessible names for interactive controls
    Given APPT case "APPT-027" has approved execution contracts
    Given My Appointments is visible
    When automation inspects the accessibility tree for each available action
    Then each available interactive control exposes an actionable role and non-empty accessible name

  Scenario: APPT-029 - Refresh the selected appointment category safely
    Given APPT case "APPT-029" has approved execution contracts
    Given one appointment category is selected without assuming whether records exist
    When the browser refreshes
    Then the app preserves the selection or returns to the documented default and the resulting data state is valid

  Scenario: APPT-030 - Move an upcoming appointment to Past Appointments
    Given APPT case "APPT-030" has approved execution contracts
    Given an isolated owned upcoming appointment exists because the lifecycle is the test objective
    When the appointment time passes or the backend transitions the same appointment to past and the panels are refreshed
    Then the same business appointment no longer appears as upcoming and appears exactly once in Past Appointments

  Scenario: APPT-031 - Start appointment booking from My Appointments
    Given APPT case "APPT-031" has approved execution contracts
    Given the authenticated user is on My Appointments
    When the user activates the new-appointment link
    Then the appointment-booking flow opens once

  Scenario: APPT-033 - Handle appointment-booking destination failure
    Given APPT case "APPT-033" has approved execution contracts
    Given the booking destination or bootstrap service is configured to fail
    When the user starts appointment booking
    Then a controlled failure state is shown and false booking success is not shown

  Scenario: APPT-034 - Prevent duplicate booking from rapid activation
    Given APPT case "APPT-034" has approved execution contracts
    Given the booking entry is available and request monitoring is enabled
    When the user activates the booking link twice rapidly
    Then at most one booking context or accepted booking request is created
