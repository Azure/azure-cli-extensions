$ENVCONFIG = Get-Content -Path $PSScriptRoot/../../settings.json | ConvertFrom-Json

$MAX_RETRY_ATTEMPTS = 30
$ARC_LOCATION = "uksouth"
$SUCCEEDED = "Succeeded"