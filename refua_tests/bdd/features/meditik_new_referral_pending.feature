@bdd @meditik @new_referral
Feature: New Referral Request workflows awaiting approved clarification
  Pending specifications, not implemented UI or backend coverage.

  Scenario: NEW-REFERRAL-001 - Open New Referral Request entry point
    Given NEW-REFERRAL case "NEW-REFERRAL-001" has approved execution contracts
    Given an authorized eligible user is on a supported source page
    When the user opens quick actions
    Then the New Referral Request action is available through the approved action locator contract

  Scenario: NEW-REFERRAL-002 - Navigate to New Referral Request
    Given NEW-REFERRAL case "NEW-REFERRAL-002" has approved execution contracts
    Given quick actions are open and New Referral Request is available
    When the user activates New Referral Request
    Then the approved New Referral Request route and form shell open

  Scenario: NEW-REFERRAL-003 - Enter a valid referral request
    Given NEW-REFERRAL case "NEW-REFERRAL-003" has approved execution contracts
    Given the New Referral Request form is displayed
    When the user completes every mandatory field with valid data
    Then all entered values are accepted and the submission control becomes available

  Scenario: NEW-REFERRAL-004 - Submit a valid New Referral Request
    Given NEW-REFERRAL case "NEW-REFERRAL-004" has approved execution contracts
    Given all mandatory referral fields are valid
    When the user submits the form once
    Then one referral request is accepted and becomes observable in My Requests

  Scenario: NEW-REFERRAL-005 - Verify the submitted request in My Requests
    Given NEW-REFERRAL case "NEW-REFERRAL-005" has approved execution contracts
    Given a valid referral request was submitted
    When the user opens My Requests
    Then the new referral request appears in the Active Requests panel with its submitted state

  Scenario: NEW-REFERRAL-006 - Unauthenticated referral request access
    Given NEW-REFERRAL case "NEW-REFERRAL-006" has approved execution contracts
    Given the user has no valid session
    When a New Referral Request entry point or route is requested
    Then protected referral form data is not exposed

  Scenario: NEW-REFERRAL-007 - Unauthorized referral creation
    Given NEW-REFERRAL case "NEW-REFERRAL-007" has approved execution contracts
    Given the user is authenticated but lacks referral-create permission
    When the user attempts to open or submit New Referral Request
    Then the action or form is unavailable and no request is accepted

  Scenario: NEW-REFERRAL-008 - Mandatory-field validation
    Given NEW-REFERRAL case "NEW-REFERRAL-008" has approved execution contracts
    Given the New Referral Request form is displayed with empty mandatory fields
    When the user attempts to submit
    Then submission is blocked and every missing mandatory field receives approved validation

  Scenario: NEW-REFERRAL-009 - Submission API failure
    Given NEW-REFERRAL case "NEW-REFERRAL-009" has approved execution contracts
    Given the user completed a valid referral form
    When submission returns a server failure
    Then the form remains recoverable and no accepted request is shown

  Scenario: NEW-REFERRAL-010 - Submission timeout
    Given NEW-REFERRAL case "NEW-REFERRAL-010" has approved execution contracts
    Given a valid referral submission is in progress
    When the request exceeds the approved timeout
    Then the UI reaches a controlled state and retry cannot create duplicates

  Scenario: NEW-REFERRAL-011 - Maximum valid field lengths
    Given NEW-REFERRAL case "NEW-REFERRAL-011" has approved execution contracts
    Given the New Referral Request form is displayed
    When the user enters values at each approved maximum length
    Then values are accepted without truncation or corruption

  Scenario: NEW-REFERRAL-012 - Over-maximum field validation
    Given NEW-REFERRAL case "NEW-REFERRAL-012" has approved execution contracts
    Given the form is displayed
    When the user enters a value above an approved maximum
    Then the value is blocked or a specific validation error appears

  Scenario: NEW-REFERRAL-013 - Duplicate referral submission
    Given NEW-REFERRAL case "NEW-REFERRAL-013" has approved execution contracts
    Given a valid referral request is ready
    When the submit action is activated twice rapidly
    Then no more than one referral request is accepted

  Scenario: NEW-REFERRAL-014 - Localized referral form
    Given NEW-REFERRAL case "NEW-REFERRAL-014" has approved execution contracts
    Given the New Referral Request form is available in a supported locale
    When the user switches locale and enters supported localized data
    Then labels, layout, direction, and persisted values follow the approved localization contract

  Scenario: NEW-REFERRAL-015 - Accessible responsive referral request
    Given NEW-REFERRAL case "NEW-REFERRAL-015" has approved execution contracts
    Given the New Referral Request flow is displayed at the minimum supported viewport
    When the user completes the flow using keyboard navigation
    Then all controls remain visible, enabled, accessible, uniquely locatable, and unobstructed

  Scenario: NEW-REFERRAL-016 - Home-to-request business workflow
    Given NEW-REFERRAL case "NEW-REFERRAL-016" has approved execution contracts
    Given the user is on Home
    When the user opens New Referral Request, completes valid data, and submits once
    Then one referral request is created and visible in My Requests

  Scenario: NEW-REFERRAL-017 - Referrals-to-new-request workflow
    Given NEW-REFERRAL case "NEW-REFERRAL-017" has approved execution contracts
    Given the user is on the Referrals page
    When the user starts New Referral Request from quick actions and submits valid data
    Then one request is accepted and appears in My Requests

  Scenario: NEW-REFERRAL-018 - Back navigation from incomplete request
    Given NEW-REFERRAL case "NEW-REFERRAL-018" has approved execution contracts
    Given the user has entered data without submitting
    When the user uses the approved Back navigation
    Then the approved discard or retention behavior occurs and no request is created

  Scenario: NEW-REFERRAL-019 - Refresh incomplete New Referral Request
    Given NEW-REFERRAL case "NEW-REFERRAL-019" has approved execution contracts
    Given a valid incomplete form is displayed
    When the browser refreshes
    Then data retention or clearing follows the approved draft policy

  Scenario: NEW-REFERRAL-020 - Completed referral workflow destination
    Given NEW-REFERRAL case "NEW-REFERRAL-020" has approved execution contracts
    Given a valid referral request is ready
    When submission succeeds
    Then the user reaches the approved completion destination and the request remains visible in My Requests

  Scenario: NEW-REFERRAL-021 - Dependent-field response race
    Given NEW-REFERRAL case "NEW-REFERRAL-021" has approved execution contracts
    Given one field selection triggers dependent data loading
    When the user changes the selection before the first response returns
    Then the form reflects only the latest accepted selection

  Scenario: NEW-REFERRAL-022 - New Referral Request initialization failure
    Given NEW-REFERRAL case "NEW-REFERRAL-022" has approved execution contracts
    Given the user activates New Referral Request
    When required form metadata cannot load
    Then no incomplete actionable form is presented and the user receives approved recovery behavior

  Scenario: NEW-REFERRAL-023 - Submit during asynchronous validation
    Given NEW-REFERRAL case "NEW-REFERRAL-023" has approved execution contracts
    Given a mandatory field validation is still pending
    When the user attempts to submit
    Then submission is blocked until validation resolves successfully

  Scenario: NEW-REFERRAL-024 - Session expiry during submission
    Given NEW-REFERRAL case "NEW-REFERRAL-024" has approved execution contracts
    Given the user completed a valid form and the session expires
    When the user submits
    Then no unauthorized request is accepted and form data handling follows security policy

  Scenario: NEW-REFERRAL-025 - Timeout retry idempotency
    Given NEW-REFERRAL case "NEW-REFERRAL-025" has approved execution contracts
    Given the server accepts a request but the client times out
    When the user retries submission
    Then only one request remains in My Requests

  Scenario: NEW-REFERRAL-026 - Maximum attachment boundary
    Given NEW-REFERRAL case "NEW-REFERRAL-026" has approved execution contracts
    Given the referral form supports attachments
    When the user uploads the maximum approved valid attachment set
    Then all attachments are accepted and remain associated with the request

  Scenario: NEW-REFERRAL-027 - Invalid attachment validation
    Given NEW-REFERRAL case "NEW-REFERRAL-027" has approved execution contracts
    Given the referral form supports attachments
    When the user uploads an invalid file
    Then the file is rejected with an approved accessible validation message

  Scenario: NEW-REFERRAL-028 - Unicode referral data integrity
    Given NEW-REFERRAL case "NEW-REFERRAL-028" has approved execution contracts
    Given the form accepts supported free-text input
    When the user submits approved Unicode and punctuation values
    Then accepted values remain unchanged in the resulting request

  Scenario: NEW-REFERRAL-029 - Refresh during referral submission
    Given NEW-REFERRAL case "NEW-REFERRAL-029" has approved execution contracts
    Given a referral submission is still processing
    When the browser is refreshed
    Then the flow recovers without creating duplicate or ambiguous requests

  Scenario: NEW-REFERRAL-030 - All available source elements smoke flow
    Given NEW-REFERRAL case "NEW-REFERRAL-030" has approved execution contracts
    Given source pages expose quick actions and My Requests exposes referral records
    When the user traverses all source-backed entry and verification points
    Then every available source data-testid is covered with a unique context-aware strategy
