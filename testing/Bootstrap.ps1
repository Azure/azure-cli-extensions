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

az group show --name $envConfig.resourceGroup
if (!$?) {
    Write-Host "Resource group does not exist, creating it now in region 'eastus2euap'"
    az group create --name $envConfig.resourceGroup --location eastus2euap

    if (!$?) {
        Write-Host "Failed to create Resource Group - exiting!"
        Exit 1
    }
}


Copy-Item $HOME/.kube/config -Destination $PSScriptRoot/tmp/KUBECONFIG 