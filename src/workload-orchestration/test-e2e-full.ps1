# Full end-to-end regression for shorthand-syntax refactor + children-array rule.
# Drives real az CLI calls. Creates + destroys two fresh RGs for real hierarchy tests.

$ErrorActionPreference = 'Continue'
$env:PATH = "C:\Users\audapure\Projects\ConfigManager\CLI\.venv\Scripts;$env:PATH"

$script:pass = 0
$script:fail = 0
$script:results = @()

function Test-Az {
    param(
        [string]$Name,
        [string[]]$AzArgs,
        [bool]$ShouldFail,
        [string]$ExpectInOutput = $null,
        [string]$RejectInOutput = $null
    )
    Write-Host ""
    Write-Host ">> $Name" -ForegroundColor Cyan
    Write-Host "   az $($AzArgs -join ' ')" -ForegroundColor DarkGray
    $out = & az @AzArgs 2>&1 | Out-String
    $exit = $LASTEXITCODE

    $failed = $false
    $reason = ''
    if ($ShouldFail)  { if ($exit -eq 0) { $failed = $true; $reason = 'expected failure; exit=0' } }
    else              { if ($exit -ne 0) { $failed = $true; $reason = "expected success; exit=$exit" } }

    if (-not $failed -and $ExpectInOutput -and ($out -notmatch [regex]::Escape($ExpectInOutput))) {
        $failed = $true; $reason = "missing expected: $ExpectInOutput"
    }
    if (-not $failed -and $RejectInOutput -and ($out -match [regex]::Escape($RejectInOutput))) {
        $failed = $true; $reason = "should not contain: $RejectInOutput"
    }

    if ($failed) {
        Write-Host "   FAIL: $reason" -ForegroundColor Red
        ($out -split "`n" | Select-Object -Last 6) | ForEach-Object { Write-Host "     $_" -ForegroundColor DarkGray }
        $script:fail++
        $script:results += [PSCustomObject]@{Name=$Name; Status='FAIL'; Reason=$reason}
    } else {
        Write-Host "   PASS" -ForegroundColor Green
        $script:pass++
        $script:results += [PSCustomObject]@{Name=$Name; Status='PASS'; Reason=''}
    }
}

$NX = 'zzz-nonexistent-cluster-999'
$NXRG = 'zzz-nonexistent-rg-999'

Write-Host ""
Write-Host "===== Shorthand Refactor + Children-Array -- Full E2E =====" -ForegroundColor Magenta

# =================================================================
# SECTION 1: Help output
# =================================================================
Write-Host ""
Write-Host "--- Help output ---" -ForegroundColor Yellow

Test-Az 'help: cluster init shows --extension-dependency-version' @('workload-orchestration','cluster','init','--help') $false 'extension-dependency-version'
Test-Az 'help: cluster init shows shorthand example' @('workload-orchestration','cluster','init','--help') $false 'iotplatform:0.7.6'
Test-Az 'help: cluster init no old cert-manager-version' @('workload-orchestration','cluster','init','--help') $false $null 'cert-manager-version'
Test-Az 'help: hierarchy create shows inline shorthand' @('workload-orchestration','hierarchy','create','--help') $false 'name:Mehoopany'
Test-Az 'help: hierarchy create shows @file' @('workload-orchestration','hierarchy','create','--help') $false '@hierarchy.yaml'

# =================================================================
# SECTION 2: Flag removal
# =================================================================
Write-Host ""
Write-Host "--- Old flag removed ---" -ForegroundColor Yellow
Test-Az 'CLI: old --cert-manager-version rejected' @('workload-orchestration','cluster','init','-c',$NX,'-g',$NXRG,'-l','eastus2euap','--cert-manager-version','1.0') $true 'unrecognized arguments'

# =================================================================
# SECTION 3: extension-dependency-version validation
# =================================================================
Write-Host ""
Write-Host "--- extension-dependency-version validation ---" -ForegroundColor Yellow

