# Workbook V2 Case Intake

Source: `Untitled spreadsheet.xlsx`, Sheet1, 48 cases, received 2026-09-08.
The original protected workbook could not be read. The readable replacement
is the source of the imported requirements.

## Current Status

All 48 business cases are **Blocked**, not implemented workflow coverage.
The pytest adapter and BDD loader register 96 skipped entries. The BDD feature
preserves the source Given/When/Then text, but has no implemented UI steps.
Collection-time skip markers prevent authentication and other fixture setup.
Do not remove those markers until implementing the corresponding assertions,
data setup, cleanup, and step definitions.

`docs/setup/WORKBOOK_CASES.json` retains all 18 source columns and a blocking
reason per case. `docs/setup/TEST_CASE_TRACKER.csv` adds MED-070 through MED-117,
with original workbook IDs in test names and matching pytest/BDD references.
Original tags and detailed actions/expected results remain in the JSON catalog;
the pending BDD feature uses only registered `bdd` and `meditik` tags.

## Approved Decisions

- Target TEST using isolated synthetic data; submissions and cleanup authorized.
- API contracts and data-model mappings are not available. Cases depending on
  them remain blocked. Direct-DB seeding/cleanup for Meditik requests now exists
  (`refua_tests/utils/meditik_seed.py`, `tools/db_seed_meditik.py`) and can unblock
  cases that only needed synthetic request data.
- Undefined business rules are deferred, not inferred from observed behavior.
- Browser-level network interception is approved for failure simulation. It
  must not be presented as real downstream failure or persistence verification.

Every full workbook case requires unavailable contracts, including the home
cases' no-mutation assertions. HOME-004 additionally conflicts with itself:
the action only opens a form, while persistence expects one created request.
Resolve this before asserting a persisted workflow.

## Validation

```powershell
.\venv\Scripts\python.exe -m pytest refua_tests/tests/test_workbook_cases.py refua_tests/bdd/test_workbook_pending_bdd.py -q -o log_cli=false --alluredir=allure/results/workbook -rN
```

Verified: 96 collected, 96 skipped, 0 passed, 0 failed. This validates pending
registration and Gherkin parsing only. No BDD actions execute, so executed-step
Allure attachments cannot yet be verified. Allure results are under
`allure/results/workbook`.

An initial body-level skip attempt triggered the existing autouse session
capture and timed out awaiting login. Moving skips before fixture setup fixed
that validation path. No request submissions or data seeding were performed.
No MCP live inspection was performed; selectors, missing data-testid values,
and live UI behavior remain unverified. No CORE changes were needed for intake.

## Resume

Provide approved synthetic-user setup/cleanup and API/DB contracts, then select
a case from the catalog. Verify the flow and data-testid contract using MCP
Playwright, implement actual pytest assertions and matching BDD steps, update
the tracker status, and run focused pytest/BDD checks with Allure action traces.
