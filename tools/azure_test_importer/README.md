# Upload Test Plan to Azure

Standalone Excel-to-Azure importer. It does not load the application's pytest
fixtures, create medical test data, or depend on `refua-automation-core`.

## One-time setup

In this repository, open **Settings > Secrets and variables > Actions > New
repository secret**. Set the name to `AZURE_DEVOPS_PAT` and enter a fresh Azure
DevOps PAT as its value. The token needs **Work Items: Read & write**, **Test
Management: Read & write**, and access to the organization/project. The token
owner also needs the appropriate Azure Test Plans permissions and access level.

GitHub has no secure password input in the Run workflow form. Do not paste a PAT
into workflow inputs, Excel, source code, or logs. Only enter it in the secret UI.
This secret is shared by authorized workflow users, not supplied per run.
Restrict workflow/code changes to trusted contributors and use a protected branch
for live imports. Do not execute untrusted branches with repository secrets.

## Run from GitHub

1. Upload an `.xlsx` file using **Code > Add file > Upload files**. Commit it to
   the branch you will run. Any filename is accepted, including spaces. An
   `uploads/` folder is optional.
2. Open **Actions > Upload Test Plan to Azure > Run workflow**.
3. Select the branch containing your file and enter:

| Input | Meaning / example |
| --- | --- |
| `excel_path` | Repository-relative path, such as `uploads/Visit_Summaries_Test_Cases.xlsx` |
| `plan_name` | `Visit_Summaries` creates/reuses `AUTO_Visit_Summaries` |
| `sheet_name` | Worksheet name, usually `Test_Cases` |
| `organization` | Defaults to `ShaharDigital` |
| `project` | Defaults to `MedicalCenter` |
| `suite` | Optional override; otherwise use Module/Feature from Excel |
| `dry_run` | Checked by default: validate Excel only, no Azure writes or PAT needed |

4. Run once with `dry_run` checked. Review the case count, plan name, and suites
   under **Validate workbook**. This does not verify Azure credentials.
5. Run again with `dry_run` unchecked for a live import. Every live run first
   validates the workbook. Logs show `[CREATED]`, `[UPDATED]`, `[LINKED]`, and a
   final failure count. A partially failed import has no automatic rollback.

For a harmless workflow smoke test, use
`tools/azure_test_importer/example.xlsx`, plan `Importer_Verification`, sheet
`Test_Cases`, and leave `dry_run` checked. This workbook contains synthetic data.

Paths and filenames are case-sensitive on the hosted Linux runner. Local computer
paths are not available there. The workflow must be on the default branch for
GitHub to show its Run workflow button. Users need workflow-dispatch permissions.

The PAT is scoped to the upload step. Its raw and Basic-auth-encoded forms are
masked in logs. Inputs are passed as arguments, not interpolated into shell
commands. Imports share a concurrency group to avoid simultaneous runs of this
workflow within the repository.

Committed workbooks remain in Git history, and case content can appear in Actions
logs. Only upload approved synthetic/non-sensitive test specifications. Never
commit credentials or patient information.

## Matching and updates

- New plans get one `AUTO_` prefix. Matching existing prefixed plans are reused
  case-insensitively and are not renamed.
- A supplied `TC_ID` is matched across the Azure project by an exact tag or an
  existing `[TC_ID]` title prefix. A match is updated using its existing Azure ID;
  otherwise a new case is created. Without `TC_ID`, the exact title is used.
- Matches are project-wide, not restricted to a suite/plan. Updates affect the
  shared work item, including other plans that link to it.
- Duplicate Excel IDs or multiple matching Azure cases cause an error. Blank
  optional fields are not cleared. Tags are replaced with workbook tags plus ID.
- Changed module names add links to the new suite, without removing old links.
- Regenerated or renumbered IDs are not stable identities. Do not reuse an ID for
  a different scenario. Topic-plus-scenario/fuzzy matching is not implemented.
  If both title and ID change, automatic identification is not possible.

## Local development

Run these commands from the repository root with Python 3.12:

```powershell
py -m pip install -r tools/azure_test_importer/requirements-dev.txt
py -m unittest discover -s tools/azure_test_importer -p test_azure_testcase_importer.py -v
py -m py_compile tools/azure_test_importer/azure_testcase_importer.py
py tools/azure_test_importer/azure_testcase_importer.py tools/azure_test_importer/example.xlsx --plan Importer_Verification --sheet Test_Cases --dry-run
```

Tests generate temporary synthetic workbooks and mock Azure requests. Use
`unittest` as above; do not invoke the application's pytest fixtures for these
standalone tests. The root requirements and application test runner are unchanged.

For authentication failures, check token expiry/scopes, project access and the
token owner's Azure Test Plans access level. Browser sign-in does not authenticate
this Python script; it reads `AZURE_DEVOPS_PAT` from its process environment.