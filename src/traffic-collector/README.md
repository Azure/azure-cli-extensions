# Azure CLI TrafficCollector Extension #
This is an extension to manage azure traffic collector resources.

### How to use
Install this extension using the below CLI command.
```
az extension add --name traffic-collector
```

### Azure Traffic Collector

Create new azure traffic collector.
```
az network-function traffic-collector create --resource-group rg1 --traffic-collector-name atc1 --location eastus
```
Get the specified azure traffic collector in a resource group.
```
az network-function traffic-collector show --resource-group rg1 --traffic-collector-name atc1
```
Return a list of azure traffic collectors in a resource group.
```
az network-function traffic-collector list --resource-group rg1
```
Update an azure traffic collector resource.
```
az network-function traffic-collector update --resource-group rg1 --traffic-collector-name atc1 --tags key=value
```
Delete a specified azure traffic collector.
```
az network-function traffic-collector delete --resource-group rg1 --traffic-collector-name atc1
```

### Collector Policy
Create a new collector policy.
```
az network-function traffic-collector collector-policy create --resource-group rg1 --traffic-collector-name atc1 --name cp1 --location eastus --ingestion-policy {ingestion-sources:[{resource-id:/subscriptions/<subscription_id>/resourceGroups/<resource_group>/providers/Microsoft.Network/expressRouteCircuits/<cp_name>,source-type:Resource}],ingestion-type:IPFIX}
```
Get the specified collector policy.
```
az network-function traffic-collector collector-policy show --resource-group rg1 --traffic-collector-name atc1 --name cp1
```
Return a list of collector policies by resource group and traffic-collector name.
```
az network-function traffic-collector collector-policy show --resource-group rg1 --traffic-collector-name atc1
```
Update a specified collector policy.
```
az network-function traffic-collector collector-policy update --resource-group rg1 --traffic-collector-name atc1 --name cp1 --location eastus --emission-policies [0]={emission-destinations:[{destination-type:AzureMonitor}],emission-type:IPFIX}
```
Delete a specified collector policy.
```
az network-function traffic-collector collector-policy delete --resource-group rg1 --traffic-collector-name atc1 --name cp1
```