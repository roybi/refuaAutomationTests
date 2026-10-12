@bdd @meditik @smoke @referrals
Feature: Meditik Referrals / הפניות tabbed screen
  As a Meditik user
  I want to review My Referrals, those Waiting for Approval and Past Referrals
  So that I can track every referral issued to me

  Background:
    Given an authenticated "meditik" application user is on the home page

  Scenario: REFERRALS-001 - Successfully load the Referrals page
    When the user navigates to the Referrals page
    Then the Referrals page shell and all three tabs are operational

  Scenario Outline: A referral tab displays its panel
    When the user navigates to the Referrals page
    And the user selects the "<tab>" referral tab
    Then the "<tab>" referral panel is displayed

    Examples:
      | tab              |
      | mine             |
      | waiting_approval |
      | past             |

  Scenario: REFERRALS-009 - My Referrals empty state
    Given the user navigates to the Referrals page
    And the user selects the "mine" referral tab
    Then the "mine" panel shows a scoped empty-state icon and title

  Scenario Outline: A referral category shows its scoped empty-state title
    Given the user navigates to the Referrals page
    And the user selects the "<tab>" referral tab
    Then the "<tab>" panel shows a scoped empty-state title

    Examples:
      | tab              |
      | waiting_approval |
      | past             |

  Scenario: REFERRALS-015 - E2E navigation through all referral states
    When the user navigates to the Referrals page
    And the user walks through every referral category
    Then exactly one referral panel is displayed at each step
