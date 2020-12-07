# Azure CLI machinelearningservices Extension #
This is the extension for machinelearningservices

### How to use ###
Install this extension using the below CLI command
```
az extension add --name machinelearningservices
```

### Included Features ###
#### machinelearningservices workspace ####
##### Create #####
```
az machinelearningservices workspace create --identity-type "SystemAssigned" --location "eastus2euap" \
    --description "test description" \
    --application-insights "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/workspace-1234/providers/microsoft.insights/components/testinsights" \
    --container-registry "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/workspace-1234/providers/Microsoft.ContainerRegistry/registries/testRegistry" \
    --friendly-name "HelloName" --hbi-workspace false \
    --key-vault "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/workspace-1234/providers/Microsoft.KeyVault/vaults/testkv" \
    --shared-private-link-resources name="testdbresource" private-link-resource-id="/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/workspace-1234/providers/Microsoft.DocumentDB/databaseAccounts/testdbresource/privateLinkResources/Sql" group-id="Sql" request-message="Please approve" status="Approved" \
    --storage-account "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/accountcrud-1234/providers/Microsoft.Storage/storageAccounts/testStorageAccount" \
    --sku name="Basic" tier="Basic" --resource-group "workspace-1234" --name "testworkspace" 

az machinelearningservices workspace wait --created --resource-group "{rg}" --name "{myWorkspace}"
```
##### Show #####
```
az machinelearningservices workspace show --resource-group "workspace-1234" --name "testworkspace"
```
##### List #####
```
az machinelearningservices workspace list --resource-group "workspace-1234"
```
##### Update #####
```
az machinelearningservices workspace update --description "new description" --friendly-name "New friendly name" \
    --sku name="Enterprise" tier="Enterprise" --resource-group "workspace-1234" --name "testworkspace" 
```
##### List-key #####
```
az machinelearningservices workspace list-key --resource-group "testrg123" --name "workspaces123"
```
##### Resync-key #####
```
az machinelearningservices workspace resync-key --resource-group "testrg123" --name "workspaces123"
```
##### Delete #####
```
az machinelearningservices workspace delete --resource-group "workspace-1234" --name "testworkspace"
```
#### machinelearningservices workspace-feature ####
##### List #####
```
az machinelearningservices workspace-feature list --resource-group "myResourceGroup" --workspace-name "testworkspace"
```
#### machinelearningservices notebook ####
##### Prepare #####
```
az machinelearningservices notebook prepare --resource-group "testrg123" --workspace-name "workspaces123"
```
#### machinelearningservices usage ####
##### List #####
```
az machinelearningservices usage list --location "eastus"
```
#### machinelearningservices virtual-machine-size ####
##### List #####
```
az machinelearningservices virtual-machine-size list --location "eastus" --recommended false
```
#### machinelearningservices quota ####
##### List #####
```
az machinelearningservices quota list --location "eastus"
```
##### Update #####
```
az machinelearningservices quota update --location "eastus" \
    --value type="Microsoft.MachineLearningServices/workspaces/dedicatedCores/quotas" id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/Microsoft.MachineLearningServices/workspaces/demo_workspace1/quotas/StandardDSv2Family" limit=100 unit="Count" \
    --value type="Microsoft.MachineLearningServices/workspaces/dedicatedCores/quotas" id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/Microsoft.MachineLearningServices/workspaces/demo_workspace2/quotas/StandardDSv2Family" limit=200 unit="Count" 
```
#### machinelearningservices workspace-connection ####
##### Create #####
```
az machinelearningservices workspace-connection create --connection-name "connection-1" --name "connection-1" \
    --auth-type "PAT" --category "ACR" --target "www.facebook.com" --value "secrets" \
    --resource-group "resourceGroup-1" --workspace-name "workspace-1" 
```
##### Show #####
```
az machinelearningservices workspace-connection show --connection-name "connection-1" \
    --resource-group "resourceGroup-1" --workspace-name "workspace-1" 
```
##### List #####
```
az machinelearningservices workspace-connection list --category "ACR" --resource-group "resourceGroup-1" \
    --target "www.facebook.com" --workspace-name "workspace-1" 
```
##### Delete #####
```
az machinelearningservices workspace-connection delete --connection-name "connection-1" \
    --resource-group "resourceGroup-1" --workspace-name "workspace-1" 
```
#### machinelearningservices machine-learning-compute ####
##### Aks create #####
```
az machinelearningservices machine-learning-compute aks create --compute-name "compute123" --location "eastus" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Aks create #####
```
az machinelearningservices machine-learning-compute aks create --compute-name "compute123" \
    --identity-type "SystemAssigned,UserAssigned" \
    --identity-user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/identity-name\\":{}}" \
    --location "eastus" \
    --ak-s-properties "{\\"remoteLoginPortPublicAccess\\":\\"NotSpecified\\",\\"scaleSettings\\":{\\"maxNodeCount\\":1,\\"minNodeCount\\":0,\\"nodeIdleTimeBeforeScaleDown\\":\\"PT5M\\"},\\"vmPriority\\":\\"Dedicated\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Aks create #####
