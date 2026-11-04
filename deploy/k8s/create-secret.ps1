<#
.SYNOPSIS
  Creates (or updates) the namespace and the Secret 'refua-tests-env' for the runner deployment.

.DESCRIPTION
  The Secret holds the .env.<env> values (AUTOMATION_SECRET, ORM_DB_*, SEED_ALLOWED_PERSONAL_NUMBERS, ...) plus
  SERVICE_API_TOKEN. It is created straight from files on this PC and is never written into the repository.
  Only key names are printed, never values.

  -Context is mandatory on purpose: the script acts on exactly that kubectl context and nothing else.

.EXAMPLE
  .\deploy\k8s\create-secret.ps1 -Context kind-refua-rehearsal
.EXAMPLE
  .\deploy\k8s\create-secret.ps1 -Context <eks-context> -EnvFile C:\secure\env.test
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Context,
    [string]$Namespace = 'refua-tests',
    [string]$SecretName = 'refua-tests-env',
    [string]$EnvFile = (Join-Path $env:USERPROFILE 'refua-docker\env.test'),
    [string]$TokenFile = (Join-Path $env:USERPROFILE 'refua-docker\service_token.txt')
)

$ErrorActionPreference = 'Stop'
$MinTokenLength = 16
$temporary = $null

try {
    if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) { throw 'kubectl is not installed.' }

    $known = & kubectl config get-contexts -o name
    if ($known -notcontains $Context) { throw "kubectl context '$Context' does not exist. Known contexts: $($known -join ', ')" }
    if (-not (Test-Path $EnvFile)) { throw "Env file not found: $EnvFile (see docs/guides/RUN_IMAGE_WITH_REAL_TESTS.md, step 2)" }

    if (Test-Path $TokenFile) {
        $token = (Get-Content $TokenFile -Raw).Trim()
        $tokenSource = "read from $TokenFile"
    }
    else {
        $token = [Convert]::ToBase64String((1..24 | ForEach-Object { Get-Random -Maximum 256 }))
        [IO.File]::WriteAllText($TokenFile, $token)
        $tokenSource = "generated and saved to $TokenFile"
    }
    if ($token.Length -lt $MinTokenLength) { throw "SERVICE_API_TOKEN must have at least $MinTokenLength characters." }

    $clean = Get-Content $EnvFile |
        Where-Object { $_ -match '^[A-Za-z_][A-Za-z0-9_]*=' -and $_ -notmatch '^(SERVICE_API_TOKEN|SERVICE_REQUIRE_TOKEN)=' } |
        ForEach-Object { ($_ -replace '\s+#.*$', '').TrimEnd() }
    $clean = @($clean) + "SERVICE_API_TOKEN=$token"

    $temporary = [IO.Path]::GetTempFileName()
    [IO.File]::WriteAllText($temporary, ($clean -join "`n") + "`n")

    Write-Host "Target kubectl context: $Context   namespace: $Namespace   secret: $SecretName"
    Write-Host "SERVICE_API_TOKEN $tokenSource"

    & kubectl --context $Context create namespace $Namespace --dry-run=client -o yaml | & kubectl --context $Context apply -f - | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Could not create the namespace.' }

    & kubectl --context $Context -n $Namespace create secret generic $SecretName --from-env-file=$temporary --dry-run=client -o yaml |
        & kubectl --context $Context apply -f - | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Could not create the secret.' }

    $keys = (& kubectl --context $Context -n $Namespace get secret $SecretName -o json | ConvertFrom-Json).data.PSObject.Properties.Name
    Write-Host "Secret '$SecretName' holds $(@($keys).Count) keys: $(@($keys | Sort-Object) -join ', ')"
    foreach ($required in 'SERVICE_API_TOKEN', 'AUTOMATION_SECRET', 'ORM_DB_HOST') {
        if ($keys -notcontains $required) { Write-Warning "Key $required is missing in the secret." }
    }
}
finally {
    if ($temporary -and (Test-Path $temporary)) { Remove-Item $temporary -Force }
}
