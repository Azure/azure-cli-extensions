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
    [int]$SshPort         = 2222
)

$ErrorActionPreference = "Continue"
$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$resultsFile = "e2e-results-$ts.csv"
$results = @()
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# ── helpers ──────────────────────────────────────────────────
function Run-Test {
    param([string]$Id,[string]$Name,[string]$Desc,[string]$Cmd,[string]$Expected,[scriptblock]$Block)
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
# 1. EXTENSION INSTALLATION & HELP
# ═════════════════════════════════════════════════════════════
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
    $q = '[?name==''provisionedmachine''].{N:name,V:version}'
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
    
    # Remove ALL PM role assignments (including inherited from parent RG/subscription)
    $allAssignments = az role assignment list --assignee $userOid --scope $EdgeMachine --include-inherited --query "[?contains(roleDefinitionName, 'Provisioned Machine')]" -o json 2>$null | ConvertFrom-Json
    if ($allAssignments -and $allAssignments.Count -gt 0) {
        foreach ($a in $allAssignments) {
            Write-Host "    Removing direct assignment: $($a.roleDefinitionName) (scope: $($a.scope))" -ForegroundColor Gray
            az role assignment delete --ids $a.id 2>&1 | Out-Null
        }
        Start-Sleep 5
    }
    
    $minDurationHit = $false
    foreach ($rn in $allPmRoles) {
        $rd = az role definition list --name $rn --query "[0].id" -o tsv 2>$null
        if ($rd) {
            $dg = [guid]::NewGuid().ToString()
            $deactOut = az rest --method PUT --url "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/${dg}?api-version=2020-10-01" --headers "Content-Type=application/json" --body "{'properties':{'principalId':'${userOid}','roleDefinitionId':'${rd}','requestType':'SelfDeactivate','justification':'E2E role isolation'}}" 2>&1 | Out-String
            if ($deactOut -match "minimum.*duration|not allowed before|ActiveDurationTooShort|MinimumActiveDuration") {
                Write-Host "    '$rn' cannot be deactivated yet (min activation duration). Will wait..." -ForegroundColor Yellow
                $minDurationHit = $true
            }
        }
    }

    # If any role hit minimum duration error, wait 5 minutes then retry deactivation
    if ($minDurationHit) {
        Write-Host "    Waiting 5 min for minimum activation duration to pass..." -ForegroundColor Yellow
        $waitElapsed = 0
        while ($waitElapsed -lt 300) {
            Start-Sleep 10; $waitElapsed += 10
            if ($waitElapsed % 60 -eq 0) { Write-Host "    Waited ${waitElapsed}s / 300s..." -ForegroundColor Gray }
        }
        # Retry deactivation after waiting
        foreach ($rn in $allPmRoles) {
            $rd = az role definition list --name $rn --query "[0].id" -o tsv 2>$null
            if ($rd) {
                $dg2 = [guid]::NewGuid().ToString()
                az rest --method PUT --url "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/${dg2}?api-version=2020-10-01" --headers "Content-Type=application/json" --body "{'properties':{'principalId':'${userOid}','roleDefinitionId':'${rd}','requestType':'SelfDeactivate','justification':'E2E role isolation retry'}}" 2>&1 | Out-Null
            }
        }
    }

    # Poll for up to 5 minutes (every 10s) — confirm deactivation via role assignment schedule API
    Write-Host "    Polling for PIM deactivation (every 10s, max 5min)..." -ForegroundColor Gray
    $maxWait = 300; $elapsed = 0
    while ($elapsed -lt $maxWait) {
        Start-Sleep 10; $elapsed += 10
        # Query active role assignment schedules to confirm no PM roles are active
        $tokDeact = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
        $schedResp = Invoke-RestMethod -Uri "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleAssignmentScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tokDeact"} -EA SilentlyContinue
        $activePm = @($schedResp.value | Where-Object {
            $dn = $_.properties.expandedProperties.roleDefinition.displayName
            $dn -match "Provisioned Machine"
        })
        if ($activePm.Count -eq 0) {
            Write-Host "    PIM deactivated after ${elapsed}s (confirmed via API)" -ForegroundColor Green
            return
        }
        $activeNames = ($activePm | ForEach-Object { $_.properties.expandedProperties.roleDefinition.displayName }) -join ", "
        Write-Host "    Still active: $activeNames (${elapsed}s)" -ForegroundColor Gray
    }
    Write-Host "    WARNING: PIM still active after 5min polling" -ForegroundColor Yellow
}

