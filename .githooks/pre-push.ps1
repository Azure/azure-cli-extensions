Write-Host "Running pre-push hook in powershell..." -ForegroundColor Green

# run azdev_active script
$scriptPath = Join-Path $PSScriptRoot "azdev_active.ps1"
. $scriptPath
if ($LASTEXITCODE -ne 0) {
    exit 1
}

# Check if azure-cli is installed in editable mode
$pipShowOutput = pip show azure-cli 2>&1
$editableLocation = if ($pipShowOutput) {
    $match = $pipShowOutput | Select-String "Editable project location: (.+)"
    if ($match) {
        $match.Matches.Groups[1].Value
    }
}
if ($editableLocation) {
    # get the parent of parent directory of the editable location
    $AZURE_CLI_FOLDER = Split-Path -Parent (Split-Path -Parent $editableLocation)
}

$ExtensionRepo = Split-Path -Parent  $PSScriptRoot

# verify if the $ExtensionRepo is in the output of azdev extension repo list
$Extensions = (azdev extension repo list -o tsv) -join ' '
if ($Extensions -notlike "*$ExtensionRepo*") {
    Write-Host "The current repo is not added as an extension repo. Please run the following command to add it:" -ForegroundColor Red
    Write-Host "+++++++++++++++++++++++++++++++++++++++++++++++++++++++" -ForegroundColor Red
    Write-Host "azdev extension repo add $ExtensionRepo" -ForegroundColor Red
    Write-Host "+++++++++++++++++++++++++++++++++++++++++++++++++++++++" -ForegroundColor Red
    exit 1
}

# Fetch upstream/main branch
Write-Host "Fetching upstream/main branch..." -ForegroundColor Green
git fetch upstream main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to fetch upstream/main branch. Please run the following command to add the upstream remote:" -ForegroundColor Red
    Write-Host "+++++++++++++++++++++++++++++++++++++++++++++++++++++++" -ForegroundColor Red
    Write-Host "git remote add upstream https://github.com/Azure/azure-cli-extensions.git" -ForegroundColor Red
    Write-Host "+++++++++++++++++++++++++++++++++++++++++++++++++++++++" -ForegroundColor Red
    exit 1
}

if ($AZURE_CLI_FOLDER) {
    # run git fetch upstream/dev for the AZURE_CLI_FOLDER and check if it is successful
    Write-Host "Fetching $AZURE_CLI_FOLDER upstream/dev branch..." -ForegroundColor Green
    git -C $AZURE_CLI_FOLDER fetch upstream dev
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to fetch $AZURE_CLI_FOLDER upstream/dev branch. Please run the following command to add the upstream remote:" -ForegroundColor Red
        Write-Host "+++++++++++++++++++++++++++++++++++++++++++++++++++++++" -ForegroundColor Red
        Write-Host "git -C $AZURE_CLI_FOLDER remote add upstream https://github.com/Azure/azure-cli.git" -ForegroundColor Red
        Write-Host "+++++++++++++++++++++++++++++++++++++++++++++++++++++++" -ForegroundColor Red
        exit 1
    }

    # Check if current branch needs rebasing
    $cliMergeBase = git -C $AZURE_CLI_FOLDER merge-base HEAD upstream/dev
    $cliUpstreamHead = git -C $AZURE_CLI_FOLDER rev-parse upstream/dev
    if ($cliMergeBase -ne $cliUpstreamHead) {
        Write-Host ""
        Write-Host "Your $AZURE_CLI_FOLDER repo code is not up to date with upstream/dev. Please run the following commands to rebase and setup:" -ForegroundColor Yellow
        Write-Host "+++++++++++++++++++++++++++++++++++++++++++++++++++++++" -ForegroundColor Yellow
        Write-Host "git -C $AZURE_CLI_FOLDER rebase upstream/dev" -ForegroundColor Yellow
        if ($Extensions) {
            Write-Host "azdev setup -c $AZURE_CLI_FOLDER -r $Extensions" -ForegroundColor Yellow
        } else {
            Write-Host "azdev setup -c $AZURE_CLI_FOLDER" -ForegroundColor Yellow
        }
        Write-Host "+++++++++++++++++++++++++++++++++++++++++++++++++++++++" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "You have 5 seconds to stop the push (Ctrl+C)..." -ForegroundColor Yellow
        for ($i = 5; $i -gt 0; $i--) {
            Write-Host "`rTime remaining: $i seconds..." -NoNewline -ForegroundColor Yellow
            Start-Sleep -Seconds 1
        }
        Write-Host "`rContinuing without rebase..."
    }
}

