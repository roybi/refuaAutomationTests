"""Testable entry points for the manual Azure import workflow."""

import argparse
import base64
import json
import os
from pathlib import Path

import azure_testcase_importer as importer


def validate_workbook():
    workspace = Path(os.environ["GITHUB_WORKSPACE"]).resolve()
    supplied_path = Path(os.environ["EXCEL_PATH"])
    excel = (workspace / supplied_path).resolve()
    if supplied_path.is_absolute() or not excel.is_relative_to(workspace):
        raise SystemExit("Excel path must be relative to and inside this repository.")
    if excel.suffix.lower() != ".xlsx" or not excel.is_file():
        raise SystemExit("Excel file not found. Upload an .xlsx file to the selected branch first.")
    arguments = [
        str(excel),
        "--plan", os.environ["PLAN_NAME"],
        "--sheet", os.environ["SHEET_NAME"],
        "--organization", os.environ["AZURE_ORGANIZATION"],
        "--project", os.environ["AZURE_PROJECT"],
    ]
    if os.environ.get("SUITE_NAME", "").strip():
        arguments.extend(["--suite", os.environ["SUITE_NAME"]])
    result = importer.main(arguments + ["--dry-run"])
    if result:
        raise SystemExit(result)
    Path(os.environ["RUNNER_TEMP"], "azure-import-arguments.json").write_text(
        json.dumps(arguments), encoding="utf-8"
    )


def upload_test_plan():
    pat = os.environ.get("AZURE_DEVOPS_PAT", "").strip()
    if not pat:
        raise SystemExit(
            "Missing AZURE_DEVOPS_PAT. Add it in Settings > Secrets and variables > Actions."
        )
    if any(character in pat for character in "\r\n"):
        raise SystemExit("AZURE_DEVOPS_PAT must not contain line breaks.")
    print("::add-mask::" + pat, flush=True)
    print("::add-mask::" + base64.b64encode((":" + pat).encode()).decode(), flush=True)
    os.environ["AZURE_DEVOPS_PAT"] = pat
    arguments = json.loads(
        Path(os.environ["RUNNER_TEMP"], "azure-import-arguments.json").read_text(encoding="utf-8")
    )
    result = importer.main(arguments)
    if result:
        raise SystemExit(result)


def write_summary():
    mode = "Excel validation only; no Azure changes" if os.environ["VALIDATION_ONLY"] == "true" else "Azure import"
    summary = "# Upload Test Plan to Azure\n\n"
    summary += "Mode: " + mode + "\n\n"
    summary += "Status: " + os.environ["JOB_STATUS"] + "\n\n"
    summary += "See the validation/import step logs for case counts, CREATED/UPDATED IDs, and errors.\n"
    with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a", encoding="utf-8") as output:
        output.write(summary)


def main():
    operations = {"validate": validate_workbook, "upload": upload_test_plan, "summary": write_summary}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=operations)
    args = parser.parse_args()
    operations[args.operation]()


if __name__ == "__main__":
    main()