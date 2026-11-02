@bdd @meditik
Feature: Workbook v2 workflows awaiting approved contracts
  Pending specifications, not implemented UI or backend coverage.

  Scenario: HOME-001 - Display personalized Meditik home and supported navigation
    Given workbook case "HOME-001" has approved execution contracts
    Given an eligible authenticated user enters Meditik
    When the home page finishes loading
    Then the home page shows the user context and supported navigation areas.

  Scenario: REFERRAL-001 - Submit a new referral request
    Given workbook case "REFERRAL-001" has approved execution contracts
    Given the user opens the new referral request form
    When valid referral request data is entered and submitted
    Then the request is accepted for processing and the UI presents the resulting state.

  Scenario: RX-001 - Submit a prescription request for one medicine
    Given workbook case "RX-001" has approved execution contracts
    Given the user opens the prescription request form
    When one valid medicine and valid request details are submitted
    Then the prescription request is accepted for processing.

  Scenario: REFUND-001 - Open and submit a monetary reimbursement request
    Given workbook case "REFUND-001" has approved execution contracts
    Given the user selects the monetary reimbursement action
    When valid request details are submitted
    Then a monetary reimbursement request, not a referral-use confirmation request, is initiated.

  Scenario: INSOLES-001 - Submit an insole issuance request
    Given workbook case "INSOLES-001" has approved execution contracts
    Given the user opens the insole request form
    When a network is selected, details are entered, the declaration is checked, and the request is submitted
    Then the request is accepted for processing.

  Scenario: FORM119-001 - Submit a complete Form 119 request
    Given workbook case "FORM119-001" has approved execution contracts
    Given the user opens the Form 119 request
    When all specified visit fields, details, attachment, and declaration are supplied and submitted
    Then the request is accepted for processing.

  Scenario: SICK-001 - Submit a sick-leave approval request
    Given workbook case "SICK-001" has approved execution contracts
    Given the user opens the sick-leave approval form
    When valid dates, details, phone and attachment data are submitted
    Then the request is accepted for processing.

  Scenario: DOCTOR-001 - Submit a new doctor-contact request
    Given workbook case "DOCTOR-001" has approved execution contracts
    Given the user opens the doctor-contact request
    When valid details and attachment data are submitted
    Then the request is accepted for processing.

  Scenario: HOME-002 - Reject unauthenticated access to Meditik
    Given workbook case "HOME-002" has approved execution contracts
    Given the user is at the relevant Meditik entry point
    When attempt to enter Meditik without a valid authenticated session
    Then invalid access or submission is blocked and no unintended record is created.

  Scenario: REFERRAL-002 - Prevent referral submission when required data is missing
    Given workbook case "REFERRAL-002" has approved execution contracts
    Given the user is at the relevant Meditik entry point
    When leave one approved mandatory referral field empty and submit
    Then invalid access or submission is blocked and no unintended record is created.

  Scenario: RX-002 - Handle prescription request API failure without duplicate creation
    Given workbook case "RX-002" has approved execution contracts
    Given the user is at the relevant Meditik entry point
    When submit valid prescription data while the request API returns an approved failure response
    Then invalid access or submission is blocked and no unintended record is created.

  Scenario: REFUND-002 - Prevent mixing reimbursement and referral-use confirmation process types
    Given workbook case "REFUND-002" has approved execution contracts
    Given the user is at the relevant Meditik entry point
    When open monetary reimbursement and attempt to submit data intended for referral-use confirmation
    Then invalid access or submission is blocked and no unintended record is created.

  Scenario: INSOLES-002 - Block insole request when declaration is not accepted
    Given workbook case "INSOLES-002" has approved execution contracts
    Given the user is at the relevant Meditik entry point
    When complete the form but leave the declaration unchecked and submit
    Then invalid access or submission is blocked and no unintended record is created.

  Scenario: FORM119-002 - Reject a non-numeric ER visit number
    Given workbook case "FORM119-002" has approved execution contracts
    Given the user is at the relevant Meditik entry point
    When enter non-numeric content in the ER visit number field and submit
    Then invalid access or submission is blocked and no unintended record is created.

  Scenario: SICK-002 - Reject an invalid sick-leave date range
    Given workbook case "SICK-002" has approved execution contracts
    Given the user is at the relevant Meditik entry point
    When set an end date before the start date and submit
    Then invalid access or submission is blocked and no unintended record is created.

  Scenario: DOCTOR-002 - Handle doctor-contact submission timeout without duplicate request
    Given workbook case "DOCTOR-002" has approved execution contracts
    Given the user is at the relevant Meditik entry point
    When submit valid data while the service times out and then observe/retry through the approved UX
    Then invalid access or submission is blocked and no unintended record is created.

  Scenario: HOME-003 - Keyboard and screen-reader navigation of action entry points
    Given workbook case "HOME-003" has approved execution contracts
    Given the user has the specified boundary state
    When navigate all supported action entry points by keyboard and inspect accessible names/states
    Then the UI and process follow an explicit approved rule without truncation, ambiguity, or data corruption.

  Scenario: REFERRAL-003 - New referral with empty optional attachment
    Given workbook case "REFERRAL-003" has approved execution contracts
    Given the user has the specified boundary state
    When submit valid referral data without an attachment
    Then the UI and process follow an explicit approved rule without truncation, ambiguity, or data corruption.

  Scenario: RX-003 - Renew multiple prescriptions from the prescription lobby
    Given workbook case "RX-003" has approved execution contracts
    Given the user has the specified boundary state
    When select multiple eligible prescriptions and initiate renewal
    Then the UI and process follow an explicit approved rule without truncation, ambiguity, or data corruption.

  Scenario: REFUND-003 - Open separate referral-use confirmation and monetary reimbursement actions
    Given workbook case "REFUND-003" has approved execution contracts
    Given the user has the specified boundary state
    When open both actions independently and compare their route/form/process type
    Then the UI and process follow an explicit approved rule without truncation, ambiguity, or data corruption.

  Scenario: INSOLES-003 - Insole network list with exactly one available network
    Given workbook case "INSOLES-003" has approved execution contracts
    Given the user has the specified boundary state
    When open the form for a user with one available network
    Then the UI and process follow an explicit approved rule without truncation, ambiguity, or data corruption.

  Scenario: FORM119-003 - Form 119 at date/time boundary
    Given workbook case "FORM119-003" has approved execution contracts
    Given the user has the specified boundary state
    When submit data at an approved minimum/maximum date or time boundary
    Then the UI and process follow an explicit approved rule without truncation, ambiguity, or data corruption.

  Scenario: SICK-003 - Sick-leave request where start and end date are the same
    Given workbook case "SICK-003" has approved execution contracts
    Given the user has the specified boundary state
    When submit a one-day date range
    Then the UI and process follow an explicit approved rule without truncation, ambiguity, or data corruption.

  Scenario: DOCTOR-003 - Doctor-contact request with maximum supported details and attachment size
    Given workbook case "DOCTOR-003" has approved execution contracts
    Given the user has the specified boundary state
    When enter details and attach a file at the approved boundary
    Then the UI and process follow an explicit approved rule without truncation, ambiguity, or data corruption.

  Scenario: HOME-004 - Navigate from home Actions control to a supported request form
    Given workbook case "HOME-004" has approved execution contracts
    Given all required Meditik and downstream services are available
    When the user open the Actions control and select a supported request
    Then The selected action form opens through the supported entry point.

  Scenario: REFERRAL-004 - Renew a past referral from the referral lobby
    Given workbook case "REFERRAL-004" has approved execution contracts
    Given all required Meditik and downstream services are available
    When the user open Referrals > past referrals, choose an eligible referral, and initiate renewal with prefilled editable service/provider values
    Then A renewal request is submitted and linked to the selected past referral.

  Scenario: RX-004 - Renew multiple prescriptions from fixed/past medicines
    Given workbook case "RX-004" has approved execution contracts
    Given all required Meditik and downstream services are available
    When the user select eligible prescriptions in the prescription lobby, review editable prefilled medicine values, and submit renewal
    Then One renewal request represents the selected medicines according to the approved model.

  Scenario: REFUND-004 - Complete referral-use confirmation from referral details
    Given workbook case "REFUND-004" has approved execution contracts
    Given all required Meditik and downstream services are available
    When the user open an eligible referral in My Referrals and submit the referral-use confirmation request
    Then The confirmation flow completes and remains distinct from reimbursement.

  Scenario: INSOLES-004 - Complete insole issuance from Actions to process creation
    Given workbook case "INSOLES-004" has approved execution contracts
    Given all required Meditik and downstream services are available
    When the user open the action, complete all approved fields, and submit
    Then The full user workflow completes once.

  Scenario: FORM119-004 - Complete Form 119 from Actions through persisted process
    Given workbook case "FORM119-004" has approved execution contracts
    Given all required Meditik and downstream services are available
    When the user open Form 119, enter all approved ER visit data, check declaration, attach evidence, and submit
    Then The full Form 119 process starts once with preserved data.

  Scenario: SICK-004 - Complete sick-leave approval from Actions through persisted process
    Given workbook case "SICK-004" has approved execution contracts
    Given all required Meditik and downstream services are available
    When the user open the form, enter the date range, details, phone and attachment, and submit
    Then The full sick-leave process starts once.

  Scenario: DOCTOR-004 - Complete new doctor-contact request from Actions through persisted process
    Given workbook case "DOCTOR-004" has approved execution contracts
    Given all required Meditik and downstream services are available
    When the user open the action, enter details and attachment, and submit
    Then The full doctor-contact process starts once.

  Scenario: HOME-005 - Expired session during navigation to an action
    Given workbook case "HOME-005" has approved execution contracts
    Given the user has valid input but a controlled end-to-end failure condition exists
    When the user expire the session after home load and select an action
    Then the approved failure state is shown and no duplicate or partial successful mutation occurs.

  Scenario: REFERRAL-005 - Duplicate submission of a new referral request
    Given workbook case "REFERRAL-005" has approved execution contracts
    Given the user has valid input but a controlled end-to-end failure condition exists
    When the user double-activate submit or replay the same correlated request
    Then the approved failure state is shown and no duplicate or partial successful mutation occurs.

  Scenario: RX-005 - Prescription downstream service unavailable after submission
    Given workbook case "RX-005" has approved execution contracts
    Given the user has valid input but a controlled end-to-end failure condition exists
    When the user submit valid data while the downstream service is unavailable
    Then the approved failure state is shown and no duplicate or partial successful mutation occurs.

  Scenario: REFUND-005 - Reimbursement submission fails during attachment/process handoff
    Given workbook case "REFUND-005" has approved execution contracts
    Given the user has valid input but a controlled end-to-end failure condition exists
    When the user submit valid reimbursement data while the handoff fails
    Then the approved failure state is shown and no duplicate or partial successful mutation occurs.

  Scenario: INSOLES-005 - Insole request concurrent duplicate submission
    Given workbook case "INSOLES-005" has approved execution contracts
    Given the user has valid input but a controlled end-to-end failure condition exists
    When the user submit the same request concurrently from two browser contexts
    Then the approved failure state is shown and no duplicate or partial successful mutation occurs.

  Scenario: FORM119-005 - Form 119 upload failure after valid field entry
    Given workbook case "FORM119-005" has approved execution contracts
    Given the user has valid input but a controlled end-to-end failure condition exists
    When the user submit with a controlled attachment upload failure
    Then the approved failure state is shown and no duplicate or partial successful mutation occurs.

  Scenario: SICK-005 - Sick-leave API validation rejects the request
    Given workbook case "SICK-005" has approved execution contracts
    Given the user has valid input but a controlled end-to-end failure condition exists
    When the user submit UI-valid data that the API rejects under an approved business rule
    Then the approved failure state is shown and no duplicate or partial successful mutation occurs.

  Scenario: DOCTOR-005 - Doctor-contact service failure and retry
    Given workbook case "DOCTOR-005" has approved execution contracts
    Given the user has valid input but a controlled end-to-end failure condition exists
    When the user submit during a service failure and retry once through approved UX
    Then the approved failure state is shown and no duplicate or partial successful mutation occurs.

  Scenario: HOME-006 - Responsive home and Actions navigation on supported viewport boundaries
    Given workbook case "HOME-006" has approved execution contracts
    Given the workflow is in the specified cross-screen or boundary state
    When the user repeat home/action navigation at approved minimum and maximum supported viewports
    Then the approved state is consistent across UI, process, and persistence with no data leakage or duplicate mutation.

  Scenario: REFERRAL-006 - Extend an active referral from its details page and refresh
    Given workbook case "REFERRAL-006" has approved execution contracts
    Given the workflow is in the specified cross-screen or boundary state
    When the user open an active non-expired referral, initiate extension, submit, refresh, and navigate back
    Then the approved state is consistent across UI, process, and persistence with no data leakage or duplicate mutation.

  Scenario: RX-006 - Prescription renewal containing medicines from fixed and past lists
    Given workbook case "RX-006" has approved execution contracts
    Given the workflow is in the specified cross-screen or boundary state
    When the user select an approved combination across supported lobby tabs and submit
    Then the approved state is consistent across UI, process, and persistence with no data leakage or duplicate mutation.

  Scenario: REFUND-006 - Back navigation between separate reimbursement and referral-use flows
    Given workbook case "REFUND-006" has approved execution contracts
    Given the workflow is in the specified cross-screen or boundary state
    When the user open one flow, navigate back, open the other, and submit only the second
    Then the approved state is consistent across UI, process, and persistence with no data leakage or duplicate mutation.

  Scenario: INSOLES-006 - Insole network availability changes before submission
    Given workbook case "INSOLES-006" has approved execution contracts
    Given the workflow is in the specified cross-screen or boundary state
    When the user open the form, change seeded network availability, then submit the previously selected network
    Then the approved state is consistent across UI, process, and persistence with no data leakage or duplicate mutation.

  Scenario: FORM119-006 - Form 119 refresh/back navigation preserves or clears draft according to approved rule
    Given workbook case "FORM119-006" has approved execution contracts
    Given the workflow is in the specified cross-screen or boundary state
    When the user complete part of the form, refresh or navigate back, and return
    Then the approved state is consistent across UI, process, and persistence with no data leakage or duplicate mutation.

  Scenario: SICK-006 - Sick-leave submission across localization and date-format boundary
    Given workbook case "SICK-006" has approved execution contracts
    Given the workflow is in the specified cross-screen or boundary state
    When the user enter dates using the approved localized UI and submit
    Then the approved state is consistent across UI, process, and persistence with no data leakage or duplicate mutation.

  Scenario: DOCTOR-006 - Doctor-contact duplicate browser-tab submission
    Given workbook case "DOCTOR-006" has approved execution contracts
    Given the workflow is in the specified cross-screen or boundary state
    When the user open the same draft in two tabs and submit both
    Then the approved state is consistent across UI, process, and persistence with no data leakage or duplicate mutation.
