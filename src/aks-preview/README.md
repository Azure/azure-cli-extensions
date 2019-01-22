#Azure CLI AKS Preview Extension#
This is an extension for AKS features. This will replace the full AKS module.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name aks-preview
```

## Included Features
### Cluster Auto Scaler: 
[more info](https://docs.microsoft.com/en-us/azure/aks/autoscaler)


#### create aks cluster with enabled cluster autoscaler 
*Examples:*
```
az aks create \
    -g MyResourceGroup \
    -n MyManagedCluster \
    --enable-cluster-autoscaler \
    --min-count 1 \
    --max-count 5 \
    --node-count 3 \
    --kubernetes-version 1.11.3
```

#### enable cluster autoscaler for existing cluster
Note: make sure following setting:
1. min-count <= node-count 
2. max-count >= node-count
3. kubernetes-version >= 1.10.6
*Examples:*
```
az aks update \
    -g MyResourceGroup \
    -n MyManagedCluster \
    --enable-cluster-autoscaler \
    --min-count 1 \
    --max-count 5
```

#### disable cluster autoscaler for exisiting enabled cluster
*Examples:*
```
az aks update \
    -g MyResourceGroup \
    -n MyManagedCluster \
    --disable-cluster-autoscaler
```

#### update min-count/max-count for exisiting enabled cluster
*Examples:*
```
az aks update \
    -g MyResourceGroup \
    -n MyManagedCluster \
    --update-cluster-autoscaler \
    --min-count 1 \
    --max-count 5
```

#### Enable VMSS for new cluster
*Examples:*
```
az aks create \
    -g MyResourceGroup \
    -n MyManagedCluster \
    --enable-VMSS \
```
