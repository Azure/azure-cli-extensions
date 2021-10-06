# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
param (
    [Parameter()]
    [switch]
    $SkipInstall=$False
)

# For debug, print all relevant environment variables:
Get-ChildItem env:AZURE*, env:*VERSION, env:*OUTDIR | Format-Table | Out-String | Write-Host

<# >>>>> Code from IQ# Run.ps1 script: The CLI Extension tests probably won't use Pester <<<<<
# Install and run Pester
Import-Module Pester

$config = [PesterConfiguration]::Default
$config.Run.Exit = $true
$config.TestResult.Enabled = $true
$config.TestResult.OutputPath = "TestResults.xml"
$config.TestResult.OutputFormat = "JUnitXml"
$config.Output.Verbosity = "Detailed"

Invoke-Pester -Configuration $config -Verbose 
<<<<< #>

# Run the Quantum CLI Extension tests in an azdev environment
env\Scripts\activate.ps1
azdev extension add quantum
az account set -s 916dfd6d-030c-4bd9-b579-7bb6d1926e97
azdev test quantum --live
#<<<<< Will this work? <<<<<
#<<<<< What about the Azure login? Does that happen somewhere else? <<<<<