@bdd @meditik @smoke @visit_summaries
Feature: Meditik Visit Summaries / סיכומי ביקור
  As a Meditik user
  I want to open the Visit Summaries page and see its state clearly
  So that I know which visit summaries have been recorded for me

  Background:
    Given an authenticated "meditik" application user is on the home page

  Scenario: VSUM-001 - Open the Visit Summaries page
    When the user navigates to the Visit Summaries page
    Then the Visit Summaries toolbar and empty-state title are displayed

  Scenario: VSUM-002 - Display the Visit Summaries empty-state icon
    Given the user navigates to the Visit Summaries page
    When the Visit Summaries empty-state icon is located
    Then exactly one Visit Summaries empty-state icon is rendered with a loaded image

  Scenario: VSUM-003 - Display the correct Visit Summaries empty-state text
    Given the user navigates to the Visit Summaries page
    When the Visit Summaries empty-state title is read
    Then the Visit Summaries empty-state text matches the approved copy exactly

  Scenario: VSUM-004 - Visit Summaries quick-actions control is available
    Given the user navigates to the Visit Summaries page
    When the Visit Summaries quick-actions control is located
    Then the Visit Summaries quick-action trigger, FAB and add icon are each present once and enabled

  Scenario: VSUM-008 - Zero-result dataset renders the complete empty state
    Given the user navigates to the Visit Summaries page
    When the Visit Summaries empty dataset is processed
    Then the Visit Summaries empty state is complete with no phantom record

  Scenario: VSUM-011 - Reach Visit Summaries through application navigation
    When the user opens application navigation and selects Visit Summaries
    Then the Visit Summaries toolbar and empty-state title are displayed
    And the Visit Summaries empty-state text matches the approved copy exactly
