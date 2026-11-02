@bdd @meditik @vaccinations
Feature: Vaccinations workflows awaiting approved clarification
  Pending specifications, not implemented UI or backend coverage.

  Scenario: VACC-004 - Display and activate the hamburger menu button.
    Given VACC case "VACC-004" has approved execution contracts
    Given The Vaccinations page has loaded.
    When Locate and activate meditik-navbar-btn-hamburger.
    Then The button is unique, visible, enabled, accessible, and responds once.

  Scenario: VACC-005 - Display the logo button and image.
    Given VACC case "VACC-005" has approved execution contracts
    Given The Vaccinations page has loaded.
    When Locate the logo button and logo image.
    Then Both locators are unique and visible; the button is enabled and accessible.

  Scenario: VACC-006 - Open the Quick Actions control.
    Given VACC case "VACC-006" has approved execution contracts
    Given The Vaccinations page has loaded.
    When Activate meditik-speed-dial-btn-fab.
    Then The quick-actions trigger is visible and the action container exposes זימון תור and הפניה חדשה.

  Scenario: VACC-007 - Block direct unauthenticated access to Vaccinations.
    Given VACC case "VACC-007" has approved execution contracts
    Given No authenticated session exists.
    When Navigate directly to /vaccinations.
    Then Protected content is not exposed.

  Scenario: VACC-008 - Handle session expiry while viewing Vaccinations.
    Given VACC case "VACC-008" has approved execution contracts
    Given The Vaccinations page is open with an authenticated session.
    When Expire the session and refresh or trigger a page request.
    Then Protected content is no longer accessible.

  Scenario: VACC-009 - Handle an API 500 during Vaccinations loading.
    Given VACC case "VACC-009" has approved execution contracts
    Given The user is authenticated.
    When Intercept the Vaccinations retrieval call with HTTP 500 and load the page.
    Then The application remains stable and does not display a false successful state.

  Scenario: VACC-010 - Handle a timeout while loading Vaccinations.
    Given VACC case "VACC-010" has approved execution contracts
    Given The user is authenticated.
    When Delay the Vaccinations retrieval beyond the configured timeout.
    Then The application does not hang indefinitely or show unverified data.

  Scenario: VACC-011 - Render Vaccinations correctly in Hebrew RTL.
    Given VACC case "VACC-011" has approved execution contracts
    Given The browser is configured for the Hebrew experience.
    When Open /vaccinations and inspect layout direction and element alignment.
    Then Hebrew text is readable, ordered correctly, and not clipped or overlapped.

  Scenario: VACC-012 - Render Vaccinations at 320x568.
    Given VACC case "VACC-012" has approved execution contracts
    Given A clean browser context uses a 320x568 viewport.
    When Open /vaccinations and inspect all listed locators.
    Then Controls and empty-state content remain visible, reachable, and non-overlapping.

  Scenario: VACC-013 - Validate accessibility of Vaccinations navigation controls.
    Given VACC case "VACC-013" has approved execution contracts
    Given The Vaccinations page has loaded.
    When Tab through controls and inspect accessible names, roles, focus, and activation.
    Then Every interactive locator is unique, focusable, visible, enabled, and keyboard-activatable.

  Scenario: VACC-015 - Navigate from Vaccinations Quick Actions to appointment booking.
    Given VACC case "VACC-015" has approved execution contracts
    Given The user is on the Vaccinations page.
    When Open Quick Actions and select זימון תור.
    Then The supported appointment-booking destination or flow opens exactly once.

  Scenario: VACC-016 - Navigate through the application menu to Vaccinations.
    Given VACC case "VACC-016" has approved execution contracts
    Given The user is on an authenticated application page.
    When Open the hamburger menu and select חיסונים.
    Then The /vaccinations route opens and the Vaccinations empty state displays.

  Scenario: VACC-017 - Prevent duplicate navigation from rapid repeated selection.
    Given VACC case "VACC-017" has approved execution contracts
    Given The menu is open and Vaccinations is selectable.
    When Activate the Vaccinations entry multiple times rapidly.
    Then Only one effective route transition and one stable page instance result.

  Scenario: VACC-018 - Open Vaccinations while the backend is unavailable.
    Given VACC case "VACC-018" has approved execution contracts
    Given The user starts from an authenticated application page.
    When Make the Vaccinations backend unavailable and navigate to the module.
    Then The application remains stable and does not show fabricated vaccination records.

  Scenario: VACC-019 - Render and use Vaccinations across the browser matrix.
    Given VACC case "VACC-019" has approved execution contracts
    Given A clean authenticated context exists in each browser.
    When Open /vaccinations, verify page elements, and open Quick Actions in each browser.
    Then The same visible, accessible, and stable behavior is observed in supported browsers.

  Scenario: VACC-020 - Render and use Vaccinations across viewport sizes.
    Given VACC case "VACC-020" has approved execution contracts
    Given A clean authenticated context exists for each viewport.
    When Open /vaccinations and open Quick Actions at each viewport.
    Then All key elements remain visible, accessible, and non-overlapping, and the control responds once.
