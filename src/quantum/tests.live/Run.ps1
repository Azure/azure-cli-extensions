# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
param (
    [Parameter()]
    [switch]
    $SkipInstall=$False
)

# For debug, print all relevant environment variables:
Get-ChildItem env:AZURE*, env:*VERSION, env:*OUTDIR | Format-Table | Out-String | Write-Host

# Run the Quantum CLI Extension tests in an azdev environment
python -m venv env
env\Scripts\activate.ps1
python -m pip install -U pip
pip install azdev
azdev setup --cli /a/1/s/src/subrepos/azure_cli --repo /a/1/s/src/subrepos/cli_extension
azdev extension add quantum
az account set -s 916dfd6d-030c-4bd9-b579-7bb6d1926e97
azdev test quantum --live
