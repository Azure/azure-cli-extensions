# Azure CLI fidalgo Extension #
This is the extension for fidalgo

### How to use ###
Install this extension using the below CLI command
```
az extension add --name fidalgo
```

### Included Features ###
#### fidalgo dev-center ####
##### Create #####
```
az fidalgo dev-center create --location "centralus" --tags CostCode="12345" --name "Contoso" --resource-group "rg1"

az fidalgo dev-center wait --created --name "{myDevCenter}" --resource-group "{rg}"
```
##### Create #####
```
az fidalgo dev-center create --type "UserAssigned" \
    --user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/identityGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/testidentity1\\":{}}" \
    --location "centralus" --tags CostCode="12345" --name "Contoso" --resource-group "rg1" 

az fidalgo dev-center wait --created --name "{myDevCenter}" --resource-group "{rg}"
```
##### List #####
```
az fidalgo dev-center list --resource-group "rg1"
```
##### Show #####
```
az fidalgo dev-center show --name "Contoso" --resource-group "rg1"
```
##### Update #####
```
az fidalgo dev-center update --tags CostCode="12345" --name "Contoso" --resource-group "rg1"
```
##### Delete #####
```
az fidalgo dev-center delete --name "Contoso" --resource-group "rg1"
```
#### fidalgo project ####
##### Create #####
```
az fidalgo project create --location "centralus" --description "This is my first project." \
    --dev-center-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.Fidalgo/devcenters/{devCenterName}" \
    --tags CostCenter="R&D" --name "{projectName}" --resource-group "rg1" 

az fidalgo project wait --created --name "{myProject}" --resource-group "{rg}"
```
##### Show #####
```
az fidalgo project show --name "{projectName}" --resource-group "rg1"
```
##### List #####
```
az fidalgo project list --resource-group "rg1"
```
##### Update #####
```
az fidalgo project update --description "This is my first project." --tags CostCenter="R&D" --name "{projectName}" \
    --resource-group "rg1" 
```
##### Delete #####
```
az fidalgo project delete --name "{projectName}" --resource-group "rg1"
```
#### fidalgo environment ####
##### Create #####
```
az fidalgo environment create --location "centralus" --description "Personal Dev Environment" \
    --catalog-item-name "helloworld" --deployment-parameters "{\\"app_name\\":\\"mydevApi\\"}" \
    --environment-type "DevTest" --tags ProjectType="WebApi" Role="Development" Tech="NetCore" \
    --name "{environmentName}" --project-name "{projectName}" --resource-group "rg1" 

az fidalgo environment wait --created --name "{myEnvironment}" --project-name "{myProject}" --resource-group "{rg}"
```
##### Create #####
```
az fidalgo environment create --location "centralus" --description "Personal Dev Environment" \
    --deployment-parameters "{\\"app_name\\":\\"mydevApi\\"}" --environment-type "DevTest" \
    --template-uri "https://raw.githubusercontent.com/contoso/webhelpcenter/master/environments/composition-template.json" \
    --tags ProjectType="WebApi" Role="Development" Tech="NetCore" --name "{environmentName}" \
    --project-name "{projectName}" --resource-group "rg1" 

az fidalgo environment wait --created --name "{myEnvironment}" --project-name "{myProject}" --resource-group "{rg}"
```
##### List #####
```
az fidalgo environment list --project-name "{projectName}" --resource-group "rg1"
```
##### Show #####
```
az fidalgo environment show --name "{environmentName}" --project-name "{projectName}" --resource-group "rg1"
```
##### Update #####
```
az fidalgo environment update --description "Personal Dev Environment 2" \
    --tags ProjectType="WebApi" Role="Development" Tech="NetCore" --name "{environmentName}" \
    --project-name "{projectName}" --resource-group "rg1" 
```
##### Deploy #####
```
az fidalgo environment deploy --name "{environmentName}" --project-name "{projectName}" --resource-group "rg1"
```
##### Delete #####
```
az fidalgo environment delete --name "{environmentName}" --project-name "{projectName}" --resource-group "rg1"
```
#### fidalgo deployment ####
##### List #####
```
az fidalgo deployment list --environment-name "{environmentName}" --project-name "{projectName}" --resource-group "rg1"
```
#### fidalgo environment-type ####
##### Create #####
```
az fidalgo environment-type create --description "Developer/Testing environment" --dev-center-name "Contoso" \
    --name "{environmentTypeName}" --resource-group "rg1" 
```
##### Show #####
```
az fidalgo environment-type show --dev-center-name "Contoso" --name "{environmentTypeName}" --resource-group "rg1"
```
##### List #####
```
az fidalgo environment-type list --project-name "Contoso" --resource-group "rg1"
```
##### Update #####
```
az fidalgo environment-type update --description "Updated description" --dev-center-name "Contoso" \
    --name "{environmentTypeName}" --resource-group "rg1" 
```
##### Delete #####
```
az fidalgo environment-type delete --dev-center-name "Contoso" --name "{environmentTypeName}" --resource-group "rg1"
```
#### fidalgo catalog-item ####
##### Create #####
```
az fidalgo catalog-item create --description "Hello world template to deploy a basic API service" \
    --parameters name="app_name" type="string" description="The name of the application. This must be provided when deploying an environment with this template." \
    --template-path "azuredeploy.json" --name "{itemName}" --catalog-name "{catalogName}" --dev-center-name "Contoso" \
    --resource-group "rg1" 
```
##### Show #####
```
az fidalgo catalog-item show --name "{itemName}" --catalog-name "{catalogName}" --dev-center-name "Contoso" \
    --resource-group "rg1" 
```
##### List #####
```
az fidalgo catalog-item list --catalog-name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
```
##### Update #####
```
az fidalgo catalog-item update --description "Hello world template to deploy a basic API service" --name "{itemName}" \
    --catalog-name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1" 
```
##### Delete #####
```
az fidalgo catalog-item delete --name "{itemName}" --catalog-name "{catalogName}" --dev-center-name "Contoso" \
    --resource-group "rg1" 
```
#### fidalgo catalog ####
##### Create #####
```
az fidalgo catalog create \
    --ado-git path="/templates" branch="main" secret-identifier="https://contosokv.vault.azure.net/secrets/CentralRepoPat" uri="https://contoso@dev.azure.com/contoso/contosoOrg/_git/centralrepo-fakecontoso" \
    --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1" 

az fidalgo catalog wait --created --name "{myCatalog}" --dev-center-name "{myDevCenter}" --resource-group "{rg}"
```
##### Create #####
```
az fidalgo catalog create \
    --git-hub path="/templates" branch="main" secret-identifier="https://contosokv.vault.azure.net/secrets/CentralRepoPat" uri="https://github.com/Contoso/centralrepo-fake.git" \
    --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1" 

az fidalgo catalog wait --created --name "{myCatalog}" --dev-center-name "{myDevCenter}" --resource-group "{rg}"
```
##### List #####
```
az fidalgo catalog list --dev-center-name "Contoso" --resource-group "rg1"
```
##### Show #####
```
az fidalgo catalog show --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
```
##### Update #####
```
az fidalgo catalog update --git-hub path="/environments" --name "{catalogName}" --dev-center-name "Contoso" \
    --resource-group "rg1" 
```
##### Sync #####
```
az fidalgo catalog sync --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
```
##### Delete #####
```
az fidalgo catalog delete --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
```
#### fidalgo mapping ####
##### Create #####
```
az fidalgo mapping create --environment-type "Sandbox" \
    --mapped-subscription-id "/subscriptions/57a221ae-b5e9-4bea-be0a-e86e5f9317cc" \
    --project-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.Fidalgo/projects/{projectName}" \
    --dev-center-name "Contoso" --name "{mappingName}" --resource-group "rg1" 
```
##### Show #####
```
az fidalgo mapping show --dev-center-name "Contoso" --name "{mappingName}" --resource-group "rg1"
```
##### List #####
```
az fidalgo mapping list --dev-center-name "Contoso" --resource-group "rg1"
```
##### Update #####
```
az fidalgo mapping update --mapped-subscription-id "/subscriptions/57a221ae-b5e9-4bea-be0a-e86e5f9317cc" \
    --dev-center-name "Contoso" --name "{mappingName}" --resource-group "rg1" 
```
##### Delete #####
```
az fidalgo mapping delete --dev-center-name "Contoso" --name "{mappingName}" --resource-group "rg1"
```
#### fidalgo operation-statuses ####
##### Show #####
```
az fidalgo operation-statuses show --operation-id "{operationId}" --location "{location}"
```
#### fidalgo sku ####
##### List #####
```
az fidalgo sku list
```
#### fidalgo pool ####
##### Create #####
```
az fidalgo pool create --location "centralus" \
    --machine-definition-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.Fidalgo/machinedefinitions/{machineDefinitionName}" \
    --network-settings-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.Fidalgo/networksettings/{networkSettingName}" \
    --sku name="medium" --name "{poolName}" --project-name "{projectName}" --resource-group "rg1" 

az fidalgo pool wait --created --name "{myPool}" --project-name "{myProject}" --resource-group "{rg}"
```
##### Show #####
```
az fidalgo pool show --name "{poolName}" --project-name "{projectName}" --resource-group "rg1"
```
##### List #####
```
az fidalgo pool list --project-name "{projectName}" --resource-group "rg1"
```
##### Update #####
```
az fidalgo pool update \
    --machine-definition-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.Fidalgo/machinedefinitions/{machineDefinitionName}" \
    --name "{poolName}" --project-name "{projectName}" --resource-group "rg1" 
```
##### Delete #####
```
az fidalgo pool delete --name "poolName" --project-name "{projectName}" --resource-group "rg1"
```
#### fidalgo machine-definition ####
##### Create #####
```
az fidalgo machine-definition create --location "centralus" \
    --image-reference id="/subscriptions/0ac520ee-14c0-480f-b6c9-0a90c58ffff/resourceGroups/Example/providers/Microsoft.Compute/images/exampleImage" \
    --name "{machineDefinitionName}" --resource-group "rg1" 

az fidalgo machine-definition wait --created --name "{myMachineDefinition}" --resource-group "{rg}"
```
##### Show #####
```
az fidalgo machine-definition show --name "{machineDefinitionName}" --resource-group "rg1"
```
##### List #####
```
az fidalgo machine-definition list --resource-group "rg1"
```
##### Update #####
```
az fidalgo machine-definition update \
    --image-reference id="/subscriptions/0ac520ee-14c0-480f-b6c9-0a90c58ffff/resourceGroups/Example/providers/Microsoft.Compute/images/image2" \
    --name "{machineDefinitionName}" --resource-group "rg1" 
```
##### Delete #####
```
az fidalgo machine-definition delete --name "{machineDefinitionName}" --resource-group "rg1"
```
#### fidalgo network-setting ####
##### Create #####
```
az fidalgo network-setting create --location "centralus" --domain-name "mydomaincontroller.local" \
    --domain-password "Password value for user" --domain-username "testuser@mydomaincontroller.local" \
    --networking-resource-group-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/ExampleRG" \
    --subnet-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/ExampleRG/providers/Microsoft.Network/virtualNetworks/ExampleVNet/subnets/default" \
    --name "{networkSettingName}" --resource-group "rg1" 

az fidalgo network-setting wait --created --name "{myNetworkSetting}" --resource-group "{rg}"
```
##### Show #####
```
az fidalgo network-setting show --name "{networkSettingName}" --resource-group "rg1"
```
##### List #####
```
az fidalgo network-setting list --resource-group "rg1"
```
##### Update #####
```
az fidalgo network-setting update --domain-password "New Password value for user" --name "{networkSettingName}" \
    --resource-group "rg1" 
```
##### Show-health-detail #####
```
az fidalgo network-setting show-health-detail --name "{networkSettingName}" --resource-group "rg1"
```
##### Delete #####
```
az fidalgo network-setting delete --name "{networkSettingName}" --resource-group "rg1"
```