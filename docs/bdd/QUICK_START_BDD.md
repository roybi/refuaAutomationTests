# BDD Quick Start (pytest-bdd)

BDD scenarios mirror the pytest sanity suites **1:1 per workbook case** and run on the same shared, authenticated browser tab.

## Layout

```
refua_tests/bdd/
├── conftest.py                 # shared app_session, known_issue handling, Allure step trace
├── features/
│   ├── meditik_<module>.feature            # Ready cases (executable)
│   ├── meditik_<module>_pending.feature    # Pending cases (generated, skipped)
│   └── mainPage.feature                    # Legacy framework smoke feature
├── step_defs/
│   ├── meditikSteps.py         # Shared: bdd_context fixture, Background, home, menu, request forms
│   └── <module>Steps.py        # medicines, myRequests, myAppointments, referrals, scheduling,
│                               # sickDays, vaccinations, medicalProfile, visitSummaries
├── test_meditik_bdd.py         # scenarios() for every Ready feature
├── test_<module>_pending_bdd.py
├── test_workbook_pending_bdd.py
└── test_main_page_bdd.py
```

## Run

```powershell
$env:TEST_ENV = "test"
venv\Scripts\pytest.exe refua_tests\bdd --personal-number <PN>                       # all BDD
venv\Scripts\pytest.exe refua_tests\bdd\test_meditik_bdd.py --personal-number <PN>   # Ready scenarios only
venv\Scripts\pytest.exe refua_tests\bdd -m "meditik and medicines" --personal-number <PN>
venv\Scripts\pytest.exe refua_tests\bdd -m "meditik and not known_issue" --personal-number <PN>
```

Tags: `@bdd @meditik` plus one module tag (`@home`, `@menu`, `@request_forms`, `@my_requests`, `@my_appointments`, `@scheduling`, `@referrals`, `@new_referral`, `@medicines`, `@sick_days`, `@vaccinations`, `@medical_profile`, `@visit_summaries`). `@cprgo` is reserved for a future application. Every tag must be registered in `pytest.ini`.

Each executed Given/When/Then is attached to the Allure result as `BDD scenario action` with its status.

## Adding a Ready case

1. Implement the sanity test in `refua_tests/tests/meditik<Module>Sanity.py` (page object first).
2. Add the scenario to `features/meditik_<module>.feature`, titled with the case id:

   ```gherkin
   Scenario: VSUM-001 - Open the Visit Summaries page
     When the user navigates to the Visit Summaries page
     Then the Visit Summaries toolbar and empty-state title are displayed
   ```

3. Add steps in `step_defs/<module>Steps.py`, reusing the same page object. Steps receive `bdd_context`; keep app-specific steps out of shared files.

   ```python
   @given("the user navigates to the Visit Summaries page")
   @when("the user navigates to the Visit Summaries page")
   def navigate_to_visit_summaries(bdd_context):
       summaries = _summaries(bdd_context)
       summaries.open_direct()
       summaries.wait_until_loaded()
   ```

4. New feature file -> add `scenarios("features/...")` and the step-module import to `test_meditik_bdd.py`.
5. Remove the case from the pending feature and update `docs/setup/TEST_CASE_TRACKER.csv`. To regenerate a pending feature from its catalog:

   ```powershell
   venv\Scripts\python.exe tools\generate_pending_feature.py docs\setup\<MODULE>_CASES.json refua_tests\bdd\features\meditik_<module>_pending.feature --feature-name "<name>" --tags "@bdd @meditik @<module>" --case-label "<PREFIX>"
   ```

Pending cases stay as skipped scenarios with the workbook Clarification Status; never add steps that assert unapproved behaviour. See [WORKBOOK_V2.md](WORKBOOK_V2.md) for the original workbook intake.
