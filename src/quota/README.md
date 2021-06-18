# Azure CLI quota Extension #
This is the extension for quota

### How to use ###
Install this extension using the below CLI command
```
az extension add --name quota
```

### Included Features ###
#### quota ####
##### Create #####
```
az quota create --properties "{\\"name\\":{\\"value\\":\\"standardFSv2Family\\"},\\"limit\\":200}" \
    --resource-name "standardFSv2Family" \
    --scope "subscriptions/D7EC67B3-7657-4966-BFFC-41EFD36BAAB3/providers/Microsoft.Compute/locations/eastus" 
```
##### Create #####
```
az quota create --properties "{\\"name\\":{\\"value\\":\\"standardFSv2Family\\"},\\"limit\\":200}" \
    --resource-name "standardFSv2Family" \
    --scope "subscriptions/D7EC67B3-7657-4966-BFFC-41EFD36BAAB3/providers/Microsoft.Compute/locations/eastus" 
```
##### Create #####
```
az quota create \
    --properties "{\\"name\\":{\\"value\\":\\"TotalLowPriorityCores\\"},\\"limit\\":200,\\"resourceType\\":\\"lowPriority\\"}" \
    --resource-name "TotalLowPriorityCores" \
    --scope "subscriptions/D7EC67B3-7657-4966-BFFC-41EFD36BAAB3/providers/Microsoft.MachineLearningServices/locations/eastus" 
```
##### List #####
```
az quota list --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Compute/locations/eastus"
```
##### List #####
```
az quota list \
    --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.MachineLearningServices/locations/eastus" 
```
##### Show #####
```
az quota show --resource-name "standardNDSFamily" \
    --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Compute/locations/eastus" 
```
##### Update #####
```
az quota update --properties "{\\"name\\":{\\"value\\":\\"standardFSv2Family\\"},\\"limit\\":200}" \
    --resource-name "standardFSv2Family" \
    --scope "subscriptions/D7EC67B3-7657-4966-BFFC-41EFD36BAAB3/providers/Microsoft.Compute/locations/eastus" 
```
#### quota quota-request-status ####
##### List #####
```
az quota quota-request-status list \
    --scope "subscriptions/D7EC67B3-7657-4966-BFFC-41EFD36BAAB3/providers/Microsoft.Compute/locations/eastus" 
```
##### Show #####
```
az quota quota-request-status show --id "2B5C8515-37D8-4B6A-879B-CD641A2CF605" \
    --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Compute/locations/eastus" 
```
##### Show #####
```
az quota quota-request-status show --id "2B5C8515-37D8-4B6A-879B-CD641A2CF605" \
    --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Compute/locations/eastus" 
```
##### Show #####
```
az quota quota-request-status show --id "2B5C8515-37D8-4B6A-879B-CD641A2CF605" \
    --scope "subscriptions/D7EC67B3-7657-4966-BFFC-41EFD36BAAB3/providers/Microsoft.Compute/locations/eastus" 
```
#### quota quota-resource-provider ####
##### List #####
```
az quota quota-resource-provider list
```
#### quota operation ####
##### List #####
```
az quota operation list
```