Test-Az 'ext-dep: unknown key (partial) rejected' @('workload-orchestration','cluster','init','-c',$NX,'-g',$NXRG,'-l','eastus2euap','--extension-dependency-version','bogus=1.0') $true
Test-Az 'ext-dep: unknown key (full) rejected' @('workload-orchestration','cluster','init','-c',$NX,'-g',$NXRG,'-l','eastus2euap','--extension-dependency-version','{bogus:1.0}') $true
Test-Az 'ext-dep: empty value rejected' @('workload-orchestration','cluster','init','-c',$NX,'-g',$NXRG,'-l','eastus2euap','--extension-dependency-version','iotplatform=') $true
Test-Az 'ext-dep: duplicate (case-insensitive) rejected' @('workload-orchestration','cluster','init','-c',$NX,'-g',$NXRG,'-l','eastus2euap','--extension-dependency-version','{iotplatform:1.0,IOTPlatform:2.0}') $true
Test-Az 'ext-dep: array rejected' @('workload-orchestration','cluster','init','-c',$NX,'-g',$NXRG,'-l','eastus2euap','--extension-dependency-version','[iotplatform,1.0]') $true
Test-Az 'ext-dep: bare token (no =) rejected' @('workload-orchestration','cluster','init','-c',$NX,'-g',$NXRG,'-l','eastus2euap','--extension-dependency-version','iotplatform') $true

# File input
$df = Join-Path $env:TEMP 'deps-valid.json'
'{"iotplatform":"1.6.1"}' | Set-Content -Path $df -Encoding utf8
Test-Az 'ext-dep: @file.json parses (past parser)' @('workload-orchestration','cluster','init','-c',$NX,'-g',$NXRG,'-l','eastus2euap','--extension-dependency-version',"@$df") $true $null 'Unknown dependency key'
$dfBad = Join-Path $env:TEMP 'deps-bad.json'
'{"notarealkey":"1.6.1"}' | Set-Content -Path $dfBad -Encoding utf8
Test-Az 'ext-dep: @file.json unknown key rejected' @('workload-orchestration','cluster','init','-c',$NX,'-g',$NXRG,'-l','eastus2euap','--extension-dependency-version',"@$dfBad") $true
Test-Az 'ext-dep: @missing file rejected' @('workload-orchestration','cluster','init','-c',$NX,'-g',$NXRG,'-l','eastus2euap','--extension-dependency-version','@C:\no-such-deps-xyz.json') $true
Remove-Item $df, $dfBad -ErrorAction SilentlyContinue

# =================================================================
# SECTION 4: hierarchy-spec shorthand validation
# =================================================================
Write-Host ""
Write-Host "--- hierarchy-spec validation ---" -ForegroundColor Yellow

Test-Az 'hierarchy: inline missing name rejected' @('workload-orchestration','hierarchy','create','-g',$NXRG,'--configuration-location','eastus2euap','--hierarchy-spec','{level:factory}') $true "must include 'name'"
Test-Az 'hierarchy: inline missing level rejected' @('workload-orchestration','hierarchy','create','-g',$NXRG,'--configuration-location','eastus2euap','--hierarchy-spec','{name:FactoryZ}') $true "must include 'level'"
Test-Az 'hierarchy: invalid name rejected' @('workload-orchestration','hierarchy','create','-g',$NXRG,'--configuration-location','eastus2euap','--hierarchy-spec','{name:-bad-,level:factory}') $true
Test-Az 'hierarchy: scalar rejected' @('workload-orchestration','hierarchy','create','-g',$NXRG,'--configuration-location','eastus2euap','--hierarchy-spec','justastring') $true
Test-Az 'hierarchy: @missing file rejected' @('workload-orchestration','hierarchy','create','-g',$NXRG,'--configuration-location','eastus2euap','--hierarchy-spec','@no-such-file.yaml') $true

# =================================================================
# SECTION 5: children-must-be-list enforcement
# =================================================================
Write-Host ""
Write-Host "--- children-must-be-list ---" -ForegroundColor Yellow

# children as a DICT must be rejected
$ydict = Join-Path $env:TEMP 'hier-children-dict.yaml'
@"
type: ServiceGroup
name: CountryX
level: country
children:
  name: RegionY
  level: region
"@ | Set-Content -Path $ydict -Encoding utf8
Test-Az 'hierarchy: children as dict rejected' @('workload-orchestration','hierarchy','create','-g',$NXRG,'--configuration-location','eastus2euap','--hierarchy-spec',"@$ydict") $true
Remove-Item $ydict -ErrorAction SilentlyContinue

