# Azure CLI fidalgo-admin Extension #
This is the extension for fidalgo-admin

### How to use ###
Install this extension using the below CLI command
```
az extension add --name fidalgo-admin
```

### Included Features ###
#### fidalgo-admin dev-center ####
##### Create #####
```
az fidalgo-admin dev-center create --location "centralus" --tags CostCode="12345" --name "Contoso" \
    --resource-group "rg1" 

az fidalgo-admin dev-center wait --created --name "{myDevCenter}" --resource-group "{rg}"
```
##### Create #####
```
az fidalgo-admin dev-center create --type "UserAssigned" \
    --user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/identityGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/testidentity1\\":{}}" \
    --location "centralus" --tags CostCode="12345" --name "Contoso" --resource-group "rg1" 

az fidalgo-admin dev-center wait --created --name "{myDevCenter}" --resource-group "{rg}"
```
##### List #####
```
az fidalgo-admin dev-center list --resource-group "rg1"
```
##### Show #####
```
az fidalgo-admin dev-center show --name "Contoso" --resource-group "rg1"
```
##### Update #####
```
az fidalgo-admin dev-center update --tags CostCode="12345" --name "Contoso" --resource-group "rg1"
```
##### Delete #####
```
az fidalgo-admin dev-center delete --name "Contoso" --resource-group "rg1"
```
#### fidalgo-admin project ####
##### Create #####
```
az fidalgo-admin project create --location "centralus" --description "This is my first project." \
    --dev-center-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.Fidalgo/devcenters/{devCenterName}" \
    --tags CostCenter="R&D" --name "{projectName}" --resource-group "rg1" 

az fidalgo-admin project wait --created --name "{myProject}" --resource-group "{rg}"
```
##### Show #####
```
az fidalgo-admin project show --name "{projectName}" --resource-group "rg1"
```
##### List #####
```
az fidalgo-admin project list --resource-group "rg1"
```
##### Update #####
```
az fidalgo-admin project update --description "This is my first project." --tags CostCenter="R&D" \
    --name "{projectName}" --resource-group "rg1" 
```
##### Delete #####
```
az fidalgo-admin project delete --name "{projectName}" --resource-group "rg1"
```
#### fidalgo-admin environment ####
##### Create #####
```
az fidalgo-admin environment create --location "centralus" --description "Personal Dev Environment" \
    --catalog-item-name "helloworld" --deployment-parameters "{\\"app_name\\":\\"mydevApi\\"}" \
    --environment-type "DevTest" --tags ProjectType="WebApi" Role="Development" Tech="NetCore" \
    --name "{environmentName}" --project-name "{projectName}" --resource-group "rg1" 

az fidalgo-admin environment wait --created --name "{myEnvironment}" --project-name "{myProject}" \
    --resource-group "{rg}" 
```
##### Create #####
```
az fidalgo-admin environment create --location "centralus" --description "Personal Dev Environment" \
    --deployment-parameters "{\\"app_name\\":\\"mydevApi\\"}" --environment-type "DevTest" \
    --template-uri "https://raw.githubusercontent.com/contoso/webhelpcenter/master/environments/composition-template.json" \
    --tags ProjectType="WebApi" Role="Development" Tech="NetCore" --name "{environmentName}" \
    --project-name "{projectName}" --resource-group "rg1" 

az fidalgo-admin environment wait --created --name "{myEnvironment}" --project-name "{myProject}" \
    --resource-group "{rg}" 
```
##### List #####
```
az fidalgo-admin environment list --project-name "{projectName}" --resource-group "rg1"
```
##### Show #####
```
az fidalgo-admin environment show --name "{environmentName}" --project-name "{projectName}" --resource-group "rg1"
```
##### Update #####
```
az fidalgo-admin environment update --description "Personal Dev Environment 2" \
    --tags ProjectType="WebApi" Role="Development" Tech="NetCore" --name "{environmentName}" \
    --project-name "{projectName}" --resource-group "rg1" 
```
##### Deploy #####
```
az fidalgo-admin environment deploy --name "{environmentName}" --project-name "{projectName}" --resource-group "rg1"
```
##### Delete #####
```
az fidalgo-admin environment delete --name "{environmentName}" --project-name "{projectName}" --resource-group "rg1"
```
#### fidalgo-admin deployment ####
##### List #####
```
az fidalgo-admin deployment list --environment-name "{environmentName}" --project-name "{projectName}" \
    --resource-group "rg1" 
```
#### fidalgo-admin environment-type ####
##### Create #####
```
az fidalgo-admin environment-type create --description "Developer/Testing environment" --dev-center-name "Contoso" \
    --name "{environmentTypeName}" --resource-group "rg1" 
```
##### Show #####
```
az fidalgo-admin environment-type show --dev-center-name "Contoso" --name "{environmentTypeName}" \
    --resource-group "rg1" 
```
##### List #####
```
az fidalgo-admin environment-type list --project-name "Contoso" --resource-group "rg1"
```
##### Update #####
```
az fidalgo-admin environment-type update --description "Updated description" --dev-center-name "Contoso" \
    --name "{environmentTypeName}" --resource-group "rg1" 
```
##### Delete #####
```
az fidalgo-admin environment-type delete --dev-center-name "Contoso" --name "{environmentTypeName}" \
    --resource-group "rg1" 
```
#### fidalgo-admin catalog-item ####
##### Create #####
```
az fidalgo-admin catalog-item create --description "Hello world template to deploy a basic API service" \
    --parameters name="app_name" type="string" description="The name of the application. This must be provided when deploying an environment with this template." \
    --template-path "azuredeploy.json" --name "{itemName}" --catalog-name "{catalogName}" --dev-center-name "Contoso" \
    --resource-group "rg1" 
```
##### Show #####
```
az fidalgo-admin catalog-item show --name "{itemName}" --catalog-name "{catalogName}" --dev-center-name "Contoso" \
    --resource-group "rg1" 
```
##### List #####
```
az fidalgo-admin catalog-item list --catalog-name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
```
##### Update #####
```
az fidalgo-admin catalog-item update --description "Hello world template to deploy a basic API service" \
    --name "{itemName}" --catalog-name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1" 
```
##### Delete #####
```
az fidalgo-admin catalog-item delete --name "{itemName}" --catalog-name "{catalogName}" --dev-center-name "Contoso" \
    --resource-group "rg1" 
```
#### fidalgo-admin catalog ####
##### Create #####
```
az fidalgo-admin catalog create \
    --ado-git path="/templates" branch="main" secret-identifier="https://contosokv.vault.azure.net/secrets/CentralRepoPat" uri="https://contoso@dev.azure.com/contoso/contosoOrg/_git/centralrepo-fakecontoso" \
    --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1" 

az fidalgo-admin catalog wait --created --name "{myCatalog}" --dev-center-name "{myDevCenter}" --resource-group "{rg}"
```
##### Create #####
```
az fidalgo-admin catalog create \
    --git-hub path="/templates" branch="main" secret-identifier="https://contosokv.vault.azure.net/secrets/CentralRepoPat" uri="https://github.com/Contoso/centralrepo-fake.git" \
    --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1" 

az fidalgo-admin catalog wait --created --name "{myCatalog}" --dev-center-name "{myDevCenter}" --resource-group "{rg}"
```
##### List #####
```
az fidalgo-admin catalog list --dev-center-name "Contoso" --resource-group "rg1"
```
##### Show #####
```
az fidalgo-admin catalog show --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
```
##### Update #####
```
az fidalgo-admin catalog update --git-hub path="/environments" --name "{catalogName}" --dev-center-name "Contoso" \
    --resource-group "rg1" 
```
##### Sync #####
```
az fidalgo-admin catalog sync --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
```
##### Delete #####
```
az fidalgo-admin catalog delete --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
```
#### fidalgo-admin mapping ####
##### Create #####
```
az fidalgo-admin mapping create --environment-type "Sandbox" \
    --mapped-subscription-id "/subscriptions/57a221ae-b5e9-4bea-be0a-e86e5f9317cc" \
    --project-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.Fidalgo/projects/{projectName}" \
    --dev-center-name "Contoso" --name "{mappingName}" --resource-group "rg1" 
```
##### Show #####
```
az fidalgo-admin mapping show --dev-center-name "Contoso" --name "{mappingName}" --resource-group "rg1"
```
##### List #####
```
az fidalgo-admin mapping list --dev-center-name "Contoso" --resource-group "rg1"
```
##### Update #####
```
az fidalgo-admin mapping update --mapped-subscription-id "/subscriptions/57a221ae-b5e9-4bea-be0a-e86e5f9317cc" \
    --dev-center-name "Contoso" --name "{mappingName}" --resource-group "rg1" 
```
##### Delete #####
```
az fidalgo-admin mapping delete --dev-center-name "Contoso" --name "{mappingName}" --resource-group "rg1"
```
#### fidalgo-admin operation-statuses ####
##### Show #####
```
az fidalgo-admin operation-statuses show --operation-id "{operationId}" --location "{location}"
```
#### fidalgo-admin sku ####
##### List #####
```
az fidalgo-admin sku list
```
#### fidalgo-admin pool ####
##### Create #####
```
az fidalgo-admin pool create --location "centralus" \
    --machine-definition-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.Fidalgo/machinedefinitions/{machineDefinitionName}" \
    --network-settings-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.Fidalgo/networksettings/{networkSettingName}" \
    --sku name="medium" --name "{poolName}" --project-name "{projectName}" --resource-group "rg1" 

az fidalgo-admin pool wait --created --name "{myPool}" --project-name "{myProject}" --resource-group "{rg}"
```
##### Show #####
```
az fidalgo-admin pool show --name "{poolName}" --project-name "{projectName}" --resource-group "rg1"
```
##### List #####
```
az fidalgo-admin pool list --project-name "{projectName}" --resource-group "rg1"
```
##### Update #####
```
az fidalgo-admin pool update \
    --machine-definition-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.Fidalgo/machinedefinitions/{machineDefinitionName}" \
    --name "{poolName}" --project-name "{projectName}" --resource-group "rg1" 
```
##### Delete #####
```
az fidalgo-admin pool delete --name "poolName" --project-name "{projectName}" --resource-group "rg1"
```
#### fidalgo-admin machine-definition ####
##### Create #####
```
az fidalgo-admin machine-definition create --location "centralus" \
    --image-reference id="/subscriptions/0ac520ee-14c0-480f-b6c9-0a90c58ffff/resourceGroups/Example/providers/Microsoft.Compute/images/exampleImage" \
    --name "{machineDefinitionName}" --resource-group "rg1" 

az fidalgo-admin machine-definition wait --created --name "{myMachineDefinition}" --resource-group "{rg}"
```
##### Show #####
```
az fidalgo-admin machine-definition show --name "{machineDefinitionName}" --resource-group "rg1"
```
##### List #####
```
az fidalgo-admin machine-definition list --resource-group "rg1"
```
##### Update #####
```
az fidalgo-admin machine-definition update \
    --image-reference id="/subscriptions/0ac520ee-14c0-480f-b6c9-0a90c58ffff/resourceGroups/Example/providers/Microsoft.Compute/images/image2" \
    --name "{machineDefinitionName}" --resource-group "rg1" 
```
##### Delete #####
```
az fidalgo-admin machine-definition delete --name "{machineDefinitionName}" --resource-group "rg1"
```
#### fidalgo-admin network-setting ####
##### Create #####
```
az fidalgo-admin network-setting create --location "centralus" --domain-name "mydomaincontroller.local" \
    --domain-password "Password value for user" --domain-username "testuser@mydomaincontroller.local" \
    --networking-resource-group-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/ExampleRG" \
    --subnet-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/ExampleRG/providers/Microsoft.Network/virtualNetworks/ExampleVNet/subnets/default" \
    --name "{networkSettingName}" --resource-group "rg1" 

az fidalgo-admin network-setting wait --created --name "{myNetworkSetting}" --resource-group "{rg}"
```
##### Show #####
```
az fidalgo-admin network-setting show --name "{networkSettingName}" --resource-group "rg1"
```
##### List #####
```
az fidalgo-admin network-setting list --resource-group "rg1"
```
##### Update #####
```
az fidalgo-admin network-setting update --domain-password "New Password value for user" --name "{networkSettingName}" \
    --resource-group "rg1" 
```
##### Show-health-detail #####
```
az fidalgo-admin network-setting show-health-detail --name "{networkSettingName}" --resource-group "rg1"
```
##### Delete #####
```
az fidalgo-admin network-setting delete --name "{networkSettingName}" --resource-group "rg1"
```