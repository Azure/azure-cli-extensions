# Azure CLI connectedmachine Extension #
This is the extension for connectedmachine

### How to use ###
Install this extension using the below CLI command
```
az extension add --name connectedmachine
```

### Included Features ###
#### connectedmachine ####
##### List #####
```
az connectedmachine list --resource-group "myResourceGroup"
```
##### Show #####
```
az connectedmachine show --name "myMachine" --resource-group "myResourceGroup"
```
##### Delete #####
```
az connectedmachine delete --name "myMachine" --resource-group "myResourceGroup"
```
#### connectedmachine extension ####
##### Create #####
```
az connectedmachine extension create --n "CustomScriptExtension" --location "eastus2euap" \
    --type "CustomScriptExtension" --publisher "Microsoft.Compute" \
    --settings "{\\"commandToExecute\\":\\"powershell.exe -c \\\\\\"Get-Process | Where-Object { $_.CPU -gt 10000 }\\\\\\"\\"}" \
    --type-handler-version "1.10" --machine-name "myMachine" --resource-group "myResourceGroup" 
```
##### Show #####
```
az connectedmachine extension show --n "CustomScriptExtension" --machine-name "myMachine" \
    --resource-group "myResourceGroup" 
```
##### List #####
```
az connectedmachine extension list --machine-name "myMachine" --resource-group "myResourceGroup"
```
##### Update #####
```
az connectedmachine extension update --n "CustomScriptExtension" --type "CustomScriptExtension" \
    --publisher "Microsoft.Compute" \
    --settings "{\\"commandToExecute\\":\\"powershell.exe -c \\\\\\"Get-Process | Where-Object { $_.CPU -lt 100 }\\\\\\"\\"}" \
    --type-handler-version "1.10" --machine-name "myMachine" --resource-group "myResourceGroup" 
```
##### Delete #####
```
az connectedmachine extension delete --n "MMA" --machine-name "myMachine" --resource-group "myResourceGroup"
```
#### connectedmachine ####
##### Upgrade-extension #####
```
az connectedmachine upgrade-extension \
    --extension-targets "{\\"Microsoft.Azure.Monitoring\\":{\\"targetVersion\\":\\"2.0\\"},\\"Microsoft.Compute.CustomScriptExtension\\":{\\"targetVersion\\":\\"1.10\\"}}" \
    --machine-name "myMachine" --resource-group "myResourceGroup" 
```
#### connectedmachine private-link-scope ####
##### Create #####
```
az connectedmachine private-link-scope create --location "westus" --resource-group "my-resource-group" \
    --scope-name "my-privatelinkscope" 
```
##### Update #####
```
az connectedmachine private-link-scope update --location "westus" --tags Tag1="Value1" \
    --resource-group "my-resource-group" --scope-name "my-privatelinkscope" 
```
##### List #####
```
az connectedmachine private-link-scope list --resource-group "my-resource-group"
```
##### Show #####
```
az connectedmachine private-link-scope show --resource-group "my-resource-group" --scope-name "my-privatelinkscope"
```
##### Update-tag #####
```
az connectedmachine private-link-scope update-tag --tags Tag1="Value1" Tag2="Value2" \
    --resource-group "my-resource-group" --scope-name "my-privatelinkscope" 
```
##### Delete #####
```
az connectedmachine private-link-scope delete --resource-group "my-resource-group" --scope-name "my-privatelinkscope"
```
#### connectedmachine private-link-resource ####
##### List #####
```
az connectedmachine private-link-resource list --resource-group "myResourceGroup" --scope-name "myPrivateLinkScope"
```
##### Show #####
```
az connectedmachine private-link-resource show --group-name "hybridcompute" --resource-group "myResourceGroup" \
    --scope-name "myPrivateLinkScope" 
```
#### connectedmachine private-endpoint-connection ####
##### Update #####
```
az connectedmachine private-endpoint-connection update \
    --private-link-service-connection-state description="Approved by johndoe@contoso.com" status="Approved" \
    --name "private-endpoint-connection-name" --resource-group "myResourceGroup" --scope-name "myPrivateLinkScope" 
```
##### Show #####
```
az connectedmachine private-endpoint-connection show --name "private-endpoint-connection-name" \
    --resource-group "myResourceGroup" --scope-name "myPrivateLinkScope" 
```
##### List #####
```
az connectedmachine private-endpoint-connection list --resource-group "myResourceGroup" \
    --scope-name "myPrivateLinkScope" 
```
##### Delete #####
```
az connectedmachine private-endpoint-connection delete --name "private-endpoint-connection-name" \
    --resource-group "myResourceGroup" --scope-name "myPrivateLinkScope" 
```