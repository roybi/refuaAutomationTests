@bdd @meditik @medical_profile
Feature: Medical Profile workflows awaiting approved clarification
  Pending specifications, not implemented UI or backend coverage.

  Scenario: MEDICAL-PROFILE-002 - Hamburger navigation control is displayed and usable
    Given MEDICAL-PROFILE case "MEDICAL-PROFILE-002" has approved execution contracts
    Given The user is on Medical Profile.
    When The user locates and activates the hamburger menu button.
    Then The hamburger button and icon are visible, and the menu action completes without leaving the application in an invalid state.

  Scenario: MEDICAL-PROFILE-003 - Application logo control is displayed
    Given MEDICAL-PROFILE case "MEDICAL-PROFILE-003" has approved execution contracts
    Given The user is on Medical Profile.
    When The user locates the logo button and logo image.
    Then Both logo elements are visible and the logo button is enabled and accessible.

  Scenario: MEDICAL-PROFILE-005 - Unauthenticated direct access is blocked
    Given MEDICAL-PROFILE case "MEDICAL-PROFILE-005" has approved execution contracts
    Given The browser has no valid authenticated session.
    When The user requests /medical-profile directly.
    Then Protected Medical Profile content is not displayed.

  Scenario: MEDICAL-PROFILE-006 - Medical Profile retrieval failure is handled safely
    Given MEDICAL-PROFILE case "MEDICAL-PROFILE-006" has approved execution contracts
    Given The user is navigating to Medical Profile and retrieval will fail.
    When The page requests Medical Profile data.
    Then The page remains stable and failed data is not presented as valid profile information.

  Scenario: MEDICAL-PROFILE-007 - Medical Profile retrieval timeout is handled safely
    Given MEDICAL-PROFILE case "MEDICAL-PROFILE-007" has approved execution contracts
    Given The user is navigating to Medical Profile and retrieval will not complete.
    When The request reaches the timeout condition.
    Then The UI remains usable and incomplete profile information is not presented as complete.

  Scenario: MEDICAL-PROFILE-008 - Null or empty Medical Profile response is handled without broken content
    Given MEDICAL-PROFILE case "MEDICAL-PROFILE-008" has approved execution contracts
    Given The user is on Medical Profile and the retrieval response contains no profile content.
    When The page processes the response.
    Then The page remains stable and does not display fabricated profile values.

  Scenario: MEDICAL-PROFILE-009 - Hebrew RTL page heading and layout render correctly
    Given MEDICAL-PROFILE case "MEDICAL-PROFILE-009" has approved execution contracts
    Given The user is on Medical Profile with Hebrew localization active.
    When The page renders.
    Then The visible פרופיל רפואי page heading and navigation area render without clipping, overlap, or reversed character order.

  Scenario: MEDICAL-PROFILE-010 - Medical Profile navigation controls are accessible
    Given MEDICAL-PROFILE case "MEDICAL-PROFILE-010" has approved execution contracts
    Given The user is on Medical Profile with accessibility inspection enabled.
    When The accessibility tree and keyboard focus are evaluated for supplied actionable testids.
    Then Each actionable data-testid resolves to one accessible, visible, and enabled element.

  Scenario: MEDICAL-PROFILE-012 - Medical Profile data is displayed after successful retrieval
    Given MEDICAL-PROFILE case "MEDICAL-PROFILE-012" has approved execution contracts
    Given An approved populated profile exists for the authenticated user and the user navigates to Medical Profile.
    When The approved profile retrieval process completes.
    Then The corresponding profile information is presented once and belongs to the authenticated user.

  Scenario: MEDICAL-PROFILE-013 - User cannot receive another user’s Medical Profile
    Given MEDICAL-PROFILE case "MEDICAL-PROFILE-013" has approved execution contracts
    Given User A is authenticated and User B has a distinct profile.
    When A request attempts to retrieve User B profile in User A context.
    Then User B profile information is not displayed to User A.

  Scenario: MEDICAL-PROFILE-014 - Maximum supported Medical Profile payload remains usable
    Given MEDICAL-PROFILE case "MEDICAL-PROFILE-014" has approved execution contracts
    Given The authenticated user has a profile at the supported boundary and navigates to Medical Profile.
    When The profile retrieval and rendering process completes.
    Then The page remains usable and approved profile fields are neither duplicated nor omitted.
