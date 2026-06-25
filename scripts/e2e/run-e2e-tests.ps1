<#
.SYNOPSIS
    JIT SSH Certificate - Comprehensive Automated E2E Test Suite
.DESCRIPTION
    Covers: Extension install, input validation, auth/PIM, KV errors,
    certificate generation (default + custom paths), and SSH login.
    Outputs timestamped CSV with all results.
.EXAMPLE
    .\run-e2e-tests.ps1
    .\run-e2e-tests.ps1 -WhlPath "C:\path\to\provisionedmachine-1.0.0b3-py3-none-any.whl"
#>
param(
    [string]$WhlPath = "",
    [string]$Tenant       = "2ffc1db7-b373-4be0-a5ec-f54edd5bf695",
    [string]$Subscription = "98f24b96-fffa-4142-bec5-8472d0f30749",
    # --- Positive test resources ---
    [string]$VaultName    = "remote-ssh-poc1",
    [string]$EdgeMachine  = "/subscriptions/98f24b96-fffa-4142-bec5-8472d0f30749/resourceGroups/ar-sff-rg/providers/Microsoft.AzureStackHCI/edgeMachines/aurosffeus16062026B",
    [string]$KvResourceId = "/subscriptions/98f24b96-fffa-4142-bec5-8472d0f30749/resourceGroups/pushkar-test-rg/providers/Microsoft.KeyVault/vaults/remote-ssh-poc1",
    # --- Negative test resources ---
    [string]$BadVault     = "remote-ssh-poc2",
    [string]$BadEdgeMachine = "/subscriptions/98f24b96-fffa-4142-bec5-8472d0f30749/resourceGroups/pushkar-test-rg/providers/Microsoft.KeyVault/vaults/remote-ssh-poc2",
    # --- Role & container ---
    [string]$RoleName     = "Provisioned Machine Admin",
    [string]$AcrName      = "jitsshtester",
    [string]$ImageName    = "jitsshtester.azurecr.io/jit-ssh-test:0.0.1",
    [string]$ContainerName = "ssh-jit-tester",
    [int]$SshPort         = 2222,
    # --- Skip phases ---
    # --- Test selection: comma-separated test IDs (e.g. "2.5,2.7,3.5") or empty for all ---
    [string]$RunTests = ""
)

$ErrorActionPreference = "Continue"
$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$resultsFile = "e2e-results-$ts.csv"
$results = @()
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Parse test filter — supports individual IDs ("2.5,3.3") or phase prefixes ("2,3")
$script:testFilter = @()
if ($RunTests) {
    $script:testFilter = $RunTests -split "," | ForEach-Object { $_.Trim() }
    Write-Host "Test filter active: running only [$($script:testFilter -join ', ')]" -ForegroundColor Yellow
}
function Should-RunTest([string]$Id) {
    if ($script:testFilter.Count -eq 0) { return $true }  # No filter = run all
    foreach ($f in $script:testFilter) {
        if ($Id -eq $f) { return $true }          # Exact match: "2.5"
        if ($Id.StartsWith("$f.")) { return $true } # Phase prefix: "2" matches "2.5"
    }
    return $false
}

# ── helpers ──────────────────────────────────────────────────
function Run-Test {
    param([string]$Id,[string]$Name,[string]$Desc,[string]$Cmd,[string]$Expected,[scriptblock]$Block)
    if (-not (Should-RunTest $Id)) {
        # Silently skip filtered-out tests
        return
    }
    Write-Host "`n=== [$Id] $Name ===" -ForegroundColor Cyan
    Write-Host "  $Desc" -ForegroundColor Gray
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        $actual = (& $Block 2>&1 | Out-String).Trim()
        $status = "PASS"
        Write-Host "  PASS: $($actual.Substring(0,[Math]::Min($actual.Length,100)))" -ForegroundColor Green
    } catch {
        $actual = $_.Exception.Message
        $status = "FAIL"
        Write-Host "  FAIL: $actual" -ForegroundColor Red
    }
    $sw.Stop()
    $script:results += [PSCustomObject]@{
        SNo=$Id; TestCase=$Name; Description=$Desc; Command=$Cmd; ExpectedResult=$Expected
        ActualResult=$actual.Substring(0,[Math]::Min($actual.Length,300)); Status=$status
        Duration="$($sw.Elapsed.TotalSeconds.ToString('F1'))s"
    }
}
function Skip-Test { param([string]$Id,[string]$Name,[string]$Reason)
    $script:results += [PSCustomObject]@{
        SNo=$Id; TestCase=$Name; Description=$Reason; Command=""; ExpectedResult=""
        ActualResult="SKIPPED - $Reason"; Status="SKIP"; Duration="0s"
    }
    Write-Host "  [$Id] $Name — SKIPPED ($Reason)" -ForegroundColor Yellow
}
function Prompt-Manual { param([string]$Msg)
    Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "║  MANUAL STEP: $Msg" -ForegroundColor Yellow
    Write-Host "║  Type 'skip' to skip PIM-dependent tests.  ║" -ForegroundColor Yellow
    Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Yellow
    $r = Read-Host "Press ENTER when done (or 'skip')"
    return ($r -ne "skip")
}

# ── Phase 0: Setup ───────────────────────────────────────────
Write-Host "`n================================================================" -ForegroundColor Yellow
Write-Host "  JIT SSH Certificate — E2E Test Suite  ($ts)" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Yellow

$cur = az account show --query tenantId -o tsv 2>$null
if ($cur -ne $Tenant) { az login --tenant $Tenant --only-show-errors 2>&1 | Out-Null }
az account set --subscription $Subscription 2>$null
$upn = az ad signed-in-user show --query userPrincipalName -o tsv 2>$null
# Handle guest UPN: alias_domain.com#EXT#@tenant.onmicrosoft.com -> alias
if ($upn -match "^([^_]+)_.*#EXT#") { $userAlias = $Matches[1] }
elseif ($upn -match "@") { $userAlias = $upn.Split("@")[0] }
else { $userAlias = $upn }
$userOid = az ad signed-in-user show --query id -o tsv 2>$null
Write-Host "User: $userAlias | OID: $userOid" -ForegroundColor Green

if (-not $WhlPath -or -not (Test-Path $WhlPath)) {
    $f = Get-ChildItem ".", "..", "C:\az-development\az-cli-provisioned-machine\azure-cli-extensions\src\provisionedmachine\dist" -Filter "provisionedmachine-*.whl" -EA SilentlyContinue | Select-Object -First 1
    if ($f) { $WhlPath = $f.FullName } else { Write-Host "ERROR: .whl not found" -ForegroundColor Red; exit 1 }
}
Write-Host "Wheel: $WhlPath`n" -ForegroundColor Green
$dummyRid = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/X/Y/Z"

# ═════════════════════════════════════════════════════════════
# CLEANUP: Cancel any pending PIM requests from previous runs
# ═════════════════════════════════════════════════════════════
Write-Host "─── Cancelling stale pending PIM requests ───" -ForegroundColor Magenta
$tokClean = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
$cleanScopes = @($EdgeMachine, $KvResourceId)
foreach ($cleanScope in $cleanScopes) {
    $pendingReqs = Invoke-RestMethod -Uri "https://management.azure.com${cleanScope}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tokClean"} -EA SilentlyContinue
    $stalePending = @($pendingReqs.value | Where-Object { $_.properties.status -eq "PendingApproval" -and $_.properties.principalId -eq $userOid })
    if ($stalePending.Count -gt 0) {
        foreach ($sp in $stalePending) {
            $cancelGuid = [guid]::NewGuid().ToString()
            $roleName = $sp.properties.expandedProperties.roleDefinition.displayName
            $linkedEid = $sp.properties.linkedRoleEligibilityScheduleId
            $rdId = $sp.properties.roleDefinitionId
            Write-Host "  Cancelling pending: $roleName on $cleanScope" -ForegroundColor Yellow
            $cancelBody = "{'properties':{'principalId':'${userOid}','roleDefinitionId':'${rdId}','requestType':'SelfDeactivate','justification':'E2E cleanup - cancel stale request'}}"
            az rest --method PUT --url "https://management.azure.com${cleanScope}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/${cancelGuid}?api-version=2020-10-01" --headers "Content-Type=application/json" --body $cancelBody 2>&1 | Out-Null
        }
        Write-Host "  Cancelled $($stalePending.Count) stale request(s) on $cleanScope" -ForegroundColor Green
    } else {
        Write-Host "  No pending requests on $cleanScope" -ForegroundColor Green
    }
}
Start-Sleep 5

# ═════════════════════════════════════════════════════════════
# 1. EXTENSION INSTALLATION & HELP
# ═════════════════════════════════════════════════════════════
# Always reinstall from wheel to ensure latest code is used
az extension remove --name provisionedmachine 2>$null
az extension add --source $WhlPath --yes 2>&1 | Out-Null

Write-Host "─── Phase 1: Extension Installation & Help ───" -ForegroundColor Magenta

Run-Test "1.1" "Install extension" "Install from .whl file" `
    "az extension add --source ...whl --yes" "Extension installs successfully" {
    az extension remove --name provisionedmachine 2>$null
    $o = az extension add --source $WhlPath --yes 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0 -and $o -notmatch "preview") { throw "Failed: $o" }
    "Installed successfully"
}

Run-Test "1.2" "Verify extension listed" "Confirm version 1.0.0b3 in list" `
    'az extension list -o table' "provisionedmachine 1.0.0b3" {
    $q = '[?name==''provisionedmachine''].{Name:name,Version:version}'
    $o = az extension list --query $q -o table 2>&1 | Out-String
    if ($o -notmatch "provisionedmachine") { throw "Not listed" }; $o.Trim()
}

