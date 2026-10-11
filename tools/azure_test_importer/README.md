# Upload Test Plan to Azure

Standalone Excel-to-Azure importer. It does not load the application's pytest
fixtures, create medical test data, or depend on `refua-automation-core`.

## One-time setup

1. Merge the updated workflow and uploader into the repository's default branch.
2. Install Python 3.12 (with Tkinter, included in the standard Windows installer)
   and [GitHub CLI](https://cli.github.com/). Clone or download this repository.
3. From the repository root, install the standalone dependencies and sign in to
   GitHub through your browser:

```powershell
py -m pip install -r tools/azure_test_importer/requirements.txt
gh auth login --hostname github.com --web
```

Your GitHub identity must have access to this private repository, permission to
create/delete draft releases and dispatch workflows, and, for live imports,
permission to **create and delete repository Actions secrets**. Repository admin
access is normally required for secret management. A user who can only run
Actions cannot use this per-run PAT transport without an appropriate role.
Authorize the GitHub sign-in for the organization's SSO policy where required.

Each user supplies their own current Azure PAT for each live execution. Its scopes
must include **Work Items: Read & write** and **Test Management: Read & write**,
with project access and the required Azure Test Plans permissions/access level.
Use a short expiry. No shared or permanent Azure PAT secret is used by this flow.

GitHub's Run workflow form has neither a secure PAT field nor a file picker.
Do not put a PAT in that form, a command argument, Excel, source, or chat. The
local uploader has a masked PAT dialog and sends the value to `gh secret set`
over stdin. GitHub stores it as an encrypted repository secret with a unique
`AZURE_IMPORT_PAT_<UPLOAD_ID>` name. The Action selects only that run's secret;
the old shared `AZURE_DEVOPS_PAT` repository secret is not a fallback.
Only use reviewed code and protect the default branch. Contributors able to
change trusted workflow code can potentially access repository secrets.

## Select a file from your PC

Validate first, without an Azure PAT or any Azure requests:

```powershell
py tools/azure_test_importer/local_upload.py
```

For a live import using your personal PAT:

```powershell
py tools/azure_test_importer/local_upload.py --live --plan Visit_Summaries
```

1. Choose the `.xlsx` file in the native file picker. It can remain in Downloads
   or any other local folder; no workbook commit is needed.
2. Review the local validation output and confirmation dialog. The plan defaults
   to the workbook filename with one `AUTO_` prefix unless `--plan` is supplied.
3. In live mode, enter your current Azure PAT in the masked dialog. Cancelling
   either dialog stops before any upload or secret creation. Dry runs never
   request a PAT. An expired PAT must be replaced on the next execution.
4. The uploader creates a temporary draft release, uploads the workbook as
   `workbook.xlsx`, and starts **Upload Test Plan to Azure**. The workbook is not
   committed to Git history. Only the upload ID and non-secret options are sent
   as workflow inputs; the PAT is not part of the release or dispatch payload.
5. In live mode, keep the uploader open. It displays the run URL, waits for the
   Action, and deletes the temporary PAT secret after success or failure.
   The Action independently deletes the draft workbook upload in its cleanup step.

Optional arguments: `--file "C:\path\cases.xlsx"` skips the file picker;
`--sheet Test_Cases`, `--organization ShaharDigital`, `--project MedicalCenter`,
and `--suite "Visit Summaries"` override import options. `--yes` skips the file
confirmation only; it never skips the personal PAT prompt in live mode.
`--ref` selects a branch for dry runs; live PATs are restricted to the repository's
default branch. File size is limited to 20 MB, with a 100 MB expanded-workbook cap.

There are two separate authentications: GitHub CLI authorizes file/secret upload
and workflow execution; the personal Azure PAT authorizes creating/updating Azure
Test Cases. A successful dry run does not validate Azure credentials.

## Cleanup and retries

Cleanup is best-effort, not a token expiry mechanism. If the uploader is killed,
the PC loses power, the job never starts, or GitHub rejects cleanup, temporary
resources may remain. Check **Settings > Secrets and variables > Actions** for
the printed `AZURE_IMPORT_PAT_<UPLOAD_ID>` name and **Releases** for the matching
`azure-import-input-<upload_id>` draft. Delete only your matching resources and
revoke the PAT in Azure DevOps when finished. The workflow token does not have
permission to delete repository secrets; that deletion requires the local user's
GitHub identity. Interrupted runs may already have changed Azure cases.

If workflow dispatch times out, inspect Actions before retrying: GitHub may have
accepted the request. The workbook draft is retained for inspection, but the
temporary PAT cleanup is still attempted. Start a fresh uploader execution to
retry a live import; rerunning an old job will not recreate its deleted secret.
Use stable test IDs to avoid duplicates. No automatic Azure rollback is performed.

## Repository-file validation from GitHub

Existing repository workbooks can still be validated from
**Actions > Upload Test Plan to Azure > Run workflow**. Select the branch and
keep `dry_run` checked. Live imports must use the local uploader with a personal
PAT; there is no shared-secret live mode.

| Input          | Meaning / example                                                                          |
| -------------- | ------------------------------------------------------------------------------------------ |
| `excel_path`   | Repository-relative path for validation, such as `uploads/Visit_Summaries_Test_Cases.xlsx` |
| `upload_id`    | Filled by the local uploader; do not supply together with `excel_path`                     |
| `plan_name`    | `Visit_Summaries` creates/reuses `AUTO_Visit_Summaries`                                    |
| `sheet_name`   | Worksheet name, usually `Test_Cases`                                                       |
| `organization` | Defaults to `ShaharDigital`                                                                |
| `project`      | Defaults to `MedicalCenter`                                                                |
| `suite`        | Optional override; otherwise use Module/Feature from Excel                                 |
| `dry_run`      | Checked by default: validate Excel only, no Azure writes or PAT needed                     |

Review case counts, the plan name, and suites under **Validate workbook**.
Live runs requested by the local uploader also validate before any Azure writes.
Logs show `[CREATED]`, `[UPDATED]`, `[LINKED]`, and a final failure count.

For a harmless workflow smoke test, use
`tools/azure_test_importer/example.xlsx`, plan `Importer_Verification`, sheet
`Test_Cases`, and leave `dry_run` checked. This workbook contains synthetic data.

Paths and filenames are case-sensitive on the hosted Linux runner. Local computer
paths are not available there: use the local uploader, not a Windows path in the
workflow form. The workflow must be on the default branch for
GitHub to show its Run workflow button. Users need workflow-dispatch permissions.

The PAT is scoped to the upload step. Its raw and Basic-auth-encoded forms are
masked in logs. Inputs are passed as arguments, not interpolated into shell
commands. Imports share a concurrency group to avoid simultaneous runs of this
workflow within the repository.

Draft assets are not public releases, but authorized repository users can access
them. Case content can appear in Actions logs. Only upload approved synthetic or
non-sensitive test specifications. Never upload credentials or patient information.
The runner verifies the draft owner and SHA256 checksum before using the workbook;
cleanup refuses published releases, unrelated tags, and other users' drafts.

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
py -m py_compile tools/azure_test_importer/azure_testcase_importer.py tools/azure_test_importer/workflow_runner.py tools/azure_test_importer/local_upload.py
py tools/azure_test_importer/azure_testcase_importer.py tools/azure_test_importer/example.xlsx --plan Importer_Verification --sheet Test_Cases --dry-run
```

Tests generate temporary synthetic workbooks and mock Azure requests. Use
`unittest` as above; do not invoke the application's pytest fixtures for these
standalone tests. The root requirements and application test runner are unchanged.

The workflow calls `workflow_runner.py` for validation, upload, draft cleanup, and
summaries. Tests cover YAML entry points, local file/PAT dialog cancellation,
personal-secret stdin transport and cleanup, ownership/checksum validation,
pagination, exact-run monitoring, and no shared-secret fallback. A real subprocess
test also validates the synthetic sample without a PAT or Azure writes.

For authentication failures, check token expiry/scopes, project access and the
token owner's Azure Test Plans access level. Browser sign-in does not authenticate
this Python script; it reads `AZURE_DEVOPS_PAT` from its process environment.
