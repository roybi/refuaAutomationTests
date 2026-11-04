<#
.SYNOPSIS
  Phase 2 check: pull the tests image through the organization's ECR pull-through cache and verify it.

.DESCRIPTION
  1. Checks docker and the AWS CLI are installed, and that the AWS profile is logged in (VPN needed).
  2. Logs docker in to ECR, pulls <registry>/ghcr/<owner>/<repo>/<image>:<tag>.
  3. Compares the pulled digest with -ExpectedDigest (the digest printed by the build workflow).
  4. Starts the image once to read the build info (image tag and git sha) that every run record contains.

  Run from anywhere. Nothing is written except the docker login and the pulled image.

.EXAMPLE
  .\tools\ecr_pull_check.ps1 -Profile my-sso-profile -ExpectedDigest sha256:9a05...
.EXAMPLE
  .\tools\ecr_pull_check.ps1 -Profile my-sso-profile -Tag f239b6656389
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Profile,
    [string]$Tag,
    [string]$ExpectedDigest,
    [string]$Account = '373007444960',
    [string]$Region = 'il-central-1',
    [string]$Owner = 'digitalidf',
    [string]$Repo = 'refuaautomationtests',
    [string]$Image = 'refua-automation-tests',
    [string]$GitHubRepo = 'DigitalIDF/refuaAutomationTests',
    [switch]$SkipBuildInfo
)

$ErrorActionPreference = 'Stop'
$script:failed = $false

function Report([string]$name, [bool]$ok, [string]$detail = '') {
    $mark = if ($ok) { 'PASS' } else { 'FAIL'; $script:failed = $true }
    Write-Host ("{0} {1} {2}" -f $mark, $name, $detail)
}

function Need([string]$command, [string]$hint) {
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) { throw "$command is not installed. $hint" }
}

try {
    Need 'docker' 'Install Docker Desktop and start it.'
    Need 'aws' 'Install the AWS CLI v2 (winget install Amazon.AWSCLI), then: aws configure sso --profile <name>'

    $registry = "$Account.dkr.ecr.$Region.amazonaws.com"
    $repository = "ghcr/$Owner/$Repo/$Image"

    if (-not $Tag) {
        Need 'gh' 'Pass -Tag <first 12 characters of the commit on main> instead.'
        $sha = (& gh api "repos/$GitHubRepo/commits/main" --jq '.sha').Trim()
        $Tag = $sha.Substring(0, 12)
        Write-Host "Tag not given: using the head of main, $Tag"
    }
    $reference = "$registry/${repository}:$Tag"

    $identity = & aws sts get-caller-identity --profile $Profile --region $Region --output json 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "AWS login failed for profile '$Profile'. Run: aws sso login --profile $Profile (and connect the VPN). Details: $identity"
    }
    $account = ($identity | ConvertFrom-Json).Account
    Report 'AWS login' ($account -eq $Account) "account $account (expected $Account)"

    $password = & aws ecr get-login-password --profile $Profile --region $Region
    if ($LASTEXITCODE -ne 0 -or -not $password) { throw 'aws ecr get-login-password failed (no ECR permission?)' }
    $password | & docker login --username AWS --password-stdin $registry | Out-Null
    Report 'docker login to ECR' ($LASTEXITCODE -eq 0) $registry

    Write-Host "Pulling $reference (the first pull makes ECR fetch it from ghcr.io; this can take minutes)"
    & docker pull $reference
    $pulled = ($LASTEXITCODE -eq 0)
    Report 'docker pull' $pulled $reference
    if (-not $pulled) { throw 'Pull failed. If the error says not found or access denied, see plan step 2.5 (package visibility, ECR prefix permission).' }

    $digest = (& docker image inspect $reference --format '{{index .RepoDigests 0}}').Split('@')[1]
    Write-Host "Pulled digest: $digest"
    if ($ExpectedDigest) { Report 'digest equals the published image' ($digest -eq $ExpectedDigest) "expected $ExpectedDigest" }
    else { Write-Host 'No -ExpectedDigest given: compare the digest above with the build workflow log.' }

    if (-not $SkipBuildInfo) {
        $token = [Convert]::ToBase64String((1..24 | ForEach-Object { Get-Random -Maximum 256 }))
        $code = 'import json; from refua_service import buildinfo; print(json.dumps(buildinfo.collect()))'
        $json = & docker run --rm -e "SERVICE_API_TOKEN=$token" $reference python -c $code
        $info = $json | ConvertFrom-Json
        Write-Host "Build info: $json"
        Report 'build info image_tag equals the tag' ($info.image_tag -eq $Tag) "image_tag=$($info.image_tag)"
        Report 'build info has git sha and core version' ([bool]$info.git_sha -and [bool]$info.core_version) "git_sha=$($info.git_sha) core=$($info.core_version)"

        & docker run --rm $reference python -c 'from refua_service.settings import load_settings; load_settings()' *> $null
        Report 'image refuses to start without a token' ($LASTEXITCODE -ne 0)
    }
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $script:failed = $true
}

if ($script:failed) { Write-Host 'RESULT: FAILED'; exit 1 }
Write-Host 'RESULT: OK'
exit 0
