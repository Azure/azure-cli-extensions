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
az machinelearningservices workspace create \
    --identity type="SystemAssigned,UserAssigned" userAssignedIdentities={"/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/workspace-1234/providers/Microsoft.ManagedIdentity/userAssignedIdentities/testuai":{}} \
    --location "eastus2euap" --description "test description" \
    --application-insights "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/workspace-1234/providers/microsoft.insights/components/testinsights" \
    --container-registry "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/workspace-1234/providers/Microsoft.ContainerRegistry/registries/testRegistry" \
    --identity user-assigned-identity="/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/workspace-1234/providers/Microsoft.ManagedIdentity/userAssignedIdentities/testuai" \
    --key-vault-properties identity-client-id="" key-identifier="https://testkv.vault.azure.net/keys/testkey/aabbccddee112233445566778899aabb" key-vault-arm-id="/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/workspace-1234/providers/Microsoft.KeyVault/vaults/testkv" \
    --status "Enabled" --friendly-name "HelloName" --hbi-workspace false \
    --key-vault "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/workspace-1234/providers/Microsoft.KeyVault/vaults/testkv" \
    --shared-private-link-resources name="testdbresource" private-link-resource-id="/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/workspace-1234/providers/Microsoft.DocumentDB/databaseAccounts/testdbresource/privateLinkResources/Sql" group-id="Sql" request-message="Please approve" status="Approved" \
    --storage-account "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/accountcrud-1234/providers/Microsoft.Storage/storageAccounts/testStorageAccount" \
    --resource-group "workspace-1234" --name "testworkspace" 

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
    --resource-group "workspace-1234" --name "testworkspace" 
```
##### List-key #####
```
az machinelearningservices workspace list-key --resource-group "testrg123" --name "workspaces123"
```
##### List-notebook-access-token #####
```
az machinelearningservices workspace list-notebook-access-token --resource-group "workspace-1234" \
    --name "testworkspace" 
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
#### machinelearningservices usage ####
##### List #####
```
az machinelearningservices usage list --location "eastus"
```
#### machinelearningservices virtual-machine-size ####
##### List #####
```
az machinelearningservices virtual-machine-size list --location "eastus"
```
#### machinelearningservices quota ####
##### List #####
```
az machinelearningservices quota list --location "eastus"
```
##### Update #####
```
az machinelearningservices quota update --location "eastus" \
    --value type="Microsoft.MachineLearningServices/workspaces/quotas" id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/Microsoft.MachineLearningServices/workspaces/demo_workspace1/quotas/Standard_DSv2_Family_Cluster_Dedicated_vCPUs" limit=100 unit="Count" \
    --value type="Microsoft.MachineLearningServices/workspaces/quotas" id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/Microsoft.MachineLearningServices/workspaces/demo_workspace2/quotas/Standard_DSv2_Family_Cluster_Dedicated_vCPUs" limit=200 unit="Count" 
```
#### machinelearningservices machine-learning-compute ####
##### Aks create #####
```
az machinelearningservices machine-learning-compute aks create --compute-name "compute123" --location "eastus" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Aks create #####
```
az machinelearningservices machine-learning-compute aks create --compute-name "compute123" --location "eastus" \
    --ak-s-properties "{\\"enableNodePublicIp\\":true,\\"isolatedNetwork\\":false,\\"osType\\":\\"Windows\\",\\"remoteLoginPortPublicAccess\\":\\"NotSpecified\\",\\"scaleSettings\\":{\\"maxNodeCount\\":1,\\"minNodeCount\\":0,\\"nodeIdleTimeBeforeScaleDown\\":\\"PT5M\\"},\\"virtualMachineImage\\":{\\"id\\":\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.Compute/galleries/myImageGallery/images/myImageDefinition/versions/0.0.1\\"},\\"vmPriority\\":\\"Dedicated\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Aks create #####
```
az machinelearningservices machine-learning-compute aks create --compute-name "compute123" --location "eastus" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Aks create #####
```
az machinelearningservices machine-learning-compute aks create --compute-name "compute123" --location "eastus" \
    --ak-s-properties "{\\"applicationSharingPolicy\\":\\"Personal\\",\\"computeInstanceAuthorizationType\\":\\"personal\\",\\"personalComputeInstanceSettings\\":{\\"assignedUser\\":{\\"objectId\\":\\"00000000-0000-0000-0000-000000000000\\",\\"tenantId\\":\\"00000000-0000-0000-0000-000000000000\\"}},\\"sshSettings\\":{\\"sshPublicAccess\\":\\"Disabled\\"},\\"subnet\\":\\"test-subnet-resource-id\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Aks create #####
