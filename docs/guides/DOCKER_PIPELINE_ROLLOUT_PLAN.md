# Rollout plan: Nexus -> GitHub Action -> ECR -> pod -> web UI -> Allure 24/7

Companion to [DOCKER_PIPELINE.md](DOCKER_PIPELINE.md) (reference). This file is the ordered setup plan.

## Context
The code is already written and pushed (commit a042903 on `royShfiutMeditik`): two Dockerfiles, the single workflow
`.github/workflows/build-push-ecr.yml`, and `refua_service/` (FastAPI backend + one-page web UI + Allure report server).
Nothing has been built or run yet. What is missing is the **operational path**: a click-by-click setup guide, the first
real build, the deployment, and a verified run. This plan lists every operation in order, who does it, and how to verify.

How the pieces answer the requirements:
- **Web page to run tests:** `refua_service/static/index.html` at `http://<host>:8080/`. Dropdowns for system, suite, tag, user,
  env, a `--clean` checkbox, a preview of the exact `run_tests.py ...` command, live log, status, Cancel, Open report.
  The same actions exist as REST (`POST /api/runs` ...) for cron-style callers.
- **Allure 24/7:** the same container serves every generated report from `/data/allure/reports/<run_id>/` (`/reports/latest`,
  `/reports/<id>/`). History is carried between runs, so trends span all runs. No separate Allure server is needed.
- **Persistence:** PVC mounted at `/data` (runs, logs, raw results, reports, seed manifests, HOME).

## Phase 0 - Decisions you must make (blockers)
1. Nexus base image name (Python 3.9+ + Chromium + OS libs) -> repo variable `BASE_IMAGE`.
2. Do pip / apt / Allure CLI downloads also have to come from Nexus? If yes I add build args (`PIP_INDEX_URL`, apt mirror,
   `ALLURE_BASE_URL`) to `docker/tests/Dockerfile`, or you provide an Allure/Java image.
3. Where the pod runs (assumed: Kubernetes/EKS with ECR pull) and how users reach it (ingress/VPN). The service has no
   login; `SERVICE_API_TOKEN` only protects start/cancel.
4. Core ref: tests need refua-core >= 2.0.1, only on `feat/meditik-element-scraper`; merge to core `main` and set `CORE_REF`.

## Phase 1 - AWS (one time, AWS admin)
1. Create ECR repos `refua-automation-core` and `refua-automation-tests` (same region).
2. GitHub OIDC: add the identity provider `token.actions.githubusercontent.com`; create role `refua-github-ecr-push`
   with trust limited to `repo:DigitalIDF/refuaAutomationTests:*` (or `ref:refs/heads/main`) and a policy allowing
   `ecr:GetAuthorizationToken`, `BatchCheckLayerAvailability`, `InitiateLayerUpload`, `UploadLayerPart`,
   `CompleteLayerUpload`, `PutImage`, `DescribeRepositories`, `DescribeImages` on the two repos.
   (Alternative: IAM user keys as secrets `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`.)
3. Cluster nodes' role can pull from ECR.

## Phase 2 - GitHub (one time, repo admin on DigitalIDF/refuaAutomationTests)
Settings -> Secrets and variables -> Actions:
- Variables: `BASE_IMAGE`, `AWS_REGION`, `AWS_ROLE_ARN`; optional `ECR_CORE_REPOSITORY`, `ECR_TESTS_REPOSITORY`, `CORE_REF`.
- Secrets: `CORE_REPO_TOKEN` (read access to DigitalIDF/refuaAutomationCore); only if no OIDC: AWS key pair.
- If Nexus requires login: secrets `NEXUS_USER`, `NEXUS_PASSWORD` + a `docker login` step (I add it once the host is known).
- The workflow file must be on the default branch (`main`) to appear under Actions: merge/cherry-pick
  `.github/workflows/build-push-ecr.yml`, `docker/`, `refua_service/`, `.dockerignore`, `.gitattributes`, `requirements-service.txt`.
- Run: Actions -> "Docker - Build and push to ECR" -> Run workflow (core_ref blank, push_latest on).
  Expected steps: validate -> checkout x2 -> resolve tags -> build core -> build tests -> smoke test (Allure version,
  refua-core version, `--list-systems`, collect-only, service `/api/health`, `/api/options`, UI page) -> AWS login ->
  ECR login -> repo check -> push core -> push tests; the summary lists the pushed tags.
