# Azure CLI dnc Extension #
This is the extension for dnc

### How to use ###
Install this extension using the below CLI command
```
az extension add --name dnc
```

### Included Features ###
#### dnc controller ####
##### Create #####
```
az dnc controller create --location "eastus2euap" --resource-group "TestRG" --resource-name "testcontroller"
```
##### Patch #####
```
az dnc controller patch --tags key="value" --resource-group "TestRG" --resource-name "testcontroller"
```
##### Show-detail #####
```
az dnc controller show-detail --resource-group "TestRG" --resource-name "testcontroller"
```
##### Delete #####
```
az dnc controller delete --resource-group "TestRG" --resource-name "testcontroller"
```
#### dnc delegated-network ####
##### List #####
```
az dnc delegated-network list --resource-group "testRG"
```
#### dnc orchestrator-instance-service ####
##### Create #####
```
az dnc orchestrator-instance-service create --type "SystemAssigned" --location "eastus2euap" \
    --api-server-endpoint "https://testk8s.cloudapp.net" --cluster-root-ca "ddsadsad344mfdsfdl" \
    --id "/subscriptions/613192d7-503f-477a-9cfe-4efc3ee2bd60/resourceGroups/TestRG/providers/Microsoft.DelegatedNetwork/controller/testcontroller" \
    --orchestrator-app-id "546192d7-503f-477a-9cfe-4efc3ee2b6e1" \
    --orchestrator-tenant-id "da6192d7-503f-477a-9cfe-4efc3ee2b6c3" \
    --private-link-resource-id "/subscriptions/613192d7-503f-477a-9cfe-4efc3ee2bd60/resourceGroups/TestRG/providers/Microsoft.Network/privateLinkServices/plresource1" \
    --resource-group "TestRG" --resource-name "testk8s1" 
```
##### List #####
```
az dnc orchestrator-instance-service list --resource-group "testRG"
```
##### Patch #####
```
az dnc orchestrator-instance-service patch --tags key="value" --resource-group "TestRG" --resource-name "testk8s1"
```
##### Show-detail #####
```
az dnc orchestrator-instance-service show-detail --resource-group "TestRG" --resource-name "testk8s1"
```
##### Delete #####
```
az dnc orchestrator-instance-service delete --resource-group "TestRG" --resource-name "k8stest1"
```
#### dnc delegated-subnet-service ####
##### Put-detail #####
```
az dnc delegated-subnet-service put-detail --location "eastus2euap" \
    --id "/subscriptions/613192d7-503f-477a-9cfe-4efc3ee2bd60/resourceGroups/TestRG/providers/Microsoft.DelegatedNetwork/controller/dnctestcontroller" \
    --subnet-details-id "/subscriptions/613192d7-503f-477a-9cfe-4efc3ee2bd60/resourceGroups/TestRG/providers/Microsoft.Network/virtualNetworks/testvnet/subnets/testsubnet" \
    --resource-group "TestRG" --resource-name "delegated1" 
```
##### Patch-detail #####
```
az dnc delegated-subnet-service patch-detail --tags key="value" --resource-group "TestRG" --resource-name "delegated1"
```
##### List #####
```
az dnc delegated-subnet-service list --resource-group "testRG"
```
##### Show-detail #####
```
az dnc delegated-subnet-service show-detail --resource-group "TestRG" --resource-name "delegated1"
```
##### Delete #####
```
az dnc delegated-subnet-service delete --resource-group "TestRG" --resource-name "delegated1"
```