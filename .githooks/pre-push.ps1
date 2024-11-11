Write-Host "Running pre-push hook in powershell..." -ForegroundColor Green

# run azdev_active script
$scriptPath = Join-Path $PSScriptRoot "azdev_active.ps1"
. $scriptPath
if ($LASTEXITCODE -ne 0) {
    exit 1
}

# Fetch upstream/main branch
Write-Host "Fetching upstream/main branch..." -ForegroundColor Green
git fetch upstream main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to fetch upstream/main branch. Please run 'git remote add upstream https://github.com/Azure/azure-cli-extensions.git' first." -ForegroundColor Red
    exit 1
}

# get the current branch name
$currentBranch = git branch --show-current

# Run command azdev lint
Write-Host "Running azdev lint..." -ForegroundColor Green
azdev linter --repo ./ --src $currentBranch --tgt upstream/main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: azdev lint check failed." -ForegroundColor Red
    exit 1
}

# Run command azdev style
Write-Host "Running azdev style..." -ForegroundColor Green
azdev style --repo ./ --src $currentBranch --tgt upstream/main
if ($LASTEXITCODE -ne 0) {
    $error_msg = azdev style --repo ./ --src $currentBranch --tgt upstream/main 2>&1
    if ($error_msg -like "*No modules*") {
        Write-Host "Pre-push hook passed." -ForegroundColor Green
        exit 0
    }
    Write-Host "Error: azdev style check failed." -ForegroundColor Red
    exit 1
}

# Run command azdev test
Write-Host "Running azdev test..." -ForegroundColor Green
azdev test --repo ./ --src $currentBranch --tgt upstream/main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: azdev test check failed." -ForegroundColor Red
    exit 1
}

Write-Host "Pre-push hook passed." -ForegroundColor Green
exit 0
