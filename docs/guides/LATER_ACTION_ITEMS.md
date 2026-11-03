# Later action items (need the platform team / other teams)

Nothing here blocks the website from working on your machine, or the GitHub build and publish
(see [DOCKER_PIPELINE_ROLLOUT_PLAN.md](DOCKER_PIPELINE_ROLLOUT_PLAN.md), Parts A and B). Do these when you want the website
**always on**. Owners in brackets.

Images are published to **ghcr.io** and mirrored into ECR by the organization's pull-through cache, so there are **no ECR
repositories, AWS roles or access keys to create** for this project.

## 1. Decide where it runs 24/7  [you + platform team]
- Kubernetes (EKS) pulling `373007444960.dkr.ecr.il-central-1.amazonaws.com/ghcr/digitalidf/refuaautomationtests/refua-automation-tests:<tag>`
  is what the manual and sketch assume. A single VM running the container (or even `runService.bat` on a server) also works:
  it is one process and one data folder.
- Network: the host must reach the application under test (TEST URL) and its database, and users must reach the website
  (internal network/VPN). The website has no login of its own.

## 2. Make sure the package is pullable  [platform team, first time only]
After the first workflow run the packages exist under the organization's Packages. If the pull-through cache cannot fetch
them, link each package to the repository / grant the organization access in the package settings.

## 3. Deploy  [platform team]
Follow DOCKER_PIPELINE.md (environment variables, `/data` volume, Kubernetes sketch):
- Secret with the `.env.test` values + `SERVICE_API_TOKEN`; persistent volume (>= 20 GiB) mounted at `/data`.
- Exactly **one** replica (`strategy: Recreate`, `fsGroup` so the volume is writable for user `pwuser`); readiness probe `/api/health`.
- Optional: a scheduled job that calls `POST /api/runs` (replaces cron).

## 4. Protect it  [platform team]
Reports and the run list are readable without a token; only start/cancel need `SERVICE_API_TOKEN`. Put the service behind
the company network/VPN or an authenticating proxy (SSO) before exposing it.

## 5. Operations  [QA]
- Retention: `RETENTION_DAYS` (default 30) deletes old runs, results and reports; set 0 to keep everything.
- Backups: snapshot the data volume if report history matters.
- Updating: merge to `main` -> the workflow pushes a new image -> point the deployment to the new tag; data stays on the volume.

## 6. Core versioning  [core repo owner]
Merge `feat/meditik-element-scraper` (refua-core 2.0.1) into the core repo's default branch, then set the repository
variable `CORE_REF=main` so the workflow builds from a stable branch.

## 7. Only if you want a registry mirror for the base image  [you, once it is confirmed to exist]
Build with `--build-arg BASE_IMAGE=<mirror>/playwright/python:v1.56.0-noble` (set the repository variable `BASE_IMAGE`). If builds
must not reach the internet at all, also add mirrors for pip (`PIP_INDEX_URL`), apt (Java) and the Allure CLI download in
`docker/tests/Dockerfile`.
