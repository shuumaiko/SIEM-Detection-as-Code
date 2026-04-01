Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$omxSourceRoot = Join-Path $repoRoot ".vendor\oh-my-codex"
$omxCli = Join-Path $omxSourceRoot "dist\cli\omx.js"
$codexHome = Join-Path $repoRoot ".codex"

if (-not (Test-Path -LiteralPath $omxSourceRoot)) {
    throw "OMX source checkout was not found at '$omxSourceRoot'."
}

if (-not (Test-Path -LiteralPath $omxCli)) {
    throw @"
OMX CLI has not been built yet.

Build it first:
  cd $omxSourceRoot
  npm install
  npm run build
"@
}

New-Item -ItemType Directory -Path $codexHome -Force | Out-Null

$env:CODEX_HOME = $codexHome
Remove-Item Env:OMX_MODEL_INSTRUCTIONS_FILE -ErrorAction SilentlyContinue

if ($args.Count -eq 0) {
    Write-Host "Using project CODEX_HOME: $codexHome"
    Write-Host "Forwarding to local OMX source: $omxSourceRoot"
}

& node $omxCli @args
$exitCode = $LASTEXITCODE
if ($null -ne $exitCode) {
    exit $exitCode
}
