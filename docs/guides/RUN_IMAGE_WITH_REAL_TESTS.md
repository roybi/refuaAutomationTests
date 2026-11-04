# Run the container image with real tests (step by step)

Goal: prove that the **published image** runs real tests against TEST, starts from the website, produces an Allure report and keeps
its data across a restart. Windows + Docker Desktop + PowerShell.

> **This writes to the TEST database.** Every run seeds rows for the chosen user (about 33 rows per run, kept by default),
> exactly like running `run_tests.py` on your machine. Use an approved test user from `SEED_ALLOWED_PERSONAL_NUMBERS`.
> The env file in step 2 contains secrets: keep it outside the repository and delete it at the end (step 10).

## Before you start

- [ ] VPN connected (you need the same network access as for a normal run: TEST application **and** its database).
- [ ] Docker Desktop is running (`docker version` shows a Server section).
- [ ] You are in the repository folder: `cd C:\_Dev\python\refuaAutomationTests`
- [ ] You know the test user (personal number) to use, e.g. `4444401`.

## Step 1 - Get the image

**Option A (fastest): the image already on your machine.** It was built from the same code as the published one:
```powershell
docker images refua-tests-local:test
```
Use `refua-tests-local:test` as `$IMAGE` below. (To rebuild it, see DOCKER_PIPELINE.md -> Build locally.)

**Option B (proves the published image): pull it from ghcr.io.** One-time login with a token that may read packages:
```powershell
gh auth refresh -s read:packages          # opens a browser; approve it
gh auth token | docker login ghcr.io -u <your-github-username> --password-stdin
docker pull ghcr.io/digitalidf/refuaautomationtests/refua-automation-tests:latest
```
Use `ghcr.io/digitalidf/refuaautomationtests/refua-automation-tests:latest` as `$IMAGE`.

```powershell
$IMAGE = "refua-tests-local:test"      # or the ghcr.io address from option B
```

## Step 2 - Make a clean env file (outside the repo)
Docker's `--env-file` does not understand Windows line endings or `# comments` after a value (it would glue them onto the value),
so create a cleaned copy of `.env.test`:
```powershell
$dir = "$env:USERPROFILE\refua-docker"
New-Item -ItemType Directory -Force $dir | Out-Null
$lines = Get-Content .env.test |
  Where-Object { $_ -match '^[A-Za-z_][A-Za-z0-9_]*=' } |
  ForEach-Object { ($_ -replace '\s+#.*$', '').TrimEnd() }
[IO.File]::WriteAllText("$dir\env.test", ($lines -join "`n") + "`n")
(Get-Content "$dir\env.test").Count      # number of variables, about 32
```
Check, **without printing values**, that the important keys are there:
```powershell
'AUTOMATION_SECRET','ORM_DB_HOST','ORM_DB_PASSWORD','SEED_ALLOWED_PERSONAL_NUMBERS','MEDITIK_SEED_ENV' |
  ForEach-Object { "{0,-32} {1}" -f $_, ((Select-String -Path "$dir\env.test" -Pattern "^$_=.+").Count -gt 0) }
```
All should say `True`.

## Step 3 - Check the container can reach TEST and the database
```powershell
docker run --rm --env-file "$dir\env.test" $IMAGE python -c "import urllib.request; print('app http', urllib.request.urlopen('https://meditik.test.medical.idf.il/home', timeout=30).status)"
docker run --rm --env-file "$dir\env.test" $IMAGE python -c "import os,socket; socket.create_connection((os.environ['ORM_DB_HOST'], int(os.environ.get('ORM_DB_PORT','5432'))), 15); print('db port reachable')"
```
Expected: `app http 200` and `db port reachable`. If one fails, fix the network first (see Troubleshooting); a test run would fail too.

