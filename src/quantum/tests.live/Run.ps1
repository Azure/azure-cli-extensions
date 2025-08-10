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
        (Get-Content $PathToRecording) -replace 'sig=[\w%]+','sig=REDACTED' | Set-Content $PathToRecording
    }
}

function Invoke-APIKeyObfuscation {
    param (
        [Parameter(mandatory=$true)]
        $RecordingsFolderPath
    )

    Get-ChildItem "$RecordingsFolderPath" -Filter *.yaml | 
    Foreach-Object {
        $RecordingFileName = $_.Name
        $PathToRecording = "$RecordingsFolderPath\$RecordingFileName"
        Write-Verbose -Message "Searching for API Keys in ""$PathToRecording"" and obfuscating it..."
        (Get-Content $PathToRecording) -replace 'api_key=[\w%\-+=/_]+','api_key=REDACTED' | Set-Content $PathToRecording
    }
}

function Invoke-QuantumWorkspaceDataObfuscation {
    param (
        [Parameter(mandatory=$true)]
        $RecordingsFolderPath
    )

    Get-ChildItem "$RecordingsFolderPath" -Filter *.yaml | 
    Foreach-Object {
        $RecordingFileName = $_.Name
        $PathToRecording = "$RecordingsFolderPath\$RecordingFileName"
        Write-Host "Starting obfuscation of sensitive fields in recording file: $PathToRecording"

        # Read full content
        $content = Get-Content $PathToRecording -Raw
        Write-Host "Loaded file content."

        # Obfuscate primaryKey and secondaryKey inside JSON strings
        $content = $content -replace '"primaryKey"\s*:\s*\{[^}]*"key"\s*:\s*"[^"]+"', '"primaryKey":{"key":"REDACTED"'
        Write-Host "Obfuscated 'primaryKey'."

        $content = $content -replace '"secondaryKey"\s*:\s*\{[^}]*"key"\s*:\s*"[^"]+"', '"secondaryKey":{"key":"REDACTED"'
        Write-Host "Obfuscated 'secondaryKey'."

        # Obfuscate primary and secondary connection strings
        $connectionPattern = '"(primary|secondary)ConnectionString"\s*:\s*"SubscriptionId=[^;]+;ResourceGroupName=[^;]+;WorkspaceName=[^;]+;ApiKey=[^;]+;QuantumEndpoint=[^"]+"'
        $replacementConnection = '"$1ConnectionString":"SubscriptionId=REDACTED;ResourceGroupName=REDACTED;WorkspaceName=REDACTED;ApiKey=REDACTED;QuantumEndpoint=REDACTED"'
        $content = $content -replace $connectionPattern, $replacementConnection
        Write-Host "Obfuscated primary and secondary connection strings."

        # Obfuscate standalone ApiKey
        $content = $content -replace 'ApiKey=[\w\-+=/_]+;', 'ApiKey=REDACTED;'
        Write-Host "Obfuscated standalone ApiKey values."

        # Obfuscate apiKeyEnabled boolean
        $content = $content -replace '"apiKeyEnabled"\s*:\s*(true|false)', '"apiKeyEnabled":REDACTED'
        Write-Host "Obfuscated 'apiKeyEnabled' values."

        # Obfuscate resourceName
        $content = $content -replace '"resourceName"\s*:\s*"[^"]+"', '"resourceName":"REDACTED"'
        Write-Host "Obfuscated 'resourceName' values."

        # Obfuscate quantumWorkspaceName
        $content = $content -replace '"quantumWorkspaceName"\s*:\s*\{\s*"type"\s*:\s*"String",\s*"value"\s*:\s*"[^"]+"\s*\}', '"quantumWorkspaceName":{"type":"String","value":"REDACTED"}'
        Write-Host "Obfuscated 'quantumWorkspaceName'."

        # Obfuscate location and storageAccountLocation
        $content = $content -replace '"(location|storageAccountLocation)"\s*:\s*\{\s*"type"\s*:\s*"String",\s*"value"\s*:\s*"[^"]+"\s*\}', '"$1":{"type":"String","value":"REDACTED"}'
        Write-Host "Obfuscated 'location' and 'storageAccountLocation'."

        # Obfuscate workspaceName in connection strings
        $content = $content -replace 'WorkspaceName=[^;]+;', 'WorkspaceName=REDACTED;'
        Write-Host "Obfuscated 'WorkspaceName' in connection strings."

        # Obfuscate Set-Cookie headers
        $content = $content -replace 'ApplicationGatewayAffinityCORS=[\w-]+;', 'ApplicationGatewayAffinityCORS=REDACTED;'
        $content = $content -replace 'ApplicationGatewayAffinity=[\w-]+;', 'ApplicationGatewayAffinity=REDACTED;'
        $content = $content -replace 'ARRAffinity=[\w-]+;', 'ARRAffinity=REDACTED;'
        $content = $content -replace 'ARRAffinitySameSite=[\w-]+;', 'ARRAffinitySameSite=REDACTED;'
        Write-Host "Obfuscated sensitive Set-Cookie headers."

        # Save the modified content
        Set-Content -Path $PathToRecording -Value $content
        Write-Host "Finished obfuscation. Changes saved to: $PathToRecording"
    }
}

# For debug, print all relevant environment variables:
Get-ChildItem env:AZURE*, env:*VERSION, env:*OUTDIR | ForEach-Object {
    Write-Host $_.Name "=" $_.Value
}

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

# Make sure we don't check-in API keys, Connection strings and quantum workspace data
Invoke-QuantumWorkspaceDataObfuscation -RecordingsFolderPath $RecordingsFolderPath

# Restoring to initial folder location
Pop-Location