Run-Test "1.3" "Help text - group" "No implementation details leaked" `
    "az provisionedmachine -h" "Manage provisioned machine resources" {
    $o = az provisionedmachine -h 2>&1 | Out-String
    if ($o -notmatch "(?i)provisionedmachine|ssh-cert-create") { throw "Bad help: $o" }
    if ($o -match "PIM|RBAC|RS512|Key Vault Sign") { throw "Leaks internals" }
    "Group help correct"
}

Run-Test "1.4" "Help text - command" "Shows all 4 params + examples" `
    "az provisionedmachine ssh-cert-create -h" "--vault-name, --resource-id, --cert-path, --private-key-path" {
    $o = az provisionedmachine ssh-cert-create -h 2>&1 | Out-String
    $m = @(); @("--vault-name","--resource-id","--cert-path","--private-key-path") | % { if ($o -notmatch [regex]::Escape($_)) { $m += $_ } }
    if ($m.Count) { throw "Missing: $($m -join ', ')" }; "All params present"
}

Run-Test "1.5" "Uninstall and reinstall" "Clean cycle" `
    "remove + add + help" "All succeed" {
    az extension remove --name provisionedmachine 2>$null
    az extension add --source $WhlPath --yes 2>&1 | Out-Null
    $o = az provisionedmachine ssh-cert-create -h 2>&1 | Out-String
    if ($o -notmatch "--vault-name") { throw "Broken after reinstall" }; "Cycle succeeded"
}

# ═════════════════════════════════════════════════════════════
# 2. INPUT VALIDATION
# ═════════════════════════════════════════════════════════════
Write-Host "`n─── Phase 2: Input Validation ───" -ForegroundColor Magenta

Run-Test "2.1" "Invalid resource ID - random string" "Reject non-ARM" `
    'ssh-cert-create --resource-id "invalid-string"' "not a valid ARM resource ID" {
    $o = az provisionedmachine ssh-cert-create --vault-name test --resource-id "invalid-string" 2>&1 | Out-String
    if ($o -notmatch "not a valid ARM resource ID") { throw "Wrong: $o" }; "Rejected"
}

Run-Test "2.2" "Invalid resource ID - missing /subscriptions" "Reject incomplete ARM" `
    'ssh-cert-create --resource-id "/resourceGroups/..."' "not a valid ARM resource ID" {
    $o = az provisionedmachine ssh-cert-create --vault-name test --resource-id "/resourceGroups/rg/providers/X/Y/Z" 2>&1 | Out-String
    if ($o -notmatch "not a valid ARM resource ID") { throw "Wrong: $o" }; "Rejected"
}

Run-Test "2.3" "Invalid resource ID - empty" "Reject empty string" `
    'ssh-cert-create --resource-id ""' "Error about empty/required" {
    $o = az provisionedmachine ssh-cert-create --vault-name test --resource-id "" 2>&1 | Out-String
    if ($o -notmatch "not a valid ARM resource ID|expected one argument|required") { throw "Wrong: $o" }; "Rejected"
}

Run-Test "2.4" "Invalid resource ID - deleted/non-existent machine" "Resource doesn't exist" `
    'ssh-cert-create --resource-id ".../edgeMachines/deletedMachine123"' "Resource not found or PIM error" {
    $fakeRid = "/subscriptions/$Subscription/resourceGroups/ar-sff-rg/providers/Microsoft.AzureStackHCI/edgeMachines/deletedMachine12345"
    $o = az provisionedmachine ssh-cert-create --vault-name $VaultName --resource-id $fakeRid 2>&1 | Out-String
    if ($o -match "certificatePath") { throw "Should not succeed for deleted machine" }
    if ($o -notmatch "not found|No active|expired|deactivated|404|401|InvalidAuthentication") { throw "Unexpected: $o" }; "Rejected non-existent machine"
}

# 2.5-2.7: Role-based tests — for each role: deactivate ALL other roles, assign, activate, verify cert
# Helper: Deactivate all PM roles and wait (handles "not allowed before 5 min" by waiting)
function Deactivate-AllPmRoles {
    $allPmRoles = @("Provisioned Machine Admin", "Provisioned Machine Reader", "Provisioned Machine Contributor")
    
    # Remove any direct RBAC PM role assignments (cleanup from prior runs)
    $allAssignments = az role assignment list --assignee $userOid --scope $EdgeMachine --include-inherited --query "[?contains(roleDefinitionName, 'Provisioned Machine')]" -o json 2>$null | ConvertFrom-Json
    if ($allAssignments -and $allAssignments.Count -gt 0) {
        foreach ($a in $allAssignments) {
            Write-Host "    Removing direct assignment: $($a.roleDefinitionName) (scope: $($a.scope))" -ForegroundColor Gray
            az role assignment delete --ids $a.id 2>&1 | Out-Null
        }
    }

    # Send PIM SelfDeactivate for all PM roles on edge machine + parent scopes
    $emParts = $EdgeMachine -split "/"
    $subScope = "/subscriptions/$($emParts[2])"
    $rgScope = "/subscriptions/$($emParts[2])/resourceGroups/$($emParts[4])"
    $allScopes = @($EdgeMachine, $rgScope, $subScope)
    foreach ($scope in $allScopes) {
        foreach ($rn in $allPmRoles) {
            $rd = az role definition list --name $rn --query "[0].id" -o tsv 2>$null
            if ($rd) {
                $dg = [guid]::NewGuid().ToString()
                az rest --method PUT --url "https://management.azure.com${scope}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/${dg}?api-version=2020-10-01" --headers "Content-Type=application/json" --body "{'properties':{'principalId':'${userOid}','roleDefinitionId':'${rd}','requestType':'SelfDeactivate','justification':'E2E role isolation'}}" 2>&1 | Out-Null
            }
        }
    }

    # Poll: confirm no PM roles visible via schedule instances + RBAC (max 60s)
    Write-Host "    Polling for PM role removal (every 10s, max 60s)..." -ForegroundColor Gray
    $maxWait = 60; $elapsed = 0
    while ($elapsed -lt $maxWait) {
        Start-Sleep 10; $elapsed += 10
        # Check RBAC direct assignments
        $rbacAssignments = az role assignment list --assignee $userOid --scope $EdgeMachine --include-inherited --query "[?contains(roleDefinitionName, 'Provisioned Machine')]" -o json 2>$null | ConvertFrom-Json
        $rbacCount = if ($rbacAssignments) { $rbacAssignments.Count } else { 0 }
        # Check PIM schedule instances
        $tokChk = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
        $pimActive = Invoke-RestMethod -Uri "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleAssignmentScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tokChk"} -EA SilentlyContinue
        $pimPmRoles = $pimActive.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -match "Provisioned Machine" }
        $pimCount = if ($pimPmRoles) { @($pimPmRoles).Count } else { 0 }
        if ($rbacCount -eq 0 -and $pimCount -eq 0) {
            Write-Host "    All PM roles removed after ${elapsed}s" -ForegroundColor Green
            return
        }
        $activeNames = @()
        if ($rbacAssignments) { $activeNames += $rbacAssignments | ForEach-Object { $_.roleDefinitionName } }
        if ($pimPmRoles) { $activeNames += $pimPmRoles | ForEach-Object { $_.properties.expandedProperties.roleDefinition.displayName } }
        Write-Host "    Still active: $(($activeNames | Select-Object -Unique) -join ', ') (${elapsed}s)" -ForegroundColor Gray
    }
    Write-Host "    WARNING: PM roles still visible after ${maxWait}s" -ForegroundColor Yellow
}

# Helper: Activate a specific role via PIM SelfActivate (polls for approval up to 5 min)
function Activate-SingleRole {
    param([string]$RoleName2, [string]$RoleDef2)
    
    $tokEm = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
    
    # Find PIM eligibility for this role on the edge machine
    $emElig = Invoke-RestMethod -Uri "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleEligibilityScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tokEm"} -EA SilentlyContinue
    $emEid = ($emElig.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq $RoleName2 -and $_.properties.memberType -eq "Direct" }).name
    
    if (-not $emEid) {
        # Check parent scopes (RG, subscription) for inherited eligibility
        $emParts = $EdgeMachine -split "/"
        $rgScope = "/subscriptions/$($emParts[2])/resourceGroups/$($emParts[4])"
        $subScope = "/subscriptions/$($emParts[2])"
        foreach ($scope in @($rgScope, $subScope)) {
            $parentElig = Invoke-RestMethod -Uri "https://management.azure.com${scope}/providers/Microsoft.Authorization/roleEligibilityScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tokEm"} -EA SilentlyContinue
            $emEid = ($parentElig.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq $RoleName2 }).name
            if ($emEid) { break }
        }
    }
    
    if (-not $emEid) { throw "No PIM eligibility found for $RoleName2 on $EdgeMachine (or parent scopes)" }
    
    # Attempt PIM SelfActivate — single request only
    $ag = [guid]::NewGuid().ToString()
    $ab = "{'properties':{'principalId':'${userOid}','roleDefinitionId':'${RoleDef2}','requestType':'SelfActivate','linkedRoleEligibilityScheduleId':'${emEid}','justification':'E2E test - $RoleName2','scheduleInfo':{'expiration':{'type':'AfterDuration','duration':'PT30M'}}}}"
    $ar = az rest --method PUT --url "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/${ag}?api-version=2020-10-01" --headers "Content-Type=application/json" --body $ab 2>&1 | Out-String
    
    if ($ar -match '"status"\s*:\s*"Provisioned"') {
        Write-Host "    PIM activated: $RoleName2" -ForegroundColor Green
        Write-Host "    Waiting 30s for ARM propagation..." -ForegroundColor Gray
        Start-Sleep 30
        return
    }
    if ($ar -match "RoleAssignmentExists") {
        Write-Host "    PIM already active: $RoleName2" -ForegroundColor Green
        return
    }
    if ($ar -match "PendingApproval|PendingRoleAssignmentRequest") {
        # Check if role is already active via schedule instances
        $tokEm2 = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
        $emActive = Invoke-RestMethod -Uri "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleAssignmentScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tokEm2"} -EA SilentlyContinue
        $emFound = $emActive.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq $RoleName2 }
        if ($emFound) {
            Write-Host "    PIM already active: $RoleName2 (confirmed via schedule instances)" -ForegroundColor Green
            return
        }
        
        Write-Host "    PIM for $RoleName2 : PENDING APPROVAL" -ForegroundColor Yellow
        Write-Host "    >>> Please APPROVE '$RoleName2' on $EdgeMachine <<<" -ForegroundColor Yellow
        Write-Host "    Polling for 10 minutes..." -ForegroundColor Yellow
        $maxWait = 600; $elapsed = 0
        while ($elapsed -lt $maxWait) {
            Start-Sleep 10; $elapsed += 10
            # Monitor only — check schedule instances
            $tokEm3 = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
            $emActive3 = Invoke-RestMethod -Uri "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleAssignmentScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tokEm3"} -EA SilentlyContinue
            $emFound3 = $emActive3.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq $RoleName2 }
            if ($emFound3) {
                Write-Host "    PIM $RoleName2 active after ${elapsed}s" -ForegroundColor Green
                Write-Host "    Waiting 30s for ARM propagation..." -ForegroundColor Gray
                Start-Sleep 30
                return
            }
            if ($elapsed % 60 -eq 0) { Write-Host "    Waiting for $RoleName2 approval... (${elapsed}s / 600s)" -ForegroundColor Gray }
        }
        throw "PIM approval for $RoleName2 timed out after 10min. Please approve and re-run."
    }
    throw "PIM SelfActivate failed for $RoleName2 : $ar"
}