```
az machinelearningservices machine-learning-compute aks create --compute-name "compute123" --location "eastus" \
    --ak-s-properties "{\\"applicationSharingPolicy\\":\\"Personal\\",\\"sshSettings\\":{\\"sshPublicAccess\\":\\"Disabled\\"},\\"subnet\\":\\"test-subnet-resource-id\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Aks create #####
```
az machinelearningservices machine-learning-compute aks create --compute-name "compute123" --location "eastus" \
    --ak-s-properties "{\\"vmSize\\":\\"STANDARD_NC6\\"}" --resource-group "testrg123" \
    --workspace-name "workspaces123" 
```
##### Aks create #####
```
az machinelearningservices machine-learning-compute aks create --compute-name "compute123" --location "eastus" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Aks create #####
```
az machinelearningservices machine-learning-compute aks create --compute-name "compute123" --location "eastus" \
    --ak-s-description "some compute" --ak-s-properties "{\\"agentCount\\":4}" \
    --ak-s-resource-id "/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourcegroups/testrg123/providers/Microsoft.ContainerService/managedClusters/compute123-56826-c9b00420020b2" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Aks create #####
```
az machinelearningservices machine-learning-compute aks create --compute-name "compute123" \
    --identity-type "SystemAssigned,UserAssigned" \
    --identity-user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/identity-name\\":{}}" \
    --location "eastus" \
    --ak-s-properties "{\\"scaleSettings\\":{\\"maxNodeCount\\":1,\\"minNodeCount\\":0,\\"nodeIdleTimeBeforeScaleDown\\":\\"PT5M\\"}}" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Aml-compute create #####
```
az machinelearningservices machine-learning-compute aml-compute create --compute-name "compute123" --location "eastus" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Aml-compute create #####
```
az machinelearningservices machine-learning-compute aml-compute create --compute-name "compute123" \
    --identity-type "SystemAssigned,UserAssigned" \
    --identity-user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/identity-name\\":{}}" \
    --location "eastus" \
    --aml-compute-properties "{\\"remoteLoginPortPublicAccess\\":\\"NotSpecified\\",\\"scaleSettings\\":{\\"maxNodeCount\\":1,\\"minNodeCount\\":0,\\"nodeIdleTimeBeforeScaleDown\\":\\"PT5M\\"},\\"vmPriority\\":\\"Dedicated\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Aml-compute create #####
