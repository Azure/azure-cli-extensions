# Azure CLI operationsmanagement Extension #
This is the extension for operationsmanagement

### How to use ###
Install this extension using the below CLI command
```
az extension add --name operationsmanagement
```

### Included Features ###
#### operationsmanagement solution ####
##### Create #####
```
az operationsmanagement solution create --location "East US" \
    --plan name="name1" product="product1" promotion-code="promocode1" publisher="publisher1" \
    --properties contained-resources="/subscriptions/sub2/resourceGroups/rg2/providers/provider1/resources/resource1" contained-resources="/subscriptions/sub2/resourceGroups/rg2/providers/provider2/resources/resource2" referenced-resources="/subscriptions/sub2/resourceGroups/rg2/providers/provider1/resources/resource2" referenced-resources="/subscriptions/sub2/resourceGroups/rg2/providers/provider2/resources/resource3" workspace-resource-id="/subscriptions/sub2/resourceGroups/rg2/providers/Microsoft.OperationalInsights/workspaces/ws1" \
    --resource-group "rg1" --name "solution1" 
```
##### Show #####
```
az operationsmanagement solution show --resource-group "rg1" --name "solution1"
```
##### List #####
```
az operationsmanagement solution list --resource-group "rg1"
```
##### Update #####
```
az operationsmanagement solution update --tags Dept="IT" Environment="Test" --resource-group "rg1" --name "solution1"
```
##### Delete #####
```
az operationsmanagement solution delete --resource-group "rg1" --name "solution1"
```
#### operationsmanagement management-association ####
##### Create #####
```
az operationsmanagement management-association create --name "managementAssociation1" --location "East US" \
    --application-id "/subscriptions/sub1/resourcegroups/rg1/providers/Microsoft.Appliance/Appliances/appliance1" \
    --provider-name "providerName" --resource-group "rg1" --resource-name "resourceName" \
    --resource-type "resourceType" 
```
##### Show #####
```
az operationsmanagement management-association show --name "managementAssociation1" --provider-name "providerName" \
    --resource-group "rg1" --resource-name "resourceName" --resource-type "resourceType" 
```
##### List #####
```
az operationsmanagement management-association list
```
##### Delete #####
```
az operationsmanagement management-association delete --name "managementAssociationName" \
    --provider-name "providerName" --resource-group "rg1" --resource-name "resourceName" \
    --resource-type "resourceType" 
```
#### operationsmanagement management-configuration ####
##### Create #####
```
az operationsmanagement management-configuration create --name "managementConfiguration1" \
    --properties-parameters location="East US" --resource-group "rg1" 
```
##### Show #####
```
az operationsmanagement management-configuration show --name "managementConfigurationName" --resource-group "rg1"
```
##### List #####
```
az operationsmanagement management-configuration list
```
##### Delete #####
```
az operationsmanagement management-configuration delete --name "managementConfigurationName" --resource-group "rg1"
```