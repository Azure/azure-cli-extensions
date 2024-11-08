Write-Host "Running pre-push hook in powershell..." -ForegroundColor Green

# Check if in the python environment
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Path
Write-Host "Python file path: $pythonPath"

if (-not $pythonPath) {
    Write-Host "Error: Python not found in PATH" -ForegroundColor Red
    exit 1
}

$pythonEnvFolder = Split-Path -Parent (Split-Path -Parent $pythonPath)
$pythonActiveFile = Join-Path $pythonEnvFolder "Scripts\activate.ps1"

if (-not (Test-Path $pythonActiveFile)) {
    Write-Host "Python active file does not exist: $pythonActiveFile" -ForegroundColor Red
    Write-Host "Error: Please activate the python environment first." -ForegroundColor Red
    exit 1
}

# Construct the full path to the .azdev\env_config directory
$azdevEnvConfigFolder = Join-Path $env:USERPROFILE ".azdev\env_config"
Write-Host "AZDEV_ENV_CONFIG_FOLDER: $azdevEnvConfigFolder"

# Check if the directory exists
if (-not (Test-Path $azdevEnvConfigFolder)) {
    Write-Host "AZDEV_ENV_CONFIG_FOLDER does not exist: $azdevEnvConfigFolder" -ForegroundColor Red
    Write-Host "Error: azdev environment is not completed, please run 'azdev setup' first." -ForegroundColor Red
    exit 1
}

$configFile = Join-Path $azdevEnvConfigFolder ($pythonEnvFolder.Substring(2) + "\config")
if (-not (Test-Path $configFile)) {
    Write-Host "CONFIG_FILE does not exist: $configFile" -ForegroundColor Red
    Write-Host "Error: azdev environment is not completed, please run 'azdev setup' first." -ForegroundColor Red
    exit 1
}

Write-Host "CONFIG_FILE: $configFile"

# Fetch upstream/main branch
Write-Host "Fetching upstream/main branch..." -ForegroundColor Green
git fetch upstream main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to fetch upstream/main branch. Please run 'git remote add upstream https://github.com/Azure/azure-cli-extensions.git' first." -ForegroundColor Red
    exit 1
}

# Run command azdev style
Write-Host "Running azdev style..." -ForegroundColor Green
# get the current branch name
$currentBranch = git branch --show-current
azdev style --repo ./ --tgt $currentBranch --src upstream/main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: azdev style check failed." -ForegroundColor Red
    exit 1
}

# Run command azdev lint
Write-Host "Running azdev lint..." -ForegroundColor Green
azdev linter --repo azure-cli-extensions --src upstream/main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: azdev lint check failed." -ForegroundColor Red
    exit 1
}

# Run command azdev test
Write-Host "Running azdev test..." -ForegroundColor Green
azdev test --repo azure-cli-extensions --src upstream/main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: azdev test check failed." -ForegroundColor Red
    exit 1
}

exit 0
