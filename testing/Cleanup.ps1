param (
    [switch] $CI
)

# Disable confirm prompt for script
az config set core.disable_confirm_prompt=true

$ENVCONFIG = Get-Content -Path $PSScriptRoot/settings.json | ConvertFrom-Json

az account set --subscription $ENVCONFIG.subscriptionId

$Env:KUBECONFIG="$PSScriptRoot/tmp/KUBECONFIG"
Write-Host "Removing the connectedk8s arc agents from the cluster..."
az connectedk8s delete -g $ENVCONFIG.resourceGroup -n $ENVCONFIG.arcClusterName

# Skip deleting the AKS Cluster if this is CI
if (!$CI) {
    Write-Host "Deleting the AKS cluster from Azure..."
    az aks delete -g $ENVCONFIG.resourceGroup -n $ENVCONFIG.aksClusterName
    if (Test-Path -Path $PSScriptRoot/tmp) {
        Write-Host "Deleting the tmp directory from the test directory"
        Remove-Item -Path $PSScriptRoot/tmp -Force -Confirm:$false
    }
}