# Helper: Activate a specific role (polls for approval up to 5 min every 10s)
function Activate-SingleRole {
    param([string]$RoleName2, [string]$RoleDef2)
    
    $tok3 = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
    $er3 = Invoke-RestMethod -Uri "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleEligibilityScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tok3"} -EA SilentlyContinue
    $eid3 = ($er3.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq $RoleName2 -and $_.properties.memberType -eq "Direct" }).name
    
    # Create eligibility if not exists
    if (-not $eid3) {
        $eg3 = [guid]::NewGuid().ToString()
        $eb3 = "{'properties':{'principalId':'${userOid}','roleDefinitionId':'${RoleDef2}','requestType':'AdminAssign','scheduleInfo':{'expiration':{'type':'AfterDuration','duration':'PT1H'}}}}"
        az rest --method PUT --url "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleEligibilityScheduleRequests/${eg3}?api-version=2020-10-01" --headers "Content-Type=application/json" --body $eb3 2>&1 | Out-Null
        Start-Sleep 8
        $tok3 = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
        $er3 = Invoke-RestMethod -Uri "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleEligibilityScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tok3"}
        $eid3 = ($er3.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq $RoleName2 -and $_.properties.memberType -eq "Direct" }).name
    }
    if (-not $eid3) { throw "Could not get eligibility for $RoleName2" }
    
    # Attempt activation — if PendingApproval, poll every 10s for 5 min
    $ag3 = [guid]::NewGuid().ToString()
    $ab3 = "{'properties':{'principalId':'${userOid}','roleDefinitionId':'${RoleDef2}','requestType':'SelfActivate','linkedRoleEligibilityScheduleId':'${eid3}','justification':'E2E role test','scheduleInfo':{'expiration':{'type':'AfterDuration','duration':'PT5M'}}}}"
    $actOut3 = az rest --method PUT --url "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/${ag3}?api-version=2020-10-01" --headers "Content-Type=application/json" --body $ab3 2>&1 | Out-String
    
    if ($actOut3 -match '"status"\s*:\s*"Provisioned"|RoleAssignmentExists') { return }
    
    if ($actOut3 -match "PendingApproval|PendingRoleAssignment|Pending") {
        Write-Host "    '$RoleName2' pending approval — polling every 10s for 5min..." -ForegroundColor Yellow
        Write-Host "    >>> Please APPROVE in Azure Portal: '$RoleName2' on $EdgeMachine <<<" -ForegroundColor Yellow
        $maxWait = 300; $elapsed = 0
        while ($elapsed -lt $maxWait) {
            Start-Sleep 10; $elapsed += 10
            # Check if cert-create now works (means PIM got approved)
            $check = az provisionedmachine ssh-cert-create --vault-name $VaultName --resource-id $EdgeMachine 2>&1 | Out-String
            if ($check -match "certificatePath") {
                Write-Host "    Approved and active after ${elapsed}s" -ForegroundColor Green
                return
            }
            # Also try re-activating in case the pending cleared
            $ag4 = [guid]::NewGuid().ToString()
            $reAct = az rest --method PUT --url "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/${ag4}?api-version=2020-10-01" --headers "Content-Type=application/json" --body $ab3 2>&1 | Out-String
            if ($reAct -match '"status"\s*:\s*"Provisioned"|RoleAssignmentExists') {
                Write-Host "    Activated after ${elapsed}s" -ForegroundColor Green
                return
            }
            if ($elapsed % 60 -eq 0) { Write-Host "    Waiting... (${elapsed}s / 300s)" -ForegroundColor Gray }
        }
        throw "Timed out waiting for approval of '$RoleName2' after 5 minutes. Approve in Portal: $EdgeMachine"
    }
    
    throw "Activation failed for $RoleName2 : $actOut3"
}