# Helper: Activate PM role + KV Crypto User PIM in parallel, poll both for 10 min
function Activate-PmAndKv-Parallel {
    param([string]$RoleName2, [string]$RoleDef2)
    
    # KV Crypto User is pre-activated for PT3H before role tests start.
    # This function only activates the PM role now.
    
    $tokInit = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
    
    # --- Find PM eligibility (retry up to 3 times for ARM propagation after deactivation) ---
    $emEid = $null
    for ($eligRetry = 1; $eligRetry -le 3; $eligRetry++) {
        $tokInit = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
        $emElig = Invoke-RestMethod -Uri "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleEligibilityScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tokInit"} -EA SilentlyContinue
        $emEid = ($emElig.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq $RoleName2 -and $_.properties.memberType -eq "Direct" }).name
        if (-not $emEid) {
            $emParts = $EdgeMachine -split "/"
            foreach ($scope in @("/subscriptions/$($emParts[2])/resourceGroups/$($emParts[4])", "/subscriptions/$($emParts[2])")) {
                $parentElig = Invoke-RestMethod -Uri "https://management.azure.com${scope}/providers/Microsoft.Authorization/roleEligibilityScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tokInit"} -EA SilentlyContinue
                $emEid = ($parentElig.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq $RoleName2 }).name
                if ($emEid) { break }
            }
        }
        if ($emEid) { break }
        if ($eligRetry -lt 3) {
            Write-Host "    Eligibility for $RoleName2 not found (attempt $eligRetry/3), retrying in 10s..." -ForegroundColor Gray
            Start-Sleep 10
        }
    }
    if (-not $emEid) { throw "No PIM eligibility found for $RoleName2 on $EdgeMachine (or parent scopes)" }
    
    # --- Activate PM role — single request only ---
    $pmGuid = [guid]::NewGuid().ToString()
    $pmBody = "{'properties':{'principalId':'${userOid}','roleDefinitionId':'${RoleDef2}','requestType':'SelfActivate','linkedRoleEligibilityScheduleId':'${emEid}','justification':'E2E test - $RoleName2','scheduleInfo':{'expiration':{'type':'AfterDuration','duration':'PT30M'}}}}"
    $pmResult = az rest --method PUT --url "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/${pmGuid}?api-version=2020-10-01" --headers "Content-Type=application/json" --body $pmBody 2>&1 | Out-String
    
    if ($pmResult -match '"status"\s*:\s*"Provisioned"|RoleAssignmentExists') {
        Write-Host "    PIM activated: $RoleName2" -ForegroundColor Green
        Write-Host "    Waiting 30s for ARM propagation..." -ForegroundColor Gray
        Start-Sleep 30
        return
    }
    
    # --- Pending approval: poll for PM role only ---
    Write-Host "    PIM PENDING APPROVAL: $RoleName2" -ForegroundColor Yellow
    Write-Host "    >>> Please APPROVE '$RoleName2' on $EdgeMachine <<<" -ForegroundColor Yellow
    Write-Host "    Polling for 10 minutes (every 10s)..." -ForegroundColor Yellow
    
    $maxWait = 600; $elapsed = 0
    while ($elapsed -lt $maxWait) {
        Start-Sleep 10; $elapsed += 10
        $tok = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
        
        $emActive = Invoke-RestMethod -Uri "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleAssignmentScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tok"} -EA SilentlyContinue
        $emFound = $emActive.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq $RoleName2 }
        if ($emFound) {
            Write-Host "    PIM $RoleName2 active after ${elapsed}s" -ForegroundColor Green
            Write-Host "    Waiting 30s for ARM propagation..." -ForegroundColor Gray
            Start-Sleep 30
            return
        }
        
        if ($elapsed % 60 -eq 0) {
            Write-Host "    Waiting: $RoleName2 (${elapsed}s / 600s)" -ForegroundColor Gray
        }
    }
    
    throw "PIM approval timed out after 10min for: $RoleName2. Please approve and re-run."
}

# Helper: Ensure KV Crypto User PIM is active (needed for cert signing)
function Ensure-KvPim {
    $kvRole = "Key Vault Crypto User"
    $kvRd = "/subscriptions/$Subscription/providers/Microsoft.Authorization/roleDefinitions/12338af0-0e69-4776-bea7-57ae8d297424"
    $tokKv = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
    
    # Always attempt activation (don't just trust schedule instances — they can be stale)
    # Check eligibility
    $kvElig = Invoke-RestMethod -Uri "https://management.azure.com${KvResourceId}/providers/Microsoft.Authorization/roleEligibilityScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tokKv"} -EA SilentlyContinue
    $kvEid = ($kvElig.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq $kvRole -and $_.properties.memberType -eq "Direct" }).name
    
    if (-not $kvEid) {
        Write-Host "    KV Crypto User: No PIM eligibility found. Creating..." -ForegroundColor Yellow
        $eg = [guid]::NewGuid().ToString()
        $eb = "{'properties':{'principalId':'${userOid}','roleDefinitionId':'${kvRd}','requestType':'AdminAssign','scheduleInfo':{'expiration':{'type':'AfterDuration','duration':'P365D'}}}}"
        az rest --method PUT --url "https://management.azure.com${KvResourceId}/providers/Microsoft.Authorization/roleEligibilityScheduleRequests/${eg}?api-version=2020-10-01" --headers "Content-Type=application/json" --body $eb 2>&1 | Out-Null
        Start-Sleep 8
        $tokKv = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
        $kvElig = Invoke-RestMethod -Uri "https://management.azure.com${KvResourceId}/providers/Microsoft.Authorization/roleEligibilityScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tokKv"}
        $kvEid = ($kvElig.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq $kvRole -and $_.properties.memberType -eq "Direct" }).name
    }
    if (-not $kvEid) { throw "Cannot get KV Crypto User eligibility" }
    
    # Attempt activation (PT1H) — RoleAssignmentExists means it's already active
    $ag = [guid]::NewGuid().ToString()
    $ab = "{'properties':{'principalId':'${userOid}','roleDefinitionId':'${kvRd}','requestType':'SelfActivate','linkedRoleEligibilityScheduleId':'${kvEid}','justification':'E2E cert test','scheduleInfo':{'expiration':{'type':'AfterDuration','duration':'PT1H'}}}}"
    $ar = az rest --method PUT --url "https://management.azure.com${KvResourceId}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/${ag}?api-version=2020-10-01" --headers "Content-Type=application/json" --body $ab 2>&1 | Out-String
    
    if ($ar -match '"status"\s*:\s*"Provisioned"') {
        Write-Host "    KV Crypto User PIM: ACTIVATED (PT1H)" -ForegroundColor Green
        return
    }
    if ($ar -match "RoleAssignmentExists") {
        Write-Host "    KV Crypto User PIM: already active (confirmed via activation attempt)" -ForegroundColor Green
        return
    }
    if ($ar -match "PendingApproval|PendingRoleAssignmentRequest") {
        # Check if KV is already active despite the pending request
        $tokKv2 = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
        $kvActive = Invoke-RestMethod -Uri "https://management.azure.com${KvResourceId}/providers/Microsoft.Authorization/roleAssignmentScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tokKv2"} -EA SilentlyContinue
        $kvFound = $kvActive.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq $kvRole }
        if ($kvFound) {
            Write-Host "    KV Crypto User PIM: already active (confirmed via schedule instances)" -ForegroundColor Green
            return
        }

        Write-Host "    KV Crypto User PIM: PENDING APPROVAL" -ForegroundColor Yellow
        Write-Host "    >>> Please APPROVE 'Key Vault Crypto User' on $KvResourceId <<<" -ForegroundColor Yellow
        Write-Host "    Polling for 5 minutes..." -ForegroundColor Yellow
        $maxWait = 300; $elapsed = 0
        while ($elapsed -lt $maxWait) {
            Start-Sleep 10; $elapsed += 10
            # Monitor only — check schedule instances
            $tokKv3 = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
            $kvActive3 = Invoke-RestMethod -Uri "https://management.azure.com${KvResourceId}/providers/Microsoft.Authorization/roleAssignmentScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tokKv3"} -EA SilentlyContinue
            $kvFound3 = $kvActive3.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq $kvRole }
            if ($kvFound3) {
                Write-Host "    KV Crypto User active after ${elapsed}s" -ForegroundColor Green
                return
            }
            if ($elapsed % 60 -eq 0) { Write-Host "    Waiting for KV approval... (${elapsed}s / 300s)" -ForegroundColor Gray }
        }
        throw "KV Crypto User PIM approval timed out after 5min. Please approve and re-run."
    }
    Write-Host "    KV Crypto User PIM activation: $ar" -ForegroundColor Yellow
}

