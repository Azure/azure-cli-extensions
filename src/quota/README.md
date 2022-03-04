# Azure CLI quota Extension #
This is the extension for quota

### How to use ###
Install this extension using the below CLI command
```
az extension add --name quota
```

### Included Features ###
#### quota usage ####
##### List-UsagesForCompute #####
```
az quota usage list \
    --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Compute/locations/eastus" 
```
##### List-UsagesForNetwork #####
```
az quota usage list \
    --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Network/locations/eastus" 
```
##### List-UsagesMachineLearningServices #####
```
az quota usage list \
    --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.MachineLearningServices/locations/eastus" 
```
##### Show-UsagesRequestForCompute #####
```
az quota usage show --resource-name "standardNDSFamily" \
    --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Compute/locations/eastus" 
```
##### Show-UsagesRequestForNetwork #####
```
az quota usage show --resource-name "MinPublicIpInterNetworkPrefixLength" \
    --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Network/locations/eastus" 
```
#### quota ####
##### Create-ForNetwork #####
```
az quota create --resource-name "MinPublicIpInterNetworkPrefixLength" --scope "subscriptions/00000000-00\
    00-0000-0000-000000000000/providers/Microsoft.Network/locations/eastus" \
    --limit-object value=10 limit-object-type=LimitValue --resource-type MinPublicIpInterNetworkPrefixLength
```
##### Create-ForNetworkStandardSkuPublicIpAddressesResource #####
```
az quota create --resource-name "StandardSkuPublicIpAddresses" --scope "subscriptions/00000000-0000-0000\
    -0000-000000000000/providers/Microsoft.Network/locations/eastus" \
    --limit-object value=10 limit-object-type=LimitValue --resource-type PublicIpAddresses
```
##### Create-ForCompute #####
```
az quota create --resource-name "standardFSv2Family" --scope "subscriptions/00000000-0000-0000-0000-0000\
    00000000/providers/Microsoft.Compute/locations/eastus" \
    --limit-object value=10 limit-object-type=LimitValue --resource-type dedicated
```
##### Create-MachineLearningServicesLowPriorityResource #####
```
az quota create  --resource-name "TotalLowPriorityCores" --scope "subscriptions/00000000-0000-0000-0000-\
    000000000000/providers/Microsoft.MachineLearning/Services/locations/eastus" \
    --limit-object value=10 limit-object-type=LimitValue --resource-type lowPriority
```
##### Show-ForNetwork #####
```
az quota show --resource-name "MinPublicIpInterNetworkPrefixLength" \
    --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Network/locations/eastus" 
```
##### Show-ForCompute #####
```
az quota show --resource-name "standardNDSFamily" \
    --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Compute/locations/eastus" 
```
##### List-QuotaLimitsForCompute #####
```
az quota list --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Compute/locations/eastus"
```
##### List-QuotaLimitsForNetwork #####
```
az quota list --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Network/locations/eastus"
```
##### List-QuotaLimitsMachineLearningServices #####
```
az quota list \
    --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.MachineLearningServices/locations/eastus" 
```
##### Update-ForCompute #####
```
az quota update --resource-name "standardFSv2Family" --scope "subscriptions/00000000-0000-0000-0000-0000\
    00000000/providers/Microsoft.Compute/locations/eastus" --limit-object value=10 limit-object-type=LimitValue 
    --resource-type dedicated
```
##### Update-ForNetwork #####
```
az quota update --resource-name "MinPublicIpInterNetworkPrefixLength" --scope "subscriptions/00000000-00\
    00-0000-0000-000000000000/providers/Microsoft.Network/locations/eastus" \
    --limit-object value=10 limit-object-type=LimitValue --resource-type MinPublicIpInterNetworkPrefixLength 
```
#### quota request status ####
##### List-QuotaRequestHistory #####
```
az quota request status list \
    --scope "subscriptions/D7EC67B3-7657-4966-BFFC-41EFD36BAAB3/providers/Microsoft.Compute/locations/eastus" 
```
##### Show #####
```
az quota request status show --name "2B5C8515-37D8-4B6A-879B-CD641A2CF605" \
    --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Compute/locations/eastus" 
```
#### quota operation ####
##### List #####
```
az quota operation list
```