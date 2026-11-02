# Later action items (need AWS / cluster / other teams)

Nothing here blocks the website from working on your machine or the GitHub build check
(see [DOCKER_PIPELINE_ROLLOUT_PLAN.md](DOCKER_PIPELINE_ROLLOUT_PLAN.md), Part A). Do these when you want the website
**always on** and the images **in ECR**. Owners in brackets.

## 1. Decide where it runs 24/7  [you + platform team]
- Kubernetes (EKS) pod pulling from ECR is what the manual and sketch assume. A single VM running the container
  (or even `runService.bat` on a server) also works: it is one process and one data folder.
- Network: the host must reach the application under test (TEST URL) and its database, and users must reach the website
  (internal network/VPN). The website has no login of its own.

## 2. AWS  [AWS admin]
1. Create two ECR repositories in one region: `refua-automation-core`, `refua-automation-tests`.
2. GitHub OIDC: identity provider `token.actions.githubusercontent.com`; an IAM role (e.g. `refua-github-ecr-push`) whose trust
   policy is limited to `repo:DigitalIDF/refuaAutomationTests:*`, with a policy allowing on those two repositories:
   `ecr:GetAuthorizationToken` (resource `*`), `BatchCheckLayerAvailability`, `InitiateLayerUpload`, `UploadLayerPart`,
   `CompleteLayerUpload`, `PutImage`, `BatchGetImage`, `GetDownloadUrlForLayer`, `DescribeRepositories`, `DescribeImages`.
   (Alternative: an IAM user's access keys stored as GitHub secrets.)
3. Nodes/hosts that will run the container can pull from ECR.

## 3. GitHub repository settings  [repo admin]
Settings -> Secrets and variables -> Actions -> Variables: `AWS_REGION`, `AWS_ROLE_ARN`
(optional: `ECR_CORE_REPOSITORY`, `ECR_TESTS_REPOSITORY`). When these are set the same workflow starts pushing to ECR
(tags: commit SHA, `latest`, optional extra tag). If the ECR repositories use immutable tags, run it manually with
"push_latest" off.

## 4. Deploy  [platform team]
Follow DOCKER_PIPELINE.md (environment variables, `/data` volume, Kubernetes sketch):
- Secret with the `.env.test` values + `SERVICE_API_TOKEN`; persistent volume (>= 20 GiB) mounted at `/data`.
- Exactly **one** replica (`strategy: Recreate`, `fsGroup: 1000`); readiness probe `/api/health`.
- Optional: a scheduled job that calls `POST /api/runs` (replaces cron).

## 5. Protect it  [platform team]
Reports and the run list are readable without a token; only start/cancel need `SERVICE_API_TOKEN`. Put the service behind
the company network/VPN or an authenticating proxy (SSO) before exposing it.

## 6. Operations  [QA]
- Retention: `RETENTION_DAYS` (default 30) deletes old runs, results and reports; set 0 to keep everything.
- Backups: snapshot the data volume if report history matters.
- Updating: merge to `main` -> workflow pushes a new image -> point the deployment to the new tag; data stays on the volume.

## 7. Only if you use a private registry mirror (Nexus or similar)  [you, once it is confirmed to exist]
- Base image: build with `--build-arg BASE_IMAGE=<mirror>/playwright/python:v1.56.0-noble` (set repository variable
  `BASE_IMAGE` for the workflow).
- If builds must not reach the internet: add mirrors for pip (`PIP_INDEX_URL`), apt (Java) and the Allure CLI download in
  `docker/tests/Dockerfile`, plus a `docker login` step in the workflow with secrets for the registry user.

## 8. Core versioning  [core repo owner]
Merge `feat/meditik-element-scraper` (refua-core 2.0.1) into the core repo's default branch, then set the repository
variable `CORE_REF=main` so the workflow builds from a stable branch.