- Failure map is in `docs/guides/DOCKER_PIPELINE.md` (Troubleshooting).

## Phase 3 - First image build locally (optional but recommended before CI)
```
docker build -f docker/core/Dockerfile --build-arg BASE_IMAGE=<nexus image> -t refua-automation-core <core checkout>
docker build -f docker/tests/Dockerfile --build-arg CORE_IMAGE=refua-automation-core -t refua-automation-tests .
docker run --rm -p 8080:8080 -v refua-data:/data -e AUTOMATION_SECRET=... -e ORM_DB_...=... refua-automation-tests
```
Open http://localhost:8080. (Core build context: use `git archive` of the core repo, its working tree has a huge venv.)

## Phase 4 - Deploy (platform/DevOps)
1. Kubernetes Secret `refua-tests-env` with the `.env.test` keys (AUTOMATION_SECRET, ORM_DB_*, SEED_ALLOWED_PERSONAL_NUMBERS,
   MEDITIK_SEED_*, `SERVICE_API_TOKEN`, optional `SERVICE_ALLOWED_USERS`).
2. PVC `refua-tests-data` (RWO, >= 20 GiB; Allure results with screenshots grow, `RETENTION_DAYS` defaults to 30).
3. Deployment: 1 replica, `strategy: Recreate`, `fsGroup: 1000`, mount `/data`, `envFrom` the secret, readiness `/api/health`
   (sketch is in the manual). Service + ingress/VPN-only access. Pod must reach the TEST app URL and the DB.
4. Never scale above 1 replica (queue and child processes are in-process).

## Phase 5 - Operate (daily use)
- UI: open the URL -> choose system/suite/tag/user/env/clean -> Start run -> watch the log -> "Open Allure report".
  Equivalent of `python run_tests.py --system meditik --tags home --user 4444401 --env test --clean`.
- API/cron: `POST /api/runs` with header `X-API-Token` (examples in the manual); a Kubernetes CronJob can `curl` it.
- Reports: `/reports/latest`, `/reports/<run_id>/`; runs list shows pass/fail counts.
- Update: merge to `main` -> workflow pushes new tag -> `kubectl set image deployment/refua-tests runner=<ecr>:<sha>` (data persists on the PVC).
- Backup: snapshot the PVC if report history is important.

## Phase 6 - Verification checklist (end to end)
1. Workflow green; ECR shows `refua-automation-core:<core_sha>` and `refua-automation-tests:<sha>,latest`.
2. Pod Ready; `GET /api/health` -> `allure:true`; UI loads and dropdowns are filled from `/api/options`.
3. Start `--tags home --user 4444401 --env test`: status goes queued -> running -> passed/failed with a live log and pass/fail counts;
   the report opens. (Use a user in the allow-list; the run writes seed rows to TEST DB - expected.)
4. Second run -> report trend shows both runs (history carried).
5. Delete the pod: runs, logs and reports are still there after restart; a run killed mid-flight shows `interrupted`.
6. Cancel a running run; verify the process stops and status = `cancelled`.

## Work I will do after approval (code/doc changes)
- Write `docs/guides/GITHUB_ACTION_SETUP.md` (click-by-click Phases 1-2 with screenshots-level detail and the IAM policy JSON) and link it from `DOCKER_PIPELINE.md`.
- Add Nexus support once Phase 0 answers exist: `docker login` step, pip/apt/Allure mirror build args.
- Add a ready `deploy/k8s/*.yaml` (Deployment, PVC, Service, Secret template, CronJob example) instead of only a sketch.
- Finish the missing verification: build both images locally, run the service from the image, drive the UI with Playwright, fix findings.
- Optional hardening: login in front of the UI (ingress/OIDC proxy) since reports and the run list are readable without a token.

## Critical files
`.github/workflows/build-push-ecr.yml`, `docker/core/Dockerfile`, `docker/tests/Dockerfile`, `refua_service/{app,runs,reports,settings}.py`,
`refua_service/static/index.html`, `docs/guides/DOCKER_PIPELINE.md`, `run_tests.py` (reused as the single command entry point).