## Step 4 - Start the service
```powershell
docker volume create refua-data
$TOKEN = [Convert]::ToBase64String((1..24 | ForEach-Object { Get-Random -Maximum 256 }))   # any random value of 16+ characters
docker run -d --name refua-svc -p 8080:8080 -v refua-data:/data --env-file "$dir\env.test" -e SERVICE_API_TOKEN=$TOKEN $IMAGE
Start-Sleep 8
Invoke-RestMethod http://localhost:8080/api/health
```
Expected: `status ok` and `allure True`. If not: `docker logs refua-svc`.
The image refuses to start without `SERVICE_API_TOKEN` (at least 16 characters; the log says `SERVICE_REQUIRE_TOKEN is on but SERVICE_API_TOKEN is not set`). Keep `echo $TOKEN` for step 5.

## Step 5 - Open the website and start a run
1. Open http://localhost:8080
2. System `meditik`, Suite `bdd`, Tag `home` (a small set, about 15 scenarios), User = your test user, Environment `test`, Clean on.
3. Enter the token from step 4 in the **API token** field (starting and cancelling runs need it).
4. Check the command preview matches what you expect, then **Start run**.
5. Watch the live log. A healthy start shows `System: meditik | User: <your user> | Env: test`, then the DB seeding lines, then scenarios.

## Step 6 - Judge the result
- Status ends as `passed` or `failed` (red scenarios are normal if the application has issues; what matters is that tests **ran**).
- The Results column shows pass/fail/skipped counts, and **Open Allure report** works.
- Compare with a normal run on your machine for the same tag and user:
  `.\venv\Scripts\python.exe run_tests.py --system meditik --tags home --user <user> --env test --clean`.
  The counts should be broadly the same. (The image installs newer pytest/pytest-bdd than your venv, so tell me about any difference.)
- Red flags: `AUTOMATION_SECRET is required` (env file missing the key), redirect to a Microsoft login page (wrong/expired secret),
  `could not connect` to the DB (network), HTTP 429 (TEST rate limit: wait a few minutes).

## Step 7 - Run it twice and check the trend
Start a second run with the same parameters. Open its report: the trend/history graph should show both runs.

## Step 8 - Check that data survives a restart
```powershell
docker restart refua-svc
Start-Sleep 8
Invoke-RestMethod http://localhost:8080/api/runs | Select-Object id, status
```
Both runs are still listed, and their reports still open at http://localhost:8080/reports/latest.

## Step 9 - Optional: test cancel
Start a run with Tag `(all tests)`, then press **Cancel run** during the first minute. Status becomes `cancelled` and the log stops.

## Step 10 - Clean up (and delete the secrets)
```powershell
docker rm -f refua-svc
docker volume rm refua-data                      # removes the stored runs/reports (skip to keep them)
Remove-Item "$env:USERPROFILE\refua-docker\env.test"
```
Seeded rows stay in the TEST DB, as with any run (cleanup mode `report`).

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| Step 3 DB check fails, but works on the host | VPN routes are not used by Docker Desktop. Reconnect the VPN, then restart Docker Desktop, and retry |
| Step 3 app check fails with a certificate/timeout error | VPN not connected, or a corporate proxy: set `HTTPS_PROXY` with `-e` on the `docker run` |
| `AUTOMATION_SECRET is required` | The env file lacks the key (recheck step 2) or the value is empty |
| Run redirects to Microsoft login | The automation secret is wrong/expired for TEST |
| User rejected (HTTP 422) | The user is outside `SEED_ALLOWED_PERSONAL_NUMBERS`; use an allowed number |
| `Port 8080 is already in use` | Use `-p 8081:8080` and open http://localhost:8081, or stop `runService.bat` |
| Every scenario fails at once with `Executable doesn't exist at /ms-playwright/...` | The image is older than 2026-11-03: its Playwright package did not match the installed browsers. Pull/build the latest image |
| `Meditik DB seed skipped (... Missing .env.test ...)` | Same old image: the seed guard did not accept settings from environment variables. Pull/build the latest image |
| `2FA bypass enabled but session file missing` at the top of the log | Harmless: automation login does not use a saved session |
| Everything fails the same way | `docker logs refua-svc` and the run's log in the website, then send me the first error |