# ═════════════════════════════════════════════════════════════
# TEST 3.5 (MOVED FIRST): No KV Crypto User PIM = cert fails
# Must run BEFORE KV pre-activation so KV is deactivated.
# ═════════════════════════════════════════════════════════════
Run-Test "3.5" "No KV Crypto User PIM = cert fails" "Deactivate KV Crypto User, verify cert fails with KV access denied" `
    "Deactivate KV PIM, then ssh-cert-create" "Correctly failed - KV access denied without Crypto User PIM" {
    # First, activate Edge Machine Admin so PIM check passes (isolate the KV failure)
    $adminDef35 = az role definition list --name "Provisioned Machine Admin" --query "[0].id" -o tsv 2>$null
    Activate-SingleRole -RoleName2 "Provisioned Machine Admin" -RoleDef2 $adminDef35
    Start-Sleep 5
    
    # Deactivate KV Crypto User PIM (may already be inactive)
    $kvRd35 = "/subscriptions/$Subscription/providers/Microsoft.Authorization/roleDefinitions/12338af0-0e69-4776-bea7-57ae8d297424"
    $dg35 = [guid]::NewGuid().ToString()
    $kvDeact = az rest --method PUT --url "https://management.azure.com${KvResourceId}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/${dg35}?api-version=2020-10-01" --headers "Content-Type=application/json" --body "{'properties':{'principalId':'${userOid}','roleDefinitionId':'${kvRd35}','requestType':'SelfDeactivate','justification':'E2E test - verify KV PIM required'}}" 2>&1 | Out-String
    
    if ($kvDeact -match "minimum.*duration|not allowed before|ActiveDurationTooShort") {
        Write-Host "    KV Crypto User: min duration not met, waiting 5 min..." -ForegroundColor Yellow
        Start-Sleep 300
        $dg35b = [guid]::NewGuid().ToString()
        az rest --method PUT --url "https://management.azure.com${KvResourceId}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/${dg35b}?api-version=2020-10-01" --headers "Content-Type=application/json" --body "{'properties':{'principalId':'${userOid}','roleDefinitionId':'${kvRd35}','requestType':'SelfDeactivate','justification':'E2E - KV deactivation retry'}}" 2>&1 | Out-Null
    }
    
    # Wait for KV deactivation propagation
    Write-Host "    Waiting 15s for KV Crypto User deactivation..." -ForegroundColor Gray
    Start-Sleep 15
    
    # Attempt cert-create - should fail with KV access denied (Sign permission missing)
    $o = az provisionedmachine ssh-cert-create --vault-name $VaultName --resource-id $EdgeMachine 2>&1 | Out-String
    if ($o -match "certificatePath") {
        throw "BUG: Cert generated without KV Crypto User PIM! KV should deny signing."
    }
    if ($o -notmatch "Access denied|Forbidden|401|Key Sign|vault|Unauthorized|denied") {
        throw "Unexpected error (expected KV access denied): $o"
    }
    Write-Host "    Correctly failed: no KV Crypto User PIM = no signing permission" -ForegroundColor Green
    "Correctly failed - KV access denied without Crypto User PIM"
}

# ── Pre-activate KV Crypto User for PT3H (after 3.5 confirmed KV denial) ──
# This avoids KV data-plane RBAC propagation issues caused by rapid deactivation/reactivation.
# KV stays active for remainder of tests since 3.5 already ran.
if (Should-RunTest "2.5" -or (Should-RunTest "2.6") -or (Should-RunTest "2.7") -or (Should-RunTest "2.7a") -or (Should-RunTest "2.7b") -or (Should-RunTest "5")) {
    Write-Host "`n── Pre-activating KV Crypto User (PT3H) for role tests ──" -ForegroundColor Cyan
    $kvRole = "Key Vault Crypto User"
    $kvRd = "/subscriptions/$Subscription/providers/Microsoft.Authorization/roleDefinitions/12338af0-0e69-4776-bea7-57ae8d297424"
    $tokKvPre = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
    
    # Check if already active
    $kvActiveChk = Invoke-RestMethod -Uri "https://management.azure.com${KvResourceId}/providers/Microsoft.Authorization/roleAssignmentScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tokKvPre"} -EA SilentlyContinue
    $kvAlready = $kvActiveChk.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq $kvRole }
    
    if ($kvAlready) {
        Write-Host "  KV Crypto User already active — skipping activation" -ForegroundColor Green
    } else {
        # Find eligibility
        $kvEligPre = Invoke-RestMethod -Uri "https://management.azure.com${KvResourceId}/providers/Microsoft.Authorization/roleEligibilityScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tokKvPre"} -EA SilentlyContinue
        $kvEidPre = ($kvEligPre.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq $kvRole -and $_.properties.memberType -eq "Direct" }).name
        if (-not $kvEidPre) { throw "No PIM eligibility for KV Crypto User on $KvResourceId" }
        
        $kvGuidPre = [guid]::NewGuid().ToString()
        $kvBodyPre = "{'properties':{'principalId':'${userOid}','roleDefinitionId':'${kvRd}','requestType':'SelfActivate','linkedRoleEligibilityScheduleId':'${kvEidPre}','justification':'E2E role tests - KV pre-activation','scheduleInfo':{'expiration':{'type':'AfterDuration','duration':'PT3H'}}}}"
        $kvResPre = az rest --method PUT --url "https://management.azure.com${KvResourceId}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/${kvGuidPre}?api-version=2020-10-01" --headers "Content-Type=application/json" --body $kvBodyPre 2>&1 | Out-String
        
        if ($kvResPre -match '"status"\s*:\s*"Provisioned"|RoleAssignmentExists') {
            Write-Host "  KV Crypto User PIM: ACTIVATED (PT3H)" -ForegroundColor Green
        } elseif ($kvResPre -match "PendingApproval|PendingRoleAssignmentRequest") {
            Write-Host "  >>> Please APPROVE 'Key Vault Crypto User' on $KvResourceId <<<" -ForegroundColor Yellow
            Write-Host "  Polling for 10 minutes..." -ForegroundColor Yellow
            $kvMaxPre = 600; $kvElPre = 0
            while ($kvElPre -lt $kvMaxPre) {
                Start-Sleep 10; $kvElPre += 10
                $tokKvPre2 = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
                $kvAct2 = Invoke-RestMethod -Uri "https://management.azure.com${KvResourceId}/providers/Microsoft.Authorization/roleAssignmentScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tokKvPre2"} -EA SilentlyContinue
                $kvF2 = $kvAct2.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq $kvRole }
                if ($kvF2) {
                    Write-Host "  KV Crypto User active after ${kvElPre}s" -ForegroundColor Green
                    break
                }
                if ($kvElPre % 60 -eq 0) { Write-Host "  Waiting for KV approval... (${kvElPre}s / 600s)" -ForegroundColor Gray }
            }
            if (-not $kvF2) { throw "KV Crypto User PIM approval timed out. Please approve and re-run." }
        } else {
            Write-Host "  KV activation response: $kvResPre" -ForegroundColor Yellow
        }
        # Wait for KV data-plane propagation
        Write-Host "  Waiting 60s for KV data-plane RBAC propagation..." -ForegroundColor Gray
        Start-Sleep 60
    }
}

Run-Test "2.5" "Reader role on Provisioned Machine" "Deactivate all, assign Reader, verify cert" `
    "Isolate Reader role, ssh-cert-create" "Certificate generated with role=Provisioned Machine Reader" {
    $readerDef = az role definition list --name "Provisioned Machine Reader" --query "[0].id" -o tsv 2>$null
    if (-not $readerDef) { throw "Provisioned Machine Reader role not found" }
    
    # Deactivate all PM roles, then activate Reader + KV in parallel
    Deactivate-AllPmRoles
    Activate-PmAndKv-Parallel -RoleName2 "Provisioned Machine Reader" -RoleDef2 $readerDef
    
    # Generate cert
    $o = az provisionedmachine ssh-cert-create --vault-name $VaultName --resource-id $EdgeMachine 2>&1 | Out-String
    if ($o -notmatch "certificatePath") { throw "Cert gen failed: $o" }
    
    # Verify cert has Reader role (not Admin or Contributor)
    $m = [regex]::Match($o, '\{[^}]+\}')
    if ($m.Success) {
        $j = $m.Value | ConvertFrom-Json
        $certOut = ssh-keygen -L -f $j.certificatePath 2>&1 | Out-String
        if ($certOut -match "role=Provisioned Machine Admin") { throw "Admin role still active! Priority conflict. Got: $certOut" }
        if ($certOut -match "role=Provisioned Machine Contributor") { throw "Contributor role still active! Priority conflict. Got: $certOut" }
        if ($certOut -notmatch "role=Provisioned Machine Reader") { throw "Cert does not have Reader role. Got: $certOut" }
        Remove-Item -Recurse -Force (Split-Path $j.privateKeyPath) -EA SilentlyContinue
    }
    
    "Certificate generated with role=Provisioned Machine Reader"
}

Run-Test "2.6" "Contributor role on Provisioned Machine" "Deactivate all, assign Contributor, verify cert" `
    "Isolate Contributor role, ssh-cert-create" "Certificate generated with role=Provisioned Machine Contributor" {
    $contribDef = az role definition list --name "Provisioned Machine Contributor" --query "[0].id" -o tsv 2>$null
    if (-not $contribDef) { throw "Provisioned Machine Contributor role not found" }
    
    # Deactivate all PM roles, then activate Contributor + KV in parallel
    Deactivate-AllPmRoles
    Activate-PmAndKv-Parallel -RoleName2 "Provisioned Machine Contributor" -RoleDef2 $contribDef
    
    # Generate cert
    $o = az provisionedmachine ssh-cert-create --vault-name $VaultName --resource-id $EdgeMachine 2>&1 | Out-String
    if ($o -notmatch "certificatePath") { throw "Cert gen failed: $o" }
    
    $m = [regex]::Match($o, '\{[^}]+\}')
    if ($m.Success) {
        $j = $m.Value | ConvertFrom-Json
        $certOut = ssh-keygen -L -f $j.certificatePath 2>&1 | Out-String
        if ($certOut -match "role=Provisioned Machine Admin") { throw "Admin role still active! Priority conflict. Got: $certOut" }
        if ($certOut -notmatch "role=Provisioned Machine Contributor") { throw "Cert does not have Contributor role. Got: $certOut" }
        Remove-Item -Recurse -Force (Split-Path $j.privateKeyPath) -EA SilentlyContinue
    }
    "Certificate generated with role=Provisioned Machine Contributor"
}

