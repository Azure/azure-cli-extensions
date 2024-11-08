#!/usr/bin/env pwsh
Write-Host "Running pre-commit hook in powershell..." -ForegroundColor Green

# run azdev_active script
$scriptPath = Join-Path $PSScriptRoot "azdev_active.ps1"
. $scriptPath
if ($LASTEXITCODE -ne 0) {
    exit 1
}

# Check if we have a previous commit to compare against
if (git rev-parse --verify HEAD 2>$null) {
    $against = "HEAD"
}
else {
    # Initial commit: diff against an empty tree object
    $against = $(git hash-object -t tree /dev/null)
}

$hasSecrets = 0
$files = $(git diff --cached --name-only --diff-filter=AM $against)

foreach ($file in $files) {
    # Check if the file contains secrets
    $detected = $(azdev scan -f $file | ConvertFrom-Json).secrets_detected
    if ($detected -eq "True") {
        Write-Host "Detected secrets from $file. You can run 'azdev mask' to remove secrets before commit." -ForegroundColor Red
        $hasSecrets = 1
    }
}

if ($hasSecrets -eq 1) {
    Write-Host "Secret detected. If you want to skip that, run add '--no-verify' in the end of 'git commit' command." -ForegroundColor Red
    exit 1
}
exit 0
