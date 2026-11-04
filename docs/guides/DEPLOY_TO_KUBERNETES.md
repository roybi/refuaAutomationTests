# Deploy the runner to Kubernetes (plan Phase 3, by hand)

What this sets up: the runner website in one pod (single replica), a volume for the run data, and a Secret with the
`.env.<env>` values and the API token. Files are in `deploy/k8s/`:

| File | Purpose |
|---|---|
| `base/` | Namespace, service account, volume claim, Deployment (1 replica, `Recreate`, probes), Service |
| `overlays/local/` | Rehearsal on a local kind cluster (small volume, image loaded from local Docker) |
| `overlays/aws/` | AWS: ECR pull-through image address, `gp3` volume of 50 Gi |
| `create-secret.ps1` | Creates the namespace and the Secret from your env file plus the token |
| `rehearse-local.ps1` | Runs the whole sequence on a throwaway kind cluster and checks the result |

Why these settings (checked on the published image `f239b6656389`):
- **One replica, `Recreate`:** the run queue and the test processes live inside the service, and the DB seed has a per-user lock.
- **User and group 1001:** the image runs as `pwuser`, which is uid/gid 1001 (`docker exec <container> id`), not 1000.
- **`/dev/shm` as an in-memory volume (1 Gi):** the default of 64 MB is too small for Chromium in a pod.
- **The token is required:** the image does not start without `SERVICE_API_TOKEN` (16+ characters). The pod stays in `CrashLoopBackOff`
  with the error `SERVICE_REQUIRE_TOKEN is on but SERVICE_API_TOKEN is not set` if the Secret lacks it.
- **The Secret is never in git:** it is created from files on your PC by `create-secret.ps1`, and only key names are printed.

## Part 1: Rehearse on your PC (no AWS needed)

Needs Docker Desktop, `kind` and `kubectl`. The image must be in your local Docker (`docker images` shows it).
A kind cluster plus the image copy needs about 5 GB of disk and 1 to 2 GB of memory.

```powershell
.\deploy\k8s\rehearse-local.ps1            # add -Cleanup to delete the cluster afterwards
```

It prints PASS or FAIL for: pod ready, single replica, health, token required, start without a token refused,
build info equals the deployed tag, and data surviving a pod restart. No test run is started, so the TEST database is untouched.

Same steps by hand:
```powershell
kind create cluster --name refua-rehearsal
kind load docker-image ghcr.io/digitalidf/refuaautomationtests/refua-automation-tests:f239b6656389 --name refua-rehearsal
.\deploy\k8s\create-secret.ps1 -Context kind-refua-rehearsal
kubectl --context kind-refua-rehearsal apply -k deploy/k8s/overlays/local
kubectl --context kind-refua-rehearsal -n refua-tests rollout status deployment/refua-tests
kubectl --context kind-refua-rehearsal -n refua-tests port-forward svc/refua-tests 8081:80
```
Then open http://localhost:8081. The token is in `%USERPROFILE%\refua-docker\service_token.txt`.

## Part 2: Deploy on AWS (needs the platform team)

You need: a kubectl context for the cluster, permission to create a namespace, secrets and a volume claim in it,
and a cluster node role that can pull from the ECR address (plan Phase 2, assumed OK until the first pull).

1. **Pick the context.** `kubectl config get-contexts`, then use `--context <name>` on every command. Never rely on the current context.
2. **Check the target.** `kubectl --context <name> get nodes` and `kubectl --context <name> get storageclass`.
   The AWS overlay asks for the storage class `gp3`; change `storageClassName` in `overlays/aws/kustomization.yaml` if the cluster uses another one.
3. **Create the Secret** (uses your env file and the token file):
   ```powershell
   .\deploy\k8s\create-secret.ps1 -Context <name>
   ```
   For a shared cluster use a fresh token (delete or rename `service_token.txt` first) and hand it over through your password manager, not chat.
4. **Pick the image tag.** Edit `newTag` in `overlays/aws/kustomization.yaml` to the commit SHA of the build you want
   (12 characters, from the "Push images" step of the build workflow). Never `latest`.
5. **Preview, then apply:**
   ```powershell
   kubectl --context <name> apply -k deploy/k8s/overlays/aws --dry-run=server
   kubectl --context <name> apply -k deploy/k8s/overlays/aws
   kubectl --context <name> -n refua-tests rollout status deployment/refua-tests --timeout=600s
   ```
6. **Check.**
   ```powershell
   kubectl --context <name> -n refua-tests get pods,pvc
   kubectl --context <name> -n refua-tests port-forward svc/refua-tests 8081:80
   ```
   Open http://localhost:8081 or call `/api/health` (expect `status ok`, `allure true`).
7. **Verify the image that runs is the one you built** (a green health check can pass on a stale pod):
   ```powershell
   kubectl --context <name> -n refua-tests exec deploy/refua-tests -- python -c "from refua_service import buildinfo; print(buildinfo.collect())"
   ```
   `image_tag` must equal the tag from step 4.
8. **Restart test:** `kubectl --context <name> -n refua-tests delete pod -l app=refua-tests`, wait until Ready, and check that earlier runs are still listed.

Later (other plan steps): attach the S3 role to the service account (`eks.amazonaws.com/role-arn` annotation) and add
`ARCHIVE_S3_BUCKET` to the Deployment env (Phase 4); decide how users reach the page (Phase 6, plan D2).

## If something fails

| Symptom | Likely cause and fix |
|---|---|
| `ErrImagePull` / `ImagePullBackOff` on the ECR address | The ECR pull was never verified (plan Phase 2). Send the Phase 2 request to the platform team with the exact error from `kubectl describe pod` |
| `CrashLoopBackOff`, log says `SERVICE_API_TOKEN is not set` or `at least 16 characters` | The Secret is missing the token or it is too short: rerun `create-secret.ps1`, then `kubectl rollout restart deployment/refua-tests -n refua-tests` |
| Pod `Pending`, event `unbound immediate PersistentVolumeClaims` | No matching storage class, or no capacity: check `get storageclass` and the claim's events |
| `Permission denied` writing to `/data` | `fsGroup` does not match the image user (must be 1001) or the volume type ignores `fsGroup` |
| Chromium crashes during a run | `/dev/shm` too small; the manifest mounts a 1 Gi in-memory volume, check it is present and the memory limit leaves room (4 Gi) |
| Runs fail at login or DB access | The pod has no network path to TEST or its database, or the env file lacks `AUTOMATION_SECRET` / `ORM_DB_*` |
| Two pods share the volume | The strategy must stay `Recreate` and `replicas: 1` |
