"""Choose a local workbook, upload it temporarily, and dispatch the Azure workflow."""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
import zipfile
from pathlib import Path
from urllib.parse import quote

import azure_testcase_importer as importer

DEFAULT_REPOSITORY = "DigitalIDF/refuaAutomationTests"
WORKFLOW = "upload-test-plan-to-azure.yml"
UPLOAD_PREFIX = "azure-import-input-"
MAX_BYTES = 20 * 1024 * 1024
MAX_EXPANDED_BYTES = 100 * 1024 * 1024


def run_gh(arguments, body=None, *, stdin=None, sensitive=False, timeout=180):
    environment = {**os.environ, "GH_HOST": "github.com", "GH_PROMPT_DISABLED": "1"}
    environment.pop("AZURE_DEVOPS_PAT", None)
    try:
        result = subprocess.run(
            ["gh", *arguments], input=stdin if stdin is not None else json.dumps(body) if body is not None else None,
            capture_output=True, text=True, encoding="utf-8", check=True, timeout=timeout, env=environment,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("Install GitHub CLI, then sign in using gh auth login --web.") from exc
    except subprocess.CalledProcessError as exc:
        if sensitive:
            raise RuntimeError("Could not store the temporary PAT secret. Repository secret-management permission is required.") from None
        raise RuntimeError(exc.stderr.strip() or "GitHub CLI request failed.") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("GitHub CLI request timed out; check GitHub before retrying.") from exc
    return result.stdout


def github_json(endpoint, method="GET", body=None):
    arguments = ["api", "--hostname", "github.com", endpoint, "--method", method]
    if body is not None:
        arguments.extend(["--input", "-"])
    output = run_gh(arguments, body)
    return json.loads(output) if output.strip() else None


def validate_repository(repository):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Repository must use the owner/repository format.")
    return repository


def upload_tag(upload_id):
    if not re.fullmatch(r"[0-9a-fA-F]{32}", upload_id):
        raise ValueError("Invalid temporary upload ID.")
    return UPLOAD_PREFIX + upload_id.lower()


def validate_file(path):
    if path.suffix.lower() != ".xlsx" or not path.is_file():
        raise ValueError("Choose an existing .xlsx file.")
    if not 0 < path.stat().st_size <= MAX_BYTES:
        raise ValueError("Workbook must be between 1 byte and 20 MB.")
    with zipfile.ZipFile(path) as archive:
        if sum(entry.file_size for entry in archive.infolist()) > MAX_EXPANDED_BYTES:
            raise ValueError("Expanded workbook exceeds 100 MB.")
    with path.open("rb") as workbook:
        return hashlib.file_digest(workbook, "sha256").hexdigest()


def owned_release(repository, upload_id, actor):
    validate_repository(repository)
    tag = upload_tag(upload_id)
    page = 1
    while True:
        releases = github_json(f"repos/{repository}/releases?per_page=100&page={page}")
        matches = [release for release in releases if release.get("tag_name") == tag]
        if matches:
            if len(matches) != 1:
                raise ValueError("Multiple releases match this temporary upload; cleanup stopped.")
            release = matches[0]
            break
        if len(releases) < 100:
            raise ValueError("Temporary upload draft not found or not accessible to this user.")
        page += 1
    if (not actor or release.get("draft") is not True or release.get("tag_name") != tag
            or release.get("author", {}).get("login", "").casefold() != actor.casefold()):
        raise ValueError("Temporary upload must be a draft owned by the workflow's initiating user.")
    return release


def download_workbook(repository, upload_id, actor, temporary_root):
    release = owned_release(repository, upload_id, actor)
    assets = release.get("assets", [])
    if (len(assets) != 1 or assets[0].get("name") != "workbook.xlsx"
            or assets[0].get("state") != "uploaded"
            or not 0 < assets[0].get("size", 0) <= MAX_BYTES):
        raise ValueError("Temporary upload must contain exactly one workbook.xlsx, at most 20 MB.")
    manifest = json.loads(release.get("body") or "{}")
    checksum = manifest.get("sha256", "")
    if not re.fullmatch(r"[0-9a-f]{64}", checksum):
        raise ValueError("Temporary upload has no valid SHA256 manifest.")
    directory = Path(tempfile.mkdtemp(prefix="azure-import-", dir=temporary_root))
    run_gh(["release", "download", upload_tag(upload_id), "--repo", repository,
            "--pattern", "workbook.xlsx", "--dir", str(directory)])
    workbook = directory / "workbook.xlsx"
    if validate_file(workbook) != checksum:
        raise ValueError("Uploaded workbook checksum does not match; import stopped.")
    return workbook


def delete_upload(repository, upload_id, actor):
    release = owned_release(repository, upload_id, actor)
    github_json(f"repos/{repository}/releases/{int(release['id'])}", method="DELETE")


def personal_secret_name(upload_id):
    upload_tag(upload_id)
    return "AZURE_IMPORT_PAT_" + upload_id.upper()


def wait_for_workflow(repository, ref, upload_id):
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        response = github_json(
            f"repos/{repository}/actions/workflows/{WORKFLOW}/runs"
            f"?event=workflow_dispatch&branch={quote(ref, safe='')}&per_page=100"
        )
        matches = [run for run in response.get("workflow_runs", [])
                   if run.get("display_title") == "Azure import - " + upload_id]
        if len(matches) > 1:
            raise RuntimeError("Multiple workflow runs match this upload; check Actions before retrying.")
        if matches:
            run_id = int(matches[0]["id"])
            print(f"Waiting for https://github.com/{repository}/actions/runs/{run_id}", flush=True)
            run_gh(["run", "watch", str(run_id), "--repo", repository, "--exit-status"], timeout=3600)
            return
        time.sleep(3)
    raise RuntimeError("Workflow run was not found. Check Actions before retrying; the temporary PAT will be removed.")


def publish_workbook(path, repository, ref, inputs, *, pat=None):
    validate_repository(repository)
    checksum = validate_file(path)
    live = inputs.get("dry_run") == "false"
    if live and (not pat or not pat.strip() or any(character in pat for character in "\r\n")):
        raise ValueError("Every live run requires your personal PAT without line breaks.")
    metadata = github_json(f"repos/{repository}")
    if not metadata.get("private"):
        raise ValueError("Local workbook uploads require a private GitHub repository.")
    if live and ref != metadata.get("default_branch"):
        raise ValueError("Personal PATs may only be used with the repository's protected default branch.")
    upload_id = uuid.uuid4().hex.upper()
    secret_name = personal_secret_name(upload_id)
    try:
        if live:
            print(f"Temporary secret: {secret_name}. Keep this uploader open until the run finishes.", flush=True)
            run_gh(["secret", "set", secret_name, "--repo", repository], stdin=pat.strip(), sensitive=True)
        dispatch_workbook(path, repository, ref, inputs, upload_id, checksum)
        if live:
            wait_for_workflow(repository, ref, upload_id)
    finally:
        if live:
            try:
                run_gh(["secret", "delete", secret_name, "--repo", repository])
            except RuntimeError:
                print(f"WARNING: delete temporary secret {secret_name} in {repository} and revoke the PAT.", file=sys.stderr)
    return upload_id


def dispatch_workbook(path, repository, ref, inputs, upload_id, checksum):
    tag = upload_tag(upload_id)
    release = github_json(f"repos/{repository}/releases", method="POST", body={
        "tag_name": tag,
        "target_commitish": ref,
        "name": "Temporary Azure test-case upload " + upload_id,
        "body": json.dumps({"sha256": checksum}),
        "draft": True,
    })
    try:
        with tempfile.TemporaryDirectory() as directory:
            payload = Path(directory, "workbook.xlsx")
            shutil.copyfile(path, payload)
            run_gh(["release", "upload", tag, str(payload), "--repo", repository])
    except (RuntimeError, OSError):
        try:
            github_json(f"repos/{repository}/releases/{int(release['id'])}", method="DELETE")
        except RuntimeError:
            print(f"Cleanup failed. Delete draft release {tag} from {repository}.", file=sys.stderr)
        raise
    try:
        github_json(f"repos/{repository}/actions/workflows/{WORKFLOW}/dispatches", method="POST", body={
            "ref": ref, "inputs": {**inputs, "excel_path": "", "upload_id": upload_id},
        })
    except RuntimeError as exc:
        raise RuntimeError(
            f"Could not confirm workflow dispatch. Check Actions before retrying. "
            f"Draft {tag} was retained; delete it manually if no run was started."
        ) from exc
    print(f"Workflow requested. Upload ID: {upload_id}")
    print(f"https://github.com/{repository}/actions/workflows/{WORKFLOW}")
    print("The workflow deletes the draft upload when it finishes. Check Releases after a cancelled run.")


def choose_file():
    import tkinter
    from tkinter import filedialog

    root = tkinter.Tk()
    root.withdraw()
    try:
        filename = filedialog.askopenfilename(parent=root, title="Select test cases workbook",
                                              filetypes=[("Excel workbook", "*.xlsx")])
        return Path(filename) if filename else None
    finally:
        root.destroy()


def confirm_upload(path, repository, plan, live):
    import tkinter
    from tkinter import messagebox

    root = tkinter.Tk()
    root.withdraw()
    mode = "CREATE or UPDATE Azure test cases" if live else "Validate only; no Azure changes"
    try:
        return messagebox.askyesno(
            "Upload test cases", f"File: {path.name}\nRepository: {repository}\n"
            f"Plan: {plan}\nMode: {mode}\n\nUpload this approved test specification "
            "as a temporary draft-release asset? Do not upload patient data or credentials.", parent=root,
        )
    finally:
        root.destroy()


def prompt_personal_pat():
    import tkinter
    from tkinter import simpledialog

    root = tkinter.Tk()
    root.withdraw()
    try:
        return simpledialog.askstring(
            "Personal Azure PAT", "Enter your current Azure DevOps PAT for this run.\n"
            "It will be stored as a temporary GitHub secret and removed after the run.\n"
            "Work Items and Test Management Read & write permissions are required.",
            show="*", parent=root,
        )
    finally:
        root.destroy()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, help="Local .xlsx path; otherwise open a file picker")
    parser.add_argument("--repo", default=DEFAULT_REPOSITORY)
    parser.add_argument("--ref", default="main", help="Trusted branch containing the updated workflow")
    parser.add_argument("--plan", help="Azure Test Plan name; defaults to the workbook filename")
    parser.add_argument("--sheet", default="Test_Cases")
    parser.add_argument("--organization", default=importer.DEFAULT_ORG)
    parser.add_argument("--project", default=importer.DEFAULT_PROJECT)
    parser.add_argument("--suite", default="")
    parser.add_argument("--live", action="store_true", help="Create or update Azure cases; default is validation only")
    parser.add_argument("--yes", action="store_true", help="Confirm uploading approved data without a dialog")
    args = parser.parse_args(argv)
    try:
        path = args.file or choose_file()
        if path is None:
            print("Cancelled; nothing uploaded.")
            return 0
        path = path.resolve()
        validate_file(path)
        plan = importer.normalize_plan_name(args.plan or path.stem)
        validation = [str(path), "--plan", plan, "--sheet", args.sheet, "--dry-run"]
        if args.suite:
            validation.extend(["--suite", args.suite])
        result = importer.main(validation)
        if result:
            return result
        if not args.yes and not confirm_upload(path, args.repo, plan, args.live):
            print("Cancelled; nothing uploaded.")
            return 0
        pat = prompt_personal_pat() if args.live else None
        if args.live and pat is None:
            print("Cancelled; nothing uploaded.")
            return 0
        publish_workbook(path, args.repo, args.ref, {
            "plan_name": plan, "sheet_name": args.sheet,
            "organization": args.organization, "project": args.project,
            "suite": args.suite, "dry_run": "false" if args.live else "true",
        }, pat=pat)
    except (RuntimeError, ValueError, OSError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())