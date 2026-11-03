# Docker images, GHCR/ECR pipeline and runner service

How `refuaAutomationTests` is packaged as a backend service and published to ghcr.io (mirrored into ECR by the organization's pull-through cache).

## Overview

```
refuaAutomationCore repo ──► refua-automation-core image   (docker/core/Dockerfile, base = BASE_IMAGE)
                                      │ FROM
refuaAutomationTests repo ─► refua-automation-tests image  (docker/tests/Dockerfile)
                                      │ runs
                       uvicorn refua_service.app:app  (UI + REST API on :8080)
                                      │ spawns
                       python run_tests.py --system … --tags … --user … --env … --clean
```

One workflow, `.github/workflows/build-push-image.yml` (Actions -> "Docker - Build and push to GHCR (ECR pull-through)"),
builds both images in order, smoke-tests the tests image, then pushes both to `ghcr.io/digitalidf/refuaautomationtests/...`
with the built-in `GITHUB_TOKEN`. It runs on push to `main` (when image-relevant files change) and manually.
No AWS role, keys or ECR repositories are involved: DigitalIDF's ECR pull-through cache fetches the image from ghcr.io the first
time it is pulled, at
`373007444960.dkr.ecr.il-central-1.amazonaws.com/ghcr/digitalidf/refuaautomationtests/<image>:<tag>`.

## Run it without Docker (your machine)
`runService.bat` (or `venv\Scripts\python.exe -m uvicorn refua_service.app:app --port 8080`) starts the same website on
http://localhost:8080 using your venv, `.env.test`, Java and the Allure CLI. Data goes to `.service_data\`.
Step-by-step: [DOCKER_PIPELINE_ROLLOUT_PLAN.md](DOCKER_PIPELINE_ROLLOUT_PLAN.md). Hosting 24/7: [LATER_ACTION_ITEMS.md](LATER_ACTION_ITEMS.md).

## GitHub workflow settings
Only the core token is required.

| Where | Name | Value |
|---|---|---|
| Secret | `CORE_REPO_TOKEN` | Token that can read `DigitalIDF/refuaAutomationCore` (required) |
| Variable (optional) | `CORE_REF` | refuaAutomationCore ref to build. Default `feat/meditik-element-scraper` |
| Variable (optional) | `BASE_IMAGE` | Mirror of the Playwright base image; blank = Microsoft's public `playwright/python` image |

Image names (lowercase) and tags (commit SHA, `latest`, optional extra tag):
`ghcr.io/digitalidf/refuaautomationtests/refua-automation-core` and `.../refua-automation-tests`.

**Core version:** the tests need refua-core >= 2.0.1 (automation login). On `DigitalIDF/refuaAutomationCore` that is only on
`feat/meditik-element-scraper`; `main` is 1.0.1. The workflow fails if the chosen ref is 1.x. Once 2.0.1 is merged, set
`CORE_REF=main`.


## Run the published image with real tests
Step by step (env file, network check, first run, restart check): [RUN_IMAGE_WITH_REAL_TESTS.md](RUN_IMAGE_WITH_REAL_TESTS.md).

## Build locally

```bash
docker build -f docker/core/Dockerfile -t refua-automation-core ../refuaAutomationCore
docker build -f docker/tests/Dockerfile --build-arg CORE_IMAGE=refua-automation-core -t refua-automation-tests .
docker run --rm -p 8080:8080 -v refua-data:/data --env-file .env.test refua-automation-tests
```

Open http://localhost:8080. Never bake `.env.*` into the image (`.dockerignore` excludes them); pass the content as
environment variables (`.env.test` is loaded with `override=False`, so env vars win).

## Runtime configuration (environment variables)

| Variable | Default | Meaning |
|---|---|---|
| `AUTOMATION_SECRET`, `ORM_DB_*`, `SEED_ALLOWED_PERSONAL_NUMBERS`, ... | - | The content of `.env.<env>`; use a Kubernetes Secret |
| `DATA_DIR` | `/data` | Persistent volume root |
| `SERVICE_ALLOWED_USERS` | `SEED_ALLOWED_PERSONAL_NUMBERS` | Users offered/accepted, e.g. `4444401,4444400-4444499` |
| `SERVICE_ALLOWED_ENVS` | `test,preprod` | Environments a run may target (`prod` is off by default) |
| `MAX_CONCURRENT_RUNS` | `1` | Parallel runs (the rest queue) |
| `RUN_TIMEOUT_MINUTES` | `180` | A run exceeding it is killed (`timed_out`) |
| `RETENTION_DAYS` | `30` | Older runs, results and reports are deleted; `0` keeps everything |
| `SERVICE_API_TOKEN` | unset | If set, starting/cancelling runs needs header `X-API-Token`. Reads and reports stay open: restrict access at ingress/VPN |

The pod also needs network access to the application under test and its database.

## Using it

**UI:** choose system, suite, tag, user, environment, "clean", then *Start run*. The page shows the equivalent
`run_tests.py` command, live log, status, pass/fail counts and an *Open Allure report* link. `/reports/latest` opens the
newest report.

**API:**

```bash
curl -X POST http://HOST:8080/api/runs -H 'Content-Type: application/json' -H 'X-API-Token: …' \
  -d '{"system":"meditik","suite":"bdd","tags":"home","user":"4444401","env":"test","clean":true}'
curl http://HOST:8080/api/runs                    # list
curl http://HOST:8080/api/runs/<id>/log?offset=0  # log (poll with next_offset)
curl -X POST http://HOST:8080/api/runs/<id>/cancel
curl http://HOST:8080/api/options                 # valid values for every parameter
```

Statuses: `queued`, `running`, `passed`, `failed` (pytest exit 1), `error` (other exit codes, e.g. 5 = nothing collected),
`cancelled`, `timed_out`, `interrupted` (pod restarted mid-run). A second run for the same user and environment is
rejected while one is active (the DB seed holds a per-user lock). `clean` only empties that run's own results folder.

## Where results are kept

Everything under `/data` (mount a PersistentVolumeClaim; the container runs as user `pwuser`, uid 1000 in the Playwright
image, so set `fsGroup: 1000`):

```
/data/runs/<id>.json | .log      run parameters, status, exit code, console output
/data/allure/results/<id>/       raw Allure results
/data/allure/reports/<id>/       generated HTML report, served at /reports/<id>/
/data/seeds/                     DB seed manifests;  /data/home/  HOME of the test process
```

After each run the service generates the report and copies the previous report's `history/` into the new results, so
Allure's trend graphs span runs. The service is the always-on report server: it serves every report that is on the volume.
Run exactly **one replica** (the queue and child processes live in the process).

## Kubernetes sketch

```yaml
spec:
  replicas: 1
  strategy: { type: Recreate }
  template:
    spec:
      securityContext: { fsGroup: 1000 }
      containers:
        - name: runner
          image: 373007444960.dkr.ecr.il-central-1.amazonaws.com/ghcr/digitalidf/refuaautomationtests/refua-automation-tests:<tag>
          ports: [{ containerPort: 8080 }]
          envFrom: [{ secretRef: { name: refua-tests-env } }]
          volumeMounts: [{ name: data, mountPath: /data }]
          readinessProbe: { httpGet: { path: /api/health, port: 8080 } }
          resources: { requests: { memory: 2Gi, cpu: "1" } }
      volumes: [{ name: data, persistentVolumeClaim: { claimName: refua-tests-data } }]
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| Push step fails with `denied` / 403 | The workflow needs `packages: write` (set in the file); check that the organization allows GITHUB_TOKEN to publish packages |
| Workflow: core version is 1.x | Set `CORE_REF` to a ref containing refua-core >= 2.0.1 |
| ECR pull of the image fails the first time | The package must be visible to the pull-through cache: link/grant it under the package settings on GitHub (platform team) |
| Report link missing, log says Allure CLI not found | `ALLURE_BIN` must point to the Allure CLI (set in the image) |
| Runs fail at login/DB | Missing `AUTOMATION_SECRET` / `ORM_DB_*`, or no network path to the environment |
