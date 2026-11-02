@bdd @meditik @sick_days
Feature: Sick Days workflows awaiting approved clarification
  Pending specifications, not implemented UI or backend coverage.

  Scenario: SICK-DAYS-004 - Display and activate the hamburger menu button.
    Given SICK-DAYS case "SICK-DAYS-004" has approved execution contracts
    Given The Sick Days page has loaded.
    When Locate and activate meditik-navbar-btn-hamburger.
    Then The button is unique, visible, enabled, accessible, and responds once.

  Scenario: SICK-DAYS-005 - Display the logo button and image.
    Given SICK-DAYS case "SICK-DAYS-005" has approved execution contracts
    Given The Sick Days page has loaded.
    When Locate the logo button and logo image.
    Then Both locators are unique and visible; the button is enabled and accessible.

  Scenario: SICK-DAYS-006 - Open the Quick Actions control.
    Given SICK-DAYS case "SICK-DAYS-006" has approved execution contracts
    Given The Sick Days page has loaded.
    When Activate meditik-speed-dial-btn-fab.
    Then The quick-actions trigger is visible and the action container exposes אישור ימי מחלה and זימון תור.

  Scenario: SICK-DAYS-007 - Block direct unauthenticated access to Sick Days.
    Given SICK-DAYS case "SICK-DAYS-007" has approved execution contracts
    Given No authenticated session exists.
    When Navigate directly to /sick-days.
    Then Protected content is not exposed.

  Scenario: SICK-DAYS-008 - Handle session expiry while viewing Sick Days.
    Given SICK-DAYS case "SICK-DAYS-008" has approved execution contracts
    Given The Sick Days page is open with an authenticated session.
    When Expire the session and refresh or trigger a page request.
    Then Protected content is no longer accessible.

  Scenario: SICK-DAYS-009 - Handle an API 500 during Sick Days loading.
    Given SICK-DAYS case "SICK-DAYS-009" has approved execution contracts
    Given The user is authenticated.
    When Intercept the Sick Days retrieval call with HTTP 500 and load the page.
    Then The application remains stable and does not display a false successful state.

  Scenario: SICK-DAYS-010 - Handle a timeout while loading Sick Days.
    Given SICK-DAYS case "SICK-DAYS-010" has approved execution contracts
    Given The user is authenticated.
    When Delay the Sick Days retrieval beyond the configured timeout.
    Then The application does not hang indefinitely or show unverified data.

  Scenario: SICK-DAYS-011 - Render Sick Days correctly in Hebrew RTL.
    Given SICK-DAYS case "SICK-DAYS-011" has approved execution contracts
    Given The browser is configured for the Hebrew experience.
    When Open /sick-days and inspect layout direction and element alignment.
    Then Hebrew text is readable, ordered correctly, and not clipped or overlapped.

  Scenario: SICK-DAYS-012 - Render Sick Days at 320x568.
    Given SICK-DAYS case "SICK-DAYS-012" has approved execution contracts
    Given A clean browser context uses a 320x568 viewport.
    When Open /sick-days and inspect all listed locators.
    Then Controls and empty-state content remain visible, reachable, and non-overlapping.

  Scenario: SICK-DAYS-013 - Validate accessibility of Sick Days navigation controls.
    Given SICK-DAYS case "SICK-DAYS-013" has approved execution contracts
    Given The Sick Days page has loaded.
    When Tab through controls and inspect accessible names, roles, focus, and activation.
    Then Every interactive locator is unique, focusable, visible, enabled, and keyboard-activatable.

  Scenario: SICK-DAYS-015 - Navigate from Quick Actions to the Sick Days approval flow.
    Given SICK-DAYS case "SICK-DAYS-015" has approved execution contracts
    Given The user is on a page exposing the Quick Actions control.
    When Open Quick Actions and select אישור ימי מחלה.
    Then The supported Sick Days approval destination or flow opens exactly once.

  Scenario: SICK-DAYS-016 - Navigate through the application menu to Sick Days.
    Given SICK-DAYS case "SICK-DAYS-016" has approved execution contracts
    Given The user is on an authenticated application page.
    When Open the hamburger menu and select ימי מחלה.
    Then The /sick-days route opens and the Sick Days empty state displays.

  Scenario: SICK-DAYS-017 - Prevent duplicate navigation from rapid repeated selection.
    Given SICK-DAYS case "SICK-DAYS-017" has approved execution contracts
    Given The menu is open and Sick Days is selectable.
    When Activate the Sick Days entry multiple times rapidly.
    Then Only one effective route transition and one stable page instance result.

  Scenario: SICK-DAYS-018 - Open Sick Days while the backend is unavailable.
    Given SICK-DAYS case "SICK-DAYS-018" has approved execution contracts
    Given The user starts from an authenticated application page.
    When Make the Sick Days backend unavailable and navigate to the module.
    Then The application remains stable and does not show fabricated records.

  Scenario: SICK-DAYS-019 - Render and use Sick Days across the browser matrix.
    Given SICK-DAYS case "SICK-DAYS-019" has approved execution contracts
    Given A clean authenticated context exists in each browser.
    When Open /sick-days, verify page elements, and open Quick Actions in each browser.
    Then The same visible, accessible, and stable behavior is observed in supported browsers.

  Scenario: SICK-DAYS-020 - Render and use Sick Days across viewport sizes.
    Given SICK-DAYS case "SICK-DAYS-020" has approved execution contracts
    Given A clean authenticated context exists for each viewport.
    When Open /sick-days and open Quick Actions at each viewport.
    Then All key elements remain visible, accessible, and non-overlapping, and the control responds once.
