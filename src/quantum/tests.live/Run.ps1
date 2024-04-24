# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

param (
    [Parameter()]
    [switch]
    $SkipInstall=$False
)

$RecordingsFolderPath = "src\quantum\azext_quantum\tests\latest\recordings"

function Invoke-SASTokenObfuscation {
    param (
        [Parameter(mandatory=$true)]
        $RecordingsFolderPath
    )
    
    Get-ChildItem "$RecordingsFolderPath" -Filter *.yaml | 
    Foreach-Object {
        $RecordingFileName = $_.Name
        $PathToRecording = "$RecordingsFolderPath\$RecordingFileName"
        Write-Verbose -Message "Searching for SAS Tokens in ""$PathToRecording"" and obfuscating it..."
        # Signature "sig=" query parameter consists of URL-encoded Base64 characters, so [\w%] should suffice
        (Get-Content $PathToRecording) -replace 'sig=[\w%]+(&|$)','sig=REDACTED$1' | Set-Content $PathToRecording
    }
}

# For debug, print all relevant environment variables:
Get-ChildItem env:AZURE*, env:*VERSION, env:*OUTDIR | Format-Table | Out-String | Write-Host

# Remembering current folder location
Push-Location .

# Run the Quantum CLI Extension tests in an azdev environment
Set-Location $PSScriptRoot/../../..
python -m venv env
env\Scripts\activate.ps1
python -m pip install -U pip
pip install azdev
azdev setup --repo .
azdev extension add quantum
az account set -s $Env:AZURE_QUANTUM_SUBSCRIPTION_ID
azdev test quantum --live --verbose --xml-path $RecordingsFolderPath

# Make sure we don't check-in SAS-tokens
Invoke-SASTokenObfuscation -RecordingsFolderPath $RecordingsFolderPath

# Restoring to initial folder location
Pop-Location