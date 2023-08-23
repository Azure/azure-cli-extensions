param (
    [switch] $SkipInstall,
    [switch] $CI
)

# Disable confirm prompt for script
az config set core.disable_confirm_prompt=true

# Configuring the environment
$ENVCONFIG = Get-Content -Path $PSScriptRoot/settings.json | ConvertFrom-Json

az account set --subscription $ENVCONFIG.subscriptionId

if (-not (Test-Path -Path $PSScriptRoot/tmp)) {
    New-Item -ItemType Directory -Path $PSScriptRoot/tmp
}

if (!$SkipInstall) {
    Write-Host "Removing the old connnectedk8s extension..."
    az extension remove -n connectedk8s
    Write-Host "Installing connectedk8s..."
    az extension add -n connectedk8s
    if (!$?) {
        Write-Host "Unable to install connectedk8s, exiting..."
        exit 1
    }
}

Write-Host "Onboard cluster to Azure...starting!"

az group show --name $envConfig.resourceGroup
if (!$?) {
    Write-Host "Resource group does not exist, creating it now in region 'eastus2euap'"
    az group create --name $envConfig.resourceGroup --location eastus2euap

    if (!$?) {
        Write-Host "Failed to create Resource Group - exiting!"
        Exit 1
    }
}

# Skip creating the AKS Cluster if this is CI
if (!$CI) {
    az aks show -g $ENVCONFIG.resourceGroup -n $ENVCONFIG.aksClusterName
    if (!$?) {
        Write-Host "Cluster does not exist, creating it now"
        az aks create -g $ENVCONFIG.resourceGroup -n $ENVCONFIG.aksClusterName --generate-ssh-keys
    } else {
        Write-Host "Cluster already exists, no need to create it."
    }

    Write-Host "Retrieving credentials for your AKS cluster..."

    az aks get-credentials -g $ENVCONFIG.resourceGroup -n $ENVCONFIG.aksClusterName -f tmp/KUBECONFIG
    if (!$?) 
    {
        Write-Host "Cluster did not create successfully, exiting!" -ForegroundColor Red
        Exit 1
    }
    Write-Host "Successfully retrieved the AKS kubectl credentials"
} else {
    Copy-Item $HOME/.kube/config -Destination $PSScriptRoot/tmp/KUBECONFIG 
}

az connectedk8s show -g $ENVCONFIG.resourceGroup -n $ENVCONFIG.arcClusterName
if ($?)
{
    Write-Host "Cluster is already connected, no need to re-connect"
    Exit 0
}

Write-Host "Connecting the cluster to Arc with connectedk8s..."
$Env:KUBECONFIG="$PSScriptRoot/tmp/KUBECONFIG"
az connectedk8s connect -g $ENVCONFIG.resourceGroup -n $ENVCONFIG.arcClusterName -l westeurope
if (!$?)
{
    kubectl get pods -A
    Exit 1
}
Write-Host "Successfully onboarded the cluster to Azure"