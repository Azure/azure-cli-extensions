[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$CloudName = "AzureLocal",

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9a-fA-F-]{36}$')]
    [string]$SubscriptionId,

    [Parameter(Mandatory = $true)]
    [string]$ResourceId,

    [Parameter(Mandatory = $true)]
    [string]$ResourceName,

    [Parameter(Mandatory = $true)]
    [string]$StampId,

    [Parameter(Mandatory = $false)]
    [string]$Location = "eastus",

    [Parameter(Mandatory = $false)]
    [string]$BillingModel = "Capacity",

    [Parameter(Mandatory = $false)]
    [string]$ConnectionIntent = "Connected",

    [Parameter(Mandatory = $false)]
    [string]$AutoRenew = "Enabled",

    [Parameter(Mandatory = $false)]
    [string]$BillingStatus = "Enabled",

    [Parameter(Mandatory = $false)]
    [int]$CurrentCores = 12,

    [Parameter(Mandatory = $false)]
    [string]$CurrentPricingModel = "Trial",

    [Parameter(Mandatory = $false)]
    [string]$CurrentStartDate = "2025-11-01",

    [Parameter(Mandatory = $false)]
    [string]$CurrentEndDate = "2025-12-31",

    [Parameter(Mandatory = $false)]
    [string]$Cloud = "Public",

    [Parameter(Mandatory = $false)]
    [int]$UpcomingCores = 24,

    [Parameter(Mandatory = $false)]
    [string]$UpcomingPricingModel = "Annual",

    [Parameter(Mandatory = $false)]
    [string]$UpcomingStartDate = "2026-01-01",

    [Parameter(Mandatory = $false)]
    [string]$UpcomingEndDate,

    [Parameter(Mandatory = $false)]
    [string]$AzureHybridWindowsServerBenefit = "Enabled",

    [Parameter(Mandatory = $false)]
    [int]$WindowsServerVmCount = 5,

    [Parameter(Mandatory = $false)]
    [string]$SnapshotName,

    [Parameter(Mandatory = $false)]
    [switch]$UseDeviceCode,

    [Parameter(Mandatory = $false)]
    [switch]$SkipCreateOrUpdate,

    [Parameter(Mandatory = $false)]
    [switch]$RunNegativeValidation
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Invoke-AzJson {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Args,
        [Parameter(Mandatory = $true)]
        [string]$Description,
        [switch]$ExpectFailure
    )

    Write-Host "[az] $($Args -join ' ')" -ForegroundColor DarkGray

    $raw = & az @Args 2>&1
    $exit = $LASTEXITCODE

    if ($ExpectFailure) {
        if ($exit -eq 0) {
            throw "Expected failure but command succeeded: $Description"
        }
        Write-Host "Expected failure observed: $Description" -ForegroundColor Yellow
        Write-Host ($raw | Out-String) -ForegroundColor DarkYellow
        return $null
    }

    if ($exit -ne 0) {
        $rawText = $raw | Out-String
        if ($rawText -match "CERTIFICATE_VERIFY_FAILED|certificate verify failed|SSL: CERTIFICATE_VERIFY_FAILED") {
            throw @"
Command failed ($Description) due to TLS certificate trust.

Action required:
1) Export your enterprise/proxy root CA chain to a PEM file.
2) Set one of these before running tests:
   - `$env:REQUESTS_CA_BUNDLE = "C:\path\enterprise-ca-chain.pem"`
   - az config set core.ca_bundle="C:\path\enterprise-ca-chain.pem"
3) Re-run the script.

Original output:
$rawText
"@
        }
        throw "Command failed ($Description). ExitCode=$exit`n$($raw | Out-String)"
    }

    if ($null -eq $raw -or [string]::IsNullOrWhiteSpace(($raw | Out-String))) {
        return $null
    }

    try {
        return ($raw | Out-String | ConvertFrom-Json)
    }
    catch {
        throw "Failed to parse JSON for: $Description`nRaw output:`n$($raw | Out-String)"
    }
}

function Ensure-AzLogin {
    param([switch]$UseDeviceCode)

    $null = & az account show --only-show-errors -o none 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Already logged in to Azure CLI." -ForegroundColor Green
        return
    }

    Write-Step "No active Azure CLI login found. Logging in"
    if ($UseDeviceCode) {
        & az login --use-device-code
    }
    else {
        & az login
    }

    if ($LASTEXITCODE -ne 0) {
        throw "az login failed."
    }
}

Write-Step "Checking az CLI availability"
$azVersionRaw = & az version 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "Azure CLI (az) is not available in PATH."
}
Write-Host "az is available." -ForegroundColor Green

Write-Step "Setting cloud to $CloudName"
& az cloud set --name $CloudName
if ($LASTEXITCODE -ne 0) {
    throw "Failed to set cloud: $CloudName"
}

Ensure-AzLogin -UseDeviceCode:$UseDeviceCode

Write-Step "Selecting subscription $SubscriptionId"
& az account set --subscription $SubscriptionId
if ($LASTEXITCODE -ne 0) {
    throw "Failed to set subscription: $SubscriptionId"
}

$activeSub = Invoke-AzJson -Args @("account", "show", "--query", "id", "-o", "json") -Description "Get active subscription id"
if ($activeSub -ne $SubscriptionId) {
    throw "Active subscription mismatch. Expected $SubscriptionId, got $activeSub"
}
Write-Host "Subscription is set correctly." -ForegroundColor Green