Run-Test "2.7" "Admin role on Provisioned Machine" "Deactivate all, assign Admin, verify cert" `
    "Isolate Admin role, ssh-cert-create" "Certificate generated with role=Provisioned Machine Admin" {
    $adminDef = az role definition list --name "Provisioned Machine Admin" --query "[0].id" -o tsv 2>$null
    if (-not $adminDef) { throw "Provisioned Machine Admin role not found" }
    
    # Deactivate all PM roles, then activate Admin + KV in parallel
    Deactivate-AllPmRoles
    Activate-PmAndKv-Parallel -RoleName2 "Provisioned Machine Admin" -RoleDef2 $adminDef
    
    # Generate cert
    $o = az provisionedmachine ssh-cert-create --vault-name $VaultName --resource-id $EdgeMachine 2>&1 | Out-String
    if ($o -notmatch "certificatePath") { throw "Cert gen failed: $o" }
    
    $m = [regex]::Match($o, '\{[^}]+\}')
    if ($m.Success) {
        $j = $m.Value | ConvertFrom-Json
        $certOut = ssh-keygen -L -f $j.certificatePath 2>&1 | Out-String
        if ($certOut -notmatch "role=Provisioned Machine Admin") { throw "Cert does not have Admin role. Got: $certOut" }
        Remove-Item -Recurse -Force (Split-Path $j.privateKeyPath) -EA SilentlyContinue
    }
    "Certificate generated with role=Provisioned Machine Admin"
}

# --- Role Priority Tests: multiple roles active simultaneously ---

Run-Test "2.7a" "Priority: Admin wins over Reader+Contributor" "Activate Admin+Reader+KV, verify Admin in cert" `
    "Admin > Contributor > Reader priority" "Certificate generated with role=Provisioned Machine Admin" {
    $adminDef = az role definition list --name "Provisioned Machine Admin" --query "[0].id" -o tsv 2>$null
    $readerDef = az role definition list --name "Provisioned Machine Reader" --query "[0].id" -o tsv 2>$null
    
    # Activate Admin (Reader may still be active from prior test — that's fine)
    Deactivate-AllPmRoles
    Activate-PmAndKv-Parallel -RoleName2 "Provisioned Machine Admin" -RoleDef2 $adminDef
    # Also activate Reader to create multi-role scenario
    Write-Host "    Activating secondary role: Provisioned Machine Reader" -ForegroundColor Gray
    $tokPri = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
    $emElig = Invoke-RestMethod -Uri "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleEligibilityScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tokPri"} -EA SilentlyContinue
    $readerEid = ($emElig.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq "Provisioned Machine Reader" -and $_.properties.memberType -eq "Direct" }).name
    if ($readerEid) {
        $rGuid = [guid]::NewGuid().ToString()
        $rBody = "{'properties':{'principalId':'${userOid}','roleDefinitionId':'${readerDef}','requestType':'SelfActivate','linkedRoleEligibilityScheduleId':'${readerEid}','justification':'E2E priority test','scheduleInfo':{'expiration':{'type':'AfterDuration','duration':'PT30M'}}}}"
        $rResult = az rest --method PUT --url "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/${rGuid}?api-version=2020-10-01" --headers "Content-Type=application/json" --body $rBody 2>&1 | Out-String
        if ($rResult -match '"status"\s*:\s*"Provisioned"|RoleAssignmentExists') {
            Write-Host "    Reader PIM activated" -ForegroundColor Green
        } elseif ($rResult -match "PendingApproval") {
            Write-Host "    >>> Please APPROVE 'Provisioned Machine Reader' on $EdgeMachine <<<" -ForegroundColor Yellow
            $rMax = 600; $rEl = 0
            while ($rEl -lt $rMax) {
                Start-Sleep 10; $rEl += 10
                $tokR = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
                $rAct = Invoke-RestMethod -Uri "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleAssignmentScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tokR"} -EA SilentlyContinue
                $rFound = $rAct.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq "Provisioned Machine Reader" }
                if ($rFound) { Write-Host "    Reader active after ${rEl}s" -ForegroundColor Green; break }
                if ($rEl % 60 -eq 0) { Write-Host "    Waiting: Reader (${rEl}s / 600s)" -ForegroundColor Gray }
            }
        }
        Write-Host "    Waiting 30s for ARM propagation..." -ForegroundColor Gray
        Start-Sleep 30
    }
    
    # Generate cert — should pick Admin (highest priority)
    $o = az provisionedmachine ssh-cert-create --vault-name $VaultName --resource-id $EdgeMachine 2>&1 | Out-String
    if ($o -notmatch "certificatePath") { throw "Cert gen failed: $o" }
    
    $m = [regex]::Match($o, '\{[^}]+\}')
    if ($m.Success) {
        $j = $m.Value | ConvertFrom-Json
        $certOut = ssh-keygen -L -f $j.certificatePath 2>&1 | Out-String
        if ($certOut -notmatch "role=Provisioned Machine Admin") { throw "Expected Admin priority but got: $certOut" }
        Remove-Item -Recurse -Force (Split-Path $j.privateKeyPath) -EA SilentlyContinue
    }
    "Certificate generated with role=Provisioned Machine Admin"
}

Run-Test "2.7b" "Priority: Contributor wins over Reader" "Activate Contributor+Reader+KV, verify Contributor in cert" `
    "Contributor > Reader priority" "Certificate generated with role=Provisioned Machine Contributor" {
    $contribDef = az role definition list --name "Provisioned Machine Contributor" --query "[0].id" -o tsv 2>$null
    $readerDef = az role definition list --name "Provisioned Machine Reader" --query "[0].id" -o tsv 2>$null
    
    # Deactivate all, then activate Contributor
    Deactivate-AllPmRoles
    Activate-PmAndKv-Parallel -RoleName2 "Provisioned Machine Contributor" -RoleDef2 $contribDef
    # Also activate Reader
    Write-Host "    Activating secondary role: Provisioned Machine Reader" -ForegroundColor Gray
    $tokPri = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
    $emElig = Invoke-RestMethod -Uri "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleEligibilityScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tokPri"} -EA SilentlyContinue
    $readerEid = ($emElig.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq "Provisioned Machine Reader" -and $_.properties.memberType -eq "Direct" }).name
    if ($readerEid) {
        $rGuid = [guid]::NewGuid().ToString()
        $rBody = "{'properties':{'principalId':'${userOid}','roleDefinitionId':'${readerDef}','requestType':'SelfActivate','linkedRoleEligibilityScheduleId':'${readerEid}','justification':'E2E priority test','scheduleInfo':{'expiration':{'type':'AfterDuration','duration':'PT30M'}}}}"
        $rResult = az rest --method PUT --url "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/${rGuid}?api-version=2020-10-01" --headers "Content-Type=application/json" --body $rBody 2>&1 | Out-String
        if ($rResult -match '"status"\s*:\s*"Provisioned"|RoleAssignmentExists') {
            Write-Host "    Reader PIM activated" -ForegroundColor Green
        } elseif ($rResult -match "PendingApproval") {
            Write-Host "    >>> Please APPROVE 'Provisioned Machine Reader' on $EdgeMachine <<<" -ForegroundColor Yellow
            $rMax = 600; $rEl = 0
            while ($rEl -lt $rMax) {
                Start-Sleep 10; $rEl += 10
                $tokR = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
                $rAct = Invoke-RestMethod -Uri "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleAssignmentScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tokR"} -EA SilentlyContinue
                $rFound = $rAct.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq "Provisioned Machine Reader" }
                if ($rFound) { Write-Host "    Reader active after ${rEl}s" -ForegroundColor Green; break }
                if ($rEl % 60 -eq 0) { Write-Host "    Waiting: Reader (${rEl}s / 600s)" -ForegroundColor Gray }
            }
        }
        Write-Host "    Waiting 30s for ARM propagation..." -ForegroundColor Gray
        Start-Sleep 30
    }
    
    # Generate cert — should pick Contributor (higher than Reader)
    $o = az provisionedmachine ssh-cert-create --vault-name $VaultName --resource-id $EdgeMachine 2>&1 | Out-String
    if ($o -notmatch "certificatePath") { throw "Cert gen failed: $o" }
    
    $m = [regex]::Match($o, '\{[^}]+\}')
    if ($m.Success) {
        $j = $m.Value | ConvertFrom-Json
        $certOut = ssh-keygen -L -f $j.certificatePath 2>&1 | Out-String
        if ($certOut -match "role=Provisioned Machine Admin") { throw "Admin should not be active! Got: $certOut" }
        if ($certOut -notmatch "role=Provisioned Machine Contributor") { throw "Expected Contributor priority but got: $certOut" }
        Remove-Item -Recurse -Force (Split-Path $j.privateKeyPath) -EA SilentlyContinue
    }
    "Certificate generated with role=Provisioned Machine Contributor"
}

Run-Test "2.8" "No role on Provisioned Machine" "User has no PM roles on resource" `
    'ssh-cert-create on resource with no PM roles' "No Provisioned Machine role found" {
    $o = az provisionedmachine ssh-cert-create --vault-name $VaultName --resource-id $BadEdgeMachine 2>&1 | Out-String
    if ($o -match "certificatePath") { throw "Should not succeed without role" }
    if ($o -notmatch "No active|No Provisioned Machine|expired|deactivated|not found|401|InvalidAuthentication") { throw "Unexpected: $o" }
    "Rejected - no PM role"
}

