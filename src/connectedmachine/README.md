# Microsoft Azure CLI 'connectedmachine' Extension

This package is for the 'connectedmachine' extension, i.e. 'az connectedmachine'.

## Prerequisite

In order to use this extension,
first follow the quick start for
[Hybrid Compute](https://docs.microsoft.com/en-us/azure/azure-arc/servers/learn/quick-enable-hybrid-vm)
and onboard your machine(s).

## How to use

Install this extension using the below CLI command

```sh
az extension add --name connectedmachine
```

### Included Features

#### Connected Machine Management

*Examples:*

##### Show connected machine

```sh
az connectedmachine show \
    --subscription subscription_id \
    --resource-group my-rg \
    --name my-cluster
```

##### List connected machines in resource group

```sh
az connectedmachine list --resource-group my-rg
```

##### Delete a connected machine

```sh
az connectedmachine delete \
    --subscription subscription_id \
    --resource-group my-rg \
    --name my-machine
```

#### Connected Machine Extension Management

*Examples:*

##### Create or Update a Machine Extension

```sh
az connectedmachine extension create \
    --machine-name "myMachine" \
    --name "customScriptExtension" \
    --location "eastus2euap" \
    --type "CustomScriptExtension" \
    --publisher "Microsoft.Compute" \
    --settings "{\"commandToExecute\":\"powershell.exe -c \\\"Get-Process | Where-Object { $_.CPU -gt 10000 }\\\"\"}" \
    --type-handler-version "1.10" \
    --resource-group "myResourceGroup"
```

##### Get all Machine Extensions

```sh
az connectedmachine extension list \
    --machine-name "myMachine" \
    --resource-group "myResourceGroup"
```

##### Get a Machine Extension

```sh
az connectedmachine extension show \
    --machine-name "myMachine" \
    --name "CustomScriptExtension" \
    --resource-group "myResourceGroup"
```

##### Update a Machine Extension

```sh
az connectedmachine extension update \
    --machine-name "myMachine" \
    --name "CustomScriptExtension" \
    --type "CustomScriptExtension" \
    --publisher "Microsoft.Compute" \
    --settings "{\"commandToExecute\":\"powershell.exe -c \\\"Get-Process | Where-Object { $_.CPU -lt 100 }\\\"\"}" \ --type-handler-version "1.10" \
    --resource-group "myResourceGroup"
```

##### Delete a Machine Extension

```sh
az connectedmachine extension delete \
    --machine-name "myMachine" \
    --name "MMA" \
    --resource-group "myResourceGroup"
```