```
az machinelearningservices machine-learning-compute aks create --compute-name "compute123" --location "eastus" \
    --ak-s-properties "{\\"vmSize\\":\\"STANDARD_NC6\\"}" --resource-group "testrg123" \
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
    --aml-compute-properties "{\\"enableNodePublicIp\\":true,\\"isolatedNetwork\\":false,\\"osType\\":\\"Windows\\",\\"remoteLoginPortPublicAccess\\":\\"NotSpecified\\",\\"scaleSettings\\":{\\"maxNodeCount\\":1,\\"minNodeCount\\":0,\\"nodeIdleTimeBeforeScaleDown\\":\\"PT5M\\"},\\"virtualMachineImage\\":{\\"id\\":\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.Compute/galleries/myImageGallery/images/myImageDefinition/versions/0.0.1\\"},\\"vmPriority\\":\\"Dedicated\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Aml-compute create #####
```
az machinelearningservices machine-learning-compute aml-compute create --compute-name "compute123" --location "eastus" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Aml-compute create #####
```
az machinelearningservices machine-learning-compute aml-compute create --compute-name "compute123" --location "eastus" \
    --aml-compute-properties "{\\"applicationSharingPolicy\\":\\"Personal\\",\\"computeInstanceAuthorizationType\\":\\"personal\\",\\"personalComputeInstanceSettings\\":{\\"assignedUser\\":{\\"objectId\\":\\"00000000-0000-0000-0000-000000000000\\",\\"tenantId\\":\\"00000000-0000-0000-0000-000000000000\\"}},\\"sshSettings\\":{\\"sshPublicAccess\\":\\"Disabled\\"},\\"subnet\\":\\"test-subnet-resource-id\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Aml-compute create #####
```
az machinelearningservices machine-learning-compute aml-compute create --compute-name "compute123" --location "eastus" \
    --aml-compute-properties "{\\"vmSize\\":\\"STANDARD_NC6\\"}" --resource-group "testrg123" \
    --workspace-name "workspaces123" 
