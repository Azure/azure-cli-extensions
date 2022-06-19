# Azure CLI devcenter Extension #
This is the extension for devcenter

### How to use ###
Install this extension using the below CLI command
```
az extension add --name devcenter
```

### Included Features ###
#### devcenter dev-center ####
##### Create #####
```
az devcenter dev-center create --location "centralus" --tags CostCode="12345" --name "Contoso" --resource-group "rg1"

az devcenter dev-center wait --created --name "{myDevCenter}" --resource-group "{rg}"
```
##### Create #####
```
az devcenter dev-center create --type "UserAssigned" \
    --user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/identityGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/testidentity1\\":{}}" \
    --location "centralus" --tags CostCode="12345" --name "Contoso" --resource-group "rg1" 

az devcenter dev-center wait --created --name "{myDevCenter}" --resource-group "{rg}"
```
##### List #####
```
az devcenter dev-center list --resource-group "rg1"
```
##### Show #####
```
az devcenter dev-center show --name "Contoso" --resource-group "rg1"
```
##### Update #####
```
az devcenter dev-center update --tags CostCode="12345" --name "Contoso" --resource-group "rg1"
```
##### Delete #####
```
az devcenter dev-center delete --name "Contoso" --resource-group "rg1"
```
#### devcenter project ####
##### Create #####
```
az devcenter project create --location "centralus" --description "This is my first project." \
    --dev-center-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.DevCenter/devcenters/{devCenterName}" \
    --tags CostCenter="R&D" --name "{projectName}" --resource-group "rg1" 

az devcenter project wait --created --name "{myProject}" --resource-group "{rg}"
```
##### Show #####
```
az devcenter project show --name "{projectName}" --resource-group "rg1"
```
##### List #####
```
az devcenter project list --resource-group "rg1"
```
##### Update #####
```
az devcenter project update --description "This is my first project." --tags CostCenter="R&D" --name "{projectName}" \
    --resource-group "rg1" 
```
##### Delete #####
```
az devcenter project delete --name "{projectName}" --resource-group "rg1"
```
#### devcenter attached-network ####
##### Create #####
```
az devcenter attached-network create --attached-network-connection-name "{attachedNetworkConnectionName}" \
    --network-connection-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.DevCenter/NetworkConnections/network-uswest3" \
    --dev-center-name "Contoso" --resource-group "rg1" 
```
##### Show #####
```
az devcenter attached-network show --attached-network-connection-name "network-uswest3" --project-name "{projectName}" \
    --resource-group "rg1" 
```
##### List #####
```
az devcenter attached-network list --project-name "{projectName}" --resource-group "rg1"
```
##### Delete #####
```
az devcenter attached-network delete --attached-network-connection-name "{attachedNetworkConnectionName}" \
    --dev-center-name "Contoso" --resource-group "rg1" 
```
#### devcenter gallery ####
##### Create #####
```
az devcenter gallery create \
    --gallery-resource-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.Compute/galleries/{galleryName}" \
    --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1" 

az devcenter gallery wait --created --dev-center-name "{myDevCenter}" --name "{myGallery}" --resource-group "{rg}"
```
##### Show #####
```
az devcenter gallery show --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1"
```
##### List #####
```
az devcenter gallery list --dev-center-name "Contoso" --resource-group "rg1"
```
##### Delete #####
```
az devcenter gallery delete --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1"
```
#### devcenter image ####
##### List #####
```
az devcenter image list --dev-center-name "Contoso" --gallery-name "DevGallery" --resource-group "rg1"
```
##### Show #####
```
az devcenter image show --dev-center-name "Contoso" --gallery-name "DefaultDevGallery" --name "{imageName}" \
    --resource-group "rg1" 
```
#### devcenter image-version ####
##### List #####
```
az devcenter image-version list --dev-center-name "Contoso" --gallery-name "DefaultDevGallery" --image-name "Win11" \
    --resource-group "rg1" 
```
##### Show #####
```
az devcenter image-version show --dev-center-name "Contoso" --gallery-name "DefaultDevGallery" --image-name "Win11" \
    --resource-group "rg1" --version-name "{versionName}" 
```
#### devcenter catalog ####
##### Create #####
```
az devcenter catalog create \
    --ado-git path="/templates" branch="main" secret-identifier="https://contosokv.vault.azure.net/secrets/CentralRepoPat" uri="https://contoso@dev.azure.com/contoso/contosoOrg/_git/centralrepo-fakecontoso" \
    --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1" 

az devcenter catalog wait --created --name "{myCatalog}" --dev-center-name "{myDevCenter}" --resource-group "{rg}"
```
##### Create #####
```
az devcenter catalog create \
    --git-hub path="/templates" branch="main" secret-identifier="https://contosokv.vault.azure.net/secrets/CentralRepoPat" uri="https://github.com/Contoso/centralrepo-fake.git" \
    --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1" 

az devcenter catalog wait --created --name "{myCatalog}" --dev-center-name "{myDevCenter}" --resource-group "{rg}"
```
##### List #####
```
az devcenter catalog list --dev-center-name "Contoso" --resource-group "rg1"
```
##### Show #####
```
az devcenter catalog show --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
```
##### Update #####
```
az devcenter catalog update --git-hub path="/environments" --name "{catalogName}" --dev-center-name "Contoso" \
    --resource-group "rg1" 
```
##### Sync #####
```
az devcenter catalog sync --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
```
##### Delete #####
```
az devcenter catalog delete --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
```
#### devcenter environment-type ####
##### Create #####
```
az devcenter environment-type create --tags Owner="superuser" --dev-center-name "Contoso" \
    --name "{environmentTypeName}" --resource-group "rg1" 
```
##### Show #####
```
az devcenter environment-type show --dev-center-name "Contoso" --name "{environmentTypeName}" --resource-group "rg1"
```
##### List #####
```
az devcenter environment-type list --dev-center-name "Contoso" --resource-group "rg1"
```
##### Update #####
```
az devcenter environment-type update --tags Owner="superuser" --dev-center-name "Contoso" \
    --name "{environmentTypeName}" --resource-group "rg1" 
```
##### Delete #####
```
az devcenter environment-type delete --dev-center-name "Contoso" --name "{environmentTypeName}" --resource-group "rg1"
```
#### devcenter project-environment-type ####
##### Create #####
```
az devcenter project-environment-type create --type "UserAssigned" \
    --user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/identityGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/testidentity1\\":{}}" \
    --creator-role-assignment "/some/role/definition/id" \
    --deployment-target-id "/subscriptions/00000000-0000-0000-0000-000000000000" --status "Enabled" \
    --user-role-assignments "{\\"e45e3m7c-176e-416a-b466-0c5ec8298f8a\\":{\\"roles\\":{\\"4cbf0b6c-e750-441c-98a7-10da8387e4d6\\":{}}}}" \
    --tags CostCenter="RnD" --environment-type-name "{environmentTypeName}" --project-name "ContosoProj" \
    --resource-group "rg1" 
```
##### Show #####
```
az devcenter project-environment-type show --environment-type-name "{environmentTypeName}" \
    --project-name "ContosoProj" --resource-group "rg1" 
```
##### List #####
```
az devcenter project-environment-type list --project-name "ContosoProj" --resource-group "rg1"
```
##### Update #####
```
az devcenter project-environment-type update --type "UserAssigned" \
    --user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/identityGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/testidentity1\\":{}}" \
    --deployment-target-id "/subscriptions/00000000-0000-0000-0000-000000000000" --status "Enabled" \
    --user-role-assignments "{\\"e45e3m7c-176e-416a-b466-0c5ec8298f8a\\":{\\"roles\\":{\\"4cbf0b6c-e750-441c-98a7-10da8387e4d6\\":{}}}}" \
    --tags CostCenter="RnD" --environment-type-name "{environmentTypeName}" --project-name "ContosoProj" \
    --resource-group "rg1" 
```
##### Delete #####
```
az devcenter project-environment-type delete --environment-type-name "{environmentTypeName}" \
    --project-name "ContosoProj" --resource-group "rg1" 
```
#### devcenter dev-box-definition ####
##### Create #####
```
az devcenter dev-box-definition create --location "centralus" \
    --image-reference id="/subscriptions/0ac520ee-14c0-480f-b6c9-0a90c58ffff/resourceGroups/Example/providers/Microsoft.DevCenter/devcenters/Contoso/galleries/contosogallery/images/exampleImage/version/1.0.0" \
    --os-storage-type "SSD_1024" --sku name="Preview" --name "WebDevBox" --dev-center-name "Contoso" \
    --resource-group "rg1" 

az devcenter dev-box-definition wait --created --name "{myDevBoxDefinition}" --dev-center-name "{myDevCenter}" \
    --resource-group "{rg}" 
```
##### Show #####
```
az devcenter dev-box-definition show --name "WebDevBox" --dev-center-name "Contoso" --resource-group "rg1"
```
##### List #####
```
az devcenter dev-box-definition list --dev-center-name "Contoso" --resource-group "rg1"
```
##### Update #####
```
az devcenter dev-box-definition update \
    --image-reference id="/subscriptions/0ac520ee-14c0-480f-b6c9-0a90c58ffff/resourceGroups/Example/providers/Microsoft.DevCenter/devcenters/Contoso/galleries/contosogallery/images/exampleImage/version/2.0.0" \
    --name "WebDevBox" --dev-center-name "Contoso" --resource-group "rg1" 
```
##### Delete #####
```
az devcenter dev-box-definition delete --name "WebDevBox" --dev-center-name "Contoso" --resource-group "rg1"
```
#### devcenter operation-statuses ####
##### Show #####
```
az devcenter operation-statuses show --operation-id "{operationId}" --location "{location}"
```
#### devcenter usage ####
##### List #####
```
az devcenter usage list --location "westus"
```
#### devcenter sku ####
##### List #####
```
az devcenter sku list
```
#### devcenter pool ####
##### Create #####
```
az devcenter pool create --location "centralus" --dev-box-definition-name "WebDevBox" --local-administrator "Enabled" \
    --network-connection-name "Network1-westus2" --name "{poolName}" --project-name "{projectName}" \
    --resource-group "rg1" 

az devcenter pool wait --created --name "{myPool}" --project-name "{myProject}" --resource-group "{rg}"
```
##### Show #####
```
az devcenter pool show --name "{poolName}" --project-name "{projectName}" --resource-group "rg1"
```
##### List #####
```
az devcenter pool list --project-name "{projectName}" --resource-group "rg1"
```
##### Update #####
```
az devcenter pool update --dev-box-definition-name "WebDevBox2" --name "{poolName}" --project-name "{projectName}" \
    --resource-group "rg1" 
```
##### Delete #####
```
az devcenter pool delete --name "poolName" --project-name "{projectName}" --resource-group "rg1"
```
#### devcenter schedule ####
##### Create #####
```
az devcenter schedule create --state "Enabled" --time "17:30" --time-zone "America/Los_Angeles" --pool-name "DevPool" \
    --project-name "DevProject" --resource-group "rg1" --name "autoShutdown" 

az devcenter schedule wait --created --pool-name "{myPool3}" --project-name "{myProject5}" --resource-group "{rg}" \
    --name "{mySchedule}" 
```
##### Show #####
```
az devcenter schedule show --pool-name "DevPool" --project-name "TestProject" --resource-group "rg1" \
    --name "autoShutdown" 
```
##### List #####
```
az devcenter schedule list --pool-name "DevPool" --project-name "TestProject" --resource-group "rg1"
```
##### Update #####
```
az devcenter schedule update --time "18:00" --pool-name "DevPool" --project-name "TestProject" --resource-group "rg1" \
    --name "autoShutdown" 
```
##### Delete #####
```
az devcenter schedule delete --pool-name "DevPool" --project-name "TestProject" --resource-group "rg1" \
    --name "autoShutdown" 
```
#### devcenter network-connection ####
##### Create #####
```
az devcenter network-connection create --location "centralus" --domain-join-type "HybridAzureADJoin" \
    --domain-name "mydomaincontroller.local" --domain-password "Password value for user" \
    --domain-username "testuser@mydomaincontroller.local" --networking-resource-group-name "NetworkInterfaces" \
    --subnet-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/ExampleRG/providers/Microsoft.Network/virtualNetworks/ExampleVNet/subnets/default" \
    --name "uswest3network" --resource-group "rg1" 

az devcenter network-connection wait --created --name "{myNetworkConnection3}" --resource-group "{rg}"
```
##### Show #####
```
az devcenter network-connection show --name "uswest3network" --resource-group "rg1"
```
##### List #####
```
az devcenter network-connection list --resource-group "rg1"
```
##### Update #####
```
az devcenter network-connection update --domain-password "New Password value for user" --name "uswest3network" \
    --resource-group "rg1" 
```
##### List-health-detail #####
```
az devcenter network-connection list-health-detail --name "uswest3network" --resource-group "rg1"
```
##### Run-health-check #####
```
az devcenter network-connection run-health-check --name "uswest3network" --resource-group "rg1"
```
##### Show-health-detail #####
```
az devcenter network-connection show-health-detail --name "{networkConnectionName}" --resource-group "rg1"
```
##### Delete #####
```
az devcenter network-connection delete --name "{networkConnectionName}" --resource-group "rg1"
```