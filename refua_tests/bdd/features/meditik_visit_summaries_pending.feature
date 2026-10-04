@bdd @meditik @visit_summaries
Feature: Visit Summaries workflows awaiting approved clarification
  Pending specifications, not implemented UI or backend coverage.

  Scenario: VSUM-005 - Unauthenticated direct access is blocked
    Given VSUM case "VSUM-005" has approved execution contracts
    Given The browser has no valid authenticated session.
    When The user requests /appointments directly.
    Then Protected Visit Summaries content is not displayed.

  Scenario: VSUM-006 - Visit-summary retrieval API failure is handled safely
    Given VSUM case "VSUM-006" has approved execution contracts
    Given The user is navigating to Visit Summaries and the retrieval service will fail.
    When The page requests visit-summary data.
    Then The page remains stable and does not present failed data as valid.

  Scenario: VSUM-007 - Visit-summary retrieval timeout is handled safely
    Given VSUM case "VSUM-007" has approved execution contracts
    Given The user is navigating to Visit Summaries and the retrieval request will not complete.
    When The request reaches the timeout condition.
    Then The UI remains usable and incomplete content is not presented as complete.

  Scenario: VSUM-009 - Hebrew RTL content renders correctly
    Given VSUM case "VSUM-009" has approved execution contracts
    Given The user is on Visit Summaries with Hebrew localization active.
    When The page renders.
    Then Hebrew page title and empty-state text are readable without clipping or overlap.

  Scenario: VSUM-010 - Interactive controls and empty-state content are accessible
    Given VSUM case "VSUM-010" has approved execution contracts
    Given The user is on Visit Summaries with accessibility inspection enabled.
    When The page accessibility tree is evaluated and keyboard focus is moved through controls.
    Then Each actionable testid has one accessible element and the empty-state title is exposed as readable content.

  Scenario: VSUM-012 - Completed medical encounter results in an available visit summary
    Given VSUM case "VSUM-012" has approved execution contracts
    Given An eligible encounter has completed and the user navigates to Visit Summaries.
    When The approved summary synchronization completes and the page refreshes.
    Then The corresponding visit summary is available exactly once.

  Scenario: VSUM-013 - Failed summary generation does not expose a broken record
    Given VSUM case "VSUM-013" has approved execution contracts
    Given Summary generation has failed and the user navigates to Visit Summaries.
    When The page retrieves the current summary state.
    Then No broken or incomplete summary is presented as valid.

  Scenario: VSUM-014 - Large historical summary volume remains usable
    Given VSUM case "VSUM-014" has approved execution contracts
    Given The user has a boundary-volume dataset and navigates to Visit Summaries.
    When The page loads and the user traverses the available results.
    Then The UI remains usable and records are not duplicated or omitted within the approved loading model.