# Check if current branch needs rebasing
$mergeBase = git merge-base HEAD upstream/main

# get the current branch name
$currentBranch = git branch --show-current

# detect all extension folder names changed under src/
$changedFiles = git diff --name-only $mergeBase $currentBranch
$changedExtensions = $changedFiles | 
    Where-Object { $_ -like "src/*" } | 
    ForEach-Object { 
        $parts = $_ -split '/'
        if ($parts.Length -gt 1) { $parts[1] }
    } | 
    Select-Object -Unique

if ($changedExtensions) {
    Write-Host "Changed extensions: $($changedExtensions -join ', ')" -ForegroundColor Green
    
    # Add each changed extension using azdev extension add
    foreach ($extension in $changedExtensions) {
        Write-Host "Adding extension: $extension"
        azdev extension add $extension
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Error: Failed to add extension $extension" -ForegroundColor Red
            exit 1
        }
    }
}

# Run command azdev lint
Write-Host "Running azdev lint..." -ForegroundColor Green
azdev linter --min-severity medium --repo ./ --src $currentBranch --tgt $mergeBase
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: azdev lint check failed." -ForegroundColor Red
    exit 1
}

# Run command azdev style
Write-Host "Running azdev style..." -ForegroundColor Green
azdev style --repo ./ --src $currentBranch --tgt $mergeBase
if ($LASTEXITCODE -ne 0) {
    $error_msg = azdev style --repo ./ --src $currentBranch --tgt $mergeBase 2>&1
    if ($error_msg -like "*No modules*") {
        Write-Host "Pre-push hook passed." -ForegroundColor Green
        exit 0
    }
    Write-Host "Error: azdev style check failed." -ForegroundColor Red
    exit 1
}

# Run command azdev test
Write-Host "Running azdev test..." -ForegroundColor Green
azdev test --repo ./ --src $currentBranch --tgt $mergeBase --discover --no-exitfirst --xml-path test_results.xml 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: azdev test check failed. You can check the test logs in the 'test_results.xml' file." -ForegroundColor Red
    exit 1
} else {
    # remove the test_results.xml file
    Remove-Item -Path test_results.xml
}

Write-Host "Pre-push hook passed." -ForegroundColor Green

if ($AZURE_CLI_FOLDER) {
    if ($cliMergeBase -ne $cliUpstreamHead) {
        Write-Host ""
        Write-Host "Your $AZURE_CLI_FOLDER repo code is not up to date with upstream/dev. Please run the following commands to rebase and setup:" -ForegroundColor Yellow
        Write-Host "+++++++++++++++++++++++++++++++++++++++++++++++++++++++" -ForegroundColor Yellow
        Write-Host "git -C $AZURE_CLI_FOLDER rebase upstream/dev" -ForegroundColor Yellow
        if ($Extensions) {
            Write-Host "azdev setup -c $AZURE_CLI_FOLDER -r $Extensions" -ForegroundColor Yellow
        } else {
            Write-Host "azdev setup -c $AZURE_CLI_FOLDER" -ForegroundColor Yellow
        }
        Write-Host "+++++++++++++++++++++++++++++++++++++++++++++++++++++++" -ForegroundColor Yellow
    }
}
exit 0
