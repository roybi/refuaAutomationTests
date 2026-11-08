# Pipeline implementation plan: images -> GHCR -> ECR -> AWS runner with Allure history and 60-day log archive

Status (2026-11-04): Phase 5 (repository changes) is done and merged or in review; Phase 1 is done on our side (images build and publish from `main`, `CORE_REF` set), the remaining items wait on others: core PR #1 (1.1) and the code-scanning alert (1.8). Phases 2 to 4, 6 and 7 are not started. See the status line of each phase.

This document is the single list of actions to take the work from "runs on a developer machine" to "runs on AWS, always on,
every report visible, every log kept 60 days and ready for a later LLM analysis agent".
It builds on [DOCKER_PIPELINE.md](DOCKER_PIPELINE.md) (reference), [DOCKER_PIPELINE_ROLLOUT_PLAN.md](DOCKER_PIPELINE_ROLLOUT_PLAN.md)
(parts A to C), [RUN_IMAGE_WITH_REAL_TESTS.md](RUN_IMAGE_WITH_REAL_TESTS.md) and [LATER_ACTION_ITEMS.md](LATER_ACTION_ITEMS.md).
Where those documents already explain a step, this plan links to it instead of repeating it.

## 1. Goals

| # | Goal | Done when |
|---|---|---|
| G1 | Two images (core, tests) are built and published automatically | A push to `main` produces `refua-automation-core` and `refua-automation-tests` on ghcr.io, tagged with the commit SHA |
| G2 | The images reach ECR with no manual step | `docker pull` of the ECR pull-through address works for that SHA tag |
| G3 | A homepage lets any user start a test run without a command line | A user picks system/suite/tag/user/env on the page and gets a result |
| G4 | Execution happens on AWS (Docker or Kubernetes), not on user machines | The runs come from the pod; the pod survives a restart without losing history |
| G5 | Every Allure report stays reachable, with trends across runs | The homepage lists every run of the last 60 days with a working report link; trend graphs span runs |
| G6 | All execution logs are kept 60 days, in a form an LLM agent can read later | Each run is archived outside the pod (S3) with a machine-readable manifest; objects expire after 60 days |

Out of scope here: the LLM analysis agent itself. Section 9 only prepares its data.

## 2. Current state (checked against the repo on 2026-11-04)

