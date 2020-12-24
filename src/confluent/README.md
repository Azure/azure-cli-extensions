# Azure CLI confluent Extension #
This is the extension for confluent

### How to use ###
Install this extension using the below CLI command
```
az extension add --name confluent
```

### Included Features ###
#### confluent terms ####
##### List #####
```
az confluent terms list
```
#### confluent organization ####
##### Create #####
```
az confluent organization create --location "West US" \
    --offer-detail id="string" plan-id="string" plan-name="string" publisher-id="string" term-unit="string" \
    --user-detail email-address="contoso@microsoft.com" first-name="string" last-name="string" \
    --tags Environment="Dev" --name "myOrganization" --resource-group "myResourceGroup" 

az confluent organization wait --created --name "{myOrganization}" --resource-group "{rg}"
```
##### Show #####
```
az confluent organization show --name "myOrganization" --resource-group "myResourceGroup"
```
##### List #####
```
az confluent organization list --resource-group "myResourceGroup"
```
##### Update #####
```
az confluent organization update --tags client="dev-client" env="dev" --name "myOrganization" \
    --resource-group "myResourceGroup" 
```
##### Delete #####
```
az confluent organization delete --name "myOrganization" --resource-group "myResourceGroup"
```