```
##### Compute-instance create #####
```
az machinelearningservices machine-learning-compute compute-instance create --compute-name "compute123" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Compute-instance create #####
```
az machinelearningservices machine-learning-compute compute-instance create --compute-name "compute123" \
    --location "eastus" \
    --compute-instance-properties "{\\"enableNodePublicIp\\":true,\\"isolatedNetwork\\":false,\\"osType\\":\\"Windows\\",\\"remoteLoginPortPublicAccess\\":\\"NotSpecified\\",\\"scaleSettings\\":{\\"maxNodeCount\\":1,\\"minNodeCount\\":0,\\"nodeIdleTimeBeforeScaleDown\\":\\"PT5M\\"},\\"virtualMachineImage\\":{\\"id\\":\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.Compute/galleries/myImageGallery/images/myImageDefinition/versions/0.0.1\\"},\\"vmPriority\\":\\"Dedicated\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" \
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
    --location "eastus" \
    --compute-instance-properties "{\\"applicationSharingPolicy\\":\\"Personal\\",\\"computeInstanceAuthorizationType\\":\\"personal\\",\\"personalComputeInstanceSettings\\":{\\"assignedUser\\":{\\"objectId\\":\\"00000000-0000-0000-0000-000000000000\\",\\"tenantId\\":\\"00000000-0000-0000-0000-000000000000\\"}},\\"sshSettings\\":{\\"sshPublicAccess\\":\\"Disabled\\"},\\"subnet\\":\\"test-subnet-resource-id\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Compute-instance create #####
```
az machinelearningservices machine-learning-compute compute-instance create --compute-name "compute123" \
    --location "eastus" --compute-instance-properties "{\\"vmSize\\":\\"STANDARD_NC6\\"}" --resource-group "testrg123" \
    --workspace-name "workspaces123" 
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
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Data-factory create #####
```
az machinelearningservices machine-learning-compute data-factory create --compute-name "compute123" \
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
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Data-lake-analytics create #####
```
az machinelearningservices machine-learning-compute data-lake-analytics create --compute-name "compute123" \
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
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Databricks create #####
```
az machinelearningservices machine-learning-compute databricks create --compute-name "compute123" --location "eastus" \
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
##### Synapse-spark create #####
```
az machinelearningservices machine-learning-compute synapse-spark create --compute-name "compute123" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Synapse-spark create #####
```
az machinelearningservices machine-learning-compute synapse-spark create --compute-name "compute123" \
    --location "eastus" \
    --synapse-spark-properties "{\\"enableNodePublicIp\\":true,\\"isolatedNetwork\\":false,\\"osType\\":\\"Windows\\",\\"remoteLoginPortPublicAccess\\":\\"NotSpecified\\",\\"scaleSettings\\":{\\"maxNodeCount\\":1,\\"minNodeCount\\":0,\\"nodeIdleTimeBeforeScaleDown\\":\\"PT5M\\"},\\"virtualMachineImage\\":{\\"id\\":\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.Compute/galleries/myImageGallery/images/myImageDefinition/versions/0.0.1\\"},\\"vmPriority\\":\\"Dedicated\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Synapse-spark create #####
```
az machinelearningservices machine-learning-compute synapse-spark create --compute-name "compute123" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Synapse-spark create #####
```
az machinelearningservices machine-learning-compute synapse-spark create --compute-name "compute123" \
    --location "eastus" \
    --synapse-spark-properties "{\\"applicationSharingPolicy\\":\\"Personal\\",\\"computeInstanceAuthorizationType\\":\\"personal\\",\\"personalComputeInstanceSettings\\":{\\"assignedUser\\":{\\"objectId\\":\\"00000000-0000-0000-0000-000000000000\\",\\"tenantId\\":\\"00000000-0000-0000-0000-000000000000\\"}},\\"sshSettings\\":{\\"sshPublicAccess\\":\\"Disabled\\"},\\"subnet\\":\\"test-subnet-resource-id\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Synapse-spark create #####
```
az machinelearningservices machine-learning-compute synapse-spark create --compute-name "compute123" \
    --location "eastus" --synapse-spark-properties "{\\"vmSize\\":\\"STANDARD_NC6\\"}" --resource-group "testrg123" \
    --workspace-name "workspaces123" 
```
##### Virtual-machine create #####
```
az machinelearningservices machine-learning-compute virtual-machine create --compute-name "compute123" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Virtual-machine create #####
```
az machinelearningservices machine-learning-compute virtual-machine create --compute-name "compute123" \
    --location "eastus" \
    --virtual-machine-properties "{\\"enableNodePublicIp\\":true,\\"isolatedNetwork\\":false,\\"osType\\":\\"Windows\\",\\"remoteLoginPortPublicAccess\\":\\"NotSpecified\\",\\"scaleSettings\\":{\\"maxNodeCount\\":1,\\"minNodeCount\\":0,\\"nodeIdleTimeBeforeScaleDown\\":\\"PT5M\\"},\\"virtualMachineImage\\":{\\"id\\":\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.Compute/galleries/myImageGallery/images/myImageDefinition/versions/0.0.1\\"},\\"vmPriority\\":\\"Dedicated\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Virtual-machine create #####
```
az machinelearningservices machine-learning-compute virtual-machine create --compute-name "compute123" \
    --location "eastus" --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Virtual-machine create #####
```
az machinelearningservices machine-learning-compute virtual-machine create --compute-name "compute123" \
    --location "eastus" \
    --virtual-machine-properties "{\\"applicationSharingPolicy\\":\\"Personal\\",\\"computeInstanceAuthorizationType\\":\\"personal\\",\\"personalComputeInstanceSettings\\":{\\"assignedUser\\":{\\"objectId\\":\\"00000000-0000-0000-0000-000000000000\\",\\"tenantId\\":\\"00000000-0000-0000-0000-000000000000\\"}},\\"sshSettings\\":{\\"sshPublicAccess\\":\\"Disabled\\"},\\"subnet\\":\\"test-subnet-resource-id\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" \
    --resource-group "testrg123" --workspace-name "workspaces123" 
```
##### Virtual-machine create #####
```
az machinelearningservices machine-learning-compute virtual-machine create --compute-name "compute123" \
    --location "eastus" --virtual-machine-properties "{\\"vmSize\\":\\"STANDARD_NC6\\"}" --resource-group "testrg123" \
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
##### Show #####
```
az machinelearningservices machine-learning-compute show --compute-name "compute123" --resource-group "testrg123" \
    --workspace-name "workspaces123" 
