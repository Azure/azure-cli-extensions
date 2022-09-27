$ENVCONFIG = Get-Content -Path $PSScriptRoot/../../settings.json | ConvertFrom-Json
$SUCCESS_MESSAGE = "Successfully installed the extension"
$FAILED_MESSAGE = "Failed to install the extension"

$POD_RUNNING = "Running"

$MAX_RETRY_ATTEMPTS = 10