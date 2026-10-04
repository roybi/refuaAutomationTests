@bdd @meditik @smoke @request_forms
Feature: Meditik request forms
  As a Meditik user
  I want request forms to load with usable controls and validation
  So that I can prepare a request safely

  Background:
    Given an authenticated "meditik" application user is on the home page

  Scenario Outline: A request form opens from All Actions
    When the user opens the "<form_path>" request form from All Actions
    Then the request form is loaded

    Examples:
      | form_path                 |
      | /referral-request          |
      | /prescription-request      |
      | /sick-days-request         |
      | /insoles-request           |
      | /referral-answers-request  |
      | /dentist-request           |

  Scenario Outline: A request form shows all required controls
    When the user opens the "<form_path>" request form from All Actions
    Then all required request form controls are visible

    Examples:
      | form_path                 |
      | /referral-request          |
      | /prescription-request      |
      | /sick-days-request         |
      | /insoles-request           |
      | /referral-answers-request  |
      | /dentist-request           |

  Scenario Outline: A request form exposes interactive input controls
    When the user opens the "<form_path>" request form from All Actions
    Then non-submit request form controls are interactive

    Examples:
      | form_path                 |
      | /referral-request          |
      | /prescription-request      |
      | /sick-days-request         |
      | /insoles-request           |
      | /referral-answers-request  |
      | /dentist-request           |

  Scenario Outline: A request form displays all required content
    When the user opens the "<form_path>" request form from All Actions
    Then all required request form content is displayed

    Examples:
      | form_path                 |
      | /referral-request          |
      | /prescription-request      |
      | /sick-days-request         |
      | /insoles-request           |
      | /referral-answers-request  |
      | /dentist-request           |

  Scenario Outline: A request form accepts a valid phone number
    When the user opens the "<form_path>" request form from All Actions
    Then the request form accepts a valid phone number

    Examples:
      | form_path                 |
      | /referral-request          |
      | /prescription-request      |
      | /sick-days-request         |
      | /insoles-request           |
      | /referral-answers-request  |
      | /dentist-request           |

  @known_issue
  Scenario Outline: A request form rejects an invalid phone number
    When the user opens the "<form_path>" request form from All Actions
    Then the request form rejects an invalid phone number

    Examples:
      | form_path                 |
      | /referral-request          |
      | /prescription-request      |
      | /sick-days-request         |
      | /insoles-request           |
      | /referral-answers-request  |
      | /dentist-request           |

  Scenario Outline: A request form supports its additional controls
    When the user opens the "<form_path>" request form from All Actions
    Then the request form additional controls are usable

    Examples:
      | form_path         |
      | /sick-days-request |
      | /dentist-request   |

  Scenario: Urgent Care opens from All Actions
    When the user opens Urgent Care from All Actions
    Then the Urgent Care page is loaded

  Scenario: Prescription opens from the speed dial
    When the user opens the prescription request from the speed dial
    Then the prescription request form is loaded