```
##### List #####
```
az machinelearningservices machine-learning-compute list --resource-group "testrg123" --workspace-name "workspaces123"
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
#### machinelearningservices workspace ####
##### List-sku #####
```
az machinelearningservices workspace list-sku
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
#### machinelearningservices machine-learning-service ####
##### Create #####
```
az machinelearningservices machine-learning-service create \
    --properties "{\\"appInsightsEnabled\\":true,\\"authEnabled\\":true,\\"computeType\\":\\"ACI\\",\\"containerResourceRequirements\\":{\\"cpu\\":1,\\"memoryInGB\\":1},\\"environmentImageRequest\\":{\\"assets\\":[{\\"id\\":null,\\"mimeType\\":\\"application/x-python\\",\\"unpack\\":false,\\"url\\":\\"aml://storage/azureml/score.py\\"}],\\"driverProgram\\":\\"score.py\\",\\"environment\\":{\\"name\\":\\"AzureML-Scikit-learn-0.20.3\\",\\"docker\\":{\\"baseDockerfile\\":null,\\"baseImage\\":\\"mcr.microsoft.com/azureml/base:openmpi3.1.2-ubuntu16.04\\",\\"baseImageRegistry\\":{\\"address\\":null,\\"password\\":null,\\"username\\":null}},\\"environmentVariables\\":{\\"EXAMPLE_ENV_VAR\\":\\"EXAMPLE_VALUE\\"},\\"inferencingStackVersion\\":null,\\"python\\":{\\"baseCondaEnvironment\\":null,\\"condaDependencies\\":{\\"name\\":\\"azureml_ae1acbe6e1e6aabbad900b53c491a17c\\",\\"channels\\":[\\"conda-forge\\"],\\"dependencies\\":[\\"python=3.6.2\\",{\\"pip\\":[\\"azureml-core==1.0.69\\",\\"azureml-defaults==1.0.69\\",\\"azureml-telemetry==1.0.69\\",\\"azureml-train-restclients-hyperdrive==1.0.69\\",\\"azureml-train-core==1.0.69\\",\\"scikit-learn==0.20.3\\",\\"scipy==1.2.1\\",\\"numpy==1.16.2\\",\\"joblib==0.13.2\\"]}]},\\"interpreterPath\\":\\"python\\",\\"userManagedDependencies\\":false},\\"spark\\":{\\"packages\\":[],\\"precachePackages\\":true,\\"repositories\\":[]},\\"version\\":\\"3\\"},\\"models\\":[{\\"name\\":\\"sklearn_regression_model.pkl\\",\\"mimeType\\":\\"application/x-python\\",\\"url\\":\\"aml://storage/azureml/sklearn_regression_model.pkl\\"}]},\\"location\\":\\"eastus2\\"}" \
    --resource-group "testrg123" --service-name "service456" --workspace-name "workspaces123" 
```
##### Show #####
```
az machinelearningservices machine-learning-service show --resource-group "testrg123" --service-name "service123" \
    --workspace-name "workspaces123" 
```
##### List #####
```
az machinelearningservices machine-learning-service list --resource-group "testrg123" --workspace-name "workspaces123"
```
##### Delete #####
```
az machinelearningservices machine-learning-service delete --resource-group "testrg123" --service-name "service123" \
    --workspace-name "workspaces123" 
```
#### machinelearningservices notebook ####
##### List-key #####
```
az machinelearningservices notebook list-key --resource-group "testrg123" --workspace-name "workspaces123"
```
##### Prepare #####
```
az machinelearningservices notebook prepare --resource-group "testrg123" --workspace-name "workspaces123"
```
#### machinelearningservices storage-account ####
##### List-key #####
```
az machinelearningservices storage-account list-key --resource-group "testrg123" --workspace-name "workspaces123"
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