```
az machinelearningservices machine-learning-compute aml-compute create --compute-name "compute123" --location "eastus" \
    --aml-compute-properties "{\\"applicationSharingPolicy\\":\\"Personal\\",\\"sshSettings\\":{\\"sshPublicAccess\\":\\"Disabled\\"},\\"subnet\\":\\"test-subnet-resource-id\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Aml-compute create #####
```
az machinelearningservices machine-learning-compute aml-compute create --compute-name "compute123" --location "eastus" \
    --aml-compute-properties "{\\"vmSize\\":\\"STANDARD_NC6\\"}" --resource-group "testrg123" \
    --workspace-name "workspaces123" 
```
##### Aml-compute create #####
```
az machinelearningservices machine-learning-compute aml-compute create --compute-name "compute123" --location "eastus" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Aml-compute create #####
```
az machinelearningservices machine-learning-compute aml-compute create --compute-name "compute123" --location "eastus" \
    --description "some compute" --aml-compute-properties "{\\"agentCount\\":4}" \
    --resource-id "/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourcegroups/testrg123/providers/Microsoft.ContainerService/managedClusters/compute123-56826-c9b00420020b2" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Aml-compute create #####
```
az machinelearningservices machine-learning-compute aml-compute create --compute-name "compute123" \
    --identity-type "SystemAssigned,UserAssigned" \
    --identity-user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/identity-name\\":{}}" \
    --location "eastus" \
    --aml-compute-properties "{\\"scaleSettings\\":{\\"maxNodeCount\\":1,\\"minNodeCount\\":0,\\"nodeIdleTimeBeforeScaleDown\\":\\"PT5M\\"}}" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Compute-instance create #####
```
az machinelearningservices machine-learning-compute compute-instance create --compute-name "compute123" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Compute-instance create #####
```
az machinelearningservices machine-learning-compute compute-instance create --compute-name "compute123" \
    --identity-type "SystemAssigned,UserAssigned" \
    --identity-user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/identity-name\\":{}}" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Compute-instance create #####
```
az machinelearningservices machine-learning-compute compute-instance create --compute-name "compute123" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Compute-instance create #####
```
az machinelearningservices machine-learning-compute compute-instance create --compute-name "compute123" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Compute-instance create #####
```
az machinelearningservices machine-learning-compute compute-instance create --compute-name "compute123" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Compute-instance create #####
```
az machinelearningservices machine-learning-compute compute-instance create --compute-name "compute123" \
    --location "eastus" --description "some compute" \
    --resource-id "/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourcegroups/testrg123/providers/Microsoft.ContainerService/managedClusters/compute123-56826-c9b00420020b2" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Compute-instance create #####
```
az machinelearningservices machine-learning-compute compute-instance create --compute-name "compute123" \
    --identity-type "SystemAssigned,UserAssigned" \
    --identity-user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/identity-name\\":{}}" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Data-factory create #####
```
az machinelearningservices machine-learning-compute data-factory create --compute-name "compute123" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Data-factory create #####
```
az machinelearningservices machine-learning-compute data-factory create --compute-name "compute123" \
    --identity-type "SystemAssigned,UserAssigned" \
    --identity-user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/identity-name\\":{}}" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Data-factory create #####
```
az machinelearningservices machine-learning-compute data-factory create --compute-name "compute123" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Data-factory create #####
```
az machinelearningservices machine-learning-compute data-factory create --compute-name "compute123" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Data-factory create #####
```
az machinelearningservices machine-learning-compute data-factory create --compute-name "compute123" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Data-factory create #####
```
az machinelearningservices machine-learning-compute data-factory create --compute-name "compute123" \
    --location "eastus" --description "some compute" \
    --resource-id "/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourcegroups/testrg123/providers/Microsoft.ContainerService/managedClusters/compute123-56826-c9b00420020b2" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Data-factory create #####
```
az machinelearningservices machine-learning-compute data-factory create --compute-name "compute123" \
    --identity-type "SystemAssigned,UserAssigned" \
    --identity-user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/identity-name\\":{}}" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Data-lake-analytics create #####
