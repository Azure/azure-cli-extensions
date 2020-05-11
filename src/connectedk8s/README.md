# Azure CLI Connected Kubernetes Extension #
This package is for the 'connectedk8s' extension, i.e. 'az connectedk8s'.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name connectedk8s
```

### Included Features
#### Connected Kubernetes Management:
*Examples:*

##### Create a connected kubernetes cluster
```
az connectedk8s connect \
    --subscription subscription_id \
    --resource-group my-rg \
    --name my-cluster \
    --location eastus
```

##### Show connected kubernetes cluster
```
az connectedk8s show \
    --subscription subscription_id \
    --resource-group my-rg \
    --name my-cluster \
```
or
```
az connectedk8s show \
    --ids "/subscriptions/subscription_id/resourceGroups/my-rg/providers/Microsoft.Kubernetes/connectedClusters/my-cluster" \
```

##### List connected kubernetes cluster in resource group
```
az connectedk8s list \
    --resource-group my-rg
```

##### Delete connected kubernetes cluster
```
az connectedk8s delete \
    --subscription subscription_id \
    --resource-group my-rg \
    --name my-cluster \
```
or
```
az connectedk8s delete \
    --ids "/subscriptions/subscription_id/resourceGroups/my-rg/providers/Microsoft.Kubernetes/connectedClusters/my-cluster" \
    -y
```