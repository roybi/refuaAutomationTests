# Rollout plan: test-runner website, Allure reports, images in ECR

Three parts, in order of who can act:

| Part | What | Who | Needs AWS? |
|---|---|---|---|
| A | Run the website on your machine; open Allure reports | You | No |
| B | Check on GitHub that both Docker images build and start | You | No |
| C | Put the images in ECR (and then host them) | You + whoever has AWS access | Yes |

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

## Part B - Check the Docker images build on GitHub (no AWS)

The workflow **Docker - Build and push to ECR** (`.github/workflows/build-push-ecr.yml`) builds both images and smoke-tests
them (starts the website inside the image and checks it). While AWS is not configured it **pushes nothing**.

1. The workflow only appears under Actions when it is on the default branch. Merge to `main`:
   `.github/workflows/build-push-ecr.yml`, `docker/`, `refua_service/`, `.dockerignore`, `.gitattributes`,
   `requirements-service.txt`, `run_tests.py`, `refua_tests/tests/conftest.py`.
2. Repository -> Settings -> Secrets and variables -> Actions -> **Secrets**: `CORE_REPO_TOKEN` = a token that can read
   `DigitalIDF/refuaAutomationCore` (the existing "BDD - Run by tag" workflow already uses it; skip if it is set).
3. Actions -> **Docker - Build and push to ECR** -> Run workflow (leave the fields).
4. Expected: build core, build tests, smoke test are green; the AWS/ECR steps are skipped, with the notice
   "AWS is not configured". Failures: DOCKER_PIPELINE.md -> Troubleshooting.

Heads-up: the tests need refua-core >= 2.0.1, which on DigitalIDF is only on branch `feat/meditik-element-scraper` (`main` is
1.0.1). The workflow builds that branch by default and fails if it resolves to 1.x. After merging it into core `main`, set the
repository variable `CORE_REF=main`.

Optional, not needed: building the images on your own machine. The public Playwright base image is ~2 GB and was very slow
on your network; GitHub's runners are faster.

---

## Part C - Images in ECR (when AWS access is available)

The workflow already contains the push; it switches on by itself once the two variables in C3 exist.
What is pushed: `refua-automation-core` (base) and `refua-automation-tests` (the one you run), tagged with the commit SHA;
`latest` is added on pushes to `main` or when `push_latest` is on.

### C1. Create the two ECR repositories  [AWS admin]
Same region, names exactly (or set `ECR_CORE_REPOSITORY` / `ECR_TESTS_REPOSITORY`):
```
aws ecr create-repository --repository-name refua-automation-core  --region <region>
aws ecr create-repository --repository-name refua-automation-tests --region <region>
```
The workflow does not create them; it checks and fails with a clear message if one is missing.
If you enable "immutable tags", `latest` cannot be moved: run the workflow manually with `push_latest` off.

### C2. Let GitHub log in to AWS  [AWS admin] - choose one
**Role (recommended, no stored keys)**
1. IAM -> Identity providers -> add OpenID Connect: provider URL `https://token.actions.githubusercontent.com`, audience `sts.amazonaws.com`.
2. Create a role (e.g. `refua-github-ecr-push`) with this trust policy:
```json
{ "Version": "2012-10-17", "Statement": [{
  "Effect": "Allow",
  "Principal": { "Federated": "arn:aws:iam::<account-id>:oidc-provider/token.actions.githubusercontent.com" },
  "Action": "sts:AssumeRoleWithWebIdentity",
  "Condition": {
    "StringEquals": { "token.actions.githubusercontent.com:aud": "sts.amazonaws.com" },
    "StringLike":   { "token.actions.githubusercontent.com:sub": "repo:DigitalIDF/refuaAutomationTests:*" } } }] }
```
3. Attach this permission policy:
```json
{ "Version": "2012-10-17", "Statement": [
  { "Effect": "Allow", "Action": "ecr:GetAuthorizationToken", "Resource": "*" },
  { "Effect": "Allow",
    "Action": ["ecr:BatchCheckLayerAvailability","ecr:InitiateLayerUpload","ecr:UploadLayerPart","ecr:CompleteLayerUpload",
               "ecr:PutImage","ecr:BatchGetImage","ecr:GetDownloadUrlForLayer","ecr:DescribeRepositories","ecr:DescribeImages"],
    "Resource": ["arn:aws:ecr:<region>:<account-id>:repository/refua-automation-core",
                 "arn:aws:ecr:<region>:<account-id>:repository/refua-automation-tests"] }] }
```
**Access keys (alternative)**: an IAM user with the same permission policy; store its keys as the GitHub secrets
`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.

### C3. Turn the push on  [repo admin]
Settings -> Secrets and variables -> Actions -> **Variables**: `AWS_REGION` and `AWS_ROLE_ARN`
(with access keys: `AWS_REGION` plus the two secrets). Optional: `ECR_CORE_REPOSITORY`, `ECR_TESTS_REPOSITORY`, `CORE_REF`.
Run the workflow again. Expected: all steps green including "Push core base image" and "Push tests image";
the run summary lists the pushed tags; the images appear in the ECR console.

### C4. Run the image 24/7  [platform team]
Pull `refua-automation-tests:<tag>` on a host that can reach the TEST app and its DB, with:
- the `.env.test` values as environment variables (never inside the image) plus `SERVICE_API_TOKEN`;
- a persistent volume at `/data` (runs, logs, Allure results and reports, seed manifests);
- exactly **one** replica; readiness check `/api/health`; the website on port 8080.
Environment variables, volume layout and a Kubernetes sketch: DOCKER_PIPELINE.md. Protection (VPN/SSO), retention, backups
and updating to a new tag: LATER_ACTION_ITEMS.md.

Check it works: the pod/container is Ready; `/api/health` returns `allure: true`; a run from the page produces a report; after
restarting the container the previous runs and reports are still there.
