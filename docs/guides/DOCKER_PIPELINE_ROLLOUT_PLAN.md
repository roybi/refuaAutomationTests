# Rollout plan: the test-runner website, Allure reports, and the container build

Reference for details: [DOCKER_PIPELINE.md](DOCKER_PIPELINE.md). Things that need AWS, Kubernetes or a private
registry are deliberately **not** here: they are in [LATER_ACTION_ITEMS.md](LATER_ACTION_ITEMS.md).

## What you get

A website (`refua_service`) that replaces typing
`python run_tests.py --system meditik --tags home --user 4444401 --env test --clean`:

- Dropdowns for **system, suite, tag, user, environment**, a **clean** checkbox, and a live preview of the exact command.
- **Start run** -> the website runs `run_tests.py`, shows the live log, status and pass/fail counts; **Cancel** works.
- **Open Allure report** per run, and `/reports/latest` for the newest. Allure history carries over, so trends cover all runs.
- Every run (parameters, log, raw results, report) is stored on disk and survives restarts.
- The same actions exist as a REST API (`/api/runs` ...) for scripts and scheduled jobs.

The Allure reports are served by the same website; there is no separate Allure server to run.

## Part A - What you can do now (your machine + GitHub only)

### A1. Run the website on your machine (no Docker) - 5 minutes
Prerequisites you already have: the `venv`, Java and the Allure CLI (`generateReport.bat` uses them).

1. One-time: `venv\Scripts\pip.exe install -r requirements-service.txt`
2. Start it: double-click **`runService.bat`** (or `venv\Scripts\python.exe -m uvicorn refua_service.app:app --port 8080`).
   The browser opens http://localhost:8080.
3. Choose parameters -> **Start run** -> watch the log -> **Open Allure report**.
4. Data lives in `.service_data\` (git-ignored). Change it with `set DATA_DIR=D:\refua_data` before starting.
5. The approved users in the dropdown come from `SEED_ALLOWED_PERSONAL_NUMBERS` in `.env.test`.

The run uses your `.env.test` (automation login secret, DB), exactly like a manual `run_tests.py`. You need VPN/network access to
the TEST environment as usual. The website stays up only while that window is open; for "always on" see the later items.

Who can open it: the batch file binds to `127.0.0.1`, so only your machine. To let colleagues use your machine, start uvicorn
with `--host 0.0.0.0` and set `SERVICE_API_TOKEN` (then starting/cancelling runs needs the token; the UI has a field for it).

### A2. Check the Docker image builds on GitHub (no AWS needed)
The workflow `Docker - Build and push to ECR` (`.github/workflows/build-push-ecr.yml`) builds both images and smoke-tests
the result. Without AWS settings it **does not push anything**; it only proves the images build and the website starts.

Steps (repository admin on DigitalIDF/refuaAutomationTests):
1. Make sure the workflow file and `docker/`, `refua_service/`, `.dockerignore`, `.gitattributes`, `requirements-service.txt`
   are on the default branch (`main`); GitHub only lists workflows from the default branch.
2. Settings -> Secrets and variables -> Actions -> **Secrets** -> New repository secret:
   `CORE_REPO_TOKEN` = a token with read access to `DigitalIDF/refuaAutomationCore`
   (same secret the existing `BDD - Run by tag` workflow uses; if it is already there, skip this).
3. Actions -> **Docker - Build and push to ECR** -> Run workflow (leave the fields as they are).
4. Open the run. Expected: all build and smoke-test steps green; the AWS/ECR steps are skipped with the notice
   "AWS is not configured". Failures are explained in DOCKER_PIPELINE.md -> Troubleshooting.

Heads-up: the tests need refua-core >= 2.0.1, which on DigitalIDF is only on branch `feat/meditik-element-scraper`
(`main` is 1.0.1). The workflow builds that branch by default; if you merge it to core `main`, set the repository variable
`CORE_REF=main`.

### A3. Optional: try the container on your machine
Docker Desktop is installed. The public Playwright base image is large (~2 GB) and was very slow on this network, so
prefer A2 (GitHub's runners are fast). If you do want it locally:
```
docker build -f docker/core/Dockerfile -t refua-automation-core <checkout-of-refuaAutomationCore>
docker build -f docker/tests/Dockerfile --build-arg CORE_IMAGE=refua-automation-core -t refua-automation-tests .
docker run --rm -p 8080:8080 -v refua-data:/data -e AUTOMATION_SECRET=... refua-automation-tests
```
(Pass the `.env.test` values as `-e` variables; they are never baked into the image.)

## Part B - Later
Always-on hosting, ECR, Kubernetes, ingress/login, backups, Nexus mirrors and the Allure retention policy:
see [LATER_ACTION_ITEMS.md](LATER_ACTION_ITEMS.md).

## Verification checklist for Part A
1. `runService.bat` opens the page; dropdowns are filled (systems, tags, users, environments).
2. A run with a small tag (e.g. `home`, your user) goes queued -> running -> passed/failed with a live log.
3. **Open Allure report** loads; run twice and the report's trend graph shows both runs.
4. Restart the website: the previous runs and reports are still listed.
5. GitHub workflow is green up to and including the smoke test.