```
az machinelearningservices machine-learning-compute data-lake-analytics create --compute-name "compute123" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Data-lake-analytics create #####
```
az machinelearningservices machine-learning-compute data-lake-analytics create --compute-name "compute123" \
    --identity-type "SystemAssigned,UserAssigned" \
    --identity-user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/identity-name\\":{}}" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Data-lake-analytics create #####
```
az machinelearningservices machine-learning-compute data-lake-analytics create --compute-name "compute123" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Data-lake-analytics create #####
```
az machinelearningservices machine-learning-compute data-lake-analytics create --compute-name "compute123" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Data-lake-analytics create #####
```
az machinelearningservices machine-learning-compute data-lake-analytics create --compute-name "compute123" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Data-lake-analytics create #####
```
az machinelearningservices machine-learning-compute data-lake-analytics create --compute-name "compute123" \
    --location "eastus" --description "some compute" \
    --resource-id "/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourcegroups/testrg123/providers/Microsoft.ContainerService/managedClusters/compute123-56826-c9b00420020b2" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Data-lake-analytics create #####
```
az machinelearningservices machine-learning-compute data-lake-analytics create --compute-name "compute123" \
    --identity-type "SystemAssigned,UserAssigned" \
    --identity-user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/identity-name\\":{}}" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Databricks create #####
```
az machinelearningservices machine-learning-compute databricks create --compute-name "compute123" --location "eastus" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Databricks create #####
```
az machinelearningservices machine-learning-compute databricks create --compute-name "compute123" \
    --identity-type "SystemAssigned,UserAssigned" \
    --identity-user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/identity-name\\":{}}" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Databricks create #####
```
az machinelearningservices machine-learning-compute databricks create --compute-name "compute123" --location "eastus" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Databricks create #####
```
az machinelearningservices machine-learning-compute databricks create --compute-name "compute123" --location "eastus" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Databricks create #####
```
az machinelearningservices machine-learning-compute databricks create --compute-name "compute123" --location "eastus" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Databricks create #####
```
az machinelearningservices machine-learning-compute databricks create --compute-name "compute123" --location "eastus" \
    --description "some compute" \
    --resource-id "/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourcegroups/testrg123/providers/Microsoft.ContainerService/managedClusters/compute123-56826-c9b00420020b2" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Databricks create #####
```
az machinelearningservices machine-learning-compute databricks create --compute-name "compute123" \
    --identity-type "SystemAssigned,UserAssigned" \
    --identity-user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/identity-name\\":{}}" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Hd-insight create #####
```
az machinelearningservices machine-learning-compute hd-insight create --compute-name "compute123" --location "eastus" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Hd-insight create #####
```
az machinelearningservices machine-learning-compute hd-insight create --compute-name "compute123" \
    --identity-type "SystemAssigned,UserAssigned" \
    --identity-user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/identity-name\\":{}}" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Hd-insight create #####
```
az machinelearningservices machine-learning-compute hd-insight create --compute-name "compute123" --location "eastus" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Hd-insight create #####
```
az machinelearningservices machine-learning-compute hd-insight create --compute-name "compute123" --location "eastus" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Hd-insight create #####
```
az machinelearningservices machine-learning-compute hd-insight create --compute-name "compute123" --location "eastus" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Hd-insight create #####
```
az machinelearningservices machine-learning-compute hd-insight create --compute-name "compute123" --location "eastus" \
    --description "some compute" \
    --resource-id "/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourcegroups/testrg123/providers/Microsoft.ContainerService/managedClusters/compute123-56826-c9b00420020b2" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Hd-insight create #####
