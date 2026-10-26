# Allure Reports

Every pytest run writes raw results to `allure/results/` (`--alluredir` is set in `pytest.ini`; requires `allure-pytest`). The helpers in `refua_tests/reports/` turn them into HTML.

## Quick start

```powershell
.\generateReport.bat   # allure/results -> allure/report, opens it
.\viewReport.bat       # serves allure/report on http://localhost:8000 (avoids file:// CORS blanks)
```

## Modules

| Module                                                  | Purpose                                                                                                                                                       | Needs                                                  |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| `python -m refua_tests.reports.generateReportJava`      | Generate `allure/report` by calling the Allure jar with Java (avoids the npm wrapper bug with spaces in the Windows user path). Used by `generateReport.bat`. | Java + `allure-commandline` installed via npm or Scoop |
| `python -m refua_tests.reports.generateReport`          | Generate `allure/report` via the npm `allure` script                                                                                                          | Node.js + `npm install -g allure-commandline`          |
| `python -m refua_tests.reports.serveAllure`             | `allure serve` (temporary report + server, Ctrl+C to stop)                                                                                                    | Node.js + allure-commandline                           |
| `python -m refua_tests.reports.serveHttp [--port 8001]` | Serve an already generated `allure/report` over HTTP. Used by `viewReport.bat`.                                                                               | Python only                                            |

## Workflow

```powershell
Remove-Item -Recurse -Force allure\results\* -ErrorAction SilentlyContinue   # avoid mixing runs
$env:TEST_ENV = "test"; venv\Scripts\pytest.exe --personal-number <PN>
.\generateReport.bat
.\viewReport.bat
```

What the report contains:

- Pending workbook cases appear as **skipped** with the Clarification Status as reason and the full case JSON attached.
- BDD scenarios attach each executed Given/When/Then as `BDD scenario action`.
- Soft notes (non-fatal label/copy mismatches) appear as warning steps and a summary attachment.

## Troubleshooting

| Symptom                               | Fix                                                                         |
| ------------------------------------- | --------------------------------------------------------------------------- |
| Report opens but is empty / no graphs | Opened via `file://`; use `viewReport.bat` (HTTP)                           |
| "No data available"                   | No results - check `allure/results` exists and `allure-pytest` is installed |
| Old runs in the report                | Clear `allure\results` before running                                       |
| `Port 8000 is already in use`         | `python -m refua_tests.reports.serveHttp --port 8001`                       |
| Allure / Java not found               | Install the missing prerequisite, or switch module per the table above      |