# children as a LIST parses fine (Azure call fails on nonexistent RG — but parser passed)
$ylist = Join-Path $env:TEMP 'hier-children-list.yaml'
@"
type: ServiceGroup
name: CountryL
level: country
children:
  - name: RegionL
    level: region
"@ | Set-Content -Path $ylist -Encoding utf8
Test-Az 'hierarchy: children as list parses (Azure fail expected)' @('workload-orchestration','hierarchy','create','-g',$NXRG,'--configuration-location','eastus2euap','--hierarchy-spec',"@$ylist") $true $null "must be a list"
Remove-Item $ylist -ErrorAction SilentlyContinue

# =================================================================
# SECTION 6: REAL end-to-end on fresh RGs
# =================================================================
Write-Host ""
Write-Host "--- REAL end-to-end on fresh RGs ---" -ForegroundColor Yellow

$rgRG  = "audapure-e2e-rg-$(Get-Random -Max 9999)"
$rgSG  = "audapure-e2e-sg-$(Get-Random -Max 9999)"
$suffix = Get-Random -Max 9999

try {
    # --- RG hierarchy via inline shorthand ---
    Write-Host ""
    Write-Host "Creating fresh RG for RG-hierarchy test: $rgRG" -ForegroundColor DarkGray
    az group create -n $rgRG -l eastus2euap -o none 2>&1 | Out-Null

    Test-Az 'REAL: hierarchy create (RG, inline shorthand)' `
        @('workload-orchestration','hierarchy','create','-g',$rgRG,'--configuration-location','eastus2euap','--hierarchy-spec',"{type:ResourceGroup,name:Factory$suffix,level:factory}") `
        $false 'Hierarchy created'

    # --- SG hierarchy with TWO children via YAML file ---
    Write-Host ""
    Write-Host "Creating fresh RG for SG-hierarchy test: $rgSG" -ForegroundColor DarkGray
    az group create -n $rgSG -l eastus2euap -o none 2>&1 | Out-Null

    $sgYaml = Join-Path $env:TEMP "hier-sg-real-$suffix.yaml"
    @"
type: ServiceGroup
name: Country$suffix
level: country
children:
  - name: RegionA$suffix
    level: region
  - name: RegionB$suffix
    level: region
"@ | Set-Content -Path $sgYaml -Encoding utf8

    Test-Az 'REAL: hierarchy create (SG, 2 sibling children via @YAML)' `
        @('workload-orchestration','hierarchy','create','-g',$rgSG,'--configuration-location','eastus2euap','--hierarchy-spec',"@$sgYaml") `
        $false 'Hierarchy created'

    # Verify TWO regions appeared under the country in output (name substrings unique to this run)
    Test-Az 'REAL: both SG siblings exist (list RegionA)' `
        @('resource','list','-g',$rgSG,'--query',"[?contains(name, 'RegionA$suffix')].{n:name}",'-o','tsv') `
        $false "RegionA$suffix"
    Test-Az 'REAL: both SG siblings exist (list RegionB)' `
        @('resource','list','-g',$rgSG,'--query',"[?contains(name, 'RegionB$suffix')].{n:name}",'-o','tsv') `
        $false "RegionB$suffix"

    Remove-Item $sgYaml -ErrorAction SilentlyContinue
}
finally {
    Write-Host ""
    Write-Host "Cleanup: deleting RGs in background..." -ForegroundColor DarkGray
    az group delete -n $rgRG --yes --no-wait 2>&1 | Out-Null
    az group delete -n $rgSG --yes --no-wait 2>&1 | Out-Null
    # Best-effort cleanup of created ServiceGroups (at tenant scope, survive RG deletion)
    foreach ($sgName in @("Country$suffix","RegionA$suffix","RegionB$suffix")) {
        $sgId = "/providers/Microsoft.Management/serviceGroups/$sgName"
        az rest --method delete --url "https://management.azure.com$($sgId)?api-version=2024-02-01-preview" 2>&1 | Out-Null
    }
}

# =================================================================
# Summary
# =================================================================
Write-Host ""
Write-Host "================================================================"
Write-Host "Total: $($pass + $fail)  Passed: $pass  Failed: $fail" -ForegroundColor $(if ($fail -eq 0) {'Green'} else {'Red'})
Write-Host "================================================================"
$results | Format-Table -AutoSize -Wrap
exit $fail