if (-not $SkipCreateOrUpdate) {
    Write-Step "Running billing-configuration create-or-update"

    $createArgs = @(
        "aldo-edge-operator", "billing-configuration", "create-or-update",
        "--resource-id", $ResourceId,
        "--resource-name", $ResourceName,
        "--stamp-id", $StampId,
        "--location", $Location,
        "--billing-model", $BillingModel,
        "--connection-intent", $ConnectionIntent,
        "--auto-renew", $AutoRenew,
        "--billing-status", $BillingStatus,
        "--current-cores", "$CurrentCores",
        "--current-pricing-model", $CurrentPricingModel,
        "--current-start-date", $CurrentStartDate,
        "--current-end-date", $CurrentEndDate,
        "--cloud", $Cloud,
        "--upcoming-cores", "$UpcomingCores",
        "--upcoming-pricing-model", $UpcomingPricingModel,
        "--upcoming-start-date", $UpcomingStartDate,
        "--azure-hybrid-windows-server-benefit", $AzureHybridWindowsServerBenefit,
        "--windows-server-vm-count", "$WindowsServerVmCount",
        "-o", "json"
    )

    if (-not [string]::IsNullOrWhiteSpace($UpcomingEndDate)) {
        $createArgs += @("--upcoming-end-date", $UpcomingEndDate)
    }

    $createResult = Invoke-AzJson -Args $createArgs -Description "create-or-update billing configuration"
    if ($createResult.name -ne "default") {
        throw "create-or-update returned unexpected resource name: $($createResult.name)"
    }
    Write-Host "create-or-update succeeded." -ForegroundColor Green
}
else {
    Write-Step "Skipping create-or-update by request"
}

Write-Step "Running billing-configuration show"
$showResult = Invoke-AzJson -Args @(
    "aldo-edge-operator", "billing-configuration", "show",
    "-o", "json"
) -Description "show billing configuration"
if ($showResult.name -ne "default") {
    throw "show returned unexpected name: $($showResult.name)"
}
Write-Host "show succeeded." -ForegroundColor Green

Write-Step "Running billing-configuration list"
$listResult = Invoke-AzJson -Args @(
    "aldo-edge-operator", "billing-configuration", "list",
    "-o", "json"
) -Description "list billing configurations"
if ($null -eq $listResult -or $listResult.Count -lt 1) {
    throw "list returned no billing configurations."
}
Write-Host "list succeeded. Found $($listResult.Count) item(s)." -ForegroundColor Green

Write-Step "Running snapshot list"
$snapshotList = Invoke-AzJson -Args @(
    "aldo-edge-operator", "billing-configuration", "snapshot", "list",
    "-o", "json"
) -Description "list billing configuration snapshots"
if ($null -eq $snapshotList) {
    $snapshotList = @()
}
Write-Host "snapshot list succeeded. Found $($snapshotList.Count) item(s)." -ForegroundColor Green

if ([string]::IsNullOrWhiteSpace($SnapshotName) -and $snapshotList.Count -gt 0) {
    $SnapshotName = $snapshotList[0].name
}

if (-not [string]::IsNullOrWhiteSpace($SnapshotName)) {
    Write-Step "Running snapshot show for '$SnapshotName'"
    $snapshotShow = Invoke-AzJson -Args @(
        "aldo-edge-operator", "billing-configuration", "snapshot", "show",
        "--snapshot-name", $SnapshotName,
        "-o", "json"
    ) -Description "show billing configuration snapshot"

    if ($snapshotShow.name -ne $SnapshotName) {
        throw "snapshot show returned unexpected name: $($snapshotShow.name)"
    }
    Write-Host "snapshot show succeeded." -ForegroundColor Green
}
else {
    Write-Host "No snapshot available and --SnapshotName not provided. Skipping snapshot show." -ForegroundColor Yellow
}

if ($RunNegativeValidation) {
    Write-Step "Running negative validation test (partial upcoming args should fail)"
    $null = Invoke-AzJson -Args @(
        "aldo-edge-operator", "billing-configuration", "create-or-update",
        "--resource-id", $ResourceId,
        "--resource-name", $ResourceName,
        "--stamp-id", $StampId,
        "--location", $Location,
        "--billing-model", $BillingModel,
        "--connection-intent", $ConnectionIntent,
        "--auto-renew", $AutoRenew,
        "--billing-status", $BillingStatus,
        "--current-cores", "$CurrentCores",
        "--current-pricing-model", $CurrentPricingModel,
        "--current-start-date", $CurrentStartDate,
        "--upcoming-cores", "$UpcomingCores",
        "-o", "json"
    ) -Description "negative validation for partial upcoming args" -ExpectFailure
}

Write-Step "All billing cmdlet tests completed successfully"
Write-Host "Tested commands:" -ForegroundColor Green
Write-Host "  - aldo-edge-operator billing-configuration create-or-update" -ForegroundColor Gray
Write-Host "  - aldo-edge-operator billing-configuration show" -ForegroundColor Gray
Write-Host "  - aldo-edge-operator billing-configuration list" -ForegroundColor Gray
Write-Host "  - aldo-edge-operator billing-configuration snapshot list" -ForegroundColor Gray
Write-Host "  - aldo-edge-operator billing-configuration snapshot show (if snapshot available)" -ForegroundColor Gray
