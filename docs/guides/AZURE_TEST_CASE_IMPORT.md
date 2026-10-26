# Import Excel Test Cases Into Azure DevOps

The **Azure - Import Excel test cases** GitHub Action runs
[the importer](../../tools/azure_testcase_importer.py), not just its unit tests.
It creates missing Test Cases, updates existing cases matched by `TC_ID`, and
links them to static suites in an `AUTO_` Test Plan. It does not run the medical
application, require CORE, or seed the Meditik database.

## One-Time Setup

1. Merge [the workflow](../../.github/workflows/azure-import-test-cases.yml),
   importer, tests, and dependency file into the repository's default branch.
   GitHub requires a manual workflow to exist on the default branch before its
   **Run workflow** button is available.
2. In Azure DevOps, create a short-lived PAT for the target organization with
   **Work Items: Read & write** and **Test Management: Read & write**. The PAT's
   owner also needs access to the project and permission to manage Test Plans.
3. In GitHub, open **Settings > Environments > New environment**. Create
   `azure-test-import`, or a separate environment per user such as
   `azure-import-roy`. Under that environment's **Environment secrets**, add
   `AZURE_DEVOPS_PAT` and enter the PAT there, never in chat, source, Excel,
   workflow inputs, or an issue. A repository administrator may need to do this.
4. Restrict environment deployment branches to reviewed, trusted branches and
   configure required reviewers where supported. Only authorized users should
   be able to run repository code with these credentials. Do not define a
   repository-wide fallback PAT if each environment must use its own identity.

GitHub workflow inputs are not secret fields. This workflow uses an Environment
secret, not a per-run PAT textbox. The PAT persists until replaced or deleted;
rotate or revoke it after use as appropriate. Repository write access is
required to start the workflow; environment protection may also require approval.

## Upload And Run

1. On GitHub's **Code** tab, select a trusted branch containing the workflow and
   importer. Open `docs/setup`, choose **Add file > Upload files**, upload your
   `.xlsx` workbook, and commit it. For example, upload `Visit_Test_Cases.xlsx`
   and use the input path `docs/setup/Visit_Test_Cases.xlsx`.
2. Open **Actions > Azure - Import Excel test cases > Run workflow**.
3. Choose that same branch and your GitHub Environment. Enter the workbook's
   repository-relative path, Azure organization name, project, Test Plan name,
   and worksheet. Leave **suite** blank to group by `Module` or `Feature`.
4. Leave **dry_run** checked for the first run. This validates Excel without
   accessing Azure or loading the PAT into the import step. A successful dry run
   does **not** verify credentials, Azure permissions, or existing remote cases.
5. After reviewing the dry run and target project, start another run with
   **dry_run unchecked** to create or update the Azure Test Cases.
6. Open the **Import or validate Excel** log for `[CREATED]`, `[UPDATED]`, and
   `[LINKED]` entries and their Azure IDs. Find the resulting `AUTO_` plan in
   Azure DevOps **Test Plans**.

GitHub Actions does not provide a native file-upload input on **Run workflow**.
This workflow accepts a committed workbook path, not a local Windows path, URL,
or email attachment. Uploading a file alone never triggers an import.

Only upload approved test specifications with synthetic data. Do not upload
real patient data, secrets, or confidential workbooks to an unauthorized
repository. Committed workbooks remain in Git history even after deletion, and
case titles, suite names, and failures can appear in Actions logs. No workbook
or import payload is uploaded as an Actions artifact.

## Workbook Format

One row represents one Test Case. The first row contains headers; no title or
merged banner rows should precede it. The default worksheet is `Test Cases`;
`Test_Cases` and case-only differences are also accepted.

| Column                                            | Meaning                                                                                 |
| ------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `TC_ID`                                           | Recommended stable, unique ID, for example `VISIT-001`. Keep it unchanged on re-import. |
| `Scenario` or `Title`                             | Required test title. Rows with no title are ignored.                                    |
| `Feature` or `Module`                             | Required suite column unless the workflow's suite override is supplied.                 |
| `Detailed Automation Steps` or `Steps`            | Actions separated by Excel line breaks.                                                 |
| `Detailed Expected Results` or `Expected Results` | Expected results separated by line breaks.                                              |
| `Preconditions`                                   | Optional setup conditions.                                                              |
| `Priority`                                        | Optional `P0` through `P3`, Azure priority `1` through `4`, or high/medium/low.         |
| `Tags`                                            | Optional semicolon-separated tags; `TC_ID` is also added as a tag.                      |
| `Test Data` or `Description`                      | Optional description containing synthetic data only.                                    |

An example row is `VISIT-001`, `Open visit summaries`, `Visits`, `Open Visits`,
`The visit list is shown`, with priority `P1`. A BDD worksheet may instead use
`When` and `Then / Expected Result` for actions and expected results.

## Re-Imports And Failures

- `AUTO_` is added to the plan name exactly once. Existing matching plans and
  suites are reused.
- Case identity is project-wide, not scoped to a plan or suite. Use IDs unique
  across the target project: reusing an existing ID updates that case even if
  it belongs to another plan. No ID falls back to exact title matching.
- Duplicate Excel IDs are rejected before Azure writes. Ambiguous Azure matches
  are rejected for the affected case. Other rows may still be processed.
- Matching cases get updated titles and steps. Supplied tags replace existing
  tags; blank optional fields do not clear existing values.
- Imports are not atomic. A failure or timeout can leave created plans, suites,
  or updated cases. The run fails on reported row/suite errors. Inspect the log,
  resolve the cause, and rerun using the same stable IDs. No automatic deletion
  or rollback is performed.
- Runs of this workflow are serialized to reduce duplicate-creation races.
  Do not simultaneously import the same project from another repository or CLI.
- HTTP 401/403 usually requires a valid PAT, correct project access, and both
  permission scopes. Organization policy or network restrictions may also
  prevent a GitHub-hosted runner from reaching Azure DevOps.

## Local Validation

Python 3.10+ is required; the workflow uses Python 3.12. Run from the repo root:

```powershell
python -m pip install -r tools/azure-import-requirements.txt
python -m unittest discover -s tools/tests -p test_azure_testcase_importer.py -v
python tools/azure_testcase_importer.py "docs/setup/Visit_Test_Cases.xlsx" --sheet "Test_Cases" --dry-run
```

The unit tests use temporary synthetic workbooks and mocked Azure responses.
No local private workbook, PAT, CORE installation, or browser is needed. Actual
Azure connectivity and writes require a separately approved live import.