Run-Test "2.9" "Invalid vault name - starts with digit" "Reject '1vault'" `
    'ssh-cert-create --vault-name "1vault"' "not a valid Key Vault name" {
    $o = az provisionedmachine ssh-cert-create --vault-name "1vault" --resource-id $dummyRid 2>&1 | Out-String
    if ($o -notmatch "not a valid Key Vault name") { throw "Wrong: $o" }; "Rejected"
}

Run-Test "2.10" "Invalid vault name - special chars" "Reject 'vault_name!'" `
    'ssh-cert-create --vault-name "vault_name!"' "not a valid Key Vault name" {
    $o = az provisionedmachine ssh-cert-create --vault-name "vault_name!" --resource-id $dummyRid 2>&1 | Out-String
    if ($o -notmatch "not a valid Key Vault name") { throw "Wrong: $o" }; "Rejected"
}

Run-Test "2.11" "Missing --vault-name" "Required param" `
    'ssh-cert-create --resource-id [RID]' "required: --vault-name" {
    $o = az provisionedmachine ssh-cert-create --resource-id $dummyRid 2>&1 | Out-String
    if ($o -notmatch "required.*vault-name|vault-name.*required") { throw "Wrong: $o" }; "Required"
}

Run-Test "2.12" "Missing --resource-id" "Required param" `
    'ssh-cert-create --vault-name test' "required: --resource-id" {
    $o = az provisionedmachine ssh-cert-create --vault-name test 2>&1 | Out-String
    if ($o -notmatch "required.*resource-id|resource-id.*required") { throw "Wrong: $o" }; "Required"
}

# ═════════════════════════════════════════════════════════════
# 3. AUTHENTICATION & AUTHORIZATION
# ═════════════════════════════════════════════════════════════
Write-Host "`n─── Phase 3: Authentication & Authorization ───" -ForegroundColor Magenta

Run-Test "3.1" "Not logged in" "Run after az logout" `
    "az logout && ssh-cert-create" "Error: az login required" {
    # Save current state, logout, test, re-login
    az logout 2>$null
    $o = az provisionedmachine ssh-cert-create --vault-name $VaultName --resource-id $EdgeMachine 2>&1 | Out-String
    # Re-login immediately
    az login --tenant $Tenant --only-show-errors 2>&1 | Out-Null
    az account set --subscription $Subscription 2>$null
    if ($o -notmatch "az login|login|not logged|Please sign") { throw "Unexpected: $o" }
    "Correctly requires login"
}

Run-Test "3.2" "Wrong tenant" "Login to Microsoft tenant, test against ALCS resource" `
    "az login --tenant msft && ssh-cert-create" "Auth error or resource not found" {
    az login --tenant 72f988bf-86f1-41af-91ab-2d7cd011db47 --only-show-errors 2>&1 | Out-Null
    $o = az provisionedmachine ssh-cert-create --vault-name $VaultName --resource-id $EdgeMachine 2>&1 | Out-String
    # Switch back
    az login --tenant $Tenant --only-show-errors 2>&1 | Out-Null
    az account set --subscription $Subscription 2>$null
    if ($o -match "certificatePath") { throw "Should fail with wrong tenant" }
    "Correctly failed with wrong tenant"
}

Run-Test "3.3" "Direct (non-PIM) role assignment rejected" "Assign direct PM role, verify cert FAILS without PIM, remove assignment" `
    "Direct role only (no PIM) on $EdgeMachine" "Direct role correctly rejected - PIM required" {
    # Deactivate all PIM roles first and wait until the PIM schedule API confirms no active SelfActivate
    Deactivate-AllPmRoles

    # Extra verification: poll roleAssignmentScheduleRequests to confirm no active PIM SelfActivate exists
    # (The extension's check_pim_eligibility checks this API, not role_assignments)
    Write-Host "    Verifying PIM schedule requests are cleared..." -ForegroundColor Gray
    $maxWaitPim = 300; $elapsedPim = 0
    while ($elapsedPim -lt $maxWaitPim) {
        $tokPim = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
        $schedUrl = "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests?api-version=2020-10-01"
        $schedResp = Invoke-RestMethod -Uri $schedUrl -Headers @{Authorization="Bearer $tokPim"} -EA SilentlyContinue
        $activeSelfActivate = @($schedResp.value | Where-Object {
            $p = $_.properties
            $p.principalId -eq $userOid -and
            $p.requestType -eq "SelfActivate" -and
            $p.status -eq "Provisioned"
        } | Where-Object {
            # Check if expired
            $sched = $_.properties.scheduleInfo
            $startStr = $sched.startDateTime
            $dur = $sched.expiration.duration
            if ($startStr -and $dur -match "(\d+)H") { $hrs = [int]$Matches[1] } 
            elseif ($dur -match "(\d+)M") { $hrs = [int]$Matches[1] / 60.0 }
            else { $hrs = 0 }
            if ($startStr -and $hrs -gt 0) {
                $start = [DateTime]::Parse($startStr).ToUniversalTime()
                $end = $start.AddHours($hrs)
                $end -gt [DateTime]::UtcNow
            } else { $true }
        })
        if ($activeSelfActivate.Count -eq 0) {
            Write-Host "    PIM schedule requests confirmed empty (no active SelfActivate)" -ForegroundColor Green
            break
        }
        Start-Sleep 10; $elapsedPim += 10
        if ($elapsedPim % 60 -eq 0) { Write-Host "    Waiting for PIM expiry... (${elapsedPim}s)" -ForegroundColor Gray }
    }
    if ($elapsedPim -ge $maxWaitPim) {
        throw "PIM SelfActivate records still active after 5min. Cannot test direct-only assignment."
    }

    # Now create a DIRECT (permanent) role assignment for Provisioned Machine Admin
    $directRoleName = "Provisioned Machine Admin"
    Write-Host "    Creating direct role assignment: $directRoleName on $EdgeMachine" -ForegroundColor Cyan
    $assignOut = az role assignment create --assignee-object-id $userOid --assignee-principal-type User --role $directRoleName --scope $EdgeMachine 2>&1 | Out-String
    if ($assignOut -match "ERROR|error" -and $assignOut -notmatch "already exists|RoleAssignmentExists") {
        throw "Failed to create direct role assignment: $assignOut"
    }

    # Wait for propagation
    Write-Host "    Waiting 30s for role assignment propagation..." -ForegroundColor Gray
    Start-Sleep 30

    try {
        # Verify cert-create FAILS — check_pim_eligibility() requires SelfActivate records
        # Direct/permanent assignments do NOT create SelfActivate requests, so must be rejected
        $o = az provisionedmachine ssh-cert-create --vault-name $VaultName --resource-id $EdgeMachine 2>&1 | Out-String
        if ($o -match "certificatePath") {
            throw "BUG: Extension accepted direct role assignment without PIM! check_pim_eligibility() should reject this."
        }
        # Verify the error message mentions PIM requirement
        if ($o -notmatch "PIM|expired|deactivated|JIT|re-activate|No active") {
            throw "Unexpected error (expected PIM-related rejection): $o"
        }
        Write-Host "    Correctly rejected: direct role without PIM activation" -ForegroundColor Green
    }
    finally {
        # ALWAYS clean up: remove the direct role assignment
        Write-Host "    Removing direct role assignment..." -ForegroundColor Cyan
        az role assignment delete --assignee $userOid --role $directRoleName --scope $EdgeMachine 2>&1 | Out-Null
        Start-Sleep 5
        Write-Host "    Direct role assignment removed." -ForegroundColor Green
    }

    "Direct role correctly rejected - PIM required"
}

Run-Test "3.4" "No role assignment at all" "Use resource where user has no roles" `
    'ssh-cert-create on unrelated resource' "No role / not found" {
    $o = az provisionedmachine ssh-cert-create --vault-name $VaultName --resource-id $BadEdgeMachine 2>&1 | Out-String
    if ($o -match "certificatePath") { throw "Should not succeed" }
    "Correctly rejected"
}

# Re-login after Phase 3 (which does logout/wrong-tenant tests)
Write-Host "`n  Re-establishing login to correct tenant..." -ForegroundColor Gray
az login --tenant $Tenant --only-show-errors 2>&1 | Out-Null
az account set --subscription $Subscription 2>$null

# ═════════════════════════════════════════════════════════════
# PRE-CHECK: Remove any direct KV role assignments (must be PIM-only)
# ═════════════════════════════════════════════════════════════
Write-Host "`n─── Pre-check: Ensure KV access is PIM-only ───" -ForegroundColor Magenta
$kvDirectRoles = az role assignment list --assignee $userOid --scope $KvResourceId --include-inherited --query "[?contains(roleDefinitionName, 'Key Vault')]" -o json 2>$null | ConvertFrom-Json
if ($kvDirectRoles -and $kvDirectRoles.Count -gt 0) {
    foreach ($kvr in $kvDirectRoles) {
        Write-Host "  Removing direct KV assignment: $($kvr.roleDefinitionName) (scope: $($kvr.scope))" -ForegroundColor Yellow
        az role assignment delete --assignee $userOid --role $kvr.roleDefinitionName --scope $kvr.scope 2>&1 | Out-Null
    }
    Write-Host "  Removed $($kvDirectRoles.Count) direct KV role assignment(s). KV access is now PIM-only." -ForegroundColor Green
} else {
    Write-Host "  No direct KV role assignments found — already PIM-only." -ForegroundColor Green
}