| Area | State |
|---|---|
| Image build | `.github/workflows/build-push-image.yml` builds core then tests image, smoke-tests (starts the site, collects tests, launches Chromium), pushes to ghcr.io with `GITHUB_TOKEN`. Runs on push to `main` and manually. **Checked on GitHub 2026-11-04: all 3 runs on `main` succeeded** (PR #9, #10, #12; the last at 11:30 UTC, 1m46s). The secret `CORE_REPO_TOKEN` exists; the variable `CORE_REF` is set |
| Core version | Builds `feat/meditik-element-scraper` (refua-core **2.0.1**); the repository variable `CORE_REF` is set to that branch (the workflow keeps the same value as its fallback). Core `main` is still **1.0.1**; the tests need >= 2.0.1. The merge request is core PR #1 (open since 2026-09-24, failing checks). The core repo has branches `main`, `feat/meditik-element-scraper`, `sync/latest-20260813` |
| Homepage + API | `refua_service` (FastAPI): start/cancel runs, live log, per-run Allure report at `/reports/<id>/`, `/reports/latest`, `/reports/` (all reports), run list paging and filters (PR #13, open) |
| Allure trends | After each run the previous report's `history/` is copied into the new results (`reports.py`) |
| Storage | Everything under `DATA_DIR` (`/data`): run JSON, console log, raw Allure results, HTML reports |
| Retention | `RETENTION_DAYS`, default **60** (changed from 30 in `17a872d`, merged). `prune()` deletes the run JSON, log, raw results and report together, at service start and after each run, and skips runs whose archive upload is pending |
| Auth | None for reads. Start/cancel need `SERVICE_API_TOKEN`, and **the image refuses to start without a token** (`SERVICE_REQUIRE_TOKEN=true`, token of 16+ characters; branch `feat/service-auth`). Reads and reports stay open, see D2 |
| Off-pod copy of logs/results | **Built and merged** (`refua_service/archive.py`, S3 or folder). Not yet tried against a real bucket |
| ECR | The organization already runs an ECR Pull Through Cache for `ghcr.io/digitalidf/...` (platform team). Only the image address in the manifest is ours to set. Not yet tested with this project's images |
| PR checks | PR #13 fails only `ScanLi / Checking Scanning Results`: it fails when the repo has any open code-scanning alert. The one open alert (#23, `actions/excessive-secrets-exposure`, `.github/workflows/upload-test-plan-to-azure.yml` line 92, on `main`) is outside this pipeline. CodeQL, Dependabot, version check and the Dockerfile scans pass |

### Gaps this plan closes

Status 2026-11-04: the gaps for retention, off-pod copy, run metadata, the 500-run limit, the liveness probe and `SERVICE_PORT` are closed by Phase 5 (code and docs). Still open: login for reads (Phase 6: VPN-only) and the mutable `latest` tag (deploy by SHA, Phase 3).

| Gap | Why it matters | Phase |
|---|---|---|
| Retention default is 30 days, requirement is 60 | Reports and logs would vanish early | 4 |
| Logs live only on the pod volume, and `prune()` deletes raw results and logs together with the report | A lost volume loses the data the LLM agent needs; there is nothing to analyse after pruning | 5 |
| Run metadata does not record the image tag, refua-core version or git SHA | The agent cannot tell whether a failure came from a code change | 5 |
| `GET /api/runs` returns at most 500 runs and the homepage shows the newest ones | With 60 days of runs older reports may not be listed | 5 |
| Reports and logs are readable without login | They contain personal numbers and environment details | 3, 6 |
| Kubernetes sketch has a readiness probe but no liveness probe | A hung uvicorn is never restarted | 3 |
| `SERVICE_PORT` is read by the image but missing from the variable table | Operators cannot discover it | 5 (docs) |
| `latest` tag is mutable and ECR re-checks the upstream registry at most about once a day | A deploy by `latest` can run stale code | 3 |

## 3. Target architecture

```
GitHub (refuaAutomationTests main)
   | push -> build-push-image.yml (core image, then tests image, smoke test)
   v
ghcr.io/digitalidf/refuaautomationtests/refua-automation-{core,tests}:<sha>
   | organization's ECR Pull Through Cache (managed by the platform team; first pull of an ECR address creates the image in ECR;
   |  no GitHub PAT and no rule or repository to create on our side)
   v
373007444960.dkr.ecr.il-central-1.amazonaws.com/ghcr/digitalidf/refuaautomationtests/refua-automation-tests:<sha>
   | image: in the Deployment
   v
EKS pod (1 replica, Recreate) -- port 8080 -- internal address reachable over the VPN -- users' browsers
   |-- /data  <- PersistentVolume (EBS gp3): run JSON, console logs, raw Allure results, HTML reports (60 days)
   |-- on run end -> archive to S3  s3://<bucket>/runs/YYYY/MM/DD/<run_id>/  (60-day lifecycle)
   '-- stdout/stderr -> CloudWatch Logs (60-day retention)

later: LLM agent (Bedrock) reads the S3 archive + manifest
```

Decisions behind it:
- **One replica.** The run queue and child processes live in the process, and the DB seed uses a per-user lock. Do not scale out.
- **EBS volume for the live data, S3 for the archive.** The volume serves reports fast and is what the service already writes to.
  S3 is the durable copy and the LLM input. If you prefer one storage for both, EFS removes the single-AZ limit of EBS but is slower and
  costs more; EBS plus S3 is the recommendation.
- **Deploy by SHA tag, never by `latest`.**

## 4. Decisions

| # | Question | Decision |
|---|---|---|
| D1 | Kubernetes (EKS) or a single EC2/ECS host? | Not final. Reaching AWS requires the VPN. Exact platform (EKS or Docker host) is decided at Phase 3, when the first deployment is tried by hand |
| D2 | How do users reach the page? | **Corrected 2026-11-04:** the VPN is needed to reach AWS from the developer PC, but the service itself is not guaranteed to be VPN-only, so it must not rely on the network. Done: starting and cancelling runs always needs `SERVICE_API_TOKEN` (the image will not start without it). Open: reads (run list, logs, reports) are still unauthenticated. Either confirm with the platform team that the internal address is reachable only from company networks, or add the opt-in read protection (login with the same token, cookie for report links) |
| D3 | What goes to S3? | **Raw data only**: console log, raw Allure results and the run record. The HTML report is not archived (it can be regenerated from the raw results) |
| D4 | Is 60 days the final retention for the S3 archive, or only for the website? | 60 days for both; the lifecycle days are a parameter, so a longer archive for the LLM is a one-value change |
| D5 | Do logs contain personal data or tokens? | **No** (confirmed 2026-11-04). No redaction step is built; if that changes, add one in `archive.py` before upload |
| D6 | Which environments may be run from AWS (`test`, `preprod`; `prod` stays off)? | `SERVICE_ALLOWED_ENVS=test,preprod` |
| D7 | Request to the platform team | **Updated 2026-11-04:** trying the AWS steps by hand is not possible for Phase 2 because the developer has no AWS CLI or CloudShell access. The Phase 2 request is written (see Phase 2). The Phase 3 and 4 request is still to be written from what the platform team says |

## 5. Phases

Owners: **You** = this repo's maintainer, **Platform** = platform/DevOps team, **Core** = refuaAutomationCore owner.

### Phase 1 - Build and publish both images  [You, Core]  (no AWS)

| # | Action | Check |
|---|---|---|
| 1.1 | **OPEN, waiting on the core repo.** Merge `feat/meditik-element-scraper` (refua-core 2.0.1) into core `main`  [Core]. Checked 2026-11-04: `main` is still 1.0.1. The merge request already exists: [refuaAutomationCore PR #1](https://github.com/DigitalIDF/refuaAutomationCore/pull/1), open since 2026-09-24 (3 commits, 8 files, +1014 -94, mergeable, branch is 3 ahead and 0 behind `main`, `main` is protected, no review decision yet). Its checks fail: `CodeQL`, `ScanLi / Checking Scanning Results` and two `comment-and-fail` jobs. The core repo has one open code-scanning alert (#1, rule `WS-I011-PYTHON-00030`, `setup.py` line 7, on branch `sync/latest-20260813`), the same kind of repo-wide alert that fails ScanLi here (1.8). The job logs do not state the reason for `CodeQL` and `comment-and-fail`; the core owner has to open those runs. The PR head `018d4958591f` is exactly the core commit the images are built from | `main` reports version >= 2.0.1 |
| 1.2 | **DONE for now (2026-11-04 11:56 UTC), final value after 1.1.** Repository variable `CORE_REF` is set to `feat/meditik-element-scraper` (same as the old hardcoded fallback, so builds do not change, but the value is now visible and editable in Settings). After 1.1 is merged, change it to `main` (`gh variable set CORE_REF --repo DigitalIDF/refuaAutomationTests --body main`). To pin a build to an exact core commit, use its SHA instead (the PR head is `018d4958591fc3b24d803831f635e61b12058fc7`). A manual run of the workflow can also override it with the `core_ref` input | Workflow log prints core version 2.x |
| 1.3 | **DONE.** Secret `CORE_REPO_TOKEN` (fine-grained, Contents: read on `DigitalIDF/refuaAutomationCore`), created 2026-11-02 | `gh secret list --repo DigitalIDF/refuaAutomationTests` shows it (checked 2026-11-04) |
| 1.4 | **DONE** for the Docker and archive work (PRs #9, #10, #12). PR #13 (run history, reports index) is open. The old `build-push-ecr.yml` is gone from `main` | Workflow "Docker - Build and push to GHCR (ECR pull-through)" is listed under Actions |
| 1.5 | **DONE.** Push-to-`main` triggers the workflow: 3 successful runs (latest 2026-11-04 11:30 UTC, after PR #12). The log of that run shows: refua-core 2.0.1 installed, Chromium 141 launches, 735 tests collected, both images pushed with tags `<sha>` and `latest` (tests `107d8fffa8ce`, core `018d4958591f`). The Packages page itself was not opened | Both packages visible under the organization's Packages with tags `<sha>` and `latest` |
| 1.6 | **DONE 2026-11-04 (checked on the developer PC).** The image `ghcr.io/digitalidf/refuaautomationtests/refua-automation-tests:f239b6656389` was pulled from ghcr.io (after adding the `read:packages` scope to the `gh` login) and its digest equals the published `sha256:9a05879b185deafc58ee7e3a14cb255ae7ea66effed24520822a392b62bc6647`. Inside the running container `buildinfo.collect()` returns `image_tag` `f239b6656389`, `git_sha` `f239b6656389f146ba5dd5822db7a06141a3b34f`, `core_version` 2.0.1, `playwright_version` 1.56.0. The service is healthy, `token_required` is true, a start request without the token returns 401, and the image refuses to start without a token. Earlier digests (from the build log of the run for `107d8ff`): Tests image `107d8fffa8ce` = `sha256:592bdcbe34a552f4a720f1cc5c77365c2ae2ef64b481ce40fa184a4b2ebc14ad`; core image `018d4958591f` = `sha256:b271358b4b1e0a8f464bbef93334366649989c677317256ae64587b6f752c219`. Compare the tests digest with what ECR returns after the first pull (Phase 2.4). Still to check: that the image reports `build.image_tag` and `git_sha` (step 5.4), which needs the image to be started (Phase 7.2) | Digest noted in the run summary or release notes |
| 1.7 | **ADDRESSES KNOWN FROM THE BUILD LOG, Packages page not yet confirmed.** The workflow pushes to `ghcr.io/digitalidf/refuaautomationtests/refua-automation-tests` and `.../refua-automation-core`, so the ECR addresses are the ones in Phase 2. Open the organization's Packages page once to confirm them and the access settings (only needed if the Phase 2 pull fails). To list them with `gh`, refresh the login with the `read:packages` scope: `gh auth refresh -h github.com -s read:packages` | Addresses noted |
| 1.8 | **OPEN, outside this pipeline.** PR check `ScanLi / Checking Scanning Results` fails while any code-scanning alert is open. Alert #23 (`actions/excessive-secrets-exposure`) is in `.github/workflows/upload-test-plan-to-azure.yml` line 92: the dynamic secret lookup `secrets[format('AZURE_IMPORT_PAT_{0}', inputs.upload_id)]` that gives each upload its own temporary PAT. Decide with the owner of the Azure import tool: fix it, or dismiss the alert with a reason. It is not caused by the Docker pipeline or PR #13 | PR checks green, or the alert dismissed with a recorded reason |

### Phase 2 - GHCR -> ECR pull-through (ECR PTC)  [You; Platform only if the first pull fails]

**What it is.** The ECR Pull Through Cache (PTC) is an AWS mechanism, already set up by the platform team for the DigitalIDF
organization. When something pulls an image from the ECR address below, ECR looks for it at the matching `ghcr.io/digitalidf/...`
address and, if it is not in ECR yet, creates it there. Nobody packs or pushes the image to ECR by hand.
Because the image is stored inside the AWS account, the AWS side needs no GitHub PAT, and **our side needs nothing except the image
address in the manifest**. We do not create a cache rule, a Secrets Manager secret or an ECR repository.
The old "build and push to ECR" workflow is no longer supported by the platform team. If PTC causes problems, the fallback is the old
"build and push image" workflow (not planned for this project).

**Address mapping** (this is the whole integration):

```
ghcr.io/digitalidf/{UpstreamRepositoryName}/{ImageName}:{ImageTag}
373007444960.dkr.ecr.il-central-1.amazonaws.com/ghcr/digitalidf/{UpstreamRepositoryName}/{ImageName}:{ImageTag}
```

For this project (`UpstreamRepositoryName` = `refuaautomationtests`):

| Image | ghcr.io address | ECR address used in the manifest |
|---|---|---|
| tests | `ghcr.io/digitalidf/refuaautomationtests/refua-automation-tests:<sha>` | `373007444960.dkr.ecr.il-central-1.amazonaws.com/ghcr/digitalidf/refuaautomationtests/refua-automation-tests:<sha>` |
| core | `ghcr.io/digitalidf/refuaautomationtests/refua-automation-core:<sha>` | `373007444960.dkr.ecr.il-central-1.amazonaws.com/ghcr/digitalidf/refuaautomationtests/refua-automation-core:<sha>` |

Only the tests image is deployed. The core image is used as its base at build time, so it is published but never pulled by the pod.

| # | Action | Check |
|---|---|---|
| 2.1 | Open the organization's **Packages** page on GitHub and copy the exact address of each image. Sometimes the address has no image name and looks like `ghcr.io/digitalidf/{UpstreamRepositoryName}:{ImageTag}` (the image name is the repository name). If that is the case here, drop the extra segment in the ECR address too | The address in the manifest is the Packages address with the prefix `373007444960.dkr.ecr.il-central-1.amazonaws.com/ghcr/` instead of `ghcr.io/` |
| 2.2 | Use the ECR address as `image:` in the Deployment (Phase 3). Always use the commit SHA tag | The manifest contains no `ghcr.io/` address |
| 2.3 | **Script ready, not run yet (no AWS login or AWS CLI on the dev PC).** `tools/ecr_pull_check.ps1 -Profile <aws-profile> [-Tag <12-char sha>] [-ExpectedDigest sha256:...]` does 2.3 and 2.4 and also reads the image build info (5.4) and checks the token rule. Needs Docker, AWS CLI v2 (`winget install Amazon.AWSCLI`), `aws configure sso --profile <name>`, `aws sso login --profile <name>` and the VPN. Latest published tests image at the time of writing: tag `f239b6656389`, digest `sha256:9a05879b185deafc58ee7e3a14cb255ae7ea66effed24520822a392b62bc6647`. Manual steps: Test the first pull from a machine or node with ECR access: `aws ecr get-login-password --region il-central-1 \| docker login --username AWS --password-stdin 373007444960.dkr.ecr.il-central-1.amazonaws.com`, then `docker pull <ECR address>:<sha>` | The pull succeeds and ECR now has a `ghcr/digitalidf/refuaautomationtests/...` repository |
| 2.4 | Compare the pulled image digest with the one recorded in step 1.6 (do this after every deploy: a green health check can pass on stale containers) | Digests are identical |
| 2.5 | Only if 2.3 fails with access denied or "not found": ask the platform team to check that the package is visible to the organization's cache (Packages -> the package -> package settings -> link to the repository / org access) and that the nodes may pull from the `ghcr/` ECR prefix | Pull works after their fix |

Note: ECR re-checks the upstream registry for an already cached tag at most about once a day, so a moving tag like `latest` can be stale.
Always reference the commit SHA.

**Status 2026-11-04: ASSUMED OK, NOT VERIFIED (decision of the maintainer).** The account 373007444960 is not in the developer's AWS access portal, and the console role in the `digitalidf-dev` account (1192-6860-5376, role `General-Developer-PS`) cannot list pull-through cache rules, so the rule and the pull could not be checked. Phase 2 continues on the assumption that the pull works, as the platform team's note says (only the image URL changes). The assumption is tested for real at the first deployment (step 3.5): `ErrImagePull` or `ImagePullBackOff` on the ECR address means 2.5 applies and the request below is sent. Background: the developer PC has no AWS CLI, no AWS profile and no CloudShell access, so the first pull cannot be made from our side. Either the platform team makes it, or it happens on its own when the pod is deployed (Phase 3): an `ImagePullBackOff` with the ECR address means 2.5 applies. What is known: the tests image `f239b6656389` is published on ghcr.io with digest `sha256:9a05879b185deafc58ee7e3a14cb255ae7ea66effed24520822a392b62bc6647` (build run for PR #14). The script `tools/ecr_pull_check.ps1` (PR #15) automates 2.3 and 2.4 for whoever has AWS access.

Request to the platform team (copy and paste):

> Hi, we publish our test-runner image to `ghcr.io/digitalidf/refuaautomationtests/refua-automation-tests` and want to deploy it from the ECR pull-through address. Could you check three things in account 373007444960, region il-central-1?
>
> 1. The pull-through cache rule for `ghcr.io` with prefix `ghcr` exists.
> 2. A pull works: `docker pull 373007444960.dkr.ecr.il-central-1.amazonaws.com/ghcr/digitalidf/refuaautomationtests/refua-automation-tests:f239b6656389`. The digest should be `sha256:9a05879b185deafc58ee7e3a14cb255ae7ea66effed24520822a392b62bc6647`.
> 3. The role our cluster nodes (or pods) use is allowed to pull from the `ghcr/` prefix in ECR.
>
> If the first pull fails, please send us the exact error. Also, which cluster and namespace should we deploy into, and who creates the S3 bucket and the pod's access role? We will send the details.

Replace the tag and digest if a newer build has been published. The expected digest is in the build workflow log ("Push images" step).

### Phase 3 - Run it on AWS  [Platform, You]

| # | Action | Check |
|---|---|---|
| 3.1 | Create namespace `refua-tests` | `kubectl get ns` |
| 3.2 | Create Secret `refua-tests-env` from the `.env.<env>` content plus `SERVICE_API_TOKEN`: a random value of 16+ characters; the pod does not start without it (never in the image or in git) | `kubectl describe secret` lists the keys |
| 3.3 | Create the PVC (EBS gp3, start at 50 GiB, `allowVolumeExpansion: true`) | Bound |
| 3.4 | Create an IAM role for the service account (IRSA) with `s3:PutObject`, `s3:GetObject`, `s3:ListBucket` on the archive bucket only | `aws sts get-caller-identity` inside the pod shows the role |
| 3.5 | Apply the Deployment/Service/Ingress below with the SHA tag | Pod Ready |
| 3.6 | Expose the service on an internal address only, reachable over the VPN (decision D2) | A request from outside the VPN is refused |
| 3.7 | Allow the pod network egress to the TEST application, its database and S3 | A small run (tag `home`) passes |

Manifest sketch (replace the placeholders):

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: refua-tests
  namespace: refua-tests
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::<account>:role/<irsa-role>
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata: { name: refua-tests-data, namespace: refua-tests }
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: gp3
  resources: { requests: { storage: 50Gi } }
---
apiVersion: apps/v1
kind: Deployment
metadata: { name: refua-tests, namespace: refua-tests }
spec:
  replicas: 1
  strategy: { type: Recreate }
  selector: { matchLabels: { app: refua-tests } }
  template:
    metadata: { labels: { app: refua-tests } }
    spec:
      serviceAccountName: refua-tests
      securityContext: { fsGroup: 1000 }
      containers:
        - name: runner
          image: 373007444960.dkr.ecr.il-central-1.amazonaws.com/ghcr/digitalidf/refuaautomationtests/refua-automation-tests:<sha>
          ports: [{ containerPort: 8080 }]
          envFrom: [{ secretRef: { name: refua-tests-env } }]
          env:
            - { name: RETENTION_DAYS, value: "60" }
            - { name: SERVICE_ALLOWED_ENVS, value: "test,preprod" }
            - { name: ARCHIVE_S3_BUCKET, value: "<bucket>" }
            - { name: ARCHIVE_PREFIX, value: "runs" }
          volumeMounts: [{ name: data, mountPath: /data }]
          readinessProbe: { httpGet: { path: /api/health, port: 8080 } }
          livenessProbe:  { httpGet: { path: /api/health, port: 8080 }, initialDelaySeconds: 30, periodSeconds: 30, failureThreshold: 3 }
          resources: { requests: { memory: 2Gi, cpu: "1" }, limits: { memory: 4Gi } }
      volumes: [{ name: data, persistentVolumeClaim: { claimName: refua-tests-data } }]
---
apiVersion: v1
kind: Service
metadata: { name: refua-tests, namespace: refua-tests }
spec:
  selector: { app: refua-tests }
  ports: [{ port: 80, targetPort: 8080 }]
```

Pick the memory limit after measuring a real run: Chromium plus Allure generation is the peak.
A plain Docker host (D1 alternative) uses the same image with `docker run -v refua-data:/data --env-file ... -p 8080:8080`.

### Phase 4 - Storage and retention (60 days)  [Platform, You]

| # | Action | Check |
|---|---|---|
| 4.1 | Set `RETENTION_DAYS=60` (manifest above) | Page and `/api/runs` keep runs for 60 days |
| 4.2 | Size the volume: `runs per day x average run size (MB) x 60 x 1.3`. Measure the average from 5 to 10 real runs (`du -sh /data/runs /data/allure/*`) and resize | Usage stays below 70% after 60 days |
| 4.3 | Create the S3 bucket `<org>-refua-test-archive` (versioning off, SSE-KMS or SSE-S3, block public access, bucket policy limited to the IRSA role and the future agent role) | `aws s3api get-public-access-block` shows all four blocks on |
| 4.4 | Add an S3 lifecycle rule on prefix `runs/` that expires objects after 60 days (and aborts incomplete multipart uploads after 7 days) | `aws s3api get-bucket-lifecycle-configuration` |
| 4.5 | Set CloudWatch log group retention to 60 days for the pod's stdout | Retention shows 60 days |
| 4.6 | Schedule a volume snapshot (AWS Backup or a CronJob) if the 60-day report history must survive volume loss; S3 already covers logs and raw results | Snapshot exists |
| 4.7 | Add an alarm on volume usage above 80% and on pod restarts | Alarm in place |

Keep the retention value in one place per layer (`RETENTION_DAYS`, S3 lifecycle days, CloudWatch retention) so a later change to
a longer LLM-training window is three parameter edits, not code.

### Phase 5 - Repository changes  [You]

All values come from environment variables with defaults, following the existing `settings.py` pattern. Each item gets unit tests in
`tools/tests/` (the service already has tests there). Work on a feature branch, run the build/tests, commit, push, open a PR.

| # | Change | Files | Acceptance |
|---|---|---|---|
| 5.1 | **DONE (branch `feat/run-archive-s3`).** **Archive on run end.** `refua_service/archive.py`: an `Archiver` with an S3 backend (`ARCHIVE_S3_BUCKET`) and a folder backend (`ARCHIVE_DIR`, for tests and local use). After the report is generated, each finished run is copied to `<prefix>/YYYY/MM/DD/<run_id>/` (UTC creation date) as `run.json`, `console.log` and `allure-results/` file by file. The HTML report and the copied Allure `history/` are not archived (D3). Upload runs on its own worker thread and never changes the run result; a failed upload keeps a marker in `/data/archive_pending/` and is retried at service start and after every run | `refua_service/archive.py`, `refua_service/runs.py`, `refua_service/settings.py`, `requirements-service.txt` | Tests: layout, failed upload keeps the marker, retry after recovery, S3 calls, path escape refused, end-to-end run is archived |
| 5.2 | **DONE.** **Prune only after archive.** `prune()` skips runs whose archive upload is pending when archiving is enabled (markers are ignored when archiving is off, so they cannot keep runs forever) | `refua_service/reports.py` | Tests: pending run older than retention is kept, others deleted |
| 5.3 | **DROPPED (D5).** Redaction is not built because the logs contain no personal data or tokens | - | - |
| 5.4 | **DONE and verified 2026-11-04 on the image `f239b6656389` (see 1.6).** **Richer run metadata.** Each run JSON has `build`: `image_tag`, `git_sha`, `core_version`, `playwright_version`, `python_version`. `docker/tests/Dockerfile` now sets `IMAGE_TAG` and `GIT_SHA` from the existing `APP_VERSION` and `GIT_SHA` build args, which the workflow already passes | `docker/tests/Dockerfile`, `refua_service/buildinfo.py`, `refua_service/runs.py` | `GET /api/runs/<id>` shows `build`; checked in the image in Phase 7.2 |
| 5.5 | **DONE (changed).** **Manifest for the future agent.** `manifest.json` per run (schema version, run id, status, archived_at, list of files with sizes), written last, so its presence means the archive is complete. The planned daily `index.jsonl` and `summary.json` are not built: S3 cannot append to an object, `run.json` already holds the summary, and listing `<prefix>/YYYY/MM/DD/` finds every run of a day | `refua_service/archive.py` | Tests check the manifest content and that it is the last object written |
| 5.6 | **DONE (PR #13).** The page reloads the already loaded older pages behind the new head when a new run arrives, so no run falls between the live page and the older pages (covered by `tools/tests/js/runlist_sim.js`, run from `test_homepage_run_list.py` when node is installed). **Complete run history on the homepage.** `GET /api/runs` takes `offset`, `status`, `system`, `date_from`, `date_to` (offset counts matching runs); the page has filters and "Load more" (newest page refreshes live, older pages load on demand) | `refua_service/app.py`, `refua_service/runs.py`, `refua_service/static/index.html` | 60 days of runs are all reachable from the page |
| 5.7 | **DONE.** **Report index.** A `/reports/` page listing all stored reports newest first with status counts (the static mount has no directory listing today) | `refua_service/app.py` | Opening `/reports/` shows every report |
| 5.8 | **DONE.** **Docs.** Done (all): `SERVICE_PORT`, `ARCHIVE_S3_BUCKET`, `ARCHIVE_DIR`, `ARCHIVE_PREFIX`, the archive layout and the 60-day default in DOCKER_PIPELINE.md; the 60-day default in LATER_ACTION_ITEMS.md. liveness probe in the DOCKER_PIPELINE.md Kubernetes sketch, link to RUN_IMAGE_WITH_REAL_TESTS.md from the rollout plan, paging/filters and `/reports/` described | `docs/guides/*.md` | Docs match the code |
| 5.9 | **DONE.** **Default retention.** Code default of `RETENTION_DAYS` is now 60 (`DEFAULT_RETENTION_DAYS`) | `refua_service/settings.py` | Test for the default |

Allure note: the trend widget keeps a limited number of past builds (Allure default is 20), so the trend graph will not show all 60 days.
The report index (5.7) and the archive cover the full period.

### Phase 6 - Homepage access and hardening  [Platform, You]

| # | Action | Check |
|---|---|---|
| 6.1 | **PARTLY DONE.** Start/cancel are protected by a mandatory token (`SERVICE_REQUIRE_TOKEN`). Still open: protect reads. Ask the platform team who can reach the internal address; if it is wider than intended, build the opt-in read protection or put SSO in front (D2) | A start request without the token returns 401, the pod fails to start without a token; reads decided as above |
| 6.2 | Use TLS on the ingress | HTTPS only |
| 6.3 | Run the container as non-root (already `pwuser`), read-only root filesystem if the tests allow it, drop capabilities | Pod security admission passes |
| 6.4 | Restrict who can start runs against `preprod` (`SERVICE_ALLOWED_USERS`, `SERVICE_ALLOWED_ENVS`) | A disallowed env or user returns 422 |
| 6.5 | Enable ECR image scanning and review findings after each build | Scan results visible |

### Phase 7 - Verification before announcing  [You, QA]

Run each check once on AWS and record the result in the PR.

| # | Check | Expected |
|---|---|---|
| 7.1 | Push a trivial change to `main` | New SHA tags on ghcr.io within the workflow time; ECR pull of the new SHA works and the digest matches |
| 7.2 | Deploy that SHA; read `image_tag` from `GET /api/runs/<id>` of a new run | Equals the pushed SHA (proves the new code is running, not just healthy) |
| 7.3 | Start a `home` run from the page | Status goes queued, running, passed/failed; report opens |
| 7.4 | Start a second run | Report trend shows both runs |
| 7.5 | Delete the pod | After restart both runs and reports are still listed |
| 7.6 | Check S3 | Both runs archived with `manifest.json`, `run.json` (with `build.image_tag` = deployed SHA), `console.log` and `allure-results/` |
| 7.7 | Simulate S3 outage (block the role), run, restore | Run unaffected; archive catches up |
| 7.8 | Unit tests for `prune`: `RETENTION_DAYS=0` keeps everything; `60` keeps a 59-day-old run and deletes a 61-day-old run; a run with a pending archive upload is kept | Unit tests pass |
| 7.9 | Check lifecycle and retention settings | S3 lifecycle = 60 days, CloudWatch = 60 days, `RETENTION_DAYS=60` |
| 7.10 | Anonymous request from outside the VPN | Refused |

### Phase 8 - Prepare for the LLM analysis agent  [You, later]

Not built now. These choices keep it cheap later:
- Data is already in S3 under date-partitioned prefixes with a schema-versioned `manifest.json` per run (list a day's prefix to find its runs).
- A future agent role gets read-only access to `runs/` (bucket policy prepared in 4.3).
- Suggested first use: after each run, send `summary.json` plus failed-test log excerpts to Bedrock and write the analysis back next to the run as `analysis.json`, shown on the report page.
- Keep an eye on data governance: archived logs include test-user identifiers (the run record has the user number). D5 says there is no personal data or token in the logs; the bucket policy (4.3) is the control if that changes.
- If the agent needs more than 60 days, change the S3 lifecycle days only (decision D4).

## 6. Order of work and dependencies

```
Phase 1 (build/publish) -> Phase 2 (ECR) ---------------.
Phase 5 (code, can start now, needs no AWS) -----------+--> Phase 3 (deploy) -> Phase 4 (retention) -> Phase 6 -> Phase 7
Decisions D1-D6 ---------------------------------------'
```

Phase 5 steps 5.1 to 5.5 do not need AWS: the archive has a folder backend (`ARCHIVE_DIR`), so they are developed and tested before the bucket exists.
Phases 3 and 4 need the platform team; send them the 3.1 to 3.4 and 4.3 to 4.6 items as one request early, since their lead time is the longest.
Phase 2 needs no platform work unless the first pull fails (step 2.5).

## 7. Risks

| Risk | Mitigation |
|---|---|
| Two runs against the same user collide (DB seed lock) | Already rejected with 409; keep `MAX_CONCURRENT_RUNS=1` until per-user seeding is verified |
| EBS volume is tied to one availability zone; a node loss in another AZ blocks the pod | Use `Recreate` with a node group in the same AZ, or move to EFS; S3 holds the durable copy |
| TEST rate-limits (HTTP 429) after repeated runs | Keep the concurrency at 1; add a minimum gap between scheduled runs |
| Logs later turn out to hold personal data or tokens | Bucket encryption and a restricted bucket policy (4.3); add a redaction step in `archive.py` (D5) |
| Disk fills before 60 days | Alarm at 80% (4.7), measured sizing (4.2), volume expansion enabled |
| The ECR pull of our image was never verified (no access to account 373007444960) | Assumed OK; the first deployment is the test (3.5, 7.1). If the pod shows `ErrImagePull`, send the Phase 2 request to the platform team |
| ECR serves a stale tag | Deploy by SHA only, compare digests (2.5, 7.2) |
| Core `main` still 1.x when the workflow runs | The workflow already fails fast on 1.x; finish step 1.1 first |

## 8. Parameters summary

| Parameter | Layer | Value |
|---|---|---|
| `RETENTION_DAYS` | service | 60 |
| `ARCHIVE_S3_BUCKET`, `ARCHIVE_PREFIX` (or `ARCHIVE_DIR` for a folder) | service | bucket name, `runs` |
| S3 lifecycle expiration | S3 | 60 days on `runs/` |
| CloudWatch retention | CloudWatch | 60 days |
| `SERVICE_ALLOWED_ENVS` | service | `test,preprod` |
| `MAX_CONCURRENT_RUNS` | service | 1 |
| `RUN_TIMEOUT_MINUTES` | service | 180 |
| `CORE_REF` | GitHub variable | `main` after step 1.1 |
| Image tag in the manifest | Deployment | commit SHA |

## 9. Definition of done

- Phases 1 to 4 and 6 completed, Phase 5 merged to `main`.
- Every check in Phase 7 recorded as passed.
- The homepage URL, the SHA currently deployed and the S3 bucket name are written in DOCKER_PIPELINE.md.
- The ECR pull of our image addresses works (Phase 2.3), and the platform team has confirmed the IAM role, the lifecycle rule and the log retention in writing.
