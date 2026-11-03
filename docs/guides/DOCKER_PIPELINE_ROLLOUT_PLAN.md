# Rollout plan: test-runner website, Allure reports, images in GHCR (ECR pull-through)

Three parts, in order of who can act:

| Part | What | Who | Needs AWS? |
|---|---|---|---|
| A | Run the website on your machine; open Allure reports | You | No |
| B | Build, test and publish both images with GitHub (to ghcr.io) | You | No |
| C | Pull the image through ECR and run it 24/7 | You + platform team | Platform team only |

Reference for details: [DOCKER_PIPELINE.md](DOCKER_PIPELINE.md). Other later items (hosting 24/7, login, backups):
[LATER_ACTION_ITEMS.md](LATER_ACTION_ITEMS.md).

## What the website does
It replaces typing `python run_tests.py --system meditik --tags home --user 4444401 --env test --clean`:

- Dropdowns for **system, suite, tag, user, environment**, a **clean** checkbox, and a preview of the exact command.
- **Start run** -> runs `run_tests.py`, live log, status, pass/fail counts, **Cancel**.
- **Open Allure report** per run, and `/reports/latest`. Allure history carries over between runs (trend graphs).
- Every run (parameters, log, raw results, report) is stored on disk and survives restarts.
- Same actions as a REST API (`/api/runs`, ...) for scripts or scheduled jobs.

Allure reports are served by the same website; there is no separate Allure server.

---

## Part A - Run the website on your machine (no Docker, no AWS)

Prerequisites you already have: the `venv`, Java and the Allure CLI (what `generateReport.bat` uses), `.env.test`, VPN access to TEST.

1. One time: `venv\Scripts\pip.exe install -r requirements-service.txt`
2. Double-click **`runService.bat`** (or `venv\Scripts\python.exe -m uvicorn refua_service.app:app --port 8080`).
   The browser opens http://localhost:8080.
3. Pick system / suite / tag / user / environment -> **Start run** -> watch the log -> **Open Allure report**.
4. Data is kept in `.service_data\` (git-ignored). Use another folder with `set DATA_DIR=D:\refua_data` before starting.
5. The user dropdown comes from `SEED_ALLOWED_PERSONAL_NUMBERS` in `.env.test`.

Notes:
- A run uses your `.env.test` (automation secret, DB) exactly like a manual `run_tests.py`.
  A real run seeds rows in the TEST DB, as it always does.
- The batch file binds to `127.0.0.1` (only your machine). To share it, start uvicorn with `--host 0.0.0.0` and set
  `SERVICE_API_TOKEN` (starting/cancelling then needs the token; the page has a field for it).
- It runs only while the window is open. "Always on" is Part C.

Check it works: the page loads with filled dropdowns; a small run (e.g. tag `home`) goes queued -> running -> passed/failed;
the report opens; after two runs the report's trend shows both; after restarting the site the old runs are still listed.

## Part B - Build, test and publish the images with GitHub (no AWS)

DigitalIDF does not use ECR repositories that you create. You push to **GitHub Container Registry** (`ghcr.io/digitalidf/...`)
and AWS mirrors it automatically (**ECR pull-through cache**), so the workflow needs no AWS role, keys or repositories.

The workflow **Docker - Build and push to GHCR (ECR pull-through)** (`.github/workflows/build-push-image.yml`) builds both images,
smoke-tests the tests image (starts the website inside it, collects all tests), then pushes with the built-in `GITHUB_TOKEN`.

1. The workflow file must be on the default branch (`main`). Merge your pull request.
2. Repository -> Settings -> Secrets and variables -> Actions -> **Secrets**: `CORE_REPO_TOKEN` = a token that can read
   `DigitalIDF/refuaAutomationCore` (fine-grained, Contents: Read-only). Set it with
   `gh secret set CORE_REPO_TOKEN --repo DigitalIDF/refuaAutomationTests`.
3. Actions -> **Docker - Build and push to GHCR (ECR pull-through)** -> Run workflow. Leave "push_images" and "push_latest" on.
   (It also runs by itself on every push to `main` that changes the image, service or tests.)
4. Expected: every step green; the run summary lists the pushed images and tags. They appear in the organization's
   **Packages**: `refua-automation-core` and `refua-automation-tests` under `ghcr.io/digitalidf/refuaautomationtests/`.
5. Tags: the commit SHA, `latest`, and an optional extra tag (e.g. `v1.0.0`) typed into "extra_tag".

Names (all lowercase, as the registry requires):
```
ghcr.io/digitalidf/refuaautomationtests/refua-automation-core:<tag>
ghcr.io/digitalidf/refuaautomationtests/refua-automation-tests:<tag>
```
Heads-up: the tests need refua-core >= 2.0.1, which on DigitalIDF is only on branch `feat/meditik-element-scraper` (`main` is
1.0.1). The workflow builds that branch by default and fails if it resolves to 1.x. After merging it into core `main`, set the
repository variable `CORE_REF=main`.

First publish only: if the package is not visible to the pull-through cache, check the package's access settings
(Packages -> the package -> Package settings -> link it to the repository / give the organization access).

---

## Part C - Pull it through ECR and run it 24/7  [you + platform team]

Anything that runs on AWS uses the pull-through address (the platform team's cache fetches it from ghcr.io on first pull):
```
373007444960.dkr.ecr.il-central-1.amazonaws.com/ghcr/digitalidf/refuaautomationtests/refua-automation-tests:<tag>
```
Use that as the `image:` in the deployment manifest instead of the ghcr.io address.

Run it with:
- the `.env.test` values as environment variables (a Kubernetes Secret, never inside the image) plus `SERVICE_API_TOKEN`;
- a persistent volume at `/data` (runs, logs, Allure results and reports, seed manifests); the container user is `pwuser`
  (set `fsGroup` so the volume is writable);
- exactly **one** replica; readiness check `/api/health`; the website on port 8080;
- network access to the TEST application and its database.

Environment variables, volume layout and a Kubernetes sketch: DOCKER_PIPELINE.md. Protection (VPN/SSO), retention, backups and
updating to a new tag: LATER_ACTION_ITEMS.md.

Check it works: the pod is Ready; `/api/health` returns `allure: true`; a run started from the page produces a report; after
restarting the pod the previous runs and reports are still there.