# Helper: Ensure KV Crypto User PIM is active (needed for cert signing)
function Ensure-KvPim {
    $kvRole = "Key Vault Crypto User"
    $kvRd = "/subscriptions/$Subscription/providers/Microsoft.Authorization/roleDefinitions/12338af0-0e69-4776-bea7-57ae8d297424"
    $tokKv = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv 2>$null
    
    # Check if already active via schedule instances
    $kvSched = Invoke-RestMethod -Uri "https://management.azure.com${KvResourceId}/providers/Microsoft.Authorization/roleAssignmentScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $tokKv"} -EA SilentlyContinue
    $kvActive = @($kvSched.value | Where-Object { $_.properties.expandedProperties.roleDefinition.displayName -eq $kvRole })
    if ($kvActive.Count -gt 0) {
        Write-Host "    KV Crypto User PIM: already active" -ForegroundColor Green
        return
    }
    
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
    
    # Activate
    $ag = [guid]::NewGuid().ToString()
    $ab = "{'properties':{'principalId':'${userOid}','roleDefinitionId':'${kvRd}','requestType':'SelfActivate','linkedRoleEligibilityScheduleId':'${kvEid}','justification':'E2E cert test','scheduleInfo':{'expiration':{'type':'AfterDuration','duration':'PT30M'}}}}"
    $ar = az rest --method PUT --url "https://management.azure.com${KvResourceId}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/${ag}?api-version=2020-10-01" --headers "Content-Type=application/json" --body $ab 2>&1 | Out-String
    
    if ($ar -match '"status"\s*:\s*"Provisioned"|RoleAssignmentExists') {
        Write-Host "    KV Crypto User PIM: ACTIVATED" -ForegroundColor Green
        return
    }
    if ($ar -match "PendingApproval") {
        Write-Host "    KV Crypto User PIM: PENDING APPROVAL" -ForegroundColor Yellow
        Write-Host "    >>> Please APPROVE 'Key Vault Crypto User' on $KvResourceId <<<" -ForegroundColor Yellow
        $maxWait = 300; $elapsed = 0
        while ($elapsed -lt $maxWait) {
            Start-Sleep 10; $elapsed += 10
            $ag2 = [guid]::NewGuid().ToString()
            $reAct = az rest --method PUT --url "https://management.azure.com${KvResourceId}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/${ag2}?api-version=2020-10-01" --headers "Content-Type=application/json" --body $ab 2>&1 | Out-String
            if ($reAct -match '"status"\s*:\s*"Provisioned"|RoleAssignmentExists') {
                Write-Host "    KV Crypto User approved after ${elapsed}s" -ForegroundColor Green
                return
            }
            if ($elapsed % 60 -eq 0) { Write-Host "    Waiting for KV approval... (${elapsed}s / 300s)" -ForegroundColor Gray }
        }
        throw "KV Crypto User PIM approval timed out after 5min"
    }
    Write-Host "    KV Crypto User PIM activation: $ar" -ForegroundColor Yellow
}

