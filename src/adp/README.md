# Azure CLI adp Extension #
This is the extension for adp

### How to use ###
Install this extension using the below CLI command
```
az extension add --name adp
```

### Included Features ###
#### adp account ####
##### Create #####
```
az adp account create --name "sampleacct" --location "Global" --resource-group "adpClient"

az adp account wait --created --name "{myAccount}" --resource-group "{rg}"
```
##### Show #####
```
az adp account show --name "sampleacct" --resource-group "adpClient"
```
##### List #####
```
az adp account list --resource-group "adpClient"
```
##### Update #####
```
az adp account update --name "sampleacct" --resource-group "adpClient"
```
##### Delete #####
```
az adp account delete --name "sampleacct" --resource-group "adpClient"
```
#### adp data-pool ####
##### Create #####
```
az adp data-pool create --account-name "sampleacct" --name "sampledp" --locations name="westus" \
    --resource-group "adpClient" 

az adp data-pool wait --created --name "{myDataPool}" --resource-group "{rg}"
```
##### Show #####
```
az adp data-pool show --account-name "sampleacct" --name "sampledp" --resource-group "adpClient"
```
##### List #####
```
az adp data-pool list --account-name "sampleacct" --resource-group "adpClient"
```
##### Update #####
```
az adp data-pool update --account-name "sampleacct" --name "sampledp" --locations name="westus" \
    --resource-group "adpClient" 
```
##### Delete #####
```
az adp data-pool delete --account-name "sampleacct" --name "sampledp" --resource-group "adpClient"
```