# ═════════════════════════════════════════════════════════════
# PIM ACTIVATION (Edge Machine + Key Vault, shortest duration)
# ═════════════════════════════════════════════════════════════
Write-Host "`n─── PIM Activation (Edge Machine + Key Vault) ───" -ForegroundColor Magenta
$pimOk = $false
$pimDuration = "PT30M"  # 30 minutes — enough for Phase 4-6 to complete

# --- Helper: Assign eligibility + Activate PIM for a role on a scope ---
function Activate-PimRole {
    param([string]$Scope, [string]$Role, [string]$Duration, [string]$Oid)
    
    $rd = az role definition list --name $Role --query "[0].id" -o tsv 2>$null
    if (-not $rd) {
        # Try built-in role ID for Key Vault Crypto User
        $rd = "/subscriptions/$Subscription/providers/Microsoft.Authorization/roleDefinitions/12338af0-0e69-4776-bea7-57ae8d297424"
    }
    $t = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
    
    # Check eligibility
    $er = Invoke-RestMethod -Uri "https://management.azure.com${Scope}/providers/Microsoft.Authorization/roleEligibilityScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${Oid}')" -Headers @{Authorization="Bearer $t"} -EA SilentlyContinue
    $eid = ($er.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq $Role -and $_.properties.memberType -eq "Direct" }).name
    
    # Create eligibility if missing
    if (-not $eid) {
        Write-Host "    Creating eligibility for '$Role' on scope..." -ForegroundColor Yellow
        $eg = [guid]::NewGuid().ToString()
        $eb = "{'properties':{'principalId':'${Oid}','roleDefinitionId':'${rd}','requestType':'AdminAssign','scheduleInfo':{'expiration':{'type':'AfterDuration','duration':'P365D'}}}}"
        az rest --method PUT --url "https://management.azure.com${Scope}/providers/Microsoft.Authorization/roleEligibilityScheduleRequests/${eg}?api-version=2020-10-01" --headers "Content-Type=application/json" --body $eb 2>&1 | Out-Null
        Start-Sleep 8
        $t = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
        $er = Invoke-RestMethod -Uri "https://management.azure.com${Scope}/providers/Microsoft.Authorization/roleEligibilityScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${Oid}')" -Headers @{Authorization="Bearer $t"}
        $eid = ($er.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq $Role -and $_.properties.memberType -eq "Direct" }).name
    }
    
    if (-not $eid) { return "NO_ELIGIBILITY" }
    
    # Activate
    $ag = [guid]::NewGuid().ToString()
    $ab = "{'properties':{'principalId':'${Oid}','roleDefinitionId':'${rd}','requestType':'SelfActivate','linkedRoleEligibilityScheduleId':'${eid}','justification':'E2E test $ts','scheduleInfo':{'expiration':{'type':'AfterDuration','duration':'${Duration}'}}}}"
    $ar = az rest --method PUT --url "https://management.azure.com${Scope}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/${ag}?api-version=2020-10-01" --headers "Content-Type=application/json" --body $ab 2>&1 | Out-String
    
    if ($ar -match '"status"\s*:\s*"Provisioned"') { return "ACTIVATED" }
    elseif ($ar -match "PendingApproval") { return "PENDING_APPROVAL" }
    elseif ($ar -match "RoleAssignmentExists") { return "ALREADY_ACTIVE" }
    else { return "FAILED:$ar" }
}

# --- Helper: Deactivate PIM ---
function Deactivate-PimRole {
    param([string]$Scope, [string]$Role, [string]$Oid)
    $rd = az role definition list --name $Role --query "[0].id" -o tsv 2>$null
    if (-not $rd) { $rd = "/subscriptions/$Subscription/providers/Microsoft.Authorization/roleDefinitions/12338af0-0e69-4776-bea7-57ae8d297424" }
    $dg = [guid]::NewGuid().ToString()
    $result = az rest --method PUT --url "https://management.azure.com${Scope}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/${dg}?api-version=2020-10-01" --headers "Content-Type=application/json" --body "{'properties':{'principalId':'${Oid}','roleDefinitionId':'${rd}','requestType':'SelfDeactivate','justification':'E2E deactivation'}}" 2>&1 | Out-String
    return $result
}

try {
    # --- Activate Edge Machine PIM ---
    Write-Host "  [1/2] Edge Machine: $RoleName ($pimDuration)..." -ForegroundColor Gray
    $emResult = Activate-PimRole -Scope $EdgeMachine -Role $RoleName -Duration $pimDuration -Oid $userOid
    
    if ($emResult -eq "ACTIVATED") {
        Write-Host "    Edge Machine PIM: ACTIVATED" -ForegroundColor Green
    } elseif ($emResult -eq "ALREADY_ACTIVE") {
        Write-Host "    Edge Machine PIM: Already active" -ForegroundColor Green
    } elseif ($emResult -eq "PENDING_APPROVAL") {
        Write-Host "    Edge Machine PIM: PENDING APPROVAL" -ForegroundColor Yellow
        $null = Prompt-Manual "Approve '$RoleName' PIM on Edge Machine: $EdgeMachine"
    } else {
        Write-Host "    Edge Machine PIM: $emResult" -ForegroundColor Yellow
        $null = Prompt-Manual "Activate '$RoleName' on Edge Machine manually: $EdgeMachine"
    }
    
    # --- Key Vault PIM: already activated for PT1H after test 3.5 ---
    Write-Host "  [2/2] Key Vault: KV Crypto User (already active from PT1H activation after Phase 3)" -ForegroundColor Gray
    $tokKvChk = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
    $kvSchedChk = Invoke-RestMethod -Uri "https://management.azure.com${KvResourceId}/providers/Microsoft.Authorization/roleAssignmentScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tokKvChk"} -EA SilentlyContinue
    $kvActiveChk = @($kvSchedChk.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq "Key Vault Crypto User" })
    if ($kvActiveChk.Count -gt 0) {
        Write-Host "    Key Vault PIM: confirmed active (PT1H)" -ForegroundColor Green
    } else {
        # Fallback: re-activate if not found (shouldn't happen unless approval timed out)
        Write-Host "    Key Vault PIM: not active, re-activating..." -ForegroundColor Yellow
        $kvFallback = Activate-PimRole -Scope $KvResourceId -Role "Key Vault Crypto User" -Duration "PT30M" -Oid $userOid
        Write-Host "    Key Vault PIM fallback: $kvFallback" -ForegroundColor $(if ($kvFallback -match "ACTIV") { "Green" } else { "Yellow" })
    }
    
    Start-Sleep 5
    $pimOk = $true
    Write-Host "  PIM activation complete. Window: $pimDuration (EM) + PT1H (KV)" -ForegroundColor Green
    
} catch {
    Write-Host "  Error: $_" -ForegroundColor Red
    $pimOk = Prompt-Manual "PIM setup failed. Activate both roles manually:`n  1. '$RoleName' on $EdgeMachine`n  2. 'Key Vault Crypto User' on $KvResourceId"
}

# ═════════════════════════════════════════════════════════════
# 4. KEY VAULT ERRORS (requires PIM)
# ═════════════════════════════════════════════════════════════
Write-Host "`n─── Phase 4: Key Vault Errors ───" -ForegroundColor Magenta