Run-Test "2.5" "Reader role on Provisioned Machine" "Deactivate all, assign Reader, verify cert" `
    "Isolate Reader role, ssh-cert-create" "Certificate generated with role=Provisioned Machine Reader" {
    $readerDef = az role definition list --name "Provisioned Machine Reader" --query "[0].id" -o tsv 2>$null
    if (-not $readerDef) { throw "Provisioned Machine Reader role not found" }
    
    # Deactivate all roles first (Admin has highest priority, must be gone)
    Deactivate-AllPmRoles
    
    # Explicitly ensure Admin and Contributor are deactivated (they outrank Reader)
    $adminDef25 = az role definition list --name "Provisioned Machine Admin" --query "[0].id" -o tsv 2>$null
    $contribDef25 = az role definition list --name "Provisioned Machine Contributor" --query "[0].id" -o tsv 2>$null
    foreach ($higherDef in @($adminDef25, $contribDef25)) {
        if ($higherDef) {
            $dg25 = [guid]::NewGuid().ToString()
            az rest --method PUT --url "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/${dg25}?api-version=2020-10-01" --headers "Content-Type=application/json" --body "{'properties':{'principalId':'${userOid}','roleDefinitionId':'${higherDef}','requestType':'SelfDeactivate','justification':'Ensure only Reader is active'}}" 2>&1 | Out-Null
        }
    }
    Start-Sleep 5
    
    # Activate only Reader
    Activate-SingleRole -RoleName2 "Provisioned Machine Reader" -RoleDef2 $readerDef
    Start-Sleep 5
    
    # Ensure KV Crypto User PIM is active (required for cert signing)
    Ensure-KvPim
    
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

Run-Test "2.6" "Admin role on Provisioned Machine" "Deactivate all, assign Admin, verify cert" `
    "Isolate Admin role, ssh-cert-create" "Certificate generated with role=Provisioned Machine Admin" {
    $adminDef = az role definition list --name "Provisioned Machine Admin" --query "[0].id" -o tsv 2>$null
    if (-not $adminDef) { throw "Provisioned Machine Admin role not found" }
    
    # Deactivate all roles first (Reader/Contributor must be gone)
    Deactivate-AllPmRoles
    
    # Explicitly ensure Reader and Contributor are deactivated
    $readerDef26 = az role definition list --name "Provisioned Machine Reader" --query "[0].id" -o tsv 2>$null
    $contribDef26 = az role definition list --name "Provisioned Machine Contributor" --query "[0].id" -o tsv 2>$null
    foreach ($otherDef in @($readerDef26, $contribDef26)) {
        if ($otherDef) {
            $dg26 = [guid]::NewGuid().ToString()
            az rest --method PUT --url "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/${dg26}?api-version=2020-10-01" --headers "Content-Type=application/json" --body "{'properties':{'principalId':'${userOid}','roleDefinitionId':'${otherDef}','requestType':'SelfDeactivate','justification':'Ensure only Admin is active'}}" 2>&1 | Out-Null
        }
    }
    Start-Sleep 5
    
    # Activate only Admin
    Activate-SingleRole -RoleName2 "Provisioned Machine Admin" -RoleDef2 $adminDef
    Start-Sleep 5
    
    # Ensure KV Crypto User PIM is active (required for cert signing)
    Ensure-KvPim
    
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

Run-Test "2.7" "Contributor role on Provisioned Machine" "Deactivate all, assign Contributor, verify cert" `
    "Isolate Contributor role, ssh-cert-create" "Certificate generated with role=Provisioned Machine Contributor" {
    $contribDef = az role definition list --name "Provisioned Machine Contributor" --query "[0].id" -o tsv 2>$null
    if (-not $contribDef) { throw "Provisioned Machine Contributor role not found" }
    
    # Deactivate all roles first (Admin outranks Contributor, must be gone)
    Deactivate-AllPmRoles
    
    # Explicitly ensure Admin is deactivated (it outranks Contributor)
    $adminDef27 = az role definition list --name "Provisioned Machine Admin" --query "[0].id" -o tsv 2>$null
    if ($adminDef27) {
        $dg27 = [guid]::NewGuid().ToString()
        az rest --method PUT --url "https://management.azure.com${EdgeMachine}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/${dg27}?api-version=2020-10-01" --headers "Content-Type=application/json" --body "{'properties':{'principalId':'${userOid}','roleDefinitionId':'${adminDef27}','requestType':'SelfDeactivate','justification':'Ensure only Contributor is active'}}" 2>&1 | Out-Null
    }
    Start-Sleep 5
    
    # Activate only Contributor
    Activate-SingleRole -RoleName2 "Provisioned Machine Contributor" -RoleDef2 $contribDef
    Start-Sleep 5
    
    # Ensure KV Crypto User PIM is active (required for cert signing)
    Ensure-KvPim
    
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
    
    # --- Activate Key Vault PIM ---
    Write-Host "  [2/2] Key Vault: Key Vault Crypto User ($pimDuration)..." -ForegroundColor Gray
    $kvResult = Activate-PimRole -Scope $KvResourceId -Role "Key Vault Crypto User" -Duration $pimDuration -Oid $userOid
    
    if ($kvResult -eq "ACTIVATED") {
        Write-Host "    Key Vault PIM: ACTIVATED" -ForegroundColor Green
    } elseif ($kvResult -eq "ALREADY_ACTIVE") {
        Write-Host "    Key Vault PIM: Already active" -ForegroundColor Green
    } elseif ($kvResult -eq "PENDING_APPROVAL") {
        Write-Host "    Key Vault PIM: PENDING APPROVAL" -ForegroundColor Yellow
        $null = Prompt-Manual "Approve 'Key Vault Crypto User' PIM on vault: $KvResourceId"
    } elseif ($kvResult -eq "NO_ELIGIBILITY") {
        # KV Crypto User might be direct assignment (not PIM) - that is fine
        Write-Host "    Key Vault: No PIM eligibility (may have direct RBAC - OK)" -ForegroundColor Gray
    } else {
        Write-Host "    Key Vault PIM: $kvResult" -ForegroundColor Yellow
        $null = Prompt-Manual "Activate 'Key Vault Crypto User' on vault manually: $KvResourceId"
    }
    
    Start-Sleep 5
    $pimOk = $true
    Write-Host "  PIM activation complete. Window: $pimDuration" -ForegroundColor Green
    
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
