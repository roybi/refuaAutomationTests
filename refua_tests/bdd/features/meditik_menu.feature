@bdd @meditik @smoke @menu
Feature: Meditik side-menu navigation
  As a Meditik user
  I want each supported side-menu destination to open correctly
  So that I can reach my healthcare information and workflows

  Background:
    Given an authenticated "meditik" application user is on the home page

  Scenario Outline: A side-menu destination loads its content
    When the user opens the "<destination>" Meditik side-menu destination
    Then the "<destination>" Meditik destination content is loaded

    Examples:
      | destination          |
      | appointment booking  |
      | all actions           |
      | urgent care           |
      | my appointments       |
      | my requests           |
      | lab results           |
      | medicines             |
      | visit summaries       |
      | exemptions            |
      | sick days             |
      | referrals             |
      | vaccinations          |
      | medical profile       |
      | feedback              |
