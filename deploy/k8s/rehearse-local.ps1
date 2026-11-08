<#
.SYNOPSIS
  Rehearses the whole deployment on a throwaway local kind cluster, before touching AWS.

.DESCRIPTION
  1. creates a kind cluster (skipped if it exists) and loads the image from the local Docker into it
  2. creates the namespace and the Secret (create-secret.ps1)
  3. applies the 'local' overlay (one replica, volume, probes)
  4. waits for the pod, then checks health, token rule and build info through a port-forward
  5. writes a marker file to the volume, deletes the pod, and checks the marker survived (restart test)

  Nothing here starts a test run, so the TEST database is not touched.
  Needs Docker Desktop, kind and kubectl. The image must already be in the local Docker (docker pull / docker images).

.EXAMPLE
  .\deploy\k8s\rehearse-local.ps1
.EXAMPLE
  .\deploy\k8s\rehearse-local.ps1 -Cleanup     # also deletes the cluster at the end
#>
[CmdletBinding()]
param(
    [string]$ClusterName = 'refua-rehearsal',
    [string]$Image = 'ghcr.io/digitalidf/refuaautomationtests/refua-automation-tests:f239b6656389',
    [int]$LocalPort = 8081,
    [switch]$Cleanup
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot | Split-Path -Parent
$context = "kind-$ClusterName"
$namespace = 'refua-tests'
$failed = $false
$forward = $null

function Report([string]$name, [bool]$ok, [string]$detail = '') {
    $mark = if ($ok) { 'PASS' } else { 'FAIL' }
    if (-not $ok) { $script:failed = $true }
    Write-Host ("{0} {1} {2}" -f $mark, $name, $detail)
}
function Kube { & kubectl --context $context -n $namespace @args }

try {
    foreach ($tool in 'docker', 'kind', 'kubectl') {
        if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) { throw "$tool is not installed." }
    }
    & docker image inspect $Image *> $null
    if ($LASTEXITCODE -ne 0) { throw "Image not found in the local Docker: $Image (docker pull it first)." }

    $existing = & kind get clusters 2>$null
    if ($existing -notcontains $ClusterName) {
        Write-Host "Creating kind cluster $ClusterName ..."
        & kind create cluster --name $ClusterName --wait 120s
        if ($LASTEXITCODE -ne 0) { throw 'kind create cluster failed.' }
    }
    else { Write-Host "Using existing kind cluster $ClusterName" }

    Write-Host "Loading the image into the cluster (a few GB; takes a while) ..."
    & kind load docker-image $Image --name $ClusterName
    if ($LASTEXITCODE -ne 0) { throw 'kind load docker-image failed.' }

    & (Join-Path $PSScriptRoot 'create-secret.ps1') -Context $context -Namespace $namespace

    $tag = $Image.Split(':')[-1]
    $overlay = Join-Path $PSScriptRoot 'overlays\local'
    $rendered = (& kubectl kustomize $overlay) -join "`n"
    if ($LASTEXITCODE -ne 0) { throw 'kubectl kustomize failed.' }
    $rendered = $rendered -replace '(refua-automation-tests):[A-Za-z0-9_.-]+', "`$1:$tag"
    $rendered | & kubectl --context $context apply -f -
    if ($LASTEXITCODE -ne 0) { throw 'kubectl apply failed.' }
    & kubectl --context $context -n $namespace rollout status deployment/refua-tests --timeout=300s
    Report 'pod is ready (readiness probe on /api/health)' ($LASTEXITCODE -eq 0)

    $replicas = (Kube get deployment refua-tests -o json | ConvertFrom-Json).spec.replicas
    Report 'single replica' ($replicas -eq 1) "replicas=$replicas"

    $forward = Start-Process -FilePath kubectl -ArgumentList "--context $context -n $namespace port-forward svc/refua-tests ${LocalPort}:80" -PassThru -WindowStyle Hidden
    Start-Sleep -Seconds 4
    $base = "http://127.0.0.1:$LocalPort"

    $health = Invoke-RestMethod "$base/api/health"
    Report 'health' ($health.status -eq 'ok' -and $health.allure) ($health | ConvertTo-Json -Compress)

    $options = Invoke-RestMethod "$base/api/options"
    Report 'token is required (token_required)' ([bool]$options.token_required)

    $code = 0
    try { Invoke-RestMethod -Method Post -Uri "$base/api/runs" -ContentType 'application/json' -Body '{"system":"meditik","suite":"bdd","tags":"home","user":"4444401","env":"test","clean":true}' | Out-Null; $code = 201 }
    catch { $code = [int]$_.Exception.Response.StatusCode }
    Report 'start without token is refused' ($code -eq 401) "HTTP $code"

    $info = Kube exec deploy/refua-tests '--' python -c "import json; from refua_service import buildinfo; print(json.dumps(buildinfo.collect()))" | ConvertFrom-Json
    Report 'build info image_tag equals the deployed tag' ($info.image_tag -eq $tag) "image_tag=$($info.image_tag) core=$($info.core_version)"

    Kube exec deploy/refua-tests '--' sh -c 'echo rehearsal > /data/rehearsal-marker'
    Kube delete pod -l app=refua-tests --wait=true | Out-Null
    & kubectl --context $context -n $namespace rollout status deployment/refua-tests --timeout=300s
    $marker = (Kube exec deploy/refua-tests '--' cat /data/rehearsal-marker) -join ''
    Report 'data survives a pod restart (volume)' ($marker.Trim() -eq 'rehearsal')
    Kube exec deploy/refua-tests '--' rm -f /data/rehearsal-marker | Out-Null
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $failed = $true
}
finally {
    if ($forward -and -not $forward.HasExited) { Stop-Process -Id $forward.Id -Force }
    if ($Cleanup) { Write-Host 'Deleting the kind cluster ...'; & kind delete cluster --name $ClusterName }
}

if ($failed) { Write-Host 'RESULT: FAILED'; exit 1 }
Write-Host 'RESULT: OK'
exit 0