```
az machinelearningservices machine-learning-compute hd-insight create --compute-name "compute123" \
    --identity-type "SystemAssigned,UserAssigned" \
    --identity-user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/identity-name\\":{}}" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Virtual-machine create #####
```
az machinelearningservices machine-learning-compute virtual-machine create --compute-name "compute123" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Virtual-machine create #####
```
az machinelearningservices machine-learning-compute virtual-machine create --compute-name "compute123" \
    --identity-type "SystemAssigned,UserAssigned" \
    --identity-user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/identity-name\\":{}}" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Virtual-machine create #####
```
az machinelearningservices machine-learning-compute virtual-machine create --compute-name "compute123" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Virtual-machine create #####
```
az machinelearningservices machine-learning-compute virtual-machine create --compute-name "compute123" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Virtual-machine create #####
```
az machinelearningservices machine-learning-compute virtual-machine create --compute-name "compute123" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Virtual-machine create #####
```
az machinelearningservices machine-learning-compute virtual-machine create --compute-name "compute123" \
    --location "eastus" --description "some compute" \
    --resource-id "/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourcegroups/testrg123/providers/Microsoft.ContainerService/managedClusters/compute123-56826-c9b00420020b2" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Virtual-machine create #####
```
az machinelearningservices machine-learning-compute virtual-machine create --compute-name "compute123" \
    --identity-type "SystemAssigned,UserAssigned" \
    --identity-user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/identity-name\\":{}}" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### List #####
```
az machinelearningservices machine-learning-compute list --resource-group "testrg123" --workspace-name "workspaces123"
```
##### Show #####
```
az machinelearningservices machine-learning-compute show --compute-name "compute123" --resource-group "testrg123" \
    --workspace-name "workspaces123" 
```
##### Show #####
```
az machinelearningservices machine-learning-compute show --compute-name "compute123" --resource-group "testrg123" \
    --workspace-name "workspaces123" 
```
##### Show #####
```
az machinelearningservices machine-learning-compute show --compute-name "compute123" --resource-group "testrg123" \
    --workspace-name "workspaces123" 
```
##### Update #####
```
az machinelearningservices machine-learning-compute update --compute-name "compute123" \
    --scale-settings max-node-count=4 min-node-count=4 node-idle-time-before-scale-down="PT5M" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### List-key #####
```
az machinelearningservices machine-learning-compute list-key --compute-name "compute123" --resource-group "testrg123" \
    --workspace-name "workspaces123" 
```
##### List-node #####
```
az machinelearningservices machine-learning-compute list-node --compute-name "compute123" --resource-group "testrg123" \
    --workspace-name "workspaces123" 
```
##### Restart #####
```
az machinelearningservices machine-learning-compute restart --compute-name "compute123" --resource-group "testrg123" \
    --workspace-name "workspaces123" 
```
##### Start #####
```
az machinelearningservices machine-learning-compute start --compute-name "compute123" --resource-group "testrg123" \
    --workspace-name "workspaces123" 
```
##### Stop #####
```
az machinelearningservices machine-learning-compute stop --compute-name "compute123" --resource-group "testrg123" \
    --workspace-name "workspaces123" 
```
##### Delete #####
```
az machinelearningservices machine-learning-compute delete --compute-name "compute123" --resource-group "testrg123" \
    --underlying-resource-action "Delete" --workspace-name "workspaces123" 
```
#### machinelearningservices  ####
##### List-sku #####
```
az machinelearningservices  list-sku
```
#### machinelearningservices private-endpoint-connection ####
##### Put #####
```
az machinelearningservices private-endpoint-connection put --name "{privateEndpointConnectionName}" \
    --private-link-service-connection-state description="Auto-Approved" status="Approved" --resource-group "rg-1234" \
    --workspace-name "testworkspace" 
```
##### Show #####
```
az machinelearningservices private-endpoint-connection show --name "{privateEndpointConnectionName}" \
    --resource-group "rg-1234" --workspace-name "testworkspace" 
```
##### Delete #####
```
az machinelearningservices private-endpoint-connection delete --name "{privateEndpointConnectionName}" \
    --resource-group "rg-1234" --workspace-name "testworkspace" 
```
#### machinelearningservices private-link-resource ####
##### List #####
```
az machinelearningservices private-link-resource list --resource-group "rg-1234" --workspace-name "testworkspace"
```