if ($pimOk) {
    Run-Test "4.1" "Non-existent vault" "Vault DNS doesn't resolve" `
        'ssh-cert-create --vault-name "nonExistentVault123"' "Unable to connect to Key Vault" {
        $o = az provisionedmachine ssh-cert-create --vault-name "nonExistentVault123" --resource-id $EdgeMachine 2>&1 | Out-String
        if ($o -match "certificatePath") { throw "Should fail" }
        if ($o -notmatch "Unable to connect|not found|error") { throw "Unexpected: $o" }
        "Correctly failed - vault not found"
    }

    Run-Test "4.2" "Vault exists but CA key missing" "No deviceId-ssh-ca key in vault" `
        "ssh-cert-create with wrong vault" "Key not found in vault" {
        # Use a valid vault but with a resource ID whose deviceId doesn't have a key
        $fakeEm = "/subscriptions/$Subscription/resourceGroups/ar-sff-rg/providers/Microsoft.AzureStackHCI/edgeMachines/nonExistentDevice999"
        $o = az provisionedmachine ssh-cert-create --vault-name $VaultName --resource-id $fakeEm 2>&1 | Out-String
        if ($o -match "certificatePath") { throw "Should fail" }
        if ($o -notmatch "not found|No active|PIM|Key.*not found") { throw "Unexpected: $o" }
        "Correctly failed - key missing or no PIM"
    }

    Run-Test "4.3" "No KV access permissions" "User lacks Key Get/Sign" `
        "ssh-cert-create with no-access vault" "Access denied" {
        $o = az provisionedmachine ssh-cert-create --vault-name $BadVault --resource-id $EdgeMachine 2>&1 | Out-String
        if ($o -match "certificatePath") { throw "Should fail" }
        if ($o -notmatch "Access denied|Forbidden|Unable to connect|not found|error") { throw "Unexpected: $o" }
        "Correctly failed - no KV access"
    }
} else {
    "4.1","4.2","4.3" | % { Skip-Test $_ "KV error test" "PIM not activated" }
}

# ═════════════════════════════════════════════════════════════
# 5. CERTIFICATE GENERATION (requires PIM)
# ═════════════════════════════════════════════════════════════
Write-Host "`n─── Phase 5: Certificate Generation ───" -ForegroundColor Magenta

$script:certPath = $null; $script:keyPath = $null
$customDir = Join-Path $env:TEMP "e2e_custom_$ts"

if ($pimOk) {
    Run-Test "5.1" "Successful cert generation (default paths)" "Happy path" `
        "ssh-cert-create --vault-name $VaultName" "JSON with privateKeyPath + certificatePath" {
        $o = az provisionedmachine ssh-cert-create --vault-name $VaultName --resource-id $EdgeMachine 2>&1 | Out-String
        if ($o -notmatch "certificatePath") { throw "Failed: $o" }
        $m = [regex]::Match($o, '\{[^}]+\}')
        if ($m.Success) { $j = $m.Value | ConvertFrom-Json; $script:certPath=$j.certificatePath; $script:keyPath=$j.privateKeyPath }
        "Certificate generated"
    }

    Run-Test "5.2" "Inspect generated certificate" "Verify principals and extensions" `
        "ssh-keygen -L -f [cert]" "username=[alias] role=Provisioned Machine Admin permit-pty" {
        if (-not $script:certPath) { throw "No cert from 5.1" }
        $o = ssh-keygen -L -f $script:certPath 2>&1 | Out-String
        $e = @()
        if ($o -notmatch "ssh-rsa-cert-v01@openssh.com") { $e += "wrong type" }
        if ($o -notmatch "username=") { $e += "no username" }
        if ($o -notmatch "role=Provisioned Machine Admin") { $e += "no role" }
        if ($o -notmatch "permit-pty") { $e += "no permit-pty" }
        if ($o -notmatch "rsa-sha2-512") { $e += "wrong signing algo" }
        if ($e.Count -gt 0) {
            throw ($e -join "; ")
        }
        "Cert valid"
    }

    Run-Test "5.3" "Multiple consecutive generations" "Each creates new temp dir" `
        "ssh-cert-create x3" "3 different directories" {
        $paths = @()
        1..3 | % {
            $o = az provisionedmachine ssh-cert-create --vault-name $VaultName --resource-id $EdgeMachine 2>&1 | Out-String
            $m = [regex]::Match($o, '\{[^}]+\}')
            if ($m.Success) { $j = $m.Value | ConvertFrom-Json; $paths += (Split-Path $j.privateKeyPath) }
        }
        $unique = $paths | Select-Object -Unique
        if ($unique.Count -lt 3) { throw "Expected 3 unique dirs, got $($unique.Count)" }
        # Cleanup extra dirs
        $paths | % { Remove-Item -Recurse -Force $_ -EA SilentlyContinue }
        "3 unique directories created"
    }

    Run-Test "5.4" "Private key is RSA-4096" "Confirm key strength" `
        "ssh-keygen -l -f [key]" "4096 SHA256:... (RSA)" {
        if (-not $script:keyPath) { throw "No key from 5.1" }
        $o = ssh-keygen -l -f $script:keyPath 2>&1 | Out-String
        if ($o -notmatch "4096.*RSA") { throw "Not RSA-4096: $o" }; "RSA-4096 confirmed"
    }

    # Create custom output dir
    New-Item -ItemType Directory -Path $customDir -Force | Out-Null

    Run-Test "5.5" "Custom output paths (both)" "Both --cert-path and --private-key-path" `
        "ssh-cert-create --private-key-path ... --cert-path ..." "Files at custom locations" {
        $ck = Join-Path $customDir "my_key"; $cc = Join-Path $customDir "my_cert.pub"
        $o = az provisionedmachine ssh-cert-create --vault-name $VaultName --resource-id $EdgeMachine --private-key-path $ck --cert-path $cc 2>&1 | Out-String
        if ($o -notmatch "certificatePath") { throw "Failed: $o" }
        if (-not (Test-Path $ck)) { throw "Key not at custom path" }
        if (-not (Test-Path $cc)) { throw "Cert not at custom path" }
        "Both files at custom paths"
    }

    Run-Test "5.6" "Custom --private-key-path only" "Only key path customized" `
        "ssh-cert-create --private-key-path ..." "Key at custom, cert in temp" {
        $ck2 = Join-Path $customDir "my_key2"
        $o = az provisionedmachine ssh-cert-create --vault-name $VaultName --resource-id $EdgeMachine --private-key-path $ck2 2>&1 | Out-String
        if ($o -notmatch "certificatePath") { throw "Failed: $o" }
        if (-not (Test-Path $ck2)) { throw "Key not at custom path" }
        "Key at custom path, cert in temp"
    }

    Run-Test "5.7" "Custom --cert-path only" "Only cert path customized" `
        "ssh-cert-create --cert-path ..." "Cert at custom, key in temp" {
        $cc2 = Join-Path $customDir "my_cert2.pub"
        $o = az provisionedmachine ssh-cert-create --vault-name $VaultName --resource-id $EdgeMachine --cert-path $cc2 2>&1 | Out-String
        if ($o -notmatch "certificatePath") { throw "Failed: $o" }
        if (-not (Test-Path $cc2)) { throw "Cert not at custom path" }
        "Cert at custom path, key in temp"
    }

    Run-Test "5.8" "Custom path - non-existent directory" "Dir does not exist" `
        "ssh-cert-create --private-key-path C:\nonexistent\folder\key" "Directory does not exist" {
        $o = az provisionedmachine ssh-cert-create --vault-name $VaultName --resource-id $EdgeMachine --private-key-path "C:\nonexistent\folder\key" 2>&1 | Out-String
        if ($o -notmatch "does not exist|not found|error") { throw "Unexpected: $o" }
        "Correctly rejected non-existent dir"
    }

    # Cleanup custom dir
    Remove-Item -Recurse -Force $customDir -EA SilentlyContinue
} else {
    "5.1","5.2","5.3","5.4","5.5","5.6","5.7","5.8" | % { Skip-Test $_ "Cert gen test" "PIM not activated" }
}

# ═════════════════════════════════════════════════════════════
# 6. SSH CONNECTION (requires Docker + cert)
# ═════════════════════════════════════════════════════════════
Write-Host "`n─── Phase 6: SSH Connection ───" -ForegroundColor Magenta

$dockerOk = $false; try { docker info 2>$null | Out-Null; $dockerOk=$true } catch {}

if ($dockerOk -and $script:certPath) {
    # Ensure container running
    $st = docker ps --filter "name=$ContainerName" --format "{{.Status}}" 2>$null
    if ($st -notmatch "Up") {
        docker stop $ContainerName 2>$null; docker rm $ContainerName 2>$null
        az acr login --name $AcrName 2>$null
        docker pull $ImageName 2>$null
        docker run -d -p "${SshPort}:22" --name $ContainerName $ImageName 2>$null
        Start-Sleep 5
    }

    Run-Test "6.1" "SSH with generated certificate" "Full login using cert" `
        "ssh -p $SshPort ${userAlias}_jit@localhost" "whoami returns ${userAlias}_jit" {
        $ju = "${userAlias}_jit"
        $o = ssh -i $script:keyPath -o "CertificateFile=$($script:certPath)" -o UserKnownHostsFile=NUL -o StrictHostKeyChecking=no -o BatchMode=yes -p $SshPort "${ju}@localhost" 'whoami; echo E2E_SSH_OK' 2>&1 | Out-String
        if ($o -notmatch "E2E_SSH_OK") { throw "SSH failed: $o" }
        "SSH succeeded as $ju"
    }

    Skip-Test "6.2" "SSH with expired certificate" "PIM window is $pimDuration - run script again after expiry to test"

    Run-Test "6.3" "SSH with wrong OS user" "Login as non-existent user" `
        "ssh -p $SshPort wronguser@localhost" "Permission denied" {
        $o = ssh -i $script:keyPath -o "CertificateFile=$($script:certPath)" -o UserKnownHostsFile=NUL -o StrictHostKeyChecking=no -o BatchMode=yes -p $SshPort "wronguser@localhost" "whoami" 2>&1 | Out-String
        if ($o -match "wronguser" -and $o -notmatch "denied|error|refused") { throw "Should have been rejected" }
        "Correctly rejected wrong user"
    }

    Run-Test "6.4" "SSH without certificate (key only)" "Key alone not authorized" `
        "ssh -p $SshPort (no cert)" "Permission denied" {
        $ju = "${userAlias}_jit"
        $o = ssh -i $script:keyPath -o UserKnownHostsFile=NUL -o StrictHostKeyChecking=no -o BatchMode=yes -p $SshPort "${ju}@localhost" "whoami" 2>&1 | Out-String
        $matchPat = "E2E_SSH_OK"
        if ($o -match $matchPat) { throw "Should not succeed without cert" }
        "Correctly rejected - key only, no cert"
    }
} elseif (-not $dockerOk) {
    "6.1","6.2","6.3","6.4" | % { Skip-Test $_ "SSH test" "Docker not available" }
} else {
    "6.1","6.2","6.3","6.4" | % { Skip-Test $_ "SSH test" "No certificate from Phase 5" }
}

# ── Cleanup ──────────────────────────────────────────────────
if ($script:keyPath) {
    $kd = Split-Path $script:keyPath
    if ($kd -match "azssh_pm_") { Remove-Item -Recurse -Force $kd -EA SilentlyContinue }
}

# ── Results ──────────────────────────────────────────────────
$pass = ($results | ? Status -eq "PASS").Count
$fail = ($results | ? Status -eq "FAIL").Count
$skip = ($results | ? Status -eq "SKIP").Count
$total = $results.Count
$c = if ($fail -eq 0) { "Green" } else { "Red" }

Write-Host "`n================================================================" -ForegroundColor $c
Write-Host "  RESULTS: Total=$total | Pass=$pass | Fail=$fail | Skip=$skip" -ForegroundColor $c
Write-Host "================================================================" -ForegroundColor $c

$results | Format-Table SNo, TestCase, Status, Duration, @{L="Result";E={$_.ActualResult.Substring(0,[Math]::Min($_.ActualResult.Length,60))}} -AutoSize

$results | Export-Csv $resultsFile -NoTypeInformation
Write-Host "Saved: $resultsFile" -ForegroundColor Yellow
Write-Host "Done" -ForegroundColor Yellow
